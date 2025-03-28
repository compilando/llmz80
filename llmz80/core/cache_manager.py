import json
import logging
import numpy as np
from pathlib import Path
import shutil
from datetime import datetime
from typing import Dict, Tuple, Any, List, Optional

class EmbeddingsCacheManager:
    """Gestiona la carga, guardado y mantenimiento del caché de embeddings."""
    
    def __init__(self, platform: str, cache_dir: Path):
        """Inicializa el gestor de caché de embeddings.
        
        Args:
            platform: Plataforma seleccionada
            cache_dir: Directorio para almacenar el caché
        """
        self.platform = platform
        self.cache_dir = cache_dir
        self.cache_file = cache_dir / f"{platform}_embeddings.json"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def load_cache(self) -> Dict[str, Tuple[str, np.ndarray]]:
        """Carga el caché de embeddings si existe.
        
        Returns:
            Diccionario con las rutas de archivo y sus correspondientes (contenido, embedding)
        """
        if not self.cache_file.exists():
            logging.info(f"No se encontró caché de embeddings en {self.cache_file}")
            return {}
        
        try:
            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)
            
            embeddings_cache = {}
            valid_count = 0
            invalid_count = 0
            
            if not isinstance(cache_data, dict):
                logging.error("⚠️ Caché corrupto: El formato no es un diccionario")
                return {}
            
            for file_path, data in cache_data.items():
                if not isinstance(file_path, str):
                    invalid_count += 1
                    continue
                
                if not isinstance(data, (list, tuple)) or len(data) != 2:
                    invalid_count += 1
                    continue
                
                content, embedding_data = data
                if not isinstance(content, str):
                    content = str(content) if content is not None else ""
                
                if embedding_data is not None and isinstance(embedding_data, list):
                    try:
                        embedding_array = np.array(embedding_data, dtype=float)
                        if embedding_array.size > 0:
                            embeddings_cache[file_path] = (content, embedding_array)
                            valid_count += 1
                        else:
                            embeddings_cache[file_path] = (content, None)
                            invalid_count += 1
                    except Exception:
                        embeddings_cache[file_path] = (content, None)
                        invalid_count += 1
                else:
                    embeddings_cache[file_path] = (content, None)
                    invalid_count += 1
            
            logging.info(f"✅ Caché cargado: {valid_count} embeddings válidos, {invalid_count} a regenerar")
            return embeddings_cache
            
        except json.JSONDecodeError:
            logging.error(f"El archivo de caché {self.cache_file} no es un JSON válido")
            try:
                corrupted_backup = self.cache_dir / f"{self.platform}_embeddings_corrupted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                shutil.copy2(self.cache_file, corrupted_backup)
                logging.info(f"Backup del caché corrupto guardado en {corrupted_backup}")
            except:
                pass
            return {}
        except Exception as e:
            logging.error(f"Error al cargar el caché de embeddings: {e}")
            return {}
    
    def save_cache(self, embeddings_cache: Dict[str, Tuple[str, np.ndarray]]) -> None:
        """Guarda el caché de embeddings.
        
        Args:
            embeddings_cache: Diccionario de (ruta_archivo, (contenido, embedding))
        """
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            serializable_cache = {}
            valid_count = 0
            invalid_count = 0
            
            for file_path, data in embeddings_cache.items():
                if not isinstance(data, (tuple, list)) or len(data) != 2:
                    invalid_count += 1
                    continue
                
                content, embedding_array = data
                if not isinstance(content, str):
                    content = str(content) if content is not None else ""
                
                if embedding_array is not None and isinstance(embedding_array, np.ndarray) and embedding_array.size > 0:
                    try:
                        serializable_cache[file_path] = (content, embedding_array.tolist())
                        valid_count += 1
                    except Exception:
                        serializable_cache[file_path] = (content, None)
                        invalid_count += 1
                else:
                    serializable_cache[file_path] = (content, None)
                    invalid_count += 1
            
            with open(self.cache_file, 'w') as f:
                json.dump(serializable_cache, f)
            
            logging.info(f"✅ Caché guardado: {valid_count} embeddings válidos, {invalid_count} inválidos")
            
        except Exception as e:
            logging.error(f"Error al guardar el caché de embeddings: {e}")
            try:
                emergency_file = self.cache_dir / f"{self.platform}_embeddings_emergency.json"
                emergency_cache = {k: (v[0] if isinstance(v, (tuple, list)) and len(v) > 0 else "", None) 
                                 for k, v in embeddings_cache.items()}
                with open(emergency_file, 'w') as f:
                    json.dump(emergency_cache, f)
                logging.info(f"✅ Caché de emergencia guardado en {emergency_file}")
            except Exception as e2:
                logging.error(f"Error al guardar el caché de emergencia: {e2}")
                
    def clear_cache(self) -> None:
        """Elimina el caché de embeddings para la plataforma actual."""
        try:
            if self.cache_file.exists():
                self.cache_file.unlink()
                logging.info(f"✅ Caché de embeddings eliminado: {self.cache_file}")
            else:
                logging.info(f"No existe archivo de caché para eliminar: {self.cache_file}")
        except Exception as e:
            logging.error(f"Error al eliminar el caché de embeddings: {e}")
            
    def repair_invalid_embeddings(self) -> bool:
        """Busca y repara especificamente valores escalares en el caché de embeddings.
        
        Returns:
            bool: True si se realizaron reparaciones, False si no
        """
        if not self.cache_file.exists():
            logging.info(f"No hay caché para reparar: {self.cache_file}")
            return False
        
        try:
            # Cargar el caché actual
            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)
                
            if not isinstance(cache_data, dict):
                logging.error(f"⚠️ El caché no es un diccionario. No se puede reparar.")
                return False
                
            # Hacer una copia para modificar
            fixed_cache = {}
            scalar_count = 0
            other_invalid_count = 0
            valid_count = 0
            
            # Revisar cada entrada buscando escalares
            for file_path, data_tuple in cache_data.items():
                if not isinstance(file_path, str):
                    other_invalid_count += 1
                    continue  # Ignorar entradas con claves no válidas
                
                # Verificar si es una tupla/lista válida
                if not isinstance(data_tuple, (tuple, list)):
                    logging.warning(f"⚠️ Entrada inválida para {file_path}: {type(data_tuple)}")
                    # Si es un string, asumir que es contenido
                    if isinstance(data_tuple, str):
                        fixed_cache[file_path] = (data_tuple, None)
                    else:
                        fixed_cache[file_path] = ("", None)
                    other_invalid_count += 1
                    continue
                    
                # Verificar longitud
                if len(data_tuple) != 2:
                    logging.warning(f"⚠️ Formato inválido para {file_path}: {len(data_tuple)} elementos")
                    # Intentar rescatar el primer elemento si es string
                    if len(data_tuple) > 0 and isinstance(data_tuple[0], str):
                        fixed_cache[file_path] = (data_tuple[0], None)
                    else:
                        fixed_cache[file_path] = ("", None)
                    other_invalid_count += 1
                    continue
                
                # Extraer valores
                content, embedding = data_tuple
                
                # Verificar que el contenido sea un string
                if not isinstance(content, str):
                    content = str(content) if content is not None else ""
                    logging.warning(f"⚠️ Contenido no string para {file_path}, convertido a: '{content}'")
                
                # CASO CRÍTICO: detectar valores escalares (int o float)
                if isinstance(embedding, (int, float)):
                    logging.error(f"⚠️ ¡ENCONTRADO! Embedding escalar ({type(embedding)}) en {file_path}: {embedding}")
                    # Reemplazar con None para regenerar
                    fixed_cache[file_path] = (content, None)
                    scalar_count += 1
                    continue
                
                # Verificar otros casos inválidos
                if embedding is None:
                    # Mantener como None para regenerar
                    fixed_cache[file_path] = (content, None)
                    other_invalid_count += 1
                elif not isinstance(embedding, list):
                    logging.warning(f"⚠️ Embedding de tipo inválido en {file_path}: {type(embedding)}")
                    fixed_cache[file_path] = (content, None)
                    other_invalid_count += 1
                else:
                    # Verificar que la lista contenga números
                    if all(isinstance(x, (int, float)) for x in embedding):
                        # Parece un embedding válido
                        fixed_cache[file_path] = (content, embedding)
                        valid_count += 1
                    else:
                        logging.warning(f"⚠️ Embedding con elementos no numéricos en {file_path}")
                        fixed_cache[file_path] = (content, None)
                        other_invalid_count += 1
            
            # Si no se encontraron problemas, no hay que guardar
            if scalar_count == 0 and other_invalid_count == 0:
                logging.info("✅ No se encontraron valores escalares ni otros problemas en el caché.")
                return False
                
            # Guardar caché reparado
            # Primero hacer backup
            backup_file = self.cache_dir / f"{self.platform}_embeddings_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            try:
                shutil.copy2(self.cache_file, backup_file)
                logging.info(f"Backup del caché original guardado en {backup_file}")
            except Exception as e:
                logging.warning(f"No se pudo crear backup: {e}")
            
            # Guardar caché reparado
            with open(self.cache_file, 'w') as f:
                json.dump(fixed_cache, f)
                
            logging.info(f"✅ Caché reparado guardado en {self.cache_file}")
            logging.info(f"   Reparados: {scalar_count} escalares, {other_invalid_count} otros problemas, {valid_count} entradas válidas")
            
            return True
            
        except Exception as e:
            logging.error(f"Error al reparar el caché: {e}")
            return False
            
    def verify_and_repair_cache(self) -> None:
        """Verifica el estado del caché de embeddings y lo repara si es necesario."""
        backup_file = self.cache_dir / f"{self.platform}_embeddings_backup.json"
        
        if not self.cache_file.exists():
            logging.info(f"No hay caché para verificar: {self.cache_file}")
            return
        
        # Primero intentar reparar valores escalares y otros problemas críticos
        if self.repair_invalid_embeddings():
            logging.info("✅ Reparación de valores escalares y otros problemas completada.")
        else:
            logging.info("✅ No se encontraron valores escalares ni otros problemas críticos.")
            
        try:
            # Intentar cargar el caché para verificarlo
            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)
                
            # Verificar estructura básica (debe ser un diccionario)
            if not isinstance(cache_data, dict):
                raise ValueError("El caché no es un diccionario JSON válido")
                
            # Verificar cada entrada
            valid_entries = {}
            invalid_count = 0
            
            for file_path, data_tuple in cache_data.items():
                if not isinstance(file_path, str):
                    invalid_count += 1
                    continue
                    
                # Verificar que data_tuple sea una lista/tupla de 2 elementos
                if not isinstance(data_tuple, (list, tuple)) or len(data_tuple) != 2:
                    invalid_count += 1
                    continue
                    
                content, embedding = data_tuple
                
                # Verificar contenido
                if not isinstance(content, str):
                    invalid_count += 1
                    continue
                    
                # Verificar embedding (si no es None)
                if embedding is not None:
                    if not isinstance(embedding, list):
                        # Marcar para regeneración
                        valid_entries[file_path] = (content, None)
                        invalid_count += 1
                    else:
                        # Verificar que todos los elementos sean números
                        if all(isinstance(x, (int, float)) for x in embedding):
                            valid_entries[file_path] = (content, embedding)
                        else:
                            valid_entries[file_path] = (content, None)
                            invalid_count += 1
                else:
                    # Mantener entradas con embedding None
                    valid_entries[file_path] = (content, None)
            
            # Si hay entradas inválidas, hacer backup y guardar la versión reparada
            if invalid_count > 0:
                logging.warning(f"Se encontraron {invalid_count} entradas inválidas en el caché.")
                
                # Hacer backup del caché original
                if self.cache_file.exists():
                    # Crear directorio de backup si no existe
                    self.cache_dir.mkdir(parents=True, exist_ok=True)
                    # Copiar archivo actual a backup
                    shutil.copy2(self.cache_file, backup_file)
                    logging.info(f"Backup guardado en {backup_file}")
                
                # Guardar versión reparada
                with open(self.cache_file, 'w') as f:
                    json.dump(valid_entries, f)
                    
                logging.info(f"✅ Caché reparado y guardado en {self.cache_file}")
            else:
                logging.info(f"✅ Caché verificado sin problemas: {len(valid_entries)} entradas válidas.")
                
        except json.JSONDecodeError:
            logging.error(f"El archivo de caché {self.cache_file} está corrupto y no puede ser decodificado como JSON.")
            
            # Hacer backup del caché corrupto
            if self.cache_file.exists():
                self.cache_dir.mkdir(parents=True, exist_ok=True)
                # Añadir timestamp al nombre para evitar sobrescribir backups anteriores
                corrupted_backup = self.cache_dir / f"{self.platform}_embeddings_corrupted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                shutil.copy2(self.cache_file, corrupted_backup)
                logging.info(f"Backup del caché corrupto guardado en {corrupted_backup}")
                
                # Borrar el caché corrupto
                self.cache_file.unlink()
                logging.info(f"Caché corrupto eliminado. Se creará uno nuevo en la próxima ejecución.")
        except Exception as e:
            logging.error(f"Error al verificar el caché: {e}") 