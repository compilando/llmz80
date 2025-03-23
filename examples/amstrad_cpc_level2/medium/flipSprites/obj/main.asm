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
	.globl _cpct_setPalette
	.globl _cpct_setVideoMode
	.globl _cpct_drawStringM0
	.globl _cpct_setDrawCharM0
	.globl _cpct_drawSprite
	.globl _cpct_drawSolidBox
	.globl _cpct_px2byteM0
	.globl _cpct_hflipSpriteM0
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
;src/main.c:42: void initialize() {
;	---------------------------------
; Function initialize
; ---------------------------------
_initialize::
;src/main.c:46: cpct_disableFirmware();
	call	_cpct_disableFirmware
;src/main.c:49: cpct_setPalette(g_palette, 16);
	ld	hl, #0x0010
	push	hl
	ld	hl, #_g_palette
	push	hl
	call	_cpct_setPalette
;src/main.c:50: cpct_setBorder(HW_BLACK);
	ld	hl, #0x1410
	push	hl
	call	_cpct_setPALColour
;src/main.c:53: cpct_setVideoMode(0);
	ld	l, #0x00
	call	_cpct_setVideoMode
;src/main.c:57: pvideomem = cpct_getScreenPtr(CPCT_VMEM_START,       0, FLOOR_Y);
	ld	hl, #0xa000
	push	hl
	ld	h, #0xc0
	push	hl
	call	_cpct_getScreenPtr
;src/main.c:58: cpct_drawSolidBox(pvideomem, FLOOR_COLOR, SCR_W/2, FLOOR_HEIGHT);
	push	hl
	ld	bc, #0x0201
	push	bc
	call	_cpct_px2byteM0
	ld	c, l
	pop	hl
	ld	b, #0x00
	ld	de, #0x0a28
	push	de
	push	bc
	push	hl
	call	_cpct_drawSolidBox
;src/main.c:59: pvideomem = cpct_getScreenPtr(CPCT_VMEM_START, SCR_W/2, FLOOR_Y);
	ld	hl, #0xa028
	push	hl
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
;src/main.c:60: cpct_drawSolidBox(pvideomem, FLOOR_COLOR, SCR_W/2, FLOOR_HEIGHT);
	push	hl
	ld	bc, #0x0201
	push	bc
	call	_cpct_px2byteM0
	ld	c, l
	pop	hl
	ld	b, #0x00
	ld	de, #0x0a28
	push	de
	push	bc
	push	hl
	call	_cpct_drawSolidBox
;src/main.c:63: pvideomem = cpct_getScreenPtr(CPCT_VMEM_START,  0, 20);
	ld	hl, #0x1400
	push	hl
	ld	h, #0xc0
	push	hl
	call	_cpct_getScreenPtr
;src/main.c:64: cpct_setDrawCharM0(2, 0);
	push	hl
	ld	bc, #0x0002
	push	bc
	call	_cpct_setDrawCharM0
	pop	hl
;src/main.c:65: cpct_drawStringM0("  Sprite Flip Demo  ", pvideomem);
	ld	bc, #___str_0+0
	push	hl
	push	bc
	call	_cpct_drawStringM0
;src/main.c:66: pvideomem = cpct_getScreenPtr(CPCT_VMEM_START,  0, 34);
	ld	hl, #0x2200
	push	hl
	ld	h, #0xc0
	push	hl
	call	_cpct_getScreenPtr
;src/main.c:67: cpct_setDrawCharM0(4, 0);
	push	hl
	ld	bc, #0x0004
	push	bc
	call	_cpct_setDrawCharM0
	pop	hl
;src/main.c:68: cpct_drawStringM0("[Cursor]",   pvideomem);
	ld	bc, #___str_1+0
	push	hl
	push	bc
	call	_cpct_drawStringM0
;src/main.c:69: pvideomem = cpct_getScreenPtr(CPCT_VMEM_START, 40, 34);
	ld	hl, #0x2228
	push	hl
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
;src/main.c:70: cpct_setDrawCharM0(3, 0);
	push	hl
	ld	bc, #0x0003
	push	bc
	call	_cpct_setDrawCharM0
	pop	hl
;src/main.c:71: cpct_drawStringM0("Left/Right", pvideomem);
	ld	bc, #___str_2+0
	push	hl
	push	bc
	call	_cpct_drawStringM0
	ret
___str_0:
	.ascii "  Sprite Flip Demo  "
	.db 0x00
___str_1:
	.ascii "[Cursor]"
	.db 0x00
___str_2:
	.ascii "Left/Right"
	.db 0x00
;src/main.c:77: void main(void) {
;	---------------------------------
; Function main
; ---------------------------------
_main::
	push	ix
	ld	ix,#0
	add	ix,sp
	dec	sp
;src/main.c:78: u8 x=20;                     // Sprite horizontal coordinate
	ld	c, #0x14
;src/main.c:79: u8 lookingAt = LOOK_RIGHT;   // Know where the sprite is looking at 
	ld	-1 (ix), #0x01
;src/main.c:80: u8 nowLookingAt = lookingAt; // New looking direction after keypress
	ld	b, #0x01
;src/main.c:83: initialize();
	push	bc
	call	_initialize
	pop	bc
;src/main.c:88: while(1) {
00111$:
;src/main.c:94: cpct_scanKeyboard_f();
	push	bc
	call	_cpct_scanKeyboard_f
	ld	hl, #0x0200
	call	_cpct_isKeyPressed
	pop	bc
	ld	a, l
	or	a, a
	jr	Z,00105$
	ld	a, c
	sub	a, #0x39
	jr	NC,00105$
;src/main.c:99: ++x;
	inc	c
;src/main.c:100: nowLookingAt = LOOK_RIGHT;
	ld	b, #0x01
	jr	00106$
00105$:
;src/main.c:101: } else if (cpct_isKeyPressed(Key_CursorLeft)  && x > 0) {
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
;src/main.c:102: --x; 
	dec	c
;src/main.c:103: nowLookingAt = LOOK_LEFT;
	ld	b, #0x00
00106$:
;src/main.c:107: if (lookingAt != nowLookingAt) {
	ld	a, -1 (ix)
	sub	a, b
	jr	Z,00109$
;src/main.c:108: lookingAt = nowLookingAt;
	ld	-1 (ix), b
;src/main.c:109: cpct_hflipSpriteM0(SP_W, SP_H, g_spirit);
	push	bc
	ld	hl, #_g_spirit
	push	hl
	ld	hl, #0x3617
	push	hl
	call	_cpct_hflipSpriteM0
	pop	bc
00109$:
;src/main.c:113: pvideomem = cpct_getScreenPtr(CPCT_VMEM_START, x, FLOOR_Y - SP_H);
	push	bc
	ld	b, #0x6a
	push	bc
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
	ex	de,hl
	ld	hl, #0x3617
	push	hl
	push	de
	ld	hl, #_g_spirit
	push	hl
	call	_cpct_drawSprite
	pop	bc
	jr	00111$
	inc	sp
	pop	ix
	ret
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
