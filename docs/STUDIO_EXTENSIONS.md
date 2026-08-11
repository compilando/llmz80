# Extending LLMZ80 Studio

Studio discovers external components through standard Python entry points. An extension consumes a
validated `GameProject`; it must not mutate it in place or write outside the output directory passed
to it.

## Entry-point groups

| Group | Contract | Purpose |
|---|---|---|
| `llmz80.genre_packs` | `GenrePack` | Guided defaults and required capabilities for a game family |
| `llmz80.target_plugins` | `TargetPack` | Machine modes, hard budgets and supported emulator adapters |
| `llmz80.capabilities` | `CapabilityModule` | Reusable mechanics and their validation |
| `llmz80.exporters` | `ReleaseExporter` | Reproducible release packages |

The public protocols are in `llmz80.studio.plugins`. Code backends, validators, model providers and
emulator adapters use the same project-first contracts even when they are composed directly rather
than discovered globally.

## Minimal genre pack

The repository includes an installable example in `examples/studio_plugin`:

```bash
.venv/bin/python -m pip install --no-build-isolation -e examples/studio_plugin
```

Its `pyproject.toml` registers a module-level `PACK` object:

```toml
[project.entry-points."llmz80.genre_packs"]
dodge_arena = "retro_bonus_pack:PACK"
```

IDs are lowercase stable API names. A plugin may add a new genre ID without modifying the Studio
enum or core schema. Duplicate IDs fail at registry construction instead of silently shadowing an
installed pack.

## Compatibility rules

1. Declare the minimum compatible LLMZ80 version in the extension package.
2. Treat `GameProject.schema_version` as an API version and reject versions not understood.
3. Return diagnostics; do not lower memory, warning, semantic or runtime quality gates.
4. Generated files belong under the supplied build directory. User-authored originals stay under
   the project directory.
5. Tests for a backend must compile at least one project with the real toolchain and run its supported
   headless emulator adapter.
