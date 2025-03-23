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
	.globl _fillupScreen
	.globl _cpct_getScreenPtr
	.globl _cpct_setVideoMode
	.globl _cpct_drawTileAligned4x8_f
	.globl _cpct_drawTileAligned4x4_f
	.globl _cpct_drawTileAligned2x8_f
	.globl _cpct_drawTileAligned2x4_f
	.globl _cpct_drawTileAligned4x8
	.globl _cpct_drawTileAligned2x8
	.globl _cpct_memset
	.globl _cpct_disableFirmware
	.globl _tiles
	.globl _WAITPAINTED
	.globl _WAITCLEARED
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
;src/main.c:53: void fillupScreen(TTile* tile) {
;	---------------------------------
; Function fillupScreen
; ---------------------------------
_fillupScreen::
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	hl, #-12
	add	hl, sp
	ld	sp, hl
;src/main.c:56: u8 tilesperline = 80/tile->width;   // Number of tiles per line = LINEWIDTH / TILEWIDTH
	ld	c,4 (ix)
	ld	b,5 (ix)
	ld	hl, #0x0002
	add	hl,bc
	ld	-2 (ix), l
	ld	-1 (ix), h
	ld	d, (hl)
	push	bc
	ld	e, #0x50
	push	de
	call	__divuchar
	pop	af
	pop	bc
	ld	-12 (ix), l
;src/main.c:59: for (y=0; y < 200; y += tile->height) { 
	ld	-11 (ix), #0x00
	ld	-4 (ix), c
	ld	-3 (ix), b
	ld	-6 (ix), c
	ld	-5 (ix), b
00113$:
;src/main.c:60: pvideomem = cpct_getScreenPtr(CPCT_VMEM_START, 0, y); // Calculate byte there this pixel line starts
	push	bc
	ld	a, -11 (ix)
	push	af
	inc	sp
	xor	a, a
	push	af
	inc	sp
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
	pop	bc
	ld	-9 (ix), l
	ld	-8 (ix), h
;src/main.c:63: for (x=0; x < tilesperline; x++) {       
	ld	-10 (ix), #0x00
00111$:
	ld	a, -10 (ix)
	sub	a, -12 (ix)
	jp	NC, 00114$
;src/main.c:65: switch (tile->function) {
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	de, #0x0004
	add	hl, de
	ld	a, (hl)
	ld	-7 (ix), a
	ld	a, #0x05
	sub	a, -7 (ix)
	jr	C,00107$
;src/main.c:66: case _2x4Fast: cpct_drawTileAligned2x4_f(tile->sprite, pvideomem); break;
	ld	e, -9 (ix)
	ld	d, -8 (ix)
	push	de
	pop	iy
	ld	l, c
	ld	h, b
	ld	e, (hl)
	inc	hl
	ld	d, (hl)
;src/main.c:65: switch (tile->function) {
	push	de
	ld	e, -7 (ix)
	ld	d, #0x00
	ld	hl, #00134$
	add	hl, de
	add	hl, de
;src/main.c:66: case _2x4Fast: cpct_drawTileAligned2x4_f(tile->sprite, pvideomem); break;
	pop	de
	jp	(hl)
00134$:
	jr	00104$
	jr	00106$
	jr	00101$
	jr	00102$
	jr	00103$
	jr	00105$
00101$:
	push	bc
	push	iy
	push	de
	call	_cpct_drawTileAligned2x4_f
	pop	bc
	jr	00107$
;src/main.c:67: case _4x4Fast: cpct_drawTileAligned4x4_f(tile->sprite, pvideomem); break;
00102$:
	push	bc
	push	iy
	push	de
	call	_cpct_drawTileAligned4x4_f
	pop	bc
	jr	00107$
;src/main.c:68: case _2x8Fast: cpct_drawTileAligned2x8_f(tile->sprite, pvideomem); break;
00103$:
	push	bc
	push	iy
	push	de
	call	_cpct_drawTileAligned2x8_f
	pop	bc
	jr	00107$
;src/main.c:69: case _2x8:     cpct_drawTileAligned2x8  (tile->sprite, pvideomem); break;
00104$:
	push	bc
	push	iy
	push	de
	call	_cpct_drawTileAligned2x8
	pop	bc
	jr	00107$
;src/main.c:70: case _4x8Fast: cpct_drawTileAligned4x8_f(tile->sprite, pvideomem); break;
00105$:
	push	bc
	push	iy
	push	de
	call	_cpct_drawTileAligned4x8_f
	pop	bc
	jr	00107$
;src/main.c:71: case _4x8:     cpct_drawTileAligned4x8  (tile->sprite, pvideomem); break;
00106$:
	push	bc
	push	iy
	push	de
	call	_cpct_drawTileAligned4x8
	pop	bc
;src/main.c:72: }
00107$:
;src/main.c:75: pvideomem += tile->width;
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	ld	e, (hl)
	ld	a, -9 (ix)
	add	a, e
	ld	-9 (ix), a
	ld	a, -8 (ix)
	adc	a, #0x00
	ld	-8 (ix), a
;src/main.c:63: for (x=0; x < tilesperline; x++) {       
	inc	-10 (ix)
	jp	00111$
00114$:
;src/main.c:59: for (y=0; y < 200; y += tile->height) { 
	ld	l,-6 (ix)
	ld	h,-5 (ix)
	inc	hl
	inc	hl
	inc	hl
	ld	e, (hl)
	ld	a, -11 (ix)
	add	a, e
	ld	-11 (ix), a
	sub	a, #0xc8
	jp	C, 00113$
	ld	sp, ix
	pop	ix
	ret
_WAITCLEARED:
	.dw #0x4e20
_WAITPAINTED:
	.dw #0xea60
_tiles:
	.dw _waves_2x4
	.db #0x02	; 2
	.db #0x04	; 4
	.db #0x02	; 2
	.dw _waves_4x4
	.db #0x04	; 4
	.db #0x04	; 4
	.db #0x03	; 3
	.dw _waves_2x8
	.db #0x02	; 2
	.db #0x08	; 8
	.db #0x00	; 0
	.dw _F_2x8
	.db #0x02	; 2
	.db #0x08	; 8
	.db #0x04	; 4
	.dw _waves_4x8
	.db #0x04	; 4
	.db #0x08	; 8
	.db #0x01	; 1
	.dw _FF_4x8
	.db #0x04	; 4
	.db #0x08	; 8
	.db #0x05	; 5
;src/main.c:83: void main(void) {
;	---------------------------------
; Function main
; ---------------------------------
_main::
	push	ix
	ld	ix,#0
	add	ix,sp
	dec	sp
;src/main.c:85: cpct_disableFirmware();
	call	_cpct_disableFirmware
;src/main.c:86: cpct_setVideoMode(0);
	ld	l, #0x00
	call	_cpct_setVideoMode
;src/main.c:96: for (i=0; i < 6; i++) {
00121$:
	ld	-1 (ix), #0x00
00113$:
;src/main.c:98: cpct_clearScreen(0);
	ld	hl, #0x4000
	push	hl
	xor	a, a
	push	af
	inc	sp
	ld	h, #0xc0
	push	hl
	call	_cpct_memset
;src/main.c:99: for (w=0; w < WAITCLEARED; w++);
	ld	de, #0x0000
00108$:
	ld	hl, (_WAITCLEARED)
	ld	a, e
	sub	a, l
	ld	a, d
	sbc	a, h
	jr	NC,00101$
	inc	de
	jr	00108$
00101$:
;src/main.c:102: fillupScreen(&(tiles[i]));
	ld	c,-1 (ix)
	ld	b,#0x00
	ld	l, c
	ld	h, b
	add	hl, hl
	add	hl, hl
	add	hl, bc
	ld	de, #_tiles
	add	hl, de
	push	hl
	call	_fillupScreen
	pop	af
;src/main.c:103: for (w=0; w < WAITPAINTED; w++);
	ld	bc, #0x0000
00111$:
	ld	hl, (_WAITPAINTED)
	ld	a, c
	sub	a, l
	ld	a, b
	sbc	a, h
	jr	NC,00114$
	inc	bc
	jr	00111$
00114$:
;src/main.c:96: for (i=0; i < 6; i++) {
	inc	-1 (ix)
	ld	a, -1 (ix)
	sub	a, #0x06
	jr	C,00113$
	jr	00121$
	inc	sp
	pop	ix
	ret
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
