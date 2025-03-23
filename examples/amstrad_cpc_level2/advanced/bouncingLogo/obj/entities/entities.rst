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
                             11 	.globl _cpct_getScreenPtr
                             12 	.globl _g_gravity
                             13 	.globl _moveEntityX
                             14 	.globl _moveEntityY
                             15 	.globl _entityPhysicsUpdate
                             16 	.globl _updateEntities
                             17 ;--------------------------------------------------------
                             18 ; special function registers
                             19 ;--------------------------------------------------------
                             20 ;--------------------------------------------------------
                             21 ; ram data
                             22 ;--------------------------------------------------------
                             23 	.area _DATA
   5242                      24 _g_gravity::
   5242                      25 	.ds 4
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
                             50 ;src/entities/entities.c:38: i8 moveEntityX (TEntity* ent, i8 mx, u8 sx) {
                             51 ;	---------------------------------
                             52 ; Function moveEntityX
                             53 ; ---------------------------------
   43B0                      54 _moveEntityX::
   43B0 DD E5         [15]   55 	push	ix
   43B2 DD 21 00 00   [14]   56 	ld	ix,#0
   43B6 DD 39         [15]   57 	add	ix,sp
   43B8 21 F2 FF      [10]   58 	ld	hl, #-14
   43BB 39            [11]   59 	add	hl, sp
   43BC F9            [ 6]   60 	ld	sp, hl
                             61 ;src/entities/entities.c:39: i8 bounced = 0;
   43BD DD 36 F3 00   [19]   62 	ld	-13 (ix), #0x00
                             63 ;src/entities/entities.c:47: if (umx <= ent->x) {
   43C1 DD 7E 04      [19]   64 	ld	a, 4 (ix)
   43C4 DD 77 FE      [19]   65 	ld	-2 (ix), a
   43C7 DD 7E 05      [19]   66 	ld	a, 5 (ix)
   43CA DD 77 FF      [19]   67 	ld	-1 (ix), a
                             68 ;src/entities/entities.c:49: ent->videopos -= umx;
   43CD DD 7E FE      [19]   69 	ld	a, -2 (ix)
   43D0 C6 02         [ 7]   70 	add	a, #0x02
   43D2 DD 77 FC      [19]   71 	ld	-4 (ix), a
   43D5 DD 7E FF      [19]   72 	ld	a, -1 (ix)
   43D8 CE 00         [ 7]   73 	adc	a, #0x00
   43DA DD 77 FD      [19]   74 	ld	-3 (ix), a
                             75 ;src/entities/entities.c:47: if (umx <= ent->x) {
   43DD DD 7E FE      [19]   76 	ld	a, -2 (ix)
   43E0 C6 04         [ 7]   77 	add	a, #0x04
   43E2 DD 77 FA      [19]   78 	ld	-6 (ix), a
   43E5 DD 7E FF      [19]   79 	ld	a, -1 (ix)
   43E8 CE 00         [ 7]   80 	adc	a, #0x00
   43EA DD 77 FB      [19]   81 	ld	-5 (ix), a
                             82 ;src/entities/entities.c:42: if (mx < 0) {
   43ED DD CB 06 7E   [20]   83 	bit	7, 6 (ix)
   43F1 CA 85 44      [10]   84 	jp	Z, 00110$
                             85 ;src/entities/entities.c:44: u8 umx = -mx;
   43F4 AF            [ 4]   86 	xor	a, a
   43F5 DD 96 06      [19]   87 	sub	a, 6 (ix)
   43F8 DD 77 F2      [19]   88 	ld	-14 (ix), a
                             89 ;src/entities/entities.c:47: if (umx <= ent->x) {
   43FB DD 6E FA      [19]   90 	ld	l,-6 (ix)
   43FE DD 66 FB      [19]   91 	ld	h,-5 (ix)
   4401 7E            [ 7]   92 	ld	a, (hl)
   4402 DD 77 F9      [19]   93 	ld	-7 (ix), a
   4405 DD 96 F2      [19]   94 	sub	a, -14 (ix)
   4408 38 50         [12]   95 	jr	C,00102$
                             96 ;src/entities/entities.c:48: ent->x        -= umx;
   440A DD 7E F9      [19]   97 	ld	a, -7 (ix)
   440D DD 96 F2      [19]   98 	sub	a, -14 (ix)
   4410 DD 77 F8      [19]   99 	ld	-8 (ix), a
   4413 DD 6E FA      [19]  100 	ld	l,-6 (ix)
   4416 DD 66 FB      [19]  101 	ld	h,-5 (ix)
   4419 DD 7E F8      [19]  102 	ld	a, -8 (ix)
   441C 77            [ 7]  103 	ld	(hl), a
                            104 ;src/entities/entities.c:49: ent->videopos -= umx;
   441D DD 6E FC      [19]  105 	ld	l,-4 (ix)
   4420 DD 66 FD      [19]  106 	ld	h,-3 (ix)
   4423 7E            [ 7]  107 	ld	a, (hl)
   4424 DD 77 F6      [19]  108 	ld	-10 (ix), a
   4427 23            [ 6]  109 	inc	hl
   4428 7E            [ 7]  110 	ld	a, (hl)
   4429 DD 77 F7      [19]  111 	ld	-9 (ix), a
   442C DD 7E F2      [19]  112 	ld	a, -14 (ix)
   442F DD 77 F4      [19]  113 	ld	-12 (ix), a
   4432 DD 36 F5 00   [19]  114 	ld	-11 (ix), #0x00
   4436 DD 7E F6      [19]  115 	ld	a, -10 (ix)
   4439 DD 96 F4      [19]  116 	sub	a, -12 (ix)
   443C DD 77 F4      [19]  117 	ld	-12 (ix), a
   443F DD 7E F7      [19]  118 	ld	a, -9 (ix)
   4442 DD 9E F5      [19]  119 	sbc	a, -11 (ix)
   4445 DD 77 F5      [19]  120 	ld	-11 (ix), a
   4448 DD 6E FC      [19]  121 	ld	l,-4 (ix)
   444B DD 66 FD      [19]  122 	ld	h,-3 (ix)
   444E DD 7E F4      [19]  123 	ld	a, -12 (ix)
   4451 77            [ 7]  124 	ld	(hl), a
   4452 23            [ 6]  125 	inc	hl
   4453 DD 7E F5      [19]  126 	ld	a, -11 (ix)
   4456 77            [ 7]  127 	ld	(hl), a
   4457 C3 F5 44      [10]  128 	jp	00111$
   445A                     129 00102$:
                            130 ;src/entities/entities.c:52: ent->videopos -= ent->x;
   445A DD 6E FC      [19]  131 	ld	l,-4 (ix)
   445D DD 66 FD      [19]  132 	ld	h,-3 (ix)
   4460 4E            [ 7]  133 	ld	c, (hl)
   4461 23            [ 6]  134 	inc	hl
   4462 46            [ 7]  135 	ld	b, (hl)
   4463 DD 5E F9      [19]  136 	ld	e, -7 (ix)
   4466 16 00         [ 7]  137 	ld	d, #0x00
   4468 79            [ 4]  138 	ld	a, c
   4469 93            [ 4]  139 	sub	a, e
   446A 4F            [ 4]  140 	ld	c, a
   446B 78            [ 4]  141 	ld	a, b
   446C 9A            [ 4]  142 	sbc	a, d
   446D 47            [ 4]  143 	ld	b, a
   446E DD 6E FC      [19]  144 	ld	l,-4 (ix)
   4471 DD 66 FD      [19]  145 	ld	h,-3 (ix)
   4474 71            [ 7]  146 	ld	(hl), c
   4475 23            [ 6]  147 	inc	hl
   4476 70            [ 7]  148 	ld	(hl), b
                            149 ;src/entities/entities.c:53: ent->x         = 0;
   4477 DD 6E FA      [19]  150 	ld	l,-6 (ix)
   447A DD 66 FB      [19]  151 	ld	h,-5 (ix)
   447D 36 00         [10]  152 	ld	(hl), #0x00
                            153 ;src/entities/entities.c:54: bounced = 1;
   447F DD 36 F3 01   [19]  154 	ld	-13 (ix), #0x01
   4483 18 70         [12]  155 	jr	00111$
   4485                     156 00110$:
                            157 ;src/entities/entities.c:57: } else if (mx) {
   4485 DD 7E 06      [19]  158 	ld	a, 6 (ix)
   4488 B7            [ 4]  159 	or	a, a
   4489 28 6A         [12]  160 	jr	Z,00111$
                            161 ;src/entities/entities.c:59: u8 space_left = sx - ent->width - ent->x;
   448B DD 6E FE      [19]  162 	ld	l,-2 (ix)
   448E DD 66 FF      [19]  163 	ld	h,-1 (ix)
   4491 11 06 00      [10]  164 	ld	de, #0x0006
   4494 19            [11]  165 	add	hl, de
   4495 DD 7E 07      [19]  166 	ld	a,7 (ix)
   4498 96            [ 7]  167 	sub	a,(hl)
   4499 4F            [ 4]  168 	ld	c, a
   449A DD 6E FA      [19]  169 	ld	l,-6 (ix)
   449D DD 66 FB      [19]  170 	ld	h,-5 (ix)
   44A0 6E            [ 7]  171 	ld	l, (hl)
   44A1 79            [ 4]  172 	ld	a, c
   44A2 95            [ 4]  173 	sub	a, l
   44A3 4F            [ 4]  174 	ld	c, a
                            175 ;src/entities/entities.c:60: u8 umx = mx;
   44A4 DD 5E 06      [19]  176 	ld	e, 6 (ix)
                            177 ;src/entities/entities.c:63: if (umx > space_left) {
   44A7 79            [ 4]  178 	ld	a, c
   44A8 93            [ 4]  179 	sub	a, e
   44A9 30 28         [12]  180 	jr	NC,00105$
                            181 ;src/entities/entities.c:65: ent->x        += space_left;
   44AB 7D            [ 4]  182 	ld	a, l
   44AC 81            [ 4]  183 	add	a, c
   44AD DD 6E FA      [19]  184 	ld	l,-6 (ix)
   44B0 DD 66 FB      [19]  185 	ld	h,-5 (ix)
   44B3 77            [ 7]  186 	ld	(hl), a
                            187 ;src/entities/entities.c:66: ent->videopos += space_left;
   44B4 DD 6E FC      [19]  188 	ld	l,-4 (ix)
   44B7 DD 66 FD      [19]  189 	ld	h,-3 (ix)
   44BA 5E            [ 7]  190 	ld	e, (hl)
   44BB 23            [ 6]  191 	inc	hl
   44BC 46            [ 7]  192 	ld	b, (hl)
   44BD 7B            [ 4]  193 	ld	a, e
   44BE 81            [ 4]  194 	add	a, c
   44BF 4F            [ 4]  195 	ld	c, a
   44C0 78            [ 4]  196 	ld	a, b
   44C1 CE 00         [ 7]  197 	adc	a, #0x00
   44C3 47            [ 4]  198 	ld	b, a
   44C4 DD 6E FC      [19]  199 	ld	l,-4 (ix)
   44C7 DD 66 FD      [19]  200 	ld	h,-3 (ix)
   44CA 71            [ 7]  201 	ld	(hl), c
   44CB 23            [ 6]  202 	inc	hl
   44CC 70            [ 7]  203 	ld	(hl), b
                            204 ;src/entities/entities.c:67: bounced = 1;
   44CD DD 36 F3 01   [19]  205 	ld	-13 (ix), #0x01
   44D1 18 22         [12]  206 	jr	00111$
   44D3                     207 00105$:
                            208 ;src/entities/entities.c:69: ent->x        += umx;
   44D3 7D            [ 4]  209 	ld	a, l
   44D4 83            [ 4]  210 	add	a, e
   44D5 DD 6E FA      [19]  211 	ld	l,-6 (ix)
   44D8 DD 66 FB      [19]  212 	ld	h,-5 (ix)
   44DB 77            [ 7]  213 	ld	(hl), a
                            214 ;src/entities/entities.c:70: ent->videopos += umx;
   44DC DD 6E FC      [19]  215 	ld	l,-4 (ix)
   44DF DD 66 FD      [19]  216 	ld	h,-3 (ix)
   44E2 4E            [ 7]  217 	ld	c, (hl)
   44E3 23            [ 6]  218 	inc	hl
   44E4 46            [ 7]  219 	ld	b, (hl)
   44E5 79            [ 4]  220 	ld	a, c
   44E6 83            [ 4]  221 	add	a, e
   44E7 4F            [ 4]  222 	ld	c, a
   44E8 78            [ 4]  223 	ld	a, b
   44E9 CE 00         [ 7]  224 	adc	a, #0x00
   44EB 47            [ 4]  225 	ld	b, a
   44EC DD 6E FC      [19]  226 	ld	l,-4 (ix)
   44EF DD 66 FD      [19]  227 	ld	h,-3 (ix)
   44F2 71            [ 7]  228 	ld	(hl), c
   44F3 23            [ 6]  229 	inc	hl
   44F4 70            [ 7]  230 	ld	(hl), b
   44F5                     231 00111$:
                            232 ;src/entities/entities.c:75: return bounced;
   44F5 DD 6E F3      [19]  233 	ld	l, -13 (ix)
   44F8 DD F9         [10]  234 	ld	sp, ix
   44FA DD E1         [14]  235 	pop	ix
   44FC C9            [10]  236 	ret
                            237 ;src/entities/entities.c:87: i8 moveEntityY (TEntity* ent, i8 my, u8 sy) {
                            238 ;	---------------------------------
                            239 ; Function moveEntityY
                            240 ; ---------------------------------
   44FD                     241 _moveEntityY::
   44FD DD E5         [15]  242 	push	ix
   44FF DD 21 00 00   [14]  243 	ld	ix,#0
   4503 DD 39         [15]  244 	add	ix,sp
   4505 21 F8 FF      [10]  245 	ld	hl, #-8
   4508 39            [11]  246 	add	hl, sp
   4509 F9            [ 6]  247 	ld	sp, hl
                            248 ;src/entities/entities.c:88: i8 bounced = 0;
   450A 0E 00         [ 7]  249 	ld	c, #0x00
                            250 ;src/entities/entities.c:96: if (umy <= ent->y) {
   450C DD 5E 04      [19]  251 	ld	e,4 (ix)
   450F DD 56 05      [19]  252 	ld	d,5 (ix)
                            253 ;src/entities/entities.c:98: ent->videopos  = cpct_getScreenPtr(CPCT_VMEM_START, ent->x, 2*ent->y);
   4512 21 02 00      [10]  254 	ld	hl, #0x0002
   4515 19            [11]  255 	add	hl,de
   4516 DD 75 FE      [19]  256 	ld	-2 (ix), l
   4519 DD 74 FF      [19]  257 	ld	-1 (ix), h
   451C 21 04 00      [10]  258 	ld	hl, #0x0004
   451F 19            [11]  259 	add	hl,de
   4520 DD 75 FA      [19]  260 	ld	-6 (ix), l
   4523 DD 74 FB      [19]  261 	ld	-5 (ix), h
                            262 ;src/entities/entities.c:96: if (umy <= ent->y) {
   4526 21 05 00      [10]  263 	ld	hl, #0x0005
   4529 19            [11]  264 	add	hl,de
   452A DD 75 FC      [19]  265 	ld	-4 (ix), l
   452D DD 74 FD      [19]  266 	ld	-3 (ix), h
                            267 ;src/entities/entities.c:91: if (my < 0) {
   4530 DD CB 06 7E   [20]  268 	bit	7, 6 (ix)
   4534 28 59         [12]  269 	jr	Z,00110$
                            270 ;src/entities/entities.c:93: u8 umy = -my;
   4536 AF            [ 4]  271 	xor	a, a
   4537 DD 96 06      [19]  272 	sub	a, 6 (ix)
   453A 47            [ 4]  273 	ld	b, a
                            274 ;src/entities/entities.c:96: if (umy <= ent->y) {
   453B DD 6E FC      [19]  275 	ld	l,-4 (ix)
   453E DD 66 FD      [19]  276 	ld	h,-3 (ix)
                            277 ;src/entities/entities.c:97: ent->y        -= umy;
   4541 7E            [ 7]  278 	ld	a, (hl)
   4542 B8            [ 4]  279 	cp	a,b
   4543 38 29         [12]  280 	jr	C,00102$
   4545 90            [ 4]  281 	sub	a, b
   4546 DD 6E FC      [19]  282 	ld	l,-4 (ix)
   4549 DD 66 FD      [19]  283 	ld	h,-3 (ix)
   454C 77            [ 7]  284 	ld	(hl), a
                            285 ;src/entities/entities.c:98: ent->videopos  = cpct_getScreenPtr(CPCT_VMEM_START, ent->x, 2*ent->y);
   454D 87            [ 4]  286 	add	a, a
   454E 57            [ 4]  287 	ld	d, a
   454F DD 6E FA      [19]  288 	ld	l,-6 (ix)
   4552 DD 66 FB      [19]  289 	ld	h,-5 (ix)
   4555 46            [ 7]  290 	ld	b, (hl)
   4556 C5            [11]  291 	push	bc
   4557 58            [ 4]  292 	ld	e, b
   4558 D5            [11]  293 	push	de
   4559 21 00 C0      [10]  294 	ld	hl, #0xc000
   455C E5            [11]  295 	push	hl
   455D CD F1 51      [17]  296 	call	_cpct_getScreenPtr
   4560 EB            [ 4]  297 	ex	de,hl
   4561 C1            [10]  298 	pop	bc
   4562 DD 6E FE      [19]  299 	ld	l,-2 (ix)
   4565 DD 66 FF      [19]  300 	ld	h,-1 (ix)
   4568 73            [ 7]  301 	ld	(hl), e
   4569 23            [ 6]  302 	inc	hl
   456A 72            [ 7]  303 	ld	(hl), d
   456B C3 F0 45      [10]  304 	jp	00111$
   456E                     305 00102$:
                            306 ;src/entities/entities.c:101: ent->videopos  = CPCT_VMEM_START + ent->x;
   456E DD 6E FA      [19]  307 	ld	l,-6 (ix)
   4571 DD 66 FB      [19]  308 	ld	h,-5 (ix)
   4574 4E            [ 7]  309 	ld	c, (hl)
   4575 3E 00         [ 7]  310 	ld	a,#0x00
   4577 C6 C0         [ 7]  311 	add	a,#0xc0
   4579 47            [ 4]  312 	ld	b, a
   457A DD 6E FE      [19]  313 	ld	l,-2 (ix)
   457D DD 66 FF      [19]  314 	ld	h,-1 (ix)
   4580 71            [ 7]  315 	ld	(hl), c
   4581 23            [ 6]  316 	inc	hl
   4582 70            [ 7]  317 	ld	(hl), b
                            318 ;src/entities/entities.c:102: ent->y         = 0;
   4583 DD 6E FC      [19]  319 	ld	l,-4 (ix)
   4586 DD 66 FD      [19]  320 	ld	h,-3 (ix)
   4589 36 00         [10]  321 	ld	(hl), #0x00
                            322 ;src/entities/entities.c:103: bounced = 1;
   458B 0E 01         [ 7]  323 	ld	c, #0x01
   458D 18 61         [12]  324 	jr	00111$
   458F                     325 00110$:
                            326 ;src/entities/entities.c:106: } else if (my) {
   458F DD 7E 06      [19]  327 	ld	a, 6 (ix)
   4592 B7            [ 4]  328 	or	a, a
   4593 28 5B         [12]  329 	jr	Z,00111$
                            330 ;src/entities/entities.c:108: u8 space_left = sy - (ent->height>>1) - ent->y;
   4595 33            [ 6]  331 	inc	sp
   4596 33            [ 6]  332 	inc	sp
   4597 D5            [11]  333 	push	de
   4598 E1            [10]  334 	pop	hl
   4599 E5            [11]  335 	push	hl
   459A 11 07 00      [10]  336 	ld	de, #0x0007
   459D 19            [11]  337 	add	hl, de
   459E 46            [ 7]  338 	ld	b, (hl)
   459F CB 38         [ 8]  339 	srl	b
   45A1 DD 7E 07      [19]  340 	ld	a, 7 (ix)
   45A4 90            [ 4]  341 	sub	a, b
   45A5 5F            [ 4]  342 	ld	e, a
   45A6 DD 6E FC      [19]  343 	ld	l,-4 (ix)
   45A9 DD 66 FD      [19]  344 	ld	h,-3 (ix)
   45AC 46            [ 7]  345 	ld	b, (hl)
   45AD 7B            [ 4]  346 	ld	a, e
   45AE 90            [ 4]  347 	sub	a, b
   45AF 6F            [ 4]  348 	ld	l, a
                            349 ;src/entities/entities.c:109: u8 umy = my;
   45B0 DD 56 06      [19]  350 	ld	d, 6 (ix)
                            351 ;src/entities/entities.c:112: if (umy > space_left) {
   45B3 7D            [ 4]  352 	ld	a, l
   45B4 92            [ 4]  353 	sub	a, d
   45B5 30 0B         [12]  354 	jr	NC,00105$
                            355 ;src/entities/entities.c:114: ent->y  = sy - (ent->height>>1);
   45B7 DD 6E FC      [19]  356 	ld	l,-4 (ix)
   45BA DD 66 FD      [19]  357 	ld	h,-3 (ix)
   45BD 73            [ 7]  358 	ld	(hl), e
                            359 ;src/entities/entities.c:115: bounced = 1;
   45BE 0E 01         [ 7]  360 	ld	c, #0x01
   45C0 18 09         [12]  361 	jr	00106$
   45C2                     362 00105$:
                            363 ;src/entities/entities.c:117: ent->y += umy;
   45C2 78            [ 4]  364 	ld	a, b
   45C3 82            [ 4]  365 	add	a, d
   45C4 DD 6E FC      [19]  366 	ld	l,-4 (ix)
   45C7 DD 66 FD      [19]  367 	ld	h,-3 (ix)
   45CA 77            [ 7]  368 	ld	(hl), a
   45CB                     369 00106$:
                            370 ;src/entities/entities.c:120: ent->videopos = cpct_getScreenPtr(CPCT_VMEM_START, ent->x, 2*ent->y);
   45CB DD 6E FC      [19]  371 	ld	l,-4 (ix)
   45CE DD 66 FD      [19]  372 	ld	h,-3 (ix)
   45D1 46            [ 7]  373 	ld	b, (hl)
   45D2 CB 20         [ 8]  374 	sla	b
   45D4 DD 6E FA      [19]  375 	ld	l,-6 (ix)
   45D7 DD 66 FB      [19]  376 	ld	h,-5 (ix)
   45DA 56            [ 7]  377 	ld	d, (hl)
   45DB C5            [11]  378 	push	bc
   45DC 4A            [ 4]  379 	ld	c, d
   45DD C5            [11]  380 	push	bc
   45DE 21 00 C0      [10]  381 	ld	hl, #0xc000
   45E1 E5            [11]  382 	push	hl
   45E2 CD F1 51      [17]  383 	call	_cpct_getScreenPtr
   45E5 EB            [ 4]  384 	ex	de,hl
   45E6 C1            [10]  385 	pop	bc
   45E7 DD 6E FE      [19]  386 	ld	l,-2 (ix)
   45EA DD 66 FF      [19]  387 	ld	h,-1 (ix)
   45ED 73            [ 7]  388 	ld	(hl), e
   45EE 23            [ 6]  389 	inc	hl
   45EF 72            [ 7]  390 	ld	(hl), d
   45F0                     391 00111$:
                            392 ;src/entities/entities.c:123: return bounced;
   45F0 69            [ 4]  393 	ld	l, c
   45F1 DD F9         [10]  394 	ld	sp, ix
   45F3 DD E1         [14]  395 	pop	ix
   45F5 C9            [10]  396 	ret
                            397 ;src/entities/entities.c:133: void entityPhysicsUpdate (TVelocity *vel, f32 ax, f32 ay) {
                            398 ;	---------------------------------
                            399 ; Function entityPhysicsUpdate
                            400 ; ---------------------------------
   45F6                     401 _entityPhysicsUpdate::
   45F6 DD E5         [15]  402 	push	ix
   45F8 DD 21 00 00   [14]  403 	ld	ix,#0
   45FC DD 39         [15]  404 	add	ix,sp
   45FE 21 F4 FF      [10]  405 	ld	hl, #-12
   4601 39            [11]  406 	add	hl, sp
   4602 F9            [ 6]  407 	ld	sp, hl
                            408 ;src/entities/entities.c:135: vel->vx += ax;
   4603 DD 7E 04      [19]  409 	ld	a, 4 (ix)
   4606 DD 77 FE      [19]  410 	ld	-2 (ix), a
   4609 DD 7E 05      [19]  411 	ld	a, 5 (ix)
   460C DD 77 FF      [19]  412 	ld	-1 (ix), a
   460F DD 6E FE      [19]  413 	ld	l,-2 (ix)
   4612 DD 66 FF      [19]  414 	ld	h,-1 (ix)
   4615 4E            [ 7]  415 	ld	c, (hl)
   4616 23            [ 6]  416 	inc	hl
   4617 46            [ 7]  417 	ld	b, (hl)
   4618 23            [ 6]  418 	inc	hl
   4619 5E            [ 7]  419 	ld	e, (hl)
   461A 23            [ 6]  420 	inc	hl
   461B 56            [ 7]  421 	ld	d, (hl)
   461C DD 6E 08      [19]  422 	ld	l,8 (ix)
   461F DD 66 09      [19]  423 	ld	h,9 (ix)
   4622 E5            [11]  424 	push	hl
   4623 DD 6E 06      [19]  425 	ld	l,6 (ix)
   4626 DD 66 07      [19]  426 	ld	h,7 (ix)
   4629 E5            [11]  427 	push	hl
   462A D5            [11]  428 	push	de
   462B C5            [11]  429 	push	bc
   462C CD D6 57      [17]  430 	call	___fsadd
   462F F1            [10]  431 	pop	af
   4630 F1            [10]  432 	pop	af
   4631 F1            [10]  433 	pop	af
   4632 F1            [10]  434 	pop	af
   4633 DD 72 F7      [19]  435 	ld	-9 (ix), d
   4636 DD 73 F6      [19]  436 	ld	-10 (ix), e
   4639 DD 74 F5      [19]  437 	ld	-11 (ix), h
   463C DD 75 F4      [19]  438 	ld	-12 (ix), l
   463F DD 5E FE      [19]  439 	ld	e,-2 (ix)
   4642 DD 56 FF      [19]  440 	ld	d,-1 (ix)
   4645 21 00 00      [10]  441 	ld	hl, #0x0000
   4648 39            [11]  442 	add	hl, sp
   4649 01 04 00      [10]  443 	ld	bc, #0x0004
   464C ED B0         [21]  444 	ldir
                            445 ;src/entities/entities.c:136: vel->vy += ay;
   464E DD 7E FE      [19]  446 	ld	a, -2 (ix)
   4651 C6 04         [ 7]  447 	add	a, #0x04
   4653 DD 77 FC      [19]  448 	ld	-4 (ix), a
   4656 DD 7E FF      [19]  449 	ld	a, -1 (ix)
   4659 CE 00         [ 7]  450 	adc	a, #0x00
   465B DD 77 FD      [19]  451 	ld	-3 (ix), a
   465E DD 6E FC      [19]  452 	ld	l,-4 (ix)
   4661 DD 66 FD      [19]  453 	ld	h,-3 (ix)
   4664 4E            [ 7]  454 	ld	c, (hl)
   4665 23            [ 6]  455 	inc	hl
   4666 46            [ 7]  456 	ld	b, (hl)
   4667 23            [ 6]  457 	inc	hl
   4668 5E            [ 7]  458 	ld	e, (hl)
   4669 23            [ 6]  459 	inc	hl
   466A 56            [ 7]  460 	ld	d, (hl)
   466B DD 6E 0C      [19]  461 	ld	l,12 (ix)
   466E DD 66 0D      [19]  462 	ld	h,13 (ix)
   4671 E5            [11]  463 	push	hl
   4672 DD 6E 0A      [19]  464 	ld	l,10 (ix)
   4675 DD 66 0B      [19]  465 	ld	h,11 (ix)
   4678 E5            [11]  466 	push	hl
   4679 D5            [11]  467 	push	de
   467A C5            [11]  468 	push	bc
   467B CD D6 57      [17]  469 	call	___fsadd
   467E F1            [10]  470 	pop	af
   467F F1            [10]  471 	pop	af
   4680 F1            [10]  472 	pop	af
   4681 F1            [10]  473 	pop	af
   4682 4D            [ 4]  474 	ld	c, l
   4683 44            [ 4]  475 	ld	b, h
   4684 DD 6E FC      [19]  476 	ld	l,-4 (ix)
   4687 DD 66 FD      [19]  477 	ld	h,-3 (ix)
   468A 71            [ 7]  478 	ld	(hl), c
   468B 23            [ 6]  479 	inc	hl
   468C 70            [ 7]  480 	ld	(hl), b
   468D 23            [ 6]  481 	inc	hl
   468E 73            [ 7]  482 	ld	(hl), e
   468F 23            [ 6]  483 	inc	hl
   4690 72            [ 7]  484 	ld	(hl), d
                            485 ;src/entities/entities.c:139: vel->vy += g_gravity;
   4691 2A 44 52      [16]  486 	ld	hl, (_g_gravity + 2)
   4694 E5            [11]  487 	push	hl
   4695 2A 42 52      [16]  488 	ld	hl, (_g_gravity)
   4698 E5            [11]  489 	push	hl
   4699 D5            [11]  490 	push	de
   469A C5            [11]  491 	push	bc
   469B CD D6 57      [17]  492 	call	___fsadd
   469E F1            [10]  493 	pop	af
   469F F1            [10]  494 	pop	af
   46A0 F1            [10]  495 	pop	af
   46A1 F1            [10]  496 	pop	af
   46A2 4D            [ 4]  497 	ld	c, l
   46A3 44            [ 4]  498 	ld	b, h
   46A4 DD 6E FC      [19]  499 	ld	l,-4 (ix)
   46A7 DD 66 FD      [19]  500 	ld	h,-3 (ix)
   46AA 71            [ 7]  501 	ld	(hl), c
   46AB 23            [ 6]  502 	inc	hl
   46AC 70            [ 7]  503 	ld	(hl), b
   46AD 23            [ 6]  504 	inc	hl
   46AE 73            [ 7]  505 	ld	(hl), e
   46AF 23            [ 6]  506 	inc	hl
   46B0 72            [ 7]  507 	ld	(hl), d
                            508 ;src/entities/entities.c:142: if      (vel->vx >  vel->max_x) vel->vx= vel->max_x;
   46B1 DD 6E FE      [19]  509 	ld	l,-2 (ix)
   46B4 DD 66 FF      [19]  510 	ld	h,-1 (ix)
   46B7 4E            [ 7]  511 	ld	c, (hl)
   46B8 23            [ 6]  512 	inc	hl
   46B9 46            [ 7]  513 	ld	b, (hl)
   46BA 23            [ 6]  514 	inc	hl
   46BB 5E            [ 7]  515 	ld	e, (hl)
   46BC 23            [ 6]  516 	inc	hl
   46BD 56            [ 7]  517 	ld	d, (hl)
   46BE DD 6E FE      [19]  518 	ld	l,-2 (ix)
   46C1 DD 66 FF      [19]  519 	ld	h,-1 (ix)
   46C4 C5            [11]  520 	push	bc
   46C5 01 10 00      [10]  521 	ld	bc, #0x0010
   46C8 09            [11]  522 	add	hl, bc
   46C9 C1            [10]  523 	pop	bc
   46CA 7E            [ 7]  524 	ld	a, (hl)
   46CB DD 77 F8      [19]  525 	ld	-8 (ix), a
   46CE 23            [ 6]  526 	inc	hl
   46CF 7E            [ 7]  527 	ld	a, (hl)
   46D0 DD 77 F9      [19]  528 	ld	-7 (ix), a
   46D3 23            [ 6]  529 	inc	hl
   46D4 7E            [ 7]  530 	ld	a, (hl)
   46D5 DD 77 FA      [19]  531 	ld	-6 (ix), a
   46D8 23            [ 6]  532 	inc	hl
   46D9 7E            [ 7]  533 	ld	a, (hl)
   46DA DD 77 FB      [19]  534 	ld	-5 (ix), a
   46DD C5            [11]  535 	push	bc
   46DE D5            [11]  536 	push	de
   46DF DD 6E FA      [19]  537 	ld	l,-6 (ix)
   46E2 DD 66 FB      [19]  538 	ld	h,-5 (ix)
   46E5 E5            [11]  539 	push	hl
   46E6 DD 6E F8      [19]  540 	ld	l,-8 (ix)
   46E9 DD 66 F9      [19]  541 	ld	h,-7 (ix)
   46EC E5            [11]  542 	push	hl
   46ED DD 6E F6      [19]  543 	ld	l,-10 (ix)
   46F0 DD 66 F7      [19]  544 	ld	h,-9 (ix)
   46F3 E5            [11]  545 	push	hl
   46F4 DD 6E F4      [19]  546 	ld	l,-12 (ix)
   46F7 DD 66 F5      [19]  547 	ld	h,-11 (ix)
   46FA E5            [11]  548 	push	hl
   46FB CD E0 55      [17]  549 	call	___fsgt
   46FE F1            [10]  550 	pop	af
   46FF F1            [10]  551 	pop	af
   4700 F1            [10]  552 	pop	af
   4701 F1            [10]  553 	pop	af
   4702 D1            [10]  554 	pop	de
   4703 C1            [10]  555 	pop	bc
   4704 7D            [ 4]  556 	ld	a, l
   4705 B7            [ 4]  557 	or	a, a
   4706 28 11         [12]  558 	jr	Z,00104$
   4708 DD 5E FE      [19]  559 	ld	e,-2 (ix)
   470B DD 56 FF      [19]  560 	ld	d,-1 (ix)
   470E 21 04 00      [10]  561 	ld	hl, #0x0004
   4711 39            [11]  562 	add	hl, sp
   4712 01 04 00      [10]  563 	ld	bc, #0x0004
   4715 ED B0         [21]  564 	ldir
   4717 18 42         [12]  565 	jr	00105$
   4719                     566 00104$:
                            567 ;src/entities/entities.c:143: else if (vel->vx < -vel->max_x) vel->vx=-vel->max_x;
   4719 DD 7E FB      [19]  568 	ld	a, -5 (ix)
   471C EE 80         [ 7]  569 	xor	a,#0x80
   471E DD 77 FB      [19]  570 	ld	-5 (ix), a
   4721 DD 7E F8      [19]  571 	ld	a, -8 (ix)
   4724 DD 77 F8      [19]  572 	ld	-8 (ix), a
   4727 DD 7E F9      [19]  573 	ld	a, -7 (ix)
   472A DD 77 F9      [19]  574 	ld	-7 (ix), a
   472D DD 7E FA      [19]  575 	ld	a, -6 (ix)
   4730 DD 77 FA      [19]  576 	ld	-6 (ix), a
   4733 6F            [ 4]  577 	ld	l, a
   4734 DD 66 FB      [19]  578 	ld	h,-5 (ix)
   4737 E5            [11]  579 	push	hl
   4738 DD 6E F8      [19]  580 	ld	l,-8 (ix)
   473B DD 66 F9      [19]  581 	ld	h,-7 (ix)
   473E E5            [11]  582 	push	hl
   473F D5            [11]  583 	push	de
   4740 C5            [11]  584 	push	bc
   4741 CD DB 56      [17]  585 	call	___fslt
   4744 F1            [10]  586 	pop	af
   4745 F1            [10]  587 	pop	af
   4746 F1            [10]  588 	pop	af
   4747 F1            [10]  589 	pop	af
   4748 7D            [ 4]  590 	ld	a, l
   4749 B7            [ 4]  591 	or	a, a
   474A 28 0F         [12]  592 	jr	Z,00105$
   474C DD 5E FE      [19]  593 	ld	e,-2 (ix)
   474F DD 56 FF      [19]  594 	ld	d,-1 (ix)
   4752 21 04 00      [10]  595 	ld	hl, #0x0004
   4755 39            [11]  596 	add	hl, sp
   4756 01 04 00      [10]  597 	ld	bc, #0x0004
   4759 ED B0         [21]  598 	ldir
   475B                     599 00105$:
                            600 ;src/entities/entities.c:136: vel->vy += ay;
   475B DD 5E FC      [19]  601 	ld	e,-4 (ix)
   475E DD 56 FD      [19]  602 	ld	d,-3 (ix)
   4761 21 04 00      [10]  603 	ld	hl, #0x0004
   4764 39            [11]  604 	add	hl, sp
   4765 EB            [ 4]  605 	ex	de, hl
   4766 01 04 00      [10]  606 	ld	bc, #0x0004
   4769 ED B0         [21]  607 	ldir
                            608 ;src/entities/entities.c:144: if      (vel->vy >  vel->max_y) vel->vy= vel->max_y;
   476B DD 6E FE      [19]  609 	ld	l,-2 (ix)
   476E DD 66 FF      [19]  610 	ld	h,-1 (ix)
   4771 11 14 00      [10]  611 	ld	de, #0x0014
   4774 19            [11]  612 	add	hl, de
   4775 4E            [ 7]  613 	ld	c, (hl)
   4776 23            [ 6]  614 	inc	hl
   4777 46            [ 7]  615 	ld	b, (hl)
   4778 23            [ 6]  616 	inc	hl
   4779 5E            [ 7]  617 	ld	e, (hl)
   477A 23            [ 6]  618 	inc	hl
   477B 56            [ 7]  619 	ld	d, (hl)
   477C C5            [11]  620 	push	bc
   477D D5            [11]  621 	push	de
   477E D5            [11]  622 	push	de
   477F C5            [11]  623 	push	bc
   4780 DD 6E FA      [19]  624 	ld	l,-6 (ix)
   4783 DD 66 FB      [19]  625 	ld	h,-5 (ix)
   4786 E5            [11]  626 	push	hl
   4787 DD 6E F8      [19]  627 	ld	l,-8 (ix)
   478A DD 66 F9      [19]  628 	ld	h,-7 (ix)
   478D E5            [11]  629 	push	hl
   478E CD E0 55      [17]  630 	call	___fsgt
   4791 F1            [10]  631 	pop	af
   4792 F1            [10]  632 	pop	af
   4793 F1            [10]  633 	pop	af
   4794 F1            [10]  634 	pop	af
   4795 D1            [10]  635 	pop	de
   4796 C1            [10]  636 	pop	bc
   4797 7D            [ 4]  637 	ld	a, l
   4798 B7            [ 4]  638 	or	a, a
   4799 28 0F         [12]  639 	jr	Z,00109$
   479B DD 6E FC      [19]  640 	ld	l,-4 (ix)
   479E DD 66 FD      [19]  641 	ld	h,-3 (ix)
   47A1 71            [ 7]  642 	ld	(hl), c
   47A2 23            [ 6]  643 	inc	hl
   47A3 70            [ 7]  644 	ld	(hl), b
   47A4 23            [ 6]  645 	inc	hl
   47A5 73            [ 7]  646 	ld	(hl), e
   47A6 23            [ 6]  647 	inc	hl
   47A7 72            [ 7]  648 	ld	(hl), d
   47A8 18 30         [12]  649 	jr	00110$
   47AA                     650 00109$:
                            651 ;src/entities/entities.c:145: else if (vel->vy < -vel->max_y) vel->vy=-vel->max_y;
   47AA 7A            [ 4]  652 	ld	a, d
   47AB EE 80         [ 7]  653 	xor	a,#0x80
   47AD 57            [ 4]  654 	ld	d, a
   47AE C5            [11]  655 	push	bc
   47AF D5            [11]  656 	push	de
   47B0 D5            [11]  657 	push	de
   47B1 C5            [11]  658 	push	bc
   47B2 DD 6E FA      [19]  659 	ld	l,-6 (ix)
   47B5 DD 66 FB      [19]  660 	ld	h,-5 (ix)
   47B8 E5            [11]  661 	push	hl
   47B9 DD 6E F8      [19]  662 	ld	l,-8 (ix)
   47BC DD 66 F9      [19]  663 	ld	h,-7 (ix)
   47BF E5            [11]  664 	push	hl
   47C0 CD DB 56      [17]  665 	call	___fslt
   47C3 F1            [10]  666 	pop	af
   47C4 F1            [10]  667 	pop	af
   47C5 F1            [10]  668 	pop	af
   47C6 F1            [10]  669 	pop	af
   47C7 D1            [10]  670 	pop	de
   47C8 C1            [10]  671 	pop	bc
   47C9 7D            [ 4]  672 	ld	a, l
   47CA B7            [ 4]  673 	or	a, a
   47CB 28 0D         [12]  674 	jr	Z,00110$
   47CD DD 6E FC      [19]  675 	ld	l,-4 (ix)
   47D0 DD 66 FD      [19]  676 	ld	h,-3 (ix)
   47D3 71            [ 7]  677 	ld	(hl), c
   47D4 23            [ 6]  678 	inc	hl
   47D5 70            [ 7]  679 	ld	(hl), b
   47D6 23            [ 6]  680 	inc	hl
   47D7 73            [ 7]  681 	ld	(hl), e
   47D8 23            [ 6]  682 	inc	hl
   47D9 72            [ 7]  683 	ld	(hl), d
   47DA                     684 00110$:
                            685 ;src/entities/entities.c:148: vel->acum_x += vel->vx;
   47DA DD 7E FE      [19]  686 	ld	a, -2 (ix)
   47DD C6 08         [ 7]  687 	add	a, #0x08
   47DF DD 77 F8      [19]  688 	ld	-8 (ix), a
   47E2 DD 7E FF      [19]  689 	ld	a, -1 (ix)
   47E5 CE 00         [ 7]  690 	adc	a, #0x00
   47E7 DD 77 F9      [19]  691 	ld	-7 (ix), a
   47EA DD 5E F8      [19]  692 	ld	e,-8 (ix)
   47ED DD 56 F9      [19]  693 	ld	d,-7 (ix)
   47F0 21 00 00      [10]  694 	ld	hl, #0x0000
   47F3 39            [11]  695 	add	hl, sp
   47F4 EB            [ 4]  696 	ex	de, hl
   47F5 01 04 00      [10]  697 	ld	bc, #0x0004
   47F8 ED B0         [21]  698 	ldir
   47FA DD 6E FE      [19]  699 	ld	l,-2 (ix)
   47FD DD 66 FF      [19]  700 	ld	h,-1 (ix)
   4800 4E            [ 7]  701 	ld	c, (hl)
   4801 23            [ 6]  702 	inc	hl
   4802 46            [ 7]  703 	ld	b, (hl)
   4803 23            [ 6]  704 	inc	hl
   4804 5E            [ 7]  705 	ld	e, (hl)
   4805 23            [ 6]  706 	inc	hl
   4806 56            [ 7]  707 	ld	d, (hl)
   4807 D5            [11]  708 	push	de
   4808 C5            [11]  709 	push	bc
   4809 DD 6E F6      [19]  710 	ld	l,-10 (ix)
   480C DD 66 F7      [19]  711 	ld	h,-9 (ix)
   480F E5            [11]  712 	push	hl
   4810 DD 6E F4      [19]  713 	ld	l,-12 (ix)
   4813 DD 66 F5      [19]  714 	ld	h,-11 (ix)
   4816 E5            [11]  715 	push	hl
   4817 CD D6 57      [17]  716 	call	___fsadd
   481A F1            [10]  717 	pop	af
   481B F1            [10]  718 	pop	af
   481C F1            [10]  719 	pop	af
   481D F1            [10]  720 	pop	af
   481E 4D            [ 4]  721 	ld	c, l
   481F 44            [ 4]  722 	ld	b, h
   4820 DD 6E F8      [19]  723 	ld	l,-8 (ix)
   4823 DD 66 F9      [19]  724 	ld	h,-7 (ix)
   4826 71            [ 7]  725 	ld	(hl), c
   4827 23            [ 6]  726 	inc	hl
   4828 70            [ 7]  727 	ld	(hl), b
   4829 23            [ 6]  728 	inc	hl
   482A 73            [ 7]  729 	ld	(hl), e
   482B 23            [ 6]  730 	inc	hl
   482C 72            [ 7]  731 	ld	(hl), d
                            732 ;src/entities/entities.c:149: vel->acum_y += vel->vy;
   482D DD 7E FE      [19]  733 	ld	a, -2 (ix)
   4830 C6 0C         [ 7]  734 	add	a, #0x0c
   4832 DD 77 F8      [19]  735 	ld	-8 (ix), a
   4835 DD 7E FF      [19]  736 	ld	a, -1 (ix)
   4838 CE 00         [ 7]  737 	adc	a, #0x00
   483A DD 77 F9      [19]  738 	ld	-7 (ix), a
   483D DD 5E F8      [19]  739 	ld	e,-8 (ix)
   4840 DD 56 F9      [19]  740 	ld	d,-7 (ix)
   4843 21 00 00      [10]  741 	ld	hl, #0x0000
   4846 39            [11]  742 	add	hl, sp
   4847 EB            [ 4]  743 	ex	de, hl
   4848 01 04 00      [10]  744 	ld	bc, #0x0004
   484B ED B0         [21]  745 	ldir
   484D DD 6E FC      [19]  746 	ld	l,-4 (ix)
   4850 DD 66 FD      [19]  747 	ld	h,-3 (ix)
   4853 4E            [ 7]  748 	ld	c, (hl)
   4854 23            [ 6]  749 	inc	hl
   4855 46            [ 7]  750 	ld	b, (hl)
   4856 23            [ 6]  751 	inc	hl
   4857 5E            [ 7]  752 	ld	e, (hl)
   4858 23            [ 6]  753 	inc	hl
   4859 56            [ 7]  754 	ld	d, (hl)
   485A D5            [11]  755 	push	de
   485B C5            [11]  756 	push	bc
   485C DD 6E F6      [19]  757 	ld	l,-10 (ix)
   485F DD 66 F7      [19]  758 	ld	h,-9 (ix)
   4862 E5            [11]  759 	push	hl
   4863 DD 6E F4      [19]  760 	ld	l,-12 (ix)
   4866 DD 66 F5      [19]  761 	ld	h,-11 (ix)
   4869 E5            [11]  762 	push	hl
   486A CD D6 57      [17]  763 	call	___fsadd
   486D F1            [10]  764 	pop	af
   486E F1            [10]  765 	pop	af
   486F F1            [10]  766 	pop	af
   4870 F1            [10]  767 	pop	af
   4871 4D            [ 4]  768 	ld	c, l
   4872 44            [ 4]  769 	ld	b, h
   4873 DD 6E F8      [19]  770 	ld	l,-8 (ix)
   4876 DD 66 F9      [19]  771 	ld	h,-7 (ix)
   4879 71            [ 7]  772 	ld	(hl), c
   487A 23            [ 6]  773 	inc	hl
   487B 70            [ 7]  774 	ld	(hl), b
   487C 23            [ 6]  775 	inc	hl
   487D 73            [ 7]  776 	ld	(hl), e
   487E 23            [ 6]  777 	inc	hl
   487F 72            [ 7]  778 	ld	(hl), d
   4880 DD F9         [10]  779 	ld	sp, ix
   4882 DD E1         [14]  780 	pop	ix
   4884 C9            [10]  781 	ret
                            782 ;src/entities/entities.c:156: void updateEntities(TEntity *logo, f32 ax, f32 ay) {
                            783 ;	---------------------------------
                            784 ; Function updateEntities
                            785 ; ---------------------------------
   4885                     786 _updateEntities::
   4885 DD E5         [15]  787 	push	ix
   4887 DD 21 00 00   [14]  788 	ld	ix,#0
   488B DD 39         [15]  789 	add	ix,sp
   488D 21 F4 FF      [10]  790 	ld	hl, #-12
   4890 39            [11]  791 	add	hl, sp
   4891 F9            [ 6]  792 	ld	sp, hl
                            793 ;src/entities/entities.c:158: i8 dx=0, dy=0;
   4892 DD 36 F5 00   [19]  794 	ld	-11 (ix), #0x00
   4896 DD 36 F4 00   [19]  795 	ld	-12 (ix), #0x00
                            796 ;src/entities/entities.c:161: entityPhysicsUpdate(&logo->vel, ax, ay);
   489A DD 7E 04      [19]  797 	ld	a, 4 (ix)
   489D DD 77 FE      [19]  798 	ld	-2 (ix), a
   48A0 DD 7E 05      [19]  799 	ld	a, 5 (ix)
   48A3 DD 77 FF      [19]  800 	ld	-1 (ix), a
   48A6 DD 7E FE      [19]  801 	ld	a, -2 (ix)
   48A9 C6 08         [ 7]  802 	add	a, #0x08
   48AB DD 77 F6      [19]  803 	ld	-10 (ix), a
   48AE DD 7E FF      [19]  804 	ld	a, -1 (ix)
   48B1 CE 00         [ 7]  805 	adc	a, #0x00
   48B3 DD 77 F7      [19]  806 	ld	-9 (ix), a
   48B6 DD 6E 0C      [19]  807 	ld	l,12 (ix)
   48B9 DD 66 0D      [19]  808 	ld	h,13 (ix)
   48BC E5            [11]  809 	push	hl
   48BD DD 6E 0A      [19]  810 	ld	l,10 (ix)
   48C0 DD 66 0B      [19]  811 	ld	h,11 (ix)
   48C3 E5            [11]  812 	push	hl
   48C4 DD 6E 08      [19]  813 	ld	l,8 (ix)
   48C7 DD 66 09      [19]  814 	ld	h,9 (ix)
   48CA E5            [11]  815 	push	hl
   48CB DD 6E 06      [19]  816 	ld	l,6 (ix)
   48CE DD 66 07      [19]  817 	ld	h,7 (ix)
   48D1 E5            [11]  818 	push	hl
   48D2 DD 6E F6      [19]  819 	ld	l,-10 (ix)
   48D5 DD 66 F7      [19]  820 	ld	h,-9 (ix)
   48D8 E5            [11]  821 	push	hl
   48D9 CD F6 45      [17]  822 	call	_entityPhysicsUpdate
   48DC 21 0A 00      [10]  823 	ld	hl, #10
   48DF 39            [11]  824 	add	hl, sp
   48E0 F9            [ 6]  825 	ld	sp, hl
                            826 ;src/entities/entities.c:165: if      (logo->vel.acum_x > 1 ) { dx =  1; logo->vel.acum_x-=1.0; }
   48E1 DD 7E FE      [19]  827 	ld	a, -2 (ix)
   48E4 C6 10         [ 7]  828 	add	a, #0x10
   48E6 DD 77 FC      [19]  829 	ld	-4 (ix), a
   48E9 DD 7E FF      [19]  830 	ld	a, -1 (ix)
   48EC CE 00         [ 7]  831 	adc	a, #0x00
   48EE DD 77 FD      [19]  832 	ld	-3 (ix), a
   48F1 DD 5E FC      [19]  833 	ld	e,-4 (ix)
   48F4 DD 56 FD      [19]  834 	ld	d,-3 (ix)
   48F7 21 04 00      [10]  835 	ld	hl, #0x0004
   48FA 39            [11]  836 	add	hl, sp
   48FB EB            [ 4]  837 	ex	de, hl
   48FC 01 04 00      [10]  838 	ld	bc, #0x0004
   48FF ED B0         [21]  839 	ldir
   4901 21 80 3F      [10]  840 	ld	hl, #0x3f80
   4904 E5            [11]  841 	push	hl
   4905 21 00 00      [10]  842 	ld	hl, #0x0000
   4908 E5            [11]  843 	push	hl
   4909 DD 6E FA      [19]  844 	ld	l,-6 (ix)
   490C DD 66 FB      [19]  845 	ld	h,-5 (ix)
   490F E5            [11]  846 	push	hl
   4910 DD 6E F8      [19]  847 	ld	l,-8 (ix)
   4913 DD 66 F9      [19]  848 	ld	h,-7 (ix)
   4916 E5            [11]  849 	push	hl
   4917 CD E0 55      [17]  850 	call	___fsgt
   491A F1            [10]  851 	pop	af
   491B F1            [10]  852 	pop	af
   491C F1            [10]  853 	pop	af
   491D F1            [10]  854 	pop	af
   491E 7D            [ 4]  855 	ld	a, l
   491F B7            [ 4]  856 	or	a, a
   4920 28 32         [12]  857 	jr	Z,00104$
   4922 DD 36 F5 01   [19]  858 	ld	-11 (ix), #0x01
   4926 21 80 3F      [10]  859 	ld	hl, #0x3f80
   4929 E5            [11]  860 	push	hl
   492A 21 00 00      [10]  861 	ld	hl, #0x0000
   492D E5            [11]  862 	push	hl
   492E DD 6E FA      [19]  863 	ld	l,-6 (ix)
   4931 DD 66 FB      [19]  864 	ld	h,-5 (ix)
   4934 E5            [11]  865 	push	hl
   4935 DD 6E F8      [19]  866 	ld	l,-8 (ix)
   4938 DD 66 F9      [19]  867 	ld	h,-7 (ix)
   493B E5            [11]  868 	push	hl
   493C CD 46 52      [17]  869 	call	___fssub
   493F F1            [10]  870 	pop	af
   4940 F1            [10]  871 	pop	af
   4941 F1            [10]  872 	pop	af
   4942 F1            [10]  873 	pop	af
   4943 4D            [ 4]  874 	ld	c, l
   4944 44            [ 4]  875 	ld	b, h
   4945 DD 6E FC      [19]  876 	ld	l,-4 (ix)
   4948 DD 66 FD      [19]  877 	ld	h,-3 (ix)
   494B 71            [ 7]  878 	ld	(hl), c
   494C 23            [ 6]  879 	inc	hl
   494D 70            [ 7]  880 	ld	(hl), b
   494E 23            [ 6]  881 	inc	hl
   494F 73            [ 7]  882 	ld	(hl), e
   4950 23            [ 6]  883 	inc	hl
   4951 72            [ 7]  884 	ld	(hl), d
   4952 18 51         [12]  885 	jr	00105$
   4954                     886 00104$:
                            887 ;src/entities/entities.c:166: else if (logo->vel.acum_x < -1) { dx = -1; logo->vel.acum_x+=1.0; }
   4954 21 80 BF      [10]  888 	ld	hl, #0xbf80
   4957 E5            [11]  889 	push	hl
   4958 21 00 00      [10]  890 	ld	hl, #0x0000
   495B E5            [11]  891 	push	hl
   495C DD 6E FA      [19]  892 	ld	l,-6 (ix)
   495F DD 66 FB      [19]  893 	ld	h,-5 (ix)
   4962 E5            [11]  894 	push	hl
   4963 DD 6E F8      [19]  895 	ld	l,-8 (ix)
   4966 DD 66 F9      [19]  896 	ld	h,-7 (ix)
   4969 E5            [11]  897 	push	hl
   496A CD DB 56      [17]  898 	call	___fslt
   496D F1            [10]  899 	pop	af
   496E F1            [10]  900 	pop	af
   496F F1            [10]  901 	pop	af
   4970 F1            [10]  902 	pop	af
   4971 7D            [ 4]  903 	ld	a, l
   4972 B7            [ 4]  904 	or	a, a
   4973 28 30         [12]  905 	jr	Z,00105$
   4975 DD 36 F5 FF   [19]  906 	ld	-11 (ix), #0xff
   4979 21 80 3F      [10]  907 	ld	hl, #0x3f80
   497C E5            [11]  908 	push	hl
   497D 21 00 00      [10]  909 	ld	hl, #0x0000
   4980 E5            [11]  910 	push	hl
   4981 DD 6E FA      [19]  911 	ld	l,-6 (ix)
   4984 DD 66 FB      [19]  912 	ld	h,-5 (ix)
   4987 E5            [11]  913 	push	hl
   4988 DD 6E F8      [19]  914 	ld	l,-8 (ix)
   498B DD 66 F9      [19]  915 	ld	h,-7 (ix)
   498E E5            [11]  916 	push	hl
   498F CD D6 57      [17]  917 	call	___fsadd
   4992 F1            [10]  918 	pop	af
   4993 F1            [10]  919 	pop	af
   4994 F1            [10]  920 	pop	af
   4995 F1            [10]  921 	pop	af
   4996 4D            [ 4]  922 	ld	c, l
   4997 44            [ 4]  923 	ld	b, h
   4998 DD 6E FC      [19]  924 	ld	l,-4 (ix)
   499B DD 66 FD      [19]  925 	ld	h,-3 (ix)
   499E 71            [ 7]  926 	ld	(hl), c
   499F 23            [ 6]  927 	inc	hl
   49A0 70            [ 7]  928 	ld	(hl), b
   49A1 23            [ 6]  929 	inc	hl
   49A2 73            [ 7]  930 	ld	(hl), e
   49A3 23            [ 6]  931 	inc	hl
   49A4 72            [ 7]  932 	ld	(hl), d
   49A5                     933 00105$:
                            934 ;src/entities/entities.c:167: if      (logo->vel.acum_y > 1 ) { dy =  1; logo->vel.acum_y-=1.0; }
   49A5 DD 7E FE      [19]  935 	ld	a, -2 (ix)
   49A8 C6 14         [ 7]  936 	add	a, #0x14
   49AA DD 77 F8      [19]  937 	ld	-8 (ix), a
   49AD DD 7E FF      [19]  938 	ld	a, -1 (ix)
   49B0 CE 00         [ 7]  939 	adc	a, #0x00
   49B2 DD 77 F9      [19]  940 	ld	-7 (ix), a
   49B5 DD 6E F8      [19]  941 	ld	l,-8 (ix)
   49B8 DD 66 F9      [19]  942 	ld	h,-7 (ix)
   49BB 4E            [ 7]  943 	ld	c, (hl)
   49BC 23            [ 6]  944 	inc	hl
   49BD 46            [ 7]  945 	ld	b, (hl)
   49BE 23            [ 6]  946 	inc	hl
   49BF 5E            [ 7]  947 	ld	e, (hl)
   49C0 23            [ 6]  948 	inc	hl
   49C1 56            [ 7]  949 	ld	d, (hl)
   49C2 C5            [11]  950 	push	bc
   49C3 D5            [11]  951 	push	de
   49C4 21 80 3F      [10]  952 	ld	hl, #0x3f80
   49C7 E5            [11]  953 	push	hl
   49C8 21 00 00      [10]  954 	ld	hl, #0x0000
   49CB E5            [11]  955 	push	hl
   49CC D5            [11]  956 	push	de
   49CD C5            [11]  957 	push	bc
   49CE CD E0 55      [17]  958 	call	___fsgt
   49D1 F1            [10]  959 	pop	af
   49D2 F1            [10]  960 	pop	af
   49D3 F1            [10]  961 	pop	af
   49D4 F1            [10]  962 	pop	af
   49D5 D1            [10]  963 	pop	de
   49D6 C1            [10]  964 	pop	bc
   49D7 7D            [ 4]  965 	ld	a, l
   49D8 B7            [ 4]  966 	or	a, a
   49D9 28 26         [12]  967 	jr	Z,00109$
   49DB DD 36 F4 01   [19]  968 	ld	-12 (ix), #0x01
   49DF 21 80 3F      [10]  969 	ld	hl, #0x3f80
   49E2 E5            [11]  970 	push	hl
   49E3 21 00 00      [10]  971 	ld	hl, #0x0000
   49E6 E5            [11]  972 	push	hl
   49E7 D5            [11]  973 	push	de
   49E8 C5            [11]  974 	push	bc
   49E9 CD 46 52      [17]  975 	call	___fssub
   49EC F1            [10]  976 	pop	af
   49ED F1            [10]  977 	pop	af
   49EE F1            [10]  978 	pop	af
   49EF F1            [10]  979 	pop	af
   49F0 4D            [ 4]  980 	ld	c, l
   49F1 44            [ 4]  981 	ld	b, h
   49F2 DD 6E F8      [19]  982 	ld	l,-8 (ix)
   49F5 DD 66 F9      [19]  983 	ld	h,-7 (ix)
   49F8 71            [ 7]  984 	ld	(hl), c
   49F9 23            [ 6]  985 	inc	hl
   49FA 70            [ 7]  986 	ld	(hl), b
   49FB 23            [ 6]  987 	inc	hl
   49FC 73            [ 7]  988 	ld	(hl), e
   49FD 23            [ 6]  989 	inc	hl
   49FE 72            [ 7]  990 	ld	(hl), d
   49FF 18 3D         [12]  991 	jr	00110$
   4A01                     992 00109$:
                            993 ;src/entities/entities.c:168: else if (logo->vel.acum_y < -1) { dy = -1; logo->vel.acum_y+=1.0; }
   4A01 C5            [11]  994 	push	bc
   4A02 D5            [11]  995 	push	de
   4A03 21 80 BF      [10]  996 	ld	hl, #0xbf80
   4A06 E5            [11]  997 	push	hl
   4A07 21 00 00      [10]  998 	ld	hl, #0x0000
   4A0A E5            [11]  999 	push	hl
   4A0B D5            [11] 1000 	push	de
   4A0C C5            [11] 1001 	push	bc
   4A0D CD DB 56      [17] 1002 	call	___fslt
   4A10 F1            [10] 1003 	pop	af
   4A11 F1            [10] 1004 	pop	af
   4A12 F1            [10] 1005 	pop	af
   4A13 F1            [10] 1006 	pop	af
   4A14 D1            [10] 1007 	pop	de
   4A15 C1            [10] 1008 	pop	bc
   4A16 7D            [ 4] 1009 	ld	a, l
   4A17 B7            [ 4] 1010 	or	a, a
   4A18 28 24         [12] 1011 	jr	Z,00110$
   4A1A DD 36 F4 FF   [19] 1012 	ld	-12 (ix), #0xff
   4A1E 21 80 3F      [10] 1013 	ld	hl, #0x3f80
   4A21 E5            [11] 1014 	push	hl
   4A22 21 00 00      [10] 1015 	ld	hl, #0x0000
   4A25 E5            [11] 1016 	push	hl
   4A26 D5            [11] 1017 	push	de
   4A27 C5            [11] 1018 	push	bc
   4A28 CD D6 57      [17] 1019 	call	___fsadd
   4A2B F1            [10] 1020 	pop	af
   4A2C F1            [10] 1021 	pop	af
   4A2D F1            [10] 1022 	pop	af
   4A2E F1            [10] 1023 	pop	af
   4A2F 4D            [ 4] 1024 	ld	c, l
   4A30 44            [ 4] 1025 	ld	b, h
   4A31 DD 6E F8      [19] 1026 	ld	l,-8 (ix)
   4A34 DD 66 F9      [19] 1027 	ld	h,-7 (ix)
   4A37 71            [ 7] 1028 	ld	(hl), c
   4A38 23            [ 6] 1029 	inc	hl
   4A39 70            [ 7] 1030 	ld	(hl), b
   4A3A 23            [ 6] 1031 	inc	hl
   4A3B 73            [ 7] 1032 	ld	(hl), e
   4A3C 23            [ 6] 1033 	inc	hl
   4A3D 72            [ 7] 1034 	ld	(hl), d
   4A3E                    1035 00110$:
                           1036 ;src/entities/entities.c:173: if (moveEntityX(logo, dx,  80) ) {
   4A3E 3E 50         [ 7] 1037 	ld	a, #0x50
   4A40 F5            [11] 1038 	push	af
   4A41 33            [ 6] 1039 	inc	sp
   4A42 DD 7E F5      [19] 1040 	ld	a, -11 (ix)
   4A45 F5            [11] 1041 	push	af
   4A46 33            [ 6] 1042 	inc	sp
   4A47 DD 6E FE      [19] 1043 	ld	l,-2 (ix)
   4A4A DD 66 FF      [19] 1044 	ld	h,-1 (ix)
   4A4D E5            [11] 1045 	push	hl
   4A4E CD B0 43      [17] 1046 	call	_moveEntityX
   4A51 F1            [10] 1047 	pop	af
   4A52 F1            [10] 1048 	pop	af
   4A53 7D            [ 4] 1049 	ld	a, l
   4A54 B7            [ 4] 1050 	or	a, a
   4A55 28 30         [12] 1051 	jr	Z,00112$
                           1052 ;src/entities/entities.c:174: logo->vel.vx = -logo->vel.vx*bounceCoefficient;
   4A57 DD 6E F6      [19] 1053 	ld	l,-10 (ix)
   4A5A DD 66 F7      [19] 1054 	ld	h,-9 (ix)
   4A5D 4E            [ 7] 1055 	ld	c, (hl)
   4A5E 23            [ 6] 1056 	inc	hl
   4A5F 46            [ 7] 1057 	ld	b, (hl)
   4A60 23            [ 6] 1058 	inc	hl
   4A61 5E            [ 7] 1059 	ld	e, (hl)
   4A62 23            [ 6] 1060 	inc	hl
   4A63 7E            [ 7] 1061 	ld	a, (hl)
   4A64 EE 80         [ 7] 1062 	xor	a,#0x80
   4A66 57            [ 4] 1063 	ld	d, a
   4A67 21 59 3F      [10] 1064 	ld	hl, #0x3f59
   4A6A E5            [11] 1065 	push	hl
   4A6B 21 9A 99      [10] 1066 	ld	hl, #0x999a
   4A6E E5            [11] 1067 	push	hl
   4A6F D5            [11] 1068 	push	de
   4A70 C5            [11] 1069 	push	bc
   4A71 CD 7B 52      [17] 1070 	call	___fsmul
   4A74 F1            [10] 1071 	pop	af
   4A75 F1            [10] 1072 	pop	af
   4A76 F1            [10] 1073 	pop	af
   4A77 F1            [10] 1074 	pop	af
   4A78 4D            [ 4] 1075 	ld	c, l
   4A79 44            [ 4] 1076 	ld	b, h
   4A7A DD 6E F6      [19] 1077 	ld	l,-10 (ix)
   4A7D DD 66 F7      [19] 1078 	ld	h,-9 (ix)
   4A80 71            [ 7] 1079 	ld	(hl), c
   4A81 23            [ 6] 1080 	inc	hl
   4A82 70            [ 7] 1081 	ld	(hl), b
   4A83 23            [ 6] 1082 	inc	hl
   4A84 73            [ 7] 1083 	ld	(hl), e
   4A85 23            [ 6] 1084 	inc	hl
   4A86 72            [ 7] 1085 	ld	(hl), d
   4A87                    1086 00112$:
                           1087 ;src/entities/entities.c:176: if (moveEntityY(logo, dy, 100) ) {
   4A87 3E 64         [ 7] 1088 	ld	a, #0x64
   4A89 F5            [11] 1089 	push	af
   4A8A 33            [ 6] 1090 	inc	sp
   4A8B DD 7E F4      [19] 1091 	ld	a, -12 (ix)
   4A8E F5            [11] 1092 	push	af
   4A8F 33            [ 6] 1093 	inc	sp
   4A90 DD 6E 04      [19] 1094 	ld	l,4 (ix)
   4A93 DD 66 05      [19] 1095 	ld	h,5 (ix)
   4A96 E5            [11] 1096 	push	hl
   4A97 CD FD 44      [17] 1097 	call	_moveEntityY
   4A9A F1            [10] 1098 	pop	af
   4A9B F1            [10] 1099 	pop	af
   4A9C 7D            [ 4] 1100 	ld	a, l
   4A9D B7            [ 4] 1101 	or	a, a
   4A9E 28 40         [12] 1102 	jr	Z,00115$
                           1103 ;src/entities/entities.c:177: logo->vel.vy = -logo->vel.vy*bounceCoefficient;
   4AA0 DD 7E FE      [19] 1104 	ld	a, -2 (ix)
   4AA3 C6 0C         [ 7] 1105 	add	a, #0x0c
   4AA5 DD 77 F8      [19] 1106 	ld	-8 (ix), a
   4AA8 DD 7E FF      [19] 1107 	ld	a, -1 (ix)
   4AAB CE 00         [ 7] 1108 	adc	a, #0x00
   4AAD DD 77 F9      [19] 1109 	ld	-7 (ix), a
   4AB0 DD 6E F8      [19] 1110 	ld	l,-8 (ix)
   4AB3 DD 66 F9      [19] 1111 	ld	h,-7 (ix)
   4AB6 4E            [ 7] 1112 	ld	c, (hl)
   4AB7 23            [ 6] 1113 	inc	hl
   4AB8 46            [ 7] 1114 	ld	b, (hl)
   4AB9 23            [ 6] 1115 	inc	hl
   4ABA 5E            [ 7] 1116 	ld	e, (hl)
   4ABB 23            [ 6] 1117 	inc	hl
   4ABC 7E            [ 7] 1118 	ld	a, (hl)
   4ABD EE 80         [ 7] 1119 	xor	a,#0x80
   4ABF 57            [ 4] 1120 	ld	d, a
   4AC0 21 59 3F      [10] 1121 	ld	hl, #0x3f59
   4AC3 E5            [11] 1122 	push	hl
   4AC4 21 9A 99      [10] 1123 	ld	hl, #0x999a
   4AC7 E5            [11] 1124 	push	hl
   4AC8 D5            [11] 1125 	push	de
   4AC9 C5            [11] 1126 	push	bc
   4ACA CD 7B 52      [17] 1127 	call	___fsmul
   4ACD F1            [10] 1128 	pop	af
   4ACE F1            [10] 1129 	pop	af
   4ACF F1            [10] 1130 	pop	af
   4AD0 F1            [10] 1131 	pop	af
   4AD1 4D            [ 4] 1132 	ld	c, l
   4AD2 44            [ 4] 1133 	ld	b, h
   4AD3 DD 6E F8      [19] 1134 	ld	l,-8 (ix)
   4AD6 DD 66 F9      [19] 1135 	ld	h,-7 (ix)
   4AD9 71            [ 7] 1136 	ld	(hl), c
   4ADA 23            [ 6] 1137 	inc	hl
   4ADB 70            [ 7] 1138 	ld	(hl), b
   4ADC 23            [ 6] 1139 	inc	hl
   4ADD 73            [ 7] 1140 	ld	(hl), e
   4ADE 23            [ 6] 1141 	inc	hl
   4ADF 72            [ 7] 1142 	ld	(hl), d
   4AE0                    1143 00115$:
   4AE0 DD F9         [10] 1144 	ld	sp, ix
   4AE2 DD E1         [14] 1145 	pop	ix
   4AE4 C9            [10] 1146 	ret
                           1147 	.area _CODE
                           1148 	.area _INITIALIZER
                           1149 	.area _CABS (ABS)
