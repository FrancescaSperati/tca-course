#!/usr/bin/env bash
# Install everything needed to run the app: uv, Node 20+, backend and frontend deps.
set -euo pipefail
cd "$(dirname "$0")/.."

MIN_NODE=20

node_major() { node -p 'process.versions.node.split(".")[0]' 2>/dev/null || echo 0; }

# --- uv ---
if ! command -v uv >/dev/null 2>&1; then
  echo "==> Installing uv"
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
fi

# --- Node ---
if [ "$(node_major)" -lt "$MIN_NODE" ] && [ -s "${NVM_DIR:-$HOME/.nvm}/nvm.sh" ]; then
  echo "==> Node is older than $MIN_NODE, switching via nvm (.nvmrc)"
  # shellcheck disable=SC1091
  . "${NVM_DIR:-$HOME/.nvm}/nvm.sh"
  nvm install
  nvm use
fi
if [ "$(node_major)" -lt "$MIN_NODE" ]; then
  echo "Node $MIN_NODE+ is required (found: $(node -v 2>/dev/null || echo none)). Install it, e.g. 'nvm install 22'." >&2
  exit 1
fi

echo "==> Backend dependencies"
(cd backend && uv sync)

echo "==> Frontend dependencies"
(cd frontend && npm install)

echo "Setup complete. Run 'make dev' to start both servers."
