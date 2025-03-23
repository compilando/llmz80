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
                             12 	.globl _game
                             13 	.globl _initialize
                             14 	.globl _drawFrame
                             15 	.globl _drawBuidlingScrolled
                             16 	.globl _video_switchBuffers
                             17 	.globl _video_initBuffers
                             18 	.globl _video_getBackBufferPtr
                             19 	.globl _cpct_etm_drawTilemap4x8_ag
                             20 	.globl _cpct_etm_setDrawTilemap4x8_ag
                             21 	.globl _cpct_getScreenPtr
                             22 	.globl _cpct_setPALColour
                             23 	.globl _cpct_setPalette
                             24 	.globl _cpct_setVideoMode
                             25 	.globl _cpct_isKeyPressed
                             26 	.globl _cpct_scanKeyboard_f
                             27 	.globl _cpct_setStackLocation
                             28 	.globl _cpct_disableFirmware
                             29 ;--------------------------------------------------------
                             30 ; special function registers
                             31 ;--------------------------------------------------------
                             32 ;--------------------------------------------------------
                             33 ; ram data
                             34 ;--------------------------------------------------------
                             35 	.area _DATA
                             36 ;--------------------------------------------------------
                             37 ; ram data
                             38 ;--------------------------------------------------------
                             39 	.area _INITIALIZED
                             40 ;--------------------------------------------------------
                             41 ; absolute external ram data
                             42 ;--------------------------------------------------------
                             43 	.area _DABS (ABS)
                             44 ;--------------------------------------------------------
                             45 ; global & static initialisations
                             46 ;--------------------------------------------------------
                             47 	.area _HOME
                             48 	.area _GSINIT
                             49 	.area _GSFINAL
                             50 	.area _GSINIT
                             51 ;--------------------------------------------------------
                             52 ; Home
                             53 ;--------------------------------------------------------
                             54 	.area _HOME
                             55 	.area _HOME
                             56 ;--------------------------------------------------------
                             57 ; code
                             58 ;--------------------------------------------------------
                             59 	.area _CODE
                             60 ;src/main.c:79: void drawBuidlingScrolled(u16 offset) {
                             61 ;	---------------------------------
                             62 ; Function drawBuidlingScrolled
                             63 ; ---------------------------------
   4864                      64 _drawBuidlingScrolled::
   4864 DD E5         [15]   65 	push	ix
   4866 DD 21 00 00   [14]   66 	ld	ix,#0
   486A DD 39         [15]   67 	add	ix,sp
                             68 ;src/main.c:84: u8* vmem = video_getBackBufferPtr() + VIEWPORT_OFFSET;
   486C CD A2 49      [17]   69 	call	_video_getBackBufferPtr
   486F 01 48 01      [10]   70 	ld	bc, #0x0148
   4872 09            [11]   71 	add	hl, bc
                             72 ;src/main.c:89: cpct_etm_drawTilemap4x8_ag(vmem, g_building + offset);
   4873 01 94 40      [10]   73 	ld	bc, #_g_building+0
   4876 DD 7E 04      [19]   74 	ld	a, 4 (ix)
   4879 81            [ 4]   75 	add	a, c
   487A 4F            [ 4]   76 	ld	c, a
   487B DD 7E 05      [19]   77 	ld	a, 5 (ix)
   487E 88            [ 4]   78 	adc	a, b
   487F 47            [ 4]   79 	ld	b, a
   4880 C5            [11]   80 	push	bc
   4881 E5            [11]   81 	push	hl
   4882 CD 79 4A      [17]   82 	call	_cpct_etm_drawTilemap4x8_ag
                             83 ;src/main.c:92: video_switchBuffers();
   4885 CD A6 49      [17]   84 	call	_video_switchBuffers
   4888 DD E1         [14]   85 	pop	ix
   488A C9            [10]   86 	ret
                             87 ;src/main.c:101: void drawFrame() {
                             88 ;	---------------------------------
                             89 ; Function drawFrame
                             90 ; ---------------------------------
   488B                      91 _drawFrame::
                             92 ;src/main.c:103: u8* vmem_buffer = video_getBackBufferPtr();  // Get present Hardware Back Buffer were we are going to draw
   488B CD A2 49      [17]   93 	call	_video_getBackBufferPtr
                             94 ;src/main.c:114: cpct_etm_setDrawTilemap4x8_ag (20, 4, g_frame_ud_W, g_tileset_00);
   488E E5            [11]   95 	push	hl
   488F 21 A4 44      [10]   96 	ld	hl, #_g_tileset_00
   4892 E5            [11]   97 	push	hl
   4893 21 15 00      [10]   98 	ld	hl, #0x0015
   4896 E5            [11]   99 	push	hl
   4897 21 14 04      [10]  100 	ld	hl, #0x0414
   489A E5            [11]  101 	push	hl
   489B CD 62 4B      [17]  102 	call	_cpct_etm_setDrawTilemap4x8_ag
   489E C1            [10]  103 	pop	bc
                            104 ;src/main.c:116: cpct_etm_drawTilemap4x8_ag    (vmem_buffer, g_frame_ud);
   489F 11 40 40      [10]  105 	ld	de, #_g_frame_ud
   48A2 C5            [11]  106 	push	bc
   48A3 D5            [11]  107 	push	de
   48A4 C5            [11]  108 	push	bc
   48A5 CD 79 4A      [17]  109 	call	_cpct_etm_drawTilemap4x8_ag
   48A8 C1            [10]  110 	pop	bc
                            111 ;src/main.c:123: vmem = cpct_getScreenPtr   (vmem_buffer,  0*TILE_W, 20*TILE_H);
   48A9 C5            [11]  112 	push	bc
   48AA 21 00 A0      [10]  113 	ld	hl, #0xa000
   48AD E5            [11]  114 	push	hl
   48AE C5            [11]  115 	push	bc
   48AF CD 92 4B      [17]  116 	call	_cpct_getScreenPtr
   48B2 C1            [10]  117 	pop	bc
                            118 ;src/main.c:126: cpct_etm_drawTilemap4x8_ag (vmem, g_frame_ud + 1);
   48B3 11 41 40      [10]  119 	ld	de, #_g_frame_ud + 1
   48B6 C5            [11]  120 	push	bc
   48B7 D5            [11]  121 	push	de
   48B8 E5            [11]  122 	push	hl
   48B9 CD 79 4A      [17]  123 	call	_cpct_etm_drawTilemap4x8_ag
   48BC 21 A4 44      [10]  124 	ld	hl, #_g_tileset_00
   48BF E5            [11]  125 	push	hl
   48C0 21 04 00      [10]  126 	ld	hl, #0x0004
   48C3 E5            [11]  127 	push	hl
   48C4 21 02 10      [10]  128 	ld	hl, #0x1002
   48C7 E5            [11]  129 	push	hl
   48C8 CD 62 4B      [17]  130 	call	_cpct_etm_setDrawTilemap4x8_ag
   48CB C1            [10]  131 	pop	bc
                            132 ;src/main.c:141: vmem = cpct_getScreenPtr   (vmem_buffer,  0*TILE_W, 4*TILE_H);
   48CC C5            [11]  133 	push	bc
   48CD 21 00 20      [10]  134 	ld	hl, #0x2000
   48D0 E5            [11]  135 	push	hl
   48D1 C5            [11]  136 	push	bc
   48D2 CD 92 4B      [17]  137 	call	_cpct_getScreenPtr
   48D5 EB            [ 4]  138 	ex	de,hl
   48D6 C1            [10]  139 	pop	bc
                            140 ;src/main.c:142: cpct_etm_drawTilemap4x8_ag (vmem, g_frame_lr);   
   48D7 21 00 40      [10]  141 	ld	hl, #_g_frame_lr
   48DA C5            [11]  142 	push	bc
   48DB E5            [11]  143 	push	hl
   48DC D5            [11]  144 	push	de
   48DD CD 79 4A      [17]  145 	call	_cpct_etm_drawTilemap4x8_ag
   48E0 C1            [10]  146 	pop	bc
                            147 ;src/main.c:145: vmem = cpct_getScreenPtr   (vmem_buffer, 18*TILE_W, 4*TILE_H);
   48E1 21 48 20      [10]  148 	ld	hl, #0x2048
   48E4 E5            [11]  149 	push	hl
   48E5 C5            [11]  150 	push	bc
   48E6 CD 92 4B      [17]  151 	call	_cpct_getScreenPtr
                            152 ;src/main.c:146: cpct_etm_drawTilemap4x8_ag (vmem, g_frame_lr + 2);
   48E9 01 02 40      [10]  153 	ld	bc, #_g_frame_lr + 2
   48EC C5            [11]  154 	push	bc
   48ED E5            [11]  155 	push	hl
   48EE CD 79 4A      [17]  156 	call	_cpct_etm_drawTilemap4x8_ag
   48F1 C9            [10]  157 	ret
                            158 ;src/main.c:154: void initialize() {
                            159 ;	---------------------------------
                            160 ; Function initialize
                            161 ; ---------------------------------
   48F2                     162 _initialize::
                            163 ;src/main.c:155: cpct_disableFirmware();          // We use own mode and colours, firmware must be disabled
   48F2 CD 51 4B      [17]  164 	call	_cpct_disableFirmware
                            165 ;src/main.c:156: cpct_setVideoMode(0);            // Set video mode 0 (160x200 pixels, 20x25 characters, 16 colours)
   48F5 2E 00         [ 7]  166 	ld	l, #0x00
   48F7 CD 35 4B      [17]  167 	call	_cpct_setVideoMode
                            168 ;src/main.c:157: cpct_setPalette(g_palette, 16);  // Set our own colours defined en g_palette (automatically generated in maps/tileset.c)
   48FA 21 10 00      [10]  169 	ld	hl, #0x0010
   48FD E5            [11]  170 	push	hl
   48FE 21 94 44      [10]  171 	ld	hl, #_g_palette
   4901 E5            [11]  172 	push	hl
   4902 CD E0 49      [17]  173 	call	_cpct_setPalette
                            174 ;src/main.c:158: cpct_setBorder(HW_BLUE);         // Set border same as background colour: BLUE
   4905 21 10 04      [10]  175 	ld	hl, #0x0410
   4908 E5            [11]  176 	push	hl
   4909 CD 6D 4A      [17]  177 	call	_cpct_setPALColour
                            178 ;src/main.c:164: video_initBuffers();    // Initialize screen video buffers
   490C CD CF 49      [17]  179 	call	_video_initBuffers
                            180 ;src/main.c:165: drawFrame();            // Draw a frame at the first selected screen buffer
   490F CD 8B 48      [17]  181 	call	_drawFrame
                            182 ;src/main.c:166: video_switchBuffers();  // Switch video buffers (current screen <--> current backbuffer)
   4912 CD A6 49      [17]  183 	call	_video_switchBuffers
                            184 ;src/main.c:167: drawFrame();            // Draw the same frame at the second screen buffer
   4915 CD 8B 48      [17]  185 	call	_drawFrame
                            186 ;src/main.c:173: cpct_etm_setDrawTilemap4x8_ag(VIEWPORT_W, VIEWPORT_H, g_building_W, g_tileset_00);
   4918 21 A4 44      [10]  187 	ld	hl, #_g_tileset_00
   491B E5            [11]  188 	push	hl
   491C 21 20 00      [10]  189 	ld	hl, #0x0020
   491F E5            [11]  190 	push	hl
   4920 21 10 10      [10]  191 	ld	hl, #0x1010
   4923 E5            [11]  192 	push	hl
   4924 CD 62 4B      [17]  193 	call	_cpct_etm_setDrawTilemap4x8_ag
   4927 C9            [10]  194 	ret
                            195 ;src/main.c:181: void game() {
                            196 ;	---------------------------------
                            197 ; Function game
                            198 ; ---------------------------------
   4928                     199 _game::
                            200 ;src/main.c:182: u16 offset=0;  // Offset in tiles of the start of the view window in the g_building tilemap
   4928 01 00 00      [10]  201 	ld	bc, #0x0000
                            202 ;src/main.c:183: u8  x=0, y=0;  // (x, y) coordinates of the start of the view window in the g_building tilemap
   492B 11 00 00      [10]  203 	ld	de,#0x0000
                            204 ;src/main.c:186: while (1) {
   492E                     205 00114$:
                            206 ;src/main.c:189: drawBuidlingScrolled(offset);
   492E C5            [11]  207 	push	bc
   492F D5            [11]  208 	push	de
   4930 C5            [11]  209 	push	bc
   4931 CD 64 48      [17]  210 	call	_drawBuidlingScrolled
   4934 F1            [10]  211 	pop	af
   4935 CD 03 4A      [17]  212 	call	_cpct_scanKeyboard_f
   4938 21 04 04      [10]  213 	ld	hl, #0x0404
   493B CD F7 49      [17]  214 	call	_cpct_isKeyPressed
   493E D1            [10]  215 	pop	de
   493F C1            [10]  216 	pop	bc
   4940 7D            [ 4]  217 	ld	a, l
   4941 B7            [ 4]  218 	or	a, a
   4942 28 06         [12]  219 	jr	Z,00102$
   4944 7B            [ 4]  220 	ld	a, e
   4945 B7            [ 4]  221 	or	a, a
   4946 28 02         [12]  222 	jr	Z,00102$
   4948 1D            [ 4]  223 	dec	e
   4949 0B            [ 6]  224 	dec	bc
   494A                     225 00102$:
                            226 ;src/main.c:205: if (cpct_isKeyPressed(Key_P) && x < g_building_W - VIEWPORT_W) { ++x; ++offset; }
   494A C5            [11]  227 	push	bc
   494B D5            [11]  228 	push	de
   494C 21 03 08      [10]  229 	ld	hl, #0x0803
   494F CD F7 49      [17]  230 	call	_cpct_isKeyPressed
   4952 D1            [10]  231 	pop	de
   4953 C1            [10]  232 	pop	bc
   4954 7D            [ 4]  233 	ld	a, l
   4955 B7            [ 4]  234 	or	a, a
   4956 28 07         [12]  235 	jr	Z,00105$
   4958 7B            [ 4]  236 	ld	a, e
   4959 D6 10         [ 7]  237 	sub	a, #0x10
   495B 30 02         [12]  238 	jr	NC,00105$
   495D 1C            [ 4]  239 	inc	e
   495E 03            [ 6]  240 	inc	bc
   495F                     241 00105$:
                            242 ;src/main.c:206: if (cpct_isKeyPressed(Key_Q) && y > 0)                         { --y; offset -= g_building_W; }
   495F C5            [11]  243 	push	bc
   4960 D5            [11]  244 	push	de
   4961 21 08 08      [10]  245 	ld	hl, #0x0808
   4964 CD F7 49      [17]  246 	call	_cpct_isKeyPressed
   4967 D1            [10]  247 	pop	de
   4968 C1            [10]  248 	pop	bc
   4969 7D            [ 4]  249 	ld	a, l
   496A B7            [ 4]  250 	or	a, a
   496B 28 0D         [12]  251 	jr	Z,00108$
   496D 7A            [ 4]  252 	ld	a, d
   496E B7            [ 4]  253 	or	a, a
   496F 28 09         [12]  254 	jr	Z,00108$
   4971 15            [ 4]  255 	dec	d
   4972 79            [ 4]  256 	ld	a, c
   4973 C6 E0         [ 7]  257 	add	a, #0xe0
   4975 4F            [ 4]  258 	ld	c, a
   4976 78            [ 4]  259 	ld	a, b
   4977 CE FF         [ 7]  260 	adc	a, #0xff
   4979 47            [ 4]  261 	ld	b, a
   497A                     262 00108$:
                            263 ;src/main.c:207: if (cpct_isKeyPressed(Key_A) && y < g_building_H - VIEWPORT_H) { ++y; offset += g_building_W; }
   497A C5            [11]  264 	push	bc
   497B D5            [11]  265 	push	de
   497C 21 08 20      [10]  266 	ld	hl, #0x2008
   497F CD F7 49      [17]  267 	call	_cpct_isKeyPressed
   4982 D1            [10]  268 	pop	de
   4983 C1            [10]  269 	pop	bc
   4984 7D            [ 4]  270 	ld	a, l
   4985 B7            [ 4]  271 	or	a, a
   4986 28 A6         [12]  272 	jr	Z,00114$
   4988 7A            [ 4]  273 	ld	a, d
   4989 D6 10         [ 7]  274 	sub	a, #0x10
   498B 30 A1         [12]  275 	jr	NC,00114$
   498D 14            [ 4]  276 	inc	d
   498E 21 20 00      [10]  277 	ld	hl, #0x0020
   4991 09            [11]  278 	add	hl,bc
   4992 4D            [ 4]  279 	ld	c, l
   4993 44            [ 4]  280 	ld	b, h
   4994 18 98         [12]  281 	jr	00114$
                            282 ;src/main.c:215: void main(void) {
                            283 ;	---------------------------------
                            284 ; Function main
                            285 ; ---------------------------------
   4996                     286 _main::
                            287 ;src/main.c:221: cpct_setStackLocation((void*)0x8000);
   4996 21 00 80      [10]  288 	ld	hl, #0x8000
   4999 CD 31 4B      [17]  289 	call	_cpct_setStackLocation
                            290 ;src/main.c:224: initialize();
   499C CD F2 48      [17]  291 	call	_initialize
                            292 ;src/main.c:225: game();
   499F C3 28 49      [10]  293 	jp  _game
                            294 	.area _CODE
                            295 	.area _INITIALIZER
                            296 	.area _CABS (ABS)
