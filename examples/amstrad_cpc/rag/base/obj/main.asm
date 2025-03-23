;--------------------------------------------------------
; File Created by SDCC : free open source ISO C Compiler
; Version 4.5.0 #15242 (Linux)
;--------------------------------------------------------
	.module main
	
	.optsdcc -mz80 sdcccall(1)
;--------------------------------------------------------
; Public variables in this module
;--------------------------------------------------------
	.globl _main
	.globl _initialize_cpc
	.globl _cpct_setVideoMode
	.globl _cpct_setDrawCharM0
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
;src/main.c:6: void initialize_cpc()
;	---------------------------------
; Function initialize_cpc
; ---------------------------------
_initialize_cpc::
;src/main.c:8: cpct_disableFirmware();   // Disable firmware to prevent it from interfering with setPalette and setVideoMode
	call	_cpct_disableFirmware
;src/main.c:9: cpct_setVideoMode(0);     // Set video mode 0 (160x200, 16 colours)
	ld	l, #0x00
	call	_cpct_setVideoMode
;src/main.c:10: cpct_setDrawCharM0(3, 0); // Set PEN 3, PAPER 0 for Characters to be drawn using cpct_drawCharM0
	ld	l, #0x00
	ld	a, #0x03
;src/main.c:11: }
	jp	_cpct_setDrawCharM0
;src/main.c:16: void main(void)
;	---------------------------------
; Function main
; ---------------------------------
_main::
;src/main.c:18: initialize_cpc(); // Initialize the CPC
	call	_initialize_cpc
;src/main.c:23: while (1)
00102$:
;src/main.c:26: }
	jr	00102$
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
