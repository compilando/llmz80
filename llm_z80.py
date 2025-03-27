#!/usr/bin/env python3
import argparse
import logging
import os
from pathlib import Path
from termcolor import colored

# Importación de módulos propios
from llmz80.utils.config import load_config, load_api_key, initialize_global_vars, DEFAULT_LOG_LEVEL
from llmz80.utils.logger import setup_logging
from llmz80.api.generator import LLMZ80Generator

# Constantes
CONFIG_FILE = "config.yml"

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
    parser.add_argument('--rebuild-embeddings', action='store_true',
                        help='Elimina y reconstruye completamente el caché de embeddings.')
    parser.add_argument('--test-file', type=str,
                        help='Prueba la generación de embeddings para un archivo específico.')
    parser.add_argument('--max-chunk-size', type=int,
                        help='Define el tamaño máximo de chunk para embeddings (reemplaza valor en config.yml).')

    args = parser.parse_args()

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
            
            print(colored("\n✨ ¡Éxito! ✨", "green", attrs=['bold']))
            print(colored(f"📂 Archivos guardados en: {paths['base'].resolve()}", "cyan"))
            
        except Exception as e:
            logging.error(f"Error durante generación o guardado de código: {e}")
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
        logging.error(f"Error de Configuración: {e}")
        print(colored(f"❌ Error de Configuración: {e}", "red"))
    except Exception as e:
        logging.exception(f"Ocurrió un error inesperado: {e}")  # Registrar traceback completo para errores inesperados
        print(colored(f"❌ Ocurrió un error inesperado. Revisar logs en {global_vars['log_dir'] if 'global_vars' in locals() else 'logs'} para detalles.", "red"))

if __name__ == "__main__":
    main() 