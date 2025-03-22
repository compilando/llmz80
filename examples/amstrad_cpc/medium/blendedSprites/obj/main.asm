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
	.globl _performUserActions
	.globl _selectNextBlendMode
	.globl _selectNextItem
	.globl _updateKeyboardStatus
	.globl _drawUserInterfaceMessages
	.globl _drawUserInterfaceStatus
	.globl _drawBackground
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
;src/main.c:28: void selectNextItem() {
;	---------------------------------
; Function selectNextItem
; ---------------------------------
_selectNextItem::
;src/main.c:31: if (++g_selectedItem >= G_NITEMS)
	ld	iy, #_g_selectedItem
	inc	0 (iy)
	ld	a, 0 (iy)
	sub	a, #0x04
	jp	C,_drawUserInterfaceStatus
;src/main.c:32: g_selectedItem = 0;
	ld	0 (iy), #0x00
;src/main.c:35: drawUserInterfaceStatus();
	jp  _drawUserInterfaceStatus
;src/main.c:42: void selectNextBlendMode() {
;	---------------------------------
; Function selectNextBlendMode
; ---------------------------------
_selectNextBlendMode::
;src/main.c:45: if (++g_selectedBlendMode >= G_NBLENDMODES) 
	ld	iy, #_g_selectedBlendMode
	inc	0 (iy)
	ld	a, 0 (iy)
	sub	a, #0x09
	jp	C,_drawUserInterfaceStatus
;src/main.c:46: g_selectedBlendMode = 0;
	ld	0 (iy), #0x00
;src/main.c:49: drawUserInterfaceStatus();
	jp  _drawUserInterfaceStatus
;src/main.c:56: void performUserActions() {
;	---------------------------------
; Function performUserActions
; ---------------------------------
_performUserActions::
;src/main.c:63: for(i = 0; i < G_NKEYS; i++) {
	ld	de, #_g_keys+0
	ld	c, #0x00
00104$:
;src/main.c:64: if (g_keys[i].status == KeySt_Pressed)
	ld	b,#0x00
	ld	l, c
	ld	h, b
	add	hl, hl
	add	hl, hl
	add	hl, bc
	add	hl, de
	push	hl
	pop	iy
	push	iy
	pop	hl
	inc	hl
	inc	hl
	ld	b, (hl)
	djnz	00105$
;src/main.c:65: g_keys[i].action();
	ld	l, 3 (iy)
	ld	h, 4 (iy)
	push	bc
	push	de
	call	___sdcc_call_hl
	pop	de
	pop	bc
00105$:
;src/main.c:63: for(i = 0; i < G_NKEYS; i++) {
	inc	c
	ld	a, c
	sub	a, #0x04
	jr	C,00104$
	ret
;src/main.c:73: void initialize (){ 
;	---------------------------------
; Function initialize
; ---------------------------------
_initialize::
;src/main.c:75: cpct_disableFirmware();
	call	_cpct_disableFirmware
;src/main.c:80: cpct_setPalette  (g_palette, G_NCOLOURS);
	ld	hl, #0x000b
	push	hl
	ld	hl, #_g_palette
	push	hl
	call	_cpct_setPalette
;src/main.c:81: cpct_setBorder   (HW_BLACK);
	ld	hl, #0x1410
	push	hl
	call	_cpct_setPALColour
;src/main.c:82: cpct_setVideoMode(0);
	ld	l, #0x00
	call	_cpct_setVideoMode
;src/main.c:85: drawUserInterfaceMessages();   
	call	_drawUserInterfaceMessages
;src/main.c:86: drawBackground();
	call	_drawBackground
;src/main.c:89: g_selectedItem      = 0;
	ld	hl,#_g_selectedItem + 0
	ld	(hl), #0x00
;src/main.c:90: g_selectedBlendMode = 0;
	ld	hl,#_g_selectedBlendMode + 0
	ld	(hl), #0x00
;src/main.c:91: drawUserInterfaceStatus();
	call	_drawUserInterfaceStatus
	ret
;src/main.c:97: void main(void) {
;	---------------------------------
; Function main
; ---------------------------------
_main::
;src/main.c:98: initialize();  // Initialize the Amstrad CPC, 
	call	_initialize
;src/main.c:102: while(1) {
00102$:
;src/main.c:103: updateKeyboardStatus();
	call	_updateKeyboardStatus
;src/main.c:104: performUserActions();
	call	_performUserActions
	jr	00102$
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
