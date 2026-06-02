# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [Sin versionar] - 2026-06-02

### Añadido
- Informe de gaps y plan de mejora para Retro Vibe-Coding ASM Z80 en Amstrad CPC (`docs/RETRO_VIBE_CODING_GAP_REPORT.md`).
- Sección en README sobre el estado real del soporte ASM Z80 y la dirección recomendada para `amstrad_cpc_asm`.
- Contrato CPCtelera `main.c` autocontenido en prompt, validación y RAG.
- Correcciones deterministas seguras para generación CPCtelera antes de compilar.
- Registro de entorno de build y verificación de artefactos `.dsk`/`.tap`.

### Cambiado
- README actualizado para reflejar GPT-5/configuración actual, validación previa, aprendizaje local y alcance C/CPCtelera.
- El validador CPCtelera ahora trata funciones `cpct_*` desconocidas, APIs estándar problemáticas, includes locales y errores de orden de inicialización como fallos críticos.
- Los ejemplos RAG de Amstrad CPC se filtran para preferir snippets autocontenidos compatibles con el contrato `main.c`.
- Corregidos falsos positivos del validador por comentarios con paréntesis, heurísticas de punto y coma y declaraciones previas a `cpct_disableFirmware()`.
- Corregida documentación CPCtelera para `cpct_drawCharM*()` y funciones random reales de la instalación local.

## [Sin versionar] - 2024-11-20

### Añadido
- Documentación completa para AI coding assistants (`.cline/cline_docs.md`)
- Reglas de Cursor AI (`.cursorrules`) con guías de estilo y mejores prácticas
- Guía de contribución (`CONTRIBUTING.md`) con instrucciones detalladas
- Archivo de licencia MIT (`LICENSE`)
- README.md mejorado con badges, ejemplos y documentación completa
- Dependencias de desarrollo (`requirements-dev.txt`) con pytest, black, mypy, etc.
- Este archivo CHANGELOG.md para rastrear cambios

### Cambiado
- `requirements.txt` actualizado con versiones más recientes y mejor organizado
  - `python-dotenv`: 1.1.0 → 1.0.1
  - `termcolor`: 3.0.1 → 2.5.0
  - Añadidos comentarios para organizar dependencias por categoría

### Mejorado
- README.md completamente reescrito con:
  - Badges de estado del proyecto
  - Tabla de contenidos
  - Instrucciones de instalación detalladas
  - Ejemplos de uso con casos reales
  - Diagramas de arquitectura
  - Sección de solución de problemas ampliada
  - Enlaces a recursos externos

## Versiones Anteriores

### Características Implementadas

#### Sistema de Generación de Código
- ✅ Integración con OpenAI GPT-4 para generación de código C
- ✅ Soporte para ZX Spectrum 48K (Z88DK)
- ✅ Soporte para Amstrad CPC 464/6128 (CPCtelera)
- ✅ Sistema de prompts específicos por plataforma
- ✅ Compilación automática del código generado
- ✅ Sugerencias de corrección cuando la compilación falla

#### Sistema RAG (Retrieval Augmented Generation)
- ✅ Integración con Qdrant como base de datos vectorial
- ✅ Generación de embeddings con OpenAI (text-embedding-3-small)
- ✅ Búsqueda semántica de ejemplos relevantes
- ✅ Sistema de caché de embeddings local
- ✅ Carga y gestión de ejemplos de código

#### Generación de Sprites
- ✅ Soporte para múltiples proveedores de IA:
  - OpenAI DALL-E
  - Google Gemini
  - Vertex AI
- ✅ Conversión automática a formato de sprite
- ✅ Soporte para diferentes modos gráficos de Amstrad CPC

#### Scripts de Compilación
- ✅ `build_spectrum.sh`: Compilación para ZX Spectrum
- ✅ `build_amstrad.sh`: Compilación para Amstrad CPC
- ✅ Soporte para múltiples emuladores
- ✅ Creación automática de estructura de proyecto

#### Utilidades
- ✅ Sistema de logging configurable
- ✅ Configuración centralizada en `config.yml`
- ✅ Gestión de variables de entorno con `.env`
- ✅ Helpers para limpieza de respuestas de API
- ✅ Generación de slugs para nombres de directorios

## [Planeado] - Roadmap

### Alta Prioridad
- [ ] Suite de tests unitarios con pytest
- [ ] Tests de integración para compilación
- [ ] CI/CD con GitHub Actions
- [ ] Pre-commit hooks configurados
- [ ] Configuración de mypy para type checking

### Media Prioridad
- [ ] Soporte para más modelos LLM (Claude, Llama, etc.)
- [ ] Interfaz web con Gradio o Streamlit
- [ ] Exportación de proyectos completos
- [ ] Sistema de plantillas de código
- [ ] Documentación con Sphinx

### Baja Prioridad
- [ ] Soporte para MSX
- [ ] Soporte para Commodore 64
- [ ] Generación de música con AI
- [ ] Editor visual de sprites
- [ ] Marketplace de ejemplos comunitarios

## Notas de Versión

### Convenciones de Commits

Este proyecto usa [Conventional Commits](https://www.conventionalcommits.org/):

- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `docs`: Cambios en documentación
- `style`: Cambios de formato (no afectan el código)
- `refactor`: Refactorización de código
- `test`: Añadir o modificar tests
- `chore`: Cambios en el proceso de build o herramientas

### Proceso de Release

1. Actualizar versión en archivos relevantes
2. Actualizar este CHANGELOG.md
3. Crear tag de git: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
4. Push de cambios y tags: `git push && git push --tags`
5. Crear release en GitHub con notas del changelog

---

**Leyenda:**
- ✅ Completado
- 🚧 En progreso
- 📋 Planeado
- ❌ Cancelado/Pospuesto
