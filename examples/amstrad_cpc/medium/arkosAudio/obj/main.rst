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
                             12 	.globl _checkKeyEvent
                             13 	.globl _cpct_akp_SFXGetInstrument
                             14 	.globl _cpct_akp_SFXPlay
                             15 	.globl _cpct_akp_SFXInit
                             16 	.globl _cpct_akp_stop
                             17 	.globl _cpct_akp_musicPlay
                             18 	.globl _cpct_akp_musicInit
                             19 	.globl _cpct_waitVSYNC
                             20 	.globl _cpct_setVideoMode
                             21 	.globl _cpct_drawCharM2
                             22 	.globl _cpct_setDrawCharM2
                             23 	.globl _cpct_isKeyPressed
                             24 	.globl _cpct_scanKeyboard_f
                             25 	.globl _cpct_disableFirmware
                             26 ;--------------------------------------------------------
                             27 ; special function registers
                             28 ;--------------------------------------------------------
                             29 ;--------------------------------------------------------
                             30 ; ram data
                             31 ;--------------------------------------------------------
                             32 	.area _DATA
                             33 ;--------------------------------------------------------
                             34 ; ram data
                             35 ;--------------------------------------------------------
                             36 	.area _INITIALIZED
                             37 ;--------------------------------------------------------
                             38 ; absolute external ram data
                             39 ;--------------------------------------------------------
                             40 	.area _DABS (ABS)
                             41 ;--------------------------------------------------------
                             42 ; global & static initialisations
                             43 ;--------------------------------------------------------
                             44 	.area _HOME
                             45 	.area _GSINIT
                             46 	.area _GSFINAL
                             47 	.area _GSINIT
                             48 ;--------------------------------------------------------
                             49 ; Home
                             50 ;--------------------------------------------------------
                             51 	.area _HOME
                             52 	.area _HOME
                             53 ;--------------------------------------------------------
                             54 ; code
                             55 ;--------------------------------------------------------
                             56 	.area _CODE
                             57 ;src/main.c:36: TKeyStatus checkKeyEvent(cpct_keyID key, TKeyStatus *keystatus) {
                             58 ;	---------------------------------
                             59 ; Function checkKeyEvent
                             60 ; ---------------------------------
   4000                      61 _checkKeyEvent::
                             62 ;src/main.c:40: if ( cpct_isKeyPressed(key) )
   4000 C1            [10]   63 	pop	bc
   4001 E1            [10]   64 	pop	hl
   4002 E5            [11]   65 	push	hl
   4003 C5            [11]   66 	push	bc
   4004 CD 6E 41      [17]   67 	call	_cpct_isKeyPressed
   4007 7D            [ 4]   68 	ld	a, l
   4008 B7            [ 4]   69 	or	a, a
   4009 28 04         [12]   70 	jr	Z,00102$
                             71 ;src/main.c:41: newstatus = K_PRESSED;   // Key is now pressed
   400B 0E 02         [ 7]   72 	ld	c, #0x02
   400D 18 02         [12]   73 	jr	00103$
   400F                      74 00102$:
                             75 ;src/main.c:43: newstatus = K_RELEASED;  // Key is now released
   400F 0E 01         [ 7]   76 	ld	c, #0x01
   4011                      77 00103$:
                             78 ;src/main.c:47: if (newstatus == *keystatus)
   4011 21 04 00      [10]   79 	ld	hl, #4
   4014 39            [11]   80 	add	hl, sp
   4015 5E            [ 7]   81 	ld	e, (hl)
   4016 23            [ 6]   82 	inc	hl
   4017 56            [ 7]   83 	ld	d, (hl)
   4018 1A            [ 7]   84 	ld	a, (de)
                             85 ;src/main.c:48: return K_NOEVENT;       // Same key status, report NO EVENT
   4019 91            [ 4]   86 	sub	a,c
   401A 20 02         [12]   87 	jr	NZ,00105$
   401C 6F            [ 4]   88 	ld	l,a
   401D C9            [10]   89 	ret
   401E                      90 00105$:
                             91 ;src/main.c:50: *keystatus = newstatus; // Status has changed, save it...
   401E 79            [ 4]   92 	ld	a, c
   401F 12            [ 7]   93 	ld	(de), a
                             94 ;src/main.c:51: return newstatus;       // And return the new status
   4020 69            [ 4]   95 	ld	l, c
   4021 C9            [10]   96 	ret
                             97 ;src/main.c:62: void main(void) {
                             98 ;	---------------------------------
                             99 ; Function main
                            100 ; ---------------------------------
   4022                     101 _main::
   4022 DD E5         [15]  102 	push	ix
   4024 DD 21 00 00   [14]  103 	ld	ix,#0
   4028 DD 39         [15]  104 	add	ix,sp
   402A 21 F9 FF      [10]  105 	ld	hl, #-7
   402D 39            [11]  106 	add	hl, sp
   402E F9            [ 6]  107 	ld	sp, hl
                            108 ;src/main.c:64: u8  playing   = 1;               // Flag to know if music is playing or not
   402F DD 36 FC 01   [19]  109 	ld	-4 (ix), #0x01
                            110 ;src/main.c:65: u8  color     = 1;               // Color to draw charactes (normal / inverse)
   4033 DD 36 FB 01   [19]  111 	ld	-5 (ix), #0x01
                            112 ;src/main.c:66: u8* pvideomem = CPCT_VMEM_START; // Pointer to video memory where next character will be drawn
   4037 21 00 C0      [10]  113 	ld	hl, #0xc000
   403A E3            [19]  114 	ex	(sp), hl
                            115 ;src/main.c:69: k_space = k_0 = k_1 = K_RELEASED;
   403B DD 36 FD 01   [19]  116 	ld	-3 (ix), #0x01
   403F DD 36 FE 01   [19]  117 	ld	-2 (ix), #0x01
   4043 DD 36 FF 01   [19]  118 	ld	-1 (ix), #0x01
                            119 ;src/main.c:72: cpct_disableFirmware();    // Disable firmware to prevent interaction
   4047 CD 48 4A      [17]  120 	call	_cpct_disableFirmware
                            121 ;src/main.c:73: cpct_setVideoMode(2);      // Set Mode 2 (640x200, 2 colours)
   404A 2E 02         [ 7]  122 	ld	l, #0x02
   404C CD 3A 4A      [17]  123 	call	_cpct_setVideoMode
                            124 ;src/main.c:74: cpct_setDrawCharM2(1, 0);  // Set Initial colours for drawCharM2 (Foreground/Background)
   404F 21 01 00      [10]  125 	ld	hl, #0x0001
   4052 E5            [11]  126 	push	hl
   4053 CD 59 4A      [17]  127 	call	_cpct_setDrawCharM2
                            128 ;src/main.c:77: cpct_akp_musicInit(molusk_song);    // Initialize the music
   4056 21 4D 1D      [10]  129 	ld	hl, #_molusk_song
   4059 E5            [11]  130 	push	hl
   405A CD E9 48      [17]  131 	call	_cpct_akp_musicInit
                            132 ;src/main.c:78: cpct_akp_SFXInit(molusk_song);      // Initialize instruments to be used for SFX (Same as music song)
   405D 21 4D 1D      [10]  133 	ld	hl, #_molusk_song
   4060 E3            [19]  134 	ex	(sp),hl
   4061 CD 75 49      [17]  135 	call	_cpct_akp_SFXInit
   4064 F1            [10]  136 	pop	af
                            137 ;src/main.c:80: while (1) {
   4065                     138 00124$:
                            139 ;src/main.c:84: cpct_waitVSYNC();
   4065 CD 32 4A      [17]  140 	call	_cpct_waitVSYNC
                            141 ;src/main.c:88: if (playing) {
   4068 DD 7E FC      [19]  142 	ld	a, -4 (ix)
   406B B7            [ 4]  143 	or	a, a
   406C CA EE 40      [10]  144 	jp	Z, 00112$
                            145 ;src/main.c:89: cpct_akp_musicPlay();   // Play next music 1/50 step.
   406F CD E6 41      [17]  146 	call	_cpct_akp_musicPlay
                            147 ;src/main.c:96: if (cpct_akp_SFXGetInstrument(AY_CHANNEL_A))
   4072 3E 01         [ 7]  148 	ld	a, #0x01
   4074 F5            [11]  149 	push	af
   4075 33            [ 6]  150 	inc	sp
   4076 CD 5C 49      [17]  151 	call	_cpct_akp_SFXGetInstrument
   4079 33            [ 6]  152 	inc	sp
                            153 ;src/main.c:97: cpct_drawCharM2(pvideomem, 'A'); // Write an 'A' because channel A is playing
   407A C1            [10]  154 	pop	bc
   407B C5            [11]  155 	push	bc
                            156 ;src/main.c:96: if (cpct_akp_SFXGetInstrument(AY_CHANNEL_A))
   407C 7C            [ 4]  157 	ld	a, h
   407D B5            [ 4]  158 	or	a,l
   407E 28 0A         [12]  159 	jr	Z,00105$
                            160 ;src/main.c:97: cpct_drawCharM2(pvideomem, 'A'); // Write an 'A' because channel A is playing
   4080 21 41 00      [10]  161 	ld	hl, #0x0041
   4083 E5            [11]  162 	push	hl
   4084 C5            [11]  163 	push	bc
   4085 CD 0D 4A      [17]  164 	call	_cpct_drawCharM2
   4088 18 29         [12]  165 	jr	00106$
   408A                     166 00105$:
                            167 ;src/main.c:100: else if (cpct_akp_SFXGetInstrument(AY_CHANNEL_C))
   408A C5            [11]  168 	push	bc
   408B 3E 04         [ 7]  169 	ld	a, #0x04
   408D F5            [11]  170 	push	af
   408E 33            [ 6]  171 	inc	sp
   408F CD 5C 49      [17]  172 	call	_cpct_akp_SFXGetInstrument
   4092 33            [ 6]  173 	inc	sp
   4093 C1            [10]  174 	pop	bc
   4094 7C            [ 4]  175 	ld	a, h
   4095 B5            [ 4]  176 	or	a,l
   4096 28 0A         [12]  177 	jr	Z,00102$
                            178 ;src/main.c:101: cpct_drawCharM2(pvideomem, 'C'); // Write an 'C' because channel A is playing 
   4098 21 43 00      [10]  179 	ld	hl, #0x0043
   409B E5            [11]  180 	push	hl
   409C C5            [11]  181 	push	bc
   409D CD 0D 4A      [17]  182 	call	_cpct_drawCharM2
   40A0 18 11         [12]  183 	jr	00106$
   40A2                     184 00102$:
                            185 ;src/main.c:106: cpct_drawCharM2(pvideomem, '0' + cpct_akp_songLoopTimes);
   40A2 21 E5 41      [10]  186 	ld	hl,#_cpct_akp_songLoopTimes + 0
   40A5 4E            [ 7]  187 	ld	c, (hl)
   40A6 06 00         [ 7]  188 	ld	b, #0x00
   40A8 21 30 00      [10]  189 	ld	hl, #0x0030
   40AB 09            [11]  190 	add	hl, bc
   40AC C1            [10]  191 	pop	bc
   40AD C5            [11]  192 	push	bc
   40AE E5            [11]  193 	push	hl
   40AF C5            [11]  194 	push	bc
   40B0 CD 0D 4A      [17]  195 	call	_cpct_drawCharM2
   40B3                     196 00106$:
                            197 ;src/main.c:109: if (++pvideomem >= (u8*)0xC7D0) {
   40B3 DD 34 F9      [23]  198 	inc	-7 (ix)
   40B6 20 03         [12]  199 	jr	NZ,00168$
   40B8 DD 34 FA      [23]  200 	inc	-6 (ix)
   40BB                     201 00168$:
   40BB DD 7E F9      [19]  202 	ld	a, -7 (ix)
   40BE D6 D0         [ 7]  203 	sub	a, #0xd0
   40C0 DD 7E FA      [19]  204 	ld	a, -6 (ix)
   40C3 DE C7         [ 7]  205 	sbc	a, #0xc7
   40C5 38 19         [12]  206 	jr	C,00108$
                            207 ;src/main.c:110: pvideomem = CPCT_VMEM_START; // When we reach the end of the screen, we return..
   40C7 21 00 C0      [10]  208 	ld	hl, #0xc000
   40CA E3            [19]  209 	ex	(sp), hl
                            210 ;src/main.c:111: color ^= 1;                  // .. to the start, and change the colour
   40CB DD 7E FB      [19]  211 	ld	a, -5 (ix)
   40CE EE 01         [ 7]  212 	xor	a, #0x01
                            213 ;src/main.c:112: cpct_setDrawCharM2(color, color^1); // Set new colour pair for drawCharM2 (inverted from previous one)
   40D0 DD 77 FB      [19]  214 	ld	-5 (ix), a
   40D3 EE 01         [ 7]  215 	xor	a, #0x01
   40D5 47            [ 4]  216 	ld	b, a
   40D6 C5            [11]  217 	push	bc
   40D7 33            [ 6]  218 	inc	sp
   40D8 DD 7E FB      [19]  219 	ld	a, -5 (ix)
   40DB F5            [11]  220 	push	af
   40DC 33            [ 6]  221 	inc	sp
   40DD CD 59 4A      [17]  222 	call	_cpct_setDrawCharM2
   40E0                     223 00108$:
                            224 ;src/main.c:116: if (cpct_akp_songLoopTimes > 0)
   40E0 3A E5 41      [13]  225 	ld	a,(#_cpct_akp_songLoopTimes + 0)
   40E3 B7            [ 4]  226 	or	a, a
   40E4 28 08         [12]  227 	jr	Z,00112$
                            228 ;src/main.c:117: cpct_akp_musicInit(molusk_song); // Song has ended, start it again and set loop to 0
   40E6 21 4D 1D      [10]  229 	ld	hl, #_molusk_song
   40E9 E5            [11]  230 	push	hl
   40EA CD E9 48      [17]  231 	call	_cpct_akp_musicInit
   40ED F1            [10]  232 	pop	af
   40EE                     233 00112$:
                            234 ;src/main.c:122: cpct_scanKeyboard_f();
   40EE CD 7A 41      [17]  235 	call	_cpct_scanKeyboard_f
                            236 ;src/main.c:125: if ( checkKeyEvent(Key_Space, &k_space) == K_RELEASED ) {
   40F1 21 06 00      [10]  237 	ld	hl, #0x0006
   40F4 39            [11]  238 	add	hl, sp
   40F5 E5            [11]  239 	push	hl
   40F6 21 05 80      [10]  240 	ld	hl, #0x8005
   40F9 E5            [11]  241 	push	hl
   40FA CD 00 40      [17]  242 	call	_checkKeyEvent
   40FD F1            [10]  243 	pop	af
   40FE F1            [10]  244 	pop	af
   40FF 2D            [ 4]  245 	dec	l
   4100 20 14         [12]  246 	jr	NZ,00121$
                            247 ;src/main.c:130: if (playing)
   4102 DD 7E FC      [19]  248 	ld	a, -4 (ix)
   4105 B7            [ 4]  249 	or	a, a
   4106 28 03         [12]  250 	jr	Z,00114$
                            251 ;src/main.c:131: cpct_akp_stop();
   4108 CD 49 49      [17]  252 	call	_cpct_akp_stop
   410B                     253 00114$:
                            254 ;src/main.c:134: playing ^= 1;
   410B DD 7E FC      [19]  255 	ld	a, -4 (ix)
   410E EE 01         [ 7]  256 	xor	a, #0x01
   4110 DD 77 FC      [19]  257 	ld	-4 (ix), a
   4113 C3 65 40      [10]  258 	jp	00124$
   4116                     259 00121$:
                            260 ;src/main.c:137: } else if ( checkKeyEvent(Key_0, &k_0) == K_RELEASED ) {
   4116 21 05 00      [10]  261 	ld	hl, #0x0005
   4119 39            [11]  262 	add	hl, sp
   411A E5            [11]  263 	push	hl
   411B 21 04 01      [10]  264 	ld	hl, #0x0104
   411E E5            [11]  265 	push	hl
   411F CD 00 40      [17]  266 	call	_checkKeyEvent
   4122 F1            [10]  267 	pop	af
   4123 F1            [10]  268 	pop	af
   4124 2D            [ 4]  269 	dec	l
   4125 20 1B         [12]  270 	jr	NZ,00118$
                            271 ;src/main.c:138: cpct_akp_SFXPlay(13, 15, 36, 20, 0, AY_CHANNEL_A);
   4127 3E 01         [ 7]  272 	ld	a, #0x01
   4129 F5            [11]  273 	push	af
   412A 33            [ 6]  274 	inc	sp
   412B 21 00 00      [10]  275 	ld	hl, #0x0000
   412E E5            [11]  276 	push	hl
   412F 21 24 14      [10]  277 	ld	hl, #0x1424
   4132 E5            [11]  278 	push	hl
   4133 21 0D 0F      [10]  279 	ld	hl, #0x0f0d
   4136 E5            [11]  280 	push	hl
   4137 CD 90 49      [17]  281 	call	_cpct_akp_SFXPlay
   413A 21 07 00      [10]  282 	ld	hl, #7
   413D 39            [11]  283 	add	hl, sp
   413E F9            [ 6]  284 	ld	sp, hl
   413F C3 65 40      [10]  285 	jp	00124$
   4142                     286 00118$:
                            287 ;src/main.c:141: } else if ( checkKeyEvent(Key_1, &k_1) == K_RELEASED ) 
   4142 21 04 00      [10]  288 	ld	hl, #0x0004
   4145 39            [11]  289 	add	hl, sp
   4146 E5            [11]  290 	push	hl
   4147 21 08 01      [10]  291 	ld	hl, #0x0108
   414A E5            [11]  292 	push	hl
   414B CD 00 40      [17]  293 	call	_checkKeyEvent
   414E F1            [10]  294 	pop	af
   414F F1            [10]  295 	pop	af
   4150 2D            [ 4]  296 	dec	l
   4151 C2 65 40      [10]  297 	jp	NZ,00124$
                            298 ;src/main.c:142: cpct_akp_SFXPlay(3, 15, 60, 0, 40, AY_CHANNEL_C);
   4154 3E 04         [ 7]  299 	ld	a, #0x04
   4156 F5            [11]  300 	push	af
   4157 33            [ 6]  301 	inc	sp
   4158 21 28 00      [10]  302 	ld	hl, #0x0028
   415B E5            [11]  303 	push	hl
   415C 2E 3C         [ 7]  304 	ld	l, #0x3c
   415E E5            [11]  305 	push	hl
   415F 21 03 0F      [10]  306 	ld	hl, #0x0f03
   4162 E5            [11]  307 	push	hl
   4163 CD 90 49      [17]  308 	call	_cpct_akp_SFXPlay
   4166 21 07 00      [10]  309 	ld	hl, #7
   4169 39            [11]  310 	add	hl, sp
   416A F9            [ 6]  311 	ld	sp, hl
   416B C3 65 40      [10]  312 	jp	00124$
                            313 	.area _CODE
                            314 	.area _INITIALIZER
                            315 	.area _CABS (ABS)
