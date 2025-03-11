;--------------------------------------------------------
; File Created by SDCC : free open source ANSI-C Compiler
; Version 3.6.8 #9946 (Linux)
;--------------------------------------------------------
	.module anivemin_example
	.optsdcc -mz80
	
;--------------------------------------------------------
; Public variables in this module
;--------------------------------------------------------
	.globl _main
	.globl _cpct_setPalette
	.globl _cpct_waitVSYNC
	.globl _cpct_setVideoMode
	.globl _cpct_drawSolidBox
	.globl _cpct_isKeyPressed
	.globl _cpct_scanKeyboard
	.globl _cpct_memset
	.globl _cpct_disableFirmware
	.globl _border_color
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
_border_color::
	.ds 1
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
;anivemin_example.c:19: void main(void)
;	---------------------------------
; Function main
; ---------------------------------
_main::
;anivemin_example.c:22: cpct_disableFirmware();
	call	_cpct_disableFirmware
;anivemin_example.c:25: cpct_setVideoMode(0);
	ld	l, #0x00
	call	_cpct_setVideoMode
;anivemin_example.c:28: cpct_setPalette(g_palette, 16);
	ld	hl, #0x0010
	push	hl
	ld	hl, #_g_palette
	push	hl
	call	_cpct_setPalette
;anivemin_example.c:31: cpct_clearScreen(0);
	ld	hl, #0x4000
	push	hl
	xor	a, a
	push	af
	inc	sp
	ld	h, #0xc0
	push	hl
	call	_cpct_memset
;anivemin_example.c:34: cpct_drawSolidBox((void *)0xC000, border_color, 40, 200);
	ld	hl,#_border_color + 0
	ld	c, (hl)
	ld	b, #0x00
	ld	hl, #0xc828
	push	hl
	push	bc
	ld	hl, #0xc000
	push	hl
	call	_cpct_drawSolidBox
;anivemin_example.c:35: cpct_drawSolidBox((void *)(0xC000 + 40 * 4 - 4), border_color, 4, 200);
	ld	hl,#_border_color + 0
	ld	c, (hl)
	ld	b, #0x00
	ld	hl, #0xc804
	push	hl
	push	bc
	ld	hl, #0xc09c
	push	hl
	call	_cpct_drawSolidBox
;anivemin_example.c:36: cpct_drawSolidBox((void *)0xC000, border_color, 40 * 4, 8);
	ld	hl,#_border_color + 0
	ld	c, (hl)
	ld	b, #0x00
	ld	hl, #0x08a0
	push	hl
	push	bc
	ld	hl, #0xc000
	push	hl
	call	_cpct_drawSolidBox
;anivemin_example.c:37: cpct_drawSolidBox((void *)(0xC000 + 80 * 24), border_color, 40 * 4, 8);
	ld	hl,#_border_color + 0
	ld	c, (hl)
	ld	b, #0x00
	ld	hl, #0x08a0
	push	hl
	push	bc
	ld	hl, #0xc780
	push	hl
	call	_cpct_drawSolidBox
;anivemin_example.c:40: while (1)
00107$:
;anivemin_example.c:43: cpct_scanKeyboard();
	call	_cpct_scanKeyboard
;anivemin_example.c:46: if (cpct_isKeyPressed(Key_Space))
	ld	hl, #0x8005
	call	_cpct_isKeyPressed
	ld	a, l
	or	a, a
	jr	Z,00105$
;anivemin_example.c:48: border_color = (border_color + 1) % 16;
	ld	hl,#_border_color + 0
	ld	c, (hl)
	ld	b, #0x00
	inc	bc
	ld	hl, #0x0010
	push	hl
	push	bc
	call	__modsint
	pop	af
	pop	af
	ld	iy, #_border_color
	ld	0 (iy), l
;anivemin_example.c:51: cpct_drawSolidBox((void *)0xC000, border_color, 40, 200);
	ld	c, 0 (iy)
	ld	b, #0x00
	ld	hl, #0xc828
	push	hl
	push	bc
	ld	hl, #0xc000
	push	hl
	call	_cpct_drawSolidBox
;anivemin_example.c:52: cpct_drawSolidBox((void *)(0xC000 + 40 * 4 - 4), border_color, 4, 200);
	ld	hl,#_border_color + 0
	ld	c, (hl)
	ld	b, #0x00
	ld	hl, #0xc804
	push	hl
	push	bc
	ld	hl, #0xc09c
	push	hl
	call	_cpct_drawSolidBox
;anivemin_example.c:53: cpct_drawSolidBox((void *)0xC000, border_color, 40 * 4, 8);
	ld	hl,#_border_color + 0
	ld	c, (hl)
	ld	b, #0x00
	ld	hl, #0x08a0
	push	hl
	push	bc
	ld	hl, #0xc000
	push	hl
	call	_cpct_drawSolidBox
;anivemin_example.c:54: cpct_drawSolidBox((void *)(0xC000 + 80 * 24), border_color, 40 * 4, 8);
	ld	hl,#_border_color + 0
	ld	c, (hl)
	ld	b, #0x00
	ld	hl, #0x08a0
	push	hl
	push	bc
	ld	hl, #0xc780
	push	hl
	call	_cpct_drawSolidBox
;anivemin_example.c:57: while (cpct_isKeyPressed(Key_Space))
00101$:
	ld	hl, #0x8005
	call	_cpct_isKeyPressed
	ld	a, l
	or	a, a
	jr	Z,00105$
;anivemin_example.c:59: cpct_scanKeyboard();
	call	_cpct_scanKeyboard
;anivemin_example.c:60: cpct_waitVSYNC();
	call	_cpct_waitVSYNC
	jr	00101$
00105$:
;anivemin_example.c:65: cpct_waitVSYNC();
	call	_cpct_waitVSYNC
	jp	00107$
_g_palette:
	.db #0x00	; 0
	.db #0x03	; 3
	.db #0x06	; 6
	.db #0x09	; 9
	.db #0x0c	; 12
	.db #0x0f	; 15
	.db #0x12	; 18
	.db #0x15	; 21
	.db #0x18	; 24
	.db #0x1a	; 26
	.db #0x1c	; 28
	.db #0x1e	; 30
	.db #0x1f	; 31
	.db #0x16	; 22
	.db #0x0e	; 14
	.db #0x06	; 6
	.area _CODE
	.area _INITIALIZER
__xinit__border_color:
	.db #0x01	; 1
	.area _CABS (ABS)
