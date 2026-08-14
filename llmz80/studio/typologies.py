"""Typologies, demoted from catalogue to inspiration.

`resources/genres.yml` used to decide what a project was made of: a genre set
its terrain shape and its enemy count, and validation refused designs that
strayed. It now does exactly one thing -- give the designer prompt a list of
kinds of game that exist -- and has no say over any design.
"""

from __future__ import annotations

from pathlib import Path

import yaml

TYPOLOGIES_FILE = Path(__file__).resolve().parents[2] / "resources" / "genres.yml"


def typology_hints(path: Path | None = None) -> str:
    """One line per typology, as a prompt block for whoever proposes a design.

    Not cached: `resources/genres.yml` is a small, rarely-read file, and a
    long-lived process (Studio's TUI, an editing session) that edits it should
    see the change on the next call rather than a stale `lru_cache` hit from
    an earlier one.
    """
    source = path or TYPOLOGIES_FILE
    document = yaml.safe_load(source.read_text(encoding="utf-8"))
    entries = document.get("genres", [])
    if not entries:
        raise ValueError(f"{source}: no typologies declared under 'genres'")
    lines = [
        "KINDS OF GAME THAT EXIST",
        "",
        "These are examples, not a menu, and nothing validates a design against",
        "them. A design may be one of these, a mixture, or something else.",
        "",
    ]
    for index, entry in enumerate(entries):
        missing = [key for key in ("name", "description") if key not in entry]
        if missing:
            raise ValueError(f"{source}: genres[{index}] is missing {', '.join(missing)}")
        lines.append(f"  {entry['name']}: {entry['description']}")
    return "\n".join(lines)
