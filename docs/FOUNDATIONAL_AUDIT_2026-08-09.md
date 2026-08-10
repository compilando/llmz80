# Auditoría fundacional del generador (2026-08-09)

## Resultado

El pipeline base ha pasado de recuperar ficheros C arbitrarios a recuperar
programas completos certificados por la toolchain. Spectrum y Amstrad CPC
mantienen salida `main.c` autocontenida y usan el compilador real como fuente de
verdad.

Evidencia de esta iteración:

- 42 tests Python, incluidos builds mínimos reales de Z88DK y CPCtelera.
- 53/53 programas recuperables compilan: 10 Spectrum y 43 Amstrad CPC.
- Tres pruebas prompt → C → compilador → artefacto, todas en el primer build:
  - Spectrum: minijuego QAOP con sprites y puntuación (`output.tap`).
  - CPC: nave, cristales, puntuación y victoria (`output.dsk`).
  - CPC avanzado: mapa, scroll horizontal, colisiones y HUD (`output.dsk`).

Los resultados concretos viven bajo `local/` y no se versionan.

## Causas raíz encontradas

1. El prompt Spectrum enseñaba APIs inexistentes (`zx_plot`, `zx_point`) y
   scancodes QAOP con mayúsculas que Z88DK no define.
2. El prompt/validador CPC enseñaba `cpct_getKeyASCII` y esperas inexistentes, y
   tenía mal la aridad de `cpct_vflipSprite`.
3. El RAG indexaba cada `.c`, por lo que módulos de datos y sprites sin `main()`
   podían presentarse como programas completos.
4. Sin colección Qdrant se elegía una muestra aleatoria; además,
   `--no-embeddings` ni siquiera arrancaba si `qdrant-client` no estaba
   instalado.
5. `examples/amstrad_cpc_level2` no se utilizaba, pese a contener la mayor parte
   de la biblioteca avanzada.
6. CPCtelera estaba ligado a una ruta absoluta local y el sistema consumía una
   llamada al modelo antes de comprobar algunas toolchains.
7. Los tests verificaban heurísticas, pero no ejecutaban los compiladores.

## Nuevo flujo

1. Preflight de la toolchain antes de generar.
2. Catálogo local determinista sobre entrypoints con `main()` y proyecto de
   build válido.
3. Ranking bilingüe por intención; Qdrant sólo amplía el catálogo y nunca es un
   requisito.
4. Prompt breve con contrato verificado y ejemplos completos relevantes.
5. Limpieza de respuesta y correcciones deterministas seguras.
6. Validación local, compilación real y hasta cuatro iteraciones guiadas por el
   diagnóstico del compilador.
7. Registro de artefactos, contexto recuperado, entorno de build e historial de
   correcciones.

## Biblioteca y exclusiones

El catálogo abarca `examples/amstrad_cpc` y `examples/amstrad_cpc_level2`.
`medium/arkosAudio` conserva sus fuentes y binarios, pero se excluye de RAG con
`.llmz80-rag-exclude`: su fuente dispara un error interno de SDCC
(`SDCCgenconstprop.cc:1012`) con la toolchain soportada. Una exclusión es visible,
auditable y reversible cuando el proyecto vuelva a compilar.

Ejecutar la certificación completa:

```bash
make audit-examples
```

## Límites honestos

Compilar no demuestra por sí solo jugabilidad perfecta. La iteración valida
contratos, memoria estática básica, toolchains y producción de TAP/DSK, pero no
automatiza todavía una inspección visual del emulador ni pruebas de controles
frame a frame. Los modelos también son no deterministas: el bucle de compilación
reduce ese riesgo, no lo elimina matemáticamente.

El siguiente nivel de garantía debe ser un corpus fijo de prompts con métricas de
first-build success, success tras reparación, tamaño de binario y pruebas de
emulador automatizables por plataforma.
