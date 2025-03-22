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
	.globl _MyInterruptWrapper
	.globl _cpct_drawStringM1
	.globl _cpct_setDrawCharM1
	.globl _cpct_setInterruptHandler_naked
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
;src/main.c:26: void main(void) {
;	---------------------------------
; Function main
; ---------------------------------
_main::
;src/main.c:33: cpct_setInterruptHandler_naked(MyInterruptWrapper);
	ld	hl, #_MyInterruptWrapper
	call	_cpct_setInterruptHandler_naked
;src/main.c:39: cpct_setDrawCharM1(1, 0);
	ld	hl, #0x0001
	push	hl
	call	_cpct_setDrawCharM1
;src/main.c:42: cpct_drawStringM1("Interrupt Handler Wrapper Example", location);
	ld	hl, #0xc3c6
	push	hl
	ld	hl, #___str_0
	push	hl
	call	_cpct_drawStringM1
;src/main.c:47: while (1);
00102$:
	jr	00102$
___str_0:
	.ascii "Interrupt Handler Wrapper Example"
	.db 0x00
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
