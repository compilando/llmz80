import os
import yaml
import sys
import logging

logger = logging.getLogger(__name__)

# --- Definición Explícita de Paletas Amstrad CPC ---
# Fuente: https://www.cpcwiki.eu/index.php/CPC_Palette
# Los índices corresponden a los 'Hardware Colour Number'
AMSTRAD_PALETTE_MODE0_MODE1 = {
    0: {"name": "Black", "rgb": [0, 0, 0]},
    1: {"name": "Blue", "rgb": [0, 0, 128]},
    2: {"name": "Bright Blue", "rgb": [0, 0, 255]},
    3: {"name": "Red", "rgb": [128, 0, 0]},
    4: {"name": "Magenta", "rgb": [128, 0, 128]},
    5: {"name": "Mauve", "rgb": [128, 0, 255]}, # O Bright Magenta
    6: {"name": "Bright Red", "rgb": [255, 0, 0]},
    7: {"name": "Purple", "rgb": [255, 0, 128]},
    8: {"name": "Bright Magenta", "rgb": [255, 0, 255]},
    9: {"name": "Green", "rgb": [0, 128, 0]},
    10: {"name": "Cyan", "rgb": [0, 128, 128]},
    11: {"name": "Sky Blue", "rgb": [0, 128, 255]},
    12: {"name": "Bright Green", "rgb": [0, 255, 0]},
    13: {"name": "Bright Cyan", "rgb": [0, 255, 128]},
    14: {"name": "Bright Blue", "rgb": [0, 255, 255]}, # Conflicto nombre, es más como Bright Cyan?
    15: {"name": "Orange", "rgb": [128, 128, 0]},
    16: {"name": "Pastel Blue", "rgb": [128, 128, 128]}, # O Grey
    17: {"name": "Pink", "rgb": [128, 128, 255]},
    18: {"name": "Pastel Yellow", "rgb": [255, 128, 0]},
    19: {"name": "Pastel Magenta", "rgb": [255, 128, 128]},
    20: {"name": "Bright Pink", "rgb": [255, 128, 255]},
    21: {"name": "Pastel Green", "rgb": [0, 128, 0]}, # Duplicado? No, este es el #14 hardware.
}

# Paletas por defecto de Amstrad CPC
AMSTRAD_DEFAULT_PALETTES = {
    'mode0': [
        (0, 0, 0), (0, 0, 128), (0, 255, 0), (0, 255, 255),
        (128, 0, 0), (128, 0, 128), (128, 255, 0), (128, 255, 255),
        (255, 0, 0), (255, 0, 128), (255, 255, 0), (255, 255, 255),
        (0, 0, 255), (0, 128, 255), (128, 0, 255), (128, 128, 255) # Ajustados para tener 16
    ],
    'mode1': [
        (0, 0, 0), (0, 255, 255), (255, 255, 0), (255, 255, 255)
    ],
    'mode2': [
        (0, 0, 0), (0, 255, 0) # Negro y Verde brillante por defecto
    ]
}

# Paleta simple para Spectrum (como lista de tuplas RGB)
SPECTRUM_PALETTE_LIST = [(255, 255, 255), (0, 0, 0)]

# Constante para la plantilla genérica
GENERIC_PROMPT_TEMPLATE_PATH = os.path.join("resources", "sprite_prompt_generic.txt")

# Load platform configurations from YAML
def load_platform_config():
    """Load platform configurations from YAML file"""
    logger.debug("Cargando configuración de plataformas desde YAML")
    try:
        yaml_path = os.path.join("resources", "platforms.yml")
        logger.debug(f"Archivo YAML: {yaml_path} (existe: {os.path.exists(yaml_path)})")
        with open(yaml_path, "r") as f:
            config = yaml.safe_load(f)
            if not config:
                 logger.error(f"❌ Error: El archivo YAML '{yaml_path}' está vacío o no se pudo parsear.")
                 sys.exit(1)
            logger.debug(f"Plataformas cargadas: {list(config.keys())}")
            return config
    except FileNotFoundError:
        logger.error(f"❌ Error: No se encontró el archivo de configuración de plataformas: {yaml_path}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error cargando configuración de plataformas desde {yaml_path}: {str(e)}")
        sys.exit(1)

# Carga la configuración una vez al importar el módulo
PLATFORMS = load_platform_config()

# --- Funciones para obtener paleta --- 

def get_palette_for_platform(platform: str, mode: str = None) -> list[tuple[int, int, int]]:
    """Devuelve la lista de tuplas RGB para la plataforma/modo especificado."""
    if platform == 'spectrum':
        return SPECTRUM_PALETTE_LIST
    elif platform == 'amstrad_cpc' and mode:
        palette = AMSTRAD_DEFAULT_PALETTES.get(mode)
        if palette:
            return palette
        else:
            logger.warning(f"No se encontró paleta por defecto para Amstrad modo {mode}. Usando B/N.")
            return SPECTRUM_PALETTE_LIST # Fallback
    else:
        logger.warning(f"Combinación inválida para obtener paleta: {platform}/{mode}. Usando B/N.")
        return SPECTRUM_PALETTE_LIST # Fallback
