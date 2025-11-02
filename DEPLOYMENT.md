# Render Deployment Guide

This guide walks you through deploying the FastAPI backend to Render.

## Quick Setup (Using render.yaml)

If you have `render.yaml` in your repo:

1. Go to https://render.com
2. Click "New" → "Blueprint"
3. Connect your GitHub repository
4. Render will auto-detect `render.yaml` and deploy

## Manual Setup

If you prefer to set up manually or `render.yaml` isn't detected:

### 1. Create a New Web Service

1. Go to https://render.com
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Select your repository

### 2. Configure Service Settings

#### Basic Settings:
- **Name:** `llm-checker-backend` (or your preferred name)
- **Region:** Choose closest to you (e.g., Oregon, Frankfurt)
- **Branch:** `main` (or your default branch)
- **Root Directory:** `backend`
- **Runtime:** `Python 3`
- **Plan:** `Free` (spins down after inactivity) or `Starter` (always-on)

#### Build Settings:
- **Build Command:**
  ```bash
  pip install --upgrade pip && pip install -r requirements.txt && python -m spacy download en_core_web_sm
  ```

- **Start Command:**
  ```bash
  uvicorn app:app --host 0.0.0.0 --port $PORT
  ```

### 3. Environment Variables

Click "Advanced" → "Environment Variables" and add:

| Key | Value | Description |
|-----|-------|-------------|
| `PYTHON_VERSION` | `3.11` | Python version to use |
| `SEARX_URL` | `http://127.0.0.1:8080/search` | SearXNG instance URL (update if you have one deployed) |
| `SEARX_TIMEOUT_S` | `15` | Timeout for SearXNG requests |

**Note:** Render provides `$PORT` automatically - don't set it manually.

#### Option: Import from .env

If you created `backend/.env.example`, you can:
1. Copy it to `backend/.env`
2. Fill in your values
3. In Render dashboard, click "Import from .env file"
4. Upload your `backend/.env` file

**Important:** Never commit `.env` file to Git! Only commit `.env.example`.

### 4. Deploy

Click "Create Web Service" and wait for deployment.

- **First deployment:** May take 10-15 minutes (downloads ML models)
- **Free tier:** First request after spin-down takes ~30 seconds

### 5. Get Your Backend URL

After deployment, you'll get a URL like:
```
https://llm-checker-backend.onrender.com
```

Your API endpoint will be:
```
https://llm-checker-backend.onrender.com/check
```

### 6. Update Frontend Configuration

Edit `config.js` in your repository:

```javascript
window.API_URL = 'https://llm-checker-backend.onrender.com/check';
```

Commit and push. Users can now use the site without configuration!

## Troubleshooting

### Build Fails
- Check that `backend/requirements.txt` exists
- Verify Python version is 3.11
- Check build logs for specific errors

### Service Won't Start
- Verify start command is correct
- Check that `backend/app.py` exists
- Review service logs

### SearXNG Not Working
- Default `SEARX_URL` points to localhost (won't work on Render)
- Either deploy SearXNG separately or update `SEARX_URL` to your SearXNG instance
- You can temporarily disable SearXNG dependency if not using it

### Models Taking Too Long
- First deployment downloads ML models (~1-2 GB)
- Subsequent deployments cache models
- Free tier has limited memory - may need to upgrade

## Free Tier Limitations

- **Spins down:** After 15 minutes of inactivity
- **Cold starts:** First request after spin-down takes ~30 seconds
- **Memory:** May be limited for large ML models
- **Bandwidth:** Limited monthly bandwidth

**Upgrade to Starter ($7/month)** for:
- Always-on service
- More memory
- Better performance

## Next Steps

1. Test your deployment: `https://your-service.onrender.com/docs`
2. Update `config.js` with your backend URL
3. Test the frontend with the new backend

