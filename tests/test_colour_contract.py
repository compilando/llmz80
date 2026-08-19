"""What a design may name as a colour, and what the program is then promised.

Two defects, both found by generating a basketball game and reading why four of
its five attempts died.

**The contract lied.** The design named six colours; `game_config.h` defined
five. `codegen._colour_lines` skips a palette entry whose prose resolves to
nothing, and `acceptance.generation_prompt` listed the palette unfiltered -- so
the writer was told `COLOUR_PISTA` existed, used it, and the build failed with
`error 20: Undefined identifier 'COLOUR_PISTA'`. Twice, in attempts one and
three, out of five.

**And it resolved to nothing for a bad reason.** The prose was "naranja claro
de parquet", and the CPC in mode 0 *has* orange -- `HW_ORANGE` is one of the
sixteen pens the packer writes. What could not name it was the parser:
`cpc_pen` went through `spectrum_attribute`, which knows the Spectrum's eight
inks and nothing else. Half of mode 0's palette was unreachable from a design's
own vocabulary.

The same route had a quieter fault. `spectrum_attribute` synthesises RGB at the
*Spectrum's* two intensities, 0xCD and 0xFF, and the CPC's are 0, 128 and 255 --
so a plain "azul marino oscuro" came out at 205 and landed on HW_BRIGHT_BLUE
rather than HW_BLUE, which is why that design's dark navy and its bright blue
were the same pen.
"""

from __future__ import annotations

import pytest

from llmz80.studio.codegen import declared_colours, render_config_header
from llmz80.studio.models import PaletteEntry, TargetPlatform, VideoMode
from llmz80.studio.palette import cpc_palette, cpc_pen, declared_attribute
from llmz80.studio.samples import blank_project


def _project(platform=TargetPlatform.AMSTRAD_CPC, mode=VideoMode.CPC_MODE_0, **colours):
    project = blank_project("Colours", platform)
    if platform is TargetPlatform.AMSTRAD_CPC:
        project.target.video_mode = mode
    project.presentation.palette = [
        PaletteEntry(id=name, colour=prose) for name, prose in colours.items()
    ]
    return project


def _rgb(mode, pen):
    return cpc_palette(mode)[pen].rgb


class TestTheCpcCanNameItsOwnPalette:
    @pytest.mark.parametrize("prose", ["naranja", "orange", "naranja claro de parquet"])
    def test_orange_is_a_colour_a_design_may_ask_for(self, prose):
        """The word that started this. Mode 0 shows HW_ORANGE and the design
        could not say so."""
        pen = cpc_pen(prose, mode=0)

        assert pen is not None
        assert _rgb(0, pen) == (255, 128, 0)

    @pytest.mark.parametrize("prose", ["rosa", "pink"])
    def test_pink_too(self, prose):
        pen = cpc_pen(prose, mode=0)

        assert pen is not None
        assert _rgb(0, pen) == (255, 128, 128)

    def test_bright_and_plain_are_different_pens(self):
        """Mode 0 carries both intensities of blue, and a design that
        distinguishes them should get two pens rather than one twice."""
        plain = cpc_pen("azul", mode=0)
        bright = cpc_pen("azul brillante", mode=0)

        assert plain != bright
        assert _rgb(0, plain) == (0, 0, 128)
        assert _rgb(0, bright) == (0, 0, 255)

    def test_a_dark_navy_is_not_the_bright_blue(self):
        """The quieter half of the same defect: routed through the Spectrum's
        0xCD intensity, "azul marino oscuro" came out nearer 255 than 128 and
        collided with "azul brillante" on one pen."""
        navy = cpc_pen("azul marino oscuro", mode=0)
        bright = cpc_pen("azul brillante", mode=0)

        assert navy != bright
        assert _rgb(0, navy) == (0, 0, 128)

    def test_every_pen_the_mode_shows_can_be_named_by_something(self):
        """The claim the whole change rests on: sixteen pens the packer can
        write, and a vocabulary that reaches all of them."""
        from llmz80.studio.palette import CPC_COLOUR_WORDS

        reachable = {cpc_pen(word, mode=0) for word in CPC_COLOUR_WORDS}
        reachable |= {cpc_pen(f"{word} brillante", mode=0) for word in CPC_COLOUR_WORDS}

        assert reachable >= set(range(len(cpc_palette(0))))

    def test_mode_1_still_quantises_to_its_four(self):
        """A richer vocabulary must not make mode 1 name pens it does not
        have: the word resolves, then the nearest of four wins."""
        pen = cpc_pen("naranja", mode=1)

        assert pen is not None
        assert 0 <= pen < 4

    def test_prose_naming_no_colour_still_answers_nothing(self):
        assert cpc_pen("a sort of shimmering", mode=0) is None

    def test_black_is_still_only_for_prose_that_asked_for_it(self):
        assert cpc_pen("negro", mode=0) == 0
        assert cpc_pen("naranja", mode=0) != 0


class TestTheHeaderAndThePromptAgree:
    """One list, two readers. They drifted, and the drift cost two attempts."""

    def test_every_colour_the_prompt_offers_is_defined(self):
        from llmz80.studio.acceptance import generation_prompt

        project = _project(pista="naranja claro de parquet", grada="azul marino oscuro")
        header = render_config_header(project)
        prompt = generation_prompt(project)

        for entry in project.presentation.palette:
            macro = f"COLOUR_{entry.id.upper()}"
            if macro in prompt.replace(f"{macro} is not", ""):
                assert f"#define {macro} " in header, macro

    def test_an_unresolvable_colour_is_not_offered_as_a_macro(self):
        from llmz80.studio.acceptance import generation_prompt

        project = _project(nada="a sort of shimmering")
        prompt = generation_prompt(project)
        header = render_config_header(project)

        assert "#define COLOUR_NADA" not in header
        assert "plat_ink(COLOUR_NADA)" not in prompt

    def test_but_the_writer_is_told_it_was_dropped(self):
        """Silence would leave the writer to notice a colour missing from a
        list it never saw complete. The design named it; the machine cannot
        show it; saying so is cheaper than letting it be inferred."""
        from llmz80.studio.acceptance import generation_prompt

        prompt = generation_prompt(_project(nada="a sort of shimmering"))

        assert "nada" in prompt
        assert "no macro" in prompt or "cannot" in prompt

    def test_declared_colours_is_what_both_read(self):
        project = _project(pista="naranja", nada="a sort of shimmering")

        resolved = {entry.id for entry, _ in declared_colours(project)}

        assert resolved == {"pista"}


class TestTheSpectrumIsUnchanged:
    """This is a CPC parser. The Spectrum has eight inks and a bright bit, and
    nothing here may quietly give it a ninth."""

    def test_its_colours_still_resolve_the_way_they_did(self):
        project = blank_project("Ink", TargetPlatform.SPECTRUM)
        project.presentation.palette = [PaletteEntry(id="cielo", colour="cian brillante")]

        assert declared_attribute(project, "cielo") == 0x45

    def test_a_colour_only_the_cpc_has_resolves_to_nothing_there(self):
        """Orange is not a Spectrum ink. Answering with the nearest one would
        put a colour the design did not choose behind its own word."""
        project = blank_project("Ink", TargetPlatform.SPECTRUM)
        project.presentation.palette = [PaletteEntry(id="parquet", colour="naranja")]

        assert declared_attribute(project, "parquet") is None


class TestTheDeterministicFixesAreApplied:
    """`apply_deterministic_cpc_fixes` is tested against a real toolchain and,
    until now, called by nothing.

    Found the same way. The basketball run's fourth attempt *compiled* and
    produced a DSK, and the build was refused for

        src/main.c:493: warning 158: overflow in implicit constant conversion

    which is exactly what `_cast_high_byte_constants` exists to silence -- a
    byte constant between 128 and 255 that SDCC reads as an int. The fix had
    been sitting in `utils/helpers.py` since the legacy generator was deleted,
    with a comment saying Studio's build not applying it was a gap to close.
    """

    def test_a_high_byte_constant_is_cast_before_the_compiler_sees_it(self, tmp_path):
        from llmz80.studio.compiler import prepare_program_source

        fixed, notes = prepare_program_source(
            "#include <cpctelera.h>\nvoid main(void) { u8 x = 0xFF; }\n",
            TargetPlatform.AMSTRAD_CPC,
        )

        assert "(u8)0xFF" in fixed or "(uint8_t)0xFF" in fixed
        assert notes

    def test_a_program_with_nothing_to_fix_comes_back_unchanged(self):
        from llmz80.studio.compiler import prepare_program_source

        source = "#include <arch/zx.h>\nvoid main(void) { while (1) { } }\n"
        fixed, notes = prepare_program_source(source, TargetPlatform.SPECTRUM)

        assert fixed == source
        assert notes == []

    def test_what_was_changed_is_recorded_rather_than_done_in_silence(self):
        """A build that quietly rewrites the program it was given is one whose
        diagnostics point at lines the model never wrote."""
        from llmz80.studio.compiler import prepare_program_source

        _, notes = prepare_program_source(
            "#include <cpctelera.h>\nvoid main(void) { u8 x = 0xFF; }\n",
            TargetPlatform.AMSTRAD_CPC,
        )

        assert any("cast" in note for note in notes)

    def test_each_machine_gets_its_own_fixes(self):
        """The CPC ones name CPCtelera functions and the Spectrum ones name
        z88dk scancodes; crossing them would rewrite one machine's code with
        the other's idioms."""
        from llmz80.studio.compiler import prepare_program_source

        cpc_source = "#include <cpctelera.h>\nvoid main(void) { cpct_getKeyASCII(); }\n"

        crossed, _ = prepare_program_source(cpc_source, TargetPlatform.SPECTRUM)
        fixed, _ = prepare_program_source(cpc_source, TargetPlatform.AMSTRAD_CPC)

        assert "cpct_getKeyASCII" in crossed
        assert "cpct_getKeypressedAsASCII" in fixed
