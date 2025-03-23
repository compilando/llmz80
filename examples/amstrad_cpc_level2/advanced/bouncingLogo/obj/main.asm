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
	.globl _checkUserInput
	.globl _strcpy
	.globl _concatNum
	.globl _drawMessage
	.globl _updateEntities
	.globl _cpct_setPALColour
	.globl _cpct_setPalette
	.globl _cpct_fw2hw
	.globl _cpct_setVideoMode
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
;src/main.c:30: void checkUserInput (f32 *ax, f32 *ay) {
;	---------------------------------
; Function checkUserInput
; ---------------------------------
_checkUserInput::
	push	ix
	ld	ix,#0
	add	ix,sp
	push	af
	push	af
;src/main.c:32: cpct_scanKeyboard_f();
	call	_cpct_scanKeyboard_f
;src/main.c:36: if      (cpct_isKeyPressed(Key_CursorRight) ) { *ax=0.5;  }
	ld	hl, #0x0200
	call	_cpct_isKeyPressed
	ld	c, l
	ld	l,4 (ix)
	ld	h,5 (ix)
	ld	a, c
	or	a, a
	jr	Z,00104$
	xor	a, a
	ld	(hl), a
	inc	hl
	ld	(hl), a
	inc	hl
	ld	(hl), #0x00
	inc	hl
	ld	(hl), #0x3f
	jr	00105$
00104$:
;src/main.c:37: else if (cpct_isKeyPressed(Key_CursorLeft)  ) { *ax=-0.5; }
	push	hl
	ld	hl, #0x0101
	call	_cpct_isKeyPressed
	ld	a, l
	pop	hl
	or	a, a
	jr	Z,00105$
	xor	a, a
	ld	(hl), a
	inc	hl
	ld	(hl), a
	inc	hl
	ld	(hl), #0x00
	inc	hl
	ld	(hl), #0xbf
00105$:
;src/main.c:38: if      (cpct_isKeyPressed(Key_CursorUp)    ) { *ay=-0.5; }
	ld	hl, #0x0100
	call	_cpct_isKeyPressed
	ld	c, l
	ld	l,6 (ix)
	ld	h,7 (ix)
	ld	a, c
	or	a, a
	jr	Z,00109$
	xor	a, a
	ld	(hl), a
	inc	hl
	ld	(hl), a
	inc	hl
	ld	(hl), #0x00
	inc	hl
	ld	(hl), #0xbf
	jr	00110$
00109$:
;src/main.c:39: else if (cpct_isKeyPressed(Key_CursorDown)  ) { *ay=0.5;  }
	push	hl
	ld	hl, #0x0400
	call	_cpct_isKeyPressed
	ld	a, l
	pop	hl
	or	a, a
	jr	Z,00110$
	xor	a, a
	ld	(hl), a
	inc	hl
	ld	(hl), a
	inc	hl
	ld	(hl), #0x00
	inc	hl
	ld	(hl), #0x3f
00110$:
;src/main.c:42: if      (cpct_isKeyPressed(Key_Q)) {
	ld	hl, #0x0808
	call	_cpct_isKeyPressed
	ld	a, l
	or	a, a
	jr	Z,00115$
;src/main.c:43: g_gravity += 0.01;
	ld	hl, #0x3c23
	push	hl
	ld	hl, #0xd70a
	push	hl
	ld	hl, (_g_gravity + 2)
	push	hl
	ld	hl, (_g_gravity)
	push	hl
	call	___fsadd
	pop	af
	pop	af
	pop	af
	pop	af
	ld	-1 (ix), d
	ld	-2 (ix), e
	ld	-3 (ix), h
	ld	-4 (ix), l
	ld	de, #_g_gravity
	ld	hl, #0
	add	hl, sp
	ld	bc, #4
	ldir
	jr	00116$
00115$:
;src/main.c:44: } else  if (cpct_isKeyPressed(Key_A)) {
	ld	hl, #0x2008
	call	_cpct_isKeyPressed
	ld	a, l
	or	a, a
	jr	Z,00117$
;src/main.c:45: g_gravity -= 0.01;
	ld	hl, #0x3c23
	push	hl
	ld	hl, #0xd70a
	push	hl
	ld	hl, (_g_gravity + 2)
	push	hl
	ld	hl, (_g_gravity)
	push	hl
	call	___fssub
	pop	af
	pop	af
	pop	af
	pop	af
	ld	-1 (ix), d
	ld	-2 (ix), e
	ld	-3 (ix), h
	ld	-4 (ix), l
	ld	de, #_g_gravity
	ld	hl, #0
	add	hl, sp
	ld	bc, #4
	ldir
	jr	00116$
;src/main.c:48: return;
	jr	00117$
00116$:
;src/main.c:52: strcpy(g_message.str, "Gravity:");
	ld	hl, #___str_0
	push	hl
	ld	hl, #(_g_message + 0x0002)
	push	hl
	call	_strcpy
	pop	af
	pop	af
;src/main.c:53: concatNum(&g_message.str[8], g_gravity*100);
	ld	hl, (_g_gravity + 2)
	push	hl
	ld	hl, (_g_gravity)
	push	hl
	ld	hl, #0x42c8
	push	hl
	ld	hl, #0x0000
	push	hl
	call	___fsmul
	pop	af
	pop	af
	pop	af
	pop	af
	push	de
	push	hl
	call	___fs2schar
	pop	af
	pop	af
	ld	b, l
	push	bc
	inc	sp
	ld	hl, #(_g_message + 0x000a)
	push	hl
	call	_concatNum
	pop	af
	inc	sp
;src/main.c:54: g_message.time  = 25;
	ld	hl, #(_g_message + 0x0010)
	ld	(hl), #0x19
00117$:
	ld	sp, ix
	pop	ix
	ret
___str_0:
	.ascii "Gravity:"
	.db 0x00
;src/main.c:60: void main(void) {
;	---------------------------------
; Function main
; ---------------------------------
_main::
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	hl, #-47
	add	hl, sp
	ld	sp, hl
;src/main.c:62: TEntity logo = {
	ld	hl, #0x0008
	add	hl, sp
	ld	bc, #_gc_LogoFremos+0
	ld	(hl), c
	inc	hl
	ld	(hl), b
	ld	hl, #0x0008
	add	hl, sp
	ld	c, l
	ld	b, h
	ld	hl, #0x0002
	add	hl,bc
	ld	-2 (ix), l
	ld	-1 (ix), h
	ld	(hl), #0x00
	inc	hl
	ld	(hl), #0xc0
	ld	hl, #0x0004
	add	hl, bc
	ld	(hl), #0x00
	ld	hl, #0x0005
	add	hl, bc
	ld	(hl), #0x00
	ld	hl, #0x0006
	add	hl,bc
	ld	-5 (ix), l
	ld	-4 (ix), h
	ld	(hl), #0x37
	ld	hl, #0x0007
	add	hl,bc
	ld	-7 (ix), l
	ld	-6 (ix), h
	ld	(hl), #0x14
	ld	hl, #0x0008
	add	hl, bc
	ld	(hl), #0x00
	inc	hl
	ld	(hl), #0x00
	inc	hl
	ld	(hl), #0x00
	inc	hl
	ld	(hl), #0x3f
	ld	hl, #0x000c
	add	hl, bc
	ld	(hl), #0xcd
	inc	hl
	ld	(hl), #0xcc
	inc	hl
	ld	(hl), #0x4c
	inc	hl
	ld	(hl), #0x3e
	ld	hl, #0x0010
	add	hl, bc
	ld	(hl), #0x00
	inc	hl
	ld	(hl), #0x00
	inc	hl
	ld	(hl), #0x00
	inc	hl
	ld	(hl), #0x00
	ld	hl, #0x0014
	add	hl, bc
	ld	(hl), #0x00
	inc	hl
	ld	(hl), #0x00
	inc	hl
	ld	(hl), #0x00
	inc	hl
	ld	(hl), #0x00
	ld	hl, #0x0018
	add	hl, bc
	ld	(hl), #0x00
	inc	hl
	ld	(hl), #0x00
	inc	hl
	ld	(hl), #0x80
	inc	hl
	ld	(hl), #0x3f
	ld	hl, #0x001c
	add	hl, bc
	ld	(hl), #0x00
	inc	hl
	ld	(hl), #0x00
	inc	hl
	ld	(hl), #0x80
	inc	hl
	ld	(hl), #0x3f
;src/main.c:68: g_message.videopos = CPCT_VMEM_START;
	ld	hl, #0xc000
	ld	(_g_message), hl
;src/main.c:69: g_message.str[0]   = '\0';
	ld	hl, #(_g_message + 0x0002)
	ld	(hl), #0x00
;src/main.c:70: g_message.time     = 0;
	ld	hl, #(_g_message + 0x0010)
	ld	(hl), #0x00
;src/main.c:73: g_gravity = 0.02;
	ld	iy, #_g_gravity
	ld	0 (iy), #0x0a
	ld	1 (iy), #0xd7
	ld	2 (iy), #0xa3
	ld	3 (iy), #0x3c
;src/main.c:76: cpct_disableFirmware();
	push	bc
	call	_cpct_disableFirmware
	ld	hl, #0x0010
	push	hl
	ld	hl, #_gc_palette
	push	hl
	call	_cpct_fw2hw
	pop	bc
;src/main.c:80: cpct_setBorder(gc_palette[2]);   // Set the border
	ld	hl, #_gc_palette + 2
	ld	d, (hl)
	push	bc
	ld	e, #0x10
	push	de
	call	_cpct_setPALColour
	ld	hl, #0x0010
	push	hl
	ld	hl, #_gc_palette
	push	hl
	call	_cpct_setPalette
	ld	l, #0x00
	call	_cpct_setVideoMode
	pop	bc
;src/main.c:87: while(1) {
00102$:
;src/main.c:88: f32 ax=0, ay=0;    // User acceleration values
	ld	-47 (ix), #0x00
	ld	-46 (ix), #0x00
	ld	-45 (ix), #0x00
	ld	-44 (ix), #0x00
	ld	-43 (ix), #0x00
	ld	-42 (ix), #0x00
	ld	-41 (ix), #0x00
	ld	-40 (ix), #0x00
;src/main.c:90: checkUserInput(&ax, &ay);
	ld	hl, #0x0004
	add	hl, sp
	ex	de,hl
	ld	hl, #0x0000
	add	hl, sp
	push	bc
	push	de
	push	hl
	call	_checkUserInput
	pop	af
	pop	af
	pop	bc
;src/main.c:91: updateEntities(&logo, ax, ay);
	ld	e, c
	ld	d, b
	push	bc
	ld	l,-41 (ix)
	ld	h,-40 (ix)
	push	hl
	ld	l,-43 (ix)
	ld	h,-42 (ix)
	push	hl
	ld	l,-45 (ix)
	ld	h,-44 (ix)
	push	hl
	ld	l,-47 (ix)
	ld	h,-46 (ix)
	push	hl
	push	de
	call	_updateEntities
	ld	hl, #10
	add	hl, sp
	ld	sp, hl
	call	_drawMessage
	pop	bc
;src/main.c:93: cpct_drawSprite(logo.sprite, logo.videopos, logo.width, logo.height);
	ld	l,-7 (ix)
	ld	h,-6 (ix)
	ld	a, (hl)
	ld	l,-5 (ix)
	ld	h,-4 (ix)
	push	af
	ld	a, (hl)
	ld	-3 (ix), a
	pop	af
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	push	af
	ld	a, (hl)
	inc	hl
	ld	h, (hl)
	ld	l, a
	pop	af
	push	hl
	pop	iy
	ld	l, c
	ld	h, b
	ld	e, (hl)
	inc	hl
	ld	d, (hl)
	push	bc
	push	af
	inc	sp
	ld	a, -3 (ix)
	push	af
	inc	sp
	push	iy
	push	de
	call	_cpct_drawSprite
	pop	bc
	jp	00102$
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
