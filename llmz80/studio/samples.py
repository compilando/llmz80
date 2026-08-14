"""The blank document a new project starts from.

This is not a template and has no authority: it is one screen, one actor and
two tiles, so that a freshly created project is openable, saveable and
buildable while its designer decides what it is. Everything about it is meant
to be replaced.
"""

from __future__ import annotations

from llmz80.utils.helpers import slugify as _make_slug

from .models import (
    BudgetSpec,
    ControlsSpec,
    EntitySpec,
    GameProject,
    MenuOption,
    Metadata,
    PresentationSpec,
    SceneSpec,
    ScreenSpec,
    SpawnSpec,
    TargetPlatform,
    TargetSpec,
    TileSpec,
    VideoMode,
)

#: The blank screen: a bordered room that fits every target's playfield,
#: including cpc_mode_0's 20 columns -- the tightest of the three.
BLANK_WIDTH = 20
BLANK_HEIGHT = 14


def slugify(value: str) -> str:
    """Delegate to the shared, accent-aware slugifier.

    `Metadata.language` defaults to "es", so titles routinely carry accents
    and enyes; the ascii-only regex this used to run turned "Niño español"
    into "ni-o-espa-ol" instead of transliterating it. `create_slug` returns
    "" for a title with no ascii-representable character at all (e.g. one in
    a non-Latin script), which SLUG_PATTERN rejects, so the empty-input
    fallback stays.
    """
    return _make_slug(value, max_length=48) or "new-game"


def _blank_rows() -> list[str]:
    top = "#" * BLANK_WIDTH
    middle = "#" + "." * (BLANK_WIDTH - 2) + "#"
    return [top] + [middle] * (BLANK_HEIGHT - 2) + [top]


def blank_project(
    title: str, platform: TargetPlatform, video_mode: VideoMode | None = None
) -> GameProject:
    """A valid, empty starting point for `title` on `platform`.

    `video_mode` defaults to each platform's usual mode -- spectrum_bitmap, or
    cpc_mode_1 for the CPC's wider screen -- but may be overridden, e.g. to
    cpc_mode_0 for its 16 colours over cpc_mode_1's 4.
    """
    cpc = platform is TargetPlatform.AMSTRAD_CPC
    mode = video_mode or (VideoMode.CPC_MODE_1 if cpc else VideoMode.SPECTRUM_BITMAP)
    return GameProject(
        metadata=Metadata(slug=slugify(title), title=title),
        target=TargetSpec(platform=platform, video_mode=mode),
        presentation=PresentationSpec(),
        controls=ControlsSpec(
            bindings=(
                # The CPC has dedicated cursor keys.
                {
                    "left": "LEFT",
                    "right": "RIGHT",
                    "up": "UP",
                    "down": "DOWN",
                    "action": "SPACE",
                }
                if cpc
                # QAOP+space: the 48K Spectrum's rubber keyboard has no
                # cursor keys, so this left-hand layout is what decades of
                # its games settled on instead.
                else {
                    "left": "O",
                    "right": "P",
                    "up": "Q",
                    "down": "A",
                    "action": "SPACE",
                }
            )
        ),
        # Matches the machine budgets used elsewhere in the generator (see
        # llmz80/core/generation_spec.py and llmz80/studio/registry.py): the
        # 48K Spectrum's usable RAM below its screen and system variables is
        # smaller than the CPC's, for both the binary and its static data.
        budgets=BudgetSpec(
            binary_bytes=32768 if cpc else 24576,
            static_data_bytes=12288 if cpc else 8192,
        ),
        tiles=[
            # '#'/'.' and the "solid" trait are this document's own choice of
            # alphabet, not a Studio convention: a blank project still needs
            # *some* tiles to be openable, and nothing here -- or anywhere in
            # structure.py -- validates a design against what a trait means.
            TileSpec(id="wall", char="#", traits=["solid"]),
            TileSpec(id="floor", char="."),
        ],
        entities=[EntitySpec(id="actor", kind="actor", notes="the one the player moves")],
        # Empty on purpose: the examiner derives its script from this list,
        # and a blank document should assert nothing about what it does yet.
        mechanics=[],
        screens=[
            ScreenSpec(
                id="screen_1",
                name="SCREEN 1",
                width=BLANK_WIDTH,
                height=BLANK_HEIGHT,
                tiles=_blank_rows(),
                spawns=[SpawnSpec(entity="actor", col=BLANK_WIDTH // 2, row=BLANK_HEIGHT // 2)],
            )
        ],
        initial_screen="screen_1",
        scenes=[
            SceneSpec(
                id="title",
                kind="title",
                title=title,
                options=[MenuOption(label="START", target_scene="game")],
            ),
            SceneSpec(id="game", kind="gameplay", next_scene="game_over"),
            SceneSpec(id="game_over", kind="game_over", title="GAME OVER", next_scene="title"),
        ],
        initial_scene="title",
    )
