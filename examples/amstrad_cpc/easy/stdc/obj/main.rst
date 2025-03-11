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
                             13 	.globl _cpct_memset
                             14 ;--------------------------------------------------------
                             15 ; special function registers
                             16 ;--------------------------------------------------------
                             17 ;--------------------------------------------------------
                             18 ; ram data
                             19 ;--------------------------------------------------------
                             20 	.area _DATA
                             21 ;--------------------------------------------------------
                             22 ; ram data
                             23 ;--------------------------------------------------------
                             24 	.area _INITIALIZED
                             25 ;--------------------------------------------------------
                             26 ; absolute external ram data
                             27 ;--------------------------------------------------------
                             28 	.area _DABS (ABS)
                             29 ;--------------------------------------------------------
                             30 ; global & static initialisations
                             31 ;--------------------------------------------------------
                             32 	.area _HOME
                             33 	.area _GSINIT
                             34 	.area _GSFINAL
                             35 	.area _GSINIT
                             36 ;--------------------------------------------------------
                             37 ; Home
                             38 ;--------------------------------------------------------
                             39 	.area _HOME
                             40 	.area _HOME
                             41 ;--------------------------------------------------------
                             42 ; code
                             43 ;--------------------------------------------------------
                             44 	.area _CODE
                             45 ;src/main.c:27: void main(void) {
                             46 ;	---------------------------------
                             47 ; Function main
                             48 ; ---------------------------------
   0100                      49 _main::
                             50 ;src/main.c:29: cpct_clearScreen(0);
   0100 21 00 40      [10]   51 	ld	hl, #0x4000
   0103 E5            [11]   52 	push	hl
   0104 AF            [ 4]   53 	xor	a, a
   0105 F5            [11]   54 	push	af
   0106 33            [ 6]   55 	inc	sp
   0107 26 C0         [ 7]   56 	ld	h, #0xc0
   0109 E5            [11]   57 	push	hl
   010A CD C8 03      [17]   58 	call	_cpct_memset
                             59 ;src/main.c:38: printf("      \017\003Welcome to \017\002CPCtelera\017\003!\017\001\n\r\n\r");
   010D 21 9F 01      [10]   60 	ld	hl, #___str_0
   0110 E5            [11]   61 	push	hl
   0111 CD AB 03      [17]   62 	call	_printf
                             63 ;src/main.c:39: printf("This  example  makes  use  of standard C");
   0114 21 C7 01      [10]   64 	ld	hl, #___str_1
   0117 E3            [19]   65 	ex	(sp),hl
   0118 CD AB 03      [17]   66 	call	_printf
                             67 ;src/main.c:40: printf("libraries  to  print out  byte sizes  of");
   011B 21 F0 01      [10]   68 	ld	hl, #___str_2
   011E E3            [19]   69 	ex	(sp),hl
   011F CD AB 03      [17]   70 	call	_printf
                             71 ;src/main.c:41: printf("standard  SDCC  types, using \017\002CPCtelera\017\001's");
   0122 21 19 02      [10]   72 	ld	hl, #___str_3
   0125 E3            [19]   73 	ex	(sp),hl
   0126 CD AB 03      [17]   74 	call	_printf
                             75 ;src/main.c:42: printf("convenient aliases.\n\r\n\r");
   0129 21 46 02      [10]   76 	ld	hl, #___str_4
   012C E3            [19]   77 	ex	(sp),hl
   012D CD AB 03      [17]   78 	call	_printf
                             79 ;src/main.c:43: printf("Size of \017\003 u8 \017\001=\017\002 %d \017\001byte\n\r", sizeof(u8));
   0130 21 01 00      [10]   80 	ld	hl, #0x0001
   0133 E3            [19]   81 	ex	(sp),hl
   0134 21 5E 02      [10]   82 	ld	hl, #___str_5
   0137 E5            [11]   83 	push	hl
   0138 CD AB 03      [17]   84 	call	_printf
   013B F1            [10]   85 	pop	af
                             86 ;src/main.c:44: printf("Size of \017\003u16 \017\001=\017\002 %d \017\001byte\n\r", sizeof(u16));
   013C 21 02 00      [10]   87 	ld	hl, #0x0002
   013F E3            [19]   88 	ex	(sp),hl
   0140 21 7E 02      [10]   89 	ld	hl, #___str_6
   0143 E5            [11]   90 	push	hl
   0144 CD AB 03      [17]   91 	call	_printf
   0147 F1            [10]   92 	pop	af
                             93 ;src/main.c:45: printf("Size of \017\003u32 \017\001=\017\002 %d \017\001byte\n\r", sizeof(u32));
   0148 21 04 00      [10]   94 	ld	hl, #0x0004
   014B E3            [19]   95 	ex	(sp),hl
   014C 21 9E 02      [10]   96 	ld	hl, #___str_7
   014F E5            [11]   97 	push	hl
   0150 CD AB 03      [17]   98 	call	_printf
   0153 F1            [10]   99 	pop	af
                            100 ;src/main.c:46: printf("Size of \017\003u64 \017\001=\017\002 %d \017\001byte\n\r", sizeof(u64));
   0154 21 08 00      [10]  101 	ld	hl, #0x0008
   0157 E3            [19]  102 	ex	(sp),hl
   0158 21 BE 02      [10]  103 	ld	hl, #___str_8
   015B E5            [11]  104 	push	hl
   015C CD AB 03      [17]  105 	call	_printf
   015F F1            [10]  106 	pop	af
                            107 ;src/main.c:47: printf("Size of \017\003 i8 \017\001=\017\002 %d \017\001byte\n\r", sizeof(i8));
   0160 21 01 00      [10]  108 	ld	hl, #0x0001
   0163 E3            [19]  109 	ex	(sp),hl
   0164 21 DE 02      [10]  110 	ld	hl, #___str_9
   0167 E5            [11]  111 	push	hl
   0168 CD AB 03      [17]  112 	call	_printf
   016B F1            [10]  113 	pop	af
                            114 ;src/main.c:48: printf("Size of \017\003i16 \017\001=\017\002 %d \017\001byte\n\r", sizeof(i16));
   016C 21 02 00      [10]  115 	ld	hl, #0x0002
   016F E3            [19]  116 	ex	(sp),hl
   0170 21 FE 02      [10]  117 	ld	hl, #___str_10
   0173 E5            [11]  118 	push	hl
   0174 CD AB 03      [17]  119 	call	_printf
   0177 F1            [10]  120 	pop	af
                            121 ;src/main.c:49: printf("Size of \017\003i32 \017\001=\017\002 %d \017\001byte\n\r", sizeof(i32));
   0178 21 04 00      [10]  122 	ld	hl, #0x0004
   017B E3            [19]  123 	ex	(sp),hl
   017C 21 1E 03      [10]  124 	ld	hl, #___str_11
   017F E5            [11]  125 	push	hl
   0180 CD AB 03      [17]  126 	call	_printf
   0183 F1            [10]  127 	pop	af
                            128 ;src/main.c:50: printf("Size of \017\003i64 \017\001=\017\002 %d \017\001byte\n\r", sizeof(i64));
   0184 21 08 00      [10]  129 	ld	hl, #0x0008
   0187 E3            [19]  130 	ex	(sp),hl
   0188 21 3E 03      [10]  131 	ld	hl, #___str_12
   018B E5            [11]  132 	push	hl
   018C CD AB 03      [17]  133 	call	_printf
   018F F1            [10]  134 	pop	af
                            135 ;src/main.c:51: printf("Size of \017\003f32 \017\001=\017\002 %d \017\001byte\n\r", sizeof(f32));
   0190 21 04 00      [10]  136 	ld	hl, #0x0004
   0193 E3            [19]  137 	ex	(sp),hl
   0194 21 5E 03      [10]  138 	ld	hl, #___str_13
   0197 E5            [11]  139 	push	hl
   0198 CD AB 03      [17]  140 	call	_printf
   019B F1            [10]  141 	pop	af
   019C F1            [10]  142 	pop	af
                            143 ;src/main.c:54: while (1);
   019D                     144 00102$:
   019D 18 FE         [12]  145 	jr	00102$
   019F                     146 ___str_0:
   019F 20 20 20 20 20 20   147 	.ascii "      "
   01A5 0F                  148 	.db 0x0f
   01A6 03                  149 	.db 0x03
   01A7 57 65 6C 63 6F 6D   150 	.ascii "Welcome to "
        65 20 74 6F 20
   01B2 0F                  151 	.db 0x0f
   01B3 02                  152 	.db 0x02
   01B4 43 50 43 74 65 6C   153 	.ascii "CPCtelera"
        65 72 61
   01BD 0F                  154 	.db 0x0f
   01BE 03                  155 	.db 0x03
   01BF 21                  156 	.ascii "!"
   01C0 0F                  157 	.db 0x0f
   01C1 01                  158 	.db 0x01
   01C2 0A                  159 	.db 0x0a
   01C3 0D                  160 	.db 0x0d
   01C4 0A                  161 	.db 0x0a
   01C5 0D                  162 	.db 0x0d
   01C6 00                  163 	.db 0x00
   01C7                     164 ___str_1:
   01C7 54 68 69 73 20 20   165 	.ascii "This  example  makes  use  of standard C"
        65 78 61 6D 70 6C
        65 20 20 6D 61 6B
        65 73 20 20 75 73
        65 20 20 6F 66 20
        73 74 61 6E 64 61
        72 64 20 43
   01EF 00                  166 	.db 0x00
   01F0                     167 ___str_2:
   01F0 6C 69 62 72 61 72   168 	.ascii "libraries  to  print out  byte sizes  of"
        69 65 73 20 20 74
        6F 20 20 70 72 69
        6E 74 20 6F 75 74
        20 20 62 79 74 65
        20 73 69 7A 65 73
        20 20 6F 66
   0218 00                  169 	.db 0x00
   0219                     170 ___str_3:
   0219 73 74 61 6E 64 61   171 	.ascii "standard  SDCC  types, using "
        72 64 20 20 53 44
        43 43 20 20 74 79
        70 65 73 2C 20 75
        73 69 6E 67 20
   0236 0F                  172 	.db 0x0f
   0237 02                  173 	.db 0x02
   0238 43 50 43 74 65 6C   174 	.ascii "CPCtelera"
        65 72 61
   0241 0F                  175 	.db 0x0f
   0242 01                  176 	.db 0x01
   0243 27 73               177 	.ascii "'s"
   0245 00                  178 	.db 0x00
   0246                     179 ___str_4:
   0246 63 6F 6E 76 65 6E   180 	.ascii "convenient aliases."
        69 65 6E 74 20 61
        6C 69 61 73 65 73
        2E
   0259 0A                  181 	.db 0x0a
   025A 0D                  182 	.db 0x0d
   025B 0A                  183 	.db 0x0a
   025C 0D                  184 	.db 0x0d
   025D 00                  185 	.db 0x00
   025E                     186 ___str_5:
   025E 53 69 7A 65 20 6F   187 	.ascii "Size of "
        66 20
   0266 0F                  188 	.db 0x0f
   0267 03                  189 	.db 0x03
   0268 20 75 38 20         190 	.ascii " u8 "
   026C 0F                  191 	.db 0x0f
   026D 01                  192 	.db 0x01
   026E 3D                  193 	.ascii "="
   026F 0F                  194 	.db 0x0f
   0270 02                  195 	.db 0x02
   0271 20 25 64 20         196 	.ascii " %d "
   0275 0F                  197 	.db 0x0f
   0276 01                  198 	.db 0x01
   0277 62 79 74 65         199 	.ascii "byte"
   027B 0A                  200 	.db 0x0a
   027C 0D                  201 	.db 0x0d
   027D 00                  202 	.db 0x00
   027E                     203 ___str_6:
   027E 53 69 7A 65 20 6F   204 	.ascii "Size of "
        66 20
   0286 0F                  205 	.db 0x0f
   0287 03                  206 	.db 0x03
   0288 75 31 36 20         207 	.ascii "u16 "
   028C 0F                  208 	.db 0x0f
   028D 01                  209 	.db 0x01
   028E 3D                  210 	.ascii "="
   028F 0F                  211 	.db 0x0f
   0290 02                  212 	.db 0x02
   0291 20 25 64 20         213 	.ascii " %d "
   0295 0F                  214 	.db 0x0f
   0296 01                  215 	.db 0x01
   0297 62 79 74 65         216 	.ascii "byte"
   029B 0A                  217 	.db 0x0a
   029C 0D                  218 	.db 0x0d
   029D 00                  219 	.db 0x00
   029E                     220 ___str_7:
   029E 53 69 7A 65 20 6F   221 	.ascii "Size of "
        66 20
   02A6 0F                  222 	.db 0x0f
   02A7 03                  223 	.db 0x03
   02A8 75 33 32 20         224 	.ascii "u32 "
   02AC 0F                  225 	.db 0x0f
   02AD 01                  226 	.db 0x01
   02AE 3D                  227 	.ascii "="
   02AF 0F                  228 	.db 0x0f
   02B0 02                  229 	.db 0x02
   02B1 20 25 64 20         230 	.ascii " %d "
   02B5 0F                  231 	.db 0x0f
   02B6 01                  232 	.db 0x01
   02B7 62 79 74 65         233 	.ascii "byte"
   02BB 0A                  234 	.db 0x0a
   02BC 0D                  235 	.db 0x0d
   02BD 00                  236 	.db 0x00
   02BE                     237 ___str_8:
   02BE 53 69 7A 65 20 6F   238 	.ascii "Size of "
        66 20
   02C6 0F                  239 	.db 0x0f
   02C7 03                  240 	.db 0x03
   02C8 75 36 34 20         241 	.ascii "u64 "
   02CC 0F                  242 	.db 0x0f
   02CD 01                  243 	.db 0x01
   02CE 3D                  244 	.ascii "="
   02CF 0F                  245 	.db 0x0f
   02D0 02                  246 	.db 0x02
   02D1 20 25 64 20         247 	.ascii " %d "
   02D5 0F                  248 	.db 0x0f
   02D6 01                  249 	.db 0x01
   02D7 62 79 74 65         250 	.ascii "byte"
   02DB 0A                  251 	.db 0x0a
   02DC 0D                  252 	.db 0x0d
   02DD 00                  253 	.db 0x00
   02DE                     254 ___str_9:
   02DE 53 69 7A 65 20 6F   255 	.ascii "Size of "
        66 20
   02E6 0F                  256 	.db 0x0f
   02E7 03                  257 	.db 0x03
   02E8 20 69 38 20         258 	.ascii " i8 "
   02EC 0F                  259 	.db 0x0f
   02ED 01                  260 	.db 0x01
   02EE 3D                  261 	.ascii "="
   02EF 0F                  262 	.db 0x0f
   02F0 02                  263 	.db 0x02
   02F1 20 25 64 20         264 	.ascii " %d "
   02F5 0F                  265 	.db 0x0f
   02F6 01                  266 	.db 0x01
   02F7 62 79 74 65         267 	.ascii "byte"
   02FB 0A                  268 	.db 0x0a
   02FC 0D                  269 	.db 0x0d
   02FD 00                  270 	.db 0x00
   02FE                     271 ___str_10:
   02FE 53 69 7A 65 20 6F   272 	.ascii "Size of "
        66 20
   0306 0F                  273 	.db 0x0f
   0307 03                  274 	.db 0x03
   0308 69 31 36 20         275 	.ascii "i16 "
   030C 0F                  276 	.db 0x0f
   030D 01                  277 	.db 0x01
   030E 3D                  278 	.ascii "="
   030F 0F                  279 	.db 0x0f
   0310 02                  280 	.db 0x02
   0311 20 25 64 20         281 	.ascii " %d "
   0315 0F                  282 	.db 0x0f
   0316 01                  283 	.db 0x01
   0317 62 79 74 65         284 	.ascii "byte"
   031B 0A                  285 	.db 0x0a
   031C 0D                  286 	.db 0x0d
   031D 00                  287 	.db 0x00
   031E                     288 ___str_11:
   031E 53 69 7A 65 20 6F   289 	.ascii "Size of "
        66 20
   0326 0F                  290 	.db 0x0f
   0327 03                  291 	.db 0x03
   0328 69 33 32 20         292 	.ascii "i32 "
   032C 0F                  293 	.db 0x0f
   032D 01                  294 	.db 0x01
   032E 3D                  295 	.ascii "="
   032F 0F                  296 	.db 0x0f
   0330 02                  297 	.db 0x02
   0331 20 25 64 20         298 	.ascii " %d "
   0335 0F                  299 	.db 0x0f
   0336 01                  300 	.db 0x01
   0337 62 79 74 65         301 	.ascii "byte"
   033B 0A                  302 	.db 0x0a
   033C 0D                  303 	.db 0x0d
   033D 00                  304 	.db 0x00
   033E                     305 ___str_12:
   033E 53 69 7A 65 20 6F   306 	.ascii "Size of "
        66 20
   0346 0F                  307 	.db 0x0f
   0347 03                  308 	.db 0x03
   0348 69 36 34 20         309 	.ascii "i64 "
   034C 0F                  310 	.db 0x0f
   034D 01                  311 	.db 0x01
   034E 3D                  312 	.ascii "="
   034F 0F                  313 	.db 0x0f
   0350 02                  314 	.db 0x02
   0351 20 25 64 20         315 	.ascii " %d "
   0355 0F                  316 	.db 0x0f
   0356 01                  317 	.db 0x01
   0357 62 79 74 65         318 	.ascii "byte"
   035B 0A                  319 	.db 0x0a
   035C 0D                  320 	.db 0x0d
   035D 00                  321 	.db 0x00
   035E                     322 ___str_13:
   035E 53 69 7A 65 20 6F   323 	.ascii "Size of "
        66 20
   0366 0F                  324 	.db 0x0f
   0367 03                  325 	.db 0x03
   0368 66 33 32 20         326 	.ascii "f32 "
   036C 0F                  327 	.db 0x0f
   036D 01                  328 	.db 0x01
   036E 3D                  329 	.ascii "="
   036F 0F                  330 	.db 0x0f
   0370 02                  331 	.db 0x02
   0371 20 25 64 20         332 	.ascii " %d "
   0375 0F                  333 	.db 0x0f
   0376 01                  334 	.db 0x01
   0377 62 79 74 65         335 	.ascii "byte"
   037B 0A                  336 	.db 0x0a
   037C 0D                  337 	.db 0x0d
   037D 00                  338 	.db 0x00
                            339 	.area _CODE
                            340 	.area _INITIALIZER
                            341 	.area _CABS (ABS)
