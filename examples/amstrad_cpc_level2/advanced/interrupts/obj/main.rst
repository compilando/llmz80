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
                             13 	.globl _myInterruptHandler
                             14 	.globl _cpct_setPALColour
                             15 	.globl _cpct_drawStringM1
                             16 	.globl _cpct_setDrawCharM1
                             17 	.globl _cpct_setInterruptHandler
                             18 	.globl _cpct_disableFirmware
                             19 ;--------------------------------------------------------
                             20 ; special function registers
                             21 ;--------------------------------------------------------
                             22 ;--------------------------------------------------------
                             23 ; ram data
                             24 ;--------------------------------------------------------
                             25 	.area _DATA
   427E                      26 _myInterruptHandler_i_1_128:
   427E                      27 	.ds 1
                             28 ;--------------------------------------------------------
                             29 ; ram data
                             30 ;--------------------------------------------------------
                             31 	.area _INITIALIZED
                             32 ;--------------------------------------------------------
                             33 ; absolute external ram data
                             34 ;--------------------------------------------------------
                             35 	.area _DABS (ABS)
                             36 ;--------------------------------------------------------
                             37 ; global & static initialisations
                             38 ;--------------------------------------------------------
                             39 	.area _HOME
                             40 	.area _GSINIT
                             41 	.area _GSFINAL
                             42 	.area _GSINIT
                             43 ;--------------------------------------------------------
                             44 ; Home
                             45 ;--------------------------------------------------------
                             46 	.area _HOME
                             47 	.area _HOME
                             48 ;--------------------------------------------------------
                             49 ; code
                             50 ;--------------------------------------------------------
                             51 	.area _CODE
                             52 ;src/main.c:30: void myInterruptHandler() {
                             53 ;	---------------------------------
                             54 ; Function myInterruptHandler
                             55 ; ---------------------------------
   4000                      56 _myInterruptHandler::
                             57 ;src/main.c:34: cpct_setBorder(i+1);
   4000 21 7E 42      [10]   58 	ld	hl,#_myInterruptHandler_i_1_128 + 0
   4003 46            [ 7]   59 	ld	b, (hl)
   4004 04            [ 4]   60 	inc	b
   4005 C5            [11]   61 	push	bc
   4006 33            [ 6]   62 	inc	sp
   4007 3E 10         [ 7]   63 	ld	a, #0x10
   4009 F5            [11]   64 	push	af
   400A 33            [ 6]   65 	inc	sp
   400B CD 62 41      [17]   66 	call	_cpct_setPALColour
                             67 ;src/main.c:37: if (++i > 5) i=0;
   400E FD 21 7E 42   [14]   68 	ld	iy, #_myInterruptHandler_i_1_128
   4012 FD 34 00      [23]   69 	inc	0 (iy)
   4015 3E 05         [ 7]   70 	ld	a, #0x05
   4017 FD 96 00      [19]   71 	sub	a, 0 (iy)
   401A D0            [11]   72 	ret	NC
   401B FD 36 00 00   [19]   73 	ld	0 (iy), #0x00
   401F C9            [10]   74 	ret
                             75 ;src/main.c:43: void printMessages() {
                             76 ;	---------------------------------
                             77 ; Function printMessages
                             78 ; ---------------------------------
   4020                      79 _printMessages::
                             80 ;src/main.c:45: cpct_setDrawCharM1(0, 3);
   4020 21 00 03      [10]   81 	ld	hl, #0x0300
   4023 E5            [11]   82 	push	hl
   4024 CD FF 41      [17]   83 	call	_cpct_setDrawCharM1
                             84 ;src/main.c:46: cpct_drawStringM1("Interrupt Handler Example", pvm);
   4027 21 00 C0      [10]   85 	ld	hl, #0xc000
   402A E5            [11]   86 	push	hl
   402B 21 71 40      [10]   87 	ld	hl, #___str_0
   402E E5            [11]   88 	push	hl
   402F CD 6E 41      [17]   89 	call	_cpct_drawStringM1
                             90 ;src/main.c:49: cpct_setDrawCharM1(1, 0);
   4032 21 01 00      [10]   91 	ld	hl, #0x0001
   4035 E5            [11]   92 	push	hl
   4036 CD FF 41      [17]   93 	call	_cpct_setDrawCharM1
                             94 ;src/main.c:50: cpct_drawStringM1("This example is running a void loop, but", pvm);
   4039 21 F0 C0      [10]   95 	ld	hl, #0xc0f0
   403C E5            [11]   96 	push	hl
   403D 21 8B 40      [10]   97 	ld	hl, #___str_1
   4040 E5            [11]   98 	push	hl
   4041 CD 6E 41      [17]   99 	call	_cpct_drawStringM1
                            100 ;src/main.c:52: cpct_drawStringM1("border color is changed 6 times each", pvm);
   4044 21 40 C1      [10]  101 	ld	hl, #0xc140
   4047 E5            [11]  102 	push	hl
   4048 21 B4 40      [10]  103 	ld	hl, #___str_2
   404B E5            [11]  104 	push	hl
   404C CD 6E 41      [17]  105 	call	_cpct_drawStringM1
                            106 ;src/main.c:54: cpct_drawStringM1("frame. This change  is done by the inte-", pvm);
   404F 21 90 C1      [10]  107 	ld	hl, #0xc190
   4052 E5            [11]  108 	push	hl
   4053 21 D9 40      [10]  109 	ld	hl, #___str_3
   4056 E5            [11]  110 	push	hl
   4057 CD 6E 41      [17]  111 	call	_cpct_drawStringM1
                            112 ;src/main.c:56: cpct_drawStringM1("rrupt handler. As z80 produces 300 inte-", pvm);
   405A 21 E0 C1      [10]  113 	ld	hl, #0xc1e0
   405D E5            [11]  114 	push	hl
   405E 21 02 41      [10]  115 	ld	hl, #___str_4
   4061 E5            [11]  116 	push	hl
   4062 CD 6E 41      [17]  117 	call	_cpct_drawStringM1
                            118 ;src/main.c:58: cpct_drawStringM1("rrupts per second, you have 6 per frame.", pvm);
   4065 21 30 C2      [10]  119 	ld	hl, #0xc230
   4068 E5            [11]  120 	push	hl
   4069 21 2B 41      [10]  121 	ld	hl, #___str_5
   406C E5            [11]  122 	push	hl
   406D CD 6E 41      [17]  123 	call	_cpct_drawStringM1
   4070 C9            [10]  124 	ret
   4071                     125 ___str_0:
   4071 49 6E 74 65 72 72   126 	.ascii "Interrupt Handler Example"
        75 70 74 20 48 61
        6E 64 6C 65 72 20
        45 78 61 6D 70 6C
        65
   408A 00                  127 	.db 0x00
   408B                     128 ___str_1:
   408B 54 68 69 73 20 65   129 	.ascii "This example is running a void loop, but"
        78 61 6D 70 6C 65
        20 69 73 20 72 75
        6E 6E 69 6E 67 20
        61 20 76 6F 69 64
        20 6C 6F 6F 70 2C
        20 62 75 74
   40B3 00                  130 	.db 0x00
   40B4                     131 ___str_2:
   40B4 62 6F 72 64 65 72   132 	.ascii "border color is changed 6 times each"
        20 63 6F 6C 6F 72
        20 69 73 20 63 68
        61 6E 67 65 64 20
        36 20 74 69 6D 65
        73 20 65 61 63 68
   40D8 00                  133 	.db 0x00
   40D9                     134 ___str_3:
   40D9 66 72 61 6D 65 2E   135 	.ascii "frame. This change  is done by the inte-"
        20 54 68 69 73 20
        63 68 61 6E 67 65
        20 20 69 73 20 64
        6F 6E 65 20 62 79
        20 74 68 65 20 69
        6E 74 65 2D
   4101 00                  136 	.db 0x00
   4102                     137 ___str_4:
   4102 72 72 75 70 74 20   138 	.ascii "rrupt handler. As z80 produces 300 inte-"
        68 61 6E 64 6C 65
        72 2E 20 41 73 20
        7A 38 30 20 70 72
        6F 64 75 63 65 73
        20 33 30 30 20 69
        6E 74 65 2D
   412A 00                  139 	.db 0x00
   412B                     140 ___str_5:
   412B 72 72 75 70 74 73   141 	.ascii "rrupts per second, you have 6 per frame."
        20 70 65 72 20 73
        65 63 6F 6E 64 2C
        20 79 6F 75 20 68
        61 76 65 20 36 20
        70 65 72 20 66 72
        61 6D 65 2E
   4153 00                  142 	.db 0x00
                            143 ;src/main.c:65: void main(void) {
                            144 ;	---------------------------------
                            145 ; Function main
                            146 ; ---------------------------------
   4154                     147 _main::
                            148 ;src/main.c:69: cpct_disableFirmware();
   4154 CD EE 41      [17]  149 	call	_cpct_disableFirmware
                            150 ;src/main.c:70: cpct_setInterruptHandler( myInterruptHandler );
   4157 21 00 40      [10]  151 	ld	hl, #_myInterruptHandler
   415A CD 53 42      [17]  152 	call	_cpct_setInterruptHandler
                            153 ;src/main.c:73: printMessages();
   415D CD 20 40      [17]  154 	call	_printMessages
                            155 ;src/main.c:77: while (1);
   4160                     156 00102$:
   4160 18 FE         [12]  157 	jr	00102$
                            158 	.area _CODE
                            159 	.area _INITIALIZER
                            160 	.area _CABS (ABS)
