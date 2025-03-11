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
                             12 	.globl _drawCharacters
                             13 	.globl _print256Chars
                             14 	.globl _incrementedVideoPos
                             15 	.globl _cpct_setVideoMode
                             16 	.globl _cpct_drawCharM2
                             17 	.globl _cpct_drawCharM1
                             18 	.globl _cpct_drawCharM0
                             19 	.globl _cpct_setDrawCharM2
                             20 	.globl _cpct_setDrawCharM1
                             21 	.globl _cpct_setDrawCharM0
                             22 	.globl _cpct_memset
                             23 	.globl _cpct_disableFirmware
                             24 ;--------------------------------------------------------
                             25 ; special function registers
                             26 ;--------------------------------------------------------
                             27 ;--------------------------------------------------------
                             28 ; ram data
                             29 ;--------------------------------------------------------
                             30 	.area _DATA
                             31 ;--------------------------------------------------------
                             32 ; ram data
                             33 ;--------------------------------------------------------
                             34 	.area _INITIALIZED
                             35 ;--------------------------------------------------------
                             36 ; absolute external ram data
                             37 ;--------------------------------------------------------
                             38 	.area _DABS (ABS)
                             39 ;--------------------------------------------------------
                             40 ; global & static initialisations
                             41 ;--------------------------------------------------------
                             42 	.area _HOME
                             43 	.area _GSINIT
                             44 	.area _GSFINAL
                             45 	.area _GSINIT
                             46 ;--------------------------------------------------------
                             47 ; Home
                             48 ;--------------------------------------------------------
                             49 	.area _HOME
                             50 	.area _HOME
                             51 ;--------------------------------------------------------
                             52 ; code
                             53 ;--------------------------------------------------------
                             54 	.area _CODE
                             55 ;src/main.c:25: u8* incrementedVideoPos(u8* pvideomem, u8 inc) {
                             56 ;	---------------------------------
                             57 ; Function incrementedVideoPos
                             58 ; ---------------------------------
   4000                      59 _incrementedVideoPos::
   4000 DD E5         [15]   60 	push	ix
   4002 DD 21 00 00   [14]   61 	ld	ix,#0
   4006 DD 39         [15]   62 	add	ix,sp
                             63 ;src/main.c:27: pvideomem += inc;
   4008 DD 7E 04      [19]   64 	ld	a, 4 (ix)
   400B DD 86 06      [19]   65 	add	a, 6 (ix)
   400E DD 77 04      [19]   66 	ld	4 (ix), a
   4011 DD 7E 05      [19]   67 	ld	a, 5 (ix)
   4014 CE 00         [ 7]   68 	adc	a, #0x00
   4016 DD 77 05      [19]   69 	ld	5 (ix), a
                             70 ;src/main.c:32: if (pvideomem > (u8*)0xC7D0)
   4019 3E D0         [ 7]   71 	ld	a, #0xd0
   401B DD BE 04      [19]   72 	cp	a, 4 (ix)
   401E 3E C7         [ 7]   73 	ld	a, #0xc7
   4020 DD 9E 05      [19]   74 	sbc	a, 5 (ix)
   4023 30 08         [12]   75 	jr	NC,00102$
                             76 ;src/main.c:33: pvideomem = (u8*)CPCT_VMEM_START;
   4025 DD 36 04 00   [19]   77 	ld	4 (ix), #0x00
   4029 DD 36 05 C0   [19]   78 	ld	5 (ix), #0xc0
   402D                      79 00102$:
                             80 ;src/main.c:36: return pvideomem;
   402D DD 6E 04      [19]   81 	ld	l,4 (ix)
   4030 DD 66 05      [19]   82 	ld	h,5 (ix)
   4033 DD E1         [14]   83 	pop	ix
   4035 C9            [10]   84 	ret
                             85 ;src/main.c:42: void print256Chars(u8 **pvideomem, u8 mode, u8 fg_colour, u8 bg_colour) {
                             86 ;	---------------------------------
                             87 ; Function print256Chars
                             88 ; ---------------------------------
   4036                      89 _print256Chars::
   4036 DD E5         [15]   90 	push	ix
   4038 DD 21 00 00   [14]   91 	ld	ix,#0
   403C DD 39         [15]   92 	add	ix,sp
   403E 21 F4 FF      [10]   93 	ld	hl, #-12
   4041 39            [11]   94 	add	hl, sp
                             95 ;src/main.c:43: const u8 increments[3] = { 4, 2, 1 };
   4042 F9            [ 6]   96 	ld	sp, hl
   4043 23            [ 6]   97 	inc	hl
   4044 23            [ 6]   98 	inc	hl
   4045 4D            [ 4]   99 	ld	c,l
   4046 44            [ 4]  100 	ld	b,h
   4047 36 04         [10]  101 	ld	(hl),#0x04
   4049 69            [ 4]  102 	ld	l, c
   404A 60            [ 4]  103 	ld	h, b
   404B 23            [ 6]  104 	inc	hl
   404C 36 02         [10]  105 	ld	(hl), #0x02
   404E 69            [ 4]  106 	ld	l, c
   404F 60            [ 4]  107 	ld	h, b
   4050 23            [ 6]  108 	inc	hl
   4051 23            [ 6]  109 	inc	hl
   4052 36 01         [10]  110 	ld	(hl), #0x01
                            111 ;src/main.c:48: increment = increments[mode];
   4054 DD 6E 06      [19]  112 	ld	l,6 (ix)
   4057 26 00         [ 7]  113 	ld	h,#0x00
   4059 09            [11]  114 	add	hl, bc
   405A 7E            [ 7]  115 	ld	a, (hl)
   405B DD 77 F4      [19]  116 	ld	-12 (ix), a
                            117 ;src/main.c:51: switch (mode) {
   405E DD 7E 06      [19]  118 	ld	a, 6 (ix)
   4061 B7            [ 4]  119 	or	a, a
   4062 20 04         [12]  120 	jr	NZ,00143$
   4064 3E 01         [ 7]  121 	ld	a,#0x01
   4066 18 01         [12]  122 	jr	00144$
   4068                     123 00143$:
   4068 AF            [ 4]  124 	xor	a,a
   4069                     125 00144$:
   4069 DD 77 FF      [19]  126 	ld	-1 (ix), a
   406C DD 7E 06      [19]  127 	ld	a, 6 (ix)
   406F 3D            [ 4]  128 	dec	a
   4070 20 04         [12]  129 	jr	NZ,00145$
   4072 3E 01         [ 7]  130 	ld	a,#0x01
   4074 18 01         [12]  131 	jr	00146$
   4076                     132 00145$:
   4076 AF            [ 4]  133 	xor	a,a
   4077                     134 00146$:
   4077 57            [ 4]  135 	ld	d, a
   4078 DD 7E 06      [19]  136 	ld	a, 6 (ix)
   407B D6 02         [ 7]  137 	sub	a, #0x02
   407D 20 04         [12]  138 	jr	NZ,00147$
   407F 3E 01         [ 7]  139 	ld	a,#0x01
   4081 18 01         [12]  140 	jr	00148$
   4083                     141 00147$:
   4083 AF            [ 4]  142 	xor	a,a
   4084                     143 00148$:
   4084 5F            [ 4]  144 	ld	e, a
   4085 DD 7E FF      [19]  145 	ld	a, -1 (ix)
   4088 B7            [ 4]  146 	or	a,a
   4089 20 22         [12]  147 	jr	NZ,00103$
   408B B2            [ 4]  148 	or	a,d
   408C 20 11         [12]  149 	jr	NZ,00102$
   408E B3            [ 4]  150 	or	a,e
   408F 28 28         [12]  151 	jr	Z,00120$
                            152 ;src/main.c:52: case 2: cpct_setDrawCharM2(fg_colour, bg_colour);  break;
   4091 D5            [11]  153 	push	de
   4092 DD 66 08      [19]  154 	ld	h, 8 (ix)
   4095 DD 6E 07      [19]  155 	ld	l, 7 (ix)
   4098 E5            [11]  156 	push	hl
   4099 CD 1F 44      [17]  157 	call	_cpct_setDrawCharM2
   409C D1            [10]  158 	pop	de
   409D 18 1A         [12]  159 	jr	00120$
                            160 ;src/main.c:53: case 1: cpct_setDrawCharM1(fg_colour, bg_colour);  break;
   409F                     161 00102$:
   409F D5            [11]  162 	push	de
   40A0 DD 66 08      [19]  163 	ld	h, 8 (ix)
   40A3 DD 6E 07      [19]  164 	ld	l, 7 (ix)
   40A6 E5            [11]  165 	push	hl
   40A7 CD 7B 43      [17]  166 	call	_cpct_setDrawCharM1
   40AA D1            [10]  167 	pop	de
   40AB 18 0C         [12]  168 	jr	00120$
                            169 ;src/main.c:54: case 0: cpct_setDrawCharM0(fg_colour, bg_colour);  break;
   40AD                     170 00103$:
   40AD D5            [11]  171 	push	de
   40AE DD 66 08      [19]  172 	ld	h, 8 (ix)
   40B1 DD 6E 07      [19]  173 	ld	l, 7 (ix)
   40B4 E5            [11]  174 	push	hl
   40B5 CD 56 43      [17]  175 	call	_cpct_setDrawCharM0
   40B8 D1            [10]  176 	pop	de
                            177 ;src/main.c:58: for(charnum=1; charnum != 0; charnum++) {
   40B9                     178 00120$:
   40B9 DD 72 F9      [19]  179 	ld	-7 (ix), d
   40BC DD 4E 04      [19]  180 	ld	c,4 (ix)
   40BF DD 46 05      [19]  181 	ld	b,5 (ix)
   40C2 DD 71 FD      [19]  182 	ld	-3 (ix), c
   40C5 DD 70 FE      [19]  183 	ld	-2 (ix), b
   40C8 DD 71 FB      [19]  184 	ld	-5 (ix), c
   40CB DD 70 FC      [19]  185 	ld	-4 (ix), b
   40CE DD 73 FA      [19]  186 	ld	-6 (ix), e
   40D1 DD 36 F5 01   [19]  187 	ld	-11 (ix), #0x01
   40D5                     188 00110$:
                            189 ;src/main.c:60: case 2: cpct_drawCharM2  (*pvideomem, charnum); break;
   40D5 DD 5E F5      [19]  190 	ld	e, -11 (ix)
   40D8 16 00         [ 7]  191 	ld	d, #0x00
                            192 ;src/main.c:59: switch (mode) {
   40DA DD 7E FF      [19]  193 	ld	a, -1 (ix)
   40DD B7            [ 4]  194 	or	a, a
   40DE 20 32         [12]  195 	jr	NZ,00107$
   40E0 DD 7E F9      [19]  196 	ld	a, -7 (ix)
   40E3 B7            [ 4]  197 	or	a, a
   40E4 20 19         [12]  198 	jr	NZ,00106$
   40E6 DD 7E FA      [19]  199 	ld	a, -6 (ix)
   40E9 B7            [ 4]  200 	or	a, a
   40EA 28 33         [12]  201 	jr	Z,00108$
                            202 ;src/main.c:60: case 2: cpct_drawCharM2  (*pvideomem, charnum); break;
   40EC DD 6E FB      [19]  203 	ld	l,-5 (ix)
   40EF DD 66 FC      [19]  204 	ld	h,-4 (ix)
   40F2 7E            [ 7]  205 	ld	a, (hl)
   40F3 23            [ 6]  206 	inc	hl
   40F4 66            [ 7]  207 	ld	h, (hl)
   40F5 6F            [ 4]  208 	ld	l, a
   40F6 C5            [11]  209 	push	bc
   40F7 D5            [11]  210 	push	de
   40F8 E5            [11]  211 	push	hl
   40F9 CD 0E 43      [17]  212 	call	_cpct_drawCharM2
   40FC C1            [10]  213 	pop	bc
   40FD 18 20         [12]  214 	jr	00108$
                            215 ;src/main.c:61: case 1: cpct_drawCharM1  (*pvideomem, charnum); break;
   40FF                     216 00106$:
   40FF DD 6E FD      [19]  217 	ld	l,-3 (ix)
   4102 DD 66 FE      [19]  218 	ld	h,-2 (ix)
   4105 7E            [ 7]  219 	ld	a, (hl)
   4106 23            [ 6]  220 	inc	hl
   4107 66            [ 7]  221 	ld	h, (hl)
   4108 6F            [ 4]  222 	ld	l, a
   4109 C5            [11]  223 	push	bc
   410A D5            [11]  224 	push	de
   410B E5            [11]  225 	push	hl
   410C CD EB 42      [17]  226 	call	_cpct_drawCharM1
   410F C1            [10]  227 	pop	bc
   4110 18 0D         [12]  228 	jr	00108$
                            229 ;src/main.c:62: case 0: cpct_drawCharM0  (*pvideomem, charnum); break;
   4112                     230 00107$:
   4112 69            [ 4]  231 	ld	l, c
   4113 60            [ 4]  232 	ld	h, b
   4114 7E            [ 7]  233 	ld	a, (hl)
   4115 23            [ 6]  234 	inc	hl
   4116 66            [ 7]  235 	ld	h, (hl)
   4117 6F            [ 4]  236 	ld	l, a
   4118 C5            [11]  237 	push	bc
   4119 D5            [11]  238 	push	de
   411A E5            [11]  239 	push	hl
   411B CD C8 42      [17]  240 	call	_cpct_drawCharM0
   411E C1            [10]  241 	pop	bc
                            242 ;src/main.c:63: }
   411F                     243 00108$:
                            244 ;src/main.c:65: *pvideomem = incrementedVideoPos(*pvideomem, increment);
   411F 69            [ 4]  245 	ld	l, c
   4120 60            [ 4]  246 	ld	h, b
   4121 5E            [ 7]  247 	ld	e, (hl)
   4122 23            [ 6]  248 	inc	hl
   4123 56            [ 7]  249 	ld	d, (hl)
   4124 C5            [11]  250 	push	bc
   4125 DD 7E F4      [19]  251 	ld	a, -12 (ix)
   4128 F5            [11]  252 	push	af
   4129 33            [ 6]  253 	inc	sp
   412A D5            [11]  254 	push	de
   412B CD 00 40      [17]  255 	call	_incrementedVideoPos
   412E F1            [10]  256 	pop	af
   412F 33            [ 6]  257 	inc	sp
   4130 EB            [ 4]  258 	ex	de,hl
   4131 C1            [10]  259 	pop	bc
   4132 69            [ 4]  260 	ld	l, c
   4133 60            [ 4]  261 	ld	h, b
   4134 73            [ 7]  262 	ld	(hl), e
   4135 23            [ 6]  263 	inc	hl
   4136 72            [ 7]  264 	ld	(hl), d
                            265 ;src/main.c:58: for(charnum=1; charnum != 0; charnum++) {
   4137 DD 34 F5      [23]  266 	inc	-11 (ix)
   413A DD 7E F5      [19]  267 	ld	a, -11 (ix)
   413D B7            [ 4]  268 	or	a, a
   413E 20 95         [12]  269 	jr	NZ,00110$
   4140 DD F9         [10]  270 	ld	sp, ix
   4142 DD E1         [14]  271 	pop	ix
   4144 C9            [10]  272 	ret
                            273 ;src/main.c:73: void drawCharacters(u8** pvideomem, u8 maxtimes, u8 mode, u8* fg_colour, u8* bg_colour) {
                            274 ;	---------------------------------
                            275 ; Function drawCharacters
                            276 ; ---------------------------------
   4145                     277 _drawCharacters::
   4145 DD E5         [15]  278 	push	ix
   4147 DD 21 00 00   [14]  279 	ld	ix,#0
   414B DD 39         [15]  280 	add	ix,sp
   414D 21 FA FF      [10]  281 	ld	hl, #-6
   4150 39            [11]  282 	add	hl, sp
   4151 F9            [ 6]  283 	ld	sp, hl
                            284 ;src/main.c:75: const u8 colours[3] = { 16, 4, 2 };  // Number of colour each mode has (0 = 16, 1 = 4, 2 = 2)
   4152 21 00 00      [10]  285 	ld	hl, #0x0000
   4155 39            [11]  286 	add	hl, sp
   4156 4D            [ 4]  287 	ld	c,l
   4157 44            [ 4]  288 	ld	b,h
   4158 36 10         [10]  289 	ld	(hl),#0x10
   415A 69            [ 4]  290 	ld	l, c
   415B 60            [ 4]  291 	ld	h, b
   415C 23            [ 6]  292 	inc	hl
   415D 36 04         [10]  293 	ld	(hl), #0x04
   415F 69            [ 4]  294 	ld	l, c
   4160 60            [ 4]  295 	ld	h, b
   4161 23            [ 6]  296 	inc	hl
   4162 23            [ 6]  297 	inc	hl
   4163 36 02         [10]  298 	ld	(hl), #0x02
                            299 ;src/main.c:77: cpct_clearScreen(0);     // Clear Screen filling up with 0's
   4165 C5            [11]  300 	push	bc
   4166 21 00 40      [10]  301 	ld	hl, #0x4000
   4169 E5            [11]  302 	push	hl
   416A AF            [ 4]  303 	xor	a, a
   416B F5            [11]  304 	push	af
   416C 33            [ 6]  305 	inc	sp
   416D 26 C0         [ 7]  306 	ld	h, #0xc0
   416F E5            [11]  307 	push	hl
   4170 CD 37 43      [17]  308 	call	_cpct_memset
   4173 DD 6E 07      [19]  309 	ld	l, 7 (ix)
   4176 CD 29 43      [17]  310 	call	_cpct_setVideoMode
   4179 C1            [10]  311 	pop	bc
                            312 ;src/main.c:81: for(times=0; times < maxtimes; times++) {
   417A DD 7E 07      [19]  313 	ld	a, 7 (ix)
   417D 81            [ 4]  314 	add	a, c
   417E DD 77 FE      [19]  315 	ld	-2 (ix), a
   4181 3E 00         [ 7]  316 	ld	a, #0x00
   4183 88            [ 4]  317 	adc	a, b
   4184 DD 77 FF      [19]  318 	ld	-1 (ix), a
   4187 DD 5E 0A      [19]  319 	ld	e,10 (ix)
   418A DD 56 0B      [19]  320 	ld	d,11 (ix)
   418D 0E 00         [ 7]  321 	ld	c, #0x00
   418F                     322 00107$:
   418F 79            [ 4]  323 	ld	a, c
   4190 DD 96 06      [19]  324 	sub	a, 6 (ix)
   4193 30 57         [12]  325 	jr	NC,00109$
                            326 ;src/main.c:84: if (++(*fg_colour) == colours[mode]) {
   4195 E5            [11]  327 	push	hl
   4196 DD 6E 08      [19]  328 	ld	l, 8 (ix)
   4199 DD 66 09      [19]  329 	ld	h, 9 (ix)
   419C E5            [11]  330 	push	hl
   419D FD E1         [14]  331 	pop	iy
   419F E1            [10]  332 	pop	hl
   41A0 FD 34 00      [23]  333 	inc	0 (iy)
   41A3 FD 46 00      [19]  334 	ld	b, 0 (iy)
   41A6 DD 6E FE      [19]  335 	ld	l,-2 (ix)
   41A9 DD 66 FF      [19]  336 	ld	h,-1 (ix)
   41AC 7E            [ 7]  337 	ld	a, (hl)
   41AD 90            [ 4]  338 	sub	a, b
   41AE 20 1B         [12]  339 	jr	NZ,00104$
                            340 ;src/main.c:85: *fg_colour = 0;
   41B0 FD 36 00 00   [19]  341 	ld	0 (iy), #0x00
                            342 ;src/main.c:86: if (++(*bg_colour) == colours[mode])
   41B4 1A            [ 7]  343 	ld	a, (de)
   41B5 47            [ 4]  344 	ld	b, a
   41B6 04            [ 4]  345 	inc	b
   41B7 78            [ 4]  346 	ld	a, b
   41B8 12            [ 7]  347 	ld	(de), a
   41B9 DD 6E FE      [19]  348 	ld	l,-2 (ix)
   41BC DD 66 FF      [19]  349 	ld	h,-1 (ix)
   41BF 7E            [ 7]  350 	ld	a, (hl)
   41C0 DD 77 FD      [19]  351 	ld	-3 (ix), a
   41C3 78            [ 4]  352 	ld	a, b
   41C4 DD 96 FD      [19]  353 	sub	a, -3 (ix)
   41C7 20 02         [12]  354 	jr	NZ,00104$
                            355 ;src/main.c:87: *bg_colour = 0;
   41C9 AF            [ 4]  356 	xor	a, a
   41CA 12            [ 7]  357 	ld	(de), a
   41CB                     358 00104$:
                            359 ;src/main.c:91: print256Chars(pvideomem, mode, *fg_colour, *bg_colour);
   41CB 1A            [ 7]  360 	ld	a, (de)
   41CC FD 46 00      [19]  361 	ld	b, 0 (iy)
   41CF C5            [11]  362 	push	bc
   41D0 D5            [11]  363 	push	de
   41D1 F5            [11]  364 	push	af
   41D2 33            [ 6]  365 	inc	sp
   41D3 C5            [11]  366 	push	bc
   41D4 33            [ 6]  367 	inc	sp
   41D5 DD 7E 07      [19]  368 	ld	a, 7 (ix)
   41D8 F5            [11]  369 	push	af
   41D9 33            [ 6]  370 	inc	sp
   41DA DD 6E 04      [19]  371 	ld	l,4 (ix)
   41DD DD 66 05      [19]  372 	ld	h,5 (ix)
   41E0 E5            [11]  373 	push	hl
   41E1 CD 36 40      [17]  374 	call	_print256Chars
   41E4 F1            [10]  375 	pop	af
   41E5 F1            [10]  376 	pop	af
   41E6 33            [ 6]  377 	inc	sp
   41E7 D1            [10]  378 	pop	de
   41E8 C1            [10]  379 	pop	bc
                            380 ;src/main.c:81: for(times=0; times < maxtimes; times++) {
   41E9 0C            [ 4]  381 	inc	c
   41EA 18 A3         [12]  382 	jr	00107$
   41EC                     383 00109$:
   41EC DD F9         [10]  384 	ld	sp, ix
   41EE DD E1         [14]  385 	pop	ix
   41F0 C9            [10]  386 	ret
                            387 ;src/main.c:98: void main(void) {
                            388 ;	---------------------------------
                            389 ; Function main
                            390 ; ---------------------------------
   41F1                     391 _main::
   41F1 DD E5         [15]  392 	push	ix
   41F3 DD 21 00 00   [14]  393 	ld	ix,#0
   41F7 DD 39         [15]  394 	add	ix,sp
   41F9 21 EA FF      [10]  395 	ld	hl, #-22
   41FC 39            [11]  396 	add	hl, sp
   41FD F9            [ 6]  397 	ld	sp, hl
                            398 ;src/main.c:99: u8* pvideomem  = CPCT_VMEM_START; // Pointer to video memory
   41FE 21 00 C0      [10]  399 	ld	hl, #0xc000
   4201 E3            [19]  400 	ex	(sp), hl
                            401 ;src/main.c:100: u8  colours[6] = {0};             // 6 variables for 3 pairs of foreground / background colour
   4202 21 02 00      [10]  402 	ld	hl, #0x0002
   4205 39            [11]  403 	add	hl, sp
   4206 4D            [ 4]  404 	ld	c, l
   4207 44            [ 4]  405 	ld	b, h
   4208 AF            [ 4]  406 	xor	a, a
   4209 02            [ 7]  407 	ld	(bc), a
   420A 21 01 00      [10]  408 	ld	hl, #0x0001
   420D 09            [11]  409 	add	hl,bc
   420E DD 75 FE      [19]  410 	ld	-2 (ix), l
   4211 DD 74 FF      [19]  411 	ld	-1 (ix), h
   4214 36 00         [10]  412 	ld	(hl), #0x00
   4216 21 02 00      [10]  413 	ld	hl, #0x0002
   4219 09            [11]  414 	add	hl,bc
   421A DD 75 F4      [19]  415 	ld	-12 (ix), l
   421D DD 74 F5      [19]  416 	ld	-11 (ix), h
   4220 36 00         [10]  417 	ld	(hl), #0x00
   4222 21 03 00      [10]  418 	ld	hl, #0x0003
   4225 09            [11]  419 	add	hl,bc
   4226 DD 75 FA      [19]  420 	ld	-6 (ix), l
   4229 DD 74 FB      [19]  421 	ld	-5 (ix), h
   422C 36 00         [10]  422 	ld	(hl), #0x00
   422E 21 04 00      [10]  423 	ld	hl, #0x0004
   4231 09            [11]  424 	add	hl,bc
   4232 DD 75 F2      [19]  425 	ld	-14 (ix), l
   4235 DD 74 F3      [19]  426 	ld	-13 (ix), h
   4238 36 00         [10]  427 	ld	(hl), #0x00
   423A 21 05 00      [10]  428 	ld	hl, #0x0005
   423D 09            [11]  429 	add	hl,bc
   423E DD 75 FC      [19]  430 	ld	-4 (ix), l
   4241 DD 74 FD      [19]  431 	ld	-3 (ix), h
   4244 36 00         [10]  432 	ld	(hl), #0x00
                            433 ;src/main.c:104: cpct_disableFirmware();
   4246 C5            [11]  434 	push	bc
   4247 CD 45 43      [17]  435 	call	_cpct_disableFirmware
   424A C1            [10]  436 	pop	bc
                            437 ;src/main.c:108: while(1) {
   424B                     438 00102$:
                            439 ;src/main.c:109: drawCharacters(&pvideomem, 14, 2, (colours+0), (colours+1)); // Drawing on mode 2, 14 times
   424B DD 5E FE      [19]  440 	ld	e,-2 (ix)
   424E DD 56 FF      [19]  441 	ld	d,-1 (ix)
   4251 DD 71 F6      [19]  442 	ld	-10 (ix), c
   4254 DD 70 F7      [19]  443 	ld	-9 (ix), b
   4257 21 00 00      [10]  444 	ld	hl, #0x0000
   425A 39            [11]  445 	add	hl, sp
   425B DD 75 F8      [19]  446 	ld	-8 (ix), l
   425E DD 74 F9      [19]  447 	ld	-7 (ix), h
   4261 C5            [11]  448 	push	bc
   4262 D5            [11]  449 	push	de
   4263 DD 5E F6      [19]  450 	ld	e,-10 (ix)
   4266 DD 56 F7      [19]  451 	ld	d,-9 (ix)
   4269 D5            [11]  452 	push	de
   426A 11 0E 02      [10]  453 	ld	de, #0x020e
   426D D5            [11]  454 	push	de
   426E E5            [11]  455 	push	hl
   426F CD 45 41      [17]  456 	call	_drawCharacters
   4272 21 08 00      [10]  457 	ld	hl, #8
   4275 39            [11]  458 	add	hl, sp
   4276 F9            [ 6]  459 	ld	sp, hl
   4277 C1            [10]  460 	pop	bc
                            461 ;src/main.c:110: drawCharacters(&pvideomem, 17, 1, (colours+2), (colours+3)); // Drawing on mode 1, 17 times
   4278 DD 5E FA      [19]  462 	ld	e,-6 (ix)
   427B DD 56 FB      [19]  463 	ld	d,-5 (ix)
   427E D5            [11]  464 	push	de
   427F FD E1         [14]  465 	pop	iy
   4281 DD 6E F4      [19]  466 	ld	l,-12 (ix)
   4284 DD 66 F5      [19]  467 	ld	h,-11 (ix)
   4287 DD 5E F8      [19]  468 	ld	e,-8 (ix)
   428A DD 56 F9      [19]  469 	ld	d,-7 (ix)
   428D C5            [11]  470 	push	bc
   428E FD E5         [15]  471 	push	iy
   4290 E5            [11]  472 	push	hl
   4291 21 11 01      [10]  473 	ld	hl, #0x0111
   4294 E5            [11]  474 	push	hl
   4295 D5            [11]  475 	push	de
   4296 CD 45 41      [17]  476 	call	_drawCharacters
   4299 21 08 00      [10]  477 	ld	hl, #8
   429C 39            [11]  478 	add	hl, sp
   429D F9            [ 6]  479 	ld	sp, hl
   429E C1            [10]  480 	pop	bc
                            481 ;src/main.c:111: drawCharacters(&pvideomem, 21, 0, (colours+4), (colours+5)); // Drawing on mode 0, 21 times
   429F DD 5E FC      [19]  482 	ld	e,-4 (ix)
   42A2 DD 56 FD      [19]  483 	ld	d,-3 (ix)
   42A5 D5            [11]  484 	push	de
   42A6 FD E1         [14]  485 	pop	iy
   42A8 DD 6E F2      [19]  486 	ld	l,-14 (ix)
   42AB DD 66 F3      [19]  487 	ld	h,-13 (ix)
   42AE DD 5E F8      [19]  488 	ld	e,-8 (ix)
   42B1 DD 56 F9      [19]  489 	ld	d,-7 (ix)
   42B4 C5            [11]  490 	push	bc
   42B5 FD E5         [15]  491 	push	iy
   42B7 E5            [11]  492 	push	hl
   42B8 21 15 00      [10]  493 	ld	hl, #0x0015
   42BB E5            [11]  494 	push	hl
   42BC D5            [11]  495 	push	de
   42BD CD 45 41      [17]  496 	call	_drawCharacters
   42C0 21 08 00      [10]  497 	ld	hl, #8
   42C3 39            [11]  498 	add	hl, sp
   42C4 F9            [ 6]  499 	ld	sp, hl
   42C5 C1            [10]  500 	pop	bc
   42C6 18 83         [12]  501 	jr	00102$
                            502 	.area _CODE
                            503 	.area _INITIALIZER
                            504 	.area _CABS (ABS)
