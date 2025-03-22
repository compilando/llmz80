                              1 ;--------------------------------------------------------
                              2 ; File Created by SDCC : free open source ANSI-C Compiler
                              3 ; Version 3.6.8 #9946 (Linux)
                              4 ;--------------------------------------------------------
                              5 	.module frame
                              6 	.optsdcc -mz80
                              7 	
                              8 ;--------------------------------------------------------
                              9 ; Public variables in this module
                             10 ;--------------------------------------------------------
                             11 	.globl _cpct_getScreenPtr
                             12 	.globl _cpct_drawSprite
                             13 	.globl _cpct_drawTileAligned4x8
                             14 	.globl _drawFrame
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
                             46 ;src/sprites/frame.c:28: void drawFrame(u8* pscr, u8 x) {
                             47 ;	---------------------------------
                             48 ; Function drawFrame
                             49 ; ---------------------------------
   5E2F                      50 _drawFrame::
   5E2F DD E5         [15]   51 	push	ix
   5E31 DD 21 00 00   [14]   52 	ld	ix,#0
   5E35 DD 39         [15]   53 	add	ix,sp
   5E37 F5            [11]   54 	push	af
                             55 ;src/sprites/frame.c:33: pvmem = cpct_getScreenPtr(pscr, x, 0);
   5E38 DD 7E 04      [19]   56 	ld	a, 4 (ix)
   5E3B DD 77 FE      [19]   57 	ld	-2 (ix), a
   5E3E DD 7E 05      [19]   58 	ld	a, 5 (ix)
   5E41 DD 77 FF      [19]   59 	ld	-1 (ix), a
   5E44 AF            [ 4]   60 	xor	a, a
   5E45 F5            [11]   61 	push	af
   5E46 33            [ 6]   62 	inc	sp
   5E47 DD 7E 06      [19]   63 	ld	a, 6 (ix)
   5E4A F5            [11]   64 	push	af
   5E4B 33            [ 6]   65 	inc	sp
   5E4C C1            [10]   66 	pop	bc
   5E4D E1            [10]   67 	pop	hl
   5E4E E5            [11]   68 	push	hl
   5E4F C5            [11]   69 	push	bc
   5E50 E5            [11]   70 	push	hl
   5E51 CD 9B 67      [17]   71 	call	_cpct_getScreenPtr
                             72 ;src/sprites/frame.c:34: cpct_drawTileAligned4x8(G_frameUpLeftCorner,  pvmem);       // Up-Left
   5E54 5D            [ 4]   73 	ld	e, l
   5E55 54            [ 4]   74 	ld	d, h
   5E56 01 6E 5F      [10]   75 	ld	bc, #_G_frameUpLeftCorner+0
   5E59 E5            [11]   76 	push	hl
   5E5A D5            [11]   77 	push	de
   5E5B C5            [11]   78 	push	bc
   5E5C CD 5B 67      [17]   79 	call	_cpct_drawTileAligned4x8
   5E5F E1            [10]   80 	pop	hl
                             81 ;src/sprites/frame.c:35: cpct_drawTileAligned4x8(G_frameUpRightCorner, pvmem + 54);  // Up-Right
   5E60 01 36 00      [10]   82 	ld	bc, #0x0036
   5E63 09            [11]   83 	add	hl, bc
   5E64 01 8E 5F      [10]   84 	ld	bc, #_G_frameUpRightCorner+0
   5E67 E5            [11]   85 	push	hl
   5E68 C5            [11]   86 	push	bc
   5E69 CD 5B 67      [17]   87 	call	_cpct_drawTileAligned4x8
                             88 ;src/sprites/frame.c:38: for(i=8; i < 192; i += 8) {
   5E6C 06 08         [ 7]   89 	ld	b, #0x08
   5E6E                      90 00104$:
                             91 ;src/sprites/frame.c:39: pvmem = cpct_getScreenPtr(pscr, x, i);
   5E6E C5            [11]   92 	push	bc
   5E6F C5            [11]   93 	push	bc
   5E70 33            [ 6]   94 	inc	sp
   5E71 DD 7E 06      [19]   95 	ld	a, 6 (ix)
   5E74 F5            [11]   96 	push	af
   5E75 33            [ 6]   97 	inc	sp
   5E76 DD 6E FE      [19]   98 	ld	l,-2 (ix)
   5E79 DD 66 FF      [19]   99 	ld	h,-1 (ix)
   5E7C E5            [11]  100 	push	hl
   5E7D CD 9B 67      [17]  101 	call	_cpct_getScreenPtr
   5E80 C1            [10]  102 	pop	bc
                            103 ;src/sprites/frame.c:40: cpct_drawTileAligned4x8(G_frameLeft,  pvmem);      // Left border
   5E81 5D            [ 4]  104 	ld	e, l
   5E82 54            [ 4]  105 	ld	d, h
   5E83 E5            [11]  106 	push	hl
   5E84 C5            [11]  107 	push	bc
   5E85 D5            [11]  108 	push	de
   5E86 11 EE 5F      [10]  109 	ld	de, #_G_frameLeft
   5E89 D5            [11]  110 	push	de
   5E8A CD 5B 67      [17]  111 	call	_cpct_drawTileAligned4x8
   5E8D C1            [10]  112 	pop	bc
   5E8E E1            [10]  113 	pop	hl
                            114 ;src/sprites/frame.c:41: cpct_drawTileAligned4x8(G_frameRight, pvmem + 54); // Right border
   5E8F 11 36 00      [10]  115 	ld	de, #0x0036
   5E92 19            [11]  116 	add	hl, de
   5E93 C5            [11]  117 	push	bc
   5E94 E5            [11]  118 	push	hl
   5E95 21 0E 60      [10]  119 	ld	hl, #_G_frameRight
   5E98 E5            [11]  120 	push	hl
   5E99 CD 5B 67      [17]  121 	call	_cpct_drawTileAligned4x8
   5E9C C1            [10]  122 	pop	bc
                            123 ;src/sprites/frame.c:38: for(i=8; i < 192; i += 8) {
   5E9D 78            [ 4]  124 	ld	a, b
   5E9E C6 08         [ 7]  125 	add	a, #0x08
   5EA0 47            [ 4]  126 	ld	b,a
   5EA1 D6 C0         [ 7]  127 	sub	a, #0xc0
   5EA3 38 C9         [12]  128 	jr	C,00104$
                            129 ;src/sprites/frame.c:45: pvmem = cpct_getScreenPtr(pscr, x, 0);
   5EA5 AF            [ 4]  130 	xor	a, a
   5EA6 F5            [11]  131 	push	af
   5EA7 33            [ 6]  132 	inc	sp
   5EA8 DD 7E 06      [19]  133 	ld	a, 6 (ix)
   5EAB F5            [11]  134 	push	af
   5EAC 33            [ 6]  135 	inc	sp
   5EAD C1            [10]  136 	pop	bc
   5EAE E1            [10]  137 	pop	hl
   5EAF E5            [11]  138 	push	hl
   5EB0 C5            [11]  139 	push	bc
   5EB1 E5            [11]  140 	push	hl
   5EB2 CD 9B 67      [17]  141 	call	_cpct_getScreenPtr
   5EB5 4D            [ 4]  142 	ld	c, l
   5EB6 44            [ 4]  143 	ld	b, h
                            144 ;src/sprites/frame.c:46: for(i=4; i < 28; i += 4) {
   5EB7 1E 04         [ 7]  145 	ld	e, #0x04
   5EB9                     146 00106$:
                            147 ;src/sprites/frame.c:47: pvmem += 4;
   5EB9 03            [ 6]  148 	inc	bc
   5EBA 03            [ 6]  149 	inc	bc
   5EBB 03            [ 6]  150 	inc	bc
   5EBC 03            [ 6]  151 	inc	bc
                            152 ;src/sprites/frame.c:48: cpct_drawTileAligned4x8(G_frameUp, pvmem);       // Left part 
   5EBD 69            [ 4]  153 	ld	l, c
   5EBE 60            [ 4]  154 	ld	h, b
   5EBF C5            [11]  155 	push	bc
   5EC0 D5            [11]  156 	push	de
   5EC1 E5            [11]  157 	push	hl
   5EC2 21 2E 60      [10]  158 	ld	hl, #_G_frameUp
   5EC5 E5            [11]  159 	push	hl
   5EC6 CD 5B 67      [17]  160 	call	_cpct_drawTileAligned4x8
   5EC9 D1            [10]  161 	pop	de
   5ECA C1            [10]  162 	pop	bc
                            163 ;src/sprites/frame.c:49: cpct_drawTileAligned4x8(G_frameUp, pvmem + 26);  // Right part
   5ECB 21 1A 00      [10]  164 	ld	hl, #0x001a
   5ECE 09            [11]  165 	add	hl, bc
   5ECF C5            [11]  166 	push	bc
   5ED0 D5            [11]  167 	push	de
   5ED1 E5            [11]  168 	push	hl
   5ED2 21 2E 60      [10]  169 	ld	hl, #_G_frameUp
   5ED5 E5            [11]  170 	push	hl
   5ED6 CD 5B 67      [17]  171 	call	_cpct_drawTileAligned4x8
   5ED9 D1            [10]  172 	pop	de
   5EDA C1            [10]  173 	pop	bc
                            174 ;src/sprites/frame.c:46: for(i=4; i < 28; i += 4) {
   5EDB 1C            [ 4]  175 	inc	e
   5EDC 1C            [ 4]  176 	inc	e
   5EDD 1C            [ 4]  177 	inc	e
   5EDE 1C            [ 4]  178 	inc	e
   5EDF 7B            [ 4]  179 	ld	a, e
   5EE0 D6 1C         [ 7]  180 	sub	a, #0x1c
   5EE2 38 D5         [12]  181 	jr	C,00106$
                            182 ;src/sprites/frame.c:51: cpct_drawSprite(G_frameUpCenter, pvmem + 2, 6, 8);  // Central tile
   5EE4 03            [ 6]  183 	inc	bc
   5EE5 03            [ 6]  184 	inc	bc
   5EE6 21 06 08      [10]  185 	ld	hl, #0x0806
   5EE9 E5            [11]  186 	push	hl
   5EEA C5            [11]  187 	push	bc
   5EEB 21 6E 60      [10]  188 	ld	hl, #_G_frameUpCenter
   5EEE E5            [11]  189 	push	hl
   5EEF CD F5 64      [17]  190 	call	_cpct_drawSprite
                            191 ;src/sprites/frame.c:54: pvmem = cpct_getScreenPtr(pscr, x, 192);
   5EF2 3E C0         [ 7]  192 	ld	a, #0xc0
   5EF4 F5            [11]  193 	push	af
   5EF5 33            [ 6]  194 	inc	sp
   5EF6 DD 7E 06      [19]  195 	ld	a, 6 (ix)
   5EF9 F5            [11]  196 	push	af
   5EFA 33            [ 6]  197 	inc	sp
   5EFB C1            [10]  198 	pop	bc
   5EFC E1            [10]  199 	pop	hl
   5EFD E5            [11]  200 	push	hl
   5EFE C5            [11]  201 	push	bc
   5EFF E5            [11]  202 	push	hl
   5F00 CD 9B 67      [17]  203 	call	_cpct_getScreenPtr
   5F03 4D            [ 4]  204 	ld	c, l
   5F04 44            [ 4]  205 	ld	b, h
                            206 ;src/sprites/frame.c:55: for(i=4; i < 28; i += 4) {
   5F05 1E 04         [ 7]  207 	ld	e, #0x04
   5F07                     208 00108$:
                            209 ;src/sprites/frame.c:56: pvmem += 4;
   5F07 03            [ 6]  210 	inc	bc
   5F08 03            [ 6]  211 	inc	bc
   5F09 03            [ 6]  212 	inc	bc
   5F0A 03            [ 6]  213 	inc	bc
                            214 ;src/sprites/frame.c:57: cpct_drawTileAligned4x8(G_frameDown, pvmem);       // Left part
   5F0B 69            [ 4]  215 	ld	l, c
   5F0C 60            [ 4]  216 	ld	h, b
   5F0D C5            [11]  217 	push	bc
   5F0E D5            [11]  218 	push	de
   5F0F E5            [11]  219 	push	hl
   5F10 21 4E 60      [10]  220 	ld	hl, #_G_frameDown
   5F13 E5            [11]  221 	push	hl
   5F14 CD 5B 67      [17]  222 	call	_cpct_drawTileAligned4x8
   5F17 D1            [10]  223 	pop	de
   5F18 C1            [10]  224 	pop	bc
                            225 ;src/sprites/frame.c:58: cpct_drawTileAligned4x8(G_frameDown, pvmem + 26);  // Right part
   5F19 21 1A 00      [10]  226 	ld	hl, #0x001a
   5F1C 09            [11]  227 	add	hl, bc
   5F1D C5            [11]  228 	push	bc
   5F1E D5            [11]  229 	push	de
   5F1F E5            [11]  230 	push	hl
   5F20 21 4E 60      [10]  231 	ld	hl, #_G_frameDown
   5F23 E5            [11]  232 	push	hl
   5F24 CD 5B 67      [17]  233 	call	_cpct_drawTileAligned4x8
   5F27 D1            [10]  234 	pop	de
   5F28 C1            [10]  235 	pop	bc
                            236 ;src/sprites/frame.c:55: for(i=4; i < 28; i += 4) {
   5F29 1C            [ 4]  237 	inc	e
   5F2A 1C            [ 4]  238 	inc	e
   5F2B 1C            [ 4]  239 	inc	e
   5F2C 1C            [ 4]  240 	inc	e
   5F2D 7B            [ 4]  241 	ld	a, e
   5F2E D6 1C         [ 7]  242 	sub	a, #0x1c
   5F30 38 D5         [12]  243 	jr	C,00108$
                            244 ;src/sprites/frame.c:60: cpct_drawSprite(G_frameDownCenter, pvmem + 2, 6, 8);  // Central tile
   5F32 03            [ 6]  245 	inc	bc
   5F33 03            [ 6]  246 	inc	bc
   5F34 21 06 08      [10]  247 	ld	hl, #0x0806
   5F37 E5            [11]  248 	push	hl
   5F38 C5            [11]  249 	push	bc
   5F39 21 9E 60      [10]  250 	ld	hl, #_G_frameDownCenter
   5F3C E5            [11]  251 	push	hl
   5F3D CD F5 64      [17]  252 	call	_cpct_drawSprite
                            253 ;src/sprites/frame.c:63: pvmem = cpct_getScreenPtr(pscr, x, 192);
   5F40 3E C0         [ 7]  254 	ld	a, #0xc0
   5F42 F5            [11]  255 	push	af
   5F43 33            [ 6]  256 	inc	sp
   5F44 DD 7E 06      [19]  257 	ld	a, 6 (ix)
   5F47 F5            [11]  258 	push	af
   5F48 33            [ 6]  259 	inc	sp
   5F49 C1            [10]  260 	pop	bc
   5F4A E1            [10]  261 	pop	hl
   5F4B E5            [11]  262 	push	hl
   5F4C C5            [11]  263 	push	bc
   5F4D E5            [11]  264 	push	hl
   5F4E CD 9B 67      [17]  265 	call	_cpct_getScreenPtr
                            266 ;src/sprites/frame.c:64: cpct_drawTileAligned4x8(G_frameDownLeftCorner,  pvmem);        // Down-Left
   5F51 5D            [ 4]  267 	ld	e, l
   5F52 54            [ 4]  268 	ld	d, h
   5F53 01 CE 5F      [10]  269 	ld	bc, #_G_frameDownLeftCorner+0
   5F56 E5            [11]  270 	push	hl
   5F57 D5            [11]  271 	push	de
   5F58 C5            [11]  272 	push	bc
   5F59 CD 5B 67      [17]  273 	call	_cpct_drawTileAligned4x8
   5F5C E1            [10]  274 	pop	hl
                            275 ;src/sprites/frame.c:65: cpct_drawTileAligned4x8(G_frameDownRightCorner, pvmem + 54);   // Down-Right
   5F5D 01 36 00      [10]  276 	ld	bc, #0x0036
   5F60 09            [11]  277 	add	hl, bc
   5F61 01 AE 5F      [10]  278 	ld	bc, #_G_frameDownRightCorner+0
   5F64 E5            [11]  279 	push	hl
   5F65 C5            [11]  280 	push	bc
   5F66 CD 5B 67      [17]  281 	call	_cpct_drawTileAligned4x8
   5F69 DD F9         [10]  282 	ld	sp, ix
   5F6B DD E1         [14]  283 	pop	ix
   5F6D C9            [10]  284 	ret
                            285 	.area _CODE
                            286 	.area _INITIALIZER
                            287 	.area _CABS (ABS)
