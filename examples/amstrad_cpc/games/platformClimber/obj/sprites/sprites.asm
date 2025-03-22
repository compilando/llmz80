;--------------------------------------------------------
; File Created by SDCC : free open source ANSI-C Compiler
; Version 3.6.8 #9946 (Linux)
;--------------------------------------------------------
	.module sprites
	.optsdcc -mz80
	
;--------------------------------------------------------
; Public variables in this module
;--------------------------------------------------------
	.globl _G_EMRhitleft
	.globl _G_EMRhitright
	.globl _G_EMRjumpleft4
	.globl _G_EMRjumpleft3
	.globl _G_EMRjumpleft2
	.globl _G_EMRjumpleft1
	.globl _G_EMRjumpright4
	.globl _G_EMRjumpright3
	.globl _G_EMRjumpright2
	.globl _G_EMRjumpright1
	.globl _G_EMRleft3
	.globl _G_EMRleft2
	.globl _G_EMRleft
	.globl _G_EMRright3
	.globl _G_EMRright2
	.globl _G_EMRright
	.globl _G_palette
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
_G_palette:
	.db #0x0b	; 11
	.db #0x0f	; 15
	.db #0x03	; 3
	.db #0x18	; 24
	.db #0x0d	; 13
	.db #0x14	; 20
	.db #0x06	; 6
	.db #0x1a	; 26
	.db #0x00	; 0
	.db #0x02	; 2
	.db #0x01	; 1
	.db #0x12	; 18
	.db #0x08	; 8
	.db #0x05	; 5
	.db #0x10	; 16
	.db #0x09	; 9
_G_EMRright:
	.db #0x00	; 0
	.db #0x0c	; 12
	.db #0x08	; 8
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x1d	; 29
	.db #0x2a	; 42
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x1d	; 29
	.db #0x2a	; 42
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x3f	; 63
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x30	; 48	'0'
	.db #0xa8	; 168
	.db #0x00	; 0
	.db #0x10	; 16
	.db #0x30	; 48	'0'
	.db #0x7e	; 126
	.db #0x00	; 0
	.db #0x3a	; 58
	.db #0xbd	; 189
	.db #0x3f	; 63
	.db #0x3f	; 63
	.db #0x3f	; 63
	.db #0xfc	; 252
	.db #0x3f	; 63
	.db #0x3f	; 63
	.db #0x3f	; 63
	.db #0xff	; 255
	.db #0xaa	; 170
	.db #0x00	; 0
	.db #0x3f	; 63
	.db #0xc4	; 196
	.db #0x7d	; 125
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x6c	; 108	'l'
	.db #0x7d	; 125
	.db #0xaa	; 170
	.db #0x14	; 20
	.db #0x9c	; 156
	.db #0xff	; 255
	.db #0xaa	; 170
	.db #0x6c	; 108	'l'
	.db #0x28	; 40
	.db #0x44	; 68	'D'
	.db #0xaa	; 170
	.db #0x9c	; 156
	.db #0x00	; 0
	.db #0x14	; 20
	.db #0xaa	; 170
	.db #0xfc	; 252
	.db #0x00	; 0
	.db #0x54	; 84	'T'
	.db #0xa8	; 168
	.db #0xfc	; 252
	.db #0xa8	; 168
	.db #0x54	; 84	'T'
	.db #0xfc	; 252
_G_EMRright2:
	.db #0x0c	; 12
	.db #0x08	; 8
	.db #0x1d	; 29
	.db #0x2a	; 42
	.db #0x1d	; 29
	.db #0x2a	; 42
	.db #0x3f	; 63
	.db #0x00	; 0
	.db #0x30	; 48	'0'
	.db #0xa8	; 168
	.db #0x30	; 48	'0'
	.db #0xfc	; 252
	.db #0x30	; 48	'0'
	.db #0xfc	; 252
	.db #0x3f	; 63
	.db #0xa8	; 168
	.db #0x3f	; 63
	.db #0xaa	; 170
	.db #0x3f	; 63
	.db #0x28	; 40
	.db #0x3f	; 63
	.db #0x28	; 40
	.db #0x9c	; 156
	.db #0x28	; 40
	.db #0x9c	; 156
	.db #0x00	; 0
	.db #0x9c	; 156
	.db #0x00	; 0
	.db #0xfc	; 252
	.db #0x00	; 0
	.db #0xfc	; 252
	.db #0xa8	; 168
_G_EMRright3:
	.db #0x00	; 0
	.db #0x0c	; 12
	.db #0x08	; 8
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x1d	; 29
	.db #0x2a	; 42
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x1d	; 29
	.db #0x2a	; 42
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x3f	; 63
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x30	; 48	'0'
	.db #0xa8	; 168
	.db #0x00	; 0
	.db #0x10	; 16
	.db #0x30	; 48	'0'
	.db #0xfc	; 252
	.db #0x00	; 0
	.db #0x3f	; 63
	.db #0x74	; 116	't'
	.db #0xfc	; 252
	.db #0x3f	; 63
	.db #0x3f	; 63
	.db #0xfc	; 252
	.db #0xbd	; 189
	.db #0x3f	; 63
	.db #0x3f	; 63
	.db #0xff	; 255
	.db #0xaa	; 170
	.db #0x00	; 0
	.db #0x3f	; 63
	.db #0x6c	; 108	'l'
	.db #0x3c	; 60
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x3c	; 60
	.db #0x9c	; 156
	.db #0x28	; 40
	.db #0x55	; 85	'U'
	.db #0xbe	; 190
	.db #0x6c	; 108	'l'
	.db #0x28	; 40
	.db #0xdd	; 221
	.db #0xaa	; 170
	.db #0x14	; 20
	.db #0x88	; 136
	.db #0x7d	; 125
	.db #0x00	; 0
	.db #0x14	; 20
	.db #0x88	; 136
	.db #0xfc	; 252
	.db #0x00	; 0
	.db #0x54	; 84	'T'
	.db #0xa8	; 168
	.db #0xfc	; 252
	.db #0xa8	; 168
	.db #0x54	; 84	'T'
	.db #0xfc	; 252
_G_EMRleft:
	.db #0x00	; 0
	.db #0x04	; 4
	.db #0x0c	; 12
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x15	; 21
	.db #0x2e	; 46
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x15	; 21
	.db #0x2e	; 46
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x3f	; 63
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x54	; 84	'T'
	.db #0x30	; 48	'0'
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xbd	; 189
	.db #0x30	; 48	'0'
	.db #0x20	; 32
	.db #0x3f	; 63
	.db #0x3f	; 63
	.db #0x7e	; 126
	.db #0x35	; 53	'5'
	.db #0x3f	; 63
	.db #0x3f	; 63
	.db #0xfc	; 252
	.db #0x3f	; 63
	.db #0x00	; 0
	.db #0x55	; 85	'U'
	.db #0xff	; 255
	.db #0x3f	; 63
	.db #0x00	; 0
	.db #0xbe	; 190
	.db #0x9c	; 156
	.db #0x3f	; 63
	.db #0x55	; 85	'U'
	.db #0xbe	; 190
	.db #0x9c	; 156
	.db #0x00	; 0
	.db #0x55	; 85	'U'
	.db #0xff	; 255
	.db #0x6c	; 108	'l'
	.db #0x28	; 40
	.db #0x55	; 85	'U'
	.db #0x88	; 136
	.db #0x14	; 20
	.db #0x9c	; 156
	.db #0x55	; 85	'U'
	.db #0x28	; 40
	.db #0x00	; 0
	.db #0x6c	; 108	'l'
	.db #0x54	; 84	'T'
	.db #0xa8	; 168
	.db #0x00	; 0
	.db #0xfc	; 252
	.db #0xfc	; 252
	.db #0xa8	; 168
	.db #0x54	; 84	'T'
	.db #0xfc	; 252
_G_EMRleft2:
	.db #0x04	; 4
	.db #0x0c	; 12
	.db #0x15	; 21
	.db #0x2e	; 46
	.db #0x15	; 21
	.db #0x2e	; 46
	.db #0x00	; 0
	.db #0x3f	; 63
	.db #0x54	; 84	'T'
	.db #0x30	; 48	'0'
	.db #0xfc	; 252
	.db #0x30	; 48	'0'
	.db #0xfc	; 252
	.db #0x30	; 48	'0'
	.db #0x54	; 84	'T'
	.db #0x3f	; 63
	.db #0x55	; 85	'U'
	.db #0x3f	; 63
	.db #0x14	; 20
	.db #0x3f	; 63
	.db #0x14	; 20
	.db #0x3f	; 63
	.db #0x14	; 20
	.db #0x6c	; 108	'l'
	.db #0x00	; 0
	.db #0x6c	; 108	'l'
	.db #0x00	; 0
	.db #0x6c	; 108	'l'
	.db #0x00	; 0
	.db #0xfc	; 252
	.db #0x54	; 84	'T'
	.db #0xfc	; 252
_G_EMRleft3:
	.db #0x00	; 0
	.db #0x04	; 4
	.db #0x0c	; 12
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x15	; 21
	.db #0x2e	; 46
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x15	; 21
	.db #0x2e	; 46
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x3f	; 63
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x54	; 84	'T'
	.db #0x30	; 48	'0'
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xfc	; 252
	.db #0x30	; 48	'0'
	.db #0x20	; 32
	.db #0x3f	; 63
	.db #0xfc	; 252
	.db #0xb8	; 184
	.db #0x3f	; 63
	.db #0x3f	; 63
	.db #0x7e	; 126
	.db #0xfc	; 252
	.db #0x3f	; 63
	.db #0x00	; 0
	.db #0x55	; 85	'U'
	.db #0xff	; 255
	.db #0x3f	; 63
	.db #0x00	; 0
	.db #0x3c	; 60
	.db #0x9c	; 156
	.db #0x3f	; 63
	.db #0x14	; 20
	.db #0x6c	; 108	'l'
	.db #0x3c	; 60
	.db #0x00	; 0
	.db #0x14	; 20
	.db #0x9c	; 156
	.db #0x7d	; 125
	.db #0xaa	; 170
	.db #0x44	; 68	'D'
	.db #0x28	; 40
	.db #0x55	; 85	'U'
	.db #0xee	; 238
	.db #0x44	; 68	'D'
	.db #0x28	; 40
	.db #0x00	; 0
	.db #0xbe	; 190
	.db #0x54	; 84	'T'
	.db #0xa8	; 168
	.db #0x00	; 0
	.db #0xfc	; 252
	.db #0xfc	; 252
	.db #0xa8	; 168
	.db #0x54	; 84	'T'
	.db #0xfc	; 252
_G_EMRjumpright1:
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x2e	; 46
	.db #0x0c	; 12
	.db #0x00	; 0
	.db #0x15	; 21
	.db #0x3f	; 63
	.db #0x2e	; 46
	.db #0x00	; 0
	.db #0x30	; 48	'0'
	.db #0xbd	; 189
	.db #0x2e	; 46
	.db #0x00	; 0
	.db #0x30	; 48	'0'
	.db #0x7e	; 126
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xbd	; 189
	.db #0x3f	; 63
	.db #0x3f	; 63
	.db #0xfc	; 252
	.db #0xcc	; 204
	.db #0x3f	; 63
	.db #0x3f	; 63
	.db #0xfc	; 252
	.db #0x3c	; 60
	.db #0x3c	; 60
	.db #0x7d	; 125
	.db #0xa8	; 168
	.db #0x55	; 85	'U'
	.db #0xff	; 255
	.db #0xaa	; 170
_G_EMRjumpright2:
	.db #0xfc	; 252
	.db #0xa8	; 168
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x54	; 84	'T'
	.db #0xa8	; 168
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x14	; 20
	.db #0xdc	; 220
	.db #0x30	; 48	'0'
	.db #0x00	; 0
	.db #0xbe	; 190
	.db #0x9d	; 157
	.db #0x30	; 48	'0'
	.db #0x2a	; 42
	.db #0xbe	; 190
	.db #0x3f	; 63
	.db #0x7e	; 126
	.db #0x3f	; 63
	.db #0xbe	; 190
	.db #0x3f	; 63
	.db #0xbd	; 189
	.db #0x2e	; 46
	.db #0xbe	; 190
	.db #0x3f	; 63
	.db #0x15	; 21
	.db #0x2e	; 46
	.db #0x55	; 85	'U'
	.db #0x3f	; 63
	.db #0x04	; 4
	.db #0x0c	; 12
_G_EMRjumpright3:
	.db #0x55	; 85	'U'
	.db #0xff	; 255
	.db #0xaa	; 170
	.db #0x54	; 84	'T'
	.db #0xbe	; 190
	.db #0x3c	; 60
	.db #0x3c	; 60
	.db #0xfc	; 252
	.db #0x3f	; 63
	.db #0x3f	; 63
	.db #0xcc	; 204
	.db #0xfc	; 252
	.db #0x3f	; 63
	.db #0x3f	; 63
	.db #0x7e	; 126
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xbd	; 189
	.db #0x30	; 48	'0'
	.db #0x00	; 0
	.db #0x1d	; 29
	.db #0x7e	; 126
	.db #0x30	; 48	'0'
	.db #0x00	; 0
	.db #0x1d	; 29
	.db #0x3f	; 63
	.db #0x2a	; 42
	.db #0x00	; 0
	.db #0x0c	; 12
	.db #0x1d	; 29
	.db #0x00	; 0
	.db #0x00	; 0
_G_EMRjumpright4:
	.db #0x0c	; 12
	.db #0x08	; 8
	.db #0x3f	; 63
	.db #0xaa	; 170
	.db #0x1d	; 29
	.db #0x2a	; 42
	.db #0x3f	; 63
	.db #0x7d	; 125
	.db #0x1d	; 29
	.db #0x7e	; 126
	.db #0x3f	; 63
	.db #0x7d	; 125
	.db #0x3f	; 63
	.db #0xbd	; 189
	.db #0x3f	; 63
	.db #0x7d	; 125
	.db #0x15	; 21
	.db #0x30	; 48	'0'
	.db #0x6e	; 110	'n'
	.db #0x7d	; 125
	.db #0x00	; 0
	.db #0x30	; 48	'0'
	.db #0xec	; 236
	.db #0x7d	; 125
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x54	; 84	'T'
	.db #0xa8	; 168
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x54	; 84	'T'
	.db #0xfc	; 252
_G_EMRjumpleft1:
	.db #0x0c	; 12
	.db #0x1d	; 29
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x1d	; 29
	.db #0x3f	; 63
	.db #0x2a	; 42
	.db #0x00	; 0
	.db #0x1d	; 29
	.db #0x7e	; 126
	.db #0x30	; 48	'0'
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xbd	; 189
	.db #0x30	; 48	'0'
	.db #0x00	; 0
	.db #0x3f	; 63
	.db #0x3f	; 63
	.db #0x7e	; 126
	.db #0x00	; 0
	.db #0x3f	; 63
	.db #0x3f	; 63
	.db #0xcc	; 204
	.db #0xfc	; 252
	.db #0xbe	; 190
	.db #0x3c	; 60
	.db #0x3c	; 60
	.db #0xfc	; 252
	.db #0x55	; 85	'U'
	.db #0xff	; 255
	.db #0xaa	; 170
	.db #0x54	; 84	'T'
_G_EMRjumpleft2:
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x54	; 84	'T'
	.db #0xfc	; 252
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x54	; 84	'T'
	.db #0xa8	; 168
	.db #0x00	; 0
	.db #0x30	; 48	'0'
	.db #0xec	; 236
	.db #0x28	; 40
	.db #0x15	; 21
	.db #0x30	; 48	'0'
	.db #0x6e	; 110	'n'
	.db #0x7d	; 125
	.db #0x3f	; 63
	.db #0xbd	; 189
	.db #0x3f	; 63
	.db #0x7d	; 125
	.db #0x1d	; 29
	.db #0x7e	; 126
	.db #0x3f	; 63
	.db #0x7d	; 125
	.db #0x1d	; 29
	.db #0x2a	; 42
	.db #0x3f	; 63
	.db #0x7d	; 125
	.db #0x0c	; 12
	.db #0x08	; 8
	.db #0x3f	; 63
	.db #0xaa	; 170
_G_EMRjumpleft3:
	.db #0xa8	; 168
	.db #0x55	; 85	'U'
	.db #0xff	; 255
	.db #0xaa	; 170
	.db #0xfc	; 252
	.db #0x3c	; 60
	.db #0x3c	; 60
	.db #0x7d	; 125
	.db #0xfc	; 252
	.db #0xcc	; 204
	.db #0x3f	; 63
	.db #0x3f	; 63
	.db #0x00	; 0
	.db #0xbd	; 189
	.db #0x3f	; 63
	.db #0x3f	; 63
	.db #0x00	; 0
	.db #0x30	; 48	'0'
	.db #0x7e	; 126
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x30	; 48	'0'
	.db #0xbd	; 189
	.db #0x2e	; 46
	.db #0x00	; 0
	.db #0x15	; 21
	.db #0x3f	; 63
	.db #0x2e	; 46
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x2e	; 46
	.db #0x0c	; 12
_G_EMRjumpleft4:
	.db #0x55	; 85	'U'
	.db #0x3f	; 63
	.db #0x04	; 4
	.db #0x0c	; 12
	.db #0xbe	; 190
	.db #0x3f	; 63
	.db #0x15	; 21
	.db #0x2e	; 46
	.db #0xbe	; 190
	.db #0x3f	; 63
	.db #0xbd	; 189
	.db #0x2e	; 46
	.db #0xbe	; 190
	.db #0x3f	; 63
	.db #0x7e	; 126
	.db #0x3f	; 63
	.db #0xbe	; 190
	.db #0x9d	; 157
	.db #0x30	; 48	'0'
	.db #0x2a	; 42
	.db #0xbe	; 190
	.db #0xdc	; 220
	.db #0x30	; 48	'0'
	.db #0x00	; 0
	.db #0x54	; 84	'T'
	.db #0xa8	; 168
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xfc	; 252
	.db #0xa8	; 168
	.db #0x00	; 0
	.db #0x00	; 0
_G_EMRhitright:
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x28	; 40
	.db #0x00	; 0
	.db #0x1d	; 29
	.db #0x2a	; 42
	.db #0x00	; 0
	.db #0x28	; 40
	.db #0x1d	; 29
	.db #0x3f	; 63
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x0c	; 12
	.db #0x1d	; 29
	.db #0x2a	; 42
	.db #0x28	; 40
	.db #0x00	; 0
	.db #0x30	; 48	'0'
	.db #0xa8	; 168
	.db #0x00	; 0
	.db #0x10	; 16
	.db #0x30	; 48	'0'
	.db #0xfc	; 252
	.db #0x14	; 20
	.db #0x3a	; 58
	.db #0xfc	; 252
	.db #0xfc	; 252
	.db #0x00	; 0
	.db #0x3f	; 63
	.db #0xfc	; 252
	.db #0xa8	; 168
	.db #0x14	; 20
	.db #0x3f	; 63
	.db #0xff	; 255
	.db #0xaa	; 170
	.db #0x00	; 0
	.db #0x3f	; 63
	.db #0x6c	; 108	'l'
	.db #0x7d	; 125
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x6c	; 108	'l'
	.db #0x7d	; 125
	.db #0xaa	; 170
	.db #0x14	; 20
	.db #0x9c	; 156
	.db #0xff	; 255
	.db #0xaa	; 170
	.db #0x6c	; 108	'l'
	.db #0x28	; 40
	.db #0x44	; 68	'D'
	.db #0xaa	; 170
	.db #0x9c	; 156
	.db #0x00	; 0
	.db #0x14	; 20
	.db #0xaa	; 170
	.db #0xfc	; 252
	.db #0x00	; 0
	.db #0x54	; 84	'T'
	.db #0xa8	; 168
	.db #0xfc	; 252
	.db #0xa8	; 168
	.db #0x54	; 84	'T'
	.db #0xfc	; 252
_G_EMRhitleft:
	.db #0x00	; 0
	.db #0x14	; 20
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x14	; 20
	.db #0x00	; 0
	.db #0x15	; 21
	.db #0x2e	; 46
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x3f	; 63
	.db #0x2e	; 46
	.db #0x14	; 20
	.db #0x15	; 21
	.db #0x2e	; 46
	.db #0x0c	; 12
	.db #0x00	; 0
	.db #0x54	; 84	'T'
	.db #0x30	; 48	'0'
	.db #0x00	; 0
	.db #0x28	; 40
	.db #0xfc	; 252
	.db #0x30	; 48	'0'
	.db #0x20	; 32
	.db #0x00	; 0
	.db #0xfc	; 252
	.db #0xfc	; 252
	.db #0x35	; 53	'5'
	.db #0x28	; 40
	.db #0x54	; 84	'T'
	.db #0xfc	; 252
	.db #0x3f	; 63
	.db #0x00	; 0
	.db #0x55	; 85	'U'
	.db #0xff	; 255
	.db #0x3f	; 63
	.db #0x00	; 0
	.db #0xbe	; 190
	.db #0x9c	; 156
	.db #0x3f	; 63
	.db #0x55	; 85	'U'
	.db #0xbe	; 190
	.db #0x9c	; 156
	.db #0x00	; 0
	.db #0x55	; 85	'U'
	.db #0xff	; 255
	.db #0x6c	; 108	'l'
	.db #0x28	; 40
	.db #0x55	; 85	'U'
	.db #0x88	; 136
	.db #0x14	; 20
	.db #0x9c	; 156
	.db #0x55	; 85	'U'
	.db #0x28	; 40
	.db #0x00	; 0
	.db #0x6c	; 108	'l'
	.db #0x54	; 84	'T'
	.db #0xa8	; 168
	.db #0x00	; 0
	.db #0xfc	; 252
	.db #0xfc	; 252
	.db #0xa8	; 168
	.db #0x54	; 84	'T'
	.db #0xfc	; 252
	.area _INITIALIZER
	.area _CABS (ABS)
