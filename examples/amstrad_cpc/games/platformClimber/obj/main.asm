;--------------------------------------------------------
; File Created by SDCC : free open source ANSI-C Compiler
; Version 3.6.8 #9946 (Linux)
;--------------------------------------------------------
	.module main
	.optsdcc -mz80
	
;--------------------------------------------------------
; Public variables in this module
;--------------------------------------------------------
	.globl _main
	.globl _initializeCPC
	.globl _game
	.globl _showGameEnd
	.globl _cpct_setPALColour
	.globl _cpct_setPalette
	.globl _cpct_fw2hw
	.globl _cpct_setVideoMode
	.globl _cpct_disableFirmware
;--------------------------------------------------------
; special function registers
;--------------------------------------------------------
;--------------------------------------------------------
; ram data
;--------------------------------------------------------
	.area _DATA
;--------------------------------------------------------
; ram data
;--------------------------------------------------------
	.area _INITIALIZED
;--------------------------------------------------------
; absolute external ram data
;--------------------------------------------------------
	.area _DABS (ABS)
;--------------------------------------------------------
; global & static initialisations
;--------------------------------------------------------
	.area _HOME
	.area _GSINIT
	.area _GSFINAL
	.area _GSINIT
;--------------------------------------------------------
; Home
;--------------------------------------------------------
	.area _HOME
	.area _HOME
;--------------------------------------------------------
; code
;--------------------------------------------------------
	.area _CODE
;src/main.c:28: void initializeCPC() {
;	---------------------------------
; Function initializeCPC
; ---------------------------------
_initializeCPC::
;src/main.c:30: cpct_disableFirmware();
	call	_cpct_disableFirmware
;src/main.c:33: cpct_fw2hw(G_palette, 16);
	ld	hl, #0x0010
	push	hl
	ld	hl, #_G_palette
	push	hl
	call	_cpct_fw2hw
;src/main.c:34: cpct_setPalette(G_palette, 16);
	ld	hl, #0x0010
	push	hl
	ld	hl, #_G_palette
	push	hl
	call	_cpct_setPalette
;src/main.c:35: cpct_setBorder(G_palette[8]);
	ld	hl, #_G_palette + 8
	ld	b, (hl)
	push	bc
	inc	sp
	ld	a, #0x10
	push	af
	inc	sp
	call	_cpct_setPALColour
;src/main.c:38: cpct_setVideoMode(0);
	ld	l, #0x00
	call	_cpct_setVideoMode
	ret
;src/main.c:45: void main(void) {
;	---------------------------------
; Function main
; ---------------------------------
_main::
;src/main.c:47: u16 hi = 0;    // Hi-score
	ld	bc, #0x0000
;src/main.c:50: initializeCPC();
	push	bc
	call	_initializeCPC
	pop	bc
;src/main.c:55: while(1) {
00104$:
;src/main.c:56: score = game(hi);    // Play a game and get the score
	push	bc
	push	bc
	call	_game
	pop	af
	pop	bc
;src/main.c:57: showGameEnd(score);  // Show end-game stats
	push	hl
	push	bc
	push	hl
	call	_showGameEnd
	pop	af
	pop	bc
	pop	hl
;src/main.c:59: if (score > hi)      // Update hi-score
	ld	a, c
	sub	a, l
	ld	a, b
	sbc	a, h
	jr	NC,00104$
;src/main.c:60: hi = score;
	ld	c, l
	ld	b, h
	jr	00104$
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
