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
                             12 	.globl _MyInterruptWrapper
                             13 	.globl _cpct_drawStringM1
                             14 	.globl _cpct_setDrawCharM1
                             15 	.globl _cpct_setInterruptHandler_naked
                             16 ;--------------------------------------------------------
                             17 ; special function registers
                             18 ;--------------------------------------------------------
                             19 ;--------------------------------------------------------
                             20 ; ram data
                             21 ;--------------------------------------------------------
                             22 	.area _DATA
                             23 ;--------------------------------------------------------
                             24 ; ram data
                             25 ;--------------------------------------------------------
                             26 	.area _INITIALIZED
                             27 ;--------------------------------------------------------
                             28 ; absolute external ram data
                             29 ;--------------------------------------------------------
                             30 	.area _DABS (ABS)
                             31 ;--------------------------------------------------------
                             32 ; global & static initialisations
                             33 ;--------------------------------------------------------
                             34 	.area _HOME
                             35 	.area _GSINIT
                             36 	.area _GSFINAL
                             37 	.area _GSINIT
                             38 ;--------------------------------------------------------
                             39 ; Home
                             40 ;--------------------------------------------------------
                             41 	.area _HOME
                             42 	.area _HOME
                             43 ;--------------------------------------------------------
                             44 ; code
                             45 ;--------------------------------------------------------
                             46 	.area _CODE
                             47 ;src/main.c:26: void main(void) {
                             48 ;	---------------------------------
                             49 ; Function main
                             50 ; ---------------------------------
   403E                      51 _main::
                             52 ;src/main.c:33: cpct_setInterruptHandler_naked(MyInterruptWrapper);
   403E 21 20 40      [10]   53 	ld	hl, #_MyInterruptWrapper
   4041 CD 06 41      [17]   54 	call	_cpct_setInterruptHandler_naked
                             55 ;src/main.c:39: cpct_setDrawCharM1(1, 0);
   4044 21 01 00      [10]   56 	ld	hl, #0x0001
   4047 E5            [11]   57 	push	hl
   4048 CD 12 41      [17]   58 	call	_cpct_setDrawCharM1
                             59 ;src/main.c:42: cpct_drawStringM1("Interrupt Handler Wrapper Example", location);
   404B 21 C6 C3      [10]   60 	ld	hl, #0xc3c6
   404E E5            [11]   61 	push	hl
   404F 21 58 40      [10]   62 	ld	hl, #___str_0
   4052 E5            [11]   63 	push	hl
   4053 CD 86 40      [17]   64 	call	_cpct_drawStringM1
                             65 ;src/main.c:47: while (1);
   4056                      66 00102$:
   4056 18 FE         [12]   67 	jr	00102$
   4058                      68 ___str_0:
   4058 49 6E 74 65 72 72    69 	.ascii "Interrupt Handler Wrapper Example"
        75 70 74 20 48 61
        6E 64 6C 65 72 20
        57 72 61 70 70 65
        72 20 45 78 61 6D
        70 6C 65
   4079 00                   70 	.db 0x00
                             71 	.area _CODE
                             72 	.area _INITIALIZER
                             73 	.area _CABS (ABS)
