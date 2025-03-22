                              1 ;--------------------------------------------------------
                              2 ; File Created by SDCC : free open source ANSI-C Compiler
                              3 ; Version 3.6.8 #9946 (Linux)
                              4 ;--------------------------------------------------------
                              5 	.module interrupts
                              6 	.optsdcc -mz80
                              7 	
                              8 ;--------------------------------------------------------
                              9 ; Public variables in this module
                             10 ;--------------------------------------------------------
                             11 	.globl _dummy_MyInterruptWrapper
                             12 	.globl _myInterruptHandler
                             13 	.globl _cpct_setPALColour
                             14 ;--------------------------------------------------------
                             15 ; special function registers
                             16 ;--------------------------------------------------------
                             17 ;--------------------------------------------------------
                             18 ; ram data
                             19 ;--------------------------------------------------------
                             20 	.area _DATA
   416A                      21 _myInterruptHandler_i_1_128:
   416A                      22 	.ds 1
                             23 ;--------------------------------------------------------
                             24 ; ram data
                             25 ;--------------------------------------------------------
                             26 	.area _INITIALIZED
                             27 ;--------------------------------------------------------
                             28 ; absolute external ram data
                             29 ;--------------------------------------------------------
                             30 	.area _DABS (ABS)
                             31 ;--------------------------------------------------------
                             32 ; global & static initialisations
                             33 ;--------------------------------------------------------
                             34 	.area _HOME
                             35 	.area _GSINIT
                             36 	.area _GSFINAL
                             37 	.area _GSINIT
                             38 ;--------------------------------------------------------
                             39 ; Home
                             40 ;--------------------------------------------------------
                             41 	.area _HOME
                             42 	.area _HOME
                             43 ;--------------------------------------------------------
                             44 ; code
                             45 ;--------------------------------------------------------
                             46 	.area _CODE
                             47 ;src/interrupts.c:27: void myInterruptHandler() {
                             48 ;	---------------------------------
                             49 ; Function myInterruptHandler
                             50 ; ---------------------------------
   4000                      51 _myInterruptHandler::
                             52 ;src/interrupts.c:29: cpct_setBorder(i+1);    // Set the color of the border differently for each interrupt  
   4000 21 6A 41      [10]   53 	ld	hl,#_myInterruptHandler_i_1_128 + 0
   4003 46            [ 7]   54 	ld	b, (hl)
   4004 04            [ 4]   55 	inc	b
   4005 C5            [11]   56 	push	bc
   4006 33            [ 6]   57 	inc	sp
   4007 3E 10         [ 7]   58 	ld	a, #0x10
   4009 F5            [11]   59 	push	af
   400A 33            [ 6]   60 	inc	sp
   400B CD 7A 40      [17]   61 	call	_cpct_setPALColour
                             62 ;src/interrupts.c:30: if (++i > 5) i=0;       // Count one more interrupt. There are 6 interrupts in total (0-5)
   400E FD 21 6A 41   [14]   63 	ld	iy, #_myInterruptHandler_i_1_128
   4012 FD 34 00      [23]   64 	inc	0 (iy)
   4015 3E 05         [ 7]   65 	ld	a, #0x05
   4017 FD 96 00      [19]   66 	sub	a, 0 (iy)
   401A D0            [11]   67 	ret	NC
   401B FD 36 00 00   [19]   68 	ld	0 (iy), #0x00
   401F C9            [10]   69 	ret
                             70 ;src/interrupts.c:41: cpctm_createInterruptHandlerWrapper(MyInterruptWrapper, myInterruptHandler, af, bc, de, hl, ix, iy, alt, af, hl);
                             71 ;	---------------------------------
                             72 ; Function dummy_MyInterruptWrapper
                             73 ; ---------------------------------
   4020                      74 _dummy_MyInterruptWrapper::
                             75 	.include "firmware/cpctm_createInterruptHandlerWrapper.asm" 
                              1 ;;-----------------------------LICENSE NOTICE------------------------------------
                              2 ;;  This file is part of CPCtelera: An Amstrad CPC Game Engine
                              3 ;;  Copyright (C) 2021 ronaldo / Fremos / Cheesetea / ByteRealms (@FranGallegoBR)
                              4 ;;  Copyright (C) 2021 Nestornillo (https://github.com/nestornillo)
                              5 ;;
                              6 ;;  This program is free software: you can redistribute it and/or modify
                              7 ;;  it under the terms of the GNU Lesser General Public License as published by
                              8 ;;  the Free Software Foundation, either version 3 of the License, or
                              9 ;;  (at your option) any later version.
                             10 ;;
                             11 ;;  This program is distributed in the hope that it will be useful,
                             12 ;;  but WITHOUT ANY WARRANTY; without even the implied warranty of
                             13 ;;  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
                             14 ;;  GNU Lesser General Public License for more details.
                             15 ;;
                             16 ;;  You should have received a copy of the GNU Lesser General Public License
                             17 ;;  along with this program.  If not, see <http://www.gnu.org/licenses/>.
                             18 ;;-------------------------------------------------------------------------------
                             19 
                             20 ;;  cpctm_createInterruptHandlerWrapper_asm
                             21 ;;    Macro that creates a custom interrupt handler wrapper function.
                             22 ;;    See file firmware_macros.h.s for help.
                             23 
                             24 .mdelete cpct_checkReg_
                             25 .macro cpct_checkReg_
                             26 .endm
                             27 
                             28 .mdelete cpct_checkReg_alt
                             29 .macro cpct_checkReg_alt
                             30   .equ cpct_altDetected, 1
                             31 .endm
                             32 
                             33 .mdelete cpct_checkReg_af
                             34 .macro cpct_checkReg_af
                             35   .if cpct_altDetected
                             36     .equ cpct_altAFdetected, 1
                             37   .endif
                             38 .endm
                             39 
                             40 .mdelete cpct_checkReg_bc
                             41 .macro cpct_checkReg_bc
                             42   .if cpct_altDetected
                             43     .equ cpct_altBCDEHLdetected, 1
                             44   .endif
                             45 .endm
                             46 
                             47 .mdelete cpct_checkReg_de
                             48 .macro cpct_checkReg_de
                             49   .if cpct_altDetected
                             50     .equ cpct_altBCDEHLdetected, 1
                             51   .endif
                             52 .endm
                             53 
                             54 .mdelete cpct_checkReg_hl
                             55 .macro cpct_checkReg_hl
                             56   .if cpct_altDetected
                             57     .equ cpct_altBCDEHLdetected, 1
                             58   .endif
                             59 .endm
                             60 
                             61 .mdelete cpct_checkReg_ix
                             62 .macro cpct_checkReg_ix
                             63 .endm
                             64 
                             65 .mdelete cpct_checkReg_iy
                             66 .macro cpct_checkReg_iy
                             67 .endm
                             68 
                             69 .mdelete cpct_saveReg_
                             70 .macro cpct_saveReg_
                             71 .endm
                             72 
                             73 .mdelete cpct_saveReg_alt
                             74 .macro cpct_saveReg_alt
                             75   .if cpct_altAFdetected
                             76     ex af, af' ;; [1]
                             77   .endif
                             78   .if cpct_altBCDEHLdetected
                             79     exx        ;; [1]
                             80   .endif
                             81 .endm
                             82 
                             83 .mdelete cpct_saveReg_af
                             84 .macro cpct_saveReg_af
                             85   push af      ;; [4]
                             86 .endm
                             87 
                             88 .mdelete cpct_saveReg_bc
                             89 .macro cpct_saveReg_bc
                             90   push bc      ;; [4]
                             91 .endm
                             92 
                             93 .mdelete cpct_saveReg_de
                             94 .macro cpct_saveReg_de
                             95   push de      ;; [4]
                             96 .endm
                             97 
                             98 .mdelete cpct_saveReg_hl
                             99 .macro cpct_saveReg_hl
                            100   push hl      ;; [4]
                            101 .endm
                            102 
                            103 .mdelete cpct_saveReg_ix
                            104 .macro cpct_saveReg_ix
                            105   push ix      ;; [5]
                            106 .endm
                            107 
                            108 .mdelete cpct_saveReg_iy
                            109 .macro cpct_saveReg_iy
                            110   push iy      ;; [5]
                            111 .endm
                            112 
                            113 .mdelete cpct_restoreReg_
                            114 .macro cpct_restoreReg_
                            115 .endm
                            116 
                            117 .mdelete cpct_restoreReg_alt
                            118 .macro cpct_restoreReg_alt
                            119   .if cpct_altBCDEHLdetected
                            120     exx        ;; [1]
                            121   .endif
                            122   .if cpct_altAFdetected
                            123     ex af, af' ;; [1]
                            124   .endif
                            125 .endm
                            126 
                            127 .mdelete cpct_restoreReg_af
                            128 .macro cpct_restoreReg_af
                            129   pop af       ;; [3]
                            130 .endm
                            131 
                            132 .mdelete cpct_restoreReg_bc
                            133 .macro cpct_restoreReg_bc
                            134   pop bc       ;; [3]
                            135 .endm
                            136 
                            137 .mdelete cpct_restoreReg_de
                            138 .macro cpct_restoreReg_de
                            139   pop de       ;; [3]
                            140 .endm
                            141 
                            142 .mdelete cpct_restoreReg_hl
                            143 .macro cpct_restoreReg_hl
                            144   pop hl       ;; [3]
                            145 .endm
                            146 
                            147 .mdelete cpct_restoreReg_ix
                            148 .macro cpct_restoreReg_ix
                            149   pop ix       ;; [4]
                            150 .endm
                            151 
                            152 .mdelete cpct_restoreReg_iy
                            153 .macro cpct_restoreReg_iy
                            154   pop iy       ;; [4]
                            155 .endm
                            156 
                            157 .mdelete cpctm_createInterruptHandlerWrapper_asm
                            158 .macro cpctm_createInterruptHandlerWrapper_asm WrapperName, intHandAddress, R1, R2, R3, R4, R5, R6, R7, R8, R9, R10, R11
                            159   .equ cpct_altAFdetected, 0
                            160   .equ cpct_altBCDEHLdetected, 0
                            161   .equ cpct_altDetected, 0
                            162   cpct_checkReg_'R1
                            163   cpct_checkReg_'R2
                            164   cpct_checkReg_'R3
                            165   cpct_checkReg_'R4
                            166   cpct_checkReg_'R5
                            167   cpct_checkReg_'R6
                            168   cpct_checkReg_'R7
                            169   cpct_checkReg_'R8
                            170   cpct_checkReg_'R9
                            171   cpct_checkReg_'R10
                            172   cpct_checkReg_'R11
                            173 
                            174   WrapperName::
                            175   _'WrapperName::
                            176 
                            177   cpct_saveReg_'R1
                            178   cpct_saveReg_'R2
                            179   cpct_saveReg_'R3
                            180   cpct_saveReg_'R4
                            181   cpct_saveReg_'R5
                            182   cpct_saveReg_'R6
                            183   cpct_saveReg_'R7
                            184   cpct_saveReg_'R8
                            185   cpct_saveReg_'R9
                            186   cpct_saveReg_'R10
                            187   cpct_saveReg_'R11
                            188 
                            189   call #intHandAddress ;; [5] Call Interrupt Handler
                            190 
                            191   cpct_restoreReg_'R11
                            192   cpct_restoreReg_'R10
                            193   cpct_restoreReg_'R9
                            194   cpct_restoreReg_'R8
                            195   cpct_restoreReg_'R7
                            196   cpct_restoreReg_'R6
                            197   cpct_restoreReg_'R5
                            198   cpct_restoreReg_'R4
                            199   cpct_restoreReg_'R3
                            200   cpct_restoreReg_'R2
                            201   cpct_restoreReg_'R1
                            202   
                            203   ei         ;; [1] Reenable interrupts
                            204   reti       ;; [4] Return to main program
                            205 .endm
   4020                      76 	cpctm_createInterruptHandlerWrapper_asm MyInterruptWrapper, _myInterruptHandler, af, bc, de, hl, ix, iy, alt, af, hl 
                     0000     1   .equ cpct_altAFdetected, 0
                     0000     2   .equ cpct_altBCDEHLdetected, 0
                     0000     3   .equ cpct_altDetected, 0
   4020                       4   cpct_checkReg_af
                     0000     1   .if cpct_altDetected
                              2     .equ cpct_altAFdetected, 1
                              3   .endif
   0020                       5   cpct_checkReg_bc
                     0000     1   .if cpct_altDetected
                              2     .equ cpct_altBCDEHLdetected, 1
                              3   .endif
   0020                       6   cpct_checkReg_de
                     0000     1   .if cpct_altDetected
                              2     .equ cpct_altBCDEHLdetected, 1
                              3   .endif
   0020                       7   cpct_checkReg_hl
                     0000     1   .if cpct_altDetected
                              2     .equ cpct_altBCDEHLdetected, 1
                              3   .endif
   0020                       8   cpct_checkReg_ix
   0020                       9   cpct_checkReg_iy
   0020                      10   cpct_checkReg_alt
                     0001     1   .equ cpct_altDetected, 1
   0020                      11   cpct_checkReg_af
                     0001     1   .if cpct_altDetected
                     0001     2     .equ cpct_altAFdetected, 1
                              3   .endif
   0020                      12   cpct_checkReg_hl
                     0001     1   .if cpct_altDetected
                     0001     2     .equ cpct_altBCDEHLdetected, 1
                              3   .endif
   0020                      13   cpct_checkReg_
   0020                      14   cpct_checkReg_
                             15 
   0020                      16   MyInterruptWrapper::
   0020                      17   _MyInterruptWrapper::
                             18 
   0020                      19   cpct_saveReg_af
   4020 F5            [11]    1   push af      ;; [4]
   0021                      20   cpct_saveReg_bc
   4021 C5            [11]    1   push bc      ;; [4]
   0022                      21   cpct_saveReg_de
   4022 D5            [11]    1   push de      ;; [4]
   0023                      22   cpct_saveReg_hl
   4023 E5            [11]    1   push hl      ;; [4]
   0024                      23   cpct_saveReg_ix
   4024 DD E5         [15]    1   push ix      ;; [5]
   0026                      24   cpct_saveReg_iy
   4026 FD E5         [15]    1   push iy      ;; [5]
   0028                      25   cpct_saveReg_alt
                     0001     1   .if cpct_altAFdetected
   4028 08            [ 4]    2     ex af, af' ;; [1]
                              3   .endif
                     0001     4   .if cpct_altBCDEHLdetected
   4029 D9            [ 4]    5     exx        ;; [1]
                              6   .endif
   002A                      26   cpct_saveReg_af
   402A F5            [11]    1   push af      ;; [4]
   002B                      27   cpct_saveReg_hl
   402B E5            [11]    1   push hl      ;; [4]
   002C                      28   cpct_saveReg_
   002C                      29   cpct_saveReg_
                             30 
   402C CD 00 40      [17]   31   call #_myInterruptHandler ;; [5] Call Interrupt Handler
                             32 
   002F                      33   cpct_restoreReg_
   002F                      34   cpct_restoreReg_
   002F                      35   cpct_restoreReg_hl
   402F E1            [10]    1   pop hl       ;; [3]
   0030                      36   cpct_restoreReg_af
   4030 F1            [10]    1   pop af       ;; [3]
   0031                      37   cpct_restoreReg_alt
                     0001     1   .if cpct_altBCDEHLdetected
   4031 D9            [ 4]    2     exx        ;; [1]
                              3   .endif
                     0001     4   .if cpct_altAFdetected
   4032 08            [ 4]    5     ex af, af' ;; [1]
                              6   .endif
   0033                      38   cpct_restoreReg_iy
   4033 FD E1         [14]    1   pop iy       ;; [4]
   0035                      39   cpct_restoreReg_ix
   4035 DD E1         [14]    1   pop ix       ;; [4]
   0037                      40   cpct_restoreReg_hl
   4037 E1            [10]    1   pop hl       ;; [3]
   0038                      41   cpct_restoreReg_de
   4038 D1            [10]    1   pop de       ;; [3]
   0039                      42   cpct_restoreReg_bc
   4039 C1            [10]    1   pop bc       ;; [3]
   003A                      43   cpct_restoreReg_af
   403A F1            [10]    1   pop af       ;; [3]
                             44   
   403B FB            [ 4]   45   ei         ;; [1] Reenable interrupts
   403C ED 4D         [14]   46   reti       ;; [4] Return to main program
                             77 	.area _CODE
                             78 	.area _INITIALIZER
                             79 	.area _CABS (ABS)
