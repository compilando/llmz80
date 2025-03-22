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
                             12 	.globl _updateUser
                             13 	.globl _initializeCPC
                             14 	.globl _drawEntity
                             15 	.globl _setAnimation
                             16 	.globl _updateEntity
                             17 	.globl _getPersea
                             18 	.globl _cpct_setPalette
                             19 	.globl _cpct_fw2hw
                             20 	.globl _cpct_waitVSYNC
                             21 	.globl _cpct_setVideoMode
                             22 	.globl _cpct_drawSprite
                             23 	.globl _cpct_drawSolidBox
                             24 	.globl _cpct_px2byteM0
                             25 	.globl _cpct_isKeyPressed
                             26 	.globl _cpct_scanKeyboard
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
                             59 ;src/main.c:28: void initializeCPC() {
                             60 ;	---------------------------------
                             61 ; Function initializeCPC
                             62 ; ---------------------------------
   0100                      63 _initializeCPC::
                             64 ;src/main.c:32: cpct_disableFirmware();
   0100 CD 2A 14      [17]   65 	call	_cpct_disableFirmware
                             66 ;src/main.c:35: cpct_fw2hw(gc_palette, 16);
   0103 21 10 00      [10]   67 	ld	hl, #0x0010
   0106 E5            [11]   68 	push	hl
   0107 21 CC 08      [10]   69 	ld	hl, #_gc_palette
   010A E5            [11]   70 	push	hl
   010B CD C0 13      [17]   71 	call	_cpct_fw2hw
                             72 ;src/main.c:36: cpct_setPalette(gc_palette, 16);
   010E 21 10 00      [10]   73 	ld	hl, #0x0010
   0111 E5            [11]   74 	push	hl
   0112 21 CC 08      [10]   75 	ld	hl, #_gc_palette
   0115 E5            [11]   76 	push	hl
   0116 CD F8 12      [17]   77 	call	_cpct_setPalette
                             78 ;src/main.c:39: cpct_setVideoMode(0);
   0119 2E 00         [ 7]   79 	ld	l, #0x00
   011B CD 00 14      [17]   80 	call	_cpct_setVideoMode
                             81 ;src/main.c:42: c0 = cpct_px2byteM0(4, 4);   // c0 = 2 consecutive pixels of firmware colour 4 (blue)
   011E 21 04 04      [10]   82 	ld	hl, #0x0404
   0121 E5            [11]   83 	push	hl
   0122 CD 0E 14      [17]   84 	call	_cpct_px2byteM0
   0125 4D            [ 4]   85 	ld	c, l
                             86 ;src/main.c:43: cpct_drawSolidBox(CPCT_VMEM_START, c0, 40, 60); // Boxes cannot be wider than 64 bytes,
   0126 06 00         [ 7]   87 	ld	b, #0x00
   0128 C5            [11]   88 	push	bc
   0129 21 28 3C      [10]   89 	ld	hl, #0x3c28
   012C E5            [11]   90 	push	hl
   012D C5            [11]   91 	push	bc
   012E 21 00 C0      [10]   92 	ld	hl, #0xc000
   0131 E5            [11]   93 	push	hl
   0132 CD 3A 14      [17]   94 	call	_cpct_drawSolidBox
   0135 C1            [10]   95 	pop	bc
                             96 ;src/main.c:44: cpct_drawSolidBox((void*)0xC028, c0, 40, 60); // ... so we use 2 boxes of 40 bytes wide.
   0136 C5            [11]   97 	push	bc
   0137 21 28 3C      [10]   98 	ld	hl, #0x3c28
   013A E5            [11]   99 	push	hl
   013B C5            [11]  100 	push	bc
   013C 26 C0         [ 7]  101 	ld	h, #0xc0
   013E E5            [11]  102 	push	hl
   013F CD 3A 14      [17]  103 	call	_cpct_drawSolidBox
   0142 21 37 14      [10]  104 	ld	hl, #0x1437
   0145 E5            [11]  105 	push	hl
   0146 21 FC C0      [10]  106 	ld	hl, #0xc0fc
   0149 E5            [11]  107 	push	hl
   014A 21 DC 08      [10]  108 	ld	hl, #_gc_LogoFremos
   014D E5            [11]  109 	push	hl
   014E CD 1B 13      [17]  110 	call	_cpct_drawSprite
   0151 21 02 08      [10]  111 	ld	hl, #0x0802
   0154 E5            [11]  112 	push	hl
   0155 CD 0E 14      [17]  113 	call	_cpct_px2byteM0
   0158 C1            [10]  114 	pop	bc
                            115 ;src/main.c:49: cpct_drawSolidBox((void*)0xC3C0, c1, 40, 8);
   0159 26 00         [ 7]  116 	ld	h, #0x00
   015B E5            [11]  117 	push	hl
   015C C5            [11]  118 	push	bc
   015D 11 28 08      [10]  119 	ld	de, #0x0828
   0160 D5            [11]  120 	push	de
   0161 E5            [11]  121 	push	hl
   0162 11 C0 C3      [10]  122 	ld	de, #0xc3c0
   0165 D5            [11]  123 	push	de
   0166 CD 3A 14      [17]  124 	call	_cpct_drawSolidBox
   0169 C1            [10]  125 	pop	bc
   016A E1            [10]  126 	pop	hl
                            127 ;src/main.c:50: cpct_drawSolidBox((void*)0xC3E8, c1, 40, 8);
   016B C5            [11]  128 	push	bc
   016C 11 28 08      [10]  129 	ld	de, #0x0828
   016F D5            [11]  130 	push	de
   0170 E5            [11]  131 	push	hl
   0171 21 E8 C3      [10]  132 	ld	hl, #0xc3e8
   0174 E5            [11]  133 	push	hl
   0175 CD 3A 14      [17]  134 	call	_cpct_drawSolidBox
   0178 C1            [10]  135 	pop	bc
                            136 ;src/main.c:53: cpct_drawSolidBox((void*)0xC410, c0, 40, 96);
   0179 C5            [11]  137 	push	bc
   017A 21 28 60      [10]  138 	ld	hl, #0x6028
   017D E5            [11]  139 	push	hl
   017E C5            [11]  140 	push	bc
   017F 21 10 C4      [10]  141 	ld	hl, #0xc410
   0182 E5            [11]  142 	push	hl
   0183 CD 3A 14      [17]  143 	call	_cpct_drawSolidBox
   0186 C1            [10]  144 	pop	bc
                            145 ;src/main.c:54: cpct_drawSolidBox((void*)0xC438, c0, 40, 96);
   0187 21 28 60      [10]  146 	ld	hl, #0x6028
   018A E5            [11]  147 	push	hl
   018B C5            [11]  148 	push	bc
   018C 21 38 C4      [10]  149 	ld	hl, #0xc438
   018F E5            [11]  150 	push	hl
   0190 CD 3A 14      [17]  151 	call	_cpct_drawSolidBox
   0193 C9            [10]  152 	ret
                            153 ;src/main.c:60: void updateUser(TEntity* user) {
                            154 ;	---------------------------------
                            155 ; Function updateUser
                            156 ; ---------------------------------
   0194                     157 _updateUser::
                            158 ;src/main.c:62: TEntityStatus animrequest = es_stop;
   0194 06 01         [ 7]  159 	ld	b, #0x01
                            160 ;src/main.c:65: cpct_scanKeyboard();
   0196 C5            [11]  161 	push	bc
   0197 CD F8 14      [17]  162 	call	_cpct_scanKeyboard
   019A 21 05 80      [10]  163 	ld	hl, #0x8005
   019D CD 0F 13      [17]  164 	call	_cpct_isKeyPressed
   01A0 C1            [10]  165 	pop	bc
   01A1 7D            [ 4]  166 	ld	a, l
   01A2 B7            [ 4]  167 	or	a, a
   01A3 28 04         [12]  168 	jr	Z,00119$
   01A5 06 07         [ 7]  169 	ld	b, #0x07
   01A7 18 5E         [12]  170 	jr	00120$
   01A9                     171 00119$:
                            172 ;src/main.c:69: else if ( cpct_isKeyPressed(Key_CursorUp)    ) animrequest = es_kick;
   01A9 C5            [11]  173 	push	bc
   01AA 21 00 01      [10]  174 	ld	hl, #0x0100
   01AD CD 0F 13      [17]  175 	call	_cpct_isKeyPressed
   01B0 C1            [10]  176 	pop	bc
   01B1 7D            [ 4]  177 	ld	a, l
   01B2 B7            [ 4]  178 	or	a, a
   01B3 28 04         [12]  179 	jr	Z,00116$
   01B5 06 05         [ 7]  180 	ld	b, #0x05
   01B7 18 4E         [12]  181 	jr	00120$
   01B9                     182 00116$:
                            183 ;src/main.c:70: else if ( cpct_isKeyPressed(Key_CursorDown)  ) animrequest = es_fist;
   01B9 C5            [11]  184 	push	bc
   01BA 21 00 04      [10]  185 	ld	hl, #0x0400
   01BD CD 0F 13      [17]  186 	call	_cpct_isKeyPressed
   01C0 C1            [10]  187 	pop	bc
   01C1 7D            [ 4]  188 	ld	a, l
   01C2 B7            [ 4]  189 	or	a, a
   01C3 28 04         [12]  190 	jr	Z,00113$
   01C5 06 04         [ 7]  191 	ld	b, #0x04
   01C7 18 3E         [12]  192 	jr	00120$
   01C9                     193 00113$:
                            194 ;src/main.c:71: else if ( cpct_isKeyPressed(Key_CursorRight) ) animrequest = es_walk_right;
   01C9 C5            [11]  195 	push	bc
   01CA 21 00 02      [10]  196 	ld	hl, #0x0200
   01CD CD 0F 13      [17]  197 	call	_cpct_isKeyPressed
   01D0 C1            [10]  198 	pop	bc
   01D1 7D            [ 4]  199 	ld	a, l
   01D2 B7            [ 4]  200 	or	a, a
   01D3 28 04         [12]  201 	jr	Z,00110$
   01D5 06 02         [ 7]  202 	ld	b, #0x02
   01D7 18 2E         [12]  203 	jr	00120$
   01D9                     204 00110$:
                            205 ;src/main.c:72: else if ( cpct_isKeyPressed(Key_CursorLeft)  ) animrequest = es_walk_left;
   01D9 C5            [11]  206 	push	bc
   01DA 21 01 01      [10]  207 	ld	hl, #0x0101
   01DD CD 0F 13      [17]  208 	call	_cpct_isKeyPressed
   01E0 C1            [10]  209 	pop	bc
   01E1 7D            [ 4]  210 	ld	a, l
   01E2 B7            [ 4]  211 	or	a, a
   01E3 28 04         [12]  212 	jr	Z,00107$
   01E5 06 03         [ 7]  213 	ld	b, #0x03
   01E7 18 1E         [12]  214 	jr	00120$
   01E9                     215 00107$:
                            216 ;src/main.c:73: else if ( cpct_isKeyPressed(Key_1)           ) animrequest = es_dead;
   01E9 C5            [11]  217 	push	bc
   01EA 21 08 01      [10]  218 	ld	hl, #0x0108
   01ED CD 0F 13      [17]  219 	call	_cpct_isKeyPressed
   01F0 C1            [10]  220 	pop	bc
   01F1 7D            [ 4]  221 	ld	a, l
   01F2 B7            [ 4]  222 	or	a, a
   01F3 28 04         [12]  223 	jr	Z,00104$
   01F5 06 00         [ 7]  224 	ld	b, #0x00
   01F7 18 0E         [12]  225 	jr	00120$
   01F9                     226 00104$:
                            227 ;src/main.c:74: else if ( cpct_isKeyPressed(Key_2)           ) animrequest = es_win;
   01F9 C5            [11]  228 	push	bc
   01FA 21 08 02      [10]  229 	ld	hl, #0x0208
   01FD CD 0F 13      [17]  230 	call	_cpct_isKeyPressed
   0200 C1            [10]  231 	pop	bc
   0201 7D            [ 4]  232 	ld	a, l
   0202 B7            [ 4]  233 	or	a, a
   0203 28 02         [12]  234 	jr	Z,00120$
   0205 06 06         [ 7]  235 	ld	b, #0x06
   0207                     236 00120$:
                            237 ;src/main.c:77: if (animrequest != es_stop)
   0207 78            [ 4]  238 	ld	a, b
   0208 3D            [ 4]  239 	dec	a
   0209 C8            [11]  240 	ret	Z
                            241 ;src/main.c:78: setAnimation(user, animrequest);
   020A C5            [11]  242 	push	bc
   020B 33            [ 6]  243 	inc	sp
   020C 21 03 00      [10]  244 	ld	hl, #3
   020F 39            [11]  245 	add	hl, sp
   0210 4E            [ 7]  246 	ld	c, (hl)
   0211 23            [ 6]  247 	inc	hl
   0212 46            [ 7]  248 	ld	b, (hl)
   0213 C5            [11]  249 	push	bc
   0214 CD CB 07      [17]  250 	call	_setAnimation
   0217 F1            [10]  251 	pop	af
   0218 33            [ 6]  252 	inc	sp
   0219 C9            [10]  253 	ret
                            254 ;src/main.c:91: void main(void) {
                            255 ;	---------------------------------
                            256 ; Function main
                            257 ; ---------------------------------
   021A                     258 _main::
                            259 ;src/main.c:95: initializeCPC();
   021A CD 00 01      [17]  260 	call	_initializeCPC
                            261 ;src/main.c:96: persea = getPersea();
   021D CD 3A 02      [17]  262 	call	_getPersea
                            263 ;src/main.c:99: while(1) {
   0220                     264 00102$:
                            265 ;src/main.c:100: updateUser(persea);
   0220 E5            [11]  266 	push	hl
   0221 E5            [11]  267 	push	hl
   0222 CD 94 01      [17]  268 	call	_updateUser
   0225 F1            [10]  269 	pop	af
   0226 CD F8 13      [17]  270 	call	_cpct_waitVSYNC
   0229 E1            [10]  271 	pop	hl
                            272 ;src/main.c:102: updateEntity(persea);
   022A E5            [11]  273 	push	hl
   022B E5            [11]  274 	push	hl
   022C CD A2 06      [17]  275 	call	_updateEntity
   022F F1            [10]  276 	pop	af
   0230 E1            [10]  277 	pop	hl
                            278 ;src/main.c:103: drawEntity(persea);
   0231 E5            [11]  279 	push	hl
   0232 E5            [11]  280 	push	hl
   0233 CD 7B 08      [17]  281 	call	_drawEntity
   0236 F1            [10]  282 	pop	af
   0237 E1            [10]  283 	pop	hl
   0238 18 E6         [12]  284 	jr	00102$
                            285 	.area _CODE
                            286 	.area _INITIALIZER
                            287 	.area _CABS (ABS)
