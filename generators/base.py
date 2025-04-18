from abc import ABC, abstractmethod
from PIL import Image

class BaseImageGenerator(ABC):
    """Abstract base class for image generators."""

    @abstractmethod
    def generate_image(self, prompt: str) -> Image.Image:
        """Generates an image based on the provided prompt.

        Args:
            prompt: The text prompt to guide image generation.

        Returns:
            A PIL Image object.
        
        Raises:
            NotImplementedError: If the method is not implemented by the subclass.
            Exception: For any errors during the image generation process.
        """
        pass
