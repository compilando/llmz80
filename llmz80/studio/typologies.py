"""Typologies, demoted from catalogue to inspiration.

`resources/genres.yml` used to decide what a project was made of: a genre set
its terrain shape and its enemy count, and validation refused designs that
strayed. It now does exactly one thing -- give the designer prompt a list of
kinds of game that exist -- and has no say over any design.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

TYPOLOGIES_FILE = Path(__file__).resolve().parents[2] / "resources" / "genres.yml"


@lru_cache(maxsize=1)
def typology_hints(path: Path | None = None) -> str:
    """One line per typology, as a prompt block for whoever proposes a design."""
    document = yaml.safe_load((path or TYPOLOGIES_FILE).read_text(encoding="utf-8"))
    lines = [
        "KINDS OF GAME THAT EXIST",
        "",
        "These are examples, not a menu, and nothing validates a design against",
        "them. A design may be one of these, a mixture, or something else.",
        "",
    ]
    for entry in document.get("genres", []):
        lines.append(f"  {entry['name']}: {entry['description']}")
    return "\n".join(lines)
