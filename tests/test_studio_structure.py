"""Studio validates that a design refers to itself consistently. Nothing else."""

from copy import deepcopy

import pytest
from pydantic import ValidationError

from llmz80.studio.models import GameProject, TargetPlatform
from llmz80.studio.samples import blank_project


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
    assert "undeclared tile character 'X'" in _refused(broken)


def test_two_tiles_cannot_share_a_character(document):
    broken = deepcopy(document)
    broken["tiles"].append({"id": "otra", "char": broken["tiles"][0]["char"], "traits": []})
    assert "two tiles share the character" in _refused(broken)


def test_a_spawn_must_name_a_declared_entity(document):
    broken = deepcopy(document)
    broken["screens"][0]["spawns"][0]["entity"] = "fantasma"
    assert "spawns unknown entity 'fantasma'" in _refused(broken)


def test_a_screen_cannot_place_more_of_an_entity_than_it_declares(document):
    broken = deepcopy(document)
    spawn = dict(broken["screens"][0]["spawns"][0])
    spawn["col"] += 1
    broken["screens"][0]["spawns"].append(spawn)
    assert "places hero 2 times but declares 1" in _refused(broken)


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


def test_an_observable_cannot_shadow_a_contract_symbol(document):
    broken = deepcopy(document)
    broken["observables"] = [{"symbol": "g_score", "width": 2, "meaning": "otra cosa"}]
    assert "already in the state contract" in _refused(broken)


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
