;--------------------------------------------------------
; File Created by SDCC : free open source ANSI-C Compiler
; Version 3.6.8 #9946 (Linux)
;--------------------------------------------------------
	.module ryu
	.optsdcc -mz80
	
;--------------------------------------------------------
; Public variables in this module
;--------------------------------------------------------
	.globl _g_sprite_ryu
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
_g_sprite_ryu:
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xe4	; 228
	.db #0xa0	; 160
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
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xe4	; 228
	.db #0xcc	; 204
	.db #0xf0	; 240
	.db #0x88	; 136
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
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xe4	; 228
	.db #0xcc	; 204
	.db #0xd8	; 216
	.db #0xe4	; 228
	.db #0xcc	; 204
	.db #0x8a	; 138
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
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x50	; 80	'P'
	.db #0xcc	; 204
	.db #0xd8	; 216
	.db #0xe5	; 229
	.db #0xcc	; 204
	.db #0xd8	; 216
	.db #0xcd	; 205
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
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xe4	; 228
	.db #0xce	; 206
	.db #0xe5	; 229
	.db #0xcf	; 207
	.db #0xce	; 206
	.db #0xf0	; 240
	.db #0xe4	; 228
	.db #0x8a	; 138
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
	.db #0x00	; 0
	.db #0xe4	; 228
	.db #0xd8	; 216
	.db #0xd8	; 216
	.db #0xcc	; 204
	.db #0xe5	; 229
	.db #0xf0	; 240
	.db #0xb0	; 176
	.db #0xcc	; 204
	.db #0x8d	; 141
	.db #0x30	; 48	'0'
	.db #0x30	; 48	'0'
	.db #0x20	; 32
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xf0	; 240
	.db #0xd8	; 216
	.db #0xcc	; 204
	.db #0xe4	; 228
	.db #0xc8	; 200
	.db #0xf0	; 240
	.db #0xe4	; 228
	.db #0x64	; 100	'd'
	.db #0x30	; 48	'0'
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0x98	; 152
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xf0	; 240
	.db #0xcd	; 205
	.db #0xda	; 218
	.db #0xcd	; 205
	.db #0xcf	; 207
	.db #0xe5	; 229
	.db #0x98	; 152
	.db #0x4e	; 78	'N'
	.db #0x64	; 100	'd'
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0x20	; 32
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x50	; 80	'P'
	.db #0xf0	; 240
	.db #0xf0	; 240
	.db #0x60	; 96
	.db #0xcc	; 204
	.db #0xca	; 202
	.db #0x30	; 48	'0'
	.db #0x8d	; 141
	.db #0x64	; 100	'd'
	.db #0xcc	; 204
	.db #0xce	; 206
	.db #0xcc	; 204
	.db #0x25	; 37
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x50	; 80	'P'
	.db #0x52	; 82	'R'
	.db #0xce	; 206
	.db #0xc5	; 197
	.db #0xce	; 206
	.db #0xca	; 202
	.db #0x25	; 37
	.db #0x98	; 152
	.db #0x64	; 100	'd'
	.db #0xca	; 202
	.db #0xc5	; 197
	.db #0xcc	; 204
	.db #0x98	; 152
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xa0	; 160
	.db #0xcc	; 204
	.db #0xc5	; 197
	.db #0xce	; 206
	.db #0x9a	; 154
	.db #0x64	; 100	'd'
	.db #0x0f	; 15
	.db #0x64	; 100	'd'
	.db #0xcd	; 205
	.db #0xc5	; 197
	.db #0xcc	; 204
	.db #0x98	; 152
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
	.db #0x44	; 68	'D'
	.db #0xcd	; 205
	.db #0xcc	; 204
	.db #0x98	; 152
	.db #0x4e	; 78	'N'
	.db #0x25	; 37
	.db #0xcc	; 204
	.db #0xcd	; 205
	.db #0xcf	; 207
	.db #0xcc	; 204
	.db #0x98	; 152
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x44	; 68	'D'
	.db #0xce	; 206
	.db #0xc5	; 197
	.db #0xcc	; 204
	.db #0x30	; 48	'0'
	.db #0x8d	; 141
	.db #0x30	; 48	'0'
	.db #0xcc	; 204
	.db #0xcf	; 207
	.db #0xce	; 206
	.db #0xcc	; 204
	.db #0x98	; 152
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xcd	; 205
	.db #0x4e	; 78	'N'
	.db #0xd8	; 216
	.db #0xf0	; 240
	.db #0x25	; 37
	.db #0x98	; 152
	.db #0x30	; 48	'0'
	.db #0xcd	; 205
	.db #0xca	; 202
	.db #0xc5	; 197
	.db #0xcc	; 204
	.db #0x98	; 152
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xcf	; 207
	.db #0x64	; 100	'd'
	.db #0xcd	; 205
	.db #0xcc	; 204
	.db #0xf0	; 240
	.db #0x1a	; 26
	.db #0x64	; 100	'd'
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0xcf	; 207
	.db #0xcc	; 204
	.db #0x98	; 152
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xca	; 202
	.db #0x64	; 100	'd'
	.db #0xd0	; 208
	.db #0xcc	; 204
	.db #0xd8	; 216
	.db #0xf0	; 240
	.db #0xe5	; 229
	.db #0xcf	; 207
	.db #0xcf	; 207
	.db #0xcd	; 205
	.db #0xce	; 206
	.db #0x8d	; 141
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xcd	; 205
	.db #0x64	; 100	'd'
	.db #0xd0	; 208
	.db #0xcc	; 204
	.db #0xd8	; 216
	.db #0xcc	; 204
	.db #0xc8	; 200
	.db #0xc0	; 192
	.db #0xc5	; 197
	.db #0xcf	; 207
	.db #0xce	; 206
	.db #0x8d	; 141
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xcd	; 205
	.db #0x64	; 100	'd'
	.db #0xca	; 202
	.db #0xf0	; 240
	.db #0xe4	; 228
	.db #0xcc	; 204
	.db #0xca	; 202
	.db #0xc0	; 192
	.db #0xc0	; 192
	.db #0xcf	; 207
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xcc	; 204
	.db #0x64	; 100	'd'
	.db #0xcc	; 204
	.db #0xda	; 218
	.db #0xf0	; 240
	.db #0xcc	; 204
	.db #0xca	; 202
	.db #0xc0	; 192
	.db #0xc5	; 197
	.db #0xce	; 206
	.db #0xcc	; 204
	.db #0x4e	; 78	'N'
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xcc	; 204
	.db #0x64	; 100	'd'
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0xf0	; 240
	.db #0xf0	; 240
	.db #0xcd	; 205
	.db #0xcf	; 207
	.db #0xcf	; 207
	.db #0xce	; 206
	.db #0xcc	; 204
	.db #0x4e	; 78	'N'
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xcc	; 204
	.db #0x64	; 100	'd'
	.db #0xcc	; 204
	.db #0x98	; 152
	.db #0xcc	; 204
	.db #0xf0	; 240
	.db #0xcc	; 204
	.db #0xcd	; 205
	.db #0xcf	; 207
	.db #0xcc	; 204
	.db #0x8d	; 141
	.db #0xcc	; 204
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x44	; 68	'D'
	.db #0xce	; 206
	.db #0x64	; 100	'd'
	.db #0xcc	; 204
	.db #0x1a	; 26
	.db #0x8d	; 141
	.db #0x64	; 100	'd'
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0x8d	; 141
	.db #0xcc	; 204
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x44	; 68	'D'
	.db #0xc5	; 197
	.db #0x98	; 152
	.db #0xcc	; 204
	.db #0x30	; 48	'0'
	.db #0x98	; 152
	.db #0x30	; 48	'0'
	.db #0x64	; 100	'd'
	.db #0xcc	; 204
	.db #0xcd	; 205
	.db #0xce	; 206
	.db #0x4e	; 78	'N'
	.db #0x88	; 136
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x44	; 68	'D'
	.db #0xca	; 202
	.db #0xcc	; 204
	.db #0x64	; 100	'd'
	.db #0x30	; 48	'0'
	.db #0x98	; 152
	.db #0x30	; 48	'0'
	.db #0x30	; 48	'0'
	.db #0x4e	; 78	'N'
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0x4e	; 78	'N'
	.db #0x88	; 136
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x44	; 68	'D'
	.db #0xcf	; 207
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0x1a	; 26
	.db #0x98	; 152
	.db #0x30	; 48	'0'
	.db #0x30	; 48	'0'
	.db #0x30	; 48	'0'
	.db #0x30	; 48	'0'
	.db #0x25	; 37
	.db #0xcc	; 204
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x44	; 68	'D'
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0x8d	; 141
	.db #0x8d	; 141
	.db #0x30	; 48	'0'
	.db #0x30	; 48	'0'
	.db #0x30	; 48	'0'
	.db #0x30	; 48	'0'
	.db #0x4e	; 78	'N'
	.db #0xcc	; 204
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xca	; 202
	.db #0xce	; 206
	.db #0xe4	; 228
	.db #0xcc	; 204
	.db #0x8d	; 141
	.db #0xcc	; 204
	.db #0x1a	; 26
	.db #0x30	; 48	'0'
	.db #0x30	; 48	'0'
	.db #0x0f	; 15
	.db #0xcc	; 204
	.db #0x88	; 136
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x44	; 68	'D'
	.db #0xcf	; 207
	.db #0xcc	; 204
	.db #0xd8	; 216
	.db #0x03	; 3
	.db #0xe4	; 228
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0x0f	; 15
	.db #0x4e	; 78	'N'
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0x88	; 136
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xce	; 206
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0xc5	; 197
	.db #0xcc	; 204
	.db #0xf0	; 240
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xcf	; 207
	.db #0xcc	; 204
	.db #0xc8	; 200
	.db #0xcc	; 204
	.db #0xcd	; 205
	.db #0xcc	; 204
	.db #0xf0	; 240
	.db #0xcc	; 204
	.db #0x1a	; 26
	.db #0x25	; 37
	.db #0xcc	; 204
	.db #0xf0	; 240
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xcf	; 207
	.db #0xe4	; 228
	.db #0xc8	; 200
	.db #0xc5	; 197
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0xd8	; 216
	.db #0xf0	; 240
	.db #0xf0	; 240
	.db #0xf0	; 240
	.db #0xf0	; 240
	.db #0xe4	; 228
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xcc	; 204
	.db #0xf0	; 240
	.db #0xe5	; 229
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0x4e	; 78	'N'
	.db #0xf0	; 240
	.db #0xf0	; 240
	.db #0xf0	; 240
	.db #0x8d	; 141
	.db #0x64	; 100	'd'
	.db #0x88	; 136
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x44	; 68	'D'
	.db #0xd8	; 216
	.db #0xe0	; 224
	.db #0xcf	; 207
	.db #0xcc	; 204
	.db #0x4e	; 78	'N'
	.db #0x25	; 37
	.db #0xd8	; 216
	.db #0xf0	; 240
	.db #0x8d	; 141
	.db #0x30	; 48	'0'
	.db #0x8d	; 141
	.db #0xcc	; 204
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xcc	; 204
	.db #0xf0	; 240
	.db #0xce	; 206
	.db #0x98	; 152
	.db #0x25	; 37
	.db #0x98	; 152
	.db #0xd8	; 216
	.db #0xd8	; 216
	.db #0x98	; 152
	.db #0x4e	; 78	'N'
	.db #0x1a	; 26
	.db #0x64	; 100	'd'
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
	.db #0xcc	; 204
	.db #0x98	; 152
	.db #0x30	; 48	'0'
	.db #0x4e	; 78	'N'
	.db #0xd8	; 216
	.db #0x5a	; 90	'Z'
	.db #0xe4	; 228
	.db #0x8d	; 141
	.db #0x30	; 48	'0'
	.db #0x98	; 152
	.db #0x88	; 136
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
	.db #0x8d	; 141
	.db #0x30	; 48	'0'
	.db #0x25	; 37
	.db #0xf0	; 240
	.db #0xd8	; 216
	.db #0xe4	; 228
	.db #0x1a	; 26
	.db #0x30	; 48	'0'
	.db #0x98	; 152
	.db #0x88	; 136
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
	.db #0xcc	; 204
	.db #0x1a	; 26
	.db #0x30	; 48	'0'
	.db #0xf0	; 240
	.db #0xd8	; 216
	.db #0xb0	; 176
	.db #0x30	; 48	'0'
	.db #0x30	; 48	'0'
	.db #0xcc	; 204
	.db #0x20	; 32
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
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0x30	; 48	'0'
	.db #0xf0	; 240
	.db #0x70	; 112	'p'
	.db #0xb0	; 176
	.db #0x30	; 48	'0'
	.db #0x30	; 48	'0'
	.db #0xcc	; 204
	.db #0x20	; 32
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
	.db #0x44	; 68	'D'
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0x8d	; 141
	.db #0xf0	; 240
	.db #0x70	; 112	'p'
	.db #0xb0	; 176
	.db #0x30	; 48	'0'
	.db #0x30	; 48	'0'
	.db #0xcc	; 204
	.db #0x88	; 136
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
	.db #0x44	; 68	'D'
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0xf0	; 240
	.db #0x70	; 112	'p'
	.db #0xb0	; 176
	.db #0x30	; 48	'0'
	.db #0x64	; 100	'd'
	.db #0x98	; 152
	.db #0x88	; 136
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
	.db #0x44	; 68	'D'
	.db #0xcc	; 204
	.db #0x8d	; 141
	.db #0x4e	; 78	'N'
	.db #0xf0	; 240
	.db #0xd8	; 216
	.db #0xe4	; 228
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0x30	; 48	'0'
	.db #0x0a	; 10
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
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0x0f	; 15
	.db #0x30	; 48	'0'
	.db #0xf0	; 240
	.db #0xd8	; 216
	.db #0xe4	; 228
	.db #0xcc	; 204
	.db #0x98	; 152
	.db #0x30	; 48	'0'
	.db #0x64	; 100	'd'
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
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0x1a	; 26
	.db #0x30	; 48	'0'
	.db #0xf0	; 240
	.db #0xd8	; 216
	.db #0xe4	; 228
	.db #0xcc	; 204
	.db #0x30	; 48	'0'
	.db #0x30	; 48	'0'
	.db #0x25	; 37
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
	.db #0xcc	; 204
	.db #0x8d	; 141
	.db #0x1a	; 26
	.db #0x30	; 48	'0'
	.db #0xf0	; 240
	.db #0xd8	; 216
	.db #0xe4	; 228
	.db #0x8d	; 141
	.db #0x30	; 48	'0'
	.db #0x30	; 48	'0'
	.db #0x25	; 37
	.db #0x88	; 136
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xcc	; 204
	.db #0x8d	; 141
	.db #0x30	; 48	'0'
	.db #0x30	; 48	'0'
	.db #0xf0	; 240
	.db #0xd8	; 216
	.db #0xcc	; 204
	.db #0x0f	; 15
	.db #0x30	; 48	'0'
	.db #0x30	; 48	'0'
	.db #0x30	; 48	'0'
	.db #0x88	; 136
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x44	; 68	'D'
	.db #0x8d	; 141
	.db #0x8d	; 141
	.db #0x30	; 48	'0'
	.db #0x30	; 48	'0'
	.db #0x70	; 112	'p'
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0x0f	; 15
	.db #0x30	; 48	'0'
	.db #0x30	; 48	'0'
	.db #0x30	; 48	'0'
	.db #0x0a	; 10
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x44	; 68	'D'
	.db #0x8d	; 141
	.db #0x8d	; 141
	.db #0x30	; 48	'0'
	.db #0x30	; 48	'0'
	.db #0x25	; 37
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0x0f	; 15
	.db #0x1a	; 26
	.db #0x30	; 48	'0'
	.db #0x30	; 48	'0'
	.db #0x4e	; 78	'N'
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x44	; 68	'D'
	.db #0x8d	; 141
	.db #0x8d	; 141
	.db #0x30	; 48	'0'
	.db #0x30	; 48	'0'
	.db #0x25	; 37
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0x0f	; 15
	.db #0x1a	; 26
	.db #0x30	; 48	'0'
	.db #0x30	; 48	'0'
	.db #0x64	; 100	'd'
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x44	; 68	'D'
	.db #0x98	; 152
	.db #0x0f	; 15
	.db #0x30	; 48	'0'
	.db #0x30	; 48	'0'
	.db #0x64	; 100	'd'
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0x8d	; 141
	.db #0x0f	; 15
	.db #0x30	; 48	'0'
	.db #0x30	; 48	'0'
	.db #0x25	; 37
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xcc	; 204
	.db #0x98	; 152
	.db #0x0f	; 15
	.db #0x30	; 48	'0'
	.db #0x30	; 48	'0'
	.db #0x4e	; 78	'N'
	.db #0x88	; 136
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0x0f	; 15
	.db #0x30	; 48	'0'
	.db #0x30	; 48	'0'
	.db #0x25	; 37
	.db #0x88	; 136
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xcc	; 204
	.db #0x98	; 152
	.db #0x25	; 37
	.db #0x30	; 48	'0'
	.db #0x30	; 48	'0'
	.db #0x4e	; 78	'N'
	.db #0x88	; 136
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0x8d	; 141
	.db #0x1a	; 26
	.db #0x30	; 48	'0'
	.db #0x30	; 48	'0'
	.db #0x88	; 136
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xcc	; 204
	.db #0x98	; 152
	.db #0x30	; 48	'0'
	.db #0x30	; 48	'0'
	.db #0x25	; 37
	.db #0xcc	; 204
	.db #0x00	; 0
	.db #0x44	; 68	'D'
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0x1a	; 26
	.db #0x30	; 48	'0'
	.db #0x30	; 48	'0'
	.db #0x0a	; 10
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x44	; 68	'D'
	.db #0xcc	; 204
	.db #0x98	; 152
	.db #0x30	; 48	'0'
	.db #0x30	; 48	'0'
	.db #0x25	; 37
	.db #0xcc	; 204
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0x8d	; 141
	.db #0x30	; 48	'0'
	.db #0x30	; 48	'0'
	.db #0x0a	; 10
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x44	; 68	'D'
	.db #0xcc	; 204
	.db #0x98	; 152
	.db #0x30	; 48	'0'
	.db #0x30	; 48	'0'
	.db #0x4e	; 78	'N'
	.db #0x88	; 136
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x44	; 68	'D'
	.db #0xcc	; 204
	.db #0x8d	; 141
	.db #0x30	; 48	'0'
	.db #0x30	; 48	'0'
	.db #0x0a	; 10
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xcc	; 204
	.db #0x8d	; 141
	.db #0x98	; 152
	.db #0x30	; 48	'0'
	.db #0x25	; 37
	.db #0xcc	; 204
	.db #0x88	; 136
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x44	; 68	'D'
	.db #0xcc	; 204
	.db #0x1a	; 26
	.db #0x1a	; 26
	.db #0x1a	; 26
	.db #0x0a	; 10
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xcc	; 204
	.db #0x8d	; 141
	.db #0x98	; 152
	.db #0x30	; 48	'0'
	.db #0x64	; 100	'd'
	.db #0x4e	; 78	'N'
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xcc	; 204
	.db #0x8d	; 141
	.db #0x4e	; 78	'N'
	.db #0x1a	; 26
	.db #0x98	; 152
	.db #0x0a	; 10
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x44	; 68	'D'
	.db #0xcc	; 204
	.db #0x8d	; 141
	.db #0x1a	; 26
	.db #0x30	; 48	'0'
	.db #0x1a	; 26
	.db #0xcc	; 204
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xcc	; 204
	.db #0x4e	; 78	'N'
	.db #0xcc	; 204
	.db #0x64	; 100	'd'
	.db #0x98	; 152
	.db #0x0a	; 10
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x44	; 68	'D'
	.db #0xcc	; 204
	.db #0x8d	; 141
	.db #0x0f	; 15
	.db #0x25	; 37
	.db #0x64	; 100	'd'
	.db #0x88	; 136
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0x8d	; 141
	.db #0x4e	; 78	'N'
	.db #0x1a	; 26
	.db #0x88	; 136
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0x30	; 48	'0'
	.db #0x0f	; 15
	.db #0xcc	; 204
	.db #0x88	; 136
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x8d	; 141
	.db #0x4e	; 78	'N'
	.db #0x98	; 152
	.db #0xcc	; 204
	.db #0x25	; 37
	.db #0x88	; 136
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0x4e	; 78	'N'
	.db #0x8d	; 141
	.db #0x0f	; 15
	.db #0xcc	; 204
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x44	; 68	'D'
	.db #0x8d	; 141
	.db #0xcc	; 204
	.db #0x0f	; 15
	.db #0x8d	; 141
	.db #0x25	; 37
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x44	; 68	'D'
	.db #0xcc	; 204
	.db #0x8d	; 141
	.db #0x1a	; 26
	.db #0x0f	; 15
	.db #0x4e	; 78	'N'
	.db #0x88	; 136
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x44	; 68	'D'
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0x64	; 100	'd'
	.db #0x98	; 152
	.db #0x4e	; 78	'N'
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x44	; 68	'D'
	.db #0xcc	; 204
	.db #0x0f	; 15
	.db #0x30	; 48	'0'
	.db #0x30	; 48	'0'
	.db #0x4e	; 78	'N'
	.db #0x88	; 136
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0x8d	; 141
	.db #0xcc	; 204
	.db #0x1a	; 26
	.db #0x4e	; 78	'N'
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xcc	; 204
	.db #0x8d	; 141
	.db #0x1a	; 26
	.db #0x30	; 48	'0'
	.db #0x30	; 48	'0'
	.db #0xcc	; 204
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0x4e	; 78	'N'
	.db #0x8d	; 141
	.db #0x25	; 37
	.db #0x0a	; 10
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xcc	; 204
	.db #0x0f	; 15
	.db #0x30	; 48	'0'
	.db #0x30	; 48	'0'
	.db #0x64	; 100	'd'
	.db #0xcc	; 204
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x44	; 68	'D'
	.db #0xcc	; 204
	.db #0x0f	; 15
	.db #0x8d	; 141
	.db #0x1a	; 26
	.db #0x25	; 37
	.db #0x88	; 136
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x05	; 5
	.db #0x1a	; 26
	.db #0x30	; 48	'0'
	.db #0x30	; 48	'0'
	.db #0xcc	; 204
	.db #0x88	; 136
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x44	; 68	'D'
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0x0f	; 15
	.db #0x30	; 48	'0'
	.db #0x0f	; 15
	.db #0x88	; 136
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x44	; 68	'D'
	.db #0x1a	; 26
	.db #0x30	; 48	'0'
	.db #0x25	; 37
	.db #0xcc	; 204
	.db #0x88	; 136
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x44	; 68	'D'
	.db #0xcc	; 204
	.db #0x8d	; 141
	.db #0x1a	; 26
	.db #0x30	; 48	'0'
	.db #0x4e	; 78	'N'
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x1a	; 26
	.db #0x30	; 48	'0'
	.db #0x64	; 100	'd'
	.db #0xcc	; 204
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xcc	; 204
	.db #0x8d	; 141
	.db #0x0f	; 15
	.db #0x30	; 48	'0'
	.db #0x25	; 37
	.db #0x4e	; 78	'N'
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x44	; 68	'D'
	.db #0x1a	; 26
	.db #0x30	; 48	'0'
	.db #0xcc	; 204
	.db #0x88	; 136
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x44	; 68	'D'
	.db #0x0f	; 15
	.db #0x30	; 48	'0'
	.db #0x30	; 48	'0'
	.db #0x25	; 37
	.db #0x88	; 136
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xcc	; 204
	.db #0x98	; 152
	.db #0x25	; 37
	.db #0x4e	; 78	'N'
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x98	; 152
	.db #0x30	; 48	'0'
	.db #0x30	; 48	'0'
	.db #0x25	; 37
	.db #0x88	; 136
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0x25	; 37
	.db #0x88	; 136
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xcc	; 204
	.db #0x30	; 48	'0'
	.db #0x30	; 48	'0'
	.db #0x0f	; 15
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0x88	; 136
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x44	; 68	'D'
	.db #0xcc	; 204
	.db #0x8d	; 141
	.db #0x30	; 48	'0'
	.db #0x4e	; 78	'N'
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xcc	; 204
	.db #0xcf	; 207
	.db #0xcc	; 204
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x44	; 68	'D'
	.db #0xcf	; 207
	.db #0xcf	; 207
	.db #0xcc	; 204
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0xcd	; 205
	.db #0xcf	; 207
	.db #0xce	; 206
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0xcd	; 205
	.db #0xc5	; 197
	.db #0xc5	; 197
	.db #0xce	; 206
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x44	; 68	'D'
	.db #0xcd	; 205
	.db #0xc0	; 192
	.db #0xc5	; 197
	.db #0x89	; 137
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x46	; 70	'F'
	.db #0xcc	; 204
	.db #0xc0	; 192
	.db #0xc5	; 197
	.db #0x88	; 136
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x44	; 68	'D'
	.db #0xcf	; 207
	.db #0xc5	; 197
	.db #0xcf	; 207
	.db #0x89	; 137
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x46	; 70	'F'
	.db #0xcf	; 207
	.db #0xcf	; 207
	.db #0xcc	; 204
	.db #0x88	; 136
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x03	; 3
	.db #0x46	; 70	'F'
	.db #0xcf	; 207
	.db #0xcf	; 207
	.db #0xc0	; 192
	.db #0x89	; 137
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x46	; 70	'F'
	.db #0xc5	; 197
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0x89	; 137
	.db #0x02	; 2
	.db #0x00	; 0
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x46	; 70	'F'
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0xcd	; 205
	.db #0x89	; 137
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x46	; 70	'F'
	.db #0xca	; 202
	.db #0xc0	; 192
	.db #0xcd	; 205
	.db #0xcd	; 205
	.db #0x89	; 137
	.db #0x03	; 3
	.db #0x02	; 2
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x46	; 70	'F'
	.db #0xce	; 206
	.db #0xce	; 206
	.db #0xcf	; 207
	.db #0x89	; 137
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0xcc	; 204
	.db #0xcf	; 207
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0x89	; 137
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x46	; 70	'F'
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0xcc	; 204
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0xcc	; 204
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x02	; 2
	.db #0x00	; 0
	.db #0x01	; 1
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x02	; 2
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x00	; 0
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x03	; 3
	.db #0x00	; 0
	.db #0x00	; 0
	.area _INITIALIZER
	.area _CABS (ABS)
