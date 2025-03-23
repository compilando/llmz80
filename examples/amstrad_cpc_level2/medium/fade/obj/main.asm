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
	.globl _wait_frames
	.globl _setBlackPalette
	.globl _fade_out
	.globl _fade_in
	.globl _cpct_getScreenPtr
	.globl _cpct_setVideoMode
	.globl _cpct_drawSprite
	.globl _cpct_memset
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
;src/main.c:29: void main(void) {
;	---------------------------------
; Function main
; ---------------------------------
_main::
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	hl, #-21
	add	hl, sp
	ld	sp, hl
;src/main.c:31: const TSprite img[3] = { 
	ld	hl, #0x0001
	add	hl, sp
	ld	bc, #_G_Goku+0
	ld	(hl), c
	inc	hl
	ld	(hl), b
	ld	hl, #0x0001
	add	hl, sp
	ld	c,l
	ld	b,h
	inc	hl
	inc	hl
	ld	(hl), #0x1e
	ld	l, c
	ld	h, b
	inc	hl
	inc	hl
	inc	hl
	ld	(hl), #0x4b
	ld	hl, #0x0004
	add	hl, bc
	ld	(hl), #0x14
	ld	hl, #0x0005
	add	hl, bc
	ld	(hl), #0x31
	ld	hl, #0x0006
	add	hl, bc
	ld	de, #_G_Vegeta+0
	ld	(hl), e
	inc	hl
	ld	(hl), d
	ld	hl, #0x0008
	add	hl, bc
	ld	(hl), #0x16
	ld	hl, #0x0009
	add	hl, bc
	ld	(hl), #0x3c
	ld	hl, #0x000a
	add	hl, bc
	ld	(hl), #0x24
	ld	hl, #0x000b
	add	hl, bc
	ld	(hl), #0x50
	ld	hl, #0x000c
	add	hl, bc
	ld	de, #_G_No13+0
	ld	(hl), e
	inc	hl
	ld	(hl), d
	ld	hl, #0x000e
	add	hl, bc
	ld	(hl), #0x16
	ld	hl, #0x000f
	add	hl, bc
	ld	(hl), #0x3c
	ld	hl, #0x0010
	add	hl, bc
	ld	(hl), #0x24
	ld	hl, #0x0011
	add	hl, bc
	ld	(hl), #0x50
;src/main.c:40: cpct_disableFirmware();   // Disable firmware to prevent it from interfering
	push	bc
	call	_cpct_disableFirmware
	ld	l, #0x00
	call	_cpct_setVideoMode
	ld	hl, #0x1000
	push	hl
	call	_setBlackPalette
	pop	af
	pop	bc
;src/main.c:50: for(i=0; i < 3; ++i) {
00109$:
	ld	-21 (ix), #0x00
00105$:
;src/main.c:51: cpct_clearScreen(0x00);   // Clear the screen filling it up with 0's
	push	bc
	ld	hl, #0x4000
	push	hl
	xor	a, a
	push	af
	inc	sp
	ld	h, #0xc0
	push	hl
	call	_cpct_memset
	pop	bc
;src/main.c:54: pvmem = cpct_getScreenPtr(CPCT_VMEM_START, img[i].x, img[i].y);
	ld	e,-21 (ix)
	ld	d,#0x00
	ld	l, e
	ld	h, d
	add	hl, hl
	add	hl, de
	add	hl, hl
	add	hl,bc
	ex	de,hl
	push	de
	pop	iy
	ld	a, 3 (iy)
	ld	-1 (ix), a
	ld	l, e
	ld	h, d
	inc	hl
	inc	hl
	ld	a, (hl)
	ld	-2 (ix), a
	push	bc
	push	de
	ld	h, -1 (ix)
	ld	l, -2 (ix)
	push	hl
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
	pop	de
	pop	bc
	push	hl
	pop	iy
;src/main.c:55: cpct_drawSprite(img[i].sprite, pvmem, img[i].w, img[i].h);
	ld	l, e
	ld	h, d
	inc	hl
	inc	hl
	inc	hl
	inc	hl
	inc	hl
	ld	a, (hl)
	ld	-2 (ix), a
	ld	l, e
	ld	h, d
	inc	hl
	inc	hl
	inc	hl
	inc	hl
	ld	a, (hl)
	ld	-1 (ix), a
	ex	de,hl
	ld	e, (hl)
	inc	hl
	ld	d, (hl)
	push	bc
	ld	h, -2 (ix)
	ld	l, -1 (ix)
	push	hl
	push	iy
	push	de
	call	_cpct_drawSprite
	ld	hl, #0x0032
	push	hl
	call	_wait_frames
	ld	hl, #0x0410
	ex	(sp),hl
	xor	a, a
	push	af
	inc	sp
	ld	hl, #_G_rgb_palette
	push	hl
	call	_fade_in
	pop	af
	inc	sp
	ld	hl,#0x0064
	ex	(sp),hl
	call	_wait_frames
	ld	hl, #0x0410
	ex	(sp),hl
	xor	a, a
	push	af
	inc	sp
	ld	hl, #_G_rgb_palette
	push	hl
	call	_fade_out
	pop	af
	pop	af
	inc	sp
	pop	bc
;src/main.c:50: for(i=0; i < 3; ++i) {
	inc	-21 (ix)
	ld	a, -21 (ix)
	sub	a, #0x03
	jp	C, 00105$
	jp	00109$
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
