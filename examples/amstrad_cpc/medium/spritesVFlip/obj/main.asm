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
	.globl _getUserInput
	.globl _clearRockets
	.globl _drawRockets
	.globl _cpct_getScreenPtr
	.globl _cpct_setPALColour
	.globl _cpct_setPalette
	.globl _cpct_waitVSYNC
	.globl _cpct_setVideoMode
	.globl _cpct_drawSprite
	.globl _cpct_drawSolidBox
	.globl _cpct_drawSpriteVFlip
	.globl _cpct_getBottomLeftPtr
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
;src/main.c:37: void drawRockets(u8 x, u8 y) {
;	---------------------------------
; Function drawRockets
; ---------------------------------
_drawRockets::
	push	ix
	ld	ix,#0
	add	ix,sp
;src/main.c:43: pvmem = cpct_getScreenPtr(CPCT_VMEM_START, x, y);
	ld	h, 5 (ix)
	ld	l, 4 (ix)
	push	hl
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
	ld	c, l
	ld	b, h
;src/main.c:45: cpct_drawSprite(g_rocket, pvmem, G_ROCKET_W, G_ROCKET_H);
	push	bc
	ld	hl, #0x0e04
	push	hl
	push	bc
	ld	hl, #_g_rocket
	push	hl
	call	_cpct_drawSprite
	pop	bc
;src/main.c:52: pvmem = cpct_getBottomLeftPtr(pvmem, G_ROCKET_H);
	ld	hl, #0x000e
	push	hl
	push	bc
	call	_cpct_getBottomLeftPtr
;src/main.c:56: pvmem += G_ROCKET_W + 1;
	ld	bc, #0x0005
	add	hl, bc
;src/main.c:60: cpct_drawSpriteVFlip(g_rocket, pvmem, G_ROCKET_W, G_ROCKET_H);  
	ld	bc, #0x0e04
	push	bc
	push	hl
	ld	hl, #_g_rocket
	push	hl
	call	_cpct_drawSpriteVFlip
	pop	ix
	ret
;src/main.c:70: void clearRockets(u8 x, u8 y) {
;	---------------------------------
; Function clearRockets
; ---------------------------------
_clearRockets::
;src/main.c:76: pvmem = cpct_getScreenPtr(CPCT_VMEM_START, x, y);
	ld	hl, #3+0
	add	hl, sp
	ld	a, (hl)
	push	af
	inc	sp
	ld	hl, #3+0
	add	hl, sp
	ld	a, (hl)
	push	af
	inc	sp
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
;src/main.c:80: cpct_drawSolidBox(pvmem, cpctm_px2byteM0(0, 0), 2*G_ROCKET_W+1, G_ROCKET_H);
	ld	bc, #0x0e09
	push	bc
	ld	bc, #0x0000
	push	bc
	push	hl
	call	_cpct_drawSolidBox
	ret
;src/main.c:88: void getUserInput(i8* vx, i8* vy) {
;	---------------------------------
; Function getUserInput
; ---------------------------------
_getUserInput::
	push	ix
	ld	ix,#0
	add	ix,sp
;src/main.c:90: *vx = *vy = 0;
	ld	e,4 (ix)
	ld	d,5 (ix)
	ld	c,6 (ix)
	ld	b,7 (ix)
	xor	a, a
	ld	(bc), a
	xor	a, a
	ld	(de), a
;src/main.c:93: cpct_scanKeyboard_f();
	push	bc
	push	de
	call	_cpct_scanKeyboard_f
	ld	hl, #0x0404
	call	_cpct_isKeyPressed
	pop	de
	pop	bc
	ld	a, l
	or	a, a
	jr	Z,00102$
	ld	a, (de)
	add	a, #0xff
	ld	(de), a
00102$:
;src/main.c:98: if ( cpct_isKeyPressed(Key_P) ) (*vx)++;  // P: Right
	push	bc
	push	de
	ld	hl, #0x0803
	call	_cpct_isKeyPressed
	pop	de
	pop	bc
	ld	a, l
	or	a, a
	jr	Z,00104$
	ld	a, (de)
	inc	a
	ld	(de), a
00104$:
;src/main.c:99: if ( cpct_isKeyPressed(Key_Q) ) (*vy)--;  // Q: Up
	push	bc
	ld	hl, #0x0808
	call	_cpct_isKeyPressed
	pop	bc
	ld	a, l
	or	a, a
	jr	Z,00106$
	ld	a, (bc)
	add	a, #0xff
	ld	(bc), a
00106$:
;src/main.c:100: if ( cpct_isKeyPressed(Key_A) ) (*vy)++;  // A: Down
	push	bc
	ld	hl, #0x2008
	call	_cpct_isKeyPressed
	pop	bc
	ld	a, l
	or	a, a
	jr	Z,00109$
	ld	a, (bc)
	inc	a
	ld	(bc), a
00109$:
	pop	ix
	ret
;src/main.c:107: void initialize() {
;	---------------------------------
; Function initialize
; ---------------------------------
_initialize::
;src/main.c:108: cpct_disableFirmware();          // Disable firmware to prevent it from restoring mode and palette
	call	_cpct_disableFirmware
;src/main.c:109: cpct_setVideoMode(0);            // Set video mode to 0 (160x200, 16 colours)
	ld	l, #0x00
	call	_cpct_setVideoMode
;src/main.c:110: cpct_setPalette(g_palette, 16);  // Set the palette using hardware values generated at rocket.h
	ld	hl, #0x0010
	push	hl
	ld	hl, #_g_palette
	push	hl
	call	_cpct_setPalette
;src/main.c:111: cpct_setBorder(HW_BLACK);        // Set border colour to Black 
	ld	hl, #0x1410
	push	hl
	call	_cpct_setPALColour
	ret
;src/main.c:117: void main(void) {
;	---------------------------------
; Function main
; ---------------------------------
_main::
	push	ix
	ld	ix,#0
	add	ix,sp
	push	af
;src/main.c:118: u8 x = INIT_X, y = INIT_Y;    // x, y coordinates
	ld	bc,#0x6414
;src/main.c:119: i8 vx = 1, vy = 0;            // vx, vy velocity (vx not 0 to force initial drawing)
	ld	-2 (ix), #0x01
	ld	-1 (ix), #0x00
;src/main.c:122: initialize();
	push	bc
	call	_initialize
	pop	bc
;src/main.c:125: while (1) {
00105$:
;src/main.c:129: cpct_waitVSYNC();
	push	bc
	call	_cpct_waitVSYNC
	pop	bc
;src/main.c:135: if (vx || vy) {
	ld	a, -2 (ix)
	or	a, a
	jr	NZ,00101$
	ld	a, -1 (ix)
	or	a, a
	jr	Z,00102$
00101$:
;src/main.c:136: clearRockets(x, y);  // Clear Rockets
	push	bc
	push	bc
	call	_clearRockets
	pop	af
	pop	bc
;src/main.c:137: x += vx; y += vy;    // Update x,y coordinates according to velocity
	ld	a, c
	add	a, -2 (ix)
	ld	c, a
	ld	a, b
	add	a, -1 (ix)
	ld	b, a
;src/main.c:138: drawRockets(x, y);   // Draw Rockets at their new location
	push	bc
	push	bc
	call	_drawRockets
	pop	af
	pop	bc
00102$:
;src/main.c:142: getUserInput(&vx, &vy);
	ld	hl, #0x0001
	add	hl, sp
	ex	de,hl
	ld	hl, #0x0000
	add	hl, sp
	push	bc
	push	de
	push	hl
	call	_getUserInput
	pop	af
	pop	af
	pop	bc
	jr	00105$
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
