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
	.globl _checkUserInputAndPerformActions
	.globl _initialize
	.globl _drawMessages
	.globl _cursor_getY
	.globl _cursor_getX
	.globl _cursor_move
	.globl _cursor_draw
	.globl _cursor_setLocation
	.globl _map_clear
	.globl _map_draw
	.globl _map_changeTile
	.globl _map_setBaseMem
	.globl _cpct_getScreenPtr
	.globl _cpct_setPALColour
	.globl _cpct_waitVSYNC
	.globl _cpct_setVideoMode
	.globl _cpct_drawStringM1
	.globl _cpct_setDrawCharM1
	.globl _cpct_isAnyKeyPressed
	.globl _cpct_isKeyPressed
	.globl _cpct_scanKeyboard
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
;src/main.c:28: void drawMessages() {
;	---------------------------------
; Function drawMessages
; ---------------------------------
_drawMessages::
	push	ix
	ld	ix,#0
	add	ix,sp
	push	af
	dec	sp
;src/main.c:53: for(i=0; i < NUM_MSGS; i++) {
	ld	-3 (ix), #0x00
00102$:
;src/main.c:58: pmem = cpct_getScreenPtr(CPCT_VMEM_START, msg_prop[i][0], msg_prop[i][1]);
	ld	a, -3 (ix)
	ld	-2 (ix), a
	ld	-1 (ix), #0x00
	ld	l, a
	ld	h, #0x00
	add	hl, hl
	add	hl, hl
	ld	a, #<(_drawMessages_msg_prop_1_135)
	add	a, l
	ld	c, a
	ld	a, #>(_drawMessages_msg_prop_1_135)
	adc	a, h
	ld	b, a
	ld	l, c
	ld	h, b
	inc	hl
	ld	d, (hl)
	ld	a, (bc)
	push	bc
	ld	e, a
	push	de
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
	ex	de,hl
	pop	bc
;src/main.c:61: cpct_setDrawCharM1(msg_prop[i][2], msg_prop[i][3]);
	ld	l, c
	ld	h, b
	inc	hl
	inc	hl
	inc	hl
	ld	a, (hl)
	ld	l, c
	ld	h, b
	inc	hl
	inc	hl
	ld	b, (hl)
	push	de
	push	af
	inc	sp
	push	bc
	inc	sp
	call	_cpct_setDrawCharM1
	pop	de
;src/main.c:62: cpct_drawStringM1(strings[i], pmem);
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	add	hl, hl
	ld	bc, #_drawMessages_strings_1_135
	add	hl, bc
	ld	c, (hl)
	inc	hl
	ld	b, (hl)
	push	de
	push	bc
	call	_cpct_drawStringM1
;src/main.c:53: for(i=0; i < NUM_MSGS; i++) {
	inc	-3 (ix)
	ld	a, -3 (ix)
	sub	a, #0x06
	jr	C,00102$
	ld	sp, ix
	pop	ix
	ret
_drawMessages_strings_1_135:
	.dw ___str_0
	.dw ___str_1
	.dw ___str_2
	.dw ___str_3
	.dw ___str_4
	.dw ___str_5
_drawMessages_msg_prop_1_135:
	.db #0x14	; 20
	.db #0x00	; 0
	.db #0x03	; 3
	.db #0x00	; 0
	.db #0x28	; 40
	.db #0x00	; 0
	.db #0x02	; 2
	.db #0x00	; 0
	.db #0x14	; 20
	.db #0x10	; 16
	.db #0x03	; 3
	.db #0x00	; 0
	.db #0x28	; 40
	.db #0x10	; 16
	.db #0x02	; 2
	.db #0x00	; 0
	.db #0x14	; 20
	.db #0x20	; 32
	.db #0x03	; 3
	.db #0x00	; 0
	.db #0x28	; 40
	.db #0x20	; 32
	.db #0x02	; 2
	.db #0x00	; 0
___str_0:
	.ascii "[Cursors]"
	.db 0x00
___str_1:
	.ascii "Move"
	.db 0x00
___str_2:
	.ascii "[Space]"
	.db 0x00
___str_3:
	.ascii "Draw/Remove"
	.db 0x00
___str_4:
	.ascii "[Escape]"
	.db 0x00
___str_5:
	.ascii "Clear"
	.db 0x00
;src/main.c:73: void initialize() {
;	---------------------------------
; Function initialize
; ---------------------------------
_initialize::
;src/main.c:78: cpct_disableFirmware();
	call	_cpct_disableFirmware
;src/main.c:81: cpct_setVideoMode(1); 
	ld	l, #0x01
	call	_cpct_setVideoMode
;src/main.c:86: cpct_setPALColour(0, 0x14);
	ld	hl, #0x1400
	push	hl
	call	_cpct_setPALColour
;src/main.c:87: cpct_setBorder(0x14);
	ld	hl, #0x1410
	push	hl
	call	_cpct_setPALColour
;src/main.c:92: pmem = cpct_getScreenPtr(CPCT_VMEM_START, MAP_START_X, MAP_START_Y);
	ld	hl, #0x3000
	push	hl
	ld	h, #0xc0
	push	hl
	call	_cpct_getScreenPtr
;src/main.c:93: map_setBaseMem(pmem);
	push	hl
	call	_map_setBaseMem
;src/main.c:96: cursor_setLocation(0, 0);
	ld	hl, #0x0000
	ex	(sp),hl
	call	_cursor_setLocation
	pop	af
;src/main.c:99: drawMessages();
	call	_drawMessages
;src/main.c:100: map_draw();
	call	_map_draw
;src/main.c:101: cursor_draw();
	call	_cursor_draw
	ret
;src/main.c:110: void checkUserInputAndPerformActions() {
;	---------------------------------
; Function checkUserInputAndPerformActions
; ---------------------------------
_checkUserInputAndPerformActions::
;src/main.c:112: cpct_scanKeyboard();
	call	_cpct_scanKeyboard
;src/main.c:116: if(cpct_isAnyKeyPressed()) {
	call	_cpct_isAnyKeyPressed
	ld	a, l
	or	a, a
	ret	Z
;src/main.c:118: u8 x = cursor_getX();
	call	_cursor_getX
	ld	c, l
;src/main.c:119: u8 y = cursor_getY();
	push	bc
	call	_cursor_getY
	pop	bc
	ld	b, l
;src/main.c:127: if (cpct_isKeyPressed(Key_CursorUp) && y > 0)
	push	bc
	ld	hl, #0x0100
	call	_cpct_isKeyPressed
	pop	bc
	ld	a, l
	or	a, a
	jr	Z,00105$
	ld	a, b
	or	a, a
	jr	Z,00105$
;src/main.c:128: cursor_move(DIR_UP);
	push	bc
	ld	a, #0x02
	push	af
	inc	sp
	call	_cursor_move
	inc	sp
	pop	bc
	jr	00106$
00105$:
;src/main.c:129: else if (cpct_isKeyPressed(Key_CursorDown) && y < MAP_HEIGHT-1)
	push	bc
	ld	hl, #0x0400
	call	_cpct_isKeyPressed
	pop	bc
	ld	a, l
	or	a, a
	jr	Z,00106$
	ld	a, b
	sub	a, #0x18
	jr	NC,00106$
;src/main.c:130: cursor_move(DIR_DOWN);
	push	bc
	ld	a, #0x03
	push	af
	inc	sp
	call	_cursor_move
	inc	sp
	pop	bc
00106$:
;src/main.c:135: if (cpct_isKeyPressed(Key_CursorLeft) && x > 0)
	push	bc
	ld	hl, #0x0101
	call	_cpct_isKeyPressed
	pop	bc
	ld	a, l
	or	a, a
	jr	Z,00112$
	ld	a, c
	or	a, a
	jr	Z,00112$
;src/main.c:136: cursor_move(DIR_LEFT);
	push	bc
	xor	a, a
	push	af
	inc	sp
	call	_cursor_move
	inc	sp
	pop	bc
	jr	00113$
00112$:
;src/main.c:137: else if (cpct_isKeyPressed(Key_CursorRight) && x < MAP_WIDTH-1)
	push	bc
	ld	hl, #0x0200
	call	_cpct_isKeyPressed
	pop	bc
	ld	a, l
	or	a, a
	jr	Z,00113$
	ld	a, c
	sub	a, #0x4f
	jr	NC,00113$
;src/main.c:138: cursor_move(DIR_RIGHT);
	push	bc
	ld	a, #0x01
	push	af
	inc	sp
	call	_cursor_move
	inc	sp
	pop	bc
00113$:
;src/main.c:142: if (cpct_isKeyPressed(Key_Space)) 
	push	bc
	ld	hl, #0x8005
	call	_cpct_isKeyPressed
	pop	bc
	ld	a, l
	or	a, a
	jr	Z,00118$
;src/main.c:143: map_changeTile(x, y);
	push	bc
	call	_map_changeTile
	pop	af
	jp	_cursor_draw
00118$:
;src/main.c:144: else if (cpct_isKeyPressed(Key_Esc))
	ld	hl, #0x0408
	call	_cpct_isKeyPressed
	ld	a, l
	or	a, a
	jp	Z,_cursor_draw
;src/main.c:145: map_clear();
	call	_map_clear
;src/main.c:148: cursor_draw();
	jp  _cursor_draw
;src/main.c:157: void main (void) {
;	---------------------------------
; Function main
; ---------------------------------
_main::
;src/main.c:159: initialize();
	call	_initialize
;src/main.c:162: while(1) {
00102$:
;src/main.c:164: cpct_waitVSYNC();
	call	_cpct_waitVSYNC
;src/main.c:167: checkUserInputAndPerformActions();
	call	_checkUserInputAndPerformActions
	jr	00102$
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
