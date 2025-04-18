import os
import base64
import io
import logging
from PIL import Image
from dotenv import load_dotenv
import google.cloud.aiplatform as aiplatform
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value

from .base import BaseImageGenerator

logger = logging.getLogger(__name__)

# Modelo de Imagen en Vertex AI (ajustar si es necesario)
# Cambiado a 005 por posible indisponibilidad de 006 en la región
VERTEX_IMAGE_MODEL_NAME = "imagen-3.0-generate-002"

class VertexAIImageGenerator(BaseImageGenerator):
    """Image generator using Google Cloud Vertex AI's Imagen models."""

    def __init__(self, project_id: str, location: str, api_endpoint: str = None):
        """Initializes the Vertex AI client.

        Args:
            project_id: Your Google Cloud project ID.
            location: The GCP region for Vertex AI (e.g., 'us-central1').
            api_endpoint: Optional custom API endpoint.
        """
        if not project_id:
            raise ValueError("Vertex AI project ID is required.")
        if not location:
            raise ValueError("Vertex AI location is required.")
            
        self.project_id = project_id
        self.location = location
        self.api_endpoint = api_endpoint or f"{location}-aiplatform.googleapis.com"
        
        try:
            # Initialize Vertex AI client
            aiplatform.init(project=self.project_id, location=self.location)
            # The client doesn't need to be stored if using aiplatform.gapic
            logger.info(f"Vertex AI client initialized")
            
            # Prepare the model reference (optional, can be done in generate_image)
            # self.model = aiplatform.gapic.ModelServiceClient(client_options={"api_endpoint": self.api_endpoint})
            # logger.info(f"Vertex AI Image Generator configured to use model endpoint: {self.api_endpoint}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI client: {e}")
            logger.error("Ensure GOOGLE_APPLICATION_CREDENTIALS is set correctly and the Vertex AI API is enabled.")
            raise ValueError(f"Failed to initialize Vertex AI client: {e}") from e

    def generate_image(self, prompt: str, number_of_images: int = 1) -> Image.Image:
        """Generates an image using the Vertex AI Imagen API."""
        logger.info(f"🤖 Generating image with Vertex AI Imagen ({VERTEX_IMAGE_MODEL_NAME})...")
        logger.debug(f"Prompt: {prompt[:100]}...")

        client_options = {"api_endpoint": self.api_endpoint}
        client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)
        
        endpoint = f"projects/{self.project_id}/locations/{self.location}/publishers/google/models/{VERTEX_IMAGE_MODEL_NAME}"

        # Prepare instance parameters
        instance_dict = {
            "prompt": prompt,
            "negativePrompt": "text, labels, words, letters, watermark, signature, border, frame", # Basic negative prompt
            "sampleCount": number_of_images,
            "aspectRatio": "1:1", # Generate square images
            "outputFormat": "png", # Request PNG format
            # "seed": 12345 # Optional seed for reproducibility
        }
        instance = json_format.ParseDict(instance_dict, Value())
        instances = [instance]

        # Set parameters (can include things like quality, guidance scale etc. if supported)
        parameters_dict = {}
        parameters = json_format.ParseDict(parameters_dict, Value())

        try:
            response = client.predict(
                endpoint=endpoint,
                instances=instances,
                parameters=parameters,
            )
            
            logger.debug("Respuesta recibida de Vertex AI")
            # Parse the response
            if not response.predictions:
                raise Exception("Respuesta inválida de Vertex AI: No se encontraron predicciones.")

            # Assuming the response format includes base64 encoded images
            # Adjust parsing based on the actual response structure of the model version
            image_b64_string = None
            for prediction in response.predictions:
                 # Treat prediction as a dictionary-like object directly for newer models
                 try:
                     # Check if prediction behaves like a dict and has the key
                     if isinstance(prediction, dict) or hasattr(prediction, 'get'): 
                          image_b64_string = prediction.get("bytesBase64Encoded")
                     else:
                          # Fallback: Attempt MessageToDict for older model compatibility?
                          # Or log a warning/error about unexpected type
                          logger.warning(f"Prediction object type is unexpected: {type(prediction)}. Attempting direct access.")
                          # You might need more specific handling based on the actual object type if not dict-like
                          if hasattr(prediction, "bytesBase64Encoded"): # Direct attribute access if possible
                               image_b64_string = prediction.bytesBase64Encoded
                 except AttributeError:
                     logger.warning(f"Could not access 'bytesBase64Encoded' in prediction object: {prediction}")
                     image_b64_string = None # Ensure it's None if access failed
                 
                 if image_b64_string:
                     break # Take the first image found
            
            if not image_b64_string:
                 # Log the actual predictions if debugging is needed
                 logger.debug(f"Raw predictions received: {response.predictions}")
                 raise Exception("Respuesta inválida de Vertex AI: No se encontró 'bytesBase64Encoded' en las predicciones.")

            # Decode base64 image
            logger.debug("Decodificando imagen base64 de Vertex AI")
            image_data = base64.b64decode(image_b64_string)
            image = Image.open(io.BytesIO(image_data))
            logger.info(f"✅ Image generated successfully by Vertex AI ({image.size})")
            return image

        except Exception as e:
            logger.error(f"❌ Error inesperado durante la generación con Vertex AI: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            logger.error("Asegúrate de que el endpoint, proyecto, ubicación y modelo son correctos y que la API Vertex AI está habilitada.")
            raise Exception(f"Error generando imagen con Vertex AI: {str(e)}") from e 