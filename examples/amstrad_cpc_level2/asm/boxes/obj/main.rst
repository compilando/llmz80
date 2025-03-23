ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 1.
Hexadecimal [16-Bits]



                              1 ;;-----------------------------LICENSE NOTICE------------------------------------
                              2 ;;  This file is part of CPCtelera: An Amstrad CPC Game Engine 
                              3 ;;  Copyright (C) 2015 ronaldo / Fremos / Cheesetea / ByteRealms (@FranGallegoBR)
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
                             20 ;; Start of _DATA area
                             21 ;;    (SDCC requires at least _DATA and _CODE areas to be declared. )
                             22 ;;
                             23 .area _DATA
                             24 
                             25 ;; Include all CPCtelera keyboard constant definitions and variables
                             26 ;; (Beware not to include this in code area, or variables will be 
                             27 ;; treated as code and executed!)
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 2.
Hexadecimal [16-Bits]



                             28 .include "keyboard/keyboard.s"
                              1 ;;-----------------------------LICENSE NOTICE------------------------------------
                              2 ;;  This file is part of CPCtelera: An Amstrad CPC Game Engine 
                              3 ;;  Copyright (C) 2014-2017 ronaldo / Fremos / Cheesetea / ByteRealms (@FranGallegoBR)
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
                             18 .module cpct_keyboard
                             19 
                             20 ;; Definition of the cpct_keyboardStatusBuffer array where
                             21 ;; keypresses are temporarily stored
   42D8 FF FF FF FF FF FF    22 _cpct_keyboardStatusBuffer:: .db 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF
        FF FF FF FF
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 3.
Hexadecimal [16-Bits]



                             29 
   42E2 50 6C 65 61 73 65    30 str_press: .asciz "Please, press any key.";
        2C 20 70 72 65 73
        73 20 61 6E 79 20
        6B 65 79 2E 00
                             31 
                             32 ;;
                             33 ;; Start of _CODE area
                             34 ;; 
                             35 .area _CODE
                             36 
                             37 ;; 
                             38 ;; Declare all function entry points as global symbols for the compiler
                             39 ;; (The linker will know what to do with them)
                             40 .globl cpct_memset_asm
                             41 .globl cpct_drawSolidBox_asm
                             42 .globl cpct_isAnyKeyPressed_asm  
                             43 .globl cpct_scanKeyboard_asm 
                             44 .globl cpct_drawStringM1_f_asm
                             45 .globl cpct_disableFirmware_asm
                             46 .globl cpct_getScreenPtr_asm
                             47 
                             48 ;;
                             49 ;; MAIN function. This is the entry point of the application.
                             50 ;;    _main:: global symbol is required for correctly compiling and linking
                             51 ;;
   4000                      52 _main::
                             53    ;; Disable firmware to prevent it from interfering with string drawing
   4000 CD E1 41      [17]   54    call cpct_disableFirmware_asm
                             55 
                             56    ;; Clear the screen (in red)
   4003 11 00 C0      [10]   57    ld   de, #0xC000  ;; DE = Pointer to video memory location to start copying bytes
   4006 01 00 40      [10]   58    ld   bc, #0x4000  ;; BC = 0x4000 (16K) bytes to copy (full video memory)
   4009 3E FF         [ 7]   59    ld    a, #0xFF    ;; A  = 0xFF, Colour pattern (3, 3, 3, 3)
                             60    
   400B CD D9 41      [17]   61    call cpct_memset_asm ;; Fill up video memory with colour pattern
                             62 
                             63    ;; Calculate a location for printing a string
   400E 11 00 C0      [10]   64    ld   de, #0xC000    ;; DE = Pointer to start of the screen
   4011 01 10 18      [10]   65    ld   bc, #0x1810    ;; B  = y coordinate (0x18 = 24), C = x coordinate (0x10 = 16)
                             66 
   4014 CD C6 42      [17]   67    call cpct_getScreenPtr_asm ;; Calculate video memory location and return it in HL
                             68 
                             69    ;; Print a string to ask the user for pressing Space
   4017 EB            [ 4]   70    ex   de, hl         ;; Interchange HL <-> DE to make DE = Pointer to video memory where string will be drawn
   4018 21 E2 42      [10]   71    ld   hl, #str_press ;; HL = Pointer to the string 
   401B 01 00 03      [10]   72    ld   bc, #0x0300    ;; B  = Background PEN (3), C = Foreground PEN (0)
                             73 
   401E CD 55 40      [17]   74    call cpct_drawStringM1_f_asm  ;; Draw the string
                             75 
                             76    ;; Wait for the user to press a Key
   4021                      77 loop:
   4021 CD 95 42      [17]   78    call cpct_scanKeyboard_asm    ;; Scan the keyboard
                             79 
   4024 CD CC 41      [17]   80    call cpct_isAnyKeyPressed_asm ;; Check for any key being pressed
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 4.
Hexadecimal [16-Bits]



   4027 B7            [ 4]   81    or   a                        ;; If A key is pressed, A != 0
   4028 28 F7         [12]   82    jr   z, loop                  ;; When A=0, No key is pressed, Loop again
                             83 
                             84    ;; Draw a Box
   402A 11 25 C3      [10]   85    ld   de, #0xC325  ;; DE = Pointer to video memory location where the box will be drawn
   402D 01 0A 14      [10]   86    ld   bc, #0x140A  ;; B = Height (20 = 0x14), C = Width (10 = 0x0A)
   4030 3E AA         [ 7]   87    ld    a, #0xAA    ;; A = Colour Pattern (0xAA = 3, 0, 3, 0)
                             88 
   4032 CD F1 41      [17]   89    call cpct_drawSolidBox_asm ;; Call the box drawing function
                             90 
                             91    ;; Draw another Box
   4035 11 35 C3      [10]   92    ld   de, #0xC335  ;; DE = Pointer to video memory location where the box will be drawn
   4038 01 0A 14      [10]   93    ld   bc, #0x140A  ;; B = Height (20 = 0x14), C = Width (10 = 0x0A)
   403B 3E A0         [ 7]   94    ld    a, #0xA0    ;; A = Colour Pattern (0xAA = 1, 0, 1, 0)
                             95 
   403D CD F1 41      [17]   96    call cpct_drawSolidBox_asm ;; Call the box drawing function
                             97 
                             98    ;; Draw a third Box
   4040 11 45 C3      [10]   99    ld   de, #0xC345  ;; DE = Pointer to video memory location where the box will be drawn
   4043 01 0A 14      [10]  100    ld   bc, #0x140A  ;; B = Height (20 = 0x14), C = Width (10 = 0x0A)
   4046 3E 0A         [ 7]  101    ld    a, #0x0A    ;; A = Colour Pattern (0xAA = 2, 0, 2, 0)
                            102 
   4048 CD F1 41      [17]  103    call cpct_drawSolidBox_asm ;; Call the box drawing function
                            104 
   404B                     105 forever:
   404B 18 FE         [12]  106    jr forever        ;; Infinite waiting loop
