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
	.globl _updateUser
	.globl _initializeCPC
	.globl _drawEntity
	.globl _setAnimation
	.globl _updateEntity
	.globl _getPersea
	.globl _cpct_setPalette
	.globl _cpct_fw2hw
	.globl _cpct_waitVSYNC
	.globl _cpct_setVideoMode
	.globl _cpct_drawSprite
	.globl _cpct_drawSolidBox
	.globl _cpct_px2byteM0
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
;src/main.c:28: void initializeCPC() {
;	---------------------------------
; Function initializeCPC
; ---------------------------------
_initializeCPC::
;src/main.c:32: cpct_disableFirmware();
	call	_cpct_disableFirmware
;src/main.c:35: cpct_fw2hw(gc_palette, 16);
	ld	hl, #0x0010
	push	hl
	ld	hl, #_gc_palette
	push	hl
	call	_cpct_fw2hw
;src/main.c:36: cpct_setPalette(gc_palette, 16);
	ld	hl, #0x0010
	push	hl
	ld	hl, #_gc_palette
	push	hl
	call	_cpct_setPalette
;src/main.c:39: cpct_setVideoMode(0);
	ld	l, #0x00
	call	_cpct_setVideoMode
;src/main.c:42: c0 = cpct_px2byteM0(4, 4);   // c0 = 2 consecutive pixels of firmware colour 4 (blue)
	ld	hl, #0x0404
	push	hl
	call	_cpct_px2byteM0
	ld	c, l
;src/main.c:43: cpct_drawSolidBox(CPCT_VMEM_START, c0, 40, 60); // Boxes cannot be wider than 64 bytes,
	ld	b, #0x00
	push	bc
	ld	hl, #0x3c28
	push	hl
	push	bc
	ld	hl, #0xc000
	push	hl
	call	_cpct_drawSolidBox
	pop	bc
;src/main.c:44: cpct_drawSolidBox((void*)0xC028, c0, 40, 60); // ... so we use 2 boxes of 40 bytes wide.
	push	bc
	ld	hl, #0x3c28
	push	hl
	push	bc
	ld	h, #0xc0
	push	hl
	call	_cpct_drawSolidBox
	ld	hl, #0x1437
	push	hl
	ld	hl, #0xc0fc
	push	hl
	ld	hl, #_gc_LogoFremos
	push	hl
	call	_cpct_drawSprite
	ld	hl, #0x0802
	push	hl
	call	_cpct_px2byteM0
	pop	bc
;src/main.c:49: cpct_drawSolidBox((void*)0xC3C0, c1, 40, 8);
	ld	h, #0x00
	push	hl
	push	bc
	ld	de, #0x0828
	push	de
	push	hl
	ld	de, #0xc3c0
	push	de
	call	_cpct_drawSolidBox
	pop	bc
	pop	hl
;src/main.c:50: cpct_drawSolidBox((void*)0xC3E8, c1, 40, 8);
	push	bc
	ld	de, #0x0828
	push	de
	push	hl
	ld	hl, #0xc3e8
	push	hl
	call	_cpct_drawSolidBox
	pop	bc
;src/main.c:53: cpct_drawSolidBox((void*)0xC410, c0, 40, 96);
	push	bc
	ld	hl, #0x6028
	push	hl
	push	bc
	ld	hl, #0xc410
	push	hl
	call	_cpct_drawSolidBox
	pop	bc
;src/main.c:54: cpct_drawSolidBox((void*)0xC438, c0, 40, 96);
	ld	hl, #0x6028
	push	hl
	push	bc
	ld	hl, #0xc438
	push	hl
	call	_cpct_drawSolidBox
	ret
;src/main.c:60: void updateUser(TEntity* user) {
;	---------------------------------
; Function updateUser
; ---------------------------------
_updateUser::
;src/main.c:62: TEntityStatus animrequest = es_stop;
	ld	b, #0x01
;src/main.c:65: cpct_scanKeyboard();
	push	bc
	call	_cpct_scanKeyboard
	ld	hl, #0x8005
	call	_cpct_isKeyPressed
	pop	bc
	ld	a, l
	or	a, a
	jr	Z,00119$
	ld	b, #0x07
	jr	00120$
00119$:
;src/main.c:69: else if ( cpct_isKeyPressed(Key_CursorUp)    ) animrequest = es_kick;
	push	bc
	ld	hl, #0x0100
	call	_cpct_isKeyPressed
	pop	bc
	ld	a, l
	or	a, a
	jr	Z,00116$
	ld	b, #0x05
	jr	00120$
00116$:
;src/main.c:70: else if ( cpct_isKeyPressed(Key_CursorDown)  ) animrequest = es_fist;
	push	bc
	ld	hl, #0x0400
	call	_cpct_isKeyPressed
	pop	bc
	ld	a, l
	or	a, a
	jr	Z,00113$
	ld	b, #0x04
	jr	00120$
00113$:
;src/main.c:71: else if ( cpct_isKeyPressed(Key_CursorRight) ) animrequest = es_walk_right;
	push	bc
	ld	hl, #0x0200
	call	_cpct_isKeyPressed
	pop	bc
	ld	a, l
	or	a, a
	jr	Z,00110$
	ld	b, #0x02
	jr	00120$
00110$:
;src/main.c:72: else if ( cpct_isKeyPressed(Key_CursorLeft)  ) animrequest = es_walk_left;
	push	bc
	ld	hl, #0x0101
	call	_cpct_isKeyPressed
	pop	bc
	ld	a, l
	or	a, a
	jr	Z,00107$
	ld	b, #0x03
	jr	00120$
00107$:
;src/main.c:73: else if ( cpct_isKeyPressed(Key_1)           ) animrequest = es_dead;
	push	bc
	ld	hl, #0x0108
	call	_cpct_isKeyPressed
	pop	bc
	ld	a, l
	or	a, a
	jr	Z,00104$
	ld	b, #0x00
	jr	00120$
00104$:
;src/main.c:74: else if ( cpct_isKeyPressed(Key_2)           ) animrequest = es_win;
	push	bc
	ld	hl, #0x0208
	call	_cpct_isKeyPressed
	pop	bc
	ld	a, l
	or	a, a
	jr	Z,00120$
	ld	b, #0x06
00120$:
;src/main.c:77: if (animrequest != es_stop)
	ld	a, b
	dec	a
	ret	Z
;src/main.c:78: setAnimation(user, animrequest);
	push	bc
	inc	sp
	ld	hl, #3
	add	hl, sp
	ld	c, (hl)
	inc	hl
	ld	b, (hl)
	push	bc
	call	_setAnimation
	pop	af
	inc	sp
	ret
;src/main.c:91: void main(void) {
;	---------------------------------
; Function main
; ---------------------------------
_main::
;src/main.c:95: initializeCPC();
	call	_initializeCPC
;src/main.c:96: persea = getPersea();
	call	_getPersea
;src/main.c:99: while(1) {
00102$:
;src/main.c:100: updateUser(persea);
	push	hl
	push	hl
	call	_updateUser
	pop	af
	call	_cpct_waitVSYNC
	pop	hl
;src/main.c:102: updateEntity(persea);
	push	hl
	push	hl
	call	_updateEntity
	pop	af
	pop	hl
;src/main.c:103: drawEntity(persea);
	push	hl
	push	hl
	call	_drawEntity
	pop	af
	pop	hl
	jr	00102$
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
