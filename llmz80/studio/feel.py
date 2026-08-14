"""Judging animation from what memory showed between steps.

The state contract (`llmz80.core.state_contract`) declares `g_anim_frame` as
optional, with a meaning stated in prose: "the animation frame the player is
currently drawn with; it must advance while the player moves and hold still
while it does not". `AcceptanceScenario.expect` cannot express that -- it is
exact equality against one value, and this claim is about a value moving
between two points and staying put at a third. So this gate does not extend
that schema; it reads the emulator's own record of what happened at each
scripted step (`step_readings`, built in
`llmz80.quality.emulator_smoke._run_zesarux`) and compares consecutive
readings directly.

Each `step_readings` entry carries the scripted step's own `hold` alongside
its id and reading -- see the line that builds them,
`reading: dict[str, Any] = {"id": step.get("id"), "hold": step.get("hold"),
"read": {}}`. `hold` is the literal "none" for a step that touches no key, or
one of the four movement directions for a step that does (the vocabulary
is `HOLD_NONE`, `HOLD_ACTION` and `HOLD_DIRECTIONS` in
`llmz80.studio.models`, which `llmz80.studio.observation` writes and this
module reads); a fifth value, "action", holds the start/fire key and says
nothing about whether the player is moving. So this
module classifies straight from that fact rather than from any naming
convention on the id: "none" is idle, a direction is movement, and "action"
(or an absent `hold`) is neither and is left out of the comparison.
"""

from __future__ import annotations

from typing import Any

from .models import HOLD_DIRECTIONS, HOLD_NONE

#: The one state-contract symbol this gate is about.
_SYMBOL = "g_anim_frame"


def _classify(hold: Any) -> str | None:
    """Movement state a scripted `hold` implies, or None when it says nothing.

    "action" presses the start/fire key and does not say whether the player
    sprite is moving, so it is left unclassified rather than guessed at. A
    missing `hold` -- what every `step_readings` entry looked like before this
    field was threaded through -- is unclassified for the same reason: no
    information beats a guess.
    """
    if hold == HOLD_NONE:
        return "idle"
    if hold in HOLD_DIRECTIONS:
        return "moving"
    return None


def animation_report(runtime: dict[str, Any]) -> dict[str, Any]:
    """Judge `g_anim_frame` against its declared meaning.

    Abstaining is not passing: when no step yields both a reading of the
    symbol and a `hold` that classifies as moving or idle, this returns
    `observed: False` and `quality_pass: None`, exactly as `probe_report` and
    `acceptance_report` do when a target has no memory probe adapter -- a
    target that never reports usable evidence must not inherit a pass it
    never earned. This is also what happens to a report written before
    `hold` reached `step_readings`: every entry is unclassifiable, so it reads
    exactly like a target that reported nothing.

    Once at least one classified reading exists, the verdict is a definite
    True or False: partial evidence (no idle step in the run, or only one
    moving reading) is reported as a failure with a reason, not as a second
    kind of abstention, so a script that omits the checks this gate needs
    does not silently let a broken animation through.
    """
    entries: list[tuple[Any, int, str]] = []
    for reading in runtime.get("step_readings") or []:
        read = reading.get("read") or {}
        if _SYMBOL not in read:
            continue
        state = _classify(reading.get("hold"))
        if state is None:
            continue
        entries.append((reading.get("id"), read[_SYMBOL], state))

    if not entries:
        return {
            "schema_version": 1,
            "observed": False,
            "reason": f"no step yielded both a reading of {_SYMBOL} and a hold "
            "that classifies as moving or idle; this target has no memory "
            "probe adapter, the program never declared the symbol, or the "
            "steps never reached this gate with their hold intact",
            "failures": [],
            "quality_pass": None,
        }

    # A wrapping counter (an unsigned char cycling 3, 0, 1, ...) is still
    # advancing at every step, so "advanced" only ever means "differs from
    # the previous reading" -- never a numeric increase.
    moving_changed: list[bool] = []
    moving_ids: list[str] = []
    idle_held: list[bool] = []
    idle_ids: list[str] = []
    for (_prev_id, prev_value, _prev_state), (curr_id, curr_value, curr_state) in zip(
        entries, entries[1:]
    ):
        if curr_state == "idle":
            idle_ids.append(str(curr_id))
            idle_held.append(prev_value == curr_value)
        else:
            moving_ids.append(str(curr_id))
            moving_changed.append(prev_value != curr_value)

    failures: list[str] = []
    if not moving_changed:
        failures.append(
            f"{_SYMBOL} was read at fewer than two consecutive moving steps; "
            "whether it advances while the player moves cannot be confirmed"
        )
    elif not any(moving_changed):
        failures.append(
            f"{_SYMBOL} never advanced across the moving steps "
            f"({', '.join(moving_ids)})"
        )

    if not idle_held:
        failures.append(
            f"no idle step reported {_SYMBOL} in this run; whether it holds still "
            "while the player does not move cannot be confirmed"
        )
    else:
        broken = [step_id for step_id, held in zip(idle_ids, idle_held) if not held]
        if broken:
            failures.append(
                f"{_SYMBOL} changed while idle at step(s) {', '.join(broken)}"
            )

    return {
        "schema_version": 1,
        "observed": True,
        "readings": [
            {"id": step_id, "read": value, "state": state} for step_id, value, state in entries
        ],
        "failures": failures,
        "quality_pass": not failures,
    }
