ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 1.
Hexadecimal [16-Bits]



                              1 ;;-----------------------------LICENSE NOTICE------------------------------------
                              2 ;;  This file is part of CPCtelera: An Amstrad CPC Game Engine 
                              3 ;;  Copyright (C) 2016 ronaldo / Fremos / Cheesetea / ByteRealms (@FranGallegoBR)
                              4 ;;
                              5 ;;  This program is free software: you can redistribute it and/or modify
                              6 ;;  it under the terms of the GNU Lesser General Public License as published by
                              7 ;;  the Free Software Foundation, either version 3 of the License, or
                              8 ;;  (at your option) any later version.
                              9 ;;
                             10 ;;  This program is distributed in the hope that it will be useful,
                             11 ;;  but WITHOUT ANY WARRANTY; without even the implied warranty of
                             12 ;;  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
                             13 ;;  GNU Lesser General Public License for more details.
                             14 ;;
                             15 ;;  You should have received a copy of the GNU Lesser General Public License
                             16 ;;  along with this program.  If not, see <http://www.gnu.org/licenses/>.
                             17 ;;-------------------------------------------------------------------------------
                             18 
                             19 ;;===============================================================================
                             20 ;; DEFINED CONSTANTS
                             21 ;;===============================================================================
                             22 
                     C000    23 pvideomem     = 0xC000         ;; First byte of video memory
                     00C8    24 screen_H      = 200            ;; Height of the screen in pixels
                     0050    25 screen_W      = 80             ;; Width of the screen in bytes
                     0001    26 init_colour   = 0x0001         ;; Background = 0x00, Foreground = 0x01
                     0010    27 palete_size   = 16             ;; Number of total palette colours
                     1F10    28 border_colour = 0x1F10         ;; 0x10 (Border ID), 0x1F (Colour to set, Pen 0 from palette). Ready to be loaded into HL
                     C711    29 initxy_sprite = 0xC711         ;; (x, y) = (17, 200) = (0x11, 0xC8) Initial Sprite coordinates in bytes
                     852D    30 sprite_HxW    = 0x852D         ;; Height (133, 0x85) and Width (45, 0x2D) of the sprite in bytes. To be loaded in BC   
                     0014    31 sprite_end_y  = 20             ;; y coordinate where sprite will stop its entering animation
                     0043    32 clip_Height   = screen_H - 133 ;; Minimum height at which to do clipping (200 - sprite_Height)
                     0212    33 xy_str_dav    = 0x0212         ;; y = 2 (0x02), x = 18 (0x12) (ready to be loaded into BC, B=y, C=x)  
                     0006    34 itmusiccycles = 6              ;; Number of interrupt cycles between music calls
                             35 
                             36 ;;===============================================================================
                             37 ;; DATA SECTION
                             38 ;;===============================================================================
                             39 
                             40 .area _DATA
                             41 
                             42 ;; Interrupt status counter
   627E 06                   43 iscount:  .db itmusiccycles
                             44 
                             45 ;; Ascii zero-terminated strings
   627F 48 61 70 70 79 00    46 str_happy: .asciz "Happy"
   6285 42 69 72 74 68 64    47 str_bday:  .asciz "Birthday"
        61 79 00
   628E 40 6F 63 74 6F 70    48 str_dav:   .asciz "@octopusjig"
        75 73 6A 69 67 00
                             49 
                             50 ;; Sprite, Palette and music (defined in their own generated source files)
                             51 .globl _g_octopusjig
                             52 .globl _g_palette
                             53 .globl _g_music
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 2.
Hexadecimal [16-Bits]



                             54 
                             55 ;; Scrolling data structures for both scrolling strings (Happy / BDay)
   629A                      56 tscroll_happy: 
   629A 7F 62                57    .dw   str_happy       ;; String pointer (2 bytes)
   629C 01 A0                58    .db   1, 20*8         ;; x, y starting coordinates (y=20th character line)
   629E FF                   59    .db  -1               ;; x velocity
   629F 3B                   60    .db   screen_W-5*4-1  ;; maxX coordinate: line-size (80) - 5 chars * 4 bytes/char - 1 (to set boundary 1 byte before)
                             61 
   62A0                      62 tscroll_bday: 
   62A0 85 62                63    .dw   str_bday        ;; String pointer (2 bytes)
   62A2 2F B8                64    .db   47, 23*8        ;; x, y starting coordinates (y=23th character line)
   62A4 01                   65    .db    1              ;; x velocity 
   62A5 2F                   66    .db   screen_W-8*4-1  ;; maxX coordinate: line-size (80) - 8 chars * 4 bytes/char - 1 (to set boundary 1 byte before)
                             67 
                             68 ;;===============================================================================
                             69 ;; CODE SECTION
                             70 ;;===============================================================================
                             71 
                             72 .area _CODE
                             73 
                             74 ;; Include all CPCtelera macros, including opcode macros that 
                             75 ;; we will be using later
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 3.
Hexadecimal [16-Bits]



                             76 .include "macros/allmacros.h.s"
                              1 ;;-----------------------------LICENSE NOTICE------------------------------------
                              2 ;;  This file is part of CPCtelera: An Amstrad CPC Game Engine
                              3 ;;  Copyright (C) 2017 ronaldo / Fremos / Cheesetea / ByteRealms (@FranGallegoBR)
                              4 ;;
                              5 ;;  This program is free software: you can redistribute it and/or modify
                              6 ;;  it under the terms of the GNU Lesser General Public License as published by
                              7 ;;  the Free Software Foundation, either version 3 of the License, or
                              8 ;;  (at your option) any later version.
                              9 ;;
                             10 ;;  This program is distributed in the hope that it will be useful,
                             11 ;;  but WITHOUT ANY WARRANTY; without even the implied warranty of
                             12 ;;  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
                             13 ;;  GNU Lesser General Public License for more details.
                             14 ;;
                             15 ;;  You should have received a copy of the GNU Lesser General Public License
                             16 ;;  along with this program.  If not, see <http://www.gnu.org/licenses/>.
                             17 ;;-------------------------------------------------------------------------------
                             18 
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 4.
Hexadecimal [16-Bits]



                             19 .include "macros/cpct_maths.h.s"
                              1 ;;-----------------------------LICENSE NOTICE------------------------------------
                              2 ;;  This file is part of CPCtelera: An Amstrad CPC Game Engine 
                              3 ;;  Copyright (C) 2017 ronaldo / Fremos / Cheesetea / ByteRealms (@FranGallegoBR)
                              4 ;;
                              5 ;;  This program is free software: you can redistribute it and/or modify
                              6 ;;  it under the terms of the GNU Lesser General Public License as published by
                              7 ;;  the Free Software Foundation, either version 3 of the License, or
                              8 ;;  (at your option) any later version.
                              9 ;;
                             10 ;;  This program is distributed in the hope that it will be useful,
                             11 ;;  but WITHOUT ANY WARRANTY; without even the implied warranty of
                             12 ;;  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
                             13 ;;  GNU Lesser General Public License for more details.
                             14 ;;
                             15 ;;  You should have received a copy of the GNU Lesser General Public License
                             16 ;;  along with this program.  If not, see <http://www.gnu.org/licenses/>.
                             17 ;;-------------------------------------------------------------------------------
                             18 
                             19 ;;
                             20 ;; File: Math Macros
                             21 ;;
                             22 ;;    Useful assembler macros for doing common math operations
                             23 ;;
                             24 
                             25 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                             26 ;; Macro: add_REGPAIR_a 
                             27 ;;
                             28 ;;    Performs the operation REGPAIR = REGPAIR + A. REGPAIR is any given pair of 8-bit registers.
                             29 ;;
                             30 ;; ASM Definition:
                             31 ;;    .macro <add_REGPAIR_a> RH, RL
                             32 ;;
                             33 ;; Parameters:
                             34 ;;    RH    - Register 1 of the REGPAIR. Holds higher-byte value
                             35 ;;    RL    - Register 2 of the REGPAIR. Holds lower-byte value
                             36 ;; 
                             37 ;; Input Registers: 
                             38 ;;    RH:RL - 16-value used as left-operand and final storage for the sum
                             39 ;;    A     - Second sum operand
                             40 ;;
                             41 ;; Return Value:
                             42 ;;    RH:RL - Holds the sum of RH:RL + A
                             43 ;;
                             44 ;; Details:
                             45 ;;    This macro performs the sum of RH:RL + A and stores it directly on RH:RL.
                             46 ;; It uses only RH:RL and A to perform the operation.
                             47 ;;
                             48 ;; Modified Registers: 
                             49 ;;    A, RH, RL
                             50 ;;
                             51 ;; Required memory:
                             52 ;;    5 bytes
                             53 ;;
                             54 ;; Time Measures:
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 5.
Hexadecimal [16-Bits]



                             55 ;; (start code)
                             56 ;;  Case | microSecs(us) | CPU Cycles
                             57 ;; ------------------------------------
                             58 ;;  Any  |       5       |     20
                             59 ;; ------------------------------------
                             60 ;; (end code)
                             61 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                             62 .macro add_REGPAIR_a rh, rl
                             63    ;; First Perform RH = E + A
                             64    add rl    ;; [1] A' = RL + A 
                             65    ld  rl, a ;; [1] RL' = A' = RL + A. It might generate Carry that must be added to RH
                             66    
                             67    ;; Then Perform RH = RH + Carry 
                             68    adc rh    ;; [1] A'' = A' + RH + Carry = RL + A + RH + Carry
                             69    sub rl    ;; [1] Remove RL'. A''' = A'' - RL' = RL + A + RH + Carry - (RL + A) = RH + Carry
                             70    ld  rh, a ;; [1] Save into RH (RH' = A''' = RH + Carry)
                             71 .endm
                             72 
                             73 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                             74 ;; Macro: add_de_a
                             75 ;;
                             76 ;;    Performs the operation DE = DE + A
                             77 ;;
                             78 ;; ASM Definition:
                             79 ;;    .macro <add_de_a>
                             80 ;;
                             81 ;; Parameters:
                             82 ;;    None
                             83 ;; 
                             84 ;; Input Registers: 
                             85 ;;    DE    - First sum operand and Destination Register
                             86 ;;    A     - Second sum operand
                             87 ;;
                             88 ;; Return Value:
                             89 ;;    DE - Holds the sum of DE + A
                             90 ;;
                             91 ;; Details:
                             92 ;;    This macro performs the sum of DE + A and stores it directly on DE.
                             93 ;; It uses only DE and A to perform the operation.
                             94 ;;    This macro is a direct instantiation of the macro <add_REGPAIR_a>.
                             95 ;;
                             96 ;; Modified Registers: 
                             97 ;;    A, DE
                             98 ;;
                             99 ;; Required memory:
                            100 ;;    5 bytes
                            101 ;;
                            102 ;; Time Measures:
                            103 ;; (start code)
                            104 ;;  Case | microSecs(us) | CPU Cycles
                            105 ;; ------------------------------------
                            106 ;;  Any  |       5       |     20
                            107 ;; ------------------------------------
                            108 ;; (end code)
                            109 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 6.
Hexadecimal [16-Bits]



                            110 .macro add_de_a
                            111    add_REGPAIR_a  d, e
                            112 .endm
                            113 
                            114 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                            115 ;; Macro: add_hl_a
                            116 ;;
                            117 ;;    Performs the operation HL = HL + A
                            118 ;;
                            119 ;; ASM Definition:
                            120 ;;    .macro <add_hl_a>
                            121 ;;
                            122 ;; Parameters:
                            123 ;;    None
                            124 ;; 
                            125 ;; Input Registers: 
                            126 ;;    HL    - First sum operand and Destination Register
                            127 ;;    A     - Second sum operand
                            128 ;;
                            129 ;; Return Value:
                            130 ;;    HL - Holds the sum of HL + A
                            131 ;;
                            132 ;; Details:
                            133 ;;    This macro performs the sum of HL + A and stores it directly on HL.
                            134 ;; It uses only HL and A to perform the operation.
                            135 ;;    This macro is a direct instantiation of the macro <add_REGPAIR_a>.
                            136 ;;
                            137 ;; Modified Registers: 
                            138 ;;    A, HL
                            139 ;;
                            140 ;; Required memory:
                            141 ;;    5 bytes
                            142 ;;
                            143 ;; Time Measures:
                            144 ;; (start code)
                            145 ;;  Case | microSecs(us) | CPU Cycles
                            146 ;; ------------------------------------
                            147 ;;  Any  |       5       |     20
                            148 ;; ------------------------------------
                            149 ;; (end code)
                            150 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                            151 .macro add_hl_a
                            152    add_REGPAIR_a  h, l
                            153 .endm
                            154 
                            155 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                            156 ;; Macro: add_bc_a
                            157 ;;
                            158 ;;    Performs the operation BC = BC + A
                            159 ;;
                            160 ;; ASM Definition:
                            161 ;;    .macro <add_bc_a>
                            162 ;;
                            163 ;; Parameters:
                            164 ;;    None
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 7.
Hexadecimal [16-Bits]



                            165 ;; 
                            166 ;; Input Registers: 
                            167 ;;    BC    - First sum operand and Destination Register
                            168 ;;    A     - Second sum operand
                            169 ;;
                            170 ;; Return Value:
                            171 ;;    BC - Holds the sum of BC + A
                            172 ;;
                            173 ;; Details:
                            174 ;;    This macro performs the sum of BC + A and stores it directly on BC.
                            175 ;; It uses only BC and A to perform the operation.
                            176 ;;    This macro is a direct instantiation of the macro <add_REGPAIR_a>.
                            177 ;;
                            178 ;; Modified Registers: 
                            179 ;;    A, BC
                            180 ;;
                            181 ;; Required memory:
                            182 ;;    5 bytes
                            183 ;;
                            184 ;; Time Measures:
                            185 ;; (start code)
                            186 ;;  Case | microSecs(us) | CPU Cycles
                            187 ;; ------------------------------------
                            188 ;;  Any  |       5       |     20
                            189 ;; ------------------------------------
                            190 ;; (end code)
                            191 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                            192 .macro add_bc_a
                            193    add_REGPAIR_a  b, c
                            194 .endm
                            195 
                            196 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                            197 ;; Macro: sub_REGPAIR_a 
                            198 ;;
                            199 ;;    Performs the operation REGPAIR = REGPAIR - A. REGPAIR is any given pair of 8-bit registers.
                            200 ;;
                            201 ;; ASM Definition:
                            202 ;;    .macro <sub_REGPAIR_a> RH, RL
                            203 ;;
                            204 ;; Parameters:
                            205 ;;    RH    - Register 1 of the REGPAIR. Holds higher-byte value
                            206 ;;    RL    - Register 2 of the REGPAIR. Holds lower-byte value
                            207 ;;  ?JMPLBL - Optional Jump label. A temporal one will be produced if none is given.
                            208 ;; 
                            209 ;; Input Registers: 
                            210 ;;    RH:RL - 16-value used as left-operand and final storage for the subtraction
                            211 ;;    A     - Second subtraction operand (A > 0)
                            212 ;;
                            213 ;; Preconditions:
                            214 ;;    A > 0 - Value in register A is considered to be unsigned and must be greater
                            215 ;;            than 0 for this macro to work properly.
                            216 ;;
                            217 ;; Return Value:
                            218 ;;    RH:RL - Holds the result of RH:RL - A
                            219 ;;
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 8.
Hexadecimal [16-Bits]



                            220 ;; Details:
                            221 ;;    This macro performs the subtraction of RH:RL - A and stores it directly on RH:RL.
                            222 ;; It uses only RH:RL and A to perform the operation.
                            223 ;;    With respect to the optional label ?JMPLBL, it is often better not to provide 
                            224 ;; this parameter. A temporal local symbol will be automatically generated for that label.
                            225 ;; Only provide it when you have a specific reason to do that.
                            226 ;;
                            227 ;; Modified Registers: 
                            228 ;;    A, RH, RL
                            229 ;;
                            230 ;; Required memory:
                            231 ;;    7 bytes
                            232 ;;
                            233 ;; Time Measures:
                            234 ;; (start code)
                            235 ;;  Case | microSecs(us) | CPU Cycles
                            236 ;; ------------------------------------
                            237 ;;  Any  |       7       |     28
                            238 ;; ------------------------------------
                            239 ;; (end code)
                            240 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                            241 .macro sub_REGPAIR_a rh, rl, ?jmplbl
                            242    ;; First Perform A' = A - 1 - RL 
                            243    ;; (Inverse subtraction minus 1, used  to test for Carry, needed to know when to subtract 1 from RH)
                            244    dec    a          ;; [1] --A (In case A == RL, inverse subtraction should produce carry not to decrement RH)
                            245    sub   rl          ;; [1] A' = A - 1 - RL
                            246    jr     c, jmplbl  ;; [2/3] If A <= RL, Carry will be produced, and no decrement of RH is required, so jump over it
                            247      dec   rh        ;; [1] --RH (A > RL, so RH must be decremented)
                            248 jmplbl:   
                            249    ;; Now invert A to get the subtraction we wanted 
                            250    ;; { RL' = -A' - 1 = -(A - 1 - RL) - 1 = RL - A }
                            251    cpl            ;; [1] A'' = RL - A (Original subtraction we wanted, calculated trough one's complement of A')
                            252    ld    rl, a    ;; [1] Save into RL (RL' = RL - A)
                            253 .endm
                            254 
                            255 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                            256 ;; Macro: sub_de_a 
                            257 ;;
                            258 ;;    Performs the operation DE = DE - A. DE is any given pair of 8-bit registers.
                            259 ;;
                            260 ;; ASM Definition:
                            261 ;;    .macro <sub_de_a>
                            262 ;; 
                            263 ;; Input Registers: 
                            264 ;;    DE - 16-value used as left-operand and final storage for the subtraction
                            265 ;;    A  - Second subtraction operand
                            266 ;;
                            267 ;; Return Value:
                            268 ;;    DE - Holds the result of DE - A
                            269 ;;
                            270 ;; Details:
                            271 ;;    This macro performs the subtraction of DE - A and stores it directly on DE.
                            272 ;; It uses only DE and A to perform the operation.
                            273 ;;
                            274 ;; Modified Registers: 
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 9.
Hexadecimal [16-Bits]



                            275 ;;    A, DE
                            276 ;;
                            277 ;; Required memory:
                            278 ;;    7 bytes
                            279 ;;
                            280 ;; Time Measures:
                            281 ;; (start code)
                            282 ;;  Case | microSecs(us) | CPU Cycles
                            283 ;; ------------------------------------
                            284 ;;  Any  |       7       |     28
                            285 ;; ------------------------------------
                            286 ;; (end code)
                            287 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                            288 .macro sub_de_a
                            289    sub_REGPAIR_a  d, e
                            290 .endm
                            291 
                            292 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                            293 ;; Macro: sub_hl_a 
                            294 ;;
                            295 ;;    Performs the operation HL = HL - A. HL is any given pair of 8-bit registers.
                            296 ;;
                            297 ;; ASM Definition:
                            298 ;;    .macro <sub_hl_a>
                            299 ;; 
                            300 ;; Input Registers: 
                            301 ;;    HL - 16-value used as left-operand and final storage for the subtraction
                            302 ;;    A  - Second subtraction operand
                            303 ;;
                            304 ;; Return Value:
                            305 ;;    HL - Holds the result of HL - A
                            306 ;;
                            307 ;; Details:
                            308 ;;    This macro performs the subtraction of HL - A and stores it directly on HL.
                            309 ;; It uses only HL and A to perform the operation.
                            310 ;;
                            311 ;; Modified Registers: 
                            312 ;;    A, HL
                            313 ;;
                            314 ;; Required memory:
                            315 ;;    7 bytes
                            316 ;;
                            317 ;; Time Measures:
                            318 ;; (start code)
                            319 ;;  Case | microSecs(us) | CPU Cycles
                            320 ;; ------------------------------------
                            321 ;;  Any  |       7       |     28
                            322 ;; ------------------------------------
                            323 ;; (end code)
                            324 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                            325 .macro sub_hl_a
                            326    sub_REGPAIR_a  h, l
                            327 .endm
                            328 
                            329 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 10.
Hexadecimal [16-Bits]



                            330 ;; Macro: sub_bc_a 
                            331 ;;
                            332 ;;    Performs the operation BC = BC - A. BC is any given pair of 8-bit registers.
                            333 ;;
                            334 ;; ASM Definition:
                            335 ;;    .macro <sub_bc_a>
                            336 ;; 
                            337 ;; Input Registers: 
                            338 ;;    BC - 16-value used as left-operand and final storage for the subtraction
                            339 ;;    A  - Second subtraction operand
                            340 ;;
                            341 ;; Return Value:
                            342 ;;    BC - Holds the result of BC - A
                            343 ;;
                            344 ;; Details:
                            345 ;;    This macro performs the subtraction of BC - A and stores it directly on BC.
                            346 ;; It uses only BC and A to perform the operation.
                            347 ;;
                            348 ;; Modified Registers: 
                            349 ;;    A, BC
                            350 ;;
                            351 ;; Required memory:
                            352 ;;    7 bytes
                            353 ;;
                            354 ;; Time Measures:
                            355 ;; (start code)
                            356 ;;  Case | microSecs(us) | CPU Cycles
                            357 ;; ------------------------------------
                            358 ;;  Any  |       7       |     28
                            359 ;; ------------------------------------
                            360 ;; (end code)
                            361 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                            362 .macro sub_bc_a
                            363    sub_REGPAIR_a  b, c
                            364 .endm
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 11.
Hexadecimal [16-Bits]



                             20 .include "macros/cpct_opcodeConstants.h.s"
                              1 ;;-----------------------------LICENSE NOTICE------------------------------------
                              2 ;;  This file is part of CPCtelera: An Amstrad CPC Game Engine 
                              3 ;;  Copyright (C) 2016 ronaldo / Fremos / Cheesetea / ByteRealms (@FranGallegoBR)
                              4 ;;
                              5 ;;  This program is free software: you can redistribute it and/or modify
                              6 ;;  it under the terms of the GNU Lesser General Public License as published by
                              7 ;;  the Free Software Foundation, either version 3 of the License, or
                              8 ;;  (at your option) any later version.
                              9 ;;
                             10 ;;  This program is distributed in the hope that it will be useful,
                             11 ;;  but WITHOUT ANY WARRANTY; without even the implied warranty of
                             12 ;;  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
                             13 ;;  GNU Lesser General Public License for more details.
                             14 ;;
                             15 ;;  You should have received a copy of the GNU Lesser General Public License
                             16 ;;  along with this program.  If not, see <http://www.gnu.org/licenses/>.
                             17 ;;-------------------------------------------------------------------------------
                             18 
                             19 ;;
                             20 ;; File: Opcodes
                             21 ;;
                             22 ;;    Constant definitions of Z80 opcodes. This will be normally used as data
                             23 ;; for self-modifying code.
                             24 ;;
                             25 
                             26 ;; Constant: opc_JR
                             27 ;;    Opcode for "JR xx" instruction. Requires 1-byte parameter (xx)
                     0018    28 opc_JR   = 0x18
                             29 
                             30 ;; Constant: opc_LD_D
                             31 ;;    Opcode for "LD d, xx" instruction. Requires 1-byte parameter (xx)
                     0016    32 opc_LD_D = 0x16
                             33 
                             34 ;; Constant: opc_EI
                             35 ;;    Opcode for "EI" instruction. 
                     00FB    36 opc_EI = 0xFB
                             37 
                             38 ;; Constant: opc_DI
                             39 ;;    Opcode for "DI" instruction. 
                     00F3    40 opc_DI = 0xF3
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 12.
Hexadecimal [16-Bits]



                             21 .include "macros/cpct_reverseBits.h.s"
                              1 ;;-----------------------------LICENSE NOTICE------------------------------------
                              2 ;;  This file is part of CPCtelera: An Amstrad CPC Game Engine 
                              3 ;;  Copyright (C) 2016 ronaldo / Fremos / Cheesetea / ByteRealms (@FranGallegoBR)
                              4 ;;
                              5 ;;  This program is free software: you can redistribute it and/or modify
                              6 ;;  it under the terms of the GNU Lesser General Public License as published by
                              7 ;;  the Free Software Foundation, either version 3 of the License, or
                              8 ;;  (at your option) any later version.
                              9 ;;
                             10 ;;  This program is distributed in the hope that it will be useful,
                             11 ;;  but WITHOUT ANY WARRANTY; without even the implied warranty of
                             12 ;;  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
                             13 ;;  GNU Lesser General Public License for more details.
                             14 ;;
                             15 ;;  You should have received a copy of the GNU Lesser General Public License
                             16 ;;  along with this program.  If not, see <http://www.gnu.org/licenses/>.
                             17 ;;-------------------------------------------------------------------------------
                             18 
                             19 ;;
                             20 ;; File: Reverse Bits
                             21 ;;
                             22 ;;    Useful macros for bit reversing and selecting in different ways. Only
                             23 ;; valid to be used from assembly language (not from C).
                             24 ;;
                             25 
                             26 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                             27 ;; Macro: cpctm_reverse_and_select_bits_of_A
                             28 ;;
                             29 ;;    Reorders the bits of A and mixes them letting the user select the 
                             30 ;; new order for the bits by using a selection mask.
                             31 ;;
                             32 ;; Parameters:
                             33 ;;    TReg          - An 8-bits register that will be used for intermediate calculations.
                             34 ;; This register may be one of these: B, C, D, E, H, L
                             35 ;;    SelectionMask - An 8-bits mask that will be used to select the bits to get from 
                             36 ;; the reordered bits. It might be an 8-bit register or even (hl).
                             37 ;; 
                             38 ;; Input Registers: 
                             39 ;;    A     - Byte to be reversed
                             40 ;;    TReg  - Should have a copy of A (same exact value)
                             41 ;;
                             42 ;; Return Value:
                             43 ;;    A - Resulting value with bits reversed and selected 
                             44 ;;
                             45 ;; Details:
                             46 ;;    This macro reorders the bits in A and mixes them with the same bits in
                             47 ;; their original order by using a *SelectionMask*. The process is as follows:
                             48 ;;
                             49 ;;    1. Consider the 8 bits of A = TReg = [01234567]
                             50 ;;    2. Reorder the 8 bits of A, producing A2 = [32547610]
                             51 ;;    2. Reorder the bits of TReg, producing TReg2 = [76103254]
                             52 ;;    3. Combines both reorders into final result using a *SelectionMask*. Each 
                             53 ;; 0 bit from the selection mask means "select bit from A2", whereas each 1 bit
                             54 ;; means "select bit from TReg2".
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 13.
Hexadecimal [16-Bits]



                             55 ;;
                             56 ;;    For instance, a selection mask 0b11001100 will produce this result:
                             57 ;;
                             58 ;; (start code)
                             59 ;;       A2 = [ 32 54 76 10 ]
                             60 ;;    TReg2 = [ 76 10 32 54 ]
                             61 ;;  SelMask = [ 11 00 11 00 ] // 1 = TReg2-bits, 0 = A2-bits
                             62 ;;  ---------------------------
                             63 ;;   Result = [ 76 54 32 10 ]
                             64 ;; (end code)
                             65 ;;
                             66 ;;    Therefore, mask 0b11001100 produces the effect of reversing the bits of A
                             67 ;; completely. Other masks will produce different reorders of the bits in A, for
                             68 ;; different requirements or needs.
                             69 ;;
                             70 ;; Modified Registers: 
                             71 ;;    AF, TReg
                             72 ;;
                             73 ;; Required memory:
                             74 ;;    16 bytes
                             75 ;;
                             76 ;; Time Measures:
                             77 ;; (start code)
                             78 ;;  Case | microSecs(us) | CPU Cycles
                             79 ;; ------------------------------------
                             80 ;;  Any  |      16       |     64
                             81 ;; ------------------------------------
                             82 ;; (end code)
                             83 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                             84 .macro cpctm_reverse_and_select_bits_of_A  TReg, SelectionMask
                             85    rlca            ;; [1] | Rotate left twice so that...
                             86    rlca            ;; [1] | ... A=[23456701]
                             87 
                             88    ;; Mix bits of TReg and A so that all bits are in correct relative order
                             89    ;; but displaced from their final desired location
                             90    xor TReg        ;; [1] TReg = [01234567] (original value)
                             91    and #0b01010101 ;; [2]    A = [23456701] (bits rotated twice left)
                             92    xor TReg        ;; [1]   A2 = [03254761] (TReg mixed with A to get bits in order)
                             93    
                             94    ;; Now get bits 54 and 10 in their right location and save them into TReg
                             95    rlca            ;; [1]    A = [ 32 54 76 10 ] (54 and 10 are in their desired place)
                             96    ld TReg, a      ;; [1] TReg = A (Save this bit location into TReg)
                             97    
                             98    ;; Now get bits 76 and 32 in their right location in A
                             99    rrca            ;; [1] | Rotate A right 4 times to...
                            100    rrca            ;; [1] | ... get bits 76 and 32 located at their ...
                            101    rrca            ;; [1] | ... desired location :
                            102    rrca            ;; [1] | ... A = [ 76 10 32 54 ] (76 and 32 are in their desired place)
                            103    
                            104    ;; Finally, mix bits from TReg and A to get all bits reversed and selected
                            105    xor TReg          ;; [1] TReg = [32547610] (Mixed bits with 54 & 10 in their right place)
                            106    and SelectionMask ;; [2]    A = [76103254] (Mixed bits with 76 & 32 in their right place)
                            107    xor TReg          ;; [1]   A2 = [xxxxxxxx] final value: bits of A reversed and selected using *SelectionMask*
                            108 .endm
                            109 
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 14.
Hexadecimal [16-Bits]



                            110 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                            111 ;; Macro: cpctm_reverse_bits_of_A 
                            112 ;; Macro: cpctm_reverse_mode_2_pixels_of_A
                            113 ;;
                            114 ;;    Reverses the 8-bits of A, from [01234567] to [76543210]. This also reverses
                            115 ;; all pixels contained in A when A is in screen pixel format, mode 2.
                            116 ;;
                            117 ;; Parameters:
                            118 ;;    TReg - An 8-bits register that will be used for intermediate calculations.
                            119 ;; This register may be one of these: B, C, D, E, H, L
                            120 ;; 
                            121 ;; Input Registers: 
                            122 ;;    A    - Byte to be reversed
                            123 ;;    TReg - Should have a copy of A (same exact value)
                            124 ;;
                            125 ;; Return Value:
                            126 ;;    A - Resulting value with bits reversed 
                            127 ;;
                            128 ;; Requires:
                            129 ;;   - Uses the macro <cpctm_reverse_and_select_bits_of_A>.
                            130 ;;
                            131 ;; Details:
                            132 ;;    This macro reverses the bits in A. If bits of A = [01234567], the final
                            133 ;; result after processing this macro will be A = [76543210]. Register TReg is
                            134 ;; used for intermediate calculations and its value is destroyed.
                            135 ;;
                            136 ;; Modified Registers: 
                            137 ;;    AF, TReg
                            138 ;;
                            139 ;; Required memory:
                            140 ;;    16 bytes
                            141 ;;
                            142 ;; Time Measures:
                            143 ;; (start code)
                            144 ;;  Case | microSecs(us) | CPU Cycles
                            145 ;; ------------------------------------
                            146 ;;  Any  |      16       |     64
                            147 ;; ------------------------------------
                            148 ;; (end code)
                            149 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                            150 .macro cpctm_reverse_bits_of_A  TReg
                            151    cpctm_reverse_and_select_bits_of_A  TReg, #0b11001100
                            152 .endm
                            153 .macro cpctm_reverse_mode_2_pixels_of_A   TReg
                            154    cpctm_reverse_bits_of_A  TReg
                            155 .endm
                            156 
                            157 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                            158 ;; Macro: cpctm_reverse_mode_1_pixels_of_A
                            159 ;;
                            160 ;;    Reverses the order of pixel values contained in register A, assuming A is 
                            161 ;; in screen pixel format, mode 1.
                            162 ;;
                            163 ;; Parameters:
                            164 ;;    TReg - An 8-bits register that will be used for intermediate calculations.
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 15.
Hexadecimal [16-Bits]



                            165 ;; This register may be one of these: B, C, D, E, H, L
                            166 ;; 
                            167 ;; Input Registers: 
                            168 ;;    A    - Byte with pixel values to be reversed
                            169 ;;    TReg - Should have a copy of A (same exact value)
                            170 ;;
                            171 ;; Return Value:
                            172 ;;    A - Resulting byte with the 4 pixels values reversed in order
                            173 ;;
                            174 ;; Requires:
                            175 ;;   - Uses the macro <cpctm_reverse_and_select_bits_of_A>.
                            176 ;;
                            177 ;; Details:
                            178 ;;    This macro considers that A contains a byte that codifies 4 pixels in 
                            179 ;; screen pixel format, mode 1. It modifies A to reverse the order of its 4 
                            180 ;; contained pixel values left-to-right (1234 -> 4321). With respect to the 
                            181 ;; order of the 8-bits of A, the concrete operations performed is:
                            182 ;; (start code)
                            183 ;;    A = [01234567] == reverse-pixels ==> [32107654] = A2
                            184 ;; (end code)
                            185 ;;    You may want to check <cpct_px2byteM1> to know how bits codify both pixels
                            186 ;; in one single byte for screen pixel format, mode 1.
                            187 ;;
                            188 ;;    *TReg* is an 8-bit register that will be used for intermediate calculations,
                            189 ;; destroying its original value (that should be same as A, at the start).
                            190 ;;
                            191 ;; Modified Registers: 
                            192 ;;    AF, TReg
                            193 ;;
                            194 ;; Required memory:
                            195 ;;    16 bytes
                            196 ;;
                            197 ;; Time Measures:
                            198 ;; (start code)
                            199 ;;  Case | microSecs(us) | CPU Cycles
                            200 ;; ------------------------------------
                            201 ;;  Any  |      16       |     64
                            202 ;; ------------------------------------
                            203 ;; (end code)
                            204 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                            205 .macro cpctm_reverse_mode_1_pixels_of_A  TReg
                            206    cpctm_reverse_and_select_bits_of_A  TReg, #0b00110011
                            207 .endm
                            208 
                            209 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                            210 ;; Macro: cpctm_reverse_mode_0_pixels_of_A
                            211 ;;
                            212 ;;    Reverses the order of pixel values contained in register A, assuming A is 
                            213 ;; in screen pixel format, mode 0.
                            214 ;;
                            215 ;; Parameters:
                            216 ;;    TReg - An 8-bits register that will be used for intermediate calculations.
                            217 ;; This register may be one of these: B, C, D, E, H, L
                            218 ;; 
                            219 ;; Input Registers: 
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 16.
Hexadecimal [16-Bits]



                            220 ;;    A    - Byte with pixel values to be reversed
                            221 ;;    TReg - Should have a copy of A (same exact value)
                            222 ;;
                            223 ;; Return Value:
                            224 ;;    A - Resulting byte with the 2 pixels values reversed in order
                            225 ;;
                            226 ;; Details:
                            227 ;;    This macro considers that A contains a byte that codifies 2 pixels in 
                            228 ;; screen pixel format, mode 0. It modifies A to reverse the order of its 2 
                            229 ;; contained pixel values left-to-right (12 -> 21). With respect to the 
                            230 ;; order of the 8-bits of A, the concrete operation performed is:
                            231 ;; (start code)
                            232 ;;    A = [01234567] == reverse-pixels ==> [10325476] = A2
                            233 ;; (end code)
                            234 ;;    You may want to check <cpct_px2byteM0> to know how bits codify both pixels
                            235 ;; in one single byte for screen pixel format, mode 0.
                            236 ;;
                            237 ;;    *TReg* is an 8-bit register that will be used for intermediate calculations,
                            238 ;; destroying its original value (that should be same as A, at the start).
                            239 ;;
                            240 ;; Modified Registers: 
                            241 ;;    AF, TReg
                            242 ;;
                            243 ;; Required memory:
                            244 ;;    7 bytes
                            245 ;;
                            246 ;; Time Measures:
                            247 ;; (start code)
                            248 ;;  Case | microSecs(us) | CPU Cycles
                            249 ;; ------------------------------------
                            250 ;;  Any  |       7       |     28
                            251 ;; ------------------------------------
                            252 ;; (end code)
                            253 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                            254 .macro cpctm_reverse_mode_0_pixels_of_A  TReg
                            255    rlca            ;; [1] | Rotate A twice to the left to get bits ordered...
                            256    rlca            ;; [1] | ... in the way we need for mixing, A = [23456701]
                            257   
                            258    ;; Mix TReg with A to get pixels reversed by reordering bits
                            259    xor TReg        ;; [1] | TReg = [01234567]
                            260    and #0b01010101 ;; [2] |    A = [23456701]
                            261    xor TReg        ;; [1] |   A2 = [03254761]
                            262    rrca            ;; [1] Rotate right to get pixels reversed A = [10325476]
                            263 .endm
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 17.
Hexadecimal [16-Bits]



                             22 .include "macros/cpct_undocumentedOpcodes.h.s"
                              1 ;;-----------------------------LICENSE NOTICE------------------------------------
                              2 ;;  This file is part of CPCtelera: An Amstrad CPC Game Engine 
                              3 ;;  Copyright (C) 2021 ronaldo / Fremos / Cheesetea / ByteRealms (@FranGallegoBR)
                              4 ;;
                              5 ;;  This program is free software: you can redistribute it and/or modify
                              6 ;;  it under the terms of the GNU Lesser General Public License as published by
                              7 ;;  the Free Software Foundation, either version 3 of the License, or
                              8 ;;  (at your option) any later version.
                              9 ;;
                             10 ;;  This program is distributed in the hope that it will be useful,
                             11 ;;  but WITHOUT ANY WARRANTY; without even the implied warranty of
                             12 ;;  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
                             13 ;;  GNU Lesser General Public License for more details.
                             14 ;;
                             15 ;;  You should have received a copy of the GNU Lesser General Public License
                             16 ;;  along with this program.  If not, see <http://www.gnu.org/licenses/>.
                             17 ;;-------------------------------------------------------------------------------
                             18 
                             19 ;;
                             20 ;; File: Undocumented Opcodes
                             21 ;;
                             22 ;;    Macros to clarify source code when using undocumented opcodes. Only
                             23 ;; valid to be used from assembly language (not from C).
                             24 ;;
                             25 
                             26 ;; Macro: jr__0
                             27 ;;    Opcode for "JR #0" instruction
                             28 ;; 
                             29 .mdelete jr__0
                             30 .macro jr__0
                             31    .DW #0x0018  ;; JR #00 (Normally used as a modifiable jump, as jr 0 is an infinite loop)
                             32 .endm
                             33 
                             34 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,
                             35 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,
                             36 ;; SLL Instructions
                             37 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,
                             38 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,
                             39 
                             40 ;; Macro: sll__b
                             41 ;;    Opcode for "SLL b" instruction
                             42 ;; 
                             43 .mdelete sll__b
                             44 .macro sll__b
                             45    .db #0xCB, #0x30  ;; Opcode for sll b
                             46 .endm
                             47 
                             48 ;; Macro: sll__c
                             49 ;;    Opcode for "SLL c" instruction
                             50 ;; 
                             51 .mdelete sll__c
                             52 .macro sll__c
                             53    .db #0xCB, #0x31  ;; Opcode for sll c
                             54 .endm
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 18.
Hexadecimal [16-Bits]



                             55 
                             56 ;; Macro: sll__d
                             57 ;;    Opcode for "SLL d" instruction
                             58 ;; 
                             59 .mdelete sll__d
                             60 .macro sll__d
                             61    .db #0xCB, #0x32  ;; Opcode for sll d
                             62 .endm
                             63 
                             64 ;; Macro: sll__e
                             65 ;;    Opcode for "SLL e" instruction
                             66 ;; 
                             67 .mdelete sll__e
                             68 .macro sll__e
                             69    .db #0xCB, #0x33  ;; Opcode for sll e
                             70 .endm
                             71 
                             72 ;; Macro: sll__h
                             73 ;;    Opcode for "SLL h" instruction
                             74 ;; 
                             75 .mdelete sll__h
                             76 .macro sll__h
                             77    .db #0xCB, #0x34  ;; Opcode for sll h
                             78 .endm
                             79 
                             80 ;; Macro: sll__l
                             81 ;;    Opcode for "SLL l" instruction
                             82 ;; 
                             83 .mdelete sll__l
                             84 .macro sll__l
                             85    .db #0xCB, #0x35  ;; Opcode for sll l
                             86 .endm
                             87 
                             88 ;; Macro: sll___hl_
                             89 ;;    Opcode for "SLL (hl)" instruction
                             90 ;; 
                             91 .mdelete sll___hl_
                             92 .macro sll___hl_
                             93    .db #0xCB, #0x36  ;; Opcode for sll (hl)
                             94 .endm
                             95 
                             96 ;; Macro: sll__a
                             97 ;;    Opcode for "SLL a" instruction
                             98 ;; 
                             99 .mdelete sll__a
                            100 .macro sll__a
                            101    .db #0xCB, #0x37  ;; Opcode for sll a
                            102 .endm
                            103 
                            104 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,
                            105 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,
                            106 ;; IXL Related Macros
                            107 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,
                            108 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,
                            109 
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 19.
Hexadecimal [16-Bits]



                            110 ;; Macro: ld__ixl    Value
                            111 ;;    Opcode for "LD ixl, Value" instruction
                            112 ;;  
                            113 ;; Parameters:
                            114 ;;    Value - An inmediate 8-bits value that will be loaded into ixl
                            115 ;; 
                            116 .mdelete ld__ixl
                            117 .macro ld__ixl    Value 
                            118    .db #0xDD, #0x2E, Value  ;; Opcode for ld ixl, Value
                            119 .endm
                            120 
                            121 ;; Macro: ld__ixl_a
                            122 ;;    Opcode for "LD ixl, a" instruction
                            123 ;; 
                            124 .mdelete ld__ixl_a
                            125 .macro ld__ixl_a
                            126    .dw #0x6FDD  ;; Opcode for ld ixl, a
                            127 .endm
                            128 
                            129 ;; Macro: ld__ixl_b
                            130 ;;    Opcode for "LD ixl, B" instruction
                            131 ;; 
                            132 .mdelete ld__ixl_b
                            133 .macro ld__ixl_b
                            134    .dw #0x68DD  ;; Opcode for ld ixl, b
                            135 .endm
                            136 
                            137 ;; Macro: ld__ixl_c
                            138 ;;    Opcode for "LD ixl, C" instruction
                            139 ;; 
                            140 .mdelete ld__ixl_c
                            141 .macro ld__ixl_c
                            142    .dw #0x69DD  ;; Opcode for ld ixl, c
                            143 .endm
                            144 
                            145 ;; Macro: ld__ixl_d
                            146 ;;    Opcode for "LD ixl, D" instruction
                            147 ;; 
                            148 .mdelete ld__ixl_d
                            149 .macro ld__ixl_d
                            150    .dw #0x6ADD  ;; Opcode for ld ixl, d
                            151 .endm
                            152 
                            153 ;; Macro: ld__ixl_e
                            154 ;;    Opcode for "LD ixl, E" instruction
                            155 ;; 
                            156 .mdelete ld__ixl_e
                            157 .macro ld__ixl_e
                            158    .dw #0x6BDD  ;; Opcode for ld ixl, e
                            159 .endm
                            160 
                            161 ;; Macro: ld__ixl_ixh
                            162 ;;    Opcode for "LD ixl, IXH" instruction
                            163 ;; 
                            164 .mdelete  ld__ixl_ixh
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 20.
Hexadecimal [16-Bits]



                            165 .macro ld__ixl_ixh
                            166    .dw #0x6CDD  ;; Opcode for ld ixl, ixh
                            167 .endm
                            168 
                            169 ;; Macro: ld__a_ixl
                            170 ;;    Opcode for "LD A, ixl" instruction
                            171 ;; 
                            172 .mdelete ld__a_ixl
                            173 .macro ld__a_ixl
                            174    .dw #0x7DDD  ;; Opcode for ld a, ixl
                            175 .endm
                            176 
                            177 ;; Macro: ld__b_ixl
                            178 ;;    Opcode for "LD B, ixl" instruction
                            179 ;; 
                            180 .mdelete ld__b_ixl
                            181 .macro ld__b_ixl
                            182    .dw #0x45DD  ;; Opcode for ld b, ixl
                            183 .endm
                            184 
                            185 ;; Macro: ld__c_ixl
                            186 ;;    Opcode for "LD c, ixl" instruction
                            187 ;; 
                            188 .mdelete ld__c_ixl
                            189 .macro ld__c_ixl
                            190    .dw #0x4DDD  ;; Opcode for ld c, ixl
                            191 .endm
                            192 
                            193 ;; Macro: ld__d_ixl
                            194 ;;    Opcode for "LD D, ixl" instruction
                            195 ;; 
                            196 .mdelete ld__d_ixl
                            197 .macro ld__d_ixl
                            198    .dw #0x55DD  ;; Opcode for ld d, ixl
                            199 .endm
                            200 
                            201 ;; Macro: ld__e_ixl
                            202 ;;    Opcode for "LD e, ixl" instruction
                            203 ;; 
                            204 .mdelete ld__e_ixl
                            205 .macro ld__e_ixl
                            206    .dw #0x5DDD  ;; Opcode for ld e, ixl
                            207 .endm
                            208 
                            209 ;; Macro: add__ixl
                            210 ;;    Opcode for "Add ixl" instruction
                            211 ;; 
                            212 .mdelete add__ixl
                            213 .macro add__ixl
                            214    .dw #0x85DD  ;; Opcode for add ixl
                            215 .endm
                            216 
                            217 ;; Macro: sub__ixl
                            218 ;;    Opcode for "SUB ixl" instruction
                            219 ;; 
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 21.
Hexadecimal [16-Bits]



                            220 .mdelete sub__ixl
                            221 .macro sub__ixl
                            222    .dw #0x95DD  ;; Opcode for sub ixl
                            223 .endm
                            224 
                            225 ;; Macro: adc__ixl
                            226 ;;    Opcode for "ADC ixl" instruction
                            227 ;; 
                            228 .mdelete adc__ixl
                            229 .macro adc__ixl
                            230    .dw #0x8DDD  ;; Opcode for adc ixl
                            231 .endm
                            232 
                            233 ;; Macro: sbc__ixl
                            234 ;;    Opcode for "SBC ixl" instruction
                            235 ;; 
                            236 .mdelete sbc__ixl
                            237 .macro sbc__ixl
                            238    .dw #0x9DDD  ;; Opcode for sbc ixl
                            239 .endm
                            240 
                            241 ;; Macro: and__ixl
                            242 ;;    Opcode for "AND ixl" instruction
                            243 ;; 
                            244 .mdelete and__ixl
                            245 .macro and__ixl
                            246    .dw #0xA5DD  ;; Opcode for and ixl
                            247 .endm
                            248 
                            249 ;; Macro: or__ixl
                            250 ;;    Opcode for "OR ixl" instruction
                            251 ;; 
                            252 .mdelete or__ixl
                            253 .macro or__ixl
                            254    .dw #0xB5DD  ;; Opcode for or ixl
                            255 .endm
                            256 
                            257 ;; Macro: xor__ixl
                            258 ;;    Opcode for "XOR ixl" instruction
                            259 ;; 
                            260 .mdelete xor__ixl
                            261 .macro xor__ixl
                            262    .dw #0xADDD  ;; Opcode for xor ixl
                            263 .endm
                            264 
                            265 ;; Macro: cp__ixl
                            266 ;;    Opcode for "CP ixl" instruction
                            267 ;; 
                            268 .mdelete cp__ixl
                            269 .macro cp__ixl
                            270    .dw #0xBDDD  ;; Opcode for cp ixl
                            271 .endm
                            272 
                            273 ;; Macro: dec__ixl
                            274 ;;    Opcode for "DEC ixl" instruction
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 22.
Hexadecimal [16-Bits]



                            275 ;; 
                            276 .mdelete dec__ixl
                            277 .macro dec__ixl
                            278    .dw #0x2DDD  ;; Opcode for dec ixl
                            279 .endm
                            280 
                            281 ;; Macro: inc__ixl
                            282 ;;    Opcode for "INC ixl" instruction
                            283 ;; 
                            284 .mdelete inc__ixl
                            285 .macro inc__ixl
                            286    .dw #0x2CDD  ;; Opcode for inc ixl
                            287 .endm
                            288 
                            289 
                            290 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,
                            291 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,
                            292 ;; IXH Related Macros
                            293 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,
                            294 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,
                            295 
                            296 ;; Macro: ld__ixh    Value
                            297 ;;    Opcode for "LD IXH, Value" instruction
                            298 ;;  
                            299 ;; Parameters:
                            300 ;;    Value - An inmediate 8-bits value that will be loaded into IXH
                            301 ;; 
                            302 .mdelete  ld__ixh
                            303 .macro ld__ixh    Value 
                            304    .db #0xDD, #0x26, Value  ;; Opcode for ld ixh, Value
                            305 .endm
                            306 
                            307 ;; Macro: ld__ixh_a
                            308 ;;    Opcode for "LD IXH, a" instruction
                            309 ;; 
                            310 .mdelete ld__ixh_a
                            311 .macro ld__ixh_a
                            312    .dw #0x67DD  ;; Opcode for ld ixh, a
                            313 .endm
                            314 
                            315 ;; Macro: ld__ixh_b
                            316 ;;    Opcode for "LD IXH, B" instruction
                            317 ;; 
                            318 .mdelete ld__ixh_b
                            319 .macro ld__ixh_b
                            320    .dw #0x60DD  ;; Opcode for ld ixh, b
                            321 .endm
                            322 
                            323 ;; Macro: ld__ixh_c
                            324 ;;    Opcode for "LD IXH, C" instruction
                            325 ;; 
                            326 .mdelete ld__ixh_c
                            327 .macro ld__ixh_c
                            328    .dw #0x61DD  ;; Opcode for ld ixh, c
                            329 .endm
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 23.
Hexadecimal [16-Bits]



                            330 
                            331 ;; Macro: ld__ixh_d
                            332 ;;    Opcode for "LD IXH, D" instruction
                            333 ;; 
                            334 .mdelete ld__ixh_d
                            335 .macro ld__ixh_d
                            336    .dw #0x62DD  ;; Opcode for ld ixh, d
                            337 .endm
                            338 
                            339 ;; Macro: ld__ixh_e
                            340 ;;    Opcode for "LD IXH, E" instruction
                            341 ;; 
                            342 .mdelete ld__ixh_e
                            343 .macro ld__ixh_e
                            344    .dw #0x63DD  ;; Opcode for ld ixh, e
                            345 .endm
                            346 
                            347 ;; Macro: ld__ixh_ixl
                            348 ;;    Opcode for "LD IXH, IXL" instruction
                            349 ;; 
                            350 .mdelete ld__ixh_ixl
                            351 .macro ld__ixh_ixl
                            352    .dw #0x65DD  ;; Opcode for ld ixh, ixl
                            353 .endm
                            354 
                            355 ;; Macro: ld__a_ixh
                            356 ;;    Opcode for "LD A, IXH" instruction
                            357 ;; 
                            358 .mdelete ld__a_ixh
                            359 .macro ld__a_ixh
                            360    .dw #0x7CDD  ;; Opcode for ld a, ixh
                            361 .endm
                            362 
                            363 ;; Macro: ld__b_ixh
                            364 ;;    Opcode for "LD B, IXH" instruction
                            365 ;; 
                            366 .mdelete ld__b_ixh
                            367 .macro ld__b_ixh
                            368    .dw #0x44DD  ;; Opcode for ld b, ixh
                            369 .endm
                            370 
                            371 ;; Macro: ld__c_ixh
                            372 ;;    Opcode for "LD c, IXH" instruction
                            373 ;; 
                            374 .mdelete ld__c_ixh
                            375 .macro ld__c_ixh
                            376    .dw #0x4CDD  ;; Opcode for ld c, ixh
                            377 .endm
                            378 
                            379 ;; Macro: ld__d_ixh
                            380 ;;    Opcode for "LD D, IXH" instruction
                            381 ;; 
                            382 .mdelete ld__d_ixh
                            383 .macro ld__d_ixh
                            384    .dw #0x54DD  ;; Opcode for ld d, ixh
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 24.
Hexadecimal [16-Bits]



                            385 .endm
                            386 
                            387 ;; Macro: ld__e_ixh
                            388 ;;    Opcode for "LD e, IXH" instruction
                            389 ;; 
                            390 .mdelete ld__e_ixh
                            391 .macro ld__e_ixh
                            392    .dw #0x5CDD  ;; Opcode for ld e, ixh
                            393 .endm
                            394 
                            395 ;; Macro: add__ixh
                            396 ;;    Opcode for "ADD IXH" instruction
                            397 ;; 
                            398 .mdelete add__ixh
                            399 .macro add__ixh
                            400    .dw #0x84DD  ;; Opcode for add ixh
                            401 .endm
                            402 
                            403 ;; Macro: sub__ixh
                            404 ;;    Opcode for "SUB IXH" instruction
                            405 ;; 
                            406 .mdelete sub__ixh
                            407 .macro sub__ixh
                            408    .dw #0x94DD  ;; Opcode for sub ixh
                            409 .endm
                            410 
                            411 ;; Macro: adc__ixh
                            412 ;;    Opcode for "ADC IXH" instruction
                            413 ;; 
                            414 .mdelete adc__ixh
                            415 .macro adc__ixh
                            416    .dw #0x8CDD  ;; Opcode for adc ixh
                            417 .endm
                            418 
                            419 ;; Macro: sbc__ixh
                            420 ;;    Opcode for "SBC IXH" instruction
                            421 ;; 
                            422 .mdelete sbc__ixh
                            423 .macro sbc__ixh
                            424    .dw #0x9CDD  ;; Opcode for sbc ixh
                            425 .endm
                            426 
                            427 ;; Macro: and__ixh
                            428 ;;    Opcode for "AND IXH" instruction
                            429 ;; 
                            430 .mdelete and__ixh
                            431 .macro and__ixh
                            432    .dw #0xA4DD  ;; Opcode for and ixh
                            433 .endm
                            434 
                            435 ;; Macro: or__ixh
                            436 ;;    Opcode for "OR IXH" instruction
                            437 ;; 
                            438 .mdelete or__ixh
                            439 .macro or__ixh
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 25.
Hexadecimal [16-Bits]



                            440    .dw #0xB4DD  ;; Opcode for or ixh
                            441 .endm
                            442 
                            443 ;; Macro: xor__ixh
                            444 ;;    Opcode for "XOR IXH" instruction
                            445 ;; 
                            446 .mdelete xor__ixh
                            447 .macro xor__ixh
                            448    .dw #0xACDD  ;; Opcode for xor ixh
                            449 .endm
                            450 
                            451 ;; Macro: cp__ixh
                            452 ;;    Opcode for "CP IXH" instruction
                            453 ;; 
                            454 .mdelete cp__ixh
                            455 .macro cp__ixh
                            456    .dw #0xBCDD  ;; Opcode for cp ixh
                            457 .endm
                            458 
                            459 ;; Macro: dec__ixh
                            460 ;;    Opcode for "DEC IXH" instruction
                            461 ;; 
                            462 .mdelete dec__ixh
                            463 .macro dec__ixh
                            464    .dw #0x25DD  ;; Opcode for dec ixh
                            465 .endm
                            466 
                            467 ;; Macro: inc__ixh
                            468 ;;    Opcode for "INC IXH" instruction
                            469 ;; 
                            470 .mdelete inc__ixh
                            471 .macro inc__ixh
                            472    .dw #0x24DD  ;; Opcode for inc ixh
                            473 .endm
                            474 
                            475 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,
                            476 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,
                            477 ;; IYL Related Macros
                            478 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,
                            479 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,
                            480 
                            481 ;; Macro: ld__iyl    Value
                            482 ;;    Opcode for "LD iyl, Value" instruction
                            483 ;;  
                            484 ;; Parameters:
                            485 ;;    Value - An inmediate 8-bits value that will be loaded into iyl
                            486 ;; 
                            487 .mdelete  ld__iyl
                            488 .macro ld__iyl    Value 
                            489    .db #0xFD, #0x2E, Value  ;; Opcode for ld iyl, Value
                            490 .endm
                            491 
                            492 ;; Macro: ld__iyl_a
                            493 ;;    Opcode for "LD iyl, a" instruction
                            494 ;; 
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 26.
Hexadecimal [16-Bits]



                            495 .mdelete ld__iyl_a
                            496 .macro ld__iyl_a
                            497    .dw #0x6FFD  ;; Opcode for ld iyl, a
                            498 .endm
                            499 
                            500 ;; Macro: ld__iyl_b
                            501 ;;    Opcode for "LD iyl, B" instruction
                            502 ;; 
                            503 .mdelete ld__iyl_b
                            504 .macro ld__iyl_b
                            505    .dw #0x68FD  ;; Opcode for ld iyl, b
                            506 .endm
                            507 
                            508 ;; Macro: ld__iyl_c
                            509 ;;    Opcode for "LD iyl, C" instruction
                            510 ;; 
                            511 .mdelete ld__iyl_c
                            512 .macro ld__iyl_c
                            513    .dw #0x69FD  ;; Opcode for ld iyl, c
                            514 .endm
                            515 
                            516 ;; Macro: ld__iyl_d
                            517 ;;    Opcode for "LD iyl, D" instruction
                            518 ;; 
                            519 .mdelete ld__iyl_d
                            520 .macro ld__iyl_d
                            521    .dw #0x6AFD  ;; Opcode for ld iyl, d
                            522 .endm
                            523 
                            524 ;; Macro: ld__iyl_e
                            525 ;;    Opcode for "LD iyl, E" instruction
                            526 ;; 
                            527 .mdelete ld__iyl_e
                            528 .macro ld__iyl_e
                            529    .dw #0x6BFD  ;; Opcode for ld iyl, e
                            530 .endm
                            531 
                            532 ;; Macro: ld__iyl_iyh
                            533 ;;    Opcode for "LD iyl, IXL" instruction
                            534 ;; 
                            535 .mdelete  ld__iyl_iyh
                            536 .macro ld__iyl_iyh
                            537    .dw #0x6CFD  ;; Opcode for ld iyl, ixl
                            538 .endm
                            539 
                            540 ;; Macro: ld__a_iyl
                            541 ;;    Opcode for "LD A, iyl" instruction
                            542 ;; 
                            543 .mdelete ld__a_iyl
                            544 .macro ld__a_iyl
                            545    .dw #0x7DFD  ;; Opcode for ld a, iyl
                            546 .endm
                            547 
                            548 ;; Macro: ld__b_iyl
                            549 ;;    Opcode for "LD B, iyl" instruction
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 27.
Hexadecimal [16-Bits]



                            550 ;; 
                            551 .mdelete ld__b_iyl
                            552 .macro ld__b_iyl
                            553    .dw #0x45FD  ;; Opcode for ld b, iyl
                            554 .endm
                            555 
                            556 ;; Macro: ld__c_iyl
                            557 ;;    Opcode for "LD c, iyl" instruction
                            558 ;; 
                            559 .mdelete ld__c_iyl
                            560 .macro ld__c_iyl
                            561    .dw #0x4DFD  ;; Opcode for ld c, iyl
                            562 .endm
                            563 
                            564 ;; Macro: ld__d_iyl
                            565 ;;    Opcode for "LD D, iyl" instruction
                            566 ;; 
                            567 .mdelete ld__d_iyl
                            568 .macro ld__d_iyl
                            569    .dw #0x55FD  ;; Opcode for ld d, iyl
                            570 .endm
                            571 
                            572 ;; Macro: ld__e_iyl
                            573 ;;    Opcode for "LD e, iyl" instruction
                            574 ;; 
                            575 .mdelete ld__e_iyl
                            576 .macro ld__e_iyl
                            577    .dw #0x5DFD  ;; Opcode for ld e, iyl
                            578 .endm
                            579 
                            580 ;; Macro: add__iyl
                            581 ;;    Opcode for "Add iyl" instruction
                            582 ;; 
                            583 .mdelete add__iyl
                            584 .macro add__iyl
                            585    .dw #0x85FD  ;; Opcode for add iyl
                            586 .endm
                            587 
                            588 ;; Macro: sub__iyl
                            589 ;;    Opcode for "SUB iyl" instruction
                            590 ;; 
                            591 .mdelete sub__iyl
                            592 .macro sub__iyl
                            593    .dw #0x95FD  ;; Opcode for sub iyl
                            594 .endm
                            595 
                            596 ;; Macro: adc__iyl
                            597 ;;    Opcode for "ADC iyl" instruction
                            598 ;; 
                            599 .mdelete adc__iyl
                            600 .macro adc__iyl
                            601    .dw #0x8DFD  ;; Opcode for adc iyl
                            602 .endm
                            603 
                            604 ;; Macro: sbc__iyl
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 28.
Hexadecimal [16-Bits]



                            605 ;;    Opcode for "SBC iyl" instruction
                            606 ;; 
                            607 .mdelete sbc__iyl
                            608 .macro sbc__iyl
                            609    .dw #0x9DFD  ;; Opcode for sbc iyl
                            610 .endm
                            611 
                            612 ;; Macro: and__iyl
                            613 ;;    Opcode for "AND iyl" instruction
                            614 ;; 
                            615 .mdelete and__iyl
                            616 .macro and__iyl
                            617    .dw #0xA5FD  ;; Opcode for and iyl
                            618 .endm
                            619 
                            620 ;; Macro: or__iyl
                            621 ;;    Opcode for "OR iyl" instruction
                            622 ;; 
                            623 .mdelete or__iyl
                            624 .macro or__iyl
                            625    .dw #0xB5FD  ;; Opcode for or iyl
                            626 .endm
                            627 
                            628 ;; Macro: xor__iyl
                            629 ;;    Opcode for "XOR iyl" instruction
                            630 ;; 
                            631 .mdelete xor__iyl
                            632 .macro xor__iyl
                            633    .dw #0xADFD  ;; Opcode for xor iyl
                            634 .endm
                            635 
                            636 ;; Macro: cp__iyl
                            637 ;;    Opcode for "CP iyl" instruction
                            638 ;; 
                            639 .mdelete cp__iyl
                            640 .macro cp__iyl
                            641    .dw #0xBDFD  ;; Opcode for cp iyl
                            642 .endm
                            643 
                            644 ;; Macro: dec__iyl
                            645 ;;    Opcode for "DEC iyl" instruction
                            646 ;; 
                            647 .mdelete dec__iyl
                            648 .macro dec__iyl
                            649    .dw #0x2DFD  ;; Opcode for dec iyl
                            650 .endm
                            651 
                            652 ;; Macro: inc__iyl
                            653 ;;    Opcode for "INC iyl" instruction
                            654 ;; 
                            655 .mdelete inc__iyl
                            656 .macro inc__iyl
                            657    .dw #0x2CFD  ;; Opcode for inc iyl
                            658 .endm
                            659 
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 29.
Hexadecimal [16-Bits]



                            660 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,
                            661 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,
                            662 ;; IYH Related Macros
                            663 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,
                            664 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,
                            665 
                            666 ;; Macro: ld__iyh    Value
                            667 ;;    Opcode for "LD iyh, Value" instruction
                            668 ;;  
                            669 ;; Parameters:
                            670 ;;    Value - An inmediate 8-bits value that will be loaded into iyh
                            671 ;; 
                            672 .mdelete  ld__iyh
                            673 .macro ld__iyh    Value 
                            674    .db #0xFD, #0x26, Value  ;; Opcode for ld iyh, Value
                            675 .endm
                            676 
                            677 ;; Macro: ld__iyh_a
                            678 ;;    Opcode for "LD iyh, a" instruction
                            679 ;; 
                            680 .mdelete ld__iyh_a
                            681 .macro ld__iyh_a
                            682    .dw #0x67FD  ;; Opcode for ld iyh, a
                            683 .endm
                            684 
                            685 ;; Macro: ld__iyh_b
                            686 ;;    Opcode for "LD iyh, B" instruction
                            687 ;; 
                            688 .mdelete ld__iyh_b
                            689 .macro ld__iyh_b
                            690    .dw #0x60FD  ;; Opcode for ld iyh, b
                            691 .endm
                            692 
                            693 ;; Macro: ld__iyh_c
                            694 ;;    Opcode for "LD iyh, C" instruction
                            695 ;; 
                            696 .mdelete ld__iyh_c
                            697 .macro ld__iyh_c
                            698    .dw #0x61FD  ;; Opcode for ld iyh, c
                            699 .endm
                            700 
                            701 ;; Macro: ld__iyh_d
                            702 ;;    Opcode for "LD iyh, D" instruction
                            703 ;; 
                            704 .mdelete ld__iyh_d
                            705 .macro ld__iyh_d
                            706    .dw #0x62FD  ;; Opcode for ld iyh, d
                            707 .endm
                            708 
                            709 ;; Macro: ld__iyh_e
                            710 ;;    Opcode for "LD iyh, E" instruction
                            711 ;; 
                            712 .mdelete ld__iyh_e
                            713 .macro ld__iyh_e
                            714    .dw #0x63FD  ;; Opcode for ld iyh, e
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 30.
Hexadecimal [16-Bits]



                            715 .endm
                            716 
                            717 ;; Macro: ld__iyh_iyl
                            718 ;;    Opcode for "LD iyh, IyL" instruction
                            719 ;; 
                            720 .mdelete  ld__iyh_iyl
                            721 .macro ld__iyh_iyl
                            722    .dw #0x65FD  ;; Opcode for ld iyh, iyl
                            723 .endm
                            724 
                            725 ;; Macro: ld__a_iyh
                            726 ;;    Opcode for "LD A, iyh" instruction
                            727 ;; 
                            728 .mdelete ld__a_iyh
                            729 .macro ld__a_iyh
                            730    .dw #0x7CFD  ;; Opcode for ld a, iyh
                            731 .endm
                            732 
                            733 ;; Macro: ld__b_iyh
                            734 ;;    Opcode for "LD B, iyh" instruction
                            735 ;; 
                            736 .mdelete ld__b_iyh
                            737 .macro ld__b_iyh
                            738    .dw #0x44FD  ;; Opcode for ld b, iyh
                            739 .endm
                            740 
                            741 ;; Macro: ld__c_iyh
                            742 ;;    Opcode for "LD c, iyh" instruction
                            743 ;; 
                            744 .mdelete ld__c_iyh
                            745 .macro ld__c_iyh
                            746    .dw #0x4CFD  ;; Opcode for ld c, iyh
                            747 .endm
                            748 
                            749 ;; Macro: ld__d_iyh
                            750 ;;    Opcode for "LD D, iyh" instruction
                            751 ;; 
                            752 .mdelete ld__d_iyh
                            753 .macro ld__d_iyh
                            754    .dw #0x54FD  ;; Opcode for ld d, iyh
                            755 .endm
                            756 
                            757 ;; Macro: ld__e_iyh
                            758 ;;    Opcode for "LD e, iyh" instruction
                            759 ;; 
                            760 .mdelete ld__e_iyh
                            761 .macro ld__e_iyh
                            762    .dw #0x5CFD  ;; Opcode for ld e, iyh
                            763 .endm
                            764 
                            765 ;; Macro: add__iyh
                            766 ;;    Opcode for "Add iyh" instruction
                            767 ;; 
                            768 .mdelete add__iyh
                            769 .macro add__iyh
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 31.
Hexadecimal [16-Bits]



                            770    .dw #0x84FD  ;; Opcode for add iyh
                            771 .endm
                            772 
                            773 ;; Macro: sub__iyh
                            774 ;;    Opcode for "SUB iyh" instruction
                            775 ;; 
                            776 .mdelete sub__iyh
                            777 .macro sub__iyh
                            778    .dw #0x94FD  ;; Opcode for sub iyh
                            779 .endm
                            780 
                            781 ;; Macro: adc__iyh
                            782 ;;    Opcode for "ADC iyh" instruction
                            783 ;; 
                            784 .mdelete adc__iyh
                            785 .macro adc__iyh
                            786    .dw #0x8CFD  ;; Opcode for adc iyh
                            787 .endm
                            788 
                            789 ;; Macro: sbc__iyh
                            790 ;;    Opcode for "SBC iyh" instruction
                            791 ;; 
                            792 .mdelete sbc__iyh
                            793 .macro sbc__iyh
                            794    .dw #0x9CFD  ;; Opcode for sbc iyh
                            795 .endm
                            796 
                            797 ;; Macro: and__iyh
                            798 ;;    Opcode for "AND iyh" instruction
                            799 ;; 
                            800 .mdelete and__iyh
                            801 .macro and__iyh
                            802    .dw #0xA4FD  ;; Opcode for and iyh
                            803 .endm
                            804 
                            805 ;; Macro: or__iyh
                            806 ;;    Opcode for "OR iyh" instruction
                            807 ;; 
                            808 .mdelete or__iyh
                            809 .macro or__iyh
                            810    .dw #0xB4FD  ;; Opcode for or iyh
                            811 .endm
                            812 
                            813 ;; Macro: xor__iyh
                            814 ;;    Opcode for "XOR iyh" instruction
                            815 ;; 
                            816 .mdelete xor__iyh
                            817 .macro xor__iyh
                            818    .dw #0xACFD  ;; Opcode for xor iyh
                            819 .endm
                            820 
                            821 ;; Macro: cp__iyh
                            822 ;;    Opcode for "CP iyh" instruction
                            823 ;; 
                            824 .mdelete cp__iyh
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 32.
Hexadecimal [16-Bits]



                            825 .macro cp__iyh
                            826    .dw #0xBCFD  ;; Opcode for cp iyh
                            827 .endm
                            828 
                            829 ;; Macro: dec__iyh
                            830 ;;    Opcode for "DEC iyh" instruction
                            831 ;; 
                            832 .mdelete dec__iyh
                            833 .macro dec__iyh
                            834    .dw #0x25FD  ;; Opcode for dec iyh
                            835 .endm
                            836 
                            837 ;; Macro: inc__iyh
                            838 ;;    Opcode for "INC iyh" instruction
                            839 ;; 
                            840 .mdelete inc__iyh
                            841 .macro inc__iyh
                            842    .dw #0x24FD  ;; Opcode for inc iyh
                            843 .endm
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 33.
Hexadecimal [16-Bits]



                             23 .include "macros/cpct_combinedOperations.h.s"
                              1 ;;-----------------------------LICENSE NOTICE------------------------------------
                              2 ;;  This file is part of CPCtelera: An Amstrad CPC Game Engine 
                              3 ;;  Copyright (C) 2021 ronaldo / Fremos / Cheesetea / ByteRealms (@FranGallegoBR)
                              4 ;;
                              5 ;;  This program is free software: you can redistribute it and/or modify
                              6 ;;  it under the terms of the GNU Lesser General Public License as published by
                              7 ;;  the Free Software Foundation, either version 3 of the License, or
                              8 ;;  (at your option) any later version.
                              9 ;;
                             10 ;;  This program is distributed in the hope that it will be useful,
                             11 ;;  but WITHOUT ANY WARRANTY; without even the implied warranty of
                             12 ;;  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
                             13 ;;  GNU Lesser General Public License for more details.
                             14 ;;
                             15 ;;  You should have received a copy of the GNU Lesser General Public License
                             16 ;;  along with this program.  If not, see <http://www.gnu.org/licenses/>.
                             17 ;;-------------------------------------------------------------------------------
                             18 
                             19 ;;
                             20 ;; File: Combined operations
                             21 ;;
                             22 ;;    Macros to clarify source code that combine several operations in one macro.
                             23 ;; For instance, macros to copy HL to DE or IX to DE, that require 2 or more 
                             24 ;; instructions but are commonly used.
                             25 ;;
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 34.
Hexadecimal [16-Bits]



                             26 .include "macros/cpct_undocumentedOpcodes.h.s"
                              1 ;;-----------------------------LICENSE NOTICE------------------------------------
                              2 ;;  This file is part of CPCtelera: An Amstrad CPC Game Engine 
                              3 ;;  Copyright (C) 2021 ronaldo / Fremos / Cheesetea / ByteRealms (@FranGallegoBR)
                              4 ;;
                              5 ;;  This program is free software: you can redistribute it and/or modify
                              6 ;;  it under the terms of the GNU Lesser General Public License as published by
                              7 ;;  the Free Software Foundation, either version 3 of the License, or
                              8 ;;  (at your option) any later version.
                              9 ;;
                             10 ;;  This program is distributed in the hope that it will be useful,
                             11 ;;  but WITHOUT ANY WARRANTY; without even the implied warranty of
                             12 ;;  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
                             13 ;;  GNU Lesser General Public License for more details.
                             14 ;;
                             15 ;;  You should have received a copy of the GNU Lesser General Public License
                             16 ;;  along with this program.  If not, see <http://www.gnu.org/licenses/>.
                             17 ;;-------------------------------------------------------------------------------
                             18 
                             19 ;;
                             20 ;; File: Undocumented Opcodes
                             21 ;;
                             22 ;;    Macros to clarify source code when using undocumented opcodes. Only
                             23 ;; valid to be used from assembly language (not from C).
                             24 ;;
                             25 
                             26 ;; Macro: jr__0
                             27 ;;    Opcode for "JR #0" instruction
                             28 ;; 
                             29 .mdelete jr__0
                             30 .macro jr__0
                             31    .DW #0x0018  ;; JR #00 (Normally used as a modifiable jump, as jr 0 is an infinite loop)
                             32 .endm
                             33 
                             34 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,
                             35 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,
                             36 ;; SLL Instructions
                             37 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,
                             38 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,
                             39 
                             40 ;; Macro: sll__b
                             41 ;;    Opcode for "SLL b" instruction
                             42 ;; 
                             43 .mdelete sll__b
                             44 .macro sll__b
                             45    .db #0xCB, #0x30  ;; Opcode for sll b
                             46 .endm
                             47 
                             48 ;; Macro: sll__c
                             49 ;;    Opcode for "SLL c" instruction
                             50 ;; 
                             51 .mdelete sll__c
                             52 .macro sll__c
                             53    .db #0xCB, #0x31  ;; Opcode for sll c
                             54 .endm
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 35.
Hexadecimal [16-Bits]



                             55 
                             56 ;; Macro: sll__d
                             57 ;;    Opcode for "SLL d" instruction
                             58 ;; 
                             59 .mdelete sll__d
                             60 .macro sll__d
                             61    .db #0xCB, #0x32  ;; Opcode for sll d
                             62 .endm
                             63 
                             64 ;; Macro: sll__e
                             65 ;;    Opcode for "SLL e" instruction
                             66 ;; 
                             67 .mdelete sll__e
                             68 .macro sll__e
                             69    .db #0xCB, #0x33  ;; Opcode for sll e
                             70 .endm
                             71 
                             72 ;; Macro: sll__h
                             73 ;;    Opcode for "SLL h" instruction
                             74 ;; 
                             75 .mdelete sll__h
                             76 .macro sll__h
                             77    .db #0xCB, #0x34  ;; Opcode for sll h
                             78 .endm
                             79 
                             80 ;; Macro: sll__l
                             81 ;;    Opcode for "SLL l" instruction
                             82 ;; 
                             83 .mdelete sll__l
                             84 .macro sll__l
                             85    .db #0xCB, #0x35  ;; Opcode for sll l
                             86 .endm
                             87 
                             88 ;; Macro: sll___hl_
                             89 ;;    Opcode for "SLL (hl)" instruction
                             90 ;; 
                             91 .mdelete sll___hl_
                             92 .macro sll___hl_
                             93    .db #0xCB, #0x36  ;; Opcode for sll (hl)
                             94 .endm
                             95 
                             96 ;; Macro: sll__a
                             97 ;;    Opcode for "SLL a" instruction
                             98 ;; 
                             99 .mdelete sll__a
                            100 .macro sll__a
                            101    .db #0xCB, #0x37  ;; Opcode for sll a
                            102 .endm
                            103 
                            104 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,
                            105 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,
                            106 ;; IXL Related Macros
                            107 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,
                            108 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,
                            109 
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 36.
Hexadecimal [16-Bits]



                            110 ;; Macro: ld__ixl    Value
                            111 ;;    Opcode for "LD ixl, Value" instruction
                            112 ;;  
                            113 ;; Parameters:
                            114 ;;    Value - An inmediate 8-bits value that will be loaded into ixl
                            115 ;; 
                            116 .mdelete ld__ixl
                            117 .macro ld__ixl    Value 
                            118    .db #0xDD, #0x2E, Value  ;; Opcode for ld ixl, Value
                            119 .endm
                            120 
                            121 ;; Macro: ld__ixl_a
                            122 ;;    Opcode for "LD ixl, a" instruction
                            123 ;; 
                            124 .mdelete ld__ixl_a
                            125 .macro ld__ixl_a
                            126    .dw #0x6FDD  ;; Opcode for ld ixl, a
                            127 .endm
                            128 
                            129 ;; Macro: ld__ixl_b
                            130 ;;    Opcode for "LD ixl, B" instruction
                            131 ;; 
                            132 .mdelete ld__ixl_b
                            133 .macro ld__ixl_b
                            134    .dw #0x68DD  ;; Opcode for ld ixl, b
                            135 .endm
                            136 
                            137 ;; Macro: ld__ixl_c
                            138 ;;    Opcode for "LD ixl, C" instruction
                            139 ;; 
                            140 .mdelete ld__ixl_c
                            141 .macro ld__ixl_c
                            142    .dw #0x69DD  ;; Opcode for ld ixl, c
                            143 .endm
                            144 
                            145 ;; Macro: ld__ixl_d
                            146 ;;    Opcode for "LD ixl, D" instruction
                            147 ;; 
                            148 .mdelete ld__ixl_d
                            149 .macro ld__ixl_d
                            150    .dw #0x6ADD  ;; Opcode for ld ixl, d
                            151 .endm
                            152 
                            153 ;; Macro: ld__ixl_e
                            154 ;;    Opcode for "LD ixl, E" instruction
                            155 ;; 
                            156 .mdelete ld__ixl_e
                            157 .macro ld__ixl_e
                            158    .dw #0x6BDD  ;; Opcode for ld ixl, e
                            159 .endm
                            160 
                            161 ;; Macro: ld__ixl_ixh
                            162 ;;    Opcode for "LD ixl, IXH" instruction
                            163 ;; 
                            164 .mdelete  ld__ixl_ixh
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 37.
Hexadecimal [16-Bits]



                            165 .macro ld__ixl_ixh
                            166    .dw #0x6CDD  ;; Opcode for ld ixl, ixh
                            167 .endm
                            168 
                            169 ;; Macro: ld__a_ixl
                            170 ;;    Opcode for "LD A, ixl" instruction
                            171 ;; 
                            172 .mdelete ld__a_ixl
                            173 .macro ld__a_ixl
                            174    .dw #0x7DDD  ;; Opcode for ld a, ixl
                            175 .endm
                            176 
                            177 ;; Macro: ld__b_ixl
                            178 ;;    Opcode for "LD B, ixl" instruction
                            179 ;; 
                            180 .mdelete ld__b_ixl
                            181 .macro ld__b_ixl
                            182    .dw #0x45DD  ;; Opcode for ld b, ixl
                            183 .endm
                            184 
                            185 ;; Macro: ld__c_ixl
                            186 ;;    Opcode for "LD c, ixl" instruction
                            187 ;; 
                            188 .mdelete ld__c_ixl
                            189 .macro ld__c_ixl
                            190    .dw #0x4DDD  ;; Opcode for ld c, ixl
                            191 .endm
                            192 
                            193 ;; Macro: ld__d_ixl
                            194 ;;    Opcode for "LD D, ixl" instruction
                            195 ;; 
                            196 .mdelete ld__d_ixl
                            197 .macro ld__d_ixl
                            198    .dw #0x55DD  ;; Opcode for ld d, ixl
                            199 .endm
                            200 
                            201 ;; Macro: ld__e_ixl
                            202 ;;    Opcode for "LD e, ixl" instruction
                            203 ;; 
                            204 .mdelete ld__e_ixl
                            205 .macro ld__e_ixl
                            206    .dw #0x5DDD  ;; Opcode for ld e, ixl
                            207 .endm
                            208 
                            209 ;; Macro: add__ixl
                            210 ;;    Opcode for "Add ixl" instruction
                            211 ;; 
                            212 .mdelete add__ixl
                            213 .macro add__ixl
                            214    .dw #0x85DD  ;; Opcode for add ixl
                            215 .endm
                            216 
                            217 ;; Macro: sub__ixl
                            218 ;;    Opcode for "SUB ixl" instruction
                            219 ;; 
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 38.
Hexadecimal [16-Bits]



                            220 .mdelete sub__ixl
                            221 .macro sub__ixl
                            222    .dw #0x95DD  ;; Opcode for sub ixl
                            223 .endm
                            224 
                            225 ;; Macro: adc__ixl
                            226 ;;    Opcode for "ADC ixl" instruction
                            227 ;; 
                            228 .mdelete adc__ixl
                            229 .macro adc__ixl
                            230    .dw #0x8DDD  ;; Opcode for adc ixl
                            231 .endm
                            232 
                            233 ;; Macro: sbc__ixl
                            234 ;;    Opcode for "SBC ixl" instruction
                            235 ;; 
                            236 .mdelete sbc__ixl
                            237 .macro sbc__ixl
                            238    .dw #0x9DDD  ;; Opcode for sbc ixl
                            239 .endm
                            240 
                            241 ;; Macro: and__ixl
                            242 ;;    Opcode for "AND ixl" instruction
                            243 ;; 
                            244 .mdelete and__ixl
                            245 .macro and__ixl
                            246    .dw #0xA5DD  ;; Opcode for and ixl
                            247 .endm
                            248 
                            249 ;; Macro: or__ixl
                            250 ;;    Opcode for "OR ixl" instruction
                            251 ;; 
                            252 .mdelete or__ixl
                            253 .macro or__ixl
                            254    .dw #0xB5DD  ;; Opcode for or ixl
                            255 .endm
                            256 
                            257 ;; Macro: xor__ixl
                            258 ;;    Opcode for "XOR ixl" instruction
                            259 ;; 
                            260 .mdelete xor__ixl
                            261 .macro xor__ixl
                            262    .dw #0xADDD  ;; Opcode for xor ixl
                            263 .endm
                            264 
                            265 ;; Macro: cp__ixl
                            266 ;;    Opcode for "CP ixl" instruction
                            267 ;; 
                            268 .mdelete cp__ixl
                            269 .macro cp__ixl
                            270    .dw #0xBDDD  ;; Opcode for cp ixl
                            271 .endm
                            272 
                            273 ;; Macro: dec__ixl
                            274 ;;    Opcode for "DEC ixl" instruction
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 39.
Hexadecimal [16-Bits]



                            275 ;; 
                            276 .mdelete dec__ixl
                            277 .macro dec__ixl
                            278    .dw #0x2DDD  ;; Opcode for dec ixl
                            279 .endm
                            280 
                            281 ;; Macro: inc__ixl
                            282 ;;    Opcode for "INC ixl" instruction
                            283 ;; 
                            284 .mdelete inc__ixl
                            285 .macro inc__ixl
                            286    .dw #0x2CDD  ;; Opcode for inc ixl
                            287 .endm
                            288 
                            289 
                            290 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,
                            291 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,
                            292 ;; IXH Related Macros
                            293 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,
                            294 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,
                            295 
                            296 ;; Macro: ld__ixh    Value
                            297 ;;    Opcode for "LD IXH, Value" instruction
                            298 ;;  
                            299 ;; Parameters:
                            300 ;;    Value - An inmediate 8-bits value that will be loaded into IXH
                            301 ;; 
                            302 .mdelete  ld__ixh
                            303 .macro ld__ixh    Value 
                            304    .db #0xDD, #0x26, Value  ;; Opcode for ld ixh, Value
                            305 .endm
                            306 
                            307 ;; Macro: ld__ixh_a
                            308 ;;    Opcode for "LD IXH, a" instruction
                            309 ;; 
                            310 .mdelete ld__ixh_a
                            311 .macro ld__ixh_a
                            312    .dw #0x67DD  ;; Opcode for ld ixh, a
                            313 .endm
                            314 
                            315 ;; Macro: ld__ixh_b
                            316 ;;    Opcode for "LD IXH, B" instruction
                            317 ;; 
                            318 .mdelete ld__ixh_b
                            319 .macro ld__ixh_b
                            320    .dw #0x60DD  ;; Opcode for ld ixh, b
                            321 .endm
                            322 
                            323 ;; Macro: ld__ixh_c
                            324 ;;    Opcode for "LD IXH, C" instruction
                            325 ;; 
                            326 .mdelete ld__ixh_c
                            327 .macro ld__ixh_c
                            328    .dw #0x61DD  ;; Opcode for ld ixh, c
                            329 .endm
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 40.
Hexadecimal [16-Bits]



                            330 
                            331 ;; Macro: ld__ixh_d
                            332 ;;    Opcode for "LD IXH, D" instruction
                            333 ;; 
                            334 .mdelete ld__ixh_d
                            335 .macro ld__ixh_d
                            336    .dw #0x62DD  ;; Opcode for ld ixh, d
                            337 .endm
                            338 
                            339 ;; Macro: ld__ixh_e
                            340 ;;    Opcode for "LD IXH, E" instruction
                            341 ;; 
                            342 .mdelete ld__ixh_e
                            343 .macro ld__ixh_e
                            344    .dw #0x63DD  ;; Opcode for ld ixh, e
                            345 .endm
                            346 
                            347 ;; Macro: ld__ixh_ixl
                            348 ;;    Opcode for "LD IXH, IXL" instruction
                            349 ;; 
                            350 .mdelete ld__ixh_ixl
                            351 .macro ld__ixh_ixl
                            352    .dw #0x65DD  ;; Opcode for ld ixh, ixl
                            353 .endm
                            354 
                            355 ;; Macro: ld__a_ixh
                            356 ;;    Opcode for "LD A, IXH" instruction
                            357 ;; 
                            358 .mdelete ld__a_ixh
                            359 .macro ld__a_ixh
                            360    .dw #0x7CDD  ;; Opcode for ld a, ixh
                            361 .endm
                            362 
                            363 ;; Macro: ld__b_ixh
                            364 ;;    Opcode for "LD B, IXH" instruction
                            365 ;; 
                            366 .mdelete ld__b_ixh
                            367 .macro ld__b_ixh
                            368    .dw #0x44DD  ;; Opcode for ld b, ixh
                            369 .endm
                            370 
                            371 ;; Macro: ld__c_ixh
                            372 ;;    Opcode for "LD c, IXH" instruction
                            373 ;; 
                            374 .mdelete ld__c_ixh
                            375 .macro ld__c_ixh
                            376    .dw #0x4CDD  ;; Opcode for ld c, ixh
                            377 .endm
                            378 
                            379 ;; Macro: ld__d_ixh
                            380 ;;    Opcode for "LD D, IXH" instruction
                            381 ;; 
                            382 .mdelete ld__d_ixh
                            383 .macro ld__d_ixh
                            384    .dw #0x54DD  ;; Opcode for ld d, ixh
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 41.
Hexadecimal [16-Bits]



                            385 .endm
                            386 
                            387 ;; Macro: ld__e_ixh
                            388 ;;    Opcode for "LD e, IXH" instruction
                            389 ;; 
                            390 .mdelete ld__e_ixh
                            391 .macro ld__e_ixh
                            392    .dw #0x5CDD  ;; Opcode for ld e, ixh
                            393 .endm
                            394 
                            395 ;; Macro: add__ixh
                            396 ;;    Opcode for "ADD IXH" instruction
                            397 ;; 
                            398 .mdelete add__ixh
                            399 .macro add__ixh
                            400    .dw #0x84DD  ;; Opcode for add ixh
                            401 .endm
                            402 
                            403 ;; Macro: sub__ixh
                            404 ;;    Opcode for "SUB IXH" instruction
                            405 ;; 
                            406 .mdelete sub__ixh
                            407 .macro sub__ixh
                            408    .dw #0x94DD  ;; Opcode for sub ixh
                            409 .endm
                            410 
                            411 ;; Macro: adc__ixh
                            412 ;;    Opcode for "ADC IXH" instruction
                            413 ;; 
                            414 .mdelete adc__ixh
                            415 .macro adc__ixh
                            416    .dw #0x8CDD  ;; Opcode for adc ixh
                            417 .endm
                            418 
                            419 ;; Macro: sbc__ixh
                            420 ;;    Opcode for "SBC IXH" instruction
                            421 ;; 
                            422 .mdelete sbc__ixh
                            423 .macro sbc__ixh
                            424    .dw #0x9CDD  ;; Opcode for sbc ixh
                            425 .endm
                            426 
                            427 ;; Macro: and__ixh
                            428 ;;    Opcode for "AND IXH" instruction
                            429 ;; 
                            430 .mdelete and__ixh
                            431 .macro and__ixh
                            432    .dw #0xA4DD  ;; Opcode for and ixh
                            433 .endm
                            434 
                            435 ;; Macro: or__ixh
                            436 ;;    Opcode for "OR IXH" instruction
                            437 ;; 
                            438 .mdelete or__ixh
                            439 .macro or__ixh
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 42.
Hexadecimal [16-Bits]



                            440    .dw #0xB4DD  ;; Opcode for or ixh
                            441 .endm
                            442 
                            443 ;; Macro: xor__ixh
                            444 ;;    Opcode for "XOR IXH" instruction
                            445 ;; 
                            446 .mdelete xor__ixh
                            447 .macro xor__ixh
                            448    .dw #0xACDD  ;; Opcode for xor ixh
                            449 .endm
                            450 
                            451 ;; Macro: cp__ixh
                            452 ;;    Opcode for "CP IXH" instruction
                            453 ;; 
                            454 .mdelete cp__ixh
                            455 .macro cp__ixh
                            456    .dw #0xBCDD  ;; Opcode for cp ixh
                            457 .endm
                            458 
                            459 ;; Macro: dec__ixh
                            460 ;;    Opcode for "DEC IXH" instruction
                            461 ;; 
                            462 .mdelete dec__ixh
                            463 .macro dec__ixh
                            464    .dw #0x25DD  ;; Opcode for dec ixh
                            465 .endm
                            466 
                            467 ;; Macro: inc__ixh
                            468 ;;    Opcode for "INC IXH" instruction
                            469 ;; 
                            470 .mdelete inc__ixh
                            471 .macro inc__ixh
                            472    .dw #0x24DD  ;; Opcode for inc ixh
                            473 .endm
                            474 
                            475 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,
                            476 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,
                            477 ;; IYL Related Macros
                            478 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,
                            479 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,
                            480 
                            481 ;; Macro: ld__iyl    Value
                            482 ;;    Opcode for "LD iyl, Value" instruction
                            483 ;;  
                            484 ;; Parameters:
                            485 ;;    Value - An inmediate 8-bits value that will be loaded into iyl
                            486 ;; 
                            487 .mdelete  ld__iyl
                            488 .macro ld__iyl    Value 
                            489    .db #0xFD, #0x2E, Value  ;; Opcode for ld iyl, Value
                            490 .endm
                            491 
                            492 ;; Macro: ld__iyl_a
                            493 ;;    Opcode for "LD iyl, a" instruction
                            494 ;; 
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 43.
Hexadecimal [16-Bits]



                            495 .mdelete ld__iyl_a
                            496 .macro ld__iyl_a
                            497    .dw #0x6FFD  ;; Opcode for ld iyl, a
                            498 .endm
                            499 
                            500 ;; Macro: ld__iyl_b
                            501 ;;    Opcode for "LD iyl, B" instruction
                            502 ;; 
                            503 .mdelete ld__iyl_b
                            504 .macro ld__iyl_b
                            505    .dw #0x68FD  ;; Opcode for ld iyl, b
                            506 .endm
                            507 
                            508 ;; Macro: ld__iyl_c
                            509 ;;    Opcode for "LD iyl, C" instruction
                            510 ;; 
                            511 .mdelete ld__iyl_c
                            512 .macro ld__iyl_c
                            513    .dw #0x69FD  ;; Opcode for ld iyl, c
                            514 .endm
                            515 
                            516 ;; Macro: ld__iyl_d
                            517 ;;    Opcode for "LD iyl, D" instruction
                            518 ;; 
                            519 .mdelete ld__iyl_d
                            520 .macro ld__iyl_d
                            521    .dw #0x6AFD  ;; Opcode for ld iyl, d
                            522 .endm
                            523 
                            524 ;; Macro: ld__iyl_e
                            525 ;;    Opcode for "LD iyl, E" instruction
                            526 ;; 
                            527 .mdelete ld__iyl_e
                            528 .macro ld__iyl_e
                            529    .dw #0x6BFD  ;; Opcode for ld iyl, e
                            530 .endm
                            531 
                            532 ;; Macro: ld__iyl_iyh
                            533 ;;    Opcode for "LD iyl, IXL" instruction
                            534 ;; 
                            535 .mdelete  ld__iyl_iyh
                            536 .macro ld__iyl_iyh
                            537    .dw #0x6CFD  ;; Opcode for ld iyl, ixl
                            538 .endm
                            539 
                            540 ;; Macro: ld__a_iyl
                            541 ;;    Opcode for "LD A, iyl" instruction
                            542 ;; 
                            543 .mdelete ld__a_iyl
                            544 .macro ld__a_iyl
                            545    .dw #0x7DFD  ;; Opcode for ld a, iyl
                            546 .endm
                            547 
                            548 ;; Macro: ld__b_iyl
                            549 ;;    Opcode for "LD B, iyl" instruction
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 44.
Hexadecimal [16-Bits]



                            550 ;; 
                            551 .mdelete ld__b_iyl
                            552 .macro ld__b_iyl
                            553    .dw #0x45FD  ;; Opcode for ld b, iyl
                            554 .endm
                            555 
                            556 ;; Macro: ld__c_iyl
                            557 ;;    Opcode for "LD c, iyl" instruction
                            558 ;; 
                            559 .mdelete ld__c_iyl
                            560 .macro ld__c_iyl
                            561    .dw #0x4DFD  ;; Opcode for ld c, iyl
                            562 .endm
                            563 
                            564 ;; Macro: ld__d_iyl
                            565 ;;    Opcode for "LD D, iyl" instruction
                            566 ;; 
                            567 .mdelete ld__d_iyl
                            568 .macro ld__d_iyl
                            569    .dw #0x55FD  ;; Opcode for ld d, iyl
                            570 .endm
                            571 
                            572 ;; Macro: ld__e_iyl
                            573 ;;    Opcode for "LD e, iyl" instruction
                            574 ;; 
                            575 .mdelete ld__e_iyl
                            576 .macro ld__e_iyl
                            577    .dw #0x5DFD  ;; Opcode for ld e, iyl
                            578 .endm
                            579 
                            580 ;; Macro: add__iyl
                            581 ;;    Opcode for "Add iyl" instruction
                            582 ;; 
                            583 .mdelete add__iyl
                            584 .macro add__iyl
                            585    .dw #0x85FD  ;; Opcode for add iyl
                            586 .endm
                            587 
                            588 ;; Macro: sub__iyl
                            589 ;;    Opcode for "SUB iyl" instruction
                            590 ;; 
                            591 .mdelete sub__iyl
                            592 .macro sub__iyl
                            593    .dw #0x95FD  ;; Opcode for sub iyl
                            594 .endm
                            595 
                            596 ;; Macro: adc__iyl
                            597 ;;    Opcode for "ADC iyl" instruction
                            598 ;; 
                            599 .mdelete adc__iyl
                            600 .macro adc__iyl
                            601    .dw #0x8DFD  ;; Opcode for adc iyl
                            602 .endm
                            603 
                            604 ;; Macro: sbc__iyl
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 45.
Hexadecimal [16-Bits]



                            605 ;;    Opcode for "SBC iyl" instruction
                            606 ;; 
                            607 .mdelete sbc__iyl
                            608 .macro sbc__iyl
                            609    .dw #0x9DFD  ;; Opcode for sbc iyl
                            610 .endm
                            611 
                            612 ;; Macro: and__iyl
                            613 ;;    Opcode for "AND iyl" instruction
                            614 ;; 
                            615 .mdelete and__iyl
                            616 .macro and__iyl
                            617    .dw #0xA5FD  ;; Opcode for and iyl
                            618 .endm
                            619 
                            620 ;; Macro: or__iyl
                            621 ;;    Opcode for "OR iyl" instruction
                            622 ;; 
                            623 .mdelete or__iyl
                            624 .macro or__iyl
                            625    .dw #0xB5FD  ;; Opcode for or iyl
                            626 .endm
                            627 
                            628 ;; Macro: xor__iyl
                            629 ;;    Opcode for "XOR iyl" instruction
                            630 ;; 
                            631 .mdelete xor__iyl
                            632 .macro xor__iyl
                            633    .dw #0xADFD  ;; Opcode for xor iyl
                            634 .endm
                            635 
                            636 ;; Macro: cp__iyl
                            637 ;;    Opcode for "CP iyl" instruction
                            638 ;; 
                            639 .mdelete cp__iyl
                            640 .macro cp__iyl
                            641    .dw #0xBDFD  ;; Opcode for cp iyl
                            642 .endm
                            643 
                            644 ;; Macro: dec__iyl
                            645 ;;    Opcode for "DEC iyl" instruction
                            646 ;; 
                            647 .mdelete dec__iyl
                            648 .macro dec__iyl
                            649    .dw #0x2DFD  ;; Opcode for dec iyl
                            650 .endm
                            651 
                            652 ;; Macro: inc__iyl
                            653 ;;    Opcode for "INC iyl" instruction
                            654 ;; 
                            655 .mdelete inc__iyl
                            656 .macro inc__iyl
                            657    .dw #0x2CFD  ;; Opcode for inc iyl
                            658 .endm
                            659 
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 46.
Hexadecimal [16-Bits]



                            660 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,
                            661 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,
                            662 ;; IYH Related Macros
                            663 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,
                            664 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,
                            665 
                            666 ;; Macro: ld__iyh    Value
                            667 ;;    Opcode for "LD iyh, Value" instruction
                            668 ;;  
                            669 ;; Parameters:
                            670 ;;    Value - An inmediate 8-bits value that will be loaded into iyh
                            671 ;; 
                            672 .mdelete  ld__iyh
                            673 .macro ld__iyh    Value 
                            674    .db #0xFD, #0x26, Value  ;; Opcode for ld iyh, Value
                            675 .endm
                            676 
                            677 ;; Macro: ld__iyh_a
                            678 ;;    Opcode for "LD iyh, a" instruction
                            679 ;; 
                            680 .mdelete ld__iyh_a
                            681 .macro ld__iyh_a
                            682    .dw #0x67FD  ;; Opcode for ld iyh, a
                            683 .endm
                            684 
                            685 ;; Macro: ld__iyh_b
                            686 ;;    Opcode for "LD iyh, B" instruction
                            687 ;; 
                            688 .mdelete ld__iyh_b
                            689 .macro ld__iyh_b
                            690    .dw #0x60FD  ;; Opcode for ld iyh, b
                            691 .endm
                            692 
                            693 ;; Macro: ld__iyh_c
                            694 ;;    Opcode for "LD iyh, C" instruction
                            695 ;; 
                            696 .mdelete ld__iyh_c
                            697 .macro ld__iyh_c
                            698    .dw #0x61FD  ;; Opcode for ld iyh, c
                            699 .endm
                            700 
                            701 ;; Macro: ld__iyh_d
                            702 ;;    Opcode for "LD iyh, D" instruction
                            703 ;; 
                            704 .mdelete ld__iyh_d
                            705 .macro ld__iyh_d
                            706    .dw #0x62FD  ;; Opcode for ld iyh, d
                            707 .endm
                            708 
                            709 ;; Macro: ld__iyh_e
                            710 ;;    Opcode for "LD iyh, E" instruction
                            711 ;; 
                            712 .mdelete ld__iyh_e
                            713 .macro ld__iyh_e
                            714    .dw #0x63FD  ;; Opcode for ld iyh, e
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 47.
Hexadecimal [16-Bits]



                            715 .endm
                            716 
                            717 ;; Macro: ld__iyh_iyl
                            718 ;;    Opcode for "LD iyh, IyL" instruction
                            719 ;; 
                            720 .mdelete  ld__iyh_iyl
                            721 .macro ld__iyh_iyl
                            722    .dw #0x65FD  ;; Opcode for ld iyh, iyl
                            723 .endm
                            724 
                            725 ;; Macro: ld__a_iyh
                            726 ;;    Opcode for "LD A, iyh" instruction
                            727 ;; 
                            728 .mdelete ld__a_iyh
                            729 .macro ld__a_iyh
                            730    .dw #0x7CFD  ;; Opcode for ld a, iyh
                            731 .endm
                            732 
                            733 ;; Macro: ld__b_iyh
                            734 ;;    Opcode for "LD B, iyh" instruction
                            735 ;; 
                            736 .mdelete ld__b_iyh
                            737 .macro ld__b_iyh
                            738    .dw #0x44FD  ;; Opcode for ld b, iyh
                            739 .endm
                            740 
                            741 ;; Macro: ld__c_iyh
                            742 ;;    Opcode for "LD c, iyh" instruction
                            743 ;; 
                            744 .mdelete ld__c_iyh
                            745 .macro ld__c_iyh
                            746    .dw #0x4CFD  ;; Opcode for ld c, iyh
                            747 .endm
                            748 
                            749 ;; Macro: ld__d_iyh
                            750 ;;    Opcode for "LD D, iyh" instruction
                            751 ;; 
                            752 .mdelete ld__d_iyh
                            753 .macro ld__d_iyh
                            754    .dw #0x54FD  ;; Opcode for ld d, iyh
                            755 .endm
                            756 
                            757 ;; Macro: ld__e_iyh
                            758 ;;    Opcode for "LD e, iyh" instruction
                            759 ;; 
                            760 .mdelete ld__e_iyh
                            761 .macro ld__e_iyh
                            762    .dw #0x5CFD  ;; Opcode for ld e, iyh
                            763 .endm
                            764 
                            765 ;; Macro: add__iyh
                            766 ;;    Opcode for "Add iyh" instruction
                            767 ;; 
                            768 .mdelete add__iyh
                            769 .macro add__iyh
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 48.
Hexadecimal [16-Bits]



                            770    .dw #0x84FD  ;; Opcode for add iyh
                            771 .endm
                            772 
                            773 ;; Macro: sub__iyh
                            774 ;;    Opcode for "SUB iyh" instruction
                            775 ;; 
                            776 .mdelete sub__iyh
                            777 .macro sub__iyh
                            778    .dw #0x94FD  ;; Opcode for sub iyh
                            779 .endm
                            780 
                            781 ;; Macro: adc__iyh
                            782 ;;    Opcode for "ADC iyh" instruction
                            783 ;; 
                            784 .mdelete adc__iyh
                            785 .macro adc__iyh
                            786    .dw #0x8CFD  ;; Opcode for adc iyh
                            787 .endm
                            788 
                            789 ;; Macro: sbc__iyh
                            790 ;;    Opcode for "SBC iyh" instruction
                            791 ;; 
                            792 .mdelete sbc__iyh
                            793 .macro sbc__iyh
                            794    .dw #0x9CFD  ;; Opcode for sbc iyh
                            795 .endm
                            796 
                            797 ;; Macro: and__iyh
                            798 ;;    Opcode for "AND iyh" instruction
                            799 ;; 
                            800 .mdelete and__iyh
                            801 .macro and__iyh
                            802    .dw #0xA4FD  ;; Opcode for and iyh
                            803 .endm
                            804 
                            805 ;; Macro: or__iyh
                            806 ;;    Opcode for "OR iyh" instruction
                            807 ;; 
                            808 .mdelete or__iyh
                            809 .macro or__iyh
                            810    .dw #0xB4FD  ;; Opcode for or iyh
                            811 .endm
                            812 
                            813 ;; Macro: xor__iyh
                            814 ;;    Opcode for "XOR iyh" instruction
                            815 ;; 
                            816 .mdelete xor__iyh
                            817 .macro xor__iyh
                            818    .dw #0xACFD  ;; Opcode for xor iyh
                            819 .endm
                            820 
                            821 ;; Macro: cp__iyh
                            822 ;;    Opcode for "CP iyh" instruction
                            823 ;; 
                            824 .mdelete cp__iyh
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 49.
Hexadecimal [16-Bits]



                            825 .macro cp__iyh
                            826    .dw #0xBCFD  ;; Opcode for cp iyh
                            827 .endm
                            828 
                            829 ;; Macro: dec__iyh
                            830 ;;    Opcode for "DEC iyh" instruction
                            831 ;; 
                            832 .mdelete dec__iyh
                            833 .macro dec__iyh
                            834    .dw #0x25FD  ;; Opcode for dec iyh
                            835 .endm
                            836 
                            837 ;; Macro: inc__iyh
                            838 ;;    Opcode for "INC iyh" instruction
                            839 ;; 
                            840 .mdelete inc__iyh
                            841 .macro inc__iyh
                            842    .dw #0x24FD  ;; Opcode for inc iyh
                            843 .endm
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 50.
Hexadecimal [16-Bits]



                             27 
                             28 ;; Macro: ld__hl_de
                             29 ;;    Copy DE to HL, using 2 instructions
                             30 ;; COST: 2 us (8 CPU Cycles)
                             31 ;; 
                             32 .macro ld__hl_de
                             33    ;; LD HL, DE
                             34    ;;------------
                             35    ld h, d
                             36    ld l, e
                             37    ;;------------
                             38 .endm
                             39 
                             40 ;; Macro: ld__de_hl
                             41 ;;    Copy HL to DE, using 2 instructions (ld d, h : ld e, l)
                             42 ;; COST: 2 us (8 CPU Cycles)
                             43 ;; 
                             44 .macro ld__de_hl
                             45    ;; LD DE, HL
                             46    ;;------------
                             47    ld d, h
                             48    ld e, l
                             49    ;;------------
                             50 .endm
                             51 
                             52 ;; Macro: ld__de_ix
                             53 ;;    Copy IX to DE, using 2 instructions (ld e, ixl : ld d, ixh)
                             54 ;; COST: 4 us (16 CPU Cycles)
                             55 ;; 
                             56 .macro ld__de_ix
                             57    ;; LD DE, IX
                             58    ;;------------
                             59    ld__e_ixl
                             60    ld__d_ixh
                             61    ;;------------
                             62 .endm
                             63 
                             64 ;; Macro: ld__bc_ix
                             65 ;;    Copy IX to BC, using 2 instructions (ld c, ixl : ld b, ixh)
                             66 ;; COST: 4 us (16 CPU Cycles)
                             67 ;; 
                             68 .macro ld__bc_ix
                             69    ;; LD BC, IX
                             70    ;;------------
                             71    ld__c_ixl
                             72    ld__b_ixh
                             73    ;;------------
                             74 .endm
                             75 
                             76 ;; Macro: ld__hl_ix
                             77 ;;    Copy IX to HL, using 4 instructions. 
                             78 ;;    Modifies A Register
                             79 ;; COST: 6 us (24 CPU Cycles)
                             80 ;; 
                             81 .macro ld__hl_ix
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 51.
Hexadecimal [16-Bits]



                             82    ;; LD HL, IX
                             83    ;;------------
                             84    ld__a_ixl
                             85    ld  l, a
                             86    ld__a_ixh
                             87    ld  h, a
                             88    ;;------------
                             89 .endm
                             90 
                             91 ;; Macro: ld__ix_de
                             92 ;;    Copy DE to IX, using 2 instructions (ld ixl, e : ld ixh, d)
                             93 ;; COST: 4 us (16 CPU Cycles)
                             94 ;; 
                             95 .macro ld__ix_de
                             96    ;; LD IX, DE
                             97    ;;------------
                             98    ld__ixl_e
                             99    ld__ixh_d
                            100    ;;------------
                            101 .endm
                            102 
                            103 ;; Macro: ld__ix_bc
                            104 ;;    Copy BX to IX, using 2 instructions (ld ixl, c : ld ixh, b)
                            105 ;; COST: 4 us (16 CPU Cycles)
                            106 ;; 
                            107 .macro ld__ix_bc
                            108    ;; LD IX, BC
                            109    ;;------------
                            110    ld__ixl_c
                            111    ld__ixh_b
                            112    ;;------------
                            113 .endm
                            114 
                            115 ;; Macro: ld__ix_hl
                            116 ;;    Copy HL to IX, using 4 instructions. 
                            117 ;;    Modifies A Register
                            118 ;; COST: 6 us (24 CPU Cycles)
                            119 ;; 
                            120 .macro ld__ix_hl
                            121    ;; LD IX, HL
                            122    ;;------------
                            123    ld  a, l
                            124    ld__ixl_a
                            125    ld  a, h
                            126    ld__ixh_a
                            127    ;;------------
                            128 .endm
                            129 
                            130 ;; Macro: ld__de_iy
                            131 ;;    Copy IY to DE, using 2 instructions (ld e, iyl : ld d, iyh)
                            132 ;; COST: 4 us (16 CPU Cycles)
                            133 ;; 
                            134 .macro ld__de_iy
                            135    ;; LD DE, IY
                            136    ;;------------
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 52.
Hexadecimal [16-Bits]



                            137    ld__e_iyl
                            138    ld__d_iyh
                            139    ;;------------
                            140 .endm
                            141 
                            142 ;; Macro: ld__bc_iy
                            143 ;;    Copy IY to BC, using 2 instructions (ld c, iyl : ld b, iyh)
                            144 ;; COST: 4 us (16 CPU Cycles)
                            145 ;; 
                            146 .macro ld__bc_iy
                            147    ;; LD BC, IY
                            148    ;;------------
                            149    ld__c_iyl
                            150    ld__b_iyh
                            151    ;;------------
                            152 .endm
                            153 
                            154 ;; Macro: ld__hl_iy
                            155 ;;    Copy IY to HL, using 4 instructions. 
                            156 ;;    Modifies A Register
                            157 ;; COST: 6 us (24 CPU Cycles)
                            158 ;; 
                            159 .macro ld__hl_iy
                            160    ;; LD HL, IY
                            161    ;;------------
                            162    ld__a_iyl
                            163    ld  l, a
                            164    ld__a_iyh
                            165    ld  h, a
                            166    ;;------------
                            167 .endm
                            168 
                            169 ;; Macro: ld__iy_de
                            170 ;;    Copy DE to IY, using 2 instructions (ld iyl, e : ld iyh, d)
                            171 ;; COST: 4 us (16 CPU Cycles)
                            172 ;; 
                            173 .macro ld__iy_de
                            174    ;; LD IY, DE
                            175    ;;------------
                            176    ld__iyl_e
                            177    ld__iyh_d
                            178    ;;------------
                            179 .endm
                            180 
                            181 ;; Macro: ld__iy_bc
                            182 ;;    Copy BX to IY, using 2 instructions (ld iyl, c : ld iyh, b)
                            183 ;; COST: 4 us (16 CPU Cycles)
                            184 ;; 
                            185 .macro ld__iy_bc
                            186    ;; LD IY, BC
                            187    ;;------------
                            188    ld__iyl_c
                            189    ld__iyh_b
                            190    ;;------------
                            191 .endm
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 53.
Hexadecimal [16-Bits]



                            192 
                            193 ;; Macro: ld__iy_hl
                            194 ;;    Copy HL to IY, using 4 instructions. 
                            195 ;;    Modifies A Register
                            196 ;; COST: 6 us (24 CPU Cycles)
                            197 ;; 
                            198 .macro ld__iy_hl
                            199    ;; LD IY, HL
                            200    ;;------------
                            201    ld  a, l
                            202    ld__iyl_a
                            203    ld  a, h
                            204    ld__iyh_a
                            205    ;;------------
                            206 .endm
                            207 
                            208 ;; Macro: ld__ix_iy
                            209 ;;    Copy IY to IX, using 4 instructions. 
                            210 ;;    Modifies A Register
                            211 ;; Cost: 8 us (32 CPU Cycles)
                            212 ;; 
                            213 .macro ld__ix_iy
                            214    ;; LD IX, IY
                            215    ;;------------
                            216    ld__a_iyl
                            217    ld__ixl_a
                            218    ld__a_iyh
                            219    ld__ixh_a
                            220    ;;------------
                            221 .endm
                            222 
                            223 ;; Macro: ld__iy_ix
                            224 ;;    Copy IX to IY, using 4 instructions. 
                            225 ;;    Modifies A Register
                            226 ;; Cost: 8 us (32 CPU Cycles)
                            227 ;; 
                            228 .macro ld__iy_ix
                            229    ;; LD IY, IX
                            230    ;;------------
                            231    ld__a_ixl
                            232    ld__iyl_a
                            233    ld__a_ixh
                            234    ld__iyh_a
                            235    ;;------------
                            236 .endm
                            237 
                            238 ;; Macro: ex__de_ix
                            239 ;;    Swap DE with IX
                            240 ;;    Modifies A Register
                            241 ;; Cost: 10 us (40 CPU Cycles)
                            242 ;; 
                            243 .macro ex__de_ix
                            244    ;; EX DE, IX
                            245    ;;------------
                            246    ld a, e
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 54.
Hexadecimal [16-Bits]



                            247    ld__e_ixl
                            248    ld__ixl_a
                            249    ld a, d
                            250    ld__d_ixh
                            251    ld__ixh_a
                            252    ;;------------
                            253 .endm
                            254 
                            255 ;; Macro: ex__bc_ix
                            256 ;;    Swap BC with IX
                            257 ;;    Modifies A Register
                            258 ;; Cost: 10 us (40 CPU Cycles)
                            259 ;; 
                            260 .macro ex__bc_ix
                            261    ;; EX BC, IX
                            262    ;;------------
                            263    ld a, c
                            264    ld__c_ixl
                            265    ld__ixl_a
                            266    ld a, b
                            267    ld__b_ixh
                            268    ld__ixh_a
                            269    ;;------------
                            270 .endm
                            271 
                            272 ;; Macro: ex__hl_ix
                            273 ;;    Swap HL with IX
                            274 ;;    Uses 2 bytes on the stack for the swap
                            275 ;;    Modifies A register
                            276 ;; Cost: 15 us (60 CPU Cycles)
                            277 ;; 
                            278 .macro ex__hl_ix
                            279    ;; EX HL, IX
                            280    ;;------------
                            281    push  hl
                            282    ld__a_ixl
                            283    ld l, a
                            284    ld__a_ixh
                            285    ld h, a
                            286    pop   ix
                            287    ;;------------
                            288 .endm
                            289 
                            290 ;; Macro: ex__de_iy
                            291 ;;    Swap DE with IY
                            292 ;;    Modifies A Register
                            293 ;; Cost: 10 us (40 CPU Cycles)
                            294 ;; 
                            295 .macro ex__de_iy
                            296    ;; EX DE, IY
                            297    ;;------------
                            298    ld a, e
                            299    ld__e_iyl
                            300    ld__iyl_a
                            301    ld a, d
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 55.
Hexadecimal [16-Bits]



                            302    ld__d_iyh
                            303    ld__iyh_a
                            304    ;;------------
                            305 .endm
                            306 
                            307 ;; Macro: ex__bc_iy
                            308 ;;    Swap BC with IY
                            309 ;;    Modifies A Register
                            310 ;; Cost: 10 us (40 CPU Cycles)
                            311 ;; 
                            312 .macro ex__bc_iy
                            313    ;; EX BC, IY
                            314    ;;------------
                            315    ld a, c
                            316    ld__c_iyl
                            317    ld__iyl_a
                            318    ld a, b
                            319    ld__b_iyh
                            320    ld__iyh_a
                            321    ;;------------
                            322 .endm
                            323 
                            324 ;; Macro: ex__hl_iy
                            325 ;;    Swap HL with IY
                            326 ;;    Uses 2 bytes on the stack for the swap
                            327 ;;    Modifies A register
                            328 ;; Cost: 15 us (60 CPU Cycles)
                            329 ;; 
                            330 .macro ex__hl_iy
                            331    ;; EX HL, IY
                            332    ;;------------
                            333    push  hl
                            334    ld__a_iyl
                            335    ld l, a
                            336    ld__a_iyh
                            337    ld h, a
                            338    pop   iy
                            339    ;;------------
                            340 .endm
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 56.
Hexadecimal [16-Bits]



                             24 .include "macros/cpct_pushpop.h.s"
                              1 ;;-----------------------------LICENSE NOTICE------------------------------------
                              2 ;;  This file is part of CPCtelera: An Amstrad CPC Game Engine 
                              3 ;;  Copyright (C) 2020 ronaldo / Fremos / Cheesetea / ByteRealms (@FranGallegoBR)
                              4 ;;
                              5 ;;  This program is free software: you can redistribute it and/or modify
                              6 ;;  it under the terms of the GNU Lesser General Public License as published by
                              7 ;;  the Free Software Foundation, either version 3 of the License, or
                              8 ;;  (at your option) any later version.
                              9 ;;
                             10 ;;  This program is distributed in the hope that it will be useful,
                             11 ;;  but WITHOUT ANY WARRANTY; without even the implied warranty of
                             12 ;;  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
                             13 ;;  GNU Lesser General Public License for more details.
                             14 ;;
                             15 ;;  You should have received a copy of the GNU Lesser General Public License
                             16 ;;  along with this program.  If not, see <http://www.gnu.org/licenses/>.
                             17 ;;-------------------------------------------------------------------------------
                             18 
                             19 ;;
                             20 ;; File: Push - Pop Macros
                             21 ;;
                             22 ;;    Useful macros to simplify push-pop save/restore operations
                             23 ;;
                             24 
                             25 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                             26 ;; Macro: cpctm_push RO, R1, R2, R3, R4, R5
                             27 ;;
                             28 ;;    Pushes any given registers (up to 6) into the stack
                             29 ;;
                             30 ;; ASM Definition:
                             31 ;;    .macro <cpctm_push> R0, R1, R2, R3, R4, R5
                             32 ;;
                             33 ;; Parameters:
                             34 ;;    R0-R5 - Any number of 16-bit pushable registers, up to 6
                             35 ;;
                             36 ;; Details:
                             37 ;;    This macro converts the list of 16-bit registers given as parameters into a list
                             38 ;; of 'push' operations to push all of them into the stack. The registers are pushed
                             39 ;; into the stack in the same order as they are given in the parameter list.
                             40 ;;    The macro accepts any number of registers up to the maximum of 6 that are 
                             41 ;; predefined as parameters. However, you may use it with 1, 2, 3, 4 or 5 registers
                             42 ;; as parameters. There is no need to give the 6 parameters: only those given will 
                             43 ;; be considered.
                             44 ;;
                             45 ;; Modified Registers: 
                             46 ;;    none
                             47 ;;
                             48 ;; Required memory:
                             49 ;;    1 byte per register given (2 if they are IX or IY)
                             50 ;;
                             51 ;; Time Measures:
                             52 ;; (start code)
                             53 ;;  Case     | microSecs(us) | CPU Cycles
                             54 ;; ------------------------------------
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 57.
Hexadecimal [16-Bits]



                             55 ;;  Per Reg  |       4       |     16
                             56 ;; ------------------------------------
                             57 ;;  Per IX/IY|       5       |     20
                             58 ;; ------------------------------------
                             59 ;; (end code)
                             60 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                             61 .macro cpctm_push r0, r1, r2, r3, r4, r5
                             62    .narg v
                             63    .if v
                             64    push r0
                             65    .if v-1
                             66    push r1
                             67    .if v-2
                             68    push r2
                             69    .if v-3
                             70    push r3
                             71    .if v-4
                             72    push r4
                             73    .if v-5
                             74    push r5
                             75    .else
                             76    .mexit
                             77    .endif
                             78    .else
                             79    .mexit
                             80    .endif
                             81    .else
                             82    .mexit
                             83    .endif
                             84    .else
                             85    .mexit
                             86    .endif
                             87    .else
                             88    .mexit
                             89    .endif
                             90    .else
                             91    .mexit
                             92    .endif
                             93 .endm
                             94 
                             95 
                             96 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                             97 ;; Macro: cpctm_pop RO, R1, R2, R3, R4, R5
                             98 ;;
                             99 ;;    Pops any given registers (up to 6) from the stack
                            100 ;;
                            101 ;; ASM Definition:
                            102 ;;    .macro <cpctm_pop> R0, R1, R2, R3, R4, R5
                            103 ;;
                            104 ;; Parameters:
                            105 ;;    R0-R5 - Any number of 16-bit pushable/popable registers, up to 6
                            106 ;;
                            107 ;; Details:
                            108 ;;    This macro converts the list of 16-bit registers given as parameters into a list
                            109 ;; of 'pop' operations to pop all of them from the stack. The registers are poped
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 58.
Hexadecimal [16-Bits]



                            110 ;; in the same order as they are given in the parameter list.
                            111 ;;    The macro accepts any number of registers up to the maximum of 6 that are 
                            112 ;; predefined as parameters. However, you may use it with 1, 2, 3, 4 or 5 registers
                            113 ;; as parameters. There is no need to give the 6 parameters: only those given will 
                            114 ;; be considered.
                            115 ;;
                            116 ;; Modified Registers: 
                            117 ;;    R0, R1, R2, R3, R4, R5 (Those given as parameters are loaded from the stack)
                            118 ;;
                            119 ;; Required memory:
                            120 ;;    1 byte per register given (2 if they are IX or IY)
                            121 ;;
                            122 ;; Time Measures:
                            123 ;; (start code)
                            124 ;;  Case     | microSecs(us) | CPU Cycles
                            125 ;; ------------------------------------
                            126 ;;  Per Reg  |       3       |     12
                            127 ;; ------------------------------------
                            128 ;;  Per IX/IY|       5       |     20
                            129 ;; ------------------------------------
                            130 ;; (end code)
                            131 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                            132 .macro cpctm_pop r0, r1, r2, r3, r4, r5
                            133    .narg v
                            134    .if v
                            135    pop r0
                            136    .if v-1
                            137    pop r1
                            138    .if v-2
                            139    pop r2
                            140    .if v-3
                            141    pop r3
                            142    .if v-4
                            143    pop r4
                            144    .if v-5
                            145    pop r5
                            146    .else
                            147    .mexit
                            148    .endif
                            149    .else
                            150    .mexit
                            151    .endif
                            152    .else
                            153    .mexit
                            154    .endif
                            155    .else
                            156    .mexit
                            157    .endif
                            158    .else
                            159    .mexit
                            160    .endif
                            161    .else
                            162    .mexit
                            163    .endif
                            164 .endm
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 59.
Hexadecimal [16-Bits]



                             25 .include "macros/cpct_luts.h.s"
                              1 ;;-----------------------------LICENSE NOTICE------------------------------------
                              2 ;;  This file is part of CPCtelera: An Amstrad CPC Game Engine 
                              3 ;;  Copyright (C) 2018 ronaldo / Fremos / Cheesetea / ByteRealms (@FranGallegoBR)
                              4 ;;
                              5 ;;  This program is free software: you can redistribute it and/or modify
                              6 ;;  it under the terms of the GNU Lesser General Public License as published by
                              7 ;;  the Free Software Foundation, either version 3 of the License, or
                              8 ;;  (at your option) any later version.
                              9 ;;
                             10 ;;  This program is distributed in the hope that it will be useful,
                             11 ;;  but WITHOUT ANY WARRANTY; without even the implied warranty of
                             12 ;;  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
                             13 ;;  GNU Lesser General Public License for more details.
                             14 ;;
                             15 ;;  You should have received a copy of the GNU Lesser General Public License
                             16 ;;  along with this program.  If not, see <http://www.gnu.org/licenses/>.
                             17 ;;-------------------------------------------------------------------------------
                             18 
                             19 ;;
                             20 ;; File: LUTs (Look-Up-Tables)
                             21 ;;
                             22 ;;    Useful macros for accessing and managing Look-Up-Tables
                             23 ;;
                             24 
                             25 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                             26 ;; Macro: cpctm_lutget8
                             27 ;;
                             28 ;;    Gets a value from a 256-byte-max 8-bit table into A register
                             29 ;;
                             30 ;; Parameters:
                             31 ;;    Table         - Memory address where the 256-byte-max table starts. It can be 
                             32 ;;  either an hexadecimal, decimal or octal address, or a symbol (the table name).
                             33 ;;    TR1           - An 8-bits register from the set {B, D, H}
                             34 ;;    TR2           - An 8-bits register from the set {C, E, L}. This register must
                             35 ;;  match TR1 to form a valid 16-bits register (BC, DE or HL), as the register TR1'TR2
                             36 ;;  will be loaded with the address of the table, to be the base pointer.
                             37 ;; 
                             38 ;; Input Registers: 
                             39 ;;    A     - Index in the LUT to be accessed.
                             40 ;;
                             41 ;; Return Value:
                             42 ;;    A     - Value got from the LUT ( table[TR1'TR2 + A] )
                             43 ;;
                             44 ;; Details:
                             45 ;;    This macro gets a value from a table into the A register. The process is simple:
                             46 ;;
                             47 ;;    1. It loads the address of the table in the 16-bits register TR1'TR2
                             48 ;;    2. It adds the index (A) to TR1'TR2  (TR1'TR2 += A)
                             49 ;;    3. It loads into A register the byte pointed by TR1'TR2
                             50 ;;
                             51 ;; Modified Registers: 
                             52 ;;    AF, TR1, TR2
                             53 ;;
                             54 ;; Required memory:
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 60.
Hexadecimal [16-Bits]



                             55 ;;    9 bytes
                             56 ;;
                             57 ;; Time Measures:
                             58 ;; (start code)
                             59 ;;  Case | microSecs(us) | CPU Cycles
                             60 ;; ------------------------------------
                             61 ;;  Any  |      10       |     40
                             62 ;; ------------------------------------
                             63 ;; (end code)
                             64 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                             65 
                             66 .macro cpctm_lutget8 Table, TR1, TR2
                             67     ld   TR1'TR2, #Table   ;; [3] TR1_TR2 points to the LUT
                             68     
                             69     ;; Compute TR1'TR2 += A
                             70     add  TR2               ;; [1] | TR2 += A
                             71     ld   TR2, a            ;; [1] |
                             72     sub  a                 ;; [1] A = 0 (preserving Carry Flag)
                             73     adc  TR1               ;; [1] | TR1 += Carry
                             74     ld   TR1, a            ;; [1] |
                             75 
                             76     ;; A = *(TR1_TR2 + A)
                             77     ld   a, (TR1'TR2)      ;; [2] A = Value stored at given index from the LUT 
                             78 .endm
                             79 
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 61.
Hexadecimal [16-Bits]



                             26 
                             27 ;;//////////////////////////////////////////////////////////////////////
                             28 ;; Group: General Useful Macros
                             29 ;;//////////////////////////////////////////////////////////////////////
                             30 
                             31 ;;
                             32 ;; Macro: cpctm_produceHalts_asm
                             33 ;;
                             34 ;;   Produce a set of consecutive halt instructions in order to wait for 
                             35 ;; a given number of interrupts.
                             36 ;;
                             37 ;; C Definition:
                             38 ;;   .macro <cpctm_produceHalts_asm> *N*
                             39 ;;
                             40 ;; Input Parameters:
                             41 ;;   (_) N - Number of consecutive halts to be produced
                             42 ;;
                             43 ;; Known issues:
                             44 ;;    * *N* must be a constant expression that can evaluate to a number
                             45 ;; at compile time.
                             46 ;;    * If the code generated by this macro is executed with interrupts
                             47 ;; being disabled, your CPU will effectively hang forever.
                             48 ;;    * This macro can only be used from assembler code. For C callings
                             49 ;; use <cpctm_produceHalts> instead.
                             50 ;;
                             51 ;; Size of generated code:
                             52 ;;    * *N* bytes (1 byte each halt instruction produced)
                             53 ;;
                             54 ;; Time Measures:
                             55 ;;    * Time depends on the exact moment of execution and the status of
                             56 ;; interrupts. *N* interrupts will pass.
                             57 ;;
                             58 ;; Details:
                             59 ;;    This macro produces a set of *N* consecutive *halt* assembly 
                             60 ;; instructions. Each *halt* instruction stops de Z80 CPU until 
                             61 ;; an interrupt is received. Therefore, this waits for *N* interrupts
                             62 ;; to be produced. This can be used for waiting or synchronization 
                             63 ;; purposes.
                             64 ;;
                             65 ;;    Please, take into account that this is a macro, and not a function.
                             66 ;; Each time this macro is used in your code it will produce the requested
                             67 ;; amount of halts. That can produce more code than you effectively need.
                             68 ;; For a unique function that controls a loop of *halt* waiting use
                             69 ;; <cpct_waitHalts> instead.
                             70 ;;
                             71 ;;
                             72 .mdelete cpctm_produceHalts
                             73 .macro cpctm_produceHalts N
                             74    .rept N
                             75       halt
                             76    .endm
                             77 .endm
                             78 
                             79 ;;
                             80 ;; macro: cpctm_WINAPE_BRK
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 62.
Hexadecimal [16-Bits]



                             81 ;;
                             82 ;;    Used to insert the values 0xED 0xFF in the binary code, that 
                             83 ;; represent a Break Instruction in WinAPE. This is useful to
                             84 ;; easily include Breakpoints in the code for debugging purposes.
                             85 ;;
                             86 .macro cpctm_WINAPE_BRK
                             87    .db 0xED, 0xFF    ;; WinAPE Breakpoint Instruction
                             88 .endm
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 63.
Hexadecimal [16-Bits]



                             77 
                             78 ;; Symbols with the names of the CPCtelera functions we want to use
                             79 ;; must be declared globl to be recognized by the compiler. Later on,
                             80 ;; linker will do its job and make the calls go to function code.
                             81 .globl cpct_disableFirmware_asm
                             82 .globl cpct_setVideoMode_asm
                             83 .globl cpct_setPalette_asm
                             84 .globl cpct_setPALColour_asm
                             85 .globl cpct_getScreenPtr_asm
                             86 .globl cpct_drawSprite_asm
                             87 .globl cpct_waitVSYNC_asm
                             88 .globl cpct_drawStringM0_asm
                             89 .globl cpct_setDrawCharM0_asm
                             90 .globl cpct_akp_musicInit_asm
                             91 .globl cpct_akp_musicPlay_asm
                             92 .globl cpct_setInterruptHandler_asm
                             93 
   5771                      94 interrupt_handler:
                             95    ;; Update interrupt counter variable (iscount)
   5771 21 7E 62      [10]   96    ld   hl, #iscount          ;; HL points to interrupt counter variable (iscount)
   5774 35            [11]   97    dec (hl)                   ;; --iscount
   5775 C0            [11]   98    ret  nz                    ;; Do not play music if iscount != 0 (so, return)
                             99 
                            100    ;; Play music
   5776 36 06         [10]  101    ld    (hl), #itmusiccycles    ;; Restore interrupt counter variable intial value
   5778 CD 01 5A      [17]  102    call  cpct_akp_musicPlay_asm  ;; Play the music
                            103 
   577B C9            [10]  104    ret                           ;; Return
                            105 
                            106 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                            107 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                            108 ;; FUNC: init
                            109 ;;    Sets CPC to its initial status
                            110 ;; DESTROYS:
                            111 ;;    AF, BC, DE, HL
                            112 ;;
   577C                     113 init:
                            114    ;; Disable Firmware
   577C CD 28 62      [17]  115    call  cpct_disableFirmware_asm   ;; Disable firmware
                            116 
                            117    ;; Set Mode 0
   577F 0E 00         [ 7]  118    ld    c, #0                      ;; C = 0 (New video mode)
   5781 CD EA 59      [17]  119    call  cpct_setVideoMode_asm      ;; Set Mode 0
                            120    
                            121    ;; Set Palette
   5784 21 00 40      [10]  122    ld    hl, #_g_palette            ;; HL = pointer to the start of the palette array
   5787 11 10 00      [10]  123    ld    de, #palete_size           ;; DE = Size of the palette array (num of colours)
   578A CD A3 58      [17]  124    call  cpct_setPalette_asm        ;; Set the new palette
                            125 
                            126    ;; Change border colour
   578D 21 10 1F      [10]  127    ld    hl, #border_colour         ;; L=Border colour value, H=Palette Colour to be set (Border=16)
   5790 CD B6 58      [17]  128    call  cpct_setPALColour_asm      ;; Set the border (colour 16)
                            129 
                            130    ;; Initialize music
   5793 11 41 2A      [10]  131    ld    de, #_g_music              ;; DE points to the start of the song to be initialized
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 64.
Hexadecimal [16-Bits]



   5796 CD 0B 61      [17]  132    call  cpct_akp_musicInit_asm     ;; Initalize arkos tracker player with the song pointed by DE
                            133 
                            134    ;; 
   5799 21 71 57      [10]  135    ld    hl, #interrupt_handler       ;; HL points to the interrupt handler routine
   579C CD 7C 58      [17]  136    call  cpct_setInterruptHandler_asm ;; Set the new interrupt handler routine
                            137 
   579F C9            [10]  138    ret                              ;; return
                            139 
                            140 
                            141 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                            142 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                            143 ;; FUNC: drawSpriteClipped
                            144 ;;    Draw sprite with down clippling
                            145 ;; INPUT:
                            146 ;;    B: y pixel coordinate where to draw the sprite
                            147 ;;    C: x pixel coordinate where to draw the sprite
                            148 ;; DESTROYS:
                            149 ;;    AF, BC, DE, HL
                            150 ;;
   57A0                     151 drawSpriteClipped:
                            152    ;; Calculate the memory location where the sprite will be drawn
   57A0 C5            [11]  153    push  bc                      ;; save x,y coordinates passed as parameters
   57A1 11 00 C0      [10]  154    ld    de, #pvideomem          ;; DE points to the start of video memory
   57A4 CD 5C 62      [17]  155    call  cpct_getScreenPtr_asm   ;; Return pointer to byte located at (x,y) (C, B) in HL
   57A7 EB            [ 4]  156    ex    de, hl                  ;; DE = pointer to video memory location to draw the sprite
   57A8 F1            [10]  157    pop   af                      ;; A = y coordinate
                            158 
                            159    ;; Check if clipping is needed
   57A9 01 2D 85      [10]  160    ld    bc, #sprite_HxW         ;; WidthxHeight of the sprite in bytes
   57AC FE 43         [ 7]  161    cp    #clip_Height            ;; Compare A with clipping height: y coordinate where clipping starts
   57AE 38 05         [12]  162    jr     c, no_clip             ;; If Carry, (A < 160), no need to do clipping
                            163 
                            164    ;; Perform clippling (A = vertical size of the sprite to be drawn)
   57B0 D6 C8         [ 7]  165    sub   #screen_H               ;; A2 =  A - screen_Height
   57B2 ED 44         [ 8]  166    neg                           ;; A3 = -A2 = screen_Height - A
   57B4 47            [ 4]  167    ld     b, a                   ;; B = Reduced sprite height (clipped) to be drawn
                            168 
   57B5                     169 no_clip:
                            170    ;; Draw the sprite 
                            171    ;; - DE already points to video mem, and BC contains WidthxHeight)
   57B5 21 10 40      [10]  172    ld    hl, #_g_octopusjig      ;; HL points to the sprite
   57B8 CD 4A 59      [17]  173    call  cpct_drawSprite_asm     ;; Draw the sprite on the screen
                            174 
   57BB C9            [10]  175    ret                           ;; Return
                            176 
                            177 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                            178 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                            179 ;; FUNC: moveSprite
                            180 ;;    Moves the sprite from down the screen to its final location in a
                            181 ;; simple, linear animation.
                            182 ;; DESTROYS:
                            183 ;;    AF, BC, DE, HL
                            184 ;;
   57BC                     185 moveSprite:
                            186    ;; Draw Sprite After VSYNC
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 65.
Hexadecimal [16-Bits]



   57BC CD F7 59      [17]  187    call  cpct_waitVSYNC_asm   ;; Wait for VSYNC
                            188 
                     0050   189    y_coord = .+2              ;; Location in memory of the value for the Y coordinate
   57BF 01 11 C7      [10]  190    ld    bc, #initxy_sprite   ;; BC takes XY coordinates (value loaded is modified dynamically)
   57C2 CD A0 57      [17]  191    call  drawSpriteClipped    ;; Draw the sprite
                            192 
                            193    ;; Move Sprite Up
   57C5 21 C1 57      [10]  194    ld    hl, #y_coord         ;; HL points to y_coord in memory
   57C8 7E            [ 7]  195    ld     a, (hl)             ;; A = y (Vertical coordinate)
   57C9 FE 14         [ 7]  196    cp    #sprite_end_y        ;; Check against y coordinate where sprite has to end its animation (end_y)
   57CB C8            [11]  197    ret   z                    ;; If y==end_y, end of the animation (no more coordinate update)
                            198 
   57CC 35            [11]  199    dec   (hl)                 ;; Move sprite 1 pixel UP (y--)
                            200 
   57CD 18 ED         [12]  201    jr    moveSprite           ;; Loop again
                            202 
                            203 
                            204 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                            205 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                            206 ;; FUNC: redrawString
                            207 ;;    Draws a string with a new colour value each time, on a given location
                            208 ;; INPUT:
                            209 ;;    IY: Pointer to the string
                            210 ;;    B: y pixel coordinate where to draw the string
                            211 ;;    C: x pixel coordinate where to draw the string
                            212 ;; DESTROYS:
                            213 ;;    AF, BC, DE, HL
                            214 ;;
   57CF                     215 redrawString:
                            216    ;; Calculate screen location where to draw the string
                            217    ;; BC Already have screen coordinates for the string to be drawn
   57CF 11 00 C0      [10]  218    ld    de, #pvideomem          ;; DE points to the start of video memory
   57D2 CD 5C 62      [17]  219    call  cpct_getScreenPtr_asm   ;; Return pointer to byte located at (x,y) (C, B) in HL
   57D5 E5            [11]  220    push  hl                      ;; Returns HL = Pointer to video memory (Required by drawStringM0)
                            221                                  ;; We save it for later use
                            222 
                            223    ;; Set colours to be used by DrawChar/DrawStringM0 functions
                     0066   224    fg_colour = .+1               ;; fg_colour = location in memory of the Foreground colour value
   57D6 21 01 00      [10]  225    ld    hl, #init_colour        ;; HL = fg/bg colours (value modified dynamically)
   57D9 CD 39 62      [17]  226    call  cpct_setDrawCharM0_asm  ;; Set colours before using DrawStringM0
                            227 
                            228    ;; Draw the string (IY points to the string)
   57DC E1            [10]  229    pop   hl                      ;; HL Points to video memory location where the string will be drawn
   57DD CD C0 58      [17]  230    call  cpct_drawStringM0_asm   ;; Draw the string
                            231 
                            232    ;; Increment colour for next call
   57E0 3A D7 57      [13]  233    ld     a, (fg_colour)         ;; A = Foreground colour
   57E3 3C            [ 4]  234    inc    a                      ;; A++
   57E4 FE 10         [ 7]  235    cp     #palete_size           ;; Check against number of palette colours used
   57E6 38 02         [12]  236    jr     c, dont_reset_a        ;; If Carry (A < palette_size), do nothing
   57E8 3E 01         [ 7]  237    ld     a, #1                  ;; Else, set A=1 again
                            238 
   57EA                     239 dont_reset_a:
   57EA 32 D7 57      [13]  240    ld    (fg_colour), a          ;; Save Foreground colour for next use
                            241 
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 66.
Hexadecimal [16-Bits]



   57ED C9            [10]  242    ret                           ;; Return
                            243 
                            244 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                            245 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                            246 ;; FUNC: doOneScrollStep
                            247 ;;    Scrolls a complete charater line 1 byte to the left or to the right 
                            248 ;; (2 mode 0 pixels)
                            249 ;; INPUT: 
                            250 ;;    HL: Pointer to the start of the first screen line to be scrolled (it
                            251 ;; must be a pixel-0 screen line of a character)
                            252 ;;     A: -1 to scroll the line to the left, other value to scroll to the right
                            253 ;; DESTROYS:
                            254 ;;    AF, BC, DE, HL
                            255 ;;
                     001C   256 inc_e  = 0x1C   ;; Opcode for incrementing e
                     002C   257 inc_l  = 0x2C   ;; Opcode for incrementing l
                     B0ED   258 _ldir_ = 0xB0ED ;; Opcode for LDIR
                     B8ED   259 _lddr_ = 0xB8ED ;; Opcode for LDDR
                            260 
   57EE                     261 doOneScrollStep:
                            262    ;;
                            263    ;; Set up the copy
                            264    ;;
                            265    
                            266    ;; Check type of copy (-1=scroll left, scroll right otherwise)
   57EE 3C            [ 4]  267    inc    a                ;; A++ (To check if A is -1 or not)
   57EF 28 0B         [12]  268    jr     z, scr_left      ;; If A=-1, scroll left
                            269 
   57F1                     270 scr_right:                 ;; A is not -1, scroll right
   57F1 3E 1C         [ 7]  271    ld     a, #inc_e        ;; Increment e on scrolling right (so DE = HL + 1)
   57F3 01 4E 00      [10]  272    ld    bc, #screen_W-2   ;; | Add 78 bytes to point to ...
   57F6 09            [11]  273    add   hl, bc            ;; | ... the byte before the last byte of the line 
   57F7 01 ED B8      [10]  274    ld    bc, #_lddr_       ;; Copy instruction to use: decrementing copy (HL=>DE, DE--, HL--, BC--)
   57FA 18 05         [12]  275    jr    start_copy        ;; Start the copy
                            276 
   57FC                     277 scr_left:
   57FC 3E 2C         [ 7]  278    ld     a, #inc_l        ;; | Increment l on scrolling left (so HL = DE + 1)
   57FE 01 ED B0      [10]  279    ld    bc, #_ldir_       ;; Copy instruction to use: incrementing copy (HL=>DE, DE++, HL++, BC--)
                            280 
   5801                     281 start_copy:
                            282    ;; Modify loop instruction that differs between movements and start
   5801 ED 43 11 58   [20]  283    ld   (scr_pcopy), bc    ;; | Modify internal loop code with instructions...
   5805 32 0D 58      [13]  284    ld   (scr_pincr), a     ;; | ... required for this type of copy
                            285    
                            286    ;;
                            287    ;; Do the copy
                            288    ;;
   5808 3E 08         [ 7]  289    ld     a, #8            ;; 8 pixel lines to be scrolled
   580A                     290 loop_scroll:
   580A E5            [11]  291    push  hl                ;; Save current hl value
                            292 
   580B 54            [ 4]  293    ld     d, h             ;; | DE points to the first byte...
   580C 5D            [ 4]  294    ld     e, l             ;; | and HL to the next one
                     009C   295    scr_pincr = .           ;; << Memory address of the increment instruction
   580D 2C            [ 4]  296    inc    l                ;; | (this instruction is modified dynamically: inc l / inc e)
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 67.
Hexadecimal [16-Bits]



                            297 
   580E 01 4F 00      [10]  298    ld    bc, #screen_W-1   ;; 79 bytes to copy (all bytes in 1 line minus the first one)
                     00A0   299    scr_pcopy = .           ;; << Memory address of the copy instruction
   5811 ED B0         [21]  300    ldir                    ;; do the copy  (This instruction is modified dynamically: ldir / lddr)
                            301 
   5813 E1            [10]  302    pop   hl                ;; Restore HL value, for calculations
                            303 
   5814 3D            [ 4]  304    dec    a                ;; A-- (1 line less to be copied)
   5815 C8            [11]  305    ret    z                ;; If A==0, scroll has ended
                            306 
                            307    ;; Point to the next line to be scrolled inside this same character (HL += 0x800)
   5816 47            [ 4]  308    ld     b, a             ;; B = A (B acts as a backup of A)
   5817 7C            [ 4]  309    ld     a, h             ;; | HL += 0x800
   5818 C6 08         [ 7]  310    add   #8                ;; |
   581A 67            [ 4]  311    ld     h, a             ;; |
   581B 78            [ 4]  312    ld     a, b             ;; A = B (Restore A value from its backup)
                            313 
   581C 18 EC         [12]  314    jr    loop_scroll       ;; Next line
                            315 
                            316 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                            317 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                            318 ;; FUNC: moveString
                            319 ;;    Moves a string 1 byte to the left or to the right, bouncing on the
                            320 ;; boundaries and then redrawing the string with a new colour
                            321 ;; INPUT:
                            322 ;;    IX: Pointer to a 6-bytes structure containing these fields,
                            323 ;;       2 bytes > Pointer to string to be drawn
                            324 ;;       1 byte  > x coordinate where the string is
                            325 ;;       1 byte  > y coordinate where the string is
                            326 ;;       1 byte  > current movement velocity (-1 or +1)
                            327 ;;       1 byte  > max x coordinate (where it should bounce on the right side)
                            328 ;; MODIFIES:
                            329 ;;       byte 2: x coordinate 
                            330 ;;       byte 4: movement velocity 
                            331 ;; DESTROYS:
                            332 ;;    AF, AF', BC, DE, HL
                            333 ;;
   581E                     334 moveString:
                            335    ;; Update x location
   581E DD 56 04      [19]  336    ld     d, 4(ix)               ;; D  = x velocity (VelX)
   5821 DD 7E 02      [19]  337    ld     a, 2(ix)               ;; A  = x coordinate
   5824 82            [ 4]  338    add    d                      ;; A2 = A + D = x + VelX
                            339 
                            340    ;; Set B=y coordinate, as this value will be used by both next branches
   5825 DD 46 03      [19]  341    ld     b, 3(ix)               ;; B = y coordinate of the string
                            342 
                            343    ;; Check whether string is touching a boundary or not
   5828 28 05         [12]  344    jr     z, boundary_hit        ;; If x == 0, left boundary (1) has been exceeded
   582A DD BE 05      [19]  345    cp  5(ix)                     ;; Check against maxX value
   582D 38 15         [12]  346    jr     c, do_string_movement  ;; If x < maxX, right boundary has not been hit
                            347 
   582F                     348 boundary_hit:
                            349    ;; Save in C the x coordinate previous to the actual one (boundary exceeded)
   582F 92            [ 4]  350    sub    d                      ;; A = A2 - D = x + VelX - VelX = x
   5830 4F            [ 4]  351    ld     c, a                   ;; C = x
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 68.
Hexadecimal [16-Bits]



                            352 
                            353    ;; Invert velocity (to start scrolling to the other side)
   5831 AF            [ 4]  354    xor    a                      ;; A = 0
   5832 92            [ 4]  355    sub    d                      ;; A = -D = -VelX
   5833 DD 77 04      [19]  356    ld 4(ix), a                   ;; Update VelX value
                            357    
                            358    ;; Redraw string with a new colour value
                            359    ;; (BC already contains y and x coordinates)
   5836 DD 7E 00      [19]  360    ld     a, 0(ix)               ;; | IY = Pointer to the string
   00C8                     361    ld__iyl_a                     ;; |
   5839 FD 6F                 1    .dw #0x6FFD  ;; Opcode for ld iyl, a
   583B DD 7E 01      [19]  362    ld     a, 1(ix)               ;; |
   00CD                     363    ld__iyh_a                     ;; |
   583E FD 67                 1    .dw #0x67FD  ;; Opcode for ld iyh, a
   5840 CD CF 57      [17]  364    call  redrawString            ;; Redraws the string
                            365 
   5843 C9            [10]  366    ret                           ;; Nothing more to do, return.
                            367 
   5844                     368 do_string_movement:
                            369    ;; Update string's x location
   5844 DD 77 02      [19]  370    ld 2(ix), a                   ;; Update x location value
                            371 
                            372    ;; Save VelX into a'
   5847 7A            [ 4]  373    ld     a, d                   ;; A = D = VelX
   5848 08            [ 4]  374    ex    af, af'                 ;; A' = VelX
                            375 
                            376    ;; Calculate memory location for y line
                            377    ;; (B already contains y coordinate)
   5849 0E 00         [ 7]  378    ld     c, #0                  ;; C = 0 (x coordinate = 0 to get the start of the y line)
   584B 11 00 C0      [10]  379    ld    de, #pvideomem          ;; DE points to the start of video memory
   584E CD 5C 62      [17]  380    call  cpct_getScreenPtr_asm   ;; Return pointer to byte located at (x,y) (C, B) in HL
                            381    ;; HL now points to the start of the first pixel line where the
                            382    ;; string is located (to be able to scroll it)
                            383 
                            384    ;; Scroll the string
                            385    ;; (HL already points to the start of the first pixel line to be scrolled)
   5851 08            [ 4]  386    ex    af, af'                 ;; A = VelX (recover value from A')
   5852 CD EE 57      [17]  387    call  doOneScrollStep         ;; Do scroll to the side determined by VelX
                            388 
   5855 C9            [10]  389    ret                           ;; Return
                            390 
                            391 
                            392 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                            393 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                            394 ;; MAIN function. This is the entry point of the application.
                            395 ;;    _main:: global symbol is required for correctly compiling and linking
                            396 ;;
   5856                     397 _main:: 
   5856 CD 7C 57      [17]  398    call  init                 ;; Initialize the CPC
   5859 CD BC 57      [17]  399    call  moveSprite           ;; Do the complete sprite animation and return when finished
                            400 
                            401    ;; Draw octopusjig string
   585C FD 21 8E 62   [14]  402    ld    iy, #str_dav         ;; IY points to @octopusjig string
   5860 01 12 02      [10]  403    ld    bc, #xy_str_dav      ;; BC = y, x coordinates where to draw @octopusjig string
   5863 CD CF 57      [17]  404    call  redrawString         ;; Draw the string with the initial colour
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 69.
Hexadecimal [16-Bits]



                            405 
   5866                     406 loop:
                            407    ;; Scroll Happy String
   5866 DD 21 9A 62   [14]  408    ld    ix, #tscroll_happy   ;; IX points to the structure with scroll information about "Happy"
   586A CD F7 59      [17]  409    call  cpct_waitVSYNC_asm   ;; Wait for VSYNC before proceeding
   586D CD 1E 58      [17]  410    call  moveString           ;; Move "Happy" String
                            411 
                            412    ;; Scroll BDay String
   5870 DD 21 A0 62   [14]  413    ld    ix, #tscroll_bday    ;; IX points to the structure with scroll information about "Birthday"
   5874 CD F7 59      [17]  414    call  cpct_waitVSYNC_asm   ;; Wait for VSYNC before proceeding
   5877 CD 1E 58      [17]  415    call  moveString           ;; Move "Birthday" String
                            416 
   587A 18 EA         [12]  417    jr    loop                 ;; Repeat forever
