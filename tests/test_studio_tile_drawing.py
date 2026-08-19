"""Drawing the terrain the design asked to be drawn.

The asymmetry this closes: an entity has always had artwork drawn for it, so a
game's actors were pixels while its terrain was letters. Nothing was missing
from the *design* -- `TileSpec.art` existed -- but no stage ever filled it in,
and it could not have been filled in by hand either: `structure.py` refuses a
document whose `tile.art` names an asset that does not exist yet, exactly as it
refuses `entity.sprite` doing the same. So the design says what it wants drawn
in words (`TileSpec.art_note`) and the drawing stage is what turns that into an
asset and a filled-in `art`, both in the same breath, the way
`services.draw_sprites` already does for an entity.
"""

from pathlib import Path

from PIL import Image

from llmz80.studio.models import TargetPlatform, TileSpec
from llmz80.studio.services import StudioService
from llmz80.studio.sprite_artist import DrawnFrames, DrawnSheet
from llmz80.studio.spriting import TILE_SIZE


def test_a_tile_declares_what_it_should_look_like_and_that_is_what_asks_for_art():
    """A tile with a note wants artwork; one without stays its character.
    Empty space is the case that must stay a character: there is nothing to
    draw, and a stage that drew every tile would spend a model call producing
    a blank."""
    blank = TileSpec(id="floor", char=".")
    brick = TileSpec(id="ladrillo", char="B", art_note="brickwork, mortar lines between courses")

    assert blank.art_note == ""
    assert brick.wants_art is True
    assert blank.wants_art is False


class _FakeTileArtist:
    """Answers with one 8x8 tile, recording which tiles it was asked for."""

    def __init__(self) -> None:
        self.asked: list[str] = []

    def draw_tile(self, project, tile, dossier=None, *, on_progress=None) -> DrawnFrames:
        self.asked.append(tile.id)
        image = Image.new("RGBA", (TILE_SIZE, TILE_SIZE), (0, 0, 0, 0))
        pixels = image.load()
        for y in range(TILE_SIZE):
            for x in range(TILE_SIZE):
                if (x + y) % 2 == 0:
                    pixels[x, y] = (255, 255, 255, 255)
        return DrawnFrames([image], sheet=image, sheets=[image], attempts=1, repairs=[])


def _project_with_terrain(tmp_path: Path):
    service = StudioService.at(tmp_path / "projects")
    project, directory = service.create_project("Terrain", TargetPlatform.SPECTRUM)
    project.tiles[0].art_note = "brickwork, mortar lines between courses"
    return service, project, directory


def test_drawing_registers_the_art_and_fills_in_the_tile_that_wears_it(tmp_path: Path):
    service, project, directory = _project_with_terrain(tmp_path)
    artist = _FakeTileArtist()

    drawn = service.draw_tiles(project, directory, artist)

    assert [asset.id for asset in drawn] == [project.tiles[0].id]
    assert project.tiles[0].art == project.tiles[0].id
    registered = next(asset for asset in project.assets if asset.id == project.tiles[0].id)
    assert registered.kind == "tileset"
    assert (registered.width, registered.height) == (TILE_SIZE, TILE_SIZE)
    assert (directory / registered.source).is_file()


def test_a_tile_that_asked_for_nothing_is_left_as_its_character(tmp_path: Path):
    service, project, directory = _project_with_terrain(tmp_path)
    plain = [tile.id for tile in project.tiles if not tile.wants_art]
    assert plain  # the blank project has more than one tile
    artist = _FakeTileArtist()

    service.draw_tiles(project, directory, artist)

    assert artist.asked == [project.tiles[0].id]
    for tile in project.tiles:
        if tile.id in plain:
            assert tile.art is None


def test_art_already_on_disk_is_never_redrawn(tmp_path: Path):
    """Same rule `draw_sprites` follows: a caller that wants terrain redrawn
    removes the asset first, so from here that tile is simply missing art."""
    service, project, directory = _project_with_terrain(tmp_path)
    service.draw_tiles(project, directory, _FakeTileArtist())

    second = _FakeTileArtist()
    drawn_again = service.draw_tiles(project, directory, second)

    assert drawn_again == []
    assert second.asked == []


def test_the_saved_project_round_trips_with_its_terrain_art(tmp_path: Path):
    """The state this used to be unable to reach: a tile pointing at an asset
    that really exists. If either half were saved without the other,
    `structure.py` would refuse the document on the way back in."""
    service, project, directory = _project_with_terrain(tmp_path)
    service.draw_tiles(project, directory, _FakeTileArtist())

    reopened = service.open_project(directory)

    tile = next(tile for tile in reopened.tiles if tile.id == project.tiles[0].id)
    assert tile.art == tile.id


class _RefusingTileArtist:
    def draw_tile(self, project, tile, dossier=None, *, on_progress=None):
        raise ValueError("the tile could not be drawn in 3 attempts")


def test_a_tile_that_cannot_be_drawn_leaves_the_design_untouched(tmp_path: Path):
    """Nothing half-written reaches disk: `tile.art` is only ever set beside
    the asset that backs it."""
    service, project, directory = _project_with_terrain(tmp_path)

    try:
        service.draw_tiles(project, directory, _RefusingTileArtist())
    except ValueError:
        pass
    else:  # pragma: no cover - the fake always raises
        raise AssertionError("the refusal should have propagated")

    reopened = service.open_project(directory)
    assert all(tile.art is None for tile in reopened.tiles)


def test_the_tile_prompt_says_what_the_terrain_is_and_asks_for_one_cell():
    from llmz80.studio.samples import blank_project
    from llmz80.studio.sprite_artist import compose_tile_prompt
    from llmz80.studio.sprite_grid import palette_for

    project = blank_project("Terrain", TargetPlatform.SPECTRUM)
    tile = TileSpec(
        id="ladrillo",
        char="B",
        art_note="brickwork, mortar lines between courses",
        traits=["solid", "breakable"],
    )

    prompt = compose_tile_prompt(project, tile, None, palette_for(project))

    assert "brickwork, mortar lines between courses" in prompt
    assert "ladrillo" in prompt
    assert "solid, breakable" in prompt
    assert f"{TILE_SIZE} rows of exactly {TILE_SIZE}" in prompt
    # A tile tiles: the edges have to meet the cell next door.
    assert "edge" in prompt
    # And unlike a sprite, a filled block is a legitimate answer for a wall.
    assert "1 frame" in prompt


class _GridClient:
    """Stands in for the model: answers with one 8x8 grid of pen characters."""

    def __init__(self, rows: list[str]) -> None:
        self.rows = rows
        self.messages = self

    def stream(self, **_kwargs):
        from llmz80.studio.sprite_grid import SpriteFrameGrid, SpriteSheetGrid
        from tests.conftest import FakeMessageStream, fake_message

        sheet = SpriteSheetGrid(frames=[SpriteFrameGrid(rows=self.rows)])
        return FakeMessageStream(fake_message(sheet))


def test_a_solid_tile_comes_back_accepted(tmp_path: Path):
    """A wall is a solid block. The sprite path refuses one and is right to;
    terrain is the case that rule was never about."""
    from llmz80.studio.samples import blank_project
    from llmz80.studio.sprite_artist import ClaudeGridTileSource

    source = ClaudeGridTileSource(_GridClient(["0" * TILE_SIZE] * TILE_SIZE))
    project = blank_project("Wall", TargetPlatform.SPECTRUM)

    drawn: DrawnSheet = source.draw(project, "draw a wall")

    assert drawn.reason is None
    assert len(drawn.frames) == 1
    assert drawn.frames[0].size == (TILE_SIZE, TILE_SIZE)


def test_a_blank_tile_is_refused_with_a_reason_the_next_attempt_can_act_on(tmp_path: Path):
    from llmz80.studio.samples import blank_project
    from llmz80.studio.sprite_artist import ClaudeGridTileSource

    source = ClaudeGridTileSource(_GridClient(["." * TILE_SIZE] * TILE_SIZE))
    project = blank_project("Nothing", TargetPlatform.SPECTRUM)

    drawn = source.draw(project, "draw a wall")

    assert drawn.reason is not None and "transparent" in drawn.reason
    assert drawn.frames == []
