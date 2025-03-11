;--------------------------------------------------------
; File Created by SDCC : free open source ANSI-C Compiler
; Version 3.6.8 #9946 (Linux)
;--------------------------------------------------------
	.module 02_print
	.optsdcc -mz80
	
;--------------------------------------------------------
; Public variables in this module
;--------------------------------------------------------
	.globl _main
	.globl _cpct_setPALColour
	.globl _cpct_setVideoMode
	.globl _cpct_drawStringM1
	.globl _cpct_setDrawCharM1
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
;02_print.c:8: void main(void)
;	---------------------------------
; Function main
; ---------------------------------
_main::
;02_print.c:11: cpct_disableFirmware();
	call	_cpct_disableFirmware
;02_print.c:14: cpct_setVideoMode(1);
	ld	l, #0x01
	call	_cpct_setVideoMode
;02_print.c:17: cpct_setBorder(1);
	ld	hl, #0x0110
	push	hl
	call	_cpct_setPALColour
;02_print.c:20: cpct_setDrawCharM1(3, 0); // Tinta blanca (3) sobre fondo negro (0)
	ld	hl, #0x0003
	push	hl
	call	_cpct_setDrawCharM1
;02_print.c:23: cpct_drawStringM1("Hola Mundo en Amstrad CPC!", (u8 *)0xC000);
	ld	hl, #0xc000
	push	hl
	ld	hl, #___str_0
	push	hl
	call	_cpct_drawStringM1
;02_print.c:24: cpct_drawStringM1("Usando CPCtelera", (u8 *)0xC050);
	ld	hl, #0xc050
	push	hl
	ld	hl, #___str_1
	push	hl
	call	_cpct_drawStringM1
;02_print.c:25: cpct_drawStringM1("Generado con LLM", (u8 *)0xC0A0);
	ld	hl, #0xc0a0
	push	hl
	ld	hl, #___str_2
	push	hl
	call	_cpct_drawStringM1
;02_print.c:28: while (1)
00102$:
	jr	00102$
___str_0:
	.ascii "Hola Mundo en Amstrad CPC!"
	.db 0x00
___str_1:
	.ascii "Usando CPCtelera"
	.db 0x00
___str_2:
	.ascii "Generado con LLM"
	.db 0x00
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
