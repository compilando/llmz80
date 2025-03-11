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
                             12 	.globl _printRandomNumbers
                             13 	.globl _initialize
                             14 	.globl _wait4UserKeypress
                             15 	.globl _printf
                             16 	.globl _cpct_restoreState_mxor_u8
                             17 	.globl _cpct_setSeed_mxor
                             18 	.globl _cpct_getRandom_mxor_u8
                             19 	.globl _cpct_isAnyKeyPressed_f
                             20 	.globl _cpct_scanKeyboard_f
                             21 ;--------------------------------------------------------
                             22 ; special function registers
                             23 ;--------------------------------------------------------
                             24 ;--------------------------------------------------------
                             25 ; ram data
                             26 ;--------------------------------------------------------
                             27 	.area _DATA
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
                             52 ;src/main.c:33: u32 wait4UserKeypress() {
                             53 ;	---------------------------------
                             54 ; Function wait4UserKeypress
                             55 ; ---------------------------------
   4000                      56 _wait4UserKeypress::
                             57 ;src/main.c:37: do {
   4000 21 00 00      [10]   58 	ld	hl,#0x0000
   4003 5D            [ 4]   59 	ld	e,l
   4004 54            [ 4]   60 	ld	d,h
   4005                      61 00101$:
                             62 ;src/main.c:38: c++;                       // One more cycle
   4005 2C            [ 4]   63 	inc	l
   4006 20 07         [12]   64 	jr	NZ,00115$
   4008 24            [ 4]   65 	inc	h
   4009 20 04         [12]   66 	jr	NZ,00115$
   400B 1C            [ 4]   67 	inc	e
   400C 20 01         [12]   68 	jr	NZ,00115$
   400E 14            [ 4]   69 	inc	d
   400F                      70 00115$:
                             71 ;src/main.c:39: cpct_scanKeyboard_f();     // Scan the scan the keyboard
   400F E5            [11]   72 	push	hl
   4010 D5            [11]   73 	push	de
   4011 CD 53 41      [17]   74 	call	_cpct_scanKeyboard_f
   4014 CD 1D 42      [17]   75 	call	_cpct_isAnyKeyPressed_f
   4017 7D            [ 4]   76 	ld	a, l
   4018 D1            [10]   77 	pop	de
   4019 E1            [10]   78 	pop	hl
   401A B7            [ 4]   79 	or	a, a
   401B 28 E8         [12]   80 	jr	Z,00101$
                             81 ;src/main.c:42: return c;
   401D C9            [10]   82 	ret
                             83 ;src/main.c:50: void initialize() {
                             84 ;	---------------------------------
                             85 ; Function initialize
                             86 ; ---------------------------------
   401E                      87 _initialize::
                             88 ;src/main.c:54: printf("\017\003========= BASIC RANDOM NUMBERS =========\n\n\r");
   401E 21 5A 40      [10]   89 	ld	hl, #___str_0
   4021 E5            [11]   90 	push	hl
   4022 CD 65 42      [17]   91 	call	_printf
                             92 ;src/main.c:55: printf("\017\002Press any key to generate random numbers\n\n\r");
   4025 21 88 40      [10]   93 	ld	hl, #___str_1
   4028 E3            [19]   94 	ex	(sp),hl
   4029 CD 65 42      [17]   95 	call	_printf
   402C F1            [10]   96 	pop	af
                             97 ;src/main.c:59: seed = wait4UserKeypress();
   402D CD 00 40      [17]   98 	call	_wait4UserKeypress
   4030 EB            [ 4]   99 	ex	de, hl
                            100 ;src/main.c:62: if (!seed)
   4031 7C            [ 4]  101 	ld	a, h
   4032 B5            [ 4]  102 	or	a, l
   4033 B2            [ 4]  103 	or	a, d
   4034 B3            [ 4]  104 	or	a,e
   4035 20 0A         [12]  105 	jr	NZ,00102$
                            106 ;src/main.c:63: seed++;
   4037 1C            [ 4]  107 	inc	e
   4038 20 07         [12]  108 	jr	NZ,00109$
   403A 14            [ 4]  109 	inc	d
   403B 20 04         [12]  110 	jr	NZ,00109$
   403D 2C            [ 4]  111 	inc	l
   403E 20 01         [12]  112 	jr	NZ,00109$
   4040 24            [ 4]  113 	inc	h
   4041                     114 00109$:
   4041                     115 00102$:
                            116 ;src/main.c:66: printf("\017\003Selected seed: \017\002%d\n\r", seed);
   4041 01 B6 40      [10]  117 	ld	bc, #___str_2+0
   4044 E5            [11]  118 	push	hl
   4045 D5            [11]  119 	push	de
   4046 E5            [11]  120 	push	hl
   4047 D5            [11]  121 	push	de
   4048 C5            [11]  122 	push	bc
   4049 CD 65 42      [17]  123 	call	_printf
   404C 21 06 00      [10]  124 	ld	hl, #6
   404F 39            [11]  125 	add	hl, sp
   4050 F9            [ 6]  126 	ld	sp, hl
   4051 D1            [10]  127 	pop	de
   4052 E1            [10]  128 	pop	hl
                            129 ;src/main.c:67: cpct_srand(seed);
   4053 EB            [ 4]  130 	ex	de, hl
   4054 CD C7 41      [17]  131 	call	_cpct_setSeed_mxor
   4057 C3 CF 41      [10]  132 	jp  _cpct_restoreState_mxor_u8
   405A                     133 ___str_0:
   405A 0F                  134 	.db 0x0f
   405B 03                  135 	.db 0x03
   405C 3D 3D 3D 3D 3D 3D   136 	.ascii "========= BASIC RANDOM NUMBERS ========="
        3D 3D 3D 20 42 41
        53 49 43 20 52 41
        4E 44 4F 4D 20 4E
        55 4D 42 45 52 53
        20 3D 3D 3D 3D 3D
        3D 3D 3D 3D
   4084 0A                  137 	.db 0x0a
   4085 0A                  138 	.db 0x0a
   4086 0D                  139 	.db 0x0d
   4087 00                  140 	.db 0x00
   4088                     141 ___str_1:
   4088 0F                  142 	.db 0x0f
   4089 02                  143 	.db 0x02
   408A 50 72 65 73 73 20   144 	.ascii "Press any key to generate random numbers"
        61 6E 79 20 6B 65
        79 20 74 6F 20 67
        65 6E 65 72 61 74
        65 20 72 61 6E 64
        6F 6D 20 6E 75 6D
        62 65 72 73
   40B2 0A                  145 	.db 0x0a
   40B3 0A                  146 	.db 0x0a
   40B4 0D                  147 	.db 0x0d
   40B5 00                  148 	.db 0x00
   40B6                     149 ___str_2:
   40B6 0F                  150 	.db 0x0f
   40B7 03                  151 	.db 0x03
   40B8 53 65 6C 65 63 74   152 	.ascii "Selected seed: "
        65 64 20 73 65 65
        64 3A 20
   40C7 0F                  153 	.db 0x0f
   40C8 02                  154 	.db 0x02
   40C9 25 64               155 	.ascii "%d"
   40CB 0A                  156 	.db 0x0a
   40CC 0D                  157 	.db 0x0d
   40CD 00                  158 	.db 0x00
                            159 ;src/main.c:76: void printRandomNumbers(u8 nNumbers) {
                            160 ;	---------------------------------
                            161 ; Function printRandomNumbers
                            162 ; ---------------------------------
   40CE                     163 _printRandomNumbers::
   40CE DD E5         [15]  164 	push	ix
   40D0 DD 21 00 00   [14]  165 	ld	ix,#0
   40D4 DD 39         [15]  166 	add	ix,sp
                            167 ;src/main.c:78: printf("\017\003Generating \017\002%d\017\003 random numbers\n\n\r\017\001", N_RND_NUMBERS);
   40D6 21 32 00      [10]  168 	ld	hl, #0x0032
   40D9 E5            [11]  169 	push	hl
   40DA 21 0C 41      [10]  170 	ld	hl, #___str_3
   40DD E5            [11]  171 	push	hl
   40DE CD 65 42      [17]  172 	call	_printf
   40E1 F1            [10]  173 	pop	af
   40E2 F1            [10]  174 	pop	af
                            175 ;src/main.c:81: while (nNumbers--) {
   40E3 DD 4E 04      [19]  176 	ld	c, 4 (ix)
   40E6                     177 00101$:
   40E6 41            [ 4]  178 	ld	b, c
   40E7 0D            [ 4]  179 	dec	c
   40E8 78            [ 4]  180 	ld	a, b
   40E9 B7            [ 4]  181 	or	a, a
   40EA 28 15         [12]  182 	jr	Z,00103$
                            183 ;src/main.c:82: u8 random_number = cpct_rand();  // Get next random number
   40EC C5            [11]  184 	push	bc
   40ED CD D5 41      [17]  185 	call	_cpct_getRandom_mxor_u8
   40F0 C1            [10]  186 	pop	bc
                            187 ;src/main.c:83: printf("%d ", random_number);    // Print it 
   40F1 26 00         [ 7]  188 	ld	h, #0x00
   40F3 C5            [11]  189 	push	bc
   40F4 E5            [11]  190 	push	hl
   40F5 21 34 41      [10]  191 	ld	hl, #___str_4
   40F8 E5            [11]  192 	push	hl
   40F9 CD 65 42      [17]  193 	call	_printf
   40FC F1            [10]  194 	pop	af
   40FD F1            [10]  195 	pop	af
   40FE C1            [10]  196 	pop	bc
   40FF 18 E5         [12]  197 	jr	00101$
   4101                     198 00103$:
                            199 ;src/main.c:87: printf("\n\n\r");
   4101 21 38 41      [10]  200 	ld	hl, #___str_5
   4104 E5            [11]  201 	push	hl
   4105 CD 65 42      [17]  202 	call	_printf
   4108 F1            [10]  203 	pop	af
   4109 DD E1         [14]  204 	pop	ix
   410B C9            [10]  205 	ret
   410C                     206 ___str_3:
   410C 0F                  207 	.db 0x0f
   410D 03                  208 	.db 0x03
   410E 47 65 6E 65 72 61   209 	.ascii "Generating "
        74 69 6E 67 20
   4119 0F                  210 	.db 0x0f
   411A 02                  211 	.db 0x02
   411B 25 64               212 	.ascii "%d"
   411D 0F                  213 	.db 0x0f
   411E 03                  214 	.db 0x03
   411F 20 72 61 6E 64 6F   215 	.ascii " random numbers"
        6D 20 6E 75 6D 62
        65 72 73
   412E 0A                  216 	.db 0x0a
   412F 0A                  217 	.db 0x0a
   4130 0D                  218 	.db 0x0d
   4131 0F                  219 	.db 0x0f
   4132 01                  220 	.db 0x01
   4133 00                  221 	.db 0x00
   4134                     222 ___str_4:
   4134 25 64 20            223 	.ascii "%d "
   4137 00                  224 	.db 0x00
   4138                     225 ___str_5:
   4138 0A                  226 	.db 0x0a
   4139 0A                  227 	.db 0x0a
   413A 0D                  228 	.db 0x0d
   413B 00                  229 	.db 0x00
                            230 ;src/main.c:93: void main(void) {
                            231 ;	---------------------------------
                            232 ; Function main
                            233 ; ---------------------------------
   413C                     234 _main::
                            235 ;src/main.c:95: while (1) {
   413C                     236 00105$:
                            237 ;src/main.c:97: initialize();  
   413C CD 1E 40      [17]  238 	call	_initialize
                            239 ;src/main.c:98: printRandomNumbers(N_RND_NUMBERS);
   413F 3E 32         [ 7]  240 	ld	a, #0x32
   4141 F5            [11]  241 	push	af
   4142 33            [ 6]  242 	inc	sp
   4143 CD CE 40      [17]  243 	call	_printRandomNumbers
   4146 33            [ 6]  244 	inc	sp
                            245 ;src/main.c:101: do { cpct_scanKeyboard_f(); } while ( cpct_isAnyKeyPressed_f() );
   4147                     246 00101$:
   4147 CD 53 41      [17]  247 	call	_cpct_scanKeyboard_f
   414A CD 1D 42      [17]  248 	call	_cpct_isAnyKeyPressed_f
   414D 7D            [ 4]  249 	ld	a, l
   414E B7            [ 4]  250 	or	a, a
   414F 20 F6         [12]  251 	jr	NZ,00101$
   4151 18 E9         [12]  252 	jr	00105$
                            253 	.area _CODE
                            254 	.area _INITIALIZER
                            255 	.area _CABS (ABS)
