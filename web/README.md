# LLM Fact Checker - Web Interface

A modern, interactive web interface for fact-checking LLM outputs.

## Local Development

```bash
cd web
npm install
npm run dev
```

The app will be available at `http://localhost:3000`.

## Building for Production

```bash
npm run build
# or
npm run export
```

The static files will be in the `out` directory.

## Environment Variables

- `NEXT_PUBLIC_API_URL`: The backend API URL (defaults to `/api/check` for local development)

## Project Structure

```
web/
├── app/
│   ├── api/          # API routes (only works in dev mode)
│   ├── layout.tsx     # Root layout
│   └── page.tsx       # Main page component
├── public/            # Static assets
├── package.json       # Dependencies
└── next.config.js     # Next.js configuration
```

