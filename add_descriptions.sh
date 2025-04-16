#!/bin/bash

# Colores para mensajes
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# --- Configuración ---
PYTHON_SCRIPT="llm_z80.py" # Script principal que contiene la nueva lógica --describe-code
VENV_PATH="venv"          # Ruta al entorno virtual
EXAMPLE_BASE_DIR="examples"
PLATFORMS=("spectrum" "amstrad_cpc")
DESCRIPTION_PREFIX="// Description:"
SKIP_EXISTING=true # Poner a false para regenerar descripciones existentes

# --- Funciones ---
log_info() {
    echo -e "${BLUE}INFO:${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}WARN:${NC} $1"
}

log_error() {
    echo -e "${RED}ERROR:${NC} $1"
}

log_success() {
    echo -e "${GREEN}SUCCESS:${NC} $1"
}

activate_venv() {
    if [ -d "$VENV_PATH" ] && [ -f "$VENV_PATH/bin/activate" ]; then
        log_info "Activando entorno virtual..."
        source "$VENV_PATH/bin/activate"
        if [ $? -ne 0 ]; then
            log_error "No se pudo activar el entorno virtual."
            exit 1
        fi
    else
        log_error "Entorno virtual no encontrado en '$VENV_PATH'."
        exit 1
    fi
}

# --- Script Principal ---
log_info "Iniciando proceso para añadir descripciones a archivos de ejemplo..."

activate_venv

# Verificar que el script Python existe
if [ ! -f "$PYTHON_SCRIPT" ]; then
    log_error "Script Python '$PYTHON_SCRIPT' no encontrado."
    exit 1
fi

# Verificar que el directorio base de ejemplos existe
if [ ! -d "$EXAMPLE_BASE_DIR" ]; then
    log_error "Directorio base de ejemplos '$EXAMPLE_BASE_DIR' no encontrado."
    exit 1
fi

processed_count=0
skipped_count=0
error_count=0

for platform in "${PLATFORMS[@]}"; do
    platform_dir="$EXAMPLE_BASE_DIR/$platform"
    log_info "Procesando plataforma: $platform en $platform_dir"

    if [ ! -d "$platform_dir" ]; then
        log_warn "Directorio para plataforma $platform no encontrado, saltando."
        continue
    fi

    # Buscar archivos .c excluyendo directorios 'common' y 'build'
    find "$platform_dir" -name "*.c" -type f -not \( -path "*/common/*" -o -path "*/build/*" \) | while read -r c_file; do
        relative_path="${c_file#$EXAMPLE_BASE_DIR/}"
        log_info "  Verificando archivo: $relative_path"

        # Leer primera línea para comprobaciones iniciales
        first_line=$(head -n 1 "$c_file")
        found_existing_description=false
        existing_description_text=""

        # 1. Comprobar si ya tiene el formato estándar "// Description:"
        if echo "$first_line" | grep -qE "^//\s*Description:"; then
            found_existing_description=true
            existing_description_text=$(echo "$first_line" | sed 's|^//\s*Description:\s*||')
            log_info "    -> Encontrado formato estándar: '$existing_description_text'"
        
        # 2. Si no, comprobar si empieza con /* y buscar descripción dentro
        elif echo "$first_line" | grep -qE "^\s*/\*"; then
            # Leer desde la línea 2, quitar espacios/* iniciales, quitar líneas vacías, tomar la primera
            potential_desc=$(tail -n +2 "$c_file" | sed -e 's/^\s*\*\{0,1\}\s*//' -e '/^\s*$/d' | head -n 1)
            # Quitar posible cierre de comentario */ si está en la misma línea
            potential_desc=$(echo "$potential_desc" | sed 's/\s*\*\/\s*$//')

            if [ -n "$potential_desc" ]; then
                 # Podríamos añadir heurísticas más complejas para validar si parece una descripción
                 # Por ahora, aceptamos la primera línea no vacía/no-asterisco
                 found_existing_description=true
                 existing_description_text="$potential_desc"
                 log_info "    -> Encontrada descripción potencial en bloque /*: '$existing_description_text'"
            else
                log_warn "    -> Se encontró bloque /* pero no texto útil dentro como descripción."
            fi
        fi
        
        # 3. Decidir si saltar o continuar basado en la descripción encontrada y SKIP_EXISTING
        if $found_existing_description && $SKIP_EXISTING; then
             log_info "    -> Saltando archivo (SKIP_EXISTING=true)."
             skipped_count=$((skipped_count + 1))
             continue
        fi

        # 4. Si no se encontró descripción existente útil O si SKIP_EXISTING es false, generar con LLM
        log_info "    -> Generando descripción con LLM..."
        generated_description=$(python "$PYTHON_SCRIPT" --describe-code --file "$c_file" --platform "$platform")
        python_exit_code=$?

        if [ $python_exit_code -ne 0 ] || [ -z "$generated_description" ]; then
            log_error "    -> Falló la generación de descripción para $relative_path (Código: $python_exit_code)"
            error_count=$((error_count + 1))
            continue
        fi

        # Limpiar descripción por si acaso (eliminar saltos de línea extras)
        generated_description=$(echo "$generated_description" | tr -d '\n\r')

        log_info "    -> Descripción generada: '$generated_description'"
        log_info "    -> Añadiendo descripción al archivo..."

        # Crear archivo temporal
        temp_file=$(mktemp)
        if [ $? -ne 0 ]; then
            log_error "    -> No se pudo crear archivo temporal para $relative_path"
            error_count=$((error_count + 1))
            continue
        fi

        # Escribir la nueva descripción generada por el LLM
        echo "$DESCRIPTION_PREFIX $generated_description" > "$temp_file"
        
        # Añadir el resto del contenido original
        # Si la primera línea original era una descripción (en cualquier formato detectado), la saltamos.
        # Si no, incluimos todo el archivo original.
        if $found_existing_description; then
            log_info "    -> Reemplazando descripción existente detectada."
            # Si empezó con /*, puede que necesitemos quitar más líneas (todo el bloque)?
            # Por simplicidad ahora: solo quitamos la primera línea si era // Description:
            # Si era /*, el nuevo // Description: se añadirá encima.
            if echo "$first_line" | grep -qE "^//\s*Description:"; then
                tail -n +2 "$c_file" >> "$temp_file"
            else
                # Si era un bloque /*, añadimos todo el contenido original (la nueva desc va antes)
                cat "$c_file" >> "$temp_file"
            fi
        else
             # Si no había descripción detectable, añadimos todo el contenido original
             cat "$c_file" >> "$temp_file"
        fi

        # Reemplazar el archivo original con el temporal
        mv "$temp_file" "$c_file"
        if [ $? -ne 0 ]; then
            log_error "    -> No se pudo actualizar el archivo $relative_path"
            error_count=$((error_count + 1))
            # Limpiar archivo temporal si mv falló
            rm -f "$temp_file"
            continue
        fi

        log_success "    -> Descripción añadida/actualizada correctamente."
        processed_count=$((processed_count + 1))

    done # Fin del bucle while read

done # Fin del bucle for platform

log_info "----------------------------------------"
log_info "Proceso completado."
log_success "Descripciones añadidas/actualizadas: $processed_count"
log_info "Archivos saltados (ya tenían descripción): $skipped_count"
log_error "Archivos con errores: $error_count"
log_info "----------------------------------------"

exit $error_count 