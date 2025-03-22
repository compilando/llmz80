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
	.globl _initialize_CPC
	.globl _scrollScreenTilemap
	.globl _wait4KeyboardInput
	.globl _cpct_etm_setTileset2x4
	.globl _cpct_etm_drawTileBox2x4
	.globl _cpct_getScreenPtr
	.globl _cpct_setVideoMemoryOffset
	.globl _cpct_setPALColour
	.globl _cpct_setPalette
	.globl _cpct_waitVSYNC
	.globl _cpct_setVideoMode
	.globl _cpct_drawSolidBox
	.globl _cpct_isKeyPressed
	.globl _cpct_scanKeyboard_f
	.globl _cpct_memset
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
;src/main.c:43: i16 wait4KeyboardInput(){
;	---------------------------------
; Function wait4KeyboardInput
; ---------------------------------
_wait4KeyboardInput::
;src/main.c:45: while(1) {
00107$:
;src/main.c:47: cpct_scanKeyboard_f(); 
	call	_cpct_scanKeyboard_f
;src/main.c:51: if      (cpct_isKeyPressed(Key_CursorRight)) return  1;
	ld	hl, #0x0200
	call	_cpct_isKeyPressed
	ld	a, l
	or	a, a
	jr	Z,00104$
	ld	hl, #0x0001
	ret
00104$:
;src/main.c:52: else if (cpct_isKeyPressed(Key_CursorLeft))  return -1;
	ld	hl, #0x0101
	call	_cpct_isKeyPressed
	ld	a, l
	or	a, a
	jr	Z,00107$
	ld	hl, #0xffff
	ret
;src/main.c:60: void scrollScreenTilemap(TScreenTilemap *scr, i16 scroll) { 
;	---------------------------------
; Function scrollScreenTilemap
; ---------------------------------
_scrollScreenTilemap::
	push	ix
	ld	ix,#0
	add	ix,sp
	push	af
	push	af
;src/main.c:63: u8 column = (scroll > 0) ? (SCR_TILE_WIDTH-1) : (0);
	xor	a, a
	cp	a, 6 (ix)
	sbc	a, 7 (ix)
	jp	PO, 00116$
	xor	a, #0x80
00116$:
	rlca
	and	a,#0x01
	ld	-1 (ix), a
	or	a, a
	jr	Z,00106$
	ld	c, #0x27
	jr	00107$
00106$:
	ld	c, #0x00
00107$:
	ld	-4 (ix), c
;src/main.c:67: scr->pVideo   += 2*scroll; // Video memory starts now 2 bytes to the left or to the right
	ld	c,4 (ix)
	ld	b,5 (ix)
	ld	l, c
	ld	h, b
	ld	e, (hl)
	inc	hl
	ld	d, (hl)
	ld	l,6 (ix)
	ld	h,7 (ix)
	add	hl, hl
	add	hl,de
	ex	de,hl
	ld	l, c
	ld	h, b
	ld	(hl), e
	inc	hl
	ld	(hl), d
;src/main.c:68: scr->pTilemap += scroll;   // Move the start pointer to the tilemap 1 tile (1 byte) to point to the drawable zone (viewport)
	ld	hl, #0x0002
	add	hl,bc
	ld	-3 (ix), l
	ld	-2 (ix), h
	ld	e, (hl)
	inc	hl
	ld	d, (hl)
	ld	a, 6 (ix)
	add	a, e
	ld	e, a
	ld	a, 7 (ix)
	adc	a, d
	ld	d, a
	ld	l,-3 (ix)
	ld	h,-2 (ix)
	ld	(hl), e
	inc	hl
	ld	(hl), d
;src/main.c:69: scr->scroll   += scroll;   // Update scroll offset to produce scrolling
	ld	hl, #0x0004
	add	hl, bc
	ld	d, (hl)
	ld	e, 6 (ix)
	ld	a, d
	add	a, e
	ld	(hl), a
;src/main.c:72: cpct_waitVSYNC();
	push	hl
	push	bc
	call	_cpct_waitVSYNC
	pop	bc
	pop	hl
;src/main.c:75: cpct_setVideoMemoryOffset(scr->scroll);    
	ld	l, (hl)
	push	bc
	call	_cpct_setVideoMemoryOffset
	pop	bc
;src/main.c:82: scr->pTilemap);    // Pointer to the first tile of the tilemap to be drawn (upper-left corner
	ld	l,-3 (ix)
	ld	h,-2 (ix)
	ld	e, (hl)
	inc	hl
	ld	d, (hl)
;src/main.c:81: scr->pVideo,       // Pointer to the upper-left corner of the tilemap in video memory
	ld	l, c
	ld	h, b
	ld	a, (hl)
	inc	hl
	ld	h, (hl)
	ld	l, a
;src/main.c:78: cpct_etm_drawTileBox2x4(column, 0,         // (X, Y) Upper-left Location of the Box (column in this case) to be redrawn
	push	bc
	push	de
	push	hl
	ld	hl, #0x782e
	push	hl
	ld	hl, #0x0100
	push	hl
	ld	a, -4 (ix)
	push	af
	inc	sp
	call	_cpct_etm_drawTileBox2x4
;src/main.c:67: scr->pVideo   += 2*scroll; // Video memory starts now 2 bytes to the left or to the right
	pop	hl
	ld	c, (hl)
	inc	hl
	ld	b, (hl)
;src/main.c:90: if (scroll > 0) 
	ld	a, -1 (ix)
	or	a, a
	jr	Z,00102$
;src/main.c:91: cpct_drawSolidBox(scr->pVideo - 2, 0, 2, 8);  // top-left scrolled-out char
	dec	bc
	dec	bc
	ld	hl, #0x0802
	push	hl
	ld	hl, #0x0000
	push	hl
	push	bc
	call	_cpct_drawSolidBox
	jr	00104$
00102$:
;src/main.c:93: u8* br_char = cpct_getScreenPtr(scr->pVideo, 0, 4*MAP_HEIGHT);
	ld	hl, #0xb800
	push	hl
	push	bc
	call	_cpct_getScreenPtr
;src/main.c:94: cpct_drawSolidBox(br_char, 0, 2, 8);  // bottom-right scrolled-out char
	ld	bc, #0x0802
	push	bc
	ld	bc, #0x0000
	push	bc
	push	hl
	call	_cpct_drawSolidBox
00104$:
	ld	sp, ix
	pop	ix
	ret
;src/main.c:101: void initialize_CPC() {
;	---------------------------------
; Function initialize_CPC
; ---------------------------------
_initialize_CPC::
;src/main.c:103: cpct_disableFirmware();         // Firmware must be disabled for this application to work
	call	_cpct_disableFirmware
;src/main.c:104: cpct_setVideoMode(0);           // Set Mode 0 (160x200, 16 Colours)
	ld	l, #0x00
	call	_cpct_setVideoMode
;src/main.c:105: cpct_setPalette(g_palette, 13); // Set Palette 
	ld	hl, #0x000d
	push	hl
	ld	hl, #_g_palette
	push	hl
	call	_cpct_setPalette
;src/main.c:106: cpct_setBorder(HW_BLACK);       // Set the border and background colours to black
	ld	hl, #0x1410
	push	hl
	call	_cpct_setPALColour
;src/main.c:110: cpct_etm_setTileset2x4(g_tileset);   
	ld	hl, #_g_tileset
	call	_cpct_etm_setTileset2x4
;src/main.c:113: cpct_memset(CPCT_VMEM_START, 0x00, 0x4000);
	ld	hl, #0x4000
	push	hl
	xor	a, a
	push	af
	inc	sp
	ld	h, #0xc0
	push	hl
	call	_cpct_memset
;src/main.c:121: g_tilemap);                 // Pointer to the first tile of the tilemap to be drawn (upper-left
;src/main.c:116: cpct_etm_drawTileBox2x4(0, 0,                       // (X, Y) upper-left corner of the tilemap
	ld	hl, #_g_tilemap
	push	hl
	ld	hl, #0xc000
	push	hl
	ld	hl, #0x782e
	push	hl
	ld	hl, #0x2800
	push	hl
	xor	a, a
	push	af
	inc	sp
	call	_cpct_etm_drawTileBox2x4
	ret
;src/main.c:128: void main(void) {
;	---------------------------------
; Function main
; ---------------------------------
_main::
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	hl, #-7
	add	hl, sp
;src/main.c:129: TScreenTilemap scr = { CPCT_VMEM_START, g_tilemap, 0 }; // Screen tilemap properties
	ld	sp, hl
	inc	hl
	inc	hl
	ld	(hl), #0x00
	inc	hl
	ld	(hl), #0xc0
	ld	hl, #0x0002
	add	hl, sp
	ld	c,l
	ld	b,h
	inc	hl
	inc	hl
	ld	de, #_g_tilemap+0
	ld	(hl), e
	inc	hl
	ld	(hl), d
	ld	hl, #0x0004
	add	hl, bc
	ld	(hl), #0x00
;src/main.c:132: initialize_CPC(); // Initialize the machine and set up all necessary things
	push	hl
	push	bc
	call	_initialize_CPC
	pop	bc
	pop	hl
;src/main.c:136: while(1) {
00109$:
;src/main.c:138: scroll_offset = wait4KeyboardInput();
	push	hl
	push	bc
	call	_wait4KeyboardInput
	ex	de,hl
	pop	bc
	pop	hl
	inc	sp
	inc	sp
	push	de
;src/main.c:142: if     ( scr.scroll == MAXSCROLL ) continue;  // Do not scroll passed the right limit
	ld	e, (hl)
;src/main.c:141: if ( scroll_offset > 0 ) {
	xor	a, a
	cp	a, -7 (ix)
	sbc	a, -6 (ix)
	jp	PO, 00125$
	xor	a, #0x80
00125$:
	jp	P, 00106$
;src/main.c:142: if     ( scr.scroll == MAXSCROLL ) continue;  // Do not scroll passed the right limit
	ld	a, e
	sub	a, #0x50
	jr	Z,00109$
	jr	00107$
	jr	00109$
00106$:
;src/main.c:143: } else if ( scr.scroll ==         0 ) continue;  // Do not scroll passed the left limit
	ld	a, e
	or	a, a
	jr	Z,00109$
00107$:
;src/main.c:146: scrollScreenTilemap(&scr, scroll_offset);
	push	bc
	pop	iy
	push	hl
	push	bc
	ld	e,-7 (ix)
	ld	d,-6 (ix)
	push	de
	push	iy
	call	_scrollScreenTilemap
	pop	af
	pop	af
	pop	bc
	pop	hl
	jr	00109$
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
