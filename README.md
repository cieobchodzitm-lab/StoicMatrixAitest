---
title: L7 Rzeczpospolita CNOTA Dashboard
emoji: ⚖️
colorFrom: yellow
colorTo: gray
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# L7 Rzeczpospolita CNOTA — Virtue Governance Dashboard

A full-stack dashboard for the L7 Stoic Virtue Governance system, combining virtue scoring, NFT passports, and on-chain governance metrics.

## Features

- **Virtue Radar** — Radar chart visualizing four Stoic virtues (Sophia, Andreia, Dikaiosyne, Sophrosyne)
- **Score Bars** — Individual virtue progress bars and profile card
- **NFT Passport** — ERC-1155 passport card with on-chain mint button
- **Leaderboard** — Paginated rankings with per-virtue sorting
- **Dark Stoic Theme** — Cinzel serif, gold accents on dark gray

## Architecture

```
.
├── Dockerfile          # Multi-stage: Node 18 build → Python 3.11 runtime
├── docker-compose.yml  # Local dev stack (Postgres, Ollama, Chroma)
├── deploy_to_hf.sh     # One-command HuggingFace Spaces deployment
├── .env.example        # All 72 environment variables documented
├── backend/            # FastAPI + SQLAlchemy
│   ├── main.py
│   ├── requirements.txt
│   └── routers/
│       ├── health.py           # GET /api/health
│       ├── cnota.py            # /api/cnota/{profile,leaderboard,score,stats}
│       ├── passport.py         # /api/passport/{id,metadata,mint}
│       └── rewards_processor.py # Virtue→NFT mint pipeline
└── frontend/           # React 18 + Vite + Chart.js
    ├── src/
    │   ├── App.jsx
    │   └── components/
    │       ├── Layout.jsx
    │       ├── Dashboard.jsx
    │       ├── PassportView.jsx
    │       └── LeaderboardView.jsx
    └── package.json
```

## Local Development

```bash
# App only (recommended first smoke test)
docker compose up --build app postgres

# Full stack (Ollama + Chroma too)
docker compose --profile full up --build

# Frontend only
cd frontend && npm ci && npm run dev

# Backend only (Python 3.11 recommended)
cd backend && pip install -r requirements.txt && python main.py --port 7860
```

## Deploy to HuggingFace Spaces

```bash
export HF_TOKEN="hf_your_token_here"
chmod +x deploy_to_hf.sh
./deploy_to_hf.sh cieobchodzitm l7-cnota-dashboard
```

### Windows (PowerShell)

```powershell
$env:HF_TOKEN = "hf_your_token_here"
.\deploy_to_hf.ps1 -HfUser cieobchodzitm -RepoName l7-cnota-dashboard
```

### Create offline deployment zip

```powershell
.\scripts\create-deployment-package.ps1
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Service health status |
| GET | `/api/cnota/profile/{user_id}` | Virtue profile |
| GET | `/api/cnota/leaderboard` | Top 100 leaderboard |
| POST | `/api/cnota/score` | Calculate score |
| GET | `/api/passport/{user_id}` | NFT passport data |
| POST | `/api/passport/mint` | Queue NFT mint |
| GET | `/api/passport/{user_id}/metadata` | ERC-1155 metadata |

## HF Spaces Constraints

- `USER user:1000` — UID 1000 required
- `EXPOSE 7860` — Fixed port
- `sdk: docker` + `app_port: 7860` in README frontmatter
