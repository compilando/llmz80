"""Drawing a sheet by asking the model for the grid, not for a picture.

No network call is made anywhere in this file: `client.messages.parse` is a
fake that returns a grid decided in advance.
"""

import pytest

from llmz80.studio.models import EntitySpec, TargetPlatform, VideoMode
from llmz80.studio.samples import blank_project
from llmz80.studio.sprite_artist import (
    FRAMES_PER_SHEET,
    ClaudeGridSheetSource,
    SpriteArtist,
    SpriteDrawFailure,
    compose_grid_prompt,
)
from llmz80.studio.sprite_grid import (
    TRANSPARENT,
    SpriteFrameGrid,
    SpriteSheetGrid,
    palette_for,
)
from llmz80.studio.spriting import SPRITE_SIZE
from tests.conftest import FakeMessageStream


def _project(platform=TargetPlatform.SPECTRUM, mode=None):
    return blank_project("Grid", platform, mode)


def _entity(**overrides) -> EntitySpec:
    fields = {"id": "hero", "kind": "perseguidor", "sprite": "hero", "notes": ""}
    fields.update(overrides)
    return EntitySpec(**fields)


def _good(fill: str = "0") -> SpriteSheetGrid:
    half = fill * (SPRITE_SIZE // 2) + TRANSPARENT * (SPRITE_SIZE // 2)
    return SpriteSheetGrid(
        frames=[SpriteFrameGrid(rows=[half] * SPRITE_SIZE) for _ in range(FRAMES_PER_SHEET)]
    )


def _short_row() -> SpriteSheetGrid:
    sheet = _good()
    sheet.frames[1].rows[5] = "0" * (SPRITE_SIZE - 1)
    return sheet


class _FakeMessages:
    """Returns each scripted grid in turn, then repeats the last one."""

    def __init__(self, *grids):
        self.grids = list(grids)
        self.calls = []

    def stream(self, **kwargs):
        self.calls.append(kwargs)
        grid = self.grids[min(len(self.calls), len(self.grids)) - 1]
        return FakeMessageStream(type("Response", (), {"parsed_output": grid})())


class _FakeClient:
    def __init__(self, *grids):
        self.messages = _FakeMessages(*grids)


# --- what gets asked --------------------------------------------------------


def test_the_request_asks_for_a_grid_and_says_which_pens_exist():
    project = _project(TargetPlatform.AMSTRAD_CPC, VideoMode.CPC_MODE_0)
    prompt = compose_grid_prompt(project, _entity(), None, palette_for(project))

    assert f"{SPRITE_SIZE} rows" in prompt
    assert "'0'" in prompt and "'3'" in prompt
    assert f"'{TRANSPARENT}' = transparent" in prompt


def test_the_spectrum_is_told_it_has_one_pen_and_the_cpc_that_it_has_four():
    spectrum = _project()
    cpc = _project(TargetPlatform.AMSTRAD_CPC, VideoMode.CPC_MODE_1)

    on_spectrum = compose_grid_prompt(spectrum, _entity(), None, palette_for(spectrum))
    on_cpc = compose_grid_prompt(cpc, _entity(), None, palette_for(cpc))

    assert "'2'" not in on_spectrum
    assert "'2'" in on_cpc


def test_the_contract_is_last_so_a_style_note_cannot_be_the_final_word():
    """Same reasoning as the image path's `_technical_constraints`: what the
    model reads last carries most weight, and a referenced game's palette
    must not be what it reads last."""
    project = _project()

    prompt = compose_grid_prompt(project, _entity(), None, palette_for(project))

    assert prompt.rindex("TECHNICAL REQUIREMENTS") > prompt.rindex("REFERENCE GAME")


def test_the_subject_carries_the_designs_own_words_for_this_actor():
    project = _project()
    entity = _entity(kind="puerta", notes="se abre cuando el jugador lleva la llave")

    prompt = compose_grid_prompt(project, entity, None, palette_for(project))

    assert "puerta" in prompt
    assert "se abre cuando el jugador lleva la llave" in prompt


def test_the_grid_schema_is_what_the_model_is_asked_to_fill():
    source = ClaudeGridSheetSource(_FakeClient(_good()))

    source.draw(_project(), "draw a hero")

    call = source.client.messages.calls[0]
    assert call["output_format"] is SpriteSheetGrid
    assert call["messages"][0]["content"] == "draw a hero"


# --- what comes back --------------------------------------------------------


def test_a_good_grid_becomes_frames_at_the_packers_size():
    source = ClaudeGridSheetSource(_FakeClient(_good()))

    drawn = source.draw(_project(), "draw a hero")

    assert drawn.reason is None
    assert len(drawn.frames) == FRAMES_PER_SHEET
    assert all(frame.size == (SPRITE_SIZE, SPRITE_SIZE) for frame in drawn.frames)


def test_a_malformed_grid_comes_back_as_a_reason_rather_than_an_exception():
    source = ClaudeGridSheetSource(_FakeClient(_short_row()))

    drawn = source.draw(_project(), "draw a hero")

    assert drawn.reason is not None
    assert "frame 2" in drawn.reason and "row 6" in drawn.reason
    assert drawn.frames == []


def test_a_rejected_attempt_still_leaves_a_picture_to_look_at():
    """`services.StudioService._save_raw_sheet` writes this to disk, and the
    run worth having evidence for is precisely the one that failed."""
    source = ClaudeGridSheetSource(_FakeClient(_short_row()))

    drawn = source.draw(_project(), "draw a hero")

    assert drawn.sheet.size[0] > 0 and drawn.sheet.size[1] > 0


# --- and through the artist's own retry loop --------------------------------


def test_a_bad_first_grid_is_redrawn_with_the_reason_appended():
    """The loop `SpriteArtist` already ran for image models works unchanged
    here -- which is the whole point of the source seam."""
    client = _FakeClient(_short_row(), _good())
    artist = SpriteArtist(source=ClaudeGridSheetSource(client))

    frames = artist.draw_frames(_project(), _entity())

    assert len(frames) == FRAMES_PER_SHEET
    assert artist.source.client.messages.calls[1]["messages"][0]["content"].count(
        "REJECTED"
    ) == 1
    assert "row 6" in artist.source.client.messages.calls[1]["messages"][0]["content"]


def test_a_model_that_never_draws_a_valid_grid_fails_with_every_attempt_kept():
    client = _FakeClient(_short_row())
    artist = SpriteArtist(source=ClaudeGridSheetSource(client), attempts=2)

    with pytest.raises(SpriteDrawFailure) as failure:
        artist.draw_frames(_project(), _entity())

    assert len(failure.value.sheets) == 2
    assert len(failure.value.reasons) == 2


# --- what survived the image path, ported to the one that replaced it -------
#
# `tests/test_sprite_artist.py` held 37 tests, nearly all of them about
# recovering a sprite from a picture: background detection, halo tolerance,
# column splitting, aspect fitting. That code is gone, so those tests went
# with it. These are the ones that were never about pictures.


def _dossier():
    from datetime import datetime, timezone

    from llmz80.studio.reference import GameReference, ReferenceSource

    return GameReference(
        identified=True,
        confidence="high",
        title="Manic Miner",
        publisher="Bug-Byte",
        year=1983,
        visual_style="cavernas de colores planos con plataformas de ladrillo",
        sources=[
            ReferenceSource(
                url="https://example.org/manic-miner",
                title="Manic Miner",
                retrieved_at=datetime(1983, 1, 1, tzinfo=timezone.utc),
            )
        ],
    )


def test_the_dossiers_visual_style_and_publisher_reach_the_request():
    project = _project()
    dossier = _dossier()

    prompt = compose_grid_prompt(project, _entity(), dossier, palette_for(project))

    assert dossier.publisher in prompt
    assert dossier.visual_style in prompt


def test_source_urls_never_reach_the_request():
    """A dossier's source URLs are for a person auditing the dossier, not for
    the model -- to it they are noise sitting at the most heavily weighted
    position in the prompt. `compose_grid_prompt` composes its own, shorter
    style block instead of reusing `reference_prompt` wholesale, precisely so
    those URLs never arrive.
    """
    project = _project()
    dossier = _dossier()
    assert dossier.sources, "the fixture must carry sources for this to check anything"

    prompt = compose_grid_prompt(project, _entity(), dossier, palette_for(project))

    for source in dossier.sources:
        assert source.url not in prompt
    assert "Researched from" not in prompt


def _solid() -> SpriteSheetGrid:
    """Every pixel drawn: a 16x16 block, not a shape."""
    return SpriteSheetGrid(
        frames=[
            SpriteFrameGrid(rows=["0" * SPRITE_SIZE] * SPRITE_SIZE)
            for _ in range(FRAMES_PER_SHEET)
        ]
    )


def test_a_solid_block_is_retried_and_the_feedback_names_the_problem():
    """A sheet that packs to a solid block must be redrawn, not packed as-is,
    and the second request must say exactly what was wrong -- the way
    `planner.repair_feedback` names a refused proposal's specific fields
    rather than just saying "try again"."""
    client = _FakeClient(_solid(), _good())
    artist = SpriteArtist(source=ClaudeGridSheetSource(client))

    frames = artist.draw_frames(_project(), _entity())

    assert len(frames) == FRAMES_PER_SHEET
    assert len(client.messages.calls) == 2, "the solid first attempt must be retried once"
    feedback = client.messages.calls[1]["messages"][0]["content"]
    assert "REJECTED" in feedback
    assert "solid" in feedback
    assert frames.attempts == 2
    assert len(frames.repairs) == 1


def test_a_statically_repeated_pose_is_accepted_without_retrying():
    """A collectible like a `pellet` does not animate -- a model drawing it
    identically in all four frames drew it *correctly*, not wrongly. An
    earlier `_judge_frames` refused a sheet whose frames were all identical
    on principle, which cost three wasted generations on exactly this
    response before raising. Only the 0/256 pixel-count check remains.
    """
    client = _FakeClient(_good())
    artist = SpriteArtist(source=ClaudeGridSheetSource(client))

    frames = artist.draw_frames(_project(), _entity(id="pellet", sprite="pellet"))

    assert len(frames) == FRAMES_PER_SHEET
    assert len(client.messages.calls) == 1, "a correctly-static sprite must not be retried"
    assert frames.attempts == 1
    assert len({frame.tobytes() for frame in frames}) == 1, "identical is the point here"


def test_the_artist_narrates_before_the_slow_call_rather_than_only_afterwards():
    """`draw_frames` used to hand its history back only through
    `DrawnFrames.repairs`, readable once the whole call was over. Somebody
    watching a run needs to know an attempt has *started*."""
    client = _FakeClient(_solid(), _good())
    artist = SpriteArtist(source=ClaudeGridSheetSource(client))
    said: list[str] = []

    artist.draw_frames(_project(), _entity(), on_progress=said.append)

    assert any("intento 1" in line and "dibujando" in line for line in said)
    assert any("rechazado" in line for line in said)


# ---------------------------------------------------------------------------
# Terrain artwork reuses this machinery at a different size: 8x8, one frame,
# and a solid block is a legitimate answer for a wall rather than a defect.
# ---------------------------------------------------------------------------


def test_a_tile_grid_is_checked_at_its_own_size():
    from llmz80.studio.sprite_grid import GridPalette, SpriteFrameGrid, SpriteSheetGrid, grid_errors

    palette = GridPalette(pens=((0, 0, 0),))
    tile = SpriteSheetGrid(frames=[SpriteFrameGrid(rows=["0.0.0.0."] * 8)])

    assert grid_errors(tile, palette, frames_expected=1, size=8) is None


def test_a_sixteen_row_frame_is_wrong_when_a_tile_was_asked_for():
    from llmz80.studio.sprite_grid import GridPalette, SpriteFrameGrid, SpriteSheetGrid, grid_errors

    palette = GridPalette(pens=((0, 0, 0),))
    sheet = SpriteSheetGrid(frames=[SpriteFrameGrid(rows=["0" * 16] * 16)])

    problem = grid_errors(sheet, palette, frames_expected=1, size=8)

    assert problem is not None and "8 rows" in problem


def test_a_solid_tile_is_allowed_where_a_solid_sprite_is_not():
    """A wall is a solid block; that is what a wall looks like. The
    no-solid-frames rule exists because a solid *sprite* is a 16x16 brick
    where a figure should be, which is a different claim about a different
    kind of art."""
    from llmz80.studio.sprite_grid import GridPalette, SpriteFrameGrid, SpriteSheetGrid, grid_errors

    palette = GridPalette(pens=((0, 0, 0),))
    solid = SpriteSheetGrid(frames=[SpriteFrameGrid(rows=["0" * 8] * 8)])

    assert grid_errors(solid, palette, frames_expected=1, size=8, solid_allowed=True) is None


def test_a_blank_tile_is_still_refused():
    """Transparent everywhere draws nothing at all, and a tile that draws
    nothing is the character it replaced, minus the character."""
    from llmz80.studio.sprite_grid import GridPalette, SpriteFrameGrid, SpriteSheetGrid, grid_errors

    palette = GridPalette(pens=((0, 0, 0),))
    blank = SpriteSheetGrid(frames=[SpriteFrameGrid(rows=["." * 8] * 8)])

    problem = grid_errors(blank, palette, frames_expected=1, size=8, solid_allowed=True)

    assert problem is not None and "transparent" in problem


def test_a_tile_grid_becomes_an_eight_by_eight_image():
    from llmz80.studio.sprite_grid import (
        GridPalette,
        SpriteFrameGrid,
        SpriteSheetGrid,
        frames_from_grid,
    )

    palette = GridPalette(pens=((0, 0, 0),))
    tile = SpriteSheetGrid(frames=[SpriteFrameGrid(rows=["0" * 8] * 8)])

    frames = frames_from_grid(tile, palette, size=8)

    assert len(frames) == 1
    assert frames[0].size == (8, 8)
