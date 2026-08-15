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

    The one exception is a still frame across moving steps that all held the
    *same* direction. `hold` records which key the emulator pressed, not that
    the player moved, and a program that advances the frame only when the actor
    changed position -- which is what the contract asks for -- reports the same
    value twice as soon as the arena clamps it against a wall. That reading
    cannot be told apart from a program that never animates, so it abstains
    instead of blaming one of them. The "holds still while idle" half keeps its
    hard failure: an idle step holds no key at all, which *is* evidence the
    player did not move, so there the gate is judging what it actually saw.

    The straddle test -- two consecutive moving readings whose directions
    differ -- is a heuristic, not a proof. A design binding only `left` and
    `up` with the player starting in the top-left corner straddles on every
    pair and still never moves, and would be failed for a clamp. The error only
    ever runs that way: a straddle can be missing when movement happened
    (costing a verdict) but the gate never invents a failure for a pair that
    held one direction throughout. Stating the claim exactly would need the
    state contract to expose the player's position, which is a contract change,
    a writer-prompt change and a regeneration of every program.
    """
    entries: list[tuple[Any, int, str, Any]] = []
    for reading in runtime.get("step_readings") or []:
        read = reading.get("read") or {}
        if _SYMBOL not in read:
            continue
        hold = reading.get("hold")
        state = _classify(hold)
        if state is None:
            continue
        # `hold` is carried alongside the classification, not folded into it:
        # deciding whether a *pair* of moving steps can support a definite
        # failure needs to know whether the two held the same direction.
        entries.append((reading.get("id"), read[_SYMBOL], state, hold))

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
    straddling_ids: list[str] = []
    idle_held: list[bool] = []
    idle_ids: list[str] = []
    for (_prev_id, prev_value, prev_state, prev_hold), (
        curr_id,
        curr_value,
        curr_state,
        curr_hold,
    ) in zip(entries, entries[1:]):
        if curr_state == "idle":
            idle_ids.append(str(curr_id))
            idle_held.append(prev_value == curr_value)
        else:
            moving_ids.append(str(curr_id))
            moving_changed.append(prev_value != curr_value)
            if prev_state == "moving" and prev_hold != curr_hold:
                straddling_ids.append(str(curr_id))

    failures: list[str] = []
    unclear: str | None = None
    if not moving_changed:
        failures.append(
            f"{_SYMBOL} was read at fewer than two consecutive moving steps; "
            "whether it advances while the player moves cannot be confirmed"
        )
    elif not any(moving_changed):
        if straddling_ids:
            failures.append(
                f"{_SYMBOL} never advanced across the moving steps ({', '.join(moving_ids)})"
            )
        else:
            unclear = (
                f"{_SYMBOL} never advanced across the moving steps "
                f"({', '.join(moving_ids)}), but no two consecutive ones held "
                "different directions; a program that animates only when the "
                "actor moves reads the same value twice once the arena has "
                "clamped it against a wall, so a still animation cannot be "
                "told apart from a clamped player here"
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

    readings = [
        {"id": step_id, "read": value, "state": state} for step_id, value, state, _hold in entries
    ]
    if unclear and not failures:
        # Abstaining rather than passing, for the same reason as the branch
        # above: evidence this gate cannot read is not evidence in the
        # program's favour. A definite failure elsewhere in the run still wins,
        # which is why this is checked after `failures`.
        return {
            "schema_version": 1,
            "observed": False,
            "reason": unclear,
            "readings": readings,
            "failures": [],
            "quality_pass": None,
        }

    return {
        "schema_version": 1,
        "observed": True,
        "readings": readings,
        "failures": failures,
        "quality_pass": not failures,
    }
