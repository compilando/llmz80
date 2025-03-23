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
                             12 	.globl _waitNVSYNCs
                             13 	.globl _initialization
                             14 	.globl _cpct_etm_setTileset2x4
                             15 	.globl _cpct_etm_drawTileBox2x4
                             16 	.globl _cpct_etm_drawTilemap2x4_f
                             17 	.globl _cpct_getScreenPtr
                             18 	.globl _cpct_setPALColour
                             19 	.globl _cpct_setPalette
                             20 	.globl _cpct_waitVSYNC
                             21 	.globl _cpct_setVideoMode
                             22 	.globl _cpct_drawSpriteMaskedAlignedTable
                             23 	.globl _cpct_disableFirmware
                             24 ;--------------------------------------------------------
                             25 ; special function registers
                             26 ;--------------------------------------------------------
                             27 ;--------------------------------------------------------
                             28 ; ram data
                             29 ;--------------------------------------------------------
                             30 	.area _DATA
                             31 ;--------------------------------------------------------
                             32 ; ram data
                             33 ;--------------------------------------------------------
                             34 	.area _INITIALIZED
                             35 ;--------------------------------------------------------
                             36 ; absolute external ram data
                             37 ;--------------------------------------------------------
                             38 	.area _DABS (ABS)
                             39 ;--------------------------------------------------------
                             40 ; global & static initialisations
                             41 ;--------------------------------------------------------
                             42 	.area _HOME
                             43 	.area _GSINIT
                             44 	.area _GSFINAL
                             45 	.area _GSINIT
                             46 ;--------------------------------------------------------
                             47 ; Home
                             48 ;--------------------------------------------------------
                             49 	.area _HOME
                             50 	.area _HOME
                             51 ;--------------------------------------------------------
                             52 ; code
                             53 ;--------------------------------------------------------
                             54 	.area _CODE
                             55 ;src/main.c:26: cpctm_createTransparentMaskTable(g_masktable, 0x0100, M0, 0);
                             56 ;	---------------------------------
                             57 ; Function dummy_cpct_transparentMaskTable0M0_container
                             58 ; ---------------------------------
   0B61                      59 _dummy_cpct_transparentMaskTable0M0_container::
                             60 	.area _g_masktable_ (ABS) 
   0100                      61 	.org 0x0100 
   0100                      62 	 _g_masktable::
   0100 FF AA 55 00 AA AA    63 	.db 0xFF, 0xAA, 0x55, 0x00, 0xAA, 0xAA, 0x00, 0x00 
        00 00
   0108 55 00 55 00 00 00    64 	.db 0x55, 0x00, 0x55, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   0110 AA AA 00 00 AA AA    65 	.db 0xAA, 0xAA, 0x00, 0x00, 0xAA, 0xAA, 0x00, 0x00 
        00 00
   0118 00 00 00 00 00 00    66 	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   0120 55 00 55 00 00 00    67 	.db 0x55, 0x00, 0x55, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   0128 55 00 55 00 00 00    68 	.db 0x55, 0x00, 0x55, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   0130 00 00 00 00 00 00    69 	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   0138 00 00 00 00 00 00    70 	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   0140 AA AA 00 00 AA AA    71 	.db 0xAA, 0xAA, 0x00, 0x00, 0xAA, 0xAA, 0x00, 0x00 
        00 00
   0148 00 00 00 00 00 00    72 	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   0150 AA AA 00 00 AA AA    73 	.db 0xAA, 0xAA, 0x00, 0x00, 0xAA, 0xAA, 0x00, 0x00 
        00 00
   0158 00 00 00 00 00 00    74 	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   0160 00 00 00 00 00 00    75 	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   0168 00 00 00 00 00 00    76 	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   0170 00 00 00 00 00 00    77 	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   0178 00 00 00 00 00 00    78 	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   0180 55 00 55 00 00 00    79 	.db 0x55, 0x00, 0x55, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   0188 55 00 55 00 00 00    80 	.db 0x55, 0x00, 0x55, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   0190 00 00 00 00 00 00    81 	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   0198 00 00 00 00 00 00    82 	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   01A0 55 00 55 00 00 00    83 	.db 0x55, 0x00, 0x55, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   01A8 55 00 55 00 00 00    84 	.db 0x55, 0x00, 0x55, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   01B0 00 00 00 00 00 00    85 	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   01B8 00 00 00 00 00 00    86 	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   01C0 00 00 00 00 00 00    87 	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   01C8 00 00 00 00 00 00    88 	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   01D0 00 00 00 00 00 00    89 	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   01D8 00 00 00 00 00 00    90 	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   01E0 00 00 00 00 00 00    91 	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   01E8 00 00 00 00 00 00    92 	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   01F0 00 00 00 00 00 00    93 	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   01F8 00 00 00 00 00 00    94 	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
                             95 	.area _CSEG (REL, CON) 
                             96 ;src/main.c:51: void initialization (){ 
                             97 ;	---------------------------------
                             98 ; Function initialization
                             99 ; ---------------------------------
   0CFD                     100 _initialization::
                            101 ;src/main.c:52: cpct_disableFirmware();          // Disable firmware to prevent it from interfering
   0CFD CD 7A 0C      [17]  102 	call	_cpct_disableFirmware
                            103 ;src/main.c:53: cpct_setPalette(g_palette, 7);   // Set palette using hardware colour values
   0D00 21 07 00      [10]  104 	ld	hl, #0x0007
   0D03 E5            [11]  105 	push	hl
   0D04 21 CA 0A      [10]  106 	ld	hl, #_g_palette
   0D07 E5            [11]  107 	push	hl
   0D08 CD 61 0B      [17]  108 	call	_cpct_setPalette
                            109 ;src/main.c:54: cpct_setBorder (HW_BLACK);       // Set border colour same as background (Black)
   0D0B 21 10 14      [10]  110 	ld	hl, #0x1410
   0D0E E5            [11]  111 	push	hl
   0D0F CD 78 0B      [17]  112 	call	_cpct_setPALColour
                            113 ;src/main.c:55: cpct_setVideoMode(0);            // Change to Mode 0 (160x200, 16 colours)
   0D12 2E 00         [ 7]  114 	ld	l, #0x00
   0D14 CD 6C 0C      [17]  115 	call	_cpct_setVideoMode
                            116 ;src/main.c:58: cpct_etm_setTileset2x4(g_tileset);
   0D17 21 D0 09      [10]  117 	ld	hl, #_g_tileset
   0D1A CD 13 0C      [17]  118 	call	_cpct_etm_setTileset2x4
                            119 ;src/main.c:62: CPCT_VMEM_START, g_background);  
                            120 ;src/main.c:61: cpct_etm_drawTilemap2x4_f(MAP_WIDTH_TILES, MAP_HEIGHT_TILES, 
   0D1D 21 00 02      [10]  121 	ld	hl, #_g_background
   0D20 E5            [11]  122 	push	hl
   0D21 21 00 C0      [10]  123 	ld	hl, #0xc000
   0D24 E5            [11]  124 	push	hl
   0D25 21 28 32      [10]  125 	ld	hl, #0x3228
   0D28 E5            [11]  126 	push	hl
   0D29 CD 38 0C      [17]  127 	call	_cpct_etm_drawTilemap2x4_f
   0D2C C9            [10]  128 	ret
                            129 ;src/main.c:68: void waitNVSYNCs(u8 n) {
                            130 ;	---------------------------------
                            131 ; Function waitNVSYNCs
                            132 ; ---------------------------------
   0D2D                     133 _waitNVSYNCs::
                            134 ;src/main.c:69: do {
   0D2D 21 02 00      [10]  135 	ld	hl, #2+0
   0D30 39            [11]  136 	add	hl, sp
   0D31 4E            [ 7]  137 	ld	c, (hl)
   0D32                     138 00103$:
                            139 ;src/main.c:70: cpct_waitVSYNC();
   0D32 C5            [11]  140 	push	bc
   0D33 CD 64 0C      [17]  141 	call	_cpct_waitVSYNC
   0D36 C1            [10]  142 	pop	bc
                            143 ;src/main.c:71: if (--n) {
   0D37 0D            [ 4]  144 	dec	c
   0D38 79            [ 4]  145 	ld	a, c
   0D39 B7            [ 4]  146 	or	a, a
   0D3A 28 02         [12]  147 	jr	Z,00104$
                            148 ;src/main.c:72: __asm__ ("halt");
   0D3C 76            [ 4]  149 	halt
                            150 ;src/main.c:73: __asm__ ("halt");
   0D3D 76            [ 4]  151 	halt
   0D3E                     152 00104$:
                            153 ;src/main.c:75: } while (n);
   0D3E 79            [ 4]  154 	ld	a, c
   0D3F B7            [ 4]  155 	or	a, a
   0D40 20 F0         [12]  156 	jr	NZ,00103$
   0D42 C9            [10]  157 	ret
                            158 ;src/main.c:81: void main(void) {
                            159 ;	---------------------------------
                            160 ; Function main
                            161 ; ---------------------------------
   0D43                     162 _main::
   0D43 DD E5         [15]  163 	push	ix
   0D45 DD 21 00 00   [14]  164 	ld	ix,#0
   0D49 DD 39         [15]  165 	add	ix,sp
   0D4B 21 F8 FF      [10]  166 	ld	hl, #-8
   0D4E 39            [11]  167 	add	hl, sp
   0D4F F9            [ 6]  168 	ld	sp, hl
                            169 ;src/main.c:84: TAlien* a = (void*)&sa;
   0D50 01 BA 0E      [10]  170 	ld	bc, #_main_sa_1_135+0
   0D53 33            [ 6]  171 	inc	sp
   0D54 33            [ 6]  172 	inc	sp
   0D55 C5            [11]  173 	push	bc
                            174 ;src/main.c:87: initialization();
   0D56 CD FD 0C      [17]  175 	call	_initialization
                            176 ;src/main.c:92: while(1) {
   0D59                     177 00116$:
                            178 ;src/main.c:96: if (a->vx < 0) {
   0D59 DD 7E F8      [19]  179 	ld	a, -8 (ix)
   0D5C C6 02         [ 7]  180 	add	a, #0x02
   0D5E DD 77 FE      [19]  181 	ld	-2 (ix), a
   0D61 DD 7E F9      [19]  182 	ld	a, -7 (ix)
   0D64 CE 00         [ 7]  183 	adc	a, #0x00
   0D66 DD 77 FF      [19]  184 	ld	-1 (ix), a
   0D69 DD 6E FE      [19]  185 	ld	l,-2 (ix)
   0D6C DD 66 FF      [19]  186 	ld	h,-1 (ix)
   0D6F 4E            [ 7]  187 	ld	c, (hl)
                            188 ;src/main.c:97: if (a->tx < -a->vx)
   0D70 E1            [10]  189 	pop	hl
   0D71 E5            [11]  190 	push	hl
   0D72 46            [ 7]  191 	ld	b, (hl)
   0D73 DD 71 FC      [19]  192 	ld	-4 (ix), c
   0D76 79            [ 4]  193 	ld	a, c
   0D77 17            [ 4]  194 	rla
   0D78 9F            [ 4]  195 	sbc	a, a
   0D79 DD 77 FD      [19]  196 	ld	-3 (ix), a
   0D7C DD 70 FA      [19]  197 	ld	-6 (ix), b
   0D7F DD 36 FB 00   [19]  198 	ld	-5 (ix), #0x00
                            199 ;src/main.c:96: if (a->vx < 0) {
   0D83 CB 79         [ 8]  200 	bit	7, c
   0D85 28 25         [12]  201 	jr	Z,00106$
                            202 ;src/main.c:97: if (a->tx < -a->vx)
   0D87 AF            [ 4]  203 	xor	a, a
   0D88 DD 96 FC      [19]  204 	sub	a, -4 (ix)
   0D8B 4F            [ 4]  205 	ld	c, a
   0D8C 3E 00         [ 7]  206 	ld	a, #0x00
   0D8E DD 9E FD      [19]  207 	sbc	a, -3 (ix)
   0D91 47            [ 4]  208 	ld	b, a
   0D92 DD 7E FA      [19]  209 	ld	a, -6 (ix)
   0D95 91            [ 4]  210 	sub	a, c
   0D96 DD 7E FB      [19]  211 	ld	a, -5 (ix)
   0D99 98            [ 4]  212 	sbc	a, b
   0D9A E2 9F 0D      [10]  213 	jp	PO, 00148$
   0D9D EE 80         [ 7]  214 	xor	a, #0x80
   0D9F                     215 00148$:
   0D9F F2 E5 0D      [10]  216 	jp	P, 00107$
                            217 ;src/main.c:98: a->vx = 1;
   0DA2 DD 6E FE      [19]  218 	ld	l,-2 (ix)
   0DA5 DD 66 FF      [19]  219 	ld	h,-1 (ix)
   0DA8 36 01         [10]  220 	ld	(hl), #0x01
   0DAA 18 39         [12]  221 	jr	00107$
   0DAC                     222 00106$:
                            223 ;src/main.c:99: } else if (a->tx + a->vx + ALIEN_WIDTH_TILES >= MAP_WIDTH_TILES)
   0DAC DD 7E FA      [19]  224 	ld	a, -6 (ix)
   0DAF DD 86 FC      [19]  225 	add	a, -4 (ix)
   0DB2 DD 77 FA      [19]  226 	ld	-6 (ix), a
   0DB5 DD 7E FB      [19]  227 	ld	a, -5 (ix)
   0DB8 DD 8E FD      [19]  228 	adc	a, -3 (ix)
   0DBB DD 77 FB      [19]  229 	ld	-5 (ix), a
   0DBE DD 7E FA      [19]  230 	ld	a, -6 (ix)
   0DC1 C6 03         [ 7]  231 	add	a, #0x03
   0DC3 DD 77 FA      [19]  232 	ld	-6 (ix), a
   0DC6 DD 7E FB      [19]  233 	ld	a, -5 (ix)
   0DC9 CE 00         [ 7]  234 	adc	a, #0x00
   0DCB DD 77 FB      [19]  235 	ld	-5 (ix), a
   0DCE DD 7E FA      [19]  236 	ld	a, -6 (ix)
   0DD1 D6 28         [ 7]  237 	sub	a, #0x28
   0DD3 DD 7E FB      [19]  238 	ld	a, -5 (ix)
   0DD6 17            [ 4]  239 	rla
   0DD7 3F            [ 4]  240 	ccf
   0DD8 1F            [ 4]  241 	rra
   0DD9 DE 80         [ 7]  242 	sbc	a, #0x80
   0DDB 38 08         [12]  243 	jr	C,00107$
                            244 ;src/main.c:100: a->vx = -1;
   0DDD DD 6E FE      [19]  245 	ld	l,-2 (ix)
   0DE0 DD 66 FF      [19]  246 	ld	h,-1 (ix)
   0DE3 36 FF         [10]  247 	ld	(hl), #0xff
   0DE5                     248 00107$:
                            249 ;src/main.c:102: if (a->vy < 0) {
   0DE5 DD 7E F8      [19]  250 	ld	a, -8 (ix)
   0DE8 C6 03         [ 7]  251 	add	a, #0x03
   0DEA DD 77 FA      [19]  252 	ld	-6 (ix), a
   0DED DD 7E F9      [19]  253 	ld	a, -7 (ix)
   0DF0 CE 00         [ 7]  254 	adc	a, #0x00
   0DF2 DD 77 FB      [19]  255 	ld	-5 (ix), a
   0DF5 DD 6E FA      [19]  256 	ld	l,-6 (ix)
   0DF8 DD 66 FB      [19]  257 	ld	h,-5 (ix)
   0DFB 4E            [ 7]  258 	ld	c, (hl)
                            259 ;src/main.c:103: if (a->ty < -a->vy)
   0DFC D1            [10]  260 	pop	de
   0DFD D5            [11]  261 	push	de
   0DFE 13            [ 6]  262 	inc	de
   0DFF DD 71 FC      [19]  263 	ld	-4 (ix), c
   0E02 79            [ 4]  264 	ld	a, c
   0E03 17            [ 4]  265 	rla
   0E04 9F            [ 4]  266 	sbc	a, a
   0E05 DD 77 FD      [19]  267 	ld	-3 (ix), a
                            268 ;src/main.c:113: cpct_etm_drawTileBox2x4(a->tx, a->ty, ALIEN_WIDTH_TILES, ALIEN_HEIGHT_TILES, 
   0E08 1A            [ 7]  269 	ld	a, (de)
   0E09 6F            [ 4]  270 	ld	l, a
                            271 ;src/main.c:103: if (a->ty < -a->vy)
   0E0A 26 00         [ 7]  272 	ld	h, #0x00
                            273 ;src/main.c:102: if (a->vy < 0) {
   0E0C CB 79         [ 8]  274 	bit	7, c
   0E0E 28 21         [12]  275 	jr	Z,00113$
                            276 ;src/main.c:103: if (a->ty < -a->vy)
   0E10 AF            [ 4]  277 	xor	a, a
   0E11 DD 96 FC      [19]  278 	sub	a, -4 (ix)
   0E14 4F            [ 4]  279 	ld	c, a
   0E15 3E 00         [ 7]  280 	ld	a, #0x00
   0E17 DD 9E FD      [19]  281 	sbc	a, -3 (ix)
   0E1A 47            [ 4]  282 	ld	b, a
   0E1B 7D            [ 4]  283 	ld	a, l
   0E1C 91            [ 4]  284 	sub	a, c
   0E1D 7C            [ 4]  285 	ld	a, h
   0E1E 98            [ 4]  286 	sbc	a, b
   0E1F E2 24 0E      [10]  287 	jp	PO, 00149$
   0E22 EE 80         [ 7]  288 	xor	a, #0x80
   0E24                     289 00149$:
   0E24 F2 51 0E      [10]  290 	jp	P, 00114$
                            291 ;src/main.c:104: a->vy = 1;
   0E27 DD 6E FA      [19]  292 	ld	l,-6 (ix)
   0E2A DD 66 FB      [19]  293 	ld	h,-5 (ix)
   0E2D 36 01         [10]  294 	ld	(hl), #0x01
   0E2F 18 20         [12]  295 	jr	00114$
   0E31                     296 00113$:
                            297 ;src/main.c:105: } else if (a->ty + a->vy + ALIEN_HEIGHT_TILES >= MAP_HEIGHT_TILES)
   0E31 DD 4E FC      [19]  298 	ld	c,-4 (ix)
   0E34 DD 46 FD      [19]  299 	ld	b,-3 (ix)
   0E37 09            [11]  300 	add	hl, bc
   0E38 01 06 00      [10]  301 	ld	bc, #0x0006
   0E3B 09            [11]  302 	add	hl, bc
   0E3C 01 32 80      [10]  303 	ld	bc, #0x8032
   0E3F 29            [11]  304 	add	hl, hl
   0E40 3F            [ 4]  305 	ccf
   0E41 CB 1C         [ 8]  306 	rr	h
   0E43 CB 1D         [ 8]  307 	rr	l
   0E45 ED 42         [15]  308 	sbc	hl, bc
   0E47 38 08         [12]  309 	jr	C,00114$
                            310 ;src/main.c:106: a->vy = -1;
   0E49 DD 6E FA      [19]  311 	ld	l,-6 (ix)
   0E4C DD 66 FB      [19]  312 	ld	h,-5 (ix)
   0E4F 36 FF         [10]  313 	ld	(hl), #0xff
   0E51                     314 00114$:
                            315 ;src/main.c:110: waitNVSYNCs(2);
   0E51 D5            [11]  316 	push	de
   0E52 3E 02         [ 7]  317 	ld	a, #0x02
   0E54 F5            [11]  318 	push	af
   0E55 33            [ 6]  319 	inc	sp
   0E56 CD 2D 0D      [17]  320 	call	_waitNVSYNCs
   0E59 33            [ 6]  321 	inc	sp
   0E5A D1            [10]  322 	pop	de
                            323 ;src/main.c:114: MAP_WIDTH_TILES, CPCT_VMEM_START, g_background);
                            324 ;src/main.c:113: cpct_etm_drawTileBox2x4(a->tx, a->ty, ALIEN_WIDTH_TILES, ALIEN_HEIGHT_TILES, 
   0E5B 1A            [ 7]  325 	ld	a, (de)
   0E5C 4F            [ 4]  326 	ld	c, a
   0E5D E1            [10]  327 	pop	hl
   0E5E E5            [11]  328 	push	hl
   0E5F 46            [ 7]  329 	ld	b, (hl)
   0E60 D5            [11]  330 	push	de
   0E61 21 00 02      [10]  331 	ld	hl, #_g_background
   0E64 E5            [11]  332 	push	hl
   0E65 21 00 C0      [10]  333 	ld	hl, #0xc000
   0E68 E5            [11]  334 	push	hl
   0E69 21 06 28      [10]  335 	ld	hl, #0x2806
   0E6C E5            [11]  336 	push	hl
   0E6D 3E 03         [ 7]  337 	ld	a, #0x03
   0E6F F5            [11]  338 	push	af
   0E70 33            [ 6]  339 	inc	sp
   0E71 79            [ 4]  340 	ld	a, c
   0E72 F5            [11]  341 	push	af
   0E73 33            [ 6]  342 	inc	sp
   0E74 C5            [11]  343 	push	bc
   0E75 33            [ 6]  344 	inc	sp
   0E76 CD 84 0B      [17]  345 	call	_cpct_etm_drawTileBox2x4
   0E79 D1            [10]  346 	pop	de
                            347 ;src/main.c:116: a->tx += a->vx; 
   0E7A E1            [10]  348 	pop	hl
   0E7B E5            [11]  349 	push	hl
   0E7C 4E            [ 7]  350 	ld	c, (hl)
   0E7D DD 6E FE      [19]  351 	ld	l,-2 (ix)
   0E80 DD 66 FF      [19]  352 	ld	h,-1 (ix)
   0E83 46            [ 7]  353 	ld	b, (hl)
   0E84 79            [ 4]  354 	ld	a, c
   0E85 80            [ 4]  355 	add	a, b
   0E86 E1            [10]  356 	pop	hl
   0E87 E5            [11]  357 	push	hl
   0E88 77            [ 7]  358 	ld	(hl), a
                            359 ;src/main.c:117: a->ty += a->vy;
   0E89 1A            [ 7]  360 	ld	a, (de)
   0E8A 4F            [ 4]  361 	ld	c, a
   0E8B DD 6E FA      [19]  362 	ld	l,-6 (ix)
   0E8E DD 66 FB      [19]  363 	ld	h,-5 (ix)
   0E91 46            [ 7]  364 	ld	b, (hl)
   0E92 79            [ 4]  365 	ld	a, c
   0E93 80            [ 4]  366 	add	a, b
   0E94 12            [ 7]  367 	ld	(de), a
                            368 ;src/main.c:118: pscra = cpct_getScreenPtr(CPCT_VMEM_START, TILEWIDTH_BYTES*a->tx, TILEHEIGHT_BYTES*a->ty);
   0E95 1A            [ 7]  369 	ld	a, (de)
   0E96 87            [ 4]  370 	add	a, a
   0E97 87            [ 4]  371 	add	a, a
   0E98 47            [ 4]  372 	ld	b, a
   0E99 E1            [10]  373 	pop	hl
   0E9A E5            [11]  374 	push	hl
   0E9B 56            [ 7]  375 	ld	d, (hl)
   0E9C CB 22         [ 8]  376 	sla	d
   0E9E 4A            [ 4]  377 	ld	c, d
   0E9F C5            [11]  378 	push	bc
   0EA0 21 00 C0      [10]  379 	ld	hl, #0xc000
   0EA3 E5            [11]  380 	push	hl
   0EA4 CD AC 0C      [17]  381 	call	_cpct_getScreenPtr
                            382 ;src/main.c:121: ALIEN_HEIGHT_BYTES, g_masktable);
   0EA7 01 00 01      [10]  383 	ld	bc, #_g_masktable+0
                            384 ;src/main.c:120: cpct_drawSpriteMaskedAlignedTable(g_alien, pscra, ALIEN_WIDTH_BYTES, 
   0EAA 11 D1 0A      [10]  385 	ld	de, #_g_alien+0
   0EAD C5            [11]  386 	push	bc
   0EAE 01 06 18      [10]  387 	ld	bc, #0x1806
   0EB1 C5            [11]  388 	push	bc
   0EB2 E5            [11]  389 	push	hl
   0EB3 D5            [11]  390 	push	de
   0EB4 CD C2 0C      [17]  391 	call	_cpct_drawSpriteMaskedAlignedTable
   0EB7 C3 59 0D      [10]  392 	jp	00116$
   0EBA                     393 _main_sa_1_135:
   0EBA 00                  394 	.db #0x00	; 0
   0EBB 00                  395 	.db #0x00	; 0
   0EBC 01                  396 	.db #0x01	;  1
   0EBD 01                  397 	.db #0x01	;  1
                            398 	.area _CODE
                            399 	.area _INITIALIZER
                            400 	.area _CABS (ABS)
