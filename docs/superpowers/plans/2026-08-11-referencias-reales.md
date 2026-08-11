# Referencias reales dirigiendo el diseño — Plan de implementación (1 de 3)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Que citar un juego real en el brief produzca una ficha documentada por búsqueda web, archivada en el proyecto, que dirija tanto una propuesta de diseño revisable como el prompt del escritor.

**Architecture:** Un módulo nuevo `llmz80/studio/reference.py` obtiene una `GameReference` tipada con la herramienta `web_search` de la Responses API y la archiva en `<proyecto>/reference.yml`. A partir de ahí todo es determinista: la ficha alimenta `generator.writing_prompt` y una `ProjectProposal` que se aplica con el `apply_proposal` que ya existe, con su diff y sus protecciones. El cliente se inyecta en todas partes, igual que en `ResponsesProgramWriter`, así que ningún test toca la red.

**Tech Stack:** Python 3.10+, pydantic v2, OpenAI Responses API (`responses.parse` con `tools=[{"type": "web_search"}]`), PyYAML, pytest.

**Planes hermanos (no incluidos aquí):** 2 de 3, sprites por IA y blitter enmascarado. 3 de 3, gates de game feel y TUI de mando. Este plan no depende de ninguno de los dos.

---

## Estructura de archivos

| Archivo | Responsabilidad |
|---|---|
| `llmz80/studio/reference.py` (crear) | Modelo `GameReference`, búsqueda, persistencia y bloque de prompt. Nada más: no conoce `ProjectProposal` ni la TUI |
| `llmz80/studio/reference_design.py` (crear) | Traduce una ficha a `ProjectProposal`. Separado de `reference.py` porque cambia por motivos distintos: uno sigue a la fuente de datos, el otro al esquema del diseño |
| `llmz80/studio/generator.py` (modificar) | `writing_prompt` gana la interfaz de la librería y la ficha |
| `llmz80/studio/services.py` (modificar) | Dos operaciones nuevas que la TUI y el CLI comparten |
| `llmz80/cli.py` (modificar) | Comandos `project reference` y `project propose` |
| `tests/test_studio_reference.py` (crear) | Ficha, búsqueda con cliente falso, persistencia |
| `tests/test_studio_reference_design.py` (crear) | Ficha a propuesta, y las protecciones |
| `tests/test_studio_generator.py` (modificar) | Los dos bloques nuevos del prompt |

---

### Task 1: El escritor ve la interfaz de la plataforma

Hoy `_instructions` le dice al modelo que `platform.h` es incluible pero nunca le enseña su contenido. Por eso inventó `plat_sync` cuando la función real es `plat_wait_frame`, y gastó dos de cuatro intentos en descubrirlo.

**Files:**
- Modify: `llmz80/studio/generator.py:79-95` (`writing_prompt`)
- Test: `tests/test_studio_generator.py`

- [ ] **Step 1: Escribir el test que falla**

Añadir al final de `tests/test_studio_generator.py`:

```python
def test_the_writing_prompt_shows_the_platform_interface():
    """A writer told to include platform.h must be shown what is in it."""
    project = create_default_project("Iface", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)

    prompt = writing_prompt(project, with_examples=False)

    assert "unsigned char plat_wait_frame(void);" in prompt
    assert "void plat_cell(unsigned char col, unsigned char row, unsigned char kind);" in prompt
    assert "PLATFORM LIBRARY INTERFACE" in prompt
```

Comprobar que la cabecera del archivo ya importa lo necesario; si no, añadir:

```python
from llmz80.studio.generator import writing_prompt
from llmz80.studio.models import GenreId, TargetPlatform
from llmz80.studio.packs import create_default_project
```

- [ ] **Step 2: Ejecutar el test y verificar que falla**

Run: `python -m pytest tests/test_studio_generator.py::test_the_writing_prompt_shows_the_platform_interface -v`
Expected: FAIL, `assert 'PLATFORM LIBRARY INTERFACE' in prompt`

- [ ] **Step 3: Implementar**

En `llmz80/studio/generator.py`, junto a los imports, añadir:

```python
#: The interface every target implements. Handed to the writer verbatim: telling
#: it the library exists without showing the header invites invented functions.
PLATFORM_HEADER = (
    Path(__file__).resolve().parents[2] / "resources" / "studio_lib" / "common" / "platform.h"
)


def library_interface() -> str:
    """The platform header, as a prompt block."""
    body = PLATFORM_HEADER.read_text(encoding="utf-8")
    return "PLATFORM LIBRARY INTERFACE\n\nThis header is beside your sources:\n\n" + body
```

Y en `writing_prompt`, insertar el bloque tras las notas de plataforma:

```python
    parts = [
        generation_prompt(project),
        platform_notes(project.target.platform.value),
        library_interface(),
    ]
```

- [ ] **Step 4: Ejecutar y verificar que pasa**

Run: `python -m pytest tests/test_studio_generator.py -v`
Expected: PASS, incluidos los tests ya existentes del módulo

- [ ] **Step 5: Commit**

```bash
git add llmz80/studio/generator.py tests/test_studio_generator.py
git commit -m "fix(studio): show the writer the header it is told to include"
```

---

### Task 2: La ficha de referencia como dato

**Files:**
- Create: `llmz80/studio/reference.py`
- Test: `tests/test_studio_reference.py`

- [ ] **Step 1: Escribir el test que falla**

Crear `tests/test_studio_reference.py`:

```python
"""The reference dossier: shape, rules and what it refuses to be."""

import pytest
from pydantic import ValidationError

from llmz80.studio.reference import GameReference, ReferenceSource


def _dossier(**overrides) -> GameReference:
    document = {
        "identified": True,
        "confidence": "high",
        "title": "Zampa Bolas",
        "publisher": "Iber Soft",
        "year": 1985,
        "platforms": ["spectrum"],
        "mechanics": ["eat every dot", "two ghosts chase the player"],
        "screen_layout": "score on the top row, maze below it",
        "pacing": "the player moves one cell per frame, ghosts one every four",
        "visual_style": "bright maze on black, chunky monochrome sprites",
        "level_structure": "three mazes of rising density",
        "sources": [
            {
                "url": "https://worldofspectrum.org/example",
                "title": "Zampa Bolas",
                "retrieved_at": "2026-08-11T09:00:00Z",
            }
        ],
    }
    document.update(overrides)
    return GameReference.model_validate(document)


def test_a_dossier_keeps_its_sources():
    dossier = _dossier()

    assert dossier.identified is True
    assert isinstance(dossier.sources[0], ReferenceSource)
    assert dossier.sources[0].url == "https://worldofspectrum.org/example"


def test_an_identified_dossier_without_sources_is_refused():
    """A claim about a real game with nothing behind it is worse than no claim."""
    with pytest.raises(ValidationError, match="sources"):
        _dossier(sources=[])


def test_an_unidentified_dossier_needs_no_sources():
    dossier = _dossier(identified=False, confidence="low", sources=[], title="")

    assert dossier.identified is False
    assert dossier.sources == []
```

- [ ] **Step 2: Ejecutar el test y verificar que falla**

Run: `python -m pytest tests/test_studio_reference.py -v`
Expected: FAIL, `ModuleNotFoundError: No module named 'llmz80.studio.reference'`

- [ ] **Step 3: Implementar**

Crear `llmz80/studio/reference.py`:

```python
"""What is known about the real game a brief names, and where it was read.

Studio's typologies give a design its shape; this gives it its identity. The
dossier is deliberately prose-heavy: a model writing a program reads sentences
better than it reads enum values, and a person correcting a wrong dossier edits
sentences more happily than fields.

Every claim carries its sources, and a dossier that claims to have identified a
game without any is refused. An unsupported claim about a real title is worse
than admitting the title was not found, because the rest of the pipeline treats
identification as licence to rewrite the design.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ReferenceSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    url: str = Field(min_length=1, max_length=400)
    title: str = Field(min_length=1, max_length=200)
    retrieved_at: datetime


class GameReference(BaseModel):
    """One researched game, as the rest of Studio needs it."""

    model_config = ConfigDict(extra="forbid")

    identified: bool
    confidence: Literal["high", "medium", "low"]
    title: str = Field(default="", max_length=120)
    publisher: str = Field(default="", max_length=120)
    year: int | None = Field(default=None, ge=1975, le=1999)
    platforms: list[str] = Field(default_factory=list, max_length=8)
    mechanics: list[str] = Field(default_factory=list, max_length=20)
    screen_layout: str = Field(default="", max_length=600)
    pacing: str = Field(default="", max_length=600)
    visual_style: str = Field(default="", max_length=600)
    level_structure: str = Field(default="", max_length=600)
    sources: list[ReferenceSource] = Field(default_factory=list, max_length=10)

    @model_validator(mode="after")
    def validate_identification(self) -> "GameReference":
        if self.identified and not self.sources:
            raise ValueError(
                "an identified game must cite its sources; "
                "without them the dossier cannot be checked or corrected"
            )
        if self.identified and not self.title.strip():
            raise ValueError("an identified game must have a title")
        return self
```

- [ ] **Step 4: Ejecutar y verificar que pasa**

Run: `python -m pytest tests/test_studio_reference.py -v`
Expected: PASS, 3 tests

- [ ] **Step 5: Commit**

```bash
git add llmz80/studio/reference.py tests/test_studio_reference.py
git commit -m "feat(studio): model what is known about a real game"
```

---

### Task 3: Buscar la ficha, sin tocar la red en los tests

**Files:**
- Modify: `llmz80/studio/reference.py`
- Test: `tests/test_studio_reference.py`

- [ ] **Step 1: Escribir el test que falla**

Añadir a `tests/test_studio_reference.py`:

```python
class _FakeResponses:
    """Stands in for client.responses, recording how it was called."""

    def __init__(self, parsed):
        self.parsed = parsed
        self.calls = []

    def parse(self, **kwargs):
        self.calls.append(kwargs)
        return type("Response", (), {"output_parsed": self.parsed})()


class _FakeClient:
    def __init__(self, parsed):
        self.responses = _FakeResponses(parsed)


def test_research_asks_for_web_search_and_returns_the_dossier():
    client = _FakeClient(_dossier())

    dossier = ResponsesReferenceResearcher(client).research(
        "Zampabolas runs through a walled maze eating every dot", "spectrum"
    )

    assert dossier.title == "Zampa Bolas"
    call = client.responses.calls[0]
    assert {"type": "web_search"} in call["tools"]
    assert call["text_format"] is GameReference
    assert "spectrum" in call["input"][1]["content"]


def test_research_refuses_an_empty_parse():
    """No dossier is a failure, not an unidentified game: they mean different things."""
    client = _FakeClient(None)

    with pytest.raises(ValueError, match="did not return"):
        ResponsesReferenceResearcher(client).research("something", "spectrum")
```

Y añadir al import de cabecera del archivo de test:

```python
from llmz80.studio.reference import (
    GameReference,
    ReferenceSource,
    ResponsesReferenceResearcher,
)
```

- [ ] **Step 2: Ejecutar el test y verificar que falla**

Run: `python -m pytest tests/test_studio_reference.py -v`
Expected: FAIL, `ImportError: cannot import name 'ResponsesReferenceResearcher'`

- [ ] **Step 3: Implementar**

Añadir a `llmz80/studio/reference.py`:

```python
from typing import Any, Protocol

#: What the researcher is told before it looks anything up. It is told to admit
#: failure explicitly because a model asked to describe a game it cannot find
#: will describe a plausible game instead, and a plausible game is exactly the
#: failure this whole stage exists to prevent.
RESEARCH_SYSTEM_PROMPT = """\
You research games published for 8-bit home computers in the 1980s, chiefly the
ZX Spectrum and the Amstrad CPC.

Search the web for the game the brief names. Report only what your sources
support, and cite every source you used.

If you cannot find the game, or you are not confident that what you found is the
same game the brief means, set identified to false and leave the descriptive
fields empty. Do not describe a game you did not find. A wrong dossier is worse
than no dossier, because the rest of the system will rebuild the design from it.

Describe mechanics, pacing, screen layout and visual style in short plain
sentences that a programmer can act on, not in marketing prose.
"""


class ReferenceResearcher(Protocol):
    def research(self, brief: str, target: str) -> GameReference: ...


class ResponsesReferenceResearcher:
    """Researches through the OpenAI Responses API with web search enabled."""

    def __init__(self, client: Any, model: str = "gpt-5") -> None:
        self.client = client
        self.model = model

    def research(self, brief: str, target: str) -> GameReference:
        response = self.client.responses.parse(
            model=self.model,
            input=[
                {"role": "system", "content": RESEARCH_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"TARGET PLATFORM: {target}\n\n"
                        f"WHAT THE DESIGNER ASKED FOR:\n{brief}"
                    ),
                },
            ],
            tools=[{"type": "web_search"}],
            text_format=GameReference,
        )
        parsed = response.output_parsed
        if parsed is None:
            raise ValueError("the model did not return a structured game reference")
        return parsed
```

- [ ] **Step 4: Ejecutar y verificar que pasa**

Run: `python -m pytest tests/test_studio_reference.py -v`
Expected: PASS, 5 tests

- [ ] **Step 5: Commit**

```bash
git add llmz80/studio/reference.py tests/test_studio_reference.py
git commit -m "feat(studio): research a named game with web search"
```

---

### Task 4: Archivar la ficha para que el build sea reproducible

La búsqueda no es reproducible; el archivo sí. Todo lo que va después lee el archivo.

**Files:**
- Modify: `llmz80/studio/reference.py`
- Test: `tests/test_studio_reference.py`

- [ ] **Step 1: Escribir el test que falla**

Añadir a `tests/test_studio_reference.py`:

```python
def test_a_dossier_survives_a_round_trip(tmp_path):
    saved = save_reference(_dossier(), tmp_path)

    assert saved == tmp_path / "reference.yml"
    assert load_reference(tmp_path).title == "Zampa Bolas"


def test_a_missing_dossier_reads_as_none(tmp_path):
    assert load_reference(tmp_path) is None


def test_a_corrupt_dossier_is_refused_rather_than_ignored(tmp_path):
    """Silently ignoring a broken file would rebuild the design from nothing."""
    (tmp_path / "reference.yml").write_text("identified: yes please\n", encoding="utf-8")

    with pytest.raises(ValueError, match="reference.yml"):
        load_reference(tmp_path)


def test_a_hand_edited_dossier_wins(tmp_path):
    """Correcting a wrong dossier by hand has to stick, or correcting it is pointless."""
    save_reference(_dossier(), tmp_path)
    path = tmp_path / "reference.yml"
    path.write_text(
        path.read_text(encoding="utf-8").replace("Iber Soft", "Topo Soft"), encoding="utf-8"
    )

    assert load_reference(tmp_path).publisher == "Topo Soft"
```

Ampliar el import de `llmz80.studio.reference` con `load_reference` y `save_reference`.

- [ ] **Step 2: Ejecutar el test y verificar que falla**

Run: `python -m pytest tests/test_studio_reference.py -v`
Expected: FAIL, `ImportError: cannot import name 'save_reference'`

- [ ] **Step 3: Implementar**

Añadir a `llmz80/studio/reference.py`:

```python
from pathlib import Path

import yaml

#: Beside game.yml, and just as editable by hand.
REFERENCE_FILENAME = "reference.yml"


def save_reference(dossier: GameReference, directory: Path) -> Path:
    """Archive the dossier atomically, so a crash leaves the old one intact."""
    directory = Path(directory).expanduser().resolve()
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / REFERENCE_FILENAME
    text = yaml.safe_dump(
        dossier.model_dump(mode="json"), allow_unicode=True, sort_keys=False, width=100
    )
    temporary = path.with_suffix(".yml.tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)
    return path


def load_reference(directory: Path) -> GameReference | None:
    """Read the archived dossier, or None when the project has none.

    A malformed file raises: a project that has a dossier and cannot read it is
    not the same as a project without one, and treating them alike would quietly
    rebuild a design from a blank.
    """
    path = Path(directory).expanduser().resolve() / REFERENCE_FILENAME
    if not path.exists():
        return None
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return GameReference.model_validate(data)
    except Exception as exc:
        raise ValueError(f"cannot read {path.name}: {exc}") from exc
```

- [ ] **Step 4: Ejecutar y verificar que pasa**

Run: `python -m pytest tests/test_studio_reference.py -v`
Expected: PASS, 9 tests

- [ ] **Step 5: Commit**

```bash
git add llmz80/studio/reference.py tests/test_studio_reference.py
git commit -m "feat(studio): archive the dossier so a build stops depending on the web"
```

---

### Task 5: La ficha llega al escritor

**Files:**
- Modify: `llmz80/studio/reference.py` (bloque de prompt)
- Modify: `llmz80/studio/generator.py:79-95`
- Test: `tests/test_studio_reference.py`, `tests/test_studio_generator.py`

- [ ] **Step 1: Escribir el test que falla**

En `tests/test_studio_reference.py`:

```python
def test_the_prompt_block_carries_the_facts_and_the_sources():
    block = reference_prompt(_dossier())

    assert "REFERENCE GAME" in block
    assert "Zampa Bolas" in block
    assert "Iber Soft" in block
    assert "two ghosts chase the player" in block
    assert "https://worldofspectrum.org/example" in block


def test_an_unidentified_dossier_produces_no_prompt_block():
    assert reference_prompt(_dossier(identified=False, sources=[], title="")) == ""


def test_no_dossier_produces_no_prompt_block():
    assert reference_prompt(None) == ""
```

En `tests/test_studio_generator.py`:

```python
def test_the_writing_prompt_carries_the_dossier_when_the_project_has_one(tmp_path):
    project = create_default_project("Ref", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)
    dossier = GameReference(
        identified=True,
        confidence="high",
        title="Zampa Bolas",
        publisher="Iber Soft",
        mechanics=["eat every dot"],
        sources=[
            ReferenceSource(
                url="https://example.org/z",
                title="Zampa Bolas",
                retrieved_at="1985-01-01T00:00:00Z",
            )
        ],
    )

    prompt = writing_prompt(project, with_examples=False, reference=dossier)

    assert "REFERENCE GAME" in prompt
    assert "Zampa Bolas" in prompt


def test_the_writing_prompt_is_unchanged_without_a_dossier():
    project = create_default_project("Ref", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)

    assert "REFERENCE GAME" not in writing_prompt(project, with_examples=False)
```

Añadir a los imports de `tests/test_studio_generator.py`:

```python
from llmz80.studio.reference import GameReference, ReferenceSource
```

- [ ] **Step 2: Ejecutar los tests y verificar que fallan**

Run: `python -m pytest tests/test_studio_reference.py tests/test_studio_generator.py -v`
Expected: FAIL, `ImportError: cannot import name 'reference_prompt'` y `TypeError: writing_prompt() got an unexpected keyword argument 'reference'`

- [ ] **Step 3: Implementar**

Añadir a `llmz80/studio/reference.py`:

```python
def reference_prompt(dossier: GameReference | None) -> str:
    """The dossier as a prompt block, or nothing at all.

    An unidentified dossier yields nothing rather than a block saying so: the
    absence of a reference is already the default, and a paragraph explaining
    that there is no reference only spends attention.
    """
    if dossier is None or not dossier.identified:
        return ""
    lines = ["REFERENCE GAME", ""]
    published = f"{dossier.publisher}, {dossier.year}" if dossier.year else dossier.publisher
    lines.append(f"{dossier.title} ({published}) for {', '.join(dossier.platforms)}.")
    lines.append(
        "This is what the designer asked for. Make the program feel like this "
        "game, within what the design below states."
    )
    for heading, value in (
        ("How it plays", "\n".join(f"  - {rule}" for rule in dossier.mechanics)),
        ("Screen layout", dossier.screen_layout),
        ("Pacing", dossier.pacing),
        ("Look", dossier.visual_style),
        ("Levels", dossier.level_structure),
    ):
        if value.strip():
            lines.extend(["", f"{heading}:", value if "\n" in value else f"  {value}"])
    lines.extend(["", f"Researched from: {', '.join(source.url for source in dossier.sources)}"])
    return "\n".join(lines)
```

En `llmz80/studio/generator.py`, cambiar la firma y el cuerpo de `writing_prompt`:

```python
def writing_prompt(
    project: GameProject,
    *,
    with_examples: bool = True,
    reference: "GameReference | None" = None,
) -> str:
    """Everything the writer is told before its first attempt."""
    parts = [
        generation_prompt(project),
        platform_notes(project.target.platform.value),
        library_interface(),
        reference_prompt(reference),
    ]
    if with_examples:
        examples = examples_prompt(project)
        if examples:
            parts.append(examples)
    parts.append(_instructions(project))
    return "\n\n".join(part for part in parts if part)
```

Y añadir el import en `llmz80/studio/generator.py`:

```python
from .reference import GameReference, reference_prompt
```

Comprobar si alguna llamada existente pasa `with_examples` posicionalmente y corregirla al nuevo keyword:

Run: `grep -rn "writing_prompt(" llmz80 tests`

- [ ] **Step 4: Ejecutar y verificar que pasan**

Run: `python -m pytest tests/test_studio_reference.py tests/test_studio_generator.py -v`
Expected: PASS

- [ ] **Step 5: Que el escritor use realmente la ficha**

En `llmz80/studio/generator.py`, `ResponsesProgramWriter.write` construye el prompt. Pasarle la ficha del proyecto:

```python
    def write(self, project: GameProject, feedback: str | None = None) -> ProgramSources:
        prompt = writing_prompt(project, reference=self.reference)
```

El constructor actual, en `llmz80/studio/generator.py:153`, es exactamente:

```python
    def __init__(self, client: Any, model: str = "gpt-5") -> None:
        self.client = client
        self.model = model
```

Sustituirlo por:

```python
    def __init__(
        self,
        client: Any,
        model: str = "gpt-5",
        reference: GameReference | None = None,
    ) -> None:
        self.client = client
        self.model = model
        self.reference = reference
```

Y en `write`, la línea `content = writing_prompt(project)` pasa a ser:

```python
        content = writing_prompt(project, reference=self.reference)
```

`with_examples` ya es keyword-only y no hay llamadas posicionales, así que ningún
llamador existente se rompe. Los tres que hay están en `generator.py:158`,
`tests/test_studio_retrieval.py:76-77` y `tests/test_studio_generator.py:67`.

- [ ] **Step 6: Que `project write` pase la ficha archivada**

Sin esto la cadena se queda a un paso del programa. En `llmz80/cli.py`, en el
bloque del comando `write`, la construcción del escritor pasa de:

```python
        writer = ResponsesProgramWriter(OpenAI(api_key=load_api_key()), model=model)
```

a:

```python
        from llmz80.studio.reference import load_reference

        dossier = load_reference(directory)
        if dossier is not None and dossier.identified:
            print(f"Writing as {dossier.title} ({dossier.publisher}).")
        writer = ResponsesProgramWriter(
            OpenAI(api_key=load_api_key()), model=model, reference=dossier
        )
```

- [ ] **Step 7: Ejecutar la suite entera**

Run: `python -m pytest tests -q`
Expected: PASS, sin regresiones

- [ ] **Step 8: Commit**

```bash
git add llmz80/studio/reference.py llmz80/studio/generator.py llmz80/cli.py tests/test_studio_reference.py tests/test_studio_generator.py
git commit -m "feat(studio): tell the writer which game it is making"
```

---

### Task 6: De la ficha a una propuesta de diseño revisable

**Files:**
- Create: `llmz80/studio/reference_design.py`
- Test: `tests/test_studio_reference_design.py`

- [ ] **Step 1: Escribir el test que falla**

Crear `tests/test_studio_reference_design.py`:

```python
"""Turning a dossier into a reviewable design proposal."""

import pytest

from llmz80.studio.models import GenreId, TargetPlatform
from llmz80.studio.packs import create_default_project
from llmz80.studio.planner import ProjectChange, ProjectProposal, apply_proposal
from llmz80.studio.reference import GameReference, ReferenceSource
from llmz80.studio.reference_design import ResponsesReferenceDesigner


def _dossier(**overrides) -> GameReference:
    document = {
        "identified": True,
        "confidence": "high",
        "title": "Zampa Bolas",
        "publisher": "Iber Soft",
        "year": 1985,
        "platforms": ["spectrum"],
        "mechanics": ["eat every dot", "two ghosts chase the player"],
        "screen_layout": "score on the top row",
        "pacing": "ghosts are slower than the player",
        "visual_style": "bright maze on black",
        "level_structure": "three mazes of rising density",
        "sources": [
            {
                "url": "https://example.org/z",
                "title": "Zampa Bolas",
                "retrieved_at": "2026-08-11T09:00:00Z",
            }
        ],
    }
    document.update(overrides)
    return GameReference.model_validate(document)


class _FakeResponses:
    def __init__(self, parsed):
        self.parsed = parsed
        self.calls = []

    def parse(self, **kwargs):
        self.calls.append(kwargs)
        return type("Response", (), {"output_parsed": self.parsed})()


class _FakeClient:
    def __init__(self, parsed):
        self.responses = _FakeResponses(parsed)


@pytest.fixture
def project():
    return create_default_project("Zampa", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)


def test_the_dossier_and_the_project_both_reach_the_model(project):
    proposal = ProjectProposal(
        summary="match the original",
        changes=[
            ProjectChange(
                path="/presentation/style",
                operation="replace",
                value="bright maze on black",
                reason="the original drew a bright maze on black",
            )
        ],
    )
    client = _FakeClient(proposal)

    ResponsesReferenceDesigner(client).propose(project, _dossier())

    sent = client.responses.calls[0]["input"][1]["content"]
    assert "Zampa Bolas" in sent
    assert "maze_chase" in sent


def test_a_proposal_from_a_dossier_applies_like_any_other(project):
    proposal = ProjectProposal(
        summary="match the original",
        changes=[
            ProjectChange(
                path="/presentation/style",
                operation="replace",
                value="bright maze on black",
                reason="the original drew a bright maze on black",
            )
        ],
    )

    updated = apply_proposal(project, proposal)

    assert updated.presentation.style == "bright maze on black"
    assert project.presentation.style != "bright maze on black"


def test_an_unidentified_dossier_yields_no_proposal(project):
    """Nothing was found, so there is nothing to rebuild the design from."""
    client = _FakeClient(None)

    with pytest.raises(ValueError, match="not identified"):
        ResponsesReferenceDesigner(client).propose(
            project, _dossier(identified=False, sources=[], title="")
        )

    assert client.responses.calls == []
```

- [ ] **Step 2: Ejecutar el test y verificar que falla**

Run: `python -m pytest tests/test_studio_reference_design.py -v`
Expected: FAIL, `ModuleNotFoundError: No module named 'llmz80.studio.reference_design'`

- [ ] **Step 3: Implementar**

Crear `llmz80/studio/reference_design.py`:

```python
"""Rebuild a design from what was researched about the real game.

Kept apart from `reference.py` because the two change for different reasons: one
follows where the facts come from, this one follows the design schema. It emits
the same `ProjectProposal` the AI assistant already emits, so it inherits the
diff, the protected paths and the playability refusal for free.
"""

from __future__ import annotations

from typing import Any

from .models import GameProject
from .planner import ProjectProposal
from .reference import GameReference

#: Everything the designer is told. It is pointed at the fields that carry a
#: game's identity, and warned off the ones that carry Studio's guarantees:
#: a proposal touching a protected path is refused on apply anyway, and one that
#: seals a level off is refused by the playability gate, so spending changes
#: there only wastes the twenty a proposal is allowed.
DESIGN_SYSTEM_PROMPT = """\
You adapt a game design so it resembles a real 1980s game that has been
researched for you.

Propose JSON-pointer changes to the supplied GameProject. Aim them at what makes
the game recognisable:
  /levels/N/tiles          the maze or screen layout, as rows of '#' and '.'
  /levels/N/spawns         where each actor starts
  /entities/N/count        how many of each actor
  /entities/N/speed        pacing, 1 is slowest and 4 moves every frame
  /entities/N/behaviour    chase, patrol_h, patrol_v, bounce, guard
  /presentation/style      how it should look, in a short phrase
  /gameplay/lives          lives the player starts with
  /gameplay/difficulty_curve

Rules:
  * Terrain rows must all be the same width, keep the outer ring solid, and
    leave every floor cell reachable. A layout that seals anything off is
    rejected and your whole proposal is lost with it.
  * Never propose changes to /schema_version, /metadata/slug, /target/platform,
    /acceptance or /budgets. They are refused.
  * Only propose what the dossier supports. Where it says nothing, leave the
    design alone.
  * Give each change a reason that cites what in the dossier motivates it.
"""


class ReferenceDesigner:
    def propose(
        self, project: GameProject, dossier: GameReference
    ) -> ProjectProposal: ...


class ResponsesReferenceDesigner:
    """Proposes a design adaptation through the OpenAI Responses API."""

    def __init__(self, client: Any, model: str = "gpt-5") -> None:
        self.client = client
        self.model = model

    def propose(self, project: GameProject, dossier: GameReference) -> ProjectProposal:
        if not dossier.identified:
            raise ValueError(
                "this game was not identified, so there is nothing to adapt the design to"
            )
        response = self.client.responses.parse(
            model=self.model,
            input=[
                {"role": "system", "content": DESIGN_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"RESEARCHED GAME:\n{dossier.model_dump_json(indent=2)}\n\n"
                        f"CURRENT DESIGN:\n{project.model_dump_json(indent=2)}"
                    ),
                },
            ],
            text_format=ProjectProposal,
        )
        parsed = response.output_parsed
        if parsed is None:
            raise ValueError("the model did not return a structured project proposal")
        return parsed
```

- [ ] **Step 4: Ejecutar y verificar que pasa**

Run: `python -m pytest tests/test_studio_reference_design.py -v`
Expected: PASS, 3 tests

- [ ] **Step 5: Commit**

```bash
git add llmz80/studio/reference_design.py tests/test_studio_reference_design.py
git commit -m "feat(studio): adapt a design to the game it was named after"
```

---

### Task 7: Las dos operaciones, en los servicios

La TUI y el CLI comparten operaciones; ninguna de las dos decide nada.

**Files:**
- Modify: `llmz80/studio/services.py`
- Test: `tests/test_studio_reference_design.py`

- [ ] **Step 1: Escribir el test que falla**

Añadir a `tests/test_studio_reference_design.py`:

```python
from llmz80.studio.reference import load_reference
from llmz80.studio.services import StudioService


def test_researching_archives_the_dossier_in_the_project(tmp_path):
    service = StudioService.at(tmp_path)
    project, directory = service.create_project(
        "Zampa", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE
    )

    class _Researcher:
        def research(self, brief, target):
            return _dossier()

    dossier = service.research_reference(project, directory, _Researcher())

    assert dossier.title == "Zampa Bolas"
    assert load_reference(directory).title == "Zampa Bolas"


def test_a_reference_proposal_is_returned_with_its_diff(tmp_path):
    service = StudioService.at(tmp_path)
    project, directory = service.create_project(
        "Zampa", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE
    )
    proposal = ProjectProposal(
        summary="match the original",
        changes=[
            ProjectChange(
                path="/presentation/style",
                operation="replace",
                value="bright maze on black",
                reason="the original drew a bright maze on black",
            )
        ],
    )

    class _Designer:
        def propose(self, project, dossier):
            return proposal

    returned, diff = service.propose_from_reference(project, directory, _Designer(), _dossier())

    assert returned is proposal
    assert "presentation/style" in diff


def test_proposing_without_a_dossier_says_so(tmp_path):
    service = StudioService.at(tmp_path)
    project, directory = service.create_project(
        "Zampa", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE
    )

    class _Designer:
        def propose(self, project, dossier):
            raise AssertionError("must not be called")

    with pytest.raises(ValueError, match="no researched game"):
        service.propose_from_reference(project, directory, _Designer(), None)
```

- [ ] **Step 2: Ejecutar los tests y verificar que fallan**

Run: `python -m pytest tests/test_studio_reference_design.py -v`
Expected: FAIL, `AttributeError: 'StudioService' object has no attribute 'research_reference'`

- [ ] **Step 3: Implementar**

Añadir a los imports de `llmz80/studio/services.py`:

```python
from .planner import ProjectProposal, proposal_diff
from .reference import GameReference, load_reference, save_reference
```

Y añadir a `StudioService`, después de `add_asset`:

```python
    def research_reference(
        self, project: GameProject, directory: Path, researcher: Any
    ) -> GameReference:
        """Research the game the brief names and archive what was found.

        Archived whether or not the game was identified: knowing that a search
        already came up empty is worth as much as the dossier itself, and stops
        every later action paying for the same search again.
        """
        dossier = researcher.research(project.metadata.brief, project.target.platform.value)
        save_reference(dossier, directory)
        return dossier

    def reference(self, directory: Path) -> GameReference | None:
        return load_reference(directory)

    def propose_from_reference(
        self,
        project: GameProject,
        directory: Path,
        designer: Any,
        dossier: GameReference | None = None,
    ) -> tuple[ProjectProposal, str]:
        """Propose a design adaptation, returned with the diff a reviewer reads.

        Nothing is applied here. Applying is `planner.apply_proposal`, called
        once somebody has looked at the diff.
        """
        dossier = dossier or load_reference(directory)
        if dossier is None:
            raise ValueError("there is no researched game for this project yet")
        if not dossier.identified:
            raise ValueError(
                "no researched game was identified, so there is nothing to adapt to"
            )
        proposal = designer.propose(project, dossier)
        return proposal, proposal_diff(proposal)
```

- [ ] **Step 4: Ejecutar y verificar que pasan**

Run: `python -m pytest tests/test_studio_reference_design.py -v`
Expected: PASS, 6 tests

- [ ] **Step 5: Commit**

```bash
git add llmz80/studio/services.py tests/test_studio_reference_design.py
git commit -m "feat(studio): share research and adaptation between the front ends"
```

---

### Task 8: Usarlo desde el CLI

El plan 3 le pondrá pantalla. Hasta entonces esto es lo que hace la función utilizable de verdad.

**Files:**
- Modify: `llmz80/cli.py:8-25` (ayuda), `llmz80/cli.py:64-90` (despacho)
- Test: `tests/test_studio_cli.py`

- [ ] **Step 1: Escribir el test que falla**

Añadir a `tests/test_studio_cli.py`:

```python
def test_the_help_lists_the_reference_commands(capsys):
    from llmz80.cli import main

    main(["help"])

    printed = capsys.readouterr().out
    assert "project reference PATH" in printed
    assert "project adapt PATH" in printed
```

- [ ] **Step 2: Ejecutar el test y verificar que falla**

Run: `python -m pytest tests/test_studio_cli.py -v`
Expected: FAIL, `assert 'project reference PATH' in printed`

- [ ] **Step 3: Implementar**

En `_print_help`, añadir dos líneas tras `project contract PATH`:

```python
        "  llmz80 project reference PATH    (searches the web, calls the OpenAI API)\n"
        "  llmz80 project adapt PATH        (adapts the design to the researched game)\n"
```

En `_project_command`, añadir `"reference"` y `"adapt"` al conjunto de comandos aceptados, y antes del bloque de `write`:

```python
    if arguments[0] == "reference":
        from openai import OpenAI

        from llmz80.studio.reference import ResponsesReferenceResearcher
        from llmz80.utils.config import load_api_key, load_config

        model = load_config("config.yml").get("openai", {}).get("model", "gpt-5")
        print(f"Researching with {model}; this searches the web and calls the OpenAI API.")
        researcher = ResponsesReferenceResearcher(OpenAI(api_key=load_api_key()), model=model)
        dossier = service.research_reference(project, directory, researcher)
        if not dossier.identified:
            print("No game was identified. The design keeps its typology.")
            return 1
        print(f"{dossier.title} ({dossier.publisher}, {dossier.year})")
        for source in dossier.sources:
            print(f"  {source.url}")
        print(directory / "reference.yml")
        return 0
    if arguments[0] == "adapt":
        from openai import OpenAI

        from llmz80.studio.planner import apply_proposal
        from llmz80.studio.reference_design import ResponsesReferenceDesigner
        from llmz80.utils.config import load_api_key, load_config

        model = load_config("config.yml").get("openai", {}).get("model", "gpt-5")
        designer = ResponsesReferenceDesigner(OpenAI(api_key=load_api_key()), model=model)
        try:
            proposal, diff = service.propose_from_reference(project, directory, designer)
        except ValueError as exc:
            print(f"ERROR: {exc}")
            return 1
        print(diff)
        if input("\nApply these changes? [y/N] ").strip().casefold() != "y":
            print("Left unchanged.")
            return 0
        try:
            updated = apply_proposal(project, proposal)
        except ValueError as exc:
            print(f"REFUSED: {exc}")
            return 1
        service.save_project(updated, directory)
        print(directory / "game.yml")
        return 0
```

Comprobar que `directory` se calcula antes de este bloque; en el archivo actual se define justo tras el comando `validate`, así que los dos bloques nuevos van después de esa línea.

- [ ] **Step 4: Ejecutar y verificar que pasa**

Run: `python -m pytest tests/test_studio_cli.py -v`
Expected: PASS

- [ ] **Step 5: Ejecutar la suite entera y los linters**

Run: `python -m pytest tests -q && python -m flake8 llmz80/studio/reference.py llmz80/studio/reference_design.py && python -m black --check llmz80/studio`
Expected: PASS en los tres

- [ ] **Step 6: Commit**

```bash
git add llmz80/cli.py tests/test_studio_cli.py
git commit -m "feat(cli): research a game and adapt a design to it"
```

---

### Task 9: Documentar lo que cambió

**Files:**
- Modify: `README.md`, `docs/STUDIO_ROADMAP.md`

- [ ] **Step 1: README**

En la lista de características principales, tras la línea de "Jugabilidad contractual", añadir:

```markdown
- 📖 **Referencias reales**: cuando el brief nombra un juego de la época, Studio
  lo busca en la web, archiva una ficha citada en `reference.yml` y la usa para
  proponer un diseño y para decirle al escritor qué juego está haciendo; una
  ficha sin fuentes se rechaza y un juego no identificado deja el diseño intacto
```

En la sección de uso, tras `llmz80 project contract PATH`, añadir:

```markdown
llmz80 project reference PATH   # busca el juego citado y archiva la ficha
llmz80 project adapt PATH       # propone el diseño derivado y pide aprobación
```

- [ ] **Step 2: Roadmap**

En `docs/STUDIO_ROADMAP.md`, en la tabla de etapas, añadir una fila:

```markdown
| S11 | Referencias reales dirigiendo el diseño | Implemented | Ficha citada en `reference.yml`, propuesta con diff aprobable y bloque de prompt para el escritor |
```

Y en "Still open", borrar cualquier punto que este trabajo cierre, dejando los demás intactos.

- [ ] **Step 3: Commit**

```bash
git add README.md docs/STUDIO_ROADMAP.md
git commit -m "docs: record how a design learns which game it is"
```

---

## Verificación final del plan

- [ ] `python -m pytest tests -q` pasa entero
- [ ] `llmz80 project reference studio-projects/zampabolas` devuelve una ficha con fuentes reales
- [ ] `llmz80 project adapt studio-projects/zampabolas` enseña un diff que menciona el laberinto del original, y aplicarlo deja `game.yml` válido y solvable
- [ ] `llmz80 project write studio-projects/zampabolas` llega a un programa aceptado en menos intentos que los cuatro que gastó sin `platform.h`
