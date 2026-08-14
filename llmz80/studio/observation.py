"""The steps the emulator drives so a program can be observed at all.

This is not the examiner and it must never become one. It states no
expectation about what the program should do: it holds each binding the design
declared, twice, then lets go, and the gates that read `step_readings` decide
what those readings mean. Keeping the two apart is what stops an
expectation-free script from being mistaken for a passed examination --
`acceptance.runtime_script` stays empty and `acceptance_report` keeps
abstaining, while `feel.animation_report` finally gets readings to judge (and
the pacing gate will too, once it exists).
"""

from __future__ import annotations

from typing import Any

from .models import HOLD_ACTION, HOLD_DIRECTIONS, HOLD_NONE, GameProject, TargetPlatform

#: Design key label -> the name `emulator_smoke._SPECTRUM_ROWS` knows it by,
#: which is a 48K keyboard matrix position rather than anything about the
#: remote protocol. The four directions follow `codegen.KEY_CODES`: the 48K
#: has no cursor keys, and 5678 is what every game of the era used.
#:
#: This states the same fact as `codegen.KEY_CODES[SPECTRUM]` from the other
#: side -- that one decides which key the *program reads*, this one which key
#: the *emulator presses* -- so the two must agree exactly or every moving
#: step presses a key the program ignores and the animation gate reports a
#: failure for a correct program. `test_studio_observation` pins the
#: equivalence across every label in `KEY_LABELS`. Written out rather than
#: derived from the C macro names, because string surgery on those would only
#: trade a loud, tested duplication for a silent, untested one.
SPECTRUM_KEYS: dict[str, str] = {
    **{chr(code): chr(code).lower() for code in range(ord("A"), ord("Z") + 1)},
    **{str(digit): str(digit) for digit in range(10)},
    "SPACE": "space",
    "ENTER": "enter",
    "LEFT": "5",
    "DOWN": "6",
    "UP": "7",
    "RIGHT": "8",
}

#: Frames each step holds its key. Fifty is one second at 50 Hz: long enough
#: that a program pacing itself on the frame clock has certainly moved.
STEP_FRAMES = 50


def observation_script(project: GameProject) -> list[dict[str, Any]]:
    """Hold each declared binding twice, then let go.

    Twice, because `feel.animation_report` compares consecutive readings and a
    single reading of a moving step can be compared against nothing. The
    trailing idle step is what lets it check the other half of its claim: that
    the animation frame holds still while the player does not move.

    The two holds of a direction are not adjacent: the script sweeps every
    direction once, then sweeps them all again. Grouping them -- `left_a`,
    `left_b`, `right_a`, ... -- is what the first real emulator run showed to
    be worthless. A second helping of the same direction finds the player
    pinned against the wall the first one drove it into, so a program that
    animates only while the actor moves reports the same frame twice, and all
    four pairs of the sample bindings contributed nothing at all; the run
    passed on the three transitions *between* direction groups, which no test
    covered and no comment claimed. Interleaved, every adjacent moving pair
    changes direction, which is both what gives the player somewhere to move
    and the straddle `feel.animation_report` requires before it will call a
    still frame a failure.

    Action bindings go first and directions last, so the idle step is
    *temporally* adjacent to the moving reading it will be compared against.
    The gate drops the action steps from its comparison but the emulator still
    spent their two seconds holding a key: with the directions first, a
    program that animates while the action key is held -- a jump, a fire
    animation, SPACE leaving a title screen -- moved its animation frame
    between the last direction reading and the idle one, and was failed with
    `g_anim_frame changed while idle`. That is a complaint no writer can
    satisfy, and `generator.py` feeds it to `repair_prompt` and burns an
    attempt on it.

    Empty for any target the harness cannot drive. `_run_caprice32` ignores
    its `script` argument entirely, so a CPC script would promise readings
    that never arrive and make every gate look broken rather than absent.
    Empty, too, when no binding is named for a direction: `hold` comes from
    the name the *design* coined, and a design that calls them `izquierda` and
    `saltar` -- the default project language is Spanish -- yields only action
    steps. Handing those to the gate makes it report `observed: True` and a
    definite failure for a program it never actually watched move. A script
    that can tell the gate nothing must let it abstain honestly instead.
    """
    if project.target.platform is not TargetPlatform.SPECTRUM:
        return []
    bindings = project.controls.bindings.items()
    # The design's own declaration order survives within each group; only the
    # action-before-direction split is imposed.
    actions = [item for item in bindings if item[0] not in HOLD_DIRECTIONS]
    directions = [item for item in bindings if item[0] in HOLD_DIRECTIONS]
    if not directions:
        return []

    def _hold(name: str, label: str, repeat: str) -> dict[str, Any]:
        return {
            "id": f"hold_{name}_{repeat}",
            # Indexed, not `.get`: `KEY_LABELS` is a source constant that
            # `ControlsSpec` validates every binding against, so a label
            # missing here is a developer error and should be loud rather than
            # silently dropping the binding from the script.
            "key": SPECTRUM_KEYS[label],
            "hold": name if name in HOLD_DIRECTIONS else HOLD_ACTION,
            "frames": STEP_FRAMES,
            "expect": {},
        }

    # Actions stay grouped at the front rather than joining the sweep: the gate
    # drops them, but the emulator still spends their seconds holding a key, and
    # one landing between two direction readings would let a program that
    # animates on the fire key supply a change the moving pair did not earn.
    steps: list[dict[str, Any]] = [
        _hold(name, label, repeat) for repeat in ("a", "b") for name, label in actions
    ]
    steps += [_hold(name, label, repeat) for repeat in ("a", "b") for name, label in directions]
    steps.append(
        {"id": "idle", "hold": HOLD_NONE, "key": None, "frames": STEP_FRAMES, "expect": {}}
    )
    return steps
