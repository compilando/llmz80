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
                             12 	.globl _wait_frames
                             13 	.globl _setBlackPalette
                             14 	.globl _fade_out
                             15 	.globl _fade_in
                             16 	.globl _cpct_getScreenPtr
                             17 	.globl _cpct_setVideoMode
                             18 	.globl _cpct_drawSprite
                             19 	.globl _cpct_memset
                             20 	.globl _cpct_disableFirmware
                             21 ;--------------------------------------------------------
                             22 ; special function registers
                             23 ;--------------------------------------------------------
                             24 ;--------------------------------------------------------
                             25 ; ram data
                             26 ;--------------------------------------------------------
                             27 	.area _DATA
                             28 ;--------------------------------------------------------
                             29 ; ram data
                             30 ;--------------------------------------------------------
                             31 	.area _INITIALIZED
                             32 ;--------------------------------------------------------
                             33 ; absolute external ram data
                             34 ;--------------------------------------------------------
                             35 	.area _DABS (ABS)
                             36 ;--------------------------------------------------------
                             37 ; global & static initialisations
                             38 ;--------------------------------------------------------
                             39 	.area _HOME
                             40 	.area _GSINIT
                             41 	.area _GSFINAL
                             42 	.area _GSINIT
                             43 ;--------------------------------------------------------
                             44 ; Home
                             45 ;--------------------------------------------------------
                             46 	.area _HOME
                             47 	.area _HOME
                             48 ;--------------------------------------------------------
                             49 ; code
                             50 ;--------------------------------------------------------
                             51 	.area _CODE
                             52 ;src/main.c:29: void main(void) {
                             53 ;	---------------------------------
                             54 ; Function main
                             55 ; ---------------------------------
   0040                      56 _main::
   0040 DD E5         [15]   57 	push	ix
   0042 DD 21 00 00   [14]   58 	ld	ix,#0
   0046 DD 39         [15]   59 	add	ix,sp
   0048 21 EB FF      [10]   60 	ld	hl, #-21
   004B 39            [11]   61 	add	hl, sp
   004C F9            [ 6]   62 	ld	sp, hl
                             63 ;src/main.c:31: const TSprite img[3] = { 
   004D 21 01 00      [10]   64 	ld	hl, #0x0001
   0050 39            [11]   65 	add	hl, sp
   0051 01 E6 03      [10]   66 	ld	bc, #_G_Goku+0
   0054 71            [ 7]   67 	ld	(hl), c
   0055 23            [ 6]   68 	inc	hl
   0056 70            [ 7]   69 	ld	(hl), b
   0057 21 01 00      [10]   70 	ld	hl, #0x0001
   005A 39            [11]   71 	add	hl, sp
   005B 4D            [ 4]   72 	ld	c,l
   005C 44            [ 4]   73 	ld	b,h
   005D 23            [ 6]   74 	inc	hl
   005E 23            [ 6]   75 	inc	hl
   005F 36 1E         [10]   76 	ld	(hl), #0x1e
   0061 69            [ 4]   77 	ld	l, c
   0062 60            [ 4]   78 	ld	h, b
   0063 23            [ 6]   79 	inc	hl
   0064 23            [ 6]   80 	inc	hl
   0065 23            [ 6]   81 	inc	hl
   0066 36 4B         [10]   82 	ld	(hl), #0x4b
   0068 21 04 00      [10]   83 	ld	hl, #0x0004
   006B 09            [11]   84 	add	hl, bc
   006C 36 14         [10]   85 	ld	(hl), #0x14
   006E 21 05 00      [10]   86 	ld	hl, #0x0005
   0071 09            [11]   87 	add	hl, bc
   0072 36 31         [10]   88 	ld	(hl), #0x31
   0074 21 06 00      [10]   89 	ld	hl, #0x0006
   0077 09            [11]   90 	add	hl, bc
   0078 11 BA 07      [10]   91 	ld	de, #_G_Vegeta+0
   007B 73            [ 7]   92 	ld	(hl), e
   007C 23            [ 6]   93 	inc	hl
   007D 72            [ 7]   94 	ld	(hl), d
   007E 21 08 00      [10]   95 	ld	hl, #0x0008
   0081 09            [11]   96 	add	hl, bc
   0082 36 16         [10]   97 	ld	(hl), #0x16
   0084 21 09 00      [10]   98 	ld	hl, #0x0009
   0087 09            [11]   99 	add	hl, bc
   0088 36 3C         [10]  100 	ld	(hl), #0x3c
   008A 21 0A 00      [10]  101 	ld	hl, #0x000a
   008D 09            [11]  102 	add	hl, bc
   008E 36 24         [10]  103 	ld	(hl), #0x24
   0090 21 0B 00      [10]  104 	ld	hl, #0x000b
   0093 09            [11]  105 	add	hl, bc
   0094 36 50         [10]  106 	ld	(hl), #0x50
   0096 21 0C 00      [10]  107 	ld	hl, #0x000c
   0099 09            [11]  108 	add	hl, bc
   009A 11 FA 12      [10]  109 	ld	de, #_G_No13+0
   009D 73            [ 7]  110 	ld	(hl), e
   009E 23            [ 6]  111 	inc	hl
   009F 72            [ 7]  112 	ld	(hl), d
   00A0 21 0E 00      [10]  113 	ld	hl, #0x000e
   00A3 09            [11]  114 	add	hl, bc
   00A4 36 16         [10]  115 	ld	(hl), #0x16
   00A6 21 0F 00      [10]  116 	ld	hl, #0x000f
   00A9 09            [11]  117 	add	hl, bc
   00AA 36 3C         [10]  118 	ld	(hl), #0x3c
   00AC 21 10 00      [10]  119 	ld	hl, #0x0010
   00AF 09            [11]  120 	add	hl, bc
   00B0 36 24         [10]  121 	ld	(hl), #0x24
   00B2 21 11 00      [10]  122 	ld	hl, #0x0011
   00B5 09            [11]  123 	add	hl, bc
   00B6 36 50         [10]  124 	ld	(hl), #0x50
                            125 ;src/main.c:40: cpct_disableFirmware();   // Disable firmware to prevent it from interfering
   00B8 C5            [11]  126 	push	bc
   00B9 CD 3A 1F      [17]  127 	call	_cpct_disableFirmware
   00BC 2E 00         [ 7]  128 	ld	l, #0x00
   00BE CD 1E 1F      [17]  129 	call	_cpct_setVideoMode
   00C1 21 00 10      [10]  130 	ld	hl, #0x1000
   00C4 E5            [11]  131 	push	hl
   00C5 CD CC 03      [17]  132 	call	_setBlackPalette
   00C8 F1            [10]  133 	pop	af
   00C9 C1            [10]  134 	pop	bc
                            135 ;src/main.c:50: for(i=0; i < 3; ++i) {
   00CA                     136 00109$:
   00CA DD 36 EB 00   [19]  137 	ld	-21 (ix), #0x00
   00CE                     138 00105$:
                            139 ;src/main.c:51: cpct_clearScreen(0x00);   // Clear the screen filling it up with 0's
   00CE C5            [11]  140 	push	bc
   00CF 21 00 40      [10]  141 	ld	hl, #0x4000
   00D2 E5            [11]  142 	push	hl
   00D3 AF            [ 4]  143 	xor	a, a
   00D4 F5            [11]  144 	push	af
   00D5 33            [ 6]  145 	inc	sp
   00D6 26 C0         [ 7]  146 	ld	h, #0xc0
   00D8 E5            [11]  147 	push	hl
   00D9 CD 2C 1F      [17]  148 	call	_cpct_memset
   00DC C1            [10]  149 	pop	bc
                            150 ;src/main.c:54: pvmem = cpct_getScreenPtr(CPCT_VMEM_START, img[i].x, img[i].y);
   00DD DD 5E EB      [19]  151 	ld	e,-21 (ix)
   00E0 16 00         [ 7]  152 	ld	d,#0x00
   00E2 6B            [ 4]  153 	ld	l, e
   00E3 62            [ 4]  154 	ld	h, d
   00E4 29            [11]  155 	add	hl, hl
   00E5 19            [11]  156 	add	hl, de
   00E6 29            [11]  157 	add	hl, hl
   00E7 09            [11]  158 	add	hl,bc
   00E8 EB            [ 4]  159 	ex	de,hl
   00E9 D5            [11]  160 	push	de
   00EA FD E1         [14]  161 	pop	iy
   00EC FD 7E 03      [19]  162 	ld	a, 3 (iy)
   00EF DD 77 FF      [19]  163 	ld	-1 (ix), a
   00F2 6B            [ 4]  164 	ld	l, e
   00F3 62            [ 4]  165 	ld	h, d
   00F4 23            [ 6]  166 	inc	hl
   00F5 23            [ 6]  167 	inc	hl
   00F6 7E            [ 7]  168 	ld	a, (hl)
   00F7 DD 77 FE      [19]  169 	ld	-2 (ix), a
   00FA C5            [11]  170 	push	bc
   00FB D5            [11]  171 	push	de
   00FC DD 66 FF      [19]  172 	ld	h, -1 (ix)
   00FF DD 6E FE      [19]  173 	ld	l, -2 (ix)
   0102 E5            [11]  174 	push	hl
   0103 21 00 C0      [10]  175 	ld	hl, #0xc000
   0106 E5            [11]  176 	push	hl
   0107 CD 4B 1F      [17]  177 	call	_cpct_getScreenPtr
   010A D1            [10]  178 	pop	de
   010B C1            [10]  179 	pop	bc
   010C E5            [11]  180 	push	hl
   010D FD E1         [14]  181 	pop	iy
                            182 ;src/main.c:55: cpct_drawSprite(img[i].sprite, pvmem, img[i].w, img[i].h);
   010F 6B            [ 4]  183 	ld	l, e
   0110 62            [ 4]  184 	ld	h, d
   0111 23            [ 6]  185 	inc	hl
   0112 23            [ 6]  186 	inc	hl
   0113 23            [ 6]  187 	inc	hl
   0114 23            [ 6]  188 	inc	hl
   0115 23            [ 6]  189 	inc	hl
   0116 7E            [ 7]  190 	ld	a, (hl)
   0117 DD 77 FE      [19]  191 	ld	-2 (ix), a
   011A 6B            [ 4]  192 	ld	l, e
   011B 62            [ 4]  193 	ld	h, d
   011C 23            [ 6]  194 	inc	hl
   011D 23            [ 6]  195 	inc	hl
   011E 23            [ 6]  196 	inc	hl
   011F 23            [ 6]  197 	inc	hl
   0120 7E            [ 7]  198 	ld	a, (hl)
   0121 DD 77 FF      [19]  199 	ld	-1 (ix), a
   0124 EB            [ 4]  200 	ex	de,hl
   0125 5E            [ 7]  201 	ld	e, (hl)
   0126 23            [ 6]  202 	inc	hl
   0127 56            [ 7]  203 	ld	d, (hl)
   0128 C5            [11]  204 	push	bc
   0129 DD 66 FE      [19]  205 	ld	h, -2 (ix)
   012C DD 6E FF      [19]  206 	ld	l, -1 (ix)
   012F E5            [11]  207 	push	hl
   0130 FD E5         [15]  208 	push	iy
   0132 D5            [11]  209 	push	de
   0133 CD 71 1E      [17]  210 	call	_cpct_drawSprite
   0136 21 32 00      [10]  211 	ld	hl, #0x0032
   0139 E5            [11]  212 	push	hl
   013A CD 3A 1E      [17]  213 	call	_wait_frames
   013D 21 10 04      [10]  214 	ld	hl, #0x0410
   0140 E3            [19]  215 	ex	(sp),hl
   0141 AF            [ 4]  216 	xor	a, a
   0142 F5            [11]  217 	push	af
   0143 33            [ 6]  218 	inc	sp
   0144 21 0E 02      [10]  219 	ld	hl, #_G_rgb_palette
   0147 E5            [11]  220 	push	hl
   0148 CD 5C 02      [17]  221 	call	_fade_in
   014B F1            [10]  222 	pop	af
   014C 33            [ 6]  223 	inc	sp
   014D 21 64 00      [10]  224 	ld	hl,#0x0064
   0150 E3            [19]  225 	ex	(sp),hl
   0151 CD 3A 1E      [17]  226 	call	_wait_frames
   0154 21 10 04      [10]  227 	ld	hl, #0x0410
   0157 E3            [19]  228 	ex	(sp),hl
   0158 AF            [ 4]  229 	xor	a, a
   0159 F5            [11]  230 	push	af
   015A 33            [ 6]  231 	inc	sp
   015B 21 0E 02      [10]  232 	ld	hl, #_G_rgb_palette
   015E E5            [11]  233 	push	hl
   015F CD 16 03      [17]  234 	call	_fade_out
   0162 F1            [10]  235 	pop	af
   0163 F1            [10]  236 	pop	af
   0164 33            [ 6]  237 	inc	sp
   0165 C1            [10]  238 	pop	bc
                            239 ;src/main.c:50: for(i=0; i < 3; ++i) {
   0166 DD 34 EB      [23]  240 	inc	-21 (ix)
   0169 DD 7E EB      [19]  241 	ld	a, -21 (ix)
   016C D6 03         [ 7]  242 	sub	a, #0x03
   016E DA CE 00      [10]  243 	jp	C, 00105$
   0171 C3 CA 00      [10]  244 	jp	00109$
                            245 	.area _CODE
                            246 	.area _INITIALIZER
                            247 	.area _CABS (ABS)
