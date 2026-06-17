# AI Governance Dashboard

A Next.js 15 compliance dashboard for the toolkit: risk verdict, red-team pass
rate, per-OWASP-category results, and audit volume.

## Data

Reads `data/summary.json` (the shape of the API's `GET /summary`). In production,
fetch it live from the running toolkit API instead of the bundled sample.

## Develop

```bash
cd dashboard
npm install
npm run dev      # http://localhost:3000
npm run build    # production build
```

Stack: Next.js 15 (App Router) · React 19 · Recharts · TypeScript.
