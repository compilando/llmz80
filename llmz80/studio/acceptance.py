"""Acceptance criteria that are executed, and shown to whoever writes the code.

One definition serves three readers: a person reading prose, the runtime gate
executing the step, and a generator being told in advance exactly what its
program will be tested against. Handing the test over before the code is written
is deliberate; a generator that knows the check tends to satisfy it.
"""

from __future__ import annotations

from typing import Any

from llmz80.core.state_contract import STATE_PLAYING, contract_prompt

from .models import AcceptanceScenario, GameProject
from .solvability import sweep_plan

#: Frames to hold the action key before gameplay is expected to be running.
START_FRAMES = 30

#: Frames to hold a direction while sweeping for collectibles.
SWEEP_FRAMES = 60


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
                frames=SWEEP_FRAMES,
                expect={
                    "g_score": collected * project.gameplay.score_per_collectible,
                    "g_remaining": total - collected,
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


def generation_prompt(project: GameProject) -> str:
    """Everything a generator is owed before it writes the program."""
    parts = [contract_prompt(), scenarios_prompt(project)]
    return "\n\n".join(part for part in parts if part)
