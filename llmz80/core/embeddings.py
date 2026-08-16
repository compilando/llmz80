import json
import time
import logging
import numpy as np
from numpy.linalg import norm
from pathlib import Path
from typing import Dict, Tuple, Any, List, Optional
import os
from ..utils.helpers import estimate_tokens
from .embedding_backend import EMBEDDING_DIM, embed, zero_vector

class EmbeddingsManager:
    """Administrador para generar y gestionar embeddings."""
    
    def __init__(self, client, platform: str, global_vars: Dict[str, Any]):
        """Inicializa el administrador de embeddings.

        Args:
            client: ya no se usa. Los embeddings los calcula un modelo local
                (`embedding_backend`), sin llamada de red ni clave de API. El
                parámetro sigue aquí, y sigue guardándose, porque
                `llmz80/api/generator.py` construye este objeto pasándole su
                cliente y quitarlo obligaría a tocar ese camino legacy sin
                ninguna ganancia. `self.embedding_model` corre la misma
                suerte: el modelo real lo decide `embedding_backend`.
            platform: Plataforma seleccionada
            global_vars: Variables globales configuradas
        """
        self.client = client
        self.platform = platform
        self.embeddings_cache_dir = global_vars['embeddings_cache_dir']
        self.max_example_size = global_vars['max_example_size']
        self.max_chunk_size = global_vars['max_chunk_size'] 
        self.token_limit = global_vars['token_limit']
        self.safety_margin = global_vars['safety_margin']
        self.example_dir_template = global_vars['example_dir_template']
        self.embedding_model = global_vars['embedding_model']
        self.embeddings_cache = {}
        self.force_truncate = False
        
    def get_embeddings_for_text(self, text: str) -> List[Tuple[Optional[np.ndarray], int]]:
        """Obtiene los embeddings para un texto, manejando chunks.
        
        Devuelve una lista de tuplas (embedding, chunk_index). 
        Si el texto no se divide, devuelve [(embedding, 0)].
        Si falla un chunk, devuelve (None, chunk_index) para ese chunk.
        """
        results = []
        try:
            if not text.strip():
                logging.warning("Texto vacío para embedding.")
                return [(zero_vector(), 0)] # Devuelve un vector cero con índice 0

            safe_token_limit = int(self.token_limit * self.safety_margin)
            estimated_tokens = estimate_tokens(text)

            # --- Texto corto --- 
            if estimated_tokens <= safe_token_limit:
                logging.debug(f"Texto dentro del límite de tokens (~{estimated_tokens} tokens), procesando directamente.")
                try:
                    embedding = embed([text])[0]
                    if embedding.shape != (EMBEDDING_DIM,):
                        logging.error(
                            f"El modelo devolvió un vector de forma {embedding.shape}, "
                            f"y se esperaba ({EMBEDDING_DIM},)"
                        )
                        results.append((None, 0))
                    else:
                        results.append((embedding, 0)) # Índice 0 para texto no dividido
                except Exception as e:
                    logging.error(f"Error al obtener embedding directo: {e}")
                    results.append((None, 0))
                return results # Devuelve la lista con un solo resultado (o None)

            # --- Texto largo (Chunking) --- 
            logging.info(f"Texto demasiado largo (~{estimated_tokens} tokens). Dividiendo...")
            
            # Ajustar tamaño de chunk
            chars_per_token_estimation = 4.0 # Más conservador que 3.5
            if estimated_tokens > safe_token_limit * 1.5:
                reduction_factor = min(4, max(2, estimated_tokens / safe_token_limit))
                # Usar la nueva estimación aquí
                actual_chunk_size = int((safe_token_limit * chars_per_token_estimation) / reduction_factor)
                logging.info(f"Reduciendo tamaño de chunk por factor {reduction_factor:.1f}")
            else:
                 # Usar la nueva estimación aquí
                actual_chunk_size = min(self.max_chunk_size, int(safe_token_limit * chars_per_token_estimation))
            # Actualizar el log con la nueva estimación
            logging.info(f"Usando tamaño de chunk de {actual_chunk_size} caracteres (~{int(actual_chunk_size/chars_per_token_estimation)} tokens est.)")

            # Dividir en chunks
            chunks = [text[i:i + actual_chunk_size] for i in range(0, len(text), actual_chunk_size) if text[i:i + actual_chunk_size].strip()]

            # Manejar caso donde un solo chunk sigue siendo demasiado grande
            if len(chunks) == 1 and estimate_tokens(chunks[0]) > safe_token_limit:
                logging.warning(f"El único chunk sigue siendo demasiado grande ({estimate_tokens(chunks[0])} tokens). Dividiendo más...")
                chunk = chunks[0]
                # Usar la nueva estimación aquí también para la subdivisión
                smaller_chunk_size = int(actual_chunk_size / 2)
                chunks = [chunk[i:i + smaller_chunk_size] for i in range(0, len(chunk), smaller_chunk_size) if chunk[i:i + smaller_chunk_size].strip()]
                logging.info(f"Re-dividido en {len(chunks)} chunks más pequeños.")

            # Limitar número de chunks (muestreo)
            max_chunks_to_process = 10
            if len(chunks) > max_chunks_to_process:
                logging.warning(f"Demasiados chunks ({len(chunks)}). Tomando muestra de {max_chunks_to_process}...")
                indices_to_keep = np.linspace(0, len(chunks) - 1, max_chunks_to_process, dtype=int)
                sampled_chunks = [(chunks[i], i) for i in indices_to_keep] # Guardar índice original
            else:
                sampled_chunks = [(chunk, i) for i, chunk in enumerate(chunks)] # Usar todos los chunks con índice original

            # Procesar cada chunk (o muestra)
            for chunk_content, original_index in sampled_chunks:
                chunk_tokens = estimate_tokens(chunk_content)
                logging.info(f"Procesando chunk {original_index + 1} (de {len(chunks)} totales) - ~{chunk_tokens} tokens...")
                try:
                    chunk_embedding = embed([chunk_content])[0]
                    if chunk_embedding.shape != (EMBEDDING_DIM,):
                        logging.warning(
                            f"Chunk {original_index + 1}: el modelo devolvió un vector de "
                            f"forma {chunk_embedding.shape}."
                        )
                        results.append((None, original_index))
                    else:
                        results.append((chunk_embedding, original_index))
                except Exception as e:
                    logging.error(f"Error procesando chunk {original_index + 1}: {e}")
                    results.append((None, original_index)) # Añadir None si el chunk falla
            
            return results
            
        except Exception as e:
            logging.exception(f"Error inesperado en get_embeddings_for_text: {e}")
            return [(None, 0)] # Devuelve None con índice 0 en caso de error general

    def get_embedding(self, text: str) -> np.ndarray:
        """Obtiene UN embedding para un texto, promediando si se divide en chunks.
           Mantiene la interfaz original pero usa la nueva lógica.
        """
        embeddings_data = self.get_embeddings_for_text(text)
        
        valid_embeddings = [emb for emb, idx in embeddings_data if emb is not None and isinstance(emb, np.ndarray) and emb.size > 0]
        
        if not valid_embeddings:
            logging.error("No se pudieron generar embeddings válidos para el texto.")
            return zero_vector() # Dimensión por defecto
            
        if len(valid_embeddings) == 1:
            # Si solo hay uno (texto corto o solo un chunk válido), devolver ese
            logging.debug("Devolviendo embedding único.")
            return valid_embeddings[0]
        else:
            # Si hay múltiples (texto chunked), promediar y normalizar
            logging.info(f"Combinando {len(valid_embeddings)} embeddings de chunks...")
            try:
                combined_embedding = np.mean(valid_embeddings, axis=0)
                # Normalizar
                norm_val = norm(combined_embedding)
                if norm_val > 0:
                    combined_embedding = combined_embedding / norm_val
                else: # Caso raro: promedio es vector cero
                     logging.warning("Promedio de embeddings resultó en vector cero.")
                     return zero_vector()
                 
                if not isinstance(combined_embedding, np.ndarray):
                     logging.error(f"Resultado combinado no es numpy array: {type(combined_embedding)}")
                     return zero_vector()
                
                logging.info(f"Embedding combinado generado con éxito.")
                return combined_embedding
            except Exception as e:
                logging.error(f"Error al combinar embeddings: {e}")
                return zero_vector()

    def get_embedding_for_large_file(self, text: str) -> np.ndarray:
        """Compatibility wrapper for callers that explicitly flag large files."""
        return self.get_embedding(text)

    def cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calcula la similitud coseno entre dos vectores.
        
        Args:
            a: Primer vector
            b: Segundo vector
            
        Returns:
            Similitud coseno entre los vectores
        """
        try:
            # Verificar que ambos vectores son arrays numpy y no están vacíos
            if not isinstance(a, np.ndarray) or not isinstance(b, np.ndarray):
                logging.warning(f"⚠️ Tipos no válidos para similitud coseno: {type(a)}, {type(b)}")
                # Si alguno es un escalar, convertirlo a array vacío
                if isinstance(a, (int, float)):
                    logging.error(f"⚠️ Primer vector para similitud coseno es un escalar: {a}")
                    a = zero_vector()
                if isinstance(b, (int, float)):
                    logging.error(f"⚠️ Segundo vector para similitud coseno es un escalar: {b}")
                    b = zero_vector()
                
                # Si después de convertir todavía no son arrays, retornar 0
                if not isinstance(a, np.ndarray) or not isinstance(b, np.ndarray):
                    return 0.0
            
            if a.size == 0 or b.size == 0:
                logging.warning("⚠️ Uno de los vectores para similitud coseno está vacío")
                return 0.0
                
            # Verificar que los vectores tienen la misma longitud
            if a.shape != b.shape:
                logging.warning(f"⚠️ Los vectores tienen formas diferentes: {a.shape} vs {b.shape}")
                return 0.0
                
            a_norm = norm(a)
            b_norm = norm(b)
            
            if a_norm == 0 or b_norm == 0:
                logging.warning("⚠️ Uno de los vectores tiene norma cero, no se puede calcular similitud coseno")
                return 0.0
                
            similarity = np.dot(a, b) / (a_norm * b_norm)
            
            # Verificar que el resultado es un float válido
            if not isinstance(similarity, (int, float)) or np.isnan(similarity) or np.isinf(similarity):
                logging.warning(f"⚠️ Resultado de similitud no válido: {similarity}")
                return 0.0
            
            return float(similarity)  # Asegurar que devolvemos un float estándar
        except Exception as e:
            logging.error(f"❌ Error en cálculo de similitud coseno: {e}")
            return 0.0 
