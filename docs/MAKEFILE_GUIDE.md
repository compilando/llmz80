# LLMZ80 Makefile guide

The Makefile is a thin interface over the Python CLI. It covers common project
workflows without duplicating application logic.

## First run

```bash
make setup
# Add OPENAI_API_KEY to .env
make doctor
```

`setup` creates `.venv`, installs runtime dependencies there, creates `.env`
when needed, and creates the local runtime directories. It does not modify the
operating-system Python and does not start Docker or Qdrant.

The dependency set supports Python 3.10 through 3.13. The Makefile selects the
newest compatible `python3.x` command installed on the host instead of blindly
using a newer, unsupported system Python.

## Generate programs

```bash
# Direct prompts
make generate-spectrum PROMPT="Create a Pong game"
make generate-cpc PROMPT="Create a Mode 0 graphics demo"

# Omit PROMPT for the interactive prompt
make generate-spectrum

# Launch the configured emulator after a successful build
make run-spectrum PROMPT="Create a maze game"
make run-cpc PROMPT="Create a sprite animation"

# Override the configured emulator
make run-cpc EMULATOR=cpcec PROMPT="Create a sprite animation"
make run-spectrum EMULATOR=zesarux PROMPT="Create a maze game"
```

With the default `cap32` adapter, `run-cpc` mounts the canonical `output.dsk`
and queues `run"program.bin"` after firmware boot, so the generated application
starts automatically instead of stopping at the BASIC prompt. Other emulator
overrides keep their native launch behaviour.

On Arch Linux, the Spectrum options are the AUR packages
`fuse-emulator-sdl` and `zesarux`; the expected commands are `fuse` and
`zesarux`, respectively. Emulator preflight runs before code generation, so a
missing executable never consumes an API request.

The generic form is useful in scripts:

```bash
make generate PLATFORM=spectrum PROMPT="Create a scrolling message"
make generate PLATFORM=amstrad_cpc PROMPT="Create a platform game"
```

Optional CLI flags can be passed through `GENERATOR_ARGS`:

```bash
make generate-spectrum \
  PROMPT="Create a keyboard-controlled character" \
  GENERATOR_ARGS="--no-embeddings --max-attempts 6"
```

Generation does not require Qdrant. The deterministic local catalog remains
available when Qdrant is offline or `--no-embeddings` is used.

## Validate changes

```bash
make test             # Python tests
make coverage         # Tests plus HTML coverage report
make lint             # Flake8; failures are returned to the shell
make format           # Apply Black formatting
make audit-examples   # Compile every example the RAG catalog may retrieve
make check            # Tests plus the complete real-toolchain example audit
```

`make check` requires Z88DK and CPCtelera because it performs real Spectrum and
Amstrad builds. `make test` can be used when those toolchains are unavailable;
toolchain-dependent integration tests skip themselves.

## Optional Qdrant service

```bash
make qdrant-up
make qdrant-status
make qdrant-index
make qdrant-down
```

Qdrant needs Docker. Indexing also needs a valid OpenAI API key because it
creates embeddings. Stopping Qdrant preserves its data under
`local/qdrant_storage`. The image is pinned to a client-compatible release;
override `QDRANT_IMAGE` deliberately when upgrading both sides.

## Variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `VENV_DIR` | `.venv` | Project virtual-environment directory |
| `BOOTSTRAP_PYTHON` | newest installed Python 3.10–3.13 | Python used only to create `.venv` |
| `PYTHON` | `.venv/bin/python` | Project Python interpreter |
| `PLATFORM` | `spectrum` | Generic generation target platform |
| `PROMPT` | empty | Empty enables the interactive prompt |
| `LOG_LEVEL` | `INFO` | CLI logging level |
| `GENERATOR_ARGS` | empty | Additional `llm_z80.py` arguments |
| `EMULATOR` | configured value | Emulator override for `run*` targets |
| `QDRANT_URL` | `http://127.0.0.1:6333` | Optional Qdrant endpoint |
| `QDRANT_IMAGE` | `qdrant/qdrant:v1.18.3` | Reproducible optional Qdrant image |

Run `make help` for the complete public command list.

## Removed legacy targets

The previous Makefile mixed application features, host installation notes, and
service management. The rewrite intentionally removes:

- `qdrant-preflight` from generation: Qdrant is optional.
- `docker-build` and `docker-run`: there is no application `Dockerfile`.
- separate interactive targets: omitting `PROMPT` already starts that mode.
- demo/example targets: they duplicated normal generation with hard-coded prompts.
- statistics, learning-reset, and embedding-cache shortcuts: they exposed stale
  internal file formats and made destructive operations too easy.
- emulator installation instructions: they were distro-specific documentation,
  not build tasks.

Generated programs, learning data, embeddings, and Qdrant storage are never
deleted by `make clean`.
