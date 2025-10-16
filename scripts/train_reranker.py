import argparse
import os
import sys
from typing import Any, Dict, List, Tuple

import torch
from torch.utils.data import DataLoader

# Allow importing project modules when running from repo root
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from backend.datasets.hover_loader import (  # noqa: E402
    load_reranker_pairs,
    to_crossencoder_inputs,
)

try:  # Optional dependency
    import wandb  # type: ignore
except Exception:  # pragma: no cover
    wandb = None

from sentence_transformers import InputExample  # type: ignore
from sentence_transformers.cross_encoder import CrossEncoder  # type: ignore


def pairs_to_examples(
    pairs: List[Dict[str, Any]]
) -> List[InputExample]:
    texts, labels = to_crossencoder_inputs(pairs)
    return [InputExample(texts=list(t), label=float(l)) for t, l in zip(texts, labels)]


@torch.inference_mode()
def evaluate_accuracy(model: CrossEncoder, examples: List[InputExample], batch_size: int = 32) -> Tuple[float, float]:
    """Return (accuracy, mean_score) with 0.5 threshold."""
    texts = [ex.texts for ex in examples]
    labels = torch.tensor([ex.label for ex in examples], dtype=torch.float32)
    scores = torch.tensor(model.predict(texts, batch_size=batch_size), dtype=torch.float32)
    preds = (scores >= 0.5).float()
    acc = (preds == labels).float().mean().item()
    mean_score = scores.mean().item()
    return acc, mean_score


def main():
    ap = argparse.ArgumentParser(description="Train a CrossEncoder reranker with optional W&B logging")
    ap.add_argument("--train", required=True, help="Path to train pairs JSONL (text1,text2,label)")
    ap.add_argument("--dev", help="Optional path to dev pairs JSONL for eval")
    ap.add_argument("--model", default="cross-encoder/ms-marco-MiniLM-L-6-v2", help="Base CrossEncoder model ID")
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--epochs", type=int, default=1)
    ap.add_argument("--lr", type=float, default=2e-5)
    ap.add_argument("--warmup-steps", type=int, default=0)
    ap.add_argument("--output-dir", default="models/reranker")
    ap.add_argument("--wandb-project", help="W&B project name to enable logging")
    ap.add_argument("--wandb-run-name", help="Optional W&B run name")
    args = ap.parse_args()

    train_pairs = load_reranker_pairs(args.train)
    if not train_pairs:
        raise SystemExit(f"No training pairs found in {args.train}")
    train_examples = pairs_to_examples(train_pairs)

    dev_examples: List[InputExample] = []
    if args.dev:
        dev_pairs = load_reranker_pairs(args.dev)
        dev_examples = pairs_to_examples(dev_pairs)

    # Init W&B if requested
    run = None
    if args.wandb_project and wandb is not None:
        run = wandb.init(project=args.wandb_project, name=args.wandb_run_name, config={
            "model": args.model,
            "batch_size": args.batch_size,
            "epochs": args.epochs,
            "lr": args.lr,
            "warmup_steps": args.warmup_steps,
            "train_path": args.train,
            "dev_path": args.dev,
        })

    model = CrossEncoder(args.model, num_labels=1, max_length=512)

    train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=args.batch_size)

    # sentence-transformers CrossEncoder.fit handles optimizer/scheduler internally
    model.fit(
        train_dataloader=train_dataloader,
        epochs=args.epochs,
        warmup_steps=args.warmup_steps,
        optimizer_params={"lr": args.lr},
        output_path=args.output_dir,
        use_amp=True,
    )

    # Final evaluation (post-training)
    if dev_examples:
        acc, mean_score = evaluate_accuracy(model, dev_examples, batch_size=args.batch_size)
        print(f"Dev accuracy={acc:.4f} mean_score={mean_score:.4f}")
        if run is not None:
            wandb.log({"dev/accuracy": acc, "dev/mean_score": mean_score})

    if run is not None:
        run.finish()

    print(f"Model saved to: {args.output_dir}")


if __name__ == "__main__":
    main()

