# CLAUDE.md — StoicMatrixAitest

Angel Guardian Technologies / Stoic Matrix — multi-surface monorepo.

## What this repo is

| Area | Path | Stack |
|------|------|--------|
| L7 CNOTA dashboard | `frontend/`, `backend/` | React 18 + Vite + Chart.js · FastAPI + Pydantic |
| Puter React template | `src/`, root `package.json` | React 19 + Vite + TypeScript + ESLint |
| Memory layer | `Stoic-Matrix-Layer3/` | Python vector memory |
| Protocol bridge | `Stoic-Matrix-Layer4/` | Python event bus / stream |
| Deploy | `Dockerfile`, `docker-compose.yml`, `deploy_to_hf.*` | Docker · HF Spaces port **7860** |

## Hard rules

1. **Never commit secrets** — `.env`, `credentials.json`, `HF_TOKEN`, API keys, private keys.
2. **Do not hand-edit lockfiles** — change deps via `npm install` / `npm ci` only.
3. **Docker before compose** — run `docker info`; if it hangs or errors, stop and tell the user to fix Docker Desktop. Do not spin forever on `docker compose`.
4. **HF Spaces constraints** — image runs as UID **1000**, listens on **7860**, README frontmatter `sdk: docker`.
5. **API vs SPA** — `/api/*` must never be swallowed by static SPA fallback (`backend/main.py`).
6. Prefer **Python 3.11** for backend (matches Docker). Local Python 3.14 often fails on pydantic-core wheels.

## Common commands

```bash
# L7 frontend
cd frontend && npm ci && npm run build && npm run dev

# L7 backend
cd backend && pip install -r requirements.txt && python main.py --port 7860

# Docker app (+ postgres)
docker compose up --build app

# Full stack extras
docker compose --profile full up --build

# HF deploy (token required)
# export HF_TOKEN=...   /   $env:HF_TOKEN="..."
./deploy_to_hf.sh <hf_user> <space_name>
# Windows: .\deploy_to_hf.ps1 -HfUser ... -RepoName ...

# Offline zip
./scripts/create-deployment-package.ps1

# Root Puter app
npm ci && npm run lint && npm run build
```

## Health checks

- API: `GET http://localhost:7860/api/health`
- UI: `http://localhost:7860/`
- Docs: `http://localhost:7860/docs`

## Claude Code layout

```
.claude/
  settings.json          # hooks + permissions
  agents/                # specialized reviewers
  skills/deploy-l7/      # /deploy-l7 skill
  hooks/                 # hook helper scripts
```

Use **`/deploy-l7`** for build + smoke deploy. Use agent **deploy-smoke-reviewer** on Dockerfile/backend/compose PRs.

## PR / branch notes

- Active deploy work: `copilot/create-deployment-package`, PR history around L7 CNOTA.
- After adding GitHub Actions workflows, token needs `workflow` scope: `gh auth refresh -h github.com -s workflow`.
