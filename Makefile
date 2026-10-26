.PHONY: setup dev test

setup:
	./scripts/setup.sh

dev:
	./scripts/dev.sh

test:
	@export PATH="$$HOME/.local/bin:$$HOME/.cargo/bin:$$PATH"; \
	if [ -s "$${NVM_DIR:-$$HOME/.nvm}/nvm.sh" ]; then . "$${NVM_DIR:-$$HOME/.nvm}/nvm.sh"; nvm use >/dev/null 2>&1 || true; fi; \
	(cd backend && uv run pytest) && (cd frontend && npm run typecheck)
