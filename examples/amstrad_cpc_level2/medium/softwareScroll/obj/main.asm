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
	.globl _game
	.globl _initialize
	.globl _drawFrame
	.globl _drawBuidlingScrolled
	.globl _video_switchBuffers
	.globl _video_initBuffers
	.globl _video_getBackBufferPtr
	.globl _cpct_etm_drawTilemap4x8_ag
	.globl _cpct_etm_setDrawTilemap4x8_ag
	.globl _cpct_getScreenPtr
	.globl _cpct_setPALColour
	.globl _cpct_setPalette
	.globl _cpct_setVideoMode
	.globl _cpct_isKeyPressed
	.globl _cpct_scanKeyboard_f
	.globl _cpct_setStackLocation
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
;src/main.c:79: void drawBuidlingScrolled(u16 offset) {
;	---------------------------------
; Function drawBuidlingScrolled
; ---------------------------------
_drawBuidlingScrolled::
	push	ix
	ld	ix,#0
	add	ix,sp
;src/main.c:84: u8* vmem = video_getBackBufferPtr() + VIEWPORT_OFFSET;
	call	_video_getBackBufferPtr
	ld	bc, #0x0148
	add	hl, bc
;src/main.c:89: cpct_etm_drawTilemap4x8_ag(vmem, g_building + offset);
	ld	bc, #_g_building+0
	ld	a, 4 (ix)
	add	a, c
	ld	c, a
	ld	a, 5 (ix)
	adc	a, b
	ld	b, a
	push	bc
	push	hl
	call	_cpct_etm_drawTilemap4x8_ag
;src/main.c:92: video_switchBuffers();
	call	_video_switchBuffers
	pop	ix
	ret
;src/main.c:101: void drawFrame() {
;	---------------------------------
; Function drawFrame
; ---------------------------------
_drawFrame::
;src/main.c:103: u8* vmem_buffer = video_getBackBufferPtr();  // Get present Hardware Back Buffer were we are going to draw
	call	_video_getBackBufferPtr
;src/main.c:114: cpct_etm_setDrawTilemap4x8_ag (20, 4, g_frame_ud_W, g_tileset_00);
	push	hl
	ld	hl, #_g_tileset_00
	push	hl
	ld	hl, #0x0015
	push	hl
	ld	hl, #0x0414
	push	hl
	call	_cpct_etm_setDrawTilemap4x8_ag
	pop	bc
;src/main.c:116: cpct_etm_drawTilemap4x8_ag    (vmem_buffer, g_frame_ud);
	ld	de, #_g_frame_ud
	push	bc
	push	de
	push	bc
	call	_cpct_etm_drawTilemap4x8_ag
	pop	bc
;src/main.c:123: vmem = cpct_getScreenPtr   (vmem_buffer,  0*TILE_W, 20*TILE_H);
	push	bc
	ld	hl, #0xa000
	push	hl
	push	bc
	call	_cpct_getScreenPtr
	pop	bc
;src/main.c:126: cpct_etm_drawTilemap4x8_ag (vmem, g_frame_ud + 1);
	ld	de, #_g_frame_ud + 1
	push	bc
	push	de
	push	hl
	call	_cpct_etm_drawTilemap4x8_ag
	ld	hl, #_g_tileset_00
	push	hl
	ld	hl, #0x0004
	push	hl
	ld	hl, #0x1002
	push	hl
	call	_cpct_etm_setDrawTilemap4x8_ag
	pop	bc
;src/main.c:141: vmem = cpct_getScreenPtr   (vmem_buffer,  0*TILE_W, 4*TILE_H);
	push	bc
	ld	hl, #0x2000
	push	hl
	push	bc
	call	_cpct_getScreenPtr
	ex	de,hl
	pop	bc
;src/main.c:142: cpct_etm_drawTilemap4x8_ag (vmem, g_frame_lr);   
	ld	hl, #_g_frame_lr
	push	bc
	push	hl
	push	de
	call	_cpct_etm_drawTilemap4x8_ag
	pop	bc
;src/main.c:145: vmem = cpct_getScreenPtr   (vmem_buffer, 18*TILE_W, 4*TILE_H);
	ld	hl, #0x2048
	push	hl
	push	bc
	call	_cpct_getScreenPtr
;src/main.c:146: cpct_etm_drawTilemap4x8_ag (vmem, g_frame_lr + 2);
	ld	bc, #_g_frame_lr + 2
	push	bc
	push	hl
	call	_cpct_etm_drawTilemap4x8_ag
	ret
;src/main.c:154: void initialize() {
;	---------------------------------
; Function initialize
; ---------------------------------
_initialize::
;src/main.c:155: cpct_disableFirmware();          // We use own mode and colours, firmware must be disabled
	call	_cpct_disableFirmware
;src/main.c:156: cpct_setVideoMode(0);            // Set video mode 0 (160x200 pixels, 20x25 characters, 16 colours)
	ld	l, #0x00
	call	_cpct_setVideoMode
;src/main.c:157: cpct_setPalette(g_palette, 16);  // Set our own colours defined en g_palette (automatically generated in maps/tileset.c)
	ld	hl, #0x0010
	push	hl
	ld	hl, #_g_palette
	push	hl
	call	_cpct_setPalette
;src/main.c:158: cpct_setBorder(HW_BLUE);         // Set border same as background colour: BLUE
	ld	hl, #0x0410
	push	hl
	call	_cpct_setPALColour
;src/main.c:164: video_initBuffers();    // Initialize screen video buffers
	call	_video_initBuffers
;src/main.c:165: drawFrame();            // Draw a frame at the first selected screen buffer
	call	_drawFrame
;src/main.c:166: video_switchBuffers();  // Switch video buffers (current screen <--> current backbuffer)
	call	_video_switchBuffers
;src/main.c:167: drawFrame();            // Draw the same frame at the second screen buffer
	call	_drawFrame
;src/main.c:173: cpct_etm_setDrawTilemap4x8_ag(VIEWPORT_W, VIEWPORT_H, g_building_W, g_tileset_00);
	ld	hl, #_g_tileset_00
	push	hl
	ld	hl, #0x0020
	push	hl
	ld	hl, #0x1010
	push	hl
	call	_cpct_etm_setDrawTilemap4x8_ag
	ret
;src/main.c:181: void game() {
;	---------------------------------
; Function game
; ---------------------------------
_game::
;src/main.c:182: u16 offset=0;  // Offset in tiles of the start of the view window in the g_building tilemap
	ld	bc, #0x0000
;src/main.c:183: u8  x=0, y=0;  // (x, y) coordinates of the start of the view window in the g_building tilemap
	ld	de,#0x0000
;src/main.c:186: while (1) {
00114$:
;src/main.c:189: drawBuidlingScrolled(offset);
	push	bc
	push	de
	push	bc
	call	_drawBuidlingScrolled
	pop	af
	call	_cpct_scanKeyboard_f
	ld	hl, #0x0404
	call	_cpct_isKeyPressed
	pop	de
	pop	bc
	ld	a, l
	or	a, a
	jr	Z,00102$
	ld	a, e
	or	a, a
	jr	Z,00102$
	dec	e
	dec	bc
00102$:
;src/main.c:205: if (cpct_isKeyPressed(Key_P) && x < g_building_W - VIEWPORT_W) { ++x; ++offset; }
	push	bc
	push	de
	ld	hl, #0x0803
	call	_cpct_isKeyPressed
	pop	de
	pop	bc
	ld	a, l
	or	a, a
	jr	Z,00105$
	ld	a, e
	sub	a, #0x10
	jr	NC,00105$
	inc	e
	inc	bc
00105$:
;src/main.c:206: if (cpct_isKeyPressed(Key_Q) && y > 0)                         { --y; offset -= g_building_W; }
	push	bc
	push	de
	ld	hl, #0x0808
	call	_cpct_isKeyPressed
	pop	de
	pop	bc
	ld	a, l
	or	a, a
	jr	Z,00108$
	ld	a, d
	or	a, a
	jr	Z,00108$
	dec	d
	ld	a, c
	add	a, #0xe0
	ld	c, a
	ld	a, b
	adc	a, #0xff
	ld	b, a
00108$:
;src/main.c:207: if (cpct_isKeyPressed(Key_A) && y < g_building_H - VIEWPORT_H) { ++y; offset += g_building_W; }
	push	bc
	push	de
	ld	hl, #0x2008
	call	_cpct_isKeyPressed
	pop	de
	pop	bc
	ld	a, l
	or	a, a
	jr	Z,00114$
	ld	a, d
	sub	a, #0x10
	jr	NC,00114$
	inc	d
	ld	hl, #0x0020
	add	hl,bc
	ld	c, l
	ld	b, h
	jr	00114$
;src/main.c:215: void main(void) {
;	---------------------------------
; Function main
; ---------------------------------
_main::
;src/main.c:221: cpct_setStackLocation((void*)0x8000);
	ld	hl, #0x8000
	call	_cpct_setStackLocation
;src/main.c:224: initialize();
	call	_initialize
;src/main.c:225: game();
	jp  _game
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
