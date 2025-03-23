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
	.globl _waitNVSYNCs
	.globl _initialization
	.globl _cpct_etm_setTileset2x4
	.globl _cpct_etm_drawTileBox2x4
	.globl _cpct_etm_drawTilemap2x4_f
	.globl _cpct_getScreenPtr
	.globl _cpct_setPALColour
	.globl _cpct_setPalette
	.globl _cpct_waitVSYNC
	.globl _cpct_setVideoMode
	.globl _cpct_drawSpriteMaskedAlignedTable
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
;src/main.c:26: cpctm_createTransparentMaskTable(g_masktable, 0x0100, M0, 0);
;	---------------------------------
; Function dummy_cpct_transparentMaskTable0M0_container
; ---------------------------------
_dummy_cpct_transparentMaskTable0M0_container::
	.area _g_masktable_ (ABS) 
	.org 0x0100 
	 _g_masktable::
	.db 0xFF, 0xAA, 0x55, 0x00, 0xAA, 0xAA, 0x00, 0x00 
	.db 0x55, 0x00, 0x55, 0x00, 0x00, 0x00, 0x00, 0x00 
	.db 0xAA, 0xAA, 0x00, 0x00, 0xAA, 0xAA, 0x00, 0x00 
	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
	.db 0x55, 0x00, 0x55, 0x00, 0x00, 0x00, 0x00, 0x00 
	.db 0x55, 0x00, 0x55, 0x00, 0x00, 0x00, 0x00, 0x00 
	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
	.db 0xAA, 0xAA, 0x00, 0x00, 0xAA, 0xAA, 0x00, 0x00 
	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
	.db 0xAA, 0xAA, 0x00, 0x00, 0xAA, 0xAA, 0x00, 0x00 
	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
	.db 0x55, 0x00, 0x55, 0x00, 0x00, 0x00, 0x00, 0x00 
	.db 0x55, 0x00, 0x55, 0x00, 0x00, 0x00, 0x00, 0x00 
	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
	.db 0x55, 0x00, 0x55, 0x00, 0x00, 0x00, 0x00, 0x00 
	.db 0x55, 0x00, 0x55, 0x00, 0x00, 0x00, 0x00, 0x00 
	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
	.area _CSEG (REL, CON) 
;src/main.c:51: void initialization (){ 
;	---------------------------------
; Function initialization
; ---------------------------------
_initialization::
;src/main.c:52: cpct_disableFirmware();          // Disable firmware to prevent it from interfering
	call	_cpct_disableFirmware
;src/main.c:53: cpct_setPalette(g_palette, 7);   // Set palette using hardware colour values
	ld	hl, #0x0007
	push	hl
	ld	hl, #_g_palette
	push	hl
	call	_cpct_setPalette
;src/main.c:54: cpct_setBorder (HW_BLACK);       // Set border colour same as background (Black)
	ld	hl, #0x1410
	push	hl
	call	_cpct_setPALColour
;src/main.c:55: cpct_setVideoMode(0);            // Change to Mode 0 (160x200, 16 colours)
	ld	l, #0x00
	call	_cpct_setVideoMode
;src/main.c:58: cpct_etm_setTileset2x4(g_tileset);
	ld	hl, #_g_tileset
	call	_cpct_etm_setTileset2x4
;src/main.c:62: CPCT_VMEM_START, g_background);  
;src/main.c:61: cpct_etm_drawTilemap2x4_f(MAP_WIDTH_TILES, MAP_HEIGHT_TILES, 
	ld	hl, #_g_background
	push	hl
	ld	hl, #0xc000
	push	hl
	ld	hl, #0x3228
	push	hl
	call	_cpct_etm_drawTilemap2x4_f
	ret
;src/main.c:68: void waitNVSYNCs(u8 n) {
;	---------------------------------
; Function waitNVSYNCs
; ---------------------------------
_waitNVSYNCs::
;src/main.c:69: do {
	ld	hl, #2+0
	add	hl, sp
	ld	c, (hl)
00103$:
;src/main.c:70: cpct_waitVSYNC();
	push	bc
	call	_cpct_waitVSYNC
	pop	bc
;src/main.c:71: if (--n) {
	dec	c
	ld	a, c
	or	a, a
	jr	Z,00104$
;src/main.c:72: __asm__ ("halt");
	halt
;src/main.c:73: __asm__ ("halt");
	halt
00104$:
;src/main.c:75: } while (n);
	ld	a, c
	or	a, a
	jr	NZ,00103$
	ret
;src/main.c:81: void main(void) {
;	---------------------------------
; Function main
; ---------------------------------
_main::
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	hl, #-8
	add	hl, sp
	ld	sp, hl
;src/main.c:84: TAlien* a = (void*)&sa;
	ld	bc, #_main_sa_1_135+0
	inc	sp
	inc	sp
	push	bc
;src/main.c:87: initialization();
	call	_initialization
;src/main.c:92: while(1) {
00116$:
;src/main.c:96: if (a->vx < 0) {
	ld	a, -8 (ix)
	add	a, #0x02
	ld	-2 (ix), a
	ld	a, -7 (ix)
	adc	a, #0x00
	ld	-1 (ix), a
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	ld	c, (hl)
;src/main.c:97: if (a->tx < -a->vx)
	pop	hl
	push	hl
	ld	b, (hl)
	ld	-4 (ix), c
	ld	a, c
	rla
	sbc	a, a
	ld	-3 (ix), a
	ld	-6 (ix), b
	ld	-5 (ix), #0x00
;src/main.c:96: if (a->vx < 0) {
	bit	7, c
	jr	Z,00106$
;src/main.c:97: if (a->tx < -a->vx)
	xor	a, a
	sub	a, -4 (ix)
	ld	c, a
	ld	a, #0x00
	sbc	a, -3 (ix)
	ld	b, a
	ld	a, -6 (ix)
	sub	a, c
	ld	a, -5 (ix)
	sbc	a, b
	jp	PO, 00148$
	xor	a, #0x80
00148$:
	jp	P, 00107$
;src/main.c:98: a->vx = 1;
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	ld	(hl), #0x01
	jr	00107$
00106$:
;src/main.c:99: } else if (a->tx + a->vx + ALIEN_WIDTH_TILES >= MAP_WIDTH_TILES)
	ld	a, -6 (ix)
	add	a, -4 (ix)
	ld	-6 (ix), a
	ld	a, -5 (ix)
	adc	a, -3 (ix)
	ld	-5 (ix), a
	ld	a, -6 (ix)
	add	a, #0x03
	ld	-6 (ix), a
	ld	a, -5 (ix)
	adc	a, #0x00
	ld	-5 (ix), a
	ld	a, -6 (ix)
	sub	a, #0x28
	ld	a, -5 (ix)
	rla
	ccf
	rra
	sbc	a, #0x80
	jr	C,00107$
;src/main.c:100: a->vx = -1;
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	ld	(hl), #0xff
00107$:
;src/main.c:102: if (a->vy < 0) {
	ld	a, -8 (ix)
	add	a, #0x03
	ld	-6 (ix), a
	ld	a, -7 (ix)
	adc	a, #0x00
	ld	-5 (ix), a
	ld	l,-6 (ix)
	ld	h,-5 (ix)
	ld	c, (hl)
;src/main.c:103: if (a->ty < -a->vy)
	pop	de
	push	de
	inc	de
	ld	-4 (ix), c
	ld	a, c
	rla
	sbc	a, a
	ld	-3 (ix), a
;src/main.c:113: cpct_etm_drawTileBox2x4(a->tx, a->ty, ALIEN_WIDTH_TILES, ALIEN_HEIGHT_TILES, 
	ld	a, (de)
	ld	l, a
;src/main.c:103: if (a->ty < -a->vy)
	ld	h, #0x00
;src/main.c:102: if (a->vy < 0) {
	bit	7, c
	jr	Z,00113$
;src/main.c:103: if (a->ty < -a->vy)
	xor	a, a
	sub	a, -4 (ix)
	ld	c, a
	ld	a, #0x00
	sbc	a, -3 (ix)
	ld	b, a
	ld	a, l
	sub	a, c
	ld	a, h
	sbc	a, b
	jp	PO, 00149$
	xor	a, #0x80
00149$:
	jp	P, 00114$
;src/main.c:104: a->vy = 1;
	ld	l,-6 (ix)
	ld	h,-5 (ix)
	ld	(hl), #0x01
	jr	00114$
00113$:
;src/main.c:105: } else if (a->ty + a->vy + ALIEN_HEIGHT_TILES >= MAP_HEIGHT_TILES)
	ld	c,-4 (ix)
	ld	b,-3 (ix)
	add	hl, bc
	ld	bc, #0x0006
	add	hl, bc
	ld	bc, #0x8032
	add	hl, hl
	ccf
	rr	h
	rr	l
	sbc	hl, bc
	jr	C,00114$
;src/main.c:106: a->vy = -1;
	ld	l,-6 (ix)
	ld	h,-5 (ix)
	ld	(hl), #0xff
00114$:
;src/main.c:110: waitNVSYNCs(2);
	push	de
	ld	a, #0x02
	push	af
	inc	sp
	call	_waitNVSYNCs
	inc	sp
	pop	de
;src/main.c:114: MAP_WIDTH_TILES, CPCT_VMEM_START, g_background);
;src/main.c:113: cpct_etm_drawTileBox2x4(a->tx, a->ty, ALIEN_WIDTH_TILES, ALIEN_HEIGHT_TILES, 
	ld	a, (de)
	ld	c, a
	pop	hl
	push	hl
	ld	b, (hl)
	push	de
	ld	hl, #_g_background
	push	hl
	ld	hl, #0xc000
	push	hl
	ld	hl, #0x2806
	push	hl
	ld	a, #0x03
	push	af
	inc	sp
	ld	a, c
	push	af
	inc	sp
	push	bc
	inc	sp
	call	_cpct_etm_drawTileBox2x4
	pop	de
;src/main.c:116: a->tx += a->vx; 
	pop	hl
	push	hl
	ld	c, (hl)
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	ld	b, (hl)
	ld	a, c
	add	a, b
	pop	hl
	push	hl
	ld	(hl), a
;src/main.c:117: a->ty += a->vy;
	ld	a, (de)
	ld	c, a
	ld	l,-6 (ix)
	ld	h,-5 (ix)
	ld	b, (hl)
	ld	a, c
	add	a, b
	ld	(de), a
;src/main.c:118: pscra = cpct_getScreenPtr(CPCT_VMEM_START, TILEWIDTH_BYTES*a->tx, TILEHEIGHT_BYTES*a->ty);
	ld	a, (de)
	add	a, a
	add	a, a
	ld	b, a
	pop	hl
	push	hl
	ld	d, (hl)
	sla	d
	ld	c, d
	push	bc
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
;src/main.c:121: ALIEN_HEIGHT_BYTES, g_masktable);
	ld	bc, #_g_masktable+0
;src/main.c:120: cpct_drawSpriteMaskedAlignedTable(g_alien, pscra, ALIEN_WIDTH_BYTES, 
	ld	de, #_g_alien+0
	push	bc
	ld	bc, #0x1806
	push	bc
	push	hl
	push	de
	call	_cpct_drawSpriteMaskedAlignedTable
	jp	00116$
_main_sa_1_135:
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x01	;  1
	.db #0x01	;  1
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
