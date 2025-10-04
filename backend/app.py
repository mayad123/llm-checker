from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx, trafilatura, spacy, time, os
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer, util
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

SEARX_URL = os.getenv("SEARX_URL", "http://localhost:8080/search")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

nlp = spacy.load("en_core_web_sm")
embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
tok = AutoTokenizer.from_pretrained("microsoft/deberta-v3-base-mnli")
nli = AutoModelForSequenceClassification.from_pretrained("microsoft/deberta-v3-base-mnli")
label_map = {0: "contradicted", 1: "unclear", 2: "supported"}

def extract_claims(text: str, cap: int = 8):
    doc = nlp(text)
    claims = []
    for sent in doc.sents:
        if any(ent.label_ in {"PERSON","ORG","GPE","EVENT","DATE","MONEY"} for ent in sent.ents) and any(t.pos_=="VERB" for t in sent):
            claims.append(sent.text.strip())
    return claims[:cap]

async def searx(query: str):
    params = {"q": query, "format": "json", "language": "en"}
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(SEARX_URL, params=params)
        r.raise_for_status()
        return r.json().get("results", [])[:5]

def fetch_text(url: str):
    downloaded = trafilatura.fetch_url(url)
    return trafilatura.extract(downloaded) if downloaded else None

def nli_label(claim: str, passage: str):
    inputs = tok(claim, passage, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        logits = nli(**inputs).logits[0]
    probs = torch.softmax(logits, dim=-1)
    idx = int(torch.argmax(probs))
    return label_map[idx], float(probs[idx])

@app.post("/check")
async def check(payload: dict):
    t0 = time.time()
    llm_output = payload.get("llm_output", "")
    claims = extract_claims(llm_output)
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

                paras = [p for p in text.split("\n") if len(p.split()) > 12][:10]
                if not paras:
                    continue

                bm25 = BM25Okapi([p.split() for p in paras])
                bm = bm25.get_scores(c.split())
                emb_c = embedder.encode([c], convert_to_tensor=True)
                emb_p = embedder.encode(paras, convert_to_tensor=True)
                cos = util.cos_sim(emb_c, emb_p)[0].tolist()
                maxbm = max(bm) if max(bm) > 0 else 1.0
                hybrid = [0.6*(s/maxbm) + 0.4*cosv for s,cosv in zip(bm, cos)]
                ranked = sorted(zip(paras, hybrid), key=lambda x: x[1], reverse=True)[:5]

                for p,_score in ranked:
                    label, conf = nli_label(c, p)
                    candidates.append({"url": url, "passage": p, "label": label, "conf": conf})

        best_support = max([x for x in candidates if x["label"]=="supported"], key=lambda y:y["conf"], default=None)
        best_contra  = max([x for x in candidates if x["label"]=="contradicted"], key=lambda y:y["conf"], default=None)

        if best_contra and best_contra["conf"] >= 0.8:
            verdict, best = "contradicted", best_contra
        elif best_support and best_support["conf"] >= 0.8:
            verdict, best = "supported", best_support
        else:
            verdict, best = "unclear", max(candidates, key=lambda y:y["conf"], default=None)

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
