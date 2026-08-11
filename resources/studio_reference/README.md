# Reference programs

A complete maze game for each target, kept as ordinary source. It is not an
engine and nothing generates from it: Studio no longer produces games by
configuring a runtime.

It earns its place twice over.

**It proves the gates work.** Every quality gate claims to measure a program's
behaviour rather than its pixels. A claim like that is worth nothing without a
program that satisfies it and, just as importantly, one that can be made to
fail. Sabotaging `g_score += SCORE_PER_COLLECTIBLE` here produces a build that
still compiles, boots, draws and answers the keyboard, and the acceptance gate
still rejects it with `g_score: expected 10, read 0`.

**It shows a generator what honouring the contract looks like.** Prose telling a
model to expose `g_score` at file scope is weaker than a working program that
does it, alongside the design the program satisfies.

## Layout

    spectrum/design.yml       the design the program satisfies
    spectrum/src/*.c *.h      the program
    amstrad_cpc/...           the same game for the other machine

`engine.c` is shared between both targets byte for byte; `platform.c` is where
the machines differ.

## Building it

    zcc +zx -vn -O3 -clib=sdcc_iy src/engine.c src/game_data.c src/main.c \
        src/platform.c -m -o output -create-app -subtype=default

The CPC build needs a CPCtelera project layout; `llmz80 project build` does that
part for you.

## What is not true of it

It is not retrievable context yet. The example catalog and its audit compile one
source file per entry, so a multi-file program cannot join them without changing
both. Until that changes, this is read by people and by tests, not by retrieval.
