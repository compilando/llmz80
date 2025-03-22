;--------------------------------------------------------
; File Created by SDCC : free open source ANSI-C Compiler
; Version 3.6.8 #9946 (Linux)
;--------------------------------------------------------
	.module animation
	.optsdcc -mz80
	
;--------------------------------------------------------
; Public variables in this module
;--------------------------------------------------------
	.globl _updateAnimation
;--------------------------------------------------------
; special function registers
;--------------------------------------------------------
;--------------------------------------------------------
; ram data
;--------------------------------------------------------
	.area _DATA
;--------------------------------------------------------
; ram data
;--------------------------------------------------------
	.area _INITIALIZED
;--------------------------------------------------------
; absolute external ram data
;--------------------------------------------------------
	.area _DABS (ABS)
;--------------------------------------------------------
; global & static initialisations
;--------------------------------------------------------
	.area _HOME
	.area _GSINIT
	.area _GSFINAL
	.area _GSINIT
;--------------------------------------------------------
; Home
;--------------------------------------------------------
	.area _HOME
	.area _HOME
;--------------------------------------------------------
; code
;--------------------------------------------------------
	.area _CODE
;src/anim/animation.c:40: i8 updateAnimation(TAnimation* anim, TAnimFrame** newAnim, TAnimStatus newStatus) {
;	---------------------------------
; Function updateAnimation
; ---------------------------------
_updateAnimation::
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	hl, #-8
	add	hl, sp
	ld	sp, hl
;src/anim/animation.c:41: i8 newframe = 0;
	ld	c, #0x00
;src/anim/animation.c:45: anim->frames   = newAnim;    // Sets the new animation to the entity
	ld	e,4 (ix)
	ld	d,5 (ix)
;src/anim/animation.c:46: anim->frame_id = 0;          // First frame of the animation
	ld	hl, #0x0002
	add	hl,de
	ld	-2 (ix), l
	ld	-1 (ix), h
;src/anim/animation.c:50: anim->time = newAnim[0]->time; // Animation is at its initial timestep
	ld	hl, #0x0003
	add	hl,de
	ex	(sp), hl
;src/anim/animation.c:44: if ( newAnim ) {
	ld	a, 7 (ix)
	or	a,6 (ix)
	jr	Z,00104$
;src/anim/animation.c:45: anim->frames   = newAnim;    // Sets the new animation to the entity
	ld	l, e
	ld	h, d
	ld	a, 6 (ix)
	ld	(hl), a
	inc	hl
	ld	a, 7 (ix)
	ld	(hl), a
;src/anim/animation.c:46: anim->frame_id = 0;          // First frame of the animation
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	ld	(hl), #0x00
;src/anim/animation.c:49: if ( newAnim[0] )
	ld	l,6 (ix)
	ld	h,7 (ix)
	ld	c, (hl)
	inc	hl
	ld	h, (hl)
	ld	a, h
	or	a,c
	jr	Z,00102$
;src/anim/animation.c:50: anim->time = newAnim[0]->time; // Animation is at its initial timestep
	ld	l, c
	ld	bc, #0x0004
	add	hl, bc
	ld	c, (hl)
	pop	hl
	push	hl
	ld	(hl), c
00102$:
;src/anim/animation.c:52: newframe = 1; // We have changed animation, an that makes this a new frame
	ld	c, #0x01
00104$:
;src/anim/animation.c:57: anim->status = newStatus;  // Set the initial status for the animation    
	ld	hl, #0x0004
	add	hl,de
	ld	-4 (ix), l
	ld	-3 (ix), h
;src/anim/animation.c:56: if ( newStatus )
	ld	a, 8 (ix)
	or	a, a
	jr	Z,00106$
;src/anim/animation.c:57: anim->status = newStatus;  // Set the initial status for the animation    
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	a, 8 (ix)
	ld	(hl), a
00106$:
;src/anim/animation.c:60: if (anim->status != as_pause && anim->status != as_end) {
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	a, (hl)
	cp	a, #0x03
	jp	Z,00116$
	sub	a, #0x04
	jp	Z,00116$
;src/anim/animation.c:63: if ( ! --anim->time ) {
	pop	hl
	push	hl
	ld	b, (hl)
	dec	b
	pop	hl
	push	hl
	ld	(hl), b
	ld	a, b
	or	a, a
	jp	NZ, 00116$
;src/anim/animation.c:67: newframe = 1;
	ld	c, #0x01
;src/anim/animation.c:68: frame = anim->frames[ ++anim->frame_id ];
	ld	a, (de)
	ld	-6 (ix), a
	inc	de
	ld	a, (de)
	ld	-5 (ix), a
	dec	de
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	ld	b, (hl)
	inc	b
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	ld	(hl), b
	ld	h, #0x00
	ld	l, b
	add	hl, hl
	ld	a, l
	add	a, -6 (ix)
	ld	l, a
	ld	a, h
	adc	a, -5 (ix)
	ld	h, a
	ld	a, (hl)
	inc	hl
	ld	h, (hl)
	ld	l, a
	push	hl
	pop	iy
;src/anim/animation.c:71: if (frame) {
	ld	a, h
	or	a,l
	jr	Z,00111$
;src/anim/animation.c:73: anim->time = frame->time;
	push	iy
	pop	hl
	ld	de, #0x0004
	add	hl, de
	ld	b, (hl)
	pop	hl
	push	hl
	ld	(hl), b
	jr	00116$
00111$:
;src/anim/animation.c:74: } else if ( anim->status == as_cycle ) {
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	a, (hl)
	sub	a, #0x02
	jr	NZ,00108$
;src/anim/animation.c:76: anim->frame_id = 0;
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	ld	(hl), #0x00
;src/anim/animation.c:77: anim->time     = anim->frames[0]->time;
	ex	de,hl
	ld	b, (hl)
	inc	hl
	ld	h, (hl)
	ld	l, b
	ld	a, (hl)
	inc	hl
	ld	h, (hl)
	ld	l, a
	ld	de, #0x0004
	add	hl, de
	ld	e, (hl)
	pop	hl
	push	hl
	ld	(hl), e
	jr	00116$
00108$:
;src/anim/animation.c:80: --anim->frame_id;
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	ld	b, (hl)
	dec	b
	ld	l,-2 (ix)
	ld	h,-1 (ix)
	ld	(hl), b
;src/anim/animation.c:81: anim->status = as_end;
	ld	l,-4 (ix)
	ld	h,-3 (ix)
	ld	(hl), #0x04
00116$:
;src/anim/animation.c:87: return newframe;
	ld	l, c
	ld	sp, ix
	pop	ix
	ret
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
