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
                             12 	.globl _wait_frames
                             13 	.globl _cpct_waitVSYNC
                             14 	.globl _cpct_setVideoMode
                             15 	.globl _cpct_drawStringM2
                             16 	.globl _cpct_drawStringM1
                             17 	.globl _cpct_drawStringM0
                             18 	.globl _cpct_setDrawCharM2
                             19 	.globl _cpct_setDrawCharM1
                             20 	.globl _cpct_setDrawCharM0
                             21 	.globl _cpct_memset
                             22 	.globl _cpct_disableFirmware
                             23 ;--------------------------------------------------------
                             24 ; special function registers
                             25 ;--------------------------------------------------------
                             26 ;--------------------------------------------------------
                             27 ; ram data
                             28 ;--------------------------------------------------------
                             29 	.area _DATA
                             30 ;--------------------------------------------------------
                             31 ; ram data
                             32 ;--------------------------------------------------------
                             33 	.area _INITIALIZED
                             34 ;--------------------------------------------------------
                             35 ; absolute external ram data
                             36 ;--------------------------------------------------------
                             37 	.area _DABS (ABS)
                             38 ;--------------------------------------------------------
                             39 ; global & static initialisations
                             40 ;--------------------------------------------------------
                             41 	.area _HOME
                             42 	.area _GSINIT
                             43 	.area _GSFINAL
                             44 	.area _GSINIT
                             45 ;--------------------------------------------------------
                             46 ; Home
                             47 ;--------------------------------------------------------
                             48 	.area _HOME
                             49 	.area _HOME
                             50 ;--------------------------------------------------------
                             51 ; code
                             52 ;--------------------------------------------------------
                             53 	.area _CODE
                             54 ;src/main.c:30: void wait_frames(u16 nframes) {
                             55 ;	---------------------------------
                             56 ; Function wait_frames
                             57 ; ---------------------------------
   4000                      58 _wait_frames::
   4000 DD E5         [15]   59 	push	ix
   4002 DD 21 00 00   [14]   60 	ld	ix,#0
   4006 DD 39         [15]   61 	add	ix,sp
                             62 ;src/main.c:34: for (i=0; i < nframes; i++) {
   4008 01 00 00      [10]   63 	ld	bc, #0x0000
   400B                      64 00107$:
   400B 79            [ 4]   65 	ld	a, c
   400C DD 96 04      [19]   66 	sub	a, 4 (ix)
   400F 78            [ 4]   67 	ld	a, b
   4010 DD 9E 05      [19]   68 	sbc	a, 5 (ix)
   4013 30 13         [12]   69 	jr	NC,00109$
                             70 ;src/main.c:35: cpct_waitVSYNC();
   4015 C5            [11]   71 	push	bc
   4016 CD 41 44      [17]   72 	call	_cpct_waitVSYNC
   4019 C1            [10]   73 	pop	bc
                             74 ;src/main.c:42: for (j=0; j < 750; j++);
   401A 11 EE 02      [10]   75 	ld	de, #0x02ee
   401D                      76 00105$:
   401D EB            [ 4]   77 	ex	de,hl
   401E 2B            [ 6]   78 	dec	hl
   401F 5D            [ 4]   79 	ld	e, l
   4020 7C            [ 4]   80 	ld	a,h
   4021 57            [ 4]   81 	ld	d,a
   4022 B5            [ 4]   82 	or	a,l
   4023 20 F8         [12]   83 	jr	NZ,00105$
                             84 ;src/main.c:34: for (i=0; i < nframes; i++) {
   4025 03            [ 6]   85 	inc	bc
   4026 18 E3         [12]   86 	jr	00107$
   4028                      87 00109$:
   4028 DD E1         [14]   88 	pop	ix
   402A C9            [10]   89 	ret
                             90 ;src/main.c:49: void main(void) {
                             91 ;	---------------------------------
                             92 ; Function main
                             93 ; ---------------------------------
   402B                      94 _main::
   402B DD E5         [15]   95 	push	ix
   402D DD 21 00 00   [14]   96 	ld	ix,#0
   4031 DD 39         [15]   97 	add	ix,sp
   4033 21 EA FF      [10]   98 	ld	hl, #-22
   4036 39            [11]   99 	add	hl, sp
                            100 ;src/main.c:52: u8 colours[6] = {0};  // 5 Colour values, 2 for each mode
   4037 F9            [ 6]  101 	ld	sp, hl
   4038 23            [ 6]  102 	inc	hl
   4039 23            [ 6]  103 	inc	hl
   403A DD 75 FE      [19]  104 	ld	-2 (ix), l
   403D DD 74 FF      [19]  105 	ld	-1 (ix), h
   4040 36 00         [10]  106 	ld	(hl), #0x00
   4042 DD 7E FE      [19]  107 	ld	a, -2 (ix)
   4045 C6 01         [ 7]  108 	add	a, #0x01
   4047 DD 77 FB      [19]  109 	ld	-5 (ix), a
   404A DD 7E FF      [19]  110 	ld	a, -1 (ix)
   404D CE 00         [ 7]  111 	adc	a, #0x00
   404F DD 77 FC      [19]  112 	ld	-4 (ix), a
   4052 DD 6E FB      [19]  113 	ld	l,-5 (ix)
   4055 DD 66 FC      [19]  114 	ld	h,-4 (ix)
   4058 36 00         [10]  115 	ld	(hl), #0x00
   405A DD 7E FE      [19]  116 	ld	a, -2 (ix)
   405D C6 02         [ 7]  117 	add	a, #0x02
   405F DD 77 F3      [19]  118 	ld	-13 (ix), a
   4062 DD 7E FF      [19]  119 	ld	a, -1 (ix)
   4065 CE 00         [ 7]  120 	adc	a, #0x00
   4067 DD 77 F4      [19]  121 	ld	-12 (ix), a
   406A DD 6E F3      [19]  122 	ld	l,-13 (ix)
   406D DD 66 F4      [19]  123 	ld	h,-12 (ix)
   4070 36 00         [10]  124 	ld	(hl), #0x00
   4072 DD 7E FE      [19]  125 	ld	a, -2 (ix)
   4075 C6 03         [ 7]  126 	add	a, #0x03
   4077 DD 77 F5      [19]  127 	ld	-11 (ix), a
   407A DD 7E FF      [19]  128 	ld	a, -1 (ix)
   407D CE 00         [ 7]  129 	adc	a, #0x00
   407F DD 77 F6      [19]  130 	ld	-10 (ix), a
   4082 DD 6E F5      [19]  131 	ld	l,-11 (ix)
   4085 DD 66 F6      [19]  132 	ld	h,-10 (ix)
   4088 36 00         [10]  133 	ld	(hl), #0x00
   408A DD 7E FE      [19]  134 	ld	a, -2 (ix)
   408D C6 04         [ 7]  135 	add	a, #0x04
   408F DD 77 F7      [19]  136 	ld	-9 (ix), a
   4092 DD 7E FF      [19]  137 	ld	a, -1 (ix)
   4095 CE 00         [ 7]  138 	adc	a, #0x00
   4097 DD 77 F8      [19]  139 	ld	-8 (ix), a
   409A DD 6E F7      [19]  140 	ld	l,-9 (ix)
   409D DD 66 F8      [19]  141 	ld	h,-8 (ix)
   40A0 36 00         [10]  142 	ld	(hl), #0x00
   40A2 DD 7E FE      [19]  143 	ld	a, -2 (ix)
   40A5 C6 05         [ 7]  144 	add	a, #0x05
   40A7 DD 77 F9      [19]  145 	ld	-7 (ix), a
   40AA DD 7E FF      [19]  146 	ld	a, -1 (ix)
   40AD CE 00         [ 7]  147 	adc	a, #0x00
   40AF DD 77 FA      [19]  148 	ld	-6 (ix), a
   40B2 DD 6E F9      [19]  149 	ld	l,-7 (ix)
   40B5 DD 66 FA      [19]  150 	ld	h,-6 (ix)
   40B8 36 00         [10]  151 	ld	(hl), #0x00
                            152 ;src/main.c:56: cpct_disableFirmware();
   40BA CD 65 44      [17]  153 	call	_cpct_disableFirmware
                            154 ;src/main.c:60: while(1) {
   40BD                     155 00105$:
                            156 ;src/main.c:67: cpct_clearScreen(0);
   40BD 21 00 40      [10]  157 	ld	hl, #0x4000
   40C0 E5            [11]  158 	push	hl
   40C1 AF            [ 4]  159 	xor	a, a
   40C2 F5            [11]  160 	push	af
   40C3 33            [ 6]  161 	inc	sp
   40C4 26 C0         [ 7]  162 	ld	h, #0xc0
   40C6 E5            [11]  163 	push	hl
   40C7 CD 57 44      [17]  164 	call	_cpct_memset
                            165 ;src/main.c:68: cpct_setVideoMode(0);
   40CA 2E 00         [ 7]  166 	ld	l, #0x00
   40CC CD 49 44      [17]  167 	call	_cpct_setVideoMode
                            168 ;src/main.c:74: for (times=0; times < 25; times++) {
   40CF 21 00 C0      [10]  169 	ld	hl, #0xc000
   40D2 E3            [19]  170 	ex	(sp), hl
   40D3 DD 36 F2 00   [19]  171 	ld	-14 (ix), #0x00
   40D7                     172 00107$:
                            173 ;src/main.c:78: colours[0] = ++colours[0] & 15;
   40D7 DD 6E FE      [19]  174 	ld	l,-2 (ix)
   40DA DD 66 FF      [19]  175 	ld	h,-1 (ix)
   40DD 7E            [ 7]  176 	ld	a, (hl)
   40DE DD 77 FD      [19]  177 	ld	-3 (ix), a
   40E1 3C            [ 4]  178 	inc	a
   40E2 DD 6E FE      [19]  179 	ld	l,-2 (ix)
   40E5 DD 66 FF      [19]  180 	ld	h,-1 (ix)
   40E8 77            [ 7]  181 	ld	(hl), a
   40E9 E6 0F         [ 7]  182 	and	a, #0x0f
   40EB 47            [ 4]  183 	ld	b, a
   40EC DD 6E FE      [19]  184 	ld	l,-2 (ix)
   40EF DD 66 FF      [19]  185 	ld	h,-1 (ix)
   40F2 70            [ 7]  186 	ld	(hl), b
                            187 ;src/main.c:81: cpct_setDrawCharM0(colours[0], colours[3]);
   40F3 DD 6E F5      [19]  188 	ld	l,-11 (ix)
   40F6 DD 66 F6      [19]  189 	ld	h,-10 (ix)
   40F9 56            [ 7]  190 	ld	d, (hl)
   40FA 58            [ 4]  191 	ld	e, b
   40FB D5            [11]  192 	push	de
   40FC CD 76 44      [17]  193 	call	_cpct_setDrawCharM0
                            194 ;src/main.c:82: cpct_drawStringM0("$ Mode 0 string $", pvideomem);
   40FF C1            [10]  195 	pop	bc
   4100 C5            [11]  196 	push	bc
   4101 C5            [11]  197 	push	bc
   4102 21 7E 42      [10]  198 	ld	hl, #___str_0
   4105 E5            [11]  199 	push	hl
   4106 CD CE 42      [17]  200 	call	_cpct_drawStringM0
                            201 ;src/main.c:83: wait_frames(WFRAMES);
   4109 21 03 00      [10]  202 	ld	hl, #0x0003
   410C E5            [11]  203 	push	hl
   410D CD 00 40      [17]  204 	call	_wait_frames
   4110 F1            [10]  205 	pop	af
                            206 ;src/main.c:86: pvideomem += 0x50;
   4111 DD 7E EA      [19]  207 	ld	a, -22 (ix)
   4114 C6 50         [ 7]  208 	add	a, #0x50
   4116 DD 77 EA      [19]  209 	ld	-22 (ix), a
   4119 DD 7E EB      [19]  210 	ld	a, -21 (ix)
   411C CE 00         [ 7]  211 	adc	a, #0x00
   411E DD 77 EB      [19]  212 	ld	-21 (ix), a
                            213 ;src/main.c:74: for (times=0; times < 25; times++) {
   4121 DD 34 F2      [23]  214 	inc	-14 (ix)
   4124 DD 7E F2      [19]  215 	ld	a, -14 (ix)
   4127 D6 19         [ 7]  216 	sub	a, #0x19
   4129 38 AC         [12]  217 	jr	C,00107$
                            218 ;src/main.c:89: colours[3] = ++colours[3] & 15;
   412B DD 6E F5      [19]  219 	ld	l,-11 (ix)
   412E DD 66 F6      [19]  220 	ld	h,-10 (ix)
   4131 7E            [ 7]  221 	ld	a, (hl)
   4132 3C            [ 4]  222 	inc	a
   4133 DD 6E F5      [19]  223 	ld	l,-11 (ix)
   4136 DD 66 F6      [19]  224 	ld	h,-10 (ix)
   4139 77            [ 7]  225 	ld	(hl), a
   413A E6 0F         [ 7]  226 	and	a, #0x0f
   413C DD 6E F5      [19]  227 	ld	l,-11 (ix)
   413F DD 66 F6      [19]  228 	ld	h,-10 (ix)
   4142 77            [ 7]  229 	ld	(hl), a
                            230 ;src/main.c:96: cpct_clearScreen(0);
   4143 21 00 40      [10]  231 	ld	hl, #0x4000
   4146 E5            [11]  232 	push	hl
   4147 AF            [ 4]  233 	xor	a, a
   4148 F5            [11]  234 	push	af
   4149 33            [ 6]  235 	inc	sp
   414A 26 C0         [ 7]  236 	ld	h, #0xc0
   414C E5            [11]  237 	push	hl
   414D CD 57 44      [17]  238 	call	_cpct_memset
                            239 ;src/main.c:97: cpct_setVideoMode(1);
   4150 2E 01         [ 7]  240 	ld	l, #0x01
   4152 CD 49 44      [17]  241 	call	_cpct_setVideoMode
                            242 ;src/main.c:103: for (times=0; times < 25; times++) {
   4155 01 00 C0      [10]  243 	ld	bc, #0xc000
   4158 DD 36 F2 00   [19]  244 	ld	-14 (ix), #0x00
   415C                     245 00109$:
                            246 ;src/main.c:106: colours[1] = ++colours[1] & 3;
   415C DD 6E FB      [19]  247 	ld	l,-5 (ix)
   415F DD 66 FC      [19]  248 	ld	h,-4 (ix)
   4162 7E            [ 7]  249 	ld	a, (hl)
   4163 3C            [ 4]  250 	inc	a
   4164 DD 6E FB      [19]  251 	ld	l,-5 (ix)
   4167 DD 66 FC      [19]  252 	ld	h,-4 (ix)
   416A 77            [ 7]  253 	ld	(hl), a
   416B E6 03         [ 7]  254 	and	a, #0x03
   416D 57            [ 4]  255 	ld	d, a
   416E DD 6E FB      [19]  256 	ld	l,-5 (ix)
   4171 DD 66 FC      [19]  257 	ld	h,-4 (ix)
   4174 72            [ 7]  258 	ld	(hl), d
                            259 ;src/main.c:109: cpct_setDrawCharM1(colours[1], colours[4]);
   4175 DD 6E F7      [19]  260 	ld	l,-9 (ix)
   4178 DD 66 F8      [19]  261 	ld	h,-8 (ix)
   417B 66            [ 7]  262 	ld	h, (hl)
   417C C5            [11]  263 	push	bc
   417D 6A            [ 4]  264 	ld	l, d
   417E E5            [11]  265 	push	hl
   417F CD 9B 44      [17]  266 	call	_cpct_setDrawCharM1
   4182 C1            [10]  267 	pop	bc
                            268 ;src/main.c:110: cpct_drawStringM1("Mode 1 string :D", pvideomem);
   4183 59            [ 4]  269 	ld	e, c
   4184 50            [ 4]  270 	ld	d, b
   4185 C5            [11]  271 	push	bc
   4186 D5            [11]  272 	push	de
   4187 21 90 42      [10]  273 	ld	hl, #___str_1
   418A E5            [11]  274 	push	hl
   418B CD 08 43      [17]  275 	call	_cpct_drawStringM1
   418E C1            [10]  276 	pop	bc
                            277 ;src/main.c:112: colours[1] = ++colours[1] & 3;
   418F DD 6E FB      [19]  278 	ld	l,-5 (ix)
   4192 DD 66 FC      [19]  279 	ld	h,-4 (ix)
   4195 7E            [ 7]  280 	ld	a, (hl)
   4196 3C            [ 4]  281 	inc	a
   4197 DD 6E FB      [19]  282 	ld	l,-5 (ix)
   419A DD 66 FC      [19]  283 	ld	h,-4 (ix)
   419D 77            [ 7]  284 	ld	(hl), a
   419E E6 03         [ 7]  285 	and	a, #0x03
   41A0 57            [ 4]  286 	ld	d, a
   41A1 DD 6E FB      [19]  287 	ld	l,-5 (ix)
   41A4 DD 66 FC      [19]  288 	ld	h,-4 (ix)
   41A7 72            [ 7]  289 	ld	(hl), d
                            290 ;src/main.c:113: cpct_setDrawCharM1(colours[1], colours[4]);
   41A8 DD 6E F7      [19]  291 	ld	l,-9 (ix)
   41AB DD 66 F8      [19]  292 	ld	h,-8 (ix)
   41AE 66            [ 7]  293 	ld	h, (hl)
   41AF C5            [11]  294 	push	bc
   41B0 6A            [ 4]  295 	ld	l, d
   41B1 E5            [11]  296 	push	hl
   41B2 CD 9B 44      [17]  297 	call	_cpct_setDrawCharM1
   41B5 C1            [10]  298 	pop	bc
                            299 ;src/main.c:114: cpct_drawStringM1("Mode 1 string :D", pvideomem + 38);
   41B6 21 26 00      [10]  300 	ld	hl, #0x0026
   41B9 09            [11]  301 	add	hl, bc
   41BA C5            [11]  302 	push	bc
   41BB E5            [11]  303 	push	hl
   41BC 21 90 42      [10]  304 	ld	hl, #___str_1
   41BF E5            [11]  305 	push	hl
   41C0 CD 08 43      [17]  306 	call	_cpct_drawStringM1
   41C3 C1            [10]  307 	pop	bc
                            308 ;src/main.c:117: colours[1] = ++colours[1] & 3;
   41C4 DD 6E FB      [19]  309 	ld	l,-5 (ix)
   41C7 DD 66 FC      [19]  310 	ld	h,-4 (ix)
   41CA 7E            [ 7]  311 	ld	a, (hl)
   41CB 3C            [ 4]  312 	inc	a
   41CC DD 6E FB      [19]  313 	ld	l,-5 (ix)
   41CF DD 66 FC      [19]  314 	ld	h,-4 (ix)
   41D2 77            [ 7]  315 	ld	(hl), a
   41D3 E6 03         [ 7]  316 	and	a, #0x03
   41D5 DD 6E FB      [19]  317 	ld	l,-5 (ix)
   41D8 DD 66 FC      [19]  318 	ld	h,-4 (ix)
   41DB 77            [ 7]  319 	ld	(hl), a
                            320 ;src/main.c:118: wait_frames(WFRAMES);
   41DC C5            [11]  321 	push	bc
   41DD 21 03 00      [10]  322 	ld	hl, #0x0003
   41E0 E5            [11]  323 	push	hl
   41E1 CD 00 40      [17]  324 	call	_wait_frames
   41E4 F1            [10]  325 	pop	af
   41E5 C1            [10]  326 	pop	bc
                            327 ;src/main.c:121: pvideomem += 0x50;
   41E6 21 50 00      [10]  328 	ld	hl, #0x0050
   41E9 09            [11]  329 	add	hl,bc
   41EA 4D            [ 4]  330 	ld	c, l
   41EB 44            [ 4]  331 	ld	b, h
                            332 ;src/main.c:103: for (times=0; times < 25; times++) {
   41EC DD 34 F2      [23]  333 	inc	-14 (ix)
   41EF DD 7E F2      [19]  334 	ld	a, -14 (ix)
   41F2 D6 19         [ 7]  335 	sub	a, #0x19
   41F4 DA 5C 41      [10]  336 	jp	C, 00109$
                            337 ;src/main.c:123: colours[4] = ++colours[4] & 3;
   41F7 DD 6E F7      [19]  338 	ld	l,-9 (ix)
   41FA DD 66 F8      [19]  339 	ld	h,-8 (ix)
   41FD 7E            [ 7]  340 	ld	a, (hl)
   41FE 3C            [ 4]  341 	inc	a
   41FF DD 6E F7      [19]  342 	ld	l,-9 (ix)
   4202 DD 66 F8      [19]  343 	ld	h,-8 (ix)
   4205 77            [ 7]  344 	ld	(hl), a
   4206 E6 03         [ 7]  345 	and	a, #0x03
   4208 DD 6E F7      [19]  346 	ld	l,-9 (ix)
   420B DD 66 F8      [19]  347 	ld	h,-8 (ix)
   420E 77            [ 7]  348 	ld	(hl), a
                            349 ;src/main.c:130: cpct_clearScreen(0);
   420F 21 00 40      [10]  350 	ld	hl, #0x4000
   4212 E5            [11]  351 	push	hl
   4213 AF            [ 4]  352 	xor	a, a
   4214 F5            [11]  353 	push	af
   4215 33            [ 6]  354 	inc	sp
   4216 26 C0         [ 7]  355 	ld	h, #0xc0
   4218 E5            [11]  356 	push	hl
   4219 CD 57 44      [17]  357 	call	_cpct_memset
                            358 ;src/main.c:131: cpct_setVideoMode(2);
   421C 2E 02         [ 7]  359 	ld	l, #0x02
   421E CD 49 44      [17]  360 	call	_cpct_setVideoMode
                            361 ;src/main.c:137: for (times=0; times < 25; times++) {
   4221 01 00 C0      [10]  362 	ld	bc, #0xc000
   4224 DD 36 F2 00   [19]  363 	ld	-14 (ix), #0x00
   4228                     364 00111$:
                            365 ;src/main.c:140: colours[2] ^= 1;
   4228 DD 6E F3      [19]  366 	ld	l,-13 (ix)
   422B DD 66 F4      [19]  367 	ld	h,-12 (ix)
   422E 7E            [ 7]  368 	ld	a, (hl)
   422F EE 01         [ 7]  369 	xor	a, #0x01
   4231 57            [ 4]  370 	ld	d, a
   4232 DD 6E F3      [19]  371 	ld	l,-13 (ix)
   4235 DD 66 F4      [19]  372 	ld	h,-12 (ix)
   4238 72            [ 7]  373 	ld	(hl), d
                            374 ;src/main.c:143: cpct_setDrawCharM2(colours[2], colours[5]);
   4239 DD 6E F9      [19]  375 	ld	l,-7 (ix)
   423C DD 66 FA      [19]  376 	ld	h,-6 (ix)
   423F 66            [ 7]  377 	ld	h, (hl)
   4240 C5            [11]  378 	push	bc
   4241 6A            [ 4]  379 	ld	l, d
   4242 E5            [11]  380 	push	hl
   4243 CD EF 44      [17]  381 	call	_cpct_setDrawCharM2
   4246 C1            [10]  382 	pop	bc
                            383 ;src/main.c:144: cpct_drawStringM2("And, finally, this is a long mode 2 string!!", pvideomem);
   4247 59            [ 4]  384 	ld	e, c
   4248 50            [ 4]  385 	ld	d, b
   4249 C5            [11]  386 	push	bc
   424A D5            [11]  387 	push	de
   424B 21 A1 42      [10]  388 	ld	hl, #___str_2
   424E E5            [11]  389 	push	hl
   424F CD 38 43      [17]  390 	call	_cpct_drawStringM2
   4252 21 03 00      [10]  391 	ld	hl, #0x0003
   4255 E5            [11]  392 	push	hl
   4256 CD 00 40      [17]  393 	call	_wait_frames
   4259 F1            [10]  394 	pop	af
   425A C1            [10]  395 	pop	bc
                            396 ;src/main.c:148: pvideomem += 0x50;
   425B 21 50 00      [10]  397 	ld	hl, #0x0050
   425E 09            [11]  398 	add	hl,bc
   425F 4D            [ 4]  399 	ld	c, l
   4260 44            [ 4]  400 	ld	b, h
                            401 ;src/main.c:137: for (times=0; times < 25; times++) {
   4261 DD 34 F2      [23]  402 	inc	-14 (ix)
   4264 DD 7E F2      [19]  403 	ld	a, -14 (ix)
   4267 D6 19         [ 7]  404 	sub	a, #0x19
   4269 38 BD         [12]  405 	jr	C,00111$
                            406 ;src/main.c:151: colours[5] ^= 1;
   426B DD 6E F9      [19]  407 	ld	l,-7 (ix)
   426E DD 66 FA      [19]  408 	ld	h,-6 (ix)
   4271 7E            [ 7]  409 	ld	a, (hl)
   4272 EE 01         [ 7]  410 	xor	a, #0x01
   4274 DD 6E F9      [19]  411 	ld	l,-7 (ix)
   4277 DD 66 FA      [19]  412 	ld	h,-6 (ix)
   427A 77            [ 7]  413 	ld	(hl), a
   427B C3 BD 40      [10]  414 	jp	00105$
   427E                     415 ___str_0:
   427E 24 20 4D 6F 64 65   416 	.ascii "$ Mode 0 string $"
        20 30 20 73 74 72
        69 6E 67 20 24
   428F 00                  417 	.db 0x00
   4290                     418 ___str_1:
   4290 4D 6F 64 65 20 31   419 	.ascii "Mode 1 string :D"
        20 73 74 72 69 6E
        67 20 3A 44
   42A0 00                  420 	.db 0x00
   42A1                     421 ___str_2:
   42A1 41 6E 64 2C 20 66   422 	.ascii "And, finally, this is a long mode 2 string!!"
        69 6E 61 6C 6C 79
        2C 20 74 68 69 73
        20 69 73 20 61 20
        6C 6F 6E 67 20 6D
        6F 64 65 20 32 20
        73 74 72 69 6E 67
        21 21
   42CD 00                  423 	.db 0x00
                            424 	.area _CODE
                            425 	.area _INITIALIZER
                            426 	.area _CABS (ABS)
