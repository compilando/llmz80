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
                             12 	.globl _changeVideoMemoryPage
                             13 	.globl _cpct_getScreenPtr
                             14 	.globl _cpct_setVideoMemoryPage
                             15 	.globl _cpct_setPALColour
                             16 	.globl _cpct_setPalette
                             17 	.globl _cpct_fw2hw
                             18 	.globl _cpct_waitVSYNC
                             19 	.globl _cpct_setVideoMode
                             20 	.globl _cpct_drawSprite
                             21 	.globl _cpct_memset
                             22 	.globl _cpct_disableFirmware
                             23 ;--------------------------------------------------------
                             24 ; special function registers
                             25 ;--------------------------------------------------------
                             26 ;--------------------------------------------------------
                             27 ; ram data
                             28 ;--------------------------------------------------------
                             29 	.area _DATA
   3669                      30 _changeVideoMemoryPage_cycles_1_129:
   3669                      31 	.ds 1
   366A                      32 _changeVideoMemoryPage_page_1_129:
   366A                      33 	.ds 1
                             34 ;--------------------------------------------------------
                             35 ; ram data
                             36 ;--------------------------------------------------------
                             37 	.area _INITIALIZED
                             38 ;--------------------------------------------------------
                             39 ; absolute external ram data
                             40 ;--------------------------------------------------------
                             41 	.area _DABS (ABS)
                             42 ;--------------------------------------------------------
                             43 ; global & static initialisations
                             44 ;--------------------------------------------------------
                             45 	.area _HOME
                             46 	.area _GSINIT
                             47 	.area _GSFINAL
                             48 	.area _GSINIT
                             49 ;src/main.c:45: static u8 cycles = 0;   // Static value to count the number of times this function has been called
   366B FD 21 69 36   [14]   50 	ld	iy, #_changeVideoMemoryPage_cycles_1_129
   366F FD 36 00 00   [19]   51 	ld	0 (iy), #0x00
                             52 ;src/main.c:46: static u8 page   = 0;   // Static value to remember the last page shown (0 = page 40, 1 = page C0)
   3673 FD 21 6A 36   [14]   53 	ld	iy, #_changeVideoMemoryPage_page_1_129
   3677 FD 36 00 00   [19]   54 	ld	0 (iy), #0x00
                             55 ;--------------------------------------------------------
                             56 ; Home
                             57 ;--------------------------------------------------------
                             58 	.area _HOME
                             59 	.area _HOME
                             60 ;--------------------------------------------------------
                             61 ; code
                             62 ;--------------------------------------------------------
                             63 	.area _CODE
                             64 ;src/main.c:44: void changeVideoMemoryPage(u8 waitcycles) {
                             65 ;	---------------------------------
                             66 ; Function changeVideoMemoryPage
                             67 ; ---------------------------------
   0040                      68 _changeVideoMemoryPage::
                             69 ;src/main.c:49: if (++cycles >= waitcycles) {     
   0040 FD 21 69 36   [14]   70 	ld	iy, #_changeVideoMemoryPage_cycles_1_129
   0044 FD 34 00      [23]   71 	inc	0 (iy)
   0047 21 02 00      [10]   72 	ld	hl, #2
   004A 39            [11]   73 	add	hl, sp
   004B FD 7E 00      [19]   74 	ld	a, 0 (iy)
   004E 96            [ 7]   75 	sub	a, (hl)
   004F D8            [11]   76 	ret	C
                             77 ;src/main.c:50: cycles = 0;    // We have arrived, restore count to 0
   0050 FD 36 00 00   [19]   78 	ld	0 (iy), #0x00
                             79 ;src/main.c:54: if (page) {
   0054 3A 6A 36      [13]   80 	ld	a,(#_changeVideoMemoryPage_page_1_129 + 0)
   0057 B7            [ 4]   81 	or	a, a
   0058 28 0B         [12]   82 	jr	Z,00102$
                             83 ;src/main.c:55: cpct_setVideoMemoryPage(cpct_pageC0);  // Set video memory at banck 3 (0xC000 - 0xFFFF)
   005A 2E 30         [ 7]   84 	ld	l, #0x30
   005C CD FA 35      [17]   85 	call	_cpct_setVideoMemoryPage
                             86 ;src/main.c:56: page = 0;                              // Next page = 0
   005F 21 6A 36      [10]   87 	ld	hl,#_changeVideoMemoryPage_page_1_129 + 0
   0062 36 00         [10]   88 	ld	(hl), #0x00
   0064 C9            [10]   89 	ret
   0065                      90 00102$:
                             91 ;src/main.c:58: cpct_setVideoMemoryPage(cpct_page40);  // Set video memory at banck 1 (0x4000 - 0x7FFF)
   0065 2E 10         [ 7]   92 	ld	l, #0x10
   0067 CD FA 35      [17]   93 	call	_cpct_setVideoMemoryPage
                             94 ;src/main.c:59: page = 1;                              // Next page = 1
   006A 21 6A 36      [10]   95 	ld	hl,#_changeVideoMemoryPage_page_1_129 + 0
   006D 36 01         [10]   96 	ld	(hl), #0x01
   006F C9            [10]   97 	ret
                             98 ;src/main.c:69: void main(void) {
                             99 ;	---------------------------------
                            100 ; Function main
                            101 ; ---------------------------------
   0070                     102 _main::
   0070 DD E5         [15]  103 	push	ix
   0072 DD 21 00 00   [14]  104 	ld	ix,#0
   0076 DD 39         [15]  105 	add	ix,sp
   0078 F5            [11]  106 	push	af
                            107 ;src/main.c:70: u8  br_y = 55; // Y coordinate of the ByteRealms Logo 
   0079 DD 36 FF 37   [19]  108 	ld	-1 (ix), #0x37
                            109 ;src/main.c:71: i8  vy   = 1;  // Velocity of the ByteRealms Logo in Y axis
   007D DD 36 FE 01   [19]  110 	ld	-2 (ix), #0x01
                            111 ;src/main.c:75: cpct_disableFirmware();             // Disable firmware to prevent it from interfering
   0081 CD 42 36      [17]  112 	call	_cpct_disableFirmware
                            113 ;src/main.c:76: cpct_fw2hw       (G_palette, 16);   // Convert Firmware colours to Hardware colours 
   0084 21 10 00      [10]  114 	ld	hl, #0x0010
   0087 E5            [11]  115 	push	hl
   0088 21 43 01      [10]  116 	ld	hl, #_G_palette
   008B E5            [11]  117 	push	hl
   008C CD E7 35      [17]  118 	call	_cpct_fw2hw
                            119 ;src/main.c:77: cpct_setPalette  (G_palette, 16);   // Set up palette using hardware colours
   008F 21 10 00      [10]  120 	ld	hl, #0x0010
   0092 E5            [11]  121 	push	hl
   0093 21 43 01      [10]  122 	ld	hl, #_G_palette
   0096 E5            [11]  123 	push	hl
   0097 CD 1F 35      [17]  124 	call	_cpct_setPalette
                            125 ;src/main.c:78: cpct_setBorder   (G_palette[0]);    // Set up the border to the background colour (white)
   009A 21 43 01      [10]  126 	ld	hl, #_G_palette + 0
   009D 46            [ 7]  127 	ld	b, (hl)
   009E C5            [11]  128 	push	bc
   009F 33            [ 6]  129 	inc	sp
   00A0 3E 10         [ 7]  130 	ld	a, #0x10
   00A2 F5            [11]  131 	push	af
   00A3 33            [ 6]  132 	inc	sp
   00A4 CD 36 35      [17]  133 	call	_cpct_setPALColour
                            134 ;src/main.c:79: cpct_setVideoMode(0);               // Change to Mode 0 (160x200, 16 colours)
   00A7 2E 00         [ 7]  135 	ld	l, #0x00
   00A9 CD 26 36      [17]  136 	call	_cpct_setVideoMode
                            137 ;src/main.c:82: cpct_memset(CPCT_VMEM_START, 0x00, 0x4000);
   00AC 21 00 40      [10]  138 	ld	hl, #0x4000
   00AF E5            [11]  139 	push	hl
   00B0 AF            [ 4]  140 	xor	a, a
   00B1 F5            [11]  141 	push	af
   00B2 33            [ 6]  142 	inc	sp
   00B3 26 C0         [ 7]  143 	ld	h, #0xc0
   00B5 E5            [11]  144 	push	hl
   00B6 CD 34 36      [17]  145 	call	_cpct_memset
                            146 ;src/main.c:83: cpct_memset(       SCR_BUFF, 0x00, 0x4000);
   00B9 21 00 40      [10]  147 	ld	hl, #0x4000
   00BC E5            [11]  148 	push	hl
   00BD AF            [ 4]  149 	xor	a, a
   00BE F5            [11]  150 	push	af
   00BF 33            [ 6]  151 	inc	sp
   00C0 2E 00         [ 7]  152 	ld	l, #0x00
   00C2 E5            [11]  153 	push	hl
   00C3 CD 34 36      [17]  154 	call	_cpct_memset
                            155 ;src/main.c:90: pvmem = cpct_getScreenPtr(SCR_BUFF, 0,   52);
   00C6 21 00 34      [10]  156 	ld	hl, #0x3400
   00C9 E5            [11]  157 	push	hl
   00CA 26 40         [ 7]  158 	ld	h, #0x40
   00CC E5            [11]  159 	push	hl
   00CD CD 53 36      [17]  160 	call	_cpct_getScreenPtr
   00D0 4D            [ 4]  161 	ld	c, l
   00D1 44            [ 4]  162 	ld	b, h
                            163 ;src/main.c:91: cpct_drawSprite(G_CPCt_left,  pvmem,          CPCT_W, CPCT_H);
   00D2 59            [ 4]  164 	ld	e, c
   00D3 50            [ 4]  165 	ld	d, b
   00D4 C5            [11]  166 	push	bc
   00D5 21 28 60      [10]  167 	ld	hl, #0x6028
   00D8 E5            [11]  168 	push	hl
   00D9 D5            [11]  169 	push	de
   00DA 21 1F 26      [10]  170 	ld	hl, #_G_CPCt_left
   00DD E5            [11]  171 	push	hl
   00DE CD 42 35      [17]  172 	call	_cpct_drawSprite
   00E1 C1            [10]  173 	pop	bc
                            174 ;src/main.c:92: cpct_drawSprite(G_CPCt_right, pvmem + CPCT_W, CPCT_W, CPCT_H);
   00E2 21 28 00      [10]  175 	ld	hl, #0x0028
   00E5 09            [11]  176 	add	hl, bc
   00E6 01 1F 17      [10]  177 	ld	bc, #_G_CPCt_right+0
   00E9 11 28 60      [10]  178 	ld	de, #0x6028
   00EC D5            [11]  179 	push	de
   00ED E5            [11]  180 	push	hl
   00EE C5            [11]  181 	push	bc
   00EF CD 42 35      [17]  182 	call	_cpct_drawSprite
                            183 ;src/main.c:97: while(1) {
   00F2                     184 00105$:
                            185 ;src/main.c:101: pvmem = cpct_getScreenPtr(CPCT_VMEM_START, 10, br_y);  // Locate sprite at (10,br_y) in Default Video Memory
   00F2 DD 56 FF      [19]  186 	ld	d, -1 (ix)
   00F5 1E 0A         [ 7]  187 	ld	e,#0x0a
   00F7 D5            [11]  188 	push	de
   00F8 21 00 C0      [10]  189 	ld	hl, #0xc000
   00FB E5            [11]  190 	push	hl
   00FC CD 53 36      [17]  191 	call	_cpct_getScreenPtr
                            192 ;src/main.c:102: cpct_drawSprite(G_BR, pvmem, BR_W, BR_H);       // Draw the sprite
   00FF 01 53 01      [10]  193 	ld	bc, #_G_BR+0
   0102 11 3E 5A      [10]  194 	ld	de, #0x5a3e
   0105 D5            [11]  195 	push	de
   0106 E5            [11]  196 	push	hl
   0107 C5            [11]  197 	push	bc
   0108 CD 42 35      [17]  198 	call	_cpct_drawSprite
                            199 ;src/main.c:106: changeVideoMemoryPage(125);
   010B 3E 7D         [ 7]  200 	ld	a, #0x7d
   010D F5            [11]  201 	push	af
   010E 33            [ 6]  202 	inc	sp
   010F CD 40 00      [17]  203 	call	_changeVideoMemoryPage
   0112 33            [ 6]  204 	inc	sp
                            205 ;src/main.c:109: br_y += vy;                            // Add current velocity to Y coordinate
   0113 DD 7E FF      [19]  206 	ld	a, -1 (ix)
   0116 DD 86 FE      [19]  207 	add	a, -2 (ix)
                            208 ;src/main.c:110: if ( br_y < 1 || br_y + BR_H > 199 )   // Check if it exceeds boundaries
   0119 DD 77 FF      [19]  209 	ld	-1 (ix), a
   011C D6 01         [ 7]  210 	sub	a, #0x01
   011E 38 17         [12]  211 	jr	C,00101$
   0120 DD 4E FF      [19]  212 	ld	c, -1 (ix)
   0123 06 00         [ 7]  213 	ld	b, #0x00
   0125 21 5A 00      [10]  214 	ld	hl, #0x005a
   0128 09            [11]  215 	add	hl, bc
   0129 3E C7         [ 7]  216 	ld	a, #0xc7
   012B BD            [ 4]  217 	cp	a, l
   012C 3E 00         [ 7]  218 	ld	a, #0x00
   012E 9C            [ 4]  219 	sbc	a, h
   012F E2 34 01      [10]  220 	jp	PO, 00117$
   0132 EE 80         [ 7]  221 	xor	a, #0x80
   0134                     222 00117$:
   0134 F2 3E 01      [10]  223 	jp	P, 00102$
   0137                     224 00101$:
                            225 ;src/main.c:111: vy = -vy;                           // When we exceed boundaries, we change velocity sense
   0137 AF            [ 4]  226 	xor	a, a
   0138 DD 96 FE      [19]  227 	sub	a, -2 (ix)
   013B DD 77 FE      [19]  228 	ld	-2 (ix), a
   013E                     229 00102$:
                            230 ;src/main.c:114: cpct_waitVSYNC();
   013E CD 1E 36      [17]  231 	call	_cpct_waitVSYNC
   0141 18 AF         [12]  232 	jr	00105$
                            233 	.area _CODE
                            234 	.area _INITIALIZER
                            235 	.area _CABS (ABS)
