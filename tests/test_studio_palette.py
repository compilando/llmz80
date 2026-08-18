"""The colour a design names, resolved to what each machine can show.

`TileSpec.colour` and `EntitySpec.colour` hold a palette entry id, and
`PaletteEntry.colour` holds prose -- "bright cyan", "azul brillante". Nothing
used to read either: every tile was drawn in white and every sprite took the
ink its own pixels happened to resolve to. These tests pin the translation
from that prose to a Spectrum attribute byte and to a CPC pen.
"""

import pytest

from llmz80.studio.models import GameProject, PaletteEntry, TargetPlatform
from llmz80.studio.palette import cpc_pen, declared_attribute, spectrum_attribute
from llmz80.studio.samples import blank_project

# From <arch/zx.h>, quoted in spriting.py: PAPER_BLACK is 0, the ink is the low
# three bits (blue=1, red=2, green=4, and every other ink is their OR) and
# BRIGHT is 0x40.
INK_CYAN = 0x05
INK_YELLOW = 0x06
INK_WHITE = 0x07
BRIGHT = 0x40


def test_an_english_colour_becomes_its_ink():
    assert spectrum_attribute("cyan") == INK_CYAN


def test_a_spanish_colour_becomes_the_same_ink():
    """Designs come back in the language the brief was written in, so the
    prose a Spanish drafter writes has to resolve too -- not to white."""
    assert spectrum_attribute("cian") == INK_CYAN


def test_bright_lifts_the_ink_in_either_language():
    assert spectrum_attribute("bright yellow") == BRIGHT | INK_YELLOW
    assert spectrum_attribute("amarillo brillante") == BRIGHT | INK_YELLOW


def test_word_order_does_not_matter():
    """ "bright cyan" and "cyan bright" name one colour; so does a comma."""
    assert spectrum_attribute("cyan, bright") == BRIGHT | INK_CYAN


def test_prose_naming_no_colour_at_all_resolves_to_nothing():
    """`None`, not white: a caller that cannot tell "unnamed" from "white"
    cannot leave the pixel-derived ink alone when the design said nothing."""
    assert spectrum_attribute("the colour of a stormy afternoon") is None


def test_black_is_a_colour_a_design_may_name():
    """Ink 0 is falsy and must still come back as an attribute, or a tile
    declared black would be treated as undeclared."""
    assert spectrum_attribute("black") == 0x00


def test_a_cpc_colour_resolves_to_a_pen_the_mode_really_shows():
    """A named colour has to land on a pen this mode programs, rather than on
    a hardware colour no design ever sets."""
    assert cpc_pen("black", mode=1) == 0
    assert cpc_pen("blue", mode=1) == 1
    assert cpc_pen("bright yellow", mode=1) == 2
    assert cpc_pen("white", mode=1) == 3


def test_a_named_colour_never_resolves_to_the_background_pen():
    """Pen 0 is the paper every design draws on, so a red four pens cannot
    show has to land on *some* pen a player can see -- resolving it to black
    would draw the design's brickwork in the colour of the background.

    Which pen it lands on is deliberately not asserted. Mode 1 has no red and
    no near-red: whichever of blue and yellow wins is an artefact of Euclidean
    distance over a palette that cannot answer the question, and pinning the
    winner would make this test fail every time one of the four pens is
    corrected -- which is exactly what happened when HW_BLUE stopped being
    written down as (0, 0, 255). What must never change is that the answer is
    visible.
    """
    assert cpc_pen("red", mode=1) != 0


def test_mode_0_does_not_have_to_approximate_that_red_at_all():
    """The same prose, on the mode whose sixteen pens include red. This is
    what the four-pen palette was costing every mode 0 design."""
    from llmz80.studio.palette import cpc_palette

    red, green, blue = cpc_palette(0)[cpc_pen("red", mode=0)].rgb

    assert red > 0
    assert (green, blue) == (0, 0)


def test_black_still_resolves_to_the_background_pen():
    """The rule above is about colours the palette cannot show, not about a
    design that asked for black on purpose."""
    assert cpc_pen("negro", mode=1) == 0
    assert cpc_pen("negro", mode=0) == 0


def test_an_unnamed_cpc_colour_resolves_to_nothing():
    assert cpc_pen("something else entirely", mode=1) is None


def _with_palette(platform: TargetPlatform) -> GameProject:
    project = blank_project("Coloured", platform)
    project.presentation.palette = [
        PaletteEntry(id="brick_red", colour="bright red"),
        PaletteEntry(id="ladrillo", colour="cian"),
    ]
    return project


def test_a_declared_colour_id_resolves_through_the_designs_own_palette():
    project = _with_palette(TargetPlatform.SPECTRUM)

    assert declared_attribute(project, "ladrillo") == INK_CYAN


def test_the_same_id_resolves_to_a_pen_on_the_cpc():
    project = _with_palette(TargetPlatform.AMSTRAD_CPC)

    assert declared_attribute(project, "brick_red") == 2  # nearest visible pen


def test_an_id_the_palette_never_declared_resolves_to_nothing():
    project = _with_palette(TargetPlatform.SPECTRUM)

    assert declared_attribute(project, "no_such_colour") is None


def test_no_colour_at_all_resolves_to_nothing():
    """A tile or entity with `colour: None` asks for nothing."""
    project = _with_palette(TargetPlatform.SPECTRUM)

    assert declared_attribute(project, None) is None


@pytest.mark.parametrize(
    "prose, ink",
    [
        ("blue", 0x01),
        ("red", 0x02),
        ("magenta", 0x03),
        ("green", 0x04),
        ("cyan", 0x05),
        ("yellow", 0x06),
        ("white", 0x07),
        ("azul", 0x01),
        ("rojo", 0x02),
        ("verde", 0x04),
        ("amarillo", 0x06),
        ("blanco", 0x07),
        ("negro", 0x00),
    ],
)
def test_every_ink_the_machine_has_is_nameable(prose, ink):
    assert spectrum_attribute(prose) == ink
