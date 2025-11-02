# llm-checker

Fact-checking system for LLM outputs using semantic search, reranking, and natural language inference.

## Features

- Extract factual claims from LLM responses
- Search and retrieve relevant sources
- Verify claims with NLI models (supported/contradicted/unclear)
- Modern web interface with interactive UI

## Tech Stack

- **Backend:** FastAPI, PyTorch, spaCy, Sentence Transformers
- **Frontend:** HTML, CSS, JavaScript (Tailwind CSS)
- **Deployment:** GitHub Pages (frontend), Render/Railway (backend)

## Quick Start

```bash
# Backend
cd backend
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python -m uvicorn app:app --host 0.0.0.0 --port 8000

# Frontend
# Open index.html in browser or deploy to GitHub Pages
```
