# Informe: Retro Vibe-Coding ASM Z80 para Amstrad CPC

Fecha: 2026-06-02

## Referencia Analizada

- Artículo original: https://www.elladodelmal.com/2026/05/como-crear-con-vibe-coding-codigo-asm.html
- Copia indexada consultada: https://seguridadpy.info/2026/05/como-crear-con-vibe-coding-codigo-asm-html/

## Resumen del Artículo

El artículo describe un experimento de Vibe-Coding/Spec-Coding para crear utilidades en ASM Z80 para Amstrad CPC 6128. La conclusión práctica es que el proceso aún exige mucho control humano: los modelos tienden a mezclar ensambladores, instrucciones o máquinas distintas, y cuesta mantenerlos centrados en Z80 para CPC.

El flujo que propone el artículo es:

1. Prompt muy restrictivo para generar ASM Z80 CPC6128.
2. Programa standalone con `ORG &4000`.
3. Carga con `LOAD` y ejecución con `CALL &4000`.
4. Compilación con `pasmo` en formato BIN con cabecera AMSDOS.
5. Creación manual del DSK con Amstrad DSK Filesystem Manager.
6. Prueba en CPCBox, WinAPE, JavaCPC, Caprice u otro emulador fiable.
7. Iteración manual si el binario cuelga el sistema o falla.

Los riesgos principales que se mencionan son desvíos a otros dialectos, otros microprocesadores, Sinclair/Spectrum, BASIC, cargadores incorrectos, fallos de compilación, uso inseguro de memoria y cuelgues por no retornar o no dejar un bucle seguro.

## Qué Hace Hoy LLMZ80

LLMZ80 ya resuelve una parte relevante del problema general de generación retro:

- Genera C para ZX Spectrum y Amstrad CPC.
- Usa prompts de sistema específicos por plataforma.
- Recupera ejemplos mediante embeddings y Qdrant.
- Compila automáticamente el resultado.
- Ejecuta un ciclo de validación, compilación, corrección y reintento.
- Guarda ejemplos exitosos y firmas de errores para aprendizaje local.
- Prepara proyectos CPCtelera completos para Amstrad CPC.
- Incluye una colección amplia de ejemplos CPC, algunos con ensamblador dentro de proyectos existentes.

## Gaps Frente al Flujo ASM del Artículo

### Gap 1: No hay plataforma ASM standalone

El CLI trabaja con `spectrum` y `amstrad_cpc`; ambos flujos están orientados a C. El prompt de Amstrad CPC exige CPCtelera y prohíbe bloques ASM inline, por lo que no puede usarse directamente para el flujo del artículo.

Impacto: LLMZ80 no puede reproducir de forma automática el proceso `ASM -> BIN AMSDOS -> DSK -> CALL &4000`.

### Gap 2: El compilador configurado no cubre pasmo

`config.yml` declara `z80asm` como ensamblador, pero el ciclo de compilación implementado solo maneja `zcc`, `sdcc` y `make` CPCtelera. No hay rama para `pasmo`, cabecera AMSDOS ni artefactos `.bin`/`.dsk` ASM.

Impacto: aunque el modelo generase ASM correcto, no habría pipeline de build para validarlo.

### Gap 3: Falta validador ASM CPC6128

El proyecto tiene validación pre-compilación para C, pero faltan reglas para:

- Instrucciones Z80 estándar.
- Prohibición de opcodes no documentados si se quiere máxima compatibilidad.
- `ORG &4000` o dirección configurable.
- Direcciones firmware válidas.
- Rango VRAM `&C000` a `&FE7F`.
- Control de pila.
- Terminación segura con `RET` o bucle controlado.
- Ausencia de dependencias BASIC/Spectrum/Sinclair no solicitadas.

Impacto: se perdería una de las mayores ventajas actuales del proyecto, que es filtrar fallos antes de gastar una iteración LLM o compilar.

### Gap 4: El RAG no está especializado en ASM CPC

La base de ejemplos CPC es muy útil, pero está dominada por CPCtelera/C. Para ASM standalone harían falta ejemplos mínimos y corregidos: texto por firmware, modo de pantalla, teclado, VRAM, llamadas BIOS/firmware, carga en `&4000`, rutinas de disco, errores comunes y equivalencias entre ensambladores.

Impacto: el modelo seguiría expuesto al problema descrito en el artículo: mezclar dialectos o hardware.

### Gap 5: No hay empaquetado DSK automático para ASM

El artículo usa Amstrad DSK Filesystem Manager manualmente. LLMZ80 ya produce `.dsk` en el flujo CPCtelera, pero no tiene una ruta genérica para importar un BIN AMSDOS generado por `pasmo`.

Impacto: el bucle de prueba queda fuera del agente y el coste humano de iteración se mantiene alto.

### Gap 6: No hay harness de ejecución en emulador

El proyecto puede lanzar emuladores, pero no verifica comportamiento. Para ASM de bajo nivel haría falta, como mínimo, comprobar que el emulador arranca, carga el binario, ejecuta `CALL &4000` y no se cuelga en los primeros segundos.

Impacto: se puede confundir "compila" con "funciona en CPC".

## Puntos a Favor de LLMZ80

- La arquitectura ya tiene el patrón correcto: prompt específico, RAG, compilación, corrección, aprendizaje y logs.
- El sistema de aprendizaje local encaja muy bien con ASM, donde las firmas de error y las correcciones son repetitivas.
- La separación por plataforma permite añadir `amstrad_cpc_asm` sin romper el flujo C existente.
- Ya existe integración con Qdrant y embeddings, así que mejorar la calidad depende sobre todo de curar ejemplos.
- El proyecto ya distingue Spectrum y Amstrad CPC, algo esencial para evitar mezclas de hardware.
- La documentación de prompts de CPC es extensa y muestra una forma práctica de codificar conocimiento de plataforma.

## Puntos en Contra o Riesgos

- El README anterior podía dar una imagen demasiado genérica de "Z80", cuando el producto real está centrado en C.
- El prompt actual de Amstrad CPC bloquea ASM inline, así que reutilizarlo para el artículo sería contraproducente.
- Añadir ASM sin validadores aumentaría deuda cognitiva: el usuario tendría que confiar en código de bajo nivel difícil de auditar.
- El build actual depende de entornos locales como CPCtelera, SDCC, Z88DK y emuladores; ASM añadiría `pasmo` y una herramienta DSK más.
- Las pruebas de compilación no equivalen a pruebas funcionales en hardware/emulador.
- La colección de ejemplos es grande, pero si no se etiqueta bien puede meter ruido en retrieval para tareas ASM.

## Plan de Mejora

### Fase 1: Perfil ASM mínimo

- Añadir plataforma `amstrad_cpc_asm` en `resources/platforms.yml`, `config.yml` y CLI.
- Crear `resources/system_prompt_amstrad_cpc_asm.txt`.
- Definir artefactos esperados: `main.asm`, `output.bin`, `output.dsk`.
- Documentar instalación de `pasmo` y herramienta DSK elegida.

Resultado esperado: generar un "Hello CPC" ASM que compile a BIN AMSDOS.

### Fase 2: Build y empaquetado

- Implementar rama de compilación `pasmo`.
- Generar BIN con cabecera AMSDOS.
- Automatizar creación/importación a DSK.
- Añadir script `build_amstrad_asm.sh` o integrar el perfil en el CLI principal.

Resultado esperado: `llm_z80.py --platform amstrad_cpc_asm --prompt ...` produce un DSK cargable.

### Fase 3: Validación ASM

- Implementar `AsmZ80CPCValidator`.
- Validar sintaxis básica, instrucciones permitidas, `ORG`, etiquetas, rangos de memoria y llamadas firmware conocidas.
- Detectar patrones de riesgo: escritura fuera de VRAM, salto sin retorno, dependencia de estado previo, mezcla Spectrum/Sinclair/BASIC.
- Guardar `validation_report.txt` igual que en el flujo C.

Resultado esperado: rechazar errores típicos antes de compilar.

### Fase 4: RAG especializado

- Crear ejemplos curados ASM CPC por dificultad.
- Indexar código, descripción, direcciones usadas, llamadas firmware y errores corregidos.
- Separar colecciones Qdrant por perfil para no mezclar CPCtelera C con ASM.

Resultado esperado: prompts de ASM recuperan ASM real, no C ni otros dialectos.

### Fase 5: Prueba en emulador

- Automatizar una ejecución smoke test con Caprice/CPCEC/JavaCPC si está disponible.
- Cargar DSK, ejecutar `MEMORY &3FFF`, `LOAD "PROG.BIN",&4000`, `CALL &4000`.
- Registrar si el emulador termina, se cuelga o muestra errores.

Resultado esperado: distinguir "compila" de "arranca en CPC".

### Fase 6: Objetivos avanzados

- Plantillas para firmware, acceso directo a VRAM, teclado, CRTC, PSG y disco.
- Banco de tests para rutinas pequeñas.
- Métricas de coste por intento, intentos hasta compilar y éxito en emulador.
- Modo "spec-coding" con contrato técnico antes de generar código.

Resultado esperado: reducir iteraciones humanas en tareas de bajo nivel.

## Recomendación

La mejora más rentable es añadir `amstrad_cpc_asm` como perfil separado, no mezclar ASM dentro del flujo `amstrad_cpc` actual. El flujo C/CPCtelera ya funciona como producto coherente; el ASM necesita otro prompt, otro compilador, otros validadores y otra definición de éxito.

La segunda prioridad es el validador. Sin validación ASM, el sistema repetiría el problema central del artículo: cada fallo se descubre tarde, dentro del emulador, con alto coste de iteración.

## Lectura Conceptual Para el Flujo C/CPCtelera Actual

El valor más aplicable del artículo no es `pasmo` ni ASM, sino la disciplina de acotar el entorno hasta que el modelo no tenga espacio para mezclar dialectos. En nuestro caso, el problema equivalente es: pedimos C para CPCtelera, pero el resultado puede parecer C razonable y aun así no compilar con el proyecto real CPCtelera.

### Concepto 1: Contrato de Plataforma Antes de Generar

El artículo mejora resultados cuando el prompt fija reglas no negociables: máquina, ensamblador, dirección de carga, llamadas firmware, memoria y forma de ejecución.

Traducción a LLMZ80:

- Definir un contrato CPCtelera previo a la generación.
- Incluir versión/ruta real de CPCtelera si se conoce.
- Prohibir APIs no verificadas contra `<cpctelera.h>`.
- Exigir un único formato de salida: `main.c` autocontenido, o proyecto multiarchivo completo, pero no una mezcla.
- Exigir que el código sea compatible con el Makefile real que vamos a ejecutar, no con una idea genérica de SDCC.

Gap detectado: el prompt actual dice en una sección que se pueden separar programas grandes en `.h` y fuentes separados, pero el generador y el validador esperan un `main.c` autocontenido. Esa contradicción facilita que el modelo genere includes locales o estructuras que luego el build real no tiene.

Acción recomendada: escoger uno de estos dos modos:

- Modo simple: solo `main.c` autocontenido, sin includes locales.
- Modo proyecto: salida estructurada con `main.c`, `.h`, `.c`, assets y manifest de build.

Para reducir errores ahora, conviene empezar por el modo simple.

### Concepto 2: Checklist Mental Convertido en Validador

El artículo pide al modelo "comprueba mentalmente" direcciones, VRAM, pila y retorno. Eso ayuda, pero es más fuerte convertirlo en reglas locales.

Traducción a LLMZ80:

- Validar que `cpct_disableFirmware()` aparece como primera llamada ejecutable en `main`.
- Validar que `cpct_setVideoMode()` precede a dibujo/texto.
- Validar que se llama a `cpct_scanKeyboard()` o `cpct_scanKeyboard_f()` antes de `cpct_isKeyPressed()`.
- Validar que las funciones de texto coinciden con el modo: `M0`, `M1`, `M2`.
- Validar rangos de coordenadas por modo antes de `cpct_getScreenPtr()`.
- Validar tamaño de sprites y buffers estáticos.
- Validar que no hay funciones inventadas `cpct_*`.

Gap detectado: ya existe un validador CPCtelera, pero su tabla de firmas es manual y parece tener inconsistencias con el propio prompt. Por ejemplo, el prompt muestra `cpct_getKeyASCII()` sin argumentos, mientras el validador espera 1. También el prompt dice que `cpct_px2byteM2` no existe, pero aparece en la lista segura del validador.

Acción recomendada: generar la lista segura desde el `cpctelera.h` local o mantener una tabla auditada con tests unitarios. El validador no puede ser menos fiable que el compilador.

### Concepto 3: Compilar Contra el Entorno Real, No Contra una Abstracción

El artículo insiste en probar en el emulador y con el empaquetado real porque ahí aparecen los fallos.

Traducción a LLMZ80:

- La validación debe ejecutar exactamente el mismo build que usará el usuario.
- La salida de compilación debe incluir el Makefile generado, `cfg/`, `src/main.c` y artefacto `.dsk`.
- Si `build_amstrad.sh` es el camino real, el ciclo automático debe usarlo o ser equivalente byte a byte.
- Guardar el entorno de build en el log: `CPCT_PATH`, versión de SDCC, commit o versión CPCtelera, comando exacto.

Gap detectado: el ciclo Python prepara un proyecto CPCtelera y llama a `make`, mientras `build_amstrad.sh` tiene su propio flujo. Si ambos divergen, puede aparecer el caso "compila en un modo, falla en real".

Acción recomendada: unificar el compilador real en una sola ruta. El agente debería llamar a la misma función/script que el desarrollador usa manualmente.

### Concepto 4: Iteración Barata y Dirigida

El artículo sufre porque cada cambio obliga a repetir DSK/emulador. Nuestro ciclo ya reduce parte de eso con retry automático, pero puede dirigir mejor los intentos.

Traducción a LLMZ80:

- Clasificar errores antes de pedir corrección: API inexistente, firma incorrecta, include local, tipo SDCC, linker/CPCtelera, memoria/assets.
- Para cada clase, aplicar una corrección determinista si es posible.
- Solo llamar al LLM cuando no haya regla local.
- Si se repite la misma firma de error, cambiar de estrategia y no pedir una corrección genérica.

El proyecto ya deduplica firmas repetidas, lo cual está alineado con esta idea.

### Concepto 5: Corpus Curado de Fallos Reales

El artículo muestra que los modelos fallan por desviarse de la plataforma. Para C/CPCtelera, el RAG debe premiar ejemplos que hayan compilado en el entorno real.

Traducción a LLMZ80:

- Separar ejemplos "curados" de ejemplos "aprendidos".
- Etiquetar cada ejemplo con: modo gráfico, APIs usadas, si compila, versión de toolchain, número de intentos.
- Penalizar ejemplos que requieren archivos auxiliares cuando estamos en modo `main.c`.
- Inyectar ejemplos negativos mínimos: "no uses `printf`", "no uses `cpct_px2byteM2`", "no inventes `cpct_drawCircle`".

Gap detectado: el sistema ya indexa éxitos aprendidos y los bonifica si compilaron en pocos intentos. Falta añadir compatibilidad de contrato: si el contrato actual es `main.c` autocontenido, no deberían recuperarse ejemplos que dependan de assets o headers locales salvo que se incluyan completos.

## Plan de Mejora Para Reducir Fallos de Compilación CPCtelera

### Prioridad 1: Eliminar contradicciones del prompt

- Quitar la recomendación de separar en `.h`/`.c` mientras la salida esperada sea solo `main.c`.
- Reforzar "no local includes" y "todo dato de sprite debe estar embebido".
- Corregir firmas dudosas del prompt y del validador.

### Prioridad 2: Validar contra headers reales

- Extraer símbolos `cpct_*` desde `$CPCT_PATH/src/cpctelera.h` y headers incluidos.
- Comparar funciones usadas contra símbolos reales.
- Mantener una tabla de aridad solo para funciones con firma no ambigua.
- Añadir tests unitarios para las funciones CPCtelera más usadas.

### Prioridad 3: Unificar build real

- Hacer que el ciclo automático use exactamente el mismo flujo que `build_amstrad.sh`, o reemplazar ambos por una función común.
- Registrar comando, variables y versiones.
- Fallar si `CPCT_PATH` no apunta a una instalación válida.

### Prioridad 4: Correcciones deterministas

- Reescribir automáticamente includes locales prohibidos.
- Corregir llamadas conocidas de aridad incorrecta cuando la intención sea obvia.
- Sustituir APIs Spectrum/Z88DK por equivalentes CPCtelera conocidos.
- Eliminar `printf`, `malloc`, `float`, file I/O y funciones inventadas antes de compilar.

### Prioridad 5: Smoke test de artefacto

- Tras compilar, verificar que existe `.dsk`.
- Opcionalmente arrancar emulador headless o herramienta equivalente.
- Registrar que el artefacto se puede cargar, no solo que SDCC terminó.

## Recomendación Ajustada

Para nuestro problema actual, no empezaría implementando ASM. Empezaría por convertir el aprendizaje del artículo en un "contrato CPCtelera ejecutable": prompt sin contradicciones, validador sincronizado con los headers reales y una única ruta de build. Eso ataca directamente la causa de "el modelo genera C, pero luego en real no compila".

## Implementado en Esta Iteración

- Prompt CPCtelera endurecido para generar un único `main.c` autocontenido.
- Eliminada la contradicción que recomendaba separar código en `.h`/`.c` auxiliares.
- Validador CPCtelera más estricto:
  - includes locales son error;
  - funciones `cpct_*` desconocidas son error;
  - `printf`, memoria dinámica, file I/O, `float`/`double` y Z88DK son error;
  - `cpct_disableFirmware()`, modo de video y escaneo de teclado se validan como contrato;
  - firmas de funciones de alto uso corregidas.
- RAG filtrado por contrato: se prefieren ejemplos autocontenidos para Amstrad CPC.
- Correcciones deterministas conservadoras antes de compilar:
  - añadir `#include <cpctelera.h>` si faltaba;
  - añadir `cpct_disableFirmware()` cuando falta en programas con hardware;
  - añadir `cpct_scanKeyboard_f()` antes del primer `cpct_isKeyPressed()`;
  - sustituir `zx_cls()` por `cpct_clearScreen(0x00)`.
- Build reforzado:
  - guarda `build_environment.txt` con comando, `CPCT_PATH`, SDCC, make y commit CPCtelera si existe;
  - no acepta compilación exitosa si no aparece artefacto final;
  - crea `output.dsk` canónico para Amstrad CPC cuando el build genera otro nombre.
