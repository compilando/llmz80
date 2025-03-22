;--------------------------------------------------------
; File Created by SDCC : free open source ANSI-C Compiler
; Version 3.6.8 #9946 (Linux)
;--------------------------------------------------------
	.module main
	.optsdcc -mz80
	
;--------------------------------------------------------
; Public variables in this module
;--------------------------------------------------------
	.globl _main
	.globl _checkKeyEvent
	.globl _cpct_akp_SFXGetInstrument
	.globl _cpct_akp_SFXPlay
	.globl _cpct_akp_SFXInit
	.globl _cpct_akp_stop
	.globl _cpct_akp_musicPlay
	.globl _cpct_akp_musicInit
	.globl _cpct_waitVSYNC
	.globl _cpct_setVideoMode
	.globl _cpct_drawCharM2
	.globl _cpct_setDrawCharM2
	.globl _cpct_isKeyPressed
	.globl _cpct_scanKeyboard_f
	.globl _cpct_disableFirmware
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
;src/main.c:36: TKeyStatus checkKeyEvent(cpct_keyID key, TKeyStatus *keystatus) {
;	---------------------------------
; Function checkKeyEvent
; ---------------------------------
_checkKeyEvent::
;src/main.c:40: if ( cpct_isKeyPressed(key) )
	pop	bc
	pop	hl
	push	hl
	push	bc
	call	_cpct_isKeyPressed
	ld	a, l
	or	a, a
	jr	Z,00102$
;src/main.c:41: newstatus = K_PRESSED;   // Key is now pressed
	ld	c, #0x02
	jr	00103$
00102$:
;src/main.c:43: newstatus = K_RELEASED;  // Key is now released
	ld	c, #0x01
00103$:
;src/main.c:47: if (newstatus == *keystatus)
	ld	hl, #4
	add	hl, sp
	ld	e, (hl)
	inc	hl
	ld	d, (hl)
	ld	a, (de)
;src/main.c:48: return K_NOEVENT;       // Same key status, report NO EVENT
	sub	a,c
	jr	NZ,00105$
	ld	l,a
	ret
00105$:
;src/main.c:50: *keystatus = newstatus; // Status has changed, save it...
	ld	a, c
	ld	(de), a
;src/main.c:51: return newstatus;       // And return the new status
	ld	l, c
	ret
;src/main.c:62: void main(void) {
;	---------------------------------
; Function main
; ---------------------------------
_main::
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	hl, #-7
	add	hl, sp
	ld	sp, hl
;src/main.c:64: u8  playing   = 1;               // Flag to know if music is playing or not
	ld	-4 (ix), #0x01
;src/main.c:65: u8  color     = 1;               // Color to draw charactes (normal / inverse)
	ld	-5 (ix), #0x01
;src/main.c:66: u8* pvideomem = CPCT_VMEM_START; // Pointer to video memory where next character will be drawn
	ld	hl, #0xc000
	ex	(sp), hl
;src/main.c:69: k_space = k_0 = k_1 = K_RELEASED;
	ld	-3 (ix), #0x01
	ld	-2 (ix), #0x01
	ld	-1 (ix), #0x01
;src/main.c:72: cpct_disableFirmware();    // Disable firmware to prevent interaction
	call	_cpct_disableFirmware
;src/main.c:73: cpct_setVideoMode(2);      // Set Mode 2 (640x200, 2 colours)
	ld	l, #0x02
	call	_cpct_setVideoMode
;src/main.c:74: cpct_setDrawCharM2(1, 0);  // Set Initial colours for drawCharM2 (Foreground/Background)
	ld	hl, #0x0001
	push	hl
	call	_cpct_setDrawCharM2
;src/main.c:77: cpct_akp_musicInit(molusk_song);    // Initialize the music
	ld	hl, #_molusk_song
	push	hl
	call	_cpct_akp_musicInit
;src/main.c:78: cpct_akp_SFXInit(molusk_song);      // Initialize instruments to be used for SFX (Same as music song)
	ld	hl, #_molusk_song
	ex	(sp),hl
	call	_cpct_akp_SFXInit
	pop	af
;src/main.c:80: while (1) {
00124$:
;src/main.c:84: cpct_waitVSYNC();
	call	_cpct_waitVSYNC
;src/main.c:88: if (playing) {
	ld	a, -4 (ix)
	or	a, a
	jp	Z, 00112$
;src/main.c:89: cpct_akp_musicPlay();   // Play next music 1/50 step.
	call	_cpct_akp_musicPlay
;src/main.c:96: if (cpct_akp_SFXGetInstrument(AY_CHANNEL_A))
	ld	a, #0x01
	push	af
	inc	sp
	call	_cpct_akp_SFXGetInstrument
	inc	sp
;src/main.c:97: cpct_drawCharM2(pvideomem, 'A'); // Write an 'A' because channel A is playing
	pop	bc
	push	bc
;src/main.c:96: if (cpct_akp_SFXGetInstrument(AY_CHANNEL_A))
	ld	a, h
	or	a,l
	jr	Z,00105$
;src/main.c:97: cpct_drawCharM2(pvideomem, 'A'); // Write an 'A' because channel A is playing
	ld	hl, #0x0041
	push	hl
	push	bc
	call	_cpct_drawCharM2
	jr	00106$
00105$:
;src/main.c:100: else if (cpct_akp_SFXGetInstrument(AY_CHANNEL_C))
	push	bc
	ld	a, #0x04
	push	af
	inc	sp
	call	_cpct_akp_SFXGetInstrument
	inc	sp
	pop	bc
	ld	a, h
	or	a,l
	jr	Z,00102$
;src/main.c:101: cpct_drawCharM2(pvideomem, 'C'); // Write an 'C' because channel A is playing 
	ld	hl, #0x0043
	push	hl
	push	bc
	call	_cpct_drawCharM2
	jr	00106$
00102$:
;src/main.c:106: cpct_drawCharM2(pvideomem, '0' + cpct_akp_songLoopTimes);
	ld	hl,#_cpct_akp_songLoopTimes + 0
	ld	c, (hl)
	ld	b, #0x00
	ld	hl, #0x0030
	add	hl, bc
	pop	bc
	push	bc
	push	hl
	push	bc
	call	_cpct_drawCharM2
00106$:
;src/main.c:109: if (++pvideomem >= (u8*)0xC7D0) {
	inc	-7 (ix)
	jr	NZ,00168$
	inc	-6 (ix)
00168$:
	ld	a, -7 (ix)
	sub	a, #0xd0
	ld	a, -6 (ix)
	sbc	a, #0xc7
	jr	C,00108$
;src/main.c:110: pvideomem = CPCT_VMEM_START; // When we reach the end of the screen, we return..
	ld	hl, #0xc000
	ex	(sp), hl
;src/main.c:111: color ^= 1;                  // .. to the start, and change the colour
	ld	a, -5 (ix)
	xor	a, #0x01
;src/main.c:112: cpct_setDrawCharM2(color, color^1); // Set new colour pair for drawCharM2 (inverted from previous one)
	ld	-5 (ix), a
	xor	a, #0x01
	ld	b, a
	push	bc
	inc	sp
	ld	a, -5 (ix)
	push	af
	inc	sp
	call	_cpct_setDrawCharM2
00108$:
;src/main.c:116: if (cpct_akp_songLoopTimes > 0)
	ld	a,(#_cpct_akp_songLoopTimes + 0)
	or	a, a
	jr	Z,00112$
;src/main.c:117: cpct_akp_musicInit(molusk_song); // Song has ended, start it again and set loop to 0
	ld	hl, #_molusk_song
	push	hl
	call	_cpct_akp_musicInit
	pop	af
00112$:
;src/main.c:122: cpct_scanKeyboard_f();
	call	_cpct_scanKeyboard_f
;src/main.c:125: if ( checkKeyEvent(Key_Space, &k_space) == K_RELEASED ) {
	ld	hl, #0x0006
	add	hl, sp
	push	hl
	ld	hl, #0x8005
	push	hl
	call	_checkKeyEvent
	pop	af
	pop	af
	dec	l
	jr	NZ,00121$
;src/main.c:130: if (playing)
	ld	a, -4 (ix)
	or	a, a
	jr	Z,00114$
;src/main.c:131: cpct_akp_stop();
	call	_cpct_akp_stop
00114$:
;src/main.c:134: playing ^= 1;
	ld	a, -4 (ix)
	xor	a, #0x01
	ld	-4 (ix), a
	jp	00124$
00121$:
;src/main.c:137: } else if ( checkKeyEvent(Key_0, &k_0) == K_RELEASED ) {
	ld	hl, #0x0005
	add	hl, sp
	push	hl
	ld	hl, #0x0104
	push	hl
	call	_checkKeyEvent
	pop	af
	pop	af
	dec	l
	jr	NZ,00118$
;src/main.c:138: cpct_akp_SFXPlay(13, 15, 36, 20, 0, AY_CHANNEL_A);
	ld	a, #0x01
	push	af
	inc	sp
	ld	hl, #0x0000
	push	hl
	ld	hl, #0x1424
	push	hl
	ld	hl, #0x0f0d
	push	hl
	call	_cpct_akp_SFXPlay
	ld	hl, #7
	add	hl, sp
	ld	sp, hl
	jp	00124$
00118$:
;src/main.c:141: } else if ( checkKeyEvent(Key_1, &k_1) == K_RELEASED ) 
	ld	hl, #0x0004
	add	hl, sp
	push	hl
	ld	hl, #0x0108
	push	hl
	call	_checkKeyEvent
	pop	af
	pop	af
	dec	l
	jp	NZ,00124$
;src/main.c:142: cpct_akp_SFXPlay(3, 15, 60, 0, 40, AY_CHANNEL_C);
	ld	a, #0x04
	push	af
	inc	sp
	ld	hl, #0x0028
	push	hl
	ld	l, #0x3c
	push	hl
	ld	hl, #0x0f03
	push	hl
	call	_cpct_akp_SFXPlay
	ld	hl, #7
	add	hl, sp
	ld	sp, hl
	jp	00124$
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
