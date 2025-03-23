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
	.globl _drawPixelCount
	.globl _putpixel
	.globl _mixedRandomGenerator
	.globl _initializeRandomGenerators
	.globl _sprintf
	.globl _cpct_getRandom_glfsr16_u8
	.globl _cpct_setTaps_glfsr16
	.globl _cpct_setSeed_glfsr16
	.globl _cpct_setSeed_lcg_u8
	.globl _cpct_getRandom_lcg_u8
	.globl _cpct_getScreenPtr
	.globl _cpct_setVideoMode
	.globl _cpct_drawStringM2
	.globl _cpct_setDrawCharM2
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
;src/main.c:28: void initializeRandomGenerators() {
;	---------------------------------
; Function initializeRandomGenerators
; ---------------------------------
_initializeRandomGenerators::
;src/main.c:29: cpct_setSeed_lcg_u8 (0x55);
	ld	l, #0x55
	call	_cpct_setSeed_lcg_u8
;src/main.c:30: cpct_setSeed_glfsr16(0x1120);
	ld	hl, #0x1120
	call	_cpct_setSeed_glfsr16
;src/main.c:31: cpct_setTaps_glfsr16(GLFSR16_TAPSET_0512);
	ld	hl, #0xbad0
	jp  _cpct_setTaps_glfsr16
;src/main.c:34: u8 mixedRandomGenerator() {
;	---------------------------------
; Function mixedRandomGenerator
; ---------------------------------
_mixedRandomGenerator::
;src/main.c:35: return cpct_getRandom_lcg_u8( cpct_getRandom_glfsr16_u8() );
	call	_cpct_getRandom_glfsr16_u8
	jp  _cpct_getRandom_lcg_u8
;src/main.c:38: void putpixel(u16 x, u8 y, u8 val) {
;	---------------------------------
; Function putpixel
; ---------------------------------
_putpixel::
	push	ix
	ld	ix,#0
	add	ix,sp
;src/main.c:39: u8* vram = cpct_getScreenPtr(CPCT_VMEM_START, x >> 3, y + 8);
	ld	a, 6 (ix)
	add	a, #0x08
	ld	d, a
	ld	b, 4 (ix)
	ld	c, 5 (ix)
	srl	c
	rr	b
	srl	c
	rr	b
	srl	c
	rr	b
	ld	e, b
	push	de
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
;src/main.c:40: u8  byte = *vram;
	ld	b, (hl)
;src/main.c:41: u8  pen  = val << (7 - (x & 7));
	ld	a, 4 (ix)
	and	a, #0x07
	ld	c, a
	ld	a, #0x07
	sub	a, c
	ld	c, 7 (ix)
	inc	a
	jr	00104$
00103$:
	sla	c
00104$:
	dec	a
	jr	NZ,00103$
;src/main.c:42: *vram = byte & (pen ^ 0xFF) | pen;
	ld	a, c
	xor	a, #0xff
	and	a, b
	or	a, c
	ld	(hl), a
	pop	ix
	ret
;src/main.c:45: void drawPixelCount(u16 pixels) {
;	---------------------------------
; Function drawPixelCount
; ---------------------------------
_drawPixelCount::
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	hl, #-7
	add	hl, sp
	ld	sp, hl
;src/main.c:46: if (! (pixels & 15) ) {
	ld	a, 4 (ix)
	and	a, #0x0f
	jr	NZ,00103$
;src/main.c:48: sprintf(str, "%6u", pixels);
	ld	hl, #0x0000
	add	hl, sp
	ld	c, l
	ld	b, h
	push	hl
	ld	e,4 (ix)
	ld	d,5 (ix)
	push	de
	ld	de, #___str_0
	push	de
	push	bc
	call	_sprintf
	ld	hl, #6
	add	hl, sp
	ld	sp, hl
	pop	hl
;src/main.c:49: cpct_drawStringM2(str, CPCT_VMEM_START+26);
	ld	bc, #0xc01a
	push	bc
	push	hl
	call	_cpct_drawStringM2
00103$:
	ld	sp, ix
	pop	ix
	ret
___str_0:
	.ascii "%6u"
	.db 0x00
;src/main.c:53: void main(void) {
;	---------------------------------
; Function main
; ---------------------------------
_main::
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	hl, #-6
	add	hl, sp
	ld	sp, hl
;src/main.c:54: u8 last_y = 0x20;
	ld	-5 (ix), #0x20
;src/main.c:57: cpct_disableFirmware();
	call	_cpct_disableFirmware
;src/main.c:58: cpct_setVideoMode(2);
	ld	l, #0x02
	call	_cpct_setVideoMode
;src/main.c:59: cpct_setDrawCharM2(1, 0);
	ld	hl, #0x0001
	push	hl
	call	_cpct_setDrawCharM2
;src/main.c:60: initializeRandomGenerators();
	call	_initializeRandomGenerators
;src/main.c:62: cpct_drawStringM2("Random numbers generated:", CPCT_VMEM_START);
	ld	hl, #0xc000
	push	hl
	ld	hl, #___str_1
	push	hl
	call	_cpct_drawStringM2
;src/main.c:63: while(1) {
	xor	a, a
	ld	-4 (ix), a
	ld	-3 (ix), a
	ld	-2 (ix), a
	ld	-1 (ix), a
00102$:
;src/main.c:64: u8 y = mixedRandomGenerator();
	call	_mixedRandomGenerator
;src/main.c:65: putpixel(last_y, y>>1, 1);
	ld	-6 (ix), l
	ld	d, l
	srl	d
	ld	c, -5 (ix)
	ld	b, #0x00
	ld	a, #0x01
	push	af
	inc	sp
	push	de
	inc	sp
	push	bc
	call	_putpixel
	pop	af
	pop	af
;src/main.c:66: drawPixelCount(i++);
	ld	c, -4 (ix)
	ld	b, -3 (ix)
	inc	-4 (ix)
	jr	NZ,00110$
	inc	-3 (ix)
	jr	NZ,00110$
	inc	-2 (ix)
	jr	NZ,00110$
	inc	-1 (ix)
00110$:
	push	bc
	call	_drawPixelCount
	pop	af
;src/main.c:67: last_y = y;
	ld	a, -6 (ix)
	ld	-5 (ix), a
	jr	00102$
___str_1:
	.ascii "Random numbers generated:"
	.db 0x00
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
