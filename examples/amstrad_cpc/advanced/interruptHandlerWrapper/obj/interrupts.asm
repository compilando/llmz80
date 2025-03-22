;--------------------------------------------------------
; File Created by SDCC : free open source ANSI-C Compiler
; Version 3.6.8 #9946 (Linux)
;--------------------------------------------------------
	.module interrupts
	.optsdcc -mz80
	
;--------------------------------------------------------
; Public variables in this module
;--------------------------------------------------------
	.globl _dummy_MyInterruptWrapper
	.globl _myInterruptHandler
	.globl _cpct_setPALColour
;--------------------------------------------------------
; special function registers
;--------------------------------------------------------
;--------------------------------------------------------
; ram data
;--------------------------------------------------------
	.area _DATA
_myInterruptHandler_i_1_128:
	.ds 1
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
;src/interrupts.c:27: void myInterruptHandler() {
;	---------------------------------
; Function myInterruptHandler
; ---------------------------------
_myInterruptHandler::
;src/interrupts.c:29: cpct_setBorder(i+1);    // Set the color of the border differently for each interrupt  
	ld	hl,#_myInterruptHandler_i_1_128 + 0
	ld	b, (hl)
	inc	b
	push	bc
	inc	sp
	ld	a, #0x10
	push	af
	inc	sp
	call	_cpct_setPALColour
;src/interrupts.c:30: if (++i > 5) i=0;       // Count one more interrupt. There are 6 interrupts in total (0-5)
	ld	iy, #_myInterruptHandler_i_1_128
	inc	0 (iy)
	ld	a, #0x05
	sub	a, 0 (iy)
	ret	NC
	ld	0 (iy), #0x00
	ret
;src/interrupts.c:41: cpctm_createInterruptHandlerWrapper(MyInterruptWrapper, myInterruptHandler, af, bc, de, hl, ix, iy, alt, af, hl);
;	---------------------------------
; Function dummy_MyInterruptWrapper
; ---------------------------------
_dummy_MyInterruptWrapper::
	.include "firmware/cpctm_createInterruptHandlerWrapper.asm" 
	cpctm_createInterruptHandlerWrapper_asm MyInterruptWrapper, _myInterruptHandler, af, bc, de, hl, ix, iy, alt, af, hl 
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
