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
	.globl _cpct_drawSprite
	.globl _cpct_memset
	.globl _gVMem
	.globl _gSpriteBackBuffer
	.globl _InitializeVideoMemoryBuffers
	.globl _FlipBuffers
	.globl _GetScreenPtr
	.globl _GetBackBufferPtr
	.globl _GetSpriteBackBufferPtr
	.globl _DrawSpriteBackBufferToScreen
;--------------------------------------------------------
; special function registers
;--------------------------------------------------------
;--------------------------------------------------------
; ram data
;--------------------------------------------------------
	.area _DATA
_gSpriteBackBuffer::
	.ds 3000
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
;src/manageVideoMem.c:32: void InitializeVideoMemoryBuffers() {
;	---------------------------------
; Function InitializeVideoMemoryBuffers
; ---------------------------------
_InitializeVideoMemoryBuffers::
;src/manageVideoMem.c:35: cpct_memset((u8*)SCREEN_BUFF, 0, 0x4000);   
	ld	hl, #0x4000
	push	hl
	xor	a, a
	push	af
	inc	sp
	ld	h, #0x80
	push	hl
	call	_cpct_memset
;src/manageVideoMem.c:37: gVMem = VIDEO_MEM;   
	ld	hl,#_gVMem + 0
	ld	(hl), #0x00
	ret
;src/manageVideoMem.c:49: void FlipBuffers() {
;	---------------------------------
; Function FlipBuffers
; ---------------------------------
_FlipBuffers::
;src/manageVideoMem.c:50: cpct_waitVSYNC(); // Wait until VSYNC is up
	call	_cpct_waitVSYNC
;src/manageVideoMem.c:54: if (gVMem == BUFFER_MEM) {
	ld	a,(#_gVMem + 0)
	dec	a
	jr	NZ,00102$
;src/manageVideoMem.c:55: cpct_setVideoMemoryPage(cpct_pageC0);
	ld	l, #0x30
	call	_cpct_setVideoMemoryPage
;src/manageVideoMem.c:56: gVMem = VIDEO_MEM;
	ld	hl,#_gVMem + 0
	ld	(hl), #0x00
	ret
00102$:
;src/manageVideoMem.c:58: cpct_setVideoMemoryPage(cpct_page80);
	ld	l, #0x20
	call	_cpct_setVideoMemoryPage
;src/manageVideoMem.c:59: gVMem = BUFFER_MEM;
	ld	hl,#_gVMem + 0
	ld	(hl), #0x01
	ret
;src/manageVideoMem.c:67: u8* GetScreenPtr(u8 xPos, u8 yPos) {
;	---------------------------------
; Function GetScreenPtr
; ---------------------------------
_GetScreenPtr::
;src/manageVideoMem.c:72: if (gVMem == VIDEO_MEM) screenStart = (u8*)CPCT_VMEM_START;
	ld	a,(#_gVMem + 0)
	or	a, a
	jr	NZ,00102$
	ld	bc, #0xc000
	jr	00103$
00102$:
;src/manageVideoMem.c:73: else                    screenStart = (u8*)SCREEN_BUFF;
	ld	bc, #0x8000
00103$:
;src/manageVideoMem.c:76: return cpct_getScreenPtr(screenStart, xPos, yPos);
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
;src/manageVideoMem.c:83: u8* GetBackBufferPtr(u8 xPos, u8 yPos) {
;	---------------------------------
; Function GetBackBufferPtr
; ---------------------------------
_GetBackBufferPtr::
;src/manageVideoMem.c:88: if (gVMem == VIDEO_MEM) backBufferStart = (u8*)SCREEN_BUFF;
	ld	a,(#_gVMem + 0)
	or	a, a
	jr	NZ,00102$
	ld	bc, #0x8000
	jr	00103$
00102$:
;src/manageVideoMem.c:89: else                    backBufferStart = (u8*)CPCT_VMEM_START;
	ld	bc, #0xc000
00103$:
;src/manageVideoMem.c:92: return cpct_getScreenPtr(backBufferStart, xPos, yPos);
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
;src/manageVideoMem.c:99: u8* GetSpriteBackBufferPtr(u8 xPos, u8 yPos) {
;	---------------------------------
; Function GetSpriteBackBufferPtr
; ---------------------------------
_GetSpriteBackBufferPtr::
	push	ix
	ld	ix,#0
	add	ix,sp
;src/manageVideoMem.c:100: return cpctm_spriteBufferPtr(gSpriteBackBuffer, VIEW_W_BYTES, xPos, yPos);
	ld	bc, #_gSpriteBackBuffer+0
	ld	e,5 (ix)
	ld	d,#0x00
	ld	l, e
	ld	h, d
	add	hl, hl
	add	hl, de
	add	hl, hl
	add	hl, hl
	add	hl, hl
	add	hl, de
	add	hl, hl
	add	hl,bc
	ld	c, l
	ld	b, h
	ld	l,4 (ix)
	ld	h,#0x00
	add	hl, bc
	pop	ix
	ret
;src/manageVideoMem.c:110: void DrawSpriteBackBufferToScreen() {
;	---------------------------------
; Function DrawSpriteBackBufferToScreen
; ---------------------------------
_DrawSpriteBackBufferToScreen::
;src/manageVideoMem.c:112: u8*   pVideoMemLocation = GetScreenPtr(VIEW_X, VIEW_Y);
	ld	hl, #0x000f
	push	hl
	call	_GetScreenPtr
;src/manageVideoMem.c:115: cpct_waitVSYNC();
	ex	(sp),hl
	call	_cpct_waitVSYNC
	pop	bc
;src/manageVideoMem.c:116: cpct_drawSprite(gSpriteBackBuffer, pVideoMemLocation, VIEW_W_BYTES, VIEW_H_BYTES);
	ld	hl, #0x3c32
	push	hl
	push	bc
	ld	hl, #_gSpriteBackBuffer
	push	hl
	call	_cpct_drawSprite
	ret
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
