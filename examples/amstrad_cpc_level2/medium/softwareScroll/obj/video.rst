                              1 ;--------------------------------------------------------
                              2 ; File Created by SDCC : free open source ANSI-C Compiler
                              3 ; Version 3.6.8 #9946 (Linux)
                              4 ;--------------------------------------------------------
                              5 	.module video
                              6 	.optsdcc -mz80
                              7 	
                              8 ;--------------------------------------------------------
                              9 ; Public variables in this module
                             10 ;--------------------------------------------------------
                             11 	.globl _video_initBuffers
                             12 	.globl _video_switchBuffers
                             13 	.globl _video_getBackBufferPtr
                             14 	.globl _cpct_setVideoMemoryPage
                             15 	.globl _cpct_memset
                             16 	.globl _video_buffer
                             17 ;--------------------------------------------------------
                             18 ; special function registers
                             19 ;--------------------------------------------------------
                             20 ;--------------------------------------------------------
                             21 ; ram data
                             22 ;--------------------------------------------------------
                             23 	.area _DATA
   4BA8                      24 _video_buffer::
   4BA8                      25 	.ds 2
                             26 ;--------------------------------------------------------
                             27 ; ram data
                             28 ;--------------------------------------------------------
                             29 	.area _INITIALIZED
                             30 ;--------------------------------------------------------
                             31 ; absolute external ram data
                             32 ;--------------------------------------------------------
                             33 	.area _DABS (ABS)
                             34 ;--------------------------------------------------------
                             35 ; global & static initialisations
                             36 ;--------------------------------------------------------
                             37 	.area _HOME
                             38 	.area _GSINIT
                             39 	.area _GSFINAL
                             40 	.area _GSINIT
                             41 ;--------------------------------------------------------
                             42 ; Home
                             43 ;--------------------------------------------------------
                             44 	.area _HOME
                             45 	.area _HOME
                             46 ;--------------------------------------------------------
                             47 ; code
                             48 ;--------------------------------------------------------
                             49 	.area _CODE
                             50 ;src/video.c:51: u8* video_getBackBufferPtr() {
                             51 ;	---------------------------------
                             52 ; Function video_getBackBufferPtr
                             53 ; ---------------------------------
   49A2                      54 _video_getBackBufferPtr::
                             55 ;src/video.c:52: return video_buffer;
   49A2 2A A8 4B      [16]   56 	ld	hl, (_video_buffer)
   49A5 C9            [10]   57 	ret
                             58 ;src/video.c:61: void video_switchBuffers() {
                             59 ;	---------------------------------
                             60 ; Function video_switchBuffers
                             61 ; ---------------------------------
   49A6                      62 _video_switchBuffers::
                             63 ;src/video.c:66: if (video_buffer == HW_BACKBUFFER) {
   49A6 FD 21 A8 4B   [14]   64 	ld	iy, #_video_buffer
   49AA FD 7E 00      [19]   65 	ld	a, 0 (iy)
   49AD B7            [ 4]   66 	or	a, a
   49AE 20 13         [12]   67 	jr	NZ,00102$
   49B0 FD 7E 01      [19]   68 	ld	a, 1 (iy)
   49B3 D6 80         [ 7]   69 	sub	a, #0x80
   49B5 20 0C         [12]   70 	jr	NZ,00102$
                             71 ;src/video.c:69: cpct_setVideoMemoryPage(cpct_page80);
   49B7 2E 20         [ 7]   72 	ld	l, #0x20
   49B9 CD 28 4B      [17]   73 	call	_cpct_setVideoMemoryPage
                             74 ;src/video.c:70: video_buffer = CPCT_VMEM_START;
   49BC 21 00 C0      [10]   75 	ld	hl, #0xc000
   49BF 22 A8 4B      [16]   76 	ld	(_video_buffer), hl
   49C2 C9            [10]   77 	ret
   49C3                      78 00102$:
                             79 ;src/video.c:74: cpct_setVideoMemoryPage(cpct_pageC0);
   49C3 2E 30         [ 7]   80 	ld	l, #0x30
   49C5 CD 28 4B      [17]   81 	call	_cpct_setVideoMemoryPage
                             82 ;src/video.c:75: video_buffer = HW_BACKBUFFER;
   49C8 21 00 80      [10]   83 	ld	hl, #0x8000
   49CB 22 A8 4B      [16]   84 	ld	(_video_buffer), hl
   49CE C9            [10]   85 	ret
                             86 ;src/video.c:83: void video_initBuffers() {
                             87 ;	---------------------------------
                             88 ; Function video_initBuffers
                             89 ; ---------------------------------
   49CF                      90 _video_initBuffers::
                             91 ;src/video.c:86: cpct_memset(HW_BACKBUFFER, 0, 0x4000);  // 16K HW_BACKBUFFER set to 0
   49CF 21 00 40      [10]   92 	ld	hl, #0x4000
   49D2 E5            [11]   93 	push	hl
   49D3 AF            [ 4]   94 	xor	a, a
   49D4 F5            [11]   95 	push	af
   49D5 33            [ 6]   96 	inc	sp
   49D6 26 80         [ 7]   97 	ld	h, #0x80
   49D8 E5            [11]   98 	push	hl
   49D9 CD 43 4B      [17]   99 	call	_cpct_memset
                            100 ;src/video.c:91: video_switchBuffers();
   49DC CD A6 49      [17]  101 	call	_video_switchBuffers
   49DF C9            [10]  102 	ret
                            103 	.area _CODE
                            104 	.area _INITIALIZER
                            105 	.area _CABS (ABS)
