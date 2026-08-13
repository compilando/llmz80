"""A new project is a blank document, not an instance of a genre."""

import pytest

from llmz80.studio.models import GameProject, TargetPlatform, VideoMode
from llmz80.studio.samples import blank_project
from llmz80.studio.typologies import typology_hints


@pytest.mark.parametrize(
    "platform,mode",
    [
        (TargetPlatform.SPECTRUM, VideoMode.SPECTRUM_BITMAP),
        (TargetPlatform.AMSTRAD_CPC, VideoMode.CPC_MODE_1),
    ],
)
def test_a_blank_project_is_valid_on_every_target(platform, mode):
    project = blank_project("Blank", platform)
    assert isinstance(project, GameProject)
    assert project.target.video_mode is mode


def test_a_blank_project_carries_no_enemy_and_no_collectible():
    """The old default forced three entities on every game. This forces one."""
    project = blank_project("Blank", TargetPlatform.SPECTRUM)
    assert [entity.id for entity in project.entities] == ["hero"]


def test_a_blank_project_has_one_screen_and_starts_on_it():
    project = blank_project("Blank", TargetPlatform.SPECTRUM)
    assert len(project.screens) == 1
    assert project.initial_screen == project.screens[0].id


def test_the_slug_comes_from_the_title():
    assert blank_project("Mi Juego!", TargetPlatform.SPECTRUM).metadata.slug == "mi-juego"


def test_typologies_are_prompt_material_with_no_power_over_a_design():
    hints = typology_hints()
    assert "maze chase" in hints.casefold()
    assert "brick breaker" in hints.casefold()
    assert isinstance(hints, str)


def test_the_genre_machinery_is_gone():
    for module in ("llmz80.studio.packs", "llmz80.studio.layout"):
        with pytest.raises(ModuleNotFoundError):
            __import__(module)
