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
                             12 	.globl _scrollLine
                             13 	.globl _wait_n_VSYNCs
                             14 	.globl _strlen
                             15 	.globl _cpct_waitVSYNC
                             16 	.globl _cpct_drawStringM1
                             17 	.globl _cpct_drawCharM1
                             18 	.globl _cpct_setDrawCharM1
                             19 	.globl _cpct_isAnyKeyPressed_f
                             20 	.globl _cpct_scanKeyboard_f
                             21 	.globl _cpct_memcpy
                             22 ;--------------------------------------------------------
                             23 ; special function registers
                             24 ;--------------------------------------------------------
                             25 ;--------------------------------------------------------
                             26 ; ram data
                             27 ;--------------------------------------------------------
                             28 	.area _DATA
                             29 ;--------------------------------------------------------
                             30 ; ram data
                             31 ;--------------------------------------------------------
                             32 	.area _INITIALIZED
                             33 ;--------------------------------------------------------
                             34 ; absolute external ram data
                             35 ;--------------------------------------------------------
                             36 	.area _DABS (ABS)
                             37 ;--------------------------------------------------------
                             38 ; global & static initialisations
                             39 ;--------------------------------------------------------
                             40 	.area _HOME
                             41 	.area _GSINIT
                             42 	.area _GSFINAL
                             43 	.area _GSINIT
                             44 ;--------------------------------------------------------
                             45 ; Home
                             46 ;--------------------------------------------------------
                             47 	.area _HOME
                             48 	.area _HOME
                             49 ;--------------------------------------------------------
                             50 ; code
                             51 ;--------------------------------------------------------
                             52 	.area _CODE
                             53 ;src/main.c:37: void wait_n_VSYNCs(u8 n) {
                             54 ;	---------------------------------
                             55 ; Function wait_n_VSYNCs
                             56 ; ---------------------------------
   4000                      57 _wait_n_VSYNCs::
                             58 ;src/main.c:38: do {
   4000 21 02 00      [10]   59 	ld	hl, #2+0
   4003 39            [11]   60 	add	hl, sp
   4004 4E            [ 7]   61 	ld	c, (hl)
   4005                      62 00103$:
                             63 ;src/main.c:40: cpct_waitVSYNC();
   4005 C5            [11]   64 	push	bc
   4006 CD 8B 42      [17]   65 	call	_cpct_waitVSYNC
   4009 C1            [10]   66 	pop	bc
                             67 ;src/main.c:45: if (--n) {
   400A 0D            [ 4]   68 	dec	c
   400B 79            [ 4]   69 	ld	a, c
   400C B7            [ 4]   70 	or	a, a
   400D 28 02         [12]   71 	jr	Z,00104$
                             72 ;src/main.c:46: __asm__("halt");
   400F 76            [ 4]   73 	halt
                             74 ;src/main.c:47: __asm__("halt");
   4010 76            [ 4]   75 	halt
   4011                      76 00104$:
                             77 ;src/main.c:49: } while(n);
   4011 79            [ 4]   78 	ld	a, c
   4012 B7            [ 4]   79 	or	a, a
   4013 20 F0         [12]   80 	jr	NZ,00103$
   4015 C9            [10]   81 	ret
                             82 ;src/main.c:58: void scrollLine(u8* pCharline, u16 lineSize) {
                             83 ;	---------------------------------
                             84 ; Function scrollLine
                             85 ; ---------------------------------
   4016                      86 _scrollLine::
   4016 DD E5         [15]   87 	push	ix
   4018 DD 21 00 00   [14]   88 	ld	ix,#0
   401C DD 39         [15]   89 	add	ix,sp
   401E DD 6E 04      [19]   90 	ld	l,4 (ix)
   4021 DD 66 05      [19]   91 	ld	h,5 (ix)
   4024                      92 00103$:
                             93 ;src/main.c:62: for (; pCharline > CPCT_VMEM_START; pCharline += PIXEL_LINE_OFFSET)
   4024 AF            [ 4]   94 	xor	a, a
   4025 BD            [ 4]   95 	cp	a, l
   4026 3E C0         [ 7]   96 	ld	a, #0xc0
   4028 9C            [ 4]   97 	sbc	a, h
   4029 30 1B         [12]   98 	jr	NC,00105$
                             99 ;src/main.c:63: cpct_memcpy(pCharline, pCharline+1, lineSize);
   402B 4D            [ 4]  100 	ld	c, l
   402C 44            [ 4]  101 	ld	b, h
   402D 03            [ 6]  102 	inc	bc
   402E E5            [11]  103 	push	hl
   402F FD E1         [14]  104 	pop	iy
   4031 E5            [11]  105 	push	hl
   4032 DD 5E 06      [19]  106 	ld	e,6 (ix)
   4035 DD 56 07      [19]  107 	ld	d,7 (ix)
   4038 D5            [11]  108 	push	de
   4039 C5            [11]  109 	push	bc
   403A FD E5         [15]  110 	push	iy
   403C CD AE 42      [17]  111 	call	_cpct_memcpy
   403F E1            [10]  112 	pop	hl
                            113 ;src/main.c:62: for (; pCharline > CPCT_VMEM_START; pCharline += PIXEL_LINE_OFFSET)
   4040 01 00 08      [10]  114 	ld	bc, #0x0800
   4043 09            [11]  115 	add	hl, bc
   4044 18 DE         [12]  116 	jr	00103$
   4046                     117 00105$:
   4046 DD E1         [14]  118 	pop	ix
   4048 C9            [10]  119 	ret
                            120 ;src/main.c:69: void main(void) {
                            121 ;	---------------------------------
                            122 ; Function main
                            123 ; ---------------------------------
   4049                     124 _main::
   4049 DD E5         [15]  125 	push	ix
   404B DD 21 00 00   [14]  126 	ld	ix,#0
   404F DD 39         [15]  127 	add	ix,sp
   4051 F5            [11]  128 	push	af
   4052 3B            [ 6]  129 	dec	sp
                            130 ;src/main.c:72: const u8 *text="This is a simple software scrolling mode 1 text. Not really smooth, but easy to understand.     ";
   4053 01 F6 40      [10]  131 	ld	bc, #___str_0+0
                            132 ;src/main.c:78: u8* pCharline_start = CPCT_VMEM_START + (PIXEL_LINE_SIZE * CHARLINE);
   4056 21 C0 C3      [10]  133 	ld	hl, #0xc3c0
   4059 E3            [19]  134 	ex	(sp), hl
                            135 ;src/main.c:84: const u8 textlen=strlen(text);  // Save the lenght of the text for later use
   405A C5            [11]  136 	push	bc
   405B C5            [11]  137 	push	bc
   405C CD B6 42      [17]  138 	call	_strlen
   405F F1            [10]  139 	pop	af
   4060 C1            [10]  140 	pop	bc
   4061 DD 75 FF      [19]  141 	ld	-1 (ix), l
                            142 ;src/main.c:85: u8 nextChar=0;                  // Next character of the text to be drawn on the screen
                            143 ;src/main.c:86: u8 penColour=1;                 // Pen colour for the characters
   4064 11 00 01      [10]  144 	ld	de,#0x0100
                            145 ;src/main.c:89: cpct_setDrawCharM1(1, 3);
   4067 C5            [11]  146 	push	bc
   4068 D5            [11]  147 	push	de
   4069 21 01 03      [10]  148 	ld	hl, #0x0301
   406C E5            [11]  149 	push	hl
   406D CD C6 42      [17]  150 	call	_cpct_setDrawCharM1
   4070 21 00 C0      [10]  151 	ld	hl, #0xc000
   4073 E5            [11]  152 	push	hl
   4074 21 57 41      [10]  153 	ld	hl, #___str_1
   4077 E5            [11]  154 	push	hl
   4078 CD DE 41      [17]  155 	call	_cpct_drawStringM1
   407B 21 01 00      [10]  156 	ld	hl, #0x0001
   407E E5            [11]  157 	push	hl
   407F CD C6 42      [17]  158 	call	_cpct_setDrawCharM1
   4082 D1            [10]  159 	pop	de
   4083 C1            [10]  160 	pop	bc
                            161 ;src/main.c:95: do { cpct_scanKeyboard_f(); } while( cpct_isAnyKeyPressed_f() );
   4084                     162 00101$:
   4084 C5            [11]  163 	push	bc
   4085 D5            [11]  164 	push	de
   4086 CD 74 41      [17]  165 	call	_cpct_scanKeyboard_f
   4089 CD 93 42      [17]  166 	call	_cpct_isAnyKeyPressed_f
   408C D1            [10]  167 	pop	de
   408D C1            [10]  168 	pop	bc
   408E 7D            [ 4]  169 	ld	a, l
   408F B7            [ 4]  170 	or	a, a
   4090 20 F2         [12]  171 	jr	NZ,00101$
                            172 ;src/main.c:99: cpct_drawCharM1(pNextCharLocation, text[nextChar]);
   4092 6B            [ 4]  173 	ld	l,e
   4093 26 00         [ 7]  174 	ld	h,#0x00
   4095 09            [11]  175 	add	hl, bc
   4096 6E            [ 7]  176 	ld	l, (hl)
   4097 26 00         [ 7]  177 	ld	h, #0x00
   4099 C5            [11]  178 	push	bc
   409A D5            [11]  179 	push	de
   409B E5            [11]  180 	push	hl
   409C 21 0E C4      [10]  181 	ld	hl, #0xc40e
   409F E5            [11]  182 	push	hl
   40A0 CD 5E 42      [17]  183 	call	_cpct_drawCharM1
   40A3 D1            [10]  184 	pop	de
   40A4 C1            [10]  185 	pop	bc
                            186 ;src/main.c:104: if (++nextChar == textlen) {
   40A5 1C            [ 4]  187 	inc	e
   40A6 DD 7E FF      [19]  188 	ld	a, -1 (ix)
                            189 ;src/main.c:105: nextChar = 0;
   40A9 93            [ 4]  190 	sub	a,e
   40AA 20 15         [12]  191 	jr	NZ,00107$
   40AC 5F            [ 4]  192 	ld	e,a
                            193 ;src/main.c:106: if (++penColour > 3) penColour = 1;
   40AD 14            [ 4]  194 	inc	d
   40AE 3E 03         [ 7]  195 	ld	a, #0x03
   40B0 92            [ 4]  196 	sub	a, d
   40B1 30 02         [12]  197 	jr	NC,00105$
   40B3 16 01         [ 7]  198 	ld	d, #0x01
   40B5                     199 00105$:
                            200 ;src/main.c:107: cpct_setDrawCharM1(penColour, 0);
   40B5 C5            [11]  201 	push	bc
   40B6 D5            [11]  202 	push	de
   40B7 AF            [ 4]  203 	xor	a, a
   40B8 F5            [11]  204 	push	af
   40B9 33            [ 6]  205 	inc	sp
   40BA D5            [11]  206 	push	de
   40BB 33            [ 6]  207 	inc	sp
   40BC CD C6 42      [17]  208 	call	_cpct_setDrawCharM1
   40BF D1            [10]  209 	pop	de
   40C0 C1            [10]  210 	pop	bc
   40C1                     211 00107$:
                            212 ;src/main.c:113: wait_n_VSYNCs(2);
   40C1 C5            [11]  213 	push	bc
   40C2 D5            [11]  214 	push	de
   40C3 3E 02         [ 7]  215 	ld	a, #0x02
   40C5 F5            [11]  216 	push	af
   40C6 33            [ 6]  217 	inc	sp
   40C7 CD 00 40      [17]  218 	call	_wait_n_VSYNCs
   40CA 33            [ 6]  219 	inc	sp
   40CB 21 50 00      [10]  220 	ld	hl, #0x0050
   40CE E5            [11]  221 	push	hl
   40CF DD 6E FD      [19]  222 	ld	l,-3 (ix)
   40D2 DD 66 FE      [19]  223 	ld	h,-2 (ix)
   40D5 E5            [11]  224 	push	hl
   40D6 CD 16 40      [17]  225 	call	_scrollLine
   40D9 F1            [10]  226 	pop	af
   40DA 26 02         [ 7]  227 	ld	h,#0x02
   40DC E3            [19]  228 	ex	(sp),hl
   40DD 33            [ 6]  229 	inc	sp
   40DE CD 00 40      [17]  230 	call	_wait_n_VSYNCs
   40E1 33            [ 6]  231 	inc	sp
   40E2 21 50 00      [10]  232 	ld	hl, #0x0050
   40E5 E5            [11]  233 	push	hl
   40E6 DD 6E FD      [19]  234 	ld	l,-3 (ix)
   40E9 DD 66 FE      [19]  235 	ld	h,-2 (ix)
   40EC E5            [11]  236 	push	hl
   40ED CD 16 40      [17]  237 	call	_scrollLine
   40F0 F1            [10]  238 	pop	af
   40F1 F1            [10]  239 	pop	af
   40F2 D1            [10]  240 	pop	de
   40F3 C1            [10]  241 	pop	bc
   40F4 18 8E         [12]  242 	jr	00101$
   40F6                     243 ___str_0:
   40F6 54 68 69 73 20 69   244 	.ascii "This is a simple software scrolling mode 1 text. Not really "
        73 20 61 20 73 69
        6D 70 6C 65 20 73
        6F 66 74 77 61 72
        65 20 73 63 72 6F
        6C 6C 69 6E 67 20
        6D 6F 64 65 20 31
        20 74 65 78 74 2E
        20 4E 6F 74 20 72
        65 61 6C 6C 79 20
   4132 73 6D 6F 6F 74 68   245 	.ascii "smooth, but easy to understand.     "
        2C 20 62 75 74 20
        65 61 73 79 20 74
        6F 20 75 6E 64 65
        72 73 74 61 6E 64
        2E 20 20 20 20 20
   4156 00                  246 	.db 0x00
   4157                     247 ___str_1:
   4157 48 6F 6C 64 20 61   248 	.ascii "Hold any key to pause scroll"
        6E 79 20 6B 65 79
        20 74 6F 20 70 61
        75 73 65 20 73 63
        72 6F 6C 6C
   4173 00                  249 	.db 0x00
                            250 	.area _CODE
                            251 	.area _INITIALIZER
                            252 	.area _CABS (ABS)
