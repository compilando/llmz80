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
	.globl _printf
	.globl _cpct_setVideoMemoryPage
	.globl _cpct_setPALColour
	.globl _cpct_waitVSYNC
	.globl _cpct_isKeyPressed
	.globl _cpct_scanKeyboard
	.globl _cpct_setStackLocation
	.globl _cpct_memcpy
	.globl _cpct_memset_f64
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
;src/main.c:29: void printMessages() {
;	---------------------------------
; Function printMessages
; ---------------------------------
_printMessages::
;src/main.c:33: printf("     \017\003SET PROGRAM STACK LOCATION DEMO\n\r");
	ld	hl, #___str_0
	push	hl
	call	_printf
;src/main.c:34: printf("    \017\002#################################\n\n\r");
	ld	hl, #___str_1
	ex	(sp),hl
	call	_printf
;src/main.c:36: printf("\017\001  This program  changes  stack  location");
	ld	hl, #___str_2
	ex	(sp),hl
	call	_printf
;src/main.c:37: printf("to \017\0030x200\017\001, just  below  the start  of the");
	ld	hl, #___str_3
	ex	(sp),hl
	call	_printf
;src/main.c:38: printf("main function.\n\n\r");
	ld	hl, #___str_4
	ex	(sp),hl
	call	_printf
;src/main.c:40: printf("  With this change, the 3rd  memory bank");
	ld	hl, #___str_5
	ex	(sp),hl
	call	_printf
;src/main.c:41: printf("can be  enterely used as  double buffer,");
	ld	hl, #___str_6
	ex	(sp),hl
	call	_printf
;src/main.c:42: printf("making easier to map code and  data into");
	ld	hl, #___str_7
	ex	(sp),hl
	call	_printf
;src/main.c:43: printf("memory.\n\n\r");
	ld	hl, #___str_8
	ex	(sp),hl
	call	_printf
;src/main.c:45: printf("  If you  want to  check this, open  the");
	ld	hl, #___str_9
	ex	(sp),hl
	call	_printf
;src/main.c:46: printf("debugger and  have  a look at the  stack");
	ld	hl, #___str_10
	ex	(sp),hl
	call	_printf
;src/main.c:47: printf("pointer (\017\002SP\017\001) and the stack contents.\n\n\r");
	ld	hl, #___str_11
	ex	(sp),hl
	call	_printf
;src/main.c:49: printf("  Now you can use \017\002keys \017\003[\017\0021\017\003]");
	ld	hl, #___str_12
	ex	(sp),hl
	call	_printf
;src/main.c:50: printf("\017\001&\017\003[\017\0022\017\003]\017\001 to change");
	ld	hl, #___str_13
	ex	(sp),hl
	call	_printf
;src/main.c:51: printf("from main  screen  buffer to  the double");
	ld	hl, #___str_14
	ex	(sp),hl
	call	_printf
;src/main.c:52: printf("buffer which contains a fullscreen image");
	ld	hl, #___str_15
	ex	(sp),hl
	call	_printf
;src/main.c:53: printf("with a pattern like this:\n\n\r");
	ld	hl, #___str_16
	ex	(sp),hl
	call	_printf
	pop	af
;src/main.c:55: for (i=0; i < 60; ++i)
	ld	c, #0x00
00102$:
;src/main.c:56: printf("\017\001#\017\003#");
	push	bc
	ld	hl, #___str_17
	push	hl
	call	_printf
	pop	af
	pop	bc
;src/main.c:55: for (i=0; i < 60; ++i)
	inc	c
	ld	a, c
	sub	a, #0x3c
	jr	C,00102$
	ret
___str_0:
	.ascii "     "
	.db 0x0f
	.db 0x03
	.ascii "SET PROGRAM STACK LOCATION DEMO"
	.db 0x0a
	.db 0x0d
	.db 0x00
___str_1:
	.ascii "    "
	.db 0x0f
	.db 0x02
	.ascii "#################################"
	.db 0x0a
	.db 0x0a
	.db 0x0d
	.db 0x00
___str_2:
	.db 0x0f
	.db 0x01
	.ascii "  This program  changes  stack  location"
	.db 0x00
___str_3:
	.ascii "to "
	.db 0x0f
	.db 0x03
	.ascii "0x200"
	.db 0x0f
	.db 0x01
	.ascii ", just  below  the start  of the"
	.db 0x00
___str_4:
	.ascii "main function."
	.db 0x0a
	.db 0x0a
	.db 0x0d
	.db 0x00
___str_5:
	.ascii "  With this change, the 3rd  memory bank"
	.db 0x00
___str_6:
	.ascii "can be  enterely used as  double buffer,"
	.db 0x00
___str_7:
	.ascii "making easier to map code and  data into"
	.db 0x00
___str_8:
	.ascii "memory."
	.db 0x0a
	.db 0x0a
	.db 0x0d
	.db 0x00
___str_9:
	.ascii "  If you  want to  check this, open  the"
	.db 0x00
___str_10:
	.ascii "debugger and  have  a look at the  stack"
	.db 0x00
___str_11:
	.ascii "pointer ("
	.db 0x0f
	.db 0x02
	.ascii "SP"
	.db 0x0f
	.db 0x01
	.ascii ") and the stack contents."
	.db 0x0a
	.db 0x0a
	.db 0x0d
	.db 0x00
___str_12:
	.ascii "  Now you can use "
	.db 0x0f
	.db 0x02
	.ascii "keys "
	.db 0x0f
	.db 0x03
	.ascii "["
	.db 0x0f
	.db 0x02
	.ascii "1"
	.db 0x0f
	.db 0x03
	.ascii "]"
	.db 0x00
___str_13:
	.db 0x0f
	.db 0x01
	.ascii "&"
	.db 0x0f
	.db 0x03
	.ascii "["
	.db 0x0f
	.db 0x02
	.ascii "2"
	.db 0x0f
	.db 0x03
	.ascii "]"
	.db 0x0f
	.db 0x01
	.ascii " to change"
	.db 0x00
___str_14:
	.ascii "from main  screen  buffer to  the double"
	.db 0x00
___str_15:
	.ascii "buffer which contains a fullscreen image"
	.db 0x00
___str_16:
	.ascii "with a pattern like this:"
	.db 0x0a
	.db 0x0a
	.db 0x0d
	.db 0x00
___str_17:
	.db 0x0f
	.db 0x01
	.ascii "#"
	.db 0x0f
	.db 0x03
	.ascii "#"
	.db 0x00
;src/main.c:62: void main(void) { 
;	---------------------------------
; Function main
; ---------------------------------
_main::
;src/main.c:64: cpct_clearScreen_f64(0x0000);
	ld	hl, #0x4000
	push	hl
	ld	h, #0x00
	push	hl
	ld	h, #0xc0
	push	hl
	call	_cpct_memset_f64
;src/main.c:65: printMessages();
	call	_printMessages
;src/main.c:69: cpct_disableFirmware();
	call	_cpct_disableFirmware
;src/main.c:76: cpct_memcpy(NEW_STACK_LOCATION - 6, PREVIOUS_STACK_LOCATION - 6, 6);
	ld	hl, #0x0006
	push	hl
	ld	hl, #0xbffa
	push	hl
	ld	h, #0x01
	push	hl
	call	_cpct_memcpy
;src/main.c:77: cpct_setStackLocation(NEW_STACK_LOCATION - 6);
	ld	hl, #0x01fa
	call	_cpct_setStackLocation
;src/main.c:81: cpct_memset_f64((void*)0x8000, 0xFFF0, 0x4000);
	ld	hl, #0x4000
	push	hl
	ld	hl, #0xfff0
	push	hl
	ld	hl, #0x8000
	push	hl
	call	_cpct_memset_f64
;src/main.c:85: while(1) {
00107$:
;src/main.c:86: cpct_waitVSYNC();
	call	_cpct_waitVSYNC
;src/main.c:87: cpct_scanKeyboard();     
	call	_cpct_scanKeyboard
;src/main.c:89: if (cpct_isKeyPressed(Key_1)) {
	ld	hl, #0x0108
	call	_cpct_isKeyPressed
	ld	a, l
	or	a, a
	jr	Z,00104$
;src/main.c:90: cpct_setBorder(4);
	ld	hl, #0x0410
	push	hl
	call	_cpct_setPALColour
;src/main.c:91: cpct_setVideoMemoryPage(cpct_pageC0);
	ld	l, #0x30
	call	_cpct_setVideoMemoryPage
	jr	00107$
00104$:
;src/main.c:92: } else if (cpct_isKeyPressed(Key_2)) {
	ld	hl, #0x0208
	call	_cpct_isKeyPressed
	ld	a, l
	or	a, a
	jr	Z,00107$
;src/main.c:93: cpct_setBorder(3);
	ld	hl, #0x0310
	push	hl
	call	_cpct_setPALColour
;src/main.c:94: cpct_setVideoMemoryPage(cpct_page80);
	ld	l, #0x20
	call	_cpct_setVideoMemoryPage
	jr	00107$
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
