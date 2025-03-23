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
                             12 	.globl _checkUserInput
                             13 	.globl _drawEntity
                             14 	.globl _shiftSprite
                             15 	.globl _shiftSpritePixelsLeft
                             16 	.globl _shiftSpritePixelsRight
                             17 	.globl _cpct_getScreenPtr
                             18 	.globl _cpct_setPALColour
                             19 	.globl _cpct_setPalette
                             20 	.globl _cpct_waitVSYNC
                             21 	.globl _cpct_setVideoMode
                             22 	.globl _cpct_drawSprite
                             23 	.globl _cpct_drawSolidBox
                             24 	.globl _cpct_isKeyPressed
                             25 	.globl _cpct_scanKeyboard_f
                             26 	.globl _cpct_memset_f64
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
                             59 ;src/main.c:53: void shiftSpritePixelsRight(u8* sprite, u8 size) {
                             60 ;	---------------------------------
                             61 ; Function shiftSpritePixelsRight
                             62 ; ---------------------------------
   4000                      63 _shiftSpritePixelsRight::
   4000 DD E5         [15]   64 	push	ix
   4002 DD 21 00 00   [14]   65 	ld	ix,#0
   4006 DD 39         [15]   66 	add	ix,sp
   4008 3B            [ 6]   67 	dec	sp
                             68 ;src/main.c:58: prev_rightpixel = 0;
   4009 0E 00         [ 7]   69 	ld	c, #0x00
                             70 ;src/main.c:59: do {
   400B DD 6E 04      [19]   71 	ld	l,4 (ix)
   400E DD 66 05      [19]   72 	ld	h,5 (ix)
   4011 DD 46 06      [19]   73 	ld	b, 6 (ix)
   4014                      74 00101$:
                             75 ;src/main.c:61: rightpixel      = *sprite & 0b01010101;
   4014 5E            [ 7]   76 	ld	e, (hl)
   4015 7B            [ 4]   77 	ld	a, e
   4016 E6 55         [ 7]   78 	and	a, #0x55
   4018 DD 77 FF      [19]   79 	ld	-1 (ix), a
                             80 ;src/main.c:64: *sprite         = (prev_rightpixel << 1) | ((*sprite & 0b10101010) >> 1);
   401B CB 21         [ 8]   81 	sla	c
   401D 7B            [ 4]   82 	ld	a, e
   401E E6 AA         [ 7]   83 	and	a, #0xaa
   4020 CB 3F         [ 8]   84 	srl	a
   4022 B1            [ 4]   85 	or	a, c
   4023 77            [ 7]   86 	ld	(hl), a
                             87 ;src/main.c:66: prev_rightpixel = rightpixel;
   4024 DD 4E FF      [19]   88 	ld	c, -1 (ix)
                             89 ;src/main.c:67: ++sprite;
   4027 23            [ 6]   90 	inc	hl
                             91 ;src/main.c:68: } while(--size);
   4028 10 EA         [13]   92 	djnz	00101$
   402A 33            [ 6]   93 	inc	sp
   402B DD E1         [14]   94 	pop	ix
   402D C9            [10]   95 	ret
                             96 ;src/main.c:74: void shiftSpritePixelsLeft(u8* sprite, u8 size) {
                             97 ;	---------------------------------
                             98 ; Function shiftSpritePixelsLeft
                             99 ; ---------------------------------
   402E                     100 _shiftSpritePixelsLeft::
   402E DD E5         [15]  101 	push	ix
   4030 DD 21 00 00   [14]  102 	ld	ix,#0
   4034 DD 39         [15]  103 	add	ix,sp
   4036 F5            [11]  104 	push	af
                            105 ;src/main.c:75: u8* next_byte = sprite + 1; // Maintain a pointer to the next byte of the sprite 
   4037 DD 4E 04      [19]  106 	ld	c,4 (ix)
   403A DD 46 05      [19]  107 	ld	b,5 (ix)
   403D 03            [ 6]  108 	inc	bc
                            109 ;src/main.c:80: while (--size) {
   403E DD 5E 04      [19]  110 	ld	e,4 (ix)
   4041 DD 56 05      [19]  111 	ld	d,5 (ix)
   4044 DD 7E 06      [19]  112 	ld	a, 6 (ix)
   4047 DD 77 FF      [19]  113 	ld	-1 (ix), a
   404A                     114 00101$:
   404A DD 35 FF      [23]  115 	dec	-1 (ix)
                            116 ;src/main.c:84: *sprite = ((*sprite & 0b01010101) << 1) | ((*(next_byte) & 0b10101010) >> 1);
   404D 1A            [ 7]  117 	ld	a, (de)
   404E E6 55         [ 7]  118 	and	a, #0x55
   4050 87            [ 4]  119 	add	a, a
   4051 DD 77 FE      [19]  120 	ld	-2 (ix), a
                            121 ;src/main.c:80: while (--size) {
   4054 DD 7E FF      [19]  122 	ld	a, -1 (ix)
   4057 B7            [ 4]  123 	or	a, a
   4058 28 0D         [12]  124 	jr	Z,00103$
                            125 ;src/main.c:84: *sprite = ((*sprite & 0b01010101) << 1) | ((*(next_byte) & 0b10101010) >> 1);
   405A 0A            [ 7]  126 	ld	a, (bc)
   405B E6 AA         [ 7]  127 	and	a, #0xaa
   405D CB 3F         [ 8]  128 	srl	a
   405F DD B6 FE      [19]  129 	or	a, -2 (ix)
   4062 12            [ 7]  130 	ld	(de), a
                            131 ;src/main.c:85: ++sprite; ++next_byte;
   4063 13            [ 6]  132 	inc	de
   4064 03            [ 6]  133 	inc	bc
   4065 18 E3         [12]  134 	jr	00101$
   4067                     135 00103$:
                            136 ;src/main.c:89: *sprite = (*sprite & 0b01010101) << 1;
   4067 DD 7E FE      [19]  137 	ld	a, -2 (ix)
   406A 12            [ 7]  138 	ld	(de), a
   406B DD F9         [10]  139 	ld	sp, ix
   406D DD E1         [14]  140 	pop	ix
   406F C9            [10]  141 	ret
                            142 ;src/main.c:95: void shiftSprite(TEntity *e) {
                            143 ;	---------------------------------
                            144 ; Function shiftSprite
                            145 ; ---------------------------------
   4070                     146 _shiftSprite::
   4070 DD E5         [15]  147 	push	ix
   4072 DD 21 00 00   [14]  148 	ld	ix,#0
   4076 DD 39         [15]  149 	add	ix,sp
   4078 F5            [11]  150 	push	af
                            151 ;src/main.c:98: if (e->shift == ON_EVEN_PIXEL) {     
   4079 DD 5E 04      [19]  152 	ld	e,4 (ix)
   407C DD 56 05      [19]  153 	ld	d,5 (ix)
   407F 21 08 00      [10]  154 	ld	hl, #0x0008
   4082 19            [11]  155 	add	hl,de
   4083 E3            [19]  156 	ex	(sp), hl
   4084 E1            [10]  157 	pop	hl
   4085 E5            [11]  158 	push	hl
   4086 4E            [ 7]  159 	ld	c, (hl)
                            160 ;src/main.c:100: shiftSpritePixelsRight(e->sprite, e->w * e->h);
   4087 6B            [ 4]  161 	ld	l, e
   4088 62            [ 4]  162 	ld	h, d
   4089 D5            [11]  163 	push	de
   408A FD E1         [14]  164 	pop	iy
   408C 23            [ 6]  165 	inc	hl
   408D 23            [ 6]  166 	inc	hl
   408E 23            [ 6]  167 	inc	hl
   408F 23            [ 6]  168 	inc	hl
   4090 46            [ 7]  169 	ld	b, (hl)
   4091 FD 7E 05      [19]  170 	ld	a, 5 (iy)
   4094 EB            [ 4]  171 	ex	de,hl
   4095 11 06 00      [10]  172 	ld	de, #0x0006
   4098 19            [11]  173 	add	hl, de
   4099 5E            [ 7]  174 	ld	e, (hl)
   409A 23            [ 6]  175 	inc	hl
   409B 56            [ 7]  176 	ld	d, (hl)
   409C D5            [11]  177 	push	de
   409D 5F            [ 4]  178 	ld	e, a
   409E 60            [ 4]  179 	ld	h, b
   409F 2E 00         [ 7]  180 	ld	l, #0x00
   40A1 55            [ 4]  181 	ld	d, l
   40A2 06 08         [ 7]  182 	ld	b, #0x08
   40A4                     183 00110$:
   40A4 29            [11]  184 	add	hl, hl
   40A5 30 01         [12]  185 	jr	NC,00111$
   40A7 19            [11]  186 	add	hl, de
   40A8                     187 00111$:
   40A8 10 FA         [13]  188 	djnz	00110$
   40AA D1            [10]  189 	pop	de
   40AB 45            [ 4]  190 	ld	b, l
                            191 ;src/main.c:98: if (e->shift == ON_EVEN_PIXEL) {     
   40AC 79            [ 4]  192 	ld	a, c
   40AD B7            [ 4]  193 	or	a, a
   40AE 20 0E         [12]  194 	jr	NZ,00102$
                            195 ;src/main.c:100: shiftSpritePixelsRight(e->sprite, e->w * e->h);
   40B0 C5            [11]  196 	push	bc
   40B1 33            [ 6]  197 	inc	sp
   40B2 D5            [11]  198 	push	de
   40B3 CD 00 40      [17]  199 	call	_shiftSpritePixelsRight
   40B6 F1            [10]  200 	pop	af
   40B7 33            [ 6]  201 	inc	sp
                            202 ;src/main.c:101: e->shift = ON_ODD_PIXEL;
   40B8 E1            [10]  203 	pop	hl
   40B9 E5            [11]  204 	push	hl
   40BA 36 01         [10]  205 	ld	(hl), #0x01
   40BC 18 0C         [12]  206 	jr	00104$
   40BE                     207 00102$:
                            208 ;src/main.c:104: shiftSpritePixelsLeft(e->sprite, e->w * e->h);
   40BE C5            [11]  209 	push	bc
   40BF 33            [ 6]  210 	inc	sp
   40C0 D5            [11]  211 	push	de
   40C1 CD 2E 40      [17]  212 	call	_shiftSpritePixelsLeft
   40C4 F1            [10]  213 	pop	af
   40C5 33            [ 6]  214 	inc	sp
                            215 ;src/main.c:105: e->shift = ON_EVEN_PIXEL;
   40C6 E1            [10]  216 	pop	hl
   40C7 E5            [11]  217 	push	hl
   40C8 36 00         [10]  218 	ld	(hl), #0x00
   40CA                     219 00104$:
   40CA DD F9         [10]  220 	ld	sp, ix
   40CC DD E1         [14]  221 	pop	ix
   40CE C9            [10]  222 	ret
                            223 ;src/main.c:113: void drawEntity(TEntity *e) {
                            224 ;	---------------------------------
                            225 ; Function drawEntity
                            226 ; ---------------------------------
   40CF                     227 _drawEntity::
   40CF DD E5         [15]  228 	push	ix
   40D1 DD 21 00 00   [14]  229 	ld	ix,#0
   40D5 DD 39         [15]  230 	add	ix,sp
   40D7 21 F4 FF      [10]  231 	ld	hl, #-12
   40DA 39            [11]  232 	add	hl, sp
   40DB F9            [ 6]  233 	ld	sp, hl
                            234 ;src/main.c:119: if (e->shift != (TShiftStatus) e->nx % 2)
   40DC DD 4E 04      [19]  235 	ld	c,4 (ix)
   40DF DD 46 05      [19]  236 	ld	b,5 (ix)
   40E2 C5            [11]  237 	push	bc
   40E3 FD E1         [14]  238 	pop	iy
   40E5 FD 5E 08      [19]  239 	ld	e, 8 (iy)
   40E8 21 02 00      [10]  240 	ld	hl, #0x0002
   40EB 09            [11]  241 	add	hl,bc
   40EC DD 75 FE      [19]  242 	ld	-2 (ix), l
   40EF DD 74 FF      [19]  243 	ld	-1 (ix), h
   40F2 7E            [ 7]  244 	ld	a, (hl)
   40F3 E6 01         [ 7]  245 	and	a, #0x01
   40F5 93            [ 4]  246 	sub	a, e
   40F6 28 07         [12]  247 	jr	Z,00102$
                            248 ;src/main.c:120: shiftSprite(e);
   40F8 C5            [11]  249 	push	bc
   40F9 C5            [11]  250 	push	bc
   40FA CD 70 40      [17]  251 	call	_shiftSprite
   40FD F1            [10]  252 	pop	af
   40FE C1            [10]  253 	pop	bc
   40FF                     254 00102$:
                            255 ;src/main.c:123: cpct_waitVSYNC();
   40FF C5            [11]  256 	push	bc
   4100 CD 0F 45      [17]  257 	call	_cpct_waitVSYNC
   4103 C1            [10]  258 	pop	bc
                            259 ;src/main.c:128: pscr = cpct_getScreenPtr(CPCT_VMEM_START, e->x / PIXELS_PER_BYTE, e->y);
   4104 21 01 00      [10]  260 	ld	hl, #0x0001
   4107 09            [11]  261 	add	hl,bc
   4108 E3            [19]  262 	ex	(sp), hl
   4109 E1            [10]  263 	pop	hl
   410A E5            [11]  264 	push	hl
   410B 56            [ 7]  265 	ld	d, (hl)
   410C 0A            [ 7]  266 	ld	a, (bc)
   410D CB 3F         [ 8]  267 	srl	a
   410F C5            [11]  268 	push	bc
   4110 5F            [ 4]  269 	ld	e, a
   4111 D5            [11]  270 	push	de
   4112 21 00 C0      [10]  271 	ld	hl, #0xc000
   4115 E5            [11]  272 	push	hl
   4116 CD DD 45      [17]  273 	call	_cpct_getScreenPtr
   4119 EB            [ 4]  274 	ex	de,hl
   411A C1            [10]  275 	pop	bc
                            276 ;src/main.c:129: cpct_drawSolidBox(pscr, 0x00, e->w, e->h);
   411B 21 05 00      [10]  277 	ld	hl, #0x0005
   411E 09            [11]  278 	add	hl,bc
   411F DD 75 F6      [19]  279 	ld	-10 (ix), l
   4122 DD 74 F7      [19]  280 	ld	-9 (ix), h
   4125 7E            [ 7]  281 	ld	a, (hl)
   4126 DD 77 FA      [19]  282 	ld	-6 (ix), a
   4129 21 04 00      [10]  283 	ld	hl, #0x0004
   412C 09            [11]  284 	add	hl,bc
   412D DD 75 F8      [19]  285 	ld	-8 (ix), l
   4130 DD 74 F9      [19]  286 	ld	-7 (ix), h
   4133 7E            [ 7]  287 	ld	a, (hl)
   4134 DD 77 FD      [19]  288 	ld	-3 (ix), a
   4137 C5            [11]  289 	push	bc
   4138 DD 66 FA      [19]  290 	ld	h, -6 (ix)
   413B DD 6E FD      [19]  291 	ld	l, -3 (ix)
   413E E5            [11]  292 	push	hl
   413F 21 00 00      [10]  293 	ld	hl, #0x0000
   4142 E5            [11]  294 	push	hl
   4143 D5            [11]  295 	push	de
   4144 CD 35 45      [17]  296 	call	_cpct_drawSolidBox
   4147 C1            [10]  297 	pop	bc
                            298 ;src/main.c:132: pscr = cpct_getScreenPtr(CPCT_VMEM_START, e->nx / PIXELS_PER_BYTE, e->ny);
   4148 21 03 00      [10]  299 	ld	hl, #0x0003
   414B 09            [11]  300 	add	hl,bc
   414C DD 75 FB      [19]  301 	ld	-5 (ix), l
   414F DD 74 FC      [19]  302 	ld	-4 (ix), h
   4152 56            [ 7]  303 	ld	d, (hl)
   4153 DD 6E FE      [19]  304 	ld	l,-2 (ix)
   4156 DD 66 FF      [19]  305 	ld	h,-1 (ix)
   4159 7E            [ 7]  306 	ld	a, (hl)
   415A CB 3F         [ 8]  307 	srl	a
   415C C5            [11]  308 	push	bc
   415D 5F            [ 4]  309 	ld	e, a
   415E D5            [11]  310 	push	de
   415F 21 00 C0      [10]  311 	ld	hl, #0xc000
   4162 E5            [11]  312 	push	hl
   4163 CD DD 45      [17]  313 	call	_cpct_getScreenPtr
   4166 EB            [ 4]  314 	ex	de,hl
   4167 C1            [10]  315 	pop	bc
                            316 ;src/main.c:133: cpct_drawSprite(e->sprite, pscr, e->w, e->h);
   4168 DD 6E F6      [19]  317 	ld	l,-10 (ix)
   416B DD 66 F7      [19]  318 	ld	h,-9 (ix)
   416E 7E            [ 7]  319 	ld	a, (hl)
   416F DD 77 FD      [19]  320 	ld	-3 (ix), a
   4172 DD 6E F8      [19]  321 	ld	l,-8 (ix)
   4175 DD 66 F9      [19]  322 	ld	h,-7 (ix)
   4178 7E            [ 7]  323 	ld	a, (hl)
   4179 DD 77 F8      [19]  324 	ld	-8 (ix), a
   417C D5            [11]  325 	push	de
   417D FD E1         [14]  326 	pop	iy
   417F 69            [ 4]  327 	ld	l, c
   4180 60            [ 4]  328 	ld	h, b
   4181 11 06 00      [10]  329 	ld	de, #0x0006
   4184 19            [11]  330 	add	hl, de
   4185 5E            [ 7]  331 	ld	e, (hl)
   4186 23            [ 6]  332 	inc	hl
   4187 56            [ 7]  333 	ld	d, (hl)
   4188 C5            [11]  334 	push	bc
   4189 DD 66 FD      [19]  335 	ld	h, -3 (ix)
   418C DD 6E F8      [19]  336 	ld	l, -8 (ix)
   418F E5            [11]  337 	push	hl
   4190 FD E5         [15]  338 	push	iy
   4192 D5            [11]  339 	push	de
   4193 CD 15 44      [17]  340 	call	_cpct_drawSprite
   4196 C1            [10]  341 	pop	bc
                            342 ;src/main.c:136: e->x = e->nx;
   4197 DD 6E FE      [19]  343 	ld	l,-2 (ix)
   419A DD 66 FF      [19]  344 	ld	h,-1 (ix)
   419D 7E            [ 7]  345 	ld	a, (hl)
   419E 02            [ 7]  346 	ld	(bc), a
                            347 ;src/main.c:137: e->y = e->ny;
   419F DD 6E FB      [19]  348 	ld	l,-5 (ix)
   41A2 DD 66 FC      [19]  349 	ld	h,-4 (ix)
   41A5 4E            [ 7]  350 	ld	c, (hl)
   41A6 E1            [10]  351 	pop	hl
   41A7 E5            [11]  352 	push	hl
   41A8 71            [ 7]  353 	ld	(hl), c
   41A9 DD F9         [10]  354 	ld	sp, ix
   41AB DD E1         [14]  355 	pop	ix
   41AD C9            [10]  356 	ret
                            357 ;src/main.c:143: void checkUserInput(TEntity *e) {
                            358 ;	---------------------------------
                            359 ; Function checkUserInput
                            360 ; ---------------------------------
   41AE                     361 _checkUserInput::
   41AE DD E5         [15]  362 	push	ix
   41B0 DD 21 00 00   [14]  363 	ld	ix,#0
   41B4 DD 39         [15]  364 	add	ix,sp
   41B6 F5            [11]  365 	push	af
   41B7 3B            [ 6]  366 	dec	sp
                            367 ;src/main.c:144: cpct_scanKeyboard_f();
   41B8 CD 9F 43      [17]  368 	call	_cpct_scanKeyboard_f
                            369 ;src/main.c:148: if (cpct_isKeyPressed(Key_CursorLeft) && e->nx > 0) {
   41BB 21 01 01      [10]  370 	ld	hl, #0x0101
   41BE CD 93 43      [17]  371 	call	_cpct_isKeyPressed
   41C1 DD 7E 04      [19]  372 	ld	a, 4 (ix)
   41C4 DD 77 FE      [19]  373 	ld	-2 (ix), a
   41C7 DD 7E 05      [19]  374 	ld	a, 5 (ix)
   41CA DD 77 FF      [19]  375 	ld	-1 (ix), a
   41CD DD 4E FE      [19]  376 	ld	c,-2 (ix)
   41D0 DD 46 FF      [19]  377 	ld	b,-1 (ix)
   41D3 03            [ 6]  378 	inc	bc
   41D4 03            [ 6]  379 	inc	bc
   41D5 7D            [ 4]  380 	ld	a, l
   41D6 B7            [ 4]  381 	or	a, a
   41D7 28 09         [12]  382 	jr	Z,00105$
   41D9 0A            [ 7]  383 	ld	a, (bc)
   41DA B7            [ 4]  384 	or	a, a
   41DB 28 05         [12]  385 	jr	Z,00105$
                            386 ;src/main.c:149: e->nx--;
   41DD C6 FF         [ 7]  387 	add	a, #0xff
   41DF 02            [ 7]  388 	ld	(bc), a
   41E0 18 34         [12]  389 	jr	00106$
   41E2                     390 00105$:
                            391 ;src/main.c:150: } else if (cpct_isKeyPressed(Key_CursorRight) && e->nx + e->w*PIXELS_PER_BYTE < SCR_WIDTH_PIXELS) {
   41E2 C5            [11]  392 	push	bc
   41E3 21 00 02      [10]  393 	ld	hl, #0x0200
   41E6 CD 93 43      [17]  394 	call	_cpct_isKeyPressed
   41E9 C1            [10]  395 	pop	bc
   41EA 7D            [ 4]  396 	ld	a, l
   41EB B7            [ 4]  397 	or	a, a
   41EC 28 28         [12]  398 	jr	Z,00106$
   41EE 0A            [ 7]  399 	ld	a, (bc)
   41EF DD 77 FD      [19]  400 	ld	-3 (ix), a
   41F2 5F            [ 4]  401 	ld	e, a
   41F3 16 00         [ 7]  402 	ld	d, #0x00
   41F5 DD 6E FE      [19]  403 	ld	l,-2 (ix)
   41F8 DD 66 FF      [19]  404 	ld	h,-1 (ix)
   41FB 23            [ 6]  405 	inc	hl
   41FC 23            [ 6]  406 	inc	hl
   41FD 23            [ 6]  407 	inc	hl
   41FE 23            [ 6]  408 	inc	hl
   41FF 6E            [ 7]  409 	ld	l, (hl)
   4200 26 00         [ 7]  410 	ld	h, #0x00
   4202 29            [11]  411 	add	hl, hl
   4203 19            [11]  412 	add	hl, de
   4204 11 A0 80      [10]  413 	ld	de, #0x80a0
   4207 29            [11]  414 	add	hl, hl
   4208 3F            [ 4]  415 	ccf
   4209 CB 1C         [ 8]  416 	rr	h
   420B CB 1D         [ 8]  417 	rr	l
   420D ED 52         [15]  418 	sbc	hl, de
   420F 30 05         [12]  419 	jr	NC,00106$
                            420 ;src/main.c:151: e->nx++;
   4211 DD 7E FD      [19]  421 	ld	a, -3 (ix)
   4214 3C            [ 4]  422 	inc	a
   4215 02            [ 7]  423 	ld	(bc), a
   4216                     424 00106$:
                            425 ;src/main.c:153: if (cpct_isKeyPressed(Key_CursorUp) && e->ny > 0) {
   4216 21 00 01      [10]  426 	ld	hl, #0x0100
   4219 CD 93 43      [17]  427 	call	_cpct_isKeyPressed
   421C DD 4E FE      [19]  428 	ld	c,-2 (ix)
   421F DD 46 FF      [19]  429 	ld	b,-1 (ix)
   4222 03            [ 6]  430 	inc	bc
   4223 03            [ 6]  431 	inc	bc
   4224 03            [ 6]  432 	inc	bc
   4225 7D            [ 4]  433 	ld	a, l
   4226 B7            [ 4]  434 	or	a, a
   4227 28 09         [12]  435 	jr	Z,00112$
   4229 0A            [ 7]  436 	ld	a, (bc)
   422A B7            [ 4]  437 	or	a, a
   422B 28 05         [12]  438 	jr	Z,00112$
                            439 ;src/main.c:154: e->ny--;
   422D C6 FF         [ 7]  440 	add	a, #0xff
   422F 02            [ 7]  441 	ld	(bc), a
   4230 18 34         [12]  442 	jr	00115$
   4232                     443 00112$:
                            444 ;src/main.c:155: } else if (cpct_isKeyPressed(Key_CursorDown) && e->ny + e->h < SCR_HEIGHT_PIXELS) {
   4232 C5            [11]  445 	push	bc
   4233 21 00 04      [10]  446 	ld	hl, #0x0400
   4236 CD 93 43      [17]  447 	call	_cpct_isKeyPressed
   4239 C1            [10]  448 	pop	bc
   423A 7D            [ 4]  449 	ld	a, l
   423B B7            [ 4]  450 	or	a, a
   423C 28 28         [12]  451 	jr	Z,00115$
   423E 0A            [ 7]  452 	ld	a, (bc)
   423F DD 77 FD      [19]  453 	ld	-3 (ix), a
   4242 5F            [ 4]  454 	ld	e, a
   4243 16 00         [ 7]  455 	ld	d, #0x00
   4245 DD 6E FE      [19]  456 	ld	l,-2 (ix)
   4248 DD 66 FF      [19]  457 	ld	h,-1 (ix)
   424B 23            [ 6]  458 	inc	hl
   424C 23            [ 6]  459 	inc	hl
   424D 23            [ 6]  460 	inc	hl
   424E 23            [ 6]  461 	inc	hl
   424F 23            [ 6]  462 	inc	hl
   4250 6E            [ 7]  463 	ld	l, (hl)
   4251 26 00         [ 7]  464 	ld	h, #0x00
   4253 19            [11]  465 	add	hl, de
   4254 11 C8 80      [10]  466 	ld	de, #0x80c8
   4257 29            [11]  467 	add	hl, hl
   4258 3F            [ 4]  468 	ccf
   4259 CB 1C         [ 8]  469 	rr	h
   425B CB 1D         [ 8]  470 	rr	l
   425D ED 52         [15]  471 	sbc	hl, de
   425F 30 05         [12]  472 	jr	NC,00115$
                            473 ;src/main.c:156: e->ny++;
   4261 DD 7E FD      [19]  474 	ld	a, -3 (ix)
   4264 3C            [ 4]  475 	inc	a
   4265 02            [ 7]  476 	ld	(bc), a
   4266                     477 00115$:
   4266 DD F9         [10]  478 	ld	sp, ix
   4268 DD E1         [14]  479 	pop	ix
   426A C9            [10]  480 	ret
                            481 ;src/main.c:163: void main(void) {
                            482 ;	---------------------------------
                            483 ; Function main
                            484 ; ---------------------------------
   426B                     485 _main::
                            486 ;src/main.c:175: TEntity* e = (void*)&ec;// And then we create a non-const pointer to modify the data
   426B 01 AE 42      [10]  487 	ld	bc, #_main_ec_1_147+0
                            488 ;src/main.c:178: cpct_disableFirmware();          // Firmware must be disabled
   426E C5            [11]  489 	push	bc
   426F CD 25 45      [17]  490 	call	_cpct_disableFirmware
   4272 2E 00         [ 7]  491 	ld	l, #0x00
   4274 CD 17 45      [17]  492 	call	_cpct_setVideoMode
   4277 21 05 00      [10]  493 	ld	hl, #0x0005
   427A E5            [11]  494 	push	hl
   427B 21 B7 42      [10]  495 	ld	hl, #_g_palette
   427E E5            [11]  496 	push	hl
   427F CD 7C 43      [17]  497 	call	_cpct_setPalette
   4282 C1            [10]  498 	pop	bc
                            499 ;src/main.c:181: cpct_setBorder(g_palette[0]);    // Set the border to the background colour (colour 0)
   4283 21 B7 42      [10]  500 	ld	hl, #_g_palette + 0
   4286 56            [ 7]  501 	ld	d, (hl)
   4287 C5            [11]  502 	push	bc
   4288 1E 10         [ 7]  503 	ld	e, #0x10
   428A D5            [11]  504 	push	de
   428B CD 09 44      [17]  505 	call	_cpct_setPALColour
   428E 21 00 40      [10]  506 	ld	hl, #0x4000
   4291 E5            [11]  507 	push	hl
   4292 21 55 55      [10]  508 	ld	hl, #0x5555
   4295 E5            [11]  509 	push	hl
   4296 21 00 C0      [10]  510 	ld	hl, #0xc000
   4299 E5            [11]  511 	push	hl
   429A CD C4 44      [17]  512 	call	_cpct_memset_f64
   429D C1            [10]  513 	pop	bc
                            514 ;src/main.c:185: while (1) {
   429E                     515 00102$:
                            516 ;src/main.c:186: checkUserInput(e);  // Get user input and perform actions
   429E C5            [11]  517 	push	bc
   429F C5            [11]  518 	push	bc
   42A0 CD AE 41      [17]  519 	call	_checkUserInput
   42A3 F1            [10]  520 	pop	af
   42A4 C1            [10]  521 	pop	bc
                            522 ;src/main.c:187: drawEntity(e);      // Draw the entity at its new location on screen
   42A5 C5            [11]  523 	push	bc
   42A6 C5            [11]  524 	push	bc
   42A7 CD CF 40      [17]  525 	call	_drawEntity
   42AA F1            [10]  526 	pop	af
   42AB C1            [10]  527 	pop	bc
   42AC 18 F0         [12]  528 	jr	00102$
   42AE                     529 _main_ec_1_147:
   42AE 20                  530 	.db #0x20	; 32
   42AF 58                  531 	.db #0x58	; 88	'X'
   42B0 20                  532 	.db #0x20	; 32
   42B1 58                  533 	.db #0x58	; 88	'X'
   42B2 08                  534 	.db #0x08	; 8
   42B3 18                  535 	.db #0x18	; 24
   42B4 BC 42               536 	.dw _g_character
   42B6 00                  537 	.db #0x00	; 0
                            538 	.area _CODE
                            539 	.area _INITIALIZER
                            540 	.area _CABS (ABS)
