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
                             12 	.globl _fillupScreen
                             13 	.globl _cpct_getScreenPtr
                             14 	.globl _cpct_setVideoMode
                             15 	.globl _cpct_drawTileAligned4x8_f
                             16 	.globl _cpct_drawTileAligned4x4_f
                             17 	.globl _cpct_drawTileAligned2x8_f
                             18 	.globl _cpct_drawTileAligned2x4_f
                             19 	.globl _cpct_drawTileAligned4x8
                             20 	.globl _cpct_drawTileAligned2x8
                             21 	.globl _cpct_memset
                             22 	.globl _cpct_disableFirmware
                             23 	.globl _tiles
                             24 	.globl _WAITPAINTED
                             25 	.globl _WAITCLEARED
                             26 ;--------------------------------------------------------
                             27 ; special function registers
                             28 ;--------------------------------------------------------
                             29 ;--------------------------------------------------------
                             30 ; ram data
                             31 ;--------------------------------------------------------
                             32 	.area _DATA
                             33 ;--------------------------------------------------------
                             34 ; ram data
                             35 ;--------------------------------------------------------
                             36 	.area _INITIALIZED
                             37 ;--------------------------------------------------------
                             38 ; absolute external ram data
                             39 ;--------------------------------------------------------
                             40 	.area _DABS (ABS)
                             41 ;--------------------------------------------------------
                             42 ; global & static initialisations
                             43 ;--------------------------------------------------------
                             44 	.area _HOME
                             45 	.area _GSINIT
                             46 	.area _GSFINAL
                             47 	.area _GSINIT
                             48 ;--------------------------------------------------------
                             49 ; Home
                             50 ;--------------------------------------------------------
                             51 	.area _HOME
                             52 	.area _HOME
                             53 ;--------------------------------------------------------
                             54 ; code
                             55 ;--------------------------------------------------------
                             56 	.area _CODE
                             57 ;src/main.c:53: void fillupScreen(TTile* tile) {
                             58 ;	---------------------------------
                             59 ; Function fillupScreen
                             60 ; ---------------------------------
   0100                      61 _fillupScreen::
   0100 DD E5         [15]   62 	push	ix
   0102 DD 21 00 00   [14]   63 	ld	ix,#0
   0106 DD 39         [15]   64 	add	ix,sp
   0108 21 F4 FF      [10]   65 	ld	hl, #-12
   010B 39            [11]   66 	add	hl, sp
   010C F9            [ 6]   67 	ld	sp, hl
                             68 ;src/main.c:56: u8 tilesperline = 80/tile->width;   // Number of tiles per line = LINEWIDTH / TILEWIDTH
   010D DD 4E 04      [19]   69 	ld	c,4 (ix)
   0110 DD 46 05      [19]   70 	ld	b,5 (ix)
   0113 21 02 00      [10]   71 	ld	hl, #0x0002
   0116 09            [11]   72 	add	hl,bc
   0117 DD 75 FE      [19]   73 	ld	-2 (ix), l
   011A DD 74 FF      [19]   74 	ld	-1 (ix), h
   011D 56            [ 7]   75 	ld	d, (hl)
   011E C5            [11]   76 	push	bc
   011F 1E 50         [ 7]   77 	ld	e, #0x50
   0121 D5            [11]   78 	push	de
   0122 CD 75 03      [17]   79 	call	__divuchar
   0125 F1            [10]   80 	pop	af
   0126 C1            [10]   81 	pop	bc
   0127 DD 75 F4      [19]   82 	ld	-12 (ix), l
                             83 ;src/main.c:59: for (y=0; y < 200; y += tile->height) { 
   012A DD 36 F5 00   [19]   84 	ld	-11 (ix), #0x00
   012E DD 71 FC      [19]   85 	ld	-4 (ix), c
   0131 DD 70 FD      [19]   86 	ld	-3 (ix), b
   0134 DD 71 FA      [19]   87 	ld	-6 (ix), c
   0137 DD 70 FB      [19]   88 	ld	-5 (ix), b
   013A                      89 00113$:
                             90 ;src/main.c:60: pvideomem = cpct_getScreenPtr(CPCT_VMEM_START, 0, y); // Calculate byte there this pixel line starts
   013A C5            [11]   91 	push	bc
   013B DD 7E F5      [19]   92 	ld	a, -11 (ix)
   013E F5            [11]   93 	push	af
   013F 33            [ 6]   94 	inc	sp
   0140 AF            [ 4]   95 	xor	a, a
   0141 F5            [11]   96 	push	af
   0142 33            [ 6]   97 	inc	sp
   0143 21 00 C0      [10]   98 	ld	hl, #0xc000
   0146 E5            [11]   99 	push	hl
   0147 CD 66 04      [17]  100 	call	_cpct_getScreenPtr
   014A C1            [10]  101 	pop	bc
   014B DD 75 F7      [19]  102 	ld	-9 (ix), l
   014E DD 74 F8      [19]  103 	ld	-8 (ix), h
                            104 ;src/main.c:63: for (x=0; x < tilesperline; x++) {       
   0151 DD 36 F6 00   [19]  105 	ld	-10 (ix), #0x00
   0155                     106 00111$:
   0155 DD 7E F6      [19]  107 	ld	a, -10 (ix)
   0158 DD 96 F4      [19]  108 	sub	a, -12 (ix)
   015B D2 F0 01      [10]  109 	jp	NC, 00114$
                            110 ;src/main.c:65: switch (tile->function) {
   015E DD 6E FC      [19]  111 	ld	l,-4 (ix)
   0161 DD 66 FD      [19]  112 	ld	h,-3 (ix)
   0164 11 04 00      [10]  113 	ld	de, #0x0004
   0167 19            [11]  114 	add	hl, de
   0168 7E            [ 7]  115 	ld	a, (hl)
   0169 DD 77 F9      [19]  116 	ld	-7 (ix), a
   016C 3E 05         [ 7]  117 	ld	a, #0x05
   016E DD 96 F9      [19]  118 	sub	a, -7 (ix)
   0171 38 61         [12]  119 	jr	C,00107$
                            120 ;src/main.c:66: case _2x4Fast: cpct_drawTileAligned2x4_f(tile->sprite, pvideomem); break;
   0173 DD 5E F7      [19]  121 	ld	e, -9 (ix)
   0176 DD 56 F8      [19]  122 	ld	d, -8 (ix)
   0179 D5            [11]  123 	push	de
   017A FD E1         [14]  124 	pop	iy
   017C 69            [ 4]  125 	ld	l, c
   017D 60            [ 4]  126 	ld	h, b
   017E 5E            [ 7]  127 	ld	e, (hl)
   017F 23            [ 6]  128 	inc	hl
   0180 56            [ 7]  129 	ld	d, (hl)
                            130 ;src/main.c:65: switch (tile->function) {
   0181 D5            [11]  131 	push	de
   0182 DD 5E F9      [19]  132 	ld	e, -7 (ix)
   0185 16 00         [ 7]  133 	ld	d, #0x00
   0187 21 8E 01      [10]  134 	ld	hl, #00134$
   018A 19            [11]  135 	add	hl, de
   018B 19            [11]  136 	add	hl, de
                            137 ;src/main.c:66: case _2x4Fast: cpct_drawTileAligned2x4_f(tile->sprite, pvideomem); break;
   018C D1            [10]  138 	pop	de
   018D E9            [ 4]  139 	jp	(hl)
   018E                     140 00134$:
   018E 18 28         [12]  141 	jr	00104$
   0190 18 3A         [12]  142 	jr	00106$
   0192 18 06         [12]  143 	jr	00101$
   0194 18 0E         [12]  144 	jr	00102$
   0196 18 16         [12]  145 	jr	00103$
   0198 18 28         [12]  146 	jr	00105$
   019A                     147 00101$:
   019A C5            [11]  148 	push	bc
   019B FD E5         [15]  149 	push	iy
   019D D5            [11]  150 	push	de
   019E CD F1 03      [17]  151 	call	_cpct_drawTileAligned2x4_f
   01A1 C1            [10]  152 	pop	bc
   01A2 18 30         [12]  153 	jr	00107$
                            154 ;src/main.c:67: case _4x4Fast: cpct_drawTileAligned4x4_f(tile->sprite, pvideomem); break;
   01A4                     155 00102$:
   01A4 C5            [11]  156 	push	bc
   01A5 FD E5         [15]  157 	push	iy
   01A7 D5            [11]  158 	push	de
   01A8 CD 31 04      [17]  159 	call	_cpct_drawTileAligned4x4_f
   01AB C1            [10]  160 	pop	bc
   01AC 18 26         [12]  161 	jr	00107$
                            162 ;src/main.c:68: case _2x8Fast: cpct_drawTileAligned2x8_f(tile->sprite, pvideomem); break;
   01AE                     163 00103$:
   01AE C5            [11]  164 	push	bc
   01AF FD E5         [15]  165 	push	iy
   01B1 D5            [11]  166 	push	de
   01B2 CD 7C 04      [17]  167 	call	_cpct_drawTileAligned2x8_f
   01B5 C1            [10]  168 	pop	bc
   01B6 18 1C         [12]  169 	jr	00107$
                            170 ;src/main.c:69: case _2x8:     cpct_drawTileAligned2x8  (tile->sprite, pvideomem); break;
   01B8                     171 00104$:
   01B8 C5            [11]  172 	push	bc
   01B9 FD E5         [15]  173 	push	iy
   01BB D5            [11]  174 	push	de
   01BC CD DA 03      [17]  175 	call	_cpct_drawTileAligned2x8
   01BF C1            [10]  176 	pop	bc
   01C0 18 12         [12]  177 	jr	00107$
                            178 ;src/main.c:70: case _4x8Fast: cpct_drawTileAligned4x8_f(tile->sprite, pvideomem); break;
   01C2                     179 00105$:
   01C2 C5            [11]  180 	push	bc
   01C3 FD E5         [15]  181 	push	iy
   01C5 D5            [11]  182 	push	de
   01C6 CD 08 03      [17]  183 	call	_cpct_drawTileAligned4x8_f
   01C9 C1            [10]  184 	pop	bc
   01CA 18 08         [12]  185 	jr	00107$
                            186 ;src/main.c:71: case _4x8:     cpct_drawTileAligned4x8  (tile->sprite, pvideomem); break;
   01CC                     187 00106$:
   01CC C5            [11]  188 	push	bc
   01CD FD E5         [15]  189 	push	iy
   01CF D5            [11]  190 	push	de
   01D0 CD 16 04      [17]  191 	call	_cpct_drawTileAligned4x8
   01D3 C1            [10]  192 	pop	bc
                            193 ;src/main.c:72: }
   01D4                     194 00107$:
                            195 ;src/main.c:75: pvideomem += tile->width;
   01D4 DD 6E FE      [19]  196 	ld	l,-2 (ix)
   01D7 DD 66 FF      [19]  197 	ld	h,-1 (ix)
   01DA 5E            [ 7]  198 	ld	e, (hl)
   01DB DD 7E F7      [19]  199 	ld	a, -9 (ix)
   01DE 83            [ 4]  200 	add	a, e
   01DF DD 77 F7      [19]  201 	ld	-9 (ix), a
   01E2 DD 7E F8      [19]  202 	ld	a, -8 (ix)
   01E5 CE 00         [ 7]  203 	adc	a, #0x00
   01E7 DD 77 F8      [19]  204 	ld	-8 (ix), a
                            205 ;src/main.c:63: for (x=0; x < tilesperline; x++) {       
   01EA DD 34 F6      [23]  206 	inc	-10 (ix)
   01ED C3 55 01      [10]  207 	jp	00111$
   01F0                     208 00114$:
                            209 ;src/main.c:59: for (y=0; y < 200; y += tile->height) { 
   01F0 DD 6E FA      [19]  210 	ld	l,-6 (ix)
   01F3 DD 66 FB      [19]  211 	ld	h,-5 (ix)
   01F6 23            [ 6]  212 	inc	hl
   01F7 23            [ 6]  213 	inc	hl
   01F8 23            [ 6]  214 	inc	hl
   01F9 5E            [ 7]  215 	ld	e, (hl)
   01FA DD 7E F5      [19]  216 	ld	a, -11 (ix)
   01FD 83            [ 4]  217 	add	a, e
   01FE DD 77 F5      [19]  218 	ld	-11 (ix), a
   0201 D6 C8         [ 7]  219 	sub	a, #0xc8
   0203 DA 3A 01      [10]  220 	jp	C, 00113$
   0206 DD F9         [10]  221 	ld	sp, ix
   0208 DD E1         [14]  222 	pop	ix
   020A C9            [10]  223 	ret
   020B                     224 _WAITCLEARED:
   020B 20 4E               225 	.dw #0x4e20
   020D                     226 _WAITPAINTED:
   020D 60 EA               227 	.dw #0xea60
   020F                     228 _tiles:
   020F 90 02               229 	.dw _waves_2x4
   0211 02                  230 	.db #0x02	; 2
   0212 04                  231 	.db #0x04	; 4
   0213 02                  232 	.db #0x02	; 2
   0214 B8 02               233 	.dw _waves_4x4
   0216 04                  234 	.db #0x04	; 4
   0217 04                  235 	.db #0x04	; 4
   0218 03                  236 	.db #0x03	; 3
   0219 98 02               237 	.dw _waves_2x8
   021B 02                  238 	.db #0x02	; 2
   021C 08                  239 	.db #0x08	; 8
   021D 00                  240 	.db #0x00	; 0
   021E A8 02               241 	.dw _F_2x8
   0220 02                  242 	.db #0x02	; 2
   0221 08                  243 	.db #0x08	; 8
   0222 04                  244 	.db #0x04	; 4
   0223 C8 02               245 	.dw _waves_4x8
   0225 04                  246 	.db #0x04	; 4
   0226 08                  247 	.db #0x08	; 8
   0227 01                  248 	.db #0x01	; 1
   0228 E8 02               249 	.dw _FF_4x8
   022A 04                  250 	.db #0x04	; 4
   022B 08                  251 	.db #0x08	; 8
   022C 05                  252 	.db #0x05	; 5
                            253 ;src/main.c:83: void main(void) {
                            254 ;	---------------------------------
                            255 ; Function main
                            256 ; ---------------------------------
   022D                     257 _main::
   022D DD E5         [15]  258 	push	ix
   022F DD 21 00 00   [14]  259 	ld	ix,#0
   0233 DD 39         [15]  260 	add	ix,sp
   0235 3B            [ 6]  261 	dec	sp
                            262 ;src/main.c:85: cpct_disableFirmware();
   0236 CD CA 03      [17]  263 	call	_cpct_disableFirmware
                            264 ;src/main.c:86: cpct_setVideoMode(0);
   0239 2E 00         [ 7]  265 	ld	l, #0x00
   023B CD AE 03      [17]  266 	call	_cpct_setVideoMode
                            267 ;src/main.c:96: for (i=0; i < 6; i++) {
   023E                     268 00121$:
   023E DD 36 FF 00   [19]  269 	ld	-1 (ix), #0x00
   0242                     270 00113$:
                            271 ;src/main.c:98: cpct_clearScreen(0);
   0242 21 00 40      [10]  272 	ld	hl, #0x4000
   0245 E5            [11]  273 	push	hl
   0246 AF            [ 4]  274 	xor	a, a
   0247 F5            [11]  275 	push	af
   0248 33            [ 6]  276 	inc	sp
   0249 26 C0         [ 7]  277 	ld	h, #0xc0
   024B E5            [11]  278 	push	hl
   024C CD BC 03      [17]  279 	call	_cpct_memset
                            280 ;src/main.c:99: for (w=0; w < WAITCLEARED; w++);
   024F 11 00 00      [10]  281 	ld	de, #0x0000
   0252                     282 00108$:
   0252 2A 0B 02      [16]  283 	ld	hl, (_WAITCLEARED)
   0255 7B            [ 4]  284 	ld	a, e
   0256 95            [ 4]  285 	sub	a, l
   0257 7A            [ 4]  286 	ld	a, d
   0258 9C            [ 4]  287 	sbc	a, h
   0259 30 03         [12]  288 	jr	NC,00101$
   025B 13            [ 6]  289 	inc	de
   025C 18 F4         [12]  290 	jr	00108$
   025E                     291 00101$:
                            292 ;src/main.c:102: fillupScreen(&(tiles[i]));
   025E DD 4E FF      [19]  293 	ld	c,-1 (ix)
   0261 06 00         [ 7]  294 	ld	b,#0x00
   0263 69            [ 4]  295 	ld	l, c
   0264 60            [ 4]  296 	ld	h, b
   0265 29            [11]  297 	add	hl, hl
   0266 29            [11]  298 	add	hl, hl
   0267 09            [11]  299 	add	hl, bc
   0268 11 0F 02      [10]  300 	ld	de, #_tiles
   026B 19            [11]  301 	add	hl, de
   026C E5            [11]  302 	push	hl
   026D CD 00 01      [17]  303 	call	_fillupScreen
   0270 F1            [10]  304 	pop	af
                            305 ;src/main.c:103: for (w=0; w < WAITPAINTED; w++);
   0271 01 00 00      [10]  306 	ld	bc, #0x0000
   0274                     307 00111$:
   0274 2A 0D 02      [16]  308 	ld	hl, (_WAITPAINTED)
   0277 79            [ 4]  309 	ld	a, c
   0278 95            [ 4]  310 	sub	a, l
   0279 78            [ 4]  311 	ld	a, b
   027A 9C            [ 4]  312 	sbc	a, h
   027B 30 03         [12]  313 	jr	NC,00114$
   027D 03            [ 6]  314 	inc	bc
   027E 18 F4         [12]  315 	jr	00111$
   0280                     316 00114$:
                            317 ;src/main.c:96: for (i=0; i < 6; i++) {
   0280 DD 34 FF      [23]  318 	inc	-1 (ix)
   0283 DD 7E FF      [19]  319 	ld	a, -1 (ix)
   0286 D6 06         [ 7]  320 	sub	a, #0x06
   0288 38 B8         [12]  321 	jr	C,00113$
   028A 18 B2         [12]  322 	jr	00121$
   028C 33            [ 6]  323 	inc	sp
   028D DD E1         [14]  324 	pop	ix
   028F C9            [10]  325 	ret
                            326 	.area _CODE
                            327 	.area _INITIALIZER
                            328 	.area _CABS (ABS)
