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
                             12 	.globl _checkUserInputAndPerformActions
                             13 	.globl _initialize
                             14 	.globl _drawMessages
                             15 	.globl _cursor_getY
                             16 	.globl _cursor_getX
                             17 	.globl _cursor_move
                             18 	.globl _cursor_draw
                             19 	.globl _cursor_setLocation
                             20 	.globl _map_clear
                             21 	.globl _map_draw
                             22 	.globl _map_changeTile
                             23 	.globl _map_setBaseMem
                             24 	.globl _cpct_getScreenPtr
                             25 	.globl _cpct_setPALColour
                             26 	.globl _cpct_waitVSYNC
                             27 	.globl _cpct_setVideoMode
                             28 	.globl _cpct_drawStringM1
                             29 	.globl _cpct_setDrawCharM1
                             30 	.globl _cpct_isAnyKeyPressed
                             31 	.globl _cpct_isKeyPressed
                             32 	.globl _cpct_scanKeyboard
                             33 	.globl _cpct_disableFirmware
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
                             65 ;src/main.c:28: void drawMessages() {
                             66 ;	---------------------------------
                             67 ; Function drawMessages
                             68 ; ---------------------------------
   40A7                      69 _drawMessages::
   40A7 DD E5         [15]   70 	push	ix
   40A9 DD 21 00 00   [14]   71 	ld	ix,#0
   40AD DD 39         [15]   72 	add	ix,sp
   40AF F5            [11]   73 	push	af
   40B0 3B            [ 6]   74 	dec	sp
                             75 ;src/main.c:53: for(i=0; i < NUM_MSGS; i++) {
   40B1 DD 36 FD 00   [19]   76 	ld	-3 (ix), #0x00
   40B5                      77 00102$:
                             78 ;src/main.c:58: pmem = cpct_getScreenPtr(CPCT_VMEM_START, msg_prop[i][0], msg_prop[i][1]);
   40B5 DD 7E FD      [19]   79 	ld	a, -3 (ix)
   40B8 DD 77 FE      [19]   80 	ld	-2 (ix), a
   40BB DD 36 FF 00   [19]   81 	ld	-1 (ix), #0x00
   40BF 6F            [ 4]   82 	ld	l, a
   40C0 26 00         [ 7]   83 	ld	h, #0x00
   40C2 29            [11]   84 	add	hl, hl
   40C3 29            [11]   85 	add	hl, hl
   40C4 3E 1F         [ 7]   86 	ld	a, #<(_drawMessages_msg_prop_1_135)
   40C6 85            [ 4]   87 	add	a, l
   40C7 4F            [ 4]   88 	ld	c, a
   40C8 3E 41         [ 7]   89 	ld	a, #>(_drawMessages_msg_prop_1_135)
   40CA 8C            [ 4]   90 	adc	a, h
   40CB 47            [ 4]   91 	ld	b, a
   40CC 69            [ 4]   92 	ld	l, c
   40CD 60            [ 4]   93 	ld	h, b
   40CE 23            [ 6]   94 	inc	hl
   40CF 56            [ 7]   95 	ld	d, (hl)
   40D0 0A            [ 7]   96 	ld	a, (bc)
   40D1 C5            [11]   97 	push	bc
   40D2 5F            [ 4]   98 	ld	e, a
   40D3 D5            [11]   99 	push	de
   40D4 21 00 C0      [10]  100 	ld	hl, #0xc000
   40D7 E5            [11]  101 	push	hl
   40D8 CD 59 47      [17]  102 	call	_cpct_getScreenPtr
   40DB EB            [ 4]  103 	ex	de,hl
   40DC C1            [10]  104 	pop	bc
                            105 ;src/main.c:61: cpct_setDrawCharM1(msg_prop[i][2], msg_prop[i][3]);
   40DD 69            [ 4]  106 	ld	l, c
   40DE 60            [ 4]  107 	ld	h, b
   40DF 23            [ 6]  108 	inc	hl
   40E0 23            [ 6]  109 	inc	hl
   40E1 23            [ 6]  110 	inc	hl
   40E2 7E            [ 7]  111 	ld	a, (hl)
   40E3 69            [ 4]  112 	ld	l, c
   40E4 60            [ 4]  113 	ld	h, b
   40E5 23            [ 6]  114 	inc	hl
   40E6 23            [ 6]  115 	inc	hl
   40E7 46            [ 7]  116 	ld	b, (hl)
   40E8 D5            [11]  117 	push	de
   40E9 F5            [11]  118 	push	af
   40EA 33            [ 6]  119 	inc	sp
   40EB C5            [11]  120 	push	bc
   40EC 33            [ 6]  121 	inc	sp
   40ED CD D4 46      [17]  122 	call	_cpct_setDrawCharM1
   40F0 D1            [10]  123 	pop	de
                            124 ;src/main.c:62: cpct_drawStringM1(strings[i], pmem);
   40F1 DD 6E FE      [19]  125 	ld	l,-2 (ix)
   40F4 DD 66 FF      [19]  126 	ld	h,-1 (ix)
   40F7 29            [11]  127 	add	hl, hl
   40F8 01 13 41      [10]  128 	ld	bc, #_drawMessages_strings_1_135
   40FB 09            [11]  129 	add	hl, bc
   40FC 4E            [ 7]  130 	ld	c, (hl)
   40FD 23            [ 6]  131 	inc	hl
   40FE 46            [ 7]  132 	ld	b, (hl)
   40FF D5            [11]  133 	push	de
   4100 C5            [11]  134 	push	bc
   4101 CD FB 44      [17]  135 	call	_cpct_drawStringM1
                            136 ;src/main.c:53: for(i=0; i < NUM_MSGS; i++) {
   4104 DD 34 FD      [23]  137 	inc	-3 (ix)
   4107 DD 7E FD      [19]  138 	ld	a, -3 (ix)
   410A D6 06         [ 7]  139 	sub	a, #0x06
   410C 38 A7         [12]  140 	jr	C,00102$
   410E DD F9         [10]  141 	ld	sp, ix
   4110 DD E1         [14]  142 	pop	ix
   4112 C9            [10]  143 	ret
   4113                     144 _drawMessages_strings_1_135:
   4113 37 41               145 	.dw ___str_0
   4115 41 41               146 	.dw ___str_1
   4117 46 41               147 	.dw ___str_2
   4119 4E 41               148 	.dw ___str_3
   411B 5A 41               149 	.dw ___str_4
   411D 63 41               150 	.dw ___str_5
   411F                     151 _drawMessages_msg_prop_1_135:
   411F 14                  152 	.db #0x14	; 20
   4120 00                  153 	.db #0x00	; 0
   4121 03                  154 	.db #0x03	; 3
   4122 00                  155 	.db #0x00	; 0
   4123 28                  156 	.db #0x28	; 40
   4124 00                  157 	.db #0x00	; 0
   4125 02                  158 	.db #0x02	; 2
   4126 00                  159 	.db #0x00	; 0
   4127 14                  160 	.db #0x14	; 20
   4128 10                  161 	.db #0x10	; 16
   4129 03                  162 	.db #0x03	; 3
   412A 00                  163 	.db #0x00	; 0
   412B 28                  164 	.db #0x28	; 40
   412C 10                  165 	.db #0x10	; 16
   412D 02                  166 	.db #0x02	; 2
   412E 00                  167 	.db #0x00	; 0
   412F 14                  168 	.db #0x14	; 20
   4130 20                  169 	.db #0x20	; 32
   4131 03                  170 	.db #0x03	; 3
   4132 00                  171 	.db #0x00	; 0
   4133 28                  172 	.db #0x28	; 40
   4134 20                  173 	.db #0x20	; 32
   4135 02                  174 	.db #0x02	; 2
   4136 00                  175 	.db #0x00	; 0
   4137                     176 ___str_0:
   4137 5B 43 75 72 73 6F   177 	.ascii "[Cursors]"
        72 73 5D
   4140 00                  178 	.db 0x00
   4141                     179 ___str_1:
   4141 4D 6F 76 65         180 	.ascii "Move"
   4145 00                  181 	.db 0x00
   4146                     182 ___str_2:
   4146 5B 53 70 61 63 65   183 	.ascii "[Space]"
        5D
   414D 00                  184 	.db 0x00
   414E                     185 ___str_3:
   414E 44 72 61 77 2F 52   186 	.ascii "Draw/Remove"
        65 6D 6F 76 65
   4159 00                  187 	.db 0x00
   415A                     188 ___str_4:
   415A 5B 45 73 63 61 70   189 	.ascii "[Escape]"
        65 5D
   4162 00                  190 	.db 0x00
   4163                     191 ___str_5:
   4163 43 6C 65 61 72      192 	.ascii "Clear"
   4168 00                  193 	.db 0x00
                            194 ;src/main.c:73: void initialize() {
                            195 ;	---------------------------------
                            196 ; Function initialize
                            197 ; ---------------------------------
   4169                     198 _initialize::
                            199 ;src/main.c:78: cpct_disableFirmware();
   4169 CD 1C 46      [17]  200 	call	_cpct_disableFirmware
                            201 ;src/main.c:81: cpct_setVideoMode(1); 
   416C 2E 01         [ 7]  202 	ld	l, #0x01
   416E CD ED 45      [17]  203 	call	_cpct_setVideoMode
                            204 ;src/main.c:86: cpct_setPALColour(0, 0x14);
   4171 21 00 14      [10]  205 	ld	hl, #0x1400
   4174 E5            [11]  206 	push	hl
   4175 CD CD 44      [17]  207 	call	_cpct_setPALColour
                            208 ;src/main.c:87: cpct_setBorder(0x14);
   4178 21 10 14      [10]  209 	ld	hl, #0x1410
   417B E5            [11]  210 	push	hl
   417C CD CD 44      [17]  211 	call	_cpct_setPALColour
                            212 ;src/main.c:92: pmem = cpct_getScreenPtr(CPCT_VMEM_START, MAP_START_X, MAP_START_Y);
   417F 21 00 30      [10]  213 	ld	hl, #0x3000
   4182 E5            [11]  214 	push	hl
   4183 26 C0         [ 7]  215 	ld	h, #0xc0
   4185 E5            [11]  216 	push	hl
   4186 CD 59 47      [17]  217 	call	_cpct_getScreenPtr
                            218 ;src/main.c:93: map_setBaseMem(pmem);
   4189 E5            [11]  219 	push	hl
   418A CD 4F 42      [17]  220 	call	_map_setBaseMem
                            221 ;src/main.c:96: cursor_setLocation(0, 0);
   418D 21 00 00      [10]  222 	ld	hl, #0x0000
   4190 E3            [19]  223 	ex	(sp),hl
   4191 CD 00 40      [17]  224 	call	_cursor_setLocation
   4194 F1            [10]  225 	pop	af
                            226 ;src/main.c:99: drawMessages();
   4195 CD A7 40      [17]  227 	call	_drawMessages
                            228 ;src/main.c:100: map_draw();
   4198 CD 0C 44      [17]  229 	call	_map_draw
                            230 ;src/main.c:101: cursor_draw();
   419B CD 19 40      [17]  231 	call	_cursor_draw
   419E C9            [10]  232 	ret
                            233 ;src/main.c:110: void checkUserInputAndPerformActions() {
                            234 ;	---------------------------------
                            235 ; Function checkUserInputAndPerformActions
                            236 ; ---------------------------------
   419F                     237 _checkUserInputAndPerformActions::
                            238 ;src/main.c:112: cpct_scanKeyboard();
   419F CD 28 47      [17]  239 	call	_cpct_scanKeyboard
                            240 ;src/main.c:116: if(cpct_isAnyKeyPressed()) {
   41A2 CD D8 45      [17]  241 	call	_cpct_isAnyKeyPressed
   41A5 7D            [ 4]  242 	ld	a, l
   41A6 B7            [ 4]  243 	or	a, a
   41A7 C8            [11]  244 	ret	Z
                            245 ;src/main.c:118: u8 x = cursor_getX();
   41A8 CD 97 40      [17]  246 	call	_cursor_getX
   41AB 4D            [ 4]  247 	ld	c, l
                            248 ;src/main.c:119: u8 y = cursor_getY();
   41AC C5            [11]  249 	push	bc
   41AD CD 9F 40      [17]  250 	call	_cursor_getY
   41B0 C1            [10]  251 	pop	bc
   41B1 45            [ 4]  252 	ld	b, l
                            253 ;src/main.c:127: if (cpct_isKeyPressed(Key_CursorUp) && y > 0)
   41B2 C5            [11]  254 	push	bc
   41B3 21 00 01      [10]  255 	ld	hl, #0x0100
   41B6 CD C1 44      [17]  256 	call	_cpct_isKeyPressed
   41B9 C1            [10]  257 	pop	bc
   41BA 7D            [ 4]  258 	ld	a, l
   41BB B7            [ 4]  259 	or	a, a
   41BC 28 10         [12]  260 	jr	Z,00105$
   41BE 78            [ 4]  261 	ld	a, b
   41BF B7            [ 4]  262 	or	a, a
   41C0 28 0C         [12]  263 	jr	Z,00105$
                            264 ;src/main.c:128: cursor_move(DIR_UP);
   41C2 C5            [11]  265 	push	bc
   41C3 3E 02         [ 7]  266 	ld	a, #0x02
   41C5 F5            [11]  267 	push	af
   41C6 33            [ 6]  268 	inc	sp
   41C7 CD 4A 40      [17]  269 	call	_cursor_move
   41CA 33            [ 6]  270 	inc	sp
   41CB C1            [10]  271 	pop	bc
   41CC 18 1B         [12]  272 	jr	00106$
   41CE                     273 00105$:
                            274 ;src/main.c:129: else if (cpct_isKeyPressed(Key_CursorDown) && y < MAP_HEIGHT-1)
   41CE C5            [11]  275 	push	bc
   41CF 21 00 04      [10]  276 	ld	hl, #0x0400
   41D2 CD C1 44      [17]  277 	call	_cpct_isKeyPressed
   41D5 C1            [10]  278 	pop	bc
   41D6 7D            [ 4]  279 	ld	a, l
   41D7 B7            [ 4]  280 	or	a, a
   41D8 28 0F         [12]  281 	jr	Z,00106$
   41DA 78            [ 4]  282 	ld	a, b
   41DB D6 18         [ 7]  283 	sub	a, #0x18
   41DD 30 0A         [12]  284 	jr	NC,00106$
                            285 ;src/main.c:130: cursor_move(DIR_DOWN);
   41DF C5            [11]  286 	push	bc
   41E0 3E 03         [ 7]  287 	ld	a, #0x03
   41E2 F5            [11]  288 	push	af
   41E3 33            [ 6]  289 	inc	sp
   41E4 CD 4A 40      [17]  290 	call	_cursor_move
   41E7 33            [ 6]  291 	inc	sp
   41E8 C1            [10]  292 	pop	bc
   41E9                     293 00106$:
                            294 ;src/main.c:135: if (cpct_isKeyPressed(Key_CursorLeft) && x > 0)
   41E9 C5            [11]  295 	push	bc
   41EA 21 01 01      [10]  296 	ld	hl, #0x0101
   41ED CD C1 44      [17]  297 	call	_cpct_isKeyPressed
   41F0 C1            [10]  298 	pop	bc
   41F1 7D            [ 4]  299 	ld	a, l
   41F2 B7            [ 4]  300 	or	a, a
   41F3 28 0F         [12]  301 	jr	Z,00112$
   41F5 79            [ 4]  302 	ld	a, c
   41F6 B7            [ 4]  303 	or	a, a
   41F7 28 0B         [12]  304 	jr	Z,00112$
                            305 ;src/main.c:136: cursor_move(DIR_LEFT);
   41F9 C5            [11]  306 	push	bc
   41FA AF            [ 4]  307 	xor	a, a
   41FB F5            [11]  308 	push	af
   41FC 33            [ 6]  309 	inc	sp
   41FD CD 4A 40      [17]  310 	call	_cursor_move
   4200 33            [ 6]  311 	inc	sp
   4201 C1            [10]  312 	pop	bc
   4202 18 1B         [12]  313 	jr	00113$
   4204                     314 00112$:
                            315 ;src/main.c:137: else if (cpct_isKeyPressed(Key_CursorRight) && x < MAP_WIDTH-1)
   4204 C5            [11]  316 	push	bc
   4205 21 00 02      [10]  317 	ld	hl, #0x0200
   4208 CD C1 44      [17]  318 	call	_cpct_isKeyPressed
   420B C1            [10]  319 	pop	bc
   420C 7D            [ 4]  320 	ld	a, l
   420D B7            [ 4]  321 	or	a, a
   420E 28 0F         [12]  322 	jr	Z,00113$
   4210 79            [ 4]  323 	ld	a, c
   4211 D6 4F         [ 7]  324 	sub	a, #0x4f
   4213 30 0A         [12]  325 	jr	NC,00113$
                            326 ;src/main.c:138: cursor_move(DIR_RIGHT);
   4215 C5            [11]  327 	push	bc
   4216 3E 01         [ 7]  328 	ld	a, #0x01
   4218 F5            [11]  329 	push	af
   4219 33            [ 6]  330 	inc	sp
   421A CD 4A 40      [17]  331 	call	_cursor_move
   421D 33            [ 6]  332 	inc	sp
   421E C1            [10]  333 	pop	bc
   421F                     334 00113$:
                            335 ;src/main.c:142: if (cpct_isKeyPressed(Key_Space)) 
   421F C5            [11]  336 	push	bc
   4220 21 05 80      [10]  337 	ld	hl, #0x8005
   4223 CD C1 44      [17]  338 	call	_cpct_isKeyPressed
   4226 C1            [10]  339 	pop	bc
   4227 7D            [ 4]  340 	ld	a, l
   4228 B7            [ 4]  341 	or	a, a
   4229 28 08         [12]  342 	jr	Z,00118$
                            343 ;src/main.c:143: map_changeTile(x, y);
   422B C5            [11]  344 	push	bc
   422C CD 67 44      [17]  345 	call	_map_changeTile
   422F F1            [10]  346 	pop	af
   4230 C3 19 40      [10]  347 	jp	_cursor_draw
   4233                     348 00118$:
                            349 ;src/main.c:144: else if (cpct_isKeyPressed(Key_Esc))
   4233 21 08 04      [10]  350 	ld	hl, #0x0408
   4236 CD C1 44      [17]  351 	call	_cpct_isKeyPressed
   4239 7D            [ 4]  352 	ld	a, l
   423A B7            [ 4]  353 	or	a, a
   423B CA 19 40      [10]  354 	jp	Z,_cursor_draw
                            355 ;src/main.c:145: map_clear();
   423E CD 9F 44      [17]  356 	call	_map_clear
                            357 ;src/main.c:148: cursor_draw();
   4241 C3 19 40      [10]  358 	jp  _cursor_draw
                            359 ;src/main.c:157: void main (void) {
                            360 ;	---------------------------------
                            361 ; Function main
                            362 ; ---------------------------------
   4244                     363 _main::
                            364 ;src/main.c:159: initialize();
   4244 CD 69 41      [17]  365 	call	_initialize
                            366 ;src/main.c:162: while(1) {
   4247                     367 00102$:
                            368 ;src/main.c:164: cpct_waitVSYNC();
   4247 CD E5 45      [17]  369 	call	_cpct_waitVSYNC
                            370 ;src/main.c:167: checkUserInputAndPerformActions();
   424A CD 9F 41      [17]  371 	call	_checkUserInputAndPerformActions
   424D 18 F8         [12]  372 	jr	00102$
                            373 	.area _CODE
                            374 	.area _INITIALIZER
                            375 	.area _CABS (ABS)
