;--------------------------------------------------------
; File Created by SDCC : free open source ANSI-C Compiler
; Version 3.6.8 #9946 (Linux)
;--------------------------------------------------------
	.module keyboard
	.optsdcc -mz80
	
;--------------------------------------------------------
; Public variables in this module
;--------------------------------------------------------
	.globl _updateKeyboardStatus
	.globl _cpct_isKeyPressed
	.globl _cpct_scanKeyboard
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
;src/keyboard.c:27: void updateKeyboardStatus() {
;	---------------------------------
; Function updateKeyboardStatus
; ---------------------------------
_updateKeyboardStatus::
	push	ix
	ld	ix,#0
	add	ix,sp
	push	af
	dec	sp
;src/keyboard.c:32: cpct_scanKeyboard();
	call	_cpct_scanKeyboard
;src/keyboard.c:39: k = g_keys;
	ld	bc, #_g_keys+0
;src/keyboard.c:40: for(i=0; i < G_NKEYS; i++, k++) {
	ld	-3 (ix), #0x00
00113$:
;src/keyboard.c:42: if (cpct_isKeyPressed(k->key)) {
	ld	l, c
	ld	h, b
	ld	e, (hl)
	inc	hl
	ld	h, (hl)
	push	bc
	ld	l, e
	call	_cpct_isKeyPressed
	ld	-1 (ix), l
	pop	bc
;src/keyboard.c:45: switch(k->status) {
	ld	e, c
	ld	d, b
	inc	de
	inc	de
	ld	a, (de)
	ld	l,a
	dec	a
	jr	NZ,00150$
	ld	a,#0x01
	jr	00151$
00150$:
	xor	a,a
00151$:
	ld	h, a
	ld	a, l
	sub	a, #0x03
	jr	NZ,00152$
	ld	a,#0x01
	jr	00153$
00152$:
	xor	a,a
00153$:
	ld	-2 (ix), a
;src/keyboard.c:42: if (cpct_isKeyPressed(k->key)) {
	ld	a, -1 (ix)
	or	a, a
	jr	Z,00110$
;src/keyboard.c:45: switch(k->status) {
	ld	a, l
	or	a, a
	jr	Z,00103$
	ld	a, h
	or	a, a
	jr	NZ,00101$
	ld	a, -2 (ix)
	or	a, a
	jr	NZ,00103$
	jr	00114$
;src/keyboard.c:47: case KeySt_Pressed:  { k->status = KeySt_StillPressed; break; }
00101$:
	ld	a, #0x02
	ld	(de), a
	jr	00114$
;src/keyboard.c:50: case KeySt_Released: { k->status = KeySt_Pressed; }
00103$:
	ld	a, #0x01
	ld	(de), a
;src/keyboard.c:51: }
	jr	00114$
00110$:
;src/keyboard.c:55: switch(k->status) {
	ld	a, h
	or	a, a
	jr	NZ,00106$
	ld	a, l
	sub	a, #0x02
	jr	Z,00106$
	ld	a, -2 (ix)
	or	a, a
	jr	NZ,00107$
	jr	00114$
;src/keyboard.c:58: case KeySt_StillPressed: { k->status = KeySt_Released; break; }
00106$:
	ld	a, #0x03
	ld	(de), a
	jr	00114$
;src/keyboard.c:60: case KeySt_Released:     { k->status = KeySt_Free; }
00107$:
	xor	a, a
	ld	(de), a
;src/keyboard.c:61: }         
00114$:
;src/keyboard.c:40: for(i=0; i < G_NKEYS; i++, k++) {
	inc	-3 (ix)
	inc	bc
	inc	bc
	inc	bc
	inc	bc
	inc	bc
	ld	a, -3 (ix)
	sub	a, #0x04
	jr	C,00113$
	ld	sp, ix
	pop	ix
	ret
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
