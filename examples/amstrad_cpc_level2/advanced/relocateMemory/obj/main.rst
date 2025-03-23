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
                             12 	.globl _wait4KeyPress
                             13 	.globl _dummy_data_absorber_102
                             14 	.globl _initializeCPC
                             15 	.globl _dummy_data_absorber0x4000
                             16 	.globl _setUpVideoBuffer
                             17 	.globl _cpct_getScreenPtr
                             18 	.globl _cpct_setVideoMemoryPage
                             19 	.globl _cpct_setPALColour
                             20 	.globl _cpct_setPalette
                             21 	.globl _cpct_waitVSYNC
                             22 	.globl _cpct_setVideoMode
                             23 	.globl _cpct_drawStringM0
                             24 	.globl _cpct_setDrawCharM0
                             25 	.globl _cpct_px2byteM0
                             26 	.globl _cpct_isAnyKeyPressed
                             27 	.globl _cpct_scanKeyboard
                             28 	.globl _cpct_memset_f64
                             29 	.globl _cpct_disableFirmware
                             30 	.globl _g_buffers
                             31 	.globl _g_palette
                             32 ;--------------------------------------------------------
                             33 ; special function registers
                             34 ;--------------------------------------------------------
                             35 ;--------------------------------------------------------
                             36 ; ram data
                             37 ;--------------------------------------------------------
                             38 	.area _DATA
                             39 ;--------------------------------------------------------
                             40 ; ram data
                             41 ;--------------------------------------------------------
                             42 	.area _INITIALIZED
                             43 ;--------------------------------------------------------
                             44 ; absolute external ram data
                             45 ;--------------------------------------------------------
                             46 	.area _DABS (ABS)
                             47 ;--------------------------------------------------------
                             48 ; global & static initialisations
                             49 ;--------------------------------------------------------
                             50 	.area _HOME
                             51 	.area _GSINIT
                             52 	.area _GSFINAL
                             53 	.area _GSINIT
                             54 ;--------------------------------------------------------
                             55 ; Home
                             56 ;--------------------------------------------------------
                             57 	.area _HOME
                             58 	.area _HOME
                             59 ;--------------------------------------------------------
                             60 ; code
                             61 ;--------------------------------------------------------
                             62 	.area _CODE
                             63 ;src/main.c:56: void setUpVideoBuffer(u8* vmem, u16 c_pattern, u8* string, u8 pen, u8 bpen) {
                             64 ;	---------------------------------
                             65 ; Function setUpVideoBuffer
                             66 ; ---------------------------------
   8000                      67 _setUpVideoBuffer::
   8000 DD E5         [15]   68 	push	ix
   8002 DD 21 00 00   [14]   69 	ld	ix,#0
   8006 DD 39         [15]   70 	add	ix,sp
                             71 ;src/main.c:57: cpct_memset_f64(vmem, c_pattern, VMEM_SIZE);
   8008 DD 4E 04      [19]   72 	ld	c,4 (ix)
   800B DD 46 05      [19]   73 	ld	b,5 (ix)
   800E C5            [11]   74 	push	bc
   800F 21 00 40      [10]   75 	ld	hl, #0x4000
   8012 E5            [11]   76 	push	hl
   8013 DD 6E 06      [19]   77 	ld	l,6 (ix)
   8016 DD 66 07      [19]   78 	ld	h,7 (ix)
   8019 E5            [11]   79 	push	hl
   801A C5            [11]   80 	push	bc
   801B CD 16 81      [17]   81 	call	_cpct_memset_f64
   801E C1            [10]   82 	pop	bc
                             83 ;src/main.c:58: vmem = cpct_getScreenPtr(vmem, 0, 80);
   801F 21 00 50      [10]   84 	ld	hl, #0x5000
   8022 E5            [11]   85 	push	hl
   8023 C5            [11]   86 	push	bc
   8024 CD D6 81      [17]   87 	call	_cpct_getScreenPtr
   8027 DD 75 04      [19]   88 	ld	4 (ix), l
   802A DD 74 05      [19]   89 	ld	5 (ix), h
                             90 ;src/main.c:59: cpct_setDrawCharM0(pen, bpen);
   802D DD 66 0B      [19]   91 	ld	h, 11 (ix)
   8030 DD 6E 0A      [19]   92 	ld	l, 10 (ix)
   8033 E5            [11]   93 	push	hl
   8034 CD B1 81      [17]   94 	call	_cpct_setDrawCharM0
                             95 ;src/main.c:60: cpct_drawStringM0(string, vmem);
   8037 DD 4E 04      [19]   96 	ld	c,4 (ix)
   803A DD 46 05      [19]   97 	ld	b,5 (ix)
   803D C5            [11]   98 	push	bc
   803E DD 6E 08      [19]   99 	ld	l,8 (ix)
   8041 DD 66 09      [19]  100 	ld	h,9 (ix)
   8044 E5            [11]  101 	push	hl
   8045 CD 6F 80      [17]  102 	call	_cpct_drawStringM0
   8048 DD E1         [14]  103 	pop	ix
   804A C9            [10]  104 	ret
                            105 ;src/main.c:68: CPCT_ABSOLUTE_LOCATION_AREA(0x4000);
                            106 ;	---------------------------------
                            107 ; Function dummy_data_absorber0x4000
                            108 ; ---------------------------------
   804B                     109 _dummy_data_absorber0x4000::
   804B C9            [10]  110 	ret
                            111 ;src/main.c:68: 
                            112 ;	---------------------------------
                            113 ; Function dummy_absolute_0x4000
                            114 ; ---------------------------------
   804C                     115 _dummy_absolute_0x4000::
                            116 	.area _0x4000_ (ABS) 
   4000                     117 	.org 0x4000 
                            118 ;src/main.c:84: void initializeCPC() {
                            119 ;	---------------------------------
                            120 ; Function initializeCPC
                            121 ; ---------------------------------
   4000                     122 _initializeCPC::
                            123 ;src/main.c:85: cpct_disableFirmware();          // Disable the firmware not to interfere with us
   4000 CD A0 81      [17]  124 	call	_cpct_disableFirmware
                            125 ;src/main.c:86: cpct_setVideoMode(0);            // Set mode 0 (160x200, 16 colours)
   4003 2E 00         [ 7]  126 	ld	l, #0x00
   4005 CD 76 81      [17]  127 	call	_cpct_setVideoMode
                            128 ;src/main.c:87: cpct_setPalette(g_palette, 16);  // Set colour palette
   4008 21 10 00      [10]  129 	ld	hl, #0x0010
   400B E5            [11]  130 	push	hl
   400C 21 38 40      [10]  131 	ld	hl, #_g_palette
   400F E5            [11]  132 	push	hl
   4010 CD 4C 80      [17]  133 	call	_cpct_setPalette
                            134 ;src/main.c:88: cpct_setBorder(g_palette[0]);    // Set the border with same colour used for background (0)
   4013 21 38 40      [10]  135 	ld	hl, #_g_palette + 0
   4016 46            [ 7]  136 	ld	b, (hl)
   4017 C5            [11]  137 	push	bc
   4018 33            [ 6]  138 	inc	sp
   4019 3E 10         [ 7]  139 	ld	a, #0x10
   401B F5            [11]  140 	push	af
   401C 33            [ 6]  141 	inc	sp
   401D CD 63 80      [17]  142 	call	_cpct_setPALColour
                            143 ;src/main.c:91: setUpVideoBuffer(VMEM_0, 0, "Main Screen Buffer", 6, 0);
   4020 21 06 00      [10]  144 	ld	hl, #0x0006
   4023 E5            [11]  145 	push	hl
   4024 21 48 40      [10]  146 	ld	hl, #___str_0
   4027 E5            [11]  147 	push	hl
   4028 21 00 00      [10]  148 	ld	hl, #0x0000
   402B E5            [11]  149 	push	hl
   402C 26 C0         [ 7]  150 	ld	h, #0xc0
   402E E5            [11]  151 	push	hl
   402F CD 00 80      [17]  152 	call	_setUpVideoBuffer
   4032 21 08 00      [10]  153 	ld	hl, #8
   4035 39            [11]  154 	add	hl, sp
   4036 F9            [ 6]  155 	ld	sp, hl
   4037 C9            [10]  156 	ret
   4038                     157 _g_palette:
   4038 1A                  158 	.db #0x1a	; 26
   4039 03                  159 	.db #0x03	; 3
   403A 01                  160 	.db #0x01	; 1
   403B 00                  161 	.db #0x00	; 0
   403C 0D                  162 	.db #0x0d	; 13
   403D 19                  163 	.db #0x19	; 25
   403E 14                  164 	.db #0x14	; 20
   403F 12                  165 	.db #0x12	; 18
   4040 16                  166 	.db #0x16	; 22
   4041 15                  167 	.db #0x15	; 21
   4042 13                  168 	.db #0x13	; 19
   4043 06                  169 	.db #0x06	; 6
   4044 07                  170 	.db #0x07	; 7
   4045 08                  171 	.db #0x08	; 8
   4046 02                  172 	.db #0x02	; 2
   4047 0A                  173 	.db #0x0a	; 10
   4048                     174 ___str_0:
   4048 4D 61 69 6E 20 53   175 	.ascii "Main Screen Buffer"
        63 72 65 65 6E 20
        42 75 66 66 65 72
   405A 00                  176 	.db 0x00
                            177 ;src/main.c:102: CPCT_RELOCATABLE_AREA();
                            178 ;	---------------------------------
                            179 ; Function dummy_data_absorber_102
                            180 ; ---------------------------------
   405B                     181 _dummy_data_absorber_102::
   405B C9            [10]  182 	ret
                            183 ;src/main.c:102: 
                            184 ;	---------------------------------
                            185 ; Function dummy_relocatable_102
                            186 ; ---------------------------------
   405C                     187 _dummy_relocatable_102::
                            188 	.area _CSEG (REL, CON) 
                            189 ;src/main.c:107: void wait4KeyPress () {
                            190 ;	---------------------------------
                            191 ; Function wait4KeyPress
                            192 ; ---------------------------------
   8237                     193 _wait4KeyPress::
                            194 ;src/main.c:109: do { cpct_scanKeyboard(); } while (  cpct_isAnyKeyPressed() );
   8237                     195 00101$:
   8237 CD EC 81      [17]  196 	call	_cpct_scanKeyboard
   823A CD 61 81      [17]  197 	call	_cpct_isAnyKeyPressed
   823D 7D            [ 4]  198 	ld	a, l
   823E B7            [ 4]  199 	or	a, a
   823F 20 F6         [12]  200 	jr	NZ,00101$
                            201 ;src/main.c:112: do { cpct_scanKeyboard(); } while ( !cpct_isAnyKeyPressed() );
   8241                     202 00104$:
   8241 CD EC 81      [17]  203 	call	_cpct_scanKeyboard
   8244 CD 61 81      [17]  204 	call	_cpct_isAnyKeyPressed
   8247 7D            [ 4]  205 	ld	a, l
   8248 B7            [ 4]  206 	or	a, a
   8249 28 F6         [12]  207 	jr	Z,00104$
   824B C9            [10]  208 	ret
                            209 ;src/main.c:124: void main(void) {
                            210 ;	---------------------------------
                            211 ; Function main
                            212 ; ---------------------------------
   824C                     213 _main::
   824C DD E5         [15]  214 	push	ix
   824E DD 21 00 00   [14]  215 	ld	ix,#0
   8252 DD 39         [15]  216 	add	ix,sp
   8254 3B            [ 6]  217 	dec	sp
                            218 ;src/main.c:125: u8  scr = 0;      // Video buffer selector: selects what is to be shown on the screen
   8255 DD 36 FF 00   [19]  219 	ld	-1 (ix), #0x00
                            220 ;src/main.c:129: initializeCPC();
   8259 CD 00 40      [17]  221 	call	_initializeCPC
                            222 ;src/main.c:133: pattern = ( cpct_px2byteM0(4, 6) << 8 ) | cpct_px2byteM0(8, 9);
   825C 21 04 06      [10]  223 	ld	hl, #0x0604
   825F E5            [11]  224 	push	hl
   8260 CD 84 81      [17]  225 	call	_cpct_px2byteM0
   8263 45            [ 4]  226 	ld	b, l
   8264 0E 00         [ 7]  227 	ld	c, #0x00
   8266 C5            [11]  228 	push	bc
   8267 21 08 09      [10]  229 	ld	hl, #0x0908
   826A E5            [11]  230 	push	hl
   826B CD 84 81      [17]  231 	call	_cpct_px2byteM0
   826E C1            [10]  232 	pop	bc
   826F 26 00         [ 7]  233 	ld	h, #0x00
   8271 79            [ 4]  234 	ld	a, c
   8272 B5            [ 4]  235 	or	a, l
   8273 4F            [ 4]  236 	ld	c, a
   8274 78            [ 4]  237 	ld	a, b
   8275 B4            [ 4]  238 	or	a, h
   8276 47            [ 4]  239 	ld	b, a
                            240 ;src/main.c:139: setUpVideoBuffer(VMEM_1, pattern, "0x4000 Screen Buffer", 0, 6);
   8277 21 00 06      [10]  241 	ld	hl, #0x0600
   827A E5            [11]  242 	push	hl
   827B 21 AF 82      [10]  243 	ld	hl, #___str_1
   827E E5            [11]  244 	push	hl
   827F C5            [11]  245 	push	bc
   8280 21 00 40      [10]  246 	ld	hl, #0x4000
   8283 E5            [11]  247 	push	hl
   8284 CD 00 80      [17]  248 	call	_setUpVideoBuffer
   8287 21 08 00      [10]  249 	ld	hl, #8
   828A 39            [11]  250 	add	hl, sp
   828B F9            [ 6]  251 	ld	sp, hl
                            252 ;src/main.c:142: while (1) {
   828C                     253 00102$:
                            254 ;src/main.c:145: cpct_waitVSYNC();
   828C CD 6E 81      [17]  255 	call	_cpct_waitVSYNC
                            256 ;src/main.c:146: cpct_setVideoMemoryPage(g_buffers[scr]);  // Sets the memory page that will be shown on screen
   828F 01 AD 82      [10]  257 	ld	bc, #_g_buffers+0
   8292 DD 6E FF      [19]  258 	ld	l,-1 (ix)
   8295 26 00         [ 7]  259 	ld	h,#0x00
   8297 09            [11]  260 	add	hl, bc
   8298 6E            [ 7]  261 	ld	l, (hl)
   8299 CD 0D 81      [17]  262 	call	_cpct_setVideoMemoryPage
                            263 ;src/main.c:150: scr = scr ^ 0x01;    // Does operation scr XOR 1, which alternates the value of the last bit of scr, 
   829C DD 7E FF      [19]  264 	ld	a, -1 (ix)
   829F EE 01         [ 7]  265 	xor	a, #0x01
   82A1 DD 77 FF      [19]  266 	ld	-1 (ix), a
                            267 ;src/main.c:152: wait4KeyPress();
   82A4 CD 37 82      [17]  268 	call	_wait4KeyPress
   82A7 18 E3         [12]  269 	jr	00102$
   82A9 33            [ 6]  270 	inc	sp
   82AA DD E1         [14]  271 	pop	ix
   82AC C9            [10]  272 	ret
   82AD                     273 _g_buffers:
   82AD 30                  274 	.db #0x30	; 48	'0'
   82AE 10                  275 	.db #0x10	; 16
   82AF                     276 ___str_1:
   82AF 30 78 34 30 30 30   277 	.ascii "0x4000 Screen Buffer"
        20 53 63 72 65 65
        6E 20 42 75 66 66
        65 72
   82C3 00                  278 	.db 0x00
                            279 	.area _CODE
                            280 	.area _INITIALIZER
                            281 	.area _CABS (ABS)
