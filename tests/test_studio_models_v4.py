"""The v4 IR declares its own vocabulary instead of inheriting one."""

import pytest
from pydantic import ValidationError

from llmz80.studio.models import (
    ControlsSpec,
    EntitySpec,
    ObservableSpec,
    ScreenSpec,
    TileSpec,
)


def test_a_tile_declares_its_own_character_and_free_traits():
    tile = TileSpec(id="escalera", char="H", traits=["climbable", "no_solid"])
    assert tile.char == "H"
    assert tile.traits == ["climbable", "no_solid"]


def test_a_tile_character_is_exactly_one_printable_character():
    with pytest.raises(ValidationError):
        TileSpec(id="ancho", char="HH")
    with pytest.raises(ValidationError):
        TileSpec(id="vacio", char="")


def test_an_entity_kind_is_free_vocabulary_not_a_role():
    entity = EntitySpec(id="momia", kind="perseguidor", sprite="momia", count=3)
    assert entity.kind == "perseguidor"


def test_an_entity_may_name_its_poses():
    entity = EntitySpec(id="hero", kind="explorador", poses=["walk", "jump", "die"])
    assert entity.poses == ["walk", "jump", "die"]


def test_bindings_are_named_by_the_design_not_by_studio():
    controls = ControlsSpec(bindings={"left": "O", "right": "P", "jump": "SPACE"})
    assert controls.bindings["jump"] == "SPACE"


def test_more_than_eight_bindings_do_not_fit_one_input_byte():
    with pytest.raises(ValidationError):
        ControlsSpec(bindings={f"key{index}": "SPACE" for index in range(9)})


def test_an_observable_must_look_like_a_contract_symbol():
    observable = ObservableSpec(symbol="g_keys", width=1, meaning="llaves recogidas")
    assert observable.symbol == "g_keys"
    with pytest.raises(ValidationError):
        ObservableSpec(symbol="keys", width=1, meaning="sin prefijo")


def test_a_screen_carries_its_exits():
    screen = ScreenSpec(
        id="sala_1",
        name="SALA 1",
        width=8,
        height=8,
        tiles=["########", "#......#", "#......#", "#......#",
               "#......#", "#......#", "#......#", "########"],
        spawns=[{"entity": "hero", "col": 1, "row": 1}],
        exits={"right": "sala_2"},
    )
    assert screen.exits == {"right": "sala_2"}


def test_a_screen_row_that_is_not_its_declared_width_is_refused():
    with pytest.raises(ValidationError):
        ScreenSpec(
            id="rota",
            name="ROTA",
            width=8,
            height=8,
            tiles=["#######", "#......#", "#......#", "#......#",
                   "#......#", "#......#", "#......#", "########"],
            spawns=[{"entity": "hero", "col": 1, "row": 1}],
        )


def test_the_removed_vocabulary_is_really_gone():
    import llmz80.studio.models as models

    for name in ("GenreId", "ProjectKind", "ProjectScope", "GameplaySpec",
                 "LevelSpec", "AcceptanceScenario", "TILE_WALL", "TILE_FLOOR"):
        assert not hasattr(models, name), f"{name} survives the v4 cut"
