import os
import argparse
from openai import OpenAI
from pathlib import Path
import yaml
from dotenv import load_dotenv
import re
from datetime import datetime
import logging
from termcolor import colored
import glob
from typing import Dict, List, Optional, Any, Tuple # Import type hints
import numpy as np
from numpy.linalg import norm
import json
import time
import random

# --- Constants ---
CONFIG_FILE = "config.yml"

# Valores por defecto que serán reemplazados por la configuración
DEFAULT_MODEL = "gpt-4o"
DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 4096
DEFAULT_MAX_EXAMPLES = 10
DEFAULT_LOG_LEVEL = "INFO"

# Estos valores serán cargados desde la configuración
LOG_DIR = None
BASE_OUTPUT_DIR = None
EXAMPLE_DIR_TEMPLATE = "examples/{platform}"
SYSTEM_PROMPT_FILE_TEMPLATE = None
ERROR_DOC_GLOB_PATTERN = '**/*.md'
EMBEDDINGS_CACHE_DIR = None
MAX_EXAMPLE_SIZE = None
MAX_CHUNK_SIZE = None
SLUG_MAX_LENGTH = None
TOKEN_LIMIT = None
SAFETY_MARGIN = None

# --- Custom Logger Formatter ---
class ConsoleFormatter(logging.Formatter):
    ICONS = {
        'INFO': '🔵',
        'ERROR': '🔴',
        'WARNING': '🟡',
        'DEBUG': '🟣'
    }
    COLORS = {
        'INFO': 'cyan',
        'ERROR': 'red',
        'WARNING': 'yellow',
        'DEBUG': 'magenta'
    }

    def format(self, record: logging.LogRecord) -> str:
        icon = self.ICONS.get(record.levelname, '🔵')
        color = self.COLORS.get(record.levelname, 'white')
        message = record.getMessage()

        if record.levelname == 'INFO':
            return colored(f"{icon} {message}", color)
        return colored(f"{icon} {record.levelname}: {message}", color)

# --- Main Generator Class ---
class LLMZ80Generator:
    def __init__(self, platform: str = "spectrum", config_path: str = CONFIG_FILE):
        # 1. Configuraciones básicas que no dependen del config
        self.platform = platform.lower()
        self.force_truncate = False  # Por defecto, no forzar truncado
        self.use_embeddings = True   # Por defecto, usar embeddings para búsqueda semántica
        
        # 2. Cargar configuración primero para poder inicializar variables globales
        self.config = self._load_config(config_path)
        self._init_global_variables()
        
        # 3. Configuración inicial para los logs ahora que tenemos las variables globales
        self._setup_logging()  
        
        try:            
            # 4. Cargar el resto de configuraciones
            self.api_key = self._load_api_key()
            self.client = OpenAI(api_key=self.api_key)
            
            # Get generation parameters from config or use defaults
            self.model = self.config.get('openai', {}).get('model', DEFAULT_MODEL)
            self.temperature = self.config.get('openai', {}).get('temperature', DEFAULT_TEMPERATURE)
            self.max_tokens = self.config.get('openai', {}).get('max_tokens', DEFAULT_MAX_TOKENS)
            self.max_examples = self.config.get('examples', {}).get('max_examples', DEFAULT_MAX_EXAMPLES)
            
            logging.info(f"🚀 Initializing LLMZ80 Code Generator for {self.platform.upper().replace('_', ' ')}")
            logging.info(f"⚙️ Using Model: {self.model}, Temp: {self.temperature}, Max Tokens: {self.max_tokens}, Max Examples: {self.max_examples}")
            logging.info("✅ Generator initialized successfully.")
            
        except Exception as e:
            logging.error(f"Initialization error: {e}")
            raise

    def _setup_logging(self) -> None:
        """Configures file and console logging."""
        try:
            LOG_DIR.mkdir(parents=True, exist_ok=True)
            log_file = LOG_DIR / f"llmz80_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

            # Usar valores por defecto para el nivel de log
            log_level_str = DEFAULT_LOG_LEVEL
            if hasattr(self, 'config') and self.config:
                log_level_str = self.config.get('logging', {}).get('level', DEFAULT_LOG_LEVEL).upper()
            log_level = getattr(logging, log_level_str, logging.INFO)

            # File handler
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))

            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(ConsoleFormatter())

            # Configure root logger
            logging.basicConfig(
                level=log_level,
                handlers=[file_handler, console_handler],
                # force=True # Use force=True in Python 3.8+ to allow reconfiguration
            )
            # For older Python versions or to avoid 'force': remove existing handlers
            root_logger = logging.getLogger()
            if root_logger.hasHandlers():
                 root_logger.handlers.clear()
            root_logger.addHandler(file_handler)
            root_logger.addHandler(console_handler)
            root_logger.setLevel(log_level)


            logging.debug("Logging configured.")
        except Exception as e:
            print(f"🔴 FATAL: Error setting up logging: {e}") # Use print as logging might not work
            raise

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Loads configuration from a YAML file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
                print(f"✅ Configuration loaded successfully from {config_path}")
                return config_data if config_data else {}
        except FileNotFoundError:
            print(f"⚠️ Configuration file {config_path} not found. Using defaults.")
            return {}
        except Exception as e:
            print(f"❌ Error loading configuration from {config_path}: {e}")
            raise # Re-raise critical error

    def _load_api_key(self) -> str:
        """Loads OpenAI API key from environment variables."""
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            logging.error("❌ OPENAI_API_KEY not found in environment variables or .env file")
            raise ValueError("OPENAI_API_KEY is required.")
        logging.info("🔑 OpenAI API key found.")
        return api_key

    def _create_slug(self, text: str, max_length: int = None) -> str:
        """Generates a URL-friendly slug from text."""
        if max_length is None:
            max_length = SLUG_MAX_LENGTH
            
        logging.debug(f"Creating slug from text: {text[:50]}...")
        slug = text.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug) # Remove unwanted chars
        slug = re.sub(r'[-\s]+', '-', slug).strip('-') # Replace spaces/hyphens with single hyphen
        slug = slug[:max_length] # Truncate
        logging.debug(f"Created slug: {slug}")
        return slug

    def _get_output_paths(self, prompt: str) -> Dict[str, Path]:
        """Generates paths for output files based on timestamp and prompt slug."""
        logging.info("🗂️ Generating output paths...")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        slug = self._create_slug(prompt)
        base_dir = BASE_OUTPUT_DIR / f"{timestamp}_{slug}"

        paths = {
            'base': base_dir,
            'c_file': base_dir / 'main.c',
            'prompt_file': base_dir / 'prompt.txt',
            'platform_file': base_dir / 'platform.txt', # Renamed for clarity
            'obj_dir': base_dir / 'obj', # Explicitly add obj dir path
        }

        # Platform-specific output file (might need adjustment based on build process)
        if self.platform == 'spectrum':
            paths['output_artifact'] = base_dir / 'output.tap' # Example artifact name
        elif self.platform == 'amstrad_cpc':
            paths['output_artifact'] = base_dir / 'output.dsk' # Example artifact name
        else:
             paths['output_artifact'] = base_dir / 'output.bin' # Generic fallback

        logging.debug(f"Generated paths: {paths}")
        return paths

    def _load_embeddings_cache(self) -> Dict[str, Tuple[str, np.ndarray]]:
        """Carga el caché de embeddings si existe."""
        cache_file = EMBEDDINGS_CACHE_DIR / f"{self.platform}_embeddings.json"
        if not cache_file.exists():
            logging.info(f"No se encontró caché de embeddings en {cache_file}")
            return {}
        
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # Convertir las listas de embeddings en numpy arrays
            embeddings_cache = {}
            valid_count = 0
            invalid_count = 0
            
            # Verificar que cache_data sea un diccionario
            if not isinstance(cache_data, dict):
                logging.error(f"Caché corrupto: El formato no es un diccionario. Regenerando caché.")
                return {}
            
            for file_path, data_tuple in cache_data.items():
                # Verificar que data_tuple sea una tupla o lista con 2 elementos
                if not isinstance(data_tuple, (list, tuple)) or len(data_tuple) != 2:
                    logging.warning(f"Formato incorrecto para {file_path} en caché. Será regenerado.")
                    invalid_count += 1
                    continue
                
                # Extraer contenido y embedding
                content, embedding_data = data_tuple
                
                # Verificar que el contenido sea un string
                if not isinstance(content, str):
                    logging.warning(f"Contenido no es string para {file_path}. Será ignorado.")
                    invalid_count += 1
                    continue
                
                # Procesar el embedding si existe
                if embedding_data is not None:
                    # Verificar que embedding_data sea una lista de números
                    if isinstance(embedding_data, list) and all(isinstance(x, (int, float)) for x in embedding_data):
                        try:
                            # Convertir a array numpy
                            embedding_array = np.array(embedding_data, dtype=float)
                            # Solo añadir si el array no está vacío
                            if embedding_array.size > 0:
                                embeddings_cache[file_path] = (content, embedding_array)
                                valid_count += 1
                            else:
                                embeddings_cache[file_path] = (content, None)
                                invalid_count += 1
                                logging.warning(f"Embedding vacío para {file_path}. Será regenerado.")
                        except Exception as e:
                            logging.warning(f"Error al convertir embedding para {file_path}: {e}. Será regenerado.")
                            embeddings_cache[file_path] = (content, None)
                            invalid_count += 1
                    else:
                        logging.warning(f"Embedding inválido para {file_path}: tipo {type(embedding_data)}. Será regenerado.")
                        embeddings_cache[file_path] = (content, None)
                        invalid_count += 1
                else:
                    # Si el embedding es None, mantenerlo como None para regenerarlo
                    embeddings_cache[file_path] = (content, None)
                    invalid_count += 1
            
            logging.info(f"✅ Caché cargado: {valid_count} embeddings válidos, {invalid_count} a regenerar.")
            
            # Si todos los embeddings son inválidos, podríamos tener un problema con el formato del caché
            if valid_count == 0 and invalid_count > 0:
                logging.warning(f"⚠️ Todos los embeddings ({invalid_count}) necesitan regeneración.")
            
            return embeddings_cache
            
        except json.JSONDecodeError:
            logging.error(f"El archivo de caché {cache_file} no es un JSON válido. Se ignorará.")
            return {}
        except Exception as e:
            logging.error(f"Error al cargar el caché de embeddings: {e}")
            return {}

    def _save_embeddings_cache(self, embeddings_cache: Dict[str, Tuple[str, np.ndarray]]) -> None:
        """Guarda el caché de embeddings."""
        EMBEDDINGS_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_file = EMBEDDINGS_CACHE_DIR / f"{self.platform}_embeddings.json"
        
        try:
            # Convertir numpy arrays a listas para serialización JSON
            serializable_cache = {}
            valid_count = 0
            invalid_count = 0
            
            for file_path, (content, embedding_array) in embeddings_cache.items():
                if embedding_array is not None and isinstance(embedding_array, np.ndarray) and embedding_array.size > 0:
                    try:
                        # Verificar que el embedding es válido para serializar
                        embedding_list = embedding_array.tolist()
                        serializable_cache[file_path] = (content, embedding_list)
                        valid_count += 1
                    except Exception as e:
                        logging.warning(f"Error al serializar embedding para {file_path}: {e}")
                        # Guardar con embedding None para regenerar en la próxima ejecución
                        serializable_cache[file_path] = (content, None)
                        invalid_count += 1
                else:
                    # Guardar con embedding None para regenerar en la próxima ejecución
                    serializable_cache[file_path] = (content, None)
                    invalid_count += 1
            
            with open(cache_file, 'w') as f:
                json.dump(serializable_cache, f)
            
            logging.info(f"✅ Caché de embeddings guardado en {cache_file}")
            logging.info(f"   Embeddings guardados: {valid_count} válidos, {invalid_count} inválidos o nulos")
        except Exception as e:
            logging.error(f"Error al guardar el caché de embeddings: {e}")
            # Intentar guardar un archivo de emergencia para recuperar al menos los contenidos
            try:
                emergency_file = EMBEDDINGS_CACHE_DIR / f"{self.platform}_embeddings_emergency.json"
                emergency_cache = {}
                
                for file_path, (content, _) in embeddings_cache.items():
                    # Guardar solo los contenidos sin embeddings
                    emergency_cache[file_path] = (content, None)
                
                with open(emergency_file, 'w') as f:
                    json.dump(emergency_cache, f)
                
                logging.info(f"✅ Caché de emergencia guardado en {emergency_file} (sin embeddings)")
            except Exception as e2:
                logging.error(f"Error al guardar el caché de emergencia: {e2}")

    def _estimate_tokens(self, text: str) -> int:
        """Estima de manera sencilla el número de tokens en un texto.
        
        Aproximación: 1 token ≈ 4 caracteres en inglés/código.
        Esta es una estimación muy básica; en realidad varía según el modelo y el idioma.
        """
        # Estimación conservadora: 1 token por cada 3.5 caracteres (para ser más seguros)
        return int(len(text) / 3.5)

    def _get_embedding(self, text: str) -> np.ndarray:
        """Obtiene el embedding para un texto dado usando la API de OpenAI."""
        try:
            # Obtener el modelo de embedding de la configuración
            embedding_model = self.config.get('openai', {}).get('embedding_model', DEFAULT_EMBEDDING_MODEL)
            
            # Calcular el máximo tamaño seguro para un chunk
            # TOKEN_LIMIT y SAFETY_MARGIN están inicializados desde la configuración
            safe_token_limit = int(TOKEN_LIMIT * SAFETY_MARGIN)  # Usar margen de seguridad
            estimated_tokens = self._estimate_tokens(text)
            
            # Si el texto está vacío, devolver un array vacío
            if not text.strip():
                logging.warning("Texto vacío para embedding. Devolviendo array vacío.")
                return np.zeros((1536,), dtype=float)  # Dimensión por defecto para embeddings
            
            # Si el texto es corto (está dentro del límite seguro), procesarlo directamente
            if estimated_tokens <= safe_token_limit:
                logging.debug(f"Texto dentro del límite de tokens: ~{estimated_tokens} tokens estimados")
                try:
                    response = self.client.embeddings.create(
                        model=embedding_model,
                        input=text
                    )
                    embedding_data = response.data[0].embedding
                    
                    # Verificar que embedding_data sea una lista antes de convertirlo
                    if not isinstance(embedding_data, list):
                        logging.error(f"API devolvió un embedding inválido, tipo: {type(embedding_data)}")
                        return np.zeros((1536,), dtype=float)  # Devolver array por defecto en caso de error
                        
                    # Verificar que todos los elementos sean números
                    if not all(isinstance(x, (int, float)) for x in embedding_data):
                        logging.error("API devolvió elementos no numéricos en el embedding")
                        return np.zeros((1536,), dtype=float)
                        
                    return np.array(embedding_data, dtype=float)
                except Exception as e:
                    if "maximum context length" in str(e):
                        logging.warning(f"La estimación de tokens falló, el texto es demasiado largo. Dividiendo...")
                        # Si falla, caemos en la división en chunks más pequeños
                    else:
                        logging.error(f"Error al obtener embedding: {e}")
                        return np.zeros((1536,), dtype=float)  # Devolver array por defecto en caso de error
            
            # Para textos largos, dividir en chunks más pequeños
            logging.info(f"Texto demasiado largo para embedding (~{estimated_tokens} tokens estimados). Dividiendo en chunks...")
            
            # Usar un tamaño de chunk más agresivo si es extremadamente grande
            if estimated_tokens > safe_token_limit * 1.5:
                # Si es extremadamente grande, reducir aún más el tamaño del chunk
                reduction_factor = min(4, max(2, estimated_tokens / safe_token_limit))
                actual_chunk_size = int((safe_token_limit * 3.5) / reduction_factor)
                logging.info(f"Texto extremadamente grande, reduciendo tamaño de chunk por factor {reduction_factor:.1f}")
            else:
                # Tamaño normal para textos largos pero no extremos
                actual_chunk_size = min(MAX_CHUNK_SIZE, int((safe_token_limit * 3.5)))
                
            logging.info(f"Usando tamaño de chunk de {actual_chunk_size} caracteres (~{int(actual_chunk_size/3.5)} tokens est.)")
            
            chunks = []
            # Asegurarnos de que los chunks sean lo suficientemente pequeños
            for i in range(0, len(text), actual_chunk_size):
                chunk = text[i:i + actual_chunk_size]
                if chunk:  # Asegurarse de que el chunk no esté vacío
                    chunks.append(chunk)
                    
            # Si aún así los chunks son demasiado grandes, intentar una segunda división
            if len(chunks) == 1 and self._estimate_tokens(chunks[0]) > safe_token_limit:
                logging.warning(f"El único chunk sigue siendo demasiado grande ({self._estimate_tokens(chunks[0])} tokens). Dividiendo más agresivamente...")
                chunk = chunks[0]
                chunks = []
                smaller_chunk_size = int(actual_chunk_size / 2)
                for i in range(0, len(chunk), smaller_chunk_size):
                    subchunk = chunk[i:i + smaller_chunk_size]
                    if subchunk:
                        chunks.append(subchunk)
                logging.info(f"Re-dividido en {len(chunks)} chunks más pequeños de ~{smaller_chunk_size} caracteres")
            
            # Si hay demasiados chunks, tomar solo una muestra representativa
            max_chunks_to_process = 10  # Limitar el número de chunks a procesar
            if len(chunks) > max_chunks_to_process:
                logging.warning(f"Demasiados chunks ({len(chunks)}). Tomando una muestra representativa...")
                # Tomar el primer chunk, algunos del medio y el último
                sampled_chunks = [chunks[0]]  # Primer chunk
                
                # Chunks del medio con espaciado uniforme
                middle_indices = np.linspace(1, len(chunks)-2, max_chunks_to_process-2, dtype=int)
                for idx in middle_indices:
                    sampled_chunks.append(chunks[idx])
                
                sampled_chunks.append(chunks[-1])  # Último chunk
                chunks = sampled_chunks
                logging.info(f"Muestra reducida a {len(chunks)} chunks representativos")
            
            # Procesar cada chunk por separado
            embeddings = []
            for i, chunk in enumerate(chunks):
                chunk_tokens = self._estimate_tokens(chunk)
                logging.info(f"Procesando chunk {i+1} de {len(chunks)} (~{chunk_tokens} tokens est.)...")
                
                try:
                    response = self.client.embeddings.create(
                        model=embedding_model,
                        input=chunk
                    )
                    chunk_embedding_data = response.data[0].embedding
                    
                    # Verificar que sea una lista y contenga solo números
                    if not isinstance(chunk_embedding_data, list):
                        logging.warning(f"Chunk {i+1}: API devolvió un embedding inválido, tipo: {type(chunk_embedding_data)}")
                        continue
                        
                    if not all(isinstance(x, (int, float)) for x in chunk_embedding_data):
                        logging.warning(f"Chunk {i+1}: API devolvió elementos no numéricos en el embedding")
                        continue
                    
                    chunk_embedding = np.array(chunk_embedding_data, dtype=float)
                    embeddings.append(chunk_embedding)
                except Exception as e:
                    if "maximum context length" in str(e):
                        logging.error(f"Chunk {i+1} sigue siendo demasiado grande: {str(e)}")
                        # Si un chunk sigue siendo demasiado grande, podríamos dividirlo más
                        # Por ahora, lo omitimos para evitar recursión
                        logging.warning(f"Omitiendo chunk {i+1} por ser demasiado grande")
                        continue
                    else:
                        logging.error(f"Error al procesar chunk {i+1}: {e}")
                        continue  # Continuar con el siguiente chunk en caso de error
            
            # Combinar los embeddings (promedio simple)
            if embeddings:
                try:
                    combined_embedding = np.mean(embeddings, axis=0)
                    # Normalizar para mantener las propiedades del espacio de embeddings
                    if norm(combined_embedding) > 0:
                        combined_embedding = combined_embedding / norm(combined_embedding)
                    logging.info(f"Embedding combinado generado con éxito a partir de {len(embeddings)} chunks (de {len(chunks)} intentados).")
                    return combined_embedding
                except Exception as e:
                    logging.error(f"Error al combinar embeddings: {e}")
                    return np.zeros((1536,), dtype=float)  # Devolver array por defecto en caso de error
            else:
                logging.error("No se pudo generar ningún embedding válido de los chunks")
                return np.zeros((1536,), dtype=float)  # Devolver array por defecto en caso de error
            
        except Exception as e:
            logging.error(f"Error al obtener embedding: {e}")
            # Retornar un embedding vacío en caso de error
            return np.zeros((1536,), dtype=float)  # Dimensión por defecto para text-embedding-3-small

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calcula la similitud coseno entre dos vectores."""
        try:
            # Verificar que ambos vectores son arrays numpy y no están vacíos
            if not isinstance(a, np.ndarray) or not isinstance(b, np.ndarray):
                logging.warning(f"Tipos no válidos para similitud coseno: {type(a)}, {type(b)}")
                return 0.0
            
            if a.size == 0 or b.size == 0:
                logging.warning("Uno de los vectores para similitud coseno está vacío")
                return 0.0
                
            # Verificar que los vectores tienen la misma longitud
            if a.shape != b.shape:
                logging.warning(f"Los vectores tienen formas diferentes: {a.shape} vs {b.shape}")
                return 0.0
                
            a_norm = norm(a)
            b_norm = norm(b)
            
            if a_norm == 0 or b_norm == 0:
                logging.warning("Uno de los vectores tiene norma cero, no se puede calcular similitud coseno")
                return 0.0
                
            return np.dot(a, b) / (a_norm * b_norm)
        except Exception as e:
            logging.error(f"Error en cálculo de similitud coseno: {e}")
            return 0.0

    def _get_embedding_for_large_file(self, content: str) -> np.ndarray:
        """Obtiene el embedding para un archivo muy grande usando una estrategia de muestreo.
        
        Args:
            content: El contenido del archivo grande
            
        Returns:
            Un array numpy con el embedding combinado de las muestras del archivo
        """
        logging.info(f"Procesando archivo grande ({len(content)} caracteres) con estrategia de muestreo...")
        
        # 1. Dividir el archivo en secciones significativas (inicio, fragmentos intermedios, final)
        sample_size = min(15000, int(MAX_EXAMPLE_SIZE / 4))
        
        # Tomar inicio
        start_content = content[:sample_size]
        
        # Tomar final
        end_content = content[-sample_size:] if len(content) > sample_size else ""
        
        # Tomar algunos fragmentos intermedios si el archivo es muy grande
        middle_samples = []
        if len(content) > sample_size * 3:
            # Tomar hasta 4 muestras intermedias equidistantes
            sections = min(4, max(2, int(len(content) / MAX_EXAMPLE_SIZE)))
            mid_points = np.linspace(sample_size, len(content) - sample_size - 1, sections, dtype=int)
            for point in mid_points:
                if point > sample_size and point < len(content) - sample_size:
                    middle_samples.append(content[point:point + sample_size])
        
        # 2. Generar embeddings para cada sección y combinarlos
        embeddings_to_combine = []
        samples_attempted = 0
        samples_successful = 0
        
        # Procesar inicio
        samples_attempted += 1
        try:
            start_embedding = self._get_embedding(start_content)
            if isinstance(start_embedding, np.ndarray) and start_embedding.size > 0 and not np.all(start_embedding == 0):
                embeddings_to_combine.append(start_embedding)
                samples_successful += 1
                logging.debug(f"✅ Muestra de inicio procesada correctamente")
            else:
                logging.warning(f"⚠️ La muestra de inicio no generó un embedding válido")
        except Exception as e:
            logging.error(f"Error al procesar muestra de inicio: {e}")
        
        # Procesar muestras intermedias
        for i, mid_sample in enumerate(middle_samples):
            samples_attempted += 1
            try:
                mid_embedding = self._get_embedding(mid_sample)
                if isinstance(mid_embedding, np.ndarray) and mid_embedding.size > 0 and not np.all(mid_embedding == 0):
                    embeddings_to_combine.append(mid_embedding)
                    samples_successful += 1
                    logging.debug(f"✅ Muestra intermedia {i+1} procesada correctamente")
                else:
                    logging.warning(f"⚠️ La muestra intermedia {i+1} no generó un embedding válido")
            except Exception as e:
                logging.error(f"Error al procesar muestra intermedia {i+1}: {e}")
        
        # Procesar final
        if end_content:
            samples_attempted += 1
            try:
                end_embedding = self._get_embedding(end_content)
                if isinstance(end_embedding, np.ndarray) and end_embedding.size > 0 and not np.all(end_embedding == 0):
                    embeddings_to_combine.append(end_embedding)
                    samples_successful += 1
                    logging.debug(f"✅ Muestra de final procesada correctamente")
                else:
                    logging.warning(f"⚠️ La muestra de final no generó un embedding válido")
            except Exception as e:
                logging.error(f"Error al procesar muestra de final: {e}")
        
        # 3. Combinar los embeddings si hay al menos uno válido
        if embeddings_to_combine:
            try:
                combined_embedding = np.mean(embeddings_to_combine, axis=0)
                # Normalizar para mantener las propiedades del espacio de embeddings
                if norm(combined_embedding) > 0:
                    combined_embedding = combined_embedding / norm(combined_embedding)
                logging.info(f"✅ Embedding combinado generado de {samples_successful}/{samples_attempted} muestras exitosas")
                return combined_embedding
            except Exception as e:
                logging.error(f"Error al combinar embeddings de muestras: {e}")
                return np.zeros((1536,), dtype=float)
        else:
            logging.warning(f"⚠️ No se pudo generar ningún embedding válido de las muestras del archivo")
            return np.zeros((1536,), dtype=float)

    def _load_code_examples(self) -> List[Dict[str, str]]:
        """Carga ejemplos de código para la plataforma seleccionada."""
        examples_dir = Path(EXAMPLE_DIR_TEMPLATE.format(platform=self.platform))
        logging.info(f"📚 Cargando ejemplos de código para {self.platform.upper().replace('_', ' ')}...")
        
        examples = []
        
        # Intentar cargar el caché de embeddings
        embeddings_cache = self._load_embeddings_cache()
        
        # Buscar recursivamente en todas las carpetas
        all_c_files = list(examples_dir.rglob('*.c'))
        if not all_c_files:
            logging.warning(f"⚠️ No se encontraron archivos .c en {examples_dir}")
            return examples
        
        # Límite para archivos de ejemplo extremadamente grandes (cargado de la configuración)
        # MAX_EXAMPLE_SIZE se inicializa en _init_global_variables
        
        # Calcular el número aproximado de tokens
        estimated_max_tokens = self._estimate_tokens(MAX_EXAMPLE_SIZE)
        logging.info(f"Tamaño máximo de ejemplo: {MAX_EXAMPLE_SIZE} caracteres (~{estimated_max_tokens} tokens)")
        
        # Cargar contenido de archivos y generar embeddings si es necesario
        need_to_update_cache = False
        for file_path in all_c_files:
            rel_path = str(file_path.relative_to(examples_dir))
            
            # Verificar si necesitamos procesar este archivo
            # Lo hacemos si: no está en caché O si está en caché pero se fuerza truncado
            if rel_path not in embeddings_cache or self.force_truncate:
                # Cargar el archivo fresco
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Truncar ejemplos extremadamente grandes
                    original_size = len(content)
                    estimated_tokens = self._estimate_tokens(content)
                    
                    if original_size > MAX_EXAMPLE_SIZE:
                        # Estrategia de truncado: mantener inicio y final
                        first_part_size = int(MAX_EXAMPLE_SIZE * 0.7)  # 70% para el inicio
                        last_part_size = MAX_EXAMPLE_SIZE - first_part_size  # 30% para el final
                        
                        first_part = content[:first_part_size]
                        last_part = content[-last_part_size:] if last_part_size > 0 else ""
                        
                        # Mensaje de truncación
                        truncation_msg = f"\n/* ... CONTENIDO TRUNCADO ({original_size - MAX_EXAMPLE_SIZE} caracteres) ... */\n"
                        
                        # Combinar las partes
                        content = first_part + truncation_msg + last_part
                        
                        logging.warning(f"⚠️ Ejemplo truncado: {rel_path} ({original_size} -> {len(content)} caracteres)")
                        logging.warning(f"   Tokens estimados: {estimated_tokens} -> {self._estimate_tokens(content)}")
                    
                    # Actualizar caché o añadir nueva entrada
                    embeddings_cache[rel_path] = (content, None)  # Embedding a None para regenerarlo después
                    examples.append({"path": rel_path, "content": content})
                    need_to_update_cache = True
                    
                    if self.force_truncate and rel_path in embeddings_cache:
                        logging.info(f"🔄 Ejemplo recargado y truncado (forzado): {rel_path}")
                    
                except Exception as e:
                    logging.warning(f"Error al cargar ejemplo {file_path}: {e}")
            else:
                # El archivo ya está en la caché, usar su contenido y embedding
                content, _ = embeddings_cache[rel_path]
                examples.append({"path": rel_path, "content": content})
        
        # Generar embeddings para archivos nuevos o modificados
        if need_to_update_cache:
            logging.info("Generando embeddings para nuevos archivos...")
            success_count = 0
            error_count = 0
            
            for rel_path, (content, embedding) in list(embeddings_cache.items()):
                if embedding is None:
                    # Añadir una pequeña pausa para evitar rate limits en la API
                    time.sleep(0.25)  # Pausa más larga para evitar problemas de rate limiting
                    try:
                        # Para archivos extremadamente grandes, usar estrategia adaptativa
                        if len(content) > MAX_EXAMPLE_SIZE * 1.5:
                            logging.warning(f"Archivo extremadamente grande ({len(content)} caracteres) en generación de embeddings. Usando estrategia adaptativa.")
                            new_embedding = self._get_embedding_for_large_file(content)
                        else:
                            # Para archivos de tamaño normal, generar embedding directamente
                            new_embedding = self._get_embedding(content)
                            
                        embeddings_cache[rel_path] = (content, new_embedding)
                        success_count += 1
                    except Exception as e:
                        logging.error(f"Error al generar embedding para {rel_path}: {e}")
                        error_count += 1
            
            logging.info(f"Embeddings generados: {success_count} exitosos, {error_count} con error")
            
            # Guardar el caché actualizado
            self._save_embeddings_cache(embeddings_cache)
        
        logging.info(f"✅ {len(examples)} ejemplos cargados para búsqueda semántica.")
        # Guardar el caché de embeddings para uso posterior
        self.embeddings_cache = embeddings_cache
        return examples

    def _get_relevant_examples(self, user_request: str, max_examples: int = None) -> List[Dict[str, str]]:
        """Obtiene los ejemplos más relevantes para la solicitud del usuario."""
        if max_examples is None:
            max_examples = self.max_examples
        
        if not hasattr(self, 'embeddings_cache') or not self.embeddings_cache:
            logging.warning("No hay caché de embeddings disponible para búsqueda semántica.")
            # Cargar todos los ejemplos como respaldo
            examples = self._load_code_examples()
            return examples[:max_examples]
        
        logging.info(f"🔍 Buscando {max_examples} ejemplos relevantes para la solicitud...")
        
        # Obtener embedding para la solicitud del usuario
        query_embedding = self._get_embedding(user_request)
        
        # Verificar que el embedding sea válido
        if not isinstance(query_embedding, np.ndarray) or query_embedding.size == 0 or np.all(query_embedding == 0):
            logging.warning("❌ No se pudo generar un embedding válido para la consulta. Usando ejemplos aleatorios.")
            # Si no tenemos un embedding válido para la consulta, devolver algunos ejemplos de forma aleatoria
            all_examples = []
            for rel_path, (content, _) in self.embeddings_cache.items():
                all_examples.append({"path": rel_path, "content": content})
            
            # Limitar a la cantidad solicitada
            random.shuffle(all_examples)
            return all_examples[:max_examples]
        
        # Calcular similitud con todos los ejemplos
        similarities = []
        valid_embeddings_count = 0
        invalid_embeddings_count = 0
        
        for rel_path, (content, embedding) in self.embeddings_cache.items():
            # Verificar que el embedding sea válido
            if (embedding is not None and 
                isinstance(embedding, np.ndarray) and 
                embedding.size > 0 and 
                not np.all(embedding == 0)):
                try:
                    similarity = self._cosine_similarity(query_embedding, embedding)
                    similarities.append((rel_path, content, similarity))
                    valid_embeddings_count += 1
                except Exception as e:
                    logging.warning(f"Error al calcular similitud para {rel_path}: {e}")
                    invalid_embeddings_count += 1
            else:
                invalid_embeddings_count += 1
                # No lo incluimos para cálculo de similitud
        
        if invalid_embeddings_count > 0:
            logging.warning(f"Se ignoraron {invalid_embeddings_count} embeddings inválidos o nulos.")
        
        if not similarities:
            logging.warning("❌ No se encontraron embeddings válidos para comparar. Usando ejemplos aleatorios.")
            # Si no hay embeddings válidos, devolver algunos ejemplos de forma aleatoria
            all_examples = []
            for rel_path, (content, _) in self.embeddings_cache.items():
                all_examples.append({"path": rel_path, "content": content})
            
            # Limitar a la cantidad solicitada
            random.shuffle(all_examples)
            return all_examples[:max_examples]
        
        # Ordenar por similitud descendente
        similarities.sort(key=lambda x: x[2], reverse=True)
        
        # Tomar los N ejemplos más relevantes
        relevant_examples = []
        for rel_path, content, similarity in similarities[:max_examples]:
            logging.debug(f"Ejemplo relevante: {rel_path} (similitud: {similarity:.4f})")
            relevant_examples.append({"path": rel_path, "content": content})
        
        logging.info(f"✅ Se encontraron {len(relevant_examples)} ejemplos relevantes (de {valid_embeddings_count} válidos).")
        return relevant_examples

    def _load_error_documentation(self) -> str:
        """Loads error documentation (*.md) recursively from the examples directory."""
        examples_dir = Path(EXAMPLE_DIR_TEMPLATE.format(platform=self.platform))
        logging.info(f"📚 Loading error documentation from {examples_dir}...")
        docs_content = ""

        if not examples_dir.is_dir():
            logging.warning(f"⚠️ Example directory not found for error docs: {examples_dir}")
            return docs_content

        md_files = list(examples_dir.rglob(ERROR_DOC_GLOB_PATTERN))

        if not md_files:
            logging.info("ℹ️ No error documentation (.md) files found.")
            return docs_content

        logging.info(f"Found {len(md_files)} documentation files.")
        for md_file in md_files:
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                    relative_path = md_file.relative_to(examples_dir)
                    docs_content += f"\n\n--- DOCUMENTATION: {relative_path} ---\n\n"
                    docs_content += file_content
                    logging.debug(f"  Loaded doc: {relative_path}")
            except Exception as e:
                logging.error(f"❌ Error loading documentation {md_file}: {e}")

        logging.info(f"✅ Error documentation loaded ({len(docs_content)} chars).")
        return docs_content

    def _load_platform_instructions(self) -> str:
        """Loads platform-specific instructions from the system prompt file."""
        # La variable global SYSTEM_PROMPT_FILE_TEMPLATE ya contiene la ruta correcta según la plataforma
        logging.info(f"📚 Loading platform instructions from {SYSTEM_PROMPT_FILE_TEMPLATE}...")
        content = ""
        try:
            if os.path.exists(SYSTEM_PROMPT_FILE_TEMPLATE):
                with open(SYSTEM_PROMPT_FILE_TEMPLATE, 'r', encoding='utf-8') as f:
                    content = f.read()
                logging.info(f"✅ Platform instructions loaded ({len(content)} chars).")
            else:
                logging.warning(f"⚠️ Platform instruction file not found: {SYSTEM_PROMPT_FILE_TEMPLATE}")
        except Exception as e:
            logging.error(f"❌ Error reading platform instructions from {SYSTEM_PROMPT_FILE_TEMPLATE}: {e}")
        return content

    def _build_system_prompt(self, relevant_examples: List[Dict[str, str]] = None) -> str:
        """Constructs the full system prompt incorporating base instructions, examples, and docs."""
        logging.debug("Building system prompt...")

        # 1. Base Instructions
        if self.platform == 'spectrum':
            base_prompt = """You are an expert Z88DK C code generator for ZX Spectrum 48K.
CRITICAL: Output ONLY the raw C source code. No introductory text, no explanations, no markdown fences (```), just the code itself.
Ensure the code is complete, directly compilable with 'zcc +zx', and functional on a ZX Spectrum 48K.
Adhere strictly to Z88DK's C dialect and library functions suitable for the Spectrum.
Prioritize clarity, efficiency for the Z80, and correct hardware interaction (screen, keyboard, sound if applicable).
"""
        elif self.platform == 'amstrad_cpc':
            base_prompt = """You are an expert CPCtelera C code generator for Amstrad CPC 464/6128.
CRITICAL: Output ONLY the raw C source code. No introductory text, no explanations, no markdown fences (```), just the code itself.
Ensure the code is complete, directly compilable with the CPCtelera toolchain, and functional on an Amstrad CPC.
Adhere strictly to the CPCtelera API and best practices. Do NOT use generic Z88DK functions unless they are part of the official CPCtelera API.
Prioritize clarity, efficiency for the Z80, static memory management, and correct hardware interaction using CPCtelera functions (graphics modes, keyboard, sound, etc.).
"""
        else:
            # Fallback - Consider raising an error for unsupported platforms
            logging.error(f"❌ Unsupported platform for system prompt: {self.platform}")
            raise ValueError(f"Unsupported platform: {self.platform}")

        # 2. Platform-Specific Instructions from File
        platform_instructions = self._load_platform_instructions()

        # 3. Code Examples
        examples_prompt_part = "\n--- CODE EXAMPLES ---\n"
        examples_prompt_part += "Use the following examples as a reference for style, structure, and API usage:\n"
        
        # Usar los ejemplos relevantes proporcionados o cargar todos si no se proporcionan
        if relevant_examples is None:
            # Nota: Ahora no cargamos todos, pero utilizamos el método para obtener los relevantes
            all_examples = self._load_code_examples()
            examples_to_use = all_examples[:self.max_examples]
        else:
            examples_to_use = relevant_examples

        # Añadir ejemplos al prompt
        for i, example in enumerate(examples_to_use):
            examples_prompt_part += f"\nExample {i+1} ('{example['path']}'):\n"
            examples_prompt_part += f"```c\n{example['content']}\n```\n"
        
        # 4. Error Documentation
        error_docs = self._load_error_documentation()

        # 5. Combine all parts
        full_system_prompt = base_prompt
        if platform_instructions:
             full_system_prompt += "\n--- PLATFORM INSTRUCTIONS ---\n" + platform_instructions
        if examples_to_use:
            full_system_prompt += examples_prompt_part
        if error_docs:
            # Append error docs (already contains header)
            full_system_prompt += error_docs
        # Final reminder
        full_system_prompt += "\n--- FINAL INSTRUCTIONS ---\nRemember: ONLY output the raw C code. No extra text or markdown."

        logging.debug(f"System prompt built ({len(full_system_prompt)} chars).")
        return full_system_prompt

    def _build_user_prompt(self, user_request: str) -> str:
        """Constructs the user prompt."""
        # Keep it simple, as most context is in the system prompt
        platform_name = self.platform.replace('_', ' ')
        return f"Generate {platform_name} C code according to the system instructions that does the following: {user_request}"

    def _clean_api_response(self, raw_response: str) -> str:
        """Attempts to extract only the C code from the API response."""
        logging.debug("Cleaning API response...")
        code = raw_response.strip()

        # Attempt 1: Regex for markdown code blocks (non-greedy)
        match = re.search(r'```(?:c)?\n(.*?)\n```', code, re.DOTALL | re.IGNORECASE)
        if match:
            extracted_code = match.group(1).strip()
            logging.info("✅ Extracted code using markdown regex.")
            return extracted_code

        # Attempt 2: If no markdown, assume the whole response might be code,
        # but try to remove common introductory/closing phrases.
        # This is less reliable.
        logging.warning("⚠️ Could not find markdown code block. Attempting basic cleaning.")
        lines = code.splitlines()
        # Remove potential leading/trailing explanation lines (heuristic)
        if lines:
            if "here is the c code" in lines[0].lower() or "```" in lines[0]:
                lines.pop(0)
        if lines:
            if "```" in lines[-1]:
                lines.pop(-1)

        cleaned_code = "\n".join(lines).strip()
        if len(cleaned_code) < 0.5 * len(raw_response): # Arbitrary threshold
             logging.warning("⚠️ Basic cleaning significantly reduced content length. Result might be incomplete.")
        elif not cleaned_code:
             logging.warning("⚠️ Cleaning resulted in empty code.")

        return cleaned_code if cleaned_code else raw_response # Return original if cleaning failed badly

    def _clear_embeddings_cache(self) -> None:
        """Elimina el caché de embeddings para la plataforma actual."""
        cache_file = EMBEDDINGS_CACHE_DIR / f"{self.platform}_embeddings.json"
        try:
            if cache_file.exists():
                cache_file.unlink()
                logging.info(f"✅ Caché de embeddings eliminado: {cache_file}")
            else:
                logging.info(f"No existe archivo de caché para eliminar: {cache_file}")
        except Exception as e:
            logging.error(f"Error al eliminar el caché de embeddings: {e}")

    def generate_c_code(self, user_request: str) -> str:
        """Generates C code using the OpenAI API based on the user request and context."""
        logging.info(f"🤖 Generating code for: '{user_request[:100]}...'")

        # Obtener ejemplos según el modo de operación (con o sin embeddings)
        if self.use_embeddings:
            # Modo con embeddings (búsqueda semántica)
            try:
                # Cargar ejemplos de código si aún no se han cargado
                if not hasattr(self, 'embeddings_cache'):
                    self._load_code_examples()
                
                # Obtener ejemplos relevantes para la solicitud del usuario
                relevant_examples = self._get_relevant_examples(user_request)
                logging.info(f"Usando búsqueda semántica con embeddings para seleccionar ejemplos.")
            except TypeError as e:
                # Error específico para cuando se intenta usar len() en un objeto que no lo soporta
                if "object of type 'int' has no len()" in str(e):
                    logging.error(f"Error en la búsqueda semántica: {e}")
                    logging.warning("Error típico con embeddings mal formados. Cambiando a modo sin embeddings.")
                    # Deshabilitar embeddings para futuras llamadas
                    self.use_embeddings = False
                    # Fallback a modo sin embeddings
                    all_examples = self._load_code_examples_basic()
                    relevant_examples = all_examples[:self.max_examples]
                else:
                    # Otro tipo de TypeError
                    raise
            except Exception as e:
                logging.error(f"Error en la búsqueda semántica: {e}")
                logging.warning("Fallback a modo sin embeddings debido a error.")
                # Si hay error, fallback a modo sin embeddings
                all_examples = self._load_code_examples_basic()
                relevant_examples = all_examples[:self.max_examples]
        else:
            # Modo sin embeddings (más simple y directo)
            logging.info(f"Usando selección básica de ejemplos (sin búsqueda semántica).")
            all_examples = self._load_code_examples_basic()
            relevant_examples = all_examples[:self.max_examples]
        
        # Construir el prompt del sistema con los ejemplos seleccionados
        system_prompt = self._build_system_prompt(relevant_examples)
        user_prompt = self._build_user_prompt(user_request)

        # Log prompts for debugging (optional, consider security/privacy)
        # logging.debug(f"System Prompt:\n{system_prompt}")
        # logging.debug(f"User Prompt:\n{user_prompt}")

        try:
            logging.info(f"📞 Calling OpenAI API (Model: {self.model})...")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            raw_code = response.choices[0].message.content
            logging.info("✅ API call successful.")
            #logging.debug(f"Raw API response:\n{raw_code}") # Log raw response if needed

            cleaned_code = self._clean_api_response(raw_code)
            logging.info("✨ Code generation complete.")
            return cleaned_code

        except Exception as e:
            logging.error(f"❌ Error during OpenAI API call or processing: {e}")
            # Consider more specific error handling for API errors (e.g., rate limits, auth)
            raise # Re-raise to indicate failure

    def save_generated_files(self, code: str, prompt: str, paths: Dict[str, Path]) -> None:
        """Saves the generated C code, original prompt, and platform info."""
        logging.info("💾 Saving generated files...")
        try:
            # Ensure base and obj directories exist
            paths['base'].mkdir(parents=True, exist_ok=True)
            paths['obj_dir'].mkdir(exist_ok=True) # obj_dir should be under base

            # Save C code
            with open(paths['c_file'], 'w', encoding='utf-8') as f:
                f.write(code)
            logging.info(f"  📄 C code saved to: {paths['c_file']}")

            # Save original prompt
            with open(paths['prompt_file'], 'w', encoding='utf-8') as f:
                f.write(prompt)
            logging.info(f"  📝 Prompt saved to: {paths['prompt_file']}")

            # Save platform info
            with open(paths['platform_file'], 'w', encoding='utf-8') as f:
                f.write(self.platform)
            logging.info(f"  ℹ️ Platform info saved to: {paths['platform_file']}")

            logging.info("✅ All files saved successfully!")
            logging.info(f"  📁 Output Directory: {paths['base'].resolve()}")
            logging.info(f"  🛠️  Build/Object Directory: {paths['obj_dir'].resolve()}")


        except Exception as e:
            logging.error(f"❌ Failed to save files: {e}")
            raise # Re-raise to indicate failure

    def _init_global_variables(self):
        """Inicializa las variables globales desde la configuración."""
        global LOG_DIR, BASE_OUTPUT_DIR, SYSTEM_PROMPT_FILE_TEMPLATE, EMBEDDINGS_CACHE_DIR
        global MAX_EXAMPLE_SIZE, MAX_CHUNK_SIZE, SLUG_MAX_LENGTH, TOKEN_LIMIT, SAFETY_MARGIN
        
        # Configuración de logging
        log_dir_str = self.config.get('logging', {}).get('log_dir', 'local/logs')
        LOG_DIR = Path(log_dir_str)
        
        # Configuración de directorios de salida
        base_dir_str = self.config.get('output', {}).get('base_dir', 'local')
        BASE_OUTPUT_DIR = Path(base_dir_str)
        
        # Configuración de archivos de prompt
        prompt_files = self.config.get('prompt_files', {})
        spectrum_prompt = prompt_files.get('spectrum', 'system_prompt_spectrum.txt')
        amstrad_prompt = prompt_files.get('amstrad_cpc', 'system_prompt_amstrad_cpc.txt')
        
        # Decidir qué plantilla usar según la plataforma
        if self.platform == 'spectrum':
            SYSTEM_PROMPT_FILE_TEMPLATE = spectrum_prompt
        else:
            SYSTEM_PROMPT_FILE_TEMPLATE = amstrad_prompt
        
        # Configuración de embeddings
        embeddings_config = self.config.get('embeddings', {})
        cache_dir_str = embeddings_config.get('cache_dir', 'local/embeddings')
        EMBEDDINGS_CACHE_DIR = Path(cache_dir_str)
        MAX_CHUNK_SIZE = embeddings_config.get('max_chunk_size', 15000)
        TOKEN_LIMIT = embeddings_config.get('token_limit', 8000)
        SAFETY_MARGIN = embeddings_config.get('safety_margin', 0.8)
        
        # Configuración de ejemplos
        examples_config = self.config.get('examples', {})
        MAX_EXAMPLE_SIZE = examples_config.get('truncate_size', 50000)
        
        # Configuración de slug
        SLUG_MAX_LENGTH = self.config.get('output', {}).get('slug_max_length', 40)
        
        # Crear directorios necesarios
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        EMBEDDINGS_CACHE_DIR.mkdir(parents=True, exist_ok=True)

    def _load_code_examples_basic(self) -> List[Dict[str, str]]:
        """Carga ejemplos de código de manera básica sin usar embeddings."""
        examples_dir = Path(EXAMPLE_DIR_TEMPLATE.format(platform=self.platform))
        logging.info(f"📚 Cargando ejemplos de código básicos para {self.platform.upper().replace('_', ' ')}...")
        
        examples = []
        
        # Buscar recursivamente en todas las carpetas
        all_c_files = list(examples_dir.rglob('*.c'))
        if not all_c_files:
            logging.warning(f"⚠️ No se encontraron archivos .c en {examples_dir}")
            return examples
            
        # Si hay demasiados archivos, toma una muestra aleatoria para mayor diversidad
        if len(all_c_files) > self.max_examples * 3:
            random.shuffle(all_c_files)
            all_c_files = all_c_files[:self.max_examples * 3]
        
        # Cargar contenido de archivos
        for file_path in all_c_files:
            rel_path = str(file_path.relative_to(examples_dir))
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Truncar ejemplos extremadamente grandes
                original_size = len(content)
                
                if original_size > MAX_EXAMPLE_SIZE:
                    # Estrategia de truncado
                    first_part_size = int(MAX_EXAMPLE_SIZE * 0.7)
                    last_part_size = MAX_EXAMPLE_SIZE - first_part_size
                    
                    first_part = content[:first_part_size]
                    last_part = content[-last_part_size:] if last_part_size > 0 else ""
                    
                    truncation_msg = f"\n/* ... CONTENIDO TRUNCADO ({original_size - MAX_EXAMPLE_SIZE} caracteres) ... */\n"
                    content = first_part + truncation_msg + last_part
                    
                    logging.info(f"⚠️ Ejemplo truncado: {rel_path} ({original_size} -> {len(content)} caracteres)")
                
                examples.append({"path": rel_path, "content": content})
                
            except Exception as e:
                logging.warning(f"Error al cargar ejemplo {file_path}: {e}")
        
        logging.info(f"✅ {len(examples)} ejemplos básicos cargados.")
        
        # Ordenar por tamaño para tomar una muestra variada
        examples.sort(key=lambda x: len(x["content"]))
        
        # Tomar ejemplos variados: algunos pequeños, medianos y grandes
        result = []
        step = max(1, len(examples) // self.max_examples)
        for i in range(0, len(examples), step):
            if len(result) < self.max_examples:
                result.append(examples[i])
        
        return result

    def _verify_and_repair_cache(self) -> None:
        """Verifica el estado del caché de embeddings y lo repara si es necesario."""
        cache_file = EMBEDDINGS_CACHE_DIR / f"{self.platform}_embeddings.json"
        backup_file = EMBEDDINGS_CACHE_DIR / f"{self.platform}_embeddings_backup.json"
        
        if not cache_file.exists():
            logging.info(f"No hay caché para verificar: {cache_file}")
            return
            
        try:
            # Intentar cargar el caché para verificarlo
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
                
            # Verificar estructura básica (debe ser un diccionario)
            if not isinstance(cache_data, dict):
                raise ValueError("El caché no es un diccionario JSON válido")
                
            # Verificar cada entrada
            valid_entries = {}
            invalid_count = 0
            
            for file_path, data_tuple in cache_data.items():
                if not isinstance(file_path, str):
                    invalid_count += 1
                    continue
                    
                # Verificar que data_tuple sea una lista/tupla de 2 elementos
                if not isinstance(data_tuple, (list, tuple)) or len(data_tuple) != 2:
                    invalid_count += 1
                    continue
                    
                content, embedding = data_tuple
                
                # Verificar contenido
                if not isinstance(content, str):
                    invalid_count += 1
                    continue
                    
                # Verificar embedding (si no es None)
                if embedding is not None:
                    if not isinstance(embedding, list):
                        # Marcar para regeneración
                        valid_entries[file_path] = (content, None)
                        invalid_count += 1
                    else:
                        # Verificar que todos los elementos sean números
                        if all(isinstance(x, (int, float)) for x in embedding):
                            valid_entries[file_path] = (content, embedding)
                        else:
                            valid_entries[file_path] = (content, None)
                            invalid_count += 1
                else:
                    # Mantener entradas con embedding None
                    valid_entries[file_path] = (content, None)
            
            # Si hay entradas inválidas, hacer backup y guardar la versión reparada
            if invalid_count > 0:
                logging.warning(f"Se encontraron {invalid_count} entradas inválidas en el caché.")
                
                # Hacer backup del caché original
                if cache_file.exists():
                    # Crear directorio de backup si no existe
                    EMBEDDINGS_CACHE_DIR.mkdir(parents=True, exist_ok=True)
                    # Copiar archivo actual a backup
                    import shutil
                    shutil.copy2(cache_file, backup_file)
                    logging.info(f"Backup guardado en {backup_file}")
                
                # Guardar versión reparada
                with open(cache_file, 'w') as f:
                    json.dump(valid_entries, f)
                    
                logging.info(f"✅ Caché reparado y guardado en {cache_file}")
            else:
                logging.info(f"✅ Caché verificado sin problemas: {len(valid_entries)} entradas válidas.")
                
        except json.JSONDecodeError:
            logging.error(f"El archivo de caché {cache_file} está corrupto y no puede ser decodificado como JSON.")
            
            # Hacer backup del caché corrupto
            if cache_file.exists():
                import shutil
                EMBEDDINGS_CACHE_DIR.mkdir(parents=True, exist_ok=True)
                # Añadir timestamp al nombre para evitar sobrescribir backups anteriores
                corrupted_backup = EMBEDDINGS_CACHE_DIR / f"{self.platform}_embeddings_corrupted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                shutil.copy2(cache_file, corrupted_backup)
                logging.info(f"Backup del caché corrupto guardado en {corrupted_backup}")
                
                # Borrar el caché corrupto
                cache_file.unlink()
                logging.info(f"Caché corrupto eliminado. Se creará uno nuevo en la próxima ejecución.")
        except Exception as e:
            logging.error(f"Error al verificar el caché: {e}")

    def _rebuild_embeddings_cache(self) -> None:
        """Elimina y reconstruye completamente el caché de embeddings."""
        cache_file = EMBEDDINGS_CACHE_DIR / f"{self.platform}_embeddings.json"
        
        # 1. Primero eliminar el caché si existe
        try:
            if cache_file.exists():
                cache_file.unlink()
                logging.info(f"✅ Caché de embeddings eliminado: {cache_file}")
            else:
                logging.info(f"No existe archivo de caché para eliminar: {cache_file}")
        except Exception as e:
            logging.error(f"Error al eliminar el caché de embeddings: {e}")
        
        # 2. Inicializar un caché vacío
        embeddings_cache = {}
        
        # 3. Cargar todos los archivos de ejemplo
        examples_dir = Path(EXAMPLE_DIR_TEMPLATE.format(platform=self.platform))
        logging.info(f"🔄 Reconstruyendo caché de embeddings para {self.platform.upper().replace('_', ' ')}...")
        
        # Buscar recursivamente en todas las carpetas
        all_c_files = list(examples_dir.rglob('*.c'))
        if not all_c_files:
            logging.warning(f"⚠️ No se encontraron archivos .c en {examples_dir}")
            return
            
        # 4. Procesar cada archivo
        total_files = len(all_c_files)
        success_count = 0
        error_count = 0
        
        for i, file_path in enumerate(all_c_files):
            rel_path = str(file_path.relative_to(examples_dir))
            logging.info(f"Procesando archivo {i+1}/{total_files}: {rel_path}")
            
            try:
                # Cargar contenido del archivo
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Truncar ejemplos extremadamente grandes
                original_size = len(content)
                
                if original_size > MAX_EXAMPLE_SIZE:
                    # Estrategia de truncado
                    first_part_size = int(MAX_EXAMPLE_SIZE * 0.7)
                    last_part_size = MAX_EXAMPLE_SIZE - first_part_size
                    
                    first_part = content[:first_part_size]
                    last_part = content[-last_part_size:] if last_part_size > 0 else ""
                    
                    truncation_msg = f"\n/* ... CONTENIDO TRUNCADO ({original_size - MAX_EXAMPLE_SIZE} caracteres) ... */\n"
                    content = first_part + truncation_msg + last_part
                    
                    logging.info(f"⚠️ Ejemplo truncado: {rel_path} ({original_size} -> {len(content)} caracteres)")
                
                # Generar embedding
                logging.info(f"Generando embedding para {rel_path}...")
                try:
                    # Para archivos extremadamente grandes, usar la estrategia adaptativa
                    if len(content) > MAX_EXAMPLE_SIZE * 1.5:
                        logging.warning(f"Archivo extremadamente grande ({len(content)} caracteres). Usando estrategia adaptativa.")
                        embedding = self._get_embedding_for_large_file(content)
                    else:
                        # Para archivos de tamaño normal, generar embedding directamente
                        embedding = self._get_embedding(content)
                except Exception as e:
                    logging.error(f"Error al generar embedding para {rel_path}: {e}")
                    embedding = None
                
                # Verificar que el embedding sea válido
                if isinstance(embedding, np.ndarray) and embedding.size > 0 and not np.all(embedding == 0):
                    embeddings_cache[rel_path] = (content, embedding)
                    logging.info(f"✅ Embedding generado correctamente para {rel_path}")
                    success_count += 1
                else:
                    embeddings_cache[rel_path] = (content, None)
                    logging.warning(f"⚠️ No se pudo generar un embedding válido para {rel_path}")
                    error_count += 1
                
                # Añadir una pequeña pausa para evitar rate limits
                time.sleep(0.25)
                
            except Exception as e:
                logging.error(f"Error al procesar {file_path}: {e}")
                error_count += 1
        
        # 5. Guardar el caché reconstruido
        self._save_embeddings_cache(embeddings_cache)
        
        logging.info(f"✅ Reconstrucción de caché completada: {success_count} exitosos, {error_count} con error")
        self.embeddings_cache = embeddings_cache

    def _test_file_embedding(self, file_path: str) -> None:
        """Prueba la generación de embeddings para un archivo específico.
        
        Args:
            file_path: Ruta al archivo a probar
        """
        try:
            # Verificar que el archivo existe
            if not os.path.exists(file_path):
                logging.error(f"⚠️ El archivo {file_path} no existe")
                return
                
            logging.info(f"🧪 Probando generación de embedding para archivo: {file_path}")
            
            # Cargar contenido del archivo
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Mostrar info del archivo
            file_size = len(content)
            estimated_tokens = self._estimate_tokens(content)
            logging.info(f"📄 Tamaño del archivo: {file_size} caracteres (~{estimated_tokens} tokens estimados)")
            
            # Primero intentar con el método estándar
            logging.info("🔄 Intentando método estándar de embedding...")
            try:
                start_time = time.time()
                embedding = self._get_embedding(content)
                elapsed = time.time() - start_time
                
                if isinstance(embedding, np.ndarray) and embedding.size > 0 and not np.all(embedding == 0):
                    logging.info(f"✅ Embedding generado correctamente con método estándar en {elapsed:.2f} segundos")
                    logging.info(f"   Dimensiones: {embedding.shape}, Norma: {norm(embedding):.4f}")
                else:
                    logging.warning(f"⚠️ El método estándar no generó un embedding válido")
            except Exception as e:
                logging.error(f"❌ Error al generar embedding con método estándar: {e}")
                
            # Luego intentar con el método para archivos grandes
            logging.info("🔄 Intentando método para archivos grandes...")
            try:
                start_time = time.time()
                large_embedding = self._get_embedding_for_large_file(content)
                elapsed = time.time() - start_time
                
                if isinstance(large_embedding, np.ndarray) and large_embedding.size > 0 and not np.all(large_embedding == 0):
                    logging.info(f"✅ Embedding generado correctamente con método para archivos grandes en {elapsed:.2f} segundos")
                    logging.info(f"   Dimensiones: {large_embedding.shape}, Norma: {norm(large_embedding):.4f}")
                else:
                    logging.warning(f"⚠️ El método para archivos grandes no generó un embedding válido")
            except Exception as e:
                logging.error(f"❌ Error al generar embedding con método para archivos grandes: {e}")
                
            logging.info("🏁 Prueba de generación de embedding completada")
            
        except Exception as e:
            logging.error(f"❌ Error al probar el archivo {file_path}: {e}")

# --- Main Execution ---
def main():
    parser = argparse.ArgumentParser(
        description='LLMZ80 Code Generator - Generates C code for Z80 platforms using OpenAI.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter # Show defaults in help
        )
    parser.add_argument('--platform', type=str, default='spectrum',
                        choices=['spectrum', 'amstrad_cpc'],
                        help='Target platform.')
    parser.add_argument('--prompt', type=str, default=None,
                        help='Prompt for code generation (if omitted, will ask interactively).')
    parser.add_argument('--config', type=str, default=CONFIG_FILE,
                        help='Path to the configuration YAML file.')
    # Add log level argument
    parser.add_argument('--log-level', type=str, default=DEFAULT_LOG_LEVEL,
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                        help='Set the console logging level.')
    # Add cache control arguments
    parser.add_argument('--clear-cache', action='store_true',
                        help='Clear the embeddings cache before running.')
    parser.add_argument('--force-truncate', action='store_true',
                        help='Force truncation of all examples, even those already in cache.')
    parser.add_argument('--no-embeddings', action='store_true',
                        help='Skip embeddings and semantic search (faster, but less relevant examples).')
    parser.add_argument('--repair-cache', action='store_true',
                        help='Verify and repair corrupted embeddings cache.')
    parser.add_argument('--rebuild-embeddings', action='store_true',
                        help='Elimina y reconstruye completamente el caché de embeddings.')
    parser.add_argument('--test-file', type=str,
                        help='Prueba la generación de embeddings para un archivo específico.')
    parser.add_argument('--max-chunk-size', type=int,
                        help='Define el tamaño máximo de chunk para embeddings (reemplaza valor en config.yml).')

    args = parser.parse_args()

    platform_name = args.platform.upper().replace('_', ' ')
    print(colored(f"\n🎮 Welcome to the {platform_name} Code Generator 🎮", "green", attrs=['bold']))
    print(colored("=" * (len(platform_name) + 24), "green"))

    try:
        # Update log level based on argument *before* initializing generator if possible
        # (This requires adjusting setup_logging or passing level to __init__)
        # Simplified: Initialize then potentially reconfigure logger level if needed
        # Or, better: read log level from args *before* basicConfig in _setup_logging
        # Let's stick to the current flow for now, config file takes precedence after init.

        generator = LLMZ80Generator(platform=args.platform, config_path=args.config)

        # Override log level from args if specified (after initial setup)
        log_level_arg = getattr(logging, args.log_level.upper(), logging.INFO)
        logging.getLogger().setLevel(log_level_arg) # Set level for root logger
        logging.info(f"Console log level set to: {args.log_level.upper()}")
        
        # Aplicar tamaño máximo de chunk si se especifica
        if args.max_chunk_size:
            global MAX_CHUNK_SIZE
            MAX_CHUNK_SIZE = args.max_chunk_size
            logging.info(f"Tamaño máximo de chunk establecido a {MAX_CHUNK_SIZE} caracteres")
        
        # Limpiar caché si se solicita
        if args.clear_cache:
            try:
                generator._clear_embeddings_cache()
                logging.info("Caché de embeddings eliminado. Se generarán nuevos embeddings.")
            except Exception as e:
                logging.error(f"Error al limpiar caché de embeddings: {e}")
                # Continuamos a pesar del error
        
        # Reparar caché de embeddings si se solicita
        if args.repair_cache:
            try:
                generator._verify_and_repair_cache()
                logging.info("Verificación y reparación de caché completada.")
            except Exception as e:
                logging.error(f"Error al reparar caché de embeddings: {e}")
                # Continuamos a pesar del error
        
        # Reconstruir completamente el caché de embeddings si se solicita
        if args.rebuild_embeddings:
            try:
                generator._rebuild_embeddings_cache()
                logging.info("Reconstrucción completa de caché de embeddings terminada.")
            except Exception as e:
                logging.error(f"Error al reconstruir caché de embeddings: {e}")
                # Continuamos a pesar del error
        
        # Probar un archivo específico si se solicita
        if args.test_file:
            try:
                generator._test_file_embedding(args.test_file)
                logging.info(f"Prueba de embedding para {args.test_file} completada.")
                # Si solo se solicitó esta operación, terminar
                if not args.prompt:
                    return
            except Exception as e:
                logging.error(f"Error al probar embedding para {args.test_file}: {e}")
                # Continuamos a pesar del error
        
        # Habilitar el modo de truncado forzado si se solicita
        if args.force_truncate:
            generator.force_truncate = True
            logging.info("Se forzará el truncado de todos los ejemplos, incluso los que ya están en caché.")
        else:
            generator.force_truncate = False
            
        # Si se solicita, deshabilitar uso de embeddings
        if args.no_embeddings:
            generator.use_embeddings = False
            logging.info("Modo sin embeddings activado. No se usará búsqueda semántica.")
        else:
            generator.use_embeddings = True

        # Get user prompt
        user_prompt = args.prompt
        if not user_prompt:
            try:
                user_prompt = input(colored("\n📝 Enter your code generation prompt: ", "yellow"))
            except EOFError:
                print(colored("\n❌ No prompt provided. Exiting.", "red"))
                return # Exit gracefully if input is interrupted

        if not user_prompt: # Check again if input was empty
             print(colored("\n❌ Prompt cannot be empty. Exiting.", "red"))
             return

        logging.info("🏁 Starting code generation process...")

        try:
            output_paths = generator._get_output_paths(user_prompt)
            logging.info(f"=== PREBUILD PROCCESSING DONE! ===")
            logging.info(f"📁 Ruta de generación de fuentes: {output_paths['base'].absolute()}")
            logging.info(f"📁 Ruta de trabajo: {output_paths['obj_dir'].absolute()}")
        except Exception as e:
            logging.error(f"Error al crear rutas de salida: {e}")
            output_paths = {
                'base': Path('local/error_output'),
                'c_file': Path('local/error_output/main.c'),
                'prompt_file': Path('local/error_output/prompt.txt'),
                'platform_file': Path('local/error_output/platform.txt'),
                'obj_dir': Path('local/error_output/obj')
            }
            logging.info("Se usarán rutas de salida por defecto.")

        try:
            generated_code = generator.generate_c_code(user_prompt)
        except Exception as e:
            logging.error(f"Error durante la generación de código: {e}")
            print(colored(f"\n❌ Error durante la generación de código: {e}", "red"))
            print(colored("Intentando continuar con el guardado de archivos...", "yellow"))
            generated_code = f"// Error durante la generación de código: {e}\n\n// Prompt: {user_prompt}"

        if generated_code: # Only save if code was generated
            try:
                generator.save_generated_files(generated_code, user_prompt, output_paths)
                print(colored("\n✨ Success! ✨", "green", attrs=['bold']))
                print(colored(f"📂 Files saved in: {output_paths['base'].resolve()}", "cyan"))
            except Exception as e:
                logging.error(f"Error al guardar archivos: {e}")
                print(colored(f"\n❌ Error al guardar archivos: {e}", "red"))
                
                # Intento de emergencia para guardar al menos el código
                try:
                    emergency_dir = Path("local/emergency_output")
                    emergency_dir.mkdir(parents=True, exist_ok=True)
                    
                    with open(emergency_dir / "emergency_code.c", "w") as f:
                        f.write(generated_code)
                    with open(emergency_dir / "emergency_prompt.txt", "w") as f:
                        f.write(user_prompt)
                        
                    print(colored(f"📂 Emergency files saved in: {emergency_dir.resolve()}", "yellow"))
                except Exception as e2:
                    print(colored(f"❌ Error al guardar archivos de emergencia: {e2}", "red"))
        else:
             print(colored("\n⚠️ Warning: Code generation resulted in empty output. Files not saved.", "yellow"))


    except ValueError as e: # Catch specific expected errors like missing API key
         logging.error(f"Configuration Error: {e}")
         print(colored(f"❌ Configuration Error: {e}", "red"))
    except Exception as e:
         logging.exception(f"An unexpected error occurred: {e}") # Log full traceback for unexpected errors
         print(colored(f"❌ An unexpected error occurred. Check logs in {LOG_DIR} for details.", "red"))

if __name__ == "__main__":
    main()