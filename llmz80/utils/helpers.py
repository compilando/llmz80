import re
from pathlib import Path
from datetime import datetime
import logging
from typing import Dict

def create_slug(text: str, max_length: int = 40) -> str:
    """Genera un slug URL-friendly a partir de un texto.
    
    Args:
        text: Texto a convertir en slug
        max_length: Longitud máxima del slug
        
    Returns:
        Slug generado
    """
    logging.debug(f"Creando slug desde texto: {text[:50]}...")
    slug = text.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)  # Eliminar caracteres no deseados
    slug = re.sub(r'[-\s]+', '-', slug).strip('-')  # Reemplazar espacios/guiones por un solo guión
    slug = slug[:max_length]  # Truncar
    logging.debug(f"Slug creado: {slug}")
    return slug

def get_output_paths(prompt: str, platform: str, base_output_dir: Path, slug_max_length: int) -> Dict[str, Path]:
    """Genera rutas para archivos de salida basadas en timestamp y slug del prompt.
    
    Args:
        prompt: Prompt del usuario
        platform: Plataforma seleccionada
        base_output_dir: Directorio base para la salida
        slug_max_length: Longitud máxima para el slug
        
    Returns:
        Diccionario con las rutas generadas
    """
    logging.info("🗂️ Generando rutas de salida...")
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    slug = create_slug(prompt, slug_max_length)
    base_dir = base_output_dir / f"{timestamp}_{slug}"

    paths = {
        'base': base_dir,
        'c_file': base_dir / 'main.c',
        'prompt_file': base_dir / 'prompt.txt',
        'platform_file': base_dir / 'platform.txt',  # Renombrado para claridad
        'obj_dir': base_dir / 'obj',  # Añadir explícitamente la ruta del dir obj
    }

    # Archivo de salida específico según la plataforma
    if platform == 'spectrum':
        paths['output_artifact'] = base_dir / 'output.tap'  # Nombre de ejemplo
    elif platform == 'amstrad_cpc':
        paths['output_artifact'] = base_dir / 'output.dsk'  # Nombre de ejemplo
    else:
        paths['output_artifact'] = base_dir / 'output.bin'  # Fallback genérico

    logging.debug(f"Rutas generadas: {paths}")
    return paths

def estimate_tokens(text: str) -> int:    
    """Estima de manera sencilla el número de tokens en un texto.
    
    Aproximación: 1 token ≈ 3.5 caracteres en inglés/código.
    
    Args:
        text: Texto cuya longitud en tokens se quiere estimar
        
    Returns:
        Número estimado de tokens
    """
    # Estimación conservadora: 1 token por cada 3.5 caracteres
    return int(len(str(text)) / 3.5)

def clean_api_response(raw_response: str) -> str:
    """Intenta extraer solo el código C de la respuesta de la API.
    
    Args:
        raw_response: Respuesta completa de la API
        
    Returns:
        Código C limpio
    """
    logging.debug("Limpiando respuesta de la API...")
    code = raw_response.strip()

    # Intento 1: Regex para bloques de código markdown (non-greedy)
    match = re.search(r'```(?:c)?\n(.*?)\n```', code, re.DOTALL | re.IGNORECASE)
    if match:
        extracted_code = match.group(1).strip()
        logging.info("✅ Código extraído usando regex de markdown.")
        return extracted_code

    # Intento 2: Si no hay markdown, asumir que toda la respuesta podría ser código,
    # pero intentar eliminar frases introductorias/de cierre comunes.
    # Esto es menos confiable.
    logging.warning("⚠️ No se encontró bloque de código markdown. Intentando limpieza básica.")
    lines = code.splitlines()
    # Eliminar posibles líneas de explicación iniciales/finales (heurística)
    if lines:
        if "here is the c code" in lines[0].lower() or "```" in lines[0]:
            lines.pop(0)
    if lines:
        if "```" in lines[-1]:
            lines.pop(-1)

    cleaned_code = "\n".join(lines).strip()
    if len(cleaned_code) < 0.5 * len(raw_response):  # Umbral arbitrario
        logging.warning("⚠️ La limpieza básica redujo significativamente la longitud del contenido. El resultado podría estar incompleto.")
    elif not cleaned_code:
        logging.warning("⚠️ La limpieza resultó en código vacío.")

    return cleaned_code if cleaned_code else raw_response  # Devolver original si la limpieza falló gravemente 