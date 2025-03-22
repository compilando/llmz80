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
	.globl _changeVideoMemoryPage
	.globl _cpct_getScreenPtr
	.globl _cpct_setVideoMemoryPage
	.globl _cpct_setPALColour
	.globl _cpct_setPalette
	.globl _cpct_fw2hw
	.globl _cpct_waitVSYNC
	.globl _cpct_setVideoMode
	.globl _cpct_drawSprite
	.globl _cpct_memset
	.globl _cpct_disableFirmware
;--------------------------------------------------------
; special function registers
;--------------------------------------------------------
;--------------------------------------------------------
; ram data
;--------------------------------------------------------
	.area _DATA
_changeVideoMemoryPage_cycles_1_129:
	.ds 1
_changeVideoMemoryPage_page_1_129:
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
;src/main.c:45: static u8 cycles = 0;   // Static value to count the number of times this function has been called
	ld	iy, #_changeVideoMemoryPage_cycles_1_129
	ld	0 (iy), #0x00
;src/main.c:46: static u8 page   = 0;   // Static value to remember the last page shown (0 = page 40, 1 = page C0)
	ld	iy, #_changeVideoMemoryPage_page_1_129
	ld	0 (iy), #0x00
;--------------------------------------------------------
; Home
;--------------------------------------------------------
	.area _HOME
	.area _HOME
;--------------------------------------------------------
; code
;--------------------------------------------------------
	.area _CODE
;src/main.c:44: void changeVideoMemoryPage(u8 waitcycles) {
;	---------------------------------
; Function changeVideoMemoryPage
; ---------------------------------
_changeVideoMemoryPage::
;src/main.c:49: if (++cycles >= waitcycles) {     
	ld	iy, #_changeVideoMemoryPage_cycles_1_129
	inc	0 (iy)
	ld	hl, #2
	add	hl, sp
	ld	a, 0 (iy)
	sub	a, (hl)
	ret	C
;src/main.c:50: cycles = 0;    // We have arrived, restore count to 0
	ld	0 (iy), #0x00
;src/main.c:54: if (page) {
	ld	a,(#_changeVideoMemoryPage_page_1_129 + 0)
	or	a, a
	jr	Z,00102$
;src/main.c:55: cpct_setVideoMemoryPage(cpct_pageC0);  // Set video memory at banck 3 (0xC000 - 0xFFFF)
	ld	l, #0x30
	call	_cpct_setVideoMemoryPage
;src/main.c:56: page = 0;                              // Next page = 0
	ld	hl,#_changeVideoMemoryPage_page_1_129 + 0
	ld	(hl), #0x00
	ret
00102$:
;src/main.c:58: cpct_setVideoMemoryPage(cpct_page40);  // Set video memory at banck 1 (0x4000 - 0x7FFF)
	ld	l, #0x10
	call	_cpct_setVideoMemoryPage
;src/main.c:59: page = 1;                              // Next page = 1
	ld	hl,#_changeVideoMemoryPage_page_1_129 + 0
	ld	(hl), #0x01
	ret
;src/main.c:69: void main(void) {
;	---------------------------------
; Function main
; ---------------------------------
_main::
	push	ix
	ld	ix,#0
	add	ix,sp
	push	af
;src/main.c:70: u8  br_y = 55; // Y coordinate of the ByteRealms Logo 
	ld	-1 (ix), #0x37
;src/main.c:71: i8  vy   = 1;  // Velocity of the ByteRealms Logo in Y axis
	ld	-2 (ix), #0x01
;src/main.c:75: cpct_disableFirmware();             // Disable firmware to prevent it from interfering
	call	_cpct_disableFirmware
;src/main.c:76: cpct_fw2hw       (G_palette, 16);   // Convert Firmware colours to Hardware colours 
	ld	hl, #0x0010
	push	hl
	ld	hl, #_G_palette
	push	hl
	call	_cpct_fw2hw
;src/main.c:77: cpct_setPalette  (G_palette, 16);   // Set up palette using hardware colours
	ld	hl, #0x0010
	push	hl
	ld	hl, #_G_palette
	push	hl
	call	_cpct_setPalette
;src/main.c:78: cpct_setBorder   (G_palette[0]);    // Set up the border to the background colour (white)
	ld	hl, #_G_palette + 0
	ld	b, (hl)
	push	bc
	inc	sp
	ld	a, #0x10
	push	af
	inc	sp
	call	_cpct_setPALColour
;src/main.c:79: cpct_setVideoMode(0);               // Change to Mode 0 (160x200, 16 colours)
	ld	l, #0x00
	call	_cpct_setVideoMode
;src/main.c:82: cpct_memset(CPCT_VMEM_START, 0x00, 0x4000);
	ld	hl, #0x4000
	push	hl
	xor	a, a
	push	af
	inc	sp
	ld	h, #0xc0
	push	hl
	call	_cpct_memset
;src/main.c:83: cpct_memset(       SCR_BUFF, 0x00, 0x4000);
	ld	hl, #0x4000
	push	hl
	xor	a, a
	push	af
	inc	sp
	ld	l, #0x00
	push	hl
	call	_cpct_memset
;src/main.c:90: pvmem = cpct_getScreenPtr(SCR_BUFF, 0,   52);
	ld	hl, #0x3400
	push	hl
	ld	h, #0x40
	push	hl
	call	_cpct_getScreenPtr
	ld	c, l
	ld	b, h
;src/main.c:91: cpct_drawSprite(G_CPCt_left,  pvmem,          CPCT_W, CPCT_H);
	ld	e, c
	ld	d, b
	push	bc
	ld	hl, #0x6028
	push	hl
	push	de
	ld	hl, #_G_CPCt_left
	push	hl
	call	_cpct_drawSprite
	pop	bc
;src/main.c:92: cpct_drawSprite(G_CPCt_right, pvmem + CPCT_W, CPCT_W, CPCT_H);
	ld	hl, #0x0028
	add	hl, bc
	ld	bc, #_G_CPCt_right+0
	ld	de, #0x6028
	push	de
	push	hl
	push	bc
	call	_cpct_drawSprite
;src/main.c:97: while(1) {
00105$:
;src/main.c:101: pvmem = cpct_getScreenPtr(CPCT_VMEM_START, 10, br_y);  // Locate sprite at (10,br_y) in Default Video Memory
	ld	d, -1 (ix)
	ld	e,#0x0a
	push	de
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
;src/main.c:102: cpct_drawSprite(G_BR, pvmem, BR_W, BR_H);       // Draw the sprite
	ld	bc, #_G_BR+0
	ld	de, #0x5a3e
	push	de
	push	hl
	push	bc
	call	_cpct_drawSprite
;src/main.c:106: changeVideoMemoryPage(125);
	ld	a, #0x7d
	push	af
	inc	sp
	call	_changeVideoMemoryPage
	inc	sp
;src/main.c:109: br_y += vy;                            // Add current velocity to Y coordinate
	ld	a, -1 (ix)
	add	a, -2 (ix)
;src/main.c:110: if ( br_y < 1 || br_y + BR_H > 199 )   // Check if it exceeds boundaries
	ld	-1 (ix), a
	sub	a, #0x01
	jr	C,00101$
	ld	c, -1 (ix)
	ld	b, #0x00
	ld	hl, #0x005a
	add	hl, bc
	ld	a, #0xc7
	cp	a, l
	ld	a, #0x00
	sbc	a, h
	jp	PO, 00117$
	xor	a, #0x80
00117$:
	jp	P, 00102$
00101$:
;src/main.c:111: vy = -vy;                           // When we exceed boundaries, we change velocity sense
	xor	a, a
	sub	a, -2 (ix)
	ld	-2 (ix), a
00102$:
;src/main.c:114: cpct_waitVSYNC();
	call	_cpct_waitVSYNC
	jr	00105$
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
