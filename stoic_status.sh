#!/usr/bin/env bash
# stoic_status.sh — one-shot StoicMatrix system status report
# Usage: bash stoic_status.sh

set -euo pipefail

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
RESET='\033[0m'

ok()   { printf "  ${GREEN}🟢 OK${RESET}     %s\n" "$1"; }
fail() { printf "  ${RED}🔴 FAIL${RESET}   %s\n" "$1"; }
warn() { printf "  ${YELLOW}🟡 WARN${RESET}   %s\n" "$1"; }

check_http() {
  local label="$1" url="$2"
  if curl -sf --max-time 3 "$url" > /dev/null 2>&1; then
    ok "$label ($url)"
  else
    fail "$label — unreachable at $url"
  fi
}

check_port() {
  local label="$1" host="$2" port="$3"
  if (echo > /dev/tcp/"$host"/"$port") 2>/dev/null; then
    ok "$label (${host}:${port})"
  else
    fail "$label — port ${port} not open on ${host}"
  fi
}

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║       StoicMatrix — System Status Report         ║"
echo "╚══════════════════════════════════════════════════╝"
echo "  Generated: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo ""

echo "── Services ──────────────────────────────────────"
check_http "Memory5 API (Spring Boot)" "http://localhost:8080/health"
check_port "PostgreSQL"                "localhost" 5432
check_http "Ollama (qwen:latest)"      "http://localhost:11434"
check_http "Chroma (vector store)"     "http://localhost:8000"

echo ""
echo "── Docker containers ─────────────────────────────"
if command -v docker &>/dev/null; then
  docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || warn "docker ps failed"
else
  warn "Docker not found — skipping container check"
fi

echo ""
echo "── Crisis Agents logs (last 10 lines) ────────────"
BRIDGE_DIR="${STOIC_BRIDGE_DIR:-${HOME}/.stoic-matrix/l7-bridge}"
if [ -d "$BRIDGE_DIR" ]; then
  docker-compose -f "$BRIDGE_DIR/docker-compose.yml" logs --tail=10 crisis-agents 2>/dev/null \
    || warn "Could not fetch crisis-agents logs from $BRIDGE_DIR"
else
  warn "Bridge dir not found: $BRIDGE_DIR (set STOIC_BRIDGE_DIR to override)"
fi

echo ""
echo "── Solana RPC client ─────────────────────────────"
RPC_BIN="${STOIC_SOLANA_BIN:-${HOME}/.stoic-matrix/solana-rpc/target/release/solana-rpc}"
if [ -x "$RPC_BIN" ]; then
  ok "Solana RPC binary present ($(du -sh "$RPC_BIN" | cut -f1))"
else
  warn "Solana RPC binary not found at $RPC_BIN (set STOIC_SOLANA_BIN to override)"
fi

echo ""
echo "──────────────────────────────────────────────────"
echo "  Done. Fix any 🔴 items above before deploying."
echo ""
