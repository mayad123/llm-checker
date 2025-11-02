// Configuration for API URL
// For GitHub Pages, update this with your deployed backend URL
// Examples:
// - Heroku: 'https://your-app.herokuapp.com/check'
// - Railway: 'https://your-app.railway.app/check'
// - AWS/Other: 'https://your-api-domain.com/check'

// ========================================
// SET A DEFAULT PUBLIC BACKEND URL HERE
// ========================================
// Uncomment and set a public backend URL for all users:
// window.API_URL = 'https://your-public-backend-url.com/check';

// If you're hosting a public backend for GitHub Pages users, set it above.
// This will be the default URL for all visitors to the GitHub Pages site.
// Users can still override it using the settings panel (⚙️ icon).

// If not set, defaults to localhost for local development
// For GitHub Pages visitors, they'll need to configure their own backend URL
if (typeof window !== 'undefined' && !window.API_URL) {
  // Check if we're on GitHub Pages (github.io domain)
  if (window.location.hostname.includes('github.io')) {
    // No default backend - users must configure their own
    // Or uncomment the line above to provide a public backend
    console.info('ℹ️ No default backend configured for GitHub Pages.');
    console.info('Users can configure their own backend URL using the settings panel (⚙️ icon).');
  }
}

