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
import shutil

# Importación de módulos propios
from llmz80.utils.config import load_config, load_api_key, initialize_global_vars, DEFAULT_LOG_LEVEL
from llmz80.utils.logger import setup_logging
from llmz80.api.generator import LLMZ80Generator
from llmz80.utils.helpers import (
    apply_deterministic_cpc_fixes,
    build_completion_kwargs,
    filter_compiler_output,
    hash_error_signature,
)
from llmz80.core.validators import CodeValidator
from llmz80.core.learning import LearningSystem
from llmz80.core.code_context import (
    build_embedding_text,
    build_example_context,
    discover_support_files,
    extract_descriptions,
)
# Importar módulo de Vector DB
from vector_db import get_qdrant_client, ensure_collection_exists, upsert_embeddings, PointStruct
import uuid # Para generar IDs únicos para Qdrant

# Constantes
CONFIG_FILE = "config.yml"

def launch_emulator_for_platform(platform: str, output_dir: Path, config: dict, emulator_override: str = None):
    """Lanza el emulador apropiado con el archivo generado.
    
    Args:
        platform: Plataforma (spectrum, amstrad_cpc)
        output_dir: Directorio donde está el archivo compilado
        config: Configuración del proyecto
        emulator_override: Emulador específico a usar (opcional)
    """
    logging.info("🚀 Lanzando emulador...")
    
    # Obtener configuración del emulador
    emulator_config = config.get('emulator', {}).get(platform, {})
    emulator_name = emulator_override or emulator_config.get('name', 'fuse' if platform == 'spectrum' else 'cap32')
    emulator_params = emulator_config.get('params', '').split()
    
    # Buscar el archivo generado
    if platform == 'spectrum':
        artifact_pattern = "*.tap"
    elif platform == 'amstrad_cpc':
        artifact_pattern = "*.dsk"
    else:
        logging.error(f"❌ Plataforma no soportada para emulador: {platform}")
        return
    
    # Buscar el archivo
    artifact_files = list(output_dir.glob(artifact_pattern))
    if not artifact_files:
        logging.error(f"❌ No se encontró archivo {artifact_pattern} en {output_dir}")
        return
    
    artifact_file = artifact_files[0].resolve()  # Tomar el primero y convertir a ruta absoluta
    logging.info(f"📂 Archivo encontrado: {artifact_file}")
    
    # Construir comando del emulador según la plataforma
    if platform == 'spectrum':
        if emulator_name == 'fuse':
            cmd = ['fuse', '--machine', '48', '--graphics-filter', '3x', '--tape', str(artifact_file), '--auto-load']
        elif emulator_name == 'zesarux':
            cmd = ['zesarux', '--noconfigfile', '--machine', '48k', '--realvideo', '--nosplash', '--zoom', '2', '--tape', str(artifact_file)]
        else:
            logging.warning(f"⚠️ Emulador {emulator_name} no configurado, intentando con fuse")
            cmd = ['fuse', '--machine', '48', '--graphics-filter', '3x', '--tape', str(artifact_file), '--auto-load']
    
    elif platform == 'amstrad_cpc':
        if emulator_name == 'cap32':
            cmd = ['cap32', str(artifact_file)]
        elif emulator_name == 'cpcec':
            cmd = ['cpcec', str(artifact_file)]
        else:
            logging.warning(f"⚠️ Emulador {emulator_name} no configurado, intentando con cap32")
            cmd = ['cap32', str(artifact_file)]
    
    # Verificar que el emulador existe
    try:
        result = subprocess.run(['which', cmd[0]], capture_output=True)
        if result.returncode != 0:
            logging.error(f"❌ Emulador '{cmd[0]}' no encontrado en el sistema")
            print(colored(f"❌ Emulador '{cmd[0]}' no encontrado. Por favor instálalo:", "red"))
            if platform == 'spectrum':
                print(colored(f"   sudo pacman -S fuse  # o zesarux", "yellow"))
            else:
                print(colored(f"   Instala Cap32 o CPCEC para Amstrad CPC", "yellow"))
            return
    except Exception as e:
        logging.error(f"❌ Error verificando emulador: {e}")
        return
    
    # Lanzar emulador
    try:
        logging.info(f"🎮 Ejecutando: {' '.join(cmd)}")
        print(colored(f"\n🎮 Lanzando emulador {cmd[0]}...", "blue"))
        print(colored(f"📂 Archivo: {artifact_file.name}", "cyan"))
        
        # Ejecutar en primer plano para que el usuario vea el emulador
        # No cambiar al directorio output_dir, ejecutar desde donde estamos
        process = subprocess.run(cmd)
        
        if process.returncode == 0:
            logging.info("✅ Emulador cerrado correctamente")
        else:
            logging.warning(f"⚠️ Emulador cerrado con código: {process.returncode}")
            
    except KeyboardInterrupt:
        logging.info("⚠️ Emulador interrumpido por el usuario")
    except Exception as e:
        logging.error(f"❌ Error al lanzar emulador: {e}")
        print(colored(f"❌ Error al lanzar emulador: {e}", "red"))

def populate_vector_db(platform: str, generator: LLMZ80Generator):
    """Extrae descripciones, genera embeddings de ellas y sube a Qdrant junto con el código fuente."""
    logging.info(f"🚀 Iniciando población de la base de datos vectorial para la plataforma: {platform}")
    
    qdrant_client = get_qdrant_client()
    if not qdrant_client:
        logging.error("❌ No se pudo conectar a Qdrant. Abortando población.")
        return

    if not ensure_collection_exists(qdrant_client, platform):
        logging.error("❌ No se pudo asegurar la existencia de la colección en Qdrant. Abortando población.")
        return

    examples_dir = Path(generator.global_vars['example_dir_template'].format(platform=platform))
    example_file_pattern = "**/*.c"
    excluded_dirs = {examples_dir / "common", examples_dir / "build"}
    # Patrones para buscar ambas descripciones
    desc_en_pattern = re.compile(r"^//\s*Description:\s*(.*)", re.IGNORECASE)
    desc_es_pattern = re.compile(r"^//\s*Descripcion:\s*(.*)", re.IGNORECASE) # Sin tilde por simplicidad regex/compatibilidad

    logging.info(f"🔍 Buscando archivos de ejemplo ({example_file_pattern}) en: {examples_dir}")
    
    all_points_to_upsert = []
    processed_files = 0
    failed_files = 0

    for file_path in examples_dir.rglob(example_file_pattern):
        if any(excluded in file_path.parents for excluded in excluded_dirs):
            logging.debug(f"Omitiendo archivo en directorio excluido: {file_path}")
            continue
            
        logging.info(f"📄 Procesando archivo: {file_path.relative_to(examples_dir)}")
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')

            if not content.strip():
                logging.warning(f"⚠️ Archivo vacío, omitiendo: {file_path}")
                continue

            # --- Extraer Descripciones (Inglés y Español) ---
            desc_en, desc_es = extract_descriptions(content)

            # Fallback si no se encuentra ninguna descripción
            project_dir = file_path.parent.parent if file_path.parent.name == "src" else file_path.parent
            support_files = discover_support_files(file_path, project_dir)
            rel_path = str(file_path.relative_to(examples_dir))
            text_for_embedding = build_embedding_text(rel_path, content, support_files)
            if desc_en and desc_es:
                logging.debug(f"  -> Descripciones encontradas: '{desc_en}' / '{desc_es}'")
            elif desc_en:
                logging.debug(f"  -> Descripción EN encontrada: '{desc_en}'")
            elif desc_es:
                logging.debug(f"  -> Descripción ES encontrada: '{desc_es}'")
            else:
                fallback_desc = file_path.stem.replace('_', ' ') # Usar nombre base sin extensión
                desc_en = fallback_desc # Guardar fallback como EN por defecto
                logging.warning(f"⚠️ No se encontró descripción EN ({desc_en_pattern.pattern}) ni ES ({desc_es_pattern.pattern}) en {file_path}. Usando nombre de archivo: '{fallback_desc}'")
                
            if not text_for_embedding: # Doble chequeo por si acaso
                logging.error(f"❌ No se pudo obtener texto para embedding en {file_path}. Omitiendo.")
                failed_files += 1
                continue

            # --- Generar Embedding del Texto Combinado (o individual) ---
            logging.debug(f"  -> Texto para embedding: '{text_for_embedding}'")
            embedding_vector = generator.embedding_manager.get_embedding(text_for_embedding)

            if embedding_vector is None or not isinstance(embedding_vector, np.ndarray) or embedding_vector.size == 0:
                 logging.warning(f"⚠️ No se pudo generar embedding para: {file_path}")
                 failed_files += 1
                 continue

            # --- Crear Punto para Qdrant --- 
            point_id = str(uuid.uuid4())

            # Limitar tamaño del código fuente si es necesario (raro, pero por seguridad)
            max_payload_code_size = 500 * 1024 # Límite ejemplo: 500KB por seguridad
            source_code_payload = build_example_context(file_path, examples_dir, generator.global_vars['max_example_size'])
            if len(source_code_payload) > max_payload_code_size:
                logging.warning(f"Truncando código fuente en payload para {file_path} ({len(content)} > {max_payload_code_size})")
                source_code_payload = source_code_payload[:max_payload_code_size] + "\n//... TRUNCATED ..."

            point = PointStruct(
                     id=point_id,
                     vector=embedding_vector.tolist(),
                     payload={
                         "file_path": rel_path,
                         "description": desc_en, # Guardar descripción EN
                         "descripcion_es": desc_es, # Guardar descripción ES (puede ser vacía)
                         "source_code": source_code_payload # Guardar código fuente
                     }
                 )

            all_points_to_upsert.append(point)
            logging.info(f"  -> Generado 1 punto de embedding.")
            processed_files += 1
            
            # Upsert en batches (opcional)
            # ...

        except Exception as e:
            logging.error(f"❌ Error procesando archivo {file_path}: {e}")
            failed_files += 1

    # Upsert final
    if all_points_to_upsert:
        logging.info(f"Iniciando upsert final de {len(all_points_to_upsert)} puntos a Qdrant...")
        try:
            # Asegurarse de que el cliente Qdrant está disponible
            qdrant_client = get_qdrant_client() # Asumiendo que existe una función para obtener el cliente
            if qdrant_client:
                 upsert_embeddings(qdrant_client, platform, all_points_to_upsert)
                 logging.info("✅ Upsert final completado.")
            else:
                logging.error("❌ No se pudo obtener el cliente Qdrant para el upsert final.")
        except Exception as e:
            logging.error(f"❌ Error durante el upsert final a Qdrant: {e}")
            # Considerar si se debe reintentar o manejar el error de otra forma
    else:
        logging.warning("⚠️ No se generaron puntos para hacer upsert.")

    logging.info("🏁 Población de la base de datos vectorial completada.")
    logging.info(f"📊 Resumen: {processed_files} archivos procesados, {failed_files} archivos con errores.")

def describe_code_file(platform: str, file_path: str, generator: LLMZ80Generator):
    """Genera una descripción para un archivo de código C usando el LLM."""
    logging.info(f"📄 Iniciando descripción del archivo: {file_path} para la plataforma {platform}")
    
    try:
        # 1. Leer el contenido del archivo
        source_path = Path(file_path)
        if not source_path.is_file():
            logging.error(f"❌ Archivo no encontrado: {file_path}")
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
            
        with open(source_path, 'r', encoding='utf-8', errors='ignore') as f:
            source_code = f.read()
            
        if not source_code.strip():
            logging.error(f"❌ Archivo vacío: {file_path}")
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
            logging.warning(f"El código fuente es muy largo ({len(source_code)} chars), truncando para el prompt de descripción.")
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
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                **build_completion_kwargs(
                    generator.model,
                    max_tokens=150,
                    temperature=0.2,
                    reasoning_effort=getattr(generator, 'reasoning_effort', None),
                ),
            )
            raw_description = response.choices[0].message.content
        except Exception as api_error:
            logging.error(f"❌ Error durante la llamada a la API de OpenAI: {api_error}")
            raise

        # 4. Limpiar y Devolver Descripción
        if not raw_description:
            logging.error("❌ La API no devolvió una descripción.")
            raise ValueError("La API no devolvió contenido.")
        
        # Limpieza básica: quitar espacios extra, saltos de línea, y posibles comillas o prefijos
        cleaned_description = raw_description.strip().replace('\n', ' ').replace('\r', '')
        # Quitar comillas si la descripción viene entre comillas
        if cleaned_description.startswith('"') and cleaned_description.endswith('"'):
            cleaned_description = cleaned_description[1:-1]
        elif cleaned_description.startswith("'") and cleaned_description.endswith("'"):
            cleaned_description = cleaned_description[1:-1]
            
        logging.info(f"✅ Descripción generada: '{cleaned_description}'")
        # Imprimir SOLO la descripción a stdout para que el script .sh la capture
        print(cleaned_description)

    except Exception as e:
        logging.error(f"❌ Error generando descripción para {file_path}: {e}")
        # Salir con código de error para que el script .sh lo detecte
        # No imprimir nada a stdout en caso de error
        # Considerar si es mejor imprimir un mensaje de error a stderr
        # import sys
        # print(f"Error: {e}", file=sys.stderr)
        raise # Re-lanzar la excepción para que main() la capture si es necesario

def prepare_amstrad_cpc_build_project(output_dir: Path) -> bool:
    """Prepara el directorio generado como proyecto CPCtelera compilable."""
    cpct_path = os.environ.get("CPCT_PATH", "/home/oscar/cpctelera/cpctelera/")
    if not cpct_path.endswith("/"):
        cpct_path += "/"

    cpct_dir = Path(cpct_path)
    if not (cpct_dir / "src" / "cpctelera.h").exists():
        logging.error(f"❌ No se encontró CPCtelera en CPCT_PATH={cpct_path}")
        return False

    template_dir = Path("templates/amstrad_cpc")
    template_makefile = template_dir / "Makefile"
    template_cfg_dir = template_dir / "cfg"
    if not template_makefile.exists() or not template_cfg_dir.exists():
        logging.error("❌ No se encontraron templates/amstrad_cpc/Makefile o templates/amstrad_cpc/cfg")
        return False

    src_dir = output_dir / "src"
    cfg_dir = output_dir / "cfg"
    src_dir.mkdir(exist_ok=True)
    cfg_dir.mkdir(exist_ok=True)

    shutil.copy2(output_dir / "main.c", src_dir / "main.c")
    shutil.copy2(template_makefile, output_dir / "Makefile")

    for cfg_file in template_cfg_dir.glob("*.mk"):
        target = cfg_dir / cfg_file.name
        shutil.copy2(cfg_file, target)
        if cfg_file.name == "build_config.mk":
            content = target.read_text(encoding="utf-8", errors="ignore")
            content = content.replace("{{CPCT_PATH}}", cpct_path.rstrip("/"))
            target.write_text(content, encoding="utf-8")

    return True


def _run_version_command(command: list[str]) -> str:
    """Return a compact version string for build diagnostics."""
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
    except Exception as exc:
        return f"unavailable ({exc})"
    output = (result.stdout or result.stderr or "").strip().splitlines()
    if not output:
        return f"exit={result.returncode}"
    return output[0][:300]


def save_build_environment_report(platform: str, output_dir: Path, compile_command: list[str]) -> None:
    """Persist the exact local build context used for this generation."""
    report_path = output_dir / "build_environment.txt"
    cpct_path = os.environ.get("CPCT_PATH", "/home/oscar/cpctelera/cpctelera/")
    lines = [
        "BUILD ENVIRONMENT",
        "=" * 50,
        f"platform: {platform}",
        f"output_dir: {output_dir.resolve()}",
        f"compile_command: {' '.join(compile_command)}",
        f"CPCT_PATH: {cpct_path}",
        f"sdcc: {_run_version_command(['sdcc', '--version'])}",
        f"make: {_run_version_command(['make', '--version'])}",
    ]

    cpct_dir = Path(cpct_path)
    if (cpct_dir / ".git").exists():
        lines.append(f"CPCtelera git: {_run_version_command(['git', '-C', str(cpct_dir), 'rev-parse', '--short', 'HEAD'])}")
    lines.append("")

    try:
        report_path.write_text("\n".join(lines), encoding="utf-8")
        logging.info(f"🧾 Entorno de build guardado en: {report_path}")
    except Exception as exc:
        logging.warning(f"⚠️ No se pudo guardar entorno de build: {exc}")


def find_platform_artifacts(platform: str, output_dir: Path) -> list[Path]:
    """Find generated artifacts that prove the real toolchain produced output."""
    if platform == "spectrum":
        patterns = ["*.tap"]
    elif platform == "amstrad_cpc":
        patterns = ["*.dsk"]
    else:
        patterns = ["*.bin"]

    artifacts: list[Path] = []
    for pattern in patterns:
        artifacts.extend(sorted(output_dir.rglob(pattern)))
    return artifacts



def attempt_compilation_and_correction(platform: str, output_dir: Path, config: dict, generator: LLMZ80Generator, 
                                      user_prompt: str, max_attempts: int = 3, enable_validation: bool = True,
                                      learning_system: LearningSystem = None):
    """Intenta compilar el código C generado y, si falla, aplica correcciones automáticas con retry.
    
    Args:
        platform: Plataforma objetivo
        output_dir: Directorio donde se encuentra el código generado
        config: Configuración del proyecto
        generator: Instancia del generador LLMZ80
        user_prompt: Prompt original del usuario
        max_attempts: Número máximo de intentos de corrección (default: 3)
        enable_validation: Habilitar validación pre-compilación (default: True)
        learning_system: Sistema de aprendizaje (opcional)
    
    Returns:
        bool: True si la compilación fue exitosa, False si falló después de todos los intentos
    """
    logging.info("🔨 Iniciando ciclo de compilación con validación, corrección y aprendizaje...")
    main_c_file = output_dir / "main.c"
    
    if not main_c_file.exists():
        logging.error(f"❌ No se encontró el archivo {main_c_file} para compilar.")
        return False
    
    # Inicializar validador si está habilitado
    validator = None
    if enable_validation:
        try:
            validator = CodeValidator(platform)
            logging.info("✅ Validador pre-compilación inicializado")
        except Exception as e:
            logging.warning(f"⚠️ No se pudo inicializar validador: {e}")
            logging.warning("⚠️ Continuando sin validación pre-compilación")

    # Obtener configuración del compilador
    compiler_config = config.get('compiler', {}).get(platform)
    if not compiler_config or not compiler_config.get('c_compiler'):
        logging.warning(f"⚠️ No se encontró configuración de compilador para '{platform}'. Omitiendo compilación.")
        return False

    compiler_cmd = compiler_config['c_compiler']
    compiler_params = compiler_config.get('params', '').split()
    output_artifact_name = config.get('paths', {}).get(platform, {}).get('output_artifact', f'program_{platform}.tap')

    # Construir comando de compilación según el compilador
    if compiler_cmd == "zcc":
        compile_command = [
            compiler_cmd
        ] + compiler_params + [
            "main.c",
            "-o", str(Path(output_artifact_name).stem),
            "-create-app",
            "--subtype=tap"
        ]
    elif compiler_cmd == "sdcc":
        if platform == "amstrad_cpc":
            if not prepare_amstrad_cpc_build_project(output_dir):
                return False
            cpct_path = os.environ.get("CPCT_PATH", "/home/oscar/cpctelera/cpctelera/")
            if not cpct_path.endswith("/"):
                cpct_path += "/"
            compile_command = [
                "make",
                f"CPCT_PATH={cpct_path}"
            ]
        else:
            compile_command = [
                compiler_cmd
            ] + compiler_params + [
                "main.c",
                "-o", f"{Path(output_artifact_name).stem}.rel"
            ]
    else:
        logging.error(f"❌ Compilador '{compiler_cmd}' no soportado.")
        return False

    if compiler_cmd == "sdcc" and platform == "amstrad_cpc":
        logging.info("ℹ️ Compilando Amstrad CPC mediante Makefile CPCtelera generado")
    elif compiler_cmd == "sdcc":
        compile_command = [
            compiler_cmd
        ] + compiler_params + [
            "main.c",
            "-o", f"{Path(output_artifact_name).stem}.rel"
        ]

    # Ciclo de retry con validación y corrección automática
    # Memoria de intentos previos: lista de {'code', 'error_summary', 'error_hash'}
    prior_attempts: list = []
    for attempt in range(1, max_attempts + 1):
        logging.info(f"📍 Intento {attempt}/{max_attempts}...")

        # === VALIDACIÓN PRE-COMPILACIÓN === (en CADA intento, no solo el 1º)
        if validator:
            logging.info("🔍 Ejecutando validación pre-compilación...")
            
            try:
                # Leer código para validar
                with open(main_c_file, 'r') as f:
                    code_to_validate = f.read()

                if platform == "amstrad_cpc":
                    fixed_code, deterministic_fixes = apply_deterministic_cpc_fixes(code_to_validate)
                    if deterministic_fixes and fixed_code != code_to_validate:
                        deterministic_log = output_dir / f"deterministic_fixes_attempt_{attempt}.txt"
                        try:
                            deterministic_log.write_text(
                                "\n".join(f"- {fix}" for fix in deterministic_fixes) + "\n",
                                encoding="utf-8",
                            )
                            (output_dir / f"main_before_deterministic_fixes_attempt_{attempt}.c").write_text(
                                code_to_validate,
                                encoding="utf-8",
                            )
                            main_c_file.write_text(fixed_code, encoding="utf-8")
                            logging.info(
                                "🔧 Correcciones deterministas aplicadas: "
                                + "; ".join(deterministic_fixes)
                            )
                            code_to_validate = fixed_code
                        except Exception as e:
                            logging.warning(f"⚠️ No se pudieron aplicar correcciones deterministas: {e}")
                
                # Validar y generar reporte
                is_valid, validation_report = validator.validate_and_report(code_to_validate)
                
                # Guardar reporte de validación
                validation_report_path = output_dir / "validation_report.txt"
                try:
                    with open(validation_report_path, "w") as f:
                        f.write(validation_report)
                    logging.info(f"📄 Reporte de validación guardado en: {validation_report_path}")
                except Exception as e:
                    logging.warning(f"⚠️ No se pudo guardar reporte de validación: {e}")
                
                # Mostrar reporte en consola
                print("\n" + validation_report + "\n")
                
                # Si hay errores críticos de validación, intentar corrección antes de compilar
                if not is_valid:
                    logging.warning("⚠️ Validación pre-compilación detectó errores críticos")
                    logging.info("🔄 Solicitando corrección basada en validación...")
                    
                    # Construir mensaje de error para el LLM
                    validation_errors = "\n".join([f"- {err}" for err in validator.validate(code_to_validate).errors])
                    error_message = f"PRE-COMPILATION VALIDATION ERRORS:\n{validation_errors}"
                    
                    try:
                        corrected_code = generator.suggest_code_correction(
                            code_to_validate,
                            error_message,
                            platform,
                            user_request=user_prompt,
                            prior_attempts=prior_attempts,
                        )
                        
                        if corrected_code:
                            # Guardar código original
                            backup_validation = output_dir / "main_before_validation_fix.c"
                            try:
                                with open(backup_validation, "w") as f:
                                    f.write(code_to_validate)
                                logging.info(f"💾 Código pre-validación guardado en: {backup_validation}")
                            except Exception as e:
                                logging.warning(f"⚠️ No se pudo guardar backup: {e}")
                            
                            # Aplicar código corregido
                            try:
                                with open(main_c_file, "w") as f:
                                    f.write(corrected_code)
                                logging.info("✨ Código corregido por validación aplicado")
                            except Exception as e:
                                logging.error(f"❌ No se pudo aplicar corrección: {e}")
                                return False
                        else:
                            logging.warning("⚠️ No se obtuvo corrección del LLM para errores de validación")
                            logging.info("⏭️ Continuando con compilación para obtener errores más detallados...")
                    
                    except Exception as e:
                        logging.error(f"❌ Error durante corrección por validación: {e}")
                        logging.info("⏭️ Continuando con compilación...")
                else:
                    logging.info("✅ Código pasó validación pre-compilación")
            
            except Exception as e:
                logging.error(f"❌ Error durante validación pre-compilación: {e}")
                logging.info("⏭️ Continuando con compilación...")
        
        # === COMPILACIÓN ===
        logging.info(f"🔨 Intentando compilación {attempt}/{max_attempts}...")
        
        try:
            if platform == "amstrad_cpc":
                prepare_amstrad_cpc_build_project(output_dir)

            save_build_environment_report(platform, output_dir, compile_command)

            # Ejecutar compilador
            process = subprocess.run(
                compile_command,
                cwd=output_dir,
                capture_output=True,
                text=True,
                check=False
            )

            if process.returncode == 0:
                artifacts = find_platform_artifacts(platform, output_dir)
                if not artifacts:
                    logging.error("❌ El compilador terminó con éxito pero no se encontró artefacto final")
                    print(colored("\n❌ Build sin artefacto final (.tap/.dsk)", "red", attrs=['bold']))
                    return False

                if platform == "amstrad_cpc":
                    canonical_artifact = output_dir / "output.dsk"
                    first_dsk = artifacts[0]
                    if first_dsk.resolve() != canonical_artifact.resolve():
                        try:
                            shutil.copy2(first_dsk, canonical_artifact)
                            logging.info(f"📦 DSK canónico creado: {canonical_artifact}")
                        except Exception as exc:
                            logging.warning(f"⚠️ No se pudo crear output.dsk canónico: {exc}")

                logging.info(f"✅ Compilación exitosa en el intento {attempt}!")
                
                # Guardar log de éxito
                success_log = output_dir / "compilation_success.log"
                try:
                    with open(success_log, "w") as f:
                        f.write(f"Compilación exitosa en el intento {attempt}\n")
                        f.write(f"Comando: {' '.join(compile_command)}\n\n")
                        f.write("ARTEFACTOS:\n")
                        for artifact in artifacts:
                            f.write(f"- {artifact.relative_to(output_dir)} ({artifact.stat().st_size} bytes)\n")
                        f.write("\n")
                        f.write("STDOUT:\n")
                        f.write(process.stdout)
                        if process.stderr:
                            f.write("\nSTDERR:\n")
                            f.write(process.stderr)
                    logging.info(f"📝 Log de éxito guardado en: {success_log}")
                except Exception as e:
                    logging.warning(f"⚠️ No se pudo guardar log de éxito: {e}")
                
                # Registrar éxito en sistema de aprendizaje
                if learning_system:
                    try:
                        with open(main_c_file, 'r') as f:
                            final_code = f.read()
                        learning_system.add_successful_example(
                            prompt=user_prompt,
                            code=final_code,
                            compilation_attempts=attempt
                        )
                        # Indexar también en Qdrant para que retrieval RAG futuro
                        # use este éxito (con boost por compilation_attempts bajos).
                        try:
                            generator.index_successful_generation(
                                user_prompt=user_prompt,
                                code=final_code,
                                compilation_attempts=attempt,
                            )
                        except Exception as e:
                            logging.debug(f"No se pudo indexar éxito en Qdrant: {e}")
                        # Marcar errores previos como resueltos: la correction final
                        # SÍ funcionó, así sube success_rate de esas firmas.
                        for prev in prior_attempts:
                            sig = prev.get('error_hash')
                            desc = prev.get('error_summary', '')[:200]
                            if sig:
                                try:
                                    learning_system.add_common_error(
                                        error_pattern=sig[:120],
                                        error_description=desc,
                                        solution=f"Resuelto en intento {attempt}",
                                        success=True,
                                    )
                                except Exception:
                                    pass
                        logging.info("📚 Ejemplo exitoso registrado en sistema de aprendizaje")
                    except Exception as e:
                        logging.warning(f"⚠️ No se pudo registrar en sistema de aprendizaje: {e}")
                
                return True
            
            # Compilación falló
            logging.error(f"❌ Compilación fallida en el intento {attempt} (código: {process.returncode})")
            raw_error_output = process.stdout + "\n" + process.stderr
            # Filtrar ruido (make[1], Entering directory, etc.) — solo señal a LLM
            error_output = filter_compiler_output(raw_error_output, max_lines=40)
            error_sig = hash_error_signature(error_output)

            # Mostrar error en consola para el usuario (versión filtrada)
            print(colored(f"\n❌ Compilación fallida en intento {attempt}/{max_attempts}", "red"))
            print(colored("=" * 60, "red"))
            for line in error_output.splitlines()[-15:]:
                if 'error' in line.lower() or 'fatal' in line.lower():
                    print(colored(f"  {line}", "red", attrs=['bold']))
                elif 'warning' in line.lower():
                    print(colored(f"  {line}", "yellow"))
                else:
                    print(colored(f"  {line}", "white"))
            print(colored("=" * 60, "red"))

            # Dedupe: si el mismo error firma ya falló antes, no quemamos otro intento
            prior_sigs = {a.get('error_hash') for a in prior_attempts}
            if error_sig and error_sig in prior_sigs:
                logging.error(
                    f"⛔ Mismo error que intento previo (sig={error_sig[:40]}...). "
                    "El LLM no puede corregir; abortando retries."
                )
                print(colored("⛔ Error repetido — abortando ciclo de corrección.", "red", attrs=['bold']))
                return False
            
            # Dar sugerencias específicas según el tipo de error
            if platform == "amstrad_cpc" and "cpctelera.h" in error_output:
                print(colored("\n💡 Sugerencia: Para compilar código Amstrad CPC, usa:", "cyan"))
                print(colored(f"   ./build_amstrad.sh --example={output_dir.name}", "cyan", attrs=['bold']))
                print(colored("   (El script configura automáticamente CPCtelera)", "cyan"))
            
            # Guardar log de error del intento actual
            error_log_path = output_dir / f"compilation_error_attempt_{attempt}.log"
            try:
                with open(error_log_path, "w") as f:
                    f.write(f"Intento {attempt}/{max_attempts}\n")
                    f.write(f"Comando: {' '.join(compile_command)}\n")
                    f.write(f"Código de retorno: {process.returncode}\n\n")
                    f.write(error_output)
                logging.info(f"📝 Error del intento {attempt} guardado en: {error_log_path}")
            except Exception as e:
                logging.error(f"❌ No se pudo guardar log de error: {e}")

            # Si no es el último intento, intentar corrección
            if attempt < max_attempts:
                logging.info(f"🔄 Intentando corrección automática (intento {attempt}/{max_attempts})...")
                
                # Leer código actual
                try:
                    with open(main_c_file, 'r') as f:
                        failed_code = f.read()
                except Exception as e:
                    logging.error(f"❌ No se pudo leer {main_c_file}: {e}")
                    return False

                # Registrar este intento ANTES de pedir corrección, para que el LLM
                # vea su propio historial en intentos futuros del bucle.
                prior_attempts.append({
                    'code': failed_code,
                    'error_summary': error_output[:600],
                    'error_hash': error_sig,
                })

                # Solicitar corrección al LLM con contexto completo
                try:
                    corrected_code = generator.suggest_code_correction(
                        failed_code,
                        error_output,
                        platform,
                        user_request=user_prompt,
                        prior_attempts=prior_attempts[:-1],  # exclude current attempt
                    )
                    
                    # Registrar error en sistema de aprendizaje con firma real
                    # para que get_top_errors() agregue ocurrencias correctamente.
                    if learning_system and corrected_code:
                        try:
                            # Primera línea con 'error:' como descripción legible
                            err_desc = next(
                                (ln for ln in error_output.splitlines() if 'error' in ln.lower()),
                                error_output.splitlines()[0] if error_output else "Compilación falló",
                            )
                            learning_system.add_common_error(
                                error_pattern=error_sig[:120] or err_desc[:120],
                                error_description=err_desc[:200],
                                solution="Corrección aplicada por LLM (resultado pendiente)",
                                success=False,
                            )
                        except Exception as e:
                            logging.debug(f"No se pudo registrar error en aprendizaje: {e}")
                    
                    if corrected_code:
                        # Guardar versión anterior
                        backup_path = output_dir / f"main_attempt_{attempt}.c"
                        try:
                            with open(backup_path, "w") as f:
                                f.write(failed_code)
                            logging.info(f"💾 Código del intento {attempt} guardado en: {backup_path}")
                        except Exception as e:
                            logging.warning(f"⚠️ No se pudo guardar backup: {e}")
                        
                        # Aplicar corrección
                        try:
                            with open(main_c_file, "w") as f:
                                f.write(corrected_code)
                            logging.info(f"✨ Código corregido aplicado en main.c para el intento {attempt + 1}")
                        except Exception as e:
                            logging.error(f"❌ No se pudo aplicar corrección: {e}")
                            return False
                    else:
                        logging.warning(f"⚠️ No se obtuvo código corregido del LLM en el intento {attempt}")
                        return False
                        
                except Exception as e:
                    logging.error(f"❌ Error al obtener corrección del LLM: {e}")
                    return False
            else:
                # Último intento fallido
                logging.error(f"❌ Compilación fallida después de {max_attempts} intentos.")
                print(colored(f"\n💔 Compilación fallida después de {max_attempts} intentos", "red", attrs=['bold']))
                print(colored(f"📁 Los logs detallados están en: {output_dir}", "yellow"))
                
                # Crear resumen de todos los intentos
                summary_path = output_dir / "compilation_attempts_summary.txt"
                try:
                    with open(summary_path, "w") as f:
                        f.write(f"RESUMEN DE COMPILACIÓN\n")
                        f.write(f"{'=' * 50}\n")
                        f.write(f"Total de intentos: {max_attempts}\n")
                        f.write(f"Resultado: FALLIDO\n\n")
                        f.write(f"Comando de compilación:\n{' '.join(compile_command)}\n\n")
                        f.write(f"Logs individuales:\n")
                        for i in range(1, max_attempts + 1):
                            log_file = output_dir / f"compilation_error_attempt_{i}.log"
                            if log_file.exists():
                                f.write(f"  - Intento {i}: {log_file.name}\n")
                        f.write(f"\nCódigos guardados:\n")
                        for i in range(1, max_attempts):
                            code_file = output_dir / f"main_attempt_{i}.c"
                            if code_file.exists():
                                f.write(f"  - Intento {i}: {code_file.name}\n")
                        f.write(f"  - Intento {max_attempts} (final): main.c\n")
                    logging.info(f"📄 Resumen guardado en: {summary_path}")
                except Exception as e:
                    logging.error(f"❌ No se pudo guardar resumen: {e}")
                
                return False

        except FileNotFoundError:
            logging.error(f"❌ Comando del compilador '{compiler_cmd}' no encontrado.")
            return False
        except Exception as e:
            logging.error(f"❌ Error inesperado durante compilación: {e}")
            return False
    
    return False

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
    parser.add_argument('--launch-emulator', action='store_true',
                        help='Lanza el emulador automáticamente después de una compilación exitosa.')
    parser.add_argument('--emulator', type=str, default=None,
                        help='Especifica el emulador a usar (fuse, zesarux, etc.). Por defecto usa el configurado.')
    parser.add_argument('--no-compile', action='store_true',
                        help='Solo genera el código sin compilar. Útil cuando se usará build_amstrad.sh.')

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
                 logging.exception(f"Error inesperado durante descripción: {e}")
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
            
            # Inicializar logger después de configurar logging
            logger = logging.getLogger(__name__)
            
            # 4. Cargar clave de API
            api_key = load_api_key()
            
            # 5. Aplicar tamaño máximo de chunk si se especifica
            if args.max_chunk_size:
                global_vars['max_chunk_size'] = args.max_chunk_size
                logging.info(f"Tamaño máximo de chunk establecido a {args.max_chunk_size} caracteres")
            
            # 6. Inicializar generador
            generator = LLMZ80Generator(args.platform, global_vars, api_key)

            # 6b. Inicializar learning system temprano y conectarlo al generator
            # para que get_top_errors() pueda inyectar guidance en el system prompt.
            try:
                generator.learning_system = LearningSystem(args.platform)
                logging.info("📚 LearningSystem conectado al generator (prompt injection activa)")
            except Exception as e:
                logging.warning(f"⚠️ LearningSystem no disponible al generador: {e}")
                generator.learning_system = None
            
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

                # Si se especificó --no-compile, solo generar el código y salir
                if args.no_compile:
                    logging.info("ℹ️ Opción --no-compile activada. No se intentará compilar.")
                    print(colored(f"\n📁 Directorio: {output_dir.name}", "cyan"))
                    print(colored("ℹ️ Código generado sin compilar", "blue"))
                    if args.platform == "amstrad_cpc":
                        print(colored(f"\n💡 Para compilar, usa:", "cyan"))
                        print(colored(f"   ./build_amstrad.sh --example={output_dir.name}", "cyan", attrs=['bold']))
                else:
                    # Reutilizar learning system ya conectado al generator
                    learning_system = generator.learning_system
                    
                    # Intentar compilar y corregir con aprendizaje
                    if output_dir and output_dir.exists():
                         compilation_success = attempt_compilation_and_correction(
                             args.platform, output_dir, config, generator, 
                             user_prompt, learning_system=learning_system
                         )
                         
                         # Generar reporte de aprendizaje si está disponible
                         if learning_system and compilation_success:
                             try:
                                 report_path = output_dir / "learning_stats.txt"
                                 learning_system.export_report(report_path)
                                 logging.info(f"📊 Reporte de aprendizaje guardado en: {report_path}")
                             except Exception as e:
                                 logging.debug(f"No se pudo guardar reporte de aprendizaje: {e}")
                         
                         # Lanzar emulador si se solicitó y la compilación fue exitosa
                         if args.launch_emulator and compilation_success:
                             launch_emulator_for_platform(args.platform, output_dir, config, args.emulator)
                    else:
                        logging.error("No se pudo determinar el directorio de salida para la compilación.")

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
