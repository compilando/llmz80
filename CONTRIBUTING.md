# Contributing to LLMZ80

¡Gracias por tu interés en contribuir a LLMZ80! Este documento proporciona pautas para contribuir al proyecto.

## Tabla de Contenidos

- [Código de Conducta](#código-de-conducta)
- [Cómo Puedo Contribuir](#cómo-puedo-contribuir)
- [Configuración del Entorno de Desarrollo](#configuración-del-entorno-de-desarrollo)
- [Proceso de Pull Request](#proceso-de-pull-request)
- [Guías de Estilo](#guías-de-estilo)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Testing](#testing)
- [Reportar Bugs](#reportar-bugs)
- [Sugerir Mejoras](#sugerir-mejoras)

## Código de Conducta

Este proyecto y todos los que participan en él se rigen por un código de conducta implícito de respeto y profesionalismo. Al participar, se espera que mantengas este estándar.

## Cómo Puedo Contribuir

### Reportar Bugs

Los bugs se rastrean como issues en GitHub. Antes de crear un bug report:

1. **Verifica** que no sea un duplicado buscando en los issues existentes
2. **Determina** qué repositorio debería recibir el problema
3. **Recopila** información sobre el problema:
   - Usa el template de issue si está disponible
   - Incluye los pasos para reproducir el problema
   - Proporciona ejemplos específicos
   - Describe el comportamiento observado vs el esperado
   - Incluye capturas de pantalla si es relevante
   - Incluye información del entorno (SO, versión de Python, etc.)

### Sugerir Mejoras

Las sugerencias de mejoras también se rastrean como GitHub issues. Al crear una sugerencia:

1. **Usa un título claro y descriptivo**
2. **Proporciona una descripción paso a paso** de la mejora sugerida
3. **Proporciona ejemplos específicos** para demostrar los pasos
4. **Describe el comportamiento actual** y explica qué comportamiento esperabas ver
5. **Explica por qué esta mejora sería útil** para la mayoría de los usuarios de LLMZ80

### Contribuir con Código

#### Tipos de Contribuciones

- **Corrección de bugs**: Corregir problemas existentes
- **Nuevas funcionalidades**: Añadir nuevas capacidades
- **Mejoras de rendimiento**: Optimizar código existente
- **Documentación**: Mejorar o corregir documentación
- **Ejemplos**: Añadir nuevos ejemplos de código para las plataformas
- **Tests**: Añadir o mejorar tests

## Configuración del Entorno de Desarrollo

### Requisitos Previos

- Python 3.10 o superior
- Git
- Docker (para Qdrant)
- SDCC (para Amstrad CPC)
- Z88DK (para ZX Spectrum)

### Instalación

1. **Fork el repositorio** en GitHub

2. **Clona tu fork localmente:**
```bash
git clone https://github.com/TU_USUARIO/llmz80.git
cd llmz80
```

3. **Añade el repositorio upstream:**
```bash
git remote add upstream https://github.com/compilando/llmz80.git
```

4. **Crea un entorno virtual:**
```bash
python -m venv venv
source venv/bin/activate  # En Linux/Mac
# o
venv\Scripts\activate  # En Windows
```

5. **Instala las dependencias:**
```bash
pip install -r requirements.txt
```

6. **Instala dependencias de desarrollo (cuando estén disponibles):**
```bash
pip install -r requirements-dev.txt  # Si existe
```

7. **Configura las variables de entorno:**
```bash
cp .env.example .env
# Edita .env con tus API keys
```

8. **Inicia Qdrant (base de datos vectorial):**
```bash
docker run -p 6333:6333 qdrant/qdrant
```

9. **Inicializa la base de datos con ejemplos:**
```bash
python llm_z80.py --platform spectrum --populate-db
python llm_z80.py --platform amstrad_cpc --populate-db
```

### Verifica tu Instalación

```bash
# Test básico
python llm_z80.py --platform spectrum --log-level DEBUG --prompt "Change border color to red"

# Verifica compiladores
which sdcc
which zcc

# Test de compilación
./build_spectrum.sh --example=01_border --no-emulator
```

## Proceso de Pull Request

1. **Crea una rama para tu feature/fix:**
```bash
git checkout -b feature/descripcion-corta
# o
git checkout -b fix/descripcion-del-bug
```

2. **Haz tus cambios siguiendo las guías de estilo**

3. **Añade tests** si es aplicable

4. **Asegúrate de que los tests pasen:**
```bash
pytest  # Cuando haya tests
```

5. **Actualiza la documentación** si es necesario:
   - README.md
   - .cline/cline_docs.md
   - Docstrings en el código

6. **Commit tus cambios:**
```bash
git add .
git commit -m "tipo: descripción breve

Descripción más detallada del cambio si es necesario.

Fixes #123"
```

Tipos de commit válidos:
- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `docs`: Cambios en documentación
- `style`: Cambios de formato (no afectan el código)
- `refactor`: Refactorización de código
- `test`: Añadir o modificar tests
- `chore`: Cambios en el proceso de build o herramientas

7. **Push a tu fork:**
```bash
git push origin feature/descripcion-corta
```

8. **Abre un Pull Request** en GitHub con:
   - Título descriptivo
   - Descripción detallada de los cambios
   - Referencias a issues relacionados
   - Capturas de pantalla si aplica

### Revisión del Pull Request

- Mantén la conversación profesional y constructiva
- Responde a los comentarios de revisión
- Realiza los cambios solicitados
- Los PR son revisados cuando hay tiempo disponible

## Guías de Estilo

### Python

**Seguir PEP 8 estrictamente**

```python
# Bueno
def generate_code(platform: str, prompt: str) -> str:
    """Genera código C para la plataforma especificada.
    
    Args:
        platform: Plataforma objetivo (spectrum o amstrad_cpc)
        prompt: Solicitud del usuario
        
    Returns:
        Código C generado
    """
    logger.info(f"Generando código para {platform}")
    return generated_code

# Malo
def genCode(p, pr):
    print("Generating...")  # No usar print en código principal
    return code
```

### Logging

**NUNCA usar print() en el código principal:**

```python
# Bueno
import logging
logger = logging.getLogger(__name__)
logger.info("Mensaje informativo")
logger.debug("Mensaje de debug")
logger.error("Mensaje de error")

# Malo
print("Mensaje")  # Solo permitido en scripts shell
```

### Type Hints

**Usar type hints siempre que sea posible:**

```python
# Bueno
from typing import List, Dict, Optional
from pathlib import Path

def load_examples(directory: Path, limit: int = 10) -> List[Dict[str, str]]:
    pass

# Aceptable para casos simples
def simple_func(x: int) -> int:
    return x * 2
```

### Docstrings

**Usar formato Google Style:**

```python
def complex_function(param1: str, param2: int, param3: bool = False) -> Dict[str, Any]:
    """Breve descripción de una línea.
    
    Descripción más detallada si es necesario, puede ocupar
    múltiples líneas.
    
    Args:
        param1: Descripción del primer parámetro
        param2: Descripción del segundo parámetro
        param3: Descripción del tercer parámetro. Defaults to False.
        
    Returns:
        Descripción del valor de retorno
        
    Raises:
        ValueError: Cuándo se lanza esta excepción
        TypeError: Cuándo se lanza esta otra excepción
    """
    pass
```

### Código C Generado

**Los ejemplos de código C deben incluir:**

```c
// Description: Brief description in English
// Descripcion: Breve descripción en español (sin tilde en el comentario)

#include <appropriate_headers.h>

void main(void) {
    // Código compilable y funcional
}
```

## Estructura del Proyecto

```
llmz80/
├── .cline/                  # Documentación para AI assistants
├── llmz80/                  # Código principal del paquete
│   ├── api/                 # API de generación
│   │   └── generator.py     # Clase principal LLMZ80Generator
│   ├── core/                # Módulos core
│   │   ├── embeddings.py    # Gestión de embeddings
│   │   ├── cache_manager.py # Caché de embeddings
│   │   └── examples_loader.py # Carga de ejemplos
│   └── utils/               # Utilidades
│       ├── config.py        # Configuración
│       ├── logger.py        # Setup de logging
│       └── helpers.py       # Funciones auxiliares
├── generators/              # Generadores de sprites
├── examples/                # Ejemplos por plataforma
│   ├── spectrum/            # ZX Spectrum
│   └── amstrad_cpc/         # Amstrad CPC
├── resources/               # Recursos (prompts, configs)
├── tests/                   # Tests (a crear)
├── config.yml               # Configuración principal
├── llm_z80.py              # Script principal
└── vector_db.py            # Integración con Qdrant
```

### Dónde Añadir Código

- **Nueva funcionalidad de generación**: `llmz80/api/generator.py`
- **Utilidades de embeddings**: `llmz80/core/embeddings.py`
- **Gestión de caché**: `llmz80/core/cache_manager.py`
- **Helpers genéricos**: `llmz80/utils/helpers.py`
- **Ejemplos nuevos**: `examples/{platform}/`
- **Tests**: `tests/` (estructura a definir)

## Testing

### Ejecutar Tests

```bash
# Cuando haya tests implementados
pytest

# Con cobertura
pytest --cov=llmz80

# Tests específicos
pytest tests/test_generator.py
```

### Escribir Tests

```python
import pytest
from llmz80.api.generator import LLMZ80Generator

def test_generator_initialization():
    """Test que el generador se inicializa correctamente."""
    generator = LLMZ80Generator("spectrum", mock_globals, mock_api_key)
    assert generator.platform == "spectrum"
    assert generator.model == "gpt-4o"

def test_code_generation_spectrum():
    """Test generación de código para Spectrum."""
    # Implementar test
    pass
```

### Testing Manual

```bash
# Test generación básica
python llm_z80.py --platform spectrum --prompt "test"

# Test con debug
python llm_z80.py --platform spectrum --log-level DEBUG --prompt "test"

# Test de compilación
./build_spectrum.sh --example=01_border --no-emulator
```

## Reportar Bugs

### Template de Bug Report

```markdown
**Descripción del Bug**
Descripción clara y concisa del bug.

**Pasos para Reproducir**
1. Ejecuta '...'
2. Con parámetros '...'
3. Ver error

**Comportamiento Esperado**
Qué esperabas que sucediera.

**Comportamiento Actual**
Qué sucedió en realidad.

**Capturas de Pantalla**
Si aplica, añade capturas.

**Entorno:**
- OS: [e.g. Ubuntu 22.04, Windows 11]
- Python: [e.g. 3.10.12]
- Versión LLMZ80: [e.g. commit hash]
- Compilador: [e.g. Z88DK 2.2, SDCC 4.2]

**Logs**
```
Pega aquí logs relevantes
```

**Contexto Adicional**
Cualquier otra información relevante.
```

## Sugerir Mejoras

### Template de Feature Request

```markdown
**¿Tu feature request está relacionada con un problema?**
Descripción clara del problema. Ej: "Siempre me frustro cuando [...]"

**Describe la solución que te gustaría**
Descripción clara y concisa de lo que quieres que suceda.

**Describe alternativas que hayas considerado**
Descripción de soluciones o features alternativas.

**Contexto Adicional**
Cualquier otra información o capturas sobre el feature request.
```

## Áreas que Necesitan Ayuda

Contribuciones especialmente bienvenidas en:

1. **Tests Unitarios**: El proyecto necesita cobertura de tests
2. **Documentación**: Siempre se puede mejorar
3. **Ejemplos**: Más ejemplos de código para ambas plataformas
4. **Soporte de Plataformas**: Mejorar compatibilidad con diferentes OS
5. **Optimización**: Mejorar rendimiento de generación y compilación
6. **UI**: Interfaz web opcional con Gradio/Streamlit

## Preguntas

Si tienes preguntas sobre cómo contribuir:

1. Revisa la documentación en `.cline/cline_docs.md`
2. Busca en issues cerrados
3. Abre un issue con la etiqueta `question`

## Reconocimientos

Todos los contribuidores serán reconocidos en el README.md

## Licencia

Al contribuir, aceptas que tus contribuciones serán licenciadas bajo la misma licencia MIT que el proyecto.
