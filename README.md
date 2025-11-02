# llm-checker

## Web Interface

The web interface is available as a standalone HTML file (`index.html`) that can be deployed to GitHub Pages.

### GitHub Pages Deployment

The site is automatically deployed to GitHub Pages via GitHub Actions. The `index.html` file contains the complete application with Tailwind CSS via CDN.

### Configuration

**User Configuration (Easiest Method):**

Users can configure the API URL directly in the browser:
1. Click the ⚙️ settings icon in the header
2. Enter your backend API URL (e.g., `https://your-backend.herokuapp.com/check`)
3. Click "Test" to verify the connection
4. Click "Save" to save it (stored in browser's localStorage)

**What goes in the API URL:**

The API URL should point to your FastAPI backend's `/check` endpoint:
- **Format:** `https://your-backend-url.com/check`
- **Must end with:** `/check` (the app will auto-add it if missing)
- **Examples:**
  - Local: `http://localhost:8000/check`
  - Heroku: `https://your-app.herokuapp.com/check`
  - Railway: `https://your-app.railway.app/check`
  - AWS/Other: `https://your-api-domain.com/check`

**For GitHub Pages Visitors:**

The default `localhost:8000` will NOT work on GitHub Pages. Visitors have three options:

1. **Use a Public Backend (if provided)**
   - Check if the site owner has set a default backend in `config.js`
   - Or ask the site owner for a public API URL

2. **Deploy Your Own Backend**
   - Clone this repository
   - Deploy the FastAPI backend (`backend/app.py`) to a free service:
     - **Railway** (recommended): Connect GitHub repo, auto-deploys
     - **Render**: Connect GitHub repo, free tier available
     - **Heroku**: Requires credit card but has free tier
   - You'll get a URL like `https://your-app.railway.app/check`
   - Use the settings panel (⚙️ icon) to configure it

3. **Run Backend Locally** (for testing)
   ```bash
   cd backend
   pip install -r requirements.txt
   python -m uvicorn app:app --host 0.0.0.0 --port 8000
   ```
   Then use `http://localhost:8000/check` (only works locally)

**For Site Owners - Enable Zero-Config for Users:**

If you want users to use the site **without any configuration**:
1. Deploy your FastAPI backend (`backend/app.py`) to a free service:
   - **Railway** (recommended): https://railway.app - Connect GitHub repo, auto-deploys
   - **Render**: https://render.com - Free tier available (see below for setup)
   - **Heroku**: Requires credit card but has free tier

2. **For Render deployment:**
   - Push your code to GitHub
   - Go to https://render.com and connect your GitHub repo
   - Render will automatically detect `render.yaml` and deploy
   - Or manually create a Web Service:
     - **Root Directory:** `backend`
     - **Build Command:** `pip install -r requirements.txt && python -m spacy download en_core_web_sm`
     - **Start Command:** `uvicorn app:app --host 0.0.0.0 --port $PORT`
     - **Python Version:** 3.11

3. Get your backend URL (e.g., `https://llm-checker-backend.onrender.com`)

4. Edit `config.js` and uncomment/set:
   ```javascript
   window.API_URL = 'https://llm-checker-backend.onrender.com/check';
   ```

5. Commit and push - All visitors will automatically use this backend!

**Result:** Users can immediately start using the fact-checker without any setup. They can still override it in settings (⚙️ icon) if needed.

## Notes

- Reranker training now runs in Colab; see `docs/TRAINING.md` for links and workflow.
