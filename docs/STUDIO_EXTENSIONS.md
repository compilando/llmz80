# Extending LLMZ80 Studio

There is one extension point, and this document used to describe seven.

Studio discovers a third-party **target pack** — a machine, its video modes, its
hard budgets and the emulator adapters that can drive it — through a standard
Python entry point. An extension consumes a validated `GameProject`; it must not
mutate it in place or write outside the output directory passed to it.

## The entry-point group

| Group | Contract | Purpose |
|---|---|---|
| `llmz80.target_plugins` | `llmz80.studio.registry.TargetPack` | Machine modes, hard budgets and supported emulator adapters |

`registry.target_registry()` iterates that group and adds whatever it finds to
the built-in machines. Nothing in this repository registers one, so on a plain
checkout the loop finds nothing and the built-ins are the whole registry.

## What is no longer here

`llmz80.studio.plugins` declared seven `Protocol`s — capability modules, code
backends, semantic validators, emulator adapters, model providers, release
exporters — and three entry-point group names, of which only the one above was
ever read. Nothing in the repository implemented or checked any of the
protocols, and no package declared an entry point in the other two groups. A
contract nobody has implemented is not an extension seam; it is a description
of one, and it goes stale silently because nothing fails when it does.

Code backends, validators, model providers and emulator adapters are still
composed directly — `StudioService` takes a researcher, a designer, an artist
and a writer as parameters, which is how the tests replace them — and that is
a real seam because it is the one the program itself uses. A discovery
mechanism can be added back the day something needs discovering, and it will be
written against whatever the caller actually looks like then.

A genre is not an extension either, because it is no longer anything: a design
declares its own tiles, entities and mechanics, and what used to be added as a
genre pack is now written into the project's `brief`.

## Minimal target plugin

The repository includes an installable example in `examples/studio_plugin`:

```bash
.venv/bin/python -m pip install --no-build-isolation -e examples/studio_plugin
```

Its `pyproject.toml` registers a module-level `PACK` object:

```toml
[project.entry-points."llmz80.target_plugins"]
dodge_arena = "retro_bonus_pack:PACK"
```

IDs are lowercase stable API names. Duplicate IDs fail at registry construction
instead of silently shadowing an installed pack.

## Compatibility rules

1. Declare the minimum compatible LLMZ80 version in the extension package.
2. Treat `GameProject.schema_version` as an API version and reject versions not understood.
3. Return diagnostics; do not lower memory, warning, semantic or runtime quality gates.
4. Generated files belong under the supplied build directory. User-authored originals stay under
   the project directory.
5. Tests for a backend must compile at least one project with the real toolchain and run its supported
   headless emulator adapter.
