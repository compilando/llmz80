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
	.globl _printMessages
	.globl _myInterruptHandler
	.globl _cpct_setPALColour
	.globl _cpct_drawStringM1
	.globl _cpct_setDrawCharM1
	.globl _cpct_setInterruptHandler
	.globl _cpct_disableFirmware
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
;src/main.c:30: void myInterruptHandler() {
;	---------------------------------
; Function myInterruptHandler
; ---------------------------------
_myInterruptHandler::
;src/main.c:34: cpct_setBorder(i+1);
	ld	hl,#_myInterruptHandler_i_1_128 + 0
	ld	b, (hl)
	inc	b
	push	bc
	inc	sp
	ld	a, #0x10
	push	af
	inc	sp
	call	_cpct_setPALColour
;src/main.c:37: if (++i > 5) i=0;
	ld	iy, #_myInterruptHandler_i_1_128
	inc	0 (iy)
	ld	a, #0x05
	sub	a, 0 (iy)
	ret	NC
	ld	0 (iy), #0x00
	ret
;src/main.c:43: void printMessages() {
;	---------------------------------
; Function printMessages
; ---------------------------------
_printMessages::
;src/main.c:45: cpct_setDrawCharM1(0, 3);
	ld	hl, #0x0300
	push	hl
	call	_cpct_setDrawCharM1
;src/main.c:46: cpct_drawStringM1("Interrupt Handler Example", pvm);
	ld	hl, #0xc000
	push	hl
	ld	hl, #___str_0
	push	hl
	call	_cpct_drawStringM1
;src/main.c:49: cpct_setDrawCharM1(1, 0);
	ld	hl, #0x0001
	push	hl
	call	_cpct_setDrawCharM1
;src/main.c:50: cpct_drawStringM1("This example is running a void loop, but", pvm);
	ld	hl, #0xc0f0
	push	hl
	ld	hl, #___str_1
	push	hl
	call	_cpct_drawStringM1
;src/main.c:52: cpct_drawStringM1("border color is changed 6 times each", pvm);
	ld	hl, #0xc140
	push	hl
	ld	hl, #___str_2
	push	hl
	call	_cpct_drawStringM1
;src/main.c:54: cpct_drawStringM1("frame. This change  is done by the inte-", pvm);
	ld	hl, #0xc190
	push	hl
	ld	hl, #___str_3
	push	hl
	call	_cpct_drawStringM1
;src/main.c:56: cpct_drawStringM1("rrupt handler. As z80 produces 300 inte-", pvm);
	ld	hl, #0xc1e0
	push	hl
	ld	hl, #___str_4
	push	hl
	call	_cpct_drawStringM1
;src/main.c:58: cpct_drawStringM1("rrupts per second, you have 6 per frame.", pvm);
	ld	hl, #0xc230
	push	hl
	ld	hl, #___str_5
	push	hl
	call	_cpct_drawStringM1
	ret
___str_0:
	.ascii "Interrupt Handler Example"
	.db 0x00
___str_1:
	.ascii "This example is running a void loop, but"
	.db 0x00
___str_2:
	.ascii "border color is changed 6 times each"
	.db 0x00
___str_3:
	.ascii "frame. This change  is done by the inte-"
	.db 0x00
___str_4:
	.ascii "rrupt handler. As z80 produces 300 inte-"
	.db 0x00
___str_5:
	.ascii "rrupts per second, you have 6 per frame."
	.db 0x00
;src/main.c:65: void main(void) {
;	---------------------------------
; Function main
; ---------------------------------
_main::
;src/main.c:69: cpct_disableFirmware();
	call	_cpct_disableFirmware
;src/main.c:70: cpct_setInterruptHandler( myInterruptHandler );
	ld	hl, #_myInterruptHandler
	call	_cpct_setInterruptHandler
;src/main.c:73: printMessages();
	call	_printMessages
;src/main.c:77: while (1);
00102$:
	jr	00102$
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
