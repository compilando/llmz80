"""Load the small compile-certified contracts supplied to code generation."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def runtime_header_path(platform: str) -> Path:
    if platform not in {"spectrum", "amstrad_cpc"}:
        raise ValueError(f"unsupported platform: {platform}")
    return ROOT / "resources" / "runtimes" / f"{platform}.h"


def runtime_contract(platform: str) -> str:
    """Return a self-contained snippet the model may copy into main.c."""
    return runtime_header_path(platform).read_text(encoding="utf-8")


def archetype_contract(archetype: str) -> dict[str, object]:
    data = yaml.safe_load((ROOT / "resources/archetypes.yml").read_text(encoding="utf-8"))
    try:
        return data["archetypes"][archetype]
    except KeyError as exc:
        raise ValueError(f"unsupported archetype: {archetype}") from exc


def generation_contract(platform: str, archetype: str) -> str:
    archetype_data = archetype_contract(archetype)
    primitives = ", ".join(archetype_data["required_primitives"])
    return (
        "--- VERIFIED RUNTIME CONTRACT ---\n"
        "Use these exact primitives when they apply. Because output is one main.c, "
        "copy only required static definitions; do not include llmz80 local headers.\n"
        f"Archetype loop: {archetype_data['loop']}\n"
        f"Required primitives: {primitives}\n"
        "```c\n"
        f"{runtime_contract(platform)}"
        "```\n"
    )
