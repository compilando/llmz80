"""The v4 IR declares its own vocabulary instead of inheriting one."""

import pytest
from pydantic import ValidationError

from llmz80.studio.models import (
    AssetSpec,
    AudioSpec,
    ControlsSpec,
    EntitySpec,
    ObservableSpec,
    PresentationSpec,
    ScreenSpec,
    TargetPlatform,
    TargetSpec,
    TileSpec,
    VideoMode,
)


def test_a_tile_declares_its_own_character_and_free_traits():
    tile = TileSpec(id="escalera", char="H", traits=["climbable", "no_solid"])
    assert tile.char == "H"
    assert tile.traits == ["climbable", "no_solid"]


def test_a_tile_character_is_exactly_one_printable_character():
    with pytest.raises(ValidationError, match="char"):
        TileSpec(id="ancho", char="HH")
    with pytest.raises(ValidationError, match="char"):
        TileSpec(id="vacio", char="")
    with pytest.raises(ValidationError, match="char"):
        TileSpec(id="blanco", char=" ")
    with pytest.raises(ValidationError, match="char"):
        TileSpec(id="acento", char="ñ")
    with pytest.raises(ValidationError, match="char"):
        TileSpec(id="comilla", char="'")
    with pytest.raises(ValidationError, match="char"):
        TileSpec(id="barra", char="\\")


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
    with pytest.raises(ValidationError, match="at most 8 items"):
        ControlsSpec(bindings={f"key{index}": "SPACE" for index in range(9)})


def test_a_binding_name_must_be_a_usable_identifier():
    with pytest.raises(ValidationError, match="not a usable identifier"):
        ControlsSpec(bindings={"1jump": "SPACE"})
    with pytest.raises(ValidationError, match="not a usable identifier"):
        ControlsSpec(bindings={"Jump": "SPACE"})


def test_a_binding_key_must_be_a_recognized_label():
    with pytest.raises(ValidationError, match="recognized key label"):
        ControlsSpec(bindings={"jump": "F1"})
    with pytest.raises(ValidationError, match="recognized key label"):
        ControlsSpec(bindings={"jump": "space"})


def test_two_bindings_cannot_share_one_key():
    with pytest.raises(ValidationError, match="bound to more than one action"):
        ControlsSpec(bindings={"left": "O", "jump": "O"})


def test_an_observable_must_look_like_a_contract_symbol():
    observable = ObservableSpec(symbol="g_keys", width=1, meaning="llaves recogidas")
    assert observable.symbol == "g_keys"
    with pytest.raises(ValidationError, match="symbol"):
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
    with pytest.raises(ValidationError, match="characters"):
        ScreenSpec(
            id="rota",
            name="ROTA",
            width=8,
            height=8,
            tiles=["#######", "#......#", "#......#", "#......#",
                   "#......#", "#......#", "#......#", "########"],
            spawns=[{"entity": "hero", "col": 1, "row": 1}],
        )


def test_a_screen_with_the_wrong_number_of_rows_is_refused():
    # One row over height=8, but still >= the field's own min_length=8, so
    # this exercises validate_grid's own count check, not the field bound.
    with pytest.raises(ValidationError, match="rows"):
        ScreenSpec(
            id="filas_de_mas",
            name="FILAS DE MAS",
            width=8,
            height=8,
            tiles=["########", "#......#", "#......#", "#......#",
                   "#......#", "#......#", "#......#", "#......#",
                   "########"],
            spawns=[{"entity": "hero", "col": 1, "row": 1}],
        )


def test_a_spawn_outside_the_grid_is_refused():
    with pytest.raises(ValidationError, match="outside its"):
        ScreenSpec(
            id="spawn_fuera",
            name="SPAWN FUERA",
            width=8,
            height=8,
            tiles=["########", "#......#", "#......#", "#......#",
                   "#......#", "#......#", "#......#", "########"],
            spawns=[{"entity": "hero", "col": 20, "row": 1}],
        )


def test_a_target_must_pair_its_platform_with_its_own_video_modes():
    TargetSpec(platform=TargetPlatform.SPECTRUM, video_mode=VideoMode.SPECTRUM_BITMAP)
    with pytest.raises(ValidationError, match="only has spectrum_bitmap"):
        TargetSpec(platform=TargetPlatform.SPECTRUM, video_mode=VideoMode.CPC_MODE_0)
    with pytest.raises(ValidationError, match="cpc_mode_0 and cpc_mode_1"):
        TargetSpec(platform=TargetPlatform.AMSTRAD_CPC, video_mode=VideoMode.SPECTRUM_BITMAP)


def test_an_asset_sheet_must_hold_whole_frames():
    AssetSpec(id="hero", kind="sprite", source="assets/hero.png", width=32, height=16, frames=2)
    with pytest.raises(ValidationError, match="cannot hold"):
        AssetSpec(id="hero", kind="sprite", source="assets/hero.png", width=33, height=16, frames=2)


def test_audio_effects_must_be_unique():
    AudioSpec(music=True, effects=["collect", "hit"])
    with pytest.raises(ValidationError, match="unique"):
        AudioSpec(effects=["collect", "collect"])


def test_the_removed_vocabulary_is_really_gone():
    import llmz80.studio.models as models

    for name in ("GenreId", "ProjectKind", "ProjectScope", "GameplaySpec",
                 "LevelSpec", "AcceptanceScenario", "TILE_WALL", "TILE_FLOOR",
                 "SceneKind", "AUDIO_EFFECTS"):
        assert not hasattr(models, name), f"{name} survives the v4 cut"


def test_a_design_string_carrying_the_json_object_separator_is_refused():
    """The `},{` incident, in the two fields it actually landed in.

    `kind` is the one that motivated widening `Prose`: it carries the design's
    own free-written word for an actor, nothing else constrains it, and
    `studio-projects/minero-vigilado` reached the program writer with
    `minero},{` in it. `style` is the other casualty, and `mechanics` is
    checked too because it is the field the same failure hit with NUL bytes
    the first time round.
    """
    for separator in ("},{", "}, {", "},\n{"):
        with pytest.raises(ValidationError, match="JSON separator"):
            EntitySpec(id="minero", kind="minero" + separator)
    with pytest.raises(ValidationError, match="JSON separator"):
        PresentationSpec(style="plain walls, minimal detail, tiny sprites},{")
    with pytest.raises(ValidationError, match="JSON separator"):
        ObservableSpec(symbol="g_dug", meaning="celdas cavadas},{")


def test_a_brace_a_design_meant_to_write_is_still_allowed():
    """The refusal is the separator, not the character.

    Refusing every brace would be cheap and would fail honest prose: a mechanic
    is free to describe a `{` on the screen or in a key legend, and a design
    that does is not corrupt. Nothing may start refusing legitimate designs is
    the bar this guards.
    """
    assert PresentationSpec(style="HUD in {braces}, sprites in blue").style
    assert EntitySpec(id="llave", kind="{llave}").kind == "{llave}"
    assert ObservableSpec(symbol="g_dug", meaning="celdas cavadas {solo sube}, nunca baja").meaning


def test_a_design_string_carrying_a_control_character_is_refused():
    """The first incident of this kind, which had a guard and no test: the
    adaptation stage returned mechanics with NUL bytes where accented
    characters belonged, and `studio-projects/un-minero-que-cava-tuneles-y`
    could not be loaded at all afterwards."""
    with pytest.raises(ValidationError, match="control character"):
        EntitySpec(id="minero", kind="pulsaci\0n")
    # Tab, newline and carriage return stay legal: prose may wrap.
    assert EntitySpec(id="minero", kind="mine\tro").kind == "mine\tro"
