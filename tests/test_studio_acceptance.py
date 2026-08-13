"""Until the examiner exists, the runtime gate abstains instead of guessing."""

from llmz80.studio.acceptance import design_prompt, generation_prompt, runtime_script
from llmz80.studio.models import GameProject, TargetPlatform
from llmz80.studio.samples import blank_project


def test_the_runtime_script_is_empty_and_says_so():
    assert runtime_script(blank_project("Quiet", TargetPlatform.SPECTRUM)) == []


def test_the_design_prompt_shows_the_declared_vocabulary():
    project = blank_project("Vocabulary", TargetPlatform.SPECTRUM)
    document = project.model_dump(mode="json")
    document["metadata"]["brief"] = "un explorador cruza salas de piedra"
    document["mechanics"] = ["SPACE salta y la gravedad devuelve al suelo"]
    document["entities"][0]["notes"] = "el que mueve el jugador"
    prompt = design_prompt(GameProject.model_validate(document))
    assert "un explorador cruza salas de piedra" in prompt
    assert "SPACE salta" in prompt
    assert "el que mueve el jugador" in prompt
    assert "actor" in prompt


def test_the_design_prompt_shows_the_tile_alphabet_the_design_coined():
    prompt = design_prompt(blank_project("Tiles", TargetPlatform.SPECTRUM))
    assert "'#' is wall" in prompt
    assert "'.' is floor" in prompt


def test_the_design_prompt_names_the_bindings_and_their_bits():
    prompt = design_prompt(blank_project("Keys", TargetPlatform.SPECTRUM))
    assert "INPUT_LEFT" in prompt
    assert "O" in prompt


def test_the_design_prompt_lists_screens_and_where_they_lead():
    project = blank_project("Rooms", TargetPlatform.SPECTRUM)
    document = project.model_dump(mode="json")
    second = dict(document["screens"][0])
    second.update(id="screen_2", name="SCREEN 2", spawns=[], exits={"left": "screen_1"})
    document["screens"] = [dict(document["screens"][0], exits={"right": "screen_2"}), second]
    prompt = design_prompt(GameProject.model_validate(document))
    assert "screen_1" in prompt and "screen_2" in prompt
    assert "right -> screen_2" in prompt


def test_the_generation_prompt_still_carries_the_state_contract():
    prompt = generation_prompt(blank_project("Contract", TargetPlatform.SPECTRUM))
    assert "OBSERVABLE STATE CONTRACT" in prompt
    assert "g_score" in prompt


def test_the_pellet_derivation_is_gone():
    import llmz80.studio.acceptance as acceptance

    for name in (
        "derive_scenarios",
        "sweep_frames",
        "chase_catch_frames",
        "FRAMES_PER_CELL",
        "with_executable_scenarios",
    ):
        assert not hasattr(acceptance, name), f"{name} survives"
