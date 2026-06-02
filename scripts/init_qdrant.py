#!/usr/bin/env python3
"""
Script para inicializar las colecciones de Qdrant necesarias para LLMZ80.
Crea las colecciones con la configuración correcta si no existen.
"""

import sys
import logging
from pathlib import Path

# Añadir el directorio raíz al path para importar módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

from vector_db import (
    OPENAI_EMBEDDING_DIM,
    get_collection_name,
    get_qdrant_client,
)
from qdrant_client.models import Distance, VectorParams

# Configurar logging básico
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)

logger = logging.getLogger(__name__)

# Configuración de las colecciones
COLLECTIONS_CONFIG = {
    get_collection_name('spectrum'): {
        'vector_size': OPENAI_EMBEDDING_DIM,
        'distance': Distance.COSINE,
        'description': 'Embeddings de ejemplos de ZX Spectrum'
    },
    get_collection_name('amstrad_cpc'): {
        'vector_size': OPENAI_EMBEDDING_DIM,
        'distance': Distance.COSINE,
        'description': 'Embeddings de ejemplos de Amstrad CPC'
    }
}


def init_collections():
    """Inicializa todas las colecciones necesarias en Qdrant."""
    logger.info("🚀 Inicializando colecciones de Qdrant...")
    
    try:
        # Obtener cliente de Qdrant
        client = get_qdrant_client()
        if not client:
            logger.error("❌ No se pudo conectar a Qdrant")
            logger.error("   Verifica que Qdrant esté ejecutándose y que QDRANT_URL y QDRANT_API_KEY estén configurados")
            return False
        
        logger.info("✅ Conectado a Qdrant exitosamente")
        
        # Obtener colecciones existentes
        try:
            collections_response = client.get_collections()
            existing_collections = {col.name for col in collections_response.collections}
            logger.info(f"📊 Colecciones existentes: {existing_collections if existing_collections else 'ninguna'}")
        except Exception as e:
            logger.warning(f"⚠️  No se pudo obtener lista de colecciones: {e}")
            existing_collections = set()
        
        # Crear cada colección si no existe
        created = 0
        skipped = 0
        
        for collection_name, config in COLLECTIONS_CONFIG.items():
            if collection_name in existing_collections:
                logger.info(f"⏭️  Colección '{collection_name}' ya existe, omitiendo...")
                skipped += 1
                continue
            
            try:
                logger.info(f"📝 Creando colección '{collection_name}'...")
                logger.info(f"   - Vector size: {config['vector_size']}")
                logger.info(f"   - Distance: {config['distance']}")
                
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=config['vector_size'],
                        distance=config['distance']
                    )
                )
                
                logger.info(f"✅ Colección '{collection_name}' creada exitosamente")
                created += 1
                
            except Exception as e:
                logger.error(f"❌ Error creando colección '{collection_name}': {e}")
                return False
        
        # Resumen
        logger.info("")
        logger.info("=" * 60)
        logger.info("RESUMEN DE INICIALIZACIÓN")
        logger.info("=" * 60)
        logger.info(f"✅ Colecciones creadas: {created}")
        logger.info(f"⏭️  Colecciones ya existentes: {skipped}")
        logger.info(f"📊 Total de colecciones: {len(COLLECTIONS_CONFIG)}")
        logger.info("=" * 60)
        logger.info("")
        
        if created > 0:
            logger.info("🎉 Qdrant inicializado correctamente")
            logger.info("")
            logger.info("📝 Próximo paso: Poblar las colecciones con ejemplos")
            logger.info("   make populate-all")
        else:
            logger.info("✅ Todas las colecciones ya estaban inicializadas")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error durante la inicialización: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return False


def main():
    """Función principal."""
    print("🔧 LLMZ80 - Inicializador de Qdrant")
    print("=" * 60)
    print("")
    
    success = init_collections()
    
    if success:
        print("")
        print("✅ Inicialización completada exitosamente")
        sys.exit(0)
    else:
        print("")
        print("❌ Inicialización falló")
        print("   Revisa los mensajes de error arriba")
        sys.exit(1)


if __name__ == "__main__":
    main()
