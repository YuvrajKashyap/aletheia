# Vercel Frontend Deployment

This is a readiness guide only. Do not deploy from this step unless the project owner explicitly starts the deployment step.

## Project Setup

- Connect the GitHub repository in Vercel.
- Set the project root to `apps/web`.
- Use the Next.js framework preset.
- Install command: `npm install`
- Build command: `npm run build`
- Output is handled by Vercel for Next.js.

## Environment

Set this Vercel environment variable:

```text
NEXT_PUBLIC_API_BASE_URL=https://<backend-api-domain>
```

If the backend is not deployed yet, the frontend can still build and deploy. Runtime pages will show honest API errors instead of fake fallback data.

## Custom Domain

Later, attach:

```text
aletheia.yuvrajkashyap.com
```

After the custom domain is active, add it to backend `CORS_ALLOWED_ORIGINS`.

## Validation

Before deploying, run from the repo root:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/powershell/production-build-check.ps1
```

No fake API fallback should be added for Vercel. The real backend API remains the source of truth.
