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
	.globl _cpct_setPalette
	.globl _cpct_setVideoMode
	.globl _cpct_drawSprite
	.globl _cpct_disableFirmware
	.globl _g_palette
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
;src/main.c:41: void main(void) {
;	---------------------------------
; Function main
; ---------------------------------
_main::
;src/main.c:43: cpct_disableFirmware();          // Disable firmware (as we are going to use mode and colours)
	call	_cpct_disableFirmware
;src/main.c:44: cpct_setVideoMode(0);            // Set video mode 0 (160x200, 16 colours)
	ld	l, #0x00
	call	_cpct_setVideoMode
;src/main.c:45: cpct_setPalette(g_palette, 5);   // Set first 5 colours from our palette (we aren't going to use more)
	ld	hl, #0x0005
	push	hl
	ld	hl, #_g_palette
	push	hl
	call	_cpct_setPalette
;src/main.c:49: cpct_drawSprite(G_sprite, CPCT_VMEM_START, 8, 24);
	ld	hl, #0x1808
	push	hl
	ld	hl, #0xc000
	push	hl
	ld	hl, #_G_sprite
	push	hl
	call	_cpct_drawSprite
;src/main.c:52: while (1);
00102$:
	jr	00102$
_g_palette:
	.db #0x14	; 20
	.db #0x15	; 21
	.db #0x13	; 19
	.db #0x16	; 22
	.db #0x0e	; 14
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
