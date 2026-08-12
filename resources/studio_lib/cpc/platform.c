/* Amstrad CPC implementation of the Studio engine platform layer.
 *
 * Cells are one 8x8 character block wide, so the engine grid maps directly to
 * CPCtelera's screen pointer arithmetic in both mode 0 and mode 1.
 */
#include <cpctelera.h>

#include "platform.h"
#include "game_config.h"
#include "sprites.h"

#if CPC_MODE == 0
#define CELL_BYTES 4
#define draw_string cpct_drawStringM0
#define set_draw_char cpct_setDrawCharM0
#else
#define CELL_BYTES 2
#define draw_string cpct_drawStringM1
#define set_draw_char cpct_setDrawCharM1
#endif

/* Mode 1 offers only four pens, so wall, enemy and player take one each and the
 * collectible shares the enemy pen but is drawn as a smaller box. */
#if CPC_MODE == 0
#define PIXELS_PLAYER 0xFF
#define PIXELS_WALL 0x0F
#define PIXELS_ENEMY 0xF0
#else
#define PIXELS_PLAYER 0xFF
#define PIXELS_WALL 0xF0
#define PIXELS_ENEMY 0x0F
#endif
#define PIXELS_ITEM PIXELS_ENEMY
#define PIXELS_EMPTY 0x00

/* Pen 0 black, pen 1 wall, pen 2 actors, pen 3 player. Set explicitly so the
 * result does not depend on whichever palette the firmware left behind.
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
unsigned char plat_wait_frame(void) {
    cpct_waitVSYNC();
    return 0;
}

unsigned char plat_input(void) {
    unsigned char keys = 0;
    cpct_scanKeyboard_f();
    if (cpct_isKeyPressed(Key_CursorLeft)) keys |= IN_LEFT;
    if (cpct_isKeyPressed(Key_CursorRight)) keys |= IN_RIGHT;
    if (cpct_isKeyPressed(Key_CursorUp)) keys |= IN_UP;
    if (cpct_isKeyPressed(Key_CursorDown)) keys |= IN_DOWN;
    if (cpct_isKeyPressed(Key_Space)) keys |= IN_ACTION;
    return keys;
}

void plat_text(unsigned char col, unsigned char row, const char *text) {
    u8 *screen = cpct_getScreenPtr(CPCT_VMEM_START, (u8)(col * CELL_BYTES), (u8)(row * 8));
    draw_string((void *)text, screen);
}

void plat_cell(unsigned char col, unsigned char row, unsigned char kind) {
    u8 *screen;
    if (col >= (80 / CELL_BYTES) || row >= 25) return;
    screen = cpct_getScreenPtr(CPCT_VMEM_START, (u8)(col * CELL_BYTES), (u8)(row * 8));
    if (kind == CELL_COLLECTIBLE) {
        /* Same pen as an enemy, half the height, so the two never look alike. */
        cpct_drawSolidBox(screen, PIXELS_EMPTY, CELL_BYTES, 8);
        screen = cpct_getScreenPtr(CPCT_VMEM_START, (u8)(col * CELL_BYTES), (u8)(row * 8 + 2));
        cpct_drawSolidBox(screen, PIXELS_ITEM, CELL_BYTES, 4);
        return;
    }
    if (kind == CELL_PLAYER) cpct_drawSolidBox(screen, PIXELS_PLAYER, CELL_BYTES, 8);
    else if (kind == CELL_ENEMY) cpct_drawSolidBox(screen, PIXELS_ENEMY, CELL_BYTES, 8);
    else if (kind == CELL_WALL) cpct_drawSolidBox(screen, PIXELS_WALL, CELL_BYTES, 8);
    else cpct_drawSolidBox(screen, PIXELS_EMPTY, CELL_BYTES, 8);
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
