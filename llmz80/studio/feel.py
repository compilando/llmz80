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

`step_readings` entries carry only an id and a reading -- see the line that
builds them, `reading: dict[str, Any] = {"id": step.get("id"), "read": {}}`.
The scripted step's own `hold` (a direction, or the literal "none" for a step
that touches no key) never reaches that structure, so this module cannot read
it. Instead it reads the id: a step whose id names it as idle (contains the
substring "idle") is treated as a hold of "none"; every other step that
carries a reading of the symbol is treated as movement. This is a naming
convention for whoever builds the script handed to this gate, not a property
of `step_readings` itself.
"""

from __future__ import annotations

from typing import Any

#: The one state-contract symbol this gate is about.
_SYMBOL = "g_anim_frame"


def _is_idle_step(step_id: Any) -> bool:
    return "idle" in str(step_id or "").lower()


def animation_report(runtime: dict[str, Any]) -> dict[str, Any]:
    """Judge `g_anim_frame` against its declared meaning.

    Abstaining is not passing: when no step ever reported the symbol, this
    returns `observed: False` and `quality_pass: None`, exactly as
    `probe_report` and `acceptance_report` do when a target has no memory
    probe adapter -- a target that never reports the symbol must not inherit
    a pass it never earned. Once at least one reading exists, the verdict is
    a definite True or False: partial evidence (no idle step in the run, or
    only one moving reading) is reported as a failure with a reason, not as
    a second kind of abstention, so a script that omits the checks this gate
    needs does not silently let a broken animation through.
    """
    entries: list[tuple[Any, int, bool]] = []
    for reading in runtime.get("step_readings") or []:
        read = reading.get("read") or {}
        if _SYMBOL not in read:
            continue
        entries.append((reading.get("id"), read[_SYMBOL], _is_idle_step(reading.get("id"))))

    if not entries:
        return {
            "schema_version": 1,
            "observed": False,
            "reason": f"no step reported {_SYMBOL}; this target has no memory probe "
            "adapter or the program never declared the symbol",
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
    for (_prev_id, prev_value, _prev_idle), (curr_id, curr_value, curr_idle) in zip(
        entries, entries[1:]
    ):
        if curr_idle:
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
            {"id": step_id, "read": value, "idle": idle} for step_id, value, idle in entries
        ],
        "failures": failures,
        "quality_pass": not failures,
    }
