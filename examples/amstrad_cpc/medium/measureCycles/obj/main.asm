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
	.globl _cpct_setPALColour
	.globl _cpct_setPalette
	.globl _cpct_fw2hw
	.globl _cpct_count2VSYNC
	.globl _cpct_waitVSYNC
	.globl _cpct_setVideoMode
	.globl _cpct_drawCharM1
	.globl _cpct_setDrawCharM1
	.globl _cpct_drawSprite
	.globl _cpct_isKeyPressed
	.globl _cpct_scanKeyboard_f
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
;src/main.c:31: void main(void) {
;	---------------------------------
; Function main
; ---------------------------------
_main::
	push	ix
	ld	ix,#0
	add	ix,sp
	push	af
	push	af
	dec	sp
;src/main.c:33: u8  x=0, y=0;                    // Sprite coordinates (in bytes)
	ld	-2 (ix), #0x00
	ld	-3 (ix), #0x00
;src/main.c:34: u8* pvideomem = CPCT_VMEM_START; // Sprite initial video memory byte location (where it will be drawn)
	ld	hl, #0xc000
	ex	(sp), hl
;src/main.c:39: cpct_disableFirmware();
	call	_cpct_disableFirmware
;src/main.c:41: cpct_fw2hw     (G_palette, 4);
	ld	hl, #0x0004
	push	hl
	ld	hl, #_G_palette
	push	hl
	call	_cpct_fw2hw
;src/main.c:42: cpct_setPalette(G_palette, 4);
	ld	hl, #0x0004
	push	hl
	ld	hl, #_G_palette
	push	hl
	call	_cpct_setPalette
;src/main.c:43: cpct_setBorder (G_palette[1]);
	ld	hl, #_G_palette + 1
	ld	b, (hl)
	push	bc
	inc	sp
	ld	a, #0x10
	push	af
	inc	sp
	call	_cpct_setPALColour
;src/main.c:44: cpct_setVideoMode(1);         // Ensure MODE 1 is set
	ld	l, #0x01
	call	_cpct_setVideoMode
;src/main.c:45: cpct_setDrawCharM1(3, 0);     // Always draw characters using same colours (3 (Yellow) / 0 (Grey))
	ld	hl, #0x0003
	push	hl
	call	_cpct_setDrawCharM1
;src/main.c:48: while(1) {
00117$:
;src/main.c:50: cpct_scanKeyboard_f();
	call	_cpct_scanKeyboard_f
;src/main.c:51: if      (cpct_isKeyPressed(Key_CursorRight) && x <  80 - SPR_W) { x++; pvideomem++; }
	ld	hl, #0x0200
	call	_cpct_isKeyPressed
	ld	a, l
	or	a, a
	jr	Z,00105$
	ld	a, -2 (ix)
	sub	a, #0x47
	jr	NC,00105$
	inc	-2 (ix)
	inc	-5 (ix)
	jr	NZ,00106$
	inc	-4 (ix)
	jr	00106$
00105$:
;src/main.c:52: else if (cpct_isKeyPressed(Key_CursorLeft)  && x >   0        ) { x--; pvideomem--; }
	ld	hl, #0x0101
	call	_cpct_isKeyPressed
	ld	a, l
	or	a, a
	jr	Z,00106$
	ld	a, -2 (ix)
	or	a, a
	jr	Z,00106$
	dec	-2 (ix)
	pop	hl
	push	hl
	dec	hl
	ex	(sp), hl
00106$:
;src/main.c:53: if      (cpct_isKeyPressed(Key_CursorUp)    && y >   0        ) { pvideomem -= (y-- & 7) ? 0x0800 : 0xC850; }
	ld	hl, #0x0100
	call	_cpct_isKeyPressed
	ld	a, l
	or	a, a
	jr	Z,00112$
	ld	a, -3 (ix)
	or	a, a
	jr	Z,00112$
	ld	c, -3 (ix)
	dec	-3 (ix)
	ld	a, c
	and	a, #0x07
	jr	Z,00123$
	ld	de, #0x0800
	jr	00124$
00123$:
	ld	de, #0xc850
00124$:
	ld	a, -5 (ix)
	sub	a, e
	ld	-5 (ix), a
	ld	a, -4 (ix)
	sbc	a, d
	ld	-4 (ix), a
	jr	00113$
00112$:
;src/main.c:54: else if (cpct_isKeyPressed(Key_CursorDown)  && y < 200 - SPR_H) { pvideomem += (++y & 7) ? 0x0800 : 0xC850; }
	ld	hl, #0x0400
	call	_cpct_isKeyPressed
	ld	a, l
	or	a, a
	jr	Z,00113$
	ld	a, -3 (ix)
	sub	a, #0x9c
	jr	NC,00113$
	inc	-3 (ix)
	ld	a, -3 (ix)
	and	a, #0x07
	jr	Z,00125$
	ld	bc, #0x0800
	jr	00126$
00125$:
	ld	bc, #0xc850
00126$:
	ld	a, -5 (ix)
	add	a, c
	ld	-5 (ix), a
	ld	a, -4 (ix)
	adc	a, b
	ld	-4 (ix), a
00113$:
;src/main.c:58: cpct_waitVSYNC();
	call	_cpct_waitVSYNC
;src/main.c:63: cpct_drawSprite(G_death, pvideomem, SPR_W, SPR_H);
	pop	bc
	push	bc
	ld	hl, #0x2c09
	push	hl
	push	bc
	ld	hl, #_G_death
	push	hl
	call	_cpct_drawSprite
;src/main.c:69: ms = 14 + 9 * cpct_count2VSYNC();
	call	_cpct_count2VSYNC
	ld	c, l
	ld	b, h
	add	hl, hl
	add	hl, hl
	add	hl, hl
	add	hl, bc
	ld	bc, #0x000e
	add	hl, bc
;src/main.c:75: for(i=0; i<5; i++) {
	ld	-1 (ix), #0x00
00119$:
;src/main.c:76: u8 digit = '0' + (ms % 10);
	push	hl
	ld	bc, #0x000a
	push	bc
	push	hl
	call	__moduint
	pop	af
	pop	af
	ld	c, l
	pop	hl
	ld	a, c
	add	a, #0x30
	ld	c, a
;src/main.c:77: cpct_drawCharM1((void*)(LASTDIGIT_VMEM - 2*i), digit);
	ld	b, #0x00
	ld	e, -1 (ix)
	ld	d, #0x00
	sla	e
	rl	d
	ld	a, #0x4e
	sub	a, e
	ld	e, a
	ld	a, #0xc0
	sbc	a, d
	ld	d, a
	push	hl
	push	bc
	push	de
	call	_cpct_drawCharM1
	pop	hl
;src/main.c:78: ms /= 10;
	ld	bc, #0x000a
	push	bc
	push	hl
	call	__divuint
	pop	af
	pop	af
;src/main.c:75: for(i=0; i<5; i++) {
	inc	-1 (ix)
	ld	a, -1 (ix)
	sub	a, #0x05
	jr	C,00119$
	jp	00117$
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
