;--------------------------------------------------------
; File Created by SDCC : free open source ANSI-C Compiler
; Version 3.6.8 #9946 (Linux)
;--------------------------------------------------------
	.module cursor
	.optsdcc -mz80
	
;--------------------------------------------------------
; Public variables in this module
;--------------------------------------------------------
	.globl _map_drawTile
	.globl _map_getBaseMem
	.globl _cpct_getScreenPtr
	.globl _cpct_drawSpriteMasked
	.globl _cursor_y
	.globl _cursor_x
	.globl _cursor_sprite
	.globl _cursor_setLocation
	.globl _cursor_draw
	.globl _cursor_move
	.globl _cursor_getX
	.globl _cursor_getY
;--------------------------------------------------------
; special function registers
;--------------------------------------------------------
;--------------------------------------------------------
; ram data
;--------------------------------------------------------
	.area _DATA
_cursor_x::
	.ds 1
_cursor_y::
	.ds 1
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
;src/cursor.c:53: void cursor_setLocation(u8 x, u8 y) {
;	---------------------------------
; Function cursor_setLocation
; ---------------------------------
_cursor_setLocation::
;src/cursor.c:54: cursor_x = x; 
	ld	hl, #2+0
	add	hl, sp
	ld	a, (hl)
	ld	(#_cursor_x + 0),a
;src/cursor.c:55: cursor_y = y;
	ld	hl, #3+0
	add	hl, sp
	ld	a, (hl)
	ld	(#_cursor_y + 0),a
	ret
_cursor_sprite:
	.db #0x00	; 0
	.db #0xff	; 255
	.db #0x66	; 102	'f'
	.db #0x99	; 153
	.db #0x66	; 102	'f'
	.db #0x99	; 153
	.db #0x00	; 0
	.db #0xff	; 255
;src/cursor.c:64: void cursor_draw() {
;	---------------------------------
; Function cursor_draw
; ---------------------------------
_cursor_draw::
;src/cursor.c:68: map_drawTile(cursor_x, cursor_y);
	ld	a, (_cursor_y)
	push	af
	inc	sp
	ld	a, (_cursor_x)
	push	af
	inc	sp
	call	_map_drawTile
	pop	af
;src/cursor.c:72: pmem = cpct_getScreenPtr(map_getBaseMem(), cursor_x, cursor_y*TILE_HEIGHT);
	ld	a,(#_cursor_y + 0)
	add	a, a
	add	a, a
	ld	d, a
	push	de
	call	_map_getBaseMem
	ld	c, l
	ld	b, h
	inc	sp
	ld	a, (_cursor_x)
	push	af
	inc	sp
	push	bc
	call	_cpct_getScreenPtr
;src/cursor.c:73: cpct_drawSpriteMasked(cursor_sprite, pmem, TILE_WIDTH, TILE_HEIGHT);
	ld	bc, #_cursor_sprite+0
	ld	de, #0x0401
	push	de
	push	hl
	push	bc
	call	_cpct_drawSpriteMasked
	ret
;src/cursor.c:81: void cursor_move(TMoveDir dir) {
;	---------------------------------
; Function cursor_move
; ---------------------------------
_cursor_move::
;src/cursor.c:84: map_drawTile(cursor_x, cursor_y);
	ld	a, (_cursor_y)
	push	af
	inc	sp
	ld	a, (_cursor_x)
	push	af
	inc	sp
	call	_map_drawTile
	pop	af
;src/cursor.c:87: switch(dir) {
	ld	iy, #2
	add	iy, sp
	ld	a, 0 (iy)
	or	a, a
	jr	Z,00101$
	ld	a, 0 (iy)
	dec	a
	jr	Z,00102$
	ld	a, 0 (iy)
	sub	a, #0x02
	jr	Z,00103$
	ld	a, 0 (iy)
	sub	a, #0x03
	jr	Z,00104$
	jp	_cursor_draw
;src/cursor.c:88: case DIR_LEFT:  cursor_x--; break;
00101$:
	ld	hl, #_cursor_x+0
	dec	(hl)
	jp	_cursor_draw
;src/cursor.c:89: case DIR_RIGHT: cursor_x++; break;
00102$:
	ld	hl, #_cursor_x+0
	inc	(hl)
	jp	_cursor_draw
;src/cursor.c:90: case DIR_UP:    cursor_y--; break;
00103$:
	ld	hl, #_cursor_y+0
	dec	(hl)
	jp	_cursor_draw
;src/cursor.c:91: case DIR_DOWN:  cursor_y++; break;
00104$:
	ld	hl, #_cursor_y+0
	inc	(hl)
;src/cursor.c:92: }
;src/cursor.c:95: cursor_draw();
	jp  _cursor_draw
;src/cursor.c:102: u8 cursor_getX() { return cursor_x; }
;	---------------------------------
; Function cursor_getX
; ---------------------------------
_cursor_getX::
	ld	iy, #_cursor_x
	ld	l, 0 (iy)
	ret
;src/cursor.c:103: u8 cursor_getY() { return cursor_y; }
;	---------------------------------
; Function cursor_getY
; ---------------------------------
_cursor_getY::
	ld	iy, #_cursor_y
	ld	l, 0 (iy)
	ret
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
