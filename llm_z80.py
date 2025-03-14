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
    def __init__(self, platform="zx_spectrum", config_path="config.yml"):
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
        
        # Set platform (zx_spectrum or amstrad_cpc)
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
        if self.platform == 'zx_spectrum':
            paths['output_file'] = base_dir / 'output.tap'
        elif self.platform == 'amstrad_cpc':
            paths['output_file'] = base_dir / 'output.dsk'
        
        logging.debug(f"Generated paths: {paths}")
        return paths
        
    def _load_examples(self):
        """Carga y procesa los ejemplos existentes."""
        logging.info(f"📚 Cargando ejemplos de código para {self.platform.upper().replace('_', ' ')}...")
        examples_dir = Path(f'examples/{self.platform}')
        examples = []
        
        if not examples_dir.exists():
            logging.warning(f"Directorio de ejemplos para {self.platform} no encontrado")
            return examples
        
        # Función recursiva para buscar archivos .c en todas las subcarpetas
        def process_directory(directory):
            local_examples = []
            # Procesar archivos .c en el directorio actual
            for file in directory.glob('*.c'):
                try:
                    with open(file, 'r') as f:
                        content = f.read()
                        # Extraer el comentario de descripción
                        description = ""
                        if '/*' in content and '*/' in content:
                            description = content.split('/*')[1].split('*/')[0].strip()
                        local_examples.append({
                            'file': str(file.relative_to(examples_dir)),
                            'content': content,
                            'description': description
                        })
                    logging.debug(f"Ejemplo cargado: {file.relative_to(examples_dir)}")
                except Exception as e:
                    logging.error(f"Error al cargar ejemplo {file}: {e}")
            
            # Procesar subdirectorios
            for subdir in directory.glob('*/'):
                if subdir.is_dir() and not subdir.name.startswith('.'):
                    # Si es un directorio src, buscar archivos .c directamente
                    if subdir.name == 'src':
                        for file in subdir.glob('*.c'):
                            try:
                                with open(file, 'r') as f:
                                    content = f.read()
                                    # Extraer el comentario de descripción
                                    description = ""
                                    if '/*' in content and '*/' in content:
                                        description = content.split('/*')[1].split('*/')[0].strip()
                                    local_examples.append({
                                        'file': str(file.relative_to(examples_dir)),
                                        'content': content,
                                        'description': description
                                    })
                                logging.debug(f"Ejemplo cargado: {file.relative_to(examples_dir)}")
                            except Exception as e:
                                logging.error(f"Error al cargar ejemplo {file}: {e}")
                    else:
                        # Recursivamente procesar subdirectorios
                        local_examples.extend(process_directory(subdir))
            
            return local_examples
        
        # Iniciar el procesamiento recursivo
        examples = process_directory(examples_dir)
        
        logging.info(f"✅ {len(examples)} ejemplos cargados")
        return examples

    def read_system_prompt_extra(self):
        """Lee el archivo de recomendaciones adicionales para el system prompt"""
        content = ""
        
        # Intentar leer archivo específico de la plataforma primero
        platform_file = f'system_prompt_extra_{self.platform}.txt'
        try:
            if os.path.exists(platform_file):
                with open(platform_file, 'r', encoding='utf-8') as f:
                    content = "\n" + f.read()
                logging.info(f"✅ Archivo de prompt específico cargado: {platform_file}")
            else:
                # Caer en el archivo genérico
                with open('system_prompt_extra.txt', 'r', encoding='utf-8') as f:
                    content = "\n" + f.read()
                logging.info(f"✅ Archivo de prompt genérico cargado: system_prompt_extra.txt")
        except FileNotFoundError:
            logging.warning(f"⚠️ No se encontró {platform_file} ni system_prompt_extra.txt")
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

    def generate_c_code(self, prompt):
        logging.info(f"🤖 Generando código Z80 para {self.platform.upper().replace('_', ' ')} basado en ejemplos existentes...")
        
        # Cargar ejemplos
        examples = self._load_examples()
        
        # Crear el prompt del sistema con los ejemplos
        if self.platform == 'zx_spectrum':
            system_prompt = """You are a Z88DK C code generator for ZX Spectrum 48K.
CRITICAL: Output ONLY the source code itself. No introduction, no explanation, no markdown blocks.
"""
        elif self.platform == 'amstrad_cpc':
            system_prompt = """You are a CPCtelera C code generator for Amstrad CPC 464.
CRITICAL: Output ONLY the source code itself. No introduction, no explanation, no markdown blocks.
"""
        
        system_prompt += "\nHere are some example programs to guide your generation:\n"
        
        # Agregar ejemplos al prompt del sistema (limitado a 5 ejemplos para no sobrecargar)
        example_count = 0
        max_examples = 5
        
        # Organizar ejemplos por categorías
        categorized_examples = {}
        for example in examples:
            # Extraer la categoría del path del archivo
            path_parts = example['file'].split('/')
            if len(path_parts) > 1:
                category = path_parts[0]  # La primera parte del path es la categoría
            else:
                category = "general"
                
            if category not in categorized_examples:
                categorized_examples[category] = []
            
            categorized_examples[category].append(example)
        
        # Mostrar ejemplos por categoría
        for category, category_examples in categorized_examples.items():
            system_prompt += f"\n## Category: {category}\n"
            
            # Limitar a 2 ejemplos por categoría
            for example in category_examples[:2]:
                if example_count >= max_examples:
                    break
                    
                system_prompt += f"\nExample '{example['file']}':\n"
                if example['description']:
                    system_prompt += f"Description: {example['description']}\n"
                system_prompt += f"Code:\n{example['content']}\n"
                example_count += 1
                
            if example_count >= max_examples:
                break
        
        if self.platform == 'zx_spectrum':
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
        
        system_prompt += self.read_system_prompt_extra()  
    
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Write {self.platform.replace('_', ' ')} C code that: {prompt} OUTPUT CODE ONLY."}
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
    parser.add_argument('--platform', type=str, default='zx_spectrum', 
                        choices=['zx_spectrum', 'amstrad_cpc'],
                        help='Target platform (zx_spectrum or amstrad_cpc)')
    args = parser.parse_args()
    
    platform_name = args.platform.upper().replace('_', ' ')
    
    print(colored(f"\n🎮 {platform_name} Code Generator 🎮", "green", attrs=['bold']))
    print(colored("=" * 40, "green"))
    
    try:
        generator = LLMZ80Generator(platform=args.platform)
        prompt = input(colored("\n📝 Enter your prompt: ", "yellow"))
        logging.info("Starting code generation process")
        
        paths = generator._get_output_paths(prompt)
        c_code = generator.generate_c_code(prompt)
        generator.save_c_code(c_code, prompt, paths)
        
        print(colored("\n✨ Success! ✨", "green", attrs=['bold']))
        print(colored(f"📂 Files saved in: {paths['base']}", "cyan"))
        print(colored(f"📄 C code: {paths['c_file']}", "cyan"))
        
        if args.platform == 'zx_spectrum':
            print(colored("\n🚀 Continuing 'build.sh' to compile and run the program", "yellow"))
        elif args.platform == 'amstrad_cpc':
            print(colored("\n🚀 Continuing 'build_amstrad.sh' to compile and run the program", "yellow"))
        
    except Exception as e:
        logging.error(f"Process failed: {e}")
        raise

if __name__ == "__main__":
    main()
