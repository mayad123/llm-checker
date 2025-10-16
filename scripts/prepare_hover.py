import argparse
import json
from typing import Any, Dict, Iterable, List, Tuple


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
) -> Tuple[int, int, int]:
    total_items = 0
    pos_pairs = 0
    neg_pairs = 0

    with open(out_path, "w", encoding="utf-8") as out_f:
        for obj in iter_jsonl(in_path):
            total_items += 1
            claim = obj.get(claim_key)
            if not isinstance(claim, str) or not claim.strip():
                # try alternative common keys
                for alt in ("query", "question", "claim_text"):
                    if isinstance(obj.get(alt), str) and obj[alt].strip():
                        claim = obj[alt]
                        break
            if not isinstance(claim, str) or not claim.strip():
                continue
            claim = claim.strip()

            pos = extract_texts(obj.get(pos_key))
            neg = extract_texts(obj.get(neg_key))

            # fallbacks for alternative field names commonly seen
            if not pos:
                pos = extract_texts(obj.get("positives")) or extract_texts(obj.get("evidence"))
            if not neg:
                neg = extract_texts(obj.get("negatives")) or extract_texts(obj.get("distractors"))

            for passage in pos:
                rec = {"text1": claim, "text2": passage, "label": 1}
                out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                pos_pairs += 1
            for passage in neg:
                rec = {"text1": claim, "text2": passage, "label": 0}
                out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                neg_pairs += 1

    return total_items, pos_pairs, neg_pairs


def main():
    ap = argparse.ArgumentParser(description="Prepare HoVer-style JSONL into reranker pairs")
    ap.add_argument("--in", dest="in_path", required=True, help="Input .jsonl path")
    ap.add_argument("--out", dest="out_path", required=True, help="Output .jsonl path for pairs")
    ap.add_argument("--claim-key", default="claim", help="Key for claim text")
    ap.add_argument("--pos-key", default="positive_passages", help="Key for positive passages")
    ap.add_argument("--neg-key", default="negative_passages", help="Key for negative passages")
    args = ap.parse_args()

    total, pos_n, neg_n = convert(
        in_path=args.in_path,
        out_path=args.out_path,
        claim_key=args.claim_key,
        pos_key=args.pos_key,
        neg_key=args.neg_key,
    )
    print(f"Processed items={total} positives={pos_n} negatives={neg_n} -> {args.out_path}")


if __name__ == "__main__":
    main()

