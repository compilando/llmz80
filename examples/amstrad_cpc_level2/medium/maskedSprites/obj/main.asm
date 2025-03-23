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
	.globl _initialization
	.globl _repaintBackgroundOverSprite
	.globl _drawBackground
	.globl _drawFrame
	.globl _cpct_getScreenPtr
	.globl _cpct_setPALColour
	.globl _cpct_setPalette
	.globl _cpct_fw2hw
	.globl _cpct_waitVSYNC
	.globl _cpct_setVideoMode
	.globl _cpct_drawSpriteMasked
	.globl _cpct_drawSolidBox
	.globl _cpct_px2byteM0
	.globl _cpct_drawTileAligned4x8_f
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
;src/main.c:41: void drawFrame() {
;	---------------------------------
; Function drawFrame
; ---------------------------------
_drawFrame::
;src/main.c:46: pattern = cpct_px2byteM0 (15, 15);
	ld	hl, #0x0f0f
	push	hl
	call	_cpct_px2byteM0
	ld	c, l
;src/main.c:49: pvmem = cpct_getScreenPtr(CPCT_VMEM_START, (BACK_X),  (BACK_Y - 8) );
	push	bc
	ld	hl, #0x400c
	push	hl
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
	pop	bc
;src/main.c:50: cpct_drawSolidBox(pvmem, pattern, 4*BACK_W,  8);
	ld	b, #0x00
	push	bc
	ld	de, #0x0838
	push	de
	push	bc
	push	hl
	call	_cpct_drawSolidBox
	ld	hl, #0x780c
	push	hl
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
	pop	bc
;src/main.c:54: cpct_drawSolidBox(pvmem, pattern, 4*BACK_W,  8);
	push	bc
	ld	de, #0x0838
	push	de
	push	bc
	push	hl
	call	_cpct_drawSolidBox
	ld	hl, #0x4008
	push	hl
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
	pop	bc
;src/main.c:58: cpct_drawSolidBox(pvmem, pattern,  4, 8*(BACK_H + 2) );
	push	bc
	ld	de, #0x4004
	push	de
	push	bc
	push	hl
	call	_cpct_drawSolidBox
	ld	hl, #0x4044
	push	hl
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
	pop	bc
;src/main.c:62: cpct_drawSolidBox(pvmem, pattern,  4, 8*(BACK_H + 2) );
	ld	de, #0x4004
	push	de
	push	bc
	push	hl
	call	_cpct_drawSolidBox
	ret
;src/main.c:70: void drawBackground() {
;	---------------------------------
; Function drawBackground
; ---------------------------------
_drawBackground::
	push	ix
	ld	ix,#0
	add	ix,sp
	dec	sp
;src/main.c:77: for (y=0; y < BACK_H; ++y) {     
	ld	c, #0x00
00105$:
;src/main.c:82: pvideomem = cpct_getScreenPtr(CPCT_VMEM_START, BACK_X, BACK_Y + 8*y);
	ld	a, c
	rlca
	rlca
	rlca
	and	a, #0xf8
	add	a, #0x48
	ld	b, a
	push	bc
	push	bc
	inc	sp
	ld	a, #0x0c
	push	af
	inc	sp
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
	ex	de,hl
	pop	bc
;src/main.c:85: for(x=0; x < BACK_W; ++x) {
	ld	a, c
	rrca
	rrca
	rrca
	and	a, #0xe0
	ld	-1 (ix), a
	ld	b, #0x00
00103$:
;src/main.c:86: cpct_drawTileAligned4x8_f(G_background[x][y], pvideomem);  // Draw next tile
	push	de
	pop	iy
	push	de
	ld	e,b
	ld	d,#0x00
	ld	l, e
	ld	h, d
	add	hl, hl
	add	hl, de
	add	hl, hl
	add	hl, hl
	add	hl, hl
	add	hl, hl
	add	hl, hl
	add	hl, hl
	pop	de
	ld	a, #<(_G_background)
	add	a, l
	ld	l, a
	ld	a, #>(_G_background)
	adc	a, h
	ld	h, a
	ld	a, -1 (ix)
	add	a, l
	ld	l, a
	ld	a, #0x00
	adc	a, h
	ld	h, a
	push	bc
	push	de
	push	iy
	push	hl
	call	_cpct_drawTileAligned4x8_f
	pop	de
	pop	bc
;src/main.c:90: pvideomem += 4;  
	inc	de
	inc	de
	inc	de
	inc	de
;src/main.c:85: for(x=0; x < BACK_W; ++x) {
	inc	b
	ld	a, b
	sub	a, #0x0e
	jr	C,00103$
;src/main.c:77: for (y=0; y < BACK_H; ++y) {     
	inc	c
	ld	a, c
	sub	a, #0x06
	jr	C,00105$
	inc	sp
	pop	ix
	ret
;src/main.c:101: void repaintBackgroundOverSprite(u8 x, u8 y) {
;	---------------------------------
; Function repaintBackgroundOverSprite
; ---------------------------------
_repaintBackgroundOverSprite::
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	hl, #-9
	add	hl, sp
	ld	sp, hl
;src/main.c:106: u8 tilex = (x - BACK_X) / 4;   // Calculate tile column into the tile array (integer division, 4 bytes per tile)
	ld	c, 4 (ix)
	ld	b, #0x00
	ld	a, c
	add	a, #0xf4
	ld	e, a
	ld	a, b
	adc	a, #0xff
	ld	d, a
	ld	l, e
	ld	h, d
	bit	7, d
	jr	Z,00103$
	ld	hl, #0xfff7
	add	hl, bc
00103$:
	sra	h
	rr	l
	sra	h
	rr	l
	ld	-8 (ix), l
;src/main.c:107: u8 tiley = (y - BACK_Y) / 8;   // Calculate tile row into the tile array (integer division, 8 bytes per tile)
	ld	c, 5 (ix)
	ld	b, #0x00
	ld	a, c
	add	a, #0xb8
	ld	e, a
	ld	a, b
	adc	a, #0xff
	ld	d, a
	ld	l, e
	ld	h, d
	bit	7, d
	jr	Z,00104$
	ld	hl, #0xffbf
	add	hl, bc
00104$:
	sra	h
	rr	l
	sra	h
	rr	l
	sra	h
	rr	l
	ld	-9 (ix), l
;src/main.c:108: u8 scrx = BACK_X + 4*tilex;    // Calculate x screen byte coordinate of the tile
	ld	a, -8 (ix)
	add	a, a
	add	a, a
	add	a, #0x0c
	ld	-7 (ix), a
;src/main.c:109: u8 scry = BACK_Y + 8*tiley;    // Calculate y screen byte coordinate of the tile
	ld	a, -9 (ix)
	rlca
	rlca
	rlca
	and	a, #0xf8
	add	a, #0x48
;src/main.c:116: pvmem = cpct_getScreenPtr(CPCT_VMEM_START, scrx, scry);
	ld	-6 (ix), a
	push	af
	inc	sp
	ld	a, -7 (ix)
	push	af
	inc	sp
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
	ex	de,hl
;src/main.c:117: cpct_drawTileAligned4x8_f(G_background[tilex  ][tiley], pvmem    );
	ld	c, e
	ld	b, d
	push	de
	ld	e,-8 (ix)
	ld	d,#0x00
	ld	l, e
	ld	h, d
	add	hl, hl
	add	hl, de
	add	hl, hl
	add	hl, hl
	add	hl, hl
	add	hl, hl
	add	hl, hl
	add	hl, hl
	pop	de
	ld	a, #<(_G_background)
	add	a, l
	ld	-2 (ix), a
	ld	a, #>(_G_background)
	adc	a, h
	ld	-1 (ix), a
	ld	a, -9 (ix)
	rrca
	rrca
	rrca
	and	a, #0xe0
	ld	-5 (ix), a
	ld	a, -2 (ix)
	add	a, -5 (ix)
	ld	l, a
	ld	a, -1 (ix)
	adc	a, #0x00
	ld	h, a
	push	de
	push	bc
	push	hl
	call	_cpct_drawTileAligned4x8_f
	pop	de
;src/main.c:118: cpct_drawTileAligned4x8_f(G_background[tilex+1][tiley], pvmem + 4);
	inc	de
	inc	de
	inc	de
	inc	de
	ld	c, -8 (ix)
	ld	b, #0x00
	inc	bc
	ld	l, c
	ld	h, b
	add	hl, hl
	add	hl, bc
	add	hl, hl
	add	hl, hl
	add	hl, hl
	add	hl, hl
	add	hl, hl
	add	hl, hl
	ld	bc,#_G_background
	add	hl,bc
	ld	-4 (ix), l
	ld	-3 (ix), h
	ld	a, -5 (ix)
	add	a, -4 (ix)
	ld	c, a
	ld	a, #0x00
	adc	a, -3 (ix)
	ld	b, a
	push	de
	push	bc
	call	_cpct_drawTileAligned4x8_f
;src/main.c:119: pvmem = cpct_getScreenPtr(CPCT_VMEM_START, scrx, scry + 8);
	ld	a, -6 (ix)
	add	a, #0x08
	ld	b, a
	push	bc
	inc	sp
	ld	a, -7 (ix)
	push	af
	inc	sp
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
;src/main.c:120: cpct_drawTileAligned4x8_f(G_background[tilex  ][tiley+1], pvmem    );
	ld	e, l
	ld	d, h
	ld	a, -9 (ix)
	inc	a
	rrca
	rrca
	rrca
	and	a, #0xe0
	ld	-5 (ix), a
	ld	a, -2 (ix)
	add	a, -5 (ix)
	ld	c, a
	ld	a, -1 (ix)
	adc	a, #0x00
	ld	b, a
	push	hl
	push	de
	push	bc
	call	_cpct_drawTileAligned4x8_f
	pop	hl
;src/main.c:121: cpct_drawTileAligned4x8_f(G_background[tilex+1][tiley+1], pvmem + 4);
	ld	bc, #0x0004
	add	hl, bc
	ld	a, -5 (ix)
	add	a, -4 (ix)
	ld	c, a
	ld	a, #0x00
	adc	a, -3 (ix)
	ld	b, a
	push	hl
	push	bc
	call	_cpct_drawTileAligned4x8_f
	ld	sp, ix
	pop	ix
	ret
;src/main.c:129: void initialization (){ 
;	---------------------------------
; Function initialization
; ---------------------------------
_initialization::
;src/main.c:130: cpct_disableFirmware();          // Disable firmware to prevent it from interfering
	call	_cpct_disableFirmware
;src/main.c:131: cpct_fw2hw     (G_palette, 16);  // Convert firmware colours to hardware colours 
	ld	hl, #0x0010
	push	hl
	ld	hl, #_G_palette
	push	hl
	call	_cpct_fw2hw
;src/main.c:132: cpct_setPalette(G_palette, 16);  // Set palette using hardware colour values
	ld	hl, #0x0010
	push	hl
	ld	hl, #_G_palette
	push	hl
	call	_cpct_setPalette
;src/main.c:133: cpct_setBorder (G_palette[0]);   // Set border colour same as background (0)
	ld	hl, #_G_palette + 0
	ld	b, (hl)
	push	bc
	inc	sp
	ld	a, #0x10
	push	af
	inc	sp
	call	_cpct_setPALColour
;src/main.c:134: cpct_setVideoMode(0);            // Change to Mode 0 (160x200, 16 colours)
	ld	l, #0x00
	call	_cpct_setVideoMode
;src/main.c:136: drawFrame();       // Draw a Frame around the "play zone"
	call	_drawFrame
;src/main.c:137: drawBackground();  // Draw the tiled background
	call	_drawBackground
	ret
;src/main.c:140: void main(void) {
;	---------------------------------
; Function main
; ---------------------------------
_main::
;src/main.c:141: u8 x=BACK_X+1;   // x byte screen coord. of the sprite (1 byte to the right of the start of the "play zone")
;src/main.c:143: i8 vx=1;         // Horizontal movement velocity in bytes (1 byte to the right)
	ld	bc,#0x0d01
;src/main.c:148: initialization();
	push	bc
	call	_initialization
	pop	bc
;src/main.c:153: while(1) {
00106$:
;src/main.c:157: pvmem = cpct_getScreenPtr(CPCT_VMEM_START, x, y);      
	push	bc
	ld	a, #0x68
	push	af
	inc	sp
	push	bc
	inc	sp
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
	ex	de,hl
	ld	hl, #0x1004
	push	hl
	push	de
	ld	hl, #_G_sprite_EMR
	push	hl
	call	_cpct_drawSpriteMasked
	pop	bc
;src/main.c:160: for(i=0; i < WAITLOOPS; i++); // Wait for a little while
	ld	de, #0x0fa0
00110$:
	ex	de,hl
	dec	hl
	ld	e, l
	ld	a,h
	ld	d,a
	or	a,l
	jr	NZ,00110$
;src/main.c:161: cpct_waitVSYNC();             // Synchronize with VSYNC to prevent flickering
	push	bc
	call	_cpct_waitVSYNC
	pop	bc
;src/main.c:163: repaintBackgroundOverSprite(x, y); // Repaint the background only where the sprite is located
	push	bc
	ld	a, #0x68
	push	af
	inc	sp
	push	bc
	inc	sp
	call	_repaintBackgroundOverSprite
	pop	af
	pop	bc
;src/main.c:166: x += vx;
	ld	a, b
	add	a, c
;src/main.c:170: if (x < BACK_X || x > (BACK_X + 4*BACK_W-5) ) {
	ld	b,a
	sub	a, #0x0c
	jr	C,00102$
	ld	a, #0x3f
	sub	a, b
	jr	NC,00106$
00102$:
;src/main.c:171: x -= vx;    // Undo latest movement subtracting vx from current x position
	ld	a, b
	sub	a, c
	ld	b, a
;src/main.c:172: vx = -vx;   // Change the sense of velocity to start moving opposite
	xor	a, a
	sub	a, c
	ld	c, a
	jr	00106$
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
