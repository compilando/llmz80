                              1 ;--------------------------------------------------------
                              2 ; File Created by SDCC : free open source ANSI-C Compiler
                              3 ; Version 3.6.8 #9946 (Linux)
                              4 ;--------------------------------------------------------
                              5 	.module predefinedAnimations
                              6 	.optsdcc -mz80
                              7 	
                              8 ;--------------------------------------------------------
                              9 ; Public variables in this module
                             10 ;--------------------------------------------------------
                             11 	.globl _g_anim
                             12 	.globl _g_hitRight
                             13 	.globl _g_hitLeft
                             14 	.globl _g_jumpRight
                             15 	.globl _g_jumpLeft
                             16 	.globl _g_walkRight
                             17 	.globl _g_walkLeft
                             18 	.globl _g_allAnimFrames
                             19 ;--------------------------------------------------------
                             20 ; special function registers
                             21 ;--------------------------------------------------------
                             22 ;--------------------------------------------------------
                             23 ; ram data
                             24 ;--------------------------------------------------------
                             25 	.area _DATA
                             26 ;--------------------------------------------------------
                             27 ; ram data
                             28 ;--------------------------------------------------------
                             29 	.area _INITIALIZED
                             30 ;--------------------------------------------------------
                             31 ; absolute external ram data
                             32 ;--------------------------------------------------------
                             33 	.area _DABS (ABS)
                             34 ;--------------------------------------------------------
                             35 ; global & static initialisations
                             36 ;--------------------------------------------------------
                             37 	.area _HOME
                             38 	.area _GSINIT
                             39 	.area _GSFINAL
                             40 	.area _GSINIT
                             41 ;--------------------------------------------------------
                             42 ; Home
                             43 ;--------------------------------------------------------
                             44 	.area _HOME
                             45 	.area _HOME
                             46 ;--------------------------------------------------------
                             47 ; code
                             48 ;--------------------------------------------------------
                             49 	.area _CODE
                             50 	.area _CODE
   5D9B                      51 _g_allAnimFrames:
   5D9B FE 60                52 	.dw _G_EMRright
   5D9D 04                   53 	.db #0x04	; 4
   5D9E 10                   54 	.db #0x10	; 16
   5D9F 04                   55 	.db #0x04	; 4
   5DA0 3E 61                56 	.dw _G_EMRright2
   5DA2 02                   57 	.db #0x02	; 2
   5DA3 10                   58 	.db #0x10	; 16
   5DA4 04                   59 	.db #0x04	; 4
   5DA5 9E 61                60 	.dw _G_EMRleft
   5DA7 04                   61 	.db #0x04	; 4
   5DA8 10                   62 	.db #0x10	; 16
   5DA9 04                   63 	.db #0x04	; 4
   5DAA DE 61                64 	.dw _G_EMRleft2
   5DAC 02                   65 	.db #0x02	; 2
   5DAD 10                   66 	.db #0x10	; 16
   5DAE 04                   67 	.db #0x04	; 4
   5DAF 3E 62                68 	.dw _G_EMRjumpright1
   5DB1 04                   69 	.db #0x04	; 4
   5DB2 08                   70 	.db #0x08	; 8
   5DB3 03                   71 	.db #0x03	; 3
   5DB4 5E 62                72 	.dw _G_EMRjumpright2
   5DB6 04                   73 	.db #0x04	; 4
   5DB7 08                   74 	.db #0x08	; 8
   5DB8 04                   75 	.db #0x04	; 4
   5DB9 7E 62                76 	.dw _G_EMRjumpright3
   5DBB 04                   77 	.db #0x04	; 4
   5DBC 08                   78 	.db #0x08	; 8
   5DBD 04                   79 	.db #0x04	; 4
   5DBE 9E 62                80 	.dw _G_EMRjumpright4
   5DC0 04                   81 	.db #0x04	; 4
   5DC1 08                   82 	.db #0x08	; 8
   5DC2 03                   83 	.db #0x03	; 3
   5DC3 BE 62                84 	.dw _G_EMRjumpleft1
   5DC5 04                   85 	.db #0x04	; 4
   5DC6 08                   86 	.db #0x08	; 8
   5DC7 03                   87 	.db #0x03	; 3
   5DC8 DE 62                88 	.dw _G_EMRjumpleft2
   5DCA 04                   89 	.db #0x04	; 4
   5DCB 08                   90 	.db #0x08	; 8
   5DCC 04                   91 	.db #0x04	; 4
   5DCD FE 62                92 	.dw _G_EMRjumpleft3
   5DCF 04                   93 	.db #0x04	; 4
   5DD0 08                   94 	.db #0x08	; 8
   5DD1 04                   95 	.db #0x04	; 4
   5DD2 1E 63                96 	.dw _G_EMRjumpleft4
   5DD4 04                   97 	.db #0x04	; 4
   5DD5 08                   98 	.db #0x08	; 8
   5DD6 03                   99 	.db #0x03	; 3
   5DD7 3E 63               100 	.dw _G_EMRhitright
   5DD9 04                  101 	.db #0x04	; 4
   5DDA 10                  102 	.db #0x10	; 16
   5DDB 06                  103 	.db #0x06	; 6
   5DDC 7E 63               104 	.dw _G_EMRhitleft
   5DDE 04                  105 	.db #0x04	; 4
   5DDF 10                  106 	.db #0x10	; 16
   5DE0 06                  107 	.db #0x06	; 6
   5DE1 5E 61               108 	.dw _G_EMRright3
   5DE3 04                  109 	.db #0x04	; 4
   5DE4 10                  110 	.db #0x10	; 16
   5DE5 04                  111 	.db #0x04	; 4
   5DE6 FE 61               112 	.dw _G_EMRleft3
   5DE8 04                  113 	.db #0x04	; 4
   5DE9 10                  114 	.db #0x10	; 16
   5DEA 04                  115 	.db #0x04	; 4
   5DEB                     116 _g_walkLeft:
   5DEB A5 5D               117 	.dw (_g_allAnimFrames + 10)
   5DED AA 5D               118 	.dw (_g_allAnimFrames + 15)
   5DEF E6 5D               119 	.dw (_g_allAnimFrames + 75)
   5DF1 AA 5D               120 	.dw (_g_allAnimFrames + 15)
   5DF3 00 00               121 	.dw #0x0000
   5DF5                     122 _g_walkRight:
   5DF5 9B 5D               123 	.dw (_g_allAnimFrames + 0)
   5DF7 A0 5D               124 	.dw (_g_allAnimFrames + 5)
   5DF9 E1 5D               125 	.dw (_g_allAnimFrames + 70)
   5DFB A0 5D               126 	.dw (_g_allAnimFrames + 5)
   5DFD 00 00               127 	.dw #0x0000
   5DFF                     128 _g_jumpLeft:
   5DFF C3 5D               129 	.dw (_g_allAnimFrames + 40)
   5E01 C8 5D               130 	.dw (_g_allAnimFrames + 45)
   5E03 CD 5D               131 	.dw (_g_allAnimFrames + 50)
   5E05 D2 5D               132 	.dw (_g_allAnimFrames + 55)
   5E07 AA 5D               133 	.dw (_g_allAnimFrames + 15)
   5E09 00 00               134 	.dw #0x0000
   5E0B                     135 _g_jumpRight:
   5E0B AF 5D               136 	.dw (_g_allAnimFrames + 20)
   5E0D B4 5D               137 	.dw (_g_allAnimFrames + 25)
   5E0F B9 5D               138 	.dw (_g_allAnimFrames + 30)
   5E11 BE 5D               139 	.dw (_g_allAnimFrames + 35)
   5E13 A0 5D               140 	.dw (_g_allAnimFrames + 5)
   5E15 00 00               141 	.dw #0x0000
   5E17                     142 _g_hitLeft:
   5E17 DC 5D               143 	.dw (_g_allAnimFrames + 65)
   5E19 00 00               144 	.dw #0x0000
   5E1B                     145 _g_hitRight:
   5E1B D7 5D               146 	.dw (_g_allAnimFrames + 60)
   5E1D 00 00               147 	.dw #0x0000
   5E1F                     148 _g_anim:
   5E1F 00 00               149 	.dw #0x0000
   5E21 00 00               150 	.dw #0x0000
   5E23 EB 5D               151 	.dw _g_walkLeft
   5E25 F5 5D               152 	.dw _g_walkRight
   5E27 FF 5D               153 	.dw _g_jumpLeft
   5E29 0B 5E               154 	.dw _g_jumpRight
   5E2B 17 5E               155 	.dw _g_hitLeft
   5E2D 1B 5E               156 	.dw _g_hitRight
                            157 	.area _INITIALIZER
                            158 	.area _CABS (ABS)
