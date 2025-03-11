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
	.globl _initialize
	.globl _cpct_etm_drawTilemap4x8_ag
	.globl _cpct_etm_setDrawTilemap4x8_ag
	.globl _cpct_setPALColour
	.globl _cpct_setPalette
	.globl _cpct_setVideoMode
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
;src/main.c:79: void initialize() {
;	---------------------------------
; Function initialize
; ---------------------------------
_initialize::
;src/main.c:82: cpct_disableFirmware();          // Disable firmware 
	call	_cpct_disableFirmware
;src/main.c:83: cpct_setVideoMode(0);            // Set Video Mode 0 (160x200, 16 colours)
	ld	l, #0x00
	call	_cpct_setVideoMode
;src/main.c:84: cpct_setPalette(g_palette, 16);  // Set palette colours (g_palette is generated in tiles.c)
	ld	hl, #0x0010
	push	hl
	ld	hl, #_g_palette
	push	hl
	call	_cpct_setPalette
;src/main.c:85: cpct_setBorder(HW_BLACK);        // Set border colour to black
	ld	hl, #0x1410
	push	hl
	call	_cpct_setPALColour
	ret
;src/main.c:92: void main(void) {
;	---------------------------------
; Function main
; ---------------------------------
_main::
;src/main.c:93: initialize();  // Initialize the CPC
	call	_initialize
;src/main.c:103: cpct_etm_setDrawTilemap4x8_ag(g_courtMap_W, g_courtMap_H, g_courtMap_W, g_tiles_00);
	ld	hl, #_g_tiles_00
	push	hl
	ld	hl, #0x0012
	push	hl
	ld	h, #0x16
	push	hl
	call	_cpct_etm_setDrawTilemap4x8_ag
;src/main.c:111: cpct_etm_drawTilemap4x8_ag(TILEMAP_VMEM, g_courtMap);
	ld	hl, #_g_courtMap
	push	hl
	ld	hl, #0xc0a4
	push	hl
	call	_cpct_etm_drawTilemap4x8_ag
;src/main.c:114: while (1);
00102$:
	jr	00102$
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
