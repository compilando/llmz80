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
	.globl _printRandomNumbers
	.globl _initialize
	.globl _wait4UserKeypress
	.globl _printf
	.globl _cpct_restoreState_mxor_u8
	.globl _cpct_setSeed_mxor
	.globl _cpct_getRandom_mxor_u8
	.globl _cpct_isAnyKeyPressed_f
	.globl _cpct_scanKeyboard_f
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
;src/main.c:33: u32 wait4UserKeypress() {
;	---------------------------------
; Function wait4UserKeypress
; ---------------------------------
_wait4UserKeypress::
;src/main.c:37: do {
	ld	hl,#0x0000
	ld	e,l
	ld	d,h
00101$:
;src/main.c:38: c++;                       // One more cycle
	inc	l
	jr	NZ,00115$
	inc	h
	jr	NZ,00115$
	inc	e
	jr	NZ,00115$
	inc	d
00115$:
;src/main.c:39: cpct_scanKeyboard_f();     // Scan the scan the keyboard
	push	hl
	push	de
	call	_cpct_scanKeyboard_f
	call	_cpct_isAnyKeyPressed_f
	ld	a, l
	pop	de
	pop	hl
	or	a, a
	jr	Z,00101$
;src/main.c:42: return c;
	ret
;src/main.c:50: void initialize() {
;	---------------------------------
; Function initialize
; ---------------------------------
_initialize::
;src/main.c:54: printf("\017\003========= BASIC RANDOM NUMBERS =========\n\n\r");
	ld	hl, #___str_0
	push	hl
	call	_printf
;src/main.c:55: printf("\017\002Press any key to generate random numbers\n\n\r");
	ld	hl, #___str_1
	ex	(sp),hl
	call	_printf
	pop	af
;src/main.c:59: seed = wait4UserKeypress();
	call	_wait4UserKeypress
	ex	de, hl
;src/main.c:62: if (!seed)
	ld	a, h
	or	a, l
	or	a, d
	or	a,e
	jr	NZ,00102$
;src/main.c:63: seed++;
	inc	e
	jr	NZ,00109$
	inc	d
	jr	NZ,00109$
	inc	l
	jr	NZ,00109$
	inc	h
00109$:
00102$:
;src/main.c:66: printf("\017\003Selected seed: \017\002%d\n\r", seed);
	ld	bc, #___str_2+0
	push	hl
	push	de
	push	hl
	push	de
	push	bc
	call	_printf
	ld	hl, #6
	add	hl, sp
	ld	sp, hl
	pop	de
	pop	hl
;src/main.c:67: cpct_srand(seed);
	ex	de, hl
	call	_cpct_setSeed_mxor
	jp  _cpct_restoreState_mxor_u8
___str_0:
	.db 0x0f
	.db 0x03
	.ascii "========= BASIC RANDOM NUMBERS ========="
	.db 0x0a
	.db 0x0a
	.db 0x0d
	.db 0x00
___str_1:
	.db 0x0f
	.db 0x02
	.ascii "Press any key to generate random numbers"
	.db 0x0a
	.db 0x0a
	.db 0x0d
	.db 0x00
___str_2:
	.db 0x0f
	.db 0x03
	.ascii "Selected seed: "
	.db 0x0f
	.db 0x02
	.ascii "%d"
	.db 0x0a
	.db 0x0d
	.db 0x00
;src/main.c:76: void printRandomNumbers(u8 nNumbers) {
;	---------------------------------
; Function printRandomNumbers
; ---------------------------------
_printRandomNumbers::
	push	ix
	ld	ix,#0
	add	ix,sp
;src/main.c:78: printf("\017\003Generating \017\002%d\017\003 random numbers\n\n\r\017\001", N_RND_NUMBERS);
	ld	hl, #0x0032
	push	hl
	ld	hl, #___str_3
	push	hl
	call	_printf
	pop	af
	pop	af
;src/main.c:81: while (nNumbers--) {
	ld	c, 4 (ix)
00101$:
	ld	b, c
	dec	c
	ld	a, b
	or	a, a
	jr	Z,00103$
;src/main.c:82: u8 random_number = cpct_rand();  // Get next random number
	push	bc
	call	_cpct_getRandom_mxor_u8
	pop	bc
;src/main.c:83: printf("%d ", random_number);    // Print it 
	ld	h, #0x00
	push	bc
	push	hl
	ld	hl, #___str_4
	push	hl
	call	_printf
	pop	af
	pop	af
	pop	bc
	jr	00101$
00103$:
;src/main.c:87: printf("\n\n\r");
	ld	hl, #___str_5
	push	hl
	call	_printf
	pop	af
	pop	ix
	ret
___str_3:
	.db 0x0f
	.db 0x03
	.ascii "Generating "
	.db 0x0f
	.db 0x02
	.ascii "%d"
	.db 0x0f
	.db 0x03
	.ascii " random numbers"
	.db 0x0a
	.db 0x0a
	.db 0x0d
	.db 0x0f
	.db 0x01
	.db 0x00
___str_4:
	.ascii "%d "
	.db 0x00
___str_5:
	.db 0x0a
	.db 0x0a
	.db 0x0d
	.db 0x00
;src/main.c:93: void main(void) {
;	---------------------------------
; Function main
; ---------------------------------
_main::
;src/main.c:95: while (1) {
00105$:
;src/main.c:97: initialize();  
	call	_initialize
;src/main.c:98: printRandomNumbers(N_RND_NUMBERS);
	ld	a, #0x32
	push	af
	inc	sp
	call	_printRandomNumbers
	inc	sp
;src/main.c:101: do { cpct_scanKeyboard_f(); } while ( cpct_isAnyKeyPressed_f() );
00101$:
	call	_cpct_scanKeyboard_f
	call	_cpct_isAnyKeyPressed_f
	ld	a, l
	or	a, a
	jr	NZ,00101$
	jr	00105$
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
