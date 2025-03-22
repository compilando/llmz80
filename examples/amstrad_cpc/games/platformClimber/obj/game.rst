                              1 ;--------------------------------------------------------
                              2 ; File Created by SDCC : free open source ANSI-C Compiler
                              3 ; Version 3.6.8 #9946 (Linux)
                              4 ;--------------------------------------------------------
                              5 	.module game
                              6 	.optsdcc -mz80
                              7 	
                              8 ;--------------------------------------------------------
                              9 ; Public variables in this module
                             10 ;--------------------------------------------------------
                             11 	.globl _showGameEnd
                             12 	.globl _game
                             13 	.globl _wait4Key
                             14 	.globl _updateUser
                             15 	.globl _initializeGameScreen
                             16 	.globl _getRandomUniform
                             17 	.globl _drawFrame
                             18 	.globl _getCharacter
                             19 	.globl _drawAll
                             20 	.globl _getScore
                             21 	.globl _scrollWorld
                             22 	.globl _updateCharacter
                             23 	.globl _performAction
                             24 	.globl _initializeEntities
                             25 	.globl _cpct_getScreenPtr
                             26 	.globl _cpct_waitVSYNC
                             27 	.globl _cpct_drawStringM0
                             28 	.globl _cpct_setDrawCharM0
                             29 	.globl _cpct_drawSprite
                             30 	.globl _cpct_drawSolidBox
                             31 	.globl _cpct_px2byteM0
                             32 	.globl _cpct_isKeyPressed
                             33 	.globl _cpct_scanKeyboard_f
                             34 	.globl _cpct_memset
                             35 	.globl _sprintf
                             36 ;--------------------------------------------------------
                             37 ; special function registers
                             38 ;--------------------------------------------------------
                             39 ;--------------------------------------------------------
                             40 ; ram data
                             41 ;--------------------------------------------------------
                             42 	.area _DATA
                             43 ;--------------------------------------------------------
                             44 ; ram data
                             45 ;--------------------------------------------------------
                             46 	.area _INITIALIZED
                             47 ;--------------------------------------------------------
                             48 ; absolute external ram data
                             49 ;--------------------------------------------------------
                             50 	.area _DABS (ABS)
                             51 ;--------------------------------------------------------
                             52 ; global & static initialisations
                             53 ;--------------------------------------------------------
                             54 	.area _HOME
                             55 	.area _GSINIT
                             56 	.area _GSFINAL
                             57 	.area _GSINIT
                             58 ;--------------------------------------------------------
                             59 ; Home
                             60 ;--------------------------------------------------------
                             61 	.area _HOME
                             62 	.area _HOME
                             63 ;--------------------------------------------------------
                             64 ; code
                             65 ;--------------------------------------------------------
                             66 	.area _CODE
                             67 ;src/game.c:30: void initializeGameScreen(u16 hiscore) {
                             68 ;	---------------------------------
                             69 ; Function initializeGameScreen
                             70 ; ---------------------------------
   422C                      71 _initializeGameScreen::
   422C DD E5         [15]   72 	push	ix
   422E DD 21 00 00   [14]   73 	ld	ix,#0
   4232 DD 39         [15]   74 	add	ix,sp
   4234 21 FA FF      [10]   75 	ld	hl, #-6
   4237 39            [11]   76 	add	hl, sp
   4238 F9            [ 6]   77 	ld	sp, hl
                             78 ;src/game.c:36: cpct_clearScreen(0);
   4239 21 00 40      [10]   79 	ld	hl, #0x4000
   423C E5            [11]   80 	push	hl
   423D AF            [ 4]   81 	xor	a, a
   423E F5            [11]   82 	push	af
   423F 33            [ 6]   83 	inc	sp
   4240 26 C0         [ 7]   84 	ld	h, #0xc0
   4242 E5            [11]   85 	push	hl
   4243 CD 96 66      [17]   86 	call	_cpct_memset
                             87 ;src/game.c:41: c = cpct_px2byteM0(8,8);  // Colour pattern 8-8 (black-black)
   4246 21 08 08      [10]   88 	ld	hl, #0x0808
   4249 E5            [11]   89 	push	hl
   424A CD 7A 66      [17]   90 	call	_cpct_px2byteM0
   424D 4D            [ 4]   91 	ld	c, l
                             92 ;src/game.c:44: pscr = cpct_getScreenPtr(CPCT_VMEM_START, 54,   0);  
   424E C5            [11]   93 	push	bc
   424F 21 36 00      [10]   94 	ld	hl, #0x0036
   4252 E5            [11]   95 	push	hl
   4253 21 00 C0      [10]   96 	ld	hl, #0xc000
   4256 E5            [11]   97 	push	hl
   4257 CD 9B 67      [17]   98 	call	_cpct_getScreenPtr
   425A C1            [10]   99 	pop	bc
                            100 ;src/game.c:45: cpct_drawSolidBox(pscr, c, 26, 200);
   425B 06 00         [ 7]  101 	ld	b, #0x00
   425D 11 1A C8      [10]  102 	ld	de, #0xc81a
   4260 D5            [11]  103 	push	de
   4261 C5            [11]  104 	push	bc
   4262 E5            [11]  105 	push	hl
   4263 CD B4 66      [17]  106 	call	_cpct_drawSolidBox
                            107 ;src/game.c:48: pscr = cpct_getScreenPtr(CPCT_VMEM_START, 60,  16);   
   4266 21 3C 10      [10]  108 	ld	hl, #0x103c
   4269 E5            [11]  109 	push	hl
   426A 21 00 C0      [10]  110 	ld	hl, #0xc000
   426D E5            [11]  111 	push	hl
   426E CD 9B 67      [17]  112 	call	_cpct_getScreenPtr
                            113 ;src/game.c:49: cpct_setDrawCharM0(3, 8);
   4271 E5            [11]  114 	push	hl
   4272 01 03 08      [10]  115 	ld	bc, #0x0803
   4275 C5            [11]  116 	push	bc
   4276 CD 76 67      [17]  117 	call	_cpct_setDrawCharM0
   4279 E1            [10]  118 	pop	hl
                            119 ;src/game.c:50: cpct_drawStringM0("HI", pscr);
   427A 01 E1 42      [10]  120 	ld	bc, #___str_0+0
   427D E5            [11]  121 	push	hl
   427E C5            [11]  122 	push	bc
   427F CD 57 64      [17]  123 	call	_cpct_drawStringM0
                            124 ;src/game.c:53: pscr = cpct_getScreenPtr(CPCT_VMEM_START, 60,  24);
   4282 21 3C 18      [10]  125 	ld	hl, #0x183c
   4285 E5            [11]  126 	push	hl
   4286 21 00 C0      [10]  127 	ld	hl, #0xc000
   4289 E5            [11]  128 	push	hl
   428A CD 9B 67      [17]  129 	call	_cpct_getScreenPtr
   428D 4D            [ 4]  130 	ld	c, l
   428E 44            [ 4]  131 	ld	b, h
                            132 ;src/game.c:54: sprintf(str, "%5u", hiscore);
   428F 21 00 00      [10]  133 	ld	hl, #0x0000
   4292 39            [11]  134 	add	hl, sp
   4293 E5            [11]  135 	push	hl
   4294 FD E1         [14]  136 	pop	iy
   4296 E5            [11]  137 	push	hl
   4297 C5            [11]  138 	push	bc
   4298 DD 5E 04      [19]  139 	ld	e,4 (ix)
   429B DD 56 05      [19]  140 	ld	d,5 (ix)
   429E D5            [11]  141 	push	de
   429F 11 E4 42      [10]  142 	ld	de, #___str_1
   42A2 D5            [11]  143 	push	de
   42A3 FD E5         [15]  144 	push	iy
   42A5 CD 0C 66      [17]  145 	call	_sprintf
   42A8 21 06 00      [10]  146 	ld	hl, #6
   42AB 39            [11]  147 	add	hl, sp
   42AC F9            [ 6]  148 	ld	sp, hl
   42AD 11 0F 08      [10]  149 	ld	de, #0x080f
   42B0 D5            [11]  150 	push	de
   42B1 CD 76 67      [17]  151 	call	_cpct_setDrawCharM0
   42B4 C1            [10]  152 	pop	bc
   42B5 E1            [10]  153 	pop	hl
                            154 ;src/game.c:56: cpct_drawStringM0(str, pscr);
   42B6 C5            [11]  155 	push	bc
   42B7 E5            [11]  156 	push	hl
   42B8 CD 57 64      [17]  157 	call	_cpct_drawStringM0
                            158 ;src/game.c:59: pscr = cpct_getScreenPtr(CPCT_VMEM_START, 60, 172);
   42BB 21 3C AC      [10]  159 	ld	hl, #0xac3c
   42BE E5            [11]  160 	push	hl
   42BF 21 00 C0      [10]  161 	ld	hl, #0xc000
   42C2 E5            [11]  162 	push	hl
   42C3 CD 9B 67      [17]  163 	call	_cpct_getScreenPtr
                            164 ;src/game.c:60: cpct_drawSprite(G_credits, pscr, 20, 27);
   42C6 01 10 40      [10]  165 	ld	bc, #_G_credits+0
   42C9 11 14 1B      [10]  166 	ld	de, #0x1b14
   42CC D5            [11]  167 	push	de
   42CD E5            [11]  168 	push	hl
   42CE C5            [11]  169 	push	bc
   42CF CD F5 64      [17]  170 	call	_cpct_drawSprite
                            171 ;src/game.c:63: drawFrame(CPCT_VMEM_START, 0);
   42D2 AF            [ 4]  172 	xor	a, a
   42D3 F5            [11]  173 	push	af
   42D4 33            [ 6]  174 	inc	sp
   42D5 21 00 C0      [10]  175 	ld	hl, #0xc000
   42D8 E5            [11]  176 	push	hl
   42D9 CD 2F 5E      [17]  177 	call	_drawFrame
   42DC DD F9         [10]  178 	ld	sp,ix
   42DE DD E1         [14]  179 	pop	ix
   42E0 C9            [10]  180 	ret
   42E1                     181 ___str_0:
   42E1 48 49               182 	.ascii "HI"
   42E3 00                  183 	.db 0x00
   42E4                     184 ___str_1:
   42E4 25 35 75            185 	.ascii "%5u"
   42E7 00                  186 	.db 0x00
                            187 ;src/game.c:69: void updateUser(TCharacter* user) {
                            188 ;	---------------------------------
                            189 ; Function updateUser
                            190 ; ---------------------------------
   42E8                     191 _updateUser::
   42E8 DD E5         [15]  192 	push	ix
   42EA DD 21 00 00   [14]  193 	ld	ix,#0
   42EE DD 39         [15]  194 	add	ix,sp
                            195 ;src/game.c:71: cpct_scanKeyboard_f();
   42F0 CD E1 63      [17]  196 	call	_cpct_scanKeyboard_f
                            197 ;src/game.c:78: if ( cpct_isKeyPressed(Key_CursorUp) && user->status != es_jump ) {
   42F3 21 00 01      [10]  198 	ld	hl, #0x0100
   42F6 CD D5 63      [17]  199 	call	_cpct_isKeyPressed
   42F9 DD 4E 04      [19]  200 	ld	c,4 (ix)
   42FC DD 46 05      [19]  201 	ld	b,5 (ix)
                            202 ;src/game.c:79: performAction(user, es_jump, user->side);    // Perform the action of jumping
   42FF 79            [ 4]  203 	ld	a, c
   4300 C6 20         [ 7]  204 	add	a, #0x20
   4302 5F            [ 4]  205 	ld	e, a
   4303 78            [ 4]  206 	ld	a, b
   4304 CE 00         [ 7]  207 	adc	a, #0x00
   4306 57            [ 4]  208 	ld	d, a
                            209 ;src/game.c:78: if ( cpct_isKeyPressed(Key_CursorUp) && user->status != es_jump ) {
   4307 7D            [ 4]  210 	ld	a, l
   4308 B7            [ 4]  211 	or	a, a
   4309 28 25         [12]  212 	jr	Z,00111$
   430B C5            [11]  213 	push	bc
   430C FD E1         [14]  214 	pop	iy
   430E FD 7E 1F      [19]  215 	ld	a, 31 (iy)
   4311 D6 02         [ 7]  216 	sub	a, #0x02
   4313 28 1B         [12]  217 	jr	Z,00111$
                            218 ;src/game.c:79: performAction(user, es_jump, user->side);    // Perform the action of jumping
   4315 1A            [ 7]  219 	ld	a, (de)
   4316 57            [ 4]  220 	ld	d, a
   4317 C5            [11]  221 	push	bc
   4318 1E 02         [ 7]  222 	ld	e, #0x02
   431A D5            [11]  223 	push	de
   431B C5            [11]  224 	push	bc
   431C CD 70 47      [17]  225 	call	_performAction
   431F F1            [10]  226 	pop	af
   4320 F1            [10]  227 	pop	af
   4321 C1            [10]  228 	pop	bc
                            229 ;src/game.c:80: getRandomUniform(user->entity.nx);           // Use X coordinate of the user when jumping to forward update the random seed
   4322 C5            [11]  230 	push	bc
   4323 FD E1         [14]  231 	pop	iy
   4325 FD 46 0B      [19]  232 	ld	b, 11 (iy)
   4328 C5            [11]  233 	push	bc
   4329 33            [ 6]  234 	inc	sp
   432A CD 20 45      [17]  235 	call	_getRandomUniform
   432D 33            [ 6]  236 	inc	sp
   432E 18 68         [12]  237 	jr	00114$
   4330                     238 00111$:
                            239 ;src/game.c:83: } else if ( cpct_isKeyPressed(Key_CursorRight) )
   4330 C5            [11]  240 	push	bc
   4331 D5            [11]  241 	push	de
   4332 21 00 02      [10]  242 	ld	hl, #0x0200
   4335 CD D5 63      [17]  243 	call	_cpct_isKeyPressed
   4338 D1            [10]  244 	pop	de
   4339 C1            [10]  245 	pop	bc
   433A 7D            [ 4]  246 	ld	a, l
   433B B7            [ 4]  247 	or	a, a
   433C 28 12         [12]  248 	jr	Z,00108$
                            249 ;src/game.c:84: performAction(user, es_walk, s_right);       // Move player to the right
   433E 21 01 01      [10]  250 	ld	hl, #0x0101
   4341 E5            [11]  251 	push	hl
   4342 DD 6E 04      [19]  252 	ld	l,4 (ix)
   4345 DD 66 05      [19]  253 	ld	h,5 (ix)
   4348 E5            [11]  254 	push	hl
   4349 CD 70 47      [17]  255 	call	_performAction
   434C F1            [10]  256 	pop	af
   434D F1            [10]  257 	pop	af
   434E 18 48         [12]  258 	jr	00114$
   4350                     259 00108$:
                            260 ;src/game.c:87: else if ( cpct_isKeyPressed(Key_CursorLeft) ) 
   4350 C5            [11]  261 	push	bc
   4351 D5            [11]  262 	push	de
   4352 21 01 01      [10]  263 	ld	hl, #0x0101
   4355 CD D5 63      [17]  264 	call	_cpct_isKeyPressed
   4358 D1            [10]  265 	pop	de
   4359 C1            [10]  266 	pop	bc
   435A 7D            [ 4]  267 	ld	a, l
   435B B7            [ 4]  268 	or	a, a
   435C 28 12         [12]  269 	jr	Z,00105$
                            270 ;src/game.c:88: performAction(user, es_walk, s_left);        // Move player to the left
   435E 21 01 00      [10]  271 	ld	hl, #0x0001
   4361 E5            [11]  272 	push	hl
   4362 DD 6E 04      [19]  273 	ld	l,4 (ix)
   4365 DD 66 05      [19]  274 	ld	h,5 (ix)
   4368 E5            [11]  275 	push	hl
   4369 CD 70 47      [17]  276 	call	_performAction
   436C F1            [10]  277 	pop	af
   436D F1            [10]  278 	pop	af
   436E 18 28         [12]  279 	jr	00114$
   4370                     280 00105$:
                            281 ;src/game.c:91: else if ( cpct_isKeyPressed(Key_CursorDown) ) 
   4370 C5            [11]  282 	push	bc
   4371 D5            [11]  283 	push	de
   4372 21 00 04      [10]  284 	ld	hl, #0x0400
   4375 CD D5 63      [17]  285 	call	_cpct_isKeyPressed
   4378 7D            [ 4]  286 	ld	a, l
   4379 D1            [10]  287 	pop	de
   437A C1            [10]  288 	pop	bc
                            289 ;src/game.c:79: performAction(user, es_jump, user->side);    // Perform the action of jumping
   437B F5            [11]  290 	push	af
   437C 1A            [ 7]  291 	ld	a, (de)
   437D 57            [ 4]  292 	ld	d, a
   437E F1            [10]  293 	pop	af
                            294 ;src/game.c:91: else if ( cpct_isKeyPressed(Key_CursorDown) ) 
   437F B7            [ 4]  295 	or	a, a
   4380 28 0B         [12]  296 	jr	Z,00102$
                            297 ;src/game.c:92: performAction(user, es_moveFloor, user->side); // Enable moving floor
   4382 1E 03         [ 7]  298 	ld	e, #0x03
   4384 D5            [11]  299 	push	de
   4385 C5            [11]  300 	push	bc
   4386 CD 70 47      [17]  301 	call	_performAction
   4389 F1            [10]  302 	pop	af
   438A F1            [10]  303 	pop	af
   438B 18 0B         [12]  304 	jr	00114$
   438D                     305 00102$:
                            306 ;src/game.c:96: performAction(user, es_static, user->side);
   438D D5            [11]  307 	push	de
   438E 33            [ 6]  308 	inc	sp
   438F AF            [ 4]  309 	xor	a, a
   4390 F5            [11]  310 	push	af
   4391 33            [ 6]  311 	inc	sp
   4392 C5            [11]  312 	push	bc
   4393 CD 70 47      [17]  313 	call	_performAction
   4396 F1            [10]  314 	pop	af
   4397 F1            [10]  315 	pop	af
   4398                     316 00114$:
   4398 DD E1         [14]  317 	pop	ix
   439A C9            [10]  318 	ret
                            319 ;src/game.c:102: void wait4Key(cpct_keyID key) {
                            320 ;	---------------------------------
                            321 ; Function wait4Key
                            322 ; ---------------------------------
   439B                     323 _wait4Key::
                            324 ;src/game.c:103: do
   439B                     325 00101$:
                            326 ;src/game.c:104: cpct_scanKeyboard_f();
   439B CD E1 63      [17]  327 	call	_cpct_scanKeyboard_f
                            328 ;src/game.c:105: while( ! cpct_isKeyPressed(key) );
   439E C1            [10]  329 	pop	bc
   439F E1            [10]  330 	pop	hl
   43A0 E5            [11]  331 	push	hl
   43A1 C5            [11]  332 	push	bc
   43A2 CD D5 63      [17]  333 	call	_cpct_isKeyPressed
   43A5 7D            [ 4]  334 	ld	a, l
   43A6 B7            [ 4]  335 	or	a, a
   43A7 28 F2         [12]  336 	jr	Z,00101$
                            337 ;src/game.c:106: do
   43A9                     338 00104$:
                            339 ;src/game.c:107: cpct_scanKeyboard_f();
   43A9 CD E1 63      [17]  340 	call	_cpct_scanKeyboard_f
                            341 ;src/game.c:108: while( cpct_isKeyPressed(key) );
   43AC C1            [10]  342 	pop	bc
   43AD E1            [10]  343 	pop	hl
   43AE E5            [11]  344 	push	hl
   43AF C5            [11]  345 	push	bc
   43B0 CD D5 63      [17]  346 	call	_cpct_isKeyPressed
   43B3 7D            [ 4]  347 	ld	a, l
   43B4 B7            [ 4]  348 	or	a, a
   43B5 20 F2         [12]  349 	jr	NZ,00104$
   43B7 C9            [10]  350 	ret
                            351 ;src/game.c:114: u16 game(u16 hiscore) {
                            352 ;	---------------------------------
                            353 ; Function game
                            354 ; ---------------------------------
   43B8                     355 _game::
   43B8 3B            [ 6]  356 	dec	sp
                            357 ;src/game.c:115: u8 alive = 1;        // Main character still alive?
   43B9 FD 21 00 00   [14]  358 	ld	iy, #0
   43BD FD 39         [15]  359 	add	iy, sp
   43BF FD 36 00 01   [19]  360 	ld	0 (iy), #0x01
                            361 ;src/game.c:119: initializeGameScreen(hiscore);   // Set up Game Screen
   43C3 21 03 00      [10]  362 	ld	hl, #3
   43C6 39            [11]  363 	add	hl, sp
   43C7 4E            [ 7]  364 	ld	c, (hl)
   43C8 23            [ 6]  365 	inc	hl
   43C9 46            [ 7]  366 	ld	b, (hl)
   43CA C5            [11]  367 	push	bc
   43CB CD 2C 42      [17]  368 	call	_initializeGameScreen
   43CE F1            [10]  369 	pop	af
                            370 ;src/game.c:120: initializeEntities();            // Set up initial entities
   43CF CD 3B 46      [17]  371 	call	_initializeEntities
                            372 ;src/game.c:121: c = getCharacter();              // Get the main character
   43D2 CD 6C 47      [17]  373 	call	_getCharacter
                            374 ;src/game.c:126: while(alive) {
   43D5                     375 00101$:
   43D5 FD 21 00 00   [14]  376 	ld	iy, #0
   43D9 FD 39         [15]  377 	add	iy, sp
   43DB FD 7E 00      [19]  378 	ld	a, 0 (iy)
   43DE B7            [ 4]  379 	or	a, a
   43DF 28 25         [12]  380 	jr	Z,00103$
                            381 ;src/game.c:127: updateUser(c);                // Update user status (depending on keypresses)
   43E1 E5            [11]  382 	push	hl
   43E2 E5            [11]  383 	push	hl
   43E3 CD E8 42      [17]  384 	call	_updateUser
   43E6 F1            [10]  385 	pop	af
   43E7 CD 6C 4B      [17]  386 	call	_scrollWorld
   43EA E1            [10]  387 	pop	hl
                            388 ;src/game.c:129: alive = updateCharacter(c);   // Update character status     
   43EB E5            [11]  389 	push	hl
   43EC E5            [11]  390 	push	hl
   43ED CD D8 52      [17]  391 	call	_updateCharacter
   43F0 F1            [10]  392 	pop	af
   43F1 4D            [ 4]  393 	ld	c, l
   43F2 E1            [10]  394 	pop	hl
   43F3 FD 21 00 00   [14]  395 	ld	iy, #0
   43F7 FD 39         [15]  396 	add	iy, sp
   43F9 FD 71 00      [19]  397 	ld	0 (iy), c
                            398 ;src/game.c:130: cpct_waitVSYNC();             // Wait for VSYNC and...
   43FC E5            [11]  399 	push	hl
   43FD CD 6A 66      [17]  400 	call	_cpct_waitVSYNC
   4400 CD 18 5A      [17]  401 	call	_drawAll
   4403 E1            [10]  402 	pop	hl
   4404 18 CF         [12]  403 	jr	00101$
   4406                     404 00103$:
                            405 ;src/game.c:135: return getScore();
   4406 CD 68 47      [17]  406 	call	_getScore
   4409 33            [ 6]  407 	inc	sp
   440A C9            [10]  408 	ret
                            409 ;src/game.c:141: void showGameEnd(u16 score) {
                            410 ;	---------------------------------
                            411 ; Function showGameEnd
                            412 ; ---------------------------------
   440B                     413 _showGameEnd::
   440B DD E5         [15]  414 	push	ix
   440D DD 21 00 00   [14]  415 	ld	ix,#0
   4411 DD 39         [15]  416 	add	ix,sp
   4413 21 FA FF      [10]  417 	ld	hl, #-6
   4416 39            [11]  418 	add	hl, sp
   4417 F9            [ 6]  419 	ld	sp, hl
                            420 ;src/game.c:146: pscr = cpct_getScreenPtr(CPCT_VMEM_START,  8, 24);
   4418 21 08 18      [10]  421 	ld	hl, #0x1808
   441B E5            [11]  422 	push	hl
   441C 21 00 C0      [10]  423 	ld	hl, #0xc000
   441F E5            [11]  424 	push	hl
   4420 CD 9B 67      [17]  425 	call	_cpct_getScreenPtr
                            426 ;src/game.c:147: cpct_setDrawCharM0(6, 0);
   4423 E5            [11]  427 	push	hl
   4424 01 06 00      [10]  428 	ld	bc, #0x0006
   4427 C5            [11]  429 	push	bc
   4428 CD 76 67      [17]  430 	call	_cpct_setDrawCharM0
   442B E1            [10]  431 	pop	hl
                            432 ;src/game.c:148: cpct_drawStringM0("GAME  OVER", pscr);
   442C 01 B1 44      [10]  433 	ld	bc, #___str_2+0
   442F E5            [11]  434 	push	hl
   4430 C5            [11]  435 	push	bc
   4431 CD 57 64      [17]  436 	call	_cpct_drawStringM0
                            437 ;src/game.c:151: pscr = cpct_getScreenPtr(CPCT_VMEM_START, 16, 48);
   4434 21 10 30      [10]  438 	ld	hl, #0x3010
   4437 E5            [11]  439 	push	hl
   4438 21 00 C0      [10]  440 	ld	hl, #0xc000
   443B E5            [11]  441 	push	hl
   443C CD 9B 67      [17]  442 	call	_cpct_getScreenPtr
                            443 ;src/game.c:152: cpct_setDrawCharM0(9, 0);
   443F E5            [11]  444 	push	hl
   4440 01 09 00      [10]  445 	ld	bc, #0x0009
   4443 C5            [11]  446 	push	bc
   4444 CD 76 67      [17]  447 	call	_cpct_setDrawCharM0
   4447 E1            [10]  448 	pop	hl
                            449 ;src/game.c:153: cpct_drawStringM0(  "SCORE", pscr);
   4448 01 BC 44      [10]  450 	ld	bc, #___str_3+0
   444B E5            [11]  451 	push	hl
   444C C5            [11]  452 	push	bc
   444D CD 57 64      [17]  453 	call	_cpct_drawStringM0
                            454 ;src/game.c:156: pscr = cpct_getScreenPtr(CPCT_VMEM_START, 16, 56);
   4450 21 10 38      [10]  455 	ld	hl, #0x3810
   4453 E5            [11]  456 	push	hl
   4454 21 00 C0      [10]  457 	ld	hl, #0xc000
   4457 E5            [11]  458 	push	hl
   4458 CD 9B 67      [17]  459 	call	_cpct_getScreenPtr
   445B 4D            [ 4]  460 	ld	c, l
   445C 44            [ 4]  461 	ld	b, h
                            462 ;src/game.c:157: sprintf(str, "%5u", score);
   445D 21 00 00      [10]  463 	ld	hl, #0x0000
   4460 39            [11]  464 	add	hl, sp
   4461 E5            [11]  465 	push	hl
   4462 FD E1         [14]  466 	pop	iy
   4464 E5            [11]  467 	push	hl
   4465 C5            [11]  468 	push	bc
   4466 DD 5E 04      [19]  469 	ld	e,4 (ix)
   4469 DD 56 05      [19]  470 	ld	d,5 (ix)
   446C D5            [11]  471 	push	de
   446D 11 C2 44      [10]  472 	ld	de, #___str_4
   4470 D5            [11]  473 	push	de
   4471 FD E5         [15]  474 	push	iy
   4473 CD 0C 66      [17]  475 	call	_sprintf
   4476 21 06 00      [10]  476 	ld	hl, #6
   4479 39            [11]  477 	add	hl, sp
   447A F9            [ 6]  478 	ld	sp, hl
   447B 11 0E 00      [10]  479 	ld	de, #0x000e
   447E D5            [11]  480 	push	de
   447F CD 76 67      [17]  481 	call	_cpct_setDrawCharM0
   4482 C1            [10]  482 	pop	bc
   4483 E1            [10]  483 	pop	hl
                            484 ;src/game.c:159: cpct_drawStringM0(str, pscr);
   4484 C5            [11]  485 	push	bc
   4485 E5            [11]  486 	push	hl
   4486 CD 57 64      [17]  487 	call	_cpct_drawStringM0
                            488 ;src/game.c:162: pscr = cpct_getScreenPtr(CPCT_VMEM_START, 6, 112);
   4489 21 06 70      [10]  489 	ld	hl, #0x7006
   448C E5            [11]  490 	push	hl
   448D 21 00 C0      [10]  491 	ld	hl, #0xc000
   4490 E5            [11]  492 	push	hl
   4491 CD 9B 67      [17]  493 	call	_cpct_getScreenPtr
                            494 ;src/game.c:163: cpct_setDrawCharM0(11, 0);
   4494 E5            [11]  495 	push	hl
   4495 01 0B 00      [10]  496 	ld	bc, #0x000b
   4498 C5            [11]  497 	push	bc
   4499 CD 76 67      [17]  498 	call	_cpct_setDrawCharM0
   449C E1            [10]  499 	pop	hl
                            500 ;src/game.c:164: cpct_drawStringM0("PRESS SPACE", pscr);
   449D 01 C6 44      [10]  501 	ld	bc, #___str_5+0
   44A0 E5            [11]  502 	push	hl
   44A1 C5            [11]  503 	push	bc
   44A2 CD 57 64      [17]  504 	call	_cpct_drawStringM0
                            505 ;src/game.c:167: wait4Key(Key_Space);
   44A5 21 05 80      [10]  506 	ld	hl, #0x8005
   44A8 E5            [11]  507 	push	hl
   44A9 CD 9B 43      [17]  508 	call	_wait4Key
   44AC DD F9         [10]  509 	ld	sp,ix
   44AE DD E1         [14]  510 	pop	ix
   44B0 C9            [10]  511 	ret
   44B1                     512 ___str_2:
   44B1 47 41 4D 45 20 20   513 	.ascii "GAME  OVER"
        4F 56 45 52
   44BB 00                  514 	.db 0x00
   44BC                     515 ___str_3:
   44BC 53 43 4F 52 45      516 	.ascii "SCORE"
   44C1 00                  517 	.db 0x00
   44C2                     518 ___str_4:
   44C2 25 35 75            519 	.ascii "%5u"
   44C5 00                  520 	.db 0x00
   44C6                     521 ___str_5:
   44C6 50 52 45 53 53 20   522 	.ascii "PRESS SPACE"
        53 50 41 43 45
   44D1 00                  523 	.db 0x00
                            524 	.area _CODE
                            525 	.area _INITIALIZER
                            526 	.area _CABS (ABS)
