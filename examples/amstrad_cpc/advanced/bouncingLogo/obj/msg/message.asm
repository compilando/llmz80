;--------------------------------------------------------
; File Created by SDCC : free open source ANSI-C Compiler
; Version 3.6.8 #9946 (Linux)
;--------------------------------------------------------
	.module message
	.optsdcc -mz80
	
;--------------------------------------------------------
; Public variables in this module
;--------------------------------------------------------
	.globl _cpct_drawStringM0
	.globl _cpct_setDrawCharM0
	.globl _g_message
	.globl _drawMessage
	.globl _strcpy
	.globl _concatNum
;--------------------------------------------------------
; special function registers
;--------------------------------------------------------
;--------------------------------------------------------
; ram data
;--------------------------------------------------------
	.area _DATA
_g_message::
	.ds 17
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
;src/msg/message.c:26: void drawMessage() {
;	---------------------------------
; Function drawMessage
; ---------------------------------
_drawMessage::
;src/msg/message.c:28: if (g_message.time > 1) {
	ld	bc, #_g_message+0
	ld	hl, #(_g_message + 0x0010) + 0
	ld	e, (hl)
;src/msg/message.c:31: cpct_drawStringM0(g_message.str, g_message.videopos);
;src/msg/message.c:28: if (g_message.time > 1) {
	ld	a, #0x01
	sub	a, e
	jr	NC,00104$
;src/msg/message.c:30: cpct_setDrawCharM0(1, 0);
	push	bc
	ld	hl, #0x0001
	push	hl
	call	_cpct_setDrawCharM0
;src/msg/message.c:31: cpct_drawStringM0(g_message.str, g_message.videopos);
	pop	hl
	ld	c, (hl)
	inc	hl
	ld	b, (hl)
	push	bc
	ld	hl, #(_g_message + 0x0002)
	push	hl
	call	_cpct_drawStringM0
;src/msg/message.c:32: g_message.time--;
	ld	hl, #(_g_message + 0x0010) + 0
	ld	c, (hl)
	dec	c
	ld	hl, #(_g_message + 0x0010)
	ld	(hl), c
	ret
00104$:
;src/msg/message.c:33: } else if (g_message.time > 0) {
	ld	a, e
	or	a, a
	ret	Z
;src/msg/message.c:35: cpct_setDrawCharM0(0, 0);
	push	bc
	ld	hl, #0x0000
	push	hl
	call	_cpct_setDrawCharM0
;src/msg/message.c:36: cpct_drawStringM0(g_message.str, g_message.videopos);
	pop	hl
	ld	c, (hl)
	inc	hl
	ld	b, (hl)
	push	bc
	ld	hl, #(_g_message + 0x0002)
	push	hl
	call	_cpct_drawStringM0
;src/msg/message.c:37: g_message.time=0;
	ld	hl, #(_g_message + 0x0010)
	ld	(hl), #0x00
	ret
;src/msg/message.c:44: void strcpy(i8* to, const i8* from){
;	---------------------------------
; Function strcpy
; ---------------------------------
_strcpy::
;src/msg/message.c:45: while (*to++ = *from++);
	ld	hl, #4
	add	hl, sp
	ld	c, (hl)
	inc	hl
	ld	b, (hl)
	ld	hl, #2
	add	hl, sp
	ld	e, (hl)
	inc	hl
	ld	d, (hl)
00101$:
	ld	a, (bc)
	inc	bc
	ld	(de), a
	inc	de
	or	a, a
	jr	NZ,00101$
	ret
;src/msg/message.c:52: void concatNum (i8* to, i8 num) {
;	---------------------------------
; Function concatNum
; ---------------------------------
_concatNum::
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	hl, #-6
	add	hl, sp
	ld	sp, hl
;src/msg/message.c:53: i8 digits[5] = { 32, 48, 48, 48, 0 };
	ld	hl, #0x0001
	add	hl, sp
	ld	c,l
	ld	b,h
	ld	(hl),#0x20
	ld	l, c
	ld	h, b
	inc	hl
	ld	(hl), #0x30
	ld	l, c
	ld	h, b
	inc	hl
	inc	hl
	ld	(hl), #0x30
	ld	l, c
	ld	h, b
	inc	hl
	inc	hl
	inc	hl
	ld	(hl), #0x30
	ld	hl, #0x0004
	add	hl, bc
	ld	(hl), #0x00
;src/msg/message.c:57: if (num < 0) {
	bit	7, 6 (ix)
	jr	Z,00102$
;src/msg/message.c:58: unum = -num;
	xor	a, a
	sub	a, 6 (ix)
	ld	d, a
;src/msg/message.c:59: digits[0]=45;
	ld	a, #0x2d
	ld	(bc), a
	jr	00113$
00102$:
;src/msg/message.c:61: unum = num;
	ld	d, 6 (ix)
;src/msg/message.c:65: for (d=3; d != 0; --d) {
00113$:
	ld	e, #0x03
00106$:
;src/msg/message.c:66: u8 r=unum % 10;
	push	bc
	push	de
	ld	a, #0x0a
	push	af
	inc	sp
	push	de
	inc	sp
	call	__moduchar
	pop	af
	pop	de
;src/msg/message.c:67: unum /= 10;
	ld	-6 (ix), l
	push	de
	ld	a, #0x0a
	push	af
	inc	sp
	push	de
	inc	sp
	call	__divuchar
	pop	af
	pop	de
	pop	bc
	ld	d, l
;src/msg/message.c:68: digits[d]=48 + r;
	ld	l,e
	ld	h,#0x00
	add	hl, bc
	ld	a, -6 (ix)
	add	a, #0x30
	ld	(hl), a
;src/msg/message.c:65: for (d=3; d != 0; --d) {
	dec e
	jr	NZ,00106$
;src/msg/message.c:73: for (d=0; d<5; d++){
	ld	e, 4 (ix)
	ld	d, 5 (ix)
	push	de
	pop	iy
	ld	e, #0x00
00108$:
;src/msg/message.c:74: *to++ = digits[d];
	ld	l,e
	ld	h,#0x00
	add	hl, bc
	ld	d, (hl)
	ld	0 (iy), d
	inc	iy
;src/msg/message.c:73: for (d=0; d<5; d++){
	inc	e
	ld	a, e
	sub	a, #0x05
	jr	C,00108$
	ld	sp, ix
	pop	ix
	ret
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
