;--------------------------------------------------------
; File Created by SDCC : free open source ANSI-C Compiler
; Version 3.6.8 #9946 (Linux)
;--------------------------------------------------------
	.module entities
	.optsdcc -mz80
	
;--------------------------------------------------------
; Public variables in this module
;--------------------------------------------------------
	.globl _updateAnimation
	.globl _cpct_getScreenPtr
	.globl _cpct_drawSprite
	.globl _cpct_drawSolidBox
	.globl _g_SCR_HEIGHT
	.globl _g_SCR_WIDTH
	.globl _g_persea
	.globl _g_perseaAnimation
	.globl _g_animDie
	.globl _g_animWin
	.globl _g_animHit
	.globl _g_animKick
	.globl _g_animFist
	.globl _g_animWalkLeft
	.globl _g_animWalkRight
	.globl _g_animStay
	.globl _g_allAnimFrames
	.globl _getPersea
	.globl _moveEntityX
	.globl _moveEntityY
	.globl _updateEntity
	.globl _setAnimation
	.globl _drawEntity
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
;src/entities/entities.c:102: TEntity* getPersea() {
;	---------------------------------
; Function getPersea
; ---------------------------------
_getPersea::
;src/entities/entities.c:103: return (TEntity*)g_persea;
	ld	hl, #_g_persea+0
	ret
_g_allAnimFrames:
	.dw _gc_PerseaWalk2
	.db #0x08	; 8
	.db #0x18	; 24
	.db #0x02	;  2
	.db #0x00	;  0
	.db #0x00	;  0
	.db #0x00	;  0
	.db #0x00	;  0
	.db #0x04	; 4
	.dw _gc_PerseaWalk13
	.db #0x08	; 8
	.db #0x18	; 24
	.db #0x02	;  2
	.db #0x00	;  0
	.db #0x00	;  0
	.db #0x03	;  3
	.db #0x18	;  24
	.db #0x04	; 4
	.dw _gc_PerseaWalk4
	.db #0x08	; 8
	.db #0x18	; 24
	.db #0x02	;  2
	.db #0x00	;  0
	.db #0x00	;  0
	.db #0x00	;  0
	.db #0x00	;  0
	.db #0x04	; 4
	.dw _gc_PerseaWalk4
	.db #0x08	; 8
	.db #0x18	; 24
	.db #0xfe	; -2
	.db #0x00	;  0
	.db #0x00	;  0
	.db #0x00	;  0
	.db #0x00	;  0
	.db #0x04	; 4
	.dw _gc_PerseaWalk13
	.db #0x08	; 8
	.db #0x18	; 24
	.db #0xfe	; -2
	.db #0x00	;  0
	.db #0x06	;  6
	.db #0x03	;  3
	.db #0x18	;  24
	.db #0x04	; 4
	.dw _gc_PerseaWalk2
	.db #0x08	; 8
	.db #0x18	; 24
	.db #0xfe	; -2
	.db #0x00	;  0
	.db #0x00	;  0
	.db #0x00	;  0
	.db #0x00	;  0
	.db #0x04	; 4
	.dw _gc_PerseaFist
	.db #0x09	; 9
	.db #0x18	; 24
	.db #0x00	;  0
	.db #0x00	;  0
	.db #0x06	;  6
	.db #0x03	;  3
	.db #0x06	;  6
	.db #0x0f	; 15
	.dw _gc_PerseaKick
	.db #0x09	; 9
	.db #0x18	; 24
	.db #0x00	;  0
	.db #0x00	;  0
	.db #0x06	;  6
	.db #0x03	;  3
	.db #0x0c	;  12
	.db #0x19	; 25
	.dw _gc_PerseaHit
	.db #0x08	; 8
	.db #0x18	; 24
	.db #0x00	;  0
	.db #0x00	;  0
	.db #0x00	;  0
	.db #0x00	;  0
	.db #0x00	;  0
	.db #0x19	; 25
	.dw _gc_PerseaKO
	.db #0x0c	; 12
	.db #0x08	; 8
	.db #0xfc	; -4
	.db #0x10	;  16
	.db #0x02	;  2
	.db #0x04	;  4
	.db #0x10	;  16
	.db #0x32	; 50	'2'
	.dw _gc_PerseaWins
	.db #0x08	; 8
	.db #0x18	; 24
	.db #0x00	;  0
	.db #0x00	;  0
	.db #0x00	;  0
	.db #0x00	;  0
	.db #0x00	;  0
	.db #0x32	; 50	'2'
	.dw _gc_PerseaWalk13
	.db #0x08	; 8
	.db #0x18	; 24
	.db #0x00	;  0
	.db #0x00	;  0
	.db #0x06	;  6
	.db #0x03	;  3
	.db #0x18	;  24
	.db #0x01	; 1
	.dw _gc_PerseaWalk13
	.db #0x08	; 8
	.db #0x18	; 24
	.db #0x00	;  0
	.db #0x00	;  0
	.db #0x00	;  0
	.db #0x00	;  0
	.db #0x00	;  0
	.db #0x01	; 1
	.dw _gc_PerseaWalk13
	.db #0x08	; 8
	.db #0x18	; 24
	.db #0x04	;  4
	.db #0xf0	; -16
	.db #0x00	;  0
	.db #0x0c	;  12
	.db #0x08	;  8
	.db #0x01	; 1
_g_animStay:
	.dw (_g_allAnimFrames + 40)
	.dw #0x0000
_g_animWalkRight:
	.dw (_g_allAnimFrames + 0)
	.dw (_g_allAnimFrames + 10)
	.dw (_g_allAnimFrames + 20)
	.dw (_g_allAnimFrames + 10)
	.dw #0x0000
_g_animWalkLeft:
	.dw (_g_allAnimFrames + 30)
	.dw (_g_allAnimFrames + 40)
	.dw (_g_allAnimFrames + 50)
	.dw (_g_allAnimFrames + 40)
	.dw #0x0000
_g_animFist:
	.dw (_g_allAnimFrames + 60)
	.dw (_g_allAnimFrames + 110)
	.dw #0x0000
_g_animKick:
	.dw (_g_allAnimFrames + 70)
	.dw (_g_allAnimFrames + 110)
	.dw #0x0000
_g_animHit:
	.dw (_g_allAnimFrames + 80)
	.dw (_g_allAnimFrames + 120)
	.dw #0x0000
_g_animWin:
	.dw (_g_allAnimFrames + 100)
	.dw (_g_allAnimFrames + 110)
	.dw #0x0000
_g_animDie:
	.dw (_g_allAnimFrames + 90)
	.dw (_g_allAnimFrames + 130)
	.dw #0x0000
_g_perseaAnimation:
	.dw _g_animStay
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x03	; 3
_g_persea:
	.dw _g_perseaAnimation
	.dw #0xc2d0
	.db #0x00	; 0
	.db #0x48	; 72	'H'
	.db #0x01	; 1
_g_SCR_WIDTH:
	.db #0x50	; 80	'P'
_g_SCR_HEIGHT:
	.db #0xc8	; 200
;src/entities/entities.c:113: i8 moveEntityX (TEntity* ent, i8 mx) {
;	---------------------------------
; Function moveEntityX
; ---------------------------------
_moveEntityX::
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	hl, #-15
	add	hl, sp
	ld	sp, hl
;src/entities/entities.c:114: u8 moved = 0;// Tells us how many bytes the entity has moved
	ld	-1 (ix), #0x00
;src/entities/entities.c:122: if (umx <= ent->x) {
	ld	a, 4 (ix)
	ld	-15 (ix), a
	ld	a, 5 (ix)
	ld	-14 (ix), a
;src/entities/entities.c:124: ent->videopos -= umx;
	ld	a, -15 (ix)
	add	a, #0x02
	ld	-9 (ix), a
	ld	a, -14 (ix)
	adc	a, #0x00
	ld	-8 (ix), a
;src/entities/entities.c:125: moved          = mx;
	ld	a, 6 (ix)
	ld	-10 (ix), a
;src/entities/entities.c:122: if (umx <= ent->x) {
	ld	a, -15 (ix)
	add	a, #0x04
	ld	-12 (ix), a
	ld	a, -14 (ix)
	adc	a, #0x00
	ld	-11 (ix), a
;src/entities/entities.c:118: if (mx < 0) {
	bit	7, 6 (ix)
	jp	Z, 00114$
;src/entities/entities.c:119: umx = -mx;   // umx = positive value of mx, that is negative
	xor	a, a
	sub	a, 6 (ix)
	ld	-13 (ix), a
;src/entities/entities.c:122: if (umx <= ent->x) {
	ld	l,-12 (ix)
	ld	h,-11 (ix)
	ld	a, (hl)
	ld	-2 (ix), a
	sub	a, -13 (ix)
	jr	C,00104$
;src/entities/entities.c:123: ent->x        -= umx;
	ld	a, -2 (ix)
	sub	a, -13 (ix)
	ld	-3 (ix), a
	ld	l,-12 (ix)
	ld	h,-11 (ix)
	ld	a, -3 (ix)
	ld	(hl), a
;src/entities/entities.c:124: ent->videopos -= umx;
	ld	l,-9 (ix)
	ld	h,-8 (ix)
	ld	a, (hl)
	ld	-5 (ix), a
	inc	hl
	ld	a, (hl)
	ld	-4 (ix), a
	ld	a, -13 (ix)
	ld	-7 (ix), a
	ld	-6 (ix), #0x00
	ld	a, -5 (ix)
	sub	a, -7 (ix)
	ld	-7 (ix), a
	ld	a, -4 (ix)
	sbc	a, -6 (ix)
	ld	-6 (ix), a
	ld	l,-9 (ix)
	ld	h,-8 (ix)
	ld	a, -7 (ix)
	ld	(hl), a
	inc	hl
	ld	a, -6 (ix)
	ld	(hl), a
;src/entities/entities.c:125: moved          = mx;
	ld	a, -10 (ix)
	ld	-1 (ix), a
	jp	00115$
00104$:
;src/entities/entities.c:126: } else if (ent->x) {
	ld	a, -2 (ix)
	or	a, a
	jp	Z, 00115$
;src/entities/entities.c:128: ent->videopos -= ent->x;
	ld	l,-9 (ix)
	ld	h,-8 (ix)
	ld	c, (hl)
	inc	hl
	ld	b, (hl)
	ld	e, -2 (ix)
	ld	d, #0x00
	ld	a, c
	sub	a, e
	ld	c, a
	ld	a, b
	sbc	a, d
	ld	b, a
	ld	l,-9 (ix)
	ld	h,-8 (ix)
	ld	(hl), c
	inc	hl
	ld	(hl), b
;src/entities/entities.c:129: moved          = -ent->x;
	ld	l,-12 (ix)
	ld	h,-11 (ix)
	ld	c, (hl)
	xor	a, a
	sub	a, c
	ld	-1 (ix), a
;src/entities/entities.c:130: ent->x         = 0;
	ld	l,-12 (ix)
	ld	h,-11 (ix)
	ld	(hl), #0x00
	jp	00115$
00114$:
;src/entities/entities.c:133: } else if (mx) {
	ld	a, 6 (ix)
	or	a, a
	jp	Z, 00115$
;src/entities/entities.c:139: anim = ent->anim; 
	pop	hl
	push	hl
	ld	a, (hl)
	inc	hl
	ld	h, (hl)
	ld	l, a
;src/entities/entities.c:140: space_left = g_SCR_WIDTH - anim->frames[anim->frame_id]->width - ent->x;
	push	hl
	ld	c, (hl)
	inc	hl
	ld	b, (hl)
	pop	hl
	inc	hl
	inc	hl
	ld	l, (hl)
	ld	h, #0x00
	add	hl, hl
	add	hl, bc
	ld	a, (hl)
	inc	hl
	ld	h, (hl)
	ld	l, a
	inc	hl
	inc	hl
	ld	c, (hl)
	ld	a,(#_g_SCR_WIDTH + 0)
	sub	a, c
	ld	c, a
	ld	l,-12 (ix)
	ld	h,-11 (ix)
	ld	b, (hl)
	ld	a, c
	sub	a, b
;src/entities/entities.c:144: if (umx <= space_left) {
	ld	c,a
	sub	a, -10 (ix)
	jr	C,00109$
;src/entities/entities.c:145: ent->x        += umx;
	ld	a, b
	add	a, -10 (ix)
	ld	l,-12 (ix)
	ld	h,-11 (ix)
	ld	(hl), a
;src/entities/entities.c:146: ent->videopos += umx;
	ld	l,-9 (ix)
	ld	h,-8 (ix)
	ld	c, (hl)
	inc	hl
	ld	b, (hl)
	ld	a, c
	add	a, -10 (ix)
	ld	c, a
	ld	a, b
	adc	a, #0x00
	ld	b, a
	ld	l,-9 (ix)
	ld	h,-8 (ix)
	ld	(hl), c
	inc	hl
	ld	(hl), b
;src/entities/entities.c:147: moved         = umx;
	ld	a, -10 (ix)
	ld	-1 (ix), a
	jr	00115$
00109$:
;src/entities/entities.c:148: } else if (space_left) {
	ld	a, c
	or	a, a
	jr	Z,00115$
;src/entities/entities.c:150: ent->x        += space_left;
	ld	a, b
	add	a, c
	ld	l,-12 (ix)
	ld	h,-11 (ix)
	ld	(hl), a
;src/entities/entities.c:151: ent->videopos += space_left;
	ld	l,-9 (ix)
	ld	h,-8 (ix)
	ld	b, (hl)
	inc	hl
	ld	e, (hl)
	ld	a, b
	add	a, c
	ld	b, a
	ld	a, e
	adc	a, #0x00
	ld	e, a
	ld	l,-9 (ix)
	ld	h,-8 (ix)
	ld	(hl), b
	inc	hl
	ld	(hl), e
;src/entities/entities.c:152: moved         = space_left;
	ld	-1 (ix), c
00115$:
;src/entities/entities.c:157: return moved;
	ld	l, -1 (ix)
	ld	sp, ix
	pop	ix
	ret
;src/entities/entities.c:167: i8 moveEntityY (TEntity* ent, i8 my) {
;	---------------------------------
; Function moveEntityY
; ---------------------------------
_moveEntityY::
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	hl, #-11
	add	hl, sp
	ld	sp, hl
;src/entities/entities.c:168: i8 moved = 0;      // Number of bytes the entity has moved 
	ld	-10 (ix), #0x00
;src/entities/entities.c:176: if (umy <= ent->y) {
	ld	a, 4 (ix)
	ld	-2 (ix), a
	ld	a, 5 (ix)
	ld	-1 (ix), a
;src/entities/entities.c:178: ent->videopos  = cpct_getScreenPtr(CPCT_VMEM_START, ent->x, ent->y);
	ld	a, -2 (ix)
	add	a, #0x02
	ld	-9 (ix), a
	ld	a, -1 (ix)
	adc	a, #0x00
	ld	-8 (ix), a
	ld	a, -2 (ix)
	add	a, #0x04
	ld	-7 (ix), a
	ld	a, -1 (ix)
	adc	a, #0x00
	ld	-6 (ix), a
;src/entities/entities.c:179: moved          = my;
	ld	a, 6 (ix)
	ld	-5 (ix), a
;src/entities/entities.c:176: if (umy <= ent->y) {
	ld	a, -2 (ix)
	add	a, #0x05
	ld	-4 (ix), a
	ld	a, -1 (ix)
	adc	a, #0x00
	ld	-3 (ix), a
;src/entities/entities.c:172: if (my < 0) {
	bit	7, 6 (ix)
	jr	Z,00116$
;src/entities/entities.c:173: umy = -my;  // umy = possive value of my, that is negative.
	xor	a, a
	sub	a, 6 (ix)
	ld	b, a
;src/entities/entities.c:176: if (umy <= ent->y) {
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	c, (hl)
;src/entities/entities.c:177: ent->y        -= umy;
	ld	a,c
	cp	a,b
	jr	C,00104$
	sub	a, b
	ld	d, a
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	(hl), d
;src/entities/entities.c:178: ent->videopos  = cpct_getScreenPtr(CPCT_VMEM_START, ent->x, ent->y);
	ld	l,-7 (ix)
	ld	h,-6 (ix)
	ld	e, (hl)
	push	de
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
	ld	c, l
	ld	b, h
	ld	l,-9 (ix)
	ld	h,-8 (ix)
	ld	(hl), c
	inc	hl
	ld	(hl), b
;src/entities/entities.c:179: moved          = my;
	ld	a, -5 (ix)
	ld	-10 (ix), a
	jp	00117$
00104$:
;src/entities/entities.c:180: } else if ( ent->y ) {
	ld	a, c
	or	a, a
	jp	Z, 00117$
;src/entities/entities.c:182: ent->videopos  = CPCT_VMEM_START + ent->x;
	ld	l,-7 (ix)
	ld	h,-6 (ix)
	ld	c, (hl)
	ld	a,#0x00
	add	a,#0xc0
	ld	b, a
	ld	l,-9 (ix)
	ld	h,-8 (ix)
	ld	(hl), c
	inc	hl
	ld	(hl), b
;src/entities/entities.c:183: moved          = -ent->y;
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	c, (hl)
	xor	a, a
	sub	a, c
	ld	-10 (ix), a
;src/entities/entities.c:184: ent->y         = 0;
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	(hl), #0x00
	jp	00117$
00116$:
;src/entities/entities.c:187: } else if (my) {
	ld	a, 6 (ix)
	or	a, a
	jp	Z, 00117$
;src/entities/entities.c:193: anim       = ent->anim;
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	ld	a, (hl)
	inc	hl
	ld	h, (hl)
	ld	l, a
;src/entities/entities.c:194: space_left = g_SCR_HEIGHT - anim->frames[anim->frame_id]->height - ent->y;
	push	hl
	ld	c, (hl)
	inc	hl
	ld	b, (hl)
	pop	hl
	inc	hl
	inc	hl
	ld	l, (hl)
	ld	h, #0x00
	add	hl, hl
	add	hl, bc
	ld	a, (hl)
	inc	hl
	ld	h, (hl)
	ld	l, a
	inc	hl
	inc	hl
	inc	hl
	ld	c, (hl)
	ld	a,(#_g_SCR_HEIGHT + 0)
	sub	a, c
	ld	c, a
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	a, (hl)
	ld	-2 (ix), a
	ld	a, c
	sub	a, -2 (ix)
;src/entities/entities.c:197: if (umy <= space_left) {
	ld	-11 (ix), a
	sub	a, -5 (ix)
	jr	C,00109$
;src/entities/entities.c:198: ent->y  += umy;
	ld	a, -2 (ix)
	add	a, -5 (ix)
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	(hl), a
;src/entities/entities.c:199: moved    = umy;
	ld	a, -5 (ix)
	ld	-10 (ix), a
	jr	00110$
00109$:
;src/entities/entities.c:200: } else if (space_left) {
	ld	a, -11 (ix)
	or	a, a
	jr	Z,00110$
;src/entities/entities.c:202: ent->y  += space_left;
	ld	a, -2 (ix)
	add	a, -11 (ix)
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	(hl), a
;src/entities/entities.c:203: moved    = space_left;
	ld	a, -11 (ix)
	ld	-10 (ix), a
00110$:
;src/entities/entities.c:205: if (moved) {
	ld	a, -10 (ix)
	or	a, a
	jr	Z,00117$
;src/entities/entities.c:207: ent->videopos = cpct_getScreenPtr(CPCT_VMEM_START, ent->x, ent->y);
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	b, (hl)
	ld	l,-7 (ix)
	ld	h,-6 (ix)
	ld	c, (hl)
	push	bc
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
	ld	c, l
	ld	b, h
	ld	l,-9 (ix)
	ld	h,-8 (ix)
	ld	(hl), c
	inc	hl
	ld	(hl), b
00117$:
;src/entities/entities.c:212: return moved;
	ld	l, -10 (ix)
	ld	sp, ix
	pop	ix
	ret
;src/entities/entities.c:219: i8 updateAnimation(TAnimation* anim) {
;	---------------------------------
; Function updateAnimation
; ---------------------------------
_updateAnimation::
	push	ix
	ld	ix,#0
	add	ix,sp
	push	af
	push	af
	dec	sp
;src/entities/entities.c:220: i8 newframe = 0;
	ld	-5 (ix), #0x00
;src/entities/entities.c:223: if (anim->status != as_pause && anim->status != as_end) {
	ld	c,4 (ix)
	ld	b,5 (ix)
	ld	hl, #0x0004
	add	hl,bc
	ld	-2 (ix), l
	ld	-1 (ix), h
	ld	a, (hl)
	cp	a, #0x02
	jp	Z,00110$
	sub	a, #0x03
	jp	Z,00110$
;src/entities/entities.c:226: if ( ! --anim->time ) {
	ld	e, c
	ld	d, b
	inc	de
	inc	de
	inc	de
	ld	a, (de)
	add	a, #0xff
	ld	(de), a
	or	a, a
	jr	NZ,00110$
;src/entities/entities.c:230: newframe = 1;
	ld	-5 (ix), #0x01
;src/entities/entities.c:231: frame = anim->frames[ ++anim->frame_id ]; 
	ld	a, (bc)
	ld	-4 (ix), a
	inc	bc
	ld	a, (bc)
	ld	-3 (ix), a
	dec	bc
	push	bc
	pop	iy
	inc	iy
	inc	iy
	inc	0 (iy)
	ld	l, 0 (iy)
	ld	h, #0x00
	add	hl, hl
	ld	a, -4 (ix)
	add	a, l
	ld	l, a
	ld	a, -3 (ix)
	adc	a, h
	ld	h, a
	ld	a, (hl)
	inc	hl
	ld	h, (hl)
	ld	l, a
	ld	-4 (ix), l
	ld	-3 (ix), h
;src/entities/entities.c:234: if (frame) {
	ld	a, h
	or	a,l
	jr	Z,00105$
;src/entities/entities.c:236: anim->time = frame->time;  // Get animation cycles for this frame
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	bc, #0x0009
	add	hl, bc
	ld	a, (hl)
	ld	(de), a
	jr	00110$
00105$:
;src/entities/entities.c:237: } else if ( anim->status == as_cycle ) {
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	ld	l, (hl)
	dec	l
	jr	NZ,00102$
;src/entities/entities.c:239: anim->frame_id = 0;        // Next frame_id is first one of this animation
	ld	0 (iy), #0x00
;src/entities/entities.c:240: anim->time     = anim->frames[0]->time; // Restore animation cycles for the first frame
	ld	l, c
	ld	h, b
	ld	a, (hl)
	inc	hl
	ld	h, (hl)
	ld	l, a
	ld	a, (hl)
	inc	hl
	ld	h, (hl)
	ld	l, a
	ld	bc, #0x0009
	add	hl, bc
	ld	a, (hl)
	ld	(de), a
	jr	00110$
00102$:
;src/entities/entities.c:243: anim->status = as_end;  // Animation set to end status
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	ld	(hl), #0x03
;src/entities/entities.c:244: --anim->frame_id;       // frame_id decremented to leave animation permanently on last frame
	dec	0 (iy)
00110$:
;src/entities/entities.c:250: return newframe;
	ld	l, -5 (ix)
	ld	sp, ix
	pop	ix
	ret
;src/entities/entities.c:256: void updateEntity(TEntity *ent) {
;	---------------------------------
; Function updateEntity
; ---------------------------------
_updateEntity::
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	hl, #-7
	add	hl, sp
	ld	sp, hl
;src/entities/entities.c:257: TAnimation* anim = ent->anim;
	ld	a, 4 (ix)
	ld	-2 (ix), a
	ld	a, 5 (ix)
	ld	-1 (ix), a
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	ld	a, (hl)
	ld	-7 (ix), a
	inc	hl
	ld	a, (hl)
	ld	-6 (ix), a
;src/entities/entities.c:259: if ( updateAnimation(anim) ) {
	pop	hl
	push	hl
	push	hl
	call	_updateAnimation
	pop	af
	ld	a, l
	or	a, a
	jp	Z, 00117$
;src/entities/entities.c:260: if ( anim->status != as_end ) {
	pop	hl
	push	hl
	ld	de, #0x0004
	add	hl, de
	ld	c, (hl)
;src/entities/entities.c:261: TAnimFrame* frame = anim->frames[anim->frame_id];
	pop	hl
	push	hl
	inc	hl
	inc	hl
	ld	a, (hl)
	ld	-3 (ix), a
;src/entities/entities.c:260: if ( anim->status != as_end ) {
	ld	a, c
	sub	a, #0x03
	jp	Z,00113$
;src/entities/entities.c:261: TAnimFrame* frame = anim->frames[anim->frame_id];
	pop	hl
	push	hl
	ld	c, (hl)
	inc	hl
	ld	b, (hl)
	ld	l, -3 (ix)
	ld	h, #0x00
	add	hl, hl
	add	hl, bc
	ld	c, (hl)
	inc	hl
	ld	b, (hl)
;src/entities/entities.c:264: if (frame->ew) cpct_drawSolidBox(ent->videopos + (int)frame->ex, 0x00, frame->ew, frame->eh);
	push	bc
	pop	iy
	ld	a, 7 (iy)
	ld	-4 (ix), a
	or	a, a
	jr	Z,00102$
	push	bc
	pop	iy
	ld	a, 8 (iy)
	ld	-5 (ix), a
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	inc	hl
	inc	hl
	ld	e, (hl)
	inc	hl
	ld	d, (hl)
	push	bc
	pop	iy
	ld	l, 6 (iy)
	ld	a, l
	rla
	sbc	a, a
	ld	h, a
	add	hl,de
	ex	de,hl
	push	bc
	ld	h, -5 (ix)
	ld	l, -4 (ix)
	push	hl
	ld	hl, #0x0000
	push	hl
	push	de
	call	_cpct_drawSolidBox
	pop	bc
00102$:
;src/entities/entities.c:265: if (frame->mx) moveEntityX(ent, frame->mx);
	push	bc
	pop	iy
	ld	d, 4 (iy)
	ld	a, d
	or	a, a
	jr	Z,00104$
	push	bc
	push	de
	inc	sp
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	push	hl
	call	_moveEntityX
	pop	af
	inc	sp
	pop	bc
00104$:
;src/entities/entities.c:266: if (frame->my) moveEntityY(ent, frame->my);
	push	bc
	pop	iy
	ld	a, 5 (iy)
	or	a, a
	jr	Z,00106$
	push	bc
	push	af
	inc	sp
	ld	l,4 (ix)
	ld	h,5 (ix)
	push	hl
	call	_moveEntityY
	pop	af
	inc	sp
	pop	bc
00106$:
;src/entities/entities.c:269: if (frame->width + ent->x > g_SCR_WIDTH) {
	ld	l, c
	ld	h, b
	inc	hl
	inc	hl
	ld	c, (hl)
	ld	b, #0x00
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	ld	de, #0x0004
	add	hl, de
	ld	l, (hl)
	ld	h, #0x00
	add	hl, bc
	ld	a,(#_g_SCR_WIDTH + 0)
	ld	b, #0x00
	sub	a, l
	ld	a, b
	sbc	a, h
	jp	PO, 00148$
	xor	a, #0x80
00148$:
	jp	P, 00117$
;src/entities/entities.c:270: moveEntityX(ent, -1);
	ld	a, #0xff
	push	af
	inc	sp
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	push	hl
	call	_moveEntityX
	pop	af
	inc	sp
	jr	00117$
00113$:
;src/entities/entities.c:272: } else if (anim->frame_id == 0xFF) {
	ld	a, -3 (ix)
	inc	a
	jr	NZ,00110$
;src/entities/entities.c:273: cpct_drawSolidBox(CPCT_VMEM_START, 0xFF, 4, 8);
	ld	hl, #0x0804
	push	hl
	ld	hl, #0x00ff
	push	hl
	ld	hl, #0xc000
	push	hl
	call	_cpct_drawSolidBox
	jr	00117$
00110$:
;src/entities/entities.c:275: ent->status = es_stop;
	ld	a, -2 (ix)
	add	a, #0x06
	ld	l, a
	ld	a, -1 (ix)
	adc	a, #0x00
	ld	h, a
	ld	(hl), #0x01
00117$:
	ld	sp, ix
	pop	ix
	ret
;src/entities/entities.c:283: void setAnimation(TEntity *ent, TEntityStatus newstatus) {
;	---------------------------------
; Function setAnimation
; ---------------------------------
_setAnimation::
	push	ix
	ld	ix,#0
	add	ix,sp
	push	af
;src/entities/entities.c:284: TAnimation* anim = ent->anim;
	ld	c,4 (ix)
	ld	b,5 (ix)
	ld	l, c
	ld	h, b
	ld	e, (hl)
	inc	hl
	ld	d, (hl)
;src/entities/entities.c:287: if ( anim->status == as_end ) {
	ld	hl, #0x0004
	add	hl,de
	ex	(sp), hl
	pop	hl
	push	hl
	ld	a, (hl)
	sub	a, #0x03
	jp	NZ,00112$
;src/entities/entities.c:288: ent->status = newstatus;
	ld	hl, #0x0006
	add	hl, bc
	ld	a, 6 (ix)
	ld	(hl), a
;src/entities/entities.c:291: switch (newstatus) {
	ld	a, #0x07
	sub	a, 6 (ix)
	jr	C,00109$
	ld	c, 6 (ix)
	ld	b, #0x00
	ld	hl, #00124$
	add	hl, bc
	add	hl, bc
	add	hl, bc
	jp	(hl)
00124$:
	jp	00101$
	jp	00102$
	jp	00103$
	jp	00104$
	jp	00105$
	jp	00106$
	jp	00107$
	jp	00108$
;src/entities/entities.c:292: case es_dead:        { anim->frames = (TAnimFrame**)g_animDie;       break;  }
00101$:
	ld	l, e
	ld	h, d
	ld	(hl), #<(_g_animDie)
	inc	hl
	ld	(hl), #>(_g_animDie)
	jr	00109$
;src/entities/entities.c:293: case es_stop:        { anim->frames = (TAnimFrame**)g_animStay;      break;  }
00102$:
	ld	l, e
	ld	h, d
	ld	(hl), #<(_g_animStay)
	inc	hl
	ld	(hl), #>(_g_animStay)
	jr	00109$
;src/entities/entities.c:294: case es_walk_right:  { anim->frames = (TAnimFrame**)g_animWalkRight; break;  }
00103$:
	ld	l, e
	ld	h, d
	ld	(hl), #<(_g_animWalkRight)
	inc	hl
	ld	(hl), #>(_g_animWalkRight)
	jr	00109$
;src/entities/entities.c:295: case es_walk_left:   { anim->frames = (TAnimFrame**)g_animWalkLeft;  break;  }
00104$:
	ld	l, e
	ld	h, d
	ld	(hl), #<(_g_animWalkLeft)
	inc	hl
	ld	(hl), #>(_g_animWalkLeft)
	jr	00109$
;src/entities/entities.c:296: case es_fist:        { anim->frames = (TAnimFrame**)g_animFist;      break;  }
00105$:
	ld	l, e
	ld	h, d
	ld	(hl), #<(_g_animFist)
	inc	hl
	ld	(hl), #>(_g_animFist)
	jr	00109$
;src/entities/entities.c:297: case es_kick:        { anim->frames = (TAnimFrame**)g_animKick;      break;  }
00106$:
	ld	l, e
	ld	h, d
	ld	(hl), #<(_g_animKick)
	inc	hl
	ld	(hl), #>(_g_animKick)
	jr	00109$
;src/entities/entities.c:298: case es_win:         { anim->frames = (TAnimFrame**)g_animWin;       break;  }
00107$:
	ld	l, e
	ld	h, d
	ld	(hl), #<(_g_animWin)
	inc	hl
	ld	(hl), #>(_g_animWin)
	jr	00109$
;src/entities/entities.c:299: case es_hit:         { anim->frames = (TAnimFrame**)g_animHit;       break;  }
00108$:
	ld	l, e
	ld	h, d
	ld	(hl), #<(_g_animHit)
	inc	hl
	ld	(hl), #>(_g_animHit)
;src/entities/entities.c:300: }
00109$:
;src/entities/entities.c:303: anim->status=as_play;
	pop	hl
	push	hl
	ld	(hl), #0x00
;src/entities/entities.c:304: anim->frame_id = 0xFF;
	ld	l, e
	ld	h, d
	inc	hl
	inc	hl
	ld	(hl), #0xff
;src/entities/entities.c:305: anim->time = 1;
	inc	de
	inc	de
	inc	de
	ld	h, d
	ld	l, e
	ld	(hl), #0x01
00112$:
	ld	sp, ix
	pop	ix
	ret
;src/entities/entities.c:312: void drawEntity  (TEntity* ent){
;	---------------------------------
; Function drawEntity
; ---------------------------------
_drawEntity::
	push	ix
	ld	ix,#0
	add	ix,sp
	push	af
;src/entities/entities.c:314: TAnimation* anim  = ent->anim;
	ld	e,4 (ix)
	ld	d,5 (ix)
	ld	l, e
	ld	h, d
	ld	a, (hl)
	inc	hl
	ld	h, (hl)
	ld	l, a
;src/entities/entities.c:315: TAnimFrame* frame = anim->frames[anim->frame_id];
	push	hl
	ld	c, (hl)
	inc	hl
	ld	b, (hl)
	pop	hl
	inc	hl
	inc	hl
	ld	l, (hl)
	ld	h, #0x00
	add	hl, hl
	add	hl, bc
	ld	c, (hl)
	inc	hl
	ld	b, (hl)
;src/entities/entities.c:318: cpct_drawSprite(frame->sprite, ent->videopos, frame->width, frame->height);
	push	bc
	pop	iy
	ld	a, 3 (iy)
	ld	-1 (ix), a
	ld	l, c
	ld	h, b
	inc	hl
	inc	hl
	ld	a, (hl)
	ld	-2 (ix), a
	ex	de,hl
	inc	hl
	inc	hl
	ld	e, (hl)
	inc	hl
	ld	d, (hl)
	ld	l, c
	ld	h, b
	ld	c, (hl)
	inc	hl
	ld	b, (hl)
	ld	h, -1 (ix)
	ld	l, -2 (ix)
	push	hl
	push	de
	push	bc
	call	_cpct_drawSprite
	ld	sp, ix
	pop	ix
	ret
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
