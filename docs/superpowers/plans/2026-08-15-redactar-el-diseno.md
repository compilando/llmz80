# Redactar el diseño — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Dar al pipeline la etapa que le falta: la que convierte un brief en entidades, tiles y mecánicas, para que `adapt` tenga algo que vestir y `write` algo que implementar.

**Architecture:** Una etapa nueva, `redacción`, entre `referencia` y `diseño`. Emite el mismo `ProjectProposal` que ya emite el diseñador, así que hereda el diff, las rutas protegidas y la validación transaccional de `apply_proposal` sin escribir ninguna de las tres. Lo que cambia es el prompt, las rutas que se le permiten y dos formas de valor nuevas — `ProjectChange` hoy sabe llevar texto, número, filas y spawns, y una entidad es un objeto. Redacta sólo sobre un diseño que no dice nada; uno que ya declara mecánicas es de alguien y no se reinterpreta.

**Tech Stack:** Python 3.10+, pydantic v2, OpenAI Responses API con structured outputs, pytest.

---

## Por qué existe esta etapa

`docs/superpowers/plans/2026-08-14-suelo-de-calidad-y-motores.md` cerró el suelo de calidad: un diseño que lleva brief y no declara mecánicas ya no se escribe (`quality.design_quality_report`), y `pipeline.write` se niega antes de pagar al escritor. Eso destapó que detrás de la puerta no hay nadie.

- `adapt` no redacta, y lo dice en su propio prompt: *«el diseño ya decidió qué es este juego -- el `kind` de cada entidad, las mecánicas que declara y cómo se conectan sus pantallas están decididos y no son tuyos para cambiarlos»* (`reference_design.py:29-42`). Viste un diseño que ya existe.
- `samples.blank_project` da una entidad `actor`, dos tiles y `mechanics=[]` (`samples.py:112`), y su propio docstring dice que no es una plantilla y no tiene autoridad.

Entre los dos no hay nadie. Por eso los dos proyectos v4 del repo llegaron al escritor con `mechanics: []` — uno de ellos desde una ficha que había identificado correctamente *Harrier Attack!* de Durell — y por eso `llmz80 make` se detiene hoy en `programa` cuando la investigación no identifica nada.

**La etapa va después de `referencia`, no antes.** Cuando hay ficha, la redacción la lee: la de `zampabolas` traía cinco mecánicas documentadas con tres fuentes citadas que nadie usó nunca. Cuando no la hay, redacta del brief solo — y eso es exactamente lo que desatasca el callejón de `make`.

**Lo que esta etapa no es.** No sustituye a `adapt` ni le quita trabajo. Redacción decide *qué es* el juego; adaptación decide *a qué se parece*. Mantener las dos separadas es lo que deja intacto el prompt de `adapt`, que existe para impedir que una ficha reinterprete un juego que ya está decidido.

---

## File Structure

**Se crean:**

| Fichero | Responsabilidad |
|---|---|
| `llmz80/studio/drafting.py` | El prompt de redacción, el protocolo `DesignDrafter`, el bucle `draft_and_apply` y su feedback de reparación |
| `tests/test_studio_drafting.py` | |

**Se modifican:**

| Fichero | Cambio |
|---|---|
| `llmz80/studio/planner.py` | `EntityValue` y `TileValue`, y los campos `value_entity` / `value_tile` en `ProjectChange` |
| `llmz80/studio/pipeline.py` | La etapa `draft` |
| `llmz80/studio/make.py` | `redacción` en el orden, y el callejón que deja de serlo |
| `llmz80/cli.py` | `llmz80 project draft` |
| `tests/test_studio_planner_gate.py` | Las formas de valor nuevas |
| `tests/test_studio_make.py` | El orden con cinco etapas |

**Orden y dependencias:** 1 → 2 → 3 → 4 → 5 → 6. La tarea 1 es la que desbloquea todo: sin una forma de valor para un objeto, una entidad no se puede proponer.

**Comandos:** `make test`; un test suelto con `.venv/bin/python -m pytest tests/test_x.py::test_y -v`.

---

## Task 1: Las formas de valor que una redacción necesita

`ProjectChange` lleva `value_text`, `value_number`, `value_rows` y `value_spawns`, y su docstring dice por qué no lleva un `value` genérico: los structured outputs de OpenAI exigen que cada propiedad tenga un tipo JSON concreto, y `Any` no tiene ninguno. `SpawnValue` existe por esa misma razón. Una entidad y un tile son objetos, así que necesitan lo mismo.

**Files:**
- Modify: `llmz80/studio/planner.py`
- Test: `tests/test_studio_planner_gate.py`

- [ ] **Step 1: Write the failing test**

```python
def test_a_change_can_carry_a_whole_entity():
    """A design that states nothing has no entity to edit a field of: the
    drafting stage has to add one, and `value_text` cannot hold an object."""
    from llmz80.studio.planner import EntityValue, ProjectChange

    change = ProjectChange(
        path="/entities/-",
        operation="add",
        reason="the brief asks for enemy fighters and the design has none",
        value_entity=EntityValue(id="caza", kind="enemigo", notes="cruza la pantalla disparando"),
    )

    assert change.value == {
        "id": "caza",
        "kind": "enemigo",
        "sprite": None,
        "poses": [],
        "count": 1,
        "colour": None,
        "notes": "cruza la pantalla disparando",
    }


def test_a_change_can_carry_a_whole_tile():
    from llmz80.studio.planner import ProjectChange, TileValue

    change = ProjectChange(
        path="/tiles/-",
        operation="add",
        reason="the brief asks for water the player cannot cross",
        value_tile=TileValue(id="agua", char="~", traits=["solid"]),
    )

    assert change.value["id"] == "agua"
    assert change.value["char"] == "~"
    assert change.value["traits"] == ["solid"]


def test_an_entity_and_a_tile_are_still_only_one_value_each():
    """The one-value-per-change rule is what keeps `value` unambiguous, and a
    new shape must not become an exception to it."""
    import pytest

    from llmz80.studio.planner import EntityValue, ProjectChange, TileValue

    with pytest.raises(ValueError, match="exactly one value_"):
        ProjectChange(
            path="/entities/-",
            operation="add",
            reason="two shapes at once",
            value_entity=EntityValue(id="uno", kind="actor"),
            value_tile=TileValue(id="dos", char="#"),
        )
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_studio_planner_gate.py -v -k "entity or tile"`
Expected: FAIL con `ImportError: cannot import name 'EntityValue'`

- [ ] **Step 3: Write minimal implementation**

En `llmz80/studio/planner.py`, junto a `SpawnValue`:

```python
class EntityValue(BaseModel):
    """One whole entity, in the shape `EntitySpec` validates.

    Flat and with every field concrete, for the reason `ProjectChange`'s own
    docstring gives: structured outputs reject a property with no JSON type,
    which is why there is no generic `value` and why `SpawnValue` exists. An
    entity is the first thing a proposal ever needed to *add* rather than
    edit -- the designer only ever touched `/entities/N/notes` of an entity
    that was already there -- and a design that states nothing has none.

    The defaults mirror `EntitySpec`'s own, so a drafter that names only an id
    and a kind gets exactly what a designer writing the same two fields by
    hand would get.
    """

    model_config = ConfigDict(extra="forbid")

    id: str
    kind: str
    sprite: str | None = None
    poses: list[str] = Field(default_factory=list)
    count: int = 1
    colour: str | None = None
    notes: str = ""


class TileValue(BaseModel):
    """One whole tile, in the shape `TileSpec` validates."""

    model_config = ConfigDict(extra="forbid")

    id: str
    char: str
    art: str | None = None
    colour: str | None = None
    traits: list[str] = Field(default_factory=list)
```

En `ProjectChange`, dos campos más y las dos variantes en el validador:

```python
    value_entity: EntityValue | None = None  # a whole entity
    value_tile: TileValue | None = None  # a whole tile
```

```python
        variants = [
            v
            for v in (
                self.value_text,
                self.value_number,
                self.value_rows,
                self.value_spawns,
                self.value_entity,
                self.value_tile,
            )
            if v is not None
        ]
```

Y en la propiedad `value`, devolver `model_dump()` para las dos formas nuevas, igual que se hace con `value_spawns`. Leer cómo lo hace hoy y seguir esa forma exactamente; no inventar una segunda.

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_studio_planner_gate.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add llmz80/studio/planner.py tests/test_studio_planner_gate.py
git commit -m "feat(studio): let a proposal carry a whole entity, not only a field of one"
```

---

## Task 2: La redacción

**Files:**
- Create: `llmz80/studio/drafting.py`
- Test: `tests/test_studio_drafting.py`

- [ ] **Step 1: Write the failing test**

```python
"""Turning a brief into a design that states something."""

import pytest

from llmz80.studio.drafting import (
    DraftRefused,
    draft_and_apply,
    drafting_prompt,
    needs_drafting,
)
from llmz80.studio.editing import rename_project
from llmz80.studio.models import TargetPlatform
from llmz80.studio.planner import ProjectChange, ProjectProposal
from llmz80.studio.samples import blank_project


@pytest.fixture
def blank():
    return rename_project(
        blank_project("Harrier", TargetPlatform.SPECTRUM),
        "Harrier",
        brief="un avión de combate que vuela hacia la derecha; hay scroll y van "
        "apareciendo otros cazas, y se disparan entre ambos",
    )


class ScriptedDrafter:
    """A drafter whose proposals are decided in advance, so the loop is
    testable without an API call -- the same shape `tests/test_studio_
    reference_design.py` uses for the designer."""

    def __init__(self, *proposals: ProjectProposal) -> None:
        self.proposals = list(proposals)
        self.feedback_seen: list[str | None] = []

    def draft(self, project, dossier=None, feedback=None):
        self.feedback_seen.append(feedback)
        return self.proposals[min(len(self.feedback_seen), len(self.proposals)) - 1]


def _mechanics(*sentences: str) -> ProjectProposal:
    return ProjectProposal(
        summary="state what the game does",
        changes=[
            ProjectChange(
                path="/mechanics",
                operation="replace",
                reason="the brief says what this game is and the design said nothing",
                value_rows=list(sentences),
            )
        ],
        risks=[],
    )


def test_a_design_that_states_nothing_wants_drafting(blank):
    assert needs_drafting(blank) is True


def test_a_design_that_already_states_its_rules_is_left_alone(blank):
    """A design with mechanics is somebody's. Redrafting it would be the
    reinterpretation `adapt`'s own prompt exists to refuse."""
    stated = blank.model_copy(update={"mechanics": ["el avión dispara misiles"]})

    assert needs_drafting(stated) is False


def test_a_design_with_no_brief_is_not_drafted_either(blank):
    """Nobody has said what this game should be, so there is nothing to draft
    from and inventing one is exactly what this pipeline must not do."""
    briefless = blank.model_copy(
        update={"metadata": blank.metadata.model_copy(update={"brief": ""})}
    )

    assert needs_drafting(briefless) is False


def test_the_prompt_carries_the_brief_and_what_the_design_has_so_far(blank):
    prompt = drafting_prompt(blank, None)

    assert "avión de combate" in prompt
    assert "actor" in prompt
    assert "20x14" in prompt


def test_the_prompt_carries_the_dossier_when_one_was_researched(blank):
    from llmz80.studio.reference import GameReference, ReferenceSource

    dossier = GameReference(
        identified=True,
        confidence="high",
        title="Harrier Attack!",
        mechanics=["el avión despega del portaaviones", "el combustible se agota"],
        sources=[ReferenceSource(url="https://example.test/x", title="x")],
    )

    prompt = drafting_prompt(blank, dossier)

    assert "Harrier Attack!" in prompt
    assert "el combustible se agota" in prompt


def test_a_draft_that_states_the_rules_is_applied(blank):
    drafter = ScriptedDrafter(_mechanics("el avión dispara misiles hacia delante"))

    result = draft_and_apply(blank, drafter)

    assert result.project.mechanics == ["el avión dispara misiles hacia delante"]
    assert result.refusals == []


def test_a_draft_that_still_says_nothing_is_tried_again_with_the_reason(blank):
    """The design gate is the drafter's own acceptance test, so failing it is
    feedback rather than the end -- the same repair loop `propose_and_apply`
    and `generator.write_program` both run."""
    drafter = ScriptedDrafter(
        ProjectProposal(summary="nothing", changes=[], risks=[]),
        _mechanics("el avión aterriza en el portaaviones para repostar"),
    )

    result = draft_and_apply(blank, drafter, attempts=2)

    assert result.project.mechanics == ["el avión aterriza en el portaaviones para repostar"]
    assert len(result.refusals) == 1
    assert "mechanics" in result.refusals[0]
    assert drafter.feedback_seen[1] is not None


def test_a_drafter_that_never_states_anything_is_refused_with_what_it_kept_missing(blank):
    drafter = ScriptedDrafter(ProjectProposal(summary="nothing", changes=[], risks=[]))

    with pytest.raises(DraftRefused, match="mechanics"):
        draft_and_apply(blank, drafter, attempts=2)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_studio_drafting.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'llmz80.studio.drafting'`

- [ ] **Step 3: Write the implementation**

`llmz80/studio/drafting.py`. La estructura, que debes seguir de cerca porque existe ya dos veces en el repo:

- `DRAFT_SYSTEM_PROMPT`, escrito como el de `reference_design.py`: dice qué rutas puede tocar, con qué forma de valor cada una, y **por qué** las demás no. Las que sí: `/mechanics` (`value_rows`), `/entities/-` (`value_entity`, `add`), `/entities/N/*`, `/tiles/-` (`value_tile`, `add`), `/screens/N/tiles` (`value_rows`), `/screens/N/spawns` (`value_spawns`), `/controls/bindings` sólo si el brief nombra una acción que el proyecto en blanco no tiene tecla para. Fuera: `/budgets` (los impone la máquina), `/target` (protegida), `/metadata` (la escribió una persona).
- `needs_drafting(project) -> bool`: `bool(brief.strip()) and not project.mechanics`. Las dos mitades importan y el docstring debe decir por qué cada una: sin brief nadie ha dicho qué debe ser el juego e inventarlo es el fallo que este pipeline existe para impedir; con mecánicas el diseño ya es de alguien y redactarlo otra vez es la reinterpretación que el prompt de `adapt` rechaza.
- `DesignDrafter` Protocol con `draft(project, dossier=None, feedback=None) -> ProjectProposal`.
- `drafting_prompt(project, dossier)`: el brief, lo que el diseño tiene hoy (reutiliza `design_exam._design_summary` en vez de escribir un segundo resumen — son la misma pregunta desde los dos lados), y la ficha cuando existe.
- `DraftRefused(ValueError)`, para que `make` distinga «el redactor no supo» de cualquier otro `ValueError`, igual que `pipeline.DesignRefused` ya distingue el rechazo del diseño.
- `DraftResult` dataclass con `proposal`, `project`, `refusals`.
- `draft_and_apply(project, drafter, dossier=None, *, attempts=3)`: el bucle. Propone, aplica con `apply_proposal`, y si el resultado no pasa `quality.design_quality_report` lo devuelve como feedback y reintenta. Un `ValueError` de `apply_proposal` es feedback igual, vía `reference_design.repair_feedback`, que ya traduce esos rechazos.

El bucle es el mismo de `propose_and_apply` (`reference_design.py:225-289`) con la aceptación cambiada. **Léelo antes de escribir el tuyo** y dime si conviene extraer el bucle compartido en vez de tener un tercero; si lo tuyo acaba siendo una copia con dos líneas distintas, extraerlo es mejor, y quiero saberlo antes de que existan tres.

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_studio_drafting.py -v`
Expected: PASS, 8 tests

- [ ] **Step 5: Commit**

```bash
git add llmz80/studio/drafting.py tests/test_studio_drafting.py
git commit -m "feat(studio): turn a brief into a design that states something"
```

---

## Task 3: La etapa en el pipeline

**Files:**
- Modify: `llmz80/studio/pipeline.py`
- Test: `tests/test_studio_pipeline.py`

- [ ] **Step 1: Write the failing test**

```python
def test_drafting_saves_what_it_came_to(tmp_path):
    from llmz80.studio.drafting import DesignDrafter  # noqa: F401
    from llmz80.studio.editing import rename_project
    from llmz80.studio.models import TargetPlatform
    from llmz80.studio.pipeline import draft
    from llmz80.studio.planner import ProjectChange, ProjectProposal
    from llmz80.studio.services import StudioService

    service = StudioService.at(tmp_path)
    project, directory = service.create_project("Drafted", TargetPlatform.SPECTRUM)
    project = rename_project(project, "Drafted", brief="un minero cava y esquiva murciélagos")
    service.save_project(project, directory)

    class Drafter:
        def draft(self, project, dossier=None, feedback=None):
            return ProjectProposal(
                summary="state the rules",
                changes=[
                    ProjectChange(
                        path="/mechanics",
                        operation="replace",
                        reason="the brief says what this is",
                        value_rows=["el minero cava hacia abajo", "un murciélago le quita una vida"],
                    )
                ],
                risks=[],
            )

    updated = draft(service, project, directory, Drafter())

    assert updated.mechanics[0] == "el minero cava hacia abajo"
    assert service.open_project(directory).mechanics == updated.mechanics


def test_drafting_a_design_that_already_states_its_rules_changes_nothing(tmp_path):
    """`needs_drafting` is asked before the drafter is built, so a project that
    does not want drafting costs nothing -- the same rule `pipeline.research`
    follows when it puts its question before the OpenAI client."""
    from llmz80.studio.models import TargetPlatform
    from llmz80.studio.pipeline import draft
    from llmz80.studio.services import StudioService

    service = StudioService.at(tmp_path)
    project, directory = service.create_project("Stated", TargetPlatform.SPECTRUM)
    project = project.model_copy(update={"mechanics": ["ya lo dice"]})
    service.save_project(project, directory)

    class NeverCalled:
        def draft(self, project, dossier=None, feedback=None):
            raise AssertionError("the drafter must not be asked")

    assert draft(service, project, directory, NeverCalled()).mechanics == ["ya lo dice"]
```

- [ ] **Step 2:** run, expect `ImportError: cannot import name 'draft'`.

- [ ] **Step 3: Implement `pipeline.draft`**

Firma paralela a `adapt`: `draft(service, project, directory, drafter=None, dossier=None, *, say=_quiet, confirm=None)`.

- Pregunta `needs_drafting` **antes** de construir nada. Si es `False`, devuelve el proyecto intacto y dice por qué a través de `say` — que un diseño no quiera redacción es un resultado ordinario, no un fallo.
- Lee la ficha con `load_reference(directory)` cuando no se la dan, igual que `sprites` y `adapt`.
- Construye `ResponsesDesignDrafter` sólo si hace falta, dentro de la etapa, por la razón que da `make.py`: una clave ausente debe detener la etapa que la necesitaba con lo anterior ya en disco.
- `confirm` recibe el diff y decide si se aplica, como en `adapt`.
- Guarda con `service.save_project`.

Y el `ResponsesDesignDrafter` en `drafting.py`, copiando la forma de `ResponsesReferenceDesigner`.

- [ ] **Step 4:** `.venv/bin/python -m pytest tests/test_studio_pipeline.py -v` → PASS.

- [ ] **Step 5: Commit**

```bash
git commit -m "feat(studio): give the pipeline the stage that decides what a game is"
```

---

## Task 4: El callejón deja de serlo

**Files:**
- Modify: `llmz80/studio/make.py`
- Test: `tests/test_studio_make.py`

Hoy `make` corre cuatro etapas de pago — `referencia`, `diseño`, `sprites`, `programa` (`make.py:61`) — y cuando la investigación no identifica nada salta `diseño` y avisa de que `programa` va a rechazar el diseño mudo. Con la redacción esa advertencia deja de hacer falta: la etapa nueva llena `mechanics` haya ficha o no.

- [ ] **Step 1: Write the failing test**

```python
def test_the_order_drafts_before_it_adapts():
    """Drafting decides what the game is; adapting decides what it looks like.
    A dossier can only dress a design that already states something."""
    from llmz80.studio.make import PAID_STAGES

    assert PAID_STAGES.index("redacción") < PAID_STAGES.index("diseño")
    assert PAID_STAGES.index("referencia") < PAID_STAGES.index("redacción")


def test_an_unidentified_game_no_longer_dead_ends_the_order(tmp_path):
    """Research finding nothing used to mean `diseño` was skipped, `mechanics`
    stayed empty and `programa` refused three stages later, pointing at a
    command that refused identically. Drafting runs from the brief alone."""
```

Escribir el cuerpo del segundo contra la maquinaria de etapas que `tests/test_studio_make.py` ya usa para dirigir un orden sin gastar nada — leerlo primero y seguir esa forma; no inventar un segundo arnés.

- [ ] **Step 2:** run, expect FAIL (`redacción` no está en `PAID_STAGES`).

- [ ] **Step 3: Implement**

- `PAID_STAGES = ("referencia", "redacción", "diseño", "sprites", "programa")` y la entrada correspondiente en el mapa de nombres a funciones de `pipeline`.
- La etapa `redacción` corre siempre; salta sola cuando `needs_drafting` es `False`, y esa abstención se dice como un `SKIP` con su razón, no como un fallo.
- Retirar la advertencia que añadió el plan anterior (`make.py:402-420`) **sólo si la redacción la deja sin objeto**. Si sigue habiendo un camino por el que se llega a `programa` con `mechanics` vacío — por ejemplo un redactor que se niega — la advertencia sigue haciendo falta y hay que reescribirla para nombrar ese camino. Comprobarlo, no suponerlo.
- Renumerar las etapas en el diario. `_Diary` las numera para que «se detuvo en 4 programa» signifique lo mismo en el log, en pantalla y en el informe (`make.py:114-116`); con cinco etapas `programa` pasa a ser la 5.

- [ ] **Step 4:** `.venv/bin/python -m pytest tests/test_studio_make.py -v` → PASS.

- [ ] **Step 5: Commit**

```bash
git commit -m "feat(studio): let the order draft its way past a game nobody recognised"
```

---

## Task 5: `llmz80 project draft`

**Files:** modify `llmz80/cli.py`; test `tests/test_studio_cli.py`.

Una etapa del pipeline que sólo se puede correr desde `make` no se puede reparar a mano, que es justo lo que hacía falta cuando `programa` rechazaba. Seguir exactamente la forma de `llmz80 project adapt`: mismo manejo de `ValueError` → `ERROR: …` → salida 1, misma confirmación del diff cuando hay alguien al teclado, mismo `--yes` si `adapt` lo tiene.

Test: que un diseño ya redactado sale por la vía de «no hace falta» sin construir cliente, y que un `DraftRefused` se reporta como error y no como traza.

- [ ] **Commit**: `feat(cli): let somebody run the drafting stage on its own`

---

## Task 6: Un juego de punta a punta

Esto es lo que decide si el plan sirvió. Todo lo anterior se puede verificar con dobles; esto no.

- [ ] **Step 1:** `.venv/bin/python -m llmz80.cli make "un minero que cava túneles y esquiva murciélagos" --platform spectrum`

- [ ] **Step 2:** Registrar, sin adornos, qué pasó en cada etapa: si `referencia` identificó algo, qué escribió `redacción` en `mechanics` y `entities`, si `diseño` corrió y qué cambió, y si `programa` pasó las puertas.

- [ ] **Step 3:** Leer el `game.yml` resultante y decir si un lector humano diría que describe el juego del brief. **Esto es un juicio, no una aserción**, y hay que marcarlo como tal.

- [ ] **Step 4:** Leer `emulator_report.json` y registrar el nivel de verificación y el veredicto de cada puerta.

- [ ] **Step 5:** Si alguna etapa falla, **no arreglarla a la carrera**: informar de dónde y por qué. Un primer extremo a extremo que falla honestamente vale más que uno que pasa porque alguien tocó algo hasta que pasó.

---

## Riesgos

1. **El redactor inventa un juego distinto del que pide el brief.** Es el riesgo que el prompt de `adapt` evita no redactando nunca, y esta etapa lo asume a propósito. Lo que lo acota: el examinador de la tarea 8 del plan anterior (`design_exam.py`) ya compara diseño contra brief y ya está enchufado al bucle de `adapt` — engancharlo también aquí es la defensa natural, y si el bucle acaba siendo compartido (ver tarea 2) sale gratis.
2. **Coste.** Una llamada más por juego, y hasta tres con reparaciones. `adapt` ya cuesta hasta seis desde el plan anterior.
3. **`/entities/-` es la primera ruta que *añade* algo.** El diseñador sólo editaba campos de entidades que ya existían. `apply_proposal` es transaccional y revalida el documento entero, así que el riesgo no es corromper nada — es que `structure.py` rechace combinaciones que el redactor produzca a menudo (una entidad que nombra un sprite que no existe, por ejemplo). Si eso pasa repetidamente, el arreglo es el prompt, no relajar `structure.py`.
