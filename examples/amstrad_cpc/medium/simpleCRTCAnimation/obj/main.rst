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
                             12 	.globl _open_close_animation
                             13 	.globl _initialization
                             14 	.globl _cpct_setCRTCReg
                             15 	.globl _cpct_setPALColour
                             16 	.globl _cpct_waitVSYNC
                             17 	.globl _cpct_waitHalts
                             18 	.globl _cpct_memset_f8
                             19 	.globl _cpct_disableFirmware
                             20 	.globl _widths
                             21 ;--------------------------------------------------------
                             22 ; special function registers
                             23 ;--------------------------------------------------------
                             24 ;--------------------------------------------------------
                             25 ; ram data
                             26 ;--------------------------------------------------------
                             27 	.area _DATA
   4133                      28 _open_close_animation_v_1_129:
   4133                      29 	.ds 1
                             30 ;--------------------------------------------------------
                             31 ; ram data
                             32 ;--------------------------------------------------------
                             33 	.area _INITIALIZED
                             34 ;--------------------------------------------------------
                             35 ; absolute external ram data
                             36 ;--------------------------------------------------------
                             37 	.area _DABS (ABS)
                             38 ;--------------------------------------------------------
                             39 ; global & static initialisations
                             40 ;--------------------------------------------------------
                             41 	.area _HOME
                             42 	.area _GSINIT
                             43 	.area _GSFINAL
                             44 	.area _GSINIT
                             45 ;--------------------------------------------------------
                             46 ; Home
                             47 ;--------------------------------------------------------
                             48 	.area _HOME
                             49 	.area _HOME
                             50 ;--------------------------------------------------------
                             51 ; code
                             52 ;--------------------------------------------------------
                             53 	.area _CODE
                             54 ;src/main.c:43: void initialization() {
                             55 ;	---------------------------------
                             56 ; Function initialization
                             57 ; ---------------------------------
   4000                      58 _initialization::
                             59 ;src/main.c:45: cpct_disableFirmware();
   4000 CD 14 41      [17]   60 	call	_cpct_disableFirmware
                             61 ;src/main.c:47: cpct_setBorder(HW_BLACK);
   4003 21 10 14      [10]   62 	ld	hl, #0x1410
   4006 E5            [11]   63 	push	hl
   4007 CD CB 40      [17]   64 	call	_cpct_setPALColour
                             65 ;src/main.c:49: cpct_memset_f8(CPCT_VMEM_START, 0x35CA, 0x4000);
   400A 21 00 40      [10]   66 	ld	hl, #0x4000
   400D E5            [11]   67 	push	hl
   400E 21 CA 35      [10]   68 	ld	hl, #0x35ca
   4011 E5            [11]   69 	push	hl
   4012 21 00 C0      [10]   70 	ld	hl, #0xc000
   4015 E5            [11]   71 	push	hl
   4016 CD E4 40      [17]   72 	call	_cpct_memset_f8
   4019 C9            [10]   73 	ret
   401A                      74 _widths:
   401A 28                   75 	.db #0x28	; 40
   401B 28                   76 	.db #0x28	; 40
   401C 28                   77 	.db #0x28	; 40
   401D 28                   78 	.db #0x28	; 40
   401E 28                   79 	.db #0x28	; 40
   401F 28                   80 	.db #0x28	; 40
   4020 27                   81 	.db #0x27	; 39
   4021 27                   82 	.db #0x27	; 39
   4022 27                   83 	.db #0x27	; 39
   4023 27                   84 	.db #0x27	; 39
   4024 27                   85 	.db #0x27	; 39
   4025 26                   86 	.db #0x26	; 38
   4026 26                   87 	.db #0x26	; 38
   4027 26                   88 	.db #0x26	; 38
   4028 25                   89 	.db #0x25	; 37
   4029 25                   90 	.db #0x25	; 37
   402A 25                   91 	.db #0x25	; 37
   402B 24                   92 	.db #0x24	; 36
   402C 24                   93 	.db #0x24	; 36
   402D 23                   94 	.db #0x23	; 35
   402E 23                   95 	.db #0x23	; 35
   402F 22                   96 	.db #0x22	; 34
   4030 22                   97 	.db #0x22	; 34
   4031 21                   98 	.db #0x21	; 33
   4032 21                   99 	.db #0x21	; 33
   4033 20                  100 	.db #0x20	; 32
   4034 20                  101 	.db #0x20	; 32
   4035 1F                  102 	.db #0x1f	; 31
   4036 1E                  103 	.db #0x1e	; 30
   4037 1E                  104 	.db #0x1e	; 30
   4038 1D                  105 	.db #0x1d	; 29
   4039 1C                  106 	.db #0x1c	; 28
   403A 1C                  107 	.db #0x1c	; 28
   403B 1B                  108 	.db #0x1b	; 27
   403C 1A                  109 	.db #0x1a	; 26
   403D 1A                  110 	.db #0x1a	; 26
   403E 19                  111 	.db #0x19	; 25
   403F 18                  112 	.db #0x18	; 24
   4040 17                  113 	.db #0x17	; 23
   4041 16                  114 	.db #0x16	; 22
   4042 16                  115 	.db #0x16	; 22
   4043 15                  116 	.db #0x15	; 21
   4044 14                  117 	.db #0x14	; 20
   4045 13                  118 	.db #0x13	; 19
   4046 12                  119 	.db #0x12	; 18
   4047 11                  120 	.db #0x11	; 17
   4048 10                  121 	.db #0x10	; 16
   4049 0F                  122 	.db #0x0f	; 15
   404A 0F                  123 	.db #0x0f	; 15
   404B 0E                  124 	.db #0x0e	; 14
   404C 0D                  125 	.db #0x0d	; 13
   404D 0C                  126 	.db #0x0c	; 12
   404E 0B                  127 	.db #0x0b	; 11
   404F 0A                  128 	.db #0x0a	; 10
   4050 09                  129 	.db #0x09	; 9
   4051 08                  130 	.db #0x08	; 8
   4052 07                  131 	.db #0x07	; 7
   4053 06                  132 	.db #0x06	; 6
   4054 05                  133 	.db #0x05	; 5
   4055 04                  134 	.db #0x04	; 4
   4056 03                  135 	.db #0x03	; 3
   4057 02                  136 	.db #0x02	; 2
   4058 01                  137 	.db #0x01	; 1
   4059 00                  138 	.db #0x00	; 0
   405A 00                  139 	.db #0x00	; 0
   405B 01                  140 	.db #0x01	; 1
   405C 02                  141 	.db #0x02	; 2
   405D 03                  142 	.db #0x03	; 3
   405E 04                  143 	.db #0x04	; 4
   405F 05                  144 	.db #0x05	; 5
   4060 06                  145 	.db #0x06	; 6
   4061 07                  146 	.db #0x07	; 7
   4062 08                  147 	.db #0x08	; 8
   4063 09                  148 	.db #0x09	; 9
   4064 0A                  149 	.db #0x0a	; 10
   4065 0B                  150 	.db #0x0b	; 11
   4066 0C                  151 	.db #0x0c	; 12
   4067 0D                  152 	.db #0x0d	; 13
   4068 0E                  153 	.db #0x0e	; 14
   4069 0F                  154 	.db #0x0f	; 15
   406A 0F                  155 	.db #0x0f	; 15
   406B 10                  156 	.db #0x10	; 16
   406C 11                  157 	.db #0x11	; 17
   406D 12                  158 	.db #0x12	; 18
   406E 13                  159 	.db #0x13	; 19
   406F 14                  160 	.db #0x14	; 20
   4070 15                  161 	.db #0x15	; 21
   4071 16                  162 	.db #0x16	; 22
   4072 16                  163 	.db #0x16	; 22
   4073 17                  164 	.db #0x17	; 23
   4074 18                  165 	.db #0x18	; 24
   4075 19                  166 	.db #0x19	; 25
   4076 1A                  167 	.db #0x1a	; 26
   4077 1A                  168 	.db #0x1a	; 26
   4078 1B                  169 	.db #0x1b	; 27
   4079 1C                  170 	.db #0x1c	; 28
   407A 1C                  171 	.db #0x1c	; 28
   407B 1D                  172 	.db #0x1d	; 29
   407C 1E                  173 	.db #0x1e	; 30
   407D 1E                  174 	.db #0x1e	; 30
   407E 1F                  175 	.db #0x1f	; 31
   407F 20                  176 	.db #0x20	; 32
   4080 20                  177 	.db #0x20	; 32
   4081 21                  178 	.db #0x21	; 33
   4082 21                  179 	.db #0x21	; 33
   4083 22                  180 	.db #0x22	; 34
   4084 22                  181 	.db #0x22	; 34
   4085 23                  182 	.db #0x23	; 35
   4086 23                  183 	.db #0x23	; 35
   4087 24                  184 	.db #0x24	; 36
   4088 24                  185 	.db #0x24	; 36
   4089 25                  186 	.db #0x25	; 37
   408A 25                  187 	.db #0x25	; 37
   408B 25                  188 	.db #0x25	; 37
   408C 26                  189 	.db #0x26	; 38
   408D 26                  190 	.db #0x26	; 38
   408E 26                  191 	.db #0x26	; 38
   408F 27                  192 	.db #0x27	; 39
   4090 27                  193 	.db #0x27	; 39
   4091 27                  194 	.db #0x27	; 39
   4092 27                  195 	.db #0x27	; 39
   4093 27                  196 	.db #0x27	; 39
   4094 28                  197 	.db #0x28	; 40
   4095 28                  198 	.db #0x28	; 40
   4096 28                  199 	.db #0x28	; 40
   4097 28                  200 	.db #0x28	; 40
   4098 28                  201 	.db #0x28	; 40
   4099 28                  202 	.db #0x28	; 40
                            203 ;src/main.c:57: void open_close_animation() {
                            204 ;	---------------------------------
                            205 ; Function open_close_animation
                            206 ; ---------------------------------
   409A                     207 _open_close_animation::
                            208 ;src/main.c:61: cpct_setCRTCReg(1, widths[v]);   // Set CRTC Register 1 = Screen Width in characters
   409A 01 1A 40      [10]  209 	ld	bc, #_widths+0
   409D 2A 33 41      [16]  210 	ld	hl, (_open_close_animation_v_1_129)
   40A0 26 00         [ 7]  211 	ld	h, #0x00
   40A2 09            [11]  212 	add	hl, bc
   40A3 46            [ 7]  213 	ld	b, (hl)
   40A4 C5            [11]  214 	push	bc
   40A5 33            [ 6]  215 	inc	sp
   40A6 3E 01         [ 7]  216 	ld	a, #0x01
   40A8 F5            [11]  217 	push	af
   40A9 33            [ 6]  218 	inc	sp
   40AA CD 25 41      [17]  219 	call	_cpct_setCRTCReg
                            220 ;src/main.c:66: v = (v + 1) & 127;
   40AD FD 21 33 41   [14]  221 	ld	iy, #_open_close_animation_v_1_129
   40B1 FD 7E 00      [19]  222 	ld	a, 0 (iy)
   40B4 3C            [ 4]  223 	inc	a
   40B5 E6 7F         [ 7]  224 	and	a, #0x7f
   40B7 FD 77 00      [19]  225 	ld	0 (iy), a
   40BA C9            [10]  226 	ret
                            227 ;src/main.c:71: void main(void) {
                            228 ;	---------------------------------
                            229 ; Function main
                            230 ; ---------------------------------
   40BB                     231 _main::
                            232 ;src/main.c:72: initialization(); // Initialize the screen
   40BB CD 00 40      [17]  233 	call	_initialization
                            234 ;src/main.c:75: while (1) {
   40BE                     235 00102$:
                            236 ;src/main.c:76: cpct_waitVSYNC();       // Wait for VSYNC
   40BE CD DC 40      [17]  237 	call	_cpct_waitVSYNC
                            238 ;src/main.c:77: open_close_animation(); // Perform animation step
   40C1 CD 9A 40      [17]  239 	call	_open_close_animation
                            240 ;src/main.c:84: cpct_waitHalts(2);      
   40C4 2E 02         [ 7]  241 	ld	l, #0x02
   40C6 CD D7 40      [17]  242 	call	_cpct_waitHalts
   40C9 18 F3         [12]  243 	jr	00102$
                            244 	.area _CODE
                            245 	.area _INITIALIZER
                            246 	.area _CABS (ABS)
