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
	.globl _printf
	.globl _cpct_getHWColour
	.globl _cpct_memset
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
;src/main.c:30: cpct_clearScreen(0);
	ld	hl, #0x4000
	push	hl
	xor	a, a
	push	af
	inc	sp
	ld	h, #0xc0
	push	hl
	call	_cpct_memset
;src/main.c:40: printf("        \017\003Hardware Colour values\017\002          ");
	ld	hl, #___str_0
	push	hl
	call	_printf
;src/main.c:41: printf("This example shows the  equivalence between firmware co-");
	ld	hl, #___str_1
	ex	(sp),hl
	call	_printf
;src/main.c:42: printf("lour  values  and harwdware  colour values. \017\003CPCtelera\017\002's ");
	ld	hl, #___str_2
	ex	(sp),hl
	call	_printf
;src/main.c:43: printf("functions that change colours use hardware ones.\n\r\n\r");
	ld	hl, #___str_3
	ex	(sp),hl
	call	_printf
;src/main.c:44: printf("   \017\003==================================\n\r");
	ld	hl, #___str_4
	ex	(sp),hl
	call	_printf
;src/main.c:45: printf("   || \017\002FIRM -- HARD \017\003|| \017\002FIRM -- HARD \017\003||\n\r");
	ld	hl, #___str_5
	ex	(sp),hl
	call	_printf
;src/main.c:46: printf("   ==================================\n\r");
	ld	hl, #___str_6
	ex	(sp),hl
	call	_printf
	pop	af
;src/main.c:47: for (i=0; i < 13; ++i) {
	ld	c, #0x00
00105$:
;src/main.c:48: printf("   \017\003||  \017\001%2d  \017\003--  \017\001%2d\017\003  ",       i, cpct_getHWColour(i));
	ld	l, c
	ld	h, #0x00
	push	bc
	call	_cpct_getHWColour
	pop	bc
	ld	h, #0x00
	ld	e, c
	ld	d, #0x00
	push	bc
	push	de
	push	hl
	push	de
	ld	hl, #___str_7
	push	hl
	call	_printf
	ld	hl, #6
	add	hl, sp
	ld	sp, hl
	pop	de
	pop	bc
;src/main.c:49: printf("\017\003||  \017\001%2d  \017\003--  \017\001%2d\017\003  ||\n\r", i+13, cpct_getHWColour(i+13));
	ld	hl, #0x000d
	add	hl, de
	push	hl
	push	bc
	call	_cpct_getHWColour
	ld	e, l
	pop	bc
	pop	hl
	ld	d, #0x00
	push	bc
	push	de
	push	hl
	ld	hl, #___str_8
	push	hl
	call	_printf
	ld	hl, #6
	add	hl, sp
	ld	sp, hl
	pop	bc
;src/main.c:47: for (i=0; i < 13; ++i) {
	inc	c
	ld	a, c
	sub	a, #0x0d
	jr	C,00105$
;src/main.c:51: printf("   ==================================\n\r");
	ld	hl, #___str_6
	push	hl
	call	_printf
	pop	af
;src/main.c:54: while (1);
00103$:
	jr	00103$
___str_0:
	.ascii "        "
	.db 0x0f
	.db 0x03
	.ascii "Hardware Colour values"
	.db 0x0f
	.db 0x02
	.ascii "          "
	.db 0x00
___str_1:
	.ascii "This example shows the  equivalence between firmware co-"
	.db 0x00
___str_2:
	.ascii "lour  values  and harwdware  colour values. "
	.db 0x0f
	.db 0x03
	.ascii "CPCtelera"
	.db 0x0f
	.db 0x02
	.ascii "'s "
	.db 0x00
___str_3:
	.ascii "functions that change colours use hardware ones."
	.db 0x0a
	.db 0x0d
	.db 0x0a
	.db 0x0d
	.db 0x00
___str_4:
	.ascii "   "
	.db 0x0f
	.db 0x03
	.ascii "=================================="
	.db 0x0a
	.db 0x0d
	.db 0x00
___str_5:
	.ascii "   || "
	.db 0x0f
	.db 0x02
	.ascii "FIRM -- HARD "
	.db 0x0f
	.db 0x03
	.ascii "|| "
	.db 0x0f
	.db 0x02
	.ascii "FIRM -- HARD "
	.db 0x0f
	.db 0x03
	.ascii "||"
	.db 0x0a
	.db 0x0d
	.db 0x00
___str_6:
	.ascii "   =================================="
	.db 0x0a
	.db 0x0d
	.db 0x00
___str_7:
	.ascii "   "
	.db 0x0f
	.db 0x03
	.ascii "||  "
	.db 0x0f
	.db 0x01
	.ascii "%2d  "
	.db 0x0f
	.db 0x03
	.ascii "--  "
	.db 0x0f
	.db 0x01
	.ascii "%2d"
	.db 0x0f
	.db 0x03
	.ascii "  "
	.db 0x00
___str_8:
	.db 0x0f
	.db 0x03
	.ascii "||  "
	.db 0x0f
	.db 0x01
	.ascii "%2d  "
	.db 0x0f
	.db 0x03
	.ascii "--  "
	.db 0x0f
	.db 0x01
	.ascii "%2d"
	.db 0x0f
	.db 0x03
	.ascii "  ||"
	.db 0x0a
	.db 0x0d
	.db 0x00
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
