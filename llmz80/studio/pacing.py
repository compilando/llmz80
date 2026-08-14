"""Judging frame pacing from what memory showed between steps.

This is the one performance claim that can be made about any design at all,
which is why it survives where the v3 gates did not: solvability and
difficulty assumed a kind of game, and "the loop fitted inside its frame"
assumes only that there is a loop and a frame.

Nothing here counts a T-state. `plat_wait_frame` already measures the cost in
the currency that matters -- whole display frames the previous iteration
overran by -- and the program keeps the worst it ever saw in
`g_worst_frame_cost`, which the linker map locates and ZRCP reads. Profiling
T-states would need an instrumented emulator and would answer a question
nobody asked.
"""

from __future__ import annotations

from typing import Any

from .models import TargetPlatform

#: The one state-contract symbol this gate is about.
_SYMBOL = "g_worst_frame_cost"

#: Targets whose `plat_wait_frame` actually counts the frames the previous
#: iteration cost. `resources/studio_lib/spectrum/platform.c` reads the ROM
#: frame counter and returns the elapsed count less the one frame the wait
#: itself is worth; `resources/studio_lib/cpc/platform.c` calls
#: `cpct_waitVSYNC()` and returns a literal zero, because with the firmware
#: disabled the CPC has no free-running counter to subtract. This mirrors the
#: `HAS_FRAME_CLOCK` define that `codegen.render_config_header` writes into
#: game_config.h -- the same fact, told to the gate instead of to the C.
_FRAME_CLOCK_PLATFORMS = frozenset({TargetPlatform.SPECTRUM.value})

#: Missed frames tolerated. One absorbs the cost of the first fully drawn
#: frame and of the step where the harness writes its input; two or more is a
#: game loop that does not fit inside its frame and will read as juddering.
MAX_MISSED_FRAMES = 1


def pacing_report(runtime: dict[str, Any]) -> dict[str, Any]:
    """Judge the worst frame overrun the program admitted to.

    Abstaining is not passing, exactly as in `feel.animation_report`: a run
    where no step ever reported the symbol returns `quality_pass: None`.

    The frame clock is checked before the readings are, and it is the reason
    this gate is not simply a comparison against a ceiling. A CPC program
    reports `g_worst_frame_cost` as zero however badly it ran, because its
    `plat_wait_frame` never measured anything; taking that zero for a pass
    would clear the entire platform on the strength of a number nobody
    computed, which is the precise failure this floor exists to eliminate. So
    a target with no frame clock abstains, and an unrecognised platform
    abstains with it -- a target this module has never heard of has not shown
    it can count frames either. Writing a frame counter for the CPC is real
    work; until it exists, silence is the honest reading.
    """
    platform = runtime.get("platform")
    if platform not in _FRAME_CLOCK_PLATFORMS:
        return {
            "schema_version": 1,
            "observed": False,
            "reason": f"target {platform!r} has no free-running frame clock, so its "
            f"plat_wait_frame returns zero without measuring anything and {_SYMBOL} "
            "says nothing about how the loop actually ran",
            "worst": None,
            "failures": [],
            "quality_pass": None,
        }
    readings = [
        (reading.get("id"), (reading.get("read") or {})[_SYMBOL])
        for reading in runtime.get("step_readings") or []
        if _SYMBOL in (reading.get("read") or {})
    ]
    if not readings:
        return {
            "schema_version": 1,
            "observed": False,
            "reason": f"no step reported {_SYMBOL}; this target has no memory probe "
            "adapter, or the program never declared the symbol",
            "worst": None,
            "failures": [],
            "quality_pass": None,
        }
    worst_id, worst = max(readings, key=lambda item: item[1])
    failures: list[str] = []
    if worst > MAX_MISSED_FRAMES:
        failures.append(
            f"{_SYMBOL} reached {worst} at step {worst_id}: one iteration of the "
            f"game loop overran its display frame by {worst} frames, and at most "
            f"{MAX_MISSED_FRAMES} is accepted. Redraw only what changed, and move "
            "work that does not need to happen every frame out of the loop."
        )
    return {
        "schema_version": 1,
        "observed": True,
        "readings": [{"id": step_id, "read": value} for step_id, value in readings],
        "worst": worst,
        "failures": failures,
        "quality_pass": not failures,
    }
