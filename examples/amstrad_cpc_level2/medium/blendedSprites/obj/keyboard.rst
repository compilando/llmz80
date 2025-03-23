                              1 ;--------------------------------------------------------
                              2 ; File Created by SDCC : free open source ANSI-C Compiler
                              3 ; Version 3.6.8 #9946 (Linux)
                              4 ;--------------------------------------------------------
                              5 	.module keyboard
                              6 	.optsdcc -mz80
                              7 	
                              8 ;--------------------------------------------------------
                              9 ; Public variables in this module
                             10 ;--------------------------------------------------------
                             11 	.globl _updateKeyboardStatus
                             12 	.globl _cpct_isKeyPressed
                             13 	.globl _cpct_scanKeyboard
                             14 ;--------------------------------------------------------
                             15 ; special function registers
                             16 ;--------------------------------------------------------
                             17 ;--------------------------------------------------------
                             18 ; ram data
                             19 ;--------------------------------------------------------
                             20 	.area _DATA
                             21 ;--------------------------------------------------------
                             22 ; ram data
                             23 ;--------------------------------------------------------
                             24 	.area _INITIALIZED
                             25 ;--------------------------------------------------------
                             26 ; absolute external ram data
                             27 ;--------------------------------------------------------
                             28 	.area _DABS (ABS)
                             29 ;--------------------------------------------------------
                             30 ; global & static initialisations
                             31 ;--------------------------------------------------------
                             32 	.area _HOME
                             33 	.area _GSINIT
                             34 	.area _GSFINAL
                             35 	.area _GSINIT
                             36 ;--------------------------------------------------------
                             37 ; Home
                             38 ;--------------------------------------------------------
                             39 	.area _HOME
                             40 	.area _HOME
                             41 ;--------------------------------------------------------
                             42 ; code
                             43 ;--------------------------------------------------------
                             44 	.area _CODE
                             45 ;src/keyboard.c:27: void updateKeyboardStatus() {
                             46 ;	---------------------------------
                             47 ; Function updateKeyboardStatus
                             48 ; ---------------------------------
   6B1F                      49 _updateKeyboardStatus::
   6B1F DD E5         [15]   50 	push	ix
   6B21 DD 21 00 00   [14]   51 	ld	ix,#0
   6B25 DD 39         [15]   52 	add	ix,sp
   6B27 F5            [11]   53 	push	af
   6B28 3B            [ 6]   54 	dec	sp
                             55 ;src/keyboard.c:32: cpct_scanKeyboard();
   6B29 CD A9 6E      [17]   56 	call	_cpct_scanKeyboard
                             57 ;src/keyboard.c:39: k = g_keys;
   6B2C 01 0B 6B      [10]   58 	ld	bc, #_g_keys+0
                             59 ;src/keyboard.c:40: for(i=0; i < G_NKEYS; i++, k++) {
   6B2F DD 36 FD 00   [19]   60 	ld	-3 (ix), #0x00
   6B33                      61 00113$:
                             62 ;src/keyboard.c:42: if (cpct_isKeyPressed(k->key)) {
   6B33 69            [ 4]   63 	ld	l, c
   6B34 60            [ 4]   64 	ld	h, b
   6B35 5E            [ 7]   65 	ld	e, (hl)
   6B36 23            [ 6]   66 	inc	hl
   6B37 66            [ 7]   67 	ld	h, (hl)
   6B38 C5            [11]   68 	push	bc
   6B39 6B            [ 4]   69 	ld	l, e
   6B3A CD 51 6C      [17]   70 	call	_cpct_isKeyPressed
   6B3D DD 75 FF      [19]   71 	ld	-1 (ix), l
   6B40 C1            [10]   72 	pop	bc
                             73 ;src/keyboard.c:45: switch(k->status) {
   6B41 59            [ 4]   74 	ld	e, c
   6B42 50            [ 4]   75 	ld	d, b
   6B43 13            [ 6]   76 	inc	de
   6B44 13            [ 6]   77 	inc	de
   6B45 1A            [ 7]   78 	ld	a, (de)
   6B46 6F            [ 4]   79 	ld	l,a
   6B47 3D            [ 4]   80 	dec	a
   6B48 20 04         [12]   81 	jr	NZ,00150$
   6B4A 3E 01         [ 7]   82 	ld	a,#0x01
   6B4C 18 01         [12]   83 	jr	00151$
   6B4E                      84 00150$:
   6B4E AF            [ 4]   85 	xor	a,a
   6B4F                      86 00151$:
   6B4F 67            [ 4]   87 	ld	h, a
   6B50 7D            [ 4]   88 	ld	a, l
   6B51 D6 03         [ 7]   89 	sub	a, #0x03
   6B53 20 04         [12]   90 	jr	NZ,00152$
   6B55 3E 01         [ 7]   91 	ld	a,#0x01
   6B57 18 01         [12]   92 	jr	00153$
   6B59                      93 00152$:
   6B59 AF            [ 4]   94 	xor	a,a
   6B5A                      95 00153$:
   6B5A DD 77 FE      [19]   96 	ld	-2 (ix), a
                             97 ;src/keyboard.c:42: if (cpct_isKeyPressed(k->key)) {
   6B5D DD 7E FF      [19]   98 	ld	a, -1 (ix)
   6B60 B7            [ 4]   99 	or	a, a
   6B61 28 1A         [12]  100 	jr	Z,00110$
                            101 ;src/keyboard.c:45: switch(k->status) {
   6B63 7D            [ 4]  102 	ld	a, l
   6B64 B7            [ 4]  103 	or	a, a
   6B65 28 11         [12]  104 	jr	Z,00103$
   6B67 7C            [ 4]  105 	ld	a, h
   6B68 B7            [ 4]  106 	or	a, a
   6B69 20 08         [12]  107 	jr	NZ,00101$
   6B6B DD 7E FE      [19]  108 	ld	a, -2 (ix)
   6B6E B7            [ 4]  109 	or	a, a
   6B6F 20 07         [12]  110 	jr	NZ,00103$
   6B71 18 22         [12]  111 	jr	00114$
                            112 ;src/keyboard.c:47: case KeySt_Pressed:  { k->status = KeySt_StillPressed; break; }
   6B73                     113 00101$:
   6B73 3E 02         [ 7]  114 	ld	a, #0x02
   6B75 12            [ 7]  115 	ld	(de), a
   6B76 18 1D         [12]  116 	jr	00114$
                            117 ;src/keyboard.c:50: case KeySt_Released: { k->status = KeySt_Pressed; }
   6B78                     118 00103$:
   6B78 3E 01         [ 7]  119 	ld	a, #0x01
   6B7A 12            [ 7]  120 	ld	(de), a
                            121 ;src/keyboard.c:51: }
   6B7B 18 18         [12]  122 	jr	00114$
   6B7D                     123 00110$:
                            124 ;src/keyboard.c:55: switch(k->status) {
   6B7D 7C            [ 4]  125 	ld	a, h
   6B7E B7            [ 4]  126 	or	a, a
   6B7F 20 0D         [12]  127 	jr	NZ,00106$
   6B81 7D            [ 4]  128 	ld	a, l
   6B82 D6 02         [ 7]  129 	sub	a, #0x02
   6B84 28 08         [12]  130 	jr	Z,00106$
   6B86 DD 7E FE      [19]  131 	ld	a, -2 (ix)
   6B89 B7            [ 4]  132 	or	a, a
   6B8A 20 07         [12]  133 	jr	NZ,00107$
   6B8C 18 07         [12]  134 	jr	00114$
                            135 ;src/keyboard.c:58: case KeySt_StillPressed: { k->status = KeySt_Released; break; }
   6B8E                     136 00106$:
   6B8E 3E 03         [ 7]  137 	ld	a, #0x03
   6B90 12            [ 7]  138 	ld	(de), a
   6B91 18 02         [12]  139 	jr	00114$
                            140 ;src/keyboard.c:60: case KeySt_Released:     { k->status = KeySt_Free; }
   6B93                     141 00107$:
   6B93 AF            [ 4]  142 	xor	a, a
   6B94 12            [ 7]  143 	ld	(de), a
                            144 ;src/keyboard.c:61: }         
   6B95                     145 00114$:
                            146 ;src/keyboard.c:40: for(i=0; i < G_NKEYS; i++, k++) {
   6B95 DD 34 FD      [23]  147 	inc	-3 (ix)
   6B98 03            [ 6]  148 	inc	bc
   6B99 03            [ 6]  149 	inc	bc
   6B9A 03            [ 6]  150 	inc	bc
   6B9B 03            [ 6]  151 	inc	bc
   6B9C 03            [ 6]  152 	inc	bc
   6B9D DD 7E FD      [19]  153 	ld	a, -3 (ix)
   6BA0 D6 04         [ 7]  154 	sub	a, #0x04
   6BA2 38 8F         [12]  155 	jr	C,00113$
   6BA4 DD F9         [10]  156 	ld	sp, ix
   6BA6 DD E1         [14]  157 	pop	ix
   6BA8 C9            [10]  158 	ret
                            159 	.area _CODE
                            160 	.area _INITIALIZER
                            161 	.area _CABS (ABS)
