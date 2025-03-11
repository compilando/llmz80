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
                             13 	.globl _cpct_etm_drawTilemap4x8_ag
                             14 	.globl _cpct_etm_setDrawTilemap4x8_ag
                             15 	.globl _cpct_setPALColour
                             16 	.globl _cpct_setPalette
                             17 	.globl _cpct_setVideoMode
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
                             50 ;src/main.c:79: void initialize() {
                             51 ;	---------------------------------
                             52 ; Function initialize
                             53 ; ---------------------------------
   4C9C                      54 _initialize::
                             55 ;src/main.c:82: cpct_disableFirmware();          // Disable firmware 
   4C9C CD AB 4D      [17]   56 	call	_cpct_disableFirmware
                             57 ;src/main.c:83: cpct_setVideoMode(0);            // Set Video Mode 0 (160x200, 16 colours)
   4C9F 2E 00         [ 7]   58 	ld	l, #0x00
   4CA1 CD 9D 4D      [17]   59 	call	_cpct_setVideoMode
                             60 ;src/main.c:84: cpct_setPalette(g_palette, 16);  // Set palette colours (g_palette is generated in tiles.c)
   4CA4 21 10 00      [10]   61 	ld	hl, #0x0010
   4CA7 E5            [11]   62 	push	hl
   4CA8 21 8C 41      [10]   63 	ld	hl, #_g_palette
   4CAB E5            [11]   64 	push	hl
   4CAC CD D5 4C      [17]   65 	call	_cpct_setPalette
                             66 ;src/main.c:85: cpct_setBorder(HW_BLACK);        // Set border colour to black
   4CAF 21 10 14      [10]   67 	ld	hl, #0x1410
   4CB2 E5            [11]   68 	push	hl
   4CB3 CD EC 4C      [17]   69 	call	_cpct_setPALColour
   4CB6 C9            [10]   70 	ret
                             71 ;src/main.c:92: void main(void) {
                             72 ;	---------------------------------
                             73 ; Function main
                             74 ; ---------------------------------
   4CB7                      75 _main::
                             76 ;src/main.c:93: initialize();  // Initialize the CPC
   4CB7 CD 9C 4C      [17]   77 	call	_initialize
                             78 ;src/main.c:103: cpct_etm_setDrawTilemap4x8_ag(g_courtMap_W, g_courtMap_H, g_courtMap_W, g_tiles_00);
   4CBA 21 9C 41      [10]   79 	ld	hl, #_g_tiles_00
   4CBD E5            [11]   80 	push	hl
   4CBE 21 12 00      [10]   81 	ld	hl, #0x0012
   4CC1 E5            [11]   82 	push	hl
   4CC2 26 16         [ 7]   83 	ld	h, #0x16
   4CC4 E5            [11]   84 	push	hl
   4CC5 CD BC 4D      [17]   85 	call	_cpct_etm_setDrawTilemap4x8_ag
                             86 ;src/main.c:111: cpct_etm_drawTilemap4x8_ag(TILEMAP_VMEM, g_courtMap);
   4CC8 21 00 40      [10]   87 	ld	hl, #_g_courtMap
   4CCB E5            [11]   88 	push	hl
   4CCC 21 A4 C0      [10]   89 	ld	hl, #0xc0a4
   4CCF E5            [11]   90 	push	hl
   4CD0 CD F8 4C      [17]   91 	call	_cpct_etm_drawTilemap4x8_ag
                             92 ;src/main.c:114: while (1);
   4CD3                      93 00102$:
   4CD3 18 FE         [12]   94 	jr	00102$
                             95 	.area _CODE
                             96 	.area _INITIALIZER
                             97 	.area _CABS (ABS)
