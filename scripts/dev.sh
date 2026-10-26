#!/usr/bin/env bash
# Run the API (:8000) and the Vite dev server (:5173) together; Ctrl-C stops both.
set -euo pipefail
cd "$(dirname "$0")/.."

export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
if [ -s "${NVM_DIR:-$HOME/.nvm}/nvm.sh" ]; then
  # shellcheck disable=SC1091
  . "${NVM_DIR:-$HOME/.nvm}/nvm.sh"
  nvm use >/dev/null 2>&1 || true
fi

pids=()
cleanup() {
  trap - INT TERM EXIT
  kill "${pids[@]}" 2>/dev/null || true
  wait 2>/dev/null || true
}
trap cleanup INT TERM EXIT

(cd backend && exec uv run uvicorn app.main:app --reload --port 8000) &
pids+=($!)
(cd frontend && exec npm run dev) &
pids+=($!)

echo "API: http://localhost:8000/docs   App: http://localhost:5173"
# Exit as soon as either server dies (bash 3.2 on macOS has no `wait -n`).
while kill -0 "${pids[0]}" 2>/dev/null && kill -0 "${pids[1]}" 2>/dev/null; do
  sleep 1
done
