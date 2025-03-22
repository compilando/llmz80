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
                             13 	.globl _getUserInput
                             14 	.globl _clearRockets
                             15 	.globl _drawRockets
                             16 	.globl _cpct_getScreenPtr
                             17 	.globl _cpct_setPALColour
                             18 	.globl _cpct_setPalette
                             19 	.globl _cpct_waitVSYNC
                             20 	.globl _cpct_setVideoMode
                             21 	.globl _cpct_drawSprite
                             22 	.globl _cpct_drawSolidBox
                             23 	.globl _cpct_drawSpriteVFlip
                             24 	.globl _cpct_getBottomLeftPtr
                             25 	.globl _cpct_isKeyPressed
                             26 	.globl _cpct_scanKeyboard_f
                             27 	.globl _cpct_disableFirmware
                             28 ;--------------------------------------------------------
                             29 ; special function registers
                             30 ;--------------------------------------------------------
                             31 ;--------------------------------------------------------
                             32 ; ram data
                             33 ;--------------------------------------------------------
                             34 	.area _DATA
                             35 ;--------------------------------------------------------
                             36 ; ram data
                             37 ;--------------------------------------------------------
                             38 	.area _INITIALIZED
                             39 ;--------------------------------------------------------
                             40 ; absolute external ram data
                             41 ;--------------------------------------------------------
                             42 	.area _DABS (ABS)
                             43 ;--------------------------------------------------------
                             44 ; global & static initialisations
                             45 ;--------------------------------------------------------
                             46 	.area _HOME
                             47 	.area _GSINIT
                             48 	.area _GSFINAL
                             49 	.area _GSINIT
                             50 ;--------------------------------------------------------
                             51 ; Home
                             52 ;--------------------------------------------------------
                             53 	.area _HOME
                             54 	.area _HOME
                             55 ;--------------------------------------------------------
                             56 ; code
                             57 ;--------------------------------------------------------
                             58 	.area _CODE
                             59 ;src/main.c:37: void drawRockets(u8 x, u8 y) {
                             60 ;	---------------------------------
                             61 ; Function drawRockets
                             62 ; ---------------------------------
   4048                      63 _drawRockets::
   4048 DD E5         [15]   64 	push	ix
   404A DD 21 00 00   [14]   65 	ld	ix,#0
   404E DD 39         [15]   66 	add	ix,sp
                             67 ;src/main.c:43: pvmem = cpct_getScreenPtr(CPCT_VMEM_START, x, y);
   4050 DD 66 05      [19]   68 	ld	h, 5 (ix)
   4053 DD 6E 04      [19]   69 	ld	l, 4 (ix)
   4056 E5            [11]   70 	push	hl
   4057 21 00 C0      [10]   71 	ld	hl, #0xc000
   405A E5            [11]   72 	push	hl
   405B CD E5 43      [17]   73 	call	_cpct_getScreenPtr
   405E 4D            [ 4]   74 	ld	c, l
   405F 44            [ 4]   75 	ld	b, h
                             76 ;src/main.c:45: cpct_drawSprite(g_rocket, pvmem, G_ROCKET_W, G_ROCKET_H);
   4060 C5            [11]   77 	push	bc
   4061 21 04 0E      [10]   78 	ld	hl, #0x0e04
   4064 E5            [11]   79 	push	hl
   4065 C5            [11]   80 	push	bc
   4066 21 10 40      [10]   81 	ld	hl, #_g_rocket
   4069 E5            [11]   82 	push	hl
   406A CD 15 42      [17]   83 	call	_cpct_drawSprite
   406D C1            [10]   84 	pop	bc
                             85 ;src/main.c:52: pvmem = cpct_getBottomLeftPtr(pvmem, G_ROCKET_H);
   406E 21 0E 00      [10]   86 	ld	hl, #0x000e
   4071 E5            [11]   87 	push	hl
   4072 C5            [11]   88 	push	bc
   4073 CD C4 42      [17]   89 	call	_cpct_getBottomLeftPtr
                             90 ;src/main.c:56: pvmem += G_ROCKET_W + 1;
   4076 01 05 00      [10]   91 	ld	bc, #0x0005
   4079 09            [11]   92 	add	hl, bc
                             93 ;src/main.c:60: cpct_drawSpriteVFlip(g_rocket, pvmem, G_ROCKET_W, G_ROCKET_H);  
   407A 01 04 0E      [10]   94 	ld	bc, #0x0e04
   407D C5            [11]   95 	push	bc
   407E E5            [11]   96 	push	hl
   407F 21 10 40      [10]   97 	ld	hl, #_g_rocket
   4082 E5            [11]   98 	push	hl
   4083 CD EC 42      [17]   99 	call	_cpct_drawSpriteVFlip
   4086 DD E1         [14]  100 	pop	ix
   4088 C9            [10]  101 	ret
                            102 ;src/main.c:70: void clearRockets(u8 x, u8 y) {
                            103 ;	---------------------------------
                            104 ; Function clearRockets
                            105 ; ---------------------------------
   4089                     106 _clearRockets::
                            107 ;src/main.c:76: pvmem = cpct_getScreenPtr(CPCT_VMEM_START, x, y);
   4089 21 03 00      [10]  108 	ld	hl, #3+0
   408C 39            [11]  109 	add	hl, sp
   408D 7E            [ 7]  110 	ld	a, (hl)
   408E F5            [11]  111 	push	af
   408F 33            [ 6]  112 	inc	sp
   4090 21 03 00      [10]  113 	ld	hl, #3+0
   4093 39            [11]  114 	add	hl, sp
   4094 7E            [ 7]  115 	ld	a, (hl)
   4095 F5            [11]  116 	push	af
   4096 33            [ 6]  117 	inc	sp
   4097 21 00 C0      [10]  118 	ld	hl, #0xc000
   409A E5            [11]  119 	push	hl
   409B CD E5 43      [17]  120 	call	_cpct_getScreenPtr
                            121 ;src/main.c:80: cpct_drawSolidBox(pvmem, cpctm_px2byteM0(0, 0), 2*G_ROCKET_W+1, G_ROCKET_H);
   409E 01 09 0E      [10]  122 	ld	bc, #0x0e09
   40A1 C5            [11]  123 	push	bc
   40A2 01 00 00      [10]  124 	ld	bc, #0x0000
   40A5 C5            [11]  125 	push	bc
   40A6 E5            [11]  126 	push	hl
   40A7 CD 3D 43      [17]  127 	call	_cpct_drawSolidBox
   40AA C9            [10]  128 	ret
                            129 ;src/main.c:88: void getUserInput(i8* vx, i8* vy) {
                            130 ;	---------------------------------
                            131 ; Function getUserInput
                            132 ; ---------------------------------
   40AB                     133 _getUserInput::
   40AB DD E5         [15]  134 	push	ix
   40AD DD 21 00 00   [14]  135 	ld	ix,#0
   40B1 DD 39         [15]  136 	add	ix,sp
                            137 ;src/main.c:90: *vx = *vy = 0;
   40B3 DD 5E 04      [19]  138 	ld	e,4 (ix)
   40B6 DD 56 05      [19]  139 	ld	d,5 (ix)
   40B9 DD 4E 06      [19]  140 	ld	c,6 (ix)
   40BC DD 46 07      [19]  141 	ld	b,7 (ix)
   40BF AF            [ 4]  142 	xor	a, a
   40C0 02            [ 7]  143 	ld	(bc), a
   40C1 AF            [ 4]  144 	xor	a, a
   40C2 12            [ 7]  145 	ld	(de), a
                            146 ;src/main.c:93: cpct_scanKeyboard_f();
   40C3 C5            [11]  147 	push	bc
   40C4 D5            [11]  148 	push	de
   40C5 CD 9F 41      [17]  149 	call	_cpct_scanKeyboard_f
   40C8 21 04 04      [10]  150 	ld	hl, #0x0404
   40CB CD 93 41      [17]  151 	call	_cpct_isKeyPressed
   40CE D1            [10]  152 	pop	de
   40CF C1            [10]  153 	pop	bc
   40D0 7D            [ 4]  154 	ld	a, l
   40D1 B7            [ 4]  155 	or	a, a
   40D2 28 04         [12]  156 	jr	Z,00102$
   40D4 1A            [ 7]  157 	ld	a, (de)
   40D5 C6 FF         [ 7]  158 	add	a, #0xff
   40D7 12            [ 7]  159 	ld	(de), a
   40D8                     160 00102$:
                            161 ;src/main.c:98: if ( cpct_isKeyPressed(Key_P) ) (*vx)++;  // P: Right
   40D8 C5            [11]  162 	push	bc
   40D9 D5            [11]  163 	push	de
   40DA 21 03 08      [10]  164 	ld	hl, #0x0803
   40DD CD 93 41      [17]  165 	call	_cpct_isKeyPressed
   40E0 D1            [10]  166 	pop	de
   40E1 C1            [10]  167 	pop	bc
   40E2 7D            [ 4]  168 	ld	a, l
   40E3 B7            [ 4]  169 	or	a, a
   40E4 28 03         [12]  170 	jr	Z,00104$
   40E6 1A            [ 7]  171 	ld	a, (de)
   40E7 3C            [ 4]  172 	inc	a
   40E8 12            [ 7]  173 	ld	(de), a
   40E9                     174 00104$:
                            175 ;src/main.c:99: if ( cpct_isKeyPressed(Key_Q) ) (*vy)--;  // Q: Up
   40E9 C5            [11]  176 	push	bc
   40EA 21 08 08      [10]  177 	ld	hl, #0x0808
   40ED CD 93 41      [17]  178 	call	_cpct_isKeyPressed
   40F0 C1            [10]  179 	pop	bc
   40F1 7D            [ 4]  180 	ld	a, l
   40F2 B7            [ 4]  181 	or	a, a
   40F3 28 04         [12]  182 	jr	Z,00106$
   40F5 0A            [ 7]  183 	ld	a, (bc)
   40F6 C6 FF         [ 7]  184 	add	a, #0xff
   40F8 02            [ 7]  185 	ld	(bc), a
   40F9                     186 00106$:
                            187 ;src/main.c:100: if ( cpct_isKeyPressed(Key_A) ) (*vy)++;  // A: Down
   40F9 C5            [11]  188 	push	bc
   40FA 21 08 20      [10]  189 	ld	hl, #0x2008
   40FD CD 93 41      [17]  190 	call	_cpct_isKeyPressed
   4100 C1            [10]  191 	pop	bc
   4101 7D            [ 4]  192 	ld	a, l
   4102 B7            [ 4]  193 	or	a, a
   4103 28 03         [12]  194 	jr	Z,00109$
   4105 0A            [ 7]  195 	ld	a, (bc)
   4106 3C            [ 4]  196 	inc	a
   4107 02            [ 7]  197 	ld	(bc), a
   4108                     198 00109$:
   4108 DD E1         [14]  199 	pop	ix
   410A C9            [10]  200 	ret
                            201 ;src/main.c:107: void initialize() {
                            202 ;	---------------------------------
                            203 ; Function initialize
                            204 ; ---------------------------------
   410B                     205 _initialize::
                            206 ;src/main.c:108: cpct_disableFirmware();          // Disable firmware to prevent it from restoring mode and palette
   410B CD 2D 43      [17]  207 	call	_cpct_disableFirmware
                            208 ;src/main.c:109: cpct_setVideoMode(0);            // Set video mode to 0 (160x200, 16 colours)
   410E 2E 00         [ 7]  209 	ld	l, #0x00
   4110 CD 1F 43      [17]  210 	call	_cpct_setVideoMode
                            211 ;src/main.c:110: cpct_setPalette(g_palette, 16);  // Set the palette using hardware values generated at rocket.h
   4113 21 10 00      [10]  212 	ld	hl, #0x0010
   4116 E5            [11]  213 	push	hl
   4117 21 00 40      [10]  214 	ld	hl, #_g_palette
   411A E5            [11]  215 	push	hl
   411B CD 7C 41      [17]  216 	call	_cpct_setPalette
                            217 ;src/main.c:111: cpct_setBorder(HW_BLACK);        // Set border colour to Black 
   411E 21 10 14      [10]  218 	ld	hl, #0x1410
   4121 E5            [11]  219 	push	hl
   4122 CD 09 42      [17]  220 	call	_cpct_setPALColour
   4125 C9            [10]  221 	ret
                            222 ;src/main.c:117: void main(void) {
                            223 ;	---------------------------------
                            224 ; Function main
                            225 ; ---------------------------------
   4126                     226 _main::
   4126 DD E5         [15]  227 	push	ix
   4128 DD 21 00 00   [14]  228 	ld	ix,#0
   412C DD 39         [15]  229 	add	ix,sp
   412E F5            [11]  230 	push	af
                            231 ;src/main.c:118: u8 x = INIT_X, y = INIT_Y;    // x, y coordinates
   412F 01 14 64      [10]  232 	ld	bc,#0x6414
                            233 ;src/main.c:119: i8 vx = 1, vy = 0;            // vx, vy velocity (vx not 0 to force initial drawing)
   4132 DD 36 FE 01   [19]  234 	ld	-2 (ix), #0x01
   4136 DD 36 FF 00   [19]  235 	ld	-1 (ix), #0x00
                            236 ;src/main.c:122: initialize();
   413A C5            [11]  237 	push	bc
   413B CD 0B 41      [17]  238 	call	_initialize
   413E C1            [10]  239 	pop	bc
                            240 ;src/main.c:125: while (1) {
   413F                     241 00105$:
                            242 ;src/main.c:129: cpct_waitVSYNC();
   413F C5            [11]  243 	push	bc
   4140 CD 17 43      [17]  244 	call	_cpct_waitVSYNC
   4143 C1            [10]  245 	pop	bc
                            246 ;src/main.c:135: if (vx || vy) {
   4144 DD 7E FE      [19]  247 	ld	a, -2 (ix)
   4147 B7            [ 4]  248 	or	a, a
   4148 20 06         [12]  249 	jr	NZ,00101$
   414A DD 7E FF      [19]  250 	ld	a, -1 (ix)
   414D B7            [ 4]  251 	or	a, a
   414E 28 18         [12]  252 	jr	Z,00102$
   4150                     253 00101$:
                            254 ;src/main.c:136: clearRockets(x, y);  // Clear Rockets
   4150 C5            [11]  255 	push	bc
   4151 C5            [11]  256 	push	bc
   4152 CD 89 40      [17]  257 	call	_clearRockets
   4155 F1            [10]  258 	pop	af
   4156 C1            [10]  259 	pop	bc
                            260 ;src/main.c:137: x += vx; y += vy;    // Update x,y coordinates according to velocity
   4157 79            [ 4]  261 	ld	a, c
   4158 DD 86 FE      [19]  262 	add	a, -2 (ix)
   415B 4F            [ 4]  263 	ld	c, a
   415C 78            [ 4]  264 	ld	a, b
   415D DD 86 FF      [19]  265 	add	a, -1 (ix)
   4160 47            [ 4]  266 	ld	b, a
                            267 ;src/main.c:138: drawRockets(x, y);   // Draw Rockets at their new location
   4161 C5            [11]  268 	push	bc
   4162 C5            [11]  269 	push	bc
   4163 CD 48 40      [17]  270 	call	_drawRockets
   4166 F1            [10]  271 	pop	af
   4167 C1            [10]  272 	pop	bc
   4168                     273 00102$:
                            274 ;src/main.c:142: getUserInput(&vx, &vy);
   4168 21 01 00      [10]  275 	ld	hl, #0x0001
   416B 39            [11]  276 	add	hl, sp
   416C EB            [ 4]  277 	ex	de,hl
   416D 21 00 00      [10]  278 	ld	hl, #0x0000
   4170 39            [11]  279 	add	hl, sp
   4171 C5            [11]  280 	push	bc
   4172 D5            [11]  281 	push	de
   4173 E5            [11]  282 	push	hl
   4174 CD AB 40      [17]  283 	call	_getUserInput
   4177 F1            [10]  284 	pop	af
   4178 F1            [10]  285 	pop	af
   4179 C1            [10]  286 	pop	bc
   417A 18 C3         [12]  287 	jr	00105$
                            288 	.area _CODE
                            289 	.area _INITIALIZER
                            290 	.area _CABS (ABS)
