import json

import pytest

from llmz80.core.generation_spec import create_generation_spec


@pytest.mark.parametrize(
    "prompt,platform,archetype,language,capability",
    [
        ("Una pulga que salta por la pantalla", "spectrum", "platform_movement", "es", "sprite"),
        ("A flea that jumps around the screen", "spectrum", "platform_movement", "en", "sprite"),
        ("Recoge monedas con marcador", "amstrad_cpc", "collect_game", "es", "score"),
        ("A playable maze with an exit", "amstrad_cpc", "board_game", "en", "end_state"),
    ],
)
def test_bilingual_specs_are_stable(prompt, platform, archetype, language, capability):
    first = create_generation_spec(prompt, platform)
    second = create_generation_spec(prompt, platform)
    assert first == second
    assert first.archetype == archetype
    assert first.language == language
    assert capability in first.capabilities
    assert json.loads(first.to_json())["schema_version"] == 1


def test_spec_has_platform_resource_and_timing_contracts():
    spec = create_generation_spec("Animated Mode 0 sprite", "amstrad_cpc")
    assert spec.presentation["video_mode"] == 0
    assert spec.timing["frame_hz"] == 50
    assert spec.budgets["program_binary_bytes"] > 0


def test_empty_prompt_is_rejected():
    with pytest.raises(ValueError):
        create_generation_spec("   ", "spectrum")


def test_start_message_implies_input_contract():
    spec = create_generation_spec(
        "A title screen with instructions and a blinking start message", "amstrad_cpc"
    )
    assert "input" in spec.capabilities
    assert spec.timing["input_edges_required"] is True
