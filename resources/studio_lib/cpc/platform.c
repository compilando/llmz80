/* Amstrad CPC implementation of the Studio engine platform layer.
 *
 * Cells are one 8x8 character block wide, so the engine grid maps directly to
 * CPCtelera's screen pointer arithmetic in both mode 0 and mode 1.
 */
#include <cpctelera.h>

#include "platform.h"
#include "game_config.h"
#include "sprites.h"
#include "tiles.h"

#if CPC_MODE == 0
#define CELL_BYTES 4
#define draw_string cpct_drawStringM0
#define set_draw_char cpct_setDrawCharM0
#else
#define CELL_BYTES 2
#define draw_string cpct_drawStringM1
#define set_draw_char cpct_setDrawCharM1
#endif

/* Four pens, set explicitly so the result does not depend on whichever
 * palette the firmware left behind. Which pen means what is the design's
 * business, not this library's; mode 1 offers no more than these four.
 *
 * Built on the stack on purpose. A file-scope initialised array lands in the
 * DATA segment, which this link does not initialise at run time, and a const
 * array would need a cast that raises SDCC warning 357. Either way the palette
 * would be filled with whatever happened to be in memory. */
static void apply_palette(void) {
    u8 palette[4];
    palette[0] = HW_BLACK;
    palette[1] = HW_BLUE;
    palette[2] = HW_BRIGHT_YELLOW;
    palette[3] = HW_WHITE;
    cpct_setPalette(palette, 4);
}

void plat_init(void) {
    cpct_disableFirmware();
    cpct_setVideoMode(CPC_MODE);
    apply_palette();
    cpct_setBorder(HW_BLACK);
    cpct_clearScreen(0x00);
    set_draw_char(3, 0);
}

void plat_clear(void) {
    cpct_clearScreen(0x00);
}

void plat_border(unsigned char colour) {
    cpct_setBorder(colour == 2 ? HW_RED : HW_BLACK);
}

/* With the firmware disabled the CPC has no free-running frame counter, so a
 * missed frame is indistinguishable from a met one here. HAS_FRAME_CLOCK is 0
 * on this target and the engine hides the overrun readout accordingly. */
/* Defined here, as on the Spectrum, so the linker map carries the contract
 * symbol on both machines and no program has to keep the number itself. It
 * never moves: this target has no free-running frame counter to subtract, so
 * `HAS_FRAME_CLOCK` is 0 and `pacing.pacing_report` abstains rather than
 * reading this zero as a game that kept perfect time. */
unsigned char g_worst_frame_cost;

unsigned char plat_wait_frame(void) {
    cpct_waitVSYNC();
    return 0;
}

/* Nothing to resynchronise: with the firmware disabled this machine has no
 * free-running frame counter, so plat_wait_frame measures nothing and there is
 * no accumulated gap to forgive. Present so one program compiles unchanged
 * against either platform library -- the same reason plat_sound is a no-op
 * here. */
void plat_frame_baseline(void) {
}

unsigned char plat_input(void) {
    unsigned char keys = 0;
    cpct_scanKeyboard_f();
#define X(bit, code) if (cpct_isKeyPressed(code)) keys |= bit;
    INPUT_BINDINGS(X)
#undef X
    return keys;
}

void plat_text(unsigned char col, unsigned char row, const char *text) {
    u8 *screen = cpct_getScreenPtr(CPCT_VMEM_START, (u8)(col * CELL_BYTES), (u8)(row * 8));
    draw_string((void *)text, screen);
}

/* Reuses the proven text path rather than a second glyph blitter: one
 * character, drawn where a cell is. */
void plat_cell(unsigned char col, unsigned char row, char glyph) {
    char text[2];
    if (col >= (80 / CELL_BYTES) || row >= 25) return;
    text[0] = glyph;
    text[1] = 0;
    plat_text(col, row, text);
}

/* The pen characters and text are drawn in. Colour on this machine is a pen
 * per pixel rather than an attribute per cell, so "the current ink" is the
 * foreground pen cpct_setDrawCharM* is told to use, and switching it is a call
 * to that same setter -- not a byte kept here and applied later. Pen 3 (white
 * in apply_palette's four) is what plat_init already set, so a program that
 * never calls this looks exactly as it did.
 *
 * The attribute a Spectrum program passes is accepted unchanged and read as a
 * pen index, because that is what `palette.declared_attribute` hands back on
 * this target: COLOUR_<ID> is a pen here and an attribute byte there, and the
 * program says plat_ink(COLOUR_LADRILLO) on both. Anything outside the four
 * pens is ignored rather than set, since cpct_setDrawCharM* would encode the
 * low bits of a bad index into a colour nobody chose. */
static u8 draw_pen = 3;

unsigned char plat_ink(unsigned char attribute) {
    u8 previous = draw_pen;
    if (attribute < 4) {
        draw_pen = attribute;
        set_draw_char(draw_pen, 0);
    }
    return previous;
}

/* Draws a tile's own 8x8 block into one cell, through the *unmasked*
 * cpct_drawSprite (~/cpctelera/cpctelera/src/sprites/cpct_drawSprite.asm).
 * Unmasked is the point: terrain is the background, so there is nothing to
 * keep and no mask to interleave -- which also makes a tile half the bytes a
 * masked one would be.
 *
 * Bounds guard: one cell wide and one cell tall, so unlike plat_sprite the
 * last legal column is (80 / CELL_BYTES) - 1 and the last legal row is 24.
 * The crossing arithmetic plat_sprite's comment describes does not arise at
 * all here: eight pixel lines starting at a character row boundary stay inside
 * one 8-line block, which is exactly one cpct_getScreenPtr result plus the
 * callee's own per-line stepping.
 *
 * TILE_BYTES_WIDE is CELL_BYTES by construction (spriting.pack_cpc_tile packs
 * 8 pixels at the mode's pixels per byte, and a cell is 8 pixels), so the
 * width passed is the tile's real byte width and not an assumption. */
void plat_tile(unsigned char col, unsigned char row, unsigned char tile) {
#if TILE_COUNT
    u8 *screen;
    if (tile >= TILE_COUNT) return;
    if (col >= (80 / CELL_BYTES) || row >= 25) return;
    screen = cpct_getScreenPtr(CPCT_VMEM_START, (u8)(col * CELL_BYTES), (u8)(row * 8));
    cpct_drawSprite((void *)tile_data[tile], screen, TILE_BYTES_WIDE, TILE_HEIGHT);
#else
    (void)col; (void)row; (void)tile;
#endif
}

/* The CPC target declares no audio, so this is deliberately silent. The design
 * gate refuses any project that asks this machine for sound, which is why a
 * no-op here can never lose an effect the designer expected to hear. */
void plat_sound(unsigned char effect) {
    (void)effect;
}

/* Draws one 16x16 masked sprite as two rows of two cells, through
 * cpct_drawSpriteMasked (~/cpctelera/cpctelera/src/sprites/cpct_drawSpriteMasked.asm).
 *
 * Vertical boundary crossing: the CPC screen is laid out in eight interleaved
 * 8-pixel-line blocks per character row (cpct_getScreenPtr's own formula,
 * screen_start + 80*(y/8) + 2048*(y%8) + x -- see cpct_getScreenPtr.asm's
 * Details section), so a naive `address += stride` per pixel line is wrong
 * once a sprite's second half starts a new character row. That crossing is
 * *not* this function's job to get right: cpct_drawSpriteMasked.asm's own
 * per-line loop (labels dms_sprite_height_loop..dms_sprite_8bit_boundary_crossed,
 * lines ~161-186) already detects it -- `and #0x38` on the recomputed high
 * byte catches every 8th line -- and repoints DE by adding 0xC050 (three
 * banks forward, i.e. one bank back plus 0x50) to land on the next
 * character row. One cpct_getScreenPtr call up front is therefore enough;
 * no fresh call is needed per half the way the Spectrum blitter needs one
 * per third.
 *
 * What the callee will *not* do (documented directly above that loop, under
 * "Known limitations" in the same .asm): no boundary check or clipping
 * against the edge of video memory, and the crossing math it does do only
 * ever steps forward through the current 16K bank -- it never wraps back to
 * row 0. A sprite whose bottom half would fall past the last character row
 * corrupts whatever memory follows the screen instead of failing loudly, so
 * the guard below refuses that case rather than trust the call site.
 *
 * Bounds guard: the sprite is 2 cells wide and 2 cells tall. A row of cells
 * is 80 bytes wide regardless of mode (mode 0: 20 cells * 4 bytes; mode 1:
 * 40 cells * 2 bytes -- both 80), so the last column a 2-cell sprite can
 * start at is (80 / CELL_BYTES) - 2, i.e. col must be < (80 / CELL_BYTES) - 1.
 * The screen is 25 character rows (200 pixel lines / 8) with no third
 * boundary of its own -- unlike the Spectrum, one bank covers the whole
 * screen -- so the last row a 2-cell-tall sprite can start at is 23, i.e.
 * row must be < 24.
 *
 * Alignment/size: cpct_drawSpriteMasked only requires whole-byte width and a
 * byte-aligned destination (same doc, "As this function receives a
 * byte-pointer to memory..."). Both hold here for free: col*CELL_BYTES is
 * always a whole number of bytes because CELL_BYTES is the byte width of one
 * cell, and SPRITE_BYTES_WIDE (8 in mode 0, 4 in mode 1) is already the
 * sprite's width in whole bytes, not pixels. */
void plat_sprite(unsigned char col, unsigned char row, unsigned char sprite,
                 unsigned char frame) {
#if SPRITE_COUNT
    u8 *screen;
    const u8 *bytes;
    if (sprite >= SPRITE_COUNT) return;
    if (col >= (80 / CELL_BYTES) - 1 || row >= 24) return;
    screen = cpct_getScreenPtr(CPCT_VMEM_START, (u8)(col * CELL_BYTES), (u8)(row * 8));
    bytes = sprite_data[sprite] + sprite_frame_offset[sprite][frame];
    /* SPRITE_BYTES_WIDE is 8 in mode 0 and 4 in mode 1: sixteen pixels across,
     * at the mode's pixels per byte. The mask travels interleaved inside the
     * data, which is what cpct_drawSpriteMasked expects. */
    cpct_drawSpriteMasked((void *)bytes, screen, SPRITE_BYTES_WIDE, 16);
#else
    (void)col; (void)row; (void)sprite; (void)frame;
#endif
}
