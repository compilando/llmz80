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

from .codegen import has_frame_clock

#: The one state-contract symbol this gate is about.
_SYMBOL = "g_worst_frame_cost"

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
    if not has_frame_clock(platform):
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
        failures.append(_diagnosis(readings, worst_id, worst))
    return {
        "schema_version": 1,
        "observed": True,
        "readings": [{"id": step_id, "read": value} for step_id, value in readings],
        "worst": worst,
        "failures": failures,
        "quality_pass": not failures,
    }


def _diagnosis(readings: list[tuple[Any, int]], worst_id: Any, worst: int) -> str:
    """Why the frame was missed, told apart by when it started being missed.

    `g_worst_frame_cost` is a worst-ever, so a loop that never fitted and one
    frame that painted a screen both keep failing every step after the first
    one to go wrong. They want opposite fixes and this gate used to give one
    message for both -- "redraw only what changed" -- which is advice about the
    loop.

    A basketball program was refused three times with it. Its readings were
    1, 1, 2, 2, 2, 7, 7, 7, 7, 7, 7, and the 7 arrived at the step where
    `g_state` went from playing to game over: a screen painted once, charged to
    whoever called `plat_wait_frame` next. Its loop cost 1 at the outset and it
    spent three attempts cutting drawing that was already cheap.

    The first reading is what the loop cost before the run had been anywhere,
    and the readings only ever rise, so the two causes separate cleanly: a
    first reading already over budget is a loop that never fitted, and a worst
    above the first reading is frames later in the run that cost more than the
    loop does. Both can be true, and then both are said.
    """
    opening = readings[0][1]
    said = [
        f"{_SYMBOL} reached {worst} at step {worst_id}: one iteration of the "
        f"game loop overran its display frame by {worst} frames, and at most "
        f"{MAX_MISSED_FRAMES} is accepted."
    ]
    if opening > MAX_MISSED_FRAMES:
        said.append(
            f"The loop was already {opening} over at the first reading, before "
            "the run had been anywhere, so this is what it costs every frame: "
            "redraw only what changed, and move work that does not need to "
            "happen every frame out of the loop."
        )
    if worst > opening:
        # "also" only when the loop was blamed first, so the sentence does not
        # follow on from nothing.
        rose = "It also rose" if len(said) > 1 else "It rose"
        said.append(
            f"{rose} from {opening} to {worst} during the run, so at "
            "least one frame cost far more than the loop does. That is the "
            "shape of a screen painted in the middle of a run -- a new level, "
            "a game-over panel, a pause message, a screen cleared and lettered "
            "-- charged to whoever calls plat_wait_frame next. Call "
            "plat_frame_baseline() after painting it and before the loop that "
            "follows, including a loop that only waits."
        )
    return " ".join(said)
