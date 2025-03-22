;--------------------------------------------------------
; File Created by SDCC : free open source ANSI-C Compiler
; Version 3.6.8 #9946 (Linux)
;--------------------------------------------------------
	.module frametiles
	.optsdcc -mz80
	
;--------------------------------------------------------
; Public variables in this module
;--------------------------------------------------------
	.globl _G_frameDownCenter2
	.globl _G_frameUpCenter2
	.globl _G_frameDownCenter
	.globl _G_frameUpCenter
	.globl _G_frameDown
	.globl _G_frameUp
	.globl _G_frameRight
	.globl _G_frameLeft
	.globl _G_frameDownLeftCorner
	.globl _G_frameDownRightCorner
	.globl _G_frameUpRightCorner
	.globl _G_frameUpLeftCorner
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
_G_frameUpLeftCorner:
	.db #0x09	; 9
	.db #0x42	; 66	'B'
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x42	; 66	'B'
	.db #0x09	; 9
	.db #0x09	; 9
	.db #0x06	; 6
	.db #0x06	; 6
	.db #0x84	; 132
	.db #0xc0	; 192
	.db #0xc0	; 192
	.db #0x81	; 129
	.db #0x0c	; 12
	.db #0x84	; 132
	.db #0x0c	; 12
	.db #0x06	; 6
	.db #0xc0	; 192
	.db #0x48	; 72	'H'
	.db #0xc0	; 192
	.db #0x03	; 3
	.db #0x84	; 132
	.db #0xc0	; 192
	.db #0x0c	; 12
	.db #0x03	; 3
	.db #0x84	; 132
	.db #0x84	; 132
	.db #0x00	; 0
	.db #0x06	; 6
	.db #0x84	; 132
	.db #0x84	; 132
	.db #0x00	; 0
_G_frameUpRightCorner:
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x81	; 129
	.db #0x06	; 6
	.db #0x09	; 9
	.db #0x06	; 6
	.db #0x06	; 6
	.db #0x81	; 129
	.db #0xc0	; 192
	.db #0xc0	; 192
	.db #0x48	; 72	'H'
	.db #0x09	; 9
	.db #0x0c	; 12
	.db #0x48	; 72	'H'
	.db #0x0c	; 12
	.db #0x42	; 66	'B'
	.db #0xc0	; 192
	.db #0x84	; 132
	.db #0xc0	; 192
	.db #0x09	; 9
	.db #0x0c	; 12
	.db #0xc0	; 192
	.db #0x48	; 72	'H'
	.db #0x03	; 3
	.db #0x00	; 0
	.db #0x48	; 72	'H'
	.db #0x48	; 72	'H'
	.db #0x03	; 3
	.db #0x00	; 0
	.db #0x48	; 72	'H'
	.db #0x48	; 72	'H'
	.db #0x09	; 9
_G_frameDownRightCorner:
	.db #0x3c	; 60
	.db #0x48	; 72	'H'
	.db #0x48	; 72	'H'
	.db #0x09	; 9
	.db #0x3c	; 60
	.db #0x48	; 72	'H'
	.db #0x48	; 72	'H'
	.db #0x03	; 3
	.db #0x0c	; 12
	.db #0xc0	; 192
	.db #0x48	; 72	'H'
	.db #0x03	; 3
	.db #0xc0	; 192
	.db #0x84	; 132
	.db #0xc0	; 192
	.db #0x09	; 9
	.db #0x0c	; 12
	.db #0x48	; 72	'H'
	.db #0x0c	; 12
	.db #0x42	; 66	'B'
	.db #0xc0	; 192
	.db #0xc0	; 192
	.db #0x48	; 72	'H'
	.db #0x09	; 9
	.db #0x09	; 9
	.db #0x06	; 6
	.db #0x06	; 6
	.db #0x81	; 129
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x81	; 129
	.db #0x06	; 6
_G_frameDownLeftCorner:
	.db #0x06	; 6
	.db #0x84	; 132
	.db #0x84	; 132
	.db #0x3c	; 60
	.db #0x03	; 3
	.db #0x84	; 132
	.db #0x84	; 132
	.db #0x3c	; 60
	.db #0x03	; 3
	.db #0x84	; 132
	.db #0xc0	; 192
	.db #0x0c	; 12
	.db #0x06	; 6
	.db #0xc0	; 192
	.db #0x48	; 72	'H'
	.db #0xc0	; 192
	.db #0x81	; 129
	.db #0x0c	; 12
	.db #0x84	; 132
	.db #0x0c	; 12
	.db #0x06	; 6
	.db #0x84	; 132
	.db #0xc0	; 192
	.db #0xc0	; 192
	.db #0x42	; 66	'B'
	.db #0x09	; 9
	.db #0x09	; 9
	.db #0x06	; 6
	.db #0x09	; 9
	.db #0x42	; 66	'B'
	.db #0x03	; 3
	.db #0x03	; 3
_G_frameLeft:
	.db #0x06	; 6
	.db #0x48	; 72	'H'
	.db #0x0c	; 12
	.db #0x00	; 0
	.db #0x03	; 3
	.db #0x84	; 132
	.db #0x84	; 132
	.db #0x00	; 0
	.db #0x03	; 3
	.db #0x84	; 132
	.db #0x84	; 132
	.db #0x00	; 0
	.db #0x03	; 3
	.db #0x48	; 72	'H'
	.db #0x48	; 72	'H'
	.db #0x00	; 0
	.db #0x03	; 3
	.db #0x48	; 72	'H'
	.db #0x48	; 72	'H'
	.db #0x00	; 0
	.db #0x03	; 3
	.db #0x84	; 132
	.db #0x84	; 132
	.db #0x00	; 0
	.db #0x03	; 3
	.db #0x84	; 132
	.db #0x84	; 132
	.db #0x00	; 0
	.db #0x06	; 6
	.db #0x48	; 72	'H'
	.db #0x0c	; 12
	.db #0x00	; 0
_G_frameRight:
	.db #0x00	; 0
	.db #0x0c	; 12
	.db #0x84	; 132
	.db #0x09	; 9
	.db #0x00	; 0
	.db #0x48	; 72	'H'
	.db #0x48	; 72	'H'
	.db #0x03	; 3
	.db #0x00	; 0
	.db #0x48	; 72	'H'
	.db #0x48	; 72	'H'
	.db #0x03	; 3
	.db #0x00	; 0
	.db #0x84	; 132
	.db #0x84	; 132
	.db #0x03	; 3
	.db #0x00	; 0
	.db #0x84	; 132
	.db #0x84	; 132
	.db #0x03	; 3
	.db #0x00	; 0
	.db #0x48	; 72	'H'
	.db #0x48	; 72	'H'
	.db #0x03	; 3
	.db #0x00	; 0
	.db #0x48	; 72	'H'
	.db #0x48	; 72	'H'
	.db #0x03	; 3
	.db #0x00	; 0
	.db #0x0c	; 12
	.db #0x84	; 132
	.db #0x09	; 9
_G_frameUp:
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x09	; 9
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x06	; 6
	.db #0x48	; 72	'H'
	.db #0x84	; 132
	.db #0x48	; 72	'H'
	.db #0x84	; 132
	.db #0x84	; 132
	.db #0x48	; 72	'H'
	.db #0x84	; 132
	.db #0x48	; 72	'H'
	.db #0x48	; 72	'H'
	.db #0x84	; 132
	.db #0x48	; 72	'H'
	.db #0x84	; 132
	.db #0x0c	; 12
	.db #0x48	; 72	'H'
	.db #0x84	; 132
	.db #0x0c	; 12
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
_G_frameDown:
	.db #0x3c	; 60
	.db #0x3c	; 60
	.db #0x3c	; 60
	.db #0x3c	; 60
	.db #0x3c	; 60
	.db #0x3c	; 60
	.db #0x3c	; 60
	.db #0x3c	; 60
	.db #0x0c	; 12
	.db #0x48	; 72	'H'
	.db #0x84	; 132
	.db #0x0c	; 12
	.db #0x48	; 72	'H'
	.db #0x84	; 132
	.db #0x48	; 72	'H'
	.db #0x84	; 132
	.db #0x84	; 132
	.db #0x48	; 72	'H'
	.db #0x84	; 132
	.db #0x48	; 72	'H'
	.db #0x48	; 72	'H'
	.db #0x84	; 132
	.db #0x48	; 72	'H'
	.db #0x84	; 132
	.db #0x09	; 9
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x06	; 6
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
_G_frameUpCenter:
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x42	; 66	'B'
	.db #0x81	; 129
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x09	; 9
	.db #0x03	; 3
	.db #0x0c	; 12
	.db #0x0c	; 12
	.db #0x03	; 3
	.db #0x06	; 6
	.db #0x48	; 72	'H'
	.db #0xc0	; 192
	.db #0x48	; 72	'H'
	.db #0x84	; 132
	.db #0xc0	; 192
	.db #0x84	; 132
	.db #0x84	; 132
	.db #0x0c	; 12
	.db #0x84	; 132
	.db #0x48	; 72	'H'
	.db #0x0c	; 12
	.db #0x48	; 72	'H'
	.db #0x48	; 72	'H'
	.db #0xc0	; 192
	.db #0x84	; 132
	.db #0x48	; 72	'H'
	.db #0xc0	; 192
	.db #0x84	; 132
	.db #0x0c	; 12
	.db #0x0c	; 12
	.db #0x48	; 72	'H'
	.db #0x84	; 132
	.db #0x0c	; 12
	.db #0x0c	; 12
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
_G_frameDownCenter:
	.db #0x3c	; 60
	.db #0x3c	; 60
	.db #0x3c	; 60
	.db #0x3c	; 60
	.db #0x3c	; 60
	.db #0x3c	; 60
	.db #0x3c	; 60
	.db #0x3c	; 60
	.db #0x3c	; 60
	.db #0x3c	; 60
	.db #0x3c	; 60
	.db #0x3c	; 60
	.db #0x0c	; 12
	.db #0x0c	; 12
	.db #0x48	; 72	'H'
	.db #0x84	; 132
	.db #0x0c	; 12
	.db #0x0c	; 12
	.db #0x48	; 72	'H'
	.db #0xc0	; 192
	.db #0x84	; 132
	.db #0x48	; 72	'H'
	.db #0xc0	; 192
	.db #0x84	; 132
	.db #0x84	; 132
	.db #0x0c	; 12
	.db #0x84	; 132
	.db #0x48	; 72	'H'
	.db #0x0c	; 12
	.db #0x48	; 72	'H'
	.db #0x48	; 72	'H'
	.db #0xc0	; 192
	.db #0x48	; 72	'H'
	.db #0x84	; 132
	.db #0xc0	; 192
	.db #0x84	; 132
	.db #0x09	; 9
	.db #0x03	; 3
	.db #0x0c	; 12
	.db #0x0c	; 12
	.db #0x03	; 3
	.db #0x06	; 6
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x42	; 66	'B'
	.db #0x81	; 129
	.db #0x03	; 3
	.db #0x03	; 3
_G_frameUpCenter2:
	.db #0x42	; 66	'B'
	.db #0x81	; 129
	.db #0x0c	; 12
	.db #0x0c	; 12
	.db #0x48	; 72	'H'
	.db #0x84	; 132
	.db #0x84	; 132
	.db #0x48	; 72	'H'
	.db #0x84	; 132
	.db #0x48	; 72	'H'
	.db #0x48	; 72	'H'
	.db #0x84	; 132
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
_G_frameDownCenter2:
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x48	; 72	'H'
	.db #0x84	; 132
	.db #0x84	; 132
	.db #0x48	; 72	'H'
	.db #0x84	; 132
	.db #0x48	; 72	'H'
	.db #0x48	; 72	'H'
	.db #0x84	; 132
	.db #0x0c	; 12
	.db #0x0c	; 12
	.db #0x42	; 66	'B'
	.db #0x81	; 129
	.area _INITIALIZER
	.area _CABS (ABS)
