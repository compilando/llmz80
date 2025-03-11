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
;src/main.c:27: void main(void) {
;	---------------------------------
; Function main
; ---------------------------------
_main::
;src/main.c:29: cpct_clearScreen(0);
	ld	hl, #0x4000
	push	hl
	xor	a, a
	push	af
	inc	sp
	ld	h, #0xc0
	push	hl
	call	_cpct_memset
;src/main.c:38: printf("      \017\003Welcome to \017\002CPCtelera\017\003!\017\001\n\r\n\r");
	ld	hl, #___str_0
	push	hl
	call	_printf
;src/main.c:39: printf("This  example  makes  use  of standard C");
	ld	hl, #___str_1
	ex	(sp),hl
	call	_printf
;src/main.c:40: printf("libraries  to  print out  byte sizes  of");
	ld	hl, #___str_2
	ex	(sp),hl
	call	_printf
;src/main.c:41: printf("standard  SDCC  types, using \017\002CPCtelera\017\001's");
	ld	hl, #___str_3
	ex	(sp),hl
	call	_printf
;src/main.c:42: printf("convenient aliases.\n\r\n\r");
	ld	hl, #___str_4
	ex	(sp),hl
	call	_printf
;src/main.c:43: printf("Size of \017\003 u8 \017\001=\017\002 %d \017\001byte\n\r", sizeof(u8));
	ld	hl, #0x0001
	ex	(sp),hl
	ld	hl, #___str_5
	push	hl
	call	_printf
	pop	af
;src/main.c:44: printf("Size of \017\003u16 \017\001=\017\002 %d \017\001byte\n\r", sizeof(u16));
	ld	hl, #0x0002
	ex	(sp),hl
	ld	hl, #___str_6
	push	hl
	call	_printf
	pop	af
;src/main.c:45: printf("Size of \017\003u32 \017\001=\017\002 %d \017\001byte\n\r", sizeof(u32));
	ld	hl, #0x0004
	ex	(sp),hl
	ld	hl, #___str_7
	push	hl
	call	_printf
	pop	af
;src/main.c:46: printf("Size of \017\003u64 \017\001=\017\002 %d \017\001byte\n\r", sizeof(u64));
	ld	hl, #0x0008
	ex	(sp),hl
	ld	hl, #___str_8
	push	hl
	call	_printf
	pop	af
;src/main.c:47: printf("Size of \017\003 i8 \017\001=\017\002 %d \017\001byte\n\r", sizeof(i8));
	ld	hl, #0x0001
	ex	(sp),hl
	ld	hl, #___str_9
	push	hl
	call	_printf
	pop	af
;src/main.c:48: printf("Size of \017\003i16 \017\001=\017\002 %d \017\001byte\n\r", sizeof(i16));
	ld	hl, #0x0002
	ex	(sp),hl
	ld	hl, #___str_10
	push	hl
	call	_printf
	pop	af
;src/main.c:49: printf("Size of \017\003i32 \017\001=\017\002 %d \017\001byte\n\r", sizeof(i32));
	ld	hl, #0x0004
	ex	(sp),hl
	ld	hl, #___str_11
	push	hl
	call	_printf
	pop	af
;src/main.c:50: printf("Size of \017\003i64 \017\001=\017\002 %d \017\001byte\n\r", sizeof(i64));
	ld	hl, #0x0008
	ex	(sp),hl
	ld	hl, #___str_12
	push	hl
	call	_printf
	pop	af
;src/main.c:51: printf("Size of \017\003f32 \017\001=\017\002 %d \017\001byte\n\r", sizeof(f32));
	ld	hl, #0x0004
	ex	(sp),hl
	ld	hl, #___str_13
	push	hl
	call	_printf
	pop	af
	pop	af
;src/main.c:54: while (1);
00102$:
	jr	00102$
___str_0:
	.ascii "      "
	.db 0x0f
	.db 0x03
	.ascii "Welcome to "
	.db 0x0f
	.db 0x02
	.ascii "CPCtelera"
	.db 0x0f
	.db 0x03
	.ascii "!"
	.db 0x0f
	.db 0x01
	.db 0x0a
	.db 0x0d
	.db 0x0a
	.db 0x0d
	.db 0x00
___str_1:
	.ascii "This  example  makes  use  of standard C"
	.db 0x00
___str_2:
	.ascii "libraries  to  print out  byte sizes  of"
	.db 0x00
___str_3:
	.ascii "standard  SDCC  types, using "
	.db 0x0f
	.db 0x02
	.ascii "CPCtelera"
	.db 0x0f
	.db 0x01
	.ascii "'s"
	.db 0x00
___str_4:
	.ascii "convenient aliases."
	.db 0x0a
	.db 0x0d
	.db 0x0a
	.db 0x0d
	.db 0x00
___str_5:
	.ascii "Size of "
	.db 0x0f
	.db 0x03
	.ascii " u8 "
	.db 0x0f
	.db 0x01
	.ascii "="
	.db 0x0f
	.db 0x02
	.ascii " %d "
	.db 0x0f
	.db 0x01
	.ascii "byte"
	.db 0x0a
	.db 0x0d
	.db 0x00
___str_6:
	.ascii "Size of "
	.db 0x0f
	.db 0x03
	.ascii "u16 "
	.db 0x0f
	.db 0x01
	.ascii "="
	.db 0x0f
	.db 0x02
	.ascii " %d "
	.db 0x0f
	.db 0x01
	.ascii "byte"
	.db 0x0a
	.db 0x0d
	.db 0x00
___str_7:
	.ascii "Size of "
	.db 0x0f
	.db 0x03
	.ascii "u32 "
	.db 0x0f
	.db 0x01
	.ascii "="
	.db 0x0f
	.db 0x02
	.ascii " %d "
	.db 0x0f
	.db 0x01
	.ascii "byte"
	.db 0x0a
	.db 0x0d
	.db 0x00
___str_8:
	.ascii "Size of "
	.db 0x0f
	.db 0x03
	.ascii "u64 "
	.db 0x0f
	.db 0x01
	.ascii "="
	.db 0x0f
	.db 0x02
	.ascii " %d "
	.db 0x0f
	.db 0x01
	.ascii "byte"
	.db 0x0a
	.db 0x0d
	.db 0x00
___str_9:
	.ascii "Size of "
	.db 0x0f
	.db 0x03
	.ascii " i8 "
	.db 0x0f
	.db 0x01
	.ascii "="
	.db 0x0f
	.db 0x02
	.ascii " %d "
	.db 0x0f
	.db 0x01
	.ascii "byte"
	.db 0x0a
	.db 0x0d
	.db 0x00
___str_10:
	.ascii "Size of "
	.db 0x0f
	.db 0x03
	.ascii "i16 "
	.db 0x0f
	.db 0x01
	.ascii "="
	.db 0x0f
	.db 0x02
	.ascii " %d "
	.db 0x0f
	.db 0x01
	.ascii "byte"
	.db 0x0a
	.db 0x0d
	.db 0x00
___str_11:
	.ascii "Size of "
	.db 0x0f
	.db 0x03
	.ascii "i32 "
	.db 0x0f
	.db 0x01
	.ascii "="
	.db 0x0f
	.db 0x02
	.ascii " %d "
	.db 0x0f
	.db 0x01
	.ascii "byte"
	.db 0x0a
	.db 0x0d
	.db 0x00
___str_12:
	.ascii "Size of "
	.db 0x0f
	.db 0x03
	.ascii "i64 "
	.db 0x0f
	.db 0x01
	.ascii "="
	.db 0x0f
	.db 0x02
	.ascii " %d "
	.db 0x0f
	.db 0x01
	.ascii "byte"
	.db 0x0a
	.db 0x0d
	.db 0x00
___str_13:
	.ascii "Size of "
	.db 0x0f
	.db 0x03
	.ascii "f32 "
	.db 0x0f
	.db 0x01
	.ascii "="
	.db 0x0f
	.db 0x02
	.ascii " %d "
	.db 0x0f
	.db 0x01
	.ascii "byte"
	.db 0x0a
	.db 0x0d
	.db 0x00
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
