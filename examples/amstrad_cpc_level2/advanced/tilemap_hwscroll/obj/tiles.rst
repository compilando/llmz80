                              1 ;--------------------------------------------------------
                              2 ; File Created by SDCC : free open source ANSI-C Compiler
                              3 ; Version 3.6.8 #9946 (Linux)
                              4 ;--------------------------------------------------------
                              5 	.module tiles
                              6 	.optsdcc -mz80
                              7 	
                              8 ;--------------------------------------------------------
                              9 ; Public variables in this module
                             10 ;--------------------------------------------------------
                             11 	.globl _g_tiles_119
                             12 	.globl _g_tiles_118
                             13 	.globl _g_tiles_117
                             14 	.globl _g_tiles_116
                             15 	.globl _g_tiles_115
                             16 	.globl _g_tiles_114
                             17 	.globl _g_tiles_113
                             18 	.globl _g_tiles_112
                             19 	.globl _g_tiles_111
                             20 	.globl _g_tiles_110
                             21 	.globl _g_tiles_109
                             22 	.globl _g_tiles_108
                             23 	.globl _g_tiles_107
                             24 	.globl _g_tiles_106
                             25 	.globl _g_tiles_105
                             26 	.globl _g_tiles_104
                             27 	.globl _g_tiles_103
                             28 	.globl _g_tiles_102
                             29 	.globl _g_tiles_101
                             30 	.globl _g_tiles_100
                             31 	.globl _g_tiles_099
                             32 	.globl _g_tiles_098
                             33 	.globl _g_tiles_097
                             34 	.globl _g_tiles_096
                             35 	.globl _g_tiles_095
                             36 	.globl _g_tiles_094
                             37 	.globl _g_tiles_093
                             38 	.globl _g_tiles_092
                             39 	.globl _g_tiles_091
                             40 	.globl _g_tiles_090
                             41 	.globl _g_tiles_089
                             42 	.globl _g_tiles_088
                             43 	.globl _g_tiles_087
                             44 	.globl _g_tiles_086
                             45 	.globl _g_tiles_085
                             46 	.globl _g_tiles_084
                             47 	.globl _g_tiles_083
                             48 	.globl _g_tiles_082
                             49 	.globl _g_tiles_081
                             50 	.globl _g_tiles_080
                             51 	.globl _g_tiles_079
                             52 	.globl _g_tiles_078
                             53 	.globl _g_tiles_077
                             54 	.globl _g_tiles_076
                             55 	.globl _g_tiles_075
                             56 	.globl _g_tiles_074
                             57 	.globl _g_tiles_073
                             58 	.globl _g_tiles_072
                             59 	.globl _g_tiles_071
                             60 	.globl _g_tiles_070
                             61 	.globl _g_tiles_069
                             62 	.globl _g_tiles_068
                             63 	.globl _g_tiles_067
                             64 	.globl _g_tiles_066
                             65 	.globl _g_tiles_065
                             66 	.globl _g_tiles_064
                             67 	.globl _g_tiles_063
                             68 	.globl _g_tiles_062
                             69 	.globl _g_tiles_061
                             70 	.globl _g_tiles_060
                             71 	.globl _g_tiles_059
                             72 	.globl _g_tiles_058
                             73 	.globl _g_tiles_057
                             74 	.globl _g_tiles_056
                             75 	.globl _g_tiles_055
                             76 	.globl _g_tiles_054
                             77 	.globl _g_tiles_053
                             78 	.globl _g_tiles_052
                             79 	.globl _g_tiles_051
                             80 	.globl _g_tiles_050
                             81 	.globl _g_tiles_049
                             82 	.globl _g_tiles_048
                             83 	.globl _g_tiles_047
                             84 	.globl _g_tiles_046
                             85 	.globl _g_tiles_045
                             86 	.globl _g_tiles_044
                             87 	.globl _g_tiles_043
                             88 	.globl _g_tiles_042
                             89 	.globl _g_tiles_041
                             90 	.globl _g_tiles_040
                             91 	.globl _g_tiles_039
                             92 	.globl _g_tiles_038
                             93 	.globl _g_tiles_037
                             94 	.globl _g_tiles_036
                             95 	.globl _g_tiles_035
                             96 	.globl _g_tiles_034
                             97 	.globl _g_tiles_033
                             98 	.globl _g_tiles_032
                             99 	.globl _g_tiles_031
                            100 	.globl _g_tiles_030
                            101 	.globl _g_tiles_029
                            102 	.globl _g_tiles_028
                            103 	.globl _g_tiles_027
                            104 	.globl _g_tiles_026
                            105 	.globl _g_tiles_025
                            106 	.globl _g_tiles_024
                            107 	.globl _g_tiles_023
                            108 	.globl _g_tiles_022
                            109 	.globl _g_tiles_021
                            110 	.globl _g_tiles_020
                            111 	.globl _g_tiles_019
                            112 	.globl _g_tiles_018
                            113 	.globl _g_tiles_017
                            114 	.globl _g_tiles_016
                            115 	.globl _g_tiles_015
                            116 	.globl _g_tiles_014
                            117 	.globl _g_tiles_013
                            118 	.globl _g_tiles_012
                            119 	.globl _g_tiles_011
                            120 	.globl _g_tiles_010
                            121 	.globl _g_tiles_009
                            122 	.globl _g_tiles_008
                            123 	.globl _g_tiles_007
                            124 	.globl _g_tiles_006
                            125 	.globl _g_tiles_005
                            126 	.globl _g_tiles_004
                            127 	.globl _g_tiles_003
                            128 	.globl _g_tiles_002
                            129 	.globl _g_tiles_001
                            130 	.globl _g_tiles_000
                            131 	.globl _g_tileset
                            132 	.globl _g_palette
                            133 ;--------------------------------------------------------
                            134 ; special function registers
                            135 ;--------------------------------------------------------
                            136 ;--------------------------------------------------------
                            137 ; ram data
                            138 ;--------------------------------------------------------
                            139 	.area _DATA
                            140 ;--------------------------------------------------------
                            141 ; ram data
                            142 ;--------------------------------------------------------
                            143 	.area _INITIALIZED
                            144 ;--------------------------------------------------------
                            145 ; absolute external ram data
                            146 ;--------------------------------------------------------
                            147 	.area _DABS (ABS)
                            148 ;--------------------------------------------------------
                            149 ; global & static initialisations
                            150 ;--------------------------------------------------------
                            151 	.area _HOME
                            152 	.area _GSINIT
                            153 	.area _GSFINAL
                            154 	.area _GSINIT
                            155 ;--------------------------------------------------------
                            156 ; Home
                            157 ;--------------------------------------------------------
                            158 	.area _HOME
                            159 	.area _HOME
                            160 ;--------------------------------------------------------
                            161 ; code
                            162 ;--------------------------------------------------------
                            163 	.area _CODE
                            164 	.area _CODE
   15D0                     165 _g_palette:
   15D0 54                  166 	.db #0x54	; 84	'T'
   15D1 4C                  167 	.db #0x4c	; 76	'L'
   15D2 40                  168 	.db #0x40	; 64
   15D3 46                  169 	.db #0x46	; 70	'F'
   15D4 5E                  170 	.db #0x5e	; 94
   15D5 5C                  171 	.db #0x5c	; 92
   15D6 56                  172 	.db #0x56	; 86	'V'
   15D7 52                  173 	.db #0x52	; 82	'R'
   15D8 4B                  174 	.db #0x4b	; 75	'K'
   15D9 4E                  175 	.db #0x4e	; 78	'N'
   15DA 43                  176 	.db #0x43	; 67	'C'
   15DB 44                  177 	.db #0x44	; 68	'D'
   15DC 5F                  178 	.db #0x5f	; 95
   15DD                     179 _g_tileset:
   15DD CD 16               180 	.dw _g_tiles_000
   15DF D5 16               181 	.dw _g_tiles_001
   15E1 DD 16               182 	.dw _g_tiles_002
   15E3 E5 16               183 	.dw _g_tiles_003
   15E5 ED 16               184 	.dw _g_tiles_004
   15E7 F5 16               185 	.dw _g_tiles_005
   15E9 FD 16               186 	.dw _g_tiles_006
   15EB 05 17               187 	.dw _g_tiles_007
   15ED 0D 17               188 	.dw _g_tiles_008
   15EF 15 17               189 	.dw _g_tiles_009
   15F1 1D 17               190 	.dw _g_tiles_010
   15F3 25 17               191 	.dw _g_tiles_011
   15F5 2D 17               192 	.dw _g_tiles_012
   15F7 35 17               193 	.dw _g_tiles_013
   15F9 3D 17               194 	.dw _g_tiles_014
   15FB 45 17               195 	.dw _g_tiles_015
   15FD 4D 17               196 	.dw _g_tiles_016
   15FF 55 17               197 	.dw _g_tiles_017
   1601 5D 17               198 	.dw _g_tiles_018
   1603 65 17               199 	.dw _g_tiles_019
   1605 6D 17               200 	.dw _g_tiles_020
   1607 75 17               201 	.dw _g_tiles_021
   1609 7D 17               202 	.dw _g_tiles_022
   160B 85 17               203 	.dw _g_tiles_023
   160D 8D 17               204 	.dw _g_tiles_024
   160F 95 17               205 	.dw _g_tiles_025
   1611 9D 17               206 	.dw _g_tiles_026
   1613 A5 17               207 	.dw _g_tiles_027
   1615 AD 17               208 	.dw _g_tiles_028
   1617 B5 17               209 	.dw _g_tiles_029
   1619 BD 17               210 	.dw _g_tiles_030
   161B C5 17               211 	.dw _g_tiles_031
   161D CD 17               212 	.dw _g_tiles_032
   161F D5 17               213 	.dw _g_tiles_033
   1621 DD 17               214 	.dw _g_tiles_034
   1623 E5 17               215 	.dw _g_tiles_035
   1625 ED 17               216 	.dw _g_tiles_036
   1627 F5 17               217 	.dw _g_tiles_037
   1629 FD 17               218 	.dw _g_tiles_038
   162B 05 18               219 	.dw _g_tiles_039
   162D 0D 18               220 	.dw _g_tiles_040
   162F 15 18               221 	.dw _g_tiles_041
   1631 1D 18               222 	.dw _g_tiles_042
   1633 25 18               223 	.dw _g_tiles_043
   1635 2D 18               224 	.dw _g_tiles_044
   1637 35 18               225 	.dw _g_tiles_045
   1639 3D 18               226 	.dw _g_tiles_046
   163B 45 18               227 	.dw _g_tiles_047
   163D 4D 18               228 	.dw _g_tiles_048
   163F 55 18               229 	.dw _g_tiles_049
   1641 5D 18               230 	.dw _g_tiles_050
   1643 65 18               231 	.dw _g_tiles_051
   1645 6D 18               232 	.dw _g_tiles_052
   1647 75 18               233 	.dw _g_tiles_053
   1649 7D 18               234 	.dw _g_tiles_054
   164B 85 18               235 	.dw _g_tiles_055
   164D 8D 18               236 	.dw _g_tiles_056
   164F 95 18               237 	.dw _g_tiles_057
   1651 9D 18               238 	.dw _g_tiles_058
   1653 A5 18               239 	.dw _g_tiles_059
   1655 AD 18               240 	.dw _g_tiles_060
   1657 B5 18               241 	.dw _g_tiles_061
   1659 BD 18               242 	.dw _g_tiles_062
   165B C5 18               243 	.dw _g_tiles_063
   165D CD 18               244 	.dw _g_tiles_064
   165F D5 18               245 	.dw _g_tiles_065
   1661 DD 18               246 	.dw _g_tiles_066
   1663 E5 18               247 	.dw _g_tiles_067
   1665 ED 18               248 	.dw _g_tiles_068
   1667 F5 18               249 	.dw _g_tiles_069
   1669 FD 18               250 	.dw _g_tiles_070
   166B 05 19               251 	.dw _g_tiles_071
   166D 0D 19               252 	.dw _g_tiles_072
   166F 15 19               253 	.dw _g_tiles_073
   1671 1D 19               254 	.dw _g_tiles_074
   1673 25 19               255 	.dw _g_tiles_075
   1675 2D 19               256 	.dw _g_tiles_076
   1677 35 19               257 	.dw _g_tiles_077
   1679 3D 19               258 	.dw _g_tiles_078
   167B 45 19               259 	.dw _g_tiles_079
   167D 4D 19               260 	.dw _g_tiles_080
   167F 55 19               261 	.dw _g_tiles_081
   1681 5D 19               262 	.dw _g_tiles_082
   1683 65 19               263 	.dw _g_tiles_083
   1685 6D 19               264 	.dw _g_tiles_084
   1687 75 19               265 	.dw _g_tiles_085
   1689 7D 19               266 	.dw _g_tiles_086
   168B 85 19               267 	.dw _g_tiles_087
   168D 8D 19               268 	.dw _g_tiles_088
   168F 95 19               269 	.dw _g_tiles_089
   1691 9D 19               270 	.dw _g_tiles_090
   1693 A5 19               271 	.dw _g_tiles_091
   1695 AD 19               272 	.dw _g_tiles_092
   1697 B5 19               273 	.dw _g_tiles_093
   1699 BD 19               274 	.dw _g_tiles_094
   169B C5 19               275 	.dw _g_tiles_095
   169D CD 19               276 	.dw _g_tiles_096
   169F D5 19               277 	.dw _g_tiles_097
   16A1 DD 19               278 	.dw _g_tiles_098
   16A3 E5 19               279 	.dw _g_tiles_099
   16A5 ED 19               280 	.dw _g_tiles_100
   16A7 F5 19               281 	.dw _g_tiles_101
   16A9 FD 19               282 	.dw _g_tiles_102
   16AB 05 1A               283 	.dw _g_tiles_103
   16AD 0D 1A               284 	.dw _g_tiles_104
   16AF 15 1A               285 	.dw _g_tiles_105
   16B1 1D 1A               286 	.dw _g_tiles_106
   16B3 25 1A               287 	.dw _g_tiles_107
   16B5 2D 1A               288 	.dw _g_tiles_108
   16B7 35 1A               289 	.dw _g_tiles_109
   16B9 3D 1A               290 	.dw _g_tiles_110
   16BB 45 1A               291 	.dw _g_tiles_111
   16BD 4D 1A               292 	.dw _g_tiles_112
   16BF 55 1A               293 	.dw _g_tiles_113
   16C1 5D 1A               294 	.dw _g_tiles_114
   16C3 65 1A               295 	.dw _g_tiles_115
   16C5 6D 1A               296 	.dw _g_tiles_116
   16C7 75 1A               297 	.dw _g_tiles_117
   16C9 7D 1A               298 	.dw _g_tiles_118
   16CB 85 1A               299 	.dw _g_tiles_119
   16CD                     300 _g_tiles_000:
   16CD C0                  301 	.db #0xc0	; 192
   16CE C0                  302 	.db #0xc0	; 192
   16CF C0                  303 	.db #0xc0	; 192
   16D0 C0                  304 	.db #0xc0	; 192
   16D1 C0                  305 	.db #0xc0	; 192
   16D2 C0                  306 	.db #0xc0	; 192
   16D3 C0                  307 	.db #0xc0	; 192
   16D4 C0                  308 	.db #0xc0	; 192
   16D5                     309 _g_tiles_001:
   16D5 C0                  310 	.db #0xc0	; 192
   16D6 C0                  311 	.db #0xc0	; 192
   16D7 C0                  312 	.db #0xc0	; 192
   16D8 C0                  313 	.db #0xc0	; 192
   16D9 C0                  314 	.db #0xc0	; 192
   16DA C0                  315 	.db #0xc0	; 192
   16DB C0                  316 	.db #0xc0	; 192
   16DC C0                  317 	.db #0xc0	; 192
   16DD                     318 _g_tiles_002:
   16DD C0                  319 	.db #0xc0	; 192
   16DE C0                  320 	.db #0xc0	; 192
   16DF C0                  321 	.db #0xc0	; 192
   16E0 C0                  322 	.db #0xc0	; 192
   16E1 C0                  323 	.db #0xc0	; 192
   16E2 C0                  324 	.db #0xc0	; 192
   16E3 C0                  325 	.db #0xc0	; 192
   16E4 C0                  326 	.db #0xc0	; 192
   16E5                     327 _g_tiles_003:
   16E5 C0                  328 	.db #0xc0	; 192
   16E6 C0                  329 	.db #0xc0	; 192
   16E7 C0                  330 	.db #0xc0	; 192
   16E8 C0                  331 	.db #0xc0	; 192
   16E9 C0                  332 	.db #0xc0	; 192
   16EA C0                  333 	.db #0xc0	; 192
   16EB C0                  334 	.db #0xc0	; 192
   16EC C0                  335 	.db #0xc0	; 192
   16ED                     336 _g_tiles_004:
   16ED C0                  337 	.db #0xc0	; 192
   16EE C0                  338 	.db #0xc0	; 192
   16EF C0                  339 	.db #0xc0	; 192
   16F0 C0                  340 	.db #0xc0	; 192
   16F1 C0                  341 	.db #0xc0	; 192
   16F2 C0                  342 	.db #0xc0	; 192
   16F3 C0                  343 	.db #0xc0	; 192
   16F4 C0                  344 	.db #0xc0	; 192
   16F5                     345 _g_tiles_005:
   16F5 C0                  346 	.db #0xc0	; 192
   16F6 C0                  347 	.db #0xc0	; 192
   16F7 C0                  348 	.db #0xc0	; 192
   16F8 C0                  349 	.db #0xc0	; 192
   16F9 C0                  350 	.db #0xc0	; 192
   16FA C0                  351 	.db #0xc0	; 192
   16FB C0                  352 	.db #0xc0	; 192
   16FC C0                  353 	.db #0xc0	; 192
   16FD                     354 _g_tiles_006:
   16FD 00                  355 	.db #0x00	; 0
   16FE 4C                  356 	.db #0x4c	; 76	'L'
   16FF 00                  357 	.db #0x00	; 0
   1700 0C                  358 	.db #0x0c	; 12
   1701 00                  359 	.db #0x00	; 0
   1702 44                  360 	.db #0x44	; 68	'D'
   1703 00                  361 	.db #0x00	; 0
   1704 8C                  362 	.db #0x8c	; 140
   1705                     363 _g_tiles_007:
   1705 00                  364 	.db #0x00	; 0
   1706 08                  365 	.db #0x08	; 8
   1707 44                  366 	.db #0x44	; 68	'D'
   1708 08                  367 	.db #0x08	; 8
   1709 0C                  368 	.db #0x0c	; 12
   170A 00                  369 	.db #0x00	; 0
   170B 08                  370 	.db #0x08	; 8
   170C 00                  371 	.db #0x00	; 0
   170D                     372 _g_tiles_008:
   170D 00                  373 	.db #0x00	; 0
   170E 30                  374 	.db #0x30	; 48	'0'
   170F 64                  375 	.db #0x64	; 100	'd'
   1710 28                  376 	.db #0x28	; 40
   1711 44                  377 	.db #0x44	; 68	'D'
   1712 00                  378 	.db #0x00	; 0
   1713 44                  379 	.db #0x44	; 68	'D'
   1714 00                  380 	.db #0x00	; 0
   1715                     381 _g_tiles_009:
   1715 10                  382 	.db #0x10	; 16
   1716 A0                  383 	.db #0xa0	; 160
   1717 10                  384 	.db #0x10	; 16
   1718 20                  385 	.db #0x20	; 32
   1719 10                  386 	.db #0x10	; 16
   171A 20                  387 	.db #0x20	; 32
   171B 10                  388 	.db #0x10	; 16
   171C A0                  389 	.db #0xa0	; 160
   171D                     390 _g_tiles_010:
   171D 00                  391 	.db #0x00	; 0
   171E 0C                  392 	.db #0x0c	; 12
   171F 04                  393 	.db #0x04	; 4
   1720 0C                  394 	.db #0x0c	; 12
   1721 04                  395 	.db #0x04	; 4
   1722 0C                  396 	.db #0x0c	; 12
   1723 04                  397 	.db #0x04	; 4
   1724 00                  398 	.db #0x00	; 0
   1725                     399 _g_tiles_011:
   1725 08                  400 	.db #0x08	; 8
   1726 00                  401 	.db #0x00	; 0
   1727 0C                  402 	.db #0x0c	; 12
   1728 00                  403 	.db #0x00	; 0
   1729 0C                  404 	.db #0x0c	; 12
   172A 88                  405 	.db #0x88	; 136
   172B 04                  406 	.db #0x04	; 4
   172C 88                  407 	.db #0x88	; 136
   172D                     408 _g_tiles_012:
   172D 04                  409 	.db #0x04	; 4
   172E 04                  410 	.db #0x04	; 4
   172F 00                  411 	.db #0x00	; 0
   1730 00                  412 	.db #0x00	; 0
   1731 0C                  413 	.db #0x0c	; 12
   1732 0C                  414 	.db #0x0c	; 12
   1733 00                  415 	.db #0x00	; 0
   1734 00                  416 	.db #0x00	; 0
   1735                     417 _g_tiles_013:
   1735 00                  418 	.db #0x00	; 0
   1736 00                  419 	.db #0x00	; 0
   1737 04                  420 	.db #0x04	; 4
   1738 04                  421 	.db #0x04	; 4
   1739 00                  422 	.db #0x00	; 0
   173A 00                  423 	.db #0x00	; 0
   173B 0C                  424 	.db #0x0c	; 12
   173C 0C                  425 	.db #0x0c	; 12
   173D                     426 _g_tiles_014:
   173D 00                  427 	.db #0x00	; 0
   173E 04                  428 	.db #0x04	; 4
   173F 00                  429 	.db #0x00	; 0
   1740 04                  430 	.db #0x04	; 4
   1741 00                  431 	.db #0x00	; 0
   1742 0C                  432 	.db #0x0c	; 12
   1743 00                  433 	.db #0x00	; 0
   1744 8C                  434 	.db #0x8c	; 140
   1745                     435 _g_tiles_015:
   1745 88                  436 	.db #0x88	; 136
   1746 00                  437 	.db #0x00	; 0
   1747 88                  438 	.db #0x88	; 136
   1748 00                  439 	.db #0x00	; 0
   1749 4C                  440 	.db #0x4c	; 76	'L'
   174A 00                  441 	.db #0x00	; 0
   174B CC                  442 	.db #0xcc	; 204
   174C 00                  443 	.db #0x00	; 0
   174D                     444 _g_tiles_016:
   174D 04                  445 	.db #0x04	; 4
   174E 0C                  446 	.db #0x0c	; 12
   174F 04                  447 	.db #0x04	; 4
   1750 00                  448 	.db #0x00	; 0
   1751 00                  449 	.db #0x00	; 0
   1752 00                  450 	.db #0x00	; 0
   1753 00                  451 	.db #0x00	; 0
   1754 00                  452 	.db #0x00	; 0
   1755                     453 _g_tiles_017:
   1755 08                  454 	.db #0x08	; 8
   1756 00                  455 	.db #0x00	; 0
   1757 4C                  456 	.db #0x4c	; 76	'L'
   1758 00                  457 	.db #0x00	; 0
   1759 0C                  458 	.db #0x0c	; 12
   175A 00                  459 	.db #0x00	; 0
   175B 04                  460 	.db #0x04	; 4
   175C 88                  461 	.db #0x88	; 136
   175D                     462 _g_tiles_018:
   175D 20                  463 	.db #0x20	; 32
   175E 20                  464 	.db #0x20	; 32
   175F B0                  465 	.db #0xb0	; 176
   1760 28                  466 	.db #0x28	; 40
   1761 00                  467 	.db #0x00	; 0
   1762 98                  468 	.db #0x98	; 152
   1763 44                  469 	.db #0x44	; 68	'D'
   1764 50                  470 	.db #0x50	; 80	'P'
   1765                     471 _g_tiles_019:
   1765 B0                  472 	.db #0xb0	; 176
   1766 00                  473 	.db #0x00	; 0
   1767 30                  474 	.db #0x30	; 48	'0'
   1768 00                  475 	.db #0x00	; 0
   1769 70                  476 	.db #0x70	; 112	'p'
   176A 00                  477 	.db #0x00	; 0
   176B 30                  478 	.db #0x30	; 48	'0'
   176C 00                  479 	.db #0x00	; 0
   176D                     480 _g_tiles_020:
   176D 04                  481 	.db #0x04	; 4
   176E 44                  482 	.db #0x44	; 68	'D'
   176F 04                  483 	.db #0x04	; 4
   1770 0C                  484 	.db #0x0c	; 12
   1771 04                  485 	.db #0x04	; 4
   1772 0C                  486 	.db #0x0c	; 12
   1773 04                  487 	.db #0x04	; 4
   1774 04                  488 	.db #0x04	; 4
   1775                     489 _g_tiles_021:
   1775 8C                  490 	.db #0x8c	; 140
   1776 88                  491 	.db #0x88	; 136
   1777 0C                  492 	.db #0x0c	; 12
   1778 88                  493 	.db #0x88	; 136
   1779 0C                  494 	.db #0x0c	; 12
   177A 88                  495 	.db #0x88	; 136
   177B 04                  496 	.db #0x04	; 4
   177C 88                  497 	.db #0x88	; 136
   177D                     498 _g_tiles_022:
   177D 44                  499 	.db #0x44	; 68	'D'
   177E 44                  500 	.db #0x44	; 68	'D'
   177F 04                  501 	.db #0x04	; 4
   1780 04                  502 	.db #0x04	; 4
   1781 04                  503 	.db #0x04	; 4
   1782 04                  504 	.db #0x04	; 4
   1783 04                  505 	.db #0x04	; 4
   1784 04                  506 	.db #0x04	; 4
   1785                     507 _g_tiles_023:
   1785 00                  508 	.db #0x00	; 0
   1786 00                  509 	.db #0x00	; 0
   1787 44                  510 	.db #0x44	; 68	'D'
   1788 44                  511 	.db #0x44	; 68	'D'
   1789 04                  512 	.db #0x04	; 4
   178A 04                  513 	.db #0x04	; 4
   178B 00                  514 	.db #0x00	; 0
   178C 04                  515 	.db #0x04	; 4
   178D                     516 _g_tiles_024:
   178D 00                  517 	.db #0x00	; 0
   178E 04                  518 	.db #0x04	; 4
   178F 00                  519 	.db #0x00	; 0
   1790 04                  520 	.db #0x04	; 4
   1791 00                  521 	.db #0x00	; 0
   1792 00                  522 	.db #0x00	; 0
   1793 44                  523 	.db #0x44	; 68	'D'
   1794 CC                  524 	.db #0xcc	; 204
   1795                     525 _g_tiles_025:
   1795 88                  526 	.db #0x88	; 136
   1796 00                  527 	.db #0x00	; 0
   1797 88                  528 	.db #0x88	; 136
   1798 00                  529 	.db #0x00	; 0
   1799 00                  530 	.db #0x00	; 0
   179A 00                  531 	.db #0x00	; 0
   179B CC                  532 	.db #0xcc	; 204
   179C 00                  533 	.db #0x00	; 0
   179D                     534 _g_tiles_026:
   179D C0                  535 	.db #0xc0	; 192
   179E C0                  536 	.db #0xc0	; 192
   179F C0                  537 	.db #0xc0	; 192
   17A0 C0                  538 	.db #0xc0	; 192
   17A1 C0                  539 	.db #0xc0	; 192
   17A2 C0                  540 	.db #0xc0	; 192
   17A3 C0                  541 	.db #0xc0	; 192
   17A4 C0                  542 	.db #0xc0	; 192
   17A5                     543 _g_tiles_027:
   17A5 C0                  544 	.db #0xc0	; 192
   17A6 C0                  545 	.db #0xc0	; 192
   17A7 C0                  546 	.db #0xc0	; 192
   17A8 C0                  547 	.db #0xc0	; 192
   17A9 C0                  548 	.db #0xc0	; 192
   17AA C0                  549 	.db #0xc0	; 192
   17AB C0                  550 	.db #0xc0	; 192
   17AC C0                  551 	.db #0xc0	; 192
   17AD                     552 _g_tiles_028:
   17AD 44                  553 	.db #0x44	; 68	'D'
   17AE 00                  554 	.db #0x00	; 0
   17AF 00                  555 	.db #0x00	; 0
   17B0 88                  556 	.db #0x88	; 136
   17B1 00                  557 	.db #0x00	; 0
   17B2 88                  558 	.db #0x88	; 136
   17B3 00                  559 	.db #0x00	; 0
   17B4 00                  560 	.db #0x00	; 0
   17B5                     561 _g_tiles_029:
   17B5 30                  562 	.db #0x30	; 48	'0'
   17B6 00                  563 	.db #0x00	; 0
   17B7 10                  564 	.db #0x10	; 16
   17B8 A0                  565 	.db #0xa0	; 160
   17B9 10                  566 	.db #0x10	; 16
   17BA 20                  567 	.db #0x20	; 32
   17BB 10                  568 	.db #0x10	; 16
   17BC 20                  569 	.db #0x20	; 32
   17BD                     570 _g_tiles_030:
   17BD 00                  571 	.db #0x00	; 0
   17BE 88                  572 	.db #0x88	; 136
   17BF CC                  573 	.db #0xcc	; 204
   17C0 44                  574 	.db #0x44	; 68	'D'
   17C1 CC                  575 	.db #0xcc	; 204
   17C2 3C                  576 	.db #0x3c	; 60
   17C3 54                  577 	.db #0x54	; 84	'T'
   17C4 14                  578 	.db #0x14	; 20
   17C5                     579 _g_tiles_031:
   17C5 88                  580 	.db #0x88	; 136
   17C6 00                  581 	.db #0x00	; 0
   17C7 6C                  582 	.db #0x6c	; 108	'l'
   17C8 88                  583 	.db #0x88	; 136
   17C9 9C                  584 	.db #0x9c	; 156
   17CA 44                  585 	.db #0x44	; 68	'D'
   17CB 00                  586 	.db #0x00	; 0
   17CC A8                  587 	.db #0xa8	; 168
   17CD                     588 _g_tiles_032:
   17CD 00                  589 	.db #0x00	; 0
   17CE 00                  590 	.db #0x00	; 0
   17CF 88                  591 	.db #0x88	; 136
   17D0 CC                  592 	.db #0xcc	; 204
   17D1 6C                  593 	.db #0x6c	; 108	'l'
   17D2 28                  594 	.db #0x28	; 40
   17D3 00                  595 	.db #0x00	; 0
   17D4 54                  596 	.db #0x54	; 84	'T'
   17D5                     597 _g_tiles_033:
   17D5 44                  598 	.db #0x44	; 68	'D'
   17D6 00                  599 	.db #0x00	; 0
   17D7 88                  600 	.db #0x88	; 136
   17D8 CC                  601 	.db #0xcc	; 204
   17D9 CC                  602 	.db #0xcc	; 204
   17DA 28                  603 	.db #0x28	; 40
   17DB 00                  604 	.db #0x00	; 0
   17DC 00                  605 	.db #0x00	; 0
   17DD                     606 _g_tiles_034:
   17DD 04                  607 	.db #0x04	; 4
   17DE 0C                  608 	.db #0x0c	; 12
   17DF 04                  609 	.db #0x04	; 4
   17E0 00                  610 	.db #0x00	; 0
   17E1 04                  611 	.db #0x04	; 4
   17E2 44                  612 	.db #0x44	; 68	'D'
   17E3 04                  613 	.db #0x04	; 4
   17E4 0C                  614 	.db #0x0c	; 12
   17E5                     615 _g_tiles_035:
   17E5 0C                  616 	.db #0x0c	; 12
   17E6 88                  617 	.db #0x88	; 136
   17E7 04                  618 	.db #0x04	; 4
   17E8 88                  619 	.db #0x88	; 136
   17E9 8C                  620 	.db #0x8c	; 140
   17EA 88                  621 	.db #0x88	; 136
   17EB 04                  622 	.db #0x04	; 4
   17EC 88                  623 	.db #0x88	; 136
   17ED                     624 _g_tiles_036:
   17ED 00                  625 	.db #0x00	; 0
   17EE 00                  626 	.db #0x00	; 0
   17EF 00                  627 	.db #0x00	; 0
   17F0 00                  628 	.db #0x00	; 0
   17F1 00                  629 	.db #0x00	; 0
   17F2 00                  630 	.db #0x00	; 0
   17F3 00                  631 	.db #0x00	; 0
   17F4 00                  632 	.db #0x00	; 0
   17F5                     633 _g_tiles_037:
   17F5 C0                  634 	.db #0xc0	; 192
   17F6 C0                  635 	.db #0xc0	; 192
   17F7 C0                  636 	.db #0xc0	; 192
   17F8 C0                  637 	.db #0xc0	; 192
   17F9 C0                  638 	.db #0xc0	; 192
   17FA C0                  639 	.db #0xc0	; 192
   17FB C0                  640 	.db #0xc0	; 192
   17FC C0                  641 	.db #0xc0	; 192
   17FD                     642 _g_tiles_038:
   17FD 00                  643 	.db #0x00	; 0
   17FE 10                  644 	.db #0x10	; 16
   17FF 14                  645 	.db #0x14	; 20
   1800 30                  646 	.db #0x30	; 48	'0'
   1801 44                  647 	.db #0x44	; 68	'D'
   1802 A0                  648 	.db #0xa0	; 160
   1803 00                  649 	.db #0x00	; 0
   1804 88                  650 	.db #0x88	; 136
   1805                     651 _g_tiles_039:
   1805 50                  652 	.db #0x50	; 80	'P'
   1806 20                  653 	.db #0x20	; 32
   1807 00                  654 	.db #0x00	; 0
   1808 30                  655 	.db #0x30	; 48	'0'
   1809 00                  656 	.db #0x00	; 0
   180A 30                  657 	.db #0x30	; 48	'0'
   180B 00                  658 	.db #0x00	; 0
   180C B0                  659 	.db #0xb0	; 176
   180D                     660 _g_tiles_040:
   180D FC                  661 	.db #0xfc	; 252
   180E 54                  662 	.db #0x54	; 84	'T'
   180F BC                  663 	.db #0xbc	; 188
   1810 A8                  664 	.db #0xa8	; 168
   1811 54                  665 	.db #0x54	; 84	'T'
   1812 7C                  666 	.db #0x7c	; 124
   1813 BC                  667 	.db #0xbc	; 188
   1814 3C                  668 	.db #0x3c	; 60
   1815                     669 _g_tiles_041:
   1815 28                  670 	.db #0x28	; 40
   1816 28                  671 	.db #0x28	; 40
   1817 A8                  672 	.db #0xa8	; 168
   1818 BC                  673 	.db #0xbc	; 188
   1819 54                  674 	.db #0x54	; 84	'T'
   181A 7C                  675 	.db #0x7c	; 124
   181B 3C                  676 	.db #0x3c	; 60
   181C A8                  677 	.db #0xa8	; 168
   181D                     678 _g_tiles_042:
   181D 3C                  679 	.db #0x3c	; 60
   181E 00                  680 	.db #0x00	; 0
   181F 14                  681 	.db #0x14	; 20
   1820 00                  682 	.db #0x00	; 0
   1821 82                  683 	.db #0x82	; 130
   1822 96                  684 	.db #0x96	; 150
   1823 82                  685 	.db #0x82	; 130
   1824 96                  686 	.db #0x96	; 150
   1825                     687 _g_tiles_043:
   1825 00                  688 	.db #0x00	; 0
   1826 44                  689 	.db #0x44	; 68	'D'
   1827 44                  690 	.db #0x44	; 68	'D'
   1828 03                  691 	.db #0x03	; 3
   1829 01                  692 	.db #0x01	; 1
   182A 03                  693 	.db #0x03	; 3
   182B 01                  694 	.db #0x01	; 1
   182C 0C                  695 	.db #0x0c	; 12
   182D                     696 _g_tiles_044:
   182D 89                  697 	.db #0x89	; 137
   182E 03                  698 	.db #0x03	; 3
   182F 03                  699 	.db #0x03	; 3
   1830 03                  700 	.db #0x03	; 3
   1831 03                  701 	.db #0x03	; 3
   1832 03                  702 	.db #0x03	; 3
   1833 0C                  703 	.db #0x0c	; 12
   1834 0C                  704 	.db #0x0c	; 12
   1835                     705 _g_tiles_045:
   1835 88                  706 	.db #0x88	; 136
   1836 00                  707 	.db #0x00	; 0
   1837 CC                  708 	.db #0xcc	; 204
   1838 00                  709 	.db #0x00	; 0
   1839 03                  710 	.db #0x03	; 3
   183A 88                  711 	.db #0x88	; 136
   183B 09                  712 	.db #0x09	; 9
   183C 88                  713 	.db #0x88	; 136
   183D                     714 _g_tiles_046:
   183D 00                  715 	.db #0x00	; 0
   183E 04                  716 	.db #0x04	; 4
   183F 00                  717 	.db #0x00	; 0
   1840 04                  718 	.db #0x04	; 4
   1841 04                  719 	.db #0x04	; 4
   1842 4C                  720 	.db #0x4c	; 76	'L'
   1843 04                  721 	.db #0x04	; 4
   1844 0C                  722 	.db #0x0c	; 12
   1845                     723 _g_tiles_047:
   1845 08                  724 	.db #0x08	; 8
   1846 00                  725 	.db #0x00	; 0
   1847 08                  726 	.db #0x08	; 8
   1848 00                  727 	.db #0x00	; 0
   1849 0C                  728 	.db #0x0c	; 12
   184A 88                  729 	.db #0x88	; 136
   184B 0C                  730 	.db #0x0c	; 12
   184C 88                  731 	.db #0x88	; 136
   184D                     732 _g_tiles_048:
   184D C0                  733 	.db #0xc0	; 192
   184E C0                  734 	.db #0xc0	; 192
   184F C0                  735 	.db #0xc0	; 192
   1850 C0                  736 	.db #0xc0	; 192
   1851 C0                  737 	.db #0xc0	; 192
   1852 C0                  738 	.db #0xc0	; 192
   1853 C0                  739 	.db #0xc0	; 192
   1854 C0                  740 	.db #0xc0	; 192
   1855                     741 _g_tiles_049:
   1855 C0                  742 	.db #0xc0	; 192
   1856 C0                  743 	.db #0xc0	; 192
   1857 C0                  744 	.db #0xc0	; 192
   1858 C0                  745 	.db #0xc0	; 192
   1859 C0                  746 	.db #0xc0	; 192
   185A C0                  747 	.db #0xc0	; 192
   185B C0                  748 	.db #0xc0	; 192
   185C C0                  749 	.db #0xc0	; 192
   185D                     750 _g_tiles_050:
   185D 3C                  751 	.db #0x3c	; 60
   185E A8                  752 	.db #0xa8	; 168
   185F 3C                  753 	.db #0x3c	; 60
   1860 3C                  754 	.db #0x3c	; 60
   1861 BC                  755 	.db #0xbc	; 188
   1862 7C                  756 	.db #0x7c	; 124
   1863 28                  757 	.db #0x28	; 40
   1864 BC                  758 	.db #0xbc	; 188
   1865                     759 _g_tiles_051:
   1865 BC                  760 	.db #0xbc	; 188
   1866 28                  761 	.db #0x28	; 40
   1867 28                  762 	.db #0x28	; 40
   1868 BC                  763 	.db #0xbc	; 188
   1869 14                  764 	.db #0x14	; 20
   186A 3C                  765 	.db #0x3c	; 60
   186B 14                  766 	.db #0x14	; 20
   186C 3C                  767 	.db #0x3c	; 60
   186D                     768 _g_tiles_052:
   186D 00                  769 	.db #0x00	; 0
   186E 3C                  770 	.db #0x3c	; 60
   186F 14                  771 	.db #0x14	; 20
   1870 28                  772 	.db #0x28	; 40
   1871 41                  773 	.db #0x41	; 65	'A'
   1872 41                  774 	.db #0x41	; 65	'A'
   1873 41                  775 	.db #0x41	; 65	'A'
   1874 05                  776 	.db #0x05	; 5
   1875                     777 _g_tiles_053:
   1875 01                  778 	.db #0x01	; 1
   1876 4C                  779 	.db #0x4c	; 76	'L'
   1877 01                  780 	.db #0x01	; 1
   1878 0C                  781 	.db #0x0c	; 12
   1879 01                  782 	.db #0x01	; 1
   187A 4C                  783 	.db #0x4c	; 76	'L'
   187B 01                  784 	.db #0x01	; 1
   187C CC                  785 	.db #0xcc	; 204
   187D                     786 _g_tiles_054:
   187D CC                  787 	.db #0xcc	; 204
   187E CC                  788 	.db #0xcc	; 204
   187F CC                  789 	.db #0xcc	; 204
   1880 0C                  790 	.db #0x0c	; 12
   1881 CC                  791 	.db #0xcc	; 204
   1882 CC                  792 	.db #0xcc	; 204
   1883 03                  793 	.db #0x03	; 3
   1884 46                  794 	.db #0x46	; 70	'F'
   1885                     795 _g_tiles_055:
   1885 89                  796 	.db #0x89	; 137
   1886 88                  797 	.db #0x88	; 136
   1887 89                  798 	.db #0x89	; 137
   1888 88                  799 	.db #0x88	; 136
   1889 89                  800 	.db #0x89	; 137
   188A 88                  801 	.db #0x88	; 136
   188B 03                  802 	.db #0x03	; 3
   188C 88                  803 	.db #0x88	; 136
   188D                     804 _g_tiles_056:
   188D 00                  805 	.db #0x00	; 0
   188E 04                  806 	.db #0x04	; 4
   188F 00                  807 	.db #0x00	; 0
   1890 04                  808 	.db #0x04	; 4
   1891 00                  809 	.db #0x00	; 0
   1892 44                  810 	.db #0x44	; 68	'D'
   1893 00                  811 	.db #0x00	; 0
   1894 04                  812 	.db #0x04	; 4
   1895                     813 _g_tiles_057:
   1895 08                  814 	.db #0x08	; 8
   1896 00                  815 	.db #0x00	; 0
   1897 08                  816 	.db #0x08	; 8
   1898 00                  817 	.db #0x00	; 0
   1899 08                  818 	.db #0x08	; 8
   189A 00                  819 	.db #0x00	; 0
   189B 08                  820 	.db #0x08	; 8
   189C 00                  821 	.db #0x00	; 0
   189D                     822 _g_tiles_058:
   189D 50                  823 	.db #0x50	; 80	'P'
   189E 00                  824 	.db #0x00	; 0
   189F 0F                  825 	.db #0x0f	; 15
   18A0 0F                  826 	.db #0x0f	; 15
   18A1 50                  827 	.db #0x50	; 80	'P'
   18A2 00                  828 	.db #0x00	; 0
   18A3 05                  829 	.db #0x05	; 5
   18A4 50                  830 	.db #0x50	; 80	'P'
   18A5                     831 _g_tiles_059:
   18A5 00                  832 	.db #0x00	; 0
   18A6 A0                  833 	.db #0xa0	; 160
   18A7 0F                  834 	.db #0x0f	; 15
   18A8 0F                  835 	.db #0x0f	; 15
   18A9 00                  836 	.db #0x00	; 0
   18AA A0                  837 	.db #0xa0	; 160
   18AB A0                  838 	.db #0xa0	; 160
   18AC 0A                  839 	.db #0x0a	; 10
   18AD                     840 _g_tiles_060:
   18AD 3C                  841 	.db #0x3c	; 60
   18AE 14                  842 	.db #0x14	; 20
   18AF 3C                  843 	.db #0x3c	; 60
   18B0 14                  844 	.db #0x14	; 20
   18B1 14                  845 	.db #0x14	; 20
   18B2 28                  846 	.db #0x28	; 40
   18B3 28                  847 	.db #0x28	; 40
   18B4 3C                  848 	.db #0x3c	; 60
   18B5                     849 _g_tiles_061:
   18B5 3C                  850 	.db #0x3c	; 60
   18B6 28                  851 	.db #0x28	; 40
   18B7 28                  852 	.db #0x28	; 40
   18B8 3C                  853 	.db #0x3c	; 60
   18B9 28                  854 	.db #0x28	; 40
   18BA 3C                  855 	.db #0x3c	; 60
   18BB 14                  856 	.db #0x14	; 20
   18BC 14                  857 	.db #0x14	; 20
   18BD                     858 _g_tiles_062:
   18BD 00                  859 	.db #0x00	; 0
   18BE 00                  860 	.db #0x00	; 0
   18BF 00                  861 	.db #0x00	; 0
   18C0 44                  862 	.db #0x44	; 68	'D'
   18C1 00                  863 	.db #0x00	; 0
   18C2 3C                  864 	.db #0x3c	; 60
   18C3 54                  865 	.db #0x54	; 84	'T'
   18C4 14                  866 	.db #0x14	; 20
   18C5                     867 _g_tiles_063:
   18C5 01                  868 	.db #0x01	; 1
   18C6 46                  869 	.db #0x46	; 70	'F'
   18C7 01                  870 	.db #0x01	; 1
   18C8 03                  871 	.db #0x03	; 3
   18C9 01                  872 	.db #0x01	; 1
   18CA 03                  873 	.db #0x03	; 3
   18CB 01                  874 	.db #0x01	; 1
   18CC 28                  875 	.db #0x28	; 40
   18CD                     876 _g_tiles_064:
   18CD 03                  877 	.db #0x03	; 3
   18CE 03                  878 	.db #0x03	; 3
   18CF 03                  879 	.db #0x03	; 3
   18D0 03                  880 	.db #0x03	; 3
   18D1 03                  881 	.db #0x03	; 3
   18D2 03                  882 	.db #0x03	; 3
   18D3 16                  883 	.db #0x16	; 22
   18D4 01                  884 	.db #0x01	; 1
   18D5                     885 _g_tiles_065:
   18D5 89                  886 	.db #0x89	; 137
   18D6 88                  887 	.db #0x88	; 136
   18D7 03                  888 	.db #0x03	; 3
   18D8 88                  889 	.db #0x88	; 136
   18D9 03                  890 	.db #0x03	; 3
   18DA 88                  891 	.db #0x88	; 136
   18DB 44                  892 	.db #0x44	; 68	'D'
   18DC 88                  893 	.db #0x88	; 136
   18DD                     894 _g_tiles_066:
   18DD C0                  895 	.db #0xc0	; 192
   18DE C0                  896 	.db #0xc0	; 192
   18DF C0                  897 	.db #0xc0	; 192
   18E0 C0                  898 	.db #0xc0	; 192
   18E1 C0                  899 	.db #0xc0	; 192
   18E2 C0                  900 	.db #0xc0	; 192
   18E3 C0                  901 	.db #0xc0	; 192
   18E4 C0                  902 	.db #0xc0	; 192
   18E5                     903 _g_tiles_067:
   18E5 C0                  904 	.db #0xc0	; 192
   18E6 C0                  905 	.db #0xc0	; 192
   18E7 C0                  906 	.db #0xc0	; 192
   18E8 C0                  907 	.db #0xc0	; 192
   18E9 C0                  908 	.db #0xc0	; 192
   18EA C0                  909 	.db #0xc0	; 192
   18EB C0                  910 	.db #0xc0	; 192
   18EC C0                  911 	.db #0xc0	; 192
   18ED                     912 _g_tiles_068:
   18ED C0                  913 	.db #0xc0	; 192
   18EE C0                  914 	.db #0xc0	; 192
   18EF C0                  915 	.db #0xc0	; 192
   18F0 C0                  916 	.db #0xc0	; 192
   18F1 C0                  917 	.db #0xc0	; 192
   18F2 C0                  918 	.db #0xc0	; 192
   18F3 C0                  919 	.db #0xc0	; 192
   18F4 C0                  920 	.db #0xc0	; 192
   18F5                     921 _g_tiles_069:
   18F5 C0                  922 	.db #0xc0	; 192
   18F6 C0                  923 	.db #0xc0	; 192
   18F7 C0                  924 	.db #0xc0	; 192
   18F8 C0                  925 	.db #0xc0	; 192
   18F9 C0                  926 	.db #0xc0	; 192
   18FA C0                  927 	.db #0xc0	; 192
   18FB C0                  928 	.db #0xc0	; 192
   18FC C0                  929 	.db #0xc0	; 192
   18FD                     930 _g_tiles_070:
   18FD 28                  931 	.db #0x28	; 40
   18FE 3C                  932 	.db #0x3c	; 60
   18FF 69                  933 	.db #0x69	; 105	'i'
   1900 28                  934 	.db #0x28	; 40
   1901 3C                  935 	.db #0x3c	; 60
   1902 14                  936 	.db #0x14	; 20
   1903 14                  937 	.db #0x14	; 20
   1904 3C                  938 	.db #0x3c	; 60
   1905                     939 _g_tiles_071:
   1905 14                  940 	.db #0x14	; 20
   1906 3C                  941 	.db #0x3c	; 60
   1907 3C                  942 	.db #0x3c	; 60
   1908 28                  943 	.db #0x28	; 40
   1909 14                  944 	.db #0x14	; 20
   190A 28                  945 	.db #0x28	; 40
   190B 14                  946 	.db #0x14	; 20
   190C 96                  947 	.db #0x96	; 150
   190D                     948 _g_tiles_072:
   190D 54                  949 	.db #0x54	; 84	'T'
   190E 54                  950 	.db #0x54	; 84	'T'
   190F BC                  951 	.db #0xbc	; 188
   1910 A8                  952 	.db #0xa8	; 168
   1911 54                  953 	.db #0x54	; 84	'T'
   1912 7C                  954 	.db #0x7c	; 124
   1913 BC                  955 	.db #0xbc	; 188
   1914 3C                  956 	.db #0x3c	; 60
   1915                     957 _g_tiles_073:
   1915 C0                  958 	.db #0xc0	; 192
   1916 C0                  959 	.db #0xc0	; 192
   1917 C0                  960 	.db #0xc0	; 192
   1918 C0                  961 	.db #0xc0	; 192
   1919 C0                  962 	.db #0xc0	; 192
   191A C0                  963 	.db #0xc0	; 192
   191B C0                  964 	.db #0xc0	; 192
   191C C0                  965 	.db #0xc0	; 192
   191D                     966 _g_tiles_074:
   191D C0                  967 	.db #0xc0	; 192
   191E C0                  968 	.db #0xc0	; 192
   191F C0                  969 	.db #0xc0	; 192
   1920 C0                  970 	.db #0xc0	; 192
   1921 C0                  971 	.db #0xc0	; 192
   1922 C0                  972 	.db #0xc0	; 192
   1923 C0                  973 	.db #0xc0	; 192
   1924 C0                  974 	.db #0xc0	; 192
   1925                     975 _g_tiles_075:
   1925 C0                  976 	.db #0xc0	; 192
   1926 C0                  977 	.db #0xc0	; 192
   1927 C0                  978 	.db #0xc0	; 192
   1928 C0                  979 	.db #0xc0	; 192
   1929 C0                  980 	.db #0xc0	; 192
   192A C0                  981 	.db #0xc0	; 192
   192B C0                  982 	.db #0xc0	; 192
   192C C0                  983 	.db #0xc0	; 192
   192D                     984 _g_tiles_076:
   192D 04                  985 	.db #0x04	; 4
   192E 04                  986 	.db #0x04	; 4
   192F 45                  987 	.db #0x45	; 69	'E'
   1930 45                  988 	.db #0x45	; 69	'E'
   1931 11                  989 	.db #0x11	; 17
   1932 11                  990 	.db #0x11	; 17
   1933 44                  991 	.db #0x44	; 68	'D'
   1934 04                  992 	.db #0x04	; 4
   1935                     993 _g_tiles_077:
   1935 00                  994 	.db #0x00	; 0
   1936 08                  995 	.db #0x08	; 8
   1937 04                  996 	.db #0x04	; 4
   1938 4C                  997 	.db #0x4c	; 76	'L'
   1939 00                  998 	.db #0x00	; 0
   193A CC                  999 	.db #0xcc	; 204
   193B 0C                 1000 	.db #0x0c	; 12
   193C 44                 1001 	.db #0x44	; 68	'D'
   193D                    1002 _g_tiles_078:
   193D C0                 1003 	.db #0xc0	; 192
   193E C0                 1004 	.db #0xc0	; 192
   193F C0                 1005 	.db #0xc0	; 192
   1940 C0                 1006 	.db #0xc0	; 192
   1941 C0                 1007 	.db #0xc0	; 192
   1942 C0                 1008 	.db #0xc0	; 192
   1943 C0                 1009 	.db #0xc0	; 192
   1944 C0                 1010 	.db #0xc0	; 192
   1945                    1011 _g_tiles_079:
   1945 C0                 1012 	.db #0xc0	; 192
   1946 C0                 1013 	.db #0xc0	; 192
   1947 C0                 1014 	.db #0xc0	; 192
   1948 C0                 1015 	.db #0xc0	; 192
   1949 C0                 1016 	.db #0xc0	; 192
   194A C0                 1017 	.db #0xc0	; 192
   194B C0                 1018 	.db #0xc0	; 192
   194C C0                 1019 	.db #0xc0	; 192
   194D                    1020 _g_tiles_080:
   194D 3C                 1021 	.db #0x3c	; 60
   194E 3C                 1022 	.db #0x3c	; 60
   194F 3C                 1023 	.db #0x3c	; 60
   1950 00                 1024 	.db #0x00	; 0
   1951 28                 1025 	.db #0x28	; 40
   1952 D2                 1026 	.db #0xd2	; 210
   1953 69                 1027 	.db #0x69	; 105	'i'
   1954 C3                 1028 	.db #0xc3	; 195
   1955                    1029 _g_tiles_081:
   1955 3C                 1030 	.db #0x3c	; 60
   1956 28                 1031 	.db #0x28	; 40
   1957 28                 1032 	.db #0x28	; 40
   1958 82                 1033 	.db #0x82	; 130
   1959 B4                 1034 	.db #0xb4	; 180
   195A C3                 1035 	.db #0xc3	; 195
   195B 82                 1036 	.db #0x82	; 130
   195C 82                 1037 	.db #0x82	; 130
   195D                    1038 _g_tiles_082:
   195D C0                 1039 	.db #0xc0	; 192
   195E C0                 1040 	.db #0xc0	; 192
   195F C0                 1041 	.db #0xc0	; 192
   1960 C0                 1042 	.db #0xc0	; 192
   1961 C0                 1043 	.db #0xc0	; 192
   1962 C0                 1044 	.db #0xc0	; 192
   1963 C0                 1045 	.db #0xc0	; 192
   1964 C0                 1046 	.db #0xc0	; 192
   1965                    1047 _g_tiles_083:
   1965 C0                 1048 	.db #0xc0	; 192
   1966 C0                 1049 	.db #0xc0	; 192
   1967 C0                 1050 	.db #0xc0	; 192
   1968 C0                 1051 	.db #0xc0	; 192
   1969 C0                 1052 	.db #0xc0	; 192
   196A C0                 1053 	.db #0xc0	; 192
   196B C0                 1054 	.db #0xc0	; 192
   196C C0                 1055 	.db #0xc0	; 192
   196D                    1056 _g_tiles_084:
   196D C0                 1057 	.db #0xc0	; 192
   196E C0                 1058 	.db #0xc0	; 192
   196F C0                 1059 	.db #0xc0	; 192
   1970 C0                 1060 	.db #0xc0	; 192
   1971 C0                 1061 	.db #0xc0	; 192
   1972 C0                 1062 	.db #0xc0	; 192
   1973 C0                 1063 	.db #0xc0	; 192
   1974 C0                 1064 	.db #0xc0	; 192
   1975                    1065 _g_tiles_085:
   1975 C0                 1066 	.db #0xc0	; 192
   1976 C0                 1067 	.db #0xc0	; 192
   1977 C0                 1068 	.db #0xc0	; 192
   1978 C0                 1069 	.db #0xc0	; 192
   1979 C0                 1070 	.db #0xc0	; 192
   197A C0                 1071 	.db #0xc0	; 192
   197B C0                 1072 	.db #0xc0	; 192
   197C C0                 1073 	.db #0xc0	; 192
   197D                    1074 _g_tiles_086:
   197D 00                 1075 	.db #0x00	; 0
   197E 00                 1076 	.db #0x00	; 0
   197F 00                 1077 	.db #0x00	; 0
   1980 04                 1078 	.db #0x04	; 4
   1981 00                 1079 	.db #0x00	; 0
   1982 04                 1080 	.db #0x04	; 4
   1983 00                 1081 	.db #0x00	; 0
   1984 04                 1082 	.db #0x04	; 4
   1985                    1083 _g_tiles_087:
   1985 08                 1084 	.db #0x08	; 8
   1986 88                 1085 	.db #0x88	; 136
   1987 04                 1086 	.db #0x04	; 4
   1988 4C                 1087 	.db #0x4c	; 76	'L'
   1989 04                 1088 	.db #0x04	; 4
   198A 0C                 1089 	.db #0x0c	; 12
   198B 88                 1090 	.db #0x88	; 136
   198C CC                 1091 	.db #0xcc	; 204
   198D                    1092 _g_tiles_088:
   198D 88                 1093 	.db #0x88	; 136
   198E 00                 1094 	.db #0x00	; 0
   198F 88                 1095 	.db #0x88	; 136
   1990 00                 1096 	.db #0x00	; 0
   1991 88                 1097 	.db #0x88	; 136
   1992 00                 1098 	.db #0x00	; 0
   1993 00                 1099 	.db #0x00	; 0
   1994 00                 1100 	.db #0x00	; 0
   1995                    1101 _g_tiles_089:
   1995 C0                 1102 	.db #0xc0	; 192
   1996 C0                 1103 	.db #0xc0	; 192
   1997 C0                 1104 	.db #0xc0	; 192
   1998 C0                 1105 	.db #0xc0	; 192
   1999 C0                 1106 	.db #0xc0	; 192
   199A C0                 1107 	.db #0xc0	; 192
   199B C0                 1108 	.db #0xc0	; 192
   199C C0                 1109 	.db #0xc0	; 192
   199D                    1110 _g_tiles_090:
   199D 00                 1111 	.db #0x00	; 0
   199E C3                 1112 	.db #0xc3	; 195
   199F 69                 1113 	.db #0x69	; 105	'i'
   19A0 28                 1114 	.db #0x28	; 40
   19A1 41                 1115 	.db #0x41	; 65	'A'
   19A2 41                 1116 	.db #0x41	; 65	'A'
   19A3 69                 1117 	.db #0x69	; 105	'i'
   19A4 05                 1118 	.db #0x05	; 5
   19A5                    1119 _g_tiles_091:
   19A5 D2                 1120 	.db #0xd2	; 210
   19A6 05                 1121 	.db #0x05	; 5
   19A7 14                 1122 	.db #0x14	; 20
   19A8 41                 1123 	.db #0x41	; 65	'A'
   19A9 A0                 1124 	.db #0xa0	; 160
   19AA 4B                 1125 	.db #0x4b	; 75	'K'
   19AB 82                 1126 	.db #0x82	; 130
   19AC 96                 1127 	.db #0x96	; 150
   19AD                    1128 _g_tiles_092:
   19AD C0                 1129 	.db #0xc0	; 192
   19AE C0                 1130 	.db #0xc0	; 192
   19AF C0                 1131 	.db #0xc0	; 192
   19B0 C0                 1132 	.db #0xc0	; 192
   19B1 C0                 1133 	.db #0xc0	; 192
   19B2 C0                 1134 	.db #0xc0	; 192
   19B3 C0                 1135 	.db #0xc0	; 192
   19B4 C0                 1136 	.db #0xc0	; 192
   19B5                    1137 _g_tiles_093:
   19B5 C0                 1138 	.db #0xc0	; 192
   19B6 C0                 1139 	.db #0xc0	; 192
   19B7 C0                 1140 	.db #0xc0	; 192
   19B8 C0                 1141 	.db #0xc0	; 192
   19B9 C0                 1142 	.db #0xc0	; 192
   19BA C0                 1143 	.db #0xc0	; 192
   19BB C0                 1144 	.db #0xc0	; 192
   19BC C0                 1145 	.db #0xc0	; 192
   19BD                    1146 _g_tiles_094:
   19BD C0                 1147 	.db #0xc0	; 192
   19BE C0                 1148 	.db #0xc0	; 192
   19BF C0                 1149 	.db #0xc0	; 192
   19C0 C0                 1150 	.db #0xc0	; 192
   19C1 C0                 1151 	.db #0xc0	; 192
   19C2 C0                 1152 	.db #0xc0	; 192
   19C3 C0                 1153 	.db #0xc0	; 192
   19C4 C0                 1154 	.db #0xc0	; 192
   19C5                    1155 _g_tiles_095:
   19C5 C0                 1156 	.db #0xc0	; 192
   19C6 C0                 1157 	.db #0xc0	; 192
   19C7 C0                 1158 	.db #0xc0	; 192
   19C8 C0                 1159 	.db #0xc0	; 192
   19C9 C0                 1160 	.db #0xc0	; 192
   19CA C0                 1161 	.db #0xc0	; 192
   19CB C0                 1162 	.db #0xc0	; 192
   19CC C0                 1163 	.db #0xc0	; 192
   19CD                    1164 _g_tiles_096:
   19CD 00                 1165 	.db #0x00	; 0
   19CE 04                 1166 	.db #0x04	; 4
   19CF 00                 1167 	.db #0x00	; 0
   19D0 0C                 1168 	.db #0x0c	; 12
   19D1 00                 1169 	.db #0x00	; 0
   19D2 0C                 1170 	.db #0x0c	; 12
   19D3 04                 1171 	.db #0x04	; 4
   19D4 04                 1172 	.db #0x04	; 4
   19D5                    1173 _g_tiles_097:
   19D5 4C                 1174 	.db #0x4c	; 76	'L'
   19D6 00                 1175 	.db #0x00	; 0
   19D7 4C                 1176 	.db #0x4c	; 76	'L'
   19D8 44                 1177 	.db #0x44	; 68	'D'
   19D9 0C                 1178 	.db #0x0c	; 12
   19DA 88                 1179 	.db #0x88	; 136
   19DB 0C                 1180 	.db #0x0c	; 12
   19DC 88                 1181 	.db #0x88	; 136
   19DD                    1182 _g_tiles_098:
   19DD CC                 1183 	.db #0xcc	; 204
   19DE 00                 1184 	.db #0x00	; 0
   19DF 4C                 1185 	.db #0x4c	; 76	'L'
   19E0 00                 1186 	.db #0x00	; 0
   19E1 0C                 1187 	.db #0x0c	; 12
   19E2 88                 1188 	.db #0x88	; 136
   19E3 0C                 1189 	.db #0x0c	; 12
   19E4 4C                 1190 	.db #0x4c	; 76	'L'
   19E5                    1191 _g_tiles_099:
   19E5 00                 1192 	.db #0x00	; 0
   19E6 00                 1193 	.db #0x00	; 0
   19E7 88                 1194 	.db #0x88	; 136
   19E8 00                 1195 	.db #0x00	; 0
   19E9 4C                 1196 	.db #0x4c	; 76	'L'
   19EA 00                 1197 	.db #0x00	; 0
   19EB 0C                 1198 	.db #0x0c	; 12
   19EC CC                 1199 	.db #0xcc	; 204
   19ED                    1200 _g_tiles_100:
   19ED 82                 1201 	.db #0x82	; 130
   19EE C3                 1202 	.db #0xc3	; 195
   19EF 82                 1203 	.db #0x82	; 130
   19F0 4B                 1204 	.db #0x4b	; 75	'K'
   19F1 28                 1205 	.db #0x28	; 40
   19F2 C3                 1206 	.db #0xc3	; 195
   19F3 82                 1207 	.db #0x82	; 130
   19F4 4B                 1208 	.db #0x4b	; 75	'K'
   19F5                    1209 _g_tiles_101:
   19F5 D2                 1210 	.db #0xd2	; 210
   19F6 41                 1211 	.db #0x41	; 65	'A'
   19F7 C3                 1212 	.db #0xc3	; 195
   19F8 41                 1213 	.db #0x41	; 65	'A'
   19F9 82                 1214 	.db #0x82	; 130
   19FA 00                 1215 	.db #0x00	; 0
   19FB 82                 1216 	.db #0x82	; 130
   19FC 0A                 1217 	.db #0x0a	; 10
   19FD                    1218 _g_tiles_102:
   19FD C0                 1219 	.db #0xc0	; 192
   19FE C0                 1220 	.db #0xc0	; 192
   19FF C0                 1221 	.db #0xc0	; 192
   1A00 C0                 1222 	.db #0xc0	; 192
   1A01 C0                 1223 	.db #0xc0	; 192
   1A02 C0                 1224 	.db #0xc0	; 192
   1A03 C0                 1225 	.db #0xc0	; 192
   1A04 C0                 1226 	.db #0xc0	; 192
   1A05                    1227 _g_tiles_103:
   1A05 C0                 1228 	.db #0xc0	; 192
   1A06 C0                 1229 	.db #0xc0	; 192
   1A07 C0                 1230 	.db #0xc0	; 192
   1A08 C0                 1231 	.db #0xc0	; 192
   1A09 C0                 1232 	.db #0xc0	; 192
   1A0A C0                 1233 	.db #0xc0	; 192
   1A0B C0                 1234 	.db #0xc0	; 192
   1A0C C0                 1235 	.db #0xc0	; 192
   1A0D                    1236 _g_tiles_104:
   1A0D C0                 1237 	.db #0xc0	; 192
   1A0E C0                 1238 	.db #0xc0	; 192
   1A0F C0                 1239 	.db #0xc0	; 192
   1A10 C0                 1240 	.db #0xc0	; 192
   1A11 C0                 1241 	.db #0xc0	; 192
   1A12 C0                 1242 	.db #0xc0	; 192
   1A13 C0                 1243 	.db #0xc0	; 192
   1A14 C0                 1244 	.db #0xc0	; 192
   1A15                    1245 _g_tiles_105:
   1A15 00                 1246 	.db #0x00	; 0
   1A16 00                 1247 	.db #0x00	; 0
   1A17 00                 1248 	.db #0x00	; 0
   1A18 00                 1249 	.db #0x00	; 0
   1A19 00                 1250 	.db #0x00	; 0
   1A1A 04                 1251 	.db #0x04	; 4
   1A1B 00                 1252 	.db #0x00	; 0
   1A1C 0C                 1253 	.db #0x0c	; 12
   1A1D                    1254 _g_tiles_106:
   1A1D 04                 1255 	.db #0x04	; 4
   1A1E 44                 1256 	.db #0x44	; 68	'D'
   1A1F 0C                 1257 	.db #0x0c	; 12
   1A20 88                 1258 	.db #0x88	; 136
   1A21 0C                 1259 	.db #0x0c	; 12
   1A22 88                 1260 	.db #0x88	; 136
   1A23 0C                 1261 	.db #0x0c	; 12
   1A24 4C                 1262 	.db #0x4c	; 76	'L'
   1A25                    1263 _g_tiles_107:
   1A25 0C                 1264 	.db #0x0c	; 12
   1A26 44                 1265 	.db #0x44	; 68	'D'
   1A27 4C                 1266 	.db #0x4c	; 76	'L'
   1A28 04                 1267 	.db #0x04	; 4
   1A29 88                 1268 	.db #0x88	; 136
   1A2A 0C                 1269 	.db #0x0c	; 12
   1A2B 04                 1270 	.db #0x04	; 4
   1A2C 0C                 1271 	.db #0x0c	; 12
   1A2D                    1272 _g_tiles_108:
   1A2D 04                 1273 	.db #0x04	; 4
   1A2E 4C                 1274 	.db #0x4c	; 76	'L'
   1A2F 88                 1275 	.db #0x88	; 136
   1A30 88                 1276 	.db #0x88	; 136
   1A31 88                 1277 	.db #0x88	; 136
   1A32 04                 1278 	.db #0x04	; 4
   1A33 88                 1279 	.db #0x88	; 136
   1A34 0C                 1280 	.db #0x0c	; 12
   1A35                    1281 _g_tiles_109:
   1A35 00                 1282 	.db #0x00	; 0
   1A36 00                 1283 	.db #0x00	; 0
   1A37 00                 1284 	.db #0x00	; 0
   1A38 00                 1285 	.db #0x00	; 0
   1A39 88                 1286 	.db #0x88	; 136
   1A3A 00                 1287 	.db #0x00	; 0
   1A3B 88                 1288 	.db #0x88	; 136
   1A3C 00                 1289 	.db #0x00	; 0
   1A3D                    1290 _g_tiles_110:
   1A3D 41                 1291 	.db #0x41	; 65	'A'
   1A3E C3                 1292 	.db #0xc3	; 195
   1A3F 41                 1293 	.db #0x41	; 65	'A'
   1A40 82                 1294 	.db #0x82	; 130
   1A41 41                 1295 	.db #0x41	; 65	'A'
   1A42 41                 1296 	.db #0x41	; 65	'A'
   1A43 00                 1297 	.db #0x00	; 0
   1A44 05                 1298 	.db #0x05	; 5
   1A45                    1299 _g_tiles_111:
   1A45 05                 1300 	.db #0x05	; 5
   1A46 C3                 1301 	.db #0xc3	; 195
   1A47 41                 1302 	.db #0x41	; 65	'A'
   1A48 C3                 1303 	.db #0xc3	; 195
   1A49 0A                 1304 	.db #0x0a	; 10
   1A4A C3                 1305 	.db #0xc3	; 195
   1A4B 82                 1306 	.db #0x82	; 130
   1A4C C3                 1307 	.db #0xc3	; 195
   1A4D                    1308 _g_tiles_112:
   1A4D 41                 1309 	.db #0x41	; 65	'A'
   1A4E C3                 1310 	.db #0xc3	; 195
   1A4F 50                 1311 	.db #0x50	; 80	'P'
   1A50 82                 1312 	.db #0x82	; 130
   1A51 50                 1313 	.db #0x50	; 80	'P'
   1A52 50                 1314 	.db #0x50	; 80	'P'
   1A53 00                 1315 	.db #0x00	; 0
   1A54 00                 1316 	.db #0x00	; 0
   1A55                    1317 _g_tiles_113:
   1A55 05                 1318 	.db #0x05	; 5
   1A56 C3                 1319 	.db #0xc3	; 195
   1A57 41                 1320 	.db #0x41	; 65	'A'
   1A58 E1                 1321 	.db #0xe1	; 225
   1A59 A0                 1322 	.db #0xa0	; 160
   1A5A F0                 1323 	.db #0xf0	; 240
   1A5B 00                 1324 	.db #0x00	; 0
   1A5C 00                 1325 	.db #0x00	; 0
   1A5D                    1326 _g_tiles_114:
   1A5D C0                 1327 	.db #0xc0	; 192
   1A5E C0                 1328 	.db #0xc0	; 192
   1A5F C0                 1329 	.db #0xc0	; 192
   1A60 C0                 1330 	.db #0xc0	; 192
   1A61 C0                 1331 	.db #0xc0	; 192
   1A62 C0                 1332 	.db #0xc0	; 192
   1A63 C0                 1333 	.db #0xc0	; 192
   1A64 C0                 1334 	.db #0xc0	; 192
   1A65                    1335 _g_tiles_115:
   1A65 04                 1336 	.db #0x04	; 4
   1A66 0C                 1337 	.db #0x0c	; 12
   1A67 04                 1338 	.db #0x04	; 4
   1A68 08                 1339 	.db #0x08	; 8
   1A69 04                 1340 	.db #0x04	; 4
   1A6A 00                 1341 	.db #0x00	; 0
   1A6B 4C                 1342 	.db #0x4c	; 76	'L'
   1A6C 00                 1343 	.db #0x00	; 0
   1A6D                    1344 _g_tiles_116:
   1A6D 0C                 1345 	.db #0x0c	; 12
   1A6E 0C                 1346 	.db #0x0c	; 12
   1A6F 8C                 1347 	.db #0x8c	; 140
   1A70 04                 1348 	.db #0x04	; 4
   1A71 08                 1349 	.db #0x08	; 8
   1A72 CC                 1350 	.db #0xcc	; 204
   1A73 88                 1351 	.db #0x88	; 136
   1A74 00                 1352 	.db #0x00	; 0
   1A75                    1353 _g_tiles_117:
   1A75 8C                 1354 	.db #0x8c	; 140
   1A76 0C                 1355 	.db #0x0c	; 12
   1A77 88                 1356 	.db #0x88	; 136
   1A78 0C                 1357 	.db #0x0c	; 12
   1A79 00                 1358 	.db #0x00	; 0
   1A7A 44                 1359 	.db #0x44	; 68	'D'
   1A7B 00                 1360 	.db #0x00	; 0
   1A7C 00                 1361 	.db #0x00	; 0
   1A7D                    1362 _g_tiles_118:
   1A7D 4C                 1363 	.db #0x4c	; 76	'L'
   1A7E 04                 1364 	.db #0x04	; 4
   1A7F 4C                 1365 	.db #0x4c	; 76	'L'
   1A80 CC                 1366 	.db #0xcc	; 204
   1A81 88                 1367 	.db #0x88	; 136
   1A82 00                 1368 	.db #0x00	; 0
   1A83 00                 1369 	.db #0x00	; 0
   1A84 00                 1370 	.db #0x00	; 0
   1A85                    1371 _g_tiles_119:
   1A85 4C                 1372 	.db #0x4c	; 76	'L'
   1A86 00                 1373 	.db #0x00	; 0
   1A87 4C                 1374 	.db #0x4c	; 76	'L'
   1A88 88                 1375 	.db #0x88	; 136
   1A89 88                 1376 	.db #0x88	; 136
   1A8A 88                 1377 	.db #0x88	; 136
   1A8B 00                 1378 	.db #0x00	; 0
   1A8C 04                 1379 	.db #0x04	; 4
                           1380 	.area _INITIALIZER
                           1381 	.area _CABS (ABS)
