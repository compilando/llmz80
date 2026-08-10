#!/bin/bash

# Colores para mensajes
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Emulador por defecto
DEFAULT_EMULATOR="fuse"

# Función para mostrar ayuda
show_help() {
    echo -e "${BLUE}🔧 ZX Spectrum Program Builder${NC}"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --example=NAME       Compiles and runs the specified example"
    echo "  --list-examples      Lists all available examples"
    echo "  --show-errors        Shows solutions to common errors"
    echo "  --no-emulator        Compiles but doesn't run the emulator"
    echo "  --emulator=EMULATOR  Specifies the emulator to use (fuse, zesarux, zxspin)"
    echo "  --clean              Removes all temporary files and folders in ./local"
    echo "  --help               Shows this help"
    echo ""
    echo "Examples:"
    echo "  $0 --example=hello_world"
    echo "  $0 --example=graphics/ball"
    echo "  $0 --list-examples"
    echo "  $0 --example=text_example --emulator=fuse"
    echo ""
}

# Función para listar ejemplos
list_examples() {
    echo -e "${BLUE}🔧 ZX Spectrum Program Builder${NC}"
    echo ""
    echo -e "${GREEN}Available examples:${NC}"
    echo ""
    
    echo -e "${BLUE}Examples:${NC}"
    # Buscar archivos .c recursivamente, quitar el prefijo y la extensión
    find examples/spectrum -type f -name "*.c" | sed 's|^examples/spectrum/||; s|\.c$||' | sort | while read -r example_path; do
        # Omitir archivos en un posible directorio 'common' si existe
        if [[ "$example_path" != "common" && "$example_path" != common/* ]]; then
             echo "  - $example_path"
        fi
    done
}

# Función para mostrar soluciones a errores comunes
show_errors() {
    if [ -f "examples/spectrum/error_solutions.md" ]; then
        cat "examples/spectrum/error_solutions.md"
    else
        echo -e "${RED}❌ Error: Error solutions file not found${NC}"
    fi
}

# Función para compilar un ejemplo
compile_example() {
    local example=$1
    local example_path="examples/spectrum"
    local example_file="${example_path}/${example}.c"
    local build_dir="build/spectrum/${example}"
    local tap_file=""
    
    # Redireccionar la salida estándar a un archivo temporal
    exec 3>&1
    exec 1>/tmp/build_spectrum_output.txt

    echo -e "${BLUE}🔧 ZX Spectrum Program Builder${NC}"
    echo ""
    echo -e "Compiling example: ${example_file}"
    
    # Verificar que el archivo del ejemplo existe
    if [ ! -f "$example_file" ]; then
        echo -e "${RED}❌ Error: Example file $example_file does not exist${NC}"
        echo "Use --list-examples to see available examples"
        
        # Restaurar la salida estándar
        exec 1>&3
        exit 1
    fi
    
    # Crear el directorio de construcción
    mkdir -p "$build_dir"
    
    # Copiar el archivo .c al directorio de construcción
    cp "$example_file" "$build_dir/main.c"
    
    # Crear un Makefile para el ejemplo
    cat > "$build_dir/Makefile" << EOL
CC=zcc
CFLAGS=+zx -vn -O3 -clib=sdcc_iy -I.
LDFLAGS=-create-app
SUBTYPE=-subtype=default

TARGET=program
SOURCES=main.c
OBJECTS=\$(SOURCES:.c=.o)

.PHONY: all clean

all: \$(TARGET)

\$(TARGET): \$(OBJECTS)
	\$(CC) \$(CFLAGS) \$(OBJECTS) -o \$@ \$(LDFLAGS) \$(SUBTYPE)

%.o: %.c
	\$(CC) \$(CFLAGS) -c \$< -o \$@

clean:
	rm -f \$(OBJECTS) \$(TARGET) \$(TARGET).tap
EOL
    
    # Compilar el ejemplo
    cd "$build_dir" && make
    
    # Verificar si la compilación fue exitosa
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Error: Compilation failed. Please check the error messages above.${NC}"
        cd - > /dev/null
        
        # Restaurar la salida estándar
        exec 1>&3
        exit 1
    fi
    
    # Volver al directorio original
    cd - > /dev/null
    
    # Obtener la ruta completa del archivo TAP
    tap_file=$(find "$build_dir" -name "*.tap" | head -1)
    
    if [ -z "$tap_file" ]; then
        echo -e "${RED}❌ Error: No TAP file found in $build_dir${NC}"
        
        # Restaurar la salida estándar
        exec 1>&3
        exit 1
    fi
    
    echo -e "Full TAP path: $tap_file"
    echo -e "${GREEN}✨ Example compiled successfully!${NC}"
    echo -e "TAP file generated: $tap_file"
    
    # Restaurar la salida estándar y mostrar el output
    exec 1>&3
    cat /tmp/build_spectrum_output.txt
    
    # Devolver la ruta del TAP como resultado de la función
    echo "$tap_file"
}

# Function to run the emulator
run_emulator() {
    local tap_file="$1"
    local emulator="$2"
    
    echo -e "${BLUE}🔧 Launching emulator: $emulator${NC}"
    echo -e "${BLUE}📂 TAP file: $tap_file${NC}"
    
    # Verificar que el archivo TAP existe
    if [ ! -f "$tap_file" ]; then
        echo -e "${RED}❌ Error: TAP file not found: $tap_file${NC}"
        return 1
    fi
    
    # Verificar que el archivo TAP tiene permisos de lectura
    if [ ! -r "$tap_file" ]; then
        echo -e "${RED}❌ Error: Cannot read TAP file: $tap_file${NC}"
        return 1
    fi
    
    case $emulator in
        "fuse")
            if command -v fuse &> /dev/null; then
                echo -e "${GREEN}✅ Found Fuse emulator${NC}"
                echo -e "${BLUE}🚀 Starting Fuse with auto-load...${NC}"
                echo -e "${BLUE}⚙️  Command: fuse --machine 48 --tape \"$tap_file\" --auto-load${NC}"
                
                # Ejecutar en primer plano y esperar a que termine
                fuse --machine 48 --tape "$tap_file" --auto-load
                
                # Verificar el código de retorno
                if [ $? -eq 0 ]; then
                    echo -e "${GREEN}✅ Fuse exited successfully${NC}"
                else
                    echo -e "${RED}❌ Fuse exited with error code: $?${NC}"
                fi
            else
                echo -e "${RED}❌ Error: Fuse not found${NC}"
                echo -e "${BLUE}💡 Please install Fuse:${NC}"
                echo -e "  sudo pacman -S fuse"
                return 1
            fi
            ;;
        "zesarux")
            if command -v zesarux &> /dev/null; then
                echo -e "${GREEN}✅ Found ZEsarUX emulator${NC}"
                echo -e "${BLUE}🚀 Starting ZEsarUX...${NC}"
                echo -e "${BLUE}⚙️  Command: zesarux --noconfigfile --machine 48k --realvideo --nosplash --tape \"$tap_file\"${NC}"
                
                # Ejecutar en primer plano y esperar a que termine
                zesarux --noconfigfile --machine 48k --realvideo --nosplash --tape "$tap_file"
                
                # Verificar el código de retorno
                if [ $? -eq 0 ]; then
                    echo -e "${GREEN}✅ ZEsarUX exited successfully${NC}"
                else
                    echo -e "${RED}❌ ZEsarUX exited with error code: $?${NC}"
                fi
            else
                echo -e "${RED}❌ Error: ZEsarUX not found${NC}"
                echo -e "${BLUE}💡 Please install ZEsarUX:${NC}"
                echo -e "  sudo pacman -S zesarux"
                return 1
            fi
            ;;
        "zxspin")
            if command -v zxspin &> /dev/null; then
                echo -e "${GREEN}✅ Found ZXSpin emulator${NC}"
                echo -e "${BLUE}🚀 Starting ZXSpin with auto-load...${NC}"
                echo -e "${BLUE}⚙️  Command: zxspin --tape \"$tap_file\" --auto-load${NC}"
                
                # Ejecutar en primer plano y esperar a que termine
                zxspin --tape "$tap_file" --auto-load
                
                # Verificar el código de retorno
                if [ $? -eq 0 ]; then
                    echo -e "${GREEN}✅ ZXSpin exited successfully${NC}"
                else
                    echo -e "${RED}❌ ZXSpin exited with error code: $?${NC}"
                fi
            else
                echo -e "${RED}❌ Error: ZXSpin not found${NC}"
                echo -e "${BLUE}💡 Please install ZXSpin:${NC}"
                echo -e "  sudo pacman -S zxspin"
                return 1
            fi
            ;;
        *)
            echo -e "${RED}❌ Error: Unsupported emulator: $emulator${NC}"
            echo -e "${BLUE}💡 Supported emulators:${NC}"
            echo -e "  - fuse"
            echo -e "  - zesarux"
            echo -e "  - zxspin"
            return 1
            ;;
    esac
}

# Function to display the main menu
display_menu() {
    clear
    echo "╔════════════════════════════════════════════════════════════════════════════╗"
    echo "║                                                                            ║"
    echo "║  AI (LLM) ZX Spectrum Program Builder                                      ║"
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
    echo -e "${BLUE}║${NC}                                                                            ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}  ${GREEN}Available Examples${NC}                                                        ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}                                                                            ${BLUE}║${NC}"
    echo -e "${BLUE}╠════════════════════════════════════════════════════════════════════════════╣${NC}"
    echo -e "${BLUE}║${NC}                                                                            ${BLUE}║${NC}"
    find examples/spectrum -maxdepth 1 -type f -name "*.c" | sort | sed 's|examples/spectrum/||' | nl | while read -r line; do
        echo -e "${BLUE}║${NC}  ${line}"
    done
    echo -e "${BLUE}║${NC}                                                                            ${BLUE}║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    read -p "Select example number: " example_num
    EXAMPLE=$(find examples/spectrum -maxdepth 1 -type f -name "*.c" | sort | sed 's|examples/spectrum/||' | sed -n "${example_num}p")
    EXAMPLE="${EXAMPLE%.c}"
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
    echo -e "${BLUE}║${NC}  ${GREEN}1)${NC} 🎮 Fuse (default)                                           ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}  ${GREEN}2)${NC} 🎲 ZEsarUX                                                  ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}  ${GREEN}3)${NC} 🎯 ZXSpin                                                   ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}                                                                                ${BLUE}║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    read -p "Select emulator number: " emulator_num
    case $emulator_num in
        1) EMULATOR="fuse" ;;
        2) EMULATOR="zesarux" ;;
        3) EMULATOR="zxspin" ;;
        *) EMULATOR=$DEFAULT_EMULATOR ;;
    esac
}

# Function to generate program with prompt
generate_with_prompt() {
    echo -e "${BLUE}🔧 ZX Spectrum Program Generator${NC}"
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
        python llm_z80.py --platform=spectrum --prompt="$prompt"
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
            
            # Create Makefile if needed
            if [ ! -f "Makefile" ]; then
                echo -e "${YELLOW}Creating Makefile...${NC}"
                cat > Makefile << 'EOL'
CC=zcc
CFLAGS=+zx -vn -O3 -clib=sdcc_iy
LDFLAGS=-create-app -subtype=default

all: program

program: main.c
	$(CC) $(CFLAGS) $< -o $@ $(LDFLAGS)

clean:
	rm -f program program.tap
EOL
            fi
            
            # Compile
            make
            compile_result=$?
            
            if [ $compile_result -ne 0 ]; then
                echo -e "${RED}❌ Compilation failed${NC}"
                cd "$original_dir"
                read -p "Press Enter to return to the main menu..." dummy
                return 1
            fi
            
            echo -e "${GREEN}✅ Compilation successful!${NC}"
            
            # Find the generated TAP file (absolute path)
            tap_file="$PWD/$(find . -name "*.tap" | head -1)"
            
            if [ ! -f "$tap_file" ]; then
                echo -e "${RED}❌ No TAP file found after compilation${NC}"
                cd "$original_dir"
                read -p "Press Enter to return to the main menu..." dummy
                return 1
            fi
            
            echo -e "${GREEN}📋 TAP file created: $tap_file${NC}"
            
            # Return to original directory
            cd "$original_dir"
            
            # IMPORTANTE: Ejecutar el emulador directamente, no usar la función run_emulator
            # ya que esta puede estar usando valores globales incorrectos
            echo -e "${BLUE}🚀 Running the program with emulator...${NC}"
            echo -e "${BLUE}📂 Using TAP file: $tap_file${NC}"
            
            if command -v fuse >/dev/null 2>&1; then
                echo -e "${GREEN}✅ Starting Fuse emulator${NC}"
                fuse --machine 48 --tape "$tap_file" --auto-load
            elif command -v zesarux >/dev/null 2>&1; then
                echo -e "${GREEN}✅ Starting ZEsarUX emulator${NC}"
                zesarux --noconfigfile --machine 48k --realvideo --nosplash --tape "$tap_file"
            else
                echo -e "${RED}❌ No emulator found. Please install Fuse or ZEsarUX.${NC}"
                read -p "Press Enter to return to the main menu..." dummy
                return 1
            fi
        else
            echo -e "${RED}❌ No main.c file found in $generated_dir${NC}"
            read -p "Press Enter to return to the main menu..." dummy
            return 1
        fi
    fi
    return 0
}

# Function to populate vector database
# Placeholder function - Will call the python script later
populate_vector_db() {
    echo "📊 Populating Vector DB for ZX Spectrum examples..."
    # Corrected Python script name
    if python llm_z80.py --populate-db --platform spectrum; then
        echo "✅ Vector DB population process finished."
    else
        echo "❌ Error during Vector DB population."
    fi
    read -p "Press Enter to return to the main menu..."
}

# --- Nueva función para limpiar ./local ---
clean_local_directory() {
    echo -e "${BLUE}🧹 Cleaning temporary files...${NC}"
    if [ -d "./local" ]; then
        echo "   Removing contents of ./local/" 
        # Usar find para más seguridad que rm -rf *, y manejar si local está vacío
        find ./local -mindepth 1 -delete
        local exit_code=$?
        if [ $exit_code -eq 0 ]; then
            echo -e "${GREEN}✅ Temporary files in ./local cleaned successfully.${NC}"
        else
            echo -e "${RED}❌ Error cleaning temporary files in ./local (Code: $exit_code).${NC}"
            # Devolver el código de error para que el menú sepa si falló
            return $exit_code
        fi
    else
        echo -e "${BLUE}ℹ️ Directory ./local not found, nothing to clean.${NC}"
    fi
    return 0
}

# Parse command-line arguments
EXAMPLE_NAME=""
LIST_EXAMPLES=false
SHOW_ERRORS=false
RUN_EMULATOR=true
EMULATOR=$DEFAULT_EMULATOR
CLEAN_LOCAL=false

while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --example=*) EXAMPLE_NAME="${key#*=}"; shift ;; 
        --list-examples) LIST_EXAMPLES=true; shift ;; 
        --show-errors) SHOW_ERRORS=true; shift ;; 
        --no-emulator) RUN_EMULATOR=false; shift ;; 
        --emulator=*) EMULATOR="${key#*=}"; shift ;; 
        --clean) CLEAN_LOCAL=true; shift ;;
        --help) show_help; exit 0 ;; 
        *) echo -e "${RED}❌ Error: Unknown option: $key${NC}"; show_help; exit 1 ;; 
    esac
done

# --- Execute Clean Action (si se usó --clean) --- 
if [ "$CLEAN_LOCAL" = true ]; then
    clean_local_directory # Llamar a la función
    clean_exit_code=$?
    # Salir si la única acción era limpiar (independientemente del éxito? O solo si éxito?)
    # Por ahora, salimos si la única acción era limpiar.
    if [ -z "$EXAMPLE_NAME" ] && [ "$LIST_EXAMPLES" = false ] && [ "$SHOW_ERRORS" = false ]; then
        exit $clean_exit_code
    fi
fi

# --- Determine Action --- 
# Si se pasó un argumento de acción específico, no mostrar menú
ACTION_REQUESTED=false
if [ -n "$EXAMPLE_NAME" ] || [ "$LIST_EXAMPLES" = true ] || [ "$SHOW_ERRORS" = true ]; then
    ACTION_REQUESTED=true
fi

# --- Execute Actions OR Show Menu --- 
if [ "$ACTION_REQUESTED" = true ]; then
    # Ejecutar acciones basadas en flags
    if [ "$LIST_EXAMPLES" = true ]; then
        list_examples
    elif [ "$SHOW_ERRORS" = true ]; then
        show_errors
    elif [ -n "$EXAMPLE_NAME" ]; then
        # Compilar el ejemplo
        tap_file_result=$(compile_example "$EXAMPLE_NAME")
        compile_exit_code=$?
        
        # Extraer solo la ruta del TAP (última línea)
        tap_file=$(echo "$tap_file_result" | tail -n 1)

        # Ejecutar emulador si la compilación fue exitosa y no se indicó lo contrario
        if [ $compile_exit_code -eq 0 ] && [ "$RUN_EMULATOR" = true ]; then
            if [ -f "$tap_file" ]; then
                run_emulator "$tap_file" "$EMULATOR"
            else
                # El error ya debería haberse mostrado en compile_example o run_emulator
                # pero añadimos un log extra por si acaso.
                echo -e "${RED}❌ Error: TAP file '$tap_file' not found after successful compilation report?${NC}"
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
            1) generate_with_prompt ;; # Asegúrate que esta función existe y es correcta
            2) 
                list_examples 
                read -p "Press Enter to continue..." # Pausa para ver la lista
                ;; 
            3) 
                select_example # Pregunta interactivamente
                if [ -n "$EXAMPLE" ]; then # EXAMPLE es la variable que setea select_example
                    select_emulator # Pregunta interactivamente
                    tap_file_result=$(compile_example "$EXAMPLE")
                    compile_exit_code=$?
                    tap_file=$(echo "$tap_file_result" | tail -n 1)
                    if [ $compile_exit_code -eq 0 ]; then
                         run_emulator "$tap_file" "$EMULATOR"
                    else
                         read -p "Compilation failed. Press Enter to continue..."
                    fi
                fi
                ;; 
            4) 
                # Llamar a la función para generar sprites (si existe)
                # generate_sprites_prompt 
                echo "Sprite generation not implemented in this menu yet."
                read -p "Press Enter to continue..." 
                ;; 
            5) populate_vector_db ;; # Asegúrate que esta función existe
            6) # Nueva opción para limpiar
                clean_local_directory
                read -p "Press Enter to continue..." # Pausa para ver el mensaje
                ;;
            7) echo "👋 Exiting..."; exit 0 ;; # Ahora la opción de salir es la 7
            *) echo "❌ Invalid option. Please try again."; sleep 2 ;; 
        esac
    done
fi
