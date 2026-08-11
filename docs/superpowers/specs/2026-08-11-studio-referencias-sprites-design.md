# Diseño: juegos guiados por referencias reales, sprites por IA y TUI de mando

Fecha: 2026-08-11. Rama: `p0-studio-engine`.

## Problema

Studio genera juegos que compilan, pasan las gates y se dejan jugar, pero no se
parecen a lo que se pidió. Pedir "Zampabolas" produce un pack de género
`maze_chase` genérico: una sala de 20×16 con pilares repartidos cada N celdas por
`layout.py:_maze()` y doce puntos sueltos. El sistema aplanó un título real de la
época contra su catálogo de dieciocho tipologías en vez de documentarse sobre él.

Tres consecuencias medibles en `studio-projects/zampabolas`:

- El diseño no tiene contenido autoral: `threat: false`, sin límite de tiempo,
  tres niveles que sólo difieren en el patrón de pilares.
- No hay game feel: nada se anima, nada reacciona, no hay secuencia de muerte ni
  aviso de nivel, y la dificultad no crece de forma perceptible.
- El escritor gastó dos de sus cuatro intentos en errores mecánicos
  (`plat_sync` inexistente, `MAX_LEVELS` sin definir) porque el prompt le dice
  que la librería de plataforma es incluible pero nunca le enseña `platform.h`.

Y bajo todo eso, el eslabón que el roadmap ya daba por roto: los assets se
normalizan y se empaquetan, pero el C generado nunca los referencia. Dibuja
formas de celda. Sin blitter enmascarado no hay sprites, y sin sprites no hay
animación.

## Objetivo

Que un juego generado por Studio se reconozca como descendiente del juego real
que se citó al pedirlo, con sprites propios en pantalla y una partida con
principio, muerte y final.

Fuera de alcance en este spec: audio (descartado explícitamente), pathfinding
real de enemigos, y el soporte de sondas de memoria en CPC, que sigue bloqueado
por el emulador instalado.

## Decisiones tomadas

| Decisión | Elegido | Descartado y por qué |
|---|---|---|
| Origen de las referencias | Búsqueda web en vivo | Corpus curado a mano: no cubre títulos oscuros y envejece. Sólo conocimiento del modelo: alucinable y no verificable |
| Alcance de la referencia | Propuesta de diseño con diff aprobable, más contexto para el escritor | Sólo contexto: el diseño seguiría siendo la rejilla genérica y el escritor tendría que contradecirlo. Reescritura automática: fiel pero sin control |
| Sprites por IA | En este spec, cadena completa | Aplazarlos: la animación exige sprites reales, así que aplazarlos vacía el objetivo |
| Game feel obligatorio | Animación y reacción, transiciones y ritmo, dificultad perceptible | Sonido: descartado por el usuario |
| Forma de la TUI | Pantalla de mando única con paneles bajo demanda | Asistente por pasos: tedioso al reabrir. Tabs recortadas: no absorbe las etapas nuevas |
| Arquitectura | Etapa de investigación separada | Todo dentro del escritor: sin diff, sin ficha reutilizable, sin corregir a mano. Agente autónomo: opaco y difícil de gatear |

## Arquitectura

Tres unidades nuevas, cada una con una entrada, una salida en disco y ninguna
dependencia de la interfaz:

```
brief ──▶ reference.py ──▶ reference.yml ──┬──▶ editing.reference_proposal ──▶ diff ──▶ game.yml
                                           ├──▶ spriting.py ──▶ assets/*.png + AssetSpec
                                           └──▶ generator.writing_prompt ──▶ programa
```

`reference.yml` es el corte determinista: la búsqueda ocurre una vez, su
resultado queda archivado con URLs y fecha, y todo lo que va después es
reproducible aunque la web cambie.

### 1. Ficha de referencia — `llmz80/studio/reference.py`

```python
class ReferenceSource(StrictModel):
    url: str
    title: str
    retrieved_at: datetime

class GameReference(StrictModel):
    identified: bool
    confidence: Literal["high", "medium", "low"]
    title: str
    publisher: str          # Dinamic, Topo Soft, Opera, Iber Soft...
    year: int | None
    platforms: list[str]
    mechanics: list[str]        # reglas en prosa corta, una por línea
    screen_layout: str          # dónde va el HUD, tamaño de la zona de juego
    pacing: str                 # velocidades relativas, ritmo de partida
    visual_style: str           # paleta, look de sprites, casa de referencia
    level_structure: str
    sources: list[ReferenceSource]
```

Obtención: `client.responses.parse(tools=[{"type": "web_search"}],
text_format=GameReference)` sobre el brief del proyecto. Un único punto de
entrada, `research(brief, target) -> GameReference`, con el cliente inyectado
igual que en `ResponsesProgramWriter`, para poder ejercitar el resto sin red.

Cuando no se identifica ningún título, devuelve `identified=False` y Studio sigue
con el pack de género como hoy. **No se inventa un juego que no existe**: una
ficha con `identified=False` no genera propuesta de diseño.

Persistencia en `<proyecto>/reference.yml`, YAML atómico por el mismo camino que
`store.py` usa para `game.yml`. Editable a mano. No se vuelve a buscar salvo
petición explícita.

### 2. Diseño derivado — `reference_proposal` en `llmz80/studio/editing.py`

La ficha produce un `DesignProposal` tipado sobre `game.yml`, reutilizando el
mecanismo de propuesta y diff que `planner.py` ya tiene para las sugerencias de
IA. Puede proponer:

- terreno autoral por nivel (`LevelSpec.tiles`, que ya lo admite desde P1),
- entidades, sus cuentas y sus velocidades relativas,
- `presentation.palette` y `presentation.style`,
- `gameplay.lives`, `level_count` y `difficulty_curve`,
- las escenas del flujo de partida.

Toda propuesta pasa por la validación existente antes de mostrarse: la gate de
solvabilidad rechaza un mapa que selle una zona, y `validate_backend_support`
rechaza lo que el target no aguante. Una propuesta inválida se muestra con su
motivo, no se aplica a medias.

El pack de género pasa a ser el fallback, no el molde.

### 3. Sprites — `llmz80/studio/spriting.py`

Cuatro pasos, cada uno con artefacto en disco para poder inspeccionarlo:

1. **Prompt**: se compone de `visual_style` y `publisher` de la ficha, el rol de
   la entidad, y las restricciones reales del target. Reutiliza las plantillas
   ya presentes en `resources/sprite_prompt_spectrum.txt` y
   `resources/sprite_prompt_amstrad_cpc_mode{0,1,2}.txt`.
2. **Generación**: una sola imagen por entidad conteniendo una **hoja de cuatro
   fotogramas** en rejilla. Una llamada por fotograma pierde la identidad del
   personaje entre fotogramas; la hoja la conserva. La rejilla se parte de forma
   determinista por coordenadas, no por detección.
3. **Cuantización**: reutiliza `image_utils` (`_clean_image`, `_scale_image`,
   `_process_image`). Spectrum: 16×16 a 1 bpp, con un atributo de color por
   celda de 8×8. CPC modo 0: 16 plumas, 2 px/byte. CPC modo 1: 4 plumas,
   4 px/byte. La máscara sale del canal alfa.
4. **Empaquetado**: bytes y máscara a un `.h` generado en `build/generated_assets`,
   referenciado desde `AssetSpec` con su número de fotogramas.

### 4. Blitter — `resources/studio_lib/{spectrum,cpc}/platform.c`

API nueva en `platform.h`:

```c
void plat_sprite(unsigned char col_px, unsigned char row_px,
                 unsigned char sprite_id, unsigned char frame);
```

- **Spectrum**: blit enmascarado alineado a byte en horizontal (pasos de 8 px) y
  libre en vertical (1 px). Es lo que hacía buena parte del catálogo de la época
  y cuesta poco. Pre-desplazamiento de ocho copias como opción por entidad:
  16×16 con máscara son 64 bytes por fotograma, por ocho desplazamientos y
  cuatro fotogramas son 2 KB por entidad, así que lo autoriza la gate de
  presupuesto de datos estáticos, no el modelo.
- **CPC**: `cpct_drawSpriteMasked` a granularidad natural de 2 px en modo 0.

`plat_cell` se conserva para el terreno; los actores pasan a `plat_sprite`.

## Gates de game feel

Cada una medida sobre evidencia, no inferida de que el código exista.

**Animación y reacción.** El contrato de estado observable gana `g_anim_frame`.
La sonda de memoria exige que cambie mientras el jugador se mueve y que se quede
quieto cuando no hay entrada. La secuencia de muerte exige `g_lives`
decrementado **y** la pantalla distinta durante los fotogramas siguientes al
impacto, con el mismo mecanismo de comparación de capturas que ya usa la gate
de "el juego se ve".

**Transiciones y ritmo.** Escenario guionizado nuevo que recorre título → juego →
muerte → game over → título leyendo `g_state`, y otro que recorre completar
nivel → aviso → siguiente nivel leyendo `g_level`. Cierra el hueco que el
roadmap dejó abierto: "la sonda prueba que recoger puntúa; no prueba todavía que
una colisión cueste una vida ni que completar un nivel avance".

**Dificultad perceptible.** Chequeo en tiempo de diseño en
`quality.design_quality_report`: velocidad o número de enemigos monótono
creciente por nivel, y `estimated_steps` de la solvabilidad no decreciente. El
build falla si el nivel 3 no es medible más duro que el 1.

Limitación aceptada: en CPC las sondas de memoria siguen sin funcionar, así que
las dos primeras gates abstienen allí igual que hoy, y sólo se aplica la gate de
diseño. No se marca como aprobado lo que no se ha observado.

## Corrección al prompt del escritor

`generator.writing_prompt` gana dos bloques:

- el contenido literal de `resources/studio_lib/common/platform.h`, que hoy no
  se le enseña pese a decirle que lo incluya — origen directo del `plat_sync`
  inventado y de dos intentos perdidos;
- la ficha de referencia cuando existe, para el look y el ritmo.

## TUI de mando — `llmz80/studio/tui.py`

Altura fija en reposo: cabecera, brief, línea de etapas, atajos. Los paneles se
abren encima, uno cada vez.

```
LLMZ80 Studio · zampabolas · spectrum · maze_chase
┌ Brief ───────────────────────────────────────────┐
│ Zampabolas runs through a walled maze eating...  │
└──────────────────────────────────────────────────┘
referencia ✓  diseño ✓  sprites ✓  programa ✗  gates —  release —
  Zampa Bolas (Iber Soft, 1985) · 3 fuentes
[m] mapa  [e] entidades  [s] sprites  [d] diff  [l] log
```

Campos que se retiran y a dónde va cada uno:

| Campo | Destino | Motivo |
|---|---|---|
| `Style` | Derivado de `visual_style` de la ficha | Texto libre que sólo alimentaba el prompt |
| `Win score` | Derivado de coleccionables × puntos | `quality.py` ya lo trata como fuente única; el campo permitía contradecirla |
| `Open` | Selector del workspace | `store.list_projects()` ya sabe listarlos; escribir la ruta a mano sobra |
| `Target`, `Type` | Diálogo de creación | Inmutables después de crear el proyecto |
| `Lives` | Panel de entidades | Es un parámetro de diseño, no de proyecto |

El panel `[s]` muestra los sprites generados como pixel art en el terminal, con
`image_utils.display_sprite`, para aprobar o regenerar antes de que entren al
build. El panel `[d]` muestra el diff de la propuesta de diseño y lo acepta o lo
descarta.

`render_map` y las operaciones de edición se quedan donde están: la interfaz
sigue sin decidir nada sobre un diseño, que es lo que mantiene las mismas
operaciones utilizables desde un script.

## Estrategia de pruebas

- `reference.py`: cliente falso que devuelve fichas fijas. Se prueba que
  `identified=False` no genera propuesta, que la ficha se archiva y se relee, y
  que una ficha corrupta en disco se rechaza en vez de propagarse.
- `reference_proposal`: sobre fichas fijas, se prueba que una propuesta con un
  mapa que sella una zona se rechaza con su motivo, y que aplicarla es
  reversible por el historial de revisiones que `store.py` ya mantiene.
- `spriting.py`: sobre imágenes fijas en disco, sin llamada de generación. Se
  prueba el partido de la hoja, la cuantización a cada target y que la máscara
  cubre exactamente los píxeles transparentes.
- Blitter: programa mínimo por target que dibuja un sprite conocido, compilado
  con la toolchain real, y comparación de la captura del emulador contra el
  patrón esperado.
- Gates: escenarios guionizados sobre un programa de referencia que aprueba y
  otro mutado que falla cada gate, para probar que la gate distingue.
- TUI: `render_map` y el estado de la línea de etapas se prueban como funciones
  sobre datos, sin aplicación viva, igual que hoy.

## Riesgos

- **La búsqueda traerá fichas incompletas o cruzadas** con otro juego del mismo
  nombre, sobre todo en títulos españoles oscuros. Mitigación: la ficha es un
  archivo editable, la propuesta pasa por diff, y una corrección a mano se queda
  hecha.
- **El presupuesto de datos estáticos**: sprites pre-desplazados en Spectrum 48K
  se comen la RAM deprisa. Mitigación: lo decide la gate de presupuesto y por
  defecto no se pre-desplaza.
- **Reproducibilidad**: un build no repite la búsqueda, pero un proyecto creado
  hoy y otro mañana con el mismo brief pueden partir de fichas distintas. Se
  acepta: es el precio de la búsqueda en vivo, y queda registrado en las fuentes
  con su fecha.

## Secuencia

1. `platform.h` al prompt del escritor. Barato, independiente, recupera dos
   intentos por generación desde el primer día.
2. `reference.py` y `reference.yml`.
3. `reference_proposal` y el diff.
4. Blitter enmascarado en ambos targets, con sprites fijos de prueba.
5. `spriting.py` y la cadena de generación.
6. Gates de game feel.
7. TUI de mando sobre todo lo anterior.
