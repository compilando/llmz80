                              1 ;--------------------------------------------------------
                              2 ; File Created by SDCC : free open source ANSI-C Compiler
                              3 ; Version 3.6.8 #9946 (Linux)
                              4 ;--------------------------------------------------------
                              5 	.module g_palette
                              6 	.optsdcc -mz80
                              7 	
                              8 ;--------------------------------------------------------
                              9 ; Public variables in this module
                             10 ;--------------------------------------------------------
                             11 	.globl _g_palette
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
   0B5A                      44 _g_palette:
   0B5A 40                   45 	.db #0x40	; 64
   0B5B 44                   46 	.db #0x44	; 68	'D'
   0B5C 55                   47 	.db #0x55	; 85	'U'
   0B5D 5C                   48 	.db #0x5c	; 92
   0B5E 4C                   49 	.db #0x4c	; 76	'L'
   0B5F 58                   50 	.db #0x58	; 88	'X'
   0B60 5D                   51 	.db #0x5d	; 93
   0B61 4D                   52 	.db #0x4d	; 77	'M'
   0B62 4F                   53 	.db #0x4f	; 79	'O'
   0B63 56                   54 	.db #0x56	; 86	'V'
   0B64 52                   55 	.db #0x52	; 82	'R'
   0B65 4E                   56 	.db #0x4e	; 78	'N'
   0B66 4A                   57 	.db #0x4a	; 74	'J'
   0B67 54                   58 	.db #0x54	; 84	'T'
   0B68 57                   59 	.db #0x57	; 87	'W'
   0B69 4B                   60 	.db #0x4b	; 75	'K'
                             61 	.area _INITIALIZER
                             62 	.area _CABS (ABS)
