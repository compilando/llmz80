;--------------------------------------------------------
; File Created by SDCC : free open source ANSI-C Compiler
; Version 3.6.8 #9946 (Linux)
;--------------------------------------------------------
	.module manageVideoMem
	.optsdcc -mz80
	
;--------------------------------------------------------
; Public variables in this module
;--------------------------------------------------------
	.globl _cpct_getScreenPtr
	.globl _cpct_setVideoMemoryPage
	.globl _cpct_waitVSYNC
	.globl _gVMem
	.globl _InitializeVideoMemoryBuffers
	.globl _FlipBuffers
	.globl _GetScreenPtr
	.globl _GetBackBufferPtr
;--------------------------------------------------------
; special function registers
;--------------------------------------------------------
;--------------------------------------------------------
; ram data
;--------------------------------------------------------
	.area _DATA
_gVMem::
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
;src/manageVideoMem.c:31: void InitializeVideoMemoryBuffers() {
;	---------------------------------
; Function InitializeVideoMemoryBuffers
; ---------------------------------
_InitializeVideoMemoryBuffers::
;src/manageVideoMem.c:32: gVMem = VIDEO_MEM;   
	ld	hl,#_gVMem + 0
	ld	(hl), #0x00
	ret
;src/manageVideoMem.c:44: void FlipBuffers() {
;	---------------------------------
; Function FlipBuffers
; ---------------------------------
_FlipBuffers::
;src/manageVideoMem.c:45: cpct_waitVSYNC(); // Wait until VSYNC is up
	call	_cpct_waitVSYNC
;src/manageVideoMem.c:49: if (gVMem == BUFFER_MEM) {
	ld	a,(#_gVMem + 0)
	dec	a
	jr	NZ,00102$
;src/manageVideoMem.c:50: cpct_setVideoMemoryPage(cpct_pageC0);
	ld	l, #0x30
	call	_cpct_setVideoMemoryPage
;src/manageVideoMem.c:51: gVMem = VIDEO_MEM;
	ld	hl,#_gVMem + 0
	ld	(hl), #0x00
	ret
00102$:
;src/manageVideoMem.c:53: cpct_setVideoMemoryPage(cpct_page80);
	ld	l, #0x20
	call	_cpct_setVideoMemoryPage
;src/manageVideoMem.c:54: gVMem = BUFFER_MEM;
	ld	hl,#_gVMem + 0
	ld	(hl), #0x01
	ret
;src/manageVideoMem.c:62: u8* GetScreenPtr(u8 xPos, u8 yPos) {
;	---------------------------------
; Function GetScreenPtr
; ---------------------------------
_GetScreenPtr::
;src/manageVideoMem.c:67: if (gVMem == VIDEO_MEM) screenStart = (u8*)CPCT_VMEM_START;
	ld	a,(#_gVMem + 0)
	or	a, a
	jr	NZ,00102$
	ld	bc, #0xc000
	jr	00103$
00102$:
;src/manageVideoMem.c:68: else                    screenStart = (u8*)SCREEN_BUFF;
	ld	bc, #0x8000
00103$:
;src/manageVideoMem.c:71: return cpct_getScreenPtr(screenStart, xPos, yPos);
	ld	hl, #3+0
	add	hl, sp
	ld	a, (hl)
	push	af
	inc	sp
	ld	hl, #3+0
	add	hl, sp
	ld	a, (hl)
	push	af
	inc	sp
	push	bc
	call	_cpct_getScreenPtr
	ret
;src/manageVideoMem.c:78: u8* GetBackBufferPtr(u8 xPos, u8 yPos) {
;	---------------------------------
; Function GetBackBufferPtr
; ---------------------------------
_GetBackBufferPtr::
;src/manageVideoMem.c:83: if (gVMem == VIDEO_MEM) backBufferStart = (u8*)SCREEN_BUFF;
	ld	a,(#_gVMem + 0)
	or	a, a
	jr	NZ,00102$
	ld	bc, #0x8000
	jr	00103$
00102$:
;src/manageVideoMem.c:84: else                    backBufferStart = (u8*)CPCT_VMEM_START;
	ld	bc, #0xc000
00103$:
;src/manageVideoMem.c:87: return cpct_getScreenPtr(backBufferStart, xPos, yPos);
	ld	hl, #3+0
	add	hl, sp
	ld	a, (hl)
	push	af
	inc	sp
	ld	hl, #3+0
	add	hl, sp
	ld	a, (hl)
	push	af
	inc	sp
	push	bc
	call	_cpct_getScreenPtr
	ret
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
