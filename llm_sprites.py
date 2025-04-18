#!/usr/bin/env python3

import os
import sys
import argparse
import datetime
import time
import json
import logging
import base64
import openai
from openai import OpenAI
from dotenv import load_dotenv
from PIL import Image
import io
import numpy as np
import yaml
import re
import subprocess
from scipy.ndimage import label, sum as ndi_sum # Importar para componentes conectados
from generators.base import BaseImageGenerator
from generators.openai_generator import OpenAIImageGenerator
from generators.gemini_generator import GeminiImageGenerator
from generators.vertexai_generator import VertexAIImageGenerator # Importar VertexAI
from config import PLATFORMS, GENERIC_PROMPT_TEMPLATE_PATH # Import PLATFORMS and TEMPLATE_PATH
from image_utils import (
    process_image_pipeline, 
    generate_sprite_text, 
    display_sprite, 
    display_image_in_terminal,
    save_results # Importar save_results
)

# Configure logging
# Configure root logger instead of just __name__
logging.basicConfig(
    level=logging.INFO, # Default level for root
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
# Get the logger for this specific module if needed, but level is controlled by root
logger = logging.getLogger(__name__)

# Inicio de la ejecución
logger.debug("🔍 Iniciando ejecución de llm_sprites.py")

# Load environment variables from .env
logger.debug("Cargando variables de entorno desde .env")
load_dotenv()

# --- Funciones Interactivas --- (Reintroducidas)
def get_platform_interactive():
    """Get platform selection from user interactively"""
    print("\n🎮 Select platform:")
    platform_keys = list(PLATFORMS.keys())
    for i, key in enumerate(platform_keys, 1):
        print(f"{i}. {PLATFORMS[key].get('name', key)}") # Use name if available
    
    while True:
        try:
            choice = int(input("\nEnter platform number: "))
            if 1 <= choice <= len(platform_keys):
                selected_key = platform_keys[choice - 1]
                logger.info(f"Plataforma seleccionada: {selected_key}")
                return selected_key
            print(f"❌ Selección inválida. Introduce un número entre 1 y {len(platform_keys)}.")
        except ValueError:
            print("❌ Por favor, introduce un número.")
        except EOFError:
            logger.error("\nCancelado por el usuario.")
            sys.exit(1)

def get_mode_interactive(platform):
    """Get mode selection from user interactively for Amstrad CPC"""
    if platform != 'amstrad_cpc':
        return None
        
    platform_config = PLATFORMS.get(platform, {})
    modes = platform_config.get('modes', [])
    if not modes:
        logger.warning(f"No se encontraron modos definidos para {platform} en la configuración.")
        return None # No modes to select
        
    print("\n📺 Select Amstrad CPC mode:")
    for i, mode in enumerate(modes, 1):
        colors = platform_config.get('colors', {}).get(mode, '?')
        print(f"{i}. {mode} ({colors} colors)")
    
    while True:
        try:
            choice = int(input("\nEnter mode number: "))
            if 1 <= choice <= len(modes):
                selected_mode = modes[choice - 1]
                logger.info(f"Modo seleccionado: {selected_mode}")
                return selected_mode
            print(f"❌ Selección inválida. Introduce un número entre 1 y {len(modes)}.")
        except ValueError:
            print("❌ Por favor, introduce un número.")
        except EOFError:
            logger.error("\nCancelado por el usuario.")
            sys.exit(1)

def get_dimensions_interactive(platform):
    """Get sprite dimensions from user interactively"""
    platform_config = PLATFORMS.get(platform, {})
    max_width = platform_config.get('max_width', 256) # Default max if not specified
    max_height = platform_config.get('max_height', 256)
    default_width = platform_config.get('default_width', 16)
    default_height = platform_config.get('default_height', 16)
    
    print(f"\n📏 Enter sprite dimensions (max: {max_width}x{max_height})")
    print(f"   Press Enter for default size ({default_width}x{default_height})")
    
    while True:
        try:
            width_input = input(f"   Width [{default_width}]: ").strip()
            height_input = input(f"   Height [{default_height}]: ").strip()
            
            width = int(width_input) if width_input else default_width
            height = int(height_input) if height_input else default_height
            
            if 1 <= width <= max_width and 1 <= height <= max_height:
                logger.info(f"Dimensiones seleccionadas: {width}x{height}")
                return width, height
            print(f"❌ Dimensiones deben estar entre 1x1 y {max_width}x{max_height}")
        except ValueError:
            print("❌ Por favor, introduce números válidos.")
        except EOFError:
            logger.error("\nCancelado por el usuario.")
            sys.exit(1)

def get_prompt_interactive():
    """Get sprite description from user interactively"""
    print("\n💭 Enter sprite description (e.g., running knight, spaceship):")
    while True:
        try:
            prompt = input("> ").strip()
            if prompt:
                #logger.debug(f"Prompt introducido: '{prompt}'")
                return prompt
            else:
                print("❌ La descripción no puede estar vacía.")
        except EOFError:
             logger.error("\nCancelado por el usuario.")
             sys.exit(1)
# -----------------------------

def parse_arguments():
    logger.debug("Analizando argumentos de línea de comandos")
    parser = argparse.ArgumentParser(description='Sprite generator using LLM', add_help=False) # Defer help action
    
    # --- Define Arguments ---
    # Core arguments
    parser.add_argument('--prompt', type=str, help='Description of the sprite to generate')
    parser.add_argument('--platform', type=str, choices=list(PLATFORMS.keys()), 
                      help='Target platform (e.g., spectrum, amstrad_cpc)')
    parser.add_argument('--mode', type=str, help='Display mode for the platform (required for amstrad_cpc)')
    parser.add_argument('--width', type=int, help='Final sprite width')
    parser.add_argument('--height', type=int, help='Final sprite height')
    
    # Generation options
    parser.add_argument('--generator', type=str, choices=['gemini', 'openai', 'vertexai'], default='vertexai',
                      help='Image generation model/API to use (default: vertexai)')
    parser.add_argument('--negative-prompt', type=str, default='', help='Negative prompt for generation')
    parser.add_argument('--output-dir', type=str, default='sprites', help='Base directory for output sprites')
    parser.add_argument('--interactive', action='store_true', help='Run in interactive mode to ask for missing parameters')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    # Vertex AI Specific Arguments
    parser.add_argument('--gcp-project-id', type=str, default=os.getenv('GCP_PROJECT_ID'),
                       help='Google Cloud Project ID (required for vertexai generator). Can also be set via GCP_PROJECT_ID env var.')
    parser.add_argument('--gcp-location', type=str, default=os.getenv('GCP_LOCATION', 'us-central1'),
                       help='Google Cloud Location (region) for Vertex AI (default: us-central1). Can also be set via GCP_LOCATION env var.')

    # Add help argument separately to handle it before interactive mode if needed
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, 
                        help='show this help message and exit')

    # --- Parse Initial Arguments ---
    # Parse known args first to check for --interactive or missing core args without exiting on errors yet
    args, unknown = parser.parse_known_args()
    logger.debug(f"Argumentos iniciales parseados: {args}")
    if unknown:
        logger.warning(f"Argumentos desconocidos ignorados: {unknown}")

    # Set root logger level based on debug flag
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        # No need to loop through handlers if root level is set
        logger.info("*** Debug logging enabled ***") # Use INFO so it's always visible when enabled
        
    logger.debug(f"Argumentos recibidos inicialmente: {args}")

    # --- Interactive Mode Logic ---
    # Determine if we need interactive mode
    is_missing_core_arg = not args.prompt or not args.platform or args.width is None or args.height is None
    run_interactive = args.interactive or (is_missing_core_arg and not unknown) # Don't run interactive if there were unknown args (likely a typo)

    if run_interactive:
        logger.info("⚙️ Iniciando modo interactivo para completar parámetros...")
        if not args.platform:
            args.platform = get_platform_interactive()
            # Reset mode if platform changes, as it might become invalid
            args.mode = None 
            
        if args.platform == 'amstrad_cpc' and not args.mode:
            args.mode = get_mode_interactive(args.platform)
            
        if args.width is None or args.height is None:
            args.width, args.height = get_dimensions_interactive(args.platform)
            
        if not args.prompt:
            args.prompt = get_prompt_interactive()
            
        logger.info("Parámetros completados interactivamente.")
        # Optionally ask for negative prompt? For now, keep it command-line only.
        # Optionally ask for generator? For now, keep it command-line only.

    # --- Final Validation (using the potentially modified args) ---
    # No need to re-parse; validate the args object directly as it might have been modified interactively.
    logger.debug(f"Argumentos finales tras posible modo interactivo: {args}")
    
    # --- Perform Validation on Final Args ---
    # Now perform the required checks on the potentially updated args
    if not args.prompt:
        logger.error("❌ Error: Se necesita un prompt (proporcionado o introducido interactivamente).")
        sys.exit(1)
    if not args.platform:
        logger.error("❌ Error: Se necesita una plataforma (proporcionada o introducida interactivamente).")
        sys.exit(1)
    if args.width is None or args.height is None:
        logger.error("❌ Error: Se necesitan ancho y alto (proporcionados o introducidos interactivamente).")
        sys.exit(1)
        
    try:
        platform_config = PLATFORMS[args.platform]
        logger.debug(f"Configuración de plataforma: {platform_config}")
        
        # Validate dimensions
        if args.width > platform_config['max_width']:
            logger.error(f"❌ Width exceeds maximum for {platform_config['name']} ({platform_config['max_width']})")
            sys.exit(1)
        if args.height > platform_config['max_height']:
            logger.error(f"❌ Height exceeds maximum for {platform_config['name']} ({platform_config['max_height']})")
            sys.exit(1)
        
        # Validate mode for Amstrad CPC
        if args.platform == 'amstrad_cpc':
            logger.debug(f"Validando modo para Amstrad CPC: {args.mode}")
            if not args.mode:
                 logger.error("❌ Mode is required for Amstrad CPC")
                 sys.exit(1)
            if args.mode not in platform_config['modes']:
                 logger.error(f"❌ Invalid mode for Amstrad CPC: {args.mode}")
                 logger.debug(f"Modos válidos: {platform_config['modes']}")
                 sys.exit(1)
         
        # Vertex AI specific validation
        if args.generator == 'vertexai':
             if not args.gcp_project_id:
                 logger.error("❌ Error: El argumento --gcp-project-id (o variable de entorno GCP_PROJECT_ID) es obligatorio cuando se usa --generator=vertexai.")
                 sys.exit(1)
             if not args.gcp_location:
                 # Default is set, but explicit check is good practice
                 logger.error("❌ Error: El argumento --gcp-location (o variable de entorno GCP_LOCATION) es obligatorio cuando se usa --generator=vertexai.")
                 sys.exit(1)

        return args # Return the final, potentially interactively-filled arguments
    except Exception as e:
        logger.error(f"❌ Error durante la validación final de argumentos: {str(e)}")
        sys.exit(1)

def create_output_directory(args):
    logger.debug("Determinando el directorio de salida")
    
    # Crear el directorio sprites si no existe
    if not os.path.exists("sprites"):
        os.makedirs("sprites", exist_ok=True)
        logger.debug("Directorio sprites creado")
    
    # Crear un slug a partir del prompt
    prompt_slug = "-".join(args.prompt.lower().split()[:3])
    # Eliminar caracteres no alfanuméricos excepto guiones
    prompt_slug = re.sub(r'[^a-z0-9\-]', '', prompt_slug)
    
    if args.platform == 'amstrad_cpc':
        directory = f"sprites/{args.platform}_{args.mode}_{prompt_slug}"
    else:
        directory = f"sprites/{args.platform}_{prompt_slug}"
    
    logger.debug(f"Directorio a crear: {directory}")
    
    # Crear directorio si no existe
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        logger.info(f"✅ Directory created: {directory}")
    
    return directory

def display_prompt(prompt):
    """Display final prompt in terminal"""
    print("\n💭 Final prompt:")
    print("═" * 80)
    print(prompt)
    print("═" * 80)

def display_final_prompt(prompt):
    print("="*80 + "\n")

def select_generator(generator_name: str, args) -> BaseImageGenerator:
    """Instantiates and returns the selected image generator based on args."""
    logger.info(f"Seleccionando generador: {generator_name}")
    if generator_name == 'openai':
        try:
            # API key is handled within the generator class init
            return OpenAIImageGenerator()
        except ValueError as e:
             logger.error(f"❌ Error al inicializar OpenAI Generator: {e}. Asegúrate de que OPENAI_API_KEY está configurada.")
             sys.exit(1)
        except Exception as e:
             logger.error(f"❌ Error inesperado al inicializar OpenAI Generator: {e}.")
             sys.exit(1)
    elif generator_name == 'gemini':
        try:
            # API key is handled within the generator class init
            return GeminiImageGenerator()
        except ValueError as e:
             logger.error(f"❌ Error al inicializar Gemini Generator: {e}. Asegúrate de que GEMINI_API_KEY está configurada.")
             sys.exit(1)
        except Exception as e:
             logger.error(f"❌ Error inesperado al inicializar Gemini Generator: {e}.")
             sys.exit(1)
        # Note: Gemini generation itself might raise NotImplementedError later
    elif generator_name == 'vertexai':
        try:
            # Pass project ID and location from args
            if not args.gcp_project_id or not args.gcp_location:
                 logger.error("❌ Error: --gcp-project-id y --gcp-location son necesarios para el generador vertexai.")
                 sys.exit(1)
            return VertexAIImageGenerator(project_id=args.gcp_project_id, location=args.gcp_location)
        except ValueError as e:
            logger.error(f"❌ Error al inicializar Vertex AI Generator: {e}.")
            logger.error("Asegúrate de que --gcp-project-id y --gcp-location son correctos, GOOGLE_APPLICATION_CREDENTIALS está configurado y la API Vertex AI está habilitada.")
            sys.exit(1)
        except Exception as e: # Catch other potential init errors like auth
            logger.error(f"❌ Error inesperado al inicializar Vertex AI Generator: {e}.")
            sys.exit(1)
    else:
        # This case should be prevented by argparse choices
        logger.error(f"Generador desconocido: {generator_name}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        logger.debug("🚀 Iniciando programa principal")
        args = parse_arguments()
        config = PLATFORMS[args.platform] 
        output_dir = create_output_directory(args)
    
        logger.info(f"🔍 Generating sprite for user prompt: '{args.prompt}'")
        logger.info(f"🎯 Target size: {args.width}x{args.height}")
        logger.info(f"🕹️ Platform: {args.platform}" + (f", Mode: {args.mode}" if args.platform == 'amstrad_cpc' else ""))
    
        start_time = time.time()
        # 1. Cargar plantilla genérica
        try:
            with open(GENERIC_PROMPT_TEMPLATE_PATH, "r") as f:
                generic_template = f.read()
            logger.debug(f"Plantilla genérica cargada desde {GENERIC_PROMPT_TEMPLATE_PATH}")
        except FileNotFoundError:
            logger.error(f"❌ Error: No se encontró la plantilla genérica: {GENERIC_PROMPT_TEMPLATE_PATH}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"❌ Error cargando plantilla genérica: {str(e)}")
            sys.exit(1)

        # 2. Formatear prompt para LLM (usando un tamaño mayor fijo, p.ej., 1024x1024 que es lo que soporta DALL-E 3)
        # Aunque la plantilla pide {llm_width}x{llm_height}, DALL-E 3 fuerza el tamaño.
        # Podríamos quitar esos placeholders de la plantilla genérica.
        # Por ahora, los dejamos pero no se usan para la llamada a la API.
        llm_width = 1024 # Tamaño fijo para DALL-E 3
        llm_height = 1024
        try:
            final_prompt = generic_template.format(
                user_prompt=args.prompt,
                llm_width=llm_width, # Placeholder en plantilla
                llm_height=llm_height, # Placeholder en plantilla
                negative_prompt=args.negative_prompt
            )
            logger.debug(f"Prompt final para LLM formateado.")
        except KeyError as e:
            logger.error(f"❌ Error: La plantilla genérica no contiene la clave esperada: {e}")
            logger.error("Asegúrate de que la plantilla incluya {user_prompt}, {llm_width}, {llm_height}, {negative_prompt}")
            sys.exit(1)

        # display_prompt(final_prompt)

        # 2. Select and Initialize Generator
        generator = select_generator(args.generator, args)
        
        # 3. Generate Raw Image using the selected generator
        logger.info("⏳ Iniciando llamada a la API de generación de imágenes...")
        gen_start_time = time.time()
        try:
            raw_image = generator.generate_image(final_prompt)
        except NotImplementedError as nie:
             logger.error(f"❌ Error: El generador '{args.generator}' no implementa la generación de imágenes: {nie}")
             sys.exit(1)
        except Exception as gen_err:
             logger.error(f"❌ Falló la generación de imagen con '{args.generator}': {gen_err}")
             # Attempt to remove the output directory if generation failed badly
             import shutil
             try:
                 if os.path.exists(output_dir):
                    logger.warning(f"Intentando eliminar directorio incompleto: {output_dir}")
                    shutil.rmtree(output_dir)
             except Exception as rm_err:
                 logger.error(f"No se pudo eliminar el directorio '{output_dir}': {rm_err}")
             sys.exit(1)
        
        gen_time = time.time() - gen_start_time
        logger.info(f"⏱️ Tiempo de generación API: {gen_time:.2f} segundos")

        # Save raw generated image before processing
        raw_file = os.path.join(output_dir, "original.png")
        try:
            raw_image.save(raw_file)
            logger.info(f"✅ Imagen original (raw) guardada: {raw_file}")
        except Exception as e:
            logger.warning(f"⚠️ No se pudo guardar la imagen original: {str(e)}")
            raw_file = None # Indicate it wasn't saved

        # Save cleaned image (intermediate step) for debugging
        try:
            # Re-run cleaning just for saving this intermediate step
            # Note: process_image_pipeline already does this internally
            from image_utils import _clean_image # Local import for clarity
            cleaned_for_save = _clean_image(raw_image) 
            cleaned_file_path = os.path.join(output_dir, "cleaned.png")
            cleaned_for_save.save(cleaned_file_path)
            logger.info(f"✅ Imagen limpiada (intermedia) guardada: {cleaned_file_path}")
        except Exception as e:
            logger.warning(f"⚠️ No se pudo guardar la imagen limpiada intermedia: {str(e)}")

        # 4. Process Image (Clean, Palette, Scale)
        proc_start_time = time.time()
        # Use the function from image_utils
        processed_rgb_image, binary_array = process_image_pipeline(raw_image, args) 
        proc_time = time.time() - proc_start_time
        logger.info(f"⏱️ Tiempo de procesamiento de imagen: {proc_time:.2f} segundos")

        # 5. Save final results (using imported function)
        png_file, txt_file = save_results(processed_rgb_image, binary_array, output_dir, args, final_prompt)

        # 6. Display results (only if saving was successful)
        if png_file and txt_file:
            if raw_file:
                logger.info("--- Mostrando Imagen Original ---")
                display_image_in_terminal(raw_file)
                
            logger.info("--- Mostrando Imagen Procesada Final ---")
            display_image_in_terminal(png_file)

            logger.info("--- Mostrando Sprite en Consola (ANSI) ---")
            display_sprite(binary_array, args)
        else:
            logger.error("❌ No se pudieron guardar los archivos de resultados. No se mostrarán las imágenes ni el sprite ANSI.")
            logger.error("   Revisa los logs anteriores para ver el error específico ocurrido durante el guardado.")

        main_time = time.time() - start_time
        logger.info(f"✨ Proceso completado en {gen_time + proc_time:.2f} segundos")
        logger.info(f"📂 Files saved in: {output_dir}")
    except Exception as e:
        logger.error(f"❌ Error general: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1) 