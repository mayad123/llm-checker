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

**For Site Owners:**

If you want to provide a public backend for all GitHub Pages visitors:
1. Deploy your backend to a public URL
2. Edit `config.js` and uncomment: `window.API_URL = 'https://your-backend-url.com/check';`
3. All visitors will use this backend by default (they can still override it)

## Notes

- Reranker training now runs in Colab; see `docs/TRAINING.md` for links and workflow.
