"""Judging frame pacing from what memory showed between steps."""

from llmz80.studio.codegen import render_config_header
from llmz80.studio.models import TargetPlatform
from llmz80.studio.pacing import MAX_MISSED_FRAMES, pacing_report
from llmz80.studio.samples import blank_project


def _runtime(readings):
    return {
        "platform": "spectrum",
        "step_readings": [{"id": name, "read": read} for name, read in readings],
    }


def test_a_loop_that_keeps_pace_passes():
    report = pacing_report(
        _runtime(
            [
                ("hold_left_a", {"g_worst_frame_cost": 0}),
                ("idle", {"g_worst_frame_cost": 0}),
            ]
        )
    )

    assert report["quality_pass"] is True
    assert report["worst"] == 0


def test_one_missed_frame_is_tolerated():
    """The first drawn frame and the step where the harness writes its input
    both cost real time, and rejecting a game for them would reject every game."""
    report = pacing_report(_runtime([("hold_left_a", {"g_worst_frame_cost": MAX_MISSED_FRAMES})]))

    assert report["quality_pass"] is True


def test_a_loop_that_does_not_fit_in_its_frame_fails_and_says_where():
    report = pacing_report(
        _runtime(
            [
                ("hold_left_a", {"g_worst_frame_cost": 1}),
                ("hold_right_b", {"g_worst_frame_cost": 7}),
            ]
        )
    )

    assert report["quality_pass"] is False
    assert "7" in report["failures"][0]
    assert "hold_right_b" in report["failures"][0]


def test_a_run_that_never_reported_the_symbol_abstains():
    """Abstaining is not passing: a target with no probe adapter must not
    inherit a verdict it never earned."""
    report = pacing_report(_runtime([("idle", {"g_score": 10})]))

    assert report["quality_pass"] is None
    assert report["observed"] is False


def test_a_target_with_no_frame_clock_abstains_however_good_the_number_looks():
    """`cpc/platform.c` waits for VSYNC and returns zero without measuring
    anything, so every CPC program reads a perfect score it never earned. A
    zero that is not a measurement must not become a pass."""
    runtime = {
        "platform": "amstrad_cpc",
        "step_readings": [{"id": "idle", "read": {"g_worst_frame_cost": 0}}],
    }

    report = pacing_report(runtime)

    assert report["quality_pass"] is None
    assert report["observed"] is False
    assert "frame clock" in report["reason"]


def test_the_header_and_the_gate_never_disagree_about_which_targets_count_frames():
    """The C and the gate read one predicate, `codegen.has_frame_clock`, and
    this pins them to it for every target that exists.

    They used to decide it apart, and the drift would have been silent and in
    the bad direction: the day the CPC gets a frame counter, whoever writes it
    edits `cpc/platform.c` and sees `HAS_FRAME_CLOCK` turn 1, while the gate
    goes on abstaining on a target that has started measuring for real. Adding
    a target has the same shape. This test is the thing that would say so.
    """
    for platform in TargetPlatform:
        header = render_config_header(blank_project("Pacing", platform))
        header_measures = "#define HAS_FRAME_CLOCK 1" in header
        assert header_measures or "#define HAS_FRAME_CLOCK 0" in header, platform

        runtime = {
            "platform": platform.value,
            "step_readings": [{"id": "idle", "read": {"g_worst_frame_cost": 0}}],
        }
        report = pacing_report(runtime)
        gate_measures = report["quality_pass"] is not None

        assert gate_measures is header_measures, (
            f"{platform.value}: game_config.h says HAS_FRAME_CLOCK "
            f"{int(header_measures)} but the pacing gate "
            f"{'judged' if gate_measures else 'abstained on'} the reading"
        )
