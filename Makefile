# UP Factory Siting Tool: the commands you run day to day.
# `make` (or `make help`) lists them. Learn: docs/learn/make.md
#
# Works in two places with the same commands:
#   host           macOS / Linux / Windows-WSL2 terminal; the database runs via docker compose
#   Dev Container  UP_SITING_DEVCONTAINER=1; the editor already runs the `db` service beside us,
#                  so database targets talk to it over the network instead of using docker

SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := help

# Settings: .env if present, else the same defaults as .env.example and docker-compose.yml.
# (Never leave them undefined: an exported undefined variable is an EMPTY string, and docker
# compose lets shell variables override .env, so the empty value would win.)
-include .env
POSTGRES_USER     ?= up_siting
POSTGRES_PASSWORD ?= change-me-locally
POSTGRES_DB       ?= up_siting
POSTGRES_PORT     ?= 5432
POSTGRES_HOST     ?= localhost

ifdef UP_SITING_DEVCONTAINER
# Container-to-container: the `db` service on its internal port, whatever .env says for the host.
POSTGRES_HOST := db
POSTGRES_PORT := 5432
PSQL      := PGPASSWORD="$(POSTGRES_PASSWORD)" psql -v ON_ERROR_STOP=1 -h $(POSTGRES_HOST) -p $(POSTGRES_PORT) -U $(POSTGRES_USER) -d $(POSTGRES_DB)
SMOKE_SQL := db/smoke_test.sql
LAB_ARGS  := --ip=0.0.0.0 --no-browser
else
PSQL      := docker compose exec -T db psql -v ON_ERROR_STOP=1 -U $(POSTGRES_USER) -d $(POSTGRES_DB)
SMOKE_SQL := /opt/up-siting/smoke_test.sql
LAB_ARGS  :=
endif
export POSTGRES_USER POSTGRES_PASSWORD POSTGRES_DB POSTGRES_PORT POSTGRES_HOST

UV      := uv
COMPOSE := docker compose

.PHONY: help check-tools env hooks setup lint format test todo ci profiles \
        db-up db-wait db-smoke db-down db-reset db-psql db-logs lab clean host-only

help: ## List the targets
	@grep -hE '^[a-zA-Z_-]+:.*?## ' Makefile \
	  | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

# ---------------------------------------------------------------- setup
check-tools: ## Check that the tools this project needs are installed
	@command -v uv >/dev/null || { echo "uv not found: see docs/SETUP.md"; exit 1; }
ifdef UP_SITING_DEVCONTAINER
	@echo "tools ok (Dev Container): $$(uv --version) | $$(psql --version)"
else
	@command -v docker >/dev/null || { echo "docker not found: see docs/SETUP.md"; exit 1; }
	@docker compose version >/dev/null 2>&1 \
	  || { echo "docker compose v2 not found: see docs/SETUP.md"; exit 1; }
	@echo "tools ok: $$(uv --version) | $$(docker --version) | $$(git --version)"
endif

env: ## Create .env from .env.example if it doesn't exist yet
	@if [ ! -f .env ]; then cp .env.example .env; echo "created .env from .env.example"; fi

hooks: ## Use the repo's git hooks (.githooks/), which work on the host and in the container
	git config core.hooksPath .githooks

setup: check-tools env hooks ## Install Python and dependencies, create .env, enable git hooks
	$(UV) sync --locked
	@echo "setup complete. Next: make test, make lint, make db-up"

# ---------------------------------------------------------------- quality
lint: ## Ruff lint + format check + product-profile validation (CI runs the same)
	$(UV) run ruff check .
	$(UV) run ruff format --check .
	$(UV) run validate-profiles config/product_profiles

format: ## Auto-fix what ruff can, then reformat
	$(UV) run ruff check --fix .
	$(UV) run ruff format .

test: ## Unit and notebook tests (no database needed). Sage's TODOs show as "xfailed"
	$(UV) run pytest

todo: ## Sage's TODO tests as real pass/fail (ignores the xfail marker)
	$(UV) run pytest -m todo --runxfail

ci: lint test ## Run what CI runs (except the database job)

profiles: ## Validate product profiles and list fields still waiting on the partners
	$(UV) run validate-profiles config/product_profiles --show-missing

# ---------------------------------------------------------------- database
ifdef UP_SITING_DEVCONTAINER
db-up: db-wait
	$(MAKE) db-smoke

db-wait:
	@for i in $$(seq 1 30); do \
	  pg_isready -q -h $(POSTGRES_HOST) -p $(POSTGRES_PORT) -U $(POSTGRES_USER) && exit 0; sleep 1; \
	done; echo "database not reachable at $(POSTGRES_HOST):$(POSTGRES_PORT)"; exit 1

db-down db-reset db-logs: host-only

host-only:
	@echo "Inside the Dev Container the editor manages the database container."
	@echo "Run 'make $(MAKECMDGOALS)' from a terminal on your host instead."; exit 1
else
db-up: env ## Start PostGIS (host) or wait for it (Dev Container), then smoke-test it
	$(COMPOSE) up -d --wait db
	$(MAKE) db-smoke

db-down: ## Stop the database (data stays in the pgdata volume) [host only]
	$(COMPOSE) down

db-reset: ## Stop the database and DELETE its data volume (asks first) [host only]
	@read -r -p "Delete the local database volume? [y/N] " ans; [ "$${ans:-N}" = "y" ]
	$(COMPOSE) down -v

db-logs: ## Follow the database logs (Ctrl-C to stop) [host only]
	$(COMPOSE) logs -f db
endif

db-smoke: ## Run db/smoke_test.sql, then the Python integration tests
	$(PSQL) -f $(SMOKE_SQL)
	$(UV) run pytest -m integration

db-psql: ## Open an interactive psql shell on the database
ifdef UP_SITING_DEVCONTAINER
	$(PSQL)
else
	$(COMPOSE) exec db psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)
endif

# ---------------------------------------------------------------- notebooks
lab: ## Start JupyterLab on the EDA notebooks
	$(UV) run jupyter lab notebooks/eda $(LAB_ARGS)

# ---------------------------------------------------------------- housekeeping
clean: ## Remove caches (keeps .venv, data and the database)
	rm -rf .pytest_cache .ruff_cache
	find . -path ./.venv -prune -o -type d -name __pycache__ -exec rm -rf {} +
