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
    #: Defined by the platform library rather than by the program. The linker
    #: map carries it either way, so the probe gate is unaffected -- what
    #: changes is who is told to write it. A game that keeps its own frame
    #: cost gets it wrong in ways a gate reading one number cannot see: one
    #: program latched the maximum from before it drew its first screen, and
    #: another stored the last cost rather than the worst. Neither could be
    #: repaired by telling the writer more clearly, because neither ever
    #: failed the gate.
    provided_by_library: bool = False


#: Three symbols are required, but not on the same grounds. `g_score` and
#: `g_state` are demands on the design: a number it can put on screen, and
#: which screen is showing. `g_worst_frame_cost` is a demand on the
#: instrumentation -- it says nothing about what kind of game this is, only
#: how badly the loop overran the display. That is why it can be required of
#: everything when `g_lives` cannot: a game may have no score to lose and no
#: level to reach, but there is no game whose loop takes no time. It was
#: optional until a game that cannot report how badly it missed its frame
#: turned out to be a game nothing can judge on pacing, and pacing is the one
#: performance claim the machine can make about any design at all.
#:
#: Lives, levels and remaining objectives are notions some designs have and
#: others do not; they are probed when present and skipped when not, so a
#: puzzle with no score to lose and no level to reach is not failed for
#: lacking them.
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
    StateSymbol(
        "g_remaining",
        1,
        False,
        "objectives still to clear here, when the game counts them",
    ),
    StateSymbol("g_hiscore", 2, False, "best score of this session"),
    StateSymbol(
        "g_worst_frame_cost",
        1,
        True,
        "worst number of display frames a single game iteration missed; the "
        "platform library defines it and keeps it, so your program must not",
        provided_by_library=True,
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


def _ctype(symbol: StateSymbol) -> str:
    return "unsigned int" if symbol.width == 2 else "unsigned char"


def _declaration(symbol: StateSymbol) -> str:
    return f"    {_ctype(symbol)} {symbol.name};  /* {symbol.meaning} */"


def required_declarations() -> str:
    """The required symbols as C definitions, one per line, ready to paste.

    Exists so a program that only needs to satisfy the gate -- a test fixture
    proving something else entirely, say -- can honour the contract without
    hand-copying the names and their types. Two such copies had already been
    written out by hand in different test modules; adding a fourth required
    symbol would have broken them with a linker diagnostic pointing at the
    toolchain rather than at the stale fixture.

    A symbol the platform library defines is left out: a program defining it
    too gets `duplicate definition` from the linker, which is exactly the
    diagnostic-pointing-at-the-toolchain this function exists to prevent. That
    is not hypothetical either -- moving `g_worst_frame_cost` into the library
    broke every fixture built from this list until the filter was added.
    """
    return "".join(
        f"{_ctype(SYMBOLS_BY_NAME[name])} {name};\n"
        for name in REQUIRED_SYMBOLS
        if not SYMBOLS_BY_NAME[name].provided_by_library
    )


def contract_prompt() -> str:
    """Instructions to hand a generator before it writes a line of code.

    Stated as a hard requirement with the reason attached: a generator told only
    "name this variable X" will rename it while refactoring, whereas one told
    that memory is read at that symbol tends to leave it alone.
    """
    required = "\n".join(
        _declaration(s) for s in STATE_CONTRACT if s.required and not s.provided_by_library
    )
    library = "\n".join(
        _declaration(s) for s in STATE_CONTRACT if s.provided_by_library
    )
    optional = "\n".join(_declaration(s) for s in STATE_CONTRACT if not s.required)
    return f"""OBSERVABLE STATE CONTRACT

The finished program is verified by reading these variables straight out of
emulated memory and comparing them against the design. Declare them at file
scope with external linkage and exactly these names and types:

{required}

Declare these too, and only these, when the game has the corresponding
concept. A design with no such notion must not declare the symbol at all:

{optional}

The platform library already defines these, and keeps them accurate itself.
Do not declare or assign them; just call the library:

{library}

Rules that make the contract work:
  * Do not mark them static, const or register: a static symbol is absent from
    the linker map and cannot be read.
  * Do not rename, pack or reuse them for other purposes.
  * Assign their starting values at run time, inside your initialisation code.
    Do not rely on an initialiser at declaration: the Amstrad CPC link does not
    initialise the data segment, so such a variable holds whatever was in memory.
  * Keep g_state accurate. It is how a test knows which screen is showing.
"""
