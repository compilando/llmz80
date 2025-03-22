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
                             13 	.globl _strcpy
                             14 	.globl _concatNum
                             15 	.globl _drawMessage
                             16 	.globl _updateEntities
                             17 	.globl _cpct_setPALColour
                             18 	.globl _cpct_setPalette
                             19 	.globl _cpct_fw2hw
                             20 	.globl _cpct_setVideoMode
                             21 	.globl _cpct_drawSprite
                             22 	.globl _cpct_isKeyPressed
                             23 	.globl _cpct_scanKeyboard_f
                             24 	.globl _cpct_disableFirmware
                             25 ;--------------------------------------------------------
                             26 ; special function registers
                             27 ;--------------------------------------------------------
                             28 ;--------------------------------------------------------
                             29 ; ram data
                             30 ;--------------------------------------------------------
                             31 	.area _DATA
                             32 ;--------------------------------------------------------
                             33 ; ram data
                             34 ;--------------------------------------------------------
                             35 	.area _INITIALIZED
                             36 ;--------------------------------------------------------
                             37 ; absolute external ram data
                             38 ;--------------------------------------------------------
                             39 	.area _DABS (ABS)
                             40 ;--------------------------------------------------------
                             41 ; global & static initialisations
                             42 ;--------------------------------------------------------
                             43 	.area _HOME
                             44 	.area _GSINIT
                             45 	.area _GSFINAL
                             46 	.area _GSINIT
                             47 ;--------------------------------------------------------
                             48 ; Home
                             49 ;--------------------------------------------------------
                             50 	.area _HOME
                             51 	.area _HOME
                             52 ;--------------------------------------------------------
                             53 ; code
                             54 ;--------------------------------------------------------
                             55 	.area _CODE
                             56 ;src/main.c:30: void checkUserInput (f32 *ax, f32 *ay) {
                             57 ;	---------------------------------
                             58 ; Function checkUserInput
                             59 ; ---------------------------------
   4000                      60 _checkUserInput::
   4000 DD E5         [15]   61 	push	ix
   4002 DD 21 00 00   [14]   62 	ld	ix,#0
   4006 DD 39         [15]   63 	add	ix,sp
   4008 F5            [11]   64 	push	af
   4009 F5            [11]   65 	push	af
                             66 ;src/main.c:32: cpct_scanKeyboard_f();
   400A CD 64 4F      [17]   67 	call	_cpct_scanKeyboard_f
                             68 ;src/main.c:36: if      (cpct_isKeyPressed(Key_CursorRight) ) { *ax=0.5;  }
   400D 21 00 02      [10]   69 	ld	hl, #0x0200
   4010 CD 58 4F      [17]   70 	call	_cpct_isKeyPressed
   4013 4D            [ 4]   71 	ld	c, l
   4014 DD 6E 04      [19]   72 	ld	l,4 (ix)
   4017 DD 66 05      [19]   73 	ld	h,5 (ix)
   401A 79            [ 4]   74 	ld	a, c
   401B B7            [ 4]   75 	or	a, a
   401C 28 0C         [12]   76 	jr	Z,00104$
   401E AF            [ 4]   77 	xor	a, a
   401F 77            [ 7]   78 	ld	(hl), a
   4020 23            [ 6]   79 	inc	hl
   4021 77            [ 7]   80 	ld	(hl), a
   4022 23            [ 6]   81 	inc	hl
   4023 36 00         [10]   82 	ld	(hl), #0x00
   4025 23            [ 6]   83 	inc	hl
   4026 36 3F         [10]   84 	ld	(hl), #0x3f
   4028 18 16         [12]   85 	jr	00105$
   402A                      86 00104$:
                             87 ;src/main.c:37: else if (cpct_isKeyPressed(Key_CursorLeft)  ) { *ax=-0.5; }
   402A E5            [11]   88 	push	hl
   402B 21 01 01      [10]   89 	ld	hl, #0x0101
   402E CD 58 4F      [17]   90 	call	_cpct_isKeyPressed
   4031 7D            [ 4]   91 	ld	a, l
   4032 E1            [10]   92 	pop	hl
   4033 B7            [ 4]   93 	or	a, a
   4034 28 0A         [12]   94 	jr	Z,00105$
   4036 AF            [ 4]   95 	xor	a, a
   4037 77            [ 7]   96 	ld	(hl), a
   4038 23            [ 6]   97 	inc	hl
   4039 77            [ 7]   98 	ld	(hl), a
   403A 23            [ 6]   99 	inc	hl
   403B 36 00         [10]  100 	ld	(hl), #0x00
   403D 23            [ 6]  101 	inc	hl
   403E 36 BF         [10]  102 	ld	(hl), #0xbf
   4040                     103 00105$:
                            104 ;src/main.c:38: if      (cpct_isKeyPressed(Key_CursorUp)    ) { *ay=-0.5; }
   4040 21 00 01      [10]  105 	ld	hl, #0x0100
   4043 CD 58 4F      [17]  106 	call	_cpct_isKeyPressed
   4046 4D            [ 4]  107 	ld	c, l
   4047 DD 6E 06      [19]  108 	ld	l,6 (ix)
   404A DD 66 07      [19]  109 	ld	h,7 (ix)
   404D 79            [ 4]  110 	ld	a, c
   404E B7            [ 4]  111 	or	a, a
   404F 28 0C         [12]  112 	jr	Z,00109$
   4051 AF            [ 4]  113 	xor	a, a
   4052 77            [ 7]  114 	ld	(hl), a
   4053 23            [ 6]  115 	inc	hl
   4054 77            [ 7]  116 	ld	(hl), a
   4055 23            [ 6]  117 	inc	hl
   4056 36 00         [10]  118 	ld	(hl), #0x00
   4058 23            [ 6]  119 	inc	hl
   4059 36 BF         [10]  120 	ld	(hl), #0xbf
   405B 18 16         [12]  121 	jr	00110$
   405D                     122 00109$:
                            123 ;src/main.c:39: else if (cpct_isKeyPressed(Key_CursorDown)  ) { *ay=0.5;  }
   405D E5            [11]  124 	push	hl
   405E 21 00 04      [10]  125 	ld	hl, #0x0400
   4061 CD 58 4F      [17]  126 	call	_cpct_isKeyPressed
   4064 7D            [ 4]  127 	ld	a, l
   4065 E1            [10]  128 	pop	hl
   4066 B7            [ 4]  129 	or	a, a
   4067 28 0A         [12]  130 	jr	Z,00110$
   4069 AF            [ 4]  131 	xor	a, a
   406A 77            [ 7]  132 	ld	(hl), a
   406B 23            [ 6]  133 	inc	hl
   406C 77            [ 7]  134 	ld	(hl), a
   406D 23            [ 6]  135 	inc	hl
   406E 36 00         [10]  136 	ld	(hl), #0x00
   4070 23            [ 6]  137 	inc	hl
   4071 36 3F         [10]  138 	ld	(hl), #0x3f
   4073                     139 00110$:
                            140 ;src/main.c:42: if      (cpct_isKeyPressed(Key_Q)) {
   4073 21 08 08      [10]  141 	ld	hl, #0x0808
   4076 CD 58 4F      [17]  142 	call	_cpct_isKeyPressed
   4079 7D            [ 4]  143 	ld	a, l
   407A B7            [ 4]  144 	or	a, a
   407B 28 31         [12]  145 	jr	Z,00115$
                            146 ;src/main.c:43: g_gravity += 0.01;
   407D 21 23 3C      [10]  147 	ld	hl, #0x3c23
   4080 E5            [11]  148 	push	hl
   4081 21 0A D7      [10]  149 	ld	hl, #0xd70a
   4084 E5            [11]  150 	push	hl
   4085 2A 44 52      [16]  151 	ld	hl, (_g_gravity + 2)
   4088 E5            [11]  152 	push	hl
   4089 2A 42 52      [16]  153 	ld	hl, (_g_gravity)
   408C E5            [11]  154 	push	hl
   408D CD D6 57      [17]  155 	call	___fsadd
   4090 F1            [10]  156 	pop	af
   4091 F1            [10]  157 	pop	af
   4092 F1            [10]  158 	pop	af
   4093 F1            [10]  159 	pop	af
   4094 DD 72 FF      [19]  160 	ld	-1 (ix), d
   4097 DD 73 FE      [19]  161 	ld	-2 (ix), e
   409A DD 74 FD      [19]  162 	ld	-3 (ix), h
   409D DD 75 FC      [19]  163 	ld	-4 (ix), l
   40A0 11 42 52      [10]  164 	ld	de, #_g_gravity
   40A3 21 00 00      [10]  165 	ld	hl, #0
   40A6 39            [11]  166 	add	hl, sp
   40A7 01 04 00      [10]  167 	ld	bc, #4
   40AA ED B0         [21]  168 	ldir
   40AC 18 3D         [12]  169 	jr	00116$
   40AE                     170 00115$:
                            171 ;src/main.c:44: } else  if (cpct_isKeyPressed(Key_A)) {
   40AE 21 08 20      [10]  172 	ld	hl, #0x2008
   40B1 CD 58 4F      [17]  173 	call	_cpct_isKeyPressed
   40B4 7D            [ 4]  174 	ld	a, l
   40B5 B7            [ 4]  175 	or	a, a
   40B6 28 6F         [12]  176 	jr	Z,00117$
                            177 ;src/main.c:45: g_gravity -= 0.01;
   40B8 21 23 3C      [10]  178 	ld	hl, #0x3c23
   40BB E5            [11]  179 	push	hl
   40BC 21 0A D7      [10]  180 	ld	hl, #0xd70a
   40BF E5            [11]  181 	push	hl
   40C0 2A 44 52      [16]  182 	ld	hl, (_g_gravity + 2)
   40C3 E5            [11]  183 	push	hl
   40C4 2A 42 52      [16]  184 	ld	hl, (_g_gravity)
   40C7 E5            [11]  185 	push	hl
   40C8 CD 46 52      [17]  186 	call	___fssub
   40CB F1            [10]  187 	pop	af
   40CC F1            [10]  188 	pop	af
   40CD F1            [10]  189 	pop	af
   40CE F1            [10]  190 	pop	af
   40CF DD 72 FF      [19]  191 	ld	-1 (ix), d
   40D2 DD 73 FE      [19]  192 	ld	-2 (ix), e
   40D5 DD 74 FD      [19]  193 	ld	-3 (ix), h
   40D8 DD 75 FC      [19]  194 	ld	-4 (ix), l
   40DB 11 42 52      [10]  195 	ld	de, #_g_gravity
   40DE 21 00 00      [10]  196 	ld	hl, #0
   40E1 39            [11]  197 	add	hl, sp
   40E2 01 04 00      [10]  198 	ld	bc, #4
   40E5 ED B0         [21]  199 	ldir
   40E7 18 02         [12]  200 	jr	00116$
                            201 ;src/main.c:48: return;
   40E9 18 3C         [12]  202 	jr	00117$
   40EB                     203 00116$:
                            204 ;src/main.c:52: strcpy(g_message.str, "Gravity:");
   40EB 21 2C 41      [10]  205 	ld	hl, #___str_0
   40EE E5            [11]  206 	push	hl
   40EF 21 33 52      [10]  207 	ld	hl, #(_g_message + 0x0002)
   40F2 E5            [11]  208 	push	hl
   40F3 CD 0D 43      [17]  209 	call	_strcpy
   40F6 F1            [10]  210 	pop	af
   40F7 F1            [10]  211 	pop	af
                            212 ;src/main.c:53: concatNum(&g_message.str[8], g_gravity*100);
   40F8 2A 44 52      [16]  213 	ld	hl, (_g_gravity + 2)
   40FB E5            [11]  214 	push	hl
   40FC 2A 42 52      [16]  215 	ld	hl, (_g_gravity)
   40FF E5            [11]  216 	push	hl
   4100 21 C8 42      [10]  217 	ld	hl, #0x42c8
   4103 E5            [11]  218 	push	hl
   4104 21 00 00      [10]  219 	ld	hl, #0x0000
   4107 E5            [11]  220 	push	hl
   4108 CD 7B 52      [17]  221 	call	___fsmul
   410B F1            [10]  222 	pop	af
   410C F1            [10]  223 	pop	af
   410D F1            [10]  224 	pop	af
   410E F1            [10]  225 	pop	af
   410F D5            [11]  226 	push	de
   4110 E5            [11]  227 	push	hl
   4111 CD 9F 5B      [17]  228 	call	___fs2schar
   4114 F1            [10]  229 	pop	af
   4115 F1            [10]  230 	pop	af
   4116 45            [ 4]  231 	ld	b, l
   4117 C5            [11]  232 	push	bc
   4118 33            [ 6]  233 	inc	sp
   4119 21 3B 52      [10]  234 	ld	hl, #(_g_message + 0x000a)
   411C E5            [11]  235 	push	hl
   411D CD 23 43      [17]  236 	call	_concatNum
   4120 F1            [10]  237 	pop	af
   4121 33            [ 6]  238 	inc	sp
                            239 ;src/main.c:54: g_message.time  = 25;
   4122 21 41 52      [10]  240 	ld	hl, #(_g_message + 0x0010)
   4125 36 19         [10]  241 	ld	(hl), #0x19
   4127                     242 00117$:
   4127 DD F9         [10]  243 	ld	sp, ix
   4129 DD E1         [14]  244 	pop	ix
   412B C9            [10]  245 	ret
   412C                     246 ___str_0:
   412C 47 72 61 76 69 74   247 	.ascii "Gravity:"
        79 3A
   4134 00                  248 	.db 0x00
                            249 ;src/main.c:60: void main(void) {
                            250 ;	---------------------------------
                            251 ; Function main
                            252 ; ---------------------------------
   4135                     253 _main::
   4135 DD E5         [15]  254 	push	ix
   4137 DD 21 00 00   [14]  255 	ld	ix,#0
   413B DD 39         [15]  256 	add	ix,sp
   413D 21 D1 FF      [10]  257 	ld	hl, #-47
   4140 39            [11]  258 	add	hl, sp
   4141 F9            [ 6]  259 	ld	sp, hl
                            260 ;src/main.c:62: TEntity logo = {
   4142 21 08 00      [10]  261 	ld	hl, #0x0008
   4145 39            [11]  262 	add	hl, sp
   4146 01 F5 4A      [10]  263 	ld	bc, #_gc_LogoFremos+0
   4149 71            [ 7]  264 	ld	(hl), c
   414A 23            [ 6]  265 	inc	hl
   414B 70            [ 7]  266 	ld	(hl), b
   414C 21 08 00      [10]  267 	ld	hl, #0x0008
   414F 39            [11]  268 	add	hl, sp
   4150 4D            [ 4]  269 	ld	c, l
   4151 44            [ 4]  270 	ld	b, h
   4152 21 02 00      [10]  271 	ld	hl, #0x0002
   4155 09            [11]  272 	add	hl,bc
   4156 DD 75 FE      [19]  273 	ld	-2 (ix), l
   4159 DD 74 FF      [19]  274 	ld	-1 (ix), h
   415C 36 00         [10]  275 	ld	(hl), #0x00
   415E 23            [ 6]  276 	inc	hl
   415F 36 C0         [10]  277 	ld	(hl), #0xc0
   4161 21 04 00      [10]  278 	ld	hl, #0x0004
   4164 09            [11]  279 	add	hl, bc
   4165 36 00         [10]  280 	ld	(hl), #0x00
   4167 21 05 00      [10]  281 	ld	hl, #0x0005
   416A 09            [11]  282 	add	hl, bc
   416B 36 00         [10]  283 	ld	(hl), #0x00
   416D 21 06 00      [10]  284 	ld	hl, #0x0006
   4170 09            [11]  285 	add	hl,bc
   4171 DD 75 FB      [19]  286 	ld	-5 (ix), l
   4174 DD 74 FC      [19]  287 	ld	-4 (ix), h
   4177 36 37         [10]  288 	ld	(hl), #0x37
   4179 21 07 00      [10]  289 	ld	hl, #0x0007
   417C 09            [11]  290 	add	hl,bc
   417D DD 75 F9      [19]  291 	ld	-7 (ix), l
   4180 DD 74 FA      [19]  292 	ld	-6 (ix), h
   4183 36 14         [10]  293 	ld	(hl), #0x14
   4185 21 08 00      [10]  294 	ld	hl, #0x0008
   4188 09            [11]  295 	add	hl, bc
   4189 36 00         [10]  296 	ld	(hl), #0x00
   418B 23            [ 6]  297 	inc	hl
   418C 36 00         [10]  298 	ld	(hl), #0x00
   418E 23            [ 6]  299 	inc	hl
   418F 36 00         [10]  300 	ld	(hl), #0x00
   4191 23            [ 6]  301 	inc	hl
   4192 36 3F         [10]  302 	ld	(hl), #0x3f
   4194 21 0C 00      [10]  303 	ld	hl, #0x000c
   4197 09            [11]  304 	add	hl, bc
   4198 36 CD         [10]  305 	ld	(hl), #0xcd
   419A 23            [ 6]  306 	inc	hl
   419B 36 CC         [10]  307 	ld	(hl), #0xcc
   419D 23            [ 6]  308 	inc	hl
   419E 36 4C         [10]  309 	ld	(hl), #0x4c
   41A0 23            [ 6]  310 	inc	hl
   41A1 36 3E         [10]  311 	ld	(hl), #0x3e
   41A3 21 10 00      [10]  312 	ld	hl, #0x0010
   41A6 09            [11]  313 	add	hl, bc
   41A7 36 00         [10]  314 	ld	(hl), #0x00
   41A9 23            [ 6]  315 	inc	hl
   41AA 36 00         [10]  316 	ld	(hl), #0x00
   41AC 23            [ 6]  317 	inc	hl
   41AD 36 00         [10]  318 	ld	(hl), #0x00
   41AF 23            [ 6]  319 	inc	hl
   41B0 36 00         [10]  320 	ld	(hl), #0x00
   41B2 21 14 00      [10]  321 	ld	hl, #0x0014
   41B5 09            [11]  322 	add	hl, bc
   41B6 36 00         [10]  323 	ld	(hl), #0x00
   41B8 23            [ 6]  324 	inc	hl
   41B9 36 00         [10]  325 	ld	(hl), #0x00
   41BB 23            [ 6]  326 	inc	hl
   41BC 36 00         [10]  327 	ld	(hl), #0x00
   41BE 23            [ 6]  328 	inc	hl
   41BF 36 00         [10]  329 	ld	(hl), #0x00
   41C1 21 18 00      [10]  330 	ld	hl, #0x0018
   41C4 09            [11]  331 	add	hl, bc
   41C5 36 00         [10]  332 	ld	(hl), #0x00
   41C7 23            [ 6]  333 	inc	hl
   41C8 36 00         [10]  334 	ld	(hl), #0x00
   41CA 23            [ 6]  335 	inc	hl
   41CB 36 80         [10]  336 	ld	(hl), #0x80
   41CD 23            [ 6]  337 	inc	hl
   41CE 36 3F         [10]  338 	ld	(hl), #0x3f
   41D0 21 1C 00      [10]  339 	ld	hl, #0x001c
   41D3 09            [11]  340 	add	hl, bc
   41D4 36 00         [10]  341 	ld	(hl), #0x00
   41D6 23            [ 6]  342 	inc	hl
   41D7 36 00         [10]  343 	ld	(hl), #0x00
   41D9 23            [ 6]  344 	inc	hl
   41DA 36 80         [10]  345 	ld	(hl), #0x80
   41DC 23            [ 6]  346 	inc	hl
   41DD 36 3F         [10]  347 	ld	(hl), #0x3f
                            348 ;src/main.c:68: g_message.videopos = CPCT_VMEM_START;
   41DF 21 00 C0      [10]  349 	ld	hl, #0xc000
   41E2 22 31 52      [16]  350 	ld	(_g_message), hl
                            351 ;src/main.c:69: g_message.str[0]   = '\0';
   41E5 21 33 52      [10]  352 	ld	hl, #(_g_message + 0x0002)
   41E8 36 00         [10]  353 	ld	(hl), #0x00
                            354 ;src/main.c:70: g_message.time     = 0;
   41EA 21 41 52      [10]  355 	ld	hl, #(_g_message + 0x0010)
   41ED 36 00         [10]  356 	ld	(hl), #0x00
                            357 ;src/main.c:73: g_gravity = 0.02;
   41EF FD 21 42 52   [14]  358 	ld	iy, #_g_gravity
   41F3 FD 36 00 0A   [19]  359 	ld	0 (iy), #0x0a
   41F7 FD 36 01 D7   [19]  360 	ld	1 (iy), #0xd7
   41FB FD 36 02 A3   [19]  361 	ld	2 (iy), #0xa3
   41FF FD 36 03 3C   [19]  362 	ld	3 (iy), #0x3c
                            363 ;src/main.c:76: cpct_disableFirmware();
   4203 C5            [11]  364 	push	bc
   4204 CD BB 51      [17]  365 	call	_cpct_disableFirmware
   4207 21 10 00      [10]  366 	ld	hl, #0x0010
   420A E5            [11]  367 	push	hl
   420B 21 E5 4A      [10]  368 	ld	hl, #_gc_palette
   420E E5            [11]  369 	push	hl
   420F CD 75 51      [17]  370 	call	_cpct_fw2hw
   4212 C1            [10]  371 	pop	bc
                            372 ;src/main.c:80: cpct_setBorder(gc_palette[2]);   // Set the border
   4213 21 E7 4A      [10]  373 	ld	hl, #_gc_palette + 2
   4216 56            [ 7]  374 	ld	d, (hl)
   4217 C5            [11]  375 	push	bc
   4218 1E 10         [ 7]  376 	ld	e, #0x10
   421A D5            [11]  377 	push	de
   421B CD CE 4F      [17]  378 	call	_cpct_setPALColour
   421E 21 10 00      [10]  379 	ld	hl, #0x0010
   4221 E5            [11]  380 	push	hl
   4222 21 E5 4A      [10]  381 	ld	hl, #_gc_palette
   4225 E5            [11]  382 	push	hl
   4226 CD 41 4F      [17]  383 	call	_cpct_setPalette
   4229 2E 00         [ 7]  384 	ld	l, #0x00
   422B CD AD 51      [17]  385 	call	_cpct_setVideoMode
   422E C1            [10]  386 	pop	bc
                            387 ;src/main.c:87: while(1) {
   422F                     388 00102$:
                            389 ;src/main.c:88: f32 ax=0, ay=0;    // User acceleration values
   422F DD 36 D1 00   [19]  390 	ld	-47 (ix), #0x00
   4233 DD 36 D2 00   [19]  391 	ld	-46 (ix), #0x00
   4237 DD 36 D3 00   [19]  392 	ld	-45 (ix), #0x00
   423B DD 36 D4 00   [19]  393 	ld	-44 (ix), #0x00
   423F DD 36 D5 00   [19]  394 	ld	-43 (ix), #0x00
   4243 DD 36 D6 00   [19]  395 	ld	-42 (ix), #0x00
   4247 DD 36 D7 00   [19]  396 	ld	-41 (ix), #0x00
   424B DD 36 D8 00   [19]  397 	ld	-40 (ix), #0x00
                            398 ;src/main.c:90: checkUserInput(&ax, &ay);
   424F 21 04 00      [10]  399 	ld	hl, #0x0004
   4252 39            [11]  400 	add	hl, sp
   4253 EB            [ 4]  401 	ex	de,hl
   4254 21 00 00      [10]  402 	ld	hl, #0x0000
   4257 39            [11]  403 	add	hl, sp
   4258 C5            [11]  404 	push	bc
   4259 D5            [11]  405 	push	de
   425A E5            [11]  406 	push	hl
   425B CD 00 40      [17]  407 	call	_checkUserInput
   425E F1            [10]  408 	pop	af
   425F F1            [10]  409 	pop	af
   4260 C1            [10]  410 	pop	bc
                            411 ;src/main.c:91: updateEntities(&logo, ax, ay);
   4261 59            [ 4]  412 	ld	e, c
   4262 50            [ 4]  413 	ld	d, b
   4263 C5            [11]  414 	push	bc
   4264 DD 6E D7      [19]  415 	ld	l,-41 (ix)
   4267 DD 66 D8      [19]  416 	ld	h,-40 (ix)
   426A E5            [11]  417 	push	hl
   426B DD 6E D5      [19]  418 	ld	l,-43 (ix)
   426E DD 66 D6      [19]  419 	ld	h,-42 (ix)
   4271 E5            [11]  420 	push	hl
   4272 DD 6E D3      [19]  421 	ld	l,-45 (ix)
   4275 DD 66 D4      [19]  422 	ld	h,-44 (ix)
   4278 E5            [11]  423 	push	hl
   4279 DD 6E D1      [19]  424 	ld	l,-47 (ix)
   427C DD 66 D2      [19]  425 	ld	h,-46 (ix)
   427F E5            [11]  426 	push	hl
   4280 D5            [11]  427 	push	de
   4281 CD 85 48      [17]  428 	call	_updateEntities
   4284 21 0A 00      [10]  429 	ld	hl, #10
   4287 39            [11]  430 	add	hl, sp
   4288 F9            [ 6]  431 	ld	sp, hl
   4289 CD C6 42      [17]  432 	call	_drawMessage
   428C C1            [10]  433 	pop	bc
                            434 ;src/main.c:93: cpct_drawSprite(logo.sprite, logo.videopos, logo.width, logo.height);
   428D DD 6E F9      [19]  435 	ld	l,-7 (ix)
   4290 DD 66 FA      [19]  436 	ld	h,-6 (ix)
   4293 7E            [ 7]  437 	ld	a, (hl)
   4294 DD 6E FB      [19]  438 	ld	l,-5 (ix)
   4297 DD 66 FC      [19]  439 	ld	h,-4 (ix)
   429A F5            [11]  440 	push	af
   429B 7E            [ 7]  441 	ld	a, (hl)
   429C DD 77 FD      [19]  442 	ld	-3 (ix), a
   429F F1            [10]  443 	pop	af
   42A0 DD 6E FE      [19]  444 	ld	l,-2 (ix)
   42A3 DD 66 FF      [19]  445 	ld	h,-1 (ix)
   42A6 F5            [11]  446 	push	af
   42A7 7E            [ 7]  447 	ld	a, (hl)
   42A8 23            [ 6]  448 	inc	hl
   42A9 66            [ 7]  449 	ld	h, (hl)
   42AA 6F            [ 4]  450 	ld	l, a
   42AB F1            [10]  451 	pop	af
   42AC E5            [11]  452 	push	hl
   42AD FD E1         [14]  453 	pop	iy
   42AF 69            [ 4]  454 	ld	l, c
   42B0 60            [ 4]  455 	ld	h, b
   42B1 5E            [ 7]  456 	ld	e, (hl)
   42B2 23            [ 6]  457 	inc	hl
   42B3 56            [ 7]  458 	ld	d, (hl)
   42B4 C5            [11]  459 	push	bc
   42B5 F5            [11]  460 	push	af
   42B6 33            [ 6]  461 	inc	sp
   42B7 DD 7E FD      [19]  462 	ld	a, -3 (ix)
   42BA F5            [11]  463 	push	af
   42BB 33            [ 6]  464 	inc	sp
   42BC FD E5         [15]  465 	push	iy
   42BE D5            [11]  466 	push	de
   42BF CD 78 50      [17]  467 	call	_cpct_drawSprite
   42C2 C1            [10]  468 	pop	bc
   42C3 C3 2F 42      [10]  469 	jp	00102$
                            470 	.area _CODE
                            471 	.area _INITIALIZER
                            472 	.area _CABS (ABS)
