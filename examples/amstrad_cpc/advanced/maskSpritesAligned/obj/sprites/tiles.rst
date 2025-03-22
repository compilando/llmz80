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
                             11 	.globl _g_tiles_24
                             12 	.globl _g_tiles_23
                             13 	.globl _g_tiles_22
                             14 	.globl _g_tiles_21
                             15 	.globl _g_tiles_20
                             16 	.globl _g_tiles_19
                             17 	.globl _g_tiles_18
                             18 	.globl _g_tiles_17
                             19 	.globl _g_tiles_16
                             20 	.globl _g_tiles_15
                             21 	.globl _g_tiles_14
                             22 	.globl _g_tiles_13
                             23 	.globl _g_tiles_12
                             24 	.globl _g_tiles_11
                             25 	.globl _g_tiles_10
                             26 	.globl _g_tiles_09
                             27 	.globl _g_tiles_08
                             28 	.globl _g_tiles_07
                             29 	.globl _g_tiles_06
                             30 	.globl _g_tiles_05
                             31 	.globl _g_tiles_04
                             32 	.globl _g_tiles_03
                             33 	.globl _g_tiles_02
                             34 	.globl _g_tiles_01
                             35 	.globl _g_tiles_00
                             36 	.globl _g_tileset
                             37 ;--------------------------------------------------------
                             38 ; special function registers
                             39 ;--------------------------------------------------------
                             40 ;--------------------------------------------------------
                             41 ; ram data
                             42 ;--------------------------------------------------------
                             43 	.area _DATA
                             44 ;--------------------------------------------------------
                             45 ; ram data
                             46 ;--------------------------------------------------------
                             47 	.area _INITIALIZED
                             48 ;--------------------------------------------------------
                             49 ; absolute external ram data
                             50 ;--------------------------------------------------------
                             51 	.area _DABS (ABS)
                             52 ;--------------------------------------------------------
                             53 ; global & static initialisations
                             54 ;--------------------------------------------------------
                             55 	.area _HOME
                             56 	.area _GSINIT
                             57 	.area _GSFINAL
                             58 	.area _GSINIT
                             59 ;--------------------------------------------------------
                             60 ; Home
                             61 ;--------------------------------------------------------
                             62 	.area _HOME
                             63 	.area _HOME
                             64 ;--------------------------------------------------------
                             65 ; code
                             66 ;--------------------------------------------------------
                             67 	.area _CODE
                             68 	.area _CODE
   09D0                      69 _g_tileset:
   09D0 02 0A                70 	.dw _g_tiles_00
   09D2 0A 0A                71 	.dw _g_tiles_01
   09D4 12 0A                72 	.dw _g_tiles_02
   09D6 1A 0A                73 	.dw _g_tiles_03
   09D8 22 0A                74 	.dw _g_tiles_04
   09DA 2A 0A                75 	.dw _g_tiles_05
   09DC 32 0A                76 	.dw _g_tiles_06
   09DE 3A 0A                77 	.dw _g_tiles_07
   09E0 42 0A                78 	.dw _g_tiles_08
   09E2 4A 0A                79 	.dw _g_tiles_09
   09E4 52 0A                80 	.dw _g_tiles_10
   09E6 5A 0A                81 	.dw _g_tiles_11
   09E8 62 0A                82 	.dw _g_tiles_12
   09EA 6A 0A                83 	.dw _g_tiles_13
   09EC 72 0A                84 	.dw _g_tiles_14
   09EE 7A 0A                85 	.dw _g_tiles_15
   09F0 82 0A                86 	.dw _g_tiles_16
   09F2 8A 0A                87 	.dw _g_tiles_17
   09F4 92 0A                88 	.dw _g_tiles_18
   09F6 9A 0A                89 	.dw _g_tiles_19
   09F8 A2 0A                90 	.dw _g_tiles_20
   09FA AA 0A                91 	.dw _g_tiles_21
   09FC B2 0A                92 	.dw _g_tiles_22
   09FE BA 0A                93 	.dw _g_tiles_23
   0A00 C2 0A                94 	.dw _g_tiles_24
   0A02                      95 _g_tiles_00:
   0A02 00                   96 	.db #0x00	; 0
   0A03 00                   97 	.db #0x00	; 0
   0A04 00                   98 	.db #0x00	; 0
   0A05 C0                   99 	.db #0xc0	; 192
   0A06 C0                  100 	.db #0xc0	; 192
   0A07 C0                  101 	.db #0xc0	; 192
   0A08 C0                  102 	.db #0xc0	; 192
   0A09 C0                  103 	.db #0xc0	; 192
   0A0A                     104 _g_tiles_01:
   0A0A C0                  105 	.db #0xc0	; 192
   0A0B C0                  106 	.db #0xc0	; 192
   0A0C C0                  107 	.db #0xc0	; 192
   0A0D C0                  108 	.db #0xc0	; 192
   0A0E C0                  109 	.db #0xc0	; 192
   0A0F C0                  110 	.db #0xc0	; 192
   0A10 C0                  111 	.db #0xc0	; 192
   0A11 C0                  112 	.db #0xc0	; 192
   0A12                     113 _g_tiles_02:
   0A12 00                  114 	.db #0x00	; 0
   0A13 00                  115 	.db #0x00	; 0
   0A14 C0                  116 	.db #0xc0	; 192
   0A15 00                  117 	.db #0x00	; 0
   0A16 C0                  118 	.db #0xc0	; 192
   0A17 C0                  119 	.db #0xc0	; 192
   0A18 C0                  120 	.db #0xc0	; 192
   0A19 C0                  121 	.db #0xc0	; 192
   0A1A                     122 _g_tiles_03:
   0A1A 00                  123 	.db #0x00	; 0
   0A1B 00                  124 	.db #0x00	; 0
   0A1C C0                  125 	.db #0xc0	; 192
   0A1D C0                  126 	.db #0xc0	; 192
   0A1E C0                  127 	.db #0xc0	; 192
   0A1F C0                  128 	.db #0xc0	; 192
   0A20 C0                  129 	.db #0xc0	; 192
   0A21 C0                  130 	.db #0xc0	; 192
   0A22                     131 _g_tiles_04:
   0A22 00                  132 	.db #0x00	; 0
   0A23 00                  133 	.db #0x00	; 0
   0A24 00                  134 	.db #0x00	; 0
   0A25 00                  135 	.db #0x00	; 0
   0A26 C0                  136 	.db #0xc0	; 192
   0A27 C0                  137 	.db #0xc0	; 192
   0A28 C0                  138 	.db #0xc0	; 192
   0A29 C0                  139 	.db #0xc0	; 192
   0A2A                     140 _g_tiles_05:
   0A2A 0C                  141 	.db #0x0c	; 12
   0A2B 0C                  142 	.db #0x0c	; 12
   0A2C 08                  143 	.db #0x08	; 8
   0A2D 04                  144 	.db #0x04	; 4
   0A2E 08                  145 	.db #0x08	; 8
   0A2F 04                  146 	.db #0x04	; 4
   0A30 0C                  147 	.db #0x0c	; 12
   0A31 0C                  148 	.db #0x0c	; 12
   0A32                     149 _g_tiles_06:
   0A32 0C                  150 	.db #0x0c	; 12
   0A33 0C                  151 	.db #0x0c	; 12
   0A34 00                  152 	.db #0x00	; 0
   0A35 00                  153 	.db #0x00	; 0
   0A36 00                  154 	.db #0x00	; 0
   0A37 00                  155 	.db #0x00	; 0
   0A38 00                  156 	.db #0x00	; 0
   0A39 00                  157 	.db #0x00	; 0
   0A3A                     158 _g_tiles_07:
   0A3A 0C                  159 	.db #0x0c	; 12
   0A3B 0C                  160 	.db #0x0c	; 12
   0A3C 08                  161 	.db #0x08	; 8
   0A3D 04                  162 	.db #0x04	; 4
   0A3E 0C                  163 	.db #0x0c	; 12
   0A3F 0C                  164 	.db #0x0c	; 12
   0A40 0C                  165 	.db #0x0c	; 12
   0A41 0C                  166 	.db #0x0c	; 12
   0A42                     167 _g_tiles_08:
   0A42 0C                  168 	.db #0x0c	; 12
   0A43 0C                  169 	.db #0x0c	; 12
   0A44 08                  170 	.db #0x08	; 8
   0A45 04                  171 	.db #0x04	; 4
   0A46 08                  172 	.db #0x08	; 8
   0A47 0C                  173 	.db #0x0c	; 12
   0A48 0C                  174 	.db #0x0c	; 12
   0A49 0C                  175 	.db #0x0c	; 12
   0A4A                     176 _g_tiles_09:
   0A4A 0C                  177 	.db #0x0c	; 12
   0A4B 0C                  178 	.db #0x0c	; 12
   0A4C 0C                  179 	.db #0x0c	; 12
   0A4D 04                  180 	.db #0x04	; 4
   0A4E 08                  181 	.db #0x08	; 8
   0A4F 04                  182 	.db #0x04	; 4
   0A50 0C                  183 	.db #0x0c	; 12
   0A51 0C                  184 	.db #0x0c	; 12
   0A52                     185 _g_tiles_10:
   0A52 0C                  186 	.db #0x0c	; 12
   0A53 0C                  187 	.db #0x0c	; 12
   0A54 0C                  188 	.db #0x0c	; 12
   0A55 0C                  189 	.db #0x0c	; 12
   0A56 0C                  190 	.db #0x0c	; 12
   0A57 0C                  191 	.db #0x0c	; 12
   0A58 0C                  192 	.db #0x0c	; 12
   0A59 0C                  193 	.db #0x0c	; 12
   0A5A                     194 _g_tiles_11:
   0A5A 00                  195 	.db #0x00	; 0
   0A5B 00                  196 	.db #0x00	; 0
   0A5C 00                  197 	.db #0x00	; 0
   0A5D 00                  198 	.db #0x00	; 0
   0A5E 00                  199 	.db #0x00	; 0
   0A5F 00                  200 	.db #0x00	; 0
   0A60 00                  201 	.db #0x00	; 0
   0A61 00                  202 	.db #0x00	; 0
   0A62                     203 _g_tiles_12:
   0A62 00                  204 	.db #0x00	; 0
   0A63 00                  205 	.db #0x00	; 0
   0A64 00                  206 	.db #0x00	; 0
   0A65 00                  207 	.db #0x00	; 0
   0A66 80                  208 	.db #0x80	; 128
   0A67 80                  209 	.db #0x80	; 128
   0A68 C0                  210 	.db #0xc0	; 192
   0A69 C0                  211 	.db #0xc0	; 192
   0A6A                     212 _g_tiles_13:
   0A6A 04                  213 	.db #0x04	; 4
   0A6B 00                  214 	.db #0x00	; 0
   0A6C 00                  215 	.db #0x00	; 0
   0A6D 00                  216 	.db #0x00	; 0
   0A6E 08                  217 	.db #0x08	; 8
   0A6F 04                  218 	.db #0x04	; 4
   0A70 00                  219 	.db #0x00	; 0
   0A71 00                  220 	.db #0x00	; 0
   0A72                     221 _g_tiles_14:
   0A72 00                  222 	.db #0x00	; 0
   0A73 00                  223 	.db #0x00	; 0
   0A74 00                  224 	.db #0x00	; 0
   0A75 00                  225 	.db #0x00	; 0
   0A76 00                  226 	.db #0x00	; 0
   0A77 00                  227 	.db #0x00	; 0
   0A78 00                  228 	.db #0x00	; 0
   0A79 04                  229 	.db #0x04	; 4
   0A7A                     230 _g_tiles_15:
   0A7A 00                  231 	.db #0x00	; 0
   0A7B 40                  232 	.db #0x40	; 64
   0A7C 00                  233 	.db #0x00	; 0
   0A7D C0                  234 	.db #0xc0	; 192
   0A7E 40                  235 	.db #0x40	; 64
   0A7F C4                  236 	.db #0xc4	; 196
   0A80 40                  237 	.db #0x40	; 64
   0A81 C0                  238 	.db #0xc0	; 192
   0A82                     239 _g_tiles_16:
   0A82 80                  240 	.db #0x80	; 128
   0A83 00                  241 	.db #0x00	; 0
   0A84 C0                  242 	.db #0xc0	; 192
   0A85 80                  243 	.db #0x80	; 128
   0A86 C0                  244 	.db #0xc0	; 192
   0A87 C0                  245 	.db #0xc0	; 192
   0A88 C0                  246 	.db #0xc0	; 192
   0A89 80                  247 	.db #0x80	; 128
   0A8A                     248 _g_tiles_17:
   0A8A 00                  249 	.db #0x00	; 0
   0A8B 00                  250 	.db #0x00	; 0
   0A8C 00                  251 	.db #0x00	; 0
   0A8D 00                  252 	.db #0x00	; 0
   0A8E 00                  253 	.db #0x00	; 0
   0A8F 00                  254 	.db #0x00	; 0
   0A90 00                  255 	.db #0x00	; 0
   0A91 40                  256 	.db #0x40	; 64
   0A92                     257 _g_tiles_18:
   0A92 00                  258 	.db #0x00	; 0
   0A93 00                  259 	.db #0x00	; 0
   0A94 00                  260 	.db #0x00	; 0
   0A95 00                  261 	.db #0x00	; 0
   0A96 80                  262 	.db #0x80	; 128
   0A97 00                  263 	.db #0x00	; 0
   0A98 80                  264 	.db #0x80	; 128
   0A99 00                  265 	.db #0x00	; 0
   0A9A                     266 _g_tiles_19:
   0A9A 00                  267 	.db #0x00	; 0
   0A9B 00                  268 	.db #0x00	; 0
   0A9C 00                  269 	.db #0x00	; 0
   0A9D 00                  270 	.db #0x00	; 0
   0A9E 00                  271 	.db #0x00	; 0
   0A9F 08                  272 	.db #0x08	; 8
   0AA0 00                  273 	.db #0x00	; 0
   0AA1 00                  274 	.db #0x00	; 0
   0AA2                     275 _g_tiles_20:
   0AA2 00                  276 	.db #0x00	; 0
   0AA3 04                  277 	.db #0x04	; 4
   0AA4 00                  278 	.db #0x00	; 0
   0AA5 04                  279 	.db #0x04	; 4
   0AA6 80                  280 	.db #0x80	; 128
   0AA7 84                  281 	.db #0x84	; 132
   0AA8 C0                  282 	.db #0xc0	; 192
   0AA9 84                  283 	.db #0x84	; 132
   0AAA                     284 _g_tiles_21:
   0AAA C0                  285 	.db #0xc0	; 192
   0AAB 00                  286 	.db #0x00	; 0
   0AAC 08                  287 	.db #0x08	; 8
   0AAD 00                  288 	.db #0x00	; 0
   0AAE 08                  289 	.db #0x08	; 8
   0AAF 80                  290 	.db #0x80	; 128
   0AB0 48                  291 	.db #0x48	; 72	'H'
   0AB1 C0                  292 	.db #0xc0	; 192
   0AB2                     293 _g_tiles_22:
   0AB2 40                  294 	.db #0x40	; 64
   0AB3 40                  295 	.db #0x40	; 64
   0AB4 C0                  296 	.db #0xc0	; 192
   0AB5 C0                  297 	.db #0xc0	; 192
   0AB6 40                  298 	.db #0x40	; 64
   0AB7 C0                  299 	.db #0xc0	; 192
   0AB8 C0                  300 	.db #0xc0	; 192
   0AB9 C0                  301 	.db #0xc0	; 192
   0ABA                     302 _g_tiles_23:
   0ABA C0                  303 	.db #0xc0	; 192
   0ABB 80                  304 	.db #0x80	; 128
   0ABC C8                  305 	.db #0xc8	; 200
   0ABD 00                  306 	.db #0x00	; 0
   0ABE C0                  307 	.db #0xc0	; 192
   0ABF 80                  308 	.db #0x80	; 128
   0AC0 C0                  309 	.db #0xc0	; 192
   0AC1 80                  310 	.db #0x80	; 128
   0AC2                     311 _g_tiles_24:
   0AC2 00                  312 	.db #0x00	; 0
   0AC3 00                  313 	.db #0x00	; 0
   0AC4 04                  314 	.db #0x04	; 4
   0AC5 00                  315 	.db #0x00	; 0
   0AC6 00                  316 	.db #0x00	; 0
   0AC7 00                  317 	.db #0x00	; 0
   0AC8 00                  318 	.db #0x00	; 0
   0AC9 00                  319 	.db #0x00	; 0
                            320 	.area _INITIALIZER
                            321 	.area _CABS (ABS)
