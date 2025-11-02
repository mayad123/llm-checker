// Configuration for API URL
// For GitHub Pages, update this with your deployed backend URL
// Examples:
// - Heroku: 'https://your-app.herokuapp.com/check'
// - Railway: 'https://your-app.railway.app/check'
// - AWS/Other: 'https://your-api-domain.com/check'

// Uncomment and set your API URL:
// window.API_URL = 'https://your-backend-url.com/check';

// If not set, defaults to localhost for local development
// For GitHub Pages, this MUST be set to a publicly accessible URL
if (typeof window !== 'undefined' && !window.API_URL) {
  // Check if we're on GitHub Pages (github.io domain)
  if (window.location.hostname.includes('github.io')) {
    // Default for GitHub Pages - UPDATE THIS with your backend URL
    window.API_URL = 'http://localhost:8000/check'; // ⚠️ UPDATE THIS!
    
    // Show a warning if using localhost on GitHub Pages
    console.error('⚠️ API_URL is not configured for GitHub Pages!');
    console.error('Please update config.js with your backend API URL.');
  }
}

