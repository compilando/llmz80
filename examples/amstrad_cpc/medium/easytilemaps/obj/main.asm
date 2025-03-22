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
	.globl _application
	.globl _drawScreenTilemap
	.globl _readKeyboardInput
	.globl _showMessages
	.globl _wait4Key
	.globl _swapBuffers
	.globl _printf
	.globl _cpct_etm_setTileset2x4
	.globl _cpct_etm_drawTileBox2x4
	.globl _cpct_getScreenPtr
	.globl _cpct_setVideoMemoryPage
	.globl _cpct_setPALColour
	.globl _cpct_waitVSYNC
	.globl _cpct_isKeyPressed
	.globl _cpct_scanKeyboard_f
	.globl _cpct_setStackLocation
	.globl _cpct_memset_f64
	.globl _cpct_disableFirmware
	.globl _g_scrbuffers
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
;src/main.c:51: void swapBuffers(u8** scrbuffers) {
;	---------------------------------
; Function swapBuffers
; ---------------------------------
_swapBuffers::
	push	ix
	ld	ix,#0
	add	ix,sp
	push	af
;src/main.c:59: cpct_setVideoMemoryPage( (u16)(scrbuffers[1]) >> 10 );
	ld	l,4 (ix)
	ld	h,5 (ix)
	inc	hl
	inc	hl
	ld	c, (hl)
	inc	hl
	ld	a, (hl)
	rrca
	rrca
	and	a, #0x3f
	ld	l, a
	call	_cpct_setVideoMemoryPage
;src/main.c:63: aux = scrbuffers[0];
	ld	e,4 (ix)
	ld	d,5 (ix)
	ld	l, e
	ld	h, d
	ld	c, (hl)
	inc	hl
	ld	b, (hl)
;src/main.c:64: scrbuffers[0] = scrbuffers[1];
	push	de
	pop	iy
	inc	iy
	inc	iy
	ld	a, 0 (iy)
	ld	-2 (ix), a
	ld	a, 1 (iy)
	ld	-1 (ix), a
	ld	a, -2 (ix)
	ld	(de), a
	inc	de
	ld	a, -1 (ix)
	ld	(de), a
;src/main.c:65: scrbuffers[1] = aux;
	ld	0 (iy), c
	ld	1 (iy), b
	ld	sp, ix
	pop	ix
	ret
_g_scrbuffers:
	.dw #0xc000
	.dw #0x8000
;src/main.c:71: void wait4Key(cpct_keyID key) {
;	---------------------------------
; Function wait4Key
; ---------------------------------
_wait4Key::
;src/main.c:74: do
00101$:
;src/main.c:75: cpct_scanKeyboard_f();
	call	_cpct_scanKeyboard_f
;src/main.c:76: while(cpct_isKeyPressed(key));
	pop	bc
	pop	hl
	push	hl
	push	bc
	call	_cpct_isKeyPressed
	ld	a, l
	or	a, a
	jr	NZ,00101$
;src/main.c:79: do
00104$:
;src/main.c:80: cpct_scanKeyboard_f();
	call	_cpct_scanKeyboard_f
;src/main.c:81: while(!cpct_isKeyPressed(key));
	pop	bc
	pop	hl
	push	hl
	push	bc
	call	_cpct_isKeyPressed
	ld	a, l
	or	a, a
	jr	Z,00104$
	ret
;src/main.c:89: void showMessages() {
;	---------------------------------
; Function showMessages
; ---------------------------------
_showMessages::
;src/main.c:112: for (i=0; i < NUMMSGS; ++i)
	ld	c, #0x00
00102$:
;src/main.c:113: printf(messages [i]);
	ld	l, c
	ld	h, #0x00
	add	hl, hl
	ld	de, #_showMessages_messages_1_142
	add	hl, de
	ld	e, (hl)
	inc	hl
	ld	d, (hl)
	push	bc
	push	de
	call	_printf
	pop	af
	pop	bc
;src/main.c:112: for (i=0; i < NUMMSGS; ++i)
	inc	c
	ld	a, c
	sub	a, #0x0f
	jr	C,00102$
;src/main.c:116: wait4Key(Key_Space);
	ld	hl, #0x8005
	push	hl
	call	_wait4Key
	pop	af
	ret
_showMessages_messages_1_142:
	.dw ___str_0
	.dw ___str_1
	.dw ___str_2
	.dw ___str_3
	.dw ___str_4
	.dw ___str_5
	.dw ___str_6
	.dw ___str_7
	.dw ___str_8
	.dw ___str_9
	.dw ___str_10
	.dw ___str_11
	.dw ___str_12
	.dw ___str_13
	.dw ___str_14
___str_0:
	.db 0x0f
	.db 0x02
	.ascii "*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-"
	.db 0x00
___str_1:
	.db 0x0f
	.db 0x03
	.ascii "             TILEMAPS DEMO"
	.db 0x0a
	.db 0x0d
	.db 0x00
___str_2:
	.db 0x0f
	.db 0x02
	.ascii "*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-"
	.db 0x0a
	.db 0x0d
	.db 0x00
___str_3:
	.db 0x0f
	.db 0x01
	.ascii "Shows  a "
	.db 0x0f
	.db 0x03
	.ascii "tilemap"
	.db 0x0f
	.db 0x01
	.ascii "  through   a  viewport,"
	.db 0x00
___str_4:
	.ascii "letting you control the  "
	.db 0x0f
	.db 0x02
	.ascii "location"
	.db 0x0f
	.db 0x01
	.ascii " of the"
	.db 0x00
___str_5:
	.db 0x0f
	.db 0x03
	.ascii "tilemap"
	.db 0x0f
	.db 0x01
	.ascii " and the "
	.db 0x0f
	.db 0x02
	.ascii "size"
	.db 0x0f
	.db 0x01
	.ascii " and "
	.db 0x0f
	.db 0x02
	.ascii "position"
	.db 0x0f
	.db 0x01
	.ascii " of the"
	.db 0x00
___str_6:
	.ascii "viewport. All is done  using "
	.db 0x0f
	.db 0x03
	.ascii "C"
	.db 0x0f
	.db 0x03
	.ascii "P"
	.db 0x0f
	.db 0x03
	.ascii "C"
	.db 0x0f
	.db 0x02
	.ascii "telera"
	.db 0x0f
	.db 0x01
	.ascii "'s"
	.db 0x00
___str_7:
	.ascii "function  "
	.db 0x0f
	.db 0x02
	.ascii "cpct_etm_drawTileBox2x4"
	.db 0x0f
	.db 0x01
	.ascii ",  from"
	.db 0x00
___str_8:
	.ascii "its EasyTileMaps module."
	.db 0x0a
	.db 0x0d
	.db 0x0a
	.db 0x0d
	.db 0x00
___str_9:
	.ascii "These are the "
	.db 0x0f
	.db 0x03
	.ascii "control Keys"
	.db 0x0f
	.db 0x01
	.ascii ":"
	.db 0x0a
	.db 0x0d
	.db 0x0a
	.db 0x0d
	.db 0x00
___str_10:
	.db 0x0f
	.db 0x02
	.ascii " Cursors "
	.db 0x0f
	.db 0x03
	.ascii "-"
	.db 0x0f
	.db 0x01
	.ascii " Move tilemap location."
	.db 0x0a
	.db 0x0d
	.db 0x00
___str_11:
	.db 0x0f
	.db 0x02
	.ascii "  1, 2   "
	.db 0x0f
	.db 0x03
	.ascii "-"
	.db 0x0f
	.db 0x01
	.ascii " Change viewport width."
	.db 0x0a
	.db 0x0d
	.db 0x00
___str_12:
	.db 0x0f
	.db 0x02
	.ascii "  3, 4   "
	.db 0x0f
	.db 0x03
	.ascii "-"
	.db 0x0f
	.db 0x01
	.ascii " Change viewport height."
	.db 0x0a
	.db 0x0d
	.db 0x00
___str_13:
	.db 0x0f
	.db 0x02
	.ascii " W,A,S,D "
	.db 0x0f
	.db 0x03
	.ascii "-"
	.db 0x0f
	.db 0x01
	.ascii " Move viewport."
	.db 0x0a
	.db 0x0d
	.db 0x0a
	.db 0x0d
	.db 0x00
___str_14:
	.ascii "       Press "
	.db 0x0f
	.db 0x02
	.ascii "["
	.db 0x0f
	.db 0x03
	.ascii "Space"
	.db 0x0f
	.db 0x02
	.ascii "]"
	.db 0x0f
	.db 0x01
	.ascii " to continue"
	.db 0x00
;src/main.c:122: void readKeyboardInput(TScreenTilemap *scr){
;	---------------------------------
; Function readKeyboardInput
; ---------------------------------
_readKeyboardInput::
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	hl, #-13
	add	hl, sp
	ld	sp, hl
;src/main.c:125: while(1) {
00149$:
;src/main.c:127: cpct_scanKeyboard_f(); 
	call	_cpct_scanKeyboard_f
;src/main.c:132: if (cpct_isKeyPressed(Key_CursorUp) && scr->y) {
	ld	hl, #0x0100
	call	_cpct_isKeyPressed
	ld	-1 (ix), l
	ld	a, 4 (ix)
	ld	-3 (ix), a
	ld	a, 5 (ix)
	ld	-2 (ix), a
	ld	a, -3 (ix)
	add	a, #0x01
	ld	-5 (ix), a
	ld	a, -2 (ix)
	adc	a, #0x00
	ld	-4 (ix), a
	ld	a, -1 (ix)
	or	a, a
	jr	Z,00145$
	ld	l,-5 (ix)
	ld	h,-4 (ix)
	ld	a, (hl)
	or	a, a
	jr	Z,00145$
;src/main.c:133: scr->y -= 4;   // Move Tilemap Up (4 by 4 pixels, as it can only be placed
	add	a, #0xfc
	ld	l,-5 (ix)
	ld	h,-4 (ix)
	ld	(hl), a
;src/main.c:134: return;        // ... on pixel lines 0 and 4
	jp	00151$
00145$:
;src/main.c:135: } else if (cpct_isKeyPressed(Key_CursorDown) && scr->y < (SCR_HEIGHT - 4*MAP_HEIGHT)) {
	ld	hl, #0x0400
	call	_cpct_isKeyPressed
	ld	a, l
	or	a, a
	jr	Z,00141$
	ld	l,-5 (ix)
	ld	h,-4 (ix)
	ld	a, (hl)
	cp	a, #0x88
	jr	NC,00141$
;src/main.c:136: scr->y += 4;   // Move Tilemap Down (same as moving Up, 4 by 4 pixels)
	add	a, #0x04
	ld	l,-5 (ix)
	ld	h,-4 (ix)
	ld	(hl), a
;src/main.c:137: return;
	jp	00151$
00141$:
;src/main.c:138: } else if (cpct_isKeyPressed(Key_CursorLeft) && scr->x) {
	ld	hl, #0x0101
	call	_cpct_isKeyPressed
	ld	a, l
	or	a, a
	jr	Z,00137$
	ld	l,-3 (ix)
	ld	h,-2 (ix)
	ld	c, (hl)
	ld	a, c
	or	a, a
	jr	Z,00137$
;src/main.c:139: --scr->x;      // Move Tilemap Left 2 pixels (1 byte)
	dec	c
	ld	l,-3 (ix)
	ld	h,-2 (ix)
	ld	(hl), c
;src/main.c:140: return;
	jp	00151$
00137$:
;src/main.c:141: } else if (cpct_isKeyPressed(Key_CursorRight) && scr->x < (SCR_WIDTH - 2*MAP_WIDTH)) {
	ld	hl, #0x0200
	call	_cpct_isKeyPressed
	ld	a, l
	or	a, a
	jr	Z,00133$
	ld	l,-3 (ix)
	ld	h,-2 (ix)
	ld	a, (hl)
	cp	a, #0x28
	jr	NC,00133$
;src/main.c:142: ++scr->x;      // Move Tilemap Right 2 pixels (1 byte)
	inc	a
	ld	l,-3 (ix)
	ld	h,-2 (ix)
	ld	(hl), a
;src/main.c:143: return;
	jp	00151$
00133$:
;src/main.c:144: } else if (cpct_isKeyPressed(Key_2) && scr->viewport.x + scr->viewport.w < MAP_WIDTH) {
	ld	hl, #0x0208
	call	_cpct_isKeyPressed
	ld	-5 (ix), l
;src/main.c:165: } else if (cpct_isKeyPressed(Key_D) && scr->viewport.x + scr->viewport.w < MAP_WIDTH) {
	ld	a, -3 (ix)
	add	a, #0x02
	ld	-11 (ix), a
	ld	a, -2 (ix)
	adc	a, #0x00
	ld	-10 (ix), a
;src/main.c:144: } else if (cpct_isKeyPressed(Key_2) && scr->viewport.x + scr->viewport.w < MAP_WIDTH) {
	ld	a, -3 (ix)
	add	a, #0x04
	ld	-7 (ix), a
	ld	a, -2 (ix)
	adc	a, #0x00
	ld	-6 (ix), a
	ld	a, -5 (ix)
	or	a, a
	jr	Z,00129$
	ld	l,-11 (ix)
	ld	h,-10 (ix)
	ld	a, (hl)
	ld	-5 (ix), a
	ld	-5 (ix), a
	ld	-4 (ix), #0x00
	ld	l,-7 (ix)
	ld	h,-6 (ix)
	ld	a, (hl)
	ld	-1 (ix), a
	ld	-13 (ix), a
	ld	-12 (ix), #0x00
	ld	a, -5 (ix)
	add	a, -13 (ix)
	ld	-13 (ix), a
	ld	a, -4 (ix)
	adc	a, -12 (ix)
	ld	-12 (ix), a
	ld	a, -13 (ix)
	sub	a, #0x14
	ld	a, -12 (ix)
	rla
	ccf
	rra
	sbc	a, #0x80
	jr	NC,00129$
;src/main.c:145: ++scr->viewport.w;   // Enlarge viewport Horizontally
	ld	c, -1 (ix)
	inc	c
	ld	l,-7 (ix)
	ld	h,-6 (ix)
	ld	(hl), c
;src/main.c:146: return;
	jp	00151$
00129$:
;src/main.c:147: } else if (cpct_isKeyPressed(Key_1) && scr->viewport.w > 1) {
	ld	hl, #0x0108
	call	_cpct_isKeyPressed
	ld	a, l
	or	a, a
	jr	Z,00125$
	ld	l,-7 (ix)
	ld	h,-6 (ix)
	ld	c, (hl)
	ld	a, #0x01
	sub	a, c
	jr	NC,00125$
;src/main.c:148: --scr->viewport.w;   // Reduce viewport Horizontally
	dec	c
	ld	l,-7 (ix)
	ld	h,-6 (ix)
	ld	(hl), c
;src/main.c:149: return;
	jp	00151$
00125$:
;src/main.c:150: } else if (cpct_isKeyPressed(Key_4) && scr->viewport.y + scr->viewport.h < MAP_HEIGHT) {
	ld	hl, #0x0107
	call	_cpct_isKeyPressed
	ld	-13 (ix), l
	ld	a, -3 (ix)
	add	a, #0x03
	ld	-5 (ix), a
	ld	a, -2 (ix)
	adc	a, #0x00
	ld	-4 (ix), a
	ld	a, -3 (ix)
	add	a, #0x05
	ld	-3 (ix), a
	ld	a, -2 (ix)
	adc	a, #0x00
	ld	-2 (ix), a
	ld	a, -13 (ix)
	or	a, a
	jr	Z,00121$
	ld	l,-5 (ix)
	ld	h,-4 (ix)
	ld	a, (hl)
	ld	-13 (ix), a
	ld	-13 (ix), a
	ld	-12 (ix), #0x00
	ld	l,-3 (ix)
	ld	h,-2 (ix)
	ld	a, (hl)
	ld	-1 (ix), a
	ld	-9 (ix), a
	ld	-8 (ix), #0x00
	ld	a, -13 (ix)
	add	a, -9 (ix)
	ld	-9 (ix), a
	ld	a, -12 (ix)
	adc	a, -8 (ix)
	ld	-8 (ix), a
	ld	a, -9 (ix)
	sub	a, #0x10
	ld	a, -8 (ix)
	rla
	ccf
	rra
	sbc	a, #0x80
	jr	NC,00121$
;src/main.c:151: ++scr->viewport.h;   // Enlarge viewport Vertically
	ld	c, -1 (ix)
	inc	c
	ld	l,-3 (ix)
	ld	h,-2 (ix)
	ld	(hl), c
;src/main.c:152: return;
	jp	00151$
00121$:
;src/main.c:153: } else if (cpct_isKeyPressed(Key_3) && scr->viewport.h > 1) {
	ld	hl, #0x0207
	call	_cpct_isKeyPressed
	ld	a, l
	or	a, a
	jr	Z,00117$
	ld	l,-3 (ix)
	ld	h,-2 (ix)
	ld	c, (hl)
	ld	a, #0x01
	sub	a, c
	jr	NC,00117$
;src/main.c:154: --scr->viewport.h;   // Reduce viewport Vertically
	dec	c
	ld	l,-3 (ix)
	ld	h,-2 (ix)
	ld	(hl), c
;src/main.c:155: return;
	jp	00151$
00117$:
;src/main.c:156: } else if (cpct_isKeyPressed(Key_W) && scr->viewport.y) {
	ld	hl, #0x0807
	call	_cpct_isKeyPressed
	ld	a, l
	or	a, a
	jr	Z,00113$
	ld	l,-5 (ix)
	ld	h,-4 (ix)
	ld	c, (hl)
	ld	a, c
	or	a, a
	jr	Z,00113$
;src/main.c:157: --scr->viewport.y;   // Move viewport Up
	dec	c
	ld	l,-5 (ix)
	ld	h,-4 (ix)
	ld	(hl), c
;src/main.c:158: return;
	jp	00151$
00113$:
;src/main.c:159: } else if (cpct_isKeyPressed(Key_S) && scr->viewport.y + scr->viewport.h < MAP_HEIGHT) {
	ld	hl, #0x1007
	call	_cpct_isKeyPressed
	ld	a, l
	or	a, a
	jr	Z,00109$
	ld	l,-5 (ix)
	ld	h,-4 (ix)
	ld	a, (hl)
	ld	-9 (ix), a
	ld	-13 (ix), a
	ld	-12 (ix), #0x00
	ld	l,-3 (ix)
	ld	h,-2 (ix)
	ld	a, (hl)
	ld	-3 (ix), a
	ld	-3 (ix), a
	ld	-2 (ix), #0x00
	ld	a, -13 (ix)
	add	a, -3 (ix)
	ld	-13 (ix), a
	ld	a, -12 (ix)
	adc	a, -2 (ix)
	ld	-12 (ix), a
	ld	a, -13 (ix)
	sub	a, #0x10
	ld	a, -12 (ix)
	rla
	ccf
	rra
	sbc	a, #0x80
	jr	NC,00109$
;src/main.c:160: ++scr->viewport.y;   // Move viewport Down
	ld	c, -9 (ix)
	inc	c
	ld	l,-5 (ix)
	ld	h,-4 (ix)
	ld	(hl), c
;src/main.c:161: return;
	jr	00151$
00109$:
;src/main.c:162: } else if (cpct_isKeyPressed(Key_A) && scr->viewport.x) {
	ld	hl, #0x2008
	call	_cpct_isKeyPressed
	ld	a, l
	or	a, a
	jr	Z,00105$
	ld	l,-11 (ix)
	ld	h,-10 (ix)
	ld	c, (hl)
	ld	a, c
	or	a, a
	jr	Z,00105$
;src/main.c:163: --scr->viewport.x;   // Move viewport Left
	dec	c
	ld	l,-11 (ix)
	ld	h,-10 (ix)
	ld	(hl), c
;src/main.c:164: return;
	jr	00151$
00105$:
;src/main.c:165: } else if (cpct_isKeyPressed(Key_D) && scr->viewport.x + scr->viewport.w < MAP_WIDTH) {
	ld	hl, #0x2007
	call	_cpct_isKeyPressed
	ld	a, l
	or	a, a
	jp	Z, 00149$
;src/main.c:144: } else if (cpct_isKeyPressed(Key_2) && scr->viewport.x + scr->viewport.w < MAP_WIDTH) {
	ld	l,-11 (ix)
	ld	h,-10 (ix)
	ld	c, (hl)
;src/main.c:165: } else if (cpct_isKeyPressed(Key_D) && scr->viewport.x + scr->viewport.w < MAP_WIDTH) {
	ld	e, c
	ld	d, #0x00
	ld	l,-7 (ix)
	ld	h,-6 (ix)
	ld	l, (hl)
	ld	h, #0x00
	add	hl, de
	ld	de, #0x8014
	add	hl, hl
	ccf
	rr	h
	rr	l
	sbc	hl, de
	jp	NC, 00149$
;src/main.c:166: ++scr->viewport.x;   // Move viewport Right
	inc	c
	ld	l,-11 (ix)
	ld	h,-10 (ix)
	ld	(hl), c
;src/main.c:167: return;
00151$:
	ld	sp, ix
	pop	ix
	ret
;src/main.c:177: void drawScreenTilemap(TScreenTilemap *scr) {
;	---------------------------------
; Function drawScreenTilemap
; ---------------------------------
_drawScreenTilemap::
	push	ix
	ld	ix,#0
	add	ix,sp
	push	af
	push	af
;src/main.c:181: cpct_memset_f64(g_scrbuffers[1], 0x00, 0x4000);
	ld	hl, (#(_g_scrbuffers + 0x0002) + 0)
	ld	bc, #0x4000
	push	bc
	ld	bc, #0x0000
	push	bc
	push	hl
	call	_cpct_memset_f64
;src/main.c:185: ptmscr = cpct_getScreenPtr(g_scrbuffers[1], scr->x, scr->y);
	ld	c,4 (ix)
	ld	b,5 (ix)
	ld	l, c
	ld	h, b
	inc	hl
	ld	d, (hl)
	ld	a, (bc)
	ld	hl, (#(_g_scrbuffers + 0x0002) + 0)
	push	hl
	pop	iy
	push	bc
	ld	e, a
	push	de
	push	iy
	call	_cpct_getScreenPtr
	ex	de,hl
	pop	bc
;src/main.c:190: MAP_WIDTH, ptmscr, g_tilemap);
	ld	-2 (ix), e
	ld	-1 (ix), d
;src/main.c:189: scr->viewport.w, scr->viewport.h, 
	inc	sp
	inc	sp
	push	bc
	push	bc
	pop	iy
	ld	e, 5 (iy)
	ld	l, c
	ld	h, b
	inc	hl
	inc	hl
	inc	hl
	inc	hl
	ld	d, (hl)
;src/main.c:188: cpct_etm_drawTileBox2x4(scr->viewport.x, scr->viewport.y, 
	ld	l, c
	ld	h, b
	inc	hl
	inc	hl
	inc	hl
	ld	c, (hl)
	pop	hl
	push	hl
	inc	hl
	inc	hl
	ld	b, (hl)
	ld	hl, #_g_tilemap
	push	hl
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	push	hl
	ld	a, #0x14
	push	af
	inc	sp
	ld	a, e
	push	af
	inc	sp
	ld	e, c
	push	de
	push	bc
	inc	sp
	call	_cpct_etm_drawTileBox2x4
;src/main.c:194: cpct_waitVSYNC();
	call	_cpct_waitVSYNC
;src/main.c:195: swapBuffers(g_scrbuffers);
	ld	hl, #_g_scrbuffers
	push	hl
	call	_swapBuffers
	ld	sp,ix
	pop	ix
	ret
;src/main.c:202: void application(void) {
;	---------------------------------
; Function application
; ---------------------------------
_application::
	push	ix
	ld	hl, #-6
	add	hl, sp
	ld	sp, hl
;src/main.c:204: TScreenTilemap scr = { 0, 0, { 0, 0, MAP_WIDTH, MAP_HEIGHT} };
	ld	hl, #0x0000
	add	hl, sp
	ld	(hl), #0x00
	ld	hl, #0x0000
	add	hl, sp
	ld	c, l
	ld	b, h
	ld	e, c
	ld	d, b
	inc	de
	xor	a, a
	ld	(de), a
	ld	e, c
	ld	d, b
	inc	de
	inc	de
	xor	a, a
	ld	(de), a
	ld	e, c
	ld	d, b
	inc	de
	inc	de
	inc	de
	xor	a, a
	ld	(de), a
	ld	hl, #0x0004
	add	hl, bc
	ld	(hl), #0x14
	ld	hl, #0x0005
	add	hl, bc
	ld	(hl), #0x10
;src/main.c:207: showMessages();
	push	bc
	call	_showMessages
	call	_cpct_disableFirmware
	ld	hl, #0x0010
	push	hl
	call	_cpct_setPALColour
	ld	hl, #0x1400
	push	hl
	call	_cpct_setPALColour
	ld	hl, #_g_tileset
	call	_cpct_etm_setTileset2x4
	pop	bc
;src/main.c:220: while(1) {
00102$:
;src/main.c:221: drawScreenTilemap(&scr);   // Redraws the tilemap
	ld	e, c
	ld	d, b
	push	bc
	push	de
	call	_drawScreenTilemap
	pop	af
	pop	bc
;src/main.c:222: readKeyboardInput(&scr);   // Waits for a user input and makes associated changes
	ld	e, c
	ld	d, b
	push	bc
	push	de
	call	_readKeyboardInput
	pop	af
	pop	bc
	jr	00102$
;src/main.c:233: void main(void) {
;	---------------------------------
; Function main
; ---------------------------------
_main::
;src/main.c:237: cpct_setStackLocation((void*)0x8000);  
	ld	hl, #0x8000
	call	_cpct_setStackLocation
;src/main.c:240: application();   
	jp  _application
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
