import os
import base64
import io
import logging
from openai import OpenAI, BadRequestError
from PIL import Image
from dotenv import load_dotenv

from .base import BaseImageGenerator

logger = logging.getLogger(__name__)

#: Model names in this family (currently just `gpt-image-1`) take a request
#: shape incompatible with dall-e-2/dall-e-3 -- see `_request_params` below
#: for exactly how, and why. Matched by prefix, not exact string, so a future
#: `gpt-image-1-mini`-style name does not need a code change here too.
_GPT_IMAGE_PREFIX = "gpt-image"


class OpenAIImageGenerator(BaseImageGenerator):
    """Image generator using OpenAI's image models.

    Two request shapes are supported, because both are genuinely in use: the
    historical default, `dall-e-3` (`llm_sprites.py` still constructs this
    class with no `model` argument and relies on that default), and
    `gpt-image-1`, which Studio's sprite pipeline now configures instead (see
    `config.yml`'s `openai.image_model`) because it follows the strict "no
    anti-aliasing, blocky pixels" instructions in
    `resources/sprite_prompt_spectrum.txt` far better than dall-e-3 does.

    The two families do not accept the same parameters -- confirmed against
    OpenAI's own API reference, not assumed:

    - `response_format` and `style` are dall-e-3-only. OpenAI's docs say it
      plainly for the first: "This parameter isn't supported for the GPT
      image models, which always return base64-encoded images." `style` is
      documented as dall-e-3-only outright.
    - `quality` uses a different vocabulary per family: `standard`/`hd` for
      dall-e-3, `low`/`medium`/`high`/`auto` for gpt-image-1.

    None of this is caught locally by the installed SDK (openai==1.75.0,
    which predates gpt-image-1 -- its `ImageModel` type is a `Literal` of
    just `"dall-e-2"`/`"dall-e-3"`, and its `quality` type only knows
    `"standard"`/`"hd"`). Those are static, mypy-only hints; nothing in the
    SDK's request path checks a `Literal` at runtime, so an unrecognised
    `model` or `quality` string still reaches OpenAI's API unmodified, which
    is what actually enforces which parameters are valid for which model --
    with a 400 if this class got the split below wrong.
    """

    def __init__(self, api_key: str = None, model: str = "dall-e-3"):
        load_dotenv() # Load from .env if api_key is not provided directly
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable or pass it directly.")

        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        logger.info(f"OpenAI Image Generator initialized with model: {self.model}")

    def _is_gpt_image_model(self) -> bool:
        return self.model.startswith(_GPT_IMAGE_PREFIX)

    def _request_params(self, prompt: str) -> dict:
        """The `images.generate` kwargs for `self.model`, and only those it accepts."""
        params = {
            "model": self.model,
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024",
        }
        if self._is_gpt_image_model():
            # gpt-image-1: no response_format (always base64), no style;
            # quality is low/medium/high/auto. "high" trades cost for the
            # crisp, literal instruction-following this pipeline needs.
            params["quality"] = "high"
        else:
            # dall-e-2 / dall-e-3: response_format must be spelled out to get
            # base64 back at all, and style/standard-hd quality both exist.
            params["quality"] = "standard"
            params["style"] = "natural"
            params["response_format"] = "b64_json"
        return params

    def generate_image(self, prompt: str) -> Image.Image:
        """Generates an image using the OpenAI API."""
        logger.info(f"🤖 Generating image with OpenAI ({self.model})...")
        logger.debug(f"Prompt: {prompt[:100]}...")

        try:
            response = self.client.images.generate(**self._request_params(prompt))

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
