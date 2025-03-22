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
	.globl _printArray
	.globl _cpct_setVideoMode
	.globl _cpct_drawCharM2
	.globl _cpct_setDrawCharM2
	.globl _cpct_set4Bits
	.globl _cpct_set2Bits
	.globl _cpct_setBit
	.globl _cpct_get4Bits
	.globl _cpct_get2Bits
	.globl _cpct_getBit
	.globl _cpct_memset
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
;src/main.c:35: void printArray(u8* pvideomem, void *array, u8 nItems, TFunc thefunction) {
;	---------------------------------
; Function printArray
; ---------------------------------
_printArray::
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	hl, #-8
	add	hl, sp
	ld	sp, hl
;src/main.c:36: u8 out = 0; // Value returned by getBit functions [0-15]
	ld	c, #0x00
;src/main.c:41: for (i = 0; i < nItems; ++i) {
	ld	a, 9 (ix)
	or	a, a
	jr	NZ,00145$
	ld	a,#0x01
	jr	00146$
00145$:
	xor	a,a
00146$:
	ld	-1 (ix), a
	ld	a, 9 (ix)
	dec	a
	jr	NZ,00147$
	ld	a,#0x01
	jr	00148$
00147$:
	xor	a,a
00148$:
	ld	-7 (ix), a
	ld	a, 9 (ix)
	sub	a, #0x02
	jr	NZ,00149$
	ld	a,#0x01
	jr	00150$
00149$:
	xor	a,a
00150$:
	ld	-6 (ix), a
	ld	a, 4 (ix)
	ld	-5 (ix), a
	ld	a, 5 (ix)
	ld	-4 (ix), a
	ld	-8 (ix), #0x00
00110$:
	ld	a, -8 (ix)
	sub	a, 8 (ix)
	jp	NC, 00112$
;src/main.c:48: case f_getbit:   out = (cpct_getBit (array, i) > 0); break;
	ld	a, -8 (ix)
	ld	-3 (ix), a
	ld	-2 (ix), #0x00
;src/main.c:45: switch(thefunction) {
	ld	a, -1 (ix)
	or	a, a
	jr	NZ,00101$
	ld	a, -7 (ix)
	or	a, a
	jr	NZ,00102$
	ld	a, -6 (ix)
	or	a, a
	jr	NZ,00103$
	jr	00104$
;src/main.c:48: case f_getbit:   out = (cpct_getBit (array, i) > 0); break;
00101$:
	ld	l,-3 (ix)
	ld	h,-2 (ix)
	push	hl
	ld	l,6 (ix)
	ld	h,7 (ix)
	push	hl
	call	_cpct_getBit
	ld	a, l
	or	a, a
	jr	Z,00114$
	ld	c, #0x01
	jr	00104$
00114$:
	ld	c, #0x00
	jr	00104$
;src/main.c:51: case f_get2bits: out = cpct_get2Bits(array, i); break;
00102$:
	ld	l,-3 (ix)
	ld	h,-2 (ix)
	push	hl
	ld	l,6 (ix)
	ld	h,7 (ix)
	push	hl
	call	_cpct_get2Bits
	ld	c, l
	jr	00104$
;src/main.c:54: case f_get4bits: out = cpct_get4Bits(array, i); break;
00103$:
	ld	l,-3 (ix)
	ld	h,-2 (ix)
	push	hl
	ld	l,6 (ix)
	ld	h,7 (ix)
	push	hl
	call	_cpct_get4Bits
	ld	c, l
;src/main.c:55: }
00104$:
;src/main.c:58: if (out) 
	ld	a, c
	or	a, a
	jr	Z,00106$
;src/main.c:59: c = '0' + out;
	ld	a, c
	add	a, #0x30
	ld	e, a
	jr	00107$
00106$:
;src/main.c:61: c = '_';
	ld	e, #0x5f
00107$:
;src/main.c:65: cpct_drawCharM2(pvideomem, c);
	ld	d, #0x00
	ld	l,-5 (ix)
	ld	h,-4 (ix)
	push	bc
	push	de
	push	hl
	call	_cpct_drawCharM2
	pop	bc
;src/main.c:66: pvideomem++;
	inc	-5 (ix)
	jr	NZ,00151$
	inc	-4 (ix)
00151$:
;src/main.c:41: for (i = 0; i < nItems; ++i) {
	inc	-8 (ix)
	jp	00110$
00112$:
	ld	sp, ix
	pop	ix
	ret
;src/main.c:73: void main (void) {
;	---------------------------------
; Function main
; ---------------------------------
_main::
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	hl, #-83
	add	hl, sp
	ld	sp, hl
;src/main.c:81: cpct_disableFirmware();
	call	_cpct_disableFirmware
;src/main.c:84: cpct_setVideoMode(2);
	ld	l, #0x02
	call	_cpct_setVideoMode
;src/main.c:85: cpct_setDrawCharM2(1, 0); // Draw characters in Foreground colour
	ld	hl, #0x0001
	push	hl
	call	_cpct_setDrawCharM2
;src/main.c:90: while(1) {
00110$:
;src/main.c:93: cpct_memset(array1, 0, 10);
	ld	hl, #0x003d
	add	hl, sp
	ld	-2 (ix), l
	ld	-1 (ix), h
	ld	c, l
	ld	b, h
	ld	hl, #0x000a
	push	hl
	xor	a, a
	push	af
	inc	sp
	push	bc
	call	_cpct_memset
;src/main.c:94: cpct_memset(array2, 0, 20);
	ld	hl, #0x0029
	add	hl, sp
	ld	-8 (ix), l
	ld	-7 (ix), h
	ld	c, l
	ld	b, h
	ld	hl, #0x0014
	push	hl
	xor	a, a
	push	af
	inc	sp
	push	bc
	call	_cpct_memset
;src/main.c:95: cpct_memset(array4, 0, 40);
	ld	hl, #0x0001
	add	hl, sp
	ld	c, l
	ld	b, h
	ld	e, c
	ld	d, b
	push	bc
	ld	hl, #0x0028
	push	hl
	xor	a, a
	push	af
	inc	sp
	push	de
	call	_cpct_memset
	pop	bc
;src/main.c:100: for (i = 0; i < 80; ++i) {
	ld	a, -2 (ix)
	ld	-6 (ix), a
	ld	a, -1 (ix)
	ld	-5 (ix), a
	ld	a, -2 (ix)
	ld	-4 (ix), a
	ld	a, -1 (ix)
	ld	-3 (ix), a
	ld	a, -2 (ix)
	ld	-10 (ix), a
	ld	a, -1 (ix)
	ld	-9 (ix), a
	ld	-11 (ix), #0x00
00112$:
;src/main.c:102: cpct_setBit(array1, 1, i);
	ld	l, -11 (ix)
	ld	h, #0x00
	ld	e, -6 (ix)
	ld	d, -5 (ix)
	push	de
	pop	iy
	push	hl
	push	bc
	push	hl
	ld	de, #0x0001
	push	de
	push	iy
	call	_cpct_setBit
	pop	bc
	pop	hl
;src/main.c:105: printArray(CPCT_VMEM_START, array1, 80, f_getbit); 
	ld	e, -4 (ix)
	ld	d, -3 (ix)
	push	de
	pop	iy
	push	hl
	push	bc
	ld	de, #0x0050
	push	de
	push	iy
	ld	de, #0xc000
	push	de
	call	_printArray
	ld	hl, #6
	add	hl, sp
	ld	sp, hl
	pop	bc
	pop	hl
;src/main.c:108: cpct_setBit(array1, 0, i);
	ld	e,-10 (ix)
	ld	d,-9 (ix)
	push	bc
	push	hl
	ld	hl, #0x0000
	push	hl
	push	de
	call	_cpct_setBit
	pop	bc
;src/main.c:100: for (i = 0; i < 80; ++i) {
	inc	-11 (ix)
	ld	a, -11 (ix)
	sub	a, #0x50
	jr	C,00112$
;src/main.c:115: for (j = 3; j > 0; --j) { 
	ld	a, -8 (ix)
	ld	-10 (ix), a
	ld	a, -7 (ix)
	ld	-9 (ix), a
	ld	a, -8 (ix)
	ld	-4 (ix), a
	ld	a, -7 (ix)
	ld	-3 (ix), a
	ld	a, -8 (ix)
	ld	-6 (ix), a
	ld	a, -7 (ix)
	ld	-5 (ix), a
	ld	-12 (ix), #0x03
;src/main.c:116: for (i = 0; i < 80; ++i) {
00136$:
	ld	-11 (ix), #0x00
00114$:
;src/main.c:118: cpct_set2Bits(array2, j, i);
	ld	l, -11 (ix)
	ld	h, #0x00
	ld	e, -12 (ix)
	ld	d, #0x00
	push	hl
	ld	l, -10 (ix)
	ld	h, -9 (ix)
	push	hl
	pop	iy
	pop	hl
	push	hl
	push	bc
	push	hl
	push	de
	push	iy
	call	_cpct_set2Bits
	pop	bc
	pop	hl
;src/main.c:121: printArray((u8*)0xC0A0, array2, 80, f_get2bits);
	ld	e, -4 (ix)
	ld	d, -3 (ix)
	push	de
	pop	iy
	push	hl
	push	bc
	ld	de, #0x0150
	push	de
	push	iy
	ld	de, #0xc0a0
	push	de
	call	_printArray
	ld	hl, #6
	add	hl, sp
	ld	sp, hl
	pop	bc
	pop	hl
;src/main.c:124: cpct_set2Bits(array2, 0, i);
	ld	e,-6 (ix)
	ld	d,-5 (ix)
	push	bc
	push	hl
	ld	hl, #0x0000
	push	hl
	push	de
	call	_cpct_set2Bits
	pop	bc
;src/main.c:116: for (i = 0; i < 80; ++i) {
	inc	-11 (ix)
	ld	a, -11 (ix)
	sub	a, #0x50
	jr	C,00114$
;src/main.c:115: for (j = 3; j > 0; --j) { 
	dec	-12 (ix)
	ld	a, -12 (ix)
	or	a, a
	jr	NZ,00136$
;src/main.c:133: for (j = 0; j < 16; j++) { 
	ld	-10 (ix), c
	ld	-9 (ix), b
	ld	-4 (ix), c
	ld	-3 (ix), b
	ld	-12 (ix), #0x00
;src/main.c:134: for (i = 0; i < 80; ++i) {
00140$:
	ld	-11 (ix), #0x00
00118$:
;src/main.c:136: u8 value = (i + j) & 0x0F;
	ld	a, -11 (ix)
	add	a, -12 (ix)
	ld	-6 (ix), a
	and	a, #0x0f
	ld	-83 (ix), a
;src/main.c:139: cpct_set4Bits(array4, value, i);
	ld	a, -11 (ix)
	ld	-6 (ix), a
	ld	-5 (ix), #0x00
	ld	e, -83 (ix)
	ld	d, #0x00
	ld	c,-10 (ix)
	ld	b,-9 (ix)
	ld	l,-6 (ix)
	ld	h,-5 (ix)
	push	hl
	push	de
	push	bc
	call	_cpct_set4Bits
;src/main.c:140: printArray((u8*)0xC140, array4, 80, f_get4bits);
	ld	c,-4 (ix)
	ld	b,-3 (ix)
	ld	hl, #0x0250
	push	hl
	push	bc
	ld	hl, #0xc140
	push	hl
	call	_printArray
	ld	hl, #6
	add	hl, sp
	ld	sp, hl
;src/main.c:134: for (i = 0; i < 80; ++i) {
	inc	-11 (ix)
	ld	a, -11 (ix)
	sub	a, #0x50
	jr	C,00118$
;src/main.c:133: for (j = 0; j < 16; j++) { 
	inc	-12 (ix)
	ld	a, -12 (ix)
	sub	a, #0x10
	jr	C,00140$
;src/main.c:147: for (i = 0; i < 80; ++i) {
	ld	a, -2 (ix)
	ld	-10 (ix), a
	ld	a, -1 (ix)
	ld	-9 (ix), a
	ld	a, -2 (ix)
	ld	-4 (ix), a
	ld	a, -1 (ix)
	ld	-3 (ix), a
	ld	-11 (ix), #0x00
00122$:
;src/main.c:149: cpct_setBit(array1, 1, i);
	ld	e, -11 (ix)
	ld	d, #0x00
	ld	c,-10 (ix)
	ld	b,-9 (ix)
	push	de
	ld	hl, #0x0001
	push	hl
	push	bc
	call	_cpct_setBit
;src/main.c:152: printArray(CPCT_VMEM_START, array1, 80, f_getbit); 
	ld	c,-4 (ix)
	ld	b,-3 (ix)
	ld	hl, #0x0050
	push	hl
	push	bc
	ld	hl, #0xc000
	push	hl
	call	_printArray
	ld	hl, #6
	add	hl, sp
	ld	sp, hl
;src/main.c:147: for (i = 0; i < 80; ++i) {
	inc	-11 (ix)
	ld	a, -11 (ix)
	sub	a, #0x50
	jr	C,00122$
;src/main.c:158: for (j = 3; j > 0; --j) { 
	ld	c,-8 (ix)
	ld	b,-7 (ix)
	ld	e,-8 (ix)
	ld	d,-7 (ix)
	ld	-12 (ix), #0x03
;src/main.c:159: for (i = 0; i < 80; ++i) {
00146$:
	ld	-11 (ix), #0x00
00124$:
;src/main.c:161: cpct_set2Bits(array2, j, i);
	ld	l, -11 (ix)
	ld	h, #0x00
	ld	a, -12 (ix)
	ld	-10 (ix), a
	ld	-9 (ix), #0x00
	push	bc
	pop	iy
	push	bc
	push	de
	push	hl
	ld	l,-10 (ix)
	ld	h,-9 (ix)
	push	hl
	push	iy
	call	_cpct_set2Bits
	pop	de
	pop	bc
;src/main.c:164: printArray((u8*)0xC0A0, array2, 80, f_get2bits); 
	push	de
	pop	iy
	push	bc
	push	de
	ld	hl, #0x0150
	push	hl
	push	iy
	ld	hl, #0xc0a0
	push	hl
	call	_printArray
	ld	hl, #6
	add	hl, sp
	ld	sp, hl
	pop	de
	pop	bc
;src/main.c:159: for (i = 0; i < 80; ++i) {
	inc	-11 (ix)
	ld	a, -11 (ix)
	sub	a, #0x50
	jr	C,00124$
;src/main.c:158: for (j = 3; j > 0; --j) { 
	dec	-12 (ix)
	ld	a, -12 (ix)
	or	a, a
	jr	NZ,00146$
	jp	00110$
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
