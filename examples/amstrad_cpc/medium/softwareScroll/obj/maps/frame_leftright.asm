;--------------------------------------------------------
; File Created by SDCC : free open source ANSI-C Compiler
; Version 3.6.8 #9946 (Linux)
;--------------------------------------------------------
	.module frame_leftright
	.optsdcc -mz80
	
;--------------------------------------------------------
; Public variables in this module
;--------------------------------------------------------
	.globl _g_frame_lr
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
	.area _CODE
_g_frame_lr:
	.db #0x09	; 9
	.db #0x15	; 21
	.db #0x14	; 20
	.db #0x09	; 9
	.db #0x09	; 9
	.db #0x15	; 21
	.db #0x14	; 20
	.db #0x09	; 9
	.db #0x09	; 9
	.db #0x15	; 21
	.db #0x14	; 20
	.db #0x09	; 9
	.db #0x09	; 9
	.db #0x15	; 21
	.db #0x14	; 20
	.db #0x09	; 9
	.db #0x09	; 9
	.db #0x15	; 21
	.db #0x14	; 20
	.db #0x09	; 9
	.db #0x09	; 9
	.db #0x15	; 21
	.db #0x14	; 20
	.db #0x09	; 9
	.db #0x09	; 9
	.db #0x15	; 21
	.db #0x14	; 20
	.db #0x09	; 9
	.db #0x09	; 9
	.db #0x15	; 21
	.db #0x14	; 20
	.db #0x09	; 9
	.db #0x09	; 9
	.db #0x15	; 21
	.db #0x14	; 20
	.db #0x09	; 9
	.db #0x09	; 9
	.db #0x15	; 21
	.db #0x14	; 20
	.db #0x09	; 9
	.db #0x09	; 9
	.db #0x15	; 21
	.db #0x14	; 20
	.db #0x09	; 9
	.db #0x09	; 9
	.db #0x15	; 21
	.db #0x14	; 20
	.db #0x09	; 9
	.db #0x09	; 9
	.db #0x15	; 21
	.db #0x14	; 20
	.db #0x09	; 9
	.db #0x09	; 9
	.db #0x15	; 21
	.db #0x14	; 20
	.db #0x09	; 9
	.db #0x09	; 9
	.db #0x15	; 21
	.db #0x14	; 20
	.db #0x09	; 9
	.db #0x09	; 9
	.db #0x15	; 21
	.db #0x14	; 20
	.db #0x09	; 9
	.area _INITIALIZER
	.area _CABS (ABS)
