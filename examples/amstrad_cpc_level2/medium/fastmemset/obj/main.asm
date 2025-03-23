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
	.globl _doSomeClears
	.globl _doSomeClears8
	.globl _waitNVSYNCs
	.globl _getColourPattern
	.globl _cpct_setPALColour
	.globl _cpct_waitVSYNC
	.globl _cpct_setVideoMode
	.globl _cpct_px2byteM0
	.globl _cpct_memset_f64
	.globl _cpct_memset_f8
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
;src/main.c:27: u16 getColourPattern(u8 c1, u8 c2, u8 c3, u8 c4) {
;	---------------------------------
; Function getColourPattern
; ---------------------------------
_getColourPattern::
	push	ix
	ld	ix,#0
	add	ix,sp
;src/main.c:28: return 256*cpct_px2byteM0(c3, c4) + cpct_px2byteM0(c1, c2);
	ld	h, 7 (ix)
	ld	l, 6 (ix)
	push	hl
	call	_cpct_px2byteM0
	ld	b, l
	ld	c, #0x00
	push	bc
	ld	h, 5 (ix)
	ld	l, 4 (ix)
	push	hl
	call	_cpct_px2byteM0
	pop	bc
	ld	h, #0x00
	add	hl, bc
	pop	ix
	ret
;src/main.c:34: void waitNVSYNCs(u8 n) {
;	---------------------------------
; Function waitNVSYNCs
; ---------------------------------
_waitNVSYNCs::
;src/main.c:35: do {
	ld	hl, #2+0
	add	hl, sp
	ld	c, (hl)
00103$:
;src/main.c:37: cpct_waitVSYNC();
	push	bc
	call	_cpct_waitVSYNC
	pop	bc
;src/main.c:42: if (--n) {
	dec	c
	ld	a, c
	or	a, a
	jr	Z,00104$
;src/main.c:43: __asm__ ("halt"); // Halt stops the Z80 until next interrupt.
	halt
;src/main.c:44: __asm__ ("halt"); // There are 6 interrupts per VSYNC (1/300 seconds each)
	halt
00104$:
;src/main.c:46: } while(n);
	ld	a, c
	or	a, a
	jr	NZ,00103$
	ret
;src/main.c:53: void doSomeClears8(u8 colour, u8 vsyncs) {
;	---------------------------------
; Function doSomeClears8
; ---------------------------------
_doSomeClears8::
	dec	sp
;src/main.c:55: for(i=0; i < 2 ; i++) {
	ld	iy, #0
	add	iy, sp
	ld	0 (iy), #0x00
00102$:
;src/main.c:56: u8 pattern = cpct_px2byteM0(colour, colour);
	ld	iy, #3
	add	iy, sp
	ld	h, 0 (iy)
	ld	l, 0 (iy)
	push	hl
	call	_cpct_px2byteM0
	ld	b, l
;src/main.c:57: waitNVSYNCs(vsyncs);
	push	bc
	ld	hl, #6+0
	add	hl, sp
	ld	a, (hl)
	push	af
	inc	sp
	call	_waitNVSYNCs
	inc	sp
	pop	bc
;src/main.c:58: cpct_memset(CPCT_VMEM_START, pattern, 0x4000);
	ld	hl, #0x4000
	push	hl
	push	bc
	inc	sp
	ld	h, #0xc0
	push	hl
	call	_cpct_memset
;src/main.c:59: waitNVSYNCs(vsyncs);
	ld	hl, #4+0
	add	hl, sp
	ld	a, (hl)
	push	af
	inc	sp
	call	_waitNVSYNCs
	inc	sp
;src/main.c:60: cpct_memset(CPCT_VMEM_START,       0, 0x4000);
	ld	hl, #0x4000
	push	hl
	xor	a, a
	push	af
	inc	sp
	ld	h, #0xc0
	push	hl
	call	_cpct_memset
;src/main.c:55: for(i=0; i < 2 ; i++) {
	ld	iy, #0
	add	iy, sp
	inc	0 (iy)
	ld	a, 0 (iy)
	sub	a, #0x02
	jr	C,00102$
	inc	sp
	ret
;src/main.c:69: void doSomeClears(TMemsetFunc func, u8 colour, u8 vsyncs) {
;	---------------------------------
; Function doSomeClears
; ---------------------------------
_doSomeClears::
	push	ix
	ld	ix,#0
	add	ix,sp
	dec	sp
;src/main.c:71: for(i=0; i < 2 ; i++) {
	ld	-1 (ix), #0x00
00102$:
;src/main.c:72: u16 pattern = getColourPattern(colour, colour, colour, colour);
	ld	h, 6 (ix)
	ld	l, 6 (ix)
	push	hl
	ld	h, 6 (ix)
	ld	l, 6 (ix)
	push	hl
	call	_getColourPattern
	pop	af
;src/main.c:73: waitNVSYNCs(vsyncs);
	ex	(sp),hl
	ld	a, 7 (ix)
	push	af
	inc	sp
	call	_waitNVSYNCs
	inc	sp
	pop	hl
;src/main.c:74: func(CPCT_VMEM_START, pattern, 0x4000);
	ld	bc, #0x4000
	push	bc
	push	hl
	ld	hl, #0xc000
	push	hl
	ld	l,4 (ix)
	ld	h,5 (ix)
	call	___sdcc_call_hl
;src/main.c:75: waitNVSYNCs(vsyncs);
	ld	a, 7 (ix)
	push	af
	inc	sp
	call	_waitNVSYNCs
	inc	sp
;src/main.c:76: func(CPCT_VMEM_START,       0, 0x4000);
	ld	hl, #0x4000
	push	hl
	ld	h, #0x00
	push	hl
	ld	h, #0xc0
	push	hl
	ld	l,4 (ix)
	ld	h,5 (ix)
	call	___sdcc_call_hl
;src/main.c:71: for(i=0; i < 2 ; i++) {
	inc	-1 (ix)
	ld	a, -1 (ix)
	sub	a, #0x02
	jr	C,00102$
	inc	sp
	pop	ix
	ret
;src/main.c:83: void main(void) {   
;	---------------------------------
; Function main
; ---------------------------------
_main::
;src/main.c:84: u8 colour = 1, vsyncs = 50;
	ld	bc,#0x3201
;src/main.c:88: cpct_disableFirmware(); 
	push	bc
	call	_cpct_disableFirmware
	ld	l, #0x00
	call	_cpct_setVideoMode
	pop	bc
;src/main.c:92: while(1) {
00106$:
;src/main.c:94: cpct_setBorder(4);
	push	bc
	ld	hl, #0x0410
	push	hl
	call	_cpct_setPALColour
	pop	bc
;src/main.c:95: doSomeClears8(colour, vsyncs);
	push	bc
	push	bc
	call	_doSomeClears8
	ld	hl, #0x0110
	ex	(sp),hl
	call	_cpct_setPALColour
	pop	bc
;src/main.c:99: doSomeClears(&cpct_memset_f8,  colour, vsyncs);
	push	bc
	push	bc
	ld	hl, #_cpct_memset_f8
	push	hl
	call	_doSomeClears
	pop	af
	ld	hl, #0x0510
	ex	(sp),hl
	call	_cpct_setPALColour
	pop	bc
;src/main.c:103: doSomeClears(&cpct_memset_f64, colour, vsyncs);
	push	bc
	push	bc
	ld	hl, #_cpct_memset_f64
	push	hl
	call	_doSomeClears
	pop	af
	pop	af
	pop	bc
;src/main.c:106: if (++colour > 15) colour = 1;
	inc	c
	ld	a, #0x0f
	sub	a, c
	jr	NC,00102$
	ld	c, #0x01
00102$:
;src/main.c:107: if (! --vsyncs) vsyncs = 50;
	djnz	00106$
	ld	b, #0x32
	jr	00106$
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
