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
	.globl _scrollLine
	.globl _wait_n_VSYNCs
	.globl _strlen
	.globl _cpct_waitVSYNC
	.globl _cpct_drawStringM1
	.globl _cpct_drawCharM1
	.globl _cpct_setDrawCharM1
	.globl _cpct_isAnyKeyPressed_f
	.globl _cpct_scanKeyboard_f
	.globl _cpct_memcpy
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
;src/main.c:37: void wait_n_VSYNCs(u8 n) {
;	---------------------------------
; Function wait_n_VSYNCs
; ---------------------------------
_wait_n_VSYNCs::
;src/main.c:38: do {
	ld	hl, #2+0
	add	hl, sp
	ld	c, (hl)
00103$:
;src/main.c:40: cpct_waitVSYNC();
	push	bc
	call	_cpct_waitVSYNC
	pop	bc
;src/main.c:45: if (--n) {
	dec	c
	ld	a, c
	or	a, a
	jr	Z,00104$
;src/main.c:46: __asm__("halt");
	halt
;src/main.c:47: __asm__("halt");
	halt
00104$:
;src/main.c:49: } while(n);
	ld	a, c
	or	a, a
	jr	NZ,00103$
	ret
;src/main.c:58: void scrollLine(u8* pCharline, u16 lineSize) {
;	---------------------------------
; Function scrollLine
; ---------------------------------
_scrollLine::
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	l,4 (ix)
	ld	h,5 (ix)
00103$:
;src/main.c:62: for (; pCharline > CPCT_VMEM_START; pCharline += PIXEL_LINE_OFFSET)
	xor	a, a
	cp	a, l
	ld	a, #0xc0
	sbc	a, h
	jr	NC,00105$
;src/main.c:63: cpct_memcpy(pCharline, pCharline+1, lineSize);
	ld	c, l
	ld	b, h
	inc	bc
	push	hl
	pop	iy
	push	hl
	ld	e,6 (ix)
	ld	d,7 (ix)
	push	de
	push	bc
	push	iy
	call	_cpct_memcpy
	pop	hl
;src/main.c:62: for (; pCharline > CPCT_VMEM_START; pCharline += PIXEL_LINE_OFFSET)
	ld	bc, #0x0800
	add	hl, bc
	jr	00103$
00105$:
	pop	ix
	ret
;src/main.c:69: void main(void) {
;	---------------------------------
; Function main
; ---------------------------------
_main::
	push	ix
	ld	ix,#0
	add	ix,sp
	push	af
	dec	sp
;src/main.c:72: const u8 *text="This is a simple software scrolling mode 1 text. Not really smooth, but easy to understand.     ";
	ld	bc, #___str_0+0
;src/main.c:78: u8* pCharline_start = CPCT_VMEM_START + (PIXEL_LINE_SIZE * CHARLINE);
	ld	hl, #0xc3c0
	ex	(sp), hl
;src/main.c:84: const u8 textlen=strlen(text);  // Save the lenght of the text for later use
	push	bc
	push	bc
	call	_strlen
	pop	af
	pop	bc
	ld	-1 (ix), l
;src/main.c:85: u8 nextChar=0;                  // Next character of the text to be drawn on the screen
;src/main.c:86: u8 penColour=1;                 // Pen colour for the characters
	ld	de,#0x0100
;src/main.c:89: cpct_setDrawCharM1(1, 3);
	push	bc
	push	de
	ld	hl, #0x0301
	push	hl
	call	_cpct_setDrawCharM1
	ld	hl, #0xc000
	push	hl
	ld	hl, #___str_1
	push	hl
	call	_cpct_drawStringM1
	ld	hl, #0x0001
	push	hl
	call	_cpct_setDrawCharM1
	pop	de
	pop	bc
;src/main.c:95: do { cpct_scanKeyboard_f(); } while( cpct_isAnyKeyPressed_f() );
00101$:
	push	bc
	push	de
	call	_cpct_scanKeyboard_f
	call	_cpct_isAnyKeyPressed_f
	pop	de
	pop	bc
	ld	a, l
	or	a, a
	jr	NZ,00101$
;src/main.c:99: cpct_drawCharM1(pNextCharLocation, text[nextChar]);
	ld	l,e
	ld	h,#0x00
	add	hl, bc
	ld	l, (hl)
	ld	h, #0x00
	push	bc
	push	de
	push	hl
	ld	hl, #0xc40e
	push	hl
	call	_cpct_drawCharM1
	pop	de
	pop	bc
;src/main.c:104: if (++nextChar == textlen) {
	inc	e
	ld	a, -1 (ix)
;src/main.c:105: nextChar = 0;
	sub	a,e
	jr	NZ,00107$
	ld	e,a
;src/main.c:106: if (++penColour > 3) penColour = 1;
	inc	d
	ld	a, #0x03
	sub	a, d
	jr	NC,00105$
	ld	d, #0x01
00105$:
;src/main.c:107: cpct_setDrawCharM1(penColour, 0);
	push	bc
	push	de
	xor	a, a
	push	af
	inc	sp
	push	de
	inc	sp
	call	_cpct_setDrawCharM1
	pop	de
	pop	bc
00107$:
;src/main.c:113: wait_n_VSYNCs(2);
	push	bc
	push	de
	ld	a, #0x02
	push	af
	inc	sp
	call	_wait_n_VSYNCs
	inc	sp
	ld	hl, #0x0050
	push	hl
	ld	l,-3 (ix)
	ld	h,-2 (ix)
	push	hl
	call	_scrollLine
	pop	af
	ld	h,#0x02
	ex	(sp),hl
	inc	sp
	call	_wait_n_VSYNCs
	inc	sp
	ld	hl, #0x0050
	push	hl
	ld	l,-3 (ix)
	ld	h,-2 (ix)
	push	hl
	call	_scrollLine
	pop	af
	pop	af
	pop	de
	pop	bc
	jr	00101$
___str_0:
	.ascii "This is a simple software scrolling mode 1 text. Not really "
	.ascii "smooth, but easy to understand.     "
	.db 0x00
___str_1:
	.ascii "Hold any key to pause scroll"
	.db 0x00
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
