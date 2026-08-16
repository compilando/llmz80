import os
import logging
from dataclasses import dataclass
from typing import Any
from dotenv import load_dotenv

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http.models import Distance, VectorParams, PointStruct
    from qdrant_client.http.exceptions import UnexpectedResponse
    QDRANT_AVAILABLE = True
except ImportError:  # Qdrant is optional for generation and compilation.
    QdrantClient = Any
    Distance = VectorParams = None
    QDRANT_AVAILABLE = False

    class UnexpectedResponse(Exception):
        """Compatibility placeholder used only while Qdrant is unavailable."""

        status_code = None

    @dataclass
    class PointStruct:
        """Payload-compatible placeholder; never sent without qdrant-client."""

        id: str
        vector: list[float]
        payload: dict[str, Any]

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL", "http://127.0.0.1:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION_PREFIX = os.getenv("QDRANT_COLLECTION_PREFIX", "llmz80_")
#: How wide a stored vector is. Read from the backend that produces them
#: rather than written out here, because the two disagreeing is silent: a
#: collection created at the wrong width accepts nothing and reports only
#: that the vector had the wrong size.
#:
#: The name is kept for the callers that import it (`scripts/init_qdrant.py`),
#: but it is no longer OpenAI's: embeddings are computed locally now, at 384
#: dimensions rather than 1536, so **any collection built before that change
#: has to be recreated rather than reused**.
from llmz80.core.embedding_backend import EMBEDDING_DIM as OPENAI_EMBEDDING_DIM  # noqa: E402

def get_qdrant_client():
    """Initializes and returns a Qdrant client based on .env configuration."""
    if not QDRANT_AVAILABLE:
        logger.info("qdrant-client no instalado; RAG vectorial desactivado")
        return None
    logger.debug(f"Connecting to Qdrant at {QDRANT_URL}")
    try:
        if QDRANT_API_KEY:
            client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
            logger.debug("Qdrant client initialized with API Key.")
        else:
            client = QdrantClient(url=QDRANT_URL)
            logger.debug("Qdrant client initialized without API Key.")
        
        # Test connection (optional, but good practice)
        client.get_collections() 
        logger.info("✅ Successfully connected to Qdrant.")
        return client
    except Exception as e:
        logger.error(f"❌ Failed to connect to Qdrant at {QDRANT_URL}: {e}")
        logger.error("💡 Please ensure Qdrant is running and the URL/API Key in .env are correct.")
        return None

def get_collection_name(platform):
    """Generates the collection name based on the platform."""
    return f"{QDRANT_COLLECTION_PREFIX}{platform}"

def ensure_collection_exists(client: QdrantClient, platform: str):
    """Checks if a collection exists for the platform, creates it if not."""
    if not QDRANT_AVAILABLE or client is None:
        return False
    collection_name = get_collection_name(platform)
    logger.debug(f"Ensuring collection '{collection_name}' exists...")
    try:
        client.get_collection(collection_name=collection_name)
        logger.debug(f"Collection '{collection_name}' already exists.")
        return True
    except (UnexpectedResponse, ValueError) as e:
         # Handle potential ValueError if collection doesn't exist (older client versions)
         # or UnexpectedResponse (newer versions) status_code 404
        is_not_found_error = False
        if isinstance(e, UnexpectedResponse) and e.status_code == 404:
            is_not_found_error = True
        elif isinstance(e, ValueError) and "not found" in str(e).lower():
             is_not_found_error = True
             
        if is_not_found_error:
            logger.info(f"Collection '{collection_name}' not found. Creating...")
            try:
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=OPENAI_EMBEDDING_DIM, distance=Distance.COSINE)
                )
                logger.info(f"✅ Collection '{collection_name}' created successfully.")
                return True
            except Exception as create_exc:
                logger.error(f"❌ Failed to create collection '{collection_name}': {create_exc}")
                return False
        else:
             # Different error
             logger.error(f"❌ Error checking/creating collection '{collection_name}': {e}")
             return False
    except Exception as e:
        logger.error(f"❌ Unexpected error checking/creating collection '{collection_name}': {e}")
        return False


def upsert_embeddings(client: QdrantClient, platform: str, points: list[PointStruct]):
    """Upserts (inserts or updates) embedding points into the specified collection."""
    if not QDRANT_AVAILABLE or client is None:
        return False
    collection_name = get_collection_name(platform)
    if not points:
        logger.warning("No points provided for upsert.")
        return False
    logger.debug(f"Upserting {len(points)} points into collection '{collection_name}'...")
    try:
        operation_info = client.upsert(
            collection_name=collection_name,
            points=points,
            wait=True # Wait for operation to complete
        )
        logger.info(f"✅ Upsert completed: {operation_info.status}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to upsert points into '{collection_name}': {e}")
        return False

def search_similar(client: QdrantClient, platform: str, vector: list[float], limit: int = 10):
    """Searches for vectors similar to the given vector in the specified collection."""
    if not QDRANT_AVAILABLE or client is None:
        return []
    collection_name = get_collection_name(platform)
    logger.debug(f"Searching for {limit} similar vectors in '{collection_name}'...")
    if not ensure_collection_exists(client, platform):
        logger.warning(f"Collection '{collection_name}' no disponible para búsqueda.")
        return []
    try:
        if hasattr(client, "search"):
            search_result = client.search(
                collection_name=collection_name,
                query_vector=vector,
                limit=limit
            )
        else:
            query_response = client.query_points(
                collection_name=collection_name,
                query=vector,
                limit=limit,
                with_payload=True,
                with_vectors=False,
            )
            search_result = query_response.points
        logger.info(f"✅ Found {len(search_result)} similar results.")
        # Return only the payload and score for simplicity
        return [(hit.payload, hit.score) for hit in search_result]
    except Exception as e:
        logger.error(f"❌ Failed to search in collection '{collection_name}': {e}")
        return []

# Example Usage (for testing purposes)
if __name__ == '__main__':
    # Configurar logging básico para ver la salida de este script
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    TARGET_PLATFORM = "amstrad_cpc" # Cambia a "spectrum" si quieres probar esa
    
    logger.info(f"--- Checking Qdrant Collection: {get_collection_name(TARGET_PLATFORM)} ---")
    
    qdrant = get_qdrant_client()
    
    if qdrant:
        collection_name = get_collection_name(TARGET_PLATFORM)
        try:
            # 1. Obtener información de la colección
            collection_info = qdrant.get_collection(collection_name=collection_name)
            logger.info(f"Collection Info: {collection_info}")
            
            # 2. Contar puntos (si la info no lo incluye directamente)
            # Usar count() que es más directo que scroll
            count_result = qdrant.count(collection_name=collection_name, exact=True)
            logger.info(f"Point Count: {count_result.count}")

            # 3. Recuperar un punto de ejemplo (si hay alguno)
            if count_result.count > 0:
                logger.info("Retrieving one sample point...")
                # Usar scroll con límite 1 para obtener un punto
                sample_points, _ = qdrant.scroll(
                    collection_name=collection_name, 
                    limit=1, 
                    with_payload=True, 
                    with_vectors=False # No necesitamos el vector aquí
                )
                if sample_points:
                    logger.info(f"Sample Point Payload: {sample_points[0].payload}")
                else:
                    logger.warning("Count reported >0 but could not retrieve a sample point.")
            else:
                logger.info("Collection is empty, cannot retrieve sample point.")

        except (UnexpectedResponse, ValueError) as e:
            # Comprobar si es error "Not Found"
            is_not_found_error = False
            if isinstance(e, UnexpectedResponse) and e.status_code == 404:
                is_not_found_error = True
            elif isinstance(e, ValueError) and "not found" in str(e).lower():
                 is_not_found_error = True
                 
            if is_not_found_error:
                logger.error(f"Collection '{collection_name}' does NOT exist.")
            else:
                logger.error(f"Error accessing collection '{collection_name}': {e}")
        except Exception as e:
            logger.error(f"Unexpected error accessing collection '{collection_name}': {e}")
    else:
        logger.error("Could not connect to Qdrant. Cannot check collection.")

    logger.info("--- Check finished ---") 
