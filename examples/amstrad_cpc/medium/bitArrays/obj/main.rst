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
                             12 	.globl _printArray
                             13 	.globl _cpct_setVideoMode
                             14 	.globl _cpct_drawCharM2
                             15 	.globl _cpct_setDrawCharM2
                             16 	.globl _cpct_set4Bits
                             17 	.globl _cpct_set2Bits
                             18 	.globl _cpct_setBit
                             19 	.globl _cpct_get4Bits
                             20 	.globl _cpct_get2Bits
                             21 	.globl _cpct_getBit
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
                             55 ;src/main.c:35: void printArray(u8* pvideomem, void *array, u8 nItems, TFunc thefunction) {
                             56 ;	---------------------------------
                             57 ; Function printArray
                             58 ; ---------------------------------
   4000                      59 _printArray::
   4000 DD E5         [15]   60 	push	ix
   4002 DD 21 00 00   [14]   61 	ld	ix,#0
   4006 DD 39         [15]   62 	add	ix,sp
   4008 21 F8 FF      [10]   63 	ld	hl, #-8
   400B 39            [11]   64 	add	hl, sp
   400C F9            [ 6]   65 	ld	sp, hl
                             66 ;src/main.c:36: u8 out = 0; // Value returned by getBit functions [0-15]
   400D 0E 00         [ 7]   67 	ld	c, #0x00
                             68 ;src/main.c:41: for (i = 0; i < nItems; ++i) {
   400F DD 7E 09      [19]   69 	ld	a, 9 (ix)
   4012 B7            [ 4]   70 	or	a, a
   4013 20 04         [12]   71 	jr	NZ,00145$
   4015 3E 01         [ 7]   72 	ld	a,#0x01
   4017 18 01         [12]   73 	jr	00146$
   4019                      74 00145$:
   4019 AF            [ 4]   75 	xor	a,a
   401A                      76 00146$:
   401A DD 77 FF      [19]   77 	ld	-1 (ix), a
   401D DD 7E 09      [19]   78 	ld	a, 9 (ix)
   4020 3D            [ 4]   79 	dec	a
   4021 20 04         [12]   80 	jr	NZ,00147$
   4023 3E 01         [ 7]   81 	ld	a,#0x01
   4025 18 01         [12]   82 	jr	00148$
   4027                      83 00147$:
   4027 AF            [ 4]   84 	xor	a,a
   4028                      85 00148$:
   4028 DD 77 F9      [19]   86 	ld	-7 (ix), a
   402B DD 7E 09      [19]   87 	ld	a, 9 (ix)
   402E D6 02         [ 7]   88 	sub	a, #0x02
   4030 20 04         [12]   89 	jr	NZ,00149$
   4032 3E 01         [ 7]   90 	ld	a,#0x01
   4034 18 01         [12]   91 	jr	00150$
   4036                      92 00149$:
   4036 AF            [ 4]   93 	xor	a,a
   4037                      94 00150$:
   4037 DD 77 FA      [19]   95 	ld	-6 (ix), a
   403A DD 7E 04      [19]   96 	ld	a, 4 (ix)
   403D DD 77 FB      [19]   97 	ld	-5 (ix), a
   4040 DD 7E 05      [19]   98 	ld	a, 5 (ix)
   4043 DD 77 FC      [19]   99 	ld	-4 (ix), a
   4046 DD 36 F8 00   [19]  100 	ld	-8 (ix), #0x00
   404A                     101 00110$:
   404A DD 7E F8      [19]  102 	ld	a, -8 (ix)
   404D DD 96 08      [19]  103 	sub	a, 8 (ix)
   4050 D2 DD 40      [10]  104 	jp	NC, 00112$
                            105 ;src/main.c:48: case f_getbit:   out = (cpct_getBit (array, i) > 0); break;
   4053 DD 7E F8      [19]  106 	ld	a, -8 (ix)
   4056 DD 77 FD      [19]  107 	ld	-3 (ix), a
   4059 DD 36 FE 00   [19]  108 	ld	-2 (ix), #0x00
                            109 ;src/main.c:45: switch(thefunction) {
   405D DD 7E FF      [19]  110 	ld	a, -1 (ix)
   4060 B7            [ 4]  111 	or	a, a
   4061 20 0E         [12]  112 	jr	NZ,00101$
   4063 DD 7E F9      [19]  113 	ld	a, -7 (ix)
   4066 B7            [ 4]  114 	or	a, a
   4067 20 25         [12]  115 	jr	NZ,00102$
   4069 DD 7E FA      [19]  116 	ld	a, -6 (ix)
   406C B7            [ 4]  117 	or	a, a
   406D 20 33         [12]  118 	jr	NZ,00103$
   406F 18 43         [12]  119 	jr	00104$
                            120 ;src/main.c:48: case f_getbit:   out = (cpct_getBit (array, i) > 0); break;
   4071                     121 00101$:
   4071 DD 6E FD      [19]  122 	ld	l,-3 (ix)
   4074 DD 66 FE      [19]  123 	ld	h,-2 (ix)
   4077 E5            [11]  124 	push	hl
   4078 DD 6E 06      [19]  125 	ld	l,6 (ix)
   407B DD 66 07      [19]  126 	ld	h,7 (ix)
   407E E5            [11]  127 	push	hl
   407F CD 73 43      [17]  128 	call	_cpct_getBit
   4082 7D            [ 4]  129 	ld	a, l
   4083 B7            [ 4]  130 	or	a, a
   4084 28 04         [12]  131 	jr	Z,00114$
   4086 0E 01         [ 7]  132 	ld	c, #0x01
   4088 18 2A         [12]  133 	jr	00104$
   408A                     134 00114$:
   408A 0E 00         [ 7]  135 	ld	c, #0x00
   408C 18 26         [12]  136 	jr	00104$
                            137 ;src/main.c:51: case f_get2bits: out = cpct_get2Bits(array, i); break;
   408E                     138 00102$:
   408E DD 6E FD      [19]  139 	ld	l,-3 (ix)
   4091 DD 66 FE      [19]  140 	ld	h,-2 (ix)
   4094 E5            [11]  141 	push	hl
   4095 DD 6E 06      [19]  142 	ld	l,6 (ix)
   4098 DD 66 07      [19]  143 	ld	h,7 (ix)
   409B E5            [11]  144 	push	hl
   409C CD D4 43      [17]  145 	call	_cpct_get2Bits
   409F 4D            [ 4]  146 	ld	c, l
   40A0 18 12         [12]  147 	jr	00104$
                            148 ;src/main.c:54: case f_get4bits: out = cpct_get4Bits(array, i); break;
   40A2                     149 00103$:
   40A2 DD 6E FD      [19]  150 	ld	l,-3 (ix)
   40A5 DD 66 FE      [19]  151 	ld	h,-2 (ix)
   40A8 E5            [11]  152 	push	hl
   40A9 DD 6E 06      [19]  153 	ld	l,6 (ix)
   40AC DD 66 07      [19]  154 	ld	h,7 (ix)
   40AF E5            [11]  155 	push	hl
   40B0 CD FA 43      [17]  156 	call	_cpct_get4Bits
   40B3 4D            [ 4]  157 	ld	c, l
                            158 ;src/main.c:55: }
   40B4                     159 00104$:
                            160 ;src/main.c:58: if (out) 
   40B4 79            [ 4]  161 	ld	a, c
   40B5 B7            [ 4]  162 	or	a, a
   40B6 28 06         [12]  163 	jr	Z,00106$
                            164 ;src/main.c:59: c = '0' + out;
   40B8 79            [ 4]  165 	ld	a, c
   40B9 C6 30         [ 7]  166 	add	a, #0x30
   40BB 5F            [ 4]  167 	ld	e, a
   40BC 18 02         [12]  168 	jr	00107$
   40BE                     169 00106$:
                            170 ;src/main.c:61: c = '_';
   40BE 1E 5F         [ 7]  171 	ld	e, #0x5f
   40C0                     172 00107$:
                            173 ;src/main.c:65: cpct_drawCharM2(pvideomem, c);
   40C0 16 00         [ 7]  174 	ld	d, #0x00
   40C2 DD 6E FB      [19]  175 	ld	l,-5 (ix)
   40C5 DD 66 FC      [19]  176 	ld	h,-4 (ix)
   40C8 C5            [11]  177 	push	bc
   40C9 D5            [11]  178 	push	de
   40CA E5            [11]  179 	push	hl
   40CB CD 95 43      [17]  180 	call	_cpct_drawCharM2
   40CE C1            [10]  181 	pop	bc
                            182 ;src/main.c:66: pvideomem++;
   40CF DD 34 FB      [23]  183 	inc	-5 (ix)
   40D2 20 03         [12]  184 	jr	NZ,00151$
   40D4 DD 34 FC      [23]  185 	inc	-4 (ix)
   40D7                     186 00151$:
                            187 ;src/main.c:41: for (i = 0; i < nItems; ++i) {
   40D7 DD 34 F8      [23]  188 	inc	-8 (ix)
   40DA C3 4A 40      [10]  189 	jp	00110$
   40DD                     190 00112$:
   40DD DD F9         [10]  191 	ld	sp, ix
   40DF DD E1         [14]  192 	pop	ix
   40E1 C9            [10]  193 	ret
                            194 ;src/main.c:73: void main (void) {
                            195 ;	---------------------------------
                            196 ; Function main
                            197 ; ---------------------------------
   40E2                     198 _main::
   40E2 DD E5         [15]  199 	push	ix
   40E4 DD 21 00 00   [14]  200 	ld	ix,#0
   40E8 DD 39         [15]  201 	add	ix,sp
   40EA 21 AD FF      [10]  202 	ld	hl, #-83
   40ED 39            [11]  203 	add	hl, sp
   40EE F9            [ 6]  204 	ld	sp, hl
                            205 ;src/main.c:81: cpct_disableFirmware();
   40EF CD 68 44      [17]  206 	call	_cpct_disableFirmware
                            207 ;src/main.c:84: cpct_setVideoMode(2);
   40F2 2E 02         [ 7]  208 	ld	l, #0x02
   40F4 CD 13 44      [17]  209 	call	_cpct_setVideoMode
                            210 ;src/main.c:85: cpct_setDrawCharM2(1, 0); // Draw characters in Foreground colour
   40F7 21 01 00      [10]  211 	ld	hl, #0x0001
   40FA E5            [11]  212 	push	hl
   40FB CD 95 44      [17]  213 	call	_cpct_setDrawCharM2
                            214 ;src/main.c:90: while(1) {
   40FE                     215 00110$:
                            216 ;src/main.c:93: cpct_memset(array1, 0, 10);
   40FE 21 3D 00      [10]  217 	ld	hl, #0x003d
   4101 39            [11]  218 	add	hl, sp
   4102 DD 75 FE      [19]  219 	ld	-2 (ix), l
   4105 DD 74 FF      [19]  220 	ld	-1 (ix), h
   4108 4D            [ 4]  221 	ld	c, l
   4109 44            [ 4]  222 	ld	b, h
   410A 21 0A 00      [10]  223 	ld	hl, #0x000a
   410D E5            [11]  224 	push	hl
   410E AF            [ 4]  225 	xor	a, a
   410F F5            [11]  226 	push	af
   4110 33            [ 6]  227 	inc	sp
   4111 C5            [11]  228 	push	bc
   4112 CD 21 44      [17]  229 	call	_cpct_memset
                            230 ;src/main.c:94: cpct_memset(array2, 0, 20);
   4115 21 29 00      [10]  231 	ld	hl, #0x0029
   4118 39            [11]  232 	add	hl, sp
   4119 DD 75 F8      [19]  233 	ld	-8 (ix), l
   411C DD 74 F9      [19]  234 	ld	-7 (ix), h
   411F 4D            [ 4]  235 	ld	c, l
   4120 44            [ 4]  236 	ld	b, h
   4121 21 14 00      [10]  237 	ld	hl, #0x0014
   4124 E5            [11]  238 	push	hl
   4125 AF            [ 4]  239 	xor	a, a
   4126 F5            [11]  240 	push	af
   4127 33            [ 6]  241 	inc	sp
   4128 C5            [11]  242 	push	bc
   4129 CD 21 44      [17]  243 	call	_cpct_memset
                            244 ;src/main.c:95: cpct_memset(array4, 0, 40);
   412C 21 01 00      [10]  245 	ld	hl, #0x0001
   412F 39            [11]  246 	add	hl, sp
   4130 4D            [ 4]  247 	ld	c, l
   4131 44            [ 4]  248 	ld	b, h
   4132 59            [ 4]  249 	ld	e, c
   4133 50            [ 4]  250 	ld	d, b
   4134 C5            [11]  251 	push	bc
   4135 21 28 00      [10]  252 	ld	hl, #0x0028
   4138 E5            [11]  253 	push	hl
   4139 AF            [ 4]  254 	xor	a, a
   413A F5            [11]  255 	push	af
   413B 33            [ 6]  256 	inc	sp
   413C D5            [11]  257 	push	de
   413D CD 21 44      [17]  258 	call	_cpct_memset
   4140 C1            [10]  259 	pop	bc
                            260 ;src/main.c:100: for (i = 0; i < 80; ++i) {
   4141 DD 7E FE      [19]  261 	ld	a, -2 (ix)
   4144 DD 77 FA      [19]  262 	ld	-6 (ix), a
   4147 DD 7E FF      [19]  263 	ld	a, -1 (ix)
   414A DD 77 FB      [19]  264 	ld	-5 (ix), a
   414D DD 7E FE      [19]  265 	ld	a, -2 (ix)
   4150 DD 77 FC      [19]  266 	ld	-4 (ix), a
   4153 DD 7E FF      [19]  267 	ld	a, -1 (ix)
   4156 DD 77 FD      [19]  268 	ld	-3 (ix), a
   4159 DD 7E FE      [19]  269 	ld	a, -2 (ix)
   415C DD 77 F6      [19]  270 	ld	-10 (ix), a
   415F DD 7E FF      [19]  271 	ld	a, -1 (ix)
   4162 DD 77 F7      [19]  272 	ld	-9 (ix), a
   4165 DD 36 F5 00   [19]  273 	ld	-11 (ix), #0x00
   4169                     274 00112$:
                            275 ;src/main.c:102: cpct_setBit(array1, 1, i);
   4169 DD 6E F5      [19]  276 	ld	l, -11 (ix)
   416C 26 00         [ 7]  277 	ld	h, #0x00
   416E DD 5E FA      [19]  278 	ld	e, -6 (ix)
   4171 DD 56 FB      [19]  279 	ld	d, -5 (ix)
   4174 D5            [11]  280 	push	de
   4175 FD E1         [14]  281 	pop	iy
   4177 E5            [11]  282 	push	hl
   4178 C5            [11]  283 	push	bc
   4179 E5            [11]  284 	push	hl
   417A 11 01 00      [10]  285 	ld	de, #0x0001
   417D D5            [11]  286 	push	de
   417E FD E5         [15]  287 	push	iy
   4180 CD B0 43      [17]  288 	call	_cpct_setBit
   4183 C1            [10]  289 	pop	bc
   4184 E1            [10]  290 	pop	hl
                            291 ;src/main.c:105: printArray(CPCT_VMEM_START, array1, 80, f_getbit); 
   4185 DD 5E FC      [19]  292 	ld	e, -4 (ix)
   4188 DD 56 FD      [19]  293 	ld	d, -3 (ix)
   418B D5            [11]  294 	push	de
   418C FD E1         [14]  295 	pop	iy
   418E E5            [11]  296 	push	hl
   418F C5            [11]  297 	push	bc
   4190 11 50 00      [10]  298 	ld	de, #0x0050
   4193 D5            [11]  299 	push	de
   4194 FD E5         [15]  300 	push	iy
   4196 11 00 C0      [10]  301 	ld	de, #0xc000
   4199 D5            [11]  302 	push	de
   419A CD 00 40      [17]  303 	call	_printArray
   419D 21 06 00      [10]  304 	ld	hl, #6
   41A0 39            [11]  305 	add	hl, sp
   41A1 F9            [ 6]  306 	ld	sp, hl
   41A2 C1            [10]  307 	pop	bc
   41A3 E1            [10]  308 	pop	hl
                            309 ;src/main.c:108: cpct_setBit(array1, 0, i);
   41A4 DD 5E F6      [19]  310 	ld	e,-10 (ix)
   41A7 DD 56 F7      [19]  311 	ld	d,-9 (ix)
   41AA C5            [11]  312 	push	bc
   41AB E5            [11]  313 	push	hl
   41AC 21 00 00      [10]  314 	ld	hl, #0x0000
   41AF E5            [11]  315 	push	hl
   41B0 D5            [11]  316 	push	de
   41B1 CD B0 43      [17]  317 	call	_cpct_setBit
   41B4 C1            [10]  318 	pop	bc
                            319 ;src/main.c:100: for (i = 0; i < 80; ++i) {
   41B5 DD 34 F5      [23]  320 	inc	-11 (ix)
   41B8 DD 7E F5      [19]  321 	ld	a, -11 (ix)
   41BB D6 50         [ 7]  322 	sub	a, #0x50
   41BD 38 AA         [12]  323 	jr	C,00112$
                            324 ;src/main.c:115: for (j = 3; j > 0; --j) { 
   41BF DD 7E F8      [19]  325 	ld	a, -8 (ix)
   41C2 DD 77 F6      [19]  326 	ld	-10 (ix), a
   41C5 DD 7E F9      [19]  327 	ld	a, -7 (ix)
   41C8 DD 77 F7      [19]  328 	ld	-9 (ix), a
   41CB DD 7E F8      [19]  329 	ld	a, -8 (ix)
   41CE DD 77 FC      [19]  330 	ld	-4 (ix), a
   41D1 DD 7E F9      [19]  331 	ld	a, -7 (ix)
   41D4 DD 77 FD      [19]  332 	ld	-3 (ix), a
   41D7 DD 7E F8      [19]  333 	ld	a, -8 (ix)
   41DA DD 77 FA      [19]  334 	ld	-6 (ix), a
   41DD DD 7E F9      [19]  335 	ld	a, -7 (ix)
   41E0 DD 77 FB      [19]  336 	ld	-5 (ix), a
   41E3 DD 36 F4 03   [19]  337 	ld	-12 (ix), #0x03
                            338 ;src/main.c:116: for (i = 0; i < 80; ++i) {
   41E7                     339 00136$:
   41E7 DD 36 F5 00   [19]  340 	ld	-11 (ix), #0x00
   41EB                     341 00114$:
                            342 ;src/main.c:118: cpct_set2Bits(array2, j, i);
   41EB DD 6E F5      [19]  343 	ld	l, -11 (ix)
   41EE 26 00         [ 7]  344 	ld	h, #0x00
   41F0 DD 5E F4      [19]  345 	ld	e, -12 (ix)
   41F3 16 00         [ 7]  346 	ld	d, #0x00
   41F5 E5            [11]  347 	push	hl
   41F6 DD 6E F6      [19]  348 	ld	l, -10 (ix)
   41F9 DD 66 F7      [19]  349 	ld	h, -9 (ix)
   41FC E5            [11]  350 	push	hl
   41FD FD E1         [14]  351 	pop	iy
   41FF E1            [10]  352 	pop	hl
   4200 E5            [11]  353 	push	hl
   4201 C5            [11]  354 	push	bc
   4202 E5            [11]  355 	push	hl
   4203 D5            [11]  356 	push	de
   4204 FD E5         [15]  357 	push	iy
   4206 CD 2F 44      [17]  358 	call	_cpct_set2Bits
   4209 C1            [10]  359 	pop	bc
   420A E1            [10]  360 	pop	hl
                            361 ;src/main.c:121: printArray((u8*)0xC0A0, array2, 80, f_get2bits);
   420B DD 5E FC      [19]  362 	ld	e, -4 (ix)
   420E DD 56 FD      [19]  363 	ld	d, -3 (ix)
   4211 D5            [11]  364 	push	de
   4212 FD E1         [14]  365 	pop	iy
   4214 E5            [11]  366 	push	hl
   4215 C5            [11]  367 	push	bc
   4216 11 50 01      [10]  368 	ld	de, #0x0150
   4219 D5            [11]  369 	push	de
   421A FD E5         [15]  370 	push	iy
   421C 11 A0 C0      [10]  371 	ld	de, #0xc0a0
   421F D5            [11]  372 	push	de
   4220 CD 00 40      [17]  373 	call	_printArray
   4223 21 06 00      [10]  374 	ld	hl, #6
   4226 39            [11]  375 	add	hl, sp
   4227 F9            [ 6]  376 	ld	sp, hl
   4228 C1            [10]  377 	pop	bc
   4229 E1            [10]  378 	pop	hl
                            379 ;src/main.c:124: cpct_set2Bits(array2, 0, i);
   422A DD 5E FA      [19]  380 	ld	e,-6 (ix)
   422D DD 56 FB      [19]  381 	ld	d,-5 (ix)
   4230 C5            [11]  382 	push	bc
   4231 E5            [11]  383 	push	hl
   4232 21 00 00      [10]  384 	ld	hl, #0x0000
   4235 E5            [11]  385 	push	hl
   4236 D5            [11]  386 	push	de
   4237 CD 2F 44      [17]  387 	call	_cpct_set2Bits
   423A C1            [10]  388 	pop	bc
                            389 ;src/main.c:116: for (i = 0; i < 80; ++i) {
   423B DD 34 F5      [23]  390 	inc	-11 (ix)
   423E DD 7E F5      [19]  391 	ld	a, -11 (ix)
   4241 D6 50         [ 7]  392 	sub	a, #0x50
   4243 38 A6         [12]  393 	jr	C,00114$
                            394 ;src/main.c:115: for (j = 3; j > 0; --j) { 
   4245 DD 35 F4      [23]  395 	dec	-12 (ix)
   4248 DD 7E F4      [19]  396 	ld	a, -12 (ix)
   424B B7            [ 4]  397 	or	a, a
   424C 20 99         [12]  398 	jr	NZ,00136$
                            399 ;src/main.c:133: for (j = 0; j < 16; j++) { 
   424E DD 71 F6      [19]  400 	ld	-10 (ix), c
   4251 DD 70 F7      [19]  401 	ld	-9 (ix), b
   4254 DD 71 FC      [19]  402 	ld	-4 (ix), c
   4257 DD 70 FD      [19]  403 	ld	-3 (ix), b
   425A DD 36 F4 00   [19]  404 	ld	-12 (ix), #0x00
                            405 ;src/main.c:134: for (i = 0; i < 80; ++i) {
   425E                     406 00140$:
   425E DD 36 F5 00   [19]  407 	ld	-11 (ix), #0x00
   4262                     408 00118$:
                            409 ;src/main.c:136: u8 value = (i + j) & 0x0F;
   4262 DD 7E F5      [19]  410 	ld	a, -11 (ix)
   4265 DD 86 F4      [19]  411 	add	a, -12 (ix)
   4268 DD 77 FA      [19]  412 	ld	-6 (ix), a
   426B E6 0F         [ 7]  413 	and	a, #0x0f
   426D DD 77 AD      [19]  414 	ld	-83 (ix), a
                            415 ;src/main.c:139: cpct_set4Bits(array4, value, i);
   4270 DD 7E F5      [19]  416 	ld	a, -11 (ix)
   4273 DD 77 FA      [19]  417 	ld	-6 (ix), a
   4276 DD 36 FB 00   [19]  418 	ld	-5 (ix), #0x00
   427A DD 5E AD      [19]  419 	ld	e, -83 (ix)
   427D 16 00         [ 7]  420 	ld	d, #0x00
   427F DD 4E F6      [19]  421 	ld	c,-10 (ix)
   4282 DD 46 F7      [19]  422 	ld	b,-9 (ix)
   4285 DD 6E FA      [19]  423 	ld	l,-6 (ix)
   4288 DD 66 FB      [19]  424 	ld	h,-5 (ix)
   428B E5            [11]  425 	push	hl
   428C D5            [11]  426 	push	de
   428D C5            [11]  427 	push	bc
   428E CD 78 44      [17]  428 	call	_cpct_set4Bits
                            429 ;src/main.c:140: printArray((u8*)0xC140, array4, 80, f_get4bits);
   4291 DD 4E FC      [19]  430 	ld	c,-4 (ix)
   4294 DD 46 FD      [19]  431 	ld	b,-3 (ix)
   4297 21 50 02      [10]  432 	ld	hl, #0x0250
   429A E5            [11]  433 	push	hl
   429B C5            [11]  434 	push	bc
   429C 21 40 C1      [10]  435 	ld	hl, #0xc140
   429F E5            [11]  436 	push	hl
   42A0 CD 00 40      [17]  437 	call	_printArray
   42A3 21 06 00      [10]  438 	ld	hl, #6
   42A6 39            [11]  439 	add	hl, sp
   42A7 F9            [ 6]  440 	ld	sp, hl
                            441 ;src/main.c:134: for (i = 0; i < 80; ++i) {
   42A8 DD 34 F5      [23]  442 	inc	-11 (ix)
   42AB DD 7E F5      [19]  443 	ld	a, -11 (ix)
   42AE D6 50         [ 7]  444 	sub	a, #0x50
   42B0 38 B0         [12]  445 	jr	C,00118$
                            446 ;src/main.c:133: for (j = 0; j < 16; j++) { 
   42B2 DD 34 F4      [23]  447 	inc	-12 (ix)
   42B5 DD 7E F4      [19]  448 	ld	a, -12 (ix)
   42B8 D6 10         [ 7]  449 	sub	a, #0x10
   42BA 38 A2         [12]  450 	jr	C,00140$
                            451 ;src/main.c:147: for (i = 0; i < 80; ++i) {
   42BC DD 7E FE      [19]  452 	ld	a, -2 (ix)
   42BF DD 77 F6      [19]  453 	ld	-10 (ix), a
   42C2 DD 7E FF      [19]  454 	ld	a, -1 (ix)
   42C5 DD 77 F7      [19]  455 	ld	-9 (ix), a
   42C8 DD 7E FE      [19]  456 	ld	a, -2 (ix)
   42CB DD 77 FC      [19]  457 	ld	-4 (ix), a
   42CE DD 7E FF      [19]  458 	ld	a, -1 (ix)
   42D1 DD 77 FD      [19]  459 	ld	-3 (ix), a
   42D4 DD 36 F5 00   [19]  460 	ld	-11 (ix), #0x00
   42D8                     461 00122$:
                            462 ;src/main.c:149: cpct_setBit(array1, 1, i);
   42D8 DD 5E F5      [19]  463 	ld	e, -11 (ix)
   42DB 16 00         [ 7]  464 	ld	d, #0x00
   42DD DD 4E F6      [19]  465 	ld	c,-10 (ix)
   42E0 DD 46 F7      [19]  466 	ld	b,-9 (ix)
   42E3 D5            [11]  467 	push	de
   42E4 21 01 00      [10]  468 	ld	hl, #0x0001
   42E7 E5            [11]  469 	push	hl
   42E8 C5            [11]  470 	push	bc
   42E9 CD B0 43      [17]  471 	call	_cpct_setBit
                            472 ;src/main.c:152: printArray(CPCT_VMEM_START, array1, 80, f_getbit); 
   42EC DD 4E FC      [19]  473 	ld	c,-4 (ix)
   42EF DD 46 FD      [19]  474 	ld	b,-3 (ix)
   42F2 21 50 00      [10]  475 	ld	hl, #0x0050
   42F5 E5            [11]  476 	push	hl
   42F6 C5            [11]  477 	push	bc
   42F7 21 00 C0      [10]  478 	ld	hl, #0xc000
   42FA E5            [11]  479 	push	hl
   42FB CD 00 40      [17]  480 	call	_printArray
   42FE 21 06 00      [10]  481 	ld	hl, #6
   4301 39            [11]  482 	add	hl, sp
   4302 F9            [ 6]  483 	ld	sp, hl
                            484 ;src/main.c:147: for (i = 0; i < 80; ++i) {
   4303 DD 34 F5      [23]  485 	inc	-11 (ix)
   4306 DD 7E F5      [19]  486 	ld	a, -11 (ix)
   4309 D6 50         [ 7]  487 	sub	a, #0x50
   430B 38 CB         [12]  488 	jr	C,00122$
                            489 ;src/main.c:158: for (j = 3; j > 0; --j) { 
   430D DD 4E F8      [19]  490 	ld	c,-8 (ix)
   4310 DD 46 F9      [19]  491 	ld	b,-7 (ix)
   4313 DD 5E F8      [19]  492 	ld	e,-8 (ix)
   4316 DD 56 F9      [19]  493 	ld	d,-7 (ix)
   4319 DD 36 F4 03   [19]  494 	ld	-12 (ix), #0x03
                            495 ;src/main.c:159: for (i = 0; i < 80; ++i) {
   431D                     496 00146$:
   431D DD 36 F5 00   [19]  497 	ld	-11 (ix), #0x00
   4321                     498 00124$:
                            499 ;src/main.c:161: cpct_set2Bits(array2, j, i);
   4321 DD 6E F5      [19]  500 	ld	l, -11 (ix)
   4324 26 00         [ 7]  501 	ld	h, #0x00
   4326 DD 7E F4      [19]  502 	ld	a, -12 (ix)
   4329 DD 77 F6      [19]  503 	ld	-10 (ix), a
   432C DD 36 F7 00   [19]  504 	ld	-9 (ix), #0x00
   4330 C5            [11]  505 	push	bc
   4331 FD E1         [14]  506 	pop	iy
   4333 C5            [11]  507 	push	bc
   4334 D5            [11]  508 	push	de
   4335 E5            [11]  509 	push	hl
   4336 DD 6E F6      [19]  510 	ld	l,-10 (ix)
   4339 DD 66 F7      [19]  511 	ld	h,-9 (ix)
   433C E5            [11]  512 	push	hl
   433D FD E5         [15]  513 	push	iy
   433F CD 2F 44      [17]  514 	call	_cpct_set2Bits
   4342 D1            [10]  515 	pop	de
   4343 C1            [10]  516 	pop	bc
                            517 ;src/main.c:164: printArray((u8*)0xC0A0, array2, 80, f_get2bits); 
   4344 D5            [11]  518 	push	de
   4345 FD E1         [14]  519 	pop	iy
   4347 C5            [11]  520 	push	bc
   4348 D5            [11]  521 	push	de
   4349 21 50 01      [10]  522 	ld	hl, #0x0150
   434C E5            [11]  523 	push	hl
   434D FD E5         [15]  524 	push	iy
   434F 21 A0 C0      [10]  525 	ld	hl, #0xc0a0
   4352 E5            [11]  526 	push	hl
   4353 CD 00 40      [17]  527 	call	_printArray
   4356 21 06 00      [10]  528 	ld	hl, #6
   4359 39            [11]  529 	add	hl, sp
   435A F9            [ 6]  530 	ld	sp, hl
   435B D1            [10]  531 	pop	de
   435C C1            [10]  532 	pop	bc
                            533 ;src/main.c:159: for (i = 0; i < 80; ++i) {
   435D DD 34 F5      [23]  534 	inc	-11 (ix)
   4360 DD 7E F5      [19]  535 	ld	a, -11 (ix)
   4363 D6 50         [ 7]  536 	sub	a, #0x50
   4365 38 BA         [12]  537 	jr	C,00124$
                            538 ;src/main.c:158: for (j = 3; j > 0; --j) { 
   4367 DD 35 F4      [23]  539 	dec	-12 (ix)
   436A DD 7E F4      [19]  540 	ld	a, -12 (ix)
   436D B7            [ 4]  541 	or	a, a
   436E 20 AD         [12]  542 	jr	NZ,00146$
   4370 C3 FE 40      [10]  543 	jp	00110$
                            544 	.area _CODE
                            545 	.area _INITIALIZER
                            546 	.area _CABS (ABS)
