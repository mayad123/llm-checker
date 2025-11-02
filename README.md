# llm-checker

## Web Interface

The web interface is available as a standalone HTML file (`index.html`) that can be deployed to GitHub Pages.

### GitHub Pages Deployment

The site is automatically deployed to GitHub Pages via GitHub Actions. The `index.html` file contains the complete application with Tailwind CSS via CDN.

### Configuration

**For GitHub Pages (REQUIRED):**

You MUST configure the API URL before deploying to GitHub Pages. The default `localhost:8000` will NOT work on GitHub Pages.

1. Edit `config.js` in the repository root
2. Uncomment and set `window.API_URL` to your deployed backend URL:
   ```javascript
   window.API_URL = 'https://your-backend-url.com/check';
   ```
3. Examples:
   - Heroku: `'https://your-app.herokuapp.com/check'`
   - Railway: `'https://your-app.railway.app/check'`
   - AWS/Other: `'https://your-api-domain.com/check'`

**For local development:**

The default `http://localhost:8000/check` works automatically when running locally.

**Important:** You must deploy your FastAPI backend to a publicly accessible URL (Heroku, Railway, AWS, etc.) before using GitHub Pages.

## Notes

- Reranker training now runs in Colab; see `docs/TRAINING.md` for links and workflow.
