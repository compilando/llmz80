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
                             12 	.globl _drawLogo
                             13 	.globl _cpct_getScreenPtr
                             14 	.globl _cpct_setVideoMemoryOffset
                             15 	.globl _cpct_setPALColour
                             16 	.globl _cpct_setPalette
                             17 	.globl _cpct_fw2hw
                             18 	.globl _cpct_waitVSYNC
                             19 	.globl _cpct_setVideoMode
                             20 	.globl _cpct_drawSprite
                             21 	.globl _cpct_memset
                             22 	.globl _cpct_disableFirmware
                             23 	.globl _sinus_offsets
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
                             55 ;src/main.c:46: void drawLogo() {
                             56 ;	---------------------------------
                             57 ; Function drawLogo
                             58 ; ---------------------------------
   0100                      59 _drawLogo::
                             60 ;src/main.c:51: cpct_clearScreen(0);
   0100 21 00 40      [10]   61 	ld	hl, #0x4000
   0103 E5            [11]   62 	push	hl
   0104 AF            [ 4]   63 	xor	a, a
   0105 F5            [11]   64 	push	af
   0106 33            [ 6]   65 	inc	sp
   0107 26 C0         [ 7]   66 	ld	h, #0xc0
   0109 E5            [11]   67 	push	hl
   010A CD 5B 21      [17]   68 	call	_cpct_memset
                             69 ;src/main.c:54: cpct_fw2hw(G_logo_palette, 4);      // Convert palettes from firmware colour values to hardware colours
   010D 21 04 00      [10]   70 	ld	hl, #0x0004
   0110 E5            [11]   71 	push	hl
   0111 21 6A 02      [10]   72 	ld	hl, #_G_logo_palette
   0114 E5            [11]   73 	push	hl
   0115 CD 17 21      [17]   74 	call	_cpct_fw2hw
                             75 ;src/main.c:55: cpct_setPalette(G_logo_palette, 4); // Set hardware palette   
   0118 21 04 00      [10]   76 	ld	hl, #0x0004
   011B E5            [11]   77 	push	hl
   011C 21 6A 02      [10]   78 	ld	hl, #_G_logo_palette
   011F E5            [11]   79 	push	hl
   0120 CD 46 20      [17]   80 	call	_cpct_setPalette
                             81 ;src/main.c:56: cpct_setBorder(G_logo_palette[0]);  // Set the border white, using colour 0 from palette (after converting it to hardware values)
   0123 21 6A 02      [10]   82 	ld	hl, #_G_logo_palette + 0
   0126 46            [ 7]   83 	ld	b, (hl)
   0127 C5            [11]   84 	push	bc
   0128 33            [ 6]   85 	inc	sp
   0129 3E 10         [ 7]   86 	ld	a, #0x10
   012B F5            [11]   87 	push	af
   012C 33            [ 6]   88 	inc	sp
   012D CD 5D 20      [17]   89 	call	_cpct_setPALColour
                             90 ;src/main.c:57: cpct_setVideoMode(1);               // Set video mode 1 (320x200 pixels)
   0130 2E 01         [ 7]   91 	ld	l, #0x01
   0132 CD 4D 21      [17]   92 	call	_cpct_setVideoMode
                             93 ;src/main.c:67: pvideo = cpct_getScreenPtr(CPCT_VMEM_START, 40, 4);
   0135 21 28 04      [10]   94 	ld	hl, #0x0428
   0138 E5            [11]   95 	push	hl
   0139 21 00 C0      [10]   96 	ld	hl, #0xc000
   013C E5            [11]   97 	push	hl
   013D CD 7A 21      [17]   98 	call	_cpct_getScreenPtr
                             99 ;src/main.c:68: cpct_drawSprite(G_CPCt_logo, pvideo, LOGO_W, LOGO_H);
   0140 01 6E 02      [10]  100 	ld	bc, #_G_CPCt_logo+0
   0143 11 28 BF      [10]  101 	ld	de, #0xbf28
   0146 D5            [11]  102 	push	de
   0147 E5            [11]  103 	push	hl
   0148 C5            [11]  104 	push	bc
   0149 CD 72 20      [17]  105 	call	_cpct_drawSprite
   014C C9            [10]  106 	ret
   014D                     107 _sinus_offsets:
   014D 00                  108 	.db #0x00	; 0
   014E 00                  109 	.db #0x00	; 0
   014F 00                  110 	.db #0x00	; 0
   0150 00                  111 	.db #0x00	; 0
   0151 00                  112 	.db #0x00	; 0
   0152 00                  113 	.db #0x00	; 0
   0153 00                  114 	.db #0x00	; 0
   0154 00                  115 	.db #0x00	; 0
   0155 00                  116 	.db #0x00	; 0
   0156 00                  117 	.db #0x00	; 0
   0157 00                  118 	.db #0x00	; 0
   0158 00                  119 	.db #0x00	; 0
   0159 01                  120 	.db #0x01	; 1
   015A 01                  121 	.db #0x01	; 1
   015B 01                  122 	.db #0x01	; 1
   015C 01                  123 	.db #0x01	; 1
   015D 01                  124 	.db #0x01	; 1
   015E 01                  125 	.db #0x01	; 1
   015F 01                  126 	.db #0x01	; 1
   0160 01                  127 	.db #0x01	; 1
   0161 01                  128 	.db #0x01	; 1
   0162 01                  129 	.db #0x01	; 1
   0163 02                  130 	.db #0x02	; 2
   0164 02                  131 	.db #0x02	; 2
   0165 02                  132 	.db #0x02	; 2
   0166 02                  133 	.db #0x02	; 2
   0167 02                  134 	.db #0x02	; 2
   0168 02                  135 	.db #0x02	; 2
   0169 02                  136 	.db #0x02	; 2
   016A 03                  137 	.db #0x03	; 3
   016B 03                  138 	.db #0x03	; 3
   016C 03                  139 	.db #0x03	; 3
   016D 03                  140 	.db #0x03	; 3
   016E 03                  141 	.db #0x03	; 3
   016F 03                  142 	.db #0x03	; 3
   0170 04                  143 	.db #0x04	; 4
   0171 04                  144 	.db #0x04	; 4
   0172 04                  145 	.db #0x04	; 4
   0173 04                  146 	.db #0x04	; 4
   0174 04                  147 	.db #0x04	; 4
   0175 05                  148 	.db #0x05	; 5
   0176 05                  149 	.db #0x05	; 5
   0177 05                  150 	.db #0x05	; 5
   0178 05                  151 	.db #0x05	; 5
   0179 06                  152 	.db #0x06	; 6
   017A 06                  153 	.db #0x06	; 6
   017B 06                  154 	.db #0x06	; 6
   017C 06                  155 	.db #0x06	; 6
   017D 06                  156 	.db #0x06	; 6
   017E 07                  157 	.db #0x07	; 7
   017F 07                  158 	.db #0x07	; 7
   0180 07                  159 	.db #0x07	; 7
   0181 07                  160 	.db #0x07	; 7
   0182 08                  161 	.db #0x08	; 8
   0183 08                  162 	.db #0x08	; 8
   0184 08                  163 	.db #0x08	; 8
   0185 08                  164 	.db #0x08	; 8
   0186 09                  165 	.db #0x09	; 9
   0187 09                  166 	.db #0x09	; 9
   0188 09                  167 	.db #0x09	; 9
   0189 09                  168 	.db #0x09	; 9
   018A 0A                  169 	.db #0x0a	; 10
   018B 0A                  170 	.db #0x0a	; 10
   018C 0A                  171 	.db #0x0a	; 10
   018D 0A                  172 	.db #0x0a	; 10
   018E 0A                  173 	.db #0x0a	; 10
   018F 0B                  174 	.db #0x0b	; 11
   0190 0B                  175 	.db #0x0b	; 11
   0191 0B                  176 	.db #0x0b	; 11
   0192 0B                  177 	.db #0x0b	; 11
   0193 0C                  178 	.db #0x0c	; 12
   0194 0C                  179 	.db #0x0c	; 12
   0195 0C                  180 	.db #0x0c	; 12
   0196 0C                  181 	.db #0x0c	; 12
   0197 0D                  182 	.db #0x0d	; 13
   0198 0D                  183 	.db #0x0d	; 13
   0199 0D                  184 	.db #0x0d	; 13
   019A 0D                  185 	.db #0x0d	; 13
   019B 0E                  186 	.db #0x0e	; 14
   019C 0E                  187 	.db #0x0e	; 14
   019D 0E                  188 	.db #0x0e	; 14
   019E 0E                  189 	.db #0x0e	; 14
   019F 0E                  190 	.db #0x0e	; 14
   01A0 0F                  191 	.db #0x0f	; 15
   01A1 0F                  192 	.db #0x0f	; 15
   01A2 0F                  193 	.db #0x0f	; 15
   01A3 0F                  194 	.db #0x0f	; 15
   01A4 10                  195 	.db #0x10	; 16
   01A5 10                  196 	.db #0x10	; 16
   01A6 10                  197 	.db #0x10	; 16
   01A7 10                  198 	.db #0x10	; 16
   01A8 10                  199 	.db #0x10	; 16
   01A9 11                  200 	.db #0x11	; 17
   01AA 11                  201 	.db #0x11	; 17
   01AB 11                  202 	.db #0x11	; 17
   01AC 11                  203 	.db #0x11	; 17
   01AD 11                  204 	.db #0x11	; 17
   01AE 11                  205 	.db #0x11	; 17
   01AF 12                  206 	.db #0x12	; 18
   01B0 12                  207 	.db #0x12	; 18
   01B1 12                  208 	.db #0x12	; 18
   01B2 12                  209 	.db #0x12	; 18
   01B3 12                  210 	.db #0x12	; 18
   01B4 12                  211 	.db #0x12	; 18
   01B5 12                  212 	.db #0x12	; 18
   01B6 13                  213 	.db #0x13	; 19
   01B7 13                  214 	.db #0x13	; 19
   01B8 13                  215 	.db #0x13	; 19
   01B9 13                  216 	.db #0x13	; 19
   01BA 13                  217 	.db #0x13	; 19
   01BB 13                  218 	.db #0x13	; 19
   01BC 13                  219 	.db #0x13	; 19
   01BD 13                  220 	.db #0x13	; 19
   01BE 13                  221 	.db #0x13	; 19
   01BF 13                  222 	.db #0x13	; 19
   01C0 14                  223 	.db #0x14	; 20
   01C1 14                  224 	.db #0x14	; 20
   01C2 14                  225 	.db #0x14	; 20
   01C3 14                  226 	.db #0x14	; 20
   01C4 14                  227 	.db #0x14	; 20
   01C5 14                  228 	.db #0x14	; 20
   01C6 14                  229 	.db #0x14	; 20
   01C7 14                  230 	.db #0x14	; 20
   01C8 14                  231 	.db #0x14	; 20
   01C9 14                  232 	.db #0x14	; 20
   01CA 14                  233 	.db #0x14	; 20
   01CB 14                  234 	.db #0x14	; 20
   01CC 14                  235 	.db #0x14	; 20
   01CD 14                  236 	.db #0x14	; 20
   01CE 14                  237 	.db #0x14	; 20
   01CF 14                  238 	.db #0x14	; 20
   01D0 14                  239 	.db #0x14	; 20
   01D1 14                  240 	.db #0x14	; 20
   01D2 14                  241 	.db #0x14	; 20
   01D3 14                  242 	.db #0x14	; 20
   01D4 14                  243 	.db #0x14	; 20
   01D5 14                  244 	.db #0x14	; 20
   01D6 14                  245 	.db #0x14	; 20
   01D7 14                  246 	.db #0x14	; 20
   01D8 14                  247 	.db #0x14	; 20
   01D9 13                  248 	.db #0x13	; 19
   01DA 13                  249 	.db #0x13	; 19
   01DB 13                  250 	.db #0x13	; 19
   01DC 13                  251 	.db #0x13	; 19
   01DD 13                  252 	.db #0x13	; 19
   01DE 13                  253 	.db #0x13	; 19
   01DF 13                  254 	.db #0x13	; 19
   01E0 13                  255 	.db #0x13	; 19
   01E1 13                  256 	.db #0x13	; 19
   01E2 13                  257 	.db #0x13	; 19
   01E3 12                  258 	.db #0x12	; 18
   01E4 12                  259 	.db #0x12	; 18
   01E5 12                  260 	.db #0x12	; 18
   01E6 12                  261 	.db #0x12	; 18
   01E7 12                  262 	.db #0x12	; 18
   01E8 12                  263 	.db #0x12	; 18
   01E9 12                  264 	.db #0x12	; 18
   01EA 11                  265 	.db #0x11	; 17
   01EB 11                  266 	.db #0x11	; 17
   01EC 11                  267 	.db #0x11	; 17
   01ED 11                  268 	.db #0x11	; 17
   01EE 11                  269 	.db #0x11	; 17
   01EF 11                  270 	.db #0x11	; 17
   01F0 10                  271 	.db #0x10	; 16
   01F1 10                  272 	.db #0x10	; 16
   01F2 10                  273 	.db #0x10	; 16
   01F3 10                  274 	.db #0x10	; 16
   01F4 10                  275 	.db #0x10	; 16
   01F5 0F                  276 	.db #0x0f	; 15
   01F6 0F                  277 	.db #0x0f	; 15
   01F7 0F                  278 	.db #0x0f	; 15
   01F8 0F                  279 	.db #0x0f	; 15
   01F9 0E                  280 	.db #0x0e	; 14
   01FA 0E                  281 	.db #0x0e	; 14
   01FB 0E                  282 	.db #0x0e	; 14
   01FC 0E                  283 	.db #0x0e	; 14
   01FD 0E                  284 	.db #0x0e	; 14
   01FE 0D                  285 	.db #0x0d	; 13
   01FF 0D                  286 	.db #0x0d	; 13
   0200 0D                  287 	.db #0x0d	; 13
   0201 0D                  288 	.db #0x0d	; 13
   0202 0C                  289 	.db #0x0c	; 12
   0203 0C                  290 	.db #0x0c	; 12
   0204 0C                  291 	.db #0x0c	; 12
   0205 0C                  292 	.db #0x0c	; 12
   0206 0B                  293 	.db #0x0b	; 11
   0207 0B                  294 	.db #0x0b	; 11
   0208 0B                  295 	.db #0x0b	; 11
   0209 0B                  296 	.db #0x0b	; 11
   020A 0A                  297 	.db #0x0a	; 10
   020B 0A                  298 	.db #0x0a	; 10
   020C 0A                  299 	.db #0x0a	; 10
   020D 0A                  300 	.db #0x0a	; 10
   020E 0A                  301 	.db #0x0a	; 10
   020F 09                  302 	.db #0x09	; 9
   0210 09                  303 	.db #0x09	; 9
   0211 09                  304 	.db #0x09	; 9
   0212 09                  305 	.db #0x09	; 9
   0213 08                  306 	.db #0x08	; 8
   0214 08                  307 	.db #0x08	; 8
   0215 08                  308 	.db #0x08	; 8
   0216 08                  309 	.db #0x08	; 8
   0217 07                  310 	.db #0x07	; 7
   0218 07                  311 	.db #0x07	; 7
   0219 07                  312 	.db #0x07	; 7
   021A 07                  313 	.db #0x07	; 7
   021B 06                  314 	.db #0x06	; 6
   021C 06                  315 	.db #0x06	; 6
   021D 06                  316 	.db #0x06	; 6
   021E 06                  317 	.db #0x06	; 6
   021F 06                  318 	.db #0x06	; 6
   0220 05                  319 	.db #0x05	; 5
   0221 05                  320 	.db #0x05	; 5
   0222 05                  321 	.db #0x05	; 5
   0223 05                  322 	.db #0x05	; 5
   0224 04                  323 	.db #0x04	; 4
   0225 04                  324 	.db #0x04	; 4
   0226 04                  325 	.db #0x04	; 4
   0227 04                  326 	.db #0x04	; 4
   0228 04                  327 	.db #0x04	; 4
   0229 03                  328 	.db #0x03	; 3
   022A 03                  329 	.db #0x03	; 3
   022B 03                  330 	.db #0x03	; 3
   022C 03                  331 	.db #0x03	; 3
   022D 03                  332 	.db #0x03	; 3
   022E 03                  333 	.db #0x03	; 3
   022F 02                  334 	.db #0x02	; 2
   0230 02                  335 	.db #0x02	; 2
   0231 02                  336 	.db #0x02	; 2
   0232 02                  337 	.db #0x02	; 2
   0233 02                  338 	.db #0x02	; 2
   0234 02                  339 	.db #0x02	; 2
   0235 02                  340 	.db #0x02	; 2
   0236 01                  341 	.db #0x01	; 1
   0237 01                  342 	.db #0x01	; 1
   0238 01                  343 	.db #0x01	; 1
   0239 01                  344 	.db #0x01	; 1
   023A 01                  345 	.db #0x01	; 1
   023B 01                  346 	.db #0x01	; 1
   023C 01                  347 	.db #0x01	; 1
   023D 01                  348 	.db #0x01	; 1
   023E 01                  349 	.db #0x01	; 1
   023F 01                  350 	.db #0x01	; 1
   0240 00                  351 	.db #0x00	; 0
   0241 00                  352 	.db #0x00	; 0
   0242 00                  353 	.db #0x00	; 0
   0243 00                  354 	.db #0x00	; 0
   0244 00                  355 	.db #0x00	; 0
   0245 00                  356 	.db #0x00	; 0
   0246 00                  357 	.db #0x00	; 0
   0247 00                  358 	.db #0x00	; 0
   0248 00                  359 	.db #0x00	; 0
   0249 00                  360 	.db #0x00	; 0
   024A 00                  361 	.db #0x00	; 0
   024B 00                  362 	.db #0x00	; 0
   024C 00                  363 	.db #0x00	; 0
                            364 ;src/main.c:74: void main(void) { 
                            365 ;	---------------------------------
                            366 ; Function main
                            367 ; ---------------------------------
   024D                     368 _main::
                            369 ;src/main.c:78: cpct_disableFirmware(); // Disable firmware to prevent it from interfering with setVideoMode
   024D CD 69 21      [17]  370 	call	_cpct_disableFirmware
                            371 ;src/main.c:79: drawLogo();             // Initialize palette and draw CPCtelera's Logo 
   0250 CD 00 01      [17]  372 	call	_drawLogo
                            373 ;src/main.c:84: while (1) {
   0253 0E 00         [ 7]  374 	ld	c, #0x00
   0255                     375 00102$:
                            376 ;src/main.c:89: cpct_setVideoMemoryOffset(sinus_offsets[i++]);  
   0255 11 4D 01      [10]  377 	ld	de, #_sinus_offsets+0
   0258 41            [ 4]  378 	ld	b, c
   0259 0C            [ 4]  379 	inc	c
   025A 68            [ 4]  380 	ld	l,b
   025B 26 00         [ 7]  381 	ld	h,#0x00
   025D 19            [11]  382 	add	hl, de
   025E 6E            [ 7]  383 	ld	l, (hl)
   025F C5            [11]  384 	push	bc
   0260 CD 69 20      [17]  385 	call	_cpct_setVideoMemoryOffset
   0263 CD 45 21      [17]  386 	call	_cpct_waitVSYNC
   0266 C1            [10]  387 	pop	bc
                            388 ;src/main.c:93: __asm__("halt");    // HALT assembler instruction makes CPU wait till next HSYNC signal
   0267 76            [ 4]  389 	halt
   0268 18 EB         [12]  390 	jr	00102$
                            391 	.area _CODE
                            392 	.area _INITIALIZER
                            393 	.area _CABS (ABS)
