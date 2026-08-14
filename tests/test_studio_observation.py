"""The steps the emulator drives, which state no expectation about the game."""

import pytest

from llmz80.studio.feel import animation_report
from llmz80.studio.models import KEY_LABELS, TargetPlatform
from llmz80.studio.observation import SPECTRUM_KEYS, STEP_FRAMES, observation_script
from llmz80.studio.samples import blank_project


def _bind(title: str, bindings: dict[str, str]):
    """A Spectrum project whose design coined `bindings` itself."""
    project = blank_project(title, TargetPlatform.SPECTRUM)
    project.controls.bindings = bindings
    return project


def _readings(script: list[dict], animates_on_action: bool) -> dict:
    """What a correct program would leave in memory for this script.

    `_run_zesarux` reads the probes at the *end* of each step's hold, so a
    reading carries everything that happened since the previous one -- which
    is the whole point of item 1: a step the gate ignores still moves time.
    """
    frame, step_readings = 0, []
    for step in script:
        held = step["key"] is not None
        if held and (step["hold"] != "action" or animates_on_action):
            # An unsigned char cycling 0..3: advancing, never monotonic.
            frame = (frame + 1) % 4
        step_readings.append(
            {"id": step["id"], "hold": step["hold"], "read": {"g_anim_frame": frame}}
        )
    return {"step_readings": step_readings}


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
    for name in project.controls.bindings:
        assert [step_id for step_id in ids if step_id.startswith(f"hold_{name}_")] == [
            f"hold_{name}_a",
            f"hold_{name}_b",
        ]


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


@pytest.mark.parametrize("label", KEY_LABELS)
def test_the_key_pressed_is_the_key_the_program_reads(label: str):
    """`SPECTRUM_KEYS` and `codegen.KEY_CODES` state one fact from two sides:
    which key the emulator presses, and which key the program reads. Drift
    between them presses a key the program ignores, so every moving step reads
    a still animation and the gate fails a correct program. Every label, not
    just the five `blank_project` binds, and every binding reaching a script:
    a label missing from `SPECTRUM_KEYS` would drop its binding silently."""
    from llmz80.quality.emulator_smoke import _SPECTRUM_ROWS
    from llmz80.studio.codegen import KEY_CODES

    scancode = KEY_CODES[TargetPlatform.SPECTRUM][label]
    expected = scancode.removeprefix("IN_KEY_SCANCODE_").lower()

    assert SPECTRUM_KEYS[label] == expected
    assert SPECTRUM_KEYS[label] in _SPECTRUM_ROWS

    script = observation_script(_bind("Bound", {"left": label}))
    assert [step["key"] for step in script] == [expected, expected, None]


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


def test_a_design_that_never_names_a_direction_gets_no_script():
    """`hold` comes from the name the design coined, and the default project
    language is Spanish. All-action steps would make `animation_report` report
    `observed: True` and a definite failure for a program it never watched
    move; an empty script lets it abstain, which is the honest answer."""
    project = _bind("Sin Direcciones", {"izquierda": "O", "derecha": "P", "saltar": "SPACE"})

    assert observation_script(project) == []

    report = animation_report(_readings(observation_script(project), animates_on_action=True))
    assert report["observed"] is False
    assert report["quality_pass"] is None


def test_the_script_gives_the_animation_gate_both_comparisons_it_needs():
    """The reason this module exists: without steps, `step_readings` is empty
    and the gate abstains on every game. It needs consecutive moving readings
    and an idle one to be observed at all."""
    project = blank_project("Watched", TargetPlatform.SPECTRUM)

    report = animation_report(_readings(observation_script(project), animates_on_action=False))

    assert report["observed"] is True
    states = [reading["state"] for reading in report["readings"]]
    assert states.count("moving") >= 2
    assert "idle" in states
    assert report["quality_pass"] is True


def test_a_program_that_animates_while_the_action_key_is_held_still_passes():
    """A jump, a fire animation, SPACE leaving a title screen. The gate drops
    the action steps but not the two seconds they occupied, so holding them
    last -- between the final direction reading and the idle one -- failed a
    correct program with `g_anim_frame changed while idle`, a complaint no
    writer can satisfy and one `generator.py` burns a repair attempt on."""
    project = _bind("Fase Uno", {"left": "O", "right": "P", "jump": "SPACE"})

    script = observation_script(project)

    assert [step["id"] for step in script][-3:] == ["hold_right_a", "hold_right_b", "idle"]
    report = animation_report(_readings(script, animates_on_action=True))
    assert report["failures"] == []
    assert report["quality_pass"] is True
