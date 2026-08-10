#ifndef LLMZ80_AMSTRAD_CPC_RUNTIME_H
#define LLMZ80_AMSTRAD_CPC_RUNTIME_H

#include <cpctelera.h>

#define LLMZ80_CPC_SCREEN_W_BYTES 80
#define LLMZ80_CPC_SCREEN_H 200

static void llmz80_wait_frame(void) {
    cpct_waitVSYNC();
}

static void llmz80_scan_input(void) {
    cpct_scanKeyboard_f();
}

static u8 llmz80_key_pressed_once(cpct_keyID key) {
    static cpct_keyID previous = 0;
    cpct_keyID current = cpct_isKeyPressed(key) ? key : 0;
    u8 pressed = (current == key && previous != key);
    previous = current;
    return pressed;
}

static void llmz80_draw_sprite(u8 x_bytes, u8 y, const u8 *sprite,
                               u8 width_bytes, u8 height) {
    u8 *screen;
    if (width_bytes == 0 || height == 0) return;
    if (x_bytes > LLMZ80_CPC_SCREEN_W_BYTES - width_bytes) return;
    if (y > LLMZ80_CPC_SCREEN_H - height) return;
    screen = cpct_getScreenPtr(CPCT_VMEM_START, x_bytes, y);
    cpct_drawSprite((void *)sprite, screen, width_bytes, height);
}

#endif
