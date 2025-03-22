                              1 ;--------------------------------------------------------
                              2 ; File Created by SDCC : free open source ANSI-C Compiler
                              3 ; Version 3.6.8 #9946 (Linux)
                              4 ;--------------------------------------------------------
                              5 	.module entities
                              6 	.optsdcc -mz80
                              7 	
                              8 ;--------------------------------------------------------
                              9 ; Public variables in this module
                             10 ;--------------------------------------------------------
                             11 	.globl _updateAnimation
                             12 	.globl _cpct_getScreenPtr
                             13 	.globl _cpct_drawSprite
                             14 	.globl _cpct_drawSolidBox
                             15 	.globl _g_SCR_HEIGHT
                             16 	.globl _g_SCR_WIDTH
                             17 	.globl _g_persea
                             18 	.globl _g_perseaAnimation
                             19 	.globl _g_animDie
                             20 	.globl _g_animWin
                             21 	.globl _g_animHit
                             22 	.globl _g_animKick
                             23 	.globl _g_animFist
                             24 	.globl _g_animWalkLeft
                             25 	.globl _g_animWalkRight
                             26 	.globl _g_animStay
                             27 	.globl _g_allAnimFrames
                             28 	.globl _getPersea
                             29 	.globl _moveEntityX
                             30 	.globl _moveEntityY
                             31 	.globl _updateEntity
                             32 	.globl _setAnimation
                             33 	.globl _drawEntity
                             34 ;--------------------------------------------------------
                             35 ; special function registers
                             36 ;--------------------------------------------------------
                             37 ;--------------------------------------------------------
                             38 ; ram data
                             39 ;--------------------------------------------------------
                             40 	.area _DATA
                             41 ;--------------------------------------------------------
                             42 ; ram data
                             43 ;--------------------------------------------------------
                             44 	.area _INITIALIZED
                             45 ;--------------------------------------------------------
                             46 ; absolute external ram data
                             47 ;--------------------------------------------------------
                             48 	.area _DABS (ABS)
                             49 ;--------------------------------------------------------
                             50 ; global & static initialisations
                             51 ;--------------------------------------------------------
                             52 	.area _HOME
                             53 	.area _GSINIT
                             54 	.area _GSFINAL
                             55 	.area _GSINIT
                             56 ;--------------------------------------------------------
                             57 ; Home
                             58 ;--------------------------------------------------------
                             59 	.area _HOME
                             60 	.area _HOME
                             61 ;--------------------------------------------------------
                             62 ; code
                             63 ;--------------------------------------------------------
                             64 	.area _CODE
                             65 ;src/entities/entities.c:102: TEntity* getPersea() {
                             66 ;	---------------------------------
                             67 ; Function getPersea
                             68 ; ---------------------------------
   023A                      69 _getPersea::
                             70 ;src/entities/entities.c:103: return (TEntity*)g_persea;
   023A 21 05 03      [10]   71 	ld	hl, #_g_persea+0
   023D C9            [10]   72 	ret
   023E                      73 _g_allAnimFrames:
   023E E8 0D                74 	.dw _gc_PerseaWalk2
   0240 08                   75 	.db #0x08	; 8
   0241 18                   76 	.db #0x18	; 24
   0242 02                   77 	.db #0x02	;  2
   0243 00                   78 	.db #0x00	;  0
   0244 00                   79 	.db #0x00	;  0
   0245 00                   80 	.db #0x00	;  0
   0246 00                   81 	.db #0x00	;  0
   0247 04                   82 	.db #0x04	; 4
   0248 28 0D                83 	.dw _gc_PerseaWalk13
   024A 08                   84 	.db #0x08	; 8
   024B 18                   85 	.db #0x18	; 24
   024C 02                   86 	.db #0x02	;  2
   024D 00                   87 	.db #0x00	;  0
   024E 00                   88 	.db #0x00	;  0
   024F 03                   89 	.db #0x03	;  3
   0250 18                   90 	.db #0x18	;  24
   0251 04                   91 	.db #0x04	; 4
   0252 A8 0E                92 	.dw _gc_PerseaWalk4
   0254 08                   93 	.db #0x08	; 8
   0255 18                   94 	.db #0x18	; 24
   0256 02                   95 	.db #0x02	;  2
   0257 00                   96 	.db #0x00	;  0
   0258 00                   97 	.db #0x00	;  0
   0259 00                   98 	.db #0x00	;  0
   025A 00                   99 	.db #0x00	;  0
   025B 04                  100 	.db #0x04	; 4
   025C A8 0E               101 	.dw _gc_PerseaWalk4
   025E 08                  102 	.db #0x08	; 8
   025F 18                  103 	.db #0x18	; 24
   0260 FE                  104 	.db #0xfe	; -2
   0261 00                  105 	.db #0x00	;  0
   0262 00                  106 	.db #0x00	;  0
   0263 00                  107 	.db #0x00	;  0
   0264 00                  108 	.db #0x00	;  0
   0265 04                  109 	.db #0x04	; 4
   0266 28 0D               110 	.dw _gc_PerseaWalk13
   0268 08                  111 	.db #0x08	; 8
   0269 18                  112 	.db #0x18	; 24
   026A FE                  113 	.db #0xfe	; -2
   026B 00                  114 	.db #0x00	;  0
   026C 06                  115 	.db #0x06	;  6
   026D 03                  116 	.db #0x03	;  3
   026E 18                  117 	.db #0x18	;  24
   026F 04                  118 	.db #0x04	; 4
   0270 E8 0D               119 	.dw _gc_PerseaWalk2
   0272 08                  120 	.db #0x08	; 8
   0273 18                  121 	.db #0x18	; 24
   0274 FE                  122 	.db #0xfe	; -2
   0275 00                  123 	.db #0x00	;  0
   0276 00                  124 	.db #0x00	;  0
   0277 00                  125 	.db #0x00	;  0
   0278 00                  126 	.db #0x00	;  0
   0279 04                  127 	.db #0x04	; 4
   027A 68 0F               128 	.dw _gc_PerseaFist
   027C 09                  129 	.db #0x09	; 9
   027D 18                  130 	.db #0x18	; 24
   027E 00                  131 	.db #0x00	;  0
   027F 00                  132 	.db #0x00	;  0
   0280 06                  133 	.db #0x06	;  6
   0281 03                  134 	.db #0x03	;  3
   0282 06                  135 	.db #0x06	;  6
   0283 0F                  136 	.db #0x0f	; 15
   0284 40 10               137 	.dw _gc_PerseaKick
   0286 09                  138 	.db #0x09	; 9
   0287 18                  139 	.db #0x18	; 24
   0288 00                  140 	.db #0x00	;  0
   0289 00                  141 	.db #0x00	;  0
   028A 06                  142 	.db #0x06	;  6
   028B 03                  143 	.db #0x03	;  3
   028C 0C                  144 	.db #0x0c	;  12
   028D 19                  145 	.db #0x19	; 25
   028E 18 11               146 	.dw _gc_PerseaHit
   0290 08                  147 	.db #0x08	; 8
   0291 18                  148 	.db #0x18	; 24
   0292 00                  149 	.db #0x00	;  0
   0293 00                  150 	.db #0x00	;  0
   0294 00                  151 	.db #0x00	;  0
   0295 00                  152 	.db #0x00	;  0
   0296 00                  153 	.db #0x00	;  0
   0297 19                  154 	.db #0x19	; 25
   0298 98 12               155 	.dw _gc_PerseaKO
   029A 0C                  156 	.db #0x0c	; 12
   029B 08                  157 	.db #0x08	; 8
   029C FC                  158 	.db #0xfc	; -4
   029D 10                  159 	.db #0x10	;  16
   029E 02                  160 	.db #0x02	;  2
   029F 04                  161 	.db #0x04	;  4
   02A0 10                  162 	.db #0x10	;  16
   02A1 32                  163 	.db #0x32	; 50	'2'
   02A2 D8 11               164 	.dw _gc_PerseaWins
   02A4 08                  165 	.db #0x08	; 8
   02A5 18                  166 	.db #0x18	; 24
   02A6 00                  167 	.db #0x00	;  0
   02A7 00                  168 	.db #0x00	;  0
   02A8 00                  169 	.db #0x00	;  0
   02A9 00                  170 	.db #0x00	;  0
   02AA 00                  171 	.db #0x00	;  0
   02AB 32                  172 	.db #0x32	; 50	'2'
   02AC 28 0D               173 	.dw _gc_PerseaWalk13
   02AE 08                  174 	.db #0x08	; 8
   02AF 18                  175 	.db #0x18	; 24
   02B0 00                  176 	.db #0x00	;  0
   02B1 00                  177 	.db #0x00	;  0
   02B2 06                  178 	.db #0x06	;  6
   02B3 03                  179 	.db #0x03	;  3
   02B4 18                  180 	.db #0x18	;  24
   02B5 01                  181 	.db #0x01	; 1
   02B6 28 0D               182 	.dw _gc_PerseaWalk13
   02B8 08                  183 	.db #0x08	; 8
   02B9 18                  184 	.db #0x18	; 24
   02BA 00                  185 	.db #0x00	;  0
   02BB 00                  186 	.db #0x00	;  0
   02BC 00                  187 	.db #0x00	;  0
   02BD 00                  188 	.db #0x00	;  0
   02BE 00                  189 	.db #0x00	;  0
   02BF 01                  190 	.db #0x01	; 1
   02C0 28 0D               191 	.dw _gc_PerseaWalk13
   02C2 08                  192 	.db #0x08	; 8
   02C3 18                  193 	.db #0x18	; 24
   02C4 04                  194 	.db #0x04	;  4
   02C5 F0                  195 	.db #0xf0	; -16
   02C6 00                  196 	.db #0x00	;  0
   02C7 0C                  197 	.db #0x0c	;  12
   02C8 08                  198 	.db #0x08	;  8
   02C9 01                  199 	.db #0x01	; 1
   02CA                     200 _g_animStay:
   02CA 66 02               201 	.dw (_g_allAnimFrames + 40)
   02CC 00 00               202 	.dw #0x0000
   02CE                     203 _g_animWalkRight:
   02CE 3E 02               204 	.dw (_g_allAnimFrames + 0)
   02D0 48 02               205 	.dw (_g_allAnimFrames + 10)
   02D2 52 02               206 	.dw (_g_allAnimFrames + 20)
   02D4 48 02               207 	.dw (_g_allAnimFrames + 10)
   02D6 00 00               208 	.dw #0x0000
   02D8                     209 _g_animWalkLeft:
   02D8 5C 02               210 	.dw (_g_allAnimFrames + 30)
   02DA 66 02               211 	.dw (_g_allAnimFrames + 40)
   02DC 70 02               212 	.dw (_g_allAnimFrames + 50)
   02DE 66 02               213 	.dw (_g_allAnimFrames + 40)
   02E0 00 00               214 	.dw #0x0000
   02E2                     215 _g_animFist:
   02E2 7A 02               216 	.dw (_g_allAnimFrames + 60)
   02E4 AC 02               217 	.dw (_g_allAnimFrames + 110)
   02E6 00 00               218 	.dw #0x0000
   02E8                     219 _g_animKick:
   02E8 84 02               220 	.dw (_g_allAnimFrames + 70)
   02EA AC 02               221 	.dw (_g_allAnimFrames + 110)
   02EC 00 00               222 	.dw #0x0000
   02EE                     223 _g_animHit:
   02EE 8E 02               224 	.dw (_g_allAnimFrames + 80)
   02F0 B6 02               225 	.dw (_g_allAnimFrames + 120)
   02F2 00 00               226 	.dw #0x0000
   02F4                     227 _g_animWin:
   02F4 A2 02               228 	.dw (_g_allAnimFrames + 100)
   02F6 AC 02               229 	.dw (_g_allAnimFrames + 110)
   02F8 00 00               230 	.dw #0x0000
   02FA                     231 _g_animDie:
   02FA 98 02               232 	.dw (_g_allAnimFrames + 90)
   02FC C0 02               233 	.dw (_g_allAnimFrames + 130)
   02FE 00 00               234 	.dw #0x0000
   0300                     235 _g_perseaAnimation:
   0300 CA 02               236 	.dw _g_animStay
   0302 00                  237 	.db #0x00	; 0
   0303 00                  238 	.db #0x00	; 0
   0304 03                  239 	.db #0x03	; 3
   0305                     240 _g_persea:
   0305 00 03               241 	.dw _g_perseaAnimation
   0307 D0 C2               242 	.dw #0xc2d0
   0309 00                  243 	.db #0x00	; 0
   030A 48                  244 	.db #0x48	; 72	'H'
   030B 01                  245 	.db #0x01	; 1
   030C                     246 _g_SCR_WIDTH:
   030C 50                  247 	.db #0x50	; 80	'P'
   030D                     248 _g_SCR_HEIGHT:
   030D C8                  249 	.db #0xc8	; 200
                            250 ;src/entities/entities.c:113: i8 moveEntityX (TEntity* ent, i8 mx) {
                            251 ;	---------------------------------
                            252 ; Function moveEntityX
                            253 ; ---------------------------------
   030E                     254 _moveEntityX::
   030E DD E5         [15]  255 	push	ix
   0310 DD 21 00 00   [14]  256 	ld	ix,#0
   0314 DD 39         [15]  257 	add	ix,sp
   0316 21 F1 FF      [10]  258 	ld	hl, #-15
   0319 39            [11]  259 	add	hl, sp
   031A F9            [ 6]  260 	ld	sp, hl
                            261 ;src/entities/entities.c:114: u8 moved = 0;// Tells us how many bytes the entity has moved
   031B DD 36 FF 00   [19]  262 	ld	-1 (ix), #0x00
                            263 ;src/entities/entities.c:122: if (umx <= ent->x) {
   031F DD 7E 04      [19]  264 	ld	a, 4 (ix)
   0322 DD 77 F1      [19]  265 	ld	-15 (ix), a
   0325 DD 7E 05      [19]  266 	ld	a, 5 (ix)
   0328 DD 77 F2      [19]  267 	ld	-14 (ix), a
                            268 ;src/entities/entities.c:124: ent->videopos -= umx;
   032B DD 7E F1      [19]  269 	ld	a, -15 (ix)
   032E C6 02         [ 7]  270 	add	a, #0x02
   0330 DD 77 F7      [19]  271 	ld	-9 (ix), a
   0333 DD 7E F2      [19]  272 	ld	a, -14 (ix)
   0336 CE 00         [ 7]  273 	adc	a, #0x00
   0338 DD 77 F8      [19]  274 	ld	-8 (ix), a
                            275 ;src/entities/entities.c:125: moved          = mx;
   033B DD 7E 06      [19]  276 	ld	a, 6 (ix)
   033E DD 77 F6      [19]  277 	ld	-10 (ix), a
                            278 ;src/entities/entities.c:122: if (umx <= ent->x) {
   0341 DD 7E F1      [19]  279 	ld	a, -15 (ix)
   0344 C6 04         [ 7]  280 	add	a, #0x04
   0346 DD 77 F4      [19]  281 	ld	-12 (ix), a
   0349 DD 7E F2      [19]  282 	ld	a, -14 (ix)
   034C CE 00         [ 7]  283 	adc	a, #0x00
   034E DD 77 F5      [19]  284 	ld	-11 (ix), a
                            285 ;src/entities/entities.c:118: if (mx < 0) {
   0351 DD CB 06 7E   [20]  286 	bit	7, 6 (ix)
   0355 CA FF 03      [10]  287 	jp	Z, 00114$
                            288 ;src/entities/entities.c:119: umx = -mx;   // umx = positive value of mx, that is negative
   0358 AF            [ 4]  289 	xor	a, a
   0359 DD 96 06      [19]  290 	sub	a, 6 (ix)
   035C DD 77 F3      [19]  291 	ld	-13 (ix), a
                            292 ;src/entities/entities.c:122: if (umx <= ent->x) {
   035F DD 6E F4      [19]  293 	ld	l,-12 (ix)
   0362 DD 66 F5      [19]  294 	ld	h,-11 (ix)
   0365 7E            [ 7]  295 	ld	a, (hl)
   0366 DD 77 FE      [19]  296 	ld	-2 (ix), a
   0369 DD 96 F3      [19]  297 	sub	a, -13 (ix)
   036C 38 56         [12]  298 	jr	C,00104$
                            299 ;src/entities/entities.c:123: ent->x        -= umx;
   036E DD 7E FE      [19]  300 	ld	a, -2 (ix)
   0371 DD 96 F3      [19]  301 	sub	a, -13 (ix)
   0374 DD 77 FD      [19]  302 	ld	-3 (ix), a
   0377 DD 6E F4      [19]  303 	ld	l,-12 (ix)
   037A DD 66 F5      [19]  304 	ld	h,-11 (ix)
   037D DD 7E FD      [19]  305 	ld	a, -3 (ix)
   0380 77            [ 7]  306 	ld	(hl), a
                            307 ;src/entities/entities.c:124: ent->videopos -= umx;
   0381 DD 6E F7      [19]  308 	ld	l,-9 (ix)
   0384 DD 66 F8      [19]  309 	ld	h,-8 (ix)
   0387 7E            [ 7]  310 	ld	a, (hl)
   0388 DD 77 FB      [19]  311 	ld	-5 (ix), a
   038B 23            [ 6]  312 	inc	hl
   038C 7E            [ 7]  313 	ld	a, (hl)
   038D DD 77 FC      [19]  314 	ld	-4 (ix), a
   0390 DD 7E F3      [19]  315 	ld	a, -13 (ix)
   0393 DD 77 F9      [19]  316 	ld	-7 (ix), a
   0396 DD 36 FA 00   [19]  317 	ld	-6 (ix), #0x00
   039A DD 7E FB      [19]  318 	ld	a, -5 (ix)
   039D DD 96 F9      [19]  319 	sub	a, -7 (ix)
   03A0 DD 77 F9      [19]  320 	ld	-7 (ix), a
   03A3 DD 7E FC      [19]  321 	ld	a, -4 (ix)
   03A6 DD 9E FA      [19]  322 	sbc	a, -6 (ix)
   03A9 DD 77 FA      [19]  323 	ld	-6 (ix), a
   03AC DD 6E F7      [19]  324 	ld	l,-9 (ix)
   03AF DD 66 F8      [19]  325 	ld	h,-8 (ix)
   03B2 DD 7E F9      [19]  326 	ld	a, -7 (ix)
   03B5 77            [ 7]  327 	ld	(hl), a
   03B6 23            [ 6]  328 	inc	hl
   03B7 DD 7E FA      [19]  329 	ld	a, -6 (ix)
   03BA 77            [ 7]  330 	ld	(hl), a
                            331 ;src/entities/entities.c:125: moved          = mx;
   03BB DD 7E F6      [19]  332 	ld	a, -10 (ix)
   03BE DD 77 FF      [19]  333 	ld	-1 (ix), a
   03C1 C3 8A 04      [10]  334 	jp	00115$
   03C4                     335 00104$:
                            336 ;src/entities/entities.c:126: } else if (ent->x) {
   03C4 DD 7E FE      [19]  337 	ld	a, -2 (ix)
   03C7 B7            [ 4]  338 	or	a, a
   03C8 CA 8A 04      [10]  339 	jp	Z, 00115$
                            340 ;src/entities/entities.c:128: ent->videopos -= ent->x;
   03CB DD 6E F7      [19]  341 	ld	l,-9 (ix)
   03CE DD 66 F8      [19]  342 	ld	h,-8 (ix)
   03D1 4E            [ 7]  343 	ld	c, (hl)
   03D2 23            [ 6]  344 	inc	hl
   03D3 46            [ 7]  345 	ld	b, (hl)
   03D4 DD 5E FE      [19]  346 	ld	e, -2 (ix)
   03D7 16 00         [ 7]  347 	ld	d, #0x00
   03D9 79            [ 4]  348 	ld	a, c
   03DA 93            [ 4]  349 	sub	a, e
   03DB 4F            [ 4]  350 	ld	c, a
   03DC 78            [ 4]  351 	ld	a, b
   03DD 9A            [ 4]  352 	sbc	a, d
   03DE 47            [ 4]  353 	ld	b, a
   03DF DD 6E F7      [19]  354 	ld	l,-9 (ix)
   03E2 DD 66 F8      [19]  355 	ld	h,-8 (ix)
   03E5 71            [ 7]  356 	ld	(hl), c
   03E6 23            [ 6]  357 	inc	hl
   03E7 70            [ 7]  358 	ld	(hl), b
                            359 ;src/entities/entities.c:129: moved          = -ent->x;
   03E8 DD 6E F4      [19]  360 	ld	l,-12 (ix)
   03EB DD 66 F5      [19]  361 	ld	h,-11 (ix)
   03EE 4E            [ 7]  362 	ld	c, (hl)
   03EF AF            [ 4]  363 	xor	a, a
   03F0 91            [ 4]  364 	sub	a, c
   03F1 DD 77 FF      [19]  365 	ld	-1 (ix), a
                            366 ;src/entities/entities.c:130: ent->x         = 0;
   03F4 DD 6E F4      [19]  367 	ld	l,-12 (ix)
   03F7 DD 66 F5      [19]  368 	ld	h,-11 (ix)
   03FA 36 00         [10]  369 	ld	(hl), #0x00
   03FC C3 8A 04      [10]  370 	jp	00115$
   03FF                     371 00114$:
                            372 ;src/entities/entities.c:133: } else if (mx) {
   03FF DD 7E 06      [19]  373 	ld	a, 6 (ix)
   0402 B7            [ 4]  374 	or	a, a
   0403 CA 8A 04      [10]  375 	jp	Z, 00115$
                            376 ;src/entities/entities.c:139: anim = ent->anim; 
   0406 E1            [10]  377 	pop	hl
   0407 E5            [11]  378 	push	hl
   0408 7E            [ 7]  379 	ld	a, (hl)
   0409 23            [ 6]  380 	inc	hl
   040A 66            [ 7]  381 	ld	h, (hl)
   040B 6F            [ 4]  382 	ld	l, a
                            383 ;src/entities/entities.c:140: space_left = g_SCR_WIDTH - anim->frames[anim->frame_id]->width - ent->x;
   040C E5            [11]  384 	push	hl
   040D 4E            [ 7]  385 	ld	c, (hl)
   040E 23            [ 6]  386 	inc	hl
   040F 46            [ 7]  387 	ld	b, (hl)
   0410 E1            [10]  388 	pop	hl
   0411 23            [ 6]  389 	inc	hl
   0412 23            [ 6]  390 	inc	hl
   0413 6E            [ 7]  391 	ld	l, (hl)
   0414 26 00         [ 7]  392 	ld	h, #0x00
   0416 29            [11]  393 	add	hl, hl
   0417 09            [11]  394 	add	hl, bc
   0418 7E            [ 7]  395 	ld	a, (hl)
   0419 23            [ 6]  396 	inc	hl
   041A 66            [ 7]  397 	ld	h, (hl)
   041B 6F            [ 4]  398 	ld	l, a
   041C 23            [ 6]  399 	inc	hl
   041D 23            [ 6]  400 	inc	hl
   041E 4E            [ 7]  401 	ld	c, (hl)
   041F 3A 0C 03      [13]  402 	ld	a,(#_g_SCR_WIDTH + 0)
   0422 91            [ 4]  403 	sub	a, c
   0423 4F            [ 4]  404 	ld	c, a
   0424 DD 6E F4      [19]  405 	ld	l,-12 (ix)
   0427 DD 66 F5      [19]  406 	ld	h,-11 (ix)
   042A 46            [ 7]  407 	ld	b, (hl)
   042B 79            [ 4]  408 	ld	a, c
   042C 90            [ 4]  409 	sub	a, b
                            410 ;src/entities/entities.c:144: if (umx <= space_left) {
   042D 4F            [ 4]  411 	ld	c,a
   042E DD 96 F6      [19]  412 	sub	a, -10 (ix)
   0431 38 2E         [12]  413 	jr	C,00109$
                            414 ;src/entities/entities.c:145: ent->x        += umx;
   0433 78            [ 4]  415 	ld	a, b
   0434 DD 86 F6      [19]  416 	add	a, -10 (ix)
   0437 DD 6E F4      [19]  417 	ld	l,-12 (ix)
   043A DD 66 F5      [19]  418 	ld	h,-11 (ix)
   043D 77            [ 7]  419 	ld	(hl), a
                            420 ;src/entities/entities.c:146: ent->videopos += umx;
   043E DD 6E F7      [19]  421 	ld	l,-9 (ix)
   0441 DD 66 F8      [19]  422 	ld	h,-8 (ix)
   0444 4E            [ 7]  423 	ld	c, (hl)
   0445 23            [ 6]  424 	inc	hl
   0446 46            [ 7]  425 	ld	b, (hl)
   0447 79            [ 4]  426 	ld	a, c
   0448 DD 86 F6      [19]  427 	add	a, -10 (ix)
   044B 4F            [ 4]  428 	ld	c, a
   044C 78            [ 4]  429 	ld	a, b
   044D CE 00         [ 7]  430 	adc	a, #0x00
   044F 47            [ 4]  431 	ld	b, a
   0450 DD 6E F7      [19]  432 	ld	l,-9 (ix)
   0453 DD 66 F8      [19]  433 	ld	h,-8 (ix)
   0456 71            [ 7]  434 	ld	(hl), c
   0457 23            [ 6]  435 	inc	hl
   0458 70            [ 7]  436 	ld	(hl), b
                            437 ;src/entities/entities.c:147: moved         = umx;
   0459 DD 7E F6      [19]  438 	ld	a, -10 (ix)
   045C DD 77 FF      [19]  439 	ld	-1 (ix), a
   045F 18 29         [12]  440 	jr	00115$
   0461                     441 00109$:
                            442 ;src/entities/entities.c:148: } else if (space_left) {
   0461 79            [ 4]  443 	ld	a, c
   0462 B7            [ 4]  444 	or	a, a
   0463 28 25         [12]  445 	jr	Z,00115$
                            446 ;src/entities/entities.c:150: ent->x        += space_left;
   0465 78            [ 4]  447 	ld	a, b
   0466 81            [ 4]  448 	add	a, c
   0467 DD 6E F4      [19]  449 	ld	l,-12 (ix)
   046A DD 66 F5      [19]  450 	ld	h,-11 (ix)
   046D 77            [ 7]  451 	ld	(hl), a
                            452 ;src/entities/entities.c:151: ent->videopos += space_left;
   046E DD 6E F7      [19]  453 	ld	l,-9 (ix)
   0471 DD 66 F8      [19]  454 	ld	h,-8 (ix)
   0474 46            [ 7]  455 	ld	b, (hl)
   0475 23            [ 6]  456 	inc	hl
   0476 5E            [ 7]  457 	ld	e, (hl)
   0477 78            [ 4]  458 	ld	a, b
   0478 81            [ 4]  459 	add	a, c
   0479 47            [ 4]  460 	ld	b, a
   047A 7B            [ 4]  461 	ld	a, e
   047B CE 00         [ 7]  462 	adc	a, #0x00
   047D 5F            [ 4]  463 	ld	e, a
   047E DD 6E F7      [19]  464 	ld	l,-9 (ix)
   0481 DD 66 F8      [19]  465 	ld	h,-8 (ix)
   0484 70            [ 7]  466 	ld	(hl), b
   0485 23            [ 6]  467 	inc	hl
   0486 73            [ 7]  468 	ld	(hl), e
                            469 ;src/entities/entities.c:152: moved         = space_left;
   0487 DD 71 FF      [19]  470 	ld	-1 (ix), c
   048A                     471 00115$:
                            472 ;src/entities/entities.c:157: return moved;
   048A DD 6E FF      [19]  473 	ld	l, -1 (ix)
   048D DD F9         [10]  474 	ld	sp, ix
   048F DD E1         [14]  475 	pop	ix
   0491 C9            [10]  476 	ret
                            477 ;src/entities/entities.c:167: i8 moveEntityY (TEntity* ent, i8 my) {
                            478 ;	---------------------------------
                            479 ; Function moveEntityY
                            480 ; ---------------------------------
   0492                     481 _moveEntityY::
   0492 DD E5         [15]  482 	push	ix
   0494 DD 21 00 00   [14]  483 	ld	ix,#0
   0498 DD 39         [15]  484 	add	ix,sp
   049A 21 F5 FF      [10]  485 	ld	hl, #-11
   049D 39            [11]  486 	add	hl, sp
   049E F9            [ 6]  487 	ld	sp, hl
                            488 ;src/entities/entities.c:168: i8 moved = 0;      // Number of bytes the entity has moved 
   049F DD 36 F6 00   [19]  489 	ld	-10 (ix), #0x00
                            490 ;src/entities/entities.c:176: if (umy <= ent->y) {
   04A3 DD 7E 04      [19]  491 	ld	a, 4 (ix)
   04A6 DD 77 FE      [19]  492 	ld	-2 (ix), a
   04A9 DD 7E 05      [19]  493 	ld	a, 5 (ix)
   04AC DD 77 FF      [19]  494 	ld	-1 (ix), a
                            495 ;src/entities/entities.c:178: ent->videopos  = cpct_getScreenPtr(CPCT_VMEM_START, ent->x, ent->y);
   04AF DD 7E FE      [19]  496 	ld	a, -2 (ix)
   04B2 C6 02         [ 7]  497 	add	a, #0x02
   04B4 DD 77 F7      [19]  498 	ld	-9 (ix), a
   04B7 DD 7E FF      [19]  499 	ld	a, -1 (ix)
   04BA CE 00         [ 7]  500 	adc	a, #0x00
   04BC DD 77 F8      [19]  501 	ld	-8 (ix), a
   04BF DD 7E FE      [19]  502 	ld	a, -2 (ix)
   04C2 C6 04         [ 7]  503 	add	a, #0x04
   04C4 DD 77 F9      [19]  504 	ld	-7 (ix), a
   04C7 DD 7E FF      [19]  505 	ld	a, -1 (ix)
   04CA CE 00         [ 7]  506 	adc	a, #0x00
   04CC DD 77 FA      [19]  507 	ld	-6 (ix), a
                            508 ;src/entities/entities.c:179: moved          = my;
   04CF DD 7E 06      [19]  509 	ld	a, 6 (ix)
   04D2 DD 77 FB      [19]  510 	ld	-5 (ix), a
                            511 ;src/entities/entities.c:176: if (umy <= ent->y) {
   04D5 DD 7E FE      [19]  512 	ld	a, -2 (ix)
   04D8 C6 05         [ 7]  513 	add	a, #0x05
   04DA DD 77 FC      [19]  514 	ld	-4 (ix), a
   04DD DD 7E FF      [19]  515 	ld	a, -1 (ix)
   04E0 CE 00         [ 7]  516 	adc	a, #0x00
   04E2 DD 77 FD      [19]  517 	ld	-3 (ix), a
                            518 ;src/entities/entities.c:172: if (my < 0) {
   04E5 DD CB 06 7E   [20]  519 	bit	7, 6 (ix)
   04E9 28 6D         [12]  520 	jr	Z,00116$
                            521 ;src/entities/entities.c:173: umy = -my;  // umy = possive value of my, that is negative.
   04EB AF            [ 4]  522 	xor	a, a
   04EC DD 96 06      [19]  523 	sub	a, 6 (ix)
   04EF 47            [ 4]  524 	ld	b, a
                            525 ;src/entities/entities.c:176: if (umy <= ent->y) {
   04F0 DD 6E FC      [19]  526 	ld	l,-4 (ix)
   04F3 DD 66 FD      [19]  527 	ld	h,-3 (ix)
   04F6 4E            [ 7]  528 	ld	c, (hl)
                            529 ;src/entities/entities.c:177: ent->y        -= umy;
   04F7 79            [ 4]  530 	ld	a,c
   04F8 B8            [ 4]  531 	cp	a,b
   04F9 38 2C         [12]  532 	jr	C,00104$
   04FB 90            [ 4]  533 	sub	a, b
   04FC 57            [ 4]  534 	ld	d, a
   04FD DD 6E FC      [19]  535 	ld	l,-4 (ix)
   0500 DD 66 FD      [19]  536 	ld	h,-3 (ix)
   0503 72            [ 7]  537 	ld	(hl), d
                            538 ;src/entities/entities.c:178: ent->videopos  = cpct_getScreenPtr(CPCT_VMEM_START, ent->x, ent->y);
   0504 DD 6E F9      [19]  539 	ld	l,-7 (ix)
   0507 DD 66 FA      [19]  540 	ld	h,-6 (ix)
   050A 5E            [ 7]  541 	ld	e, (hl)
   050B D5            [11]  542 	push	de
   050C 21 00 C0      [10]  543 	ld	hl, #0xc000
   050F E5            [11]  544 	push	hl
   0510 CD E2 14      [17]  545 	call	_cpct_getScreenPtr
   0513 4D            [ 4]  546 	ld	c, l
   0514 44            [ 4]  547 	ld	b, h
   0515 DD 6E F7      [19]  548 	ld	l,-9 (ix)
   0518 DD 66 F8      [19]  549 	ld	h,-8 (ix)
   051B 71            [ 7]  550 	ld	(hl), c
   051C 23            [ 6]  551 	inc	hl
   051D 70            [ 7]  552 	ld	(hl), b
                            553 ;src/entities/entities.c:179: moved          = my;
   051E DD 7E FB      [19]  554 	ld	a, -5 (ix)
   0521 DD 77 F6      [19]  555 	ld	-10 (ix), a
   0524 C3 ED 05      [10]  556 	jp	00117$
   0527                     557 00104$:
                            558 ;src/entities/entities.c:180: } else if ( ent->y ) {
   0527 79            [ 4]  559 	ld	a, c
   0528 B7            [ 4]  560 	or	a, a
   0529 CA ED 05      [10]  561 	jp	Z, 00117$
                            562 ;src/entities/entities.c:182: ent->videopos  = CPCT_VMEM_START + ent->x;
   052C DD 6E F9      [19]  563 	ld	l,-7 (ix)
   052F DD 66 FA      [19]  564 	ld	h,-6 (ix)
   0532 4E            [ 7]  565 	ld	c, (hl)
   0533 3E 00         [ 7]  566 	ld	a,#0x00
   0535 C6 C0         [ 7]  567 	add	a,#0xc0
   0537 47            [ 4]  568 	ld	b, a
   0538 DD 6E F7      [19]  569 	ld	l,-9 (ix)
   053B DD 66 F8      [19]  570 	ld	h,-8 (ix)
   053E 71            [ 7]  571 	ld	(hl), c
   053F 23            [ 6]  572 	inc	hl
   0540 70            [ 7]  573 	ld	(hl), b
                            574 ;src/entities/entities.c:183: moved          = -ent->y;
   0541 DD 6E FC      [19]  575 	ld	l,-4 (ix)
   0544 DD 66 FD      [19]  576 	ld	h,-3 (ix)
   0547 4E            [ 7]  577 	ld	c, (hl)
   0548 AF            [ 4]  578 	xor	a, a
   0549 91            [ 4]  579 	sub	a, c
   054A DD 77 F6      [19]  580 	ld	-10 (ix), a
                            581 ;src/entities/entities.c:184: ent->y         = 0;
   054D DD 6E FC      [19]  582 	ld	l,-4 (ix)
   0550 DD 66 FD      [19]  583 	ld	h,-3 (ix)
   0553 36 00         [10]  584 	ld	(hl), #0x00
   0555 C3 ED 05      [10]  585 	jp	00117$
   0558                     586 00116$:
                            587 ;src/entities/entities.c:187: } else if (my) {
   0558 DD 7E 06      [19]  588 	ld	a, 6 (ix)
   055B B7            [ 4]  589 	or	a, a
   055C CA ED 05      [10]  590 	jp	Z, 00117$
                            591 ;src/entities/entities.c:193: anim       = ent->anim;
   055F DD 6E FE      [19]  592 	ld	l,-2 (ix)
   0562 DD 66 FF      [19]  593 	ld	h,-1 (ix)
   0565 7E            [ 7]  594 	ld	a, (hl)
   0566 23            [ 6]  595 	inc	hl
   0567 66            [ 7]  596 	ld	h, (hl)
   0568 6F            [ 4]  597 	ld	l, a
                            598 ;src/entities/entities.c:194: space_left = g_SCR_HEIGHT - anim->frames[anim->frame_id]->height - ent->y;
   0569 E5            [11]  599 	push	hl
   056A 4E            [ 7]  600 	ld	c, (hl)
   056B 23            [ 6]  601 	inc	hl
   056C 46            [ 7]  602 	ld	b, (hl)
   056D E1            [10]  603 	pop	hl
   056E 23            [ 6]  604 	inc	hl
   056F 23            [ 6]  605 	inc	hl
   0570 6E            [ 7]  606 	ld	l, (hl)
   0571 26 00         [ 7]  607 	ld	h, #0x00
   0573 29            [11]  608 	add	hl, hl
   0574 09            [11]  609 	add	hl, bc
   0575 7E            [ 7]  610 	ld	a, (hl)
   0576 23            [ 6]  611 	inc	hl
   0577 66            [ 7]  612 	ld	h, (hl)
   0578 6F            [ 4]  613 	ld	l, a
   0579 23            [ 6]  614 	inc	hl
   057A 23            [ 6]  615 	inc	hl
   057B 23            [ 6]  616 	inc	hl
   057C 4E            [ 7]  617 	ld	c, (hl)
   057D 3A 0D 03      [13]  618 	ld	a,(#_g_SCR_HEIGHT + 0)
   0580 91            [ 4]  619 	sub	a, c
   0581 4F            [ 4]  620 	ld	c, a
   0582 DD 6E FC      [19]  621 	ld	l,-4 (ix)
   0585 DD 66 FD      [19]  622 	ld	h,-3 (ix)
   0588 7E            [ 7]  623 	ld	a, (hl)
   0589 DD 77 FE      [19]  624 	ld	-2 (ix), a
   058C 79            [ 4]  625 	ld	a, c
   058D DD 96 FE      [19]  626 	sub	a, -2 (ix)
                            627 ;src/entities/entities.c:197: if (umy <= space_left) {
   0590 DD 77 F5      [19]  628 	ld	-11 (ix), a
   0593 DD 96 FB      [19]  629 	sub	a, -5 (ix)
   0596 38 15         [12]  630 	jr	C,00109$
                            631 ;src/entities/entities.c:198: ent->y  += umy;
   0598 DD 7E FE      [19]  632 	ld	a, -2 (ix)
   059B DD 86 FB      [19]  633 	add	a, -5 (ix)
   059E DD 6E FC      [19]  634 	ld	l,-4 (ix)
   05A1 DD 66 FD      [19]  635 	ld	h,-3 (ix)
   05A4 77            [ 7]  636 	ld	(hl), a
                            637 ;src/entities/entities.c:199: moved    = umy;
   05A5 DD 7E FB      [19]  638 	ld	a, -5 (ix)
   05A8 DD 77 F6      [19]  639 	ld	-10 (ix), a
   05AB 18 19         [12]  640 	jr	00110$
   05AD                     641 00109$:
                            642 ;src/entities/entities.c:200: } else if (space_left) {
   05AD DD 7E F5      [19]  643 	ld	a, -11 (ix)
   05B0 B7            [ 4]  644 	or	a, a
   05B1 28 13         [12]  645 	jr	Z,00110$
                            646 ;src/entities/entities.c:202: ent->y  += space_left;
   05B3 DD 7E FE      [19]  647 	ld	a, -2 (ix)
   05B6 DD 86 F5      [19]  648 	add	a, -11 (ix)
   05B9 DD 6E FC      [19]  649 	ld	l,-4 (ix)
   05BC DD 66 FD      [19]  650 	ld	h,-3 (ix)
   05BF 77            [ 7]  651 	ld	(hl), a
                            652 ;src/entities/entities.c:203: moved    = space_left;
   05C0 DD 7E F5      [19]  653 	ld	a, -11 (ix)
   05C3 DD 77 F6      [19]  654 	ld	-10 (ix), a
   05C6                     655 00110$:
                            656 ;src/entities/entities.c:205: if (moved) {
   05C6 DD 7E F6      [19]  657 	ld	a, -10 (ix)
   05C9 B7            [ 4]  658 	or	a, a
   05CA 28 21         [12]  659 	jr	Z,00117$
                            660 ;src/entities/entities.c:207: ent->videopos = cpct_getScreenPtr(CPCT_VMEM_START, ent->x, ent->y);
   05CC DD 6E FC      [19]  661 	ld	l,-4 (ix)
   05CF DD 66 FD      [19]  662 	ld	h,-3 (ix)
   05D2 46            [ 7]  663 	ld	b, (hl)
   05D3 DD 6E F9      [19]  664 	ld	l,-7 (ix)
   05D6 DD 66 FA      [19]  665 	ld	h,-6 (ix)
   05D9 4E            [ 7]  666 	ld	c, (hl)
   05DA C5            [11]  667 	push	bc
   05DB 21 00 C0      [10]  668 	ld	hl, #0xc000
   05DE E5            [11]  669 	push	hl
   05DF CD E2 14      [17]  670 	call	_cpct_getScreenPtr
   05E2 4D            [ 4]  671 	ld	c, l
   05E3 44            [ 4]  672 	ld	b, h
   05E4 DD 6E F7      [19]  673 	ld	l,-9 (ix)
   05E7 DD 66 F8      [19]  674 	ld	h,-8 (ix)
   05EA 71            [ 7]  675 	ld	(hl), c
   05EB 23            [ 6]  676 	inc	hl
   05EC 70            [ 7]  677 	ld	(hl), b
   05ED                     678 00117$:
                            679 ;src/entities/entities.c:212: return moved;
   05ED DD 6E F6      [19]  680 	ld	l, -10 (ix)
   05F0 DD F9         [10]  681 	ld	sp, ix
   05F2 DD E1         [14]  682 	pop	ix
   05F4 C9            [10]  683 	ret
                            684 ;src/entities/entities.c:219: i8 updateAnimation(TAnimation* anim) {
                            685 ;	---------------------------------
                            686 ; Function updateAnimation
                            687 ; ---------------------------------
   05F5                     688 _updateAnimation::
   05F5 DD E5         [15]  689 	push	ix
   05F7 DD 21 00 00   [14]  690 	ld	ix,#0
   05FB DD 39         [15]  691 	add	ix,sp
   05FD F5            [11]  692 	push	af
   05FE F5            [11]  693 	push	af
   05FF 3B            [ 6]  694 	dec	sp
                            695 ;src/entities/entities.c:220: i8 newframe = 0;
   0600 DD 36 FB 00   [19]  696 	ld	-5 (ix), #0x00
                            697 ;src/entities/entities.c:223: if (anim->status != as_pause && anim->status != as_end) {
   0604 DD 4E 04      [19]  698 	ld	c,4 (ix)
   0607 DD 46 05      [19]  699 	ld	b,5 (ix)
   060A 21 04 00      [10]  700 	ld	hl, #0x0004
   060D 09            [11]  701 	add	hl,bc
   060E DD 75 FE      [19]  702 	ld	-2 (ix), l
   0611 DD 74 FF      [19]  703 	ld	-1 (ix), h
   0614 7E            [ 7]  704 	ld	a, (hl)
   0615 FE 02         [ 7]  705 	cp	a, #0x02
   0617 CA 9A 06      [10]  706 	jp	Z,00110$
   061A D6 03         [ 7]  707 	sub	a, #0x03
   061C CA 9A 06      [10]  708 	jp	Z,00110$
                            709 ;src/entities/entities.c:226: if ( ! --anim->time ) {
   061F 59            [ 4]  710 	ld	e, c
   0620 50            [ 4]  711 	ld	d, b
   0621 13            [ 6]  712 	inc	de
   0622 13            [ 6]  713 	inc	de
   0623 13            [ 6]  714 	inc	de
   0624 1A            [ 7]  715 	ld	a, (de)
   0625 C6 FF         [ 7]  716 	add	a, #0xff
   0627 12            [ 7]  717 	ld	(de), a
   0628 B7            [ 4]  718 	or	a, a
   0629 20 6F         [12]  719 	jr	NZ,00110$
                            720 ;src/entities/entities.c:230: newframe = 1;
   062B DD 36 FB 01   [19]  721 	ld	-5 (ix), #0x01
                            722 ;src/entities/entities.c:231: frame = anim->frames[ ++anim->frame_id ]; 
   062F 0A            [ 7]  723 	ld	a, (bc)
   0630 DD 77 FC      [19]  724 	ld	-4 (ix), a
   0633 03            [ 6]  725 	inc	bc
   0634 0A            [ 7]  726 	ld	a, (bc)
   0635 DD 77 FD      [19]  727 	ld	-3 (ix), a
   0638 0B            [ 6]  728 	dec	bc
   0639 C5            [11]  729 	push	bc
   063A FD E1         [14]  730 	pop	iy
   063C FD 23         [10]  731 	inc	iy
   063E FD 23         [10]  732 	inc	iy
   0640 FD 34 00      [23]  733 	inc	0 (iy)
   0643 FD 6E 00      [19]  734 	ld	l, 0 (iy)
   0646 26 00         [ 7]  735 	ld	h, #0x00
   0648 29            [11]  736 	add	hl, hl
   0649 DD 7E FC      [19]  737 	ld	a, -4 (ix)
   064C 85            [ 4]  738 	add	a, l
   064D 6F            [ 4]  739 	ld	l, a
   064E DD 7E FD      [19]  740 	ld	a, -3 (ix)
   0651 8C            [ 4]  741 	adc	a, h
   0652 67            [ 4]  742 	ld	h, a
   0653 7E            [ 7]  743 	ld	a, (hl)
   0654 23            [ 6]  744 	inc	hl
   0655 66            [ 7]  745 	ld	h, (hl)
   0656 6F            [ 4]  746 	ld	l, a
   0657 DD 75 FC      [19]  747 	ld	-4 (ix), l
   065A DD 74 FD      [19]  748 	ld	-3 (ix), h
                            749 ;src/entities/entities.c:234: if (frame) {
   065D 7C            [ 4]  750 	ld	a, h
   065E B5            [ 4]  751 	or	a,l
   065F 28 0E         [12]  752 	jr	Z,00105$
                            753 ;src/entities/entities.c:236: anim->time = frame->time;  // Get animation cycles for this frame
   0661 DD 6E FC      [19]  754 	ld	l,-4 (ix)
   0664 DD 66 FD      [19]  755 	ld	h,-3 (ix)
   0667 01 09 00      [10]  756 	ld	bc, #0x0009
   066A 09            [11]  757 	add	hl, bc
   066B 7E            [ 7]  758 	ld	a, (hl)
   066C 12            [ 7]  759 	ld	(de), a
   066D 18 2B         [12]  760 	jr	00110$
   066F                     761 00105$:
                            762 ;src/entities/entities.c:237: } else if ( anim->status == as_cycle ) {
   066F DD 6E FE      [19]  763 	ld	l,-2 (ix)
   0672 DD 66 FF      [19]  764 	ld	h,-1 (ix)
   0675 6E            [ 7]  765 	ld	l, (hl)
   0676 2D            [ 4]  766 	dec	l
   0677 20 16         [12]  767 	jr	NZ,00102$
                            768 ;src/entities/entities.c:239: anim->frame_id = 0;        // Next frame_id is first one of this animation
   0679 FD 36 00 00   [19]  769 	ld	0 (iy), #0x00
                            770 ;src/entities/entities.c:240: anim->time     = anim->frames[0]->time; // Restore animation cycles for the first frame
   067D 69            [ 4]  771 	ld	l, c
   067E 60            [ 4]  772 	ld	h, b
   067F 7E            [ 7]  773 	ld	a, (hl)
   0680 23            [ 6]  774 	inc	hl
   0681 66            [ 7]  775 	ld	h, (hl)
   0682 6F            [ 4]  776 	ld	l, a
   0683 7E            [ 7]  777 	ld	a, (hl)
   0684 23            [ 6]  778 	inc	hl
   0685 66            [ 7]  779 	ld	h, (hl)
   0686 6F            [ 4]  780 	ld	l, a
   0687 01 09 00      [10]  781 	ld	bc, #0x0009
   068A 09            [11]  782 	add	hl, bc
   068B 7E            [ 7]  783 	ld	a, (hl)
   068C 12            [ 7]  784 	ld	(de), a
   068D 18 0B         [12]  785 	jr	00110$
   068F                     786 00102$:
                            787 ;src/entities/entities.c:243: anim->status = as_end;  // Animation set to end status
   068F DD 6E FE      [19]  788 	ld	l,-2 (ix)
   0692 DD 66 FF      [19]  789 	ld	h,-1 (ix)
   0695 36 03         [10]  790 	ld	(hl), #0x03
                            791 ;src/entities/entities.c:244: --anim->frame_id;       // frame_id decremented to leave animation permanently on last frame
   0697 FD 35 00      [23]  792 	dec	0 (iy)
   069A                     793 00110$:
                            794 ;src/entities/entities.c:250: return newframe;
   069A DD 6E FB      [19]  795 	ld	l, -5 (ix)
   069D DD F9         [10]  796 	ld	sp, ix
   069F DD E1         [14]  797 	pop	ix
   06A1 C9            [10]  798 	ret
                            799 ;src/entities/entities.c:256: void updateEntity(TEntity *ent) {
                            800 ;	---------------------------------
                            801 ; Function updateEntity
                            802 ; ---------------------------------
   06A2                     803 _updateEntity::
   06A2 DD E5         [15]  804 	push	ix
   06A4 DD 21 00 00   [14]  805 	ld	ix,#0
   06A8 DD 39         [15]  806 	add	ix,sp
   06AA 21 F9 FF      [10]  807 	ld	hl, #-7
   06AD 39            [11]  808 	add	hl, sp
   06AE F9            [ 6]  809 	ld	sp, hl
                            810 ;src/entities/entities.c:257: TAnimation* anim = ent->anim;
   06AF DD 7E 04      [19]  811 	ld	a, 4 (ix)
   06B2 DD 77 FE      [19]  812 	ld	-2 (ix), a
   06B5 DD 7E 05      [19]  813 	ld	a, 5 (ix)
   06B8 DD 77 FF      [19]  814 	ld	-1 (ix), a
   06BB DD 6E FE      [19]  815 	ld	l,-2 (ix)
   06BE DD 66 FF      [19]  816 	ld	h,-1 (ix)
   06C1 7E            [ 7]  817 	ld	a, (hl)
   06C2 DD 77 F9      [19]  818 	ld	-7 (ix), a
   06C5 23            [ 6]  819 	inc	hl
   06C6 7E            [ 7]  820 	ld	a, (hl)
   06C7 DD 77 FA      [19]  821 	ld	-6 (ix), a
                            822 ;src/entities/entities.c:259: if ( updateAnimation(anim) ) {
   06CA E1            [10]  823 	pop	hl
   06CB E5            [11]  824 	push	hl
   06CC E5            [11]  825 	push	hl
   06CD CD F5 05      [17]  826 	call	_updateAnimation
   06D0 F1            [10]  827 	pop	af
   06D1 7D            [ 4]  828 	ld	a, l
   06D2 B7            [ 4]  829 	or	a, a
   06D3 CA C6 07      [10]  830 	jp	Z, 00117$
                            831 ;src/entities/entities.c:260: if ( anim->status != as_end ) {
   06D6 E1            [10]  832 	pop	hl
   06D7 E5            [11]  833 	push	hl
   06D8 11 04 00      [10]  834 	ld	de, #0x0004
   06DB 19            [11]  835 	add	hl, de
   06DC 4E            [ 7]  836 	ld	c, (hl)
                            837 ;src/entities/entities.c:261: TAnimFrame* frame = anim->frames[anim->frame_id];
   06DD E1            [10]  838 	pop	hl
   06DE E5            [11]  839 	push	hl
   06DF 23            [ 6]  840 	inc	hl
   06E0 23            [ 6]  841 	inc	hl
   06E1 7E            [ 7]  842 	ld	a, (hl)
   06E2 DD 77 FD      [19]  843 	ld	-3 (ix), a
                            844 ;src/entities/entities.c:260: if ( anim->status != as_end ) {
   06E5 79            [ 4]  845 	ld	a, c
   06E6 D6 03         [ 7]  846 	sub	a, #0x03
   06E8 CA A1 07      [10]  847 	jp	Z,00113$
                            848 ;src/entities/entities.c:261: TAnimFrame* frame = anim->frames[anim->frame_id];
   06EB E1            [10]  849 	pop	hl
   06EC E5            [11]  850 	push	hl
   06ED 4E            [ 7]  851 	ld	c, (hl)
   06EE 23            [ 6]  852 	inc	hl
   06EF 46            [ 7]  853 	ld	b, (hl)
   06F0 DD 6E FD      [19]  854 	ld	l, -3 (ix)
   06F3 26 00         [ 7]  855 	ld	h, #0x00
   06F5 29            [11]  856 	add	hl, hl
   06F6 09            [11]  857 	add	hl, bc
   06F7 4E            [ 7]  858 	ld	c, (hl)
   06F8 23            [ 6]  859 	inc	hl
   06F9 46            [ 7]  860 	ld	b, (hl)
                            861 ;src/entities/entities.c:264: if (frame->ew) cpct_drawSolidBox(ent->videopos + (int)frame->ex, 0x00, frame->ew, frame->eh);
   06FA C5            [11]  862 	push	bc
   06FB FD E1         [14]  863 	pop	iy
   06FD FD 7E 07      [19]  864 	ld	a, 7 (iy)
   0700 DD 77 FC      [19]  865 	ld	-4 (ix), a
   0703 B7            [ 4]  866 	or	a, a
   0704 28 31         [12]  867 	jr	Z,00102$
   0706 C5            [11]  868 	push	bc
   0707 FD E1         [14]  869 	pop	iy
   0709 FD 7E 08      [19]  870 	ld	a, 8 (iy)
   070C DD 77 FB      [19]  871 	ld	-5 (ix), a
   070F DD 6E FE      [19]  872 	ld	l,-2 (ix)
   0712 DD 66 FF      [19]  873 	ld	h,-1 (ix)
   0715 23            [ 6]  874 	inc	hl
   0716 23            [ 6]  875 	inc	hl
   0717 5E            [ 7]  876 	ld	e, (hl)
   0718 23            [ 6]  877 	inc	hl
   0719 56            [ 7]  878 	ld	d, (hl)
   071A C5            [11]  879 	push	bc
   071B FD E1         [14]  880 	pop	iy
   071D FD 6E 06      [19]  881 	ld	l, 6 (iy)
   0720 7D            [ 4]  882 	ld	a, l
   0721 17            [ 4]  883 	rla
   0722 9F            [ 4]  884 	sbc	a, a
   0723 67            [ 4]  885 	ld	h, a
   0724 19            [11]  886 	add	hl,de
   0725 EB            [ 4]  887 	ex	de,hl
   0726 C5            [11]  888 	push	bc
   0727 DD 66 FB      [19]  889 	ld	h, -5 (ix)
   072A DD 6E FC      [19]  890 	ld	l, -4 (ix)
   072D E5            [11]  891 	push	hl
   072E 21 00 00      [10]  892 	ld	hl, #0x0000
   0731 E5            [11]  893 	push	hl
   0732 D5            [11]  894 	push	de
   0733 CD 3A 14      [17]  895 	call	_cpct_drawSolidBox
   0736 C1            [10]  896 	pop	bc
   0737                     897 00102$:
                            898 ;src/entities/entities.c:265: if (frame->mx) moveEntityX(ent, frame->mx);
   0737 C5            [11]  899 	push	bc
   0738 FD E1         [14]  900 	pop	iy
   073A FD 56 04      [19]  901 	ld	d, 4 (iy)
   073D 7A            [ 4]  902 	ld	a, d
   073E B7            [ 4]  903 	or	a, a
   073F 28 10         [12]  904 	jr	Z,00104$
   0741 C5            [11]  905 	push	bc
   0742 D5            [11]  906 	push	de
   0743 33            [ 6]  907 	inc	sp
   0744 DD 6E FE      [19]  908 	ld	l,-2 (ix)
   0747 DD 66 FF      [19]  909 	ld	h,-1 (ix)
   074A E5            [11]  910 	push	hl
   074B CD 0E 03      [17]  911 	call	_moveEntityX
   074E F1            [10]  912 	pop	af
   074F 33            [ 6]  913 	inc	sp
   0750 C1            [10]  914 	pop	bc
   0751                     915 00104$:
                            916 ;src/entities/entities.c:266: if (frame->my) moveEntityY(ent, frame->my);
   0751 C5            [11]  917 	push	bc
   0752 FD E1         [14]  918 	pop	iy
   0754 FD 7E 05      [19]  919 	ld	a, 5 (iy)
   0757 B7            [ 4]  920 	or	a, a
   0758 28 10         [12]  921 	jr	Z,00106$
   075A C5            [11]  922 	push	bc
   075B F5            [11]  923 	push	af
   075C 33            [ 6]  924 	inc	sp
   075D DD 6E 04      [19]  925 	ld	l,4 (ix)
   0760 DD 66 05      [19]  926 	ld	h,5 (ix)
   0763 E5            [11]  927 	push	hl
   0764 CD 92 04      [17]  928 	call	_moveEntityY
   0767 F1            [10]  929 	pop	af
   0768 33            [ 6]  930 	inc	sp
   0769 C1            [10]  931 	pop	bc
   076A                     932 00106$:
                            933 ;src/entities/entities.c:269: if (frame->width + ent->x > g_SCR_WIDTH) {
   076A 69            [ 4]  934 	ld	l, c
   076B 60            [ 4]  935 	ld	h, b
   076C 23            [ 6]  936 	inc	hl
   076D 23            [ 6]  937 	inc	hl
   076E 4E            [ 7]  938 	ld	c, (hl)
   076F 06 00         [ 7]  939 	ld	b, #0x00
   0771 DD 6E FE      [19]  940 	ld	l,-2 (ix)
   0774 DD 66 FF      [19]  941 	ld	h,-1 (ix)
   0777 11 04 00      [10]  942 	ld	de, #0x0004
   077A 19            [11]  943 	add	hl, de
   077B 6E            [ 7]  944 	ld	l, (hl)
   077C 26 00         [ 7]  945 	ld	h, #0x00
   077E 09            [11]  946 	add	hl, bc
   077F 3A 0C 03      [13]  947 	ld	a,(#_g_SCR_WIDTH + 0)
   0782 06 00         [ 7]  948 	ld	b, #0x00
   0784 95            [ 4]  949 	sub	a, l
   0785 78            [ 4]  950 	ld	a, b
   0786 9C            [ 4]  951 	sbc	a, h
   0787 E2 8C 07      [10]  952 	jp	PO, 00148$
   078A EE 80         [ 7]  953 	xor	a, #0x80
   078C                     954 00148$:
   078C F2 C6 07      [10]  955 	jp	P, 00117$
                            956 ;src/entities/entities.c:270: moveEntityX(ent, -1);
   078F 3E FF         [ 7]  957 	ld	a, #0xff
   0791 F5            [11]  958 	push	af
   0792 33            [ 6]  959 	inc	sp
   0793 DD 6E FE      [19]  960 	ld	l,-2 (ix)
   0796 DD 66 FF      [19]  961 	ld	h,-1 (ix)
   0799 E5            [11]  962 	push	hl
   079A CD 0E 03      [17]  963 	call	_moveEntityX
   079D F1            [10]  964 	pop	af
   079E 33            [ 6]  965 	inc	sp
   079F 18 25         [12]  966 	jr	00117$
   07A1                     967 00113$:
                            968 ;src/entities/entities.c:272: } else if (anim->frame_id == 0xFF) {
   07A1 DD 7E FD      [19]  969 	ld	a, -3 (ix)
   07A4 3C            [ 4]  970 	inc	a
   07A5 20 11         [12]  971 	jr	NZ,00110$
                            972 ;src/entities/entities.c:273: cpct_drawSolidBox(CPCT_VMEM_START, 0xFF, 4, 8);
   07A7 21 04 08      [10]  973 	ld	hl, #0x0804
   07AA E5            [11]  974 	push	hl
   07AB 21 FF 00      [10]  975 	ld	hl, #0x00ff
   07AE E5            [11]  976 	push	hl
   07AF 21 00 C0      [10]  977 	ld	hl, #0xc000
   07B2 E5            [11]  978 	push	hl
   07B3 CD 3A 14      [17]  979 	call	_cpct_drawSolidBox
   07B6 18 0E         [12]  980 	jr	00117$
   07B8                     981 00110$:
                            982 ;src/entities/entities.c:275: ent->status = es_stop;
   07B8 DD 7E FE      [19]  983 	ld	a, -2 (ix)
   07BB C6 06         [ 7]  984 	add	a, #0x06
   07BD 6F            [ 4]  985 	ld	l, a
   07BE DD 7E FF      [19]  986 	ld	a, -1 (ix)
   07C1 CE 00         [ 7]  987 	adc	a, #0x00
   07C3 67            [ 4]  988 	ld	h, a
   07C4 36 01         [10]  989 	ld	(hl), #0x01
   07C6                     990 00117$:
   07C6 DD F9         [10]  991 	ld	sp, ix
   07C8 DD E1         [14]  992 	pop	ix
   07CA C9            [10]  993 	ret
                            994 ;src/entities/entities.c:283: void setAnimation(TEntity *ent, TEntityStatus newstatus) {
                            995 ;	---------------------------------
                            996 ; Function setAnimation
                            997 ; ---------------------------------
   07CB                     998 _setAnimation::
   07CB DD E5         [15]  999 	push	ix
   07CD DD 21 00 00   [14] 1000 	ld	ix,#0
   07D1 DD 39         [15] 1001 	add	ix,sp
   07D3 F5            [11] 1002 	push	af
                           1003 ;src/entities/entities.c:284: TAnimation* anim = ent->anim;
   07D4 DD 4E 04      [19] 1004 	ld	c,4 (ix)
   07D7 DD 46 05      [19] 1005 	ld	b,5 (ix)
   07DA 69            [ 4] 1006 	ld	l, c
   07DB 60            [ 4] 1007 	ld	h, b
   07DC 5E            [ 7] 1008 	ld	e, (hl)
   07DD 23            [ 6] 1009 	inc	hl
   07DE 56            [ 7] 1010 	ld	d, (hl)
                           1011 ;src/entities/entities.c:287: if ( anim->status == as_end ) {
   07DF 21 04 00      [10] 1012 	ld	hl, #0x0004
   07E2 19            [11] 1013 	add	hl,de
   07E3 E3            [19] 1014 	ex	(sp), hl
   07E4 E1            [10] 1015 	pop	hl
   07E5 E5            [11] 1016 	push	hl
   07E6 7E            [ 7] 1017 	ld	a, (hl)
   07E7 D6 03         [ 7] 1018 	sub	a, #0x03
   07E9 C2 76 08      [10] 1019 	jp	NZ,00112$
                           1020 ;src/entities/entities.c:288: ent->status = newstatus;
   07EC 21 06 00      [10] 1021 	ld	hl, #0x0006
   07EF 09            [11] 1022 	add	hl, bc
   07F0 DD 7E 06      [19] 1023 	ld	a, 6 (ix)
   07F3 77            [ 7] 1024 	ld	(hl), a
                           1025 ;src/entities/entities.c:291: switch (newstatus) {
   07F4 3E 07         [ 7] 1026 	ld	a, #0x07
   07F6 DD 96 06      [19] 1027 	sub	a, 6 (ix)
   07F9 38 6A         [12] 1028 	jr	C,00109$
   07FB DD 4E 06      [19] 1029 	ld	c, 6 (ix)
   07FE 06 00         [ 7] 1030 	ld	b, #0x00
   0800 21 07 08      [10] 1031 	ld	hl, #00124$
   0803 09            [11] 1032 	add	hl, bc
   0804 09            [11] 1033 	add	hl, bc
   0805 09            [11] 1034 	add	hl, bc
   0806 E9            [ 4] 1035 	jp	(hl)
   0807                    1036 00124$:
   0807 C3 1F 08      [10] 1037 	jp	00101$
   080A C3 28 08      [10] 1038 	jp	00102$
   080D C3 31 08      [10] 1039 	jp	00103$
   0810 C3 3A 08      [10] 1040 	jp	00104$
   0813 C3 43 08      [10] 1041 	jp	00105$
   0816 C3 4C 08      [10] 1042 	jp	00106$
   0819 C3 55 08      [10] 1043 	jp	00107$
   081C C3 5E 08      [10] 1044 	jp	00108$
                           1045 ;src/entities/entities.c:292: case es_dead:        { anim->frames = (TAnimFrame**)g_animDie;       break;  }
   081F                    1046 00101$:
   081F 6B            [ 4] 1047 	ld	l, e
   0820 62            [ 4] 1048 	ld	h, d
   0821 36 FA         [10] 1049 	ld	(hl), #<(_g_animDie)
   0823 23            [ 6] 1050 	inc	hl
   0824 36 02         [10] 1051 	ld	(hl), #>(_g_animDie)
   0826 18 3D         [12] 1052 	jr	00109$
                           1053 ;src/entities/entities.c:293: case es_stop:        { anim->frames = (TAnimFrame**)g_animStay;      break;  }
   0828                    1054 00102$:
   0828 6B            [ 4] 1055 	ld	l, e
   0829 62            [ 4] 1056 	ld	h, d
   082A 36 CA         [10] 1057 	ld	(hl), #<(_g_animStay)
   082C 23            [ 6] 1058 	inc	hl
   082D 36 02         [10] 1059 	ld	(hl), #>(_g_animStay)
   082F 18 34         [12] 1060 	jr	00109$
                           1061 ;src/entities/entities.c:294: case es_walk_right:  { anim->frames = (TAnimFrame**)g_animWalkRight; break;  }
   0831                    1062 00103$:
   0831 6B            [ 4] 1063 	ld	l, e
   0832 62            [ 4] 1064 	ld	h, d
   0833 36 CE         [10] 1065 	ld	(hl), #<(_g_animWalkRight)
   0835 23            [ 6] 1066 	inc	hl
   0836 36 02         [10] 1067 	ld	(hl), #>(_g_animWalkRight)
   0838 18 2B         [12] 1068 	jr	00109$
                           1069 ;src/entities/entities.c:295: case es_walk_left:   { anim->frames = (TAnimFrame**)g_animWalkLeft;  break;  }
   083A                    1070 00104$:
   083A 6B            [ 4] 1071 	ld	l, e
   083B 62            [ 4] 1072 	ld	h, d
   083C 36 D8         [10] 1073 	ld	(hl), #<(_g_animWalkLeft)
   083E 23            [ 6] 1074 	inc	hl
   083F 36 02         [10] 1075 	ld	(hl), #>(_g_animWalkLeft)
   0841 18 22         [12] 1076 	jr	00109$
                           1077 ;src/entities/entities.c:296: case es_fist:        { anim->frames = (TAnimFrame**)g_animFist;      break;  }
   0843                    1078 00105$:
   0843 6B            [ 4] 1079 	ld	l, e
   0844 62            [ 4] 1080 	ld	h, d
   0845 36 E2         [10] 1081 	ld	(hl), #<(_g_animFist)
   0847 23            [ 6] 1082 	inc	hl
   0848 36 02         [10] 1083 	ld	(hl), #>(_g_animFist)
   084A 18 19         [12] 1084 	jr	00109$
                           1085 ;src/entities/entities.c:297: case es_kick:        { anim->frames = (TAnimFrame**)g_animKick;      break;  }
   084C                    1086 00106$:
   084C 6B            [ 4] 1087 	ld	l, e
   084D 62            [ 4] 1088 	ld	h, d
   084E 36 E8         [10] 1089 	ld	(hl), #<(_g_animKick)
   0850 23            [ 6] 1090 	inc	hl
   0851 36 02         [10] 1091 	ld	(hl), #>(_g_animKick)
   0853 18 10         [12] 1092 	jr	00109$
                           1093 ;src/entities/entities.c:298: case es_win:         { anim->frames = (TAnimFrame**)g_animWin;       break;  }
   0855                    1094 00107$:
   0855 6B            [ 4] 1095 	ld	l, e
   0856 62            [ 4] 1096 	ld	h, d
   0857 36 F4         [10] 1097 	ld	(hl), #<(_g_animWin)
   0859 23            [ 6] 1098 	inc	hl
   085A 36 02         [10] 1099 	ld	(hl), #>(_g_animWin)
   085C 18 07         [12] 1100 	jr	00109$
                           1101 ;src/entities/entities.c:299: case es_hit:         { anim->frames = (TAnimFrame**)g_animHit;       break;  }
   085E                    1102 00108$:
   085E 6B            [ 4] 1103 	ld	l, e
   085F 62            [ 4] 1104 	ld	h, d
   0860 36 EE         [10] 1105 	ld	(hl), #<(_g_animHit)
   0862 23            [ 6] 1106 	inc	hl
   0863 36 02         [10] 1107 	ld	(hl), #>(_g_animHit)
                           1108 ;src/entities/entities.c:300: }
   0865                    1109 00109$:
                           1110 ;src/entities/entities.c:303: anim->status=as_play;
   0865 E1            [10] 1111 	pop	hl
   0866 E5            [11] 1112 	push	hl
   0867 36 00         [10] 1113 	ld	(hl), #0x00
                           1114 ;src/entities/entities.c:304: anim->frame_id = 0xFF;
   0869 6B            [ 4] 1115 	ld	l, e
   086A 62            [ 4] 1116 	ld	h, d
   086B 23            [ 6] 1117 	inc	hl
   086C 23            [ 6] 1118 	inc	hl
   086D 36 FF         [10] 1119 	ld	(hl), #0xff
                           1120 ;src/entities/entities.c:305: anim->time = 1;
   086F 13            [ 6] 1121 	inc	de
   0870 13            [ 6] 1122 	inc	de
   0871 13            [ 6] 1123 	inc	de
   0872 62            [ 4] 1124 	ld	h, d
   0873 6B            [ 4] 1125 	ld	l, e
   0874 36 01         [10] 1126 	ld	(hl), #0x01
   0876                    1127 00112$:
   0876 DD F9         [10] 1128 	ld	sp, ix
   0878 DD E1         [14] 1129 	pop	ix
   087A C9            [10] 1130 	ret
                           1131 ;src/entities/entities.c:312: void drawEntity  (TEntity* ent){
                           1132 ;	---------------------------------
                           1133 ; Function drawEntity
                           1134 ; ---------------------------------
   087B                    1135 _drawEntity::
   087B DD E5         [15] 1136 	push	ix
   087D DD 21 00 00   [14] 1137 	ld	ix,#0
   0881 DD 39         [15] 1138 	add	ix,sp
   0883 F5            [11] 1139 	push	af
                           1140 ;src/entities/entities.c:314: TAnimation* anim  = ent->anim;
   0884 DD 5E 04      [19] 1141 	ld	e,4 (ix)
   0887 DD 56 05      [19] 1142 	ld	d,5 (ix)
   088A 6B            [ 4] 1143 	ld	l, e
   088B 62            [ 4] 1144 	ld	h, d
   088C 7E            [ 7] 1145 	ld	a, (hl)
   088D 23            [ 6] 1146 	inc	hl
   088E 66            [ 7] 1147 	ld	h, (hl)
   088F 6F            [ 4] 1148 	ld	l, a
                           1149 ;src/entities/entities.c:315: TAnimFrame* frame = anim->frames[anim->frame_id];
   0890 E5            [11] 1150 	push	hl
   0891 4E            [ 7] 1151 	ld	c, (hl)
   0892 23            [ 6] 1152 	inc	hl
   0893 46            [ 7] 1153 	ld	b, (hl)
   0894 E1            [10] 1154 	pop	hl
   0895 23            [ 6] 1155 	inc	hl
   0896 23            [ 6] 1156 	inc	hl
   0897 6E            [ 7] 1157 	ld	l, (hl)
   0898 26 00         [ 7] 1158 	ld	h, #0x00
   089A 29            [11] 1159 	add	hl, hl
   089B 09            [11] 1160 	add	hl, bc
   089C 4E            [ 7] 1161 	ld	c, (hl)
   089D 23            [ 6] 1162 	inc	hl
   089E 46            [ 7] 1163 	ld	b, (hl)
                           1164 ;src/entities/entities.c:318: cpct_drawSprite(frame->sprite, ent->videopos, frame->width, frame->height);
   089F C5            [11] 1165 	push	bc
   08A0 FD E1         [14] 1166 	pop	iy
   08A2 FD 7E 03      [19] 1167 	ld	a, 3 (iy)
   08A5 DD 77 FF      [19] 1168 	ld	-1 (ix), a
   08A8 69            [ 4] 1169 	ld	l, c
   08A9 60            [ 4] 1170 	ld	h, b
   08AA 23            [ 6] 1171 	inc	hl
   08AB 23            [ 6] 1172 	inc	hl
   08AC 7E            [ 7] 1173 	ld	a, (hl)
   08AD DD 77 FE      [19] 1174 	ld	-2 (ix), a
   08B0 EB            [ 4] 1175 	ex	de,hl
   08B1 23            [ 6] 1176 	inc	hl
   08B2 23            [ 6] 1177 	inc	hl
   08B3 5E            [ 7] 1178 	ld	e, (hl)
   08B4 23            [ 6] 1179 	inc	hl
   08B5 56            [ 7] 1180 	ld	d, (hl)
   08B6 69            [ 4] 1181 	ld	l, c
   08B7 60            [ 4] 1182 	ld	h, b
   08B8 4E            [ 7] 1183 	ld	c, (hl)
   08B9 23            [ 6] 1184 	inc	hl
   08BA 46            [ 7] 1185 	ld	b, (hl)
   08BB DD 66 FF      [19] 1186 	ld	h, -1 (ix)
   08BE DD 6E FE      [19] 1187 	ld	l, -2 (ix)
   08C1 E5            [11] 1188 	push	hl
   08C2 D5            [11] 1189 	push	de
   08C3 C5            [11] 1190 	push	bc
   08C4 CD 1B 13      [17] 1191 	call	_cpct_drawSprite
   08C7 DD F9         [10] 1192 	ld	sp, ix
   08C9 DD E1         [14] 1193 	pop	ix
   08CB C9            [10] 1194 	ret
                           1195 	.area _CODE
                           1196 	.area _INITIALIZER
                           1197 	.area _CABS (ABS)
