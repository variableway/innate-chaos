#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[findicators]${NC} $*"; }

# Ensure .env exists
if [ ! -f backend/.env ]; then
  cp backend/.env.example backend/.env
  log "Created backend/.env from .env.example"
  log "${YELLOW}Edit backend/.env to add your FRED_API_KEY${NC}"
fi

# Start TimescaleDB
log "Starting TimescaleDB..."
docker compose up -d
log "Waiting for database..."
sleep 3

# Start backend
log "Starting backend (FastAPI on :8000)..."
(cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000) &
BACKEND_PID=$!

# Start frontend
log "Starting frontend (Next.js on :3000)..."
(cd frontend && pnpm dev) &
FRONTEND_PID=$!

log ""
log "${GREEN}Findicators is running!${NC}"
log "  Frontend:  http://localhost:3000"
log "  Backend:   http://localhost:8000"
log "  API Docs:  http://localhost:8000/docs"
log ""
log "Press Ctrl+C to stop all services"

cleanup() {
  log "Stopping services..."
  kill $BACKEND_PID 2>/dev/null || true
  kill $FRONTEND_PID 2>/dev/null || true
  wait 2>/dev/null || true
  log "Stopped."
}
trap cleanup EXIT INT TERM

wait
