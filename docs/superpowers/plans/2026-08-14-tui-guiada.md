# TUI guiada: wizard y diario — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Que Studio conduzca al usuario paso a paso, con una sola tecla por paso, y cuente por escrito qué hace, cuándo empieza, cuándo acaba y cuánto tarda.

**Architecture:** Dos módulos puros nuevos —`wizard.py`, que dice en qué paso estás sobre lo que `screen.stage_line` ya calcula, y `journal.py`, que escribe cada línea en `<proyecto>/studio.log` y devuelve la misma cadena que escribió— y `tui.py` degradado a renderizador: pierde sus diez atajos `ctrl` y gana un despachador único sobre el paso actual. Los tres trabajos largos de `services.py` ganan un `on_progress` opcional, sin el cual no se puede contar nada mientras ocurren.

**Tech Stack:** Python 3.12, Textual 8.2, pydantic v2, pytest.

**Spec:** `docs/superpowers/specs/2026-08-14-tui-guiada-design.md`.

---

## Antes de empezar

1. **Tests con `.venv/bin/python -m pytest`, nunca con `python3`** — el intérprete del sistema no tiene `pytest-asyncio` e inventa 26 fallos en `tests/test_studio_tui.py`. Baseline verde en `main`: **591 passed**.
2. **Rama:** `git checkout -b tui-wizard`.
3. Commits en inglés, Conventional Commits, con los dos trailers (`Co-Authored-By:` y `Claude-Session:`) como el resto del repositorio.
4. `black` sobre lo que toques antes de commitear.
5. A diferencia del corte de esquema anterior, **aquí no hay ventana roja**: cada tarea deja la suite entera verde. Si una tarea la deja roja, es un defecto de esa tarea.

## Estructura de ficheros

**Se crean:**

| Fichero | Responsabilidad |
| --- | --- |
| `llmz80/studio/journal.py` | Formatear una línea fechada, añadirla a `studio.log`, devolverla |
| `llmz80/studio/wizard.py` | Qué paso es el actual, qué le falta, qué hace Enter |
| `tests/test_studio_journal.py` | El diario como datos |
| `tests/test_studio_wizard.py` | La máquina de estados como datos |

**Se modifican:** `llmz80/studio/services.py` (tres firmas), `llmz80/studio/tui.py` (teclas, render, despacho), `llmz80/studio/screen.py` (retirar `STAGE_KEY`), `tests/test_studio_tui.py`, `tests/test_screen.py`, `tests/test_studio_services.py`, `README.md`.

---

### Task 1: `journal.py` — el diario

**Files:**
- Create: `llmz80/studio/journal.py`
- Create: `tests/test_studio_journal.py`

- [ ] **Step 1: Escribe el test que falla**

```python
"""The diary writes what it returns, so screen and file cannot diverge."""

from datetime import datetime

import pytest

from llmz80.studio.journal import FILENAME, Journal


class _Clock:
    """A clock a test can wind forward, so durations are asserted, not timed."""

    def __init__(self) -> None:
        self.now = datetime(2026, 8, 14, 9, 14, 2)

    def __call__(self) -> datetime:
        return self.now

    def advance(self, seconds: int) -> None:
        from datetime import timedelta

        self.now += timedelta(seconds=seconds)


@pytest.fixture()
def journal(tmp_path) -> Journal:
    return Journal(tmp_path / FILENAME, clock=_Clock())


def test_a_line_carries_its_stamp_and_kind(journal):
    line = journal.write("ABRIR", "proyecto fase-uno (spectrum, v4)")
    assert line.startswith("2026-08-14 09:14:02  ABRIR")
    assert line.endswith("proyecto fase-uno (spectrum, v4)")


def test_what_it_returns_is_what_it_wrote(journal):
    line = journal.write("AVISO", "el diseño no declara mecánicas")
    assert journal.path.read_text(encoding="utf-8").splitlines() == [line]


def test_lines_accumulate_across_sessions(journal):
    first = journal.write("ABRIR", "proyecto uno")
    second = Journal(journal.path, clock=journal.clock).write("ABRIR", "proyecto uno otra vez")
    assert journal.path.read_text(encoding="utf-8").splitlines() == [first, second]


def test_a_start_hands_back_the_line_it_wrote(journal):
    token = journal.start("3 sprites — 2 entidades sin arte (API)")
    assert token.line == journal.path.read_text(encoding="utf-8").splitlines()[-1]


def test_finish_prices_the_work_from_its_own_start(journal):
    token = journal.start("3 sprites — 2 entidades sin arte (API)")
    journal.clock.advance(84)
    line = journal.finish(token, ok=True, text="2 hojas, 1024 B")
    assert "FIN" in line
    assert "en 84 s" in line
    assert "2 hojas, 1024 B" in line


def test_a_failed_finish_says_so(journal):
    token = journal.start("4 programa")
    journal.clock.advance(3)
    assert "FALLÓ" in journal.finish(token, ok=False, text="sin diagnóstico")


def test_notes_are_the_running_commentary(journal):
    assert journal.note("hero: 4 poses empaquetadas, 512 B").startswith(
        "2026-08-14 09:14:02  ..      "
    )


def test_the_diary_creates_its_directory(tmp_path):
    path = tmp_path / "nuevo" / FILENAME
    Journal(path).write("ABRIR", "proyecto nuevo")
    assert path.is_file()
```

- [ ] **Step 2: Corre el test y comprueba que falla**

Run: `.venv/bin/python -m pytest tests/test_studio_journal.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'llmz80.studio.journal'`

- [ ] **Step 3: Escribe `llmz80/studio/journal.py`**

```python
"""The project's diary: what Studio did, when, and how long it took.

Every line is written to `<project>/studio.log` *and returned*, so whatever
draws it on screen shows the same string the file keeps. Composing the screen
version separately is how the two start telling different stories about the
same event.

The diary is append-only and survives the session: a pipeline step can take
minutes and spend money, and "what happened last night" is a question worth
being able to answer the next morning.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable, Literal

#: The kinds of line a diary carries. Few and fixed-width on purpose: a reader
#: scanning the left margin sees the shape of a session -- what started, what
#: it said along the way, what it ended as -- before reading any of it.
Kind = Literal[
    "ABRIR", "ETAPA", "INICIO", "..", "FIN", "AVISO", "ERROR", "GUARDAR", "OMITIR"
]

FILENAME = "studio.log"

_STAMP = "%Y-%m-%d %H:%M:%S"


@dataclass(frozen=True)
class Token:
    """What `start` hands back: enough to price the work when it finishes, and
    the line it already wrote, so the caller can put that same line on screen
    without composing a second version of it."""

    text: str
    began: datetime
    line: str


@dataclass
class Journal:
    path: Path
    #: Injected so a test can wind time forward and assert a duration instead
    #: of timing one. The default is the local clock rather than UTC: this file
    #: is read by the person sitting at the machine, and local time is what
    #: matches their memory of what they were doing.
    clock: Callable[[], datetime] = field(default=datetime.now)

    @classmethod
    def for_project(cls, directory: Path) -> "Journal":
        return cls(directory / FILENAME)

    def write(self, kind: Kind, text: str) -> str:
        line = f"{self.clock().strftime(_STAMP)}  {kind:<8}{text}"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as diary:
            diary.write(line + "\n")
        return line

    def start(self, text: str) -> Token:
        """Open a piece of work. The token remembers when, so `finish` can say."""
        began = self.clock()
        return Token(text=text, began=began, line=self.write("INICIO", text))

    def note(self, text: str) -> str:
        """One line of running commentary from inside a piece of work."""
        return self.write("..", text)

    def finish(self, token: Token, *, ok: bool, text: str = "") -> str:
        seconds = int((self.clock() - token.began).total_seconds())
        verdict = "ok" if ok else "FALLÓ"
        tail = f" {text}" if text else ""
        return self.write("FIN", f"{token.text} — {verdict} en {seconds} s.{tail}")
```

- [ ] **Step 4: Corre el test**

Run: `.venv/bin/python -m pytest tests/test_studio_journal.py -q`
Expected: PASS, los ocho.

- [ ] **Step 5: Commit**

```bash
.venv/bin/python -m black llmz80/studio/journal.py tests/test_studio_journal.py
git add llmz80/studio/journal.py tests/test_studio_journal.py
git commit -m "feat(studio): give a project a diary that outlives the session"
```

---

### Task 2: `wizard.py` — qué paso toca

> **Corregida durante la ejecución. El código de abajo tiene un fallo de diseño.**
> `current` estaba escrita como "el primer paso que no está hecho", y `screen._design_stage` nunca devuelve `pending` — un diseño está `done` o `failed`. Con esa regla el wizard salta el paso 2 en cuanto el diseño valida, y el paso que existe para editar sería el único al que nunca se llega. La regla correcta es **el primer paso por el que la persona no ha pasado**, con `passed` en lugar de `skipped`, y una tecla `→` para dejar atrás un paso — que estaba en el mockup aprobado y se perdió al escribir el plan. Ver el spec y `git show` de la tarea 2.

**Files:**
- Create: `llmz80/studio/wizard.py`
- Create: `tests/test_studio_wizard.py`

- [ ] **Step 1: Escribe el test que falla**

```python
"""The wizard walks the pipeline in order and never guesses what is done."""

from llmz80.studio.models import GameProject, TargetPlatform
from llmz80.studio.samples import blank_project
from llmz80.studio.wizard import current, steps


def test_without_a_project_the_first_step_is_choosing_one():
    step = current(None, None)
    assert step.number == 0
    assert step.name == "proyecto"


def test_with_a_project_step_zero_is_done_and_the_walk_begins():
    project = blank_project("Walk", TargetPlatform.SPECTRUM)
    walked = steps(project, None)
    assert walked[0].number == 0
    assert walked[0].state == "done"
    assert [step.name for step in walked[1:]] == [
        "referencia", "diseño", "sprites", "programa", "gates", "release",
    ]


def test_a_fresh_project_is_pointed_at_research(tmp_path):
    project = blank_project("Fresh", TargetPlatform.SPECTRUM)
    assert current(project, tmp_path).name == "referencia"


def test_skipping_a_step_moves_past_it(tmp_path):
    project = blank_project("Skip", TargetPlatform.SPECTRUM)
    assert current(project, tmp_path, skipped={"referencia"}).name == "diseño"


def test_only_research_and_sprites_may_be_skipped(tmp_path):
    project = blank_project("Optional", TargetPlatform.SPECTRUM)
    skippable = {step.name for step in steps(project, tmp_path) if step.skippable}
    assert skippable == {"referencia", "sprites"}


def test_only_the_design_step_is_editable(tmp_path):
    project = blank_project("Editable", TargetPlatform.SPECTRUM)
    editable = {step.name for step in steps(project, tmp_path) if step.editable}
    assert editable == {"diseño"}


def test_the_steps_that_spend_money_say_so(tmp_path):
    project = blank_project("Money", TargetPlatform.SPECTRUM)
    paid = {step.name for step in steps(project, tmp_path) if step.costs_api}
    assert paid == {"referencia", "sprites", "programa"}


def test_a_failure_wins_over_a_later_pending_step(tmp_path):
    """Nothing is gained by pointing at "draw sprites" while the design is broken."""
    project = blank_project("Broken", TargetPlatform.SPECTRUM)
    broken = project.model_copy(update={"presentation": project.presentation.model_copy(
        update={"hud_rows": 4}
    )})
    step = current(broken, tmp_path, skipped={"referencia"})
    assert step.name == "diseño"
    assert step.state == "failed"
    assert step.detail


def test_every_step_carries_words_a_person_can_read(tmp_path):
    project = blank_project("Words", TargetPlatform.SPECTRUM)
    for step in steps(project, tmp_path):
        assert step.summary
        assert step.action_label
```

- [ ] **Step 2: Corre el test y comprueba que falla**

Run: `.venv/bin/python -m pytest tests/test_studio_wizard.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'llmz80.studio.wizard'`

Nota sobre `test_a_failure_wins_over_a_later_pending_step`: usa `model_copy` porque un `hud_rows` que no deja sitio a la pantalla se rechaza al construir el documento; `model_copy` es la única forma de tener en memoria un proyecto que `screen._design_stage` marcará como `failed`. Es el mismo recurso que `tests/test_screen.py` ya documenta.

- [ ] **Step 3: Escribe `llmz80/studio/wizard.py`**

```python
"""Which step the person is on, and what pressing Enter would do.

A pure state machine over `screen.stage_line`. That module already decides
what has been done, from the design in memory and the evidence the pipeline
left on disk; this one adds the three things it does not have: the order, the
words to put on screen, and the rule for what comes next. It deliberately does
not re-derive any of the "is this done" logic -- two answers to that question
would drift apart within a week.

Nothing here draws, calls an API or touches disk, which is what lets the whole
flow be tested without starting Textual, exactly as `render_map` and
`stage_line` already are.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Iterable, Literal

from .models import GameProject
from .screen import stage_line

#: `screen.StageState` plus the one state a stage cannot know about itself:
#: that the person decided to go past it.
StepState = Literal["done", "pending", "failed", "skipped"]


@dataclass(frozen=True)
class Step:
    number: int
    name: str
    summary: str
    action_label: str
    costs_api: bool
    state: StepState
    detail: str = ""
    editable: bool = False
    skippable: bool = False


#: name, summary, action label, costs API, editable, skippable.
#:
#: `referencia` and `sprites` are skippable because they are optional in the
#: pipeline itself, not as a convenience: a game need not be based on a real
#: one, and a game without sprite art is drawn with characters. Demanding
#: "done" from them would invent a requirement the pipeline does not have.
_PIPELINE: tuple[tuple[str, str, str, bool, bool, bool], ...] = (
    (
        "referencia",
        "Buscar el juego real en la web y archivar su ficha citada",
        "investigar",
        True,
        False,
        True,
    ),
    ("diseño", "Revisar y ajustar el diseño", "editar", False, True, False),
    ("sprites", "Dibujar el arte que le falte a alguna entidad", "dibujar", True, False, True),
    (
        "programa",
        "Escribir el juego en C y repararlo contra el compilador",
        "escribir",
        True,
        False,
        False,
    ),
    (
        "gates",
        "Compilar, ejecutar en el emulador y pasar las puertas",
        "probar",
        False,
        False,
        False,
    ),
    ("release", "Empaquetar el zip con su evidencia", "publicar", False, False, False),
)

#: Step zero is the wizard's own: `stage_line` knows the six pipeline stages
#: and nothing about whether a project is open, because "I have a project
#: open" is not evidence anybody leaves on disk. It is the one step whose
#: state this module decides rather than reads.
_PROJECT_STEP = Step(
    number=0,
    name="proyecto",
    summary="Elegir un proyecto del workspace, o crear uno nuevo",
    action_label="abrir",
    costs_api=False,
    state="pending",
)


def steps(
    project: GameProject | None,
    directory: Path | None,
    skipped: Iterable[str] = (),
) -> list[Step]:
    """The seven steps, in order, with the state each one is in right now."""
    passed_over = set(skipped)
    stages = {stage.name: stage for stage in stage_line(project, directory)}
    walked = [replace(_PROJECT_STEP, state="done" if project is not None else "pending")]
    for number, (name, summary, label, costs, editable, skippable) in enumerate(
        _PIPELINE, start=1
    ):
        stage = stages.get(name)
        state: StepState = "pending"
        if name in passed_over:
            state = "skipped"
        elif stage is not None:
            state = stage.state
        walked.append(
            Step(
                number=number,
                name=name,
                summary=summary,
                action_label=label,
                costs_api=costs,
                state=state,
                detail=stage.detail if stage is not None else "",
                editable=editable,
                skippable=skippable,
            )
        )
    return walked


def current(
    project: GameProject | None,
    directory: Path | None,
    skipped: Iterable[str] = (),
) -> Step:
    """The step the wizard is on: the first neither done nor skipped.

    A failure wins over a later pending step -- the same rule
    `screen.next_step` applies, for the same reason: there is nothing to gain
    from pointing at "draw the sprites" while the design itself is broken.

    Once every step is done the last one is returned rather than `None`: the
    wizard always has something to show, and "release, done" is the truthful
    thing to be showing at that point.
    """
    walked = steps(project, directory, skipped)
    failed = next((step for step in walked if step.state == "failed"), None)
    if failed is not None:
        return failed
    pending = next((step for step in walked if step.state == "pending"), None)
    return pending if pending is not None else walked[-1]
```

- [ ] **Step 4: Corre el test**

Run: `.venv/bin/python -m pytest tests/test_studio_wizard.py -q`
Expected: PASS, los nueve.

- [ ] **Step 5: Commit**

```bash
.venv/bin/python -m black llmz80/studio/wizard.py tests/test_studio_wizard.py
git add llmz80/studio/wizard.py tests/test_studio_wizard.py
git commit -m "feat(studio): name the step the pipeline is on"
```

---

### Task 3: `services.py` — contar lo que pasa mientras pasa

**Files:**
- Modify: `llmz80/studio/services.py:108` (`draw_sprites`), `:399` (`runtime_test`), `:460` (`write_program`)
- Modify: `tests/test_studio_services.py`

- [ ] **Step 1: Escribe el test que falla**

Añade al final de `tests/test_studio_services.py`:

```python
def test_draw_sprites_narrates_each_sheet_it_packs(tmp_path, monkeypatch):
    """Without this the screen can say nothing for the eighty seconds the
    artist takes, because the report only exists once it is over."""
    from llmz80.studio.samples import blank_project
    from llmz80.studio.services import StudioService

    service = StudioService.at(tmp_path)
    project, directory = service.create_project("Narrated", TargetPlatform.SPECTRUM)
    said: list[str] = []
    service.draw_sprites(project, directory, _StubArtist(), on_progress=said.append)
    assert any("actor" in line for line in said), said


def test_on_progress_is_optional(tmp_path):
    """Every existing caller passes nothing and must keep working."""
    from llmz80.studio.services import StudioService

    service = StudioService.at(tmp_path)
    project, directory = service.create_project("Quiet", TargetPlatform.SPECTRUM)
    service.draw_sprites(project, directory, _StubArtist())
```

`_StubArtist` ya existe en ese fichero para los tests de `draw_sprites`; reutilízalo. Si su nombre difiere, usa el que haya — `grep -n "class _Stub" tests/test_studio_services.py`.

- [ ] **Step 2: Corre el test y comprueba que falla**

Run: `.venv/bin/python -m pytest tests/test_studio_services.py -k narrates -q`
Expected: FAIL — `TypeError: draw_sprites() got an unexpected keyword argument 'on_progress'`

- [ ] **Step 3: Añade el parámetro a los tres trabajos largos**

En `llmz80/studio/services.py`, sobre la clase, define el alias y su razón:

```python
#: Told what is happening while it happens. The three long jobs below take
#: minutes and two of them spend money, and their reports only exist once they
#: are over -- so without this there is nothing to say during the wait, and a
#: screen that says nothing for eighty seconds reads as one that hung.
Progress = Callable[[str], None] | None


def _say(on_progress: Progress, text: str) -> None:
    """Report `text` if anyone is listening. Callers stay free of the check."""
    if on_progress is not None:
        on_progress(text)
```

Importa `Callable` de `typing` si no está ya.

Luego, en cada método:

- `draw_sprites(self, project, directory, artist, dossier=None, *, on_progress=None)` — llama `_say` justo después de registrar cada hoja, con el id de la entidad, el número de fotogramas y los bytes empaquetados; y una vez por reintento del artista, diciendo qué se le reprochó.
- `write_program(self, project, directory, writer, *, on_progress=None)` — una llamada por intento, con el número, si el build pasó y el veredicto de las puertas.
- `runtime_test(self, project, directory, *, seconds=3, on_progress=None)` — una al empezar el build y otra al empezar la ejecución en el emulador, que son las dos esperas largas.

En los tres, el parámetro es **de palabra clave y opcional**, y su ausencia no cambia nada.

- [ ] **Step 4: Corre los tests**

Run: `.venv/bin/python -m pytest tests/test_studio_services.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
.venv/bin/python -m black llmz80/studio/services.py tests/test_studio_services.py
git add llmz80/studio/services.py tests/test_studio_services.py
git commit -m "feat(studio): let the long jobs say what they are doing"
```

---

### Task 4: `tui.py` — el wizard sustituye a los atajos

Es la tarea grande y la que fija la decisión del spec.

**Files:**
- Modify: `llmz80/studio/tui.py:231-242` (BINDINGS), `:289-330` (compose), `:654` (on_key), `:716-1070` (las diez acciones)
- Modify: `tests/test_studio_tui.py`

- [ ] **Step 1: Escribe el test que falla**

Añade a `tests/test_studio_tui.py`:

```python
def test_none_of_the_ten_shortcuts_survive():
    """The decision this whole change exists to make, written as a test."""
    from llmz80.studio.tui import StudioApp

    bound = {binding[0] for binding in StudioApp.BINDINGS}
    for gone in ("ctrl+n", "ctrl+o", "ctrl+s", "ctrl+f", "ctrl+a",
                 "ctrl+d", "ctrl+w", "ctrl+b", "ctrl+t", "ctrl+r"):
        assert gone not in bound, f"{gone} survives"


@pytest.mark.asyncio
async def test_enter_runs_the_current_step(tmp_path):
    from llmz80.studio.tui import StudioApp

    app = StudioApp(tmp_path)
    async with app.run_test() as pilot:
        app.project, app.project_dir = app.service.create_project(
            "Wizard", TargetPlatform.SPECTRUM
        )
        app.skipped = {"referencia"}
        app._refresh_wizard()
        await pilot.press("enter")
        await pilot.pause()
        assert app.active_panel == "map"          # el paso 2 abre el editor


@pytest.mark.asyncio
async def test_skipping_writes_it_down(tmp_path):
    from llmz80.studio.tui import StudioApp

    app = StudioApp(tmp_path)
    async with app.run_test() as pilot:
        app.project, app.project_dir = app.service.create_project(
            "Skipped", TargetPlatform.SPECTRUM
        )
        app._refresh_wizard()
        await pilot.press("s")
        await pilot.pause()
        assert "referencia" in app.skipped
        diary = (app.project_dir / "studio.log").read_text(encoding="utf-8")
        assert "OMITIR" in diary


@pytest.mark.asyncio
async def test_a_step_that_cannot_be_skipped_says_so(tmp_path):
    from llmz80.studio.tui import StudioApp

    app = StudioApp(tmp_path)
    async with app.run_test() as pilot:
        app.project, app.project_dir = app.service.create_project(
            "Required", TargetPlatform.SPECTRUM
        )
        app.skipped = {"referencia"}
        app._refresh_wizard()
        await pilot.press("s")
        await pilot.pause()
        assert "diseño" not in app.skipped
```

- [ ] **Step 2: Corre el test y comprueba que falla**

Run: `.venv/bin/python -m pytest tests/test_studio_tui.py -k "survive or current_step" -q`
Expected: FAIL — las diez teclas siguen atadas y `_refresh_wizard` no existe.

- [ ] **Step 3: Sustituye `BINDINGS`**

```python
    BINDINGS = [
        ("enter", "do", "Hacer"),
        ("right", "advance", "Siguiente paso"),
        ("escape", "back", "Volver"),
        ("r", "repeat", "Repetir"),
        ("q", "quit", "Salir"),
    ]
```

- [ ] **Step 4: Añade el estado y el despachador del wizard**

En `__init__`, junto a los demás campos:

```python
        #: Steps the person has already left behind -- done, moved past, or
        #: skipped. Session state on purpose: the diary records the decision,
        #: but having walked past a step is not evidence of work done, and must
        #: not be read back as if it were.
        self.passed: set[str] = set()
        self.journal: Journal | None = None
```

Y el despachador, que es la única entrada a las acciones del pipeline:

```python
    def action_do(self) -> None:
        """Do whatever the current step is for. Advancing is `action_advance`."""
        step = wizard.current(self.project, self.project_dir, self.passed)
        self._actions()[step.name]()

    def action_advance(self) -> None:
        """Leave the current step behind.

        On a step already resolved this is simply moving on. On a pending one it
        is skipping, and then it only works if the step is skippable: the
        pipeline does not need `referencia` or `sprites`, but without `programa`
        or `gates` there is nothing to release. Skipping is written down;
        walking past a finished step is not, because no decision was made.
        """
        step = wizard.current(self.project, self.project_dir, self.passed)
        if step.state == "pending" and not step.skippable:
            self.notify(f"El paso {step.name} no se puede omitir", severity="warning")
            return
        if step.state == "pending":
            self._log(self.journal.write("OMITIR", f"{step.number} {step.name}"))
        self.passed.add(step.name)
        self._refresh_wizard()

    def _actions(self) -> dict[str, Callable[[], None]]:
        """One entry per step, holding the methods that used to be reachable by
        a ctrl-binding. The wizard decides which one runs; no key names any of
        them any more."""
        return {
            "proyecto": self._open_project_step,
            "referencia": self._research,
            "diseño": self._edit_design,
            "sprites": self._draw_sprites,
            "programa": self._write,
            "gates": self._test,
            "release": self._release,
        }
```

Renombra `_refresh_stage` a `_refresh_wizard`, y que redibuje tres cosas: la cabecera
(`Paso N de 6: <nombre>`), la tira de etapas con su marca por estado, y el resumen del paso
actual con su aviso de coste si `costs_api`. El diario se pinta en el panel `log`, que pasa
a estar siempre visible en vez de ser uno más de los que se abren con una tecla.

Añade `action_repeat`, que es lo que hace falta para que `Esc` a un paso ya hecho sirva de
algo — sin él sólo se puede mirar:

```python
    def action_repeat(self) -> None:
        """Do a finished step again, after asking.

        `Enter` on a done step advances, so without this there is no way to
        redo one: stepping back with `Esc` would leave the person looking at a
        finished step unable to touch it. The confirmation is the one
        `research_reference` and `draw_sprites` already ask before overwriting.
        """
        step = wizard.current(self.project, self.project_dir, self.passed)
        if step.state != "done":
            self.notify("Ese paso no está hecho todavía", severity="warning")
            return
        if not self._confirmed(f"repeat:{step.name}"):
            self.notify(f"Pulsa R otra vez para rehacer {step.name}", severity="warning")
            return
        self._actions()[step.name]()
```

Y en `_background`, cuando el trabajo lanza una excepción o devuelve un fallo, escribe
`ERROR` en el diario con la razón y **no avances**: el wizard se queda en ese paso porque
`wizard.current` lo seguirá viendo `pending` o `failed`. Que las puertas rechacen el
programa es un resultado del paso, no una excepción, y se registra igual.

Renombra las acciones existentes quitándoles el prefijo `action_` (`action_research` → `_research`, y así con `_draw_sprites`, `_write`, `_test`, `_release`). `action_build` desaparece: el paso `gates` construye antes de ejecutar, así que compilar por separado no era un paso del pipeline sino un atajo.

- [ ] **Step 5: Ata el diario al ciclo**

En `_run`, sustituye el `self._log(f"[yellow]{label}...[/yellow]")` por una apertura de diario, y pasa `on_progress` al trabajo:

```python
        token = self.journal.start(f"{step.number} {step.name} — {label}")
        self._log(token.line)
```

y en `_background`, al terminar, `self.journal.finish(token, ok=..., text=...)`, registrando también su línea en pantalla. Cada línea que el diario devuelve se pinta con `self._log`: **nunca compongas por tu cuenta la versión de pantalla**, que es justo lo que el diario existe para evitar.

- [ ] **Step 6: Corre los tests**

Run: `.venv/bin/python -m pytest tests/test_studio_tui.py -q`
Expected: PASS. Los tests existentes que pulsaban `ctrl+f`, `ctrl+d`, `ctrl+w` etc. hay que portarlos a `enter` sobre el paso correspondiente — pórtalos, no los borres: lo que probaban (que la acción llega al servicio, que pregunta antes de sobrescribir, que un fallo notifica en vez de reventar) sigue valiendo.

- [ ] **Step 7: Commit**

```bash
.venv/bin/python -m black llmz80/studio/tui.py tests/test_studio_tui.py
git add llmz80/studio/tui.py tests/test_studio_tui.py
git commit -m "feat(studio): drive the pipeline with one key instead of ten"
```

---

### Task 5: El paso 0 y el editor

**Files:**
- Modify: `llmz80/studio/tui.py` (`_open_project_step`, `_edit_design`, `action_back`)
- Modify: `tests/test_studio_tui.py`

- [ ] **Step 1: Escribe el test que falla**

```python
@pytest.mark.asyncio
async def test_without_a_project_the_wizard_offers_the_chooser(tmp_path):
    from llmz80.studio.tui import StudioApp

    app = StudioApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.press("enter")
        await pilot.pause()
        assert app.active_panel == "open"


@pytest.mark.asyncio
async def test_leaving_the_editor_saves_and_says_so(tmp_path):
    from llmz80.studio.tui import StudioApp

    app = StudioApp(tmp_path)
    async with app.run_test() as pilot:
        app.project, app.project_dir = app.service.create_project(
            "Saved", TargetPlatform.SPECTRUM
        )
        app.skipped = {"referencia"}
        app._refresh_wizard()
        await pilot.press("enter")          # entra al editor
        await pilot.press("space")          # pinta una celda
        await pilot.press("escape")         # sale, y al salir guarda
        await pilot.pause()
        assert app.active_panel is None
        diary = (app.project_dir / "studio.log").read_text(encoding="utf-8")
        assert "GUARDAR" in diary
```

- [ ] **Step 2: Corre el test y comprueba que falla**

Run: `.venv/bin/python -m pytest tests/test_studio_tui.py -k "chooser or saves_and_says" -q`
Expected: FAIL

- [ ] **Step 3: Implementa el paso 0 y la salida del editor**

`_open_project_step` abre el panel `open` que ya existe (el que hoy abre `ctrl+o`), con la lista del workspace y una entrada para crear. `_edit_design` abre el panel `map`. `action_back`:

```python
    def action_back(self) -> None:
        """Leave the editor, saving; or step back to look at an earlier step."""
        if self.active_panel is not None:
            if self.project is not None and self.project_dir is not None:
                self.service.save_project(self.project, self.project_dir)
                self._log(self.journal.write("GUARDAR", f"{self.project.metadata.slug}/game.yml"))
            self._set_panel(None)
            self._refresh_wizard()
            return
        self._step_back()
```

- [ ] **Step 4: Guarda también al avanzar de paso**

En `_advance_past`, antes de mover el cursor, guarda si hay proyecto y registra la línea:
es la otra mitad de la decisión "no hay estado sin guardar que perder". Guardar dos veces
seguidas no escribe una revisión de más — `store.save` sólo archiva la anterior cuando el
texto cambió.

- [ ] **Step 5: Corre los tests**

Run: `.venv/bin/python -m pytest tests/test_studio_tui.py -q`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add llmz80/studio/tui.py tests/test_studio_tui.py
git commit -m "feat(studio): make choosing a project the first step, and save on leaving the editor"
```

---

### Task 6: Retirar `STAGE_KEY`

**Files:**
- Modify: `llmz80/studio/screen.py:52-76`
- Modify: `tests/test_screen.py`

- [ ] **Step 1: Escribe el test que falla**

```python
def test_the_stage_line_no_longer_names_keys():
    """The keys it named are gone; the wizard decides what Enter does."""
    import llmz80.studio.screen as screen

    assert not hasattr(screen, "STAGE_KEY")
```

- [ ] **Step 2: Corre el test y comprueba que falla**

Run: `.venv/bin/python -m pytest tests/test_screen.py -k no_longer_names_keys -q`
Expected: FAIL

- [ ] **Step 3: Borra `STAGE_KEY` y su comentario**

Y con él, `next_step_hint` y cualquier otro sitio que compusiera "pulsa X para...". Búscalos: `grep -rn 'STAGE_KEY\|next_step_hint' llmz80/ tests/`. `next_step` **se queda**: el wizard lo necesita.

- [ ] **Step 4: Corre la suite entera**

Run: `.venv/bin/python -m pytest tests -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add llmz80/studio/screen.py tests/test_screen.py
git commit -m "refactor(studio): stop naming keys the interface no longer has"
```

---

### Task 7: Documentación y evidencia

**Files:**
- Modify: `README.md`, `docs/STUDIO_ROADMAP.md`

- [ ] **Step 1: Busca lo que documenta las teclas viejas**

Run: `grep -rn 'ctrl+f\|ctrl+d\|ctrl+w\|ctrl+t\|ctrl+r\|ctrl+n\|ctrl+o' README.md docs/ --include='*.md'`

Cada aparición pasa a describir el wizard: un paso cada vez, Enter para hacerlo, y `studio.log` como registro de lo que pasó.

- [ ] **Step 2: La evidencia de aceptación del spec**

Con un workspace vacío, llega hasta un `game.yml` válido usando sólo Enter, Esc y las flechas:

```bash
rm -rf /tmp/wizard-demo && mkdir -p /tmp/wizard-demo
.venv/bin/python -m llmz80.cli studio /tmp/wizard-demo
```

Crea un proyecto desde el paso 0, omite la referencia con `S`, entra al diseño con Enter, pinta algo, sal con Esc. Luego:

```bash
cat /tmp/wizard-demo/*/studio.log
```

**Pega esa salida en el informe.** Tiene que contar la sesión entera: qué se abrió, qué se omitió, qué se guardó, con sus horas. Si al recorrerlo hay algún momento en que no sabes qué tecla pulsar sin mirar el código, dilo: es exactamente el fallo que este trabajo existe para evitar.

- [ ] **Step 3: Suite y linter**

Run: `.venv/bin/python -m pytest tests -q && make lint`
Expected: PASS en ambos.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "docs(studio): describe the wizard instead of the shortcuts"
```

---

## Notas para quien ejecute

- **El diario escribe y devuelve la misma cadena.** Nunca compongas la versión de pantalla por tu cuenta: es la única forma de que fichero y pantalla no acaben contando cosas distintas del mismo suceso.
- **`skipped` es estado de sesión, no del proyecto.** Omitir un paso queda escrito en el diario porque es una decisión que conviene ver, pero no es evidencia de trabajo hecho y no debe leerse como si lo fuera al reabrir.
- **No amplíes el editor.** Sigue pintando muro y suelo con dos glifos fijos, así que un tercer tile sigue invisible. Está fuera de alcance a propósito y anotado como trabajo aparte; arreglarlo aquí mezclaría dos cosas.
- Si un test existente de `tui.py` prueba algo que sigue valiendo pero por otra tecla, **pórtalo**. Bórralo sólo si prueba un atajo que ya no existe como concepto.
