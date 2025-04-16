import logging
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from openai import OpenAI
import numpy as np

# Obtener instancia del logger para este módulo
logger = logging.getLogger(__name__)

from ..core.embeddings import EmbeddingsManager
from ..core.cache_manager import EmbeddingsCacheManager
from ..core.examples_loader import ExamplesLoader
from ..utils.helpers import clean_api_response, get_output_paths
from vector_db import get_qdrant_client, search_similar

class LLMZ80Generator:
    """Generador de código Z80 utilizando LLMs."""
    
    def __init__(self, platform: str, global_vars: Dict[str, Any], api_key: str):
        """Inicializa el generador de código Z80.
        
        Args:
            platform: Plataforma objetivo (spectrum, amstrad_cpc, etc.)
            global_vars: Variables globales de configuración
            api_key: Clave de API para OpenAI
        """
        self.platform = platform.lower()
        self.global_vars = global_vars
        
        # Inicialización del cliente de OpenAI
        self.api_key = api_key
        self.client = OpenAI(api_key=self.api_key)
        
        # Opciones de configuración
        self.model = global_vars['model']
        self.temperature = global_vars['temperature']
        self.max_tokens = global_vars['max_tokens']
        self.max_examples = global_vars['max_examples']
        self.system_prompt_file = global_vars['system_prompt_file']
        self.base_output_dir = global_vars['base_output_dir']
        self.slug_max_length = global_vars['slug_max_length']
        
        # Opciones para la búsqueda semántica
        self.use_embeddings = True
        self.force_truncate = False
        
        # Inicializar manejadores
        self.embedding_manager = EmbeddingsManager(
            self.client,
            self.platform,
            global_vars
        )
        
        self.cache_manager = EmbeddingsCacheManager(
            self.platform,
            global_vars['embeddings_cache_dir']
        )
        
        self.examples_loader = ExamplesLoader(
            self.embedding_manager,
            self.cache_manager,
            self.platform,
            global_vars['example_dir_template'],
            global_vars['max_example_size'],
            self.max_examples
        )
        
        logging.info(f"🚀 Inicializando Generador de Código LLMZ80 para {self.platform.upper().replace('_', ' ')}")
        logging.info(f"⚙️ Usando Modelo: {self.model}, Temp: {self.temperature}, Max Tokens: {self.max_tokens}, Max Ejemplos: {self.max_examples}")
        logging.info("✅ Generador inicializado correctamente.")
        
    def set_force_truncate(self, value: bool) -> None:
        """Establece la opción para forzar el truncado de ejemplos.
        
        Args:
            value: True para forzar truncado, False en caso contrario
        """
        self.force_truncate = value
        self.examples_loader.force_truncate = value
        if value:
            logging.info("Modo de truncado forzado activado.")
        else:
            logging.info("Modo de truncado forzado desactivado.")
            
    def set_use_embeddings(self, value: bool) -> None:
        """Establece la opción para usar embeddings en la búsqueda semántica.
        
        Args:
            value: True para usar embeddings, False para usar ejemplos básicos
        """
        self.use_embeddings = value
        self.examples_loader.use_embeddings = value
        if value:
            logging.info("Uso de embeddings activado para búsqueda semántica.")
        else:
            logging.info("Uso de embeddings desactivado. Se utilizarán ejemplos básicos.")
            
    def rebuild_embeddings_cache(self) -> None:
        """Elimina y reconstruye completamente el caché de embeddings."""
        # Delegar al administrador de caché y ejemplos
        self.cache_manager.clear_cache()
        
        # Cargar todos los ejemplos (esto regenerará los embeddings)
        self.examples_loader.load_code_examples()
        
        logging.info("✅ Reconstrucción de caché de embeddings completada.")
        
    def test_file_embedding(self, file_path: str) -> None:
        """Prueba la generación de embeddings para un archivo específico.
        
        Args:
            file_path: Ruta al archivo a probar
        """
        try:
            # Verificar que el archivo existe
            if not os.path.exists(file_path):
                logging.error(f"⚠️ El archivo {file_path} no existe")
                return
                
            logging.info(f"🧪 Probando generación de embedding para archivo: {file_path}")
            
            # Cargar contenido del archivo
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Mostrar info del archivo
            file_size = len(content)
            from ..utils.helpers import estimate_tokens
            estimated_tokens = estimate_tokens(content)
            logging.info(f"📄 Tamaño del archivo: {file_size} caracteres (~{estimated_tokens} tokens estimados)")
            
            # Primero intentar con el método estándar
            logging.info("🔄 Intentando método estándar de embedding...")
            try:
                import time
                start_time = time.time()
                embedding = self.embedding_manager.get_embedding(content)
                elapsed = time.time() - start_time
                
                if isinstance(embedding, np.ndarray) and embedding.size > 0 and not np.all(embedding == 0):
                    logging.info(f"✅ Embedding generado correctamente con método estándar en {elapsed:.2f} segundos")
                    logging.info(f"   Dimensiones: {embedding.shape}, Norma: {norm(embedding):.4f}")
                else:
                    logging.warning(f"⚠️ El método estándar no generó un embedding válido")
            except Exception as e:
                logging.error(f"❌ Error al generar embedding con método estándar: {e}")
                
            # Luego intentar con el método para archivos grandes
            logging.info("🔄 Intentando método para archivos grandes...")
            try:
                start_time = time.time()
                large_embedding = self.embedding_manager.get_embedding_for_large_file(content)
                elapsed = time.time() - start_time
                
                if isinstance(large_embedding, np.ndarray) and large_embedding.size > 0 and not np.all(large_embedding == 0):
                    logging.info(f"✅ Embedding generado correctamente con método para archivos grandes en {elapsed:.2f} segundos")
                    from numpy.linalg import norm
                    logging.info(f"   Dimensiones: {large_embedding.shape}, Norma: {norm(large_embedding):.4f}")
                else:
                    logging.warning(f"⚠️ El método para archivos grandes no generó un embedding válido")
            except Exception as e:
                logging.error(f"❌ Error al generar embedding con método para archivos grandes: {e}")
                
            logging.info("🏁 Prueba de generación de embedding completada")
            
        except Exception as e:
            logging.error(f"❌ Error al probar el archivo {file_path}: {e}")
    
    def _load_platform_instructions(self) -> str:
        """Carga instrucciones específicas de la plataforma desde el archivo de prompt del sistema.
        
        Returns:
            Contenido del archivo de prompt
        """
        logging.info(f"📚 Cargando instrucciones de plataforma desde {self.system_prompt_file}...")
        content = ""
        try:
            if os.path.exists(self.system_prompt_file):
                with open(self.system_prompt_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                logging.info(f"✅ Instrucciones de plataforma cargadas ({len(content)} caracteres).")
            else:
                logging.warning(f"⚠️ Archivo de instrucciones de plataforma no encontrado: {self.system_prompt_file}")
        except Exception as e:
            logging.error(f"❌ Error al leer instrucciones de plataforma desde {self.system_prompt_file}: {e}")
        return content
        
    def _load_error_documentation(self) -> str:
        """Carga documentación de errores (*.md) recursivamente desde el directorio de ejemplos.
        
        Returns:
            Contenido combinado de la documentación
        """
        examples_dir = Path(self.global_vars['example_dir_template'].format(platform=self.platform))
        error_doc_pattern = self.global_vars['error_doc_glob_pattern']
        logging.info(f"📚 Cargando documentación de errores desde {examples_dir}...")
        docs_content = ""

        if not examples_dir.is_dir():
            logging.warning(f"⚠️ Directorio de ejemplos no encontrado para documentación de errores: {examples_dir}")
            return docs_content

        md_files = list(examples_dir.rglob(error_doc_pattern))

        if not md_files:
            logging.info("ℹ️ No se encontraron archivos de documentación (.md).")
            return docs_content

        logging.info(f"Se encontraron {len(md_files)} archivos de documentación.")
        for md_file in md_files:
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                    relative_path = md_file.relative_to(examples_dir)
                    docs_content += f"\n\n--- DOCUMENTATION: {relative_path} ---\n\n"
                    docs_content += file_content
                    logging.debug(f"  Documentación cargada: {relative_path}")
            except Exception as e:
                logging.error(f"❌ Error al cargar documentación {md_file}: {e}")

        logging.info(f"✅ Documentación de errores cargada ({len(docs_content)} caracteres).")
        return docs_content
        
    def _build_system_prompt(self, relevant_examples: List[Dict[str, str]] = None) -> str:
        """Construye el prompt completo del sistema incorporando instrucciones base, ejemplos y documentación.
        
        Args:
            relevant_examples: Lista de ejemplos relevantes a incluir
            
        Returns:
            Prompt completo del sistema
        """
        logging.debug("Construyendo prompt del sistema...")

        # 1. Instrucciones Base
        if self.platform == 'spectrum':
            base_prompt = """You are an expert Z88DK C code generator for ZX Spectrum 48K.
CRITICAL: Output ONLY the raw C source code. No introductory text, no explanations, no markdown fences (```), just the code itself.
Ensure the code is complete, directly compilable with 'zcc +zx', and functional on a ZX Spectrum 48K.
Adhere strictly to Z88DK's C dialect and library functions suitable for the Spectrum.
Prioritize clarity, efficiency for the Z80, and correct hardware interaction (screen, keyboard, sound if applicable).
"""
        elif self.platform == 'amstrad_cpc':
            base_prompt = """You are an expert CPCtelera C code generator for Amstrad CPC 464/6128.
CRITICAL: Output ONLY the raw C source code. No introductory text, no explanations, no markdown fences (```), just the code itself.
Ensure the code is complete, directly compilable with the CPCtelera toolchain, and functional on an Amstrad CPC.
Adhere strictly to the CPCtelera API and best practices. Do NOT use generic Z88DK functions unless they are part of the official CPCtelera API.
Prioritize clarity, efficiency for the Z80, static memory management, and correct hardware interaction using CPCtelera functions (graphics modes, keyboard, sound, etc.).
"""
        else:
            # Fallback - Consider raising an error for unsupported platforms
            logging.error(f"❌ Plataforma no soportada para prompt del sistema: {self.platform}")
            raise ValueError(f"Plataforma no soportada: {self.platform}")

        # 2. Instrucciones Específicas de la Plataforma desde Archivo
        platform_instructions = self._load_platform_instructions()

        # 3. Ejemplos de Código
        examples_prompt_part = "\n--- CODE EXAMPLES ---\n"
        examples_prompt_part += "Use the following examples as a reference for style, structure, and API usage:\n"
        
        # Usar los ejemplos relevantes proporcionados o cargar todos si no se proporcionan
        if relevant_examples is None:
            # Cargar ejemplos básicos si no se usan embeddings
            if self.use_embeddings:
                examples_to_use = self.examples_loader.load_code_examples()[:self.max_examples]
            else:
                examples_to_use = self.examples_loader.load_code_examples_basic()[:self.max_examples]
        else:
            examples_to_use = relevant_examples

        # Añadir ejemplos al prompt
        for i, example in enumerate(examples_to_use):
            # Recuperar path, contenido (source_code) y la descripción
            path = example.get('path', 'unknown_path')
            content = example.get('content', '#error: content not found') # 'content' ahora tiene el source_code
            description = example.get('description', '') # Obtener la descripción del payload
            score = example.get('score', 0.0) # Opcional: mostrar score

            # Añadir score al encabezado del ejemplo
            examples_prompt_part += f"\n--- Example {i+1} (Retrieved from: '{path}' - Relevance: {score:.4f}) ---"
            # Añadir la descripción si existe
            if description:
                examples_prompt_part += f"\nDescription: {description}\n"
            # Añadir el código fuente
            examples_prompt_part += f"\nCode:\n```c\n{content}\n```\n"
        
        # 4. Documentación de Errores
        error_docs = self._load_error_documentation()

        # 5. Combinar todas las partes
        full_system_prompt = base_prompt
        if platform_instructions:
             full_system_prompt += "\n--- PLATFORM INSTRUCTIONS ---\n" + platform_instructions
        if examples_to_use:
            full_system_prompt += examples_prompt_part
        if error_docs:
            # Append error docs (already contains header)
            full_system_prompt += error_docs
        # Final reminder
        full_system_prompt += "\n--- FINAL INSTRUCTIONS ---\nRemember: ONLY output the raw C code. No extra text or markdown."

        logging.debug(f"Prompt del sistema construido ({len(full_system_prompt)} caracteres).")
        return full_system_prompt
        
    def _build_user_prompt(self, user_request: str) -> str:
        """Builds the user prompt.
        
        Args:
            user_request: The user's request
            
        Returns:
            Formatted user prompt string
        """
        platform_name = self.platform.replace('_', ' ')
        # Keep it direct and clear
        return f"""Generate {platform_name} C code according to the system instructions that fulfills the following request: {user_request}

Please provide specific details about desired behaviors, controls, graphics mode (if applicable), and any other relevant technical requirements."""
        
    def generate_c_code(self, user_request: str) -> str:
        """Genera código C utilizando la API de OpenAI basado en la solicitud del usuario y el contexto.
        
        Args:
            user_request: Solicitud del usuario
            
        Returns:
            Código C generado
        """
        logging.info(f"🤖 Generando código para: '{user_request[:100]}...'")

        relevant_examples_content = []
        
        if self.use_embeddings:
            logging.info("🔍 Buscando ejemplos relevantes en la base de datos vectorial...")
            try:
                # 1. Obtener cliente Qdrant
                qdrant_client = get_qdrant_client()
                if not qdrant_client:
                    raise ConnectionError("No se pudo conectar a Qdrant.")

                # 2. Generar embedding para el prompt del usuario
                prompt_embedding = self.embedding_manager.get_embedding(user_request)
                if prompt_embedding is None or not isinstance(prompt_embedding, np.ndarray) or prompt_embedding.size == 0:
                     raise ValueError("No se pudo generar un embedding válido para el prompt.")
                # --- DEBUG: Log prompt embedding --- 
                logger.debug(f"Embedding del Prompt (primeros 5 dims): {prompt_embedding[:5]}")
                logger.debug(f"Norma del Embedding del Prompt: {np.linalg.norm(prompt_embedding):.4f}")
                # ----------------------------------

                # 3. Buscar en Qdrant
                search_results = search_similar(
                    client=qdrant_client,
                    platform=self.platform,
                    vector=prompt_embedding.tolist(), # Qdrant espera una lista
                    limit=self.max_examples
                )
                # --- DEBUG: Log search results --- 
                logger.debug(f"Resultados crudos de Qdrant ({len(search_results)} encontrados):")
                for i, (payload, score) in enumerate(search_results):
                    logger.debug(f"  {i+1}. Score: {score:.4f}, Path: {payload.get('file_path', 'N/A')}, Desc: '{payload.get('description', 'N/A')[:50]}...'")
                # --------------------------------

                # 4. Cargar contenido de los archivos encontrados
                if search_results:
                    logging.info(f"✅ Se encontraron {len(search_results)} ejemplos relevantes en Qdrant.")
                    examples_dir = Path(self.global_vars['example_dir_template'].format(platform=self.platform))
                    loaded_paths = set() # Para evitar cargar el mismo archivo múltiples veces si tiene varios chunks
                    
                    for payload, score in search_results:
                        relative_path_str = payload.get("file_path")
                        if relative_path_str and relative_path_str not in loaded_paths:
                            file_path = examples_dir / relative_path_str
                            if file_path.exists():
                                try:
                                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                        content = f.read()
                                        # Truncar si es necesario (usando la lógica existente si aplica)
                                        if len(content) > self.global_vars['max_example_size']:
                                            content = content[:self.global_vars['max_example_size']]
                                            logging.debug(f"Truncando ejemplo de Qdrant: {relative_path_str}")
                                            
                                        relevant_examples_content.append({
                                            'path': relative_path_str,
                                            'content': content,
                                            'score': score # Guardar score por si es útil
                                        })
                                        loaded_paths.add(relative_path_str)
                                except Exception as read_exc:
                                    logging.warning(f"⚠️ Error leyendo archivo de ejemplo {file_path} desde Qdrant: {read_exc}")
                            else:
                                logging.warning(f"⚠️ Archivo de ejemplo referenciado en Qdrant no encontrado: {file_path}")
                else:
                    logging.warning("⚠️ No se encontraron ejemplos relevantes en Qdrant.")

            except Exception as e:
                logging.error(f"❌ Error durante la búsqueda en Qdrant: {e}")
                logging.warning("⬇️ Recurriendo a la carga básica de ejemplos (sin búsqueda semántica).")
                # Fallback: Cargar ejemplos básicos si falla Qdrant
                all_examples = self.examples_loader.load_code_examples_basic()
                relevant_examples_content = all_examples[:self.max_examples]
        
        # Si no se usan embeddings o si Qdrant falló y no se cargaron ejemplos en el fallback
        if not self.use_embeddings or not relevant_examples_content:
            if not relevant_examples_content: # Asegurar que cargamos algo si Qdrant falló
                 logging.info(f"⚙️ Usando selección básica de ejemplos (sin búsqueda semántica).")
                 all_examples = self.examples_loader.load_code_examples_basic()
                 relevant_examples_content = all_examples[:self.max_examples]
        
        # Construir el prompt del sistema con los ejemplos seleccionados
        system_prompt = self._build_system_prompt(relevant_examples_content)
        user_prompt = self._build_user_prompt(user_request)

        # Log prompts for debugging (optional, consider security/privacy)
        # logging.debug(f"System Prompt:\n{system_prompt}")
        # logging.debug(f"User Prompt:\n{user_prompt}")

        try:
            logging.info(f"📞 Llamando a la API de OpenAI (Modelo: {self.model})...")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            raw_code = response.choices[0].message.content
            logging.info("✅ Llamada a la API exitosa.")
            #logging.debug(f"Raw API response:\n{raw_code}") # Log raw response if needed

            cleaned_code = clean_api_response(raw_code)
            logging.info("✨ Generación de código completada.")
            return cleaned_code

        except Exception as e:
            logging.error(f"❌ Error durante llamada a la API de OpenAI o procesamiento: {e}")
            # Consider more specific error handling for API errors (e.g., rate limits, auth)
            raise # Re-raise to indicate failure
            
    def save_generated_files(self, code: str, prompt: str) -> Dict[str, Path]:
        """Guarda el código C generado, el prompt original y la información de la plataforma.
        
        Args:
            code: Código C generado
            prompt: Prompt original del usuario
            
        Returns:
            Diccionario con las rutas de los archivos generados
        """
        logging.info("💾 Guardando archivos generados...")
        
        try:
            # Obtener las rutas de salida
            paths = get_output_paths(
                prompt, 
                self.platform, 
                self.base_output_dir, 
                self.slug_max_length
            )

            # Asegurar que los directorios base y obj existan
            paths['base'].mkdir(parents=True, exist_ok=True)
            paths['obj_dir'].mkdir(exist_ok=True) # obj_dir debe estar bajo base

            # Guardar código C
            with open(paths['c_file'], 'w', encoding='utf-8') as f:
                f.write(code)
            logging.info(f"  📄 Código C guardado en: {paths['c_file']}")

            # Guardar prompt original
            with open(paths['prompt_file'], 'w', encoding='utf-8') as f:
                f.write(prompt)
            logging.info(f"  📝 Prompt guardado en: {paths['prompt_file']}")

            # Guardar información de la plataforma
            with open(paths['platform_file'], 'w', encoding='utf-8') as f:
                f.write(self.platform)
            logging.info(f"  ℹ️ Información de plataforma guardada en: {paths['platform_file']}")

            logging.info("✅ Todos los archivos guardados correctamente!")
            logging.info(f"  📁 Directorio de Salida: {paths['base'].resolve()}")
            logging.info(f"  🛠️ Directorio de Build/Objetos: {paths['obj_dir'].resolve()}")

            return paths
        except Exception as e:
            logging.error(f"❌ Error al guardar archivos: {e}")
            raise 