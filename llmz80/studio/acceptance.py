"""The design, in the form whoever writes the program needs it.

What this module used to also do -- derive a runnable acceptance script from
the design -- assumed one kind of game: an actor stepping through a grid at a
fixed cadence, scoring one collectible at a time. That assumption is what made
any other kind of game fail verification, so it is gone. Deriving the script is
the examiner's job (phase 2), and until it exists `runtime_script` returns
nothing and `services.acceptance_report` abstains, exactly as it already
abstains on a target with no memory probe.
"""

from __future__ import annotations

from typing import Any

from llmz80.core.state_contract import contract_prompt

from .models import AssetSpec, GameProject
from .spriting import is_blitter_sprite


def blitter_sprites(project: GameProject) -> list[AssetSpec]:
    """Assets that `render_project` will really emit a SPRITE_<ID> for.

    Filtered through `is_blitter_sprite`, not just `asset.kind == "sprite"`:
    an asset shaped wrong for the blitter (not 16x16 per frame) still falls
    back to a plain `assets.c` import with no `SPRITE_<ID>` constant, and
    promising one here that `compiler.render_project` never defines is a
    prompt that lies to the writer -- it finds out three files and one
    compiler error later. See `is_blitter_sprite`'s own docstring for why
    that filter lives in `spriting.py` rather than being duplicated here.
    """
    return [asset for asset in project.assets if is_blitter_sprite(asset)]


def runtime_script(project: GameProject) -> list[dict[str, Any]]:
    """No scripted steps yet: the examiner that derives them lands in phase 2.

    Returning an empty script makes `services.acceptance_report` abstain
    rather than pass -- an unobserved gate, which is what an unexamined
    program honestly is. `probe_report`, the other gate on the same path,
    does not read this function and does not abstain; fixing that is a
    separate, already-tracked task, not this one.

    `project` is unused today -- the examiner that replaces this body will
    need it to derive a script from, and `services.py` already calls this as
    `runtime_script(project)`, so the parameter stays rather than being
    dropped and re-added once phase 2 lands.
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
    else:
        # A design is free to declare no rules at all, but silence here must
        # not read as permission to invent a win/lose condition to fit the
        # brief's mood -- that is exactly the kind of guess phase 2's
        # examiner cannot verify. Wording softens when a brief exists (it
        # sets atmosphere, not rules -- "an explorer crosses stone rooms"
        # still does not say how the game is won) but the instruction is
        # never dropped, only its tone.
        if project.metadata.brief.strip():
            lines.append(
                "This design states no mechanics beyond the brief above, and a brief "
                "sets mood, not rules -- it does not say how the game is won or lost. "
                "Implement only what is declared elsewhere below (terrain, actors, "
                "controls, screens, scenes); do not invent a win or lose condition to "
                "match the brief silently. Leave a comment in the code naming any rule "
                "you had to assume."
            )
        else:
            lines.append(
                "This design declares no mechanics at all. Implement only what is "
                "declared below (terrain, actors, controls, screens, scenes) and do "
                "not invent a win or lose condition silently. Leave a comment in the "
                "code naming any rule you had to assume to make the game playable."
            )
        lines.append("")

    lines.append("Controls. game_config.h defines one bit per binding:")
    for name, key in project.controls.bindings.items():
        lines.append(f"  INPUT_{name.upper():<12} key {key}")
    lines.append("")

    # Drawing terrain is unconditional -- every design has at least one tile
    # (TileSpec has min_length=1) -- so this instruction must not live inside
    # the `if sprites` branch below, the way the sprite-only half of drawing
    # does. A design with no sprites (the common case: a new project starts
    # with none) still needs to be told how its screen gets drawn at all.
    lines.append(
        "Terrain characters, as they appear in the screens below. Draw one with "
        "plat_cell(col, row, character):"
    )
    for tile in project.tiles:
        traits = f" [{', '.join(tile.traits)}]" if tile.traits else ""
        lines.append(f"  '{tile.char}' is {tile.id}{traits}")
    lines.append("")

    # "Actors" would presuppose every entity plays that role; `kind` is free
    # vocabulary a design coins for itself (a door, a switch, a collectible),
    # so the heading stays neutral about what any of them do.
    lines.append("Things in this game:")
    for entity in project.entities:
        # `count` is `structure.py`'s per-screen spawn budget, not "there are
        # this many" -- rendering it as "x3" reads as the latter, so it is
        # shown as an explicit cap, and only when it says anything a reader
        # couldn't assume (a count of 1 is the default and needs no caveat).
        cap = f", at most {entity.count} per screen" if entity.count > 1 else ""
        poses = f", poses {', '.join(entity.poses)}" if entity.poses else ""
        notes = f" -- {entity.notes}" if entity.notes else ""
        lines.append(f"  {entity.id}: {entity.kind}{cap}{poses}{notes}")
    lines.append("")

    if project.observables:
        lines.append("Extra state this design exposes, declared in game_state.h:")
        for observable in project.observables:
            lines.append(f"  {observable.symbol}: {observable.meaning}")
        lines.append("")

    # blitter_sprites(), not project.assets: only what it returns gets a real
    # SPRITE_<ID> constant in sprites.h (see its own docstring), so advertising
    # anything wider here would promise a constant the header never defines.
    sprites = blitter_sprites(project)
    if sprites:
        lines.append(
            "Sprites: draw one with plat_sprite(col, row, sprite, frame). This is not "
            "optional once a design has sprites: a program that packs sprites below but "
            "never calls plat_sprite fails verification (see compiler.py's "
            "check for it). Each sprite below is a SPRITE_<ID> constant and a frame "
            "count from sprites.h."
        )
        for asset in sprites:
            wearers = [entity.id for entity in project.entities if entity.sprite == asset.id]
            worn = f", worn by {', '.join(wearers)}" if wearers else ""
            frame_word = "frame" if asset.frames == 1 else "frames"
            lines.append(
                f"  {asset.id}: SPRITE_{asset.id.upper()}, {asset.frames} {frame_word}{worn}"
            )
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

    # Presentation flow is a separate graph from the screens above: every
    # design has at least two scenes (SceneSpec has min_length=2), and
    # contract_prompt() below already hands the writer four g_state values
    # (title/playing/game over/victory) to keep accurate -- without this
    # block nothing ever told it which scene is which or how they connect.
    lines.extend(["", f"Scenes: presentation flow, starting at {project.initial_scene}."])
    for scene in project.scenes:
        title = f' "{scene.title}"' if scene.title else ""
        lines.append(f"  {scene.id} ({scene.kind}){title}")
        if scene.next_scene:
            lines.append(f"    -> {scene.next_scene}")
        for option in scene.options:
            lines.append(f'    "{option.label}" -> {option.target_scene}')

    # This paragraph is written before the writer has seen platform.h itself:
    # `generator.writing_prompt` appends this design prompt first and
    # `library_interface()` -- the actual header text -- later in the same
    # message. It orients the writer to what is coming, it does not repeat it.
    lines.extend(
        [
            "",
            "Studio writes game_config.h with these constants, and game_state.h",
            "declaring the contract and this design's observables, into the same",
            "directory as your sources. A platform library is there too:",
            "platform.h documents what it offers.",
        ]
    )
    if sprites:
        lines.append(
            "Use as much of it as helps, except plat_sprite: this design's sprites "
            "make it mandatory, not optional (see above)."
        )
    else:
        lines.append("Use it or don't.")
    return "\n".join(lines)


def generation_prompt(project: GameProject) -> str:
    """Everything a generator is owed before it writes the program."""
    return "\n\n".join([contract_prompt(), design_prompt(project)])
