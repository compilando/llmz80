#!/usr/bin/env python3
import argparse
import logging
import os
import sys
import numpy as np
from pathlib import Path
from openai import OpenAI
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
        import openai
        import termcolor
        import yaml
        import dotenv
        logging.info("✅ Todas las dependencias están instaladas correctamente.")
    except ImportError as e:
        logging.error(f"❌ Falta una dependencia: {e}")
        logging.error("Ejecuta: pip install numpy openai termcolor pyyaml python-dotenv")
        sys.exit(1)

def load_api_key():
    """Carga la clave de API de OpenAI."""
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        logging.error("❌ No se encontró la clave API de OpenAI en las variables de entorno.")
        logging.error("Crea un archivo .env con la variable OPENAI_API_KEY=tu_clave_api")
        sys.exit(1)
    return api_key

def test_api_connection(api_key):
    """Prueba la conexión a la API de OpenAI."""
    client = OpenAI(api_key=api_key)
    try:
        # Intenta una llamada simple
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input="Test"
        )
        if hasattr(response, 'data') and len(response.data) > 0:
            embedding = response.data[0].embedding
            if isinstance(embedding, list) and len(embedding) > 0:
                logging.info(f"✅ Conexión a OpenAI exitosa. Dimensión de embedding: {len(embedding)}")
                return client
            else:
                logging.error(f"❌ La API devolvió un embedding inválido: {embedding}")
                sys.exit(1)
        else:
            logging.error("❌ La API devolvió una respuesta sin datos de embedding válidos.")
            sys.exit(1)
    except Exception as e:
        logging.error(f"❌ Error al conectar con la API de OpenAI: {e}")
        sys.exit(1)

def get_embedding(client, text, model="text-embedding-3-small"):
    """Obtiene el embedding para un texto asegurando que sea válido."""
    try:
        if not text or not text.strip():
            logging.warning("⚠️ Texto vacío para embedding.")
            return np.zeros((1536,), dtype=float)
            
        response = client.embeddings.create(
            model=model,
            input=text
        )
        
        embedding_data = response.data[0].embedding
        
        # Validación exhaustiva
        if not isinstance(embedding_data, list):
            logging.error(f"❌ Tipo incorrecto de embedding: {type(embedding_data)}")
            return np.zeros((1536,), dtype=float)
        
        if not embedding_data:
            logging.error("❌ La API devolvió una lista de embedding vacía")
            return np.zeros((1536,), dtype=float)
            
        if not all(isinstance(x, (int, float)) for x in embedding_data):
            logging.error("❌ La API devolvió elementos no numéricos en el embedding")
            return np.zeros((1536,), dtype=float)
            
        # Convertir a numpy array
        embedding_array = np.array(embedding_data, dtype=float)
        
        if embedding_array.size == 0:
            logging.error("❌ Array de embedding vacío después de la conversión")
            return np.zeros((1536,), dtype=float)
            
        logging.info(f"✅ Embedding generado correctamente: {embedding_array.shape}")
        return embedding_array
        
    except Exception as e:
        logging.error(f"❌ Error al obtener embedding: {e}")
        return np.zeros((1536,), dtype=float)

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