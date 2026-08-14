/* LLMZ80 Studio engine: platform abstraction.
 *
 * Every target implements this header. The shared engine never touches target
 * headers, so gameplay rules stay identical on ZX Spectrum and Amstrad CPC.
 * Types are plain C so the header compiles under z88dk/sdcc and SDCC alike.
 */
#ifndef LLMZ80_PLATFORM_H
#define LLMZ80_PLATFORM_H

/* Input is one bit per binding the design declared. game_config.h names each
 * bit (INPUT_LEFT, INPUT_JUMP, whatever the design coined) and lists them all
 * in the INPUT_BINDINGS X-macro, so this header fixes no key and no meaning. */
void plat_init(void);
void plat_clear(void);
/* Waits for the next display frame and returns how many whole display frames
 * elapsed while the previous iteration did its work. Zero means the work fitted
 * inside its frame; anything higher counts frames the loop missed. Targets with
 * no free-running frame clock always return zero, and game_config.h reports
 * which is which through HAS_FRAME_CLOCK. */
unsigned char plat_wait_frame(void);
unsigned char plat_input(void);
void plat_text(unsigned char col, unsigned char row, const char *text);
/* Draws one character of the ROM font at a character cell. This is how terrain
 * is drawn until real tile artwork lands: a design's tile carries a character,
 * and this puts it on screen. */
void plat_cell(unsigned char col, unsigned char row, char glyph);
void plat_border(unsigned char colour);

/* Draws one 16x16 masked sprite whose top-left corner sits at character cell
 * (col, row), so it covers two cells each way. Sprites come from sprites.h,
 * which Studio generates beside your sources; SPRITE_COUNT is zero when the
 * design carries no artwork, and then this does nothing. */
void plat_sprite(unsigned char col, unsigned char row, unsigned char sprite,
                 unsigned char frame);

/* Plays effect N, where N is the index the design gave it -- game_config.h
 * defines SOUND_<NAME> for each one it declared. What each index sounds like
 * is this library's business; what it is called is the design's. A target
 * with no audio implements this as a no-op, and the design gate refuses a
 * project that asks a silent machine for sound. */
void plat_sound(unsigned char effect);

#endif
