import numpy as np
from PIL import Image
import logging
import os
import sys
import subprocess
from scipy.ndimage import label, sum as ndi_sum
import json
import datetime

# Import palettes and config loading from config.py
from config import get_palette_for_platform, PLATFORMS

logger = logging.getLogger(__name__)

def generate_sprite_text(binary_array, args):
    """Convert processed binary array to text representation with proper format for each platform/mode"""
    logger.debug("Convirtiendo matriz a representación de texto")
    sprite_text = ""
    height, width = binary_array.shape

    if args.platform == 'spectrum':
        # ZX Spectrum: Binary representation (0 and 1)
        for row in binary_array:
            sprite_text += "".join(map(str, row)) + "\n"
    elif args.platform == 'amstrad_cpc':
        num_colors = PLATFORMS[args.platform]['colors'].get(args.mode, 2)
        if args.mode == 'mode0': # 16 colors
            # Use spaces for values >= 10
            for row in binary_array:
                row_text = " ".join(map(str, row))
                sprite_text += row_text + "\n"
        elif args.mode == 'mode1': # 4 colors (0-3)
            for row in binary_array:
                sprite_text += "".join(map(str, row)) + "\n"
        elif args.mode == 'mode2': # 2 colors (0-1)
             for row in binary_array:
                 sprite_text += "".join(map(str, row)) + "\n"
        else:
            logger.warning(f"Modo Amstrad desconocido '{args.mode}' para generar texto. Usando formato binario.")
            for row in binary_array:
                 sprite_text += "".join(map(str, row)) + "\n"
    else:
        logger.warning(f"Plataforma desconocida '{args.platform}' para generar texto. Usando formato binario.")
        for row in binary_array:
             sprite_text += "".join(map(str, row)) + "\n"

    logger.debug(f"Texto del sprite generado ({len(sprite_text)} caracteres)")
    return sprite_text.strip() # Remove trailing newline

def display_sprite(binary_array, args):
    """Display visual representation of sprite in terminal using ANSI background colors."""
    print("\n")
    print("█" * 40)
    print("█      🎨 Generated sprite (ANSI):     █")
    print("█" * 40)

    height, width = binary_array.shape
    terminal_width = max(width, 20) # Single char per pixel

    # Get the correct RGB color map (using args directly)
    palette_rgb_tuples = get_palette_for_platform(args.platform, args.mode)
    color_map_rgb = {i: rgb for i, rgb in enumerate(palette_rgb_tuples)}
    if not color_map_rgb:
        logger.error("No se pudo obtener el mapa de colores para la previsualización ANSI.")
        return # Don't display if color map failed

    # Print sprite with ANSI background colors
    for y in range(height):
        print(" ", end="") # Start of line
        for x in range(width):
            color_index = int(binary_array[y, x])
            # Get RGB color, use gray if index is out of bounds
            rgb = color_map_rgb.get(color_index, (128, 128, 128))
            # ANSI sequence for True Color background
            ansi_bg_color = f"\033[48;2;{rgb[0]};{rgb[1]};{rgb[2]}m"
            # Print a single space with the background color
            print(f"{ansi_bg_color} ", end="")
        # Reset color at the end of the line
        print("\033[0m")
    print("\n" + "█" * 40)


def display_image_in_terminal(image_path):
    """Muestra una imagen directamente en la terminal si es compatible"""
    logger.debug(f"Entering display_image_in_terminal for path: {image_path}")
    if not os.path.exists(image_path):
        logger.warning(f"Cannot display image: File not found at {image_path}")
        return False
    try:
        # Check for Kitty terminal
        if "KITTY_WINDOW_ID" in os.environ or ("TERM" in os.environ and "kitty" in os.environ.get("TERM", "")):
            logger.debug(f"Terminal Kitty detectada, mostrando imagen: {image_path}")
            try:
                cmd = f"kitty +kitten icat \"{image_path}\""
                logger.debug(f"Ejecutando comando: {cmd}")
                result = subprocess.run(cmd, shell=True, check=False, capture_output=True, text=True)
                if result.returncode == 0:
                    logger.debug("Imagen mostrada correctamente en Kitty")
                    return True
                else:
                    logger.debug(f"Error al mostrar imagen en Kitty ({result.returncode}): {result.stderr}")
                    # Fall through to default viewer if kitty fails
            except Exception as e:
                logger.debug(f"Error al intentar mostrar imagen en Kitty: {str(e)}")
                # Fall through to default viewer

        # If not Kitty or Kitty failed, use default OS viewer
        logger.info("Intentando abrir imagen con visor predeterminado del sistema...")
        opened = False
        fallback_error = None
        if sys.platform.startswith('linux'):
            try:
                # Use subprocess.run with capture_output to check for errors
                result = subprocess.run(['xdg-open', image_path], check=False, capture_output=True, text=True)
                if result.returncode == 0:
                    opened = True
                else:
                    fallback_error = f"'xdg-open' falló con código {result.returncode}: {result.stderr.strip()}"
            except FileNotFoundError:
                 fallback_error = "Comando 'xdg-open' no encontrado."
            except Exception as e:
                fallback_error = f"Error inesperado con 'xdg-open': {str(e)}"
        elif sys.platform == 'darwin':  # macOS
            try:
                result = subprocess.run(['open', image_path], check=False, capture_output=True, text=True)
                if result.returncode == 0:
                    opened = True
                else:
                     fallback_error = f"'open' falló con código {result.returncode}: {result.stderr.strip()}"
            except FileNotFoundError:
                 fallback_error = "Comando 'open' no encontrado."
            except Exception as e:
                fallback_error = f"Error inesperado con 'open': {str(e)}"
        elif sys.platform == 'win32':  # Windows
            try:
                os.startfile(image_path)
                opened = True # Assume success if no immediate error
            except FileNotFoundError:
                 fallback_error = f"Archivo no encontrado para 'os.startfile': {image_path}"
            except Exception as e:
                fallback_error = f"Error inesperado con 'os.startfile': {str(e)}"

        if opened:
             logger.info(f"✅ Imagen abierta (o intento enviado) con el visor predeterminado: {image_path}")
             return True
        else:
             logger.warning(f"⚠️ No se pudo abrir la imagen con el visor predeterminado: {fallback_error or 'Razón desconocida.'}")
             return False

    except Exception as e:
        logger.error(f"Error inesperado al mostrar imagen en terminal: {str(e)}")
        return False

def _clean_image(im: Image.Image, background_color: tuple = (255, 255, 255), tolerance: int = 10) -> Image.Image:
    """Attempts to clean the image by finding the largest connected non-background object."""
    logger.info("🧼 Cleaning image: Finding largest object...")

    im_rgb = im.convert('RGB')
    width, height = im_rgb.size
    data = np.array(im_rgb)
    bg_color_np = np.array(background_color)

    # Create a mask where pixels are NOT background (within tolerance)
    diff = np.abs(data - bg_color_np)
    mask = ~np.all(diff <= tolerance, axis=2)

    # Find connected components in the mask
    labeled_array, num_features = label(mask)

    if num_features == 0:
        logger.warning("⚠️ No object found on background. Returning original image.")
        return im

    # Calculate the size of each component (feature)
    component_sizes = ndi_sum(mask, labeled_array, range(1, num_features + 1))

    if component_sizes.size == 0:
        logger.warning("⚠️ No components found after labeling. Returning original image.")
        return im

    # Find the label of the largest component
    largest_component_label = np.argmax(component_sizes) + 1 # Add 1 because range started at 1

    # Create a mask containing only the largest component
    largest_component_mask = (labeled_array == largest_component_label)

    # Find bounding box of the largest component
    coords = np.argwhere(largest_component_mask)
    if coords.size == 0:
         logger.warning("⚠️ Largest component mask is empty. Returning original image.")
         return im

    y0, x0 = coords.min(axis=0)
    y1, x1 = coords.max(axis=0)

    # Crop the original image based on the largest component's bounding box
    cropped_im = im.crop((x0, y0, x1 + 1, y1 + 1))

    # Create a corresponding mask for the cropped image
    cropped_mask = largest_component_mask[y0:y1+1, x0:x1+1]

    # Create a new image with white background, same size as cropped image
    cleaned_im = Image.new(cropped_im.mode, cropped_im.size, background_color)

    # Paste the object pixels (using the mask) onto the clean background
    pil_mask = Image.fromarray(cropped_mask.astype(np.uint8) * 255).convert('L')
    cleaned_im.paste(cropped_im, (0, 0), mask=pil_mask)

    logger.info(f"✅ Image cleaned. Kept largest component, size: {cleaned_im.size}.")
    return cleaned_im

def _scale_image(im: Image.Image, target_width: int, target_height: int) -> Image.Image:
    """Scales the image to the target dimensions using nearest neighbor interpolation."""
    logger.info(f"📏 Scaling image to {target_width}x{target_height} using NEAREST resampling...")
    scaled_im = im.resize((target_width, target_height), Image.Resampling.NEAREST)
    logger.info("✅ Image scaling complete.")
    return scaled_im

def _process_image(im: Image.Image, platform: str, mode: str) -> Image.Image:
    """Processes the image to match platform color constraints using dithering. Does NOT resize."""
    logger.info("🎨 Processing image to match platform palette...")

    palette_rgb_tuples = get_palette_for_platform(platform, mode)
    num_defined_colors = len(palette_rgb_tuples)

    # Create palette for Pillow (flat list [R1, G1, B1, R2, G2, B2, ...])
    palette_values = [val for rgb in palette_rgb_tuples for val in rgb]

    # Ensure palette has 256 entries (768 bytes)
    if num_defined_colors < 256:
        fill_color = palette_values[-3:] if palette_values else [0, 0, 0]
        palette_values.extend(fill_color * (256 - num_defined_colors))
    elif num_defined_colors > 256:
        logger.warning("La paleta definida tiene más de 256 colores, truncando.")
        palette_values = palette_values[:768]

    # Create palette image (P mode)
    palette_im = Image.new('P', (16, 16)) # Arbitrary size
    palette_im.putpalette(palette_values)

    # Quantize the image to the defined palette WITHOUT dithering
    logger.info(f"Quantizing image ({im.size}) to {num_defined_colors} colors WITHOUT dithering...")
    im_rgb = im.convert('RGB')
    im_quantized = im_rgb.quantize(colors=min(num_defined_colors, 255), palette=palette_im, dither=Image.Dither.NONE)

    logger.info("✅ Image quantization complete.")
    return im_quantized # Return quantized image (Mode 'P')

# --- Pipeline Function --- 

def process_image_pipeline(image: Image.Image, args) -> tuple[Image.Image, np.ndarray]:
    """Runs the full image processing pipeline: clean -> process -> scale -> get array.
    
    Args:
        image: The raw PIL image from the generator.
        args: The command line arguments namespace.

    Returns:
        A tuple containing:
        - processed_rgb_image: The final PIL image in RGB mode.
        - binary_array: The numpy array representing the final indexed image.
    """
    logger.info("🚀 Starting image processing pipeline...")
    # 1. Clean Image (Remove excess background)
    cleaned_image = _clean_image(image)

    # 2. Process Image (Apply Platform Palette with Dithering)
    palettized_image = _process_image(cleaned_image, args.platform, args.mode)

    # 3. Scale Image (Resize to target dimensions)
    final_image = _scale_image(palettized_image, args.width, args.height)

    # --- Generate final outputs ---
    # Create the numpy array from the final processed image (Mode 'P')
    image_array = np.array(final_image) 
    binary_array = image_array.astype(int)
    logger.debug(f"Array final shape: {binary_array.shape}, dtype: {binary_array.dtype}")

    # Create an RGB version of the final sprite for saving/displaying
    processed_rgb_image = final_image.convert('RGB')
    
    logger.info("✅ Image processing pipeline complete.")
    return processed_rgb_image, binary_array

def save_results(processed_image, binary_array, output_dir, args, llm_prompt):
    """Saves the processed image, matrix, config and LLM prompt.

    Returns:
        A tuple (png_file_path, txt_file_path) if successful, otherwise (None, None).
    """
    logger.debug(f"Guardando resultados en: {output_dir}")
    png_file = None
    txt_file = None
    try:
        # Ensure output directory exists (it should, but double-check)
        os.makedirs(output_dir, exist_ok=True)

        # Save processed PNG image (final size, final palette)
        png_file = os.path.join(output_dir, "sprite.png")
        processed_image.save(png_file)
        logger.info(f"✅ Imagen procesada guardada: {png_file}")

        # Save sprite as text matrix
        txt_file = os.path.join(output_dir, "sprite.txt")
        # generate_sprite_text is already defined in this file
        sprite_text = generate_sprite_text(binary_array, args) 
        with open(txt_file, "w") as f:
            f.write(sprite_text)
        logger.info(f"✅ Matriz de texto guardada: {txt_file}")

        # Save the LLM prompt used for generation
        prompt_file = os.path.join(output_dir, "llm_prompt.txt")
        with open(prompt_file, "w") as f:
            f.write(llm_prompt)
        logger.info(f"✅ Prompt LLM guardado: {prompt_file}")

        # Save configuration information
        config_file = os.path.join(output_dir, "config.json")
        config_data = {
            "generator": args.generator,
            "platform": args.platform,
            "mode": args.mode if args.platform == 'amstrad_cpc' else None,
            "width": args.width,
            "height": args.height,
            "timestamp": datetime.datetime.now().isoformat(), # Need datetime import
            "user_prompt": args.prompt,
            "negative_prompt": args.negative_prompt
        }
        with open(config_file, "w") as f:
            json.dump(config_data, f, indent=2)
        logger.info(f"✅ Configuración guardada: {config_file}")

        return png_file, txt_file # Return paths ONLY if all saves were successful

    except IOError as e:
        logger.error(f"❌ Error de E/S al guardar archivos en '{output_dir}'", exc_info=True)
    except Exception as e:
        logger.error(f"❌ Error inesperado al guardar resultados", exc_info=True)
        
    # If any exception occurred, return None
    return None, None
