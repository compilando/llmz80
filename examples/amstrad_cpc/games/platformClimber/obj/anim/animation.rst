                              1 ;--------------------------------------------------------
                              2 ; File Created by SDCC : free open source ANSI-C Compiler
                              3 ; Version 3.6.8 #9946 (Linux)
                              4 ;--------------------------------------------------------
                              5 	.module animation
                              6 	.optsdcc -mz80
                              7 	
                              8 ;--------------------------------------------------------
                              9 ; Public variables in this module
                             10 ;--------------------------------------------------------
                             11 	.globl _updateAnimation
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
                             43 ;src/anim/animation.c:40: i8 updateAnimation(TAnimation* anim, TAnimFrame** newAnim, TAnimStatus newStatus) {
                             44 ;	---------------------------------
                             45 ; Function updateAnimation
                             46 ; ---------------------------------
   5C89                      47 _updateAnimation::
   5C89 DD E5         [15]   48 	push	ix
   5C8B DD 21 00 00   [14]   49 	ld	ix,#0
   5C8F DD 39         [15]   50 	add	ix,sp
   5C91 21 F8 FF      [10]   51 	ld	hl, #-8
   5C94 39            [11]   52 	add	hl, sp
   5C95 F9            [ 6]   53 	ld	sp, hl
                             54 ;src/anim/animation.c:41: i8 newframe = 0;
   5C96 0E 00         [ 7]   55 	ld	c, #0x00
                             56 ;src/anim/animation.c:45: anim->frames   = newAnim;    // Sets the new animation to the entity
   5C98 DD 5E 04      [19]   57 	ld	e,4 (ix)
   5C9B DD 56 05      [19]   58 	ld	d,5 (ix)
                             59 ;src/anim/animation.c:46: anim->frame_id = 0;          // First frame of the animation
   5C9E 21 02 00      [10]   60 	ld	hl, #0x0002
   5CA1 19            [11]   61 	add	hl,de
   5CA2 DD 75 FE      [19]   62 	ld	-2 (ix), l
   5CA5 DD 74 FF      [19]   63 	ld	-1 (ix), h
                             64 ;src/anim/animation.c:50: anim->time = newAnim[0]->time; // Animation is at its initial timestep
   5CA8 21 03 00      [10]   65 	ld	hl, #0x0003
   5CAB 19            [11]   66 	add	hl,de
   5CAC E3            [19]   67 	ex	(sp), hl
                             68 ;src/anim/animation.c:44: if ( newAnim ) {
   5CAD DD 7E 07      [19]   69 	ld	a, 7 (ix)
   5CB0 DD B6 06      [19]   70 	or	a,6 (ix)
   5CB3 28 2B         [12]   71 	jr	Z,00104$
                             72 ;src/anim/animation.c:45: anim->frames   = newAnim;    // Sets the new animation to the entity
   5CB5 6B            [ 4]   73 	ld	l, e
   5CB6 62            [ 4]   74 	ld	h, d
   5CB7 DD 7E 06      [19]   75 	ld	a, 6 (ix)
   5CBA 77            [ 7]   76 	ld	(hl), a
   5CBB 23            [ 6]   77 	inc	hl
   5CBC DD 7E 07      [19]   78 	ld	a, 7 (ix)
   5CBF 77            [ 7]   79 	ld	(hl), a
                             80 ;src/anim/animation.c:46: anim->frame_id = 0;          // First frame of the animation
   5CC0 DD 6E FE      [19]   81 	ld	l,-2 (ix)
   5CC3 DD 66 FF      [19]   82 	ld	h,-1 (ix)
   5CC6 36 00         [10]   83 	ld	(hl), #0x00
                             84 ;src/anim/animation.c:49: if ( newAnim[0] )
   5CC8 DD 6E 06      [19]   85 	ld	l,6 (ix)
   5CCB DD 66 07      [19]   86 	ld	h,7 (ix)
   5CCE 4E            [ 7]   87 	ld	c, (hl)
   5CCF 23            [ 6]   88 	inc	hl
   5CD0 66            [ 7]   89 	ld	h, (hl)
   5CD1 7C            [ 4]   90 	ld	a, h
   5CD2 B1            [ 4]   91 	or	a,c
   5CD3 28 09         [12]   92 	jr	Z,00102$
                             93 ;src/anim/animation.c:50: anim->time = newAnim[0]->time; // Animation is at its initial timestep
   5CD5 69            [ 4]   94 	ld	l, c
   5CD6 01 04 00      [10]   95 	ld	bc, #0x0004
   5CD9 09            [11]   96 	add	hl, bc
   5CDA 4E            [ 7]   97 	ld	c, (hl)
   5CDB E1            [10]   98 	pop	hl
   5CDC E5            [11]   99 	push	hl
   5CDD 71            [ 7]  100 	ld	(hl), c
   5CDE                     101 00102$:
                            102 ;src/anim/animation.c:52: newframe = 1; // We have changed animation, an that makes this a new frame
   5CDE 0E 01         [ 7]  103 	ld	c, #0x01
   5CE0                     104 00104$:
                            105 ;src/anim/animation.c:57: anim->status = newStatus;  // Set the initial status for the animation    
   5CE0 21 04 00      [10]  106 	ld	hl, #0x0004
   5CE3 19            [11]  107 	add	hl,de
   5CE4 DD 75 FC      [19]  108 	ld	-4 (ix), l
   5CE7 DD 74 FD      [19]  109 	ld	-3 (ix), h
                            110 ;src/anim/animation.c:56: if ( newStatus )
   5CEA DD 7E 08      [19]  111 	ld	a, 8 (ix)
   5CED B7            [ 4]  112 	or	a, a
   5CEE 28 0A         [12]  113 	jr	Z,00106$
                            114 ;src/anim/animation.c:57: anim->status = newStatus;  // Set the initial status for the animation    
   5CF0 DD 6E FC      [19]  115 	ld	l,-4 (ix)
   5CF3 DD 66 FD      [19]  116 	ld	h,-3 (ix)
   5CF6 DD 7E 08      [19]  117 	ld	a, 8 (ix)
   5CF9 77            [ 7]  118 	ld	(hl), a
   5CFA                     119 00106$:
                            120 ;src/anim/animation.c:60: if (anim->status != as_pause && anim->status != as_end) {
   5CFA DD 6E FC      [19]  121 	ld	l,-4 (ix)
   5CFD DD 66 FD      [19]  122 	ld	h,-3 (ix)
   5D00 7E            [ 7]  123 	ld	a, (hl)
   5D01 FE 03         [ 7]  124 	cp	a, #0x03
   5D03 CA 95 5D      [10]  125 	jp	Z,00116$
   5D06 D6 04         [ 7]  126 	sub	a, #0x04
   5D08 CA 95 5D      [10]  127 	jp	Z,00116$
                            128 ;src/anim/animation.c:63: if ( ! --anim->time ) {
   5D0B E1            [10]  129 	pop	hl
   5D0C E5            [11]  130 	push	hl
   5D0D 46            [ 7]  131 	ld	b, (hl)
   5D0E 05            [ 4]  132 	dec	b
   5D0F E1            [10]  133 	pop	hl
   5D10 E5            [11]  134 	push	hl
   5D11 70            [ 7]  135 	ld	(hl), b
   5D12 78            [ 4]  136 	ld	a, b
   5D13 B7            [ 4]  137 	or	a, a
   5D14 C2 95 5D      [10]  138 	jp	NZ, 00116$
                            139 ;src/anim/animation.c:67: newframe = 1;
   5D17 0E 01         [ 7]  140 	ld	c, #0x01
                            141 ;src/anim/animation.c:68: frame = anim->frames[ ++anim->frame_id ];
   5D19 1A            [ 7]  142 	ld	a, (de)
   5D1A DD 77 FA      [19]  143 	ld	-6 (ix), a
   5D1D 13            [ 6]  144 	inc	de
   5D1E 1A            [ 7]  145 	ld	a, (de)
   5D1F DD 77 FB      [19]  146 	ld	-5 (ix), a
   5D22 1B            [ 6]  147 	dec	de
   5D23 DD 6E FE      [19]  148 	ld	l,-2 (ix)
   5D26 DD 66 FF      [19]  149 	ld	h,-1 (ix)
   5D29 46            [ 7]  150 	ld	b, (hl)
   5D2A 04            [ 4]  151 	inc	b
   5D2B DD 6E FE      [19]  152 	ld	l,-2 (ix)
   5D2E DD 66 FF      [19]  153 	ld	h,-1 (ix)
   5D31 70            [ 7]  154 	ld	(hl), b
   5D32 26 00         [ 7]  155 	ld	h, #0x00
   5D34 68            [ 4]  156 	ld	l, b
   5D35 29            [11]  157 	add	hl, hl
   5D36 7D            [ 4]  158 	ld	a, l
   5D37 DD 86 FA      [19]  159 	add	a, -6 (ix)
   5D3A 6F            [ 4]  160 	ld	l, a
   5D3B 7C            [ 4]  161 	ld	a, h
   5D3C DD 8E FB      [19]  162 	adc	a, -5 (ix)
   5D3F 67            [ 4]  163 	ld	h, a
   5D40 7E            [ 7]  164 	ld	a, (hl)
   5D41 23            [ 6]  165 	inc	hl
   5D42 66            [ 7]  166 	ld	h, (hl)
   5D43 6F            [ 4]  167 	ld	l, a
   5D44 E5            [11]  168 	push	hl
   5D45 FD E1         [14]  169 	pop	iy
                            170 ;src/anim/animation.c:71: if (frame) {
   5D47 7C            [ 4]  171 	ld	a, h
   5D48 B5            [ 4]  172 	or	a,l
   5D49 28 0D         [12]  173 	jr	Z,00111$
                            174 ;src/anim/animation.c:73: anim->time = frame->time;
   5D4B FD E5         [15]  175 	push	iy
   5D4D E1            [10]  176 	pop	hl
   5D4E 11 04 00      [10]  177 	ld	de, #0x0004
   5D51 19            [11]  178 	add	hl, de
   5D52 46            [ 7]  179 	ld	b, (hl)
   5D53 E1            [10]  180 	pop	hl
   5D54 E5            [11]  181 	push	hl
   5D55 70            [ 7]  182 	ld	(hl), b
   5D56 18 3D         [12]  183 	jr	00116$
   5D58                     184 00111$:
                            185 ;src/anim/animation.c:74: } else if ( anim->status == as_cycle ) {
   5D58 DD 6E FC      [19]  186 	ld	l,-4 (ix)
   5D5B DD 66 FD      [19]  187 	ld	h,-3 (ix)
   5D5E 7E            [ 7]  188 	ld	a, (hl)
   5D5F D6 02         [ 7]  189 	sub	a, #0x02
   5D61 20 1B         [12]  190 	jr	NZ,00108$
                            191 ;src/anim/animation.c:76: anim->frame_id = 0;
   5D63 DD 6E FE      [19]  192 	ld	l,-2 (ix)
   5D66 DD 66 FF      [19]  193 	ld	h,-1 (ix)
   5D69 36 00         [10]  194 	ld	(hl), #0x00
                            195 ;src/anim/animation.c:77: anim->time     = anim->frames[0]->time;
   5D6B EB            [ 4]  196 	ex	de,hl
   5D6C 46            [ 7]  197 	ld	b, (hl)
   5D6D 23            [ 6]  198 	inc	hl
   5D6E 66            [ 7]  199 	ld	h, (hl)
   5D6F 68            [ 4]  200 	ld	l, b
   5D70 7E            [ 7]  201 	ld	a, (hl)
   5D71 23            [ 6]  202 	inc	hl
   5D72 66            [ 7]  203 	ld	h, (hl)
   5D73 6F            [ 4]  204 	ld	l, a
   5D74 11 04 00      [10]  205 	ld	de, #0x0004
   5D77 19            [11]  206 	add	hl, de
   5D78 5E            [ 7]  207 	ld	e, (hl)
   5D79 E1            [10]  208 	pop	hl
   5D7A E5            [11]  209 	push	hl
   5D7B 73            [ 7]  210 	ld	(hl), e
   5D7C 18 17         [12]  211 	jr	00116$
   5D7E                     212 00108$:
                            213 ;src/anim/animation.c:80: --anim->frame_id;
   5D7E DD 6E FE      [19]  214 	ld	l,-2 (ix)
   5D81 DD 66 FF      [19]  215 	ld	h,-1 (ix)
   5D84 46            [ 7]  216 	ld	b, (hl)
   5D85 05            [ 4]  217 	dec	b
   5D86 DD 6E FE      [19]  218 	ld	l,-2 (ix)
   5D89 DD 66 FF      [19]  219 	ld	h,-1 (ix)
   5D8C 70            [ 7]  220 	ld	(hl), b
                            221 ;src/anim/animation.c:81: anim->status = as_end;
   5D8D DD 6E FC      [19]  222 	ld	l,-4 (ix)
   5D90 DD 66 FD      [19]  223 	ld	h,-3 (ix)
   5D93 36 04         [10]  224 	ld	(hl), #0x04
   5D95                     225 00116$:
                            226 ;src/anim/animation.c:87: return newframe;
   5D95 69            [ 4]  227 	ld	l, c
   5D96 DD F9         [10]  228 	ld	sp, ix
   5D98 DD E1         [14]  229 	pop	ix
   5D9A C9            [10]  230 	ret
                            231 	.area _CODE
                            232 	.area _INITIALIZER
                            233 	.area _CABS (ABS)
