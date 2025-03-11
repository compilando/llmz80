#!/usr/bin/env python3
import sys
import re

def ihx_to_bin(ihx_file, bin_file):
    with open(ihx_file, 'r') as f:
        ihx_content = f.readlines()
    
    # Inicializar un array de bytes
    binary_data = bytearray(65536)  # Tamaño máximo de memoria Z80
    
    for line in ihx_content:
        line = line.strip()
        if not line or not line.startswith(':'):
            continue
        
        # Formato IHX: :LLAAAATT[DD...]CC
        # LL = longitud de datos
        # AAAA = dirección
        # TT = tipo de registro
        # DD = datos
        # CC = checksum
        
        length = int(line[1:3], 16)
        address = int(line[3:7], 16)
        record_type = int(line[7:9], 16)
        
        if record_type == 0:  # Datos
            data = line[9:9+length*2]
            for i in range(0, len(data), 2):
                byte_val = int(data[i:i+2], 16)
                binary_data[address + i//2] = byte_val
    
    # Encontrar el rango de datos válidos
    start_addr = 0
    while start_addr < 65536 and binary_data[start_addr] == 0:
        start_addr += 1
    
    end_addr = 65535
    while end_addr > start_addr and binary_data[end_addr] == 0:
        end_addr -= 1
    
    # Escribir solo los datos válidos
    with open(bin_file, 'wb') as f:
        f.write(binary_data[start_addr:end_addr+1])
    
    print(f"Converted {ihx_file} to {bin_file}")
    print(f"Data range: 0x{start_addr:04X} - 0x{end_addr:04X}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: hex2bin.py input.ihx [output.bin]")
        sys.exit(1)
    
    ihx_file = sys.argv[1]
    bin_file = sys.argv[2] if len(sys.argv) > 2 else ihx_file.replace('.ihx', '.bin')
    
    ihx_to_bin(ihx_file, bin_file) 