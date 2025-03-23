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
                     0050    24 screen_W      = 80             ;; Width of the screen in bytes
                     0004    25 palete_size   = 4              ;; Number of total palette colours
                     0010    26 border_colour = 0x0010         ;; 0x10 (Border ID), 0x00 (Colour to set: White).
                     1805    27 sprite_HxW    = 0x1805         ;; Height (24, 0x18) and Width (5, 0x05) of the sprite in bytes.
                     004B    28 sprite_end_x  = 75             ;; x coordinate where sprite will bounce to the left
                     0001    29 look_left     = 0x01           ;; Looking Left
                     0000    30 look_right    = 0x00           ;; Looking right
                             31 
                             32 ;;===============================================================================
                             33 ;; DATA SECTION
                             34 ;;===============================================================================
                             35 
                             36 .area _DATA
                             37 
                             38 ;; ASCII zero-terminated String to be printed at the top of the screen
                             39 ;;
   445E 5B 20 4D 4F 44 45    40 str_demo:: .asciz "[ MODE 1 ] Sprite Flipping Demo"
        20 31 20 5D 20 53
        70 72 69 74 65 20
        46 6C 69 70 70 69
        6E 67 20 44 65 6D
        6F 00
                     0020    41 str_len      = . - str_demo  ;; Length of the string
                     0001    42 str_colour   = 0x0001	     ;; Pen 1, Paper 0 (Black over background)
                             43 
                             44 ;; String location at the centre of the first character line in the screen
                             45 ;; pvideomem is (0, 0) location and we have to add to it half the bytes
                             46 ;; that will be left after printing the string
                     C008    47 str_location = pvideomem + (screen_W - str_len*2)/2 
                             48 
                             49 ;; Sprites and palette are defined in an external file. As they are
                             50 ;; defined in C language, their symbols will be preceded by an underscore.
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 2.
Hexadecimal [16-Bits]



                             51 ;; We declare sprite symbols here as global, and the linker will look
                             52 ;; for them on the other file.
                             53 .globl _g_spr_monsters_0
                             54 .globl _g_spr_monsters_1
                             55 .globl _g_spr_palette
                             56 
                             57 ;; Monster Sprites (20x24 pixels each)
                             58 ;;  (This sprites are a modification from Mini Knight Expansion 1, by Master484
                             59 ;;   got from OpenGameArt: http://opengameart.org/content/mini-knight-expansion-1-0
                             60 ;;   with Public Domain License CC0: http://creativecommons.org/publicdomain/zero/1.0/)
                             61 ;;
                             62 ;;   Each sprite in this structure is encoded as follows (3 Bytes per sprite):
                             63 ;;     1 Byte  - Direction towards the sprite is looking (1=Left, 0=Right)
                             64 ;;     2 Bytes - Pointer to the sprite
                             65 ;; 
   447E                      66 g_sprites::
                             67    ;; Sprite 0 (monster 0)
   447E 00                   68    .db look_right        ;; Direction towards the sprite is looking at
   447F 04 40                69    .dw _g_spr_monsters_0 ;; Pointer to the sprite
                             70    ;; Sprite 1 (monster 0)
   4481 00                   71    .db look_right        ;; Direction towards the sprite is looking at
   4482 7C 40                72    .dw _g_spr_monsters_1 ;; Pointer to the sprite
                             73 
                             74 ;; Moving entities. 8 moving entities on the screen,
                             75 ;;  each one having next structure (2 Bytes per entity):
                             76 ;;   - 1 Byte - X Horizontal coordinate
                             77 ;;   - 1 Byte - look_at value (1=Left,0=Right)
                             78 ;;
   4484                      79 g_mentities::
   4484 00 00                80    .db   0, look_right   ;; Entity 0
   4486 0A 00                81    .db  10, look_right   ;; Entity 1
   4488 19 00                82    .db  25, look_right   ;; Entity 2
   448A 28 00                83    .db  40, look_right   ;; Entity 3
   448C 32 01                84    .db  50, look_left    ;; Entity 4
   448E 23 01                85    .db  35, look_left    ;; Entity 5
   4490 14 01                86    .db  20, look_left    ;; Entity 6
   4492 05 01                87    .db   5, look_left    ;; Entity 7
                             88 
                             89 ;;===============================================================================
                             90 ;; CODE SECTION
                             91 ;;===============================================================================
                             92 
                             93 .area _CODE
                             94 
                             95 ;; Symbols with the names of the CPCtelera functions we want to use
                             96 ;; must be declared globl to be recognized by the compiler. Later on,
                             97 ;; linker will do its job and make the calls go to function code.
                             98 .globl cpct_disableFirmware_asm
                             99 .globl cpct_setVideoMode_asm
                            100 .globl cpct_setPalette_asm
                            101 .globl cpct_setPALColour_asm
                            102 .globl cpct_getScreenPtr_asm
                            103 .globl cpct_hflipSpriteM1_asm
                            104 ;.globl cpct_hflipSpriteM1_r_asm ;; Alternative ROM-friendly version
                            105 .globl cpct_drawSprite_asm
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 3.
Hexadecimal [16-Bits]



                            106 .globl cpct_drawStringM1_f_asm
                            107 .globl cpct_waitVSYNC_asm
                            108 
                            109 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                            110 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                            111 ;; FUNC: initialize
                            112 ;;    Sets CPC to its initial status
                            113 ;; DESTROYS:
                            114 ;;    AF, BC, DE, HL
                            115 ;;
   40F4                     116 initialize::
                            117    ;; Disable Firmware
   40F4 CD 3B 44      [17]  118    call  cpct_disableFirmware_asm   ;; Disable firmware
                            119 
                            120    ;; Set Mode 1
   40F7 0E 01         [ 7]  121    ld    c, #1                      ;; C = 1 (New video mode)
   40F9 CD D3 43      [17]  122    call  cpct_setVideoMode_asm      ;; Set Mode 1
                            123    
                            124    ;; Set Palette
   40FC 21 00 40      [10]  125    ld    hl, #_g_spr_palette        ;; HL = pointer to the start of the palette array
   40FF 11 04 00      [10]  126    ld    de, #palete_size           ;; DE = Size of the palette array (num of colours)
   4102 CD 97 41      [17]  127    call  cpct_setPalette_asm        ;; Set the new palette
                            128 
                            129    ;; Change border colour
   4105 21 10 00      [10]  130    ld    hl, #border_colour         ;; L=Border colour value, H=Palette Colour to be set (Border=16)
   4108 CD AA 41      [17]  131    call  cpct_setPALColour_asm      ;; Set the border (colour 16)
                            132 
                            133    ;; Draw upper string             
   410B 21 5E 44      [10]  134    ld    hl, #str_demo              ;; HL points to the string with the demo message
   410E 01 01 00      [10]  135    ld    bc, #str_colour            ;; BC = fg/bg colours used to draw the string
   4111 11 08 C0      [10]  136    ld    de, #str_location          ;; DE points to the place in video memory where the string will be drawn
   4114 CD 5C 42      [17]  137    call  cpct_drawStringM1_f_asm    ;; Draw the string (fast method)
                            138 
   4117 C9            [10]  139    ret                              ;; return
                            140 
                            141 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                            142 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                            143 ;; FUNC: drawEntity
                            144 ;;    Draws an entity on the screen 
                            145 ;; INPUT:
                            146 ;;    B: y pixel coordinate where to draw the sprite
                            147 ;;    C: x pixel coordinate where to draw the sprite
                            148 ;;    D: Current entity "looking_at"
                            149 ;;   HL: Pointer to sprite structure
                            150 ;; DESTROYS:
                            151 ;;    AF, BC, DE, HL
                            152 ;;
   4118                     153 drawEntity::
                            154    ;; Check if sprite has to be flipped or not
   4118 7E            [ 7]  155    ld    a, (hl)                 ;; A = direction where the entity is currently looking at
   4119 BA            [ 4]  156    cp    d                       ;; Check against where the sprite is looking
                            157 
   411A 23            [ 6]  158    inc  hl                       ;; | DE = Pointer to the sprite
   411B 5E            [ 7]  159    ld    e, (hl)                 ;; |
   411C 23            [ 6]  160    inc  hl                       ;; |
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 4.
Hexadecimal [16-Bits]



   411D 56            [ 7]  161    ld    d, (hl)                 ;; |
   411E D5            [11]  162    push de                       ;; Save pointer to the sprite in the stack for later use
                            163 
                            164    ;; This Conditional jump uses result from previous "CP E" instruction
   411F 28 0E         [12]  165    jr    z, looking_good         ;; If Z, sprite is looking to the right direction, nothing to do
                            166 
                            167    ;; Flip the sprite because it is looking opposite
   4121 C5            [11]  168    push  bc                      ;; save x, y coordinates passed as parameters
   4122 EE 01         [ 7]  169    xor   #0x01                   ;; Switch looking direction (0->1, or 1->0)
   4124 2B            [ 6]  170    dec   hl                      ;; | HL -= 2, to make it point again to the sprite looking_at value
   4125 2B            [ 6]  171    dec   hl                      ;; |
   4126 77            [ 7]  172    ld  (hl),a                    ;; Save new looking_at direction
                            173 
                            174    ;; Flip the sprite
   4127 01 05 18      [10]  175    ld    bc, #sprite_HxW         ;; B = Sprite Height, C = Width
   412A EB            [ 4]  176    ex    de, hl                  ;; HL points to the sprite (DE was pointing to it)
   412B CD E0 43      [17]  177    call  cpct_hflipSpriteM1_asm   ;; Flip the sprite
                            178 
                            179    ;; Sprite could also be flipped using ROM-friendly version, using this code
                            180    ;; (.globl cpct_hflipSpriteM1_r_asm must be added)
                            181    ;ld    hl, #sprite_HxW         ;; H = Sprite Height, L = Width
                            182    ;call  cpct_hflipSpriteM1_r_asm;; Flip the sprite
                            183 
   412E C1            [10]  184    pop   bc                      ;; Recover coordinates to draw the sprite
                            185 
   412F                     186 looking_good:
                            187    ;; Calculate the memory location where the sprite will be drawn
   412F 11 00 C0      [10]  188    ld    de, #pvideomem          ;; DE points to the start of video memory
   4132 CD 4C 44      [17]  189    call  cpct_getScreenPtr_asm   ;; Return pointer to byte located at (x, y) (C, B) in HL
   4135 EB            [ 4]  190    ex    de, hl                  ;; DE = pointer to video memory location to draw the sprite
                            191 
                            192    ;; Draw the sprite 
                            193    ;; - DE already points to video memory location where sprite will be drawn
   4136 E1            [10]  194    pop   hl                      ;; HL points to the sprite (Recover from the stack)
   4137 01 05 18      [10]  195    ld    bc, #sprite_HxW         ;; BC = Sprite WidthxHeight
   413A CD B4 41      [17]  196    call  cpct_drawSprite_asm     ;; Draw the sprite on the screen
                            197 
   413D C9            [10]  198    ret                           ;; Return
                            199 
                            200 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                            201 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                            202 ;; FUNC: moveNextEntity
                            203 ;;    Picks up the next entity and moves it 1 step to its looking_at direction 
                            204 ;; DESTROYS:
                            205 ;;    AF, BC, DE, HL
                            206 ;;
   413E 07                  207 lastMovedEntity: .db 7  ;; Holds the ID of the last entity that has been moved
   413F                     208 moveNextEntity::
   413F 21 3E 41      [10]  209    ld    hl, #lastMovedEntity    ;; HL points to the ID value of the last entity moved
   4142 7E            [ 7]  210    ld     a, (hl)                ;; A = ID of the last entity moved
   4143 3C            [ 4]  211    inc    a                      ;; A++ (A = Next entity to be moved)
   4144 E6 07         [ 7]  212    and #0x07                     ;; A %= 8 (If A > 7 then A = 0)
   4146 77            [ 7]  213    ld   (hl), a                  ;; Store A as last moved entity (Update variable value)
                            214 
                            215    ;; Select the sprite type for this entity (odd entities = Sprite 1, even = Sprite 0)
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 5.
Hexadecimal [16-Bits]



   4147 5F            [ 4]  216    ld     e, a                   ;; E = A (Save A value for later use)
   4148 21 7E 44      [10]  217    ld    hl, #g_sprites          ;; HL points to the vector of sprite types
   414B 0F            [ 4]  218    rrca                          ;; Move Least Significant bit of A to the Carry to check if its is ODD or Even
   414C 30 04         [12]  219    jr    nc, even                ;; If Carry=0, LSB of A was 0, so A was even: HL already points to sprite 0
                            220 
                            221    ;; Odd sprite type: HL must point to sprite 1, 3 bytes away
   414E 01 03 00      [10]  222    ld    bc, #3                  ;; BC = 3
   4151 09            [11]  223    add   hl, bc                  ;; HL += 3 (HL now points to sprite 1)
                            224 
   4152                     225 even:
   4152 E5            [11]  226    push  hl                      ;; Save HL pointing to the sprite type for later use
                            227 
                            228    ;; Point to the Entity selected 
   4153 CB 23         [ 8]  229    sla    e                      ;; E *= 2 ( Entity Index (0-7) * 2)
   4155 16 00         [ 7]  230    ld     d, #0                  ;; D = 0 so that DE = E = Entity Index * 2
   4157 21 84 44      [10]  231    ld    hl, #g_mentities        ;; HL points to the start of entities vector
   415A 19            [11]  232    add   hl, de                  ;; HL += DE, HL points to the concrete entity to be updated
                            233 
                            234    ;; Update entity information
   415B 4E            [ 7]  235    ld     c, (hl)                ;; C = X coordinate of the entity
   415C 23            [ 6]  236    inc   hl                      ;; HL Points to the looking_at value for this entity
   415D 56            [ 7]  237    ld     d, (hl)                ;; D = Looking at value of the entity
   415E 7A            [ 4]  238    ld     a, d                   ;; | Check if the entity is looking right
   415F FE 00         [ 7]  239    cp    #look_right             ;; | 
   4161 28 07         [12]  240    jr     z, ent_look_right      ;; If Z, B was looking right
                            241 
                            242    ;; Entity looking left
   4163 0D            [ 4]  243    dec    c                      ;; Move entity to the left 1 byte
   4164 20 0C         [12]  244    jr     nz, location_updated   ;; If C != 0, we haven't reached left limit
                            245 
                            246    ;; left limit reached
   4166 15            [ 4]  247    dec    d                      ;; D = 0 (Look right)
   4167 72            [ 7]  248    ld  (hl), d                   ;; Make entity look right
   4168 18 08         [12]  249    jr     location_updated       ;; Finished moving, update location and continue
                            250 
   416A                     251 ent_look_right:
                            252    ;; Entity looking right
   416A 0C            [ 4]  253    inc    c                      ;; Move entity to the right 1 byte
   416B 3E 4B         [ 7]  254    ld     a, #sprite_end_x       ;; | Check against sprite end x
   416D B9            [ 4]  255    cp     c                      ;; |
   416E 20 02         [12]  256    jr    nz, location_updated    ;; If B != sprite_end_x, we haven't reached right limit
                            257 
                            258    ;; Right limit reached
   4170 14            [ 4]  259    inc    d                      ;; D = 1 (looking left)
   4171 72            [ 7]  260    ld  (hl), d                   ;; Make entity look left
                            261 
   4172                     262 location_updated:
   4172 2B            [ 6]  263    dec   hl                      ;; Make HL point again to Entity Location
   4173 71            [ 7]  264    ld  (hl), c                   ;; Update entity location
                            265 
                            266    ;; Calculate Y location for the entity, given its ID, using this formulat
                            267    ;; Y = 24*EntityID + 8
   4174 AF            [ 4]  268    xor    a                      ;; A = 0 and clear Carry flag
   4175 7B            [ 4]  269    ld     a, e                   ;; A =  2*EntityID (0-7 * 2)
   4176 17            [ 4]  270    rla                           ;; A =  4*EntityID
ASxxxx Assembler V02.00 + NoICE + SDCC mods  (Zilog Z80 / Hitachi HD64180), page 6.
Hexadecimal [16-Bits]



   4177 17            [ 4]  271    rla                           ;; A =  8*EntityID
   4178 5F            [ 4]  272    ld     e, a                   ;; E =  8*EntityID
   4179 17            [ 4]  273    rla                           ;; A = 16*EntityID
   417A 83            [ 4]  274    add    e                      ;; A = 16*EntityID + 8*EntityID = 24*EntityID
   417B C6 08         [ 7]  275    add   #8                      ;; A = 24*EntityID + 8
   417D 47            [ 4]  276    ld     b, a                   ;; B = A (Y location of the entity)
                            277 
                            278    ;; Draw entity (HL=Sprite structure, D=Entity looking_at, B=Y Coordinate, C=X Coordinate)
   417E E1            [10]  279    pop   hl                      ;; HL points to the sprite structure
   417F CD 18 41      [17]  280    call drawEntity               ;; Draw the updated entity
                            281 
   4182 C9            [10]  282    ret                           ;; Nothing more to do, return.
                            283 
                            284 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                            285 ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                            286 ;; MAIN function. This is the entry point of the application.
                            287 ;;    _main:: global symbol is required for correctly compiling and linking
                            288 ;;
   4183                     289 _main:: 
   4183 CD F4 40      [17]  290    call  initialize           ;; Initialize the CPC
                            291 
   4186                     292 loop:
   4186 CD 33 44      [17]  293    call  cpct_waitVSYNC_asm ;; Synchronize with VSYNC
                            294 
                            295    ;; Move 4 entities in a ROW
   4189 CD 3F 41      [17]  296    call  moveNextEntity     ;; Moves next Entity
   418C CD 3F 41      [17]  297    call  moveNextEntity     ;; Moves next Entity
   418F CD 3F 41      [17]  298    call  moveNextEntity     ;; Moves next Entity
   4192 CD 3F 41      [17]  299    call  moveNextEntity     ;; Moves next Entity
                            300 
   4195 18 EF         [12]  301    jr    loop               ;; Repeat forever
