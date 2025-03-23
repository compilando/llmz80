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
                             14 	.globl _cpct_drawSprite
                             15 	.globl _cpct_memset
                             16 	.globl _gVMem
                             17 	.globl _gSpriteBackBuffer
                             18 	.globl _InitializeVideoMemoryBuffers
                             19 	.globl _FlipBuffers
                             20 	.globl _GetScreenPtr
                             21 	.globl _GetBackBufferPtr
                             22 	.globl _GetSpriteBackBufferPtr
                             23 	.globl _DrawSpriteBackBufferToScreen
                             24 ;--------------------------------------------------------
                             25 ; special function registers
                             26 ;--------------------------------------------------------
                             27 ;--------------------------------------------------------
                             28 ; ram data
                             29 ;--------------------------------------------------------
                             30 	.area _DATA
   4F43                      31 _gSpriteBackBuffer::
   4F43                      32 	.ds 3000
   5AFB                      33 _gVMem::
   5AFB                      34 	.ds 1
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
                             59 ;src/manageVideoMem.c:32: void InitializeVideoMemoryBuffers() {
                             60 ;	---------------------------------
                             61 ; Function InitializeVideoMemoryBuffers
                             62 ; ---------------------------------
   47D0                      63 _InitializeVideoMemoryBuffers::
                             64 ;src/manageVideoMem.c:35: cpct_memset((u8*)SCREEN_BUFF, 0, 0x4000);   
   47D0 21 00 40      [10]   65 	ld	hl, #0x4000
   47D3 E5            [11]   66 	push	hl
   47D4 AF            [ 4]   67 	xor	a, a
   47D5 F5            [11]   68 	push	af
   47D6 33            [ 6]   69 	inc	sp
   47D7 26 80         [ 7]   70 	ld	h, #0x80
   47D9 E5            [11]   71 	push	hl
   47DA CD 09 4D      [17]   72 	call	_cpct_memset
                             73 ;src/manageVideoMem.c:37: gVMem = VIDEO_MEM;   
   47DD 21 FB 5A      [10]   74 	ld	hl,#_gVMem + 0
   47E0 36 00         [10]   75 	ld	(hl), #0x00
   47E2 C9            [10]   76 	ret
                             77 ;src/manageVideoMem.c:49: void FlipBuffers() {
                             78 ;	---------------------------------
                             79 ; Function FlipBuffers
                             80 ; ---------------------------------
   47E3                      81 _FlipBuffers::
                             82 ;src/manageVideoMem.c:50: cpct_waitVSYNC(); // Wait until VSYNC is up
   47E3 CD 01 4D      [17]   83 	call	_cpct_waitVSYNC
                             84 ;src/manageVideoMem.c:54: if (gVMem == BUFFER_MEM) {
   47E6 3A FB 5A      [13]   85 	ld	a,(#_gVMem + 0)
   47E9 3D            [ 4]   86 	dec	a
   47EA 20 0B         [12]   87 	jr	NZ,00102$
                             88 ;src/manageVideoMem.c:55: cpct_setVideoMemoryPage(cpct_pageC0);
   47EC 2E 30         [ 7]   89 	ld	l, #0x30
   47EE CD A6 4C      [17]   90 	call	_cpct_setVideoMemoryPage
                             91 ;src/manageVideoMem.c:56: gVMem = VIDEO_MEM;
   47F1 21 FB 5A      [10]   92 	ld	hl,#_gVMem + 0
   47F4 36 00         [10]   93 	ld	(hl), #0x00
   47F6 C9            [10]   94 	ret
   47F7                      95 00102$:
                             96 ;src/manageVideoMem.c:58: cpct_setVideoMemoryPage(cpct_page80);
   47F7 2E 20         [ 7]   97 	ld	l, #0x20
   47F9 CD A6 4C      [17]   98 	call	_cpct_setVideoMemoryPage
                             99 ;src/manageVideoMem.c:59: gVMem = BUFFER_MEM;
   47FC 21 FB 5A      [10]  100 	ld	hl,#_gVMem + 0
   47FF 36 01         [10]  101 	ld	(hl), #0x01
   4801 C9            [10]  102 	ret
                            103 ;src/manageVideoMem.c:67: u8* GetScreenPtr(u8 xPos, u8 yPos) {
                            104 ;	---------------------------------
                            105 ; Function GetScreenPtr
                            106 ; ---------------------------------
   4802                     107 _GetScreenPtr::
                            108 ;src/manageVideoMem.c:72: if (gVMem == VIDEO_MEM) screenStart = (u8*)CPCT_VMEM_START;
   4802 3A FB 5A      [13]  109 	ld	a,(#_gVMem + 0)
   4805 B7            [ 4]  110 	or	a, a
   4806 20 05         [12]  111 	jr	NZ,00102$
   4808 01 00 C0      [10]  112 	ld	bc, #0xc000
   480B 18 03         [12]  113 	jr	00103$
   480D                     114 00102$:
                            115 ;src/manageVideoMem.c:73: else                    screenStart = (u8*)SCREEN_BUFF;
   480D 01 00 80      [10]  116 	ld	bc, #0x8000
   4810                     117 00103$:
                            118 ;src/manageVideoMem.c:76: return cpct_getScreenPtr(screenStart, xPos, yPos);
   4810 21 03 00      [10]  119 	ld	hl, #3+0
   4813 39            [11]  120 	add	hl, sp
   4814 7E            [ 7]  121 	ld	a, (hl)
   4815 F5            [11]  122 	push	af
   4816 33            [ 6]  123 	inc	sp
   4817 21 03 00      [10]  124 	ld	hl, #3+0
   481A 39            [11]  125 	add	hl, sp
   481B 7E            [ 7]  126 	ld	a, (hl)
   481C F5            [11]  127 	push	af
   481D 33            [ 6]  128 	inc	sp
   481E C5            [11]  129 	push	bc
   481F CD 3C 4E      [17]  130 	call	_cpct_getScreenPtr
   4822 C9            [10]  131 	ret
                            132 ;src/manageVideoMem.c:83: u8* GetBackBufferPtr(u8 xPos, u8 yPos) {
                            133 ;	---------------------------------
                            134 ; Function GetBackBufferPtr
                            135 ; ---------------------------------
   4823                     136 _GetBackBufferPtr::
                            137 ;src/manageVideoMem.c:88: if (gVMem == VIDEO_MEM) backBufferStart = (u8*)SCREEN_BUFF;
   4823 3A FB 5A      [13]  138 	ld	a,(#_gVMem + 0)
   4826 B7            [ 4]  139 	or	a, a
   4827 20 05         [12]  140 	jr	NZ,00102$
   4829 01 00 80      [10]  141 	ld	bc, #0x8000
   482C 18 03         [12]  142 	jr	00103$
   482E                     143 00102$:
                            144 ;src/manageVideoMem.c:89: else                    backBufferStart = (u8*)CPCT_VMEM_START;
   482E 01 00 C0      [10]  145 	ld	bc, #0xc000
   4831                     146 00103$:
                            147 ;src/manageVideoMem.c:92: return cpct_getScreenPtr(backBufferStart, xPos, yPos);
   4831 21 03 00      [10]  148 	ld	hl, #3+0
   4834 39            [11]  149 	add	hl, sp
   4835 7E            [ 7]  150 	ld	a, (hl)
   4836 F5            [11]  151 	push	af
   4837 33            [ 6]  152 	inc	sp
   4838 21 03 00      [10]  153 	ld	hl, #3+0
   483B 39            [11]  154 	add	hl, sp
   483C 7E            [ 7]  155 	ld	a, (hl)
   483D F5            [11]  156 	push	af
   483E 33            [ 6]  157 	inc	sp
   483F C5            [11]  158 	push	bc
   4840 CD 3C 4E      [17]  159 	call	_cpct_getScreenPtr
   4843 C9            [10]  160 	ret
                            161 ;src/manageVideoMem.c:99: u8* GetSpriteBackBufferPtr(u8 xPos, u8 yPos) {
                            162 ;	---------------------------------
                            163 ; Function GetSpriteBackBufferPtr
                            164 ; ---------------------------------
   4844                     165 _GetSpriteBackBufferPtr::
   4844 DD E5         [15]  166 	push	ix
   4846 DD 21 00 00   [14]  167 	ld	ix,#0
   484A DD 39         [15]  168 	add	ix,sp
                            169 ;src/manageVideoMem.c:100: return cpctm_spriteBufferPtr(gSpriteBackBuffer, VIEW_W_BYTES, xPos, yPos);
   484C 01 43 4F      [10]  170 	ld	bc, #_gSpriteBackBuffer+0
   484F DD 5E 05      [19]  171 	ld	e,5 (ix)
   4852 16 00         [ 7]  172 	ld	d,#0x00
   4854 6B            [ 4]  173 	ld	l, e
   4855 62            [ 4]  174 	ld	h, d
   4856 29            [11]  175 	add	hl, hl
   4857 19            [11]  176 	add	hl, de
   4858 29            [11]  177 	add	hl, hl
   4859 29            [11]  178 	add	hl, hl
   485A 29            [11]  179 	add	hl, hl
   485B 19            [11]  180 	add	hl, de
   485C 29            [11]  181 	add	hl, hl
   485D 09            [11]  182 	add	hl,bc
   485E 4D            [ 4]  183 	ld	c, l
   485F 44            [ 4]  184 	ld	b, h
   4860 DD 6E 04      [19]  185 	ld	l,4 (ix)
   4863 26 00         [ 7]  186 	ld	h,#0x00
   4865 09            [11]  187 	add	hl, bc
   4866 DD E1         [14]  188 	pop	ix
   4868 C9            [10]  189 	ret
                            190 ;src/manageVideoMem.c:110: void DrawSpriteBackBufferToScreen() {
                            191 ;	---------------------------------
                            192 ; Function DrawSpriteBackBufferToScreen
                            193 ; ---------------------------------
   4869                     194 _DrawSpriteBackBufferToScreen::
                            195 ;src/manageVideoMem.c:112: u8*   pVideoMemLocation = GetScreenPtr(VIEW_X, VIEW_Y);
   4869 21 0F 00      [10]  196 	ld	hl, #0x000f
   486C E5            [11]  197 	push	hl
   486D CD 02 48      [17]  198 	call	_GetScreenPtr
                            199 ;src/manageVideoMem.c:115: cpct_waitVSYNC();
   4870 E3            [19]  200 	ex	(sp),hl
   4871 CD 01 4D      [17]  201 	call	_cpct_waitVSYNC
   4874 C1            [10]  202 	pop	bc
                            203 ;src/manageVideoMem.c:116: cpct_drawSprite(gSpriteBackBuffer, pVideoMemLocation, VIEW_W_BYTES, VIEW_H_BYTES);
   4875 21 32 3C      [10]  204 	ld	hl, #0x3c32
   4878 E5            [11]  205 	push	hl
   4879 C5            [11]  206 	push	bc
   487A 21 43 4F      [10]  207 	ld	hl, #_gSpriteBackBuffer
   487D E5            [11]  208 	push	hl
   487E CD 72 4B      [17]  209 	call	_cpct_drawSprite
   4881 C9            [10]  210 	ret
                            211 	.area _CODE
                            212 	.area _INITIALIZER
                            213 	.area _CABS (ABS)
