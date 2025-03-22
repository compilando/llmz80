;--------------------------------------------------------
; File Created by SDCC : free open source ANSI-C Compiler
; Version 3.6.8 #9946 (Linux)
;--------------------------------------------------------
	.module frame
	.optsdcc -mz80
	
;--------------------------------------------------------
; Public variables in this module
;--------------------------------------------------------
	.globl _cpct_getScreenPtr
	.globl _cpct_drawSprite
	.globl _cpct_drawTileAligned4x8
	.globl _drawFrame
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
;src/sprites/frame.c:28: void drawFrame(u8* pscr, u8 x) {
;	---------------------------------
; Function drawFrame
; ---------------------------------
_drawFrame::
	push	ix
	ld	ix,#0
	add	ix,sp
	push	af
;src/sprites/frame.c:33: pvmem = cpct_getScreenPtr(pscr, x, 0);
	ld	a, 4 (ix)
	ld	-2 (ix), a
	ld	a, 5 (ix)
	ld	-1 (ix), a
	xor	a, a
	push	af
	inc	sp
	ld	a, 6 (ix)
	push	af
	inc	sp
	pop	bc
	pop	hl
	push	hl
	push	bc
	push	hl
	call	_cpct_getScreenPtr
;src/sprites/frame.c:34: cpct_drawTileAligned4x8(G_frameUpLeftCorner,  pvmem);       // Up-Left
	ld	e, l
	ld	d, h
	ld	bc, #_G_frameUpLeftCorner+0
	push	hl
	push	de
	push	bc
	call	_cpct_drawTileAligned4x8
	pop	hl
;src/sprites/frame.c:35: cpct_drawTileAligned4x8(G_frameUpRightCorner, pvmem + 54);  // Up-Right
	ld	bc, #0x0036
	add	hl, bc
	ld	bc, #_G_frameUpRightCorner+0
	push	hl
	push	bc
	call	_cpct_drawTileAligned4x8
;src/sprites/frame.c:38: for(i=8; i < 192; i += 8) {
	ld	b, #0x08
00104$:
;src/sprites/frame.c:39: pvmem = cpct_getScreenPtr(pscr, x, i);
	push	bc
	push	bc
	inc	sp
	ld	a, 6 (ix)
	push	af
	inc	sp
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	push	hl
	call	_cpct_getScreenPtr
	pop	bc
;src/sprites/frame.c:40: cpct_drawTileAligned4x8(G_frameLeft,  pvmem);      // Left border
	ld	e, l
	ld	d, h
	push	hl
	push	bc
	push	de
	ld	de, #_G_frameLeft
	push	de
	call	_cpct_drawTileAligned4x8
	pop	bc
	pop	hl
;src/sprites/frame.c:41: cpct_drawTileAligned4x8(G_frameRight, pvmem + 54); // Right border
	ld	de, #0x0036
	add	hl, de
	push	bc
	push	hl
	ld	hl, #_G_frameRight
	push	hl
	call	_cpct_drawTileAligned4x8
	pop	bc
;src/sprites/frame.c:38: for(i=8; i < 192; i += 8) {
	ld	a, b
	add	a, #0x08
	ld	b,a
	sub	a, #0xc0
	jr	C,00104$
;src/sprites/frame.c:45: pvmem = cpct_getScreenPtr(pscr, x, 0);
	xor	a, a
	push	af
	inc	sp
	ld	a, 6 (ix)
	push	af
	inc	sp
	pop	bc
	pop	hl
	push	hl
	push	bc
	push	hl
	call	_cpct_getScreenPtr
	ld	c, l
	ld	b, h
;src/sprites/frame.c:46: for(i=4; i < 28; i += 4) {
	ld	e, #0x04
00106$:
;src/sprites/frame.c:47: pvmem += 4;
	inc	bc
	inc	bc
	inc	bc
	inc	bc
;src/sprites/frame.c:48: cpct_drawTileAligned4x8(G_frameUp, pvmem);       // Left part 
	ld	l, c
	ld	h, b
	push	bc
	push	de
	push	hl
	ld	hl, #_G_frameUp
	push	hl
	call	_cpct_drawTileAligned4x8
	pop	de
	pop	bc
;src/sprites/frame.c:49: cpct_drawTileAligned4x8(G_frameUp, pvmem + 26);  // Right part
	ld	hl, #0x001a
	add	hl, bc
	push	bc
	push	de
	push	hl
	ld	hl, #_G_frameUp
	push	hl
	call	_cpct_drawTileAligned4x8
	pop	de
	pop	bc
;src/sprites/frame.c:46: for(i=4; i < 28; i += 4) {
	inc	e
	inc	e
	inc	e
	inc	e
	ld	a, e
	sub	a, #0x1c
	jr	C,00106$
;src/sprites/frame.c:51: cpct_drawSprite(G_frameUpCenter, pvmem + 2, 6, 8);  // Central tile
	inc	bc
	inc	bc
	ld	hl, #0x0806
	push	hl
	push	bc
	ld	hl, #_G_frameUpCenter
	push	hl
	call	_cpct_drawSprite
;src/sprites/frame.c:54: pvmem = cpct_getScreenPtr(pscr, x, 192);
	ld	a, #0xc0
	push	af
	inc	sp
	ld	a, 6 (ix)
	push	af
	inc	sp
	pop	bc
	pop	hl
	push	hl
	push	bc
	push	hl
	call	_cpct_getScreenPtr
	ld	c, l
	ld	b, h
;src/sprites/frame.c:55: for(i=4; i < 28; i += 4) {
	ld	e, #0x04
00108$:
;src/sprites/frame.c:56: pvmem += 4;
	inc	bc
	inc	bc
	inc	bc
	inc	bc
;src/sprites/frame.c:57: cpct_drawTileAligned4x8(G_frameDown, pvmem);       // Left part
	ld	l, c
	ld	h, b
	push	bc
	push	de
	push	hl
	ld	hl, #_G_frameDown
	push	hl
	call	_cpct_drawTileAligned4x8
	pop	de
	pop	bc
;src/sprites/frame.c:58: cpct_drawTileAligned4x8(G_frameDown, pvmem + 26);  // Right part
	ld	hl, #0x001a
	add	hl, bc
	push	bc
	push	de
	push	hl
	ld	hl, #_G_frameDown
	push	hl
	call	_cpct_drawTileAligned4x8
	pop	de
	pop	bc
;src/sprites/frame.c:55: for(i=4; i < 28; i += 4) {
	inc	e
	inc	e
	inc	e
	inc	e
	ld	a, e
	sub	a, #0x1c
	jr	C,00108$
;src/sprites/frame.c:60: cpct_drawSprite(G_frameDownCenter, pvmem + 2, 6, 8);  // Central tile
	inc	bc
	inc	bc
	ld	hl, #0x0806
	push	hl
	push	bc
	ld	hl, #_G_frameDownCenter
	push	hl
	call	_cpct_drawSprite
;src/sprites/frame.c:63: pvmem = cpct_getScreenPtr(pscr, x, 192);
	ld	a, #0xc0
	push	af
	inc	sp
	ld	a, 6 (ix)
	push	af
	inc	sp
	pop	bc
	pop	hl
	push	hl
	push	bc
	push	hl
	call	_cpct_getScreenPtr
;src/sprites/frame.c:64: cpct_drawTileAligned4x8(G_frameDownLeftCorner,  pvmem);        // Down-Left
	ld	e, l
	ld	d, h
	ld	bc, #_G_frameDownLeftCorner+0
	push	hl
	push	de
	push	bc
	call	_cpct_drawTileAligned4x8
	pop	hl
;src/sprites/frame.c:65: cpct_drawTileAligned4x8(G_frameDownRightCorner, pvmem + 54);   // Down-Right
	ld	bc, #0x0036
	add	hl, bc
	ld	bc, #_G_frameDownRightCorner+0
	push	hl
	push	bc
	call	_cpct_drawTileAligned4x8
	ld	sp, ix
	pop	ix
	ret
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
