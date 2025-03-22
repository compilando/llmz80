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
                             12 	.globl _initialize
                             13 	.globl _cpct_getScreenPtr
                             14 	.globl _cpct_setPALColour
                             15 	.globl _cpct_waitVSYNC
                             16 	.globl _cpct_setVideoMode
                             17 	.globl _cpct_drawStringM2
                             18 	.globl _cpct_setDrawCharM2
                             19 	.globl _cpct_drawSprite
                             20 	.globl _cpct_drawSolidBox
                             21 	.globl _cpct_hflipSpriteM2
                             22 	.globl _cpct_isAnyKeyPressed
                             23 	.globl _cpct_scanKeyboard_f
                             24 	.globl _cpct_disableFirmware
                             25 	.globl _g_animation
                             26 ;--------------------------------------------------------
                             27 ; special function registers
                             28 ;--------------------------------------------------------
                             29 ;--------------------------------------------------------
                             30 ; ram data
                             31 ;--------------------------------------------------------
                             32 	.area _DATA
                             33 ;--------------------------------------------------------
                             34 ; ram data
                             35 ;--------------------------------------------------------
                             36 	.area _INITIALIZED
                             37 ;--------------------------------------------------------
                             38 ; absolute external ram data
                             39 ;--------------------------------------------------------
                             40 	.area _DABS (ABS)
                             41 ;--------------------------------------------------------
                             42 ; global & static initialisations
                             43 ;--------------------------------------------------------
                             44 	.area _HOME
                             45 	.area _GSINIT
                             46 	.area _GSFINAL
                             47 	.area _GSINIT
                             48 ;--------------------------------------------------------
                             49 ; Home
                             50 ;--------------------------------------------------------
                             51 	.area _HOME
                             52 	.area _HOME
                             53 ;--------------------------------------------------------
                             54 ; code
                             55 ;--------------------------------------------------------
                             56 	.area _CODE
                             57 ;src/main.c:52: void initialize() {
                             58 ;	---------------------------------
                             59 ; Function initialize
                             60 ; ---------------------------------
   6648                      61 _initialize::
                             62 ;src/main.c:56: cpct_disableFirmware();
   6648 CD 91 69      [17]   63 	call	_cpct_disableFirmware
                             64 ;src/main.c:59: cpct_setBorder(HW_BLACK);
   664B 21 10 14      [10]   65 	ld	hl, #0x1410
   664E E5            [11]   66 	push	hl
   664F CD 08 68      [17]   67 	call	_cpct_setPALColour
                             68 ;src/main.c:60: cpct_setPALColour(0, HW_BLACK);
   6652 21 00 14      [10]   69 	ld	hl, #0x1400
   6655 E5            [11]   70 	push	hl
   6656 CD 08 68      [17]   71 	call	_cpct_setPALColour
                             72 ;src/main.c:61: cpct_setPALColour(1, HW_WHITE);
   6659 21 01 00      [10]   73 	ld	hl, #0x0001
   665C E5            [11]   74 	push	hl
   665D CD 08 68      [17]   75 	call	_cpct_setPALColour
                             76 ;src/main.c:64: cpct_setVideoMode(2);
   6660 2E 02         [ 7]   77 	ld	l, #0x02
   6662 CD 2D 69      [17]   78 	call	_cpct_setVideoMode
                             79 ;src/main.c:68: cpct_drawSprite(g_banner_0, CPCT_VMEM_START             , BANNER_W/2, BANNER_H);
   6665 21 28 34      [10]   80 	ld	hl, #0x3428
   6668 E5            [11]   81 	push	hl
   6669 21 00 C0      [10]   82 	ld	hl, #0xc000
   666C E5            [11]   83 	push	hl
   666D 21 00 40      [10]   84 	ld	hl, #_g_banner_0
   6670 E5            [11]   85 	push	hl
   6671 CD 43 68      [17]   86 	call	_cpct_drawSprite
                             87 ;src/main.c:69: cpct_drawSprite(g_banner_1, CPCT_VMEM_START + BANNER_W/2, BANNER_W/2, BANNER_H);
   6674 21 28 34      [10]   88 	ld	hl, #0x3428
   6677 E5            [11]   89 	push	hl
   6678 26 C0         [ 7]   90 	ld	h, #0xc0
   667A E5            [11]   91 	push	hl
   667B 21 20 48      [10]   92 	ld	hl, #_g_banner_1
   667E E5            [11]   93 	push	hl
   667F CD 43 68      [17]   94 	call	_cpct_drawSprite
                             95 ;src/main.c:72: pvideomem = cpct_getScreenPtr(CPCT_VMEM_START, 29, 60);
   6682 21 1D 3C      [10]   96 	ld	hl, #0x3c1d
   6685 E5            [11]   97 	push	hl
   6686 21 00 C0      [10]   98 	ld	hl, #0xc000
   6689 E5            [11]   99 	push	hl
   668A CD 49 6A      [17]  100 	call	_cpct_getScreenPtr
                            101 ;src/main.c:73: cpct_setDrawCharM2(0, 1);
   668D E5            [11]  102 	push	hl
   668E 01 00 01      [10]  103 	ld	bc, #0x0100
   6691 C5            [11]  104 	push	bc
   6692 CD 5F 6A      [17]  105 	call	_cpct_setDrawCharM2
   6695 E1            [10]  106 	pop	hl
                            107 ;src/main.c:74: cpct_drawStringM2("[Any Key] Run Opposite", pvideomem);
   6696 01 AB 66      [10]  108 	ld	bc, #___str_0+0
   6699 E5            [11]  109 	push	hl
   669A C5            [11]  110 	push	bc
   669B CD 14 68      [17]  111 	call	_cpct_drawStringM2
   669E C9            [10]  112 	ret
   669F                     113 _g_animation:
   669F 40 50               114 	.dw _g_runner_0
   66A1 EC 53               115 	.dw _g_runner_1
   66A3 98 57               116 	.dw _g_runner_2
   66A5 44 5B               117 	.dw _g_runner_3
   66A7 F0 5E               118 	.dw _g_runner_4
   66A9 9C 62               119 	.dw _g_runner_5
   66AB                     120 ___str_0:
   66AB 5B 41 6E 79 20 4B   121 	.ascii "[Any Key] Run Opposite"
        65 79 5D 20 52 75
        6E 20 4F 70 70 6F
        73 69 74 65
   66C1 00                  122 	.db 0x00
                            123 ;src/main.c:80: void main(void) {
                            124 ;	---------------------------------
                            125 ; Function main
                            126 ; ---------------------------------
   66C2                     127 _main::
   66C2 DD E5         [15]  128 	push	ix
   66C4 DD 21 00 00   [14]  129 	ld	ix,#0
   66C8 DD 39         [15]  130 	add	ix,sp
   66CA F5            [11]  131 	push	af
   66CB F5            [11]  132 	push	af
   66CC 3B            [ 6]  133 	dec	sp
                            134 ;src/main.c:81: u8  frame  = 0;  // Actual animation frame
   66CD 0E 00         [ 7]  135 	ld	c, #0x00
                            136 ;src/main.c:82: u8  cycles = 0;  // Number of waiting cycles done for present frame
   66CF DD 36 FB 00   [19]  137 	ld	-5 (ix), #0x00
                            138 ;src/main.c:85: u8  floor_color = 0b1101010; // Pixel pattern for the floor
   66D3 1E 6A         [ 7]  139 	ld	e, #0x6a
                            140 ;src/main.c:89: initialize();
   66D5 C5            [11]  141 	push	bc
   66D6 D5            [11]  142 	push	de
   66D7 CD 48 66      [17]  143 	call	_initialize
   66DA 21 22 56      [10]  144 	ld	hl, #0x5622
   66DD E5            [11]  145 	push	hl
   66DE 21 00 C0      [10]  146 	ld	hl, #0xc000
   66E1 E5            [11]  147 	push	hl
   66E2 CD 49 6A      [17]  148 	call	_cpct_getScreenPtr
   66E5 D1            [10]  149 	pop	de
   66E6 C1            [10]  150 	pop	bc
   66E7 DD 75 FC      [19]  151 	ld	-4 (ix), l
   66EA DD 74 FD      [19]  152 	ld	-3 (ix), h
                            153 ;src/main.c:94: pvmem_floor = cpct_getScreenPtr(CPCT_VMEM_START, FLOOR_X, FLOOR_Y);
   66ED C5            [11]  154 	push	bc
   66EE D5            [11]  155 	push	de
   66EF 21 1E B4      [10]  156 	ld	hl, #0xb41e
   66F2 E5            [11]  157 	push	hl
   66F3 21 00 C0      [10]  158 	ld	hl, #0xc000
   66F6 E5            [11]  159 	push	hl
   66F7 CD 49 6A      [17]  160 	call	_cpct_getScreenPtr
   66FA D1            [10]  161 	pop	de
   66FB C1            [10]  162 	pop	bc
   66FC DD 75 FE      [19]  163 	ld	-2 (ix), l
   66FF DD 74 FF      [19]  164 	ld	-1 (ix), h
                            165 ;src/main.c:98: while(1) {
   6702                     166 00111$:
                            167 ;src/main.c:102: cpct_scanKeyboard_f();
   6702 C5            [11]  168 	push	bc
   6703 D5            [11]  169 	push	de
   6704 CD 9E 67      [17]  170 	call	_cpct_scanKeyboard_f
   6707 CD 18 69      [17]  171 	call	_cpct_isAnyKeyPressed
   670A D1            [10]  172 	pop	de
   670B C1            [10]  173 	pop	bc
   670C 7D            [ 4]  174 	ld	a, l
   670D B7            [ 4]  175 	or	a, a
   670E 28 26         [12]  176 	jr	Z,00105$
                            177 ;src/main.c:107: while (i--) {
   6710 06 06         [ 7]  178 	ld	b, #0x06
   6712                     179 00101$:
   6712 50            [ 4]  180 	ld	d, b
   6713 05            [ 4]  181 	dec	b
   6714 7A            [ 4]  182 	ld	a, d
   6715 B7            [ 4]  183 	or	a, a
   6716 28 1E         [12]  184 	jr	Z,00105$
                            185 ;src/main.c:108: cpct_hflipSpriteM2(SP_W, SP_H, g_animation[i]);
   6718 68            [ 4]  186 	ld	l, b
   6719 26 00         [ 7]  187 	ld	h, #0x00
   671B 29            [11]  188 	add	hl, hl
   671C 7D            [ 4]  189 	ld	a, l
   671D C6 9F         [ 7]  190 	add	a, #<(_g_animation)
   671F 6F            [ 4]  191 	ld	l, a
   6720 7C            [ 4]  192 	ld	a, h
   6721 CE 66         [ 7]  193 	adc	a, #>(_g_animation)
   6723 67            [ 4]  194 	ld	h, a
   6724 7E            [ 7]  195 	ld	a, (hl)
   6725 23            [ 6]  196 	inc	hl
   6726 66            [ 7]  197 	ld	h, (hl)
   6727 6F            [ 4]  198 	ld	l, a
   6728 C5            [11]  199 	push	bc
   6729 D5            [11]  200 	push	de
   672A E5            [11]  201 	push	hl
   672B 21 0A 5E      [10]  202 	ld	hl, #0x5e0a
   672E E5            [11]  203 	push	hl
   672F CD 3B 69      [17]  204 	call	_cpct_hflipSpriteM2
   6732 D1            [10]  205 	pop	de
   6733 C1            [10]  206 	pop	bc
   6734 18 DC         [12]  207 	jr	00101$
   6736                     208 00105$:
                            209 ;src/main.c:116: if (++cycles == wait_cycles) {
   6736 DD 34 FB      [23]  210 	inc	-5 (ix)
   6739 DD 7E FB      [19]  211 	ld	a, -5 (ix)
   673C D6 06         [ 7]  212 	sub	a, #0x06
   673E 20 0F         [12]  213 	jr	NZ,00109$
                            214 ;src/main.c:117: cycles = 0;                   // Restart frame counter
   6740 DD 36 FB 00   [19]  215 	ld	-5 (ix), #0x00
                            216 ;src/main.c:118: if (++frame == ANIM_FRAMES) {  // Next animation frame
   6744 0C            [ 4]  217 	inc	c
   6745 79            [ 4]  218 	ld	a, c
                            219 ;src/main.c:119: frame = 0;
   6746 D6 06         [ 7]  220 	sub	a,#0x06
   6748 20 01         [12]  221 	jr	NZ,00107$
   674A 4F            [ 4]  222 	ld	c,a
   674B                     223 00107$:
                            224 ;src/main.c:122: floor_color ^= 0xFF;
   674B 7B            [ 4]  225 	ld	a, e
   674C EE FF         [ 7]  226 	xor	a, #0xff
   674E 5F            [ 4]  227 	ld	e, a
   674F                     228 00109$:
                            229 ;src/main.c:126: cpct_waitVSYNC();
   674F C5            [11]  230 	push	bc
   6750 D5            [11]  231 	push	de
   6751 CD 25 69      [17]  232 	call	_cpct_waitVSYNC
   6754 D1            [10]  233 	pop	de
   6755 C1            [10]  234 	pop	bc
                            235 ;src/main.c:129: cpct_drawSprite(g_animation[frame], pvmem_spr, SP_W, SP_H);
   6756 DD 46 FC      [19]  236 	ld	b, -4 (ix)
   6759 DD 56 FD      [19]  237 	ld	d, -3 (ix)
   675C 69            [ 4]  238 	ld	l, c
   675D 26 00         [ 7]  239 	ld	h, #0x00
   675F 29            [11]  240 	add	hl, hl
   6760 3E 9F         [ 7]  241 	ld	a, #<(_g_animation)
   6762 85            [ 4]  242 	add	a, l
   6763 6F            [ 4]  243 	ld	l, a
   6764 3E 66         [ 7]  244 	ld	a, #>(_g_animation)
   6766 8C            [ 4]  245 	adc	a, h
   6767 67            [ 4]  246 	ld	h, a
   6768 7E            [ 7]  247 	ld	a, (hl)
   6769 23            [ 6]  248 	inc	hl
   676A 66            [ 7]  249 	ld	h, (hl)
   676B 6F            [ 4]  250 	ld	l, a
   676C E5            [11]  251 	push	hl
   676D FD E1         [14]  252 	pop	iy
   676F C5            [11]  253 	push	bc
   6770 D5            [11]  254 	push	de
   6771 21 0A 5E      [10]  255 	ld	hl, #0x5e0a
   6774 E5            [11]  256 	push	hl
   6775 58            [ 4]  257 	ld	e,b
   6776 D5            [11]  258 	push	de
   6777 FD E5         [15]  259 	push	iy
   6779 CD 43 68      [17]  260 	call	_cpct_drawSprite
   677C D1            [10]  261 	pop	de
   677D C1            [10]  262 	pop	bc
                            263 ;src/main.c:132: cpct_drawSolidBox(pvmem_floor, floor_color, FLOOR_W, FLOOR_H);
   677E 43            [ 4]  264 	ld	b, e
   677F 16 00         [ 7]  265 	ld	d, #0x00
   6781 E5            [11]  266 	push	hl
   6782 DD 6E FE      [19]  267 	ld	l, -2 (ix)
   6785 DD 66 FF      [19]  268 	ld	h, -1 (ix)
   6788 E5            [11]  269 	push	hl
   6789 FD E1         [14]  270 	pop	iy
   678B E1            [10]  271 	pop	hl
   678C C5            [11]  272 	push	bc
   678D D5            [11]  273 	push	de
   678E 21 14 0A      [10]  274 	ld	hl, #0x0a14
   6791 E5            [11]  275 	push	hl
   6792 58            [ 4]  276 	ld	e,b
   6793 D5            [11]  277 	push	de
   6794 FD E5         [15]  278 	push	iy
   6796 CD A1 69      [17]  279 	call	_cpct_drawSolidBox
   6799 D1            [10]  280 	pop	de
   679A C1            [10]  281 	pop	bc
   679B C3 02 67      [10]  282 	jp	00111$
                            283 	.area _CODE
                            284 	.area _INITIALIZER
                            285 	.area _CABS (ABS)
