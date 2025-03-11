                              1 ;--------------------------------------------------------
                              2 ; File Created by SDCC : free open source ANSI-C Compiler
                              3 ; Version 3.6.8 #9946 (Linux)
                              4 ;--------------------------------------------------------
                              5 	.module main
                              6 	.optsdcc -mz80
                              7 	
                              8 ;--------------------------------------------------------
                              9 ; Public variables in this module
                             10 ;--------------------------------------------------------
                             11 	.globl _main
                             12 	.globl _printf
                             13 	.globl _cpct_getHWColour
                             14 	.globl _cpct_memset
                             15 ;--------------------------------------------------------
                             16 ; special function registers
                             17 ;--------------------------------------------------------
                             18 ;--------------------------------------------------------
                             19 ; ram data
                             20 ;--------------------------------------------------------
                             21 	.area _DATA
                             22 ;--------------------------------------------------------
                             23 ; ram data
                             24 ;--------------------------------------------------------
                             25 	.area _INITIALIZED
                             26 ;--------------------------------------------------------
                             27 ; absolute external ram data
                             28 ;--------------------------------------------------------
                             29 	.area _DABS (ABS)
                             30 ;--------------------------------------------------------
                             31 ; global & static initialisations
                             32 ;--------------------------------------------------------
                             33 	.area _HOME
                             34 	.area _GSINIT
                             35 	.area _GSFINAL
                             36 	.area _GSINIT
                             37 ;--------------------------------------------------------
                             38 ; Home
                             39 ;--------------------------------------------------------
                             40 	.area _HOME
                             41 	.area _HOME
                             42 ;--------------------------------------------------------
                             43 ; code
                             44 ;--------------------------------------------------------
                             45 	.area _CODE
                             46 ;src/main.c:26: void main(void) {
                             47 ;	---------------------------------
                             48 ; Function main
                             49 ; ---------------------------------
   4000                      50 _main::
                             51 ;src/main.c:30: cpct_clearScreen(0);
   4000 21 00 40      [10]   52 	ld	hl, #0x4000
   4003 E5            [11]   53 	push	hl
   4004 AF            [ 4]   54 	xor	a, a
   4005 F5            [11]   55 	push	af
   4006 33            [ 6]   56 	inc	sp
   4007 26 C0         [ 7]   57 	ld	h, #0xc0
   4009 E5            [11]   58 	push	hl
   400A CD 73 42      [17]   59 	call	_cpct_memset
                             60 ;src/main.c:40: printf("        \017\003Hardware Colour values\017\002          ");
   400D 21 8E 40      [10]   61 	ld	hl, #___str_0
   4010 E5            [11]   62 	push	hl
   4011 CD 56 42      [17]   63 	call	_printf
                             64 ;src/main.c:41: printf("This example shows the  equivalence between firmware co-");
   4014 21 BB 40      [10]   65 	ld	hl, #___str_1
   4017 E3            [19]   66 	ex	(sp),hl
   4018 CD 56 42      [17]   67 	call	_printf
                             68 ;src/main.c:42: printf("lour  values  and harwdware  colour values. \017\003CPCtelera\017\002's ");
   401B 21 F4 40      [10]   69 	ld	hl, #___str_2
   401E E3            [19]   70 	ex	(sp),hl
   401F CD 56 42      [17]   71 	call	_printf
                             72 ;src/main.c:43: printf("functions that change colours use hardware ones.\n\r\n\r");
   4022 21 31 41      [10]   73 	ld	hl, #___str_3
   4025 E3            [19]   74 	ex	(sp),hl
   4026 CD 56 42      [17]   75 	call	_printf
                             76 ;src/main.c:44: printf("   \017\003==================================\n\r");
   4029 21 66 41      [10]   77 	ld	hl, #___str_4
   402C E3            [19]   78 	ex	(sp),hl
   402D CD 56 42      [17]   79 	call	_printf
                             80 ;src/main.c:45: printf("   || \017\002FIRM -- HARD \017\003|| \017\002FIRM -- HARD \017\003||\n\r");
   4030 21 90 41      [10]   81 	ld	hl, #___str_5
   4033 E3            [19]   82 	ex	(sp),hl
   4034 CD 56 42      [17]   83 	call	_printf
                             84 ;src/main.c:46: printf("   ==================================\n\r");
   4037 21 C0 41      [10]   85 	ld	hl, #___str_6
   403A E3            [19]   86 	ex	(sp),hl
   403B CD 56 42      [17]   87 	call	_printf
   403E F1            [10]   88 	pop	af
                             89 ;src/main.c:47: for (i=0; i < 13; ++i) {
   403F 0E 00         [ 7]   90 	ld	c, #0x00
   4041                      91 00105$:
                             92 ;src/main.c:48: printf("   \017\003||  \017\001%2d  \017\003--  \017\001%2d\017\003  ",       i, cpct_getHWColour(i));
   4041 69            [ 4]   93 	ld	l, c
   4042 26 00         [ 7]   94 	ld	h, #0x00
   4044 C5            [11]   95 	push	bc
   4045 CD 81 42      [17]   96 	call	_cpct_getHWColour
   4048 C1            [10]   97 	pop	bc
   4049 26 00         [ 7]   98 	ld	h, #0x00
   404B 59            [ 4]   99 	ld	e, c
   404C 16 00         [ 7]  100 	ld	d, #0x00
   404E C5            [11]  101 	push	bc
   404F D5            [11]  102 	push	de
   4050 E5            [11]  103 	push	hl
   4051 D5            [11]  104 	push	de
   4052 21 E8 41      [10]  105 	ld	hl, #___str_7
   4055 E5            [11]  106 	push	hl
   4056 CD 56 42      [17]  107 	call	_printf
   4059 21 06 00      [10]  108 	ld	hl, #6
   405C 39            [11]  109 	add	hl, sp
   405D F9            [ 6]  110 	ld	sp, hl
   405E D1            [10]  111 	pop	de
   405F C1            [10]  112 	pop	bc
                            113 ;src/main.c:49: printf("\017\003||  \017\001%2d  \017\003--  \017\001%2d\017\003  ||\n\r", i+13, cpct_getHWColour(i+13));
   4060 21 0D 00      [10]  114 	ld	hl, #0x000d
   4063 19            [11]  115 	add	hl, de
   4064 E5            [11]  116 	push	hl
   4065 C5            [11]  117 	push	bc
   4066 CD 81 42      [17]  118 	call	_cpct_getHWColour
   4069 5D            [ 4]  119 	ld	e, l
   406A C1            [10]  120 	pop	bc
   406B E1            [10]  121 	pop	hl
   406C 16 00         [ 7]  122 	ld	d, #0x00
   406E C5            [11]  123 	push	bc
   406F D5            [11]  124 	push	de
   4070 E5            [11]  125 	push	hl
   4071 21 08 42      [10]  126 	ld	hl, #___str_8
   4074 E5            [11]  127 	push	hl
   4075 CD 56 42      [17]  128 	call	_printf
   4078 21 06 00      [10]  129 	ld	hl, #6
   407B 39            [11]  130 	add	hl, sp
   407C F9            [ 6]  131 	ld	sp, hl
   407D C1            [10]  132 	pop	bc
                            133 ;src/main.c:47: for (i=0; i < 13; ++i) {
   407E 0C            [ 4]  134 	inc	c
   407F 79            [ 4]  135 	ld	a, c
   4080 D6 0D         [ 7]  136 	sub	a, #0x0d
   4082 38 BD         [12]  137 	jr	C,00105$
                            138 ;src/main.c:51: printf("   ==================================\n\r");
   4084 21 C0 41      [10]  139 	ld	hl, #___str_6
   4087 E5            [11]  140 	push	hl
   4088 CD 56 42      [17]  141 	call	_printf
   408B F1            [10]  142 	pop	af
                            143 ;src/main.c:54: while (1);
   408C                     144 00103$:
   408C 18 FE         [12]  145 	jr	00103$
   408E                     146 ___str_0:
   408E 20 20 20 20 20 20   147 	.ascii "        "
        20 20
   4096 0F                  148 	.db 0x0f
   4097 03                  149 	.db 0x03
   4098 48 61 72 64 77 61   150 	.ascii "Hardware Colour values"
        72 65 20 43 6F 6C
        6F 75 72 20 76 61
        6C 75 65 73
   40AE 0F                  151 	.db 0x0f
   40AF 02                  152 	.db 0x02
   40B0 20 20 20 20 20 20   153 	.ascii "          "
        20 20 20 20
   40BA 00                  154 	.db 0x00
   40BB                     155 ___str_1:
   40BB 54 68 69 73 20 65   156 	.ascii "This example shows the  equivalence between firmware co-"
        78 61 6D 70 6C 65
        20 73 68 6F 77 73
        20 74 68 65 20 20
        65 71 75 69 76 61
        6C 65 6E 63 65 20
        62 65 74 77 65 65
        6E 20 66 69 72 6D
        77 61 72 65 20 63
        6F 2D
   40F3 00                  157 	.db 0x00
   40F4                     158 ___str_2:
   40F4 6C 6F 75 72 20 20   159 	.ascii "lour  values  and harwdware  colour values. "
        76 61 6C 75 65 73
        20 20 61 6E 64 20
        68 61 72 77 64 77
        61 72 65 20 20 63
        6F 6C 6F 75 72 20
        76 61 6C 75 65 73
        2E 20
   4120 0F                  160 	.db 0x0f
   4121 03                  161 	.db 0x03
   4122 43 50 43 74 65 6C   162 	.ascii "CPCtelera"
        65 72 61
   412B 0F                  163 	.db 0x0f
   412C 02                  164 	.db 0x02
   412D 27 73 20            165 	.ascii "'s "
   4130 00                  166 	.db 0x00
   4131                     167 ___str_3:
   4131 66 75 6E 63 74 69   168 	.ascii "functions that change colours use hardware ones."
        6F 6E 73 20 74 68
        61 74 20 63 68 61
        6E 67 65 20 63 6F
        6C 6F 75 72 73 20
        75 73 65 20 68 61
        72 64 77 61 72 65
        20 6F 6E 65 73 2E
   4161 0A                  169 	.db 0x0a
   4162 0D                  170 	.db 0x0d
   4163 0A                  171 	.db 0x0a
   4164 0D                  172 	.db 0x0d
   4165 00                  173 	.db 0x00
   4166                     174 ___str_4:
   4166 20 20 20            175 	.ascii "   "
   4169 0F                  176 	.db 0x0f
   416A 03                  177 	.db 0x03
   416B 3D 3D 3D 3D 3D 3D   178 	.ascii "=================================="
        3D 3D 3D 3D 3D 3D
        3D 3D 3D 3D 3D 3D
        3D 3D 3D 3D 3D 3D
        3D 3D 3D 3D 3D 3D
        3D 3D 3D 3D
   418D 0A                  179 	.db 0x0a
   418E 0D                  180 	.db 0x0d
   418F 00                  181 	.db 0x00
   4190                     182 ___str_5:
   4190 20 20 20 7C 7C 20   183 	.ascii "   || "
   4196 0F                  184 	.db 0x0f
   4197 02                  185 	.db 0x02
   4198 46 49 52 4D 20 2D   186 	.ascii "FIRM -- HARD "
        2D 20 48 41 52 44
        20
   41A5 0F                  187 	.db 0x0f
   41A6 03                  188 	.db 0x03
   41A7 7C 7C 20            189 	.ascii "|| "
   41AA 0F                  190 	.db 0x0f
   41AB 02                  191 	.db 0x02
   41AC 46 49 52 4D 20 2D   192 	.ascii "FIRM -- HARD "
        2D 20 48 41 52 44
        20
   41B9 0F                  193 	.db 0x0f
   41BA 03                  194 	.db 0x03
   41BB 7C 7C               195 	.ascii "||"
   41BD 0A                  196 	.db 0x0a
   41BE 0D                  197 	.db 0x0d
   41BF 00                  198 	.db 0x00
   41C0                     199 ___str_6:
   41C0 20 20 20 3D 3D 3D   200 	.ascii "   =================================="
        3D 3D 3D 3D 3D 3D
        3D 3D 3D 3D 3D 3D
        3D 3D 3D 3D 3D 3D
        3D 3D 3D 3D 3D 3D
        3D 3D 3D 3D 3D 3D
        3D
   41E5 0A                  201 	.db 0x0a
   41E6 0D                  202 	.db 0x0d
   41E7 00                  203 	.db 0x00
   41E8                     204 ___str_7:
   41E8 20 20 20            205 	.ascii "   "
   41EB 0F                  206 	.db 0x0f
   41EC 03                  207 	.db 0x03
   41ED 7C 7C 20 20         208 	.ascii "||  "
   41F1 0F                  209 	.db 0x0f
   41F2 01                  210 	.db 0x01
   41F3 25 32 64 20 20      211 	.ascii "%2d  "
   41F8 0F                  212 	.db 0x0f
   41F9 03                  213 	.db 0x03
   41FA 2D 2D 20 20         214 	.ascii "--  "
   41FE 0F                  215 	.db 0x0f
   41FF 01                  216 	.db 0x01
   4200 25 32 64            217 	.ascii "%2d"
   4203 0F                  218 	.db 0x0f
   4204 03                  219 	.db 0x03
   4205 20 20               220 	.ascii "  "
   4207 00                  221 	.db 0x00
   4208                     222 ___str_8:
   4208 0F                  223 	.db 0x0f
   4209 03                  224 	.db 0x03
   420A 7C 7C 20 20         225 	.ascii "||  "
   420E 0F                  226 	.db 0x0f
   420F 01                  227 	.db 0x01
   4210 25 32 64 20 20      228 	.ascii "%2d  "
   4215 0F                  229 	.db 0x0f
   4216 03                  230 	.db 0x03
   4217 2D 2D 20 20         231 	.ascii "--  "
   421B 0F                  232 	.db 0x0f
   421C 01                  233 	.db 0x01
   421D 25 32 64            234 	.ascii "%2d"
   4220 0F                  235 	.db 0x0f
   4221 03                  236 	.db 0x03
   4222 20 20 7C 7C         237 	.ascii "  ||"
   4226 0A                  238 	.db 0x0a
   4227 0D                  239 	.db 0x0d
   4228 00                  240 	.db 0x00
                            241 	.area _CODE
                            242 	.area _INITIALIZER
                            243 	.area _CABS (ABS)
