"""Acceptance criteria that are executed, and shown to whoever writes the code.

One definition serves three readers: a person reading prose, the runtime gate
executing the step, and a generator being told in advance exactly what its
program will be tested against. Handing the test over before the code is written
is deliberate; a generator that knows the check tends to satisfy it.
"""

from __future__ import annotations

from typing import Any

from llmz80.core.state_contract import STATE_PLAYING, contract_prompt

from .models import AcceptanceScenario, AssetSpec, GameProject
from .solvability import sweep_plan
from .spriting import is_blitter_sprite

#: Frames to hold the action key before gameplay is expected to be running.
START_FRAMES = 30

#: Display frames an actor of speed 1 takes to advance one cell. Speed 4 moves
#: every frame. This is the design's meaning of "speed" and the program is told
#: it, because an acceptance step that counts collected items is only decidable
#: if how fast the player travels is agreed in advance.
FRAMES_PER_CELL = (4, 3, 2, 1)

#: Extra frames allowed on top of the exact travel time, absorbing a program's
#: start-up and any rounding in its own pacing.
SWEEP_MARGIN_FRAMES = 25


def frames_per_cell(speed: int) -> int:
    return FRAMES_PER_CELL[min(max(speed, 1), 4) - 1]


def sweep_frames(project: GameProject, plan: dict) -> int:
    """Frames to hold a direction so the planned collectibles are reachable."""
    player = next(
        (entity for entity in project.entities if entity.role == "player"), None
    )
    speed = player.speed if player else 1
    distance = int(plan.get("distance") or 0)
    return min(1000, distance * frames_per_cell(speed) + SWEEP_MARGIN_FRAMES)


def derive_scenarios(project: GameProject) -> list[AcceptanceScenario]:
    """Fill in the runnable half of the design's acceptance criteria.

    Only criteria the design can predict exactly become executable. Losing a
    life to an enemy stays prose, because reaching an enemy depends on where it
    has patrolled to, and a check that is only usually true is worse than none.
    """
    total = sum(entity.count for entity in project.entities if entity.role == "collectible")
    plan = sweep_plan(project, 0)
    scenarios: list[AcceptanceScenario] = []
    for scenario in project.acceptance:
        document = scenario.model_dump(mode="json")
        if scenario.id == "start_game":
            document.update(
                hold="action",
                frames=START_FRAMES,
                expect={"g_state": STATE_PLAYING, "g_level": 1, "g_score": 0},
            )
        elif scenario.id == "collect_scores" and plan.get("collected"):
            collected = plan["collected"]
            document.update(
                hold=plan["direction"],
                frames=sweep_frames(project, plan),
                expect={
                    "g_score": collected * project.gameplay.score_per_collectible,
                    "g_remaining": total - collected,
                    # Scoring while dying is not playing. A design that kills the
                    # player during its own opening move has to fail here, or the
                    # only gate that notices is a coarser one further on.
                    "g_state": STATE_PLAYING,
                    "g_lives": project.gameplay.lives,
                },
            )
        scenarios.append(AcceptanceScenario.model_validate(document))
    return scenarios


def with_executable_scenarios(project: GameProject) -> GameProject:
    document = project.model_dump(mode="json")
    document["acceptance"] = [
        scenario.model_dump(mode="json") for scenario in derive_scenarios(project)
    ]
    return GameProject.model_validate(document)


def runtime_script(project: GameProject) -> list[dict[str, Any]]:
    """Ordered steps for the emulator: hold an input, then read the contract.

    Steps run in one boot and accumulate, which is why order matters: the game
    has to be started before anything can be collected.
    """
    steps: list[dict[str, Any]] = []
    for scenario in project.acceptance:
        if not scenario.executable:
            continue
        steps.append(
            {
                "id": scenario.id,
                "hold": scenario.hold,
                "frames": scenario.frames,
                "expect": dict(scenario.expect),
            }
        )
    return steps


def scenarios_prompt(project: GameProject) -> str:
    """The acceptance half of a generation prompt."""
    steps = runtime_script(project)
    if not steps:
        return ""
    lines = [
        "RUNTIME ACCEPTANCE",
        "",
        "After the program loads, an emulator holds each input below for the",
        "stated number of 50 Hz frames, in this order and without resetting",
        "between steps. It then reads the state contract from memory. Every",
        "expected value must match exactly.",
        "",
    ]
    for index, step in enumerate(steps, start=1):
        expectations = ", ".join(
            f"{name} == {value}" for name, value in sorted(step["expect"].items())
        )
        lines.append(
            f"  {index}. hold {step['hold']} for {step['frames']} frames -> {expectations}"
        )
    lines.append("")
    lines.append(
        "The controls are: "
        + ", ".join(
            f"{name} = {getattr(project.controls, name)}"
            for name in ("left", "right", "up", "down", "action")
        )
        + "."
    )
    return "\n".join(lines)


def blitter_sprites(project: GameProject) -> list[AssetSpec]:
    """Assets that `render_project` (see `compiler.py`) actually packs into
    `sprites.h` as a `SPRITE_<ID>`.

    Telling the writer about a constant that will not exist would be a wrong
    prompt, so this calls the exact same rule `render_project` packs against --
    `spriting.is_blitter_sprite` -- rather than keeping a second copy of it
    here that could silently drift from the compiler's.
    """
    return [asset for asset in project.assets if is_blitter_sprite(asset)]


def design_prompt(project: GameProject) -> str:
    """The design itself, in the form a program author needs it.

    Levels are shown as the same grid the designer edited rather than as a byte
    table, because the author has to reason about the shape before choosing how
    to store it.
    """
    lines = ["DESIGN", ""]
    if project.metadata.brief.strip():
        # The designer's own words come first: the structured fields below say
        # what the game is made of, but only this says what it should be like.
        lines.extend(
            ["What this game should be:", "", project.metadata.brief.strip(), ""]
        )
    lines += [
        f"Title: {project.metadata.title}",
        f"Target: {project.target.platform.value}, {project.target.video_mode.value}, "
        f"{project.target.frame_hz} Hz",
        f"Genre: {project.genre}",
        f"Presentation: {project.presentation.style}",
        f"Lives: {project.gameplay.lives}    "
        f"Points per collectible: {project.gameplay.score_per_collectible}    "
        f"Levels: {project.gameplay.level_count}",
        f"Difficulty curve: {project.gameplay.difficulty_curve}",
        "",
        "Entities:",
    ]
    for entity in project.entities:
        behaviour = "" if entity.behaviour == "auto" else f", moves {entity.behaviour}"
        pace = frames_per_cell(entity.speed)
        lines.append(
            f"  {entity.id}: {entity.role} x{entity.count}, speed {entity.speed} "
            f"(one cell every {pace} frame{'s' if pace != 1 else ''}){behaviour}"
        )
    lines.append("")
    lines.append(
        "Speed is a pace, not a distance: an actor of speed 1 advances one cell "
        "every 4 frames, speed 2 every 3, speed 3 every 2, and speed 4 every "
        "frame. The runtime acceptance below times its inputs by this rule, so a "
        "program that moves faster or slower than its design says will fail it."
    )
    sprites = blitter_sprites(project)
    if sprites:
        lines.append("")
        lines.append(
            "Sprites: actors are drawn with plat_sprite(col, row, sprite, frame); "
            "terrain cells are drawn with plat_cell. Each sprite below is a "
            "SPRITE_<ID> constant and a frame count from sprites.h."
        )
        for asset in sprites:
            identifier = f"SPRITE_{asset.id.upper()}"
            frame_word = "frame" if asset.frames == 1 else "frames"
            wearers = [entity.id for entity in project.entities if entity.sprite == asset.id]
            worn_by = f", worn by {', '.join(wearers)}" if wearers else ""
            lines.append(f"  {asset.id}: {identifier}, {asset.frames} {frame_word}{worn_by}")

    if project.audio.effects:
        lines.append("")
        lines.append("Sound effects to play: " + ", ".join(project.audio.effects))

    for level in project.levels:
        limit = (
            f", time limit {level.time_limit_seconds}s"
            if level.time_limit_seconds is not None
            else ""
        )
        lines.extend(
            [
                "",
                f"Level {level.id} \"{level.name}\", {level.width}x{level.height}{limit}",
                "  '#' is wall, '.' is floor:",
            ]
        )
        lines.extend(f"    {row}" for row in level.tiles)
        lines.append("  Starting positions (column, row):")
        for spawn in level.spawns:
            lines.append(f"    {spawn.entity} at ({spawn.col}, {spawn.row})")

    lines.extend(
        [
            "",
            "Studio writes game_config.h with these values as constants, and",
            "game_state.h declaring the contract, into the same directory as your",
            "sources. A platform library is there too: platform.h documents what",
            "it offers. Use it or don't.",
        ]
    )
    return "\n".join(lines)


def generation_prompt(project: GameProject) -> str:
    """Everything a generator is owed before it writes the program."""
    parts = [contract_prompt(), design_prompt(project), scenarios_prompt(project)]
    return "\n\n".join(part for part in parts if part)
