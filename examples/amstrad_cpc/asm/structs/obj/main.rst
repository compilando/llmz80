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
                             19 ;; Note: SDCC requires at least _DATA and _CODE areas to be declared.
                             20 
                             21 ;;==============================================================================
                             22 ;; Start of _DATA area
                             23 ;;==============================================================================
                             24 .area _DATA
                             25 
                             26 ;;----------------------------------------------------
                             27 ;; Definition of DATA structures and constants
                             28 ;;----------------------------------------------------
                             29 
                             30 ;; Useful constants
                     C000    31 CPCT_VMEM_START = 0xC000
                             32 
                             33 ;;
                             34 ;; Macro: struct Player
                             35 ;;    Macro that creates a new initialized instance of Player Struct
                             36 ;; 
                             37 ;; Parameters:
                             38 ;;    instanceName: name of the variable that will be created as an instance of Player struct
                             39 ;;    st:           status of the player
                             40 ;;    px:           X location of the Player (bytes)
                             41 ;;    py:           Y location of the Player (pixels)
                             42 ;;    wi:           Width of the Player Sprite (bytes)
                             43 ;;    he:           Height of the Player Sprite (bytes)
                             44 ;;    sprite:       Pointer to the player sprite
                             45 ;;
                             46 .macro definePlayer instanceName, st, px, py, wi, he, sprite
                             47    ;; Struct data
                             48    instanceName:
                             49       instanceName'_status: .db st     ;; Status of the Player
                             50       instanceName'_x_pos:  .db px     ;; X location of the Player (bytes)
                             51       instanceName'_y_pos:  .db py     ;; Y location of the Player (pixels)
                             52       instanceName'_width:  .db wi     ;; Width of the Player Sprite (bytes)
                             53       instanceName'_height: .db he     ;; Height of the Player Sprite (bytes)
                             54       instanceName'_sprite: .dw sprite ;; Pointer to the player sprite
                             55 .endm
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 2.
Hexadecimal [16-Bits]



                             56 
                             57 ;;
                             58 ;; Macro: struct Player offsets
                             59 ;;
                             60 ;;    Macro that generates offsets for accessing different elements of 
                             61 ;; the Player struct (distances from the start of the struct to each
                             62 ;; struct member). Requires a already defined instance as an example for
                             63 ;; calculating offsets.
                             64 ;;
                             65 ;; Parameters:
                             66 ;;    stname:        Name of the structure
                             67 ;;    instanceName:  Name of the instance that will be used to calculate offsets
                             68 ;;
                             69 .macro definePlayerOffsets stname, instanceName
                             70    ;; Offset constants
                             71    stname'_status_off = instanceName'_status - instanceName ;; status offset
                             72    stname'_x_pos_off  = instanceName'_x_pos  - instanceName ;; X offset
                             73    stname'_y_pos_off  = instanceName'_y_pos  - instanceName ;; Y offset
                             74    stname'_width_off  = instanceName'_width  - instanceName ;; Width offset
                             75    stname'_height_off = instanceName'_height - instanceName ;; Height offset
                             76    stname'_sprite_off = instanceName'_sprite - instanceName ;; Sprite offset
                             77 .endm
                             78 
                             79 ;;------------------------------------------------------------
                             80 ;; Definition of data elements
                             81 ;;------------------------------------------------------------
                             82 
                             83 ;; RYU and KEN Sprites (Generated and compiled as C files)
                             84 .globl _g_sprite_ryu
                             85 .globl _g_sprite_ken
                             86 
                             87 ;; Definition of Players
   4E50                      88 definePlayer ryu, 0, 58, 60, 21, 81, _g_sprite_ryu
                              1    ;; Struct data
   0000                       2    ryu:
   4E50 00                    3       ryu_status: .db 0     ;; Status of the Player
   4E51 3A                    4       ryu_x_pos:  .db 58     ;; X location of the Player (bytes)
   4E52 3C                    5       ryu_y_pos:  .db 60     ;; Y location of the Player (pixels)
   4E53 15                    6       ryu_width:  .db 21     ;; Width of the Player Sprite (bytes)
   4E54 51                    7       ryu_height: .db 81     ;; Height of the Player Sprite (bytes)
   4E55 A5 46                 8       ryu_sprite: .dw _g_sprite_ryu ;; Pointer to the player sprite
   4E57                      89 definePlayer ken, 0,  0, 60, 21, 81, _g_sprite_ken
                              1    ;; Struct data
   0007                       2    ken:
   4E57 00                    3       ken_status: .db 0     ;; Status of the Player
   4E58 00                    4       ken_x_pos:  .db 0     ;; X location of the Player (bytes)
   4E59 3C                    5       ken_y_pos:  .db 60     ;; Y location of the Player (pixels)
   4E5A 15                    6       ken_width:  .db 21     ;; Width of the Player Sprite (bytes)
   4E5B 51                    7       ken_height: .db 81     ;; Height of the Player Sprite (bytes)
   4E5C 00 40                 8       ken_sprite: .dw _g_sprite_ken ;; Pointer to the player sprite
   4D4A                      90 definePlayerOffsets player, ryu 
                              1    ;; Offset constants
                     0000     2    player_status_off = ryu_status - ryu ;; status offset
                     0001     3    player_x_pos_off  = ryu_x_pos  - ryu ;; X offset
                     0002     4    player_y_pos_off  = ryu_y_pos  - ryu ;; Y offset
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 3.
Hexadecimal [16-Bits]



                     0003     5    player_width_off  = ryu_width  - ryu ;; Width offset
                     0004     6    player_height_off = ryu_height - ryu ;; Height offset
                     0005     7    player_sprite_off = ryu_sprite - ryu ;; Sprite offset
                             91 
                             92 ;;==============================================================================
                             93 ;; Start of _CODE area
                             94 ;;==============================================================================
                             95 .area _CODE
                             96 
                             97 ;; Symbols with the names of the CPCtelera functions we want to use
                             98 ;; must be declared globl to be recognized by the compiler. Later on,
                             99 ;; linker will do its job and make the calls go to function code.
                            100 .globl cpct_disableFirmware_asm
                            101 .globl cpct_getScreenPtr_asm
                            102 .globl cpct_drawSprite_asm
                            103 .globl cpct_setVideoMode_asm
                            104 
                            105 ;;-----------------------------------------------
                            106 ;; Draw a player
                            107 ;;    IX = player struct pointer
                            108 ;;-----------------------------------------------
   0000                     109 drawPlayer:
                            110    ;; Get Screen Pointer
   4D4A 11 00 C0      [10]  111    ld  de, #CPCT_VMEM_START      ;; DE = Pointer to video memory start
   4D4D DD 4E 01      [19]  112    ld  c, player_x_pos_off(ix)   ;; C  = Player X Position
   4D50 DD 46 02      [19]  113    ld  b, player_y_pos_off(ix)   ;; B  = Player Y Position
   4D53 CD 3E 4E      [17]  114    call cpct_getScreenPtr_asm    ;; Get Screen Pointer
                            115    ;; Return value: HL = Screen Pointer to (X, Y) byte
                            116 
                            117    ;; Draw Sprite
   4D56 EB            [ 4]  118    ex  de, hl                          ;; DE = Pointer to Video Memory (X,Y) location
   4D57 DD 66 06      [19]  119    ld   h, player_sprite_off + 1(ix)   ;; | HL = Pointer to Player Sprite
   4D5A DD 6E 05      [19]  120    ld   l, player_sprite_off + 0(ix)   ;; |
   4D5D DD 4E 03      [19]  121    ld   c, player_width_off (ix)       ;; C = Player Width (bytes)
   4D60 DD 46 04      [19]  122    ld   b, player_height_off(ix)       ;; B = Player Height (pixels)
   4D63 CD 80 4D      [17]  123    call cpct_drawSprite_asm            ;; Draw the sprite
                            124 
   4D66 C9            [10]  125    ret
                            126 
                            127 ;;-----------------------------------------------
                            128 ;; MAIN function. This is the entry point of the application.
                            129 ;;    _main:: global symbol is required for correctly compiling and linking
                            130 ;;-----------------------------------------------
   4D67                     131 _main::
                            132 
                            133    ;; Initialize CPC
   4D67 CD 2D 4E      [17]  134    call cpct_disableFirmware_asm ;; Disable Firmware
   4D6A 0E 00         [ 7]  135    ld  c, #0                     ;; C = 0 (Mode 0)
   4D6C CD 20 4E      [17]  136    call cpct_setVideoMode_asm    ;; Set Mode 0
                            137 
                            138    ;; Draw RYU and KEN
   4D6F DD 21 50 4E   [14]  139    ld  ix, #ryu                  ;; IX = Pointer to Ryu structure
   4D73 CD 4A 4D      [17]  140    call drawPlayer               ;; Draw RYU Player
   4D76 DD 21 57 4E   [14]  141    ld  ix, #ken                  ;; IX = Pointer to Ken structure
   4D7A CD 4A 4D      [17]  142    call drawPlayer               ;; Draw Ken Player
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 4.
Hexadecimal [16-Bits]



                            143 
                            144    ;; Infinite waiting loop
   4D7D                     145 forever:
   4D7D C3 7D 4D      [10]  146    jp forever
