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
                             12 	.globl _initialize_cpc
                             13 	.globl _cpct_setVideoMode
                             14 	.globl _cpct_drawCharM0
                             15 	.globl _cpct_setDrawCharM0
                             16 	.globl _cpct_getKeypressedAsASCII
                             17 	.globl _cpct_scanKeyboard_f
                             18 	.globl _cpct_disableFirmware
                             19 ;--------------------------------------------------------
                             20 ; special function registers
                             21 ;--------------------------------------------------------
                             22 ;--------------------------------------------------------
                             23 ; ram data
                             24 ;--------------------------------------------------------
                             25 	.area _DATA
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
                             50 ;src/main.c:23: void initialize_cpc() {
                             51 ;	---------------------------------
                             52 ; Function initialize_cpc
                             53 ; ---------------------------------
   4000                      54 _initialize_cpc::
                             55 ;src/main.c:24: cpct_disableFirmware();    // Disable firmware to prevent it from interfering with setPalette and setVideoMode
   4000 CD 44 41      [17]   56 	call	_cpct_disableFirmware
                             57 ;src/main.c:25: cpct_setVideoMode(0);      // Set video mode 0 (160x200, 16 colours)
   4003 2E 00         [ 7]   58 	ld	l, #0x00
   4005 CD 36 41      [17]   59 	call	_cpct_setVideoMode
                             60 ;src/main.c:26: cpct_setDrawCharM0(3, 0);  // Set PEN 3, PAPER 0 for Characters to be drawn using cpct_drawCharM0
   4008 21 03 00      [10]   61 	ld	hl, #0x0003
   400B E5            [11]   62 	push	hl
   400C CD 55 41      [17]   63 	call	_cpct_setDrawCharM0
   400F C9            [10]   64 	ret
                             65 ;src/main.c:32: void main(void) {
                             66 ;	---------------------------------
                             67 ; Function main
                             68 ; ---------------------------------
   4010                      69 _main::
                             70 ;src/main.c:33: initialize_cpc();    // Initialize the CPC
   4010 CD 00 40      [17]   71 	call	_initialize_cpc
                             72 ;src/main.c:38: while(1) {
   4013                      73 00104$:
                             74 ;src/main.c:44: cpct_scanKeyboard_f();
   4013 CD 2A 40      [17]   75 	call	_cpct_scanKeyboard_f
                             76 ;src/main.c:47: ascii = cpct_getKeypressedAsASCII();
   4016 CD C1 40      [17]   77 	call	_cpct_getKeypressedAsASCII
                             78 ;src/main.c:48: if (ascii != 0) {                            // ascii == 0 means no key is pressed, so we check first
   4019 7D            [ 4]   79 	ld	a,l
   401A 4F            [ 4]   80 	ld	c,a
   401B B7            [ 4]   81 	or	a, a
   401C 28 F5         [12]   82 	jr	Z,00104$
                             83 ;src/main.c:49: cpct_drawCharM0(CPCT_VMEM_START, ascii);  // Some key is pressed, print its ascii value to the screen
   401E 06 00         [ 7]   84 	ld	b, #0x00
   4020 C5            [11]   85 	push	bc
   4021 21 00 C0      [10]   86 	ld	hl, #0xc000
   4024 E5            [11]   87 	push	hl
   4025 CD 94 40      [17]   88 	call	_cpct_drawCharM0
   4028 18 E9         [12]   89 	jr	00104$
                             90 	.area _CODE
                             91 	.area _INITIALIZER
                             92 	.area _CABS (ABS)
