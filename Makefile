include .env
export

LOCALES = bot/locales

.PHONY: help

help: ## Display this help screen
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

deps:	## Install dependencies
	@uv sync --frozen
.PHONY: deps

compose-up: ## Run docker compose
	docker compose up --build -d
.PHONY: compose-up

compose-down: ## Down docker compose
	docker compose down
.PHONY: compose-down

compose-stop: ## docker compose stop
	docker compose stop

compose-kill: ## docker compose kill
	docker compose kill

compose-build: ## docker compose build
	docker compose build

compose-ps: ## docker compose ps
	docker compose ps

compose-exec: ## Exec command in app container
	docker compose exec app $(args)

logs:
	docker compose logs $(args) -f

# MIGRATIONS
mm: ## Create new migrations with args name in docker compose
	docker compose exec bot alembic revision --autogenerate -m "$(args)"
.PHONY: mm

migrate: ## Upgrade migrations in docker compose
	docker compose exec bot alembic upgrade head
.PHONY: migrate

downgrade: ## Downgrade to args name migration in docker compose
	docker compose exec bot alembic downgrade $(args)
.PHONY: downgrade

# STYLE
check: ## Run linters to check code
	@uv run ruff check .
	@uv run ruff format --check .
.PHONY: check

format: ## Run linters to fix code
	@uv run ruff check --fix .
	@uv run ruff format .
.PHONY: format

clean: ## Delete all temporary and generated files
	@rm -rf .pytest_cache .ruff_cache .hypothesis build/ -rf dist/ .eggs/ .coverage coverage.xml coverage.json htmlcov/ .mypy_cache
	@find . -name '*.egg-info' -exec rm -rf {} +
	@find . -name '*.egg' -exec rm -f {} +
	@find . -name '*.pyc' -exec rm -f {} +
	@find . -name '*.pyo' -exec rm -f {} +
	@find . -name '*~' -exec rm -f {} +
	@find . -name '__pycache__' -exec rm -rf {} +
	@find . -name '.pytest_cache' -exec rm -rf {} +
	@find . -name '.ipynb_checkpoints' -exec rm -rf {} +
.PHONY: clean

# BACKUPS
list-backups: ## List all available backups
	docker compose exec pgbackup ls -lh /backups

backup: ## Trigger a manual backup
	docker compose exec pgbackup /backup.sh

copy-backup: ## Copy a backup from container to host (args=filename)
	docker cp $$(docker compose ps -q pgbackup):/backups/$(args) ./$(args)

restore: ## Restore from a backup file (args=filename)
	docker compose exec pgbackup /restore.sh $(args)

# I18N
babel-extract: ## Extracts translatable strings from the source code into a .pot file
	docker compose exec bot uv run pybabel extract --input-dirs=. -o $(LOCALES)/messages.pot
.PHONY: babel-extract

babel-update: ## Updates .pot files by merging changed strings into the existing .pot files
	docker compose exec bot uv run pybabel update -d $(LOCALES) -i $(LOCALES)/messages.pot
.PHONY: babel-update

babel-compile: ## Compiles translation .po files into binary .mo files
	docker compose exec bot uv run pybabel compile -d $(LOCALES)
.PHONY: babel-compile

babel: extract update
.PHONY: babel
