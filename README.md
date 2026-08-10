# LLMZ80 🎮

> Generador inteligente de código C para microordenadores clásicos Z80 usando IA, RAG y bucles de compilación

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--5-412991.svg)](https://openai.com/)
[![Qdrant](https://img.shields.io/badge/Qdrant-Vector%20DB-DC244C.svg)](https://qdrant.tech/)

LLMZ80 es un generador inteligente de código C para microordenadores clásicos Z80 (ZX Spectrum y Amstrad CPC) que utiliza **Large Language Models** (LLMs), **embeddings**, **RAG** (Retrieval Augmented Generation), validación previa y corrección automática para generar código compilable desde descripciones en lenguaje natural.

## Estado del Proyecto

El flujo principal actual genera **C**:

- ZX Spectrum mediante Z88DK.
- Amstrad CPC mediante CPCtelera, SDCC y plantillas de proyecto.
- Amstrad CPC usa por defecto un contrato `main.c` autocontenido: sin includes locales ni assets externos.
- Sprites para Spectrum y modos gráficos de Amstrad CPC.
- Aprendizaje local de compilaciones exitosas y errores recurrentes.

El soporte para **ASM Z80 standalone** todavía no está implementado como flujo de primera clase. La configuración ya contempla ensambladores (`z80asm`) y el repositorio contiene ejemplos con ensamblador dentro de la colección CPCtelera, pero el generador principal, los prompts y la validación están orientados a C. Ver [Informe: Retro Vibe-Coding ASM Z80](docs/RETRO_VIBE_CODING_GAP_REPORT.md) para el análisis de gaps y el plan de mejora.

La revisión más reciente del flujo C, sus causas raíz y evidencia de compilación
está en [Auditoría fundacional 2026-08-09](docs/FOUNDATIONAL_AUDIT_2026-08-09.md).
El trabajo y la evidencia de mejora se registran en
[Generation quality roadmap](docs/GENERATION_QUALITY_ROADMAP.md).

## ✨ Características Principales

- 🤖 **Generación de código con IA**: Usa modelos OpenAI configurables para crear código C orientado a Z80
- 🔍 **RAG fiable**: catálogo local determinista de programas compilables, ampliable con Qdrant
- 🎯 **Compilación automática**: Compila y verifica el código generado automáticamente
- 📊 **Contrato de build verificable**: Cada ejecución guarda `build_report.json`
  con advertencias clasificadas, artefactos y tamaño del programa; una opción
  ignorada o un artefacto vacío ya no cuentan como éxito
- 🔧 **Corrección inteligente**: Si la compilación falla, el LLM sugiere correcciones
- 🧪 **Validación previa**: Reglas locales detectan errores comunes antes de compilar
- 🧱 **Contrato CPCtelera**: En Amstrad CPC se fuerza `main.c` autocontenido y APIs CPCtelera conocidas
- 📈 **Aprendizaje local**: Guarda ejemplos exitosos y errores recurrentes para mejorar iteraciones futuras
- 🎨 **Generación de sprites**: Crea sprites desde descripciones o imágenes
- 📚 **Base de conocimiento**: Aprende de ejemplos de código existentes
- 🚀 **Dos plataformas**: ZX Spectrum 48K y Amstrad CPC 464/6128

## 📋 Tabla de Contenidos

- [Requisitos Previos](#requisitos-previos)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Uso](#uso)
- [Ejemplos](#ejemplos)
- [ASM Z80 y Retro Vibe-Coding](#asm-z80-y-retro-vibe-coding)
- [Arquitectura](#arquitectura)
- [Contribuir](#contribuir)
- [Licencia](#licencia)
- [Recursos](#recursos)


## 🎯 Requisitos Previos

### Software Requerido

| Componente | Descripción | Instalación |
|------------|-------------|-------------|
| **Python 3.10+** | Lenguaje principal | [python.org](https://www.python.org/downloads/) |
| **Docker** | Opcional, sólo para ampliar el RAG con Qdrant | [docker.com](https://www.docker.com/) |
| **Git** | Control de versiones | `sudo pacman -S git` |

### Herramientas de Desarrollo Z80

#### Para ZX Spectrum

| Herramienta | Descripción | Instalación |
|-------------|-------------|-------------|
| **Z88DK** | Kit de desarrollo para Z80 | `sudo pacman -S z88dk` |
| **Fuse** | Emulador ZX Spectrum | `sudo pacman -S fuse` |

Otros emuladores compatibles: ZEsarUX, ZXSpin

#### Para Amstrad CPC

| Herramienta | Descripción | Instalación |
|-------------|-------------|-------------|
| **SDCC** | Small Device C Compiler | `sudo pacman -S sdcc` |
| **CPCtelera** | Framework de desarrollo CPC | Ver [instalación CPCtelera](#instalación-de-cpctelera) |
| **Caprice32** | Emulador Amstrad CPC | `sudo pacman -S caprice32` |
| **pasmo** | Ensamblador Z80 recomendado para futuros flujos ASM standalone | Opcional |

Otros emuladores compatibles: RetroVirtualMachine, XRoar

### API Keys Necesarias

- **OpenAI API Key**: Para generación de código (requerido)
- **Gemini API Key**: Para generación de sprites (opcional)
- **Google Cloud**: Para Vertex AI (opcional)

## 🚀 Instalación

### 1. Clonar el Repositorio

```bash
git clone https://github.com/compilando/llmz80.git
cd llmz80
```

### 2. Preparar el entorno Python

```bash
# Crea .venv e instala las dependencias sin modificar el Python del sistema
make setup
```

No es necesario activar el entorno: los targets del Makefile utilizan
`.venv/bin/python` directamente. El proyecto admite Python 3.10–3.13; si el
`python3` del sistema es más nuevo, el Makefile busca automáticamente una
versión compatible instalada.

### 3. Instalar Herramientas de Desarrollo

#### Instalación de Z88DK (ZX Spectrum)

```bash
# Arch Linux
sudo pacman -S z88dk

# Ubuntu/Debian
sudo apt-get install z88dk

# MacOS
brew install z88dk

# Desde código fuente
git clone https://github.com/z88dk/z88dk.git
cd z88dk
export BUILD_SDCC=1
./build.sh
```

#### Instalación de CPCtelera (Amstrad CPC)

```bash
# Clonar el repositorio
git clone https://github.com/lronaldo/cpctelera.git ~/cpctelera

# Compilar e instalar
cd ~/cpctelera
./setup.sh

# Configurar variables de entorno
echo 'export CPCT_PATH=~/cpctelera' >> ~/.bashrc
source ~/.bashrc
```

### 5. Iniciar Qdrant (opcional)

La generación funciona sin Qdrant: siempre usa el catálogo local de entrypoints compilables. Qdrant añade búsqueda vectorial y memoria semántica, pero no es una dependencia del flujo base.

```bash
# Con Docker (recomendado)
docker run -p 6333:6333 -p 6334:6334 \
  -v $(pwd)/local/qdrant_storage:/qdrant/storage \
  qdrant/qdrant:v1.18.3

# O instalar localmente
# Ver: https://qdrant.tech/documentation/guides/installation/
```

## ⚙️ Configuración

### 1. Variables de Entorno

Copia el archivo de ejemplo y configura tus API keys:

```bash
cp .env.example .env
nano .env  # o tu editor preferido
```

Contenido de `.env`:

```bash
# Requerido
OPENAI_API_KEY=sk-proj-...

# Opcional (para generación de sprites)
GEMINI_API_KEY=...
GOOGLE_CLOUD_PROJECT=...
```

### 2. Configuración Principal (config.yml)

El archivo `config.yml` contiene la configuración del sistema:

```yaml
openai:
  model: gpt-5               # Modelo de OpenAI
  temperature: 0.3           # Ignorado por modelos reasoning; útil para fallback
  max_tokens: 16384          # Tokens máximos
  reasoning_effort: medium   # Esfuerzo de razonamiento para modelos reasoning
  embedding_model: text-embedding-3-small

examples:
  max_examples: 8            # Programas completos en el prompt
  truncate_size: 50000       # Tamaño máximo por ejemplo

generation:
  max_attempts: 4            # Build inicial + correcciones con diagnóstico real

embeddings:
  cache_dir: "local/embeddings"
  max_chunk_size: 15000
```

### 3. Poblar Base de Datos Vectorial

Inicializa Qdrant con los ejemplos de código:

```bash
# Para ZX Spectrum
python llm_z80.py --platform spectrum --populate-db

# Para Amstrad CPC
python llm_z80.py --platform amstrad_cpc --populate-db
```

## 📖 Uso

### Generación Básica de Código

#### Modo Interactivo

```bash
# ZX Spectrum
python llm_z80.py --platform spectrum

# Amstrad CPC
python llm_z80.py --platform amstrad_cpc
```

El programa te pedirá que ingreses tu prompt.

#### Con Prompt Directo

```bash
python llm_z80.py --platform spectrum \
  --prompt "Create a bouncing ball that changes color when it hits the border"

python llm_z80.py --platform amstrad_cpc \
  --prompt "Display a sprite of a spaceship that moves with keyboard arrows"
```

### Opciones Avanzadas

```bash
# Con nivel de log debug
python llm_z80.py --platform spectrum --log-level DEBUG \
  --prompt "Your prompt here"

# Sin Qdrant/embeddings; conserva el catálogo local determinista
python llm_z80.py --platform spectrum --no-embeddings \
  --prompt "Your prompt here"

# Limpiar caché de embeddings
python llm_z80.py --platform spectrum --clear-cache

# Reconstruir completamente los embeddings
python llm_z80.py --platform spectrum --rebuild-embeddings
```

### Generación de Sprites

```bash
# ZX Spectrum (8 colores)
./generate_sprite.sh spectrum "robot futurista" 16 16

# Amstrad CPC Mode 0 (16 colores)
./generate_sprite.sh amstrad_cpc_mode0 "dragon fire" 16 16

# Amstrad CPC Mode 1 (4 colores)
./generate_sprite.sh amstrad_cpc_mode1 "treasure chest" 16 16
```

### Compilar Ejemplos Existentes

```bash
# Listar ejemplos disponibles
./build_spectrum.sh --list-examples
./build_amstrad.sh --list-examples

# Compilar y ejecutar un ejemplo
./build_spectrum.sh --example=01_border
./build_amstrad.sh --example=text_example

# Compilar sin ejecutar el emulador
./build_spectrum.sh --example=01_border --no-emulator

# Especificar emulador diferente
./build_spectrum.sh --example=01_border --emulator=zesarux
```

## 💡 Ejemplos

### Ejemplo 1: Programa Simple para ZX Spectrum

```bash
python llm_z80.py --platform spectrum \
  --prompt "Change the border color to red and print 'HELLO WORLD' in the center of the screen"
```

**Salida**: Archivo `.tap` en `local/YYYY-MM-DD_HHMMSS_change-the-border/`

### Ejemplo 2: Juego para Amstrad CPC

```bash
python llm_z80.py --platform amstrad_cpc \
  --prompt "Create a simple game where a player-controlled sprite can move left and right at the bottom of the screen, and random sprites fall from the top. If a falling sprite touches the player, show GAME OVER. Use Mode 1 graphics."
```

### Ejemplo 3: Gráficos Animados

```bash
python llm_z80.py --platform spectrum \
  --prompt "Draw a sine wave animation that scrolls across the screen horizontally"
```

### Ejemplo 4: Control de Teclado

```bash
python llm_z80.py --platform amstrad_cpc \
  --prompt "Create a program where pressing keys Q, A, O, P changes the border to different colors in Mode 0"
```

## ASM Z80 y Retro Vibe-Coding

El artículo "Cómo crear con Vibe Coding código ASM para AMSTRAD CPC 6128" describe un flujo manual para generar ASM Z80, compilarlo con `pasmo`, empaquetarlo como BIN con cabecera AMSDOS en un DSK y probarlo en CPCBox o emuladores equivalentes. Ese flujo encaja con la dirección natural de LLMZ80, pero hoy el proyecto todavía no lo automatiza.

Puntos importantes para contribuciones ASM:

- Separar claramente `amstrad_cpc` en C/CPCtelera de un futuro perfil `amstrad_cpc_asm`.
- Usar un prompt de sistema específico para ASM Z80 CPC6128 con `ORG &4000`, `LOAD`/`CALL &4000`, firmware CPC documentado y límites de VRAM.
- Añadir validadores sintácticos y semánticos para instrucciones Z80 estándar, direcciones firmware, rangos de memoria y retorno seguro.
- Automatizar `pasmo`, cabecera AMSDOS, creación de DSK y prueba en emulador.
- Alimentar RAG con ejemplos ASM CPC reales y con fallos corregidos.

El detalle completo está en [docs/RETRO_VIBE_CODING_GAP_REPORT.md](docs/RETRO_VIBE_CODING_GAP_REPORT.md).

## 🏗️ Arquitectura

### Estructura del Proyecto

```
llmz80/
├── .cline/                  # Documentación para AI assistants
├── llmz80/                  # Código principal del paquete
│   ├── api/                 # API de generación
│   │   └── generator.py     # LLMZ80Generator (clase principal)
│   ├── core/                # Módulos core
│   │   ├── example_catalog.py # RAG local centrado en programas compilables
│   │   ├── embeddings.py    # Gestión de embeddings
│   │   ├── cache_manager.py # Caché de embeddings
│   │   └── examples_loader.py # Carga de ejemplos
│   └── utils/               # Utilidades
│       ├── config.py        # Configuración
│       ├── logger.py        # Logging
│       └── helpers.py       # Funciones auxiliares
├── generators/              # Generadores de sprites
│   ├── openai_generator.py  # DALL-E
│   ├── gemini_generator.py  # Google Gemini
│   └── vertexai_generator.py # Vertex AI
├── examples/                # Ejemplos de código
│   ├── spectrum/            # ZX Spectrum (Z88DK)
│   ├── amstrad_cpc/         # Base Amstrad CPC (CPCtelera)
│   └── amstrad_cpc_level2/  # Proyectos CPC medium/advanced también indexados
├── resources/               # Recursos
│   ├── platforms.yml        # Configuración de plataformas
│   └── system_prompt_*.txt  # Prompts del sistema
├── sprites/                 # Sprites generados
├── templates/               # Plantillas de compilación
├── build/                   # Archivos compilados (gitignored)
├── local/                   # Datos locales (gitignored)
├── config.yml               # Configuración principal
├── llm_z80.py              # Script principal
├── vector_db.py            # Integración Qdrant
├── build_spectrum.sh        # Compilador ZX Spectrum
└── build_amstrad.sh         # Compilador Amstrad CPC
```

### Flujo de Trabajo

```
1. Usuario ingresa prompt
   ↓
2. Se crea y valida un GenerationSpec con comportamiento y presupuestos
   ↓
3. Catálogo local selecciona evidencia por capacidades (Qdrant es opcional)
   ↓
4. Compone entrypoints completos, runtime y arquetipo sin truncar C
   ↓
5. El modelo genera main.c o un proyecto controlado
   ↓
6. Validación sintáctica, de APIs, semántica y memoria
   ↓
7. Compilación estricta (SDCC/ZCC) e informe de recursos
   ↓
8. Smoke test portable o headless y selección opcional de candidatos
   ↓
9. Sólo los resultados con evidencia de calidad entran al aprendizaje/RAG
```

### Tecnologías Utilizadas

- **Modelos OpenAI configurables**: Generación y corrección de código
- **OpenAI Embeddings**: text-embedding-3-small para vectorización
- **Qdrant**: Base de datos vectorial para RAG
- **Z88DK**: Compilador C para ZX Spectrum
- **SDCC + CPCtelera**: Compilador C para Amstrad CPC
- **Python 3.10+**: Lenguaje principal
- **Docker**: Contenedorización de Qdrant

### Verificación del catálogo

Antes de aceptar cambios en ejemplos o toolchains, compila exactamente todos los programas que el RAG puede recuperar:

```bash
make audit-examples
```

Las pruebas de integración también compilan contratos mínimos reales y se omiten automáticamente si una toolchain no está instalada.
Un proyecto incompatible con la toolchain soportada puede incluir
`.llmz80-rag-exclude` con el motivo; seguirá en la biblioteca, pero no podrá
contaminar el contexto de generación hasta que vuelva a compilar.

El gate determinista completo ejecuta las pruebas, compila los 53 entrypoints y
genera el scorecard offline sin consumir API:

```bash
make install-dev
make quality-gate
```

Para evaluar ejecuciones guardadas o lanzar de forma deliberada una muestra live:

```bash
make benchmark
.venv/bin/python scripts/evaluate_generation.py --live --allow-api --limit 2 \
  --output local/quality/live-sample
```

La ejecución live nunca se activa implícitamente ni reemplaza el baseline.

## Uso

### Calidad, candidatos y assets

El modo normal conserva un único `main.c`. Para prompts complejos se pueden
generar hasta tres candidatos; todos se compilan y validan, y se selecciona el
mejor por evidencia, no por opinión del modelo:

```bash
make generate-spectrum PROMPT="Un juego de plataformas con marcador" \
  GENERATOR_ARGS="--candidates 3"
```

El modo proyecto acepta imágenes, genera `src/assets.c`, `src/assets.h` y el
runtime fijo, y convierte los píxeles al formato nativo de forma determinista:

```bash
make generate-cpc PROMPT="Mueve el héroe por la pantalla" \
  GENERATOR_ARGS="--output-mode project --asset art/hero.png"
```

Cada directorio de salida incluye, según corresponda,
`generation_spec.json`, `prompt_context.json`, `generation_metrics.json`,
`semantic_report.json`, `build_report.json`, `emulator_report.json` y
`candidate_selection.json`.

La comprobación estática sólo valida la estructura de TAP/DSK y nunca cuenta
como evidencia de ejecución. Para arrancar el programa, capturar framebuffers e
inyectar un control real en ZEsarUX o Caprice32:

```bash
make smoke RUN_DIR=local/MI_EJECUCION SMOKE_ARGS=--full
```

El comando falla si el binario no llega a cargar, la pantalla útil queda vacía o,
cuando el código declara controles/actualizaciones, no existe una transición
observable. Las capturas y `emulator_report.json` se guardan dentro del
directorio de la ejecución.

También puede exigirse durante una generación. Los objetivos `make run-spectrum`
y `make run-cpc` ya lo hacen automáticamente antes de abrir el emulador:

```bash
make generate-cpc PROMPT="Una pulga que salta" GENERATOR_ARGS="--runtime-check"
```

Tras superar esa comprobación, `make run-cpc` monta `output.dsk` en Caprice32 e
inyecta `run"program.bin"` después del arranque del firmware; no es necesario
escribir el comando manualmente en BASIC.

### Compilación y Ejecución

#### Amstrad CPC
```bash
# Listar ejemplos disponibles
./build_amstrad.sh --list-examples

# Compilar y ejecutar un ejemplo
./build_amstrad.sh --example=text_example

# Compilar sin ejecutar el emulador
./build_amstrad.sh --example=text_example --no-emulator

# Especificar un emulador diferente
./build_amstrad.sh --example=text_example --emulator=cap32
```

#### ZX Spectrum
```bash
# Listar ejemplos disponibles
./build_spectrum.sh --list-examples

# Compilar y ejecutar un ejemplo
./build_spectrum.sh --example=text_example

# Compilar sin ejecutar el emulador
./build_spectrum.sh --example=text_example --no-emulator

# Especificar un emulador diferente
./build_spectrum.sh --example=text_example --emulator=fuse
```

### Creación de Nuevos Ejemplos

#### Amstrad CPC
```bash
# Crear estructura para un nuevo ejemplo
./build_amstrad.sh --create-example=mi_ejemplo
```

#### ZX Spectrum
```bash
# Crear estructura para un nuevo ejemplo
./build_spectrum.sh --create-example=mi_ejemplo
```

## 🔧 Solución de Problemas

### Error: No se puede conectar a Qdrant

No bloquea la generación. Usa `--no-embeddings` para trabajar únicamente con el catálogo local, o inicia Qdrant si quieres búsqueda vectorial:

```bash
# Verificar que Qdrant está corriendo
docker ps | grep qdrant

# Iniciar Qdrant si no está corriendo
docker run -p 6333:6333 qdrant/qdrant

# Repoblar la base de datos
python llm_z80.py --platform spectrum --populate-db
```

### Error: API Key de OpenAI inválida

```bash
# Verificar que .env existe y tiene la clave correcta
cat .env | grep OPENAI_API_KEY

# La clave debe empezar con sk-proj- o sk-
# Obtener una clave en: https://platform.openai.com/api-keys
```

### Error de Compilación SDCC/Z88DK

```bash
# Verificar instalación
which sdcc
which zcc

# Ver versión
sdcc --version
zcc --version

# Para Amstrad: Verificar CPCT_PATH
echo $CPCT_PATH

# Debe apuntar a la instalación de CPCtelera
```

### Error: Cache de Embeddings Corrupto

```bash
# Reparar caché
python llm_z80.py --platform spectrum --repair-cache

# O limpiar y reconstruir completamente
python llm_z80.py --platform spectrum --rebuild-embeddings
```

### Emulador no se Abre

```bash
# Verificar que el emulador está instalado
which fuse  # Para Spectrum
which cap32  # Para Amstrad

# Compilar sin ejecutar emulador
./build_spectrum.sh --example=01_border --no-emulator

# El archivo .tap estará en el directorio build/
```

### Problemas con Sprites

```bash
# Verificar que tienes las API keys necesarias
cat .env | grep GEMINI_API_KEY

# Usar generador específico
./generate_sprite.sh spectrum "robot" 16 16 openai
```

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Por favor lee [CONTRIBUTING.md](CONTRIBUTING.md) para detalles sobre nuestro código de conducta y el proceso para enviar pull requests.

### Áreas que Necesitan Ayuda

- 🧪 Tests unitarios y de integración
- 📚 Más ejemplos de código para ambas plataformas
- 🧩 Flujo ASM Z80 standalone para Amstrad CPC
- 🌐 Documentación en otros idiomas
- 🎨 Mejoras en generación de sprites
- ⚡ Optimizaciones de rendimiento
- 🔧 Soporte para más modelos de LLM

### Desarrollo Local

```bash
# Fork y clonar
git clone https://github.com/TU_USUARIO/llmz80.git

# Crear rama
git checkout -b feature/nueva-funcionalidad

# Hacer cambios y commit
git commit -m "feat: añadir nueva funcionalidad"

# Push y crear PR
git push origin feature/nueva-funcionalidad
```

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 🙏 Agradecimientos

- **OpenAI** por los modelos de generación y la API de embeddings
- **Qdrant** por la excelente base de datos vectorial
- **Z88DK Team** por el kit de desarrollo Z80
- **CPCtelera** ([@FranGallegoBR](https://github.com/lronaldo)) por el framework de Amstrad CPC
- Comunidad retro de ZX Spectrum y Amstrad CPC

## 📚 Recursos

### Documentación del Proyecto
- [Guía de Contribución](CONTRIBUTING.md)
- [Documentación para AI Assistants](.cline/cline_docs.md)
- [Reglas de Cursor](.cursorrules)

### Z80 y Retro Computing
- [Z88DK Documentation](https://github.com/z88dk/z88dk/wiki)
- [CPCtelera API Reference](https://lronaldo.github.io/cpctelera/)
- [World of Spectrum](https://worldofspectrum.org/)
- [CPC Wiki](https://www.cpcwiki.eu/)

### APIs y Herramientas
- [OpenAI Platform](https://platform.openai.com/docs/)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [SDCC Compiler](http://sdcc.sourceforge.net/)

## 📞 Soporte

- 🐛 [Reportar un Bug](https://github.com/compilando/llmz80/issues/new?labels=bug)
- 💡 [Solicitar una Funcionalidad](https://github.com/compilando/llmz80/issues/new?labels=enhancement)
- 💬 [Discusiones](https://github.com/compilando/llmz80/discussions)

## 🌟 Star History

Si este proyecto te resulta útil, ¡considera darle una estrella! ⭐

---

**Hecho con ❤️ para la comunidad retro**
