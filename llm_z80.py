#!/usr/bin/env python3
import argparse
import logging
import os
from pathlib import Path
from termcolor import colored
import numpy as np
import re # Necesario para extraer la descripción
import sys # Añadido para sys.exit()
import subprocess # Añadido para ejecutar el compilador

# Importación de módulos propios
from llmz80.utils.config import load_config, load_api_key, initialize_global_vars, DEFAULT_LOG_LEVEL
from llmz80.utils.logger import setup_logging
from llmz80.api.generator import LLMZ80Generator
# Importar módulo de Vector DB
from vector_db import get_qdrant_client, ensure_collection_exists, upsert_embeddings, PointStruct
import uuid # Para generar IDs únicos para Qdrant

# Obtener instancia del logger para este módulo
logger = logging.getLogger(__name__)

# Constantes
CONFIG_FILE = "config.yml"

def populate_vector_db(platform: str, generator: LLMZ80Generator):
    """Extrae descripciones, genera embeddings de ellas y sube a Qdrant junto con el código fuente."""
    logger.info(f"🚀 Iniciando población de la base de datos vectorial para la plataforma: {platform}")
    
    qdrant_client = get_qdrant_client()
    if not qdrant_client:
        logger.error("❌ No se pudo conectar a Qdrant. Abortando población.")
        return

    if not ensure_collection_exists(qdrant_client, platform):
        logger.error("❌ No se pudo asegurar la existencia de la colección en Qdrant. Abortando población.")
        return

    examples_dir = Path(generator.global_vars['example_dir_template'].format(platform=platform))
    example_file_pattern = "**/*.c"
    excluded_dirs = {examples_dir / "common", examples_dir / "build"}
    # Patrones para buscar ambas descripciones
    desc_en_pattern = re.compile(r"^//\s*Description:\s*(.*)", re.IGNORECASE)
    desc_es_pattern = re.compile(r"^//\s*Descripcion:\s*(.*)", re.IGNORECASE) # Sin tilde por simplicidad regex/compatibilidad

    logger.info(f"🔍 Buscando archivos de ejemplo ({example_file_pattern}) en: {examples_dir}")
    
    all_points_to_upsert = []
    processed_files = 0
    failed_files = 0

    for file_path in examples_dir.rglob(example_file_pattern):
        if any(excluded in file_path.parents for excluded in excluded_dirs):
            logger.debug(f"Omitiendo archivo en directorio excluido: {file_path}")
            continue
            
        logger.info(f"📄 Procesando archivo: {file_path.relative_to(examples_dir)}")
        try:
            # Leer las primeras líneas para buscar descripciones y luego todo el contenido
            content = ""
            first_lines = []
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                # Leer máximo 5 líneas para buscar descripciones
                for i in range(5):
                    line = f.readline()
                    if not line:
                        break
                    first_lines.append(line.strip())
                # Leer el resto del contenido
                f.seek(0) # Volver al inicio para leer todo
                content = f.read()

            if not content.strip():
                logger.warning(f"⚠️ Archivo vacío, omitiendo: {file_path}")
                continue

            # --- Extraer Descripciones (Inglés y Español) --- 
            desc_en = ""
            desc_es = ""
            for line in first_lines:
                match_en = desc_en_pattern.match(line)
                if match_en:
                    desc_en = match_en.group(1).strip()
                    logger.debug(f"  -> Descripción EN encontrada: '{desc_en}'")
                    continue # Buscar ES en otra línea
                
                match_es = desc_es_pattern.match(line)
                if match_es:
                    desc_es = match_es.group(1).strip()
                    logger.debug(f"  -> Descripción ES encontrada: '{desc_es}'")

            # Fallback si no se encuentra ninguna descripción
            text_for_embedding = ""
            if desc_en and desc_es:
                text_for_embedding = f"{desc_en}. {desc_es}" # Combinar ambas
            elif desc_en:
                text_for_embedding = desc_en
            elif desc_es:
                text_for_embedding = desc_es # Usar español si solo existe esa
            else:
                fallback_desc = file_path.stem.replace('_', ' ') # Usar nombre base sin extensión
                text_for_embedding = fallback_desc
                desc_en = fallback_desc # Guardar fallback como EN por defecto
                logger.warning(f"⚠️ No se encontró descripción EN ({desc_en_pattern.pattern}) ni ES ({desc_es_pattern.pattern}) en {file_path}. Usando nombre de archivo: '{fallback_desc}'")
                
            if not text_for_embedding: # Doble chequeo por si acaso
                logger.error(f"❌ No se pudo obtener texto para embedding en {file_path}. Omitiendo.")
                failed_files += 1
                continue

            # --- Generar Embedding del Texto Combinado (o individual) ---
            logger.debug(f"  -> Texto para embedding: '{text_for_embedding}'")
            embedding_vector = generator.embedding_manager.get_embedding(text_for_embedding)

            if embedding_vector is None or not isinstance(embedding_vector, np.ndarray) or embedding_vector.size == 0:
                 logger.warning(f"⚠️ No se pudo generar embedding para: {file_path}")
                 failed_files += 1
                 continue

            # --- Crear Punto para Qdrant --- 
            point_id = str(uuid.uuid4())

            # Limitar tamaño del código fuente si es necesario (raro, pero por seguridad)
            max_payload_code_size = 500 * 1024 # Límite ejemplo: 500KB por seguridad
            if len(content) > max_payload_code_size:
                logger.warning(f"Truncando código fuente en payload para {file_path} ({len(content)} > {max_payload_code_size})")
                source_code_payload = content[:max_payload_code_size] + "\n//... TRUNCATED ..."
            else:
                source_code_payload = content

            point = PointStruct(
                     id=point_id,
                     vector=embedding_vector.tolist(),
                     payload={
                         "file_path": str(file_path.relative_to(examples_dir)),
                         "description": desc_en, # Guardar descripción EN
                         "descripcion_es": desc_es, # Guardar descripción ES (puede ser vacía)
                         "source_code": source_code_payload # Guardar código fuente
                     }
                 )

            all_points_to_upsert.append(point)
            logger.info(f"  -> Generado 1 punto de embedding.")
            processed_files += 1
            
            # Upsert en batches (opcional)
            # ...

        except Exception as e:
            logger.error(f"❌ Error procesando archivo {file_path}: {e}")
            failed_files += 1

    # Upsert final
    if all_points_to_upsert:
        logger.info(f"Iniciando upsert final de {len(all_points_to_upsert)} puntos a Qdrant...")
        try:
            # Asegurarse de que el cliente Qdrant está disponible
            qdrant_client = get_qdrant_client() # Asumiendo que existe una función para obtener el cliente
            if qdrant_client:
                 upsert_embeddings(qdrant_client, platform, all_points_to_upsert)
                 logger.info("✅ Upsert final completado.")
            else:
                logger.error("❌ No se pudo obtener el cliente Qdrant para el upsert final.")
        except Exception as e:
            logger.error(f"❌ Error durante el upsert final a Qdrant: {e}")
            # Considerar si se debe reintentar o manejar el error de otra forma
    else:
        logger.warning("⚠️ No se generaron puntos para hacer upsert.")

    logger.info("🏁 Población de la base de datos vectorial completada.")
    logger.info(f"📊 Resumen: {processed_files} archivos procesados, {failed_files} archivos con errores.")

def describe_code_file(platform: str, file_path: str, generator: LLMZ80Generator):
    """Genera una descripción para un archivo de código C usando el LLM."""
    logger.info(f"📄 Iniciando descripción del archivo: {file_path} para la plataforma {platform}")
    
    try:
        # 1. Leer el contenido del archivo
        source_path = Path(file_path)
        if not source_path.is_file():
            logger.error(f"❌ Archivo no encontrado: {file_path}")
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
            
        with open(source_path, 'r', encoding='utf-8', errors='ignore') as f:
            source_code = f.read()
            
        if not source_code.strip():
            logger.error(f"❌ Archivo vacío: {file_path}")
            raise ValueError("El archivo está vacío.")

        # 2. Preparar Prompts para el LLM
        system_prompt = f"""You are an expert programmer specialized in Z80 assembly and C for retro platforms like {platform}.
Your task is to analyze the provided C code and generate a concise, one-sentence description of its main functionality suitable for technical documentation or comments.
Focus on the primary purpose or visible effect.
Output ONLY the description text, without any introductory phrases like "This code..." or "The program...".
"""
        
        # Limitar el código fuente enviado si es muy largo (para evitar exceder límites)
        max_code_length_for_prompt = 15000 # Ajustar si es necesario
        if len(source_code) > max_code_length_for_prompt:
            logger.warning(f"El código fuente es muy largo ({len(source_code)} chars), truncando para el prompt de descripción.")
            source_code_for_prompt = source_code[:max_code_length_for_prompt] + "\n// ... (code truncated for description prompt) ..."
        else:
            source_code_for_prompt = source_code
            
        user_prompt = f"""Platform: {platform}
Source Code:
```c
{source_code_for_prompt}
```
Generate a concise, one-sentence description of what this code does."""

        # 3. Llamar a la API de OpenAI
        logging.info("📞 Llamando a la API de OpenAI para generar descripción...")
        try:
            # Usar el cliente y modelo del generador
            response = generator.client.chat.completions.create(
                model=generator.model, # Usar el modelo configurado
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2, # Temperatura baja para descripciones más factuales
                max_tokens=150 # Suficiente para una descripción corta
            )
            raw_description = response.choices[0].message.content
        except Exception as api_error:
            logger.error(f"❌ Error durante la llamada a la API de OpenAI: {api_error}")
            raise

        # 4. Limpiar y Devolver Descripción
        if not raw_description:
            logger.error("❌ La API no devolvió una descripción.")
            raise ValueError("La API no devolvió contenido.")
        
        # Limpieza básica: quitar espacios extra, saltos de línea, y posibles comillas o prefijos
        cleaned_description = raw_description.strip().replace('\n', ' ').replace('\r', '')
        # Quitar comillas si la descripción viene entre comillas
        if cleaned_description.startswith('"') and cleaned_description.endswith('"'):
            cleaned_description = cleaned_description[1:-1]
        elif cleaned_description.startswith("'") and cleaned_description.endswith("'"):
            cleaned_description = cleaned_description[1:-1]
            
        logger.info(f"✅ Descripción generada: '{cleaned_description}'")
        # Imprimir SOLO la descripción a stdout para que el script .sh la capture
        print(cleaned_description)

    except Exception as e:
        logger.error(f"❌ Error generando descripción para {file_path}: {e}")
        # Salir con código de error para que el script .sh lo detecte
        # No imprimir nada a stdout en caso de error
        # Considerar si es mejor imprimir un mensaje de error a stderr
        # import sys
        # print(f"Error: {e}", file=sys.stderr)
        raise # Re-lanzar la excepción para que main() la capture si es necesario

def attempt_compilation_and_correction(platform: str, output_dir: Path, config: dict, generator: LLMZ80Generator):
    """Intenta compilar el código C generado y, si falla, llama al LLM para obtener una sugerencia de corrección."""
    logger.info("🔨 Iniciando compilación...")
    main_c_file = output_dir / "main.c"
    if not main_c_file.exists():
        logger.error(f"❌ No se encontró el archivo {main_c_file} para compilar.")
        return

    # Obtener configuración del compilador desde el config cargado
    compiler_config = config.get('compiler', {}).get(platform)
    if not compiler_config or not compiler_config.get('c_compiler'):
        logger.warning(f"⚠️ No se encontró configuración de compilador para la plataforma '{platform}'. Omitiendo compilación.")
        return

    compiler_cmd = compiler_config['c_compiler']
    compiler_params = compiler_config.get('params', '').split() # Dividir params en lista
    output_artifact_name = config.get('paths', {}).get(platform, {}).get('output_artifact', f'program_{platform}.tap')

    # Asegurarse de que la salida es un .tap
    if not str(output_artifact_name).lower().endswith('.tap'):
        output_artifact_name = output_artifact_name.with_suffix('.tap')

    # Construir comando completo. Asumimos que el comando se ejecuta desde el directorio de salida.
    # Ejemplo para spectrum: zcc +zx -vn -O3 -clib=sdcc_iy main.c -o program_spectrum -create-app
    # Necesitamos añadir main.c, la salida y -create-app (o equivalente)
    # TODO: Refinar esto, puede variar mucho entre compiladores (sdcc vs zcc)
    #       Por ahora, un intento genérico basado en el ejemplo de zcc
    if compiler_cmd == "zcc":
        # Comando específico para zcc (del ejemplo)
        compile_command = [
            compiler_cmd
        ] + compiler_params + [
            str(main_c_file.name), # main.c
            "-o", str(output_artifact_name.name), # Nombre del archivo de salida .tap
            "-create-app",
            "--subtype=tap" # Generar un archivo TAP estándar
        ]
    elif compiler_cmd == "sdcc":
         # Comando específico para sdcc (más complejo, necesita linkear, etc.)
         # Ejemplo: sdcc -mz80 --no-std-crt0 main.c -o output/program.rel
         # Luego: z80asm -ooutput/program.bin output/program.rel ???
         logger.warning(f"⚠️ Compilación automática para SDCC no implementada completamente. Intentando paso simple.")
         compile_command = [
            compiler_cmd
         ] + compiler_params + [
            str(main_c_file.name),
            "-o", f"{output_artifact_name}.rel" # sdcc suele generar .rel
         ]
    else:
        logger.error(f"❌ Compilador '{compiler_cmd}' no soportado para compilación automática.")
        return


    logger.info(f"Ejecutando comando: {' '.join(compile_command)} en {output_dir}")

    try:
        # Ejecutar el compilador desde el directorio de salida
        process = subprocess.run(
            compile_command,
            cwd=output_dir, # Ejecutar en el directorio donde está main.c
            capture_output=True,
            text=True,
            check=False # No lanzar excepción automáticamente si falla
        )

        if process.returncode == 0:
            logger.info("✅ Compilación exitosa.")
            # Podríamos añadir aquí la ejecución del emulador si quisiéramos
        else:
            logger.error(f"❌ Compilación fallida (Código de retorno: {process.returncode}).")
            error_output = process.stdout + "\n" + process.stderr
            logger.debug(f"Salida del compilador:\n{error_output}")

            # Guardar el error
            error_log_path = output_dir / "compilation_error.log"
            try:
                with open(error_log_path, "w") as f:
                    f.write(f"Comando: {' '.join(compile_command)}\n")
                    f.write(f"Código de retorno: {process.returncode}\n\n")
                    f.write(error_output)
                logger.info(f"📝 Error de compilación guardado en: {error_log_path}")
            except Exception as e:
                logger.error(f"❌ No se pudo guardar el log de error de compilación: {e}")

            # Leer el código fuente original que falló
            try:
                 with open(main_c_file, 'r') as f:
                    failed_code = f.read()
            except Exception as e:
                logger.error(f"❌ No se pudo leer el archivo {main_c_file} para corrección: {e}")
                return # No podemos continuar sin el código

            # Llamar al LLM para obtener una sugerencia de corrección
            logger.info("🤖 Solicitando sugerencia de corrección al LLM...")
            try:
                # Usar una función del generador (que crearemos)
                correction_suggestion = generator.suggest_code_correction(failed_code, error_output, platform)

                if correction_suggestion:
                    suggestion_path = output_dir / "proposed_fix.c"
                    try:
                        with open(suggestion_path, "w") as f:
                            f.write("// Sugerencia de corrección basada en el error:\n")
                            f.write(f"// Comando fallido: {' '.join(compile_command)}\n")
                            f.write(f"// Error original guardado en: compilation_error.log\n\n")
                            f.write(correction_suggestion)
                        logger.info(f"💡 Sugerencia de corrección guardada en: {suggestion_path}")
                    except Exception as e:
                        logger.error(f"❌ No se pudo guardar la sugerencia de corrección: {e}")
                else:
                    logger.warning("⚠️ El LLM no proporcionó una sugerencia de corrección.")

            except Exception as e:
                logger.error(f"❌ Error al obtener sugerencia de corrección del LLM: {e}")

    except FileNotFoundError:
        logger.error(f"❌ Comando del compilador '{compiler_cmd}' no encontrado. Asegúrate de que esté en el PATH.")
    except Exception as e:
        logger.error(f"❌ Error inesperado durante la compilación: {e}")

def main():
    """Función principal para el generador de código LLMZ80."""
    parser = argparse.ArgumentParser(
        description='LLMZ80 Code Generator - Genera código C para plataformas Z80 usando OpenAI.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter  # Mostrar valores por defecto en la ayuda
    )
    parser.add_argument('--platform', type=str, default='spectrum',
                        choices=['spectrum', 'amstrad_cpc'],
                        help='Plataforma objetivo.')
    parser.add_argument('--prompt', type=str, default=None,
                        help='Prompt para generación de código (si se omite, preguntará interactivamente).')
    parser.add_argument('--config', type=str, default=CONFIG_FILE,
                        help='Ruta al archivo de configuración YAML.')
    # Añadir argumento para nivel de log
    parser.add_argument('--log-level', type=str, default=DEFAULT_LOG_LEVEL,
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                        help='Establecer nivel de logging para consola.')
    # Añadir argumentos para control de caché
    parser.add_argument('--clear-cache', action='store_true',
                        help='Limpiar el caché de embeddings antes de ejecutar.')
    parser.add_argument('--force-truncate', action='store_true',
                        help='Forzar truncado de todos los ejemplos, incluso los que ya están en caché.')
    parser.add_argument('--no-embeddings', action='store_true',
                        help='Omitir embeddings y búsqueda semántica (más rápido, pero ejemplos menos relevantes).')
    parser.add_argument('--repair-cache', action='store_true',
                        help='Verificar y reparar caché de embeddings corrupto.')
    parser.add_argument('--fix-embeddings', action='store_true',
                        help='Buscar y reparar específicamente embeddings inválidos o escalares.')
    parser.add_argument('--rebuild-embeddings', action='store_true',
                        help='Elimina y reconstruye completamente el caché de embeddings.')
    parser.add_argument('--test-file', type=str,
                        help='Prueba la generación de embeddings para un archivo específico.')
    parser.add_argument('--max-chunk-size', type=int,
                        help='Define el tamaño máximo de chunk para embeddings (reemplaza valor en config.yml).')
    # --- Nueva opción para poblar la BD vectorial ---
    parser.add_argument('--populate-db', action='store_true',
                        help='Poblar la base de datos vectorial con los embeddings de los ejemplos y salir.')
    # --- Nueva opción para describir código --- 
    parser.add_argument('--describe-code', action='store_true',
                        help='Generar una descripción para un archivo de código C y salir.')
    parser.add_argument('--file', type=str, 
                        help='Ruta al archivo .c a describir (usado con --describe-code).')

    args = parser.parse_args()

    # --- Validaciones de argumentos --- 
    if args.describe_code and not args.file:
        parser.error("--file es requerido cuando se usa --describe-code")
    if args.file and not args.describe_code:
        parser.error("--describe-code es requerido cuando se usa --file")
    # Asegurar que las acciones principales son mutuamente excluyentes
    action_flags = sum([args.prompt is not None, args.populate_db, args.describe_code])
    if action_flags > 1:
        parser.error("Solo se puede realizar una acción principal a la vez (--prompt, --populate-db, o --describe-code)")
    # Permitir --file solo con --describe-code o --test-file
    if args.file and not (args.describe_code or args.test_file):
         parser.error("--file solo es válido con --describe-code o --test-file")

    # --- Comprobar si se solicita poblar la BD --- 
    if args.populate_db:
        platform_name = args.platform.upper().replace('_', ' ')
        print(colored(f"\n🔧 Iniciando Población de Base de Datos Vectorial para {platform_name} 🔧", "blue", attrs=['bold']))
        try:
            config = load_config(args.config)
            global_vars = initialize_global_vars(config, args.platform)
            setup_logging(global_vars['log_dir'], args.log_level) 
            api_key = load_api_key()
            # Aplicar tamaño máximo de chunk si se especifica
            if args.max_chunk_size:
                global_vars['max_chunk_size'] = args.max_chunk_size
                logging.info(f"Tamaño máximo de chunk establecido a {args.max_chunk_size} caracteres")
            
            generator = LLMZ80Generator(args.platform, global_vars, api_key)
            populate_vector_db(args.platform, generator)
        except ValueError as e:
            logging.error(f"Error de Configuración durante población: {e}")
            print(colored(f"❌ Error de Configuración: {e}", "red"))
        except Exception as e:
            logging.exception(f"Error inesperado durante población: {e}")
            print(colored(f"❌ Error inesperado. Revisar logs.", "red"))
        finally:
            print(colored("✅ Proceso de población finalizado.", "blue"))
        return # Salir después de poblar la BD
    # --- Fin de la comprobación para poblar la BD ---

    # --- Comprobar si se solicita describir código --- 
    if args.describe_code:
        # Eliminar o comentar la siguiente línea para evitar que se capture
        # platform_name = args.platform.upper().replace('_', ' ')
        # print(colored(f"\n📄 Iniciando Descripción de Código para {platform_name} 📄", "blue", attrs=['bold']))
        
        # Configuración mínima necesaria para describir (log, api key, cliente)
        # El logging irá a stderr o archivo, no a stdout, así que está bien.
        try:
            config = load_config(args.config)
            global_vars = initialize_global_vars(config, args.platform)
            # Asegurarse de que el logging esté configurado ANTES de usar el logger
            # Es importante que setup_logging no imprima a stdout
            setup_logging(global_vars['log_dir'], args.log_level)
            # Obtener logger DESPUÉS de configurar
            logger = logging.getLogger(__name__) 
            api_key = load_api_key()
            
            generator = LLMZ80Generator(args.platform, global_vars, api_key)
            
            describe_code_file(args.platform, args.file, generator)
            # La función describe_code_file imprime la descripción a stdout
            sys.exit(0)
        except FileNotFoundError:
            # Los errores se loguean o se imprimen en stderr (idealmente)
            sys.exit(1) 
        except ValueError as e:
            # Imprimir errores a stderr sería mejor, pero print va a stdout
            # Lo dejamos así por ahora, pero idealmente iría a stderr
            print(colored(f"❌ Error: {e}", "red"))
            sys.exit(1)
        except Exception as e:
            # Usar logger aquí si ya está inicializado
            if 'logger' in locals():
                 logger.exception(f"Error inesperado durante descripción: {e}")
            # Imprimir a stdout (idealmente stderr)
            print(colored(f"❌ Error inesperado. Revisar logs.", "red"))
            sys.exit(1)
    # --- Fin de la comprobación para describir código ---

    # --- Flujo normal (existente para --prompt o interactivo) --- 
    # Solo continuar con el flujo completo si no se hizo una acción específica antes
    if not args.populate_db and not args.describe_code:
        platform_name = args.platform.upper().replace('_', ' ')
        print(colored(f"\n🎮 Bienvenido al Generador de Código para {platform_name} 🎮", "green", attrs=['bold']))
        print(colored("=" * (len(platform_name) + 36), "green"))

        try:
            # 1. Cargar configuración
            config = load_config(args.config)
            
            # 2. Inicializar variables globales
            global_vars = initialize_global_vars(config, args.platform)
            
            # 3. Configurar logging
            setup_logging(global_vars['log_dir'], args.log_level)
            
            # 4. Cargar clave de API
            api_key = load_api_key()
            
            # 5. Aplicar tamaño máximo de chunk si se especifica
            if args.max_chunk_size:
                global_vars['max_chunk_size'] = args.max_chunk_size
                logging.info(f"Tamaño máximo de chunk establecido a {args.max_chunk_size} caracteres")
            
            # 6. Inicializar generador
            generator = LLMZ80Generator(args.platform, global_vars, api_key)
            
            # 7. Aplicar opciones desde argumentos
            
            # Limpiar caché si se solicita
            if args.clear_cache:
                try:
                    generator.cache_manager.clear_cache()
                    logging.info("Caché de embeddings eliminado. Se generarán nuevos embeddings.")
                except Exception as e:
                    logging.error(f"Error al limpiar caché de embeddings: {e}")
                    # Continuamos a pesar del error
            
            # Reparar caché de embeddings si se solicita
            if args.repair_cache:
                try:
                    generator.cache_manager.verify_and_repair_cache()
                    logging.info("Verificación y reparación de caché completada.")
                except Exception as e:
                    logging.error(f"Error al reparar caché de embeddings: {e}")
                    # Continuamos a pesar del error

            # Reparar embeddings inválidos específicamente si se solicita
            if args.fix_embeddings:
                try:
                    if generator.cache_manager.repair_invalid_embeddings():
                        logging.info("Reparación de embeddings inválidos completada.")
                    else:
                        logging.info("No se encontraron embeddings inválidos para reparar.")
                except Exception as e:
                    logging.error(f"Error al reparar embeddings inválidos: {e}")
                    # Continuamos a pesar del error
            
            # Reconstruir completamente el caché de embeddings si se solicita
            if args.rebuild_embeddings:
                try:
                    generator.rebuild_embeddings_cache()
                    logging.info("Reconstrucción completa de caché de embeddings terminada.")
                except Exception as e:
                    logging.error(f"Error al reconstruir caché de embeddings: {e}")
                    # Continuamos a pesar del error
            
            # Probar un archivo específico si se solicita
            if args.test_file:
                try:
                    generator.test_file_embedding(args.test_file)
                    logging.info(f"Prueba de embedding para {args.test_file} completada.")
                    # Si solo se solicitó esta operación, terminar
                    if not args.prompt:
                        return
                except Exception as e:
                    logging.error(f"Error al probar embedding para {args.test_file}: {e}")
                    # Continuamos a pesar del error
            
            # Habilitar el modo de truncado forzado si se solicita
            if args.force_truncate:
                generator.set_force_truncate(True)
            
            # Si se solicita, deshabilitar uso de embeddings
            if args.no_embeddings:
                generator.set_use_embeddings(False)

            # Obtener prompt del usuario
            user_prompt = args.prompt
            if not user_prompt:
                try:
                    user_prompt = input(colored("\n📝 Ingrese su prompt para generación de código: ", "yellow"))
                except EOFError:
                    print(colored("\n❌ No se proporcionó prompt. Saliendo.", "red"))
                    return  # Salir elegantemente si se interrumpe la entrada

            if not user_prompt:  # Verificar de nuevo si la entrada estaba vacía
                 print(colored("\n❌ El prompt no puede estar vacío. Saliendo.", "red"))
                 return

            logging.info("🏁 Iniciando proceso de generación de código...")

            try:
                # Generar código
                generated_code = generator.generate_c_code(user_prompt)
                
                # Guardar archivos generados
                paths = generator.save_generated_files(generated_code, user_prompt)
                output_dir = paths['base'] # Directorio donde se guardó main.c

                print(colored("\n✨ ¡Éxito en generación! ✨", "green", attrs=['bold']))
                print(colored(f"📂 Archivos generados guardados en: {output_dir.resolve()}", "cyan"))

                # ---> ¡NUEVO! Intentar compilar y corregir <---
                if output_dir and output_dir.exists():
                     attempt_compilation_and_correction(args.platform, output_dir, config, generator)
                else:
                    logger.error("No se pudo determinar el directorio de salida para la compilación.")

            except Exception as e:
                logging.error(f"Error durante la generación de código: {e}", exc_info=True)
                print(colored(f"\n❌ Error: {e}", "red"))
                # Intento de emergencia para guardar código parcial si existe
                if 'generated_code' in locals() and generated_code:
                    try:
                        emergency_dir = Path("local/emergency_output")
                        emergency_dir.mkdir(parents=True, exist_ok=True)
                        
                        with open(emergency_dir / "emergency_code.c", "w") as f:
                            f.write(generated_code)
                        with open(emergency_dir / "emergency_prompt.txt", "w") as f:
                            f.write(user_prompt)
                            
                        print(colored(f"📂 Archivos de emergencia guardados en: {emergency_dir.resolve()}", "yellow"))
                    except Exception as e2:
                        print(colored(f"❌ Error al guardar archivos de emergencia: {e2}", "red"))

        except ValueError as e:  # Capturar errores específicos esperados como clave de API faltante
            logging.error(f"Error de Configuración: {e}", exc_info=True)
            print(colored(f"❌ Error de Configuración: {e}", "red"))
        except Exception as e:
            logging.exception(f"Ocurrió un error inesperado en main: {e}")
            print(colored(f"❌ Ocurrió un error inesperado. Revisar logs en {global_vars['log_dir'] if 'global_vars' in locals() else 'logs'} para detalles.", "red"))

if __name__ == "__main__":
    main() 