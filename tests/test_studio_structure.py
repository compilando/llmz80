"""Studio validates that a design refers to itself consistently. Nothing else."""

from copy import deepcopy

import pytest
from pydantic import ValidationError

from llmz80.studio.models import GameProject, TargetPlatform, VideoMode
from llmz80.studio.samples import blank_project
from llmz80.studio.structure import structural_errors


@pytest.fixture()
def document() -> dict:
    return blank_project("Structural", TargetPlatform.SPECTRUM).model_dump(mode="json")


def _refused(document: dict) -> str:
    with pytest.raises(ValidationError) as error:
        GameProject.model_validate(document)
    return str(error.value)


def test_the_blank_project_is_structurally_valid(document):
    assert GameProject.model_validate(document).metadata.title == "Structural"


def test_a_screen_character_with_no_declared_tile_is_refused(document):
    broken = deepcopy(document)
    rows = broken["screens"][0]["tiles"]
    rows[1] = "X" + rows[1][1:]
    assert "undeclared tile characters 'X'" in _refused(broken)


def test_every_undeclared_character_on_a_screen_is_reported(document):
    """One error per screen, but it must not drop characters past the first."""
    broken = deepcopy(document)
    rows = broken["screens"][0]["tiles"]
    rows[1] = "X" + rows[1][1:-1] + "Y"
    message = _refused(broken)
    assert "'X'" in message
    assert "'Y'" in message


def test_two_tiles_cannot_share_a_character(document):
    broken = deepcopy(document)
    broken["tiles"].append({"id": "otra", "char": broken["tiles"][0]["char"], "traits": []})
    assert "two tiles share the character" in _refused(broken)


def test_a_duplicate_tile_id_is_refused(document):
    broken = deepcopy(document)
    original = broken["tiles"][0]
    broken["tiles"].append({"id": original["id"], "char": "$", "traits": []})
    assert f"tile id {original['id']!r} is declared 2 times" in _refused(broken)


def test_a_tile_art_must_name_a_declared_asset(document):
    broken = deepcopy(document)
    broken["tiles"][0]["art"] = "missing_art"
    assert "names undeclared asset 'missing_art'" in _refused(broken)


def test_a_spawn_must_name_a_declared_entity(document):
    broken = deepcopy(document)
    broken["screens"][0]["spawns"][0]["entity"] = "fantasma"
    assert "spawns unknown entity 'fantasma'" in _refused(broken)


def test_a_screen_cannot_place_more_of_an_entity_than_it_declares(document):
    broken = deepcopy(document)
    spawn = dict(broken["screens"][0]["spawns"][0])
    spawn["col"] += 1
    broken["screens"][0]["spawns"].append(spawn)
    assert "places 'actor' 2 times but declares 1" in _refused(broken)


def test_a_duplicate_entity_id_is_refused(document):
    broken = deepcopy(document)
    original = broken["entities"][0]
    broken["entities"].append({"id": original["id"], "kind": "actor"})
    assert f"entity id {original['id']!r} is declared 2 times" in _refused(broken)


def test_an_entity_sprite_must_name_a_declared_asset(document):
    broken = deepcopy(document)
    broken["entities"][0]["sprite"] = "missing_sprite"
    assert "names undeclared asset 'missing_sprite'" in _refused(broken)


def test_an_entity_colour_must_name_a_declared_palette_entry(document):
    broken = deepcopy(document)
    broken["entities"][0]["colour"] = "verde"
    assert "names undeclared palette entry 'verde'" in _refused(broken)


def test_an_exit_must_lead_to_a_screen_that_exists(document):
    broken = deepcopy(document)
    broken["screens"][0]["exits"] = {"right": "cripta"}
    assert "exits right to unknown screen 'cripta'" in _refused(broken)


def test_the_initial_screen_must_exist(document):
    broken = deepcopy(document)
    broken["initial_screen"] = "ninguna"
    assert "initial_screen names no declared screen" in _refused(broken)


def test_a_screen_wider_than_the_playfield_is_refused(document):
    broken = deepcopy(document)
    screen = broken["screens"][0]
    screen["width"] = 40
    screen["tiles"] = [row.ljust(40, row[-1]) for row in screen["tiles"]]
    assert "offers" in _refused(broken)


def test_hud_rows_shrinks_the_playfield_a_full_screen_no_longer_fits(document):
    """`hud_rows` replaces the old hard-coded FIELD_TOP=2: at its default the
    Spectrum's 24-row screen leaves only 22 playable rows."""
    broken = deepcopy(document)
    screen = broken["screens"][0]
    screen["height"] = 23
    screen["width"] = 32
    screen["tiles"] = ["#" * 32] + ["#" + "." * 30 + "#"] * 21 + ["#" * 32]
    screen["spawns"][0].update(col=16, row=11)
    assert "offers 32x22" in _refused(broken)


def test_hud_rows_zero_frees_the_whole_spectrum_screen(document):
    """A design that shows neither score nor lives gets its two rows back."""
    tolerated = deepcopy(document)
    tolerated["presentation"]["hud_rows"] = 0
    screen = tolerated["screens"][0]
    screen["height"] = 23
    screen["width"] = 32
    screen["tiles"] = ["#" * 32] + ["#" + "." * 30 + "#"] * 21 + ["#" * 32]
    screen["spawns"][0].update(col=16, row=11)
    assert GameProject.model_validate(tolerated)


def test_a_screen_must_fit_the_cpc_mode_0_playfield_too():
    """All prior playfield tests are Spectrum; cpc_mode_0's 20-column grid is
    the tightest of the three targets and exercises the same check."""
    cpc_document = blank_project(
        "Structural", TargetPlatform.AMSTRAD_CPC, VideoMode.CPC_MODE_0
    ).model_dump(mode="json")
    assert GameProject.model_validate(cpc_document)
    broken = deepcopy(cpc_document)
    screen = broken["screens"][0]
    screen["width"] = 21
    screen["tiles"] = [row + row[-1] for row in screen["tiles"]]
    assert "cpc_mode_0 offers 20x" in _refused(broken)


def test_an_observable_cannot_shadow_a_contract_symbol(document):
    broken = deepcopy(document)
    broken["observables"] = [{"symbol": "g_score", "width": 2, "meaning": "otra cosa"}]
    assert "already in the state contract" in _refused(broken)


def test_an_observable_declared_twice_is_refused(document):
    broken = deepcopy(document)
    observable = {"symbol": "g_combo", "width": 1, "meaning": "combo streak"}
    broken["observables"] = [observable, dict(observable)]
    assert "observable 'g_combo' is declared 2 times" in _refused(broken)


def test_a_tile_colour_must_name_a_declared_palette_entry(document):
    broken = deepcopy(document)
    broken["tiles"][0]["colour"] = "verde"
    assert "names undeclared palette entry 'verde'" in _refused(broken)


def test_spawns_beyond_the_entity_budget_are_refused(document):
    broken = deepcopy(document)
    broken["budgets"]["max_entities"] = 1
    broken["entities"].append({"id": "momia", "kind": "perseguidor", "count": 4})
    screen = broken["screens"][0]
    screen["spawns"] += [{"entity": "momia", "col": 3 + index, "row": 3} for index in range(4)]
    assert "exceeds the max_entities budget" in _refused(broken)


def test_duplicate_scene_ids_are_refused(document):
    broken = deepcopy(document)
    broken["scenes"].append(dict(broken["scenes"][0]))
    assert "scene id 'title' is declared 2 times" in _refused(broken)


def test_initial_scene_must_name_a_declared_scene(document):
    broken = deepcopy(document)
    broken["initial_scene"] = "ninguna"
    assert "initial_scene must reference an existing scene: 'ninguna'" in _refused(broken)


def test_a_scenes_next_scene_must_name_a_declared_scene(document):
    broken = deepcopy(document)
    broken["scenes"][1]["next_scene"] = "ninguna"
    assert "next_scene names unknown scene 'ninguna'" in _refused(broken)


def test_a_menu_options_target_scene_must_name_a_declared_scene(document):
    broken = deepcopy(document)
    broken["scenes"][0]["options"][0]["target_scene"] = "ninguna"
    assert "targets unknown scene 'ninguna'" in _refused(broken)


def test_studio_does_not_care_what_a_trait_means(document):
    tolerated = deepcopy(document)
    tolerated["tiles"][0]["traits"] = ["solid", "deadly", "sticky"]
    assert GameProject.model_validate(tolerated).tiles[0].traits[2] == "sticky"


def test_a_spawn_on_a_solid_tile_is_the_programs_business_not_studios(document):
    """The old IR refused this. `solid` has no meaning here, so neither does the
    refusal: a design may legitimately start an actor inside what it calls a wall."""
    tolerated = deepcopy(document)
    wall = tolerated["tiles"][0]["char"]
    tolerated["screens"][0]["spawns"][0].update(col=0, row=0)
    assert tolerated["screens"][0]["tiles"][0][0] == wall
    assert GameProject.model_validate(tolerated)


def test_structural_errors_reports_every_failure_not_just_the_first():
    """`structural_errors` is a plain function over a `GameProject`, called
    directly here (bypassing `model_validate`, which would stop at the first
    pydantic-level problem) to check its own contract: every failure comes
    back, not only the one that would be raised first."""
    project = blank_project("Structural", TargetPlatform.SPECTRUM)
    # `model_copy(update=...)` sets fields without re-running validators, so
    # this builds a `GameProject` carrying two independent structural faults
    # at once -- something `GameProject.model_validate` could never hand us,
    # since it refuses to construct an invalid instance in the first place.
    broken = project.model_copy(update={"initial_screen": "ninguna", "initial_scene": "ninguna"})
    errors = structural_errors(broken)
    assert any("initial_screen" in error for error in errors)
    assert any("initial_scene" in error for error in errors)
    assert len(errors) == 2
