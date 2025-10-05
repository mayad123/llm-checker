from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx, trafilatura, spacy, time, os, traceback
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer, util
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

# ----- Config -----
SEARX_URL = os.getenv("SEARX_URL", "http://localhost:8080/search")
SEARX_TIMEOUT_S = float(os.getenv("SEARX_TIMEOUT_S", "15"))
TOP_PARAS_PER_PAGE = 3   # fewer passages => faster, more responsive
PARA_MIN_WORDS = 8
SUPPORT_THRESHOLD = 0.60
CONTRA_THRESHOLD  = 0.60

# ----- App & CORS (loose for dev; tighten allow_origins in prod) -----
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for dev; set to ["http://localhost:3000","http://127.0.0.1:3000"] later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----- NLP / Models -----
nlp = spacy.load("en_core_web_sm")
embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
MODEL_ID = "MoritzLaurer/deberta-v3-base-mnli-fever-anli"
tok = AutoTokenizer.from_pretrained(MODEL_ID)
nli = AutoModelForSequenceClassification.from_pretrained(MODEL_ID)
label_map = {0: "contradicted", 1: "unclear", 2: "supported"}

# ----- Claim extraction (guarantees at least one) -----
def extract_claims(text: str, cap: int = 8):
    """
    Return 'claim-like' sentences; if none, fall back to the whole input.
    """
    doc = nlp(text or "")
    out = []

    def has_verb(span): 
        return any(t.pos_ in {"VERB","AUX"} for t in span)

    def has_salient_ner(span):
        return any(ent.label_ in {
            "PERSON","ORG","GPE","EVENT","DATE","MONEY","NORP","FAC","LAW","WORK_OF_ART"
        } for ent in span.ents)

    def has_num_or_date(span):
        return any(t.like_num for t in span) or any(ent.label_ in {"DATE","TIME"} for ent in span.ents)

    # Pass 1: verb + (NER or numbers/dates)
    for s in doc.sents:
        if has_verb(s) and (has_salient_ner(s) or has_num_or_date(s)):
            out.append(s.text.strip())

    # Pass 2: any sentence with a verb (softer)
    if not out:
        for s in doc.sents:
            st = s.text.strip()
            if has_verb(s) and len(st.split()) >= 3:
                out.append(st)

    # Fallback: whole input
    if not out:
        whole = (text or "").strip()
        if whole:
            out = [whole if len(whole) <= 500 else whole[:500]]

    # Cleanup + cap
    out = [c.replace("\n", " ").strip(" .") for c in out]
    out = list(dict.fromkeys([c for c in out if len(c.split()) >= 3]))  # dedup & keep order
    return out[:cap]

# ----- Helpers -----
async def searx(query: str):
    params = {"q": query, "format": "json", "language": "en"}
    try:
        async with httpx.AsyncClient(timeout=SEARX_TIMEOUT_S) as client:
            r = await client.get(SEARX_URL, params=params)
            r.raise_for_status()
            return r.json().get("results", [])[:5]
    except Exception as e:
        print(f"[searx] query='{query}' error={e}")
        return []

def fetch_text(url: str):
    try:
        downloaded = trafilatura.fetch_url(url)
        return trafilatura.extract(downloaded) if downloaded else None
    except Exception as e:
        print(f"[fetch_text] url={url} error={e}")
        return None

def nli_label(claim: str, passage: str):
    inputs = tok(claim, passage, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        logits = nli(**inputs).logits[0]
    probs = torch.softmax(logits, dim=-1)
    idx = int(torch.argmax(probs))
    return label_map[idx], float(probs[idx])

# ----- API -----
@app.post("/check")
async def check(payload: dict):
    t0 = time.time()
    llm_output = (payload or {}).get("llm_output", "") or ""
    claims = extract_claims(llm_output)
    print(f"[check] text_len={len(llm_output)} claims={claims}")

    results = []

    for c in claims:
        queries = [f"\"{c}\"", c[:128]]
        candidates = []
        seen_urls = set()

        for q in queries:
            for res in await searx(q):
                url = res.get("url")
                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)

                text = fetch_text(url)
                if not text:
                    continue

                # keep short, high-signal paragraphs
                paras = [p for p in text.split("\n") if len(p.split()) >= PARA_MIN_WORDS][:10]
                if not paras:
                    continue

                # Hybrid rank: BM25 + cosine
                bm25 = BM25Okapi([p.split() for p in paras])
                bm = bm25.get_scores(c.split())
                emb_c = embedder.encode([c], convert_to_tensor=True)
                emb_p = embedder.encode(paras, convert_to_tensor=True)
                cos = util.cos_sim(emb_c, emb_p)[0].tolist()

                maxbm = max(bm) if bm and max(bm) > 0 else 1.0
                hybrid = [0.6*(s/maxbm) + 0.4*cosv for s, cosv in zip(bm, cos)]
                ranked = sorted(zip(paras, hybrid), key=lambda x: x[1], reverse=True)[:TOP_PARAS_PER_PAGE]

                for p, _score in ranked:
                    try:
                        label, conf = nli_label(c, p)
                        candidates.append({"url": url, "passage": p, "label": label, "conf": conf})
                    except Exception:
                        print(f"[nli] error on url={url}")
                        traceback.print_exc()

        best_support = max([x for x in candidates if x["label"] == "supported"], key=lambda y: y["conf"], default=None)
        best_contra  = max([x for x in candidates if x["label"] == "contradicted"], key=lambda y: y["conf"], default=None)

        if best_contra and best_contra["conf"] >= CONTRA_THRESHOLD:
            verdict, best = "contradicted", best_contra
        elif best_support and best_support["conf"] >= SUPPORT_THRESHOLD:
            verdict, best = "supported", best_support
        else:
            verdict, best = "unclear", max(candidates, key=lambda y: y["conf"], default=None)

        print(f"[check] claim='{c[:80]}' cand={len(candidates)} verdict={verdict} conf={(best or {}).get('conf')}")
        results.append({
            "text": c,
            "verdict": verdict,
            "confidence": (best or {}).get("conf", 0.0),
            "citation": ({"url": best["url"], "snippet": best["passage"][:350]} if best else None)
        })

    return {
        "checked_on": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "claims": results,
        "latency_s": round(time.time() - t0, 2)
    }
