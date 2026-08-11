/* LLMZ80 Studio engine: platform abstraction.
 *
 * Every target implements this header. The shared engine never touches target
 * headers, so gameplay rules stay identical on ZX Spectrum and Amstrad CPC.
 * Types are plain C so the header compiles under z88dk/sdcc and SDCC alike.
 */
#ifndef LLMZ80_PLATFORM_H
#define LLMZ80_PLATFORM_H

#define IN_LEFT 0x01
#define IN_RIGHT 0x02
#define IN_UP 0x04
#define IN_DOWN 0x08
#define IN_ACTION 0x10

/* Cell kinds understood by plat_cell(). Kind 0 erases the cell. */
#define CELL_EMPTY 0
#define CELL_PLAYER 1
#define CELL_ENEMY 2
#define CELL_COLLECTIBLE 3
#define CELL_WALL 4

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
void plat_cell(unsigned char col, unsigned char row, unsigned char kind);
void plat_border(unsigned char colour);

/* Sound effect identifiers, matching AUDIO_EFFECTS in the design model. */
#define SOUND_START 0
#define SOUND_COLLECT 1
#define SOUND_HIT 2
#define SOUND_LEVEL 3
#define SOUND_GAME_OVER 4

/* Plays one effect and returns. Targets without audio implement this as a
 * no-op; the design gate refuses a project that asks for sound the target
 * cannot produce, so silence here is always a declared choice. */
void plat_sound(unsigned char effect);

/* Playfield origin in character cells, reserving the top rows for the HUD. */
#define FIELD_TOP 2

#endif
