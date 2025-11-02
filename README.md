# llm-checker

## Web Interface

The web interface is available as a standalone HTML file (`index.html`) that can be deployed to GitHub Pages.

### GitHub Pages Deployment

The site is automatically deployed to GitHub Pages via GitHub Actions. The `index.html` file contains the complete application with Tailwind CSS via CDN.

### Configuration

To configure the backend API URL, you can:
1. Set `window.API_URL` in the browser console before using the app
2. Edit `index.html` and update the `API_URL` constant in the script section

Default API URL: `http://localhost:8000/check`

## Notes

- Reranker training now runs in Colab; see `docs/TRAINING.md` for links and workflow.
