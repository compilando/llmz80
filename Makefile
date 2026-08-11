SHELL := /bin/bash
.DEFAULT_GOAL := help

# Keep project dependencies isolated from the operating-system Python (PEP 668).
VENV_DIR ?= .venv
BOOTSTRAP_PYTHON ?= $(shell for candidate in python3.13 python3.12 python3.11 python3.10 python3; do if command -v $$candidate >/dev/null 2>&1; then command -v $$candidate; break; fi; done)
PYTHON ?= $(VENV_DIR)/bin/python
PLATFORM ?= spectrum
PROMPT ?=
LOG_LEVEL ?= INFO
GENERATOR_ARGS ?=
GENERATOR_MODE_ARGS ?=
EMULATOR ?=

QDRANT_CONTAINER ?= llmz80-qdrant
QDRANT_IMAGE ?= qdrant/qdrant:v1.18.3
QDRANT_URL ?= http://127.0.0.1:6333
QDRANT_STORAGE ?= $(CURDIR)/local/qdrant_storage

SUPPORTED_PLATFORMS := spectrum amstrad_cpc
PYTHON_SOURCES := llmz80 generators tests scripts $(wildcard *.py)

.PHONY: help setup venv install install-dev doctor studio \
	generate generate-spectrum generate-cpc run run-spectrum run-cpc \
	test coverage lint format check audit-examples benchmark smoke quality-gate clean \
	qdrant-up qdrant-down qdrant-status qdrant-index \
	_emulator-preflight _qdrant-wait

## General

help: ## Show the available commands
	@printf '\nLLMZ80 commands\n\n'
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z0-9_-]+:.*##/ {printf "  %-20s %s\n", $$1, $$2} /^## / {printf "\n%s\n", substr($$0, 4)}' $(MAKEFILE_LIST)
	@printf '\nExamples:\n'
	@printf '  make generate-spectrum PROMPT="Create a Pong game"\n'
	@printf '  make run-cpc PROMPT="Create a Mode 0 graphics demo"\n'
	@printf '  make generate PLATFORM=amstrad_cpc GENERATOR_ARGS="--no-embeddings"\n\n'

studio: ## Open the guided LLMZ80 Studio TUI (WORKSPACE=studio-projects)
	$(PYTHON) -m llmz80.cli studio "$(or $(WORKSPACE),studio-projects)"

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
		printf 'Created .env; add OPENAI_API_KEY before generating code.\n'; \
	else \
		printf '.env already exists.\n'; \
	fi
	@mkdir -p local/logs local/learning
	@printf 'Setup complete. Run "make doctor" to verify the environment.\n'

doctor: ## Check Python, credentials, and both native toolchains
	@if [ ! -x "$(PYTHON)" ]; then \
		printf '%s does not exist; run "make setup" first.\n' "$(PYTHON)" >&2; \
		exit 1; \
	fi
	@$(PYTHON) --version
	@$(PYTHON) -c 'import openai, numpy, pydantic, textual, yaml; print("Python dependencies: OK")'
	@if [ -f .env ] && grep -Eq '^OPENAI_API_KEY=.+$$' .env; then \
		printf 'OpenAI credentials: configured in .env\n'; \
	elif [ -n "$${OPENAI_API_KEY:-}" ]; then \
		printf 'OpenAI credentials: configured in the environment\n'; \
	else \
		printf 'OpenAI credentials: MISSING (set OPENAI_API_KEY)\n' >&2; \
		exit 1; \
	fi
	@$(PYTHON) -c 'from llmz80.utils.config import load_config; from llm_z80 import validate_toolchain_environment; config = load_config("config.yml"); results = [(name, *validate_toolchain_environment(name, config)) for name in ("spectrum", "amstrad_cpc")]; [print("{} toolchain: {}{}".format(name, "OK" if ok else "MISSING", " ({})".format(message) if message else "")) for name, ok, message in results]; raise SystemExit(0 if all(item[1] for item in results) else 1)'
	@$(PYTHON) -c 'import shutil; from llmz80.utils.config import load_config; config = load_config("config.yml"); [(lambda command: print("{} emulator: {}".format(platform, "OK" if shutil.which(command) else "not installed (optional)")))(config.get("emulator", {}).get(platform, {}).get("name", fallback)) for platform, fallback in (("spectrum", "fuse"), ("amstrad_cpc", "cap32"))]'

## Code generation

generate: ## Generate and compile (PLATFORM=spectrum|amstrad_cpc, PROMPT optional)
	@if [[ ! " $(SUPPORTED_PLATFORMS) " =~ " $(PLATFORM) " ]]; then \
		printf 'Unsupported PLATFORM: %s\n' "$(PLATFORM)" >&2; \
		printf 'Choose one of: %s\n' "$(SUPPORTED_PLATFORMS)" >&2; \
		exit 2; \
	fi
	@if [ -n "$(strip $(PROMPT))" ]; then \
		$(PYTHON) llm_z80.py --platform "$(PLATFORM)" --prompt "$(PROMPT)" \
			--log-level "$(LOG_LEVEL)" $(GENERATOR_ARGS) $(GENERATOR_MODE_ARGS); \
	else \
		$(PYTHON) llm_z80.py --platform "$(PLATFORM)" \
			--log-level "$(LOG_LEVEL)" $(GENERATOR_ARGS) $(GENERATOR_MODE_ARGS); \
	fi

generate-spectrum: PLATFORM := spectrum
generate-spectrum: generate ## Generate and compile a ZX Spectrum program

generate-cpc: PLATFORM := amstrad_cpc
generate-cpc: generate ## Generate and compile an Amstrad CPC program

_emulator-preflight:
	@PLATFORM="$(PLATFORM)" EMULATOR="$(EMULATOR)" $(PYTHON) -c 'import os, shutil; from llmz80.utils.config import load_config; platform = os.environ["PLATFORM"]; supported = platform in ("spectrum", "amstrad_cpc"); override = os.environ.get("EMULATOR"); config = load_config("config.yml"); command = override or config.get("emulator", {}).get(platform, {}).get("name", "fuse" if platform == "spectrum" else "cap32"); found = shutil.which(command) if supported else None; hint = "Install fuse-emulator-sdl, or use EMULATOR=zesarux" if platform == "spectrum" else "Install caprice32, or use EMULATOR=cpcec"; print("{} emulator: {}".format(platform, found or ("MISSING ({})\nHint: {}".format(command, hint) if supported else "unsupported platform"))); raise SystemExit(0 if found else (1 if supported else 2))'

run: GENERATOR_MODE_ARGS := --runtime-check --launch-emulator $(if $(EMULATOR),--emulator "$(EMULATOR)")
run: _emulator-preflight generate ## Generate, verify at runtime, and launch the emulator

run-spectrum: PLATFORM := spectrum
run-spectrum: run ## Generate and run a ZX Spectrum program

run-cpc: PLATFORM := amstrad_cpc
run-cpc: run ## Generate and run an Amstrad CPC program

## Quality

test: ## Run the test suite
	$(PYTHON) -m pytest tests

coverage: ## Run tests and write an HTML coverage report
	$(PYTHON) -m pytest tests --cov=llmz80 --cov-report=term-missing --cov-report=html

lint: ## Run Flake8 critical-error checks across Python sources
	$(PYTHON) -m flake8 $(PYTHON_SOURCES) --select=E9,F63,F7,F82 \
		--exclude=.git,.venv,local,examples,build,dist

format: ## Format Python sources with Black
	$(PYTHON) -m black $(PYTHON_SOURCES)

check: test audit-examples ## Run functional tests and compile every retrievable example

audit-examples: ## Compile every program available to the local RAG catalog
	$(PYTHON) scripts/audit_examples.py --platform all

benchmark: ## Evaluate saved runs against the bilingual prompt corpus (no API calls)
	$(PYTHON) scripts/evaluate_generation.py

smoke: ## Verify RUN_DIR (use SMOKE_ARGS=--full for real runtime evidence)
	@test -n "$(RUN_DIR)" || { printf 'RUN_DIR is required.\n' >&2; exit 2; }
	$(PYTHON) scripts/smoke_test.py "$(RUN_DIR)" $(SMOKE_ARGS)

quality-gate: test audit-examples benchmark ## Run all deterministic quality checks

clean: ## Remove generated Python and test artifacts (keeps generated programs)
	@find llmz80 generators tests scripts -type f \( -name '*.pyc' -o -name '*.pyo' -o -name '*~' \) -delete
	@find llmz80 generators tests scripts -depth -type d -name '__pycache__' -empty -delete
	@find . -maxdepth 1 -type f \( -name '*.pyc' -o -name '*.pyo' -o -name '*~' \) -delete
	@find . -maxdepth 1 -type d -name '__pycache__' -empty -delete
	@rm -rf .pytest_cache .mypy_cache .coverage htmlcov build dist

## Optional Qdrant service

qdrant-up: ## Start the optional local Qdrant service
	@command -v docker >/dev/null 2>&1 || { printf 'Docker is required for this target.\n' >&2; exit 1; }
	@mkdir -p "$(QDRANT_STORAGE)"
	@if docker ps --format '{{.Names}}' | grep -qx "$(QDRANT_CONTAINER)"; then \
		printf 'Qdrant is already running.\n'; \
	elif docker ps -a --format '{{.Names}}' | grep -qx "$(QDRANT_CONTAINER)"; then \
		docker start "$(QDRANT_CONTAINER)" >/dev/null; \
	else \
		docker run -d --name "$(QDRANT_CONTAINER)" -p 6333:6333 -p 6334:6334 \
			-v "$(QDRANT_STORAGE):/qdrant/storage" "$(QDRANT_IMAGE)" >/dev/null; \
	fi
	@$(MAKE) --no-print-directory _qdrant-wait

_qdrant-wait:
	@for attempt in {1..15}; do \
		if curl -fsS "$(QDRANT_URL)/collections" >/dev/null 2>&1; then \
			printf 'Qdrant is ready at %s.\n' "$(QDRANT_URL)"; \
			exit 0; \
		fi; \
		sleep 1; \
	done; \
	printf 'Qdrant did not become ready at %s.\n' "$(QDRANT_URL)" >&2; \
	exit 1

qdrant-down: ## Stop the optional local Qdrant service
	@command -v docker >/dev/null 2>&1 || { printf 'Docker is required for this target.\n' >&2; exit 1; }
	@if docker ps --format '{{.Names}}' | grep -qx "$(QDRANT_CONTAINER)"; then \
		docker stop "$(QDRANT_CONTAINER)" >/dev/null; \
		printf 'Qdrant stopped.\n'; \
	else \
		printf 'Qdrant is not running.\n'; \
	fi

qdrant-status: ## Check whether Qdrant is reachable
	@if curl -fsS "$(QDRANT_URL)/collections" >/dev/null 2>&1; then \
		printf 'Qdrant is available at %s.\n' "$(QDRANT_URL)"; \
	else \
		printf 'Qdrant is not reachable at %s.\n' "$(QDRANT_URL)" >&2; \
		exit 1; \
	fi

qdrant-index: qdrant-status ## Index both example libraries in Qdrant
	$(PYTHON) llm_z80.py --platform spectrum --populate-db --log-level "$(LOG_LEVEL)"
	$(PYTHON) llm_z80.py --platform amstrad_cpc --populate-db --log-level "$(LOG_LEVEL)"
