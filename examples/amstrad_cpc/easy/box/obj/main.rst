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
                             12 	.globl _cpct_drawSolidBox
                             13 	.globl _cpct_px2byteM1
                             14 	.globl _cpct_memset
                             15 ;--------------------------------------------------------
                             16 ; special function registers
                             17 ;--------------------------------------------------------
                             18 ;--------------------------------------------------------
                             19 ; ram data
                             20 ;--------------------------------------------------------
                             21 	.area _DATA
                             22 ;--------------------------------------------------------
                             23 ; ram data
                             24 ;--------------------------------------------------------
                             25 	.area _INITIALIZED
                             26 ;--------------------------------------------------------
                             27 ; absolute external ram data
                             28 ;--------------------------------------------------------
                             29 	.area _DABS (ABS)
                             30 ;--------------------------------------------------------
                             31 ; global & static initialisations
                             32 ;--------------------------------------------------------
                             33 	.area _HOME
                             34 	.area _GSINIT
                             35 	.area _GSFINAL
                             36 	.area _GSINIT
                             37 ;--------------------------------------------------------
                             38 ; Home
                             39 ;--------------------------------------------------------
                             40 	.area _HOME
                             41 	.area _HOME
                             42 ;--------------------------------------------------------
                             43 ; code
                             44 ;--------------------------------------------------------
                             45 	.area _CODE
                             46 ;src/main.c:36: void main(void) {
                             47 ;	---------------------------------
                             48 ; Function main
                             49 ; ---------------------------------
   0100                      50 _main::
                             51 ;src/main.c:38: cpct_clearScreen(0x00);
   0100 21 00 40      [10]   52 	ld	hl, #0x4000
   0103 E5            [11]   53 	push	hl
   0104 AF            [ 4]   54 	xor	a, a
   0105 F5            [11]   55 	push	af
   0106 33            [ 6]   56 	inc	sp
   0107 26 C0         [ 7]   57 	ld	h, #0xc0
   0109 E5            [11]   58 	push	hl
   010A CD 06 02      [17]   59 	call	_cpct_memset
                             60 ;src/main.c:43: cpct_drawSolidBox((u8*)0xC235, cpct_px2byteM1(2, 2, 1, 1), 10, 20); 
   010D 21 01 01      [10]   61 	ld	hl, #0x0101
   0110 E5            [11]   62 	push	hl
   0111 21 02 02      [10]   63 	ld	hl, #0x0202
   0114 E5            [11]   64 	push	hl
   0115 CD 14 02      [17]   65 	call	_cpct_px2byteM1
   0118 F1            [10]   66 	pop	af
   0119 F1            [10]   67 	pop	af
   011A 26 00         [ 7]   68 	ld	h, #0x00
   011C 01 0A 14      [10]   69 	ld	bc, #0x140a
   011F C5            [11]   70 	push	bc
   0120 E5            [11]   71 	push	hl
   0121 21 35 C2      [10]   72 	ld	hl, #0xc235
   0124 E5            [11]   73 	push	hl
   0125 CD 35 02      [17]   74 	call	_cpct_drawSolidBox
                             75 ;src/main.c:44: cpct_drawSolidBox((u8*)0xC245, cpct_px2byteM1(1, 0, 2, 1), 10, 20); 
   0128 21 02 01      [10]   76 	ld	hl, #0x0102
   012B E5            [11]   77 	push	hl
   012C 21 01 00      [10]   78 	ld	hl, #0x0001
   012F E5            [11]   79 	push	hl
   0130 CD 14 02      [17]   80 	call	_cpct_px2byteM1
   0133 F1            [10]   81 	pop	af
   0134 F1            [10]   82 	pop	af
   0135 26 00         [ 7]   83 	ld	h, #0x00
   0137 01 0A 14      [10]   84 	ld	bc, #0x140a
   013A C5            [11]   85 	push	bc
   013B E5            [11]   86 	push	hl
   013C 21 45 C2      [10]   87 	ld	hl, #0xc245
   013F E5            [11]   88 	push	hl
   0140 CD 35 02      [17]   89 	call	_cpct_drawSolidBox
                             90 ;src/main.c:45: cpct_drawSolidBox((u8*)0xC255, cpct_px2byteM1(0, 2, 0, 1), 10, 20); 
   0143 21 00 01      [10]   91 	ld	hl, #0x0100
   0146 E5            [11]   92 	push	hl
   0147 26 02         [ 7]   93 	ld	h, #0x02
   0149 E5            [11]   94 	push	hl
   014A CD 14 02      [17]   95 	call	_cpct_px2byteM1
   014D F1            [10]   96 	pop	af
   014E F1            [10]   97 	pop	af
   014F 26 00         [ 7]   98 	ld	h, #0x00
   0151 01 0A 14      [10]   99 	ld	bc, #0x140a
   0154 C5            [11]  100 	push	bc
   0155 E5            [11]  101 	push	hl
   0156 21 55 C2      [10]  102 	ld	hl, #0xc255
   0159 E5            [11]  103 	push	hl
   015A CD 35 02      [17]  104 	call	_cpct_drawSolidBox
                            105 ;src/main.c:48: cpct_drawSolidBox((u8*)0xC325, 0xAA, 10, 20); // 0xAA = cpct_px2byteM1(3, 0, 3, 0)
   015D 21 0A 14      [10]  106 	ld	hl, #0x140a
   0160 E5            [11]  107 	push	hl
   0161 21 AA 00      [10]  108 	ld	hl, #0x00aa
   0164 E5            [11]  109 	push	hl
   0165 21 25 C3      [10]  110 	ld	hl, #0xc325
   0168 E5            [11]  111 	push	hl
   0169 CD 35 02      [17]  112 	call	_cpct_drawSolidBox
                            113 ;src/main.c:49: cpct_drawSolidBox((u8*)0xC335, 0xA0, 10, 20); // 0xA0 = cpct_px2byteM1(1, 0, 1, 0)
   016C 21 0A 14      [10]  114 	ld	hl, #0x140a
   016F E5            [11]  115 	push	hl
   0170 21 A0 00      [10]  116 	ld	hl, #0x00a0
   0173 E5            [11]  117 	push	hl
   0174 21 35 C3      [10]  118 	ld	hl, #0xc335
   0177 E5            [11]  119 	push	hl
   0178 CD 35 02      [17]  120 	call	_cpct_drawSolidBox
                            121 ;src/main.c:50: cpct_drawSolidBox((u8*)0xC345, 0x0A, 10, 20); // 0x0A = cpct_px2byteM1(2, 0, 2, 0)
   017B 21 0A 14      [10]  122 	ld	hl, #0x140a
   017E E5            [11]  123 	push	hl
   017F 26 00         [ 7]  124 	ld	h, #0x00
   0181 E5            [11]  125 	push	hl
   0182 21 45 C3      [10]  126 	ld	hl, #0xc345
   0185 E5            [11]  127 	push	hl
   0186 CD 35 02      [17]  128 	call	_cpct_drawSolidBox
                            129 ;src/main.c:53: cpct_drawSolidBox((u8*)0xC415, 0x55, 10, 20); // 0x55 = cpct_px2byteM1(0, 3, 0, 3)
   0189 21 0A 14      [10]  130 	ld	hl, #0x140a
   018C E5            [11]  131 	push	hl
   018D 21 55 00      [10]  132 	ld	hl, #0x0055
   0190 E5            [11]  133 	push	hl
   0191 21 15 C4      [10]  134 	ld	hl, #0xc415
   0194 E5            [11]  135 	push	hl
   0195 CD 35 02      [17]  136 	call	_cpct_drawSolidBox
                            137 ;src/main.c:54: cpct_drawSolidBox((u8*)0xC425, 0x50, 10, 20); // 0x50 = cpct_px2byteM1(0, 1, 0, 1)
   0198 21 0A 14      [10]  138 	ld	hl, #0x140a
   019B E5            [11]  139 	push	hl
   019C 21 50 00      [10]  140 	ld	hl, #0x0050
   019F E5            [11]  141 	push	hl
   01A0 21 25 C4      [10]  142 	ld	hl, #0xc425
   01A3 E5            [11]  143 	push	hl
   01A4 CD 35 02      [17]  144 	call	_cpct_drawSolidBox
                            145 ;src/main.c:55: cpct_drawSolidBox((u8*)0xC435, 0x05, 10, 20); // 0x05 = cpct_px2byteM1(0, 2, 0, 2)
   01A7 21 0A 14      [10]  146 	ld	hl, #0x140a
   01AA E5            [11]  147 	push	hl
   01AB 21 05 00      [10]  148 	ld	hl, #0x0005
   01AE E5            [11]  149 	push	hl
   01AF 21 35 C4      [10]  150 	ld	hl, #0xc435
   01B2 E5            [11]  151 	push	hl
   01B3 CD 35 02      [17]  152 	call	_cpct_drawSolidBox
                            153 ;src/main.c:58: cpct_drawSolidBox((u8*)0xC505, cpct_px2byteM1(3, 3, 3, 3), 10, 20); // 0xFF 
   01B6 21 03 03      [10]  154 	ld	hl, #0x0303
   01B9 E5            [11]  155 	push	hl
   01BA 2E 03         [ 7]  156 	ld	l, #0x03
   01BC E5            [11]  157 	push	hl
   01BD CD 14 02      [17]  158 	call	_cpct_px2byteM1
   01C0 F1            [10]  159 	pop	af
   01C1 F1            [10]  160 	pop	af
   01C2 26 00         [ 7]  161 	ld	h, #0x00
   01C4 01 0A 14      [10]  162 	ld	bc, #0x140a
   01C7 C5            [11]  163 	push	bc
   01C8 E5            [11]  164 	push	hl
   01C9 21 05 C5      [10]  165 	ld	hl, #0xc505
   01CC E5            [11]  166 	push	hl
   01CD CD 35 02      [17]  167 	call	_cpct_drawSolidBox
                            168 ;src/main.c:59: cpct_drawSolidBox((u8*)0xC515, cpct_px2byteM1(2, 2, 2, 2), 10, 20); // 0xF0
   01D0 21 02 02      [10]  169 	ld	hl, #0x0202
   01D3 E5            [11]  170 	push	hl
   01D4 2E 02         [ 7]  171 	ld	l, #0x02
   01D6 E5            [11]  172 	push	hl
   01D7 CD 14 02      [17]  173 	call	_cpct_px2byteM1
   01DA F1            [10]  174 	pop	af
   01DB F1            [10]  175 	pop	af
   01DC 26 00         [ 7]  176 	ld	h, #0x00
   01DE 01 0A 14      [10]  177 	ld	bc, #0x140a
   01E1 C5            [11]  178 	push	bc
   01E2 E5            [11]  179 	push	hl
   01E3 21 15 C5      [10]  180 	ld	hl, #0xc515
   01E6 E5            [11]  181 	push	hl
   01E7 CD 35 02      [17]  182 	call	_cpct_drawSolidBox
                            183 ;src/main.c:60: cpct_drawSolidBox((u8*)0xC525, cpct_px2byteM1(1, 1, 1, 1), 10, 20); // 0x0F
   01EA 21 01 01      [10]  184 	ld	hl, #0x0101
   01ED E5            [11]  185 	push	hl
   01EE 2E 01         [ 7]  186 	ld	l, #0x01
   01F0 E5            [11]  187 	push	hl
   01F1 CD 14 02      [17]  188 	call	_cpct_px2byteM1
   01F4 F1            [10]  189 	pop	af
   01F5 F1            [10]  190 	pop	af
   01F6 26 00         [ 7]  191 	ld	h, #0x00
   01F8 01 0A 14      [10]  192 	ld	bc, #0x140a
   01FB C5            [11]  193 	push	bc
   01FC E5            [11]  194 	push	hl
   01FD 21 25 C5      [10]  195 	ld	hl, #0xc525
   0200 E5            [11]  196 	push	hl
   0201 CD 35 02      [17]  197 	call	_cpct_drawSolidBox
                            198 ;src/main.c:63: while (1);
   0204                     199 00102$:
   0204 18 FE         [12]  200 	jr	00102$
                            201 	.area _CODE
                            202 	.area _INITIALIZER
                            203 	.area _CABS (ABS)
