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
                             12 	.globl _Initialization
                             13 	.globl _DrawStars
                             14 	.globl _DrawSceneBalloons
                             15 	.globl _UpdateBalloons
                             16 	.globl _InitializeDrawing
                             17 	.globl _FlipBuffers
                             18 	.globl _InitializeVideoMemoryBuffers
                             19 	.globl _cpct_setPALColour
                             20 	.globl _cpct_setPalette
                             21 	.globl _cpct_setVideoMode
                             22 	.globl _cpct_setStackLocation
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
                             55 ;src/main.c:25: cpctm_createTransparentMaskTable(gMaskTable, MASK_TABLE_LOC, M0, 0);
                             56 ;	---------------------------------
                             57 ; Function dummy_cpct_transparentMaskTable0M0_container
                             58 ; ---------------------------------
   105D                      59 _dummy_cpct_transparentMaskTable0M0_container::
                             60 	.area _gMaskTable_ (ABS) 
   7F00                      61 	.org (0x8000 - 0x100) 
   7F00                      62 	 _gMaskTable::
   7F00 FF AA 55 00 AA AA    63 	.db 0xFF, 0xAA, 0x55, 0x00, 0xAA, 0xAA, 0x00, 0x00 
        00 00
   7F08 55 00 55 00 00 00    64 	.db 0x55, 0x00, 0x55, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   7F10 AA AA 00 00 AA AA    65 	.db 0xAA, 0xAA, 0x00, 0x00, 0xAA, 0xAA, 0x00, 0x00 
        00 00
   7F18 00 00 00 00 00 00    66 	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   7F20 55 00 55 00 00 00    67 	.db 0x55, 0x00, 0x55, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   7F28 55 00 55 00 00 00    68 	.db 0x55, 0x00, 0x55, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   7F30 00 00 00 00 00 00    69 	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   7F38 00 00 00 00 00 00    70 	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   7F40 AA AA 00 00 AA AA    71 	.db 0xAA, 0xAA, 0x00, 0x00, 0xAA, 0xAA, 0x00, 0x00 
        00 00
   7F48 00 00 00 00 00 00    72 	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   7F50 AA AA 00 00 AA AA    73 	.db 0xAA, 0xAA, 0x00, 0x00, 0xAA, 0xAA, 0x00, 0x00 
        00 00
   7F58 00 00 00 00 00 00    74 	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   7F60 00 00 00 00 00 00    75 	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   7F68 00 00 00 00 00 00    76 	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   7F70 00 00 00 00 00 00    77 	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   7F78 00 00 00 00 00 00    78 	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   7F80 55 00 55 00 00 00    79 	.db 0x55, 0x00, 0x55, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   7F88 55 00 55 00 00 00    80 	.db 0x55, 0x00, 0x55, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   7F90 00 00 00 00 00 00    81 	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   7F98 00 00 00 00 00 00    82 	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   7FA0 55 00 55 00 00 00    83 	.db 0x55, 0x00, 0x55, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   7FA8 55 00 55 00 00 00    84 	.db 0x55, 0x00, 0x55, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   7FB0 00 00 00 00 00 00    85 	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   7FB8 00 00 00 00 00 00    86 	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   7FC0 00 00 00 00 00 00    87 	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   7FC8 00 00 00 00 00 00    88 	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   7FD0 00 00 00 00 00 00    89 	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   7FD8 00 00 00 00 00 00    90 	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   7FE0 00 00 00 00 00 00    91 	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   7FE8 00 00 00 00 00 00    92 	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   7FF0 00 00 00 00 00 00    93 	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   7FF8 00 00 00 00 00 00    94 	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
                             95 	.area _CSEG (REL, CON) 
                             96 ;src/main.c:32: void Initialization()
                             97 ;	---------------------------------
                             98 ; Function Initialization
                             99 ; ---------------------------------
   1704                     100 _Initialization::
                            101 ;src/main.c:36: cpct_disableFirmware();
   1704 CD B9 13      [17]  102 	call	_cpct_disableFirmware
                            103 ;src/main.c:37: cpct_setVideoMode(0);            // Set mode 0
   1707 2E 00         [ 7]  104 	ld	l, #0x00
   1709 CD 6F 13      [17]  105 	call	_cpct_setVideoMode
                            106 ;src/main.c:38: cpct_setPalette(g_palette, 16);  // Set the palette
   170C 21 10 00      [10]  107 	ld	hl, #0x0010
   170F E5            [11]  108 	push	hl
   1710 21 5A 0B      [10]  109 	ld	hl, #_g_palette
   1713 E5            [11]  110 	push	hl
   1714 CD C4 10      [17]  111 	call	_cpct_setPalette
                            112 ;src/main.c:39: cpct_setBorder(HW_SKY_BLUE);     // Set the border color with Hardware color
   1717 21 10 17      [10]  113 	ld	hl, #0x1710
   171A E5            [11]  114 	push	hl
   171B CD DB 10      [17]  115 	call	_cpct_setPALColour
                            116 ;src/main.c:41: InitializeVideoMemoryBuffers();  // Initialize video buffers    
   171E CD 5D 10      [17]  117 	call	_InitializeVideoMemoryBuffers
                            118 ;src/main.c:42: InitializeDrawing();             // Initialize drawing elements
   1721 CD 50 10      [17]  119 	call	_InitializeDrawing
   1724 C9            [10]  120 	ret
                            121 ;src/main.c:48: void main(void) 
                            122 ;	---------------------------------
                            123 ; Function main
                            124 ; ---------------------------------
   1725                     125 _main::
                            126 ;src/main.c:53: cpct_setStackLocation((u8*)NEW_STACK_LOC);
   1725 21 00 7E      [10]  127 	ld	hl, #0x7e00
   1728 CD 0F 13      [17]  128 	call	_cpct_setStackLocation
                            129 ;src/main.c:56: Initialization();
   172B CD 04 17      [17]  130 	call	_Initialization
                            131 ;src/main.c:59: while (TRUE)
   172E                     132 00102$:
                            133 ;src/main.c:61: UpdateBalloons();
   172E CD 90 0C      [17]  134 	call	_UpdateBalloons
                            135 ;src/main.c:62: DrawSceneBalloons();
   1731 CD 94 0F      [17]  136 	call	_DrawSceneBalloons
                            137 ;src/main.c:63: DrawStars();
   1734 CD A7 0E      [17]  138 	call	_DrawStars
                            139 ;src/main.c:67: FlipBuffers();        
   1737 CD 63 10      [17]  140 	call	_FlipBuffers
   173A 18 F2         [12]  141 	jr	00102$
                            142 	.area _CODE
                            143 	.area _INITIALIZER
                            144 	.area _CABS (ABS)
