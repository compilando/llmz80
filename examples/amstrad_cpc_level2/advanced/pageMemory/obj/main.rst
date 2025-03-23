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
                             12 	.globl _cpct_getScreenPtr
                             13 	.globl _cpct_drawStringM1
                             14 	.globl _cpct_setDrawCharM1
                             15 	.globl _cpct_drawSolidBox
                             16 	.globl _cpct_px2byteM1
                             17 	.globl _cpct_pageMemory
                             18 	.globl _cpct_memset
                             19 ;--------------------------------------------------------
                             20 ; special function registers
                             21 ;--------------------------------------------------------
                             22 ;--------------------------------------------------------
                             23 ; ram data
                             24 ;--------------------------------------------------------
                             25 	.area _DATA
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
                             50 ;src/main.c:23: void main(void) {
                             51 ;	---------------------------------
                             52 ; Function main
                             53 ; ---------------------------------
   8000                      54 _main::
                             55 ;src/main.c:28: cpct_pageMemory(RAMCFG_0 | BANK_0);				// Not needed, sets the memory with the first 64kb accesible, in consecutive banks.
   8000 2E 00         [ 7]   56 	ld	l, #0x00
   8002 CD 7F 83      [17]   57 	call	_cpct_pageMemory
                             58 ;src/main.c:31: *firstByteInPage = cpct_px2byteM1(1, 1, 1, 1);	// Set the first byte in page to all pixels with colour 1 (yellow by default).
   8005 21 01 01      [10]   59 	ld	hl, #0x0101
   8008 E5            [11]   60 	push	hl
   8009 2E 01         [ 7]   61 	ld	l, #0x01
   800B E5            [11]   62 	push	hl
   800C CD 4C 82      [17]   63 	call	_cpct_px2byteM1
   800F F1            [10]   64 	pop	af
   8010 F1            [10]   65 	pop	af
   8011 4D            [ 4]   66 	ld	c, l
   8012 21 00 40      [10]   67 	ld	hl, #0x4000
   8015 71            [ 7]   68 	ld	(hl), c
                             69 ;src/main.c:33: cpct_pageMemory(RAMCFG_4 | BANK_0);				// Set the 4th page (64kb to 80kb) in 0x4000-0x7FFF
   8016 2E 04         [ 7]   70 	ld	l, #0x04
   8018 CD 7F 83      [17]   71 	call	_cpct_pageMemory
                             72 ;src/main.c:38: *firstByteInPage = cpct_px2byteM1(2, 2, 2, 2);	// Set the first byte in page to all pixels with colour 2 (cyan by default ).
   801B 21 02 02      [10]   73 	ld	hl, #0x0202
   801E E5            [11]   74 	push	hl
   801F 2E 02         [ 7]   75 	ld	l, #0x02
   8021 E5            [11]   76 	push	hl
   8022 CD 4C 82      [17]   77 	call	_cpct_px2byteM1
   8025 F1            [10]   78 	pop	af
   8026 F1            [10]   79 	pop	af
   8027 4D            [ 4]   80 	ld	c, l
   8028 21 00 40      [10]   81 	ld	hl, #0x4000
   802B 71            [ 7]   82 	ld	(hl), c
                             83 ;src/main.c:40: cpct_pageMemory(RAMCFG_5 | BANK_0);				// Set the 4th page (64kb to 80kb) in 0x4000-0x7FFF
   802C 2E 05         [ 7]   84 	ld	l, #0x05
   802E CD 7F 83      [17]   85 	call	_cpct_pageMemory
                             86 ;src/main.c:45: *firstByteInPage = cpct_px2byteM1(3, 3, 3, 3);	// Set the first byte in page to all pixels with colour 3 (red by default ).
   8031 21 03 03      [10]   87 	ld	hl, #0x0303
   8034 E5            [11]   88 	push	hl
   8035 2E 03         [ 7]   89 	ld	l, #0x03
   8037 E5            [11]   90 	push	hl
   8038 CD 4C 82      [17]   91 	call	_cpct_px2byteM1
   803B F1            [10]   92 	pop	af
   803C F1            [10]   93 	pop	af
   803D 4D            [ 4]   94 	ld	c, l
   803E 21 00 40      [10]   95 	ld	hl, #0x4000
   8041 71            [ 7]   96 	ld	(hl), c
                             97 ;src/main.c:47: cpct_pageMemory(RAMCFG_6 | BANK_0);				// Set the 4th page (64kb to 80kb) in 0x4000-0x7FFF
   8042 2E 06         [ 7]   98 	ld	l, #0x06
   8044 CD 7F 83      [17]   99 	call	_cpct_pageMemory
                            100 ;src/main.c:52: *firstByteInPage = cpct_px2byteM1(1, 1, 2, 2);	// Set the first byte in page to all pixels with colours 1, 2 (yellow, cyan by default ).
   8047 21 02 02      [10]  101 	ld	hl, #0x0202
   804A E5            [11]  102 	push	hl
   804B 21 01 01      [10]  103 	ld	hl, #0x0101
   804E E5            [11]  104 	push	hl
   804F CD 4C 82      [17]  105 	call	_cpct_px2byteM1
   8052 F1            [10]  106 	pop	af
   8053 F1            [10]  107 	pop	af
   8054 4D            [ 4]  108 	ld	c, l
   8055 21 00 40      [10]  109 	ld	hl, #0x4000
   8058 71            [ 7]  110 	ld	(hl), c
                            111 ;src/main.c:54: cpct_pageMemory(RAMCFG_7 | BANK_0);				// Set the 4th page (64kb to 80kb) in 0x4000-0x7FFF
   8059 2E 07         [ 7]  112 	ld	l, #0x07
   805B CD 7F 83      [17]  113 	call	_cpct_pageMemory
                            114 ;src/main.c:59: *firstByteInPage = cpct_px2byteM1(1, 1, 3, 3);	// Set the first byte in page to all pixels with colours 1, 3 (yellow, cyan by default ).
   805E 21 03 03      [10]  115 	ld	hl, #0x0303
   8061 E5            [11]  116 	push	hl
   8062 21 01 01      [10]  117 	ld	hl, #0x0101
   8065 E5            [11]  118 	push	hl
   8066 CD 4C 82      [17]  119 	call	_cpct_px2byteM1
   8069 F1            [10]  120 	pop	af
   806A F1            [10]  121 	pop	af
   806B 4D            [ 4]  122 	ld	c, l
   806C 21 00 40      [10]  123 	ld	hl, #0x4000
   806F 71            [ 7]  124 	ld	(hl), c
                            125 ;src/main.c:61: cpct_pageMemory(RAMCFG_0 | BANK_0); 				// Set the memory again to default state
   8070 2E 00         [ 7]  126 	ld	l, #0x00
   8072 CD 7F 83      [17]  127 	call	_cpct_pageMemory
                            128 ;src/main.c:64: cpct_memset(CPCT_VMEM_START, 0, 0x4000);
   8075 21 00 40      [10]  129 	ld	hl, #0x4000
   8078 E5            [11]  130 	push	hl
   8079 AF            [ 4]  131 	xor	a, a
   807A F5            [11]  132 	push	af
   807B 33            [ 6]  133 	inc	sp
   807C 26 C0         [ 7]  134 	ld	h, #0xc0
   807E E5            [11]  135 	push	hl
   807F CD 3E 82      [17]  136 	call	_cpct_memset
                            137 ;src/main.c:67: cpct_pageMemory(RAMCFG_0 | BANK_0); // Not needed, sets the memory with the first 64kb accesible, in consecutive banks.
   8082 2E 00         [ 7]  138 	ld	l, #0x00
   8084 CD 7F 83      [17]  139 	call	_cpct_pageMemory
                            140 ;src/main.c:68: pvmem = cpct_getScreenPtr(CPCT_VMEM_START, 0, 0);
   8087 21 00 00      [10]  141 	ld	hl, #0x0000
   808A E5            [11]  142 	push	hl
   808B 26 C0         [ 7]  143 	ld	h, #0xc0
   808D E5            [11]  144 	push	hl
   808E CD 15 83      [17]  145 	call	_cpct_getScreenPtr
   8091 4D            [ 4]  146 	ld	c, l
   8092 44            [ 4]  147 	ld	b, h
                            148 ;src/main.c:69: cpct_drawSolidBox(pvmem, *firstByteInPage, 2, 8);
   8093 21 00 40      [10]  149 	ld	hl, #0x4000
   8096 5E            [ 7]  150 	ld	e, (hl)
   8097 16 00         [ 7]  151 	ld	d, #0x00
   8099 21 02 08      [10]  152 	ld	hl, #0x0802
   809C E5            [11]  153 	push	hl
   809D D5            [11]  154 	push	de
   809E C5            [11]  155 	push	bc
   809F CD 6D 82      [17]  156 	call	_cpct_drawSolidBox
                            157 ;src/main.c:70: pvmem = cpct_getScreenPtr(CPCT_VMEM_START, 4, 0);
   80A2 21 04 00      [10]  158 	ld	hl, #0x0004
   80A5 E5            [11]  159 	push	hl
   80A6 21 00 C0      [10]  160 	ld	hl, #0xc000
   80A9 E5            [11]  161 	push	hl
   80AA CD 15 83      [17]  162 	call	_cpct_getScreenPtr
                            163 ;src/main.c:71: cpct_setDrawCharM1(1, 0);
   80AD E5            [11]  164 	push	hl
   80AE 01 01 00      [10]  165 	ld	bc, #0x0001
   80B1 C5            [11]  166 	push	bc
   80B2 CD 2B 83      [17]  167 	call	_cpct_setDrawCharM1
   80B5 E1            [10]  168 	pop	hl
                            169 ;src/main.c:72: cpct_drawStringM1("RAMCFG_0", pvmem);
   80B6 01 91 81      [10]  170 	ld	bc, #___str_0+0
   80B9 E5            [11]  171 	push	hl
   80BA C5            [11]  172 	push	bc
   80BB CD BE 81      [17]  173 	call	_cpct_drawStringM1
                            174 ;src/main.c:74: cpct_pageMemory(RAMCFG_4 | BANK_0); // Set the 4th page (64kb to 80kb) in 0x4000-0x7FFF
   80BE 2E 04         [ 7]  175 	ld	l, #0x04
   80C0 CD 7F 83      [17]  176 	call	_cpct_pageMemory
                            177 ;src/main.c:75: pvmem = cpct_getScreenPtr(CPCT_VMEM_START, 0, 16);
   80C3 21 00 10      [10]  178 	ld	hl, #0x1000
   80C6 E5            [11]  179 	push	hl
   80C7 26 C0         [ 7]  180 	ld	h, #0xc0
   80C9 E5            [11]  181 	push	hl
   80CA CD 15 83      [17]  182 	call	_cpct_getScreenPtr
   80CD 4D            [ 4]  183 	ld	c, l
   80CE 44            [ 4]  184 	ld	b, h
                            185 ;src/main.c:76: cpct_drawSolidBox(pvmem, *firstByteInPage, 2, 8);
   80CF 21 00 40      [10]  186 	ld	hl, #0x4000
   80D2 5E            [ 7]  187 	ld	e, (hl)
   80D3 16 00         [ 7]  188 	ld	d, #0x00
   80D5 21 02 08      [10]  189 	ld	hl, #0x0802
   80D8 E5            [11]  190 	push	hl
   80D9 D5            [11]  191 	push	de
   80DA C5            [11]  192 	push	bc
   80DB CD 6D 82      [17]  193 	call	_cpct_drawSolidBox
                            194 ;src/main.c:77: pvmem = cpct_getScreenPtr(CPCT_VMEM_START, 4, 16);
   80DE 21 04 10      [10]  195 	ld	hl, #0x1004
   80E1 E5            [11]  196 	push	hl
   80E2 21 00 C0      [10]  197 	ld	hl, #0xc000
   80E5 E5            [11]  198 	push	hl
   80E6 CD 15 83      [17]  199 	call	_cpct_getScreenPtr
                            200 ;src/main.c:78: cpct_drawStringM1("RAMCFG_4", pvmem);
   80E9 01 9A 81      [10]  201 	ld	bc, #___str_1+0
   80EC E5            [11]  202 	push	hl
   80ED C5            [11]  203 	push	bc
   80EE CD BE 81      [17]  204 	call	_cpct_drawStringM1
                            205 ;src/main.c:80: cpct_pageMemory(RAMCFG_5 | BANK_0); // Set the 4th page (64kb to 80kb) in 0x4000-0x7FFF
   80F1 2E 05         [ 7]  206 	ld	l, #0x05
   80F3 CD 7F 83      [17]  207 	call	_cpct_pageMemory
                            208 ;src/main.c:81: pvmem = cpct_getScreenPtr(CPCT_VMEM_START, 0, 32);
   80F6 21 00 20      [10]  209 	ld	hl, #0x2000
   80F9 E5            [11]  210 	push	hl
   80FA 26 C0         [ 7]  211 	ld	h, #0xc0
   80FC E5            [11]  212 	push	hl
   80FD CD 15 83      [17]  213 	call	_cpct_getScreenPtr
   8100 4D            [ 4]  214 	ld	c, l
   8101 44            [ 4]  215 	ld	b, h
                            216 ;src/main.c:82: cpct_drawSolidBox(pvmem, *firstByteInPage, 2, 8);
   8102 21 00 40      [10]  217 	ld	hl, #0x4000
   8105 5E            [ 7]  218 	ld	e, (hl)
   8106 16 00         [ 7]  219 	ld	d, #0x00
   8108 21 02 08      [10]  220 	ld	hl, #0x0802
   810B E5            [11]  221 	push	hl
   810C D5            [11]  222 	push	de
   810D C5            [11]  223 	push	bc
   810E CD 6D 82      [17]  224 	call	_cpct_drawSolidBox
                            225 ;src/main.c:83: pvmem = cpct_getScreenPtr(CPCT_VMEM_START, 4, 32);
   8111 21 04 20      [10]  226 	ld	hl, #0x2004
   8114 E5            [11]  227 	push	hl
   8115 21 00 C0      [10]  228 	ld	hl, #0xc000
   8118 E5            [11]  229 	push	hl
   8119 CD 15 83      [17]  230 	call	_cpct_getScreenPtr
                            231 ;src/main.c:84: cpct_drawStringM1("RAMCFG_5", pvmem);
   811C 01 A3 81      [10]  232 	ld	bc, #___str_2+0
   811F E5            [11]  233 	push	hl
   8120 C5            [11]  234 	push	bc
   8121 CD BE 81      [17]  235 	call	_cpct_drawStringM1
                            236 ;src/main.c:86: cpct_pageMemory(RAMCFG_6 | BANK_0); // Set the 4th page (64kb to 80kb) in 0x4000-0x7FFF
   8124 2E 06         [ 7]  237 	ld	l, #0x06
   8126 CD 7F 83      [17]  238 	call	_cpct_pageMemory
                            239 ;src/main.c:87: pvmem = cpct_getScreenPtr(CPCT_VMEM_START, 0, 48);
   8129 21 00 30      [10]  240 	ld	hl, #0x3000
   812C E5            [11]  241 	push	hl
   812D 26 C0         [ 7]  242 	ld	h, #0xc0
   812F E5            [11]  243 	push	hl
   8130 CD 15 83      [17]  244 	call	_cpct_getScreenPtr
   8133 4D            [ 4]  245 	ld	c, l
   8134 44            [ 4]  246 	ld	b, h
                            247 ;src/main.c:88: cpct_drawSolidBox(pvmem, *firstByteInPage, 2, 8);
   8135 21 00 40      [10]  248 	ld	hl, #0x4000
   8138 5E            [ 7]  249 	ld	e, (hl)
   8139 16 00         [ 7]  250 	ld	d, #0x00
   813B 21 02 08      [10]  251 	ld	hl, #0x0802
   813E E5            [11]  252 	push	hl
   813F D5            [11]  253 	push	de
   8140 C5            [11]  254 	push	bc
   8141 CD 6D 82      [17]  255 	call	_cpct_drawSolidBox
                            256 ;src/main.c:89: pvmem = cpct_getScreenPtr(CPCT_VMEM_START, 4, 48);
   8144 21 04 30      [10]  257 	ld	hl, #0x3004
   8147 E5            [11]  258 	push	hl
   8148 21 00 C0      [10]  259 	ld	hl, #0xc000
   814B E5            [11]  260 	push	hl
   814C CD 15 83      [17]  261 	call	_cpct_getScreenPtr
                            262 ;src/main.c:90: cpct_drawStringM1("RAMCFG_6", pvmem);
   814F 01 AC 81      [10]  263 	ld	bc, #___str_3+0
   8152 E5            [11]  264 	push	hl
   8153 C5            [11]  265 	push	bc
   8154 CD BE 81      [17]  266 	call	_cpct_drawStringM1
                            267 ;src/main.c:92: cpct_pageMemory(RAMCFG_7 | BANK_0); // Set the 4th page (64kb to 80kb) in 0x4000-0x7FFF
   8157 2E 07         [ 7]  268 	ld	l, #0x07
   8159 CD 7F 83      [17]  269 	call	_cpct_pageMemory
                            270 ;src/main.c:93: pvmem = cpct_getScreenPtr(CPCT_VMEM_START, 0, 64);
   815C 21 00 40      [10]  271 	ld	hl, #0x4000
   815F E5            [11]  272 	push	hl
   8160 26 C0         [ 7]  273 	ld	h, #0xc0
   8162 E5            [11]  274 	push	hl
   8163 CD 15 83      [17]  275 	call	_cpct_getScreenPtr
   8166 4D            [ 4]  276 	ld	c, l
   8167 44            [ 4]  277 	ld	b, h
                            278 ;src/main.c:94: cpct_drawSolidBox(pvmem, *firstByteInPage, 2, 8);
   8168 21 00 40      [10]  279 	ld	hl, #0x4000
   816B 5E            [ 7]  280 	ld	e, (hl)
   816C 16 00         [ 7]  281 	ld	d, #0x00
   816E 21 02 08      [10]  282 	ld	hl, #0x0802
   8171 E5            [11]  283 	push	hl
   8172 D5            [11]  284 	push	de
   8173 C5            [11]  285 	push	bc
   8174 CD 6D 82      [17]  286 	call	_cpct_drawSolidBox
                            287 ;src/main.c:95: pvmem = cpct_getScreenPtr(CPCT_VMEM_START, 4, 64);
   8177 21 04 40      [10]  288 	ld	hl, #0x4004
   817A E5            [11]  289 	push	hl
   817B 21 00 C0      [10]  290 	ld	hl, #0xc000
   817E E5            [11]  291 	push	hl
   817F CD 15 83      [17]  292 	call	_cpct_getScreenPtr
                            293 ;src/main.c:96: cpct_drawStringM1("RAMCFG_7", pvmem);
   8182 01 B5 81      [10]  294 	ld	bc, #___str_4+0
   8185 E5            [11]  295 	push	hl
   8186 C5            [11]  296 	push	bc
   8187 CD BE 81      [17]  297 	call	_cpct_drawStringM1
                            298 ;src/main.c:98: cpct_pageMemory(DEFAULT_MEM_CFG); // Equivalent to RAMCFG_0 | BANK_0 
   818A 2E 00         [ 7]  299 	ld	l, #0x00
   818C CD 7F 83      [17]  300 	call	_cpct_pageMemory
                            301 ;src/main.c:101: while (1);
   818F                     302 00102$:
   818F 18 FE         [12]  303 	jr	00102$
   8191                     304 ___str_0:
   8191 52 41 4D 43 46 47   305 	.ascii "RAMCFG_0"
        5F 30
   8199 00                  306 	.db 0x00
   819A                     307 ___str_1:
   819A 52 41 4D 43 46 47   308 	.ascii "RAMCFG_4"
        5F 34
   81A2 00                  309 	.db 0x00
   81A3                     310 ___str_2:
   81A3 52 41 4D 43 46 47   311 	.ascii "RAMCFG_5"
        5F 35
   81AB 00                  312 	.db 0x00
   81AC                     313 ___str_3:
   81AC 52 41 4D 43 46 47   314 	.ascii "RAMCFG_6"
        5F 36
   81B4 00                  315 	.db 0x00
   81B5                     316 ___str_4:
   81B5 52 41 4D 43 46 47   317 	.ascii "RAMCFG_7"
        5F 37
   81BD 00                  318 	.db 0x00
                            319 	.area _CODE
                            320 	.area _INITIALIZER
                            321 	.area _CABS (ABS)
