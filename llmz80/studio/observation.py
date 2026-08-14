"""The steps the emulator drives so a program can be observed at all.

This is not the examiner and it must never become one. It states no
expectation about what the program should do: it holds each binding the design
declared, twice, then lets go, and the gates that read `step_readings` decide
what those readings mean. Keeping the two apart is what stops an
expectation-free script from being mistaken for a passed examination --
`acceptance.runtime_script` stays empty and `acceptance_report` keeps
abstaining, while `feel.animation_report` and `pacing.pacing_report` finally
get readings to judge.
"""

from __future__ import annotations

from typing import Any

from .models import GameProject, TargetPlatform

#: Design key label -> the name `emulator_smoke._SPECTRUM_ROWS` knows it by.
#: The four directions follow `codegen.KEY_CODES`: the 48K has no cursor keys,
#: and 5678 is what every game of the era used.
ZRCP_KEYS: dict[str, str] = {
    **{chr(code): chr(code).lower() for code in range(ord("A"), ord("Z") + 1)},
    **{str(digit): str(digit) for digit in range(10)},
    "SPACE": "space",
    "ENTER": "enter",
    "LEFT": "5",
    "DOWN": "6",
    "UP": "7",
    "RIGHT": "8",
}

#: Binding names that say the player is moving. A design coins its own binding
#: names (`jump`, `fire`, `pump`), so anything outside this set holds a key
#: that says nothing about movement -- which is what `feel._classify` calls
#: "action" and deliberately leaves out of its comparison.
DIRECTIONS = ("left", "right", "up", "down")

#: Frames each step holds its key. Fifty is one second at 50 Hz: long enough
#: that a program pacing itself on the frame clock has certainly moved.
STEP_FRAMES = 50


def observation_script(project: GameProject) -> list[dict[str, Any]]:
    """Hold each declared binding twice, then let go.

    Twice, because `feel.animation_report` compares consecutive readings and a
    single reading of a moving step can be compared against nothing. The
    trailing idle step is what lets it check the other half of its claim: that
    the animation frame holds still while the player does not move.

    Empty for any target the harness cannot drive. `_run_caprice32` ignores
    its `script` argument entirely, so a CPC script would promise readings
    that never arrive and make every gate look broken rather than absent.
    """
    if project.target.platform is not TargetPlatform.SPECTRUM:
        return []
    steps: list[dict[str, Any]] = []
    for name, label in project.controls.bindings.items():
        key = ZRCP_KEYS.get(label)
        if key is None:
            continue
        hold = name if name in DIRECTIONS else "action"
        for repeat in ("a", "b"):
            steps.append(
                {
                    "id": f"hold_{name}_{repeat}",
                    "hold": hold,
                    "key": key,
                    "frames": STEP_FRAMES,
                    "expect": {},
                }
            )
    if steps:
        steps.append(
            {"id": "idle", "hold": "none", "key": None, "frames": STEP_FRAMES, "expect": {}}
        )
    return steps
