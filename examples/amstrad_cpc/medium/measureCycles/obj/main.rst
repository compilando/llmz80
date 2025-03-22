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
                             12 	.globl _cpct_setPALColour
                             13 	.globl _cpct_setPalette
                             14 	.globl _cpct_fw2hw
                             15 	.globl _cpct_count2VSYNC
                             16 	.globl _cpct_waitVSYNC
                             17 	.globl _cpct_setVideoMode
                             18 	.globl _cpct_drawCharM1
                             19 	.globl _cpct_setDrawCharM1
                             20 	.globl _cpct_drawSprite
                             21 	.globl _cpct_isKeyPressed
                             22 	.globl _cpct_scanKeyboard_f
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
                             55 ;src/main.c:31: void main(void) {
                             56 ;	---------------------------------
                             57 ; Function main
                             58 ; ---------------------------------
   4000                      59 _main::
   4000 DD E5         [15]   60 	push	ix
   4002 DD 21 00 00   [14]   61 	ld	ix,#0
   4006 DD 39         [15]   62 	add	ix,sp
   4008 F5            [11]   63 	push	af
   4009 F5            [11]   64 	push	af
   400A 3B            [ 6]   65 	dec	sp
                             66 ;src/main.c:33: u8  x=0, y=0;                    // Sprite coordinates (in bytes)
   400B DD 36 FE 00   [19]   67 	ld	-2 (ix), #0x00
   400F DD 36 FD 00   [19]   68 	ld	-3 (ix), #0x00
                             69 ;src/main.c:34: u8* pvideomem = CPCT_VMEM_START; // Sprite initial video memory byte location (where it will be drawn)
   4013 21 00 C0      [10]   70 	ld	hl, #0xc000
   4016 E3            [19]   71 	ex	(sp), hl
                             72 ;src/main.c:39: cpct_disableFirmware();
   4017 CD D5 44      [17]   73 	call	_cpct_disableFirmware
                             74 ;src/main.c:41: cpct_fw2hw     (G_palette, 4);
   401A 21 04 00      [10]   75 	ld	hl, #0x0004
   401D E5            [11]   76 	push	hl
   401E 21 49 41      [10]   77 	ld	hl, #_G_palette
   4021 E5            [11]   78 	push	hl
   4022 CD 7B 44      [17]   79 	call	_cpct_fw2hw
                             80 ;src/main.c:42: cpct_setPalette(G_palette, 4);
   4025 21 04 00      [10]   81 	ld	hl, #0x0004
   4028 E5            [11]   82 	push	hl
   4029 21 49 41      [10]   83 	ld	hl, #_G_palette
   402C E5            [11]   84 	push	hl
   402D CD 1A 43      [17]   85 	call	_cpct_setPalette
                             86 ;src/main.c:43: cpct_setBorder (G_palette[1]);
   4030 21 4A 41      [10]   87 	ld	hl, #_G_palette + 1
   4033 46            [ 7]   88 	ld	b, (hl)
   4034 C5            [11]   89 	push	bc
   4035 33            [ 6]   90 	inc	sp
   4036 3E 10         [ 7]   91 	ld	a, #0x10
   4038 F5            [11]   92 	push	af
   4039 33            [ 6]   93 	inc	sp
   403A CD A7 43      [17]   94 	call	_cpct_setPALColour
                             95 ;src/main.c:44: cpct_setVideoMode(1);         // Ensure MODE 1 is set
   403D 2E 01         [ 7]   96 	ld	l, #0x01
   403F CD C7 44      [17]   97 	call	_cpct_setVideoMode
                             98 ;src/main.c:45: cpct_setDrawCharM1(3, 0);     // Always draw characters using same colours (3 (Yellow) / 0 (Grey))
   4042 21 03 00      [10]   99 	ld	hl, #0x0003
   4045 E5            [11]  100 	push	hl
   4046 CD E6 44      [17]  101 	call	_cpct_setDrawCharM1
                            102 ;src/main.c:48: while(1) {
   4049                     103 00117$:
                            104 ;src/main.c:50: cpct_scanKeyboard_f();
   4049 CD 3D 43      [17]  105 	call	_cpct_scanKeyboard_f
                            106 ;src/main.c:51: if      (cpct_isKeyPressed(Key_CursorRight) && x <  80 - SPR_W) { x++; pvideomem++; }
   404C 21 00 02      [10]  107 	ld	hl, #0x0200
   404F CD 31 43      [17]  108 	call	_cpct_isKeyPressed
   4052 7D            [ 4]  109 	ld	a, l
   4053 B7            [ 4]  110 	or	a, a
   4054 28 14         [12]  111 	jr	Z,00105$
   4056 DD 7E FE      [19]  112 	ld	a, -2 (ix)
   4059 D6 47         [ 7]  113 	sub	a, #0x47
   405B 30 0D         [12]  114 	jr	NC,00105$
   405D DD 34 FE      [23]  115 	inc	-2 (ix)
   4060 DD 34 FB      [23]  116 	inc	-5 (ix)
   4063 20 1C         [12]  117 	jr	NZ,00106$
   4065 DD 34 FC      [23]  118 	inc	-4 (ix)
   4068 18 17         [12]  119 	jr	00106$
   406A                     120 00105$:
                            121 ;src/main.c:52: else if (cpct_isKeyPressed(Key_CursorLeft)  && x >   0        ) { x--; pvideomem--; }
   406A 21 01 01      [10]  122 	ld	hl, #0x0101
   406D CD 31 43      [17]  123 	call	_cpct_isKeyPressed
   4070 7D            [ 4]  124 	ld	a, l
   4071 B7            [ 4]  125 	or	a, a
   4072 28 0D         [12]  126 	jr	Z,00106$
   4074 DD 7E FE      [19]  127 	ld	a, -2 (ix)
   4077 B7            [ 4]  128 	or	a, a
   4078 28 07         [12]  129 	jr	Z,00106$
   407A DD 35 FE      [23]  130 	dec	-2 (ix)
   407D E1            [10]  131 	pop	hl
   407E E5            [11]  132 	push	hl
   407F 2B            [ 6]  133 	dec	hl
   4080 E3            [19]  134 	ex	(sp), hl
   4081                     135 00106$:
                            136 ;src/main.c:53: if      (cpct_isKeyPressed(Key_CursorUp)    && y >   0        ) { pvideomem -= (y-- & 7) ? 0x0800 : 0xC850; }
   4081 21 00 01      [10]  137 	ld	hl, #0x0100
   4084 CD 31 43      [17]  138 	call	_cpct_isKeyPressed
   4087 7D            [ 4]  139 	ld	a, l
   4088 B7            [ 4]  140 	or	a, a
   4089 28 29         [12]  141 	jr	Z,00112$
   408B DD 7E FD      [19]  142 	ld	a, -3 (ix)
   408E B7            [ 4]  143 	or	a, a
   408F 28 23         [12]  144 	jr	Z,00112$
   4091 DD 4E FD      [19]  145 	ld	c, -3 (ix)
   4094 DD 35 FD      [23]  146 	dec	-3 (ix)
   4097 79            [ 4]  147 	ld	a, c
   4098 E6 07         [ 7]  148 	and	a, #0x07
   409A 28 05         [12]  149 	jr	Z,00123$
   409C 11 00 08      [10]  150 	ld	de, #0x0800
   409F 18 03         [12]  151 	jr	00124$
   40A1                     152 00123$:
   40A1 11 50 C8      [10]  153 	ld	de, #0xc850
   40A4                     154 00124$:
   40A4 DD 7E FB      [19]  155 	ld	a, -5 (ix)
   40A7 93            [ 4]  156 	sub	a, e
   40A8 DD 77 FB      [19]  157 	ld	-5 (ix), a
   40AB DD 7E FC      [19]  158 	ld	a, -4 (ix)
   40AE 9A            [ 4]  159 	sbc	a, d
   40AF DD 77 FC      [19]  160 	ld	-4 (ix), a
   40B2 18 31         [12]  161 	jr	00113$
   40B4                     162 00112$:
                            163 ;src/main.c:54: else if (cpct_isKeyPressed(Key_CursorDown)  && y < 200 - SPR_H) { pvideomem += (++y & 7) ? 0x0800 : 0xC850; }
   40B4 21 00 04      [10]  164 	ld	hl, #0x0400
   40B7 CD 31 43      [17]  165 	call	_cpct_isKeyPressed
   40BA 7D            [ 4]  166 	ld	a, l
   40BB B7            [ 4]  167 	or	a, a
   40BC 28 27         [12]  168 	jr	Z,00113$
   40BE DD 7E FD      [19]  169 	ld	a, -3 (ix)
   40C1 D6 9C         [ 7]  170 	sub	a, #0x9c
   40C3 30 20         [12]  171 	jr	NC,00113$
   40C5 DD 34 FD      [23]  172 	inc	-3 (ix)
   40C8 DD 7E FD      [19]  173 	ld	a, -3 (ix)
   40CB E6 07         [ 7]  174 	and	a, #0x07
   40CD 28 05         [12]  175 	jr	Z,00125$
   40CF 01 00 08      [10]  176 	ld	bc, #0x0800
   40D2 18 03         [12]  177 	jr	00126$
   40D4                     178 00125$:
   40D4 01 50 C8      [10]  179 	ld	bc, #0xc850
   40D7                     180 00126$:
   40D7 DD 7E FB      [19]  181 	ld	a, -5 (ix)
   40DA 81            [ 4]  182 	add	a, c
   40DB DD 77 FB      [19]  183 	ld	-5 (ix), a
   40DE DD 7E FC      [19]  184 	ld	a, -4 (ix)
   40E1 88            [ 4]  185 	adc	a, b
   40E2 DD 77 FC      [19]  186 	ld	-4 (ix), a
   40E5                     187 00113$:
                            188 ;src/main.c:58: cpct_waitVSYNC();
   40E5 CD BF 44      [17]  189 	call	_cpct_waitVSYNC
                            190 ;src/main.c:63: cpct_drawSprite(G_death, pvideomem, SPR_W, SPR_H);
   40E8 C1            [10]  191 	pop	bc
   40E9 C5            [11]  192 	push	bc
   40EA 21 09 2C      [10]  193 	ld	hl, #0x2c09
   40ED E5            [11]  194 	push	hl
   40EE C5            [11]  195 	push	bc
   40EF 21 4D 41      [10]  196 	ld	hl, #_G_death
   40F2 E5            [11]  197 	push	hl
   40F3 CD B3 43      [17]  198 	call	_cpct_drawSprite
                            199 ;src/main.c:69: ms = 14 + 9 * cpct_count2VSYNC();
   40F6 CD 8E 44      [17]  200 	call	_cpct_count2VSYNC
   40F9 4D            [ 4]  201 	ld	c, l
   40FA 44            [ 4]  202 	ld	b, h
   40FB 29            [11]  203 	add	hl, hl
   40FC 29            [11]  204 	add	hl, hl
   40FD 29            [11]  205 	add	hl, hl
   40FE 09            [11]  206 	add	hl, bc
   40FF 01 0E 00      [10]  207 	ld	bc, #0x000e
   4102 09            [11]  208 	add	hl, bc
                            209 ;src/main.c:75: for(i=0; i<5; i++) {
   4103 DD 36 FF 00   [19]  210 	ld	-1 (ix), #0x00
   4107                     211 00119$:
                            212 ;src/main.c:76: u8 digit = '0' + (ms % 10);
   4107 E5            [11]  213 	push	hl
   4108 01 0A 00      [10]  214 	ld	bc, #0x000a
   410B C5            [11]  215 	push	bc
   410C E5            [11]  216 	push	hl
   410D CD 46 45      [17]  217 	call	__moduint
   4110 F1            [10]  218 	pop	af
   4111 F1            [10]  219 	pop	af
   4112 4D            [ 4]  220 	ld	c, l
   4113 E1            [10]  221 	pop	hl
   4114 79            [ 4]  222 	ld	a, c
   4115 C6 30         [ 7]  223 	add	a, #0x30
   4117 4F            [ 4]  224 	ld	c, a
                            225 ;src/main.c:77: cpct_drawCharM1((void*)(LASTDIGIT_VMEM - 2*i), digit);
   4118 06 00         [ 7]  226 	ld	b, #0x00
   411A DD 5E FF      [19]  227 	ld	e, -1 (ix)
   411D 16 00         [ 7]  228 	ld	d, #0x00
   411F CB 23         [ 8]  229 	sla	e
   4121 CB 12         [ 8]  230 	rl	d
   4123 3E 4E         [ 7]  231 	ld	a, #0x4e
   4125 93            [ 4]  232 	sub	a, e
   4126 5F            [ 4]  233 	ld	e, a
   4127 3E C0         [ 7]  234 	ld	a, #0xc0
   4129 9A            [ 4]  235 	sbc	a, d
   412A 57            [ 4]  236 	ld	d, a
   412B E5            [11]  237 	push	hl
   412C C5            [11]  238 	push	bc
   412D D5            [11]  239 	push	de
   412E CD 58 44      [17]  240 	call	_cpct_drawCharM1
   4131 E1            [10]  241 	pop	hl
                            242 ;src/main.c:78: ms /= 10;
   4132 01 0A 00      [10]  243 	ld	bc, #0x000a
   4135 C5            [11]  244 	push	bc
   4136 E5            [11]  245 	push	hl
   4137 CD D9 42      [17]  246 	call	__divuint
   413A F1            [10]  247 	pop	af
   413B F1            [10]  248 	pop	af
                            249 ;src/main.c:75: for(i=0; i<5; i++) {
   413C DD 34 FF      [23]  250 	inc	-1 (ix)
   413F DD 7E FF      [19]  251 	ld	a, -1 (ix)
   4142 D6 05         [ 7]  252 	sub	a, #0x05
   4144 38 C1         [12]  253 	jr	C,00119$
   4146 C3 49 40      [10]  254 	jp	00117$
                            255 	.area _CODE
                            256 	.area _INITIALIZER
                            257 	.area _CABS (ABS)
