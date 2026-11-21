# UP Factory Siting Tool: the commands you run day to day.
# `make` (or `make help`) lists them. Learn: docs/learn/make.md

SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := help

# Read POSTGRES_* from .env when it exists and pass them to every command make runs.
# The leading "-" means "don't fail if .env is missing" (make setup creates it).
-include .env
export POSTGRES_USER POSTGRES_PASSWORD POSTGRES_DB POSTGRES_PORT POSTGRES_HOST

UV      := uv
COMPOSE := docker compose
PSQL    := $(COMPOSE) exec -T db psql -v ON_ERROR_STOP=1 -U $(POSTGRES_USER) -d $(POSTGRES_DB)

.PHONY: help check-tools env setup lint format test todo ci profiles \
        db-up db-smoke db-down db-reset db-psql db-logs lab clean

help: ## List the targets
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) \
	  | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

# ---------------------------------------------------------------- setup
check-tools: ## Check that uv, docker and docker compose v2 are installed
	@command -v uv >/dev/null     || { echo "uv not found: see docs/SETUP.md"; exit 1; }
	@command -v docker >/dev/null || { echo "docker not found: see docs/SETUP.md"; exit 1; }
	@docker compose version >/dev/null 2>&1 \
	  || { echo "docker compose v2 not found: see docs/SETUP.md"; exit 1; }
	@echo "tools ok: $$(uv --version) | $$(docker --version) | $$(git --version)"

env: ## Create .env from .env.example if it doesn't exist yet
	@if [ ! -f .env ]; then cp .env.example .env; echo "created .env from .env.example"; fi

setup: check-tools env ## Install Python and dependencies, create .env, install git hooks
	$(UV) sync --locked
	$(UV) run pre-commit install
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
db-up: env ## Start PostGIS, wait until it is healthy, then run the smoke test
	$(COMPOSE) up -d --wait db
	$(MAKE) db-smoke

db-smoke: ## Run db/smoke_test.sql in the container, then the Python integration test
	$(PSQL) -f /opt/up-siting/smoke_test.sql
	$(UV) run pytest -m integration

db-down: ## Stop the database (data stays in the pgdata volume)
	$(COMPOSE) down

db-reset: ## Stop the database and DELETE its data volume (asks first)
	@read -r -p "Delete the local database volume? [y/N] " ans; [ "$${ans:-N}" = "y" ]
	$(COMPOSE) down -v

db-psql: ## Open an interactive psql shell in the container
	$(COMPOSE) exec db psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)

db-logs: ## Follow the database logs (Ctrl-C to stop)
	$(COMPOSE) logs -f db

# ---------------------------------------------------------------- notebooks
lab: ## Start JupyterLab on the EDA notebooks
	$(UV) run jupyter lab notebooks/eda

# ---------------------------------------------------------------- housekeeping
clean: ## Remove caches (keeps .venv, data and the database)
	rm -rf .pytest_cache .ruff_cache
	find . -path ./.venv -prune -o -type d -name __pycache__ -exec rm -rf {} +
