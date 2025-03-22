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
                             12 	.globl _cpct_setPalette
                             13 	.globl _cpct_setVideoMode
                             14 	.globl _cpct_drawSprite
                             15 	.globl _cpct_disableFirmware
                             16 	.globl _g_palette
                             17 ;--------------------------------------------------------
                             18 ; special function registers
                             19 ;--------------------------------------------------------
                             20 ;--------------------------------------------------------
                             21 ; ram data
                             22 ;--------------------------------------------------------
                             23 	.area _DATA
                             24 ;--------------------------------------------------------
                             25 ; ram data
                             26 ;--------------------------------------------------------
                             27 	.area _INITIALIZED
                             28 ;--------------------------------------------------------
                             29 ; absolute external ram data
                             30 ;--------------------------------------------------------
                             31 	.area _DABS (ABS)
                             32 ;--------------------------------------------------------
                             33 ; global & static initialisations
                             34 ;--------------------------------------------------------
                             35 	.area _HOME
                             36 	.area _GSINIT
                             37 	.area _GSFINAL
                             38 	.area _GSINIT
                             39 ;--------------------------------------------------------
                             40 ; Home
                             41 ;--------------------------------------------------------
                             42 	.area _HOME
                             43 	.area _HOME
                             44 ;--------------------------------------------------------
                             45 ; code
                             46 ;--------------------------------------------------------
                             47 	.area _CODE
                             48 ;src/main.c:41: void main(void) {
                             49 ;	---------------------------------
                             50 ; Function main
                             51 ; ---------------------------------
   40C0                      52 _main::
                             53 ;src/main.c:43: cpct_disableFirmware();          // Disable firmware (as we are going to use mode and colours)
   40C0 CD B3 41      [17]   54 	call	_cpct_disableFirmware
                             55 ;src/main.c:44: cpct_setVideoMode(0);            // Set video mode 0 (160x200, 16 colours)
   40C3 2E 00         [ 7]   56 	ld	l, #0x00
   40C5 CD A5 41      [17]   57 	call	_cpct_setVideoMode
                             58 ;src/main.c:45: cpct_setPalette(g_palette, 5);   // Set first 5 colours from our palette (we aren't going to use more)
   40C8 21 05 00      [10]   59 	ld	hl, #0x0005
   40CB E5            [11]   60 	push	hl
   40CC 21 E4 40      [10]   61 	ld	hl, #_g_palette
   40CF E5            [11]   62 	push	hl
   40D0 CD E9 40      [17]   63 	call	_cpct_setPalette
                             64 ;src/main.c:49: cpct_drawSprite(G_sprite, CPCT_VMEM_START, 8, 24);
   40D3 21 08 18      [10]   65 	ld	hl, #0x1808
   40D6 E5            [11]   66 	push	hl
   40D7 21 00 C0      [10]   67 	ld	hl, #0xc000
   40DA E5            [11]   68 	push	hl
   40DB 21 00 40      [10]   69 	ld	hl, #_G_sprite
   40DE E5            [11]   70 	push	hl
   40DF CD 00 41      [17]   71 	call	_cpct_drawSprite
                             72 ;src/main.c:52: while (1);
   40E2                      73 00102$:
   40E2 18 FE         [12]   74 	jr	00102$
   40E4                      75 _g_palette:
   40E4 14                   76 	.db #0x14	; 20
   40E5 15                   77 	.db #0x15	; 21
   40E6 13                   78 	.db #0x13	; 19
   40E7 16                   79 	.db #0x16	; 22
   40E8 0E                   80 	.db #0x0e	; 14
                             81 	.area _CODE
                             82 	.area _INITIALIZER
                             83 	.area _CABS (ABS)
