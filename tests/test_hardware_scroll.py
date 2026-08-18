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
