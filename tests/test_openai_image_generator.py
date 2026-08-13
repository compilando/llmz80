"""`OpenAIImageGenerator`, judged on the request it builds for each model.

No API call is made anywhere in this file: `self.client.images.generate` is
always monkeypatched to a stub that records what it was called with and
returns a small, fixed base64-encoded image, exactly like
`test_sprite_artist.py` fakes the image generator a layer up.
"""

from __future__ import annotations

import base64
import io

import pytest
from openai.types.image import Image as OpenAIImage
from openai.types.images_response import ImagesResponse
from PIL import Image

from generators.openai_generator import OpenAIImageGenerator


def _b64_pixel() -> str:
    """A tiny, valid PNG, base64-encoded -- enough for `Image.open` to decode."""
    buffer = io.BytesIO()
    Image.new("RGBA", (2, 2), (255, 0, 0, 255)).save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("ascii")


class _RecordingImages:
    """Stands in for `client.images`: records the kwargs `generate` received."""

    def __init__(self) -> None:
        self.calls: list[dict] = []

    def generate(self, **kwargs):
        self.calls.append(kwargs)
        return ImagesResponse(created=0, data=[OpenAIImage(b64_json=_b64_pixel())])


@pytest.fixture
def generator_and_images():
    generator = OpenAIImageGenerator(api_key="test-key")
    images = _RecordingImages()
    generator.client.images = images
    return generator, images


class TestRequestParams:
    """`_request_params` decides what reaches the API before any call is made."""

    def test_dall_e_3_gets_response_format_and_style_and_standard_quality(self):
        generator = OpenAIImageGenerator(api_key="test-key", model="dall-e-3")
        params = generator._request_params("a sprite")
        assert params["response_format"] == "b64_json"
        assert params["style"] == "natural"
        assert params["quality"] == "standard"

    def test_gpt_image_1_gets_none_of_dall_e_3s_extra_params(self):
        generator = OpenAIImageGenerator(api_key="test-key", model="gpt-image-1")
        params = generator._request_params("a sprite")
        assert "response_format" not in params
        assert "style" not in params
        assert params["quality"] == "high"

    def test_default_model_is_still_dall_e_3(self):
        generator = OpenAIImageGenerator(api_key="test-key")
        assert generator.model == "dall-e-3"
        assert "response_format" in generator._request_params("a sprite")

    def test_both_models_share_prompt_count_and_size(self):
        dalle = OpenAIImageGenerator(api_key="test-key", model="dall-e-3")._request_params("x")
        gpt = OpenAIImageGenerator(api_key="test-key", model="gpt-image-1")._request_params("x")
        for params in (dalle, gpt):
            assert params["prompt"] == "x"
            assert params["n"] == 1
            assert params["size"] == "1024x1024"


class TestGenerateImageSendsTheRightParams:
    """The same split, exercised through `generate_image` against a fake client."""

    def test_gpt_image_1_call_omits_response_format_and_style(self, generator_and_images):
        generator, images = generator_and_images
        generator.model = "gpt-image-1"

        image = generator.generate_image("draw a runner")

        assert isinstance(image, Image.Image)
        assert len(images.calls) == 1
        call = images.calls[0]
        assert call["model"] == "gpt-image-1"
        assert "response_format" not in call
        assert "style" not in call
        assert call["quality"] == "high"

    def test_dall_e_3_call_includes_response_format_and_style(self, generator_and_images):
        generator, images = generator_and_images
        generator.model = "dall-e-3"

        image = generator.generate_image("draw a runner")

        assert isinstance(image, Image.Image)
        assert len(images.calls) == 1
        call = images.calls[0]
        assert call["model"] == "dall-e-3"
        assert call["response_format"] == "b64_json"
        assert call["style"] == "natural"
        assert call["quality"] == "standard"
