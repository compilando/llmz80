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
                             25 ;; Define a welcome string message
   40F1 57 65 6C 63 6F 6D    26 string: .asciz "Welcome to CPCtelera in ASM!"
        65 20 74 6F 20 43
        50 43 74 65 6C 65
        72 61 20 69 6E 20
        41 53 4D 21 00
                             27 
                             28 ;;
                             29 ;; Start of _CODE area
                             30 ;; 
                             31 .area _CODE
                             32 
                             33 ;; Symbols with the names of the CPCtelera functions we want to use
                             34 ;; must be declared globl to be recognized by the compiler. Later on,
                             35 ;; linker will do its job and make the calls go to function code.
                             36 .globl cpct_disableFirmware_asm
                             37 .globl cpct_drawStringM1_asm
                             38 .globl cpct_setDrawCharM1_asm
                             39 
                             40 ;;
                             41 ;; MAIN function. This is the entry point of the application.
                             42 ;;    _main:: global symbol is required for correctly compiling and linking
                             43 ;;
   4000                      44 _main::
                             45 
                             46    ;; Disable firmware to prevent it from interfering with drawString
   4000 CD 8B 40      [17]   47    call cpct_disableFirmware_asm
                             48 
                             49    ;; Before calling drawstring, we first need to set up the PEN colours
                             50    ;; we want to use for drawing, by calling cpct_setDrawCharM1_asm
   4003 16 00         [ 7]   51    ld   d, #00   ;; Set Background PEN to 0 (BLUE)
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 2.
Hexadecimal [16-Bits]



   4005 1E 03         [ 7]   52    ld   e, #03   ;; Set Foreground PEN to 3 (RED)
                             53 
   4007 CD 9C 40      [17]   54    call cpct_setDrawCharM1_asm ;; Set up colours for drawn characters in mode 1
                             55 
                             56    ;; We are going to call draw String, and we have to push parameters
                             57    ;; to the stack first (as the function recovers it from there).
   400A FD 21 F1 40   [14]   58    ld   iy, #string  ;; IY = Pointer to the start of the string
   400E 21 80 C2      [10]   59    ld   hl, #0xC280  ;; HL = Pointer to video memory location where the string will be drawn
                             60 
   4011 CD 17 40      [17]   61    call cpct_drawStringM1_asm ;; Call the string drawing function
                             62 
   4014                      63 forever:
   4014 C3 14 40      [10]   64    jp forever        ;; Infinite waiting loop
