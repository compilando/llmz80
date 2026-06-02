# LLMZ80 - Documentación para Cline/Cursor

## Descripción del Proyecto

LLMZ80 es un generador inteligente de código C para microordenadores clásicos Z80 (ZX Spectrum y Amstrad CPC) que utiliza LLMs para generar código compilable y funcional.

## Arquitectura del Sistema

### Componentes Principales

1. **API Generator** (`llmz80/api/generator.py`)
   - Clase principal: `LLMZ80Generator`
   - Gestiona la generación de código usando OpenAI GPT-4
   - Integra búsqueda semántica con Qdrant para RAG
   - Compila automáticamente y sugiere correcciones

2. **Core Modules** (`llmz80/core/`)
   - `embeddings.py`: Gestión de embeddings con OpenAI
   - `cache_manager.py`: Caché de embeddings para optimización
   - `examples_loader.py`: Carga y gestión de ejemplos de código

3. **Vector Database** (`vector_db.py`)
   - Integración con Qdrant para búsqueda semántica
   - Almacena embeddings de ejemplos con metadatos
   - Busca ejemplos relevantes basados en el prompt del usuario

4. **Generators** (`generators/`)
   - Sistema modular para generar sprites desde imágenes
   - Soporta OpenAI DALL-E, Gemini y Vertex AI

5. **Scripts de Compilación**
   - `build_amstrad.sh`: Compilación para Amstrad CPC con CPCtelera
   - `build_spectrum.sh`: Compilación para ZX Spectrum con Z88DK

## Flujo de Trabajo Principal

```
Usuario → Prompt → LLMZ80Generator → Búsqueda Semántica (Qdrant) 
    ↓
Ejemplos Relevantes + System Prompt + User Request
    ↓
OpenAI GPT-4 → Código C Generado
    ↓
Compilador (SDCC/ZCC) → Verificación
    ↓
Si falla → LLM sugiere corrección
    ↓
Archivo .tap/.dsk para emulador
```

## Plataformas Soportadas

### ZX Spectrum 48K
- **Compilador**: Z88DK (`zcc +zx`)
- **Salida**: Archivo .tap
- **Emuladores**: Fuse, ZEsarUX, ZXSpin
- **API**: Z88DK C library

### Amstrad CPC 464/6128
- **Compilador**: SDCC + CPCtelera
- **Salida**: Archivo .dsk
- **Emuladores**: Caprice32, RetroVirtualMachine
- **API**: CPCtelera framework

## Variables de Entorno Necesarias

```bash
# Archivo .env (copiar de .env.example)
OPENAI_API_KEY=sk-...                    # Requerido para generación de código
GEMINI_API_KEY=...                       # Opcional para sprites con Gemini
GOOGLE_CLOUD_PROJECT=...                 # Opcional para Vertex AI
```

## Configuración Principal (config.yml)

```yaml
openai:
  model: gpt-4o                          # Modelo de OpenAI
  temperature: 0.3                       # Creatividad (0.0-1.0)
  max_tokens: 8096                       # Tokens máximos de respuesta
  embedding_model: text-embedding-3-small # Modelo para embeddings

examples:
  max_examples: 15                       # Ejemplos a incluir en el prompt
  truncate_size: 50000                   # Tamaño máximo por ejemplo

embeddings:
  cache_dir: "local/embeddings"          # Caché de embeddings
  max_chunk_size: 15000                  # Tamaño máximo de chunk
```

## Comandos Principales

### Generar Código
```bash
# Interactivo
python llm_z80.py --platform spectrum

# Con prompt directo
python llm_z80.py --platform spectrum --prompt "Create a game with a bouncing ball"

# Para Amstrad CPC
python llm_z80.py --platform amstrad_cpc --prompt "Draw a sprite on screen"
```

### Gestión de Base de Datos Vectorial
```bash
# Poblar Qdrant con ejemplos
python llm_z80.py --platform spectrum --populate-db

# Describir un archivo de código
python llm_z80.py --platform spectrum --describe-code --file examples/spectrum/01_border.c
```

### Generar Sprites
```bash
# Spectrum
./generate_sprite.sh spectrum "robot futurista" 16 16

# Amstrad CPC Mode 0
./generate_sprite.sh amstrad_cpc_mode0 "dragon" 16 16
```

### Compilar Ejemplos
```bash
# Spectrum
./build_spectrum.sh --example=01_border
./build_spectrum.sh --list-examples

# Amstrad CPC
./build_amstrad.sh --example=text_example
./build_amstrad.sh --no-emulator --example=graphics
```

## Estructura de Directorios

```
llmz80/
├── .cline/                  # Documentación para AI assistants
├── llmz80/                  # Código principal del paquete
│   ├── api/                 # API de generación
│   ├── core/                # Módulos core (embeddings, cache, examples)
│   └── utils/               # Utilidades (config, logger, helpers)
├── generators/              # Generadores de sprites
├── examples/                # Ejemplos de código por plataforma
│   ├── spectrum/            # Ejemplos ZX Spectrum
│   └── amstrad_cpc/         # Ejemplos Amstrad CPC
├── build/                   # Archivos compilados (gitignored)
├── local/                   # Datos locales, logs, cache (gitignored)
├── resources/               # Recursos (prompts, configuraciones)
├── sprites/                 # Sprites generados
└── templates/               # Plantillas de compilación
```

## Convenciones de Código

### Python
- **Estilo**: PEP 8
- **Logging**: Usar el logger configurado, no `print()`
- **Type Hints**: Preferir siempre que sea posible
- **Docstrings**: Formato Google Style

### Ejemplos de Código C
- Incluir comentario `// Description:` en inglés
- Incluir comentario `// Descripcion:` en español (sin tilde en el comentario)
- Código autocontenido y compilable
- Seguir convenciones de la plataforma (Z88DK o CPCtelera)

## Sistema de Caché

### Embeddings Cache
- Ubicación: `local/embeddings/{platform}/`
- Formato: JSON con metadatos y vector numpy
- Limpieza: `--clear-cache` o `--rebuild-embeddings`

### Qdrant
- Host: localhost:6333 (por defecto)
- Collections: `spectrum`, `amstrad_cpc`
- Datos: embeddings + source_code + description

## Desarrollo y Testing

### Instalación para Desarrollo
```bash
# Clonar repositorio
git clone https://github.com/compilando/llmz80.git
cd llmz80

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus API keys

# Instalar herramientas de desarrollo
# SDCC, Z88DK, CPCtelera según plataforma
```

### Debugging
```bash
# Modo debug
python llm_z80.py --platform spectrum --log-level DEBUG --prompt "test"

# Verificar caché
python llm_z80.py --platform spectrum --repair-cache

# Probar embedding de archivo
python llm_z80.py --platform spectrum --test-file examples/spectrum/01_border.c
```

## Problemas Comunes

### Error: No se conecta a Qdrant
```bash
# Iniciar Qdrant con Docker
docker run -p 6333:6333 qdrant/qdrant

# O inicializar embeddings
python init_embeddings.py
```

### Error de compilación SDCC/Z88DK
- Verificar instalación: `which sdcc`, `which zcc`
- Verificar PATH incluye los compiladores
- Para Amstrad: Verificar CPCT_PATH en build_amstrad.sh

### Error de API Key
```bash
# Verificar .env
cat .env | grep OPENAI_API_KEY

# Debe existir y ser válida
OPENAI_API_KEY=sk-proj-...
```

## Contribuir

1. Fork del repositorio
2. Crear rama feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -m 'Añadir nueva funcionalidad'`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

## Recursos Adicionales

- **Z88DK Wiki**: https://github.com/z88dk/z88dk/wiki
- **CPCtelera Docs**: https://lronaldo.github.io/cpctelera/
- **Qdrant Docs**: https://qdrant.tech/documentation/
- **OpenAI API**: https://platform.openai.com/docs/

## Notas para AI Coding Assistants

### Al Modificar Código
- Respetar arquitectura modular existente
- Usar logging en lugar de print() excepto en scripts shell
- Mantener compatibilidad con ambas plataformas
- Actualizar documentación si cambia API

### Al Añadir Funcionalidades
- Seguir patrón de configuración en config.yml
- Añadir ejemplos en directorio correspondiente
- Documentar en README y aquí
- Considerar impacto en caché de embeddings

### Al Corregir Bugs
- Identificar si es específico de plataforma
- Verificar no romper compatibilidad con ejemplos existentes
- Añadir logging para debugging
- Considerar añadir tests unitarios
