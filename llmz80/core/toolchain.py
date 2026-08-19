"""Whether this machine can build for a target, and what CPCtelera needs first.

Everything about the *build environment* rather than about the program being
built: where CPCtelera is, what shape a directory has to be in before `make`
will accept it, and whether either target's toolchain is installed at all.

These lived in `llm_z80.py` until now. That module is the legacy single-file
generator, retired in favour of `llmz80.studio`, and `studio/compiler.py`
importing two names out of it was the one edge keeping 1591 lines of retired
code inside the live pipeline's import graph -- so the legacy generator could
not be deleted without taking the CPC build with it. The functions keep the
behaviour they had apart from the bugs noted on each.
"""

from __future__ import annotations

import logging
import os
import shutil
from pathlib import Path

#: The repository root, found the way every other module in this package finds
#: it (`studio/codegen.py`, `studio/retrieval.py`, `utils/config.py`), so a
#: path here does not depend on which directory the process was started from.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

#: The CPCtelera project skeleton: a Makefile and the `cfg/*.mk` its build
#: reads. Package-relative on purpose -- see `prepare_amstrad_cpc_build_project`.
TEMPLATE_DIR = PROJECT_ROOT / "templates" / "amstrad_cpc"

#: The checkout this repository pins. `vendor/cpctelera/ENGINE.json` records a
#: full commit and `vendor/*/src/` is gitignored, so the directory exists only
#: on a machine that has vendored it -- which is exactly the condition
#: `resolve_cpct_path` tests before preferring it.
VENDOR_DIR = PROJECT_ROOT / "vendor" / "cpctelera" / "src" / "cpctelera"

#: Where a system-wide install conventionally lands, tried last. `Path.home()`
#: is read at call time rather than baked in here, so a test can move it.
SYSTEM_CANDIDATES: tuple[Path, ...] = (Path("/opt/cpctelera"),)


def _is_cpctelera(path: Path) -> bool:
    """Whether `path` is a CPCtelera a build can actually use.

    Three things, and the third is the one this had been missing.

    The first two are the tree: the umbrella header every generated program
    includes, and the makefile fragment `templates/amstrad_cpc/Makefile`
    includes. A directory with only one of them is a partial clone or an
    unrelated tree.

    The third is the toolchain. CPCtelera does not build with the system SDCC;
    `cfg/global_paths.mk` sets `SDCCBIN_PATH := $(CPCT_PATH)tools/sdcc-*/bin/`
    and every compile invokes the SDCC *inside the checkout*, which only
    exists after `setup.sh` has downloaded and built it. A fresh `git clone`
    therefore satisfies both file checks and compiles nothing: `make` dies
    with `sdcc: No such file or directory` and exit code 127.

    That is not hypothetical -- it is exactly what `vendor/cpctelera` is. The
    commit is pinned, the sources are there, and `tools/sdcc-3.6.8-r9946/bin/`
    is empty, so preferring it over a working install turned nine passing
    toolchain tests into failures. Testing for the compiler keeps the answer
    to "where is CPCtelera" and "can I build with it" the same answer, which
    is what every caller here actually wants to know.

    The version in the path is globbed rather than pinned to the
    `sdcc-3.6.8-r9946` the makefile names: a checkout at a different commit
    bundles a different SDCC, and this predicate is asked about checkouts it
    did not choose.
    """
    if not (path / "src" / "cpctelera.h").exists():
        return False
    if not (path / "cfg" / "global_main_makefile.mk").exists():
        return False
    return any((path / "tools").glob("sdcc-*/bin/sdcc"))


def resolve_cpct_path(config: dict | None = None) -> Path | None:
    """Where CPCtelera is on this machine, or `None`.

    In order: `$CPCT_PATH`, `compiler.amstrad_cpc.cpct_path` in config.yml,
    this repository's own vendored checkout, then the conventional install
    locations. Explicit beats vendored beats conventional, so a developer
    pointing at a working tree of their own is never overruled by a checkout
    that happens to be present.

    The vendored checkout was not on this list at all until now, which made
    the pinning in `vendor/cpctelera/ENGINE.json` decorative: the commit was
    recorded, `scripts/vendor_engine.py` checked it out, and then every build
    used whichever CPCtelera the host had in `~` or `/opt` instead. A pin that
    nothing builds against does not make a build reproducible.
    """
    configured = (config or {}).get("compiler", {}).get("amstrad_cpc", {}).get("cpct_path")
    candidates: list[Path | str | None] = [
        os.environ.get("CPCT_PATH"),
        configured,
        VENDOR_DIR,
        Path.home() / "cpctelera" / "cpctelera",
        Path.home() / "cpctelera",
        *SYSTEM_CANDIDATES,
    ]
    for candidate in candidates:
        if not candidate:
            continue
        path = Path(candidate).expanduser().resolve()
        if _is_cpctelera(path):
            return path
    return None


def prepare_amstrad_cpc_build_project(output_dir: Path, cpct_dir: Path) -> bool:
    """Lay `output_dir` out as a project CPCtelera's build system accepts.

    That means a `Makefile` at the top, a `cfg/` of makefile fragments beside
    it with `{{CPCT_PATH}}` resolved, and the sources under `src/`.

    The templates are found through `TEMPLATE_DIR`, which is anchored to this
    package. It used to be the bare relative `Path("templates/amstrad_cpc")`,
    which is only correct while the process happens to be running from the
    checkout root: `llmz80 make` started anywhere else copied no `cfg/` and
    the build failed inside `make`, reporting a missing `build_config.mk`
    rather than the cwd it actually depended on. The Spectrum half of the same
    build had already been fixed for this (commit 76fd144); the CPC half had
    not, which is part of why no CPC game has been through Studio.

    The `main.c` copy into `src/` is for the legacy generator, whose whole
    output was one `output_dir/main.c`. Studio writes every source into `src/`
    itself before this runs and puts the same `main.c` at the top as well
    (`compiler.render_project`), so there the copy rewrites one file with its
    own contents and leaves the siblings beside it alone. The existence guard
    is for the third case: a project whose program declares no `main.c` at
    all, which used to raise `FileNotFoundError` out of the middle of the
    layout instead of reaching the build's own diagnostic.
    """
    if not _is_cpctelera(cpct_dir):
        logging.error("CPCtelera was not found at %s", cpct_dir)
        return False
    template_makefile = TEMPLATE_DIR / "Makefile"
    template_cfg_dir = TEMPLATE_DIR / "cfg"
    if not template_makefile.exists() or not template_cfg_dir.is_dir():
        logging.error("the CPCtelera project template is missing from %s", TEMPLATE_DIR)
        return False

    src_dir = output_dir / "src"
    cfg_dir = output_dir / "cfg"
    src_dir.mkdir(exist_ok=True)
    cfg_dir.mkdir(exist_ok=True)

    main_c = output_dir / "main.c"
    if main_c.exists():
        shutil.copy2(main_c, src_dir / "main.c")
    shutil.copy2(template_makefile, output_dir / "Makefile")

    cpct_path = str(cpct_dir.resolve())
    for cfg_file in template_cfg_dir.glob("*.mk"):
        target = cfg_dir / cfg_file.name
        shutil.copy2(cfg_file, target)
        if cfg_file.name == "build_config.mk":
            content = target.read_text(encoding="utf-8", errors="ignore")
            target.write_text(content.replace("{{CPCT_PATH}}", cpct_path), encoding="utf-8")

    return True


def validate_toolchain_environment(platform: str, config: dict) -> tuple[bool, str]:
    """Whether `platform` can be built here, and what is missing if not.

    Asked before an expensive step commits to a target: a run that will fail
    at the link step should say so before it spends a model call, and `make
    toolchain` reports both targets at once from this.

    The CPC answer is now strictly stronger than it was. It used to check that
    `make` was on the PATH and that `resolve_cpct_path` found something; the
    second half of that no longer means "a directory that looks like
    CPCtelera" but "a CPCtelera whose own SDCC has been built", so a clone
    that was never set up is reported here rather than at exit code 127 in the
    middle of a build.
    """
    if platform == "spectrum":
        compiler = config.get("compiler", {}).get(platform, {}).get("c_compiler", "zcc")
        if not shutil.which(compiler):
            return False, f"the Spectrum compiler {compiler!r} is not on the PATH"
        return True, ""

    if platform == "amstrad_cpc":
        if not shutil.which("make"):
            return False, "make is not on the PATH"
        if resolve_cpct_path(config) is None:
            return False, (
                "no set-up CPCtelera was found. Point CPCT_PATH or "
                "compiler.amstrad_cpc.cpct_path at one, and check that its own SDCC "
                "has been built -- a fresh clone needs CPCtelera's setup.sh before "
                "it can compile anything"
            )
        return True, ""

    return False, f"unsupported platform: {platform}"
