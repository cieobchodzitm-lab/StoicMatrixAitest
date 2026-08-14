# Deployment package CI

GitHub Actions workflow file was prepared but not pushed (OAuth token lacks `workflow` scope).

To enable CI, re-auth:

```powershell
gh auth refresh -h github.com -s workflow
```

Then add `.github/workflows/docker-deploy-package.yml` with jobs:
- frontend: `npm ci && npm run build`
- backend: Python 3.11 `pip install -r requirements.txt` + `import main`
- docker: `docker build` + curl `/api/health`
