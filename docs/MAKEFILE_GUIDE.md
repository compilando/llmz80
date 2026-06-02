# 📘 Guía del Makefile de LLMZ80

El Makefile de LLMZ80 proporciona comandos convenientes para todas las tareas principales del proyecto.

## 🚀 Inicio Rápido

```bash
# Ver todos los comandos disponibles
make help

# Configuración inicial completa
make setup

# Verificar entorno
make check-env
```

## 📦 Instalación

```bash
# Instalar dependencias de producción
make install

# Instalar dependencias de desarrollo
make install-dev

# Configuración inicial completa (crea .env, directorios, etc.)
make setup
```

## 🎮 Generación de Código

### Modo con Prompt Directo

```bash
# ZX Spectrum
make generate-spectrum PROMPT="crear hello world"
make generate-spectrum PROMPT="crear juego de snake"

# Amstrad CPC
make generate-cpc PROMPT="crear demo gráfica"
make generate-cpc PROMPT="mostrar sprites en modo 0"
```

### Modo Interactivo

```bash
# ZX Spectrum (preguntará el prompt)
make interactive-spectrum

# Amstrad CPC (preguntará el prompt)
make interactive-cpc
```

### Ejemplos Rápidos

```bash
# Hello World
make example-hello-spectrum
make example-hello-cpc

# Juego Snake (ZX Spectrum)
make example-game-spectrum

# Demo gráfica (Amstrad CPC)
make example-demo-cpc
```

## 🗄️ Base de Datos Vectorial

```bash
# Poblar BD para una plataforma
make populate-spectrum
make populate-cpc

# Poblar ambas plataformas
make populate-all
```

## 📊 Estadísticas y Aprendizaje

```bash
# Ver estadísticas
make stats-spectrum        # Estadísticas ZX Spectrum
make stats-cpc            # Estadísticas Amstrad CPC
make stats-all            # Todas las estadísticas

# Listar ejemplos exitosos
make list-examples

# Listar errores comunes registrados
make list-errors

# Ver información completa del sistema
make info
```

### Ejemplo de Salida de Estadísticas

```json
{
  "total_generations": 15,
  "successful_compilations": 13,
  "failed_compilations": 2,
  "average_attempts": 1.2,
  "average_rating": 4.1,
  "total_ratings": 8,
  "last_updated": "2025-11-20T13:45:00"
}
```

## 🧪 Desarrollo

```bash
# Formatear código
make format

# Ejecutar linter
make lint

# Ejecutar tests
make test
```

## 🔧 Mantenimiento

### Limpieza

```bash
# Limpiar archivos temporales (__pycache__, *.pyc, etc.)
make clean

# Limpiar caché de embeddings
make clean-cache

# Limpieza completa (temporales + caché)
make clean-all

# Limpiar datos de aprendizaje (¡CUIDADO! Pedirá confirmación)
make clean-learning
```

### Validación y Reparación

```bash
# Validar y reparar caché
make validate-cache

# Reconstruir embeddings
make rebuild-embeddings-spectrum
make rebuild-embeddings-cpc
make rebuild-all

# Reset completo (limpia y repuebla)
make reset-learning
```

## 🔍 Utilidades

```bash
# Verificar configuración del entorno
make check-env

# Ver versión e información
make version

# Información completa
make info
```

### Salida de `make check-env`

```
🔍 Verificando configuración del entorno...

Python:
Python 3.10.12

Variables de entorno:
  ✅ .env existe
  ✅ OPENAI_API_KEY configurada

Directorios:
  ✅ local/learning existe
  ✅ logs existe

Datos de aprendizaje:
  ✅ Estadísticas ZX Spectrum disponibles
  ⚪ Sin estadísticas Amstrad CPC
```

## 🐳 Docker (Opcional)

```bash
# Construir imagen Docker
make docker-build

# Ejecutar en Docker
make docker-run
```

## 📋 Tabla de Comandos Principales

| Categoría | Comando | Descripción |
|-----------|---------|-------------|
| **General** | `make help` | Muestra ayuda completa |
| **Instalación** | `make setup` | Configuración inicial completa |
| | `make install` | Instala dependencias |
| **Generación** | `make generate-spectrum PROMPT="..."` | Genera código Spectrum |
| | `make generate-cpc PROMPT="..."` | Genera código CPC |
| | `make interactive-spectrum` | Modo interactivo Spectrum |
| **BD Vectorial** | `make populate-all` | Puebla todas las BDs |
| **Estadísticas** | `make stats-all` | Muestra todas las stats |
| | `make list-examples` | Lista ejemplos exitosos |
| | `make list-errors` | Lista errores comunes |
| **Desarrollo** | `make test` | Ejecuta tests |
| | `make lint` | Ejecuta linter |
| | `make format` | Formatea código |
| **Mantenimiento** | `make clean` | Limpia temporales |
| | `make validate-cache` | Valida caché |
| **Utilidades** | `make check-env` | Verifica entorno |
| | `make info` | Info completa |
| **Ejemplos** | `make example-hello-spectrum` | Hello World |
| | `make example-game-spectrum` | Juego Snake |

## 💡 Casos de Uso Comunes

### Primer Uso

```bash
# 1. Instalación inicial
make setup

# 2. Editar .env con tu API key
# (el comando setup ya creó .env desde .env.example)

# 3. Poblar bases de datos
make populate-all

# 4. Generar primer código
make example-hello-spectrum
```

### Desarrollo Diario

```bash
# Generar código
make generate-spectrum PROMPT="tu idea aquí"

# Ver cómo va el aprendizaje
make stats-spectrum
make list-examples

# Ver errores comunes
make list-errors
```

### Mantenimiento Regular

```bash
# Limpiar archivos temporales
make clean

# Validar caché si hay problemas
make validate-cache

# Ver estado del sistema
make check-env
```

### Después de Actualizar Ejemplos

```bash
# Repoblar BD vectorial
make populate-spectrum  # o populate-cpc

# O ambas
make populate-all
```

## ⚠️ Comandos con Precaución

Estos comandos son destructivos, úsalos con cuidado:

```bash
# Limpia TODOS los datos de aprendizaje (pedirá confirmación)
make clean-learning

# Reset completo del sistema de aprendizaje
make reset-learning
```

## 🎨 Personalización

Puedes modificar las variables al inicio del Makefile:

```makefile
PYTHON := python3           # Cambiar versión de Python
PLATFORM_SPECTRUM := spectrum
PLATFORM_CPC := amstrad_cpc
```

## 🆘 Solución de Problemas

### "make: command not found"
- Instala make: `sudo apt-get install make` (Linux) o usa Homebrew en macOS

### "OPENAI_API_KEY no configurada"
- Ejecuta `make setup` para crear .env
- Edita `.env` y añade tu API key

### "BD vectorial vacía"
- Ejecuta `make populate-all` para poblar las bases de datos

### "Error al generar código"
- Verifica con `make check-env`
- Revisa logs en `logs/`
- Asegura que Qdrant esté corriendo (si usas embeddings)

## 📚 Más Información

- Ver `README.md` para documentación completa del proyecto
- Ver `docs/PHASE_1_IMPLEMENTATION.md` para detalles de las fases
- Ver `.cursorrules` para reglas de desarrollo

---

**Consejo Pro**: Ejecuta `make help` en cualquier momento para ver todos los comandos disponibles con sus descripciones.
