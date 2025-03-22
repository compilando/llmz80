                              1 ;--------------------------------------------------------
                              2 ; File Created by SDCC : free open source ANSI-C Compiler
                              3 ; Version 3.6.8 #9946 (Linux)
                              4 ;--------------------------------------------------------
                              5 	.module cursor
                              6 	.optsdcc -mz80
                              7 	
                              8 ;--------------------------------------------------------
                              9 ; Public variables in this module
                             10 ;--------------------------------------------------------
                             11 	.globl _map_drawTile
                             12 	.globl _map_getBaseMem
                             13 	.globl _cpct_getScreenPtr
                             14 	.globl _cpct_drawSpriteMasked
                             15 	.globl _cursor_y
                             16 	.globl _cursor_x
                             17 	.globl _cursor_sprite
                             18 	.globl _cursor_setLocation
                             19 	.globl _cursor_draw
                             20 	.globl _cursor_move
                             21 	.globl _cursor_getX
                             22 	.globl _cursor_getY
                             23 ;--------------------------------------------------------
                             24 ; special function registers
                             25 ;--------------------------------------------------------
                             26 ;--------------------------------------------------------
                             27 ; ram data
                             28 ;--------------------------------------------------------
                             29 	.area _DATA
   4773                      30 _cursor_x::
   4773                      31 	.ds 1
   4774                      32 _cursor_y::
   4774                      33 	.ds 1
                             34 ;--------------------------------------------------------
                             35 ; ram data
                             36 ;--------------------------------------------------------
                             37 	.area _INITIALIZED
                             38 ;--------------------------------------------------------
                             39 ; absolute external ram data
                             40 ;--------------------------------------------------------
                             41 	.area _DABS (ABS)
                             42 ;--------------------------------------------------------
                             43 ; global & static initialisations
                             44 ;--------------------------------------------------------
                             45 	.area _HOME
                             46 	.area _GSINIT
                             47 	.area _GSFINAL
                             48 	.area _GSINIT
                             49 ;--------------------------------------------------------
                             50 ; Home
                             51 ;--------------------------------------------------------
                             52 	.area _HOME
                             53 	.area _HOME
                             54 ;--------------------------------------------------------
                             55 ; code
                             56 ;--------------------------------------------------------
                             57 	.area _CODE
                             58 ;src/cursor.c:53: void cursor_setLocation(u8 x, u8 y) {
                             59 ;	---------------------------------
                             60 ; Function cursor_setLocation
                             61 ; ---------------------------------
   4000                      62 _cursor_setLocation::
                             63 ;src/cursor.c:54: cursor_x = x; 
   4000 21 02 00      [10]   64 	ld	hl, #2+0
   4003 39            [11]   65 	add	hl, sp
   4004 7E            [ 7]   66 	ld	a, (hl)
   4005 32 73 47      [13]   67 	ld	(#_cursor_x + 0),a
                             68 ;src/cursor.c:55: cursor_y = y;
   4008 21 03 00      [10]   69 	ld	hl, #3+0
   400B 39            [11]   70 	add	hl, sp
   400C 7E            [ 7]   71 	ld	a, (hl)
   400D 32 74 47      [13]   72 	ld	(#_cursor_y + 0),a
   4010 C9            [10]   73 	ret
   4011                      74 _cursor_sprite:
   4011 00                   75 	.db #0x00	; 0
   4012 FF                   76 	.db #0xff	; 255
   4013 66                   77 	.db #0x66	; 102	'f'
   4014 99                   78 	.db #0x99	; 153
   4015 66                   79 	.db #0x66	; 102	'f'
   4016 99                   80 	.db #0x99	; 153
   4017 00                   81 	.db #0x00	; 0
   4018 FF                   82 	.db #0xff	; 255
                             83 ;src/cursor.c:64: void cursor_draw() {
                             84 ;	---------------------------------
                             85 ; Function cursor_draw
                             86 ; ---------------------------------
   4019                      87 _cursor_draw::
                             88 ;src/cursor.c:68: map_drawTile(cursor_x, cursor_y);
   4019 3A 74 47      [13]   89 	ld	a, (_cursor_y)
   401C F5            [11]   90 	push	af
   401D 33            [ 6]   91 	inc	sp
   401E 3A 73 47      [13]   92 	ld	a, (_cursor_x)
   4021 F5            [11]   93 	push	af
   4022 33            [ 6]   94 	inc	sp
   4023 CD B2 43      [17]   95 	call	_map_drawTile
   4026 F1            [10]   96 	pop	af
                             97 ;src/cursor.c:72: pmem = cpct_getScreenPtr(map_getBaseMem(), cursor_x, cursor_y*TILE_HEIGHT);
   4027 3A 74 47      [13]   98 	ld	a,(#_cursor_y + 0)
   402A 87            [ 4]   99 	add	a, a
   402B 87            [ 4]  100 	add	a, a
   402C 57            [ 4]  101 	ld	d, a
   402D D5            [11]  102 	push	de
   402E CD 5A 43      [17]  103 	call	_map_getBaseMem
   4031 4D            [ 4]  104 	ld	c, l
   4032 44            [ 4]  105 	ld	b, h
   4033 33            [ 6]  106 	inc	sp
   4034 3A 73 47      [13]  107 	ld	a, (_cursor_x)
   4037 F5            [11]  108 	push	af
   4038 33            [ 6]  109 	inc	sp
   4039 C5            [11]  110 	push	bc
   403A CD 59 47      [17]  111 	call	_cpct_getScreenPtr
                            112 ;src/cursor.c:73: cpct_drawSpriteMasked(cursor_sprite, pmem, TILE_WIDTH, TILE_HEIGHT);
   403D 01 11 40      [10]  113 	ld	bc, #_cursor_sprite+0
   4040 11 01 04      [10]  114 	ld	de, #0x0401
   4043 D5            [11]  115 	push	de
   4044 E5            [11]  116 	push	hl
   4045 C5            [11]  117 	push	bc
   4046 CD A9 45      [17]  118 	call	_cpct_drawSpriteMasked
   4049 C9            [10]  119 	ret
                            120 ;src/cursor.c:81: void cursor_move(TMoveDir dir) {
                            121 ;	---------------------------------
                            122 ; Function cursor_move
                            123 ; ---------------------------------
   404A                     124 _cursor_move::
                            125 ;src/cursor.c:84: map_drawTile(cursor_x, cursor_y);
   404A 3A 74 47      [13]  126 	ld	a, (_cursor_y)
   404D F5            [11]  127 	push	af
   404E 33            [ 6]  128 	inc	sp
   404F 3A 73 47      [13]  129 	ld	a, (_cursor_x)
   4052 F5            [11]  130 	push	af
   4053 33            [ 6]  131 	inc	sp
   4054 CD B2 43      [17]  132 	call	_map_drawTile
   4057 F1            [10]  133 	pop	af
                            134 ;src/cursor.c:87: switch(dir) {
   4058 FD 21 02 00   [14]  135 	ld	iy, #2
   405C FD 39         [15]  136 	add	iy, sp
   405E FD 7E 00      [19]  137 	ld	a, 0 (iy)
   4061 B7            [ 4]  138 	or	a, a
   4062 28 17         [12]  139 	jr	Z,00101$
   4064 FD 7E 00      [19]  140 	ld	a, 0 (iy)
   4067 3D            [ 4]  141 	dec	a
   4068 28 18         [12]  142 	jr	Z,00102$
   406A FD 7E 00      [19]  143 	ld	a, 0 (iy)
   406D D6 02         [ 7]  144 	sub	a, #0x02
   406F 28 18         [12]  145 	jr	Z,00103$
   4071 FD 7E 00      [19]  146 	ld	a, 0 (iy)
   4074 D6 03         [ 7]  147 	sub	a, #0x03
   4076 28 18         [12]  148 	jr	Z,00104$
   4078 C3 19 40      [10]  149 	jp	_cursor_draw
                            150 ;src/cursor.c:88: case DIR_LEFT:  cursor_x--; break;
   407B                     151 00101$:
   407B 21 73 47      [10]  152 	ld	hl, #_cursor_x+0
   407E 35            [11]  153 	dec	(hl)
   407F C3 19 40      [10]  154 	jp	_cursor_draw
                            155 ;src/cursor.c:89: case DIR_RIGHT: cursor_x++; break;
   4082                     156 00102$:
   4082 21 73 47      [10]  157 	ld	hl, #_cursor_x+0
   4085 34            [11]  158 	inc	(hl)
   4086 C3 19 40      [10]  159 	jp	_cursor_draw
                            160 ;src/cursor.c:90: case DIR_UP:    cursor_y--; break;
   4089                     161 00103$:
   4089 21 74 47      [10]  162 	ld	hl, #_cursor_y+0
   408C 35            [11]  163 	dec	(hl)
   408D C3 19 40      [10]  164 	jp	_cursor_draw
                            165 ;src/cursor.c:91: case DIR_DOWN:  cursor_y++; break;
   4090                     166 00104$:
   4090 21 74 47      [10]  167 	ld	hl, #_cursor_y+0
   4093 34            [11]  168 	inc	(hl)
                            169 ;src/cursor.c:92: }
                            170 ;src/cursor.c:95: cursor_draw();
   4094 C3 19 40      [10]  171 	jp  _cursor_draw
                            172 ;src/cursor.c:102: u8 cursor_getX() { return cursor_x; }
                            173 ;	---------------------------------
                            174 ; Function cursor_getX
                            175 ; ---------------------------------
   4097                     176 _cursor_getX::
   4097 FD 21 73 47   [14]  177 	ld	iy, #_cursor_x
   409B FD 6E 00      [19]  178 	ld	l, 0 (iy)
   409E C9            [10]  179 	ret
                            180 ;src/cursor.c:103: u8 cursor_getY() { return cursor_y; }
                            181 ;	---------------------------------
                            182 ; Function cursor_getY
                            183 ; ---------------------------------
   409F                     184 _cursor_getY::
   409F FD 21 74 47   [14]  185 	ld	iy, #_cursor_y
   40A3 FD 6E 00      [19]  186 	ld	l, 0 (iy)
   40A6 C9            [10]  187 	ret
                            188 	.area _CODE
                            189 	.area _INITIALIZER
                            190 	.area _CABS (ABS)
