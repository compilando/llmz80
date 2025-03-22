                              1 ;--------------------------------------------------------
                              2 ; File Created by SDCC : free open source ANSI-C Compiler
                              3 ; Version 3.6.8 #9946 (Linux)
                              4 ;--------------------------------------------------------
                              5 	.module manageVideoMem
                              6 	.optsdcc -mz80
                              7 	
                              8 ;--------------------------------------------------------
                              9 ; Public variables in this module
                             10 ;--------------------------------------------------------
                             11 	.globl _cpct_getScreenPtr
                             12 	.globl _cpct_setVideoMemoryPage
                             13 	.globl _cpct_waitVSYNC
                             14 	.globl _gVMem
                             15 	.globl _InitializeVideoMemoryBuffers
                             16 	.globl _FlipBuffers
                             17 	.globl _GetScreenPtr
                             18 	.globl _GetBackBufferPtr
                             19 ;--------------------------------------------------------
                             20 ; special function registers
                             21 ;--------------------------------------------------------
                             22 ;--------------------------------------------------------
                             23 ; ram data
                             24 ;--------------------------------------------------------
                             25 	.area _DATA
   16FB                      26 _gVMem::
   16FB                      27 	.ds 1
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
                             52 ;src/manageVideoMem.c:31: void InitializeVideoMemoryBuffers() {
                             53 ;	---------------------------------
                             54 ; Function InitializeVideoMemoryBuffers
                             55 ; ---------------------------------
   105D                      56 _InitializeVideoMemoryBuffers::
                             57 ;src/manageVideoMem.c:32: gVMem = VIDEO_MEM;   
   105D 21 FB 16      [10]   58 	ld	hl,#_gVMem + 0
   1060 36 00         [10]   59 	ld	(hl), #0x00
   1062 C9            [10]   60 	ret
                             61 ;src/manageVideoMem.c:44: void FlipBuffers() {
                             62 ;	---------------------------------
                             63 ; Function FlipBuffers
                             64 ; ---------------------------------
   1063                      65 _FlipBuffers::
                             66 ;src/manageVideoMem.c:45: cpct_waitVSYNC(); // Wait until VSYNC is up
   1063 CD 67 13      [17]   67 	call	_cpct_waitVSYNC
                             68 ;src/manageVideoMem.c:49: if (gVMem == BUFFER_MEM) {
   1066 3A FB 16      [13]   69 	ld	a,(#_gVMem + 0)
   1069 3D            [ 4]   70 	dec	a
   106A 20 0B         [12]   71 	jr	NZ,00102$
                             72 ;src/manageVideoMem.c:50: cpct_setVideoMemoryPage(cpct_pageC0);
   106C 2E 30         [ 7]   73 	ld	l, #0x30
   106E CD D7 12      [17]   74 	call	_cpct_setVideoMemoryPage
                             75 ;src/manageVideoMem.c:51: gVMem = VIDEO_MEM;
   1071 21 FB 16      [10]   76 	ld	hl,#_gVMem + 0
   1074 36 00         [10]   77 	ld	(hl), #0x00
   1076 C9            [10]   78 	ret
   1077                      79 00102$:
                             80 ;src/manageVideoMem.c:53: cpct_setVideoMemoryPage(cpct_page80);
   1077 2E 20         [ 7]   81 	ld	l, #0x20
   1079 CD D7 12      [17]   82 	call	_cpct_setVideoMemoryPage
                             83 ;src/manageVideoMem.c:54: gVMem = BUFFER_MEM;
   107C 21 FB 16      [10]   84 	ld	hl,#_gVMem + 0
   107F 36 01         [10]   85 	ld	(hl), #0x01
   1081 C9            [10]   86 	ret
                             87 ;src/manageVideoMem.c:62: u8* GetScreenPtr(u8 xPos, u8 yPos) {
                             88 ;	---------------------------------
                             89 ; Function GetScreenPtr
                             90 ; ---------------------------------
   1082                      91 _GetScreenPtr::
                             92 ;src/manageVideoMem.c:67: if (gVMem == VIDEO_MEM) screenStart = (u8*)CPCT_VMEM_START;
   1082 3A FB 16      [13]   93 	ld	a,(#_gVMem + 0)
   1085 B7            [ 4]   94 	or	a, a
   1086 20 05         [12]   95 	jr	NZ,00102$
   1088 01 00 C0      [10]   96 	ld	bc, #0xc000
   108B 18 03         [12]   97 	jr	00103$
   108D                      98 00102$:
                             99 ;src/manageVideoMem.c:68: else                    screenStart = (u8*)SCREEN_BUFF;
   108D 01 00 80      [10]  100 	ld	bc, #0x8000
   1090                     101 00103$:
                            102 ;src/manageVideoMem.c:71: return cpct_getScreenPtr(screenStart, xPos, yPos);
   1090 21 03 00      [10]  103 	ld	hl, #3+0
   1093 39            [11]  104 	add	hl, sp
   1094 7E            [ 7]  105 	ld	a, (hl)
   1095 F5            [11]  106 	push	af
   1096 33            [ 6]  107 	inc	sp
   1097 21 03 00      [10]  108 	ld	hl, #3+0
   109A 39            [11]  109 	add	hl, sp
   109B 7E            [ 7]  110 	ld	a, (hl)
   109C F5            [11]  111 	push	af
   109D 33            [ 6]  112 	inc	sp
   109E C5            [11]  113 	push	bc
   109F CD BF 14      [17]  114 	call	_cpct_getScreenPtr
   10A2 C9            [10]  115 	ret
                            116 ;src/manageVideoMem.c:78: u8* GetBackBufferPtr(u8 xPos, u8 yPos) {
                            117 ;	---------------------------------
                            118 ; Function GetBackBufferPtr
                            119 ; ---------------------------------
   10A3                     120 _GetBackBufferPtr::
                            121 ;src/manageVideoMem.c:83: if (gVMem == VIDEO_MEM) backBufferStart = (u8*)SCREEN_BUFF;
   10A3 3A FB 16      [13]  122 	ld	a,(#_gVMem + 0)
   10A6 B7            [ 4]  123 	or	a, a
   10A7 20 05         [12]  124 	jr	NZ,00102$
   10A9 01 00 80      [10]  125 	ld	bc, #0x8000
   10AC 18 03         [12]  126 	jr	00103$
   10AE                     127 00102$:
                            128 ;src/manageVideoMem.c:84: else                    backBufferStart = (u8*)CPCT_VMEM_START;
   10AE 01 00 C0      [10]  129 	ld	bc, #0xc000
   10B1                     130 00103$:
                            131 ;src/manageVideoMem.c:87: return cpct_getScreenPtr(backBufferStart, xPos, yPos);
   10B1 21 03 00      [10]  132 	ld	hl, #3+0
   10B4 39            [11]  133 	add	hl, sp
   10B5 7E            [ 7]  134 	ld	a, (hl)
   10B6 F5            [11]  135 	push	af
   10B7 33            [ 6]  136 	inc	sp
   10B8 21 03 00      [10]  137 	ld	hl, #3+0
   10BB 39            [11]  138 	add	hl, sp
   10BC 7E            [ 7]  139 	ld	a, (hl)
   10BD F5            [11]  140 	push	af
   10BE 33            [ 6]  141 	inc	sp
   10BF C5            [11]  142 	push	bc
   10C0 CD BF 14      [17]  143 	call	_cpct_getScreenPtr
   10C3 C9            [10]  144 	ret
                            145 	.area _CODE
                            146 	.area _INITIALIZER
                            147 	.area _CABS (ABS)
