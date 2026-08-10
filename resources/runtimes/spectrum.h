#ifndef LLMZ80_SPECTRUM_RUNTIME_H
#define LLMZ80_SPECTRUM_RUNTIME_H

#include <arch/zx.h>
#include <input.h>
#include <intrinsic.h>

#define LLMZ80_SCREEN_W 256
#define LLMZ80_SCREEN_H 192

static void llmz80_wait_frame(void) {
    intrinsic_halt();
}

static int llmz80_key(void) {
    return in_inkey();
}

static unsigned char llmz80_key_pressed(int key) {
    static int previous = 0;
    int current = in_inkey();
    unsigned char pressed = (current == key && previous != key);
    previous = current;
    return pressed;
}

static void llmz80_draw_sprite8(unsigned char x, unsigned char y,
                                const unsigned char *sprite) {
    unsigned char row;
    unsigned char *screen;
    if (x > 248 || y > 184) return;
    screen = zx_pxy2saddr(x, y);
    for (row = 0; row != 8; ++row) {
        *screen = sprite[row];
        screen = zx_saddrpdown(screen);
    }
}

#endif
