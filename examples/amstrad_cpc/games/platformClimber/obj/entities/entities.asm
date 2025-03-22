;--------------------------------------------------------
; File Created by SDCC : free open source ANSI-C Compiler
; Version 3.6.8 #9946 (Linux)
;--------------------------------------------------------
	.module entities
	.optsdcc -mz80
	
;--------------------------------------------------------
; Public variables in this module
;--------------------------------------------------------
	.globl _cropVelocity
	.globl _getRandomUniform
	.globl _updateAnimation
	.globl _cpct_getScreenPtr
	.globl _cpct_drawSprite
	.globl _cpct_drawSolidBox
	.globl _cpct_px2byteM0
	.globl _cpct_memcpy
	.globl _g_movingBlocks
	.globl _g_colMaxBlock
	.globl _g_colMinBlock
	.globl _g_lastBlock
	.globl _g_blocks
	.globl _G_score
	.globl _G_platfColour
	.globl _G_scrollVel
	.globl _g_Character
	.globl _g_SCR_HEIGHT
	.globl _g_SCR_WIDTH
	.globl _G_maxY
	.globl _G_minY
	.globl _G_maxX
	.globl _G_minX
	.globl _G_floorFric
	.globl _G_airFric
	.globl _G_maxScrollVel
	.globl _G_jumpVel
	.globl _G_minVel
	.globl _G_maxXVel
	.globl _G_maxYVel
	.globl _G_gx
	.globl _G_gy
	.globl _initializeEntities
	.globl _getScore
	.globl _getCharacter
	.globl _performAction
	.globl _moveBlock
	.globl _scrollWorld
	.globl _updateCharacterPhysics
	.globl _getNearestBlockID
	.globl _applyCharacterBlockCollisions
	.globl _updateCharacter
	.globl _checkCollisionEntBlock
	.globl _isOverFloor
	.globl _setEntityLocation
	.globl _drawAnimEntity
	.globl _drawBlockEntity
	.globl _drawAll
	.globl _newSolidBlock
	.globl _destroyBlock
	.globl _randomCreateNewBlock
;--------------------------------------------------------
; special function registers
;--------------------------------------------------------
;--------------------------------------------------------
; ram data
;--------------------------------------------------------
	.area _DATA
_G_scrollVel::
	.ds 2
_G_platfColour::
	.ds 1
_G_score::
	.ds 2
_g_blocks::
	.ds 496
_g_lastBlock::
	.ds 1
_g_colMinBlock::
	.ds 1
_g_colMaxBlock::
	.ds 1
_g_movingBlocks::
	.ds 1
_checkCollisionEntBlock_c_1_213:
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
;src/entities/entities.c:119: void initializeEntities() {
;	---------------------------------
; Function initializeEntities
; ---------------------------------
_initializeEntities::
;src/entities/entities.c:120: G_platfColour = cpct_px2byteM0(8, 8);
	ld	hl, #0x0808
	push	hl
	call	_cpct_px2byteM0
	ld	iy, #_G_platfColour
	ld	0 (iy), l
;src/entities/entities.c:121: G_scrollVel = 3 * SCALE / FPS;  // Scroll down velocity, 3 px/sec
	ld	hl, #0x000f
	ld	(_G_scrollVel), hl
;src/entities/entities.c:122: g_movingBlocks = 0;
	ld	hl,#_g_movingBlocks + 0
	ld	(hl), #0x00
;src/entities/entities.c:125: g_lastBlock = 0;                                // Block ID 
	ld	hl,#_g_lastBlock + 0
	ld	(hl), #0x00
;src/entities/entities.c:126: newSolidBlock( 4, 120, 50, 5, G_platfColour);   // 0 /
	ld	a, (_G_platfColour)
	push	af
	inc	sp
	ld	hl, #0x0532
	push	hl
	ld	hl, #0x7804
	push	hl
	call	_newSolidBlock
	pop	af
	pop	af
	inc	sp
;src/entities/entities.c:127: newSolidBlock(14, 100, 10, 3, G_platfColour);   // 1 /
	ld	a, (_G_platfColour)
	push	af
	inc	sp
	ld	hl, #0x030a
	push	hl
	ld	hl, #0x640e
	push	hl
	call	_newSolidBlock
	pop	af
	pop	af
	inc	sp
;src/entities/entities.c:128: newSolidBlock(34, 100, 10, 3, G_platfColour);   // 2 /
	ld	a, (_G_platfColour)
	push	af
	inc	sp
	ld	hl, #0x030a
	push	hl
	ld	hl, #0x6422
	push	hl
	call	_newSolidBlock
	pop	af
	pop	af
	inc	sp
;src/entities/entities.c:129: newSolidBlock(26,  80,  6, 3, G_platfColour);   // 3 /
	ld	a, (_G_platfColour)
	push	af
	inc	sp
	ld	hl, #0x0306
	push	hl
	ld	hl, #0x501a
	push	hl
	call	_newSolidBlock
	pop	af
	pop	af
	inc	sp
;src/entities/entities.c:130: newSolidBlock( 8,  60, 10, 3, G_platfColour);   // 4 /
	ld	a, (_G_platfColour)
	push	af
	inc	sp
	ld	hl, #0x030a
	push	hl
	ld	hl, #0x3c08
	push	hl
	call	_newSolidBlock
	pop	af
	pop	af
	inc	sp
;src/entities/entities.c:131: newSolidBlock(36,  55, 10, 3, G_platfColour);   // 5 /
	ld	a, (_G_platfColour)
	push	af
	inc	sp
	ld	hl, #0x030a
	push	hl
	ld	hl, #0x3724
	push	hl
	call	_newSolidBlock
	pop	af
	pop	af
	inc	sp
;src/entities/entities.c:132: newSolidBlock(20,  30, 20, 3, G_platfColour);   // 6 /
	ld	a, (_G_platfColour)
	push	af
	inc	sp
	ld	hl, #0x0314
	push	hl
	ld	h, #0x1e
	push	hl
	call	_newSolidBlock
	pop	af
	pop	af
	inc	sp
;src/entities/entities.c:133: newSolidBlock( 9,  10, 10, 3, G_platfColour);   // 7 /
	ld	a, (_G_platfColour)
	push	af
	inc	sp
	ld	hl, #0x030a
	push	hl
	ld	hl, #0x0a09
	push	hl
	call	_newSolidBlock
	pop	af
	pop	af
	inc	sp
;src/entities/entities.c:134: newSolidBlock(44,   9,  4, 3, G_platfColour);   // 8 /
	ld	a, (_G_platfColour)
	push	af
	inc	sp
	ld	hl, #0x0304
	push	hl
	ld	hl, #0x092c
	push	hl
	call	_newSolidBlock
	pop	af
	pop	af
	inc	sp
;src/entities/entities.c:135: G_score = 9; // 9 points for the 9 starting blocks
	ld	hl, #0x0009
	ld	(_G_score), hl
;src/entities/entities.c:137: G_platfColour = 8;
	ld	hl,#_G_platfColour + 0
	ld	(hl), #0x08
;src/entities/entities.c:140: setEntityLocation(&g_Character.entity, 28, 120-20, 0, 0, 1);
	ld	hl, #0x0100
	push	hl
	ld	hl, #0x0064
	push	hl
	ld	a, #0x1c
	push	af
	inc	sp
	ld	hl, #_g_Character
	push	hl
	call	_setEntityLocation
	ld	hl, #7
	add	hl, sp
	ld	sp, hl
;src/entities/entities.c:143: g_colMinBlock = 0;
	ld	hl,#_g_colMinBlock + 0
	ld	(hl), #0x00
;src/entities/entities.c:144: g_colMaxBlock = 2;
	ld	hl,#_g_colMaxBlock + 0
	ld	(hl), #0x02
	ret
_G_gy:
	.dw #0x0032
_G_gx:
	.dw #0x0000
_G_maxYVel:
	.dw #0x0300
_G_maxXVel:
	.dw #0x0100
_G_minVel:
	.dw #0x0020
_G_jumpVel:
	.dw #0xfd00
_G_maxScrollVel:
	.dw #0x0080
_G_airFric:
	.db #0x02	; 2
_G_floorFric:
	.db #0x04	; 4
_G_minX:
	.db #0x04	; 4
_G_maxX:
	.db #0x36	; 54	'6'
_G_minY:
	.db #0x08	; 8
_G_maxY:
	.db #0xc0	; 192
_g_SCR_WIDTH:
	.db #0x50	; 80	'P'
_g_SCR_HEIGHT:
	.db #0xc8	; 200
_g_Character:
	.dw _g_walkRight
	.db #0x00	; 0
	.db #0x02	; 2
	.db #0x03	; 3
	.dw #0xc000
	.dw #0xc000
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.dw #0x0000
	.dw #0x0000
	.dw #0x0000
	.dw #0x0000
	.dw #0x0000
	.dw #0x0000
	.db #0x00	; 0
	.dw #0x0000
	.db #0x00	; 0
	.db #0x01	; 1
	.db #0x01	; 1
;src/entities/entities.c:150: u16 getScore() { return G_score; }
;	---------------------------------
; Function getScore
; ---------------------------------
_getScore::
	ld	hl, (_G_score)
	ret
;src/entities/entities.c:151: TCharacter* getCharacter() { return &g_Character; }
;	---------------------------------
; Function getCharacter
; ---------------------------------
_getCharacter::
	ld	hl, #_g_Character
	ret
;src/entities/entities.c:158: void performAction(TCharacter *c, TCharacterStatus move, TCharacterSide side) {
;	---------------------------------
; Function performAction
; ---------------------------------
_performAction::
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	hl, #-12
	add	hl, sp
	ld	sp, hl
;src/entities/entities.c:159: TEntity *e = &c->entity;   // Get entity associated to the character
	ld	l,4 (ix)
	ld	h,5 (ix)
	ld	e, l
	ld	d, h
;src/entities/entities.c:160: TPhysics *p = &e->phys;    // Get Physics information associated to the entity
	ld	a, e
	add	a, #0x0f
	ld	c, a
	ld	a, d
	adc	a, #0x00
	ld	b, a
;src/entities/entities.c:170: switch(c->status) {
	ld	a, l
	add	a, #0x1f
	ld	-2 (ix), a
	ld	a, h
	adc	a, #0x00
	ld	-1 (ix), a
;src/entities/entities.c:174: if ( side != c->side ) {
	ld	a, l
	add	a, #0x20
	ld	-11 (ix), a
	ld	a, h
	adc	a, #0x00
	ld	-10 (ix), a
;src/entities/entities.c:175: e->nAnim   = g_anim[es_walk][side]; // Next animation changes
	ld	hl, #0x001c
	add	hl,de
	ld	-9 (ix), l
	ld	-8 (ix), h
	ld	a, 7 (ix)
	add	a, a
	ld	-7 (ix), a
;src/entities/entities.c:178: e->nStatus = as_cycle;  // Make character cycle animation
	ld	hl, #0x001e
	add	hl,de
	ex	de,hl
;src/entities/entities.c:163: switch(move) {
	ld	a, 6 (ix)
	dec	a
	jr	Z,00101$
;src/entities/entities.c:209: p->floor   = 0;         // When jumping, we left the floor
	ld	hl, #0x000a
	add	hl,bc
	ld	-6 (ix), l
	ld	-5 (ix), h
;src/entities/entities.c:163: switch(move) {
	ld	a, 6 (ix)
	sub	a, #0x02
	jp	Z,00111$
	ld	a, 6 (ix)
	sub	a, #0x03
	jp	Z,00114$
	jp	00122$
;src/entities/entities.c:167: case es_walk:
00101$:
;src/entities/entities.c:170: switch(c->status) {
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	ld	a, (hl)
	cp	a, #0x01
	jr	Z,00102$
	sub	a, #0x02
	jr	Z,00105$
	jp	00126$
;src/entities/entities.c:172: case es_walk:
00102$:
;src/entities/entities.c:174: if ( side != c->side ) {
	ld	l,-11 (ix)
	ld	h,-10 (ix)
	ld	a, (hl)
	ld	-12 (ix), a
	ld	a, 7 (ix)
	sub	a, -12 (ix)
	jr	Z,00104$
;src/entities/entities.c:175: e->nAnim   = g_anim[es_walk][side]; // Next animation changes
	ld	a, #<((_g_anim + 0x0004))
	add	a, -7 (ix)
	ld	l, a
	ld	a, #>((_g_anim + 0x0004))
	adc	a, #0x00
	ld	h, a
	ld	a, (hl)
	ld	-4 (ix), a
	inc	hl
	ld	a, (hl)
	ld	-3 (ix), a
	ld	l,-9 (ix)
	ld	h,-8 (ix)
	ld	a, -4 (ix)
	ld	(hl), a
	inc	hl
	ld	a, -3 (ix)
	ld	(hl), a
;src/entities/entities.c:176: c->side    = side;
	ld	l,-11 (ix)
	ld	h,-10 (ix)
	ld	a, 7 (ix)
	ld	(hl), a
00104$:
;src/entities/entities.c:178: e->nStatus = as_cycle;  // Make character cycle animation
	ld	a, #0x02
	ld	(de), a
;src/entities/entities.c:184: case es_jump:
00105$:
;src/entities/entities.c:188: p->vx -= SCALE;
	ld	hl, #0x0004
	add	hl, bc
	push	hl
	ld	c, (hl)
	inc	hl
	ld	b, (hl)
	pop	hl
;src/entities/entities.c:187: if ( side == s_left )
	ld	a, 7 (ix)
	or	a, a
	jr	NZ,00107$
;src/entities/entities.c:188: p->vx -= SCALE;
	ld	a,b
	add	a,#0xff
	ld	b, a
	ld	(hl), c
	inc	hl
	ld	(hl), b
	jp	00126$
00107$:
;src/entities/entities.c:190: p->vx += SCALE;
	ld	a,b
	add	a,#0x01
	ld	b, a
	ld	(hl), c
	inc	hl
	ld	(hl), b
;src/entities/entities.c:191: break;
	jp	00126$
;src/entities/entities.c:202: case es_jump:
00111$:
;src/entities/entities.c:204: if (c->status == es_walk) {
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	ld	l, (hl)
	dec	l
	jp	NZ,00126$
;src/entities/entities.c:205: e->nAnim   = g_anim[es_jump][side]; // Next animation changes
	ld	a, #<((_g_anim + 0x0008))
	add	a, -7 (ix)
	ld	l, a
	ld	a, #>((_g_anim + 0x0008))
	adc	a, #0x00
	ld	h, a
	ld	a, (hl)
	ld	-4 (ix), a
	inc	hl
	ld	a, (hl)
	ld	-3 (ix), a
	ld	l,-9 (ix)
	ld	h,-8 (ix)
	ld	a, -4 (ix)
	ld	(hl), a
	inc	hl
	ld	a, -3 (ix)
	ld	(hl), a
;src/entities/entities.c:206: e->nStatus = as_play;   // Jump animation only plays once
	ld	a, #0x01
	ld	(de), a
;src/entities/entities.c:207: c->side    = side;      // New side
	ld	l,-11 (ix)
	ld	h,-10 (ix)
	ld	a, 7 (ix)
	ld	(hl), a
;src/entities/entities.c:208: c->status  = es_jump;   // New status
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	ld	(hl), #0x02
;src/entities/entities.c:209: p->floor   = 0;         // When jumping, we left the floor
	ld	l,-6 (ix)
	ld	h,-5 (ix)
	xor	a, a
	ld	(hl), a
	inc	hl
	ld	(hl), a
;src/entities/entities.c:210: p->vy     += G_jumpVel; // Add jump velocity to the character
	ld	hl, #0x0006
	add	hl,bc
	ld	c,l
	ld	b,h
	ld	e, (hl)
	inc	hl
	ld	d, (hl)
	ld	hl, (_G_jumpVel)
	add	hl,de
	ex	de,hl
	ld	a, e
	ld	(bc), a
	inc	bc
	ld	a, d
	ld	(bc), a
;src/entities/entities.c:212: break;
	jr	00126$
;src/entities/entities.c:217: case es_moveFloor:
00114$:
;src/entities/entities.c:219: if (p->floor && !p->floor->phys.vx && g_movingBlocks < g_MaxMovingBlocks) {
	ld	l,-6 (ix)
	ld	h,-5 (ix)
	ld	c, (hl)
	inc	hl
	ld	b, (hl)
	ld	a, b
	or	a,c
	jr	Z,00126$
	ld	hl, #0x0013
	add	hl,bc
	ld	c,l
	ld	b,h
	ld	e, (hl)
	inc	hl
	ld	a, (hl)
	or	a,e
	jr	NZ,00126$
	ld	iy, #_g_movingBlocks
	ld	a, 0 (iy)
	sub	a, #0x02
	jr	NC,00126$
;src/entities/entities.c:220: ++g_movingBlocks;
	inc	0 (iy)
;src/entities/entities.c:221: if (side == s_left)
	ld	a, 7 (ix)
	or	a, a
	jr	NZ,00116$
;src/entities/entities.c:222: p->floor->phys.vx = -SCALE / 2;
	ld	a, #0x80
	ld	(bc), a
	inc	bc
	ld	a, #0xff
	ld	(bc), a
	jr	00126$
00116$:
;src/entities/entities.c:224: p->floor->phys.vx = SCALE / 2;
	ld	a, #0x80
	ld	(bc), a
	inc	bc
	ld	a, #0x00
	ld	(bc), a
;src/entities/entities.c:226: break;
	jr	00126$
;src/entities/entities.c:229: default:
00122$:
;src/entities/entities.c:231: if ( c->status == es_walk )
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	ld	c, (hl)
	dec	c
	jr	NZ,00126$
;src/entities/entities.c:232: e->nStatus = as_pause;     // Pause animation on next timestep
	ld	a, #0x03
	ld	(de), a
;src/entities/entities.c:233: }
00126$:
	ld	sp, ix
	pop	ix
	ret
;src/entities/entities.c:239: void cropVelocity(i16 *v, i16 maxvel, i16 minvel) {
;	---------------------------------
; Function cropVelocity
; ---------------------------------
_cropVelocity::
	push	ix
	ld	ix,#0
	add	ix,sp
;src/entities/entities.c:242: if ( *v >= 0 ) {
	ld	l,4 (ix)
	ld	h,5 (ix)
	push	hl
	ld	e, (hl)
	inc	hl
	ld	d, (hl)
	pop	hl
	bit	7, d
	jr	NZ,00112$
;src/entities/entities.c:244: if      ( *v > maxvel ) *v = maxvel; // Crop to max. positive velocity
	ld	a, 6 (ix)
	sub	a, e
	ld	a, 7 (ix)
	sbc	a, d
	jp	PO, 00136$
	xor	a, #0x80
00136$:
	jp	P, 00104$
	ld	a, 6 (ix)
	ld	(hl), a
	inc	hl
	ld	a, 7 (ix)
	ld	(hl), a
	jr	00114$
00104$:
;src/entities/entities.c:245: else if ( *v < minvel ) *v = 0;      // Round to min positive velocity
	ld	a, e
	sub	a, 8 (ix)
	ld	a, d
	sbc	a, 9 (ix)
	jp	PO, 00137$
	xor	a, #0x80
00137$:
	jp	P, 00114$
	xor	a, a
	ld	(hl), a
	inc	hl
	ld	(hl), a
	jr	00114$
00112$:
;src/entities/entities.c:248: if      ( *v < -maxvel ) *v = -maxvel;  // Crop to max negative velocity
	xor	a, a
	sub	a, 6 (ix)
	ld	c, a
	ld	a, #0x00
	sbc	a, 7 (ix)
	ld	b, a
	ld	a, e
	sub	a, c
	ld	a, d
	sbc	a, b
	jp	PO, 00138$
	xor	a, #0x80
00138$:
	jp	P, 00109$
	ld	(hl), c
	inc	hl
	ld	(hl), b
	jr	00114$
00109$:
;src/entities/entities.c:249: else if ( *v > -minvel ) *v = 0;        // Round to mix negative velocity
	xor	a, a
	sub	a, 8 (ix)
	ld	c, a
	ld	a, #0x00
	sbc	a, 9 (ix)
	ld	b, a
	ld	a, c
	sub	a, e
	ld	a, b
	sbc	a, d
	jp	PO, 00139$
	xor	a, #0x80
00139$:
	jp	P, 00114$
	xor	a, a
	ld	(hl), a
	inc	hl
	ld	(hl), a
00114$:
	pop	ix
	ret
;src/entities/entities.c:261: u8 moveBlock(u8 b_idx) {
;	---------------------------------
; Function moveBlock
; ---------------------------------
_moveBlock::
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	hl, #-12
	add	hl, sp
	ld	sp, hl
;src/entities/entities.c:262: TEntity *e = &g_blocks[b_idx]; // Get next block entity
	ld	bc, #_g_blocks+0
	ld	e,4 (ix)
	ld	d,#0x00
	ld	l, e
	ld	h, d
	add	hl, hl
	add	hl, de
	add	hl, hl
	add	hl, de
	add	hl, hl
	add	hl, de
	add	hl, hl
	add	hl, de
	add	hl,bc
	ld	c, l
	ld	b, h
;src/entities/entities.c:266: e->phys.y += G_scrollVel;      // All blocks use this same velocity for Y axis
	ld	hl, #0x000f
	add	hl,bc
	ld	-2 (ix), l
	ld	-1 (ix), h
	ld	hl, #0x0011
	add	hl,bc
	ld	-4 (ix), l
	ld	-3 (ix), h
	ld	e, (hl)
	inc	hl
	ld	d, (hl)
	ld	hl, (_G_scrollVel)
	add	hl,de
	ex	de,hl
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	(hl), e
	inc	hl
	ld	(hl), d
;src/entities/entities.c:267: e->y       = e->ny;
	ld	iy, #0x000a
	add	iy, bc
	ld	hl, #0x000c
	add	hl,bc
	ld	-4 (ix), l
	ld	-3 (ix), h
	ld	a, (hl)
	ld	-12 (ix), a
	ld	0 (iy), a
;src/entities/entities.c:268: e->ny      = e->phys.y / SCALE;
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	(hl), d
;src/entities/entities.c:271: if (e->ny != e->y) {    
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	e, (hl)
;src/entities/entities.c:279: e->draw = 1;
	ld	hl, #0x001b
	add	hl,bc
	ld	-7 (ix), l
	ld	-6 (ix), h
;src/entities/entities.c:271: if (e->ny != e->y) {    
	ld	a, -12 (ix)
	sub	a, d
	jr	Z,00104$
;src/entities/entities.c:274: if (e->ny > G_maxY) {
	ld	a,(#_G_maxY + 0)
	sub	a, e
	jr	NC,00102$
;src/entities/entities.c:275: destroyBlock(b_idx);
	ld	a, 4 (ix)
	push	af
	inc	sp
	call	_destroyBlock
	inc	sp
;src/entities/entities.c:276: return 1;         // Return informing that the block has been destroyed!
	ld	l, #0x01
	jp	00116$
00102$:
;src/entities/entities.c:279: e->draw = 1;
	ld	l,-7 (ix)
	ld	h,-6 (ix)
	ld	(hl), #0x01
00104$:
;src/entities/entities.c:283: if (e->phys.vx) {
	ld	a, -2 (ix)
	add	a, #0x04
	ld	-11 (ix), a
	ld	a, -1 (ix)
	adc	a, #0x00
	ld	-10 (ix), a
	ld	l,-11 (ix)
	ld	h,-10 (ix)
	ld	e, (hl)
	inc	hl
	ld	d, (hl)
;src/entities/entities.c:284: e->x       = e->nx;
	ld	hl, #0x000b
	add	hl,bc
	ld	-9 (ix), l
	ld	-8 (ix), h
;src/entities/entities.c:283: if (e->phys.vx) {
	ld	a, d
	or	a,e
	jp	Z, 00113$
;src/entities/entities.c:284: e->x       = e->nx;
	ld	hl, #0x0009
	add	hl,bc
	ex	de,hl
	ld	l,-9 (ix)
	ld	h,-8 (ix)
	ld	a, (hl)
	ld	-12 (ix), a
	ld	(de),a
;src/entities/entities.c:285: e->phys.x += e->phys.vx;
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	ld	e, (hl)
	inc	hl
	ld	d, (hl)
	ld	l,-11 (ix)
	ld	h,-10 (ix)
	ld	a, (hl)
	inc	hl
	ld	h, (hl)
	ld	l, a
	add	hl,de
	ex	de,hl
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	ld	(hl), e
	inc	hl
	ld	(hl), d
;src/entities/entities.c:286: e->nx      = e->phys.x / SCALE;
	ld	l,-9 (ix)
	ld	h,-8 (ix)
	ld	(hl), d
;src/entities/entities.c:289: if (e->x != e->nx) {
	ld	l,-9 (ix)
	ld	h,-8 (ix)
	ld	e, (hl)
	ld	a, -12 (ix)
	sub	a, d
	jp	Z,00113$
;src/entities/entities.c:291: if (e->nx < G_minX) {
	ld	hl,#_G_minX + 0
	ld	d, (hl)
	ld	a, e
	sub	a, d
	jr	NC,00108$
;src/entities/entities.c:293: e->nx      = G_minX + 1; 
	inc	d
	ld	l,-9 (ix)
	ld	h,-8 (ix)
	ld	(hl), d
;src/entities/entities.c:294: e->phys.x  = e->nx * SCALE; 
	ld	e, #0x00
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	ld	(hl), e
	inc	hl
	ld	(hl), d
;src/entities/entities.c:295: e->phys.vx = -e->phys.vx;
	ld	l,-11 (ix)
	ld	h,-10 (ix)
	ld	e, (hl)
	inc	hl
	ld	d, (hl)
	xor	a, a
	sub	a, e
	ld	e, a
	ld	a, #0x00
	sbc	a, d
	ld	d, a
	ld	l,-11 (ix)
	ld	h,-10 (ix)
	ld	(hl), e
	inc	hl
	ld	(hl), d
	jr	00109$
00108$:
;src/entities/entities.c:296: } else if ( e->nx + e->graph.block.w >= G_maxX ) {
	ld	d, #0x00
	ld	a, (bc)
	ld	-12 (ix), a
	ld	l, a
	ld	h, #0x00
	add	hl, de
	ld	a,(#_G_maxX + 0)
	ld	-5 (ix), a
	ld	e, a
	ld	d, #0x00
	ld	a, l
	sub	a, e
	ld	a, h
	sbc	a, d
	jp	PO, 00148$
	xor	a, #0x80
00148$:
	jp	M, 00109$
;src/entities/entities.c:298: e->nx      = G_maxX - e->graph.block.w;
	ld	a, -5 (ix)
	sub	a, -12 (ix)
	ld	e, a
	ld	l,-9 (ix)
	ld	h,-8 (ix)
	ld	(hl), e
;src/entities/entities.c:299: e->phys.x  = e->nx * SCALE;  
	ld	d, #0x00
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	ld	(hl), d
	inc	hl
	ld	(hl), e
;src/entities/entities.c:300: e->phys.vx = -e->phys.vx;
	ld	l,-11 (ix)
	ld	h,-10 (ix)
	ld	e, (hl)
	inc	hl
	ld	d, (hl)
	xor	a, a
	sub	a, e
	ld	e, a
	ld	a, #0x00
	sbc	a, d
	ld	d, a
	ld	l,-11 (ix)
	ld	h,-10 (ix)
	ld	(hl), e
	inc	hl
	ld	(hl), d
00109$:
;src/entities/entities.c:302: e->draw = 1; // Set for redraw
	ld	l,-7 (ix)
	ld	h,-6 (ix)
	ld	(hl), #0x01
00113$:
;src/entities/entities.c:307: if (e->draw) {
	ld	l,-7 (ix)
	ld	h,-6 (ix)
	ld	a, (hl)
	or	a, a
	jr	Z,00115$
;src/entities/entities.c:308: e->pscreen  = e->npscreen;
	ld	hl, #0x0005
	add	hl,bc
	ex	de,hl
	ld	hl, #0x0007
	add	hl,bc
	ld	c, l
	ld	b, h
	ld	a, (bc)
	ld	-11 (ix), a
	inc	bc
	ld	a, (bc)
	ld	-10 (ix), a
	dec	bc
	ld	a, -11 (ix)
	ld	(de), a
	inc	de
	ld	a, -10 (ix)
	ld	(de), a
;src/entities/entities.c:309: e->npscreen = cpct_getScreenPtr(CPCT_VMEM_START, e->nx, e->ny);
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	a, (hl)
	ld	l,-9 (ix)
	ld	h,-8 (ix)
	ld	d, (hl)
	push	bc
	push	af
	inc	sp
	push	de
	inc	sp
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
	ex	de,hl
	pop	bc
	ld	a, e
	ld	(bc), a
	inc	bc
	ld	a, d
	ld	(bc), a
00115$:
;src/entities/entities.c:313: return 0;
	ld	l, #0x00
00116$:
	ld	sp, ix
	pop	ix
	ret
;src/entities/entities.c:320: void scrollWorld() {
;	---------------------------------
; Function scrollWorld
; ---------------------------------
_scrollWorld::
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	hl, #-7
	add	hl, sp
	ld	sp, hl
;src/entities/entities.c:321: TEntity *ce = &(getCharacter()->entity);
	call	_getCharacter
	ex	de,hl
;src/entities/entities.c:322: TPhysics *p = &ce->phys;
	ld	hl, #0x000f
	add	hl,de
	ld	-2 (ix), l
	ld	-1 (ix), h
	ld	a, -2 (ix)
	ld	-6 (ix), a
	ld	a, -1 (ix)
	ld	-5 (ix), a
;src/entities/entities.c:326: for(i=0; i < g_lastBlock; ++i) {
	ld	b, #0x00
00117$:
;src/entities/entities.c:333: p->floor = 0;  
	ld	a, -6 (ix)
	add	a, #0x0a
	ld	-4 (ix), a
	ld	a, -5 (ix)
	adc	a, #0x00
	ld	-3 (ix), a
;src/entities/entities.c:326: for(i=0; i < g_lastBlock; ++i) {
	ld	hl, #_g_lastBlock
	ld	a, b
	sub	a, (hl)
	jr	NC,00103$
;src/entities/entities.c:328: if ( moveBlock(i) ) {
	push	bc
	push	de
	push	bc
	inc	sp
	call	_moveBlock
	inc	sp
	pop	de
	pop	bc
	ld	a, l
	or	a, a
	jr	Z,00118$
;src/entities/entities.c:333: p->floor = 0;  
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	xor	a, a
	ld	(hl), a
	inc	hl
	ld	(hl), a
;src/entities/entities.c:334: i--;
	dec	b
00118$:
;src/entities/entities.c:326: for(i=0; i < g_lastBlock; ++i) {
	inc	b
	jr	00117$
00103$:
;src/entities/entities.c:340: if (p->floor && p->floor->draw) {
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	c, (hl)
	inc	hl
	ld	b, (hl)
	ld	a, b
	or	a,c
	jr	Z,00105$
	push	bc
	pop	iy
	ld	a, 27 (iy)
	or	a, a
	jr	Z,00105$
;src/entities/entities.c:343: u8 height = anim->frames[anim->frame_id]->height;
	ld	a, (de)
	ld	-4 (ix), a
	inc	de
	ld	a, (de)
	ld	-3 (ix), a
	dec	de
	ld	l, e
	ld	h, d
	inc	hl
	inc	hl
	ld	l, (hl)
	ld	h, #0x00
	add	hl, hl
	ld	a, l
	add	a, -4 (ix)
	ld	l, a
	ld	a, h
	adc	a, -3 (ix)
	ld	h, a
	ld	a, (hl)
	inc	hl
	ld	h, (hl)
	ld	l, a
	inc	hl
	inc	hl
	inc	hl
	ld	a, (hl)
	ld	-7 (ix), a
;src/entities/entities.c:346: ce->phys.y  = (p->floor->ny - height) * SCALE;
	ld	a, -2 (ix)
	add	a, #0x02
	ld	-4 (ix), a
	ld	a, -1 (ix)
	adc	a, #0x00
	ld	-3 (ix), a
	push	bc
	pop	iy
	ld	l, 12 (iy)
	ld	h, #0x00
	ld	c, -7 (ix)
	ld	b, #0x00
	cp	a, a
	sbc	hl, bc
	ld	b, l
	ld	c, #0x00
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	(hl), c
	inc	hl
	ld	(hl), b
;src/entities/entities.c:347: ce->phys.vy = G_minVel - 1;
	ld	a, -2 (ix)
	add	a, #0x06
	ld	l, a
	ld	a, -1 (ix)
	adc	a, #0x00
	ld	h, a
	ld	bc, (_G_minVel)
	dec	bc
	ld	(hl), c
	inc	hl
	ld	(hl), b
;src/entities/entities.c:348: ce->draw    = 1;
	ld	hl, #0x001b
	add	hl, de
	ld	(hl), #0x01
00105$:
;src/entities/entities.c:353: if ( g_blocks[0].draw && randomCreateNewBlock(G_minY-3, 3, ce->nx) ) {
	ld	a,(#(_g_blocks + 0x001b) + 0)
	or	a, a
	jr	Z,00119$
	ex	de,hl
	ld	de, #0x000b
	add	hl, de
	ld	c, (hl)
	ld	a,(#_G_minY + 0)
	add	a, #0xfd
	ld	d, a
	ld	b, c
	ld	c,#0x03
	push	bc
	push	de
	inc	sp
	call	_randomCreateNewBlock
	pop	af
	inc	sp
	ld	a, l
	or	a, a
	jr	Z,00119$
;src/entities/entities.c:356: if ( !(++G_score & 0x0F) ) {
	ld	iy, #_G_score
	inc	0 (iy)
	jr	NZ,00161$
	inc	1 (iy)
00161$:
	ld	a, 0 (iy)
	and	a, #0x0f
	jr	NZ,00119$
;src/entities/entities.c:358: if ( ++G_platfColour > 15) 
	ld	iy, #_G_platfColour
	inc	0 (iy)
	ld	a, #0x0f
	sub	a, 0 (iy)
	jr	NC,00108$
;src/entities/entities.c:359: G_platfColour = 1;
	ld	0 (iy), #0x01
00108$:
;src/entities/entities.c:362: if (G_scrollVel < G_maxScrollVel)
	ld	bc, (_G_maxScrollVel)
	ld	iy, #_G_scrollVel
	ld	a, 0 (iy)
	sub	a, c
	ld	a, 1 (iy)
	sbc	a, b
	jp	PO, 00164$
	xor	a, #0x80
00164$:
	jp	P, 00119$
;src/entities/entities.c:363: ++G_scrollVel;
	ld	iy, #_G_scrollVel
	inc	0 (iy)
	jr	NZ,00165$
	inc	1 (iy)
00165$:
00119$:
	ld	sp, ix
	pop	ix
	ret
;src/entities/entities.c:373: void updateCharacterPhysics(TCharacter *c) {
;	---------------------------------
; Function updateCharacterPhysics
; ---------------------------------
_updateCharacterPhysics::
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	hl, #-11
	add	hl, sp
	ld	sp, hl
;src/entities/entities.c:374: TEntity  *e = &c->entity;
	ld	e,4 (ix)
	ld	d,5 (ix)
	ld	c, e
	ld	b, d
;src/entities/entities.c:375: TPhysics *p = &e->phys;
	ld	hl, #0x000f
	add	hl,bc
	ex	(sp), hl
;src/entities/entities.c:379: if ( !isOverFloor(e) ) {
	push	bc
	push	de
	push	bc
	call	_isOverFloor
	pop	af
	ld	-1 (ix), l
	pop	de
	pop	bc
;src/entities/entities.c:381: if ( p->floor ) {
	ld	a, -11 (ix)
	add	a, #0x0a
	ld	l, a
	ld	a, -10 (ix)
	adc	a, #0x00
	ld	h, a
;src/entities/entities.c:383: c->status    = es_jump;
	ld	a, e
	add	a, #0x1f
	ld	e, a
	ld	a, d
	adc	a, #0x00
	ld	d, a
;src/entities/entities.c:388: p->vy += G_gy;
	ld	a, -11 (ix)
	add	a, #0x06
	ld	-3 (ix), a
	ld	a, -10 (ix)
	adc	a, #0x00
	ld	-2 (ix), a
;src/entities/entities.c:392: p->vx += 1;                   // p->vx must be != 0 to enable horizontal velocity processing
	ld	a, -11 (ix)
	add	a, #0x04
	ld	-5 (ix), a
	ld	a, -10 (ix)
	adc	a, #0x00
	ld	-4 (ix), a
;src/entities/entities.c:381: if ( p->floor ) {
	push	hl
	ld	a, (hl)
	ld	-9 (ix), a
	inc	hl
	ld	a, (hl)
	ld	-8 (ix), a
	pop	hl
;src/entities/entities.c:379: if ( !isOverFloor(e) ) {
	ld	a, -1 (ix)
	or	a, a
	jr	NZ,00104$
;src/entities/entities.c:381: if ( p->floor ) {
	ld	a, -8 (ix)
	or	a,-9 (ix)
	jr	Z,00102$
;src/entities/entities.c:382: p->floor     = 0; 
	xor	a, a
	ld	(hl), a
	inc	hl
	ld	(hl), a
;src/entities/entities.c:383: c->status    = es_jump;
	ld	a, #0x02
	ld	(de), a
;src/entities/entities.c:384: anim->status = as_pause;
	ld	hl, #0x0004
	add	hl, bc
	ld	(hl), #0x03
00102$:
;src/entities/entities.c:388: p->vy += G_gy;
	ld	l,-3 (ix)
	ld	h,-2 (ix)
	ld	a, (hl)
	ld	-7 (ix), a
	inc	hl
	ld	a, (hl)
	ld	-6 (ix), a
	ld	hl, (_G_gy)
	ld	a, -7 (ix)
	add	a, l
	ld	-7 (ix), a
	ld	a, -6 (ix)
	adc	a, h
	ld	-6 (ix), a
	ld	l,-3 (ix)
	ld	h,-2 (ix)
	ld	a, -7 (ix)
	ld	(hl), a
	inc	hl
	ld	a, -6 (ix)
	ld	(hl), a
	jr	00105$
00104$:
;src/entities/entities.c:391: p->x  += p->floor->phys.vx;   // Add floor inertia
	pop	hl
	push	hl
	ld	a, (hl)
	ld	-7 (ix), a
	inc	hl
	ld	a, (hl)
	ld	-6 (ix), a
	ld	l,-9 (ix)
	ld	h,-8 (ix)
	push	bc
	ld	bc, #0x0013
	add	hl, bc
	pop	bc
	ld	a, (hl)
	inc	hl
	ld	h, (hl)
	ld	l, a
	ld	a, -7 (ix)
	add	a, l
	ld	-7 (ix), a
	ld	a, -6 (ix)
	adc	a, h
	ld	-6 (ix), a
	pop	hl
	push	hl
	ld	a, -7 (ix)
	ld	(hl), a
	inc	hl
	ld	a, -6 (ix)
	ld	(hl), a
;src/entities/entities.c:392: p->vx += 1;                   // p->vx must be != 0 to enable horizontal velocity processing
	ld	l,-5 (ix)
	ld	h,-4 (ix)
	ld	a, (hl)
	inc	hl
	ld	h, (hl)
	ld	l, a
	inc	hl
	ld	-7 (ix), l
	ld	-6 (ix), h
	ld	l,-5 (ix)
	ld	h,-4 (ix)
	ld	a, -7 (ix)
	ld	(hl), a
	inc	hl
	ld	a, -6 (ix)
	ld	(hl), a
00105$:
;src/entities/entities.c:396: p->vx += G_gx;
	ld	l,-5 (ix)
	ld	h,-4 (ix)
	ld	a, (hl)
	ld	-7 (ix), a
	inc	hl
	ld	a, (hl)
	ld	-6 (ix), a
	ld	hl, (_G_gx)
	ld	a, -7 (ix)
	add	a, l
	ld	-7 (ix), a
	ld	a, -6 (ix)
	adc	a, h
	ld	-6 (ix), a
	ld	l,-5 (ix)
	ld	h,-4 (ix)
	ld	a, -7 (ix)
	ld	(hl), a
	inc	hl
	ld	a, -6 (ix)
	ld	(hl), a
;src/entities/entities.c:399: if ( p->vy ) {
	ld	l,-3 (ix)
	ld	h,-2 (ix)
	ld	a, (hl)
	inc	hl
	ld	h, (hl)
	or	a,h
	jr	Z,00107$
;src/entities/entities.c:401: cropVelocity(&p->vy, G_maxYVel, G_minVel);   
	ld	hl, (_G_minVel)
	ld	iy, (_G_maxYVel)
	push	bc
	push	de
	push	hl
	push	iy
	ld	l,-3 (ix)
	ld	h,-2 (ix)
	push	hl
	call	_cropVelocity
	ld	hl, #6
	add	hl, sp
	ld	sp, hl
	pop	de
	pop	bc
;src/entities/entities.c:403: p->y  += p->vy;         // Then add it to position
	pop	iy
	push	iy
	inc	iy
	inc	iy
	ld	a, 0 (iy)
	ld	-7 (ix), a
	ld	a, 1 (iy)
	ld	-6 (ix), a
	ld	l,-3 (ix)
	ld	h,-2 (ix)
	ld	a, (hl)
	inc	hl
	ld	h, (hl)
	ld	l, a
	ld	a, -7 (ix)
	add	a, l
	ld	l, a
	ld	a, -6 (ix)
	adc	a, h
	ld	h, a
	ld	0 (iy), l
	ld	1 (iy), h
;src/entities/entities.c:404: e->ny  = p->y / SCALE;  // Calculate new screen position
	ld	iy, #0x000c
	add	iy, bc
	ld	0 (iy), h
00107$:
;src/entities/entities.c:408: if ( p->vx ) {
	ld	l,-5 (ix)
	ld	h,-4 (ix)
	ld	a, (hl)
	inc	hl
	ld	h, (hl)
	or	a,h
	jp	Z, 00113$
;src/entities/entities.c:410: cropVelocity(&p->vx, G_maxXVel, G_minVel);
	ld	hl, (_G_minVel)
	ld	iy, (_G_maxXVel)
	push	bc
	push	de
	push	hl
	push	iy
	ld	l,-5 (ix)
	ld	h,-4 (ix)
	push	hl
	call	_cropVelocity
	ld	hl, #6
	add	hl, sp
	ld	sp, hl
	pop	de
	pop	bc
;src/entities/entities.c:412: p->x += p->vx;          // Then add it to position
	pop	hl
	push	hl
	ld	a, (hl)
	ld	-7 (ix), a
	inc	hl
	ld	a, (hl)
	ld	-6 (ix), a
	ld	l,-5 (ix)
	ld	h,-4 (ix)
	ld	a, (hl)
	inc	hl
	ld	h, (hl)
	ld	l, a
	ld	a, -7 (ix)
	add	a, l
	ld	-7 (ix), a
	ld	a, -6 (ix)
	adc	a, h
	ld	-6 (ix), a
	pop	hl
	push	hl
	ld	a, -7 (ix)
	ld	(hl), a
	inc	hl
	ld	a, -6 (ix)
	ld	(hl), a
;src/entities/entities.c:413: e->nx = p->x / SCALE;   // And calculate new screen position
	ld	hl, #0x000b
	add	hl, bc
	ld	c, -6 (ix)
	ld	(hl), c
;src/entities/entities.c:416: if ( c->status == es_walk )
	ld	a, (de)
;src/entities/entities.c:396: p->vx += G_gx;
	ld	l,-5 (ix)
	ld	h,-4 (ix)
	ld	c, (hl)
	inc	hl
	ld	b, (hl)
;src/entities/entities.c:416: if ( c->status == es_walk )
	dec	a
	jr	NZ,00109$
;src/entities/entities.c:417: p->vx /= G_floorFric;   // Friction on the floor
	ld	hl,#_G_floorFric + 0
	ld	e, (hl)
	ld	d, #0x00
	push	de
	push	bc
	call	__divsint
	pop	af
	pop	af
	ld	c, l
	ld	b, h
	ld	l,-5 (ix)
	ld	h,-4 (ix)
	ld	(hl), c
	inc	hl
	ld	(hl), b
	jr	00113$
00109$:
;src/entities/entities.c:419: p->vx /= G_airFric;     // Friction on air
	ld	hl,#_G_airFric + 0
	ld	e, (hl)
	ld	d, #0x00
	push	de
	push	bc
	call	__divsint
	pop	af
	pop	af
	ld	c, l
	ld	b, h
	ld	l,-5 (ix)
	ld	h,-4 (ix)
	ld	(hl), c
	inc	hl
	ld	(hl), b
00113$:
	ld	sp, ix
	pop	ix
	ret
;src/entities/entities.c:429: u8 getNearestBlockID(u8 bid, u8 y) {
;	---------------------------------
; Function getNearestBlockID
; ---------------------------------
_getNearestBlockID::
	push	ix
	ld	ix,#0
	add	ix,sp
;src/entities/entities.c:431: if (g_blocks[bid].ny <= y) {
	ld	c,4 (ix)
	ld	b,#0x00
	ld	l, c
	ld	h, b
	add	hl, hl
	add	hl, bc
	add	hl, hl
	add	hl, bc
	add	hl, hl
	add	hl, bc
	add	hl, hl
	add	hl, bc
	ld	de, #_g_blocks
	add	hl, de
	ld	de, #0x000c
	add	hl, de
	ld	b, (hl)
;src/entities/entities.c:434: while (bid > 0 && g_blocks[bid-1].ny <= y) --bid;
	ld	c, 4 (ix)
;src/entities/entities.c:431: if (g_blocks[bid].ny <= y) {
	ld	a, 5 (ix)
	sub	a, b
	jr	C,00119$
;src/entities/entities.c:434: while (bid > 0 && g_blocks[bid-1].ny <= y) --bid;
00102$:
	ld	a, c
	or	a, a
	jr	Z,00120$
	ld	e, c
	ld	d, #0x00
	dec	de
	ld	l, e
	ld	h, d
	add	hl, hl
	add	hl, de
	add	hl, hl
	add	hl, de
	add	hl, hl
	add	hl, de
	add	hl, hl
	add	hl, de
	ld	de, #_g_blocks
	add	hl, de
	ld	de, #0x000c
	add	hl, de
	ld	a,5 (ix)
	sub	a,(hl)
	jr	C,00120$
	dec	c
	jr	00102$
;src/entities/entities.c:438: while (bid < g_lastBlock - 1 && g_blocks[bid+1].ny > y) ++bid;
00119$:
00106$:
	ld	hl,#_g_lastBlock + 0
	ld	e, (hl)
	ld	d, #0x00
	dec	de
	ld	l, c
	ld	h, #0x00
	ld	a, l
	sub	a, e
	ld	a, h
	sbc	a, d
	jp	PO, 00143$
	xor	a, #0x80
00143$:
	jp	P, 00121$
	inc	hl
	ld	e, l
	ld	d, h
	add	hl, hl
	add	hl, de
	add	hl, hl
	add	hl, de
	add	hl, hl
	add	hl, de
	add	hl, hl
	add	hl, de
	ld	de, #_g_blocks
	add	hl, de
	ld	de, #0x000c
	add	hl, de
	ld	a,5 (ix)
	sub	a,(hl)
	jr	NC,00121$
	inc	c
	jr	00106$
00120$:
	ld	4 (ix), c
;src/entities/entities.c:442: return bid;
	jr	00111$
;src/entities/entities.c:438: while (bid < g_lastBlock - 1 && g_blocks[bid+1].ny > y) ++bid;
00121$:
	ld	4 (ix), c
00111$:
;src/entities/entities.c:442: return bid;
	ld	l, 4 (ix)
	pop	ix
	ret
;src/entities/entities.c:451: void applyCharacterBlockCollisions(TCharacter *c) {
;	---------------------------------
; Function applyCharacterBlockCollisions
; ---------------------------------
_applyCharacterBlockCollisions::
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	hl, #-34
	add	hl, sp
	ld	sp, hl
;src/entities/entities.c:452: TEntity  *e  = &c->entity;  // Entity associated to the character
	ld	a, 4 (ix)
	ld	-2 (ix), a
	ld	a, 5 (ix)
	ld	-1 (ix), a
	ld	c,-2 (ix)
	ld	b,-1 (ix)
	ld	-28 (ix), c
	ld	-27 (ix), b
;src/entities/entities.c:453: TPhysics *p  = &e->phys;    // Physics component of the character
	ld	a, -28 (ix)
	add	a, #0x0f
	ld	-30 (ix), a
	ld	a, -27 (ix)
	adc	a, #0x00
	ld	-29 (ix), a
;src/entities/entities.c:457: i = PXMARGIN + e->ny + e->graph.anim.frames[e->graph.anim.frame_id]->height; 
	ld	a, -28 (ix)
	add	a, #0x0c
	ld	-4 (ix), a
	ld	a, -27 (ix)
	adc	a, #0x00
	ld	-3 (ix), a
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	c, (hl)
	inc	c
	inc	c
	inc	c
	inc	c
	ld	l,-28 (ix)
	ld	h,-27 (ix)
	ld	e, (hl)
	inc	hl
	ld	d, (hl)
	ld	l,-28 (ix)
	ld	h,-27 (ix)
	inc	hl
	inc	hl
	ld	l, (hl)
	ld	h, #0x00
	add	hl, hl
	add	hl, de
	ld	a, (hl)
	inc	hl
	ld	h, (hl)
	ld	l, a
	inc	hl
	inc	hl
	inc	hl
	ld	b, (hl)
	ld	a, c
	add	a, b
	ld	b, a
;src/entities/entities.c:458: g_colMinBlock = getNearestBlockID(g_colMinBlock, i);
	push	bc
	inc	sp
	ld	a, (_g_colMinBlock)
	push	af
	inc	sp
	call	_getNearestBlockID
	pop	af
	ld	iy, #_g_colMinBlock
	ld	0 (iy), l
;src/entities/entities.c:461: i = e->ny - PXMARGIN;
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	a, (hl)
	add	a, #0xfc
	ld	b, a
;src/entities/entities.c:462: g_colMaxBlock = getNearestBlockID(g_colMaxBlock, i);
	push	bc
	inc	sp
	ld	a, (_g_colMaxBlock)
	push	af
	inc	sp
	call	_getNearestBlockID
	pop	af
	ld	iy, #_g_colMaxBlock
	ld	0 (iy), l
;src/entities/entities.c:466: for(i=g_colMinBlock; i <= g_colMaxBlock; ++i) {
	ld	a,(#_g_colMinBlock + 0)
	ld	-7 (ix), a
	ld	a, -2 (ix)
	ld	-9 (ix), a
	ld	a, -1 (ix)
	ld	-8 (ix), a
	ld	a, -28 (ix)
	ld	-12 (ix), a
	ld	a, -27 (ix)
	ld	-11 (ix), a
	ld	a, -28 (ix)
	ld	-18 (ix), a
	ld	a, -27 (ix)
	ld	-17 (ix), a
	ld	a, -28 (ix)
	ld	-22 (ix), a
	ld	a, -27 (ix)
	ld	-21 (ix), a
	ld	a, -28 (ix)
	ld	-16 (ix), a
	ld	a, -27 (ix)
	ld	-15 (ix), a
;src/entities/entities.c:478: e->nx += col->w;    // move col->w bytes right (colliding right)
	ld	a, -28 (ix)
	add	a, #0x0b
	ld	-14 (ix), a
	ld	a, -27 (ix)
	adc	a, #0x00
	ld	-13 (ix), a
;src/entities/entities.c:466: for(i=g_colMinBlock; i <= g_colMaxBlock; ++i) {
	ld	a, -14 (ix)
	ld	-6 (ix), a
	ld	a, -13 (ix)
	ld	-5 (ix), a
00118$:
	ld	a, (#_g_colMaxBlock)
	sub	a, -7 (ix)
	jp	C, 00120$
;src/entities/entities.c:468: TEntity    *ebl = &g_blocks[i];
	ld	c,-7 (ix)
	ld	b,#0x00
	ld	l, c
	ld	h, b
	add	hl, hl
	add	hl, bc
	add	hl, hl
	add	hl, bc
	add	hl, hl
	add	hl, bc
	add	hl, hl
	add	hl, bc
	ld	-20 (ix), l
	ld	-19 (ix), h
	ld	a, #<(_g_blocks)
	add	a, -20 (ix)
	ld	-20 (ix), a
	ld	a, #>(_g_blocks)
	adc	a, -19 (ix)
	ld	-19 (ix), a
	ld	a, -20 (ix)
	ld	-32 (ix), a
	ld	a, -19 (ix)
	ld	-31 (ix), a
;src/entities/entities.c:469: TCollision *col = checkCollisionEntBlock(e, ebl);
	pop	bc
	pop	hl
	push	hl
	push	bc
	push	hl
	ld	l,-28 (ix)
	ld	h,-27 (ix)
	push	hl
	call	_checkCollisionEntBlock
	pop	af
	pop	af
	ld	-33 (ix), h
;src/entities/entities.c:472: if (col->w && col->h) {
	ld	-34 (ix), l
	ld	a, l
	add	a, #0x02
	ld	-20 (ix), a
	ld	a, -33 (ix)
	adc	a, #0x00
	ld	-19 (ix), a
	ld	l,-20 (ix)
	ld	h,-19 (ix)
	ld	a, (hl)
	ld	-20 (ix), a
	or	a, a
	jp	Z, 00119$
	pop	hl
	push	hl
	inc	hl
	inc	hl
	inc	hl
	ld	a, (hl)
	ld	-24 (ix), a
	or	a, a
	jp	Z, 00119$
;src/entities/entities.c:476: if(e->x <= col->x - e->pw  || e->x >= ebl->x + ebl->pw ) {
	ld	l,-12 (ix)
	ld	h,-11 (ix)
	ld	de, #0x0009
	add	hl, de
	ld	c, (hl)
	pop	hl
	push	hl
	ld	a, (hl)
	ld	-10 (ix), a
	ld	e, a
	ld	d, #0x00
	ld	l,-18 (ix)
	ld	h,-17 (ix)
	push	bc
	ld	bc, #0x000d
	add	hl, bc
	pop	bc
	ld	l, (hl)
	ld	b, #0x00
	ld	a, e
	sub	a, l
	ld	e, a
	ld	a, d
	sbc	a, b
	ld	d, a
	ld	b, #0x00
	ld	a, e
	sub	a, c
	ld	a, d
	sbc	a, b
	jp	PO, 00155$
	xor	a, #0x80
00155$:
	jp	P, 00109$
	pop	de
	pop	hl
	push	hl
	push	de
	ld	de, #0x0009
	add	hl, de
	ld	e, (hl)
	ld	d, #0x00
	ld	l,-32 (ix)
	ld	h,-31 (ix)
	push	bc
	ld	bc, #0x000d
	add	hl, bc
	pop	bc
	ld	l, (hl)
	ld	h, #0x00
	add	hl, de
	ld	a, c
	sub	a, l
	ld	a, b
	sbc	a, h
	jp	PO, 00156$
	xor	a, #0x80
00156$:
	jp	M, 00110$
00109$:
;src/entities/entities.c:477: if (col->x > ebl->nx) 
	pop	bc
	pop	hl
	push	hl
	push	bc
	ld	de, #0x000b
	add	hl, de
	ld	c, (hl)
;src/entities/entities.c:478: e->nx += col->w;    // move col->w bytes right (colliding right)
	ld	l,-14 (ix)
	ld	h,-13 (ix)
	ld	a, (hl)
	ld	-23 (ix), a
;src/entities/entities.c:477: if (col->x > ebl->nx) 
	ld	a, c
	sub	a, -10 (ix)
	jr	NC,00102$
;src/entities/entities.c:478: e->nx += col->w;    // move col->w bytes right (colliding right)
	ld	a, -23 (ix)
	add	a, -20 (ix)
	ld	l,-14 (ix)
	ld	h,-13 (ix)
	ld	(hl), a
	jr	00103$
00102$:
;src/entities/entities.c:480: e->nx -= col->w;    // move col->w bytes left  (colliding left)
	ld	a, -23 (ix)
	sub	a, -20 (ix)
	ld	l,-14 (ix)
	ld	h,-13 (ix)
	ld	(hl), a
00103$:
;src/entities/entities.c:483: p->x  = e->nx * SCALE;
	ld	l,-6 (ix)
	ld	h,-5 (ix)
	ld	c, (hl)
	ld	b, #0x00
	ld	l,-30 (ix)
	ld	h,-29 (ix)
	ld	(hl), b
	inc	hl
	ld	(hl), c
;src/entities/entities.c:484: p->vx = 0;
	ld	a, -30 (ix)
	add	a, #0x04
	ld	l, a
	ld	a, -29 (ix)
	adc	a, #0x00
	ld	h, a
	xor	a, a
	ld	(hl), a
	inc	hl
	ld	(hl), a
	jp	00119$
00110$:
;src/entities/entities.c:487: } else if (e->y < col->y - e->ph / 2) { 
	ld	l,-22 (ix)
	ld	h,-21 (ix)
	ld	de, #0x000a
	add	hl, de
	ld	a, (hl)
	ld	-23 (ix), a
	pop	bc
	push	bc
	inc	bc
	ld	a, (bc)
	ld	-10 (ix), a
	ld	e, a
	ld	d, #0x00
	ld	l,-16 (ix)
	ld	h,-15 (ix)
	push	bc
	ld	bc, #0x000e
	add	hl, bc
	pop	bc
	ld	l, (hl)
	srl	l
	ld	h, #0x00
	ld	a, e
	sub	a, l
	ld	e, a
	ld	a, d
	sbc	a, h
	ld	d, a
	ld	l, -23 (ix)
	ld	h, #0x00
;src/entities/entities.c:496: p->y       = e->ny * SCALE;
	ld	a, -30 (ix)
	add	a, #0x02
	ld	-20 (ix), a
	ld	a, -29 (ix)
	adc	a, #0x00
	ld	-19 (ix), a
;src/entities/entities.c:497: p->vy      = 0;
	ld	a, -30 (ix)
	add	a, #0x06
	ld	-26 (ix), a
	ld	a, -29 (ix)
	adc	a, #0x00
	ld	-25 (ix), a
;src/entities/entities.c:487: } else if (e->y < col->y - e->ph / 2) { 
	ld	a, l
	sub	a, e
	ld	a, h
	sbc	a, d
	jp	PO, 00157$
	xor	a, #0x80
00157$:
	jp	P, 00107$
;src/entities/entities.c:488: p->floor   = ebl; // Make this entity the floor
	ld	a, -30 (ix)
	add	a, #0x0a
	ld	e, a
	ld	a, -29 (ix)
	adc	a, #0x00
	ld	d, a
	ld	a, -32 (ix)
	ld	(de), a
	inc	de
	ld	a, -31 (ix)
	ld	(de), a
;src/entities/entities.c:489: e->nAnim   = g_anim[es_walk][c->side]; // Next animation changes
	ld	iy, #0x001c
	ld	e,-28 (ix)
	ld	d,-27 (ix)
	add	iy, de
	ld	l,-9 (ix)
	ld	h,-8 (ix)
	ld	de, #0x0020
	add	hl, de
	ld	e, (hl)
	sla	e
	ld	hl, #(_g_anim + 0x0004)
	ld	d, #0x00
	add	hl, de
	ld	e, (hl)
	inc	hl
	ld	d, (hl)
	ld	0 (iy), e
	ld	1 (iy), d
;src/entities/entities.c:490: e->nStatus = as_pause;     // Make character cycle animation
	ld	a, -28 (ix)
	add	a, #0x1e
	ld	l, a
	ld	a, -27 (ix)
	adc	a, #0x00
	ld	h, a
	ld	(hl), #0x03
;src/entities/entities.c:491: c->status  = es_walk;
	ld	a, -2 (ix)
	add	a, #0x1f
	ld	l, a
	ld	a, -1 (ix)
	adc	a, #0x00
	ld	h, a
	ld	(hl), #0x01
;src/entities/entities.c:492: e->ny      = col->y - e->nAnim[0]->height; // Move col->h bytes upside and 
	ld	a, (bc)
	ld	c, a
	ex	de,hl
	ld	a, (hl)
	inc	hl
	ld	h, (hl)
	ld	l, a
	inc	hl
	inc	hl
	inc	hl
	ld	e, (hl)
	ld	a, c
	sub	a, e
	ld	c, a
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	(hl), c
;src/entities/entities.c:494: if (e->ny > G_maxY)  
	ld	a,(#_G_maxY + 0)
	sub	a, c
	jr	NC,00105$
;src/entities/entities.c:495: e->ny=G_minY;
	ld	hl,#_G_minY + 0
	ld	c, (hl)
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	(hl), c
00105$:
;src/entities/entities.c:496: p->y       = e->ny * SCALE;
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	b, (hl)
	ld	c, #0x00
	ld	l,-20 (ix)
	ld	h,-19 (ix)
	ld	(hl), c
	inc	hl
	ld	(hl), b
;src/entities/entities.c:497: p->vy      = 0;
	ld	l,-26 (ix)
	ld	h,-25 (ix)
	xor	a, a
	ld	(hl), a
	inc	hl
	ld	(hl), a
	jr	00119$
00107$:
;src/entities/entities.c:501: e->ny  = col->y + col->h;  // Move col->h bytes downside (ceil)
	ld	a, -10 (ix)
	add	a, -24 (ix)
	ld	c, a
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	(hl), c
;src/entities/entities.c:502: p->y   = e->ny * SCALE;
	ld	b, #0x00
	ld	l,-20 (ix)
	ld	h,-19 (ix)
	ld	(hl), b
	inc	hl
	ld	(hl), c
;src/entities/entities.c:503: p->vy  = 0;
	ld	l,-26 (ix)
	ld	h,-25 (ix)
	xor	a, a
	ld	(hl), a
	inc	hl
	ld	(hl), a
00119$:
;src/entities/entities.c:466: for(i=g_colMinBlock; i <= g_colMaxBlock; ++i) {
	inc	-7 (ix)
	jp	00118$
00120$:
	ld	sp, ix
	pop	ix
	ret
;src/entities/entities.c:514: u8 updateCharacter(TCharacter *c) {
;	---------------------------------
; Function updateCharacter
; ---------------------------------
_updateCharacter::
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	hl, #-24
	add	hl, sp
	ld	sp, hl
;src/entities/entities.c:515: TEntity  *e = &c->entity;
	ld	a, 4 (ix)
	ld	-2 (ix), a
	ld	a, 5 (ix)
	ld	-1 (ix), a
	ld	e,-2 (ix)
	ld	d,-1 (ix)
;src/entities/entities.c:516: TPhysics *p = &e->phys;
	ld	hl, #0x000f
	add	hl,de
	ld	-21 (ix), l
	ld	-20 (ix), h
;src/entities/entities.c:518: TAnimFrame   *af = anim->frames[anim->frame_id];
	ld	l, e
	ld	h, d
	ld	c, (hl)
	inc	hl
	ld	b, (hl)
	ld	hl, #0x0002
	add	hl,de
	ld	-13 (ix), l
	ld	-12 (ix), h
	ld	l, (hl)
	ld	h, #0x00
	add	hl, hl
	add	hl, bc
	ld	a, (hl)
	ld	-23 (ix), a
	inc	hl
	ld	a, (hl)
	ld	-22 (ix), a
;src/entities/entities.c:519: u8         alive = 1;
	ld	-24 (ix), #0x01
;src/entities/entities.c:522: e->x       = e->nx;
	ld	hl, #0x0009
	add	hl,de
	ld	c, l
	ld	b, h
	ld	hl, #0x000b
	add	hl,de
	ld	-11 (ix), l
	ld	-10 (ix), h
	ld	a, (hl)
	ld	(bc), a
;src/entities/entities.c:523: e->y       = e->ny;
	ld	hl, #0x000a
	add	hl,de
	ld	-17 (ix), l
	ld	-16 (ix), h
	ld	hl, #0x000c
	add	hl,de
	ld	-4 (ix), l
	ld	-3 (ix), h
	ld	a, (hl)
	ld	l,-17 (ix)
	ld	h,-16 (ix)
	ld	(hl), a
;src/entities/entities.c:524: e->pscreen = e->npscreen;
	ld	iy, #0x0005
	add	iy, de
	ld	hl, #0x0007
	add	hl,de
	ld	-15 (ix), l
	ld	-14 (ix), h
	ld	a, (hl)
	inc	hl
	ld	h, (hl)
	ld	0 (iy), a
	ld	1 (iy), h
;src/entities/entities.c:525: e->pw      = af->width;
	ld	iy, #0x000d
	add	iy, de
	ld	l,-23 (ix)
	ld	h,-22 (ix)
	inc	hl
	inc	hl
	ld	l, (hl)
	ld	0 (iy), l
;src/entities/entities.c:526: e->ph      = af->height;
	ld	iy, #0x000e
	add	iy, de
	ld	l,-23 (ix)
	ld	h,-22 (ix)
	inc	hl
	inc	hl
	inc	hl
	ld	l, (hl)
	ld	0 (iy), l
;src/entities/entities.c:529: if ( updateAnimation(&e->graph.anim, e->nAnim, e->nStatus) ) { 
	ld	hl, #0x001e
	add	hl,de
	ld	-9 (ix), l
	ld	-8 (ix), h
	ld	a, (hl)
	ld	-5 (ix), a
	ld	hl, #0x001c
	add	hl,de
	ld	-7 (ix), l
	ld	-6 (ix), h
	ld	a, (hl)
	ld	-19 (ix), a
	inc	hl
	ld	a, (hl)
	ld	-18 (ix), a
	push	bc
	push	de
	ld	a, -5 (ix)
	push	af
	inc	sp
	ld	l,-19 (ix)
	ld	h,-18 (ix)
	push	hl
	push	de
	call	_updateAnimation
	pop	af
	pop	af
	inc	sp
	pop	de
	pop	bc
;src/entities/entities.c:530: e->draw = 1;                        // Redraw 
	ld	a, e
	add	a, #0x1b
	ld	-19 (ix), a
	ld	a, d
	adc	a, #0x00
	ld	-18 (ix), a
;src/entities/entities.c:529: if ( updateAnimation(&e->graph.anim, e->nAnim, e->nStatus) ) { 
	ld	a, l
	or	a, a
	jr	Z,00102$
;src/entities/entities.c:530: e->draw = 1;                        // Redraw 
	ld	l,-19 (ix)
	ld	h,-18 (ix)
	ld	(hl), #0x01
;src/entities/entities.c:531: af = anim->frames[anim->frame_id];  // Get values of the new frame
	ex	de,hl
	ld	e, (hl)
	inc	hl
	ld	d, (hl)
	ld	l,-13 (ix)
	ld	h,-12 (ix)
	ld	l, (hl)
	ld	h, #0x00
	add	hl, hl
	add	hl, de
	ld	a, (hl)
	ld	-23 (ix), a
	inc	hl
	ld	a, (hl)
	ld	-22 (ix), a
;src/entities/entities.c:532: e->nAnim   = 0;                     // No next animation/animstatus
	ld	l,-7 (ix)
	ld	h,-6 (ix)
	xor	a, a
	ld	(hl), a
	inc	hl
	ld	(hl), a
;src/entities/entities.c:533: e->nStatus = as_null;
	ld	l,-9 (ix)
	ld	h,-8 (ix)
	ld	(hl), #0x00
00102$:
;src/entities/entities.c:537: updateCharacterPhysics(c);
	push	bc
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	push	hl
	call	_updateCharacterPhysics
	pop	af
	ld	l,4 (ix)
	ld	h,5 (ix)
	push	hl
	call	_applyCharacterBlockCollisions
	pop	af
	pop	bc
;src/entities/entities.c:541: if ( e->nx <= G_minX) { 
	ld	l,-11 (ix)
	ld	h,-10 (ix)
	ld	e, (hl)
	ld	hl,#_G_minX + 0
	ld	d, (hl)
	ld	a, d
	sub	a, e
	jr	C,00106$
;src/entities/entities.c:542: e->nx = G_minX + 1; 
	inc	d
	ld	l,-11 (ix)
	ld	h,-10 (ix)
	ld	(hl), d
;src/entities/entities.c:543: p->x = e->nx * SCALE; 
	ld	e, #0x00
	ld	l,-21 (ix)
	ld	h,-20 (ix)
	ld	(hl), e
	inc	hl
	ld	(hl), d
	jr	00107$
00106$:
;src/entities/entities.c:545: else if ( e->nx + af->width >= G_maxX ) {
	ld	d, #0x00
	ld	l,-23 (ix)
	ld	h,-22 (ix)
	inc	hl
	inc	hl
	ld	a, (hl)
	ld	-7 (ix), a
	ld	l, a
	ld	h, #0x00
	add	hl, de
	ld	a,(#_G_maxX + 0)
	ld	-5 (ix), a
	ld	e, a
	ld	d, #0x00
	ld	a, l
	sub	a, e
	ld	a, h
	sbc	a, d
	jp	PO, 00148$
	xor	a, #0x80
00148$:
	jp	M, 00107$
;src/entities/entities.c:546: e->nx = G_maxX - af->width;
	ld	a, -5 (ix)
	sub	a, -7 (ix)
	ld	e, a
	ld	l,-11 (ix)
	ld	h,-10 (ix)
	ld	(hl), e
;src/entities/entities.c:547: p->x  = e->nx * SCALE;  
	ld	d, e
	ld	e, #0x00
	ld	l,-21 (ix)
	ld	h,-20 (ix)
	ld	(hl), e
	inc	hl
	ld	(hl), d
00107$:
;src/entities/entities.c:549: if ( e->ny + af->height >= G_maxY ) { 
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	a, (hl)
	ld	-7 (ix), a
	ld	e, a
	ld	d, #0x00
	ld	l,-23 (ix)
	ld	h,-22 (ix)
	inc	hl
	inc	hl
	inc	hl
	ld	a, (hl)
	ld	-5 (ix), a
	ld	l, a
	ld	h, #0x00
	add	hl, de
	ld	a,(#_G_maxY + 0)
	ld	-9 (ix), a
	ld	e, a
	ld	d, #0x00
;src/entities/entities.c:551: p->y = e->ny * SCALE;
	ld	a, -21 (ix)
	add	a, #0x02
	ld	-13 (ix), a
	ld	a, -20 (ix)
	adc	a, #0x00
	ld	-12 (ix), a
;src/entities/entities.c:549: if ( e->ny + af->height >= G_maxY ) { 
	ld	a, l
	sub	a, e
	ld	a, h
	sbc	a, d
	jp	PO, 00149$
	xor	a, #0x80
00149$:
	jp	M, 00111$
;src/entities/entities.c:550: e->ny = G_maxY - af->height;
	ld	a, -9 (ix)
	sub	a, -5 (ix)
	ld	d, a
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	(hl), d
;src/entities/entities.c:551: p->y = e->ny * SCALE;
	ld	e, #0x00
	ld	l,-13 (ix)
	ld	h,-12 (ix)
	ld	(hl), e
	inc	hl
	ld	(hl), d
;src/entities/entities.c:552: alive = 0;
	ld	-24 (ix), #0x00
	jr	00112$
00111$:
;src/entities/entities.c:554: else if ( e->ny <= G_minY ) { 
	ld	hl,#_G_minY + 0
	ld	e, (hl)
	ld	a, e
	sub	a, -7 (ix)
	jr	C,00112$
;src/entities/entities.c:555: e->ny = G_minY + 1;
	inc	e
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	(hl), e
;src/entities/entities.c:556: p->y = e->ny * SCALE;
	ld	d, e
	ld	e, #0x00
	ld	l,-13 (ix)
	ld	h,-12 (ix)
	ld	(hl), e
	inc	hl
	ld	(hl), d
00112$:
;src/entities/entities.c:549: if ( e->ny + af->height >= G_maxY ) { 
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	e, (hl)
;src/entities/entities.c:561: if ( e->ny != e->y ) { 
	ld	l,-17 (ix)
	ld	h,-16 (ix)
	ld	d, (hl)
;src/entities/entities.c:541: if ( e->nx <= G_minX) { 
	ld	l,-11 (ix)
	ld	h,-10 (ix)
	ld	a, (hl)
	ld	-7 (ix), a
;src/entities/entities.c:561: if ( e->ny != e->y ) { 
	ld	a, e
	sub	a, d
	jr	Z,00116$
;src/entities/entities.c:562: e->npscreen  = cpct_getScreenPtr(CPCT_VMEM_START, e->nx, e->ny);
	ld	d, e
	ld	e, -7 (ix)
	push	de
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
	ld	c, l
	ld	b, h
	ld	l,-15 (ix)
	ld	h,-14 (ix)
	ld	(hl), c
	inc	hl
	ld	(hl), b
;src/entities/entities.c:563: e->draw = 1;
	ld	l,-19 (ix)
	ld	h,-18 (ix)
	ld	(hl), #0x01
	jr	00117$
00116$:
;src/entities/entities.c:564: } else if ( e->nx != e->x ) {
	ld	a, (bc)
	ld	c, a
	ld	a, -7 (ix)
	sub	a, c
	jr	Z,00117$
;src/entities/entities.c:565: e->npscreen = e->npscreen + e->nx - e->x;
	ld	l,-15 (ix)
	ld	h,-14 (ix)
	ld	e, (hl)
	inc	hl
	ld	d, (hl)
	ld	l,-7 (ix)
	ld	h,#0x00
	add	hl, de
	ld	b, #0x00
	ld	a, l
	sub	a, c
	ld	c, a
	ld	a, h
	sbc	a, b
	ld	b, a
	ld	l,-15 (ix)
	ld	h,-14 (ix)
	ld	(hl), c
	inc	hl
	ld	(hl), b
;src/entities/entities.c:566: e->draw = 1; 
	ld	l,-19 (ix)
	ld	h,-18 (ix)
	ld	(hl), #0x01
00117$:
;src/entities/entities.c:569: return alive;
	ld	l, -24 (ix)
	ld	sp, ix
	pop	ix
	ret
;src/entities/entities.c:575: TCollision* checkCollisionEntBlock(TEntity *a, TEntity *b) {
;	---------------------------------
; Function checkCollisionEntBlock
; ---------------------------------
_checkCollisionEntBlock::
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	hl, #-11
	add	hl, sp
	ld	sp, hl
;src/entities/entities.c:577: TAnimFrame *ani = a->graph.anim.frames [a->graph.anim.frame_id];
	ld	c,4 (ix)
	ld	b,5 (ix)
	ld	l, c
	ld	h, b
	ld	e, (hl)
	inc	hl
	ld	d, (hl)
	ld	l, c
	ld	h, b
	inc	hl
	inc	hl
	ld	l, (hl)
	ld	h, #0x00
	add	hl, hl
	add	hl, de
	ld	a, (hl)
	ld	-9 (ix), a
	inc	hl
	ld	a, (hl)
	ld	-8 (ix), a
;src/entities/entities.c:578: TBlock     *blk = &b->graph.block;
	ld	a, 6 (ix)
	ld	-3 (ix), a
	ld	a, 7 (ix)
	ld	-2 (ix), a
	ld	e,-3 (ix)
	ld	d,-2 (ix)
	ld	-7 (ix), e
	ld	-6 (ix), d
;src/entities/entities.c:581: c.h = 0;
	ld	hl, #(_checkCollisionEntBlock_c_1_213 + 0x0003)
	ld	(hl), #0x00
;src/entities/entities.c:585: u8 a_bbound = a->ny + ani->height - 1;// -- bottom boundary of a
	ld	l, c
	ld	h, b
	ld	de, #0x000c
	add	hl, de
	ld	e, (hl)
	ld	l,-9 (ix)
	ld	h,-8 (ix)
	inc	hl
	inc	hl
	inc	hl
	ld	d, (hl)
	ld	a, e
	add	a, d
	add	a, #0xff
	ld	-11 (ix), a
;src/entities/entities.c:586: u8 b_bbound = b->ny + blk->h - 1;     // -- bottom boundary of b
	ld	l,-3 (ix)
	ld	h,-2 (ix)
	push	bc
	ld	bc, #0x000c
	add	hl, bc
	pop	bc
	ld	d, (hl)
	ld	l,-7 (ix)
	ld	h,-6 (ix)
	inc	hl
	ld	l, (hl)
	ld	a, d
	add	a, l
	add	a, #0xff
;src/entities/entities.c:591: c.y = b->ny;                    // Yes, calculate vertical collision area
;src/entities/entities.c:592: if ( b_bbound < a_bbound )
	ld	-10 (ix), a
	sub	a, -11 (ix)
	ld	a, #0x00
	rla
	ld	-1 (ix), a
;src/entities/entities.c:589: if ( a->ny <= b->ny ) {               // Case 1: a is up, b is down
	ld	a, d
	sub	a, e
	jr	C,00112$
;src/entities/entities.c:590: if ( b->ny <= a_bbound ) {         // Check if b is inside the height of a
	ld	a, -11 (ix)
	sub	a, d
	jr	C,00113$
;src/entities/entities.c:591: c.y = b->ny;                    // Yes, calculate vertical collision area
	ld	hl, #(_checkCollisionEntBlock_c_1_213 + 0x0001)
	ld	(hl), d
;src/entities/entities.c:593: c.h = b_bbound - c.y + 1;
	ld	hl, #(_checkCollisionEntBlock_c_1_213 + 0x0001) + 0
	ld	e, (hl)
;src/entities/entities.c:592: if ( b_bbound < a_bbound )
	ld	a, -1 (ix)
	or	a, a
	jr	Z,00102$
;src/entities/entities.c:593: c.h = b_bbound - c.y + 1;
	ld	a, -10 (ix)
	sub	a, e
	inc	a
	ld	(#(_checkCollisionEntBlock_c_1_213 + 0x0003)),a
	jr	00113$
00102$:
;src/entities/entities.c:595: c.h = a_bbound - c.y + 1;
	ld	a, -11 (ix)
	sub	a, e
	inc	a
	ld	(#(_checkCollisionEntBlock_c_1_213 + 0x0003)),a
	jr	00113$
00112$:
;src/entities/entities.c:598: if ( a->ny <= b_bbound ) {         // Check if a is inside the height of b
	ld	a, -10 (ix)
	sub	a, e
	jr	C,00113$
;src/entities/entities.c:599: c.y = a->ny;                    // Yes, calculate vertical collision area
	ld	hl, #(_checkCollisionEntBlock_c_1_213 + 0x0001)
	ld	(hl), e
;src/entities/entities.c:593: c.h = b_bbound - c.y + 1;
	ld	hl, #(_checkCollisionEntBlock_c_1_213 + 0x0001) + 0
	ld	e, (hl)
;src/entities/entities.c:600: if ( b_bbound < a_bbound )
	ld	a, -1 (ix)
	or	a, a
	jr	Z,00107$
;src/entities/entities.c:601: c.h = b_bbound - c.y + 1;
	ld	a, -10 (ix)
	sub	a, e
	inc	a
	ld	(#(_checkCollisionEntBlock_c_1_213 + 0x0003)),a
	jr	00113$
00107$:
;src/entities/entities.c:603: c.h = a_bbound - c.y + 1;
	ld	a, -11 (ix)
	sub	a, e
	inc	a
	ld	(#(_checkCollisionEntBlock_c_1_213 + 0x0003)),a
00113$:
;src/entities/entities.c:610: if (c.h) {
	ld	a, (#(_checkCollisionEntBlock_c_1_213 + 0x0003) + 0)
	or	a, a
	jp	Z, 00128$
;src/entities/entities.c:611: u8 a_rbound = a->nx + ani->width - 1; // -- right boundary limit of a
	ld	hl, #0x000b
	add	hl,bc
	ld	-5 (ix), l
	ld	-4 (ix), h
	ld	c, (hl)
	pop	de
	pop	hl
	push	hl
	push	de
	inc	hl
	inc	hl
	ld	e, (hl)
	ld	a, c
	add	a, e
	add	a, #0xff
	ld	-10 (ix), a
;src/entities/entities.c:612: u8 b_rbound = b->nx + blk->w - 1;     // -- right boundary limit of b
	ld	a, -3 (ix)
	add	a, #0x0b
	ld	c, a
	ld	a, -2 (ix)
	adc	a, #0x00
	ld	b, a
	ld	a, (bc)
	ld	e, a
	ld	l,-7 (ix)
	ld	h,-6 (ix)
	ld	d, (hl)
	ld	a, e
	add	a, d
	add	a, #0xff
	ld	-11 (ix), a
;src/entities/entities.c:613: c.w = 0;                          // Erase previous values and set to 0
	ld	de, #_checkCollisionEntBlock_c_1_213 + 2
	xor	a, a
	ld	(de), a
;src/entities/entities.c:615: if ( a->nx <= b->nx ) {           // Case 1: a is left, b is right
	ld	l,-5 (ix)
	ld	h,-4 (ix)
	ld	a, (hl)
	ld	-5 (ix), a
	ld	a, (bc)
	ld	b, a
;src/entities/entities.c:618: if ( b_rbound < a_rbound )
	ld	a, -11 (ix)
	sub	a, -10 (ix)
	ld	a, #0x00
	rla
	ld	c, a
;src/entities/entities.c:615: if ( a->nx <= b->nx ) {           // Case 1: a is left, b is right
	ld	a, b
	sub	a, -5 (ix)
	jr	C,00125$
;src/entities/entities.c:616: if ( b->nx <= a_rbound ) {     // Check if b is inside the width of a
	ld	a, -10 (ix)
	sub	a, b
	jr	C,00128$
;src/entities/entities.c:617: c.x = b->nx;                // Yes, calculate horizontal collision area
	ld	hl, #_checkCollisionEntBlock_c_1_213
	ld	(hl), b
;src/entities/entities.c:619: c.w = b_rbound - c.x + 1;
	ld	hl, #_checkCollisionEntBlock_c_1_213 + 0
	ld	l, (hl)
;src/entities/entities.c:618: if ( b_rbound < a_rbound )
	ld	a, c
	or	a, a
	jr	Z,00115$
;src/entities/entities.c:619: c.w = b_rbound - c.x + 1;
	ld	a, -11 (ix)
	sub	a, l
	inc	a
	ld	(de), a
	jr	00128$
00115$:
;src/entities/entities.c:621: c.w = a_rbound - c.x + 1;
	ld	a, -10 (ix)
	sub	a, l
	inc	a
	ld	(de), a
	jr	00128$
00125$:
;src/entities/entities.c:624: if ( a->nx <= b_rbound ) {     // Check if a is inside the width of b
	ld	a, -11 (ix)
	sub	a, -5 (ix)
	jr	C,00128$
;src/entities/entities.c:625: c.x = a->nx;                // Yes, calculate horizontal collision area
	ld	hl, #_checkCollisionEntBlock_c_1_213
	ld	a, -5 (ix)
	ld	(hl), a
;src/entities/entities.c:619: c.w = b_rbound - c.x + 1;
	ld	hl, #_checkCollisionEntBlock_c_1_213 + 0
	ld	l, (hl)
;src/entities/entities.c:626: if ( b_rbound < a_rbound )
	ld	a, c
	or	a, a
	jr	Z,00120$
;src/entities/entities.c:627: c.w = b_rbound - c.x + 1;
	ld	a, -11 (ix)
	sub	a, l
	inc	a
	ld	(de), a
	jr	00128$
00120$:
;src/entities/entities.c:629: c.w = a_rbound - c.x + 1;
	ld	a, -10 (ix)
	sub	a, l
	inc	a
	ld	(de), a
00128$:
;src/entities/entities.c:634: return &c;
	ld	hl, #_checkCollisionEntBlock_c_1_213
	ld	sp, ix
	pop	ix
	ret
;src/entities/entities.c:640: u8 isOverFloor(TEntity *e) {
;	---------------------------------
; Function isOverFloor
; ---------------------------------
_isOverFloor::
	push	ix
	ld	ix,#0
	add	ix,sp
	push	af
	push	af
	dec	sp
;src/entities/entities.c:641: u8 over = 0;                  // Value to sign if we are over a floor or not
	ld	-1 (ix), #0x00
;src/entities/entities.c:642: TEntity *f = e->phys.floor;   // Get the pointer to the floor assigned to this entity
	ld	c,4 (ix)
	ld	b,5 (ix)
	push	bc
	pop	iy
	ld	a, 25 (iy)
	ld	-3 (ix), a
	ld	a, 26 (iy)
;src/entities/entities.c:645: if ( f ) {
	ld	-2 (ix), a
	or	a,-3 (ix)
	jr	Z,00105$
;src/entities/entities.c:646: TAnimFrame *e_a = e->graph.anim.frames[e->graph.anim.frame_id];
	ld	l, c
	ld	h, b
	ld	e, (hl)
	inc	hl
	ld	d, (hl)
	ld	l, c
	ld	h, b
	inc	hl
	inc	hl
	ld	l, (hl)
	ld	h, #0x00
	add	hl, hl
	add	hl, de
	ld	a, (hl)
	ld	-5 (ix), a
	inc	hl
	ld	a, (hl)
	ld	-4 (ix), a
;src/entities/entities.c:648: if ( e->x <= (f->x + f->graph.block.w) &&    // X lower  than right border of the block
	ld	l, c
	ld	h, b
	ld	de, #0x0009
	add	hl, de
	ld	e, (hl)
	pop	bc
	pop	hl
	push	hl
	push	bc
	ld	bc, #0x0009
	add	hl, bc
	ld	c, (hl)
	ld	b, #0x00
	ld	l,-3 (ix)
	ld	h,-2 (ix)
	ld	l, (hl)
	ld	h, #0x00
	add	hl, bc
	ld	d, #0x00
	ld	a, l
	sub	a, e
	ld	a, h
	sbc	a, d
	jp	PO, 00120$
	xor	a, #0x80
00120$:
	jp	M, 00105$
;src/entities/entities.c:649: (e->x + e_a->width) >= f->x           )  // X + width higher than left border of the block
	pop	hl
	push	hl
	inc	hl
	inc	hl
	ld	l, (hl)
	ld	h, #0x00
	add	hl, de
	ld	a, l
	sub	a, c
	ld	a, h
	sbc	a, b
	jp	PO, 00121$
	xor	a, #0x80
00121$:
	jp	M, 00105$
;src/entities/entities.c:650: over = 1;
	ld	-1 (ix), #0x01
00105$:
;src/entities/entities.c:657: return over;
	ld	l, -1 (ix)
	ld	sp, ix
	pop	ix
	ret
;src/entities/entities.c:664: void setEntityLocation(TEntity *e, u8 x, u8 y, u8 vx, u8 vy, u8 eraseprev) {
;	---------------------------------
; Function setEntityLocation
; ---------------------------------
_setEntityLocation::
	push	ix
	ld	ix,#0
	add	ix,sp
	push	af
;src/entities/entities.c:666: e->npscreen   = cpct_getScreenPtr(CPCT_VMEM_START, x, y);
	ld	c,4 (ix)
	ld	b,5 (ix)
	ld	hl, #0x0007
	add	hl,bc
	ex	(sp), hl
	push	bc
	ld	h, 7 (ix)
	ld	l, 6 (ix)
	push	hl
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
	ex	de,hl
	pop	bc
	pop	hl
	push	hl
	ld	(hl), e
	inc	hl
	ld	(hl), d
;src/entities/entities.c:667: e->nx = x;
	ld	hl, #0x000b
	add	hl, bc
	ld	a, 6 (ix)
	ld	(hl), a
;src/entities/entities.c:668: e->ny = y;
	ld	hl, #0x000c
	add	hl, bc
	ld	a, 7 (ix)
	ld	(hl), a
;src/entities/entities.c:671: e->phys.x    = x  * SCALE;
	ld	hl, #0x000f
	add	hl, bc
	ld	d, 6 (ix)
	ld	(hl), #0x00
	inc	hl
	ld	(hl), d
;src/entities/entities.c:672: e->phys.y    = y  * SCALE;
	ld	hl, #0x0011
	add	hl, bc
	ld	d, 7 (ix)
	ld	(hl), #0x00
	inc	hl
	ld	(hl), d
;src/entities/entities.c:673: e->phys.vx   = vx * SCALE;
	ld	hl, #0x0013
	add	hl, bc
	ld	d, 8 (ix)
	ld	(hl), #0x00
	inc	hl
	ld	(hl), d
;src/entities/entities.c:674: e->phys.vy   = vy * SCALE;
	ld	hl, #0x0015
	add	hl, bc
	ld	d, 9 (ix)
	ld	(hl), #0x00
	inc	hl
	ld	(hl), d
;src/entities/entities.c:677: if (eraseprev) {
	ld	a, 10 (ix)
	or	a, a
	jr	Z,00103$
;src/entities/entities.c:678: e->pscreen  = e->npscreen;
	ld	iy, #0x0005
	add	iy, bc
	pop	hl
	push	hl
	ld	e, (hl)
	inc	hl
	ld	d, (hl)
	ld	0 (iy), e
	ld	1 (iy), d
;src/entities/entities.c:679: e->x = x;
	ld	hl, #0x0009
	add	hl, bc
	ld	a, 6 (ix)
	ld	(hl), a
;src/entities/entities.c:680: e->y = y;
	ld	hl, #0x000a
	add	hl, bc
	ld	a, 7 (ix)
	ld	(hl), a
00103$:
	ld	sp, ix
	pop	ix
	ret
;src/entities/entities.c:687: void drawAnimEntity (TEntity* e) {
;	---------------------------------
; Function drawAnimEntity
; ---------------------------------
_drawAnimEntity::
	push	ix
	ld	ix,#0
	add	ix,sp
	push	af
	push	af
;src/entities/entities.c:689: if ( e->draw ) {
	ld	c,4 (ix)
	ld	b,5 (ix)
	ld	hl, #0x001b
	add	hl,bc
	ex	(sp), hl
	pop	hl
	push	hl
	ld	a, (hl)
	or	a, a
	jr	Z,00103$
;src/entities/entities.c:691: TAnimation* anim  = &e->graph.anim;
	ld	l, c
	ld	h, b
;src/entities/entities.c:692: TAnimFrame* frame = anim->frames[anim->frame_id];
	push	hl
	ld	e, (hl)
	inc	hl
	ld	d, (hl)
	pop	hl
	inc	hl
	inc	hl
	ld	l, (hl)
	ld	h, #0x00
	add	hl, hl
	add	hl, de
	ld	e, (hl)
	inc	hl
	ld	d, (hl)
;src/entities/entities.c:695: cpct_drawSolidBox(e->pscreen, 0x00, e->pw, e->ph);
	ld	l, c
	ld	h, b
	push	bc
	ld	bc, #0x000e
	add	hl, bc
	pop	bc
	ld	a, (hl)
	ld	-1 (ix), a
	ld	l, c
	ld	h, b
	push	bc
	ld	bc, #0x000d
	add	hl, bc
	pop	bc
	ld	a, (hl)
	ld	-2 (ix), a
	ld	l, c
	ld	h, b
	inc	hl
	inc	hl
	inc	hl
	inc	hl
	inc	hl
	ld	a, (hl)
	inc	hl
	ld	h, (hl)
	ld	l, a
	push	hl
	pop	iy
	push	bc
	push	de
	ld	h, -1 (ix)
	ld	l, -2 (ix)
	push	hl
	ld	hl, #0x0000
	push	hl
	push	iy
	call	_cpct_drawSolidBox
	pop	de
	pop	bc
;src/entities/entities.c:698: cpct_drawSprite(frame->sprite, e->npscreen, frame->width, frame->height);
	ld	l, e
	ld	h, d
	inc	hl
	inc	hl
	inc	hl
	ld	a, (hl)
	ld	-2 (ix), a
	ld	l, e
	ld	h, d
	inc	hl
	inc	hl
	ld	a, (hl)
	ld	-1 (ix), a
	ld	l, c
	ld	h, b
	ld	bc, #0x0007
	add	hl, bc
	ld	c, (hl)
	inc	hl
	ld	b, (hl)
	ex	de,hl
	ld	e, (hl)
	inc	hl
	ld	d, (hl)
	ld	h, -2 (ix)
	ld	l, -1 (ix)
	push	hl
	push	bc
	push	de
	call	_cpct_drawSprite
;src/entities/entities.c:700: e->draw = 0;
	pop	hl
	push	hl
	ld	(hl), #0x00
00103$:
	ld	sp, ix
	pop	ix
	ret
;src/entities/entities.c:707: void drawBlockEntity (TEntity* e){
;	---------------------------------
; Function drawBlockEntity
; ---------------------------------
_drawBlockEntity::
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	hl, #-14
	add	hl, sp
	ld	sp, hl
;src/entities/entities.c:709: if ( e->draw ) {
	ld	a, 4 (ix)
	ld	-2 (ix), a
	ld	a, 5 (ix)
	ld	-1 (ix), a
	ld	a, -2 (ix)
	add	a, #0x1b
	ld	-4 (ix), a
	ld	a, -1 (ix)
	adc	a, #0x00
	ld	-3 (ix), a
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	a, (hl)
	ld	-9 (ix), a
	or	a, a
	jp	Z, 00113$
;src/entities/entities.c:715: TBlock* block  = &e->graph.block;
	ld	a, -2 (ix)
	ld	-14 (ix), a
	ld	a, -1 (ix)
	ld	-13 (ix), a
;src/entities/entities.c:718: sp = e->npscreen;
	ld	a, -2 (ix)
	ld	-11 (ix), a
	ld	a, -1 (ix)
	ld	-10 (ix), a
	ld	l,-11 (ix)
	ld	h,-10 (ix)
	ld	de, #0x0007
	add	hl, de
	ld	a, (hl)
	ld	-11 (ix), a
	inc	hl
	ld	a, (hl)
	ld	-10 (ix), a
;src/entities/entities.c:719: if (e->ny <= G_minY) {
	ld	a, -2 (ix)
	ld	-6 (ix), a
	ld	a, -1 (ix)
	ld	-5 (ix), a
	ld	l,-6 (ix)
	ld	h,-5 (ix)
	ld	de, #0x000c
	add	hl, de
	ld	a, (hl)
	ld	-6 (ix), a
	ld	a,(#_G_minY + 0)
	ld	-9 (ix), a
;src/entities/entities.c:720: drawh = block->h + e->ny - G_minY;
	ld	a, -14 (ix)
	ld	-8 (ix), a
	ld	a, -13 (ix)
	ld	-7 (ix), a
	ld	l,-8 (ix)
	ld	h,-7 (ix)
	inc	hl
	ld	a, (hl)
	ld	-8 (ix), a
;src/entities/entities.c:719: if (e->ny <= G_minY) {
	ld	a, -9 (ix)
	sub	a, -6 (ix)
	jr	C,00107$
;src/entities/entities.c:720: drawh = block->h + e->ny - G_minY;
	ld	a, -8 (ix)
	add	a, -6 (ix)
	ld	c,a
	sub	a, -9 (ix)
	ld	-12 (ix), a
;src/entities/entities.c:721: sp = cpct_getScreenPtr(CPCT_VMEM_START, e->nx, G_minY);
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	ld	de, #0x000b
	add	hl, de
	ld	b, (hl)
	ld	a, -9 (ix)
	push	af
	inc	sp
	push	bc
	inc	sp
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
	ld	-11 (ix), l
	ld	-10 (ix), h
	jr	00108$
00107$:
;src/entities/entities.c:723: if (e->ny + block->h > G_maxY) {
	ld	c, -6 (ix)
	ld	b, #0x00
	ld	l, -8 (ix)
	ld	h, #0x00
	add	hl, bc
	ld	a,(#_G_maxY + 0)
	ld	-9 (ix), a
	ld	b, #0x00
	sub	a, l
	ld	a, b
	sbc	a, h
	jp	PO, 00135$
	xor	a, #0x80
00135$:
	jp	P, 00102$
;src/entities/entities.c:724: drawh  = G_maxY - e->ny;
	ld	a, -9 (ix)
	sub	a, -6 (ix)
	ld	-12 (ix), a
;src/entities/entities.c:725: eraseh = G_maxY - e->y;
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	ld	de, #0x000a
	add	hl, de
	ld	a,-9 (ix)
	sub	a,(hl)
	ld	c, a
	jr	00103$
00102$:
;src/entities/entities.c:727: drawh  = block->h;
	ld	a, -8 (ix)
	ld	-8 (ix), a
;src/entities/entities.c:728: eraseh = drawh;
	ld	-12 (ix), a
	ld	c, a
00103$:
;src/entities/entities.c:732: if (eraseh)
	ld	a, c
	or	a, a
	jr	Z,00108$
;src/entities/entities.c:733: cpct_drawSolidBox(e->pscreen,  0x00, block->w, eraseh);
	pop	hl
	push	hl
	ld	b, (hl)
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	ld	de, #0x0005
	add	hl, de
	ld	e, (hl)
	inc	hl
	ld	d, (hl)
	ld	a, c
	push	af
	inc	sp
	push	bc
	inc	sp
	ld	hl, #0x0000
	push	hl
	push	de
	call	_cpct_drawSolidBox
00108$:
;src/entities/entities.c:737: if (drawh)
	ld	a, -12 (ix)
	or	a, a
	jr	Z,00110$
;src/entities/entities.c:738: cpct_drawSolidBox(sp, block->colour, block->w, drawh);
	pop	hl
	push	hl
	ld	d, (hl)
	pop	hl
	push	hl
	inc	hl
	inc	hl
	ld	c, (hl)
	ld	b, #0x00
	push	hl
	ld	l, -11 (ix)
	ld	h, -10 (ix)
	push	hl
	pop	iy
	pop	hl
	ld	a, -12 (ix)
	push	af
	inc	sp
	push	de
	inc	sp
	push	bc
	push	iy
	call	_cpct_drawSolidBox
00110$:
;src/entities/entities.c:740: e->draw = 0;
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	(hl), #0x00
00113$:
	ld	sp, ix
	pop	ix
	ret
;src/entities/entities.c:747: void drawAll() {
;	---------------------------------
; Function drawAll
; ---------------------------------
_drawAll::
;src/entities/entities.c:748: u8  i = g_lastBlock;
	ld	hl,#_g_lastBlock + 0
	ld	c, (hl)
;src/entities/entities.c:751: while(i--) 
00101$:
	ld	b, c
	dec	c
	ld	a, b
	or	a, a
	jr	Z,00103$
;src/entities/entities.c:752: drawBlockEntity(&g_blocks[i]);
	ld	b,#0x00
	ld	l, c
	ld	h, b
	add	hl, hl
	add	hl, bc
	add	hl, hl
	add	hl, bc
	add	hl, hl
	add	hl, bc
	add	hl, hl
	add	hl, bc
	ld	de, #_g_blocks
	add	hl, de
	push	bc
	push	hl
	call	_drawBlockEntity
	pop	af
	pop	bc
	jr	00101$
00103$:
;src/entities/entities.c:755: drawAnimEntity(&g_Character.entity);
	ld	hl, #_g_Character
	push	hl
	call	_drawAnimEntity
	pop	af
	ret
;src/entities/entities.c:761: TEntity* newSolidBlock(u8 x, u8 y, u8 width, u8 height, u8 colour) {
;	---------------------------------
; Function newSolidBlock
; ---------------------------------
_newSolidBlock::
	push	ix
	ld	ix,#0
	add	ix,sp
	push	af
	push	af
;src/entities/entities.c:762: TEntity *newEnt = 0;
	ld	bc, #0x0000
;src/entities/entities.c:765: if (g_lastBlock < g_MaxBlocks) {
	ld	a,(#_g_lastBlock + 0)
	sub	a, #0x10
	jp	NC, 00104$
;src/entities/entities.c:767: newEnt = &g_blocks[g_lastBlock];
	ld	bc, (_g_lastBlock)
	ld	b, #0x00
	ld	l, c
	ld	h, b
	add	hl, hl
	add	hl, bc
	add	hl, hl
	add	hl, bc
	add	hl, hl
	add	hl, bc
	add	hl, hl
	add	hl, bc
	ld	de, #_g_blocks
	add	hl, de
	ld	c, l
	ld	b, h
;src/entities/entities.c:768: newEnt->graph.block.w      = width;
	ld	a, 6 (ix)
	ld	(bc), a
;src/entities/entities.c:769: newEnt->graph.block.h      = height;
	ld	e, c
	ld	d, b
	inc	de
	ld	a, 7 (ix)
	ld	(de), a
;src/entities/entities.c:770: newEnt->pw                 = width;
	ld	hl, #0x000d
	add	hl, bc
	ld	a, 6 (ix)
	ld	(hl), a
;src/entities/entities.c:771: newEnt->ph                 = height;
	ld	hl, #0x000e
	add	hl, bc
	ld	a, 7 (ix)
	ld	(hl), a
;src/entities/entities.c:772: newEnt->graph.block.colour = colour;
	ld	e, c
	ld	d, b
	inc	de
	inc	de
	ld	a, 8 (ix)
	ld	(de), a
;src/entities/entities.c:773: setEntityLocation(newEnt, x, y, 0, 0, 1);
	push	bc
	ld	hl, #0x0100
	push	hl
	xor	a, a
	push	af
	inc	sp
	ld	h, 5 (ix)
	ld	l, 4 (ix)
	push	hl
	push	bc
	call	_setEntityLocation
	ld	hl, #7
	add	hl, sp
	ld	sp, hl
	pop	bc
;src/entities/entities.c:774: newEnt->draw               = 1;
	ld	hl, #0x001b
	add	hl, bc
	ld	(hl), #0x01
;src/entities/entities.c:777: newEnt->phys.y += g_blocks[g_lastBlock-1].phys.y % SCALE;
	ld	hl, #0x000f
	add	hl,bc
	ex	de,hl
;src/entities/entities.c:776: if (g_lastBlock > 0) 
	ld	iy, #_g_lastBlock
	ld	a, 0 (iy)
	or	a, a
	jr	Z,00102$
;src/entities/entities.c:777: newEnt->phys.y += g_blocks[g_lastBlock-1].phys.y % SCALE;
	ld	hl, #0x0002
	add	hl,de
	ld	-2 (ix), l
	ld	-1 (ix), h
	ld	a, (hl)
	ld	-4 (ix), a
	inc	hl
	ld	a, (hl)
	ld	-3 (ix), a
	ld	l, 0 (iy)
	ld	h, #0x00
	dec	hl
	push	de
	ld	e, l
	ld	d, h
	add	hl, hl
	add	hl, de
	add	hl, hl
	add	hl, de
	add	hl, hl
	add	hl, de
	add	hl, hl
	add	hl, de
	pop	de
	ld	iy, #_g_blocks
	push	bc
	ld	c, l
	ld	b, h
	add	iy, bc
	pop	bc
	ld	l, 17 (iy)
	ld	h, #0x00
	ld	a, -4 (ix)
	add	a, l
	ld	-4 (ix), a
	ld	a, -3 (ix)
	adc	a, h
	ld	-3 (ix), a
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	ld	a, -4 (ix)
	ld	(hl), a
	inc	hl
	ld	a, -3 (ix)
	ld	(hl), a
00102$:
;src/entities/entities.c:778: newEnt->phys.bounce        = 0.85 * SCALE;
	ld	hl, #0x0008
	add	hl, de
	ld	(hl), #0xd9
	inc	hl
	ld	(hl), #0x00
;src/entities/entities.c:779: newEnt->phys.vx            = 0;
	ld	hl, #0x0004
	add	hl, de
	xor	a, a
	ld	(hl), a
	inc	hl
	ld	(hl), a
;src/entities/entities.c:781: ++g_lastBlock;   // One more entity added to the vector
	ld	hl, #_g_lastBlock+0
	inc	(hl)
00104$:
;src/entities/entities.c:784: return newEnt;
	ld	l, c
	ld	h, b
	ld	sp, ix
	pop	ix
	ret
;src/entities/entities.c:790: void destroyBlock(u8 i) {
;	---------------------------------
; Function destroyBlock
; ---------------------------------
_destroyBlock::
	push	ix
	ld	ix,#0
	add	ix,sp
;src/entities/entities.c:791: i8 nEnts = g_lastBlock - i - 1; // Entities to the right of the block
	ld	a,(#_g_lastBlock + 0)
	sub	a, 4 (ix)
	ld	c, a
	dec	c
;src/entities/entities.c:794: if (g_blocks[i].phys.vx)
	ld	e,4 (ix)
	ld	d,#0x00
	ld	l, e
	ld	h, d
	add	hl, hl
	add	hl, de
	add	hl, hl
	add	hl, de
	add	hl, hl
	add	hl, de
	add	hl, hl
	add	hl, de
	ld	a, #<(_g_blocks)
	add	a, l
	ld	e, a
	ld	a, #>(_g_blocks)
	adc	a, h
	ld	d, a
	push	de
	pop	iy
	ld	l, 19 (iy)
	ld	a, 20 (iy)
	or	a,l
	jr	Z,00102$
;src/entities/entities.c:795: --g_movingBlocks;
	ld	hl, #_g_movingBlocks+0
	dec	(hl)
00102$:
;src/entities/entities.c:798: if (nEnts)
	ld	a, c
	or	a, a
	jr	Z,00104$
;src/entities/entities.c:799: cpct_memcpy(&g_blocks[i], &g_blocks[i+1], nEnts*sizeof(TEntity));
	ld	a, c
	rlc	a
	sbc	a, a
	ld	b, a
	ld	l, c
	ld	h, b
	add	hl, hl
	add	hl, bc
	add	hl, hl
	add	hl, bc
	add	hl, hl
	add	hl, bc
	add	hl, hl
	add	hl, bc
	ld	c, l
	ld	b, h
	ld	l, 4 (ix)
	ld	h, #0x00
	inc	hl
	push	de
	ld	e, l
	ld	d, h
	add	hl, hl
	add	hl, de
	add	hl, hl
	add	hl, de
	add	hl, hl
	add	hl, de
	add	hl, hl
	add	hl, de
	pop	de
	push	bc
	ld	bc, #_g_blocks
	add	hl, bc
	push	hl
	push	de
	call	_cpct_memcpy
00104$:
;src/entities/entities.c:802: --g_lastBlock;
	ld	hl, #_g_lastBlock+0
	dec	(hl)
	pop	ix
	ret
;src/entities/entities.c:817: u8 randomCreateNewBlock(u8 y, u8 h, u8 rndinc) {
;	---------------------------------
; Function randomCreateNewBlock
; ---------------------------------
_randomCreateNewBlock::
	push	ix
	ld	ix,#0
	add	ix,sp
	push	af
;src/entities/entities.c:818: u8 last_y = g_blocks[g_lastBlock-1].ny;   // y coordinate of the upmost block
	ld	bc, #_g_blocks+0
	ld	hl,#_g_lastBlock + 0
	ld	e, (hl)
	ld	d, #0x00
	dec	de
	ld	l, e
	ld	h, d
	add	hl, hl
	add	hl, de
	add	hl, hl
	add	hl, de
	add	hl, hl
	add	hl, de
	add	hl, hl
	add	hl, de
	add	hl, bc
	ld	de, #0x000c
	add	hl, de
	ld	c, (hl)
;src/entities/entities.c:819: u8 created = 0;                           // Flag to signal if a new block was created
	ld	-2 (ix), #0x00
;src/entities/entities.c:823: if ( (RAND_0_15(1) + MINPIXELSPACE) < last_y ) {
	push	bc
	ld	a, #0x01
	push	af
	inc	sp
	call	_getRandomUniform
	inc	sp
	pop	bc
	ld	a, l
	and	a, #0x0f
	ld	e, a
	ld	d, #0x00
	ld	iy, #_G_minY
	ld	l, 0 (iy)
	ld	h, #0x00
	add	hl, de
	ld	de, #0x000a
	add	hl, de
	ld	b, #0x00
	ld	a, l
	sub	a, c
	ld	a, h
	sbc	a, b
	jp	PO, 00127$
	xor	a, #0x80
00127$:
	jp	P, 00108$
;src/entities/entities.c:825: u8 x = G_minX + RAND_0_63(1);  // Random X for the new block
	ld	a, #0x01
	push	af
	inc	sp
	call	_getRandomUniform
	inc	sp
	ld	a, l
	and	a, #0x3f
	ld	l, a
	ld	iy, #_G_minX
	ld	c, 0 (iy)
	add	hl, bc
	ld	e, l
;src/entities/entities.c:828: if (x >= G_maxX - 1) x = x - G_maxX + G_minX;
	ld	a,(#_G_maxX + 0)
	ld	-1 (ix), a
	ld	l, a
	ld	h, #0x00
	dec	hl
	ld	b, e
	ld	d, #0x00
	ld	a, b
	sub	a, l
	ld	a, d
	sbc	a, h
	jp	PO, 00128$
	xor	a, #0x80
00128$:
	jp	M, 00102$
	ld	a, e
	sub	a, -1 (ix)
	ld	l, a
	add	hl, bc
	ld	e, l
00102$:
;src/entities/entities.c:831: w = RAND_0_15(rndinc) + 4;
	push	de
	ld	a, 6 (ix)
	push	af
	inc	sp
	call	_getRandomUniform
	inc	sp
	pop	de
	ld	a, l
	and	a, #0x0f
	ld	d, a
	inc	d
	inc	d
	inc	d
	inc	d
;src/entities/entities.c:835: if (x + w > G_maxX) w = G_maxX - x;
	ld	c, e
	ld	b, #0x00
	ld	l, d
	ld	h, #0x00
	add	hl, bc
	ld	a,(#_G_maxX + 0)
	ld	-1 (ix), a
	ld	b, #0x00
	sub	a, l
	ld	a, b
	sbc	a, h
	jp	PO, 00129$
	xor	a, #0x80
00129$:
	jp	P, 00104$
	ld	a, -1 (ix)
	sub	a, e
	ld	d, a
00104$:
;src/entities/entities.c:838: if ( newSolidBlock(x, y, w, h, cpct_px2byteM0(G_platfColour, G_platfColour)) )
	push	de
	ld	a, (_G_platfColour)
	push	af
	inc	sp
	ld	a, (_G_platfColour)
	push	af
	inc	sp
	call	_cpct_px2byteM0
	ld	b, l
	pop	de
	push	bc
	inc	sp
	ld	a, 5 (ix)
	push	af
	inc	sp
	push	de
	inc	sp
	ld	d, 4 (ix)
	push	de
	call	_newSolidBlock
	pop	af
	pop	af
	inc	sp
	ld	a, h
	or	a,l
	jr	Z,00108$
;src/entities/entities.c:839: created = 1;
	ld	-2 (ix), #0x01
00108$:
;src/entities/entities.c:842: return created;
	ld	l, -2 (ix)
	ld	sp, ix
	pop	ix
	ret
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
