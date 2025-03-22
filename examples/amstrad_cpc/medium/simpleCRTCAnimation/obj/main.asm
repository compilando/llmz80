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
	.globl _open_close_animation
	.globl _initialization
	.globl _cpct_setCRTCReg
	.globl _cpct_setPALColour
	.globl _cpct_waitVSYNC
	.globl _cpct_waitHalts
	.globl _cpct_memset_f8
	.globl _cpct_disableFirmware
	.globl _widths
;--------------------------------------------------------
; special function registers
;--------------------------------------------------------
;--------------------------------------------------------
; ram data
;--------------------------------------------------------
	.area _DATA
_open_close_animation_v_1_129:
	.ds 1
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
;src/main.c:43: void initialization() {
;	---------------------------------
; Function initialization
; ---------------------------------
_initialization::
;src/main.c:45: cpct_disableFirmware();
	call	_cpct_disableFirmware
;src/main.c:47: cpct_setBorder(HW_BLACK);
	ld	hl, #0x1410
	push	hl
	call	_cpct_setPALColour
;src/main.c:49: cpct_memset_f8(CPCT_VMEM_START, 0x35CA, 0x4000);
	ld	hl, #0x4000
	push	hl
	ld	hl, #0x35ca
	push	hl
	ld	hl, #0xc000
	push	hl
	call	_cpct_memset_f8
	ret
_widths:
	.db #0x28	; 40
	.db #0x28	; 40
	.db #0x28	; 40
	.db #0x28	; 40
	.db #0x28	; 40
	.db #0x28	; 40
	.db #0x27	; 39
	.db #0x27	; 39
	.db #0x27	; 39
	.db #0x27	; 39
	.db #0x27	; 39
	.db #0x26	; 38
	.db #0x26	; 38
	.db #0x26	; 38
	.db #0x25	; 37
	.db #0x25	; 37
	.db #0x25	; 37
	.db #0x24	; 36
	.db #0x24	; 36
	.db #0x23	; 35
	.db #0x23	; 35
	.db #0x22	; 34
	.db #0x22	; 34
	.db #0x21	; 33
	.db #0x21	; 33
	.db #0x20	; 32
	.db #0x20	; 32
	.db #0x1f	; 31
	.db #0x1e	; 30
	.db #0x1e	; 30
	.db #0x1d	; 29
	.db #0x1c	; 28
	.db #0x1c	; 28
	.db #0x1b	; 27
	.db #0x1a	; 26
	.db #0x1a	; 26
	.db #0x19	; 25
	.db #0x18	; 24
	.db #0x17	; 23
	.db #0x16	; 22
	.db #0x16	; 22
	.db #0x15	; 21
	.db #0x14	; 20
	.db #0x13	; 19
	.db #0x12	; 18
	.db #0x11	; 17
	.db #0x10	; 16
	.db #0x0f	; 15
	.db #0x0f	; 15
	.db #0x0e	; 14
	.db #0x0d	; 13
	.db #0x0c	; 12
	.db #0x0b	; 11
	.db #0x0a	; 10
	.db #0x09	; 9
	.db #0x08	; 8
	.db #0x07	; 7
	.db #0x06	; 6
	.db #0x05	; 5
	.db #0x04	; 4
	.db #0x03	; 3
	.db #0x02	; 2
	.db #0x01	; 1
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x01	; 1
	.db #0x02	; 2
	.db #0x03	; 3
	.db #0x04	; 4
	.db #0x05	; 5
	.db #0x06	; 6
	.db #0x07	; 7
	.db #0x08	; 8
	.db #0x09	; 9
	.db #0x0a	; 10
	.db #0x0b	; 11
	.db #0x0c	; 12
	.db #0x0d	; 13
	.db #0x0e	; 14
	.db #0x0f	; 15
	.db #0x0f	; 15
	.db #0x10	; 16
	.db #0x11	; 17
	.db #0x12	; 18
	.db #0x13	; 19
	.db #0x14	; 20
	.db #0x15	; 21
	.db #0x16	; 22
	.db #0x16	; 22
	.db #0x17	; 23
	.db #0x18	; 24
	.db #0x19	; 25
	.db #0x1a	; 26
	.db #0x1a	; 26
	.db #0x1b	; 27
	.db #0x1c	; 28
	.db #0x1c	; 28
	.db #0x1d	; 29
	.db #0x1e	; 30
	.db #0x1e	; 30
	.db #0x1f	; 31
	.db #0x20	; 32
	.db #0x20	; 32
	.db #0x21	; 33
	.db #0x21	; 33
	.db #0x22	; 34
	.db #0x22	; 34
	.db #0x23	; 35
	.db #0x23	; 35
	.db #0x24	; 36
	.db #0x24	; 36
	.db #0x25	; 37
	.db #0x25	; 37
	.db #0x25	; 37
	.db #0x26	; 38
	.db #0x26	; 38
	.db #0x26	; 38
	.db #0x27	; 39
	.db #0x27	; 39
	.db #0x27	; 39
	.db #0x27	; 39
	.db #0x27	; 39
	.db #0x28	; 40
	.db #0x28	; 40
	.db #0x28	; 40
	.db #0x28	; 40
	.db #0x28	; 40
	.db #0x28	; 40
;src/main.c:57: void open_close_animation() {
;	---------------------------------
; Function open_close_animation
; ---------------------------------
_open_close_animation::
;src/main.c:61: cpct_setCRTCReg(1, widths[v]);   // Set CRTC Register 1 = Screen Width in characters
	ld	bc, #_widths+0
	ld	hl, (_open_close_animation_v_1_129)
	ld	h, #0x00
	add	hl, bc
	ld	b, (hl)
	push	bc
	inc	sp
	ld	a, #0x01
	push	af
	inc	sp
	call	_cpct_setCRTCReg
;src/main.c:66: v = (v + 1) & 127;
	ld	iy, #_open_close_animation_v_1_129
	ld	a, 0 (iy)
	inc	a
	and	a, #0x7f
	ld	0 (iy), a
	ret
;src/main.c:71: void main(void) {
;	---------------------------------
; Function main
; ---------------------------------
_main::
;src/main.c:72: initialization(); // Initialize the screen
	call	_initialization
;src/main.c:75: while (1) {
00102$:
;src/main.c:76: cpct_waitVSYNC();       // Wait for VSYNC
	call	_cpct_waitVSYNC
;src/main.c:77: open_close_animation(); // Perform animation step
	call	_open_close_animation
;src/main.c:84: cpct_waitHalts(2);      
	ld	l, #0x02
	call	_cpct_waitHalts
	jr	00102$
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
