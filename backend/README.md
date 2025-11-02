# LLM Checker Backend

FastAPI backend for fact-checking LLM outputs.

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Run server
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

- API docs: `http://localhost:8000/docs`
- Main endpoint: `POST http://localhost:8000/check`

## Deployment

### Render

The repository includes a `render.yaml` file for automatic deployment:

1. Push code to GitHub
2. Go to https://render.com
3. Connect your GitHub repository
4. Render will automatically detect `render.yaml` and deploy

### Manual Render Setup

If you prefer manual setup:

- **Root Directory:** `backend`
- **Build Command:** `pip install -r requirements.txt && python -m spacy download en_core_web_sm`
- **Start Command:** `uvicorn app:app --host 0.0.0.0 --port $PORT`

### Environment Variables

- `SEARX_URL`: URL to your SearXNG instance (default: `http://127.0.0.1:8080/search`)
- `SEARX_TIMEOUT_S`: Timeout for SearXNG requests (default: `15`)

## Notes

- **Free tier on Render:** Services spin down after 15 minutes of inactivity. First request after spin-down may take ~30 seconds to start.
- **ML Models:** The backend downloads ML models on first startup. This may take several minutes on first deployment.
- **Memory requirements:** ML models require significant memory. Free tier may have limitations.

