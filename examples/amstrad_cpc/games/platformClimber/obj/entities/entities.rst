                              1 ;--------------------------------------------------------
                              2 ; File Created by SDCC : free open source ANSI-C Compiler
                              3 ; Version 3.6.8 #9946 (Linux)
                              4 ;--------------------------------------------------------
                              5 	.module entities
                              6 	.optsdcc -mz80
                              7 	
                              8 ;--------------------------------------------------------
                              9 ; Public variables in this module
                             10 ;--------------------------------------------------------
                             11 	.globl _cropVelocity
                             12 	.globl _getRandomUniform
                             13 	.globl _updateAnimation
                             14 	.globl _cpct_getScreenPtr
                             15 	.globl _cpct_drawSprite
                             16 	.globl _cpct_drawSolidBox
                             17 	.globl _cpct_px2byteM0
                             18 	.globl _cpct_memcpy
                             19 	.globl _g_movingBlocks
                             20 	.globl _g_colMaxBlock
                             21 	.globl _g_colMinBlock
                             22 	.globl _g_lastBlock
                             23 	.globl _g_blocks
                             24 	.globl _G_score
                             25 	.globl _G_platfColour
                             26 	.globl _G_scrollVel
                             27 	.globl _g_Character
                             28 	.globl _g_SCR_HEIGHT
                             29 	.globl _g_SCR_WIDTH
                             30 	.globl _G_maxY
                             31 	.globl _G_minY
                             32 	.globl _G_maxX
                             33 	.globl _G_minX
                             34 	.globl _G_floorFric
                             35 	.globl _G_airFric
                             36 	.globl _G_maxScrollVel
                             37 	.globl _G_jumpVel
                             38 	.globl _G_minVel
                             39 	.globl _G_maxXVel
                             40 	.globl _G_maxYVel
                             41 	.globl _G_gx
                             42 	.globl _G_gy
                             43 	.globl _initializeEntities
                             44 	.globl _getScore
                             45 	.globl _getCharacter
                             46 	.globl _performAction
                             47 	.globl _moveBlock
                             48 	.globl _scrollWorld
                             49 	.globl _updateCharacterPhysics
                             50 	.globl _getNearestBlockID
                             51 	.globl _applyCharacterBlockCollisions
                             52 	.globl _updateCharacter
                             53 	.globl _checkCollisionEntBlock
                             54 	.globl _isOverFloor
                             55 	.globl _setEntityLocation
                             56 	.globl _drawAnimEntity
                             57 	.globl _drawBlockEntity
                             58 	.globl _drawAll
                             59 	.globl _newSolidBlock
                             60 	.globl _destroyBlock
                             61 	.globl _randomCreateNewBlock
                             62 ;--------------------------------------------------------
                             63 ; special function registers
                             64 ;--------------------------------------------------------
                             65 ;--------------------------------------------------------
                             66 ; ram data
                             67 ;--------------------------------------------------------
                             68 	.area _DATA
   739C                      69 _G_scrollVel::
   739C                      70 	.ds 2
   739E                      71 _G_platfColour::
   739E                      72 	.ds 1
   739F                      73 _G_score::
   739F                      74 	.ds 2
   73A1                      75 _g_blocks::
   73A1                      76 	.ds 496
   7591                      77 _g_lastBlock::
   7591                      78 	.ds 1
   7592                      79 _g_colMinBlock::
   7592                      80 	.ds 1
   7593                      81 _g_colMaxBlock::
   7593                      82 	.ds 1
   7594                      83 _g_movingBlocks::
   7594                      84 	.ds 1
   7595                      85 _checkCollisionEntBlock_c_1_213:
   7595                      86 	.ds 4
                             87 ;--------------------------------------------------------
                             88 ; ram data
                             89 ;--------------------------------------------------------
                             90 	.area _INITIALIZED
                             91 ;--------------------------------------------------------
                             92 ; absolute external ram data
                             93 ;--------------------------------------------------------
                             94 	.area _DABS (ABS)
                             95 ;--------------------------------------------------------
                             96 ; global & static initialisations
                             97 ;--------------------------------------------------------
                             98 	.area _HOME
                             99 	.area _GSINIT
                            100 	.area _GSFINAL
                            101 	.area _GSINIT
                            102 ;--------------------------------------------------------
                            103 ; Home
                            104 ;--------------------------------------------------------
                            105 	.area _HOME
                            106 	.area _HOME
                            107 ;--------------------------------------------------------
                            108 ; code
                            109 ;--------------------------------------------------------
                            110 	.area _CODE
                            111 ;src/entities/entities.c:119: void initializeEntities() {
                            112 ;	---------------------------------
                            113 ; Function initializeEntities
                            114 ; ---------------------------------
   463B                     115 _initializeEntities::
                            116 ;src/entities/entities.c:120: G_platfColour = cpct_px2byteM0(8, 8);
   463B 21 08 08      [10]  117 	ld	hl, #0x0808
   463E E5            [11]  118 	push	hl
   463F CD 7A 66      [17]  119 	call	_cpct_px2byteM0
   4642 FD 21 9E 73   [14]  120 	ld	iy, #_G_platfColour
   4646 FD 75 00      [19]  121 	ld	0 (iy), l
                            122 ;src/entities/entities.c:121: G_scrollVel = 3 * SCALE / FPS;  // Scroll down velocity, 3 px/sec
   4649 21 0F 00      [10]  123 	ld	hl, #0x000f
   464C 22 9C 73      [16]  124 	ld	(_G_scrollVel), hl
                            125 ;src/entities/entities.c:122: g_movingBlocks = 0;
   464F 21 94 75      [10]  126 	ld	hl,#_g_movingBlocks + 0
   4652 36 00         [10]  127 	ld	(hl), #0x00
                            128 ;src/entities/entities.c:125: g_lastBlock = 0;                                // Block ID 
   4654 21 91 75      [10]  129 	ld	hl,#_g_lastBlock + 0
   4657 36 00         [10]  130 	ld	(hl), #0x00
                            131 ;src/entities/entities.c:126: newSolidBlock( 4, 120, 50, 5, G_platfColour);   // 0 /
   4659 3A 9E 73      [13]  132 	ld	a, (_G_platfColour)
   465C F5            [11]  133 	push	af
   465D 33            [ 6]  134 	inc	sp
   465E 21 32 05      [10]  135 	ld	hl, #0x0532
   4661 E5            [11]  136 	push	hl
   4662 21 04 78      [10]  137 	ld	hl, #0x7804
   4665 E5            [11]  138 	push	hl
   4666 CD 44 5A      [17]  139 	call	_newSolidBlock
   4669 F1            [10]  140 	pop	af
   466A F1            [10]  141 	pop	af
   466B 33            [ 6]  142 	inc	sp
                            143 ;src/entities/entities.c:127: newSolidBlock(14, 100, 10, 3, G_platfColour);   // 1 /
   466C 3A 9E 73      [13]  144 	ld	a, (_G_platfColour)
   466F F5            [11]  145 	push	af
   4670 33            [ 6]  146 	inc	sp
   4671 21 0A 03      [10]  147 	ld	hl, #0x030a
   4674 E5            [11]  148 	push	hl
   4675 21 0E 64      [10]  149 	ld	hl, #0x640e
   4678 E5            [11]  150 	push	hl
   4679 CD 44 5A      [17]  151 	call	_newSolidBlock
   467C F1            [10]  152 	pop	af
   467D F1            [10]  153 	pop	af
   467E 33            [ 6]  154 	inc	sp
                            155 ;src/entities/entities.c:128: newSolidBlock(34, 100, 10, 3, G_platfColour);   // 2 /
   467F 3A 9E 73      [13]  156 	ld	a, (_G_platfColour)
   4682 F5            [11]  157 	push	af
   4683 33            [ 6]  158 	inc	sp
   4684 21 0A 03      [10]  159 	ld	hl, #0x030a
   4687 E5            [11]  160 	push	hl
   4688 21 22 64      [10]  161 	ld	hl, #0x6422
   468B E5            [11]  162 	push	hl
   468C CD 44 5A      [17]  163 	call	_newSolidBlock
   468F F1            [10]  164 	pop	af
   4690 F1            [10]  165 	pop	af
   4691 33            [ 6]  166 	inc	sp
                            167 ;src/entities/entities.c:129: newSolidBlock(26,  80,  6, 3, G_platfColour);   // 3 /
   4692 3A 9E 73      [13]  168 	ld	a, (_G_platfColour)
   4695 F5            [11]  169 	push	af
   4696 33            [ 6]  170 	inc	sp
   4697 21 06 03      [10]  171 	ld	hl, #0x0306
   469A E5            [11]  172 	push	hl
   469B 21 1A 50      [10]  173 	ld	hl, #0x501a
   469E E5            [11]  174 	push	hl
   469F CD 44 5A      [17]  175 	call	_newSolidBlock
   46A2 F1            [10]  176 	pop	af
   46A3 F1            [10]  177 	pop	af
   46A4 33            [ 6]  178 	inc	sp
                            179 ;src/entities/entities.c:130: newSolidBlock( 8,  60, 10, 3, G_platfColour);   // 4 /
   46A5 3A 9E 73      [13]  180 	ld	a, (_G_platfColour)
   46A8 F5            [11]  181 	push	af
   46A9 33            [ 6]  182 	inc	sp
   46AA 21 0A 03      [10]  183 	ld	hl, #0x030a
   46AD E5            [11]  184 	push	hl
   46AE 21 08 3C      [10]  185 	ld	hl, #0x3c08
   46B1 E5            [11]  186 	push	hl
   46B2 CD 44 5A      [17]  187 	call	_newSolidBlock
   46B5 F1            [10]  188 	pop	af
   46B6 F1            [10]  189 	pop	af
   46B7 33            [ 6]  190 	inc	sp
                            191 ;src/entities/entities.c:131: newSolidBlock(36,  55, 10, 3, G_platfColour);   // 5 /
   46B8 3A 9E 73      [13]  192 	ld	a, (_G_platfColour)
   46BB F5            [11]  193 	push	af
   46BC 33            [ 6]  194 	inc	sp
   46BD 21 0A 03      [10]  195 	ld	hl, #0x030a
   46C0 E5            [11]  196 	push	hl
   46C1 21 24 37      [10]  197 	ld	hl, #0x3724
   46C4 E5            [11]  198 	push	hl
   46C5 CD 44 5A      [17]  199 	call	_newSolidBlock
   46C8 F1            [10]  200 	pop	af
   46C9 F1            [10]  201 	pop	af
   46CA 33            [ 6]  202 	inc	sp
                            203 ;src/entities/entities.c:132: newSolidBlock(20,  30, 20, 3, G_platfColour);   // 6 /
   46CB 3A 9E 73      [13]  204 	ld	a, (_G_platfColour)
   46CE F5            [11]  205 	push	af
   46CF 33            [ 6]  206 	inc	sp
   46D0 21 14 03      [10]  207 	ld	hl, #0x0314
   46D3 E5            [11]  208 	push	hl
   46D4 26 1E         [ 7]  209 	ld	h, #0x1e
   46D6 E5            [11]  210 	push	hl
   46D7 CD 44 5A      [17]  211 	call	_newSolidBlock
   46DA F1            [10]  212 	pop	af
   46DB F1            [10]  213 	pop	af
   46DC 33            [ 6]  214 	inc	sp
                            215 ;src/entities/entities.c:133: newSolidBlock( 9,  10, 10, 3, G_platfColour);   // 7 /
   46DD 3A 9E 73      [13]  216 	ld	a, (_G_platfColour)
   46E0 F5            [11]  217 	push	af
   46E1 33            [ 6]  218 	inc	sp
   46E2 21 0A 03      [10]  219 	ld	hl, #0x030a
   46E5 E5            [11]  220 	push	hl
   46E6 21 09 0A      [10]  221 	ld	hl, #0x0a09
   46E9 E5            [11]  222 	push	hl
   46EA CD 44 5A      [17]  223 	call	_newSolidBlock
   46ED F1            [10]  224 	pop	af
   46EE F1            [10]  225 	pop	af
   46EF 33            [ 6]  226 	inc	sp
                            227 ;src/entities/entities.c:134: newSolidBlock(44,   9,  4, 3, G_platfColour);   // 8 /
   46F0 3A 9E 73      [13]  228 	ld	a, (_G_platfColour)
   46F3 F5            [11]  229 	push	af
   46F4 33            [ 6]  230 	inc	sp
   46F5 21 04 03      [10]  231 	ld	hl, #0x0304
   46F8 E5            [11]  232 	push	hl
   46F9 21 2C 09      [10]  233 	ld	hl, #0x092c
   46FC E5            [11]  234 	push	hl
   46FD CD 44 5A      [17]  235 	call	_newSolidBlock
   4700 F1            [10]  236 	pop	af
   4701 F1            [10]  237 	pop	af
   4702 33            [ 6]  238 	inc	sp
                            239 ;src/entities/entities.c:135: G_score = 9; // 9 points for the 9 starting blocks
   4703 21 09 00      [10]  240 	ld	hl, #0x0009
   4706 22 9F 73      [16]  241 	ld	(_G_score), hl
                            242 ;src/entities/entities.c:137: G_platfColour = 8;
   4709 21 9E 73      [10]  243 	ld	hl,#_G_platfColour + 0
   470C 36 08         [10]  244 	ld	(hl), #0x08
                            245 ;src/entities/entities.c:140: setEntityLocation(&g_Character.entity, 28, 120-20, 0, 0, 1);
   470E 21 00 01      [10]  246 	ld	hl, #0x0100
   4711 E5            [11]  247 	push	hl
   4712 21 64 00      [10]  248 	ld	hl, #0x0064
   4715 E5            [11]  249 	push	hl
   4716 3E 1C         [ 7]  250 	ld	a, #0x1c
   4718 F5            [11]  251 	push	af
   4719 33            [ 6]  252 	inc	sp
   471A 21 47 47      [10]  253 	ld	hl, #_g_Character
   471D E5            [11]  254 	push	hl
   471E CD 86 57      [17]  255 	call	_setEntityLocation
   4721 21 07 00      [10]  256 	ld	hl, #7
   4724 39            [11]  257 	add	hl, sp
   4725 F9            [ 6]  258 	ld	sp, hl
                            259 ;src/entities/entities.c:143: g_colMinBlock = 0;
   4726 21 92 75      [10]  260 	ld	hl,#_g_colMinBlock + 0
   4729 36 00         [10]  261 	ld	(hl), #0x00
                            262 ;src/entities/entities.c:144: g_colMaxBlock = 2;
   472B 21 93 75      [10]  263 	ld	hl,#_g_colMaxBlock + 0
   472E 36 02         [10]  264 	ld	(hl), #0x02
   4730 C9            [10]  265 	ret
   4731                     266 _G_gy:
   4731 32 00               267 	.dw #0x0032
   4733                     268 _G_gx:
   4733 00 00               269 	.dw #0x0000
   4735                     270 _G_maxYVel:
   4735 00 03               271 	.dw #0x0300
   4737                     272 _G_maxXVel:
   4737 00 01               273 	.dw #0x0100
   4739                     274 _G_minVel:
   4739 20 00               275 	.dw #0x0020
   473B                     276 _G_jumpVel:
   473B 00 FD               277 	.dw #0xfd00
   473D                     278 _G_maxScrollVel:
   473D 80 00               279 	.dw #0x0080
   473F                     280 _G_airFric:
   473F 02                  281 	.db #0x02	; 2
   4740                     282 _G_floorFric:
   4740 04                  283 	.db #0x04	; 4
   4741                     284 _G_minX:
   4741 04                  285 	.db #0x04	; 4
   4742                     286 _G_maxX:
   4742 36                  287 	.db #0x36	; 54	'6'
   4743                     288 _G_minY:
   4743 08                  289 	.db #0x08	; 8
   4744                     290 _G_maxY:
   4744 C0                  291 	.db #0xc0	; 192
   4745                     292 _g_SCR_WIDTH:
   4745 50                  293 	.db #0x50	; 80	'P'
   4746                     294 _g_SCR_HEIGHT:
   4746 C8                  295 	.db #0xc8	; 200
   4747                     296 _g_Character:
   4747 F5 5D               297 	.dw _g_walkRight
   4749 00                  298 	.db #0x00	; 0
   474A 02                  299 	.db #0x02	; 2
   474B 03                  300 	.db #0x03	; 3
   474C 00 C0               301 	.dw #0xc000
   474E 00 C0               302 	.dw #0xc000
   4750 00                  303 	.db #0x00	; 0
   4751 00                  304 	.db #0x00	; 0
   4752 00                  305 	.db #0x00	; 0
   4753 00                  306 	.db #0x00	; 0
   4754 00                  307 	.db #0x00	; 0
   4755 00                  308 	.db #0x00	; 0
   4756 00 00               309 	.dw #0x0000
   4758 00 00               310 	.dw #0x0000
   475A 00 00               311 	.dw #0x0000
   475C 00 00               312 	.dw #0x0000
   475E 00 00               313 	.dw #0x0000
   4760 00 00               314 	.dw #0x0000
   4762 00                  315 	.db #0x00	; 0
   4763 00 00               316 	.dw #0x0000
   4765 00                  317 	.db #0x00	; 0
   4766 01                  318 	.db #0x01	; 1
   4767 01                  319 	.db #0x01	; 1
                            320 ;src/entities/entities.c:150: u16 getScore() { return G_score; }
                            321 ;	---------------------------------
                            322 ; Function getScore
                            323 ; ---------------------------------
   4768                     324 _getScore::
   4768 2A 9F 73      [16]  325 	ld	hl, (_G_score)
   476B C9            [10]  326 	ret
                            327 ;src/entities/entities.c:151: TCharacter* getCharacter() { return &g_Character; }
                            328 ;	---------------------------------
                            329 ; Function getCharacter
                            330 ; ---------------------------------
   476C                     331 _getCharacter::
   476C 21 47 47      [10]  332 	ld	hl, #_g_Character
   476F C9            [10]  333 	ret
                            334 ;src/entities/entities.c:158: void performAction(TCharacter *c, TCharacterStatus move, TCharacterSide side) {
                            335 ;	---------------------------------
                            336 ; Function performAction
                            337 ; ---------------------------------
   4770                     338 _performAction::
   4770 DD E5         [15]  339 	push	ix
   4772 DD 21 00 00   [14]  340 	ld	ix,#0
   4776 DD 39         [15]  341 	add	ix,sp
   4778 21 F4 FF      [10]  342 	ld	hl, #-12
   477B 39            [11]  343 	add	hl, sp
   477C F9            [ 6]  344 	ld	sp, hl
                            345 ;src/entities/entities.c:159: TEntity *e = &c->entity;   // Get entity associated to the character
   477D DD 6E 04      [19]  346 	ld	l,4 (ix)
   4780 DD 66 05      [19]  347 	ld	h,5 (ix)
   4783 5D            [ 4]  348 	ld	e, l
   4784 54            [ 4]  349 	ld	d, h
                            350 ;src/entities/entities.c:160: TPhysics *p = &e->phys;    // Get Physics information associated to the entity
   4785 7B            [ 4]  351 	ld	a, e
   4786 C6 0F         [ 7]  352 	add	a, #0x0f
   4788 4F            [ 4]  353 	ld	c, a
   4789 7A            [ 4]  354 	ld	a, d
   478A CE 00         [ 7]  355 	adc	a, #0x00
   478C 47            [ 4]  356 	ld	b, a
                            357 ;src/entities/entities.c:170: switch(c->status) {
   478D 7D            [ 4]  358 	ld	a, l
   478E C6 1F         [ 7]  359 	add	a, #0x1f
   4790 DD 77 FE      [19]  360 	ld	-2 (ix), a
   4793 7C            [ 4]  361 	ld	a, h
   4794 CE 00         [ 7]  362 	adc	a, #0x00
   4796 DD 77 FF      [19]  363 	ld	-1 (ix), a
                            364 ;src/entities/entities.c:174: if ( side != c->side ) {
   4799 7D            [ 4]  365 	ld	a, l
   479A C6 20         [ 7]  366 	add	a, #0x20
   479C DD 77 F5      [19]  367 	ld	-11 (ix), a
   479F 7C            [ 4]  368 	ld	a, h
   47A0 CE 00         [ 7]  369 	adc	a, #0x00
   47A2 DD 77 F6      [19]  370 	ld	-10 (ix), a
                            371 ;src/entities/entities.c:175: e->nAnim   = g_anim[es_walk][side]; // Next animation changes
   47A5 21 1C 00      [10]  372 	ld	hl, #0x001c
   47A8 19            [11]  373 	add	hl,de
   47A9 DD 75 F7      [19]  374 	ld	-9 (ix), l
   47AC DD 74 F8      [19]  375 	ld	-8 (ix), h
   47AF DD 7E 07      [19]  376 	ld	a, 7 (ix)
   47B2 87            [ 4]  377 	add	a, a
   47B3 DD 77 F9      [19]  378 	ld	-7 (ix), a
                            379 ;src/entities/entities.c:178: e->nStatus = as_cycle;  // Make character cycle animation
   47B6 21 1E 00      [10]  380 	ld	hl, #0x001e
   47B9 19            [11]  381 	add	hl,de
   47BA EB            [ 4]  382 	ex	de,hl
                            383 ;src/entities/entities.c:163: switch(move) {
   47BB DD 7E 06      [19]  384 	ld	a, 6 (ix)
   47BE 3D            [ 4]  385 	dec	a
   47BF 28 1D         [12]  386 	jr	Z,00101$
                            387 ;src/entities/entities.c:209: p->floor   = 0;         // When jumping, we left the floor
   47C1 21 0A 00      [10]  388 	ld	hl, #0x000a
   47C4 09            [11]  389 	add	hl,bc
   47C5 DD 75 FA      [19]  390 	ld	-6 (ix), l
   47C8 DD 74 FB      [19]  391 	ld	-5 (ix), h
                            392 ;src/entities/entities.c:163: switch(move) {
   47CB DD 7E 06      [19]  393 	ld	a, 6 (ix)
   47CE D6 02         [ 7]  394 	sub	a, #0x02
   47D0 CA 55 48      [10]  395 	jp	Z,00111$
   47D3 DD 7E 06      [19]  396 	ld	a, 6 (ix)
   47D6 D6 03         [ 7]  397 	sub	a, #0x03
   47D8 CA B7 48      [10]  398 	jp	Z,00114$
   47DB C3 F6 48      [10]  399 	jp	00122$
                            400 ;src/entities/entities.c:167: case es_walk:
   47DE                     401 00101$:
                            402 ;src/entities/entities.c:170: switch(c->status) {
   47DE DD 6E FE      [19]  403 	ld	l,-2 (ix)
   47E1 DD 66 FF      [19]  404 	ld	h,-1 (ix)
   47E4 7E            [ 7]  405 	ld	a, (hl)
   47E5 FE 01         [ 7]  406 	cp	a, #0x01
   47E7 28 07         [12]  407 	jr	Z,00102$
   47E9 D6 02         [ 7]  408 	sub	a, #0x02
   47EB 28 45         [12]  409 	jr	Z,00105$
   47ED C3 03 49      [10]  410 	jp	00126$
                            411 ;src/entities/entities.c:172: case es_walk:
   47F0                     412 00102$:
                            413 ;src/entities/entities.c:174: if ( side != c->side ) {
   47F0 DD 6E F5      [19]  414 	ld	l,-11 (ix)
   47F3 DD 66 F6      [19]  415 	ld	h,-10 (ix)
   47F6 7E            [ 7]  416 	ld	a, (hl)
   47F7 DD 77 F4      [19]  417 	ld	-12 (ix), a
   47FA DD 7E 07      [19]  418 	ld	a, 7 (ix)
   47FD DD 96 F4      [19]  419 	sub	a, -12 (ix)
   4800 28 2D         [12]  420 	jr	Z,00104$
                            421 ;src/entities/entities.c:175: e->nAnim   = g_anim[es_walk][side]; // Next animation changes
   4802 3E 23         [ 7]  422 	ld	a, #<((_g_anim + 0x0004))
   4804 DD 86 F9      [19]  423 	add	a, -7 (ix)
   4807 6F            [ 4]  424 	ld	l, a
   4808 3E 5E         [ 7]  425 	ld	a, #>((_g_anim + 0x0004))
   480A CE 00         [ 7]  426 	adc	a, #0x00
   480C 67            [ 4]  427 	ld	h, a
   480D 7E            [ 7]  428 	ld	a, (hl)
   480E DD 77 FC      [19]  429 	ld	-4 (ix), a
   4811 23            [ 6]  430 	inc	hl
   4812 7E            [ 7]  431 	ld	a, (hl)
   4813 DD 77 FD      [19]  432 	ld	-3 (ix), a
   4816 DD 6E F7      [19]  433 	ld	l,-9 (ix)
   4819 DD 66 F8      [19]  434 	ld	h,-8 (ix)
   481C DD 7E FC      [19]  435 	ld	a, -4 (ix)
   481F 77            [ 7]  436 	ld	(hl), a
   4820 23            [ 6]  437 	inc	hl
   4821 DD 7E FD      [19]  438 	ld	a, -3 (ix)
   4824 77            [ 7]  439 	ld	(hl), a
                            440 ;src/entities/entities.c:176: c->side    = side;
   4825 DD 6E F5      [19]  441 	ld	l,-11 (ix)
   4828 DD 66 F6      [19]  442 	ld	h,-10 (ix)
   482B DD 7E 07      [19]  443 	ld	a, 7 (ix)
   482E 77            [ 7]  444 	ld	(hl), a
   482F                     445 00104$:
                            446 ;src/entities/entities.c:178: e->nStatus = as_cycle;  // Make character cycle animation
   482F 3E 02         [ 7]  447 	ld	a, #0x02
   4831 12            [ 7]  448 	ld	(de), a
                            449 ;src/entities/entities.c:184: case es_jump:
   4832                     450 00105$:
                            451 ;src/entities/entities.c:188: p->vx -= SCALE;
   4832 21 04 00      [10]  452 	ld	hl, #0x0004
   4835 09            [11]  453 	add	hl, bc
   4836 E5            [11]  454 	push	hl
   4837 4E            [ 7]  455 	ld	c, (hl)
   4838 23            [ 6]  456 	inc	hl
   4839 46            [ 7]  457 	ld	b, (hl)
   483A E1            [10]  458 	pop	hl
                            459 ;src/entities/entities.c:187: if ( side == s_left )
   483B DD 7E 07      [19]  460 	ld	a, 7 (ix)
   483E B7            [ 4]  461 	or	a, a
   483F 20 0A         [12]  462 	jr	NZ,00107$
                            463 ;src/entities/entities.c:188: p->vx -= SCALE;
   4841 78            [ 4]  464 	ld	a,b
   4842 C6 FF         [ 7]  465 	add	a,#0xff
   4844 47            [ 4]  466 	ld	b, a
   4845 71            [ 7]  467 	ld	(hl), c
   4846 23            [ 6]  468 	inc	hl
   4847 70            [ 7]  469 	ld	(hl), b
   4848 C3 03 49      [10]  470 	jp	00126$
   484B                     471 00107$:
                            472 ;src/entities/entities.c:190: p->vx += SCALE;
   484B 78            [ 4]  473 	ld	a,b
   484C C6 01         [ 7]  474 	add	a,#0x01
   484E 47            [ 4]  475 	ld	b, a
   484F 71            [ 7]  476 	ld	(hl), c
   4850 23            [ 6]  477 	inc	hl
   4851 70            [ 7]  478 	ld	(hl), b
                            479 ;src/entities/entities.c:191: break;
   4852 C3 03 49      [10]  480 	jp	00126$
                            481 ;src/entities/entities.c:202: case es_jump:
   4855                     482 00111$:
                            483 ;src/entities/entities.c:204: if (c->status == es_walk) {
   4855 DD 6E FE      [19]  484 	ld	l,-2 (ix)
   4858 DD 66 FF      [19]  485 	ld	h,-1 (ix)
   485B 6E            [ 7]  486 	ld	l, (hl)
   485C 2D            [ 4]  487 	dec	l
   485D C2 03 49      [10]  488 	jp	NZ,00126$
                            489 ;src/entities/entities.c:205: e->nAnim   = g_anim[es_jump][side]; // Next animation changes
   4860 3E 27         [ 7]  490 	ld	a, #<((_g_anim + 0x0008))
   4862 DD 86 F9      [19]  491 	add	a, -7 (ix)
   4865 6F            [ 4]  492 	ld	l, a
   4866 3E 5E         [ 7]  493 	ld	a, #>((_g_anim + 0x0008))
   4868 CE 00         [ 7]  494 	adc	a, #0x00
   486A 67            [ 4]  495 	ld	h, a
   486B 7E            [ 7]  496 	ld	a, (hl)
   486C DD 77 FC      [19]  497 	ld	-4 (ix), a
   486F 23            [ 6]  498 	inc	hl
   4870 7E            [ 7]  499 	ld	a, (hl)
   4871 DD 77 FD      [19]  500 	ld	-3 (ix), a
   4874 DD 6E F7      [19]  501 	ld	l,-9 (ix)
   4877 DD 66 F8      [19]  502 	ld	h,-8 (ix)
   487A DD 7E FC      [19]  503 	ld	a, -4 (ix)
   487D 77            [ 7]  504 	ld	(hl), a
   487E 23            [ 6]  505 	inc	hl
   487F DD 7E FD      [19]  506 	ld	a, -3 (ix)
   4882 77            [ 7]  507 	ld	(hl), a
                            508 ;src/entities/entities.c:206: e->nStatus = as_play;   // Jump animation only plays once
   4883 3E 01         [ 7]  509 	ld	a, #0x01
   4885 12            [ 7]  510 	ld	(de), a
                            511 ;src/entities/entities.c:207: c->side    = side;      // New side
   4886 DD 6E F5      [19]  512 	ld	l,-11 (ix)
   4889 DD 66 F6      [19]  513 	ld	h,-10 (ix)
   488C DD 7E 07      [19]  514 	ld	a, 7 (ix)
   488F 77            [ 7]  515 	ld	(hl), a
                            516 ;src/entities/entities.c:208: c->status  = es_jump;   // New status
   4890 DD 6E FE      [19]  517 	ld	l,-2 (ix)
   4893 DD 66 FF      [19]  518 	ld	h,-1 (ix)
   4896 36 02         [10]  519 	ld	(hl), #0x02
                            520 ;src/entities/entities.c:209: p->floor   = 0;         // When jumping, we left the floor
   4898 DD 6E FA      [19]  521 	ld	l,-6 (ix)
   489B DD 66 FB      [19]  522 	ld	h,-5 (ix)
   489E AF            [ 4]  523 	xor	a, a
   489F 77            [ 7]  524 	ld	(hl), a
   48A0 23            [ 6]  525 	inc	hl
   48A1 77            [ 7]  526 	ld	(hl), a
                            527 ;src/entities/entities.c:210: p->vy     += G_jumpVel; // Add jump velocity to the character
   48A2 21 06 00      [10]  528 	ld	hl, #0x0006
   48A5 09            [11]  529 	add	hl,bc
   48A6 4D            [ 4]  530 	ld	c,l
   48A7 44            [ 4]  531 	ld	b,h
   48A8 5E            [ 7]  532 	ld	e, (hl)
   48A9 23            [ 6]  533 	inc	hl
   48AA 56            [ 7]  534 	ld	d, (hl)
   48AB 2A 3B 47      [16]  535 	ld	hl, (_G_jumpVel)
   48AE 19            [11]  536 	add	hl,de
   48AF EB            [ 4]  537 	ex	de,hl
   48B0 7B            [ 4]  538 	ld	a, e
   48B1 02            [ 7]  539 	ld	(bc), a
   48B2 03            [ 6]  540 	inc	bc
   48B3 7A            [ 4]  541 	ld	a, d
   48B4 02            [ 7]  542 	ld	(bc), a
                            543 ;src/entities/entities.c:212: break;
   48B5 18 4C         [12]  544 	jr	00126$
                            545 ;src/entities/entities.c:217: case es_moveFloor:
   48B7                     546 00114$:
                            547 ;src/entities/entities.c:219: if (p->floor && !p->floor->phys.vx && g_movingBlocks < g_MaxMovingBlocks) {
   48B7 DD 6E FA      [19]  548 	ld	l,-6 (ix)
   48BA DD 66 FB      [19]  549 	ld	h,-5 (ix)
   48BD 4E            [ 7]  550 	ld	c, (hl)
   48BE 23            [ 6]  551 	inc	hl
   48BF 46            [ 7]  552 	ld	b, (hl)
   48C0 78            [ 4]  553 	ld	a, b
   48C1 B1            [ 4]  554 	or	a,c
   48C2 28 3F         [12]  555 	jr	Z,00126$
   48C4 21 13 00      [10]  556 	ld	hl, #0x0013
   48C7 09            [11]  557 	add	hl,bc
   48C8 4D            [ 4]  558 	ld	c,l
   48C9 44            [ 4]  559 	ld	b,h
   48CA 5E            [ 7]  560 	ld	e, (hl)
   48CB 23            [ 6]  561 	inc	hl
   48CC 7E            [ 7]  562 	ld	a, (hl)
   48CD B3            [ 4]  563 	or	a,e
   48CE 20 33         [12]  564 	jr	NZ,00126$
   48D0 FD 21 94 75   [14]  565 	ld	iy, #_g_movingBlocks
   48D4 FD 7E 00      [19]  566 	ld	a, 0 (iy)
   48D7 D6 02         [ 7]  567 	sub	a, #0x02
   48D9 30 28         [12]  568 	jr	NC,00126$
                            569 ;src/entities/entities.c:220: ++g_movingBlocks;
   48DB FD 34 00      [23]  570 	inc	0 (iy)
                            571 ;src/entities/entities.c:221: if (side == s_left)
   48DE DD 7E 07      [19]  572 	ld	a, 7 (ix)
   48E1 B7            [ 4]  573 	or	a, a
   48E2 20 09         [12]  574 	jr	NZ,00116$
                            575 ;src/entities/entities.c:222: p->floor->phys.vx = -SCALE / 2;
   48E4 3E 80         [ 7]  576 	ld	a, #0x80
   48E6 02            [ 7]  577 	ld	(bc), a
   48E7 03            [ 6]  578 	inc	bc
   48E8 3E FF         [ 7]  579 	ld	a, #0xff
   48EA 02            [ 7]  580 	ld	(bc), a
   48EB 18 16         [12]  581 	jr	00126$
   48ED                     582 00116$:
                            583 ;src/entities/entities.c:224: p->floor->phys.vx = SCALE / 2;
   48ED 3E 80         [ 7]  584 	ld	a, #0x80
   48EF 02            [ 7]  585 	ld	(bc), a
   48F0 03            [ 6]  586 	inc	bc
   48F1 3E 00         [ 7]  587 	ld	a, #0x00
   48F3 02            [ 7]  588 	ld	(bc), a
                            589 ;src/entities/entities.c:226: break;
   48F4 18 0D         [12]  590 	jr	00126$
                            591 ;src/entities/entities.c:229: default:
   48F6                     592 00122$:
                            593 ;src/entities/entities.c:231: if ( c->status == es_walk )
   48F6 DD 6E FE      [19]  594 	ld	l,-2 (ix)
   48F9 DD 66 FF      [19]  595 	ld	h,-1 (ix)
   48FC 4E            [ 7]  596 	ld	c, (hl)
   48FD 0D            [ 4]  597 	dec	c
   48FE 20 03         [12]  598 	jr	NZ,00126$
                            599 ;src/entities/entities.c:232: e->nStatus = as_pause;     // Pause animation on next timestep
   4900 3E 03         [ 7]  600 	ld	a, #0x03
   4902 12            [ 7]  601 	ld	(de), a
                            602 ;src/entities/entities.c:233: }
   4903                     603 00126$:
   4903 DD F9         [10]  604 	ld	sp, ix
   4905 DD E1         [14]  605 	pop	ix
   4907 C9            [10]  606 	ret
                            607 ;src/entities/entities.c:239: void cropVelocity(i16 *v, i16 maxvel, i16 minvel) {
                            608 ;	---------------------------------
                            609 ; Function cropVelocity
                            610 ; ---------------------------------
   4908                     611 _cropVelocity::
   4908 DD E5         [15]  612 	push	ix
   490A DD 21 00 00   [14]  613 	ld	ix,#0
   490E DD 39         [15]  614 	add	ix,sp
                            615 ;src/entities/entities.c:242: if ( *v >= 0 ) {
   4910 DD 6E 04      [19]  616 	ld	l,4 (ix)
   4913 DD 66 05      [19]  617 	ld	h,5 (ix)
   4916 E5            [11]  618 	push	hl
   4917 5E            [ 7]  619 	ld	e, (hl)
   4918 23            [ 6]  620 	inc	hl
   4919 56            [ 7]  621 	ld	d, (hl)
   491A E1            [10]  622 	pop	hl
   491B CB 7A         [ 8]  623 	bit	7, d
   491D 20 31         [12]  624 	jr	NZ,00112$
                            625 ;src/entities/entities.c:244: if      ( *v > maxvel ) *v = maxvel; // Crop to max. positive velocity
   491F DD 7E 06      [19]  626 	ld	a, 6 (ix)
   4922 93            [ 4]  627 	sub	a, e
   4923 DD 7E 07      [19]  628 	ld	a, 7 (ix)
   4926 9A            [ 4]  629 	sbc	a, d
   4927 E2 2C 49      [10]  630 	jp	PO, 00136$
   492A EE 80         [ 7]  631 	xor	a, #0x80
   492C                     632 00136$:
   492C F2 3A 49      [10]  633 	jp	P, 00104$
   492F DD 7E 06      [19]  634 	ld	a, 6 (ix)
   4932 77            [ 7]  635 	ld	(hl), a
   4933 23            [ 6]  636 	inc	hl
   4934 DD 7E 07      [19]  637 	ld	a, 7 (ix)
   4937 77            [ 7]  638 	ld	(hl), a
   4938 18 4D         [12]  639 	jr	00114$
   493A                     640 00104$:
                            641 ;src/entities/entities.c:245: else if ( *v < minvel ) *v = 0;      // Round to min positive velocity
   493A 7B            [ 4]  642 	ld	a, e
   493B DD 96 08      [19]  643 	sub	a, 8 (ix)
   493E 7A            [ 4]  644 	ld	a, d
   493F DD 9E 09      [19]  645 	sbc	a, 9 (ix)
   4942 E2 47 49      [10]  646 	jp	PO, 00137$
   4945 EE 80         [ 7]  647 	xor	a, #0x80
   4947                     648 00137$:
   4947 F2 87 49      [10]  649 	jp	P, 00114$
   494A AF            [ 4]  650 	xor	a, a
   494B 77            [ 7]  651 	ld	(hl), a
   494C 23            [ 6]  652 	inc	hl
   494D 77            [ 7]  653 	ld	(hl), a
   494E 18 37         [12]  654 	jr	00114$
   4950                     655 00112$:
                            656 ;src/entities/entities.c:248: if      ( *v < -maxvel ) *v = -maxvel;  // Crop to max negative velocity
   4950 AF            [ 4]  657 	xor	a, a
   4951 DD 96 06      [19]  658 	sub	a, 6 (ix)
   4954 4F            [ 4]  659 	ld	c, a
   4955 3E 00         [ 7]  660 	ld	a, #0x00
   4957 DD 9E 07      [19]  661 	sbc	a, 7 (ix)
   495A 47            [ 4]  662 	ld	b, a
   495B 7B            [ 4]  663 	ld	a, e
   495C 91            [ 4]  664 	sub	a, c
   495D 7A            [ 4]  665 	ld	a, d
   495E 98            [ 4]  666 	sbc	a, b
   495F E2 64 49      [10]  667 	jp	PO, 00138$
   4962 EE 80         [ 7]  668 	xor	a, #0x80
   4964                     669 00138$:
   4964 F2 6C 49      [10]  670 	jp	P, 00109$
   4967 71            [ 7]  671 	ld	(hl), c
   4968 23            [ 6]  672 	inc	hl
   4969 70            [ 7]  673 	ld	(hl), b
   496A 18 1B         [12]  674 	jr	00114$
   496C                     675 00109$:
                            676 ;src/entities/entities.c:249: else if ( *v > -minvel ) *v = 0;        // Round to mix negative velocity
   496C AF            [ 4]  677 	xor	a, a
   496D DD 96 08      [19]  678 	sub	a, 8 (ix)
   4970 4F            [ 4]  679 	ld	c, a
   4971 3E 00         [ 7]  680 	ld	a, #0x00
   4973 DD 9E 09      [19]  681 	sbc	a, 9 (ix)
   4976 47            [ 4]  682 	ld	b, a
   4977 79            [ 4]  683 	ld	a, c
   4978 93            [ 4]  684 	sub	a, e
   4979 78            [ 4]  685 	ld	a, b
   497A 9A            [ 4]  686 	sbc	a, d
   497B E2 80 49      [10]  687 	jp	PO, 00139$
   497E EE 80         [ 7]  688 	xor	a, #0x80
   4980                     689 00139$:
   4980 F2 87 49      [10]  690 	jp	P, 00114$
   4983 AF            [ 4]  691 	xor	a, a
   4984 77            [ 7]  692 	ld	(hl), a
   4985 23            [ 6]  693 	inc	hl
   4986 77            [ 7]  694 	ld	(hl), a
   4987                     695 00114$:
   4987 DD E1         [14]  696 	pop	ix
   4989 C9            [10]  697 	ret
                            698 ;src/entities/entities.c:261: u8 moveBlock(u8 b_idx) {
                            699 ;	---------------------------------
                            700 ; Function moveBlock
                            701 ; ---------------------------------
   498A                     702 _moveBlock::
   498A DD E5         [15]  703 	push	ix
   498C DD 21 00 00   [14]  704 	ld	ix,#0
   4990 DD 39         [15]  705 	add	ix,sp
   4992 21 F4 FF      [10]  706 	ld	hl, #-12
   4995 39            [11]  707 	add	hl, sp
   4996 F9            [ 6]  708 	ld	sp, hl
                            709 ;src/entities/entities.c:262: TEntity *e = &g_blocks[b_idx]; // Get next block entity
   4997 01 A1 73      [10]  710 	ld	bc, #_g_blocks+0
   499A DD 5E 04      [19]  711 	ld	e,4 (ix)
   499D 16 00         [ 7]  712 	ld	d,#0x00
   499F 6B            [ 4]  713 	ld	l, e
   49A0 62            [ 4]  714 	ld	h, d
   49A1 29            [11]  715 	add	hl, hl
   49A2 19            [11]  716 	add	hl, de
   49A3 29            [11]  717 	add	hl, hl
   49A4 19            [11]  718 	add	hl, de
   49A5 29            [11]  719 	add	hl, hl
   49A6 19            [11]  720 	add	hl, de
   49A7 29            [11]  721 	add	hl, hl
   49A8 19            [11]  722 	add	hl, de
   49A9 09            [11]  723 	add	hl,bc
   49AA 4D            [ 4]  724 	ld	c, l
   49AB 44            [ 4]  725 	ld	b, h
                            726 ;src/entities/entities.c:266: e->phys.y += G_scrollVel;      // All blocks use this same velocity for Y axis
   49AC 21 0F 00      [10]  727 	ld	hl, #0x000f
   49AF 09            [11]  728 	add	hl,bc
   49B0 DD 75 FE      [19]  729 	ld	-2 (ix), l
   49B3 DD 74 FF      [19]  730 	ld	-1 (ix), h
   49B6 21 11 00      [10]  731 	ld	hl, #0x0011
   49B9 09            [11]  732 	add	hl,bc
   49BA DD 75 FC      [19]  733 	ld	-4 (ix), l
   49BD DD 74 FD      [19]  734 	ld	-3 (ix), h
   49C0 5E            [ 7]  735 	ld	e, (hl)
   49C1 23            [ 6]  736 	inc	hl
   49C2 56            [ 7]  737 	ld	d, (hl)
   49C3 2A 9C 73      [16]  738 	ld	hl, (_G_scrollVel)
   49C6 19            [11]  739 	add	hl,de
   49C7 EB            [ 4]  740 	ex	de,hl
   49C8 DD 6E FC      [19]  741 	ld	l,-4 (ix)
   49CB DD 66 FD      [19]  742 	ld	h,-3 (ix)
   49CE 73            [ 7]  743 	ld	(hl), e
   49CF 23            [ 6]  744 	inc	hl
   49D0 72            [ 7]  745 	ld	(hl), d
                            746 ;src/entities/entities.c:267: e->y       = e->ny;
   49D1 FD 21 0A 00   [14]  747 	ld	iy, #0x000a
   49D5 FD 09         [15]  748 	add	iy, bc
   49D7 21 0C 00      [10]  749 	ld	hl, #0x000c
   49DA 09            [11]  750 	add	hl,bc
   49DB DD 75 FC      [19]  751 	ld	-4 (ix), l
   49DE DD 74 FD      [19]  752 	ld	-3 (ix), h
   49E1 7E            [ 7]  753 	ld	a, (hl)
   49E2 DD 77 F4      [19]  754 	ld	-12 (ix), a
   49E5 FD 77 00      [19]  755 	ld	0 (iy), a
                            756 ;src/entities/entities.c:268: e->ny      = e->phys.y / SCALE;
   49E8 DD 6E FC      [19]  757 	ld	l,-4 (ix)
   49EB DD 66 FD      [19]  758 	ld	h,-3 (ix)
   49EE 72            [ 7]  759 	ld	(hl), d
                            760 ;src/entities/entities.c:271: if (e->ny != e->y) {    
   49EF DD 6E FC      [19]  761 	ld	l,-4 (ix)
   49F2 DD 66 FD      [19]  762 	ld	h,-3 (ix)
   49F5 5E            [ 7]  763 	ld	e, (hl)
                            764 ;src/entities/entities.c:279: e->draw = 1;
   49F6 21 1B 00      [10]  765 	ld	hl, #0x001b
   49F9 09            [11]  766 	add	hl,bc
   49FA DD 75 F9      [19]  767 	ld	-7 (ix), l
   49FD DD 74 FA      [19]  768 	ld	-6 (ix), h
                            769 ;src/entities/entities.c:271: if (e->ny != e->y) {    
   4A00 DD 7E F4      [19]  770 	ld	a, -12 (ix)
   4A03 92            [ 4]  771 	sub	a, d
   4A04 28 1C         [12]  772 	jr	Z,00104$
                            773 ;src/entities/entities.c:274: if (e->ny > G_maxY) {
   4A06 3A 44 47      [13]  774 	ld	a,(#_G_maxY + 0)
   4A09 93            [ 4]  775 	sub	a, e
   4A0A 30 0E         [12]  776 	jr	NC,00102$
                            777 ;src/entities/entities.c:275: destroyBlock(b_idx);
   4A0C DD 7E 04      [19]  778 	ld	a, 4 (ix)
   4A0F F5            [11]  779 	push	af
   4A10 33            [ 6]  780 	inc	sp
   4A11 CD 2D 5B      [17]  781 	call	_destroyBlock
   4A14 33            [ 6]  782 	inc	sp
                            783 ;src/entities/entities.c:276: return 1;         // Return informing that the block has been destroyed!
   4A15 2E 01         [ 7]  784 	ld	l, #0x01
   4A17 C3 67 4B      [10]  785 	jp	00116$
   4A1A                     786 00102$:
                            787 ;src/entities/entities.c:279: e->draw = 1;
   4A1A DD 6E F9      [19]  788 	ld	l,-7 (ix)
   4A1D DD 66 FA      [19]  789 	ld	h,-6 (ix)
   4A20 36 01         [10]  790 	ld	(hl), #0x01
   4A22                     791 00104$:
                            792 ;src/entities/entities.c:283: if (e->phys.vx) {
   4A22 DD 7E FE      [19]  793 	ld	a, -2 (ix)
   4A25 C6 04         [ 7]  794 	add	a, #0x04
   4A27 DD 77 F5      [19]  795 	ld	-11 (ix), a
   4A2A DD 7E FF      [19]  796 	ld	a, -1 (ix)
   4A2D CE 00         [ 7]  797 	adc	a, #0x00
   4A2F DD 77 F6      [19]  798 	ld	-10 (ix), a
   4A32 DD 6E F5      [19]  799 	ld	l,-11 (ix)
   4A35 DD 66 F6      [19]  800 	ld	h,-10 (ix)
   4A38 5E            [ 7]  801 	ld	e, (hl)
   4A39 23            [ 6]  802 	inc	hl
   4A3A 56            [ 7]  803 	ld	d, (hl)
                            804 ;src/entities/entities.c:284: e->x       = e->nx;
   4A3B 21 0B 00      [10]  805 	ld	hl, #0x000b
   4A3E 09            [11]  806 	add	hl,bc
   4A3F DD 75 F7      [19]  807 	ld	-9 (ix), l
   4A42 DD 74 F8      [19]  808 	ld	-8 (ix), h
                            809 ;src/entities/entities.c:283: if (e->phys.vx) {
   4A45 7A            [ 4]  810 	ld	a, d
   4A46 B3            [ 4]  811 	or	a,e
   4A47 CA 1C 4B      [10]  812 	jp	Z, 00113$
                            813 ;src/entities/entities.c:284: e->x       = e->nx;
   4A4A 21 09 00      [10]  814 	ld	hl, #0x0009
   4A4D 09            [11]  815 	add	hl,bc
   4A4E EB            [ 4]  816 	ex	de,hl
   4A4F DD 6E F7      [19]  817 	ld	l,-9 (ix)
   4A52 DD 66 F8      [19]  818 	ld	h,-8 (ix)
   4A55 7E            [ 7]  819 	ld	a, (hl)
   4A56 DD 77 F4      [19]  820 	ld	-12 (ix), a
   4A59 12            [ 7]  821 	ld	(de),a
                            822 ;src/entities/entities.c:285: e->phys.x += e->phys.vx;
   4A5A DD 6E FE      [19]  823 	ld	l,-2 (ix)
   4A5D DD 66 FF      [19]  824 	ld	h,-1 (ix)
   4A60 5E            [ 7]  825 	ld	e, (hl)
   4A61 23            [ 6]  826 	inc	hl
   4A62 56            [ 7]  827 	ld	d, (hl)
   4A63 DD 6E F5      [19]  828 	ld	l,-11 (ix)
   4A66 DD 66 F6      [19]  829 	ld	h,-10 (ix)
   4A69 7E            [ 7]  830 	ld	a, (hl)
   4A6A 23            [ 6]  831 	inc	hl
   4A6B 66            [ 7]  832 	ld	h, (hl)
   4A6C 6F            [ 4]  833 	ld	l, a
   4A6D 19            [11]  834 	add	hl,de
   4A6E EB            [ 4]  835 	ex	de,hl
   4A6F DD 6E FE      [19]  836 	ld	l,-2 (ix)
   4A72 DD 66 FF      [19]  837 	ld	h,-1 (ix)
   4A75 73            [ 7]  838 	ld	(hl), e
   4A76 23            [ 6]  839 	inc	hl
   4A77 72            [ 7]  840 	ld	(hl), d
                            841 ;src/entities/entities.c:286: e->nx      = e->phys.x / SCALE;
   4A78 DD 6E F7      [19]  842 	ld	l,-9 (ix)
   4A7B DD 66 F8      [19]  843 	ld	h,-8 (ix)
   4A7E 72            [ 7]  844 	ld	(hl), d
                            845 ;src/entities/entities.c:289: if (e->x != e->nx) {
   4A7F DD 6E F7      [19]  846 	ld	l,-9 (ix)
   4A82 DD 66 F8      [19]  847 	ld	h,-8 (ix)
   4A85 5E            [ 7]  848 	ld	e, (hl)
   4A86 DD 7E F4      [19]  849 	ld	a, -12 (ix)
   4A89 92            [ 4]  850 	sub	a, d
   4A8A CA 1C 4B      [10]  851 	jp	Z,00113$
                            852 ;src/entities/entities.c:291: if (e->nx < G_minX) {
   4A8D 21 41 47      [10]  853 	ld	hl,#_G_minX + 0
   4A90 56            [ 7]  854 	ld	d, (hl)
   4A91 7B            [ 4]  855 	ld	a, e
   4A92 92            [ 4]  856 	sub	a, d
   4A93 30 2E         [12]  857 	jr	NC,00108$
                            858 ;src/entities/entities.c:293: e->nx      = G_minX + 1; 
   4A95 14            [ 4]  859 	inc	d
   4A96 DD 6E F7      [19]  860 	ld	l,-9 (ix)
   4A99 DD 66 F8      [19]  861 	ld	h,-8 (ix)
   4A9C 72            [ 7]  862 	ld	(hl), d
                            863 ;src/entities/entities.c:294: e->phys.x  = e->nx * SCALE; 
   4A9D 1E 00         [ 7]  864 	ld	e, #0x00
   4A9F DD 6E FE      [19]  865 	ld	l,-2 (ix)
   4AA2 DD 66 FF      [19]  866 	ld	h,-1 (ix)
   4AA5 73            [ 7]  867 	ld	(hl), e
   4AA6 23            [ 6]  868 	inc	hl
   4AA7 72            [ 7]  869 	ld	(hl), d
                            870 ;src/entities/entities.c:295: e->phys.vx = -e->phys.vx;
   4AA8 DD 6E F5      [19]  871 	ld	l,-11 (ix)
   4AAB DD 66 F6      [19]  872 	ld	h,-10 (ix)
   4AAE 5E            [ 7]  873 	ld	e, (hl)
   4AAF 23            [ 6]  874 	inc	hl
   4AB0 56            [ 7]  875 	ld	d, (hl)
   4AB1 AF            [ 4]  876 	xor	a, a
   4AB2 93            [ 4]  877 	sub	a, e
   4AB3 5F            [ 4]  878 	ld	e, a
   4AB4 3E 00         [ 7]  879 	ld	a, #0x00
   4AB6 9A            [ 4]  880 	sbc	a, d
   4AB7 57            [ 4]  881 	ld	d, a
   4AB8 DD 6E F5      [19]  882 	ld	l,-11 (ix)
   4ABB DD 66 F6      [19]  883 	ld	h,-10 (ix)
   4ABE 73            [ 7]  884 	ld	(hl), e
   4ABF 23            [ 6]  885 	inc	hl
   4AC0 72            [ 7]  886 	ld	(hl), d
   4AC1 18 51         [12]  887 	jr	00109$
   4AC3                     888 00108$:
                            889 ;src/entities/entities.c:296: } else if ( e->nx + e->graph.block.w >= G_maxX ) {
   4AC3 16 00         [ 7]  890 	ld	d, #0x00
   4AC5 0A            [ 7]  891 	ld	a, (bc)
   4AC6 DD 77 F4      [19]  892 	ld	-12 (ix), a
   4AC9 6F            [ 4]  893 	ld	l, a
   4ACA 26 00         [ 7]  894 	ld	h, #0x00
   4ACC 19            [11]  895 	add	hl, de
   4ACD 3A 42 47      [13]  896 	ld	a,(#_G_maxX + 0)
   4AD0 DD 77 FB      [19]  897 	ld	-5 (ix), a
   4AD3 5F            [ 4]  898 	ld	e, a
   4AD4 16 00         [ 7]  899 	ld	d, #0x00
   4AD6 7D            [ 4]  900 	ld	a, l
   4AD7 93            [ 4]  901 	sub	a, e
   4AD8 7C            [ 4]  902 	ld	a, h
   4AD9 9A            [ 4]  903 	sbc	a, d
   4ADA E2 DF 4A      [10]  904 	jp	PO, 00148$
   4ADD EE 80         [ 7]  905 	xor	a, #0x80
   4ADF                     906 00148$:
   4ADF FA 14 4B      [10]  907 	jp	M, 00109$
                            908 ;src/entities/entities.c:298: e->nx      = G_maxX - e->graph.block.w;
   4AE2 DD 7E FB      [19]  909 	ld	a, -5 (ix)
   4AE5 DD 96 F4      [19]  910 	sub	a, -12 (ix)
   4AE8 5F            [ 4]  911 	ld	e, a
   4AE9 DD 6E F7      [19]  912 	ld	l,-9 (ix)
   4AEC DD 66 F8      [19]  913 	ld	h,-8 (ix)
   4AEF 73            [ 7]  914 	ld	(hl), e
                            915 ;src/entities/entities.c:299: e->phys.x  = e->nx * SCALE;  
   4AF0 16 00         [ 7]  916 	ld	d, #0x00
   4AF2 DD 6E FE      [19]  917 	ld	l,-2 (ix)
   4AF5 DD 66 FF      [19]  918 	ld	h,-1 (ix)
   4AF8 72            [ 7]  919 	ld	(hl), d
   4AF9 23            [ 6]  920 	inc	hl
   4AFA 73            [ 7]  921 	ld	(hl), e
                            922 ;src/entities/entities.c:300: e->phys.vx = -e->phys.vx;
   4AFB DD 6E F5      [19]  923 	ld	l,-11 (ix)
   4AFE DD 66 F6      [19]  924 	ld	h,-10 (ix)
   4B01 5E            [ 7]  925 	ld	e, (hl)
   4B02 23            [ 6]  926 	inc	hl
   4B03 56            [ 7]  927 	ld	d, (hl)
   4B04 AF            [ 4]  928 	xor	a, a
   4B05 93            [ 4]  929 	sub	a, e
   4B06 5F            [ 4]  930 	ld	e, a
   4B07 3E 00         [ 7]  931 	ld	a, #0x00
   4B09 9A            [ 4]  932 	sbc	a, d
   4B0A 57            [ 4]  933 	ld	d, a
   4B0B DD 6E F5      [19]  934 	ld	l,-11 (ix)
   4B0E DD 66 F6      [19]  935 	ld	h,-10 (ix)
   4B11 73            [ 7]  936 	ld	(hl), e
   4B12 23            [ 6]  937 	inc	hl
   4B13 72            [ 7]  938 	ld	(hl), d
   4B14                     939 00109$:
                            940 ;src/entities/entities.c:302: e->draw = 1; // Set for redraw
   4B14 DD 6E F9      [19]  941 	ld	l,-7 (ix)
   4B17 DD 66 FA      [19]  942 	ld	h,-6 (ix)
   4B1A 36 01         [10]  943 	ld	(hl), #0x01
   4B1C                     944 00113$:
                            945 ;src/entities/entities.c:307: if (e->draw) {
   4B1C DD 6E F9      [19]  946 	ld	l,-7 (ix)
   4B1F DD 66 FA      [19]  947 	ld	h,-6 (ix)
   4B22 7E            [ 7]  948 	ld	a, (hl)
   4B23 B7            [ 4]  949 	or	a, a
   4B24 28 3F         [12]  950 	jr	Z,00115$
                            951 ;src/entities/entities.c:308: e->pscreen  = e->npscreen;
   4B26 21 05 00      [10]  952 	ld	hl, #0x0005
   4B29 09            [11]  953 	add	hl,bc
   4B2A EB            [ 4]  954 	ex	de,hl
   4B2B 21 07 00      [10]  955 	ld	hl, #0x0007
   4B2E 09            [11]  956 	add	hl,bc
   4B2F 4D            [ 4]  957 	ld	c, l
   4B30 44            [ 4]  958 	ld	b, h
   4B31 0A            [ 7]  959 	ld	a, (bc)
   4B32 DD 77 F5      [19]  960 	ld	-11 (ix), a
   4B35 03            [ 6]  961 	inc	bc
   4B36 0A            [ 7]  962 	ld	a, (bc)
   4B37 DD 77 F6      [19]  963 	ld	-10 (ix), a
   4B3A 0B            [ 6]  964 	dec	bc
   4B3B DD 7E F5      [19]  965 	ld	a, -11 (ix)
   4B3E 12            [ 7]  966 	ld	(de), a
   4B3F 13            [ 6]  967 	inc	de
   4B40 DD 7E F6      [19]  968 	ld	a, -10 (ix)
   4B43 12            [ 7]  969 	ld	(de), a
                            970 ;src/entities/entities.c:309: e->npscreen = cpct_getScreenPtr(CPCT_VMEM_START, e->nx, e->ny);
   4B44 DD 6E FC      [19]  971 	ld	l,-4 (ix)
   4B47 DD 66 FD      [19]  972 	ld	h,-3 (ix)
   4B4A 7E            [ 7]  973 	ld	a, (hl)
   4B4B DD 6E F7      [19]  974 	ld	l,-9 (ix)
   4B4E DD 66 F8      [19]  975 	ld	h,-8 (ix)
   4B51 56            [ 7]  976 	ld	d, (hl)
   4B52 C5            [11]  977 	push	bc
   4B53 F5            [11]  978 	push	af
   4B54 33            [ 6]  979 	inc	sp
   4B55 D5            [11]  980 	push	de
   4B56 33            [ 6]  981 	inc	sp
   4B57 21 00 C0      [10]  982 	ld	hl, #0xc000
   4B5A E5            [11]  983 	push	hl
   4B5B CD 9B 67      [17]  984 	call	_cpct_getScreenPtr
   4B5E EB            [ 4]  985 	ex	de,hl
   4B5F C1            [10]  986 	pop	bc
   4B60 7B            [ 4]  987 	ld	a, e
   4B61 02            [ 7]  988 	ld	(bc), a
   4B62 03            [ 6]  989 	inc	bc
   4B63 7A            [ 4]  990 	ld	a, d
   4B64 02            [ 7]  991 	ld	(bc), a
   4B65                     992 00115$:
                            993 ;src/entities/entities.c:313: return 0;
   4B65 2E 00         [ 7]  994 	ld	l, #0x00
   4B67                     995 00116$:
   4B67 DD F9         [10]  996 	ld	sp, ix
   4B69 DD E1         [14]  997 	pop	ix
   4B6B C9            [10]  998 	ret
                            999 ;src/entities/entities.c:320: void scrollWorld() {
                           1000 ;	---------------------------------
                           1001 ; Function scrollWorld
                           1002 ; ---------------------------------
   4B6C                    1003 _scrollWorld::
   4B6C DD E5         [15] 1004 	push	ix
   4B6E DD 21 00 00   [14] 1005 	ld	ix,#0
   4B72 DD 39         [15] 1006 	add	ix,sp
   4B74 21 F9 FF      [10] 1007 	ld	hl, #-7
   4B77 39            [11] 1008 	add	hl, sp
   4B78 F9            [ 6] 1009 	ld	sp, hl
                           1010 ;src/entities/entities.c:321: TEntity *ce = &(getCharacter()->entity);
   4B79 CD 6C 47      [17] 1011 	call	_getCharacter
   4B7C EB            [ 4] 1012 	ex	de,hl
                           1013 ;src/entities/entities.c:322: TPhysics *p = &ce->phys;
   4B7D 21 0F 00      [10] 1014 	ld	hl, #0x000f
   4B80 19            [11] 1015 	add	hl,de
   4B81 DD 75 FE      [19] 1016 	ld	-2 (ix), l
   4B84 DD 74 FF      [19] 1017 	ld	-1 (ix), h
   4B87 DD 7E FE      [19] 1018 	ld	a, -2 (ix)
   4B8A DD 77 FA      [19] 1019 	ld	-6 (ix), a
   4B8D DD 7E FF      [19] 1020 	ld	a, -1 (ix)
   4B90 DD 77 FB      [19] 1021 	ld	-5 (ix), a
                           1022 ;src/entities/entities.c:326: for(i=0; i < g_lastBlock; ++i) {
   4B93 06 00         [ 7] 1023 	ld	b, #0x00
   4B95                    1024 00117$:
                           1025 ;src/entities/entities.c:333: p->floor = 0;  
   4B95 DD 7E FA      [19] 1026 	ld	a, -6 (ix)
   4B98 C6 0A         [ 7] 1027 	add	a, #0x0a
   4B9A DD 77 FC      [19] 1028 	ld	-4 (ix), a
   4B9D DD 7E FB      [19] 1029 	ld	a, -5 (ix)
   4BA0 CE 00         [ 7] 1030 	adc	a, #0x00
   4BA2 DD 77 FD      [19] 1031 	ld	-3 (ix), a
                           1032 ;src/entities/entities.c:326: for(i=0; i < g_lastBlock; ++i) {
   4BA5 21 91 75      [10] 1033 	ld	hl, #_g_lastBlock
   4BA8 78            [ 4] 1034 	ld	a, b
   4BA9 96            [ 7] 1035 	sub	a, (hl)
   4BAA 30 1C         [12] 1036 	jr	NC,00103$
                           1037 ;src/entities/entities.c:328: if ( moveBlock(i) ) {
   4BAC C5            [11] 1038 	push	bc
   4BAD D5            [11] 1039 	push	de
   4BAE C5            [11] 1040 	push	bc
   4BAF 33            [ 6] 1041 	inc	sp
   4BB0 CD 8A 49      [17] 1042 	call	_moveBlock
   4BB3 33            [ 6] 1043 	inc	sp
   4BB4 D1            [10] 1044 	pop	de
   4BB5 C1            [10] 1045 	pop	bc
   4BB6 7D            [ 4] 1046 	ld	a, l
   4BB7 B7            [ 4] 1047 	or	a, a
   4BB8 28 0B         [12] 1048 	jr	Z,00118$
                           1049 ;src/entities/entities.c:333: p->floor = 0;  
   4BBA DD 6E FC      [19] 1050 	ld	l,-4 (ix)
   4BBD DD 66 FD      [19] 1051 	ld	h,-3 (ix)
   4BC0 AF            [ 4] 1052 	xor	a, a
   4BC1 77            [ 7] 1053 	ld	(hl), a
   4BC2 23            [ 6] 1054 	inc	hl
   4BC3 77            [ 7] 1055 	ld	(hl), a
                           1056 ;src/entities/entities.c:334: i--;
   4BC4 05            [ 4] 1057 	dec	b
   4BC5                    1058 00118$:
                           1059 ;src/entities/entities.c:326: for(i=0; i < g_lastBlock; ++i) {
   4BC5 04            [ 4] 1060 	inc	b
   4BC6 18 CD         [12] 1061 	jr	00117$
   4BC8                    1062 00103$:
                           1063 ;src/entities/entities.c:340: if (p->floor && p->floor->draw) {
   4BC8 DD 6E FC      [19] 1064 	ld	l,-4 (ix)
   4BCB DD 66 FD      [19] 1065 	ld	h,-3 (ix)
   4BCE 4E            [ 7] 1066 	ld	c, (hl)
   4BCF 23            [ 6] 1067 	inc	hl
   4BD0 46            [ 7] 1068 	ld	b, (hl)
   4BD1 78            [ 4] 1069 	ld	a, b
   4BD2 B1            [ 4] 1070 	or	a,c
   4BD3 28 76         [12] 1071 	jr	Z,00105$
   4BD5 C5            [11] 1072 	push	bc
   4BD6 FD E1         [14] 1073 	pop	iy
   4BD8 FD 7E 1B      [19] 1074 	ld	a, 27 (iy)
   4BDB B7            [ 4] 1075 	or	a, a
   4BDC 28 6D         [12] 1076 	jr	Z,00105$
                           1077 ;src/entities/entities.c:343: u8 height = anim->frames[anim->frame_id]->height;
   4BDE 1A            [ 7] 1078 	ld	a, (de)
   4BDF DD 77 FC      [19] 1079 	ld	-4 (ix), a
   4BE2 13            [ 6] 1080 	inc	de
   4BE3 1A            [ 7] 1081 	ld	a, (de)
   4BE4 DD 77 FD      [19] 1082 	ld	-3 (ix), a
   4BE7 1B            [ 6] 1083 	dec	de
   4BE8 6B            [ 4] 1084 	ld	l, e
   4BE9 62            [ 4] 1085 	ld	h, d
   4BEA 23            [ 6] 1086 	inc	hl
   4BEB 23            [ 6] 1087 	inc	hl
   4BEC 6E            [ 7] 1088 	ld	l, (hl)
   4BED 26 00         [ 7] 1089 	ld	h, #0x00
   4BEF 29            [11] 1090 	add	hl, hl
   4BF0 7D            [ 4] 1091 	ld	a, l
   4BF1 DD 86 FC      [19] 1092 	add	a, -4 (ix)
   4BF4 6F            [ 4] 1093 	ld	l, a
   4BF5 7C            [ 4] 1094 	ld	a, h
   4BF6 DD 8E FD      [19] 1095 	adc	a, -3 (ix)
   4BF9 67            [ 4] 1096 	ld	h, a
   4BFA 7E            [ 7] 1097 	ld	a, (hl)
   4BFB 23            [ 6] 1098 	inc	hl
   4BFC 66            [ 7] 1099 	ld	h, (hl)
   4BFD 6F            [ 4] 1100 	ld	l, a
   4BFE 23            [ 6] 1101 	inc	hl
   4BFF 23            [ 6] 1102 	inc	hl
   4C00 23            [ 6] 1103 	inc	hl
   4C01 7E            [ 7] 1104 	ld	a, (hl)
   4C02 DD 77 F9      [19] 1105 	ld	-7 (ix), a
                           1106 ;src/entities/entities.c:346: ce->phys.y  = (p->floor->ny - height) * SCALE;
   4C05 DD 7E FE      [19] 1107 	ld	a, -2 (ix)
   4C08 C6 02         [ 7] 1108 	add	a, #0x02
   4C0A DD 77 FC      [19] 1109 	ld	-4 (ix), a
   4C0D DD 7E FF      [19] 1110 	ld	a, -1 (ix)
   4C10 CE 00         [ 7] 1111 	adc	a, #0x00
   4C12 DD 77 FD      [19] 1112 	ld	-3 (ix), a
   4C15 C5            [11] 1113 	push	bc
   4C16 FD E1         [14] 1114 	pop	iy
   4C18 FD 6E 0C      [19] 1115 	ld	l, 12 (iy)
   4C1B 26 00         [ 7] 1116 	ld	h, #0x00
   4C1D DD 4E F9      [19] 1117 	ld	c, -7 (ix)
   4C20 06 00         [ 7] 1118 	ld	b, #0x00
   4C22 BF            [ 4] 1119 	cp	a, a
   4C23 ED 42         [15] 1120 	sbc	hl, bc
   4C25 45            [ 4] 1121 	ld	b, l
   4C26 0E 00         [ 7] 1122 	ld	c, #0x00
   4C28 DD 6E FC      [19] 1123 	ld	l,-4 (ix)
   4C2B DD 66 FD      [19] 1124 	ld	h,-3 (ix)
   4C2E 71            [ 7] 1125 	ld	(hl), c
   4C2F 23            [ 6] 1126 	inc	hl
   4C30 70            [ 7] 1127 	ld	(hl), b
                           1128 ;src/entities/entities.c:347: ce->phys.vy = G_minVel - 1;
   4C31 DD 7E FE      [19] 1129 	ld	a, -2 (ix)
   4C34 C6 06         [ 7] 1130 	add	a, #0x06
   4C36 6F            [ 4] 1131 	ld	l, a
   4C37 DD 7E FF      [19] 1132 	ld	a, -1 (ix)
   4C3A CE 00         [ 7] 1133 	adc	a, #0x00
   4C3C 67            [ 4] 1134 	ld	h, a
   4C3D ED 4B 39 47   [20] 1135 	ld	bc, (_G_minVel)
   4C41 0B            [ 6] 1136 	dec	bc
   4C42 71            [ 7] 1137 	ld	(hl), c
   4C43 23            [ 6] 1138 	inc	hl
   4C44 70            [ 7] 1139 	ld	(hl), b
                           1140 ;src/entities/entities.c:348: ce->draw    = 1;
   4C45 21 1B 00      [10] 1141 	ld	hl, #0x001b
   4C48 19            [11] 1142 	add	hl, de
   4C49 36 01         [10] 1143 	ld	(hl), #0x01
   4C4B                    1144 00105$:
                           1145 ;src/entities/entities.c:353: if ( g_blocks[0].draw && randomCreateNewBlock(G_minY-3, 3, ce->nx) ) {
   4C4B 3A BC 73      [13] 1146 	ld	a,(#(_g_blocks + 0x001b) + 0)
   4C4E B7            [ 4] 1147 	or	a, a
   4C4F 28 64         [12] 1148 	jr	Z,00119$
   4C51 EB            [ 4] 1149 	ex	de,hl
   4C52 11 0B 00      [10] 1150 	ld	de, #0x000b
   4C55 19            [11] 1151 	add	hl, de
   4C56 4E            [ 7] 1152 	ld	c, (hl)
   4C57 3A 43 47      [13] 1153 	ld	a,(#_G_minY + 0)
   4C5A C6 FD         [ 7] 1154 	add	a, #0xfd
   4C5C 57            [ 4] 1155 	ld	d, a
   4C5D 41            [ 4] 1156 	ld	b, c
   4C5E 0E 03         [ 7] 1157 	ld	c,#0x03
   4C60 C5            [11] 1158 	push	bc
   4C61 D5            [11] 1159 	push	de
   4C62 33            [ 6] 1160 	inc	sp
   4C63 CD 9C 5B      [17] 1161 	call	_randomCreateNewBlock
   4C66 F1            [10] 1162 	pop	af
   4C67 33            [ 6] 1163 	inc	sp
   4C68 7D            [ 4] 1164 	ld	a, l
   4C69 B7            [ 4] 1165 	or	a, a
   4C6A 28 49         [12] 1166 	jr	Z,00119$
                           1167 ;src/entities/entities.c:356: if ( !(++G_score & 0x0F) ) {
   4C6C FD 21 9F 73   [14] 1168 	ld	iy, #_G_score
   4C70 FD 34 00      [23] 1169 	inc	0 (iy)
   4C73 20 03         [12] 1170 	jr	NZ,00161$
   4C75 FD 34 01      [23] 1171 	inc	1 (iy)
   4C78                    1172 00161$:
   4C78 FD 7E 00      [19] 1173 	ld	a, 0 (iy)
   4C7B E6 0F         [ 7] 1174 	and	a, #0x0f
   4C7D 20 36         [12] 1175 	jr	NZ,00119$
                           1176 ;src/entities/entities.c:358: if ( ++G_platfColour > 15) 
   4C7F FD 21 9E 73   [14] 1177 	ld	iy, #_G_platfColour
   4C83 FD 34 00      [23] 1178 	inc	0 (iy)
   4C86 3E 0F         [ 7] 1179 	ld	a, #0x0f
   4C88 FD 96 00      [19] 1180 	sub	a, 0 (iy)
   4C8B 30 04         [12] 1181 	jr	NC,00108$
                           1182 ;src/entities/entities.c:359: G_platfColour = 1;
   4C8D FD 36 00 01   [19] 1183 	ld	0 (iy), #0x01
   4C91                    1184 00108$:
                           1185 ;src/entities/entities.c:362: if (G_scrollVel < G_maxScrollVel)
   4C91 ED 4B 3D 47   [20] 1186 	ld	bc, (_G_maxScrollVel)
   4C95 FD 21 9C 73   [14] 1187 	ld	iy, #_G_scrollVel
   4C99 FD 7E 00      [19] 1188 	ld	a, 0 (iy)
   4C9C 91            [ 4] 1189 	sub	a, c
   4C9D FD 7E 01      [19] 1190 	ld	a, 1 (iy)
   4CA0 98            [ 4] 1191 	sbc	a, b
   4CA1 E2 A6 4C      [10] 1192 	jp	PO, 00164$
   4CA4 EE 80         [ 7] 1193 	xor	a, #0x80
   4CA6                    1194 00164$:
   4CA6 F2 B5 4C      [10] 1195 	jp	P, 00119$
                           1196 ;src/entities/entities.c:363: ++G_scrollVel;
   4CA9 FD 21 9C 73   [14] 1197 	ld	iy, #_G_scrollVel
   4CAD FD 34 00      [23] 1198 	inc	0 (iy)
   4CB0 20 03         [12] 1199 	jr	NZ,00165$
   4CB2 FD 34 01      [23] 1200 	inc	1 (iy)
   4CB5                    1201 00165$:
   4CB5                    1202 00119$:
   4CB5 DD F9         [10] 1203 	ld	sp, ix
   4CB7 DD E1         [14] 1204 	pop	ix
   4CB9 C9            [10] 1205 	ret
                           1206 ;src/entities/entities.c:373: void updateCharacterPhysics(TCharacter *c) {
                           1207 ;	---------------------------------
                           1208 ; Function updateCharacterPhysics
                           1209 ; ---------------------------------
   4CBA                    1210 _updateCharacterPhysics::
   4CBA DD E5         [15] 1211 	push	ix
   4CBC DD 21 00 00   [14] 1212 	ld	ix,#0
   4CC0 DD 39         [15] 1213 	add	ix,sp
   4CC2 21 F5 FF      [10] 1214 	ld	hl, #-11
   4CC5 39            [11] 1215 	add	hl, sp
   4CC6 F9            [ 6] 1216 	ld	sp, hl
                           1217 ;src/entities/entities.c:374: TEntity  *e = &c->entity;
   4CC7 DD 5E 04      [19] 1218 	ld	e,4 (ix)
   4CCA DD 56 05      [19] 1219 	ld	d,5 (ix)
   4CCD 4B            [ 4] 1220 	ld	c, e
   4CCE 42            [ 4] 1221 	ld	b, d
                           1222 ;src/entities/entities.c:375: TPhysics *p = &e->phys;
   4CCF 21 0F 00      [10] 1223 	ld	hl, #0x000f
   4CD2 09            [11] 1224 	add	hl,bc
   4CD3 E3            [19] 1225 	ex	(sp), hl
                           1226 ;src/entities/entities.c:379: if ( !isOverFloor(e) ) {
   4CD4 C5            [11] 1227 	push	bc
   4CD5 D5            [11] 1228 	push	de
   4CD6 C5            [11] 1229 	push	bc
   4CD7 CD FC 56      [17] 1230 	call	_isOverFloor
   4CDA F1            [10] 1231 	pop	af
   4CDB DD 75 FF      [19] 1232 	ld	-1 (ix), l
   4CDE D1            [10] 1233 	pop	de
   4CDF C1            [10] 1234 	pop	bc
                           1235 ;src/entities/entities.c:381: if ( p->floor ) {
   4CE0 DD 7E F5      [19] 1236 	ld	a, -11 (ix)
   4CE3 C6 0A         [ 7] 1237 	add	a, #0x0a
   4CE5 6F            [ 4] 1238 	ld	l, a
   4CE6 DD 7E F6      [19] 1239 	ld	a, -10 (ix)
   4CE9 CE 00         [ 7] 1240 	adc	a, #0x00
   4CEB 67            [ 4] 1241 	ld	h, a
                           1242 ;src/entities/entities.c:383: c->status    = es_jump;
   4CEC 7B            [ 4] 1243 	ld	a, e
   4CED C6 1F         [ 7] 1244 	add	a, #0x1f
   4CEF 5F            [ 4] 1245 	ld	e, a
   4CF0 7A            [ 4] 1246 	ld	a, d
   4CF1 CE 00         [ 7] 1247 	adc	a, #0x00
   4CF3 57            [ 4] 1248 	ld	d, a
                           1249 ;src/entities/entities.c:388: p->vy += G_gy;
   4CF4 DD 7E F5      [19] 1250 	ld	a, -11 (ix)
   4CF7 C6 06         [ 7] 1251 	add	a, #0x06
   4CF9 DD 77 FD      [19] 1252 	ld	-3 (ix), a
   4CFC DD 7E F6      [19] 1253 	ld	a, -10 (ix)
   4CFF CE 00         [ 7] 1254 	adc	a, #0x00
   4D01 DD 77 FE      [19] 1255 	ld	-2 (ix), a
                           1256 ;src/entities/entities.c:392: p->vx += 1;                   // p->vx must be != 0 to enable horizontal velocity processing
   4D04 DD 7E F5      [19] 1257 	ld	a, -11 (ix)
   4D07 C6 04         [ 7] 1258 	add	a, #0x04
   4D09 DD 77 FB      [19] 1259 	ld	-5 (ix), a
   4D0C DD 7E F6      [19] 1260 	ld	a, -10 (ix)
   4D0F CE 00         [ 7] 1261 	adc	a, #0x00
   4D11 DD 77 FC      [19] 1262 	ld	-4 (ix), a
                           1263 ;src/entities/entities.c:381: if ( p->floor ) {
   4D14 E5            [11] 1264 	push	hl
   4D15 7E            [ 7] 1265 	ld	a, (hl)
   4D16 DD 77 F7      [19] 1266 	ld	-9 (ix), a
   4D19 23            [ 6] 1267 	inc	hl
   4D1A 7E            [ 7] 1268 	ld	a, (hl)
   4D1B DD 77 F8      [19] 1269 	ld	-8 (ix), a
   4D1E E1            [10] 1270 	pop	hl
                           1271 ;src/entities/entities.c:379: if ( !isOverFloor(e) ) {
   4D1F DD 7E FF      [19] 1272 	ld	a, -1 (ix)
   4D22 B7            [ 4] 1273 	or	a, a
   4D23 20 46         [12] 1274 	jr	NZ,00104$
                           1275 ;src/entities/entities.c:381: if ( p->floor ) {
   4D25 DD 7E F8      [19] 1276 	ld	a, -8 (ix)
   4D28 DD B6 F7      [19] 1277 	or	a,-9 (ix)
   4D2B 28 0D         [12] 1278 	jr	Z,00102$
                           1279 ;src/entities/entities.c:382: p->floor     = 0; 
   4D2D AF            [ 4] 1280 	xor	a, a
   4D2E 77            [ 7] 1281 	ld	(hl), a
   4D2F 23            [ 6] 1282 	inc	hl
   4D30 77            [ 7] 1283 	ld	(hl), a
                           1284 ;src/entities/entities.c:383: c->status    = es_jump;
   4D31 3E 02         [ 7] 1285 	ld	a, #0x02
   4D33 12            [ 7] 1286 	ld	(de), a
                           1287 ;src/entities/entities.c:384: anim->status = as_pause;
   4D34 21 04 00      [10] 1288 	ld	hl, #0x0004
   4D37 09            [11] 1289 	add	hl, bc
   4D38 36 03         [10] 1290 	ld	(hl), #0x03
   4D3A                    1291 00102$:
                           1292 ;src/entities/entities.c:388: p->vy += G_gy;
   4D3A DD 6E FD      [19] 1293 	ld	l,-3 (ix)
   4D3D DD 66 FE      [19] 1294 	ld	h,-2 (ix)
   4D40 7E            [ 7] 1295 	ld	a, (hl)
   4D41 DD 77 F9      [19] 1296 	ld	-7 (ix), a
   4D44 23            [ 6] 1297 	inc	hl
   4D45 7E            [ 7] 1298 	ld	a, (hl)
   4D46 DD 77 FA      [19] 1299 	ld	-6 (ix), a
   4D49 2A 31 47      [16] 1300 	ld	hl, (_G_gy)
   4D4C DD 7E F9      [19] 1301 	ld	a, -7 (ix)
   4D4F 85            [ 4] 1302 	add	a, l
   4D50 DD 77 F9      [19] 1303 	ld	-7 (ix), a
   4D53 DD 7E FA      [19] 1304 	ld	a, -6 (ix)
   4D56 8C            [ 4] 1305 	adc	a, h
   4D57 DD 77 FA      [19] 1306 	ld	-6 (ix), a
   4D5A DD 6E FD      [19] 1307 	ld	l,-3 (ix)
   4D5D DD 66 FE      [19] 1308 	ld	h,-2 (ix)
   4D60 DD 7E F9      [19] 1309 	ld	a, -7 (ix)
   4D63 77            [ 7] 1310 	ld	(hl), a
   4D64 23            [ 6] 1311 	inc	hl
   4D65 DD 7E FA      [19] 1312 	ld	a, -6 (ix)
   4D68 77            [ 7] 1313 	ld	(hl), a
   4D69 18 54         [12] 1314 	jr	00105$
   4D6B                    1315 00104$:
                           1316 ;src/entities/entities.c:391: p->x  += p->floor->phys.vx;   // Add floor inertia
   4D6B E1            [10] 1317 	pop	hl
   4D6C E5            [11] 1318 	push	hl
   4D6D 7E            [ 7] 1319 	ld	a, (hl)
   4D6E DD 77 F9      [19] 1320 	ld	-7 (ix), a
   4D71 23            [ 6] 1321 	inc	hl
   4D72 7E            [ 7] 1322 	ld	a, (hl)
   4D73 DD 77 FA      [19] 1323 	ld	-6 (ix), a
   4D76 DD 6E F7      [19] 1324 	ld	l,-9 (ix)
   4D79 DD 66 F8      [19] 1325 	ld	h,-8 (ix)
   4D7C C5            [11] 1326 	push	bc
   4D7D 01 13 00      [10] 1327 	ld	bc, #0x0013
   4D80 09            [11] 1328 	add	hl, bc
   4D81 C1            [10] 1329 	pop	bc
   4D82 7E            [ 7] 1330 	ld	a, (hl)
   4D83 23            [ 6] 1331 	inc	hl
   4D84 66            [ 7] 1332 	ld	h, (hl)
   4D85 6F            [ 4] 1333 	ld	l, a
   4D86 DD 7E F9      [19] 1334 	ld	a, -7 (ix)
   4D89 85            [ 4] 1335 	add	a, l
   4D8A DD 77 F9      [19] 1336 	ld	-7 (ix), a
   4D8D DD 7E FA      [19] 1337 	ld	a, -6 (ix)
   4D90 8C            [ 4] 1338 	adc	a, h
   4D91 DD 77 FA      [19] 1339 	ld	-6 (ix), a
   4D94 E1            [10] 1340 	pop	hl
   4D95 E5            [11] 1341 	push	hl
   4D96 DD 7E F9      [19] 1342 	ld	a, -7 (ix)
   4D99 77            [ 7] 1343 	ld	(hl), a
   4D9A 23            [ 6] 1344 	inc	hl
   4D9B DD 7E FA      [19] 1345 	ld	a, -6 (ix)
   4D9E 77            [ 7] 1346 	ld	(hl), a
                           1347 ;src/entities/entities.c:392: p->vx += 1;                   // p->vx must be != 0 to enable horizontal velocity processing
   4D9F DD 6E FB      [19] 1348 	ld	l,-5 (ix)
   4DA2 DD 66 FC      [19] 1349 	ld	h,-4 (ix)
   4DA5 7E            [ 7] 1350 	ld	a, (hl)
   4DA6 23            [ 6] 1351 	inc	hl
   4DA7 66            [ 7] 1352 	ld	h, (hl)
   4DA8 6F            [ 4] 1353 	ld	l, a
   4DA9 23            [ 6] 1354 	inc	hl
   4DAA DD 75 F9      [19] 1355 	ld	-7 (ix), l
   4DAD DD 74 FA      [19] 1356 	ld	-6 (ix), h
   4DB0 DD 6E FB      [19] 1357 	ld	l,-5 (ix)
   4DB3 DD 66 FC      [19] 1358 	ld	h,-4 (ix)
   4DB6 DD 7E F9      [19] 1359 	ld	a, -7 (ix)
   4DB9 77            [ 7] 1360 	ld	(hl), a
   4DBA 23            [ 6] 1361 	inc	hl
   4DBB DD 7E FA      [19] 1362 	ld	a, -6 (ix)
   4DBE 77            [ 7] 1363 	ld	(hl), a
   4DBF                    1364 00105$:
                           1365 ;src/entities/entities.c:396: p->vx += G_gx;
   4DBF DD 6E FB      [19] 1366 	ld	l,-5 (ix)
   4DC2 DD 66 FC      [19] 1367 	ld	h,-4 (ix)
   4DC5 7E            [ 7] 1368 	ld	a, (hl)
   4DC6 DD 77 F9      [19] 1369 	ld	-7 (ix), a
   4DC9 23            [ 6] 1370 	inc	hl
   4DCA 7E            [ 7] 1371 	ld	a, (hl)
   4DCB DD 77 FA      [19] 1372 	ld	-6 (ix), a
   4DCE 2A 33 47      [16] 1373 	ld	hl, (_G_gx)
   4DD1 DD 7E F9      [19] 1374 	ld	a, -7 (ix)
   4DD4 85            [ 4] 1375 	add	a, l
   4DD5 DD 77 F9      [19] 1376 	ld	-7 (ix), a
   4DD8 DD 7E FA      [19] 1377 	ld	a, -6 (ix)
   4DDB 8C            [ 4] 1378 	adc	a, h
   4DDC DD 77 FA      [19] 1379 	ld	-6 (ix), a
   4DDF DD 6E FB      [19] 1380 	ld	l,-5 (ix)
   4DE2 DD 66 FC      [19] 1381 	ld	h,-4 (ix)
   4DE5 DD 7E F9      [19] 1382 	ld	a, -7 (ix)
   4DE8 77            [ 7] 1383 	ld	(hl), a
   4DE9 23            [ 6] 1384 	inc	hl
   4DEA DD 7E FA      [19] 1385 	ld	a, -6 (ix)
   4DED 77            [ 7] 1386 	ld	(hl), a
                           1387 ;src/entities/entities.c:399: if ( p->vy ) {
   4DEE DD 6E FD      [19] 1388 	ld	l,-3 (ix)
   4DF1 DD 66 FE      [19] 1389 	ld	h,-2 (ix)
   4DF4 7E            [ 7] 1390 	ld	a, (hl)
   4DF5 23            [ 6] 1391 	inc	hl
   4DF6 66            [ 7] 1392 	ld	h, (hl)
   4DF7 B4            [ 4] 1393 	or	a,h
   4DF8 28 54         [12] 1394 	jr	Z,00107$
                           1395 ;src/entities/entities.c:401: cropVelocity(&p->vy, G_maxYVel, G_minVel);   
   4DFA 2A 39 47      [16] 1396 	ld	hl, (_G_minVel)
   4DFD FD 2A 35 47   [20] 1397 	ld	iy, (_G_maxYVel)
   4E01 C5            [11] 1398 	push	bc
   4E02 D5            [11] 1399 	push	de
   4E03 E5            [11] 1400 	push	hl
   4E04 FD E5         [15] 1401 	push	iy
   4E06 DD 6E FD      [19] 1402 	ld	l,-3 (ix)
   4E09 DD 66 FE      [19] 1403 	ld	h,-2 (ix)
   4E0C E5            [11] 1404 	push	hl
   4E0D CD 08 49      [17] 1405 	call	_cropVelocity
   4E10 21 06 00      [10] 1406 	ld	hl, #6
   4E13 39            [11] 1407 	add	hl, sp
   4E14 F9            [ 6] 1408 	ld	sp, hl
   4E15 D1            [10] 1409 	pop	de
   4E16 C1            [10] 1410 	pop	bc
                           1411 ;src/entities/entities.c:403: p->y  += p->vy;         // Then add it to position
   4E17 FD E1         [14] 1412 	pop	iy
   4E19 FD E5         [15] 1413 	push	iy
   4E1B FD 23         [10] 1414 	inc	iy
   4E1D FD 23         [10] 1415 	inc	iy
   4E1F FD 7E 00      [19] 1416 	ld	a, 0 (iy)
   4E22 DD 77 F9      [19] 1417 	ld	-7 (ix), a
   4E25 FD 7E 01      [19] 1418 	ld	a, 1 (iy)
   4E28 DD 77 FA      [19] 1419 	ld	-6 (ix), a
   4E2B DD 6E FD      [19] 1420 	ld	l,-3 (ix)
   4E2E DD 66 FE      [19] 1421 	ld	h,-2 (ix)
   4E31 7E            [ 7] 1422 	ld	a, (hl)
   4E32 23            [ 6] 1423 	inc	hl
   4E33 66            [ 7] 1424 	ld	h, (hl)
   4E34 6F            [ 4] 1425 	ld	l, a
   4E35 DD 7E F9      [19] 1426 	ld	a, -7 (ix)
   4E38 85            [ 4] 1427 	add	a, l
   4E39 6F            [ 4] 1428 	ld	l, a
   4E3A DD 7E FA      [19] 1429 	ld	a, -6 (ix)
   4E3D 8C            [ 4] 1430 	adc	a, h
   4E3E 67            [ 4] 1431 	ld	h, a
   4E3F FD 75 00      [19] 1432 	ld	0 (iy), l
   4E42 FD 74 01      [19] 1433 	ld	1 (iy), h
                           1434 ;src/entities/entities.c:404: e->ny  = p->y / SCALE;  // Calculate new screen position
   4E45 FD 21 0C 00   [14] 1435 	ld	iy, #0x000c
   4E49 FD 09         [15] 1436 	add	iy, bc
   4E4B FD 74 00      [19] 1437 	ld	0 (iy), h
   4E4E                    1438 00107$:
                           1439 ;src/entities/entities.c:408: if ( p->vx ) {
   4E4E DD 6E FB      [19] 1440 	ld	l,-5 (ix)
   4E51 DD 66 FC      [19] 1441 	ld	h,-4 (ix)
   4E54 7E            [ 7] 1442 	ld	a, (hl)
   4E55 23            [ 6] 1443 	inc	hl
   4E56 66            [ 7] 1444 	ld	h, (hl)
   4E57 B4            [ 4] 1445 	or	a,h
   4E58 CA ED 4E      [10] 1446 	jp	Z, 00113$
                           1447 ;src/entities/entities.c:410: cropVelocity(&p->vx, G_maxXVel, G_minVel);
   4E5B 2A 39 47      [16] 1448 	ld	hl, (_G_minVel)
   4E5E FD 2A 37 47   [20] 1449 	ld	iy, (_G_maxXVel)
   4E62 C5            [11] 1450 	push	bc
   4E63 D5            [11] 1451 	push	de
   4E64 E5            [11] 1452 	push	hl
   4E65 FD E5         [15] 1453 	push	iy
   4E67 DD 6E FB      [19] 1454 	ld	l,-5 (ix)
   4E6A DD 66 FC      [19] 1455 	ld	h,-4 (ix)
   4E6D E5            [11] 1456 	push	hl
   4E6E CD 08 49      [17] 1457 	call	_cropVelocity
   4E71 21 06 00      [10] 1458 	ld	hl, #6
   4E74 39            [11] 1459 	add	hl, sp
   4E75 F9            [ 6] 1460 	ld	sp, hl
   4E76 D1            [10] 1461 	pop	de
   4E77 C1            [10] 1462 	pop	bc
                           1463 ;src/entities/entities.c:412: p->x += p->vx;          // Then add it to position
   4E78 E1            [10] 1464 	pop	hl
   4E79 E5            [11] 1465 	push	hl
   4E7A 7E            [ 7] 1466 	ld	a, (hl)
   4E7B DD 77 F9      [19] 1467 	ld	-7 (ix), a
   4E7E 23            [ 6] 1468 	inc	hl
   4E7F 7E            [ 7] 1469 	ld	a, (hl)
   4E80 DD 77 FA      [19] 1470 	ld	-6 (ix), a
   4E83 DD 6E FB      [19] 1471 	ld	l,-5 (ix)
   4E86 DD 66 FC      [19] 1472 	ld	h,-4 (ix)
   4E89 7E            [ 7] 1473 	ld	a, (hl)
   4E8A 23            [ 6] 1474 	inc	hl
   4E8B 66            [ 7] 1475 	ld	h, (hl)
   4E8C 6F            [ 4] 1476 	ld	l, a
   4E8D DD 7E F9      [19] 1477 	ld	a, -7 (ix)
   4E90 85            [ 4] 1478 	add	a, l
   4E91 DD 77 F9      [19] 1479 	ld	-7 (ix), a
   4E94 DD 7E FA      [19] 1480 	ld	a, -6 (ix)
   4E97 8C            [ 4] 1481 	adc	a, h
   4E98 DD 77 FA      [19] 1482 	ld	-6 (ix), a
   4E9B E1            [10] 1483 	pop	hl
   4E9C E5            [11] 1484 	push	hl
   4E9D DD 7E F9      [19] 1485 	ld	a, -7 (ix)
   4EA0 77            [ 7] 1486 	ld	(hl), a
   4EA1 23            [ 6] 1487 	inc	hl
   4EA2 DD 7E FA      [19] 1488 	ld	a, -6 (ix)
   4EA5 77            [ 7] 1489 	ld	(hl), a
                           1490 ;src/entities/entities.c:413: e->nx = p->x / SCALE;   // And calculate new screen position
   4EA6 21 0B 00      [10] 1491 	ld	hl, #0x000b
   4EA9 09            [11] 1492 	add	hl, bc
   4EAA DD 4E FA      [19] 1493 	ld	c, -6 (ix)
   4EAD 71            [ 7] 1494 	ld	(hl), c
                           1495 ;src/entities/entities.c:416: if ( c->status == es_walk )
   4EAE 1A            [ 7] 1496 	ld	a, (de)
                           1497 ;src/entities/entities.c:396: p->vx += G_gx;
   4EAF DD 6E FB      [19] 1498 	ld	l,-5 (ix)
   4EB2 DD 66 FC      [19] 1499 	ld	h,-4 (ix)
   4EB5 4E            [ 7] 1500 	ld	c, (hl)
   4EB6 23            [ 6] 1501 	inc	hl
   4EB7 46            [ 7] 1502 	ld	b, (hl)
                           1503 ;src/entities/entities.c:416: if ( c->status == es_walk )
   4EB8 3D            [ 4] 1504 	dec	a
   4EB9 20 1A         [12] 1505 	jr	NZ,00109$
                           1506 ;src/entities/entities.c:417: p->vx /= G_floorFric;   // Friction on the floor
   4EBB 21 40 47      [10] 1507 	ld	hl,#_G_floorFric + 0
   4EBE 5E            [ 7] 1508 	ld	e, (hl)
   4EBF 16 00         [ 7] 1509 	ld	d, #0x00
   4EC1 D5            [11] 1510 	push	de
   4EC2 C5            [11] 1511 	push	bc
   4EC3 CD B1 67      [17] 1512 	call	__divsint
   4EC6 F1            [10] 1513 	pop	af
   4EC7 F1            [10] 1514 	pop	af
   4EC8 4D            [ 4] 1515 	ld	c, l
   4EC9 44            [ 4] 1516 	ld	b, h
   4ECA DD 6E FB      [19] 1517 	ld	l,-5 (ix)
   4ECD DD 66 FC      [19] 1518 	ld	h,-4 (ix)
   4ED0 71            [ 7] 1519 	ld	(hl), c
   4ED1 23            [ 6] 1520 	inc	hl
   4ED2 70            [ 7] 1521 	ld	(hl), b
   4ED3 18 18         [12] 1522 	jr	00113$
   4ED5                    1523 00109$:
                           1524 ;src/entities/entities.c:419: p->vx /= G_airFric;     // Friction on air
   4ED5 21 3F 47      [10] 1525 	ld	hl,#_G_airFric + 0
   4ED8 5E            [ 7] 1526 	ld	e, (hl)
   4ED9 16 00         [ 7] 1527 	ld	d, #0x00
   4EDB D5            [11] 1528 	push	de
   4EDC C5            [11] 1529 	push	bc
   4EDD CD B1 67      [17] 1530 	call	__divsint
   4EE0 F1            [10] 1531 	pop	af
   4EE1 F1            [10] 1532 	pop	af
   4EE2 4D            [ 4] 1533 	ld	c, l
   4EE3 44            [ 4] 1534 	ld	b, h
   4EE4 DD 6E FB      [19] 1535 	ld	l,-5 (ix)
   4EE7 DD 66 FC      [19] 1536 	ld	h,-4 (ix)
   4EEA 71            [ 7] 1537 	ld	(hl), c
   4EEB 23            [ 6] 1538 	inc	hl
   4EEC 70            [ 7] 1539 	ld	(hl), b
   4EED                    1540 00113$:
   4EED DD F9         [10] 1541 	ld	sp, ix
   4EEF DD E1         [14] 1542 	pop	ix
   4EF1 C9            [10] 1543 	ret
                           1544 ;src/entities/entities.c:429: u8 getNearestBlockID(u8 bid, u8 y) {
                           1545 ;	---------------------------------
                           1546 ; Function getNearestBlockID
                           1547 ; ---------------------------------
   4EF2                    1548 _getNearestBlockID::
   4EF2 DD E5         [15] 1549 	push	ix
   4EF4 DD 21 00 00   [14] 1550 	ld	ix,#0
   4EF8 DD 39         [15] 1551 	add	ix,sp
                           1552 ;src/entities/entities.c:431: if (g_blocks[bid].ny <= y) {
   4EFA DD 4E 04      [19] 1553 	ld	c,4 (ix)
   4EFD 06 00         [ 7] 1554 	ld	b,#0x00
   4EFF 69            [ 4] 1555 	ld	l, c
   4F00 60            [ 4] 1556 	ld	h, b
   4F01 29            [11] 1557 	add	hl, hl
   4F02 09            [11] 1558 	add	hl, bc
   4F03 29            [11] 1559 	add	hl, hl
   4F04 09            [11] 1560 	add	hl, bc
   4F05 29            [11] 1561 	add	hl, hl
   4F06 09            [11] 1562 	add	hl, bc
   4F07 29            [11] 1563 	add	hl, hl
   4F08 09            [11] 1564 	add	hl, bc
   4F09 11 A1 73      [10] 1565 	ld	de, #_g_blocks
   4F0C 19            [11] 1566 	add	hl, de
   4F0D 11 0C 00      [10] 1567 	ld	de, #0x000c
   4F10 19            [11] 1568 	add	hl, de
   4F11 46            [ 7] 1569 	ld	b, (hl)
                           1570 ;src/entities/entities.c:434: while (bid > 0 && g_blocks[bid-1].ny <= y) --bid;
   4F12 DD 4E 04      [19] 1571 	ld	c, 4 (ix)
                           1572 ;src/entities/entities.c:431: if (g_blocks[bid].ny <= y) {
   4F15 DD 7E 05      [19] 1573 	ld	a, 5 (ix)
   4F18 90            [ 4] 1574 	sub	a, b
   4F19 38 23         [12] 1575 	jr	C,00119$
                           1576 ;src/entities/entities.c:434: while (bid > 0 && g_blocks[bid-1].ny <= y) --bid;
   4F1B                    1577 00102$:
   4F1B 79            [ 4] 1578 	ld	a, c
   4F1C B7            [ 4] 1579 	or	a, a
   4F1D 28 51         [12] 1580 	jr	Z,00120$
   4F1F 59            [ 4] 1581 	ld	e, c
   4F20 16 00         [ 7] 1582 	ld	d, #0x00
   4F22 1B            [ 6] 1583 	dec	de
   4F23 6B            [ 4] 1584 	ld	l, e
   4F24 62            [ 4] 1585 	ld	h, d
   4F25 29            [11] 1586 	add	hl, hl
   4F26 19            [11] 1587 	add	hl, de
   4F27 29            [11] 1588 	add	hl, hl
   4F28 19            [11] 1589 	add	hl, de
   4F29 29            [11] 1590 	add	hl, hl
   4F2A 19            [11] 1591 	add	hl, de
   4F2B 29            [11] 1592 	add	hl, hl
   4F2C 19            [11] 1593 	add	hl, de
   4F2D 11 A1 73      [10] 1594 	ld	de, #_g_blocks
   4F30 19            [11] 1595 	add	hl, de
   4F31 11 0C 00      [10] 1596 	ld	de, #0x000c
   4F34 19            [11] 1597 	add	hl, de
   4F35 DD 7E 05      [19] 1598 	ld	a,5 (ix)
   4F38 96            [ 7] 1599 	sub	a,(hl)
   4F39 38 35         [12] 1600 	jr	C,00120$
   4F3B 0D            [ 4] 1601 	dec	c
   4F3C 18 DD         [12] 1602 	jr	00102$
                           1603 ;src/entities/entities.c:438: while (bid < g_lastBlock - 1 && g_blocks[bid+1].ny > y) ++bid;
   4F3E                    1604 00119$:
   4F3E                    1605 00106$:
   4F3E 21 91 75      [10] 1606 	ld	hl,#_g_lastBlock + 0
   4F41 5E            [ 7] 1607 	ld	e, (hl)
   4F42 16 00         [ 7] 1608 	ld	d, #0x00
   4F44 1B            [ 6] 1609 	dec	de
   4F45 69            [ 4] 1610 	ld	l, c
   4F46 26 00         [ 7] 1611 	ld	h, #0x00
   4F48 7D            [ 4] 1612 	ld	a, l
   4F49 93            [ 4] 1613 	sub	a, e
   4F4A 7C            [ 4] 1614 	ld	a, h
   4F4B 9A            [ 4] 1615 	sbc	a, d
   4F4C E2 51 4F      [10] 1616 	jp	PO, 00143$
   4F4F EE 80         [ 7] 1617 	xor	a, #0x80
   4F51                    1618 00143$:
   4F51 F2 75 4F      [10] 1619 	jp	P, 00121$
   4F54 23            [ 6] 1620 	inc	hl
   4F55 5D            [ 4] 1621 	ld	e, l
   4F56 54            [ 4] 1622 	ld	d, h
   4F57 29            [11] 1623 	add	hl, hl
   4F58 19            [11] 1624 	add	hl, de
   4F59 29            [11] 1625 	add	hl, hl
   4F5A 19            [11] 1626 	add	hl, de
   4F5B 29            [11] 1627 	add	hl, hl
   4F5C 19            [11] 1628 	add	hl, de
   4F5D 29            [11] 1629 	add	hl, hl
   4F5E 19            [11] 1630 	add	hl, de
   4F5F 11 A1 73      [10] 1631 	ld	de, #_g_blocks
   4F62 19            [11] 1632 	add	hl, de
   4F63 11 0C 00      [10] 1633 	ld	de, #0x000c
   4F66 19            [11] 1634 	add	hl, de
   4F67 DD 7E 05      [19] 1635 	ld	a,5 (ix)
   4F6A 96            [ 7] 1636 	sub	a,(hl)
   4F6B 30 08         [12] 1637 	jr	NC,00121$
   4F6D 0C            [ 4] 1638 	inc	c
   4F6E 18 CE         [12] 1639 	jr	00106$
   4F70                    1640 00120$:
   4F70 DD 71 04      [19] 1641 	ld	4 (ix), c
                           1642 ;src/entities/entities.c:442: return bid;
   4F73 18 03         [12] 1643 	jr	00111$
                           1644 ;src/entities/entities.c:438: while (bid < g_lastBlock - 1 && g_blocks[bid+1].ny > y) ++bid;
   4F75                    1645 00121$:
   4F75 DD 71 04      [19] 1646 	ld	4 (ix), c
   4F78                    1647 00111$:
                           1648 ;src/entities/entities.c:442: return bid;
   4F78 DD 6E 04      [19] 1649 	ld	l, 4 (ix)
   4F7B DD E1         [14] 1650 	pop	ix
   4F7D C9            [10] 1651 	ret
                           1652 ;src/entities/entities.c:451: void applyCharacterBlockCollisions(TCharacter *c) {
                           1653 ;	---------------------------------
                           1654 ; Function applyCharacterBlockCollisions
                           1655 ; ---------------------------------
   4F7E                    1656 _applyCharacterBlockCollisions::
   4F7E DD E5         [15] 1657 	push	ix
   4F80 DD 21 00 00   [14] 1658 	ld	ix,#0
   4F84 DD 39         [15] 1659 	add	ix,sp
   4F86 21 DE FF      [10] 1660 	ld	hl, #-34
   4F89 39            [11] 1661 	add	hl, sp
   4F8A F9            [ 6] 1662 	ld	sp, hl
                           1663 ;src/entities/entities.c:452: TEntity  *e  = &c->entity;  // Entity associated to the character
   4F8B DD 7E 04      [19] 1664 	ld	a, 4 (ix)
   4F8E DD 77 FE      [19] 1665 	ld	-2 (ix), a
   4F91 DD 7E 05      [19] 1666 	ld	a, 5 (ix)
   4F94 DD 77 FF      [19] 1667 	ld	-1 (ix), a
   4F97 DD 4E FE      [19] 1668 	ld	c,-2 (ix)
   4F9A DD 46 FF      [19] 1669 	ld	b,-1 (ix)
   4F9D DD 71 E4      [19] 1670 	ld	-28 (ix), c
   4FA0 DD 70 E5      [19] 1671 	ld	-27 (ix), b
                           1672 ;src/entities/entities.c:453: TPhysics *p  = &e->phys;    // Physics component of the character
   4FA3 DD 7E E4      [19] 1673 	ld	a, -28 (ix)
   4FA6 C6 0F         [ 7] 1674 	add	a, #0x0f
   4FA8 DD 77 E2      [19] 1675 	ld	-30 (ix), a
   4FAB DD 7E E5      [19] 1676 	ld	a, -27 (ix)
   4FAE CE 00         [ 7] 1677 	adc	a, #0x00
   4FB0 DD 77 E3      [19] 1678 	ld	-29 (ix), a
                           1679 ;src/entities/entities.c:457: i = PXMARGIN + e->ny + e->graph.anim.frames[e->graph.anim.frame_id]->height; 
   4FB3 DD 7E E4      [19] 1680 	ld	a, -28 (ix)
   4FB6 C6 0C         [ 7] 1681 	add	a, #0x0c
   4FB8 DD 77 FC      [19] 1682 	ld	-4 (ix), a
   4FBB DD 7E E5      [19] 1683 	ld	a, -27 (ix)
   4FBE CE 00         [ 7] 1684 	adc	a, #0x00
   4FC0 DD 77 FD      [19] 1685 	ld	-3 (ix), a
   4FC3 DD 6E FC      [19] 1686 	ld	l,-4 (ix)
   4FC6 DD 66 FD      [19] 1687 	ld	h,-3 (ix)
   4FC9 4E            [ 7] 1688 	ld	c, (hl)
   4FCA 0C            [ 4] 1689 	inc	c
   4FCB 0C            [ 4] 1690 	inc	c
   4FCC 0C            [ 4] 1691 	inc	c
   4FCD 0C            [ 4] 1692 	inc	c
   4FCE DD 6E E4      [19] 1693 	ld	l,-28 (ix)
   4FD1 DD 66 E5      [19] 1694 	ld	h,-27 (ix)
   4FD4 5E            [ 7] 1695 	ld	e, (hl)
   4FD5 23            [ 6] 1696 	inc	hl
   4FD6 56            [ 7] 1697 	ld	d, (hl)
   4FD7 DD 6E E4      [19] 1698 	ld	l,-28 (ix)
   4FDA DD 66 E5      [19] 1699 	ld	h,-27 (ix)
   4FDD 23            [ 6] 1700 	inc	hl
   4FDE 23            [ 6] 1701 	inc	hl
   4FDF 6E            [ 7] 1702 	ld	l, (hl)
   4FE0 26 00         [ 7] 1703 	ld	h, #0x00
   4FE2 29            [11] 1704 	add	hl, hl
   4FE3 19            [11] 1705 	add	hl, de
   4FE4 7E            [ 7] 1706 	ld	a, (hl)
   4FE5 23            [ 6] 1707 	inc	hl
   4FE6 66            [ 7] 1708 	ld	h, (hl)
   4FE7 6F            [ 4] 1709 	ld	l, a
   4FE8 23            [ 6] 1710 	inc	hl
   4FE9 23            [ 6] 1711 	inc	hl
   4FEA 23            [ 6] 1712 	inc	hl
   4FEB 46            [ 7] 1713 	ld	b, (hl)
   4FEC 79            [ 4] 1714 	ld	a, c
   4FED 80            [ 4] 1715 	add	a, b
   4FEE 47            [ 4] 1716 	ld	b, a
                           1717 ;src/entities/entities.c:458: g_colMinBlock = getNearestBlockID(g_colMinBlock, i);
   4FEF C5            [11] 1718 	push	bc
   4FF0 33            [ 6] 1719 	inc	sp
   4FF1 3A 92 75      [13] 1720 	ld	a, (_g_colMinBlock)
   4FF4 F5            [11] 1721 	push	af
   4FF5 33            [ 6] 1722 	inc	sp
   4FF6 CD F2 4E      [17] 1723 	call	_getNearestBlockID
   4FF9 F1            [10] 1724 	pop	af
   4FFA FD 21 92 75   [14] 1725 	ld	iy, #_g_colMinBlock
   4FFE FD 75 00      [19] 1726 	ld	0 (iy), l
                           1727 ;src/entities/entities.c:461: i = e->ny - PXMARGIN;
   5001 DD 6E FC      [19] 1728 	ld	l,-4 (ix)
   5004 DD 66 FD      [19] 1729 	ld	h,-3 (ix)
   5007 7E            [ 7] 1730 	ld	a, (hl)
   5008 C6 FC         [ 7] 1731 	add	a, #0xfc
   500A 47            [ 4] 1732 	ld	b, a
                           1733 ;src/entities/entities.c:462: g_colMaxBlock = getNearestBlockID(g_colMaxBlock, i);
   500B C5            [11] 1734 	push	bc
   500C 33            [ 6] 1735 	inc	sp
   500D 3A 93 75      [13] 1736 	ld	a, (_g_colMaxBlock)
   5010 F5            [11] 1737 	push	af
   5011 33            [ 6] 1738 	inc	sp
   5012 CD F2 4E      [17] 1739 	call	_getNearestBlockID
   5015 F1            [10] 1740 	pop	af
   5016 FD 21 93 75   [14] 1741 	ld	iy, #_g_colMaxBlock
   501A FD 75 00      [19] 1742 	ld	0 (iy), l
                           1743 ;src/entities/entities.c:466: for(i=g_colMinBlock; i <= g_colMaxBlock; ++i) {
   501D 3A 92 75      [13] 1744 	ld	a,(#_g_colMinBlock + 0)
   5020 DD 77 F9      [19] 1745 	ld	-7 (ix), a
   5023 DD 7E FE      [19] 1746 	ld	a, -2 (ix)
   5026 DD 77 F7      [19] 1747 	ld	-9 (ix), a
   5029 DD 7E FF      [19] 1748 	ld	a, -1 (ix)
   502C DD 77 F8      [19] 1749 	ld	-8 (ix), a
   502F DD 7E E4      [19] 1750 	ld	a, -28 (ix)
   5032 DD 77 F4      [19] 1751 	ld	-12 (ix), a
   5035 DD 7E E5      [19] 1752 	ld	a, -27 (ix)
   5038 DD 77 F5      [19] 1753 	ld	-11 (ix), a
   503B DD 7E E4      [19] 1754 	ld	a, -28 (ix)
   503E DD 77 EE      [19] 1755 	ld	-18 (ix), a
   5041 DD 7E E5      [19] 1756 	ld	a, -27 (ix)
   5044 DD 77 EF      [19] 1757 	ld	-17 (ix), a
   5047 DD 7E E4      [19] 1758 	ld	a, -28 (ix)
   504A DD 77 EA      [19] 1759 	ld	-22 (ix), a
   504D DD 7E E5      [19] 1760 	ld	a, -27 (ix)
   5050 DD 77 EB      [19] 1761 	ld	-21 (ix), a
   5053 DD 7E E4      [19] 1762 	ld	a, -28 (ix)
   5056 DD 77 F0      [19] 1763 	ld	-16 (ix), a
   5059 DD 7E E5      [19] 1764 	ld	a, -27 (ix)
   505C DD 77 F1      [19] 1765 	ld	-15 (ix), a
                           1766 ;src/entities/entities.c:478: e->nx += col->w;    // move col->w bytes right (colliding right)
   505F DD 7E E4      [19] 1767 	ld	a, -28 (ix)
   5062 C6 0B         [ 7] 1768 	add	a, #0x0b
   5064 DD 77 F2      [19] 1769 	ld	-14 (ix), a
   5067 DD 7E E5      [19] 1770 	ld	a, -27 (ix)
   506A CE 00         [ 7] 1771 	adc	a, #0x00
   506C DD 77 F3      [19] 1772 	ld	-13 (ix), a
                           1773 ;src/entities/entities.c:466: for(i=g_colMinBlock; i <= g_colMaxBlock; ++i) {
   506F DD 7E F2      [19] 1774 	ld	a, -14 (ix)
   5072 DD 77 FA      [19] 1775 	ld	-6 (ix), a
   5075 DD 7E F3      [19] 1776 	ld	a, -13 (ix)
   5078 DD 77 FB      [19] 1777 	ld	-5 (ix), a
   507B                    1778 00118$:
   507B 3A 93 75      [13] 1779 	ld	a, (#_g_colMaxBlock)
   507E DD 96 F9      [19] 1780 	sub	a, -7 (ix)
   5081 DA D3 52      [10] 1781 	jp	C, 00120$
                           1782 ;src/entities/entities.c:468: TEntity    *ebl = &g_blocks[i];
   5084 DD 4E F9      [19] 1783 	ld	c,-7 (ix)
   5087 06 00         [ 7] 1784 	ld	b,#0x00
   5089 69            [ 4] 1785 	ld	l, c
   508A 60            [ 4] 1786 	ld	h, b
   508B 29            [11] 1787 	add	hl, hl
   508C 09            [11] 1788 	add	hl, bc
   508D 29            [11] 1789 	add	hl, hl
   508E 09            [11] 1790 	add	hl, bc
   508F 29            [11] 1791 	add	hl, hl
   5090 09            [11] 1792 	add	hl, bc
   5091 29            [11] 1793 	add	hl, hl
   5092 09            [11] 1794 	add	hl, bc
   5093 DD 75 EC      [19] 1795 	ld	-20 (ix), l
   5096 DD 74 ED      [19] 1796 	ld	-19 (ix), h
   5099 3E A1         [ 7] 1797 	ld	a, #<(_g_blocks)
   509B DD 86 EC      [19] 1798 	add	a, -20 (ix)
   509E DD 77 EC      [19] 1799 	ld	-20 (ix), a
   50A1 3E 73         [ 7] 1800 	ld	a, #>(_g_blocks)
   50A3 DD 8E ED      [19] 1801 	adc	a, -19 (ix)
   50A6 DD 77 ED      [19] 1802 	ld	-19 (ix), a
   50A9 DD 7E EC      [19] 1803 	ld	a, -20 (ix)
   50AC DD 77 E0      [19] 1804 	ld	-32 (ix), a
   50AF DD 7E ED      [19] 1805 	ld	a, -19 (ix)
   50B2 DD 77 E1      [19] 1806 	ld	-31 (ix), a
                           1807 ;src/entities/entities.c:469: TCollision *col = checkCollisionEntBlock(e, ebl);
   50B5 C1            [10] 1808 	pop	bc
   50B6 E1            [10] 1809 	pop	hl
   50B7 E5            [11] 1810 	push	hl
   50B8 C5            [11] 1811 	push	bc
   50B9 E5            [11] 1812 	push	hl
   50BA DD 6E E4      [19] 1813 	ld	l,-28 (ix)
   50BD DD 66 E5      [19] 1814 	ld	h,-27 (ix)
   50C0 E5            [11] 1815 	push	hl
   50C1 CD 7A 55      [17] 1816 	call	_checkCollisionEntBlock
   50C4 F1            [10] 1817 	pop	af
   50C5 F1            [10] 1818 	pop	af
   50C6 DD 74 DF      [19] 1819 	ld	-33 (ix), h
                           1820 ;src/entities/entities.c:472: if (col->w && col->h) {
   50C9 DD 75 DE      [19] 1821 	ld	-34 (ix), l
   50CC 7D            [ 4] 1822 	ld	a, l
   50CD C6 02         [ 7] 1823 	add	a, #0x02
   50CF DD 77 EC      [19] 1824 	ld	-20 (ix), a
   50D2 DD 7E DF      [19] 1825 	ld	a, -33 (ix)
   50D5 CE 00         [ 7] 1826 	adc	a, #0x00
   50D7 DD 77 ED      [19] 1827 	ld	-19 (ix), a
   50DA DD 6E EC      [19] 1828 	ld	l,-20 (ix)
   50DD DD 66 ED      [19] 1829 	ld	h,-19 (ix)
   50E0 7E            [ 7] 1830 	ld	a, (hl)
   50E1 DD 77 EC      [19] 1831 	ld	-20 (ix), a
   50E4 B7            [ 4] 1832 	or	a, a
   50E5 CA CD 52      [10] 1833 	jp	Z, 00119$
   50E8 E1            [10] 1834 	pop	hl
   50E9 E5            [11] 1835 	push	hl
   50EA 23            [ 6] 1836 	inc	hl
   50EB 23            [ 6] 1837 	inc	hl
   50EC 23            [ 6] 1838 	inc	hl
   50ED 7E            [ 7] 1839 	ld	a, (hl)
   50EE DD 77 E8      [19] 1840 	ld	-24 (ix), a
   50F1 B7            [ 4] 1841 	or	a, a
   50F2 CA CD 52      [10] 1842 	jp	Z, 00119$
                           1843 ;src/entities/entities.c:476: if(e->x <= col->x - e->pw  || e->x >= ebl->x + ebl->pw ) {
   50F5 DD 6E F4      [19] 1844 	ld	l,-12 (ix)
   50F8 DD 66 F5      [19] 1845 	ld	h,-11 (ix)
   50FB 11 09 00      [10] 1846 	ld	de, #0x0009
   50FE 19            [11] 1847 	add	hl, de
   50FF 4E            [ 7] 1848 	ld	c, (hl)
   5100 E1            [10] 1849 	pop	hl
   5101 E5            [11] 1850 	push	hl
   5102 7E            [ 7] 1851 	ld	a, (hl)
   5103 DD 77 F6      [19] 1852 	ld	-10 (ix), a
   5106 5F            [ 4] 1853 	ld	e, a
   5107 16 00         [ 7] 1854 	ld	d, #0x00
   5109 DD 6E EE      [19] 1855 	ld	l,-18 (ix)
   510C DD 66 EF      [19] 1856 	ld	h,-17 (ix)
   510F C5            [11] 1857 	push	bc
   5110 01 0D 00      [10] 1858 	ld	bc, #0x000d
   5113 09            [11] 1859 	add	hl, bc
   5114 C1            [10] 1860 	pop	bc
   5115 6E            [ 7] 1861 	ld	l, (hl)
   5116 06 00         [ 7] 1862 	ld	b, #0x00
   5118 7B            [ 4] 1863 	ld	a, e
   5119 95            [ 4] 1864 	sub	a, l
   511A 5F            [ 4] 1865 	ld	e, a
   511B 7A            [ 4] 1866 	ld	a, d
   511C 98            [ 4] 1867 	sbc	a, b
   511D 57            [ 4] 1868 	ld	d, a
   511E 06 00         [ 7] 1869 	ld	b, #0x00
   5120 7B            [ 4] 1870 	ld	a, e
   5121 91            [ 4] 1871 	sub	a, c
   5122 7A            [ 4] 1872 	ld	a, d
   5123 98            [ 4] 1873 	sbc	a, b
   5124 E2 29 51      [10] 1874 	jp	PO, 00155$
   5127 EE 80         [ 7] 1875 	xor	a, #0x80
   5129                    1876 00155$:
   5129 F2 53 51      [10] 1877 	jp	P, 00109$
   512C D1            [10] 1878 	pop	de
   512D E1            [10] 1879 	pop	hl
   512E E5            [11] 1880 	push	hl
   512F D5            [11] 1881 	push	de
   5130 11 09 00      [10] 1882 	ld	de, #0x0009
   5133 19            [11] 1883 	add	hl, de
   5134 5E            [ 7] 1884 	ld	e, (hl)
   5135 16 00         [ 7] 1885 	ld	d, #0x00
   5137 DD 6E E0      [19] 1886 	ld	l,-32 (ix)
   513A DD 66 E1      [19] 1887 	ld	h,-31 (ix)
   513D C5            [11] 1888 	push	bc
   513E 01 0D 00      [10] 1889 	ld	bc, #0x000d
   5141 09            [11] 1890 	add	hl, bc
   5142 C1            [10] 1891 	pop	bc
   5143 6E            [ 7] 1892 	ld	l, (hl)
   5144 26 00         [ 7] 1893 	ld	h, #0x00
   5146 19            [11] 1894 	add	hl, de
   5147 79            [ 4] 1895 	ld	a, c
   5148 95            [ 4] 1896 	sub	a, l
   5149 78            [ 4] 1897 	ld	a, b
   514A 9C            [ 4] 1898 	sbc	a, h
   514B E2 50 51      [10] 1899 	jp	PO, 00156$
   514E EE 80         [ 7] 1900 	xor	a, #0x80
   5150                    1901 00156$:
   5150 FA AD 51      [10] 1902 	jp	M, 00110$
   5153                    1903 00109$:
                           1904 ;src/entities/entities.c:477: if (col->x > ebl->nx) 
   5153 C1            [10] 1905 	pop	bc
   5154 E1            [10] 1906 	pop	hl
   5155 E5            [11] 1907 	push	hl
   5156 C5            [11] 1908 	push	bc
   5157 11 0B 00      [10] 1909 	ld	de, #0x000b
   515A 19            [11] 1910 	add	hl, de
   515B 4E            [ 7] 1911 	ld	c, (hl)
                           1912 ;src/entities/entities.c:478: e->nx += col->w;    // move col->w bytes right (colliding right)
   515C DD 6E F2      [19] 1913 	ld	l,-14 (ix)
   515F DD 66 F3      [19] 1914 	ld	h,-13 (ix)
   5162 7E            [ 7] 1915 	ld	a, (hl)
   5163 DD 77 E9      [19] 1916 	ld	-23 (ix), a
                           1917 ;src/entities/entities.c:477: if (col->x > ebl->nx) 
   5166 79            [ 4] 1918 	ld	a, c
   5167 DD 96 F6      [19] 1919 	sub	a, -10 (ix)
   516A 30 0F         [12] 1920 	jr	NC,00102$
                           1921 ;src/entities/entities.c:478: e->nx += col->w;    // move col->w bytes right (colliding right)
   516C DD 7E E9      [19] 1922 	ld	a, -23 (ix)
   516F DD 86 EC      [19] 1923 	add	a, -20 (ix)
   5172 DD 6E F2      [19] 1924 	ld	l,-14 (ix)
   5175 DD 66 F3      [19] 1925 	ld	h,-13 (ix)
   5178 77            [ 7] 1926 	ld	(hl), a
   5179 18 0D         [12] 1927 	jr	00103$
   517B                    1928 00102$:
                           1929 ;src/entities/entities.c:480: e->nx -= col->w;    // move col->w bytes left  (colliding left)
   517B DD 7E E9      [19] 1930 	ld	a, -23 (ix)
   517E DD 96 EC      [19] 1931 	sub	a, -20 (ix)
   5181 DD 6E F2      [19] 1932 	ld	l,-14 (ix)
   5184 DD 66 F3      [19] 1933 	ld	h,-13 (ix)
   5187 77            [ 7] 1934 	ld	(hl), a
   5188                    1935 00103$:
                           1936 ;src/entities/entities.c:483: p->x  = e->nx * SCALE;
   5188 DD 6E FA      [19] 1937 	ld	l,-6 (ix)
   518B DD 66 FB      [19] 1938 	ld	h,-5 (ix)
   518E 4E            [ 7] 1939 	ld	c, (hl)
   518F 06 00         [ 7] 1940 	ld	b, #0x00
   5191 DD 6E E2      [19] 1941 	ld	l,-30 (ix)
   5194 DD 66 E3      [19] 1942 	ld	h,-29 (ix)
   5197 70            [ 7] 1943 	ld	(hl), b
   5198 23            [ 6] 1944 	inc	hl
   5199 71            [ 7] 1945 	ld	(hl), c
                           1946 ;src/entities/entities.c:484: p->vx = 0;
   519A DD 7E E2      [19] 1947 	ld	a, -30 (ix)
   519D C6 04         [ 7] 1948 	add	a, #0x04
   519F 6F            [ 4] 1949 	ld	l, a
   51A0 DD 7E E3      [19] 1950 	ld	a, -29 (ix)
   51A3 CE 00         [ 7] 1951 	adc	a, #0x00
   51A5 67            [ 4] 1952 	ld	h, a
   51A6 AF            [ 4] 1953 	xor	a, a
   51A7 77            [ 7] 1954 	ld	(hl), a
   51A8 23            [ 6] 1955 	inc	hl
   51A9 77            [ 7] 1956 	ld	(hl), a
   51AA C3 CD 52      [10] 1957 	jp	00119$
   51AD                    1958 00110$:
                           1959 ;src/entities/entities.c:487: } else if (e->y < col->y - e->ph / 2) { 
   51AD DD 6E EA      [19] 1960 	ld	l,-22 (ix)
   51B0 DD 66 EB      [19] 1961 	ld	h,-21 (ix)
   51B3 11 0A 00      [10] 1962 	ld	de, #0x000a
   51B6 19            [11] 1963 	add	hl, de
   51B7 7E            [ 7] 1964 	ld	a, (hl)
   51B8 DD 77 E9      [19] 1965 	ld	-23 (ix), a
   51BB C1            [10] 1966 	pop	bc
   51BC C5            [11] 1967 	push	bc
   51BD 03            [ 6] 1968 	inc	bc
   51BE 0A            [ 7] 1969 	ld	a, (bc)
   51BF DD 77 F6      [19] 1970 	ld	-10 (ix), a
   51C2 5F            [ 4] 1971 	ld	e, a
   51C3 16 00         [ 7] 1972 	ld	d, #0x00
   51C5 DD 6E F0      [19] 1973 	ld	l,-16 (ix)
   51C8 DD 66 F1      [19] 1974 	ld	h,-15 (ix)
   51CB C5            [11] 1975 	push	bc
   51CC 01 0E 00      [10] 1976 	ld	bc, #0x000e
   51CF 09            [11] 1977 	add	hl, bc
   51D0 C1            [10] 1978 	pop	bc
   51D1 6E            [ 7] 1979 	ld	l, (hl)
   51D2 CB 3D         [ 8] 1980 	srl	l
   51D4 26 00         [ 7] 1981 	ld	h, #0x00
   51D6 7B            [ 4] 1982 	ld	a, e
   51D7 95            [ 4] 1983 	sub	a, l
   51D8 5F            [ 4] 1984 	ld	e, a
   51D9 7A            [ 4] 1985 	ld	a, d
   51DA 9C            [ 4] 1986 	sbc	a, h
   51DB 57            [ 4] 1987 	ld	d, a
   51DC DD 6E E9      [19] 1988 	ld	l, -23 (ix)
   51DF 26 00         [ 7] 1989 	ld	h, #0x00
                           1990 ;src/entities/entities.c:496: p->y       = e->ny * SCALE;
   51E1 DD 7E E2      [19] 1991 	ld	a, -30 (ix)
   51E4 C6 02         [ 7] 1992 	add	a, #0x02
   51E6 DD 77 EC      [19] 1993 	ld	-20 (ix), a
   51E9 DD 7E E3      [19] 1994 	ld	a, -29 (ix)
   51EC CE 00         [ 7] 1995 	adc	a, #0x00
   51EE DD 77 ED      [19] 1996 	ld	-19 (ix), a
                           1997 ;src/entities/entities.c:497: p->vy      = 0;
   51F1 DD 7E E2      [19] 1998 	ld	a, -30 (ix)
   51F4 C6 06         [ 7] 1999 	add	a, #0x06
   51F6 DD 77 E6      [19] 2000 	ld	-26 (ix), a
   51F9 DD 7E E3      [19] 2001 	ld	a, -29 (ix)
   51FC CE 00         [ 7] 2002 	adc	a, #0x00
   51FE DD 77 E7      [19] 2003 	ld	-25 (ix), a
                           2004 ;src/entities/entities.c:487: } else if (e->y < col->y - e->ph / 2) { 
   5201 7D            [ 4] 2005 	ld	a, l
   5202 93            [ 4] 2006 	sub	a, e
   5203 7C            [ 4] 2007 	ld	a, h
   5204 9A            [ 4] 2008 	sbc	a, d
   5205 E2 0A 52      [10] 2009 	jp	PO, 00157$
   5208 EE 80         [ 7] 2010 	xor	a, #0x80
   520A                    2011 00157$:
   520A F2 AA 52      [10] 2012 	jp	P, 00107$
                           2013 ;src/entities/entities.c:488: p->floor   = ebl; // Make this entity the floor
   520D DD 7E E2      [19] 2014 	ld	a, -30 (ix)
   5210 C6 0A         [ 7] 2015 	add	a, #0x0a
   5212 5F            [ 4] 2016 	ld	e, a
   5213 DD 7E E3      [19] 2017 	ld	a, -29 (ix)
   5216 CE 00         [ 7] 2018 	adc	a, #0x00
   5218 57            [ 4] 2019 	ld	d, a
   5219 DD 7E E0      [19] 2020 	ld	a, -32 (ix)
   521C 12            [ 7] 2021 	ld	(de), a
   521D 13            [ 6] 2022 	inc	de
   521E DD 7E E1      [19] 2023 	ld	a, -31 (ix)
   5221 12            [ 7] 2024 	ld	(de), a
                           2025 ;src/entities/entities.c:489: e->nAnim   = g_anim[es_walk][c->side]; // Next animation changes
   5222 FD 21 1C 00   [14] 2026 	ld	iy, #0x001c
   5226 DD 5E E4      [19] 2027 	ld	e,-28 (ix)
   5229 DD 56 E5      [19] 2028 	ld	d,-27 (ix)
   522C FD 19         [15] 2029 	add	iy, de
   522E DD 6E F7      [19] 2030 	ld	l,-9 (ix)
   5231 DD 66 F8      [19] 2031 	ld	h,-8 (ix)
   5234 11 20 00      [10] 2032 	ld	de, #0x0020
   5237 19            [11] 2033 	add	hl, de
   5238 5E            [ 7] 2034 	ld	e, (hl)
   5239 CB 23         [ 8] 2035 	sla	e
   523B 21 23 5E      [10] 2036 	ld	hl, #(_g_anim + 0x0004)
   523E 16 00         [ 7] 2037 	ld	d, #0x00
   5240 19            [11] 2038 	add	hl, de
   5241 5E            [ 7] 2039 	ld	e, (hl)
   5242 23            [ 6] 2040 	inc	hl
   5243 56            [ 7] 2041 	ld	d, (hl)
   5244 FD 73 00      [19] 2042 	ld	0 (iy), e
   5247 FD 72 01      [19] 2043 	ld	1 (iy), d
                           2044 ;src/entities/entities.c:490: e->nStatus = as_pause;     // Make character cycle animation
   524A DD 7E E4      [19] 2045 	ld	a, -28 (ix)
   524D C6 1E         [ 7] 2046 	add	a, #0x1e
   524F 6F            [ 4] 2047 	ld	l, a
   5250 DD 7E E5      [19] 2048 	ld	a, -27 (ix)
   5253 CE 00         [ 7] 2049 	adc	a, #0x00
   5255 67            [ 4] 2050 	ld	h, a
   5256 36 03         [10] 2051 	ld	(hl), #0x03
                           2052 ;src/entities/entities.c:491: c->status  = es_walk;
   5258 DD 7E FE      [19] 2053 	ld	a, -2 (ix)
   525B C6 1F         [ 7] 2054 	add	a, #0x1f
   525D 6F            [ 4] 2055 	ld	l, a
   525E DD 7E FF      [19] 2056 	ld	a, -1 (ix)
   5261 CE 00         [ 7] 2057 	adc	a, #0x00
   5263 67            [ 4] 2058 	ld	h, a
   5264 36 01         [10] 2059 	ld	(hl), #0x01
                           2060 ;src/entities/entities.c:492: e->ny      = col->y - e->nAnim[0]->height; // Move col->h bytes upside and 
   5266 0A            [ 7] 2061 	ld	a, (bc)
   5267 4F            [ 4] 2062 	ld	c, a
   5268 EB            [ 4] 2063 	ex	de,hl
   5269 7E            [ 7] 2064 	ld	a, (hl)
   526A 23            [ 6] 2065 	inc	hl
   526B 66            [ 7] 2066 	ld	h, (hl)
   526C 6F            [ 4] 2067 	ld	l, a
   526D 23            [ 6] 2068 	inc	hl
   526E 23            [ 6] 2069 	inc	hl
   526F 23            [ 6] 2070 	inc	hl
   5270 5E            [ 7] 2071 	ld	e, (hl)
   5271 79            [ 4] 2072 	ld	a, c
   5272 93            [ 4] 2073 	sub	a, e
   5273 4F            [ 4] 2074 	ld	c, a
   5274 DD 6E FC      [19] 2075 	ld	l,-4 (ix)
   5277 DD 66 FD      [19] 2076 	ld	h,-3 (ix)
   527A 71            [ 7] 2077 	ld	(hl), c
                           2078 ;src/entities/entities.c:494: if (e->ny > G_maxY)  
   527B 3A 44 47      [13] 2079 	ld	a,(#_G_maxY + 0)
   527E 91            [ 4] 2080 	sub	a, c
   527F 30 0B         [12] 2081 	jr	NC,00105$
                           2082 ;src/entities/entities.c:495: e->ny=G_minY;
   5281 21 43 47      [10] 2083 	ld	hl,#_G_minY + 0
   5284 4E            [ 7] 2084 	ld	c, (hl)
   5285 DD 6E FC      [19] 2085 	ld	l,-4 (ix)
   5288 DD 66 FD      [19] 2086 	ld	h,-3 (ix)
   528B 71            [ 7] 2087 	ld	(hl), c
   528C                    2088 00105$:
                           2089 ;src/entities/entities.c:496: p->y       = e->ny * SCALE;
   528C DD 6E FC      [19] 2090 	ld	l,-4 (ix)
   528F DD 66 FD      [19] 2091 	ld	h,-3 (ix)
   5292 46            [ 7] 2092 	ld	b, (hl)
   5293 0E 00         [ 7] 2093 	ld	c, #0x00
   5295 DD 6E EC      [19] 2094 	ld	l,-20 (ix)
   5298 DD 66 ED      [19] 2095 	ld	h,-19 (ix)
   529B 71            [ 7] 2096 	ld	(hl), c
   529C 23            [ 6] 2097 	inc	hl
   529D 70            [ 7] 2098 	ld	(hl), b
                           2099 ;src/entities/entities.c:497: p->vy      = 0;
   529E DD 6E E6      [19] 2100 	ld	l,-26 (ix)
   52A1 DD 66 E7      [19] 2101 	ld	h,-25 (ix)
   52A4 AF            [ 4] 2102 	xor	a, a
   52A5 77            [ 7] 2103 	ld	(hl), a
   52A6 23            [ 6] 2104 	inc	hl
   52A7 77            [ 7] 2105 	ld	(hl), a
   52A8 18 23         [12] 2106 	jr	00119$
   52AA                    2107 00107$:
                           2108 ;src/entities/entities.c:501: e->ny  = col->y + col->h;  // Move col->h bytes downside (ceil)
   52AA DD 7E F6      [19] 2109 	ld	a, -10 (ix)
   52AD DD 86 E8      [19] 2110 	add	a, -24 (ix)
   52B0 4F            [ 4] 2111 	ld	c, a
   52B1 DD 6E FC      [19] 2112 	ld	l,-4 (ix)
   52B4 DD 66 FD      [19] 2113 	ld	h,-3 (ix)
   52B7 71            [ 7] 2114 	ld	(hl), c
                           2115 ;src/entities/entities.c:502: p->y   = e->ny * SCALE;
   52B8 06 00         [ 7] 2116 	ld	b, #0x00
   52BA DD 6E EC      [19] 2117 	ld	l,-20 (ix)
   52BD DD 66 ED      [19] 2118 	ld	h,-19 (ix)
   52C0 70            [ 7] 2119 	ld	(hl), b
   52C1 23            [ 6] 2120 	inc	hl
   52C2 71            [ 7] 2121 	ld	(hl), c
                           2122 ;src/entities/entities.c:503: p->vy  = 0;
   52C3 DD 6E E6      [19] 2123 	ld	l,-26 (ix)
   52C6 DD 66 E7      [19] 2124 	ld	h,-25 (ix)
   52C9 AF            [ 4] 2125 	xor	a, a
   52CA 77            [ 7] 2126 	ld	(hl), a
   52CB 23            [ 6] 2127 	inc	hl
   52CC 77            [ 7] 2128 	ld	(hl), a
   52CD                    2129 00119$:
                           2130 ;src/entities/entities.c:466: for(i=g_colMinBlock; i <= g_colMaxBlock; ++i) {
   52CD DD 34 F9      [23] 2131 	inc	-7 (ix)
   52D0 C3 7B 50      [10] 2132 	jp	00118$
   52D3                    2133 00120$:
   52D3 DD F9         [10] 2134 	ld	sp, ix
   52D5 DD E1         [14] 2135 	pop	ix
   52D7 C9            [10] 2136 	ret
                           2137 ;src/entities/entities.c:514: u8 updateCharacter(TCharacter *c) {
                           2138 ;	---------------------------------
                           2139 ; Function updateCharacter
                           2140 ; ---------------------------------
   52D8                    2141 _updateCharacter::
   52D8 DD E5         [15] 2142 	push	ix
   52DA DD 21 00 00   [14] 2143 	ld	ix,#0
   52DE DD 39         [15] 2144 	add	ix,sp
   52E0 21 E8 FF      [10] 2145 	ld	hl, #-24
   52E3 39            [11] 2146 	add	hl, sp
   52E4 F9            [ 6] 2147 	ld	sp, hl
                           2148 ;src/entities/entities.c:515: TEntity  *e = &c->entity;
   52E5 DD 7E 04      [19] 2149 	ld	a, 4 (ix)
   52E8 DD 77 FE      [19] 2150 	ld	-2 (ix), a
   52EB DD 7E 05      [19] 2151 	ld	a, 5 (ix)
   52EE DD 77 FF      [19] 2152 	ld	-1 (ix), a
   52F1 DD 5E FE      [19] 2153 	ld	e,-2 (ix)
   52F4 DD 56 FF      [19] 2154 	ld	d,-1 (ix)
                           2155 ;src/entities/entities.c:516: TPhysics *p = &e->phys;
   52F7 21 0F 00      [10] 2156 	ld	hl, #0x000f
   52FA 19            [11] 2157 	add	hl,de
   52FB DD 75 EB      [19] 2158 	ld	-21 (ix), l
   52FE DD 74 EC      [19] 2159 	ld	-20 (ix), h
                           2160 ;src/entities/entities.c:518: TAnimFrame   *af = anim->frames[anim->frame_id];
   5301 6B            [ 4] 2161 	ld	l, e
   5302 62            [ 4] 2162 	ld	h, d
   5303 4E            [ 7] 2163 	ld	c, (hl)
   5304 23            [ 6] 2164 	inc	hl
   5305 46            [ 7] 2165 	ld	b, (hl)
   5306 21 02 00      [10] 2166 	ld	hl, #0x0002
   5309 19            [11] 2167 	add	hl,de
   530A DD 75 F3      [19] 2168 	ld	-13 (ix), l
   530D DD 74 F4      [19] 2169 	ld	-12 (ix), h
   5310 6E            [ 7] 2170 	ld	l, (hl)
   5311 26 00         [ 7] 2171 	ld	h, #0x00
   5313 29            [11] 2172 	add	hl, hl
   5314 09            [11] 2173 	add	hl, bc
   5315 7E            [ 7] 2174 	ld	a, (hl)
   5316 DD 77 E9      [19] 2175 	ld	-23 (ix), a
   5319 23            [ 6] 2176 	inc	hl
   531A 7E            [ 7] 2177 	ld	a, (hl)
   531B DD 77 EA      [19] 2178 	ld	-22 (ix), a
                           2179 ;src/entities/entities.c:519: u8         alive = 1;
   531E DD 36 E8 01   [19] 2180 	ld	-24 (ix), #0x01
                           2181 ;src/entities/entities.c:522: e->x       = e->nx;
   5322 21 09 00      [10] 2182 	ld	hl, #0x0009
   5325 19            [11] 2183 	add	hl,de
   5326 4D            [ 4] 2184 	ld	c, l
   5327 44            [ 4] 2185 	ld	b, h
   5328 21 0B 00      [10] 2186 	ld	hl, #0x000b
   532B 19            [11] 2187 	add	hl,de
   532C DD 75 F5      [19] 2188 	ld	-11 (ix), l
   532F DD 74 F6      [19] 2189 	ld	-10 (ix), h
   5332 7E            [ 7] 2190 	ld	a, (hl)
   5333 02            [ 7] 2191 	ld	(bc), a
                           2192 ;src/entities/entities.c:523: e->y       = e->ny;
   5334 21 0A 00      [10] 2193 	ld	hl, #0x000a
   5337 19            [11] 2194 	add	hl,de
   5338 DD 75 EF      [19] 2195 	ld	-17 (ix), l
   533B DD 74 F0      [19] 2196 	ld	-16 (ix), h
   533E 21 0C 00      [10] 2197 	ld	hl, #0x000c
   5341 19            [11] 2198 	add	hl,de
   5342 DD 75 FC      [19] 2199 	ld	-4 (ix), l
   5345 DD 74 FD      [19] 2200 	ld	-3 (ix), h
   5348 7E            [ 7] 2201 	ld	a, (hl)
   5349 DD 6E EF      [19] 2202 	ld	l,-17 (ix)
   534C DD 66 F0      [19] 2203 	ld	h,-16 (ix)
   534F 77            [ 7] 2204 	ld	(hl), a
                           2205 ;src/entities/entities.c:524: e->pscreen = e->npscreen;
   5350 FD 21 05 00   [14] 2206 	ld	iy, #0x0005
   5354 FD 19         [15] 2207 	add	iy, de
   5356 21 07 00      [10] 2208 	ld	hl, #0x0007
   5359 19            [11] 2209 	add	hl,de
   535A DD 75 F1      [19] 2210 	ld	-15 (ix), l
   535D DD 74 F2      [19] 2211 	ld	-14 (ix), h
   5360 7E            [ 7] 2212 	ld	a, (hl)
   5361 23            [ 6] 2213 	inc	hl
   5362 66            [ 7] 2214 	ld	h, (hl)
   5363 FD 77 00      [19] 2215 	ld	0 (iy), a
   5366 FD 74 01      [19] 2216 	ld	1 (iy), h
                           2217 ;src/entities/entities.c:525: e->pw      = af->width;
   5369 FD 21 0D 00   [14] 2218 	ld	iy, #0x000d
   536D FD 19         [15] 2219 	add	iy, de
   536F DD 6E E9      [19] 2220 	ld	l,-23 (ix)
   5372 DD 66 EA      [19] 2221 	ld	h,-22 (ix)
   5375 23            [ 6] 2222 	inc	hl
   5376 23            [ 6] 2223 	inc	hl
   5377 6E            [ 7] 2224 	ld	l, (hl)
   5378 FD 75 00      [19] 2225 	ld	0 (iy), l
                           2226 ;src/entities/entities.c:526: e->ph      = af->height;
   537B FD 21 0E 00   [14] 2227 	ld	iy, #0x000e
   537F FD 19         [15] 2228 	add	iy, de
   5381 DD 6E E9      [19] 2229 	ld	l,-23 (ix)
   5384 DD 66 EA      [19] 2230 	ld	h,-22 (ix)
   5387 23            [ 6] 2231 	inc	hl
   5388 23            [ 6] 2232 	inc	hl
   5389 23            [ 6] 2233 	inc	hl
   538A 6E            [ 7] 2234 	ld	l, (hl)
   538B FD 75 00      [19] 2235 	ld	0 (iy), l
                           2236 ;src/entities/entities.c:529: if ( updateAnimation(&e->graph.anim, e->nAnim, e->nStatus) ) { 
   538E 21 1E 00      [10] 2237 	ld	hl, #0x001e
   5391 19            [11] 2238 	add	hl,de
   5392 DD 75 F7      [19] 2239 	ld	-9 (ix), l
   5395 DD 74 F8      [19] 2240 	ld	-8 (ix), h
   5398 7E            [ 7] 2241 	ld	a, (hl)
   5399 DD 77 FB      [19] 2242 	ld	-5 (ix), a
   539C 21 1C 00      [10] 2243 	ld	hl, #0x001c
   539F 19            [11] 2244 	add	hl,de
   53A0 DD 75 F9      [19] 2245 	ld	-7 (ix), l
   53A3 DD 74 FA      [19] 2246 	ld	-6 (ix), h
   53A6 7E            [ 7] 2247 	ld	a, (hl)
   53A7 DD 77 ED      [19] 2248 	ld	-19 (ix), a
   53AA 23            [ 6] 2249 	inc	hl
   53AB 7E            [ 7] 2250 	ld	a, (hl)
   53AC DD 77 EE      [19] 2251 	ld	-18 (ix), a
   53AF C5            [11] 2252 	push	bc
   53B0 D5            [11] 2253 	push	de
   53B1 DD 7E FB      [19] 2254 	ld	a, -5 (ix)
   53B4 F5            [11] 2255 	push	af
   53B5 33            [ 6] 2256 	inc	sp
   53B6 DD 6E ED      [19] 2257 	ld	l,-19 (ix)
   53B9 DD 66 EE      [19] 2258 	ld	h,-18 (ix)
   53BC E5            [11] 2259 	push	hl
   53BD D5            [11] 2260 	push	de
   53BE CD 89 5C      [17] 2261 	call	_updateAnimation
   53C1 F1            [10] 2262 	pop	af
   53C2 F1            [10] 2263 	pop	af
   53C3 33            [ 6] 2264 	inc	sp
   53C4 D1            [10] 2265 	pop	de
   53C5 C1            [10] 2266 	pop	bc
                           2267 ;src/entities/entities.c:530: e->draw = 1;                        // Redraw 
   53C6 7B            [ 4] 2268 	ld	a, e
   53C7 C6 1B         [ 7] 2269 	add	a, #0x1b
   53C9 DD 77 ED      [19] 2270 	ld	-19 (ix), a
   53CC 7A            [ 4] 2271 	ld	a, d
   53CD CE 00         [ 7] 2272 	adc	a, #0x00
   53CF DD 77 EE      [19] 2273 	ld	-18 (ix), a
                           2274 ;src/entities/entities.c:529: if ( updateAnimation(&e->graph.anim, e->nAnim, e->nStatus) ) { 
   53D2 7D            [ 4] 2275 	ld	a, l
   53D3 B7            [ 4] 2276 	or	a, a
   53D4 28 32         [12] 2277 	jr	Z,00102$
                           2278 ;src/entities/entities.c:530: e->draw = 1;                        // Redraw 
   53D6 DD 6E ED      [19] 2279 	ld	l,-19 (ix)
   53D9 DD 66 EE      [19] 2280 	ld	h,-18 (ix)
   53DC 36 01         [10] 2281 	ld	(hl), #0x01
                           2282 ;src/entities/entities.c:531: af = anim->frames[anim->frame_id];  // Get values of the new frame
   53DE EB            [ 4] 2283 	ex	de,hl
   53DF 5E            [ 7] 2284 	ld	e, (hl)
   53E0 23            [ 6] 2285 	inc	hl
   53E1 56            [ 7] 2286 	ld	d, (hl)
   53E2 DD 6E F3      [19] 2287 	ld	l,-13 (ix)
   53E5 DD 66 F4      [19] 2288 	ld	h,-12 (ix)
   53E8 6E            [ 7] 2289 	ld	l, (hl)
   53E9 26 00         [ 7] 2290 	ld	h, #0x00
   53EB 29            [11] 2291 	add	hl, hl
   53EC 19            [11] 2292 	add	hl, de
   53ED 7E            [ 7] 2293 	ld	a, (hl)
   53EE DD 77 E9      [19] 2294 	ld	-23 (ix), a
   53F1 23            [ 6] 2295 	inc	hl
   53F2 7E            [ 7] 2296 	ld	a, (hl)
   53F3 DD 77 EA      [19] 2297 	ld	-22 (ix), a
                           2298 ;src/entities/entities.c:532: e->nAnim   = 0;                     // No next animation/animstatus
   53F6 DD 6E F9      [19] 2299 	ld	l,-7 (ix)
   53F9 DD 66 FA      [19] 2300 	ld	h,-6 (ix)
   53FC AF            [ 4] 2301 	xor	a, a
   53FD 77            [ 7] 2302 	ld	(hl), a
   53FE 23            [ 6] 2303 	inc	hl
   53FF 77            [ 7] 2304 	ld	(hl), a
                           2305 ;src/entities/entities.c:533: e->nStatus = as_null;
   5400 DD 6E F7      [19] 2306 	ld	l,-9 (ix)
   5403 DD 66 F8      [19] 2307 	ld	h,-8 (ix)
   5406 36 00         [10] 2308 	ld	(hl), #0x00
   5408                    2309 00102$:
                           2310 ;src/entities/entities.c:537: updateCharacterPhysics(c);
   5408 C5            [11] 2311 	push	bc
   5409 DD 6E FE      [19] 2312 	ld	l,-2 (ix)
   540C DD 66 FF      [19] 2313 	ld	h,-1 (ix)
   540F E5            [11] 2314 	push	hl
   5410 CD BA 4C      [17] 2315 	call	_updateCharacterPhysics
   5413 F1            [10] 2316 	pop	af
   5414 DD 6E 04      [19] 2317 	ld	l,4 (ix)
   5417 DD 66 05      [19] 2318 	ld	h,5 (ix)
   541A E5            [11] 2319 	push	hl
   541B CD 7E 4F      [17] 2320 	call	_applyCharacterBlockCollisions
   541E F1            [10] 2321 	pop	af
   541F C1            [10] 2322 	pop	bc
                           2323 ;src/entities/entities.c:541: if ( e->nx <= G_minX) { 
   5420 DD 6E F5      [19] 2324 	ld	l,-11 (ix)
   5423 DD 66 F6      [19] 2325 	ld	h,-10 (ix)
   5426 5E            [ 7] 2326 	ld	e, (hl)
   5427 21 41 47      [10] 2327 	ld	hl,#_G_minX + 0
   542A 56            [ 7] 2328 	ld	d, (hl)
   542B 7A            [ 4] 2329 	ld	a, d
   542C 93            [ 4] 2330 	sub	a, e
   542D 38 15         [12] 2331 	jr	C,00106$
                           2332 ;src/entities/entities.c:542: e->nx = G_minX + 1; 
   542F 14            [ 4] 2333 	inc	d
   5430 DD 6E F5      [19] 2334 	ld	l,-11 (ix)
   5433 DD 66 F6      [19] 2335 	ld	h,-10 (ix)
   5436 72            [ 7] 2336 	ld	(hl), d
                           2337 ;src/entities/entities.c:543: p->x = e->nx * SCALE; 
   5437 1E 00         [ 7] 2338 	ld	e, #0x00
   5439 DD 6E EB      [19] 2339 	ld	l,-21 (ix)
   543C DD 66 EC      [19] 2340 	ld	h,-20 (ix)
   543F 73            [ 7] 2341 	ld	(hl), e
   5440 23            [ 6] 2342 	inc	hl
   5441 72            [ 7] 2343 	ld	(hl), d
   5442 18 41         [12] 2344 	jr	00107$
   5444                    2345 00106$:
                           2346 ;src/entities/entities.c:545: else if ( e->nx + af->width >= G_maxX ) {
   5444 16 00         [ 7] 2347 	ld	d, #0x00
   5446 DD 6E E9      [19] 2348 	ld	l,-23 (ix)
   5449 DD 66 EA      [19] 2349 	ld	h,-22 (ix)
   544C 23            [ 6] 2350 	inc	hl
   544D 23            [ 6] 2351 	inc	hl
   544E 7E            [ 7] 2352 	ld	a, (hl)
   544F DD 77 F9      [19] 2353 	ld	-7 (ix), a
   5452 6F            [ 4] 2354 	ld	l, a
   5453 26 00         [ 7] 2355 	ld	h, #0x00
   5455 19            [11] 2356 	add	hl, de
   5456 3A 42 47      [13] 2357 	ld	a,(#_G_maxX + 0)
   5459 DD 77 FB      [19] 2358 	ld	-5 (ix), a
   545C 5F            [ 4] 2359 	ld	e, a
   545D 16 00         [ 7] 2360 	ld	d, #0x00
   545F 7D            [ 4] 2361 	ld	a, l
   5460 93            [ 4] 2362 	sub	a, e
   5461 7C            [ 4] 2363 	ld	a, h
   5462 9A            [ 4] 2364 	sbc	a, d
   5463 E2 68 54      [10] 2365 	jp	PO, 00148$
   5466 EE 80         [ 7] 2366 	xor	a, #0x80
   5468                    2367 00148$:
   5468 FA 85 54      [10] 2368 	jp	M, 00107$
                           2369 ;src/entities/entities.c:546: e->nx = G_maxX - af->width;
   546B DD 7E FB      [19] 2370 	ld	a, -5 (ix)
   546E DD 96 F9      [19] 2371 	sub	a, -7 (ix)
   5471 5F            [ 4] 2372 	ld	e, a
   5472 DD 6E F5      [19] 2373 	ld	l,-11 (ix)
   5475 DD 66 F6      [19] 2374 	ld	h,-10 (ix)
   5478 73            [ 7] 2375 	ld	(hl), e
                           2376 ;src/entities/entities.c:547: p->x  = e->nx * SCALE;  
   5479 53            [ 4] 2377 	ld	d, e
   547A 1E 00         [ 7] 2378 	ld	e, #0x00
   547C DD 6E EB      [19] 2379 	ld	l,-21 (ix)
   547F DD 66 EC      [19] 2380 	ld	h,-20 (ix)
   5482 73            [ 7] 2381 	ld	(hl), e
   5483 23            [ 6] 2382 	inc	hl
   5484 72            [ 7] 2383 	ld	(hl), d
   5485                    2384 00107$:
                           2385 ;src/entities/entities.c:549: if ( e->ny + af->height >= G_maxY ) { 
   5485 DD 6E FC      [19] 2386 	ld	l,-4 (ix)
   5488 DD 66 FD      [19] 2387 	ld	h,-3 (ix)
   548B 7E            [ 7] 2388 	ld	a, (hl)
   548C DD 77 F9      [19] 2389 	ld	-7 (ix), a
   548F 5F            [ 4] 2390 	ld	e, a
   5490 16 00         [ 7] 2391 	ld	d, #0x00
   5492 DD 6E E9      [19] 2392 	ld	l,-23 (ix)
   5495 DD 66 EA      [19] 2393 	ld	h,-22 (ix)
   5498 23            [ 6] 2394 	inc	hl
   5499 23            [ 6] 2395 	inc	hl
   549A 23            [ 6] 2396 	inc	hl
   549B 7E            [ 7] 2397 	ld	a, (hl)
   549C DD 77 FB      [19] 2398 	ld	-5 (ix), a
   549F 6F            [ 4] 2399 	ld	l, a
   54A0 26 00         [ 7] 2400 	ld	h, #0x00
   54A2 19            [11] 2401 	add	hl, de
   54A3 3A 44 47      [13] 2402 	ld	a,(#_G_maxY + 0)
   54A6 DD 77 F7      [19] 2403 	ld	-9 (ix), a
   54A9 5F            [ 4] 2404 	ld	e, a
   54AA 16 00         [ 7] 2405 	ld	d, #0x00
                           2406 ;src/entities/entities.c:551: p->y = e->ny * SCALE;
   54AC DD 7E EB      [19] 2407 	ld	a, -21 (ix)
   54AF C6 02         [ 7] 2408 	add	a, #0x02
   54B1 DD 77 F3      [19] 2409 	ld	-13 (ix), a
   54B4 DD 7E EC      [19] 2410 	ld	a, -20 (ix)
   54B7 CE 00         [ 7] 2411 	adc	a, #0x00
   54B9 DD 77 F4      [19] 2412 	ld	-12 (ix), a
                           2413 ;src/entities/entities.c:549: if ( e->ny + af->height >= G_maxY ) { 
   54BC 7D            [ 4] 2414 	ld	a, l
   54BD 93            [ 4] 2415 	sub	a, e
   54BE 7C            [ 4] 2416 	ld	a, h
   54BF 9A            [ 4] 2417 	sbc	a, d
   54C0 E2 C5 54      [10] 2418 	jp	PO, 00149$
   54C3 EE 80         [ 7] 2419 	xor	a, #0x80
   54C5                    2420 00149$:
   54C5 FA E7 54      [10] 2421 	jp	M, 00111$
                           2422 ;src/entities/entities.c:550: e->ny = G_maxY - af->height;
   54C8 DD 7E F7      [19] 2423 	ld	a, -9 (ix)
   54CB DD 96 FB      [19] 2424 	sub	a, -5 (ix)
   54CE 57            [ 4] 2425 	ld	d, a
   54CF DD 6E FC      [19] 2426 	ld	l,-4 (ix)
   54D2 DD 66 FD      [19] 2427 	ld	h,-3 (ix)
   54D5 72            [ 7] 2428 	ld	(hl), d
                           2429 ;src/entities/entities.c:551: p->y = e->ny * SCALE;
   54D6 1E 00         [ 7] 2430 	ld	e, #0x00
   54D8 DD 6E F3      [19] 2431 	ld	l,-13 (ix)
   54DB DD 66 F4      [19] 2432 	ld	h,-12 (ix)
   54DE 73            [ 7] 2433 	ld	(hl), e
   54DF 23            [ 6] 2434 	inc	hl
   54E0 72            [ 7] 2435 	ld	(hl), d
                           2436 ;src/entities/entities.c:552: alive = 0;
   54E1 DD 36 E8 00   [19] 2437 	ld	-24 (ix), #0x00
   54E5 18 1E         [12] 2438 	jr	00112$
   54E7                    2439 00111$:
                           2440 ;src/entities/entities.c:554: else if ( e->ny <= G_minY ) { 
   54E7 21 43 47      [10] 2441 	ld	hl,#_G_minY + 0
   54EA 5E            [ 7] 2442 	ld	e, (hl)
   54EB 7B            [ 4] 2443 	ld	a, e
   54EC DD 96 F9      [19] 2444 	sub	a, -7 (ix)
   54EF 38 14         [12] 2445 	jr	C,00112$
                           2446 ;src/entities/entities.c:555: e->ny = G_minY + 1;
   54F1 1C            [ 4] 2447 	inc	e
   54F2 DD 6E FC      [19] 2448 	ld	l,-4 (ix)
   54F5 DD 66 FD      [19] 2449 	ld	h,-3 (ix)
   54F8 73            [ 7] 2450 	ld	(hl), e
                           2451 ;src/entities/entities.c:556: p->y = e->ny * SCALE;
   54F9 53            [ 4] 2452 	ld	d, e
   54FA 1E 00         [ 7] 2453 	ld	e, #0x00
   54FC DD 6E F3      [19] 2454 	ld	l,-13 (ix)
   54FF DD 66 F4      [19] 2455 	ld	h,-12 (ix)
   5502 73            [ 7] 2456 	ld	(hl), e
   5503 23            [ 6] 2457 	inc	hl
   5504 72            [ 7] 2458 	ld	(hl), d
   5505                    2459 00112$:
                           2460 ;src/entities/entities.c:549: if ( e->ny + af->height >= G_maxY ) { 
   5505 DD 6E FC      [19] 2461 	ld	l,-4 (ix)
   5508 DD 66 FD      [19] 2462 	ld	h,-3 (ix)
   550B 5E            [ 7] 2463 	ld	e, (hl)
                           2464 ;src/entities/entities.c:561: if ( e->ny != e->y ) { 
   550C DD 6E EF      [19] 2465 	ld	l,-17 (ix)
   550F DD 66 F0      [19] 2466 	ld	h,-16 (ix)
   5512 56            [ 7] 2467 	ld	d, (hl)
                           2468 ;src/entities/entities.c:541: if ( e->nx <= G_minX) { 
   5513 DD 6E F5      [19] 2469 	ld	l,-11 (ix)
   5516 DD 66 F6      [19] 2470 	ld	h,-10 (ix)
   5519 7E            [ 7] 2471 	ld	a, (hl)
   551A DD 77 F9      [19] 2472 	ld	-7 (ix), a
                           2473 ;src/entities/entities.c:561: if ( e->ny != e->y ) { 
   551D 7B            [ 4] 2474 	ld	a, e
   551E 92            [ 4] 2475 	sub	a, d
   551F 28 21         [12] 2476 	jr	Z,00116$
                           2477 ;src/entities/entities.c:562: e->npscreen  = cpct_getScreenPtr(CPCT_VMEM_START, e->nx, e->ny);
   5521 53            [ 4] 2478 	ld	d, e
   5522 DD 5E F9      [19] 2479 	ld	e, -7 (ix)
   5525 D5            [11] 2480 	push	de
   5526 21 00 C0      [10] 2481 	ld	hl, #0xc000
   5529 E5            [11] 2482 	push	hl
   552A CD 9B 67      [17] 2483 	call	_cpct_getScreenPtr
   552D 4D            [ 4] 2484 	ld	c, l
   552E 44            [ 4] 2485 	ld	b, h
   552F DD 6E F1      [19] 2486 	ld	l,-15 (ix)
   5532 DD 66 F2      [19] 2487 	ld	h,-14 (ix)
   5535 71            [ 7] 2488 	ld	(hl), c
   5536 23            [ 6] 2489 	inc	hl
   5537 70            [ 7] 2490 	ld	(hl), b
                           2491 ;src/entities/entities.c:563: e->draw = 1;
   5538 DD 6E ED      [19] 2492 	ld	l,-19 (ix)
   553B DD 66 EE      [19] 2493 	ld	h,-18 (ix)
   553E 36 01         [10] 2494 	ld	(hl), #0x01
   5540 18 30         [12] 2495 	jr	00117$
   5542                    2496 00116$:
                           2497 ;src/entities/entities.c:564: } else if ( e->nx != e->x ) {
   5542 0A            [ 7] 2498 	ld	a, (bc)
   5543 4F            [ 4] 2499 	ld	c, a
   5544 DD 7E F9      [19] 2500 	ld	a, -7 (ix)
   5547 91            [ 4] 2501 	sub	a, c
   5548 28 28         [12] 2502 	jr	Z,00117$
                           2503 ;src/entities/entities.c:565: e->npscreen = e->npscreen + e->nx - e->x;
   554A DD 6E F1      [19] 2504 	ld	l,-15 (ix)
   554D DD 66 F2      [19] 2505 	ld	h,-14 (ix)
   5550 5E            [ 7] 2506 	ld	e, (hl)
   5551 23            [ 6] 2507 	inc	hl
   5552 56            [ 7] 2508 	ld	d, (hl)
   5553 DD 6E F9      [19] 2509 	ld	l,-7 (ix)
   5556 26 00         [ 7] 2510 	ld	h,#0x00
   5558 19            [11] 2511 	add	hl, de
   5559 06 00         [ 7] 2512 	ld	b, #0x00
   555B 7D            [ 4] 2513 	ld	a, l
   555C 91            [ 4] 2514 	sub	a, c
   555D 4F            [ 4] 2515 	ld	c, a
   555E 7C            [ 4] 2516 	ld	a, h
   555F 98            [ 4] 2517 	sbc	a, b
   5560 47            [ 4] 2518 	ld	b, a
   5561 DD 6E F1      [19] 2519 	ld	l,-15 (ix)
   5564 DD 66 F2      [19] 2520 	ld	h,-14 (ix)
   5567 71            [ 7] 2521 	ld	(hl), c
   5568 23            [ 6] 2522 	inc	hl
   5569 70            [ 7] 2523 	ld	(hl), b
                           2524 ;src/entities/entities.c:566: e->draw = 1; 
   556A DD 6E ED      [19] 2525 	ld	l,-19 (ix)
   556D DD 66 EE      [19] 2526 	ld	h,-18 (ix)
   5570 36 01         [10] 2527 	ld	(hl), #0x01
   5572                    2528 00117$:
                           2529 ;src/entities/entities.c:569: return alive;
   5572 DD 6E E8      [19] 2530 	ld	l, -24 (ix)
   5575 DD F9         [10] 2531 	ld	sp, ix
   5577 DD E1         [14] 2532 	pop	ix
   5579 C9            [10] 2533 	ret
                           2534 ;src/entities/entities.c:575: TCollision* checkCollisionEntBlock(TEntity *a, TEntity *b) {
                           2535 ;	---------------------------------
                           2536 ; Function checkCollisionEntBlock
                           2537 ; ---------------------------------
   557A                    2538 _checkCollisionEntBlock::
   557A DD E5         [15] 2539 	push	ix
   557C DD 21 00 00   [14] 2540 	ld	ix,#0
   5580 DD 39         [15] 2541 	add	ix,sp
   5582 21 F5 FF      [10] 2542 	ld	hl, #-11
   5585 39            [11] 2543 	add	hl, sp
   5586 F9            [ 6] 2544 	ld	sp, hl
                           2545 ;src/entities/entities.c:577: TAnimFrame *ani = a->graph.anim.frames [a->graph.anim.frame_id];
   5587 DD 4E 04      [19] 2546 	ld	c,4 (ix)
   558A DD 46 05      [19] 2547 	ld	b,5 (ix)
   558D 69            [ 4] 2548 	ld	l, c
   558E 60            [ 4] 2549 	ld	h, b
   558F 5E            [ 7] 2550 	ld	e, (hl)
   5590 23            [ 6] 2551 	inc	hl
   5591 56            [ 7] 2552 	ld	d, (hl)
   5592 69            [ 4] 2553 	ld	l, c
   5593 60            [ 4] 2554 	ld	h, b
   5594 23            [ 6] 2555 	inc	hl
   5595 23            [ 6] 2556 	inc	hl
   5596 6E            [ 7] 2557 	ld	l, (hl)
   5597 26 00         [ 7] 2558 	ld	h, #0x00
   5599 29            [11] 2559 	add	hl, hl
   559A 19            [11] 2560 	add	hl, de
   559B 7E            [ 7] 2561 	ld	a, (hl)
   559C DD 77 F7      [19] 2562 	ld	-9 (ix), a
   559F 23            [ 6] 2563 	inc	hl
   55A0 7E            [ 7] 2564 	ld	a, (hl)
   55A1 DD 77 F8      [19] 2565 	ld	-8 (ix), a
                           2566 ;src/entities/entities.c:578: TBlock     *blk = &b->graph.block;
   55A4 DD 7E 06      [19] 2567 	ld	a, 6 (ix)
   55A7 DD 77 FD      [19] 2568 	ld	-3 (ix), a
   55AA DD 7E 07      [19] 2569 	ld	a, 7 (ix)
   55AD DD 77 FE      [19] 2570 	ld	-2 (ix), a
   55B0 DD 5E FD      [19] 2571 	ld	e,-3 (ix)
   55B3 DD 56 FE      [19] 2572 	ld	d,-2 (ix)
   55B6 DD 73 F9      [19] 2573 	ld	-7 (ix), e
   55B9 DD 72 FA      [19] 2574 	ld	-6 (ix), d
                           2575 ;src/entities/entities.c:581: c.h = 0;
   55BC 21 98 75      [10] 2576 	ld	hl, #(_checkCollisionEntBlock_c_1_213 + 0x0003)
   55BF 36 00         [10] 2577 	ld	(hl), #0x00
                           2578 ;src/entities/entities.c:585: u8 a_bbound = a->ny + ani->height - 1;// -- bottom boundary of a
   55C1 69            [ 4] 2579 	ld	l, c
   55C2 60            [ 4] 2580 	ld	h, b
   55C3 11 0C 00      [10] 2581 	ld	de, #0x000c
   55C6 19            [11] 2582 	add	hl, de
   55C7 5E            [ 7] 2583 	ld	e, (hl)
   55C8 DD 6E F7      [19] 2584 	ld	l,-9 (ix)
   55CB DD 66 F8      [19] 2585 	ld	h,-8 (ix)
   55CE 23            [ 6] 2586 	inc	hl
   55CF 23            [ 6] 2587 	inc	hl
   55D0 23            [ 6] 2588 	inc	hl
   55D1 56            [ 7] 2589 	ld	d, (hl)
   55D2 7B            [ 4] 2590 	ld	a, e
   55D3 82            [ 4] 2591 	add	a, d
   55D4 C6 FF         [ 7] 2592 	add	a, #0xff
   55D6 DD 77 F5      [19] 2593 	ld	-11 (ix), a
                           2594 ;src/entities/entities.c:586: u8 b_bbound = b->ny + blk->h - 1;     // -- bottom boundary of b
   55D9 DD 6E FD      [19] 2595 	ld	l,-3 (ix)
   55DC DD 66 FE      [19] 2596 	ld	h,-2 (ix)
   55DF C5            [11] 2597 	push	bc
   55E0 01 0C 00      [10] 2598 	ld	bc, #0x000c
   55E3 09            [11] 2599 	add	hl, bc
   55E4 C1            [10] 2600 	pop	bc
   55E5 56            [ 7] 2601 	ld	d, (hl)
   55E6 DD 6E F9      [19] 2602 	ld	l,-7 (ix)
   55E9 DD 66 FA      [19] 2603 	ld	h,-6 (ix)
   55EC 23            [ 6] 2604 	inc	hl
   55ED 6E            [ 7] 2605 	ld	l, (hl)
   55EE 7A            [ 4] 2606 	ld	a, d
   55EF 85            [ 4] 2607 	add	a, l
   55F0 C6 FF         [ 7] 2608 	add	a, #0xff
                           2609 ;src/entities/entities.c:591: c.y = b->ny;                    // Yes, calculate vertical collision area
                           2610 ;src/entities/entities.c:592: if ( b_bbound < a_bbound )
   55F2 DD 77 F6      [19] 2611 	ld	-10 (ix), a
   55F5 DD 96 F5      [19] 2612 	sub	a, -11 (ix)
   55F8 3E 00         [ 7] 2613 	ld	a, #0x00
   55FA 17            [ 4] 2614 	rla
   55FB DD 77 FF      [19] 2615 	ld	-1 (ix), a
                           2616 ;src/entities/entities.c:589: if ( a->ny <= b->ny ) {               // Case 1: a is up, b is down
   55FE 7A            [ 4] 2617 	ld	a, d
   55FF 93            [ 4] 2618 	sub	a, e
   5600 38 28         [12] 2619 	jr	C,00112$
                           2620 ;src/entities/entities.c:590: if ( b->ny <= a_bbound ) {         // Check if b is inside the height of a
   5602 DD 7E F5      [19] 2621 	ld	a, -11 (ix)
   5605 92            [ 4] 2622 	sub	a, d
   5606 38 48         [12] 2623 	jr	C,00113$
                           2624 ;src/entities/entities.c:591: c.y = b->ny;                    // Yes, calculate vertical collision area
   5608 21 96 75      [10] 2625 	ld	hl, #(_checkCollisionEntBlock_c_1_213 + 0x0001)
   560B 72            [ 7] 2626 	ld	(hl), d
                           2627 ;src/entities/entities.c:593: c.h = b_bbound - c.y + 1;
   560C 21 96 75      [10] 2628 	ld	hl, #(_checkCollisionEntBlock_c_1_213 + 0x0001) + 0
   560F 5E            [ 7] 2629 	ld	e, (hl)
                           2630 ;src/entities/entities.c:592: if ( b_bbound < a_bbound )
   5610 DD 7E FF      [19] 2631 	ld	a, -1 (ix)
   5613 B7            [ 4] 2632 	or	a, a
   5614 28 0A         [12] 2633 	jr	Z,00102$
                           2634 ;src/entities/entities.c:593: c.h = b_bbound - c.y + 1;
   5616 DD 7E F6      [19] 2635 	ld	a, -10 (ix)
   5619 93            [ 4] 2636 	sub	a, e
   561A 3C            [ 4] 2637 	inc	a
   561B 32 98 75      [13] 2638 	ld	(#(_checkCollisionEntBlock_c_1_213 + 0x0003)),a
   561E 18 30         [12] 2639 	jr	00113$
   5620                    2640 00102$:
                           2641 ;src/entities/entities.c:595: c.h = a_bbound - c.y + 1;
   5620 DD 7E F5      [19] 2642 	ld	a, -11 (ix)
   5623 93            [ 4] 2643 	sub	a, e
   5624 3C            [ 4] 2644 	inc	a
   5625 32 98 75      [13] 2645 	ld	(#(_checkCollisionEntBlock_c_1_213 + 0x0003)),a
   5628 18 26         [12] 2646 	jr	00113$
   562A                    2647 00112$:
                           2648 ;src/entities/entities.c:598: if ( a->ny <= b_bbound ) {         // Check if a is inside the height of b
   562A DD 7E F6      [19] 2649 	ld	a, -10 (ix)
   562D 93            [ 4] 2650 	sub	a, e
   562E 38 20         [12] 2651 	jr	C,00113$
                           2652 ;src/entities/entities.c:599: c.y = a->ny;                    // Yes, calculate vertical collision area
   5630 21 96 75      [10] 2653 	ld	hl, #(_checkCollisionEntBlock_c_1_213 + 0x0001)
   5633 73            [ 7] 2654 	ld	(hl), e
                           2655 ;src/entities/entities.c:593: c.h = b_bbound - c.y + 1;
   5634 21 96 75      [10] 2656 	ld	hl, #(_checkCollisionEntBlock_c_1_213 + 0x0001) + 0
   5637 5E            [ 7] 2657 	ld	e, (hl)
                           2658 ;src/entities/entities.c:600: if ( b_bbound < a_bbound )
   5638 DD 7E FF      [19] 2659 	ld	a, -1 (ix)
   563B B7            [ 4] 2660 	or	a, a
   563C 28 0A         [12] 2661 	jr	Z,00107$
                           2662 ;src/entities/entities.c:601: c.h = b_bbound - c.y + 1;
   563E DD 7E F6      [19] 2663 	ld	a, -10 (ix)
   5641 93            [ 4] 2664 	sub	a, e
   5642 3C            [ 4] 2665 	inc	a
   5643 32 98 75      [13] 2666 	ld	(#(_checkCollisionEntBlock_c_1_213 + 0x0003)),a
   5646 18 08         [12] 2667 	jr	00113$
   5648                    2668 00107$:
                           2669 ;src/entities/entities.c:603: c.h = a_bbound - c.y + 1;
   5648 DD 7E F5      [19] 2670 	ld	a, -11 (ix)
   564B 93            [ 4] 2671 	sub	a, e
   564C 3C            [ 4] 2672 	inc	a
   564D 32 98 75      [13] 2673 	ld	(#(_checkCollisionEntBlock_c_1_213 + 0x0003)),a
   5650                    2674 00113$:
                           2675 ;src/entities/entities.c:610: if (c.h) {
   5650 3A 98 75      [13] 2676 	ld	a, (#(_checkCollisionEntBlock_c_1_213 + 0x0003) + 0)
   5653 B7            [ 4] 2677 	or	a, a
   5654 CA F4 56      [10] 2678 	jp	Z, 00128$
                           2679 ;src/entities/entities.c:611: u8 a_rbound = a->nx + ani->width - 1; // -- right boundary limit of a
   5657 21 0B 00      [10] 2680 	ld	hl, #0x000b
   565A 09            [11] 2681 	add	hl,bc
   565B DD 75 FB      [19] 2682 	ld	-5 (ix), l
   565E DD 74 FC      [19] 2683 	ld	-4 (ix), h
   5661 4E            [ 7] 2684 	ld	c, (hl)
   5662 D1            [10] 2685 	pop	de
   5663 E1            [10] 2686 	pop	hl
   5664 E5            [11] 2687 	push	hl
   5665 D5            [11] 2688 	push	de
   5666 23            [ 6] 2689 	inc	hl
   5667 23            [ 6] 2690 	inc	hl
   5668 5E            [ 7] 2691 	ld	e, (hl)
   5669 79            [ 4] 2692 	ld	a, c
   566A 83            [ 4] 2693 	add	a, e
   566B C6 FF         [ 7] 2694 	add	a, #0xff
   566D DD 77 F6      [19] 2695 	ld	-10 (ix), a
                           2696 ;src/entities/entities.c:612: u8 b_rbound = b->nx + blk->w - 1;     // -- right boundary limit of b
   5670 DD 7E FD      [19] 2697 	ld	a, -3 (ix)
   5673 C6 0B         [ 7] 2698 	add	a, #0x0b
   5675 4F            [ 4] 2699 	ld	c, a
   5676 DD 7E FE      [19] 2700 	ld	a, -2 (ix)
   5679 CE 00         [ 7] 2701 	adc	a, #0x00
   567B 47            [ 4] 2702 	ld	b, a
   567C 0A            [ 7] 2703 	ld	a, (bc)
   567D 5F            [ 4] 2704 	ld	e, a
   567E DD 6E F9      [19] 2705 	ld	l,-7 (ix)
   5681 DD 66 FA      [19] 2706 	ld	h,-6 (ix)
   5684 56            [ 7] 2707 	ld	d, (hl)
   5685 7B            [ 4] 2708 	ld	a, e
   5686 82            [ 4] 2709 	add	a, d
   5687 C6 FF         [ 7] 2710 	add	a, #0xff
   5689 DD 77 F5      [19] 2711 	ld	-11 (ix), a
                           2712 ;src/entities/entities.c:613: c.w = 0;                          // Erase previous values and set to 0
   568C 11 97 75      [10] 2713 	ld	de, #_checkCollisionEntBlock_c_1_213 + 2
   568F AF            [ 4] 2714 	xor	a, a
   5690 12            [ 7] 2715 	ld	(de), a
                           2716 ;src/entities/entities.c:615: if ( a->nx <= b->nx ) {           // Case 1: a is left, b is right
   5691 DD 6E FB      [19] 2717 	ld	l,-5 (ix)
   5694 DD 66 FC      [19] 2718 	ld	h,-4 (ix)
   5697 7E            [ 7] 2719 	ld	a, (hl)
   5698 DD 77 FB      [19] 2720 	ld	-5 (ix), a
   569B 0A            [ 7] 2721 	ld	a, (bc)
   569C 47            [ 4] 2722 	ld	b, a
                           2723 ;src/entities/entities.c:618: if ( b_rbound < a_rbound )
   569D DD 7E F5      [19] 2724 	ld	a, -11 (ix)
   56A0 DD 96 F6      [19] 2725 	sub	a, -10 (ix)
   56A3 3E 00         [ 7] 2726 	ld	a, #0x00
   56A5 17            [ 4] 2727 	rla
   56A6 4F            [ 4] 2728 	ld	c, a
                           2729 ;src/entities/entities.c:615: if ( a->nx <= b->nx ) {           // Case 1: a is left, b is right
   56A7 78            [ 4] 2730 	ld	a, b
   56A8 DD 96 FB      [19] 2731 	sub	a, -5 (ix)
   56AB 38 22         [12] 2732 	jr	C,00125$
                           2733 ;src/entities/entities.c:616: if ( b->nx <= a_rbound ) {     // Check if b is inside the width of a
   56AD DD 7E F6      [19] 2734 	ld	a, -10 (ix)
   56B0 90            [ 4] 2735 	sub	a, b
   56B1 38 41         [12] 2736 	jr	C,00128$
                           2737 ;src/entities/entities.c:617: c.x = b->nx;                // Yes, calculate horizontal collision area
   56B3 21 95 75      [10] 2738 	ld	hl, #_checkCollisionEntBlock_c_1_213
   56B6 70            [ 7] 2739 	ld	(hl), b
                           2740 ;src/entities/entities.c:619: c.w = b_rbound - c.x + 1;
   56B7 21 95 75      [10] 2741 	ld	hl, #_checkCollisionEntBlock_c_1_213 + 0
   56BA 6E            [ 7] 2742 	ld	l, (hl)
                           2743 ;src/entities/entities.c:618: if ( b_rbound < a_rbound )
   56BB 79            [ 4] 2744 	ld	a, c
   56BC B7            [ 4] 2745 	or	a, a
   56BD 28 08         [12] 2746 	jr	Z,00115$
                           2747 ;src/entities/entities.c:619: c.w = b_rbound - c.x + 1;
   56BF DD 7E F5      [19] 2748 	ld	a, -11 (ix)
   56C2 95            [ 4] 2749 	sub	a, l
   56C3 3C            [ 4] 2750 	inc	a
   56C4 12            [ 7] 2751 	ld	(de), a
   56C5 18 2D         [12] 2752 	jr	00128$
   56C7                    2753 00115$:
                           2754 ;src/entities/entities.c:621: c.w = a_rbound - c.x + 1;
   56C7 DD 7E F6      [19] 2755 	ld	a, -10 (ix)
   56CA 95            [ 4] 2756 	sub	a, l
   56CB 3C            [ 4] 2757 	inc	a
   56CC 12            [ 7] 2758 	ld	(de), a
   56CD 18 25         [12] 2759 	jr	00128$
   56CF                    2760 00125$:
                           2761 ;src/entities/entities.c:624: if ( a->nx <= b_rbound ) {     // Check if a is inside the width of b
   56CF DD 7E F5      [19] 2762 	ld	a, -11 (ix)
   56D2 DD 96 FB      [19] 2763 	sub	a, -5 (ix)
   56D5 38 1D         [12] 2764 	jr	C,00128$
                           2765 ;src/entities/entities.c:625: c.x = a->nx;                // Yes, calculate horizontal collision area
   56D7 21 95 75      [10] 2766 	ld	hl, #_checkCollisionEntBlock_c_1_213
   56DA DD 7E FB      [19] 2767 	ld	a, -5 (ix)
   56DD 77            [ 7] 2768 	ld	(hl), a
                           2769 ;src/entities/entities.c:619: c.w = b_rbound - c.x + 1;
   56DE 21 95 75      [10] 2770 	ld	hl, #_checkCollisionEntBlock_c_1_213 + 0
   56E1 6E            [ 7] 2771 	ld	l, (hl)
                           2772 ;src/entities/entities.c:626: if ( b_rbound < a_rbound )
   56E2 79            [ 4] 2773 	ld	a, c
   56E3 B7            [ 4] 2774 	or	a, a
   56E4 28 08         [12] 2775 	jr	Z,00120$
                           2776 ;src/entities/entities.c:627: c.w = b_rbound - c.x + 1;
   56E6 DD 7E F5      [19] 2777 	ld	a, -11 (ix)
   56E9 95            [ 4] 2778 	sub	a, l
   56EA 3C            [ 4] 2779 	inc	a
   56EB 12            [ 7] 2780 	ld	(de), a
   56EC 18 06         [12] 2781 	jr	00128$
   56EE                    2782 00120$:
                           2783 ;src/entities/entities.c:629: c.w = a_rbound - c.x + 1;
   56EE DD 7E F6      [19] 2784 	ld	a, -10 (ix)
   56F1 95            [ 4] 2785 	sub	a, l
   56F2 3C            [ 4] 2786 	inc	a
   56F3 12            [ 7] 2787 	ld	(de), a
   56F4                    2788 00128$:
                           2789 ;src/entities/entities.c:634: return &c;
   56F4 21 95 75      [10] 2790 	ld	hl, #_checkCollisionEntBlock_c_1_213
   56F7 DD F9         [10] 2791 	ld	sp, ix
   56F9 DD E1         [14] 2792 	pop	ix
   56FB C9            [10] 2793 	ret
                           2794 ;src/entities/entities.c:640: u8 isOverFloor(TEntity *e) {
                           2795 ;	---------------------------------
                           2796 ; Function isOverFloor
                           2797 ; ---------------------------------
   56FC                    2798 _isOverFloor::
   56FC DD E5         [15] 2799 	push	ix
   56FE DD 21 00 00   [14] 2800 	ld	ix,#0
   5702 DD 39         [15] 2801 	add	ix,sp
   5704 F5            [11] 2802 	push	af
   5705 F5            [11] 2803 	push	af
   5706 3B            [ 6] 2804 	dec	sp
                           2805 ;src/entities/entities.c:641: u8 over = 0;                  // Value to sign if we are over a floor or not
   5707 DD 36 FF 00   [19] 2806 	ld	-1 (ix), #0x00
                           2807 ;src/entities/entities.c:642: TEntity *f = e->phys.floor;   // Get the pointer to the floor assigned to this entity
   570B DD 4E 04      [19] 2808 	ld	c,4 (ix)
   570E DD 46 05      [19] 2809 	ld	b,5 (ix)
   5711 C5            [11] 2810 	push	bc
   5712 FD E1         [14] 2811 	pop	iy
   5714 FD 7E 19      [19] 2812 	ld	a, 25 (iy)
   5717 DD 77 FD      [19] 2813 	ld	-3 (ix), a
   571A FD 7E 1A      [19] 2814 	ld	a, 26 (iy)
                           2815 ;src/entities/entities.c:645: if ( f ) {
   571D DD 77 FE      [19] 2816 	ld	-2 (ix), a
   5720 DD B6 FD      [19] 2817 	or	a,-3 (ix)
   5723 28 59         [12] 2818 	jr	Z,00105$
                           2819 ;src/entities/entities.c:646: TAnimFrame *e_a = e->graph.anim.frames[e->graph.anim.frame_id];
   5725 69            [ 4] 2820 	ld	l, c
   5726 60            [ 4] 2821 	ld	h, b
   5727 5E            [ 7] 2822 	ld	e, (hl)
   5728 23            [ 6] 2823 	inc	hl
   5729 56            [ 7] 2824 	ld	d, (hl)
   572A 69            [ 4] 2825 	ld	l, c
   572B 60            [ 4] 2826 	ld	h, b
   572C 23            [ 6] 2827 	inc	hl
   572D 23            [ 6] 2828 	inc	hl
   572E 6E            [ 7] 2829 	ld	l, (hl)
   572F 26 00         [ 7] 2830 	ld	h, #0x00
   5731 29            [11] 2831 	add	hl, hl
   5732 19            [11] 2832 	add	hl, de
   5733 7E            [ 7] 2833 	ld	a, (hl)
   5734 DD 77 FB      [19] 2834 	ld	-5 (ix), a
   5737 23            [ 6] 2835 	inc	hl
   5738 7E            [ 7] 2836 	ld	a, (hl)
   5739 DD 77 FC      [19] 2837 	ld	-4 (ix), a
                           2838 ;src/entities/entities.c:648: if ( e->x <= (f->x + f->graph.block.w) &&    // X lower  than right border of the block
   573C 69            [ 4] 2839 	ld	l, c
   573D 60            [ 4] 2840 	ld	h, b
   573E 11 09 00      [10] 2841 	ld	de, #0x0009
   5741 19            [11] 2842 	add	hl, de
   5742 5E            [ 7] 2843 	ld	e, (hl)
   5743 C1            [10] 2844 	pop	bc
   5744 E1            [10] 2845 	pop	hl
   5745 E5            [11] 2846 	push	hl
   5746 C5            [11] 2847 	push	bc
   5747 01 09 00      [10] 2848 	ld	bc, #0x0009
   574A 09            [11] 2849 	add	hl, bc
   574B 4E            [ 7] 2850 	ld	c, (hl)
   574C 06 00         [ 7] 2851 	ld	b, #0x00
   574E DD 6E FD      [19] 2852 	ld	l,-3 (ix)
   5751 DD 66 FE      [19] 2853 	ld	h,-2 (ix)
   5754 6E            [ 7] 2854 	ld	l, (hl)
   5755 26 00         [ 7] 2855 	ld	h, #0x00
   5757 09            [11] 2856 	add	hl, bc
   5758 16 00         [ 7] 2857 	ld	d, #0x00
   575A 7D            [ 4] 2858 	ld	a, l
   575B 93            [ 4] 2859 	sub	a, e
   575C 7C            [ 4] 2860 	ld	a, h
   575D 9A            [ 4] 2861 	sbc	a, d
   575E E2 63 57      [10] 2862 	jp	PO, 00120$
   5761 EE 80         [ 7] 2863 	xor	a, #0x80
   5763                    2864 00120$:
   5763 FA 7E 57      [10] 2865 	jp	M, 00105$
                           2866 ;src/entities/entities.c:649: (e->x + e_a->width) >= f->x           )  // X + width higher than left border of the block
   5766 E1            [10] 2867 	pop	hl
   5767 E5            [11] 2868 	push	hl
   5768 23            [ 6] 2869 	inc	hl
   5769 23            [ 6] 2870 	inc	hl
   576A 6E            [ 7] 2871 	ld	l, (hl)
   576B 26 00         [ 7] 2872 	ld	h, #0x00
   576D 19            [11] 2873 	add	hl, de
   576E 7D            [ 4] 2874 	ld	a, l
   576F 91            [ 4] 2875 	sub	a, c
   5770 7C            [ 4] 2876 	ld	a, h
   5771 98            [ 4] 2877 	sbc	a, b
   5772 E2 77 57      [10] 2878 	jp	PO, 00121$
   5775 EE 80         [ 7] 2879 	xor	a, #0x80
   5777                    2880 00121$:
   5777 FA 7E 57      [10] 2881 	jp	M, 00105$
                           2882 ;src/entities/entities.c:650: over = 1;
   577A DD 36 FF 01   [19] 2883 	ld	-1 (ix), #0x01
   577E                    2884 00105$:
                           2885 ;src/entities/entities.c:657: return over;
   577E DD 6E FF      [19] 2886 	ld	l, -1 (ix)
   5781 DD F9         [10] 2887 	ld	sp, ix
   5783 DD E1         [14] 2888 	pop	ix
   5785 C9            [10] 2889 	ret
                           2890 ;src/entities/entities.c:664: void setEntityLocation(TEntity *e, u8 x, u8 y, u8 vx, u8 vy, u8 eraseprev) {
                           2891 ;	---------------------------------
                           2892 ; Function setEntityLocation
                           2893 ; ---------------------------------
   5786                    2894 _setEntityLocation::
   5786 DD E5         [15] 2895 	push	ix
   5788 DD 21 00 00   [14] 2896 	ld	ix,#0
   578C DD 39         [15] 2897 	add	ix,sp
   578E F5            [11] 2898 	push	af
                           2899 ;src/entities/entities.c:666: e->npscreen   = cpct_getScreenPtr(CPCT_VMEM_START, x, y);
   578F DD 4E 04      [19] 2900 	ld	c,4 (ix)
   5792 DD 46 05      [19] 2901 	ld	b,5 (ix)
   5795 21 07 00      [10] 2902 	ld	hl, #0x0007
   5798 09            [11] 2903 	add	hl,bc
   5799 E3            [19] 2904 	ex	(sp), hl
   579A C5            [11] 2905 	push	bc
   579B DD 66 07      [19] 2906 	ld	h, 7 (ix)
   579E DD 6E 06      [19] 2907 	ld	l, 6 (ix)
   57A1 E5            [11] 2908 	push	hl
   57A2 21 00 C0      [10] 2909 	ld	hl, #0xc000
   57A5 E5            [11] 2910 	push	hl
   57A6 CD 9B 67      [17] 2911 	call	_cpct_getScreenPtr
   57A9 EB            [ 4] 2912 	ex	de,hl
   57AA C1            [10] 2913 	pop	bc
   57AB E1            [10] 2914 	pop	hl
   57AC E5            [11] 2915 	push	hl
   57AD 73            [ 7] 2916 	ld	(hl), e
   57AE 23            [ 6] 2917 	inc	hl
   57AF 72            [ 7] 2918 	ld	(hl), d
                           2919 ;src/entities/entities.c:667: e->nx = x;
   57B0 21 0B 00      [10] 2920 	ld	hl, #0x000b
   57B3 09            [11] 2921 	add	hl, bc
   57B4 DD 7E 06      [19] 2922 	ld	a, 6 (ix)
   57B7 77            [ 7] 2923 	ld	(hl), a
                           2924 ;src/entities/entities.c:668: e->ny = y;
   57B8 21 0C 00      [10] 2925 	ld	hl, #0x000c
   57BB 09            [11] 2926 	add	hl, bc
   57BC DD 7E 07      [19] 2927 	ld	a, 7 (ix)
   57BF 77            [ 7] 2928 	ld	(hl), a
                           2929 ;src/entities/entities.c:671: e->phys.x    = x  * SCALE;
   57C0 21 0F 00      [10] 2930 	ld	hl, #0x000f
   57C3 09            [11] 2931 	add	hl, bc
   57C4 DD 56 06      [19] 2932 	ld	d, 6 (ix)
   57C7 36 00         [10] 2933 	ld	(hl), #0x00
   57C9 23            [ 6] 2934 	inc	hl
   57CA 72            [ 7] 2935 	ld	(hl), d
                           2936 ;src/entities/entities.c:672: e->phys.y    = y  * SCALE;
   57CB 21 11 00      [10] 2937 	ld	hl, #0x0011
   57CE 09            [11] 2938 	add	hl, bc
   57CF DD 56 07      [19] 2939 	ld	d, 7 (ix)
   57D2 36 00         [10] 2940 	ld	(hl), #0x00
   57D4 23            [ 6] 2941 	inc	hl
   57D5 72            [ 7] 2942 	ld	(hl), d
                           2943 ;src/entities/entities.c:673: e->phys.vx   = vx * SCALE;
   57D6 21 13 00      [10] 2944 	ld	hl, #0x0013
   57D9 09            [11] 2945 	add	hl, bc
   57DA DD 56 08      [19] 2946 	ld	d, 8 (ix)
   57DD 36 00         [10] 2947 	ld	(hl), #0x00
   57DF 23            [ 6] 2948 	inc	hl
   57E0 72            [ 7] 2949 	ld	(hl), d
                           2950 ;src/entities/entities.c:674: e->phys.vy   = vy * SCALE;
   57E1 21 15 00      [10] 2951 	ld	hl, #0x0015
   57E4 09            [11] 2952 	add	hl, bc
   57E5 DD 56 09      [19] 2953 	ld	d, 9 (ix)
   57E8 36 00         [10] 2954 	ld	(hl), #0x00
   57EA 23            [ 6] 2955 	inc	hl
   57EB 72            [ 7] 2956 	ld	(hl), d
                           2957 ;src/entities/entities.c:677: if (eraseprev) {
   57EC DD 7E 0A      [19] 2958 	ld	a, 10 (ix)
   57EF B7            [ 4] 2959 	or	a, a
   57F0 28 21         [12] 2960 	jr	Z,00103$
                           2961 ;src/entities/entities.c:678: e->pscreen  = e->npscreen;
   57F2 FD 21 05 00   [14] 2962 	ld	iy, #0x0005
   57F6 FD 09         [15] 2963 	add	iy, bc
   57F8 E1            [10] 2964 	pop	hl
   57F9 E5            [11] 2965 	push	hl
   57FA 5E            [ 7] 2966 	ld	e, (hl)
   57FB 23            [ 6] 2967 	inc	hl
   57FC 56            [ 7] 2968 	ld	d, (hl)
   57FD FD 73 00      [19] 2969 	ld	0 (iy), e
   5800 FD 72 01      [19] 2970 	ld	1 (iy), d
                           2971 ;src/entities/entities.c:679: e->x = x;
   5803 21 09 00      [10] 2972 	ld	hl, #0x0009
   5806 09            [11] 2973 	add	hl, bc
   5807 DD 7E 06      [19] 2974 	ld	a, 6 (ix)
   580A 77            [ 7] 2975 	ld	(hl), a
                           2976 ;src/entities/entities.c:680: e->y = y;
   580B 21 0A 00      [10] 2977 	ld	hl, #0x000a
   580E 09            [11] 2978 	add	hl, bc
   580F DD 7E 07      [19] 2979 	ld	a, 7 (ix)
   5812 77            [ 7] 2980 	ld	(hl), a
   5813                    2981 00103$:
   5813 DD F9         [10] 2982 	ld	sp, ix
   5815 DD E1         [14] 2983 	pop	ix
   5817 C9            [10] 2984 	ret
                           2985 ;src/entities/entities.c:687: void drawAnimEntity (TEntity* e) {
                           2986 ;	---------------------------------
                           2987 ; Function drawAnimEntity
                           2988 ; ---------------------------------
   5818                    2989 _drawAnimEntity::
   5818 DD E5         [15] 2990 	push	ix
   581A DD 21 00 00   [14] 2991 	ld	ix,#0
   581E DD 39         [15] 2992 	add	ix,sp
   5820 F5            [11] 2993 	push	af
   5821 F5            [11] 2994 	push	af
                           2995 ;src/entities/entities.c:689: if ( e->draw ) {
   5822 DD 4E 04      [19] 2996 	ld	c,4 (ix)
   5825 DD 46 05      [19] 2997 	ld	b,5 (ix)
   5828 21 1B 00      [10] 2998 	ld	hl, #0x001b
   582B 09            [11] 2999 	add	hl,bc
   582C E3            [19] 3000 	ex	(sp), hl
   582D E1            [10] 3001 	pop	hl
   582E E5            [11] 3002 	push	hl
   582F 7E            [ 7] 3003 	ld	a, (hl)
   5830 B7            [ 4] 3004 	or	a, a
   5831 28 79         [12] 3005 	jr	Z,00103$
                           3006 ;src/entities/entities.c:691: TAnimation* anim  = &e->graph.anim;
   5833 69            [ 4] 3007 	ld	l, c
   5834 60            [ 4] 3008 	ld	h, b
                           3009 ;src/entities/entities.c:692: TAnimFrame* frame = anim->frames[anim->frame_id];
   5835 E5            [11] 3010 	push	hl
   5836 5E            [ 7] 3011 	ld	e, (hl)
   5837 23            [ 6] 3012 	inc	hl
   5838 56            [ 7] 3013 	ld	d, (hl)
   5839 E1            [10] 3014 	pop	hl
   583A 23            [ 6] 3015 	inc	hl
   583B 23            [ 6] 3016 	inc	hl
   583C 6E            [ 7] 3017 	ld	l, (hl)
   583D 26 00         [ 7] 3018 	ld	h, #0x00
   583F 29            [11] 3019 	add	hl, hl
   5840 19            [11] 3020 	add	hl, de
   5841 5E            [ 7] 3021 	ld	e, (hl)
   5842 23            [ 6] 3022 	inc	hl
   5843 56            [ 7] 3023 	ld	d, (hl)
                           3024 ;src/entities/entities.c:695: cpct_drawSolidBox(e->pscreen, 0x00, e->pw, e->ph);
   5844 69            [ 4] 3025 	ld	l, c
   5845 60            [ 4] 3026 	ld	h, b
   5846 C5            [11] 3027 	push	bc
   5847 01 0E 00      [10] 3028 	ld	bc, #0x000e
   584A 09            [11] 3029 	add	hl, bc
   584B C1            [10] 3030 	pop	bc
   584C 7E            [ 7] 3031 	ld	a, (hl)
   584D DD 77 FF      [19] 3032 	ld	-1 (ix), a
   5850 69            [ 4] 3033 	ld	l, c
   5851 60            [ 4] 3034 	ld	h, b
   5852 C5            [11] 3035 	push	bc
   5853 01 0D 00      [10] 3036 	ld	bc, #0x000d
   5856 09            [11] 3037 	add	hl, bc
   5857 C1            [10] 3038 	pop	bc
   5858 7E            [ 7] 3039 	ld	a, (hl)
   5859 DD 77 FE      [19] 3040 	ld	-2 (ix), a
   585C 69            [ 4] 3041 	ld	l, c
   585D 60            [ 4] 3042 	ld	h, b
   585E 23            [ 6] 3043 	inc	hl
   585F 23            [ 6] 3044 	inc	hl
   5860 23            [ 6] 3045 	inc	hl
   5861 23            [ 6] 3046 	inc	hl
   5862 23            [ 6] 3047 	inc	hl
   5863 7E            [ 7] 3048 	ld	a, (hl)
   5864 23            [ 6] 3049 	inc	hl
   5865 66            [ 7] 3050 	ld	h, (hl)
   5866 6F            [ 4] 3051 	ld	l, a
   5867 E5            [11] 3052 	push	hl
   5868 FD E1         [14] 3053 	pop	iy
   586A C5            [11] 3054 	push	bc
   586B D5            [11] 3055 	push	de
   586C DD 66 FF      [19] 3056 	ld	h, -1 (ix)
   586F DD 6E FE      [19] 3057 	ld	l, -2 (ix)
   5872 E5            [11] 3058 	push	hl
   5873 21 00 00      [10] 3059 	ld	hl, #0x0000
   5876 E5            [11] 3060 	push	hl
   5877 FD E5         [15] 3061 	push	iy
   5879 CD B4 66      [17] 3062 	call	_cpct_drawSolidBox
   587C D1            [10] 3063 	pop	de
   587D C1            [10] 3064 	pop	bc
                           3065 ;src/entities/entities.c:698: cpct_drawSprite(frame->sprite, e->npscreen, frame->width, frame->height);
   587E 6B            [ 4] 3066 	ld	l, e
   587F 62            [ 4] 3067 	ld	h, d
   5880 23            [ 6] 3068 	inc	hl
   5881 23            [ 6] 3069 	inc	hl
   5882 23            [ 6] 3070 	inc	hl
   5883 7E            [ 7] 3071 	ld	a, (hl)
   5884 DD 77 FE      [19] 3072 	ld	-2 (ix), a
   5887 6B            [ 4] 3073 	ld	l, e
   5888 62            [ 4] 3074 	ld	h, d
   5889 23            [ 6] 3075 	inc	hl
   588A 23            [ 6] 3076 	inc	hl
   588B 7E            [ 7] 3077 	ld	a, (hl)
   588C DD 77 FF      [19] 3078 	ld	-1 (ix), a
   588F 69            [ 4] 3079 	ld	l, c
   5890 60            [ 4] 3080 	ld	h, b
   5891 01 07 00      [10] 3081 	ld	bc, #0x0007
   5894 09            [11] 3082 	add	hl, bc
   5895 4E            [ 7] 3083 	ld	c, (hl)
   5896 23            [ 6] 3084 	inc	hl
   5897 46            [ 7] 3085 	ld	b, (hl)
   5898 EB            [ 4] 3086 	ex	de,hl
   5899 5E            [ 7] 3087 	ld	e, (hl)
   589A 23            [ 6] 3088 	inc	hl
   589B 56            [ 7] 3089 	ld	d, (hl)
   589C DD 66 FE      [19] 3090 	ld	h, -2 (ix)
   589F DD 6E FF      [19] 3091 	ld	l, -1 (ix)
   58A2 E5            [11] 3092 	push	hl
   58A3 C5            [11] 3093 	push	bc
   58A4 D5            [11] 3094 	push	de
   58A5 CD F5 64      [17] 3095 	call	_cpct_drawSprite
                           3096 ;src/entities/entities.c:700: e->draw = 0;
   58A8 E1            [10] 3097 	pop	hl
   58A9 E5            [11] 3098 	push	hl
   58AA 36 00         [10] 3099 	ld	(hl), #0x00
   58AC                    3100 00103$:
   58AC DD F9         [10] 3101 	ld	sp, ix
   58AE DD E1         [14] 3102 	pop	ix
   58B0 C9            [10] 3103 	ret
                           3104 ;src/entities/entities.c:707: void drawBlockEntity (TEntity* e){
                           3105 ;	---------------------------------
                           3106 ; Function drawBlockEntity
                           3107 ; ---------------------------------
   58B1                    3108 _drawBlockEntity::
   58B1 DD E5         [15] 3109 	push	ix
   58B3 DD 21 00 00   [14] 3110 	ld	ix,#0
   58B7 DD 39         [15] 3111 	add	ix,sp
   58B9 21 F2 FF      [10] 3112 	ld	hl, #-14
   58BC 39            [11] 3113 	add	hl, sp
   58BD F9            [ 6] 3114 	ld	sp, hl
                           3115 ;src/entities/entities.c:709: if ( e->draw ) {
   58BE DD 7E 04      [19] 3116 	ld	a, 4 (ix)
   58C1 DD 77 FE      [19] 3117 	ld	-2 (ix), a
   58C4 DD 7E 05      [19] 3118 	ld	a, 5 (ix)
   58C7 DD 77 FF      [19] 3119 	ld	-1 (ix), a
   58CA DD 7E FE      [19] 3120 	ld	a, -2 (ix)
   58CD C6 1B         [ 7] 3121 	add	a, #0x1b
   58CF DD 77 FC      [19] 3122 	ld	-4 (ix), a
   58D2 DD 7E FF      [19] 3123 	ld	a, -1 (ix)
   58D5 CE 00         [ 7] 3124 	adc	a, #0x00
   58D7 DD 77 FD      [19] 3125 	ld	-3 (ix), a
   58DA DD 6E FC      [19] 3126 	ld	l,-4 (ix)
   58DD DD 66 FD      [19] 3127 	ld	h,-3 (ix)
   58E0 7E            [ 7] 3128 	ld	a, (hl)
   58E1 DD 77 F7      [19] 3129 	ld	-9 (ix), a
   58E4 B7            [ 4] 3130 	or	a, a
   58E5 CA 13 5A      [10] 3131 	jp	Z, 00113$
                           3132 ;src/entities/entities.c:715: TBlock* block  = &e->graph.block;
   58E8 DD 7E FE      [19] 3133 	ld	a, -2 (ix)
   58EB DD 77 F2      [19] 3134 	ld	-14 (ix), a
   58EE DD 7E FF      [19] 3135 	ld	a, -1 (ix)
   58F1 DD 77 F3      [19] 3136 	ld	-13 (ix), a
                           3137 ;src/entities/entities.c:718: sp = e->npscreen;
   58F4 DD 7E FE      [19] 3138 	ld	a, -2 (ix)
   58F7 DD 77 F5      [19] 3139 	ld	-11 (ix), a
   58FA DD 7E FF      [19] 3140 	ld	a, -1 (ix)
   58FD DD 77 F6      [19] 3141 	ld	-10 (ix), a
   5900 DD 6E F5      [19] 3142 	ld	l,-11 (ix)
   5903 DD 66 F6      [19] 3143 	ld	h,-10 (ix)
   5906 11 07 00      [10] 3144 	ld	de, #0x0007
   5909 19            [11] 3145 	add	hl, de
   590A 7E            [ 7] 3146 	ld	a, (hl)
   590B DD 77 F5      [19] 3147 	ld	-11 (ix), a
   590E 23            [ 6] 3148 	inc	hl
   590F 7E            [ 7] 3149 	ld	a, (hl)
   5910 DD 77 F6      [19] 3150 	ld	-10 (ix), a
                           3151 ;src/entities/entities.c:719: if (e->ny <= G_minY) {
   5913 DD 7E FE      [19] 3152 	ld	a, -2 (ix)
   5916 DD 77 FA      [19] 3153 	ld	-6 (ix), a
   5919 DD 7E FF      [19] 3154 	ld	a, -1 (ix)
   591C DD 77 FB      [19] 3155 	ld	-5 (ix), a
   591F DD 6E FA      [19] 3156 	ld	l,-6 (ix)
   5922 DD 66 FB      [19] 3157 	ld	h,-5 (ix)
   5925 11 0C 00      [10] 3158 	ld	de, #0x000c
   5928 19            [11] 3159 	add	hl, de
   5929 7E            [ 7] 3160 	ld	a, (hl)
   592A DD 77 FA      [19] 3161 	ld	-6 (ix), a
   592D 3A 43 47      [13] 3162 	ld	a,(#_G_minY + 0)
   5930 DD 77 F7      [19] 3163 	ld	-9 (ix), a
                           3164 ;src/entities/entities.c:720: drawh = block->h + e->ny - G_minY;
   5933 DD 7E F2      [19] 3165 	ld	a, -14 (ix)
   5936 DD 77 F8      [19] 3166 	ld	-8 (ix), a
   5939 DD 7E F3      [19] 3167 	ld	a, -13 (ix)
   593C DD 77 F9      [19] 3168 	ld	-7 (ix), a
   593F DD 6E F8      [19] 3169 	ld	l,-8 (ix)
   5942 DD 66 F9      [19] 3170 	ld	h,-7 (ix)
   5945 23            [ 6] 3171 	inc	hl
   5946 7E            [ 7] 3172 	ld	a, (hl)
   5947 DD 77 F8      [19] 3173 	ld	-8 (ix), a
                           3174 ;src/entities/entities.c:719: if (e->ny <= G_minY) {
   594A DD 7E F7      [19] 3175 	ld	a, -9 (ix)
   594D DD 96 FA      [19] 3176 	sub	a, -6 (ix)
   5950 38 2E         [12] 3177 	jr	C,00107$
                           3178 ;src/entities/entities.c:720: drawh = block->h + e->ny - G_minY;
   5952 DD 7E F8      [19] 3179 	ld	a, -8 (ix)
   5955 DD 86 FA      [19] 3180 	add	a, -6 (ix)
   5958 4F            [ 4] 3181 	ld	c,a
   5959 DD 96 F7      [19] 3182 	sub	a, -9 (ix)
   595C DD 77 F4      [19] 3183 	ld	-12 (ix), a
                           3184 ;src/entities/entities.c:721: sp = cpct_getScreenPtr(CPCT_VMEM_START, e->nx, G_minY);
   595F DD 6E FE      [19] 3185 	ld	l,-2 (ix)
   5962 DD 66 FF      [19] 3186 	ld	h,-1 (ix)
   5965 11 0B 00      [10] 3187 	ld	de, #0x000b
   5968 19            [11] 3188 	add	hl, de
   5969 46            [ 7] 3189 	ld	b, (hl)
   596A DD 7E F7      [19] 3190 	ld	a, -9 (ix)
   596D F5            [11] 3191 	push	af
   596E 33            [ 6] 3192 	inc	sp
   596F C5            [11] 3193 	push	bc
   5970 33            [ 6] 3194 	inc	sp
   5971 21 00 C0      [10] 3195 	ld	hl, #0xc000
   5974 E5            [11] 3196 	push	hl
   5975 CD 9B 67      [17] 3197 	call	_cpct_getScreenPtr
   5978 DD 75 F5      [19] 3198 	ld	-11 (ix), l
   597B DD 74 F6      [19] 3199 	ld	-10 (ix), h
   597E 18 63         [12] 3200 	jr	00108$
   5980                    3201 00107$:
                           3202 ;src/entities/entities.c:723: if (e->ny + block->h > G_maxY) {
   5980 DD 4E FA      [19] 3203 	ld	c, -6 (ix)
   5983 06 00         [ 7] 3204 	ld	b, #0x00
   5985 DD 6E F8      [19] 3205 	ld	l, -8 (ix)
   5988 26 00         [ 7] 3206 	ld	h, #0x00
   598A 09            [11] 3207 	add	hl, bc
   598B 3A 44 47      [13] 3208 	ld	a,(#_G_maxY + 0)
   598E DD 77 F7      [19] 3209 	ld	-9 (ix), a
   5991 06 00         [ 7] 3210 	ld	b, #0x00
   5993 95            [ 4] 3211 	sub	a, l
   5994 78            [ 4] 3212 	ld	a, b
   5995 9C            [ 4] 3213 	sbc	a, h
   5996 E2 9B 59      [10] 3214 	jp	PO, 00135$
   5999 EE 80         [ 7] 3215 	xor	a, #0x80
   599B                    3216 00135$:
   599B F2 B8 59      [10] 3217 	jp	P, 00102$
                           3218 ;src/entities/entities.c:724: drawh  = G_maxY - e->ny;
   599E DD 7E F7      [19] 3219 	ld	a, -9 (ix)
   59A1 DD 96 FA      [19] 3220 	sub	a, -6 (ix)
   59A4 DD 77 F4      [19] 3221 	ld	-12 (ix), a
                           3222 ;src/entities/entities.c:725: eraseh = G_maxY - e->y;
   59A7 DD 6E FE      [19] 3223 	ld	l,-2 (ix)
   59AA DD 66 FF      [19] 3224 	ld	h,-1 (ix)
   59AD 11 0A 00      [10] 3225 	ld	de, #0x000a
   59B0 19            [11] 3226 	add	hl, de
   59B1 DD 7E F7      [19] 3227 	ld	a,-9 (ix)
   59B4 96            [ 7] 3228 	sub	a,(hl)
   59B5 4F            [ 4] 3229 	ld	c, a
   59B6 18 0A         [12] 3230 	jr	00103$
   59B8                    3231 00102$:
                           3232 ;src/entities/entities.c:727: drawh  = block->h;
   59B8 DD 7E F8      [19] 3233 	ld	a, -8 (ix)
   59BB DD 77 F8      [19] 3234 	ld	-8 (ix), a
                           3235 ;src/entities/entities.c:728: eraseh = drawh;
   59BE DD 77 F4      [19] 3236 	ld	-12 (ix), a
   59C1 4F            [ 4] 3237 	ld	c, a
   59C2                    3238 00103$:
                           3239 ;src/entities/entities.c:732: if (eraseh)
   59C2 79            [ 4] 3240 	ld	a, c
   59C3 B7            [ 4] 3241 	or	a, a
   59C4 28 1D         [12] 3242 	jr	Z,00108$
                           3243 ;src/entities/entities.c:733: cpct_drawSolidBox(e->pscreen,  0x00, block->w, eraseh);
   59C6 E1            [10] 3244 	pop	hl
   59C7 E5            [11] 3245 	push	hl
   59C8 46            [ 7] 3246 	ld	b, (hl)
   59C9 DD 6E FE      [19] 3247 	ld	l,-2 (ix)
   59CC DD 66 FF      [19] 3248 	ld	h,-1 (ix)
   59CF 11 05 00      [10] 3249 	ld	de, #0x0005
   59D2 19            [11] 3250 	add	hl, de
   59D3 5E            [ 7] 3251 	ld	e, (hl)
   59D4 23            [ 6] 3252 	inc	hl
   59D5 56            [ 7] 3253 	ld	d, (hl)
   59D6 79            [ 4] 3254 	ld	a, c
   59D7 F5            [11] 3255 	push	af
   59D8 33            [ 6] 3256 	inc	sp
   59D9 C5            [11] 3257 	push	bc
   59DA 33            [ 6] 3258 	inc	sp
   59DB 21 00 00      [10] 3259 	ld	hl, #0x0000
   59DE E5            [11] 3260 	push	hl
   59DF D5            [11] 3261 	push	de
   59E0 CD B4 66      [17] 3262 	call	_cpct_drawSolidBox
   59E3                    3263 00108$:
                           3264 ;src/entities/entities.c:737: if (drawh)
   59E3 DD 7E F4      [19] 3265 	ld	a, -12 (ix)
   59E6 B7            [ 4] 3266 	or	a, a
   59E7 28 22         [12] 3267 	jr	Z,00110$
                           3268 ;src/entities/entities.c:738: cpct_drawSolidBox(sp, block->colour, block->w, drawh);
   59E9 E1            [10] 3269 	pop	hl
   59EA E5            [11] 3270 	push	hl
   59EB 56            [ 7] 3271 	ld	d, (hl)
   59EC E1            [10] 3272 	pop	hl
   59ED E5            [11] 3273 	push	hl
   59EE 23            [ 6] 3274 	inc	hl
   59EF 23            [ 6] 3275 	inc	hl
   59F0 4E            [ 7] 3276 	ld	c, (hl)
   59F1 06 00         [ 7] 3277 	ld	b, #0x00
   59F3 E5            [11] 3278 	push	hl
   59F4 DD 6E F5      [19] 3279 	ld	l, -11 (ix)
   59F7 DD 66 F6      [19] 3280 	ld	h, -10 (ix)
   59FA E5            [11] 3281 	push	hl
   59FB FD E1         [14] 3282 	pop	iy
   59FD E1            [10] 3283 	pop	hl
   59FE DD 7E F4      [19] 3284 	ld	a, -12 (ix)
   5A01 F5            [11] 3285 	push	af
   5A02 33            [ 6] 3286 	inc	sp
   5A03 D5            [11] 3287 	push	de
   5A04 33            [ 6] 3288 	inc	sp
   5A05 C5            [11] 3289 	push	bc
   5A06 FD E5         [15] 3290 	push	iy
   5A08 CD B4 66      [17] 3291 	call	_cpct_drawSolidBox
   5A0B                    3292 00110$:
                           3293 ;src/entities/entities.c:740: e->draw = 0;
   5A0B DD 6E FC      [19] 3294 	ld	l,-4 (ix)
   5A0E DD 66 FD      [19] 3295 	ld	h,-3 (ix)
   5A11 36 00         [10] 3296 	ld	(hl), #0x00
   5A13                    3297 00113$:
   5A13 DD F9         [10] 3298 	ld	sp, ix
   5A15 DD E1         [14] 3299 	pop	ix
   5A17 C9            [10] 3300 	ret
                           3301 ;src/entities/entities.c:747: void drawAll() {
                           3302 ;	---------------------------------
                           3303 ; Function drawAll
                           3304 ; ---------------------------------
   5A18                    3305 _drawAll::
                           3306 ;src/entities/entities.c:748: u8  i = g_lastBlock;
   5A18 21 91 75      [10] 3307 	ld	hl,#_g_lastBlock + 0
   5A1B 4E            [ 7] 3308 	ld	c, (hl)
                           3309 ;src/entities/entities.c:751: while(i--) 
   5A1C                    3310 00101$:
   5A1C 41            [ 4] 3311 	ld	b, c
   5A1D 0D            [ 4] 3312 	dec	c
   5A1E 78            [ 4] 3313 	ld	a, b
   5A1F B7            [ 4] 3314 	or	a, a
   5A20 28 19         [12] 3315 	jr	Z,00103$
                           3316 ;src/entities/entities.c:752: drawBlockEntity(&g_blocks[i]);
   5A22 06 00         [ 7] 3317 	ld	b,#0x00
   5A24 69            [ 4] 3318 	ld	l, c
   5A25 60            [ 4] 3319 	ld	h, b
   5A26 29            [11] 3320 	add	hl, hl
   5A27 09            [11] 3321 	add	hl, bc
   5A28 29            [11] 3322 	add	hl, hl
   5A29 09            [11] 3323 	add	hl, bc
   5A2A 29            [11] 3324 	add	hl, hl
   5A2B 09            [11] 3325 	add	hl, bc
   5A2C 29            [11] 3326 	add	hl, hl
   5A2D 09            [11] 3327 	add	hl, bc
   5A2E 11 A1 73      [10] 3328 	ld	de, #_g_blocks
   5A31 19            [11] 3329 	add	hl, de
   5A32 C5            [11] 3330 	push	bc
   5A33 E5            [11] 3331 	push	hl
   5A34 CD B1 58      [17] 3332 	call	_drawBlockEntity
   5A37 F1            [10] 3333 	pop	af
   5A38 C1            [10] 3334 	pop	bc
   5A39 18 E1         [12] 3335 	jr	00101$
   5A3B                    3336 00103$:
                           3337 ;src/entities/entities.c:755: drawAnimEntity(&g_Character.entity);
   5A3B 21 47 47      [10] 3338 	ld	hl, #_g_Character
   5A3E E5            [11] 3339 	push	hl
   5A3F CD 18 58      [17] 3340 	call	_drawAnimEntity
   5A42 F1            [10] 3341 	pop	af
   5A43 C9            [10] 3342 	ret
                           3343 ;src/entities/entities.c:761: TEntity* newSolidBlock(u8 x, u8 y, u8 width, u8 height, u8 colour) {
                           3344 ;	---------------------------------
                           3345 ; Function newSolidBlock
                           3346 ; ---------------------------------
   5A44                    3347 _newSolidBlock::
   5A44 DD E5         [15] 3348 	push	ix
   5A46 DD 21 00 00   [14] 3349 	ld	ix,#0
   5A4A DD 39         [15] 3350 	add	ix,sp
   5A4C F5            [11] 3351 	push	af
   5A4D F5            [11] 3352 	push	af
                           3353 ;src/entities/entities.c:762: TEntity *newEnt = 0;
   5A4E 01 00 00      [10] 3354 	ld	bc, #0x0000
                           3355 ;src/entities/entities.c:765: if (g_lastBlock < g_MaxBlocks) {
   5A51 3A 91 75      [13] 3356 	ld	a,(#_g_lastBlock + 0)
   5A54 D6 10         [ 7] 3357 	sub	a, #0x10
   5A56 D2 26 5B      [10] 3358 	jp	NC, 00104$
                           3359 ;src/entities/entities.c:767: newEnt = &g_blocks[g_lastBlock];
   5A59 ED 4B 91 75   [20] 3360 	ld	bc, (_g_lastBlock)
   5A5D 06 00         [ 7] 3361 	ld	b, #0x00
   5A5F 69            [ 4] 3362 	ld	l, c
   5A60 60            [ 4] 3363 	ld	h, b
   5A61 29            [11] 3364 	add	hl, hl
   5A62 09            [11] 3365 	add	hl, bc
   5A63 29            [11] 3366 	add	hl, hl
   5A64 09            [11] 3367 	add	hl, bc
   5A65 29            [11] 3368 	add	hl, hl
   5A66 09            [11] 3369 	add	hl, bc
   5A67 29            [11] 3370 	add	hl, hl
   5A68 09            [11] 3371 	add	hl, bc
   5A69 11 A1 73      [10] 3372 	ld	de, #_g_blocks
   5A6C 19            [11] 3373 	add	hl, de
   5A6D 4D            [ 4] 3374 	ld	c, l
   5A6E 44            [ 4] 3375 	ld	b, h
                           3376 ;src/entities/entities.c:768: newEnt->graph.block.w      = width;
   5A6F DD 7E 06      [19] 3377 	ld	a, 6 (ix)
   5A72 02            [ 7] 3378 	ld	(bc), a
                           3379 ;src/entities/entities.c:769: newEnt->graph.block.h      = height;
   5A73 59            [ 4] 3380 	ld	e, c
   5A74 50            [ 4] 3381 	ld	d, b
   5A75 13            [ 6] 3382 	inc	de
   5A76 DD 7E 07      [19] 3383 	ld	a, 7 (ix)
   5A79 12            [ 7] 3384 	ld	(de), a
                           3385 ;src/entities/entities.c:770: newEnt->pw                 = width;
   5A7A 21 0D 00      [10] 3386 	ld	hl, #0x000d
   5A7D 09            [11] 3387 	add	hl, bc
   5A7E DD 7E 06      [19] 3388 	ld	a, 6 (ix)
   5A81 77            [ 7] 3389 	ld	(hl), a
                           3390 ;src/entities/entities.c:771: newEnt->ph                 = height;
   5A82 21 0E 00      [10] 3391 	ld	hl, #0x000e
   5A85 09            [11] 3392 	add	hl, bc
   5A86 DD 7E 07      [19] 3393 	ld	a, 7 (ix)
   5A89 77            [ 7] 3394 	ld	(hl), a
                           3395 ;src/entities/entities.c:772: newEnt->graph.block.colour = colour;
   5A8A 59            [ 4] 3396 	ld	e, c
   5A8B 50            [ 4] 3397 	ld	d, b
   5A8C 13            [ 6] 3398 	inc	de
   5A8D 13            [ 6] 3399 	inc	de
   5A8E DD 7E 08      [19] 3400 	ld	a, 8 (ix)
   5A91 12            [ 7] 3401 	ld	(de), a
                           3402 ;src/entities/entities.c:773: setEntityLocation(newEnt, x, y, 0, 0, 1);
   5A92 C5            [11] 3403 	push	bc
   5A93 21 00 01      [10] 3404 	ld	hl, #0x0100
   5A96 E5            [11] 3405 	push	hl
   5A97 AF            [ 4] 3406 	xor	a, a
   5A98 F5            [11] 3407 	push	af
   5A99 33            [ 6] 3408 	inc	sp
   5A9A DD 66 05      [19] 3409 	ld	h, 5 (ix)
   5A9D DD 6E 04      [19] 3410 	ld	l, 4 (ix)
   5AA0 E5            [11] 3411 	push	hl
   5AA1 C5            [11] 3412 	push	bc
   5AA2 CD 86 57      [17] 3413 	call	_setEntityLocation
   5AA5 21 07 00      [10] 3414 	ld	hl, #7
   5AA8 39            [11] 3415 	add	hl, sp
   5AA9 F9            [ 6] 3416 	ld	sp, hl
   5AAA C1            [10] 3417 	pop	bc
                           3418 ;src/entities/entities.c:774: newEnt->draw               = 1;
   5AAB 21 1B 00      [10] 3419 	ld	hl, #0x001b
   5AAE 09            [11] 3420 	add	hl, bc
   5AAF 36 01         [10] 3421 	ld	(hl), #0x01
                           3422 ;src/entities/entities.c:777: newEnt->phys.y += g_blocks[g_lastBlock-1].phys.y % SCALE;
   5AB1 21 0F 00      [10] 3423 	ld	hl, #0x000f
   5AB4 09            [11] 3424 	add	hl,bc
   5AB5 EB            [ 4] 3425 	ex	de,hl
                           3426 ;src/entities/entities.c:776: if (g_lastBlock > 0) 
   5AB6 FD 21 91 75   [14] 3427 	ld	iy, #_g_lastBlock
   5ABA FD 7E 00      [19] 3428 	ld	a, 0 (iy)
   5ABD B7            [ 4] 3429 	or	a, a
   5ABE 28 51         [12] 3430 	jr	Z,00102$
                           3431 ;src/entities/entities.c:777: newEnt->phys.y += g_blocks[g_lastBlock-1].phys.y % SCALE;
   5AC0 21 02 00      [10] 3432 	ld	hl, #0x0002
   5AC3 19            [11] 3433 	add	hl,de
   5AC4 DD 75 FE      [19] 3434 	ld	-2 (ix), l
   5AC7 DD 74 FF      [19] 3435 	ld	-1 (ix), h
   5ACA 7E            [ 7] 3436 	ld	a, (hl)
   5ACB DD 77 FC      [19] 3437 	ld	-4 (ix), a
   5ACE 23            [ 6] 3438 	inc	hl
   5ACF 7E            [ 7] 3439 	ld	a, (hl)
   5AD0 DD 77 FD      [19] 3440 	ld	-3 (ix), a
   5AD3 FD 6E 00      [19] 3441 	ld	l, 0 (iy)
   5AD6 26 00         [ 7] 3442 	ld	h, #0x00
   5AD8 2B            [ 6] 3443 	dec	hl
   5AD9 D5            [11] 3444 	push	de
   5ADA 5D            [ 4] 3445 	ld	e, l
   5ADB 54            [ 4] 3446 	ld	d, h
   5ADC 29            [11] 3447 	add	hl, hl
   5ADD 19            [11] 3448 	add	hl, de
   5ADE 29            [11] 3449 	add	hl, hl
   5ADF 19            [11] 3450 	add	hl, de
   5AE0 29            [11] 3451 	add	hl, hl
   5AE1 19            [11] 3452 	add	hl, de
   5AE2 29            [11] 3453 	add	hl, hl
   5AE3 19            [11] 3454 	add	hl, de
   5AE4 D1            [10] 3455 	pop	de
   5AE5 FD 21 A1 73   [14] 3456 	ld	iy, #_g_blocks
   5AE9 C5            [11] 3457 	push	bc
   5AEA 4D            [ 4] 3458 	ld	c, l
   5AEB 44            [ 4] 3459 	ld	b, h
   5AEC FD 09         [15] 3460 	add	iy, bc
   5AEE C1            [10] 3461 	pop	bc
   5AEF FD 6E 11      [19] 3462 	ld	l, 17 (iy)
   5AF2 26 00         [ 7] 3463 	ld	h, #0x00
   5AF4 DD 7E FC      [19] 3464 	ld	a, -4 (ix)
   5AF7 85            [ 4] 3465 	add	a, l
   5AF8 DD 77 FC      [19] 3466 	ld	-4 (ix), a
   5AFB DD 7E FD      [19] 3467 	ld	a, -3 (ix)
   5AFE 8C            [ 4] 3468 	adc	a, h
   5AFF DD 77 FD      [19] 3469 	ld	-3 (ix), a
   5B02 DD 6E FE      [19] 3470 	ld	l,-2 (ix)
   5B05 DD 66 FF      [19] 3471 	ld	h,-1 (ix)
   5B08 DD 7E FC      [19] 3472 	ld	a, -4 (ix)
   5B0B 77            [ 7] 3473 	ld	(hl), a
   5B0C 23            [ 6] 3474 	inc	hl
   5B0D DD 7E FD      [19] 3475 	ld	a, -3 (ix)
   5B10 77            [ 7] 3476 	ld	(hl), a
   5B11                    3477 00102$:
                           3478 ;src/entities/entities.c:778: newEnt->phys.bounce        = 0.85 * SCALE;
   5B11 21 08 00      [10] 3479 	ld	hl, #0x0008
   5B14 19            [11] 3480 	add	hl, de
   5B15 36 D9         [10] 3481 	ld	(hl), #0xd9
   5B17 23            [ 6] 3482 	inc	hl
   5B18 36 00         [10] 3483 	ld	(hl), #0x00
                           3484 ;src/entities/entities.c:779: newEnt->phys.vx            = 0;
   5B1A 21 04 00      [10] 3485 	ld	hl, #0x0004
   5B1D 19            [11] 3486 	add	hl, de
   5B1E AF            [ 4] 3487 	xor	a, a
   5B1F 77            [ 7] 3488 	ld	(hl), a
   5B20 23            [ 6] 3489 	inc	hl
   5B21 77            [ 7] 3490 	ld	(hl), a
                           3491 ;src/entities/entities.c:781: ++g_lastBlock;   // One more entity added to the vector
   5B22 21 91 75      [10] 3492 	ld	hl, #_g_lastBlock+0
   5B25 34            [11] 3493 	inc	(hl)
   5B26                    3494 00104$:
                           3495 ;src/entities/entities.c:784: return newEnt;
   5B26 69            [ 4] 3496 	ld	l, c
   5B27 60            [ 4] 3497 	ld	h, b
   5B28 DD F9         [10] 3498 	ld	sp, ix
   5B2A DD E1         [14] 3499 	pop	ix
   5B2C C9            [10] 3500 	ret
                           3501 ;src/entities/entities.c:790: void destroyBlock(u8 i) {
                           3502 ;	---------------------------------
                           3503 ; Function destroyBlock
                           3504 ; ---------------------------------
   5B2D                    3505 _destroyBlock::
   5B2D DD E5         [15] 3506 	push	ix
   5B2F DD 21 00 00   [14] 3507 	ld	ix,#0
   5B33 DD 39         [15] 3508 	add	ix,sp
                           3509 ;src/entities/entities.c:791: i8 nEnts = g_lastBlock - i - 1; // Entities to the right of the block
   5B35 3A 91 75      [13] 3510 	ld	a,(#_g_lastBlock + 0)
   5B38 DD 96 04      [19] 3511 	sub	a, 4 (ix)
   5B3B 4F            [ 4] 3512 	ld	c, a
   5B3C 0D            [ 4] 3513 	dec	c
                           3514 ;src/entities/entities.c:794: if (g_blocks[i].phys.vx)
   5B3D DD 5E 04      [19] 3515 	ld	e,4 (ix)
   5B40 16 00         [ 7] 3516 	ld	d,#0x00
   5B42 6B            [ 4] 3517 	ld	l, e
   5B43 62            [ 4] 3518 	ld	h, d
   5B44 29            [11] 3519 	add	hl, hl
   5B45 19            [11] 3520 	add	hl, de
   5B46 29            [11] 3521 	add	hl, hl
   5B47 19            [11] 3522 	add	hl, de
   5B48 29            [11] 3523 	add	hl, hl
   5B49 19            [11] 3524 	add	hl, de
   5B4A 29            [11] 3525 	add	hl, hl
   5B4B 19            [11] 3526 	add	hl, de
   5B4C 3E A1         [ 7] 3527 	ld	a, #<(_g_blocks)
   5B4E 85            [ 4] 3528 	add	a, l
   5B4F 5F            [ 4] 3529 	ld	e, a
   5B50 3E 73         [ 7] 3530 	ld	a, #>(_g_blocks)
   5B52 8C            [ 4] 3531 	adc	a, h
   5B53 57            [ 4] 3532 	ld	d, a
   5B54 D5            [11] 3533 	push	de
   5B55 FD E1         [14] 3534 	pop	iy
   5B57 FD 6E 13      [19] 3535 	ld	l, 19 (iy)
   5B5A FD 7E 14      [19] 3536 	ld	a, 20 (iy)
   5B5D B5            [ 4] 3537 	or	a,l
   5B5E 28 04         [12] 3538 	jr	Z,00102$
                           3539 ;src/entities/entities.c:795: --g_movingBlocks;
   5B60 21 94 75      [10] 3540 	ld	hl, #_g_movingBlocks+0
   5B63 35            [11] 3541 	dec	(hl)
   5B64                    3542 00102$:
                           3543 ;src/entities/entities.c:798: if (nEnts)
   5B64 79            [ 4] 3544 	ld	a, c
   5B65 B7            [ 4] 3545 	or	a, a
   5B66 28 2D         [12] 3546 	jr	Z,00104$
                           3547 ;src/entities/entities.c:799: cpct_memcpy(&g_blocks[i], &g_blocks[i+1], nEnts*sizeof(TEntity));
   5B68 79            [ 4] 3548 	ld	a, c
   5B69 CB 07         [ 8] 3549 	rlc	a
   5B6B 9F            [ 4] 3550 	sbc	a, a
   5B6C 47            [ 4] 3551 	ld	b, a
   5B6D 69            [ 4] 3552 	ld	l, c
   5B6E 60            [ 4] 3553 	ld	h, b
   5B6F 29            [11] 3554 	add	hl, hl
   5B70 09            [11] 3555 	add	hl, bc
   5B71 29            [11] 3556 	add	hl, hl
   5B72 09            [11] 3557 	add	hl, bc
   5B73 29            [11] 3558 	add	hl, hl
   5B74 09            [11] 3559 	add	hl, bc
   5B75 29            [11] 3560 	add	hl, hl
   5B76 09            [11] 3561 	add	hl, bc
   5B77 4D            [ 4] 3562 	ld	c, l
   5B78 44            [ 4] 3563 	ld	b, h
   5B79 DD 6E 04      [19] 3564 	ld	l, 4 (ix)
   5B7C 26 00         [ 7] 3565 	ld	h, #0x00
   5B7E 23            [ 6] 3566 	inc	hl
   5B7F D5            [11] 3567 	push	de
   5B80 5D            [ 4] 3568 	ld	e, l
   5B81 54            [ 4] 3569 	ld	d, h
   5B82 29            [11] 3570 	add	hl, hl
   5B83 19            [11] 3571 	add	hl, de
   5B84 29            [11] 3572 	add	hl, hl
   5B85 19            [11] 3573 	add	hl, de
   5B86 29            [11] 3574 	add	hl, hl
   5B87 19            [11] 3575 	add	hl, de
   5B88 29            [11] 3576 	add	hl, hl
   5B89 19            [11] 3577 	add	hl, de
   5B8A D1            [10] 3578 	pop	de
   5B8B C5            [11] 3579 	push	bc
   5B8C 01 A1 73      [10] 3580 	ld	bc, #_g_blocks
   5B8F 09            [11] 3581 	add	hl, bc
   5B90 E5            [11] 3582 	push	hl
   5B91 D5            [11] 3583 	push	de
   5B92 CD 72 66      [17] 3584 	call	_cpct_memcpy
   5B95                    3585 00104$:
                           3586 ;src/entities/entities.c:802: --g_lastBlock;
   5B95 21 91 75      [10] 3587 	ld	hl, #_g_lastBlock+0
   5B98 35            [11] 3588 	dec	(hl)
   5B99 DD E1         [14] 3589 	pop	ix
   5B9B C9            [10] 3590 	ret
                           3591 ;src/entities/entities.c:817: u8 randomCreateNewBlock(u8 y, u8 h, u8 rndinc) {
                           3592 ;	---------------------------------
                           3593 ; Function randomCreateNewBlock
                           3594 ; ---------------------------------
   5B9C                    3595 _randomCreateNewBlock::
   5B9C DD E5         [15] 3596 	push	ix
   5B9E DD 21 00 00   [14] 3597 	ld	ix,#0
   5BA2 DD 39         [15] 3598 	add	ix,sp
   5BA4 F5            [11] 3599 	push	af
                           3600 ;src/entities/entities.c:818: u8 last_y = g_blocks[g_lastBlock-1].ny;   // y coordinate of the upmost block
   5BA5 01 A1 73      [10] 3601 	ld	bc, #_g_blocks+0
   5BA8 21 91 75      [10] 3602 	ld	hl,#_g_lastBlock + 0
   5BAB 5E            [ 7] 3603 	ld	e, (hl)
   5BAC 16 00         [ 7] 3604 	ld	d, #0x00
   5BAE 1B            [ 6] 3605 	dec	de
   5BAF 6B            [ 4] 3606 	ld	l, e
   5BB0 62            [ 4] 3607 	ld	h, d
   5BB1 29            [11] 3608 	add	hl, hl
   5BB2 19            [11] 3609 	add	hl, de
   5BB3 29            [11] 3610 	add	hl, hl
   5BB4 19            [11] 3611 	add	hl, de
   5BB5 29            [11] 3612 	add	hl, hl
   5BB6 19            [11] 3613 	add	hl, de
   5BB7 29            [11] 3614 	add	hl, hl
   5BB8 19            [11] 3615 	add	hl, de
   5BB9 09            [11] 3616 	add	hl, bc
   5BBA 11 0C 00      [10] 3617 	ld	de, #0x000c
   5BBD 19            [11] 3618 	add	hl, de
   5BBE 4E            [ 7] 3619 	ld	c, (hl)
                           3620 ;src/entities/entities.c:819: u8 created = 0;                           // Flag to signal if a new block was created
   5BBF DD 36 FE 00   [19] 3621 	ld	-2 (ix), #0x00
                           3622 ;src/entities/entities.c:823: if ( (RAND_0_15(1) + MINPIXELSPACE) < last_y ) {
   5BC3 C5            [11] 3623 	push	bc
   5BC4 3E 01         [ 7] 3624 	ld	a, #0x01
   5BC6 F5            [11] 3625 	push	af
   5BC7 33            [ 6] 3626 	inc	sp
   5BC8 CD 20 45      [17] 3627 	call	_getRandomUniform
   5BCB 33            [ 6] 3628 	inc	sp
   5BCC C1            [10] 3629 	pop	bc
   5BCD 7D            [ 4] 3630 	ld	a, l
   5BCE E6 0F         [ 7] 3631 	and	a, #0x0f
   5BD0 5F            [ 4] 3632 	ld	e, a
   5BD1 16 00         [ 7] 3633 	ld	d, #0x00
   5BD3 FD 21 43 47   [14] 3634 	ld	iy, #_G_minY
   5BD7 FD 6E 00      [19] 3635 	ld	l, 0 (iy)
   5BDA 26 00         [ 7] 3636 	ld	h, #0x00
   5BDC 19            [11] 3637 	add	hl, de
   5BDD 11 0A 00      [10] 3638 	ld	de, #0x000a
   5BE0 19            [11] 3639 	add	hl, de
   5BE1 06 00         [ 7] 3640 	ld	b, #0x00
   5BE3 7D            [ 4] 3641 	ld	a, l
   5BE4 91            [ 4] 3642 	sub	a, c
   5BE5 7C            [ 4] 3643 	ld	a, h
   5BE6 98            [ 4] 3644 	sbc	a, b
   5BE7 E2 EC 5B      [10] 3645 	jp	PO, 00127$
   5BEA EE 80         [ 7] 3646 	xor	a, #0x80
   5BEC                    3647 00127$:
   5BEC F2 81 5C      [10] 3648 	jp	P, 00108$
                           3649 ;src/entities/entities.c:825: u8 x = G_minX + RAND_0_63(1);  // Random X for the new block
   5BEF 3E 01         [ 7] 3650 	ld	a, #0x01
   5BF1 F5            [11] 3651 	push	af
   5BF2 33            [ 6] 3652 	inc	sp
   5BF3 CD 20 45      [17] 3653 	call	_getRandomUniform
   5BF6 33            [ 6] 3654 	inc	sp
   5BF7 7D            [ 4] 3655 	ld	a, l
   5BF8 E6 3F         [ 7] 3656 	and	a, #0x3f
   5BFA 6F            [ 4] 3657 	ld	l, a
   5BFB FD 21 41 47   [14] 3658 	ld	iy, #_G_minX
   5BFF FD 4E 00      [19] 3659 	ld	c, 0 (iy)
   5C02 09            [11] 3660 	add	hl, bc
   5C03 5D            [ 4] 3661 	ld	e, l
                           3662 ;src/entities/entities.c:828: if (x >= G_maxX - 1) x = x - G_maxX + G_minX;
   5C04 3A 42 47      [13] 3663 	ld	a,(#_G_maxX + 0)
   5C07 DD 77 FF      [19] 3664 	ld	-1 (ix), a
   5C0A 6F            [ 4] 3665 	ld	l, a
   5C0B 26 00         [ 7] 3666 	ld	h, #0x00
   5C0D 2B            [ 6] 3667 	dec	hl
   5C0E 43            [ 4] 3668 	ld	b, e
   5C0F 16 00         [ 7] 3669 	ld	d, #0x00
   5C11 78            [ 4] 3670 	ld	a, b
   5C12 95            [ 4] 3671 	sub	a, l
   5C13 7A            [ 4] 3672 	ld	a, d
   5C14 9C            [ 4] 3673 	sbc	a, h
   5C15 E2 1A 5C      [10] 3674 	jp	PO, 00128$
   5C18 EE 80         [ 7] 3675 	xor	a, #0x80
   5C1A                    3676 00128$:
   5C1A FA 24 5C      [10] 3677 	jp	M, 00102$
   5C1D 7B            [ 4] 3678 	ld	a, e
   5C1E DD 96 FF      [19] 3679 	sub	a, -1 (ix)
   5C21 6F            [ 4] 3680 	ld	l, a
   5C22 09            [11] 3681 	add	hl, bc
   5C23 5D            [ 4] 3682 	ld	e, l
   5C24                    3683 00102$:
                           3684 ;src/entities/entities.c:831: w = RAND_0_15(rndinc) + 4;
   5C24 D5            [11] 3685 	push	de
   5C25 DD 7E 06      [19] 3686 	ld	a, 6 (ix)
   5C28 F5            [11] 3687 	push	af
   5C29 33            [ 6] 3688 	inc	sp
   5C2A CD 20 45      [17] 3689 	call	_getRandomUniform
   5C2D 33            [ 6] 3690 	inc	sp
   5C2E D1            [10] 3691 	pop	de
   5C2F 7D            [ 4] 3692 	ld	a, l
   5C30 E6 0F         [ 7] 3693 	and	a, #0x0f
   5C32 57            [ 4] 3694 	ld	d, a
   5C33 14            [ 4] 3695 	inc	d
   5C34 14            [ 4] 3696 	inc	d
   5C35 14            [ 4] 3697 	inc	d
   5C36 14            [ 4] 3698 	inc	d
                           3699 ;src/entities/entities.c:835: if (x + w > G_maxX) w = G_maxX - x;
   5C37 4B            [ 4] 3700 	ld	c, e
   5C38 06 00         [ 7] 3701 	ld	b, #0x00
   5C3A 6A            [ 4] 3702 	ld	l, d
   5C3B 26 00         [ 7] 3703 	ld	h, #0x00
   5C3D 09            [11] 3704 	add	hl, bc
   5C3E 3A 42 47      [13] 3705 	ld	a,(#_G_maxX + 0)
   5C41 DD 77 FF      [19] 3706 	ld	-1 (ix), a
   5C44 06 00         [ 7] 3707 	ld	b, #0x00
   5C46 95            [ 4] 3708 	sub	a, l
   5C47 78            [ 4] 3709 	ld	a, b
   5C48 9C            [ 4] 3710 	sbc	a, h
   5C49 E2 4E 5C      [10] 3711 	jp	PO, 00129$
   5C4C EE 80         [ 7] 3712 	xor	a, #0x80
   5C4E                    3713 00129$:
   5C4E F2 56 5C      [10] 3714 	jp	P, 00104$
   5C51 DD 7E FF      [19] 3715 	ld	a, -1 (ix)
   5C54 93            [ 4] 3716 	sub	a, e
   5C55 57            [ 4] 3717 	ld	d, a
   5C56                    3718 00104$:
                           3719 ;src/entities/entities.c:838: if ( newSolidBlock(x, y, w, h, cpct_px2byteM0(G_platfColour, G_platfColour)) )
   5C56 D5            [11] 3720 	push	de
   5C57 3A 9E 73      [13] 3721 	ld	a, (_G_platfColour)
   5C5A F5            [11] 3722 	push	af
   5C5B 33            [ 6] 3723 	inc	sp
   5C5C 3A 9E 73      [13] 3724 	ld	a, (_G_platfColour)
   5C5F F5            [11] 3725 	push	af
   5C60 33            [ 6] 3726 	inc	sp
   5C61 CD 7A 66      [17] 3727 	call	_cpct_px2byteM0
   5C64 45            [ 4] 3728 	ld	b, l
   5C65 D1            [10] 3729 	pop	de
   5C66 C5            [11] 3730 	push	bc
   5C67 33            [ 6] 3731 	inc	sp
   5C68 DD 7E 05      [19] 3732 	ld	a, 5 (ix)
   5C6B F5            [11] 3733 	push	af
   5C6C 33            [ 6] 3734 	inc	sp
   5C6D D5            [11] 3735 	push	de
   5C6E 33            [ 6] 3736 	inc	sp
   5C6F DD 56 04      [19] 3737 	ld	d, 4 (ix)
   5C72 D5            [11] 3738 	push	de
   5C73 CD 44 5A      [17] 3739 	call	_newSolidBlock
   5C76 F1            [10] 3740 	pop	af
   5C77 F1            [10] 3741 	pop	af
   5C78 33            [ 6] 3742 	inc	sp
   5C79 7C            [ 4] 3743 	ld	a, h
   5C7A B5            [ 4] 3744 	or	a,l
   5C7B 28 04         [12] 3745 	jr	Z,00108$
                           3746 ;src/entities/entities.c:839: created = 1;
   5C7D DD 36 FE 01   [19] 3747 	ld	-2 (ix), #0x01
   5C81                    3748 00108$:
                           3749 ;src/entities/entities.c:842: return created;
   5C81 DD 6E FE      [19] 3750 	ld	l, -2 (ix)
   5C84 DD F9         [10] 3751 	ld	sp, ix
   5C86 DD E1         [14] 3752 	pop	ix
   5C88 C9            [10] 3753 	ret
                           3754 	.area _CODE
                           3755 	.area _INITIALIZER
                           3756 	.area _CABS (ABS)
