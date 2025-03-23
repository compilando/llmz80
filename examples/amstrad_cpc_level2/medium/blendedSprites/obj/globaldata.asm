;--------------------------------------------------------
; File Created by SDCC : free open source ANSI-C Compiler
; Version 3.6.8 #9946 (Linux)
;--------------------------------------------------------
	.module globaldata
	.optsdcc -mz80
	
;--------------------------------------------------------
; Public variables in this module
;--------------------------------------------------------
	.globl _g_keys
	.globl _g_palette
	.globl _g_items
	.globl _g_blendModes
	.globl _g_selectedBlendMode
	.globl _g_selectedItem
;--------------------------------------------------------
; special function registers
;--------------------------------------------------------
;--------------------------------------------------------
; ram data
;--------------------------------------------------------
	.area _DATA
_g_selectedItem::
	.ds 1
_g_selectedBlendMode::
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
	.area _CODE
_g_blendModes:
	.db #0xae	; 174
	.ascii "XOR"
	.db 0x00
	.db #0xa6	; 166
	.ascii "AND"
	.db 0x00
	.db #0xb6	; 182
	.ascii "OR "
	.db 0x00
	.db #0x86	; 134
	.ascii "ADD"
	.db 0x00
	.db #0x96	; 150
	.ascii "SUB"
	.db 0x00
	.db #0x7e	; 126
	.ascii "LDI"
	.db 0x00
	.db #0x8e	; 142
	.ascii "ADC"
	.db 0x00
	.db #0x9e	; 158
	.ascii "SBC"
	.db 0x00
	.db #0x00	; 0
	.ascii "NOP"
	.db 0x00
_g_items:
	.dw _g_items_0
	.ascii " Skull"
	.db 0x00
	.dw _g_items_1
	.ascii " Paper"
	.db 0x00
	.dw _g_items_2
	.ascii "Potion"
	.db 0x00
	.dw _g_items_3
	.ascii "   Cat"
	.db 0x00
_g_palette:
	.db #0x14	; 20
	.db #0x04	; 4
	.db #0x1c	; 28
	.db #0x0c	; 12
	.db #0x16	; 22
	.db #0x1e	; 30
	.db #0x00	; 0
	.db #0x1f	; 31
	.db #0x1b	; 27
	.db #0x03	; 3
	.db #0x0b	; 11
_g_keys:
	.dw #0x8005
	.db #0x00	; 0
	.dw _drawCurrentSpriteAtRandom
	.dw #0x0408
	.db #0x00	; 0
	.dw _drawBackground
	.dw #0x0108
	.db #0x00	; 0
	.dw _selectNextItem
	.dw #0x0208
	.db #0x00	; 0
	.dw _selectNextBlendMode
	.area _INITIALIZER
	.area _CABS (ABS)
