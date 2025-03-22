#!/bin/bash

# Forzar el uso de punto decimal
export LC_NUMERIC="en_US.UTF-8"

# Colores y estilos
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'
BOLD='\033[1m'

# Arrays para almacenar resultados
declare -a examples_array
declare -a status_array
declare -a time_array
declare -a platform_array

# Error handling
handle_error() {
    echo -e "\n${RED}❌ Error: $1${NC}"
    if [ -f "/tmp/build_error" ]; then
        echo -e "\n${RED}Error details:${NC}"
        cat /tmp/build_error
    fi
    exit 1
}

# Progress bar function
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

# Function to test an example
test_example() {
    local example=$1
    local platform=$2
    local example_name=$(basename "$example" .c)
    local start_time=$(date +%s.%N)
    
    echo -e "\n${BLUE}${BOLD}Testing: ${example_name} (${platform})${NC}"
    echo -e "${YELLOW}Compiling...${NC}"
    
    if ./build.sh --no-emulator --source="$example"; then
        echo -e "${GREEN}✓ Compilation successful${NC}"
        local status="✓"
    else
        echo -e "${RED}✗ Compilation failed${NC}"
        local status="✗"
    fi
    
    local end_time=$(date +%s.%N)
    local elapsed=$(echo "$end_time - $start_time" | bc)
    local elapsed_formatted=$(printf "%.2f seconds" $elapsed)
    
    # Guardar resultados en arrays
    examples_array+=("$example_name")
    status_array+=("$status")
    time_array+=("$elapsed_formatted")
    platform_array+=("$platform")
    
    [ "$status" = "✓" ] && return 0 || return 1
}

# Función para dibujar una línea horizontal
draw_line() {
    printf "%-40s+-%7s-+-%9s-+-%8s-+\n" "----------------------------------------" "-------" "---------" "--------"
}

# Función para mostrar la tabla de resultados
show_results_table() {
    echo -e "\n${BOLD}Resultados Detallados:${NC}"
    draw_line
    printf "%-40s | %-7s | %-9s | %-8s |\n" "Ejemplo" "Estado" "Tiempo(s)" "Platform"
    draw_line
    
    for i in "${!examples_array[@]}"; do
        if [ "${status_array[$i]}" = "✓" ]; then
            status_color=$GREEN
        else
            status_color=$RED
        fi
        printf "%-40s | ${status_color}%-7s${NC} | %-9s | %-8s |\n" \
            "${examples_array[$i]}" "${status_array[$i]}" "${time_array[$i]}" "${platform_array[$i]}"
    done
    
    draw_line
}

# Main script
clear
echo -e "${BLUE}${BOLD}🧪 Retro Computer Examples Test Suite${NC}\n"

# Plataformas a probar
PLATFORMS=("zx")

# Count total examples and platforms
total_examples=$(ls examples/spectrum/*.c | wc -l)
total_tests=$((total_examples * ${#PLATFORMS[@]}))
current=0
successful=0
failed=0

# Test each example on each platform
for platform in "${PLATFORMS[@]}"; do
    for example in examples/spectrum/*.c; do
        current=$((current + 1))
        progress=$((current * 100 / total_tests))
        
        if test_example "$example" "$platform"; then
            successful=$((successful + 1))
        else
            failed=$((failed + 1))
        fi
        
        echo -e "\n${BLUE}Progress: ${NC}"
        progress_bar $progress
    done
done

# Mostrar tabla de resultados
show_results_table

# Final report
echo -e "\n${BOLD}Resumen Final:${NC}"
echo -e "${BLUE}Total ejemplos: ${total_examples}${NC}"
echo -e "${BLUE}Total plataformas: ${#PLATFORMS[@]}${NC}"
echo -e "${BLUE}Total pruebas: ${total_tests}${NC}"
echo -e "${GREEN}Exitosos: ${successful}${NC}"
echo -e "${RED}Fallidos: ${failed}${NC}"

if [ $failed -eq 0 ]; then
    echo -e "\n${GREEN}${BOLD}✨ Todos los ejemplos compilaron exitosamente!${NC}"
    exit 0
else
    echo -e "\n${RED}${BOLD}⚠️ Algunos ejemplos fallaron al compilar${NC}"
    exit 1
fi 