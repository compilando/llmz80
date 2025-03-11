#!/bin/bash

# Colors and styling
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m'
BOLD='\033[1m'

# Check and activate virtual environment
VENV_PATH=".venv"
if [ ! -d "$VENV_PATH" ]; then
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo "Please run install_arch.sh first"
    exit 1
fi

# Activate virtual environment
source "$VENV_PATH/bin/activate" || {
    echo -e "${RED}❌ Failed to activate virtual environment!${NC}"
    exit 1
}

# Simple progress bar function
progress_bar() {
    local progress=$1
    local total=30
    local filled=$(($progress * total / 100))
    local empty=$((total - filled))
    
    printf "\r["
    printf "%${filled}s" | tr ' ' '█'
    printf "%${empty}s" | tr ' ' '.'
    printf "] %d%%" $progress
}

# Error handling
handle_error() {
    echo -e "\n${RED}❌ Error: $1${NC}"
    if [ -f "/tmp/build_error" ]; then
        echo -e "\n${RED}Error details:${NC}"
        cat /tmp/build_error
    fi
    exit 1
}

# Función para mostrar soluciones a errores comunes
show_error_solutions() {
    local error_doc="examples/amstrad_cpc/error_solutions.md"
    
    if [ -f "$error_doc" ]; then
        echo -e "${BLUE}${BOLD}📚 Soluciones a Errores Comunes en el Desarrollo para Amstrad CPC${NC}\n"
        
        # Si tenemos bat o mdcat, usarlos para mostrar el markdown con formato
        if command -v bat &> /dev/null; then
            bat --style=plain --paging=never "$error_doc"
        elif command -v mdcat &> /dev/null; then
            mdcat "$error_doc"
        else
            # Si no tenemos herramientas de formato, mostrar el contenido plano
            cat "$error_doc"
        fi
        
        echo -e "\n${BLUE}${BOLD}📝 Ejemplo de código con soluciones:${NC} examples/amstrad_cpc/error_solutions.c"
        echo -e "${YELLOW}Puedes compilar este ejemplo con:${NC} ./build_amstrad.sh --example=error_solutions"
    else
        echo -e "${RED}❌ Documentación de errores no encontrada: ${error_doc}${NC}"
        echo -e "${YELLOW}Creando archivo de documentación básico...${NC}"
        
        # Crear directorio si no existe
        mkdir -p "examples/amstrad_cpc"
        
        # Crear archivo de documentación básico
        cat > "$error_doc" << EOF
# Soluciones a Errores Comunes en el Desarrollo para Amstrad CPC

## Errores de Sintaxis

### Error: \`syntax error: token -> 'u8'\`

**Problema**: El compilador no reconoce el tipo de dato \`u8\`.

**Solución**: 
- Asegúrate de incluir \`<cpctelera.h>\` al principio de tu archivo.
- Este header define los tipos \`u8\`, \`u16\`, \`u32\`, etc.

### Error: \`syntax error: token -> '0x0400'\`

**Problema**: SDCC puede tener problemas con algunas constantes hexadecimales.

**Solución**:
- Usa paréntesis alrededor de las expresiones con constantes hexadecimales.
- Define constantes con nombres significativos.

## Errores de Variables

### Error: \`Undefined identifier 'palette'\`

**Problema**: Estás usando una variable que no ha sido definida.

**Solución**:
- Define todas las variables antes de usarlas.
- Para paletas, usa arrays de tamaño fijo.

## Errores de Tipos

### Error: \`converting integral to pointer without a cast\`

**Problema**: Estás intentando usar un número como si fuera un puntero sin hacer un casting explícito.

**Solución**:
- Usa casting explícito cuando conviertas entre tipos, especialmente con punteros.
EOF
        
        echo -e "${GREEN}✓ Archivo de documentación básico creado: ${error_doc}${NC}"
        
        # Mostrar el contenido recién creado
        if command -v bat &> /dev/null; then
            bat --style=plain --paging=never "$error_doc"
        elif command -v mdcat &> /dev/null; then
            mdcat "$error_doc"
        else
            cat "$error_doc"
        fi
    fi
}

# Función para compilar un ejemplo de CPCtelera
compile_example() {
    local example_path="$1"
    
    # Si el ejemplo no tiene un directorio propio, pero existe un archivo .c con ese nombre
    if [ ! -d "examples/amstrad_cpc/${example_path}" ] && [ -f "examples/amstrad_cpc/${example_path}.c" ]; then
        echo -e "${YELLOW}El ejemplo no tiene un directorio propio, pero existe un archivo .c${NC}"
        echo -e "${BLUE}Creando directorio para el ejemplo...${NC}"
        
        # Crear directorio para el ejemplo
        mkdir -p "examples/amstrad_cpc/${example_path}"
        
        # Copiar el archivo .c al directorio
        cp "examples/amstrad_cpc/${example_path}.c" "examples/amstrad_cpc/${example_path}/"
        
        # Crear un Makefile básico
        cat > "examples/amstrad_cpc/${example_path}/Makefile" << EOF
##-----------------------------LICENSE NOTICE------------------------------------
##  This file is part of CPCtelera: An Amstrad CPC Game Engine 
##  Copyright (C) 2018 ronaldo / Fremos / Cheesetea / ByteRealms (@FranGallegoBR)
##
##  This program is free software: you can redistribute it and/or modify
##  it under the terms of the GNU Lesser General Public License as published by
##  the Free Software Foundation, either version 3 of the License, or
##  (at your option) any later version.
##
##  This program is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##  GNU Lesser General Public License for more details.
##
##  You should have received a copy of the GNU Lesser General Public License
##  along with this program.  If not, see <http://www.gnu.org/licenses/>.
##------------------------------------------------------------------------------
##
## PROJECT CONFIGURATION
##

# Name of the project (without spaces, as it will be used as filename)
PROJNAME   := ${example_path}

# Source files (.c, .s)
SRCFILES   := ${example_path}.c

# Location of the source files
SRCDIR     := .

# Output directory for compiled binaries and assets
OBJDIR     := obj

# Compilation platform (linux, macos, win)
PLATFORM   := linux

# Compiler flags
Z80CCFLAGS := -mz80 --opt-code-size --std-c99

# Linker flags
Z80LDFLAGS := -mz80 --no-std-crt0 --code-loc 0x4000

# Executable file extension
EXTEXT     := bin

# Binary file extension
BINEXT     := bin

# Disk file extension
DSKEXT     := dsk

# Commands
MKDIR      := mkdir -p
RM         := rm -f
CP         := cp
ECHO       := echo

# Find CPCtelera directory
CPCT_PATH  := \$(shell if [ -d "/home/oscar/cpctelera/cpctelera" ]; then echo "/home/oscar/cpctelera/cpctelera"; elif [ -d "\$(CPCT_PATH)" ]; then echo "\$(CPCT_PATH)"; else echo "CPCT_PATH not found"; fi)

# Memory location for Z80 code
Z80CODELOC := 0x4000

# Target binary file
TARGET     := \$(PROJNAME).\$(BINEXT)

# Target disk file
TARGETDSK  := \$(PROJNAME).\$(DSKEXT)

# Compilation flags
CCFLAGS    := \$(Z80CCFLAGS) -I\$(CPCT_PATH)/src
LDFLAGS    := \$(Z80LDFLAGS) -L\$(CPCT_PATH)/cpctelera.lib

# Object files
OBJFILES   := \$(patsubst %.c,\$(OBJDIR)/%.rel,\$(notdir \$(SRCFILES)))

# Default target
.PHONY: all clean

all: \$(TARGETDSK)

# Create required directories
\$(OBJDIR):
	\$(MKDIR) \$(OBJDIR)

# Compile .c files
\$(OBJDIR)/%.rel: \$(SRCDIR)/%.c | \$(OBJDIR)
	\$(CPCT_PATH)/tools/sdcc-3.6.8-r9946/bin/sdcc \$(CCFLAGS) -c \$< -o \$@

# Link object files into a binary
\$(TARGET): \$(OBJFILES)
	\$(CPCT_PATH)/tools/sdcc-3.6.8-r9946/bin/sdcc \$(LDFLAGS) \$(OBJFILES) -o \$(TARGET)

# Create a DSK file
\$(TARGETDSK): \$(TARGET)
	\$(CPCT_PATH)/tools/iDSK-0.13/bin/iDSK \$(TARGETDSK) -n
	\$(CPCT_PATH)/tools/iDSK-0.13/bin/iDSK \$(TARGETDSK) -i \$(TARGET) -t 1 -e 0x4000 -c 0x4000 -o 0

# Clean up generated files
clean:
	\$(RM) -r \$(OBJDIR)
	\$(RM) \$(TARGET)
	\$(RM) \$(TARGETDSK)
EOF
        
        echo -e "${GREEN}✓ Makefile creado para el ejemplo: examples/amstrad_cpc/${example_path}/Makefile${NC}"
        
        # Actualizar la ruta del ejemplo
        example_path="examples/amstrad_cpc/${example_path}"
    else
        # Si se proporciona una ruta relativa, añadir el prefijo
        if [[ ! "$example_path" == examples/* ]]; then
            example_path="examples/amstrad_cpc/${example_path}"
        fi
    fi
    
    if [ ! -d "$example_path" ]; then
        handle_error "El directorio del ejemplo no existe: ${example_path}"
    fi
    
    # Verificar si el ejemplo tiene un Makefile
    if [ ! -f "${example_path}/Makefile" ]; then
        handle_error "El ejemplo no tiene un Makefile: ${example_path}"
    fi
    
    echo -e "${BLUE}Compilando ejemplo: ${example_path}${NC}"
    
    # Cambiar al directorio del ejemplo
    cd "${example_path}" || handle_error "No se pudo cambiar al directorio del ejemplo"
    
    # Ejecutar make para compilar
    echo -e "${BLUE}Ejecutando make...${NC}"
    make clean > /dev/null 2>&1
    make || handle_error "Compilation failed"
    
    # Verificar que se generó el archivo DSK
    local dsk_file=$(find . -name "*.dsk" | head -1)
    if [ -z "$dsk_file" ]; then
        echo -e "${RED}❌ DSK file not generated!${NC}"
        echo -e "${YELLOW}Contenido del directorio:${NC}"
        ls -la
        handle_error "DSK file not generated"
    fi
    
    # Obtener la ruta completa del DSK
    DSK_FULL_PATH="$(realpath "$dsk_file")"
    echo -e "${BLUE}Ruta completa del DSK: ${DSK_FULL_PATH}${NC}"
    
    # Volver al directorio original
    cd - > /dev/null
    
    echo -e "${GREEN}${BOLD}✨ Ejemplo compilado correctamente!${NC}"
    echo -e "${BLUE}Archivo DSK generado: ${DSK_FULL_PATH}${NC}"
    
    return 0
}

# Función para listar ejemplos disponibles
list_examples() {
    echo -e "${BLUE}${BOLD}Ejemplos disponibles:${NC}"
    
    # Buscar ejemplos en el directorio examples/amstrad_cpc
    if [ -d "examples/amstrad_cpc" ]; then
        echo -e "${YELLOW}Ejemplos básicos:${NC}"
        
        # Listar directorios de ejemplos
        find "examples/amstrad_cpc" -maxdepth 1 -type d -not -path "examples/amstrad_cpc" -not -path "examples/amstrad_cpc/easy" | sort | while read -r dir; do
            echo -e "  - ${BLUE}$(basename "$dir")${NC}"
        done
        
        # Listar archivos .c que podrían ser ejemplos
        find "examples/amstrad_cpc" -maxdepth 1 -name "*.c" | sort | while read -r file; do
            filename=$(basename "$file" .c)
            # Evitar duplicados (si ya existe un directorio con el mismo nombre)
            if [ ! -d "examples/amstrad_cpc/$filename" ]; then
                echo -e "  - ${BLUE}${filename}${NC} (archivo único)"
            fi
        done
        
        # Buscar ejemplos en el directorio examples/amstrad_cpc/easy
        if [ -d "examples/amstrad_cpc/easy" ]; then
            echo -e "${YELLOW}Ejemplos de CPCtelera (easy):${NC}"
            find "examples/amstrad_cpc/easy" -maxdepth 1 -type d -not -path "examples/amstrad_cpc/easy" | sort | while read -r dir; do
                echo -e "  - ${BLUE}easy/$(basename "$dir")${NC}"
            done
            
            # Listar archivos .c en el directorio easy
            find "examples/amstrad_cpc/easy" -maxdepth 1 -name "*.c" | sort | while read -r file; do
                filename=$(basename "$file" .c)
                echo -e "  - ${BLUE}easy/${filename}${NC} (archivo único)"
            done
        fi
    else
        echo -e "${RED}No se encontraron ejemplos para Amstrad CPC${NC}"
    fi
}

# Parse arguments
LAUNCH_EMULATOR=1
GENERATOR_MODE=1
EMULATOR="retrovirtualmachine"  # Por defecto usamos RetroVirtualMachine
CPCTELERA_PATH=""
EXAMPLE_MODE=0
EXAMPLE_PATH=""
LIST_EXAMPLES=0
SHOW_ERRORS=0

while [[ $# -gt 0 ]]; do
    case $1 in
        --no-emulator)
            LAUNCH_EMULATOR=0
            shift
            ;;
        --source=*)
            source_file="${1#*=}"
            GENERATOR_MODE=0
            shift
            ;;
        --emulator=*)
            EMULATOR="${1#*=}"
            if [[ "$EMULATOR" != "retrovirtualmachine" ]]; then
                handle_error "Invalid emulator. Use 'retrovirtualmachine'"
            fi
            shift
            ;;
        --cpctelera=*)
            CPCTELERA_PATH="${1#*=}"
            shift
            ;;
        --example=*)
            EXAMPLE_MODE=1
            EXAMPLE_PATH="${1#*=}"
            shift
            ;;
        --list-examples)
            LIST_EXAMPLES=1
            shift
            ;;
        --show-errors)
            SHOW_ERRORS=1
            shift
            ;;
        --help)
            echo -e "${BLUE}${BOLD}Uso:${NC}"
            echo -e "  ${YELLOW}./build_amstrad.sh${NC} - Genera y compila código usando el LLM"
            echo -e "  ${YELLOW}./build_amstrad.sh --source=ruta/al/archivo.c${NC} - Compila un archivo fuente específico"
            echo -e "  ${YELLOW}./build_amstrad.sh --example=ruta/al/ejemplo${NC} - Compila un ejemplo específico"
            echo -e "  ${YELLOW}./build_amstrad.sh --list-examples${NC} - Lista los ejemplos disponibles"
            echo -e "  ${YELLOW}./build_amstrad.sh --show-errors${NC} - Muestra soluciones a errores comunes"
            echo -e "  ${YELLOW}./build_amstrad.sh --no-emulator${NC} - No ejecuta el emulador después de compilar"
            echo -e "  ${YELLOW}./build_amstrad.sh --cpctelera=/ruta/a/cpctelera${NC} - Especifica la ruta a CPCtelera"
            echo -e "  ${YELLOW}./build_amstrad.sh --help${NC} - Muestra esta ayuda"
            exit 0
            ;;
        *)
            handle_error "Unknown option: $1"
            ;;
    esac
done

echo -e "${BLUE}${BOLD}🔧 Amstrad CPC Program Builder${NC}\n"

# Si se solicita mostrar soluciones a errores, mostrarlas y salir
if [ $SHOW_ERRORS -eq 1 ]; then
    show_error_solutions
    exit 0
fi

# Si se solicita listar ejemplos, mostrarlos y salir
if [ $LIST_EXAMPLES -eq 1 ]; then
    list_examples
    exit 0
fi

# Si se solicita compilar un ejemplo, hacerlo y salir
if [ $EXAMPLE_MODE -eq 1 ]; then
    compile_example "$EXAMPLE_PATH"
    
    # Si se solicita lanzar el emulador, hacerlo
    if [ $LAUNCH_EMULATOR -eq 1 ] && [ -n "$DSK_FULL_PATH" ]; then
        echo -e "${BLUE}Lanzando emulador...${NC}"
        
        case $EMULATOR in
            retrovirtualmachine)
                echo -e "${YELLOW}Ejecutando RetroVirtualMachine...${NC}"
                retrovirtualmachine "$DSK_FULL_PATH" &
                ;;
            *)
                handle_error "Invalid emulator. Use 'retrovirtualmachine'"
                ;;
        esac
    fi
    
    exit 0
fi

# Handle source code
if [ $GENERATOR_MODE -eq 1 ]; then
    # Run Python generator if no source specified
    echo -e "${BLUE}Executing AI code generator...${NC}"
    python llm_z80.py --platform amstrad_cpc || handle_error "Python generator failed"
    echo -e "\n"

    # Find the most recent .c file (generated by Python)
    latest_dir=$(ls -td local/*/ | head -1)
    if [ -z "$latest_dir" ]; then
        handle_error "No source code generated. Generator failed."
    fi

    # Eliminar la barra diagonal final si existe
    latest_dir=${latest_dir%/}
    
    source_file="${latest_dir}/main.c"
    build_dir="${latest_dir}/build"
else
    # Use provided source file
    if [ ! -f "$source_file" ]; then
        handle_error "Source file not found: ${source_file}"
    fi
    build_dir="build/$(basename $(dirname $source_file))/$(basename $source_file .c)"
fi

# Create output directory
mkdir -p "${build_dir}"

# Compilation steps with progress
echo -e "${BLUE}Compiling C to Z80 assembly for Amstrad CPC...${NC}"
echo -e "${BLUE}Using source: ${source_file}${NC}"

# Verificar que el directorio build existe
if [ ! -d "${build_dir}" ]; then
    echo -e "${BLUE}Creando directorio de compilación: ${build_dir}${NC}"
    mkdir -p "${build_dir}"
fi

# Verificar que podemos escribir en el directorio
if [ ! -w "${build_dir}" ]; then
    echo -e "${RED}❌ No se puede escribir en el directorio de compilación: ${build_dir}${NC}"
    echo -e "${YELLOW}Verificando permisos...${NC}"
    ls -la "$(dirname "${build_dir}")"
    handle_error "No se puede escribir en el directorio de compilación"
fi

# Check if CPCtelera is installed
if [ -z "$CPCTELERA_PATH" ]; then
    # Try common locations
    for path in "$HOME/cpctelera" "/opt/cpctelera" "/usr/local/cpctelera" "/usr/share/cpctelera"; do
        if [ -d "$path" ]; then
            CPCTELERA_PATH="$path"
            echo -e "${BLUE}Found CPCtelera at: ${CPCTELERA_PATH}${NC}"
            break
        fi
    done
fi

# Verificar si CPCtelera existe y tiene la estructura correcta
if [ -z "$CPCTELERA_PATH" ] || [ ! -d "$CPCTELERA_PATH" ]; then
    echo -e "${RED}❌ CPCtelera not found!${NC}"
    echo -e "${YELLOW}Por favor, instala CPCtelera siguiendo estos pasos:${NC}"
    echo -e "${YELLOW}1. Clona el repositorio:${NC}"
    echo -e "   git clone https://github.com/lronaldo/cpctelera"
    echo -e "${YELLOW}2. Entra al directorio:${NC}"
    echo -e "   cd cpctelera"
    echo -e "${YELLOW}3. Ejecuta el script de instalación:${NC}"
    echo -e "   ./setup.sh"
    echo -e "${YELLOW}4. Vuelve a ejecutar este script con la ruta a CPCtelera:${NC}"
    echo -e "   ./build_amstrad.sh --cpctelera=/ruta/a/cpctelera"
    exit 1
fi

# Verificar la estructura específica de CPCtelera
if [ -d "$CPCTELERA_PATH/cpctelera" ]; then
    echo -e "${BLUE}Detected nested CPCtelera structure${NC}"
    CPCT_PATH="$CPCTELERA_PATH/cpctelera"
else
    CPCT_PATH="$CPCTELERA_PATH"
fi

# Verificar que los directorios necesarios existen
if [ ! -d "$CPCT_PATH/cfg" ]; then
    echo -e "${RED}❌ CPCtelera cfg directory not found!${NC}"
    echo -e "${YELLOW}La instalación de CPCtelera parece incompleta o incorrecta.${NC}"
    echo -e "${YELLOW}Por favor, reinstala CPCtelera siguiendo las instrucciones anteriores.${NC}"
    exit 1
fi

# Verificar si tenemos las herramientas necesarias
if ! command -v sdcc &> /dev/null; then
    echo -e "${RED}❌ SDCC (Small Device C Compiler) no encontrado!${NC}"
    echo -e "${YELLOW}Por favor, instala SDCC:${NC}"
    echo -e "${YELLOW}En Arch Linux: sudo pacman -S sdcc${NC}"
    echo -e "${YELLOW}En Ubuntu/Debian: sudo apt-get install sdcc${NC}"
    exit 1
fi

# Verificar si hex2bin está instalado
HEX2BIN_AVAILABLE=1
if ! command -v hex2bin &> /dev/null; then
    echo -e "${YELLOW}⚠️ hex2bin no encontrado. Intentando usar una alternativa...${NC}"
    HEX2BIN_AVAILABLE=0
    
    # Buscar hex2bin en CPCtelera
    if [ -f "$CPCT_PATH/tools/hex2bin" ] || [ -f "$CPCTELERA_PATH/tools/hex2bin" ]; then
        echo -e "${BLUE}Encontrado hex2bin en CPCtelera${NC}"
        if [ -f "$CPCT_PATH/tools/hex2bin" ]; then
            HEX2BIN="$CPCT_PATH/tools/hex2bin"
        else
            HEX2BIN="$CPCTELERA_PATH/tools/hex2bin"
        fi
        chmod +x "$HEX2BIN"
    else
        echo -e "${YELLOW}⚠️ No se encontró hex2bin. Usando la implementación básica...${NC}"
        # Copiar el script de conversión de ihx a bin desde la plantilla
        HEX2BIN="${build_dir}/hex2bin.py"
        cp "templates/amstrad/hex2bin.py" "$HEX2BIN"
        chmod +x "$HEX2BIN"
    fi
fi

# Crear un proyecto CPCtelera en el directorio de compilación
echo -e "${BLUE}Creando proyecto CPCtelera en ${build_dir}...${NC}"

# Crear estructura de directorios del proyecto
mkdir -p "${build_dir}/src"
mkdir -p "${build_dir}/cfg"
mkdir -p "${build_dir}/obj"
mkdir -p "${build_dir}/dsk"

# Copiar el archivo fuente al directorio src del proyecto
cp "$source_file" "${build_dir}/src/main.c"

# Copiar el archivo Makefile desde la plantilla
cp "templates/amstrad/Makefile" "${build_dir}/Makefile"

# Copiar el archivo de configuración build_config.mk desde la plantilla y reemplazar la ruta de CPCtelera
sed "s|{{CPCT_PATH}}|$CPCT_PATH|g" "templates/amstrad/cfg/build_config.mk" > "${build_dir}/cfg/build_config.mk"

# Copiar los archivos de configuración vacíos
cp "templates/amstrad/cfg/cdt_manager.mk" "${build_dir}/cfg/cdt_manager.mk"
cp "templates/amstrad/cfg/compression.mk" "${build_dir}/cfg/compression.mk"
cp "templates/amstrad/cfg/image_conversion.mk" "${build_dir}/cfg/image_conversion.mk"
cp "templates/amstrad/cfg/music_conversion.mk" "${build_dir}/cfg/music_conversion.mk"
cp "templates/amstrad/cfg/tilemap_conversion.mk" "${build_dir}/cfg/tilemap_conversion.mk"

# Compilar el proyecto
echo -e "${BLUE}Compilando el proyecto...${NC}"
cd "${build_dir}" || handle_error "Failed to change to project directory"

# Ejecutar make para compilar
echo -e "${BLUE}Ejecutando make...${NC}"
make clean > /dev/null 2>&1
make || handle_error "Compilation failed"

# Verificar que se generó el archivo DSK
if [ ! -f "program.dsk" ]; then
    echo -e "${RED}❌ DSK file not generated!${NC}"
    echo -e "${YELLOW}Contenido del directorio:${NC}"
    ls -la
    handle_error "DSK file not generated"
fi

# Inicializar DSK_FULL_PATH con la ruta completa
DSK_FULL_PATH="$(realpath "program.dsk")"
echo -e "${BLUE}Ruta completa del DSK: ${DSK_FULL_PATH}${NC}"

# Return to the original directory
cd - > /dev/null

progress_bar 100
echo -e "\n"

# Launch message
echo -e "${GREEN}${BOLD}✨ Build successful!${NC}"
echo -e "${BLUE}Generated files in: ${build_dir}${NC}"

# Función para lanzar el emulador
launch_emulator() {
    # Definir rutas posibles para RetroVirtualMachine
    RVM_PATHS=("/usr/bin/RetroVirtualMachine" "/usr/local/bin/RetroVirtualMachine" "retrovirtualmachine" "/opt/RetroVirtualMachine/RetroVirtualMachine")
    RVM_FOUND=0
    RVM_PATH=""
    
    # Buscar RetroVirtualMachine en las rutas posibles
    for path in "${RVM_PATHS[@]}"; do
        if [ -x "$path" ]; then
            RVM_PATH="$path"
            RVM_FOUND=1
            echo -e "${BLUE}RetroVirtualMachine encontrado en: ${RVM_PATH}${NC}"
            break
        elif command -v "$path" &> /dev/null; then
            RVM_PATH="$path"
            RVM_FOUND=1
            echo -e "${BLUE}RetroVirtualMachine encontrado como: ${RVM_PATH}${NC}"
            break
        fi
    done
    
    # Verificar si se encontró RetroVirtualMachine
    if [ $RVM_FOUND -eq 0 ]; then
        echo -e "${YELLOW}⚠️ RetroVirtualMachine no está instalado o no está en el PATH.${NC}"
        echo -e "${YELLOW}Por favor, instala RetroVirtualMachine desde:${NC}"
        echo -e "${BLUE}https://www.retrovirtualmachine.org/en/download${NC}"
        echo -e "${YELLOW}O instálalo desde AUR si estás en Arch Linux:${NC}"
        echo -e "${BLUE}yay -S retrovirtualmachine${NC}"
        echo -e "\n${BLUE}El archivo DSK se ha generado en: ${DSK_FULL_PATH}${NC}"
        echo -e "${YELLOW}Puedes abrirlo manualmente con cualquier emulador de Amstrad CPC.${NC}"
        return 1
    fi

    echo -e "${BLUE}🎮 Launching ${EMULATOR}...${NC}"
    echo -e "Loading disk..."
    for i in {1..20}; do
        echo -ne "${BLUE}█${NC}"
        sleep 0.1
    done
    echo -e "\n"

    # Intentar diferentes métodos para iniciar RetroVirtualMachine
    echo -e "${BLUE}Ejecutando RetroVirtualMachine...${NC}"
    
    # Método 1: Usar el comando directamente con la ruta completa
    echo -e "${BLUE}Método 1: Usando comando directo con ruta completa${NC}"
    echo -e "${BLUE}Comando: ${RVM_PATH} ${DSK_FULL_PATH}${NC}"
    
    if "$RVM_PATH" "$DSK_FULL_PATH"; then
        echo -e "${GREEN}✓ RetroVirtualMachine iniciado correctamente${NC}"
        return 0
    else
        # Método 2: Usar el comando con parámetros específicos
        echo -e "${YELLOW}⚠️ Error al iniciar RetroVirtualMachine con ruta directa.${NC}"
        echo -e "${YELLOW}Método 2: Usando parámetros específicos${NC}"
        echo -e "${BLUE}Comando: ${RVM_PATH} --machine=cpc464 --disk=A:${DSK_FULL_PATH}${NC}"
        
        if "$RVM_PATH" --machine=cpc464 --disk=A:"$DSK_FULL_PATH"; then
            echo -e "${GREEN}✓ RetroVirtualMachine iniciado correctamente${NC}"
            return 0
        else
            # Método 3: Usar el comando sin comillas
            echo -e "${YELLOW}⚠️ Error al iniciar RetroVirtualMachine con parámetros específicos.${NC}"
            echo -e "${YELLOW}Método 3: Usando parámetros sin comillas${NC}"
            echo -e "${BLUE}Comando: ${RVM_PATH} --machine=cpc464 --disk=A:${DSK_FULL_PATH}${NC}"
            
            if "$RVM_PATH" --machine=cpc464 --disk=A:$DSK_FULL_PATH; then
                echo -e "${GREEN}✓ RetroVirtualMachine iniciado correctamente${NC}"
                return 0
            else
                # Método 4: Usar el comando con ruta relativa
                echo -e "${YELLOW}⚠️ Error al iniciar RetroVirtualMachine sin comillas.${NC}"
                echo -e "${YELLOW}Método 4: Usando ruta relativa${NC}"
                
                # Obtener ruta relativa
                cd "$(dirname "$RVM_PATH")" || handle_error "Failed to change to RetroVirtualMachine directory"
                REL_PATH=$(realpath --relative-to="$(pwd)" "$DSK_FULL_PATH")
                echo -e "${BLUE}Comando: ./$(basename "$RVM_PATH") --machine=cpc464 --disk=A:${REL_PATH}${NC}"
                
                if "./$(basename "$RVM_PATH")" --machine=cpc464 --disk=A:"$REL_PATH"; then
                    echo -e "${GREEN}✓ RetroVirtualMachine iniciado correctamente${NC}"
                    cd - > /dev/null || handle_error "Failed to return to original directory"
                    return 0
                else
                    cd - > /dev/null || handle_error "Failed to return to original directory"
                    
                    # Método 5: Abrir sin parámetros
                    echo -e "${YELLOW}⚠️ Error al iniciar RetroVirtualMachine con todos los métodos.${NC}"
                    echo -e "${YELLOW}Método 5: Abriendo sin parámetros${NC}"
                    echo -e "${BLUE}Por favor, carga manualmente el disco desde:${NC}"
                    echo -e "${BLUE}${DSK_FULL_PATH}${NC}"
                    
                    "$RVM_PATH" || handle_error "RetroVirtualMachine failed to start"
                    return 0
                fi
            fi
        fi
    fi
}

if [ $LAUNCH_EMULATOR -eq 1 ]; then
    launch_emulator
fi 