# LLMZ80 - Emulador Z80 con LLM

Este proyecto implementa un generador de código para Z80 utilizando modelos de lenguaje (LLM).

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

### FUSE (Free Unix Spectrum Emulator)
1. Instalación en Arch Linux:
```bash
sudo pacman -S fuse-emulator
```

Para otras distribuciones:
- Ubuntu/Debian: `sudo apt-get install fuse-emulator-common`
- Fedora: `sudo dnf install fuse-emulator`

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

[Instrucciones específicas de uso del proyecto]

## Estructura del Proyecto

```
llmz80/
├── src/           # Código fuente principal
├── tests/         # Tests unitarios y de integración
├── docs/          # Documentación adicional
└── examples/      # Ejemplos de uso
```

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