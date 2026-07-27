---
name: deploy-l7
description: Build and smoke-test the L7 CNOTA stack (frontend, Docker app service, /api/health). Optional Hugging Face deploy when HF_TOKEN is set. User-invoked only — has side effects (containers, network, possible registry push).
disable-model-invocation: true
---

# /deploy-l7 — L7 CNOTA deploy smoke

## When to use

User runs `/deploy-l7` to validate the local deployment package or push to HF Spaces.

## Preconditions (fail-fast)

1. Confirm repo root contains `Dockerfile`, `docker-compose.yml`, `frontend/`, `backend/`.
2. Run **`docker info`** with a short timeout mindset:
   - If it hangs/errors → **STOP**. Tell user to start Docker Desktop until engine is green.
   - Do **not** loop `docker compose` for minutes.
3. Never print or commit `HF_TOKEN`, `.env`, or API keys.

## Default path (local smoke)

Execute in order:

```bash
# 1) Frontend unit build (fast signal)
cd frontend && npm ci && npm run build && test -f dist/index.html && cd ..

# 2) Docker gate
docker info

# 3) Build & start app (+ postgres dependency as defined in compose)
docker compose up --build -d app

# 4) Health
curl -fsS http://127.0.0.1:7860/api/health
# or PowerShell: Invoke-RestMethod http://127.0.0.1:7860/api/health
```

Report:

| Step | Result |
|------|--------|
| frontend build | OK/FAIL |
| docker engine | OK/FAIL |
| compose up | OK/FAIL |
| `/api/health` | body + status |

On failure: `docker compose logs app --tail 100` (or equivalent).

## Optional: HF Spaces

Only if user asks **and** `HF_TOKEN` is set:

```bash
# bash
./deploy_to_hf.sh <hf_username> <space_name>

# PowerShell
.\deploy_to_hf.ps1 -HfUser <hf_username> -RepoName <space_name>
```

## Optional: offline zip

```powershell
.\scripts\create-deployment-package.ps1
```

## Done criteria

- Local: health JSON with `"status": "ok"` (or equivalent) from `/api/health`
- HF: script exit 0 and space URL returned
- No secrets written into git

## Related

- Agent: `deploy-smoke-reviewer` for PR review
- Docs: root `CLAUDE.md`, `README.md` HF section
