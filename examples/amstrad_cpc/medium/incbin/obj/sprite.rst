                              1 ;--------------------------------------------------------
                              2 ; File Created by SDCC : free open source ANSI-C Compiler
                              3 ; Version 3.6.8 #9946 (Linux)
                              4 ;--------------------------------------------------------
                              5 	.module sprite
                              6 	.optsdcc -mz80
                              7 	
                              8 ;--------------------------------------------------------
                              9 ; Public variables in this module
                             10 ;--------------------------------------------------------
                             11 	.globl _G_sprite
                             12 ;--------------------------------------------------------
                             13 ; special function registers
                             14 ;--------------------------------------------------------
                             15 ;--------------------------------------------------------
                             16 ; ram data
                             17 ;--------------------------------------------------------
                             18 	.area _DATA
                             19 ;--------------------------------------------------------
                             20 ; ram data
                             21 ;--------------------------------------------------------
                             22 	.area _INITIALIZED
                             23 ;--------------------------------------------------------
                             24 ; absolute external ram data
                             25 ;--------------------------------------------------------
                             26 	.area _DABS (ABS)
                             27 ;--------------------------------------------------------
                             28 ; global & static initialisations
                             29 ;--------------------------------------------------------
                             30 	.area _HOME
                             31 	.area _GSINIT
                             32 	.area _GSFINAL
                             33 	.area _GSINIT
                             34 ;--------------------------------------------------------
                             35 ; Home
                             36 ;--------------------------------------------------------
                             37 	.area _HOME
                             38 	.area _HOME
                             39 ;--------------------------------------------------------
                             40 ; code
                             41 ;--------------------------------------------------------
                             42 	.area _CODE
                             43 	.area _CODE
   4000                      44 _G_sprite:
   4000 00                   45 	.db #0x00	; 0
   4001 00                   46 	.db #0x00	; 0
   4002 C0                   47 	.db #0xc0	; 192
   4003 C0                   48 	.db #0xc0	; 192
   4004 C0                   49 	.db #0xc0	; 192
   4005 80                   50 	.db #0x80	; 128
   4006 00                   51 	.db #0x00	; 0
   4007 00                   52 	.db #0x00	; 0
   4008 00                   53 	.db #0x00	; 0
   4009 40                   54 	.db #0x40	; 64
   400A C0                   55 	.db #0xc0	; 192
   400B C0                   56 	.db #0xc0	; 192
   400C C0                   57 	.db #0xc0	; 192
   400D C0                   58 	.db #0xc0	; 192
   400E 00                   59 	.db #0x00	; 0
   400F 00                   60 	.db #0x00	; 0
   4010 00                   61 	.db #0x00	; 0
   4011 C0                   62 	.db #0xc0	; 192
   4012 C0                   63 	.db #0xc0	; 192
   4013 C0                   64 	.db #0xc0	; 192
   4014 C0                   65 	.db #0xc0	; 192
   4015 C0                   66 	.db #0xc0	; 192
   4016 80                   67 	.db #0x80	; 128
   4017 00                   68 	.db #0x00	; 0
   4018 40                   69 	.db #0x40	; 64
   4019 C0                   70 	.db #0xc0	; 192
   401A C0                   71 	.db #0xc0	; 192
   401B C0                   72 	.db #0xc0	; 192
   401C C0                   73 	.db #0xc0	; 192
   401D C0                   74 	.db #0xc0	; 192
   401E C0                   75 	.db #0xc0	; 192
   401F 00                   76 	.db #0x00	; 0
   4020 C0                   77 	.db #0xc0	; 192
   4021 0C                   78 	.db #0x0c	; 12
   4022 0C                   79 	.db #0x0c	; 12
   4023 0C                   80 	.db #0x0c	; 12
   4024 0C                   81 	.db #0x0c	; 12
   4025 0C                   82 	.db #0x0c	; 12
   4026 48                   83 	.db #0x48	; 72	'H'
   4027 80                   84 	.db #0x80	; 128
   4028 84                   85 	.db #0x84	; 132
   4029 0C                   86 	.db #0x0c	; 12
   402A 0C                   87 	.db #0x0c	; 12
   402B 0C                   88 	.db #0x0c	; 12
   402C 0C                   89 	.db #0x0c	; 12
   402D 0C                   90 	.db #0x0c	; 12
   402E 0C                   91 	.db #0x0c	; 12
   402F 80                   92 	.db #0x80	; 128
   4030 84                   93 	.db #0x84	; 132
   4031 4C                   94 	.db #0x4c	; 76	'L'
   4032 CC                   95 	.db #0xcc	; 204
   4033 CC                   96 	.db #0xcc	; 204
   4034 CC                   97 	.db #0xcc	; 204
   4035 CC                   98 	.db #0xcc	; 204
   4036 0C                   99 	.db #0x0c	; 12
   4037 80                  100 	.db #0x80	; 128
   4038 84                  101 	.db #0x84	; 132
   4039 4C                  102 	.db #0x4c	; 76	'L'
   403A CC                  103 	.db #0xcc	; 204
   403B CC                  104 	.db #0xcc	; 204
   403C CC                  105 	.db #0xcc	; 204
   403D CC                  106 	.db #0xcc	; 204
   403E 0C                  107 	.db #0x0c	; 12
   403F 80                  108 	.db #0x80	; 128
   4040 84                  109 	.db #0x84	; 132
   4041 0C                  110 	.db #0x0c	; 12
   4042 0C                  111 	.db #0x0c	; 12
   4043 0C                  112 	.db #0x0c	; 12
   4044 0C                  113 	.db #0x0c	; 12
   4045 0C                  114 	.db #0x0c	; 12
   4046 0C                  115 	.db #0x0c	; 12
   4047 80                  116 	.db #0x80	; 128
   4048 C0                  117 	.db #0xc0	; 192
   4049 0C                  118 	.db #0x0c	; 12
   404A 0C                  119 	.db #0x0c	; 12
   404B 0C                  120 	.db #0x0c	; 12
   404C 0C                  121 	.db #0x0c	; 12
   404D 0C                  122 	.db #0x0c	; 12
   404E 48                  123 	.db #0x48	; 72	'H'
   404F 80                  124 	.db #0x80	; 128
   4050 40                  125 	.db #0x40	; 64
   4051 C0                  126 	.db #0xc0	; 192
   4052 C0                  127 	.db #0xc0	; 192
   4053 C0                  128 	.db #0xc0	; 192
   4054 C0                  129 	.db #0xc0	; 192
   4055 C0                  130 	.db #0xc0	; 192
   4056 C0                  131 	.db #0xc0	; 192
   4057 00                  132 	.db #0x00	; 0
   4058 00                  133 	.db #0x00	; 0
   4059 C0                  134 	.db #0xc0	; 192
   405A 48                  135 	.db #0x48	; 72	'H'
   405B C0                  136 	.db #0xc0	; 192
   405C C0                  137 	.db #0xc0	; 192
   405D 48                  138 	.db #0x48	; 72	'H'
   405E 80                  139 	.db #0x80	; 128
   405F 00                  140 	.db #0x00	; 0
   4060 00                  141 	.db #0x00	; 0
   4061 40                  142 	.db #0x40	; 64
   4062 84                  143 	.db #0x84	; 132
   4063 C0                  144 	.db #0xc0	; 192
   4064 84                  145 	.db #0x84	; 132
   4065 C0                  146 	.db #0xc0	; 192
   4066 00                  147 	.db #0x00	; 0
   4067 00                  148 	.db #0x00	; 0
   4068 00                  149 	.db #0x00	; 0
   4069 00                  150 	.db #0x00	; 0
   406A C0                  151 	.db #0xc0	; 192
   406B 0C                  152 	.db #0x0c	; 12
   406C 48                  153 	.db #0x48	; 72	'H'
   406D 80                  154 	.db #0x80	; 128
   406E 00                  155 	.db #0x00	; 0
   406F 00                  156 	.db #0x00	; 0
   4070 00                  157 	.db #0x00	; 0
   4071 00                  158 	.db #0x00	; 0
   4072 40                  159 	.db #0x40	; 64
   4073 C0                  160 	.db #0xc0	; 192
   4074 C0                  161 	.db #0xc0	; 192
   4075 00                  162 	.db #0x00	; 0
   4076 00                  163 	.db #0x00	; 0
   4077 00                  164 	.db #0x00	; 0
   4078 00                  165 	.db #0x00	; 0
   4079 00                  166 	.db #0x00	; 0
   407A 10                  167 	.db #0x10	; 16
   407B C0                  168 	.db #0xc0	; 192
   407C 90                  169 	.db #0x90	; 144
   407D 00                  170 	.db #0x00	; 0
   407E 00                  171 	.db #0x00	; 0
   407F 00                  172 	.db #0x00	; 0
   4080 60                  173 	.db #0x60	; 96
   4081 30                  174 	.db #0x30	; 48	'0'
   4082 30                  175 	.db #0x30	; 48	'0'
   4083 C0                  176 	.db #0xc0	; 192
   4084 90                  177 	.db #0x90	; 144
   4085 30                  178 	.db #0x30	; 48	'0'
   4086 60                  179 	.db #0x60	; 96
   4087 20                  180 	.db #0x20	; 32
   4088 60                  181 	.db #0x60	; 96
   4089 C0                  182 	.db #0xc0	; 192
   408A C0                  183 	.db #0xc0	; 192
   408B C0                  184 	.db #0xc0	; 192
   408C C0                  185 	.db #0xc0	; 192
   408D C0                  186 	.db #0xc0	; 192
   408E C0                  187 	.db #0xc0	; 192
   408F 20                  188 	.db #0x20	; 32
   4090 60                  189 	.db #0x60	; 96
   4091 30                  190 	.db #0x30	; 48	'0'
   4092 30                  191 	.db #0x30	; 48	'0'
   4093 C0                  192 	.db #0xc0	; 192
   4094 90                  193 	.db #0x90	; 144
   4095 30                  194 	.db #0x30	; 48	'0'
   4096 60                  195 	.db #0x60	; 96
   4097 20                  196 	.db #0x20	; 32
   4098 00                  197 	.db #0x00	; 0
   4099 00                  198 	.db #0x00	; 0
   409A 10                  199 	.db #0x10	; 16
   409B C0                  200 	.db #0xc0	; 192
   409C 90                  201 	.db #0x90	; 144
   409D 00                  202 	.db #0x00	; 0
   409E 00                  203 	.db #0x00	; 0
   409F 00                  204 	.db #0x00	; 0
   40A0 00                  205 	.db #0x00	; 0
   40A1 00                  206 	.db #0x00	; 0
   40A2 10                  207 	.db #0x10	; 16
   40A3 C0                  208 	.db #0xc0	; 192
   40A4 90                  209 	.db #0x90	; 144
   40A5 00                  210 	.db #0x00	; 0
   40A6 00                  211 	.db #0x00	; 0
   40A7 00                  212 	.db #0x00	; 0
   40A8 00                  213 	.db #0x00	; 0
   40A9 30                  214 	.db #0x30	; 48	'0'
   40AA 30                  215 	.db #0x30	; 48	'0'
   40AB C0                  216 	.db #0xc0	; 192
   40AC 90                  217 	.db #0x90	; 144
   40AD 30                  218 	.db #0x30	; 48	'0'
   40AE 20                  219 	.db #0x20	; 32
   40AF 00                  220 	.db #0x00	; 0
   40B0 10                  221 	.db #0x10	; 16
   40B1 60                  222 	.db #0x60	; 96
   40B2 C0                  223 	.db #0xc0	; 192
   40B3 C0                  224 	.db #0xc0	; 192
   40B4 C0                  225 	.db #0xc0	; 192
   40B5 C0                  226 	.db #0xc0	; 192
   40B6 30                  227 	.db #0x30	; 48	'0'
   40B7 00                  228 	.db #0x00	; 0
   40B8 10                  229 	.db #0x10	; 16
   40B9 C0                  230 	.db #0xc0	; 192
   40BA C0                  231 	.db #0xc0	; 192
   40BB C0                  232 	.db #0xc0	; 192
   40BC C0                  233 	.db #0xc0	; 192
   40BD C0                  234 	.db #0xc0	; 192
   40BE 90                  235 	.db #0x90	; 144
   40BF 00                  236 	.db #0x00	; 0
                            237 	.area _INITIALIZER
                            238 	.area _CABS (ABS)
