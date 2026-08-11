"""Pick worked examples to show whoever writes a program.

The catalog from the generation-quality programme already ranks the certified
example corpus; this decides what a Studio design should ask it for, and how
much of the answer fits in a prompt without crowding out the contract.
"""

from __future__ import annotations

from pathlib import Path

from llmz80.core.example_catalog import ExampleCatalog

from .models import GameProject
from .packs import PACKS_BY_ID

EXAMPLES_ROOT = Path(__file__).resolve().parents[2] / "examples"
REFERENCE_ROOT = Path(__file__).resolve().parents[2] / "resources" / "studio_reference"

#: Examples to show. Two is a deliberate ceiling: the contract, the design and
#: the acceptance script all have to survive alongside them.
MAX_EXAMPLES = 2

#: Characters of any single example. A truncated program still demonstrates
#: idiom, and an over-long one pushes the acceptance criteria out of view.
MAX_EXAMPLE_CHARS = 9000


def retrieval_query(project: GameProject) -> str:
    """Describe the design in the vocabulary the catalog indexes."""
    roles = sorted({entity.role for entity in project.entities})
    behaviours = sorted(
        {entity.behaviour for entity in project.entities if entity.behaviour != "auto"}
    )
    pack = PACKS_BY_ID.get(project.genre)
    parts = [
        project.genre.replace("_", " "),
        # The typology's own keywords describe the game in the corpus's terms,
        # which its id rarely does: "breakout" retrieves less than "ball bat".
        " ".join(pack.capabilities) if pack else "",
        project.presentation.style,
        "keyboard input sprite movement collision score lives",
        " ".join(roles),
        " ".join(behaviours),
    ]
    if any(level.tiles for level in project.levels):
        parts.append("tile map walls")
    if project.audio.effects:
        parts.append("sound effects beeper")
    return " ".join(part for part in parts if part)


def _trim(source: str) -> str:
    if len(source) <= MAX_EXAMPLE_CHARS:
        return source
    return source[:MAX_EXAMPLE_CHARS].rstrip() + "\n/* ... truncated ... */\n"


def reference_program(project: GameProject) -> tuple[str, str] | None:
    """The worked program that satisfies a design like this one, if present."""
    target = "spectrum" if project.target.platform.value == "spectrum" else "amstrad_cpc"
    engine = REFERENCE_ROOT / target / "src" / "engine.c"
    if not engine.is_file():
        return None
    return "studio_reference/engine.c", engine.read_text(encoding="utf-8")


def catalog_examples(project: GameProject, limit: int = MAX_EXAMPLES) -> list[tuple[str, str]]:
    """Certified programs for this target, ranked against the design."""
    platform = project.target.platform.value
    directory = EXAMPLES_ROOT / platform
    if not directory.is_dir():
        return []
    catalog = ExampleCatalog(platform, directory)
    found: list[tuple[str, str]] = []
    for hit in catalog.search(retrieval_query(project), limit=limit * 2):
        source = hit.get("content") or hit.get("source") or ""
        if not source.strip():
            continue
        found.append((hit.get("path") or "example.c", _trim(source)))
        if len(found) >= limit:
            break
    return found


def examples_prompt(project: GameProject) -> str:
    """Worked code for the prompt, reference program first.

    The reference goes first because it is the one program known to satisfy this
    contract on this machine; the catalog entries follow as evidence of local
    idiom rather than of the contract.
    """
    blocks: list[str] = []
    reference = reference_program(project)
    if reference:
        name, source = reference
        blocks.append(
            "This program satisfies the state contract on this machine. Study how\n"
            "it declares the contract symbols and paces its main loop.\n\n"
            f"--- {name} ---\n{_trim(source)}"
        )
    for name, source in catalog_examples(project):
        blocks.append(
            f"A certified example for this machine, for idiom and API use.\n\n"
            f"--- {name} ---\n{source}"
        )
    if not blocks:
        return ""
    return (
        "WORKED EXAMPLES\n\n"
        "These compile and run on this target. Follow their idiom; do not copy\n"
        "them wholesale, since none of them is the game you are being asked for.\n\n"
        + "\n\n".join(blocks)
    )
