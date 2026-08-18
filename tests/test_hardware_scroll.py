"""Coarse hardware scrolling, which one of the two machines has.

The Amstrad CPC's CRTC keeps the address the display starts reading from, so
moving the picture costs one register write and no memory movement at all. The
ZX Spectrum has no such register: moving its picture means moving 6912 bytes,
which is not a thing a C game does every frame.

Both numbers below were measured on a real CPC through ZEsarUX rather than
read off a datasheet, because CPCtelera's own two examples disagree about the
first of them -- `advanced/hwscroll` comments "4-by-4 bytes" while
`advanced/tilemap_hwscroll` advances its software pointer by two for the same
unit:

  * one unit of `cpct_setVideoMemoryOffset` moves the start by **2 bytes**,
    which is 4 pixels across in mode 0 and 8 in mode 1;
  * 40 units is 80 bytes, one whole screen row, and scrolls the picture up by
    exactly one character row.

So this is *coarse* scrolling and the API says so. Nothing here pretends a
sub-step exists: a pixel-smooth horizontal scroll needs the background redrawn
shifted, and a sub-row vertical one needs the CRTC's vertical adjust, and
neither is this.
"""

from __future__ import annotations

import pytest

from llmz80.studio.codegen import (
    SCROLL_ROW_BYTES,
    SCROLL_STEP_BYTES,
    max_scroll_origin,
    render_config_header,
    scrolls_in_hardware,
)
from llmz80.studio.models import TargetPlatform
from llmz80.studio.samples import blank_project
from llmz80.studio.structure import structural_errors


class TestWhichMachinesCanDoIt:
    def test_the_cpc_can_and_the_spectrum_cannot(self):
        assert scrolls_in_hardware(TargetPlatform.AMSTRAD_CPC)
        assert not scrolls_in_hardware(TargetPlatform.SPECTRUM)

    def test_a_target_nobody_has_taught_cannot_either(self):
        """The same shape every other capability question here takes: absence
        is the answer for a machine this project has never heard of."""
        assert not scrolls_in_hardware("commodore_64")

    def test_the_step_is_two_bytes_on_the_cpc_and_nothing_on_the_spectrum(self):
        """2, measured -- see the module docstring for why it is not read off
        CPCtelera's own comment. 0 means "this machine does not scroll", which
        is what the C reads to compile the call away."""
        assert SCROLL_STEP_BYTES[TargetPlatform.AMSTRAD_CPC] == 2
        assert SCROLL_STEP_BYTES[TargetPlatform.SPECTRUM] == 0

    def test_a_screen_row_is_the_vertical_step(self):
        """40 units of 2 bytes. Advancing a whole row moves the picture up by
        one character row, which is the only vertical granularity there is."""
        assert SCROLL_ROW_BYTES[TargetPlatform.AMSTRAD_CPC] == 80
        assert (
            SCROLL_ROW_BYTES[TargetPlatform.AMSTRAD_CPC]
            // SCROLL_STEP_BYTES[TargetPlatform.AMSTRAD_CPC]
            == 40
        )


class TestHowFarItGoes:
    def test_the_cpc_reaches_510_bytes(self):
        """R13 is eight bits, so 255 steps of 2 bytes. Past that the *page*
        has to change, which is a different register and a different problem
        -- and the bound has to be stated or a game scrolls into a wrap it did
        not plan for."""
        assert max_scroll_origin(TargetPlatform.AMSTRAD_CPC) == 510

    def test_the_spectrum_reaches_nowhere(self):
        assert max_scroll_origin(TargetPlatform.SPECTRUM) == 0

    def test_the_reach_is_six_rows_and_a_bit(self):
        """Stated because it is the number that decides what kind of game can
        use this: 510 bytes is six screen rows plus 30, so a vertical scroller
        gets six character rows before it must change page."""
        cpc = TargetPlatform.AMSTRAD_CPC
        assert max_scroll_origin(cpc) // SCROLL_ROW_BYTES[cpc] == 6


class TestTheHeaderTellsTheProgram:
    @pytest.mark.parametrize(
        "platform,step", [(TargetPlatform.SPECTRUM, 0), (TargetPlatform.AMSTRAD_CPC, 2)]
    )
    def test_every_target_publishes_its_step(self, platform, step):
        header = render_config_header(blank_project("Scroll", platform))

        assert f"#define SCROLL_STEP_BYTES {step}" in header

    def test_the_cpc_publishes_its_row_and_its_reach(self):
        header = render_config_header(blank_project("Scroll", TargetPlatform.AMSTRAD_CPC))

        assert "#define SCROLL_ROW_BYTES 80" in header
        assert "#define MAX_SCROLL_ORIGIN 510" in header

    def test_a_program_can_tell_the_two_machines_apart_at_compile_time(self):
        """`#if SCROLL_STEP_BYTES` is how a program writes one source that
        scrolls where it can and does not where it cannot, which is the whole
        reason the Spectrum publishes a zero rather than nothing."""
        for platform in TargetPlatform:
            header = render_config_header(blank_project("Scroll", platform))

            assert "#define SCROLL_STEP_BYTES " in header


class TestADesignCannotAskAMachineForWhatItLacks:
    """The same rule the audio one follows: a design that asks a target for
    something it does not have is refused at design time, with the reason,
    rather than building into a game where the feature silently does nothing.
    """

    def test_a_scrolling_spectrum_design_is_refused(self):
        project = blank_project("Scroller", TargetPlatform.SPECTRUM)
        project.presentation.scrolling = True

        errors = structural_errors(project)

        assert any("scroll" in error for error in errors), errors

    def test_the_refusal_says_what_the_machine_lacks(self):
        project = blank_project("Scroller", TargetPlatform.SPECTRUM)
        project.presentation.scrolling = True

        message = " ".join(structural_errors(project))

        assert "spectrum" in message
        assert "hardware" in message

    def test_a_scrolling_cpc_design_is_accepted(self):
        project = blank_project("Scroller", TargetPlatform.AMSTRAD_CPC)
        project.presentation.scrolling = True

        assert not [error for error in structural_errors(project) if "scroll" in error]

    def test_a_spectrum_design_that_does_not_ask_is_untouched(self):
        project = blank_project("Static", TargetPlatform.SPECTRUM)

        assert not [error for error in structural_errors(project) if "scroll" in error]


class TestTheDesignCanAskForIt:
    def test_the_drafter_is_told_which_machine_has_it_and_how_coarse(self):
        """A drafter that only heard "the CPC can scroll" would put it in every
        CPC design, including ones whose four-pixel steps would look worse than
        not scrolling at all."""
        from llmz80.studio.drafting import DRAFT_SYSTEM_PROMPT

        assert "scrolling" in DRAFT_SYSTEM_PROMPT
        assert "Amstrad" in DRAFT_SYSTEM_PROMPT or "CPC" in DRAFT_SYSTEM_PROMPT

    def test_the_writer_is_told_the_step_and_whose_job_the_edge_is(self):
        """The incoming column is read out of memory the program has to have
        drawn. A writer that did not know would ship a game with a stripe of
        whatever was there before running down one side."""
        from llmz80.studio.acceptance import generation_prompt

        project = blank_project("Scroller", TargetPlatform.AMSTRAD_CPC)
        project.presentation.scrolling = True

        prompt = generation_prompt(project)

        assert "plat_scroll_to" in prompt
        assert "2 bytes" in prompt

    def test_a_design_that_does_not_scroll_is_not_told_about_it(self):
        """Prompt space is not free, and a call a design has no use for is one
        more thing for the writer to reach for by mistake."""
        from llmz80.studio.acceptance import generation_prompt

        prompt = generation_prompt(blank_project("Static", TargetPlatform.AMSTRAD_CPC))

        assert "plat_scroll_to" not in prompt


class TestTheMeasuredSpriteBudget:
    """What a loop can draw and still keep pace, from `codegen.SPRITES_PER_FRAME`.

    The readings behind the numbers are in that constant's comment. These pin
    the properties a reader would otherwise have to re-derive, not the figures
    themselves -- a better blitter should be able to raise them without
    rewriting the test that says the CPC is faster.
    """

    def test_the_pixel_column_blitter_is_the_dearer_one(self):
        from llmz80.studio.codegen import sprites_per_frame

        for platform in TargetPlatform:
            cheap = sprites_per_frame(platform, pixel_column=False)
            dear = sprites_per_frame(platform, pixel_column=True)

            assert dear < cheap, platform

    def test_the_cpc_draws_more_than_the_spectrum(self):
        """`cpct_drawSpriteMasked` is hand-written assembly; the Spectrum
        blitter is C in this repository."""
        from llmz80.studio.codegen import sprites_per_frame

        for pixel_column in (False, True):
            assert sprites_per_frame(
                TargetPlatform.AMSTRAD_CPC, pixel_column=pixel_column
            ) > sprites_per_frame(TargetPlatform.SPECTRUM, pixel_column=pixel_column)

    def test_a_target_nobody_measured_gets_the_most_cautious_answer(self):
        from llmz80.studio.codegen import sprites_per_frame

        unknown = sprites_per_frame("commodore_64", pixel_column=True)

        assert unknown == sprites_per_frame(TargetPlatform.SPECTRUM, pixel_column=True)

    def test_the_budget_is_below_the_measured_ceiling(self):
        """The ceilings were 12 and 8 on the Spectrum, 32 and 24 on the CPC,
        from a loop that did nothing but draw. A real game also reads keys,
        moves things and tests collisions, so publishing the ceiling would fail
        every program that used it."""
        from llmz80.studio.codegen import sprites_per_frame

        assert sprites_per_frame(TargetPlatform.SPECTRUM, pixel_column=False) < 12
        assert sprites_per_frame(TargetPlatform.SPECTRUM, pixel_column=True) < 8
        assert sprites_per_frame(TargetPlatform.AMSTRAD_CPC, pixel_column=False) < 32
        assert sprites_per_frame(TargetPlatform.AMSTRAD_CPC, pixel_column=True) < 24

    def test_the_writer_is_given_the_number(self):
        from llmz80.studio.acceptance import generation_prompt
        from llmz80.studio.codegen import sprites_per_frame
        from llmz80.studio.models import AssetSpec

        for platform in TargetPlatform:
            project = blank_project("Budget", platform)
            project.assets = [
                AssetSpec(id="hero", kind="sprite", source="assets/hero.png", width=16, height=16)
            ]

            prompt = generation_prompt(project)

            assert f"about {sprites_per_frame(platform, pixel_column=False)} sprites" in prompt


class TestADesignCanChooseTheVideoMode:
    """Mode 0's sixteen pens are reachable in the library, and were reachable
    by nothing else: `/target/platform` is protected and the drafting prompt
    told the model the rest of `/target` was not its to touch, so a design
    could only get mode 0 by somebody editing game.yml by hand.

    Which mode a CPC game runs in is a design decision and not a fact about the
    machine -- colour against width -- so it is the one part of `/target` a
    design gets to make.
    """

    def test_the_drafter_is_offered_the_choice_with_the_trade(self):
        from llmz80.studio.drafting import DRAFT_SYSTEM_PROMPT

        assert "/target/video_mode" in DRAFT_SYSTEM_PROMPT
        assert "cpc_mode_0" in DRAFT_SYSTEM_PROMPT
        assert "16 colours" in DRAFT_SYSTEM_PROMPT
        assert "20 columns" in DRAFT_SYSTEM_PROMPT

    def test_the_planner_lets_it_through(self):
        from llmz80.studio.models import VideoMode
        from llmz80.studio.planner import ProjectChange, ProjectProposal, TextValue, apply_proposal

        project = blank_project("Colourful", TargetPlatform.AMSTRAD_CPC)
        assert project.target.video_mode is VideoMode.CPC_MODE_1

        updated = apply_proposal(
            project,
            ProjectProposal(
                summary="the bricks need colours",
                changes=[
                    ProjectChange(
                        path="/target/video_mode",
                        operation="replace",
                        reason="this game is about telling coloured bricks apart",
                        value=TextValue(text="cpc_mode_0"),
                    )
                ],
            ),
        )

        assert updated.target.video_mode is VideoMode.CPC_MODE_0

    def test_the_platform_itself_is_still_not_negotiable(self):
        """A person chose the machine. The mode is a decision inside it."""
        from llmz80.studio.planner import ProjectChange, ProjectProposal, TextValue, apply_proposal

        project = blank_project("Colourful", TargetPlatform.AMSTRAD_CPC)

        with pytest.raises(ValueError, match="protected"):
            apply_proposal(
                project,
                ProjectProposal(
                    summary="switch machines",
                    changes=[
                        ProjectChange(
                            path="/target/platform",
                            operation="replace",
                            reason="no",
                            value=TextValue(text="spectrum"),
                        )
                    ],
                ),
            )
