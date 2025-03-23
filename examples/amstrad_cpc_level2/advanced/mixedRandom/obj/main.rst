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
                             12 	.globl _drawPixelCount
                             13 	.globl _putpixel
                             14 	.globl _mixedRandomGenerator
                             15 	.globl _initializeRandomGenerators
                             16 	.globl _sprintf
                             17 	.globl _cpct_getRandom_glfsr16_u8
                             18 	.globl _cpct_setTaps_glfsr16
                             19 	.globl _cpct_setSeed_glfsr16
                             20 	.globl _cpct_setSeed_lcg_u8
                             21 	.globl _cpct_getRandom_lcg_u8
                             22 	.globl _cpct_getScreenPtr
                             23 	.globl _cpct_setVideoMode
                             24 	.globl _cpct_drawStringM2
                             25 	.globl _cpct_setDrawCharM2
                             26 	.globl _cpct_disableFirmware
                             27 ;--------------------------------------------------------
                             28 ; special function registers
                             29 ;--------------------------------------------------------
                             30 ;--------------------------------------------------------
                             31 ; ram data
                             32 ;--------------------------------------------------------
                             33 	.area _DATA
                             34 ;--------------------------------------------------------
                             35 ; ram data
                             36 ;--------------------------------------------------------
                             37 	.area _INITIALIZED
                             38 ;--------------------------------------------------------
                             39 ; absolute external ram data
                             40 ;--------------------------------------------------------
                             41 	.area _DABS (ABS)
                             42 ;--------------------------------------------------------
                             43 ; global & static initialisations
                             44 ;--------------------------------------------------------
                             45 	.area _HOME
                             46 	.area _GSINIT
                             47 	.area _GSFINAL
                             48 	.area _GSINIT
                             49 ;--------------------------------------------------------
                             50 ; Home
                             51 ;--------------------------------------------------------
                             52 	.area _HOME
                             53 	.area _HOME
                             54 ;--------------------------------------------------------
                             55 ; code
                             56 ;--------------------------------------------------------
                             57 	.area _CODE
                             58 ;src/main.c:28: void initializeRandomGenerators() {
                             59 ;	---------------------------------
                             60 ; Function initializeRandomGenerators
                             61 ; ---------------------------------
   4000                      62 _initializeRandomGenerators::
                             63 ;src/main.c:29: cpct_setSeed_lcg_u8 (0x55);
   4000 2E 55         [ 7]   64 	ld	l, #0x55
   4002 CD 88 41      [17]   65 	call	_cpct_setSeed_lcg_u8
                             66 ;src/main.c:30: cpct_setSeed_glfsr16(0x1120);
   4005 21 20 11      [10]   67 	ld	hl, #0x1120
   4008 CD 8D 41      [17]   68 	call	_cpct_setSeed_glfsr16
                             69 ;src/main.c:31: cpct_setTaps_glfsr16(GLFSR16_TAPSET_0512);
   400B 21 D0 BA      [10]   70 	ld	hl, #0xbad0
   400E C3 42 42      [10]   71 	jp  _cpct_setTaps_glfsr16
                             72 ;src/main.c:34: u8 mixedRandomGenerator() {
                             73 ;	---------------------------------
                             74 ; Function mixedRandomGenerator
                             75 ; ---------------------------------
   4011                      76 _mixedRandomGenerator::
                             77 ;src/main.c:35: return cpct_getRandom_lcg_u8( cpct_getRandom_glfsr16_u8() );
   4011 CD 91 41      [17]   78 	call	_cpct_getRandom_glfsr16_u8
   4014 C3 31 42      [10]   79 	jp  _cpct_getRandom_lcg_u8
                             80 ;src/main.c:38: void putpixel(u16 x, u8 y, u8 val) {
                             81 ;	---------------------------------
                             82 ; Function putpixel
                             83 ; ---------------------------------
   4017                      84 _putpixel::
   4017 DD E5         [15]   85 	push	ix
   4019 DD 21 00 00   [14]   86 	ld	ix,#0
   401D DD 39         [15]   87 	add	ix,sp
                             88 ;src/main.c:39: u8* vram = cpct_getScreenPtr(CPCT_VMEM_START, x >> 3, y + 8);
   401F DD 7E 06      [19]   89 	ld	a, 6 (ix)
   4022 C6 08         [ 7]   90 	add	a, #0x08
   4024 57            [ 4]   91 	ld	d, a
   4025 DD 46 04      [19]   92 	ld	b, 4 (ix)
   4028 DD 4E 05      [19]   93 	ld	c, 5 (ix)
   402B CB 39         [ 8]   94 	srl	c
   402D CB 18         [ 8]   95 	rr	b
   402F CB 39         [ 8]   96 	srl	c
   4031 CB 18         [ 8]   97 	rr	b
   4033 CB 39         [ 8]   98 	srl	c
   4035 CB 18         [ 8]   99 	rr	b
   4037 58            [ 4]  100 	ld	e, b
   4038 D5            [11]  101 	push	de
   4039 21 00 C0      [10]  102 	ld	hl, #0xc000
   403C E5            [11]  103 	push	hl
   403D CD 6A 42      [17]  104 	call	_cpct_getScreenPtr
                            105 ;src/main.c:40: u8  byte = *vram;
   4040 46            [ 7]  106 	ld	b, (hl)
                            107 ;src/main.c:41: u8  pen  = val << (7 - (x & 7));
   4041 DD 7E 04      [19]  108 	ld	a, 4 (ix)
   4044 E6 07         [ 7]  109 	and	a, #0x07
   4046 4F            [ 4]  110 	ld	c, a
   4047 3E 07         [ 7]  111 	ld	a, #0x07
   4049 91            [ 4]  112 	sub	a, c
   404A DD 4E 07      [19]  113 	ld	c, 7 (ix)
   404D 3C            [ 4]  114 	inc	a
   404E 18 02         [12]  115 	jr	00104$
   4050                     116 00103$:
   4050 CB 21         [ 8]  117 	sla	c
   4052                     118 00104$:
   4052 3D            [ 4]  119 	dec	a
   4053 20 FB         [12]  120 	jr	NZ,00103$
                            121 ;src/main.c:42: *vram = byte & (pen ^ 0xFF) | pen;
   4055 79            [ 4]  122 	ld	a, c
   4056 EE FF         [ 7]  123 	xor	a, #0xff
   4058 A0            [ 4]  124 	and	a, b
   4059 B1            [ 4]  125 	or	a, c
   405A 77            [ 7]  126 	ld	(hl), a
   405B DD E1         [14]  127 	pop	ix
   405D C9            [10]  128 	ret
                            129 ;src/main.c:45: void drawPixelCount(u16 pixels) {
                            130 ;	---------------------------------
                            131 ; Function drawPixelCount
                            132 ; ---------------------------------
   405E                     133 _drawPixelCount::
   405E DD E5         [15]  134 	push	ix
   4060 DD 21 00 00   [14]  135 	ld	ix,#0
   4064 DD 39         [15]  136 	add	ix,sp
   4066 21 F9 FF      [10]  137 	ld	hl, #-7
   4069 39            [11]  138 	add	hl, sp
   406A F9            [ 6]  139 	ld	sp, hl
                            140 ;src/main.c:46: if (! (pixels & 15) ) {
   406B DD 7E 04      [19]  141 	ld	a, 4 (ix)
   406E E6 0F         [ 7]  142 	and	a, #0x0f
   4070 20 24         [12]  143 	jr	NZ,00103$
                            144 ;src/main.c:48: sprintf(str, "%6u", pixels);
   4072 21 00 00      [10]  145 	ld	hl, #0x0000
   4075 39            [11]  146 	add	hl, sp
   4076 4D            [ 4]  147 	ld	c, l
   4077 44            [ 4]  148 	ld	b, h
   4078 E5            [11]  149 	push	hl
   4079 DD 5E 04      [19]  150 	ld	e,4 (ix)
   407C DD 56 05      [19]  151 	ld	d,5 (ix)
   407F D5            [11]  152 	push	de
   4080 11 9B 40      [10]  153 	ld	de, #___str_0
   4083 D5            [11]  154 	push	de
   4084 C5            [11]  155 	push	bc
   4085 CD FC 41      [17]  156 	call	_sprintf
   4088 21 06 00      [10]  157 	ld	hl, #6
   408B 39            [11]  158 	add	hl, sp
   408C F9            [ 6]  159 	ld	sp, hl
   408D E1            [10]  160 	pop	hl
                            161 ;src/main.c:49: cpct_drawStringM2(str, CPCT_VMEM_START+26);
   408E 01 1A C0      [10]  162 	ld	bc, #0xc01a
   4091 C5            [11]  163 	push	bc
   4092 E5            [11]  164 	push	hl
   4093 CD 33 41      [17]  165 	call	_cpct_drawStringM2
   4096                     166 00103$:
   4096 DD F9         [10]  167 	ld	sp, ix
   4098 DD E1         [14]  168 	pop	ix
   409A C9            [10]  169 	ret
   409B                     170 ___str_0:
   409B 25 36 75            171 	.ascii "%6u"
   409E 00                  172 	.db 0x00
                            173 ;src/main.c:53: void main(void) {
                            174 ;	---------------------------------
                            175 ; Function main
                            176 ; ---------------------------------
   409F                     177 _main::
   409F DD E5         [15]  178 	push	ix
   40A1 DD 21 00 00   [14]  179 	ld	ix,#0
   40A5 DD 39         [15]  180 	add	ix,sp
   40A7 21 FA FF      [10]  181 	ld	hl, #-6
   40AA 39            [11]  182 	add	hl, sp
   40AB F9            [ 6]  183 	ld	sp, hl
                            184 ;src/main.c:54: u8 last_y = 0x20;
   40AC DD 36 FB 20   [19]  185 	ld	-5 (ix), #0x20
                            186 ;src/main.c:57: cpct_disableFirmware();
   40B0 CD 59 42      [17]  187 	call	_cpct_disableFirmware
                            188 ;src/main.c:58: cpct_setVideoMode(2);
   40B3 2E 02         [ 7]  189 	ld	l, #0x02
   40B5 CD 4B 42      [17]  190 	call	_cpct_setVideoMode
                            191 ;src/main.c:59: cpct_setDrawCharM2(1, 0);
   40B8 21 01 00      [10]  192 	ld	hl, #0x0001
   40BB E5            [11]  193 	push	hl
   40BC CD 80 42      [17]  194 	call	_cpct_setDrawCharM2
                            195 ;src/main.c:60: initializeRandomGenerators();
   40BF CD 00 40      [17]  196 	call	_initializeRandomGenerators
                            197 ;src/main.c:62: cpct_drawStringM2("Random numbers generated:", CPCT_VMEM_START);
   40C2 21 00 C0      [10]  198 	ld	hl, #0xc000
   40C5 E5            [11]  199 	push	hl
   40C6 21 19 41      [10]  200 	ld	hl, #___str_1
   40C9 E5            [11]  201 	push	hl
   40CA CD 33 41      [17]  202 	call	_cpct_drawStringM2
                            203 ;src/main.c:63: while(1) {
   40CD AF            [ 4]  204 	xor	a, a
   40CE DD 77 FC      [19]  205 	ld	-4 (ix), a
   40D1 DD 77 FD      [19]  206 	ld	-3 (ix), a
   40D4 DD 77 FE      [19]  207 	ld	-2 (ix), a
   40D7 DD 77 FF      [19]  208 	ld	-1 (ix), a
   40DA                     209 00102$:
                            210 ;src/main.c:64: u8 y = mixedRandomGenerator();
   40DA CD 11 40      [17]  211 	call	_mixedRandomGenerator
                            212 ;src/main.c:65: putpixel(last_y, y>>1, 1);
   40DD DD 75 FA      [19]  213 	ld	-6 (ix), l
   40E0 55            [ 4]  214 	ld	d, l
   40E1 CB 3A         [ 8]  215 	srl	d
   40E3 DD 4E FB      [19]  216 	ld	c, -5 (ix)
   40E6 06 00         [ 7]  217 	ld	b, #0x00
   40E8 3E 01         [ 7]  218 	ld	a, #0x01
   40EA F5            [11]  219 	push	af
   40EB 33            [ 6]  220 	inc	sp
   40EC D5            [11]  221 	push	de
   40ED 33            [ 6]  222 	inc	sp
   40EE C5            [11]  223 	push	bc
   40EF CD 17 40      [17]  224 	call	_putpixel
   40F2 F1            [10]  225 	pop	af
   40F3 F1            [10]  226 	pop	af
                            227 ;src/main.c:66: drawPixelCount(i++);
   40F4 DD 4E FC      [19]  228 	ld	c, -4 (ix)
   40F7 DD 46 FD      [19]  229 	ld	b, -3 (ix)
   40FA DD 34 FC      [23]  230 	inc	-4 (ix)
   40FD 20 0D         [12]  231 	jr	NZ,00110$
   40FF DD 34 FD      [23]  232 	inc	-3 (ix)
   4102 20 08         [12]  233 	jr	NZ,00110$
   4104 DD 34 FE      [23]  234 	inc	-2 (ix)
   4107 20 03         [12]  235 	jr	NZ,00110$
   4109 DD 34 FF      [23]  236 	inc	-1 (ix)
   410C                     237 00110$:
   410C C5            [11]  238 	push	bc
   410D CD 5E 40      [17]  239 	call	_drawPixelCount
   4110 F1            [10]  240 	pop	af
                            241 ;src/main.c:67: last_y = y;
   4111 DD 7E FA      [19]  242 	ld	a, -6 (ix)
   4114 DD 77 FB      [19]  243 	ld	-5 (ix), a
   4117 18 C1         [12]  244 	jr	00102$
   4119                     245 ___str_1:
   4119 52 61 6E 64 6F 6D   246 	.ascii "Random numbers generated:"
        20 6E 75 6D 62 65
        72 73 20 67 65 6E
        65 72 61 74 65 64
        3A
   4132 00                  247 	.db 0x00
                            248 	.area _CODE
                            249 	.area _INITIALIZER
                            250 	.area _CABS (ABS)
