#!/usr/bin/env python3
import argparse
import json
import os
import sys
import shutil
import subprocess
import yaml
from pathlib import Path

# Colores ANSI para terminal
GREEN = '\033[0;32m'
RED = '\033[0;31m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No color

class SpriteGenerator:
    def __init__(self):
        self.config_file = "resources/platforms.yml"
        self.platforms_data = {}
        self.platforms = []
        self.parse_arguments()
        self.load_platform_data()
        
    def parse_arguments(self):
        """Analizar argumentos de línea de comandos"""
        parser = argparse.ArgumentParser(description="Generador de sprites para plataformas retro")
        parser.add_argument("--prompt", help="Descripción del sprite a generar")
        parser.add_argument("--width", type=int, help="Ancho del sprite")
        parser.add_argument("--height", type=int, help="Alto del sprite")
        parser.add_argument("--platform", help="Plataforma objetivo (spectrum, amstrad_cpc)")
        parser.add_argument("--mode", help="Modo de video (solo para amstrad_cpc)")
        parser.add_argument("--interactive", action="store_true", help="Modo interactivo")
        parser.add_argument("--negative-prompt", help="Prompt negativo para la generación")
        self.args = parser.parse_args()
        
    def load_platform_data(self):
        """Cargar datos de plataformas desde YAML"""
        print(f"{BLUE}🔄 Cargando datos de plataformas...{NC}")
        yaml_path = Path(self.config_file)
        
        if not yaml_path.exists():
            sys.exit(f"{RED}❌ Error: No se encontró {self.config_file}. Verifica que el archivo existe en la carpeta resources/.{NC}")
            
        try:
            with open(yaml_path, 'r') as f:
                self.platforms_data = yaml.safe_load(f)
            
            if not isinstance(self.platforms_data, dict):
                sys.exit(f"{RED}❌ Error: El archivo YAML {self.config_file} no tiene el formato esperado. Debe ser un diccionario.{NC}")
                
            # Obtener lista de plataformas
            self.platforms = list(self.platforms_data.keys())
            
            if not self.platforms:
                sys.exit(f"{RED}❌ Error: No se encontraron plataformas en {self.config_file}.{NC}")
            
            # Verificar estructura mínima para cada plataforma
            for platform_id, platform_data in self.platforms_data.items():
                required_keys = ['name', 'max_width', 'max_height', 'default_width', 'default_height']
                missing_keys = [key for key in required_keys if key not in platform_data]
                if missing_keys:
                    sys.exit(f"{RED}❌ Error: La plataforma '{platform_id}' no tiene todos los campos requeridos. Faltan: {', '.join(missing_keys)}.{NC}")
                
            print(f"{GREEN}✅ Datos de plataformas cargados correctamente{NC}")
        except yaml.YAMLError as e:
            sys.exit(f"{RED}❌ Error en el formato del archivo YAML {self.config_file}:\n{str(e)}{NC}")
        except Exception as e:
            sys.exit(f"{RED}❌ Error al cargar datos: {str(e)}{NC}")
            
    def get_platform_interactive(self):
        """Solicitar plataforma interactivamente"""
        print(f"\n{BLUE}🎮 Selecciona la plataforma:{NC}")
        print(f"{BLUE}📋 Plataformas disponibles:{NC}")
        
        for i, platform_id in enumerate(self.platforms, 1):
            name = self.platforms_data[platform_id]['name']
            print(f"  {i}. {name} ({platform_id})")
        
        print("")
        while True:
            try:
                choice = int(input("Número de plataforma: "))
                if 1 <= choice <= len(self.platforms):
                    platform = self.platforms[choice-1]
                    name = self.platforms_data[platform]['name']
                    print(f"{GREEN}✅ Seleccionado: {name}{NC}")
                    return platform
                else:
                    print(f"{RED}❌ Número inválido. Intenta de nuevo.{NC}")
            except ValueError:
                print(f"{RED}❌ Entrada inválida. Intenta de nuevo.{NC}")
    
    def get_mode_interactive(self, platform):
        """Solicitar modo interactivamente"""
        platform_data = self.platforms_data[platform]
        
        # Si hay un solo modo "default", usarlo automáticamente
        if 'modes' in platform_data and len(platform_data['modes']) == 1 and platform_data['modes'][0] == 'default':
            print(f"{BLUE}ℹ️ Usando modo por defecto para {platform_data['name']}.{NC}")
            return 'default'
            
        if 'modes' not in platform_data or not platform_data['modes']:
            sys.exit(f"{RED}❌ Error: No se encontraron modos para la plataforma {platform}{NC}")
            
        print(f"\n{BLUE}📺 Selecciona el modo para {platform_data['name']}:{NC}")
        print(f"{BLUE}📋 Modos disponibles:{NC}")
        
        modes = platform_data['modes']
        
        for i, mode_name in enumerate(modes, 1):
            # Obtener número de colores para este modo
            if isinstance(platform_data['colors'], dict):
                # Es un diccionario (Amstrad)
                colors = platform_data['colors'][mode_name]
            else:
                # Es un número directo (Spectrum)
                colors = platform_data['colors']
                
            print(f"  {i}. {mode_name} ({colors} colores)")
        
        print("")
        while True:
            try:
                choice = int(input("Número de modo: "))
                if 1 <= choice <= len(modes):
                    mode = modes[choice-1]
                    print(f"{GREEN}✅ Seleccionado: {mode}{NC}")
                    return mode
                else:
                    print(f"{RED}❌ Número inválido. Intenta de nuevo.{NC}")
            except ValueError:
                print(f"{RED}❌ Entrada inválida. Intenta de nuevo.{NC}")
    
    def get_dimensions_interactive(self, platform):
        """Solicitar dimensiones interactivamente"""
        platform_data = self.platforms_data[platform]
        
        max_width = platform_data['max_width']
        max_height = platform_data['max_height']
        default_width = platform_data['default_width']
        default_height = platform_data['default_height']
        
        print(f"\n{BLUE}📐 Configura las dimensiones del sprite:{NC}")
        print(f"{BLUE}ℹ️ Dimensiones máximas: {max_width}x{max_height} píxeles{NC}")
        print(f"{BLUE}ℹ️ Dimensiones recomendadas: {default_width}x{default_height} píxeles{NC}")
        print("")
        
        # Solicitar ancho
        while True:
            try:
                width_input = input(f"Ancho del sprite (8-{max_width}) [{default_width}]: ")
                width = int(width_input) if width_input.strip() else default_width
                
                if 8 <= width <= max_width:
                    break
                print(f"{RED}❌ Ancho inválido. Debe ser entre 8 y {max_width}.{NC}")
            except ValueError:
                print(f"{RED}❌ Entrada inválida. Intenta de nuevo.{NC}")
        
        # Solicitar alto
        while True:
            try:
                height_input = input(f"Alto del sprite (8-{max_height}) [{default_height}]: ")
                height = int(height_input) if height_input.strip() else default_height
                
                if 8 <= height <= max_height:
                    break
                print(f"{RED}❌ Alto inválido. Debe ser entre 8 y {max_height}.{NC}")
            except ValueError:
                print(f"{RED}❌ Entrada inválida. Intenta de nuevo.{NC}")
        
        print(f"{GREEN}✅ Dimensiones configuradas: {width}x{height} píxeles{NC}")
        return width, height
    
    def validate_platform(self, platform):
        """Validar plataforma especificada"""
        if platform not in self.platforms:
            sys.exit(f"{RED}❌ Error: Plataforma desconocida '{platform}'. Plataformas válidas: {', '.join(self.platforms)}.{NC}")
        return True
        
    def validate_mode(self, platform, mode):
        """Validar modo especificado"""
        platform_data = self.platforms_data[platform]
        
        if 'modes' not in platform_data:
            sys.exit(f"{RED}❌ Error: La plataforma {platform} no tiene modos definidos.{NC}")
            
        if mode not in platform_data['modes']:
            sys.exit(f"{RED}❌ Error: Modo '{mode}' inválido para la plataforma '{platform}'.{NC}")
        
        return True
    
    def validate_dimensions(self, platform, width, height):
        """Validar dimensiones especificadas"""
        platform_data = self.platforms_data[platform]
        max_width = platform_data['max_width']
        max_height = platform_data['max_height']
        
        if width < 8 or width > max_width or height < 8 or height > max_height:
            sys.exit(f"{RED}❌ Error: Dimensiones no válidas. Deben estar entre 8 y {max_width}x{max_height}.{NC}")
        
        return True
    
    def prompt_for_sprite_description(self):
        """Solicitar descripción del sprite"""
        print(f"\n{BLUE}💬 Describe tu sprite:{NC}")
        while True:
            prompt = input("Descripción: ").strip()
            if prompt:
                return prompt
            print(f"{RED}❌ La descripción no puede estar vacía. Intenta de nuevo.{NC}")
    
    def prompt_for_negative(self):
        """Solicitar prompt negativo (opcional)"""
        print(f"\n{BLUE}🚫 Características a evitar (opcional, pulsa Enter para omitir):{NC}")
        negative = input("Prompt negativo: ").strip()
        if negative:
            print(f"{GREEN}✅ Prompt negativo configurado.{NC}")
        else:
            print(f"{BLUE}ℹ️ Sin prompt negativo.{NC}")
        return negative
    
    def run_interactive(self):
        """Ejecutar modo interactivo"""
        print(f"\n{BLUE}✨ Modo Interactivo Activado{NC}")
        print("Se solicitarán los parámetros necesarios.")
        
        # Obtener plataforma
        if not self.args.platform:
            platform = self.get_platform_interactive()
        else:
            platform = self.args.platform
            self.validate_platform(platform)
            print(f"{GREEN}✅ Plataforma (argumento): {self.platforms_data[platform]['name']}{NC}")
        
        # Obtener modo
        if platform == 'amstrad_cpc' and not self.args.mode:
            mode = self.get_mode_interactive(platform)
        elif self.args.mode:
            mode = self.args.mode
            self.validate_mode(platform, mode)
            print(f"{GREEN}✅ Modo (argumento): {mode}{NC}")
        elif platform == 'spectrum':
            mode = 'default'
            print(f"{BLUE}ℹ️ Modo (automático): {mode}{NC}")
        else:
            mode = None
        
        # Obtener dimensiones
        if not self.args.width or not self.args.height:
            width, height = self.get_dimensions_interactive(platform)
        else:
            width = self.args.width
            height = self.args.height
            self.validate_dimensions(platform, width, height)
            print(f"{GREEN}✅ Dimensiones (argumento): {width}x{height} píxeles{NC}")
        
        # Obtener prompt
        if not self.args.prompt:
            prompt = self.prompt_for_sprite_description()
        else:
            prompt = self.args.prompt
            print(f"{GREEN}✅ Descripción configurada: {prompt}{NC}")
        
        # Obtener prompt negativo
        if not self.args.negative_prompt:
            negative = self.prompt_for_negative()
        else:
            negative = self.args.negative_prompt
            print(f"{GREEN}✅ Prompt negativo (argumento) configurado.{NC}")
        
        return platform, mode, width, height, prompt, negative
    
    def run_non_interactive(self):
        """Ejecutar modo no interactivo"""
        print(f"\n{BLUE}⚙️ Usando parámetros de línea de comandos.{NC}")
        
        # Verificar parámetros esenciales
        if not self.args.prompt:
            sys.exit(f"{RED}❌ Error: Falta la descripción del sprite (--prompt).{NC}")
        
        if not self.args.platform:
            sys.exit(f"{RED}❌ Error: Falta la plataforma (--platform).{NC}")
        
        platform = self.args.platform
        self.validate_platform(platform)
        
        # Asignar modo
        if platform == 'amstrad_cpc':
            if not self.args.mode:
                sys.exit(f"{RED}❌ Error: Falta el modo (--mode) para Amstrad CPC.{NC}")
            mode = self.args.mode
            self.validate_mode(platform, mode)
        elif platform == 'spectrum':
            mode = self.args.mode if self.args.mode else 'default'
        else:
            mode = None
        
        # Asignar dimensiones
        if not self.args.width or not self.args.height:
            # Usar valores por defecto de la plataforma
            width = self.platforms_data[platform]['default_width']
            height = self.platforms_data[platform]['default_height']
        else:
            width = self.args.width
            height = self.args.height
            self.validate_dimensions(platform, width, height)
        
        prompt = self.args.prompt
        negative = self.args.negative_prompt or ""
        
        return platform, mode, width, height, prompt, negative
    
    def show_summary(self, platform, mode, width, height, prompt, negative):
        """Mostrar resumen de configuración"""
        print(f"\n{BLUE}📋 Resumen Final:{NC}")
        print(f"  • Plataforma: {self.platforms_data[platform]['name']} ({platform})")
        
        # Mostrar modo si es relevante
        if platform == 'amstrad_cpc' or (platform == 'spectrum' and mode != 'default'):
            if isinstance(self.platforms_data[platform]['colors'], dict):
                colors = self.platforms_data[platform]['colors'][mode]
            else:
                colors = self.platforms_data[platform]['colors']
            print(f"  • Modo: {mode} ({colors} colores)")
        
        print(f"  • Dimensiones: {width}x{height} píxeles")
        print(f"  • Descripción: {prompt}")
        
        if negative:
            print(f"  • Prompt negativo: {negative}")
        
        print("")
        
    def ask_confirmation(self):
        """Preguntar confirmación para continuar"""
        while True:
            choice = input("¿Continuar con la generación? (s/n) [s]: ").strip().lower()
            if choice == 's' or choice == '':
                return True
            elif choice == 'n':
                print(f"{RED}Generación cancelada.{NC}")
                return False
            else:
                print(f"{RED}Respuesta no válida. Por favor, escribe 's' o 'n'.{NC}")
    
    def generate_sprite(self, platform, mode, width, height, prompt, negative):
        """Generar sprite con los parámetros especificados"""
        print(f"{BLUE}🎨 Generando sprite...{NC}")
        
        # Construir la lista de argumentos
        cmd = [
            "python3", "llm_sprites.py",
            "--prompt", str(prompt),
            "--width", str(width),
            "--height", str(height),
            "--platform", platform
        ]
        
        if platform == 'amstrad_cpc' and mode:
            cmd.extend(["--mode", mode])
        
        if negative:
            cmd.extend(["--negative-prompt", str(negative)])
        
        # Mostrar el comando que se va a ejecutar (para depuración)
        cmd_str = ' '.join([f'"{arg}"' if ' ' in str(arg) else str(arg) for arg in cmd])
        print(f"{BLUE}ℹ️ Comando: {cmd_str}{NC}")
        print("")
        
        try:
            # Ejecutar el comando asegurando que se capturan los errores
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            # Mostrar la salida del comando
            if result.stdout:
                print(result.stdout)
            print(f"\n{GREEN}✅ Sprite generado correctamente!{NC}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"\n{RED}❌ Error al generar el sprite (código de salida: {e.returncode}).{NC}")
            # Mostrar el error detallado para facilitar el diagnóstico
            if e.stdout:
                print(f"{BLUE}Salida estándar:{NC}\n{e.stdout}")
            if e.stderr:
                print(f"{RED}Error:{NC}\n{e.stderr}")
            return False
    
    def run(self):
        """Ejecutar el generador de sprites"""
        try:
          
            # Determinar modo de operación
            if self.args.interactive or not (self.args.prompt and self.args.platform):
                platform, mode, width, height, prompt, negative = self.run_interactive()
            else:
                platform, mode, width, height, prompt, negative = self.run_non_interactive()
            
            # Mostrar resumen y confirmar
            self.show_summary(platform, mode, width, height, prompt, negative)
            if not self.ask_confirmation():
                return 0
            
            # Generar sprite
            success = self.generate_sprite(platform, mode, width, height, prompt, negative)
            return 0 if success else 1
            
        except KeyboardInterrupt:
            print(f"\n{RED}Script interrumpido por el usuario.{NC}")
            return 130
        except Exception as e:
            print(f"\n{RED}❌ Error inesperado: {str(e)}{NC}")
            return 1
        finally:
            print(f"\n{BLUE}👋 ¡Gracias por usar el Generador de Sprites!{NC}")


if __name__ == "__main__":
    generator = SpriteGenerator()
    sys.exit(generator.run()) 