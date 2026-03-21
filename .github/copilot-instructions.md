# Project Guidelines

## Code Style
- Prefer small, focused changes that preserve the existing split between the root app (`src/`), dashboard frontend (`frontend/`), and FastAPI backend (`backend/`).
- For root TypeScript code, keep strict typing and avoid `any`; align with `tsconfig.app.json` and existing patterns in `src/App.tsx` and `src/components/WalletPanel.tsx`.
- For dashboard frontend code (`frontend/src`), use functional React components with hooks and keep API calls in `axios` style used by existing components.
- For backend code (`backend/`), keep router-per-domain structure with `APIRouter`, Pydantic models for request bodies, and async endpoints.

## Architecture
- This repository contains two frontend surfaces plus one API backend:
  - Root app (`src/`): Puter.js + React + TypeScript example app.
  - Dashboard frontend (`frontend/`): React + Vite UI for CNOTA dashboard.
  - Backend (`backend/`): FastAPI app with routers in `backend/routers/`.
- Backend serves API under `/api/*` and can also serve built dashboard assets from `frontend/dist` when available.
- Docker setup (`docker-compose.yml`) runs app plus `postgres`, `ollama`, and `chroma` services.

## Build and Test
- Root app commands:
  - `npm install`
  - `npm run dev`
  - `npm run build`
  - `npm run lint`
- Dashboard frontend commands:
  - `cd frontend && npm install`
  - `cd frontend && npm run dev`
  - `cd frontend && npm run build`
- Backend commands:
  - `cd backend && pip install -r requirements.txt`
  - `cd backend && python main.py`
- Full stack via Docker:
  - `docker compose up`
- Health/status script:
  - `bash stoic_status.sh`

## Conventions
- Preserve the Stoic virtue domain model names and API shapes in `backend/routers/cnota.py`, `backend/routers/passport.py`, and `backend/routers/rewards_processor.py`.
- Keep API paths rooted at `/api` and avoid renaming existing endpoints unless all callers are updated.
- Default backend port is `7860` (required for Hugging Face Spaces). Do not change this without updating Docker, deploy script, and runtime docs.
- Keep Hugging Face deployment compatibility constraints intact (container user UID 1000, exposed app port 7860).
- Treat many current backend responses as mock/stub behavior; when adding real integrations, maintain backward-compatible response fields where possible.
- If working on both root app and `frontend/` app simultaneously, account for Vite port collisions and configure alternate dev ports explicitly.
