# Game feel medido y TUI de mando — Plan de implementación (3 de 3)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Que las tres cosas que separan un juego de un bucle que se mueve — que los actores se animen y reaccionen, que la partida tenga principio y final, y que el nivel 3 sea medible más duro que el 1 — dejen de ser aspiraciones y pasen a ser medidas; y que la interfaz deje de ser tres pestañas con campos muertos y pase a ser una pantalla de mando.

**Architecture:** Las gates nuevas viven donde ya viven sus hermanas: lo que se puede decidir sobre el diseño va a `quality.py`, y lo que exige ver el programa corriendo se mide leyendo memoria emulada entre pasos del guion. Una regla que no se puede observar en una máquina se abstiene allí en vez de aprobar. La TUI se reescribe sobre `StudioService`, que ya expone todas las operaciones, así que la pantalla nueva no decide nada que la vieja decidiera.

**Tech Stack:** Python 3.10+, pydantic v2, Textual, ZEsarUX vía ZRCP, Caprice32, pytest.

**Planes hermanos, ambos completados y mergeados:** 1 de 3, referencias reales. 2 de 3, sprites en pantalla.

---

## Hechos verificados del código actual

Comprobados antes de escribir el plan.

- `llmz80/core/state_contract.py` define `STATE_CONTRACT`, una tupla de `StateSymbol(name, width, required, meaning)`. De ahí salen `PROBE_WIDTHS`, `REQUIRED_SYMBOLS` y el texto de `contract_prompt()`. **Añadir un símbolo ahí lo hace sondable y lo mete en el prompt del escritor sin tocar nada más**: `probes.py` importa `PROBE_WIDTHS` y filtra por él tanto el `.map` de z88dk como el `.noi` de SDCC.
- `llmz80/quality/emulator_smoke.py` conecta por ZRCP y **lee las sondas después de cada paso del guion**, dejando cada lectura en `step_readings` con su `id` y su `read`. También guarda capturas antes, durante y después, y `_image_observation` calcula `sha256`, `dominant_fraction` y `non_dominant_pixels` de cada una.
- `AcceptanceScenario.expect` es `dict[str, int]`: igualdad exacta contra un valor. **No puede expresar "cambió respecto al paso anterior"**. Una gate comparativa tiene que leer `step_readings`, no ampliar `expect`.
- `acceptance.derive_scenarios` sólo rellena `start_game` y `collect_scores`. `enemy_costs_life` existe como prosa y nunca se vuelve ejecutable; el comentario dice por qué: alcanzar a un enemigo depende de dónde haya patrullado.
- `solvability.sweep_plan` elige **una sola dirección** mantenida, a propósito: mantener una tecla es lo único que un emulador acotado entrega con fiabilidad, y así la puntuación esperada es exacta.
- Los enemigos con `behaviour: chase` van hacia el jugador. Eso hace que el encuentro sí sea predecible sin tocar el teclado: basta esperar.
- `quality.design_quality_report` reúne checks nombrados en un dict, deriva `failures` y `quality_pass`, e incluye informes anexos. Hay dos precedentes recientes de gate añadida así: `every_level_is_solvable` y `every_level_has_genre_shaped_terrain`.
- Las sondas de memoria **no funcionan en CPC**: el Caprice32 instalado no resuelve `CAP32_SNAPSHOT` como autocmd. Está documentado en `docs/STUDIO_ROADMAP.md` y confirmado durante el plan 2.
- `llmz80/studio/tui.py` son 462 líneas: tres `TabPane` (Project, Map, Log), campos `f-title`, `f-target`, `f-genre`, `f-open`, `f-lives`, `f-score`, `f-style`, `f-brief`, una tabla de entidades y el mapa. `tests/test_studio_tui.py` tiene 9 tests.
- `StudioService` expone hoy: `create_project`, `open_project`, `save_project`, `generate_sources`, `add_asset`, `research_reference`, `reference`, `propose_from_reference`, `draw_sprites`, `build`, `runtime_test`, `verify_program`, `write_program`, `release`. **`propose_from_reference` devuelve una tupla de cuatro**, no de dos: propuesta, diff, proyecto ya validado y lista de rechazos.
- `editing.editing_status` devuelve `solvable`, `solvability_failures`, `warnings`, `buildable`, `backend_error`, `structured`, `structure_failures` y `ready`.

## Lo que este plan NO hace

- No añade audio. Se descartó explícitamente al decidir el alcance.
- No implementa pathfinding. El chase sigue siendo un paso codicioso de un eje.
- No arregla las sondas del CPC. Eso depende de otro emulador o de otra build de Caprice32.

---

## Estructura de archivos

| Archivo | Responsabilidad |
|---|---|
| `llmz80/core/state_contract.py` (modificar) | Un símbolo nuevo: el fotograma de animación |
| `llmz80/studio/feel.py` (crear) | Gates comparativas sobre `step_readings`: animación y reacción |
| `llmz80/studio/difficulty.py` (crear) | Gate de diseño: la curva es monótona y medible |
| `llmz80/studio/acceptance.py` (modificar) | `enemy_costs_life` y `level_advances` pasan a ejecutables cuando el diseño los predice |
| `llmz80/studio/quality.py` (modificar) | Recoge las gates nuevas |
| `llmz80/studio/services.py` (modificar) | El informe de runtime incluye el veredicto de feel |
| `llmz80/studio/screen.py` (crear) | Estado de la pantalla de mando como datos puros |
| `llmz80/studio/tui.py` (reescribir) | La pantalla |

---

### Task 1: El programa dice por qué fotograma va

**Files:**
- Modify: `llmz80/core/state_contract.py`
- Test: `tests/test_runtime_contracts.py`

- [ ] **Step 1: Escribir los tests que fallan**

```python
def test_the_contract_carries_an_animation_frame():
    assert "g_anim_frame" in SYMBOLS_BY_NAME
    assert SYMBOLS_BY_NAME["g_anim_frame"].required is False
    assert PROBE_WIDTHS["g_anim_frame"] == 1


def test_the_prompt_explains_when_the_animation_frame_must_change():
    text = contract_prompt()

    assert "g_anim_frame" in text
    assert "moves" in text
```

- [ ] **Step 2: Verificar que fallan**

Run: `.venv/bin/python -m pytest tests/test_runtime_contracts.py -q`

- [ ] **Step 3: Implementar**

Añadir a `STATE_CONTRACT`, entre los opcionales:

```python
    StateSymbol(
        "g_anim_frame",
        1,
        False,
        "the animation frame the player is currently drawn with; it must advance "
        "while the player moves and hold still while it does not",
    ),
```

El significado se imprime tal cual en `contract_prompt`, así que esa frase **es** la instrucción al escritor. Redáctala como tal.

No lo marques `required`. Un diseño sin animación no debe fallar el contrato entero; la gate de animación es la que lo juzga, y se abstiene cuando el símbolo no está.

- [ ] **Step 4: Verificar**

Run: `.venv/bin/python -m pytest tests -q`
Expected: verde. Usa el intérprete del venv; el `python` del sistema no tiene `pytest-asyncio`.

- [ ] **Step 5: Commit**

```bash
git add llmz80/core/state_contract.py tests/test_runtime_contracts.py
git commit -m "feat(core): let a program say which animation frame it is drawing"
```

---

### Task 2: La gate de animación

**Files:**
- Create: `llmz80/studio/feel.py`
- Test: `tests/test_studio_feel.py`

`expect` no sirve aquí: pide igualdad contra un número, y lo que hay que probar es que un valor **cambió** entre dos pasos y **no cambió** en otro. Esta gate lee `step_readings` del informe del emulador.

- [ ] **Step 1: Escribir los tests que fallan**

```python
"""Judging animation from what memory showed between steps."""

from llmz80.studio.feel import animation_report


def _runtime(readings):
    return {"step_readings": [{"id": name, "read": read} for name, read in readings]}


def test_a_frame_that_advances_while_moving_and_rests_when_idle_passes():
    report = animation_report(_runtime([
        ("move_a", {"g_anim_frame": 0}),
        ("move_b", {"g_anim_frame": 2}),
        ("idle", {"g_anim_frame": 2}),
    ]))

    assert report["quality_pass"] is True
    assert report["observed"] is True


def test_a_frame_that_never_moves_fails():
    """A program that declares the symbol and never touches it is not animating."""
    report = animation_report(_runtime([
        ("move_a", {"g_anim_frame": 1}),
        ("move_b", {"g_anim_frame": 1}),
        ("idle", {"g_anim_frame": 1}),
    ]))

    assert report["quality_pass"] is False
    assert "never advanced" in " ".join(report["failures"])


def test_a_frame_that_keeps_advancing_while_idle_fails():
    """Animation driven by a free-running counter is not reacting to the player."""
    report = animation_report(_runtime([
        ("move_a", {"g_anim_frame": 0}),
        ("move_b", {"g_anim_frame": 2}),
        ("idle", {"g_anim_frame": 4}),
    ]))

    assert report["quality_pass"] is False
    assert "while idle" in " ".join(report["failures"])


def test_a_target_that_never_reported_the_symbol_abstains():
    """No reading is not a pass and not a failure. The CPC has no probe adapter."""
    report = animation_report(_runtime([("move_a", {}), ("idle", {})]))

    assert report["observed"] is False
    assert report["quality_pass"] is None
```

- [ ] **Step 2: Verificar que fallan**

- [ ] **Step 3: Implementar**

Crear `llmz80/studio/feel.py` con `animation_report(runtime) -> dict`. Reglas:

- necesita al menos dos pasos con lectura de `g_anim_frame` en los que el jugador se movía, y al menos uno en el que no;
- pasa si el valor avanzó entre los de movimiento **y** se mantuvo en el de reposo;
- si no hay ninguna lectura del símbolo, `observed: False` y `quality_pass: None`. Abstenerse no es aprobar, y es lo que ya hacen `probe_report` y `acceptance_report` en `services.py`; sigue esa forma exacta de informe, con `schema_version`, `observed`, `failures` y `quality_pass`.

Cómo sabe qué pasos eran de movimiento: por el `hold` del guion. Un paso con `hold: "none"` es reposo; cualquier dirección es movimiento. Decide si lo lees del guion o del propio `step_readings`, y dilo.

- [ ] **Step 4: Verificar y commit**

```bash
git add llmz80/studio/feel.py tests/test_studio_feel.py
git commit -m "feat(studio): judge animation from memory instead of assuming it"
```

---

### Task 3: Perder una vida deja de ser prosa

**Files:**
- Modify: `llmz80/studio/acceptance.py`
- Test: `tests/test_studio_acceptance.py`

El comentario que hay hoy en `derive_scenarios` dice que alcanzar a un enemigo depende de dónde haya patrullado, y por eso `enemy_costs_life` se queda en prosa. Eso es cierto para `patrol_h` y `patrol_v`. **No lo es para `chase`**: un enemigo que persigue viene solo. El encuentro se guioniza esperando.

- [ ] **Step 1: Escribir los tests que fallan**

```python
def test_a_chasing_enemy_makes_losing_a_life_executable():
    project = create_default_project("Chase", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)

    scenario = next(s for s in derive_scenarios(project) if s.id == "enemy_costs_life")

    assert scenario.executable
    assert scenario.hold == "none"
    assert scenario.expect["g_lives"] == project.gameplay.lives - 1
    assert scenario.expect["g_state"] == STATE_PLAYING


def test_a_design_with_no_chasing_enemy_leaves_it_as_prose():
    """A patrolling enemy's position depends on where it wandered; that is not predictable."""
    project = create_default_project("Patrol", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)
    project = editing.set_entity_behaviour(project, "enemy", "patrol_h")

    scenario = next(s for s in derive_scenarios(project) if s.id == "enemy_costs_life")

    assert not scenario.executable
```

- [ ] **Step 2: Verificar que fallan**

- [ ] **Step 3: Implementar**

En `derive_scenarios`, cuando exista un enemigo con `behaviour == "chase"` y una ruta entre su casilla de aparición y la del jugador, rellena `hold="none"`, `frames` suficientes para que recorra esa distancia a su paso, y `expect` con la vida perdida y el estado jugando.

Los frames por celda de cada velocidad ya están en `FRAMES_PER_CELL` en este mismo archivo; úsalos, no los reinventes. El margen de `SWEEP_MARGIN_FRAMES` existe por la misma razón que aquí: arranque y redondeo. Reutilízalo o justifica otro.

Para la distancia, `solvability.py` ya calcula caminos. Mira qué expone antes de escribir una BFS nueva.

**Ojo con el orden.** `runtime_script` ejecuta los pasos acumulando en un solo arranque, sin resetear. Un paso que pierde una vida cambia lo que los pasos siguientes pueden esperar. Comprueba en qué orden quedan y si `collect_scores` sigue siendo cierto después. Si el orden importa, hazlo explícito en el código, no en un comentario.

- [ ] **Step 4: Verificar y commit**

```bash
git add llmz80/studio/acceptance.py tests/test_studio_acceptance.py
git commit -m "feat(studio): script the encounter that costs a life"
```

---

### Task 4: La curva de dificultad, medida

**Files:**
- Create: `llmz80/studio/difficulty.py`
- Test: `tests/test_difficulty.py`

Hoy `gameplay.difficulty_curve` es una etiqueta — `flat`, `linear` o `stepped` — que nada comprueba. Un diseño puede declarar `linear` y tener tres niveles idénticos.

- [ ] **Step 1: Escribir los tests que fallan**

Cubre al menos: una curva `linear` cuyos niveles no se endurecen falla y nombra los niveles; una que sí, pasa; `flat` no exige endurecimiento pero sí prohíbe que se ablande; un diseño de un solo nivel pasa por vacuidad.

- [ ] **Step 2: Verificar que fallan**

- [ ] **Step 3: Implementar**

`difficulty_report(project) -> dict`, con la misma forma que `solvability_report` y `structure_report`.

Qué medir, y esto es tuyo decidirlo con criterio: los enemigos por nivel salen de los `spawns` de cada `LevelSpec`, no de `EntitySpec.count`, que es global. La longitud del recorrido la da `solvability` como `estimated_steps`. La velocidad es global por entidad, así que **no** puede variar por nivel: dilo en el informe en vez de fingir que la mides.

Si concluyes que con el IR de hoy la única señal real es el número de enemigos por nivel y la longitud del recorrido, eso es un hallazgo legítimo: escríbelo en el docstring y mide esas dos. Una gate honesta y estrecha vale más que una amplia e inventada.

- [ ] **Step 4: Verificar y commit**

```bash
git add llmz80/studio/difficulty.py tests/test_difficulty.py
git commit -m "feat(studio): refuse a difficulty curve that does not curve"
```

---

### Task 5: Recoger las gates nuevas

**Files:**
- Modify: `llmz80/studio/quality.py`, `llmz80/studio/services.py`
- Test: `tests/test_studio_quality.py`

- [ ] **Step 1: Tests**

Que `design_quality_report` incluya el check de dificultad entre sus `checks` y su informe anexo, y que `runtime_test` incluya el veredicto de animación en el informe que escribe.

- [ ] **Step 2: Implementar**

Sigue exactamente el patrón de `every_level_has_genre_shaped_terrain`, que es el precedente más reciente. En `services.runtime_test`, la animación se juzga junto a `probe_report` y `acceptance_report`, y **un `quality_pass` en `False` debe bajar el veredicto global**, igual que hacen las otras dos. Un `None` no.

- [ ] **Step 3: Verificar y commit**

```bash
git commit -m "feat(studio): let feel and difficulty decide a build"
```

---

### Task 6: Decirle al escritor qué se le va a medir

**Files:**
- Modify: `llmz80/studio/acceptance.py`
- Test: `tests/test_studio_acceptance.py`

Handing the test over before the code is written es la política declarada de este módulo, en su propio docstring. Las gates nuevas tienen que aparecer en el prompt.

El símbolo de animación ya entra solo por `contract_prompt`. Falta que el prompt diga que la animación se mide entre pasos: que debe avanzar mientras el jugador se mueve y quedarse quieta cuando no, y que un contador libre suspende.

Dilo en una o dos frases. El prompt ya es largo, y este proyecto ya decidió dos veces que gastar atención en explicar ausencias es peor que el silencio.

- [ ] **Commit**

```bash
git commit -m "feat(studio): tell the writer that its animation will be measured"
```

---

### Task 7: El estado de la pantalla, como datos

**Files:**
- Create: `llmz80/studio/screen.py`
- Test: `tests/test_screen.py`

Antes de dibujar nada, el estado de la pantalla de mando tiene que ser una función pura sobre el proyecto y sus informes, para poder probarlo sin aplicación viva. `render_map` en la TUI actual ya sigue ese principio; esto lo extiende.

- [ ] **Step 1: Tests**

La forma, para que las tareas 8 y 9 la usen sin adivinarla:

```python
@dataclass(frozen=True)
class Stage:
    name: str                                  # "referencia", "diseño", ...
    state: Literal["done", "pending", "failed"]
    detail: str = ""                           # "Zampa Bolas (System 4, 1990) · 8 fuentes"


def stage_line(project: GameProject | None, directory: Path | None) -> list[Stage]: ...
```

Las etapas, en este orden: referencia, diseño, sprites, programa, gates, release.

Cubre: sin proyecto no hay etapas; un proyecto recién creado tiene referencia y sprites pendientes y diseño listo; un proyecto con `reference.yml` identificado muestra el título y el número de fuentes; uno con `program/main.c` muestra el programa escrito; uno con `build/studio_quality_report.json` muestra el veredicto de las gates.

Cada estado se decide mirando el disco y el diseño, nunca llamando a una API.

- [ ] **Step 2: Implementar**

Tres estados por etapa y nada más: hecha, pendiente, fallida. Un cuarto estado invita a inventar matices que la línea no puede mostrar.

- [ ] **Step 3: Verificar y commit**

```bash
git commit -m "feat(studio): model the command screen as data"
```

---

### Task 8: La pantalla de mando

**Files:**
- Rewrite: `llmz80/studio/tui.py`
- Test: `tests/test_studio_tui.py`

```
LLMZ80 Studio · zampabolas · spectrum · maze_chase
┌ Brief ───────────────────────────────────────────┐
│ Zampabolas runs through a walled maze eating...  │
└──────────────────────────────────────────────────┘
referencia ✓  diseño ✓  sprites ✓  programa ✗  gates —  release —
  Zampa Bolas (System 4, 1990) · 8 fuentes
[m] mapa  [e] entidades  [s] sprites  [d] diff  [l] log
```

Altura fija en reposo: cabecera, brief, línea de etapas, atajos. Los paneles se abren encima, uno cada vez.

Campos que se retiran y a dónde va cada uno:

| Campo | Destino | Motivo |
|---|---|---|
| `Style` | Panel de diseño | Texto libre que sólo alimenta el prompt; ahora además lo propone `adapt` |
| `Win score` | Derivado | `quality.py` ya lo trata como fuente única; el campo permitía contradecirla |
| `Open` | Selector del workspace | `store.list_projects()` ya sabe listarlos |
| `Target`, `Type` | Diálogo de creación | Inmutables después de crear |
| `Lives` | Panel de entidades | Parámetro de diseño, no de proyecto |

Los nueve tests que hay hoy en `tests/test_studio_tui.py` describen comportamiento que en su mayor parte sigue siendo cierto: que crear un proyecto lo guarda, que una operación lenta no congela la interfaz, que una edición refusada avisa en vez de romper. **Léelos antes de tocar nada** y consérvalos donde el comportamiento sobreviva; una reescritura que tira sus propios tests no ha demostrado nada.

Los atajos de acción — escribir, construir, probar, exportar — se conservan tal cual. Los nuevos son los que el plan 1 y el 2 dejaron sin interfaz: investigar la referencia, aplicar la adaptación con su diff, dibujar los sprites.

Textual necesita bucle de eventos para probarse; `tests/test_studio_tui.py` ya usa `pytest-asyncio` y `run_test()`. Sigue ese patrón.

- [ ] **Commit**

```bash
git commit -m "refactor(studio)!: one command screen instead of three tabs"
```

---

### Task 9: Las operaciones que faltaban en la interfaz

**Files:**
- Modify: `llmz80/studio/tui.py`
- Test: `tests/test_studio_tui.py`

`reference`, `adapt` y `sprites` sólo existen en el CLI. Llévalos a la pantalla, con las mismas reglas que allí: avisar de que gastan dinero antes de gastarlo, preguntar antes de pisar una ficha corregida a mano o arte existente, y en el caso de `adapt` enseñar el diff y no aplicar nada sin consentimiento.

Recuerda que `propose_from_reference` devuelve **cuatro** valores, incluido el proyecto ya validado y la lista de rechazos que el bucle de reparación fue superando. Enséñalos: un usuario que espera tres llamadas al modelo merece saber qué se está reparando.

- [ ] **Commit**

```bash
git commit -m "feat(studio): research, adapt and draw from the screen"
```

---

### Task 10: Documentar

**Files:**
- Modify: `README.md`, `docs/STUDIO_ROADMAP.md`

El roadmap tiene puntos abiertos que este plan cierra y otros que no. Léelos uno a uno.

Estos dos son suyos:

> The probe proves that collecting scores. It does not yet prove that a collision costs a life or that clearing a level advances it.

> nothing yet animates — the blitter takes a frame index and the header carries frame counts, but no generated game steps through them, and no gate observes animation.

Bórralos sólo en la medida en que este trabajo los cierre, y con la asimetría entre máquinas en la columna de evidencia: en CPC las gates de animación y de encuentro se abstienen, porque el Caprice32 instalado no vuelca memoria.

Si al terminar resulta que ningún juego generado anima todavía de verdad —porque el escritor tiene que aprender a usar `plat_sprite` con el índice de fotograma— dilo. Sería el mismo hallazgo honesto con el que cerró el plan 2.

- [ ] **Commit**

```bash
git commit -m "docs: record what is now measured about how a game feels"
```

---

## Verificación final del plan

- [ ] `.venv/bin/python -m pytest tests` pasa entero
- [ ] Un juego que no anima falla la gate en Spectrum, con el motivo
- [ ] El mismo juego en CPC se abstiene, y el informe lo dice
- [ ] Un diseño de tres niveles idénticos con curva `linear` falla en tiempo de diseño
- [ ] La pantalla de mando cabe en reposo sin desplazamiento y abre cada panel bajo demanda
- [ ] `llmz80 studio` sigue haciendo todo lo que hacía, más referencia, adaptación y sprites
