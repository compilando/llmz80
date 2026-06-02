import logging
import os
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from openai import OpenAI
import numpy as np
from numpy.linalg import norm

# Obtener instancia del logger para este módulo
logger = logging.getLogger(__name__)

MAX_PROMPT_EXAMPLE_CHARS = 8000
MAX_PROMPT_EXAMPLES_CHARS = 60000

from ..core.embeddings import EmbeddingsManager
from ..core.cache_manager import EmbeddingsCacheManager
from ..core.examples_loader import ExamplesLoader
from ..core.code_context import build_example_context, is_self_contained_c_context
from ..utils.helpers import clean_api_response, get_output_paths, build_completion_kwargs, is_reasoning_model
from vector_db import get_qdrant_client, search_similar, ensure_collection_exists, upsert_embeddings, PointStruct
import uuid as _uuid
from datetime import datetime as _datetime

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
        self.reasoning_effort = global_vars.get('reasoning_effort')
        self.is_reasoning = is_reasoning_model(self.model)

        # Optional learning system - injected by main, used to seed prompt with
        # recurring-error guidance. None when learning is disabled / unavailable.
        self.learning_system = None
        self.max_examples = global_vars['max_examples']
        self.system_prompt_file = global_vars['system_prompt_file']
        self.base_output_dir = global_vars['base_output_dir']
        self.slug_max_length = global_vars['slug_max_length']
        
        # Opciones para la búsqueda semántica
        self.use_embeddings = True
        self.force_truncate = False
        
        # Configuración para correcciones automáticas
        self.max_correction_attempts = 3
        
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
            
            # Generar embedding con el método estándar
            logging.info("🔄 Generando embedding para el archivo...")
            try:
                start_time = time.time()
                embedding = self.embedding_manager.get_embedding(content)
                elapsed = time.time() - start_time
                
                if isinstance(embedding, np.ndarray) and embedding.size > 0 and not np.all(embedding == 0):
                    logging.info(f"✅ Embedding generado correctamente en {elapsed:.2f} segundos")
                    logging.info(f"   Dimensiones: {embedding.shape}, Norma: {norm(embedding):.4f}")
                else:
                    logging.warning(f"⚠️ No se pudo generar un embedding válido")
            except Exception as e:
                logging.error(f"❌ Error al generar embedding: {e}")
                
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

        # 1. Cargar Instrucciones Específicas de la Plataforma desde Archivo
        platform_instructions = self._load_platform_instructions()
        
        # Si no hay archivo de instrucciones, usar prompt base mínimo
        if not platform_instructions:
            if self.platform == 'spectrum':
                platform_instructions = """You are an expert Z88DK C code generator for ZX Spectrum 48K.
CRITICAL: Output ONLY the raw C source code. No introductory text, no explanations, no markdown fences (```), just the code itself.
Use #include <arch/zx.h> for ZX Spectrum functions. Use printf() for text output.
Ensure the code compiles with 'zcc +zx -vn -O3 -clib=sdcc_iy'."""
            elif self.platform == 'amstrad_cpc':
                platform_instructions = """You are an expert CPCtelera C code generator for Amstrad CPC.
CRITICAL: Output ONLY the raw C source code. No introductory text, no explanations, no markdown fences (```), just the code itself.
Use #include <cpctelera.h> and CPCtelera API functions only.
Ensure the code compiles with the CPCtelera toolchain."""

        # 2. Ejemplos de Código
        examples_prompt_part = "\n\n--- CODE EXAMPLES ---\n"
        examples_prompt_part += "Study these examples carefully - they show the EXACT syntax and functions you must use:\n"
        
        # Usar los ejemplos relevantes proporcionados o cargar todos si no se proporcionan
        if relevant_examples is None:
            # Cargar ejemplos básicos si no se usan embeddings
            if self.use_embeddings:
                examples_to_use: List[Dict[str, Any]] = self.examples_loader.load_code_examples()[:self.max_examples]
            else:
                examples_to_use: List[Dict[str, Any]] = self.examples_loader.load_code_examples_basic()[:self.max_examples]
        else:
            examples_to_use: List[Dict[str, Any]] = relevant_examples

        examples_to_use = self._fit_examples_for_prompt(examples_to_use)
        examples_to_use = self._filter_examples_for_output_contract(examples_to_use)

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
        
        # 3. Documentación de Errores
        error_docs = self._load_error_documentation()

        # 4. Combinar todas las partes
        full_system_prompt = platform_instructions

        # Inject recurring-error guidance from learning system (if wired)
        if self.learning_system is not None:
            try:
                avoid_block = self.learning_system.build_avoid_block(limit=5)
                if avoid_block:
                    full_system_prompt += "\n" + avoid_block
                    logging.info(f"📚 Inyectados {avoid_block.count('ERROR (')} errores recurrentes en system prompt")
            except Exception as e:
                logging.warning(f"No se pudo inyectar errores recurrentes: {e}")

        if examples_to_use:
            full_system_prompt += examples_prompt_part

        if error_docs:
            full_system_prompt += error_docs
        
        # Final reminder
        full_system_prompt += "\n\n--- CRITICAL REMINDER ---\n"
        full_system_prompt += "Output ONLY raw C code. No markdown, no explanations, no extra text.\n"
        full_system_prompt += "First line must be #include or a comment. Code must compile successfully."
        full_system_prompt += "\nGenerate a self-contained main.c. Do not add #include \"local_file.h\"."
        full_system_prompt += "\nEmbed all required sprites, tables, palettes, and data directly in main.c."
        full_system_prompt += "\nExamples may show SUPPORT FILE and BUILD FILE sections; use them to learn valid APIs, data shapes, and compiler constraints, but do not require missing project files in your output."

        logging.debug(f"Prompt del sistema construido ({len(full_system_prompt)} caracteres).")
        return full_system_prompt

    def _filter_examples_for_output_contract(self, examples: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prefer examples compatible with the current single-file output contract."""
        if self.platform != "amstrad_cpc":
            return examples

        self_contained = [
            example for example in examples
            if is_self_contained_c_context(example.get("content", ""))
        ]
        if not self_contained:
            logging.warning(
                "No hay ejemplos autocontenidos para el contrato main.c; "
                "se usarán ejemplos originales como fallback"
            )
            return examples

        if len(self_contained) < len(examples):
            logging.info(
                "Filtrando ejemplos RAG por contrato main.c autocontenido: "
                f"{len(examples)} -> {len(self_contained)}"
            )
        return self_contained

    def _fit_examples_for_prompt(self, examples: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Keep retrieved examples useful without overflowing the model context."""
        fitted_examples = []
        used_chars = 0

        for example in examples:
            if used_chars >= MAX_PROMPT_EXAMPLES_CHARS:
                break

            content = example.get("content", "")
            remaining = MAX_PROMPT_EXAMPLES_CHARS - used_chars
            max_chars = min(MAX_PROMPT_EXAMPLE_CHARS, remaining)
            if len(content) > max_chars:
                head_size = int(max_chars * 0.7)
                tail_size = max_chars - head_size
                content = (
                    content[:head_size]
                    + "\n/* ... example truncated for prompt budget ... */\n"
                    + content[-tail_size:]
                )

            fitted_example = dict(example)
            fitted_example["content"] = content
            fitted_examples.append(fitted_example)
            used_chars += len(content)

        if len(fitted_examples) < len(examples):
            logging.info(
                "Recortando ejemplos del prompt por presupuesto de contexto: "
                f"{len(examples)} -> {len(fitted_examples)}"
            )

        return fitted_examples
        
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
                if not ensure_collection_exists(qdrant_client, self.platform):
                    raise ConnectionError(f"No se pudo inicializar colección Qdrant para {self.platform}.")

                # 2. Generar embedding para el prompt del usuario
                prompt_embedding = self.embedding_manager.get_embedding(user_request)
                if prompt_embedding is None or not isinstance(prompt_embedding, np.ndarray) or prompt_embedding.size == 0:
                     raise ValueError("No se pudo generar un embedding válido para el prompt.")
                # --- DEBUG: Log prompt embedding --- 
                logger.debug(f"Embedding del Prompt (primeros 5 dims): {prompt_embedding[:5]}")
                logger.debug(f"Norma del Embedding del Prompt: {np.linalg.norm(prompt_embedding):.4f}")
                # ----------------------------------

                # 3. Buscar en Qdrant (sobre-recuperar para rerank por éxito)
                overfetch = max(self.max_examples * 2, self.max_examples + 5)
                raw_results = search_similar(
                    client=qdrant_client,
                    platform=self.platform,
                    vector=prompt_embedding.tolist(),
                    limit=overfetch,
                )

                # Rerank: boost ejemplos APRENDIDOS que compilaron en pocos intentos.
                # Score ajustado = score * (1 + bonus). Curados quedan neutros.
                def _adjusted(payload, score):
                    bonus = 0.0
                    if payload.get('source') == 'learned':
                        attempts = int(payload.get('compilation_attempts', 1) or 1)
                        # +15% si first-try, decae con cada intento extra
                        bonus = max(0.0, 0.15 / attempts)
                    return score * (1.0 + bonus)

                search_results = sorted(
                    raw_results,
                    key=lambda r: _adjusted(r[0], r[1]),
                    reverse=True,
                )[: self.max_examples]
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
                            source_code_payload = payload.get("source_code")
                            if (
                                source_code_payload
                                and "// FILE:" in source_code_payload
                            ):
                                relevant_examples_content.append({
                                    'path': relative_path_str,
                                    'content': source_code_payload,
                                    'description': payload.get('description', ''),
                                    'score': score
                                })
                                loaded_paths.add(relative_path_str)
                            elif file_path.exists():
                                try:
                                    content = build_example_context(
                                        file_path,
                                        examples_dir,
                                        self.global_vars['max_example_size'],
                                    )
                                    if len(content) > self.global_vars['max_example_size']:
                                        content = content[:self.global_vars['max_example_size']]
                                        logging.debug(f"Truncando ejemplo de Qdrant: {relative_path_str}")
                                            
                                    relevant_examples_content.append({
                                        'path': relative_path_str,
                                        'content': content,
                                        'description': payload.get('description', ''),
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
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                **build_completion_kwargs(
                    self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    reasoning_effort=self.reasoning_effort,
                ),
            )

            raw_code = response.choices[0].message.content
            logging.info("✅ Llamada a la API exitosa.")
            
            if raw_code is None:
                raise ValueError("La API no devolvió contenido.")
            
            cleaned_code = clean_api_response(raw_code)
            logging.info("✨ Generación de código completada.")
            return cleaned_code

        except Exception as e:
            logging.error(f"❌ Error durante llamada a la API de OpenAI o procesamiento: {e}")
            # Consider more specific error handling for API errors (e.g., rate limits, auth)
            raise # Re-raise to indicate failure
    
    def suggest_code_correction(
        self,
        failed_code: str,
        error_output: str,
        platform: str,
        user_request: Optional[str] = None,
        prior_attempts: Optional[List[Dict[str, str]]] = None,
    ) -> Optional[str]:
        """Solicita al LLM una corrección del código basándose en los errores de compilación.

        Args:
            failed_code: Código C que falló la compilación
            error_output: Salida de error del compilador (filtrada)
            platform: Plataforma objetivo (spectrum, amstrad_cpc)
            user_request: Prompt original del usuario (mantiene intención)
            prior_attempts: Lista de intentos previos [{'code': ..., 'error_summary': ...}]
                            para que el LLM no repita correcciones que ya fallaron.

        Returns:
            Código C corregido o None si no se pudo generar
        """
        logging.info("🤖 Solicitando sugerencia de corrección al LLM...")

        try:
            # Construir prompt especializado para corrección
            correction_system_prompt = self._build_correction_system_prompt()
            correction_user_prompt = self._build_correction_user_prompt(
                failed_code, error_output, user_request=user_request, prior_attempts=prior_attempts
            )
            
            # Llamar a la API con temperatura más baja para correcciones más precisas
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": correction_system_prompt},
                    {"role": "user", "content": correction_user_prompt}
                ],
                **build_completion_kwargs(
                    self.model,
                    max_tokens=self.max_tokens,
                    temperature=0.2,
                    reasoning_effort=self.reasoning_effort,
                ),
            )
            
            raw_corrected_code = response.choices[0].message.content
            
            if raw_corrected_code is None:
                raise ValueError("La API no devolvió contenido para la corrección.")
            
            corrected_code = clean_api_response(raw_corrected_code)
            
            logging.info("✅ Sugerencia de corrección generada exitosamente.")
            return corrected_code
            
        except Exception as e:
            logging.error(f"❌ Error al generar sugerencia de corrección: {e}")
            return None
    
    def _build_correction_system_prompt(self) -> str:
        """Construye el prompt del sistema para correcciones de código.
        
        Returns:
            Prompt del sistema especializado para correcciones
        """
        # Load the full platform instructions for context
        platform_instructions = self._load_platform_instructions()
        
        if self.platform == 'spectrum':
            correction_prompt = """You are an expert C debugger and code corrector for ZX Spectrum 48K using Z88DK.
Your task is to analyze compilation errors and fix the code.

CRITICAL RULES:
1. Output ONLY the corrected C source code - no explanations, no markdown fences (```), no extra text
2. Fix ALL compilation errors shown in the error output
3. Maintain the original functionality and intent of the code
4. Use ONLY Z88DK library functions appropriate for ZX Spectrum
5. Ensure the corrected code will compile successfully with 'zcc +zx'
6. Keep the code structure and style consistent

MOST COMMON FIXES NEEDED:
- Use #include <arch/zx.h> NOT #include <spectrum.h>
- Use #include <stdio.h> for printf()
- Use #include <input.h> for keyboard functions
- Use #include <sound.h> for sound functions
- DO NOT invent functions - use only documented Z88DK functions
- Check function signatures match Z88DK documentation

"""
            if platform_instructions:
                correction_prompt += "\n--- REFERENCE DOCUMENTATION ---\n" + platform_instructions
            if self.learning_system is not None:
                try:
                    avoid_block = self.learning_system.build_avoid_block(limit=5)
                    if avoid_block:
                        correction_prompt += "\n" + avoid_block
                except Exception:
                    pass
            return correction_prompt
        elif self.platform == 'amstrad_cpc':
            correction_prompt = """You are an expert C debugger and code corrector for Amstrad CPC using CPCtelera.
Your task is to analyze compilation errors and fix the code.

CRITICAL RULES:
1. Output ONLY the corrected C source code - no explanations, no markdown fences (```), no extra text
2. Fix ALL compilation errors shown in the error output
3. Maintain the original functionality and intent of the code
4. Use ONLY CPCtelera API functions - DO NOT use generic Z88DK functions
5. Ensure the corrected code will compile successfully with SDCC + CPCtelera
6. Return one self-contained main.c file; do not introduce local includes, assets, headers, or extra source files
7. Keep the code structure and style consistent

MOST COMMON FIXES NEEDED:
- Use #include <cpctelera.h>
- DO NOT use zx_* functions - use cpct_* equivalents
- Add cpct_disableFirmware() at start of main()
- Use cpct_setVideoMode() before graphics operations
- Call cpct_scanKeyboard() or cpct_scanKeyboard_f() before cpct_isKeyPressed()
- DO NOT invent functions - use only documented CPCtelera functions
- Check function signatures match CPCtelera documentation
- Embed sprites/tables/palettes directly in main.c; no #include "sprites.h"

"""
            if platform_instructions:
                correction_prompt += "\n--- REFERENCE DOCUMENTATION ---\n" + platform_instructions
            if self.learning_system is not None:
                try:
                    avoid_block = self.learning_system.build_avoid_block(limit=5)
                    if avoid_block:
                        correction_prompt += "\n" + avoid_block
                except Exception:
                    pass
            return correction_prompt
        else:
            raise ValueError(f"Platform not supported: {self.platform}")
    
    def _build_correction_user_prompt(
        self,
        failed_code: str,
        error_output: str,
        user_request: Optional[str] = None,
        prior_attempts: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        """Construye el prompt del usuario para corrección de código.

        Args:
            failed_code: Código que falló
            error_output: Salida de error del compilador
            user_request: Prompt original del usuario (preserva intención)
            prior_attempts: Intentos previos fallidos (code+error_summary) para
                            evitar repetir las mismas correcciones.

        Returns:
            Prompt del usuario con código, errores, intención y memoria.
        """
        parts = []

        if user_request:
            parts.append(f"=== ORIGINAL USER REQUEST ===\n{user_request}\n")
            parts.append(
                "Preserve this intent while fixing the code. Do not strip features the user asked for.\n"
            )

        if prior_attempts:
            parts.append("=== PRIOR FAILED CORRECTIONS (do not repeat these mistakes) ===")
            for i, att in enumerate(prior_attempts, 1):
                summary = att.get("error_summary", "")[:300]
                parts.append(f"Attempt {i} failed with: {summary}")
            parts.append("")

        parts.append("=== CURRENT COMPILATION ERRORS ===")
        parts.append(error_output)
        parts.append("")
        parts.append("=== CURRENT CODE ===")
        parts.append("```c")
        parts.append(failed_code)
        parts.append("```")
        parts.append("")
        parts.append(
            "Provide the CORRECTED code that fixes ALL listed compilation errors. "
            "If a prior attempt already tried a fix that failed, choose a different approach. "
            "Output ONLY the corrected C source code, no markdown fences, no commentary."
        )
        return "\n".join(parts)
            
    def index_successful_generation(
        self,
        user_prompt: str,
        code: str,
        compilation_attempts: int = 1,
    ) -> bool:
        """Index a successfully-compiled generation into Qdrant for future RAG.

        Tagged with `source=learned` and `compilation_attempts` so retrieval
        can later rerank in favour of first-try successes.
        """
        try:
            client = get_qdrant_client()
            if not client:
                logging.warning("Qdrant no disponible: ejemplo exitoso no indexado")
                return False
            if not ensure_collection_exists(client, self.platform):
                return False

            # Embedding del par prompt+code para que recuperaciones futuras
            # con prompts similares hagan match.
            embed_text = f"PROMPT: {user_prompt}\n\nCODE:\n{code}"
            embedding = self.embedding_manager.get_embedding(embed_text)
            if embedding is None or embedding.size == 0:
                logging.warning("No se obtuvo embedding para el ejemplo aprendido")
                return False

            point = PointStruct(
                id=str(_uuid.uuid4()),
                vector=embedding.tolist(),
                payload={
                    "file_path": f"learned/{_datetime.now().strftime('%Y%m%d_%H%M%S')}.c",
                    "description": user_prompt[:200],
                    "source_code": code,
                    "source": "learned",
                    "compilation_attempts": int(compilation_attempts),
                    "timestamp": _datetime.now().isoformat(),
                },
            )
            ok = upsert_embeddings(client, self.platform, [point])
            if ok:
                logging.info(
                    f"📥 Ejemplo aprendido indexado en Qdrant (attempts={compilation_attempts})"
                )
            return bool(ok)
        except Exception as e:
            logging.warning(f"No se pudo indexar ejemplo aprendido en Qdrant: {e}")
            return False

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
