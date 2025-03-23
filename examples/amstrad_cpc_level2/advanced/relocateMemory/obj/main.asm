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
	.globl _wait4KeyPress
	.globl _dummy_data_absorber_102
	.globl _initializeCPC
	.globl _dummy_data_absorber0x4000
	.globl _setUpVideoBuffer
	.globl _cpct_getScreenPtr
	.globl _cpct_setVideoMemoryPage
	.globl _cpct_setPALColour
	.globl _cpct_setPalette
	.globl _cpct_waitVSYNC
	.globl _cpct_setVideoMode
	.globl _cpct_drawStringM0
	.globl _cpct_setDrawCharM0
	.globl _cpct_px2byteM0
	.globl _cpct_isAnyKeyPressed
	.globl _cpct_scanKeyboard
	.globl _cpct_memset_f64
	.globl _cpct_disableFirmware
	.globl _g_buffers
	.globl _g_palette
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
;src/main.c:56: void setUpVideoBuffer(u8* vmem, u16 c_pattern, u8* string, u8 pen, u8 bpen) {
;	---------------------------------
; Function setUpVideoBuffer
; ---------------------------------
_setUpVideoBuffer::
	push	ix
	ld	ix,#0
	add	ix,sp
;src/main.c:57: cpct_memset_f64(vmem, c_pattern, VMEM_SIZE);
	ld	c,4 (ix)
	ld	b,5 (ix)
	push	bc
	ld	hl, #0x4000
	push	hl
	ld	l,6 (ix)
	ld	h,7 (ix)
	push	hl
	push	bc
	call	_cpct_memset_f64
	pop	bc
;src/main.c:58: vmem = cpct_getScreenPtr(vmem, 0, 80);
	ld	hl, #0x5000
	push	hl
	push	bc
	call	_cpct_getScreenPtr
	ld	4 (ix), l
	ld	5 (ix), h
;src/main.c:59: cpct_setDrawCharM0(pen, bpen);
	ld	h, 11 (ix)
	ld	l, 10 (ix)
	push	hl
	call	_cpct_setDrawCharM0
;src/main.c:60: cpct_drawStringM0(string, vmem);
	ld	c,4 (ix)
	ld	b,5 (ix)
	push	bc
	ld	l,8 (ix)
	ld	h,9 (ix)
	push	hl
	call	_cpct_drawStringM0
	pop	ix
	ret
;src/main.c:68: CPCT_ABSOLUTE_LOCATION_AREA(0x4000);
;	---------------------------------
; Function dummy_data_absorber0x4000
; ---------------------------------
_dummy_data_absorber0x4000::
	ret
;src/main.c:68: 
;	---------------------------------
; Function dummy_absolute_0x4000
; ---------------------------------
_dummy_absolute_0x4000::
	.area _0x4000_ (ABS) 
	.org 0x4000 
;src/main.c:84: void initializeCPC() {
;	---------------------------------
; Function initializeCPC
; ---------------------------------
_initializeCPC::
;src/main.c:85: cpct_disableFirmware();          // Disable the firmware not to interfere with us
	call	_cpct_disableFirmware
;src/main.c:86: cpct_setVideoMode(0);            // Set mode 0 (160x200, 16 colours)
	ld	l, #0x00
	call	_cpct_setVideoMode
;src/main.c:87: cpct_setPalette(g_palette, 16);  // Set colour palette
	ld	hl, #0x0010
	push	hl
	ld	hl, #_g_palette
	push	hl
	call	_cpct_setPalette
;src/main.c:88: cpct_setBorder(g_palette[0]);    // Set the border with same colour used for background (0)
	ld	hl, #_g_palette + 0
	ld	b, (hl)
	push	bc
	inc	sp
	ld	a, #0x10
	push	af
	inc	sp
	call	_cpct_setPALColour
;src/main.c:91: setUpVideoBuffer(VMEM_0, 0, "Main Screen Buffer", 6, 0);
	ld	hl, #0x0006
	push	hl
	ld	hl, #___str_0
	push	hl
	ld	hl, #0x0000
	push	hl
	ld	h, #0xc0
	push	hl
	call	_setUpVideoBuffer
	ld	hl, #8
	add	hl, sp
	ld	sp, hl
	ret
_g_palette:
	.db #0x1a	; 26
	.db #0x03	; 3
	.db #0x01	; 1
	.db #0x00	; 0
	.db #0x0d	; 13
	.db #0x19	; 25
	.db #0x14	; 20
	.db #0x12	; 18
	.db #0x16	; 22
	.db #0x15	; 21
	.db #0x13	; 19
	.db #0x06	; 6
	.db #0x07	; 7
	.db #0x08	; 8
	.db #0x02	; 2
	.db #0x0a	; 10
___str_0:
	.ascii "Main Screen Buffer"
	.db 0x00
;src/main.c:102: CPCT_RELOCATABLE_AREA();
;	---------------------------------
; Function dummy_data_absorber_102
; ---------------------------------
_dummy_data_absorber_102::
	ret
;src/main.c:102: 
;	---------------------------------
; Function dummy_relocatable_102
; ---------------------------------
_dummy_relocatable_102::
	.area _CSEG (REL, CON) 
;src/main.c:107: void wait4KeyPress () {
;	---------------------------------
; Function wait4KeyPress
; ---------------------------------
_wait4KeyPress::
;src/main.c:109: do { cpct_scanKeyboard(); } while (  cpct_isAnyKeyPressed() );
00101$:
	call	_cpct_scanKeyboard
	call	_cpct_isAnyKeyPressed
	ld	a, l
	or	a, a
	jr	NZ,00101$
;src/main.c:112: do { cpct_scanKeyboard(); } while ( !cpct_isAnyKeyPressed() );
00104$:
	call	_cpct_scanKeyboard
	call	_cpct_isAnyKeyPressed
	ld	a, l
	or	a, a
	jr	Z,00104$
	ret
;src/main.c:124: void main(void) {
;	---------------------------------
; Function main
; ---------------------------------
_main::
	push	ix
	ld	ix,#0
	add	ix,sp
	dec	sp
;src/main.c:125: u8  scr = 0;      // Video buffer selector: selects what is to be shown on the screen
	ld	-1 (ix), #0x00
;src/main.c:129: initializeCPC();
	call	_initializeCPC
;src/main.c:133: pattern = ( cpct_px2byteM0(4, 6) << 8 ) | cpct_px2byteM0(8, 9);
	ld	hl, #0x0604
	push	hl
	call	_cpct_px2byteM0
	ld	b, l
	ld	c, #0x00
	push	bc
	ld	hl, #0x0908
	push	hl
	call	_cpct_px2byteM0
	pop	bc
	ld	h, #0x00
	ld	a, c
	or	a, l
	ld	c, a
	ld	a, b
	or	a, h
	ld	b, a
;src/main.c:139: setUpVideoBuffer(VMEM_1, pattern, "0x4000 Screen Buffer", 0, 6);
	ld	hl, #0x0600
	push	hl
	ld	hl, #___str_1
	push	hl
	push	bc
	ld	hl, #0x4000
	push	hl
	call	_setUpVideoBuffer
	ld	hl, #8
	add	hl, sp
	ld	sp, hl
;src/main.c:142: while (1) {
00102$:
;src/main.c:145: cpct_waitVSYNC();
	call	_cpct_waitVSYNC
;src/main.c:146: cpct_setVideoMemoryPage(g_buffers[scr]);  // Sets the memory page that will be shown on screen
	ld	bc, #_g_buffers+0
	ld	l,-1 (ix)
	ld	h,#0x00
	add	hl, bc
	ld	l, (hl)
	call	_cpct_setVideoMemoryPage
;src/main.c:150: scr = scr ^ 0x01;    // Does operation scr XOR 1, which alternates the value of the last bit of scr, 
	ld	a, -1 (ix)
	xor	a, #0x01
	ld	-1 (ix), a
;src/main.c:152: wait4KeyPress();
	call	_wait4KeyPress
	jr	00102$
	inc	sp
	pop	ix
	ret
_g_buffers:
	.db #0x30	; 48	'0'
	.db #0x10	; 16
___str_1:
	.ascii "0x4000 Screen Buffer"
	.db 0x00
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
