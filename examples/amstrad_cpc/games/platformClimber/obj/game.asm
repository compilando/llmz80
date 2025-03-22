;--------------------------------------------------------
; File Created by SDCC : free open source ANSI-C Compiler
; Version 3.6.8 #9946 (Linux)
;--------------------------------------------------------
	.module game
	.optsdcc -mz80
	
;--------------------------------------------------------
; Public variables in this module
;--------------------------------------------------------
	.globl _showGameEnd
	.globl _game
	.globl _wait4Key
	.globl _updateUser
	.globl _initializeGameScreen
	.globl _getRandomUniform
	.globl _drawFrame
	.globl _getCharacter
	.globl _drawAll
	.globl _getScore
	.globl _scrollWorld
	.globl _updateCharacter
	.globl _performAction
	.globl _initializeEntities
	.globl _cpct_getScreenPtr
	.globl _cpct_waitVSYNC
	.globl _cpct_drawStringM0
	.globl _cpct_setDrawCharM0
	.globl _cpct_drawSprite
	.globl _cpct_drawSolidBox
	.globl _cpct_px2byteM0
	.globl _cpct_isKeyPressed
	.globl _cpct_scanKeyboard_f
	.globl _cpct_memset
	.globl _sprintf
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
;src/game.c:30: void initializeGameScreen(u16 hiscore) {
;	---------------------------------
; Function initializeGameScreen
; ---------------------------------
_initializeGameScreen::
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	hl, #-6
	add	hl, sp
	ld	sp, hl
;src/game.c:36: cpct_clearScreen(0);
	ld	hl, #0x4000
	push	hl
	xor	a, a
	push	af
	inc	sp
	ld	h, #0xc0
	push	hl
	call	_cpct_memset
;src/game.c:41: c = cpct_px2byteM0(8,8);  // Colour pattern 8-8 (black-black)
	ld	hl, #0x0808
	push	hl
	call	_cpct_px2byteM0
	ld	c, l
;src/game.c:44: pscr = cpct_getScreenPtr(CPCT_VMEM_START, 54,   0);  
	push	bc
	ld	hl, #0x0036
	push	hl
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
	pop	bc
;src/game.c:45: cpct_drawSolidBox(pscr, c, 26, 200);
	ld	b, #0x00
	ld	de, #0xc81a
	push	de
	push	bc
	push	hl
	call	_cpct_drawSolidBox
;src/game.c:48: pscr = cpct_getScreenPtr(CPCT_VMEM_START, 60,  16);   
	ld	hl, #0x103c
	push	hl
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
;src/game.c:49: cpct_setDrawCharM0(3, 8);
	push	hl
	ld	bc, #0x0803
	push	bc
	call	_cpct_setDrawCharM0
	pop	hl
;src/game.c:50: cpct_drawStringM0("HI", pscr);
	ld	bc, #___str_0+0
	push	hl
	push	bc
	call	_cpct_drawStringM0
;src/game.c:53: pscr = cpct_getScreenPtr(CPCT_VMEM_START, 60,  24);
	ld	hl, #0x183c
	push	hl
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
	ld	c, l
	ld	b, h
;src/game.c:54: sprintf(str, "%5u", hiscore);
	ld	hl, #0x0000
	add	hl, sp
	push	hl
	pop	iy
	push	hl
	push	bc
	ld	e,4 (ix)
	ld	d,5 (ix)
	push	de
	ld	de, #___str_1
	push	de
	push	iy
	call	_sprintf
	ld	hl, #6
	add	hl, sp
	ld	sp, hl
	ld	de, #0x080f
	push	de
	call	_cpct_setDrawCharM0
	pop	bc
	pop	hl
;src/game.c:56: cpct_drawStringM0(str, pscr);
	push	bc
	push	hl
	call	_cpct_drawStringM0
;src/game.c:59: pscr = cpct_getScreenPtr(CPCT_VMEM_START, 60, 172);
	ld	hl, #0xac3c
	push	hl
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
;src/game.c:60: cpct_drawSprite(G_credits, pscr, 20, 27);
	ld	bc, #_G_credits+0
	ld	de, #0x1b14
	push	de
	push	hl
	push	bc
	call	_cpct_drawSprite
;src/game.c:63: drawFrame(CPCT_VMEM_START, 0);
	xor	a, a
	push	af
	inc	sp
	ld	hl, #0xc000
	push	hl
	call	_drawFrame
	ld	sp,ix
	pop	ix
	ret
___str_0:
	.ascii "HI"
	.db 0x00
___str_1:
	.ascii "%5u"
	.db 0x00
;src/game.c:69: void updateUser(TCharacter* user) {
;	---------------------------------
; Function updateUser
; ---------------------------------
_updateUser::
	push	ix
	ld	ix,#0
	add	ix,sp
;src/game.c:71: cpct_scanKeyboard_f();
	call	_cpct_scanKeyboard_f
;src/game.c:78: if ( cpct_isKeyPressed(Key_CursorUp) && user->status != es_jump ) {
	ld	hl, #0x0100
	call	_cpct_isKeyPressed
	ld	c,4 (ix)
	ld	b,5 (ix)
;src/game.c:79: performAction(user, es_jump, user->side);    // Perform the action of jumping
	ld	a, c
	add	a, #0x20
	ld	e, a
	ld	a, b
	adc	a, #0x00
	ld	d, a
;src/game.c:78: if ( cpct_isKeyPressed(Key_CursorUp) && user->status != es_jump ) {
	ld	a, l
	or	a, a
	jr	Z,00111$
	push	bc
	pop	iy
	ld	a, 31 (iy)
	sub	a, #0x02
	jr	Z,00111$
;src/game.c:79: performAction(user, es_jump, user->side);    // Perform the action of jumping
	ld	a, (de)
	ld	d, a
	push	bc
	ld	e, #0x02
	push	de
	push	bc
	call	_performAction
	pop	af
	pop	af
	pop	bc
;src/game.c:80: getRandomUniform(user->entity.nx);           // Use X coordinate of the user when jumping to forward update the random seed
	push	bc
	pop	iy
	ld	b, 11 (iy)
	push	bc
	inc	sp
	call	_getRandomUniform
	inc	sp
	jr	00114$
00111$:
;src/game.c:83: } else if ( cpct_isKeyPressed(Key_CursorRight) )
	push	bc
	push	de
	ld	hl, #0x0200
	call	_cpct_isKeyPressed
	pop	de
	pop	bc
	ld	a, l
	or	a, a
	jr	Z,00108$
;src/game.c:84: performAction(user, es_walk, s_right);       // Move player to the right
	ld	hl, #0x0101
	push	hl
	ld	l,4 (ix)
	ld	h,5 (ix)
	push	hl
	call	_performAction
	pop	af
	pop	af
	jr	00114$
00108$:
;src/game.c:87: else if ( cpct_isKeyPressed(Key_CursorLeft) ) 
	push	bc
	push	de
	ld	hl, #0x0101
	call	_cpct_isKeyPressed
	pop	de
	pop	bc
	ld	a, l
	or	a, a
	jr	Z,00105$
;src/game.c:88: performAction(user, es_walk, s_left);        // Move player to the left
	ld	hl, #0x0001
	push	hl
	ld	l,4 (ix)
	ld	h,5 (ix)
	push	hl
	call	_performAction
	pop	af
	pop	af
	jr	00114$
00105$:
;src/game.c:91: else if ( cpct_isKeyPressed(Key_CursorDown) ) 
	push	bc
	push	de
	ld	hl, #0x0400
	call	_cpct_isKeyPressed
	ld	a, l
	pop	de
	pop	bc
;src/game.c:79: performAction(user, es_jump, user->side);    // Perform the action of jumping
	push	af
	ld	a, (de)
	ld	d, a
	pop	af
;src/game.c:91: else if ( cpct_isKeyPressed(Key_CursorDown) ) 
	or	a, a
	jr	Z,00102$
;src/game.c:92: performAction(user, es_moveFloor, user->side); // Enable moving floor
	ld	e, #0x03
	push	de
	push	bc
	call	_performAction
	pop	af
	pop	af
	jr	00114$
00102$:
;src/game.c:96: performAction(user, es_static, user->side);
	push	de
	inc	sp
	xor	a, a
	push	af
	inc	sp
	push	bc
	call	_performAction
	pop	af
	pop	af
00114$:
	pop	ix
	ret
;src/game.c:102: void wait4Key(cpct_keyID key) {
;	---------------------------------
; Function wait4Key
; ---------------------------------
_wait4Key::
;src/game.c:103: do
00101$:
;src/game.c:104: cpct_scanKeyboard_f();
	call	_cpct_scanKeyboard_f
;src/game.c:105: while( ! cpct_isKeyPressed(key) );
	pop	bc
	pop	hl
	push	hl
	push	bc
	call	_cpct_isKeyPressed
	ld	a, l
	or	a, a
	jr	Z,00101$
;src/game.c:106: do
00104$:
;src/game.c:107: cpct_scanKeyboard_f();
	call	_cpct_scanKeyboard_f
;src/game.c:108: while( cpct_isKeyPressed(key) );
	pop	bc
	pop	hl
	push	hl
	push	bc
	call	_cpct_isKeyPressed
	ld	a, l
	or	a, a
	jr	NZ,00104$
	ret
;src/game.c:114: u16 game(u16 hiscore) {
;	---------------------------------
; Function game
; ---------------------------------
_game::
	dec	sp
;src/game.c:115: u8 alive = 1;        // Main character still alive?
	ld	iy, #0
	add	iy, sp
	ld	0 (iy), #0x01
;src/game.c:119: initializeGameScreen(hiscore);   // Set up Game Screen
	ld	hl, #3
	add	hl, sp
	ld	c, (hl)
	inc	hl
	ld	b, (hl)
	push	bc
	call	_initializeGameScreen
	pop	af
;src/game.c:120: initializeEntities();            // Set up initial entities
	call	_initializeEntities
;src/game.c:121: c = getCharacter();              // Get the main character
	call	_getCharacter
;src/game.c:126: while(alive) {
00101$:
	ld	iy, #0
	add	iy, sp
	ld	a, 0 (iy)
	or	a, a
	jr	Z,00103$
;src/game.c:127: updateUser(c);                // Update user status (depending on keypresses)
	push	hl
	push	hl
	call	_updateUser
	pop	af
	call	_scrollWorld
	pop	hl
;src/game.c:129: alive = updateCharacter(c);   // Update character status     
	push	hl
	push	hl
	call	_updateCharacter
	pop	af
	ld	c, l
	pop	hl
	ld	iy, #0
	add	iy, sp
	ld	0 (iy), c
;src/game.c:130: cpct_waitVSYNC();             // Wait for VSYNC and...
	push	hl
	call	_cpct_waitVSYNC
	call	_drawAll
	pop	hl
	jr	00101$
00103$:
;src/game.c:135: return getScore();
	call	_getScore
	inc	sp
	ret
;src/game.c:141: void showGameEnd(u16 score) {
;	---------------------------------
; Function showGameEnd
; ---------------------------------
_showGameEnd::
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	hl, #-6
	add	hl, sp
	ld	sp, hl
;src/game.c:146: pscr = cpct_getScreenPtr(CPCT_VMEM_START,  8, 24);
	ld	hl, #0x1808
	push	hl
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
;src/game.c:147: cpct_setDrawCharM0(6, 0);
	push	hl
	ld	bc, #0x0006
	push	bc
	call	_cpct_setDrawCharM0
	pop	hl
;src/game.c:148: cpct_drawStringM0("GAME  OVER", pscr);
	ld	bc, #___str_2+0
	push	hl
	push	bc
	call	_cpct_drawStringM0
;src/game.c:151: pscr = cpct_getScreenPtr(CPCT_VMEM_START, 16, 48);
	ld	hl, #0x3010
	push	hl
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
;src/game.c:152: cpct_setDrawCharM0(9, 0);
	push	hl
	ld	bc, #0x0009
	push	bc
	call	_cpct_setDrawCharM0
	pop	hl
;src/game.c:153: cpct_drawStringM0(  "SCORE", pscr);
	ld	bc, #___str_3+0
	push	hl
	push	bc
	call	_cpct_drawStringM0
;src/game.c:156: pscr = cpct_getScreenPtr(CPCT_VMEM_START, 16, 56);
	ld	hl, #0x3810
	push	hl
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
	ld	c, l
	ld	b, h
;src/game.c:157: sprintf(str, "%5u", score);
	ld	hl, #0x0000
	add	hl, sp
	push	hl
	pop	iy
	push	hl
	push	bc
	ld	e,4 (ix)
	ld	d,5 (ix)
	push	de
	ld	de, #___str_4
	push	de
	push	iy
	call	_sprintf
	ld	hl, #6
	add	hl, sp
	ld	sp, hl
	ld	de, #0x000e
	push	de
	call	_cpct_setDrawCharM0
	pop	bc
	pop	hl
;src/game.c:159: cpct_drawStringM0(str, pscr);
	push	bc
	push	hl
	call	_cpct_drawStringM0
;src/game.c:162: pscr = cpct_getScreenPtr(CPCT_VMEM_START, 6, 112);
	ld	hl, #0x7006
	push	hl
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
;src/game.c:163: cpct_setDrawCharM0(11, 0);
	push	hl
	ld	bc, #0x000b
	push	bc
	call	_cpct_setDrawCharM0
	pop	hl
;src/game.c:164: cpct_drawStringM0("PRESS SPACE", pscr);
	ld	bc, #___str_5+0
	push	hl
	push	bc
	call	_cpct_drawStringM0
;src/game.c:167: wait4Key(Key_Space);
	ld	hl, #0x8005
	push	hl
	call	_wait4Key
	ld	sp,ix
	pop	ix
	ret
___str_2:
	.ascii "GAME  OVER"
	.db 0x00
___str_3:
	.ascii "SCORE"
	.db 0x00
___str_4:
	.ascii "%5u"
	.db 0x00
___str_5:
	.ascii "PRESS SPACE"
	.db 0x00
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
