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

# Configure logging with more verbose output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Inicio de la ejecución
logger.debug("🔍 Iniciando ejecución de llm_sprites.py")

# Load environment variables from .env
logger.debug("Cargando variables de entorno desde .env")
load_dotenv()

# Check if OpenAI API key exists
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    logger.error("❌ Error: OPENAI_API_KEY not configured in .env file")
    logger.info("💡 Create a .env file with your API key: OPENAI_API_KEY=your_api_key")
    sys.exit(1)
else:
    logger.debug(f"API key encontrada: {api_key[:5]}...{api_key[-4:]}")

# Initialize OpenAI client
logger.debug("Inicializando cliente OpenAI")
client = OpenAI(api_key=api_key)

# Load platform configurations from YAML
def load_platform_config():
    """Load platform configurations from YAML file"""
    logger.debug("Cargando configuración de plataformas desde YAML")
    try:
        yaml_path = os.path.join("resources", "platforms.yml")
        logger.debug(f"Archivo YAML: {yaml_path} (existe: {os.path.exists(yaml_path)})")
        with open(yaml_path, "r") as f:
            config = yaml.safe_load(f)
            logger.debug(f"Plataformas cargadas: {list(config.keys())}")
            return config
    except Exception as e:
        logger.error(f"❌ Error loading platform configurations: {str(e)}")
        sys.exit(1)

# Load platform configurations
logger.debug("Cargando configuraciones de plataformas")
PLATFORMS = load_platform_config()

def get_platform_interactive():
    """Get platform selection from user interactively"""
    print("\n🎮 Select platform:")
    for i, platform in enumerate(PLATFORMS.keys(), 1):
        print(f"{i}. {PLATFORMS[platform]['name']}")
    
    while True:
        try:
            choice = int(input("\nEnter platform number: "))
            if 1 <= choice <= len(PLATFORMS):
                return list(PLATFORMS.keys())[choice - 1]
            print("❌ Invalid selection. Please try again.")
        except ValueError:
            print("❌ Please enter a number.")

def get_mode_interactive(platform):
    """Get mode selection from user interactively for Amstrad CPC"""
    if platform != 'amstrad_cpc':
        return None
        
    print("\n📺 Select Amstrad CPC mode:")
    modes = PLATFORMS[platform]['modes']
    for i, mode in enumerate(modes, 1):
        colors = PLATFORMS[platform]['colors'][mode]
        print(f"{i}. {mode} ({colors} colors)")
    
    while True:
        try:
            choice = int(input("\nEnter mode number: "))
            if 1 <= choice <= len(modes):
                return modes[choice - 1]
            print("❌ Invalid selection. Please try again.")
        except ValueError:
            print("❌ Please enter a number.")

def get_dimensions_interactive(platform, mode=None):
    """Get sprite dimensions from user interactively"""
    platform_config = PLATFORMS[platform]
    max_width = platform_config['max_width']
    max_height = platform_config['max_height']
    default_width = platform_config['default_width']
    default_height = platform_config['default_height']
    
    print(f"\n📏 Enter sprite dimensions (max: {max_width}x{max_height})")
    print(f"Press Enter for default size ({default_width}x{default_height})")
    
    while True:
        try:
            width_input = input(f"Width [{default_width}]: ").strip()
            height_input = input(f"Height [{default_height}]: ").strip()
            
            width = int(width_input) if width_input else default_width
            height = int(height_input) if height_input else default_height
            
            if 1 <= width <= max_width and 1 <= height <= max_height:
                return width, height
            print(f"❌ Dimensions must be between 1x1 and {max_width}x{max_height}")
        except ValueError:
            print("❌ Please enter valid numbers.")

def get_prompt_interactive():
    """Get sprite description from user interactively"""
    print("\n💭 Enter sprite description:")
    print("Example: running knight, shooting wizard, flying dragon")
    return input("> ").strip()

def parse_arguments():
    logger.debug("Analizando argumentos de línea de comandos")
    parser = argparse.ArgumentParser(description='Sprite generator using LLM')
    parser.add_argument('--prompt', type=str, required=True, help='Description of the sprite to generate')
    parser.add_argument('--platform', type=str, choices=list(PLATFORMS.keys()), required=True,
                      help='Target platform (spectrum or amstrad_cpc)')
    parser.add_argument('--mode', type=str, help='Display mode (for Amstrad CPC: mode0, mode1, mode2)')
    parser.add_argument('--width', type=int, required=True, help='Sprite width')
    parser.add_argument('--height', type=int, required=True, help='Sprite height')
    parser.add_argument('--negative-prompt', type=str, default='', help='Negative prompt for generation')
    
    args = parser.parse_args()
    logger.debug(f"Argumentos recibidos: {args}")
    
    # Validate provided arguments
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
        
    return args

def create_output_directory():
    logger.debug("Creando directorio de salida")
    
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

def load_prompt_template():
    """Load prompt template from resources file"""
    logger.debug("Cargando plantilla de prompt")
    platform = args.platform
    if args.platform == 'amstrad_cpc':
        platform = f"{args.platform}_{args.mode}"
    
    template_path = os.path.join("resources", f"sprite_prompt_{platform}.txt")
    logger.debug(f"Ruta de plantilla: {template_path} (existe: {os.path.exists(template_path)})")
    try:
        with open(template_path, "r") as f:
            template = f.read()
            logger.debug(f"Plantilla cargada ({len(template)} caracteres)")
            return template
    except Exception as e:
        logger.error(f"❌ Error loading prompt template: {str(e)}")
        sys.exit(1)

def generate_image_prompt(args):
    """Generate final prompt using template"""
    template = load_prompt_template()
    prompt = template.format(
        prompt=args.prompt,
        width=args.width,
        height=args.height
    )
    
    if args.negative_prompt:
        prompt += f"\n\nNegative prompts: {args.negative_prompt}"
    
    return prompt

def display_prompt(prompt):
    """Display final prompt in terminal"""
    print("\n💭 Final prompt:")
    print("═" * 80)
    print(prompt)
    print("═" * 80)

def process_image_for_platform(image, args):
    """Process image according to platform specifications"""
    platform_config = PLATFORMS[args.platform]
    
    # Convert to grayscale first for simplicity
    image = image.convert('L')
    
    # Resize to specified dimensions
    image = image.resize((args.width, args.height), Image.Resampling.NEAREST)
    
    if args.platform == 'spectrum':
        # ZX Spectrum: Simple black and white conversion
        image_array = np.array(image)
        threshold = 240
        binary_array = (image_array < threshold).astype(int)
    else:  # Amstrad CPC
        image_array = np.array(image)
        if args.mode == 'mode0':
            # Mode 0: 16 colors, 160x200 resolution
            # Convertir a niveles según la cantidad de colores
            num_colors = PLATFORMS[args.platform]['colors'][args.mode]
            levels = np.linspace(0, 255, num_colors)
            indices = np.digitize(image_array, levels) - 1
            # Asegurar que los valores estén en el rango correcto
            indices = np.clip(indices, 0, num_colors - 1)
            binary_array = indices
        elif args.mode == 'mode1':
            # Mode 1: 4 colors, 320x200 resolution
            num_colors = PLATFORMS[args.platform]['colors'][args.mode]
            levels = np.linspace(0, 255, num_colors)
            indices = np.digitize(image_array, levels) - 1
            indices = np.clip(indices, 0, num_colors - 1)
            binary_array = indices
        else:  # mode2
            # Mode 2: 2 colors, 640x200 resolution
            # Simple black and white conversion
            threshold = 240
            binary_array = (image_array < threshold).astype(int)
    
    return binary_array

def generate_sprite_text(binary_array, args):
    """Convert processed binary array to text representation with proper format for each platform/mode"""
    logger.debug("Convirtiendo matriz a representación de texto")
    sprite_text = ""
    
    if args.platform == 'spectrum':
        # ZX Spectrum: Binary representation (0 and 1)
        for row in binary_array:
            sprite_text += "".join(map(str, row)) + "\n"
    else:  # Amstrad CPC
        if args.mode == 'mode0':
            # Mode 0: Values from 0-15 for colors
            # Necesitamos usar un separador para diferenciar valores de dos dígitos
            for row in binary_array:
                # Usamos espacios como separadores entre valores
                row_text = " ".join(map(str, row))
                sprite_text += row_text + "\n"
        elif args.mode == 'mode1':
            # Mode 1: Values from 0-3 for colors
            for row in binary_array:
                sprite_text += "".join(map(str, row)) + "\n"
        else:  # mode2
            # Mode 2: Binary representation (0 and 1)
            for row in binary_array:
                sprite_text += "".join(map(str, row)) + "\n"
    
    logger.debug(f"Texto del sprite generado ({len(sprite_text)} caracteres)")
    return sprite_text

def generate_sprite(args, output_dir):
    logger.info(f"🤖 Generating sprite for {PLATFORMS[args.platform]['name']}...")
    logger.debug(f"Directorio de salida: {output_dir}")
    if args.platform == 'amstrad_cpc':
        logger.info(f"📺 Mode: {args.mode}")
    
    try:
        # Generate and display final prompt
        logger.debug("Generando prompt final")
        final_prompt = generate_image_prompt(args)
        display_prompt(final_prompt)
        
        logger.debug("Enviando solicitud a OpenAI")
        response = client.images.generate(
            model="dall-e-3",
            prompt=final_prompt,
            n=1,
            size="1024x1024",
            quality="standard",
            style="natural",
            response_format="b64_json"
        )
        
        logger.debug("Respuesta recibida de OpenAI")
        
        # Decode base64 image
        logger.debug("Decodificando imagen base64")
        image_data = base64.b64decode(response.data[0].b64_json)
        image = Image.open(io.BytesIO(image_data))
        logger.debug(f"Imagen decodificada: {image.size}")
        
        # Save original image
        original_file = os.path.join(output_dir, "original.png")
        logger.debug(f"Guardando imagen original en: {original_file}")
        image.save(original_file)
        logger.info(f"✅ Original image saved: {original_file}")
        
        # Process image according to platform
        logger.debug("Procesando imagen según la plataforma")
        binary_array = process_image_for_platform(image, args)
        logger.debug(f"Array procesado shape: {binary_array.shape}")
        
        # Generate sprite text
        sprite_text = generate_sprite_text(binary_array, args)
        
        # Crear una imagen del sprite procesado para visualización
        processed_image = create_processed_image(binary_array, args)
        
        return processed_image, sprite_text
        
    except Exception as e:
        logger.error(f"❌ Error generating sprite: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        # If there's an error, remove the created directory
        import shutil
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        sys.exit(1)

def create_processed_image(binary_array, args):
    """Create a processed image from the binary array for visualization"""
    logger.debug("Creando imagen procesada para visualización")
    
    # Create a new image with the processed data
    height, width = binary_array.shape
    processed_image = Image.new('RGB', (width, height), color='white')
    pixels = processed_image.load()
    
    # Define colors based on platform and mode
    if args.platform == 'spectrum':
        # ZX Spectrum colors (black and white)
        color_map = {
            0: (255, 255, 255),  # White (background)
            1: (0, 0, 0)         # Black
        }
    else:  # Amstrad CPC
        if args.mode == 'mode0':
            # Mode 0: 16 colores estándar de Amstrad CPC
            color_map = {
                0: (0, 0, 0),         # Negro
                1: (0, 0, 128),       # Azul
                2: (0, 0, 255),       # Azul brillante
                3: (128, 0, 0),       # Rojo
                4: (128, 0, 128),     # Magenta
                5: (128, 0, 255),     # Magenta brillante
                6: (255, 0, 0),       # Rojo brillante
                7: (255, 0, 128),     # Púrpura
                8: (255, 0, 255),     # Púrpura brillante
                9: (0, 128, 0),       # Verde
                10: (0, 128, 128),    # Turquesa
                11: (0, 128, 255),    # Azul cielo
                12: (0, 255, 0),      # Verde brillante
                13: (0, 255, 128),    # Turquesa brillante
                14: (0, 255, 255),    # Cian brillante
                15: (255, 255, 255)   # Blanco
            }
        elif args.mode == 'mode1':
            # Mode 1: 4 colors
            color_map = {
                0: (0, 0, 0),          # Negro
                1: (0, 255, 0),        # Verde
                2: (255, 0, 0),        # Rojo
                3: (255, 255, 255)     # Blanco
            }
        else:  # mode2
            # Mode 2: 2 colors (black and white)
            color_map = {
                0: (255, 255, 255),  # White (background)
                1: (0, 0, 0)         # Black
            }
    
    # Set pixels according to the binary array and color map
    for y in range(height):
        for x in range(width):
            value = int(binary_array[y, x])
            if value in color_map:
                pixels[x, y] = color_map[value]
            else:
                # Valor fuera de rango, usar color por defecto
                pixels[x, y] = (128, 128, 128)  # Gris como fallback
    
    return processed_image

def display_sprite(sprite_text):
    """Display visual representation of sprite in terminal"""
    print("\n")
    print("████████████████████████████████████████")
    print("█      🎨 Generated sprite:            █")
    print("████████████████████████████████████████")
    print("═" * (args.width + 4))
    
    lines = sprite_text.strip().split("\n")
    for line in lines:
        if args.platform == 'spectrum':
            # ZX Spectrum: 2 colores
            visual_line = line.replace("0", "·").replace("1", "█")
        else:  # Amstrad CPC
            if args.mode == 'mode0':
                # Mode 0: 16 colores - usamos diferentes caracteres para representarlos
                # Representamos con una variedad de caracteres para distinguir entre los 16 valores
                visual_line = ""
                # Separar por espacios (modo 0 usa espacios como separadores)
                values = line.strip().split()
                for value in values:
                    if value == "0":
                        visual_line += " "    # Negro (fondo)
                    elif value == "1":
                        visual_line += "."    # Azul (punto)
                    elif value == "2":
                        visual_line += ":"    # Azul brillante (dos puntos)
                    elif value == "3":
                        visual_line += "¡"    # Rojo (exclamación invertida)
                    elif value == "4":
                        visual_line += "!"    # Magenta (exclamación)
                    elif value == "5":
                        visual_line += "?"    # Magenta brillante (interrogación)
                    elif value == "6":
                        visual_line += "+"    # Rojo brillante (más)
                    elif value == "7":
                        visual_line += "*"    # Púrpura (asterisco)
                    elif value == "8":
                        visual_line += "="    # Púrpura brillante (igual)
                    elif value == "9":
                        visual_line += "-"    # Verde (guión)
                    elif value == "10":
                        visual_line += "_"    # Turquesa (guión bajo)
                    elif value == "11":
                        visual_line += "~"    # Azul cielo (tilde)
                    elif value == "12":
                        visual_line += "#"    # Verde brillante (almohadilla)
                    elif value == "13":
                        visual_line += "@"    # Turquesa brillante (arroba)
                    elif value == "14":
                        visual_line += "o"    # Cian brillante (o minúscula)
                    elif value == "15":
                        visual_line += "█"    # Blanco (bloque completo)
                    else:
                        visual_line += "?"    # Valor desconocido
                
            elif args.mode == 'mode1':
                # Mode 1: 4 colores
                visual_line = line.replace("0", " ").replace("1", "░").replace("2", "▒").replace("3", "█")
            else:  # mode2
                # Mode 2: 2 colores (blanco y negro)
                visual_line = line.replace("0", "·").replace("1", "█")
        
        # Asegurarse de que la línea tenga el ancho correcto
        if len(visual_line) < args.width:
            visual_line = visual_line.ljust(args.width)
        elif len(visual_line) > args.width:
            visual_line = visual_line[:args.width]
            
        print(f"║ {visual_line} ║")
    
    print("═" * (args.width + 4))
    print("████████████████████████████████████████")

def save_sprite(image, sprite_text, output_dir, args):
    # Save processed PNG image
    png_file = os.path.join(output_dir, "sprite.png")
    image.save(png_file)
    logger.info(f"✅ Processed image saved: {png_file}")
    
    # Save sprite as text
    txt_file = os.path.join(output_dir, "sprite.txt")
    with open(txt_file, "w") as f:
        f.write(sprite_text)
    logger.info(f"✅ Matrix saved: {txt_file}")
    
    # Save original prompt
    prompt_file = os.path.join(output_dir, "prompt.txt")
    with open(prompt_file, "w") as f:
        f.write(args.prompt)
    
    # Save configuration information
    config_file = os.path.join(output_dir, "config.json")
    config = {
        "platform": args.platform,
        "mode": args.mode if args.platform == 'amstrad_cpc' else None,
        "width": args.width,
        "height": args.height,
        "timestamp": datetime.datetime.now().isoformat(),
        "prompt": args.prompt,
        "negative_prompt": args.negative_prompt
    }
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)
    
    return png_file, txt_file

# Función para mostrar imágenes en terminal compatible (como Kitty)
def display_image_in_terminal(image_path):
    """Muestra una imagen directamente en la terminal si es compatible"""
    try:
        # Verificar si estamos en Kitty
        if "KITTY_WINDOW_ID" in os.environ or "TERM" in os.environ and "kitty" in os.environ.get("TERM", ""):
            logger.debug(f"Terminal Kitty detectada, mostrando imagen: {image_path}")
            try:
                # Usar subprocess.run con shell=True para manejar mejor la ejecución
                cmd = f"kitty +kitten icat {image_path}"
                logger.debug(f"Ejecutando comando: {cmd}")
                result = subprocess.run(cmd, shell=True, check=False)
                if result.returncode == 0:
                    logger.debug("Imagen mostrada correctamente en Kitty")
                    return True
                else:
                    logger.debug(f"Error al mostrar imagen en Kitty: {result.returncode}")
            except Exception as e:
                logger.debug(f"Error al mostrar imagen en Kitty: {str(e)}")
        
        # Si no estamos en Kitty o falló, abrir con el visor predeterminado
        logger.debug("Abriendo imagen con visor predeterminado...")
        
        if sys.platform.startswith('linux'):
            try:
                subprocess.run(['xdg-open', image_path], check=False)
                logger.info(f"✅ Imagen abierta con el visor predeterminado: {image_path}")
                return True
            except Exception as e:
                logger.debug(f"Error al abrir la imagen con 'xdg-open': {str(e)}")
        elif sys.platform == 'darwin':  # macOS
            try:
                subprocess.run(['open', image_path], check=False)
                logger.info(f"✅ Imagen abierta con el visor predeterminado: {image_path}")
                return True
            except Exception as e:
                logger.debug(f"Error al abrir la imagen con 'open': {str(e)}")
        elif sys.platform == 'win32':  # Windows
            try:
                os.startfile(image_path)
                logger.info(f"✅ Imagen abierta con el visor predeterminado: {image_path}")
                return True
            except Exception as e:
                logger.debug(f"Error al abrir la imagen con 'startfile': {str(e)}")
        
        return False
    except Exception as e:
        logger.debug(f"Error al mostrar imagen en terminal: {str(e)}")
        return False

if __name__ == "__main__":
    try:
        logger.debug("🚀 Iniciando programa principal")
        args = parse_arguments()
        output_dir = create_output_directory()
        
        logger.info(f"🔍 Generating sprite: {args.prompt}")
        logger.info(f"📏 Size: {args.width}x{args.height}")
        
        start_time = time.time()
        image, sprite_text = generate_sprite(args, output_dir)
        generation_time = time.time() - start_time
        
        png_file, txt_file = save_sprite(image, sprite_text, output_dir, args)
        
        # Mostrar SOLO la imagen original en terminal o visor
        original_file = os.path.join(output_dir, "original.png")
        if os.path.exists(original_file):
            logger.info(f"🖼️ Mostrando imagen generada")
            display_image_in_terminal(original_file)
        
        # Mostrar representación ASCII del sprite
        display_sprite(sprite_text)
        
        logger.info(f"✨ Process completed in {generation_time:.2f} seconds")
        logger.info(f"📂 Files saved in: {output_dir}")
    except Exception as e:
        logger.error(f"❌ Error general: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1) 