                              1 ;--------------------------------------------------------
                              2 ; File Created by SDCC : free open source ANSI-C Compiler
                              3 ; Version 3.6.8 #9946 (Linux)
                              4 ;--------------------------------------------------------
                              5 	.module drawing
                              6 	.optsdcc -mz80
                              7 	
                              8 ;--------------------------------------------------------
                              9 ; Public variables in this module
                             10 ;--------------------------------------------------------
                             11 	.globl _DrawUsingSpriteBackBuffer
                             12 	.globl _DrawUsingHardwareBackBuffer
                             13 	.globl _DrawDirectlyToScreen
                             14 	.globl _DrawSpriteBackBufferToScreen
                             15 	.globl _FlipBuffers
                             16 	.globl _GetSpriteBackBufferPtr
                             17 	.globl _GetBackBufferPtr
                             18 	.globl _GetScreenPtr
                             19 	.globl _cpct_waitVSYNC
                             20 	.globl _cpct_drawSpriteMaskedAlignedTable
                             21 	.globl _cpct_drawSpriteMasked
                             22 	.globl _cpct_drawSprite
                             23 	.globl _cpct_drawToSpriteBufferMaskedAlignedTable
                             24 	.globl _cpct_drawToSpriteBufferMasked
                             25 	.globl _cpct_drawToSpriteBuffer
                             26 	.globl _gDrawFunc
                             27 	.globl _gDrawFunction
                             28 	.globl _gPosScroll
                             29 	.globl _gNbTileset
                             30 	.globl _InitializeDrawing
                             31 	.globl _SelectDrawFunction
                             32 	.globl _ScrollAndDrawSpace
                             33 ;--------------------------------------------------------
                             34 ; special function registers
                             35 ;--------------------------------------------------------
                             36 ;--------------------------------------------------------
                             37 ; ram data
                             38 ;--------------------------------------------------------
                             39 	.area _DATA
   4F3E                      40 _gNbTileset::
   4F3E                      41 	.ds 1
   4F3F                      42 _gPosScroll::
   4F3F                      43 	.ds 1
   4F40                      44 _gDrawFunction::
   4F40                      45 	.ds 1
   4F41                      46 _gDrawFunc::
   4F41                      47 	.ds 2
                             48 ;--------------------------------------------------------
                             49 ; ram data
                             50 ;--------------------------------------------------------
                             51 	.area _INITIALIZED
                             52 ;--------------------------------------------------------
                             53 ; absolute external ram data
                             54 ;--------------------------------------------------------
                             55 	.area _DABS (ABS)
                             56 ;--------------------------------------------------------
                             57 ; global & static initialisations
                             58 ;--------------------------------------------------------
                             59 	.area _HOME
                             60 	.area _GSINIT
                             61 	.area _GSFINAL
                             62 	.area _GSINIT
                             63 ;--------------------------------------------------------
                             64 ; Home
                             65 ;--------------------------------------------------------
                             66 	.area _HOME
                             67 	.area _HOME
                             68 ;--------------------------------------------------------
                             69 ; code
                             70 ;--------------------------------------------------------
                             71 	.area _CODE
                             72 ;src/drawing.c:35: void InitializeDrawing() {
                             73 ;	---------------------------------
                             74 ; Function InitializeDrawing
                             75 ; ---------------------------------
   4557                      76 _InitializeDrawing::
                             77 ;src/drawing.c:36: gNbTileset = sizeof(g_tileset)/sizeof(u8*);
   4557 21 3E 4F      [10]   78 	ld	hl,#_gNbTileset + 0
   455A 36 0F         [10]   79 	ld	(hl), #0x0f
                             80 ;src/drawing.c:37: gPosScroll = 0;
   455C 21 3F 4F      [10]   81 	ld	hl,#_gPosScroll + 0
   455F 36 00         [10]   82 	ld	(hl), #0x00
                             83 ;src/drawing.c:38: SelectDrawFunction(1);
   4561 3E 01         [ 7]   84 	ld	a, #0x01
   4563 F5            [11]   85 	push	af
   4564 33            [ 6]   86 	inc	sp
   4565 CD 8A 47      [17]   87 	call	_SelectDrawFunction
   4568 33            [ 6]   88 	inc	sp
   4569 C9            [10]   89 	ret
                             90 ;src/drawing.c:47: void DrawDirectlyToScreen() {
                             91 ;	---------------------------------
                             92 ; Function DrawDirectlyToScreen
                             93 ; ---------------------------------
   456A                      94 _DrawDirectlyToScreen::
   456A DD E5         [15]   95 	push	ix
   456C DD 21 00 00   [14]   96 	ld	ix,#0
   4570 DD 39         [15]   97 	add	ix,sp
   4572 3B            [ 6]   98 	dec	sp
                             99 ;src/drawing.c:51: cpct_waitVSYNC();
   4573 CD 01 4D      [17]  100 	call	_cpct_waitVSYNC
                            101 ;src/drawing.c:56: for(i = 0; i < VIEW_W_BYTES; i++) {
   4576 DD 36 FF 00   [19]  102 	ld	-1 (ix), #0x00
   457A                     103 00102$:
                            104 ;src/drawing.c:58: u8 tile = (gPosScroll + i) % gNbTileset; 
   457A 21 3F 4F      [10]  105 	ld	hl,#_gPosScroll + 0
   457D 4E            [ 7]  106 	ld	c, (hl)
   457E 06 00         [ 7]  107 	ld	b, #0x00
   4580 DD 6E FF      [19]  108 	ld	l, -1 (ix)
   4583 26 00         [ 7]  109 	ld	h, #0x00
   4585 09            [11]  110 	add	hl,bc
   4586 4D            [ 4]  111 	ld	c, l
   4587 44            [ 4]  112 	ld	b, h
   4588 21 3E 4F      [10]  113 	ld	hl,#_gNbTileset + 0
   458B 5E            [ 7]  114 	ld	e, (hl)
   458C 16 00         [ 7]  115 	ld	d, #0x00
   458E D5            [11]  116 	push	de
   458F C5            [11]  117 	push	bc
   4590 CD DB 4D      [17]  118 	call	__modsint
   4593 F1            [10]  119 	pop	af
   4594 F1            [10]  120 	pop	af
                            121 ;src/drawing.c:59: screenPtr = GetScreenPtr(VIEW_X + i, VIEW_Y);
   4595 DD 7E FF      [19]  122 	ld	a, -1 (ix)
   4598 C6 0F         [ 7]  123 	add	a, #0x0f
   459A 47            [ 4]  124 	ld	b, a
   459B E5            [11]  125 	push	hl
   459C AF            [ 4]  126 	xor	a, a
   459D F5            [11]  127 	push	af
   459E 33            [ 6]  128 	inc	sp
   459F C5            [11]  129 	push	bc
   45A0 33            [ 6]  130 	inc	sp
   45A1 CD 02 48      [17]  131 	call	_GetScreenPtr
   45A4 F1            [10]  132 	pop	af
   45A5 EB            [ 4]  133 	ex	de,hl
   45A6 E1            [10]  134 	pop	hl
                            135 ;src/drawing.c:62: cpct_drawSprite(g_tileset[tile], screenPtr, G_BACK_00_W, G_BACK_00_H);
   45A7 26 00         [ 7]  136 	ld	h, #0x00
   45A9 29            [11]  137 	add	hl, hl
   45AA 01 B5 41      [10]  138 	ld	bc, #_g_tileset
   45AD 09            [11]  139 	add	hl, bc
   45AE 4E            [ 7]  140 	ld	c, (hl)
   45AF 23            [ 6]  141 	inc	hl
   45B0 46            [ 7]  142 	ld	b, (hl)
   45B1 21 01 3C      [10]  143 	ld	hl, #0x3c01
   45B4 E5            [11]  144 	push	hl
   45B5 D5            [11]  145 	push	de
   45B6 C5            [11]  146 	push	bc
   45B7 CD 72 4B      [17]  147 	call	_cpct_drawSprite
                            148 ;src/drawing.c:56: for(i = 0; i < VIEW_W_BYTES; i++) {
   45BA DD 34 FF      [23]  149 	inc	-1 (ix)
   45BD DD 7E FF      [19]  150 	ld	a, -1 (ix)
   45C0 D6 32         [ 7]  151 	sub	a, #0x32
   45C2 38 B6         [12]  152 	jr	C,00102$
                            153 ;src/drawing.c:68: screenPtr = GetScreenPtr(VIEW_X + POS_TITLE_X, 0);
   45C4 21 1E 00      [10]  154 	ld	hl, #0x001e
   45C7 E5            [11]  155 	push	hl
   45C8 CD 02 48      [17]  156 	call	_GetScreenPtr
   45CB F1            [10]  157 	pop	af
   45CC 4D            [ 4]  158 	ld	c, l
   45CD 44            [ 4]  159 	ld	b, h
                            160 ;src/drawing.c:69: cpct_drawSpriteMaskedAlignedTable(g_title, screenPtr, G_TITLE_W, G_TITLE_H, gMaskTable);
   45CE 11 00 7F      [10]  161 	ld	de, #_gMaskTable
   45D1 D5            [11]  162 	push	de
   45D2 21 14 10      [10]  163 	ld	hl, #0x1014
   45D5 E5            [11]  164 	push	hl
   45D6 C5            [11]  165 	push	bc
   45D7 21 00 40      [10]  166 	ld	hl, #_g_title
   45DA E5            [11]  167 	push	hl
   45DB CD 52 4E      [17]  168 	call	_cpct_drawSpriteMaskedAlignedTable
                            169 ;src/drawing.c:74: screenPtr = GetScreenPtr(VIEW_X + POS_SHIP_X, VIEW_Y + POS_SHIP_Y);
   45DE 21 27 1E      [10]  170 	ld	hl, #0x1e27
   45E1 E5            [11]  171 	push	hl
   45E2 CD 02 48      [17]  172 	call	_GetScreenPtr
   45E5 F1            [10]  173 	pop	af
                            174 ;src/drawing.c:75: cpct_drawSpriteMasked(g_ship, screenPtr, G_SHIP_W, G_SHIP_H);
   45E6 01 40 41      [10]  175 	ld	bc, #_g_ship+0
   45E9 11 05 0A      [10]  176 	ld	de, #0x0a05
   45EC D5            [11]  177 	push	de
   45ED E5            [11]  178 	push	hl
   45EE C5            [11]  179 	push	bc
   45EF CD AF 4C      [17]  180 	call	_cpct_drawSpriteMasked
                            181 ;src/drawing.c:83: const u8* fireSp = (gPosScroll % 2) ? g_fire_0 : g_fire_1;
   45F2 21 3F 4F      [10]  182 	ld	hl,#_gPosScroll+0
   45F5 CB 46         [12]  183 	bit	0, (hl)
   45F7 28 05         [12]  184 	jr	Z,00106$
   45F9 01 A4 41      [10]  185 	ld	bc, #_g_fire_0+0
   45FC 18 03         [12]  186 	jr	00107$
   45FE                     187 00106$:
   45FE 01 AA 41      [10]  188 	ld	bc, #_g_fire_1+0
   4601                     189 00107$:
                            190 ;src/drawing.c:86: screenPtr = GetScreenPtr(x, y);
   4601 C5            [11]  191 	push	bc
   4602 21 26 20      [10]  192 	ld	hl, #0x2026
   4605 E5            [11]  193 	push	hl
   4606 CD 02 48      [17]  194 	call	_GetScreenPtr
   4609 F1            [10]  195 	pop	af
   460A C1            [10]  196 	pop	bc
                            197 ;src/drawing.c:89: cpct_drawSpriteMaskedAlignedTable(fireSp, screenPtr, G_FIRE_0_W, G_FIRE_0_H, gMaskTable);
   460B 11 00 7F      [10]  198 	ld	de, #_gMaskTable
   460E D5            [11]  199 	push	de
   460F 11 01 06      [10]  200 	ld	de, #0x0601
   4612 D5            [11]  201 	push	de
   4613 E5            [11]  202 	push	hl
   4614 C5            [11]  203 	push	bc
   4615 CD 52 4E      [17]  204 	call	_cpct_drawSpriteMaskedAlignedTable
   4618 33            [ 6]  205 	inc	sp
   4619 DD E1         [14]  206 	pop	ix
   461B C9            [10]  207 	ret
                            208 ;src/drawing.c:100: void DrawUsingHardwareBackBuffer() {
                            209 ;	---------------------------------
                            210 ; Function DrawUsingHardwareBackBuffer
                            211 ; ---------------------------------
   461C                     212 _DrawUsingHardwareBackBuffer::
   461C DD E5         [15]  213 	push	ix
   461E DD 21 00 00   [14]  214 	ld	ix,#0
   4622 DD 39         [15]  215 	add	ix,sp
   4624 F5            [11]  216 	push	af
                            217 ;src/drawing.c:107: for(i = 0; i < VIEW_W_BYTES; i++) {
   4625 DD 36 FE 00   [19]  218 	ld	-2 (ix), #0x00
   4629                     219 00102$:
                            220 ;src/drawing.c:109: u8 tile = (gPosScroll + i)%gNbTileset; 
   4629 21 3F 4F      [10]  221 	ld	hl,#_gPosScroll + 0
   462C 4E            [ 7]  222 	ld	c, (hl)
   462D 06 00         [ 7]  223 	ld	b, #0x00
   462F DD 6E FE      [19]  224 	ld	l, -2 (ix)
   4632 26 00         [ 7]  225 	ld	h, #0x00
   4634 09            [11]  226 	add	hl,bc
   4635 4D            [ 4]  227 	ld	c, l
   4636 44            [ 4]  228 	ld	b, h
   4637 21 3E 4F      [10]  229 	ld	hl,#_gNbTileset + 0
   463A 5E            [ 7]  230 	ld	e, (hl)
   463B 16 00         [ 7]  231 	ld	d, #0x00
   463D D5            [11]  232 	push	de
   463E C5            [11]  233 	push	bc
   463F CD DB 4D      [17]  234 	call	__modsint
   4642 F1            [10]  235 	pop	af
   4643 F1            [10]  236 	pop	af
                            237 ;src/drawing.c:110: backScreenPtr = GetBackBufferPtr(VIEW_X + i, VIEW_Y);
   4644 DD 7E FE      [19]  238 	ld	a, -2 (ix)
   4647 C6 0F         [ 7]  239 	add	a, #0x0f
   4649 47            [ 4]  240 	ld	b, a
   464A E5            [11]  241 	push	hl
   464B AF            [ 4]  242 	xor	a, a
   464C F5            [11]  243 	push	af
   464D 33            [ 6]  244 	inc	sp
   464E C5            [11]  245 	push	bc
   464F 33            [ 6]  246 	inc	sp
   4650 CD 23 48      [17]  247 	call	_GetBackBufferPtr
   4653 F1            [10]  248 	pop	af
   4654 EB            [ 4]  249 	ex	de,hl
   4655 E1            [10]  250 	pop	hl
                            251 ;src/drawing.c:113: cpct_drawSprite(g_tileset[tile], backScreenPtr, G_BACK_00_W, G_BACK_00_H);     
   4656 26 00         [ 7]  252 	ld	h, #0x00
   4658 29            [11]  253 	add	hl, hl
   4659 01 B5 41      [10]  254 	ld	bc, #_g_tileset
   465C 09            [11]  255 	add	hl, bc
   465D 4E            [ 7]  256 	ld	c, (hl)
   465E 23            [ 6]  257 	inc	hl
   465F 46            [ 7]  258 	ld	b, (hl)
   4660 21 01 3C      [10]  259 	ld	hl, #0x3c01
   4663 E5            [11]  260 	push	hl
   4664 D5            [11]  261 	push	de
   4665 C5            [11]  262 	push	bc
   4666 CD 72 4B      [17]  263 	call	_cpct_drawSprite
                            264 ;src/drawing.c:107: for(i = 0; i < VIEW_W_BYTES; i++) {
   4669 DD 34 FE      [23]  265 	inc	-2 (ix)
   466C DD 7E FE      [19]  266 	ld	a, -2 (ix)
   466F D6 32         [ 7]  267 	sub	a, #0x32
   4671 38 B6         [12]  268 	jr	C,00102$
                            269 ;src/drawing.c:119: backScreenPtr = GetBackBufferPtr(VIEW_X + POS_TITLE_X, 0);
   4673 21 1E 00      [10]  270 	ld	hl, #0x001e
   4676 E5            [11]  271 	push	hl
   4677 CD 23 48      [17]  272 	call	_GetBackBufferPtr
   467A F1            [10]  273 	pop	af
   467B 4D            [ 4]  274 	ld	c, l
   467C 44            [ 4]  275 	ld	b, h
                            276 ;src/drawing.c:120: cpct_drawSpriteMaskedAlignedTable(g_title, backScreenPtr, G_TITLE_W, G_TITLE_H, gMaskTable);
   467D 11 00 7F      [10]  277 	ld	de, #_gMaskTable
   4680 D5            [11]  278 	push	de
   4681 21 14 10      [10]  279 	ld	hl, #0x1014
   4684 E5            [11]  280 	push	hl
   4685 C5            [11]  281 	push	bc
   4686 21 00 40      [10]  282 	ld	hl, #_g_title
   4689 E5            [11]  283 	push	hl
   468A CD 52 4E      [17]  284 	call	_cpct_drawSpriteMaskedAlignedTable
                            285 ;src/drawing.c:125: backScreenPtr = GetBackBufferPtr(VIEW_X + POS_SHIP_X, VIEW_Y + POS_SHIP_Y);
   468D 21 27 1E      [10]  286 	ld	hl, #0x1e27
   4690 E5            [11]  287 	push	hl
   4691 CD 23 48      [17]  288 	call	_GetBackBufferPtr
   4694 F1            [10]  289 	pop	af
                            290 ;src/drawing.c:126: cpct_drawSpriteMasked(g_ship, backScreenPtr, G_SHIP_W, G_SHIP_H);
   4695 01 40 41      [10]  291 	ld	bc, #_g_ship+0
   4698 11 05 0A      [10]  292 	ld	de, #0x0a05
   469B D5            [11]  293 	push	de
   469C E5            [11]  294 	push	hl
   469D C5            [11]  295 	push	bc
   469E CD AF 4C      [17]  296 	call	_cpct_drawSpriteMasked
                            297 ;src/drawing.c:133: const u8* fireSp = (gPosScroll % 2) == 0 ? g_fire_0 : g_fire_1;
   46A1 21 3F 4F      [10]  298 	ld	hl,#_gPosScroll+0
   46A4 CB 46         [12]  299 	bit	0, (hl)
   46A6 20 05         [12]  300 	jr	NZ,00106$
   46A8 01 A4 41      [10]  301 	ld	bc, #_g_fire_0+0
   46AB 18 03         [12]  302 	jr	00107$
   46AD                     303 00106$:
   46AD 01 AA 41      [10]  304 	ld	bc, #_g_fire_1+0
   46B0                     305 00107$:
                            306 ;src/drawing.c:136: backScreenPtr = GetBackBufferPtr(x, y);
   46B0 C5            [11]  307 	push	bc
   46B1 21 26 20      [10]  308 	ld	hl, #0x2026
   46B4 E5            [11]  309 	push	hl
   46B5 CD 23 48      [17]  310 	call	_GetBackBufferPtr
   46B8 F1            [10]  311 	pop	af
   46B9 C1            [10]  312 	pop	bc
                            313 ;src/drawing.c:138: cpct_drawSpriteMaskedAlignedTable(fireSp, backScreenPtr, G_FIRE_0_W, G_FIRE_0_H, gMaskTable);
   46BA 11 00 7F      [10]  314 	ld	de, #_gMaskTable
   46BD D5            [11]  315 	push	de
   46BE 11 01 06      [10]  316 	ld	de, #0x0601
   46C1 D5            [11]  317 	push	de
   46C2 E5            [11]  318 	push	hl
   46C3 C5            [11]  319 	push	bc
   46C4 CD 52 4E      [17]  320 	call	_cpct_drawSpriteMaskedAlignedTable
                            321 ;src/drawing.c:143: FlipBuffers();
   46C7 CD E3 47      [17]  322 	call	_FlipBuffers
   46CA DD F9         [10]  323 	ld	sp, ix
   46CC DD E1         [14]  324 	pop	ix
   46CE C9            [10]  325 	ret
                            326 ;src/drawing.c:157: void DrawUsingSpriteBackBuffer() {
                            327 ;	---------------------------------
                            328 ; Function DrawUsingSpriteBackBuffer
                            329 ; ---------------------------------
   46CF                     330 _DrawUsingSpriteBackBuffer::
   46CF DD E5         [15]  331 	push	ix
   46D1 3B            [ 6]  332 	dec	sp
                            333 ;src/drawing.c:164: for(i = 0; i < VIEW_W_BYTES; i++) {
   46D2 06 00         [ 7]  334 	ld	b, #0x00
   46D4                     335 00102$:
                            336 ;src/drawing.c:166: u8 tile = (gPosScroll + i)%gNbTileset;
   46D4 21 3F 4F      [10]  337 	ld	hl,#_gPosScroll + 0
   46D7 5E            [ 7]  338 	ld	e, (hl)
   46D8 16 00         [ 7]  339 	ld	d, #0x00
   46DA 68            [ 4]  340 	ld	l, b
   46DB 26 00         [ 7]  341 	ld	h, #0x00
   46DD 19            [11]  342 	add	hl,de
   46DE EB            [ 4]  343 	ex	de,hl
   46DF FD 21 3E 4F   [14]  344 	ld	iy, #_gNbTileset
   46E3 FD 6E 00      [19]  345 	ld	l, 0 (iy)
   46E6 26 00         [ 7]  346 	ld	h, #0x00
   46E8 C5            [11]  347 	push	bc
   46E9 E5            [11]  348 	push	hl
   46EA D5            [11]  349 	push	de
   46EB CD DB 4D      [17]  350 	call	__modsint
   46EE F1            [10]  351 	pop	af
   46EF F1            [10]  352 	pop	af
   46F0 C1            [10]  353 	pop	bc
   46F1 4D            [ 4]  354 	ld	c, l
                            355 ;src/drawing.c:167: backBufferPtr = GetSpriteBackBufferPtr(i, 0);
   46F2 C5            [11]  356 	push	bc
   46F3 AF            [ 4]  357 	xor	a, a
   46F4 F5            [11]  358 	push	af
   46F5 33            [ 6]  359 	inc	sp
   46F6 C5            [11]  360 	push	bc
   46F7 33            [ 6]  361 	inc	sp
   46F8 CD 44 48      [17]  362 	call	_GetSpriteBackBufferPtr
   46FB F1            [10]  363 	pop	af
   46FC EB            [ 4]  364 	ex	de,hl
   46FD C1            [10]  365 	pop	bc
                            366 ;src/drawing.c:170: cpct_drawToSpriteBuffer(VIEW_W_BYTES, backBufferPtr, G_BACK_00_W, G_BACK_00_H, g_tileset[tile]);
   46FE 69            [ 4]  367 	ld	l, c
   46FF 26 00         [ 7]  368 	ld	h, #0x00
   4701 29            [11]  369 	add	hl, hl
   4702 3E B5         [ 7]  370 	ld	a, #<(_g_tileset)
   4704 85            [ 4]  371 	add	a, l
   4705 6F            [ 4]  372 	ld	l, a
   4706 3E 41         [ 7]  373 	ld	a, #>(_g_tileset)
   4708 8C            [ 4]  374 	adc	a, h
   4709 67            [ 4]  375 	ld	h, a
   470A 7E            [ 7]  376 	ld	a, (hl)
   470B 23            [ 6]  377 	inc	hl
   470C 66            [ 7]  378 	ld	h, (hl)
   470D 6F            [ 4]  379 	ld	l, a
   470E C5            [11]  380 	push	bc
   470F E5            [11]  381 	push	hl
   4710 21 01 3C      [10]  382 	ld	hl, #0x3c01
   4713 E5            [11]  383 	push	hl
   4714 D5            [11]  384 	push	de
   4715 21 32 00      [10]  385 	ld	hl, #0x0032
   4718 E5            [11]  386 	push	hl
   4719 CD E3 4C      [17]  387 	call	_cpct_drawToSpriteBuffer
   471C C1            [10]  388 	pop	bc
                            389 ;src/drawing.c:164: for(i = 0; i < VIEW_W_BYTES; i++) {
   471D 04            [ 4]  390 	inc	b
   471E 78            [ 4]  391 	ld	a, b
   471F D6 32         [ 7]  392 	sub	a, #0x32
   4721 38 B1         [12]  393 	jr	C,00102$
                            394 ;src/drawing.c:176: backBufferPtr = GetSpriteBackBufferPtr(POS_TITLE_X, 0);
   4723 21 0F 00      [10]  395 	ld	hl, #0x000f
   4726 E5            [11]  396 	push	hl
   4727 CD 44 48      [17]  397 	call	_GetSpriteBackBufferPtr
   472A F1            [10]  398 	pop	af
   472B 4D            [ 4]  399 	ld	c, l
   472C 44            [ 4]  400 	ld	b, h
                            401 ;src/drawing.c:177: cpct_drawToSpriteBufferMaskedAlignedTable(VIEW_W_BYTES, backBufferPtr, G_TITLE_W, G_TITLE_H, g_title, gMaskTable);
   472D 21 00 7F      [10]  402 	ld	hl, #_gMaskTable
   4730 11 00 40      [10]  403 	ld	de, #_g_title+0
   4733 E5            [11]  404 	push	hl
   4734 D5            [11]  405 	push	de
   4735 21 14 10      [10]  406 	ld	hl, #0x1014
   4738 E5            [11]  407 	push	hl
   4739 C5            [11]  408 	push	bc
   473A 21 32 00      [10]  409 	ld	hl, #0x0032
   473D E5            [11]  410 	push	hl
   473E CD 71 4C      [17]  411 	call	_cpct_drawToSpriteBufferMaskedAlignedTable
                            412 ;src/drawing.c:182: backBufferPtr = GetSpriteBackBufferPtr(POS_SHIP_X, POS_SHIP_Y);
   4741 21 18 1E      [10]  413 	ld	hl, #0x1e18
   4744 E5            [11]  414 	push	hl
   4745 CD 44 48      [17]  415 	call	_GetSpriteBackBufferPtr
   4748 F1            [10]  416 	pop	af
                            417 ;src/drawing.c:183: cpct_drawToSpriteBufferMasked(VIEW_W_BYTES, backBufferPtr, G_SHIP_W, G_SHIP_H, g_ship);
   4749 01 40 41      [10]  418 	ld	bc, #_g_ship+0
   474C C5            [11]  419 	push	bc
   474D 01 05 0A      [10]  420 	ld	bc, #0x0a05
   4750 C5            [11]  421 	push	bc
   4751 E5            [11]  422 	push	hl
   4752 21 32 00      [10]  423 	ld	hl, #0x0032
   4755 E5            [11]  424 	push	hl
   4756 CD 8D 4E      [17]  425 	call	_cpct_drawToSpriteBufferMasked
                            426 ;src/drawing.c:190: const u8* fireSp = (gPosScroll % 2) == 0 ? g_fire_0 : g_fire_1;
   4759 21 3F 4F      [10]  427 	ld	hl,#_gPosScroll+0
   475C CB 46         [12]  428 	bit	0, (hl)
   475E 20 05         [12]  429 	jr	NZ,00106$
   4760 01 A4 41      [10]  430 	ld	bc, #_g_fire_0+0
   4763 18 03         [12]  431 	jr	00107$
   4765                     432 00106$:
   4765 01 AA 41      [10]  433 	ld	bc, #_g_fire_1+0
   4768                     434 00107$:
                            435 ;src/drawing.c:193: backBufferPtr = GetSpriteBackBufferPtr(x, y);
   4768 C5            [11]  436 	push	bc
   4769 21 17 20      [10]  437 	ld	hl, #0x2017
   476C E5            [11]  438 	push	hl
   476D CD 44 48      [17]  439 	call	_GetSpriteBackBufferPtr
   4770 F1            [10]  440 	pop	af
   4771 C1            [10]  441 	pop	bc
                            442 ;src/drawing.c:195: cpct_drawToSpriteBufferMaskedAlignedTable(VIEW_W_BYTES, backBufferPtr, G_FIRE_0_W, G_FIRE_0_H, fireSp, gMaskTable);
   4772 11 00 7F      [10]  443 	ld	de, #_gMaskTable
   4775 D5            [11]  444 	push	de
   4776 C5            [11]  445 	push	bc
   4777 01 01 06      [10]  446 	ld	bc, #0x0601
   477A C5            [11]  447 	push	bc
   477B E5            [11]  448 	push	hl
   477C 21 32 00      [10]  449 	ld	hl, #0x0032
   477F E5            [11]  450 	push	hl
   4780 CD 71 4C      [17]  451 	call	_cpct_drawToSpriteBufferMaskedAlignedTable
                            452 ;src/drawing.c:199: DrawSpriteBackBufferToScreen();
   4783 CD 69 48      [17]  453 	call	_DrawSpriteBackBufferToScreen
   4786 33            [ 6]  454 	inc	sp
   4787 DD E1         [14]  455 	pop	ix
   4789 C9            [10]  456 	ret
                            457 ;src/drawing.c:207: void SelectDrawFunction(u8 drawFuncNb) {
                            458 ;	---------------------------------
                            459 ; Function SelectDrawFunction
                            460 ; ---------------------------------
   478A                     461 _SelectDrawFunction::
                            462 ;src/drawing.c:209: switch(drawFuncNb) {
   478A FD 21 02 00   [14]  463 	ld	iy, #2
   478E FD 39         [15]  464 	add	iy, sp
   4790 FD 7E 00      [19]  465 	ld	a, 0 (iy)
   4793 3D            [ 4]  466 	dec	a
   4794 28 09         [12]  467 	jr	Z,00101$
   4796 FD 7E 00      [19]  468 	ld	a, 0 (iy)
   4799 D6 02         [ 7]  469 	sub	a, #0x02
   479B 28 0F         [12]  470 	jr	Z,00102$
   479D 18 1A         [12]  471 	jr	00103$
                            472 ;src/drawing.c:210: case 1:  gDrawFunc = DrawDirectlyToScreen;         break;
   479F                     473 00101$:
   479F FD 21 41 4F   [14]  474 	ld	iy, #_gDrawFunc
   47A3 FD 36 00 6A   [19]  475 	ld	0 (iy), #<(_DrawDirectlyToScreen)
   47A7 FD 36 01 45   [19]  476 	ld	1 (iy), #>(_DrawDirectlyToScreen)
   47AB C9            [10]  477 	ret
                            478 ;src/drawing.c:211: case 2:  gDrawFunc = DrawUsingHardwareBackBuffer;  break;
   47AC                     479 00102$:
   47AC FD 21 41 4F   [14]  480 	ld	iy, #_gDrawFunc
   47B0 FD 36 00 1C   [19]  481 	ld	0 (iy), #<(_DrawUsingHardwareBackBuffer)
   47B4 FD 36 01 46   [19]  482 	ld	1 (iy), #>(_DrawUsingHardwareBackBuffer)
   47B8 C9            [10]  483 	ret
                            484 ;src/drawing.c:212: default: gDrawFunc = DrawUsingSpriteBackBuffer;
   47B9                     485 00103$:
   47B9 FD 21 41 4F   [14]  486 	ld	iy, #_gDrawFunc
   47BD FD 36 00 CF   [19]  487 	ld	0 (iy), #<(_DrawUsingSpriteBackBuffer)
   47C1 FD 36 01 46   [19]  488 	ld	1 (iy), #>(_DrawUsingSpriteBackBuffer)
                            489 ;src/drawing.c:213: }
   47C5 C9            [10]  490 	ret
                            491 ;src/drawing.c:223: void ScrollAndDrawSpace() { 
                            492 ;	---------------------------------
                            493 ; Function ScrollAndDrawSpace
                            494 ; ---------------------------------
   47C6                     495 _ScrollAndDrawSpace::
                            496 ;src/drawing.c:225: gPosScroll++;
   47C6 21 3F 4F      [10]  497 	ld	hl, #_gPosScroll+0
   47C9 34            [11]  498 	inc	(hl)
                            499 ;src/drawing.c:226: gDrawFunc(); 
   47CA 2A 41 4F      [16]  500 	ld	hl, (_gDrawFunc)
   47CD C3 E2 4C      [10]  501 	jp  ___sdcc_call_hl
                            502 	.area _CODE
                            503 	.area _INITIALIZER
                            504 	.area _CABS (ABS)
