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
	.globl _initialize
	.globl _cpct_getScreenPtr
	.globl _cpct_setPALColour
	.globl _cpct_waitVSYNC
	.globl _cpct_setVideoMode
	.globl _cpct_drawStringM2
	.globl _cpct_setDrawCharM2
	.globl _cpct_drawSprite
	.globl _cpct_drawSolidBox
	.globl _cpct_hflipSpriteM2
	.globl _cpct_isAnyKeyPressed
	.globl _cpct_scanKeyboard_f
	.globl _cpct_disableFirmware
	.globl _g_animation
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
;src/main.c:52: void initialize() {
;	---------------------------------
; Function initialize
; ---------------------------------
_initialize::
;src/main.c:56: cpct_disableFirmware();
	call	_cpct_disableFirmware
;src/main.c:59: cpct_setBorder(HW_BLACK);
	ld	hl, #0x1410
	push	hl
	call	_cpct_setPALColour
;src/main.c:60: cpct_setPALColour(0, HW_BLACK);
	ld	hl, #0x1400
	push	hl
	call	_cpct_setPALColour
;src/main.c:61: cpct_setPALColour(1, HW_WHITE);
	ld	hl, #0x0001
	push	hl
	call	_cpct_setPALColour
;src/main.c:64: cpct_setVideoMode(2);
	ld	l, #0x02
	call	_cpct_setVideoMode
;src/main.c:68: cpct_drawSprite(g_banner_0, CPCT_VMEM_START             , BANNER_W/2, BANNER_H);
	ld	hl, #0x3428
	push	hl
	ld	hl, #0xc000
	push	hl
	ld	hl, #_g_banner_0
	push	hl
	call	_cpct_drawSprite
;src/main.c:69: cpct_drawSprite(g_banner_1, CPCT_VMEM_START + BANNER_W/2, BANNER_W/2, BANNER_H);
	ld	hl, #0x3428
	push	hl
	ld	h, #0xc0
	push	hl
	ld	hl, #_g_banner_1
	push	hl
	call	_cpct_drawSprite
;src/main.c:72: pvideomem = cpct_getScreenPtr(CPCT_VMEM_START, 29, 60);
	ld	hl, #0x3c1d
	push	hl
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
;src/main.c:73: cpct_setDrawCharM2(0, 1);
	push	hl
	ld	bc, #0x0100
	push	bc
	call	_cpct_setDrawCharM2
	pop	hl
;src/main.c:74: cpct_drawStringM2("[Any Key] Run Opposite", pvideomem);
	ld	bc, #___str_0+0
	push	hl
	push	bc
	call	_cpct_drawStringM2
	ret
_g_animation:
	.dw _g_runner_0
	.dw _g_runner_1
	.dw _g_runner_2
	.dw _g_runner_3
	.dw _g_runner_4
	.dw _g_runner_5
___str_0:
	.ascii "[Any Key] Run Opposite"
	.db 0x00
;src/main.c:80: void main(void) {
;	---------------------------------
; Function main
; ---------------------------------
_main::
	push	ix
	ld	ix,#0
	add	ix,sp
	push	af
	push	af
	dec	sp
;src/main.c:81: u8  frame  = 0;  // Actual animation frame
	ld	c, #0x00
;src/main.c:82: u8  cycles = 0;  // Number of waiting cycles done for present frame
	ld	-5 (ix), #0x00
;src/main.c:85: u8  floor_color = 0b1101010; // Pixel pattern for the floor
	ld	e, #0x6a
;src/main.c:89: initialize();
	push	bc
	push	de
	call	_initialize
	ld	hl, #0x5622
	push	hl
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
	pop	de
	pop	bc
	ld	-4 (ix), l
	ld	-3 (ix), h
;src/main.c:94: pvmem_floor = cpct_getScreenPtr(CPCT_VMEM_START, FLOOR_X, FLOOR_Y);
	push	bc
	push	de
	ld	hl, #0xb41e
	push	hl
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
	pop	de
	pop	bc
	ld	-2 (ix), l
	ld	-1 (ix), h
;src/main.c:98: while(1) {
00111$:
;src/main.c:102: cpct_scanKeyboard_f();
	push	bc
	push	de
	call	_cpct_scanKeyboard_f
	call	_cpct_isAnyKeyPressed
	pop	de
	pop	bc
	ld	a, l
	or	a, a
	jr	Z,00105$
;src/main.c:107: while (i--) {
	ld	b, #0x06
00101$:
	ld	d, b
	dec	b
	ld	a, d
	or	a, a
	jr	Z,00105$
;src/main.c:108: cpct_hflipSpriteM2(SP_W, SP_H, g_animation[i]);
	ld	l, b
	ld	h, #0x00
	add	hl, hl
	ld	a, l
	add	a, #<(_g_animation)
	ld	l, a
	ld	a, h
	adc	a, #>(_g_animation)
	ld	h, a
	ld	a, (hl)
	inc	hl
	ld	h, (hl)
	ld	l, a
	push	bc
	push	de
	push	hl
	ld	hl, #0x5e0a
	push	hl
	call	_cpct_hflipSpriteM2
	pop	de
	pop	bc
	jr	00101$
00105$:
;src/main.c:116: if (++cycles == wait_cycles) {
	inc	-5 (ix)
	ld	a, -5 (ix)
	sub	a, #0x06
	jr	NZ,00109$
;src/main.c:117: cycles = 0;                   // Restart frame counter
	ld	-5 (ix), #0x00
;src/main.c:118: if (++frame == ANIM_FRAMES) {  // Next animation frame
	inc	c
	ld	a, c
;src/main.c:119: frame = 0;
	sub	a,#0x06
	jr	NZ,00107$
	ld	c,a
00107$:
;src/main.c:122: floor_color ^= 0xFF;
	ld	a, e
	xor	a, #0xff
	ld	e, a
00109$:
;src/main.c:126: cpct_waitVSYNC();
	push	bc
	push	de
	call	_cpct_waitVSYNC
	pop	de
	pop	bc
;src/main.c:129: cpct_drawSprite(g_animation[frame], pvmem_spr, SP_W, SP_H);
	ld	b, -4 (ix)
	ld	d, -3 (ix)
	ld	l, c
	ld	h, #0x00
	add	hl, hl
	ld	a, #<(_g_animation)
	add	a, l
	ld	l, a
	ld	a, #>(_g_animation)
	adc	a, h
	ld	h, a
	ld	a, (hl)
	inc	hl
	ld	h, (hl)
	ld	l, a
	push	hl
	pop	iy
	push	bc
	push	de
	ld	hl, #0x5e0a
	push	hl
	ld	e,b
	push	de
	push	iy
	call	_cpct_drawSprite
	pop	de
	pop	bc
;src/main.c:132: cpct_drawSolidBox(pvmem_floor, floor_color, FLOOR_W, FLOOR_H);
	ld	b, e
	ld	d, #0x00
	push	hl
	ld	l, -2 (ix)
	ld	h, -1 (ix)
	push	hl
	pop	iy
	pop	hl
	push	bc
	push	de
	ld	hl, #0x0a14
	push	hl
	ld	e,b
	push	de
	push	iy
	call	_cpct_drawSolidBox
	pop	de
	pop	bc
	jp	00111$
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
