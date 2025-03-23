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
                             13 	.globl _CheckUserInput
                             14 	.globl _ScrollAndDrawSpace
                             15 	.globl _SelectDrawFunction
                             16 	.globl _InitializeDrawing
                             17 	.globl _DrawTextSelectionSign
                             18 	.globl _DrawInfoText
                             19 	.globl _InitializeVideoMemoryBuffers
                             20 	.globl _cpct_setPalette
                             21 	.globl _cpct_isKeyPressed
                             22 	.globl _cpct_scanKeyboard_f
                             23 	.globl _cpct_setStackLocation
                             24 	.globl _cpct_disableFirmware
                             25 ;--------------------------------------------------------
                             26 ; special function registers
                             27 ;--------------------------------------------------------
                             28 ;--------------------------------------------------------
                             29 ; ram data
                             30 ;--------------------------------------------------------
                             31 	.area _DATA
                             32 ;--------------------------------------------------------
                             33 ; ram data
                             34 ;--------------------------------------------------------
                             35 	.area _INITIALIZED
                             36 ;--------------------------------------------------------
                             37 ; absolute external ram data
                             38 ;--------------------------------------------------------
                             39 	.area _DABS (ABS)
                             40 ;--------------------------------------------------------
                             41 ; global & static initialisations
                             42 ;--------------------------------------------------------
                             43 	.area _HOME
                             44 	.area _GSINIT
                             45 	.area _GSFINAL
                             46 	.area _GSINIT
                             47 ;--------------------------------------------------------
                             48 ; Home
                             49 ;--------------------------------------------------------
                             50 	.area _HOME
                             51 	.area _HOME
                             52 ;--------------------------------------------------------
                             53 ; code
                             54 ;--------------------------------------------------------
                             55 	.area _CODE
                             56 ;src/main.c:24: cpctm_createTransparentMaskTable(gMaskTable, MASK_TABLE_LOCATION, M1, 0);
                             57 ;	---------------------------------
                             58 ; Function dummy_cpct_transparentMaskTable0M1_container
                             59 ; ---------------------------------
   47D0                      60 _dummy_cpct_transparentMaskTable0M1_container::
                             61 	.area _gMaskTable_ (ABS) 
   7F00                      62 	.org (0x8000 - 0x100) 
   7F00                      63 	 _gMaskTable::
   7F00 FF EE DD CC BB AA    64 	.db 0xFF, 0xEE, 0xDD, 0xCC, 0xBB, 0xAA, 0x99, 0x88 
        99 88
   7F08 77 66 55 44 33 22    65 	.db 0x77, 0x66, 0x55, 0x44, 0x33, 0x22, 0x11, 0x00 
        11 00
   7F10 EE EE CC CC AA AA    66 	.db 0xEE, 0xEE, 0xCC, 0xCC, 0xAA, 0xAA, 0x88, 0x88 
        88 88
   7F18 66 66 44 44 22 22    67 	.db 0x66, 0x66, 0x44, 0x44, 0x22, 0x22, 0x00, 0x00 
        00 00
   7F20 DD CC DD CC 99 88    68 	.db 0xDD, 0xCC, 0xDD, 0xCC, 0x99, 0x88, 0x99, 0x88 
        99 88
   7F28 55 44 55 44 11 00    69 	.db 0x55, 0x44, 0x55, 0x44, 0x11, 0x00, 0x11, 0x00 
        11 00
   7F30 CC CC CC CC 88 88    70 	.db 0xCC, 0xCC, 0xCC, 0xCC, 0x88, 0x88, 0x88, 0x88 
        88 88
   7F38 44 44 44 44 00 00    71 	.db 0x44, 0x44, 0x44, 0x44, 0x00, 0x00, 0x00, 0x00 
        00 00
   7F40 BB AA 99 88 BB AA    72 	.db 0xBB, 0xAA, 0x99, 0x88, 0xBB, 0xAA, 0x99, 0x88 
        99 88
   7F48 33 22 11 00 33 22    73 	.db 0x33, 0x22, 0x11, 0x00, 0x33, 0x22, 0x11, 0x00 
        11 00
   7F50 AA AA 88 88 AA AA    74 	.db 0xAA, 0xAA, 0x88, 0x88, 0xAA, 0xAA, 0x88, 0x88 
        88 88
   7F58 22 22 00 00 22 22    75 	.db 0x22, 0x22, 0x00, 0x00, 0x22, 0x22, 0x00, 0x00 
        00 00
   7F60 99 88 99 88 99 88    76 	.db 0x99, 0x88, 0x99, 0x88, 0x99, 0x88, 0x99, 0x88 
        99 88
   7F68 11 00 11 00 11 00    77 	.db 0x11, 0x00, 0x11, 0x00, 0x11, 0x00, 0x11, 0x00 
        11 00
   7F70 88 88 88 88 88 88    78 	.db 0x88, 0x88, 0x88, 0x88, 0x88, 0x88, 0x88, 0x88 
        88 88
   7F78 00 00 00 00 00 00    79 	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   7F80 77 66 55 44 33 22    80 	.db 0x77, 0x66, 0x55, 0x44, 0x33, 0x22, 0x11, 0x00 
        11 00
   7F88 77 66 55 44 33 22    81 	.db 0x77, 0x66, 0x55, 0x44, 0x33, 0x22, 0x11, 0x00 
        11 00
   7F90 66 66 44 44 22 22    82 	.db 0x66, 0x66, 0x44, 0x44, 0x22, 0x22, 0x00, 0x00 
        00 00
   7F98 66 66 44 44 22 22    83 	.db 0x66, 0x66, 0x44, 0x44, 0x22, 0x22, 0x00, 0x00 
        00 00
   7FA0 55 44 55 44 11 00    84 	.db 0x55, 0x44, 0x55, 0x44, 0x11, 0x00, 0x11, 0x00 
        11 00
   7FA8 55 44 55 44 11 00    85 	.db 0x55, 0x44, 0x55, 0x44, 0x11, 0x00, 0x11, 0x00 
        11 00
   7FB0 44 44 44 44 00 00    86 	.db 0x44, 0x44, 0x44, 0x44, 0x00, 0x00, 0x00, 0x00 
        00 00
   7FB8 44 44 44 44 00 00    87 	.db 0x44, 0x44, 0x44, 0x44, 0x00, 0x00, 0x00, 0x00 
        00 00
   7FC0 33 22 11 00 33 22    88 	.db 0x33, 0x22, 0x11, 0x00, 0x33, 0x22, 0x11, 0x00 
        11 00
   7FC8 33 22 11 00 33 22    89 	.db 0x33, 0x22, 0x11, 0x00, 0x33, 0x22, 0x11, 0x00 
        11 00
   7FD0 22 22 00 00 22 22    90 	.db 0x22, 0x22, 0x00, 0x00, 0x22, 0x22, 0x00, 0x00 
        00 00
   7FD8 22 22 00 00 22 22    91 	.db 0x22, 0x22, 0x00, 0x00, 0x22, 0x22, 0x00, 0x00 
        00 00
   7FE0 11 00 11 00 11 00    92 	.db 0x11, 0x00, 0x11, 0x00, 0x11, 0x00, 0x11, 0x00 
        11 00
   7FE8 11 00 11 00 11 00    93 	.db 0x11, 0x00, 0x11, 0x00, 0x11, 0x00, 0x11, 0x00 
        11 00
   7FF0 00 00 00 00 00 00    94 	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
   7FF8 00 00 00 00 00 00    95 	.db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
        00 00
                             96 	.area _CSEG (REL, CON) 
                             97 ;src/main.c:31: void CheckUserInput() {
                             98 ;	---------------------------------
                             99 ; Function CheckUserInput
                            100 ; ---------------------------------
   5AFC                     101 _CheckUserInput::
                            102 ;src/main.c:32: cpct_scanKeyboard_f();
   5AFC CD D8 4A      [17]  103 	call	_cpct_scanKeyboard_f
                            104 ;src/main.c:34: if       (cpct_isKeyPressed(Key_1)) { SelectDrawFunction(1); DrawTextSelectionSign(1); }
   5AFF 21 08 01      [10]  105 	ld	hl, #0x0108
   5B02 CD CC 4A      [17]  106 	call	_cpct_isKeyPressed
   5B05 7D            [ 4]  107 	ld	a, l
   5B06 B7            [ 4]  108 	or	a, a
   5B07 28 11         [12]  109 	jr	Z,00107$
   5B09 3E 01         [ 7]  110 	ld	a, #0x01
   5B0B F5            [11]  111 	push	af
   5B0C 33            [ 6]  112 	inc	sp
   5B0D CD 8A 47      [17]  113 	call	_SelectDrawFunction
   5B10 33            [ 6]  114 	inc	sp
   5B11 3E 01         [ 7]  115 	ld	a, #0x01
   5B13 F5            [11]  116 	push	af
   5B14 33            [ 6]  117 	inc	sp
   5B15 CD 8E 4A      [17]  118 	call	_DrawTextSelectionSign
   5B18 33            [ 6]  119 	inc	sp
   5B19 C9            [10]  120 	ret
   5B1A                     121 00107$:
                            122 ;src/main.c:35: else if  (cpct_isKeyPressed(Key_2)) { SelectDrawFunction(2); DrawTextSelectionSign(2); }
   5B1A 21 08 02      [10]  123 	ld	hl, #0x0208
   5B1D CD CC 4A      [17]  124 	call	_cpct_isKeyPressed
   5B20 7D            [ 4]  125 	ld	a, l
   5B21 B7            [ 4]  126 	or	a, a
   5B22 28 11         [12]  127 	jr	Z,00104$
   5B24 3E 02         [ 7]  128 	ld	a, #0x02
   5B26 F5            [11]  129 	push	af
   5B27 33            [ 6]  130 	inc	sp
   5B28 CD 8A 47      [17]  131 	call	_SelectDrawFunction
   5B2B 33            [ 6]  132 	inc	sp
   5B2C 3E 02         [ 7]  133 	ld	a, #0x02
   5B2E F5            [11]  134 	push	af
   5B2F 33            [ 6]  135 	inc	sp
   5B30 CD 8E 4A      [17]  136 	call	_DrawTextSelectionSign
   5B33 33            [ 6]  137 	inc	sp
   5B34 C9            [10]  138 	ret
   5B35                     139 00104$:
                            140 ;src/main.c:36: else if  (cpct_isKeyPressed(Key_3)) { SelectDrawFunction(3); DrawTextSelectionSign(3); }
   5B35 21 07 02      [10]  141 	ld	hl, #0x0207
   5B38 CD CC 4A      [17]  142 	call	_cpct_isKeyPressed
   5B3B 7D            [ 4]  143 	ld	a, l
   5B3C B7            [ 4]  144 	or	a, a
   5B3D C8            [11]  145 	ret	Z
   5B3E 3E 03         [ 7]  146 	ld	a, #0x03
   5B40 F5            [11]  147 	push	af
   5B41 33            [ 6]  148 	inc	sp
   5B42 CD 8A 47      [17]  149 	call	_SelectDrawFunction
   5B45 33            [ 6]  150 	inc	sp
   5B46 3E 03         [ 7]  151 	ld	a, #0x03
   5B48 F5            [11]  152 	push	af
   5B49 33            [ 6]  153 	inc	sp
   5B4A CD 8E 4A      [17]  154 	call	_DrawTextSelectionSign
   5B4D 33            [ 6]  155 	inc	sp
   5B4E C9            [10]  156 	ret
                            157 ;src/main.c:44: void Initialization() {
                            158 ;	---------------------------------
                            159 ; Function Initialization
                            160 ; ---------------------------------
   5B4F                     161 _Initialization::
                            162 ;src/main.c:47: cpct_disableFirmware(); 
   5B4F CD 17 4D      [17]  163 	call	_cpct_disableFirmware
                            164 ;src/main.c:48: cpct_setPalette(g_palette, 5);   // Set the palette
   5B52 21 05 00      [10]  165 	ld	hl, #0x0005
   5B55 E5            [11]  166 	push	hl
   5B56 21 B0 41      [10]  167 	ld	hl, #_g_palette
   5B59 E5            [11]  168 	push	hl
   5B5A CD B5 4A      [17]  169 	call	_cpct_setPalette
                            170 ;src/main.c:49: InitializeVideoMemoryBuffers();  // Initialize video buffers
   5B5D CD D0 47      [17]  171 	call	_InitializeVideoMemoryBuffers
                            172 ;src/main.c:50: InitializeDrawing();             // Initialize Drawing Module
   5B60 CD 57 45      [17]  173 	call	_InitializeDrawing
                            174 ;src/main.c:51: SelectDrawFunction(1);           // Select the 1st Drawing function
   5B63 3E 01         [ 7]  175 	ld	a, #0x01
   5B65 F5            [11]  176 	push	af
   5B66 33            [ 6]  177 	inc	sp
   5B67 CD 8A 47      [17]  178 	call	_SelectDrawFunction
   5B6A 33            [ 6]  179 	inc	sp
                            180 ;src/main.c:52: DrawTextSelectionSign(1);        // Mark 1st Drawing function as Selected
   5B6B 3E 01         [ 7]  181 	ld	a, #0x01
   5B6D F5            [11]  182 	push	af
   5B6E 33            [ 6]  183 	inc	sp
   5B6F CD 8E 4A      [17]  184 	call	_DrawTextSelectionSign
   5B72 33            [ 6]  185 	inc	sp
                            186 ;src/main.c:53: DrawInfoText();                  // Draw User Info Text 
   5B73 CD 38 4A      [17]  187 	call	_DrawInfoText
   5B76 C9            [10]  188 	ret
                            189 ;src/main.c:59: void main(void) {
                            190 ;	---------------------------------
                            191 ; Function main
                            192 ; ---------------------------------
   5B77                     193 _main::
                            194 ;src/main.c:63: cpct_setStackLocation((u8*)NEW_STACK_LOCATION);
   5B77 21 00 7E      [10]  195 	ld	hl, #0x7e00
   5B7A CD DE 4C      [17]  196 	call	_cpct_setStackLocation
                            197 ;src/main.c:66: Initialization();
   5B7D CD 4F 5B      [17]  198 	call	_Initialization
                            199 ;src/main.c:69: while(1) {
   5B80                     200 00102$:
                            201 ;src/main.c:70: CheckUserInput();
   5B80 CD FC 5A      [17]  202 	call	_CheckUserInput
                            203 ;src/main.c:71: ScrollAndDrawSpace();
   5B83 CD C6 47      [17]  204 	call	_ScrollAndDrawSpace
   5B86 18 F8         [12]  205 	jr	00102$
                            206 	.area _CODE
                            207 	.area _INITIALIZER
                            208 	.area _CABS (ABS)
