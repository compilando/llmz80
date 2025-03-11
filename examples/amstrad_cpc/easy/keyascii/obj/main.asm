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
	.globl _initialize_cpc
	.globl _cpct_setVideoMode
	.globl _cpct_drawCharM0
	.globl _cpct_setDrawCharM0
	.globl _cpct_getKeypressedAsASCII
	.globl _cpct_scanKeyboard_f
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
;src/main.c:23: void initialize_cpc() {
;	---------------------------------
; Function initialize_cpc
; ---------------------------------
_initialize_cpc::
;src/main.c:24: cpct_disableFirmware();    // Disable firmware to prevent it from interfering with setPalette and setVideoMode
	call	_cpct_disableFirmware
;src/main.c:25: cpct_setVideoMode(0);      // Set video mode 0 (160x200, 16 colours)
	ld	l, #0x00
	call	_cpct_setVideoMode
;src/main.c:26: cpct_setDrawCharM0(3, 0);  // Set PEN 3, PAPER 0 for Characters to be drawn using cpct_drawCharM0
	ld	hl, #0x0003
	push	hl
	call	_cpct_setDrawCharM0
	ret
;src/main.c:32: void main(void) {
;	---------------------------------
; Function main
; ---------------------------------
_main::
;src/main.c:33: initialize_cpc();    // Initialize the CPC
	call	_initialize_cpc
;src/main.c:38: while(1) {
00104$:
;src/main.c:44: cpct_scanKeyboard_f();
	call	_cpct_scanKeyboard_f
;src/main.c:47: ascii = cpct_getKeypressedAsASCII();
	call	_cpct_getKeypressedAsASCII
;src/main.c:48: if (ascii != 0) {                            // ascii == 0 means no key is pressed, so we check first
	ld	a,l
	ld	c,a
	or	a, a
	jr	Z,00104$
;src/main.c:49: cpct_drawCharM0(CPCT_VMEM_START, ascii);  // Some key is pressed, print its ascii value to the screen
	ld	b, #0x00
	push	bc
	ld	hl, #0xc000
	push	hl
	call	_cpct_drawCharM0
	jr	00104$
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
