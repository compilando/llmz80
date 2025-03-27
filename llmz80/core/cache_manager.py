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
            
            # Convertir las listas de embeddings en numpy arrays
            embeddings_cache = {}
            valid_count = 0
            invalid_count = 0
            
            # Verificar que cache_data sea un diccionario
            if not isinstance(cache_data, dict):
                logging.error(f"Caché corrupto: El formato no es un diccionario. Regenerando caché.")
                return {}
            
            for file_path, data_tuple in cache_data.items():
                # Verificar que data_tuple sea una tupla o lista con 2 elementos
                if not isinstance(data_tuple, (list, tuple)) or len(data_tuple) != 2:
                    logging.warning(f"Formato incorrecto para {file_path} en caché. Será regenerado.")
                    invalid_count += 1
                    continue
                
                # Extraer contenido y embedding
                content, embedding_data = data_tuple
                
                # Verificar que el contenido sea un string
                if not isinstance(content, str):
                    logging.warning(f"Contenido no es string para {file_path}. Será ignorado.")
                    invalid_count += 1
                    continue
                
                # Procesar el embedding si existe
                if embedding_data is not None:
                    # Verificar que embedding_data sea una lista de números
                    if isinstance(embedding_data, list) and all(isinstance(x, (int, float)) for x in embedding_data):
                        try:
                            # Convertir a array numpy
                            embedding_array = np.array(embedding_data, dtype=float)
                            # Solo añadir si el array no está vacío
                            if embedding_array.size > 0:
                                embeddings_cache[file_path] = (content, embedding_array)
                                valid_count += 1
                            else:
                                embeddings_cache[file_path] = (content, None)
                                invalid_count += 1
                                logging.warning(f"Embedding vacío para {file_path}. Será regenerado.")
                        except Exception as e:
                            logging.warning(f"Error al convertir embedding para {file_path}: {e}. Será regenerado.")
                            embeddings_cache[file_path] = (content, None)
                            invalid_count += 1
                    else:
                        logging.warning(f"Embedding inválido para {file_path}: tipo {type(embedding_data)}. Será regenerado.")
                        embeddings_cache[file_path] = (content, None)
                        invalid_count += 1
                else:
                    # Si el embedding es None, mantenerlo como None para regenerarlo
                    embeddings_cache[file_path] = (content, None)
                    invalid_count += 1
            
            logging.info(f"✅ Caché cargado: {valid_count} embeddings válidos, {invalid_count} a regenerar.")
            
            # Si todos los embeddings son inválidos, podríamos tener un problema con el formato del caché
            if valid_count == 0 and invalid_count > 0:
                logging.warning(f"⚠️ Todos los embeddings ({invalid_count}) necesitan regeneración.")
            
            return embeddings_cache
            
        except json.JSONDecodeError:
            logging.error(f"El archivo de caché {self.cache_file} no es un JSON válido. Se ignorará.")
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
            # Convertir numpy arrays a listas para serialización JSON
            serializable_cache = {}
            valid_count = 0
            invalid_count = 0
            
            for file_path, (content, embedding_array) in embeddings_cache.items():
                if embedding_array is not None and isinstance(embedding_array, np.ndarray) and embedding_array.size > 0:
                    try:
                        # Verificar que el embedding es válido para serializar
                        embedding_list = embedding_array.tolist()
                        serializable_cache[file_path] = (content, embedding_list)
                        valid_count += 1
                    except Exception as e:
                        logging.warning(f"Error al serializar embedding para {file_path}: {e}")
                        # Guardar con embedding None para regenerar en la próxima ejecución
                        serializable_cache[file_path] = (content, None)
                        invalid_count += 1
                else:
                    # Guardar con embedding None para regenerar en la próxima ejecución
                    serializable_cache[file_path] = (content, None)
                    invalid_count += 1
            
            with open(self.cache_file, 'w') as f:
                json.dump(serializable_cache, f)
            
            logging.info(f"✅ Caché de embeddings guardado en {self.cache_file}")
            logging.info(f"   Embeddings guardados: {valid_count} válidos, {invalid_count} inválidos o nulos")
        except Exception as e:
            logging.error(f"Error al guardar el caché de embeddings: {e}")
            # Intentar guardar un archivo de emergencia para recuperar al menos los contenidos
            try:
                emergency_file = self.cache_dir / f"{self.platform}_embeddings_emergency.json"
                emergency_cache = {}
                
                for file_path, (content, _) in embeddings_cache.items():
                    # Guardar solo los contenidos sin embeddings
                    emergency_cache[file_path] = (content, None)
                
                with open(emergency_file, 'w') as f:
                    json.dump(emergency_cache, f)
                
                logging.info(f"✅ Caché de emergencia guardado en {emergency_file} (sin embeddings)")
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
            
    def verify_and_repair_cache(self) -> None:
        """Verifica el estado del caché de embeddings y lo repara si es necesario."""
        backup_file = self.cache_dir / f"{self.platform}_embeddings_backup.json"
        
        if not self.cache_file.exists():
            logging.info(f"No hay caché para verificar: {self.cache_file}")
            return
            
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