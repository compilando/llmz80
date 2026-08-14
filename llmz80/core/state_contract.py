"""The state a generated program must expose so its behaviour can be measured.

This contract belongs to the verification apparatus, not to any one engine. Any
program that honours it -- hand written, template generated or written by a
model -- can be probed in emulated memory and checked against its design, which
is what turns "it booted and drew something" into "it obeyed the rules".

Keep this module free of Studio imports: the legacy prompt-to-C generator needs
it just as much as the project-first flow does.
"""

from __future__ import annotations

from dataclasses import dataclass

#: Values of `g_state`, so a scenario can assert which screen is showing.
STATE_TITLE = 0
STATE_PLAYING = 1
STATE_GAME_OVER = 2
STATE_VICTORY = 3


@dataclass(frozen=True)
class StateSymbol:
    name: str
    width: int
    required: bool
    meaning: str


#: Only two symbols are required, because only two say something true of every
#: program: a number it can put on screen and which screen is showing. Lives,
#: levels and remaining objectives are notions some designs have and others do
#: not; they are probed when present and skipped when not, so a puzzle with no
#: score to lose and no level to reach is not failed for lacking them.
STATE_CONTRACT: tuple[StateSymbol, ...] = (
    StateSymbol("g_score", 2, True, "current score; zero when a game begins"),
    StateSymbol(
        "g_state",
        1,
        True,
        "0 title screen, 1 playing, 2 game over, 3 victory",
    ),
    StateSymbol(
        "g_lives",
        1,
        False,
        "attempts left, when the game has such a notion; the design's mechanics "
        "say how many it starts with",
    ),
    StateSymbol(
        "g_level",
        1,
        False,
        "current level or screen number, counting from one, when the game " "advances through them",
    ),
    StateSymbol("g_remaining", 1, False, "objectives still to clear on this level"),
    StateSymbol("g_hiscore", 2, False, "best score of this session"),
    StateSymbol(
        "g_worst_frame_cost",
        1,
        False,
        "worst number of display frames a single game iteration missed; zero is ideal",
    ),
    StateSymbol(
        "g_anim_frame",
        1,
        False,
        "the animation frame the player is currently drawn with; it must advance "
        "while the player moves and hold still while it does not",
    ),
)

SYMBOLS_BY_NAME = {symbol.name: symbol for symbol in STATE_CONTRACT}
REQUIRED_SYMBOLS = tuple(symbol.name for symbol in STATE_CONTRACT if symbol.required)
PROBE_WIDTHS = {symbol.name: symbol.width for symbol in STATE_CONTRACT}


def _declaration(symbol: StateSymbol) -> str:
    ctype = "unsigned int" if symbol.width == 2 else "unsigned char"
    return f"    {ctype} {symbol.name};  /* {symbol.meaning} */"


def contract_prompt() -> str:
    """Instructions to hand a generator before it writes a line of code.

    Stated as a hard requirement with the reason attached: a generator told only
    "name this variable X" will rename it while refactoring, whereas one told
    that memory is read at that symbol tends to leave it alone.
    """
    required = "\n".join(_declaration(s) for s in STATE_CONTRACT if s.required)
    optional = "\n".join(_declaration(s) for s in STATE_CONTRACT if not s.required)
    return f"""OBSERVABLE STATE CONTRACT

The finished program is verified by reading these variables straight out of
emulated memory and comparing them against the design. Declare them at file
scope with external linkage and exactly these names and types:

{required}

Declare these too, and only these, when the game has the corresponding
concept. A design with no such notion must not declare the symbol at all:

{optional}

Rules that make the contract work:
  * Do not mark them static, const or register: a static symbol is absent from
    the linker map and cannot be read.
  * Do not rename, pack or reuse them for other purposes.
  * Assign their starting values at run time, inside your initialisation code.
    Do not rely on an initialiser at declaration: the Amstrad CPC link does not
    initialise the data segment, so such a variable holds whatever was in memory.
  * Keep g_state accurate. It is how a test knows which screen is showing.
"""
