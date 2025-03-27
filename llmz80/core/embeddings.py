import json
import time
import logging
import numpy as np
from numpy.linalg import norm
from pathlib import Path
from typing import Dict, Tuple, Any, List, Optional
import os
from ..utils.helpers import estimate_tokens

class EmbeddingsManager:
    """Administrador para generar y gestionar embeddings."""
    
    def __init__(self, client, platform: str, global_vars: Dict[str, Any]):
        """Inicializa el administrador de embeddings.
        
        Args:
            client: Cliente de OpenAI
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
        
    def get_embedding(self, text: str) -> np.ndarray:
        """Obtiene el embedding para un texto dado usando la API de OpenAI.
        
        Args:
            text: Texto para el cual generar el embedding
            
        Returns:
            Array de numpy con el embedding
        """
        try:
            # Si el texto está vacío, devolver un array vacío
            if not text.strip():
                logging.warning("Texto vacío para embedding. Devolviendo array vacío.")
                return np.zeros((1536,), dtype=float)  # Dimensión por defecto para embeddings
            
            # Calcular el máximo tamaño seguro para un chunk
            safe_token_limit = int(self.token_limit * self.safety_margin)  # Usar margen de seguridad
            estimated_tokens = estimate_tokens(text)
            
            # Si el texto es corto (está dentro del límite seguro), procesarlo directamente
            if estimated_tokens <= safe_token_limit:
                logging.debug(f"Texto dentro del límite de tokens: ~{estimated_tokens} tokens estimados")
                try:
                    response = self.client.embeddings.create(
                        model=self.embedding_model,
                        input=text
                    )
                    embedding_data = response.data[0].embedding
                    
                    # Verificar que embedding_data sea una lista antes de convertirlo
                    if not isinstance(embedding_data, list):
                        logging.error(f"API devolvió un embedding inválido, tipo: {type(embedding_data)}")
                        return np.zeros((1536,), dtype=float)  # Devolver array por defecto
                        
                    # Verificar que todos los elementos sean números
                    if not all(isinstance(x, (int, float)) for x in embedding_data):
                        logging.error("API devolvió elementos no numéricos en el embedding")
                        return np.zeros((1536,), dtype=float)
                        
                    return np.array(embedding_data, dtype=float)
                except Exception as e:
                    if "maximum context length" in str(e):
                        logging.warning(f"La estimación de tokens falló, el texto es demasiado largo. Dividiendo...")
                        # Si falla, caemos en la división en chunks más pequeños
                    else:
                        logging.error(f"Error al obtener embedding: {e}")
                        return np.zeros((1536,), dtype=float)  # Devolver array por defecto
            
            # Para textos largos, dividir en chunks más pequeños
            logging.info(f"Texto demasiado largo para embedding (~{estimated_tokens} tokens estimados). Dividiendo en chunks...")
            
            # Usar un tamaño de chunk más agresivo si es extremadamente grande
            if estimated_tokens > safe_token_limit * 1.5:
                # Si es extremadamente grande, reducir aún más el tamaño del chunk
                reduction_factor = min(4, max(2, estimated_tokens / safe_token_limit))
                actual_chunk_size = int((safe_token_limit * 3.5) / reduction_factor)
                logging.info(f"Texto extremadamente grande, reduciendo tamaño de chunk por factor {reduction_factor:.1f}")
            else:
                # Tamaño normal para textos largos pero no extremos
                actual_chunk_size = min(self.max_chunk_size, int((safe_token_limit * 3.5)))
                
            logging.info(f"Usando tamaño de chunk de {actual_chunk_size} caracteres (~{int(actual_chunk_size/3.5)} tokens est.)")
            
            chunks = []
            # Asegurarnos de que los chunks sean lo suficientemente pequeños
            for i in range(0, len(text), actual_chunk_size):
                chunk = text[i:i + actual_chunk_size]
                if chunk:  # Asegurarse de que el chunk no esté vacío
                    chunks.append(chunk)
                    
            # Si aún así los chunks son demasiado grandes, intentar una segunda división
            if len(chunks) == 1 and estimate_tokens(chunks[0]) > safe_token_limit:
                logging.warning(f"El único chunk sigue siendo demasiado grande ({estimate_tokens(chunks[0])} tokens). Dividiendo más agresivamente...")
                chunk = chunks[0]
                chunks = []
                smaller_chunk_size = int(actual_chunk_size / 2)
                for i in range(0, len(chunk), smaller_chunk_size):
                    subchunk = chunk[i:i + smaller_chunk_size]
                    if subchunk:
                        chunks.append(subchunk)
                logging.info(f"Re-dividido en {len(chunks)} chunks más pequeños de ~{smaller_chunk_size} caracteres")
            
            # Si hay demasiados chunks, tomar solo una muestra representativa
            max_chunks_to_process = 10  # Limitar el número de chunks a procesar
            if len(chunks) > max_chunks_to_process:
                logging.warning(f"Demasiados chunks ({len(chunks)}). Tomando una muestra representativa...")
                # Tomar el primer chunk, algunos del medio y el último
                sampled_chunks = [chunks[0]]  # Primer chunk
                
                # Chunks del medio con espaciado uniforme
                middle_indices = np.linspace(1, len(chunks)-2, max_chunks_to_process-2, dtype=int)
                for idx in middle_indices:
                    sampled_chunks.append(chunks[idx])
                
                sampled_chunks.append(chunks[-1])  # Último chunk
                chunks = sampled_chunks
                logging.info(f"Muestra reducida a {len(chunks)} chunks representativos")
            
            # Procesar cada chunk por separado
            embeddings = []
            for i, chunk in enumerate(chunks):
                chunk_tokens = estimate_tokens(chunk)
                logging.info(f"Procesando chunk {i+1} de {len(chunks)} (~{chunk_tokens} tokens est.)...")
                
                try:
                    response = self.client.embeddings.create(
                        model=self.embedding_model,
                        input=chunk
                    )
                    chunk_embedding_data = response.data[0].embedding
                    
                    # Verificar que sea una lista y contenga solo números
                    if not isinstance(chunk_embedding_data, list):
                        logging.warning(f"Chunk {i+1}: API devolvió un embedding inválido, tipo: {type(chunk_embedding_data)}")
                        continue
                        
                    if not all(isinstance(x, (int, float)) for x in chunk_embedding_data):
                        logging.warning(f"Chunk {i+1}: API devolvió elementos no numéricos en el embedding")
                        continue
                    
                    chunk_embedding = np.array(chunk_embedding_data, dtype=float)
                    embeddings.append(chunk_embedding)
                except Exception as e:
                    if "maximum context length" in str(e):
                        logging.error(f"Chunk {i+1} sigue siendo demasiado grande: {str(e)}")
                        # Si un chunk sigue siendo demasiado grande, podríamos dividirlo más
                        # Por ahora, lo omitimos para evitar recursión
                        logging.warning(f"Omitiendo chunk {i+1} por ser demasiado grande")
                        continue
                    else:
                        logging.error(f"Error al procesar chunk {i+1}: {e}")
                        continue  # Continuar con el siguiente chunk en caso de error
            
            # Combinar los embeddings (promedio simple)
            if embeddings:
                try:
                    combined_embedding = np.mean(embeddings, axis=0)
                    # Normalizar para mantener las propiedades del espacio de embeddings
                    if norm(combined_embedding) > 0:
                        combined_embedding = combined_embedding / norm(combined_embedding)
                    logging.info(f"Embedding combinado generado con éxito a partir de {len(embeddings)} chunks (de {len(chunks)} intentados).")
                    return combined_embedding
                except Exception as e:
                    logging.error(f"Error al combinar embeddings: {e}")
                    return np.zeros((1536,), dtype=float)  # Devolver array por defecto
            else:
                logging.error("No se pudo generar ningún embedding válido de los chunks")
                return np.zeros((1536,), dtype=float)  # Devolver array por defecto
            
        except Exception as e:
            logging.error(f"Error al obtener embedding: {e}")
            # Retornar un embedding vacío en caso de error
            return np.zeros((1536,), dtype=float)  # Dimensión por defecto

    def get_embedding_for_large_file(self, content: str) -> np.ndarray:
        """Obtiene el embedding para un archivo muy grande usando una estrategia de muestreo.
        
        Args:
            content: El contenido del archivo grande
            
        Returns:
            Un array numpy con el embedding combinado de las muestras del archivo
        """
        logging.info(f"Procesando archivo grande ({len(content)} caracteres) con estrategia de muestreo...")
        
        # 1. Dividir el archivo en secciones significativas (inicio, fragmentos intermedios, final)
        sample_size = min(15000, int(self.max_example_size / 4))
        
        # Tomar inicio
        start_content = content[:sample_size]
        
        # Tomar final
        end_content = content[-sample_size:] if len(content) > sample_size else ""
        
        # Tomar algunos fragmentos intermedios si el archivo es muy grande
        middle_samples = []
        if len(content) > sample_size * 3:
            # Tomar hasta 4 muestras intermedias equidistantes
            sections = min(4, max(2, int(len(content) / self.max_example_size)))
            mid_points = np.linspace(sample_size, len(content) - sample_size - 1, sections, dtype=int)
            for point in mid_points:
                if point > sample_size and point < len(content) - sample_size:
                    middle_samples.append(content[point:point + sample_size])
        
        # 2. Generar embeddings para cada sección y combinarlos
        embeddings_to_combine = []
        samples_attempted = 0
        samples_successful = 0
        
        # Procesar inicio
        samples_attempted += 1
        try:
            start_embedding = self.get_embedding(start_content)
            if isinstance(start_embedding, np.ndarray) and start_embedding.size > 0 and not np.all(start_embedding == 0):
                embeddings_to_combine.append(start_embedding)
                samples_successful += 1
                logging.debug(f"✅ Muestra de inicio procesada correctamente")
            else:
                logging.warning(f"⚠️ La muestra de inicio no generó un embedding válido")
        except Exception as e:
            logging.error(f"Error al procesar muestra de inicio: {e}")
        
        # Procesar muestras intermedias
        for i, mid_sample in enumerate(middle_samples):
            samples_attempted += 1
            try:
                mid_embedding = self.get_embedding(mid_sample)
                if isinstance(mid_embedding, np.ndarray) and mid_embedding.size > 0 and not np.all(mid_embedding == 0):
                    embeddings_to_combine.append(mid_embedding)
                    samples_successful += 1
                    logging.debug(f"✅ Muestra intermedia {i+1} procesada correctamente")
                else:
                    logging.warning(f"⚠️ La muestra intermedia {i+1} no generó un embedding válido")
            except Exception as e:
                logging.error(f"Error al procesar muestra intermedia {i+1}: {e}")
        
        # Procesar final
        if end_content:
            samples_attempted += 1
            try:
                end_embedding = self.get_embedding(end_content)
                if isinstance(end_embedding, np.ndarray) and end_embedding.size > 0 and not np.all(end_embedding == 0):
                    embeddings_to_combine.append(end_embedding)
                    samples_successful += 1
                    logging.debug(f"✅ Muestra de final procesada correctamente")
                else:
                    logging.warning(f"⚠️ La muestra de final no generó un embedding válido")
            except Exception as e:
                logging.error(f"Error al procesar muestra de final: {e}")
        
        # 3. Combinar los embeddings si hay al menos uno válido
        if embeddings_to_combine:
            try:
                combined_embedding = np.mean(embeddings_to_combine, axis=0)
                # Normalizar para mantener las propiedades del espacio de embeddings
                if norm(combined_embedding) > 0:
                    combined_embedding = combined_embedding / norm(combined_embedding)
                logging.info(f"✅ Embedding combinado generado de {samples_successful}/{samples_attempted} muestras exitosas")
                return combined_embedding
            except Exception as e:
                logging.error(f"Error al combinar embeddings de muestras: {e}")
                return np.zeros((1536,), dtype=float)
        else:
            logging.warning(f"⚠️ No se pudo generar ningún embedding válido de las muestras del archivo")
            return np.zeros((1536,), dtype=float)

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
                logging.warning(f"Tipos no válidos para similitud coseno: {type(a)}, {type(b)}")
                return 0.0
            
            if a.size == 0 or b.size == 0:
                logging.warning("Uno de los vectores para similitud coseno está vacío")
                return 0.0
                
            # Verificar que los vectores tienen la misma longitud
            if a.shape != b.shape:
                logging.warning(f"Los vectores tienen formas diferentes: {a.shape} vs {b.shape}")
                return 0.0
                
            a_norm = norm(a)
            b_norm = norm(b)
            
            if a_norm == 0 or b_norm == 0:
                logging.warning("Uno de los vectores tiene norma cero, no se puede calcular similitud coseno")
                return 0.0
                
            return np.dot(a, b) / (a_norm * b_norm)
        except Exception as e:
            logging.error(f"Error en cálculo de similitud coseno: {e}")
            return 0.0 