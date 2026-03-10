#!/usr/bin/env bash
# deploy_to_hf.sh — Deploy L7 CNOTA Dashboard to HuggingFace Spaces
# Usage: ./deploy_to_hf.sh <hf_username> <repo_name>
# Requires: HF_TOKEN env var, docker, git

set -euo pipefail

HF_USER="${1:?Usage: $0 <hf_username> <repo_name>}"
REPO_NAME="${2:?Usage: $0 <hf_username> <repo_name>}"
IMAGE="l7-cnota:latest"
HF_REGISTRY="registry.huggingface.co"
FULL_IMAGE="${HF_REGISTRY}/${HF_USER}/${REPO_NAME}:latest"

if [[ -z "${HF_TOKEN:-}" ]]; then
  echo "❌  Error: HF_TOKEN environment variable is not set."
  echo "   Export it with: export HF_TOKEN=\"hf_your_token_here\""
  exit 1
fi

echo "🏛️  L7 CNOTA Dashboard — HuggingFace Spaces Deployment"
echo "   Space: ${HF_USER}/${REPO_NAME}"
echo ""

# 1. Build Docker image
echo "🔨 Building Docker image…"
docker build -t "${IMAGE}" .
echo "✅ Build complete"

# 2. Tag for HF registry
echo "🏷️  Tagging image for HF registry…"
docker tag "${IMAGE}" "${FULL_IMAGE}"

# 3. Login to HF registry
echo "🔐 Logging in to HuggingFace registry…"
echo "${HF_TOKEN}" | docker login "${HF_REGISTRY}" \
  --username "${HF_USER}" \
  --password-stdin

# 4. Push image
echo "🚀 Pushing image to HuggingFace…"
docker push "${FULL_IMAGE}"
echo "✅ Push complete"

# 5. Create or update HF Space via API
echo "🌐 Creating/updating HuggingFace Space…"
SPACE_CHECK=$(curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer ${HF_TOKEN}" \
  "https://huggingface.co/api/spaces/${HF_USER}/${REPO_NAME}")

if [[ "${SPACE_CHECK}" == "200" ]]; then
  echo "   Space already exists — image push will trigger redeploy"
else
  echo "   Creating new Space…"
  curl -s -X POST \
    -H "Authorization: Bearer ${HF_TOKEN}" \
    -H "Content-Type: application/json" \
    -d "{\"type\": \"space\", \"name\": \"${REPO_NAME}\", \"private\": false, \"sdk\": \"docker\"}" \
    "https://huggingface.co/api/repos/create" \
    | python3 -m json.tool || true
fi

echo ""
echo "✅ Deployment complete!"
echo "🌐 Live at: https://huggingface.co/spaces/${HF_USER}/${REPO_NAME}"
echo ""
echo "Next steps:"
echo "  1. Set HF Secrets in Space settings:"
echo "     - DATABASE_URL"
echo "     - SOLANA_RPC_URL"
echo "     - AGENTOPS_API_KEY"
echo "  2. Monitor logs at: https://huggingface.co/spaces/${HF_USER}/${REPO_NAME}?logs=container"
