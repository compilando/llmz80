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
                             12 	.globl _doSomeClears
                             13 	.globl _doSomeClears8
                             14 	.globl _waitNVSYNCs
                             15 	.globl _getColourPattern
                             16 	.globl _cpct_setPALColour
                             17 	.globl _cpct_waitVSYNC
                             18 	.globl _cpct_setVideoMode
                             19 	.globl _cpct_px2byteM0
                             20 	.globl _cpct_memset_f64
                             21 	.globl _cpct_memset_f8
                             22 	.globl _cpct_memset
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
                             55 ;src/main.c:27: u16 getColourPattern(u8 c1, u8 c2, u8 c3, u8 c4) {
                             56 ;	---------------------------------
                             57 ; Function getColourPattern
                             58 ; ---------------------------------
   0100                      59 _getColourPattern::
   0100 DD E5         [15]   60 	push	ix
   0102 DD 21 00 00   [14]   61 	ld	ix,#0
   0106 DD 39         [15]   62 	add	ix,sp
                             63 ;src/main.c:28: return 256*cpct_px2byteM0(c3, c4) + cpct_px2byteM0(c1, c2);
   0108 DD 66 07      [19]   64 	ld	h, 7 (ix)
   010B DD 6E 06      [19]   65 	ld	l, 6 (ix)
   010E E5            [11]   66 	push	hl
   010F CD EF 02      [17]   67 	call	_cpct_px2byteM0
   0112 45            [ 4]   68 	ld	b, l
   0113 0E 00         [ 7]   69 	ld	c, #0x00
   0115 C5            [11]   70 	push	bc
   0116 DD 66 05      [19]   71 	ld	h, 5 (ix)
   0119 DD 6E 04      [19]   72 	ld	l, 4 (ix)
   011C E5            [11]   73 	push	hl
   011D CD EF 02      [17]   74 	call	_cpct_px2byteM0
   0120 C1            [10]   75 	pop	bc
   0121 26 00         [ 7]   76 	ld	h, #0x00
   0123 09            [11]   77 	add	hl, bc
   0124 DD E1         [14]   78 	pop	ix
   0126 C9            [10]   79 	ret
                             80 ;src/main.c:34: void waitNVSYNCs(u8 n) {
                             81 ;	---------------------------------
                             82 ; Function waitNVSYNCs
                             83 ; ---------------------------------
   0127                      84 _waitNVSYNCs::
                             85 ;src/main.c:35: do {
   0127 21 02 00      [10]   86 	ld	hl, #2+0
   012A 39            [11]   87 	add	hl, sp
   012B 4E            [ 7]   88 	ld	c, (hl)
   012C                      89 00103$:
                             90 ;src/main.c:37: cpct_waitVSYNC();
   012C C5            [11]   91 	push	bc
   012D CD A9 02      [17]   92 	call	_cpct_waitVSYNC
   0130 C1            [10]   93 	pop	bc
                             94 ;src/main.c:42: if (--n) {
   0131 0D            [ 4]   95 	dec	c
   0132 79            [ 4]   96 	ld	a, c
   0133 B7            [ 4]   97 	or	a, a
   0134 28 02         [12]   98 	jr	Z,00104$
                             99 ;src/main.c:43: __asm__ ("halt"); // Halt stops the Z80 until next interrupt.
   0136 76            [ 4]  100 	halt
                            101 ;src/main.c:44: __asm__ ("halt"); // There are 6 interrupts per VSYNC (1/300 seconds each)
   0137 76            [ 4]  102 	halt
   0138                     103 00104$:
                            104 ;src/main.c:46: } while(n);
   0138 79            [ 4]  105 	ld	a, c
   0139 B7            [ 4]  106 	or	a, a
   013A 20 F0         [12]  107 	jr	NZ,00103$
   013C C9            [10]  108 	ret
                            109 ;src/main.c:53: void doSomeClears8(u8 colour, u8 vsyncs) {
                            110 ;	---------------------------------
                            111 ; Function doSomeClears8
                            112 ; ---------------------------------
   013D                     113 _doSomeClears8::
   013D 3B            [ 6]  114 	dec	sp
                            115 ;src/main.c:55: for(i=0; i < 2 ; i++) {
   013E FD 21 00 00   [14]  116 	ld	iy, #0
   0142 FD 39         [15]  117 	add	iy, sp
   0144 FD 36 00 00   [19]  118 	ld	0 (iy), #0x00
   0148                     119 00102$:
                            120 ;src/main.c:56: u8 pattern = cpct_px2byteM0(colour, colour);
   0148 FD 21 03 00   [14]  121 	ld	iy, #3
   014C FD 39         [15]  122 	add	iy, sp
   014E FD 66 00      [19]  123 	ld	h, 0 (iy)
   0151 FD 6E 00      [19]  124 	ld	l, 0 (iy)
   0154 E5            [11]  125 	push	hl
   0155 CD EF 02      [17]  126 	call	_cpct_px2byteM0
   0158 45            [ 4]  127 	ld	b, l
                            128 ;src/main.c:57: waitNVSYNCs(vsyncs);
   0159 C5            [11]  129 	push	bc
   015A 21 06 00      [10]  130 	ld	hl, #6+0
   015D 39            [11]  131 	add	hl, sp
   015E 7E            [ 7]  132 	ld	a, (hl)
   015F F5            [11]  133 	push	af
   0160 33            [ 6]  134 	inc	sp
   0161 CD 27 01      [17]  135 	call	_waitNVSYNCs
   0164 33            [ 6]  136 	inc	sp
   0165 C1            [10]  137 	pop	bc
                            138 ;src/main.c:58: cpct_memset(CPCT_VMEM_START, pattern, 0x4000);
   0166 21 00 40      [10]  139 	ld	hl, #0x4000
   0169 E5            [11]  140 	push	hl
   016A C5            [11]  141 	push	bc
   016B 33            [ 6]  142 	inc	sp
   016C 26 C0         [ 7]  143 	ld	h, #0xc0
   016E E5            [11]  144 	push	hl
   016F CD 0B 03      [17]  145 	call	_cpct_memset
                            146 ;src/main.c:59: waitNVSYNCs(vsyncs);
   0172 21 04 00      [10]  147 	ld	hl, #4+0
   0175 39            [11]  148 	add	hl, sp
   0176 7E            [ 7]  149 	ld	a, (hl)
   0177 F5            [11]  150 	push	af
   0178 33            [ 6]  151 	inc	sp
   0179 CD 27 01      [17]  152 	call	_waitNVSYNCs
   017C 33            [ 6]  153 	inc	sp
                            154 ;src/main.c:60: cpct_memset(CPCT_VMEM_START,       0, 0x4000);
   017D 21 00 40      [10]  155 	ld	hl, #0x4000
   0180 E5            [11]  156 	push	hl
   0181 AF            [ 4]  157 	xor	a, a
   0182 F5            [11]  158 	push	af
   0183 33            [ 6]  159 	inc	sp
   0184 26 C0         [ 7]  160 	ld	h, #0xc0
   0186 E5            [11]  161 	push	hl
   0187 CD 0B 03      [17]  162 	call	_cpct_memset
                            163 ;src/main.c:55: for(i=0; i < 2 ; i++) {
   018A FD 21 00 00   [14]  164 	ld	iy, #0
   018E FD 39         [15]  165 	add	iy, sp
   0190 FD 34 00      [23]  166 	inc	0 (iy)
   0193 FD 7E 00      [19]  167 	ld	a, 0 (iy)
   0196 D6 02         [ 7]  168 	sub	a, #0x02
   0198 38 AE         [12]  169 	jr	C,00102$
   019A 33            [ 6]  170 	inc	sp
   019B C9            [10]  171 	ret
                            172 ;src/main.c:69: void doSomeClears(TMemsetFunc func, u8 colour, u8 vsyncs) {
                            173 ;	---------------------------------
                            174 ; Function doSomeClears
                            175 ; ---------------------------------
   019C                     176 _doSomeClears::
   019C DD E5         [15]  177 	push	ix
   019E DD 21 00 00   [14]  178 	ld	ix,#0
   01A2 DD 39         [15]  179 	add	ix,sp
   01A4 3B            [ 6]  180 	dec	sp
                            181 ;src/main.c:71: for(i=0; i < 2 ; i++) {
   01A5 DD 36 FF 00   [19]  182 	ld	-1 (ix), #0x00
   01A9                     183 00102$:
                            184 ;src/main.c:72: u16 pattern = getColourPattern(colour, colour, colour, colour);
   01A9 DD 66 06      [19]  185 	ld	h, 6 (ix)
   01AC DD 6E 06      [19]  186 	ld	l, 6 (ix)
   01AF E5            [11]  187 	push	hl
   01B0 DD 66 06      [19]  188 	ld	h, 6 (ix)
   01B3 DD 6E 06      [19]  189 	ld	l, 6 (ix)
   01B6 E5            [11]  190 	push	hl
   01B7 CD 00 01      [17]  191 	call	_getColourPattern
   01BA F1            [10]  192 	pop	af
                            193 ;src/main.c:73: waitNVSYNCs(vsyncs);
   01BB E3            [19]  194 	ex	(sp),hl
   01BC DD 7E 07      [19]  195 	ld	a, 7 (ix)
   01BF F5            [11]  196 	push	af
   01C0 33            [ 6]  197 	inc	sp
   01C1 CD 27 01      [17]  198 	call	_waitNVSYNCs
   01C4 33            [ 6]  199 	inc	sp
   01C5 E1            [10]  200 	pop	hl
                            201 ;src/main.c:74: func(CPCT_VMEM_START, pattern, 0x4000);
   01C6 01 00 40      [10]  202 	ld	bc, #0x4000
   01C9 C5            [11]  203 	push	bc
   01CA E5            [11]  204 	push	hl
   01CB 21 00 C0      [10]  205 	ld	hl, #0xc000
   01CE E5            [11]  206 	push	hl
   01CF DD 6E 04      [19]  207 	ld	l,4 (ix)
   01D2 DD 66 05      [19]  208 	ld	h,5 (ix)
   01D5 CD A8 02      [17]  209 	call	___sdcc_call_hl
                            210 ;src/main.c:75: waitNVSYNCs(vsyncs);
   01D8 DD 7E 07      [19]  211 	ld	a, 7 (ix)
   01DB F5            [11]  212 	push	af
   01DC 33            [ 6]  213 	inc	sp
   01DD CD 27 01      [17]  214 	call	_waitNVSYNCs
   01E0 33            [ 6]  215 	inc	sp
                            216 ;src/main.c:76: func(CPCT_VMEM_START,       0, 0x4000);
   01E1 21 00 40      [10]  217 	ld	hl, #0x4000
   01E4 E5            [11]  218 	push	hl
   01E5 26 00         [ 7]  219 	ld	h, #0x00
   01E7 E5            [11]  220 	push	hl
   01E8 26 C0         [ 7]  221 	ld	h, #0xc0
   01EA E5            [11]  222 	push	hl
   01EB DD 6E 04      [19]  223 	ld	l,4 (ix)
   01EE DD 66 05      [19]  224 	ld	h,5 (ix)
   01F1 CD A8 02      [17]  225 	call	___sdcc_call_hl
                            226 ;src/main.c:71: for(i=0; i < 2 ; i++) {
   01F4 DD 34 FF      [23]  227 	inc	-1 (ix)
   01F7 DD 7E FF      [19]  228 	ld	a, -1 (ix)
   01FA D6 02         [ 7]  229 	sub	a, #0x02
   01FC 38 AB         [12]  230 	jr	C,00102$
   01FE 33            [ 6]  231 	inc	sp
   01FF DD E1         [14]  232 	pop	ix
   0201 C9            [10]  233 	ret
                            234 ;src/main.c:83: void main(void) {   
                            235 ;	---------------------------------
                            236 ; Function main
                            237 ; ---------------------------------
   0202                     238 _main::
                            239 ;src/main.c:84: u8 colour = 1, vsyncs = 50;
   0202 01 01 32      [10]  240 	ld	bc,#0x3201
                            241 ;src/main.c:88: cpct_disableFirmware(); 
   0205 C5            [11]  242 	push	bc
   0206 CD 19 03      [17]  243 	call	_cpct_disableFirmware
   0209 2E 00         [ 7]  244 	ld	l, #0x00
   020B CD B1 02      [17]  245 	call	_cpct_setVideoMode
   020E C1            [10]  246 	pop	bc
                            247 ;src/main.c:92: while(1) {
   020F                     248 00106$:
                            249 ;src/main.c:94: cpct_setBorder(4);
   020F C5            [11]  250 	push	bc
   0210 21 10 04      [10]  251 	ld	hl, #0x0410
   0213 E5            [11]  252 	push	hl
   0214 CD 51 02      [17]  253 	call	_cpct_setPALColour
   0217 C1            [10]  254 	pop	bc
                            255 ;src/main.c:95: doSomeClears8(colour, vsyncs);
   0218 C5            [11]  256 	push	bc
   0219 C5            [11]  257 	push	bc
   021A CD 3D 01      [17]  258 	call	_doSomeClears8
   021D 21 10 01      [10]  259 	ld	hl, #0x0110
   0220 E3            [19]  260 	ex	(sp),hl
   0221 CD 51 02      [17]  261 	call	_cpct_setPALColour
   0224 C1            [10]  262 	pop	bc
                            263 ;src/main.c:99: doSomeClears(&cpct_memset_f8,  colour, vsyncs);
   0225 C5            [11]  264 	push	bc
   0226 C5            [11]  265 	push	bc
   0227 21 BF 02      [10]  266 	ld	hl, #_cpct_memset_f8
   022A E5            [11]  267 	push	hl
   022B CD 9C 01      [17]  268 	call	_doSomeClears
   022E F1            [10]  269 	pop	af
   022F 21 10 05      [10]  270 	ld	hl, #0x0510
   0232 E3            [19]  271 	ex	(sp),hl
   0233 CD 51 02      [17]  272 	call	_cpct_setPALColour
   0236 C1            [10]  273 	pop	bc
                            274 ;src/main.c:103: doSomeClears(&cpct_memset_f64, colour, vsyncs);
   0237 C5            [11]  275 	push	bc
   0238 C5            [11]  276 	push	bc
   0239 21 5D 02      [10]  277 	ld	hl, #_cpct_memset_f64
   023C E5            [11]  278 	push	hl
   023D CD 9C 01      [17]  279 	call	_doSomeClears
   0240 F1            [10]  280 	pop	af
   0241 F1            [10]  281 	pop	af
   0242 C1            [10]  282 	pop	bc
                            283 ;src/main.c:106: if (++colour > 15) colour = 1;
   0243 0C            [ 4]  284 	inc	c
   0244 3E 0F         [ 7]  285 	ld	a, #0x0f
   0246 91            [ 4]  286 	sub	a, c
   0247 30 02         [12]  287 	jr	NC,00102$
   0249 0E 01         [ 7]  288 	ld	c, #0x01
   024B                     289 00102$:
                            290 ;src/main.c:107: if (! --vsyncs) vsyncs = 50;
   024B 10 C2         [13]  291 	djnz	00106$
   024D 06 32         [ 7]  292 	ld	b, #0x32
   024F 18 BE         [12]  293 	jr	00106$
                            294 	.area _CODE
                            295 	.area _INITIALIZER
                            296 	.area _CABS (ABS)
