"""Judging animation from what memory showed between steps."""

from llmz80.studio.feel import animation_report


def _runtime(readings):
    return {"step_readings": [{"id": name, "read": read} for name, read in readings]}


def test_a_frame_that_advances_while_moving_and_rests_when_idle_passes():
    report = animation_report(_runtime([
        ("move_a", {"g_anim_frame": 0}),
        ("move_b", {"g_anim_frame": 2}),
        ("idle", {"g_anim_frame": 2}),
    ]))

    assert report["quality_pass"] is True
    assert report["observed"] is True


def test_a_frame_that_never_moves_fails():
    """A program that declares the symbol and never touches it is not animating."""
    report = animation_report(_runtime([
        ("move_a", {"g_anim_frame": 1}),
        ("move_b", {"g_anim_frame": 1}),
        ("idle", {"g_anim_frame": 1}),
    ]))

    assert report["quality_pass"] is False
    assert "never advanced" in " ".join(report["failures"])


def test_a_frame_that_keeps_advancing_while_idle_fails():
    """Animation driven by a free-running counter is not reacting to the player."""
    report = animation_report(_runtime([
        ("move_a", {"g_anim_frame": 0}),
        ("move_b", {"g_anim_frame": 2}),
        ("idle", {"g_anim_frame": 4}),
    ]))

    assert report["quality_pass"] is False
    assert "while idle" in " ".join(report["failures"])


def test_a_target_that_never_reported_the_symbol_abstains():
    """No reading is not a pass and not a failure. The CPC has no probe adapter."""
    report = animation_report(_runtime([("move_a", {}), ("idle", {})]))

    assert report["observed"] is False
    assert report["quality_pass"] is None


def test_a_step_missing_the_symbol_is_skipped_not_broken():
    """A step that reported nothing (a probe miss, or a step this gate does not
    care about) should not break the comparison between the steps around it."""
    report = animation_report(_runtime([
        ("move_a", {"g_anim_frame": 0}),
        ("look_around", {}),
        ("move_b", {"g_anim_frame": 2}),
        ("idle", {"g_anim_frame": 2}),
    ]))

    assert report["quality_pass"] is True


def test_a_wrapping_counter_is_advancing_not_going_backwards():
    """An unsigned char animation frame wraps constantly; 3, 0, 1 is three
    distinct steps of movement, not evidence of going backwards."""
    report = animation_report(_runtime([
        ("move_a", {"g_anim_frame": 3}),
        ("move_b", {"g_anim_frame": 0}),
        ("move_c", {"g_anim_frame": 1}),
        ("idle", {"g_anim_frame": 1}),
    ]))

    assert report["quality_pass"] is True
    assert report["failures"] == []


def test_a_run_with_no_idle_step_cannot_confirm_the_frame_holds_still():
    """Only moving steps were scripted, so the "holds still" half of the claim
    has no evidence either way. That is a failure, not a silent pass."""
    report = animation_report(_runtime([
        ("move_a", {"g_anim_frame": 0}),
        ("move_b", {"g_anim_frame": 2}),
    ]))

    assert report["observed"] is True
    assert report["quality_pass"] is False
    assert "idle" in " ".join(report["failures"])


def test_a_run_with_only_one_moving_step_cannot_confirm_advance():
    """A single moving reading has no predecessor to compare against, so the
    "advances while moving" half of the claim has no evidence."""
    report = animation_report(_runtime([
        ("move_a", {"g_anim_frame": 0}),
        ("idle", {"g_anim_frame": 0}),
    ]))

    assert report["observed"] is True
    assert report["quality_pass"] is False
    assert "fewer than two" in " ".join(report["failures"])
