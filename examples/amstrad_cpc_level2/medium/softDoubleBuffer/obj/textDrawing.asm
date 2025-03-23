;--------------------------------------------------------
; File Created by SDCC : free open source ANSI-C Compiler
; Version 3.6.8 #9946 (Linux)
;--------------------------------------------------------
	.module textDrawing
	.optsdcc -mz80
	
;--------------------------------------------------------
; Public variables in this module
;--------------------------------------------------------
	.globl _DrawSelectionToBuffer
	.globl _DrawInfoTextToBuffer
	.globl _cpct_getScreenPtr
	.globl _cpct_drawStringM1
	.globl _cpct_setDrawCharM1
	.globl _cpct_drawSolidBox
	.globl _DrawInfoText
	.globl _DrawTextSelectionSign
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
;src/textDrawing.c:31: void DrawInfoTextToBuffer(u8* bufferPtr) {
;	---------------------------------
; Function DrawInfoTextToBuffer
; ---------------------------------
_DrawInfoTextToBuffer::
	push	ix
	ld	ix,#0
	add	ix,sp
	push	af
	dec	sp
;src/textDrawing.c:53: for (i = 0; i < NB_MESSAGES; ++i) {
	ld	-1 (ix), #0x00
00102$:
;src/textDrawing.c:55: TTextData const* t = messages + i;
	ld	c,-1 (ix)
	ld	b,#0x00
	ld	l, c
	ld	h, b
	add	hl, hl
	add	hl, bc
	add	hl, hl
	ld	de, #_DrawInfoTextToBuffer_messages_1_135
	add	hl, de
;src/textDrawing.c:59: u8* pvmem = cpct_getScreenPtr(bufferPtr, t->x, t->y);
	ld	c,l
	ld	b,h
	inc	hl
	ld	e, (hl)
	ld	a, (bc)
	ld	h, a
	ld	l, 4 (ix)
	ld	d, 5 (ix)
	push	bc
	ld	a, e
	push	af
	inc	sp
	push	hl
	inc	sp
	ld	h, d
	push	hl
	call	_cpct_getScreenPtr
	pop	bc
	inc	sp
	inc	sp
	push	hl
;src/textDrawing.c:60: cpct_setDrawCharM1(t->pen, t->paper);
	ld	l, c
	ld	h, b
	inc	hl
	inc	hl
	inc	hl
	ld	d, (hl)
	ld	l, c
	ld	h, b
	inc	hl
	inc	hl
	ld	a, (hl)
	push	bc
	ld	e, a
	push	de
	call	_cpct_setDrawCharM1
	pop	bc
;src/textDrawing.c:61: cpct_drawStringM1(t->text, pvmem);
	pop	de
	push	de
	ld	l, c
	ld	h, b
	ld	bc, #0x0004
	add	hl, bc
	ld	c, (hl)
	inc	hl
	ld	b, (hl)
	push	de
	push	bc
	call	_cpct_drawStringM1
;src/textDrawing.c:53: for (i = 0; i < NB_MESSAGES; ++i) {
	inc	-1 (ix)
	ld	a, -1 (ix)
	sub	a, #0x0a
	jr	C,00102$
	ld	sp, ix
	pop	ix
	ret
_DrawInfoTextToBuffer_messages_1_135:
	.db #0x00	; 0
	.db #0x4b	; 75	'K'
	.db #0x03	; 3
	.db #0x00	; 0
	.dw ___str_0
	.db #0x04	; 4
	.db #0x5f	; 95
	.db #0x01	; 1
	.db #0x00	; 0
	.dw ___str_1
	.db #0x08	; 8
	.db #0x5f	; 95
	.db #0x02	; 2
	.db #0x00	; 0
	.dw ___str_2
	.db #0x08	; 8
	.db #0x69	; 105	'i'
	.db #0x01	; 1
	.db #0x00	; 0
	.dw ___str_3
	.db #0x04	; 4
	.db #0x78	; 120	'x'
	.db #0x01	; 1
	.db #0x00	; 0
	.dw ___str_4
	.db #0x08	; 8
	.db #0x78	; 120	'x'
	.db #0x02	; 2
	.db #0x00	; 0
	.dw ___str_5
	.db #0x08	; 8
	.db #0x82	; 130
	.db #0x01	; 1
	.db #0x00	; 0
	.dw ___str_6
	.db #0x04	; 4
	.db #0x9b	; 155
	.db #0x01	; 1
	.db #0x00	; 0
	.dw ___str_7
	.db #0x08	; 8
	.db #0x9b	; 155
	.db #0x02	; 2
	.db #0x00	; 0
	.dw ___str_8
	.db #0x08	; 8
	.db #0xa5	; 165
	.db #0x01	; 1
	.db #0x00	; 0
	.dw ___str_9
___str_0:
	.ascii "Press"
	.db 0x00
___str_1:
	.ascii "1"
	.db 0x00
___str_2:
	.ascii ": No double buffer"
	.db 0x00
___str_3:
	.ascii "Directly draw in video mem"
	.db 0x00
___str_4:
	.ascii "2"
	.db 0x00
___str_5:
	.ascii ": Hardware double buffer"
	.db 0x00
___str_6:
	.ascii "Draw alternatively in two video mem  (2*16384 bytes) and fli"
	.ascii "p between them"
	.db 0x00
___str_7:
	.ascii "3"
	.db 0x00
___str_8:
	.ascii ": Software double buffer"
	.db 0x00
___str_9:
	.ascii "Draw in buffer (50*60 bytes) of size view and copy whole buf"
	.ascii "fer to video mem (16384 bytes)"
	.db 0x00
;src/textDrawing.c:70: void DrawInfoText() {
;	---------------------------------
; Function DrawInfoText
; ---------------------------------
_DrawInfoText::
;src/textDrawing.c:71: DrawInfoTextToBuffer((u8*)CPCT_VMEM_START);
	ld	hl, #0xc000
	push	hl
	call	_DrawInfoTextToBuffer
;src/textDrawing.c:72: DrawInfoTextToBuffer((u8*)SCREEN_BUFF);
	ld	hl, #0x8000
	ex	(sp),hl
	call	_DrawInfoTextToBuffer
	pop	af
	ret
;src/textDrawing.c:82: void DrawSelectionToBuffer(u8* bufferPtr, u8 pos) {
;	---------------------------------
; Function DrawSelectionToBuffer
; ---------------------------------
_DrawSelectionToBuffer::
	push	ix
	ld	ix,#0
	add	ix,sp
;src/textDrawing.c:87: pvmem = cpct_getScreenPtr(bufferPtr, 0, POS_TEXT + 15);
	ld	c,4 (ix)
	ld	b,5 (ix)
	push	bc
	ld	hl, #0x5f00
	push	hl
	push	bc
	call	_cpct_getScreenPtr
	ld	de, #0x5002
	push	de
	ld	de, #0x0000
	push	de
	push	hl
	call	_cpct_drawSolidBox
	pop	bc
;src/textDrawing.c:91: pvmem = cpct_getScreenPtr(bufferPtr, 0, pos);
	ld	a, 6 (ix)
	push	af
	inc	sp
	xor	a, a
	push	af
	inc	sp
	push	bc
	call	_cpct_getScreenPtr
;src/textDrawing.c:92: cpct_setDrawCharM1(3, 0);
	push	hl
	ld	bc, #0x0003
	push	bc
	call	_cpct_setDrawCharM1
	pop	hl
;src/textDrawing.c:93: cpct_drawStringM1(">", pvmem);
	ld	bc, #___str_10+0
	push	hl
	push	bc
	call	_cpct_drawStringM1
	pop	ix
	ret
___str_10:
	.ascii ">"
	.db 0x00
;src/textDrawing.c:102: void DrawTextSelectionSign(u8 sel) {
;	---------------------------------
; Function DrawTextSelectionSign
; ---------------------------------
_DrawTextSelectionSign::
;src/textDrawing.c:110: u8 pos = locations[sel-1];   // Position of the User selection
	ld	hl, #2+0
	add	hl, sp
	ld	c, (hl)
	dec	c
	ld	hl, #_DrawTextSelectionSign_locations_1_142
	ld	b, #0x00
	add	hl, bc
	ld	b, (hl)
;src/textDrawing.c:113: DrawSelectionToBuffer((u8*)CPCT_VMEM_START, pos);
	push	bc
	push	bc
	inc	sp
	ld	hl, #0xc000
	push	hl
	call	_DrawSelectionToBuffer
	pop	af
	inc	sp
	inc	sp
	ld	hl, #0x8000
	push	hl
	call	_DrawSelectionToBuffer
	pop	af
	inc	sp
	ret
_DrawTextSelectionSign_locations_1_142:
	.db #0x5f	; 95
	.db #0x78	; 120	'x'
	.db #0x9b	; 155
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
