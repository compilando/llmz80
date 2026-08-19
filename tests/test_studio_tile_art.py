"""Terrain artwork: one 8x8 block per tile, packed for each machine.

Sprites were the only artwork Studio ever packed, and they are 16x16 and
masked because an actor moves over a background it must not erase. Terrain is
neither: a tile fills exactly one character cell and it is what the background
*is*, so it needs no mask and it must not be 16 pixels of anything.

`TileSpec.art` has carried "Unused until the graphics phase" since the model
was written; these tests are the start of that phase.
"""

from PIL import Image

from llmz80.studio.models import AssetSpec
from llmz80.studio.spriting import TILE_SIZE, is_tile_art, pack_cpc_tile, pack_spectrum_tile

OPAQUE_WHITE = (255, 255, 255, 255)
DIM_CYAN = (0, 205, 205, 255)  # the Spectrum's non-BRIGHT intensity
BRIGHT_CYAN = (0, 255, 255, 255)
CLEAR = (0, 0, 0, 0)


def _tile(rows: list[str], colour=OPAQUE_WHITE) -> Image.Image:
    """An 8x8 RGBA tile from eight strings of `#` (drawn) and `.` (clear)."""
    image = Image.new("RGBA", (TILE_SIZE, TILE_SIZE), CLEAR)
    pixels = image.load()
    for y, row in enumerate(rows):
        for x, character in enumerate(row):
            if character == "#":
                pixels[x, y] = colour
    return image


SOLID = ["########"] * TILE_SIZE
BRICK = [
    "########",
    "#......#",
    "########",
    "...#....",
    "########",
    "#......#",
    "########",
    "...#....",
]


def test_a_spectrum_tile_packs_to_one_byte_per_row():
    """Eight bytes, not sixteen: the whole point of tile art is that a tile is
    one character cell, so a row is one byte and a tile is a cell's worth of
    bitmap the ROM font would otherwise have supplied."""
    packed = pack_spectrum_tile(_tile(SOLID))

    assert packed.width_bytes == 1
    assert packed.height == TILE_SIZE
    assert packed.data == bytes([0xFF] * TILE_SIZE)


def test_a_spectrum_tiles_clear_pixels_are_paper_not_a_mask():
    """A tile has no mask -- it *is* the background -- so a clear pixel packs
    as a zero bit and shows the paper, rather than as a mask bit that would
    keep whatever was on screen before."""
    packed = pack_spectrum_tile(_tile(BRICK))

    assert packed.data == bytes([0xFF, 0x81, 0xFF, 0x10, 0xFF, 0x81, 0xFF, 0x10])
    assert packed.mask == b""


def test_a_spectrum_tile_takes_the_ink_its_own_pixels_resolve_to():
    """Same rule sprites already follow (`spriting._spectrum_attribute`): the
    dominant opaque colour decides the one attribute a cell can hold."""
    packed = pack_spectrum_tile(_tile(SOLID, colour=DIM_CYAN))

    assert packed.attribute == 0x05  # PAPER_BLACK | INK_CYAN


def test_a_fully_saturated_tile_colour_carries_bright():
    """The same threshold `spriting._BRIGHT_THRESHOLD` applies to a sprite:
    the machine has two intensities of every ink and the pixels pick one."""
    packed = pack_spectrum_tile(_tile(SOLID, colour=BRIGHT_CYAN))

    assert packed.attribute == 0x45  # BRIGHT | INK_CYAN


def test_a_cpc_mode_1_tile_packs_four_pixels_to_a_byte():
    """Mode 1 is four pens per byte, so an 8-pixel row is two bytes -- and a
    tile carries no interleaved mask, unlike `pack_cpc`, because there is no
    background to keep."""
    packed = pack_cpc_tile(_tile(SOLID), mode=1, palette=[(0, 0, 0), (255, 255, 255)])

    assert packed.width_bytes == 2
    assert len(packed.data) == 2 * TILE_SIZE


def test_a_cpc_mode_0_tile_packs_two_pixels_to_a_byte():
    packed = pack_cpc_tile(_tile(SOLID), mode=0, palette=[(0, 0, 0), (255, 255, 255)])

    assert packed.width_bytes == 4
    assert len(packed.data) == 4 * TILE_SIZE


def test_a_cpc_tiles_clear_pixels_pack_as_pen_zero():
    """Pen 0 is the paper, so a clear pixel is drawn in it rather than left to
    a mask that tile art does not have."""
    packed = pack_cpc_tile(
        _tile(["........"] * TILE_SIZE), mode=1, palette=[(0, 0, 0), (255, 255, 255)]
    )

    assert packed.data == bytes(2 * TILE_SIZE)


def _asset(**overrides) -> AssetSpec:
    fields = {
        "id": "ladrillo",
        "kind": "tileset",
        "source": "assets/ladrillo.png",
        "width": TILE_SIZE,
        "height": TILE_SIZE,
        "frames": 1,
    }
    fields.update(overrides)
    return AssetSpec(**fields)


def test_an_eight_by_eight_tileset_asset_is_tile_art():
    assert is_tile_art(_asset()) is True


def test_a_sprite_sized_asset_is_not_tile_art():
    """The one question two call sites must never answer differently -- the
    packer's and the prompt's -- exactly as `is_blitter_sprite` documents for
    sprites."""
    assert is_tile_art(_asset(kind="sprite", width=16, height=16)) is False


def test_a_tileset_asset_of_the_wrong_size_is_not_tile_art():
    assert is_tile_art(_asset(width=16, height=16)) is False
