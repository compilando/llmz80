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
	.globl _Initialization
	.globl _CheckUserInput
	.globl _ScrollAndDrawSpace
	.globl _SelectDrawFunction
	.globl _InitializeDrawing
	.globl _DrawTextSelectionSign
	.globl _DrawInfoText
	.globl _InitializeVideoMemoryBuffers
	.globl _cpct_setPalette
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
;src/main.c:24: cpctm_createTransparentMaskTable(gMaskTable, MASK_TABLE_LOCATION, M1, 0);
;	---------------------------------
; Function dummy_cpct_transparentMaskTable0M1_container
; ---------------------------------
_dummy_cpct_transparentMaskTable0M1_container::
	.area _gMaskTable_ (ABS) 
	.org (0x8000 - 0x100) 
	 _gMaskTable::
	.db 0xFF, 0xEE, 0xDD, 0xCC, 0xBB, 0xAA, 0x99, 0x88 
	.db 0x77, 0x66, 0x55, 0x44, 0x33, 0x22, 0x11, 0x00 
	.db 0xEE, 0xEE, 0xCC, 0xCC, 0xAA, 0xAA, 0x88, 0x88 
	.db 0x66, 0x66, 0x44, 0x44, 0x22, 0x22, 0x00, 0x00 
	.db 0xDD, 0xCC, 0xDD, 0xCC, 0x99, 0x88, 0x99, 0x88 
	.db 0x55, 0x44, 0x55, 0x44, 0x11, 0x00, 0x11, 0x00 
	.db 0xCC, 0xCC, 0xCC, 0xCC, 0x88, 0x88, 0x88, 0x88 
	.db 0x44, 0x44, 0x44, 0x44, 0x00, 0x00, 0x00, 0x00 
	.db 0xBB, 0xAA, 0x99, 0x88, 0xBB, 0xAA, 0x99, 0x88 
	.db 0x33, 0x22, 0x11, 0x00, 0x33, 0x22, 0x11, 0x00 
	.db 0xAA, 0xAA, 0x88, 0x88, 0xAA, 0xAA, 0x88, 0x88 
	.db 0x22, 0x22, 0x00, 0x00, 0x22, 0x22, 0x00, 0x00 
	.db 0x99, 0x88, 0x99, 0x88, 0x99, 0x88, 0x99, 0x88 
	.db 0x11, 0x00, 0x11, 0x00, 0x11, 0x00, 0x11, 0x00 
	.db 0x88, 0x88, 0x88, 0x88, 0x88, 0x88, 0x88, 0x88 
	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
	.db 0x77, 0x66, 0x55, 0x44, 0x33, 0x22, 0x11, 0x00 
	.db 0x77, 0x66, 0x55, 0x44, 0x33, 0x22, 0x11, 0x00 
	.db 0x66, 0x66, 0x44, 0x44, 0x22, 0x22, 0x00, 0x00 
	.db 0x66, 0x66, 0x44, 0x44, 0x22, 0x22, 0x00, 0x00 
	.db 0x55, 0x44, 0x55, 0x44, 0x11, 0x00, 0x11, 0x00 
	.db 0x55, 0x44, 0x55, 0x44, 0x11, 0x00, 0x11, 0x00 
	.db 0x44, 0x44, 0x44, 0x44, 0x00, 0x00, 0x00, 0x00 
	.db 0x44, 0x44, 0x44, 0x44, 0x00, 0x00, 0x00, 0x00 
	.db 0x33, 0x22, 0x11, 0x00, 0x33, 0x22, 0x11, 0x00 
	.db 0x33, 0x22, 0x11, 0x00, 0x33, 0x22, 0x11, 0x00 
	.db 0x22, 0x22, 0x00, 0x00, 0x22, 0x22, 0x00, 0x00 
	.db 0x22, 0x22, 0x00, 0x00, 0x22, 0x22, 0x00, 0x00 
	.db 0x11, 0x00, 0x11, 0x00, 0x11, 0x00, 0x11, 0x00 
	.db 0x11, 0x00, 0x11, 0x00, 0x11, 0x00, 0x11, 0x00 
	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
	.area _CSEG (REL, CON) 
;src/main.c:31: void CheckUserInput() {
;	---------------------------------
; Function CheckUserInput
; ---------------------------------
_CheckUserInput::
;src/main.c:32: cpct_scanKeyboard_f();
	call	_cpct_scanKeyboard_f
;src/main.c:34: if       (cpct_isKeyPressed(Key_1)) { SelectDrawFunction(1); DrawTextSelectionSign(1); }
	ld	hl, #0x0108
	call	_cpct_isKeyPressed
	ld	a, l
	or	a, a
	jr	Z,00107$
	ld	a, #0x01
	push	af
	inc	sp
	call	_SelectDrawFunction
	inc	sp
	ld	a, #0x01
	push	af
	inc	sp
	call	_DrawTextSelectionSign
	inc	sp
	ret
00107$:
;src/main.c:35: else if  (cpct_isKeyPressed(Key_2)) { SelectDrawFunction(2); DrawTextSelectionSign(2); }
	ld	hl, #0x0208
	call	_cpct_isKeyPressed
	ld	a, l
	or	a, a
	jr	Z,00104$
	ld	a, #0x02
	push	af
	inc	sp
	call	_SelectDrawFunction
	inc	sp
	ld	a, #0x02
	push	af
	inc	sp
	call	_DrawTextSelectionSign
	inc	sp
	ret
00104$:
;src/main.c:36: else if  (cpct_isKeyPressed(Key_3)) { SelectDrawFunction(3); DrawTextSelectionSign(3); }
	ld	hl, #0x0207
	call	_cpct_isKeyPressed
	ld	a, l
	or	a, a
	ret	Z
	ld	a, #0x03
	push	af
	inc	sp
	call	_SelectDrawFunction
	inc	sp
	ld	a, #0x03
	push	af
	inc	sp
	call	_DrawTextSelectionSign
	inc	sp
	ret
;src/main.c:44: void Initialization() {
;	---------------------------------
; Function Initialization
; ---------------------------------
_Initialization::
;src/main.c:47: cpct_disableFirmware(); 
	call	_cpct_disableFirmware
;src/main.c:48: cpct_setPalette(g_palette, 5);   // Set the palette
	ld	hl, #0x0005
	push	hl
	ld	hl, #_g_palette
	push	hl
	call	_cpct_setPalette
;src/main.c:49: InitializeVideoMemoryBuffers();  // Initialize video buffers
	call	_InitializeVideoMemoryBuffers
;src/main.c:50: InitializeDrawing();             // Initialize Drawing Module
	call	_InitializeDrawing
;src/main.c:51: SelectDrawFunction(1);           // Select the 1st Drawing function
	ld	a, #0x01
	push	af
	inc	sp
	call	_SelectDrawFunction
	inc	sp
;src/main.c:52: DrawTextSelectionSign(1);        // Mark 1st Drawing function as Selected
	ld	a, #0x01
	push	af
	inc	sp
	call	_DrawTextSelectionSign
	inc	sp
;src/main.c:53: DrawInfoText();                  // Draw User Info Text 
	call	_DrawInfoText
	ret
;src/main.c:59: void main(void) {
;	---------------------------------
; Function main
; ---------------------------------
_main::
;src/main.c:63: cpct_setStackLocation((u8*)NEW_STACK_LOCATION);
	ld	hl, #0x7e00
	call	_cpct_setStackLocation
;src/main.c:66: Initialization();
	call	_Initialization
;src/main.c:69: while(1) {
00102$:
;src/main.c:70: CheckUserInput();
	call	_CheckUserInput
;src/main.c:71: ScrollAndDrawSpace();
	call	_ScrollAndDrawSpace
	jr	00102$
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
