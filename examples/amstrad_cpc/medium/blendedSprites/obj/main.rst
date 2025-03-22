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
                             13 	.globl _performUserActions
                             14 	.globl _selectNextBlendMode
                             15 	.globl _selectNextItem
                             16 	.globl _updateKeyboardStatus
                             17 	.globl _drawUserInterfaceMessages
                             18 	.globl _drawUserInterfaceStatus
                             19 	.globl _drawBackground
                             20 	.globl _cpct_setPALColour
                             21 	.globl _cpct_setPalette
                             22 	.globl _cpct_setVideoMode
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
                             55 ;src/main.c:28: void selectNextItem() {
                             56 ;	---------------------------------
                             57 ; Function selectNextItem
                             58 ; ---------------------------------
   6BA9                      59 _selectNextItem::
                             60 ;src/main.c:31: if (++g_selectedItem >= G_NITEMS)
   6BA9 FD 21 27 6F   [14]   61 	ld	iy, #_g_selectedItem
   6BAD FD 34 00      [23]   62 	inc	0 (iy)
   6BB0 FD 7E 00      [19]   63 	ld	a, 0 (iy)
   6BB3 D6 04         [ 7]   64 	sub	a, #0x04
   6BB5 DA 50 69      [10]   65 	jp	C,_drawUserInterfaceStatus
                             66 ;src/main.c:32: g_selectedItem = 0;
   6BB8 FD 36 00 00   [19]   67 	ld	0 (iy), #0x00
                             68 ;src/main.c:35: drawUserInterfaceStatus();
   6BBC C3 50 69      [10]   69 	jp  _drawUserInterfaceStatus
                             70 ;src/main.c:42: void selectNextBlendMode() {
                             71 ;	---------------------------------
                             72 ; Function selectNextBlendMode
                             73 ; ---------------------------------
   6BBF                      74 _selectNextBlendMode::
                             75 ;src/main.c:45: if (++g_selectedBlendMode >= G_NBLENDMODES) 
   6BBF FD 21 28 6F   [14]   76 	ld	iy, #_g_selectedBlendMode
   6BC3 FD 34 00      [23]   77 	inc	0 (iy)
   6BC6 FD 7E 00      [19]   78 	ld	a, 0 (iy)
   6BC9 D6 09         [ 7]   79 	sub	a, #0x09
   6BCB DA 50 69      [10]   80 	jp	C,_drawUserInterfaceStatus
                             81 ;src/main.c:46: g_selectedBlendMode = 0;
   6BCE FD 36 00 00   [19]   82 	ld	0 (iy), #0x00
                             83 ;src/main.c:49: drawUserInterfaceStatus();
   6BD2 C3 50 69      [10]   84 	jp  _drawUserInterfaceStatus
                             85 ;src/main.c:56: void performUserActions() {
                             86 ;	---------------------------------
                             87 ; Function performUserActions
                             88 ; ---------------------------------
   6BD5                      89 _performUserActions::
                             90 ;src/main.c:63: for(i = 0; i < G_NKEYS; i++) {
   6BD5 11 0B 6B      [10]   91 	ld	de, #_g_keys+0
   6BD8 0E 00         [ 7]   92 	ld	c, #0x00
   6BDA                      93 00104$:
                             94 ;src/main.c:64: if (g_keys[i].status == KeySt_Pressed)
   6BDA 06 00         [ 7]   95 	ld	b,#0x00
   6BDC 69            [ 4]   96 	ld	l, c
   6BDD 60            [ 4]   97 	ld	h, b
   6BDE 29            [11]   98 	add	hl, hl
   6BDF 29            [11]   99 	add	hl, hl
   6BE0 09            [11]  100 	add	hl, bc
   6BE1 19            [11]  101 	add	hl, de
   6BE2 E5            [11]  102 	push	hl
   6BE3 FD E1         [14]  103 	pop	iy
   6BE5 FD E5         [15]  104 	push	iy
   6BE7 E1            [10]  105 	pop	hl
   6BE8 23            [ 6]  106 	inc	hl
   6BE9 23            [ 6]  107 	inc	hl
   6BEA 46            [ 7]  108 	ld	b, (hl)
   6BEB 10 0D         [13]  109 	djnz	00105$
                            110 ;src/main.c:65: g_keys[i].action();
   6BED FD 6E 03      [19]  111 	ld	l, 3 (iy)
   6BF0 FD 66 04      [19]  112 	ld	h, 4 (iy)
   6BF3 C5            [11]  113 	push	bc
   6BF4 D5            [11]  114 	push	de
   6BF5 CD 14 6E      [17]  115 	call	___sdcc_call_hl
   6BF8 D1            [10]  116 	pop	de
   6BF9 C1            [10]  117 	pop	bc
   6BFA                     118 00105$:
                            119 ;src/main.c:63: for(i = 0; i < G_NKEYS; i++) {
   6BFA 0C            [ 4]  120 	inc	c
   6BFB 79            [ 4]  121 	ld	a, c
   6BFC D6 04         [ 7]  122 	sub	a, #0x04
   6BFE 38 DA         [12]  123 	jr	C,00104$
   6C00 C9            [10]  124 	ret
                            125 ;src/main.c:73: void initialize (){ 
                            126 ;	---------------------------------
                            127 ; Function initialize
                            128 ; ---------------------------------
   6C01                     129 _initialize::
                            130 ;src/main.c:75: cpct_disableFirmware();
   6C01 CD 23 6E      [17]  131 	call	_cpct_disableFirmware
                            132 ;src/main.c:80: cpct_setPalette  (g_palette, G_NCOLOURS);
   6C04 21 0B 00      [10]  133 	ld	hl, #0x000b
   6C07 E5            [11]  134 	push	hl
   6C08 21 00 6B      [10]  135 	ld	hl, #_g_palette
   6C0B E5            [11]  136 	push	hl
   6C0C CD 3A 6C      [17]  137 	call	_cpct_setPalette
                            138 ;src/main.c:81: cpct_setBorder   (HW_BLACK);
   6C0F 21 10 14      [10]  139 	ld	hl, #0x1410
   6C12 E5            [11]  140 	push	hl
   6C13 CD 5D 6C      [17]  141 	call	_cpct_setPALColour
                            142 ;src/main.c:82: cpct_setVideoMode(0);
   6C16 2E 00         [ 7]  143 	ld	l, #0x00
   6C18 CD 15 6E      [17]  144 	call	_cpct_setVideoMode
                            145 ;src/main.c:85: drawUserInterfaceMessages();   
   6C1B CD C9 69      [17]  146 	call	_drawUserInterfaceMessages
                            147 ;src/main.c:86: drawBackground();
   6C1E CD 80 68      [17]  148 	call	_drawBackground
                            149 ;src/main.c:89: g_selectedItem      = 0;
   6C21 21 27 6F      [10]  150 	ld	hl,#_g_selectedItem + 0
   6C24 36 00         [10]  151 	ld	(hl), #0x00
                            152 ;src/main.c:90: g_selectedBlendMode = 0;
   6C26 21 28 6F      [10]  153 	ld	hl,#_g_selectedBlendMode + 0
   6C29 36 00         [10]  154 	ld	(hl), #0x00
                            155 ;src/main.c:91: drawUserInterfaceStatus();
   6C2B CD 50 69      [17]  156 	call	_drawUserInterfaceStatus
   6C2E C9            [10]  157 	ret
                            158 ;src/main.c:97: void main(void) {
                            159 ;	---------------------------------
                            160 ; Function main
                            161 ; ---------------------------------
   6C2F                     162 _main::
                            163 ;src/main.c:98: initialize();  // Initialize the Amstrad CPC, 
   6C2F CD 01 6C      [17]  164 	call	_initialize
                            165 ;src/main.c:102: while(1) {
   6C32                     166 00102$:
                            167 ;src/main.c:103: updateKeyboardStatus();
   6C32 CD 1F 6B      [17]  168 	call	_updateKeyboardStatus
                            169 ;src/main.c:104: performUserActions();
   6C35 CD D5 6B      [17]  170 	call	_performUserActions
   6C38 18 F8         [12]  171 	jr	00102$
                            172 	.area _CODE
                            173 	.area _INITIALIZER
                            174 	.area _CABS (ABS)
