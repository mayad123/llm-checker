import sys

NOTE = (
    "Training has moved to Colab. This local script is deprecated.\n"
    "Use the Colab notebook instead and log to W&B:\n"
    "  Colab: https://colab.research.google.com/drive/1TL19BQ7eSKKdLtv54qufw-aw6OkmTEv9?usp=chrome_ntp\n"
    "  Weights & Biases project: https://wandb.ai/mayad123/reranker?nw=nwusermayad123\n"
    "Typical flow: prepare data with scripts/prepare_hover.py, upload to Colab, train,\n"
    "then download/export the model to models/reranker or pull from W&B artifacts.\n"
)

def main() -> None:
    raise SystemExit(NOTE)


if __name__ == "__main__":
    main()
