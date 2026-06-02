.PHONY: help install install-dev test lint format clean populate-spectrum populate-cpc generate-spectrum generate-cpc stats-spectrum stats-cpc validate setup interactive interactive-spectrum interactive-cpc qdrant-start qdrant-stop qdrant-status qdrant-wait qdrant-preflight qdrant-logs

# Variables
# Prefer venv python if present
PYTHON := $(shell if [ -x .venv/bin/python ]; then echo .venv/bin/python; else echo python3; fi)
PIP := $(PYTHON) -m pip
PLATFORM_SPECTRUM := spectrum
PLATFORM_CPC := amstrad_cpc
QDRANT_CONTAINER := llmz80-qdrant
QDRANT_URL ?= http://127.0.0.1:6333
QDRANT_STORAGE := $(PWD)/local/qdrant_storage

# Colors para output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

##@ General

help: ## Muestra esta ayuda
	@echo '${BLUE}═══════════════════════════════════════════════════════════${NC}'
	@echo '${GREEN}           LLMZ80 - Makefile de Tareas Principales${NC}'
	@echo '${BLUE}═══════════════════════════════════════════════════════════${NC}'
	@echo ''
	@awk 'BEGIN {FS = ":.*##"; printf ""} /^[a-zA-Z_-]+:.*?##/ { printf "  ${YELLOW}%-20s${NC} %s\n", $$1, $$2 } /^##@/ { printf "\n${BLUE}%s${NC}\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
	@echo ''

##@ Instalación

install: ## Instala dependencias de producción
	@echo "${GREEN}📦 Instalando dependencias de producción...${NC}"
	$(PIP) install -r requirements.txt
	@echo "${GREEN}✅ Dependencias instaladas${NC}"

install-dev: ## Instala dependencias de desarrollo
	@echo "${GREEN}📦 Instalando dependencias de desarrollo...${NC}"
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-dev.txt
	@echo "${GREEN}✅ Dependencias de desarrollo instaladas${NC}"

setup: install ## Configuración inicial completa
	@echo "${GREEN}🔧 Configuración inicial...${NC}"
	@if [ ! -f .env ]; then \
		echo "${YELLOW}⚠️  Creando archivo .env desde .env.example...${NC}"; \
		cp .env.example .env; \
		echo "${YELLOW}⚠️  Edita .env y añade tu OPENAI_API_KEY${NC}"; \
	else \
		echo "${GREEN}✅ Archivo .env ya existe${NC}"; \
	fi
	@mkdir -p local/learning
	@mkdir -p logs
	@mkdir -p scripts
	@chmod +x scripts/init_qdrant.py 2>/dev/null || true
	@echo "${GREEN}✅ Directorios creados${NC}"
	@echo ""
	@echo "${BLUE}🗄️  Inicializando Qdrant...${NC}"
	@$(PYTHON) scripts/init_qdrant.py || echo "${YELLOW}⚠️  Qdrant no inicializado (puede estar offline o sin configurar)${NC}"
	@echo ""
	@echo "${BLUE}🎮 Verificando emuladores...${NC}"
	@$(MAKE) check-emulators
	@echo ""
	@echo "${GREEN}✅ Configuración completada${NC}"
	@echo ""
	@echo "${YELLOW}📝 Próximos pasos:${NC}"
	@echo "${YELLOW}   1. Edita .env con tus claves de API${NC}"
	@echo "${YELLOW}   2. Ejecuta: make populate-all${NC}"
	@echo "${YELLOW}   3. Prueba con: make example-hello-spectrum${NC}"
	@echo "${YELLOW}   4. Si falta un emulador, ejecuta: make install-emulators${NC}"

##@ Desarrollo

lint: ## Ejecuta linter (flake8)
	@echo "${GREEN}🔍 Ejecutando linter...${NC}"
	@$(PYTHON) -m flake8 llmz80/ --max-line-length=120 --extend-ignore=E203,W503 || true
	@echo "${GREEN}✅ Linting completado${NC}"

format: ## Formatea código con black
	@echo "${GREEN}🎨 Formateando código...${NC}"
	@$(PYTHON) -m black llmz80/ --line-length=120
	@echo "${GREEN}✅ Código formateado${NC}"

test: ## Ejecuta tests
	@echo "${GREEN}🧪 Ejecutando tests...${NC}"
	@$(PYTHON) -m pytest tests/ -v
	@echo "${GREEN}✅ Tests completados${NC}"

##@ Qdrant (Base de Datos Vectorial)

qdrant-start: ## Arranca Qdrant local con Docker
	@mkdir -p "$(QDRANT_STORAGE)"
	@if docker ps --format '{{.Names}}' | grep -qx "$(QDRANT_CONTAINER)"; then \
		printf "%b\n" "${GREEN}✅ Qdrant ya está ejecutándose ($(QDRANT_CONTAINER))${NC}"; \
	elif docker ps -a --format '{{.Names}}' | grep -qx "$(QDRANT_CONTAINER)"; then \
		printf "%b\n" "${BLUE}▶️  Arrancando contenedor Qdrant existente...${NC}"; \
		docker start "$(QDRANT_CONTAINER)" >/dev/null; \
	else \
		printf "%b\n" "${BLUE}🐳 Creando contenedor Qdrant local...${NC}"; \
		docker run -d --name "$(QDRANT_CONTAINER)" -p 6333:6333 -p 6334:6334 \
			-v "$(QDRANT_STORAGE):/qdrant/storage" qdrant/qdrant >/dev/null; \
	fi
	@$(MAKE) qdrant-wait
	@$(MAKE) init-qdrant

qdrant-stop: ## Para Qdrant local si fue arrancado por este Makefile
	@if docker ps --format '{{.Names}}' | grep -qx "$(QDRANT_CONTAINER)"; then \
		printf "%b\n" "${BLUE}⏹️  Parando Qdrant...${NC}"; \
		docker stop "$(QDRANT_CONTAINER)" >/dev/null; \
		printf "%b\n" "${GREEN}✅ Qdrant parado${NC}"; \
	else \
		printf "%b\n" "${YELLOW}⚠️  Qdrant no está ejecutándose ($(QDRANT_CONTAINER))${NC}"; \
	fi

qdrant-status: ## Comprueba conexión con Qdrant local
	@printf "%b\n" "${BLUE}🔎 Comprobando Qdrant en $(QDRANT_URL)...${NC}"
	@if curl -fsS "$(QDRANT_URL)/collections" >/dev/null 2>&1; then \
		printf "%b\n" "${GREEN}✅ Qdrant responde en $(QDRANT_URL)${NC}"; \
	else \
		printf "%b\n" "${YELLOW}⚠️  Qdrant no responde en $(QDRANT_URL)${NC}"; \
		printf "%b\n" "${YELLOW}   Ejecuta: make qdrant-start${NC}"; \
		exit 1; \
	fi

qdrant-wait: ## Espera a que Qdrant esté listo
	@printf "%b\n" "${BLUE}⏳ Esperando Qdrant en $(QDRANT_URL)...${NC}"
	@for i in 1 2 3 4 5 6 7 8 9 10; do \
		if curl -fsS "$(QDRANT_URL)/collections" >/dev/null 2>&1; then \
			printf "%b\n" "${GREEN}✅ Qdrant listo${NC}"; \
			exit 0; \
		fi; \
		sleep 1; \
	done; \
	printf "%b\n" "${RED}❌ Qdrant no respondió tras 10 segundos${NC}"; \
	exit 1

qdrant-preflight: ## Comprueba Qdrant salvo que se use NO_QDRANT=1
	@if [ "$(NO_QDRANT)" = "1" ]; then \
		printf "%b\n" "${YELLOW}⚠️  NO_QDRANT=1: generación sin RAG/indexación Qdrant${NC}"; \
	elif curl -fsS "$(QDRANT_URL)/collections" >/dev/null 2>&1; then \
		printf "%b\n" "${GREEN}✅ Qdrant disponible en $(QDRANT_URL)${NC}"; \
		$(PYTHON) scripts/init_qdrant.py >/dev/null; \
	else \
		printf "%b\n" "${YELLOW}⚠️  Qdrant no responde en $(QDRANT_URL)${NC}"; \
		printf "%b\n" "${YELLOW}   Ejecuta: make qdrant-start && make init-qdrant${NC}"; \
		printf "%b\n" "${YELLOW}   O usa NO_QDRANT=1 para generar sin RAG/indexación${NC}"; \
		exit 1; \
	fi

qdrant-logs: ## Muestra logs del contenedor Qdrant local
	@docker logs "$(QDRANT_CONTAINER)"

init-qdrant: ## Inicializa colecciones de Qdrant
	@echo "${GREEN}🗄️  Inicializando colecciones de Qdrant...${NC}"
	$(PYTHON) scripts/init_qdrant.py

##@ Base de Datos Vectorial

populate-spectrum: qdrant-status init-qdrant ## Puebla BD vectorial para ZX Spectrum
	@echo "${GREEN}🚀 Poblando BD vectorial para ZX Spectrum...${NC}"
	$(PYTHON) llm_z80.py --platform $(PLATFORM_SPECTRUM) --populate-db --log-level INFO
	@echo "${GREEN}✅ BD ZX Spectrum poblada${NC}"

populate-cpc: qdrant-status init-qdrant ## Puebla BD vectorial para Amstrad CPC
	@echo "${GREEN}🚀 Poblando BD vectorial para Amstrad CPC...${NC}"
	$(PYTHON) llm_z80.py --platform $(PLATFORM_CPC) --populate-db --log-level INFO
	@echo "${GREEN}✅ BD Amstrad CPC poblada${NC}"

populate-all: populate-spectrum populate-cpc ## Puebla BD para todas las plataformas
	@echo "${GREEN}✅ Todas las bases de datos pobladas${NC}"

##@ Generación de Código

generate-spectrum: qdrant-preflight ## Genera código para ZX Spectrum (PROMPT opcional; si falta, pregunta)
	@if [ -z "$(PROMPT)" ]; then \
		printf "%b\n" "${YELLOW}📝 Prompt ZX Spectrum:${NC}"; \
		printf "> "; \
		read -r prompt; \
	else \
		prompt="$(PROMPT)"; \
	fi; \
	if [ -z "$$prompt" ]; then \
		printf "%b\n" "${RED}❌ Error: el prompt no puede estar vacío${NC}"; \
		printf "%b\n" "${YELLOW}   Ejemplo: make generate-spectrum PROMPT='crear hello world'${NC}"; \
		exit 1; \
	fi; \
	printf "%b\n" "${GREEN}🎮 Generando código para ZX Spectrum...${NC}"; \
	$(PYTHON) llm_z80.py --platform $(PLATFORM_SPECTRUM) --prompt "$$prompt" --log-level INFO

generate-cpc: qdrant-preflight ## Genera código para Amstrad CPC (PROMPT opcional; si falta, pregunta)
	@if [ -z "$(PROMPT)" ]; then \
		printf "%b\n" "${YELLOW}📝 Prompt Amstrad CPC:${NC}"; \
		printf "> "; \
		read -r prompt; \
	else \
		prompt="$(PROMPT)"; \
	fi; \
	if [ -z "$$prompt" ]; then \
		printf "%b\n" "${RED}❌ Error: el prompt no puede estar vacío${NC}"; \
		printf "%b\n" "${YELLOW}   Ejemplo: make generate-cpc PROMPT='crear hello world'${NC}"; \
		exit 1; \
	fi; \
	printf "%b\n" "${GREEN}🎮 Generando código para Amstrad CPC...${NC}"; \
	$(PYTHON) llm_z80.py --platform $(PLATFORM_CPC) --prompt "$$prompt" --log-level INFO

interactive-spectrum: ## Modo interactivo para ZX Spectrum (con emulador)
	@echo "${GREEN}🎮 Modo interactivo ZX Spectrum (lanzará emulador tras compilar)${NC}"
	$(PYTHON) llm_z80.py --platform $(PLATFORM_SPECTRUM) --log-level INFO --launch-emulator

interactive-cpc: ## Modo interactivo para Amstrad CPC (con compilación CPCtelera completa)
	@echo "${GREEN}🎮 Modo interactivo Amstrad CPC${NC}"
	@echo "${BLUE}(Usa build_amstrad.sh con entorno CPCtelera completo)${NC}"
	@if [ ! -f build_amstrad.sh ]; then \
		echo "${RED}❌ Error: build_amstrad.sh no encontrado${NC}"; \
		exit 1; \
	fi
	@if [ ! -x build_amstrad.sh ]; then \
		echo "${YELLOW}⚠️  Haciendo build_amstrad.sh ejecutable...${NC}"; \
		chmod +x build_amstrad.sh; \
	fi
	@./build_amstrad.sh --prompt

##@ Estadísticas y Análisis

stats-spectrum: ## Muestra estadísticas de ZX Spectrum
	@echo "${GREEN}📊 Estadísticas de aprendizaje - ZX Spectrum${NC}"
	@if [ -f local/learning/$(PLATFORM_SPECTRUM)_stats.json ]; then \
		cat local/learning/$(PLATFORM_SPECTRUM)_stats.json | $(PYTHON) -m json.tool; \
	else \
		echo "${YELLOW}⚠️  No hay estadísticas disponibles para ZX Spectrum${NC}"; \
	fi

stats-cpc: ## Muestra estadísticas de Amstrad CPC
	@echo "${GREEN}📊 Estadísticas de aprendizaje - Amstrad CPC${NC}"
	@if [ -f local/learning/$(PLATFORM_CPC)_stats.json ]; then \
		cat local/learning/$(PLATFORM_CPC)_stats.json | $(PYTHON) -m json.tool; \
	else \
		echo "${YELLOW}⚠️  No hay estadísticas disponibles para Amstrad CPC${NC}"; \
	fi

stats-all: stats-spectrum stats-cpc ## Muestra todas las estadísticas
	@echo "${GREEN}✅ Estadísticas mostradas${NC}"

list-examples: ## Lista ejemplos exitosos guardados
	@echo "${GREEN}📚 Ejemplos exitosos guardados:${NC}"
	@echo ""
	@echo "${BLUE}ZX Spectrum:${NC}"
	@if [ -f local/learning/$(PLATFORM_SPECTRUM)_successful_examples.json ]; then \
		$(PYTHON) -c "import json; data=json.load(open('local/learning/$(PLATFORM_SPECTRUM)_successful_examples.json')); print(f'Total: {len(data)} ejemplos'); [print(f\"  - {v['prompt'][:60]}... (intentos: {v['compilation_attempts']}, rating: {v.get('rating', 'N/A')})\") for k,v in list(data.items())[:5]]"; \
	else \
		echo "  ${YELLOW}No hay ejemplos disponibles${NC}"; \
	fi
	@echo ""
	@echo "${BLUE}Amstrad CPC:${NC}"
	@if [ -f local/learning/$(PLATFORM_CPC)_successful_examples.json ]; then \
		$(PYTHON) -c "import json; data=json.load(open('local/learning/$(PLATFORM_CPC)_successful_examples.json')); print(f'Total: {len(data)} ejemplos'); [print(f\"  - {v['prompt'][:60]}... (intentos: {v['compilation_attempts']}, rating: {v.get('rating', 'N/A')})\") for k,v in list(data.items())[:5]]"; \
	else \
		echo "  ${YELLOW}No hay ejemplos disponibles${NC}"; \
	fi

list-errors: ## Lista errores comunes registrados
	@echo "${GREEN}🔍 Errores comunes registrados:${NC}"
	@echo ""
	@echo "${BLUE}ZX Spectrum:${NC}"
	@if [ -f local/learning/$(PLATFORM_SPECTRUM)_common_errors.json ]; then \
		$(PYTHON) -c "import json; data=json.load(open('local/learning/$(PLATFORM_SPECTRUM)_common_errors.json')); print(f'Total: {len(data)} errores'); [print(f\"  - {v['error_description']} (ocurrencias: {v['occurrences']}, éxito: {v['success_rate']:.0%})\") for k,v in sorted(data.items(), key=lambda x: x[1]['occurrences'], reverse=True)[:5]]"; \
	else \
		echo "  ${YELLOW}No hay errores registrados${NC}"; \
	fi
	@echo ""
	@echo "${BLUE}Amstrad CPC:${NC}"
	@if [ -f local/learning/$(PLATFORM_CPC)_common_errors.json ]; then \
		$(PYTHON) -c "import json; data=json.load(open('local/learning/$(PLATFORM_CPC)_common_errors.json')); print(f'Total: {len(data)} errores'); [print(f\"  - {v['error_description']} (ocurrencias: {v['occurrences']}, éxito: {v['success_rate']:.0%})\") for k,v in sorted(data.items(), key=lambda x: x[1]['occurrences'], reverse=True)[:5]]"; \
	else \
		echo "  ${YELLOW}No hay errores registrados${NC}"; \
	fi

##@ Mantenimiento

clean: ## Limpia archivos temporales y caché
	@echo "${GREEN}🧹 Limpiando archivos temporales...${NC}"
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type f -name "*~" -delete 2>/dev/null || true
	@echo "${GREEN}✅ Archivos temporales eliminados${NC}"

clean-cache: ## Limpia caché de embeddings
	@echo "${YELLOW}⚠️  Limpiando caché de embeddings...${NC}"
	@rm -rf local/embeddings/
	@echo "${GREEN}✅ Caché de embeddings eliminado${NC}"

clean-learning: ## Limpia datos de aprendizaje (¡CUIDADO!)
	@echo "${RED}⚠️  ADVERTENCIA: Esto eliminará TODOS los datos de aprendizaje${NC}"
	@echo "${YELLOW}Presiona Ctrl+C para cancelar o Enter para continuar...${NC}"
	@read confirm
	@rm -rf local/learning/
	@mkdir -p local/learning
	@echo "${GREEN}✅ Datos de aprendizaje eliminados${NC}"

clean-all: clean clean-cache ## Limpieza completa (excepto aprendizaje)
	@echo "${GREEN}✅ Limpieza completa realizada${NC}"

reset-learning: clean-learning populate-all ## Reset completo: limpia y repuebla
	@echo "${GREEN}✅ Sistema de aprendizaje reseteado${NC}"

##@ Validación y Reparación

validate-cache: ## Valida y repara caché de embeddings
	@echo "${GREEN}🔧 Validando caché de embeddings...${NC}"
	$(PYTHON) llm_z80.py --platform $(PLATFORM_SPECTRUM) --repair-cache --log-level INFO

rebuild-embeddings-spectrum: ## Reconstruye embeddings de ZX Spectrum
	@echo "${GREEN}🔨 Reconstruyendo embeddings ZX Spectrum...${NC}"
	$(PYTHON) llm_z80.py --platform $(PLATFORM_SPECTRUM) --rebuild-embeddings --log-level INFO

rebuild-embeddings-cpc: ## Reconstruye embeddings de Amstrad CPC
	@echo "${GREEN}🔨 Reconstruyendo embeddings Amstrad CPC...${NC}"
	$(PYTHON) llm_z80.py --platform $(PLATFORM_CPC) --rebuild-embeddings --log-level INFO

rebuild-all: rebuild-embeddings-spectrum rebuild-embeddings-cpc ## Reconstruye todos los embeddings
	@echo "${GREEN}✅ Todos los embeddings reconstruidos${NC}"

##@ Docker (si aplica)

docker-build: ## Construye imagen Docker (si existe Dockerfile)
	@if [ -f Dockerfile ]; then \
		echo "${GREEN}🐳 Construyendo imagen Docker...${NC}"; \
		docker build -t llmz80:latest .; \
		echo "${GREEN}✅ Imagen Docker construida${NC}"; \
	else \
		echo "${YELLOW}⚠️  No existe Dockerfile${NC}"; \
	fi

docker-run: ## Ejecuta en Docker (modo interactivo)
	@if command -v docker &> /dev/null; then \
		echo "${GREEN}🐳 Ejecutando en Docker...${NC}"; \
		docker run -it --rm -v $(PWD):/app -v $(PWD)/.env:/app/.env llmz80:latest; \
	else \
		echo "${YELLOW}⚠️  Docker no está instalado${NC}"; \
	fi

##@ Emuladores

check-emulators: ## Verifica emuladores instalados
	@echo "${BLUE}Verificando emuladores instalados...${NC}"
	@echo ""
	@echo "${BLUE}ZX Spectrum:${NC}"
	@if command -v fuse >/dev/null 2>&1; then \
		echo "  ✅ Fuse instalado"; \
	else \
		echo "  ${YELLOW}⚠️  Fuse NO instalado${NC}"; \
	fi
	@if command -v zesarux >/dev/null 2>&1; then \
		echo "  ✅ ZEsarUX instalado"; \
	else \
		echo "  ${YELLOW}⚠️  ZEsarUX NO instalado${NC}"; \
	fi
	@echo ""
	@echo "${BLUE}Amstrad CPC:${NC}"
	@if command -v cap32 >/dev/null 2>&1; then \
		echo "  ✅ Cap32 instalado"; \
	else \
		echo "  ${YELLOW}⚠️  Cap32 NO instalado${NC}"; \
	fi
	@echo ""
	@echo "${YELLOW}💡 Para instalar emuladores, ejecuta: make install-emulators${NC}"

install-emulators: ## Muestra instrucciones para instalar emuladores
	@echo "${GREEN}📦 Instrucciones de instalación de emuladores${NC}"
	@echo ""
	@echo "${BLUE}═══════════════════════════════════════════════════════════${NC}"
	@echo "${BLUE}ZX Spectrum Emulators${NC}"
	@echo "${BLUE}═══════════════════════════════════════════════════════════${NC}"
	@echo ""
	@echo "${GREEN}Fuse (recomendado):${NC}"
	@echo "  ${YELLOW}Arch Linux / Manjaro:${NC}"
	@echo "    yay -S fuse-emulator"
	@echo "    # o desde AUR:"
	@echo "    yay -S fuse-zx"
	@echo ""
	@echo "  ${YELLOW}Ubuntu / Debian:${NC}"
	@echo "    sudo apt update"
	@echo "    sudo apt install fuse-emulator-sdl"
	@echo ""
	@echo "${GREEN}ZEsarUX (alternativa):${NC}"
	@echo "  ${YELLOW}Arch Linux / Manjaro:${NC}"
	@echo "    yay -S zesarux"
	@echo ""
	@echo "  ${YELLOW}Ubuntu / Debian:${NC}"
	@echo "    # Descargar desde: https://github.com/chernandezba/zesarux/releases"
	@echo ""
	@echo "${BLUE}═══════════════════════════════════════════════════════════${NC}"
	@echo "${BLUE}Amstrad CPC Emulators${NC}"
	@echo "${BLUE}═══════════════════════════════════════════════════════════${NC}"
	@echo ""
	@echo "${GREEN}Cap32:${NC}"
	@echo "  ${YELLOW}Arch Linux / Manjaro:${NC}"
	@echo "    yay -S cap32"
	@echo ""
	@echo "  ${YELLOW}Ubuntu / Debian:${NC}"
	@echo "    sudo apt update"
	@echo "    sudo apt install cap32"
	@echo ""
	@echo "${GREEN}CPCEC (alternativa):${NC}"
	@echo "  ${YELLOW}Todas las distribuciones:${NC}"
	@echo "    # Descargar desde: http://cngsoft.no-ip.org/cpcec.htm"
	@echo ""
	@echo "${BLUE}═══════════════════════════════════════════════════════════${NC}"
	@echo ""
	@echo "${YELLOW}💡 Después de instalar, ejecuta: make check-emulators${NC}"

##@ Utilidades

check-env: ## Verifica configuración del entorno
	@echo "${GREEN}🔍 Verificando configuración del entorno...${NC}"
	@echo ""
	@echo "${BLUE}Python:${NC}"
	@$(PYTHON) --version || echo "${RED}Python no encontrado${NC}"
	@echo ""
	@echo "${BLUE}Variables de entorno:${NC}"
	@if [ -f .env ]; then \
		echo "  ✅ .env existe"; \
		if grep -q "OPENAI_API_KEY=sk-" .env 2>/dev/null; then \
			echo "  ✅ OPENAI_API_KEY configurada"; \
		else \
			echo "  ${YELLOW}⚠️  OPENAI_API_KEY no configurada${NC}"; \
		fi; \
	else \
		echo "  ${RED}❌ .env no existe${NC}"; \
	fi
	@echo ""
	@echo "${BLUE}Directorios:${NC}"
	@if [ -d local/learning ]; then echo "  ✅ local/learning existe"; else echo "  ${RED}❌ local/learning no existe${NC}"; fi
	@if [ -d logs ]; then echo "  ✅ logs existe"; else echo "  ${RED}❌ logs no existe${NC}"; fi
	@echo ""
	@echo "${BLUE}Datos de aprendizaje:${NC}"
	@if [ -f local/learning/$(PLATFORM_SPECTRUM)_stats.json ]; then \
		echo "  ✅ Estadísticas ZX Spectrum disponibles"; \
	else \
		echo "  ⚪ Sin estadísticas ZX Spectrum"; \
	fi
	@if [ -f local/learning/$(PLATFORM_CPC)_stats.json ]; then \
		echo "  ✅ Estadísticas Amstrad CPC disponibles"; \
	else \
		echo "  ⚪ Sin estadísticas Amstrad CPC"; \
	fi

version: ## Muestra información de versión
	@echo "${BLUE}LLMZ80 - Generador de código Z80 con IA${NC}"
	@echo ""
	@echo "Versión: $(shell grep 'version' pyproject.toml | cut -d'"' -f2)"
	@echo "Python: $(shell $(PYTHON) --version)"
	@echo ""
	@echo "Fases implementadas:"
	@echo "  ✅ Phase 1: Automatic Code Correction"
	@echo "  ✅ Phase 2: Pre-compilation Validation"  
	@echo "  ✅ Phase 3: Learning System"
	@echo ""

##@ Ejemplos rápidos

example-hello-spectrum: ## Ejemplo: Hello World ZX Spectrum
	@echo "${GREEN}🎮 Generando Hello World para ZX Spectrum...${NC}"
	$(PYTHON) llm_z80.py --platform $(PLATFORM_SPECTRUM) --prompt "create a simple hello world program that prints text to the screen" --log-level INFO

example-hello-cpc: ## Ejemplo: Hello World Amstrad CPC
	@echo "${GREEN}🎮 Generando Hello World para Amstrad CPC...${NC}"
	$(PYTHON) llm_z80.py --platform $(PLATFORM_CPC) --prompt "create a simple hello world program that prints text to the screen" --log-level INFO

example-game-spectrum: ## Ejemplo: Juego simple ZX Spectrum
	@echo "${GREEN}🎮 Generando juego simple para ZX Spectrum...${NC}"
	$(PYTHON) llm_z80.py --platform $(PLATFORM_SPECTRUM) --prompt "create a simple snake game with keyboard controls" --log-level INFO

example-demo-cpc: ## Ejemplo: Demo gráfica Amstrad CPC
	@echo "${GREEN}🎮 Generando demo gráfica para Amstrad CPC...${NC}"
	$(PYTHON) llm_z80.py --platform $(PLATFORM_CPC) --prompt "create a graphical demo with colorful patterns in mode 0" --log-level INFO

##@ Información

info: check-env version ## Información completa del sistema
	@echo ""
	@echo "${GREEN}✅ Información del sistema mostrada${NC}"

# Default target
.DEFAULT_GOAL := help
