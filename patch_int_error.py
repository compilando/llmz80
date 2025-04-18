#!/usr/bin/env python3
"""
Script para corregir específicamente el error 'object of type int has no len()'
Este script busca directamente valores enteros en el caché de embeddings y los reemplaza
por arrays numpy vacíos para prevenir el error.
"""

import json
import logging
import os
import sys
import numpy as np
from pathlib import Path
import argparse
from termcolor import colored

def setup_logging():
    """Configuración básica de logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s',
        handlers=[logging.StreamHandler()]
    )

def fix_int_embeddings(platform):
    """Busca y corrige valores enteros en el caché de embeddings."""
    cache_dir = Path("local/embeddings")
    cache_file = cache_dir / f"{platform}_embeddings.json"
    
    if not cache_file.exists():
        logging.error(f"El archivo de caché no existe: {cache_file}")
        logging.info("Primero debes inicializar el caché con ./init_embeddings.py")
        return False
    
    # Hacer backup
    backup_file = cache_file.with_suffix('.backup.json')
    try:
        import shutil
        shutil.copy2(cache_file, backup_file)
        logging.info(f"Backup creado: {backup_file}")
    except Exception as e:
        logging.error(f"No se pudo crear backup: {e}")
        if input("¿Continuar sin backup? (y/n): ").lower() != 'y':
            return False
    
    # Cargar caché
    try:
        with open(cache_file, 'r') as f:
            cache_data = json.load(f)
        
        if not isinstance(cache_data, dict):
            logging.error(f"El caché no es un diccionario: {type(cache_data)}")
            return False
        
        logging.info(f"Caché cargado con {len(cache_data)} entradas")
    except Exception as e:
        logging.error(f"Error al cargar caché: {e}")
        return False
    
    # Buscar y corregir enteros
    int_found = False
    fixed_cache = {}
    
    for file_path, data in cache_data.items():
        if not isinstance(data, (tuple, list)) or len(data) != 2:
            logging.warning(f"Datos inválidos para {file_path}: {type(data)}")
            fixed_cache[file_path] = (data[0] if isinstance(data, (tuple, list)) and len(data) > 0 else "", None)
            continue
        
        content, embedding = data
        
        # Específicamente buscando enteros (el error 'int' has no len())
        if isinstance(embedding, int):
            logging.warning(f"¡ENCONTRADO! Embedding entero en {file_path}: {embedding}")
            # Reemplazar con array vacío
            fixed_cache[file_path] = (content, [0.0] * 1536)  # Vector de ceros con dimensión estándar
            int_found = True
        else:
            # Verificar otros posibles problemas
            if embedding is None:
                logging.warning(f"Embedding None en {file_path}")
                # Mantener como None para regeneración posterior
                fixed_cache[file_path] = (content, None)
            elif not isinstance(embedding, (list, np.ndarray)):
                logging.warning(f"Embedding de tipo inválido en {file_path}: {type(embedding)}")
                # Reemplazar con array vacío
                fixed_cache[file_path] = (content, [0.0] * 1536)
            else:
                # Parece válido, mantener
                fixed_cache[file_path] = (content, embedding)
    
    if not int_found:
        logging.info("No se encontraron embeddings de tipo entero. El error debe estar en otra parte.")
        return False
    
    # Guardar caché corregido
    try:
        with open(cache_file, 'w') as f:
            json.dump(fixed_cache, f)
        logging.info(f"Caché corregido guardado: {cache_file}")
        return True
    except Exception as e:
        logging.error(f"Error al guardar caché corregido: {e}")
        return False

def dump_sample_entry(platform):
    """Muestra una entrada de ejemplo del caché para diagnóstico."""
    cache_dir = Path("local/embeddings")
    cache_file = cache_dir / f"{platform}_embeddings.json"
    
    if not cache_file.exists():
        logging.error(f"El archivo de caché no existe: {cache_file}")
        return
    
    try:
        with open(cache_file, 'r') as f:
            cache_data = json.load(f)
        
        if not isinstance(cache_data, dict) or len(cache_data) == 0:
            logging.error("Caché vacío o no es un diccionario")
            return
        
        # Tomar primera entrada
        first_key = list(cache_data.keys())[0]
        first_value = cache_data[first_key]
        
        print("\n--- DIAGNÓSTICO DE UNA ENTRADA DE CACHÉ ---")
        print(f"Archivo: {first_key}")
        print(f"Tipo de datos: {type(first_value)}")
        
        if isinstance(first_value, (tuple, list)) and len(first_value) == 2:
            content, embedding = first_value
            print(f"Contenido (fragmento): {content[:100]}...")
            print(f"Tipo de embedding: {type(embedding)}")
            
            if isinstance(embedding, list):
                print(f"Longitud del embedding: {len(embedding)}")
                print(f"Primer elemento: {embedding[0] if embedding else None}")
            elif isinstance(embedding, np.ndarray):
                print(f"Forma del embedding: {embedding.shape}")
            elif embedding is None:
                print("Embedding: None")
            else:
                print(f"Valor embedding: {embedding}")
        else:
            print(f"Valor: {first_value}")
    except Exception as e:
        logging.error(f"Error al mostrar entrada de ejemplo: {e}")

def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description='Corrige errores de tipo entero en embeddings'
    )
    parser.add_argument('--platform', type=str, default='spectrum',
                     choices=['spectrum', 'amstrad_cpc'],
                     help='Plataforma a procesar')
    
    args = parser.parse_args()
    platform = args.platform
    
    print(colored(f"\n🛠️ Corrector de error 'int has no len()' para {platform.upper()} 🛠️", "cyan", attrs=['bold']))
    print(colored("=" * 60, "cyan"))
    
    setup_logging()
    
    # Mostrar diagnóstico
    dump_sample_entry(platform)
    
    # Corregir errores
    success = fix_int_embeddings(platform)
    
    if success:
        print(colored("\n✅ Corrección completada exitosamente!", "green", attrs=['bold']))
        print(colored("Ahora puedes ejecutar el script principal", "green"))
    else:
        print(colored("\n⚠️ No se realizaron cambios al caché", "yellow", attrs=['bold']))
        print(colored("Intenta con ./init_embeddings.py seguido de --rebuild-embeddings", "yellow"))

if __name__ == "__main__":
    main() 