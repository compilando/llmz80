"""Judging animation from what memory showed between steps."""

from llmz80.studio.feel import animation_report


def _runtime(readings):
    """Build a runtime report from (id, hold, read) triples."""
    return {
        "step_readings": [
            {"id": name, "hold": hold, "read": read} for name, hold, read in readings
        ]
    }


def test_a_frame_that_advances_while_moving_and_rests_when_idle_passes():
    report = animation_report(_runtime([
        ("move_a", "right", {"g_anim_frame": 0}),
        ("move_b", "right", {"g_anim_frame": 2}),
        ("idle", "none", {"g_anim_frame": 2}),
    ]))

    assert report["quality_pass"] is True
    assert report["observed"] is True


def test_classification_reads_hold_not_the_step_id():
    """Ids that give no hint at all still classify correctly: it is `hold`,
    not any naming convention on `id`, that says what a step was doing."""
    report = animation_report(_runtime([
        ("step_1", "left", {"g_anim_frame": 0}),
        ("step_2", "left", {"g_anim_frame": 5}),
        ("step_3", "none", {"g_anim_frame": 5}),
    ]))

    assert report["quality_pass"] is True


def test_a_frame_that_never_moves_fails():
    """A program that declares the symbol and never touches it is not animating.

    The two moving steps hold *different* directions, which is what makes the
    verdict definite: whichever wall the player was against, one of the two
    pushed it away from that wall, so a frame that still never advanced is the
    program's own doing.
    """
    report = animation_report(_runtime([
        ("move_a", "right", {"g_anim_frame": 1}),
        ("move_b", "left", {"g_anim_frame": 1}),
        ("idle", "none", {"g_anim_frame": 1}),
    ]))

    assert report["quality_pass"] is False
    assert "never advanced" in " ".join(report["failures"])


def test_a_still_frame_under_one_repeated_direction_abstains_rather_than_blames():
    """`hold` records the key that was *pressed*, not that the player *moved*.
    Hold left twice against the left wall and a correct program -- one that
    advances the frame only on a frame where the actor actually changed
    position -- reports the same value twice, which is indistinguishable from a
    program that never animates at all.

    Blaming it was worse than a wasted verdict: `generator.repair_prompt` tells
    the writer the frame must differ between consecutive moving readings, and
    the only edit that satisfies that is to advance the frame whenever a
    direction key is held -- which contradicts the state contract's own prose
    and still passes the idle half. The gate would have taught the writer the
    wrong invariant, over and over.
    """
    report = animation_report(_runtime([
        ("move_a", "left", {"g_anim_frame": 2}),
        ("move_b", "left", {"g_anim_frame": 2}),
        ("idle", "none", {"g_anim_frame": 2}),
    ]))

    assert report["observed"] is False
    assert report["quality_pass"] is None
    assert report["failures"] == []
    assert "clamped" in report["reason"]


def test_an_idle_step_that_will_not_hold_still_fails_even_when_movement_is_unclear():
    """The asymmetry is deliberate. "Advances while moving" needs evidence the
    player moved, which a pressed key does not supply; "holds still while idle"
    needs evidence the player did *not* move, and an idle step -- no key held at
    all -- is exactly that. So the idle half stays a hard failure even when the
    moving half has to abstain."""
    report = animation_report(_runtime([
        ("move_a", "left", {"g_anim_frame": 2}),
        ("move_b", "left", {"g_anim_frame": 2}),
        ("idle", "none", {"g_anim_frame": 3}),
    ]))

    assert report["quality_pass"] is False
    assert "while idle" in " ".join(report["failures"])


def test_a_frame_that_keeps_advancing_while_idle_fails():
    """Animation driven by a free-running counter is not reacting to the player."""
    report = animation_report(_runtime([
        ("move_a", "right", {"g_anim_frame": 0}),
        ("move_b", "right", {"g_anim_frame": 2}),
        ("idle", "none", {"g_anim_frame": 4}),
    ]))

    assert report["quality_pass"] is False
    assert "while idle" in " ".join(report["failures"])


def test_a_target_that_never_reported_the_symbol_abstains():
    """No reading is not a pass and not a failure. The CPC has no probe adapter."""
    report = animation_report(_runtime([
        ("move_a", "right", {}),
        ("idle", "none", {}),
    ]))

    assert report["observed"] is False
    assert report["quality_pass"] is None


def test_a_step_missing_the_symbol_is_skipped_not_broken():
    """A step that reported nothing (a probe miss, or a step this gate does not
    care about) should not break the comparison between the steps around it."""
    report = animation_report(_runtime([
        ("move_a", "right", {"g_anim_frame": 0}),
        ("look_around", "action", {}),
        ("move_b", "right", {"g_anim_frame": 2}),
        ("idle", "none", {"g_anim_frame": 2}),
    ]))

    assert report["quality_pass"] is True


def test_an_action_hold_says_nothing_about_movement_and_is_skipped():
    """`hold: "action"` presses the start/fire key. It is neither a movement
    direction nor "none", so it must not be guessed into either bucket."""
    report = animation_report(_runtime([
        ("start", "action", {"g_anim_frame": 0}),
        ("move_a", "right", {"g_anim_frame": 0}),
        ("move_b", "right", {"g_anim_frame": 2}),
        ("idle", "none", {"g_anim_frame": 2}),
    ]))

    assert report["quality_pass"] is True


def test_a_reading_with_no_hold_is_skipped_not_guessed_at():
    """A single step whose `hold` never arrived (an older adapter, a step this
    gate was not told about) is left out, exactly like a missing symbol --
    it does not break the readings around it."""
    runtime = {
        "step_readings": [
            {"id": "move_a", "hold": "right", "read": {"g_anim_frame": 0}},
            {"id": "mystery", "read": {"g_anim_frame": 1}},
            {"id": "move_b", "hold": "right", "read": {"g_anim_frame": 2}},
            {"id": "idle", "hold": "none", "read": {"g_anim_frame": 2}},
        ]
    }

    report = animation_report(runtime)

    assert report["quality_pass"] is True


def test_a_report_with_no_hold_at_all_abstains_like_an_unobserved_target():
    """Every `step_readings` entry looked like this before `hold` was threaded
    through emulator_smoke.py: an id and a read, nothing else. With no step
    classifiable as moving or idle, this reads exactly like a target that
    reported nothing at all -- abstain, not a guess and not a failure."""
    runtime = {
        "step_readings": [
            {"id": "move_a", "read": {"g_anim_frame": 0}},
            {"id": "move_b", "read": {"g_anim_frame": 2}},
            {"id": "idle", "read": {"g_anim_frame": 2}},
        ]
    }

    report = animation_report(runtime)

    assert report["observed"] is False
    assert report["quality_pass"] is None


def test_a_wrapping_counter_is_advancing_not_going_backwards():
    """An unsigned char animation frame wraps constantly; 3, 0, 1 is three
    distinct steps of movement, not evidence of going backwards."""
    report = animation_report(_runtime([
        ("move_a", "right", {"g_anim_frame": 3}),
        ("move_b", "right", {"g_anim_frame": 0}),
        ("move_c", "right", {"g_anim_frame": 1}),
        ("idle", "none", {"g_anim_frame": 1}),
    ]))

    assert report["quality_pass"] is True
    assert report["failures"] == []


def test_a_run_with_no_idle_step_cannot_confirm_the_frame_holds_still():
    """Only moving steps were scripted, so the "holds still" half of the claim
    has no evidence either way. That is a failure, not a silent pass."""
    report = animation_report(_runtime([
        ("move_a", "right", {"g_anim_frame": 0}),
        ("move_b", "right", {"g_anim_frame": 2}),
    ]))

    assert report["observed"] is True
    assert report["quality_pass"] is False
    assert "idle" in " ".join(report["failures"])


def test_a_run_with_only_one_moving_step_cannot_confirm_advance():
    """A single moving reading has no predecessor to compare against, so the
    "advances while moving" half of the claim has no evidence."""
    report = animation_report(_runtime([
        ("move_a", "right", {"g_anim_frame": 0}),
        ("idle", "none", {"g_anim_frame": 0}),
    ]))

    assert report["observed"] is True
    assert report["quality_pass"] is False
    assert "fewer than two" in " ".join(report["failures"])
