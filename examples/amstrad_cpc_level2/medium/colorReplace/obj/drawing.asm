;--------------------------------------------------------
; File Created by SDCC : free open source ANSI-C Compiler
; Version 3.6.8 #9946 (Linux)
;--------------------------------------------------------
	.module drawing
	.optsdcc -mz80
	
;--------------------------------------------------------
; Public variables in this module
;--------------------------------------------------------
	.globl _DrawBackground
	.globl _DrawCloud
	.globl _DrawBalloon
	.globl _DeleteBalloons
	.globl _ClearBalloon
	.globl _ColorSprite
	.globl _GetRand
	.globl _GetBackBufferPtr
	.globl _cpct_getRandom_mxor_u8
	.globl _cpct_drawSpriteMasked
	.globl _cpct_drawSprite
	.globl _cpct_drawSolidBox
	.globl _cpct_pens2pixelPatternPairM0_real
	.globl _cpct_drawSpriteMaskedAlignedColorizeM0
	.globl _cpct_drawSpriteMaskedColorizeM0
	.globl _cpct_drawSpriteColorizeM0
	.globl _cpct_spriteMaskedColourizeM0
	.globl _cpct_spriteColourizeM0
	.globl _cpct_memcpy
	.globl _cpct_memset
	.globl _gStars
	.globl _gBalloons
	.globl _gPosCloud
	.globl _gBalloonColor
	.globl _gBackGroundColor
	.globl _gSpriteColorized
	.globl _UpdateBalloons
	.globl _DrawStars
	.globl _DrawSceneBalloons
	.globl _InitializeDrawing
;--------------------------------------------------------
; special function registers
;--------------------------------------------------------
;--------------------------------------------------------
; ram data
;--------------------------------------------------------
	.area _DATA
_gSpriteColorized::
	.ds 340
_gBackGroundColor::
	.ds 1
_gBalloonColor::
	.ds 1
_gPosCloud::
	.ds 1
_gBalloons::
	.ds 65
_gStars::
	.ds 30
_DrawStars_sColorAnim_1_154:
	.ds 1
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
;src/drawing.c:259: static u8 sColorAnim = 0;
	ld	iy, #_DrawStars_sColorAnim_1_154
	ld	0 (iy), #0x00
;--------------------------------------------------------
; Home
;--------------------------------------------------------
	.area _HOME
	.area _HOME
;--------------------------------------------------------
; code
;--------------------------------------------------------
	.area _CODE
;src/drawing.c:72: u8 GetRand(u8 max)
;	---------------------------------
; Function GetRand
; ---------------------------------
_GetRand::
;src/drawing.c:74: return cpct_rand()%max;
	call	_cpct_getRandom_mxor_u8
	ld	b, l
	ld	hl, #2+0
	add	hl, sp
	ld	a, (hl)
	push	af
	inc	sp
	push	bc
	inc	sp
	call	__moduchar
	pop	af
	ret
;src/drawing.c:80: u8* ColorSprite(u8 color)
;	---------------------------------
; Function ColorSprite
; ---------------------------------
_ColorSprite::
	push	ix
	ld	ix,#0
	add	ix,sp
;src/drawing.c:83: u16 replacePatColor1 = CPCTM_PENS2PIXELPATTERNPAIR_M0(1, color); // Just for example use cpct_pens2pixelPatternPairM0 with variables
	ld	a, 4 (ix)
	and	a, #0x01
	rrca
	rrca
	and	a, #0xc0
	ld	c, a
	ld	a, 4 (ix)
	and	a, #0x02
	add	a, a
	or	a, c
	ld	c, a
	ld	a, 4 (ix)
	and	a, #0x04
	add	a, a
	add	a, a
	or	a, c
	ld	c, a
	ld	a, 4 (ix)
	and	a, #0x08
	rrca
	rrca
	rrca
	and	a, #0x1f
	or	a, c
	ld	c,a
	add	a, a
	or	a, c
	ld	e, a
	ld	c, #0x00
	ld	a, c
	or	a, #0xc0
	ld	d, a
;src/drawing.c:84: u16 replacePatColor2 = cpct_pens2pixelPatternPairM0(2, color + 1);
	ld	b, 4 (ix)
	inc	b
	push	de
	ld	a, #0x02
	push	af
	inc	sp
	push	bc
	inc	sp
	call	_cpct_pens2pixelPatternPairM0_real
	ld	c, l
	ld	b, h
	pop	de
;src/drawing.c:87: cpct_memcpy(gSpriteColorized, g_balloon, G_BALLOON_W*G_BALLOON_H);
	push	bc
	push	de
	ld	hl, #0x0154
	push	hl
	ld	hl, #_g_balloon
	push	hl
	ld	hl, #_gSpriteColorized
	push	hl
	call	_cpct_memcpy
	pop	de
	ld	hl, #_gSpriteColorized
	push	hl
	ld	hl, #0x0154
	push	hl
	push	de
	call	_cpct_spriteColourizeM0
	pop	bc
;src/drawing.c:91: cpct_spriteColourizeM0(replacePatColor2, G_BALLOON_W*G_BALLOON_H, gSpriteColorized);
	ld	hl, #_gSpriteColorized
	push	hl
	ld	hl, #0x0154
	push	hl
	push	bc
	call	_cpct_spriteColourizeM0
;src/drawing.c:93: return gSpriteColorized;
	ld	hl, #_gSpriteColorized
	pop	ix
	ret
;src/drawing.c:99: void ClearBalloon(SBalloon* balloon)
;	---------------------------------
; Function ClearBalloon
; ---------------------------------
_ClearBalloon::
	push	ix
	ld	ix,#0
	add	ix,sp
	dec	sp
;src/drawing.c:102: if (balloon->drawPosY < VIEW_DOWN)
	ld	c,4 (ix)
	ld	b,5 (ix)
	ld	l, c
	ld	h, b
	inc	hl
	inc	hl
	inc	hl
	ld	e, (hl)
	ld	a, e
	sub	a, #0xb4
	jr	NC,00105$
;src/drawing.c:107: u8 clearCY = balloon->drawCY + BALLOON_TRAIL;
	push	bc
	pop	iy
	ld	a, 4 (iy)
	add	a, #0x08
	ld	-1 (ix), a
;src/drawing.c:110: u8 posDownClearY = balloon->drawPosY + clearCY;
	ld	a, e
	add	a, -1 (ix)
	ld	d, a
;src/drawing.c:111: if (posDownClearY > VIEW_DOWN)
;src/drawing.c:112: clearCY = VIEW_DOWN - balloon->drawPosY;
	ld	a,#0xb4
	cp	a,d
	jr	NC,00102$
	sub	a, e
	ld	-1 (ix), a
00102$:
;src/drawing.c:115: pvmem = GetBackBufferPtr(balloon->posX, balloon->drawPosY);
	ld	l, c
	ld	h, b
	inc	hl
	inc	hl
	ld	b, (hl)
	ld	a, e
	push	af
	inc	sp
	push	bc
	inc	sp
	call	_GetBackBufferPtr
	pop	af
	ld	c, l
	ld	b, h
;src/drawing.c:116: cpct_drawSolidBox(pvmem, gBackGroundColor, G_BALLOON_W, clearCY);    
	ld	hl,#_gBackGroundColor + 0
	ld	e, (hl)
	ld	d, #0x00
	ld	a, -1 (ix)
	push	af
	inc	sp
	ld	a, #0x0a
	push	af
	inc	sp
	push	de
	push	bc
	call	_cpct_drawSolidBox
00105$:
	inc	sp
	pop	ix
	ret
;src/drawing.c:123: void DeleteBalloons(SBalloon* balloons, SBalloon* balloonToDel, u8* nb)
;	---------------------------------
; Function DeleteBalloons
; ---------------------------------
_DeleteBalloons::
;src/drawing.c:127: const SBalloon* lastBalloon = &balloons[--*nb];
	ld	hl, #6
	add	hl, sp
	ld	c, (hl)
	inc	hl
	ld	b, (hl)
	ld	a, (bc)
	add	a, #0xff
	ld	(bc), a
	ld	l, a
	ld	h, #0x00
	add	hl, hl
	add	hl, hl
	add	hl, hl
	ld	c, l
	ld	b, h
	ld	hl, #2
	add	hl, sp
	ld	a, (hl)
	inc	hl
	ld	h, (hl)
	ld	l, a
	add	hl, bc
	ld	c, l
	ld	b, h
;src/drawing.c:130: if (balloonToDel != lastBalloon)
	ld	iy, #4
	add	iy, sp
	ld	a, 0 (iy)
	sub	a, c
	jr	NZ,00109$
	ld	a, 1 (iy)
	sub	a, b
	ret	Z
00109$:
;src/drawing.c:131: cpct_memcpy(balloonToDel, lastBalloon, sizeof(SBalloon));
	ld	e,0 (iy)
	ld	d,1 (iy)
	ld	hl, #0x0008
	push	hl
	push	bc
	push	de
	call	_cpct_memcpy
	ret
;src/drawing.c:137: void UpdateBalloons()
;	---------------------------------
; Function UpdateBalloons
; ---------------------------------
_UpdateBalloons::
	push	ix
	ld	ix,#0
	add	ix,sp
	push	af
	push	af
	dec	sp
;src/drawing.c:139: SBalloon* itBalloon = gBalloons.balloons;
;src/drawing.c:143: if (gBalloons.nb < NB_BALLOONS)
	ld	hl, #_gBalloons + 0
	ld	c, (hl)
	ld	a, c
	sub	a, #0x08
	jp	NC, 00127$
;src/drawing.c:147: SBalloon* newBalloon = &gBalloons.balloons[gBalloons.nb++];
	ld	b, c
	inc	b
	ld	hl, #_gBalloons
	ld	(hl), b
	ld	a, c
	rlca
	rlca
	rlca
	and	a, #0xf8
	ld	c, a
	ld	hl, #(_gBalloons + 0x0001)
	ld	b, #0x00
	add	hl, bc
	ld	c, l
	ld	b, h
;src/drawing.c:150: newBalloon->posX = GetRand(SCREEN_CX - G_BALLOON_W);
	ld	e, c
	ld	d, b
	inc	de
	inc	de
	push	bc
	push	de
	ld	a, #0x46
	push	af
	inc	sp
	call	_GetRand
	inc	sp
	ld	a, l
	pop	de
	pop	bc
	ld	(de), a
;src/drawing.c:151: newBalloon->posY = SCREEN_CY - GetRand(40);
	push	bc
	ld	a, #0x28
	push	af
	inc	sp
	call	_GetRand
	inc	sp
	pop	bc
	ld	h, #0x00
	ld	a, #0xc8
	sub	a, l
	ld	e, a
	ld	a, #0x00
	sbc	a, h
	ld	d, a
	ld	l, c
	ld	h, b
	ld	(hl), e
	inc	hl
	ld	(hl), d
;src/drawing.c:154: newBalloon->speed = GetRand(3) + 2;
	ld	hl, #0x0005
	add	hl, bc
	push	hl
	push	bc
	ld	a, #0x03
	push	af
	inc	sp
	call	_GetRand
	inc	sp
	ld	e, l
	pop	bc
	pop	hl
	inc	e
	inc	e
	ld	(hl), e
;src/drawing.c:157: gBalloonColor = (gBalloonColor + 2) % 12;
	ld	hl,#_gBalloonColor + 0
	ld	e, (hl)
	ld	d, #0x00
	inc	de
	inc	de
	push	bc
	ld	hl, #0x000c
	push	hl
	push	de
	call	__modsint
	pop	af
	pop	af
	pop	bc
	ld	iy, #_gBalloonColor
	ld	0 (iy), l
;src/drawing.c:158: newBalloon->color = gBalloonColor + 1;
	ld	hl, #0x0006
	add	hl,bc
	ex	de,hl
	ld	a, 0 (iy)
	inc	a
	ld	(de), a
;src/drawing.c:161: newBalloon->status = BALLOON_ACTIVE;
	ld	hl, #0x0007
	add	hl, bc
	ld	(hl), #0x01
;src/drawing.c:165: for (i = 0; i < gBalloons.nb; i++)
00127$:
	ld	bc, #(_gBalloons + 0x0001)
	ld	-5 (ix), #0x00
00117$:
	ld	hl, #_gBalloons + 0
	ld	a,-5 (ix)
	sub	a,(hl)
	jp	NC, 00119$
;src/drawing.c:168: if (itBalloon->status == BALLOON_ACTIVE)
	ld	hl, #0x0007
	add	hl,bc
	ld	-4 (ix), l
	ld	-3 (ix), h
	ld	e, (hl)
	dec	e
	jp	NZ,00113$
;src/drawing.c:171: if (itBalloon->posY + G_BALLOON_H < VIEW_TOP)
	ld	l, c
	ld	h, b
	ld	e, (hl)
	inc	hl
	ld	d, (hl)
	ld	hl, #0x0022
	add	hl, de
	bit	7, h
	jr	Z,00110$
;src/drawing.c:174: itBalloon->status = BALLOON_INACTIVE;
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	(hl), #0x00
;src/drawing.c:176: ClearBalloon(itBalloon);
	push	bc
	push	bc
	call	_ClearBalloon
	pop	af
	pop	bc
	jp	00114$
00110$:
;src/drawing.c:181: i16 posY = itBalloon->posY - itBalloon->speed;
	push	bc
	pop	iy
	ld	l, 5 (iy)
	ld	h, #0x00
	ld	a, e
	sub	a, l
	ld	e, a
	ld	a, d
	sbc	a, h
	ld	d, a
;src/drawing.c:182: itBalloon->posY = posY;
	ld	l, c
	ld	h, b
	ld	(hl), e
	inc	hl
	ld	(hl), d
;src/drawing.c:187: itBalloon->drawPosY = 0;
	ld	l, c
	ld	h, b
	inc	hl
	inc	hl
	inc	hl
;src/drawing.c:188: itBalloon->drawCY = G_BALLOON_H + posY;
	ld	iy, #0x0004
	add	iy, bc
	ld	-4 (ix), e
;src/drawing.c:185: if (posY < VIEW_TOP)
	bit	7, d
	jr	Z,00107$
;src/drawing.c:187: itBalloon->drawPosY = 0;
	ld	(hl), #0x00
;src/drawing.c:188: itBalloon->drawCY = G_BALLOON_H + posY;
	ld	a, -4 (ix)
	add	a, #0x22
	ld	0 (iy), a
	jr	00114$
00107$:
;src/drawing.c:192: if (posY + G_BALLOON_H > VIEW_DOWN)
	ld	a, e
	add	a, #0x22
	ld	-2 (ix), a
	ld	a, d
	adc	a, #0x00
	ld	-1 (ix), a
;src/drawing.c:194: itBalloon->drawPosY = posY;
;src/drawing.c:192: if (posY + G_BALLOON_H > VIEW_DOWN)
	ld	a, #0xb4
	cp	a, -2 (ix)
	ld	a, #0x00
	sbc	a, -1 (ix)
	jp	PO, 00152$
	xor	a, #0x80
00152$:
	jp	P, 00104$
;src/drawing.c:194: itBalloon->drawPosY = posY;
	ld	(hl), e
;src/drawing.c:195: itBalloon->drawCY = VIEW_DOWN - posY;
	ld	a, #0xb4
	sub	a, -4 (ix)
	ld	0 (iy), a
	jr	00114$
00104$:
;src/drawing.c:200: itBalloon->drawPosY = posY;
	ld	(hl), e
;src/drawing.c:201: itBalloon->drawCY = G_BALLOON_H;
	ld	0 (iy), #0x22
	jr	00114$
00113$:
;src/drawing.c:209: ClearBalloon(itBalloon);
	push	bc
	push	bc
	call	_ClearBalloon
	pop	af
	pop	bc
;src/drawing.c:212: DeleteBalloons(gBalloons.balloons, itBalloon, &gBalloons.nb);
	push	bc
	ld	hl, #_gBalloons
	push	hl
	push	bc
	ld	hl, #(_gBalloons + 0x0001)
	push	hl
	call	_DeleteBalloons
	ld	hl, #6
	add	hl, sp
	ld	sp, hl
	pop	bc
00114$:
;src/drawing.c:216: itBalloon++;
	ld	hl, #0x0008
	add	hl,bc
	ld	c, l
	ld	b, h
;src/drawing.c:165: for (i = 0; i < gBalloons.nb; i++)
	inc	-5 (ix)
	jp	00117$
00119$:
	ld	sp, ix
	pop	ix
	ret
;src/drawing.c:223: void DrawBalloon(SBalloon* balloon, u8* spriteBalloon)
;	---------------------------------
; Function DrawBalloon
; ---------------------------------
_DrawBalloon::
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	hl, #-6
	add	hl, sp
	ld	sp, hl
;src/drawing.c:225: i16 posY = balloon->posY;
	ld	c,4 (ix)
	ld	b,5 (ix)
	ld	a, (bc)
	ld	-2 (ix), a
	inc	bc
	ld	a, (bc)
	ld	-1 (ix), a
	dec	bc
;src/drawing.c:228: if (posY + G_BALLOON_H > VIEW_TOP && posY < VIEW_DOWN)
	ld	a, -2 (ix)
	add	a, #0x22
	ld	e, a
	ld	a, -1 (ix)
	adc	a, #0x00
	ld	d, a
	xor	a, a
	cp	a, e
	sbc	a, d
	jp	PO, 00120$
	xor	a, #0x80
00120$:
	jp	P, 00106$
	ld	a, -2 (ix)
	sub	a, #0xb4
	ld	a, -1 (ix)
	rla
	ccf
	rra
	sbc	a, #0x80
	jr	NC,00106$
;src/drawing.c:231: u8* pvmem = GetBackBufferPtr(balloon->posX, balloon->drawPosY);
	ld	l, c
	ld	h, b
	inc	hl
	inc	hl
	inc	hl
	ld	d, (hl)
	ld	l, c
	ld	h, b
	inc	hl
	inc	hl
	ld	a, (hl)
	push	bc
	ld	e, a
	push	de
	call	_GetBackBufferPtr
	pop	af
	pop	bc
	inc	sp
	inc	sp
	push	hl
;src/drawing.c:232: u8* sprite = (u8*)spriteBalloon;
	ld	e,6 (ix)
	ld	d,7 (ix)
;src/drawing.c:234: u16 replacePatColor1 = cpct_pens2pixelPatternPairM0(1, balloon->color);
	push	bc
	pop	iy
	ld	h, 6 (iy)
	push	bc
	push	de
	ld	a, #0x01
	push	af
	inc	sp
	push	hl
	inc	sp
	call	_cpct_pens2pixelPatternPairM0_real
	pop	de
	pop	bc
	ld	-4 (ix), l
	ld	-3 (ix), h
;src/drawing.c:237: if (posY < VIEW_TOP)
	bit	7, -1 (ix)
	jr	Z,00102$
;src/drawing.c:240: u8 y = -posY;
	ld	l, -2 (ix)
	xor	a, a
	sub	a, l
	ld	l, a
;src/drawing.c:243: sprite = (u8*)spriteBalloon + G_BALLOON_W * y;
	push	de
	ld	e,l
	ld	d,#0x00
	ld	l, e
	ld	h, d
	add	hl, hl
	add	hl, hl
	add	hl, de
	add	hl, hl
	pop	de
	add	hl,de
	ex	de,hl
00102$:
;src/drawing.c:246: cpct_drawSpriteMaskedAlignedColorizeM0(sprite, pvmem, G_BALLOON_W, balloon->drawCY, gMaskTable, replacePatColor1);
	push	bc
	pop	iy
	ld	b, 4 (iy)
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	push	hl
	ld	hl, #_gMaskTable
	push	hl
	push	bc
	inc	sp
	ld	a, #0x0a
	push	af
	inc	sp
	ld	l,-6 (ix)
	ld	h,-5 (ix)
	push	hl
	push	de
	call	_cpct_drawSpriteMaskedAlignedColorizeM0
00106$:
	ld	sp, ix
	pop	ix
	ret
;src/drawing.c:253: void DrawStars()
;	---------------------------------
; Function DrawStars
; ---------------------------------
_DrawStars::
	push	ix
	ld	ix,#0
	add	ix,sp
	push	af
;src/drawing.c:261: for (u8 i = 0; i < NB_STARS; i++)
	ld	c, #0x00
00109$:
;src/drawing.c:264: u8* pvmem = GetBackBufferPtr(SCREEN_CX / NB_STARS * i + 5, i + 175);
	ld	a,c
	cp	a,#0x0a
	jp	NC,00111$
	add	a, #0xaf
	ld	d, a
	ld	a, c
	rlca
	rlca
	rlca
	and	a, #0xf8
	add	a, #0x05
	ld	b, a
	push	bc
	ld	e, b
	push	de
	call	_GetBackBufferPtr
	pop	af
	pop	bc
	inc	sp
	inc	sp
	push	hl
;src/drawing.c:267: u8 colorPaletteStar = (i + sColorAnim++) % NB_COLORS_STAR;
	ld	e, c
	ld	d, #0x00
	ld	iy, #_DrawStars_sColorAnim_1_154
	ld	b, 0 (iy)
	inc	0 (iy)
	ld	h, #0x00
	ld	l, b
	add	hl, de
	push	bc
	ld	de, #0x0007
	push	de
	push	hl
	call	__modsint
	pop	af
	pop	af
	ld	e, l
	pop	bc
;src/drawing.c:270: u16 replacePatColor = cpct_pens2pixelPatternPairM0(15, sColorStar[colorPaletteStar]);
	ld	hl, #_DrawStars_sColorStar_1_154
	ld	d, #0x00
	add	hl, de
	ld	b, (hl)
	push	bc
	ld	a, #0x0f
	push	af
	inc	sp
	push	bc
	inc	sp
	call	_cpct_pens2pixelPatternPairM0_real
	ex	de,hl
	pop	bc
;src/drawing.c:272: if ((i%3) == 0)
	push	bc
	push	de
	ld	b, #0x03
	push	bc
	call	__moduchar
	pop	af
	pop	de
	pop	bc
	ld	a, l
	or	a, a
	jr	NZ,00105$
;src/drawing.c:275: cpct_memcpy(gSpriteColorized, g_circle_trans, G_CIRCLE_TRANS_W * G_CIRCLE_TRANS_H * 2);
	push	bc
	push	de
	ld	hl, #0x0018
	push	hl
	ld	hl, #_g_circle_trans
	push	hl
	ld	hl, #_gSpriteColorized
	push	hl
	call	_cpct_memcpy
	pop	de
	ld	hl, #_gSpriteColorized
	push	hl
	ld	hl, #0x000c
	push	hl
	push	de
	call	_cpct_spriteMaskedColourizeM0
	pop	bc
;src/drawing.c:281: cpct_drawSpriteMasked(gSpriteColorized, pvmem, G_CIRCLE_TRANS_W, G_CIRCLE_TRANS_H);
	pop	de
	push	de
	push	bc
	ld	hl, #0x0602
	push	hl
	push	de
	ld	hl, #_gSpriteColorized
	push	hl
	call	_cpct_drawSpriteMasked
	pop	bc
	jr	00110$
00105$:
;src/drawing.c:283: else if ((i%3) == 1)
	dec	l
	jr	NZ,00102$
;src/drawing.c:286: cpct_drawSpriteColorizeM0(g_square, pvmem, G_SQUARE_W, G_SQUARE_H, replacePatColor);
	push	bc
	push	de
	ld	hl, #0x0401
	push	hl
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	push	hl
	ld	hl, #_g_square
	push	hl
	call	_cpct_drawSpriteColorizeM0
	pop	bc
	jr	00110$
00102$:
;src/drawing.c:291: cpct_drawSpriteMaskedColorizeM0(g_star_trans, pvmem, G_STAR_TRANS_W, G_STAR_TRANS_H, replacePatColor);
	push	bc
	push	de
	ld	hl, #0x0602
	push	hl
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	push	hl
	ld	hl, #_g_star_trans
	push	hl
	call	_cpct_drawSpriteMaskedColorizeM0
	pop	bc
00110$:
;src/drawing.c:261: for (u8 i = 0; i < NB_STARS; i++)
	inc	c
	jp	00109$
00111$:
	ld	sp, ix
	pop	ix
	ret
_DrawStars_sColorStar_1_154:
	.db #0x02	; 2
	.db #0x04	; 4
	.db #0x07	; 7
	.db #0x08	; 8
	.db #0x0a	; 10
	.db #0x0b	; 11
	.db #0x0c	; 12
;src/drawing.c:299: void DrawCloud()
;	---------------------------------
; Function DrawCloud
; ---------------------------------
_DrawCloud::
;src/drawing.c:302: u8* pvmem = GetBackBufferPtr(0, POS_CLOUD_Y);
	ld	hl, #0x1400
	push	hl
	call	_GetBackBufferPtr
	pop	af
;src/drawing.c:303: cpct_drawSprite(g_cloud, pvmem, G_CLOUD_W, G_CLOUD_H);
	ld	bc, #_g_cloud+0
	ld	de, #0x361f
	push	de
	push	hl
	push	bc
	call	_cpct_drawSprite
	ret
;src/drawing.c:309: void DrawSceneBalloons()
;	---------------------------------
; Function DrawSceneBalloons
; ---------------------------------
_DrawSceneBalloons::
	push	ix
	ld	ix,#0
	add	ix,sp
	dec	sp
;src/drawing.c:312: SBalloon* itBalloon = gBalloons.balloons; // Get first balloon pointer
	ld	bc, #(_gBalloons + 0x0001)
;src/drawing.c:313: for (u8 i = 0; i < gBalloons.nb; i++)
	ld	e, #0x00
00107$:
	ld	hl, #_gBalloons + 0
	ld	d, (hl)
	ld	a, e
	sub	a, d
	jr	NC,00101$
;src/drawing.c:315: ClearBalloon(itBalloon);
	push	bc
	push	de
	push	bc
	call	_ClearBalloon
	pop	af
	pop	de
	pop	bc
;src/drawing.c:316: itBalloon++;
	ld	hl, #0x0008
	add	hl,bc
	ld	c, l
	ld	b, h
;src/drawing.c:313: for (u8 i = 0; i < gBalloons.nb; i++)
	inc	e
	jr	00107$
00101$:
;src/drawing.c:320: DrawCloud();
	call	_DrawCloud
;src/drawing.c:323: itBalloon = gBalloons.balloons; // Get first balloon pointer
	ld	bc, #(_gBalloons + 0x0001)
;src/drawing.c:324: for (u8 i = 0; i < gBalloons.nb; i++)
	ld	-1 (ix), #0x00
00110$:
	ld	hl, #_gBalloons + 0
	ld	e, (hl)
	ld	a, -1 (ix)
	sub	a, e
	jr	NC,00112$
;src/drawing.c:327: if (itBalloon->color > 1) // Color 0 and 1 are default color balloon
	push	bc
	pop	iy
	ld	d, 6 (iy)
	ld	a, #0x01
	sub	a, d
	jr	NC,00103$
;src/drawing.c:329: u8* sprite = ColorSprite(itBalloon->color); // Change colors of balloon
	push	bc
	push	de
	inc	sp
	call	_ColorSprite
	inc	sp
	pop	bc
;src/drawing.c:330: DrawBalloon(itBalloon, sprite);              // And draw colored balloon
	push	bc
	push	hl
	push	bc
	call	_DrawBalloon
	pop	af
	pop	af
	pop	bc
	jr	00104$
00103$:
;src/drawing.c:333: DrawBalloon(itBalloon, g_balloon);           // Draw default balloon sprite (blue)
	push	bc
	ld	hl, #_g_balloon
	push	hl
	push	bc
	call	_DrawBalloon
	pop	af
	pop	af
	pop	bc
00104$:
;src/drawing.c:335: itBalloon++; // Get next balloon
	ld	hl, #0x0008
	add	hl,bc
	ld	c, l
	ld	b, h
;src/drawing.c:324: for (u8 i = 0; i < gBalloons.nb; i++)
	inc	-1 (ix)
	jr	00110$
00112$:
	inc	sp
	pop	ix
	ret
;src/drawing.c:342: void DrawBackground()
;	---------------------------------
; Function DrawBackground
; ---------------------------------
_DrawBackground::
;src/drawing.c:347: cpct_memset((u8*)SCREEN_BUFF, gBackGroundColor, VMEM_SIZE);
	ld	hl, #0x4000
	push	hl
	ld	a, (_gBackGroundColor)
	push	af
	inc	sp
	ld	h, #0x80
	push	hl
	call	_cpct_memset
;src/drawing.c:350: pvmem = GetBackBufferPtr(0, SCREEN_CY - G_ROOF_H);
	ld	hl, #0xb400
	push	hl
	call	_GetBackBufferPtr
	pop	af
	ld	c, l
	ld	b, h
;src/drawing.c:351: cpct_drawSprite(g_roof, pvmem, G_ROOF_W, G_ROOF_H);
	ld	e, c
	ld	d, b
	push	bc
	ld	hl, #0x1428
	push	hl
	push	de
	ld	hl, #_g_roof
	push	hl
	call	_cpct_drawSprite
	pop	bc
;src/drawing.c:354: pvmem += G_ROOF_W;
	ld	hl, #0x0028
	add	hl, bc
;src/drawing.c:355: cpct_drawSprite(g_roof, pvmem, G_ROOF_W, G_ROOF_H);
	ld	bc, #0x1428
	push	bc
	push	hl
	ld	hl, #_g_roof
	push	hl
	call	_cpct_drawSprite
;src/drawing.c:358: cpct_memcpy(CPCT_VMEM_START, (u8*)SCREEN_BUFF, VMEM_SIZE);
	ld	hl, #0x4000
	push	hl
	ld	h, #0x80
	push	hl
	ld	h, #0xc0
	push	hl
	call	_cpct_memcpy
	ret
;src/drawing.c:366: void InitializeDrawing()
;	---------------------------------
; Function InitializeDrawing
; ---------------------------------
_InitializeDrawing::
;src/drawing.c:368: gBackGroundColor = cpctm_px2byteM0(14, 14);             // Get byte color of background for M0
	ld	hl,#_gBackGroundColor + 0
	ld	(hl), #0x3f
;src/drawing.c:369: gBalloons.nb = 0;                                       // No balloon to draw at start
	ld	hl, #_gBalloons
	ld	(hl), #0x00
;src/drawing.c:370: DrawBackground();                                       // Set background on both buffers
	jp  _DrawBackground
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
