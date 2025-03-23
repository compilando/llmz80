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
                             15 	.globl _cpct_setPalette
                             16 	.globl _cpct_setVideoMode
                             17 	.globl _cpct_drawStringM0
                             18 	.globl _cpct_setDrawCharM0
                             19 	.globl _cpct_drawSprite
                             20 	.globl _cpct_drawSolidBox
                             21 	.globl _cpct_px2byteM0
                             22 	.globl _cpct_hflipSpriteM0
                             23 	.globl _cpct_isKeyPressed
                             24 	.globl _cpct_scanKeyboard_f
                             25 	.globl _cpct_disableFirmware
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
                             57 ;src/main.c:42: void initialize() {
                             58 ;	---------------------------------
                             59 ; Function initialize
                             60 ; ---------------------------------
   44E2                      61 _initialize::
                             62 ;src/main.c:46: cpct_disableFirmware();
   44E2 CD 82 48      [17]   63 	call	_cpct_disableFirmware
                             64 ;src/main.c:49: cpct_setPalette(g_palette, 16);
   44E5 21 10 00      [10]   65 	ld	hl, #0x0010
   44E8 E5            [11]   66 	push	hl
   44E9 21 00 40      [10]   67 	ld	hl, #_g_palette
   44EC E5            [11]   68 	push	hl
   44ED CD 2E 46      [17]   69 	call	_cpct_setPalette
                             70 ;src/main.c:50: cpct_setBorder(HW_BLACK);
   44F0 21 10 14      [10]   71 	ld	hl, #0x1410
   44F3 E5            [11]   72 	push	hl
   44F4 CD BB 46      [17]   73 	call	_cpct_setPALColour
                             74 ;src/main.c:53: cpct_setVideoMode(0);
   44F7 2E 00         [ 7]   75 	ld	l, #0x00
   44F9 CD 58 48      [17]   76 	call	_cpct_setVideoMode
                             77 ;src/main.c:57: pvideomem = cpct_getScreenPtr(CPCT_VMEM_START,       0, FLOOR_Y);
   44FC 21 00 A0      [10]   78 	ld	hl, #0xa000
   44FF E5            [11]   79 	push	hl
   4500 26 C0         [ 7]   80 	ld	h, #0xc0
   4502 E5            [11]   81 	push	hl
   4503 CD 5F 49      [17]   82 	call	_cpct_getScreenPtr
                             83 ;src/main.c:58: cpct_drawSolidBox(pvideomem, FLOOR_COLOR, SCR_W/2, FLOOR_HEIGHT);
   4506 E5            [11]   84 	push	hl
   4507 01 01 02      [10]   85 	ld	bc, #0x0201
   450A C5            [11]   86 	push	bc
   450B CD 66 48      [17]   87 	call	_cpct_px2byteM0
   450E 4D            [ 4]   88 	ld	c, l
   450F E1            [10]   89 	pop	hl
   4510 06 00         [ 7]   90 	ld	b, #0x00
   4512 11 28 0A      [10]   91 	ld	de, #0x0a28
   4515 D5            [11]   92 	push	de
   4516 C5            [11]   93 	push	bc
   4517 E5            [11]   94 	push	hl
   4518 CD 92 48      [17]   95 	call	_cpct_drawSolidBox
                             96 ;src/main.c:59: pvideomem = cpct_getScreenPtr(CPCT_VMEM_START, SCR_W/2, FLOOR_Y);
   451B 21 28 A0      [10]   97 	ld	hl, #0xa028
   451E E5            [11]   98 	push	hl
   451F 21 00 C0      [10]   99 	ld	hl, #0xc000
   4522 E5            [11]  100 	push	hl
   4523 CD 5F 49      [17]  101 	call	_cpct_getScreenPtr
                            102 ;src/main.c:60: cpct_drawSolidBox(pvideomem, FLOOR_COLOR, SCR_W/2, FLOOR_HEIGHT);
   4526 E5            [11]  103 	push	hl
   4527 01 01 02      [10]  104 	ld	bc, #0x0201
   452A C5            [11]  105 	push	bc
   452B CD 66 48      [17]  106 	call	_cpct_px2byteM0
   452E 4D            [ 4]  107 	ld	c, l
   452F E1            [10]  108 	pop	hl
   4530 06 00         [ 7]  109 	ld	b, #0x00
   4532 11 28 0A      [10]  110 	ld	de, #0x0a28
   4535 D5            [11]  111 	push	de
   4536 C5            [11]  112 	push	bc
   4537 E5            [11]  113 	push	hl
   4538 CD 92 48      [17]  114 	call	_cpct_drawSolidBox
                            115 ;src/main.c:63: pvideomem = cpct_getScreenPtr(CPCT_VMEM_START,  0, 20);
   453B 21 00 14      [10]  116 	ld	hl, #0x1400
   453E E5            [11]  117 	push	hl
   453F 26 C0         [ 7]  118 	ld	h, #0xc0
   4541 E5            [11]  119 	push	hl
   4542 CD 5F 49      [17]  120 	call	_cpct_getScreenPtr
                            121 ;src/main.c:64: cpct_setDrawCharM0(2, 0);
   4545 E5            [11]  122 	push	hl
   4546 01 02 00      [10]  123 	ld	bc, #0x0002
   4549 C5            [11]  124 	push	bc
   454A CD 3A 49      [17]  125 	call	_cpct_setDrawCharM0
   454D E1            [10]  126 	pop	hl
                            127 ;src/main.c:65: cpct_drawStringM0("  Sprite Flip Demo  ", pvideomem);
   454E 01 8E 45      [10]  128 	ld	bc, #___str_0+0
   4551 E5            [11]  129 	push	hl
   4552 C5            [11]  130 	push	bc
   4553 CD C7 46      [17]  131 	call	_cpct_drawStringM0
                            132 ;src/main.c:66: pvideomem = cpct_getScreenPtr(CPCT_VMEM_START,  0, 34);
   4556 21 00 22      [10]  133 	ld	hl, #0x2200
   4559 E5            [11]  134 	push	hl
   455A 26 C0         [ 7]  135 	ld	h, #0xc0
   455C E5            [11]  136 	push	hl
   455D CD 5F 49      [17]  137 	call	_cpct_getScreenPtr
                            138 ;src/main.c:67: cpct_setDrawCharM0(4, 0);
   4560 E5            [11]  139 	push	hl
   4561 01 04 00      [10]  140 	ld	bc, #0x0004
   4564 C5            [11]  141 	push	bc
   4565 CD 3A 49      [17]  142 	call	_cpct_setDrawCharM0
   4568 E1            [10]  143 	pop	hl
                            144 ;src/main.c:68: cpct_drawStringM0("[Cursor]",   pvideomem);
   4569 01 A3 45      [10]  145 	ld	bc, #___str_1+0
   456C E5            [11]  146 	push	hl
   456D C5            [11]  147 	push	bc
   456E CD C7 46      [17]  148 	call	_cpct_drawStringM0
                            149 ;src/main.c:69: pvideomem = cpct_getScreenPtr(CPCT_VMEM_START, 40, 34);
   4571 21 28 22      [10]  150 	ld	hl, #0x2228
   4574 E5            [11]  151 	push	hl
   4575 21 00 C0      [10]  152 	ld	hl, #0xc000
   4578 E5            [11]  153 	push	hl
   4579 CD 5F 49      [17]  154 	call	_cpct_getScreenPtr
                            155 ;src/main.c:70: cpct_setDrawCharM0(3, 0);
   457C E5            [11]  156 	push	hl
   457D 01 03 00      [10]  157 	ld	bc, #0x0003
   4580 C5            [11]  158 	push	bc
   4581 CD 3A 49      [17]  159 	call	_cpct_setDrawCharM0
   4584 E1            [10]  160 	pop	hl
                            161 ;src/main.c:71: cpct_drawStringM0("Left/Right", pvideomem);
   4585 01 AC 45      [10]  162 	ld	bc, #___str_2+0
   4588 E5            [11]  163 	push	hl
   4589 C5            [11]  164 	push	bc
   458A CD C7 46      [17]  165 	call	_cpct_drawStringM0
   458D C9            [10]  166 	ret
   458E                     167 ___str_0:
   458E 20 20 53 70 72 69   168 	.ascii "  Sprite Flip Demo  "
        74 65 20 46 6C 69
        70 20 44 65 6D 6F
        20 20
   45A2 00                  169 	.db 0x00
   45A3                     170 ___str_1:
   45A3 5B 43 75 72 73 6F   171 	.ascii "[Cursor]"
        72 5D
   45AB 00                  172 	.db 0x00
   45AC                     173 ___str_2:
   45AC 4C 65 66 74 2F 52   174 	.ascii "Left/Right"
        69 67 68 74
   45B6 00                  175 	.db 0x00
                            176 ;src/main.c:77: void main(void) {
                            177 ;	---------------------------------
                            178 ; Function main
                            179 ; ---------------------------------
   45B7                     180 _main::
   45B7 DD E5         [15]  181 	push	ix
   45B9 DD 21 00 00   [14]  182 	ld	ix,#0
   45BD DD 39         [15]  183 	add	ix,sp
   45BF 3B            [ 6]  184 	dec	sp
                            185 ;src/main.c:78: u8 x=20;                     // Sprite horizontal coordinate
   45C0 0E 14         [ 7]  186 	ld	c, #0x14
                            187 ;src/main.c:79: u8 lookingAt = LOOK_RIGHT;   // Know where the sprite is looking at 
   45C2 DD 36 FF 01   [19]  188 	ld	-1 (ix), #0x01
                            189 ;src/main.c:80: u8 nowLookingAt = lookingAt; // New looking direction after keypress
   45C6 06 01         [ 7]  190 	ld	b, #0x01
                            191 ;src/main.c:83: initialize();
   45C8 C5            [11]  192 	push	bc
   45C9 CD E2 44      [17]  193 	call	_initialize
   45CC C1            [10]  194 	pop	bc
                            195 ;src/main.c:88: while(1) {
   45CD                     196 00111$:
                            197 ;src/main.c:94: cpct_scanKeyboard_f();
   45CD C5            [11]  198 	push	bc
   45CE CD 51 46      [17]  199 	call	_cpct_scanKeyboard_f
   45D1 21 00 02      [10]  200 	ld	hl, #0x0200
   45D4 CD 45 46      [17]  201 	call	_cpct_isKeyPressed
   45D7 C1            [10]  202 	pop	bc
   45D8 7D            [ 4]  203 	ld	a, l
   45D9 B7            [ 4]  204 	or	a, a
   45DA 28 0A         [12]  205 	jr	Z,00105$
   45DC 79            [ 4]  206 	ld	a, c
   45DD D6 39         [ 7]  207 	sub	a, #0x39
   45DF 30 05         [12]  208 	jr	NC,00105$
                            209 ;src/main.c:99: ++x;
   45E1 0C            [ 4]  210 	inc	c
                            211 ;src/main.c:100: nowLookingAt = LOOK_RIGHT;
   45E2 06 01         [ 7]  212 	ld	b, #0x01
   45E4 18 13         [12]  213 	jr	00106$
   45E6                     214 00105$:
                            215 ;src/main.c:101: } else if (cpct_isKeyPressed(Key_CursorLeft)  && x > 0) {
   45E6 C5            [11]  216 	push	bc
   45E7 21 01 01      [10]  217 	ld	hl, #0x0101
   45EA CD 45 46      [17]  218 	call	_cpct_isKeyPressed
   45ED C1            [10]  219 	pop	bc
   45EE 7D            [ 4]  220 	ld	a, l
   45EF B7            [ 4]  221 	or	a, a
   45F0 28 07         [12]  222 	jr	Z,00106$
   45F2 79            [ 4]  223 	ld	a, c
   45F3 B7            [ 4]  224 	or	a, a
   45F4 28 03         [12]  225 	jr	Z,00106$
                            226 ;src/main.c:102: --x; 
   45F6 0D            [ 4]  227 	dec	c
                            228 ;src/main.c:103: nowLookingAt = LOOK_LEFT;
   45F7 06 00         [ 7]  229 	ld	b, #0x00
   45F9                     230 00106$:
                            231 ;src/main.c:107: if (lookingAt != nowLookingAt) {
   45F9 DD 7E FF      [19]  232 	ld	a, -1 (ix)
   45FC 90            [ 4]  233 	sub	a, b
   45FD 28 10         [12]  234 	jr	Z,00109$
                            235 ;src/main.c:108: lookingAt = nowLookingAt;
   45FF DD 70 FF      [19]  236 	ld	-1 (ix), b
                            237 ;src/main.c:109: cpct_hflipSpriteM0(SP_W, SP_H, g_spirit);
   4602 C5            [11]  238 	push	bc
   4603 21 08 40      [10]  239 	ld	hl, #_g_spirit
   4606 E5            [11]  240 	push	hl
   4607 21 17 36      [10]  241 	ld	hl, #0x3617
   460A E5            [11]  242 	push	hl
   460B CD 14 48      [17]  243 	call	_cpct_hflipSpriteM0
   460E C1            [10]  244 	pop	bc
   460F                     245 00109$:
                            246 ;src/main.c:113: pvideomem = cpct_getScreenPtr(CPCT_VMEM_START, x, FLOOR_Y - SP_H);
   460F C5            [11]  247 	push	bc
   4610 06 6A         [ 7]  248 	ld	b, #0x6a
   4612 C5            [11]  249 	push	bc
   4613 21 00 C0      [10]  250 	ld	hl, #0xc000
   4616 E5            [11]  251 	push	hl
   4617 CD 5F 49      [17]  252 	call	_cpct_getScreenPtr
   461A EB            [ 4]  253 	ex	de,hl
   461B 21 17 36      [10]  254 	ld	hl, #0x3617
   461E E5            [11]  255 	push	hl
   461F D5            [11]  256 	push	de
   4620 21 08 40      [10]  257 	ld	hl, #_g_spirit
   4623 E5            [11]  258 	push	hl
   4624 CD 65 47      [17]  259 	call	_cpct_drawSprite
   4627 C1            [10]  260 	pop	bc
   4628 18 A3         [12]  261 	jr	00111$
   462A 33            [ 6]  262 	inc	sp
   462B DD E1         [14]  263 	pop	ix
   462D C9            [10]  264 	ret
                            265 	.area _CODE
                            266 	.area _INITIALIZER
                            267 	.area _CABS (ABS)
