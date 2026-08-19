"""Telling a heavy game loop apart from one expensive frame.

`g_worst_frame_cost` is a worst-ever, so a single costly frame keeps failing
the gate for the rest of the run. The two causes want opposite fixes and the
gate gave one message for both:

    Redraw only what changed, and move work that does not need to happen
    every frame out of the loop.

A basketball program was refused three times running with that. Its loop was
not the problem: the readings across the eleven steps were

    1, 1, 2, 2, 2, 7, 7, 7, 7, 7, 7

-- a loop costing 1 to 2, and one frame costing 7 where `g_state` went from
playing to game over and the program painted a new screen. The advice sent
three attempts cutting drawing that was already cheap, and the run ended with
the account out of credit rather than with a game.

The gate is already holding what tells them apart. A cost that is over budget
in the very first reading is a loop that never fitted; a cost that starts
inside it and jumps is a screen transition charged to whoever called
`plat_wait_frame` next, and `plat_frame_baseline` is what that program needed
to call.
"""

from __future__ import annotations

from llmz80.studio.pacing import MAX_MISSED_FRAMES, pacing_report


def _runtime(costs: list[int], platform: str = "amstrad_cpc") -> dict:
    return {
        "platform": platform,
        "step_readings": [
            {"id": f"step_{index}", "read": {"g_worst_frame_cost": cost}}
            for index, cost in enumerate(costs)
        ],
    }


class TestALoopThatNeverFitted:
    """Over budget from the first reading. Nothing changed later; the loop
    itself is too heavy, and cutting work in it is the fix."""

    def test_it_is_still_refused(self):
        report = pacing_report(_runtime([4, 4, 4, 4]))

        assert report["quality_pass"] is False

    def test_and_still_told_to_cut_work_from_the_loop(self):
        report = pacing_report(_runtime([4, 4, 4, 4]))

        assert "redraw only what changed" in report["failures"][0]

    def test_it_is_not_sent_after_a_transition_that_never_happened(self):
        report = pacing_report(_runtime([4, 4, 4, 4]))

        assert "plat_frame_baseline" not in report["failures"][0]


class TestOneExpensiveFrame:
    """Inside budget, then a jump. The loop fits; something painted a screen."""

    def test_it_is_refused_too(self):
        """The frame really did overrun, and a game that stutters when it
        changes screen is still a game that stutters."""
        report = pacing_report(_runtime([1, 1, 2, 7, 7]))

        assert report["quality_pass"] is False

    def test_the_step_it_jumped_at_is_named(self):
        report = pacing_report(_runtime([1, 1, 2, 7, 7]))

        assert "step_3" in report["failures"][0]

    def test_and_the_call_that_fixes_it(self):
        report = pacing_report(_runtime([1, 1, 2, 7, 7]))

        assert "plat_frame_baseline" in report["failures"][0]

    def test_what_the_loop_itself_cost_is_reported(self):
        """The number that says the loop was never the problem. Without it the
        writer has only the 7 and no reason to believe its drawing is fine."""
        report = pacing_report(_runtime([1, 1, 2, 7, 7]))

        assert "rose from 1 to 7" in report["failures"][0]

    def test_a_jump_from_within_budget_is_not_called_a_heavy_loop(self):
        report = pacing_report(_runtime([0, 0, 9]))

        assert "redraw only what changed" not in report["failures"][0]


class TestBothAtOnce:
    """A heavy loop does not stop a screen transition from also being charged,
    and a writer told only about one fixes only one."""

    def test_a_heavy_loop_that_also_jumps_is_told_about_both(self):
        report = pacing_report(_runtime([3, 3, 9]))

        assert "redraw only what changed" in report["failures"][0]
        assert "plat_frame_baseline" in report["failures"][0]


class TestWhatDoesNotChange:
    def test_a_loop_inside_budget_throughout_still_passes(self):
        report = pacing_report(_runtime([0, 1, 1, 1]))

        assert report["quality_pass"] is True
        assert report["failures"] == []

    def test_the_worst_and_its_step_are_unchanged(self):
        report = pacing_report(_runtime([1, 1, 2, 7, 7]))

        assert report["worst"] == 7

    def test_the_readings_are_still_published(self):
        report = pacing_report(_runtime([1, 2]))

        assert report["readings"] == [
            {"id": "step_0", "read": 1},
            {"id": "step_1", "read": 2},
        ]

    def test_a_target_with_no_frame_clock_still_abstains(self):
        report = pacing_report(_runtime([9, 9], platform="something_else"))

        assert report["quality_pass"] is None

    def test_one_reading_over_budget_is_a_heavy_loop(self):
        """With a single step there is no before and after, so the jump cannot
        be claimed and the older advice is the honest one."""
        report = pacing_report(_runtime([5]))

        assert "redraw only what changed" in report["failures"][0]
        assert MAX_MISSED_FRAMES == 1
