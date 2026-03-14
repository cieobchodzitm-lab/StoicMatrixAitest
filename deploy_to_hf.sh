#!/usr/bin/env bash
# deploy_to_hf.sh — Deploy this project to a Hugging Face Space
#
# Required environment variables:
#   HF_TOKEN        — Hugging Face API token (write access)
#   HF_USERNAME     — Hugging Face username or organisation that owns the Space
#   HF_SPACE_NAME   — Name of the target Hugging Face Space
#
# Optional environment variables:
#   HF_SPACE_SDK    — Space SDK type: "static" (default) or "docker"
#   BUILD_DIR       — Directory containing build output (default: "dist")

set -euo pipefail

# ── Helpers ──────────────────────────────────────────────────────────────────

info()  { echo "[INFO]  $*"; }
error() { echo "[ERROR] $*" >&2; exit 1; }

# ── Configuration ─────────────────────────────────────────────────────────────

HF_TOKEN="${HF_TOKEN:?HF_TOKEN is required}"
HF_USERNAME="${HF_USERNAME:?HF_USERNAME is required}"
HF_SPACE_NAME="${HF_SPACE_NAME:?HF_SPACE_NAME is required}"
HF_SPACE_SDK="${HF_SPACE_SDK:-static}"
BUILD_DIR="${BUILD_DIR:-dist}"

HF_REPO_URL="https://huggingface.co/spaces/${HF_USERNAME}/${HF_SPACE_NAME}"
HF_REPO_GIT="https://huggingface.co/spaces/${HF_USERNAME}/${HF_SPACE_NAME}"

# ── Dependency checks ─────────────────────────────────────────────────────────

command -v git  >/dev/null 2>&1 || error "git is not installed"
command -v node >/dev/null 2>&1 || error "node is not installed"
command -v npm  >/dev/null 2>&1 || error "npm is not installed"

# ── Build the project ─────────────────────────────────────────────────────────

info "Installing dependencies…"
npm ci

info "Building project…"
npm run build

[[ -d "${BUILD_DIR}" ]] || error "Build output directory '${BUILD_DIR}' not found after build"

# ── Prepare Space README (card) ───────────────────────────────────────────────

# Add a minimal YAML front-matter card if README.md does not already have one.
README_SRC="README.md"
TMP_README="$(mktemp)"

if head -1 "${README_SRC}" | grep -q '^---'; then
  cp "${README_SRC}" "${TMP_README}"
else
  {
    printf -- '---\ntitle: %s\nsdk: %s\napp_port: 80\n---\n\n' \
      "${HF_SPACE_NAME}" "${HF_SPACE_SDK}"
    cat "${README_SRC}"
  } > "${TMP_README}"
fi

# ── Clone / update the Space repository ──────────────────────────────────────

WORK_DIR="$(mktemp -d)"

info "Cloning Space repository into temporary directory…"
# Provide credentials via askpass helper to keep the token out of process listings
ASKPASS_SCRIPT="$(mktemp)"
printf '#!/bin/sh\necho "%s"\n' "${HF_TOKEN}" > "${ASKPASS_SCRIPT}"
chmod 700 "${ASKPASS_SCRIPT}"
export GIT_ASKPASS="${ASKPASS_SCRIPT}"
export GIT_USERNAME="${HF_USERNAME}"
trap 'rm -rf "${WORK_DIR}" "${TMP_README}" "${ASKPASS_SCRIPT}"' EXIT

if git ls-remote --exit-code "${HF_REPO_GIT}" HEAD >/dev/null 2>&1; then
  git clone --depth 1 "${HF_REPO_GIT}" "${WORK_DIR}"
else
  # Space does not exist yet — initialise an empty repo and set the remote
  info "Space not found; initialising a new repository…"
  git -C "${WORK_DIR}" init
  git -C "${WORK_DIR}" remote add origin "${HF_REPO_GIT}"
fi

# ── Copy build artefacts into the Space repository ───────────────────────────

info "Copying build output from '${BUILD_DIR}/' to Space repository…"
# Remove existing files except .git
find "${WORK_DIR}" -mindepth 1 -maxdepth 1 ! -name '.git' -exec rm -rf {} +

cp -r "${BUILD_DIR}/." "${WORK_DIR}/"
cp "${TMP_README}" "${WORK_DIR}/README.md"

# For Docker spaces also include the Compose file
if [[ "${HF_SPACE_SDK}" == "docker" ]] && [[ -f "docker-compose.yml" ]]; then
  cp docker-compose.yml "${WORK_DIR}/docker-compose.yml"
fi

# ── Commit and push ───────────────────────────────────────────────────────────

cd "${WORK_DIR}"

git config user.email "deploy-bot@users.noreply.huggingface.co"
git config user.name  "HF Deploy Bot"

git add -A

if git diff --cached --quiet; then
  info "Nothing to commit — Space is already up to date."
else
  COMMIT_MSG="deploy: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
  git commit -m "${COMMIT_MSG}"
  info "Pushing to ${HF_REPO_URL} …"
  git push origin HEAD:main --force-with-lease
  info "Deployment complete → ${HF_REPO_URL}"
fi
