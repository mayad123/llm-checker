import argparse
import json
import random
from typing import Any, Dict, Iterable, List, Tuple

try:
    # Optional: only needed when using --hf-dataset
    from datasets import load_dataset  # type: ignore
except Exception:  # pragma: no cover
    load_dataset = None  # lazy import guard


def iter_jsonl(path: str) -> Iterable[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def extract_texts(item_val: Any) -> List[str]:
    """Extract list of passage texts from a field that may be:
    - list[str]
    - list[dict] with "text" or "passage" keys
    - str (single)
    - None / missing
    """
    if item_val is None:
        return []
    if isinstance(item_val, str):
        s = item_val.strip()
        return [s] if s else []
    if isinstance(item_val, list):
        out: List[str] = []
        for v in item_val:
            if isinstance(v, str):
                t = v.strip()
                if t:
                    out.append(t)
            elif isinstance(v, dict):
                # try common keys
                for k in ("text", "passage", "evidence", "snippet"):
                    if k in v and isinstance(v[k], str) and v[k].strip():
                        out.append(v[k].strip())
                        break
        return out
    if isinstance(item_val, dict):
        # some datasets pack passages under a key
        for k in ("text", "passage", "evidence", "snippet"):
            if k in item_val and isinstance(item_val[k], str) and item_val[k].strip():
                return [item_val[k].strip()]
    return []


def convert(
    in_path: str,
    out_path: str,
    claim_key: str = "claim",
    pos_key: str = "positive_passages",
    neg_key: str = "negative_passages",
    neg_per_pos: int = 0,
    seed: int = 42,
) -> Tuple[int, int, int]:
    """Convert local JSONL into pairwise reranker format.

    If negatives are missing and `neg_per_pos>0`, sample negatives from other items' evidence.
    """
    # First pass: collect claims and positives (and existing negatives)
    items: List[Tuple[str, List[str], List[str]]] = []  # (claim, pos, neg)
    all_evidence: List[str] = []

    for obj in iter_jsonl(in_path):
        claim = obj.get(claim_key)
        if not isinstance(claim, str) or not claim.strip():
            for alt in ("query", "question", "claim_text"):
                if isinstance(obj.get(alt), str) and obj[alt].strip():
                    claim = obj[alt]
                    break
        if not isinstance(claim, str) or not claim.strip():
            continue
        claim = claim.strip()

        pos = extract_texts(obj.get(pos_key))
        neg = extract_texts(obj.get(neg_key))

        if not pos:
            pos = extract_texts(obj.get("positives")) or extract_texts(obj.get("evidence"))
        if not neg:
            neg = extract_texts(obj.get("negatives")) or extract_texts(obj.get("distractors"))

        items.append((claim, pos, neg))
        all_evidence.extend(pos)

    # Second pass: write out with optional negative sampling
    random.seed(seed)
    total_items = len(items)
    pos_pairs = 0
    neg_pairs = 0

    with open(out_path, "w", encoding="utf-8") as out_f:
        for claim, pos, neg in items:
            # positives
            for passage in pos:
                rec = {"text1": claim, "text2": passage, "label": 1}
                out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                pos_pairs += 1

            wrote_any_neg = False
            # existing negatives
            for passage in neg:
                rec = {"text1": claim, "text2": passage, "label": 0}
                out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                neg_pairs += 1
                wrote_any_neg = True

            # sample negatives if requested and none provided (or even if provided? keep conservative)
            if not wrote_any_neg and neg_per_pos > 0 and all_evidence:
                pos_set = set(pos)
                candidates = [t for t in all_evidence if t not in pos_set]
                need = neg_per_pos * max(1, len(pos))
                if candidates:
                    k = min(need, len(candidates))
                    for neg_psg in random.sample(candidates, k):
                        rec = {"text1": claim, "text2": neg_psg, "label": 0}
                        out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                        neg_pairs += 1

    return total_items, pos_pairs, neg_pairs


def convert_hf(
    dataset_name: str,
    split: str,
    out_path: str,
    claim_key: str = "claim",
    evidence_key: str = "evidence",
    neg_per_pos: int = 1,
    seed: int = 42,
) -> Tuple[int, int, int]:
    """Convert a Hugging Face dataset (e.g., Dzeniks/hover) into pairwise reranker format.

    Assumes each item has `claim_key` and `evidence_key` (strings or list of strings).
    Negatives are sampled from evidence of other items.
    """
    if load_dataset is None:
        raise RuntimeError(
            "datasets.load_dataset is unavailable. Please `pip install datasets` or use requirements."
        )

    ds = load_dataset(dataset_name, split=split)

    # Collect all evidence strings for negative sampling
    all_evidence: List[str] = []
    pos_by_idx: List[List[str]] = []
    claims: List[str] = []

    def to_str_list(val: Any) -> List[str]:
        if val is None:
            return []
        if isinstance(val, str):
            s = val.strip()
            return [s] if s else []
        if isinstance(val, list):
            out: List[str] = []
            for v in val:
                if isinstance(v, str):
                    t = v.strip()
                    if t:
                        out.append(t)
                elif isinstance(v, dict):
                    for k in ("text", "passage", "evidence", "snippet"):
                        if k in v and isinstance(v[k], str) and v[k].strip():
                            out.append(v[k].strip())
                            break
            return out
        if isinstance(val, dict):
            for k in ("text", "passage", "evidence", "snippet"):
                if k in val and isinstance(val[k], str) and val[k].strip():
                    return [val[k].strip()]
        return []

    for item in ds:  # type: ignore
        claim = item.get(claim_key)
        if not isinstance(claim, str) or not claim.strip():
            continue
        claims.append(claim.strip())
        ev = to_str_list(item.get(evidence_key))
        pos_by_idx.append(ev)
        all_evidence.extend(ev)

    random.seed(seed)
    total_items = len(claims)
    pos_pairs = 0
    neg_pairs = 0

    with open(out_path, "w", encoding="utf-8") as out_f:
        for i in range(total_items):
            claim = claims[i]
            positives = pos_by_idx[i]
            # Write positives
            for psg in positives:
                rec = {"text1": claim, "text2": psg, "label": 1}
                out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                pos_pairs += 1

            # Sample negatives from global pool excluding current positives
            if neg_per_pos > 0 and all_evidence:
                pos_set = set(positives)
                candidates = [t for t in all_evidence if t not in pos_set]
                need = neg_per_pos * max(1, len(positives))
                if candidates:
                    sample_n = min(need, len(candidates))
                    for neg in random.sample(candidates, sample_n):
                        rec = {"text1": claim, "text2": neg, "label": 0}
                        out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                        neg_pairs += 1

    return total_items, pos_pairs, neg_pairs


def main():
    ap = argparse.ArgumentParser(description="Prepare HoVer/HoVer-like data into reranker pairs")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--in", dest="in_path", help="Input .jsonl path")
    src.add_argument("--hf-dataset", dest="hf_dataset", help="HF dataset name, e.g. Dzeniks/hover")

    ap.add_argument("--out", dest="out_path", required=True, help="Output .jsonl path for pairs")

    # Keys for local JSONL conversion
    ap.add_argument("--claim-key", default="claim", help="Key for claim text")
    ap.add_argument("--pos-key", default="positive_passages", help="Key for positive passages")
    ap.add_argument("--neg-key", default="negative_passages", help="Key for negative passages")

    # HF dataset options
    ap.add_argument("--hf-split", default="train", help="HF split, e.g. train/dev/test")
    ap.add_argument("--hf-claim-key", default="claim", help="HF field for claim text")
    ap.add_argument("--hf-evidence-key", default="evidence", help="HF field for positive evidence")
    ap.add_argument("--neg-per-pos", type=int, default=1, help="Negatives to sample per positive")
    ap.add_argument("--seed", type=int, default=42, help="Random seed for negative sampling")
    args = ap.parse_args()

    if args.hf_dataset:
        total, pos_n, neg_n = convert_hf(
            dataset_name=args.hf_dataset,
            split=args.hf_split,
            out_path=args.out_path,
            claim_key=args.hf_claim_key,
            evidence_key=args.hf_evidence_key,
            neg_per_pos=args.neg_per_pos,
            seed=args.seed,
        )
    else:
        total, pos_n, neg_n = convert(
            in_path=args.in_path,
            out_path=args.out_path,
            claim_key=args.claim_key,
            pos_key=args.pos_key,
            neg_key=args.neg_key,
            neg_per_pos=args.neg_per_pos,
            seed=args.seed,
        )
    print(f"Processed items={total} positives={pos_n} negatives={neg_n} -> {args.out_path}")


if __name__ == "__main__":
    main()
