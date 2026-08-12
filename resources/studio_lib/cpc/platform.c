/* Amstrad CPC implementation of the Studio engine platform layer.
 *
 * Cells are one 8x8 character block wide, so the engine grid maps directly to
 * CPCtelera's screen pointer arithmetic in both mode 0 and mode 1.
 */
#include <cpctelera.h>

#include "platform.h"
#include "game_config.h"

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

/* Stub: Task 7 gives the CPC its own masked blitter (cpct_drawSpriteMasked
 * against the interleaved mask+colour bytes pack_cpc already produces). This
 * task only wires sprites.h into every build, so a CPC program that calls
 * plat_sprite compiles and links today but draws nothing yet. */
void plat_sprite(unsigned char col, unsigned char row, unsigned char sprite,
                 unsigned char frame) {
    (void)col; (void)row; (void)sprite; (void)frame;
}
