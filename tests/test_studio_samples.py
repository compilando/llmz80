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


def test_the_video_mode_can_be_overridden():
    project = blank_project("Blank", TargetPlatform.AMSTRAD_CPC, VideoMode.CPC_MODE_0)
    assert project.target.video_mode is VideoMode.CPC_MODE_0


def test_a_blank_project_carries_no_enemy_and_no_collectible():
    """The old default forced three entities on every game. This forces one,
    and names it `actor` rather than `player` -- v4's abolished role word."""
    project = blank_project("Blank", TargetPlatform.SPECTRUM)
    assert [entity.id for entity in project.entities] == ["actor"]


def test_a_blank_project_asserts_no_mechanic_of_its_own():
    """The examiner derives its script from `mechanics`; a document nobody
    has designed yet must not ship an assertion about what it does."""
    project = blank_project("Blank", TargetPlatform.SPECTRUM)
    assert project.mechanics == []


def test_a_blank_project_has_one_screen_and_starts_on_it():
    project = blank_project("Blank", TargetPlatform.SPECTRUM)
    assert len(project.screens) == 1
    assert project.initial_screen == project.screens[0].id


def test_the_slug_comes_from_the_title():
    assert blank_project("Mi Juego!", TargetPlatform.SPECTRUM).metadata.slug == "mi-juego"


def test_the_slug_transliterates_accents():
    """`Metadata.language` defaults to "es"; a slugifier that only strips
    non-ascii instead of transliterating it turns every accented title into
    a string of dashes."""
    project = blank_project("Niño español", TargetPlatform.SPECTRUM)
    assert project.metadata.slug == "nino-espanol"


def test_typologies_are_prompt_material_with_no_power_over_a_design():
    hints = typology_hints()
    assert "maze chase" in hints.casefold()
    assert "brick breaker" in hints.casefold()
    assert isinstance(hints, str)


def test_typology_hints_accepts_a_path_override(tmp_path):
    custom = tmp_path / "custom_genres.yml"
    custom.write_text(
        "genres:\n"
        "  - id: custom\n"
        "    name: Custom kind\n"
        "    description: A kind only this file knows.\n",
        encoding="utf-8",
    )
    hints = typology_hints(custom)
    assert "custom kind" in hints.casefold()
    assert "maze chase" not in hints.casefold()


def test_typology_hints_refuses_a_file_with_no_typologies(tmp_path):
    empty = tmp_path / "empty.yml"
    empty.write_text("genres: []\n", encoding="utf-8")
    with pytest.raises(ValueError, match="no typologies"):
        typology_hints(empty)


def test_typology_hints_refuses_an_entry_missing_a_field(tmp_path):
    broken = tmp_path / "broken.yml"
    broken.write_text("genres:\n  - id: x\n    name: X\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing description"):
        typology_hints(broken)


def test_the_genre_machinery_is_gone():
    for module in ("llmz80.studio.packs", "llmz80.studio.layout"):
        with pytest.raises(ModuleNotFoundError):
            __import__(module)
