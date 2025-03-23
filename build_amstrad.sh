#!/bin/bash

# Colores para mensajes
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Ruta a CPCtelera (ajusta esto según tu instalación)
CPCT_PATH="/home/oscar/cpctelera/cpctelera/"

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
        read -p "Presiona Enter para continuar..." dummy
        exit 1
    fi
    
    # Verificar que existe un Makefile
    if [ ! -f "$example_path/Makefile" ]; then
        echo -e "${RED}❌ Error: No se encontró un Makefile en $example_path${NC}" >&2
        read -p "Presiona Enter para continuar..." dummy
        exit 1
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
            read -p "Presiona Enter para continuar..." dummy
            exit 1
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
    cd "$example_path" || exit 1
    
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
        read -p "Presiona Enter para continuar..." dummy
        exit 1
    fi
    
    # Obtener la ruta completa del archivo DSK
    local dsk_file=$(find "$example_path" -name "*.dsk" | head -1)
    
    if [ -z "$dsk_file" ]; then
        echo -e "${RED}❌ Error: No se encontró un archivo DSK en $example_path${NC}" >&2
        echo -e "${BLUE}📄 Contenido del directorio:${NC}" >&2
        ls -la "$example_path" >&2
        read -p "Presiona Enter para continuar..." dummy
        exit 1
    fi
    
    echo -e "${GREEN}✨ Ejemplo compilado correctamente!${NC}" >&2
    echo -e "${GREEN}📋 Archivo DSK generado: $dsk_file${NC}" >&2
    read -p "Presiona Enter para continuar..." dummy
    
    # Devolver SOLO la ruta del DSK, sin ningún texto adicional
    echo "$dsk_file"
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
            if command -v retrovirtualmachine &> /dev/null; then
                echo -e "${GREEN}✅ Found RetroVirtualMachine emulator${NC}"
                echo -e "${BLUE}🚀 Starting RetroVirtualMachine with auto-execute...${NC}"
                echo -e "${BLUE}⚙️  Command: retrovirtualmachine -autostart \"$dsk_file\"${NC}"
                
                # Ejecutar en primer plano para ver los logs
                retrovirtualmachine -autostart "$dsk_file"
                
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

# Función para mostrar el menú interactivo
show_menu() {
    clear
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}                                                                            ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}  ${GREEN}AI (LLM) Amstrad CPC Program Builder${NC}                                      ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}                                                                            ${BLUE}║${NC}"
    echo -e "${BLUE}╠════════════════════════════════════════════════════════════════════════════╣${NC}"
    echo -e "${BLUE}║${NC}                                                                            ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}  ${GREEN}1)${NC} ✨ Generate program with Prompt                                        ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}  ${GREEN}2)${NC} 📋 List available examples                                             ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}  ${GREEN}3)${NC} 🚀 Compile and run an example                                          ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}  ${GREEN}4)${NC} 🎨 Generate sprites with Prompt                                        ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}  ${GREEN}5)${NC} 👋 Exit                                                                ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}                                                                            ${BLUE}║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    read -p "Select an option: " choice
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
        read -p "Press Enter to continue..."
        EXAMPLE=""
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
    
    if [ -n "$prompt" ]; then
        echo -e "${BLUE}🤖 Generating program with AI...${NC}"
        
        echo -e "${BLUE}📝 Calling LLM to generate code...${NC}"
        echo -e "${YELLOW}This may take a moment...${NC}"
        
        # Run the Python script with the prompt
        source .venv/bin/activate 2>/dev/null
        python llm_z80.py --platform=amstrad_cpc --prompt="$prompt"
        result=$?
        
        if [ $result -ne 0 ]; then
            echo -e "${RED}❌ Error: Failed to generate code. Error code: $result${NC}"
            read -p "Press Enter to return to the main menu..." dummy
            return 1
        fi
        
        # Find the most recently modified directory in local/
        generated_dir=$(find "local/" -maxdepth 1 -type d -name "*_*" -printf "%T@ %p\n" | sort -n | tail -1 | cut -f2- -d" ")
        
        if [ -z "$generated_dir" ] || [ ! -d "$generated_dir" ]; then
            echo -e "${RED}❌ Could not find the generated directory in local/folder${NC}"
            read -p "Press Enter to return to the main menu..." dummy
            return 1
        fi
        
        echo -e "${GREEN}✨ Code generated successfully in: $generated_dir${NC}"
        
        # Now compile the program
        echo -e "${BLUE}🔨 Compiling program...${NC}"
        
        # Check if there's a main.c file
        if [ -f "$generated_dir/main.c" ]; then
            # Navigate to the directory and compile
            original_dir="$PWD"
            cd "$generated_dir" || { 
                echo -e "${RED}❌ Failed to change to directory $generated_dir${NC}"; 
                read -p "Press Enter to return to the main menu..." dummy; 
                return 1; 
            }
            
            # Create proper directory structure
            mkdir -p src
            
            # Move main.c to src directory
            if [ -f "main.c" ]; then
                mv main.c src/
            fi
            
            # Verificar si SDCC está instalado
            sdcc_path=$(which sdcc 2>/dev/null)
            
            if [ -z "$sdcc_path" ]; then
                # Si no está en el PATH, verificar en la ruta de CPCtelera
                if [ -f "$CPCT_PATH/tools/sdcc-3.6.8-r9946/bin/sdcc" ]; then
                    sdcc_path="$CPCT_PATH/tools/sdcc-3.6.8-r9946/bin/sdcc"
                    echo -e "${GREEN}✅ Using CPCtelera SDCC: $sdcc_path${NC}"
                else
                    echo -e "${RED}❌ SDCC not found. Please install SDCC:${NC}"
                    echo -e "${BLUE}💡 In Ubuntu/Debian: sudo apt-get install sdcc${NC}"
                    echo -e "${BLUE}💡 In Arch Linux: sudo pacman -S sdcc${NC}"
                    cd "$original_dir"
                    read -p "Press Enter to return to the main menu..." dummy
                    return 1
                fi
            else
                echo -e "${GREEN}✅ Using system SDCC: $sdcc_path${NC}"
            fi
            
            # Copiar los archivos necesarios del template
            template_dir="$original_dir/templates/amstrad_cpc"
            template_makefile="$template_dir/Makefile"
            config_dir="$template_dir/cfg"
            
            # Copiar Makefile si no existe
            if [ ! -f "Makefile" ]; then
                if [ -f "$template_makefile" ]; then
                    echo -e "${BLUE}📋 Copying Makefile template...${NC}"
                    cp "$template_makefile" "Makefile"
                    
                    # Modificar el nombre del proyecto en el Makefile
                    project_name=$(basename "$generated_dir")
                    sed -i "s/example_name/$project_name/" "Makefile"
                    
                    # Verificar y copiar el directorio cfg
                    if [ -d "$config_dir" ]; then
                        echo -e "${BLUE}📁 Copying configuration files...${NC}"
                        mkdir -p "cfg"
                        cp -r "$config_dir"/* "cfg/"
                    else
                        echo -e "${YELLOW}⚠️ Configuration directory not found: $config_dir${NC}"
                        echo -e "${YELLOW}⚠️ Make sure it exists to ensure proper compilation${NC}"
                    fi
                else
                    echo -e "${RED}❌ Template Makefile not found: $template_makefile${NC}"
                    echo -e "${YELLOW}⚠️ Please create it at: $template_makefile${NC}"
                    cd "$original_dir"
                    read -p "Press Enter to return to the main menu..." dummy
                    return 1
                fi
            fi
            
            # Modificar temporalmente el Makefile para usar el SDCC encontrado
            if [ -f "cfg/build_config.mk" ]; then
                echo -e "${BLUE}🔧 Adjusting build_config.mk to use SDCC...${NC}"
                # Hacer una copia de seguridad
                cp cfg/build_config.mk cfg/build_config.mk.bak
                
                # Reemplazar la ruta de SDCC
                sed -i "s|Z80CCPATH.*|Z80CCPATH := $(dirname $sdcc_path)|g" cfg/build_config.mk
                echo -e "${GREEN}✅ Updated SDCC path in configuration${NC}"
            fi
            
            # Crear un script simple para la compilación
            env_setup="/tmp/amstrad_build_env.sh"
            echo "#!/bin/bash" > "$env_setup"
            echo "export PATH=$(dirname $sdcc_path):\$PATH" >> "$env_setup"
            echo "export Z80CCPATH=$(dirname $sdcc_path)" >> "$env_setup"
            echo "make CPCT_PATH=$CPCT_PATH" >> "$env_setup"
            chmod +x "$env_setup"
            
            # Crear un archivo para capturar la salida
            compilation_log="/tmp/amstrad_compile_detailed.log"
            
            # Ejecutar la compilación
            echo -e "${BLUE}🔨 Compiling with SDCC...${NC}"
            bash "$env_setup" > "$compilation_log" 2>&1
            compile_result=$?
            
            if [ $compile_result -ne 0 ]; then
                echo -e "${RED}❌ Compilation failed. Detailed diagnostic:${NC}"
                echo -e "${YELLOW}═════════════════ COMPILATION ERRORS ═════════════════${NC}"
                # Mostrar el log de compilación
                cat "$compilation_log"
                echo -e "${YELLOW}═════════════════════════════════════════════════════${NC}"
                
                # Información adicional de diagnóstico
                echo -e "${BLUE}🔍 Environment variables:${NC}"
                echo "CPCT_PATH=$CPCT_PATH"
                
                echo -e "${BLUE}🔍 Searching for specific error patterns:${NC}"
                grep -i "error" "$compilation_log" || echo "No specific error message found"
                
                cd "$original_dir"
                read -p "Press Enter to return to the main menu..." dummy
                return 1
            else
                echo -e "${GREEN}✅ Compilation successful!${NC}"
            fi
            
            # Find the generated DSK file (absolute path)
            dsk_file="$PWD/$(find . -name "*.dsk" | head -1)"
            
            if [ ! -f "$dsk_file" ]; then
                echo -e "${RED}❌ No DSK file found after compilation${NC}"
                cd "$original_dir"
                read -p "Press Enter to return to the main menu..." dummy
                return 1
            fi
            
            echo -e "${GREEN}📋 DSK file created: $dsk_file${NC}"
            
            # Return to original directory
            cd "$original_dir"
            
            # Select emulator if not already set
            if [ -z "$EMULATOR" ]; then
                select_emulator
            else
                EMULATOR=$DEFAULT_EMULATOR
            fi
            
            # Run the emulator
            echo -e "${BLUE}🚀 Running the program with emulator...${NC}"
            echo -e "${BLUE}📂 Using DSK file: $dsk_file${NC}"
            
            # Extract the name base of the DSK file and convert to uppercase
            local disk_basename=$(basename "$dsk_file" .dsk)
            local disk_name=$(echo "$disk_basename" | tr '[:lower:]' '[:upper:]')
            
            # Run the specified emulator
            case $EMULATOR in
                "cap32")
                    if command -v cap32 >/dev/null 2>&1; then
                        echo -e "${GREEN}✅ Found Caprice32 emulator${NC}"
                        echo -e "${BLUE}🚀 Starting Caprice32 with auto-execute...${NC}"
                        echo -e "${BLUE}⚙️  Command: cap32 \"$dsk_file\" -a \"run \\\"$disk_name\\\"\"${NC}"
                        cap32 "$dsk_file" -a "run \"$disk_name\""
                        echo -e "${GREEN}✅ Caprice32 exited successfully${NC}"
                    else
                        echo -e "${RED}❌ Caprice32 not found. Please install it.${NC}"
                        read -p "Press Enter to return to the main menu..." dummy
                        return 1
                    fi
                    ;;
                "retrovirtualmachine")
                    if command -v retrovirtualmachine >/dev/null 2>&1; then
                        echo -e "${GREEN}✅ Found RetroVirtualMachine emulator${NC}"
                        echo -e "${BLUE}🚀 Starting RetroVirtualMachine with auto-execute...${NC}"
                        echo -e "${BLUE}⚙️  Command: retrovirtualmachine -autostart \"$dsk_file\"${NC}"
                        retrovirtualmachine -autostart "$dsk_file"
                    else
                        echo -e "${RED}❌ Error: RetroVirtualMachine not found${NC}"
                        read -p "Press Enter to return to the main menu..." dummy
                        return 1
                    fi
                    ;;
                "xroar")
                    if command -v xroar >/dev/null 2>&1; then
                        echo -e "${GREEN}✅ Found XRoar emulator${NC}"
                        echo -e "${BLUE}🚀 Starting XRoar...${NC}"
                        echo -e "${BLUE}⚙️  Command: xroar -autostart \"$dsk_file\" -machine cpc${NC}"
                        xroar -autostart "$dsk_file" -machine cpc
                    else
                        echo -e "${RED}❌ Error: XRoar not found${NC}"
                        read -p "Press Enter to return to the main menu..." dummy
                        return 1
                    fi
                    ;;
                *)
                    echo -e "${RED}❌ Error: Emulator $EMULATOR not supported${NC}"
                    read -p "Press Enter to return to the main menu..." dummy
                    return 1
                    ;;
            esac
            
            echo -e "${GREEN}✅ Program execution completed${NC}"
            read -p "Press Enter to return to the main menu..." dummy
        else
            echo -e "${RED}❌ No main.c file found in $generated_dir${NC}"
            read -p "Press Enter to return to the main menu..." dummy
            return 1
        fi
    else
        echo -e "${RED}❌ No prompt provided. Operation cancelled.${NC}"
        read -p "Press Enter to return to the main menu..." dummy
        return 1
    fi
}

# Función para generar sprites con LLM
generate_sprites() {
    # Verificar si existe el script llm_sprites.py
    if [ ! -f "llm_sprites.py" ]; then
        echo -e "${RED}❌ Error: llm_sprites.py script not found${NC}"
        read -p "Press Enter to return to the main menu..." dummy
        return 1
    fi
    
    echo -e "${GREEN}Describe the sprite you want to generate:${NC}"
    read -p "> " prompt
    
    if [ -z "$prompt" ]; then
        echo -e "${RED}❌ No prompt provided. Operation cancelled.${NC}"
        read -p "Press Enter to return to the main menu..." dummy
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
    
    read -p "Press Enter to return to the main menu..." dummy
    return $result
}

# Procesar argumentos de línea de comandos
execute_emulator=true
specified_example=""
specified_emulator=""

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
        --help)
            show_help
            exit 0
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
        show_menu
        case $choice in
            1)
                generate_with_prompt
                ;;
            2)
                list_examples
                read -p "Presiona Enter para continuar..." dummy
                ;;
            3)
                select_example
                if [ -n "$EXAMPLE" ]; then
                    DSK_FILE=$(compile_example "$EXAMPLE")
                    if [ $? -eq 0 ]; then
                        select_emulator
                        run_emulator "$DSK_FILE" "$EMULATOR"
                    fi
                fi
                ;;
            4)
                generate_sprites
                ;;
            5)
                echo -e "${GREEN}👋 ¡Hasta luego!${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}❌ Opción inválida${NC}"
                sleep 1
                ;;
        esac
    done
fi 