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
    find examples/amstrad_cpc -maxdepth 2 -type d -not -path "*/\.*" -not -path "*/common*" | sort | sed 's|examples/amstrad_cpc/||' | grep -v "^$" | while read -r example; do
        echo "  - $example"
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
    
    echo -e "${BLUE}🔧 Amstrad CPC Program Builder${NC}"
    echo ""
    echo -e "Compiling example: ${example_path}"
    
    # Verificar que el directorio del ejemplo existe
    if [ ! -d "$example_path" ]; then
        echo -e "${RED}❌ Error: El ejemplo $example no existe${NC}"
        echo "Usa --list-examples para ver los ejemplos disponibles"
        exit 1
    fi
    
    # Verificar que existe un Makefile
    if [ ! -f "$example_path/Makefile" ]; then
        echo -e "${RED}❌ Error: No se encontró un Makefile en $example_path${NC}"
        exit 1
    fi
    
    # Compilar el ejemplo usando la ruta correcta a CPCtelera
    echo "Ejecutando make con CPCT_PATH=$CPCT_PATH..."
    cd "$example_path" && make CPCT_PATH=$CPCT_PATH
    
    # Verificar si la compilación fue exitosa
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Error: Compilation failed${NC}"
        cd - > /dev/null
        exit 1
    fi
    
    # Volver al directorio original
    cd - > /dev/null
    
    # Obtener la ruta completa del archivo DSK
    local dsk_file=$(find "$example_path" -name "*.dsk" | head -1)
    
    if [ -z "$dsk_file" ]; then
        echo -e "${RED}❌ Error: No se encontró un archivo DSK en $example_path${NC}"
        exit 1
    fi
    
    echo -e "Ruta completa del DSK: $dsk_file"
    echo -e "${GREEN}✨ Ejemplo compilado correctamente!${NC}"
    echo -e "Archivo DSK generado: $dsk_file"
    
    # Devolver la ruta del DSK
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
                echo -e "${GREEN}✅ Found Caprice32 emulator${NC}"
                echo -e "${BLUE}🚀 Starting Caprice32 with auto-execute...${NC}"
                echo -e "${BLUE}⚙️  Command: cap32 -a \"$dsk_file\"${NC}"
                
                # Ejecutar en primer plano para ver los logs
                cap32 -a "$dsk_file"
                
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
    find examples/amstrad_cpc -maxdepth 2 -type d -not -path "*/\.*" -not -path "*/common*" | sort | sed 's|examples/amstrad_cpc/||' | grep -v "^$" | nl | while read -r line; do
        echo -e "${BLUE}║${NC}  ${line}"
    done
    echo -e "${BLUE}║${NC}                                                                             ${BLUE}║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    read -p "Select example number: " example_num
    EXAMPLE=$(find examples/amstrad_cpc -maxdepth 2 -type d -not -path "*/\.*" -not -path "*/common*" | sort | sed 's|examples/amstrad_cpc/||' | grep -v "^$" | sed -n "${example_num}p")
}

# Función para seleccionar emulador interactivamente
select_emulator() {
    clear
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}                                                                                ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}  ${GREEN}Available Emulators${NC}                                             ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}                                                                                ${BLUE}║${NC}"
    echo -e "${BLUE}╠════════════════════════════════════════════════════════════════════════════╣${NC}"
    echo -e "${BLUE}║${NC}                                                                                ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}  ${GREEN}1)${NC} 🎮 Caprice32 (default)                                      ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}  ${GREEN}2)${NC} 🎲 RetroVirtualMachine                                     ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}  ${GREEN}3)${NC} 🎯 XRoar                                                    ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}                                                                                ${BLUE}║${NC}"
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
    
    # Verificar si existe el archivo de prompt
    local prompt_file="system_prompt_amstrad.txt"
    if [ ! -f "$prompt_file" ]; then
        echo -e "${RED}❌ Error: System prompt file not found: $prompt_file${NC}"
        return 1
    fi
    
    echo -e "${GREEN}Describe the program you want to generate:${NC}"
    read -p "> " prompt
    
    if [ -n "$prompt" ]; then
        echo -e "${BLUE}Generating program...${NC}"
        
        # Create common directory and template if they don't exist
        if ! mkdir -p "examples/amstrad_cpc/common"; then
            echo -e "${RED}❌ Error: Could not create common directory${NC}"
            return 1
        fi
        
        # Create Makefile template if it doesn't exist
        if [ ! -f "examples/amstrad_cpc/common/Makefile.template" ]; then
            echo -e "${BLUE}💡 Creating Makefile template...${NC}"
            cat > "examples/amstrad_cpc/common/Makefile.template" << 'EOL'
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

.PHONY: all clean

all: $(OUT)

$(OUT): $(TARGET)
	$(CPCT_PATH)/tools/hex2bin/2cdt.exe -n $(TARGET) -r $(TARGET) $(TARGET).bin $(OUT)

$(TARGET): $(OBJS)
	sdcc $(LDFLAGS) -o $(TARGET).ihx $(OBJS)
	hex2bin -p 00 $(TARGET).ihx

$(OBJ)/%.o: $(SRC)/%.c
	$(CC) $(CCFLAGS) -c $< -o $@

clean:
	$(RM) $(TARGET) $(OUT) $(OBJS) $(TARGET).ihx $(TARGET).bin
EOL
        fi
        
        # Create generated directory structure
        local gen_dir="examples/amstrad_cpc/generated"
        if ! mkdir -p "$gen_dir/src" "$gen_dir/obj"; then
            echo -e "${RED}❌ Error: Could not create directory structure${NC}"
            return 1
        fi
        
        # Copy Makefile template
        if ! cp "examples/amstrad_cpc/common/Makefile.template" "$gen_dir/Makefile"; then
            echo -e "${RED}❌ Error: Could not copy Makefile template${NC}"
            return 1
        fi
        
        # Create main.c with Hello World program
        if ! cat > "$gen_dir/src/main.c" << 'EOL'
#include <cpctelera.h>

void main(void) {
    // Initialize CPCtelera
    cpct_disableFirmware();
    cpct_setVideoMode(1);
    
    // Clear screen (black background)
    cpct_memset(CPCT_VMEM_START, 0x00, 0x4000);
    
    // Set text properties
    cpct_setDrawCharM1(3, 0);   // White text on black background
    
    // Print text at coordinates (10, 10)
    cpct_drawStringM1("Hello World!", CPCT_VMEM_START + 80*10 + 10);
    
    // Wait forever
    while(1) {
        cpct_waitVSYNC();
    }
}
EOL
        then
            echo -e "${RED}❌ Error: Could not create source file${NC}"
            return 1
        fi
        
        echo -e "${GREEN}✨ Program generated in $gen_dir/${NC}"
        
        # Compile and run directly
        select_emulator
        DSK_FILE=$(compile_example "generated")
        if [ $? -eq 0 ]; then
            run_emulator "$DSK_FILE" "$EMULATOR"
            exit 0
        else
            echo -e "${RED}❌ Compilation failed. Please check the error messages above.${NC}"
            exit 1
        fi
    fi
    exit 0
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
                    if [ $? -eq 0 ]; then
                        run_emulator "$DSK_FILE" "$EMULATOR"
                        exit 0
                    fi
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
            run_emulator "$DSK_FILE" "$EMULATOR"
            exit 0
        fi
    fi
fi 