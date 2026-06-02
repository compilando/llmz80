import logging
import random
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import numpy as np

from ..utils.helpers import estimate_tokens
from .code_context import build_embedding_text, build_example_context, discover_support_files

class ExamplesLoader:
    """Cargador de ejemplos de código para diferentes plataformas."""
    
    def __init__(self, 
                 embedding_manager,
                 cache_manager, 
                 platform: str, 
                 example_dir_template: str,
                 max_example_size: int,
                 max_examples: int):
        """Inicializa el cargador de ejemplos.
        
        Args:
            embedding_manager: Administrador de embeddings
            cache_manager: Administrador de caché
            platform: Plataforma seleccionada
            example_dir_template: Plantilla para el directorio de ejemplos
            max_example_size: Tamaño máximo para ejemplos (antes de truncar)
            max_examples: Número máximo de ejemplos a cargar
        """
        self.embedding_manager = embedding_manager
        self.cache_manager = cache_manager
        self.platform = platform
        self.example_dir_template = example_dir_template
        self.max_example_size = max_example_size
        self.max_examples = max_examples
        self.force_truncate = False
        self.use_embeddings = True
        self.embeddings_cache = {}
        
    def load_code_examples(self) -> List[Dict[str, str]]:
        """Carga ejemplos de código para la plataforma seleccionada.
        
        Returns:
            Lista de diccionarios con {"path": ruta_relativa, "content": contenido}
        """
        examples_dir = Path(self.example_dir_template.format(platform=self.platform))
        logging.info(f"📚 Cargando ejemplos de código para {self.platform.upper().replace('_', ' ')}...")
        
        examples = []
        
        # Intentar cargar el caché de embeddings
        self.embeddings_cache = self.cache_manager.load_cache()
        
        # Buscar recursivamente en todas las carpetas
        all_c_files = list(examples_dir.rglob('*.c'))
        if not all_c_files:
            logging.warning(f"⚠️ No se encontraron archivos .c en {examples_dir}")
            return examples
        
        # Calcular el número aproximado de tokens
        estimated_max_tokens = estimate_tokens(self.max_example_size)
        logging.info(f"Tamaño máximo de ejemplo: {self.max_example_size} caracteres (~{estimated_max_tokens} tokens)")
        
        # Cargar contenido de archivos y generar embeddings si es necesario
        need_to_update_cache = False
        for file_path in all_c_files:
            rel_path = str(file_path.relative_to(examples_dir))
            
            # Verificar si necesitamos procesar este archivo
            # Lo hacemos si: no está en caché O si está en caché pero se fuerza truncado
            if rel_path not in self.embeddings_cache or self.force_truncate:
                # Cargar el archivo fresco
                try:
                    content = build_example_context(file_path, examples_dir, self.max_example_size)
                    
                    # Truncar ejemplos extremadamente grandes
                    original_size = len(content)
                    estimated_tokens = estimate_tokens(content)
                    
                    if original_size > self.max_example_size:
                        # Estrategia de truncado: mantener inicio y final
                        first_part_size = int(self.max_example_size * 0.7)  # 70% para el inicio
                        last_part_size = self.max_example_size - first_part_size  # 30% para el final
                        
                        first_part = content[:first_part_size]
                        last_part = content[-last_part_size:] if last_part_size > 0 else ""
                        
                        # Mensaje de truncación
                        truncation_msg = f"\n/* ... CONTENIDO TRUNCADO ({original_size - self.max_example_size} caracteres) ... */\n"
                        
                        # Combinar las partes
                        content = first_part + truncation_msg + last_part
                        
                        logging.warning(f"⚠️ Ejemplo truncado: {rel_path} ({original_size} -> {len(content)} caracteres)")
                        logging.warning(f"   Tokens estimados: {estimated_tokens} -> {estimate_tokens(content)}")
                    
                    # Actualizar caché o añadir nueva entrada
                    self.embeddings_cache[rel_path] = (content, None)  # Embedding a None para regenerarlo después
                    examples.append({"path": rel_path, "content": content})
                    need_to_update_cache = True
                    
                    if self.force_truncate and rel_path in self.embeddings_cache:
                        logging.info(f"🔄 Ejemplo recargado y truncado (forzado): {rel_path}")
                    
                except Exception as e:
                    logging.warning(f"Error al cargar ejemplo {file_path}: {e}")
            else:
                # El archivo ya está en la caché, usar su contenido y embedding
                content, _ = self.embeddings_cache[rel_path]
                examples.append({"path": rel_path, "content": content})
        
        # Generar embeddings para archivos nuevos o modificados
        if need_to_update_cache and self.use_embeddings:
            logging.info("Generando embeddings para nuevos archivos...")
            success_count = 0
            error_count = 0
            
            for rel_path, (content, embedding) in list(self.embeddings_cache.items()):
                if embedding is None:
                    # Añadir una pequeña pausa para evitar rate limits en la API
                    time.sleep(0.25)  # Pausa más larga para evitar problemas de rate limiting
                    try:
                        # Para archivos extremadamente grandes, usar estrategia adaptativa
                        if len(content) > self.max_example_size * 1.5:
                            logging.warning(f"Archivo extremadamente grande ({len(content)} caracteres) en generación de embeddings. Usando estrategia adaptativa.")
                            new_embedding = self.embedding_manager.get_embedding_for_large_file(content)
                        else:
                            # Para archivos de tamaño normal, generar embedding directamente
                            source_path = examples_dir / rel_path
                            support_files = discover_support_files(
                                source_path,
                                source_path.parent.parent if source_path.parent.name == "src" else source_path.parent,
                            )
                            embedding_text = build_embedding_text(rel_path, content, support_files)
                            new_embedding = self.embedding_manager.get_embedding(embedding_text)
                        
                        # VALIDACIÓN AGREGADA: Verificar explícitamente que el embedding es un array y no un escalar
                        if isinstance(new_embedding, (int, float)):
                            logging.error(f"❌ Error crítico: Embedding para {rel_path} es un escalar ({type(new_embedding)})")
                            # Reemplazar con un array vacío para evitar el error 'int' has no len()
                            new_embedding = np.zeros((1536,), dtype=float)
                            logging.warning(f"Reemplazando embedding escalar con array vacío para evitar errores")
                        
                        # Verificación adicional para asegurar que es un array numpy
                        if not isinstance(new_embedding, np.ndarray):
                            logging.error(f"❌ Embedding para {rel_path} no es un array numpy ({type(new_embedding)})")
                            new_embedding = np.zeros((1536,), dtype=float)
                            
                        self.embeddings_cache[rel_path] = (content, new_embedding)
                        success_count += 1
                    except Exception as e:
                        logging.error(f"Error al generar embedding para {rel_path}: {e}")
                        # Asegurarse de que no hay valores escalares en la caché
                        self.embeddings_cache[rel_path] = (content, np.zeros((1536,), dtype=float))
                        error_count += 1
            
            logging.info(f"Embeddings generados: {success_count} exitosos, {error_count} con error")
            
            # Guardar el caché actualizado
            try:
                self.cache_manager.save_cache(self.embeddings_cache)
            except Exception as e:
                logging.error(f"Error al guardar caché de embeddings: {e}")
                logging.info("Intentando corregir caché antes de guardar...")
                # Intento de corrección: verificar y corregir cada entrada
                corrected_cache = {}
                for path, (content, emb) in self.embeddings_cache.items():
                    if isinstance(emb, (int, float)):
                        corrected_cache[path] = (content, np.zeros((1536,), dtype=float))
                    else:
                        corrected_cache[path] = (content, emb)
                self.embeddings_cache = corrected_cache
                # Intentar guardar nuevamente
                try:
                    self.cache_manager.save_cache(self.embeddings_cache)
                    logging.info("Caché corregido y guardado exitosamente.")
                except Exception as e2:
                    logging.error(f"No se pudo guardar el caché corregido: {e2}")
        
        logging.info(f"✅ {len(examples)} ejemplos cargados.")
        return examples
        
    def load_code_examples_basic(self) -> List[Dict[str, str]]:
        """Carga ejemplos de código de manera básica sin usar embeddings.
        
        Returns:
            Lista de diccionarios con {"path": ruta_relativa, "content": contenido}
        """
        examples_dir = Path(self.example_dir_template.format(platform=self.platform))
        logging.info(f"📚 Cargando ejemplos de código básicos para {self.platform.upper().replace('_', ' ')}...")
        
        examples = []
        
        # Buscar recursivamente en todas las carpetas
        all_c_files = list(examples_dir.rglob('*.c'))
        if not all_c_files:
            logging.warning(f"⚠️ No se encontraron archivos .c en {examples_dir}")
            return examples
            
        # Si hay demasiados archivos, toma una muestra aleatoria para mayor diversidad
        if len(all_c_files) > self.max_examples * 3:
            random.shuffle(all_c_files)
            all_c_files = all_c_files[:self.max_examples * 3]
        
        # Cargar contenido de archivos
        for file_path in all_c_files:
            rel_path = str(file_path.relative_to(examples_dir))
            
            try:
                content = build_example_context(file_path, examples_dir, self.max_example_size)
                
                # Truncar ejemplos extremadamente grandes
                original_size = len(content)
                
                if original_size > self.max_example_size:
                    # Estrategia de truncado
                    first_part_size = int(self.max_example_size * 0.7)
                    last_part_size = self.max_example_size - first_part_size
                    
                    first_part = content[:first_part_size]
                    last_part = content[-last_part_size:] if last_part_size > 0 else ""
                    
                    truncation_msg = f"\n/* ... CONTENIDO TRUNCADO ({original_size - self.max_example_size} caracteres) ... */\n"
                    content = first_part + truncation_msg + last_part
                    
                    logging.info(f"⚠️ Ejemplo truncado: {rel_path} ({original_size} -> {len(content)} caracteres)")
                
                examples.append({"path": rel_path, "content": content})
                
            except Exception as e:
                logging.warning(f"Error al cargar ejemplo {file_path}: {e}")
        
        logging.info(f"✅ {len(examples)} ejemplos básicos cargados.")
        
        # Ordenar por tamaño para tomar una muestra variada
        examples.sort(key=lambda x: len(x["content"]))
        
        # Tomar ejemplos variados: algunos pequeños, medianos y grandes
        result = []
        step = max(1, len(examples) // self.max_examples)
        for i in range(0, len(examples), step):
            if len(result) < self.max_examples:
                result.append(examples[i])
        
        return result
        
    def get_relevant_examples(self, user_request: str, max_examples: Optional[int] = None) -> List[Dict[str, str]]:
        """Obtiene los ejemplos más relevantes para la solicitud del usuario.
        
        Args:
            user_request: Solicitud del usuario
            max_examples: Número máximo de ejemplos a devolver (o None para usar el valor por defecto)
            
        Returns:
            Lista de ejemplos relevantes, cada uno como un diccionario {"path": ruta, "content": contenido}
        """
        if max_examples is None:
            max_examples = self.max_examples
        
        if not self.embeddings_cache:
            logging.warning("No hay caché de embeddings disponible para búsqueda semántica.")
            # Cargar todos los ejemplos como respaldo
            examples = self.load_code_examples()
            return examples[:max_examples]
        
        logging.info(f"🔍 Buscando {max_examples} ejemplos relevantes para la solicitud...")
        
        # Obtener embedding para la solicitud del usuario
        query_embedding = self.embedding_manager.get_embedding(user_request)
        
        # Verificar que el embedding sea válido
        if not isinstance(query_embedding, np.ndarray) or query_embedding.size == 0 or np.all(query_embedding == 0):
            logging.warning("❌ No se pudo generar un embedding válido para la consulta. Usando ejemplos aleatorios.")
            # Si no tenemos un embedding válido para la consulta, devolver algunos ejemplos de forma aleatoria
            all_examples = []
            for rel_path, (content, _) in self.embeddings_cache.items():
                all_examples.append({"path": rel_path, "content": content})
            
            # Limitar a la cantidad solicitada
            random.shuffle(all_examples)
            return all_examples[:max_examples]
        
        # Calcular similitud con todos los ejemplos
        similarities = []
        valid_embeddings_count = 0
        invalid_embeddings_count = 0
        
        for rel_path, (content, embedding) in self.embeddings_cache.items():
            # VERIFICACIÓN CRÍTICA: Detección de embeddings escalares (int/float)
            # Esta es la fuente potencial del error "object of type 'int' has no len()"
            if isinstance(embedding, (int, float)):
                logging.error(f"⚠️ ERROR CRÍTICO: Se detectó un embedding escalar ({type(embedding)}) para {rel_path}")
                logging.error(f"📍 CAUSA DEL ERROR 'object of type int has no len()' en llmz80/core/examples_loader.py:get_relevant_examples")
                # Crear un embedding vacío para evitar que falle el algoritmo
                embedding = np.zeros((1536,), dtype=float)
                # Actualizar el caché con el embedding corregido
                self.embeddings_cache[rel_path] = (content, embedding)
                invalid_embeddings_count += 1
            
            # Verificar que el embedding sea válido
            if (embedding is not None and 
                isinstance(embedding, np.ndarray) and 
                embedding.size > 0 and 
                not np.all(embedding == 0)):
                try:
                    # PROTECCIÓN ADICIONAL: Verificar explícitamente ambos argumentos
                    if not isinstance(query_embedding, np.ndarray):
                        logging.error(f"⚠️ Error en cosine_similarity: query_embedding no es numpy array: {type(query_embedding)}")
                        continue
                    if not isinstance(embedding, np.ndarray):
                        logging.error(f"⚠️ Error en cosine_similarity: embedding para {rel_path} no es numpy array: {type(embedding)}")
                        continue
                        
                    # Intentar calcular similitud con manejo de errores explícito
                    try:
                        similarity = self.embedding_manager.cosine_similarity(query_embedding, embedding)
                        similarities.append((rel_path, content, similarity))
                        valid_embeddings_count += 1
                    except TypeError as e:
                        if "object of type 'int' has no len()" in str(e):
                            logging.error(f"⚠️ ERROR 'int' has no len() al calcular similitud para {rel_path}")
                            logging.error(f"📍 Tipos: query_embedding={type(query_embedding)}, embedding={type(embedding)}")
                            invalid_embeddings_count += 1
                        else:
                            raise
                except Exception as e:
                    logging.warning(f"Error al calcular similitud para {rel_path}: {e}")
                    invalid_embeddings_count += 1
            else:
                invalid_embeddings_count += 1
                # No lo incluimos para cálculo de similitud
        
        # Si se detectaron problemas con los embeddings, intentar reparar el caché
        if invalid_embeddings_count > 0:
            logging.warning(f"Se ignoraron {invalid_embeddings_count} embeddings inválidos o nulos.")
            # Intentar guardar el caché corregido
            try:
                self.cache_manager.save_cache(self.embeddings_cache)
                logging.info("✅ Caché corregido guardado automáticamente.")
            except Exception as e:
                logging.error(f"Error al guardar caché corregido: {e}")
        
        if not similarities:
            logging.warning("❌ No se encontraron embeddings válidos para comparar. Usando ejemplos aleatorios.")
            # Si no hay embeddings válidos, devolver algunos ejemplos de forma aleatoria
            all_examples = []
            for rel_path, (content, _) in self.embeddings_cache.items():
                all_examples.append({"path": rel_path, "content": content})
            
            # Limitar a la cantidad solicitada
            random.shuffle(all_examples)
            return all_examples[:max_examples]
        
        # Ordenar por similitud descendente
        similarities.sort(key=lambda x: x[2], reverse=True)
        
        # Tomar los N ejemplos más relevantes
        relevant_examples = []
        for rel_path, content, similarity in similarities[:max_examples]:
            logging.debug(f"Ejemplo relevante: {rel_path} (similitud: {similarity:.4f})")
            relevant_examples.append({"path": rel_path, "content": content})
        
        logging.info(f"✅ Se encontraron {len(relevant_examples)} ejemplos relevantes (de {valid_embeddings_count} válidos).")
        return relevant_examples 
