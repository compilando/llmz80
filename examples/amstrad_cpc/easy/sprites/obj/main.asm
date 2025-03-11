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
	.globl _drawLogo
	.globl _drawBanner
	.globl _cpct_getScreenPtr
	.globl _cpct_setPALColour
	.globl _cpct_setPalette
	.globl _cpct_fw2hw
	.globl _cpct_setVideoMode
	.globl _cpct_drawSprite
	.globl _cpct_memset_f64
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
;src/main.c:37: void drawBanner() {
;	---------------------------------
; Function drawBanner
; ---------------------------------
_drawBanner::
;src/main.c:42: cpct_clearScreen_f64(0);
	ld	hl, #0x4000
	push	hl
	ld	h, #0x00
	push	hl
	ld	h, #0xc0
	push	hl
	call	_cpct_memset_f64
;src/main.c:45: cpct_setPalette  (G_banner_palette, 16);
	ld	hl, #0x0010
	push	hl
	ld	hl, #_G_banner_palette
	push	hl
	call	_cpct_setPalette
;src/main.c:46: cpct_setVideoMode(0);
	ld	l, #0x00
	call	_cpct_setVideoMode
;src/main.c:54: pvideo_s1 = cpct_getScreenPtr(CPCT_VMEM_START,  0, 52);
	ld	hl, #0x3400
	push	hl
	ld	h, #0xc0
	push	hl
	call	_cpct_getScreenPtr
;src/main.c:55: cpct_drawSprite(G_CPCt_left,  pvideo_s1, BANNER_W, BANNER_H);
	ld	bc, #_G_CPCt_left+0
	ld	de, #0x6028
	push	de
	push	hl
	push	bc
	call	_cpct_drawSprite
;src/main.c:58: pvideo_s2 = cpct_getScreenPtr(CPCT_VMEM_START, 40, 52);
	ld	hl, #0x3428
	push	hl
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
;src/main.c:59: cpct_drawSprite(G_CPCt_right, pvideo_s2, BANNER_W, BANNER_H);
	ld	bc, #_G_CPCt_right+0
	ld	de, #0x6028
	push	de
	push	hl
	push	bc
	call	_cpct_drawSprite
	ret
;src/main.c:65: void drawLogo() {
;	---------------------------------
; Function drawLogo
; ---------------------------------
_drawLogo::
;src/main.c:70: cpct_clearScreen_f64(0);
	ld	hl, #0x4000
	push	hl
	ld	h, #0x00
	push	hl
	ld	h, #0xc0
	push	hl
	call	_cpct_memset_f64
;src/main.c:73: cpct_setPalette(G_logo_palette, 4);
	ld	hl, #0x0004
	push	hl
	ld	hl, #_G_logo_palette
	push	hl
	call	_cpct_setPalette
;src/main.c:74: cpct_setVideoMode(1);     
	ld	l, #0x01
	call	_cpct_setVideoMode
;src/main.c:80: pvideo = cpct_getScreenPtr(CPCT_VMEM_START, 20, 4);
	ld	hl, #0x0414
	push	hl
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
;src/main.c:81: cpct_drawSprite(G_CPCt_logo, pvideo, LOGO_W, LOGO_H);
	ld	bc, #_G_CPCt_logo+0
	ld	de, #0xbf28
	push	de
	push	hl
	push	bc
	call	_cpct_drawSprite
	ret
;src/main.c:87: void main(void) {
;	---------------------------------
; Function main
; ---------------------------------
_main::
;src/main.c:92: cpct_disableFirmware();
	call	_cpct_disableFirmware
;src/main.c:96: cpct_fw2hw(G_banner_palette, 16);
	ld	hl, #0x0010
	push	hl
	ld	hl, #_G_banner_palette
	push	hl
	call	_cpct_fw2hw
;src/main.c:97: cpct_fw2hw(G_logo_palette, 4);
	ld	hl, #0x0004
	push	hl
	ld	hl, #_G_logo_palette
	push	hl
	call	_cpct_fw2hw
;src/main.c:101: cpct_setBorder(G_banner_palette[0]);
	ld	hl, #_G_banner_palette + 0
	ld	b, (hl)
	push	bc
	inc	sp
	ld	a, #0x10
	push	af
	inc	sp
	call	_cpct_setPALColour
;src/main.c:104: while (1) {
00104$:
;src/main.c:106: drawLogo();
	call	_drawLogo
;src/main.c:107: for(i=0; i < WAITLOOPS; ++i);
	ld	bc,#0x49f0
	ld	de,#0x0002
00108$:
	ld	a, c
	add	a, #0xff
	ld	c, a
	ld	a, b
	adc	a, #0xff
	ld	b, a
	ld	a, e
	adc	a, #0xff
	ld	e, a
	ld	a, d
	adc	a, #0xff
	ld	d,a
	or	a, e
	or	a, b
	or	a,c
	jr	NZ,00108$
;src/main.c:110: drawBanner();
	call	_drawBanner
;src/main.c:111: for(i=0; i < WAITLOOPS; ++i);
	ld	bc,#0x49f0
	ld	de,#0x0002
00111$:
	ld	a, c
	add	a, #0xff
	ld	c, a
	ld	a, b
	adc	a, #0xff
	ld	b, a
	ld	a, e
	adc	a, #0xff
	ld	e, a
	ld	a, d
	adc	a, #0xff
	ld	d,a
	or	a, e
	or	a, b
	or	a,c
	jr	NZ,00111$
	jr	00104$
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
