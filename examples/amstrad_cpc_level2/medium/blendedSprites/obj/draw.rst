                              1 ;--------------------------------------------------------
                              2 ; File Created by SDCC : free open source ANSI-C Compiler
                              3 ; Version 3.6.8 #9946 (Linux)
                              4 ;--------------------------------------------------------
                              5 	.module draw
                              6 	.optsdcc -mz80
                              7 	
                              8 ;--------------------------------------------------------
                              9 ; Public variables in this module
                             10 ;--------------------------------------------------------
                             11 	.globl _drawSpriteMixed
                             12 	.globl _cpct_getRandom_mxor_u8
                             13 	.globl _cpct_getScreenPtr
                             14 	.globl _cpct_drawStringM0
                             15 	.globl _cpct_setDrawCharM0
                             16 	.globl _cpct_drawSprite
                             17 	.globl _cpct_setBlendMode
                             18 	.globl _cpct_drawSpriteBlended
                             19 	.globl _drawBackground
                             20 	.globl _drawCurrentSpriteAtRandom
                             21 	.globl _drawUserInterfaceStatus
                             22 	.globl _drawUserInterfaceMessages
                             23 ;--------------------------------------------------------
                             24 ; special function registers
                             25 ;--------------------------------------------------------
                             26 ;--------------------------------------------------------
                             27 ; ram data
                             28 ;--------------------------------------------------------
                             29 	.area _DATA
                             30 ;--------------------------------------------------------
                             31 ; ram data
                             32 ;--------------------------------------------------------
                             33 	.area _INITIALIZED
                             34 ;--------------------------------------------------------
                             35 ; absolute external ram data
                             36 ;--------------------------------------------------------
                             37 	.area _DABS (ABS)
                             38 ;--------------------------------------------------------
                             39 ; global & static initialisations
                             40 ;--------------------------------------------------------
                             41 	.area _HOME
                             42 	.area _GSINIT
                             43 	.area _GSFINAL
                             44 	.area _GSINIT
                             45 ;--------------------------------------------------------
                             46 ; Home
                             47 ;--------------------------------------------------------
                             48 	.area _HOME
                             49 	.area _HOME
                             50 ;--------------------------------------------------------
                             51 ; code
                             52 ;--------------------------------------------------------
                             53 	.area _CODE
                             54 ;src/draw.c:28: void drawBackground() {
                             55 ;	---------------------------------
                             56 ; Function drawBackground
                             57 ; ---------------------------------
   6880                      58 _drawBackground::
                             59 ;src/draw.c:31: u8* p = cpct_getScreenPtr(CPCT_VMEM_START, BG_X, BG_Y);
   6880 21 00 48      [10]   60 	ld	hl, #0x4800
   6883 E5            [11]   61 	push	hl
   6884 26 C0         [ 7]   62 	ld	h, #0xc0
   6886 E5            [11]   63 	push	hl
   6887 CD DA 6E      [17]   64 	call	_cpct_getScreenPtr
   688A 4D            [ 4]   65 	ld	c, l
   688B 44            [ 4]   66 	ld	b, h
                             67 ;src/draw.c:37: cpct_drawSprite(g_scifi_bg_0, p             , BG_WIDTH/2, BG_HEIGHT);
   688C 59            [ 4]   68 	ld	e, c
   688D 50            [ 4]   69 	ld	d, b
   688E C5            [11]   70 	push	bc
   688F 21 28 80      [10]   71 	ld	hl, #0x8028
   6892 E5            [11]   72 	push	hl
   6893 D5            [11]   73 	push	de
   6894 21 80 40      [10]   74 	ld	hl, #_g_scifi_bg_0
   6897 E5            [11]   75 	push	hl
   6898 CD 07 6D      [17]   76 	call	_cpct_drawSprite
   689B C1            [10]   77 	pop	bc
                             78 ;src/draw.c:38: cpct_drawSprite(g_scifi_bg_1, p + BG_WIDTH/2, BG_WIDTH/2, BG_HEIGHT);
   689C 21 28 00      [10]   79 	ld	hl, #0x0028
   689F 09            [11]   80 	add	hl, bc
   68A0 01 80 54      [10]   81 	ld	bc, #_g_scifi_bg_1+0
   68A3 11 28 80      [10]   82 	ld	de, #0x8028
   68A6 D5            [11]   83 	push	de
   68A7 E5            [11]   84 	push	hl
   68A8 C5            [11]   85 	push	bc
   68A9 CD 07 6D      [17]   86 	call	_cpct_drawSprite
   68AC C9            [10]   87 	ret
                             88 ;src/draw.c:46: void drawSpriteMixed(  CPCT_BlendMode mode, u8* sprite
                             89 ;	---------------------------------
                             90 ; Function drawSpriteMixed
                             91 ; ---------------------------------
   68AD                      92 _drawSpriteMixed::
   68AD DD E5         [15]   93 	push	ix
   68AF DD 21 00 00   [14]   94 	ld	ix,#0
   68B3 DD 39         [15]   95 	add	ix,sp
                             96 ;src/draw.c:50: u8* p = cpct_getScreenPtr(CPCT_VMEM_START, x, y);
   68B5 DD 66 08      [19]   97 	ld	h, 8 (ix)
   68B8 DD 6E 07      [19]   98 	ld	l, 7 (ix)
   68BB E5            [11]   99 	push	hl
   68BC 21 00 C0      [10]  100 	ld	hl, #0xc000
   68BF E5            [11]  101 	push	hl
   68C0 CD DA 6E      [17]  102 	call	_cpct_getScreenPtr
                            103 ;src/draw.c:53: cpct_setBlendMode(mode);
   68C3 E5            [11]  104 	push	hl
   68C4 DD 6E 04      [19]  105 	ld	l, 4 (ix)
   68C7 CD 0E 6E      [17]  106 	call	_cpct_setBlendMode
   68CA C1            [10]  107 	pop	bc
                            108 ;src/draw.c:56: cpct_drawSpriteBlended(p, height, width, sprite);
   68CB DD 5E 05      [19]  109 	ld	e,5 (ix)
   68CE DD 56 06      [19]  110 	ld	d,6 (ix)
   68D1 D5            [11]  111 	push	de
   68D2 DD 66 09      [19]  112 	ld	h, 9 (ix)
   68D5 DD 6E 0A      [19]  113 	ld	l, 10 (ix)
   68D8 E5            [11]  114 	push	hl
   68D9 C5            [11]  115 	push	bc
   68DA CD 58 6E      [17]  116 	call	_cpct_drawSpriteBlended
   68DD DD E1         [14]  117 	pop	ix
   68DF C9            [10]  118 	ret
                            119 ;src/draw.c:64: void drawCurrentSpriteAtRandom() {
                            120 ;	---------------------------------
                            121 ; Function drawCurrentSpriteAtRandom
                            122 ; ---------------------------------
   68E0                     123 _drawCurrentSpriteAtRandom::
   68E0 DD E5         [15]  124 	push	ix
   68E2 DD 21 00 00   [14]  125 	ld	ix,#0
   68E6 DD 39         [15]  126 	add	ix,sp
   68E8 3B            [ 6]  127 	dec	sp
                            128 ;src/draw.c:70: x = BG_X + ( cpct_rand() % (BG_WIDTH  - 4) );
   68E9 CD 33 6E      [17]  129 	call	_cpct_getRandom_mxor_u8
   68EC 45            [ 4]  130 	ld	b, l
   68ED 3E 4C         [ 7]  131 	ld	a, #0x4c
   68EF F5            [11]  132 	push	af
   68F0 33            [ 6]  133 	inc	sp
   68F1 C5            [11]  134 	push	bc
   68F2 33            [ 6]  135 	inc	sp
   68F3 CD AC 6D      [17]  136 	call	__moduchar
   68F6 F1            [10]  137 	pop	af
   68F7 DD 75 FF      [19]  138 	ld	-1 (ix), l
                            139 ;src/draw.c:71: y = BG_Y + ( cpct_rand() % (BG_HEIGHT - 8) );
   68FA CD 33 6E      [17]  140 	call	_cpct_getRandom_mxor_u8
   68FD 45            [ 4]  141 	ld	b, l
   68FE 3E 78         [ 7]  142 	ld	a, #0x78
   6900 F5            [11]  143 	push	af
   6901 33            [ 6]  144 	inc	sp
   6902 C5            [11]  145 	push	bc
   6903 33            [ 6]  146 	inc	sp
   6904 CD AC 6D      [17]  147 	call	__moduchar
   6907 F1            [10]  148 	pop	af
   6908 7D            [ 4]  149 	ld	a, l
   6909 C6 48         [ 7]  150 	add	a, #0x48
   690B 47            [ 4]  151 	ld	b, a
                            152 ;src/draw.c:75: , g_items[g_selectedItem].sprite
   690C ED 5B 27 6F   [20]  153 	ld	de, (_g_selectedItem)
   6910 16 00         [ 7]  154 	ld	d, #0x00
   6912 6B            [ 4]  155 	ld	l, e
   6913 62            [ 4]  156 	ld	h, d
   6914 29            [11]  157 	add	hl, hl
   6915 29            [11]  158 	add	hl, hl
   6916 29            [11]  159 	add	hl, hl
   6917 19            [11]  160 	add	hl, de
   6918 11 DC 6A      [10]  161 	ld	de, #_g_items
   691B 19            [11]  162 	add	hl, de
   691C 5E            [ 7]  163 	ld	e, (hl)
   691D 23            [ 6]  164 	inc	hl
   691E 56            [ 7]  165 	ld	d, (hl)
                            166 ;src/draw.c:74: drawSpriteMixed(  g_blendModes[g_selectedBlendMode].blendmode
   691F D5            [11]  167 	push	de
   6920 ED 5B 28 6F   [20]  168 	ld	de, (_g_selectedBlendMode)
   6924 16 00         [ 7]  169 	ld	d, #0x00
   6926 6B            [ 4]  170 	ld	l, e
   6927 62            [ 4]  171 	ld	h, d
   6928 29            [11]  172 	add	hl, hl
   6929 29            [11]  173 	add	hl, hl
   692A 19            [11]  174 	add	hl, de
   692B D1            [10]  175 	pop	de
   692C 3E AF         [ 7]  176 	ld	a, #<(_g_blendModes)
   692E 85            [ 4]  177 	add	a, l
   692F 6F            [ 4]  178 	ld	l, a
   6930 3E 6A         [ 7]  179 	ld	a, #>(_g_blendModes)
   6932 8C            [ 4]  180 	adc	a, h
   6933 67            [ 4]  181 	ld	h, a
   6934 4E            [ 7]  182 	ld	c, (hl)
   6935 21 04 08      [10]  183 	ld	hl, #0x0804
   6938 E5            [11]  184 	push	hl
   6939 C5            [11]  185 	push	bc
   693A 33            [ 6]  186 	inc	sp
   693B DD 7E FF      [19]  187 	ld	a, -1 (ix)
   693E F5            [11]  188 	push	af
   693F 33            [ 6]  189 	inc	sp
   6940 D5            [11]  190 	push	de
   6941 79            [ 4]  191 	ld	a, c
   6942 F5            [11]  192 	push	af
   6943 33            [ 6]  193 	inc	sp
   6944 CD AD 68      [17]  194 	call	_drawSpriteMixed
   6947 21 07 00      [10]  195 	ld	hl, #7
   694A 39            [11]  196 	add	hl, sp
   694B F9            [ 6]  197 	ld	sp, hl
   694C 33            [ 6]  198 	inc	sp
   694D DD E1         [14]  199 	pop	ix
   694F C9            [10]  200 	ret
                            201 ;src/draw.c:84: void drawUserInterfaceStatus() {
                            202 ;	---------------------------------
                            203 ; Function drawUserInterfaceStatus
                            204 ; ---------------------------------
   6950                     205 _drawUserInterfaceStatus::
                            206 ;src/draw.c:87: u8 *p = cpct_getScreenPtr(CPCT_VMEM_START, 4, 60);
   6950 21 04 3C      [10]  207 	ld	hl, #0x3c04
   6953 E5            [11]  208 	push	hl
   6954 21 00 C0      [10]  209 	ld	hl, #0xc000
   6957 E5            [11]  210 	push	hl
   6958 CD DA 6E      [17]  211 	call	_cpct_getScreenPtr
                            212 ;src/draw.c:90: cpct_setDrawCharM0(8, 0);
   695B E5            [11]  213 	push	hl
   695C 21 08 00      [10]  214 	ld	hl, #0x0008
   695F E5            [11]  215 	push	hl
   6960 CD 84 6E      [17]  216 	call	_cpct_setDrawCharM0
   6963 C1            [10]  217 	pop	bc
                            218 ;src/draw.c:94: cpct_drawStringM0(g_items[g_selectedItem].name   , p       );
   6964 59            [ 4]  219 	ld	e, c
   6965 50            [ 4]  220 	ld	d, b
   6966 D5            [11]  221 	push	de
   6967 ED 5B 27 6F   [20]  222 	ld	de, (_g_selectedItem)
   696B 16 00         [ 7]  223 	ld	d, #0x00
   696D 6B            [ 4]  224 	ld	l, e
   696E 62            [ 4]  225 	ld	h, d
   696F 29            [11]  226 	add	hl, hl
   6970 29            [11]  227 	add	hl, hl
   6971 29            [11]  228 	add	hl, hl
   6972 19            [11]  229 	add	hl, de
   6973 D1            [10]  230 	pop	de
   6974 3E DC         [ 7]  231 	ld	a, #<(_g_items)
   6976 85            [ 4]  232 	add	a, l
   6977 6F            [ 4]  233 	ld	l, a
   6978 3E 6A         [ 7]  234 	ld	a, #>(_g_items)
   697A 8C            [ 4]  235 	adc	a, h
   697B 67            [ 4]  236 	ld	h, a
   697C 23            [ 6]  237 	inc	hl
   697D 23            [ 6]  238 	inc	hl
   697E C5            [11]  239 	push	bc
   697F D5            [11]  240 	push	de
   6980 E5            [11]  241 	push	hl
   6981 CD 69 6C      [17]  242 	call	_cpct_drawStringM0
   6984 C1            [10]  243 	pop	bc
                            244 ;src/draw.c:95: cpct_drawSprite  (g_items[g_selectedItem].sprite , p + 28 , 4, 8);
   6985 21 1C 00      [10]  245 	ld	hl, #0x001c
   6988 09            [11]  246 	add	hl,bc
   6989 EB            [ 4]  247 	ex	de,hl
   698A ED 4B 27 6F   [20]  248 	ld	bc, (_g_selectedItem)
   698E 06 00         [ 7]  249 	ld	b, #0x00
   6990 69            [ 4]  250 	ld	l, c
   6991 60            [ 4]  251 	ld	h, b
   6992 29            [11]  252 	add	hl, hl
   6993 29            [11]  253 	add	hl, hl
   6994 29            [11]  254 	add	hl, hl
   6995 09            [11]  255 	add	hl, bc
   6996 01 DC 6A      [10]  256 	ld	bc, #_g_items
   6999 09            [11]  257 	add	hl, bc
   699A 4E            [ 7]  258 	ld	c, (hl)
   699B 23            [ 6]  259 	inc	hl
   699C 46            [ 7]  260 	ld	b, (hl)
   699D 21 04 08      [10]  261 	ld	hl, #0x0804
   69A0 E5            [11]  262 	push	hl
   69A1 D5            [11]  263 	push	de
   69A2 C5            [11]  264 	push	bc
   69A3 CD 07 6D      [17]  265 	call	_cpct_drawSprite
                            266 ;src/draw.c:98: p = cpct_getScreenPtr(CPCT_VMEM_START, 52, 60);
   69A6 21 34 3C      [10]  267 	ld	hl, #0x3c34
   69A9 E5            [11]  268 	push	hl
   69AA 21 00 C0      [10]  269 	ld	hl, #0xc000
   69AD E5            [11]  270 	push	hl
   69AE CD DA 6E      [17]  271 	call	_cpct_getScreenPtr
   69B1 4D            [ 4]  272 	ld	c, l
   69B2 44            [ 4]  273 	ld	b, h
                            274 ;src/draw.c:99: cpct_drawStringM0(g_blendModes[g_selectedBlendMode].name, p);
   69B3 ED 5B 28 6F   [20]  275 	ld	de, (_g_selectedBlendMode)
   69B7 16 00         [ 7]  276 	ld	d, #0x00
   69B9 6B            [ 4]  277 	ld	l, e
   69BA 62            [ 4]  278 	ld	h, d
   69BB 29            [11]  279 	add	hl, hl
   69BC 29            [11]  280 	add	hl, hl
   69BD 19            [11]  281 	add	hl, de
   69BE 11 AF 6A      [10]  282 	ld	de, #_g_blendModes
   69C1 19            [11]  283 	add	hl, de
   69C2 23            [ 6]  284 	inc	hl
   69C3 C5            [11]  285 	push	bc
   69C4 E5            [11]  286 	push	hl
   69C5 CD 69 6C      [17]  287 	call	_cpct_drawStringM0
   69C8 C9            [10]  288 	ret
                            289 ;src/draw.c:106: void drawUserInterfaceMessages() {
                            290 ;	---------------------------------
                            291 ; Function drawUserInterfaceMessages
                            292 ; ---------------------------------
   69C9                     293 _drawUserInterfaceMessages::
                            294 ;src/draw.c:111: cpct_setDrawCharM0(3, 0);
   69C9 21 03 00      [10]  295 	ld	hl, #0x0003
   69CC E5            [11]  296 	push	hl
   69CD CD 84 6E      [17]  297 	call	_cpct_setDrawCharM0
                            298 ;src/draw.c:112: cpct_drawStringM0("[Space]"   , CPCT_VMEM_START    );
   69D0 21 00 C0      [10]  299 	ld	hl, #0xc000
   69D3 E5            [11]  300 	push	hl
   69D4 21 6D 6A      [10]  301 	ld	hl, #___str_0
   69D7 E5            [11]  302 	push	hl
   69D8 CD 69 6C      [17]  303 	call	_cpct_drawStringM0
                            304 ;src/draw.c:113: cpct_setDrawCharM0(9, 0);
   69DB 21 09 00      [10]  305 	ld	hl, #0x0009
   69DE E5            [11]  306 	push	hl
   69DF CD 84 6E      [17]  307 	call	_cpct_setDrawCharM0
                            308 ;src/draw.c:114: cpct_drawStringM0("Draw Item" , CPCT_VMEM_START+32 );
   69E2 21 20 C0      [10]  309 	ld	hl, #0xc020
   69E5 E5            [11]  310 	push	hl
   69E6 21 75 6A      [10]  311 	ld	hl, #___str_1
   69E9 E5            [11]  312 	push	hl
   69EA CD 69 6C      [17]  313 	call	_cpct_drawStringM0
                            314 ;src/draw.c:118: p = cpct_getScreenPtr(CPCT_VMEM_START, 0, 15);
   69ED 21 00 0F      [10]  315 	ld	hl, #0x0f00
   69F0 E5            [11]  316 	push	hl
   69F1 26 C0         [ 7]  317 	ld	h, #0xc0
   69F3 E5            [11]  318 	push	hl
   69F4 CD DA 6E      [17]  319 	call	_cpct_getScreenPtr
                            320 ;src/draw.c:119: cpct_setDrawCharM0(3, 0);
   69F7 E5            [11]  321 	push	hl
   69F8 01 03 00      [10]  322 	ld	bc, #0x0003
   69FB C5            [11]  323 	push	bc
   69FC CD 84 6E      [17]  324 	call	_cpct_setDrawCharM0
   69FF E1            [10]  325 	pop	hl
                            326 ;src/draw.c:120: cpct_drawStringM0("[1] [2]"   , p    );
   6A00 5D            [ 4]  327 	ld	e, l
   6A01 54            [ 4]  328 	ld	d, h
   6A02 01 7F 6A      [10]  329 	ld	bc, #___str_2+0
   6A05 E5            [11]  330 	push	hl
   6A06 D5            [11]  331 	push	de
   6A07 C5            [11]  332 	push	bc
   6A08 CD 69 6C      [17]  333 	call	_cpct_drawStringM0
   6A0B 01 09 00      [10]  334 	ld	bc, #0x0009
   6A0E C5            [11]  335 	push	bc
   6A0F CD 84 6E      [17]  336 	call	_cpct_setDrawCharM0
   6A12 E1            [10]  337 	pop	hl
                            338 ;src/draw.c:122: cpct_drawStringM0("Select"    , p+32 );
   6A13 01 20 00      [10]  339 	ld	bc, #0x0020
   6A16 09            [11]  340 	add	hl, bc
   6A17 01 87 6A      [10]  341 	ld	bc, #___str_3+0
   6A1A E5            [11]  342 	push	hl
   6A1B C5            [11]  343 	push	bc
   6A1C CD 69 6C      [17]  344 	call	_cpct_drawStringM0
                            345 ;src/draw.c:125: p = cpct_getScreenPtr(CPCT_VMEM_START, 0, 30);
   6A1F 21 00 1E      [10]  346 	ld	hl, #0x1e00
   6A22 E5            [11]  347 	push	hl
   6A23 26 C0         [ 7]  348 	ld	h, #0xc0
   6A25 E5            [11]  349 	push	hl
   6A26 CD DA 6E      [17]  350 	call	_cpct_getScreenPtr
                            351 ;src/draw.c:126: cpct_setDrawCharM0(3, 0);
   6A29 E5            [11]  352 	push	hl
   6A2A 01 03 00      [10]  353 	ld	bc, #0x0003
   6A2D C5            [11]  354 	push	bc
   6A2E CD 84 6E      [17]  355 	call	_cpct_setDrawCharM0
   6A31 E1            [10]  356 	pop	hl
                            357 ;src/draw.c:127: cpct_drawStringM0("[Esc]"     , p    );
   6A32 5D            [ 4]  358 	ld	e, l
   6A33 54            [ 4]  359 	ld	d, h
   6A34 01 8E 6A      [10]  360 	ld	bc, #___str_4+0
   6A37 E5            [11]  361 	push	hl
   6A38 D5            [11]  362 	push	de
   6A39 C5            [11]  363 	push	bc
   6A3A CD 69 6C      [17]  364 	call	_cpct_drawStringM0
   6A3D 01 09 00      [10]  365 	ld	bc, #0x0009
   6A40 C5            [11]  366 	push	bc
   6A41 CD 84 6E      [17]  367 	call	_cpct_setDrawCharM0
   6A44 E1            [10]  368 	pop	hl
                            369 ;src/draw.c:129: cpct_drawStringM0("Clear"     , p+32 );
   6A45 01 20 00      [10]  370 	ld	bc, #0x0020
   6A48 09            [11]  371 	add	hl, bc
   6A49 01 94 6A      [10]  372 	ld	bc, #___str_5+0
   6A4C E5            [11]  373 	push	hl
   6A4D C5            [11]  374 	push	bc
   6A4E CD 69 6C      [17]  375 	call	_cpct_drawStringM0
                            376 ;src/draw.c:133: p = cpct_getScreenPtr(CPCT_VMEM_START, 0, 50);
   6A51 21 00 32      [10]  377 	ld	hl, #0x3200
   6A54 E5            [11]  378 	push	hl
   6A55 26 C0         [ 7]  379 	ld	h, #0xc0
   6A57 E5            [11]  380 	push	hl
   6A58 CD DA 6E      [17]  381 	call	_cpct_getScreenPtr
                            382 ;src/draw.c:134: cpct_setDrawCharM0(1, 6);
   6A5B E5            [11]  383 	push	hl
   6A5C 01 01 06      [10]  384 	ld	bc, #0x0601
   6A5F C5            [11]  385 	push	bc
   6A60 CD 84 6E      [17]  386 	call	_cpct_setDrawCharM0
   6A63 E1            [10]  387 	pop	hl
                            388 ;src/draw.c:135: cpct_drawStringM0("   Item     Blend   ", p);
   6A64 01 9A 6A      [10]  389 	ld	bc, #___str_6+0
   6A67 E5            [11]  390 	push	hl
   6A68 C5            [11]  391 	push	bc
   6A69 CD 69 6C      [17]  392 	call	_cpct_drawStringM0
   6A6C C9            [10]  393 	ret
   6A6D                     394 ___str_0:
   6A6D 5B 53 70 61 63 65   395 	.ascii "[Space]"
        5D
   6A74 00                  396 	.db 0x00
   6A75                     397 ___str_1:
   6A75 44 72 61 77 20 49   398 	.ascii "Draw Item"
        74 65 6D
   6A7E 00                  399 	.db 0x00
   6A7F                     400 ___str_2:
   6A7F 5B 31 5D 20 5B 32   401 	.ascii "[1] [2]"
        5D
   6A86 00                  402 	.db 0x00
   6A87                     403 ___str_3:
   6A87 53 65 6C 65 63 74   404 	.ascii "Select"
   6A8D 00                  405 	.db 0x00
   6A8E                     406 ___str_4:
   6A8E 5B 45 73 63 5D      407 	.ascii "[Esc]"
   6A93 00                  408 	.db 0x00
   6A94                     409 ___str_5:
   6A94 43 6C 65 61 72      410 	.ascii "Clear"
   6A99 00                  411 	.db 0x00
   6A9A                     412 ___str_6:
   6A9A 20 20 20 49 74 65   413 	.ascii "   Item     Blend   "
        6D 20 20 20 20 20
        42 6C 65 6E 64 20
        20 20
   6AAE 00                  414 	.db 0x00
                            415 	.area _CODE
                            416 	.area _INITIALIZER
                            417 	.area _CABS (ABS)
