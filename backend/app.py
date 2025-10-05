from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx, trafilatura, spacy, time, os, traceback
from urllib.parse import urlparse
from functools import lru_cache
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer, util, CrossEncoder
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

# ===== Config =====
SEARX_URL = os.getenv("SEARX_URL", "http://localhost:8080/search")
SEARX_TIMEOUT_S = float(os.getenv("SEARX_TIMEOUT_S", "15"))

# Retrieval / ranking
PARA_MIN_WORDS = 8
RECALL_TOP_PARAS = 10        # candidates passed to the reranker
TOP_PARAS_PER_PAGE = 3       # NLI checks per page after rerank

# Decision thresholds
SUPPORT_THRESHOLD = 0.65
CONTRA_THRESHOLD  = 0.65
MARGIN = 0.10                # extra edge needed if both sides are strong
MIN_SOURCES = 1              # set 2 for stricter consensus

TRUST_BONUS_DOMAINS = (
    ".wikipedia.org", ".britannica.com", ".gov", ".edu",
    "reuters.com", "apnews.com", "bbc.com", "nytimes.com", "nature.com",
)

# ===== App & CORS (loose for dev; tighten for prod) =====
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev-only; in prod set to ["http://localhost:3000", ...]
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== NLP / Models =====
nlp = spacy.load("en_core_web_sm")

# Dual-encoder for semantic recall
embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Cross-encoder reranker for precision
RERANKER_ID = "cross-encoder/ms-marco-MiniLM-L-6-v2"
reranker = CrossEncoder(RERANKER_ID)

# NLI for final entailment/contradiction
MODEL_ID = "MoritzLaurer/deberta-v3-base-mnli-fever-anli"
tok = AutoTokenizer.from_pretrained(MODEL_ID)
nli = AutoModelForSequenceClassification.from_pretrained(MODEL_ID)
label_map = {0: "contradicted", 1: "unclear", 2: "supported"}

# ===== Utilities =====
def domain_weight(url: str) -> float:
    try:
        host = urlparse(url).netloc.lower()
    except Exception:
        return 1.0
    return 1.15 if any(host.endswith(d) or d in host for d in TRUST_BONUS_DOMAINS) else 1.0

def decision_from_votes(votes, support_threshold=SUPPORT_THRESHOLD, contra_threshold=CONTRA_THRESHOLD,
                        min_sources=MIN_SOURCES, margin=MARGIN):
    """Aggregate multiple evidence votes into a single verdict with consensus + margin."""
    if not votes:
        return "unclear", None

    sup = sorted([v for v in votes if v["label"] == "supported"], key=lambda x: x["conf"], reverse=True)
    con = sorted([v for v in votes if v["label"] == "contradicted"], key=lambda x: x["conf"], reverse=True)

    def distinct_sources(arr):
        seen = set()
        for v in arr:
            try:
                seen.add(urlparse(v["url"]).netloc)
            except Exception:
                pass
        return len(seen)

    def best_weighted(arr):
        if not arr: return None
        return max(arr, key=lambda v: v["conf"] * domain_weight(v.get("url","")))

    best_sup = best_weighted(sup)
    best_con = best_weighted(con)

    sup_ok = best_sup and best_sup["conf"] >= support_threshold and distinct_sources(sup) >= min_sources
    con_ok = best_con and best_con["conf"] >= contra_threshold and distinct_sources(con) >= min_sources

    if sup_ok and not con_ok:
        return "supported", best_sup
    if con_ok and not sup_ok:
        return "contradicted", best_con
    if sup_ok and con_ok:
        if (best_sup["conf"] - best_con["conf"]) >= margin:
            return "supported", best_sup
        if (best_con["conf"] - best_sup["conf"]) >= margin:
            return "contradicted", best_con
        return "unclear", max([best_sup, best_con], key=lambda v: v["conf"])

    best = best_sup if (best_sup and (not best_con or best_sup["conf"] >= best_con["conf"])) else best_con
    return "unclear", best

# ----- Claim extraction (guarantees at least one) -----
def extract_claims(text: str, cap: int = 8):
    """Return 'claim-like' sentences; if none, fall back to the whole input."""
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

def decompose_claim(claim: str):
    """
    Split long / compound claims into sub-claims using simple clause boundaries.
    Keeps it generic (no fact-specific rules).
    """
    doc = nlp(claim)
    chunks, cur = [], []
    for tok in doc:
        cur.append(tok.text)
        if tok.dep_ in {"cc"} or tok.text in {",", ";", "and", "but"}:
            s = " ".join(cur).strip(" ,;")
            if len(s.split()) >= 4:
                chunks.append(s)
            cur = []
    if cur:
        s = " ".join(cur).strip(" ,;")
        if len(s.split()) >= 4:
            chunks.append(s)
    # If decomposition produced nothing useful, return the claim as-is
    return chunks or [claim]

# ===== Retrieval helpers =====
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

# ===== API =====
@app.post("/check")
async def check(payload: dict):
    t0 = time.time()
    llm_output = (payload or {}).get("llm_output", "") or ""
    claims = extract_claims(llm_output)
    print(f"[check] text_len={len(llm_output)} claims={claims}")

    results = []

    for c in claims:
        # Decompose long/compound claims into sub-claims
        sub_claims = decompose_claim(c)

        # Light query expansion base
        q_short = c[:128]

        votes_for_overall = []  # collect votes across all sub-claims (used if you want a single verdict)

        for subc in sub_claims:
            queries = [
                f"\"{subc}\"",
                subc[:128],
                q_short.replace(" is ", " was "),
                q_short.replace(" was ", " is "),
            ]

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
                    paras_all = [p for p in text.split("\n") if len(p.split()) >= PARA_MIN_WORDS]
                    if not paras_all:
                        continue

                    # Stage 1: BM25 + cosine (recall)
                    bm25 = BM25Okapi([p.split() for p in paras_all])
                    bm = bm25.get_scores(subc.split())
                    emb_c = embedder.encode([subc], convert_to_tensor=True)
                    emb_p = embedder.encode(paras_all, convert_to_tensor=True)
                    cos = util.cos_sim(emb_c, emb_p)[0].tolist()

                    maxbm = max(bm) if bm and max(bm) > 0 else 1.0
                    hybrid = [0.6*(s/maxbm) + 0.4*cosv for s, cosv in zip(bm, cos)]
                    top_idx = sorted(range(len(paras_all)), key=lambda i: hybrid[i], reverse=True)[:RECALL_TOP_PARAS]
                    top_paras = [paras_all[i] for i in top_idx]

                    # Stage 2: cross-encoder rerank (precision)
                    pairs = [(subc, p) for p in top_paras]
                    try:
                        rerank_scores = reranker.predict(pairs).tolist()
                    except Exception:
                        # If GPU/ONNX issues, fall back to hybrid only
                        print("[reranker] fallback to hybrid")
                        rerank_scores = [hybrid[i] for i in top_idx]

                    reranked = sorted(zip(top_paras, rerank_scores), key=lambda x: x[1], reverse=True)[:TOP_PARAS_PER_PAGE]

                    # NLI with a small context window (±1 paragraph)
                    for p, _score in reranked:
                        try:
                            # Build window around the paragraph (find its index in full list)
                            try:
                                pi = paras_all.index(p)
                            except ValueError:
                                pi = None
                            if pi is not None:
                                window = " ".join(paras_all[max(0, pi-1): min(len(paras_all), pi+2)])
                            else:
                                window = p
                            # Trim to ~450 tokens to stay under 512 with claim tokens
                            window = " ".join(window.split()[:450])

                            label, conf = nli_label(subc, window)
                            candidates.append({"url": url, "passage": window, "label": label, "conf": conf})
                        except Exception:
                            print(f"[nli] error on url={url}")
                            traceback.print_exc()

            # Decide verdict for this sub-claim
            sub_verdict, sub_best = decision_from_votes(
                candidates,
                support_threshold=SUPPORT_THRESHOLD,
                contra_threshold=CONTRA_THRESHOLD,
                min_sources=MIN_SOURCES,
                margin=MARGIN
            )
            votes_for_overall.extend(candidates)

            print(f"[check] sub-claim='{subc[:80]}' cand={len(candidates)} verdict={sub_verdict} conf={(sub_best or {}).get('conf')}")
            results.append({
                "text": subc,
                "verdict": sub_verdict,
                "confidence": (sub_best or {}).get("conf", 0.0),
                "citation": ({"url": sub_best["url"], "snippet": sub_best["passage"][:350]} if sub_best else None)
            })

    return {
        "checked_on": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "claims": results,
        "latency_s": round(time.time() - t0, 2)
    }
