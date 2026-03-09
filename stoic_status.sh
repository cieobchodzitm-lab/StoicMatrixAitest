#!/usr/bin/env bash
# stoic_status.sh – StoicMatrix AI system quick-status report
# Usage: bash stoic_status.sh

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

check() {
  local label="$1"
  local cmd="$2"
  if eval "$cmd" &>/dev/null; then
    printf "  ${GREEN}🟢 %-25s OK${NC}\n" "$label"
  else
    printf "  ${RED}🔴 %-25s UNREACHABLE${NC}\n" "$label"
  fi
}

echo ""
echo "╔══════════════════════════════════════╗"
echo "║     StoicMatrix AI – Status Report   ║"
echo "╚══════════════════════════════════════╝"
echo "  $(date '+%Y-%m-%d %H:%M:%S %Z')"
echo ""

echo "── Services ─────────────────────────────"
check "Memory5 API   :8080"  "curl -sf http://localhost:8080/health"
check "PostgreSQL     :5432"  "pg_isready -h localhost -p 5432 -U postgres"
check "Ollama         :11434" "curl -sf http://localhost:11434/api/tags"
check "Chroma         :8000"  "curl -sf http://localhost:8000/api/v1/heartbeat"

echo ""
echo "── Docker containers ────────────────────"
if command -v docker &>/dev/null; then
  docker ps --format "  {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || \
    printf "  ${YELLOW}docker ps failed (daemon not running?)${NC}\n"
else
  printf "  ${YELLOW}docker not found on PATH${NC}\n"
fi

echo ""
echo "── Crisis Agents (last 5 log lines) ─────"
COMPOSE_FILE="$HOME/.stoic-matrix/l7-bridge/docker-compose.yml"
if [ -f "$COMPOSE_FILE" ]; then
  docker-compose -f "$COMPOSE_FILE" logs --tail=5 crisis-agents 2>/dev/null || \
    printf "  ${YELLOW}Could not fetch crisis-agent logs${NC}\n"
else
  printf "  ${YELLOW}Compose file not found at %s${NC}\n" "$COMPOSE_FILE"
fi

echo ""
echo "── Done ─────────────────────────────────"
echo ""
