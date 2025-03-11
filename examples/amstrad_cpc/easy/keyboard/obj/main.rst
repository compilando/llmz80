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
                             13 	.globl _cpct_setPalette
                             14 	.globl _cpct_setVideoMode
                             15 	.globl _cpct_drawSprite
                             16 	.globl _cpct_isKeyPressed
                             17 	.globl _cpct_scanKeyboard_f
                             18 	.globl _cpct_disableFirmware
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
                             50 ;src/main.c:34: void main(void) {
                             51 ;	---------------------------------
                             52 ; Function main
                             53 ; ---------------------------------
   03EC                      54 _main::
                             55 ;src/main.c:35: u8  x=10, y=10;   // Sprite coordinates
   03EC 01 0A 0A      [10]   56 	ld	bc,#0x0a0a
                             57 ;src/main.c:42: cpct_disableFirmware();
   03EF C5            [11]   58 	push	bc
   03F0 CD B4 05      [17]   59 	call	_cpct_disableFirmware
   03F3 21 04 00      [10]   60 	ld	hl, #0x0004
   03F6 E5            [11]   61 	push	hl
   03F7 21 00 01      [10]   62 	ld	hl, #_G_palette
   03FA E5            [11]   63 	push	hl
   03FB CD 6A 04      [17]   64 	call	_cpct_setPalette
   03FE 2E 01         [ 7]   65 	ld	l, #0x01
   0400 CD A6 05      [17]   66 	call	_cpct_setVideoMode
   0403 C1            [10]   67 	pop	bc
                             68 ;src/main.c:53: while(1) {
   0404                      69 00116$:
                             70 ;src/main.c:57: cpct_scanKeyboard_f();
   0404 C5            [11]   71 	push	bc
   0405 CD 8D 04      [17]   72 	call	_cpct_scanKeyboard_f
   0408 21 00 02      [10]   73 	ld	hl, #0x0200
   040B CD 81 04      [17]   74 	call	_cpct_isKeyPressed
   040E C1            [10]   75 	pop	bc
   040F 7D            [ 4]   76 	ld	a, l
   0410 B7            [ 4]   77 	or	a, a
   0411 28 08         [12]   78 	jr	Z,00105$
   0413 79            [ 4]   79 	ld	a, c
   0414 D6 44         [ 7]   80 	sub	a, #0x44
   0416 30 03         [12]   81 	jr	NC,00105$
   0418 0C            [ 4]   82 	inc	c
   0419 18 11         [12]   83 	jr	00106$
   041B                      84 00105$:
                             85 ;src/main.c:62: else if (cpct_isKeyPressed(Key_CursorLeft)  && x > 0              ) --x; 
   041B C5            [11]   86 	push	bc
   041C 21 01 01      [10]   87 	ld	hl, #0x0101
   041F CD 81 04      [17]   88 	call	_cpct_isKeyPressed
   0422 C1            [10]   89 	pop	bc
   0423 7D            [ 4]   90 	ld	a, l
   0424 B7            [ 4]   91 	or	a, a
   0425 28 05         [12]   92 	jr	Z,00106$
   0427 79            [ 4]   93 	ld	a, c
   0428 B7            [ 4]   94 	or	a, a
   0429 28 01         [12]   95 	jr	Z,00106$
   042B 0D            [ 4]   96 	dec	c
   042C                      97 00106$:
                             98 ;src/main.c:63: if      (cpct_isKeyPressed(Key_CursorUp)    && y > 0              ) --y;
   042C C5            [11]   99 	push	bc
   042D 21 00 01      [10]  100 	ld	hl, #0x0100
   0430 CD 81 04      [17]  101 	call	_cpct_isKeyPressed
   0433 C1            [10]  102 	pop	bc
   0434 7D            [ 4]  103 	ld	a, l
   0435 B7            [ 4]  104 	or	a, a
   0436 28 07         [12]  105 	jr	Z,00112$
   0438 78            [ 4]  106 	ld	a, b
   0439 B7            [ 4]  107 	or	a, a
   043A 28 03         [12]  108 	jr	Z,00112$
   043C 05            [ 4]  109 	dec	b
   043D 18 12         [12]  110 	jr	00113$
   043F                     111 00112$:
                            112 ;src/main.c:64: else if (cpct_isKeyPressed(Key_CursorDown)  && y < (SCR_H - SP_H) ) ++y;
   043F C5            [11]  113 	push	bc
   0440 21 00 04      [10]  114 	ld	hl, #0x0400
   0443 CD 81 04      [17]  115 	call	_cpct_isKeyPressed
   0446 C1            [10]  116 	pop	bc
   0447 7D            [ 4]  117 	ld	a, l
   0448 B7            [ 4]  118 	or	a, a
   0449 28 06         [12]  119 	jr	Z,00113$
   044B 78            [ 4]  120 	ld	a, b
   044C D6 8A         [ 7]  121 	sub	a, #0x8a
   044E 30 01         [12]  122 	jr	NC,00113$
   0450 04            [ 4]  123 	inc	b
   0451                     124 00113$:
                            125 ;src/main.c:67: pvideomem = cpct_getScreenPtr(CPCT_VMEM_START, x, y);
   0451 C5            [11]  126 	push	bc
   0452 C5            [11]  127 	push	bc
   0453 21 00 C0      [10]  128 	ld	hl, #0xc000
   0456 E5            [11]  129 	push	hl
   0457 CD C5 05      [17]  130 	call	_cpct_getScreenPtr
   045A EB            [ 4]  131 	ex	de,hl
   045B 21 0C 3E      [10]  132 	ld	hl, #0x3e0c
   045E E5            [11]  133 	push	hl
   045F D5            [11]  134 	push	de
   0460 21 04 01      [10]  135 	ld	hl, #_G_ctlogo
   0463 E5            [11]  136 	push	hl
   0464 CD F7 04      [17]  137 	call	_cpct_drawSprite
   0467 C1            [10]  138 	pop	bc
   0468 18 9A         [12]  139 	jr	00116$
                            140 	.area _CODE
                            141 	.area _INITIALIZER
                            142 	.area _CABS (ABS)
