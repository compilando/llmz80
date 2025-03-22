;--------------------------------------------------------
; File Created by SDCC : free open source ANSI-C Compiler
; Version 3.6.8 #9946 (Linux)
;--------------------------------------------------------
	.module palette
	.optsdcc -mz80
	
;--------------------------------------------------------
; Public variables in this module
;--------------------------------------------------------
	.globl _wait_frames
	.globl _cpct_setPALColour
	.globl _G_rgb2hw
	.globl _G_rgb_palette
	.globl _setPALColourRGBLimited
	.globl _fade_in
	.globl _fade_out
	.globl _setBlackPalette
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
;src/modules/palette.c:80: void setPALColourRGBLimited(u8 pal_index, const u8 rgb[3], const u8 maxrgb[3]) {
;	---------------------------------
; Function setPALColourRGBLimited
; ---------------------------------
_setPALColourRGBLimited::
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	hl, #-6
	add	hl, sp
	ld	sp, hl
;src/modules/palette.c:86: for (i=0; i < 3; ++i) {
	ld	hl, #0x0000
	add	hl, sp
	ld	-2 (ix), l
	ld	-1 (ix), h
	ld	c, #0x00
00104$:
;src/modules/palette.c:87: s[i] = rgb[i];  // The colour component to set is the one given in rgb[]
	ld	a, -2 (ix)
	add	a, c
	ld	e, a
	ld	a, -1 (ix)
	adc	a, #0x00
	ld	d, a
	push	hl
	ld	l, 5 (ix)
	ld	h, 6 (ix)
	push	hl
	pop	iy
	pop	hl
	push	bc
	ld	b,#0x00
	add	iy, bc
	pop	bc
	ld	a, 0 (iy)
	ld	(de), a
;src/modules/palette.c:91: if ( rgb[i] > maxrgb[i] ) 
	ld	a, 0 (iy)
	ld	-3 (ix), a
	ld	l,7 (ix)
	ld	h,8 (ix)
	ld	b, #0x00
	add	hl, bc
	ld	b, (hl)
	ld	a, b
	sub	a, -3 (ix)
	jr	NC,00105$
;src/modules/palette.c:92: s[i] = maxrgb[i];
	ld	a, b
	ld	(de), a
00105$:
;src/modules/palette.c:86: for (i=0; i < 3; ++i) {
	inc	c
	ld	a, c
	sub	a, #0x03
	jr	C,00104$
;src/modules/palette.c:96: i = G_rgb2hw[ s[0] ][ s[1] ][ s[2] ];
	ld	bc, #_G_rgb2hw+0
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	ld	e, (hl)
	ld	d,#0x00
	ld	l, e
	ld	h, d
	add	hl, hl
	add	hl, hl
	add	hl, hl
	add	hl, de
	add	hl,bc
	ld	c, l
	ld	b, h
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	inc	hl
	ld	e, (hl)
	ld	l, e
	add	hl, hl
	add	hl, de
	ld	a, c
	add	a, l
	ld	c, a
	ld	a, b
	adc	a, #0x00
	ld	b, a
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	inc	hl
	inc	hl
	ld	l, (hl)
	ld	h,#0x00
	add	hl, bc
	ld	b, (hl)
;src/modules/palette.c:99: cpct_setPALColour(pal_index, i);
	push	bc
	inc	sp
	ld	a, 4 (ix)
	push	af
	inc	sp
	call	_cpct_setPALColour
	ld	sp, ix
	pop	ix
	ret
_G_rgb_palette:
	.db #0x01	; 1
	.db #0x01	; 1
	.db #0x01	; 1
	.db #0x02	; 2
	.db #0x01	; 1
	.db #0x00	; 0
	.db #0x01	; 1
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x02	; 2
	.db #0x02	; 2
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x01	; 1
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x02	; 2
	.db #0x02	; 2
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x02	; 2
	.db #0x02	; 2
	.db #0x02	; 2
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x02	; 2
	.db #0x00	; 0
	.db #0x01	; 1
	.db #0x02	; 2
	.db #0x00	; 0
	.db #0x02	; 2
	.db #0x00	; 0
	.db #0x02	; 2
	.db #0x00	; 0
	.db #0x02	; 2
	.db #0x01	; 1
	.db #0x00	; 0
	.db #0x02	; 2
	.db #0x02	; 2
	.db #0x01	; 1
	.db #0x01	; 1
	.db #0x00	; 0
	.db #0x01	; 1
	.db #0x00	; 0
	.db #0x01	; 1
	.db #0x01	; 1
	.db #0x01	; 1
_G_rgb2hw:
	.db #0x14	; 20
	.db #0x04	; 4
	.db #0x15	; 21
	.db #0x16	; 22
	.db #0x06	; 6
	.db #0x17	; 23
	.db #0x12	; 18
	.db #0x02	; 2
	.db #0x13	; 19
	.db #0x1c	; 28
	.db #0x18	; 24
	.db #0x1d	; 29
	.db #0x1e	; 30
	.db #0x00	; 0
	.db #0x1f	; 31
	.db #0x1a	; 26
	.db #0x19	; 25
	.db #0x1b	; 27
	.db #0x0c	; 12
	.db #0x05	; 5
	.db #0x0d	; 13
	.db #0x0e	; 14
	.db #0x07	; 7
	.db #0x0f	; 15
	.db #0x0a	; 10
	.db #0x03	; 3
	.db #0x0b	; 11
;src/modules/palette.c:116: void fade_in(const u8 rgb[][3], u8 min_pi, u8 max_pi, u8 wait) {
;	---------------------------------
; Function fade_in
; ---------------------------------
_fade_in::
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	hl, #-11
	add	hl, sp
	ld	sp, hl
;src/modules/palette.c:119: u8 maxrgb[3]={0,0,0}; // Maximum components for the 3 RGB values, initially 0 (to slowly increase)
	ld	hl, #0x0000
	add	hl, sp
	ld	c, l
	ld	b, h
	xor	a, a
	ld	(bc), a
	ld	e, c
	ld	d, b
	inc	de
	xor	a, a
	ld	(de), a
	ld	e, c
	ld	d, b
	inc	de
	inc	de
	xor	a, a
	ld	(de), a
;src/modules/palette.c:126: while (maxrgb[col] <= 2) {
	ld	-2 (ix), c
	ld	-1 (ix), b
	ld	e, #0x00
00102$:
	ld	a, e
	add	a, c
	ld	-6 (ix), a
	ld	a, #0x00
	adc	a, b
	ld	-5 (ix), a
	ld	l,-6 (ix)
	ld	h,-5 (ix)
	ld	d, (hl)
	ld	a, #0x02
	sub	a, d
	jr	C,00110$
;src/modules/palette.c:130: for(pi=min_pi; pi <= max_pi; ++pi)
	ld	d, 6 (ix)
00107$:
	ld	a, 7 (ix)
	sub	a, d
	jr	C,00101$
;src/modules/palette.c:131: setPALColourRGBLimited(pi, rgb[pi], maxrgb);
	ld	a, -2 (ix)
	ld	-4 (ix), a
	ld	a, -1 (ix)
	ld	-3 (ix), a
	push	de
	ld	e,d
	ld	d,#0x00
	ld	l, e
	ld	h, d
	add	hl, hl
	add	hl, de
	pop	de
	ld	-8 (ix), l
	ld	-7 (ix), h
	push	hl
	ld	l, 4 (ix)
	ld	h, 5 (ix)
	push	hl
	pop	iy
	pop	hl
	push	bc
	ld	c,-8 (ix)
	ld	b,-7 (ix)
	add	iy, bc
	push	de
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	push	hl
	push	iy
	push	de
	inc	sp
	call	_setPALColourRGBLimited
	pop	af
	pop	af
	inc	sp
	pop	de
	pop	bc
;src/modules/palette.c:130: for(pi=min_pi; pi <= max_pi; ++pi)
	inc	d
	jr	00107$
00101$:
;src/modules/palette.c:133: ++maxrgb[col];     // Increase present maximum colour component limit
	ld	l,-6 (ix)
	ld	h,-5 (ix)
	ld	d, (hl)
	inc	d
	ld	l,-6 (ix)
	ld	h,-5 (ix)
	ld	(hl), d
;src/modules/palette.c:134: wait_frames(wait); // Wait some frames to slow down the effect and see the changes
	ld	l, 8 (ix)
	ld	h, #0x00
	push	bc
	push	de
	push	hl
	call	_wait_frames
	pop	af
	pop	de
	pop	bc
	jp	00102$
00110$:
;src/modules/palette.c:122: for(col=0; col <= 2; ++col){
	inc	e
	ld	a, #0x02
	sub	a, e
	jp	NC, 00102$
	ld	sp, ix
	pop	ix
	ret
;src/modules/palette.c:145: void fade_out(const u8 rgb[][3], u8 min_pi, u8 max_pi, u8 wait) {
;	---------------------------------
; Function fade_out
; ---------------------------------
_fade_out::
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	hl, #-11
	add	hl, sp
	ld	sp, hl
;src/modules/palette.c:148: u8 maxrgb[3]={2,2,2}; // Maximum components for the 3 RGB values, initially 2 (to slowly decrease)
	ld	hl, #0x0000
	add	hl, sp
	ld	c,l
	ld	b,h
	ld	(hl),#0x02
	ld	l, c
	ld	h, b
	inc	hl
	ld	(hl), #0x02
	ld	l, c
	ld	h, b
	inc	hl
	inc	hl
	ld	(hl), #0x02
;src/modules/palette.c:155: do {
	ld	-2 (ix), c
	ld	-1 (ix), b
	ld	e, #0x00
00102$:
;src/modules/palette.c:156: --maxrgb[col];  // Decrease present maximum colour component limit
	ld	a, e
	add	a, c
	ld	-8 (ix), a
	ld	a, #0x00
	adc	a, b
	ld	-7 (ix), a
	ld	l,-8 (ix)
	ld	h,-7 (ix)
	ld	d, (hl)
	dec	d
	ld	l,-8 (ix)
	ld	h,-7 (ix)
	ld	(hl), d
;src/modules/palette.c:160: for(pi=min_pi; pi <= max_pi; ++pi)
	ld	d, 6 (ix)
00107$:
	ld	a, 7 (ix)
	sub	a, d
	jr	C,00101$
;src/modules/palette.c:161: setPALColourRGBLimited(pi, rgb[pi], maxrgb);
	ld	a, -2 (ix)
	ld	-4 (ix), a
	ld	a, -1 (ix)
	ld	-3 (ix), a
	push	de
	ld	e,d
	ld	d,#0x00
	ld	l, e
	ld	h, d
	add	hl, hl
	add	hl, de
	pop	de
	ld	-6 (ix), l
	ld	-5 (ix), h
	push	hl
	ld	l, -6 (ix)
	ld	h, -5 (ix)
	push	hl
	pop	iy
	pop	hl
	push	bc
	ld	c,4 (ix)
	ld	b,5 (ix)
	add	iy, bc
	push	de
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	push	hl
	push	iy
	push	de
	inc	sp
	call	_setPALColourRGBLimited
	pop	af
	pop	af
	inc	sp
	pop	de
	pop	bc
;src/modules/palette.c:160: for(pi=min_pi; pi <= max_pi; ++pi)
	inc	d
	jr	00107$
00101$:
;src/modules/palette.c:163: wait_frames(wait); // Wait some frames to slow down the effect and see the changes
	ld	l, 8 (ix)
	ld	h, #0x00
	push	bc
	push	de
	push	hl
	call	_wait_frames
	pop	af
	pop	de
	pop	bc
;src/modules/palette.c:164: } while (maxrgb[col] > 0);
	ld	l,-8 (ix)
	ld	h,-7 (ix)
	ld	a, (hl)
	or	a, a
	jp	NZ, 00102$
;src/modules/palette.c:151: for(col=0; col <= 2; ++col){
	inc	e
	ld	a, #0x02
	sub	a, e
	jp	NC, 00102$
	ld	sp, ix
	pop	ix
	ret
;src/modules/palette.c:172: void setBlackPalette(u8 min_pi, u8 max_pi) {
;	---------------------------------
; Function setBlackPalette
; ---------------------------------
_setBlackPalette::
;src/modules/palette.c:176: for(i=min_pi; i <= max_pi; ++i)
	ld	hl, #2+0
	add	hl, sp
	ld	b, (hl)
00103$:
	ld	hl, #3
	add	hl, sp
	ld	a, (hl)
	sub	a, b
	ret	C
;src/modules/palette.c:177: cpct_setPALColour(i, G_rgb2hw[0][0][0]);  
	ld	hl, #_G_rgb2hw + 0
	ld	d, (hl)
	push	bc
	ld	e, b
	push	de
	call	_cpct_setPALColour
	pop	bc
;src/modules/palette.c:176: for(i=min_pi; i <= max_pi; ++i)
	inc	b
	jr	00103$
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
