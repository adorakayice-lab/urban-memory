# aurelium-nexus (minimal scaffold)

This is a small, runnable scaffold that demonstrates a monorepo layout with:

- `apps/web` — Vite + React lightweight front-end (placeholder components: `TopBar`, `AIOrb`, `PortfolioSphere`).
- `apps/api` — FastAPI backend with a simple `/ai` endpoint.

Quick start (open two terminals):

Terminal 1 — web:
```bash
cd aurelium-nexus/apps/web
npm install
npm run dev
```

Terminal 2 — api:
```bash
cd aurelium-nexus/apps/api
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Run everything with Docker Compose:

```bash
docker compose up --build
```

Wallet notes
- The web app uses an injected wallet (MetaMask) via `ethers` for quick local dev.
- When you connect, the frontend will call `/nft-check` with header `x-api-key: dev-api-key` to determine NFT gating.

Telemetry opt-in (web): open the browser console and call:

```js
localStorage.setItem('aurelium_telemetry','1')
```

Disable telemetry:

```js
localStorage.setItem('aurelium_telemetry','0')
```

Notes:
- This scaffold is intentionally minimal and focuses on getting a local dev environment running quickly.
- If you want the full, production-grade project you described (Next.js 15, React 19, AI model integrations, token/gateway logic, on-chain systems, etc.), we should iterate feature-by-feature — I can scaffold those parts next.
