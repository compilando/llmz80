                              1 ;--------------------------------------------------------
                              2 ; File Created by SDCC : free open source ANSI-C Compiler
                              3 ; Version 3.6.8 #9946 (Linux)
                              4 ;--------------------------------------------------------
                              5 	.module frame_updown
                              6 	.optsdcc -mz80
                              7 	
                              8 ;--------------------------------------------------------
                              9 ; Public variables in this module
                             10 ;--------------------------------------------------------
                             11 	.globl _g_frame_ud
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
   4040                      44 _g_frame_ud:
   4040 0C                   45 	.db #0x0c	; 12
   4041 0C                   46 	.db #0x0c	; 12
   4042 0C                   47 	.db #0x0c	; 12
   4043 0C                   48 	.db #0x0c	; 12
   4044 0C                   49 	.db #0x0c	; 12
   4045 0C                   50 	.db #0x0c	; 12
   4046 0C                   51 	.db #0x0c	; 12
   4047 0C                   52 	.db #0x0c	; 12
   4048 0C                   53 	.db #0x0c	; 12
   4049 0C                   54 	.db #0x0c	; 12
   404A 0C                   55 	.db #0x0c	; 12
   404B 0C                   56 	.db #0x0c	; 12
   404C 0C                   57 	.db #0x0c	; 12
   404D 0C                   58 	.db #0x0c	; 12
   404E 0C                   59 	.db #0x0c	; 12
   404F 0C                   60 	.db #0x0c	; 12
   4050 0C                   61 	.db #0x0c	; 12
   4051 0C                   62 	.db #0x0c	; 12
   4052 0C                   63 	.db #0x0c	; 12
   4053 0C                   64 	.db #0x0c	; 12
   4054 0C                   65 	.db #0x0c	; 12
   4055 00                   66 	.db #0x00	; 0
   4056 01                   67 	.db #0x01	; 1
   4057 00                   68 	.db #0x00	; 0
   4058 01                   69 	.db #0x01	; 1
   4059 00                   70 	.db #0x00	; 0
   405A 01                   71 	.db #0x01	; 1
   405B 00                   72 	.db #0x00	; 0
   405C 01                   73 	.db #0x01	; 1
   405D 00                   74 	.db #0x00	; 0
   405E 01                   75 	.db #0x01	; 1
   405F 00                   76 	.db #0x00	; 0
   4060 01                   77 	.db #0x01	; 1
   4061 00                   78 	.db #0x00	; 0
   4062 01                   79 	.db #0x01	; 1
   4063 00                   80 	.db #0x00	; 0
   4064 01                   81 	.db #0x01	; 1
   4065 00                   82 	.db #0x00	; 0
   4066 01                   83 	.db #0x01	; 1
   4067 00                   84 	.db #0x00	; 0
   4068 01                   85 	.db #0x01	; 1
   4069 00                   86 	.db #0x00	; 0
   406A 06                   87 	.db #0x06	; 6
   406B 07                   88 	.db #0x07	; 7
   406C 06                   89 	.db #0x06	; 6
   406D 07                   90 	.db #0x07	; 7
   406E 06                   91 	.db #0x06	; 6
   406F 07                   92 	.db #0x07	; 7
   4070 06                   93 	.db #0x06	; 6
   4071 07                   94 	.db #0x07	; 7
   4072 06                   95 	.db #0x06	; 6
   4073 07                   96 	.db #0x07	; 7
   4074 06                   97 	.db #0x06	; 6
   4075 07                   98 	.db #0x07	; 7
   4076 06                   99 	.db #0x06	; 6
   4077 07                  100 	.db #0x07	; 7
   4078 06                  101 	.db #0x06	; 6
   4079 07                  102 	.db #0x07	; 7
   407A 06                  103 	.db #0x06	; 6
   407B 07                  104 	.db #0x07	; 7
   407C 06                  105 	.db #0x06	; 6
   407D 07                  106 	.db #0x07	; 7
   407E 06                  107 	.db #0x06	; 6
   407F 0C                  108 	.db #0x0c	; 12
   4080 0C                  109 	.db #0x0c	; 12
   4081 0C                  110 	.db #0x0c	; 12
   4082 0C                  111 	.db #0x0c	; 12
   4083 0C                  112 	.db #0x0c	; 12
   4084 0C                  113 	.db #0x0c	; 12
   4085 0C                  114 	.db #0x0c	; 12
   4086 0C                  115 	.db #0x0c	; 12
   4087 0C                  116 	.db #0x0c	; 12
   4088 0C                  117 	.db #0x0c	; 12
   4089 0C                  118 	.db #0x0c	; 12
   408A 0C                  119 	.db #0x0c	; 12
   408B 0C                  120 	.db #0x0c	; 12
   408C 0C                  121 	.db #0x0c	; 12
   408D 0C                  122 	.db #0x0c	; 12
   408E 0C                  123 	.db #0x0c	; 12
   408F 0C                  124 	.db #0x0c	; 12
   4090 0C                  125 	.db #0x0c	; 12
   4091 0C                  126 	.db #0x0c	; 12
   4092 0C                  127 	.db #0x0c	; 12
   4093 0C                  128 	.db #0x0c	; 12
                            129 	.area _INITIALIZER
                            130 	.area _CABS (ABS)
