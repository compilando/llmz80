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
	.globl _cpct_getScreenPtr
	.globl _cpct_setPalette
	.globl _cpct_setVideoMode
	.globl _cpct_drawSprite
	.globl _cpct_isKeyPressed
	.globl _cpct_scanKeyboard_f
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
;src/main.c:34: void main(void) {
;	---------------------------------
; Function main
; ---------------------------------
_main::
;src/main.c:35: u8  x=10, y=10;   // Sprite coordinates
	ld	bc,#0x0a0a
;src/main.c:42: cpct_disableFirmware();
	push	bc
	call	_cpct_disableFirmware
	ld	hl, #0x0004
	push	hl
	ld	hl, #_G_palette
	push	hl
	call	_cpct_setPalette
	ld	l, #0x01
	call	_cpct_setVideoMode
	pop	bc
;src/main.c:53: while(1) {
00116$:
;src/main.c:57: cpct_scanKeyboard_f();
	push	bc
	call	_cpct_scanKeyboard_f
	ld	hl, #0x0200
	call	_cpct_isKeyPressed
	pop	bc
	ld	a, l
	or	a, a
	jr	Z,00105$
	ld	a, c
	sub	a, #0x44
	jr	NC,00105$
	inc	c
	jr	00106$
00105$:
;src/main.c:62: else if (cpct_isKeyPressed(Key_CursorLeft)  && x > 0              ) --x; 
	push	bc
	ld	hl, #0x0101
	call	_cpct_isKeyPressed
	pop	bc
	ld	a, l
	or	a, a
	jr	Z,00106$
	ld	a, c
	or	a, a
	jr	Z,00106$
	dec	c
00106$:
;src/main.c:63: if      (cpct_isKeyPressed(Key_CursorUp)    && y > 0              ) --y;
	push	bc
	ld	hl, #0x0100
	call	_cpct_isKeyPressed
	pop	bc
	ld	a, l
	or	a, a
	jr	Z,00112$
	ld	a, b
	or	a, a
	jr	Z,00112$
	dec	b
	jr	00113$
00112$:
;src/main.c:64: else if (cpct_isKeyPressed(Key_CursorDown)  && y < (SCR_H - SP_H) ) ++y;
	push	bc
	ld	hl, #0x0400
	call	_cpct_isKeyPressed
	pop	bc
	ld	a, l
	or	a, a
	jr	Z,00113$
	ld	a, b
	sub	a, #0x8a
	jr	NC,00113$
	inc	b
00113$:
;src/main.c:67: pvideomem = cpct_getScreenPtr(CPCT_VMEM_START, x, y);
	push	bc
	push	bc
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
	ex	de,hl
	ld	hl, #0x3e0c
	push	hl
	push	de
	ld	hl, #_G_ctlogo
	push	hl
	call	_cpct_drawSprite
	pop	bc
	jr	00116$
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
