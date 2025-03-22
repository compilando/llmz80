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
                             11 	.globl _DrawBackground
                             12 	.globl _DrawCloud
                             13 	.globl _DrawBalloon
                             14 	.globl _DeleteBalloons
                             15 	.globl _ClearBalloon
                             16 	.globl _ColorSprite
                             17 	.globl _GetRand
                             18 	.globl _GetBackBufferPtr
                             19 	.globl _cpct_getRandom_mxor_u8
                             20 	.globl _cpct_drawSpriteMasked
                             21 	.globl _cpct_drawSprite
                             22 	.globl _cpct_drawSolidBox
                             23 	.globl _cpct_pens2pixelPatternPairM0_real
                             24 	.globl _cpct_drawSpriteMaskedAlignedColorizeM0
                             25 	.globl _cpct_drawSpriteMaskedColorizeM0
                             26 	.globl _cpct_drawSpriteColorizeM0
                             27 	.globl _cpct_spriteMaskedColourizeM0
                             28 	.globl _cpct_spriteColourizeM0
                             29 	.globl _cpct_memcpy
                             30 	.globl _cpct_memset
                             31 	.globl _gStars
                             32 	.globl _gBalloons
                             33 	.globl _gPosCloud
                             34 	.globl _gBalloonColor
                             35 	.globl _gBackGroundColor
                             36 	.globl _gSpriteColorized
                             37 	.globl _UpdateBalloons
                             38 	.globl _DrawStars
                             39 	.globl _DrawSceneBalloons
                             40 	.globl _InitializeDrawing
                             41 ;--------------------------------------------------------
                             42 ; special function registers
                             43 ;--------------------------------------------------------
                             44 ;--------------------------------------------------------
                             45 ; ram data
                             46 ;--------------------------------------------------------
                             47 	.area _DATA
   1544                      48 _gSpriteColorized::
   1544                      49 	.ds 340
   1698                      50 _gBackGroundColor::
   1698                      51 	.ds 1
   1699                      52 _gBalloonColor::
   1699                      53 	.ds 1
   169A                      54 _gPosCloud::
   169A                      55 	.ds 1
   169B                      56 _gBalloons::
   169B                      57 	.ds 65
   16DC                      58 _gStars::
   16DC                      59 	.ds 30
   16FA                      60 _DrawStars_sColorAnim_1_154:
   16FA                      61 	.ds 1
                             62 ;--------------------------------------------------------
                             63 ; ram data
                             64 ;--------------------------------------------------------
                             65 	.area _INITIALIZED
                             66 ;--------------------------------------------------------
                             67 ; absolute external ram data
                             68 ;--------------------------------------------------------
                             69 	.area _DABS (ABS)
                             70 ;--------------------------------------------------------
                             71 ; global & static initialisations
                             72 ;--------------------------------------------------------
                             73 	.area _HOME
                             74 	.area _GSINIT
                             75 	.area _GSFINAL
                             76 	.area _GSINIT
                             77 ;src/drawing.c:259: static u8 sColorAnim = 0;
   16FC FD 21 FA 16   [14]   78 	ld	iy, #_DrawStars_sColorAnim_1_154
   1700 FD 36 00 00   [19]   79 	ld	0 (iy), #0x00
                             80 ;--------------------------------------------------------
                             81 ; Home
                             82 ;--------------------------------------------------------
                             83 	.area _HOME
                             84 	.area _HOME
                             85 ;--------------------------------------------------------
                             86 ; code
                             87 ;--------------------------------------------------------
                             88 	.area _CODE
                             89 ;src/drawing.c:72: u8 GetRand(u8 max)
                             90 ;	---------------------------------
                             91 ; Function GetRand
                             92 ; ---------------------------------
   0B6A                      93 _GetRand::
                             94 ;src/drawing.c:74: return cpct_rand()%max;
   0B6A CD C9 13      [17]   95 	call	_cpct_getRandom_mxor_u8
   0B6D 45            [ 4]   96 	ld	b, l
   0B6E 21 02 00      [10]   97 	ld	hl, #2+0
   0B71 39            [11]   98 	add	hl, sp
   0B72 7E            [ 7]   99 	ld	a, (hl)
   0B73 F5            [11]  100 	push	af
   0B74 33            [ 6]  101 	inc	sp
   0B75 C5            [11]  102 	push	bc
   0B76 33            [ 6]  103 	inc	sp
   0B77 CD 05 12      [17]  104 	call	__moduchar
   0B7A F1            [10]  105 	pop	af
   0B7B C9            [10]  106 	ret
                            107 ;src/drawing.c:80: u8* ColorSprite(u8 color)
                            108 ;	---------------------------------
                            109 ; Function ColorSprite
                            110 ; ---------------------------------
   0B7C                     111 _ColorSprite::
   0B7C DD E5         [15]  112 	push	ix
   0B7E DD 21 00 00   [14]  113 	ld	ix,#0
   0B82 DD 39         [15]  114 	add	ix,sp
                            115 ;src/drawing.c:83: u16 replacePatColor1 = CPCTM_PENS2PIXELPATTERNPAIR_M0(1, color); // Just for example use cpct_pens2pixelPatternPairM0 with variables
   0B84 DD 7E 04      [19]  116 	ld	a, 4 (ix)
   0B87 E6 01         [ 7]  117 	and	a, #0x01
   0B89 0F            [ 4]  118 	rrca
   0B8A 0F            [ 4]  119 	rrca
   0B8B E6 C0         [ 7]  120 	and	a, #0xc0
   0B8D 4F            [ 4]  121 	ld	c, a
   0B8E DD 7E 04      [19]  122 	ld	a, 4 (ix)
   0B91 E6 02         [ 7]  123 	and	a, #0x02
   0B93 87            [ 4]  124 	add	a, a
   0B94 B1            [ 4]  125 	or	a, c
   0B95 4F            [ 4]  126 	ld	c, a
   0B96 DD 7E 04      [19]  127 	ld	a, 4 (ix)
   0B99 E6 04         [ 7]  128 	and	a, #0x04
   0B9B 87            [ 4]  129 	add	a, a
   0B9C 87            [ 4]  130 	add	a, a
   0B9D B1            [ 4]  131 	or	a, c
   0B9E 4F            [ 4]  132 	ld	c, a
   0B9F DD 7E 04      [19]  133 	ld	a, 4 (ix)
   0BA2 E6 08         [ 7]  134 	and	a, #0x08
   0BA4 0F            [ 4]  135 	rrca
   0BA5 0F            [ 4]  136 	rrca
   0BA6 0F            [ 4]  137 	rrca
   0BA7 E6 1F         [ 7]  138 	and	a, #0x1f
   0BA9 B1            [ 4]  139 	or	a, c
   0BAA 4F            [ 4]  140 	ld	c,a
   0BAB 87            [ 4]  141 	add	a, a
   0BAC B1            [ 4]  142 	or	a, c
   0BAD 5F            [ 4]  143 	ld	e, a
   0BAE 0E 00         [ 7]  144 	ld	c, #0x00
   0BB0 79            [ 4]  145 	ld	a, c
   0BB1 F6 C0         [ 7]  146 	or	a, #0xc0
   0BB3 57            [ 4]  147 	ld	d, a
                            148 ;src/drawing.c:84: u16 replacePatColor2 = cpct_pens2pixelPatternPairM0(2, color + 1);
   0BB4 DD 46 04      [19]  149 	ld	b, 4 (ix)
   0BB7 04            [ 4]  150 	inc	b
   0BB8 D5            [11]  151 	push	de
   0BB9 3E 02         [ 7]  152 	ld	a, #0x02
   0BBB F5            [11]  153 	push	af
   0BBC 33            [ 6]  154 	inc	sp
   0BBD C5            [11]  155 	push	bc
   0BBE 33            [ 6]  156 	inc	sp
   0BBF CD 84 12      [17]  157 	call	_cpct_pens2pixelPatternPairM0_real
   0BC2 4D            [ 4]  158 	ld	c, l
   0BC3 44            [ 4]  159 	ld	b, h
   0BC4 D1            [10]  160 	pop	de
                            161 ;src/drawing.c:87: cpct_memcpy(gSpriteColorized, g_balloon, G_BALLOON_W*G_BALLOON_H);
   0BC5 C5            [11]  162 	push	bc
   0BC6 D5            [11]  163 	push	de
   0BC7 21 54 01      [10]  164 	ld	hl, #0x0154
   0BCA E5            [11]  165 	push	hl
   0BCB 21 06 0A      [10]  166 	ld	hl, #_g_balloon
   0BCE E5            [11]  167 	push	hl
   0BCF 21 44 15      [10]  168 	ld	hl, #_gSpriteColorized
   0BD2 E5            [11]  169 	push	hl
   0BD3 CD 7D 13      [17]  170 	call	_cpct_memcpy
   0BD6 D1            [10]  171 	pop	de
   0BD7 21 44 15      [10]  172 	ld	hl, #_gSpriteColorized
   0BDA E5            [11]  173 	push	hl
   0BDB 21 54 01      [10]  174 	ld	hl, #0x0154
   0BDE E5            [11]  175 	push	hl
   0BDF D5            [11]  176 	push	de
   0BE0 CD 93 13      [17]  177 	call	_cpct_spriteColourizeM0
   0BE3 C1            [10]  178 	pop	bc
                            179 ;src/drawing.c:91: cpct_spriteColourizeM0(replacePatColor2, G_BALLOON_W*G_BALLOON_H, gSpriteColorized);
   0BE4 21 44 15      [10]  180 	ld	hl, #_gSpriteColorized
   0BE7 E5            [11]  181 	push	hl
   0BE8 21 54 01      [10]  182 	ld	hl, #0x0154
   0BEB E5            [11]  183 	push	hl
   0BEC C5            [11]  184 	push	bc
   0BED CD 93 13      [17]  185 	call	_cpct_spriteColourizeM0
                            186 ;src/drawing.c:93: return gSpriteColorized;
   0BF0 21 44 15      [10]  187 	ld	hl, #_gSpriteColorized
   0BF3 DD E1         [14]  188 	pop	ix
   0BF5 C9            [10]  189 	ret
                            190 ;src/drawing.c:99: void ClearBalloon(SBalloon* balloon)
                            191 ;	---------------------------------
                            192 ; Function ClearBalloon
                            193 ; ---------------------------------
   0BF6                     194 _ClearBalloon::
   0BF6 DD E5         [15]  195 	push	ix
   0BF8 DD 21 00 00   [14]  196 	ld	ix,#0
   0BFC DD 39         [15]  197 	add	ix,sp
   0BFE 3B            [ 6]  198 	dec	sp
                            199 ;src/drawing.c:102: if (balloon->drawPosY < VIEW_DOWN)
   0BFF DD 4E 04      [19]  200 	ld	c,4 (ix)
   0C02 DD 46 05      [19]  201 	ld	b,5 (ix)
   0C05 69            [ 4]  202 	ld	l, c
   0C06 60            [ 4]  203 	ld	h, b
   0C07 23            [ 6]  204 	inc	hl
   0C08 23            [ 6]  205 	inc	hl
   0C09 23            [ 6]  206 	inc	hl
   0C0A 5E            [ 7]  207 	ld	e, (hl)
   0C0B 7B            [ 4]  208 	ld	a, e
   0C0C D6 B4         [ 7]  209 	sub	a, #0xb4
   0C0E 30 3D         [12]  210 	jr	NC,00105$
                            211 ;src/drawing.c:107: u8 clearCY = balloon->drawCY + BALLOON_TRAIL;
   0C10 C5            [11]  212 	push	bc
   0C11 FD E1         [14]  213 	pop	iy
   0C13 FD 7E 04      [19]  214 	ld	a, 4 (iy)
   0C16 C6 08         [ 7]  215 	add	a, #0x08
   0C18 DD 77 FF      [19]  216 	ld	-1 (ix), a
                            217 ;src/drawing.c:110: u8 posDownClearY = balloon->drawPosY + clearCY;
   0C1B 7B            [ 4]  218 	ld	a, e
   0C1C DD 86 FF      [19]  219 	add	a, -1 (ix)
   0C1F 57            [ 4]  220 	ld	d, a
                            221 ;src/drawing.c:111: if (posDownClearY > VIEW_DOWN)
                            222 ;src/drawing.c:112: clearCY = VIEW_DOWN - balloon->drawPosY;
   0C20 3E B4         [ 7]  223 	ld	a,#0xb4
   0C22 BA            [ 4]  224 	cp	a,d
   0C23 30 04         [12]  225 	jr	NC,00102$
   0C25 93            [ 4]  226 	sub	a, e
   0C26 DD 77 FF      [19]  227 	ld	-1 (ix), a
   0C29                     228 00102$:
                            229 ;src/drawing.c:115: pvmem = GetBackBufferPtr(balloon->posX, balloon->drawPosY);
   0C29 69            [ 4]  230 	ld	l, c
   0C2A 60            [ 4]  231 	ld	h, b
   0C2B 23            [ 6]  232 	inc	hl
   0C2C 23            [ 6]  233 	inc	hl
   0C2D 46            [ 7]  234 	ld	b, (hl)
   0C2E 7B            [ 4]  235 	ld	a, e
   0C2F F5            [11]  236 	push	af
   0C30 33            [ 6]  237 	inc	sp
   0C31 C5            [11]  238 	push	bc
   0C32 33            [ 6]  239 	inc	sp
   0C33 CD A3 10      [17]  240 	call	_GetBackBufferPtr
   0C36 F1            [10]  241 	pop	af
   0C37 4D            [ 4]  242 	ld	c, l
   0C38 44            [ 4]  243 	ld	b, h
                            244 ;src/drawing.c:116: cpct_drawSolidBox(pvmem, gBackGroundColor, G_BALLOON_W, clearCY);    
   0C39 21 98 16      [10]  245 	ld	hl,#_gBackGroundColor + 0
   0C3C 5E            [ 7]  246 	ld	e, (hl)
   0C3D 16 00         [ 7]  247 	ld	d, #0x00
   0C3F DD 7E FF      [19]  248 	ld	a, -1 (ix)
   0C42 F5            [11]  249 	push	af
   0C43 33            [ 6]  250 	inc	sp
   0C44 3E 0A         [ 7]  251 	ld	a, #0x0a
   0C46 F5            [11]  252 	push	af
   0C47 33            [ 6]  253 	inc	sp
   0C48 D5            [11]  254 	push	de
   0C49 C5            [11]  255 	push	bc
   0C4A CD EE 13      [17]  256 	call	_cpct_drawSolidBox
   0C4D                     257 00105$:
   0C4D 33            [ 6]  258 	inc	sp
   0C4E DD E1         [14]  259 	pop	ix
   0C50 C9            [10]  260 	ret
                            261 ;src/drawing.c:123: void DeleteBalloons(SBalloon* balloons, SBalloon* balloonToDel, u8* nb)
                            262 ;	---------------------------------
                            263 ; Function DeleteBalloons
                            264 ; ---------------------------------
   0C51                     265 _DeleteBalloons::
                            266 ;src/drawing.c:127: const SBalloon* lastBalloon = &balloons[--*nb];
   0C51 21 06 00      [10]  267 	ld	hl, #6
   0C54 39            [11]  268 	add	hl, sp
   0C55 4E            [ 7]  269 	ld	c, (hl)
   0C56 23            [ 6]  270 	inc	hl
   0C57 46            [ 7]  271 	ld	b, (hl)
   0C58 0A            [ 7]  272 	ld	a, (bc)
   0C59 C6 FF         [ 7]  273 	add	a, #0xff
   0C5B 02            [ 7]  274 	ld	(bc), a
   0C5C 6F            [ 4]  275 	ld	l, a
   0C5D 26 00         [ 7]  276 	ld	h, #0x00
   0C5F 29            [11]  277 	add	hl, hl
   0C60 29            [11]  278 	add	hl, hl
   0C61 29            [11]  279 	add	hl, hl
   0C62 4D            [ 4]  280 	ld	c, l
   0C63 44            [ 4]  281 	ld	b, h
   0C64 21 02 00      [10]  282 	ld	hl, #2
   0C67 39            [11]  283 	add	hl, sp
   0C68 7E            [ 7]  284 	ld	a, (hl)
   0C69 23            [ 6]  285 	inc	hl
   0C6A 66            [ 7]  286 	ld	h, (hl)
   0C6B 6F            [ 4]  287 	ld	l, a
   0C6C 09            [11]  288 	add	hl, bc
   0C6D 4D            [ 4]  289 	ld	c, l
   0C6E 44            [ 4]  290 	ld	b, h
                            291 ;src/drawing.c:130: if (balloonToDel != lastBalloon)
   0C6F FD 21 04 00   [14]  292 	ld	iy, #4
   0C73 FD 39         [15]  293 	add	iy, sp
   0C75 FD 7E 00      [19]  294 	ld	a, 0 (iy)
   0C78 91            [ 4]  295 	sub	a, c
   0C79 20 05         [12]  296 	jr	NZ,00109$
   0C7B FD 7E 01      [19]  297 	ld	a, 1 (iy)
   0C7E 90            [ 4]  298 	sub	a, b
   0C7F C8            [11]  299 	ret	Z
   0C80                     300 00109$:
                            301 ;src/drawing.c:131: cpct_memcpy(balloonToDel, lastBalloon, sizeof(SBalloon));
   0C80 FD 5E 00      [19]  302 	ld	e,0 (iy)
   0C83 FD 56 01      [19]  303 	ld	d,1 (iy)
   0C86 21 08 00      [10]  304 	ld	hl, #0x0008
   0C89 E5            [11]  305 	push	hl
   0C8A C5            [11]  306 	push	bc
   0C8B D5            [11]  307 	push	de
   0C8C CD 7D 13      [17]  308 	call	_cpct_memcpy
   0C8F C9            [10]  309 	ret
                            310 ;src/drawing.c:137: void UpdateBalloons()
                            311 ;	---------------------------------
                            312 ; Function UpdateBalloons
                            313 ; ---------------------------------
   0C90                     314 _UpdateBalloons::
   0C90 DD E5         [15]  315 	push	ix
   0C92 DD 21 00 00   [14]  316 	ld	ix,#0
   0C96 DD 39         [15]  317 	add	ix,sp
   0C98 F5            [11]  318 	push	af
   0C99 F5            [11]  319 	push	af
   0C9A 3B            [ 6]  320 	dec	sp
                            321 ;src/drawing.c:139: SBalloon* itBalloon = gBalloons.balloons;
                            322 ;src/drawing.c:143: if (gBalloons.nb < NB_BALLOONS)
   0C9B 21 9B 16      [10]  323 	ld	hl, #_gBalloons + 0
   0C9E 4E            [ 7]  324 	ld	c, (hl)
   0C9F 79            [ 4]  325 	ld	a, c
   0CA0 D6 08         [ 7]  326 	sub	a, #0x08
   0CA2 D2 24 0D      [10]  327 	jp	NC, 00127$
                            328 ;src/drawing.c:147: SBalloon* newBalloon = &gBalloons.balloons[gBalloons.nb++];
   0CA5 41            [ 4]  329 	ld	b, c
   0CA6 04            [ 4]  330 	inc	b
   0CA7 21 9B 16      [10]  331 	ld	hl, #_gBalloons
   0CAA 70            [ 7]  332 	ld	(hl), b
   0CAB 79            [ 4]  333 	ld	a, c
   0CAC 07            [ 4]  334 	rlca
   0CAD 07            [ 4]  335 	rlca
   0CAE 07            [ 4]  336 	rlca
   0CAF E6 F8         [ 7]  337 	and	a, #0xf8
   0CB1 4F            [ 4]  338 	ld	c, a
   0CB2 21 9C 16      [10]  339 	ld	hl, #(_gBalloons + 0x0001)
   0CB5 06 00         [ 7]  340 	ld	b, #0x00
   0CB7 09            [11]  341 	add	hl, bc
   0CB8 4D            [ 4]  342 	ld	c, l
   0CB9 44            [ 4]  343 	ld	b, h
                            344 ;src/drawing.c:150: newBalloon->posX = GetRand(SCREEN_CX - G_BALLOON_W);
   0CBA 59            [ 4]  345 	ld	e, c
   0CBB 50            [ 4]  346 	ld	d, b
   0CBC 13            [ 6]  347 	inc	de
   0CBD 13            [ 6]  348 	inc	de
   0CBE C5            [11]  349 	push	bc
   0CBF D5            [11]  350 	push	de
   0CC0 3E 46         [ 7]  351 	ld	a, #0x46
   0CC2 F5            [11]  352 	push	af
   0CC3 33            [ 6]  353 	inc	sp
   0CC4 CD 6A 0B      [17]  354 	call	_GetRand
   0CC7 33            [ 6]  355 	inc	sp
   0CC8 7D            [ 4]  356 	ld	a, l
   0CC9 D1            [10]  357 	pop	de
   0CCA C1            [10]  358 	pop	bc
   0CCB 12            [ 7]  359 	ld	(de), a
                            360 ;src/drawing.c:151: newBalloon->posY = SCREEN_CY - GetRand(40);
   0CCC C5            [11]  361 	push	bc
   0CCD 3E 28         [ 7]  362 	ld	a, #0x28
   0CCF F5            [11]  363 	push	af
   0CD0 33            [ 6]  364 	inc	sp
   0CD1 CD 6A 0B      [17]  365 	call	_GetRand
   0CD4 33            [ 6]  366 	inc	sp
   0CD5 C1            [10]  367 	pop	bc
   0CD6 26 00         [ 7]  368 	ld	h, #0x00
   0CD8 3E C8         [ 7]  369 	ld	a, #0xc8
   0CDA 95            [ 4]  370 	sub	a, l
   0CDB 5F            [ 4]  371 	ld	e, a
   0CDC 3E 00         [ 7]  372 	ld	a, #0x00
   0CDE 9C            [ 4]  373 	sbc	a, h
   0CDF 57            [ 4]  374 	ld	d, a
   0CE0 69            [ 4]  375 	ld	l, c
   0CE1 60            [ 4]  376 	ld	h, b
   0CE2 73            [ 7]  377 	ld	(hl), e
   0CE3 23            [ 6]  378 	inc	hl
   0CE4 72            [ 7]  379 	ld	(hl), d
                            380 ;src/drawing.c:154: newBalloon->speed = GetRand(3) + 2;
   0CE5 21 05 00      [10]  381 	ld	hl, #0x0005
   0CE8 09            [11]  382 	add	hl, bc
   0CE9 E5            [11]  383 	push	hl
   0CEA C5            [11]  384 	push	bc
   0CEB 3E 03         [ 7]  385 	ld	a, #0x03
   0CED F5            [11]  386 	push	af
   0CEE 33            [ 6]  387 	inc	sp
   0CEF CD 6A 0B      [17]  388 	call	_GetRand
   0CF2 33            [ 6]  389 	inc	sp
   0CF3 5D            [ 4]  390 	ld	e, l
   0CF4 C1            [10]  391 	pop	bc
   0CF5 E1            [10]  392 	pop	hl
   0CF6 1C            [ 4]  393 	inc	e
   0CF7 1C            [ 4]  394 	inc	e
   0CF8 73            [ 7]  395 	ld	(hl), e
                            396 ;src/drawing.c:157: gBalloonColor = (gBalloonColor + 2) % 12;
   0CF9 21 99 16      [10]  397 	ld	hl,#_gBalloonColor + 0
   0CFC 5E            [ 7]  398 	ld	e, (hl)
   0CFD 16 00         [ 7]  399 	ld	d, #0x00
   0CFF 13            [ 6]  400 	inc	de
   0D00 13            [ 6]  401 	inc	de
   0D01 C5            [11]  402 	push	bc
   0D02 21 0C 00      [10]  403 	ld	hl, #0x000c
   0D05 E5            [11]  404 	push	hl
   0D06 D5            [11]  405 	push	de
   0D07 CD A2 14      [17]  406 	call	__modsint
   0D0A F1            [10]  407 	pop	af
   0D0B F1            [10]  408 	pop	af
   0D0C C1            [10]  409 	pop	bc
   0D0D FD 21 99 16   [14]  410 	ld	iy, #_gBalloonColor
   0D11 FD 75 00      [19]  411 	ld	0 (iy), l
                            412 ;src/drawing.c:158: newBalloon->color = gBalloonColor + 1;
   0D14 21 06 00      [10]  413 	ld	hl, #0x0006
   0D17 09            [11]  414 	add	hl,bc
   0D18 EB            [ 4]  415 	ex	de,hl
   0D19 FD 7E 00      [19]  416 	ld	a, 0 (iy)
   0D1C 3C            [ 4]  417 	inc	a
   0D1D 12            [ 7]  418 	ld	(de), a
                            419 ;src/drawing.c:161: newBalloon->status = BALLOON_ACTIVE;
   0D1E 21 07 00      [10]  420 	ld	hl, #0x0007
   0D21 09            [11]  421 	add	hl, bc
   0D22 36 01         [10]  422 	ld	(hl), #0x01
                            423 ;src/drawing.c:165: for (i = 0; i < gBalloons.nb; i++)
   0D24                     424 00127$:
   0D24 01 9C 16      [10]  425 	ld	bc, #(_gBalloons + 0x0001)
   0D27 DD 36 FB 00   [19]  426 	ld	-5 (ix), #0x00
   0D2B                     427 00117$:
   0D2B 21 9B 16      [10]  428 	ld	hl, #_gBalloons + 0
   0D2E DD 7E FB      [19]  429 	ld	a,-5 (ix)
   0D31 96            [ 7]  430 	sub	a,(hl)
   0D32 D2 EA 0D      [10]  431 	jp	NC, 00119$
                            432 ;src/drawing.c:168: if (itBalloon->status == BALLOON_ACTIVE)
   0D35 21 07 00      [10]  433 	ld	hl, #0x0007
   0D38 09            [11]  434 	add	hl,bc
   0D39 DD 75 FC      [19]  435 	ld	-4 (ix), l
   0D3C DD 74 FD      [19]  436 	ld	-3 (ix), h
   0D3F 5E            [ 7]  437 	ld	e, (hl)
   0D40 1D            [ 4]  438 	dec	e
   0D41 C2 C4 0D      [10]  439 	jp	NZ,00113$
                            440 ;src/drawing.c:171: if (itBalloon->posY + G_BALLOON_H < VIEW_TOP)
   0D44 69            [ 4]  441 	ld	l, c
   0D45 60            [ 4]  442 	ld	h, b
   0D46 5E            [ 7]  443 	ld	e, (hl)
   0D47 23            [ 6]  444 	inc	hl
   0D48 56            [ 7]  445 	ld	d, (hl)
   0D49 21 22 00      [10]  446 	ld	hl, #0x0022
   0D4C 19            [11]  447 	add	hl, de
   0D4D CB 7C         [ 8]  448 	bit	7, h
   0D4F 28 12         [12]  449 	jr	Z,00110$
                            450 ;src/drawing.c:174: itBalloon->status = BALLOON_INACTIVE;
   0D51 DD 6E FC      [19]  451 	ld	l,-4 (ix)
   0D54 DD 66 FD      [19]  452 	ld	h,-3 (ix)
   0D57 36 00         [10]  453 	ld	(hl), #0x00
                            454 ;src/drawing.c:176: ClearBalloon(itBalloon);
   0D59 C5            [11]  455 	push	bc
   0D5A C5            [11]  456 	push	bc
   0D5B CD F6 0B      [17]  457 	call	_ClearBalloon
   0D5E F1            [10]  458 	pop	af
   0D5F C1            [10]  459 	pop	bc
   0D60 C3 DE 0D      [10]  460 	jp	00114$
   0D63                     461 00110$:
                            462 ;src/drawing.c:181: i16 posY = itBalloon->posY - itBalloon->speed;
   0D63 C5            [11]  463 	push	bc
   0D64 FD E1         [14]  464 	pop	iy
   0D66 FD 6E 05      [19]  465 	ld	l, 5 (iy)
   0D69 26 00         [ 7]  466 	ld	h, #0x00
   0D6B 7B            [ 4]  467 	ld	a, e
   0D6C 95            [ 4]  468 	sub	a, l
   0D6D 5F            [ 4]  469 	ld	e, a
   0D6E 7A            [ 4]  470 	ld	a, d
   0D6F 9C            [ 4]  471 	sbc	a, h
   0D70 57            [ 4]  472 	ld	d, a
                            473 ;src/drawing.c:182: itBalloon->posY = posY;
   0D71 69            [ 4]  474 	ld	l, c
   0D72 60            [ 4]  475 	ld	h, b
   0D73 73            [ 7]  476 	ld	(hl), e
   0D74 23            [ 6]  477 	inc	hl
   0D75 72            [ 7]  478 	ld	(hl), d
                            479 ;src/drawing.c:187: itBalloon->drawPosY = 0;
   0D76 69            [ 4]  480 	ld	l, c
   0D77 60            [ 4]  481 	ld	h, b
   0D78 23            [ 6]  482 	inc	hl
   0D79 23            [ 6]  483 	inc	hl
   0D7A 23            [ 6]  484 	inc	hl
                            485 ;src/drawing.c:188: itBalloon->drawCY = G_BALLOON_H + posY;
   0D7B FD 21 04 00   [14]  486 	ld	iy, #0x0004
   0D7F FD 09         [15]  487 	add	iy, bc
   0D81 DD 73 FC      [19]  488 	ld	-4 (ix), e
                            489 ;src/drawing.c:185: if (posY < VIEW_TOP)
   0D84 CB 7A         [ 8]  490 	bit	7, d
   0D86 28 0C         [12]  491 	jr	Z,00107$
                            492 ;src/drawing.c:187: itBalloon->drawPosY = 0;
   0D88 36 00         [10]  493 	ld	(hl), #0x00
                            494 ;src/drawing.c:188: itBalloon->drawCY = G_BALLOON_H + posY;
   0D8A DD 7E FC      [19]  495 	ld	a, -4 (ix)
   0D8D C6 22         [ 7]  496 	add	a, #0x22
   0D8F FD 77 00      [19]  497 	ld	0 (iy), a
   0D92 18 4A         [12]  498 	jr	00114$
   0D94                     499 00107$:
                            500 ;src/drawing.c:192: if (posY + G_BALLOON_H > VIEW_DOWN)
   0D94 7B            [ 4]  501 	ld	a, e
   0D95 C6 22         [ 7]  502 	add	a, #0x22
   0D97 DD 77 FE      [19]  503 	ld	-2 (ix), a
   0D9A 7A            [ 4]  504 	ld	a, d
   0D9B CE 00         [ 7]  505 	adc	a, #0x00
   0D9D DD 77 FF      [19]  506 	ld	-1 (ix), a
                            507 ;src/drawing.c:194: itBalloon->drawPosY = posY;
                            508 ;src/drawing.c:192: if (posY + G_BALLOON_H > VIEW_DOWN)
   0DA0 3E B4         [ 7]  509 	ld	a, #0xb4
   0DA2 DD BE FE      [19]  510 	cp	a, -2 (ix)
   0DA5 3E 00         [ 7]  511 	ld	a, #0x00
   0DA7 DD 9E FF      [19]  512 	sbc	a, -1 (ix)
   0DAA E2 AF 0D      [10]  513 	jp	PO, 00152$
   0DAD EE 80         [ 7]  514 	xor	a, #0x80
   0DAF                     515 00152$:
   0DAF F2 BD 0D      [10]  516 	jp	P, 00104$
                            517 ;src/drawing.c:194: itBalloon->drawPosY = posY;
   0DB2 73            [ 7]  518 	ld	(hl), e
                            519 ;src/drawing.c:195: itBalloon->drawCY = VIEW_DOWN - posY;
   0DB3 3E B4         [ 7]  520 	ld	a, #0xb4
   0DB5 DD 96 FC      [19]  521 	sub	a, -4 (ix)
   0DB8 FD 77 00      [19]  522 	ld	0 (iy), a
   0DBB 18 21         [12]  523 	jr	00114$
   0DBD                     524 00104$:
                            525 ;src/drawing.c:200: itBalloon->drawPosY = posY;
   0DBD 73            [ 7]  526 	ld	(hl), e
                            527 ;src/drawing.c:201: itBalloon->drawCY = G_BALLOON_H;
   0DBE FD 36 00 22   [19]  528 	ld	0 (iy), #0x22
   0DC2 18 1A         [12]  529 	jr	00114$
   0DC4                     530 00113$:
                            531 ;src/drawing.c:209: ClearBalloon(itBalloon);
   0DC4 C5            [11]  532 	push	bc
   0DC5 C5            [11]  533 	push	bc
   0DC6 CD F6 0B      [17]  534 	call	_ClearBalloon
   0DC9 F1            [10]  535 	pop	af
   0DCA C1            [10]  536 	pop	bc
                            537 ;src/drawing.c:212: DeleteBalloons(gBalloons.balloons, itBalloon, &gBalloons.nb);
   0DCB C5            [11]  538 	push	bc
   0DCC 21 9B 16      [10]  539 	ld	hl, #_gBalloons
   0DCF E5            [11]  540 	push	hl
   0DD0 C5            [11]  541 	push	bc
   0DD1 21 9C 16      [10]  542 	ld	hl, #(_gBalloons + 0x0001)
   0DD4 E5            [11]  543 	push	hl
   0DD5 CD 51 0C      [17]  544 	call	_DeleteBalloons
   0DD8 21 06 00      [10]  545 	ld	hl, #6
   0DDB 39            [11]  546 	add	hl, sp
   0DDC F9            [ 6]  547 	ld	sp, hl
   0DDD C1            [10]  548 	pop	bc
   0DDE                     549 00114$:
                            550 ;src/drawing.c:216: itBalloon++;
   0DDE 21 08 00      [10]  551 	ld	hl, #0x0008
   0DE1 09            [11]  552 	add	hl,bc
   0DE2 4D            [ 4]  553 	ld	c, l
   0DE3 44            [ 4]  554 	ld	b, h
                            555 ;src/drawing.c:165: for (i = 0; i < gBalloons.nb; i++)
   0DE4 DD 34 FB      [23]  556 	inc	-5 (ix)
   0DE7 C3 2B 0D      [10]  557 	jp	00117$
   0DEA                     558 00119$:
   0DEA DD F9         [10]  559 	ld	sp, ix
   0DEC DD E1         [14]  560 	pop	ix
   0DEE C9            [10]  561 	ret
                            562 ;src/drawing.c:223: void DrawBalloon(SBalloon* balloon, u8* spriteBalloon)
                            563 ;	---------------------------------
                            564 ; Function DrawBalloon
                            565 ; ---------------------------------
   0DEF                     566 _DrawBalloon::
   0DEF DD E5         [15]  567 	push	ix
   0DF1 DD 21 00 00   [14]  568 	ld	ix,#0
   0DF5 DD 39         [15]  569 	add	ix,sp
   0DF7 21 FA FF      [10]  570 	ld	hl, #-6
   0DFA 39            [11]  571 	add	hl, sp
   0DFB F9            [ 6]  572 	ld	sp, hl
                            573 ;src/drawing.c:225: i16 posY = balloon->posY;
   0DFC DD 4E 04      [19]  574 	ld	c,4 (ix)
   0DFF DD 46 05      [19]  575 	ld	b,5 (ix)
   0E02 0A            [ 7]  576 	ld	a, (bc)
   0E03 DD 77 FE      [19]  577 	ld	-2 (ix), a
   0E06 03            [ 6]  578 	inc	bc
   0E07 0A            [ 7]  579 	ld	a, (bc)
   0E08 DD 77 FF      [19]  580 	ld	-1 (ix), a
   0E0B 0B            [ 6]  581 	dec	bc
                            582 ;src/drawing.c:228: if (posY + G_BALLOON_H > VIEW_TOP && posY < VIEW_DOWN)
   0E0C DD 7E FE      [19]  583 	ld	a, -2 (ix)
   0E0F C6 22         [ 7]  584 	add	a, #0x22
   0E11 5F            [ 4]  585 	ld	e, a
   0E12 DD 7E FF      [19]  586 	ld	a, -1 (ix)
   0E15 CE 00         [ 7]  587 	adc	a, #0x00
   0E17 57            [ 4]  588 	ld	d, a
   0E18 AF            [ 4]  589 	xor	a, a
   0E19 BB            [ 4]  590 	cp	a, e
   0E1A 9A            [ 4]  591 	sbc	a, d
   0E1B E2 20 0E      [10]  592 	jp	PO, 00120$
   0E1E EE 80         [ 7]  593 	xor	a, #0x80
   0E20                     594 00120$:
   0E20 F2 A2 0E      [10]  595 	jp	P, 00106$
   0E23 DD 7E FE      [19]  596 	ld	a, -2 (ix)
   0E26 D6 B4         [ 7]  597 	sub	a, #0xb4
   0E28 DD 7E FF      [19]  598 	ld	a, -1 (ix)
   0E2B 17            [ 4]  599 	rla
   0E2C 3F            [ 4]  600 	ccf
   0E2D 1F            [ 4]  601 	rra
   0E2E DE 80         [ 7]  602 	sbc	a, #0x80
   0E30 30 70         [12]  603 	jr	NC,00106$
                            604 ;src/drawing.c:231: u8* pvmem = GetBackBufferPtr(balloon->posX, balloon->drawPosY);
   0E32 69            [ 4]  605 	ld	l, c
   0E33 60            [ 4]  606 	ld	h, b
   0E34 23            [ 6]  607 	inc	hl
   0E35 23            [ 6]  608 	inc	hl
   0E36 23            [ 6]  609 	inc	hl
   0E37 56            [ 7]  610 	ld	d, (hl)
   0E38 69            [ 4]  611 	ld	l, c
   0E39 60            [ 4]  612 	ld	h, b
   0E3A 23            [ 6]  613 	inc	hl
   0E3B 23            [ 6]  614 	inc	hl
   0E3C 7E            [ 7]  615 	ld	a, (hl)
   0E3D C5            [11]  616 	push	bc
   0E3E 5F            [ 4]  617 	ld	e, a
   0E3F D5            [11]  618 	push	de
   0E40 CD A3 10      [17]  619 	call	_GetBackBufferPtr
   0E43 F1            [10]  620 	pop	af
   0E44 C1            [10]  621 	pop	bc
   0E45 33            [ 6]  622 	inc	sp
   0E46 33            [ 6]  623 	inc	sp
   0E47 E5            [11]  624 	push	hl
                            625 ;src/drawing.c:232: u8* sprite = (u8*)spriteBalloon;
   0E48 DD 5E 06      [19]  626 	ld	e,6 (ix)
   0E4B DD 56 07      [19]  627 	ld	d,7 (ix)
                            628 ;src/drawing.c:234: u16 replacePatColor1 = cpct_pens2pixelPatternPairM0(1, balloon->color);
   0E4E C5            [11]  629 	push	bc
   0E4F FD E1         [14]  630 	pop	iy
   0E51 FD 66 06      [19]  631 	ld	h, 6 (iy)
   0E54 C5            [11]  632 	push	bc
   0E55 D5            [11]  633 	push	de
   0E56 3E 01         [ 7]  634 	ld	a, #0x01
   0E58 F5            [11]  635 	push	af
   0E59 33            [ 6]  636 	inc	sp
   0E5A E5            [11]  637 	push	hl
   0E5B 33            [ 6]  638 	inc	sp
   0E5C CD 84 12      [17]  639 	call	_cpct_pens2pixelPatternPairM0_real
   0E5F D1            [10]  640 	pop	de
   0E60 C1            [10]  641 	pop	bc
   0E61 DD 75 FC      [19]  642 	ld	-4 (ix), l
   0E64 DD 74 FD      [19]  643 	ld	-3 (ix), h
                            644 ;src/drawing.c:237: if (posY < VIEW_TOP)
   0E67 DD CB FF 7E   [20]  645 	bit	7, -1 (ix)
   0E6B 28 13         [12]  646 	jr	Z,00102$
                            647 ;src/drawing.c:240: u8 y = -posY;
   0E6D DD 6E FE      [19]  648 	ld	l, -2 (ix)
   0E70 AF            [ 4]  649 	xor	a, a
   0E71 95            [ 4]  650 	sub	a, l
   0E72 6F            [ 4]  651 	ld	l, a
                            652 ;src/drawing.c:243: sprite = (u8*)spriteBalloon + G_BALLOON_W * y;
   0E73 D5            [11]  653 	push	de
   0E74 5D            [ 4]  654 	ld	e,l
   0E75 16 00         [ 7]  655 	ld	d,#0x00
   0E77 6B            [ 4]  656 	ld	l, e
   0E78 62            [ 4]  657 	ld	h, d
   0E79 29            [11]  658 	add	hl, hl
   0E7A 29            [11]  659 	add	hl, hl
   0E7B 19            [11]  660 	add	hl, de
   0E7C 29            [11]  661 	add	hl, hl
   0E7D D1            [10]  662 	pop	de
   0E7E 19            [11]  663 	add	hl,de
   0E7F EB            [ 4]  664 	ex	de,hl
   0E80                     665 00102$:
                            666 ;src/drawing.c:246: cpct_drawSpriteMaskedAlignedColorizeM0(sprite, pvmem, G_BALLOON_W, balloon->drawCY, gMaskTable, replacePatColor1);
   0E80 C5            [11]  667 	push	bc
   0E81 FD E1         [14]  668 	pop	iy
   0E83 FD 46 04      [19]  669 	ld	b, 4 (iy)
   0E86 DD 6E FC      [19]  670 	ld	l,-4 (ix)
   0E89 DD 66 FD      [19]  671 	ld	h,-3 (ix)
   0E8C E5            [11]  672 	push	hl
   0E8D 21 00 7F      [10]  673 	ld	hl, #_gMaskTable
   0E90 E5            [11]  674 	push	hl
   0E91 C5            [11]  675 	push	bc
   0E92 33            [ 6]  676 	inc	sp
   0E93 3E 0A         [ 7]  677 	ld	a, #0x0a
   0E95 F5            [11]  678 	push	af
   0E96 33            [ 6]  679 	inc	sp
   0E97 DD 6E FA      [19]  680 	ld	l,-6 (ix)
   0E9A DD 66 FB      [19]  681 	ld	h,-5 (ix)
   0E9D E5            [11]  682 	push	hl
   0E9E D5            [11]  683 	push	de
   0E9F CD 1C 12      [17]  684 	call	_cpct_drawSpriteMaskedAlignedColorizeM0
   0EA2                     685 00106$:
   0EA2 DD F9         [10]  686 	ld	sp, ix
   0EA4 DD E1         [14]  687 	pop	ix
   0EA6 C9            [10]  688 	ret
                            689 ;src/drawing.c:253: void DrawStars()
                            690 ;	---------------------------------
                            691 ; Function DrawStars
                            692 ; ---------------------------------
   0EA7                     693 _DrawStars::
   0EA7 DD E5         [15]  694 	push	ix
   0EA9 DD 21 00 00   [14]  695 	ld	ix,#0
   0EAD DD 39         [15]  696 	add	ix,sp
   0EAF F5            [11]  697 	push	af
                            698 ;src/drawing.c:261: for (u8 i = 0; i < NB_STARS; i++)
   0EB0 0E 00         [ 7]  699 	ld	c, #0x00
   0EB2                     700 00109$:
                            701 ;src/drawing.c:264: u8* pvmem = GetBackBufferPtr(SCREEN_CX / NB_STARS * i + 5, i + 175);
   0EB2 79            [ 4]  702 	ld	a,c
   0EB3 FE 0A         [ 7]  703 	cp	a,#0x0a
   0EB5 D2 73 0F      [10]  704 	jp	NC,00111$
   0EB8 C6 AF         [ 7]  705 	add	a, #0xaf
   0EBA 57            [ 4]  706 	ld	d, a
   0EBB 79            [ 4]  707 	ld	a, c
   0EBC 07            [ 4]  708 	rlca
   0EBD 07            [ 4]  709 	rlca
   0EBE 07            [ 4]  710 	rlca
   0EBF E6 F8         [ 7]  711 	and	a, #0xf8
   0EC1 C6 05         [ 7]  712 	add	a, #0x05
   0EC3 47            [ 4]  713 	ld	b, a
   0EC4 C5            [11]  714 	push	bc
   0EC5 58            [ 4]  715 	ld	e, b
   0EC6 D5            [11]  716 	push	de
   0EC7 CD A3 10      [17]  717 	call	_GetBackBufferPtr
   0ECA F1            [10]  718 	pop	af
   0ECB C1            [10]  719 	pop	bc
   0ECC 33            [ 6]  720 	inc	sp
   0ECD 33            [ 6]  721 	inc	sp
   0ECE E5            [11]  722 	push	hl
                            723 ;src/drawing.c:267: u8 colorPaletteStar = (i + sColorAnim++) % NB_COLORS_STAR;
   0ECF 59            [ 4]  724 	ld	e, c
   0ED0 16 00         [ 7]  725 	ld	d, #0x00
   0ED2 FD 21 FA 16   [14]  726 	ld	iy, #_DrawStars_sColorAnim_1_154
   0ED6 FD 46 00      [19]  727 	ld	b, 0 (iy)
   0ED9 FD 34 00      [23]  728 	inc	0 (iy)
   0EDC 26 00         [ 7]  729 	ld	h, #0x00
   0EDE 68            [ 4]  730 	ld	l, b
   0EDF 19            [11]  731 	add	hl, de
   0EE0 C5            [11]  732 	push	bc
   0EE1 11 07 00      [10]  733 	ld	de, #0x0007
   0EE4 D5            [11]  734 	push	de
   0EE5 E5            [11]  735 	push	hl
   0EE6 CD A2 14      [17]  736 	call	__modsint
   0EE9 F1            [10]  737 	pop	af
   0EEA F1            [10]  738 	pop	af
   0EEB 5D            [ 4]  739 	ld	e, l
   0EEC C1            [10]  740 	pop	bc
                            741 ;src/drawing.c:270: u16 replacePatColor = cpct_pens2pixelPatternPairM0(15, sColorStar[colorPaletteStar]);
   0EED 21 78 0F      [10]  742 	ld	hl, #_DrawStars_sColorStar_1_154
   0EF0 16 00         [ 7]  743 	ld	d, #0x00
   0EF2 19            [11]  744 	add	hl, de
   0EF3 46            [ 7]  745 	ld	b, (hl)
   0EF4 C5            [11]  746 	push	bc
   0EF5 3E 0F         [ 7]  747 	ld	a, #0x0f
   0EF7 F5            [11]  748 	push	af
   0EF8 33            [ 6]  749 	inc	sp
   0EF9 C5            [11]  750 	push	bc
   0EFA 33            [ 6]  751 	inc	sp
   0EFB CD 84 12      [17]  752 	call	_cpct_pens2pixelPatternPairM0_real
   0EFE EB            [ 4]  753 	ex	de,hl
   0EFF C1            [10]  754 	pop	bc
                            755 ;src/drawing.c:272: if ((i%3) == 0)
   0F00 C5            [11]  756 	push	bc
   0F01 D5            [11]  757 	push	de
   0F02 06 03         [ 7]  758 	ld	b, #0x03
   0F04 C5            [11]  759 	push	bc
   0F05 CD 05 12      [17]  760 	call	__moduchar
   0F08 F1            [10]  761 	pop	af
   0F09 D1            [10]  762 	pop	de
   0F0A C1            [10]  763 	pop	bc
   0F0B 7D            [ 4]  764 	ld	a, l
   0F0C B7            [ 4]  765 	or	a, a
   0F0D 20 31         [12]  766 	jr	NZ,00105$
                            767 ;src/drawing.c:275: cpct_memcpy(gSpriteColorized, g_circle_trans, G_CIRCLE_TRANS_W * G_CIRCLE_TRANS_H * 2);
   0F0F C5            [11]  768 	push	bc
   0F10 D5            [11]  769 	push	de
   0F11 21 18 00      [10]  770 	ld	hl, #0x0018
   0F14 E5            [11]  771 	push	hl
   0F15 21 EA 09      [10]  772 	ld	hl, #_g_circle_trans
   0F18 E5            [11]  773 	push	hl
   0F19 21 44 15      [10]  774 	ld	hl, #_gSpriteColorized
   0F1C E5            [11]  775 	push	hl
   0F1D CD 7D 13      [17]  776 	call	_cpct_memcpy
   0F20 D1            [10]  777 	pop	de
   0F21 21 44 15      [10]  778 	ld	hl, #_gSpriteColorized
   0F24 E5            [11]  779 	push	hl
   0F25 21 0C 00      [10]  780 	ld	hl, #0x000c
   0F28 E5            [11]  781 	push	hl
   0F29 D5            [11]  782 	push	de
   0F2A CD 8C 11      [17]  783 	call	_cpct_spriteMaskedColourizeM0
   0F2D C1            [10]  784 	pop	bc
                            785 ;src/drawing.c:281: cpct_drawSpriteMasked(gSpriteColorized, pvmem, G_CIRCLE_TRANS_W, G_CIRCLE_TRANS_H);
   0F2E D1            [10]  786 	pop	de
   0F2F D5            [11]  787 	push	de
   0F30 C5            [11]  788 	push	bc
   0F31 21 02 06      [10]  789 	ld	hl, #0x0602
   0F34 E5            [11]  790 	push	hl
   0F35 D5            [11]  791 	push	de
   0F36 21 44 15      [10]  792 	ld	hl, #_gSpriteColorized
   0F39 E5            [11]  793 	push	hl
   0F3A CD E0 12      [17]  794 	call	_cpct_drawSpriteMasked
   0F3D C1            [10]  795 	pop	bc
   0F3E 18 2F         [12]  796 	jr	00110$
   0F40                     797 00105$:
                            798 ;src/drawing.c:283: else if ((i%3) == 1)
   0F40 2D            [ 4]  799 	dec	l
   0F41 20 17         [12]  800 	jr	NZ,00102$
                            801 ;src/drawing.c:286: cpct_drawSpriteColorizeM0(g_square, pvmem, G_SQUARE_W, G_SQUARE_H, replacePatColor);
   0F43 C5            [11]  802 	push	bc
   0F44 D5            [11]  803 	push	de
   0F45 21 01 04      [10]  804 	ld	hl, #0x0401
   0F48 E5            [11]  805 	push	hl
   0F49 DD 6E FE      [19]  806 	ld	l,-2 (ix)
   0F4C DD 66 FF      [19]  807 	ld	h,-1 (ix)
   0F4F E5            [11]  808 	push	hl
   0F50 21 02 0A      [10]  809 	ld	hl, #_g_square
   0F53 E5            [11]  810 	push	hl
   0F54 CD B4 11      [17]  811 	call	_cpct_drawSpriteColorizeM0
   0F57 C1            [10]  812 	pop	bc
   0F58 18 15         [12]  813 	jr	00110$
   0F5A                     814 00102$:
                            815 ;src/drawing.c:291: cpct_drawSpriteMaskedColorizeM0(g_star_trans, pvmem, G_STAR_TRANS_W, G_STAR_TRANS_H, replacePatColor);
   0F5A C5            [11]  816 	push	bc
   0F5B D5            [11]  817 	push	de
   0F5C 21 02 06      [10]  818 	ld	hl, #0x0602
   0F5F E5            [11]  819 	push	hl
   0F60 DD 6E FE      [19]  820 	ld	l,-2 (ix)
   0F63 DD 66 FF      [19]  821 	ld	h,-1 (ix)
   0F66 E5            [11]  822 	push	hl
   0F67 21 F6 09      [10]  823 	ld	hl, #_g_star_trans
   0F6A E5            [11]  824 	push	hl
   0F6B CD 13 13      [17]  825 	call	_cpct_drawSpriteMaskedColorizeM0
   0F6E C1            [10]  826 	pop	bc
   0F6F                     827 00110$:
                            828 ;src/drawing.c:261: for (u8 i = 0; i < NB_STARS; i++)
   0F6F 0C            [ 4]  829 	inc	c
   0F70 C3 B2 0E      [10]  830 	jp	00109$
   0F73                     831 00111$:
   0F73 DD F9         [10]  832 	ld	sp, ix
   0F75 DD E1         [14]  833 	pop	ix
   0F77 C9            [10]  834 	ret
   0F78                     835 _DrawStars_sColorStar_1_154:
   0F78 02                  836 	.db #0x02	; 2
   0F79 04                  837 	.db #0x04	; 4
   0F7A 07                  838 	.db #0x07	; 7
   0F7B 08                  839 	.db #0x08	; 8
   0F7C 0A                  840 	.db #0x0a	; 10
   0F7D 0B                  841 	.db #0x0b	; 11
   0F7E 0C                  842 	.db #0x0c	; 12
                            843 ;src/drawing.c:299: void DrawCloud()
                            844 ;	---------------------------------
                            845 ; Function DrawCloud
                            846 ; ---------------------------------
   0F7F                     847 _DrawCloud::
                            848 ;src/drawing.c:302: u8* pvmem = GetBackBufferPtr(0, POS_CLOUD_Y);
   0F7F 21 00 14      [10]  849 	ld	hl, #0x1400
   0F82 E5            [11]  850 	push	hl
   0F83 CD A3 10      [17]  851 	call	_GetBackBufferPtr
   0F86 F1            [10]  852 	pop	af
                            853 ;src/drawing.c:303: cpct_drawSprite(g_cloud, pvmem, G_CLOUD_W, G_CLOUD_H);
   0F87 01 40 00      [10]  854 	ld	bc, #_g_cloud+0
   0F8A 11 1F 36      [10]  855 	ld	de, #0x361f
   0F8D D5            [11]  856 	push	de
   0F8E E5            [11]  857 	push	hl
   0F8F C5            [11]  858 	push	bc
   0F90 CD E7 10      [17]  859 	call	_cpct_drawSprite
   0F93 C9            [10]  860 	ret
                            861 ;src/drawing.c:309: void DrawSceneBalloons()
                            862 ;	---------------------------------
                            863 ; Function DrawSceneBalloons
                            864 ; ---------------------------------
   0F94                     865 _DrawSceneBalloons::
   0F94 DD E5         [15]  866 	push	ix
   0F96 DD 21 00 00   [14]  867 	ld	ix,#0
   0F9A DD 39         [15]  868 	add	ix,sp
   0F9C 3B            [ 6]  869 	dec	sp
                            870 ;src/drawing.c:312: SBalloon* itBalloon = gBalloons.balloons; // Get first balloon pointer
   0F9D 01 9C 16      [10]  871 	ld	bc, #(_gBalloons + 0x0001)
                            872 ;src/drawing.c:313: for (u8 i = 0; i < gBalloons.nb; i++)
   0FA0 1E 00         [ 7]  873 	ld	e, #0x00
   0FA2                     874 00107$:
   0FA2 21 9B 16      [10]  875 	ld	hl, #_gBalloons + 0
   0FA5 56            [ 7]  876 	ld	d, (hl)
   0FA6 7B            [ 4]  877 	ld	a, e
   0FA7 92            [ 4]  878 	sub	a, d
   0FA8 30 12         [12]  879 	jr	NC,00101$
                            880 ;src/drawing.c:315: ClearBalloon(itBalloon);
   0FAA C5            [11]  881 	push	bc
   0FAB D5            [11]  882 	push	de
   0FAC C5            [11]  883 	push	bc
   0FAD CD F6 0B      [17]  884 	call	_ClearBalloon
   0FB0 F1            [10]  885 	pop	af
   0FB1 D1            [10]  886 	pop	de
   0FB2 C1            [10]  887 	pop	bc
                            888 ;src/drawing.c:316: itBalloon++;
   0FB3 21 08 00      [10]  889 	ld	hl, #0x0008
   0FB6 09            [11]  890 	add	hl,bc
   0FB7 4D            [ 4]  891 	ld	c, l
   0FB8 44            [ 4]  892 	ld	b, h
                            893 ;src/drawing.c:313: for (u8 i = 0; i < gBalloons.nb; i++)
   0FB9 1C            [ 4]  894 	inc	e
   0FBA 18 E6         [12]  895 	jr	00107$
   0FBC                     896 00101$:
                            897 ;src/drawing.c:320: DrawCloud();
   0FBC CD 7F 0F      [17]  898 	call	_DrawCloud
                            899 ;src/drawing.c:323: itBalloon = gBalloons.balloons; // Get first balloon pointer
   0FBF 01 9C 16      [10]  900 	ld	bc, #(_gBalloons + 0x0001)
                            901 ;src/drawing.c:324: for (u8 i = 0; i < gBalloons.nb; i++)
   0FC2 DD 36 FF 00   [19]  902 	ld	-1 (ix), #0x00
   0FC6                     903 00110$:
   0FC6 21 9B 16      [10]  904 	ld	hl, #_gBalloons + 0
   0FC9 5E            [ 7]  905 	ld	e, (hl)
   0FCA DD 7E FF      [19]  906 	ld	a, -1 (ix)
   0FCD 93            [ 4]  907 	sub	a, e
   0FCE 30 35         [12]  908 	jr	NC,00112$
                            909 ;src/drawing.c:327: if (itBalloon->color > 1) // Color 0 and 1 are default color balloon
   0FD0 C5            [11]  910 	push	bc
   0FD1 FD E1         [14]  911 	pop	iy
   0FD3 FD 56 06      [19]  912 	ld	d, 6 (iy)
   0FD6 3E 01         [ 7]  913 	ld	a, #0x01
   0FD8 92            [ 4]  914 	sub	a, d
   0FD9 30 13         [12]  915 	jr	NC,00103$
                            916 ;src/drawing.c:329: u8* sprite = ColorSprite(itBalloon->color); // Change colors of balloon
   0FDB C5            [11]  917 	push	bc
   0FDC D5            [11]  918 	push	de
   0FDD 33            [ 6]  919 	inc	sp
   0FDE CD 7C 0B      [17]  920 	call	_ColorSprite
   0FE1 33            [ 6]  921 	inc	sp
   0FE2 C1            [10]  922 	pop	bc
                            923 ;src/drawing.c:330: DrawBalloon(itBalloon, sprite);              // And draw colored balloon
   0FE3 C5            [11]  924 	push	bc
   0FE4 E5            [11]  925 	push	hl
   0FE5 C5            [11]  926 	push	bc
   0FE6 CD EF 0D      [17]  927 	call	_DrawBalloon
   0FE9 F1            [10]  928 	pop	af
   0FEA F1            [10]  929 	pop	af
   0FEB C1            [10]  930 	pop	bc
   0FEC 18 0C         [12]  931 	jr	00104$
   0FEE                     932 00103$:
                            933 ;src/drawing.c:333: DrawBalloon(itBalloon, g_balloon);           // Draw default balloon sprite (blue)
   0FEE C5            [11]  934 	push	bc
   0FEF 21 06 0A      [10]  935 	ld	hl, #_g_balloon
   0FF2 E5            [11]  936 	push	hl
   0FF3 C5            [11]  937 	push	bc
   0FF4 CD EF 0D      [17]  938 	call	_DrawBalloon
   0FF7 F1            [10]  939 	pop	af
   0FF8 F1            [10]  940 	pop	af
   0FF9 C1            [10]  941 	pop	bc
   0FFA                     942 00104$:
                            943 ;src/drawing.c:335: itBalloon++; // Get next balloon
   0FFA 21 08 00      [10]  944 	ld	hl, #0x0008
   0FFD 09            [11]  945 	add	hl,bc
   0FFE 4D            [ 4]  946 	ld	c, l
   0FFF 44            [ 4]  947 	ld	b, h
                            948 ;src/drawing.c:324: for (u8 i = 0; i < gBalloons.nb; i++)
   1000 DD 34 FF      [23]  949 	inc	-1 (ix)
   1003 18 C1         [12]  950 	jr	00110$
   1005                     951 00112$:
   1005 33            [ 6]  952 	inc	sp
   1006 DD E1         [14]  953 	pop	ix
   1008 C9            [10]  954 	ret
                            955 ;src/drawing.c:342: void DrawBackground()
                            956 ;	---------------------------------
                            957 ; Function DrawBackground
                            958 ; ---------------------------------
   1009                     959 _DrawBackground::
                            960 ;src/drawing.c:347: cpct_memset((u8*)SCREEN_BUFF, gBackGroundColor, VMEM_SIZE);
   1009 21 00 40      [10]  961 	ld	hl, #0x4000
   100C E5            [11]  962 	push	hl
   100D 3A 98 16      [13]  963 	ld	a, (_gBackGroundColor)
   1010 F5            [11]  964 	push	af
   1011 33            [ 6]  965 	inc	sp
   1012 26 80         [ 7]  966 	ld	h, #0x80
   1014 E5            [11]  967 	push	hl
   1015 CD 85 13      [17]  968 	call	_cpct_memset
                            969 ;src/drawing.c:350: pvmem = GetBackBufferPtr(0, SCREEN_CY - G_ROOF_H);
   1018 21 00 B4      [10]  970 	ld	hl, #0xb400
   101B E5            [11]  971 	push	hl
   101C CD A3 10      [17]  972 	call	_GetBackBufferPtr
   101F F1            [10]  973 	pop	af
   1020 4D            [ 4]  974 	ld	c, l
   1021 44            [ 4]  975 	ld	b, h
                            976 ;src/drawing.c:351: cpct_drawSprite(g_roof, pvmem, G_ROOF_W, G_ROOF_H);
   1022 59            [ 4]  977 	ld	e, c
   1023 50            [ 4]  978 	ld	d, b
   1024 C5            [11]  979 	push	bc
   1025 21 28 14      [10]  980 	ld	hl, #0x1428
   1028 E5            [11]  981 	push	hl
   1029 D5            [11]  982 	push	de
   102A 21 CA 06      [10]  983 	ld	hl, #_g_roof
   102D E5            [11]  984 	push	hl
   102E CD E7 10      [17]  985 	call	_cpct_drawSprite
   1031 C1            [10]  986 	pop	bc
                            987 ;src/drawing.c:354: pvmem += G_ROOF_W;
   1032 21 28 00      [10]  988 	ld	hl, #0x0028
   1035 09            [11]  989 	add	hl, bc
                            990 ;src/drawing.c:355: cpct_drawSprite(g_roof, pvmem, G_ROOF_W, G_ROOF_H);
   1036 01 28 14      [10]  991 	ld	bc, #0x1428
   1039 C5            [11]  992 	push	bc
   103A E5            [11]  993 	push	hl
   103B 21 CA 06      [10]  994 	ld	hl, #_g_roof
   103E E5            [11]  995 	push	hl
   103F CD E7 10      [17]  996 	call	_cpct_drawSprite
                            997 ;src/drawing.c:358: cpct_memcpy(CPCT_VMEM_START, (u8*)SCREEN_BUFF, VMEM_SIZE);
   1042 21 00 40      [10]  998 	ld	hl, #0x4000
   1045 E5            [11]  999 	push	hl
   1046 26 80         [ 7] 1000 	ld	h, #0x80
   1048 E5            [11] 1001 	push	hl
   1049 26 C0         [ 7] 1002 	ld	h, #0xc0
   104B E5            [11] 1003 	push	hl
   104C CD 7D 13      [17] 1004 	call	_cpct_memcpy
   104F C9            [10] 1005 	ret
                           1006 ;src/drawing.c:366: void InitializeDrawing()
                           1007 ;	---------------------------------
                           1008 ; Function InitializeDrawing
                           1009 ; ---------------------------------
   1050                    1010 _InitializeDrawing::
                           1011 ;src/drawing.c:368: gBackGroundColor = cpctm_px2byteM0(14, 14);             // Get byte color of background for M0
   1050 21 98 16      [10] 1012 	ld	hl,#_gBackGroundColor + 0
   1053 36 3F         [10] 1013 	ld	(hl), #0x3f
                           1014 ;src/drawing.c:369: gBalloons.nb = 0;                                       // No balloon to draw at start
   1055 21 9B 16      [10] 1015 	ld	hl, #_gBalloons
   1058 36 00         [10] 1016 	ld	(hl), #0x00
                           1017 ;src/drawing.c:370: DrawBackground();                                       // Set background on both buffers
   105A C3 09 10      [10] 1018 	jp  _DrawBackground
                           1019 	.area _CODE
                           1020 	.area _INITIALIZER
                           1021 	.area _CABS (ABS)
