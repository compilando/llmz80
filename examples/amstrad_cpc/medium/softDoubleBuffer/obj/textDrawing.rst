                              1 ;--------------------------------------------------------
                              2 ; File Created by SDCC : free open source ANSI-C Compiler
                              3 ; Version 3.6.8 #9946 (Linux)
                              4 ;--------------------------------------------------------
                              5 	.module textDrawing
                              6 	.optsdcc -mz80
                              7 	
                              8 ;--------------------------------------------------------
                              9 ; Public variables in this module
                             10 ;--------------------------------------------------------
                             11 	.globl _DrawSelectionToBuffer
                             12 	.globl _DrawInfoTextToBuffer
                             13 	.globl _cpct_getScreenPtr
                             14 	.globl _cpct_drawStringM1
                             15 	.globl _cpct_setDrawCharM1
                             16 	.globl _cpct_drawSolidBox
                             17 	.globl _DrawInfoText
                             18 	.globl _DrawTextSelectionSign
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
                             50 ;src/textDrawing.c:31: void DrawInfoTextToBuffer(u8* bufferPtr) {
                             51 ;	---------------------------------
                             52 ; Function DrawInfoTextToBuffer
                             53 ; ---------------------------------
   4882                      54 _DrawInfoTextToBuffer::
   4882 DD E5         [15]   55 	push	ix
   4884 DD 21 00 00   [14]   56 	ld	ix,#0
   4888 DD 39         [15]   57 	add	ix,sp
   488A F5            [11]   58 	push	af
   488B 3B            [ 6]   59 	dec	sp
                             60 ;src/textDrawing.c:53: for (i = 0; i < NB_MESSAGES; ++i) {
   488C DD 36 FF 00   [19]   61 	ld	-1 (ix), #0x00
   4890                      62 00102$:
                             63 ;src/textDrawing.c:55: TTextData const* t = messages + i;
   4890 DD 4E FF      [19]   64 	ld	c,-1 (ix)
   4893 06 00         [ 7]   65 	ld	b,#0x00
   4895 69            [ 4]   66 	ld	l, c
   4896 60            [ 4]   67 	ld	h, b
   4897 29            [11]   68 	add	hl, hl
   4898 09            [11]   69 	add	hl, bc
   4899 29            [11]   70 	add	hl, hl
   489A 11 EA 48      [10]   71 	ld	de, #_DrawInfoTextToBuffer_messages_1_135
   489D 19            [11]   72 	add	hl, de
                             73 ;src/textDrawing.c:59: u8* pvmem = cpct_getScreenPtr(bufferPtr, t->x, t->y);
   489E 4D            [ 4]   74 	ld	c,l
   489F 44            [ 4]   75 	ld	b,h
   48A0 23            [ 6]   76 	inc	hl
   48A1 5E            [ 7]   77 	ld	e, (hl)
   48A2 0A            [ 7]   78 	ld	a, (bc)
   48A3 67            [ 4]   79 	ld	h, a
   48A4 DD 6E 04      [19]   80 	ld	l, 4 (ix)
   48A7 DD 56 05      [19]   81 	ld	d, 5 (ix)
   48AA C5            [11]   82 	push	bc
   48AB 7B            [ 4]   83 	ld	a, e
   48AC F5            [11]   84 	push	af
   48AD 33            [ 6]   85 	inc	sp
   48AE E5            [11]   86 	push	hl
   48AF 33            [ 6]   87 	inc	sp
   48B0 62            [ 4]   88 	ld	h, d
   48B1 E5            [11]   89 	push	hl
   48B2 CD 3C 4E      [17]   90 	call	_cpct_getScreenPtr
   48B5 C1            [10]   91 	pop	bc
   48B6 33            [ 6]   92 	inc	sp
   48B7 33            [ 6]   93 	inc	sp
   48B8 E5            [11]   94 	push	hl
                             95 ;src/textDrawing.c:60: cpct_setDrawCharM1(t->pen, t->paper);
   48B9 69            [ 4]   96 	ld	l, c
   48BA 60            [ 4]   97 	ld	h, b
   48BB 23            [ 6]   98 	inc	hl
   48BC 23            [ 6]   99 	inc	hl
   48BD 23            [ 6]  100 	inc	hl
   48BE 56            [ 7]  101 	ld	d, (hl)
   48BF 69            [ 4]  102 	ld	l, c
   48C0 60            [ 4]  103 	ld	h, b
   48C1 23            [ 6]  104 	inc	hl
   48C2 23            [ 6]  105 	inc	hl
   48C3 7E            [ 7]  106 	ld	a, (hl)
   48C4 C5            [11]  107 	push	bc
   48C5 5F            [ 4]  108 	ld	e, a
   48C6 D5            [11]  109 	push	de
   48C7 CD E8 4D      [17]  110 	call	_cpct_setDrawCharM1
   48CA C1            [10]  111 	pop	bc
                            112 ;src/textDrawing.c:61: cpct_drawStringM1(t->text, pvmem);
   48CB D1            [10]  113 	pop	de
   48CC D5            [11]  114 	push	de
   48CD 69            [ 4]  115 	ld	l, c
   48CE 60            [ 4]  116 	ld	h, b
   48CF 01 04 00      [10]  117 	ld	bc, #0x0004
   48D2 09            [11]  118 	add	hl, bc
   48D3 4E            [ 7]  119 	ld	c, (hl)
   48D4 23            [ 6]  120 	inc	hl
   48D5 46            [ 7]  121 	ld	b, (hl)
   48D6 D5            [11]  122 	push	de
   48D7 C5            [11]  123 	push	bc
   48D8 CD 42 4B      [17]  124 	call	_cpct_drawStringM1
                            125 ;src/textDrawing.c:53: for (i = 0; i < NB_MESSAGES; ++i) {
   48DB DD 34 FF      [23]  126 	inc	-1 (ix)
   48DE DD 7E FF      [19]  127 	ld	a, -1 (ix)
   48E1 D6 0A         [ 7]  128 	sub	a, #0x0a
   48E3 38 AB         [12]  129 	jr	C,00102$
   48E5 DD F9         [10]  130 	ld	sp, ix
   48E7 DD E1         [14]  131 	pop	ix
   48E9 C9            [10]  132 	ret
   48EA                     133 _DrawInfoTextToBuffer_messages_1_135:
   48EA 00                  134 	.db #0x00	; 0
   48EB 4B                  135 	.db #0x4b	; 75	'K'
   48EC 03                  136 	.db #0x03	; 3
   48ED 00                  137 	.db #0x00	; 0
   48EE 26 49               138 	.dw ___str_0
   48F0 04                  139 	.db #0x04	; 4
   48F1 5F                  140 	.db #0x5f	; 95
   48F2 01                  141 	.db #0x01	; 1
   48F3 00                  142 	.db #0x00	; 0
   48F4 2C 49               143 	.dw ___str_1
   48F6 08                  144 	.db #0x08	; 8
   48F7 5F                  145 	.db #0x5f	; 95
   48F8 02                  146 	.db #0x02	; 2
   48F9 00                  147 	.db #0x00	; 0
   48FA 2E 49               148 	.dw ___str_2
   48FC 08                  149 	.db #0x08	; 8
   48FD 69                  150 	.db #0x69	; 105	'i'
   48FE 01                  151 	.db #0x01	; 1
   48FF 00                  152 	.db #0x00	; 0
   4900 41 49               153 	.dw ___str_3
   4902 04                  154 	.db #0x04	; 4
   4903 78                  155 	.db #0x78	; 120	'x'
   4904 01                  156 	.db #0x01	; 1
   4905 00                  157 	.db #0x00	; 0
   4906 5C 49               158 	.dw ___str_4
   4908 08                  159 	.db #0x08	; 8
   4909 78                  160 	.db #0x78	; 120	'x'
   490A 02                  161 	.db #0x02	; 2
   490B 00                  162 	.db #0x00	; 0
   490C 5E 49               163 	.dw ___str_5
   490E 08                  164 	.db #0x08	; 8
   490F 82                  165 	.db #0x82	; 130
   4910 01                  166 	.db #0x01	; 1
   4911 00                  167 	.db #0x00	; 0
   4912 77 49               168 	.dw ___str_6
   4914 04                  169 	.db #0x04	; 4
   4915 9B                  170 	.db #0x9b	; 155
   4916 01                  171 	.db #0x01	; 1
   4917 00                  172 	.db #0x00	; 0
   4918 C2 49               173 	.dw ___str_7
   491A 08                  174 	.db #0x08	; 8
   491B 9B                  175 	.db #0x9b	; 155
   491C 02                  176 	.db #0x02	; 2
   491D 00                  177 	.db #0x00	; 0
   491E C4 49               178 	.dw ___str_8
   4920 08                  179 	.db #0x08	; 8
   4921 A5                  180 	.db #0xa5	; 165
   4922 01                  181 	.db #0x01	; 1
   4923 00                  182 	.db #0x00	; 0
   4924 DD 49               183 	.dw ___str_9
   4926                     184 ___str_0:
   4926 50 72 65 73 73      185 	.ascii "Press"
   492B 00                  186 	.db 0x00
   492C                     187 ___str_1:
   492C 31                  188 	.ascii "1"
   492D 00                  189 	.db 0x00
   492E                     190 ___str_2:
   492E 3A 20 4E 6F 20 64   191 	.ascii ": No double buffer"
        6F 75 62 6C 65 20
        62 75 66 66 65 72
   4940 00                  192 	.db 0x00
   4941                     193 ___str_3:
   4941 44 69 72 65 63 74   194 	.ascii "Directly draw in video mem"
        6C 79 20 64 72 61
        77 20 69 6E 20 76
        69 64 65 6F 20 6D
        65 6D
   495B 00                  195 	.db 0x00
   495C                     196 ___str_4:
   495C 32                  197 	.ascii "2"
   495D 00                  198 	.db 0x00
   495E                     199 ___str_5:
   495E 3A 20 48 61 72 64   200 	.ascii ": Hardware double buffer"
        77 61 72 65 20 64
        6F 75 62 6C 65 20
        62 75 66 66 65 72
   4976 00                  201 	.db 0x00
   4977                     202 ___str_6:
   4977 44 72 61 77 20 61   203 	.ascii "Draw alternatively in two video mem  (2*16384 bytes) and fli"
        6C 74 65 72 6E 61
        74 69 76 65 6C 79
        20 69 6E 20 74 77
        6F 20 76 69 64 65
        6F 20 6D 65 6D 20
        20 28 32 2A 31 36
        33 38 34 20 62 79
        74 65 73 29 20 61
        6E 64 20 66 6C 69
   49B3 70 20 62 65 74 77   204 	.ascii "p between them"
        65 65 6E 20 74 68
        65 6D
   49C1 00                  205 	.db 0x00
   49C2                     206 ___str_7:
   49C2 33                  207 	.ascii "3"
   49C3 00                  208 	.db 0x00
   49C4                     209 ___str_8:
   49C4 3A 20 53 6F 66 74   210 	.ascii ": Software double buffer"
        77 61 72 65 20 64
        6F 75 62 6C 65 20
        62 75 66 66 65 72
   49DC 00                  211 	.db 0x00
   49DD                     212 ___str_9:
   49DD 44 72 61 77 20 69   213 	.ascii "Draw in buffer (50*60 bytes) of size view and copy whole buf"
        6E 20 62 75 66 66
        65 72 20 28 35 30
        2A 36 30 20 62 79
        74 65 73 29 20 6F
        66 20 73 69 7A 65
        20 76 69 65 77 20
        61 6E 64 20 63 6F
        70 79 20 77 68 6F
        6C 65 20 62 75 66
   4A19 66 65 72 20 74 6F   214 	.ascii "fer to video mem (16384 bytes)"
        20 76 69 64 65 6F
        20 6D 65 6D 20 28
        31 36 33 38 34 20
        62 79 74 65 73 29
   4A37 00                  215 	.db 0x00
                            216 ;src/textDrawing.c:70: void DrawInfoText() {
                            217 ;	---------------------------------
                            218 ; Function DrawInfoText
                            219 ; ---------------------------------
   4A38                     220 _DrawInfoText::
                            221 ;src/textDrawing.c:71: DrawInfoTextToBuffer((u8*)CPCT_VMEM_START);
   4A38 21 00 C0      [10]  222 	ld	hl, #0xc000
   4A3B E5            [11]  223 	push	hl
   4A3C CD 82 48      [17]  224 	call	_DrawInfoTextToBuffer
                            225 ;src/textDrawing.c:72: DrawInfoTextToBuffer((u8*)SCREEN_BUFF);
   4A3F 21 00 80      [10]  226 	ld	hl, #0x8000
   4A42 E3            [19]  227 	ex	(sp),hl
   4A43 CD 82 48      [17]  228 	call	_DrawInfoTextToBuffer
   4A46 F1            [10]  229 	pop	af
   4A47 C9            [10]  230 	ret
                            231 ;src/textDrawing.c:82: void DrawSelectionToBuffer(u8* bufferPtr, u8 pos) {
                            232 ;	---------------------------------
                            233 ; Function DrawSelectionToBuffer
                            234 ; ---------------------------------
   4A48                     235 _DrawSelectionToBuffer::
   4A48 DD E5         [15]  236 	push	ix
   4A4A DD 21 00 00   [14]  237 	ld	ix,#0
   4A4E DD 39         [15]  238 	add	ix,sp
                            239 ;src/textDrawing.c:87: pvmem = cpct_getScreenPtr(bufferPtr, 0, POS_TEXT + 15);
   4A50 DD 4E 04      [19]  240 	ld	c,4 (ix)
   4A53 DD 46 05      [19]  241 	ld	b,5 (ix)
   4A56 C5            [11]  242 	push	bc
   4A57 21 00 5F      [10]  243 	ld	hl, #0x5f00
   4A5A E5            [11]  244 	push	hl
   4A5B C5            [11]  245 	push	bc
   4A5C CD 3C 4E      [17]  246 	call	_cpct_getScreenPtr
   4A5F 11 02 50      [10]  247 	ld	de, #0x5002
   4A62 D5            [11]  248 	push	de
   4A63 11 00 00      [10]  249 	ld	de, #0x0000
   4A66 D5            [11]  250 	push	de
   4A67 E5            [11]  251 	push	hl
   4A68 CD 27 4D      [17]  252 	call	_cpct_drawSolidBox
   4A6B C1            [10]  253 	pop	bc
                            254 ;src/textDrawing.c:91: pvmem = cpct_getScreenPtr(bufferPtr, 0, pos);
   4A6C DD 7E 06      [19]  255 	ld	a, 6 (ix)
   4A6F F5            [11]  256 	push	af
   4A70 33            [ 6]  257 	inc	sp
   4A71 AF            [ 4]  258 	xor	a, a
   4A72 F5            [11]  259 	push	af
   4A73 33            [ 6]  260 	inc	sp
   4A74 C5            [11]  261 	push	bc
   4A75 CD 3C 4E      [17]  262 	call	_cpct_getScreenPtr
                            263 ;src/textDrawing.c:92: cpct_setDrawCharM1(3, 0);
   4A78 E5            [11]  264 	push	hl
   4A79 01 03 00      [10]  265 	ld	bc, #0x0003
   4A7C C5            [11]  266 	push	bc
   4A7D CD E8 4D      [17]  267 	call	_cpct_setDrawCharM1
   4A80 E1            [10]  268 	pop	hl
                            269 ;src/textDrawing.c:93: cpct_drawStringM1(">", pvmem);
   4A81 01 8C 4A      [10]  270 	ld	bc, #___str_10+0
   4A84 E5            [11]  271 	push	hl
   4A85 C5            [11]  272 	push	bc
   4A86 CD 42 4B      [17]  273 	call	_cpct_drawStringM1
   4A89 DD E1         [14]  274 	pop	ix
   4A8B C9            [10]  275 	ret
   4A8C                     276 ___str_10:
   4A8C 3E                  277 	.ascii ">"
   4A8D 00                  278 	.db 0x00
                            279 ;src/textDrawing.c:102: void DrawTextSelectionSign(u8 sel) {
                            280 ;	---------------------------------
                            281 ; Function DrawTextSelectionSign
                            282 ; ---------------------------------
   4A8E                     283 _DrawTextSelectionSign::
                            284 ;src/textDrawing.c:110: u8 pos = locations[sel-1];   // Position of the User selection
   4A8E 21 02 00      [10]  285 	ld	hl, #2+0
   4A91 39            [11]  286 	add	hl, sp
   4A92 4E            [ 7]  287 	ld	c, (hl)
   4A93 0D            [ 4]  288 	dec	c
   4A94 21 B2 4A      [10]  289 	ld	hl, #_DrawTextSelectionSign_locations_1_142
   4A97 06 00         [ 7]  290 	ld	b, #0x00
   4A99 09            [11]  291 	add	hl, bc
   4A9A 46            [ 7]  292 	ld	b, (hl)
                            293 ;src/textDrawing.c:113: DrawSelectionToBuffer((u8*)CPCT_VMEM_START, pos);
   4A9B C5            [11]  294 	push	bc
   4A9C C5            [11]  295 	push	bc
   4A9D 33            [ 6]  296 	inc	sp
   4A9E 21 00 C0      [10]  297 	ld	hl, #0xc000
   4AA1 E5            [11]  298 	push	hl
   4AA2 CD 48 4A      [17]  299 	call	_DrawSelectionToBuffer
   4AA5 F1            [10]  300 	pop	af
   4AA6 33            [ 6]  301 	inc	sp
   4AA7 33            [ 6]  302 	inc	sp
   4AA8 21 00 80      [10]  303 	ld	hl, #0x8000
   4AAB E5            [11]  304 	push	hl
   4AAC CD 48 4A      [17]  305 	call	_DrawSelectionToBuffer
   4AAF F1            [10]  306 	pop	af
   4AB0 33            [ 6]  307 	inc	sp
   4AB1 C9            [10]  308 	ret
   4AB2                     309 _DrawTextSelectionSign_locations_1_142:
   4AB2 5F                  310 	.db #0x5f	; 95
   4AB3 78                  311 	.db #0x78	; 120	'x'
   4AB4 9B                  312 	.db #0x9b	; 155
                            313 	.area _CODE
                            314 	.area _INITIALIZER
                            315 	.area _CABS (ABS)
