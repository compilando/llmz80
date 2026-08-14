"""The design gate checks the machine's limits, not the shape of the game."""

from llmz80.studio.models import GameProject, TargetPlatform
from llmz80.studio.quality import design_quality_report, studio_quality_report
from llmz80.studio.samples import blank_project


def test_a_blank_design_passes_the_gate():
    report = design_quality_report(blank_project("Gate", TargetPlatform.SPECTRUM))
    assert report["quality_pass"], report["failures"]


def test_a_design_with_no_enemy_and_no_collectible_passes():
    """The old gate demanded player, enemy and collectible. A game need not
    have any of the last two."""
    report = design_quality_report(blank_project("Lonely", TargetPlatform.SPECTRUM))
    assert "core_roles" not in report["checks"]
    assert report["quality_pass"]


def test_audio_the_target_cannot_play_is_still_refused():
    project = blank_project("Noisy", TargetPlatform.AMSTRAD_CPC)
    document = project.model_dump(mode="json")
    document["audio"]["effects"] = ["collect"]
    report = design_quality_report(GameProject.model_validate(document))
    assert not report["quality_pass"]
    assert report["audio_gaps"]


def test_a_binary_budget_beyond_the_machine_is_refused():
    project = blank_project("Greedy", TargetPlatform.SPECTRUM)
    document = project.model_dump(mode="json")
    document["budgets"]["binary_bytes"] = 65535
    report = design_quality_report(GameProject.model_validate(document))
    assert "budget_fits_target" in report["failures"]


def test_a_design_that_declares_no_mechanics_is_told_so_without_being_refused():
    """A design with no rules produces an arbitrary game, and the person who
    wrote it should hear about it -- but it is not Studio's place to refuse it."""
    report = design_quality_report(blank_project("Mute", TargetPlatform.SPECTRUM))
    assert report["quality_pass"]
    assert any("mechanic" in notice for notice in report["notices"])


def test_a_design_that_declares_mechanics_gets_no_such_notice():
    project = blank_project("Spoken", TargetPlatform.SPECTRUM)
    document = project.model_dump(mode="json")
    document["mechanics"] = ["the player jumps with SPACE"]
    report = design_quality_report(GameProject.model_validate(document))
    assert not any("mechanic" in notice for notice in report["notices"])


def test_the_gate_reports_the_three_stages_it_has():
    project = blank_project("Stages", TargetPlatform.SPECTRUM)
    report = studio_quality_report(project, build={"quality_pass": True}, runtime=None)
    assert set(report["gates"]) == {"design", "build", "runtime"}
    assert report["gates"]["design"] is True
    assert report["gates"]["runtime"] is False


def test_the_retired_analyses_are_gone():
    import pytest

    for module in (
        "llmz80.studio.solvability",
        "llmz80.studio.difficulty",
        "llmz80.studio.terrain_structure",
    ):
        with pytest.raises(ModuleNotFoundError):
            __import__(module)
