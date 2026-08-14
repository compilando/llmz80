"""The command screen's status line: pure state, read without drawing anything."""

from __future__ import annotations

import json

import pytest

from llmz80.studio.models import AssetSpec, TargetPlatform
from llmz80.studio.reference import GameReference, save_reference
from llmz80.studio.samples import blank_project
from llmz80.studio.screen import STAGE_NAMES, Stage, next_step, stage_line


@pytest.fixture
def project():
    return blank_project("Zampabolas", TargetPlatform.SPECTRUM)


def _by_name(stages: list[Stage]) -> dict[str, Stage]:
    return {stage.name: stage for stage in stages}


def _dossier(**overrides) -> GameReference:
    document = {
        "identified": True,
        "confidence": "high",
        "title": "Zampa Bolas",
        "publisher": "Iber Soft",
        "year": 1985,
        "platforms": ["spectrum"],
        "sources": [
            {
                "url": "https://worldofspectrum.org/example",
                "title": "Zampa Bolas",
                "retrieved_at": "2026-08-11T09:00:00Z",
            },
            {
                "url": "https://example.com/second",
                "title": "Second source",
                "retrieved_at": "2026-08-11T09:00:00Z",
            },
        ],
    }
    document.update(overrides)
    return GameReference.model_validate(document)


# --- the whole line -----------------------------------------------------


def test_with_no_project_there_are_no_stages():
    assert stage_line(None, None) == []


def test_a_fresh_project_with_no_directory_is_pending_except_its_design(project):
    stages = _by_name(stage_line(project, None))

    assert set(stages) == set(STAGE_NAMES)
    assert stages["referencia"].state == "pending"
    assert stages["diseño"].state == "done"  # blank_project starts solvable and structured
    assert stages["sprites"].state == "pending"
    assert stages["programa"].state == "pending"
    assert stages["gates"].state == "pending"
    assert stages["release"].state == "pending"


def test_a_fresh_project_saved_to_an_empty_directory_reads_the_same_way(project, tmp_path):
    stages = _by_name(stage_line(project, tmp_path))

    assert stages["referencia"].state == "pending"
    assert stages["diseño"].state == "done"
    assert stages["sprites"].state == "pending"
    assert stages["programa"].state == "pending"
    assert stages["gates"].state == "pending"
    assert stages["release"].state == "pending"


def test_stage_order_matches_the_pipeline(project, tmp_path):
    stages = stage_line(project, tmp_path)

    assert [stage.name for stage in stages] == list(STAGE_NAMES)


# --- referencia -----------------------------------------------------------


def test_referencia_is_pending_without_a_directory(project):
    stage = _by_name(stage_line(project, None))["referencia"]

    assert stage.state == "pending"
    assert stage.detail == ""


def test_referencia_is_pending_when_no_reference_file_exists(project, tmp_path):
    stage = _by_name(stage_line(project, tmp_path))["referencia"]

    assert stage.state == "pending"


def test_referencia_is_done_and_names_the_title_and_source_count(project, tmp_path):
    save_reference(_dossier(), tmp_path)

    stage = _by_name(stage_line(project, tmp_path))["referencia"]

    assert stage.state == "done"
    assert "Zampa Bolas" in stage.detail
    assert "2" in stage.detail


def test_referencia_is_failed_when_the_search_found_nothing(project, tmp_path):
    save_reference(_dossier(identified=False, confidence="low", title="", sources=[]), tmp_path)

    stage = _by_name(stage_line(project, tmp_path))["referencia"]

    assert stage.state == "failed"


def test_referencia_is_failed_rather_than_crashing_on_a_malformed_file(project, tmp_path):
    (tmp_path / "reference.yml").write_text("identified: true\nconfidence: not-a-real-value\n")

    stages = stage_line(project, tmp_path)  # must not raise

    stage = _by_name(stages)["referencia"]
    assert stage.state == "failed"


def test_referencia_distinguishes_absent_from_unidentified(project, tmp_path):
    """An unsearched project and one that searched and found nothing are not the same state."""
    absent = _by_name(stage_line(project, tmp_path))["referencia"]

    save_reference(_dossier(identified=False, confidence="low", title="", sources=[]), tmp_path)
    unidentified = _by_name(stage_line(project, tmp_path))["referencia"]

    assert absent.state == "pending"
    assert unidentified.state == "failed"
    assert absent.state != unidentified.state


# --- diseño -----------------------------------------------------------------


def test_diseno_is_done_for_a_solvable_structured_design(project):
    stage = _by_name(stage_line(project, None))["diseño"]

    assert stage.state == "done"


def _oversized(project):
    """A screen wider than its target's playfield, bypassing GameProject's
    own construction-time validation (`model_copy` runs no validators) --
    the one way `editing_status`'s `backend_error` can be reached at all,
    since `structure._fit_errors` already refuses this same thing whenever a
    project is actually constructed or edited through `editing.py`.
    """
    original = project.screens[0]
    width = 35  # wider than spectrum_bitmap's 32-column playfield
    top = "#" * width
    middle = "#" + "." * (width - 2) + "#"
    oversized = original.model_copy(
        update={"width": width, "tiles": [top] + [middle] * (original.height - 2) + [top]}
    )
    return project.model_copy(update={"screens": [oversized]})


def test_diseno_is_failed_when_a_screen_does_not_fit_the_target(project):
    """v4 has no notion of a design losing its "shape" any more -- solvability
    and terrain structure were retired along with the rules that only made
    sense for one kind of game (see `editing.editing_status`'s docstring).
    The one thing `diseño` can still fail on is a screen too big for its
    target's playable grid.
    """
    unfit = _oversized(project)

    stage = _by_name(stage_line(unfit, None))["diseño"]

    assert stage.state == "failed"
    assert stage.detail  # names why, from editing_status's own backend_error


# --- sprites ------------------------------------------------------------


def _sprite_asset(**overrides) -> AssetSpec:
    document = {
        "id": "hero",
        "kind": "sprite",
        "source": "assets/hero.png",
        "width": 16,
        "height": 16,
        "frames": 1,
    }
    document.update(overrides)
    return AssetSpec.model_validate(document)


def test_sprites_is_pending_with_no_sprite_assets(project):
    stage = _by_name(stage_line(project, None))["sprites"]

    assert stage.state == "pending"


def test_sprites_is_done_when_every_sprite_asset_fits_the_blitter(project):
    with_sprite = project.model_copy(update={"assets": [_sprite_asset()]})

    stage = _by_name(stage_line(with_sprite, None))["sprites"]

    assert stage.state == "done"
    assert "1" in stage.detail


def test_sprites_is_failed_when_the_blitter_would_reject_one(project):
    oversized = _sprite_asset(id="giant", source="assets/giant.png", width=32, height=32, frames=1)
    with_sprite = project.model_copy(update={"assets": [oversized]})

    stage = _by_name(stage_line(with_sprite, None))["sprites"]

    assert stage.state == "failed"


def test_sprites_ignores_non_sprite_assets(project):
    tileset = _sprite_asset(id="ground", kind="tileset", source="assets/ground.png")
    with_tileset = project.model_copy(update={"assets": [tileset]})

    stage = _by_name(stage_line(with_tileset, None))["sprites"]

    assert stage.state == "pending"


# --- programa -------------------------------------------------------------


def test_programa_is_pending_with_no_directory(project):
    stage = _by_name(stage_line(project, None))["programa"]

    assert stage.state == "pending"


def test_programa_is_pending_with_an_empty_directory(project, tmp_path):
    stage = _by_name(stage_line(project, tmp_path))["programa"]

    assert stage.state == "pending"


def test_programa_is_done_once_main_c_exists(project, tmp_path):
    program_dir = tmp_path / project.program_dir
    program_dir.mkdir()
    (program_dir / "main.c").write_text("int main(void) { return 0; }\n")

    stage = _by_name(stage_line(project, tmp_path))["programa"]

    assert stage.state == "done"


def test_programa_stays_done_even_if_a_later_gate_failed(project, tmp_path):
    """Ownership, not correctness: the gates stage carries the verdict."""
    program_dir = tmp_path / project.program_dir
    program_dir.mkdir()
    (program_dir / "main.c").write_text("int main(void) { return 0; }\n")
    (tmp_path / "write_report.json").write_text(
        json.dumps({"accepted": False, "last_error": "acceptance rejected"})
    )

    stage = _by_name(stage_line(project, tmp_path))["programa"]

    assert stage.state == "done"


def test_programa_is_failed_when_the_writer_left_a_report_but_no_source(project, tmp_path):
    (tmp_path / "write_report.json").write_text(
        json.dumps({"accepted": False, "attempts": [], "last_error": "the API call failed"})
    )

    stage = _by_name(stage_line(project, tmp_path))["programa"]

    assert stage.state == "failed"
    assert "the API call failed" in stage.detail


def test_programa_is_failed_rather_than_crashing_on_a_malformed_report(project, tmp_path):
    (tmp_path / "write_report.json").write_text("{not json")

    stages = stage_line(project, tmp_path)  # must not raise

    assert _by_name(stages)["programa"].state == "failed"


# --- gates ------------------------------------------------------------------


def _write_quality_report(tmp_path, **overrides) -> None:
    build_dir = tmp_path / "build"
    build_dir.mkdir(parents=True, exist_ok=True)
    document = {
        "schema_version": 1,
        "gates": {"design": True, "build": True, "runtime": True},
        "quality_pass": True,
    }
    document.update(overrides)
    (build_dir / "studio_quality_report.json").write_text(json.dumps(document))


def test_gates_is_pending_with_no_report(project, tmp_path):
    stage = _by_name(stage_line(project, tmp_path))["gates"]

    assert stage.state == "pending"


def test_gates_is_done_when_the_report_passes(project, tmp_path):
    _write_quality_report(tmp_path)

    stage = _by_name(stage_line(project, tmp_path))["gates"]

    assert stage.state == "done"


def test_gates_is_failed_when_the_report_fails(project, tmp_path):
    _write_quality_report(
        tmp_path,
        gates={"design": True, "build": False, "runtime": False},
        quality_pass=False,
    )

    stage = _by_name(stage_line(project, tmp_path))["gates"]

    assert stage.state == "failed"
    assert "build" in stage.detail
    assert "runtime" in stage.detail


def test_gates_is_failed_rather_than_crashing_on_a_malformed_report(project, tmp_path):
    build_dir = tmp_path / "build"
    build_dir.mkdir(parents=True, exist_ok=True)
    (build_dir / "studio_quality_report.json").write_text("not json at all")

    stages = stage_line(project, tmp_path)  # must not raise

    assert _by_name(stages)["gates"].state == "failed"


# --- release ------------------------------------------------------------


def test_release_is_pending_with_no_archive(project, tmp_path):
    stage = _by_name(stage_line(project, tmp_path))["release"]

    assert stage.state == "pending"


def test_release_is_done_once_the_archive_exists(project, tmp_path):
    releases = tmp_path / "releases"
    releases.mkdir()
    name = f"{project.metadata.slug}-{project.target.platform.value}.zip"
    (releases / name).write_bytes(b"PK\x03\x04")

    stage = _by_name(stage_line(project, tmp_path))["release"]

    assert stage.state == "done"
    assert stage.detail == name


def test_release_is_pending_with_no_directory(project):
    stage = _by_name(stage_line(project, None))["release"]

    assert stage.state == "pending"


# --- next_step: what advances the pipeline right now ------------------------


def test_the_stage_line_no_longer_names_keys():
    """The keys it named are gone; the wizard decides what Enter does."""
    import llmz80.studio.screen as screen

    assert not hasattr(screen, "STAGE_KEY")


def test_the_stage_line_still_names_every_stage_of_the_pipeline(project):
    """What outlived the key map: the order the pipeline runs in, which is
    what `wizard` reads to know which step follows which."""
    assert [stage.name for stage in stage_line(project, None)] == list(STAGE_NAMES)


def test_next_step_is_none_with_no_project():
    assert next_step(stage_line(None, None)) is None


def test_next_step_picks_the_earliest_pending_stage_absent_any_failure(project, tmp_path):
    stages = stage_line(project, tmp_path)  # referencia is the first pending stage

    stage = next_step(stages)

    assert stage is not None
    assert stage.name == "referencia"


def test_next_step_moves_on_as_earlier_stages_complete(project, tmp_path):
    """The hint changes as a project advances -- pinned by naming the stage
    at each of three distinct points along the pipeline, not just the first."""
    fresh = next_step(stage_line(project, tmp_path))
    assert fresh.name == "referencia"

    save_reference(_dossier(), tmp_path)
    researched = next_step(stage_line(project, tmp_path))
    assert researched.name == "sprites"  # diseño already reads done by default

    with_sprite = project.model_copy(update={"assets": [_sprite_asset()]})
    sprited = next_step(stage_line(with_sprite, tmp_path))
    assert sprited.name == "programa"


def test_next_step_prefers_an_earlier_failure_over_a_later_pending_stage(project, tmp_path):
    """A broken design blocks the pipeline even though referencia -- earlier
    in STAGE_NAMES -- is merely unstarted, not broken; pointing at "research"
    while the design does not even fit its target would not fix anything."""
    unfit = _oversized(project)

    stage = next_step(stage_line(unfit, tmp_path))

    assert stage is not None
    assert stage.name == "diseño"


def test_next_step_is_none_once_every_stage_is_done(project, tmp_path):
    save_reference(_dossier(), tmp_path)
    with_sprite = project.model_copy(update={"assets": [_sprite_asset()]})
    program_dir = tmp_path / with_sprite.program_dir
    program_dir.mkdir()
    (program_dir / "main.c").write_text("int main(void) { return 0; }\n")
    _write_quality_report(tmp_path)
    releases = tmp_path / "releases"
    releases.mkdir()
    name = f"{with_sprite.metadata.slug}-{with_sprite.target.platform.value}.zip"
    (releases / name).write_bytes(b"PK\x03\x04")

    stages = stage_line(with_sprite, tmp_path)

    assert all(stage.state == "done" for stage in stages)
    assert next_step(stages) is None
