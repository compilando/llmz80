"""The steps the emulator drives, which state no expectation about the game."""

from llmz80.studio.models import TargetPlatform
from llmz80.studio.observation import STEP_FRAMES, observation_script
from llmz80.studio.samples import blank_project


def test_every_binding_is_held_twice_and_then_let_go():
    """Twice because `feel.animation_report` compares consecutive readings, and
    one reading of a moving step has nothing to be compared against."""
    project = blank_project("Observed", TargetPlatform.SPECTRUM)

    script = observation_script(project)

    ids = [step["id"] for step in script]
    assert ids[-1] == "idle"
    assert ids.count("hold_left_a") == 1
    assert ids.count("hold_left_b") == 1
    assert len(ids) == len(set(ids))
    assert len(script) == 2 * len(project.controls.bindings) + 1


def test_a_direction_binding_holds_as_movement_and_anything_else_as_action():
    """`feel._classify` reads `hold`, so this is what decides whether a step
    counts as movement. A design coining its own name for a key gets `action`,
    which says nothing rather than something wrong."""
    project = blank_project("Classified", TargetPlatform.SPECTRUM)

    holds = {step["id"]: step["hold"] for step in observation_script(project)}

    assert holds["hold_left_a"] == "left"
    assert holds["hold_action_a"] == "action"
    assert holds["idle"] == "none"


def test_keys_are_named_the_way_the_emulator_knows_them():
    """`_run_zesarux` looks each step's key up in `_SPECTRUM_ROWS`, whose names
    are lowercase, and the 48K reaches its four directions through 5678."""
    from llmz80.quality.emulator_smoke import _SPECTRUM_ROWS

    project = blank_project("Keyed", TargetPlatform.SPECTRUM)

    for step in observation_script(project):
        if step["key"] is not None:
            assert step["key"] in _SPECTRUM_ROWS


def test_every_step_states_no_expectation():
    """Expectations belong to the phase 2 examiner. A step that predicted a
    value here would be judged by `acceptance_report` and could hand out a pass
    nobody earned."""
    project = blank_project("Silent", TargetPlatform.SPECTRUM)

    assert all(step["expect"] == {} for step in observation_script(project))
    assert all(step["frames"] == STEP_FRAMES for step in observation_script(project))


def test_a_target_the_harness_cannot_drive_gets_no_script():
    """`_run_caprice32` ignores its script entirely, so handing the CPC one
    would promise readings that never arrive."""
    project = blank_project("Silent CPC", TargetPlatform.AMSTRAD_CPC)

    assert observation_script(project) == []
