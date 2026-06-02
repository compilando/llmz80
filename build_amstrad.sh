#!/bin/bash

# Colores para mensajes
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Ruta a CPCtelera. Respeta CPCT_PATH si ya está definido en el entorno.
CPCT_PATH="${CPCT_PATH:-/home/oscar/cpctelera/cpctelera/}"

# Emulador por defecto
DEFAULT_EMULATOR="cap32"

# Función para mostrar ayuda
show_help() {
    echo -e "${BLUE}🔧 Amstrad CPC Program Builder${NC}"
    echo ""
    echo "Uso: $0 [opciones]"
    echo ""
    echo "Opciones:"
    echo "  --example=NOMBRE     Compila y ejecuta el ejemplo especificado"
    echo "  --list-examples      Lista todos los ejemplos disponibles"
    echo "  --show-errors        Muestra soluciones a errores comunes"
    echo "  --no-emulator        Compila pero no ejecuta el emulador"
    echo "  --emulator=EMULADOR  Especifica el emulador a usar (cap32, retrovirtualmachine, xroar)"
    echo "  --prompt             Genera un programa usando IA basado en tu descripción"
    echo "  --clean              Removes all temporary files and folders in ./local"
    echo "  --help               Muestra esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  $0 --example=anivemin_example"
    echo "  $0 --example=easy/border"
    echo "  $0 --list-examples"
    echo "  $0 --example=text_example --emulator=cap32"
    echo "  $0 --prompt"
    echo ""
}

# Función para listar ejemplos
list_examples() {
    echo -e "${BLUE}🔧 Amstrad CPC Program Builder${NC}"
    echo ""
    echo -e "${GREEN}Available examples:${NC}"
    echo ""
    
    echo -e "${BLUE}Examples:${NC}"
    # Buscar carpetas con Makefile en cualquier nivel bajo examples/amstrad_cpc
    find examples/amstrad_cpc -type f -name "Makefile" | sed 's|/Makefile$||' | \
    sed 's|examples/amstrad_cpc/||' | sort | while read -r example; do
        # Mostrar solo si no es la carpeta common
        if [[ "$example" != "common" && "$example" != "common/"* ]]; then
            echo "  - $example"
        fi
    done
}

# Función para mostrar soluciones a errores comunes
show_errors() {
    if [ -f "examples/amstrad_cpc/error_solutions.md" ]; then
        cat "examples/amstrad_cpc/error_solutions.md"
    else
        echo -e "${RED}❌ Error: No se encontró el archivo de soluciones a errores${NC}"
    fi
}

# Función para crear la estructura de directorios de un nuevo ejemplo
create_example_structure() {
    local example_name=$1
    local example_path="examples/amstrad_cpc/$example_name"
    
    # Crear directorios
    mkdir -p "$example_path/src" "$example_path/obj"
    
    # Copiar Makefile template
    cp "examples/amstrad_cpc/common/Makefile.template" "$example_path/Makefile"
    
    # Modificar el nombre del proyecto en el Makefile
    sed -i "s/example_name/${example_name##*/}/" "$example_path/Makefile"
    
    echo -e "${GREEN}✨ Estructura creada para el ejemplo $example_name${NC}"
}

# Función para compilar un ejemplo
compile_example() {
    local example=$1
    local example_path="examples/amstrad_cpc/$example"
    
    echo -e "${BLUE}🔧 Amstrad CPC Program Builder${NC}" >&2
    echo "" >&2
    echo -e "Compiling example: ${example_path}" >&2
    
    # Verificar que el directorio del ejemplo existe
    if [ ! -d "$example_path" ]; then
        echo -e "${RED}❌ Error: El ejemplo $example no existe${NC}" >&2
        echo "Usa --list-examples para ver los ejemplos disponibles" >&2
        return 1
    fi
    
    # Verificar que existe un Makefile
    if [ ! -f "$example_path/Makefile" ]; then
        echo -e "${RED}❌ Error: No se encontró un Makefile en $example_path${NC}" >&2
        return 1
    fi
    
    # Verificar si SDCC está instalado
    sdcc_path=$(which sdcc 2>/dev/null)
    
    if [ -z "$sdcc_path" ]; then
        # Si no está en el PATH, verificar en la ruta de CPCtelera
        if [ -f "$CPCT_PATH/tools/sdcc-3.6.8-r9946/bin/sdcc" ]; then
            sdcc_path="$CPCT_PATH/tools/sdcc-3.6.8-r9946/bin/sdcc"
            echo -e "${GREEN}✅ Using CPCtelera SDCC: $sdcc_path${NC}" >&2
        else
            echo -e "${RED}❌ SDCC not found. Please install SDCC:${NC}" >&2
            echo -e "${BLUE}💡 In Ubuntu/Debian: sudo apt-get install sdcc${NC}" >&2
            echo -e "${BLUE}💡 In Arch Linux: sudo pacman -S sdcc${NC}" >&2
            return 1
        fi
    else
        echo -e "${GREEN}✅ Using system SDCC: $sdcc_path${NC}" >&2
    fi
    
    # Compilar el ejemplo usando la ruta correcta a CPCtelera
    echo -e "${BLUE}🔨 Compiling with CPCT_PATH=$CPCT_PATH...${NC}" >&2
    
    # Crear un script simple para configurar el entorno
    env_setup="/tmp/amstrad_build_env.sh"
    echo "#!/bin/bash" > "$env_setup"
    echo "export PATH=$(dirname $sdcc_path):\$PATH" >> "$env_setup"
    echo "export Z80CCPATH=$(dirname $sdcc_path)" >> "$env_setup"
    echo "make CPCT_PATH=$CPCT_PATH" >> "$env_setup"
    chmod +x "$env_setup"
    
    # Guardar el directorio actual
    current_dir="$PWD"
    
    # Cambiar al directorio del ejemplo
    cd "$example_path" || return 1
    
    # Archivo para capturar la salida de compilación
    compilation_log="/tmp/amstrad_compile_output.log"
    
    # Ejecutar la compilación
    bash "$env_setup" > "$compilation_log" 2>&1
    compile_result=$?
    
    # Volver al directorio original
    cd "$current_dir"
    
    if [ $compile_result -ne 0 ]; then
        echo -e "${RED}❌ Error: La compilación falló. Salida detallada:${NC}" >&2
        cat "$compilation_log" >&2
        return 1
    fi
    
    # Obtener la ruta completa del archivo DSK
    local dsk_file=$(find "$example_path" -name "*.dsk" | head -1)
    
    if [ -z "$dsk_file" ]; then
        echo -e "${RED}❌ Error: No se encontró un archivo DSK en $example_path${NC}" >&2
        echo -e "${BLUE}📄 Contenido del directorio:${NC}" >&2
        ls -la "$example_path" >&2
        return 1
    fi
    
    echo -e "${GREEN}✨ Ejemplo compilado correctamente!${NC}" >&2
    echo -e "${GREEN}📋 Archivo DSK generado: $dsk_file${NC}" >&2
    
    # Devolver SOLO la ruta del DSK, sin ningún texto adicional
    echo "$dsk_file"
    return 0
}

# Function to run the emulator
run_emulator() {
    local dsk_file=$1
    local emulator=$2
    
    echo -e "${BLUE}🔧 Launching emulator: $emulator${NC}"
    echo -e "${BLUE}📂 DSK file: $dsk_file${NC}"
    
    # Verificar que el archivo DSK existe
    if [ ! -f "$dsk_file" ]; then
        echo -e "${RED}❌ Error: DSK file not found: $dsk_file${NC}"
        return 1
    fi
    
    # Verificar que el archivo DSK tiene permisos de lectura
    if [ ! -r "$dsk_file" ]; then
        echo -e "${RED}❌ Error: Cannot read DSK file: $dsk_file${NC}"
        return 1
    fi
    
    case $emulator in
        "cap32")
            if command -v cap32 &> /dev/null; then
                # Extraer el nombre base del archivo DSK y convertirlo a mayúsculas
                local disk_basename=$(basename "$dsk_file" .dsk)
                local disk_name=$(echo "$disk_basename" | tr '[:lower:]' '[:upper:]')
                
                echo -e "${GREEN}✅ Found Caprice32 emulator${NC}"
                echo -e "${BLUE}🚀 Starting Caprice32 with auto-execute...${NC}"
                echo -e "${BLUE}⚙️  Command: cap32 \"$dsk_file\" -a \"run \\\"$disk_name\\\"\"${NC}"
                
                # Ejecutar en primer plano para ver los logs
                cap32 "$dsk_file" -a "run \"$disk_name\""
                
                # Verificar el código de retorno
                if [ $? -eq 0 ]; then
                    echo -e "${GREEN}✅ Caprice32 exited successfully${NC}"
                else
                    echo -e "${RED}❌ Caprice32 exited with error code: $?${NC}"
                fi
            else
                echo -e "${RED}❌ Error: Caprice32 not found${NC}"
                echo -e "${BLUE}💡 Please install Caprice32:${NC}"
                echo -e "  sudo pacman -S caprice32"
                return 1
            fi
            ;;
        "retrovirtualmachine")
            # El ejecutable se llama RetroVirtualMachine (con mayúsculas)
            if command -v RetroVirtualMachine &> /dev/null; then
                echo -e "${GREEN}✅ Found RetroVirtualMachine emulator${NC}"
                echo -e "${BLUE}🚀 Starting RetroVirtualMachine with auto-execute...${NC}"
                echo -e "${BLUE}⚙️  Command: RetroVirtualMachine \"$dsk_file\"${NC}"
                
                # Ejecutar en primer plano para ver los logs
                RetroVirtualMachine "$dsk_file"
                
                # Verificar el código de retorno
                if [ $? -eq 0 ]; then
                    echo -e "${GREEN}✅ RetroVirtualMachine exited successfully${NC}"
                else
                    echo -e "${RED}❌ RetroVirtualMachine exited with error code: $?${NC}"
                fi
            else
                echo -e "${RED}❌ Error: RetroVirtualMachine not found${NC}"
                echo -e "${BLUE}💡 Please install RetroVirtualMachine:${NC}"
                echo -e "  sudo pacman -S retrovirtualmachine"
                return 1
            fi
            ;;
        "xroar")
            if command -v xroar &> /dev/null; then
                echo -e "${GREEN}✅ Found XRoar emulator${NC}"
                echo -e "${BLUE}🚀 Starting XRoar with auto-execute...${NC}"
                echo -e "${BLUE}⚙️  Command: xroar -autostart \"$dsk_file\" -machine cpc${NC}"
                
                # Ejecutar en primer plano para ver los logs
                xroar -autostart "$dsk_file" -machine cpc
                
                # Verificar el código de retorno
                if [ $? -eq 0 ]; then
                    echo -e "${GREEN}✅ XRoar exited successfully${NC}"
                else
                    echo -e "${RED}❌ XRoar exited with error code: $?${NC}"
                fi
            else
                echo -e "${RED}❌ Error: XRoar not found${NC}"
                echo -e "${BLUE}💡 Please install XRoar:${NC}"
                echo -e "  sudo pacman -S xroar"
                return 1
            fi
            ;;
        *)
            echo -e "${RED}❌ Error: Unsupported emulator: $emulator${NC}"
            echo -e "${BLUE}💡 Supported emulators:${NC}"
            echo -e "  - cap32"
            echo -e "  - retrovirtualmachine"
            echo -e "  - xroar"
            return 1
            ;;
    esac
}

# Function to display the main menu
display_menu() {
    clear
    echo "╔════════════════════════════════════════════════════════════════════════════╗"
    echo "║                                                                            ║"
    echo "║  AI (LLM) Amstrad CPC Program Builder                                      ║"
    echo "║                                                                            ║"
    echo "╠════════════════════════════════════════════════════════════════════════════╣"
    echo "║                                                                            ║"
    echo "║  1) ✨ Generate program with Prompt                                        ║"
    echo "║  2) 📋 List available examples                                             ║"
    echo "║  3) 🚀 Compile and run an example                                          ║"
    echo "║  4) 🎨 Generate sprites with Prompt                                        ║"
    echo "║  5) 📊 Populate Vector DB with Examples                                    ║"
    echo "║  6) 🧹 Clean temporary files (./local)                                     ║"
    echo "║  7) 👋 Exit                                                                ║"
    echo "║                                                                            ║"
    echo "╚════════════════════════════════════════════════════════════════════════════╝"
}

# Función para seleccionar ejemplo interactivamente
select_example() {
    clear
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}                                                                                ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}  ${GREEN}Available Examples${NC}                                               ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}                                                                                ${BLUE}║${NC}"
    echo -e "${BLUE}╠════════════════════════════════════════════════════════════════════════════╣${NC}"
    echo -e "${BLUE}║${NC}                                                                                ${BLUE}║${NC}"
    
    # Crear un array con los ejemplos
    mapfile -t examples < <(find examples/amstrad_cpc -type f -name "Makefile" | \
                          sed 's|/Makefile$||' | \
                          sed 's|examples/amstrad_cpc/||' | \
                          grep -v "^common" | sort)
    
    # Mostrar ejemplos numerados
    for i in "${!examples[@]}"; do
        printf "${BLUE}║${NC}  %3d) %s\n" $((i+1)) "${examples[$i]}"
    done
    
    echo -e "${BLUE}║${NC}                                                                             ${BLUE}║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    read -p "Select example number: " example_num
    
    # Validar entrada y seleccionar ejemplo
    if [[ "$example_num" =~ ^[0-9]+$ ]] && [ "$example_num" -ge 1 ] && [ "$example_num" -le "${#examples[@]}" ]; then
        EXAMPLE="${examples[$((example_num-1))]}"
    else
        echo -e "${RED}Invalid selection${NC}"
        return 1
    fi
}

# Función para seleccionar emulador interactivamente
select_emulator() {
    clear
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}                                                                            ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}  ${GREEN}Available Emulators${NC}                                                   ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}                                                                            ${BLUE}║${NC}"
    echo -e "${BLUE}╠════════════════════════════════════════════════════════════════════════════╣${NC}"
    echo -e "${BLUE}║${NC}                                                                            ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}  ${GREEN}1)${NC} 🎮 Caprice32 (default)                                                 ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}  ${GREEN}2)${NC} 🎲 RetroVirtualMachine                                                 ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}  ${GREEN}3)${NC} 🎯 XRoar                                                               ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}                                                                            ${BLUE}║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    read -p "Select emulator number: " emulator_num
    case $emulator_num in
        1) EMULATOR="cap32" ;;
        2) EMULATOR="retrovirtualmachine" ;;
        3) EMULATOR="xroar" ;;
        *) EMULATOR=$DEFAULT_EMULATOR ;;
    esac
}

# Función para generar un programa con prompt
generate_with_prompt() {
    # Verificar si existe el script llm_z80.py
    if [ ! -f "llm_z80.py" ]; then
        echo -e "${RED}❌ Error: llm_z80.py script not found${NC}"
        return 1
    fi

    echo -e "${GREEN}Describe the program you want to generate:${NC}"
    read -p "> " prompt

    if [ -z "$prompt" ]; then
        echo -e "${RED}❌ No prompt provided. Operation cancelled.${NC}"
        return 1
    fi

    echo -e "${BLUE}🤖 Generating program with AI...${NC}"
    echo -e "${BLUE}📝 Calling LLM (generate + validate + compile + auto-correct + emulator)${NC}"
    echo -e "${YELLOW}This may take a moment...${NC}"

    # Delegate the full pipeline to llm_z80.py so that:
    #  - pre-compilation validator runs (catches arity / unknown cpct_ funcs)
    #  - correction loop runs on SDCC failure (up to 3 attempts)
    #  - learning system records errors/successes
    #  - emulator launches on success
    # Previous flow used --no-compile then re-compiled here, which BYPASSED all of that.
    source .venv/bin/activate 2>/dev/null
    python llm_z80.py --platform=amstrad_cpc --prompt="$prompt" --launch-emulator
    return $?
}


# Función para generar sprites con LLM
generate_sprites() {
    # Verificar si existe el script llm_sprites.py
    if [ ! -f "llm_sprites.py" ]; then
        echo -e "${RED}❌ Error: llm_sprites.py script not found${NC}"
        return 1
    fi
    
    echo -e "${GREEN}Describe the sprite you want to generate:${NC}"
    read -p "> " prompt
    
    if [ -z "$prompt" ]; then
        echo -e "${RED}❌ No prompt provided. Operation cancelled.${NC}"
        return 1
    fi
    
    # Preguntar por las dimensiones
    read -p "Width (multiple of 8, default: 16): " width
    width=${width:-16}  # Valor por defecto: 16
    
    read -p "Height (multiple of 8, default: 16): " height
    height=${height:-16}  # Valor por defecto: 16
    
    echo -e "${BLUE}🤖 Generating sprite with AI...${NC}"
    
    # Activar el entorno virtual si existe
    source .venv/bin/activate 2>/dev/null
    
    # Ejecutar el script
    python llm_sprites.py --prompt="$prompt" --width=$width --height=$height
    result=$?
    
    if [ $result -ne 0 ]; then
        echo -e "${RED}❌ Error: Failed to generate sprite. Error code: $result${NC}"
    fi
    
    return $result
}

# Function to populate vector database
# Placeholder function - Will call the python script later
populate_vector_db() {
    echo "📊 Populating Vector DB for Amstrad CPC examples..."
    # Corrected Python script name
    if python llm_z80.py --populate-db --platform amstrad_cpc; then
        echo "✅ Vector DB population process finished."
    else
        echo "❌ Error during Vector DB population."
    fi
}

# --- Nueva función para limpiar ./local ---
clean_local_directory() {
    echo -e "${BLUE}🧹 Limpiando archivos temporales...${NC}"
    if [ -d "./local" ]; then
        echo "   Eliminando contenido de ./local/" 
        # Usar find para más seguridad que rm -rf *, y manejar si local está vacío
        find ./local -mindepth 1 -delete
        local exit_code=$?
        if [ $exit_code -eq 0 ]; then
            echo -e "${GREEN}✅ Archivos temporales en ./local eliminados.${NC}"
        else
            echo -e "${RED}❌ Error limpiando archivos temporales en ./local (Code: $exit_code).${NC}"
            # Devolver el código de error para que el menú sepa si falló
            return $exit_code
        fi
    else
        echo -e "${BLUE}ℹ️ Directorio ./local no encontrado, nada que limpiar.${NC}"
    fi
    return 0
}

# Procesar argumentos de línea de comandos
execute_emulator=true
specified_example=""
specified_emulator=""
POPULATE_DB=0
CLEAN_LOCAL=false

while [ "$#" -gt 0 ]; do
    case "$1" in
        --example=*)
            specified_example="${1#*=}"
            if [ -z "$specified_example" ]; then
                echo -e "${RED}❌ Error: No se especificó un nombre de ejemplo${NC}"
                exit 1
            fi
            ;;
        --list-examples)
            list_examples
            exit 0
            ;;
        --show-errors)
            show_errors
            exit 0
            ;;
        --no-emulator)
            execute_emulator=false
            ;;
        --emulator=*)
            specified_emulator="${1#*=}"
            if [ -z "$specified_emulator" ]; then
                echo -e "${RED}❌ Error: No se especificó un emulador${NC}"
                exit 1
            fi
            # Verificar que el emulador sea válido
            case "$specified_emulator" in
                cap32|retrovirtualmachine|xroar)
                    EMULATOR="$specified_emulator"
                    ;;
                *)
                    echo -e "${RED}❌ Error: Emulador no válido: $specified_emulator${NC}"
                    echo "Emuladores válidos: cap32, retrovirtualmachine, xroar"
                    exit 1
                    ;;
            esac
            ;;
        --prompt)
            generate_with_prompt
            exit $?
            ;;
        --clean)
            CLEAN_LOCAL=true
            ;;
        --help)
            show_help
            exit 0
            ;;
        --populate)
            POPULATE_DB=1
            ;;
        *)
            echo -e "${RED}❌ Error: Unknown option: $1${NC}"
            show_help
            exit 1
            ;;
    esac
    shift
done

# Si se especificó un ejemplo, compilarlo y ejecutarlo
if [ -n "$specified_example" ]; then
    DSK_FILE=$(compile_example "$specified_example")
    
    # Si la compilación fue exitosa y no se especificó --no-emulator, ejecutar el emulador
    if [ $? -eq 0 ] && [ "$execute_emulator" = true ]; then
        if [ ! -f "$DSK_FILE" ]; then
            echo -e "${RED}❌ Error: DSK file not found after compilation${NC}"
            exit 1
        fi
        run_emulator "$DSK_FILE" "$EMULATOR"
        exit 0
    fi
fi

# Si no se especificó ningún argumento, mostrar el menú interactivo
if [ "$#" -eq 0 ]; then
    while true; do
        display_menu
        read -p "Select an option: " choice

        case $choice in
            1) generate_with_prompt ;;
            2) 
                list_examples 
                read -p "Press Enter to continue..." # Pausa para ver la lista
                ;;
            3)
                select_example # Pregunta interactivamente por el ejemplo
                if [ -n "$EXAMPLE" ]; then # EXAMPLE es la variable que setea select_example
                    select_emulator # Pregunta interactivamente por el emulador
                    dsk_file_result=$(compile_example "$EXAMPLE") # Llama a la función de compilación
                    compile_exit_code=$?
                    dsk_file=$(echo "$dsk_file_result" | tail -n 1)
                    if [ $compile_exit_code -eq 0 ]; then
                         run_emulator "$dsk_file" "$EMULATOR"
                    else
                         # El error ya se mostró en compile_example (o debería)
                         read -p "Compilation failed. Press Enter to continue..."
                    fi
                fi
                ;;
            4) generate_sprites ;;
            5) populate_vector_db ;;
            6) clean_local_directory ;;
            7) echo "👋 Exiting..."; exit 0 ;;
            *) echo "❌ Invalid option. Please try again."; sleep 2 ;;
        esac
    done
fi

# Si se especificó la opción --populate, llamar directamente a la función
if [[ "$POPULATE_DB" -eq 1 ]]; then
    populate_vector_db
    exit 0
fi

# Si se especificó la opción --clean, limpiar el directorio local
if [ "$CLEAN_LOCAL" = true ]; then
    clean_local_directory # Llamar a la función
    clean_exit_code=$?
    # Después de limpiar, salir si era la única acción.
    if [ -z "$specified_example" ] && [ "$execute_emulator" = true ] && [ "$POPULATE_DB" -eq 0 ]; then
        exit $clean_exit_code
    fi
fi

# --- Execute Clean Action --- 
# ... (bloque --clean como antes) ...

# --- Determine Action --- 
# Si se pasó un argumento de acción específico, no mostrar menú
ACTION_REQUESTED=false
if [ -n "$EXAMPLE_NAME" ] || [ "$LIST_EXAMPLES" = true ] || [ "$SHOW_ERRORS" = true ] || [ "$GENERATE_PROMPT" = true ]; then
    ACTION_REQUESTED=true
fi

# --- Execute Actions OR Show Menu --- 
if [ "$ACTION_REQUESTED" = true ]; then
    # Ejecutar acciones basadas en flags
    if [ "$LIST_EXAMPLES" = true ]; then
        list_examples
    elif [ "$SHOW_ERRORS" = true ]; then
        show_errors
    elif [ "$GENERATE_PROMPT" = true ]; then
        generate_with_prompt # Asumiendo que esta es la función correcta
    elif [ -n "$EXAMPLE_NAME" ]; then
        # Compilar el ejemplo
        dsk_file_result=$(compile_example "$EXAMPLE_NAME")
        compile_exit_code=$?
        
        # Extraer solo la ruta del DSK (última línea)
        dsk_file=$(echo "$dsk_file_result" | tail -n 1)

        # Ejecutar emulador si la compilación fue exitosa y no se indicó lo contrario
        if [ $compile_exit_code -eq 0 ] && [ "$RUN_EMULATOR" = true ]; then
            if [ -f "$dsk_file" ]; then
                run_emulator "$dsk_file" "$EMULATOR"
            else
                echo -e "${RED}❌ Error: DSK file '$dsk_file' not found after successful compilation report?${NC}"
            fi
        elif [ $compile_exit_code -ne 0 ]; then
             echo -e "${RED}❌ Compilation failed, emulator skipped.${NC}"
        fi
    fi
else
    # No se solicitaron acciones por argumentos, mostrar menú interactivo
    # (Aquí va el bucle while true con display_menu y case)
    while true; do
        display_menu
        read -p "Select an option: " choice

        case $choice in
            1) generate_with_prompt ;; 
            2) 
                list_examples 
                read -p "Press Enter to continue..." # Pausa para ver la lista
                ;; 
            3) 
                select_example # Pregunta interactivamente
                if [ -n "$EXAMPLE" ]; then # EXAMPLE es la variable que setea select_example
                    select_emulator # Pregunta interactivamente
                    dsk_file_result=$(compile_example "$EXAMPLE")
                    compile_exit_code=$?
                    dsk_file=$(echo "$dsk_file_result" | tail -n 1)
                    if [ $compile_exit_code -eq 0 ]; then
                         run_emulator "$dsk_file" "$EMULATOR"
                    else
                         # El error ya se mostró en compile_example
                         read -p "Compilation failed. Press Enter to continue..."
                    fi
                fi
                ;; 
            4) 
                generate_sprites # Llamar a la función para generar sprites
                read -p "Press Enter to continue..."
                ;; 
            5) populate_vector_db ;; # Asegúrate que esta función existe
            6) clean_local_directory ;; # Nueva opción para limpiar
            7) echo "👋 Exiting..."; exit 0 ;; # Ahora la opción de salir es la 7
            *) echo "❌ Invalid option. Please try again."; sleep 2 ;; 
        esac
    done
fi
