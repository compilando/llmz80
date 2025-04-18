import os
import base64
import io
import logging
from openai import OpenAI, BadRequestError
from PIL import Image
from dotenv import load_dotenv

from .base import BaseImageGenerator

logger = logging.getLogger(__name__)

class OpenAIImageGenerator(BaseImageGenerator):
    """Image generator using OpenAI's DALL-E models."""

    def __init__(self, api_key: str = None, model: str = "dall-e-3"):
        load_dotenv() # Load from .env if api_key is not provided directly
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable or pass it directly.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        logger.info(f"OpenAI Image Generator initialized with model: {self.model}")

    def generate_image(self, prompt: str) -> Image.Image:
        """Generates an image using the OpenAI API."""
        logger.info(f"🤖 Generating image with OpenAI ({self.model})...")
        logger.debug(f"Prompt: {prompt[:100]}...")
        
        try:
            response = self.client.images.generate(
                model=self.model,
                prompt=prompt,
                n=1,
                size="1024x1024", # DALL-E 3 preferred size
                quality="standard", # Use standard for potentially faster/cheaper generation
                style="natural", # Style for DALL-E 3, could be vivid
                response_format="b64_json"
            )
            
            logger.debug("Respuesta recibida de OpenAI")
            if not response.data or not response.data[0].b64_json:
                raise Exception("Respuesta inválida de OpenAI: No se encontró b64_json.")

            # Decode base64 image
            logger.debug("Decodificando imagen base64")
            image_data = base64.b64decode(response.data[0].b64_json)
            image = Image.open(io.BytesIO(image_data))
            logger.info(f"✅ Image generated successfully by OpenAI ({image.size})")
            return image

        except BadRequestError as e:
            logger.error(f"❌ Error en la solicitud a OpenAI (Bad Request): {e.response.status_code} - {e.response.text}")
            # Re-raise a more specific error or handle it
            raise Exception(f"OpenAI API Bad Request: {e.response.text}") from e
        except Exception as e:
            logger.error(f"❌ Error inesperado durante la generación con OpenAI: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise Exception(f"Error generando imagen con OpenAI: {str(e)}") from e
