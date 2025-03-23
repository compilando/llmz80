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
                             12 	.globl _application
                             13 	.globl _drawScreenTilemap
                             14 	.globl _readKeyboardInput
                             15 	.globl _showMessages
                             16 	.globl _wait4Key
                             17 	.globl _swapBuffers
                             18 	.globl _printf
                             19 	.globl _cpct_etm_setTileset2x4
                             20 	.globl _cpct_etm_drawTileBox2x4
                             21 	.globl _cpct_getScreenPtr
                             22 	.globl _cpct_setVideoMemoryPage
                             23 	.globl _cpct_setPALColour
                             24 	.globl _cpct_waitVSYNC
                             25 	.globl _cpct_isKeyPressed
                             26 	.globl _cpct_scanKeyboard_f
                             27 	.globl _cpct_setStackLocation
                             28 	.globl _cpct_memset_f64
                             29 	.globl _cpct_disableFirmware
                             30 	.globl _g_scrbuffers
                             31 ;--------------------------------------------------------
                             32 ; special function registers
                             33 ;--------------------------------------------------------
                             34 ;--------------------------------------------------------
                             35 ; ram data
                             36 ;--------------------------------------------------------
                             37 	.area _DATA
                             38 ;--------------------------------------------------------
                             39 ; ram data
                             40 ;--------------------------------------------------------
                             41 	.area _INITIALIZED
                             42 ;--------------------------------------------------------
                             43 ; absolute external ram data
                             44 ;--------------------------------------------------------
                             45 	.area _DABS (ABS)
                             46 ;--------------------------------------------------------
                             47 ; global & static initialisations
                             48 ;--------------------------------------------------------
                             49 	.area _HOME
                             50 	.area _GSINIT
                             51 	.area _GSFINAL
                             52 	.area _GSINIT
                             53 ;--------------------------------------------------------
                             54 ; Home
                             55 ;--------------------------------------------------------
                             56 	.area _HOME
                             57 	.area _HOME
                             58 ;--------------------------------------------------------
                             59 ; code
                             60 ;--------------------------------------------------------
                             61 	.area _CODE
                             62 ;src/main.c:51: void swapBuffers(u8** scrbuffers) {
                             63 ;	---------------------------------
                             64 ; Function swapBuffers
                             65 ; ---------------------------------
   0040                      66 _swapBuffers::
   0040 DD E5         [15]   67 	push	ix
   0042 DD 21 00 00   [14]   68 	ld	ix,#0
   0046 DD 39         [15]   69 	add	ix,sp
   0048 F5            [11]   70 	push	af
                             71 ;src/main.c:59: cpct_setVideoMemoryPage( (u16)(scrbuffers[1]) >> 10 );
   0049 DD 6E 04      [19]   72 	ld	l,4 (ix)
   004C DD 66 05      [19]   73 	ld	h,5 (ix)
   004F 23            [ 6]   74 	inc	hl
   0050 23            [ 6]   75 	inc	hl
   0051 4E            [ 7]   76 	ld	c, (hl)
   0052 23            [ 6]   77 	inc	hl
   0053 7E            [ 7]   78 	ld	a, (hl)
   0054 0F            [ 4]   79 	rrca
   0055 0F            [ 4]   80 	rrca
   0056 E6 3F         [ 7]   81 	and	a, #0x3f
   0058 6F            [ 4]   82 	ld	l, a
   0059 CD BB 09      [17]   83 	call	_cpct_setVideoMemoryPage
                             84 ;src/main.c:63: aux = scrbuffers[0];
   005C DD 5E 04      [19]   85 	ld	e,4 (ix)
   005F DD 56 05      [19]   86 	ld	d,5 (ix)
   0062 6B            [ 4]   87 	ld	l, e
   0063 62            [ 4]   88 	ld	h, d
   0064 4E            [ 7]   89 	ld	c, (hl)
   0065 23            [ 6]   90 	inc	hl
   0066 46            [ 7]   91 	ld	b, (hl)
                             92 ;src/main.c:64: scrbuffers[0] = scrbuffers[1];
   0067 D5            [11]   93 	push	de
   0068 FD E1         [14]   94 	pop	iy
   006A FD 23         [10]   95 	inc	iy
   006C FD 23         [10]   96 	inc	iy
   006E FD 7E 00      [19]   97 	ld	a, 0 (iy)
   0071 DD 77 FE      [19]   98 	ld	-2 (ix), a
   0074 FD 7E 01      [19]   99 	ld	a, 1 (iy)
   0077 DD 77 FF      [19]  100 	ld	-1 (ix), a
   007A DD 7E FE      [19]  101 	ld	a, -2 (ix)
   007D 12            [ 7]  102 	ld	(de), a
   007E 13            [ 6]  103 	inc	de
   007F DD 7E FF      [19]  104 	ld	a, -1 (ix)
   0082 12            [ 7]  105 	ld	(de), a
                            106 ;src/main.c:65: scrbuffers[1] = aux;
   0083 FD 71 00      [19]  107 	ld	0 (iy), c
   0086 FD 70 01      [19]  108 	ld	1 (iy), b
   0089 DD F9         [10]  109 	ld	sp, ix
   008B DD E1         [14]  110 	pop	ix
   008D C9            [10]  111 	ret
   008E                     112 _g_scrbuffers:
   008E 00 C0               113 	.dw #0xc000
   0090 00 80               114 	.dw #0x8000
                            115 ;src/main.c:71: void wait4Key(cpct_keyID key) {
                            116 ;	---------------------------------
                            117 ; Function wait4Key
                            118 ; ---------------------------------
   0092                     119 _wait4Key::
                            120 ;src/main.c:74: do
   0092                     121 00101$:
                            122 ;src/main.c:75: cpct_scanKeyboard_f();
   0092 CD 87 08      [17]  123 	call	_cpct_scanKeyboard_f
                            124 ;src/main.c:76: while(cpct_isKeyPressed(key));
   0095 C1            [10]  125 	pop	bc
   0096 E1            [10]  126 	pop	hl
   0097 E5            [11]  127 	push	hl
   0098 C5            [11]  128 	push	bc
   0099 CD 7B 08      [17]  129 	call	_cpct_isKeyPressed
   009C 7D            [ 4]  130 	ld	a, l
   009D B7            [ 4]  131 	or	a, a
   009E 20 F2         [12]  132 	jr	NZ,00101$
                            133 ;src/main.c:79: do
   00A0                     134 00104$:
                            135 ;src/main.c:80: cpct_scanKeyboard_f();
   00A0 CD 87 08      [17]  136 	call	_cpct_scanKeyboard_f
                            137 ;src/main.c:81: while(!cpct_isKeyPressed(key));
   00A3 C1            [10]  138 	pop	bc
   00A4 E1            [10]  139 	pop	hl
   00A5 E5            [11]  140 	push	hl
   00A6 C5            [11]  141 	push	bc
   00A7 CD 7B 08      [17]  142 	call	_cpct_isKeyPressed
   00AA 7D            [ 4]  143 	ld	a, l
   00AB B7            [ 4]  144 	or	a, a
   00AC 28 F2         [12]  145 	jr	Z,00104$
   00AE C9            [10]  146 	ret
                            147 ;src/main.c:89: void showMessages() {
                            148 ;	---------------------------------
                            149 ; Function showMessages
                            150 ; ---------------------------------
   00AF                     151 _showMessages::
                            152 ;src/main.c:112: for (i=0; i < NUMMSGS; ++i)
   00AF 0E 00         [ 7]  153 	ld	c, #0x00
   00B1                     154 00102$:
                            155 ;src/main.c:113: printf(messages [i]);
   00B1 69            [ 4]  156 	ld	l, c
   00B2 26 00         [ 7]  157 	ld	h, #0x00
   00B4 29            [11]  158 	add	hl, hl
   00B5 11 D2 00      [10]  159 	ld	de, #_showMessages_messages_1_142
   00B8 19            [11]  160 	add	hl, de
   00B9 5E            [ 7]  161 	ld	e, (hl)
   00BA 23            [ 6]  162 	inc	hl
   00BB 56            [ 7]  163 	ld	d, (hl)
   00BC C5            [11]  164 	push	bc
   00BD D5            [11]  165 	push	de
   00BE CD 48 0A      [17]  166 	call	_printf
   00C1 F1            [10]  167 	pop	af
   00C2 C1            [10]  168 	pop	bc
                            169 ;src/main.c:112: for (i=0; i < NUMMSGS; ++i)
   00C3 0C            [ 4]  170 	inc	c
   00C4 79            [ 4]  171 	ld	a, c
   00C5 D6 0F         [ 7]  172 	sub	a, #0x0f
   00C7 38 E8         [12]  173 	jr	C,00102$
                            174 ;src/main.c:116: wait4Key(Key_Space);
   00C9 21 05 80      [10]  175 	ld	hl, #0x8005
   00CC E5            [11]  176 	push	hl
   00CD CD 92 00      [17]  177 	call	_wait4Key
   00D0 F1            [10]  178 	pop	af
   00D1 C9            [10]  179 	ret
   00D2                     180 _showMessages_messages_1_142:
   00D2 F0 00               181 	.dw ___str_0
   00D4 1B 01               182 	.dw ___str_1
   00D6 3A 01               183 	.dw ___str_2
   00D8 67 01               184 	.dw ___str_3
   00DA 96 01               185 	.dw ___str_4
   00DC C3 01               186 	.dw ___str_5
   00DE F8 01               187 	.dw ___str_6
   00E0 2B 02               188 	.dw ___str_7
   00E2 58 02               189 	.dw ___str_8
   00E4 75 02               190 	.dw ___str_9
   00E6 99 02               191 	.dw ___str_10
   00E8 C3 02               192 	.dw ___str_11
   00EA ED 02               193 	.dw ___str_12
   00EC 18 03               194 	.dw ___str_13
   00EE 3C 03               195 	.dw ___str_14
   00F0                     196 ___str_0:
   00F0 0F                  197 	.db 0x0f
   00F1 02                  198 	.db 0x02
   00F2 2A 2D 2A 2D 2A 2D   199 	.ascii "*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-"
        2A 2D 2A 2D 2A 2D
        2A 2D 2A 2D 2A 2D
        2A 2D 2A 2D 2A 2D
        2A 2D 2A 2D 2A 2D
        2A 2D 2A 2D 2A 2D
        2A 2D 2A 2D
   011A 00                  200 	.db 0x00
   011B                     201 ___str_1:
   011B 0F                  202 	.db 0x0f
   011C 03                  203 	.db 0x03
   011D 20 20 20 20 20 20   204 	.ascii "             TILEMAPS DEMO"
        20 20 20 20 20 20
        20 54 49 4C 45 4D
        41 50 53 20 44 45
        4D 4F
   0137 0A                  205 	.db 0x0a
   0138 0D                  206 	.db 0x0d
   0139 00                  207 	.db 0x00
   013A                     208 ___str_2:
   013A 0F                  209 	.db 0x0f
   013B 02                  210 	.db 0x02
   013C 2A 2D 2A 2D 2A 2D   211 	.ascii "*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-"
        2A 2D 2A 2D 2A 2D
        2A 2D 2A 2D 2A 2D
        2A 2D 2A 2D 2A 2D
        2A 2D 2A 2D 2A 2D
        2A 2D 2A 2D 2A 2D
        2A 2D 2A 2D
   0164 0A                  212 	.db 0x0a
   0165 0D                  213 	.db 0x0d
   0166 00                  214 	.db 0x00
   0167                     215 ___str_3:
   0167 0F                  216 	.db 0x0f
   0168 01                  217 	.db 0x01
   0169 53 68 6F 77 73 20   218 	.ascii "Shows  a "
        20 61 20
   0172 0F                  219 	.db 0x0f
   0173 03                  220 	.db 0x03
   0174 74 69 6C 65 6D 61   221 	.ascii "tilemap"
        70
   017B 0F                  222 	.db 0x0f
   017C 01                  223 	.db 0x01
   017D 20 20 74 68 72 6F   224 	.ascii "  through   a  viewport,"
        75 67 68 20 20 20
        61 20 20 76 69 65
        77 70 6F 72 74 2C
   0195 00                  225 	.db 0x00
   0196                     226 ___str_4:
   0196 6C 65 74 74 69 6E   227 	.ascii "letting you control the  "
        67 20 79 6F 75 20
        63 6F 6E 74 72 6F
        6C 20 74 68 65 20
        20
   01AF 0F                  228 	.db 0x0f
   01B0 02                  229 	.db 0x02
   01B1 6C 6F 63 61 74 69   230 	.ascii "location"
        6F 6E
   01B9 0F                  231 	.db 0x0f
   01BA 01                  232 	.db 0x01
   01BB 20 6F 66 20 74 68   233 	.ascii " of the"
        65
   01C2 00                  234 	.db 0x00
   01C3                     235 ___str_5:
   01C3 0F                  236 	.db 0x0f
   01C4 03                  237 	.db 0x03
   01C5 74 69 6C 65 6D 61   238 	.ascii "tilemap"
        70
   01CC 0F                  239 	.db 0x0f
   01CD 01                  240 	.db 0x01
   01CE 20 61 6E 64 20 74   241 	.ascii " and the "
        68 65 20
   01D7 0F                  242 	.db 0x0f
   01D8 02                  243 	.db 0x02
   01D9 73 69 7A 65         244 	.ascii "size"
   01DD 0F                  245 	.db 0x0f
   01DE 01                  246 	.db 0x01
   01DF 20 61 6E 64 20      247 	.ascii " and "
   01E4 0F                  248 	.db 0x0f
   01E5 02                  249 	.db 0x02
   01E6 70 6F 73 69 74 69   250 	.ascii "position"
        6F 6E
   01EE 0F                  251 	.db 0x0f
   01EF 01                  252 	.db 0x01
   01F0 20 6F 66 20 74 68   253 	.ascii " of the"
        65
   01F7 00                  254 	.db 0x00
   01F8                     255 ___str_6:
   01F8 76 69 65 77 70 6F   256 	.ascii "viewport. All is done  using "
        72 74 2E 20 41 6C
        6C 20 69 73 20 64
        6F 6E 65 20 20 75
        73 69 6E 67 20
   0215 0F                  257 	.db 0x0f
   0216 03                  258 	.db 0x03
   0217 43                  259 	.ascii "C"
   0218 0F                  260 	.db 0x0f
   0219 03                  261 	.db 0x03
   021A 50                  262 	.ascii "P"
   021B 0F                  263 	.db 0x0f
   021C 03                  264 	.db 0x03
   021D 43                  265 	.ascii "C"
   021E 0F                  266 	.db 0x0f
   021F 02                  267 	.db 0x02
   0220 74 65 6C 65 72 61   268 	.ascii "telera"
   0226 0F                  269 	.db 0x0f
   0227 01                  270 	.db 0x01
   0228 27 73               271 	.ascii "'s"
   022A 00                  272 	.db 0x00
   022B                     273 ___str_7:
   022B 66 75 6E 63 74 69   274 	.ascii "function  "
        6F 6E 20 20
   0235 0F                  275 	.db 0x0f
   0236 02                  276 	.db 0x02
   0237 63 70 63 74 5F 65   277 	.ascii "cpct_etm_drawTileBox2x4"
        74 6D 5F 64 72 61
        77 54 69 6C 65 42
        6F 78 32 78 34
   024E 0F                  278 	.db 0x0f
   024F 01                  279 	.db 0x01
   0250 2C 20 20 66 72 6F   280 	.ascii ",  from"
        6D
   0257 00                  281 	.db 0x00
   0258                     282 ___str_8:
   0258 69 74 73 20 45 61   283 	.ascii "its EasyTileMaps module."
        73 79 54 69 6C 65
        4D 61 70 73 20 6D
        6F 64 75 6C 65 2E
   0270 0A                  284 	.db 0x0a
   0271 0D                  285 	.db 0x0d
   0272 0A                  286 	.db 0x0a
   0273 0D                  287 	.db 0x0d
   0274 00                  288 	.db 0x00
   0275                     289 ___str_9:
   0275 54 68 65 73 65 20   290 	.ascii "These are the "
        61 72 65 20 74 68
        65 20
   0283 0F                  291 	.db 0x0f
   0284 03                  292 	.db 0x03
   0285 63 6F 6E 74 72 6F   293 	.ascii "control Keys"
        6C 20 4B 65 79 73
   0291 0F                  294 	.db 0x0f
   0292 01                  295 	.db 0x01
   0293 3A                  296 	.ascii ":"
   0294 0A                  297 	.db 0x0a
   0295 0D                  298 	.db 0x0d
   0296 0A                  299 	.db 0x0a
   0297 0D                  300 	.db 0x0d
   0298 00                  301 	.db 0x00
   0299                     302 ___str_10:
   0299 0F                  303 	.db 0x0f
   029A 02                  304 	.db 0x02
   029B 20 43 75 72 73 6F   305 	.ascii " Cursors "
        72 73 20
   02A4 0F                  306 	.db 0x0f
   02A5 03                  307 	.db 0x03
   02A6 2D                  308 	.ascii "-"
   02A7 0F                  309 	.db 0x0f
   02A8 01                  310 	.db 0x01
   02A9 20 4D 6F 76 65 20   311 	.ascii " Move tilemap location."
        74 69 6C 65 6D 61
        70 20 6C 6F 63 61
        74 69 6F 6E 2E
   02C0 0A                  312 	.db 0x0a
   02C1 0D                  313 	.db 0x0d
   02C2 00                  314 	.db 0x00
   02C3                     315 ___str_11:
   02C3 0F                  316 	.db 0x0f
   02C4 02                  317 	.db 0x02
   02C5 20 20 31 2C 20 32   318 	.ascii "  1, 2   "
        20 20 20
   02CE 0F                  319 	.db 0x0f
   02CF 03                  320 	.db 0x03
   02D0 2D                  321 	.ascii "-"
   02D1 0F                  322 	.db 0x0f
   02D2 01                  323 	.db 0x01
   02D3 20 43 68 61 6E 67   324 	.ascii " Change viewport width."
        65 20 76 69 65 77
        70 6F 72 74 20 77
        69 64 74 68 2E
   02EA 0A                  325 	.db 0x0a
   02EB 0D                  326 	.db 0x0d
   02EC 00                  327 	.db 0x00
   02ED                     328 ___str_12:
   02ED 0F                  329 	.db 0x0f
   02EE 02                  330 	.db 0x02
   02EF 20 20 33 2C 20 34   331 	.ascii "  3, 4   "
        20 20 20
   02F8 0F                  332 	.db 0x0f
   02F9 03                  333 	.db 0x03
   02FA 2D                  334 	.ascii "-"
   02FB 0F                  335 	.db 0x0f
   02FC 01                  336 	.db 0x01
   02FD 20 43 68 61 6E 67   337 	.ascii " Change viewport height."
        65 20 76 69 65 77
        70 6F 72 74 20 68
        65 69 67 68 74 2E
   0315 0A                  338 	.db 0x0a
   0316 0D                  339 	.db 0x0d
   0317 00                  340 	.db 0x00
   0318                     341 ___str_13:
   0318 0F                  342 	.db 0x0f
   0319 02                  343 	.db 0x02
   031A 20 57 2C 41 2C 53   344 	.ascii " W,A,S,D "
        2C 44 20
   0323 0F                  345 	.db 0x0f
   0324 03                  346 	.db 0x03
   0325 2D                  347 	.ascii "-"
   0326 0F                  348 	.db 0x0f
   0327 01                  349 	.db 0x01
   0328 20 4D 6F 76 65 20   350 	.ascii " Move viewport."
        76 69 65 77 70 6F
        72 74 2E
   0337 0A                  351 	.db 0x0a
   0338 0D                  352 	.db 0x0d
   0339 0A                  353 	.db 0x0a
   033A 0D                  354 	.db 0x0d
   033B 00                  355 	.db 0x00
   033C                     356 ___str_14:
   033C 20 20 20 20 20 20   357 	.ascii "       Press "
        20 50 72 65 73 73
        20
   0349 0F                  358 	.db 0x0f
   034A 02                  359 	.db 0x02
   034B 5B                  360 	.ascii "["
   034C 0F                  361 	.db 0x0f
   034D 03                  362 	.db 0x03
   034E 53 70 61 63 65      363 	.ascii "Space"
   0353 0F                  364 	.db 0x0f
   0354 02                  365 	.db 0x02
   0355 5D                  366 	.ascii "]"
   0356 0F                  367 	.db 0x0f
   0357 01                  368 	.db 0x01
   0358 20 74 6F 20 63 6F   369 	.ascii " to continue"
        6E 74 69 6E 75 65
   0364 00                  370 	.db 0x00
                            371 ;src/main.c:122: void readKeyboardInput(TScreenTilemap *scr){
                            372 ;	---------------------------------
                            373 ; Function readKeyboardInput
                            374 ; ---------------------------------
   0365                     375 _readKeyboardInput::
   0365 DD E5         [15]  376 	push	ix
   0367 DD 21 00 00   [14]  377 	ld	ix,#0
   036B DD 39         [15]  378 	add	ix,sp
   036D 21 F3 FF      [10]  379 	ld	hl, #-13
   0370 39            [11]  380 	add	hl, sp
   0371 F9            [ 6]  381 	ld	sp, hl
                            382 ;src/main.c:125: while(1) {
   0372                     383 00149$:
                            384 ;src/main.c:127: cpct_scanKeyboard_f(); 
   0372 CD 87 08      [17]  385 	call	_cpct_scanKeyboard_f
                            386 ;src/main.c:132: if (cpct_isKeyPressed(Key_CursorUp) && scr->y) {
   0375 21 00 01      [10]  387 	ld	hl, #0x0100
   0378 CD 7B 08      [17]  388 	call	_cpct_isKeyPressed
   037B DD 75 FF      [19]  389 	ld	-1 (ix), l
   037E DD 7E 04      [19]  390 	ld	a, 4 (ix)
   0381 DD 77 FD      [19]  391 	ld	-3 (ix), a
   0384 DD 7E 05      [19]  392 	ld	a, 5 (ix)
   0387 DD 77 FE      [19]  393 	ld	-2 (ix), a
   038A DD 7E FD      [19]  394 	ld	a, -3 (ix)
   038D C6 01         [ 7]  395 	add	a, #0x01
   038F DD 77 FB      [19]  396 	ld	-5 (ix), a
   0392 DD 7E FE      [19]  397 	ld	a, -2 (ix)
   0395 CE 00         [ 7]  398 	adc	a, #0x00
   0397 DD 77 FC      [19]  399 	ld	-4 (ix), a
   039A DD 7E FF      [19]  400 	ld	a, -1 (ix)
   039D B7            [ 4]  401 	or	a, a
   039E 28 16         [12]  402 	jr	Z,00145$
   03A0 DD 6E FB      [19]  403 	ld	l,-5 (ix)
   03A3 DD 66 FC      [19]  404 	ld	h,-4 (ix)
   03A6 7E            [ 7]  405 	ld	a, (hl)
   03A7 B7            [ 4]  406 	or	a, a
   03A8 28 0C         [12]  407 	jr	Z,00145$
                            408 ;src/main.c:133: scr->y -= 4;   // Move Tilemap Up (4 by 4 pixels, as it can only be placed
   03AA C6 FC         [ 7]  409 	add	a, #0xfc
   03AC DD 6E FB      [19]  410 	ld	l,-5 (ix)
   03AF DD 66 FC      [19]  411 	ld	h,-4 (ix)
   03B2 77            [ 7]  412 	ld	(hl), a
                            413 ;src/main.c:134: return;        // ... on pixel lines 0 and 4
   03B3 C3 27 06      [10]  414 	jp	00151$
   03B6                     415 00145$:
                            416 ;src/main.c:135: } else if (cpct_isKeyPressed(Key_CursorDown) && scr->y < (SCR_HEIGHT - 4*MAP_HEIGHT)) {
   03B6 21 00 04      [10]  417 	ld	hl, #0x0400
   03B9 CD 7B 08      [17]  418 	call	_cpct_isKeyPressed
   03BC 7D            [ 4]  419 	ld	a, l
   03BD B7            [ 4]  420 	or	a, a
   03BE 28 17         [12]  421 	jr	Z,00141$
   03C0 DD 6E FB      [19]  422 	ld	l,-5 (ix)
   03C3 DD 66 FC      [19]  423 	ld	h,-4 (ix)
   03C6 7E            [ 7]  424 	ld	a, (hl)
   03C7 FE 88         [ 7]  425 	cp	a, #0x88
   03C9 30 0C         [12]  426 	jr	NC,00141$
                            427 ;src/main.c:136: scr->y += 4;   // Move Tilemap Down (same as moving Up, 4 by 4 pixels)
   03CB C6 04         [ 7]  428 	add	a, #0x04
   03CD DD 6E FB      [19]  429 	ld	l,-5 (ix)
   03D0 DD 66 FC      [19]  430 	ld	h,-4 (ix)
   03D3 77            [ 7]  431 	ld	(hl), a
                            432 ;src/main.c:137: return;
   03D4 C3 27 06      [10]  433 	jp	00151$
   03D7                     434 00141$:
                            435 ;src/main.c:138: } else if (cpct_isKeyPressed(Key_CursorLeft) && scr->x) {
   03D7 21 01 01      [10]  436 	ld	hl, #0x0101
   03DA CD 7B 08      [17]  437 	call	_cpct_isKeyPressed
   03DD 7D            [ 4]  438 	ld	a, l
   03DE B7            [ 4]  439 	or	a, a
   03DF 28 16         [12]  440 	jr	Z,00137$
   03E1 DD 6E FD      [19]  441 	ld	l,-3 (ix)
   03E4 DD 66 FE      [19]  442 	ld	h,-2 (ix)
   03E7 4E            [ 7]  443 	ld	c, (hl)
   03E8 79            [ 4]  444 	ld	a, c
   03E9 B7            [ 4]  445 	or	a, a
   03EA 28 0B         [12]  446 	jr	Z,00137$
                            447 ;src/main.c:139: --scr->x;      // Move Tilemap Left 2 pixels (1 byte)
   03EC 0D            [ 4]  448 	dec	c
   03ED DD 6E FD      [19]  449 	ld	l,-3 (ix)
   03F0 DD 66 FE      [19]  450 	ld	h,-2 (ix)
   03F3 71            [ 7]  451 	ld	(hl), c
                            452 ;src/main.c:140: return;
   03F4 C3 27 06      [10]  453 	jp	00151$
   03F7                     454 00137$:
                            455 ;src/main.c:141: } else if (cpct_isKeyPressed(Key_CursorRight) && scr->x < (SCR_WIDTH - 2*MAP_WIDTH)) {
   03F7 21 00 02      [10]  456 	ld	hl, #0x0200
   03FA CD 7B 08      [17]  457 	call	_cpct_isKeyPressed
   03FD 7D            [ 4]  458 	ld	a, l
   03FE B7            [ 4]  459 	or	a, a
   03FF 28 16         [12]  460 	jr	Z,00133$
   0401 DD 6E FD      [19]  461 	ld	l,-3 (ix)
   0404 DD 66 FE      [19]  462 	ld	h,-2 (ix)
   0407 7E            [ 7]  463 	ld	a, (hl)
   0408 FE 28         [ 7]  464 	cp	a, #0x28
   040A 30 0B         [12]  465 	jr	NC,00133$
                            466 ;src/main.c:142: ++scr->x;      // Move Tilemap Right 2 pixels (1 byte)
   040C 3C            [ 4]  467 	inc	a
   040D DD 6E FD      [19]  468 	ld	l,-3 (ix)
   0410 DD 66 FE      [19]  469 	ld	h,-2 (ix)
   0413 77            [ 7]  470 	ld	(hl), a
                            471 ;src/main.c:143: return;
   0414 C3 27 06      [10]  472 	jp	00151$
   0417                     473 00133$:
                            474 ;src/main.c:144: } else if (cpct_isKeyPressed(Key_2) && scr->viewport.x + scr->viewport.w < MAP_WIDTH) {
   0417 21 08 02      [10]  475 	ld	hl, #0x0208
   041A CD 7B 08      [17]  476 	call	_cpct_isKeyPressed
   041D DD 75 FB      [19]  477 	ld	-5 (ix), l
                            478 ;src/main.c:165: } else if (cpct_isKeyPressed(Key_D) && scr->viewport.x + scr->viewport.w < MAP_WIDTH) {
   0420 DD 7E FD      [19]  479 	ld	a, -3 (ix)
   0423 C6 02         [ 7]  480 	add	a, #0x02
   0425 DD 77 F5      [19]  481 	ld	-11 (ix), a
   0428 DD 7E FE      [19]  482 	ld	a, -2 (ix)
   042B CE 00         [ 7]  483 	adc	a, #0x00
   042D DD 77 F6      [19]  484 	ld	-10 (ix), a
                            485 ;src/main.c:144: } else if (cpct_isKeyPressed(Key_2) && scr->viewport.x + scr->viewport.w < MAP_WIDTH) {
   0430 DD 7E FD      [19]  486 	ld	a, -3 (ix)
   0433 C6 04         [ 7]  487 	add	a, #0x04
   0435 DD 77 F9      [19]  488 	ld	-7 (ix), a
   0438 DD 7E FE      [19]  489 	ld	a, -2 (ix)
   043B CE 00         [ 7]  490 	adc	a, #0x00
   043D DD 77 FA      [19]  491 	ld	-6 (ix), a
   0440 DD 7E FB      [19]  492 	ld	a, -5 (ix)
   0443 B7            [ 4]  493 	or	a, a
   0444 28 51         [12]  494 	jr	Z,00129$
   0446 DD 6E F5      [19]  495 	ld	l,-11 (ix)
   0449 DD 66 F6      [19]  496 	ld	h,-10 (ix)
   044C 7E            [ 7]  497 	ld	a, (hl)
   044D DD 77 FB      [19]  498 	ld	-5 (ix), a
   0450 DD 77 FB      [19]  499 	ld	-5 (ix), a
   0453 DD 36 FC 00   [19]  500 	ld	-4 (ix), #0x00
   0457 DD 6E F9      [19]  501 	ld	l,-7 (ix)
   045A DD 66 FA      [19]  502 	ld	h,-6 (ix)
   045D 7E            [ 7]  503 	ld	a, (hl)
   045E DD 77 FF      [19]  504 	ld	-1 (ix), a
   0461 DD 77 F3      [19]  505 	ld	-13 (ix), a
   0464 DD 36 F4 00   [19]  506 	ld	-12 (ix), #0x00
   0468 DD 7E FB      [19]  507 	ld	a, -5 (ix)
   046B DD 86 F3      [19]  508 	add	a, -13 (ix)
   046E DD 77 F3      [19]  509 	ld	-13 (ix), a
   0471 DD 7E FC      [19]  510 	ld	a, -4 (ix)
   0474 DD 8E F4      [19]  511 	adc	a, -12 (ix)
   0477 DD 77 F4      [19]  512 	ld	-12 (ix), a
   047A DD 7E F3      [19]  513 	ld	a, -13 (ix)
   047D D6 14         [ 7]  514 	sub	a, #0x14
   047F DD 7E F4      [19]  515 	ld	a, -12 (ix)
   0482 17            [ 4]  516 	rla
   0483 3F            [ 4]  517 	ccf
   0484 1F            [ 4]  518 	rra
   0485 DE 80         [ 7]  519 	sbc	a, #0x80
   0487 30 0E         [12]  520 	jr	NC,00129$
                            521 ;src/main.c:145: ++scr->viewport.w;   // Enlarge viewport Horizontally
   0489 DD 4E FF      [19]  522 	ld	c, -1 (ix)
   048C 0C            [ 4]  523 	inc	c
   048D DD 6E F9      [19]  524 	ld	l,-7 (ix)
   0490 DD 66 FA      [19]  525 	ld	h,-6 (ix)
   0493 71            [ 7]  526 	ld	(hl), c
                            527 ;src/main.c:146: return;
   0494 C3 27 06      [10]  528 	jp	00151$
   0497                     529 00129$:
                            530 ;src/main.c:147: } else if (cpct_isKeyPressed(Key_1) && scr->viewport.w > 1) {
   0497 21 08 01      [10]  531 	ld	hl, #0x0108
   049A CD 7B 08      [17]  532 	call	_cpct_isKeyPressed
   049D 7D            [ 4]  533 	ld	a, l
   049E B7            [ 4]  534 	or	a, a
   049F 28 17         [12]  535 	jr	Z,00125$
   04A1 DD 6E F9      [19]  536 	ld	l,-7 (ix)
   04A4 DD 66 FA      [19]  537 	ld	h,-6 (ix)
   04A7 4E            [ 7]  538 	ld	c, (hl)
   04A8 3E 01         [ 7]  539 	ld	a, #0x01
   04AA 91            [ 4]  540 	sub	a, c
   04AB 30 0B         [12]  541 	jr	NC,00125$
                            542 ;src/main.c:148: --scr->viewport.w;   // Reduce viewport Horizontally
   04AD 0D            [ 4]  543 	dec	c
   04AE DD 6E F9      [19]  544 	ld	l,-7 (ix)
   04B1 DD 66 FA      [19]  545 	ld	h,-6 (ix)
   04B4 71            [ 7]  546 	ld	(hl), c
                            547 ;src/main.c:149: return;
   04B5 C3 27 06      [10]  548 	jp	00151$
   04B8                     549 00125$:
                            550 ;src/main.c:150: } else if (cpct_isKeyPressed(Key_4) && scr->viewport.y + scr->viewport.h < MAP_HEIGHT) {
   04B8 21 07 01      [10]  551 	ld	hl, #0x0107
   04BB CD 7B 08      [17]  552 	call	_cpct_isKeyPressed
   04BE DD 75 F3      [19]  553 	ld	-13 (ix), l
   04C1 DD 7E FD      [19]  554 	ld	a, -3 (ix)
   04C4 C6 03         [ 7]  555 	add	a, #0x03
   04C6 DD 77 FB      [19]  556 	ld	-5 (ix), a
   04C9 DD 7E FE      [19]  557 	ld	a, -2 (ix)
   04CC CE 00         [ 7]  558 	adc	a, #0x00
   04CE DD 77 FC      [19]  559 	ld	-4 (ix), a
   04D1 DD 7E FD      [19]  560 	ld	a, -3 (ix)
   04D4 C6 05         [ 7]  561 	add	a, #0x05
   04D6 DD 77 FD      [19]  562 	ld	-3 (ix), a
   04D9 DD 7E FE      [19]  563 	ld	a, -2 (ix)
   04DC CE 00         [ 7]  564 	adc	a, #0x00
   04DE DD 77 FE      [19]  565 	ld	-2 (ix), a
   04E1 DD 7E F3      [19]  566 	ld	a, -13 (ix)
   04E4 B7            [ 4]  567 	or	a, a
   04E5 28 51         [12]  568 	jr	Z,00121$
   04E7 DD 6E FB      [19]  569 	ld	l,-5 (ix)
   04EA DD 66 FC      [19]  570 	ld	h,-4 (ix)
   04ED 7E            [ 7]  571 	ld	a, (hl)
   04EE DD 77 F3      [19]  572 	ld	-13 (ix), a
   04F1 DD 77 F3      [19]  573 	ld	-13 (ix), a
   04F4 DD 36 F4 00   [19]  574 	ld	-12 (ix), #0x00
   04F8 DD 6E FD      [19]  575 	ld	l,-3 (ix)
   04FB DD 66 FE      [19]  576 	ld	h,-2 (ix)
   04FE 7E            [ 7]  577 	ld	a, (hl)
   04FF DD 77 FF      [19]  578 	ld	-1 (ix), a
   0502 DD 77 F7      [19]  579 	ld	-9 (ix), a
   0505 DD 36 F8 00   [19]  580 	ld	-8 (ix), #0x00
   0509 DD 7E F3      [19]  581 	ld	a, -13 (ix)
   050C DD 86 F7      [19]  582 	add	a, -9 (ix)
   050F DD 77 F7      [19]  583 	ld	-9 (ix), a
   0512 DD 7E F4      [19]  584 	ld	a, -12 (ix)
   0515 DD 8E F8      [19]  585 	adc	a, -8 (ix)
   0518 DD 77 F8      [19]  586 	ld	-8 (ix), a
   051B DD 7E F7      [19]  587 	ld	a, -9 (ix)
   051E D6 10         [ 7]  588 	sub	a, #0x10
   0520 DD 7E F8      [19]  589 	ld	a, -8 (ix)
   0523 17            [ 4]  590 	rla
   0524 3F            [ 4]  591 	ccf
   0525 1F            [ 4]  592 	rra
   0526 DE 80         [ 7]  593 	sbc	a, #0x80
   0528 30 0E         [12]  594 	jr	NC,00121$
                            595 ;src/main.c:151: ++scr->viewport.h;   // Enlarge viewport Vertically
   052A DD 4E FF      [19]  596 	ld	c, -1 (ix)
   052D 0C            [ 4]  597 	inc	c
   052E DD 6E FD      [19]  598 	ld	l,-3 (ix)
   0531 DD 66 FE      [19]  599 	ld	h,-2 (ix)
   0534 71            [ 7]  600 	ld	(hl), c
                            601 ;src/main.c:152: return;
   0535 C3 27 06      [10]  602 	jp	00151$
   0538                     603 00121$:
                            604 ;src/main.c:153: } else if (cpct_isKeyPressed(Key_3) && scr->viewport.h > 1) {
   0538 21 07 02      [10]  605 	ld	hl, #0x0207
   053B CD 7B 08      [17]  606 	call	_cpct_isKeyPressed
   053E 7D            [ 4]  607 	ld	a, l
   053F B7            [ 4]  608 	or	a, a
   0540 28 17         [12]  609 	jr	Z,00117$
   0542 DD 6E FD      [19]  610 	ld	l,-3 (ix)
   0545 DD 66 FE      [19]  611 	ld	h,-2 (ix)
   0548 4E            [ 7]  612 	ld	c, (hl)
   0549 3E 01         [ 7]  613 	ld	a, #0x01
   054B 91            [ 4]  614 	sub	a, c
   054C 30 0B         [12]  615 	jr	NC,00117$
                            616 ;src/main.c:154: --scr->viewport.h;   // Reduce viewport Vertically
   054E 0D            [ 4]  617 	dec	c
   054F DD 6E FD      [19]  618 	ld	l,-3 (ix)
   0552 DD 66 FE      [19]  619 	ld	h,-2 (ix)
   0555 71            [ 7]  620 	ld	(hl), c
                            621 ;src/main.c:155: return;
   0556 C3 27 06      [10]  622 	jp	00151$
   0559                     623 00117$:
                            624 ;src/main.c:156: } else if (cpct_isKeyPressed(Key_W) && scr->viewport.y) {
   0559 21 07 08      [10]  625 	ld	hl, #0x0807
   055C CD 7B 08      [17]  626 	call	_cpct_isKeyPressed
   055F 7D            [ 4]  627 	ld	a, l
   0560 B7            [ 4]  628 	or	a, a
   0561 28 16         [12]  629 	jr	Z,00113$
   0563 DD 6E FB      [19]  630 	ld	l,-5 (ix)
   0566 DD 66 FC      [19]  631 	ld	h,-4 (ix)
   0569 4E            [ 7]  632 	ld	c, (hl)
   056A 79            [ 4]  633 	ld	a, c
   056B B7            [ 4]  634 	or	a, a
   056C 28 0B         [12]  635 	jr	Z,00113$
                            636 ;src/main.c:157: --scr->viewport.y;   // Move viewport Up
   056E 0D            [ 4]  637 	dec	c
   056F DD 6E FB      [19]  638 	ld	l,-5 (ix)
   0572 DD 66 FC      [19]  639 	ld	h,-4 (ix)
   0575 71            [ 7]  640 	ld	(hl), c
                            641 ;src/main.c:158: return;
   0576 C3 27 06      [10]  642 	jp	00151$
   0579                     643 00113$:
                            644 ;src/main.c:159: } else if (cpct_isKeyPressed(Key_S) && scr->viewport.y + scr->viewport.h < MAP_HEIGHT) {
   0579 21 07 10      [10]  645 	ld	hl, #0x1007
   057C CD 7B 08      [17]  646 	call	_cpct_isKeyPressed
   057F 7D            [ 4]  647 	ld	a, l
   0580 B7            [ 4]  648 	or	a, a
   0581 28 50         [12]  649 	jr	Z,00109$
   0583 DD 6E FB      [19]  650 	ld	l,-5 (ix)
   0586 DD 66 FC      [19]  651 	ld	h,-4 (ix)
   0589 7E            [ 7]  652 	ld	a, (hl)
   058A DD 77 F7      [19]  653 	ld	-9 (ix), a
   058D DD 77 F3      [19]  654 	ld	-13 (ix), a
   0590 DD 36 F4 00   [19]  655 	ld	-12 (ix), #0x00
   0594 DD 6E FD      [19]  656 	ld	l,-3 (ix)
   0597 DD 66 FE      [19]  657 	ld	h,-2 (ix)
   059A 7E            [ 7]  658 	ld	a, (hl)
   059B DD 77 FD      [19]  659 	ld	-3 (ix), a
   059E DD 77 FD      [19]  660 	ld	-3 (ix), a
   05A1 DD 36 FE 00   [19]  661 	ld	-2 (ix), #0x00
   05A5 DD 7E F3      [19]  662 	ld	a, -13 (ix)
   05A8 DD 86 FD      [19]  663 	add	a, -3 (ix)
   05AB DD 77 F3      [19]  664 	ld	-13 (ix), a
   05AE DD 7E F4      [19]  665 	ld	a, -12 (ix)
   05B1 DD 8E FE      [19]  666 	adc	a, -2 (ix)
   05B4 DD 77 F4      [19]  667 	ld	-12 (ix), a
   05B7 DD 7E F3      [19]  668 	ld	a, -13 (ix)
   05BA D6 10         [ 7]  669 	sub	a, #0x10
   05BC DD 7E F4      [19]  670 	ld	a, -12 (ix)
   05BF 17            [ 4]  671 	rla
   05C0 3F            [ 4]  672 	ccf
   05C1 1F            [ 4]  673 	rra
   05C2 DE 80         [ 7]  674 	sbc	a, #0x80
   05C4 30 0D         [12]  675 	jr	NC,00109$
                            676 ;src/main.c:160: ++scr->viewport.y;   // Move viewport Down
   05C6 DD 4E F7      [19]  677 	ld	c, -9 (ix)
   05C9 0C            [ 4]  678 	inc	c
   05CA DD 6E FB      [19]  679 	ld	l,-5 (ix)
   05CD DD 66 FC      [19]  680 	ld	h,-4 (ix)
   05D0 71            [ 7]  681 	ld	(hl), c
                            682 ;src/main.c:161: return;
   05D1 18 54         [12]  683 	jr	00151$
   05D3                     684 00109$:
                            685 ;src/main.c:162: } else if (cpct_isKeyPressed(Key_A) && scr->viewport.x) {
   05D3 21 08 20      [10]  686 	ld	hl, #0x2008
   05D6 CD 7B 08      [17]  687 	call	_cpct_isKeyPressed
   05D9 7D            [ 4]  688 	ld	a, l
   05DA B7            [ 4]  689 	or	a, a
   05DB 28 15         [12]  690 	jr	Z,00105$
   05DD DD 6E F5      [19]  691 	ld	l,-11 (ix)
   05E0 DD 66 F6      [19]  692 	ld	h,-10 (ix)
   05E3 4E            [ 7]  693 	ld	c, (hl)
   05E4 79            [ 4]  694 	ld	a, c
   05E5 B7            [ 4]  695 	or	a, a
   05E6 28 0A         [12]  696 	jr	Z,00105$
                            697 ;src/main.c:163: --scr->viewport.x;   // Move viewport Left
   05E8 0D            [ 4]  698 	dec	c
   05E9 DD 6E F5      [19]  699 	ld	l,-11 (ix)
   05EC DD 66 F6      [19]  700 	ld	h,-10 (ix)
   05EF 71            [ 7]  701 	ld	(hl), c
                            702 ;src/main.c:164: return;
   05F0 18 35         [12]  703 	jr	00151$
   05F2                     704 00105$:
                            705 ;src/main.c:165: } else if (cpct_isKeyPressed(Key_D) && scr->viewport.x + scr->viewport.w < MAP_WIDTH) {
   05F2 21 07 20      [10]  706 	ld	hl, #0x2007
   05F5 CD 7B 08      [17]  707 	call	_cpct_isKeyPressed
   05F8 7D            [ 4]  708 	ld	a, l
   05F9 B7            [ 4]  709 	or	a, a
   05FA CA 72 03      [10]  710 	jp	Z, 00149$
                            711 ;src/main.c:144: } else if (cpct_isKeyPressed(Key_2) && scr->viewport.x + scr->viewport.w < MAP_WIDTH) {
   05FD DD 6E F5      [19]  712 	ld	l,-11 (ix)
   0600 DD 66 F6      [19]  713 	ld	h,-10 (ix)
   0603 4E            [ 7]  714 	ld	c, (hl)
                            715 ;src/main.c:165: } else if (cpct_isKeyPressed(Key_D) && scr->viewport.x + scr->viewport.w < MAP_WIDTH) {
   0604 59            [ 4]  716 	ld	e, c
   0605 16 00         [ 7]  717 	ld	d, #0x00
   0607 DD 6E F9      [19]  718 	ld	l,-7 (ix)
   060A DD 66 FA      [19]  719 	ld	h,-6 (ix)
   060D 6E            [ 7]  720 	ld	l, (hl)
   060E 26 00         [ 7]  721 	ld	h, #0x00
   0610 19            [11]  722 	add	hl, de
   0611 11 14 80      [10]  723 	ld	de, #0x8014
   0614 29            [11]  724 	add	hl, hl
   0615 3F            [ 4]  725 	ccf
   0616 CB 1C         [ 8]  726 	rr	h
   0618 CB 1D         [ 8]  727 	rr	l
   061A ED 52         [15]  728 	sbc	hl, de
   061C D2 72 03      [10]  729 	jp	NC, 00149$
                            730 ;src/main.c:166: ++scr->viewport.x;   // Move viewport Right
   061F 0C            [ 4]  731 	inc	c
   0620 DD 6E F5      [19]  732 	ld	l,-11 (ix)
   0623 DD 66 F6      [19]  733 	ld	h,-10 (ix)
   0626 71            [ 7]  734 	ld	(hl), c
                            735 ;src/main.c:167: return;
   0627                     736 00151$:
   0627 DD F9         [10]  737 	ld	sp, ix
   0629 DD E1         [14]  738 	pop	ix
   062B C9            [10]  739 	ret
                            740 ;src/main.c:177: void drawScreenTilemap(TScreenTilemap *scr) {
                            741 ;	---------------------------------
                            742 ; Function drawScreenTilemap
                            743 ; ---------------------------------
   062C                     744 _drawScreenTilemap::
   062C DD E5         [15]  745 	push	ix
   062E DD 21 00 00   [14]  746 	ld	ix,#0
   0632 DD 39         [15]  747 	add	ix,sp
   0634 F5            [11]  748 	push	af
   0635 F5            [11]  749 	push	af
                            750 ;src/main.c:181: cpct_memset_f64(g_scrbuffers[1], 0x00, 0x4000);
   0636 2A 90 00      [16]  751 	ld	hl, (#(_g_scrbuffers + 0x0002) + 0)
   0639 01 00 40      [10]  752 	ld	bc, #0x4000
   063C C5            [11]  753 	push	bc
   063D 01 00 00      [10]  754 	ld	bc, #0x0000
   0640 C5            [11]  755 	push	bc
   0641 E5            [11]  756 	push	hl
   0642 CD C4 09      [17]  757 	call	_cpct_memset_f64
                            758 ;src/main.c:185: ptmscr = cpct_getScreenPtr(g_scrbuffers[1], scr->x, scr->y);
   0645 DD 4E 04      [19]  759 	ld	c,4 (ix)
   0648 DD 46 05      [19]  760 	ld	b,5 (ix)
   064B 69            [ 4]  761 	ld	l, c
   064C 60            [ 4]  762 	ld	h, b
   064D 23            [ 6]  763 	inc	hl
   064E 56            [ 7]  764 	ld	d, (hl)
   064F 0A            [ 7]  765 	ld	a, (bc)
   0650 2A 90 00      [16]  766 	ld	hl, (#(_g_scrbuffers + 0x0002) + 0)
   0653 E5            [11]  767 	push	hl
   0654 FD E1         [14]  768 	pop	iy
   0656 C5            [11]  769 	push	bc
   0657 5F            [ 4]  770 	ld	e, a
   0658 D5            [11]  771 	push	de
   0659 FD E5         [15]  772 	push	iy
   065B CD 97 0A      [17]  773 	call	_cpct_getScreenPtr
   065E EB            [ 4]  774 	ex	de,hl
   065F C1            [10]  775 	pop	bc
                            776 ;src/main.c:190: MAP_WIDTH, ptmscr, g_tilemap);
   0660 DD 73 FE      [19]  777 	ld	-2 (ix), e
   0663 DD 72 FF      [19]  778 	ld	-1 (ix), d
                            779 ;src/main.c:189: scr->viewport.w, scr->viewport.h, 
   0666 33            [ 6]  780 	inc	sp
   0667 33            [ 6]  781 	inc	sp
   0668 C5            [11]  782 	push	bc
   0669 C5            [11]  783 	push	bc
   066A FD E1         [14]  784 	pop	iy
   066C FD 5E 05      [19]  785 	ld	e, 5 (iy)
   066F 69            [ 4]  786 	ld	l, c
   0670 60            [ 4]  787 	ld	h, b
   0671 23            [ 6]  788 	inc	hl
   0672 23            [ 6]  789 	inc	hl
   0673 23            [ 6]  790 	inc	hl
   0674 23            [ 6]  791 	inc	hl
   0675 56            [ 7]  792 	ld	d, (hl)
                            793 ;src/main.c:188: cpct_etm_drawTileBox2x4(scr->viewport.x, scr->viewport.y, 
   0676 69            [ 4]  794 	ld	l, c
   0677 60            [ 4]  795 	ld	h, b
   0678 23            [ 6]  796 	inc	hl
   0679 23            [ 6]  797 	inc	hl
   067A 23            [ 6]  798 	inc	hl
   067B 4E            [ 7]  799 	ld	c, (hl)
   067C E1            [10]  800 	pop	hl
   067D E5            [11]  801 	push	hl
   067E 23            [ 6]  802 	inc	hl
   067F 23            [ 6]  803 	inc	hl
   0680 46            [ 7]  804 	ld	b, (hl)
   0681 21 3B 07      [10]  805 	ld	hl, #_g_tilemap
   0684 E5            [11]  806 	push	hl
   0685 DD 6E FE      [19]  807 	ld	l,-2 (ix)
   0688 DD 66 FF      [19]  808 	ld	h,-1 (ix)
   068B E5            [11]  809 	push	hl
   068C 3E 14         [ 7]  810 	ld	a, #0x14
   068E F5            [11]  811 	push	af
   068F 33            [ 6]  812 	inc	sp
   0690 7B            [ 4]  813 	ld	a, e
   0691 F5            [11]  814 	push	af
   0692 33            [ 6]  815 	inc	sp
   0693 59            [ 4]  816 	ld	e, c
   0694 D5            [11]  817 	push	de
   0695 C5            [11]  818 	push	bc
   0696 33            [ 6]  819 	inc	sp
   0697 CD FD 08      [17]  820 	call	_cpct_etm_drawTileBox2x4
                            821 ;src/main.c:194: cpct_waitVSYNC();
   069A CD 13 0A      [17]  822 	call	_cpct_waitVSYNC
                            823 ;src/main.c:195: swapBuffers(g_scrbuffers);
   069D 21 8E 00      [10]  824 	ld	hl, #_g_scrbuffers
   06A0 E5            [11]  825 	push	hl
   06A1 CD 40 00      [17]  826 	call	_swapBuffers
   06A4 DD F9         [10]  827 	ld	sp,ix
   06A6 DD E1         [14]  828 	pop	ix
   06A8 C9            [10]  829 	ret
                            830 ;src/main.c:202: void application(void) {
                            831 ;	---------------------------------
                            832 ; Function application
                            833 ; ---------------------------------
   06A9                     834 _application::
   06A9 DD E5         [15]  835 	push	ix
   06AB 21 FA FF      [10]  836 	ld	hl, #-6
   06AE 39            [11]  837 	add	hl, sp
   06AF F9            [ 6]  838 	ld	sp, hl
                            839 ;src/main.c:204: TScreenTilemap scr = { 0, 0, { 0, 0, MAP_WIDTH, MAP_HEIGHT} };
   06B0 21 00 00      [10]  840 	ld	hl, #0x0000
   06B3 39            [11]  841 	add	hl, sp
   06B4 36 00         [10]  842 	ld	(hl), #0x00
   06B6 21 00 00      [10]  843 	ld	hl, #0x0000
   06B9 39            [11]  844 	add	hl, sp
   06BA 4D            [ 4]  845 	ld	c, l
   06BB 44            [ 4]  846 	ld	b, h
   06BC 59            [ 4]  847 	ld	e, c
   06BD 50            [ 4]  848 	ld	d, b
   06BE 13            [ 6]  849 	inc	de
   06BF AF            [ 4]  850 	xor	a, a
   06C0 12            [ 7]  851 	ld	(de), a
   06C1 59            [ 4]  852 	ld	e, c
   06C2 50            [ 4]  853 	ld	d, b
   06C3 13            [ 6]  854 	inc	de
   06C4 13            [ 6]  855 	inc	de
   06C5 AF            [ 4]  856 	xor	a, a
   06C6 12            [ 7]  857 	ld	(de), a
   06C7 59            [ 4]  858 	ld	e, c
   06C8 50            [ 4]  859 	ld	d, b
   06C9 13            [ 6]  860 	inc	de
   06CA 13            [ 6]  861 	inc	de
   06CB 13            [ 6]  862 	inc	de
   06CC AF            [ 4]  863 	xor	a, a
   06CD 12            [ 7]  864 	ld	(de), a
   06CE 21 04 00      [10]  865 	ld	hl, #0x0004
   06D1 09            [11]  866 	add	hl, bc
   06D2 36 14         [10]  867 	ld	(hl), #0x14
   06D4 21 05 00      [10]  868 	ld	hl, #0x0005
   06D7 09            [11]  869 	add	hl, bc
   06D8 36 10         [10]  870 	ld	(hl), #0x10
                            871 ;src/main.c:207: showMessages();
   06DA C5            [11]  872 	push	bc
   06DB CD AF 00      [17]  873 	call	_showMessages
   06DE CD 65 0A      [17]  874 	call	_cpct_disableFirmware
   06E1 21 10 00      [10]  875 	ld	hl, #0x0010
   06E4 E5            [11]  876 	push	hl
   06E5 CD F1 08      [17]  877 	call	_cpct_setPALColour
   06E8 21 00 14      [10]  878 	ld	hl, #0x1400
   06EB E5            [11]  879 	push	hl
   06EC CD F1 08      [17]  880 	call	_cpct_setPALColour
   06EF 21 33 07      [10]  881 	ld	hl, #_g_tileset
   06F2 CD 8C 09      [17]  882 	call	_cpct_etm_setTileset2x4
   06F5 C1            [10]  883 	pop	bc
                            884 ;src/main.c:220: while(1) {
   06F6                     885 00102$:
                            886 ;src/main.c:221: drawScreenTilemap(&scr);   // Redraws the tilemap
   06F6 59            [ 4]  887 	ld	e, c
   06F7 50            [ 4]  888 	ld	d, b
   06F8 C5            [11]  889 	push	bc
   06F9 D5            [11]  890 	push	de
   06FA CD 2C 06      [17]  891 	call	_drawScreenTilemap
   06FD F1            [10]  892 	pop	af
   06FE C1            [10]  893 	pop	bc
                            894 ;src/main.c:222: readKeyboardInput(&scr);   // Waits for a user input and makes associated changes
   06FF 59            [ 4]  895 	ld	e, c
   0700 50            [ 4]  896 	ld	d, b
   0701 C5            [11]  897 	push	bc
   0702 D5            [11]  898 	push	de
   0703 CD 65 03      [17]  899 	call	_readKeyboardInput
   0706 F1            [10]  900 	pop	af
   0707 C1            [10]  901 	pop	bc
   0708 18 EC         [12]  902 	jr	00102$
                            903 ;src/main.c:233: void main(void) {
                            904 ;	---------------------------------
                            905 ; Function main
                            906 ; ---------------------------------
   070A                     907 _main::
                            908 ;src/main.c:237: cpct_setStackLocation((void*)0x8000);  
   070A 21 00 80      [10]  909 	ld	hl, #0x8000
   070D CD 0F 0A      [17]  910 	call	_cpct_setStackLocation
                            911 ;src/main.c:240: application();   
   0710 C3 A9 06      [10]  912 	jp  _application
                            913 	.area _CODE
                            914 	.area _INITIALIZER
                            915 	.area _CABS (ABS)
