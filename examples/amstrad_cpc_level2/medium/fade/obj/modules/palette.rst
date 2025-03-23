                              1 ;--------------------------------------------------------
                              2 ; File Created by SDCC : free open source ANSI-C Compiler
                              3 ; Version 3.6.8 #9946 (Linux)
                              4 ;--------------------------------------------------------
                              5 	.module palette
                              6 	.optsdcc -mz80
                              7 	
                              8 ;--------------------------------------------------------
                              9 ; Public variables in this module
                             10 ;--------------------------------------------------------
                             11 	.globl _wait_frames
                             12 	.globl _cpct_setPALColour
                             13 	.globl _G_rgb2hw
                             14 	.globl _G_rgb_palette
                             15 	.globl _setPALColourRGBLimited
                             16 	.globl _fade_in
                             17 	.globl _fade_out
                             18 	.globl _setBlackPalette
                             19 ;--------------------------------------------------------
                             20 ; special function registers
                             21 ;--------------------------------------------------------
                             22 ;--------------------------------------------------------
                             23 ; ram data
                             24 ;--------------------------------------------------------
                             25 	.area _DATA
                             26 ;--------------------------------------------------------
                             27 ; ram data
                             28 ;--------------------------------------------------------
                             29 	.area _INITIALIZED
                             30 ;--------------------------------------------------------
                             31 ; absolute external ram data
                             32 ;--------------------------------------------------------
                             33 	.area _DABS (ABS)
                             34 ;--------------------------------------------------------
                             35 ; global & static initialisations
                             36 ;--------------------------------------------------------
                             37 	.area _HOME
                             38 	.area _GSINIT
                             39 	.area _GSFINAL
                             40 	.area _GSINIT
                             41 ;--------------------------------------------------------
                             42 ; Home
                             43 ;--------------------------------------------------------
                             44 	.area _HOME
                             45 	.area _HOME
                             46 ;--------------------------------------------------------
                             47 ; code
                             48 ;--------------------------------------------------------
                             49 	.area _CODE
                             50 ;src/modules/palette.c:80: void setPALColourRGBLimited(u8 pal_index, const u8 rgb[3], const u8 maxrgb[3]) {
                             51 ;	---------------------------------
                             52 ; Function setPALColourRGBLimited
                             53 ; ---------------------------------
   0174                      54 _setPALColourRGBLimited::
   0174 DD E5         [15]   55 	push	ix
   0176 DD 21 00 00   [14]   56 	ld	ix,#0
   017A DD 39         [15]   57 	add	ix,sp
   017C 21 FA FF      [10]   58 	ld	hl, #-6
   017F 39            [11]   59 	add	hl, sp
   0180 F9            [ 6]   60 	ld	sp, hl
                             61 ;src/modules/palette.c:86: for (i=0; i < 3; ++i) {
   0181 21 00 00      [10]   62 	ld	hl, #0x0000
   0184 39            [11]   63 	add	hl, sp
   0185 DD 75 FE      [19]   64 	ld	-2 (ix), l
   0188 DD 74 FF      [19]   65 	ld	-1 (ix), h
   018B 0E 00         [ 7]   66 	ld	c, #0x00
   018D                      67 00104$:
                             68 ;src/modules/palette.c:87: s[i] = rgb[i];  // The colour component to set is the one given in rgb[]
   018D DD 7E FE      [19]   69 	ld	a, -2 (ix)
   0190 81            [ 4]   70 	add	a, c
   0191 5F            [ 4]   71 	ld	e, a
   0192 DD 7E FF      [19]   72 	ld	a, -1 (ix)
   0195 CE 00         [ 7]   73 	adc	a, #0x00
   0197 57            [ 4]   74 	ld	d, a
   0198 E5            [11]   75 	push	hl
   0199 DD 6E 05      [19]   76 	ld	l, 5 (ix)
   019C DD 66 06      [19]   77 	ld	h, 6 (ix)
   019F E5            [11]   78 	push	hl
   01A0 FD E1         [14]   79 	pop	iy
   01A2 E1            [10]   80 	pop	hl
   01A3 C5            [11]   81 	push	bc
   01A4 06 00         [ 7]   82 	ld	b,#0x00
   01A6 FD 09         [15]   83 	add	iy, bc
   01A8 C1            [10]   84 	pop	bc
   01A9 FD 7E 00      [19]   85 	ld	a, 0 (iy)
   01AC 12            [ 7]   86 	ld	(de), a
                             87 ;src/modules/palette.c:91: if ( rgb[i] > maxrgb[i] ) 
   01AD FD 7E 00      [19]   88 	ld	a, 0 (iy)
   01B0 DD 77 FD      [19]   89 	ld	-3 (ix), a
   01B3 DD 6E 07      [19]   90 	ld	l,7 (ix)
   01B6 DD 66 08      [19]   91 	ld	h,8 (ix)
   01B9 06 00         [ 7]   92 	ld	b, #0x00
   01BB 09            [11]   93 	add	hl, bc
   01BC 46            [ 7]   94 	ld	b, (hl)
   01BD 78            [ 4]   95 	ld	a, b
   01BE DD 96 FD      [19]   96 	sub	a, -3 (ix)
   01C1 30 02         [12]   97 	jr	NC,00105$
                             98 ;src/modules/palette.c:92: s[i] = maxrgb[i];
   01C3 78            [ 4]   99 	ld	a, b
   01C4 12            [ 7]  100 	ld	(de), a
   01C5                     101 00105$:
                            102 ;src/modules/palette.c:86: for (i=0; i < 3; ++i) {
   01C5 0C            [ 4]  103 	inc	c
   01C6 79            [ 4]  104 	ld	a, c
   01C7 D6 03         [ 7]  105 	sub	a, #0x03
   01C9 38 C2         [12]  106 	jr	C,00104$
                            107 ;src/modules/palette.c:96: i = G_rgb2hw[ s[0] ][ s[1] ][ s[2] ];
   01CB 01 41 02      [10]  108 	ld	bc, #_G_rgb2hw+0
   01CE DD 6E FE      [19]  109 	ld	l,-2 (ix)
   01D1 DD 66 FF      [19]  110 	ld	h,-1 (ix)
   01D4 5E            [ 7]  111 	ld	e, (hl)
   01D5 16 00         [ 7]  112 	ld	d,#0x00
   01D7 6B            [ 4]  113 	ld	l, e
   01D8 62            [ 4]  114 	ld	h, d
   01D9 29            [11]  115 	add	hl, hl
   01DA 29            [11]  116 	add	hl, hl
   01DB 29            [11]  117 	add	hl, hl
   01DC 19            [11]  118 	add	hl, de
   01DD 09            [11]  119 	add	hl,bc
   01DE 4D            [ 4]  120 	ld	c, l
   01DF 44            [ 4]  121 	ld	b, h
   01E0 DD 6E FE      [19]  122 	ld	l,-2 (ix)
   01E3 DD 66 FF      [19]  123 	ld	h,-1 (ix)
   01E6 23            [ 6]  124 	inc	hl
   01E7 5E            [ 7]  125 	ld	e, (hl)
   01E8 6B            [ 4]  126 	ld	l, e
   01E9 29            [11]  127 	add	hl, hl
   01EA 19            [11]  128 	add	hl, de
   01EB 79            [ 4]  129 	ld	a, c
   01EC 85            [ 4]  130 	add	a, l
   01ED 4F            [ 4]  131 	ld	c, a
   01EE 78            [ 4]  132 	ld	a, b
   01EF CE 00         [ 7]  133 	adc	a, #0x00
   01F1 47            [ 4]  134 	ld	b, a
   01F2 DD 6E FE      [19]  135 	ld	l,-2 (ix)
   01F5 DD 66 FF      [19]  136 	ld	h,-1 (ix)
   01F8 23            [ 6]  137 	inc	hl
   01F9 23            [ 6]  138 	inc	hl
   01FA 6E            [ 7]  139 	ld	l, (hl)
   01FB 26 00         [ 7]  140 	ld	h,#0x00
   01FD 09            [11]  141 	add	hl, bc
   01FE 46            [ 7]  142 	ld	b, (hl)
                            143 ;src/modules/palette.c:99: cpct_setPALColour(pal_index, i);
   01FF C5            [11]  144 	push	bc
   0200 33            [ 6]  145 	inc	sp
   0201 DD 7E 04      [19]  146 	ld	a, 4 (ix)
   0204 F5            [11]  147 	push	af
   0205 33            [ 6]  148 	inc	sp
   0206 CD 65 1E      [17]  149 	call	_cpct_setPALColour
   0209 DD F9         [10]  150 	ld	sp, ix
   020B DD E1         [14]  151 	pop	ix
   020D C9            [10]  152 	ret
   020E                     153 _G_rgb_palette:
   020E 01                  154 	.db #0x01	; 1
   020F 01                  155 	.db #0x01	; 1
   0210 01                  156 	.db #0x01	; 1
   0211 02                  157 	.db #0x02	; 2
   0212 01                  158 	.db #0x01	; 1
   0213 00                  159 	.db #0x00	; 0
   0214 01                  160 	.db #0x01	; 1
   0215 00                  161 	.db #0x00	; 0
   0216 00                  162 	.db #0x00	; 0
   0217 02                  163 	.db #0x02	; 2
   0218 02                  164 	.db #0x02	; 2
   0219 00                  165 	.db #0x00	; 0
   021A 00                  166 	.db #0x00	; 0
   021B 00                  167 	.db #0x00	; 0
   021C 01                  168 	.db #0x01	; 1
   021D 00                  169 	.db #0x00	; 0
   021E 00                  170 	.db #0x00	; 0
   021F 02                  171 	.db #0x02	; 2
   0220 02                  172 	.db #0x02	; 2
   0221 00                  173 	.db #0x00	; 0
   0222 00                  174 	.db #0x00	; 0
   0223 02                  175 	.db #0x02	; 2
   0224 02                  176 	.db #0x02	; 2
   0225 02                  177 	.db #0x02	; 2
   0226 00                  178 	.db #0x00	; 0
   0227 00                  179 	.db #0x00	; 0
   0228 00                  180 	.db #0x00	; 0
   0229 00                  181 	.db #0x00	; 0
   022A 00                  182 	.db #0x00	; 0
   022B 02                  183 	.db #0x02	; 2
   022C 00                  184 	.db #0x00	; 0
   022D 01                  185 	.db #0x01	; 1
   022E 02                  186 	.db #0x02	; 2
   022F 00                  187 	.db #0x00	; 0
   0230 02                  188 	.db #0x02	; 2
   0231 00                  189 	.db #0x00	; 0
   0232 02                  190 	.db #0x02	; 2
   0233 00                  191 	.db #0x00	; 0
   0234 02                  192 	.db #0x02	; 2
   0235 01                  193 	.db #0x01	; 1
   0236 00                  194 	.db #0x00	; 0
   0237 02                  195 	.db #0x02	; 2
   0238 02                  196 	.db #0x02	; 2
   0239 01                  197 	.db #0x01	; 1
   023A 01                  198 	.db #0x01	; 1
   023B 00                  199 	.db #0x00	; 0
   023C 01                  200 	.db #0x01	; 1
   023D 00                  201 	.db #0x00	; 0
   023E 01                  202 	.db #0x01	; 1
   023F 01                  203 	.db #0x01	; 1
   0240 01                  204 	.db #0x01	; 1
   0241                     205 _G_rgb2hw:
   0241 14                  206 	.db #0x14	; 20
   0242 04                  207 	.db #0x04	; 4
   0243 15                  208 	.db #0x15	; 21
   0244 16                  209 	.db #0x16	; 22
   0245 06                  210 	.db #0x06	; 6
   0246 17                  211 	.db #0x17	; 23
   0247 12                  212 	.db #0x12	; 18
   0248 02                  213 	.db #0x02	; 2
   0249 13                  214 	.db #0x13	; 19
   024A 1C                  215 	.db #0x1c	; 28
   024B 18                  216 	.db #0x18	; 24
   024C 1D                  217 	.db #0x1d	; 29
   024D 1E                  218 	.db #0x1e	; 30
   024E 00                  219 	.db #0x00	; 0
   024F 1F                  220 	.db #0x1f	; 31
   0250 1A                  221 	.db #0x1a	; 26
   0251 19                  222 	.db #0x19	; 25
   0252 1B                  223 	.db #0x1b	; 27
   0253 0C                  224 	.db #0x0c	; 12
   0254 05                  225 	.db #0x05	; 5
   0255 0D                  226 	.db #0x0d	; 13
   0256 0E                  227 	.db #0x0e	; 14
   0257 07                  228 	.db #0x07	; 7
   0258 0F                  229 	.db #0x0f	; 15
   0259 0A                  230 	.db #0x0a	; 10
   025A 03                  231 	.db #0x03	; 3
   025B 0B                  232 	.db #0x0b	; 11
                            233 ;src/modules/palette.c:116: void fade_in(const u8 rgb[][3], u8 min_pi, u8 max_pi, u8 wait) {
                            234 ;	---------------------------------
                            235 ; Function fade_in
                            236 ; ---------------------------------
   025C                     237 _fade_in::
   025C DD E5         [15]  238 	push	ix
   025E DD 21 00 00   [14]  239 	ld	ix,#0
   0262 DD 39         [15]  240 	add	ix,sp
   0264 21 F5 FF      [10]  241 	ld	hl, #-11
   0267 39            [11]  242 	add	hl, sp
   0268 F9            [ 6]  243 	ld	sp, hl
                            244 ;src/modules/palette.c:119: u8 maxrgb[3]={0,0,0}; // Maximum components for the 3 RGB values, initially 0 (to slowly increase)
   0269 21 00 00      [10]  245 	ld	hl, #0x0000
   026C 39            [11]  246 	add	hl, sp
   026D 4D            [ 4]  247 	ld	c, l
   026E 44            [ 4]  248 	ld	b, h
   026F AF            [ 4]  249 	xor	a, a
   0270 02            [ 7]  250 	ld	(bc), a
   0271 59            [ 4]  251 	ld	e, c
   0272 50            [ 4]  252 	ld	d, b
   0273 13            [ 6]  253 	inc	de
   0274 AF            [ 4]  254 	xor	a, a
   0275 12            [ 7]  255 	ld	(de), a
   0276 59            [ 4]  256 	ld	e, c
   0277 50            [ 4]  257 	ld	d, b
   0278 13            [ 6]  258 	inc	de
   0279 13            [ 6]  259 	inc	de
   027A AF            [ 4]  260 	xor	a, a
   027B 12            [ 7]  261 	ld	(de), a
                            262 ;src/modules/palette.c:126: while (maxrgb[col] <= 2) {
   027C DD 71 FE      [19]  263 	ld	-2 (ix), c
   027F DD 70 FF      [19]  264 	ld	-1 (ix), b
   0282 1E 00         [ 7]  265 	ld	e, #0x00
   0284                     266 00102$:
   0284 7B            [ 4]  267 	ld	a, e
   0285 81            [ 4]  268 	add	a, c
   0286 DD 77 FA      [19]  269 	ld	-6 (ix), a
   0289 3E 00         [ 7]  270 	ld	a, #0x00
   028B 88            [ 4]  271 	adc	a, b
   028C DD 77 FB      [19]  272 	ld	-5 (ix), a
   028F DD 6E FA      [19]  273 	ld	l,-6 (ix)
   0292 DD 66 FB      [19]  274 	ld	h,-5 (ix)
   0295 56            [ 7]  275 	ld	d, (hl)
   0296 3E 02         [ 7]  276 	ld	a, #0x02
   0298 92            [ 4]  277 	sub	a, d
   0299 38 6F         [12]  278 	jr	C,00110$
                            279 ;src/modules/palette.c:130: for(pi=min_pi; pi <= max_pi; ++pi)
   029B DD 56 06      [19]  280 	ld	d, 6 (ix)
   029E                     281 00107$:
   029E DD 7E 07      [19]  282 	ld	a, 7 (ix)
   02A1 92            [ 4]  283 	sub	a, d
   02A2 38 46         [12]  284 	jr	C,00101$
                            285 ;src/modules/palette.c:131: setPALColourRGBLimited(pi, rgb[pi], maxrgb);
   02A4 DD 7E FE      [19]  286 	ld	a, -2 (ix)
   02A7 DD 77 FC      [19]  287 	ld	-4 (ix), a
   02AA DD 7E FF      [19]  288 	ld	a, -1 (ix)
   02AD DD 77 FD      [19]  289 	ld	-3 (ix), a
   02B0 D5            [11]  290 	push	de
   02B1 5A            [ 4]  291 	ld	e,d
   02B2 16 00         [ 7]  292 	ld	d,#0x00
   02B4 6B            [ 4]  293 	ld	l, e
   02B5 62            [ 4]  294 	ld	h, d
   02B6 29            [11]  295 	add	hl, hl
   02B7 19            [11]  296 	add	hl, de
   02B8 D1            [10]  297 	pop	de
   02B9 DD 75 F8      [19]  298 	ld	-8 (ix), l
   02BC DD 74 F9      [19]  299 	ld	-7 (ix), h
   02BF E5            [11]  300 	push	hl
   02C0 DD 6E 04      [19]  301 	ld	l, 4 (ix)
   02C3 DD 66 05      [19]  302 	ld	h, 5 (ix)
   02C6 E5            [11]  303 	push	hl
   02C7 FD E1         [14]  304 	pop	iy
   02C9 E1            [10]  305 	pop	hl
   02CA C5            [11]  306 	push	bc
   02CB DD 4E F8      [19]  307 	ld	c,-8 (ix)
   02CE DD 46 F9      [19]  308 	ld	b,-7 (ix)
   02D1 FD 09         [15]  309 	add	iy, bc
   02D3 D5            [11]  310 	push	de
   02D4 DD 6E FC      [19]  311 	ld	l,-4 (ix)
   02D7 DD 66 FD      [19]  312 	ld	h,-3 (ix)
   02DA E5            [11]  313 	push	hl
   02DB FD E5         [15]  314 	push	iy
   02DD D5            [11]  315 	push	de
   02DE 33            [ 6]  316 	inc	sp
   02DF CD 74 01      [17]  317 	call	_setPALColourRGBLimited
   02E2 F1            [10]  318 	pop	af
   02E3 F1            [10]  319 	pop	af
   02E4 33            [ 6]  320 	inc	sp
   02E5 D1            [10]  321 	pop	de
   02E6 C1            [10]  322 	pop	bc
                            323 ;src/modules/palette.c:130: for(pi=min_pi; pi <= max_pi; ++pi)
   02E7 14            [ 4]  324 	inc	d
   02E8 18 B4         [12]  325 	jr	00107$
   02EA                     326 00101$:
                            327 ;src/modules/palette.c:133: ++maxrgb[col];     // Increase present maximum colour component limit
   02EA DD 6E FA      [19]  328 	ld	l,-6 (ix)
   02ED DD 66 FB      [19]  329 	ld	h,-5 (ix)
   02F0 56            [ 7]  330 	ld	d, (hl)
   02F1 14            [ 4]  331 	inc	d
   02F2 DD 6E FA      [19]  332 	ld	l,-6 (ix)
   02F5 DD 66 FB      [19]  333 	ld	h,-5 (ix)
   02F8 72            [ 7]  334 	ld	(hl), d
                            335 ;src/modules/palette.c:134: wait_frames(wait); // Wait some frames to slow down the effect and see the changes
   02F9 DD 6E 08      [19]  336 	ld	l, 8 (ix)
   02FC 26 00         [ 7]  337 	ld	h, #0x00
   02FE C5            [11]  338 	push	bc
   02FF D5            [11]  339 	push	de
   0300 E5            [11]  340 	push	hl
   0301 CD 3A 1E      [17]  341 	call	_wait_frames
   0304 F1            [10]  342 	pop	af
   0305 D1            [10]  343 	pop	de
   0306 C1            [10]  344 	pop	bc
   0307 C3 84 02      [10]  345 	jp	00102$
   030A                     346 00110$:
                            347 ;src/modules/palette.c:122: for(col=0; col <= 2; ++col){
   030A 1C            [ 4]  348 	inc	e
   030B 3E 02         [ 7]  349 	ld	a, #0x02
   030D 93            [ 4]  350 	sub	a, e
   030E D2 84 02      [10]  351 	jp	NC, 00102$
   0311 DD F9         [10]  352 	ld	sp, ix
   0313 DD E1         [14]  353 	pop	ix
   0315 C9            [10]  354 	ret
                            355 ;src/modules/palette.c:145: void fade_out(const u8 rgb[][3], u8 min_pi, u8 max_pi, u8 wait) {
                            356 ;	---------------------------------
                            357 ; Function fade_out
                            358 ; ---------------------------------
   0316                     359 _fade_out::
   0316 DD E5         [15]  360 	push	ix
   0318 DD 21 00 00   [14]  361 	ld	ix,#0
   031C DD 39         [15]  362 	add	ix,sp
   031E 21 F5 FF      [10]  363 	ld	hl, #-11
   0321 39            [11]  364 	add	hl, sp
   0322 F9            [ 6]  365 	ld	sp, hl
                            366 ;src/modules/palette.c:148: u8 maxrgb[3]={2,2,2}; // Maximum components for the 3 RGB values, initially 2 (to slowly decrease)
   0323 21 00 00      [10]  367 	ld	hl, #0x0000
   0326 39            [11]  368 	add	hl, sp
   0327 4D            [ 4]  369 	ld	c,l
   0328 44            [ 4]  370 	ld	b,h
   0329 36 02         [10]  371 	ld	(hl),#0x02
   032B 69            [ 4]  372 	ld	l, c
   032C 60            [ 4]  373 	ld	h, b
   032D 23            [ 6]  374 	inc	hl
   032E 36 02         [10]  375 	ld	(hl), #0x02
   0330 69            [ 4]  376 	ld	l, c
   0331 60            [ 4]  377 	ld	h, b
   0332 23            [ 6]  378 	inc	hl
   0333 23            [ 6]  379 	inc	hl
   0334 36 02         [10]  380 	ld	(hl), #0x02
                            381 ;src/modules/palette.c:155: do {
   0336 DD 71 FE      [19]  382 	ld	-2 (ix), c
   0339 DD 70 FF      [19]  383 	ld	-1 (ix), b
   033C 1E 00         [ 7]  384 	ld	e, #0x00
   033E                     385 00102$:
                            386 ;src/modules/palette.c:156: --maxrgb[col];  // Decrease present maximum colour component limit
   033E 7B            [ 4]  387 	ld	a, e
   033F 81            [ 4]  388 	add	a, c
   0340 DD 77 F8      [19]  389 	ld	-8 (ix), a
   0343 3E 00         [ 7]  390 	ld	a, #0x00
   0345 88            [ 4]  391 	adc	a, b
   0346 DD 77 F9      [19]  392 	ld	-7 (ix), a
   0349 DD 6E F8      [19]  393 	ld	l,-8 (ix)
   034C DD 66 F9      [19]  394 	ld	h,-7 (ix)
   034F 56            [ 7]  395 	ld	d, (hl)
   0350 15            [ 4]  396 	dec	d
   0351 DD 6E F8      [19]  397 	ld	l,-8 (ix)
   0354 DD 66 F9      [19]  398 	ld	h,-7 (ix)
   0357 72            [ 7]  399 	ld	(hl), d
                            400 ;src/modules/palette.c:160: for(pi=min_pi; pi <= max_pi; ++pi)
   0358 DD 56 06      [19]  401 	ld	d, 6 (ix)
   035B                     402 00107$:
   035B DD 7E 07      [19]  403 	ld	a, 7 (ix)
   035E 92            [ 4]  404 	sub	a, d
   035F 38 46         [12]  405 	jr	C,00101$
                            406 ;src/modules/palette.c:161: setPALColourRGBLimited(pi, rgb[pi], maxrgb);
   0361 DD 7E FE      [19]  407 	ld	a, -2 (ix)
   0364 DD 77 FC      [19]  408 	ld	-4 (ix), a
   0367 DD 7E FF      [19]  409 	ld	a, -1 (ix)
   036A DD 77 FD      [19]  410 	ld	-3 (ix), a
   036D D5            [11]  411 	push	de
   036E 5A            [ 4]  412 	ld	e,d
   036F 16 00         [ 7]  413 	ld	d,#0x00
   0371 6B            [ 4]  414 	ld	l, e
   0372 62            [ 4]  415 	ld	h, d
   0373 29            [11]  416 	add	hl, hl
   0374 19            [11]  417 	add	hl, de
   0375 D1            [10]  418 	pop	de
   0376 DD 75 FA      [19]  419 	ld	-6 (ix), l
   0379 DD 74 FB      [19]  420 	ld	-5 (ix), h
   037C E5            [11]  421 	push	hl
   037D DD 6E FA      [19]  422 	ld	l, -6 (ix)
   0380 DD 66 FB      [19]  423 	ld	h, -5 (ix)
   0383 E5            [11]  424 	push	hl
   0384 FD E1         [14]  425 	pop	iy
   0386 E1            [10]  426 	pop	hl
   0387 C5            [11]  427 	push	bc
   0388 DD 4E 04      [19]  428 	ld	c,4 (ix)
   038B DD 46 05      [19]  429 	ld	b,5 (ix)
   038E FD 09         [15]  430 	add	iy, bc
   0390 D5            [11]  431 	push	de
   0391 DD 6E FC      [19]  432 	ld	l,-4 (ix)
   0394 DD 66 FD      [19]  433 	ld	h,-3 (ix)
   0397 E5            [11]  434 	push	hl
   0398 FD E5         [15]  435 	push	iy
   039A D5            [11]  436 	push	de
   039B 33            [ 6]  437 	inc	sp
   039C CD 74 01      [17]  438 	call	_setPALColourRGBLimited
   039F F1            [10]  439 	pop	af
   03A0 F1            [10]  440 	pop	af
   03A1 33            [ 6]  441 	inc	sp
   03A2 D1            [10]  442 	pop	de
   03A3 C1            [10]  443 	pop	bc
                            444 ;src/modules/palette.c:160: for(pi=min_pi; pi <= max_pi; ++pi)
   03A4 14            [ 4]  445 	inc	d
   03A5 18 B4         [12]  446 	jr	00107$
   03A7                     447 00101$:
                            448 ;src/modules/palette.c:163: wait_frames(wait); // Wait some frames to slow down the effect and see the changes
   03A7 DD 6E 08      [19]  449 	ld	l, 8 (ix)
   03AA 26 00         [ 7]  450 	ld	h, #0x00
   03AC C5            [11]  451 	push	bc
   03AD D5            [11]  452 	push	de
   03AE E5            [11]  453 	push	hl
   03AF CD 3A 1E      [17]  454 	call	_wait_frames
   03B2 F1            [10]  455 	pop	af
   03B3 D1            [10]  456 	pop	de
   03B4 C1            [10]  457 	pop	bc
                            458 ;src/modules/palette.c:164: } while (maxrgb[col] > 0);
   03B5 DD 6E F8      [19]  459 	ld	l,-8 (ix)
   03B8 DD 66 F9      [19]  460 	ld	h,-7 (ix)
   03BB 7E            [ 7]  461 	ld	a, (hl)
   03BC B7            [ 4]  462 	or	a, a
   03BD C2 3E 03      [10]  463 	jp	NZ, 00102$
                            464 ;src/modules/palette.c:151: for(col=0; col <= 2; ++col){
   03C0 1C            [ 4]  465 	inc	e
   03C1 3E 02         [ 7]  466 	ld	a, #0x02
   03C3 93            [ 4]  467 	sub	a, e
   03C4 D2 3E 03      [10]  468 	jp	NC, 00102$
   03C7 DD F9         [10]  469 	ld	sp, ix
   03C9 DD E1         [14]  470 	pop	ix
   03CB C9            [10]  471 	ret
                            472 ;src/modules/palette.c:172: void setBlackPalette(u8 min_pi, u8 max_pi) {
                            473 ;	---------------------------------
                            474 ; Function setBlackPalette
                            475 ; ---------------------------------
   03CC                     476 _setBlackPalette::
                            477 ;src/modules/palette.c:176: for(i=min_pi; i <= max_pi; ++i)
   03CC 21 02 00      [10]  478 	ld	hl, #2+0
   03CF 39            [11]  479 	add	hl, sp
   03D0 46            [ 7]  480 	ld	b, (hl)
   03D1                     481 00103$:
   03D1 21 03 00      [10]  482 	ld	hl, #3
   03D4 39            [11]  483 	add	hl, sp
   03D5 7E            [ 7]  484 	ld	a, (hl)
   03D6 90            [ 4]  485 	sub	a, b
   03D7 D8            [11]  486 	ret	C
                            487 ;src/modules/palette.c:177: cpct_setPALColour(i, G_rgb2hw[0][0][0]);  
   03D8 21 41 02      [10]  488 	ld	hl, #_G_rgb2hw + 0
   03DB 56            [ 7]  489 	ld	d, (hl)
   03DC C5            [11]  490 	push	bc
   03DD 58            [ 4]  491 	ld	e, b
   03DE D5            [11]  492 	push	de
   03DF CD 65 1E      [17]  493 	call	_cpct_setPALColour
   03E2 C1            [10]  494 	pop	bc
                            495 ;src/modules/palette.c:176: for(i=min_pi; i <= max_pi; ++i)
   03E3 04            [ 4]  496 	inc	b
   03E4 18 EB         [12]  497 	jr	00103$
                            498 	.area _CODE
                            499 	.area _INITIALIZER
                            500 	.area _CABS (ABS)
