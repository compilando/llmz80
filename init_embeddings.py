#!/usr/bin/env python3
import argparse
import logging
import os
import sys
import numpy as np
from pathlib import Path
from llmz80.core.embedding_backend import EMBEDDING_DIM, EMBEDDING_MODEL, embed, zero_vector
from termcolor import colored
from dotenv import load_dotenv

def setup_basic_logging():
    """Configura un sistema de logging simple para diagnóstico."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s',
        handlers=[logging.StreamHandler()]
    )

def check_imports():
    """Verifica que todas las dependencias necesarias estén instaladas."""
    try:
        import numpy
        import fastembed
        import termcolor
        import yaml
        import dotenv
        logging.info("✅ Todas las dependencias están instaladas correctamente.")
    except ImportError as e:
        logging.error(f"❌ Falta una dependencia: {e}")
        logging.error("Ejecuta: pip install numpy fastembed termcolor pyyaml python-dotenv")
        sys.exit(1)

def load_api_key():
    """Ya no hace falta ninguna clave: los embeddings se calculan aquí.

    La función se conserva y sigue devolviendo algo porque `main` la llama y
    porque un usuario que venga de la versión anterior lo primero que
    comprueba es la clave -- decirle explícitamente que ya no se necesita es
    más útil que quitar la llamada y dejarle preguntándose si se le olvidó
    configurarla.
    """
    logging.info("🔑 No se necesita clave de API: el modelo de embeddings es local.")
    return None

def test_api_connection(api_key):
    """Comprueba que el modelo local carga y produce un vector de la anchura esperada.

    El nombre se conserva porque `main` lo llama, pero ya no hay conexión que
    probar. Lo que sí conviene verificar antes de indexar un corpus entero es
    que el modelo se descarga y arranca: es una descarga de ~67MB la primera
    vez, y descubrir que falla a mitad del indexado es peor que descubrirlo
    ahora.
    """
    try:
        logging.info(f"Cargando modelo local {EMBEDDING_MODEL} (la primera vez se descarga)...")
        vector = embed(["Test"])[0]
        if vector.shape != (EMBEDDING_DIM,):
            logging.error(f"❌ El modelo devolvió un vector de forma {vector.shape}.")
            sys.exit(1)
        logging.info(f"✅ Modelo local listo. Dimensión de embedding: {EMBEDDING_DIM}")
        return None
    except Exception as e:
        logging.error(f"❌ Error al cargar el modelo de embeddings: {e}")
        sys.exit(1)

def get_embedding(client, text, model=None):
    """Obtiene el embedding para un texto asegurando que sea válido.

    `client` y `model` se ignoran; siguen en la firma porque `main` llama a
    esta función con el resultado de `test_api_connection`.
    """
    try:
        if not text or not text.strip():
            logging.warning("⚠️ Texto vacío para embedding.")
            return zero_vector()

        embedding_array = embed([text])[0]

        if embedding_array.shape != (EMBEDDING_DIM,):
            logging.error(f"❌ Forma inesperada de embedding: {embedding_array.shape}")
            return zero_vector()

        logging.info(f"✅ Embedding generado correctamente: {embedding_array.shape}")
        return embedding_array

    except Exception as e:
        logging.error(f"❌ Error al obtener embedding: {e}")
        return zero_vector()

def create_empty_cache(platform):
    """Crea un archivo de caché vacío pero válido."""
    cache_dir = Path("local/embeddings")
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    cache_file = cache_dir / f"{platform}_embeddings.json"
    
    if cache_file.exists():
        logging.info(f"⚠️ Ya existe un archivo de caché para {platform}: {cache_file}")
        backup_file = cache_dir / f"{platform}_embeddings_backup.json"
        import shutil
        shutil.copy2(cache_file, backup_file)
        logging.info(f"✅ Se creó una copia de seguridad en: {backup_file}")
    
    # Crear un caché vacío pero válido
    import json
    with open(cache_file, 'w') as f:
        json.dump({}, f)
    
    logging.info(f"✅ Se creó un archivo de caché vacío para {platform}: {cache_file}")
    return cache_file

def test_embedding_with_sample(client, platform):
    """Prueba la generación de embeddings con un ejemplo sencillo y lo guarda en caché."""
    cache_file = create_empty_cache(platform)
    
    sample_text = """// Sample C code
#include <stdio.h>

int main() {
    printf("Hello, World!");
    return 0;
}"""

    logging.info("⏳ Generando embedding de prueba...")
    embedding = get_embedding(client, sample_text)
    
    if embedding is None or (isinstance(embedding, np.ndarray) and embedding.size == 0):
        logging.error("❌ No se pudo generar un embedding válido para la prueba")
        return False
        
    # Verificar que el embedding es válido
    if not isinstance(embedding, np.ndarray):
        logging.error(f"❌ El embedding no es un array numpy: {type(embedding)}")
        return False
        
    # Guardar en el caché
    import json
    
    try:
        # Abrir el caché existente
        with open(cache_file, 'r') as f:
            cache_data = json.load(f)
        
        # Añadir el ejemplo de prueba
        cache_data["test_example.c"] = (sample_text, embedding.tolist())
        
        # Guardar el caché actualizado
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f)
            
        logging.info(f"✅ Embedding de prueba guardado en caché con dimensiones: {embedding.shape}")
        return True
    except Exception as e:
        logging.error(f"❌ Error al guardar el embedding en el caché: {e}")
        return False

def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(
        description='Inicializador de caché de embeddings para LLMZ80'
    )
    parser.add_argument('--platform', type=str, default='spectrum',
                      choices=['spectrum', 'amstrad_cpc'],
                      help='Plataforma objetivo para inicializar el caché')
    
    args = parser.parse_args()
    platform = args.platform
    
    print(colored(f"\n🔨 Inicializador de caché de embeddings para {platform.upper()} 🔨", "green", attrs=['bold']))
    print(colored("=" * 60, "green"))
    
    # 1. Configurar logging básico
    setup_basic_logging()
    
    # 2. Verificar dependencias
    check_imports()
    
    # 3. Cargar API key
    api_key = load_api_key()
    
    # 4. Probar conexión a API
    client = test_api_connection(api_key)
    
    # 5. Probar generación y guardado de embeddings
    success = test_embedding_with_sample(client, platform)
    
    if success:
        print(colored("\n✅ Inicialización exitosa del caché de embeddings", "green", attrs=['bold']))
        print(colored("Ahora puedes ejecutar el script principal sin problemas.", "green"))
    else:
        print(colored("\n❌ Error durante la inicialización del caché", "red", attrs=['bold']))
        print(colored("Revisa los mensajes de error anteriores para diagnosticar el problema.", "red"))
        
    print("\nRecuerda ejecutar el script principal con la opción --rebuild-embeddings")
    print("para reconstruir completamente el caché con todos los ejemplos.")

if __name__ == "__main__":
    main() 