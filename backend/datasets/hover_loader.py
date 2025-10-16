import json
from typing import Any, Dict, List, Sequence, Tuple


def load_reranker_pairs(path: str, limit: int | None = None) -> List[Dict[str, Any]]:
    """Load pairs produced by scripts/prepare_hover.py

    Each line in `path` must be a JSON object with keys:
      - text1: claim text
      - text2: passage text
      - label: 0 or 1
    """
    out: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            if not isinstance(obj, dict):
                continue
            if not isinstance(obj.get("text1"), str) or not isinstance(obj.get("text2"), str):
                continue
            lab = obj.get("label")
            if lab not in (0, 1):
                continue
            out.append({"text1": obj["text1"], "text2": obj["text2"], "label": int(lab)})
            if limit is not None and len(out) >= limit:
                break
    return out


def to_crossencoder_inputs(pairs: Sequence[Dict[str, Any]]) -> Tuple[List[Tuple[str, str]], List[float]]:
    """Create inputs for a sentence-transformers CrossEncoder.

    Returns:
      - texts: list of (text1, text2)
      - labels: list of floats (0.0 or 1.0)
    """
    texts: List[Tuple[str, str]] = []
    labels: List[float] = []
    for p in pairs:
        texts.append((p["text1"], p["text2"]))
        labels.append(float(p["label"]))
    return texts, labels

