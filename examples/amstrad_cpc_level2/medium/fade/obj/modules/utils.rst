                              1 ;--------------------------------------------------------
                              2 ; File Created by SDCC : free open source ANSI-C Compiler
                              3 ; Version 3.6.8 #9946 (Linux)
                              4 ;--------------------------------------------------------
                              5 	.module utils
                              6 	.optsdcc -mz80
                              7 	
                              8 ;--------------------------------------------------------
                              9 ; Public variables in this module
                             10 ;--------------------------------------------------------
                             11 	.globl _cpct_waitVSYNC
                             12 	.globl _wait_frames
                             13 ;--------------------------------------------------------
                             14 ; special function registers
                             15 ;--------------------------------------------------------
                             16 ;--------------------------------------------------------
                             17 ; ram data
                             18 ;--------------------------------------------------------
                             19 	.area _DATA
                             20 ;--------------------------------------------------------
                             21 ; ram data
                             22 ;--------------------------------------------------------
                             23 	.area _INITIALIZED
                             24 ;--------------------------------------------------------
                             25 ; absolute external ram data
                             26 ;--------------------------------------------------------
                             27 	.area _DABS (ABS)
                             28 ;--------------------------------------------------------
                             29 ; global & static initialisations
                             30 ;--------------------------------------------------------
                             31 	.area _HOME
                             32 	.area _GSINIT
                             33 	.area _GSFINAL
                             34 	.area _GSINIT
                             35 ;--------------------------------------------------------
                             36 ; Home
                             37 ;--------------------------------------------------------
                             38 	.area _HOME
                             39 	.area _HOME
                             40 ;--------------------------------------------------------
                             41 ; code
                             42 ;--------------------------------------------------------
                             43 	.area _CODE
                             44 ;src/modules/utils.c:26: void wait_frames(u16 nframes) {
                             45 ;	---------------------------------
                             46 ; Function wait_frames
                             47 ; ---------------------------------
   1E3A                      48 _wait_frames::
   1E3A DD E5         [15]   49 	push	ix
   1E3C DD 21 00 00   [14]   50 	ld	ix,#0
   1E40 DD 39         [15]   51 	add	ix,sp
                             52 ;src/modules/utils.c:30: for (i=0; i < nframes; i++) {
   1E42 01 00 00      [10]   53 	ld	bc, #0x0000
   1E45                      54 00107$:
   1E45 79            [ 4]   55 	ld	a, c
   1E46 DD 96 04      [19]   56 	sub	a, 4 (ix)
   1E49 78            [ 4]   57 	ld	a, b
   1E4A DD 9E 05      [19]   58 	sbc	a, 5 (ix)
   1E4D 30 13         [12]   59 	jr	NC,00109$
                             60 ;src/modules/utils.c:31: cpct_waitVSYNC();
   1E4F C5            [11]   61 	push	bc
   1E50 CD 16 1F      [17]   62 	call	_cpct_waitVSYNC
   1E53 C1            [10]   63 	pop	bc
                             64 ;src/modules/utils.c:38: for (j=0; j < 750; j++);
   1E54 11 EE 02      [10]   65 	ld	de, #0x02ee
   1E57                      66 00105$:
   1E57 EB            [ 4]   67 	ex	de,hl
   1E58 2B            [ 6]   68 	dec	hl
   1E59 5D            [ 4]   69 	ld	e, l
   1E5A 7C            [ 4]   70 	ld	a,h
   1E5B 57            [ 4]   71 	ld	d,a
   1E5C B5            [ 4]   72 	or	a,l
   1E5D 20 F8         [12]   73 	jr	NZ,00105$
                             74 ;src/modules/utils.c:30: for (i=0; i < nframes; i++) {
   1E5F 03            [ 6]   75 	inc	bc
   1E60 18 E3         [12]   76 	jr	00107$
   1E62                      77 00109$:
   1E62 DD E1         [14]   78 	pop	ix
   1E64 C9            [10]   79 	ret
                             80 	.area _CODE
                             81 	.area _INITIALIZER
                             82 	.area _CABS (ABS)
