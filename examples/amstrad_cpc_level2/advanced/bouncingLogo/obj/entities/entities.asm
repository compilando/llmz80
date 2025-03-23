;--------------------------------------------------------
; File Created by SDCC : free open source ANSI-C Compiler
; Version 3.6.8 #9946 (Linux)
;--------------------------------------------------------
	.module entities
	.optsdcc -mz80
	
;--------------------------------------------------------
; Public variables in this module
;--------------------------------------------------------
	.globl _cpct_getScreenPtr
	.globl _g_gravity
	.globl _moveEntityX
	.globl _moveEntityY
	.globl _entityPhysicsUpdate
	.globl _updateEntities
;--------------------------------------------------------
; special function registers
;--------------------------------------------------------
;--------------------------------------------------------
; ram data
;--------------------------------------------------------
	.area _DATA
_g_gravity::
	.ds 4
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
;src/entities/entities.c:38: i8 moveEntityX (TEntity* ent, i8 mx, u8 sx) {
;	---------------------------------
; Function moveEntityX
; ---------------------------------
_moveEntityX::
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	hl, #-14
	add	hl, sp
	ld	sp, hl
;src/entities/entities.c:39: i8 bounced = 0;
	ld	-13 (ix), #0x00
;src/entities/entities.c:47: if (umx <= ent->x) {
	ld	a, 4 (ix)
	ld	-2 (ix), a
	ld	a, 5 (ix)
	ld	-1 (ix), a
;src/entities/entities.c:49: ent->videopos -= umx;
	ld	a, -2 (ix)
	add	a, #0x02
	ld	-4 (ix), a
	ld	a, -1 (ix)
	adc	a, #0x00
	ld	-3 (ix), a
;src/entities/entities.c:47: if (umx <= ent->x) {
	ld	a, -2 (ix)
	add	a, #0x04
	ld	-6 (ix), a
	ld	a, -1 (ix)
	adc	a, #0x00
	ld	-5 (ix), a
;src/entities/entities.c:42: if (mx < 0) {
	bit	7, 6 (ix)
	jp	Z, 00110$
;src/entities/entities.c:44: u8 umx = -mx;
	xor	a, a
	sub	a, 6 (ix)
	ld	-14 (ix), a
;src/entities/entities.c:47: if (umx <= ent->x) {
	ld	l,-6 (ix)
	ld	h,-5 (ix)
	ld	a, (hl)
	ld	-7 (ix), a
	sub	a, -14 (ix)
	jr	C,00102$
;src/entities/entities.c:48: ent->x        -= umx;
	ld	a, -7 (ix)
	sub	a, -14 (ix)
	ld	-8 (ix), a
	ld	l,-6 (ix)
	ld	h,-5 (ix)
	ld	a, -8 (ix)
	ld	(hl), a
;src/entities/entities.c:49: ent->videopos -= umx;
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	a, (hl)
	ld	-10 (ix), a
	inc	hl
	ld	a, (hl)
	ld	-9 (ix), a
	ld	a, -14 (ix)
	ld	-12 (ix), a
	ld	-11 (ix), #0x00
	ld	a, -10 (ix)
	sub	a, -12 (ix)
	ld	-12 (ix), a
	ld	a, -9 (ix)
	sbc	a, -11 (ix)
	ld	-11 (ix), a
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	a, -12 (ix)
	ld	(hl), a
	inc	hl
	ld	a, -11 (ix)
	ld	(hl), a
	jp	00111$
00102$:
;src/entities/entities.c:52: ent->videopos -= ent->x;
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	c, (hl)
	inc	hl
	ld	b, (hl)
	ld	e, -7 (ix)
	ld	d, #0x00
	ld	a, c
	sub	a, e
	ld	c, a
	ld	a, b
	sbc	a, d
	ld	b, a
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	(hl), c
	inc	hl
	ld	(hl), b
;src/entities/entities.c:53: ent->x         = 0;
	ld	l,-6 (ix)
	ld	h,-5 (ix)
	ld	(hl), #0x00
;src/entities/entities.c:54: bounced = 1;
	ld	-13 (ix), #0x01
	jr	00111$
00110$:
;src/entities/entities.c:57: } else if (mx) {
	ld	a, 6 (ix)
	or	a, a
	jr	Z,00111$
;src/entities/entities.c:59: u8 space_left = sx - ent->width - ent->x;
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	ld	de, #0x0006
	add	hl, de
	ld	a,7 (ix)
	sub	a,(hl)
	ld	c, a
	ld	l,-6 (ix)
	ld	h,-5 (ix)
	ld	l, (hl)
	ld	a, c
	sub	a, l
	ld	c, a
;src/entities/entities.c:60: u8 umx = mx;
	ld	e, 6 (ix)
;src/entities/entities.c:63: if (umx > space_left) {
	ld	a, c
	sub	a, e
	jr	NC,00105$
;src/entities/entities.c:65: ent->x        += space_left;
	ld	a, l
	add	a, c
	ld	l,-6 (ix)
	ld	h,-5 (ix)
	ld	(hl), a
;src/entities/entities.c:66: ent->videopos += space_left;
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	e, (hl)
	inc	hl
	ld	b, (hl)
	ld	a, e
	add	a, c
	ld	c, a
	ld	a, b
	adc	a, #0x00
	ld	b, a
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	(hl), c
	inc	hl
	ld	(hl), b
;src/entities/entities.c:67: bounced = 1;
	ld	-13 (ix), #0x01
	jr	00111$
00105$:
;src/entities/entities.c:69: ent->x        += umx;
	ld	a, l
	add	a, e
	ld	l,-6 (ix)
	ld	h,-5 (ix)
	ld	(hl), a
;src/entities/entities.c:70: ent->videopos += umx;
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	c, (hl)
	inc	hl
	ld	b, (hl)
	ld	a, c
	add	a, e
	ld	c, a
	ld	a, b
	adc	a, #0x00
	ld	b, a
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	(hl), c
	inc	hl
	ld	(hl), b
00111$:
;src/entities/entities.c:75: return bounced;
	ld	l, -13 (ix)
	ld	sp, ix
	pop	ix
	ret
;src/entities/entities.c:87: i8 moveEntityY (TEntity* ent, i8 my, u8 sy) {
;	---------------------------------
; Function moveEntityY
; ---------------------------------
_moveEntityY::
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	hl, #-8
	add	hl, sp
	ld	sp, hl
;src/entities/entities.c:88: i8 bounced = 0;
	ld	c, #0x00
;src/entities/entities.c:96: if (umy <= ent->y) {
	ld	e,4 (ix)
	ld	d,5 (ix)
;src/entities/entities.c:98: ent->videopos  = cpct_getScreenPtr(CPCT_VMEM_START, ent->x, 2*ent->y);
	ld	hl, #0x0002
	add	hl,de
	ld	-2 (ix), l
	ld	-1 (ix), h
	ld	hl, #0x0004
	add	hl,de
	ld	-6 (ix), l
	ld	-5 (ix), h
;src/entities/entities.c:96: if (umy <= ent->y) {
	ld	hl, #0x0005
	add	hl,de
	ld	-4 (ix), l
	ld	-3 (ix), h
;src/entities/entities.c:91: if (my < 0) {
	bit	7, 6 (ix)
	jr	Z,00110$
;src/entities/entities.c:93: u8 umy = -my;
	xor	a, a
	sub	a, 6 (ix)
	ld	b, a
;src/entities/entities.c:96: if (umy <= ent->y) {
	ld	l,-4 (ix)
	ld	h,-3 (ix)
;src/entities/entities.c:97: ent->y        -= umy;
	ld	a, (hl)
	cp	a,b
	jr	C,00102$
	sub	a, b
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	(hl), a
;src/entities/entities.c:98: ent->videopos  = cpct_getScreenPtr(CPCT_VMEM_START, ent->x, 2*ent->y);
	add	a, a
	ld	d, a
	ld	l,-6 (ix)
	ld	h,-5 (ix)
	ld	b, (hl)
	push	bc
	ld	e, b
	push	de
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
	ex	de,hl
	pop	bc
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	ld	(hl), e
	inc	hl
	ld	(hl), d
	jp	00111$
00102$:
;src/entities/entities.c:101: ent->videopos  = CPCT_VMEM_START + ent->x;
	ld	l,-6 (ix)
	ld	h,-5 (ix)
	ld	c, (hl)
	ld	a,#0x00
	add	a,#0xc0
	ld	b, a
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	ld	(hl), c
	inc	hl
	ld	(hl), b
;src/entities/entities.c:102: ent->y         = 0;
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	(hl), #0x00
;src/entities/entities.c:103: bounced = 1;
	ld	c, #0x01
	jr	00111$
00110$:
;src/entities/entities.c:106: } else if (my) {
	ld	a, 6 (ix)
	or	a, a
	jr	Z,00111$
;src/entities/entities.c:108: u8 space_left = sy - (ent->height>>1) - ent->y;
	inc	sp
	inc	sp
	push	de
	pop	hl
	push	hl
	ld	de, #0x0007
	add	hl, de
	ld	b, (hl)
	srl	b
	ld	a, 7 (ix)
	sub	a, b
	ld	e, a
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	b, (hl)
	ld	a, e
	sub	a, b
	ld	l, a
;src/entities/entities.c:109: u8 umy = my;
	ld	d, 6 (ix)
;src/entities/entities.c:112: if (umy > space_left) {
	ld	a, l
	sub	a, d
	jr	NC,00105$
;src/entities/entities.c:114: ent->y  = sy - (ent->height>>1);
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	(hl), e
;src/entities/entities.c:115: bounced = 1;
	ld	c, #0x01
	jr	00106$
00105$:
;src/entities/entities.c:117: ent->y += umy;
	ld	a, b
	add	a, d
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	(hl), a
00106$:
;src/entities/entities.c:120: ent->videopos = cpct_getScreenPtr(CPCT_VMEM_START, ent->x, 2*ent->y);
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	b, (hl)
	sla	b
	ld	l,-6 (ix)
	ld	h,-5 (ix)
	ld	d, (hl)
	push	bc
	ld	c, d
	push	bc
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
	ex	de,hl
	pop	bc
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	ld	(hl), e
	inc	hl
	ld	(hl), d
00111$:
;src/entities/entities.c:123: return bounced;
	ld	l, c
	ld	sp, ix
	pop	ix
	ret
;src/entities/entities.c:133: void entityPhysicsUpdate (TVelocity *vel, f32 ax, f32 ay) {
;	---------------------------------
; Function entityPhysicsUpdate
; ---------------------------------
_entityPhysicsUpdate::
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	hl, #-12
	add	hl, sp
	ld	sp, hl
;src/entities/entities.c:135: vel->vx += ax;
	ld	a, 4 (ix)
	ld	-2 (ix), a
	ld	a, 5 (ix)
	ld	-1 (ix), a
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	ld	c, (hl)
	inc	hl
	ld	b, (hl)
	inc	hl
	ld	e, (hl)
	inc	hl
	ld	d, (hl)
	ld	l,8 (ix)
	ld	h,9 (ix)
	push	hl
	ld	l,6 (ix)
	ld	h,7 (ix)
	push	hl
	push	de
	push	bc
	call	___fsadd
	pop	af
	pop	af
	pop	af
	pop	af
	ld	-9 (ix), d
	ld	-10 (ix), e
	ld	-11 (ix), h
	ld	-12 (ix), l
	ld	e,-2 (ix)
	ld	d,-1 (ix)
	ld	hl, #0x0000
	add	hl, sp
	ld	bc, #0x0004
	ldir
;src/entities/entities.c:136: vel->vy += ay;
	ld	a, -2 (ix)
	add	a, #0x04
	ld	-4 (ix), a
	ld	a, -1 (ix)
	adc	a, #0x00
	ld	-3 (ix), a
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	c, (hl)
	inc	hl
	ld	b, (hl)
	inc	hl
	ld	e, (hl)
	inc	hl
	ld	d, (hl)
	ld	l,12 (ix)
	ld	h,13 (ix)
	push	hl
	ld	l,10 (ix)
	ld	h,11 (ix)
	push	hl
	push	de
	push	bc
	call	___fsadd
	pop	af
	pop	af
	pop	af
	pop	af
	ld	c, l
	ld	b, h
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	(hl), c
	inc	hl
	ld	(hl), b
	inc	hl
	ld	(hl), e
	inc	hl
	ld	(hl), d
;src/entities/entities.c:139: vel->vy += g_gravity;
	ld	hl, (_g_gravity + 2)
	push	hl
	ld	hl, (_g_gravity)
	push	hl
	push	de
	push	bc
	call	___fsadd
	pop	af
	pop	af
	pop	af
	pop	af
	ld	c, l
	ld	b, h
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	(hl), c
	inc	hl
	ld	(hl), b
	inc	hl
	ld	(hl), e
	inc	hl
	ld	(hl), d
;src/entities/entities.c:142: if      (vel->vx >  vel->max_x) vel->vx= vel->max_x;
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	ld	c, (hl)
	inc	hl
	ld	b, (hl)
	inc	hl
	ld	e, (hl)
	inc	hl
	ld	d, (hl)
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	push	bc
	ld	bc, #0x0010
	add	hl, bc
	pop	bc
	ld	a, (hl)
	ld	-8 (ix), a
	inc	hl
	ld	a, (hl)
	ld	-7 (ix), a
	inc	hl
	ld	a, (hl)
	ld	-6 (ix), a
	inc	hl
	ld	a, (hl)
	ld	-5 (ix), a
	push	bc
	push	de
	ld	l,-6 (ix)
	ld	h,-5 (ix)
	push	hl
	ld	l,-8 (ix)
	ld	h,-7 (ix)
	push	hl
	ld	l,-10 (ix)
	ld	h,-9 (ix)
	push	hl
	ld	l,-12 (ix)
	ld	h,-11 (ix)
	push	hl
	call	___fsgt
	pop	af
	pop	af
	pop	af
	pop	af
	pop	de
	pop	bc
	ld	a, l
	or	a, a
	jr	Z,00104$
	ld	e,-2 (ix)
	ld	d,-1 (ix)
	ld	hl, #0x0004
	add	hl, sp
	ld	bc, #0x0004
	ldir
	jr	00105$
00104$:
;src/entities/entities.c:143: else if (vel->vx < -vel->max_x) vel->vx=-vel->max_x;
	ld	a, -5 (ix)
	xor	a,#0x80
	ld	-5 (ix), a
	ld	a, -8 (ix)
	ld	-8 (ix), a
	ld	a, -7 (ix)
	ld	-7 (ix), a
	ld	a, -6 (ix)
	ld	-6 (ix), a
	ld	l, a
	ld	h,-5 (ix)
	push	hl
	ld	l,-8 (ix)
	ld	h,-7 (ix)
	push	hl
	push	de
	push	bc
	call	___fslt
	pop	af
	pop	af
	pop	af
	pop	af
	ld	a, l
	or	a, a
	jr	Z,00105$
	ld	e,-2 (ix)
	ld	d,-1 (ix)
	ld	hl, #0x0004
	add	hl, sp
	ld	bc, #0x0004
	ldir
00105$:
;src/entities/entities.c:136: vel->vy += ay;
	ld	e,-4 (ix)
	ld	d,-3 (ix)
	ld	hl, #0x0004
	add	hl, sp
	ex	de, hl
	ld	bc, #0x0004
	ldir
;src/entities/entities.c:144: if      (vel->vy >  vel->max_y) vel->vy= vel->max_y;
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	ld	de, #0x0014
	add	hl, de
	ld	c, (hl)
	inc	hl
	ld	b, (hl)
	inc	hl
	ld	e, (hl)
	inc	hl
	ld	d, (hl)
	push	bc
	push	de
	push	de
	push	bc
	ld	l,-6 (ix)
	ld	h,-5 (ix)
	push	hl
	ld	l,-8 (ix)
	ld	h,-7 (ix)
	push	hl
	call	___fsgt
	pop	af
	pop	af
	pop	af
	pop	af
	pop	de
	pop	bc
	ld	a, l
	or	a, a
	jr	Z,00109$
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	(hl), c
	inc	hl
	ld	(hl), b
	inc	hl
	ld	(hl), e
	inc	hl
	ld	(hl), d
	jr	00110$
00109$:
;src/entities/entities.c:145: else if (vel->vy < -vel->max_y) vel->vy=-vel->max_y;
	ld	a, d
	xor	a,#0x80
	ld	d, a
	push	bc
	push	de
	push	de
	push	bc
	ld	l,-6 (ix)
	ld	h,-5 (ix)
	push	hl
	ld	l,-8 (ix)
	ld	h,-7 (ix)
	push	hl
	call	___fslt
	pop	af
	pop	af
	pop	af
	pop	af
	pop	de
	pop	bc
	ld	a, l
	or	a, a
	jr	Z,00110$
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	(hl), c
	inc	hl
	ld	(hl), b
	inc	hl
	ld	(hl), e
	inc	hl
	ld	(hl), d
00110$:
;src/entities/entities.c:148: vel->acum_x += vel->vx;
	ld	a, -2 (ix)
	add	a, #0x08
	ld	-8 (ix), a
	ld	a, -1 (ix)
	adc	a, #0x00
	ld	-7 (ix), a
	ld	e,-8 (ix)
	ld	d,-7 (ix)
	ld	hl, #0x0000
	add	hl, sp
	ex	de, hl
	ld	bc, #0x0004
	ldir
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	ld	c, (hl)
	inc	hl
	ld	b, (hl)
	inc	hl
	ld	e, (hl)
	inc	hl
	ld	d, (hl)
	push	de
	push	bc
	ld	l,-10 (ix)
	ld	h,-9 (ix)
	push	hl
	ld	l,-12 (ix)
	ld	h,-11 (ix)
	push	hl
	call	___fsadd
	pop	af
	pop	af
	pop	af
	pop	af
	ld	c, l
	ld	b, h
	ld	l,-8 (ix)
	ld	h,-7 (ix)
	ld	(hl), c
	inc	hl
	ld	(hl), b
	inc	hl
	ld	(hl), e
	inc	hl
	ld	(hl), d
;src/entities/entities.c:149: vel->acum_y += vel->vy;
	ld	a, -2 (ix)
	add	a, #0x0c
	ld	-8 (ix), a
	ld	a, -1 (ix)
	adc	a, #0x00
	ld	-7 (ix), a
	ld	e,-8 (ix)
	ld	d,-7 (ix)
	ld	hl, #0x0000
	add	hl, sp
	ex	de, hl
	ld	bc, #0x0004
	ldir
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	c, (hl)
	inc	hl
	ld	b, (hl)
	inc	hl
	ld	e, (hl)
	inc	hl
	ld	d, (hl)
	push	de
	push	bc
	ld	l,-10 (ix)
	ld	h,-9 (ix)
	push	hl
	ld	l,-12 (ix)
	ld	h,-11 (ix)
	push	hl
	call	___fsadd
	pop	af
	pop	af
	pop	af
	pop	af
	ld	c, l
	ld	b, h
	ld	l,-8 (ix)
	ld	h,-7 (ix)
	ld	(hl), c
	inc	hl
	ld	(hl), b
	inc	hl
	ld	(hl), e
	inc	hl
	ld	(hl), d
	ld	sp, ix
	pop	ix
	ret
;src/entities/entities.c:156: void updateEntities(TEntity *logo, f32 ax, f32 ay) {
;	---------------------------------
; Function updateEntities
; ---------------------------------
_updateEntities::
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	hl, #-12
	add	hl, sp
	ld	sp, hl
;src/entities/entities.c:158: i8 dx=0, dy=0;
	ld	-11 (ix), #0x00
	ld	-12 (ix), #0x00
;src/entities/entities.c:161: entityPhysicsUpdate(&logo->vel, ax, ay);
	ld	a, 4 (ix)
	ld	-2 (ix), a
	ld	a, 5 (ix)
	ld	-1 (ix), a
	ld	a, -2 (ix)
	add	a, #0x08
	ld	-10 (ix), a
	ld	a, -1 (ix)
	adc	a, #0x00
	ld	-9 (ix), a
	ld	l,12 (ix)
	ld	h,13 (ix)
	push	hl
	ld	l,10 (ix)
	ld	h,11 (ix)
	push	hl
	ld	l,8 (ix)
	ld	h,9 (ix)
	push	hl
	ld	l,6 (ix)
	ld	h,7 (ix)
	push	hl
	ld	l,-10 (ix)
	ld	h,-9 (ix)
	push	hl
	call	_entityPhysicsUpdate
	ld	hl, #10
	add	hl, sp
	ld	sp, hl
;src/entities/entities.c:165: if      (logo->vel.acum_x > 1 ) { dx =  1; logo->vel.acum_x-=1.0; }
	ld	a, -2 (ix)
	add	a, #0x10
	ld	-4 (ix), a
	ld	a, -1 (ix)
	adc	a, #0x00
	ld	-3 (ix), a
	ld	e,-4 (ix)
	ld	d,-3 (ix)
	ld	hl, #0x0004
	add	hl, sp
	ex	de, hl
	ld	bc, #0x0004
	ldir
	ld	hl, #0x3f80
	push	hl
	ld	hl, #0x0000
	push	hl
	ld	l,-6 (ix)
	ld	h,-5 (ix)
	push	hl
	ld	l,-8 (ix)
	ld	h,-7 (ix)
	push	hl
	call	___fsgt
	pop	af
	pop	af
	pop	af
	pop	af
	ld	a, l
	or	a, a
	jr	Z,00104$
	ld	-11 (ix), #0x01
	ld	hl, #0x3f80
	push	hl
	ld	hl, #0x0000
	push	hl
	ld	l,-6 (ix)
	ld	h,-5 (ix)
	push	hl
	ld	l,-8 (ix)
	ld	h,-7 (ix)
	push	hl
	call	___fssub
	pop	af
	pop	af
	pop	af
	pop	af
	ld	c, l
	ld	b, h
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	(hl), c
	inc	hl
	ld	(hl), b
	inc	hl
	ld	(hl), e
	inc	hl
	ld	(hl), d
	jr	00105$
00104$:
;src/entities/entities.c:166: else if (logo->vel.acum_x < -1) { dx = -1; logo->vel.acum_x+=1.0; }
	ld	hl, #0xbf80
	push	hl
	ld	hl, #0x0000
	push	hl
	ld	l,-6 (ix)
	ld	h,-5 (ix)
	push	hl
	ld	l,-8 (ix)
	ld	h,-7 (ix)
	push	hl
	call	___fslt
	pop	af
	pop	af
	pop	af
	pop	af
	ld	a, l
	or	a, a
	jr	Z,00105$
	ld	-11 (ix), #0xff
	ld	hl, #0x3f80
	push	hl
	ld	hl, #0x0000
	push	hl
	ld	l,-6 (ix)
	ld	h,-5 (ix)
	push	hl
	ld	l,-8 (ix)
	ld	h,-7 (ix)
	push	hl
	call	___fsadd
	pop	af
	pop	af
	pop	af
	pop	af
	ld	c, l
	ld	b, h
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	(hl), c
	inc	hl
	ld	(hl), b
	inc	hl
	ld	(hl), e
	inc	hl
	ld	(hl), d
00105$:
;src/entities/entities.c:167: if      (logo->vel.acum_y > 1 ) { dy =  1; logo->vel.acum_y-=1.0; }
	ld	a, -2 (ix)
	add	a, #0x14
	ld	-8 (ix), a
	ld	a, -1 (ix)
	adc	a, #0x00
	ld	-7 (ix), a
	ld	l,-8 (ix)
	ld	h,-7 (ix)
	ld	c, (hl)
	inc	hl
	ld	b, (hl)
	inc	hl
	ld	e, (hl)
	inc	hl
	ld	d, (hl)
	push	bc
	push	de
	ld	hl, #0x3f80
	push	hl
	ld	hl, #0x0000
	push	hl
	push	de
	push	bc
	call	___fsgt
	pop	af
	pop	af
	pop	af
	pop	af
	pop	de
	pop	bc
	ld	a, l
	or	a, a
	jr	Z,00109$
	ld	-12 (ix), #0x01
	ld	hl, #0x3f80
	push	hl
	ld	hl, #0x0000
	push	hl
	push	de
	push	bc
	call	___fssub
	pop	af
	pop	af
	pop	af
	pop	af
	ld	c, l
	ld	b, h
	ld	l,-8 (ix)
	ld	h,-7 (ix)
	ld	(hl), c
	inc	hl
	ld	(hl), b
	inc	hl
	ld	(hl), e
	inc	hl
	ld	(hl), d
	jr	00110$
00109$:
;src/entities/entities.c:168: else if (logo->vel.acum_y < -1) { dy = -1; logo->vel.acum_y+=1.0; }
	push	bc
	push	de
	ld	hl, #0xbf80
	push	hl
	ld	hl, #0x0000
	push	hl
	push	de
	push	bc
	call	___fslt
	pop	af
	pop	af
	pop	af
	pop	af
	pop	de
	pop	bc
	ld	a, l
	or	a, a
	jr	Z,00110$
	ld	-12 (ix), #0xff
	ld	hl, #0x3f80
	push	hl
	ld	hl, #0x0000
	push	hl
	push	de
	push	bc
	call	___fsadd
	pop	af
	pop	af
	pop	af
	pop	af
	ld	c, l
	ld	b, h
	ld	l,-8 (ix)
	ld	h,-7 (ix)
	ld	(hl), c
	inc	hl
	ld	(hl), b
	inc	hl
	ld	(hl), e
	inc	hl
	ld	(hl), d
00110$:
;src/entities/entities.c:173: if (moveEntityX(logo, dx,  80) ) {
	ld	a, #0x50
	push	af
	inc	sp
	ld	a, -11 (ix)
	push	af
	inc	sp
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	push	hl
	call	_moveEntityX
	pop	af
	pop	af
	ld	a, l
	or	a, a
	jr	Z,00112$
;src/entities/entities.c:174: logo->vel.vx = -logo->vel.vx*bounceCoefficient;
	ld	l,-10 (ix)
	ld	h,-9 (ix)
	ld	c, (hl)
	inc	hl
	ld	b, (hl)
	inc	hl
	ld	e, (hl)
	inc	hl
	ld	a, (hl)
	xor	a,#0x80
	ld	d, a
	ld	hl, #0x3f59
	push	hl
	ld	hl, #0x999a
	push	hl
	push	de
	push	bc
	call	___fsmul
	pop	af
	pop	af
	pop	af
	pop	af
	ld	c, l
	ld	b, h
	ld	l,-10 (ix)
	ld	h,-9 (ix)
	ld	(hl), c
	inc	hl
	ld	(hl), b
	inc	hl
	ld	(hl), e
	inc	hl
	ld	(hl), d
00112$:
;src/entities/entities.c:176: if (moveEntityY(logo, dy, 100) ) {
	ld	a, #0x64
	push	af
	inc	sp
	ld	a, -12 (ix)
	push	af
	inc	sp
	ld	l,4 (ix)
	ld	h,5 (ix)
	push	hl
	call	_moveEntityY
	pop	af
	pop	af
	ld	a, l
	or	a, a
	jr	Z,00115$
;src/entities/entities.c:177: logo->vel.vy = -logo->vel.vy*bounceCoefficient;
	ld	a, -2 (ix)
	add	a, #0x0c
	ld	-8 (ix), a
	ld	a, -1 (ix)
	adc	a, #0x00
	ld	-7 (ix), a
	ld	l,-8 (ix)
	ld	h,-7 (ix)
	ld	c, (hl)
	inc	hl
	ld	b, (hl)
	inc	hl
	ld	e, (hl)
	inc	hl
	ld	a, (hl)
	xor	a,#0x80
	ld	d, a
	ld	hl, #0x3f59
	push	hl
	ld	hl, #0x999a
	push	hl
	push	de
	push	bc
	call	___fsmul
	pop	af
	pop	af
	pop	af
	pop	af
	ld	c, l
	ld	b, h
	ld	l,-8 (ix)
	ld	h,-7 (ix)
	ld	(hl), c
	inc	hl
	ld	(hl), b
	inc	hl
	ld	(hl), e
	inc	hl
	ld	(hl), d
00115$:
	ld	sp, ix
	pop	ix
	ret
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
