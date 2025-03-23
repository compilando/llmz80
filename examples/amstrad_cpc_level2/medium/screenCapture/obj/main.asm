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
	.globl _DrawBackground
	.globl _InitCapture
	.globl _DrawCity
	.globl _DrawSky
	.globl _DrawSkyGradient
	.globl _FillLine
	.globl _DrawUFO
	.globl _GetUfoSprite
	.globl _Initialization
	.globl _cpct_getScreenPtr
	.globl _cpct_setPALColour
	.globl _cpct_setPalette
	.globl _cpct_waitVSYNC
	.globl _cpct_setVideoMode
	.globl _cpct_drawSpriteMasked
	.globl _cpct_drawSprite
	.globl _cpct_px2byteM0
	.globl _cpct_getScreenToSprite
	.globl _cpct_memset
	.globl _cpct_disableFirmware
	.globl _gScreenCapture
;--------------------------------------------------------
; special function registers
;--------------------------------------------------------
;--------------------------------------------------------
; ram data
;--------------------------------------------------------
	.area _DATA
_gScreenCapture::
	.ds 336
_GetUfoSprite_anim_1_129:
	.ds 1
_DrawUFO_moveRight_1_130:
	.ds 1
_DrawUFO_posX_1_130:
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
;src/main.c:72: static u8 anim = 0;     // Currently selected animation sprite
	ld	iy, #_GetUfoSprite_anim_1_129
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
;src/main.c:57: void Initialization() {
;	---------------------------------
; Function Initialization
; ---------------------------------
_Initialization::
;src/main.c:58: cpct_disableFirmware();            // Disable firmware to take full control of the CPC
	call	_cpct_disableFirmware
;src/main.c:59: cpct_setVideoMode(0);              // Set mode 0
	ld	l, #0x00
	call	_cpct_setVideoMode
;src/main.c:60: cpct_setPalette (g_palette, 16);   // Set the palette
	ld	hl, #0x0010
	push	hl
	ld	hl, #_g_palette
	push	hl
	call	_cpct_setPalette
;src/main.c:61: cpct_setBorder(HW_BLACK);          // Set the border color with Hardware color
	ld	hl, #0x1410
	push	hl
	call	_cpct_setPALColour
;src/main.c:64: cpct_memset(CPCT_VMEM_START, cpct_px2byteM0(4, 4), VMEM_SIZE);
	ld	hl, #0x0404
	push	hl
	call	_cpct_px2byteM0
	ld	b, l
	ld	hl, #0x4000
	push	hl
	push	bc
	inc	sp
	ld	h, #0xc0
	push	hl
	call	_cpct_memset
	ret
;src/main.c:70: u8* GetUfoSprite() {
;	---------------------------------
; Function GetUfoSprite
; ---------------------------------
_GetUfoSprite::
;src/main.c:78: return ufoSprite[anim++ % 4];
	ld	bc, #_GetUfoSprite_ufoSprite_1_129+0
	ld	iy, #_GetUfoSprite_anim_1_129
	ld	e, 0 (iy)
	inc	0 (iy)
	ld	a, e
	and	a, #0x03
	ld	l, a
	ld	h, #0x00
	add	hl, hl
	add	hl, bc
	ld	c, (hl)
	inc	hl
	ld	h, (hl)
	ld	l, c
	ret
_GetUfoSprite_ufoSprite_1_129:
	.dw _g_ufo_0
	.dw _g_ufo_1
	.dw _g_ufo_2
	.dw _g_ufo_3
;src/main.c:84: void DrawUFO() {
;	---------------------------------
; Function DrawUFO
; ---------------------------------
_DrawUFO::
;src/main.c:92: u8* pvmem_ufoBg = cpct_getScreenPtr(CPCT_VMEM_START, posX, UFO_Y);
	ld	a, #0x78
	push	af
	inc	sp
	ld	a, (_DrawUFO_posX_1_130)
	push	af
	inc	sp
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
	ex	de,hl
;src/main.c:99: if (moveRight) {
	ld	a,(#_DrawUFO_moveRight_1_130 + 0)
	or	a, a
	jr	Z,00108$
;src/main.c:101: if (posX == SCREEN_CX - G_UFO_0_W)
	ld	a,(#_DrawUFO_posX_1_130 + 0)
	sub	a, #0x40
	jr	NZ,00102$
;src/main.c:102: moveRight = FALSE;   // Change direction
	ld	hl,#_DrawUFO_moveRight_1_130 + 0
	ld	(hl), #0x00
	jr	00109$
00102$:
;src/main.c:104: posX++;              // Move to right
	ld	hl, #_DrawUFO_posX_1_130+0
	inc	(hl)
	jr	00109$
00108$:
;src/main.c:107: if (posX == 0)  moveRight = TRUE;   // Change direction
	ld	a,(#_DrawUFO_posX_1_130 + 0)
	or	a, a
	jr	NZ,00105$
	ld	hl,#_DrawUFO_moveRight_1_130 + 0
	ld	(hl), #0x01
	jr	00109$
00105$:
;src/main.c:108: else            posX--;             // Move to left
	ld	hl, #_DrawUFO_posX_1_130+0
	dec	(hl)
00109$:
;src/main.c:113: pvmem = cpct_getScreenPtr(CPCT_VMEM_START, posX, UFO_Y);
	push	de
	ld	a, #0x78
	push	af
	inc	sp
	ld	a, (_DrawUFO_posX_1_130)
	push	af
	inc	sp
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
	ld	c, l
	ld	b, h
	pop	de
;src/main.c:118: cpct_waitVSYNC();
	push	bc
	push	de
	call	_cpct_waitVSYNC
	pop	de
	ld	hl, #0x1510
	push	hl
	push	de
	ld	hl, #_gScreenCapture
	push	hl
	call	_cpct_drawSprite
	pop	bc
;src/main.c:128: cpct_getScreenToSprite(pvmem, gScreenCapture, G_UFO_0_W, G_UFO_0_H);
	push	bc
	ld	hl, #0x1510
	push	hl
	ld	hl, #_gScreenCapture
	push	hl
	push	bc
	call	_cpct_getScreenToSprite
	call	_GetUfoSprite
	pop	bc
	ld	de, #0x1510
	push	de
	push	bc
	push	hl
	call	_cpct_drawSpriteMasked
	ret
;src/main.c:137: void FillLine(u8 pixColor, u8 lineY) {
;	---------------------------------
; Function FillLine
; ---------------------------------
_FillLine::
;src/main.c:140: u8* pvmem = cpct_getScreenPtr(CPCT_VMEM_START, 0, lineY);
	ld	hl, #3+0
	add	hl, sp
	ld	a, (hl)
	push	af
	inc	sp
	xor	a, a
	push	af
	inc	sp
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
	ld	c, l
	ld	b, h
;src/main.c:141: cpct_memset(pvmem, pixColor, SCREEN_CX);
	ld	hl, #0x0050
	push	hl
	ld	hl, #4+0
	add	hl, sp
	ld	a, (hl)
	push	af
	inc	sp
	push	bc
	call	_cpct_memset
	ret
;src/main.c:147: u8 DrawSkyGradient(u8 cy, u8 posY, u8 colorFront, u8 colorBack) {
;	---------------------------------
; Function DrawSkyGradient
; ---------------------------------
_DrawSkyGradient::
	push	ix
	ld	ix,#0
	add	ix,sp
	push	af
	push	af
;src/main.c:151: u8 pixFront = cpct_px2byteM0(colorFront, colorFront);
	ld	h, 6 (ix)
	ld	l, 6 (ix)
	push	hl
	call	_cpct_px2byteM0
	ld	-4 (ix), l
;src/main.c:152: u8 pixBack  = cpct_px2byteM0(colorBack, colorBack);
	ld	h, 7 (ix)
	ld	l, 7 (ix)
	push	hl
	call	_cpct_px2byteM0
	ld	b, l
;src/main.c:155: for (j = 0; j < cy; j++) {
	ld	c, #0x00
00109$:
	ld	a, c
	sub	a, 4 (ix)
	jr	NC,00104$
;src/main.c:157: if (posY == SCREEN_CY - 2)
	ld	a, 5 (ix)
	sub	a, #0xc6
	jr	Z,00104$
;src/main.c:161: for (i = 0; i < cy - j; i++) {
	ld	d, 5 (ix)
	ld	-3 (ix), #0x00
00106$:
	ld	l, 4 (ix)
	ld	h, #0x00
	ld	-2 (ix), c
	ld	-1 (ix), #0x00
	ld	a, l
	sub	a, -2 (ix)
	ld	-2 (ix), a
	ld	a, h
	sbc	a, -1 (ix)
	ld	-1 (ix), a
	ld	l, -3 (ix)
	ld	h, #0x00
;src/main.c:162: FillLine(pixFront, posY++);      
	ld	e, d
	inc	e
;src/main.c:161: for (i = 0; i < cy - j; i++) {
	ld	a, l
	sub	a, -2 (ix)
	ld	a, h
	sbc	a, -1 (ix)
	jp	PO, 00136$
	xor	a, #0x80
00136$:
	jp	P, 00103$
;src/main.c:162: FillLine(pixFront, posY++);      
	ld	h, d
	ld	d, e
	push	bc
	push	de
	push	hl
	inc	sp
	ld	a, -4 (ix)
	push	af
	inc	sp
	call	_FillLine
	pop	af
	pop	de
	pop	bc
;src/main.c:161: for (i = 0; i < cy - j; i++) {
	inc	-3 (ix)
	jr	00106$
00103$:
;src/main.c:164: FillLine(pixBack, posY++); 
	ld	5 (ix), e
	push	bc
	ld	e, b
	push	de
	call	_FillLine
	pop	af
	pop	bc
;src/main.c:155: for (j = 0; j < cy; j++) {
	inc	c
	jr	00109$
00104$:
;src/main.c:168: return posY;
	ld	l, 5 (ix)
	ld	sp, ix
	pop	ix
	ret
;src/main.c:174: void DrawSky() {
;	---------------------------------
; Function DrawSky
; ---------------------------------
_DrawSky::
;src/main.c:179: u8 startLine = 0;
;src/main.c:183: for (i = 1; i < sizeof(colors); i++)
	ld	de,#0x0001
00102$:
;src/main.c:184: startLine = DrawSkyGradient(GRADIENT_CY - i, startLine, colors[i], colors[i - 1]);
	ld	c, e
	dec	c
	ld	hl, #_DrawSky_colors_1_141
	ld	b, #0x00
	add	hl, bc
	ld	c, (hl)
	ld	a, #<(_DrawSky_colors_1_141)
	add	a, e
	ld	l, a
	ld	a, #>(_DrawSky_colors_1_141)
	adc	a, #0x00
	ld	h, a
	ld	h, (hl)
	ld	a, #0x0a
	sub	a, e
	ld	b, a
	push	de
	ld	a, c
	push	af
	inc	sp
	ld	l, d
	push	hl
	push	bc
	inc	sp
	call	_DrawSkyGradient
	pop	af
	pop	af
	pop	de
	ld	d, l
;src/main.c:183: for (i = 1; i < sizeof(colors); i++)
	inc	e
	ld	a, e
	sub	a, #0x08
	jr	C,00102$
	ret
_DrawSky_colors_1_141:
	.db #0x02	; 2
	.db #0x0f	; 15
	.db #0x02	; 2
	.db #0x07	; 7
	.db #0x0a	; 10
	.db #0x0d	; 13
	.db #0x08	; 8
	.db #0x04	; 4
;src/main.c:190: void DrawCity() {
;	---------------------------------
; Function DrawCity
; ---------------------------------
_DrawCity::
;src/main.c:199: cpct_drawSprite(g_building_1, pvmem, G_BUILDING_1_W, G_BUILDING_1_H);
	ld	hl, #0x7d0b
	push	hl
	ld	hl, #0xdada
	push	hl
	ld	hl, #_g_building_1
	push	hl
	call	_cpct_drawSprite
;src/main.c:202: cpct_drawSprite(g_building_2, pvmem, G_BUILDING_2_W, G_BUILDING_2_H);
	ld	hl, #0x6707
	push	hl
	ld	hl, #0xcbde
	push	hl
	ld	hl, #_g_building_2
	push	hl
	call	_cpct_drawSprite
;src/main.c:205: cpct_drawSprite(g_building_1, pvmem, G_BUILDING_1_W, G_BUILDING_1_H);
	ld	hl, #0x7d0b
	push	hl
	ld	hl, #0xdaf8
	push	hl
	ld	hl, #_g_building_1
	push	hl
	call	_cpct_drawSprite
;src/main.c:208: cpct_drawSprite(g_building_2, pvmem, G_BUILDING_2_W, G_BUILDING_2_H);
	ld	hl, #0x6707
	push	hl
	ld	hl, #0xcc03
	push	hl
	ld	hl, #_g_building_2
	push	hl
	call	_cpct_drawSprite
;src/main.c:211: cpct_drawSprite(g_building_3, pvmem, G_BUILDING_3_W, G_BUILDING_3_H);
	ld	hl, #0x5009
	push	hl
	ld	hl, #0xc4ec
	push	hl
	ld	hl, #_g_building_3
	push	hl
	call	_cpct_drawSprite
	ret
;src/main.c:217: void InitCapture() {
;	---------------------------------
; Function InitCapture
; ---------------------------------
_InitCapture::
;src/main.c:221: cpct_getScreenToSprite(pvmem, gScreenCapture, G_UFO_0_W, G_UFO_0_H);
	ld	hl, #0x1510
	push	hl
	ld	hl, #_gScreenCapture
	push	hl
	ld	hl, #0xc4b0
	push	hl
	call	_cpct_getScreenToSprite
	ret
;src/main.c:227: void DrawBackground() {
;	---------------------------------
; Function DrawBackground
; ---------------------------------
_DrawBackground::
;src/main.c:228: DrawSky();
	call	_DrawSky
;src/main.c:229: DrawCity();
	call	_DrawCity
;src/main.c:231: InitCapture();
	jp  _InitCapture
;src/main.c:237: void main(void)  {
;	---------------------------------
; Function main
; ---------------------------------
_main::
;src/main.c:238: Initialization();   // Initialize everything
	call	_Initialization
;src/main.c:239: DrawBackground();   // Draw background with sky and buildings
	call	_DrawBackground
;src/main.c:242: while(1) {
00102$:
;src/main.c:243: DrawUFO();
	call	_DrawUFO
	jr	00102$
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
