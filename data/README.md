HoVer dataset layout and usage

Structure
- `data/raw/hover/` — place original HoVer `.jsonl` files here (train/dev/test).
- `data/processed/hover/` — generated files ready for reranker training/eval.

Suggested filenames
- Raw: `data/raw/hover/hover_train.jsonl`, `hover_dev.jsonl`, `hover_test.jsonl`.
- Processed: `data/processed/hover/reranker_train.jsonl`, `reranker_dev.jsonl`, `reranker_test.jsonl`.

Prepare data
Run the script to convert HoVer JSONL to simple pairwise reranker inputs:

`python scripts/prepare_hover.py --in data/raw/hover/hover_train.jsonl --out data/processed/hover/reranker_train.jsonl`

Field mapping
- Defaults expect: `claim`, `positive_passages`, and `negative_passages`.
- Override with: `--claim-key`, `--pos-key`, `--neg-key`.

Output format (JSONL per line)
- `{ "text1": <claim>, "text2": <passage>, "label": 1|0 }`

Loading in backend
- Use `backend/datasets/hover_loader.py`:
  - `load_reranker_pairs(path)` returns list of dicts.
  - `to_crossencoder_inputs(pairs)` returns `(texts, labels)` ready for a CrossEncoder.

