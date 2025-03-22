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
                             12 	.globl _DrawBackground
                             13 	.globl _InitCapture
                             14 	.globl _DrawCity
                             15 	.globl _DrawSky
                             16 	.globl _DrawSkyGradient
                             17 	.globl _FillLine
                             18 	.globl _DrawUFO
                             19 	.globl _GetUfoSprite
                             20 	.globl _Initialization
                             21 	.globl _cpct_getScreenPtr
                             22 	.globl _cpct_setPALColour
                             23 	.globl _cpct_setPalette
                             24 	.globl _cpct_waitVSYNC
                             25 	.globl _cpct_setVideoMode
                             26 	.globl _cpct_drawSpriteMasked
                             27 	.globl _cpct_drawSprite
                             28 	.globl _cpct_px2byteM0
                             29 	.globl _cpct_getScreenToSprite
                             30 	.globl _cpct_memset
                             31 	.globl _cpct_disableFirmware
                             32 	.globl _gScreenCapture
                             33 ;--------------------------------------------------------
                             34 ; special function registers
                             35 ;--------------------------------------------------------
                             36 ;--------------------------------------------------------
                             37 ; ram data
                             38 ;--------------------------------------------------------
                             39 	.area _DATA
   5954                      40 _gScreenCapture::
   5954                      41 	.ds 336
   5AA4                      42 _GetUfoSprite_anim_1_129:
   5AA4                      43 	.ds 1
   5AA5                      44 _DrawUFO_moveRight_1_130:
   5AA5                      45 	.ds 1
   5AA6                      46 _DrawUFO_posX_1_130:
   5AA6                      47 	.ds 1
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
                             63 ;src/main.c:72: static u8 anim = 0;     // Currently selected animation sprite
   5AA7 FD 21 A4 5A   [14]   64 	ld	iy, #_GetUfoSprite_anim_1_129
   5AAB FD 36 00 00   [19]   65 	ld	0 (iy), #0x00
                             66 ;--------------------------------------------------------
                             67 ; Home
                             68 ;--------------------------------------------------------
                             69 	.area _HOME
                             70 	.area _HOME
                             71 ;--------------------------------------------------------
                             72 ; code
                             73 ;--------------------------------------------------------
                             74 	.area _CODE
                             75 ;src/main.c:57: void Initialization() {
                             76 ;	---------------------------------
                             77 ; Function Initialization
                             78 ; ---------------------------------
   5590                      79 _Initialization::
                             80 ;src/main.c:58: cpct_disableFirmware();            // Disable firmware to take full control of the CPC
   5590 CD 1D 59      [17]   81 	call	_cpct_disableFirmware
                             82 ;src/main.c:59: cpct_setVideoMode(0);              // Set mode 0
   5593 2E 00         [ 7]   83 	ld	l, #0x00
   5595 CD E5 58      [17]   84 	call	_cpct_setVideoMode
                             85 ;src/main.c:60: cpct_setPalette (g_palette, 16);   // Set the palette
   5598 21 10 00      [10]   86 	ld	hl, #0x0010
   559B E5            [11]   87 	push	hl
   559C 21 00 4B      [10]   88 	ld	hl, #_g_palette
   559F E5            [11]   89 	push	hl
   55A0 CD E6 57      [17]   90 	call	_cpct_setPalette
                             91 ;src/main.c:61: cpct_setBorder(HW_BLACK);          // Set the border color with Hardware color
   55A3 21 10 14      [10]   92 	ld	hl, #0x1410
   55A6 E5            [11]   93 	push	hl
   55A7 CD FD 57      [17]   94 	call	_cpct_setPALColour
                             95 ;src/main.c:64: cpct_memset(CPCT_VMEM_START, cpct_px2byteM0(4, 4), VMEM_SIZE);
   55AA 21 04 04      [10]   96 	ld	hl, #0x0404
   55AD E5            [11]   97 	push	hl
   55AE CD F3 58      [17]   98 	call	_cpct_px2byteM0
   55B1 45            [ 4]   99 	ld	b, l
   55B2 21 00 40      [10]  100 	ld	hl, #0x4000
   55B5 E5            [11]  101 	push	hl
   55B6 C5            [11]  102 	push	bc
   55B7 33            [ 6]  103 	inc	sp
   55B8 26 C0         [ 7]  104 	ld	h, #0xc0
   55BA E5            [11]  105 	push	hl
   55BB CD 0F 59      [17]  106 	call	_cpct_memset
   55BE C9            [10]  107 	ret
                            108 ;src/main.c:70: u8* GetUfoSprite() {
                            109 ;	---------------------------------
                            110 ; Function GetUfoSprite
                            111 ; ---------------------------------
   55BF                     112 _GetUfoSprite::
                            113 ;src/main.c:78: return ufoSprite[anim++ % 4];
   55BF 01 D9 55      [10]  114 	ld	bc, #_GetUfoSprite_ufoSprite_1_129+0
   55C2 FD 21 A4 5A   [14]  115 	ld	iy, #_GetUfoSprite_anim_1_129
   55C6 FD 5E 00      [19]  116 	ld	e, 0 (iy)
   55C9 FD 34 00      [23]  117 	inc	0 (iy)
   55CC 7B            [ 4]  118 	ld	a, e
   55CD E6 03         [ 7]  119 	and	a, #0x03
   55CF 6F            [ 4]  120 	ld	l, a
   55D0 26 00         [ 7]  121 	ld	h, #0x00
   55D2 29            [11]  122 	add	hl, hl
   55D3 09            [11]  123 	add	hl, bc
   55D4 4E            [ 7]  124 	ld	c, (hl)
   55D5 23            [ 6]  125 	inc	hl
   55D6 66            [ 7]  126 	ld	h, (hl)
   55D7 69            [ 4]  127 	ld	l, c
   55D8 C9            [10]  128 	ret
   55D9                     129 _GetUfoSprite_ufoSprite_1_129:
   55D9 10 4B               130 	.dw _g_ufo_0
   55DB B0 4D               131 	.dw _g_ufo_1
   55DD 50 50               132 	.dw _g_ufo_2
   55DF F0 52               133 	.dw _g_ufo_3
                            134 ;src/main.c:84: void DrawUFO() {
                            135 ;	---------------------------------
                            136 ; Function DrawUFO
                            137 ; ---------------------------------
   55E1                     138 _DrawUFO::
                            139 ;src/main.c:92: u8* pvmem_ufoBg = cpct_getScreenPtr(CPCT_VMEM_START, posX, UFO_Y);
   55E1 3E 78         [ 7]  140 	ld	a, #0x78
   55E3 F5            [11]  141 	push	af
   55E4 33            [ 6]  142 	inc	sp
   55E5 3A A6 5A      [13]  143 	ld	a, (_DrawUFO_posX_1_130)
   55E8 F5            [11]  144 	push	af
   55E9 33            [ 6]  145 	inc	sp
   55EA 21 00 C0      [10]  146 	ld	hl, #0xc000
   55ED E5            [11]  147 	push	hl
   55EE CD 2E 59      [17]  148 	call	_cpct_getScreenPtr
   55F1 EB            [ 4]  149 	ex	de,hl
                            150 ;src/main.c:99: if (moveRight) {
   55F2 3A A5 5A      [13]  151 	ld	a,(#_DrawUFO_moveRight_1_130 + 0)
   55F5 B7            [ 4]  152 	or	a, a
   55F6 28 14         [12]  153 	jr	Z,00108$
                            154 ;src/main.c:101: if (posX == SCREEN_CX - G_UFO_0_W)
   55F8 3A A6 5A      [13]  155 	ld	a,(#_DrawUFO_posX_1_130 + 0)
   55FB D6 40         [ 7]  156 	sub	a, #0x40
   55FD 20 07         [12]  157 	jr	NZ,00102$
                            158 ;src/main.c:102: moveRight = FALSE;   // Change direction
   55FF 21 A5 5A      [10]  159 	ld	hl,#_DrawUFO_moveRight_1_130 + 0
   5602 36 00         [10]  160 	ld	(hl), #0x00
   5604 18 17         [12]  161 	jr	00109$
   5606                     162 00102$:
                            163 ;src/main.c:104: posX++;              // Move to right
   5606 21 A6 5A      [10]  164 	ld	hl, #_DrawUFO_posX_1_130+0
   5609 34            [11]  165 	inc	(hl)
   560A 18 11         [12]  166 	jr	00109$
   560C                     167 00108$:
                            168 ;src/main.c:107: if (posX == 0)  moveRight = TRUE;   // Change direction
   560C 3A A6 5A      [13]  169 	ld	a,(#_DrawUFO_posX_1_130 + 0)
   560F B7            [ 4]  170 	or	a, a
   5610 20 07         [12]  171 	jr	NZ,00105$
   5612 21 A5 5A      [10]  172 	ld	hl,#_DrawUFO_moveRight_1_130 + 0
   5615 36 01         [10]  173 	ld	(hl), #0x01
   5617 18 04         [12]  174 	jr	00109$
   5619                     175 00105$:
                            176 ;src/main.c:108: else            posX--;             // Move to left
   5619 21 A6 5A      [10]  177 	ld	hl, #_DrawUFO_posX_1_130+0
   561C 35            [11]  178 	dec	(hl)
   561D                     179 00109$:
                            180 ;src/main.c:113: pvmem = cpct_getScreenPtr(CPCT_VMEM_START, posX, UFO_Y);
   561D D5            [11]  181 	push	de
   561E 3E 78         [ 7]  182 	ld	a, #0x78
   5620 F5            [11]  183 	push	af
   5621 33            [ 6]  184 	inc	sp
   5622 3A A6 5A      [13]  185 	ld	a, (_DrawUFO_posX_1_130)
   5625 F5            [11]  186 	push	af
   5626 33            [ 6]  187 	inc	sp
   5627 21 00 C0      [10]  188 	ld	hl, #0xc000
   562A E5            [11]  189 	push	hl
   562B CD 2E 59      [17]  190 	call	_cpct_getScreenPtr
   562E 4D            [ 4]  191 	ld	c, l
   562F 44            [ 4]  192 	ld	b, h
   5630 D1            [10]  193 	pop	de
                            194 ;src/main.c:118: cpct_waitVSYNC();
   5631 C5            [11]  195 	push	bc
   5632 D5            [11]  196 	push	de
   5633 CD DD 58      [17]  197 	call	_cpct_waitVSYNC
   5636 D1            [10]  198 	pop	de
   5637 21 10 15      [10]  199 	ld	hl, #0x1510
   563A E5            [11]  200 	push	hl
   563B D5            [11]  201 	push	de
   563C 21 54 59      [10]  202 	ld	hl, #_gScreenCapture
   563F E5            [11]  203 	push	hl
   5640 CD 09 58      [17]  204 	call	_cpct_drawSprite
   5643 C1            [10]  205 	pop	bc
                            206 ;src/main.c:128: cpct_getScreenToSprite(pvmem, gScreenCapture, G_UFO_0_W, G_UFO_0_H);
   5644 C5            [11]  207 	push	bc
   5645 21 10 15      [10]  208 	ld	hl, #0x1510
   5648 E5            [11]  209 	push	hl
   5649 21 54 59      [10]  210 	ld	hl, #_gScreenCapture
   564C E5            [11]  211 	push	hl
   564D C5            [11]  212 	push	bc
   564E CD BF 57      [17]  213 	call	_cpct_getScreenToSprite
   5651 CD BF 55      [17]  214 	call	_GetUfoSprite
   5654 C1            [10]  215 	pop	bc
   5655 11 10 15      [10]  216 	ld	de, #0x1510
   5658 D5            [11]  217 	push	de
   5659 C5            [11]  218 	push	bc
   565A E5            [11]  219 	push	hl
   565B CD AE 58      [17]  220 	call	_cpct_drawSpriteMasked
   565E C9            [10]  221 	ret
                            222 ;src/main.c:137: void FillLine(u8 pixColor, u8 lineY) {
                            223 ;	---------------------------------
                            224 ; Function FillLine
                            225 ; ---------------------------------
   565F                     226 _FillLine::
                            227 ;src/main.c:140: u8* pvmem = cpct_getScreenPtr(CPCT_VMEM_START, 0, lineY);
   565F 21 03 00      [10]  228 	ld	hl, #3+0
   5662 39            [11]  229 	add	hl, sp
   5663 7E            [ 7]  230 	ld	a, (hl)
   5664 F5            [11]  231 	push	af
   5665 33            [ 6]  232 	inc	sp
   5666 AF            [ 4]  233 	xor	a, a
   5667 F5            [11]  234 	push	af
   5668 33            [ 6]  235 	inc	sp
   5669 21 00 C0      [10]  236 	ld	hl, #0xc000
   566C E5            [11]  237 	push	hl
   566D CD 2E 59      [17]  238 	call	_cpct_getScreenPtr
   5670 4D            [ 4]  239 	ld	c, l
   5671 44            [ 4]  240 	ld	b, h
                            241 ;src/main.c:141: cpct_memset(pvmem, pixColor, SCREEN_CX);
   5672 21 50 00      [10]  242 	ld	hl, #0x0050
   5675 E5            [11]  243 	push	hl
   5676 21 04 00      [10]  244 	ld	hl, #4+0
   5679 39            [11]  245 	add	hl, sp
   567A 7E            [ 7]  246 	ld	a, (hl)
   567B F5            [11]  247 	push	af
   567C 33            [ 6]  248 	inc	sp
   567D C5            [11]  249 	push	bc
   567E CD 0F 59      [17]  250 	call	_cpct_memset
   5681 C9            [10]  251 	ret
                            252 ;src/main.c:147: u8 DrawSkyGradient(u8 cy, u8 posY, u8 colorFront, u8 colorBack) {
                            253 ;	---------------------------------
                            254 ; Function DrawSkyGradient
                            255 ; ---------------------------------
   5682                     256 _DrawSkyGradient::
   5682 DD E5         [15]  257 	push	ix
   5684 DD 21 00 00   [14]  258 	ld	ix,#0
   5688 DD 39         [15]  259 	add	ix,sp
   568A F5            [11]  260 	push	af
   568B F5            [11]  261 	push	af
                            262 ;src/main.c:151: u8 pixFront = cpct_px2byteM0(colorFront, colorFront);
   568C DD 66 06      [19]  263 	ld	h, 6 (ix)
   568F DD 6E 06      [19]  264 	ld	l, 6 (ix)
   5692 E5            [11]  265 	push	hl
   5693 CD F3 58      [17]  266 	call	_cpct_px2byteM0
   5696 DD 75 FC      [19]  267 	ld	-4 (ix), l
                            268 ;src/main.c:152: u8 pixBack  = cpct_px2byteM0(colorBack, colorBack);
   5699 DD 66 07      [19]  269 	ld	h, 7 (ix)
   569C DD 6E 07      [19]  270 	ld	l, 7 (ix)
   569F E5            [11]  271 	push	hl
   56A0 CD F3 58      [17]  272 	call	_cpct_px2byteM0
   56A3 45            [ 4]  273 	ld	b, l
                            274 ;src/main.c:155: for (j = 0; j < cy; j++) {
   56A4 0E 00         [ 7]  275 	ld	c, #0x00
   56A6                     276 00109$:
   56A6 79            [ 4]  277 	ld	a, c
   56A7 DD 96 04      [19]  278 	sub	a, 4 (ix)
   56AA 30 63         [12]  279 	jr	NC,00104$
                            280 ;src/main.c:157: if (posY == SCREEN_CY - 2)
   56AC DD 7E 05      [19]  281 	ld	a, 5 (ix)
   56AF D6 C6         [ 7]  282 	sub	a, #0xc6
   56B1 28 5C         [12]  283 	jr	Z,00104$
                            284 ;src/main.c:161: for (i = 0; i < cy - j; i++) {
   56B3 DD 56 05      [19]  285 	ld	d, 5 (ix)
   56B6 DD 36 FD 00   [19]  286 	ld	-3 (ix), #0x00
   56BA                     287 00106$:
   56BA DD 6E 04      [19]  288 	ld	l, 4 (ix)
   56BD 26 00         [ 7]  289 	ld	h, #0x00
   56BF DD 71 FE      [19]  290 	ld	-2 (ix), c
   56C2 DD 36 FF 00   [19]  291 	ld	-1 (ix), #0x00
   56C6 7D            [ 4]  292 	ld	a, l
   56C7 DD 96 FE      [19]  293 	sub	a, -2 (ix)
   56CA DD 77 FE      [19]  294 	ld	-2 (ix), a
   56CD 7C            [ 4]  295 	ld	a, h
   56CE DD 9E FF      [19]  296 	sbc	a, -1 (ix)
   56D1 DD 77 FF      [19]  297 	ld	-1 (ix), a
   56D4 DD 6E FD      [19]  298 	ld	l, -3 (ix)
   56D7 26 00         [ 7]  299 	ld	h, #0x00
                            300 ;src/main.c:162: FillLine(pixFront, posY++);      
   56D9 5A            [ 4]  301 	ld	e, d
   56DA 1C            [ 4]  302 	inc	e
                            303 ;src/main.c:161: for (i = 0; i < cy - j; i++) {
   56DB 7D            [ 4]  304 	ld	a, l
   56DC DD 96 FE      [19]  305 	sub	a, -2 (ix)
   56DF 7C            [ 4]  306 	ld	a, h
   56E0 DD 9E FF      [19]  307 	sbc	a, -1 (ix)
   56E3 E2 E8 56      [10]  308 	jp	PO, 00136$
   56E6 EE 80         [ 7]  309 	xor	a, #0x80
   56E8                     310 00136$:
   56E8 F2 01 57      [10]  311 	jp	P, 00103$
                            312 ;src/main.c:162: FillLine(pixFront, posY++);      
   56EB 62            [ 4]  313 	ld	h, d
   56EC 53            [ 4]  314 	ld	d, e
   56ED C5            [11]  315 	push	bc
   56EE D5            [11]  316 	push	de
   56EF E5            [11]  317 	push	hl
   56F0 33            [ 6]  318 	inc	sp
   56F1 DD 7E FC      [19]  319 	ld	a, -4 (ix)
   56F4 F5            [11]  320 	push	af
   56F5 33            [ 6]  321 	inc	sp
   56F6 CD 5F 56      [17]  322 	call	_FillLine
   56F9 F1            [10]  323 	pop	af
   56FA D1            [10]  324 	pop	de
   56FB C1            [10]  325 	pop	bc
                            326 ;src/main.c:161: for (i = 0; i < cy - j; i++) {
   56FC DD 34 FD      [23]  327 	inc	-3 (ix)
   56FF 18 B9         [12]  328 	jr	00106$
   5701                     329 00103$:
                            330 ;src/main.c:164: FillLine(pixBack, posY++); 
   5701 DD 73 05      [19]  331 	ld	5 (ix), e
   5704 C5            [11]  332 	push	bc
   5705 58            [ 4]  333 	ld	e, b
   5706 D5            [11]  334 	push	de
   5707 CD 5F 56      [17]  335 	call	_FillLine
   570A F1            [10]  336 	pop	af
   570B C1            [10]  337 	pop	bc
                            338 ;src/main.c:155: for (j = 0; j < cy; j++) {
   570C 0C            [ 4]  339 	inc	c
   570D 18 97         [12]  340 	jr	00109$
   570F                     341 00104$:
                            342 ;src/main.c:168: return posY;
   570F DD 6E 05      [19]  343 	ld	l, 5 (ix)
   5712 DD F9         [10]  344 	ld	sp, ix
   5714 DD E1         [14]  345 	pop	ix
   5716 C9            [10]  346 	ret
                            347 ;src/main.c:174: void DrawSky() {
                            348 ;	---------------------------------
                            349 ; Function DrawSky
                            350 ; ---------------------------------
   5717                     351 _DrawSky::
                            352 ;src/main.c:179: u8 startLine = 0;
                            353 ;src/main.c:183: for (i = 1; i < sizeof(colors); i++)
   5717 11 01 00      [10]  354 	ld	de,#0x0001
   571A                     355 00102$:
                            356 ;src/main.c:184: startLine = DrawSkyGradient(GRADIENT_CY - i, startLine, colors[i], colors[i - 1]);
   571A 4B            [ 4]  357 	ld	c, e
   571B 0D            [ 4]  358 	dec	c
   571C 21 47 57      [10]  359 	ld	hl, #_DrawSky_colors_1_141
   571F 06 00         [ 7]  360 	ld	b, #0x00
   5721 09            [11]  361 	add	hl, bc
   5722 4E            [ 7]  362 	ld	c, (hl)
   5723 3E 47         [ 7]  363 	ld	a, #<(_DrawSky_colors_1_141)
   5725 83            [ 4]  364 	add	a, e
   5726 6F            [ 4]  365 	ld	l, a
   5727 3E 57         [ 7]  366 	ld	a, #>(_DrawSky_colors_1_141)
   5729 CE 00         [ 7]  367 	adc	a, #0x00
   572B 67            [ 4]  368 	ld	h, a
   572C 66            [ 7]  369 	ld	h, (hl)
   572D 3E 0A         [ 7]  370 	ld	a, #0x0a
   572F 93            [ 4]  371 	sub	a, e
   5730 47            [ 4]  372 	ld	b, a
   5731 D5            [11]  373 	push	de
   5732 79            [ 4]  374 	ld	a, c
   5733 F5            [11]  375 	push	af
   5734 33            [ 6]  376 	inc	sp
   5735 6A            [ 4]  377 	ld	l, d
   5736 E5            [11]  378 	push	hl
   5737 C5            [11]  379 	push	bc
   5738 33            [ 6]  380 	inc	sp
   5739 CD 82 56      [17]  381 	call	_DrawSkyGradient
   573C F1            [10]  382 	pop	af
   573D F1            [10]  383 	pop	af
   573E D1            [10]  384 	pop	de
   573F 55            [ 4]  385 	ld	d, l
                            386 ;src/main.c:183: for (i = 1; i < sizeof(colors); i++)
   5740 1C            [ 4]  387 	inc	e
   5741 7B            [ 4]  388 	ld	a, e
   5742 D6 08         [ 7]  389 	sub	a, #0x08
   5744 38 D4         [12]  390 	jr	C,00102$
   5746 C9            [10]  391 	ret
   5747                     392 _DrawSky_colors_1_141:
   5747 02                  393 	.db #0x02	; 2
   5748 0F                  394 	.db #0x0f	; 15
   5749 02                  395 	.db #0x02	; 2
   574A 07                  396 	.db #0x07	; 7
   574B 0A                  397 	.db #0x0a	; 10
   574C 0D                  398 	.db #0x0d	; 13
   574D 08                  399 	.db #0x08	; 8
   574E 04                  400 	.db #0x04	; 4
                            401 ;src/main.c:190: void DrawCity() {
                            402 ;	---------------------------------
                            403 ; Function DrawCity
                            404 ; ---------------------------------
   574F                     405 _DrawCity::
                            406 ;src/main.c:199: cpct_drawSprite(g_building_1, pvmem, G_BUILDING_1_W, G_BUILDING_1_H);
   574F 21 0B 7D      [10]  407 	ld	hl, #0x7d0b
   5752 E5            [11]  408 	push	hl
   5753 21 DA DA      [10]  409 	ld	hl, #0xdada
   5756 E5            [11]  410 	push	hl
   5757 21 A1 45      [10]  411 	ld	hl, #_g_building_1
   575A E5            [11]  412 	push	hl
   575B CD 09 58      [17]  413 	call	_cpct_drawSprite
                            414 ;src/main.c:202: cpct_drawSprite(g_building_2, pvmem, G_BUILDING_2_W, G_BUILDING_2_H);
   575E 21 07 67      [10]  415 	ld	hl, #0x6707
   5761 E5            [11]  416 	push	hl
   5762 21 DE CB      [10]  417 	ld	hl, #0xcbde
   5765 E5            [11]  418 	push	hl
   5766 21 D0 42      [10]  419 	ld	hl, #_g_building_2
   5769 E5            [11]  420 	push	hl
   576A CD 09 58      [17]  421 	call	_cpct_drawSprite
                            422 ;src/main.c:205: cpct_drawSprite(g_building_1, pvmem, G_BUILDING_1_W, G_BUILDING_1_H);
   576D 21 0B 7D      [10]  423 	ld	hl, #0x7d0b
   5770 E5            [11]  424 	push	hl
   5771 21 F8 DA      [10]  425 	ld	hl, #0xdaf8
   5774 E5            [11]  426 	push	hl
   5775 21 A1 45      [10]  427 	ld	hl, #_g_building_1
   5778 E5            [11]  428 	push	hl
   5779 CD 09 58      [17]  429 	call	_cpct_drawSprite
                            430 ;src/main.c:208: cpct_drawSprite(g_building_2, pvmem, G_BUILDING_2_W, G_BUILDING_2_H);
   577C 21 07 67      [10]  431 	ld	hl, #0x6707
   577F E5            [11]  432 	push	hl
   5780 21 03 CC      [10]  433 	ld	hl, #0xcc03
   5783 E5            [11]  434 	push	hl
   5784 21 D0 42      [10]  435 	ld	hl, #_g_building_2
   5787 E5            [11]  436 	push	hl
   5788 CD 09 58      [17]  437 	call	_cpct_drawSprite
                            438 ;src/main.c:211: cpct_drawSprite(g_building_3, pvmem, G_BUILDING_3_W, G_BUILDING_3_H);
   578B 21 09 50      [10]  439 	ld	hl, #0x5009
   578E E5            [11]  440 	push	hl
   578F 21 EC C4      [10]  441 	ld	hl, #0xc4ec
   5792 E5            [11]  442 	push	hl
   5793 21 00 40      [10]  443 	ld	hl, #_g_building_3
   5796 E5            [11]  444 	push	hl
   5797 CD 09 58      [17]  445 	call	_cpct_drawSprite
   579A C9            [10]  446 	ret
                            447 ;src/main.c:217: void InitCapture() {
                            448 ;	---------------------------------
                            449 ; Function InitCapture
                            450 ; ---------------------------------
   579B                     451 _InitCapture::
                            452 ;src/main.c:221: cpct_getScreenToSprite(pvmem, gScreenCapture, G_UFO_0_W, G_UFO_0_H);
   579B 21 10 15      [10]  453 	ld	hl, #0x1510
   579E E5            [11]  454 	push	hl
   579F 21 54 59      [10]  455 	ld	hl, #_gScreenCapture
   57A2 E5            [11]  456 	push	hl
   57A3 21 B0 C4      [10]  457 	ld	hl, #0xc4b0
   57A6 E5            [11]  458 	push	hl
   57A7 CD BF 57      [17]  459 	call	_cpct_getScreenToSprite
   57AA C9            [10]  460 	ret
                            461 ;src/main.c:227: void DrawBackground() {
                            462 ;	---------------------------------
                            463 ; Function DrawBackground
                            464 ; ---------------------------------
   57AB                     465 _DrawBackground::
                            466 ;src/main.c:228: DrawSky();
   57AB CD 17 57      [17]  467 	call	_DrawSky
                            468 ;src/main.c:229: DrawCity();
   57AE CD 4F 57      [17]  469 	call	_DrawCity
                            470 ;src/main.c:231: InitCapture();
   57B1 C3 9B 57      [10]  471 	jp  _InitCapture
                            472 ;src/main.c:237: void main(void)  {
                            473 ;	---------------------------------
                            474 ; Function main
                            475 ; ---------------------------------
   57B4                     476 _main::
                            477 ;src/main.c:238: Initialization();   // Initialize everything
   57B4 CD 90 55      [17]  478 	call	_Initialization
                            479 ;src/main.c:239: DrawBackground();   // Draw background with sky and buildings
   57B7 CD AB 57      [17]  480 	call	_DrawBackground
                            481 ;src/main.c:242: while(1) {
   57BA                     482 00102$:
                            483 ;src/main.c:243: DrawUFO();
   57BA CD E1 55      [17]  484 	call	_DrawUFO
   57BD 18 FB         [12]  485 	jr	00102$
                            486 	.area _CODE
                            487 	.area _INITIALIZER
                            488 	.area _CABS (ABS)
