Reranker Training

Overview
- Training for the Cross-Encoder reranker now runs in Colab.
- Local data prep remains in this repo; training/logging happens in the notebook using Weights & Biases.

Links
- Colab notebook: https://colab.research.google.com/drive/1TL19BQ7eSKKdLtv54qufw-aw6OkmTEv9?usp=chrome_ntp
- W&B project: https://wandb.ai/mayad123/reranker?nw=nwusermayad123

Workflow
- Prepare data locally:
  - Use `scripts/prepare_hover.py` to create JSONL pairs under `data/processed/hover/`.
- Move data to Colab:
  - Upload the processed JSONL files or mount Google Drive in the notebook.
- Run training in Colab:
  - Configure W&B in the notebook to log metrics and, optionally, model artifacts.
- Bring model back:
  - Option A: Download/export from Colab to this repo under `models/reranker/`.
  - Option B: Pull from W&B artifacts during serving.

Note
- The local `scripts/train_reranker.py` is deprecated and now just points to the Colab/W&B links for clarity.
