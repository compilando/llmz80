"""The design, in the form whoever writes the program needs it.

What this module used to also do -- derive a runnable acceptance script from
the design -- assumed one kind of game: an actor stepping through a grid at a
fixed cadence, scoring one collectible at a time. That assumption is what made
any other kind of game fail verification, so it is gone. Deriving the script is
the examiner's job (phase 2), and until it exists `runtime_script` returns
nothing and the runtime gate abstains, exactly as it already abstains on a
target with no memory probe.
"""

from __future__ import annotations

from typing import Any

from llmz80.core.state_contract import contract_prompt

from .models import AssetSpec, GameProject
from .spriting import is_blitter_sprite


def blitter_sprites(project: GameProject) -> list[AssetSpec]:
    """Assets that `render_project` will really emit a SPRITE_<ID> for."""
    return [asset for asset in project.assets if is_blitter_sprite(asset)]


def runtime_script(project: GameProject) -> list[dict[str, Any]]:
    """No scripted steps yet: the examiner that derives them lands in phase 2.

    Returning an empty script makes the runtime gate abstain rather than pass:
    `services.acceptance_report` reports an unobserved gate, which is what an
    unexamined program honestly is.
    """
    return []


def design_prompt(project: GameProject) -> str:
    """The design itself, in the vocabulary the design coined for it."""
    lines = ["DESIGN", ""]
    if project.metadata.brief.strip():
        lines.extend(["What this game should be:", "", project.metadata.brief.strip(), ""])
    lines += [
        f"Title: {project.metadata.title}",
        f"Target: {project.target.platform.value}, {project.target.video_mode.value}, "
        f"{project.target.frame_hz} Hz",
        f"Presentation: {project.presentation.style}",
        "",
    ]
    if project.mechanics:
        lines.append("Mechanics this game must have:")
        lines.extend(f"  - {sentence}" for sentence in project.mechanics)
        lines.append("")

    lines.append("Controls. game_config.h defines one bit per binding:")
    for name, key in project.controls.bindings.items():
        lines.append(f"  INPUT_{name.upper():<12} key {key}")
    lines.append("")

    lines.append("Terrain characters, as they appear in the screens below:")
    for tile in project.tiles:
        traits = f" [{', '.join(tile.traits)}]" if tile.traits else ""
        lines.append(f"  '{tile.char}' is {tile.id}{traits}")
    lines.append("")

    lines.append("Actors:")
    for entity in project.entities:
        poses = f", poses {', '.join(entity.poses)}" if entity.poses else ""
        notes = f" -- {entity.notes}" if entity.notes else ""
        lines.append(f"  {entity.id}: {entity.kind} x{entity.count}{poses}{notes}")
    lines.append("")

    if project.observables:
        lines.append("Extra state this design exposes, declared in game_state.h:")
        for observable in project.observables:
            lines.append(f"  {observable.symbol}: {observable.meaning}")
        lines.append("")

    sprites = blitter_sprites(project)
    if sprites:
        lines.append(
            "Sprites: actors are drawn with plat_sprite(col, row, sprite, frame); "
            "terrain is drawn with plat_cell(col, row, character). Each sprite "
            "below is a SPRITE_<ID> constant and a frame count from sprites.h."
        )
        for asset in sprites:
            wearers = [entity.id for entity in project.entities if entity.sprite == asset.id]
            worn = f", worn by {', '.join(wearers)}" if wearers else ""
            lines.append(f"  {asset.id}: SPRITE_{asset.id.upper()}, {asset.frames} frames{worn}")
        lines.append("")

    if project.audio.effects:
        lines.append(
            "Sound effects, played with plat_sound(SOUND_<NAME>) from game_config.h: "
            + ", ".join(project.audio.effects)
        )
        lines.append("")

    lines.append(f"The game starts on screen {project.initial_screen}.")
    for screen in project.screens:
        limit = (
            f", time limit {screen.time_limit_seconds}s"
            if screen.time_limit_seconds is not None
            else ""
        )
        lines.extend(
            ["", f'Screen {screen.id} "{screen.name}", ' f"{screen.width}x{screen.height}{limit}"]
        )
        lines.extend(f"    {row}" for row in screen.tiles)
        if screen.spawns:
            lines.append("  Starting positions (column, row):")
            for spawn in screen.spawns:
                lines.append(f"    {spawn.entity} at ({spawn.col}, {spawn.row})")
        for direction, destination in screen.exits.items():
            lines.append(f"  Exit {direction} -> {destination}")

    lines.extend(
        [
            "",
            "Studio writes game_config.h with these constants, and game_state.h",
            "declaring the contract and this design's observables, into the same",
            "directory as your sources. A platform library is there too:",
            "platform.h documents what it offers. Use it or don't.",
        ]
    )
    return "\n".join(lines)


def generation_prompt(project: GameProject) -> str:
    """Everything a generator is owed before it writes the program."""
    return "\n\n".join([contract_prompt(), design_prompt(project)])
