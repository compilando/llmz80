import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import logging

# Valores por defecto 
DEFAULT_MODEL = "gpt-4o"
DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 4096
DEFAULT_MAX_EXAMPLES = 10
DEFAULT_LOG_LEVEL = "INFO"

# Obtener logger para este módulo
logger = logging.getLogger(__name__)

def load_config(config_path: str) -> Dict[str, Any]:
    """Carga la configuración desde un archivo YAML.
    
    Args:
        config_path: Ruta al archivo de configuración
        
    Returns:
        Un diccionario con la configuración
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
            logger.info(f"Configuración cargada correctamente desde {config_path}")
            return config_data if config_data else {}
    except FileNotFoundError:
        logger.warning(f"Archivo de configuración {config_path} no encontrado. Usando valores por defecto.")
        return {}
    except Exception as e:
        logger.error(f"Error al cargar la configuración desde {config_path}: {e}")
        raise

def load_api_key() -> str:
    """Carga la clave de API de OpenAI desde variables de entorno.
    
    Returns:
        La clave de API como string
    """
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        logging.error("❌ OPENAI_API_KEY no encontrada en variables de entorno o archivo .env")
        raise ValueError("OPENAI_API_KEY es obligatoria.")
    logging.info("🔑 Clave de API de OpenAI encontrada.")
    return api_key

def initialize_global_vars(config: Dict[str, Any], platform: str) -> Dict[str, Any]:
    """Inicializa las variables globales desde la configuración.
    
    Args:
        config: Diccionario con la configuración
        platform: Plataforma seleccionada (spectrum, amstrad_cpc, etc)
        
    Returns:
        Diccionario con las variables globales inicializadas
    """
    # Configuración de logging
    log_dir_str = config.get('logging', {}).get('log_dir', 'local/logs')
    log_dir = Path(log_dir_str)
    
    # Configuración de directorios de salida
    base_dir_str = config.get('output', {}).get('base_dir', 'local')
    base_output_dir = Path(base_dir_str)
    
    # Configuración de archivos de prompt
    prompt_files = config.get('prompt_files', {})
    spectrum_prompt = prompt_files.get('spectrum', 'system_prompt_spectrum.txt')
    amstrad_prompt = prompt_files.get('amstrad_cpc', 'system_prompt_amstrad_cpc.txt')
    
    # Decidir qué plantilla usar según la plataforma
    if platform == 'spectrum':
        system_prompt_file = spectrum_prompt
    else:
        system_prompt_file = amstrad_prompt
    
    # Configuración de embeddings
    embeddings_config = config.get('embeddings', {})
    cache_dir_str = embeddings_config.get('cache_dir', 'local/embeddings')
    embeddings_cache_dir = Path(cache_dir_str)
    max_chunk_size = embeddings_config.get('max_chunk_size', 15000)
    token_limit = embeddings_config.get('token_limit', 8000)
    safety_margin = embeddings_config.get('safety_margin', 0.8)
    
    # Configuración de ejemplos
    examples_config = config.get('examples', {})
    max_example_size = examples_config.get('truncate_size', 50000)
    example_dir_template = "examples/{platform}"
    configured_roots = examples_config.get('roots', {}).get(platform)
    if configured_roots:
        example_dirs = [Path(path) for path in configured_roots]
    elif platform == 'amstrad_cpc':
        example_dirs = [Path('examples/amstrad_cpc'), Path('examples/amstrad_cpc_level2')]
    else:
        example_dirs = [Path(example_dir_template.format(platform=platform))]
    
    # Configuración de slug
    slug_max_length = config.get('output', {}).get('slug_max_length', 40)
    
    # Crear directorios necesarios
    log_dir.mkdir(parents=True, exist_ok=True)
    embeddings_cache_dir.mkdir(parents=True, exist_ok=True)
    
    # Cargar los parámetros por defecto o desde la configuración
    model = config.get('openai', {}).get('model', DEFAULT_MODEL)
    temperature = config.get('openai', {}).get('temperature', DEFAULT_TEMPERATURE)
    max_tokens = config.get('openai', {}).get('max_tokens', DEFAULT_MAX_TOKENS)
    reasoning_effort = config.get('openai', {}).get('reasoning_effort')
    max_examples = config.get('examples', {}).get('max_examples', DEFAULT_MAX_EXAMPLES)
    embedding_model = config.get('openai', {}).get('embedding_model', DEFAULT_EMBEDDING_MODEL)
    
    # Devolver todas las variables como un diccionario
    return {
        'log_dir': log_dir,
        'base_output_dir': base_output_dir,
        'system_prompt_file': system_prompt_file,
        'embeddings_cache_dir': embeddings_cache_dir,
        'max_chunk_size': max_chunk_size,
        'token_limit': token_limit,
        'safety_margin': safety_margin,
        'max_example_size': max_example_size,
        'example_dir_template': example_dir_template,
        'example_dirs': example_dirs,
        'slug_max_length': slug_max_length,
        'model': model,
        'temperature': temperature,
        'max_tokens': max_tokens,
        'reasoning_effort': reasoning_effort,
        'max_examples': max_examples,
        'embedding_model': embedding_model,
        'error_doc_glob_pattern': '**/*.md'
    }
