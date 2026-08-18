"""LLMZ80 -- AI-assisted C generation for classic Z80 microcomputers.

Studio (`llmz80.studio`) designs a game, draws its art, writes the program,
builds it with the target's native toolchain and then examines the running
binary in an emulator before it will call the result finished. Two machines
are supported: the ZX Spectrum 48K through z88dk, and the Amstrad CPC
through CPCtelera.

The model is Anthropic's, named in config.yml and called through
`llmz80.studio.llm`.
"""

__version__ = "1.0.0"
__author__ = "Oscar González"
