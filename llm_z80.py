import os
import argparse
from openai import OpenAI
from pathlib import Path
import yaml
from dotenv import load_dotenv
import re
from datetime import datetime
import logging
from termcolor import colored
import glob
import json
import hashlib

class ConsoleFormatter(logging.Formatter):
    ICONS = {
        'INFO': '🔵',
        'ERROR': '🔴',
        'WARNING': '🟡',
        'DEBUG': '🟣'
    }
    
    COLORS = {
        'INFO': 'cyan',
        'ERROR': 'red',
        'WARNING': 'yellow',
        'DEBUG': 'magenta'
    }

    def format(self, record):
        icon = self.ICONS.get(record.levelname, '🔵')
        color = self.COLORS.get(record.levelname, 'white')
        
        if record.levelname == 'INFO':
            return colored(f"{icon} {record.getMessage()}", color)
        return colored(f"{icon} {record.levelname}: {record.getMessage()}", color)

class LLMZ80Generator:
    def __init__(self, platform="spectrum", config_path="config.yml"):
        # Configure logging
        log_dir = Path('local/logs')
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"llmz80_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        # File handler with detailed logging
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        
        # Console handler with pretty formatting
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(ConsoleFormatter())
        
        # Configure root logger
        logging.basicConfig(
            level=logging.INFO,
            handlers=[file_handler, console_handler]
        )
        
        # Set platform (spectrum or amstrad_cpc)
        self.platform = platform
        logging.info(f"Starting LLMZ80 Code Generator for {self.platform.upper().replace('_', ' ')}")
        
        load_dotenv()
        
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
                logging.info("Configuration loaded successfully")
        except Exception as e:
            logging.error(f"Error loading config: {e}")
            raise
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            logging.error("OPENAI_API_KEY not found in .env file")
            raise ValueError("OPENAI_API_KEY not found in .env file")
        
        self.client = OpenAI(api_key=api_key)
        logging.info("OpenAI API key configured")

        # Inicializar la base de conocimiento RAG
        self.knowledge_base = []
        self.vector_store = {}

    def _create_slug(self, prompt, max_length=40):
        logging.debug(f"Creating slug from prompt: {prompt[:50]}...")
        slug = prompt.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug).strip('-')
        slug = slug[:max_length]
        logging.debug(f"Created slug: {slug}")
        return slug

    def _get_output_paths(self, prompt):
        logging.info("Generating output paths")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        slug = self._create_slug(prompt)
        base_dir = Path('local') / f"{timestamp}_{slug}"
        
        paths = {
            'base': base_dir,
            'c_file': base_dir / 'main.c',
            'prompt_file': base_dir / 'prompt.txt',
            'platform': base_dir / 'platform.txt'
        }
        
        # Añadir archivos específicos de la plataforma
        if self.platform == 'spectrum':
            paths['output_file'] = base_dir / 'output.tap'
        elif self.platform == 'amstrad_cpc':
            paths['output_file'] = base_dir / 'output.dsk'
        
        logging.debug(f"Generated paths: {paths}")
        return paths
        
    def _compress_code(self, code):
        """Comprime el código fuente eliminando comentarios y optimizando espacios"""
        # Elimina comentarios y optimiza whitespace
        simplified = re.sub(r'//.*?\n|/\*.*?\*/', '', code, flags=re.DOTALL)
        simplified = re.sub(r'\n\s+', '\n', simplified)
        return simplified[:1024]  # Limite de contexto

    def _extract_metadata_from_code(self, code, file_path):
        """Extrae metadatos del código fuente y genera una estructura enriquecida"""
        metadata = {
            "category": "unknown",
            "subcategory": "general",
            "best_practices": [],
            "common_errors": [],
            "hardware_constraints": {}
        }
        
        # Inferir categoría y subcategoría basadas en el nombre del archivo y directorio
        parts = Path(file_path).parts
        if len(parts) > 2:
            # El directorio podría indicar la categoría
            potential_category = parts[-2]
            if potential_category != self.platform:
                metadata["category"] = potential_category
        
        # Buscar patrones en el código para determinar subcategorías
        if re.search(r'cpct_drawSprite|putSprite|sp_', code, re.IGNORECASE):
            metadata["category"] = "graphics"
            metadata["subcategory"] = "sprite_rendering"
        elif re.search(r'cpct_akp|play|sound|beep|SOUND', code, re.IGNORECASE):
            metadata["category"] = "audio"
            metadata["subcategory"] = "sound_effects"
        elif re.search(r'cpct_scanKey|key|INPUT|joystick', code, re.IGNORECASE):
            metadata["category"] = "input"
            metadata["subcategory"] = "keyboard_joystick"
        
        # Inferir mejores prácticas
        if self.platform == 'amstrad_cpc':
            if 'cpct_memset' in code:
                metadata["best_practices"].append("Usar cpct_memset para limpieza rápida de memoria")
            if 'cpct_etm_' in code:
                metadata["best_practices"].append("Usar cpct_etm_... para cambio de modo de entrada")
            if 'cpct_setVideoMode' in code:
                metadata["best_practices"].append("Configurar modo de video antes de dibujar")

        elif self.platform == 'spectrum':
            if 'sp_' in code:
                metadata["best_practices"].append("Usar SP_XXXX para imprimir sprites con la librería SP")
            if 'zx_' in code:
                metadata["best_practices"].append("Preferir funciones zx_* para operaciones específicas del Spectrum")
        
        # Inferir restricciones de hardware
        if self.platform == 'amstrad_cpc':
            metadata["hardware_constraints"] = {
                "vram": "0xC000-0xFFFF",
                "ram": "64K (ampliable a 128K)",
                "cpu": "Z80A @ 4MHz"
            }
        elif self.platform == 'spectrum':
            metadata["hardware_constraints"] = {
                "vram": "0x4000-0x5AFF",
                "ram": "48K (o 128K dependiendo del modelo)",
                "cpu": "Z80A @ 3.5MHz"
            }
        
        # Inferir errores comunes
        if 'sprite' in code.lower() or 'draw' in code.lower():
            metadata["common_errors"] = [
                {"error": "Corrupción de pantalla", 
                 "solution": "Respetar los límites de la pantalla y comprobar dimensiones"},
                {"error": "Parpadeo", 
                 "solution": "Implementar doble buffer o sincronizar con retrazo vertical"}
            ]
        
        return metadata

    def _create_embedding(self, text):
        """Crea un 'embedding' simple basado en hash para búsqueda (simulado)"""
        # En una implementación real, usarías un modelo de embeddings como:
        # response = self.client.embeddings.create(input=text, model="text-embedding-ada-002")
        # return response.data[0].embedding
        
        # Versión simplificada para demostración:
        hash_object = hashlib.md5(text.encode())
        hash_hex = hash_object.hexdigest()
        return hash_hex

    def _load_examples(self):
        """Carga ejemplos de código con metadatos enriquecidos para el RAG"""
        examples_dir = f"examples/{self.platform}"
        logging.info(f"📚 Cargando ejemplos de código para {self.platform.upper().replace('_', ' ')}...")
        
        self.knowledge_base = []
        self.vector_store = {}
        
        # Buscar recursivamente en todas las carpetas
        if self.platform == "amstrad_cpc":
            # Para Amstrad CPC, buscar en subdirectorios
            for root, dirs, files in os.walk(examples_dir):
                for file in files:
                    if file.endswith(".c"):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                compressed_content = self._compress_code(content)
                                
                                # Extraer metadatos y crear estructura RAG
                                metadata = self._extract_metadata_from_code(content, file_path)
                                
                                # Crear un documento RAG enriquecido
                                rag_doc = {
                                    "path": file_path,
                                    "content": compressed_content,
                                    "original_size": len(content),
                                    "category": metadata["category"],
                                    "subcategory": metadata["subcategory"],
                                    "best_practices": metadata["best_practices"],
                                    "common_errors": metadata["common_errors"],
                                    "hardware_constraints": metadata["hardware_constraints"]
                                }
                                
                                # Crear embedding para búsqueda semántica
                                embedding_key = self._create_embedding(compressed_content)
                                self.vector_store[embedding_key] = rag_doc
                                
                                self.knowledge_base.append(rag_doc)
                        except Exception as e:
                            logging.warning(f"Error al cargar ejemplo {file_path}: {e}")
        else:
            # Para otras plataformas, usar el comportamiento anterior
            for file in glob.glob(f"{examples_dir}/*.c"):
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        compressed_content = self._compress_code(content)
                        
                        # Extraer metadatos y crear estructura RAG
                        metadata = self._extract_metadata_from_code(content, file)
                        
                        # Crear un documento RAG enriquecido
                        rag_doc = {
                            "path": file,
                            "content": compressed_content,
                            "original_size": len(content),
                            "category": metadata["category"],
                            "subcategory": metadata["subcategory"],
                            "best_practices": metadata["best_practices"],
                            "common_errors": metadata["common_errors"],
                            "hardware_constraints": metadata["hardware_constraints"]
                        }
                        
                        # Crear embedding para búsqueda semántica
                        embedding_key = self._create_embedding(compressed_content)
                        self.vector_store[embedding_key] = rag_doc
                        
                        self.knowledge_base.append(rag_doc)
                except Exception as e:
                    logging.warning(f"Error al cargar ejemplo {file}: {e}")
        
        logging.info(f"✅ {len(self.knowledge_base)} ejemplos cargados y enriquecidos con metadatos")
        return self.knowledge_base

    def _find_relevant_examples(self, query, max_examples=5):
        """Busca ejemplos relevantes para la consulta del usuario usando metadatos"""
        if not self.knowledge_base:
            self._load_examples()
            
        logging.info(f"🔍 Buscando ejemplos relevantes para: {query[:50]}...")
        
        # Analizar la consulta para identificar categorías y subcategorías
        query_categories = []
        if re.search(r'sprite|dibujar|gráfico|imagen', query, re.IGNORECASE):
            query_categories.append(("graphics", "sprite_rendering"))
        if re.search(r'sonido|música|beep|audio', query, re.IGNORECASE):
            query_categories.append(("audio", "sound_effects"))
        if re.search(r'teclado|joystick|input|entrada', query, re.IGNORECASE):
            query_categories.append(("input", "keyboard_joystick"))
            
        # Puntuar ejemplos según relevancia
        scored_examples = []
        for doc in self.knowledge_base:
            score = 0
            
            # Aumentar puntuación si las categorías coinciden
            for cat, subcat in query_categories:
                if doc["category"] == cat:
                    score += 5
                if doc["subcategory"] == subcat:
                    score += 3
            
            # Puntuación por coincidencia de palabras clave
            for keyword in re.findall(r'\w+', query.lower()):
                if keyword in doc["content"].lower():
                    score += 1
            
            scored_examples.append((doc, score))
        
        # Ordenar por puntuación
        scored_examples.sort(key=lambda x: x[1], reverse=True)
        
        # Tomar los mejores ejemplos
        best_examples = [doc for doc, score in scored_examples[:max_examples]]
        
        logging.info(f"✅ Encontrados {len(best_examples)} ejemplos relevantes")
        return best_examples

    def read_system_prompt(self):
        """Lee el archivo de recomendaciones adicionales para el system prompt"""
        content = ""
        
        # Intentar leer archivo específico de la plataforma primero
        platform_file = f'system_prompt_{self.platform}.txt'
        try:
            if os.path.exists(platform_file):
                with open(platform_file, 'r', encoding='utf-8') as f:
                    content = "\n" + f.read()
                logging.info(f"✅ Archivo de prompt específico cargado: {platform_file}")
        except FileNotFoundError:
            logging.warning(f"⚠️ No se encontró {platform_file}")
        except Exception as e:
            logging.error(f"❌ Error leyendo archivo de prompt: {e}")
        
        # Cargar documentación de errores desde archivos .md
        error_docs = self._load_error_documentation()
        if error_docs:
            content += "\n\n" + error_docs
            
        return content
        
    def _load_error_documentation(self):
        """Carga la documentación de errores desde archivos .md"""
        logging.info(f"📚 Cargando documentación de errores para {self.platform.upper().replace('_', ' ')}...")
        
        docs_content = ""
        examples_dir = Path(f'examples/{self.platform}')
        
        if not examples_dir.exists():
            logging.warning(f"Directorio de ejemplos para {self.platform} no encontrado")
            return docs_content
            
        # Buscar archivos .md en el directorio de ejemplos
        md_files = list(examples_dir.glob('**/*.md'))
        
        if not md_files:
            logging.info("No se encontraron archivos de documentación .md")
            return docs_content
            
        logging.info(f"Encontrados {len(md_files)} archivos de documentación")
        
        # Leer y concatenar el contenido de los archivos .md
        for md_file in md_files:
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                    docs_content += f"\n\n--- DOCUMENTACIÓN DE ERRORES: {md_file.name} ---\n\n"
                    docs_content += file_content
                logging.info(f"✅ Documentación cargada: {md_file.relative_to(examples_dir)}")
            except Exception as e:
                logging.error(f"❌ Error al cargar documentación {md_file}: {e}")
                
        return docs_content

    def visualize_knowledge_base(self, include_content=False):
        """Visualiza la estructura de la base de conocimiento RAG"""
        if not self.knowledge_base:
            self._load_examples()
            
        print(colored("\n📊 ESTRUCTURA DE LA BASE DE CONOCIMIENTO RAG 📊", "green", attrs=['bold']))
        print(colored("=" * 70, "green"))
        
        # Agrupar ejemplos por categoría y subcategoría
        categories = {}
        for doc in self.knowledge_base:
            cat = doc["category"]
            subcat = doc["subcategory"]
            
            if cat not in categories:
                categories[cat] = {}
            
            if subcat not in categories[cat]:
                categories[cat][subcat] = []
                
            categories[cat][subcat].append(doc)
        
        # Mostrar estadísticas generales
        print(colored(f"Total de ejemplos: {len(self.knowledge_base)}", "cyan"))
        print(colored(f"Categorías: {len(categories)}", "cyan"))
        print(colored("=" * 70, "green"))
        
        # Mostrar ejemplos por categoría
        for cat, subcats in categories.items():
            print(colored(f"\n🔹 CATEGORÍA: {cat.upper()}", "yellow", attrs=['bold']))
            
            for subcat, docs in subcats.items():
                print(colored(f"  ┣━ Subcategoría: {subcat} ({len(docs)} ejemplos)", "yellow"))
                
                for i, doc in enumerate(docs):
                    print(colored(f"  ┃  ┣━ {i+1}. {Path(doc['path']).name}", "cyan"))
                    
                    # Mostrar mejores prácticas
                    if doc["best_practices"]:
                        print(colored(f"  ┃  ┃  ┣━ Mejores prácticas: {len(doc['best_practices'])}", "white"))
                        if include_content:
                            for bp in doc["best_practices"]:
                                print(colored(f"  ┃  ┃  ┃  ┣━ {bp}", "white"))
                    
                    # Mostrar errores comunes
                    if doc["common_errors"]:
                        print(colored(f"  ┃  ┃  ┣━ Errores comunes: {len(doc['common_errors'])}", "white"))
                        if include_content:
                            for err in doc["common_errors"]:
                                print(colored(f"  ┃  ┃  ┃  ┣━ {err['error']}: {err['solution']}", "white"))
                    
                    # Mostrar restricciones hardware
                    if doc["hardware_constraints"]:
                        print(colored(f"  ┃  ┃  ┣━ Restricciones hardware: {len(doc['hardware_constraints'])}", "white"))
                    
                    # Mostrar contenido del código comprimido (opcional)
                    if include_content:
                        content_preview = doc["content"][:100].replace("\n", "\\n") + "..."
                        print(colored(f"  ┃  ┃  ┣━ Contenido: {content_preview}", "white"))
                    
                    print(colored(f"  ┃  ┃", "cyan"))
        
        return categories
        
    def visualize_example_selection(self, query, max_examples=5):
        """Visualiza el proceso de selección de ejemplos para una consulta"""
        print(colored(f"\n🔍 SELECCIÓN DE EJEMPLOS PARA: '{query[:50]}...'", "green", attrs=['bold']))
        print(colored("=" * 70, "green"))
        
        # Buscar ejemplos relevantes
        relevant_examples = self._find_relevant_examples(query, max_examples)
        
        # Mostrar categorías detectadas
        print(colored("Categorías detectadas en la consulta:", "yellow"))
        query_categories = []
        if re.search(r'sprite|dibujar|gráfico|imagen', query, re.IGNORECASE):
            query_categories.append(("graphics", "sprite_rendering"))
            print(colored("  ┣━ Gráficos / Renderizado de sprites", "cyan"))
        if re.search(r'sonido|música|beep|audio', query, re.IGNORECASE):
            query_categories.append(("audio", "sound_effects"))
            print(colored("  ┣━ Audio / Efectos de sonido", "cyan"))
        if re.search(r'teclado|joystick|input|entrada', query, re.IGNORECASE):
            query_categories.append(("input", "keyboard_joystick"))
            print(colored("  ┣━ Entrada / Teclado y joystick", "cyan"))
        
        if not query_categories:
            print(colored("  ┣━ No se detectaron categorías específicas", "cyan"))
        
        print(colored("\nEjemplos seleccionados:", "yellow"))
        for i, example in enumerate(relevant_examples):
            print(colored(f"  ┣━ Ejemplo {i+1}: {Path(example['path']).name}", "cyan"))
            print(colored(f"  ┃  ┣━ Categoría: {example['category']}/{example['subcategory']}", "white"))
            print(colored(f"  ┃  ┣━ Mejores prácticas: {len(example['best_practices'])}", "white"))
            print(colored(f"  ┃  ┣━ Errores comunes: {len(example['common_errors'])}", "white"))
            print(colored(f"  ┃  ┣━ Tamaño original: {example['original_size']} bytes", "white"))
            print(colored(f"  ┃  ┣━ Tamaño comprimido: {len(example['content'])} bytes", "white"))
            print(colored(f"  ┃  ┃", "cyan"))
        
        return relevant_examples
        
    def preview_system_prompt(self, query):
        """Muestra una vista previa estructurada del prompt del sistema"""
        print(colored("\n📝 VISTA PREVIA DEL PROMPT DEL SISTEMA", "green", attrs=['bold']))
        print(colored("=" * 70, "green"))
        
        # Buscar ejemplos relevantes
        relevant_examples = self._find_relevant_examples(query)
        
        # Contar tokens aproximados
        base_prompt_tokens = 100  # Estimación de tokens para la introducción
        example_tokens = 0
        metadata_tokens = 0
        
        for example in relevant_examples:
            # Estimar tokens para código (aproximado: cada 4 caracteres = 1 token)
            example_tokens += len(example['content']) // 4
            
            # Estimar tokens para metadatos
            metadata_tokens += 10  # Base para encabezados
            metadata_tokens += len(example['best_practices']) * 5
            metadata_tokens += len(example['common_errors']) * 10
            metadata_tokens += len(example['hardware_constraints']) * 5
        
        # Leer instrucciones adicionales
        additional_instructions = self.read_system_prompt()
        additional_tokens = len(additional_instructions) // 4
        
        # Mostrar estructura
        print(colored("Estructura del prompt:", "yellow"))
        print(colored(f"  ┣━ Introducción del modelo para {self.platform.upper().replace('_', ' ')}", "cyan"))
        print(colored(f"  ┣━ Ejemplos relevantes: {len(relevant_examples)}", "cyan"))
        
        for i, example in enumerate(relevant_examples):
            print(colored(f"  ┃  ┣━ Ejemplo {i+1}: {Path(example['path']).name}", "white"))
            
        print(colored(f"  ┣━ Instrucciones de generación para {self.platform.upper().replace('_', ' ')}", "cyan"))
        print(colored(f"  ┣━ Instrucciones adicionales específicas de la plataforma", "cyan"))
        
        # Mostrar estadísticas de tokens
        total_tokens = base_prompt_tokens + example_tokens + metadata_tokens + additional_tokens
        print(colored("\nEstadísticas de tokens (aproximadas):", "yellow"))
        print(colored(f"  ┣━ Tokens base: {base_prompt_tokens}", "white"))
        print(colored(f"  ┣━ Tokens de ejemplos de código: {example_tokens}", "white"))
        print(colored(f"  ┣━ Tokens de metadatos: {metadata_tokens}", "white"))
        print(colored(f"  ┣━ Tokens de instrucciones adicionales: {additional_tokens}", "white"))
        print(colored(f"  ┣━ TOTAL DE TOKENS: {total_tokens}", "cyan", attrs=['bold']))
        
        # Advertencia de límite de tokens si es necesario
        if total_tokens > 4000:
            print(colored("\n⚠️ ADVERTENCIA: El prompt se acerca al límite de tokens", "red", attrs=['bold']))
            print(colored("  Se recomienda reducir el número de ejemplos o la cantidad de instrucciones adicionales.", "red"))
        
        return total_tokens

    def generate_c_code(self, prompt):
        logging.info(f"🤖 Generando código Z80 para {self.platform.upper().replace('_', ' ')} basado en ejemplos existentes...")
        
        # Buscar ejemplos relevantes para el prompt del usuario
        relevant_examples = self._find_relevant_examples(prompt)
        
        # Crear el prompt del sistema con los ejemplos relevantes
        if self.platform == 'spectrum':
            system_prompt = """You are a Z88DK C code generator for ZX Spectrum 48K.
CRITICAL: Output ONLY the source code itself. No introduction, no explanation, no markdown blocks.
"""
        elif self.platform == 'amstrad_cpc':
            system_prompt = """You are a CPCtelera C code generator for Amstrad CPC 464.
CRITICAL: Output ONLY the source code itself. No introduction, no explanation, no markdown blocks.
"""
        
        system_prompt += "\nHere are some example programs to guide your generation:\n"
        
        # Agregar ejemplos relevantes al prompt del sistema
        for i, example in enumerate(relevant_examples):
            system_prompt += f"\nExample {i+1} '{example['path']}' (Category: {example['category']}/{example['subcategory']}):\n"
            system_prompt += f"Code:\n{example['content']}\n"
            
            # Añadir metadatos relevantes
            if example['best_practices']:
                system_prompt += "Best Practices:\n"
                for practice in example['best_practices']:
                    system_prompt += f"- {practice}\n"
                    
            if example['common_errors']:
                system_prompt += "Common Errors to Avoid:\n"
                for error in example['common_errors']:
                    system_prompt += f"- {error['error']}: {error['solution']}\n"
            
            if example['hardware_constraints']:
                system_prompt += "Hardware Constraints:\n"
                for key, value in example['hardware_constraints'].items():
                    system_prompt += f"- {key}: {value}\n"
        
        # Leer instrucciones adicionales del system prompt
        additional_instructions = self.read_system_prompt()
        
        if self.platform == 'spectrum':
            system_prompt += """
Based on these examples, generate a new program following these rules:
- Use similar structure and style to the examples
- Include appropriate headers based on functionality needed
- Follow ZX Spectrum and Z88DK best practices
- Output ONLY the code, no explanations
- No markdown blocks
- Must compile with zcc +zx
"""
        elif self.platform == 'amstrad_cpc':
            system_prompt += """
Based on these examples, generate a new program following these rules:
- Use similar structure and style to the examples
- Include appropriate headers based on functionality needed
- Follow Amstrad CPC and CPCtelera best practices
- Output ONLY the code, no explanations
- No markdown blocks
- Must compile with CPCtelera
"""
        
        # Añadir instrucciones adicionales del archivo system_prompt
        system_prompt += additional_instructions
        
        # Crear un prompt de usuario enriquecido que incorpore el contexto
        user_prompt = f"Write {self.platform.replace('_', ' ')} C code that: {prompt}\n\nYour code should follow all the instructions and examples provided in the system prompt. Remember to output ONLY the code without any markdown or explanations."
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=4096
            )
            
            # Clean any possible markdown or extra text
            code = response.choices[0].message.content.strip()
            if code.startswith("```"):
                code = "\n".join(code.split("\n")[1:-1])
            code = code.replace("```c", "").replace("```", "").strip()
            
            logging.info("✨ Código generado exitosamente!")
            return code
        except Exception as e:
            logging.error(f"Error al generar código: {e}")
            raise
    
    def save_c_code(self, code, prompt, paths):
        logging.info("💾 Saving files...")
        try:
            os.makedirs(paths['base'], exist_ok=True)
            
            with open(paths['c_file'], 'w') as f:
                f.write(code)
            logging.info(f"C code saved to {paths['c_file']}")
            
            with open(paths['prompt_file'], 'w') as f:
                f.write(prompt)
            logging.info(f"Prompt saved to {paths['prompt_file']}")
            
            with open(paths['platform'], 'w') as f:
                f.write(self.platform)
            logging.info(f"Platform info saved to {paths['platform']}")
            
            logging.info("✅ All files saved successfully!")
            
        except Exception as e:
            logging.error(f"Failed to save files: {e}")
            raise

def main():
    # Configurar argumentos de línea de comandos
    parser = argparse.ArgumentParser(description='LLMZ80 Code Generator')
    parser.add_argument('--platform', type=str, default='spectrum', 
                        choices=['spectrum', 'amstrad_cpc'],
                        help='Target platform (spectrum or amstrad_cpc)')
    parser.add_argument('--prompt', type=str,
                        help='Prompt for code generation (optional)')
    parser.add_argument('--visualize', action='store_true',
                        help='Visualize RAG structure and example selection')
    parser.add_argument('--full-kb', action='store_true',
                        help='Show full knowledge base details including content')
    args = parser.parse_args()
    
    platform_name = args.platform.upper().replace('_', ' ')
    
    print(colored(f"\n🎮 {platform_name} Code Generator 🎮", "green", attrs=['bold']))
    print(colored("=" * 40, "green"))
    
    try:
        generator = LLMZ80Generator(platform=args.platform)
        
        # Si se solicita visualización, mostrar estructura RAG
        if args.visualize:
            generator.visualize_knowledge_base(include_content=args.full_kb)
        
        # Use provided prompt or request one interactively
        prompt = args.prompt
        if not prompt:
            prompt = input(colored("\n📝 Enter your prompt: ", "yellow"))
        
        # Si se solicita visualización, mostrar selección de ejemplos y vista previa del prompt
        if args.visualize:
            generator.visualize_example_selection(prompt)
            generator.preview_system_prompt(prompt)
            
            # Preguntar si quiere continuar con la generación
            continue_gen = input(colored("\n¿Continuar con la generación? (s/n): ", "yellow"))
            if continue_gen.lower() != 's':
                print(colored("Generación cancelada.", "red"))
                return
            
        logging.info("Starting code generation process")
        
        paths = generator._get_output_paths(prompt)
        c_code = generator.generate_c_code(prompt)
        generator.save_c_code(c_code, prompt, paths)
        
        print(colored("\n✨ Success! ✨", "green", attrs=['bold']))
        print(colored(f"📂 Files saved in: {paths['base']}", "cyan"))
        print(colored(f"📄 C code: {paths['c_file']}", "cyan"))
        
        if args.platform == 'spectrum':
            print(colored("\n🚀 Continuing 'build.sh' to compile and run the program", "yellow"))
        elif args.platform == 'amstrad_cpc':
            print(colored("\n🚀 Continuing 'build_amstrad.sh' to compile and run the program", "yellow"))
        
    except Exception as e:
        logging.error(f"Process failed: {e}")
        raise

if __name__ == "__main__":
    main()
