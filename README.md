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

**For GitHub Pages:**

The default `localhost:8000` will NOT work on GitHub Pages. Users need to:
1. Deploy the FastAPI backend to a publicly accessible URL
2. Use the settings panel (⚙️ icon) to configure the backend URL

**Alternative:** You can also pre-configure in `config.js` (see file for instructions)

## Notes

- Reranker training now runs in Colab; see `docs/TRAINING.md` for links and workflow.
