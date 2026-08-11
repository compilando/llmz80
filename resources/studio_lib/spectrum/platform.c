/* ZX Spectrum implementation of the Studio engine platform layer.
 *
 * Text is rendered straight from the ROM font instead of stdio so the binary
 * stays small and drawing is fully deterministic under the emulator harness.
 */
#include <arch/zx.h>
#include <input.h>
#include <intrinsic.h>
#include <sound.h>

#include "platform.h"
#include "game_config.h"

#define ROM_FONT ((const unsigned char *)0x3D00)
#define FRAMES ((volatile unsigned char *)23672)

static const unsigned char shape_player[8] = {0x18, 0x3C, 0x7E, 0xFF, 0xFF, 0x7E, 0x3C, 0x18};
static const unsigned char shape_enemy[8] = {0x3C, 0x7E, 0xDB, 0xFF, 0xFF, 0xA5, 0x99, 0x00};
static const unsigned char shape_item[8] = {0x00, 0x00, 0x18, 0x3C, 0x3C, 0x18, 0x00, 0x00};
static const unsigned char shape_wall[8] = {0xFF, 0xDF, 0xDF, 0xFF, 0xFD, 0xFD, 0xFF, 0x00};

static void put_glyph(unsigned char col, unsigned char row, const unsigned char *glyph,
                      unsigned char attribute) {
    unsigned char *address = (unsigned char *)zx_cxy2saddr(col, row);
    unsigned char *attributes = (unsigned char *)zx_cxy2aaddr(col, row);
    unsigned char line;
    for (line = 0; line < 8; ++line) {
        address[(unsigned int)line << 8] = glyph[line];
    }
    *attributes = attribute;
}

void plat_init(void) {
    /* Without this the ROM frame counter never advances, so plat_wait_frame
     * degenerates into a busy loop and reports a frame cost of zero forever. */
    intrinsic_ei();
    zx_border(INK_BLACK);
    zx_cls(PAPER_BLACK | INK_WHITE);
}

void plat_clear(void) {
    zx_cls(PAPER_BLACK | INK_WHITE);
}

void plat_border(unsigned char colour) {
    zx_border(colour);
}

/* Uses the ROM frame counter, with a guard so a stopped interrupt cannot hang.
 * The counter also measures the work: the number of frames that elapsed since
 * the previous wait is exactly what the last iteration cost. */
unsigned char plat_wait_frame(void) {
    static unsigned char previous;
    unsigned char start = *FRAMES;
    /* One frame between consecutive waits means the work kept pace, so the
     * frames actually lost is the elapsed count less that one. */
    unsigned char elapsed = (unsigned char)(start - previous);
    unsigned char cost = elapsed > 1 ? (unsigned char)(elapsed - 1) : 0;
    unsigned int guard = 0;
    while (*FRAMES == start && ++guard < 12000) {
    }
    previous = *FRAMES;
    return cost;
}

unsigned char plat_input(void) {
    unsigned char keys = 0;
#if CONTROL_SCHEME == 1
    if (in_key_pressed(IN_KEY_SCANCODE_5)) keys |= IN_LEFT;
    if (in_key_pressed(IN_KEY_SCANCODE_8)) keys |= IN_RIGHT;
    if (in_key_pressed(IN_KEY_SCANCODE_7)) keys |= IN_UP;
    if (in_key_pressed(IN_KEY_SCANCODE_6)) keys |= IN_DOWN;
#else
    if (in_key_pressed(IN_KEY_SCANCODE_o)) keys |= IN_LEFT;
    if (in_key_pressed(IN_KEY_SCANCODE_p)) keys |= IN_RIGHT;
    if (in_key_pressed(IN_KEY_SCANCODE_q)) keys |= IN_UP;
    if (in_key_pressed(IN_KEY_SCANCODE_a)) keys |= IN_DOWN;
#endif
    if (in_key_pressed(IN_KEY_SCANCODE_SPACE)) keys |= IN_ACTION;
    return keys;
}

void plat_text(unsigned char col, unsigned char row, const char *text) {
    while (*text != 0 && col < 32) {
        unsigned char code = (unsigned char)*text;
        if (code >= 32) {
            put_glyph(col, row, ROM_FONT + (((unsigned int)(code - 32)) << 3),
                      PAPER_BLACK | INK_WHITE);
        }
        ++col;
        ++text;
    }
}

void plat_cell(unsigned char col, unsigned char row, unsigned char kind) {
    static const unsigned char blank[8] = {0, 0, 0, 0, 0, 0, 0, 0};
    if (col >= 32 || row >= 24) return;
    if (kind == CELL_PLAYER) {
        put_glyph(col, row, shape_player, PAPER_BLACK | INK_WHITE | BRIGHT);
    } else if (kind == CELL_ENEMY) {
        put_glyph(col, row, shape_enemy, PAPER_BLACK | INK_RED | BRIGHT);
    } else if (kind == CELL_COLLECTIBLE) {
        put_glyph(col, row, shape_item, PAPER_BLACK | INK_YELLOW | BRIGHT);
    } else if (kind == CELL_WALL) {
        put_glyph(col, row, shape_wall, PAPER_BLACK | INK_CYAN);
    } else {
        put_glyph(col, row, blank, PAPER_BLACK | INK_WHITE);
    }
}

/* Beeper effects through z88dk's certified bit_beep, kept short because the
 * call blocks: every millisecond spent here is a millisecond the game loop is
 * not running. AUDIO_EFFECT_MASK lets the design switch each effect off. */
void plat_sound(unsigned char effect) {
#if AUDIO_EFFECT_MASK
    if (!(AUDIO_EFFECT_MASK & (1 << effect))) return;
    switch (effect) {
        case SOUND_COLLECT: bit_beep(6, 250); break;
        case SOUND_HIT: bit_beep(18, 900); break;
        case SOUND_START: bit_beep(10, 400); break;
        case SOUND_LEVEL: bit_beep(10, 300); break;
        case SOUND_GAME_OVER: bit_beep(30, 1400); break;
        default: break;
    }
#else
    (void)effect;
#endif
}
