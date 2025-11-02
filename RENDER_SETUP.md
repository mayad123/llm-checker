# Render Web Service Setup Guide

When setting up your web service on Render, here are the exact values to enter:

## Basic Settings

- **Name:** `llm-checker-backend` (or your preferred name)
- **Region:** Choose closest to you
- **Branch:** `main`
- **Root Directory:** `backend` ⚠️ **IMPORTANT**
- **Runtime:** `Python 3`

## Build & Deploy Settings

### Build Command:
```bash
pip install --upgrade pip && pip install -r requirements.txt && python -m spacy download en_core_web_sm
```

### Start Command:
```bash
uvicorn app:app --host 0.0.0.0 --port $PORT
```

**Important Notes:**
- Root Directory **must be** `backend` (not root of repo)
- Start command uses `$PORT` (provided automatically by Render)
- The `cd backend` in render.yaml is handled by Root Directory setting

## Environment Variables

Click "Add Environment Variable" for each:

### Option 1: Enter Manually

| Key | Value |
|-----|-------|
| `PYTHON_VERSION` | `3.11` |
| `SEARX_URL` | `http://127.0.0.1:8080/search` |
| `SEARX_TIMEOUT_S` | `15` |

### Option 2: Import from .env File

1. Create a file `backend/.env` in your local repo:
   ```
   PYTHON_VERSION=3.11
   SEARX_URL=http://127.0.0.1:8080/search
   SEARX_TIMEOUT_S=15
   ```

2. In Render dashboard:
   - Scroll to "Environment Variables" section
   - Click "Import from .env file"
   - Upload your `backend/.env` file
   - Render will import all variables

**Note:** 
- Don't commit `.env` to Git (it's in .gitignore)
- The `.env.example` file in the repo is just a template
- Render's "Import from .env" is for uploading a file, not reading from your repo

## Plan Selection

- **Free:** Spins down after 15 min inactivity (good for testing)
- **Starter ($7/mo):** Always-on, better for production

## After Deployment

1. Wait for first deployment (10-15 minutes for ML models)
2. Get your service URL: `https://llm-checker-backend.onrender.com`
3. Test: Visit `https://llm-checker-backend.onrender.com/docs`
4. Update `config.js`:
   ```javascript
   window.API_URL = 'https://llm-checker-backend.onrender.com/check';
   ```

## Quick Copy-Paste Values

**Start Command:**
```
uvicorn app:app --host 0.0.0.0 --port $PORT
```

**Build Command:**
```
pip install --upgrade pip && pip install -r requirements.txt && python -m spacy download en_core_web_sm
```

**Root Directory:**
```
backend
```

