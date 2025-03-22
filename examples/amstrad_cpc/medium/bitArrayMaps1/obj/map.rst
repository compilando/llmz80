                              1 ;--------------------------------------------------------
                              2 ; File Created by SDCC : free open source ANSI-C Compiler
                              3 ; Version 3.6.8 #9946 (Linux)
                              4 ;--------------------------------------------------------
                              5 	.module map
                              6 	.optsdcc -mz80
                              7 	
                              8 ;--------------------------------------------------------
                              9 ; Public variables in this module
                             10 ;--------------------------------------------------------
                             11 	.globl _map_clear
                             12 	.globl _map_changeTile
                             13 	.globl _map_draw
                             14 	.globl _map_drawTile
                             15 	.globl _map_getTile
                             16 	.globl _map_setTile
                             17 	.globl _map_getBaseMem
                             18 	.globl _map_setBaseMem
                             19 	.globl _cpct_getScreenPtr
                             20 	.globl _cpct_drawStringM1
                             21 	.globl _cpct_setDrawCharM1
                             22 	.globl _cpct_drawSolidBox
                             23 	.globl _cpct_px2byteM1
                             24 	.globl _cpct_setBit
                             25 	.globl _cpct_getBit
                             26 	.globl _map_base_location
                             27 	.globl _map
                             28 ;--------------------------------------------------------
                             29 ; special function registers
                             30 ;--------------------------------------------------------
                             31 ;--------------------------------------------------------
                             32 ; ram data
                             33 ;--------------------------------------------------------
                             34 	.area _DATA
   4775                      35 _map_base_location::
   4775                      36 	.ds 2
                             37 ;--------------------------------------------------------
                             38 ; ram data
                             39 ;--------------------------------------------------------
                             40 	.area _INITIALIZED
                             41 ;--------------------------------------------------------
                             42 ; absolute external ram data
                             43 ;--------------------------------------------------------
                             44 	.area _DABS (ABS)
                             45 ;--------------------------------------------------------
                             46 ; global & static initialisations
                             47 ;--------------------------------------------------------
                             48 	.area _HOME
                             49 	.area _GSINIT
                             50 	.area _GSFINAL
                             51 	.area _GSINIT
                             52 ;--------------------------------------------------------
                             53 ; Home
                             54 ;--------------------------------------------------------
                             55 	.area _HOME
                             56 	.area _HOME
                             57 ;--------------------------------------------------------
                             58 ; code
                             59 ;--------------------------------------------------------
                             60 	.area _CODE
                             61 ;src/map.c:97: void map_setBaseMem(u8* mem_location) {
                             62 ;	---------------------------------
                             63 ; Function map_setBaseMem
                             64 ; ---------------------------------
   424F                      65 _map_setBaseMem::
                             66 ;src/map.c:98: map_base_location = mem_location;
   424F 21 02 00      [10]   67 	ld	hl, #2+0
   4252 39            [11]   68 	add	hl, sp
   4253 7E            [ 7]   69 	ld	a, (hl)
   4254 32 75 47      [13]   70 	ld	(#_map_base_location + 0),a
   4257 21 03 00      [10]   71 	ld	hl, #2+1
   425A 39            [11]   72 	add	hl, sp
   425B 7E            [ 7]   73 	ld	a, (hl)
   425C 32 76 47      [13]   74 	ld	(#_map_base_location + 1),a
   425F C9            [10]   75 	ret
   4260                      76 _map:
   4260 FF                   77 	.db #0xff	; 255
   4261 FF                   78 	.db #0xff	; 255
   4262 FF                   79 	.db #0xff	; 255
   4263 FF                   80 	.db #0xff	; 255
   4264 FF                   81 	.db #0xff	; 255
   4265 FF                   82 	.db #0xff	; 255
   4266 FF                   83 	.db #0xff	; 255
   4267 FF                   84 	.db #0xff	; 255
   4268 FF                   85 	.db #0xff	; 255
   4269 FF                   86 	.db #0xff	; 255
   426A C0                   87 	.db #0xc0	; 192
   426B 00                   88 	.db #0x00	; 0
   426C 00                   89 	.db #0x00	; 0
   426D 00                   90 	.db #0x00	; 0
   426E 00                   91 	.db #0x00	; 0
   426F 00                   92 	.db #0x00	; 0
   4270 00                   93 	.db #0x00	; 0
   4271 00                   94 	.db #0x00	; 0
   4272 00                   95 	.db #0x00	; 0
   4273 03                   96 	.db #0x03	; 3
   4274 C0                   97 	.db #0xc0	; 192
   4275 00                   98 	.db #0x00	; 0
   4276 00                   99 	.db #0x00	; 0
   4277 00                  100 	.db #0x00	; 0
   4278 00                  101 	.db #0x00	; 0
   4279 00                  102 	.db #0x00	; 0
   427A 00                  103 	.db #0x00	; 0
   427B 00                  104 	.db #0x00	; 0
   427C 00                  105 	.db #0x00	; 0
   427D 03                  106 	.db #0x03	; 3
   427E C3                  107 	.db #0xc3	; 195
   427F F6                  108 	.db #0xf6	; 246
   4280 5F                  109 	.db #0x5f	; 95
   4281 BF                  110 	.db #0xbf	; 191
   4282 00                  111 	.db #0x00	; 0
   4283 00                  112 	.db #0x00	; 0
   4284 00                  113 	.db #0x00	; 0
   4285 00                  114 	.db #0x00	; 0
   4286 00                  115 	.db #0x00	; 0
   4287 03                  116 	.db #0x03	; 3
   4288 C0                  117 	.db #0xc0	; 192
   4289 C7                  118 	.db #0xc7	; 199
   428A C6                  119 	.db #0xc6	; 198
   428B 30                  120 	.db #0x30	; 48	'0'
   428C 00                  121 	.db #0x00	; 0
   428D 00                  122 	.db #0x00	; 0
   428E 00                  123 	.db #0x00	; 0
   428F 00                  124 	.db #0x00	; 0
   4290 00                  125 	.db #0x00	; 0
   4291 03                  126 	.db #0x03	; 3
   4292 C0                  127 	.db #0xc0	; 192
   4293 C7                  128 	.db #0xc7	; 199
   4294 C6                  129 	.db #0xc6	; 198
   4295 0C                  130 	.db #0x0c	; 12
   4296 00                  131 	.db #0x00	; 0
   4297 00                  132 	.db #0x00	; 0
   4298 00                  133 	.db #0x00	; 0
   4299 00                  134 	.db #0x00	; 0
   429A 00                  135 	.db #0x00	; 0
   429B 03                  136 	.db #0x03	; 3
   429C C0                  137 	.db #0xc0	; 192
   429D C6                  138 	.db #0xc6	; 198
   429E 5F                  139 	.db #0x5f	; 95
   429F BF                  140 	.db #0xbf	; 191
   42A0 00                  141 	.db #0x00	; 0
   42A1 00                  142 	.db #0x00	; 0
   42A2 00                  143 	.db #0x00	; 0
   42A3 00                  144 	.db #0x00	; 0
   42A4 00                  145 	.db #0x00	; 0
   42A5 03                  146 	.db #0x03	; 3
   42A6 C0                  147 	.db #0xc0	; 192
   42A7 00                  148 	.db #0x00	; 0
   42A8 00                  149 	.db #0x00	; 0
   42A9 00                  150 	.db #0x00	; 0
   42AA 00                  151 	.db #0x00	; 0
   42AB 00                  152 	.db #0x00	; 0
   42AC 00                  153 	.db #0x00	; 0
   42AD 00                  154 	.db #0x00	; 0
   42AE 00                  155 	.db #0x00	; 0
   42AF 03                  156 	.db #0x03	; 3
   42B0 C0                  157 	.db #0xc0	; 192
   42B1 00                  158 	.db #0x00	; 0
   42B2 00                  159 	.db #0x00	; 0
   42B3 0F                  160 	.db #0x0f	; 15
   42B4 DF                  161 	.db #0xdf	; 223
   42B5 80                  162 	.db #0x80	; 128
   42B6 00                  163 	.db #0x00	; 0
   42B7 00                  164 	.db #0x00	; 0
   42B8 00                  165 	.db #0x00	; 0
   42B9 03                  166 	.db #0x03	; 3
   42BA C0                  167 	.db #0xc0	; 192
   42BB 00                  168 	.db #0x00	; 0
   42BC 00                  169 	.db #0x00	; 0
   42BD 03                  170 	.db #0x03	; 3
   42BE 0C                  171 	.db #0x0c	; 12
   42BF 00                  172 	.db #0x00	; 0
   42C0 00                  173 	.db #0x00	; 0
   42C1 00                  174 	.db #0x00	; 0
   42C2 00                  175 	.db #0x00	; 0
   42C3 03                  176 	.db #0x03	; 3
   42C4 C0                  177 	.db #0xc0	; 192
   42C5 00                  178 	.db #0x00	; 0
   42C6 00                  179 	.db #0x00	; 0
   42C7 03                  180 	.db #0x03	; 3
   42C8 03                  181 	.db #0x03	; 3
   42C9 00                  182 	.db #0x00	; 0
   42CA 00                  183 	.db #0x00	; 0
   42CB 00                  184 	.db #0x00	; 0
   42CC 00                  185 	.db #0x00	; 0
   42CD 03                  186 	.db #0x03	; 3
   42CE C0                  187 	.db #0xc0	; 192
   42CF 00                  188 	.db #0x00	; 0
   42D0 00                  189 	.db #0x00	; 0
   42D1 0F                  190 	.db #0x0f	; 15
   42D2 DF                  191 	.db #0xdf	; 223
   42D3 80                  192 	.db #0x80	; 128
   42D4 00                  193 	.db #0x00	; 0
   42D5 00                  194 	.db #0x00	; 0
   42D6 00                  195 	.db #0x00	; 0
   42D7 03                  196 	.db #0x03	; 3
   42D8 C0                  197 	.db #0xc0	; 192
   42D9 00                  198 	.db #0x00	; 0
   42DA 00                  199 	.db #0x00	; 0
   42DB 00                  200 	.db #0x00	; 0
   42DC 00                  201 	.db #0x00	; 0
   42DD 00                  202 	.db #0x00	; 0
   42DE 00                  203 	.db #0x00	; 0
   42DF 00                  204 	.db #0x00	; 0
   42E0 00                  205 	.db #0x00	; 0
   42E1 03                  206 	.db #0x03	; 3
   42E2 C0                  207 	.db #0xc0	; 192
   42E3 00                  208 	.db #0x00	; 0
   42E4 00                  209 	.db #0x00	; 0
   42E5 00                  210 	.db #0x00	; 0
   42E6 00                  211 	.db #0x00	; 0
   42E7 30                  212 	.db #0x30	; 48	'0'
   42E8 00                  213 	.db #0x00	; 0
   42E9 00                  214 	.db #0x00	; 0
   42EA 00                  215 	.db #0x00	; 0
   42EB 03                  216 	.db #0x03	; 3
   42EC C0                  217 	.db #0xc0	; 192
   42ED 00                  218 	.db #0x00	; 0
   42EE 00                  219 	.db #0x00	; 0
   42EF 00                  220 	.db #0x00	; 0
   42F0 00                  221 	.db #0x00	; 0
   42F1 48                  222 	.db #0x48	; 72	'H'
   42F2 00                  223 	.db #0x00	; 0
   42F3 00                  224 	.db #0x00	; 0
   42F4 00                  225 	.db #0x00	; 0
   42F5 03                  226 	.db #0x03	; 3
   42F6 C0                  227 	.db #0xc0	; 192
   42F7 00                  228 	.db #0x00	; 0
   42F8 00                  229 	.db #0x00	; 0
   42F9 00                  230 	.db #0x00	; 0
   42FA 00                  231 	.db #0x00	; 0
   42FB FC                  232 	.db #0xfc	; 252
   42FC 00                  233 	.db #0x00	; 0
   42FD 00                  234 	.db #0x00	; 0
   42FE 00                  235 	.db #0x00	; 0
   42FF 03                  236 	.db #0x03	; 3
   4300 C0                  237 	.db #0xc0	; 192
   4301 00                  238 	.db #0x00	; 0
   4302 00                  239 	.db #0x00	; 0
   4303 00                  240 	.db #0x00	; 0
   4304 00                  241 	.db #0x00	; 0
   4305 CC                  242 	.db #0xcc	; 204
   4306 00                  243 	.db #0x00	; 0
   4307 00                  244 	.db #0x00	; 0
   4308 00                  245 	.db #0x00	; 0
   4309 03                  246 	.db #0x03	; 3
   430A C0                  247 	.db #0xc0	; 192
   430B 00                  248 	.db #0x00	; 0
   430C 00                  249 	.db #0x00	; 0
   430D 00                  250 	.db #0x00	; 0
   430E 00                  251 	.db #0x00	; 0
   430F 00                  252 	.db #0x00	; 0
   4310 00                  253 	.db #0x00	; 0
   4311 00                  254 	.db #0x00	; 0
   4312 00                  255 	.db #0x00	; 0
   4313 03                  256 	.db #0x03	; 3
   4314 C0                  257 	.db #0xc0	; 192
   4315 38                  258 	.db #0x38	; 56	'8'
   4316 3E                  259 	.db #0x3e	; 62
   4317 FD                  260 	.db #0xfd	; 253
   4318 F8                  261 	.db #0xf8	; 248
   4319 19                  262 	.db #0x19	; 25
   431A 8C                  263 	.db #0x8c	; 140
   431B 7E                  264 	.db #0x7e	; 126
   431C 00                  265 	.db #0x00	; 0
   431D 03                  266 	.db #0x03	; 3
   431E C0                  267 	.db #0xc0	; 192
   431F 58                  268 	.db #0x58	; 88	'X'
   4320 34                  269 	.db #0x34	; 52	'4'
   4321 30                  270 	.db #0x30	; 48	'0'
   4322 60                  271 	.db #0x60	; 96
   4323 1F                  272 	.db #0x1f	; 31
   4324 92                  273 	.db #0x92	; 146
   4325 66                  274 	.db #0x66	; 102	'f'
   4326 00                  275 	.db #0x00	; 0
   4327 03                  276 	.db #0x03	; 3
   4328 C0                  277 	.db #0xc0	; 192
   4329 18                  278 	.db #0x18	; 24
   432A 32                  279 	.db #0x32	; 50	'2'
   432B 30                  280 	.db #0x30	; 48	'0'
   432C 60                  281 	.db #0x60	; 96
   432D 19                  282 	.db #0x19	; 25
   432E BF                  283 	.db #0xbf	; 191
   432F 7E                  284 	.db #0x7e	; 126
   4330 00                  285 	.db #0x00	; 0
   4331 03                  286 	.db #0x03	; 3
   4332 C0                  287 	.db #0xc0	; 192
   4333 7E                  288 	.db #0x7e	; 126
   4334 3C                  289 	.db #0x3c	; 60
   4335 FC                  290 	.db #0xfc	; 252
   4336 60                  291 	.db #0x60	; 96
   4337 19                  292 	.db #0x19	; 25
   4338 B3                  293 	.db #0xb3	; 179
   4339 60                  294 	.db #0x60	; 96
   433A 00                  295 	.db #0x00	; 0
   433B 03                  296 	.db #0x03	; 3
   433C C0                  297 	.db #0xc0	; 192
   433D 00                  298 	.db #0x00	; 0
   433E 00                  299 	.db #0x00	; 0
   433F 00                  300 	.db #0x00	; 0
   4340 00                  301 	.db #0x00	; 0
   4341 00                  302 	.db #0x00	; 0
   4342 00                  303 	.db #0x00	; 0
   4343 00                  304 	.db #0x00	; 0
   4344 00                  305 	.db #0x00	; 0
   4345 03                  306 	.db #0x03	; 3
   4346 C0                  307 	.db #0xc0	; 192
   4347 00                  308 	.db #0x00	; 0
   4348 00                  309 	.db #0x00	; 0
   4349 00                  310 	.db #0x00	; 0
   434A 00                  311 	.db #0x00	; 0
   434B 00                  312 	.db #0x00	; 0
   434C 00                  313 	.db #0x00	; 0
   434D 00                  314 	.db #0x00	; 0
   434E 00                  315 	.db #0x00	; 0
   434F 03                  316 	.db #0x03	; 3
   4350 FF                  317 	.db #0xff	; 255
   4351 FF                  318 	.db #0xff	; 255
   4352 FF                  319 	.db #0xff	; 255
   4353 FF                  320 	.db #0xff	; 255
   4354 FF                  321 	.db #0xff	; 255
   4355 FF                  322 	.db #0xff	; 255
   4356 FF                  323 	.db #0xff	; 255
   4357 FF                  324 	.db #0xff	; 255
   4358 FF                  325 	.db #0xff	; 255
   4359 FF                  326 	.db #0xff	; 255
                            327 ;src/map.c:106: u8* map_getBaseMem() { return map_base_location; }
                            328 ;	---------------------------------
                            329 ; Function map_getBaseMem
                            330 ; ---------------------------------
   435A                     331 _map_getBaseMem::
   435A 2A 75 47      [16]  332 	ld	hl, (_map_base_location)
   435D C9            [10]  333 	ret
                            334 ;src/map.c:114: void map_setTile(u8 x, u8 y, u8 value) {
                            335 ;	---------------------------------
                            336 ; Function map_setTile
                            337 ; ---------------------------------
   435E                     338 _map_setTile::
   435E DD E5         [15]  339 	push	ix
   4360 DD 21 00 00   [14]  340 	ld	ix,#0
   4364 DD 39         [15]  341 	add	ix,sp
                            342 ;src/map.c:118: u16 tile_index = y * MAP_WIDTH + x;
   4366 DD 4E 05      [19]  343 	ld	c,5 (ix)
   4369 06 00         [ 7]  344 	ld	b,#0x00
   436B 69            [ 4]  345 	ld	l, c
   436C 60            [ 4]  346 	ld	h, b
   436D 29            [11]  347 	add	hl, hl
   436E 29            [11]  348 	add	hl, hl
   436F 09            [11]  349 	add	hl, bc
   4370 29            [11]  350 	add	hl, hl
   4371 29            [11]  351 	add	hl, hl
   4372 29            [11]  352 	add	hl, hl
   4373 29            [11]  353 	add	hl, hl
   4374 DD 4E 04      [19]  354 	ld	c, 4 (ix)
   4377 06 00         [ 7]  355 	ld	b, #0x00
   4379 09            [11]  356 	add	hl, bc
                            357 ;src/map.c:121: cpct_setBit(map, value, tile_index);
   437A DD 5E 06      [19]  358 	ld	e, 6 (ix)
   437D 16 00         [ 7]  359 	ld	d, #0x00
   437F 01 60 42      [10]  360 	ld	bc, #_map+0
   4382 E5            [11]  361 	push	hl
   4383 D5            [11]  362 	push	de
   4384 C5            [11]  363 	push	bc
   4385 CD 7B 45      [17]  364 	call	_cpct_setBit
   4388 DD E1         [14]  365 	pop	ix
   438A C9            [10]  366 	ret
                            367 ;src/map.c:130: u8 map_getTile(u8 x, u8 y) {
                            368 ;	---------------------------------
                            369 ; Function map_getTile
                            370 ; ---------------------------------
   438B                     371 _map_getTile::
   438B DD E5         [15]  372 	push	ix
   438D DD 21 00 00   [14]  373 	ld	ix,#0
   4391 DD 39         [15]  374 	add	ix,sp
                            375 ;src/map.c:134: u16 tile_index = y * MAP_WIDTH + x;
   4393 DD 4E 05      [19]  376 	ld	c,5 (ix)
   4396 06 00         [ 7]  377 	ld	b,#0x00
   4398 69            [ 4]  378 	ld	l, c
   4399 60            [ 4]  379 	ld	h, b
   439A 29            [11]  380 	add	hl, hl
   439B 29            [11]  381 	add	hl, hl
   439C 09            [11]  382 	add	hl, bc
   439D 29            [11]  383 	add	hl, hl
   439E 29            [11]  384 	add	hl, hl
   439F 29            [11]  385 	add	hl, hl
   43A0 29            [11]  386 	add	hl, hl
   43A1 DD 4E 04      [19]  387 	ld	c, 4 (ix)
   43A4 06 00         [ 7]  388 	ld	b, #0x00
   43A6 09            [11]  389 	add	hl, bc
                            390 ;src/map.c:137: u8  tile_value = cpct_getBit(map, tile_index);
   43A7 01 60 42      [10]  391 	ld	bc, #_map+0
   43AA E5            [11]  392 	push	hl
   43AB C5            [11]  393 	push	bc
   43AC CD D9 44      [17]  394 	call	_cpct_getBit
                            395 ;src/map.c:138: return tile_value;
   43AF DD E1         [14]  396 	pop	ix
   43B1 C9            [10]  397 	ret
                            398 ;src/map.c:149: void map_drawTile(u8 x, u8 y) {
                            399 ;	---------------------------------
                            400 ; Function map_drawTile
                            401 ; ---------------------------------
   43B2                     402 _map_drawTile::
   43B2 DD E5         [15]  403 	push	ix
   43B4 DD 21 00 00   [14]  404 	ld	ix,#0
   43B8 DD 39         [15]  405 	add	ix,sp
                            406 ;src/map.c:151: u8 *pmem = cpct_getScreenPtr(map_base_location, x, y*TILE_HEIGHT);
   43BA DD 7E 05      [19]  407 	ld	a, 5 (ix)
   43BD 87            [ 4]  408 	add	a, a
   43BE 87            [ 4]  409 	add	a, a
   43BF 57            [ 4]  410 	ld	d, a
   43C0 ED 4B 75 47   [20]  411 	ld	bc, (_map_base_location)
   43C4 D5            [11]  412 	push	de
   43C5 33            [ 6]  413 	inc	sp
   43C6 DD 7E 04      [19]  414 	ld	a, 4 (ix)
   43C9 F5            [11]  415 	push	af
   43CA 33            [ 6]  416 	inc	sp
   43CB C5            [11]  417 	push	bc
   43CC CD 59 47      [17]  418 	call	_cpct_getScreenPtr
                            419 ;src/map.c:155: u8 c_pattern = cpct_px2byteM1(C_BLACK, C_BLACK, C_BLACK, C_BLACK);
   43CF E5            [11]  420 	push	hl
   43D0 21 00 00      [10]  421 	ld	hl, #0x0000
   43D3 E5            [11]  422 	push	hl
   43D4 2E 00         [ 7]  423 	ld	l, #0x00
   43D6 E5            [11]  424 	push	hl
   43D7 CD FB 45      [17]  425 	call	_cpct_px2byteM1
   43DA F1            [10]  426 	pop	af
   43DB F1            [10]  427 	pop	af
   43DC 5D            [ 4]  428 	ld	e, l
   43DD D5            [11]  429 	push	de
   43DE DD 66 05      [19]  430 	ld	h, 5 (ix)
   43E1 DD 6E 04      [19]  431 	ld	l, 4 (ix)
   43E4 E5            [11]  432 	push	hl
   43E5 CD 8B 43      [17]  433 	call	_map_getTile
   43E8 F1            [10]  434 	pop	af
   43E9 D1            [10]  435 	pop	de
   43EA C1            [10]  436 	pop	bc
   43EB 7D            [ 4]  437 	ld	a, l
   43EC B7            [ 4]  438 	or	a, a
   43ED 28 0F         [12]  439 	jr	Z,00102$
                            440 ;src/map.c:157: c_pattern = cpct_px2byteM1(C_YELLOW, C_YELLOW, C_YELLOW, C_YELLOW);
   43EF C5            [11]  441 	push	bc
   43F0 21 01 01      [10]  442 	ld	hl, #0x0101
   43F3 E5            [11]  443 	push	hl
   43F4 2E 01         [ 7]  444 	ld	l, #0x01
   43F6 E5            [11]  445 	push	hl
   43F7 CD FB 45      [17]  446 	call	_cpct_px2byteM1
   43FA F1            [10]  447 	pop	af
   43FB F1            [10]  448 	pop	af
   43FC 5D            [ 4]  449 	ld	e, l
   43FD C1            [10]  450 	pop	bc
   43FE                     451 00102$:
                            452 ;src/map.c:160: cpct_drawSolidBox(pmem, c_pattern, TILE_WIDTH, TILE_HEIGHT);   
   43FE 16 00         [ 7]  453 	ld	d, #0x00
   4400 21 01 04      [10]  454 	ld	hl, #0x0401
   4403 E5            [11]  455 	push	hl
   4404 D5            [11]  456 	push	de
   4405 C5            [11]  457 	push	bc
   4406 CD 2C 46      [17]  458 	call	_cpct_drawSolidBox
   4409 DD E1         [14]  459 	pop	ix
   440B C9            [10]  460 	ret
                            461 ;src/map.c:168: void map_draw() {
                            462 ;	---------------------------------
                            463 ; Function map_draw
                            464 ; ---------------------------------
   440C                     465 _map_draw::
                            466 ;src/map.c:175: pmem = cpct_getScreenPtr(CPCT_VMEM_START, 30, 160);
   440C 21 1E A0      [10]  467 	ld	hl, #0xa01e
   440F E5            [11]  468 	push	hl
   4410 21 00 C0      [10]  469 	ld	hl, #0xc000
   4413 E5            [11]  470 	push	hl
   4414 CD 59 47      [17]  471 	call	_cpct_getScreenPtr
                            472 ;src/map.c:176: cpct_setDrawCharM1(C_BLACK, C_RED);
   4417 E5            [11]  473 	push	hl
   4418 21 00 03      [10]  474 	ld	hl, #0x0300
   441B E5            [11]  475 	push	hl
   441C CD D4 46      [17]  476 	call	_cpct_setDrawCharM1
   441F C1            [10]  477 	pop	bc
                            478 ;src/map.c:177: cpct_drawStringM1(string, pmem);
   4420 2A 59 44      [16]  479 	ld	hl, (_map_draw_string_1_137)
   4423 C5            [11]  480 	push	bc
   4424 C5            [11]  481 	push	bc
   4425 E5            [11]  482 	push	hl
   4426 CD FB 44      [17]  483 	call	_cpct_drawStringM1
   4429 C1            [10]  484 	pop	bc
                            485 ;src/map.c:180: for(y=0; y < MAP_HEIGHT; y++) 
   442A 1E 00         [ 7]  486 	ld	e, #0x00
                            487 ;src/map.c:181: for(x=0; x < MAP_WIDTH; x++) 
   442C                     488 00109$:
   442C 16 00         [ 7]  489 	ld	d, #0x00
   442E                     490 00103$:
                            491 ;src/map.c:182: map_drawTile(x, y);
   442E C5            [11]  492 	push	bc
   442F D5            [11]  493 	push	de
   4430 7B            [ 4]  494 	ld	a, e
   4431 F5            [11]  495 	push	af
   4432 33            [ 6]  496 	inc	sp
   4433 D5            [11]  497 	push	de
   4434 33            [ 6]  498 	inc	sp
   4435 CD B2 43      [17]  499 	call	_map_drawTile
   4438 F1            [10]  500 	pop	af
   4439 D1            [10]  501 	pop	de
   443A C1            [10]  502 	pop	bc
                            503 ;src/map.c:181: for(x=0; x < MAP_WIDTH; x++) 
   443B 14            [ 4]  504 	inc	d
   443C 7A            [ 4]  505 	ld	a, d
   443D D6 50         [ 7]  506 	sub	a, #0x50
   443F 38 ED         [12]  507 	jr	C,00103$
                            508 ;src/map.c:180: for(y=0; y < MAP_HEIGHT; y++) 
   4441 1C            [ 4]  509 	inc	e
   4442 7B            [ 4]  510 	ld	a, e
   4443 D6 19         [ 7]  511 	sub	a, #0x19
   4445 38 E5         [12]  512 	jr	C,00109$
                            513 ;src/map.c:186: cpct_setDrawCharM1(C_BLACK, C_BLACK);
   4447 C5            [11]  514 	push	bc
   4448 21 00 00      [10]  515 	ld	hl, #0x0000
   444B E5            [11]  516 	push	hl
   444C CD D4 46      [17]  517 	call	_cpct_setDrawCharM1
   444F C1            [10]  518 	pop	bc
                            519 ;src/map.c:187: cpct_drawStringM1(string, pmem);
   4450 2A 59 44      [16]  520 	ld	hl, (_map_draw_string_1_137)
   4453 C5            [11]  521 	push	bc
   4454 E5            [11]  522 	push	hl
   4455 CD FB 44      [17]  523 	call	_cpct_drawStringM1
   4458 C9            [10]  524 	ret
   4459                     525 _map_draw_string_1_137:
   4459 5B 44               526 	.dw ___str_0
   445B                     527 ___str_0:
   445B 44 72 61 77 69 6E   528 	.ascii "Drawing Map"
        67 20 4D 61 70
   4466 00                  529 	.db 0x00
                            530 ;src/map.c:195: void map_changeTile(u8 x, u8 y) {
                            531 ;	---------------------------------
                            532 ; Function map_changeTile
                            533 ; ---------------------------------
   4467                     534 _map_changeTile::
   4467 DD E5         [15]  535 	push	ix
   4469 DD 21 00 00   [14]  536 	ld	ix,#0
   446D DD 39         [15]  537 	add	ix,sp
                            538 ;src/map.c:197: u8 tile = map_getTile(x, y);
   446F DD 66 05      [19]  539 	ld	h, 5 (ix)
   4472 DD 6E 04      [19]  540 	ld	l, 4 (ix)
   4475 E5            [11]  541 	push	hl
   4476 CD 8B 43      [17]  542 	call	_map_getTile
   4479 F1            [10]  543 	pop	af
                            544 ;src/map.c:201: tile = (tile == 0);
   447A 7D            [ 4]  545 	ld	a, l
   447B B7            [ 4]  546 	or	a, a
   447C 20 04         [12]  547 	jr	NZ,00103$
   447E 3E 01         [ 7]  548 	ld	a,#0x01
   4480 18 01         [12]  549 	jr	00104$
   4482                     550 00103$:
   4482 AF            [ 4]  551 	xor	a,a
   4483                     552 00104$:
   4483 47            [ 4]  553 	ld	b, a
                            554 ;src/map.c:204: map_setTile(x, y, tile);
   4484 C5            [11]  555 	push	bc
   4485 33            [ 6]  556 	inc	sp
   4486 DD 66 05      [19]  557 	ld	h, 5 (ix)
   4489 DD 6E 04      [19]  558 	ld	l, 4 (ix)
   448C E5            [11]  559 	push	hl
   448D CD 5E 43      [17]  560 	call	_map_setTile
                            561 ;src/map.c:205: map_drawTile(x, y);
   4490 33            [ 6]  562 	inc	sp
   4491 DD 66 05      [19]  563 	ld	h, 5 (ix)
   4494 DD 6E 04      [19]  564 	ld	l, 4 (ix)
   4497 E3            [19]  565 	ex	(sp),hl
   4498 CD B2 43      [17]  566 	call	_map_drawTile
   449B F1            [10]  567 	pop	af
   449C DD E1         [14]  568 	pop	ix
   449E C9            [10]  569 	ret
                            570 ;src/map.c:213: void map_clear() {
                            571 ;	---------------------------------
                            572 ; Function map_clear
                            573 ; ---------------------------------
   449F                     574 _map_clear::
                            575 ;src/map.c:217: for(y=0; y < MAP_HEIGHT; y++) 
   449F 0E 00         [ 7]  576 	ld	c, #0x00
                            577 ;src/map.c:218: for(x=0; x < MAP_WIDTH; x++) 
   44A1                     578 00109$:
   44A1 06 00         [ 7]  579 	ld	b, #0x00
   44A3                     580 00103$:
                            581 ;src/map.c:219: map_setTile(x, y, 0);
   44A3 C5            [11]  582 	push	bc
   44A4 AF            [ 4]  583 	xor	a, a
   44A5 F5            [11]  584 	push	af
   44A6 33            [ 6]  585 	inc	sp
   44A7 79            [ 4]  586 	ld	a, c
   44A8 F5            [11]  587 	push	af
   44A9 33            [ 6]  588 	inc	sp
   44AA C5            [11]  589 	push	bc
   44AB 33            [ 6]  590 	inc	sp
   44AC CD 5E 43      [17]  591 	call	_map_setTile
   44AF F1            [10]  592 	pop	af
   44B0 33            [ 6]  593 	inc	sp
   44B1 C1            [10]  594 	pop	bc
                            595 ;src/map.c:218: for(x=0; x < MAP_WIDTH; x++) 
   44B2 04            [ 4]  596 	inc	b
   44B3 78            [ 4]  597 	ld	a, b
   44B4 D6 50         [ 7]  598 	sub	a, #0x50
   44B6 38 EB         [12]  599 	jr	C,00103$
                            600 ;src/map.c:217: for(y=0; y < MAP_HEIGHT; y++) 
   44B8 0C            [ 4]  601 	inc	c
   44B9 79            [ 4]  602 	ld	a, c
   44BA D6 19         [ 7]  603 	sub	a, #0x19
   44BC 38 E3         [12]  604 	jr	C,00109$
                            605 ;src/map.c:222: map_draw();
   44BE C3 0C 44      [10]  606 	jp  _map_draw
                            607 	.area _CODE
                            608 	.area _INITIALIZER
                            609 	.area _CABS (ABS)
