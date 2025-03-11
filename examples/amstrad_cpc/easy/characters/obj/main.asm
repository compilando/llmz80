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
	.globl _drawCharacters
	.globl _print256Chars
	.globl _incrementedVideoPos
	.globl _cpct_setVideoMode
	.globl _cpct_drawCharM2
	.globl _cpct_drawCharM1
	.globl _cpct_drawCharM0
	.globl _cpct_setDrawCharM2
	.globl _cpct_setDrawCharM1
	.globl _cpct_setDrawCharM0
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
;src/main.c:25: u8* incrementedVideoPos(u8* pvideomem, u8 inc) {
;	---------------------------------
; Function incrementedVideoPos
; ---------------------------------
_incrementedVideoPos::
	push	ix
	ld	ix,#0
	add	ix,sp
;src/main.c:27: pvideomem += inc;
	ld	a, 4 (ix)
	add	a, 6 (ix)
	ld	4 (ix), a
	ld	a, 5 (ix)
	adc	a, #0x00
	ld	5 (ix), a
;src/main.c:32: if (pvideomem > (u8*)0xC7D0)
	ld	a, #0xd0
	cp	a, 4 (ix)
	ld	a, #0xc7
	sbc	a, 5 (ix)
	jr	NC,00102$
;src/main.c:33: pvideomem = (u8*)CPCT_VMEM_START;
	ld	4 (ix), #0x00
	ld	5 (ix), #0xc0
00102$:
;src/main.c:36: return pvideomem;
	ld	l,4 (ix)
	ld	h,5 (ix)
	pop	ix
	ret
;src/main.c:42: void print256Chars(u8 **pvideomem, u8 mode, u8 fg_colour, u8 bg_colour) {
;	---------------------------------
; Function print256Chars
; ---------------------------------
_print256Chars::
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	hl, #-12
	add	hl, sp
;src/main.c:43: const u8 increments[3] = { 4, 2, 1 };
	ld	sp, hl
	inc	hl
	inc	hl
	ld	c,l
	ld	b,h
	ld	(hl),#0x04
	ld	l, c
	ld	h, b
	inc	hl
	ld	(hl), #0x02
	ld	l, c
	ld	h, b
	inc	hl
	inc	hl
	ld	(hl), #0x01
;src/main.c:48: increment = increments[mode];
	ld	l,6 (ix)
	ld	h,#0x00
	add	hl, bc
	ld	a, (hl)
	ld	-12 (ix), a
;src/main.c:51: switch (mode) {
	ld	a, 6 (ix)
	or	a, a
	jr	NZ,00143$
	ld	a,#0x01
	jr	00144$
00143$:
	xor	a,a
00144$:
	ld	-1 (ix), a
	ld	a, 6 (ix)
	dec	a
	jr	NZ,00145$
	ld	a,#0x01
	jr	00146$
00145$:
	xor	a,a
00146$:
	ld	d, a
	ld	a, 6 (ix)
	sub	a, #0x02
	jr	NZ,00147$
	ld	a,#0x01
	jr	00148$
00147$:
	xor	a,a
00148$:
	ld	e, a
	ld	a, -1 (ix)
	or	a,a
	jr	NZ,00103$
	or	a,d
	jr	NZ,00102$
	or	a,e
	jr	Z,00120$
;src/main.c:52: case 2: cpct_setDrawCharM2(fg_colour, bg_colour);  break;
	push	de
	ld	h, 8 (ix)
	ld	l, 7 (ix)
	push	hl
	call	_cpct_setDrawCharM2
	pop	de
	jr	00120$
;src/main.c:53: case 1: cpct_setDrawCharM1(fg_colour, bg_colour);  break;
00102$:
	push	de
	ld	h, 8 (ix)
	ld	l, 7 (ix)
	push	hl
	call	_cpct_setDrawCharM1
	pop	de
	jr	00120$
;src/main.c:54: case 0: cpct_setDrawCharM0(fg_colour, bg_colour);  break;
00103$:
	push	de
	ld	h, 8 (ix)
	ld	l, 7 (ix)
	push	hl
	call	_cpct_setDrawCharM0
	pop	de
;src/main.c:58: for(charnum=1; charnum != 0; charnum++) {
00120$:
	ld	-7 (ix), d
	ld	c,4 (ix)
	ld	b,5 (ix)
	ld	-3 (ix), c
	ld	-2 (ix), b
	ld	-5 (ix), c
	ld	-4 (ix), b
	ld	-6 (ix), e
	ld	-11 (ix), #0x01
00110$:
;src/main.c:60: case 2: cpct_drawCharM2  (*pvideomem, charnum); break;
	ld	e, -11 (ix)
	ld	d, #0x00
;src/main.c:59: switch (mode) {
	ld	a, -1 (ix)
	or	a, a
	jr	NZ,00107$
	ld	a, -7 (ix)
	or	a, a
	jr	NZ,00106$
	ld	a, -6 (ix)
	or	a, a
	jr	Z,00108$
;src/main.c:60: case 2: cpct_drawCharM2  (*pvideomem, charnum); break;
	ld	l,-5 (ix)
	ld	h,-4 (ix)
	ld	a, (hl)
	inc	hl
	ld	h, (hl)
	ld	l, a
	push	bc
	push	de
	push	hl
	call	_cpct_drawCharM2
	pop	bc
	jr	00108$
;src/main.c:61: case 1: cpct_drawCharM1  (*pvideomem, charnum); break;
00106$:
	ld	l,-3 (ix)
	ld	h,-2 (ix)
	ld	a, (hl)
	inc	hl
	ld	h, (hl)
	ld	l, a
	push	bc
	push	de
	push	hl
	call	_cpct_drawCharM1
	pop	bc
	jr	00108$
;src/main.c:62: case 0: cpct_drawCharM0  (*pvideomem, charnum); break;
00107$:
	ld	l, c
	ld	h, b
	ld	a, (hl)
	inc	hl
	ld	h, (hl)
	ld	l, a
	push	bc
	push	de
	push	hl
	call	_cpct_drawCharM0
	pop	bc
;src/main.c:63: }
00108$:
;src/main.c:65: *pvideomem = incrementedVideoPos(*pvideomem, increment);
	ld	l, c
	ld	h, b
	ld	e, (hl)
	inc	hl
	ld	d, (hl)
	push	bc
	ld	a, -12 (ix)
	push	af
	inc	sp
	push	de
	call	_incrementedVideoPos
	pop	af
	inc	sp
	ex	de,hl
	pop	bc
	ld	l, c
	ld	h, b
	ld	(hl), e
	inc	hl
	ld	(hl), d
;src/main.c:58: for(charnum=1; charnum != 0; charnum++) {
	inc	-11 (ix)
	ld	a, -11 (ix)
	or	a, a
	jr	NZ,00110$
	ld	sp, ix
	pop	ix
	ret
;src/main.c:73: void drawCharacters(u8** pvideomem, u8 maxtimes, u8 mode, u8* fg_colour, u8* bg_colour) {
;	---------------------------------
; Function drawCharacters
; ---------------------------------
_drawCharacters::
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	hl, #-6
	add	hl, sp
	ld	sp, hl
;src/main.c:75: const u8 colours[3] = { 16, 4, 2 };  // Number of colour each mode has (0 = 16, 1 = 4, 2 = 2)
	ld	hl, #0x0000
	add	hl, sp
	ld	c,l
	ld	b,h
	ld	(hl),#0x10
	ld	l, c
	ld	h, b
	inc	hl
	ld	(hl), #0x04
	ld	l, c
	ld	h, b
	inc	hl
	inc	hl
	ld	(hl), #0x02
;src/main.c:77: cpct_clearScreen(0);     // Clear Screen filling up with 0's
	push	bc
	ld	hl, #0x4000
	push	hl
	xor	a, a
	push	af
	inc	sp
	ld	h, #0xc0
	push	hl
	call	_cpct_memset
	ld	l, 7 (ix)
	call	_cpct_setVideoMode
	pop	bc
;src/main.c:81: for(times=0; times < maxtimes; times++) {
	ld	a, 7 (ix)
	add	a, c
	ld	-2 (ix), a
	ld	a, #0x00
	adc	a, b
	ld	-1 (ix), a
	ld	e,10 (ix)
	ld	d,11 (ix)
	ld	c, #0x00
00107$:
	ld	a, c
	sub	a, 6 (ix)
	jr	NC,00109$
;src/main.c:84: if (++(*fg_colour) == colours[mode]) {
	push	hl
	ld	l, 8 (ix)
	ld	h, 9 (ix)
	push	hl
	pop	iy
	pop	hl
	inc	0 (iy)
	ld	b, 0 (iy)
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	ld	a, (hl)
	sub	a, b
	jr	NZ,00104$
;src/main.c:85: *fg_colour = 0;
	ld	0 (iy), #0x00
;src/main.c:86: if (++(*bg_colour) == colours[mode])
	ld	a, (de)
	ld	b, a
	inc	b
	ld	a, b
	ld	(de), a
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	ld	a, (hl)
	ld	-3 (ix), a
	ld	a, b
	sub	a, -3 (ix)
	jr	NZ,00104$
;src/main.c:87: *bg_colour = 0;
	xor	a, a
	ld	(de), a
00104$:
;src/main.c:91: print256Chars(pvideomem, mode, *fg_colour, *bg_colour);
	ld	a, (de)
	ld	b, 0 (iy)
	push	bc
	push	de
	push	af
	inc	sp
	push	bc
	inc	sp
	ld	a, 7 (ix)
	push	af
	inc	sp
	ld	l,4 (ix)
	ld	h,5 (ix)
	push	hl
	call	_print256Chars
	pop	af
	pop	af
	inc	sp
	pop	de
	pop	bc
;src/main.c:81: for(times=0; times < maxtimes; times++) {
	inc	c
	jr	00107$
00109$:
	ld	sp, ix
	pop	ix
	ret
;src/main.c:98: void main(void) {
;	---------------------------------
; Function main
; ---------------------------------
_main::
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	hl, #-22
	add	hl, sp
	ld	sp, hl
;src/main.c:99: u8* pvideomem  = CPCT_VMEM_START; // Pointer to video memory
	ld	hl, #0xc000
	ex	(sp), hl
;src/main.c:100: u8  colours[6] = {0};             // 6 variables for 3 pairs of foreground / background colour
	ld	hl, #0x0002
	add	hl, sp
	ld	c, l
	ld	b, h
	xor	a, a
	ld	(bc), a
	ld	hl, #0x0001
	add	hl,bc
	ld	-2 (ix), l
	ld	-1 (ix), h
	ld	(hl), #0x00
	ld	hl, #0x0002
	add	hl,bc
	ld	-12 (ix), l
	ld	-11 (ix), h
	ld	(hl), #0x00
	ld	hl, #0x0003
	add	hl,bc
	ld	-6 (ix), l
	ld	-5 (ix), h
	ld	(hl), #0x00
	ld	hl, #0x0004
	add	hl,bc
	ld	-14 (ix), l
	ld	-13 (ix), h
	ld	(hl), #0x00
	ld	hl, #0x0005
	add	hl,bc
	ld	-4 (ix), l
	ld	-3 (ix), h
	ld	(hl), #0x00
;src/main.c:104: cpct_disableFirmware();
	push	bc
	call	_cpct_disableFirmware
	pop	bc
;src/main.c:108: while(1) {
00102$:
;src/main.c:109: drawCharacters(&pvideomem, 14, 2, (colours+0), (colours+1)); // Drawing on mode 2, 14 times
	ld	e,-2 (ix)
	ld	d,-1 (ix)
	ld	-10 (ix), c
	ld	-9 (ix), b
	ld	hl, #0x0000
	add	hl, sp
	ld	-8 (ix), l
	ld	-7 (ix), h
	push	bc
	push	de
	ld	e,-10 (ix)
	ld	d,-9 (ix)
	push	de
	ld	de, #0x020e
	push	de
	push	hl
	call	_drawCharacters
	ld	hl, #8
	add	hl, sp
	ld	sp, hl
	pop	bc
;src/main.c:110: drawCharacters(&pvideomem, 17, 1, (colours+2), (colours+3)); // Drawing on mode 1, 17 times
	ld	e,-6 (ix)
	ld	d,-5 (ix)
	push	de
	pop	iy
	ld	l,-12 (ix)
	ld	h,-11 (ix)
	ld	e,-8 (ix)
	ld	d,-7 (ix)
	push	bc
	push	iy
	push	hl
	ld	hl, #0x0111
	push	hl
	push	de
	call	_drawCharacters
	ld	hl, #8
	add	hl, sp
	ld	sp, hl
	pop	bc
;src/main.c:111: drawCharacters(&pvideomem, 21, 0, (colours+4), (colours+5)); // Drawing on mode 0, 21 times
	ld	e,-4 (ix)
	ld	d,-3 (ix)
	push	de
	pop	iy
	ld	l,-14 (ix)
	ld	h,-13 (ix)
	ld	e,-8 (ix)
	ld	d,-7 (ix)
	push	bc
	push	iy
	push	hl
	ld	hl, #0x0015
	push	hl
	push	de
	call	_drawCharacters
	ld	hl, #8
	add	hl, sp
	ld	sp, hl
	pop	bc
	jr	00102$
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
