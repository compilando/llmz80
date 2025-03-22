                              1 ;--------------------------------------------------------
                              2 ; File Created by SDCC : free open source ANSI-C Compiler
                              3 ; Version 3.6.8 #9946 (Linux)
                              4 ;--------------------------------------------------------
                              5 	.module globaldata
                              6 	.optsdcc -mz80
                              7 	
                              8 ;--------------------------------------------------------
                              9 ; Public variables in this module
                             10 ;--------------------------------------------------------
                             11 	.globl _g_keys
                             12 	.globl _g_palette
                             13 	.globl _g_items
                             14 	.globl _g_blendModes
                             15 	.globl _g_selectedBlendMode
                             16 	.globl _g_selectedItem
                             17 ;--------------------------------------------------------
                             18 ; special function registers
                             19 ;--------------------------------------------------------
                             20 ;--------------------------------------------------------
                             21 ; ram data
                             22 ;--------------------------------------------------------
                             23 	.area _DATA
   6F27                      24 _g_selectedItem::
   6F27                      25 	.ds 1
   6F28                      26 _g_selectedBlendMode::
   6F28                      27 	.ds 1
                             28 ;--------------------------------------------------------
                             29 ; ram data
                             30 ;--------------------------------------------------------
                             31 	.area _INITIALIZED
                             32 ;--------------------------------------------------------
                             33 ; absolute external ram data
                             34 ;--------------------------------------------------------
                             35 	.area _DABS (ABS)
                             36 ;--------------------------------------------------------
                             37 ; global & static initialisations
                             38 ;--------------------------------------------------------
                             39 	.area _HOME
                             40 	.area _GSINIT
                             41 	.area _GSFINAL
                             42 	.area _GSINIT
                             43 ;--------------------------------------------------------
                             44 ; Home
                             45 ;--------------------------------------------------------
                             46 	.area _HOME
                             47 	.area _HOME
                             48 ;--------------------------------------------------------
                             49 ; code
                             50 ;--------------------------------------------------------
                             51 	.area _CODE
                             52 	.area _CODE
   6AAF                      53 _g_blendModes:
   6AAF AE                   54 	.db #0xae	; 174
   6AB0 58 4F 52             55 	.ascii "XOR"
   6AB3 00                   56 	.db 0x00
   6AB4 A6                   57 	.db #0xa6	; 166
   6AB5 41 4E 44             58 	.ascii "AND"
   6AB8 00                   59 	.db 0x00
   6AB9 B6                   60 	.db #0xb6	; 182
   6ABA 4F 52 20             61 	.ascii "OR "
   6ABD 00                   62 	.db 0x00
   6ABE 86                   63 	.db #0x86	; 134
   6ABF 41 44 44             64 	.ascii "ADD"
   6AC2 00                   65 	.db 0x00
   6AC3 96                   66 	.db #0x96	; 150
   6AC4 53 55 42             67 	.ascii "SUB"
   6AC7 00                   68 	.db 0x00
   6AC8 7E                   69 	.db #0x7e	; 126
   6AC9 4C 44 49             70 	.ascii "LDI"
   6ACC 00                   71 	.db 0x00
   6ACD 8E                   72 	.db #0x8e	; 142
   6ACE 41 44 43             73 	.ascii "ADC"
   6AD1 00                   74 	.db 0x00
   6AD2 9E                   75 	.db #0x9e	; 158
   6AD3 53 42 43             76 	.ascii "SBC"
   6AD6 00                   77 	.db 0x00
   6AD7 00                   78 	.db #0x00	; 0
   6AD8 4E 4F 50             79 	.ascii "NOP"
   6ADB 00                   80 	.db 0x00
   6ADC                      81 _g_items:
   6ADC 00 40                82 	.dw _g_items_0
   6ADE 20 53 6B 75 6C 6C    83 	.ascii " Skull"
   6AE4 00                   84 	.db 0x00
   6AE5 20 40                85 	.dw _g_items_1
   6AE7 20 50 61 70 65 72    86 	.ascii " Paper"
   6AED 00                   87 	.db 0x00
   6AEE 40 40                88 	.dw _g_items_2
   6AF0 50 6F 74 69 6F 6E    89 	.ascii "Potion"
   6AF6 00                   90 	.db 0x00
   6AF7 60 40                91 	.dw _g_items_3
   6AF9 20 20 20 43 61 74    92 	.ascii "   Cat"
   6AFF 00                   93 	.db 0x00
   6B00                      94 _g_palette:
   6B00 14                   95 	.db #0x14	; 20
   6B01 04                   96 	.db #0x04	; 4
   6B02 1C                   97 	.db #0x1c	; 28
   6B03 0C                   98 	.db #0x0c	; 12
   6B04 16                   99 	.db #0x16	; 22
   6B05 1E                  100 	.db #0x1e	; 30
   6B06 00                  101 	.db #0x00	; 0
   6B07 1F                  102 	.db #0x1f	; 31
   6B08 1B                  103 	.db #0x1b	; 27
   6B09 03                  104 	.db #0x03	; 3
   6B0A 0B                  105 	.db #0x0b	; 11
   6B0B                     106 _g_keys:
   6B0B 05 80               107 	.dw #0x8005
   6B0D 00                  108 	.db #0x00	; 0
   6B0E E0 68               109 	.dw _drawCurrentSpriteAtRandom
   6B10 08 04               110 	.dw #0x0408
   6B12 00                  111 	.db #0x00	; 0
   6B13 80 68               112 	.dw _drawBackground
   6B15 08 01               113 	.dw #0x0108
   6B17 00                  114 	.db #0x00	; 0
   6B18 A9 6B               115 	.dw _selectNextItem
   6B1A 08 02               116 	.dw #0x0208
   6B1C 00                  117 	.db #0x00	; 0
   6B1D BF 6B               118 	.dw _selectNextBlendMode
                            119 	.area _INITIALIZER
                            120 	.area _CABS (ABS)
