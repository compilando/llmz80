"""The steps the emulator drives, which state no expectation about the game."""

import pytest

from llmz80.studio.feel import animation_report
from llmz80.studio.models import HOLD_DIRECTIONS, KEY_LABELS, TargetPlatform
from llmz80.studio.observation import (
    CPC_KEYS,
    PLATFORM_KEYS,
    SPECTRUM_KEYS,
    STEP_FRAMES,
    observation_script,
)
from llmz80.studio.samples import blank_project


def _bind(title: str, bindings: dict[str, str], platform=TargetPlatform.SPECTRUM):
    """A project whose design coined `bindings` itself."""
    project = blank_project(title, platform)
    project.controls.bindings = bindings
    return project


def _readings(
    script: list[dict], animates_on_action: bool = False, moves_on: set[str] | None = None
) -> dict:
    """What a correct program would leave in memory for this script.

    `_run_zesarux` reads the probes at the *end* of each step's hold, so a
    reading carries everything that happened since the previous one -- which
    is the whole point of item 1: a step the gate ignores still moves time.

    `moves_on` names the steps during which the player *actually moved*, which
    is what `main.c` gates the frame on and is not the same thing as a key
    being held: the arena clamps, and a pinned player animates on no step at
    all. Modelling it is how this file finally catches what the emulator run
    showed. Omitting it keeps the optimistic "every held key moves the player"
    program, which is harmless for the tests about step *ordering*.
    """
    frame, step_readings = 0, []
    for step in script:
        if moves_on is None:
            moved = step["key"] is not None and (step["hold"] != "action" or animates_on_action)
        else:
            moved = step["id"] in moves_on
        if moved:
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


@pytest.mark.parametrize("label", KEY_LABELS)
def test_the_key_pressed_on_the_cpc_is_the_key_the_program_reads(label: str):
    """The same obligation as the Spectrum test above, on the machine that
    only just acquired it. `codegen.KEY_CODES[AMSTRAD_CPC]` decides which
    CPCtelera key id the *program* tests for; `CPC_KEYS` decides which key
    ZEsarUX's `send-keys-event` *presses*. Drift between them presses
    something the program ignores, and every gate that reads `step_readings`
    then reports a failure for a correct program."""
    from llmz80.quality.emulator_smoke import _CPC_KEYS, _CPC_TOKEN_KEYS
    from llmz80.studio.codegen import KEY_CODES

    token = KEY_CODES[TargetPlatform.AMSTRAD_CPC][label]

    assert CPC_KEYS[label] == _CPC_TOKEN_KEYS[token]
    assert CPC_KEYS[label] in _CPC_KEYS

    script = observation_script(_bind("Bound CPC", {"left": label}, TargetPlatform.AMSTRAD_CPC))
    expected = CPC_KEYS[label]
    assert [step["key"] for step in script] == [expected, expected, None]


def test_every_step_states_no_expectation():
    """Expectations belong to the phase 2 examiner. A step that predicted a
    value here would be judged by `acceptance_report` and could hand out a pass
    nobody earned."""
    project = blank_project("Silent", TargetPlatform.SPECTRUM)

    assert all(step["expect"] == {} for step in observation_script(project))
    assert all(step["frames"] == STEP_FRAMES for step in observation_script(project))


def test_the_amstrad_cpc_is_driven_by_the_same_script_as_the_spectrum():
    """The CPC used to get `[]` here, because the only adapter it had read no
    memory and took no script -- so every behaviour gate abstained and no CPC
    game could reach `observed`. ZEsarUX drives it now, so it gets the same
    steps in the same order, differing only by the name of each key."""
    spectrum = observation_script(blank_project("Watched", TargetPlatform.SPECTRUM))
    cpc = observation_script(blank_project("Watched CPC", TargetPlatform.AMSTRAD_CPC))

    assert [step["id"] for step in cpc] == [step["id"] for step in spectrum]
    assert [step["hold"] for step in cpc] == [step["hold"] for step in spectrum]
    assert [step["key"] for step in cpc] != [step["key"] for step in spectrum]


def test_a_target_the_harness_cannot_drive_gets_no_script():
    """A machine absent from `PLATFORM_KEYS` has no key the harness could
    press, and a script promising readings nothing will produce makes every
    gate look broken rather than absent."""

    # Stood in rather than assigned onto a real project: `TargetSpec` validates
    # its platform against the enum, so a machine nobody has added cannot be
    # expressed as a GameProject at all -- which is exactly why this floor has
    # to be checked from outside one.
    class _Project:
        class target:
            platform = "sinclair ql"

    assert _Project.target.platform not in PLATFORM_KEYS
    assert observation_script(_Project()) == []


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


def test_the_repeats_are_interleaved_so_consecutive_moving_steps_change_direction():
    """Grouping each direction's two holds together was the bug the first real
    emulator run exposed. Every `_a`/`_b` pair reported the *same* frame -- the
    player spent the second hold pinned against the wall the first one drove it
    into -- so all four pairs contributed nothing, and the run passed only on
    the three transitions between direction groups, a mechanism nobody designed
    and no test covered.

    Interleaved, every adjacent moving pair changes direction by construction,
    which both gives the player somewhere to move and is exactly the straddle
    `feel.animation_report` needs before it will issue a definite failure.
    """
    project = blank_project("Interleaved", TargetPlatform.SPECTRUM)

    script = observation_script(project)

    directions = [step for step in script if step["hold"] in HOLD_DIRECTIONS]
    assert [step["id"] for step in directions] == [
        "hold_left_a",
        "hold_right_a",
        "hold_up_a",
        "hold_down_a",
        "hold_left_b",
        "hold_right_b",
        "hold_up_b",
        "hold_down_b",
    ]
    assert all(one["hold"] != later["hold"] for one, later in zip(directions, directions[1:]))


def test_the_script_gives_the_animation_gate_both_comparisons_it_needs():
    """The reason this module exists: without steps, `step_readings` is empty
    and the gate abstains on every game. It needs consecutive moving readings
    and an idle one to be observed at all.

    Modelled on a program that animates only while the actor really moves --
    `main.c`'s own rule -- rather than on one that animates whenever a key is
    down. Under the optimistic model this passed even for the grouped script
    the emulator showed it should not have.
    """
    project = blank_project("Watched", TargetPlatform.SPECTRUM)
    script = observation_script(project)
    # Interleaved, every direction step pushes away from the wall the previous
    # one drove the player into, so a clamped player still moves on all of them.
    moving = {step["id"] for step in script if step["hold"] in HOLD_DIRECTIONS}

    report = animation_report(_readings(script, moves_on=moving))

    assert report["observed"] is True
    states = [reading["state"] for reading in report["readings"]]
    assert states.count("moving") >= 2
    assert "idle" in states
    assert report["quality_pass"] is True


def test_a_clamped_player_under_a_single_direction_is_not_blamed_for_it():
    """One bound direction, and `models.ControlsSpec` accepts it: the player
    reaches the wall inside the first hold and cannot move again, so a correct
    program reports the same frame twice. The gate used to call that "never
    advanced" and hand `repair_prompt` a complaint whose only fix is to animate
    on input rather than on movement -- teaching the writer an invariant the
    state contract's own prose contradicts. It abstains instead."""
    project = _bind("Un Sentido", {"jump": "SPACE", "left": "O"})

    script = observation_script(project)

    assert [step["id"] for step in script] == [
        "hold_jump_a",
        "hold_jump_b",
        "hold_left_a",
        "hold_left_b",
        "idle",
    ]
    report = animation_report(_readings(script, moves_on={"hold_left_a"}))
    assert report["quality_pass"] is None
    assert report["failures"] == []


def test_a_program_that_never_animates_still_fails_under_the_sample_bindings():
    """The abstention above must not become a way through. With four directions
    the script straddles on every adjacent pair, so a frame that never moves is
    the program's own doing and is reported as a definite failure."""
    project = blank_project("Frozen", TargetPlatform.SPECTRUM)

    report = animation_report(_readings(observation_script(project), moves_on=set()))

    assert report["quality_pass"] is False
    assert "never advanced" in " ".join(report["failures"])


def test_a_program_that_animates_while_the_action_key_is_held_still_passes():
    """A jump, a fire animation, SPACE leaving a title screen. The gate drops
    the action steps but not the two seconds they occupied, so holding them
    last -- between the final direction reading and the idle one -- failed a
    correct program with `g_anim_frame changed while idle`, a complaint no
    writer can satisfy and one `generator.py` burns a repair attempt on."""
    project = _bind("Fase Uno", {"left": "O", "right": "P", "jump": "SPACE"})

    script = observation_script(project)

    assert [step["id"] for step in script][-3:] == ["hold_left_b", "hold_right_b", "idle"]
    report = animation_report(_readings(script, animates_on_action=True))
    assert report["failures"] == []
    assert report["quality_pass"] is True
