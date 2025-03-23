#!/bin/bash

# Colores para mensajes
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Función para mostrar ayuda
show_help() {
    echo -e "${BLUE}🎨 Generador de Sprites con IA${NC}"
    echo ""
    echo "Uso: $0 [opciones]"
    echo ""
    echo "Opciones:"
    echo "  --prompt=TEXTO       Descripción del sprite a generar"
    echo "  --width=ANCHO        Ancho del sprite (múltiplo de 8, default: 16)"
    echo "  --height=ALTO        Alto del sprite (múltiplo de 8, default: 16)"
    echo "  --model=MODELO       Modelo LLM a utilizar (default: gpt-4o)"
    echo "  --list               Lista los sprites generados previamente"
    echo "  --help               Muestra esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  $0 --prompt=\"un pacman\" --width=16 --height=16"
    echo "  $0 --prompt=\"nave espacial\" --width=24 --height=16"
    echo "  $0 --list"
    echo ""
}

# Función para listar sprites generados
list_sprites() {
    echo -e "${BLUE}🎨 Sprites Generados${NC}"
    echo ""
    
    if [ ! -d "sprites" ] || [ -z "$(ls -A sprites 2>/dev/null)" ]; then
        echo -e "${YELLOW}⚠️ No hay sprites generados todavía${NC}"
        return 1
    fi
    
    echo -e "${GREEN}Sprites disponibles:${NC}"
    echo ""
    
    for sprite_dir in sprites/*; do
        if [ -d "$sprite_dir" ]; then
            dir_name=$(basename "$sprite_dir")
            timestamp=${dir_name%%_*}
            prompt_text=${dir_name#*_}
            
            # Leer información del sprite
            width=0
            height=0
            if [ -f "$sprite_dir/config.json" ]; then
                width=$(grep -o '"width":[^,]*' "$sprite_dir/config.json" | cut -d':' -f2)
                height=$(grep -o '"height":[^,]*' "$sprite_dir/config.json" | cut -d':' -f2)
            fi
            
            date_formatted=$(date -d "${timestamp:0:4}-${timestamp:4:2}-${timestamp:6:2} ${timestamp:9:2}:${timestamp:11:2}:${timestamp:13:2}" "+%Y-%m-%d %H:%M:%S" 2>/dev/null)
            
            if [ -z "$date_formatted" ]; then
                date_formatted="fecha desconocida"
            fi
            
            echo -e "📁 ${GREEN}$prompt_text${NC} (${BLUE}$width×$height${NC}) - $date_formatted"
            
            # Mostrar una vista previa ASCII si existe el archivo sprite.txt
            if [ -f "$sprite_dir/sprite.txt" ]; then
                echo -e "${BLUE}Vista previa:${NC}"
                echo "╔════════════════════╗"
                sed 's/0/·/g; s/1/█/g' "$sprite_dir/sprite.txt" | sed 's/^/║ /; s/$/ ║/' | head -10
                if [ $(wc -l < "$sprite_dir/sprite.txt") -gt 10 ]; then
                    echo "║        ...         ║"
                fi
                echo "╚════════════════════╝"
            fi
            echo ""
        fi
    done
}

# Función para generar un sprite
generate_sprite() {
    local prompt="$1"
    local width="$2"
    local height="$3"
    local model="$4"
    
    # Verificar si existe el script llm_sprites.py
    if [ ! -f "llm_sprites.py" ]; then
        echo -e "${RED}❌ Error: No se encontró el script llm_sprites.py${NC}"
        exit 1
    fi
    
    # Verificar que se proporcionó un prompt
    if [ -z "$prompt" ]; then
        echo -e "${RED}❌ Error: No se proporcionó una descripción para el sprite${NC}"
        echo -e "${YELLOW}Use --prompt=\"su descripción\" para especificar qué generar${NC}"
        exit 1
    fi
    
    # Usar valores por defecto si no se especificaron
    width=${width:-16}
    height=${height:-16}
    model=${model:-"gpt-4o"}
    
    # Verificar que width y height sean múltiplos de 8
    if [ $((width % 8)) -ne 0 ] || [ $((height % 8)) -ne 0 ]; then
        echo -e "${RED}❌ Error: El ancho y alto deben ser múltiplos de 8${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}🤖 Generando sprite: ${GREEN}$prompt${NC}"
    echo -e "${BLUE}📏 Dimensiones: ${GREEN}${width}x${height}${NC}"
    echo -e "${BLUE}🧠 Modelo: ${GREEN}$model${NC}"
    echo ""
    
    # Activar entorno virtual si existe
    if [ -d ".venv" ]; then
        echo -e "${BLUE}🔧 Activando entorno virtual...${NC}"
        source .venv/bin/activate 2>/dev/null
    fi
    
    # Ejecutar el script de generación
    python llm_sprites.py --prompt="$prompt" --width=$width --height=$height --model=$model
    result=$?
    
    if [ $result -ne 0 ]; then
        echo -e "${RED}❌ Error al generar el sprite. Código de error: $result${NC}"
        exit $result
    fi
    
    echo -e "${GREEN}✅ Sprite generado correctamente${NC}"
}

# Variables para los parámetros
PROMPT=""
WIDTH=16
HEIGHT=16
MODEL="gpt-4o"

# Procesar argumentos de línea de comandos
while [ "$#" -gt 0 ]; do
    case "$1" in
        --prompt=*)
            PROMPT="${1#*=}"
            ;;
        --width=*)
            WIDTH="${1#*=}"
            ;;
        --height=*)
            HEIGHT="${1#*=}"
            ;;
        --model=*)
            MODEL="${1#*=}"
            ;;
        --list)
            list_sprites
            exit 0
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Error: Opción desconocida: $1${NC}"
            show_help
            exit 1
            ;;
    esac
    shift
done

# Si no se especificaron argumentos, mostrar un menú interactivo
if [ -z "$PROMPT" ] && [ "$WIDTH" -eq 16 ] && [ "$HEIGHT" -eq 16 ] && [ "$MODEL" = "gpt-4o" ]; then
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}                                                                            ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}  ${GREEN}Generador de Sprites con IA${NC}                                             ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}                                                                            ${BLUE}║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    echo -e "${GREEN}Describe el sprite que quieres generar:${NC}"
    read -p "> " PROMPT
    
    if [ -z "$PROMPT" ]; then
        echo -e "${RED}❌ No se proporcionó una descripción. Operación cancelada.${NC}"
        exit 1
    fi
    
    # Preguntar por las dimensiones
    read -p "Ancho (múltiplo de 8, por defecto: 16): " input_width
    if [ -n "$input_width" ]; then
        WIDTH=$input_width
    fi
    
    read -p "Alto (múltiplo de 8, por defecto: 16): " input_height
    if [ -n "$input_height" ]; then
        HEIGHT=$input_height
    fi
    
    # Preguntar por el modelo
    read -p "Modelo LLM (por defecto: gpt-4o): " input_model
    if [ -n "$input_model" ]; then
        MODEL=$input_model
    fi
fi

# Generar el sprite
generate_sprite "$PROMPT" "$WIDTH" "$HEIGHT" "$MODEL"
exit $? 