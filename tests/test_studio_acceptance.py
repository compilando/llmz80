import pytest

from llmz80.core.state_contract import (
    REQUIRED_SYMBOLS,
    STATE_PLAYING,
    STATE_CONTRACT,
    contract_prompt,
)
from llmz80.studio.acceptance import (
    generation_prompt,
    runtime_script,
    scenarios_prompt,
    with_executable_scenarios,
)
from llmz80.studio.models import AcceptanceScenario, GenreId, TargetPlatform
from llmz80.studio.packs import create_default_project
from llmz80.studio.services import StudioService


@pytest.fixture
def project():
    return create_default_project("Contract", TargetPlatform.SPECTRUM, GenreId.MAZE_CHASE)


def test_the_contract_prompt_names_every_symbol_and_its_type():
    prompt = contract_prompt()

    for symbol in STATE_CONTRACT:
        assert symbol.name in prompt
        assert symbol.meaning in prompt
    assert "unsigned int g_score;" in prompt
    assert "unsigned char g_lives;" in prompt
    # The two rules that cost real build failures to learn.
    assert "static" in prompt
    assert "data segment" in prompt


def test_required_symbols_are_the_ones_a_playable_design_cannot_omit():
    assert set(REQUIRED_SYMBOLS) == {"g_score", "g_lives", "g_level", "g_state"}


def test_default_projects_ship_runnable_acceptance(project):
    executable = [scenario for scenario in project.acceptance if scenario.executable]

    assert [scenario.id for scenario in executable] == ["start_game", "collect_scores"]
    start = executable[0]
    assert start.hold == "action"
    assert start.expect["g_state"] == STATE_PLAYING
    collect = executable[1]
    assert collect.expect["g_score"] == project.gameplay.score_per_collectible
    assert collect.expect["g_remaining"] == 7


def test_a_criterion_the_design_cannot_predict_stays_prose(project):
    enemy = next(s for s in project.acceptance if s.id == "enemy_costs_life")

    assert enemy.executable is False
    assert enemy.then  # the prose is still there for a reader


def test_the_script_keeps_the_designs_order(project):
    steps = runtime_script(project)

    assert [step["id"] for step in steps] == ["start_game", "collect_scores"]
    assert steps[0]["frames"] > 0


def test_the_prompt_states_the_checks_and_the_controls(project):
    prompt = scenarios_prompt(project)

    assert "hold action for 30 frames" in prompt
    assert "g_score == 10" in prompt
    assert "action = SPACE" in prompt
    assert prompt in generation_prompt(project)


def test_a_design_without_runnable_criteria_produces_no_script(project):
    document = project.model_dump(mode="json")
    for scenario in document["acceptance"]:
        scenario["hold"] = None
        scenario["expect"] = {}
    bare = type(project).model_validate(document)

    assert runtime_script(bare) == []
    assert scenarios_prompt(bare) == ""


def test_deriving_scenarios_is_idempotent(project):
    again = with_executable_scenarios(project)

    assert [s.model_dump() for s in again.acceptance] == [
        s.model_dump() for s in project.acceptance
    ]


def test_a_step_whose_reading_contradicts_the_design_fails(tmp_path, project):
    service = StudioService.at(tmp_path)
    runtime = {
        "step_readings": [
            {"id": "start_game", "read": {"g_state": 1, "g_level": 1, "g_score": 0}},
            {"id": "collect_scores", "read": {"g_score": 0, "g_remaining": 8}},
        ]
    }

    report = service.acceptance_report(project, runtime)

    assert report["quality_pass"] is False
    assert report["failures"] == ["collect_scores"]
    failed = next(item for item in report["scenarios"] if item["id"] == "collect_scores")
    assert "g_score: expected 10, read 0" in failed["mismatches"]


def test_every_step_matching_passes(tmp_path, project):
    service = StudioService.at(tmp_path)
    runtime = {
        "step_readings": [
            {"id": step["id"], "read": dict(step["expect"])}
            for step in runtime_script(project)
        ]
    }

    report = service.acceptance_report(project, runtime)

    assert report["quality_pass"] is True
    assert report["failures"] == []


def test_a_target_without_readings_abstains(tmp_path, project):
    service = StudioService.at(tmp_path)

    report = service.acceptance_report(project, {"step_readings": []})

    assert report["observed"] is False
    assert report["quality_pass"] is None
    assert "no memory probe adapter" in report["reason"]


def test_a_scenario_expecting_an_unknown_symbol_is_refused():
    with pytest.raises(ValueError, match="outside the state contract"):
        AcceptanceScenario(
            id="bogus",
            given="a",
            when="b",
            then="c",
            hold="down",
            expect={"g_not_a_symbol": 1},
        )
