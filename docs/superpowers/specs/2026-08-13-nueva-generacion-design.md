# Diseño: nueva generación — IR abierto, examinador independiente y gráficos propios

Fecha: 2026-08-13. Rama base: `main` (f82c138).

## Problema

El escritor ya es libre: `studio/generator.py` pide al modelo ficheros `.c`/`.h`
arbitrarios y los repara contra evidencia real. Lo que no es libre es lo que hay
a cada lado de él. El diseño no puede *expresar* un juego grande y las puertas
sólo saben *medir* un juego: barrer bolitas en una rejilla.

Evidencia recogida sobre el repositorio actual:

- `studio/models.py` fija el vocabulario: `codegen.SUPPORTED_ROLES` es
  `{player, enemy, collectible}`, los tiles son dos caracteres (`#`, `.`), la
  rejilla es de una pantalla y no hay física, disparos, puertas ni salas.
- `resources/genres.yml` declara dieciocho tipologías, pero una tipología sólo
  fija cuatro campos: `terrain`, y el `count`/`behaviour`/`speed` de los
  enemigos. Breakout, snake, sokoban y Pac-Man son el mismo juego con otro
  espaciado de pilares.
- `packs.py::_bare_project` cablea cada proyecto: tres entidades, tres niveles
  de 20×16, tres vidas, 100 de marcador, tres criterios de aceptación.
- `layout.py::PILLAR_PATTERNS` genera terreno de un ciclo de tres. En
  `studio-projects/profanacion/game.yml` los niveles 1 y 3 son idénticos byte a
  byte. Abu Simbel Profanation — plataformas de salto y pantalla fija — salió
  como tres laberintos de bolitas.
- Las puertas son el corsé real, no el prompt. `quality.design_quality_report`
  exige los roles `{player, enemy, collectible}` y los ids de aceptación
  `{start_game, collect_scores, enemy_costs_life}`;
  `acceptance.derive_scenarios` supone movimiento por celdas a la cadencia de
  `FRAMES_PER_CELL` y marcador igual a `recogidos × score_per_collectible`.
  `zampabolas` y `atic-atac-2000` agotaron sus cinco intentos contra eso:

      After holding down for 28 frames:
        g_remaining: expected 11, read 12
        g_score: expected 10, read 0

  Dos de siete proyectos rechazados por las suposiciones del arnés, no por su
  calidad.
- Tamaño: los siete programas son un solo `main.c` de 366 a 483 líneas, y los
  binarios pesan entre 6.3 KB y 9.7 KB contra un presupuesto de 24 KB. Se usa
  cerca del 30% de la máquina.
- Gráficos: `plat_cell` dibuja cuatro glifos 8×8 cableados (`shape_player`,
  `shape_enemy`, `shape_item`, `shape_wall`); cinco de los siete juegos son
  manchas de glifo y sólo `mijuego` y `profanacion` llaman a `plat_sprite`.
  `spriting.is_blitter_sprite` exige exactamente 16×16, así que **no existe
  ninguna vía de tiles**: un asset que no sea 16×16 cae a `assets.c`, que ningún
  C generado referencia. El color es una tinta por sprite sobre `PAPER_BLACK` en
  Spectrum y cuatro plumas fijas en CPC; `presentation.palette` está documentado
  como sin usar.

## Objetivo

Que Studio pueda producir un juego cuyo vocabulario no estaba previsto: un
plataformas con salto y varias pantallas conectadas, con tiles y paleta propios,
verificado en emulador contra un examen derivado de su propio diseño.

Fuera de alcance: audio (sigue descartado), puertas de comportamiento en CPC
(bloqueadas por el volcado de memoria del emulador instalado), y scroll por
hardware o software.

## Decisiones tomadas

| Decisión | Elegido | Descartado y por qué |
| --- | --- | --- |
| Papel del IR | IR abierto por juego: `game.yml` declara su propio vocabulario dentro de un meta-esquema fijo | IR cerrado más ancho (seguiría siendo una lista escrita a mano de lo que puede existir); brief en prosa como fuente de verdad (deja la TUI sin nada que editar y los diffs en prosa) |
| Forma del IR abierto | Vocabulario declarado: `tiles`, `entities`, `mechanics`, `observables`, `screens` | DSL de reglas evento→efecto: muy verificable, pero es inventar un lenguaje y reimpone el techo — lo que el DSL no sabe decir, el juego no puede hacerlo |
| Verificación | Examinador independiente: un modelo lee **sólo** el diseño y deriva el examen | Que el escritor declare sus propias pruebas (se pone el examen a sí mismo); sólo invariantes genéricas (no juzga mecánica ninguna) |
| Crecimiento | Un disparo grande multi-fichero, con reintento por parche | Construcción por etapas verificadas (más segura, se descartó por coste de implementación); un agente por módulo (exige acordar cabeceras antes de saber cómo es el juego) |
| Gráficos | Los cuatro: tiles reales, color de diseño, sprites de tamaño y poses libres, pantalla de carga y título | — |
| Plataformas | Spectrum primero; CPC detrás, cuando haya volcado de memoria | Ambas a la vez (en CPC se construiría a ciegas); arreglar antes la sonda de CPC (retrasa todo lo demás) |
| Migración | Corte limpio, `schema_version: 4`; los siete proyectos v3 se archivan | Convivencia v3/v4 (dos caminos vivos en cada puerta); migrador automático (trabajo por siete proyectos de prueba) |

## Arquitectura

```
brief + ficha de referencia citada          (existe: studio/reference.py)
        |
DISEÑADOR   modelo -> propuesta v4 tipada, diff aprobable
        |                        (existe: reference_design.py, planner.py)
   game.yml v4        <- fuente de verdad, editable
        |
ARTISTA     tiles + sprites + título/carga  (sprite_artist.py ampliado)
        |
EXAMINADOR  modelo, ve SOLO el diseño -> exam.yml            [NUEVO]
        |
ESCRITOR    modelo, ve diseño + exam + cabeceras + arte -> varios .c/.h
        |
PUERTAS     build -> invariantes -> examen leído en memoria
        |  falla                              |  pasa
   reparación por parche                   release
```

La etapa nueva es el examinador. Su llegada retira de Python la derivación del
guión: `acceptance.derive_scenarios`, `sweep_plan`, `chase_catch_frames` y
`FRAMES_PER_CELL` son la suposición "moverse por rejilla recogiendo bolitas"
escrita en código, y se van con ella.

El escritor sigue viendo el examen antes de escribir — eso funciona hoy y se
conserva. Lo que deja de poder hacer es escribirlo.

## El IR v4

`studio/models.py` se reescribe. El esquema fijo describe **cómo se declara un
vocabulario**, no cuál:

```yaml
schema_version: 4
metadata:   {slug, title, brief, ...}
target:     {platform, video_mode, frame_hz}
budgets:    {binary_bytes, static_data_bytes, ...}
controls:   {bindings: {left: O, right: P, jump: SPACE, fire: M}}
palette:    {...}

tiles:
  - {id: piedra,   char: '#', art: tile_piedra,   traits: [solid]}
  - {id: escalera, char: 'H', art: tile_escalera, traits: [climbable]}

entities:
  - {id: momia, kind: perseguidor, sprite: momia, poses: [walk, turn], count: 3,
     notes: "patrulla la cornisa; el contacto cuesta una vida"}

observables:
  - {symbol: g_keys, width: 1, meaning: "llaves recogidas en esta pantalla"}

mechanics:
  - "SPACE salta; la gravedad devuelve al suelo en unos 12 frames"

screens:
  - {id: sala_1, width: 32, height: 22, tiles: [...], spawns: [...],
     exits: {right: sala_2, down: cripta}}

scenes:  [...]        # flujo de pantallas: título, juego, game over. No es género.
assets:  [...]        # sprites, tilesets, pantalla de carga y de título
```

`controls.bindings` acepta nombres libres: hoy son cinco literales fijos y por
eso "corre a la derecha *y* salta" no existe ni en el diseño ni en el examen.
`traits` son cadenas libres — `solid` no significa nada para Studio, es asunto
del programa. `screens.exits` es lo que permite un juego grande multipantalla sin
scroll.

Studio valida **sólo estructura**, nunca semántica:

- cada carácter usado en un mapa está declarado en `tiles`;
- cada spawn nombra una entidad que existe;
- cada `exit` apunta a una pantalla que existe;
- la pantalla cabe en la rejilla del modo de vídeo;
- los presupuestos caben en los máximos de la máquina;
- los `observables` no chocan con los símbolos del contrato base;
- el arte declarado existe y entra en `static_data_bytes`.

Ninguna regla de Studio vuelve a decir qué es un juego.

## Examinador

Módulo nuevo `llmz80/studio/examiner.py`. Entrada: `game.yml`, nunca el código.
Salida: `exam.yml`, versionado junto al diseño y re-derivado cuando el diseño
cambia (`derived_from` guarda el hash).

```yaml
schema_version: 1
derived_from: <hash de game.yml>
steps:
  - id: empieza_partida
    given: "la pantalla de título está visible"
    when:  "el jugador pulsa disparo"
    then:  "empieza la partida"
    hold: {fire: 30}
    expect: {g_state: 1, g_level: 1}
  - id: salta_la_grieta
    hold: {right: 40, jump: 6}
    expect: {g_screen: 2}
  - id: la_momia_mata
    hold: {none: 90}
    expect: {g_lives: 2}
    screen_must_change: true
```

Tres cosas que el guión actual no puede expresar y éste sí: teclas compuestas
(`ScenarioHold` es hoy un literal de cinco valores, así que ningún plataformas
es examinable), observables propios del diseño además del contrato base, y el
cambio de pantalla como aserción para diseños sin nada numérico que mirar.

Barreras, porque el examinador es un modelo y puede escribir un examen imposible:

1. `exam.yml` se valida: cada símbolo existe en el contrato o en `observables`;
   cada tecla existe en `controls.bindings`; los frames dentro de límite.
2. **Un examen que ningún programa aprueba es un examen roto.** Si el mismo paso
   falla en varios intentos seguidos con el build limpio, se marca sospechoso y
   el examinador lo re-deriva *una vez*, viendo las lecturas reales de memoria.
   Si vuelve a fallar, el proceso para y presenta las dos versiones a la persona.
   Sin esta regla se repite `zampabolas`: cinco intentos contra un examen que
   exigía una cadencia que el diseño no podía dar, sin que nadie sospechara del
   examen.

## Puertas

| Puerta | Mide | Bloquea |
| --- | --- | --- |
| build | compila, sin warnings inesperados, artefacto real y no vacío, dentro de presupuesto | sí |
| invariantes | arranca, dibuja, la pantalla cambia con input, no se cuelga, símbolos presentes en el mapa del linker, coste de frame | sí |
| examen | los pasos de `exam.yml`, leídos en memoria real | sí (Spectrum) |
| CPC | se abstiene hasta que exista volcado de memoria | no |

## Escritura multi-fichero y reintento por parche

`ProgramSources` ya admite varios ficheros; quien lo impedía era el prompt y el
límite de tokens.

- Se pide reparto explícito: `main.c` (arranque y bucle), `game.c` (reglas),
  `draw.c` (dibujo), `level_data.c` (mapas), más las cabeceras propias que el
  programa quiera. `max_tokens` sube.
- **Reintento por parche.** Hoy `store_program` vacía el directorio y el modelo
  re-emite el juego entero en cada intento; con cuatro ficheros y 1500 líneas eso
  es caro y frágil. El reintento pasa a devolver sólo los ficheros que toca más
  un `deleted: []` explícito, y se aplica encima de lo que ya hay. Ésta es la
  mitigación del riesgo del disparo grande.
- El escritor ve **cuánto ha gastado el intento anterior** ("7 KB de 24 KB,
  1.2 KB de 8 KB de datos"). Hoy no lo ve, y por eso todos los juegos se quedan
  en el 30% de la máquina.
- Cabeceras que se le enseñan: `platform.h` ampliada, `game_config.h`,
  `game_state.h`, `sprites.h`, `tiles.h`, y `exam.yml` traducido a prosa.

## Cadena gráfica

**Tiles reales.** `spriting.py` deja de exigir 16×16: los empaquetadores aceptan
cualquier tamaño múltiplo de 8 e `is_blitter_sprite` pasa a ser una comprobación
de alineación. Se generan `tiles.h`/`tiles.c` con el patrón ya probado de
`sprite_header.py` — offsets precalculados en Python, cero multiplicaciones de
16 bits, por la razón de ABI que `sprite_header.py` documenta. En `platform.c`
entra `plat_tile(col, row, tile)`, sin máscara y por tanto más rápido que un
sprite, y mueren `plat_cell` y los cuatro `shape_*`.

**Color de diseño.** El bloque `palette` se usa de verdad. Spectrum: tinta y
papel por tile y por entidad, y el empaquetador guarda el atributo dominante
**por celda de 8×8** en vez de una tinta para el sprite entero. El attribute
clash no se prohíbe — es de la época —, pero el prompt del artista pide arte de
dos colores por celda y un informe nombra las celdas que lo incumplen. CPC:
`apply_palette()` programa las plumas del diseño, el modo 0 recupera sus 16, y el
cuantizador usa la paleta del diseño en vez de `CPC_DEFAULT_PALETTE`.

**Sprites más ricos.** `AssetSpec` gana ancho y alto de fotograma libres
(múltiplos de 8) y `poses` con nombre — `walk`, `jump`, `die`, `left` — en vez de
cuatro fotogramas anónimos. `plat_sprite` toma el tamaño de la tabla del sprite,
no de una constante.

**Pantalla de carga y título.** La de carga es un bloque SCR aparte, fuera del
presupuesto de código: se carga y se descarta. La de título debe dibujarse con
tiles o comprimida — 6912 bytes en crudo serían un tercio del binario.
**Desconocido a verificar primero:** cómo adjunta z88dk un bloque SCR de carga al
TAP en esta cadena concreta. Es lo primero que se comprueba del bloque gráfico,
antes de construir nada sobre ello.

`sprite_artist._judge_frames` se extiende a tiles y a pantallas: un tileset con
dos tiles indistinguibles a 8×8, o un título que sale papilla, se caza antes de
empaquetar.

## Qué se borra

`layout.py`, los defaults de `packs.py`, `solvability.py`, `difficulty.py`,
`terrain_structure.py`, `derive_scenarios`/`sweep_plan`/`chase_catch_frames`/
`FRAMES_PER_CELL`, `SUPPORTED_ROLES`, `plat_cell` y los `shape_*`, y los checks
`core_roles`, `three_core_acceptance_scenarios` y `release_has_multiple_levels`
de `design_quality_report`.

Las tres puertas de análisis de nivel (`solvability`, `difficulty`,
`terrain_structure`) se retiran porque las tres suponen rejilla de cuatro
direcciones sin salto: en un plataformas mienten. Lo que aportaban — "¿se puede
llegar?" — pasa al examinador, que puede pedir "llega a la salida" y hacer que el
emulador lo demuestre.

`resources/genres.yml` **sobrevive degradado**: deja de ser un catálogo cerrado
con poder de validación y pasa a ser material de prompt, tipologías de las que el
diseñador puede tirar sin que obliguen a nada.

Los siete proyectos de `studio-projects/` se archivan tal cual; ninguno es
contenido que merezca migrarse.

## Pruebas

Nuevas, donde el riesgo está:

- un `exam.yml` con símbolos o teclas inventadas se rechaza;
- el bucle de sospecha del examen dispara y no se come varios intentos;
- un parche aplica los ficheros que trae y borra los que declara;
- tiles empaquetados comprobados byte a byte contra memoria de vídeo real en
  ZEsarUX, igual que se hizo con los sprites en S12;
- la validación estructural del IR v4 rechaza referencias que no resuelven
  (carácter sin tile, spawn sin entidad, exit sin pantalla).

Mueren con su código: `test_studio_genres.py`, `test_difficulty*.py`,
`test_terrain_structure.py` y la parte de `test_studio_acceptance.py` que fija
los tres escenarios centrales.

## Evidencia de aceptación

Una sola, y es la que decide si el rediseño está hecho: **rehacer
`profanacion`**. Hoy Abu Simbel Profanation sale como tres laberintos de bolitas
idénticos de 20×16. Tiene que salir un plataformas con salto, varias pantallas
conectadas por `exits`, tiles y paleta propios, construido, examinado en ZEsarUX
contra su propio `exam.yml` y aprobado.

## Descomposición en fases

Esto no cabe en un solo plan de implementación. Cada fase se lleva el suyo, y
cada una termina con el repositorio en verde y con evidencia propia.

**F1 — IR v4 y desmontaje de la plantilla.** `models.py` reescrito, validación
estructural, `genres.yml` degradado a material de prompt, y borrado de
`layout.py`, los defaults de `packs.py`, `solvability.py`, `difficulty.py` y
`terrain_structure.py`. `plat_cell` **sobrevive esta fase**: dibuja el `char` del
tile como glifo, para que el escenario siga viéndose mientras no existan tiles
reales. Evidencia: crear, editar, guardar y reabrir un diseño v4 con salto,
`exits` y entidades de vocabulario propio, y que Studio no tenga ni una regla que
diga qué es un juego.

**F2 — Examinador, puertas y escritura multi-fichero.** `examiner.py`,
`exam.yml` con su validación y su bucle de sospecha, la pila de puertas nueva, la
escritura repartida en varios ficheros y el reintento por parche. Evidencia: la
de aceptación de este spec — `profanacion` como plataformas multipantalla
examinado y aprobado en ZEsarUX, todavía dibujado con glifos.

**F3 — Cadena gráfica.** Tiles reales (`plat_tile`, `tiles.h`/`tiles.c`), paleta
de diseño en ambas máquinas, sprites de tamaño y poses libres. Aquí muere
`plat_cell`. Evidencia: tiles comprobados byte a byte contra memoria de vídeo en
ZEsarUX, y `profanacion` con arte propio en pantalla.

**F4 — Pantalla de carga y título.** Sólo después de resolver el desconocido del
bloque SCR en z88dk, que se verifica al principio de la fase y puede cambiar su
alcance.

## Costes asumidos

- Una llamada de modelo más por proyecto: el examinador.
- CPC se queda sin puertas de comportamiento hasta que haya volcado de memoria
  (CPCEC, o Caprice32 con depuración).
- El disparo grande multi-fichero puede fallar tarde; el reintento por parche lo
  amortigua pero no lo elimina.
