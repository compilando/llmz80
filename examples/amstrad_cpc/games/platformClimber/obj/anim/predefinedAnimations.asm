;--------------------------------------------------------
; File Created by SDCC : free open source ANSI-C Compiler
; Version 3.6.8 #9946 (Linux)
;--------------------------------------------------------
	.module predefinedAnimations
	.optsdcc -mz80
	
;--------------------------------------------------------
; Public variables in this module
;--------------------------------------------------------
	.globl _g_anim
	.globl _g_hitRight
	.globl _g_hitLeft
	.globl _g_jumpRight
	.globl _g_jumpLeft
	.globl _g_walkRight
	.globl _g_walkLeft
	.globl _g_allAnimFrames
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
_g_allAnimFrames:
	.dw _G_EMRright
	.db #0x04	; 4
	.db #0x10	; 16
	.db #0x04	; 4
	.dw _G_EMRright2
	.db #0x02	; 2
	.db #0x10	; 16
	.db #0x04	; 4
	.dw _G_EMRleft
	.db #0x04	; 4
	.db #0x10	; 16
	.db #0x04	; 4
	.dw _G_EMRleft2
	.db #0x02	; 2
	.db #0x10	; 16
	.db #0x04	; 4
	.dw _G_EMRjumpright1
	.db #0x04	; 4
	.db #0x08	; 8
	.db #0x03	; 3
	.dw _G_EMRjumpright2
	.db #0x04	; 4
	.db #0x08	; 8
	.db #0x04	; 4
	.dw _G_EMRjumpright3
	.db #0x04	; 4
	.db #0x08	; 8
	.db #0x04	; 4
	.dw _G_EMRjumpright4
	.db #0x04	; 4
	.db #0x08	; 8
	.db #0x03	; 3
	.dw _G_EMRjumpleft1
	.db #0x04	; 4
	.db #0x08	; 8
	.db #0x03	; 3
	.dw _G_EMRjumpleft2
	.db #0x04	; 4
	.db #0x08	; 8
	.db #0x04	; 4
	.dw _G_EMRjumpleft3
	.db #0x04	; 4
	.db #0x08	; 8
	.db #0x04	; 4
	.dw _G_EMRjumpleft4
	.db #0x04	; 4
	.db #0x08	; 8
	.db #0x03	; 3
	.dw _G_EMRhitright
	.db #0x04	; 4
	.db #0x10	; 16
	.db #0x06	; 6
	.dw _G_EMRhitleft
	.db #0x04	; 4
	.db #0x10	; 16
	.db #0x06	; 6
	.dw _G_EMRright3
	.db #0x04	; 4
	.db #0x10	; 16
	.db #0x04	; 4
	.dw _G_EMRleft3
	.db #0x04	; 4
	.db #0x10	; 16
	.db #0x04	; 4
_g_walkLeft:
	.dw (_g_allAnimFrames + 10)
	.dw (_g_allAnimFrames + 15)
	.dw (_g_allAnimFrames + 75)
	.dw (_g_allAnimFrames + 15)
	.dw #0x0000
_g_walkRight:
	.dw (_g_allAnimFrames + 0)
	.dw (_g_allAnimFrames + 5)
	.dw (_g_allAnimFrames + 70)
	.dw (_g_allAnimFrames + 5)
	.dw #0x0000
_g_jumpLeft:
	.dw (_g_allAnimFrames + 40)
	.dw (_g_allAnimFrames + 45)
	.dw (_g_allAnimFrames + 50)
	.dw (_g_allAnimFrames + 55)
	.dw (_g_allAnimFrames + 15)
	.dw #0x0000
_g_jumpRight:
	.dw (_g_allAnimFrames + 20)
	.dw (_g_allAnimFrames + 25)
	.dw (_g_allAnimFrames + 30)
	.dw (_g_allAnimFrames + 35)
	.dw (_g_allAnimFrames + 5)
	.dw #0x0000
_g_hitLeft:
	.dw (_g_allAnimFrames + 65)
	.dw #0x0000
_g_hitRight:
	.dw (_g_allAnimFrames + 60)
	.dw #0x0000
_g_anim:
	.dw #0x0000
	.dw #0x0000
	.dw _g_walkLeft
	.dw _g_walkRight
	.dw _g_jumpLeft
	.dw _g_jumpRight
	.dw _g_hitLeft
	.dw _g_hitRight
	.area _INITIALIZER
	.area _CABS (ABS)
