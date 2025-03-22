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
	.globl _checkUserInput
	.globl _drawEntity
	.globl _shiftSprite
	.globl _shiftSpritePixelsLeft
	.globl _shiftSpritePixelsRight
	.globl _cpct_getScreenPtr
	.globl _cpct_setPALColour
	.globl _cpct_setPalette
	.globl _cpct_waitVSYNC
	.globl _cpct_setVideoMode
	.globl _cpct_drawSprite
	.globl _cpct_drawSolidBox
	.globl _cpct_isKeyPressed
	.globl _cpct_scanKeyboard_f
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
;src/main.c:53: void shiftSpritePixelsRight(u8* sprite, u8 size) {
;	---------------------------------
; Function shiftSpritePixelsRight
; ---------------------------------
_shiftSpritePixelsRight::
	push	ix
	ld	ix,#0
	add	ix,sp
	dec	sp
;src/main.c:58: prev_rightpixel = 0;
	ld	c, #0x00
;src/main.c:59: do {
	ld	l,4 (ix)
	ld	h,5 (ix)
	ld	b, 6 (ix)
00101$:
;src/main.c:61: rightpixel      = *sprite & 0b01010101;
	ld	e, (hl)
	ld	a, e
	and	a, #0x55
	ld	-1 (ix), a
;src/main.c:64: *sprite         = (prev_rightpixel << 1) | ((*sprite & 0b10101010) >> 1);
	sla	c
	ld	a, e
	and	a, #0xaa
	srl	a
	or	a, c
	ld	(hl), a
;src/main.c:66: prev_rightpixel = rightpixel;
	ld	c, -1 (ix)
;src/main.c:67: ++sprite;
	inc	hl
;src/main.c:68: } while(--size);
	djnz	00101$
	inc	sp
	pop	ix
	ret
;src/main.c:74: void shiftSpritePixelsLeft(u8* sprite, u8 size) {
;	---------------------------------
; Function shiftSpritePixelsLeft
; ---------------------------------
_shiftSpritePixelsLeft::
	push	ix
	ld	ix,#0
	add	ix,sp
	push	af
;src/main.c:75: u8* next_byte = sprite + 1; // Maintain a pointer to the next byte of the sprite 
	ld	c,4 (ix)
	ld	b,5 (ix)
	inc	bc
;src/main.c:80: while (--size) {
	ld	e,4 (ix)
	ld	d,5 (ix)
	ld	a, 6 (ix)
	ld	-1 (ix), a
00101$:
	dec	-1 (ix)
;src/main.c:84: *sprite = ((*sprite & 0b01010101) << 1) | ((*(next_byte) & 0b10101010) >> 1);
	ld	a, (de)
	and	a, #0x55
	add	a, a
	ld	-2 (ix), a
;src/main.c:80: while (--size) {
	ld	a, -1 (ix)
	or	a, a
	jr	Z,00103$
;src/main.c:84: *sprite = ((*sprite & 0b01010101) << 1) | ((*(next_byte) & 0b10101010) >> 1);
	ld	a, (bc)
	and	a, #0xaa
	srl	a
	or	a, -2 (ix)
	ld	(de), a
;src/main.c:85: ++sprite; ++next_byte;
	inc	de
	inc	bc
	jr	00101$
00103$:
;src/main.c:89: *sprite = (*sprite & 0b01010101) << 1;
	ld	a, -2 (ix)
	ld	(de), a
	ld	sp, ix
	pop	ix
	ret
;src/main.c:95: void shiftSprite(TEntity *e) {
;	---------------------------------
; Function shiftSprite
; ---------------------------------
_shiftSprite::
	push	ix
	ld	ix,#0
	add	ix,sp
	push	af
;src/main.c:98: if (e->shift == ON_EVEN_PIXEL) {     
	ld	e,4 (ix)
	ld	d,5 (ix)
	ld	hl, #0x0008
	add	hl,de
	ex	(sp), hl
	pop	hl
	push	hl
	ld	c, (hl)
;src/main.c:100: shiftSpritePixelsRight(e->sprite, e->w * e->h);
	ld	l, e
	ld	h, d
	push	de
	pop	iy
	inc	hl
	inc	hl
	inc	hl
	inc	hl
	ld	b, (hl)
	ld	a, 5 (iy)
	ex	de,hl
	ld	de, #0x0006
	add	hl, de
	ld	e, (hl)
	inc	hl
	ld	d, (hl)
	push	de
	ld	e, a
	ld	h, b
	ld	l, #0x00
	ld	d, l
	ld	b, #0x08
00110$:
	add	hl, hl
	jr	NC,00111$
	add	hl, de
00111$:
	djnz	00110$
	pop	de
	ld	b, l
;src/main.c:98: if (e->shift == ON_EVEN_PIXEL) {     
	ld	a, c
	or	a, a
	jr	NZ,00102$
;src/main.c:100: shiftSpritePixelsRight(e->sprite, e->w * e->h);
	push	bc
	inc	sp
	push	de
	call	_shiftSpritePixelsRight
	pop	af
	inc	sp
;src/main.c:101: e->shift = ON_ODD_PIXEL;
	pop	hl
	push	hl
	ld	(hl), #0x01
	jr	00104$
00102$:
;src/main.c:104: shiftSpritePixelsLeft(e->sprite, e->w * e->h);
	push	bc
	inc	sp
	push	de
	call	_shiftSpritePixelsLeft
	pop	af
	inc	sp
;src/main.c:105: e->shift = ON_EVEN_PIXEL;
	pop	hl
	push	hl
	ld	(hl), #0x00
00104$:
	ld	sp, ix
	pop	ix
	ret
;src/main.c:113: void drawEntity(TEntity *e) {
;	---------------------------------
; Function drawEntity
; ---------------------------------
_drawEntity::
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	hl, #-12
	add	hl, sp
	ld	sp, hl
;src/main.c:119: if (e->shift != (TShiftStatus) e->nx % 2)
	ld	c,4 (ix)
	ld	b,5 (ix)
	push	bc
	pop	iy
	ld	e, 8 (iy)
	ld	hl, #0x0002
	add	hl,bc
	ld	-2 (ix), l
	ld	-1 (ix), h
	ld	a, (hl)
	and	a, #0x01
	sub	a, e
	jr	Z,00102$
;src/main.c:120: shiftSprite(e);
	push	bc
	push	bc
	call	_shiftSprite
	pop	af
	pop	bc
00102$:
;src/main.c:123: cpct_waitVSYNC();
	push	bc
	call	_cpct_waitVSYNC
	pop	bc
;src/main.c:128: pscr = cpct_getScreenPtr(CPCT_VMEM_START, e->x / PIXELS_PER_BYTE, e->y);
	ld	hl, #0x0001
	add	hl,bc
	ex	(sp), hl
	pop	hl
	push	hl
	ld	d, (hl)
	ld	a, (bc)
	srl	a
	push	bc
	ld	e, a
	push	de
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
	ex	de,hl
	pop	bc
;src/main.c:129: cpct_drawSolidBox(pscr, 0x00, e->w, e->h);
	ld	hl, #0x0005
	add	hl,bc
	ld	-10 (ix), l
	ld	-9 (ix), h
	ld	a, (hl)
	ld	-6 (ix), a
	ld	hl, #0x0004
	add	hl,bc
	ld	-8 (ix), l
	ld	-7 (ix), h
	ld	a, (hl)
	ld	-3 (ix), a
	push	bc
	ld	h, -6 (ix)
	ld	l, -3 (ix)
	push	hl
	ld	hl, #0x0000
	push	hl
	push	de
	call	_cpct_drawSolidBox
	pop	bc
;src/main.c:132: pscr = cpct_getScreenPtr(CPCT_VMEM_START, e->nx / PIXELS_PER_BYTE, e->ny);
	ld	hl, #0x0003
	add	hl,bc
	ld	-5 (ix), l
	ld	-4 (ix), h
	ld	d, (hl)
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	ld	a, (hl)
	srl	a
	push	bc
	ld	e, a
	push	de
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
	ex	de,hl
	pop	bc
;src/main.c:133: cpct_drawSprite(e->sprite, pscr, e->w, e->h);
	ld	l,-10 (ix)
	ld	h,-9 (ix)
	ld	a, (hl)
	ld	-3 (ix), a
	ld	l,-8 (ix)
	ld	h,-7 (ix)
	ld	a, (hl)
	ld	-8 (ix), a
	push	de
	pop	iy
	ld	l, c
	ld	h, b
	ld	de, #0x0006
	add	hl, de
	ld	e, (hl)
	inc	hl
	ld	d, (hl)
	push	bc
	ld	h, -3 (ix)
	ld	l, -8 (ix)
	push	hl
	push	iy
	push	de
	call	_cpct_drawSprite
	pop	bc
;src/main.c:136: e->x = e->nx;
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	ld	a, (hl)
	ld	(bc), a
;src/main.c:137: e->y = e->ny;
	ld	l,-5 (ix)
	ld	h,-4 (ix)
	ld	c, (hl)
	pop	hl
	push	hl
	ld	(hl), c
	ld	sp, ix
	pop	ix
	ret
;src/main.c:143: void checkUserInput(TEntity *e) {
;	---------------------------------
; Function checkUserInput
; ---------------------------------
_checkUserInput::
	push	ix
	ld	ix,#0
	add	ix,sp
	push	af
	dec	sp
;src/main.c:144: cpct_scanKeyboard_f();
	call	_cpct_scanKeyboard_f
;src/main.c:148: if (cpct_isKeyPressed(Key_CursorLeft) && e->nx > 0) {
	ld	hl, #0x0101
	call	_cpct_isKeyPressed
	ld	a, 4 (ix)
	ld	-2 (ix), a
	ld	a, 5 (ix)
	ld	-1 (ix), a
	ld	c,-2 (ix)
	ld	b,-1 (ix)
	inc	bc
	inc	bc
	ld	a, l
	or	a, a
	jr	Z,00105$
	ld	a, (bc)
	or	a, a
	jr	Z,00105$
;src/main.c:149: e->nx--;
	add	a, #0xff
	ld	(bc), a
	jr	00106$
00105$:
;src/main.c:150: } else if (cpct_isKeyPressed(Key_CursorRight) && e->nx + e->w*PIXELS_PER_BYTE < SCR_WIDTH_PIXELS) {
	push	bc
	ld	hl, #0x0200
	call	_cpct_isKeyPressed
	pop	bc
	ld	a, l
	or	a, a
	jr	Z,00106$
	ld	a, (bc)
	ld	-3 (ix), a
	ld	e, a
	ld	d, #0x00
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	inc	hl
	inc	hl
	inc	hl
	inc	hl
	ld	l, (hl)
	ld	h, #0x00
	add	hl, hl
	add	hl, de
	ld	de, #0x80a0
	add	hl, hl
	ccf
	rr	h
	rr	l
	sbc	hl, de
	jr	NC,00106$
;src/main.c:151: e->nx++;
	ld	a, -3 (ix)
	inc	a
	ld	(bc), a
00106$:
;src/main.c:153: if (cpct_isKeyPressed(Key_CursorUp) && e->ny > 0) {
	ld	hl, #0x0100
	call	_cpct_isKeyPressed
	ld	c,-2 (ix)
	ld	b,-1 (ix)
	inc	bc
	inc	bc
	inc	bc
	ld	a, l
	or	a, a
	jr	Z,00112$
	ld	a, (bc)
	or	a, a
	jr	Z,00112$
;src/main.c:154: e->ny--;
	add	a, #0xff
	ld	(bc), a
	jr	00115$
00112$:
;src/main.c:155: } else if (cpct_isKeyPressed(Key_CursorDown) && e->ny + e->h < SCR_HEIGHT_PIXELS) {
	push	bc
	ld	hl, #0x0400
	call	_cpct_isKeyPressed
	pop	bc
	ld	a, l
	or	a, a
	jr	Z,00115$
	ld	a, (bc)
	ld	-3 (ix), a
	ld	e, a
	ld	d, #0x00
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	inc	hl
	inc	hl
	inc	hl
	inc	hl
	inc	hl
	ld	l, (hl)
	ld	h, #0x00
	add	hl, de
	ld	de, #0x80c8
	add	hl, hl
	ccf
	rr	h
	rr	l
	sbc	hl, de
	jr	NC,00115$
;src/main.c:156: e->ny++;
	ld	a, -3 (ix)
	inc	a
	ld	(bc), a
00115$:
	ld	sp, ix
	pop	ix
	ret
;src/main.c:163: void main(void) {
;	---------------------------------
; Function main
; ---------------------------------
_main::
;src/main.c:175: TEntity* e = (void*)&ec;// And then we create a non-const pointer to modify the data
	ld	bc, #_main_ec_1_147+0
;src/main.c:178: cpct_disableFirmware();          // Firmware must be disabled
	push	bc
	call	_cpct_disableFirmware
	ld	l, #0x00
	call	_cpct_setVideoMode
	ld	hl, #0x0005
	push	hl
	ld	hl, #_g_palette
	push	hl
	call	_cpct_setPalette
	pop	bc
;src/main.c:181: cpct_setBorder(g_palette[0]);    // Set the border to the background colour (colour 0)
	ld	hl, #_g_palette + 0
	ld	d, (hl)
	push	bc
	ld	e, #0x10
	push	de
	call	_cpct_setPALColour
	ld	hl, #0x4000
	push	hl
	ld	hl, #0x5555
	push	hl
	ld	hl, #0xc000
	push	hl
	call	_cpct_memset_f64
	pop	bc
;src/main.c:185: while (1) {
00102$:
;src/main.c:186: checkUserInput(e);  // Get user input and perform actions
	push	bc
	push	bc
	call	_checkUserInput
	pop	af
	pop	bc
;src/main.c:187: drawEntity(e);      // Draw the entity at its new location on screen
	push	bc
	push	bc
	call	_drawEntity
	pop	af
	pop	bc
	jr	00102$
_main_ec_1_147:
	.db #0x20	; 32
	.db #0x58	; 88	'X'
	.db #0x20	; 32
	.db #0x58	; 88	'X'
	.db #0x08	; 8
	.db #0x18	; 24
	.dw _g_character
	.db #0x00	; 0
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
