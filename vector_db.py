import os
import logging
from dotenv import load_dotenv
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from qdrant_client.http.exceptions import UnexpectedResponse

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION_PREFIX = os.getenv("QDRANT_COLLECTION_PREFIX", "llmz80_")
OPENAI_EMBEDDING_DIM = 1536 # Dimension for text-embedding-ada-002

def get_qdrant_client():
    """Initializes and returns a Qdrant client based on .env configuration."""
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
                client.recreate_collection(
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
    collection_name = get_collection_name(platform)
    logger.debug(f"Searching for {limit} similar vectors in '{collection_name}'...")
    try:
        search_result = client.search(
            collection_name=collection_name,
            query_vector=vector,
            limit=limit
        )
        logger.info(f"✅ Found {len(search_result)} similar results.")
        # Return only the payload and score for simplicity
        return [(hit.payload, hit.score) for hit in search_result]
    except Exception as e:
        logger.error(f"❌ Failed to search in collection '{collection_name}': {e}")
        return []

# Example Usage (for testing purposes)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger.info("Testing vector_db module...")
    
    qdrant = get_qdrant_client()
    
    if qdrant:
        test_platform = "test_platform"
        logger.info(f"Ensuring collection for '{test_platform}' exists...")
        if ensure_collection_exists(qdrant, test_platform):
            
            # Test upsert
            logger.info("Testing upsert...")
            points_to_upsert = [
                PointStruct(id=1, vector=[0.1] * OPENAI_EMBEDDING_DIM, payload={"file": "example1.asm", "chunk": 0}),
                PointStruct(id=2, vector=[0.9] * OPENAI_EMBEDDING_DIM, payload={"file": "example2.c", "chunk": 0}),
            ]
            upsert_embeddings(qdrant, test_platform, points_to_upsert)
            
            # Test search
            logger.info("Testing search...")
            results = search_similar(qdrant, test_platform, vector=[0.15] * OPENAI_EMBEDDING_DIM, limit=1)
            logger.info(f"Search results: {results}")

            # Clean up (optional)
            # try:
            #    logger.warning(f"Deleting test collection '{get_collection_name(test_platform)}'...")
            #    qdrant.delete_collection(collection_name=get_collection_name(test_platform))
            # except Exception as del_exc:
            #    logger.error(f"Failed to delete test collection: {del_exc}")
        else:
            logger.error("Could not ensure test collection exists. Aborting tests.")
    else:
        logger.error("Could not connect to Qdrant. Aborting tests.")

    logger.info("Finished testing vector_db module.") 