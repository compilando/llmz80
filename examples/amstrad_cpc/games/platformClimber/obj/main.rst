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
                             12 	.globl _initializeCPC
                             13 	.globl _game
                             14 	.globl _showGameEnd
                             15 	.globl _cpct_setPALColour
                             16 	.globl _cpct_setPalette
                             17 	.globl _cpct_fw2hw
                             18 	.globl _cpct_setVideoMode
                             19 	.globl _cpct_disableFirmware
                             20 ;--------------------------------------------------------
                             21 ; special function registers
                             22 ;--------------------------------------------------------
                             23 ;--------------------------------------------------------
                             24 ; ram data
                             25 ;--------------------------------------------------------
                             26 	.area _DATA
                             27 ;--------------------------------------------------------
                             28 ; ram data
                             29 ;--------------------------------------------------------
                             30 	.area _INITIALIZED
                             31 ;--------------------------------------------------------
                             32 ; absolute external ram data
                             33 ;--------------------------------------------------------
                             34 	.area _DABS (ABS)
                             35 ;--------------------------------------------------------
                             36 ; global & static initialisations
                             37 ;--------------------------------------------------------
                             38 	.area _HOME
                             39 	.area _GSINIT
                             40 	.area _GSFINAL
                             41 	.area _GSINIT
                             42 ;--------------------------------------------------------
                             43 ; Home
                             44 ;--------------------------------------------------------
                             45 	.area _HOME
                             46 	.area _HOME
                             47 ;--------------------------------------------------------
                             48 ; code
                             49 ;--------------------------------------------------------
                             50 	.area _CODE
                             51 ;src/main.c:28: void initializeCPC() {
                             52 ;	---------------------------------
                             53 ; Function initializeCPC
                             54 ; ---------------------------------
   44D2                      55 _initializeCPC::
                             56 ;src/main.c:30: cpct_disableFirmware();
   44D2 CD A4 66      [17]   57 	call	_cpct_disableFirmware
                             58 ;src/main.c:33: cpct_fw2hw(G_palette, 16);
   44D5 21 10 00      [10]   59 	ld	hl, #0x0010
   44D8 E5            [11]   60 	push	hl
   44D9 21 EE 60      [10]   61 	ld	hl, #_G_palette
   44DC E5            [11]   62 	push	hl
   44DD CD 9A 65      [17]   63 	call	_cpct_fw2hw
                             64 ;src/main.c:34: cpct_setPalette(G_palette, 16);
   44E0 21 10 00      [10]   65 	ld	hl, #0x0010
   44E3 E5            [11]   66 	push	hl
   44E4 21 EE 60      [10]   67 	ld	hl, #_G_palette
   44E7 E5            [11]   68 	push	hl
   44E8 CD BE 63      [17]   69 	call	_cpct_setPalette
                             70 ;src/main.c:35: cpct_setBorder(G_palette[8]);
   44EB 21 F6 60      [10]   71 	ld	hl, #_G_palette + 8
   44EE 46            [ 7]   72 	ld	b, (hl)
   44EF C5            [11]   73 	push	bc
   44F0 33            [ 6]   74 	inc	sp
   44F1 3E 10         [ 7]   75 	ld	a, #0x10
   44F3 F5            [11]   76 	push	af
   44F4 33            [ 6]   77 	inc	sp
   44F5 CD 4B 64      [17]   78 	call	_cpct_setPALColour
                             79 ;src/main.c:38: cpct_setVideoMode(0);
   44F8 2E 00         [ 7]   80 	ld	l, #0x00
   44FA CD 5C 66      [17]   81 	call	_cpct_setVideoMode
   44FD C9            [10]   82 	ret
                             83 ;src/main.c:45: void main(void) {
                             84 ;	---------------------------------
                             85 ; Function main
                             86 ; ---------------------------------
   44FE                      87 _main::
                             88 ;src/main.c:47: u16 hi = 0;    // Hi-score
   44FE 01 00 00      [10]   89 	ld	bc, #0x0000
                             90 ;src/main.c:50: initializeCPC();
   4501 C5            [11]   91 	push	bc
   4502 CD D2 44      [17]   92 	call	_initializeCPC
   4505 C1            [10]   93 	pop	bc
                             94 ;src/main.c:55: while(1) {
   4506                      95 00104$:
                             96 ;src/main.c:56: score = game(hi);    // Play a game and get the score
   4506 C5            [11]   97 	push	bc
   4507 C5            [11]   98 	push	bc
   4508 CD B8 43      [17]   99 	call	_game
   450B F1            [10]  100 	pop	af
   450C C1            [10]  101 	pop	bc
                            102 ;src/main.c:57: showGameEnd(score);  // Show end-game stats
   450D E5            [11]  103 	push	hl
   450E C5            [11]  104 	push	bc
   450F E5            [11]  105 	push	hl
   4510 CD 0B 44      [17]  106 	call	_showGameEnd
   4513 F1            [10]  107 	pop	af
   4514 C1            [10]  108 	pop	bc
   4515 E1            [10]  109 	pop	hl
                            110 ;src/main.c:59: if (score > hi)      // Update hi-score
   4516 79            [ 4]  111 	ld	a, c
   4517 95            [ 4]  112 	sub	a, l
   4518 78            [ 4]  113 	ld	a, b
   4519 9C            [ 4]  114 	sbc	a, h
   451A 30 EA         [12]  115 	jr	NC,00104$
                            116 ;src/main.c:60: hi = score;
   451C 4D            [ 4]  117 	ld	c, l
   451D 44            [ 4]  118 	ld	b, h
   451E 18 E6         [12]  119 	jr	00104$
                            120 	.area _CODE
                            121 	.area _INITIALIZER
                            122 	.area _CABS (ABS)
