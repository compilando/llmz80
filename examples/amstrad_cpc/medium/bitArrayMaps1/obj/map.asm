;--------------------------------------------------------
; File Created by SDCC : free open source ANSI-C Compiler
; Version 3.6.8 #9946 (Linux)
;--------------------------------------------------------
	.module map
	.optsdcc -mz80
	
;--------------------------------------------------------
; Public variables in this module
;--------------------------------------------------------
	.globl _map_clear
	.globl _map_changeTile
	.globl _map_draw
	.globl _map_drawTile
	.globl _map_getTile
	.globl _map_setTile
	.globl _map_getBaseMem
	.globl _map_setBaseMem
	.globl _cpct_getScreenPtr
	.globl _cpct_drawStringM1
	.globl _cpct_setDrawCharM1
	.globl _cpct_drawSolidBox
	.globl _cpct_px2byteM1
	.globl _cpct_setBit
	.globl _cpct_getBit
	.globl _map_base_location
	.globl _map
;--------------------------------------------------------
; special function registers
;--------------------------------------------------------
;--------------------------------------------------------
; ram data
;--------------------------------------------------------
	.area _DATA
_map_base_location::
	.ds 2
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
;src/map.c:97: void map_setBaseMem(u8* mem_location) {
;	---------------------------------
; Function map_setBaseMem
; ---------------------------------
_map_setBaseMem::
;src/map.c:98: map_base_location = mem_location;
	ld	hl, #2+0
	add	hl, sp
	ld	a, (hl)
	ld	(#_map_base_location + 0),a
	ld	hl, #2+1
	add	hl, sp
	ld	a, (hl)
	ld	(#_map_base_location + 1),a
	ret
_map:
	.db #0xff	; 255
	.db #0xff	; 255
	.db #0xff	; 255
	.db #0xff	; 255
	.db #0xff	; 255
	.db #0xff	; 255
	.db #0xff	; 255
	.db #0xff	; 255
	.db #0xff	; 255
	.db #0xff	; 255
	.db #0xc0	; 192
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x03	; 3
	.db #0xc0	; 192
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x03	; 3
	.db #0xc3	; 195
	.db #0xf6	; 246
	.db #0x5f	; 95
	.db #0xbf	; 191
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x03	; 3
	.db #0xc0	; 192
	.db #0xc7	; 199
	.db #0xc6	; 198
	.db #0x30	; 48	'0'
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x03	; 3
	.db #0xc0	; 192
	.db #0xc7	; 199
	.db #0xc6	; 198
	.db #0x0c	; 12
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x03	; 3
	.db #0xc0	; 192
	.db #0xc6	; 198
	.db #0x5f	; 95
	.db #0xbf	; 191
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x03	; 3
	.db #0xc0	; 192
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x03	; 3
	.db #0xc0	; 192
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x0f	; 15
	.db #0xdf	; 223
	.db #0x80	; 128
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x03	; 3
	.db #0xc0	; 192
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x03	; 3
	.db #0x0c	; 12
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x03	; 3
	.db #0xc0	; 192
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x03	; 3
	.db #0xc0	; 192
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x0f	; 15
	.db #0xdf	; 223
	.db #0x80	; 128
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x03	; 3
	.db #0xc0	; 192
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x03	; 3
	.db #0xc0	; 192
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x30	; 48	'0'
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x03	; 3
	.db #0xc0	; 192
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x48	; 72	'H'
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x03	; 3
	.db #0xc0	; 192
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xfc	; 252
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x03	; 3
	.db #0xc0	; 192
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xcc	; 204
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x03	; 3
	.db #0xc0	; 192
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x03	; 3
	.db #0xc0	; 192
	.db #0x38	; 56	'8'
	.db #0x3e	; 62
	.db #0xfd	; 253
	.db #0xf8	; 248
	.db #0x19	; 25
	.db #0x8c	; 140
	.db #0x7e	; 126
	.db #0x00	; 0
	.db #0x03	; 3
	.db #0xc0	; 192
	.db #0x58	; 88	'X'
	.db #0x34	; 52	'4'
	.db #0x30	; 48	'0'
	.db #0x60	; 96
	.db #0x1f	; 31
	.db #0x92	; 146
	.db #0x66	; 102	'f'
	.db #0x00	; 0
	.db #0x03	; 3
	.db #0xc0	; 192
	.db #0x18	; 24
	.db #0x32	; 50	'2'
	.db #0x30	; 48	'0'
	.db #0x60	; 96
	.db #0x19	; 25
	.db #0xbf	; 191
	.db #0x7e	; 126
	.db #0x00	; 0
	.db #0x03	; 3
	.db #0xc0	; 192
	.db #0x7e	; 126
	.db #0x3c	; 60
	.db #0xfc	; 252
	.db #0x60	; 96
	.db #0x19	; 25
	.db #0xb3	; 179
	.db #0x60	; 96
	.db #0x00	; 0
	.db #0x03	; 3
	.db #0xc0	; 192
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x03	; 3
	.db #0xc0	; 192
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x03	; 3
	.db #0xff	; 255
	.db #0xff	; 255
	.db #0xff	; 255
	.db #0xff	; 255
	.db #0xff	; 255
	.db #0xff	; 255
	.db #0xff	; 255
	.db #0xff	; 255
	.db #0xff	; 255
	.db #0xff	; 255
;src/map.c:106: u8* map_getBaseMem() { return map_base_location; }
;	---------------------------------
; Function map_getBaseMem
; ---------------------------------
_map_getBaseMem::
	ld	hl, (_map_base_location)
	ret
;src/map.c:114: void map_setTile(u8 x, u8 y, u8 value) {
;	---------------------------------
; Function map_setTile
; ---------------------------------
_map_setTile::
	push	ix
	ld	ix,#0
	add	ix,sp
;src/map.c:118: u16 tile_index = y * MAP_WIDTH + x;
	ld	c,5 (ix)
	ld	b,#0x00
	ld	l, c
	ld	h, b
	add	hl, hl
	add	hl, hl
	add	hl, bc
	add	hl, hl
	add	hl, hl
	add	hl, hl
	add	hl, hl
	ld	c, 4 (ix)
	ld	b, #0x00
	add	hl, bc
;src/map.c:121: cpct_setBit(map, value, tile_index);
	ld	e, 6 (ix)
	ld	d, #0x00
	ld	bc, #_map+0
	push	hl
	push	de
	push	bc
	call	_cpct_setBit
	pop	ix
	ret
;src/map.c:130: u8 map_getTile(u8 x, u8 y) {
;	---------------------------------
; Function map_getTile
; ---------------------------------
_map_getTile::
	push	ix
	ld	ix,#0
	add	ix,sp
;src/map.c:134: u16 tile_index = y * MAP_WIDTH + x;
	ld	c,5 (ix)
	ld	b,#0x00
	ld	l, c
	ld	h, b
	add	hl, hl
	add	hl, hl
	add	hl, bc
	add	hl, hl
	add	hl, hl
	add	hl, hl
	add	hl, hl
	ld	c, 4 (ix)
	ld	b, #0x00
	add	hl, bc
;src/map.c:137: u8  tile_value = cpct_getBit(map, tile_index);
	ld	bc, #_map+0
	push	hl
	push	bc
	call	_cpct_getBit
;src/map.c:138: return tile_value;
	pop	ix
	ret
;src/map.c:149: void map_drawTile(u8 x, u8 y) {
;	---------------------------------
; Function map_drawTile
; ---------------------------------
_map_drawTile::
	push	ix
	ld	ix,#0
	add	ix,sp
;src/map.c:151: u8 *pmem = cpct_getScreenPtr(map_base_location, x, y*TILE_HEIGHT);
	ld	a, 5 (ix)
	add	a, a
	add	a, a
	ld	d, a
	ld	bc, (_map_base_location)
	push	de
	inc	sp
	ld	a, 4 (ix)
	push	af
	inc	sp
	push	bc
	call	_cpct_getScreenPtr
;src/map.c:155: u8 c_pattern = cpct_px2byteM1(C_BLACK, C_BLACK, C_BLACK, C_BLACK);
	push	hl
	ld	hl, #0x0000
	push	hl
	ld	l, #0x00
	push	hl
	call	_cpct_px2byteM1
	pop	af
	pop	af
	ld	e, l
	push	de
	ld	h, 5 (ix)
	ld	l, 4 (ix)
	push	hl
	call	_map_getTile
	pop	af
	pop	de
	pop	bc
	ld	a, l
	or	a, a
	jr	Z,00102$
;src/map.c:157: c_pattern = cpct_px2byteM1(C_YELLOW, C_YELLOW, C_YELLOW, C_YELLOW);
	push	bc
	ld	hl, #0x0101
	push	hl
	ld	l, #0x01
	push	hl
	call	_cpct_px2byteM1
	pop	af
	pop	af
	ld	e, l
	pop	bc
00102$:
;src/map.c:160: cpct_drawSolidBox(pmem, c_pattern, TILE_WIDTH, TILE_HEIGHT);   
	ld	d, #0x00
	ld	hl, #0x0401
	push	hl
	push	de
	push	bc
	call	_cpct_drawSolidBox
	pop	ix
	ret
;src/map.c:168: void map_draw() {
;	---------------------------------
; Function map_draw
; ---------------------------------
_map_draw::
;src/map.c:175: pmem = cpct_getScreenPtr(CPCT_VMEM_START, 30, 160);
	ld	hl, #0xa01e
	push	hl
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
;src/map.c:176: cpct_setDrawCharM1(C_BLACK, C_RED);
	push	hl
	ld	hl, #0x0300
	push	hl
	call	_cpct_setDrawCharM1
	pop	bc
;src/map.c:177: cpct_drawStringM1(string, pmem);
	ld	hl, (_map_draw_string_1_137)
	push	bc
	push	bc
	push	hl
	call	_cpct_drawStringM1
	pop	bc
;src/map.c:180: for(y=0; y < MAP_HEIGHT; y++) 
	ld	e, #0x00
;src/map.c:181: for(x=0; x < MAP_WIDTH; x++) 
00109$:
	ld	d, #0x00
00103$:
;src/map.c:182: map_drawTile(x, y);
	push	bc
	push	de
	ld	a, e
	push	af
	inc	sp
	push	de
	inc	sp
	call	_map_drawTile
	pop	af
	pop	de
	pop	bc
;src/map.c:181: for(x=0; x < MAP_WIDTH; x++) 
	inc	d
	ld	a, d
	sub	a, #0x50
	jr	C,00103$
;src/map.c:180: for(y=0; y < MAP_HEIGHT; y++) 
	inc	e
	ld	a, e
	sub	a, #0x19
	jr	C,00109$
;src/map.c:186: cpct_setDrawCharM1(C_BLACK, C_BLACK);
	push	bc
	ld	hl, #0x0000
	push	hl
	call	_cpct_setDrawCharM1
	pop	bc
;src/map.c:187: cpct_drawStringM1(string, pmem);
	ld	hl, (_map_draw_string_1_137)
	push	bc
	push	hl
	call	_cpct_drawStringM1
	ret
_map_draw_string_1_137:
	.dw ___str_0
___str_0:
	.ascii "Drawing Map"
	.db 0x00
;src/map.c:195: void map_changeTile(u8 x, u8 y) {
;	---------------------------------
; Function map_changeTile
; ---------------------------------
_map_changeTile::
	push	ix
	ld	ix,#0
	add	ix,sp
;src/map.c:197: u8 tile = map_getTile(x, y);
	ld	h, 5 (ix)
	ld	l, 4 (ix)
	push	hl
	call	_map_getTile
	pop	af
;src/map.c:201: tile = (tile == 0);
	ld	a, l
	or	a, a
	jr	NZ,00103$
	ld	a,#0x01
	jr	00104$
00103$:
	xor	a,a
00104$:
	ld	b, a
;src/map.c:204: map_setTile(x, y, tile);
	push	bc
	inc	sp
	ld	h, 5 (ix)
	ld	l, 4 (ix)
	push	hl
	call	_map_setTile
;src/map.c:205: map_drawTile(x, y);
	inc	sp
	ld	h, 5 (ix)
	ld	l, 4 (ix)
	ex	(sp),hl
	call	_map_drawTile
	pop	af
	pop	ix
	ret
;src/map.c:213: void map_clear() {
;	---------------------------------
; Function map_clear
; ---------------------------------
_map_clear::
;src/map.c:217: for(y=0; y < MAP_HEIGHT; y++) 
	ld	c, #0x00
;src/map.c:218: for(x=0; x < MAP_WIDTH; x++) 
00109$:
	ld	b, #0x00
00103$:
;src/map.c:219: map_setTile(x, y, 0);
	push	bc
	xor	a, a
	push	af
	inc	sp
	ld	a, c
	push	af
	inc	sp
	push	bc
	inc	sp
	call	_map_setTile
	pop	af
	inc	sp
	pop	bc
;src/map.c:218: for(x=0; x < MAP_WIDTH; x++) 
	inc	b
	ld	a, b
	sub	a, #0x50
	jr	C,00103$
;src/map.c:217: for(y=0; y < MAP_HEIGHT; y++) 
	inc	c
	ld	a, c
	sub	a, #0x19
	jr	C,00109$
;src/map.c:222: map_draw();
	jp  _map_draw
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
