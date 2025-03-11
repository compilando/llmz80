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
                             12 	.globl _drawLogo
                             13 	.globl _drawBanner
                             14 	.globl _cpct_getScreenPtr
                             15 	.globl _cpct_setPALColour
                             16 	.globl _cpct_setPalette
                             17 	.globl _cpct_fw2hw
                             18 	.globl _cpct_setVideoMode
                             19 	.globl _cpct_drawSprite
                             20 	.globl _cpct_memset_f64
                             21 	.globl _cpct_disableFirmware
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
                             53 ;src/main.c:37: void drawBanner() {
                             54 ;	---------------------------------
                             55 ; Function drawBanner
                             56 ; ---------------------------------
   0100                      57 _drawBanner::
                             58 ;src/main.c:42: cpct_clearScreen_f64(0);
   0100 21 00 40      [10]   59 	ld	hl, #0x4000
   0103 E5            [11]   60 	push	hl
   0104 26 00         [ 7]   61 	ld	h, #0x00
   0106 E5            [11]   62 	push	hl
   0107 26 C0         [ 7]   63 	ld	h, #0xc0
   0109 E5            [11]   64 	push	hl
   010A CD AB 3E      [17]   65 	call	_cpct_memset_f64
                             66 ;src/main.c:45: cpct_setPalette  (G_banner_palette, 16);
   010D 21 10 00      [10]   67 	ld	hl, #0x0010
   0110 E5            [11]   68 	push	hl
   0111 21 E4 01      [10]   69 	ld	hl, #_G_banner_palette
   0114 E5            [11]   70 	push	hl
   0115 CD D0 3D      [17]   71 	call	_cpct_setPalette
                             72 ;src/main.c:46: cpct_setVideoMode(0);
   0118 2E 00         [ 7]   73 	ld	l, #0x00
   011A CD 11 3F      [17]   74 	call	_cpct_setVideoMode
                             75 ;src/main.c:54: pvideo_s1 = cpct_getScreenPtr(CPCT_VMEM_START,  0, 52);
   011D 21 00 34      [10]   76 	ld	hl, #0x3400
   0120 E5            [11]   77 	push	hl
   0121 26 C0         [ 7]   78 	ld	h, #0xc0
   0123 E5            [11]   79 	push	hl
   0124 CD 30 3F      [17]   80 	call	_cpct_getScreenPtr
                             81 ;src/main.c:55: cpct_drawSprite(G_CPCt_left,  pvideo_s1, BANNER_W, BANNER_H);
   0127 01 F8 10      [10]   82 	ld	bc, #_G_CPCt_left+0
   012A 11 28 60      [10]   83 	ld	de, #0x6028
   012D D5            [11]   84 	push	de
   012E E5            [11]   85 	push	hl
   012F C5            [11]   86 	push	bc
   0130 CD F3 3D      [17]   87 	call	_cpct_drawSprite
                             88 ;src/main.c:58: pvideo_s2 = cpct_getScreenPtr(CPCT_VMEM_START, 40, 52);
   0133 21 28 34      [10]   89 	ld	hl, #0x3428
   0136 E5            [11]   90 	push	hl
   0137 21 00 C0      [10]   91 	ld	hl, #0xc000
   013A E5            [11]   92 	push	hl
   013B CD 30 3F      [17]   93 	call	_cpct_getScreenPtr
                             94 ;src/main.c:59: cpct_drawSprite(G_CPCt_right, pvideo_s2, BANNER_W, BANNER_H);
   013E 01 F8 01      [10]   95 	ld	bc, #_G_CPCt_right+0
   0141 11 28 60      [10]   96 	ld	de, #0x6028
   0144 D5            [11]   97 	push	de
   0145 E5            [11]   98 	push	hl
   0146 C5            [11]   99 	push	bc
   0147 CD F3 3D      [17]  100 	call	_cpct_drawSprite
   014A C9            [10]  101 	ret
                            102 ;src/main.c:65: void drawLogo() {
                            103 ;	---------------------------------
                            104 ; Function drawLogo
                            105 ; ---------------------------------
   014B                     106 _drawLogo::
                            107 ;src/main.c:70: cpct_clearScreen_f64(0);
   014B 21 00 40      [10]  108 	ld	hl, #0x4000
   014E E5            [11]  109 	push	hl
   014F 26 00         [ 7]  110 	ld	h, #0x00
   0151 E5            [11]  111 	push	hl
   0152 26 C0         [ 7]  112 	ld	h, #0xc0
   0154 E5            [11]  113 	push	hl
   0155 CD AB 3E      [17]  114 	call	_cpct_memset_f64
                            115 ;src/main.c:73: cpct_setPalette(G_logo_palette, 4);
   0158 21 04 00      [10]  116 	ld	hl, #0x0004
   015B E5            [11]  117 	push	hl
   015C 21 F4 01      [10]  118 	ld	hl, #_G_logo_palette
   015F E5            [11]  119 	push	hl
   0160 CD D0 3D      [17]  120 	call	_cpct_setPalette
                            121 ;src/main.c:74: cpct_setVideoMode(1);     
   0163 2E 01         [ 7]  122 	ld	l, #0x01
   0165 CD 11 3F      [17]  123 	call	_cpct_setVideoMode
                            124 ;src/main.c:80: pvideo = cpct_getScreenPtr(CPCT_VMEM_START, 20, 4);
   0168 21 14 04      [10]  125 	ld	hl, #0x0414
   016B E5            [11]  126 	push	hl
   016C 21 00 C0      [10]  127 	ld	hl, #0xc000
   016F E5            [11]  128 	push	hl
   0170 CD 30 3F      [17]  129 	call	_cpct_getScreenPtr
                            130 ;src/main.c:81: cpct_drawSprite(G_CPCt_logo, pvideo, LOGO_W, LOGO_H);
   0173 01 F8 1F      [10]  131 	ld	bc, #_G_CPCt_logo+0
   0176 11 28 BF      [10]  132 	ld	de, #0xbf28
   0179 D5            [11]  133 	push	de
   017A E5            [11]  134 	push	hl
   017B C5            [11]  135 	push	bc
   017C CD F3 3D      [17]  136 	call	_cpct_drawSprite
   017F C9            [10]  137 	ret
                            138 ;src/main.c:87: void main(void) {
                            139 ;	---------------------------------
                            140 ; Function main
                            141 ; ---------------------------------
   0180                     142 _main::
                            143 ;src/main.c:92: cpct_disableFirmware();
   0180 CD 1F 3F      [17]  144 	call	_cpct_disableFirmware
                            145 ;src/main.c:96: cpct_fw2hw(G_banner_palette, 16);
   0183 21 10 00      [10]  146 	ld	hl, #0x0010
   0186 E5            [11]  147 	push	hl
   0187 21 E4 01      [10]  148 	ld	hl, #_G_banner_palette
   018A E5            [11]  149 	push	hl
   018B CD 98 3E      [17]  150 	call	_cpct_fw2hw
                            151 ;src/main.c:97: cpct_fw2hw(G_logo_palette, 4);
   018E 21 04 00      [10]  152 	ld	hl, #0x0004
   0191 E5            [11]  153 	push	hl
   0192 21 F4 01      [10]  154 	ld	hl, #_G_logo_palette
   0195 E5            [11]  155 	push	hl
   0196 CD 98 3E      [17]  156 	call	_cpct_fw2hw
                            157 ;src/main.c:101: cpct_setBorder(G_banner_palette[0]);
   0199 21 E4 01      [10]  158 	ld	hl, #_G_banner_palette + 0
   019C 46            [ 7]  159 	ld	b, (hl)
   019D C5            [11]  160 	push	bc
   019E 33            [ 6]  161 	inc	sp
   019F 3E 10         [ 7]  162 	ld	a, #0x10
   01A1 F5            [11]  163 	push	af
   01A2 33            [ 6]  164 	inc	sp
   01A3 CD E7 3D      [17]  165 	call	_cpct_setPALColour
                            166 ;src/main.c:104: while (1) {
   01A6                     167 00104$:
                            168 ;src/main.c:106: drawLogo();
   01A6 CD 4B 01      [17]  169 	call	_drawLogo
                            170 ;src/main.c:107: for(i=0; i < WAITLOOPS; ++i);
   01A9 01 F0 49      [10]  171 	ld	bc,#0x49f0
   01AC 11 02 00      [10]  172 	ld	de,#0x0002
   01AF                     173 00108$:
   01AF 79            [ 4]  174 	ld	a, c
   01B0 C6 FF         [ 7]  175 	add	a, #0xff
   01B2 4F            [ 4]  176 	ld	c, a
   01B3 78            [ 4]  177 	ld	a, b
   01B4 CE FF         [ 7]  178 	adc	a, #0xff
   01B6 47            [ 4]  179 	ld	b, a
   01B7 7B            [ 4]  180 	ld	a, e
   01B8 CE FF         [ 7]  181 	adc	a, #0xff
   01BA 5F            [ 4]  182 	ld	e, a
   01BB 7A            [ 4]  183 	ld	a, d
   01BC CE FF         [ 7]  184 	adc	a, #0xff
   01BE 57            [ 4]  185 	ld	d,a
   01BF B3            [ 4]  186 	or	a, e
   01C0 B0            [ 4]  187 	or	a, b
   01C1 B1            [ 4]  188 	or	a,c
   01C2 20 EB         [12]  189 	jr	NZ,00108$
                            190 ;src/main.c:110: drawBanner();
   01C4 CD 00 01      [17]  191 	call	_drawBanner
                            192 ;src/main.c:111: for(i=0; i < WAITLOOPS; ++i);
   01C7 01 F0 49      [10]  193 	ld	bc,#0x49f0
   01CA 11 02 00      [10]  194 	ld	de,#0x0002
   01CD                     195 00111$:
   01CD 79            [ 4]  196 	ld	a, c
   01CE C6 FF         [ 7]  197 	add	a, #0xff
   01D0 4F            [ 4]  198 	ld	c, a
   01D1 78            [ 4]  199 	ld	a, b
   01D2 CE FF         [ 7]  200 	adc	a, #0xff
   01D4 47            [ 4]  201 	ld	b, a
   01D5 7B            [ 4]  202 	ld	a, e
   01D6 CE FF         [ 7]  203 	adc	a, #0xff
   01D8 5F            [ 4]  204 	ld	e, a
   01D9 7A            [ 4]  205 	ld	a, d
   01DA CE FF         [ 7]  206 	adc	a, #0xff
   01DC 57            [ 4]  207 	ld	d,a
   01DD B3            [ 4]  208 	or	a, e
   01DE B0            [ 4]  209 	or	a, b
   01DF B1            [ 4]  210 	or	a,c
   01E0 20 EB         [12]  211 	jr	NZ,00111$
   01E2 18 C2         [12]  212 	jr	00104$
                            213 	.area _CODE
                            214 	.area _INITIALIZER
                            215 	.area _CABS (ABS)
