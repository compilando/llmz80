;--------------------------------------------------------
; File Created by SDCC : free open source ANSI-C Compiler
; Version 3.6.8 #9946 (Linux)
;--------------------------------------------------------
	.module video
	.optsdcc -mz80
	
;--------------------------------------------------------
; Public variables in this module
;--------------------------------------------------------
	.globl _video_initBuffers
	.globl _video_switchBuffers
	.globl _video_getBackBufferPtr
	.globl _cpct_setVideoMemoryPage
	.globl _cpct_memset
	.globl _video_buffer
;--------------------------------------------------------
; special function registers
;--------------------------------------------------------
;--------------------------------------------------------
; ram data
;--------------------------------------------------------
	.area _DATA
_video_buffer::
	.ds 2
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
;src/video.c:51: u8* video_getBackBufferPtr() {
;	---------------------------------
; Function video_getBackBufferPtr
; ---------------------------------
_video_getBackBufferPtr::
;src/video.c:52: return video_buffer;
	ld	hl, (_video_buffer)
	ret
;src/video.c:61: void video_switchBuffers() {
;	---------------------------------
; Function video_switchBuffers
; ---------------------------------
_video_switchBuffers::
;src/video.c:66: if (video_buffer == HW_BACKBUFFER) {
	ld	iy, #_video_buffer
	ld	a, 0 (iy)
	or	a, a
	jr	NZ,00102$
	ld	a, 1 (iy)
	sub	a, #0x80
	jr	NZ,00102$
;src/video.c:69: cpct_setVideoMemoryPage(cpct_page80);
	ld	l, #0x20
	call	_cpct_setVideoMemoryPage
;src/video.c:70: video_buffer = CPCT_VMEM_START;
	ld	hl, #0xc000
	ld	(_video_buffer), hl
	ret
00102$:
;src/video.c:74: cpct_setVideoMemoryPage(cpct_pageC0);
	ld	l, #0x30
	call	_cpct_setVideoMemoryPage
;src/video.c:75: video_buffer = HW_BACKBUFFER;
	ld	hl, #0x8000
	ld	(_video_buffer), hl
	ret
;src/video.c:83: void video_initBuffers() {
;	---------------------------------
; Function video_initBuffers
; ---------------------------------
_video_initBuffers::
;src/video.c:86: cpct_memset(HW_BACKBUFFER, 0, 0x4000);  // 16K HW_BACKBUFFER set to 0
	ld	hl, #0x4000
	push	hl
	xor	a, a
	push	af
	inc	sp
	ld	h, #0x80
	push	hl
	call	_cpct_memset
;src/video.c:91: video_switchBuffers();
	call	_video_switchBuffers
	ret
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
