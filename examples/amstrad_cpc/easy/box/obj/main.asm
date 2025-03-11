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
	.globl _cpct_drawSolidBox
	.globl _cpct_px2byteM1
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
;src/main.c:36: void main(void) {
;	---------------------------------
; Function main
; ---------------------------------
_main::
;src/main.c:38: cpct_clearScreen(0x00);
	ld	hl, #0x4000
	push	hl
	xor	a, a
	push	af
	inc	sp
	ld	h, #0xc0
	push	hl
	call	_cpct_memset
;src/main.c:43: cpct_drawSolidBox((u8*)0xC235, cpct_px2byteM1(2, 2, 1, 1), 10, 20); 
	ld	hl, #0x0101
	push	hl
	ld	hl, #0x0202
	push	hl
	call	_cpct_px2byteM1
	pop	af
	pop	af
	ld	h, #0x00
	ld	bc, #0x140a
	push	bc
	push	hl
	ld	hl, #0xc235
	push	hl
	call	_cpct_drawSolidBox
;src/main.c:44: cpct_drawSolidBox((u8*)0xC245, cpct_px2byteM1(1, 0, 2, 1), 10, 20); 
	ld	hl, #0x0102
	push	hl
	ld	hl, #0x0001
	push	hl
	call	_cpct_px2byteM1
	pop	af
	pop	af
	ld	h, #0x00
	ld	bc, #0x140a
	push	bc
	push	hl
	ld	hl, #0xc245
	push	hl
	call	_cpct_drawSolidBox
;src/main.c:45: cpct_drawSolidBox((u8*)0xC255, cpct_px2byteM1(0, 2, 0, 1), 10, 20); 
	ld	hl, #0x0100
	push	hl
	ld	h, #0x02
	push	hl
	call	_cpct_px2byteM1
	pop	af
	pop	af
	ld	h, #0x00
	ld	bc, #0x140a
	push	bc
	push	hl
	ld	hl, #0xc255
	push	hl
	call	_cpct_drawSolidBox
;src/main.c:48: cpct_drawSolidBox((u8*)0xC325, 0xAA, 10, 20); // 0xAA = cpct_px2byteM1(3, 0, 3, 0)
	ld	hl, #0x140a
	push	hl
	ld	hl, #0x00aa
	push	hl
	ld	hl, #0xc325
	push	hl
	call	_cpct_drawSolidBox
;src/main.c:49: cpct_drawSolidBox((u8*)0xC335, 0xA0, 10, 20); // 0xA0 = cpct_px2byteM1(1, 0, 1, 0)
	ld	hl, #0x140a
	push	hl
	ld	hl, #0x00a0
	push	hl
	ld	hl, #0xc335
	push	hl
	call	_cpct_drawSolidBox
;src/main.c:50: cpct_drawSolidBox((u8*)0xC345, 0x0A, 10, 20); // 0x0A = cpct_px2byteM1(2, 0, 2, 0)
	ld	hl, #0x140a
	push	hl
	ld	h, #0x00
	push	hl
	ld	hl, #0xc345
	push	hl
	call	_cpct_drawSolidBox
;src/main.c:53: cpct_drawSolidBox((u8*)0xC415, 0x55, 10, 20); // 0x55 = cpct_px2byteM1(0, 3, 0, 3)
	ld	hl, #0x140a
	push	hl
	ld	hl, #0x0055
	push	hl
	ld	hl, #0xc415
	push	hl
	call	_cpct_drawSolidBox
;src/main.c:54: cpct_drawSolidBox((u8*)0xC425, 0x50, 10, 20); // 0x50 = cpct_px2byteM1(0, 1, 0, 1)
	ld	hl, #0x140a
	push	hl
	ld	hl, #0x0050
	push	hl
	ld	hl, #0xc425
	push	hl
	call	_cpct_drawSolidBox
;src/main.c:55: cpct_drawSolidBox((u8*)0xC435, 0x05, 10, 20); // 0x05 = cpct_px2byteM1(0, 2, 0, 2)
	ld	hl, #0x140a
	push	hl
	ld	hl, #0x0005
	push	hl
	ld	hl, #0xc435
	push	hl
	call	_cpct_drawSolidBox
;src/main.c:58: cpct_drawSolidBox((u8*)0xC505, cpct_px2byteM1(3, 3, 3, 3), 10, 20); // 0xFF 
	ld	hl, #0x0303
	push	hl
	ld	l, #0x03
	push	hl
	call	_cpct_px2byteM1
	pop	af
	pop	af
	ld	h, #0x00
	ld	bc, #0x140a
	push	bc
	push	hl
	ld	hl, #0xc505
	push	hl
	call	_cpct_drawSolidBox
;src/main.c:59: cpct_drawSolidBox((u8*)0xC515, cpct_px2byteM1(2, 2, 2, 2), 10, 20); // 0xF0
	ld	hl, #0x0202
	push	hl
	ld	l, #0x02
	push	hl
	call	_cpct_px2byteM1
	pop	af
	pop	af
	ld	h, #0x00
	ld	bc, #0x140a
	push	bc
	push	hl
	ld	hl, #0xc515
	push	hl
	call	_cpct_drawSolidBox
;src/main.c:60: cpct_drawSolidBox((u8*)0xC525, cpct_px2byteM1(1, 1, 1, 1), 10, 20); // 0x0F
	ld	hl, #0x0101
	push	hl
	ld	l, #0x01
	push	hl
	call	_cpct_px2byteM1
	pop	af
	pop	af
	ld	h, #0x00
	ld	bc, #0x140a
	push	bc
	push	hl
	ld	hl, #0xc525
	push	hl
	call	_cpct_drawSolidBox
;src/main.c:63: while (1);
00102$:
	jr	00102$
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
