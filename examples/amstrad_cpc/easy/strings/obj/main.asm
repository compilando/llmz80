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
	.globl _wait_frames
	.globl _cpct_waitVSYNC
	.globl _cpct_setVideoMode
	.globl _cpct_drawStringM2
	.globl _cpct_drawStringM1
	.globl _cpct_drawStringM0
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
;src/main.c:30: void wait_frames(u16 nframes) {
;	---------------------------------
; Function wait_frames
; ---------------------------------
_wait_frames::
	push	ix
	ld	ix,#0
	add	ix,sp
;src/main.c:34: for (i=0; i < nframes; i++) {
	ld	bc, #0x0000
00107$:
	ld	a, c
	sub	a, 4 (ix)
	ld	a, b
	sbc	a, 5 (ix)
	jr	NC,00109$
;src/main.c:35: cpct_waitVSYNC();
	push	bc
	call	_cpct_waitVSYNC
	pop	bc
;src/main.c:42: for (j=0; j < 750; j++);
	ld	de, #0x02ee
00105$:
	ex	de,hl
	dec	hl
	ld	e, l
	ld	a,h
	ld	d,a
	or	a,l
	jr	NZ,00105$
;src/main.c:34: for (i=0; i < nframes; i++) {
	inc	bc
	jr	00107$
00109$:
	pop	ix
	ret
;src/main.c:49: void main(void) {
;	---------------------------------
; Function main
; ---------------------------------
_main::
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	hl, #-22
	add	hl, sp
;src/main.c:52: u8 colours[6] = {0};  // 5 Colour values, 2 for each mode
	ld	sp, hl
	inc	hl
	inc	hl
	ld	-2 (ix), l
	ld	-1 (ix), h
	ld	(hl), #0x00
	ld	a, -2 (ix)
	add	a, #0x01
	ld	-5 (ix), a
	ld	a, -1 (ix)
	adc	a, #0x00
	ld	-4 (ix), a
	ld	l,-5 (ix)
	ld	h,-4 (ix)
	ld	(hl), #0x00
	ld	a, -2 (ix)
	add	a, #0x02
	ld	-13 (ix), a
	ld	a, -1 (ix)
	adc	a, #0x00
	ld	-12 (ix), a
	ld	l,-13 (ix)
	ld	h,-12 (ix)
	ld	(hl), #0x00
	ld	a, -2 (ix)
	add	a, #0x03
	ld	-11 (ix), a
	ld	a, -1 (ix)
	adc	a, #0x00
	ld	-10 (ix), a
	ld	l,-11 (ix)
	ld	h,-10 (ix)
	ld	(hl), #0x00
	ld	a, -2 (ix)
	add	a, #0x04
	ld	-9 (ix), a
	ld	a, -1 (ix)
	adc	a, #0x00
	ld	-8 (ix), a
	ld	l,-9 (ix)
	ld	h,-8 (ix)
	ld	(hl), #0x00
	ld	a, -2 (ix)
	add	a, #0x05
	ld	-7 (ix), a
	ld	a, -1 (ix)
	adc	a, #0x00
	ld	-6 (ix), a
	ld	l,-7 (ix)
	ld	h,-6 (ix)
	ld	(hl), #0x00
;src/main.c:56: cpct_disableFirmware();
	call	_cpct_disableFirmware
;src/main.c:60: while(1) {
00105$:
;src/main.c:67: cpct_clearScreen(0);
	ld	hl, #0x4000
	push	hl
	xor	a, a
	push	af
	inc	sp
	ld	h, #0xc0
	push	hl
	call	_cpct_memset
;src/main.c:68: cpct_setVideoMode(0);
	ld	l, #0x00
	call	_cpct_setVideoMode
;src/main.c:74: for (times=0; times < 25; times++) {
	ld	hl, #0xc000
	ex	(sp), hl
	ld	-14 (ix), #0x00
00107$:
;src/main.c:78: colours[0] = ++colours[0] & 15;
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	ld	a, (hl)
	ld	-3 (ix), a
	inc	a
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	ld	(hl), a
	and	a, #0x0f
	ld	b, a
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	ld	(hl), b
;src/main.c:81: cpct_setDrawCharM0(colours[0], colours[3]);
	ld	l,-11 (ix)
	ld	h,-10 (ix)
	ld	d, (hl)
	ld	e, b
	push	de
	call	_cpct_setDrawCharM0
;src/main.c:82: cpct_drawStringM0("$ Mode 0 string $", pvideomem);
	pop	bc
	push	bc
	push	bc
	ld	hl, #___str_0
	push	hl
	call	_cpct_drawStringM0
;src/main.c:83: wait_frames(WFRAMES);
	ld	hl, #0x0003
	push	hl
	call	_wait_frames
	pop	af
;src/main.c:86: pvideomem += 0x50;
	ld	a, -22 (ix)
	add	a, #0x50
	ld	-22 (ix), a
	ld	a, -21 (ix)
	adc	a, #0x00
	ld	-21 (ix), a
;src/main.c:74: for (times=0; times < 25; times++) {
	inc	-14 (ix)
	ld	a, -14 (ix)
	sub	a, #0x19
	jr	C,00107$
;src/main.c:89: colours[3] = ++colours[3] & 15;
	ld	l,-11 (ix)
	ld	h,-10 (ix)
	ld	a, (hl)
	inc	a
	ld	l,-11 (ix)
	ld	h,-10 (ix)
	ld	(hl), a
	and	a, #0x0f
	ld	l,-11 (ix)
	ld	h,-10 (ix)
	ld	(hl), a
;src/main.c:96: cpct_clearScreen(0);
	ld	hl, #0x4000
	push	hl
	xor	a, a
	push	af
	inc	sp
	ld	h, #0xc0
	push	hl
	call	_cpct_memset
;src/main.c:97: cpct_setVideoMode(1);
	ld	l, #0x01
	call	_cpct_setVideoMode
;src/main.c:103: for (times=0; times < 25; times++) {
	ld	bc, #0xc000
	ld	-14 (ix), #0x00
00109$:
;src/main.c:106: colours[1] = ++colours[1] & 3;
	ld	l,-5 (ix)
	ld	h,-4 (ix)
	ld	a, (hl)
	inc	a
	ld	l,-5 (ix)
	ld	h,-4 (ix)
	ld	(hl), a
	and	a, #0x03
	ld	d, a
	ld	l,-5 (ix)
	ld	h,-4 (ix)
	ld	(hl), d
;src/main.c:109: cpct_setDrawCharM1(colours[1], colours[4]);
	ld	l,-9 (ix)
	ld	h,-8 (ix)
	ld	h, (hl)
	push	bc
	ld	l, d
	push	hl
	call	_cpct_setDrawCharM1
	pop	bc
;src/main.c:110: cpct_drawStringM1("Mode 1 string :D", pvideomem);
	ld	e, c
	ld	d, b
	push	bc
	push	de
	ld	hl, #___str_1
	push	hl
	call	_cpct_drawStringM1
	pop	bc
;src/main.c:112: colours[1] = ++colours[1] & 3;
	ld	l,-5 (ix)
	ld	h,-4 (ix)
	ld	a, (hl)
	inc	a
	ld	l,-5 (ix)
	ld	h,-4 (ix)
	ld	(hl), a
	and	a, #0x03
	ld	d, a
	ld	l,-5 (ix)
	ld	h,-4 (ix)
	ld	(hl), d
;src/main.c:113: cpct_setDrawCharM1(colours[1], colours[4]);
	ld	l,-9 (ix)
	ld	h,-8 (ix)
	ld	h, (hl)
	push	bc
	ld	l, d
	push	hl
	call	_cpct_setDrawCharM1
	pop	bc
;src/main.c:114: cpct_drawStringM1("Mode 1 string :D", pvideomem + 38);
	ld	hl, #0x0026
	add	hl, bc
	push	bc
	push	hl
	ld	hl, #___str_1
	push	hl
	call	_cpct_drawStringM1
	pop	bc
;src/main.c:117: colours[1] = ++colours[1] & 3;
	ld	l,-5 (ix)
	ld	h,-4 (ix)
	ld	a, (hl)
	inc	a
	ld	l,-5 (ix)
	ld	h,-4 (ix)
	ld	(hl), a
	and	a, #0x03
	ld	l,-5 (ix)
	ld	h,-4 (ix)
	ld	(hl), a
;src/main.c:118: wait_frames(WFRAMES);
	push	bc
	ld	hl, #0x0003
	push	hl
	call	_wait_frames
	pop	af
	pop	bc
;src/main.c:121: pvideomem += 0x50;
	ld	hl, #0x0050
	add	hl,bc
	ld	c, l
	ld	b, h
;src/main.c:103: for (times=0; times < 25; times++) {
	inc	-14 (ix)
	ld	a, -14 (ix)
	sub	a, #0x19
	jp	C, 00109$
;src/main.c:123: colours[4] = ++colours[4] & 3;
	ld	l,-9 (ix)
	ld	h,-8 (ix)
	ld	a, (hl)
	inc	a
	ld	l,-9 (ix)
	ld	h,-8 (ix)
	ld	(hl), a
	and	a, #0x03
	ld	l,-9 (ix)
	ld	h,-8 (ix)
	ld	(hl), a
;src/main.c:130: cpct_clearScreen(0);
	ld	hl, #0x4000
	push	hl
	xor	a, a
	push	af
	inc	sp
	ld	h, #0xc0
	push	hl
	call	_cpct_memset
;src/main.c:131: cpct_setVideoMode(2);
	ld	l, #0x02
	call	_cpct_setVideoMode
;src/main.c:137: for (times=0; times < 25; times++) {
	ld	bc, #0xc000
	ld	-14 (ix), #0x00
00111$:
;src/main.c:140: colours[2] ^= 1;
	ld	l,-13 (ix)
	ld	h,-12 (ix)
	ld	a, (hl)
	xor	a, #0x01
	ld	d, a
	ld	l,-13 (ix)
	ld	h,-12 (ix)
	ld	(hl), d
;src/main.c:143: cpct_setDrawCharM2(colours[2], colours[5]);
	ld	l,-7 (ix)
	ld	h,-6 (ix)
	ld	h, (hl)
	push	bc
	ld	l, d
	push	hl
	call	_cpct_setDrawCharM2
	pop	bc
;src/main.c:144: cpct_drawStringM2("And, finally, this is a long mode 2 string!!", pvideomem);
	ld	e, c
	ld	d, b
	push	bc
	push	de
	ld	hl, #___str_2
	push	hl
	call	_cpct_drawStringM2
	ld	hl, #0x0003
	push	hl
	call	_wait_frames
	pop	af
	pop	bc
;src/main.c:148: pvideomem += 0x50;
	ld	hl, #0x0050
	add	hl,bc
	ld	c, l
	ld	b, h
;src/main.c:137: for (times=0; times < 25; times++) {
	inc	-14 (ix)
	ld	a, -14 (ix)
	sub	a, #0x19
	jr	C,00111$
;src/main.c:151: colours[5] ^= 1;
	ld	l,-7 (ix)
	ld	h,-6 (ix)
	ld	a, (hl)
	xor	a, #0x01
	ld	l,-7 (ix)
	ld	h,-6 (ix)
	ld	(hl), a
	jp	00105$
___str_0:
	.ascii "$ Mode 0 string $"
	.db 0x00
___str_1:
	.ascii "Mode 1 string :D"
	.db 0x00
___str_2:
	.ascii "And, finally, this is a long mode 2 string!!"
	.db 0x00
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
