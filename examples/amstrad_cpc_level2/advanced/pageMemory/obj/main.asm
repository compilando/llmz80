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
	.globl _cpct_getScreenPtr
	.globl _cpct_drawStringM1
	.globl _cpct_setDrawCharM1
	.globl _cpct_drawSolidBox
	.globl _cpct_px2byteM1
	.globl _cpct_pageMemory
	.globl _cpct_memset
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
;src/main.c:23: void main(void) {
;	---------------------------------
; Function main
; ---------------------------------
_main::
;src/main.c:28: cpct_pageMemory(RAMCFG_0 | BANK_0);				// Not needed, sets the memory with the first 64kb accesible, in consecutive banks.
	ld	l, #0x00
	call	_cpct_pageMemory
;src/main.c:31: *firstByteInPage = cpct_px2byteM1(1, 1, 1, 1);	// Set the first byte in page to all pixels with colour 1 (yellow by default).
	ld	hl, #0x0101
	push	hl
	ld	l, #0x01
	push	hl
	call	_cpct_px2byteM1
	pop	af
	pop	af
	ld	c, l
	ld	hl, #0x4000
	ld	(hl), c
;src/main.c:33: cpct_pageMemory(RAMCFG_4 | BANK_0);				// Set the 4th page (64kb to 80kb) in 0x4000-0x7FFF
	ld	l, #0x04
	call	_cpct_pageMemory
;src/main.c:38: *firstByteInPage = cpct_px2byteM1(2, 2, 2, 2);	// Set the first byte in page to all pixels with colour 2 (cyan by default ).
	ld	hl, #0x0202
	push	hl
	ld	l, #0x02
	push	hl
	call	_cpct_px2byteM1
	pop	af
	pop	af
	ld	c, l
	ld	hl, #0x4000
	ld	(hl), c
;src/main.c:40: cpct_pageMemory(RAMCFG_5 | BANK_0);				// Set the 4th page (64kb to 80kb) in 0x4000-0x7FFF
	ld	l, #0x05
	call	_cpct_pageMemory
;src/main.c:45: *firstByteInPage = cpct_px2byteM1(3, 3, 3, 3);	// Set the first byte in page to all pixels with colour 3 (red by default ).
	ld	hl, #0x0303
	push	hl
	ld	l, #0x03
	push	hl
	call	_cpct_px2byteM1
	pop	af
	pop	af
	ld	c, l
	ld	hl, #0x4000
	ld	(hl), c
;src/main.c:47: cpct_pageMemory(RAMCFG_6 | BANK_0);				// Set the 4th page (64kb to 80kb) in 0x4000-0x7FFF
	ld	l, #0x06
	call	_cpct_pageMemory
;src/main.c:52: *firstByteInPage = cpct_px2byteM1(1, 1, 2, 2);	// Set the first byte in page to all pixels with colours 1, 2 (yellow, cyan by default ).
	ld	hl, #0x0202
	push	hl
	ld	hl, #0x0101
	push	hl
	call	_cpct_px2byteM1
	pop	af
	pop	af
	ld	c, l
	ld	hl, #0x4000
	ld	(hl), c
;src/main.c:54: cpct_pageMemory(RAMCFG_7 | BANK_0);				// Set the 4th page (64kb to 80kb) in 0x4000-0x7FFF
	ld	l, #0x07
	call	_cpct_pageMemory
;src/main.c:59: *firstByteInPage = cpct_px2byteM1(1, 1, 3, 3);	// Set the first byte in page to all pixels with colours 1, 3 (yellow, cyan by default ).
	ld	hl, #0x0303
	push	hl
	ld	hl, #0x0101
	push	hl
	call	_cpct_px2byteM1
	pop	af
	pop	af
	ld	c, l
	ld	hl, #0x4000
	ld	(hl), c
;src/main.c:61: cpct_pageMemory(RAMCFG_0 | BANK_0); 				// Set the memory again to default state
	ld	l, #0x00
	call	_cpct_pageMemory
;src/main.c:64: cpct_memset(CPCT_VMEM_START, 0, 0x4000);
	ld	hl, #0x4000
	push	hl
	xor	a, a
	push	af
	inc	sp
	ld	h, #0xc0
	push	hl
	call	_cpct_memset
;src/main.c:67: cpct_pageMemory(RAMCFG_0 | BANK_0); // Not needed, sets the memory with the first 64kb accesible, in consecutive banks.
	ld	l, #0x00
	call	_cpct_pageMemory
;src/main.c:68: pvmem = cpct_getScreenPtr(CPCT_VMEM_START, 0, 0);
	ld	hl, #0x0000
	push	hl
	ld	h, #0xc0
	push	hl
	call	_cpct_getScreenPtr
	ld	c, l
	ld	b, h
;src/main.c:69: cpct_drawSolidBox(pvmem, *firstByteInPage, 2, 8);
	ld	hl, #0x4000
	ld	e, (hl)
	ld	d, #0x00
	ld	hl, #0x0802
	push	hl
	push	de
	push	bc
	call	_cpct_drawSolidBox
;src/main.c:70: pvmem = cpct_getScreenPtr(CPCT_VMEM_START, 4, 0);
	ld	hl, #0x0004
	push	hl
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
;src/main.c:71: cpct_setDrawCharM1(1, 0);
	push	hl
	ld	bc, #0x0001
	push	bc
	call	_cpct_setDrawCharM1
	pop	hl
;src/main.c:72: cpct_drawStringM1("RAMCFG_0", pvmem);
	ld	bc, #___str_0+0
	push	hl
	push	bc
	call	_cpct_drawStringM1
;src/main.c:74: cpct_pageMemory(RAMCFG_4 | BANK_0); // Set the 4th page (64kb to 80kb) in 0x4000-0x7FFF
	ld	l, #0x04
	call	_cpct_pageMemory
;src/main.c:75: pvmem = cpct_getScreenPtr(CPCT_VMEM_START, 0, 16);
	ld	hl, #0x1000
	push	hl
	ld	h, #0xc0
	push	hl
	call	_cpct_getScreenPtr
	ld	c, l
	ld	b, h
;src/main.c:76: cpct_drawSolidBox(pvmem, *firstByteInPage, 2, 8);
	ld	hl, #0x4000
	ld	e, (hl)
	ld	d, #0x00
	ld	hl, #0x0802
	push	hl
	push	de
	push	bc
	call	_cpct_drawSolidBox
;src/main.c:77: pvmem = cpct_getScreenPtr(CPCT_VMEM_START, 4, 16);
	ld	hl, #0x1004
	push	hl
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
;src/main.c:78: cpct_drawStringM1("RAMCFG_4", pvmem);
	ld	bc, #___str_1+0
	push	hl
	push	bc
	call	_cpct_drawStringM1
;src/main.c:80: cpct_pageMemory(RAMCFG_5 | BANK_0); // Set the 4th page (64kb to 80kb) in 0x4000-0x7FFF
	ld	l, #0x05
	call	_cpct_pageMemory
;src/main.c:81: pvmem = cpct_getScreenPtr(CPCT_VMEM_START, 0, 32);
	ld	hl, #0x2000
	push	hl
	ld	h, #0xc0
	push	hl
	call	_cpct_getScreenPtr
	ld	c, l
	ld	b, h
;src/main.c:82: cpct_drawSolidBox(pvmem, *firstByteInPage, 2, 8);
	ld	hl, #0x4000
	ld	e, (hl)
	ld	d, #0x00
	ld	hl, #0x0802
	push	hl
	push	de
	push	bc
	call	_cpct_drawSolidBox
;src/main.c:83: pvmem = cpct_getScreenPtr(CPCT_VMEM_START, 4, 32);
	ld	hl, #0x2004
	push	hl
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
;src/main.c:84: cpct_drawStringM1("RAMCFG_5", pvmem);
	ld	bc, #___str_2+0
	push	hl
	push	bc
	call	_cpct_drawStringM1
;src/main.c:86: cpct_pageMemory(RAMCFG_6 | BANK_0); // Set the 4th page (64kb to 80kb) in 0x4000-0x7FFF
	ld	l, #0x06
	call	_cpct_pageMemory
;src/main.c:87: pvmem = cpct_getScreenPtr(CPCT_VMEM_START, 0, 48);
	ld	hl, #0x3000
	push	hl
	ld	h, #0xc0
	push	hl
	call	_cpct_getScreenPtr
	ld	c, l
	ld	b, h
;src/main.c:88: cpct_drawSolidBox(pvmem, *firstByteInPage, 2, 8);
	ld	hl, #0x4000
	ld	e, (hl)
	ld	d, #0x00
	ld	hl, #0x0802
	push	hl
	push	de
	push	bc
	call	_cpct_drawSolidBox
;src/main.c:89: pvmem = cpct_getScreenPtr(CPCT_VMEM_START, 4, 48);
	ld	hl, #0x3004
	push	hl
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
;src/main.c:90: cpct_drawStringM1("RAMCFG_6", pvmem);
	ld	bc, #___str_3+0
	push	hl
	push	bc
	call	_cpct_drawStringM1
;src/main.c:92: cpct_pageMemory(RAMCFG_7 | BANK_0); // Set the 4th page (64kb to 80kb) in 0x4000-0x7FFF
	ld	l, #0x07
	call	_cpct_pageMemory
;src/main.c:93: pvmem = cpct_getScreenPtr(CPCT_VMEM_START, 0, 64);
	ld	hl, #0x4000
	push	hl
	ld	h, #0xc0
	push	hl
	call	_cpct_getScreenPtr
	ld	c, l
	ld	b, h
;src/main.c:94: cpct_drawSolidBox(pvmem, *firstByteInPage, 2, 8);
	ld	hl, #0x4000
	ld	e, (hl)
	ld	d, #0x00
	ld	hl, #0x0802
	push	hl
	push	de
	push	bc
	call	_cpct_drawSolidBox
;src/main.c:95: pvmem = cpct_getScreenPtr(CPCT_VMEM_START, 4, 64);
	ld	hl, #0x4004
	push	hl
	ld	hl, #0xc000
	push	hl
	call	_cpct_getScreenPtr
;src/main.c:96: cpct_drawStringM1("RAMCFG_7", pvmem);
	ld	bc, #___str_4+0
	push	hl
	push	bc
	call	_cpct_drawStringM1
;src/main.c:98: cpct_pageMemory(DEFAULT_MEM_CFG); // Equivalent to RAMCFG_0 | BANK_0 
	ld	l, #0x00
	call	_cpct_pageMemory
;src/main.c:101: while (1);
00102$:
	jr	00102$
___str_0:
	.ascii "RAMCFG_0"
	.db 0x00
___str_1:
	.ascii "RAMCFG_4"
	.db 0x00
___str_2:
	.ascii "RAMCFG_5"
	.db 0x00
___str_3:
	.ascii "RAMCFG_6"
	.db 0x00
___str_4:
	.ascii "RAMCFG_7"
	.db 0x00
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
