;--------------------------------------------------------
; File Created by SDCC : free open source ANSI-C Compiler
; Version 3.6.8 #9946 (Linux)
;--------------------------------------------------------
	.module draw
	.optsdcc -mz80
	
;--------------------------------------------------------
; Public variables in this module
;--------------------------------------------------------
	.globl _drawSpriteMixed
	.globl _cpct_getRandom_mxor_u8
	.globl _cpct_getScreenPtr
	.globl _cpct_drawStringM0
	.globl _cpct_setDrawCharM0
	.globl _cpct_drawSprite
	.globl _cpct_setBlendMode
	.globl _cpct_drawSpriteBlended
	.globl _drawBackground
	.globl _drawCurrentSpriteAtRandom
	.globl _drawUserInterfaceStatus
	.globl _drawUserInterfaceMessages
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
;src/draw.c:28: void drawBackground() {
;	---------------------------------
; Function drawBackground
; ---------------------------------
_drawBackground::
;src/draw.c:31: u8* p = cpct_getScreenPtr(CPCT_VMEM_START, BG_X, BG_Y);
	ld	hl, #0x4800
	push	hl
	ld	h, #0xc0
	push	hl
	call	_cpct_getScreenPtr
	ld	c, l
	ld	b, h
;src/draw.c:37: cpct_drawSprite(g_scifi_bg_0, p             , BG_WIDTH/2, BG_HEIGHT);
	ld	e, c
	ld	d, b
	push	bc
	ld	hl, #0x8028
	push	hl
	push	de
	ld	hl, #_g_scifi_bg_0
	push	hl
	call	_cpct_drawSprite
	pop	bc
;src/draw.c:38: cpct_drawSprite(g_scifi_bg_1, p + BG_WIDTH/2, BG_WIDTH/2, BG_HEIGHT);
	ld	hl, #0x0028
	add	hl, bc
	ld	bc, #_g_scifi_bg_1+0
	ld	de, #0x8028
	push	de
	push	hl
	push	bc
	call	_cpct_drawSprite
	ret
;src/draw.c:46: void drawSpriteMixed(  CPCT_BlendMode mode, u8* sprite
;	---------------------------------
; Function drawSpriteMixed
; ---------------------------------
_drawSpriteMixed::
	push	ix
	ld	ix,#0
	add	ix,sp
;src/draw.c:50: u8* p = cpct_getScreenPtr(CPCT_VMEM_START, x, y);
	ld	h, 8 (ix)
	ld	l, 7 (ix)
	push	hl
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
;src/draw.c:53: cpct_setBlendMode(mode);
	push	hl
	ld	l, 4 (ix)
	call	_cpct_setBlendMode
	pop	bc
;src/draw.c:56: cpct_drawSpriteBlended(p, height, width, sprite);
	ld	e,5 (ix)
	ld	d,6 (ix)
	push	de
	ld	h, 9 (ix)
	ld	l, 10 (ix)
	push	hl
	push	bc
	call	_cpct_drawSpriteBlended
	pop	ix
	ret
;src/draw.c:64: void drawCurrentSpriteAtRandom() {
;	---------------------------------
; Function drawCurrentSpriteAtRandom
; ---------------------------------
_drawCurrentSpriteAtRandom::
	push	ix
	ld	ix,#0
	add	ix,sp
	dec	sp
;src/draw.c:70: x = BG_X + ( cpct_rand() % (BG_WIDTH  - 4) );
	call	_cpct_getRandom_mxor_u8
	ld	b, l
	ld	a, #0x4c
	push	af
	inc	sp
	push	bc
	inc	sp
	call	__moduchar
	pop	af
	ld	-1 (ix), l
;src/draw.c:71: y = BG_Y + ( cpct_rand() % (BG_HEIGHT - 8) );
	call	_cpct_getRandom_mxor_u8
	ld	b, l
	ld	a, #0x78
	push	af
	inc	sp
	push	bc
	inc	sp
	call	__moduchar
	pop	af
	ld	a, l
	add	a, #0x48
	ld	b, a
;src/draw.c:75: , g_items[g_selectedItem].sprite
	ld	de, (_g_selectedItem)
	ld	d, #0x00
	ld	l, e
	ld	h, d
	add	hl, hl
	add	hl, hl
	add	hl, hl
	add	hl, de
	ld	de, #_g_items
	add	hl, de
	ld	e, (hl)
	inc	hl
	ld	d, (hl)
;src/draw.c:74: drawSpriteMixed(  g_blendModes[g_selectedBlendMode].blendmode
	push	de
	ld	de, (_g_selectedBlendMode)
	ld	d, #0x00
	ld	l, e
	ld	h, d
	add	hl, hl
	add	hl, hl
	add	hl, de
	pop	de
	ld	a, #<(_g_blendModes)
	add	a, l
	ld	l, a
	ld	a, #>(_g_blendModes)
	adc	a, h
	ld	h, a
	ld	c, (hl)
	ld	hl, #0x0804
	push	hl
	push	bc
	inc	sp
	ld	a, -1 (ix)
	push	af
	inc	sp
	push	de
	ld	a, c
	push	af
	inc	sp
	call	_drawSpriteMixed
	ld	hl, #7
	add	hl, sp
	ld	sp, hl
	inc	sp
	pop	ix
	ret
;src/draw.c:84: void drawUserInterfaceStatus() {
;	---------------------------------
; Function drawUserInterfaceStatus
; ---------------------------------
_drawUserInterfaceStatus::
;src/draw.c:87: u8 *p = cpct_getScreenPtr(CPCT_VMEM_START, 4, 60);
	ld	hl, #0x3c04
	push	hl
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
;src/draw.c:90: cpct_setDrawCharM0(8, 0);
	push	hl
	ld	hl, #0x0008
	push	hl
	call	_cpct_setDrawCharM0
	pop	bc
;src/draw.c:94: cpct_drawStringM0(g_items[g_selectedItem].name   , p       );
	ld	e, c
	ld	d, b
	push	de
	ld	de, (_g_selectedItem)
	ld	d, #0x00
	ld	l, e
	ld	h, d
	add	hl, hl
	add	hl, hl
	add	hl, hl
	add	hl, de
	pop	de
	ld	a, #<(_g_items)
	add	a, l
	ld	l, a
	ld	a, #>(_g_items)
	adc	a, h
	ld	h, a
	inc	hl
	inc	hl
	push	bc
	push	de
	push	hl
	call	_cpct_drawStringM0
	pop	bc
;src/draw.c:95: cpct_drawSprite  (g_items[g_selectedItem].sprite , p + 28 , 4, 8);
	ld	hl, #0x001c
	add	hl,bc
	ex	de,hl
	ld	bc, (_g_selectedItem)
	ld	b, #0x00
	ld	l, c
	ld	h, b
	add	hl, hl
	add	hl, hl
	add	hl, hl
	add	hl, bc
	ld	bc, #_g_items
	add	hl, bc
	ld	c, (hl)
	inc	hl
	ld	b, (hl)
	ld	hl, #0x0804
	push	hl
	push	de
	push	bc
	call	_cpct_drawSprite
;src/draw.c:98: p = cpct_getScreenPtr(CPCT_VMEM_START, 52, 60);
	ld	hl, #0x3c34
	push	hl
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
	ld	c, l
	ld	b, h
;src/draw.c:99: cpct_drawStringM0(g_blendModes[g_selectedBlendMode].name, p);
	ld	de, (_g_selectedBlendMode)
	ld	d, #0x00
	ld	l, e
	ld	h, d
	add	hl, hl
	add	hl, hl
	add	hl, de
	ld	de, #_g_blendModes
	add	hl, de
	inc	hl
	push	bc
	push	hl
	call	_cpct_drawStringM0
	ret
;src/draw.c:106: void drawUserInterfaceMessages() {
;	---------------------------------
; Function drawUserInterfaceMessages
; ---------------------------------
_drawUserInterfaceMessages::
;src/draw.c:111: cpct_setDrawCharM0(3, 0);
	ld	hl, #0x0003
	push	hl
	call	_cpct_setDrawCharM0
;src/draw.c:112: cpct_drawStringM0("[Space]"   , CPCT_VMEM_START    );
	ld	hl, #0xc000
	push	hl
	ld	hl, #___str_0
	push	hl
	call	_cpct_drawStringM0
;src/draw.c:113: cpct_setDrawCharM0(9, 0);
	ld	hl, #0x0009
	push	hl
	call	_cpct_setDrawCharM0
;src/draw.c:114: cpct_drawStringM0("Draw Item" , CPCT_VMEM_START+32 );
	ld	hl, #0xc020
	push	hl
	ld	hl, #___str_1
	push	hl
	call	_cpct_drawStringM0
;src/draw.c:118: p = cpct_getScreenPtr(CPCT_VMEM_START, 0, 15);
	ld	hl, #0x0f00
	push	hl
	ld	h, #0xc0
	push	hl
	call	_cpct_getScreenPtr
;src/draw.c:119: cpct_setDrawCharM0(3, 0);
	push	hl
	ld	bc, #0x0003
	push	bc
	call	_cpct_setDrawCharM0
	pop	hl
;src/draw.c:120: cpct_drawStringM0("[1] [2]"   , p    );
	ld	e, l
	ld	d, h
	ld	bc, #___str_2+0
	push	hl
	push	de
	push	bc
	call	_cpct_drawStringM0
	ld	bc, #0x0009
	push	bc
	call	_cpct_setDrawCharM0
	pop	hl
;src/draw.c:122: cpct_drawStringM0("Select"    , p+32 );
	ld	bc, #0x0020
	add	hl, bc
	ld	bc, #___str_3+0
	push	hl
	push	bc
	call	_cpct_drawStringM0
;src/draw.c:125: p = cpct_getScreenPtr(CPCT_VMEM_START, 0, 30);
	ld	hl, #0x1e00
	push	hl
	ld	h, #0xc0
	push	hl
	call	_cpct_getScreenPtr
;src/draw.c:126: cpct_setDrawCharM0(3, 0);
	push	hl
	ld	bc, #0x0003
	push	bc
	call	_cpct_setDrawCharM0
	pop	hl
;src/draw.c:127: cpct_drawStringM0("[Esc]"     , p    );
	ld	e, l
	ld	d, h
	ld	bc, #___str_4+0
	push	hl
	push	de
	push	bc
	call	_cpct_drawStringM0
	ld	bc, #0x0009
	push	bc
	call	_cpct_setDrawCharM0
	pop	hl
;src/draw.c:129: cpct_drawStringM0("Clear"     , p+32 );
	ld	bc, #0x0020
	add	hl, bc
	ld	bc, #___str_5+0
	push	hl
	push	bc
	call	_cpct_drawStringM0
;src/draw.c:133: p = cpct_getScreenPtr(CPCT_VMEM_START, 0, 50);
	ld	hl, #0x3200
	push	hl
	ld	h, #0xc0
	push	hl
	call	_cpct_getScreenPtr
;src/draw.c:134: cpct_setDrawCharM0(1, 6);
	push	hl
	ld	bc, #0x0601
	push	bc
	call	_cpct_setDrawCharM0
	pop	hl
;src/draw.c:135: cpct_drawStringM0("   Item     Blend   ", p);
	ld	bc, #___str_6+0
	push	hl
	push	bc
	call	_cpct_drawStringM0
	ret
___str_0:
	.ascii "[Space]"
	.db 0x00
___str_1:
	.ascii "Draw Item"
	.db 0x00
___str_2:
	.ascii "[1] [2]"
	.db 0x00
___str_3:
	.ascii "Select"
	.db 0x00
___str_4:
	.ascii "[Esc]"
	.db 0x00
___str_5:
	.ascii "Clear"
	.db 0x00
___str_6:
	.ascii "   Item     Blend   "
	.db 0x00
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
