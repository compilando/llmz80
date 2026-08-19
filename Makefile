SHELL := /bin/bash
.DEFAULT_GOAL := help

# Keep project dependencies isolated from the operating-system Python (PEP 668).
VENV_DIR ?= .venv
BOOTSTRAP_PYTHON ?= $(shell for candidate in python3.13 python3.12 python3.11 python3.10 python3; do if command -v $$candidate >/dev/null 2>&1; then command -v $$candidate; break; fi; done)
PYTHON ?= $(VENV_DIR)/bin/python
LLMZ80 ?= $(PYTHON) -m llmz80.cli

WORKSPACE ?= studio-projects
BRIEF ?=
PLATFORM ?= spectrum
EMULATOR ?=

SUPPORTED_PLATFORMS := spectrum amstrad_cpc
PYTHON_SOURCES := llmz80 tests scripts $(wildcard *.py)

.PHONY: help setup venv install install-dev doctor studio game play \
    test coverage lint format check audit-examples benchmark smoke quality-gate clean

## General

help: ## Show the available commands
	@printf '\nLLMZ80 commands\n\n'
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z0-9_-]+:.*##/ {printf "  %-20s %s\n", $$1, $$2} /^## / {printf "\n%s\n", substr($$0, 4)}' $(MAKEFILE_LIST)
	@printf '\nExamples:\n'
	@printf '  make game BRIEF="a miner crossing stone ledges"\n'
	@printf '  make game PLATFORM=amstrad_cpc BRIEF="four ghosts chase you around a maze"\n'
	@printf '  make studio\n\n'

studio: ## Open the guided Studio TUI (WORKSPACE=studio-projects)
	$(LLMZ80) studio "$(WORKSPACE)"

venv:
	@$(BOOTSTRAP_PYTHON) -c 'import sys; raise SystemExit(0 if (3, 10) <= sys.version_info[:2] < (3, 14) else 1)' || { \
		printf 'A Python version from 3.10 through 3.13 is required; got: ' >&2; \
		$(BOOTSTRAP_PYTHON) --version >&2; \
		exit 1; \
	}
	@if [ -x "$(VENV_DIR)/bin/python" ] && ! $(PYTHON) -c 'import sys; raise SystemExit(0 if (3, 10) <= sys.version_info[:2] < (3, 14) else 1)'; then \
		printf 'Recreating incompatible virtual environment with %s...\n' "$(BOOTSTRAP_PYTHON)"; \
		$(BOOTSTRAP_PYTHON) -m venv --clear "$(VENV_DIR)"; \
	elif [ ! -x "$(VENV_DIR)/bin/python" ]; then \
		printf 'Creating virtual environment in %s...\n' "$(VENV_DIR)"; \
		$(BOOTSTRAP_PYTHON) -m venv "$(VENV_DIR)"; \
	fi

install: venv ## Install runtime dependencies in .venv
	$(PYTHON) -m pip install -r requirements.txt
	$(PYTHON) -m pip install --no-build-isolation --no-deps -e .

install-dev: venv ## Install runtime and development dependencies in .venv
	$(PYTHON) -m pip install -r requirements.txt -r requirements-dev.txt

setup: install ## Create the local configuration and runtime directories
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		printf 'Created .env; add ANTHROPIC_API_KEY before generating anything.\n'; \
	else \
		printf '.env already exists.\n'; \
	fi
	@mkdir -p local/logs "$(WORKSPACE)"
	@printf 'Setup complete. Run "make doctor" to verify the environment.\n'

doctor: ## Check Python, credentials, and both native toolchains
	@if [ ! -x "$(PYTHON)" ]; then \
		printf '%s does not exist; run "make setup" first.\n' "$(PYTHON)" >&2; \
		exit 1; \
	fi
	@$(PYTHON) --version
	@$(PYTHON) -c 'import anthropic, numpy, pydantic, textual, yaml, PIL; print("Python dependencies: OK")'
	@if [ -f .env ] && grep -Eq '^ANTHROPIC_API_KEY=.+$$' .env; then \
		printf 'Anthropic credentials: configured in .env\n'; \
	elif [ -n "$${ANTHROPIC_API_KEY:-}" ]; then \
		printf 'Anthropic credentials: configured in the environment\n'; \
	else \
		printf 'Anthropic credentials: MISSING (set ANTHROPIC_API_KEY)\n' >&2; \
		exit 1; \
	fi
	@$(PYTHON) -c 'from llmz80.utils.config import load_config; from llmz80.core.toolchain import validate_toolchain_environment; config = load_config("config.yml"); results = [(name, *validate_toolchain_environment(name, config)) for name in ("spectrum", "amstrad_cpc")]; [print("{} toolchain: {}{}".format(name, "OK" if ok else "MISSING", " ({})".format(message) if message else "")) for name, ok, message in results]; raise SystemExit(0 if all(item[1] for item in results) else 1)'
	@$(PYTHON) -c 'import shutil; from llmz80.utils.config import load_config; config = load_config("config.yml"); [(lambda command: print("{} emulator: {}".format(platform, "OK" if shutil.which(command) else "not installed (optional)")))(config.get("emulator", {}).get(platform, {}).get("name", fallback)) for platform, fallback in (("spectrum", "zesarux"), ("amstrad_cpc", "zesarux"))]'

## Making games

game: ## Design, write, build and verify a game (BRIEF="..." PLATFORM=spectrum|amstrad_cpc)
	@test -n "$(strip $(BRIEF))" || { printf 'BRIEF is required: make game BRIEF="what the game should be"\n' >&2; exit 2; }
	@if [[ ! " $(SUPPORTED_PLATFORMS) " =~ " $(PLATFORM) " ]]; then \
		printf 'Unsupported PLATFORM: %s\n' "$(PLATFORM)" >&2; \
		printf 'Choose one of: %s\n' "$(SUPPORTED_PLATFORMS)" >&2; \
		exit 2; \
	fi
	$(LLMZ80) make "$(BRIEF)" --workspace "$(WORKSPACE)" \
		$(if $(filter amstrad_cpc,$(PLATFORM)),--cpc,)

play: ## Launch a built game in an emulator (TARGET=<project|game.tap|game.dsk>)
	@test -n "$(strip $(TARGET))" || { printf 'TARGET is required: make play TARGET=studio-projects/my-game\n' >&2; exit 2; }
	$(LLMZ80) play "$(TARGET)"

## Quality

test: ## Run the test suite
	$(PYTHON) -m pytest tests

coverage: ## Run tests and write an HTML coverage report
	$(PYTHON) -m pytest tests --cov=llmz80 --cov-report=term-missing --cov-report=html

lint: ## Run Flake8 critical-error checks across Python sources
	$(PYTHON) -m flake8 $(PYTHON_SOURCES) --select=E9,F63,F7,F82 \
		--exclude=.git,.venv,local,examples,build,dist

format: ## Format Python sources with Black and isort
	$(PYTHON) -m isort $(PYTHON_SOURCES)
	$(PYTHON) -m black $(PYTHON_SOURCES)

format-check: ## Fail if anything is unformatted, exactly as CI does
	$(PYTHON) -m isort --check-only $(PYTHON_SOURCES)
	$(PYTHON) -m black --check $(PYTHON_SOURCES)

check: test audit-examples ## Run functional tests and compile every retrievable example

audit-examples: ## Compile every program available to the local retrieval catalog
	$(PYTHON) scripts/audit_examples.py --platform all

benchmark: ## Evaluate saved runs against the bilingual prompt corpus (no API calls)
	$(PYTHON) scripts/evaluate_generation.py

smoke: ## Verify RUN_DIR (use SMOKE_ARGS=--full for real runtime evidence)
	@test -n "$(RUN_DIR)" || { printf 'RUN_DIR is required.\n' >&2; exit 2; }
	$(PYTHON) scripts/smoke_test.py "$(RUN_DIR)" $(SMOKE_ARGS)

quality-gate: test audit-examples format-check ## Run all deterministic quality checks

clean: ## Remove generated Python and test artifacts (keeps generated programs)
	@find llmz80 tests scripts -type f \( -name '*.pyc' -o -name '*.pyo' -o -name '*~' \) -delete
	@find llmz80 tests scripts -depth -type d -name '__pycache__' -empty -delete
	@find . -maxdepth 1 -type f \( -name '*.pyc' -o -name '*.pyo' -o -name '*~' \) -delete
	@find . -maxdepth 1 -type d -name '__pycache__' -empty -delete
	@rm -rf .pytest_cache .mypy_cache .coverage htmlcov build dist
