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
                             12 	.globl _initialize_CPC
                             13 	.globl _scrollScreenTilemap
                             14 	.globl _wait4KeyboardInput
                             15 	.globl _cpct_etm_setTileset2x4
                             16 	.globl _cpct_etm_drawTileBox2x4
                             17 	.globl _cpct_getScreenPtr
                             18 	.globl _cpct_setVideoMemoryOffset
                             19 	.globl _cpct_setPALColour
                             20 	.globl _cpct_setPalette
                             21 	.globl _cpct_waitVSYNC
                             22 	.globl _cpct_setVideoMode
                             23 	.globl _cpct_drawSolidBox
                             24 	.globl _cpct_isKeyPressed
                             25 	.globl _cpct_scanKeyboard_f
                             26 	.globl _cpct_memset
                             27 	.globl _cpct_disableFirmware
                             28 ;--------------------------------------------------------
                             29 ; special function registers
                             30 ;--------------------------------------------------------
                             31 ;--------------------------------------------------------
                             32 ; ram data
                             33 ;--------------------------------------------------------
                             34 	.area _DATA
                             35 ;--------------------------------------------------------
                             36 ; ram data
                             37 ;--------------------------------------------------------
                             38 	.area _INITIALIZED
                             39 ;--------------------------------------------------------
                             40 ; absolute external ram data
                             41 ;--------------------------------------------------------
                             42 	.area _DABS (ABS)
                             43 ;--------------------------------------------------------
                             44 ; global & static initialisations
                             45 ;--------------------------------------------------------
                             46 	.area _HOME
                             47 	.area _GSINIT
                             48 	.area _GSFINAL
                             49 	.area _GSINIT
                             50 ;--------------------------------------------------------
                             51 ; Home
                             52 ;--------------------------------------------------------
                             53 	.area _HOME
                             54 	.area _HOME
                             55 ;--------------------------------------------------------
                             56 ; code
                             57 ;--------------------------------------------------------
                             58 	.area _CODE
                             59 ;src/main.c:43: i16 wait4KeyboardInput(){
                             60 ;	---------------------------------
                             61 ; Function wait4KeyboardInput
                             62 ; ---------------------------------
   1A8D                      63 _wait4KeyboardInput::
                             64 ;src/main.c:45: while(1) {
   1A8D                      65 00107$:
                             66 ;src/main.c:47: cpct_scanKeyboard_f(); 
   1A8D CD 4F 1C      [17]   67 	call	_cpct_scanKeyboard_f
                             68 ;src/main.c:51: if      (cpct_isKeyPressed(Key_CursorRight)) return  1;
   1A90 21 00 02      [10]   69 	ld	hl, #0x0200
   1A93 CD 43 1C      [17]   70 	call	_cpct_isKeyPressed
   1A96 7D            [ 4]   71 	ld	a, l
   1A97 B7            [ 4]   72 	or	a, a
   1A98 28 04         [12]   73 	jr	Z,00104$
   1A9A 21 01 00      [10]   74 	ld	hl, #0x0001
   1A9D C9            [10]   75 	ret
   1A9E                      76 00104$:
                             77 ;src/main.c:52: else if (cpct_isKeyPressed(Key_CursorLeft))  return -1;
   1A9E 21 01 01      [10]   78 	ld	hl, #0x0101
   1AA1 CD 43 1C      [17]   79 	call	_cpct_isKeyPressed
   1AA4 7D            [ 4]   80 	ld	a, l
   1AA5 B7            [ 4]   81 	or	a, a
   1AA6 28 E5         [12]   82 	jr	Z,00107$
   1AA8 21 FF FF      [10]   83 	ld	hl, #0xffff
   1AAB C9            [10]   84 	ret
                             85 ;src/main.c:60: void scrollScreenTilemap(TScreenTilemap *scr, i16 scroll) { 
                             86 ;	---------------------------------
                             87 ; Function scrollScreenTilemap
                             88 ; ---------------------------------
   1AAC                      89 _scrollScreenTilemap::
   1AAC DD E5         [15]   90 	push	ix
   1AAE DD 21 00 00   [14]   91 	ld	ix,#0
   1AB2 DD 39         [15]   92 	add	ix,sp
   1AB4 F5            [11]   93 	push	af
   1AB5 F5            [11]   94 	push	af
                             95 ;src/main.c:63: u8 column = (scroll > 0) ? (SCR_TILE_WIDTH-1) : (0);
   1AB6 AF            [ 4]   96 	xor	a, a
   1AB7 DD BE 06      [19]   97 	cp	a, 6 (ix)
   1ABA DD 9E 07      [19]   98 	sbc	a, 7 (ix)
   1ABD E2 C2 1A      [10]   99 	jp	PO, 00116$
   1AC0 EE 80         [ 7]  100 	xor	a, #0x80
   1AC2                     101 00116$:
   1AC2 07            [ 4]  102 	rlca
   1AC3 E6 01         [ 7]  103 	and	a,#0x01
   1AC5 DD 77 FF      [19]  104 	ld	-1 (ix), a
   1AC8 B7            [ 4]  105 	or	a, a
   1AC9 28 04         [12]  106 	jr	Z,00106$
   1ACB 0E 27         [ 7]  107 	ld	c, #0x27
   1ACD 18 02         [12]  108 	jr	00107$
   1ACF                     109 00106$:
   1ACF 0E 00         [ 7]  110 	ld	c, #0x00
   1AD1                     111 00107$:
   1AD1 DD 71 FC      [19]  112 	ld	-4 (ix), c
                            113 ;src/main.c:67: scr->pVideo   += 2*scroll; // Video memory starts now 2 bytes to the left or to the right
   1AD4 DD 4E 04      [19]  114 	ld	c,4 (ix)
   1AD7 DD 46 05      [19]  115 	ld	b,5 (ix)
   1ADA 69            [ 4]  116 	ld	l, c
   1ADB 60            [ 4]  117 	ld	h, b
   1ADC 5E            [ 7]  118 	ld	e, (hl)
   1ADD 23            [ 6]  119 	inc	hl
   1ADE 56            [ 7]  120 	ld	d, (hl)
   1ADF DD 6E 06      [19]  121 	ld	l,6 (ix)
   1AE2 DD 66 07      [19]  122 	ld	h,7 (ix)
   1AE5 29            [11]  123 	add	hl, hl
   1AE6 19            [11]  124 	add	hl,de
   1AE7 EB            [ 4]  125 	ex	de,hl
   1AE8 69            [ 4]  126 	ld	l, c
   1AE9 60            [ 4]  127 	ld	h, b
   1AEA 73            [ 7]  128 	ld	(hl), e
   1AEB 23            [ 6]  129 	inc	hl
   1AEC 72            [ 7]  130 	ld	(hl), d
                            131 ;src/main.c:68: scr->pTilemap += scroll;   // Move the start pointer to the tilemap 1 tile (1 byte) to point to the drawable zone (viewport)
   1AED 21 02 00      [10]  132 	ld	hl, #0x0002
   1AF0 09            [11]  133 	add	hl,bc
   1AF1 DD 75 FD      [19]  134 	ld	-3 (ix), l
   1AF4 DD 74 FE      [19]  135 	ld	-2 (ix), h
   1AF7 5E            [ 7]  136 	ld	e, (hl)
   1AF8 23            [ 6]  137 	inc	hl
   1AF9 56            [ 7]  138 	ld	d, (hl)
   1AFA DD 7E 06      [19]  139 	ld	a, 6 (ix)
   1AFD 83            [ 4]  140 	add	a, e
   1AFE 5F            [ 4]  141 	ld	e, a
   1AFF DD 7E 07      [19]  142 	ld	a, 7 (ix)
   1B02 8A            [ 4]  143 	adc	a, d
   1B03 57            [ 4]  144 	ld	d, a
   1B04 DD 6E FD      [19]  145 	ld	l,-3 (ix)
   1B07 DD 66 FE      [19]  146 	ld	h,-2 (ix)
   1B0A 73            [ 7]  147 	ld	(hl), e
   1B0B 23            [ 6]  148 	inc	hl
   1B0C 72            [ 7]  149 	ld	(hl), d
                            150 ;src/main.c:69: scr->scroll   += scroll;   // Update scroll offset to produce scrolling
   1B0D 21 04 00      [10]  151 	ld	hl, #0x0004
   1B10 09            [11]  152 	add	hl, bc
   1B11 56            [ 7]  153 	ld	d, (hl)
   1B12 DD 5E 06      [19]  154 	ld	e, 6 (ix)
   1B15 7A            [ 4]  155 	ld	a, d
   1B16 83            [ 4]  156 	add	a, e
   1B17 77            [ 7]  157 	ld	(hl), a
                            158 ;src/main.c:72: cpct_waitVSYNC();
   1B18 E5            [11]  159 	push	hl
   1B19 C5            [11]  160 	push	bc
   1B1A CD 8C 1D      [17]  161 	call	_cpct_waitVSYNC
   1B1D C1            [10]  162 	pop	bc
   1B1E E1            [10]  163 	pop	hl
                            164 ;src/main.c:75: cpct_setVideoMemoryOffset(scr->scroll);    
   1B1F 6E            [ 7]  165 	ld	l, (hl)
   1B20 C5            [11]  166 	push	bc
   1B21 CD C5 1C      [17]  167 	call	_cpct_setVideoMemoryOffset
   1B24 C1            [10]  168 	pop	bc
                            169 ;src/main.c:82: scr->pTilemap);    // Pointer to the first tile of the tilemap to be drawn (upper-left corner
   1B25 DD 6E FD      [19]  170 	ld	l,-3 (ix)
   1B28 DD 66 FE      [19]  171 	ld	h,-2 (ix)
   1B2B 5E            [ 7]  172 	ld	e, (hl)
   1B2C 23            [ 6]  173 	inc	hl
   1B2D 56            [ 7]  174 	ld	d, (hl)
                            175 ;src/main.c:81: scr->pVideo,       // Pointer to the upper-left corner of the tilemap in video memory
   1B2E 69            [ 4]  176 	ld	l, c
   1B2F 60            [ 4]  177 	ld	h, b
   1B30 7E            [ 7]  178 	ld	a, (hl)
   1B31 23            [ 6]  179 	inc	hl
   1B32 66            [ 7]  180 	ld	h, (hl)
   1B33 6F            [ 4]  181 	ld	l, a
                            182 ;src/main.c:78: cpct_etm_drawTileBox2x4(column, 0,         // (X, Y) Upper-left Location of the Box (column in this case) to be redrawn
   1B34 C5            [11]  183 	push	bc
   1B35 D5            [11]  184 	push	de
   1B36 E5            [11]  185 	push	hl
   1B37 21 2E 78      [10]  186 	ld	hl, #0x782e
   1B3A E5            [11]  187 	push	hl
   1B3B 21 00 01      [10]  188 	ld	hl, #0x0100
   1B3E E5            [11]  189 	push	hl
   1B3F DD 7E FC      [19]  190 	ld	a, -4 (ix)
   1B42 F5            [11]  191 	push	af
   1B43 33            [ 6]  192 	inc	sp
   1B44 CD CE 1C      [17]  193 	call	_cpct_etm_drawTileBox2x4
                            194 ;src/main.c:67: scr->pVideo   += 2*scroll; // Video memory starts now 2 bytes to the left or to the right
   1B47 E1            [10]  195 	pop	hl
   1B48 4E            [ 7]  196 	ld	c, (hl)
   1B49 23            [ 6]  197 	inc	hl
   1B4A 46            [ 7]  198 	ld	b, (hl)
                            199 ;src/main.c:90: if (scroll > 0) 
   1B4B DD 7E FF      [19]  200 	ld	a, -1 (ix)
   1B4E B7            [ 4]  201 	or	a, a
   1B4F 28 10         [12]  202 	jr	Z,00102$
                            203 ;src/main.c:91: cpct_drawSolidBox(scr->pVideo - 2, 0, 2, 8);  // top-left scrolled-out char
   1B51 0B            [ 6]  204 	dec	bc
   1B52 0B            [ 6]  205 	dec	bc
   1B53 21 02 08      [10]  206 	ld	hl, #0x0802
   1B56 E5            [11]  207 	push	hl
   1B57 21 00 00      [10]  208 	ld	hl, #0x0000
   1B5A E5            [11]  209 	push	hl
   1B5B C5            [11]  210 	push	bc
   1B5C CD C0 1D      [17]  211 	call	_cpct_drawSolidBox
   1B5F 18 14         [12]  212 	jr	00104$
   1B61                     213 00102$:
                            214 ;src/main.c:93: u8* br_char = cpct_getScreenPtr(scr->pVideo, 0, 4*MAP_HEIGHT);
   1B61 21 00 B8      [10]  215 	ld	hl, #0xb800
   1B64 E5            [11]  216 	push	hl
   1B65 C5            [11]  217 	push	bc
   1B66 CD 89 1E      [17]  218 	call	_cpct_getScreenPtr
                            219 ;src/main.c:94: cpct_drawSolidBox(br_char, 0, 2, 8);  // bottom-right scrolled-out char
   1B69 01 02 08      [10]  220 	ld	bc, #0x0802
   1B6C C5            [11]  221 	push	bc
   1B6D 01 00 00      [10]  222 	ld	bc, #0x0000
   1B70 C5            [11]  223 	push	bc
   1B71 E5            [11]  224 	push	hl
   1B72 CD C0 1D      [17]  225 	call	_cpct_drawSolidBox
   1B75                     226 00104$:
   1B75 DD F9         [10]  227 	ld	sp, ix
   1B77 DD E1         [14]  228 	pop	ix
   1B79 C9            [10]  229 	ret
                            230 ;src/main.c:101: void initialize_CPC() {
                            231 ;	---------------------------------
                            232 ; Function initialize_CPC
                            233 ; ---------------------------------
   1B7A                     234 _initialize_CPC::
                            235 ;src/main.c:103: cpct_disableFirmware();         // Firmware must be disabled for this application to work
   1B7A CD B0 1D      [17]  236 	call	_cpct_disableFirmware
                            237 ;src/main.c:104: cpct_setVideoMode(0);           // Set Mode 0 (160x200, 16 Colours)
   1B7D 2E 00         [ 7]  238 	ld	l, #0x00
   1B7F CD 94 1D      [17]  239 	call	_cpct_setVideoMode
                            240 ;src/main.c:105: cpct_setPalette(g_palette, 13); // Set Palette 
   1B82 21 0D 00      [10]  241 	ld	hl, #0x000d
   1B85 E5            [11]  242 	push	hl
   1B86 21 D0 15      [10]  243 	ld	hl, #_g_palette
   1B89 E5            [11]  244 	push	hl
   1B8A CD 2C 1C      [17]  245 	call	_cpct_setPalette
                            246 ;src/main.c:106: cpct_setBorder(HW_BLACK);       // Set the border and background colours to black
   1B8D 21 10 14      [10]  247 	ld	hl, #0x1410
   1B90 E5            [11]  248 	push	hl
   1B91 CD B9 1C      [17]  249 	call	_cpct_setPALColour
                            250 ;src/main.c:110: cpct_etm_setTileset2x4(g_tileset);   
   1B94 21 DD 15      [10]  251 	ld	hl, #_g_tileset
   1B97 CD 5D 1D      [17]  252 	call	_cpct_etm_setTileset2x4
                            253 ;src/main.c:113: cpct_memset(CPCT_VMEM_START, 0x00, 0x4000);
   1B9A 21 00 40      [10]  254 	ld	hl, #0x4000
   1B9D E5            [11]  255 	push	hl
   1B9E AF            [ 4]  256 	xor	a, a
   1B9F F5            [11]  257 	push	af
   1BA0 33            [ 6]  258 	inc	sp
   1BA1 26 C0         [ 7]  259 	ld	h, #0xc0
   1BA3 E5            [11]  260 	push	hl
   1BA4 CD A2 1D      [17]  261 	call	_cpct_memset
                            262 ;src/main.c:121: g_tilemap);                 // Pointer to the first tile of the tilemap to be drawn (upper-left
                            263 ;src/main.c:116: cpct_etm_drawTileBox2x4(0, 0,                       // (X, Y) upper-left corner of the tilemap
   1BA7 21 40 00      [10]  264 	ld	hl, #_g_tilemap
   1BAA E5            [11]  265 	push	hl
   1BAB 21 00 C0      [10]  266 	ld	hl, #0xc000
   1BAE E5            [11]  267 	push	hl
   1BAF 21 2E 78      [10]  268 	ld	hl, #0x782e
   1BB2 E5            [11]  269 	push	hl
   1BB3 21 00 28      [10]  270 	ld	hl, #0x2800
   1BB6 E5            [11]  271 	push	hl
   1BB7 AF            [ 4]  272 	xor	a, a
   1BB8 F5            [11]  273 	push	af
   1BB9 33            [ 6]  274 	inc	sp
   1BBA CD CE 1C      [17]  275 	call	_cpct_etm_drawTileBox2x4
   1BBD C9            [10]  276 	ret
                            277 ;src/main.c:128: void main(void) {
                            278 ;	---------------------------------
                            279 ; Function main
                            280 ; ---------------------------------
   1BBE                     281 _main::
   1BBE DD E5         [15]  282 	push	ix
   1BC0 DD 21 00 00   [14]  283 	ld	ix,#0
   1BC4 DD 39         [15]  284 	add	ix,sp
   1BC6 21 F9 FF      [10]  285 	ld	hl, #-7
   1BC9 39            [11]  286 	add	hl, sp
                            287 ;src/main.c:129: TScreenTilemap scr = { CPCT_VMEM_START, g_tilemap, 0 }; // Screen tilemap properties
   1BCA F9            [ 6]  288 	ld	sp, hl
   1BCB 23            [ 6]  289 	inc	hl
   1BCC 23            [ 6]  290 	inc	hl
   1BCD 36 00         [10]  291 	ld	(hl), #0x00
   1BCF 23            [ 6]  292 	inc	hl
   1BD0 36 C0         [10]  293 	ld	(hl), #0xc0
   1BD2 21 02 00      [10]  294 	ld	hl, #0x0002
   1BD5 39            [11]  295 	add	hl, sp
   1BD6 4D            [ 4]  296 	ld	c,l
   1BD7 44            [ 4]  297 	ld	b,h
   1BD8 23            [ 6]  298 	inc	hl
   1BD9 23            [ 6]  299 	inc	hl
   1BDA 11 40 00      [10]  300 	ld	de, #_g_tilemap+0
   1BDD 73            [ 7]  301 	ld	(hl), e
   1BDE 23            [ 6]  302 	inc	hl
   1BDF 72            [ 7]  303 	ld	(hl), d
   1BE0 21 04 00      [10]  304 	ld	hl, #0x0004
   1BE3 09            [11]  305 	add	hl, bc
   1BE4 36 00         [10]  306 	ld	(hl), #0x00
                            307 ;src/main.c:132: initialize_CPC(); // Initialize the machine and set up all necessary things
   1BE6 E5            [11]  308 	push	hl
   1BE7 C5            [11]  309 	push	bc
   1BE8 CD 7A 1B      [17]  310 	call	_initialize_CPC
   1BEB C1            [10]  311 	pop	bc
   1BEC E1            [10]  312 	pop	hl
                            313 ;src/main.c:136: while(1) {
   1BED                     314 00109$:
                            315 ;src/main.c:138: scroll_offset = wait4KeyboardInput();
   1BED E5            [11]  316 	push	hl
   1BEE C5            [11]  317 	push	bc
   1BEF CD 8D 1A      [17]  318 	call	_wait4KeyboardInput
   1BF2 EB            [ 4]  319 	ex	de,hl
   1BF3 C1            [10]  320 	pop	bc
   1BF4 E1            [10]  321 	pop	hl
   1BF5 33            [ 6]  322 	inc	sp
   1BF6 33            [ 6]  323 	inc	sp
   1BF7 D5            [11]  324 	push	de
                            325 ;src/main.c:142: if     ( scr.scroll == MAXSCROLL ) continue;  // Do not scroll passed the right limit
   1BF8 5E            [ 7]  326 	ld	e, (hl)
                            327 ;src/main.c:141: if ( scroll_offset > 0 ) {
   1BF9 AF            [ 4]  328 	xor	a, a
   1BFA DD BE F9      [19]  329 	cp	a, -7 (ix)
   1BFD DD 9E FA      [19]  330 	sbc	a, -6 (ix)
   1C00 E2 05 1C      [10]  331 	jp	PO, 00125$
   1C03 EE 80         [ 7]  332 	xor	a, #0x80
   1C05                     333 00125$:
   1C05 F2 11 1C      [10]  334 	jp	P, 00106$
                            335 ;src/main.c:142: if     ( scr.scroll == MAXSCROLL ) continue;  // Do not scroll passed the right limit
   1C08 7B            [ 4]  336 	ld	a, e
   1C09 D6 50         [ 7]  337 	sub	a, #0x50
   1C0B 28 E0         [12]  338 	jr	Z,00109$
   1C0D 18 06         [12]  339 	jr	00107$
   1C0F 18 DC         [12]  340 	jr	00109$
   1C11                     341 00106$:
                            342 ;src/main.c:143: } else if ( scr.scroll ==         0 ) continue;  // Do not scroll passed the left limit
   1C11 7B            [ 4]  343 	ld	a, e
   1C12 B7            [ 4]  344 	or	a, a
   1C13 28 D8         [12]  345 	jr	Z,00109$
   1C15                     346 00107$:
                            347 ;src/main.c:146: scrollScreenTilemap(&scr, scroll_offset);
   1C15 C5            [11]  348 	push	bc
   1C16 FD E1         [14]  349 	pop	iy
   1C18 E5            [11]  350 	push	hl
   1C19 C5            [11]  351 	push	bc
   1C1A DD 5E F9      [19]  352 	ld	e,-7 (ix)
   1C1D DD 56 FA      [19]  353 	ld	d,-6 (ix)
   1C20 D5            [11]  354 	push	de
   1C21 FD E5         [15]  355 	push	iy
   1C23 CD AC 1A      [17]  356 	call	_scrollScreenTilemap
   1C26 F1            [10]  357 	pop	af
   1C27 F1            [10]  358 	pop	af
   1C28 C1            [10]  359 	pop	bc
   1C29 E1            [10]  360 	pop	hl
   1C2A 18 C1         [12]  361 	jr	00109$
                            362 	.area _CODE
                            363 	.area _INITIALIZER
                            364 	.area _CABS (ABS)
