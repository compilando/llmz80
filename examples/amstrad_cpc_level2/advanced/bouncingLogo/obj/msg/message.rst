                              1 ;--------------------------------------------------------
                              2 ; File Created by SDCC : free open source ANSI-C Compiler
                              3 ; Version 3.6.8 #9946 (Linux)
                              4 ;--------------------------------------------------------
                              5 	.module message
                              6 	.optsdcc -mz80
                              7 	
                              8 ;--------------------------------------------------------
                              9 ; Public variables in this module
                             10 ;--------------------------------------------------------
                             11 	.globl _cpct_drawStringM0
                             12 	.globl _cpct_setDrawCharM0
                             13 	.globl _g_message
                             14 	.globl _drawMessage
                             15 	.globl _strcpy
                             16 	.globl _concatNum
                             17 ;--------------------------------------------------------
                             18 ; special function registers
                             19 ;--------------------------------------------------------
                             20 ;--------------------------------------------------------
                             21 ; ram data
                             22 ;--------------------------------------------------------
                             23 	.area _DATA
   5231                      24 _g_message::
   5231                      25 	.ds 17
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
                             50 ;src/msg/message.c:26: void drawMessage() {
                             51 ;	---------------------------------
                             52 ; Function drawMessage
                             53 ; ---------------------------------
   42C6                      54 _drawMessage::
                             55 ;src/msg/message.c:28: if (g_message.time > 1) {
   42C6 01 31 52      [10]   56 	ld	bc, #_g_message+0
   42C9 21 41 52      [10]   57 	ld	hl, #(_g_message + 0x0010) + 0
   42CC 5E            [ 7]   58 	ld	e, (hl)
                             59 ;src/msg/message.c:31: cpct_drawStringM0(g_message.str, g_message.videopos);
                             60 ;src/msg/message.c:28: if (g_message.time > 1) {
   42CD 3E 01         [ 7]   61 	ld	a, #0x01
   42CF 93            [ 4]   62 	sub	a, e
   42D0 30 1E         [12]   63 	jr	NC,00104$
                             64 ;src/msg/message.c:30: cpct_setDrawCharM0(1, 0);
   42D2 C5            [11]   65 	push	bc
   42D3 21 01 00      [10]   66 	ld	hl, #0x0001
   42D6 E5            [11]   67 	push	hl
   42D7 CD CC 51      [17]   68 	call	_cpct_setDrawCharM0
                             69 ;src/msg/message.c:31: cpct_drawStringM0(g_message.str, g_message.videopos);
   42DA E1            [10]   70 	pop	hl
   42DB 4E            [ 7]   71 	ld	c, (hl)
   42DC 23            [ 6]   72 	inc	hl
   42DD 46            [ 7]   73 	ld	b, (hl)
   42DE C5            [11]   74 	push	bc
   42DF 21 33 52      [10]   75 	ld	hl, #(_g_message + 0x0002)
   42E2 E5            [11]   76 	push	hl
   42E3 CD DA 4F      [17]   77 	call	_cpct_drawStringM0
                             78 ;src/msg/message.c:32: g_message.time--;
   42E6 21 41 52      [10]   79 	ld	hl, #(_g_message + 0x0010) + 0
   42E9 4E            [ 7]   80 	ld	c, (hl)
   42EA 0D            [ 4]   81 	dec	c
   42EB 21 41 52      [10]   82 	ld	hl, #(_g_message + 0x0010)
   42EE 71            [ 7]   83 	ld	(hl), c
   42EF C9            [10]   84 	ret
   42F0                      85 00104$:
                             86 ;src/msg/message.c:33: } else if (g_message.time > 0) {
   42F0 7B            [ 4]   87 	ld	a, e
   42F1 B7            [ 4]   88 	or	a, a
   42F2 C8            [11]   89 	ret	Z
                             90 ;src/msg/message.c:35: cpct_setDrawCharM0(0, 0);
   42F3 C5            [11]   91 	push	bc
   42F4 21 00 00      [10]   92 	ld	hl, #0x0000
   42F7 E5            [11]   93 	push	hl
   42F8 CD CC 51      [17]   94 	call	_cpct_setDrawCharM0
                             95 ;src/msg/message.c:36: cpct_drawStringM0(g_message.str, g_message.videopos);
   42FB E1            [10]   96 	pop	hl
   42FC 4E            [ 7]   97 	ld	c, (hl)
   42FD 23            [ 6]   98 	inc	hl
   42FE 46            [ 7]   99 	ld	b, (hl)
   42FF C5            [11]  100 	push	bc
   4300 21 33 52      [10]  101 	ld	hl, #(_g_message + 0x0002)
   4303 E5            [11]  102 	push	hl
   4304 CD DA 4F      [17]  103 	call	_cpct_drawStringM0
                            104 ;src/msg/message.c:37: g_message.time=0;
   4307 21 41 52      [10]  105 	ld	hl, #(_g_message + 0x0010)
   430A 36 00         [10]  106 	ld	(hl), #0x00
   430C C9            [10]  107 	ret
                            108 ;src/msg/message.c:44: void strcpy(i8* to, const i8* from){
                            109 ;	---------------------------------
                            110 ; Function strcpy
                            111 ; ---------------------------------
   430D                     112 _strcpy::
                            113 ;src/msg/message.c:45: while (*to++ = *from++);
   430D 21 04 00      [10]  114 	ld	hl, #4
   4310 39            [11]  115 	add	hl, sp
   4311 4E            [ 7]  116 	ld	c, (hl)
   4312 23            [ 6]  117 	inc	hl
   4313 46            [ 7]  118 	ld	b, (hl)
   4314 21 02 00      [10]  119 	ld	hl, #2
   4317 39            [11]  120 	add	hl, sp
   4318 5E            [ 7]  121 	ld	e, (hl)
   4319 23            [ 6]  122 	inc	hl
   431A 56            [ 7]  123 	ld	d, (hl)
   431B                     124 00101$:
   431B 0A            [ 7]  125 	ld	a, (bc)
   431C 03            [ 6]  126 	inc	bc
   431D 12            [ 7]  127 	ld	(de), a
   431E 13            [ 6]  128 	inc	de
   431F B7            [ 4]  129 	or	a, a
   4320 20 F9         [12]  130 	jr	NZ,00101$
   4322 C9            [10]  131 	ret
                            132 ;src/msg/message.c:52: void concatNum (i8* to, i8 num) {
                            133 ;	---------------------------------
                            134 ; Function concatNum
                            135 ; ---------------------------------
   4323                     136 _concatNum::
   4323 DD E5         [15]  137 	push	ix
   4325 DD 21 00 00   [14]  138 	ld	ix,#0
   4329 DD 39         [15]  139 	add	ix,sp
   432B 21 FA FF      [10]  140 	ld	hl, #-6
   432E 39            [11]  141 	add	hl, sp
   432F F9            [ 6]  142 	ld	sp, hl
                            143 ;src/msg/message.c:53: i8 digits[5] = { 32, 48, 48, 48, 0 };
   4330 21 01 00      [10]  144 	ld	hl, #0x0001
   4333 39            [11]  145 	add	hl, sp
   4334 4D            [ 4]  146 	ld	c,l
   4335 44            [ 4]  147 	ld	b,h
   4336 36 20         [10]  148 	ld	(hl),#0x20
   4338 69            [ 4]  149 	ld	l, c
   4339 60            [ 4]  150 	ld	h, b
   433A 23            [ 6]  151 	inc	hl
   433B 36 30         [10]  152 	ld	(hl), #0x30
   433D 69            [ 4]  153 	ld	l, c
   433E 60            [ 4]  154 	ld	h, b
   433F 23            [ 6]  155 	inc	hl
   4340 23            [ 6]  156 	inc	hl
   4341 36 30         [10]  157 	ld	(hl), #0x30
   4343 69            [ 4]  158 	ld	l, c
   4344 60            [ 4]  159 	ld	h, b
   4345 23            [ 6]  160 	inc	hl
   4346 23            [ 6]  161 	inc	hl
   4347 23            [ 6]  162 	inc	hl
   4348 36 30         [10]  163 	ld	(hl), #0x30
   434A 21 04 00      [10]  164 	ld	hl, #0x0004
   434D 09            [11]  165 	add	hl, bc
   434E 36 00         [10]  166 	ld	(hl), #0x00
                            167 ;src/msg/message.c:57: if (num < 0) {
   4350 DD CB 06 7E   [20]  168 	bit	7, 6 (ix)
   4354 28 0A         [12]  169 	jr	Z,00102$
                            170 ;src/msg/message.c:58: unum = -num;
   4356 AF            [ 4]  171 	xor	a, a
   4357 DD 96 06      [19]  172 	sub	a, 6 (ix)
   435A 57            [ 4]  173 	ld	d, a
                            174 ;src/msg/message.c:59: digits[0]=45;
   435B 3E 2D         [ 7]  175 	ld	a, #0x2d
   435D 02            [ 7]  176 	ld	(bc), a
   435E 18 03         [12]  177 	jr	00113$
   4360                     178 00102$:
                            179 ;src/msg/message.c:61: unum = num;
   4360 DD 56 06      [19]  180 	ld	d, 6 (ix)
                            181 ;src/msg/message.c:65: for (d=3; d != 0; --d) {
   4363                     182 00113$:
   4363 1E 03         [ 7]  183 	ld	e, #0x03
   4365                     184 00106$:
                            185 ;src/msg/message.c:66: u8 r=unum % 10;
   4365 C5            [11]  186 	push	bc
   4366 D5            [11]  187 	push	de
   4367 3E 0A         [ 7]  188 	ld	a, #0x0a
   4369 F5            [11]  189 	push	af
   436A 33            [ 6]  190 	inc	sp
   436B D5            [11]  191 	push	de
   436C 33            [ 6]  192 	inc	sp
   436D CD 1D 51      [17]  193 	call	__moduchar
   4370 F1            [10]  194 	pop	af
   4371 D1            [10]  195 	pop	de
                            196 ;src/msg/message.c:67: unum /= 10;
   4372 DD 75 FA      [19]  197 	ld	-6 (ix), l
   4375 D5            [11]  198 	push	de
   4376 3E 0A         [ 7]  199 	ld	a, #0x0a
   4378 F5            [11]  200 	push	af
   4379 33            [ 6]  201 	inc	sp
   437A D5            [11]  202 	push	de
   437B 33            [ 6]  203 	inc	sp
   437C CD 3C 51      [17]  204 	call	__divuchar
   437F F1            [10]  205 	pop	af
   4380 D1            [10]  206 	pop	de
   4381 C1            [10]  207 	pop	bc
   4382 55            [ 4]  208 	ld	d, l
                            209 ;src/msg/message.c:68: digits[d]=48 + r;
   4383 6B            [ 4]  210 	ld	l,e
   4384 26 00         [ 7]  211 	ld	h,#0x00
   4386 09            [11]  212 	add	hl, bc
   4387 DD 7E FA      [19]  213 	ld	a, -6 (ix)
   438A C6 30         [ 7]  214 	add	a, #0x30
   438C 77            [ 7]  215 	ld	(hl), a
                            216 ;src/msg/message.c:65: for (d=3; d != 0; --d) {
   438D 1D            [ 4]  217 	dec e
   438E 20 D5         [12]  218 	jr	NZ,00106$
                            219 ;src/msg/message.c:73: for (d=0; d<5; d++){
   4390 DD 5E 04      [19]  220 	ld	e, 4 (ix)
   4393 DD 56 05      [19]  221 	ld	d, 5 (ix)
   4396 D5            [11]  222 	push	de
   4397 FD E1         [14]  223 	pop	iy
   4399 1E 00         [ 7]  224 	ld	e, #0x00
   439B                     225 00108$:
                            226 ;src/msg/message.c:74: *to++ = digits[d];
   439B 6B            [ 4]  227 	ld	l,e
   439C 26 00         [ 7]  228 	ld	h,#0x00
   439E 09            [11]  229 	add	hl, bc
   439F 56            [ 7]  230 	ld	d, (hl)
   43A0 FD 72 00      [19]  231 	ld	0 (iy), d
   43A3 FD 23         [10]  232 	inc	iy
                            233 ;src/msg/message.c:73: for (d=0; d<5; d++){
   43A5 1C            [ 4]  234 	inc	e
   43A6 7B            [ 4]  235 	ld	a, e
   43A7 D6 05         [ 7]  236 	sub	a, #0x05
   43A9 38 F0         [12]  237 	jr	C,00108$
   43AB DD F9         [10]  238 	ld	sp, ix
   43AD DD E1         [14]  239 	pop	ix
   43AF C9            [10]  240 	ret
                            241 	.area _CODE
                            242 	.area _INITIALIZER
                            243 	.area _CABS (ABS)
