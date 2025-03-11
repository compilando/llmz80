# LLMZ80 - Emulador Z80 con LLM

Este proyecto implementa un generador de código para Z80 utilizando modelos de lenguaje (LLM), compatible con ZX Spectrum y Amstrad CPC.

## Requisitos del Sistema

### Sistema Operativo
- Linux (probado en Arch Linux 6.13.5)
- Otros sistemas Unix-like deberían funcionar también

### Python
1. Asegúrate de tener Python 3.8 o superior instalado:
```bash
python --version
```

2. Se recomienda crear un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate
```

3. Instalar dependencias Python:
```bash
pip install -r requirements.txt
```

### Z88DK (Compilador Z80)
1. Instalación en Arch Linux:
```bash
sudo pacman -S z88dk
```

Para otras distribuciones, consulta la [documentación oficial de Z88DK](https://github.com/z88dk/z88dk).

### SDCC (Small Device C Compiler)
Para compilar código para Amstrad CPC, necesitarás SDCC:

1. Instalación en Arch Linux:
```bash
sudo pacman -S sdcc
```

2. Instalación en Ubuntu/Debian:
```bash
sudo apt-get install sdcc
```

### hex2bin
Para convertir archivos IHX a binarios para Amstrad CPC:

1. Instalación en Arch Linux:
```bash
yay -S hex2bin
```

2. Instalación en Ubuntu/Debian:
```bash
sudo apt-get install hex2bin
```

3. Instalación manual desde fuente:
```bash
git clone https://github.com/hexdump2002/hex2bin.git
cd hex2bin
make
sudo make install
```

### CPCtelera
Para compilar código para Amstrad CPC, necesitarás CPCtelera:

1. Instalación:
```bash
git clone https://github.com/lronaldo/cpctelera
cd cpctelera
./setup.sh
```

### FUSE (Free Unix Spectrum Emulator)
1. Instalación en Arch Linux:
```bash
sudo pacman -S fuse-emulator
```

Para otras distribuciones:
- Ubuntu/Debian: `sudo apt-get install fuse-emulator-common`
- Fedora: `sudo dnf install fuse-emulator`

### RetroVirtualMachine
Para emular Amstrad CPC:

1. Descarga desde [RetroVirtualMachine](https://www.retrovirtualmachine.org/en/download)

2. Instalación en Arch Linux:
```bash
yay -S retrovirtualmachine
```

### ZEsarUX
1. Descarga la última versión desde el [sitio oficial de ZEsarUX](https://github.com/chernandezba/zesarux)

2. Instalación desde fuente:
```bash
./configure
make
sudo make install
```

## Configuración

1. Clona el repositorio:
```bash
git clone [URL_DEL_REPOSITORIO]
cd llmz80
```

2. Configura las variables de entorno necesarias (si las hay):
```bash
cp .env.example .env
# Edita .env con tus configuraciones
```

## Uso

### Generación de código para ZX Spectrum

1. Ejecuta el script principal:
```bash
python llm_z80.py
```

2. Compila el código generado:
```bash
./build.sh
```

3. Ejecuta el código en el emulador:
```bash
./build.sh --run
```

### Generación de código para Amstrad CPC

1. Ejecuta el script principal especificando la plataforma:
```bash
python llm_z80.py --platform amstrad_cpc
```

2. Compila el código generado:
```bash
./build_amstrad.sh
```

3. Ejecuta el código en el emulador:
```bash
./build_amstrad.sh
```

4. Para compilar sin ejecutar el emulador:
```bash
./build_amstrad.sh --no-emulator
```

5. Para compilar un archivo fuente específico:
```bash
./build_amstrad.sh --source=ruta/al/archivo.c
```

6. Para especificar la ruta a CPCtelera:
```bash
./build_amstrad.sh --cpctelera=/ruta/a/cpctelera
```

## Archivos de Plantilla

El proyecto utiliza archivos de plantilla para la compilación, ubicados en el directorio `templates/`:

### Plantillas para Amstrad CPC

- `templates/amstrad/Makefile`: Makefile principal para proyectos CPCtelera.
- `templates/amstrad/hex2bin.py`: Script Python para convertir archivos IHX a BIN cuando hex2bin no está disponible.
- `templates/amstrad/cfg/build_config.mk`: Configuración de compilación para proyectos CPCtelera.
- `templates/amstrad/cfg/*.mk`: Archivos de configuración adicionales para CPCtelera.

Estos archivos son utilizados por el script `build_amstrad.sh` para crear la estructura de proyecto necesaria para compilar código para Amstrad CPC.

## Estructura del Proyecto

```
.
├── build/                  # Directorio para archivos compilados
├── examples/               # Ejemplos de código
├── local/                  # Código generado por el LLM
├── templates/              # Plantillas para compilación
│   └── amstrad/            # Plantillas para Amstrad CPC
│       ├── cfg/            # Archivos de configuración para CPCtelera
│       ├── hex2bin.py      # Script para convertir IHX a BIN
│       └── Makefile        # Makefile para proyectos CPCtelera
├── .env                    # Variables de entorno (API keys)
├── .env.example            # Ejemplo de archivo .env
├── build.sh                # Script de compilación para ZX Spectrum
├── build_amstrad.sh        # Script de compilación para Amstrad CPC
├── config.yml              # Configuración del proyecto
├── install_arch.sh         # Script de instalación para Arch Linux
├── llm_z80.py              # Script principal del generador
├── requirements.txt        # Dependencias Python
└── test_examples.sh        # Script para probar ejemplos
```

## Diferencias entre ZX Spectrum y Amstrad CPC

| Característica | ZX Spectrum | Amstrad CPC |
|----------------|-------------|-------------|
| CPU | Z80A @ 3.5MHz | Z80A @ 4MHz |
| RAM | 16KB/48KB/128KB | 64KB/128KB |
| ROM | 16KB | 32KB |
| Gráficos | 256×192, 15 colores | Modos: 160×200 (16 colores), 320×200 (4 colores), 640×200 (2 colores) |
| Sonido | Beeper (48K), AY-3-8912 (128K) | AY-3-8912 |
| Almacenamiento | Casete | Casete y disco |

## Solución de problemas

### CPCtelera no encontrado
Si recibes el error "CPCtelera not found", asegúrate de que:

1. Has instalado CPCtelera correctamente siguiendo las instrucciones anteriores
2. Especifica la ruta correcta con `--cpctelera=/ruta/a/cpctelera`
3. Si lo has instalado en tu directorio home, verifica que la ruta sea `$HOME/cpctelera`

### Error en el script de configuración de CPCtelera
Si recibes el error "CPCtelera configuration script not found", verifica:

1. Que el archivo `cpctelera-config.sh` existe en la instalación de CPCtelera:
   ```bash
   find ~/cpctelera -name cpctelera-config.sh
   ```

2. Si el archivo existe pero en una ubicación diferente (por ejemplo, en un subdirectorio), especifica la ruta completa:
   ```bash
   ./build_amstrad.sh --cpctelera=/ruta/completa/a/cpctelera
   ```

3. Si el archivo no existe, es posible que la instalación esté incompleta. Reinstala CPCtelera siguiendo las instrucciones detalladas.

### Herramientas de compilación no encontradas
Si recibes errores sobre herramientas faltantes:

1. Para SDCC:
   ```bash
   sudo pacman -S sdcc  # Arch Linux
   sudo apt-get install sdcc  # Ubuntu/Debian
   ```

2. Para hex2bin:
   ```bash
   yay -S hex2bin  # Arch Linux (AUR)
   ```
   
   O instálalo manualmente:
   ```bash
   git clone https://github.com/hexdump2002/hex2bin.git
   cd hex2bin
   make
   sudo make install
   ```

### RetroVirtualMachine no encontrado
Si RetroVirtualMachine no está instalado o no está en el PATH:

1. Instálalo desde su [sitio oficial](https://www.retrovirtualmachine.org/en/download)
2. En Arch Linux, puedes instalarlo desde AUR: `yay -S retrovirtualmachine`
3. Alternativamente, puedes usar cualquier otro emulador de Amstrad CPC para abrir el archivo .dsk generado

## Contribuir

1. Haz fork del repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

[Especificar la licencia del proyecto]

## Contacto

[Información de contacto del mantenedor] 