"""SpriteArtist, judged on the prompt it writes and the frames it returns.

No API call is made anywhere in this file: every generator is a fake that
returns a fixed, in-memory image, exactly like `test_studio_generator.py` does
for `ResponsesProgramWriter`'s client.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from PIL import Image

from llmz80.studio.models import GameProject, GenreId, TargetPlatform, VideoMode
from llmz80.studio.packs import create_default_project
from llmz80.studio.reference import GameReference, ReferenceSource
from llmz80.studio.sprite_artist import (
    FRAMES_PER_SHEET,
    REQUEST_HEIGHT,
    REQUEST_WIDTH,
    SHEET_HEIGHT,
    SHEET_WIDTH,
    SpriteArtist,
    compose_prompt,
)
from llmz80.studio.spriting import SPRITE_SIZE


class _FakeGenerator:
    """Returns one fixed image and remembers every prompt it was asked for."""

    def __init__(self, image: Image.Image) -> None:
        self.image = image
        self.prompts: list[str] = []

    def generate_image(self, prompt: str) -> Image.Image:
        self.prompts.append(prompt)
        return self.image


def _project(platform: TargetPlatform = TargetPlatform.SPECTRUM) -> GameProject:
    return create_default_project("Test Game", platform, GenreId.MAZE_CHASE)


def _cpc_mode0_project() -> GameProject:
    """`create_default_project` always builds CPC projects in mode 1; mode 0
    is reached the same way `test_studio_models.py` reaches an alternate
    video mode -- dump, edit, revalidate -- since nothing else in Studio
    constructs one directly.
    """
    data = _project(TargetPlatform.AMSTRAD_CPC).model_dump()
    data["target"]["video_mode"] = VideoMode.CPC_MODE_0
    return GameProject.model_validate(data)


def _dossier(**overrides: object) -> GameReference:
    fields = dict(
        identified=True,
        confidence="high",
        title="Jet Set Willy",
        publisher="Software Projects",
        year=1984,
        platforms=["ZX Spectrum"],
        visual_style="Flat colour rooms, black outlines, one attribute clash per room.",
        sources=[
            ReferenceSource(
                url="https://example.com/jsw",
                title="MobyGames",
                retrieved_at=datetime.now(timezone.utc),
            )
        ],
    )
    fields.update(overrides)
    return GameReference(**fields)


def _solid_image(size: tuple[int, int], colour: tuple[int, int, int, int]) -> Image.Image:
    return Image.new("RGBA", size, colour)


# --- The composed prompt ----------------------------------------------------


def test_prompt_carries_the_dossiers_visual_style_and_publisher():
    project = _project()
    entity = next(e for e in project.entities if e.role == "enemy")
    dossier = _dossier()

    prompt = compose_prompt(project, entity, dossier)

    assert dossier.publisher in prompt
    assert dossier.visual_style in prompt


def test_prompt_states_the_spectrums_monochrome_constraint():
    project = _project(TargetPlatform.SPECTRUM)
    entity = next(e for e in project.entities if e.role == "player")

    prompt = compose_prompt(project, entity, None)

    assert "monochrome" in prompt.lower()


def test_prompt_states_cpc_mode0s_sixteen_pens():
    project = _cpc_mode0_project()
    entity = next(e for e in project.entities if e.role == "player")

    prompt = compose_prompt(project, entity, None)

    assert "16-color" in prompt


def test_prompt_states_cpc_mode1s_four_pens():
    project = _project(TargetPlatform.AMSTRAD_CPC)  # create_default_project builds mode 1
    assert project.target.video_mode is VideoMode.CPC_MODE_1
    entity = next(e for e in project.entities if e.role == "player")

    prompt = compose_prompt(project, entity, None)

    assert "4-color" in prompt


def test_prompt_asks_for_a_four_frame_sheet_at_the_requested_size():
    project = _project()
    entity = next(e for e in project.entities if e.role == "player")

    prompt = compose_prompt(project, entity, None)

    assert str(FRAMES_PER_SHEET) in prompt
    assert f"{REQUEST_WIDTH}x{REQUEST_HEIGHT}" in prompt


def test_prompt_without_a_dossier_falls_back_to_role_and_presentation_style():
    project = _project()
    entity = next(e for e in project.entities if e.role == "enemy")

    prompt = compose_prompt(project, entity, dossier=None)

    assert entity.role in prompt
    assert project.presentation.style in prompt


def test_prompt_with_an_unidentified_dossier_also_falls_back():
    """An unidentified dossier's `visual_style`/`publisher` are blank by
    construction (see `reference.RESEARCH_SYSTEM_PROMPT`), so it carries
    nothing to quote -- the fallback used for no dossier at all applies here
    too.
    """
    project = _project()
    entity = next(e for e in project.entities if e.role == "enemy")
    unidentified = GameReference(identified=False, confidence="low")

    prompt = compose_prompt(project, entity, unidentified)

    assert entity.role in prompt
    assert project.presentation.style in prompt


# --- Frames returned by SpriteArtist ----------------------------------------


def test_draw_frames_returns_four_sprite_sized_frames():
    project = _project()
    entity = next(e for e in project.entities if e.role == "player")
    image = _solid_image((900, 900), (255, 255, 255, 255))
    pixels = image.load()
    for y in range(300, 600):
        for x in range(200, 700):
            pixels[x, y] = (255, 0, 0, 255)
    artist = SpriteArtist(_FakeGenerator(image))

    frames = artist.draw_frames(project, entity)

    assert len(frames) == FRAMES_PER_SHEET
    assert all(frame.size == (SPRITE_SIZE, SPRITE_SIZE) for frame in frames)


def test_draw_frames_asks_the_generator_for_the_composed_prompt():
    project = _project()
    entity = next(e for e in project.entities if e.role == "player")
    generator = _FakeGenerator(_solid_image((512, 128), (0, 0, 0, 255)))
    artist = SpriteArtist(generator)

    artist.draw_frames(project, entity)

    assert generator.prompts == [compose_prompt(project, entity, None)]


@pytest.mark.parametrize(
    "size,colour",
    [
        ((1, 1), (10, 20, 30, 255)),
        ((37, 501), (10, 20, 30, 255)),
        ((2000, 2000), (10, 20, 30, 255)),
        ((500, 500), (255, 255, 255, 255)),  # entirely background: no object at all
    ],
)
def test_a_wrongly_sized_image_still_yields_valid_frames(
    size: tuple[int, int], colour: tuple[int, int, int, int]
):
    """Neither a tiny image, an oddly-proportioned one, an oversized one, nor
    one with nothing drawn on it (all background) should ever reach
    `split_frames` in a shape it cannot cut cleanly -- `draw_frames` forces the
    sheet to its real, final size before splitting, precisely so a
    badly-sized response cannot silently produce broken frames.
    """
    project = _project()
    entity = next(e for e in project.entities if e.role == "player")
    artist = SpriteArtist(_FakeGenerator(_solid_image(size, colour)))

    frames = artist.draw_frames(project, entity)

    assert len(frames) == FRAMES_PER_SHEET
    assert all(frame.size == (SPRITE_SIZE, SPRITE_SIZE) for frame in frames)


def test_the_sheet_and_request_sizes_are_consistent_with_the_packer():
    assert SHEET_WIDTH == FRAMES_PER_SHEET * SPRITE_SIZE
    assert SHEET_HEIGHT == SPRITE_SIZE
    assert REQUEST_WIDTH % FRAMES_PER_SHEET == 0
