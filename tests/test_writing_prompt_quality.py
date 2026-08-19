"""What the writer is told, judged against what really failed.

Every assertion here is a failure somebody paid for in a real run, not a
stylistic preference about prompts.

  * A Breakout attempt redefined `FIELD_TOP`, which `game_config.h` already
    defines, and the redefinition warning failed the build. The prompt said
    "Studio writes game_config.h with these constants" and never listed one.
  * A basketball design ran in mode 0, and the CPC notes told its writer "Mode
    1 has four pens in total. Distinguish more than four kinds of thing by
    shape or size" -- advice for the other mode, and wrong about the one it
    was in by twelve pens.
  * The same notes said "with the firmware disabled there is no free-running
    frame counter", which stopped being true when the CPC got one.
"""

from __future__ import annotations

import pytest

from llmz80.core.platform_notes import platform_notes
from llmz80.studio.generator import writing_prompt
from llmz80.studio.models import TargetPlatform, VideoMode
from llmz80.studio.samples import blank_project


def _project(platform=TargetPlatform.AMSTRAD_CPC, mode=None):
    project = blank_project("Prompt", platform)
    if mode is not None:
        project.target.video_mode = mode
    return project


def _prompt(project):
    return writing_prompt(project, with_examples=False)


class TestTheMacrosTheHeadersAlreadyDefine:
    """The writer cannot open game_config.h while it writes, so a macro it is
    not shown is one it will invent."""

    @pytest.mark.parametrize("platform", list(TargetPlatform))
    def test_the_prompt_lists_them(self, platform):
        prompt = _prompt(_project(platform))

        for macro in ("PLAYFIELD_COLS", "PLAYFIELD_ROWS", "FIELD_TOP", "MAX_SPRITE_PY"):
            assert macro in prompt, macro

    @pytest.mark.parametrize("platform", list(TargetPlatform))
    def test_and_says_not_to_redefine_them(self, platform):
        """`#define FIELD_TOP 5` over a header that says 2 is a warning, and
        the build refuses unexpected warnings -- so this cost a whole attempt."""
        prompt = _prompt(_project(platform))

        assert "redefine" in prompt

    def test_the_values_shown_are_this_design_own(self):
        """A list of names without values would still leave the writer to
        guess how tall the playfield is."""
        from llmz80.studio.structure import playfield

        project = _project(TargetPlatform.AMSTRAD_CPC, VideoMode.CPC_MODE_0)
        columns, rows = playfield(project)

        prompt = _prompt(project)

        assert f"PLAYFIELD_COLS {columns}" in prompt
        assert f"PLAYFIELD_ROWS {rows}" in prompt


class TestTheNotesMatchTheMachineThisDesignRunsOn:
    def test_mode_0_is_not_told_it_has_four_pens(self):
        project = _project(TargetPlatform.AMSTRAD_CPC, VideoMode.CPC_MODE_0)

        notes = platform_notes(project)

        assert "four pens" not in notes
        assert "sixteen pens" in notes

    def test_mode_1_still_is(self):
        """Four is the truth there, and the advice that follows from it --
        distinguish things by shape rather than colour -- is the right advice."""
        project = _project(TargetPlatform.AMSTRAD_CPC, VideoMode.CPC_MODE_1)

        notes = platform_notes(project)

        assert "four pens" in notes

    def test_the_cpc_is_no_longer_told_it_cannot_count_frames(self):
        """It grew a frame counter, and a writer told otherwise has no reason
        to pace its loop -- while the pacing gate now judges it."""
        notes = platform_notes(_project(TargetPlatform.AMSTRAD_CPC))

        assert "no free-running frame counter" not in notes

    def test_the_spectrum_notes_are_untouched(self):
        notes = platform_notes(_project(TargetPlatform.SPECTRUM))

        assert "intrinsic_ei" in notes
        assert "pens" not in notes


class TestTheThingsThatCostBuilds:
    @pytest.mark.parametrize("platform", list(TargetPlatform))
    def test_the_writer_is_warned_about_high_byte_constants(self, platform):
        """SDCC warning 158, which refused a build that had otherwise produced
        a working DSK. The build now applies the cast itself, and saying so
        still beats letting the writer produce it and be silently rewritten."""
        prompt = _prompt(_project(platform))

        assert "128" in prompt and "255" in prompt
