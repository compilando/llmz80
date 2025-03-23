;--------------------------------------------------------
; File Created by SDCC : free open source ANSI-C Compiler
; Version 3.6.8 #9946 (Linux)
;--------------------------------------------------------
	.module drawing
	.optsdcc -mz80
	
;--------------------------------------------------------
; Public variables in this module
;--------------------------------------------------------
	.globl _DrawUsingSpriteBackBuffer
	.globl _DrawUsingHardwareBackBuffer
	.globl _DrawDirectlyToScreen
	.globl _DrawSpriteBackBufferToScreen
	.globl _FlipBuffers
	.globl _GetSpriteBackBufferPtr
	.globl _GetBackBufferPtr
	.globl _GetScreenPtr
	.globl _cpct_waitVSYNC
	.globl _cpct_drawSpriteMaskedAlignedTable
	.globl _cpct_drawSpriteMasked
	.globl _cpct_drawSprite
	.globl _cpct_drawToSpriteBufferMaskedAlignedTable
	.globl _cpct_drawToSpriteBufferMasked
	.globl _cpct_drawToSpriteBuffer
	.globl _gDrawFunc
	.globl _gDrawFunction
	.globl _gPosScroll
	.globl _gNbTileset
	.globl _InitializeDrawing
	.globl _SelectDrawFunction
	.globl _ScrollAndDrawSpace
;--------------------------------------------------------
; special function registers
;--------------------------------------------------------
;--------------------------------------------------------
; ram data
;--------------------------------------------------------
	.area _DATA
_gNbTileset::
	.ds 1
_gPosScroll::
	.ds 1
_gDrawFunction::
	.ds 1
_gDrawFunc::
	.ds 2
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
;src/drawing.c:35: void InitializeDrawing() {
;	---------------------------------
; Function InitializeDrawing
; ---------------------------------
_InitializeDrawing::
;src/drawing.c:36: gNbTileset = sizeof(g_tileset)/sizeof(u8*);
	ld	hl,#_gNbTileset + 0
	ld	(hl), #0x0f
;src/drawing.c:37: gPosScroll = 0;
	ld	hl,#_gPosScroll + 0
	ld	(hl), #0x00
;src/drawing.c:38: SelectDrawFunction(1);
	ld	a, #0x01
	push	af
	inc	sp
	call	_SelectDrawFunction
	inc	sp
	ret
;src/drawing.c:47: void DrawDirectlyToScreen() {
;	---------------------------------
; Function DrawDirectlyToScreen
; ---------------------------------
_DrawDirectlyToScreen::
	push	ix
	ld	ix,#0
	add	ix,sp
	dec	sp
;src/drawing.c:51: cpct_waitVSYNC();
	call	_cpct_waitVSYNC
;src/drawing.c:56: for(i = 0; i < VIEW_W_BYTES; i++) {
	ld	-1 (ix), #0x00
00102$:
;src/drawing.c:58: u8 tile = (gPosScroll + i) % gNbTileset; 
	ld	hl,#_gPosScroll + 0
	ld	c, (hl)
	ld	b, #0x00
	ld	l, -1 (ix)
	ld	h, #0x00
	add	hl,bc
	ld	c, l
	ld	b, h
	ld	hl,#_gNbTileset + 0
	ld	e, (hl)
	ld	d, #0x00
	push	de
	push	bc
	call	__modsint
	pop	af
	pop	af
;src/drawing.c:59: screenPtr = GetScreenPtr(VIEW_X + i, VIEW_Y);
	ld	a, -1 (ix)
	add	a, #0x0f
	ld	b, a
	push	hl
	xor	a, a
	push	af
	inc	sp
	push	bc
	inc	sp
	call	_GetScreenPtr
	pop	af
	ex	de,hl
	pop	hl
;src/drawing.c:62: cpct_drawSprite(g_tileset[tile], screenPtr, G_BACK_00_W, G_BACK_00_H);
	ld	h, #0x00
	add	hl, hl
	ld	bc, #_g_tileset
	add	hl, bc
	ld	c, (hl)
	inc	hl
	ld	b, (hl)
	ld	hl, #0x3c01
	push	hl
	push	de
	push	bc
	call	_cpct_drawSprite
;src/drawing.c:56: for(i = 0; i < VIEW_W_BYTES; i++) {
	inc	-1 (ix)
	ld	a, -1 (ix)
	sub	a, #0x32
	jr	C,00102$
;src/drawing.c:68: screenPtr = GetScreenPtr(VIEW_X + POS_TITLE_X, 0);
	ld	hl, #0x001e
	push	hl
	call	_GetScreenPtr
	pop	af
	ld	c, l
	ld	b, h
;src/drawing.c:69: cpct_drawSpriteMaskedAlignedTable(g_title, screenPtr, G_TITLE_W, G_TITLE_H, gMaskTable);
	ld	de, #_gMaskTable
	push	de
	ld	hl, #0x1014
	push	hl
	push	bc
	ld	hl, #_g_title
	push	hl
	call	_cpct_drawSpriteMaskedAlignedTable
;src/drawing.c:74: screenPtr = GetScreenPtr(VIEW_X + POS_SHIP_X, VIEW_Y + POS_SHIP_Y);
	ld	hl, #0x1e27
	push	hl
	call	_GetScreenPtr
	pop	af
;src/drawing.c:75: cpct_drawSpriteMasked(g_ship, screenPtr, G_SHIP_W, G_SHIP_H);
	ld	bc, #_g_ship+0
	ld	de, #0x0a05
	push	de
	push	hl
	push	bc
	call	_cpct_drawSpriteMasked
;src/drawing.c:83: const u8* fireSp = (gPosScroll % 2) ? g_fire_0 : g_fire_1;
	ld	hl,#_gPosScroll+0
	bit	0, (hl)
	jr	Z,00106$
	ld	bc, #_g_fire_0+0
	jr	00107$
00106$:
	ld	bc, #_g_fire_1+0
00107$:
;src/drawing.c:86: screenPtr = GetScreenPtr(x, y);
	push	bc
	ld	hl, #0x2026
	push	hl
	call	_GetScreenPtr
	pop	af
	pop	bc
;src/drawing.c:89: cpct_drawSpriteMaskedAlignedTable(fireSp, screenPtr, G_FIRE_0_W, G_FIRE_0_H, gMaskTable);
	ld	de, #_gMaskTable
	push	de
	ld	de, #0x0601
	push	de
	push	hl
	push	bc
	call	_cpct_drawSpriteMaskedAlignedTable
	inc	sp
	pop	ix
	ret
;src/drawing.c:100: void DrawUsingHardwareBackBuffer() {
;	---------------------------------
; Function DrawUsingHardwareBackBuffer
; ---------------------------------
_DrawUsingHardwareBackBuffer::
	push	ix
	ld	ix,#0
	add	ix,sp
	push	af
;src/drawing.c:107: for(i = 0; i < VIEW_W_BYTES; i++) {
	ld	-2 (ix), #0x00
00102$:
;src/drawing.c:109: u8 tile = (gPosScroll + i)%gNbTileset; 
	ld	hl,#_gPosScroll + 0
	ld	c, (hl)
	ld	b, #0x00
	ld	l, -2 (ix)
	ld	h, #0x00
	add	hl,bc
	ld	c, l
	ld	b, h
	ld	hl,#_gNbTileset + 0
	ld	e, (hl)
	ld	d, #0x00
	push	de
	push	bc
	call	__modsint
	pop	af
	pop	af
;src/drawing.c:110: backScreenPtr = GetBackBufferPtr(VIEW_X + i, VIEW_Y);
	ld	a, -2 (ix)
	add	a, #0x0f
	ld	b, a
	push	hl
	xor	a, a
	push	af
	inc	sp
	push	bc
	inc	sp
	call	_GetBackBufferPtr
	pop	af
	ex	de,hl
	pop	hl
;src/drawing.c:113: cpct_drawSprite(g_tileset[tile], backScreenPtr, G_BACK_00_W, G_BACK_00_H);     
	ld	h, #0x00
	add	hl, hl
	ld	bc, #_g_tileset
	add	hl, bc
	ld	c, (hl)
	inc	hl
	ld	b, (hl)
	ld	hl, #0x3c01
	push	hl
	push	de
	push	bc
	call	_cpct_drawSprite
;src/drawing.c:107: for(i = 0; i < VIEW_W_BYTES; i++) {
	inc	-2 (ix)
	ld	a, -2 (ix)
	sub	a, #0x32
	jr	C,00102$
;src/drawing.c:119: backScreenPtr = GetBackBufferPtr(VIEW_X + POS_TITLE_X, 0);
	ld	hl, #0x001e
	push	hl
	call	_GetBackBufferPtr
	pop	af
	ld	c, l
	ld	b, h
;src/drawing.c:120: cpct_drawSpriteMaskedAlignedTable(g_title, backScreenPtr, G_TITLE_W, G_TITLE_H, gMaskTable);
	ld	de, #_gMaskTable
	push	de
	ld	hl, #0x1014
	push	hl
	push	bc
	ld	hl, #_g_title
	push	hl
	call	_cpct_drawSpriteMaskedAlignedTable
;src/drawing.c:125: backScreenPtr = GetBackBufferPtr(VIEW_X + POS_SHIP_X, VIEW_Y + POS_SHIP_Y);
	ld	hl, #0x1e27
	push	hl
	call	_GetBackBufferPtr
	pop	af
;src/drawing.c:126: cpct_drawSpriteMasked(g_ship, backScreenPtr, G_SHIP_W, G_SHIP_H);
	ld	bc, #_g_ship+0
	ld	de, #0x0a05
	push	de
	push	hl
	push	bc
	call	_cpct_drawSpriteMasked
;src/drawing.c:133: const u8* fireSp = (gPosScroll % 2) == 0 ? g_fire_0 : g_fire_1;
	ld	hl,#_gPosScroll+0
	bit	0, (hl)
	jr	NZ,00106$
	ld	bc, #_g_fire_0+0
	jr	00107$
00106$:
	ld	bc, #_g_fire_1+0
00107$:
;src/drawing.c:136: backScreenPtr = GetBackBufferPtr(x, y);
	push	bc
	ld	hl, #0x2026
	push	hl
	call	_GetBackBufferPtr
	pop	af
	pop	bc
;src/drawing.c:138: cpct_drawSpriteMaskedAlignedTable(fireSp, backScreenPtr, G_FIRE_0_W, G_FIRE_0_H, gMaskTable);
	ld	de, #_gMaskTable
	push	de
	ld	de, #0x0601
	push	de
	push	hl
	push	bc
	call	_cpct_drawSpriteMaskedAlignedTable
;src/drawing.c:143: FlipBuffers();
	call	_FlipBuffers
	ld	sp, ix
	pop	ix
	ret
;src/drawing.c:157: void DrawUsingSpriteBackBuffer() {
;	---------------------------------
; Function DrawUsingSpriteBackBuffer
; ---------------------------------
_DrawUsingSpriteBackBuffer::
	push	ix
	dec	sp
;src/drawing.c:164: for(i = 0; i < VIEW_W_BYTES; i++) {
	ld	b, #0x00
00102$:
;src/drawing.c:166: u8 tile = (gPosScroll + i)%gNbTileset;
	ld	hl,#_gPosScroll + 0
	ld	e, (hl)
	ld	d, #0x00
	ld	l, b
	ld	h, #0x00
	add	hl,de
	ex	de,hl
	ld	iy, #_gNbTileset
	ld	l, 0 (iy)
	ld	h, #0x00
	push	bc
	push	hl
	push	de
	call	__modsint
	pop	af
	pop	af
	pop	bc
	ld	c, l
;src/drawing.c:167: backBufferPtr = GetSpriteBackBufferPtr(i, 0);
	push	bc
	xor	a, a
	push	af
	inc	sp
	push	bc
	inc	sp
	call	_GetSpriteBackBufferPtr
	pop	af
	ex	de,hl
	pop	bc
;src/drawing.c:170: cpct_drawToSpriteBuffer(VIEW_W_BYTES, backBufferPtr, G_BACK_00_W, G_BACK_00_H, g_tileset[tile]);
	ld	l, c
	ld	h, #0x00
	add	hl, hl
	ld	a, #<(_g_tileset)
	add	a, l
	ld	l, a
	ld	a, #>(_g_tileset)
	adc	a, h
	ld	h, a
	ld	a, (hl)
	inc	hl
	ld	h, (hl)
	ld	l, a
	push	bc
	push	hl
	ld	hl, #0x3c01
	push	hl
	push	de
	ld	hl, #0x0032
	push	hl
	call	_cpct_drawToSpriteBuffer
	pop	bc
;src/drawing.c:164: for(i = 0; i < VIEW_W_BYTES; i++) {
	inc	b
	ld	a, b
	sub	a, #0x32
	jr	C,00102$
;src/drawing.c:176: backBufferPtr = GetSpriteBackBufferPtr(POS_TITLE_X, 0);
	ld	hl, #0x000f
	push	hl
	call	_GetSpriteBackBufferPtr
	pop	af
	ld	c, l
	ld	b, h
;src/drawing.c:177: cpct_drawToSpriteBufferMaskedAlignedTable(VIEW_W_BYTES, backBufferPtr, G_TITLE_W, G_TITLE_H, g_title, gMaskTable);
	ld	hl, #_gMaskTable
	ld	de, #_g_title+0
	push	hl
	push	de
	ld	hl, #0x1014
	push	hl
	push	bc
	ld	hl, #0x0032
	push	hl
	call	_cpct_drawToSpriteBufferMaskedAlignedTable
;src/drawing.c:182: backBufferPtr = GetSpriteBackBufferPtr(POS_SHIP_X, POS_SHIP_Y);
	ld	hl, #0x1e18
	push	hl
	call	_GetSpriteBackBufferPtr
	pop	af
;src/drawing.c:183: cpct_drawToSpriteBufferMasked(VIEW_W_BYTES, backBufferPtr, G_SHIP_W, G_SHIP_H, g_ship);
	ld	bc, #_g_ship+0
	push	bc
	ld	bc, #0x0a05
	push	bc
	push	hl
	ld	hl, #0x0032
	push	hl
	call	_cpct_drawToSpriteBufferMasked
;src/drawing.c:190: const u8* fireSp = (gPosScroll % 2) == 0 ? g_fire_0 : g_fire_1;
	ld	hl,#_gPosScroll+0
	bit	0, (hl)
	jr	NZ,00106$
	ld	bc, #_g_fire_0+0
	jr	00107$
00106$:
	ld	bc, #_g_fire_1+0
00107$:
;src/drawing.c:193: backBufferPtr = GetSpriteBackBufferPtr(x, y);
	push	bc
	ld	hl, #0x2017
	push	hl
	call	_GetSpriteBackBufferPtr
	pop	af
	pop	bc
;src/drawing.c:195: cpct_drawToSpriteBufferMaskedAlignedTable(VIEW_W_BYTES, backBufferPtr, G_FIRE_0_W, G_FIRE_0_H, fireSp, gMaskTable);
	ld	de, #_gMaskTable
	push	de
	push	bc
	ld	bc, #0x0601
	push	bc
	push	hl
	ld	hl, #0x0032
	push	hl
	call	_cpct_drawToSpriteBufferMaskedAlignedTable
;src/drawing.c:199: DrawSpriteBackBufferToScreen();
	call	_DrawSpriteBackBufferToScreen
	inc	sp
	pop	ix
	ret
;src/drawing.c:207: void SelectDrawFunction(u8 drawFuncNb) {
;	---------------------------------
; Function SelectDrawFunction
; ---------------------------------
_SelectDrawFunction::
;src/drawing.c:209: switch(drawFuncNb) {
	ld	iy, #2
	add	iy, sp
	ld	a, 0 (iy)
	dec	a
	jr	Z,00101$
	ld	a, 0 (iy)
	sub	a, #0x02
	jr	Z,00102$
	jr	00103$
;src/drawing.c:210: case 1:  gDrawFunc = DrawDirectlyToScreen;         break;
00101$:
	ld	iy, #_gDrawFunc
	ld	0 (iy), #<(_DrawDirectlyToScreen)
	ld	1 (iy), #>(_DrawDirectlyToScreen)
	ret
;src/drawing.c:211: case 2:  gDrawFunc = DrawUsingHardwareBackBuffer;  break;
00102$:
	ld	iy, #_gDrawFunc
	ld	0 (iy), #<(_DrawUsingHardwareBackBuffer)
	ld	1 (iy), #>(_DrawUsingHardwareBackBuffer)
	ret
;src/drawing.c:212: default: gDrawFunc = DrawUsingSpriteBackBuffer;
00103$:
	ld	iy, #_gDrawFunc
	ld	0 (iy), #<(_DrawUsingSpriteBackBuffer)
	ld	1 (iy), #>(_DrawUsingSpriteBackBuffer)
;src/drawing.c:213: }
	ret
;src/drawing.c:223: void ScrollAndDrawSpace() { 
;	---------------------------------
; Function ScrollAndDrawSpace
; ---------------------------------
_ScrollAndDrawSpace::
;src/drawing.c:225: gPosScroll++;
	ld	hl, #_gPosScroll+0
	inc	(hl)
;src/drawing.c:226: gDrawFunc(); 
	ld	hl, (_gDrawFunc)
	jp  ___sdcc_call_hl
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
