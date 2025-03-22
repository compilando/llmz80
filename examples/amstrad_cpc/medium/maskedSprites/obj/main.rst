                              1 ;--------------------------------------------------------
                              2 ; File Created by SDCC : free open source ANSI-C Compiler
                              3 ; Version 3.6.8 #9946 (Linux)
                              4 ;--------------------------------------------------------
                              5 	.module main
                              6 	.optsdcc -mz80
                              7 	
                              8 ;--------------------------------------------------------
                              9 ; Public variables in this module
                             10 ;--------------------------------------------------------
                             11 	.globl _main
                             12 	.globl _initialization
                             13 	.globl _repaintBackgroundOverSprite
                             14 	.globl _drawBackground
                             15 	.globl _drawFrame
                             16 	.globl _cpct_getScreenPtr
                             17 	.globl _cpct_setPALColour
                             18 	.globl _cpct_setPalette
                             19 	.globl _cpct_fw2hw
                             20 	.globl _cpct_waitVSYNC
                             21 	.globl _cpct_setVideoMode
                             22 	.globl _cpct_drawSpriteMasked
                             23 	.globl _cpct_drawSolidBox
                             24 	.globl _cpct_px2byteM0
                             25 	.globl _cpct_drawTileAligned4x8_f
                             26 	.globl _cpct_disableFirmware
                             27 ;--------------------------------------------------------
                             28 ; special function registers
                             29 ;--------------------------------------------------------
                             30 ;--------------------------------------------------------
                             31 ; ram data
                             32 ;--------------------------------------------------------
                             33 	.area _DATA
                             34 ;--------------------------------------------------------
                             35 ; ram data
                             36 ;--------------------------------------------------------
                             37 	.area _INITIALIZED
                             38 ;--------------------------------------------------------
                             39 ; absolute external ram data
                             40 ;--------------------------------------------------------
                             41 	.area _DABS (ABS)
                             42 ;--------------------------------------------------------
                             43 ; global & static initialisations
                             44 ;--------------------------------------------------------
                             45 	.area _HOME
                             46 	.area _GSINIT
                             47 	.area _GSFINAL
                             48 	.area _GSINIT
                             49 ;--------------------------------------------------------
                             50 ; Home
                             51 ;--------------------------------------------------------
                             52 	.area _HOME
                             53 	.area _HOME
                             54 ;--------------------------------------------------------
                             55 ; code
                             56 ;--------------------------------------------------------
                             57 	.area _CODE
                             58 ;src/main.c:41: void drawFrame() {
                             59 ;	---------------------------------
                             60 ; Function drawFrame
                             61 ; ---------------------------------
   0100                      62 _drawFrame::
                             63 ;src/main.c:46: pattern = cpct_px2byteM0 (15, 15);
   0100 21 0F 0F      [10]   64 	ld	hl, #0x0f0f
   0103 E5            [11]   65 	push	hl
   0104 CD 9E 0F      [17]   66 	call	_cpct_px2byteM0
   0107 4D            [ 4]   67 	ld	c, l
                             68 ;src/main.c:49: pvmem = cpct_getScreenPtr(CPCT_VMEM_START, (BACK_X),  (BACK_Y - 8) );
   0108 C5            [11]   69 	push	bc
   0109 21 0C 40      [10]   70 	ld	hl, #0x400c
   010C E5            [11]   71 	push	hl
   010D 21 00 C0      [10]   72 	ld	hl, #0xc000
   0110 E5            [11]   73 	push	hl
   0111 CD 72 10      [17]   74 	call	_cpct_getScreenPtr
   0114 C1            [10]   75 	pop	bc
                             76 ;src/main.c:50: cpct_drawSolidBox(pvmem, pattern, 4*BACK_W,  8);
   0115 06 00         [ 7]   77 	ld	b, #0x00
   0117 C5            [11]   78 	push	bc
   0118 11 38 08      [10]   79 	ld	de, #0x0838
   011B D5            [11]   80 	push	de
   011C C5            [11]   81 	push	bc
   011D E5            [11]   82 	push	hl
   011E CD CA 0F      [17]   83 	call	_cpct_drawSolidBox
   0121 21 0C 78      [10]   84 	ld	hl, #0x780c
   0124 E5            [11]   85 	push	hl
   0125 21 00 C0      [10]   86 	ld	hl, #0xc000
   0128 E5            [11]   87 	push	hl
   0129 CD 72 10      [17]   88 	call	_cpct_getScreenPtr
   012C C1            [10]   89 	pop	bc
                             90 ;src/main.c:54: cpct_drawSolidBox(pvmem, pattern, 4*BACK_W,  8);
   012D C5            [11]   91 	push	bc
   012E 11 38 08      [10]   92 	ld	de, #0x0838
   0131 D5            [11]   93 	push	de
   0132 C5            [11]   94 	push	bc
   0133 E5            [11]   95 	push	hl
   0134 CD CA 0F      [17]   96 	call	_cpct_drawSolidBox
   0137 21 08 40      [10]   97 	ld	hl, #0x4008
   013A E5            [11]   98 	push	hl
   013B 21 00 C0      [10]   99 	ld	hl, #0xc000
   013E E5            [11]  100 	push	hl
   013F CD 72 10      [17]  101 	call	_cpct_getScreenPtr
   0142 C1            [10]  102 	pop	bc
                            103 ;src/main.c:58: cpct_drawSolidBox(pvmem, pattern,  4, 8*(BACK_H + 2) );
   0143 C5            [11]  104 	push	bc
   0144 11 04 40      [10]  105 	ld	de, #0x4004
   0147 D5            [11]  106 	push	de
   0148 C5            [11]  107 	push	bc
   0149 E5            [11]  108 	push	hl
   014A CD CA 0F      [17]  109 	call	_cpct_drawSolidBox
   014D 21 44 40      [10]  110 	ld	hl, #0x4044
   0150 E5            [11]  111 	push	hl
   0151 21 00 C0      [10]  112 	ld	hl, #0xc000
   0154 E5            [11]  113 	push	hl
   0155 CD 72 10      [17]  114 	call	_cpct_getScreenPtr
   0158 C1            [10]  115 	pop	bc
                            116 ;src/main.c:62: cpct_drawSolidBox(pvmem, pattern,  4, 8*(BACK_H + 2) );
   0159 11 04 40      [10]  117 	ld	de, #0x4004
   015C D5            [11]  118 	push	de
   015D C5            [11]  119 	push	bc
   015E E5            [11]  120 	push	hl
   015F CD CA 0F      [17]  121 	call	_cpct_drawSolidBox
   0162 C9            [10]  122 	ret
                            123 ;src/main.c:70: void drawBackground() {
                            124 ;	---------------------------------
                            125 ; Function drawBackground
                            126 ; ---------------------------------
   0163                     127 _drawBackground::
   0163 DD E5         [15]  128 	push	ix
   0165 DD 21 00 00   [14]  129 	ld	ix,#0
   0169 DD 39         [15]  130 	add	ix,sp
   016B 3B            [ 6]  131 	dec	sp
                            132 ;src/main.c:77: for (y=0; y < BACK_H; ++y) {     
   016C 0E 00         [ 7]  133 	ld	c, #0x00
   016E                     134 00105$:
                            135 ;src/main.c:82: pvideomem = cpct_getScreenPtr(CPCT_VMEM_START, BACK_X, BACK_Y + 8*y);
   016E 79            [ 4]  136 	ld	a, c
   016F 07            [ 4]  137 	rlca
   0170 07            [ 4]  138 	rlca
   0171 07            [ 4]  139 	rlca
   0172 E6 F8         [ 7]  140 	and	a, #0xf8
   0174 C6 48         [ 7]  141 	add	a, #0x48
   0176 47            [ 4]  142 	ld	b, a
   0177 C5            [11]  143 	push	bc
   0178 C5            [11]  144 	push	bc
   0179 33            [ 6]  145 	inc	sp
   017A 3E 0C         [ 7]  146 	ld	a, #0x0c
   017C F5            [11]  147 	push	af
   017D 33            [ 6]  148 	inc	sp
   017E 21 00 C0      [10]  149 	ld	hl, #0xc000
   0181 E5            [11]  150 	push	hl
   0182 CD 72 10      [17]  151 	call	_cpct_getScreenPtr
   0185 EB            [ 4]  152 	ex	de,hl
   0186 C1            [10]  153 	pop	bc
                            154 ;src/main.c:85: for(x=0; x < BACK_W; ++x) {
   0187 79            [ 4]  155 	ld	a, c
   0188 0F            [ 4]  156 	rrca
   0189 0F            [ 4]  157 	rrca
   018A 0F            [ 4]  158 	rrca
   018B E6 E0         [ 7]  159 	and	a, #0xe0
   018D DD 77 FF      [19]  160 	ld	-1 (ix), a
   0190 06 00         [ 7]  161 	ld	b, #0x00
   0192                     162 00103$:
                            163 ;src/main.c:86: cpct_drawTileAligned4x8_f(G_background[x][y], pvideomem);  // Draw next tile
   0192 D5            [11]  164 	push	de
   0193 FD E1         [14]  165 	pop	iy
   0195 D5            [11]  166 	push	de
   0196 58            [ 4]  167 	ld	e,b
   0197 16 00         [ 7]  168 	ld	d,#0x00
   0199 6B            [ 4]  169 	ld	l, e
   019A 62            [ 4]  170 	ld	h, d
   019B 29            [11]  171 	add	hl, hl
   019C 19            [11]  172 	add	hl, de
   019D 29            [11]  173 	add	hl, hl
   019E 29            [11]  174 	add	hl, hl
   019F 29            [11]  175 	add	hl, hl
   01A0 29            [11]  176 	add	hl, hl
   01A1 29            [11]  177 	add	hl, hl
   01A2 29            [11]  178 	add	hl, hl
   01A3 D1            [10]  179 	pop	de
   01A4 3E 93         [ 7]  180 	ld	a, #<(_G_background)
   01A6 85            [ 4]  181 	add	a, l
   01A7 6F            [ 4]  182 	ld	l, a
   01A8 3E 03         [ 7]  183 	ld	a, #>(_G_background)
   01AA 8C            [ 4]  184 	adc	a, h
   01AB 67            [ 4]  185 	ld	h, a
   01AC DD 7E FF      [19]  186 	ld	a, -1 (ix)
   01AF 85            [ 4]  187 	add	a, l
   01B0 6F            [ 4]  188 	ld	l, a
   01B1 3E 00         [ 7]  189 	ld	a, #0x00
   01B3 8C            [ 4]  190 	adc	a, h
   01B4 67            [ 4]  191 	ld	h, a
   01B5 C5            [11]  192 	push	bc
   01B6 D5            [11]  193 	push	de
   01B7 FD E5         [15]  194 	push	iy
   01B9 E5            [11]  195 	push	hl
   01BA CD A3 0E      [17]  196 	call	_cpct_drawTileAligned4x8_f
   01BD D1            [10]  197 	pop	de
   01BE C1            [10]  198 	pop	bc
                            199 ;src/main.c:90: pvideomem += 4;  
   01BF 13            [ 6]  200 	inc	de
   01C0 13            [ 6]  201 	inc	de
   01C1 13            [ 6]  202 	inc	de
   01C2 13            [ 6]  203 	inc	de
                            204 ;src/main.c:85: for(x=0; x < BACK_W; ++x) {
   01C3 04            [ 4]  205 	inc	b
   01C4 78            [ 4]  206 	ld	a, b
   01C5 D6 0E         [ 7]  207 	sub	a, #0x0e
   01C7 38 C9         [12]  208 	jr	C,00103$
                            209 ;src/main.c:77: for (y=0; y < BACK_H; ++y) {     
   01C9 0C            [ 4]  210 	inc	c
   01CA 79            [ 4]  211 	ld	a, c
   01CB D6 06         [ 7]  212 	sub	a, #0x06
   01CD 38 9F         [12]  213 	jr	C,00105$
   01CF 33            [ 6]  214 	inc	sp
   01D0 DD E1         [14]  215 	pop	ix
   01D2 C9            [10]  216 	ret
                            217 ;src/main.c:101: void repaintBackgroundOverSprite(u8 x, u8 y) {
                            218 ;	---------------------------------
                            219 ; Function repaintBackgroundOverSprite
                            220 ; ---------------------------------
   01D3                     221 _repaintBackgroundOverSprite::
   01D3 DD E5         [15]  222 	push	ix
   01D5 DD 21 00 00   [14]  223 	ld	ix,#0
   01D9 DD 39         [15]  224 	add	ix,sp
   01DB 21 F7 FF      [10]  225 	ld	hl, #-9
   01DE 39            [11]  226 	add	hl, sp
   01DF F9            [ 6]  227 	ld	sp, hl
                            228 ;src/main.c:106: u8 tilex = (x - BACK_X) / 4;   // Calculate tile column into the tile array (integer division, 4 bytes per tile)
   01E0 DD 4E 04      [19]  229 	ld	c, 4 (ix)
   01E3 06 00         [ 7]  230 	ld	b, #0x00
   01E5 79            [ 4]  231 	ld	a, c
   01E6 C6 F4         [ 7]  232 	add	a, #0xf4
   01E8 5F            [ 4]  233 	ld	e, a
   01E9 78            [ 4]  234 	ld	a, b
   01EA CE FF         [ 7]  235 	adc	a, #0xff
   01EC 57            [ 4]  236 	ld	d, a
   01ED 6B            [ 4]  237 	ld	l, e
   01EE 62            [ 4]  238 	ld	h, d
   01EF CB 7A         [ 8]  239 	bit	7, d
   01F1 28 04         [12]  240 	jr	Z,00103$
   01F3 21 F7 FF      [10]  241 	ld	hl, #0xfff7
   01F6 09            [11]  242 	add	hl, bc
   01F7                     243 00103$:
   01F7 CB 2C         [ 8]  244 	sra	h
   01F9 CB 1D         [ 8]  245 	rr	l
   01FB CB 2C         [ 8]  246 	sra	h
   01FD CB 1D         [ 8]  247 	rr	l
   01FF DD 75 F8      [19]  248 	ld	-8 (ix), l
                            249 ;src/main.c:107: u8 tiley = (y - BACK_Y) / 8;   // Calculate tile row into the tile array (integer division, 8 bytes per tile)
   0202 DD 4E 05      [19]  250 	ld	c, 5 (ix)
   0205 06 00         [ 7]  251 	ld	b, #0x00
   0207 79            [ 4]  252 	ld	a, c
   0208 C6 B8         [ 7]  253 	add	a, #0xb8
   020A 5F            [ 4]  254 	ld	e, a
   020B 78            [ 4]  255 	ld	a, b
   020C CE FF         [ 7]  256 	adc	a, #0xff
   020E 57            [ 4]  257 	ld	d, a
   020F 6B            [ 4]  258 	ld	l, e
   0210 62            [ 4]  259 	ld	h, d
   0211 CB 7A         [ 8]  260 	bit	7, d
   0213 28 04         [12]  261 	jr	Z,00104$
   0215 21 BF FF      [10]  262 	ld	hl, #0xffbf
   0218 09            [11]  263 	add	hl, bc
   0219                     264 00104$:
   0219 CB 2C         [ 8]  265 	sra	h
   021B CB 1D         [ 8]  266 	rr	l
   021D CB 2C         [ 8]  267 	sra	h
   021F CB 1D         [ 8]  268 	rr	l
   0221 CB 2C         [ 8]  269 	sra	h
   0223 CB 1D         [ 8]  270 	rr	l
   0225 DD 75 F7      [19]  271 	ld	-9 (ix), l
                            272 ;src/main.c:108: u8 scrx = BACK_X + 4*tilex;    // Calculate x screen byte coordinate of the tile
   0228 DD 7E F8      [19]  273 	ld	a, -8 (ix)
   022B 87            [ 4]  274 	add	a, a
   022C 87            [ 4]  275 	add	a, a
   022D C6 0C         [ 7]  276 	add	a, #0x0c
   022F DD 77 F9      [19]  277 	ld	-7 (ix), a
                            278 ;src/main.c:109: u8 scry = BACK_Y + 8*tiley;    // Calculate y screen byte coordinate of the tile
   0232 DD 7E F7      [19]  279 	ld	a, -9 (ix)
   0235 07            [ 4]  280 	rlca
   0236 07            [ 4]  281 	rlca
   0237 07            [ 4]  282 	rlca
   0238 E6 F8         [ 7]  283 	and	a, #0xf8
   023A C6 48         [ 7]  284 	add	a, #0x48
                            285 ;src/main.c:116: pvmem = cpct_getScreenPtr(CPCT_VMEM_START, scrx, scry);
   023C DD 77 FA      [19]  286 	ld	-6 (ix), a
   023F F5            [11]  287 	push	af
   0240 33            [ 6]  288 	inc	sp
   0241 DD 7E F9      [19]  289 	ld	a, -7 (ix)
   0244 F5            [11]  290 	push	af
   0245 33            [ 6]  291 	inc	sp
   0246 21 00 C0      [10]  292 	ld	hl, #0xc000
   0249 E5            [11]  293 	push	hl
   024A CD 72 10      [17]  294 	call	_cpct_getScreenPtr
   024D EB            [ 4]  295 	ex	de,hl
                            296 ;src/main.c:117: cpct_drawTileAligned4x8_f(G_background[tilex  ][tiley], pvmem    );
   024E 4B            [ 4]  297 	ld	c, e
   024F 42            [ 4]  298 	ld	b, d
   0250 D5            [11]  299 	push	de
   0251 DD 5E F8      [19]  300 	ld	e,-8 (ix)
   0254 16 00         [ 7]  301 	ld	d,#0x00
   0256 6B            [ 4]  302 	ld	l, e
   0257 62            [ 4]  303 	ld	h, d
   0258 29            [11]  304 	add	hl, hl
   0259 19            [11]  305 	add	hl, de
   025A 29            [11]  306 	add	hl, hl
   025B 29            [11]  307 	add	hl, hl
   025C 29            [11]  308 	add	hl, hl
   025D 29            [11]  309 	add	hl, hl
   025E 29            [11]  310 	add	hl, hl
   025F 29            [11]  311 	add	hl, hl
   0260 D1            [10]  312 	pop	de
   0261 3E 93         [ 7]  313 	ld	a, #<(_G_background)
   0263 85            [ 4]  314 	add	a, l
   0264 DD 77 FE      [19]  315 	ld	-2 (ix), a
   0267 3E 03         [ 7]  316 	ld	a, #>(_G_background)
   0269 8C            [ 4]  317 	adc	a, h
   026A DD 77 FF      [19]  318 	ld	-1 (ix), a
   026D DD 7E F7      [19]  319 	ld	a, -9 (ix)
   0270 0F            [ 4]  320 	rrca
   0271 0F            [ 4]  321 	rrca
   0272 0F            [ 4]  322 	rrca
   0273 E6 E0         [ 7]  323 	and	a, #0xe0
   0275 DD 77 FB      [19]  324 	ld	-5 (ix), a
   0278 DD 7E FE      [19]  325 	ld	a, -2 (ix)
   027B DD 86 FB      [19]  326 	add	a, -5 (ix)
   027E 6F            [ 4]  327 	ld	l, a
   027F DD 7E FF      [19]  328 	ld	a, -1 (ix)
   0282 CE 00         [ 7]  329 	adc	a, #0x00
   0284 67            [ 4]  330 	ld	h, a
   0285 D5            [11]  331 	push	de
   0286 C5            [11]  332 	push	bc
   0287 E5            [11]  333 	push	hl
   0288 CD A3 0E      [17]  334 	call	_cpct_drawTileAligned4x8_f
   028B D1            [10]  335 	pop	de
                            336 ;src/main.c:118: cpct_drawTileAligned4x8_f(G_background[tilex+1][tiley], pvmem + 4);
   028C 13            [ 6]  337 	inc	de
   028D 13            [ 6]  338 	inc	de
   028E 13            [ 6]  339 	inc	de
   028F 13            [ 6]  340 	inc	de
   0290 DD 4E F8      [19]  341 	ld	c, -8 (ix)
   0293 06 00         [ 7]  342 	ld	b, #0x00
   0295 03            [ 6]  343 	inc	bc
   0296 69            [ 4]  344 	ld	l, c
   0297 60            [ 4]  345 	ld	h, b
   0298 29            [11]  346 	add	hl, hl
   0299 09            [11]  347 	add	hl, bc
   029A 29            [11]  348 	add	hl, hl
   029B 29            [11]  349 	add	hl, hl
   029C 29            [11]  350 	add	hl, hl
   029D 29            [11]  351 	add	hl, hl
   029E 29            [11]  352 	add	hl, hl
   029F 29            [11]  353 	add	hl, hl
   02A0 01 93 03      [10]  354 	ld	bc,#_G_background
   02A3 09            [11]  355 	add	hl,bc
   02A4 DD 75 FC      [19]  356 	ld	-4 (ix), l
   02A7 DD 74 FD      [19]  357 	ld	-3 (ix), h
   02AA DD 7E FB      [19]  358 	ld	a, -5 (ix)
   02AD DD 86 FC      [19]  359 	add	a, -4 (ix)
   02B0 4F            [ 4]  360 	ld	c, a
   02B1 3E 00         [ 7]  361 	ld	a, #0x00
   02B3 DD 8E FD      [19]  362 	adc	a, -3 (ix)
   02B6 47            [ 4]  363 	ld	b, a
   02B7 D5            [11]  364 	push	de
   02B8 C5            [11]  365 	push	bc
   02B9 CD A3 0E      [17]  366 	call	_cpct_drawTileAligned4x8_f
                            367 ;src/main.c:119: pvmem = cpct_getScreenPtr(CPCT_VMEM_START, scrx, scry + 8);
   02BC DD 7E FA      [19]  368 	ld	a, -6 (ix)
   02BF C6 08         [ 7]  369 	add	a, #0x08
   02C1 47            [ 4]  370 	ld	b, a
   02C2 C5            [11]  371 	push	bc
   02C3 33            [ 6]  372 	inc	sp
   02C4 DD 7E F9      [19]  373 	ld	a, -7 (ix)
   02C7 F5            [11]  374 	push	af
   02C8 33            [ 6]  375 	inc	sp
   02C9 21 00 C0      [10]  376 	ld	hl, #0xc000
   02CC E5            [11]  377 	push	hl
   02CD CD 72 10      [17]  378 	call	_cpct_getScreenPtr
                            379 ;src/main.c:120: cpct_drawTileAligned4x8_f(G_background[tilex  ][tiley+1], pvmem    );
   02D0 5D            [ 4]  380 	ld	e, l
   02D1 54            [ 4]  381 	ld	d, h
   02D2 DD 7E F7      [19]  382 	ld	a, -9 (ix)
   02D5 3C            [ 4]  383 	inc	a
   02D6 0F            [ 4]  384 	rrca
   02D7 0F            [ 4]  385 	rrca
   02D8 0F            [ 4]  386 	rrca
   02D9 E6 E0         [ 7]  387 	and	a, #0xe0
   02DB DD 77 FB      [19]  388 	ld	-5 (ix), a
   02DE DD 7E FE      [19]  389 	ld	a, -2 (ix)
   02E1 DD 86 FB      [19]  390 	add	a, -5 (ix)
   02E4 4F            [ 4]  391 	ld	c, a
   02E5 DD 7E FF      [19]  392 	ld	a, -1 (ix)
   02E8 CE 00         [ 7]  393 	adc	a, #0x00
   02EA 47            [ 4]  394 	ld	b, a
   02EB E5            [11]  395 	push	hl
   02EC D5            [11]  396 	push	de
   02ED C5            [11]  397 	push	bc
   02EE CD A3 0E      [17]  398 	call	_cpct_drawTileAligned4x8_f
   02F1 E1            [10]  399 	pop	hl
                            400 ;src/main.c:121: cpct_drawTileAligned4x8_f(G_background[tilex+1][tiley+1], pvmem + 4);
   02F2 01 04 00      [10]  401 	ld	bc, #0x0004
   02F5 09            [11]  402 	add	hl, bc
   02F6 DD 7E FB      [19]  403 	ld	a, -5 (ix)
   02F9 DD 86 FC      [19]  404 	add	a, -4 (ix)
   02FC 4F            [ 4]  405 	ld	c, a
   02FD 3E 00         [ 7]  406 	ld	a, #0x00
   02FF DD 8E FD      [19]  407 	adc	a, -3 (ix)
   0302 47            [ 4]  408 	ld	b, a
   0303 E5            [11]  409 	push	hl
   0304 C5            [11]  410 	push	bc
   0305 CD A3 0E      [17]  411 	call	_cpct_drawTileAligned4x8_f
   0308 DD F9         [10]  412 	ld	sp, ix
   030A DD E1         [14]  413 	pop	ix
   030C C9            [10]  414 	ret
                            415 ;src/main.c:129: void initialization (){ 
                            416 ;	---------------------------------
                            417 ; Function initialization
                            418 ; ---------------------------------
   030D                     419 _initialization::
                            420 ;src/main.c:130: cpct_disableFirmware();          // Disable firmware to prevent it from interfering
   030D CD BA 0F      [17]  421 	call	_cpct_disableFirmware
                            422 ;src/main.c:131: cpct_fw2hw     (G_palette, 16);  // Convert firmware colours to hardware colours 
   0310 21 10 00      [10]  423 	ld	hl, #0x0010
   0313 E5            [11]  424 	push	hl
   0314 21 13 0E      [10]  425 	ld	hl, #_G_palette
   0317 E5            [11]  426 	push	hl
   0318 CD 2B 0F      [17]  427 	call	_cpct_fw2hw
                            428 ;src/main.c:132: cpct_setPalette(G_palette, 16);  // Set palette using hardware colour values
   031B 21 10 00      [10]  429 	ld	hl, #0x0010
   031E E5            [11]  430 	push	hl
   031F 21 13 0E      [10]  431 	ld	hl, #_G_palette
   0322 E5            [11]  432 	push	hl
   0323 CD 08 0F      [17]  433 	call	_cpct_setPalette
                            434 ;src/main.c:133: cpct_setBorder (G_palette[0]);   // Set border colour same as background (0)
   0326 21 13 0E      [10]  435 	ld	hl, #_G_palette + 0
   0329 46            [ 7]  436 	ld	b, (hl)
   032A C5            [11]  437 	push	bc
   032B 33            [ 6]  438 	inc	sp
   032C 3E 10         [ 7]  439 	ld	a, #0x10
   032E F5            [11]  440 	push	af
   032F 33            [ 6]  441 	inc	sp
   0330 CD 1F 0F      [17]  442 	call	_cpct_setPALColour
                            443 ;src/main.c:134: cpct_setVideoMode(0);            // Change to Mode 0 (160x200, 16 colours)
   0333 2E 00         [ 7]  444 	ld	l, #0x00
   0335 CD 90 0F      [17]  445 	call	_cpct_setVideoMode
                            446 ;src/main.c:136: drawFrame();       // Draw a Frame around the "play zone"
   0338 CD 00 01      [17]  447 	call	_drawFrame
                            448 ;src/main.c:137: drawBackground();  // Draw the tiled background
   033B CD 63 01      [17]  449 	call	_drawBackground
   033E C9            [10]  450 	ret
                            451 ;src/main.c:140: void main(void) {
                            452 ;	---------------------------------
                            453 ; Function main
                            454 ; ---------------------------------
   033F                     455 _main::
                            456 ;src/main.c:141: u8 x=BACK_X+1;   // x byte screen coord. of the sprite (1 byte to the right of the start of the "play zone")
                            457 ;src/main.c:143: i8 vx=1;         // Horizontal movement velocity in bytes (1 byte to the right)
   033F 01 01 0D      [10]  458 	ld	bc,#0x0d01
                            459 ;src/main.c:148: initialization();
   0342 C5            [11]  460 	push	bc
   0343 CD 0D 03      [17]  461 	call	_initialization
   0346 C1            [10]  462 	pop	bc
                            463 ;src/main.c:153: while(1) {
   0347                     464 00106$:
                            465 ;src/main.c:157: pvmem = cpct_getScreenPtr(CPCT_VMEM_START, x, y);      
   0347 C5            [11]  466 	push	bc
   0348 3E 68         [ 7]  467 	ld	a, #0x68
   034A F5            [11]  468 	push	af
   034B 33            [ 6]  469 	inc	sp
   034C C5            [11]  470 	push	bc
   034D 33            [ 6]  471 	inc	sp
   034E 21 00 C0      [10]  472 	ld	hl, #0xc000
   0351 E5            [11]  473 	push	hl
   0352 CD 72 10      [17]  474 	call	_cpct_getScreenPtr
   0355 EB            [ 4]  475 	ex	de,hl
   0356 21 04 10      [10]  476 	ld	hl, #0x1004
   0359 E5            [11]  477 	push	hl
   035A D5            [11]  478 	push	de
   035B 21 23 0E      [10]  479 	ld	hl, #_G_sprite_EMR
   035E E5            [11]  480 	push	hl
   035F CD 3E 0F      [17]  481 	call	_cpct_drawSpriteMasked
   0362 C1            [10]  482 	pop	bc
                            483 ;src/main.c:160: for(i=0; i < WAITLOOPS; i++); // Wait for a little while
   0363 11 A0 0F      [10]  484 	ld	de, #0x0fa0
   0366                     485 00110$:
   0366 EB            [ 4]  486 	ex	de,hl
   0367 2B            [ 6]  487 	dec	hl
   0368 5D            [ 4]  488 	ld	e, l
   0369 7C            [ 4]  489 	ld	a,h
   036A 57            [ 4]  490 	ld	d,a
   036B B5            [ 4]  491 	or	a,l
   036C 20 F8         [12]  492 	jr	NZ,00110$
                            493 ;src/main.c:161: cpct_waitVSYNC();             // Synchronize with VSYNC to prevent flickering
   036E C5            [11]  494 	push	bc
   036F CD 88 0F      [17]  495 	call	_cpct_waitVSYNC
   0372 C1            [10]  496 	pop	bc
                            497 ;src/main.c:163: repaintBackgroundOverSprite(x, y); // Repaint the background only where the sprite is located
   0373 C5            [11]  498 	push	bc
   0374 3E 68         [ 7]  499 	ld	a, #0x68
   0376 F5            [11]  500 	push	af
   0377 33            [ 6]  501 	inc	sp
   0378 C5            [11]  502 	push	bc
   0379 33            [ 6]  503 	inc	sp
   037A CD D3 01      [17]  504 	call	_repaintBackgroundOverSprite
   037D F1            [10]  505 	pop	af
   037E C1            [10]  506 	pop	bc
                            507 ;src/main.c:166: x += vx;
   037F 78            [ 4]  508 	ld	a, b
   0380 81            [ 4]  509 	add	a, c
                            510 ;src/main.c:170: if (x < BACK_X || x > (BACK_X + 4*BACK_W-5) ) {
   0381 47            [ 4]  511 	ld	b,a
   0382 D6 0C         [ 7]  512 	sub	a, #0x0c
   0384 38 05         [12]  513 	jr	C,00102$
   0386 3E 3F         [ 7]  514 	ld	a, #0x3f
   0388 90            [ 4]  515 	sub	a, b
   0389 30 BC         [12]  516 	jr	NC,00106$
   038B                     517 00102$:
                            518 ;src/main.c:171: x -= vx;    // Undo latest movement subtracting vx from current x position
   038B 78            [ 4]  519 	ld	a, b
   038C 91            [ 4]  520 	sub	a, c
   038D 47            [ 4]  521 	ld	b, a
                            522 ;src/main.c:172: vx = -vx;   // Change the sense of velocity to start moving opposite
   038E AF            [ 4]  523 	xor	a, a
   038F 91            [ 4]  524 	sub	a, c
   0390 4F            [ 4]  525 	ld	c, a
   0391 18 B4         [12]  526 	jr	00106$
                            527 	.area _CODE
                            528 	.area _INITIALIZER
                            529 	.area _CABS (ABS)
