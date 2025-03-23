#!/usr/bin/env python3

import os
import sys
import argparse
import datetime
import time
import json
import logging
import openai
from openai import OpenAI
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Cargar variables de entorno desde .env
load_dotenv()

# Verificar si existe la API key de OpenAI
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    logger.error("❌ Error: OPENAI_API_KEY no está configurada en el archivo .env")
    logger.info("💡 Crea un archivo .env con tu API key: OPENAI_API_KEY=tu_api_key")
    sys.exit(1)

# Inicializar el cliente de OpenAI
client = OpenAI(api_key=api_key)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Generador de sprites usando LLM')
    parser.add_argument('--prompt', type=str, required=True, help='Descripción del sprite a generar')
    parser.add_argument('--width', type=int, default=8, help='Ancho del sprite (múltiplo de 8)')
    parser.add_argument('--height', type=int, default=8, help='Alto del sprite (múltiplo de 8)')
    parser.add_argument('--model', type=str, default='gpt-4o', help='Modelo de OpenAI a utilizar')
    
    args = parser.parse_args()
    
    # Validar que las dimensiones sean múltiplos de 8
    if args.width % 8 != 0 or args.height % 8 != 0:
        logger.error("❌ Error: El ancho y alto deben ser múltiplos de 8")
        sys.exit(1)
        
    return args

def create_output_directory():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    prompt_slug = "-".join(args.prompt.lower().split()[:3])
    directory = f"sprites/{timestamp}_{prompt_slug}"
    
    os.makedirs(directory, exist_ok=True)
    logger.info(f"✅ Directorio creado: {directory}")
    
    return directory

def generate_sprite(args, output_dir):
    logger.info("🤖 Generando sprite con LLM...")
    
    system_prompt = f"""
        Eres un diseñador experto en pixel art retro para videojuegos de 8/16 bits. 
        Generarás sprites monocromáticos de {args.width}x{args.height} píxeles usando 
        solo 0 (transparente) y 1 (color sólido).

        Instrucciones técnicas:
        1. Estilo retro: Usar técnicas de NES/Game Boy (siluetas reconocibles, patrones de dithering para sombras)
        2. Priorizar:
        - Silueta clara y reconocible desde 2 metros
        - Contraste alto entre zonas activas y fondo
        - Detalle mínimo pero expresivo (ej: ojos=2px, armas=líneas rectas)
        3. Estructura por capas:
        [Línea exterior] 1px de borde continuo (excepto en íconos pequeños)
        [Cuerpo principal] Patrones geométricos simétricos
        [Detalles] Máximo 3 píxeles de profundidad para texturas

        Formato requerido:
        - Exactamente {args.height} líneas
        - {args.width} caracteres por línea (solo 0/1)
        - Sin bordes/separadores
        - Encabezado y comentarios prohibidos

        Ejemplo para sprite 8x8 "nave espacial":
        00011000
        00111100
        01111110
        11100111
        11111111
        00111100
        00111100
        00000000

    """
   
    user_prompt = f"Crea un sprite de {args.width}x{args.height} que represente: {args.prompt}"
    
    try:
        response = client.chat.completions.create(
            model=args.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )
        
        sprite_text = response.choices[0].message.content.strip()
        
        # Extraer solo la matriz de 0 y 1
        if "```" in sprite_text:
            sprite_text = sprite_text.split("```")[1].strip()
            if sprite_text.startswith("python") or sprite_text.startswith("text"):
                sprite_text = "\n".join(sprite_text.split("\n")[1:])
        
        # Validar dimensiones
        lines = sprite_text.strip().split("\n")
        if len(lines) != args.height:
            logger.warning(f"⚠️ La altura del sprite generado ({len(lines)}) no coincide con la solicitada ({args.height})")
            
        for i, line in enumerate(lines):
            if len(line.strip()) != args.width:
                logger.warning(f"⚠️ La fila {i+1} tiene {len(line.strip())} columnas en lugar de {args.width}")
        
        return sprite_text
        
    except Exception as e:
        logger.error(f"❌ Error al generar el sprite: {str(e)}")
        sys.exit(1)

def save_sprite(sprite_text, output_dir, args):
    # Guardar el sprite en formato de texto
    sprite_file = os.path.join(output_dir, "sprite.txt")
    with open(sprite_file, "w") as f:
        f.write(sprite_text)
    
    # Guardar el prompt original
    prompt_file = os.path.join(output_dir, "prompt.txt")
    with open(prompt_file, "w") as f:
        f.write(args.prompt)
    
    # Guardar información de configuración
    config_file = os.path.join(output_dir, "config.json")
    config = {
        "width": args.width,
        "height": args.height,
        "model": args.model,
        "timestamp": datetime.datetime.now().isoformat(),
        "prompt": args.prompt
    }
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)
    
    logger.info(f"✅ Sprite guardado en: {sprite_file}")
    return sprite_file

def display_sprite(sprite_text):
    """Muestra una representación visual del sprite en la terminal"""
    print("\n🎨 Sprite generado:")
    print("═" * (args.width + 4))
    
    lines = sprite_text.strip().split("\n")
    for line in lines:
        visual_line = line.replace("0", "·").replace("1", "█")
        print(f"║ {visual_line} ║")
    
    print("═" * (args.width + 4))

if __name__ == "__main__":
    args = parse_arguments()
    output_dir = create_output_directory()
    
    logger.info(f"🔍 Generando sprite: {args.prompt}")
    logger.info(f"📏 Dimensiones: {args.width}x{args.height}")
    
    start_time = time.time()
    sprite_text = generate_sprite(args, output_dir)
    generation_time = time.time() - start_time
    
    sprite_file = save_sprite(sprite_text, output_dir, args)
    display_sprite(sprite_text)
    
    logger.info(f"✨ Proceso completado en {generation_time:.2f} segundos")
    logger.info(f"📂 Archivos guardados en: {output_dir}") 