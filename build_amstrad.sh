#!/bin/bash

# Colores para mensajes
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Ruta a CPCtelera (ajusta esto según tu instalación)
CPCT_PATH="/home/oscar/cpctelera/cpctelera"

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
    echo "  --help               Muestra esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  $0 --example=anivemin_example"
    echo "  $0 --example=easy/border"
    echo "  $0 --list-examples"
    echo "  $0 --example=text_example --emulator=cap32"
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
        exit 1
    fi
    
    # Verificar que existe un Makefile
    if [ ! -f "$example_path/Makefile" ]; then
        echo -e "${RED}❌ Error: No se encontró un Makefile en $example_path${NC}" >&2
        exit 1
    fi
    
    # Compilar el ejemplo usando la ruta correcta a CPCtelera
    echo "Ejecutando make con CPCT_PATH=$CPCT_PATH..." >&2
    cd "$example_path" && make CPCT_PATH=$CPCT_PATH >&2
    
    # Verificar si la compilación fue exitosa
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Error: Compilation failed${NC}" >&2
        cd - > /dev/null
        exit 1
    fi
    
    # Volver al directorio original
    cd - > /dev/null
    
    # Obtener la ruta completa del archivo DSK
    local dsk_file=$(find "$example_path" -name "*.dsk" | head -1)
    
    if [ -z "$dsk_file" ]; then
        echo -e "${RED}❌ Error: No se encontró un archivo DSK en $example_path${NC}" >&2
        exit 1
    fi
    
    echo -e "Ruta completa del DSK: $dsk_file" >&2
    echo -e "${GREEN}✨ Ejemplo compilado correctamente!${NC}" >&2
    echo -e "Archivo DSK generado: $dsk_file" >&2
    
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
    echo -e "${BLUE}║${NC}  ${GREEN}4)${NC} 👋 Exit                                                                ${BLUE}║${NC}"
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

# Function to generate program with prompt
generate_with_prompt() {
    echo -e "${BLUE}🔧 Amstrad CPC Program Generator${NC}"
    echo ""
    
    # Check if Python script exists
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
        
        # Reorganizar la estructura de directorios para Amstrad CPC
        if [ -f "$generated_dir/main.c" ]; then
            # Crear directorio src/ y obj/ si no existen
            mkdir -p "$generated_dir/src" "$generated_dir/obj"
            
            # Guardar una copia de respaldo del código original
            cp "$generated_dir/main.c" "$generated_dir/main.c.backup"
            
            # Mover el archivo main.c a src/
            mv "$generated_dir/main.c" "$generated_dir/src/main.c"
            
            echo -e "${GREEN}✅ Estructura de directorios reorganizada correctamente${NC}"
        elif [ -f "$generated_dir/src/main.c" ]; then
            # El archivo ya está en la ubicación correcta
            echo -e "${GREEN}✅ Estructura de directorios ya es correcta${NC}"
        else
            echo -e "${RED}❌ No se encontró el archivo main.c en ninguna ubicación esperada${NC}"
            read -p "Press Enter to return to the main menu..." dummy
            return 1
        fi
        
        # Now compile the program
        echo -e "${BLUE}🔨 Compiling program...${NC}"
        
        # Check if there's a main.c file in the root directory (where llm_z80.py places it)
        if [ -f "$generated_dir/src/main.c" ]; then
            # Create proper directory structure for Amstrad compilation
            mkdir -p "$generated_dir/src" "$generated_dir/obj"
            
            # Guardar una copia de respaldo del código original
            cp "$generated_dir/src/main.c" "$generated_dir/main.c.original"
            
            # Navigate to the directory and compile
            original_dir="$PWD"
            cd "$generated_dir" || { 
                echo -e "${RED}❌ Failed to change to directory $generated_dir${NC}"; 
                read -p "Press Enter to return to the main menu..." dummy; 
                return 1; 
            }
            
            # Create Makefile if needed
            if [ ! -f "Makefile" ]; then
                echo -e "${YELLOW}Creating Makefile...${NC}"
                cat > Makefile << 'EOL'
CPCT_PATH := $(CPCT_PATH)
CPCT_SHARED_PATH := $(CPCT_PATH)/tools/img2tileset
SRC := src
OBJ := obj

TARGET := generated
OUT := $(TARGET).dsk

SRCS := $(wildcard $(SRC)/*.c)
OBJS := $(SRCS:$(SRC)/%.c=$(OBJ)/%.o)

CCFLAGS := -mz80 -I$(CPCT_PATH)/src
CCFLAGS += -O2 -Wall
LDFLAGS := -mz80 --no-std-crt0 --code-loc 0x0400
LDFLAGS += -Wl -b_CODE=0x0400
LDFLAGS += -l$(CPCT_PATH)/cpctelera.lib

CC := sdcc

.PHONY: all clean

all: $(OUT)

$(OUT): $(TARGET)
	$(CPCT_PATH)/tools/hex2bin/2cdt.exe -n $(TARGET) -r $(TARGET) $(TARGET).bin $(OUT)

$(TARGET): $(OBJS)
	$(CC) $(LDFLAGS) -o $(TARGET).ihx $(OBJS)
	hex2bin -p 00 $(TARGET).ihx

$(OBJ)/%.o: $(SRC)/%.c
	$(CC) $(CCFLAGS) -c $< -o $@

clean:
	$(RM) $(TARGET) $(OUT) $(OBJS) $(TARGET).ihx $(TARGET).bin
EOL
            fi
            
            # Ensure obj directory exists
            mkdir -p obj
            
            # Compile
            make CPCT_PATH=$CPCT_PATH
            compile_result=$?
            
            if [ $compile_result -ne 0 ]; then
                echo -e "${RED}❌ Compilation failed${NC}"
                cd "$original_dir"
                read -p "Press Enter to return to the main menu..." dummy
                return 1
            fi
            
            echo -e "${GREEN}✅ Compilation successful!${NC}"
            
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
                        echo -e "${GREEN}✅ Starting Caprice32 emulator${NC}"
                        echo -e "${BLUE}⚙️  Command: cap32 \"$dsk_file\" -a \"run \\\"$disk_name\\\"\"${NC}"
                        cap32 "$dsk_file" -a "run \"$disk_name\""
                    else
                        echo -e "${RED}❌ Caprice32 not found. Please install it.${NC}"
                        read -p "Press Enter to return to the main menu..." dummy
                        return 1
                    fi
                    ;;
                "retrovirtualmachine")
                    if command -v retrovirtualmachine >/dev/null 2>&1; then
                        echo -e "${GREEN}✅ Starting RetroVirtualMachine emulator${NC}"
                        retrovirtualmachine -autostart "$dsk_file"
                    else
                        echo -e "${RED}❌ RetroVirtualMachine not found. Please install it.${NC}"
                        read -p "Press Enter to return to the main menu..." dummy
                        return 1
                    fi
                    ;;
                "xroar")
                    if command -v xroar >/dev/null 2>&1; then
                        echo -e "${GREEN}✅ Starting XRoar emulator${NC}"
                        xroar -autostart "$dsk_file" -machine cpc
                    else
                        echo -e "${RED}❌ XRoar not found. Please install it.${NC}"
                        read -p "Press Enter to return to the main menu..." dummy
                        return 1
                    fi
                    ;;
                *)
                    echo -e "${RED}❌ Unknown emulator: $EMULATOR. Using Caprice32 instead.${NC}"
                    if command -v cap32 >/dev/null 2>&1; then
                        echo -e "${GREEN}✅ Starting Caprice32 emulator${NC}"
                        cap32 "$dsk_file" -a "run \"$disk_name\""
                    else
                        echo -e "${RED}❌ No emulator found. Please install Caprice32.${NC}"
                        read -p "Press Enter to return to the main menu..." dummy
                        return 1
                    fi
                    ;;
            esac
        else
            echo -e "${RED}❌ No main.c file found in $generated_dir${NC}"
            read -p "Press Enter to return to the main menu..." dummy
            return 1
        fi
    fi
    return 0
}

# Procesar argumentos
if [ $# -eq 0 ]; then
    while true; do
        show_menu
        case $choice in
            1)
                generate_with_prompt
                ;;
            2)
                list_examples
                read -p "Press Enter to continue..."
                ;;
            3)
                select_example
                if [ -n "$EXAMPLE" ]; then
                    select_emulator
                    DSK_FILE=$(compile_example "$EXAMPLE")
                    if [ ! -f "$DSK_FILE" ]; then
                        echo -e "${RED}❌ Error: DSK file not found after compilation${NC}"
                        exit 1
                    fi
                    run_emulator "$DSK_FILE" "$EMULATOR"
                    exit 0
                fi
                ;;
            4)
                echo "Goodbye!"
                exit 0
                ;;
            *)
                echo -e "${RED}Invalid option${NC}"
                ;;
        esac
    done
else
    EXAMPLE=""
    NO_EMULATOR=false
    EMULATOR=$DEFAULT_EMULATOR

    for arg in "$@"; do
        case $arg in
            --example=*)
                EXAMPLE="${arg#*=}"
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
                NO_EMULATOR=true
                ;;
            --emulator=*)
                EMULATOR="${arg#*=}"
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                echo -e "${RED}❌ Error: Unknown option: $arg${NC}"
                show_help
                exit 1
                ;;
        esac
    done

    # Si se especificó un ejemplo, compilarlo y ejecutarlo
    if [ -n "$EXAMPLE" ]; then
        DSK_FILE=$(compile_example "$EXAMPLE")
        
        # Si la compilación fue exitosa y no se especificó --no-emulator, ejecutar el emulador
        if [ $? -eq 0 ] && [ "$NO_EMULATOR" = false ]; then
            if [ ! -f "$DSK_FILE" ]; then
                echo -e "${RED}❌ Error: DSK file not found after compilation${NC}"
                exit 1
            fi
            run_emulator "$DSK_FILE" "$EMULATOR"
            exit 0
        fi
    fi
fi 