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
                             12 	.globl _printMessages
                             13 	.globl _printf
                             14 	.globl _cpct_setVideoMemoryPage
                             15 	.globl _cpct_setPALColour
                             16 	.globl _cpct_waitVSYNC
                             17 	.globl _cpct_isKeyPressed
                             18 	.globl _cpct_scanKeyboard
                             19 	.globl _cpct_setStackLocation
                             20 	.globl _cpct_memcpy
                             21 	.globl _cpct_memset_f64
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
                             54 ;src/main.c:29: void printMessages() {
                             55 ;	---------------------------------
                             56 ; Function printMessages
                             57 ; ---------------------------------
   0200                      58 _printMessages::
                             59 ;src/main.c:33: printf("     \017\003SET PROGRAM STACK LOCATION DEMO\n\r");
   0200 21 8B 02      [10]   60 	ld	hl, #___str_0
   0203 E5            [11]   61 	push	hl
   0204 CD 1A 06      [17]   62 	call	_printf
                             63 ;src/main.c:34: printf("    \017\002#################################\n\n\r");
   0207 21 B4 02      [10]   64 	ld	hl, #___str_1
   020A E3            [19]   65 	ex	(sp),hl
   020B CD 1A 06      [17]   66 	call	_printf
                             67 ;src/main.c:36: printf("\017\001  This program  changes  stack  location");
   020E 21 DF 02      [10]   68 	ld	hl, #___str_2
   0211 E3            [19]   69 	ex	(sp),hl
   0212 CD 1A 06      [17]   70 	call	_printf
                             71 ;src/main.c:37: printf("to \017\0030x200\017\001, just  below  the start  of the");
   0215 21 0A 03      [10]   72 	ld	hl, #___str_3
   0218 E3            [19]   73 	ex	(sp),hl
   0219 CD 1A 06      [17]   74 	call	_printf
                             75 ;src/main.c:38: printf("main function.\n\n\r");
   021C 21 37 03      [10]   76 	ld	hl, #___str_4
   021F E3            [19]   77 	ex	(sp),hl
   0220 CD 1A 06      [17]   78 	call	_printf
                             79 ;src/main.c:40: printf("  With this change, the 3rd  memory bank");
   0223 21 49 03      [10]   80 	ld	hl, #___str_5
   0226 E3            [19]   81 	ex	(sp),hl
   0227 CD 1A 06      [17]   82 	call	_printf
                             83 ;src/main.c:41: printf("can be  enterely used as  double buffer,");
   022A 21 72 03      [10]   84 	ld	hl, #___str_6
   022D E3            [19]   85 	ex	(sp),hl
   022E CD 1A 06      [17]   86 	call	_printf
                             87 ;src/main.c:42: printf("making easier to map code and  data into");
   0231 21 9B 03      [10]   88 	ld	hl, #___str_7
   0234 E3            [19]   89 	ex	(sp),hl
   0235 CD 1A 06      [17]   90 	call	_printf
                             91 ;src/main.c:43: printf("memory.\n\n\r");
   0238 21 C4 03      [10]   92 	ld	hl, #___str_8
   023B E3            [19]   93 	ex	(sp),hl
   023C CD 1A 06      [17]   94 	call	_printf
                             95 ;src/main.c:45: printf("  If you  want to  check this, open  the");
   023F 21 CF 03      [10]   96 	ld	hl, #___str_9
   0242 E3            [19]   97 	ex	(sp),hl
   0243 CD 1A 06      [17]   98 	call	_printf
                             99 ;src/main.c:46: printf("debugger and  have  a look at the  stack");
   0246 21 F8 03      [10]  100 	ld	hl, #___str_10
   0249 E3            [19]  101 	ex	(sp),hl
   024A CD 1A 06      [17]  102 	call	_printf
                            103 ;src/main.c:47: printf("pointer (\017\002SP\017\001) and the stack contents.\n\n\r");
   024D 21 21 04      [10]  104 	ld	hl, #___str_11
   0250 E3            [19]  105 	ex	(sp),hl
   0251 CD 1A 06      [17]  106 	call	_printf
                            107 ;src/main.c:49: printf("  Now you can use \017\002keys \017\003[\017\0021\017\003]");
   0254 21 4D 04      [10]  108 	ld	hl, #___str_12
   0257 E3            [19]  109 	ex	(sp),hl
   0258 CD 1A 06      [17]  110 	call	_printf
                            111 ;src/main.c:50: printf("\017\001&\017\003[\017\0022\017\003]\017\001 to change");
   025B 21 70 04      [10]  112 	ld	hl, #___str_13
   025E E3            [19]  113 	ex	(sp),hl
   025F CD 1A 06      [17]  114 	call	_printf
                            115 ;src/main.c:51: printf("from main  screen  buffer to  the double");
   0262 21 89 04      [10]  116 	ld	hl, #___str_14
   0265 E3            [19]  117 	ex	(sp),hl
   0266 CD 1A 06      [17]  118 	call	_printf
                            119 ;src/main.c:52: printf("buffer which contains a fullscreen image");
   0269 21 B2 04      [10]  120 	ld	hl, #___str_15
   026C E3            [19]  121 	ex	(sp),hl
   026D CD 1A 06      [17]  122 	call	_printf
                            123 ;src/main.c:53: printf("with a pattern like this:\n\n\r");
   0270 21 DB 04      [10]  124 	ld	hl, #___str_16
   0273 E3            [19]  125 	ex	(sp),hl
   0274 CD 1A 06      [17]  126 	call	_printf
   0277 F1            [10]  127 	pop	af
                            128 ;src/main.c:55: for (i=0; i < 60; ++i)
   0278 0E 00         [ 7]  129 	ld	c, #0x00
   027A                     130 00102$:
                            131 ;src/main.c:56: printf("\017\001#\017\003#");
   027A C5            [11]  132 	push	bc
   027B 21 F8 04      [10]  133 	ld	hl, #___str_17
   027E E5            [11]  134 	push	hl
   027F CD 1A 06      [17]  135 	call	_printf
   0282 F1            [10]  136 	pop	af
   0283 C1            [10]  137 	pop	bc
                            138 ;src/main.c:55: for (i=0; i < 60; ++i)
   0284 0C            [ 4]  139 	inc	c
   0285 79            [ 4]  140 	ld	a, c
   0286 D6 3C         [ 7]  141 	sub	a, #0x3c
   0288 38 F0         [12]  142 	jr	C,00102$
   028A C9            [10]  143 	ret
   028B                     144 ___str_0:
   028B 20 20 20 20 20      145 	.ascii "     "
   0290 0F                  146 	.db 0x0f
   0291 03                  147 	.db 0x03
   0292 53 45 54 20 50 52   148 	.ascii "SET PROGRAM STACK LOCATION DEMO"
        4F 47 52 41 4D 20
        53 54 41 43 4B 20
        4C 4F 43 41 54 49
        4F 4E 20 44 45 4D
        4F
   02B1 0A                  149 	.db 0x0a
   02B2 0D                  150 	.db 0x0d
   02B3 00                  151 	.db 0x00
   02B4                     152 ___str_1:
   02B4 20 20 20 20         153 	.ascii "    "
   02B8 0F                  154 	.db 0x0f
   02B9 02                  155 	.db 0x02
   02BA 23 23 23 23 23 23   156 	.ascii "#################################"
        23 23 23 23 23 23
        23 23 23 23 23 23
        23 23 23 23 23 23
        23 23 23 23 23 23
        23 23 23
   02DB 0A                  157 	.db 0x0a
   02DC 0A                  158 	.db 0x0a
   02DD 0D                  159 	.db 0x0d
   02DE 00                  160 	.db 0x00
   02DF                     161 ___str_2:
   02DF 0F                  162 	.db 0x0f
   02E0 01                  163 	.db 0x01
   02E1 20 20 54 68 69 73   164 	.ascii "  This program  changes  stack  location"
        20 70 72 6F 67 72
        61 6D 20 20 63 68
        61 6E 67 65 73 20
        20 73 74 61 63 6B
        20 20 6C 6F 63 61
        74 69 6F 6E
   0309 00                  165 	.db 0x00
   030A                     166 ___str_3:
   030A 74 6F 20            167 	.ascii "to "
   030D 0F                  168 	.db 0x0f
   030E 03                  169 	.db 0x03
   030F 30 78 32 30 30      170 	.ascii "0x200"
   0314 0F                  171 	.db 0x0f
   0315 01                  172 	.db 0x01
   0316 2C 20 6A 75 73 74   173 	.ascii ", just  below  the start  of the"
        20 20 62 65 6C 6F
        77 20 20 74 68 65
        20 73 74 61 72 74
        20 20 6F 66 20 74
        68 65
   0336 00                  174 	.db 0x00
   0337                     175 ___str_4:
   0337 6D 61 69 6E 20 66   176 	.ascii "main function."
        75 6E 63 74 69 6F
        6E 2E
   0345 0A                  177 	.db 0x0a
   0346 0A                  178 	.db 0x0a
   0347 0D                  179 	.db 0x0d
   0348 00                  180 	.db 0x00
   0349                     181 ___str_5:
   0349 20 20 57 69 74 68   182 	.ascii "  With this change, the 3rd  memory bank"
        20 74 68 69 73 20
        63 68 61 6E 67 65
        2C 20 74 68 65 20
        33 72 64 20 20 6D
        65 6D 6F 72 79 20
        62 61 6E 6B
   0371 00                  183 	.db 0x00
   0372                     184 ___str_6:
   0372 63 61 6E 20 62 65   185 	.ascii "can be  enterely used as  double buffer,"
        20 20 65 6E 74 65
        72 65 6C 79 20 75
        73 65 64 20 61 73
        20 20 64 6F 75 62
        6C 65 20 62 75 66
        66 65 72 2C
   039A 00                  186 	.db 0x00
   039B                     187 ___str_7:
   039B 6D 61 6B 69 6E 67   188 	.ascii "making easier to map code and  data into"
        20 65 61 73 69 65
        72 20 74 6F 20 6D
        61 70 20 63 6F 64
        65 20 61 6E 64 20
        20 64 61 74 61 20
        69 6E 74 6F
   03C3 00                  189 	.db 0x00
   03C4                     190 ___str_8:
   03C4 6D 65 6D 6F 72 79   191 	.ascii "memory."
        2E
   03CB 0A                  192 	.db 0x0a
   03CC 0A                  193 	.db 0x0a
   03CD 0D                  194 	.db 0x0d
   03CE 00                  195 	.db 0x00
   03CF                     196 ___str_9:
   03CF 20 20 49 66 20 79   197 	.ascii "  If you  want to  check this, open  the"
        6F 75 20 20 77 61
        6E 74 20 74 6F 20
        20 63 68 65 63 6B
        20 74 68 69 73 2C
        20 6F 70 65 6E 20
        20 74 68 65
   03F7 00                  198 	.db 0x00
   03F8                     199 ___str_10:
   03F8 64 65 62 75 67 67   200 	.ascii "debugger and  have  a look at the  stack"
        65 72 20 61 6E 64
        20 20 68 61 76 65
        20 20 61 20 6C 6F
        6F 6B 20 61 74 20
        74 68 65 20 20 73
        74 61 63 6B
   0420 00                  201 	.db 0x00
   0421                     202 ___str_11:
   0421 70 6F 69 6E 74 65   203 	.ascii "pointer ("
        72 20 28
   042A 0F                  204 	.db 0x0f
   042B 02                  205 	.db 0x02
   042C 53 50               206 	.ascii "SP"
   042E 0F                  207 	.db 0x0f
   042F 01                  208 	.db 0x01
   0430 29 20 61 6E 64 20   209 	.ascii ") and the stack contents."
        74 68 65 20 73 74
        61 63 6B 20 63 6F
        6E 74 65 6E 74 73
        2E
   0449 0A                  210 	.db 0x0a
   044A 0A                  211 	.db 0x0a
   044B 0D                  212 	.db 0x0d
   044C 00                  213 	.db 0x00
   044D                     214 ___str_12:
   044D 20 20 4E 6F 77 20   215 	.ascii "  Now you can use "
        79 6F 75 20 63 61
        6E 20 75 73 65 20
   045F 0F                  216 	.db 0x0f
   0460 02                  217 	.db 0x02
   0461 6B 65 79 73 20      218 	.ascii "keys "
   0466 0F                  219 	.db 0x0f
   0467 03                  220 	.db 0x03
   0468 5B                  221 	.ascii "["
   0469 0F                  222 	.db 0x0f
   046A 02                  223 	.db 0x02
   046B 31                  224 	.ascii "1"
   046C 0F                  225 	.db 0x0f
   046D 03                  226 	.db 0x03
   046E 5D                  227 	.ascii "]"
   046F 00                  228 	.db 0x00
   0470                     229 ___str_13:
   0470 0F                  230 	.db 0x0f
   0471 01                  231 	.db 0x01
   0472 26                  232 	.ascii "&"
   0473 0F                  233 	.db 0x0f
   0474 03                  234 	.db 0x03
   0475 5B                  235 	.ascii "["
   0476 0F                  236 	.db 0x0f
   0477 02                  237 	.db 0x02
   0478 32                  238 	.ascii "2"
   0479 0F                  239 	.db 0x0f
   047A 03                  240 	.db 0x03
   047B 5D                  241 	.ascii "]"
   047C 0F                  242 	.db 0x0f
   047D 01                  243 	.db 0x01
   047E 20 74 6F 20 63 68   244 	.ascii " to change"
        61 6E 67 65
   0488 00                  245 	.db 0x00
   0489                     246 ___str_14:
   0489 66 72 6F 6D 20 6D   247 	.ascii "from main  screen  buffer to  the double"
        61 69 6E 20 20 73
        63 72 65 65 6E 20
        20 62 75 66 66 65
        72 20 74 6F 20 20
        74 68 65 20 64 6F
        75 62 6C 65
   04B1 00                  248 	.db 0x00
   04B2                     249 ___str_15:
   04B2 62 75 66 66 65 72   250 	.ascii "buffer which contains a fullscreen image"
        20 77 68 69 63 68
        20 63 6F 6E 74 61
        69 6E 73 20 61 20
        66 75 6C 6C 73 63
        72 65 65 6E 20 69
        6D 61 67 65
   04DA 00                  251 	.db 0x00
   04DB                     252 ___str_16:
   04DB 77 69 74 68 20 61   253 	.ascii "with a pattern like this:"
        20 70 61 74 74 65
        72 6E 20 6C 69 6B
        65 20 74 68 69 73
        3A
   04F4 0A                  254 	.db 0x0a
   04F5 0A                  255 	.db 0x0a
   04F6 0D                  256 	.db 0x0d
   04F7 00                  257 	.db 0x00
   04F8                     258 ___str_17:
   04F8 0F                  259 	.db 0x0f
   04F9 01                  260 	.db 0x01
   04FA 23                  261 	.ascii "#"
   04FB 0F                  262 	.db 0x0f
   04FC 03                  263 	.db 0x03
   04FD 23                  264 	.ascii "#"
   04FE 00                  265 	.db 0x00
                            266 ;src/main.c:62: void main(void) { 
                            267 ;	---------------------------------
                            268 ; Function main
                            269 ; ---------------------------------
   04FF                     270 _main::
                            271 ;src/main.c:64: cpct_clearScreen_f64(0x0000);
   04FF 21 00 40      [10]  272 	ld	hl, #0x4000
   0502 E5            [11]  273 	push	hl
   0503 26 00         [ 7]  274 	ld	h, #0x00
   0505 E5            [11]  275 	push	hl
   0506 26 C0         [ 7]  276 	ld	h, #0xc0
   0508 E5            [11]  277 	push	hl
   0509 CD 96 05      [17]  278 	call	_cpct_memset_f64
                            279 ;src/main.c:65: printMessages();
   050C CD 00 02      [17]  280 	call	_printMessages
                            281 ;src/main.c:69: cpct_disableFirmware();
   050F CD 3F 06      [17]  282 	call	_cpct_disableFirmware
                            283 ;src/main.c:76: cpct_memcpy(NEW_STACK_LOCATION - 6, PREVIOUS_STACK_LOCATION - 6, 6);
   0512 21 06 00      [10]  284 	ld	hl, #0x0006
   0515 E5            [11]  285 	push	hl
   0516 21 FA BF      [10]  286 	ld	hl, #0xbffa
   0519 E5            [11]  287 	push	hl
   051A 26 01         [ 7]  288 	ld	h, #0x01
   051C E5            [11]  289 	push	hl
   051D CD 37 06      [17]  290 	call	_cpct_memcpy
                            291 ;src/main.c:77: cpct_setStackLocation(NEW_STACK_LOCATION - 6);
   0520 21 FA 01      [10]  292 	ld	hl, #0x01fa
   0523 CD E1 05      [17]  293 	call	_cpct_setStackLocation
                            294 ;src/main.c:81: cpct_memset_f64((void*)0x8000, 0xFFF0, 0x4000);
   0526 21 00 40      [10]  295 	ld	hl, #0x4000
   0529 E5            [11]  296 	push	hl
   052A 21 F0 FF      [10]  297 	ld	hl, #0xfff0
   052D E5            [11]  298 	push	hl
   052E 21 00 80      [10]  299 	ld	hl, #0x8000
   0531 E5            [11]  300 	push	hl
   0532 CD 96 05      [17]  301 	call	_cpct_memset_f64
                            302 ;src/main.c:85: while(1) {
   0535                     303 00107$:
                            304 ;src/main.c:86: cpct_waitVSYNC();
   0535 CD E5 05      [17]  305 	call	_cpct_waitVSYNC
                            306 ;src/main.c:87: cpct_scanKeyboard();     
   0538 CD 50 06      [17]  307 	call	_cpct_scanKeyboard
                            308 ;src/main.c:89: if (cpct_isKeyPressed(Key_1)) {
   053B 21 08 01      [10]  309 	ld	hl, #0x0108
   053E CD 6B 05      [17]  310 	call	_cpct_isKeyPressed
   0541 7D            [ 4]  311 	ld	a, l
   0542 B7            [ 4]  312 	or	a, a
   0543 28 0E         [12]  313 	jr	Z,00104$
                            314 ;src/main.c:90: cpct_setBorder(4);
   0545 21 10 04      [10]  315 	ld	hl, #0x0410
   0548 E5            [11]  316 	push	hl
   0549 CD 77 05      [17]  317 	call	_cpct_setPALColour
                            318 ;src/main.c:91: cpct_setVideoMemoryPage(cpct_pageC0);
   054C 2E 30         [ 7]  319 	ld	l, #0x30
   054E CD 8D 05      [17]  320 	call	_cpct_setVideoMemoryPage
   0551 18 E2         [12]  321 	jr	00107$
   0553                     322 00104$:
                            323 ;src/main.c:92: } else if (cpct_isKeyPressed(Key_2)) {
   0553 21 08 02      [10]  324 	ld	hl, #0x0208
   0556 CD 6B 05      [17]  325 	call	_cpct_isKeyPressed
   0559 7D            [ 4]  326 	ld	a, l
   055A B7            [ 4]  327 	or	a, a
   055B 28 D8         [12]  328 	jr	Z,00107$
                            329 ;src/main.c:93: cpct_setBorder(3);
   055D 21 10 03      [10]  330 	ld	hl, #0x0310
   0560 E5            [11]  331 	push	hl
   0561 CD 77 05      [17]  332 	call	_cpct_setPALColour
                            333 ;src/main.c:94: cpct_setVideoMemoryPage(cpct_page80);
   0564 2E 20         [ 7]  334 	ld	l, #0x20
   0566 CD 8D 05      [17]  335 	call	_cpct_setVideoMemoryPage
   0569 18 CA         [12]  336 	jr	00107$
                            337 	.area _CODE
                            338 	.area _INITIALIZER
                            339 	.area _CABS (ABS)
