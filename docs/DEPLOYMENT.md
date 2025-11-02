# GitHub Pages Deployment Guide

This guide will help you deploy the LLM Fact Checker to GitHub Pages.

## Prerequisites

1. A GitHub repository
2. GitHub Pages enabled in your repository settings
3. A backend API endpoint (since GitHub Pages is static and doesn't support API routes)

## Setup Steps

### 1. Enable GitHub Pages

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Pages**
3. Under **Source**, select **GitHub Actions** (not "Deploy from a branch")
4. Save the settings

### 2. Configure Backend API URL

Since GitHub Pages is static and doesn't support Next.js API routes, you need to configure your backend API URL:

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add a secret named `API_URL` with your backend API URL (e.g., `https://your-backend.com/check`)
5. Save the secret

**Note:** The workflow will use this secret to build the site with the correct API URL. If not set, it defaults to `http://localhost:8000/check` which won't work on GitHub Pages.

### 3. Deploy

The deployment is automatic! Every time you push to the `main` or `master` branch, the GitHub Actions workflow will:

1. Build the Next.js app as a static site
2. Deploy it to GitHub Pages

You can also manually trigger a deployment:
1. Go to the **Actions** tab in your repository
2. Select **Deploy to GitHub Pages** workflow
3. Click **Run workflow**

### 4. Access Your Site

After deployment, your site will be available at:
- `https://<username>.github.io/<repository-name>/`

## Local Development

For local development with the Next.js API routes:

```bash
cd web
npm install
npm run dev
```

The app will be available at `http://localhost:3000` and will use the API route at `/api/check`.

## Manual Build & Test

To test the static export locally:

```bash
cd web
npm run export
```

The static files will be in the `web/out` directory. You can serve them with:

```bash
npx serve out
```

## Troubleshooting

### API Not Working on GitHub Pages

Remember: **API routes don't work on GitHub Pages** because it's a static site. You must:
1. Deploy your backend separately (e.g., Heroku, Railway, AWS, etc.)
2. Set the `API_URL` secret in GitHub to point to your deployed backend

### Base Path Issues

If your repository name is not the root path, update `web/next.config.js`:

```javascript
basePath: process.env.NODE_ENV === 'production' ? '/your-repo-name' : '',
assetPrefix: process.env.NODE_ENV === 'production' ? '/your-repo-name' : '',
```

Then uncomment these lines in `web/next.config.js`.

### Build Failures

Check the **Actions** tab for build errors. Common issues:
- Missing dependencies (run `npm install` locally first)
- TypeScript errors
- Missing environment variables

## Custom Domain

To use a custom domain:

1. Add a `CNAME` file in `web/public/` with your domain
2. Configure DNS records as per GitHub Pages documentation
3. Update repository settings → Pages → Custom domain

