#!/bin/bash

# Only for VertexAi
export GCP_PROJECT_ID=rossetamltest
export GCP_LOCATION=europe-southwest1

# Colores para mensajes
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Verificar si el script fue interrumpido
trap cleanup INT

# Función para limpiar antes de salir
cleanup() {
    echo -e "\n${RED}Script interrumpido por el usuario.${NC}"
    # Si el entorno virtual está activado, desactivarlo
    if [ -n "$VIRTUAL_ENV" ]; then
        deactivate &> /dev/null
    fi
    exit 130
}

# Función para mostrar ayuda
show_help() {
    echo -e "${BLUE}🎨 Sprite Generator${NC}"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --prompt=\"TEXT\"        Descripción del sprite a generar"
    echo "  --width=N              Ancho del sprite (default: 32)"
    echo "  --height=N             Alto del sprite (default: 32)"
    echo "  --platform=NAME        Plataforma objetivo (spectrum, amstrad_cpc)"
    echo "  --mode=NAME            Modo de video (solo para amstrad_cpc)"
    echo "  --negative-prompt=\"TEXT\"  Prompt negativo para evitar ciertas características"
    echo "  --interactive          Modo interactivo (preguntar parámetros)"
    echo "  --help                 Muestra esta ayuda"
    echo ""
    echo "Examples:"
    echo "  $0 --prompt=\"running knight\""
    echo "  $0 --interactive"
    echo "  $0 --platform=spectrum --prompt=\"space ship\" --width=32 --height=32"
    echo "  $0 --platform=amstrad_cpc --mode=mode0 --prompt=\"dragon\" --negative-prompt=\"details, shading\""
    echo ""
}

# Verificar dependencias básicas (Python)
if ! command -v python3 &> /dev/null; then 
    echo -e "${RED}❌ Error: Python 3 no está instalado${NC}"
    exit 1
fi

# Mostrar versión de Python
PYTHON_VERSION=$(python3 --version)
echo -e "${BLUE}ℹ️ Usando $PYTHON_VERSION${NC}"

# Verificar que el entorno virtual existe
if [ ! -d "venv" ]; then
    echo -e "${BLUE}🔧 Creando entorno virtual...${NC}"
    if ! python3 -m venv venv; then
        echo -e "${RED}❌ Error al crear entorno virtual.${NC}"
        exit 1
    fi
fi

# Activar el entorno virtual
source venv/bin/activate

# Verificar que el archivo Python externo existe
if [ ! -f "llm_sprites.py" ]; then
    echo -e "${RED}❌ Error: No se encontró el archivo llm_sprites.py${NC}"
    cleanup
    exit 1
fi

# Hacer ejecutable el script Python
chmod +x llm_sprites.py

# Construir argumentos para el script de Python
ARGS=()
# Flag to track if any core arguments were provided via command line
CORE_ARG_PROVIDED=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --prompt=*)
            PROMPT="${1#*=}"
            ARGS+=("--prompt" "$PROMPT")
            CORE_ARG_PROVIDED=true # Mark as provided
            shift
            ;;
        --width=*)
            WIDTH="${1#*=}"
            ARGS+=("--width" "$WIDTH")
            CORE_ARG_PROVIDED=true # Mark as provided
            shift
            ;;
        --height=*)
            HEIGHT="${1#*=}"
            ARGS+=("--height" "$HEIGHT")
            CORE_ARG_PROVIDED=true # Mark as provided
            shift
            ;;
        --platform=*)
            PLATFORM="${1#*=}"
            ARGS+=("--platform" "$PLATFORM")
            CORE_ARG_PROVIDED=true # Mark as provided
            shift
            ;;
        --mode=*)
            MODE="${1#*=}"
            ARGS+=("--mode" "$MODE")
            shift
            ;;
        --negative-prompt=*)
            NEGATIVE="${1#*=}"
            ARGS+=("--negative-prompt" "$NEGATIVE")
            shift
            ;;
        --interactive)
            ARGS+=("--interactive")
            # If --interactive is explicitly passed, we don't need to force it later
            CORE_ARG_PROVIDED=true 
            shift
            ;;
        --help)
            show_help
            cleanup
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Error: Argumento desconocido: $1${NC}"
            show_help
            cleanup
            exit 1
            ;;
    esac
done

# If no core arguments were provided (and not asking for help),
# force interactive mode in the python script
help_requested=false
for arg in "${ARGS[@]}"; do
    if [[ "$arg" == "--help" ]]; then
        help_requested=true
        break
    fi
done

if ! $CORE_ARG_PROVIDED && ! $help_requested; then
    echo -e "${BLUE}ℹ️ No se proporcionaron argumentos principales, iniciando modo interactivo...${NC}"
    ARGS+=("--interactive")
fi

# Ejecutar el script Python con los argumentos correctamente
echo -e "${BLUE}🔄 Ejecutando script generador...${NC}"
eval python3 "llm_sprites.py" "${ARGS[@]}" || EXIT_CODE=$?

# Desactivar entorno virtual si está activo
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate &> /dev/null
fi

exit ${EXIT_CODE:-0}