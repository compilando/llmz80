"""Where CPCtelera is, and turning a built directory into a project it accepts.

These two facts used to live in `llm_z80.py`, the legacy generator, and
`studio/compiler.py` imported them from there -- the one edge that kept a
retired 1591-line module in the import graph of the live pipeline.
"""

from pathlib import Path

import pytest

from llmz80.core.toolchain import (
    TEMPLATE_DIR,
    prepare_amstrad_cpc_build_project,
    resolve_cpct_path,
    validate_toolchain_environment,
)


def _fake_cpctelera(root: Path, *, built: bool = True) -> Path:
    """A checkout `resolve_cpct_path` recognises: the tree, and its toolchain.

    `built=False` is the shape a bare `git clone` has -- every source file
    present and `tools/sdcc-*/bin/` empty, which is what `vendor/cpctelera`
    is on a machine where CPCtelera's `setup.sh` has never run.
    """
    (root / "src").mkdir(parents=True, exist_ok=True)
    (root / "cfg").mkdir(parents=True, exist_ok=True)
    (root / "src" / "cpctelera.h").write_text("/* stub */\n", encoding="utf-8")
    (root / "cfg" / "global_main_makefile.mk").write_text("# stub\n", encoding="utf-8")
    sdcc_bin = root / "tools" / "sdcc-3.6.8-r9946" / "bin"
    sdcc_bin.mkdir(parents=True, exist_ok=True)
    if built:
        (sdcc_bin / "sdcc").write_text("#!/bin/sh\n", encoding="utf-8")
    return root


@pytest.fixture(autouse=True)
def _no_ambient_cpctelera(tmp_path, monkeypatch):
    """Neither this machine's install nor this repo's vendor may answer.

    Every test here is about the ordering rules, and a candidate the test did
    not create is one it cannot reason about: without this, `~/cpctelera` and
    `vendor/` both take part, and a test asserting `None` passes or fails
    according to what the developer happens to have installed.
    """
    monkeypatch.delenv("CPCT_PATH", raising=False)
    monkeypatch.setattr(
        "llmz80.core.toolchain.VENDOR_DIR", tmp_path / "absent-vendor", raising=True
    )
    monkeypatch.setattr(
        "llmz80.core.toolchain.SYSTEM_CANDIDATES", (tmp_path / "absent-opt",), raising=True
    )
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path / "absent-home"))


class TestResolveCpctPath:
    def test_the_environment_wins_over_everything(self, tmp_path, monkeypatch):
        chosen = _fake_cpctelera(tmp_path / "from-env")
        ignored = _fake_cpctelera(tmp_path / "from-config")
        monkeypatch.setenv("CPCT_PATH", str(chosen))

        found = resolve_cpct_path({"compiler": {"amstrad_cpc": {"cpct_path": str(ignored)}}})

        assert found == chosen.resolve()

    def test_the_config_is_read_when_the_environment_says_nothing(self, tmp_path):
        configured = _fake_cpctelera(tmp_path / "from-config")

        found = resolve_cpct_path({"compiler": {"amstrad_cpc": {"cpct_path": str(configured)}}})

        assert found == configured.resolve()

    def test_a_directory_without_the_two_markers_is_not_a_checkout(self, tmp_path, monkeypatch):
        # A bare directory, or one holding only half the layout, is refused
        # rather than returned and left to fail inside `make` with a
        # diagnostic about a missing include.
        half = tmp_path / "half"
        (half / "src").mkdir(parents=True)
        (half / "src" / "cpctelera.h").write_text("/* stub */\n", encoding="utf-8")
        monkeypatch.setenv("CPCT_PATH", str(half))

        assert resolve_cpct_path({}) is None

    def test_a_checkout_whose_toolchain_was_never_built_is_refused(self, tmp_path, monkeypatch):
        """The failure this predicate exists to move earlier.

        CPCtelera compiles with the SDCC *inside* the checkout --
        `cfg/global_paths.mk` sets `SDCCBIN_PATH := $(CPCT_PATH)tools/sdcc-*/bin/`
        -- and `setup.sh` is what puts it there. A fresh clone has every
        source file and no compiler, so accepting it hands `make` a path it
        cannot execute: exit code 127, `sdcc: No such file or directory`, and
        a diagnostic that says nothing about setup never having been run.
        """
        unbuilt = _fake_cpctelera(tmp_path / "cloned-not-built", built=False)
        monkeypatch.setenv("CPCT_PATH", str(unbuilt))

        assert resolve_cpct_path({}) is None

    def test_nothing_configured_and_nothing_installed_answers_none(self):
        assert resolve_cpct_path(None) is None

    def test_the_vendored_checkout_is_a_candidate(self, tmp_path, monkeypatch):
        """`vendor/cpctelera/src/cpctelera` is a pinned checkout this repo owns.

        It was not on the candidate list at all, so the commit
        `vendor/cpctelera/ENGINE.json` pins was never what anything built
        against -- the build silently used whatever CPCtelera the host
        happened to have in `~` or `/opt`, which is the reverse of what
        pinning a commit is for. It only wins once it is set up, which the
        test above is the other half of.
        """
        vendored = _fake_cpctelera(tmp_path / "vendor" / "cpctelera" / "src" / "cpctelera")
        monkeypatch.setattr("llmz80.core.toolchain.VENDOR_DIR", vendored, raising=True)

        assert resolve_cpct_path({}) == vendored.resolve()

    def test_an_explicit_choice_still_beats_the_vendored_checkout(self, tmp_path, monkeypatch):
        vendored = _fake_cpctelera(tmp_path / "vendored")
        explicit = _fake_cpctelera(tmp_path / "explicit")
        monkeypatch.setattr("llmz80.core.toolchain.VENDOR_DIR", vendored, raising=True)
        monkeypatch.setenv("CPCT_PATH", str(explicit))

        assert resolve_cpct_path({}) == explicit.resolve()

    def test_a_working_install_is_preferred_to_an_unbuilt_vendored_one(self, tmp_path, monkeypatch):
        """The ordering bug this whole predicate was written to stop.

        Putting the vendored checkout ahead of `~/cpctelera` is right when
        both work -- a pinned commit beats whatever the host has. It is wrong
        when the vendored one cannot compile, and that is the common case,
        because `vendor/*/src/` is gitignored and setting it up is a separate,
        manual, half-hour step. Nine toolchain tests went from passing to
        failing on exactly this.
        """
        _fake_cpctelera(tmp_path / "vendored", built=False)
        installed = _fake_cpctelera(tmp_path / "home" / "cpctelera" / "cpctelera")
        monkeypatch.setattr("llmz80.core.toolchain.VENDOR_DIR", tmp_path / "vendored", raising=True)
        monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path / "home"))

        assert resolve_cpct_path({}) == installed.resolve()


class TestPrepareBuildProject:
    def test_it_refuses_a_directory_that_is_not_cpctelera(self, tmp_path):
        (tmp_path / "main.c").write_text("void main(void){}\n", encoding="utf-8")

        assert not prepare_amstrad_cpc_build_project(tmp_path, tmp_path / "nowhere")

    def test_it_works_from_any_working_directory(self, tmp_path, monkeypatch):
        """The templates are found relative to the package, not to the cwd.

        `Path("templates/amstrad_cpc")` is what this used to read, so every
        CPC build depended on the process happening to have been started from
        the checkout root. `llmz80 make` run from anywhere else prepared no
        `cfg/` at all and failed inside `make`, complaining about a missing
        `build_config.mk` rather than about the cwd it really depended on.
        """
        cpct = _fake_cpctelera(tmp_path / "cpctelera")
        output = tmp_path / "out"
        output.mkdir()
        (output / "main.c").write_text("void main(void){}\n", encoding="utf-8")
        elsewhere = tmp_path / "elsewhere"
        elsewhere.mkdir()
        monkeypatch.chdir(elsewhere)

        assert prepare_amstrad_cpc_build_project(output, cpct)

        assert (output / "Makefile").exists()
        assert (output / "src" / "main.c").exists()
        assert (output / "cfg" / "build_config.mk").exists()

    def test_the_cpctelera_path_is_substituted_into_build_config(self, tmp_path):
        cpct = _fake_cpctelera(tmp_path / "cpctelera")
        output = tmp_path / "out"
        output.mkdir()
        (output / "main.c").write_text("void main(void){}\n", encoding="utf-8")

        assert prepare_amstrad_cpc_build_project(output, cpct)

        build_config = (output / "cfg" / "build_config.mk").read_text(encoding="utf-8")
        assert "{{CPCT_PATH}}" not in build_config
        assert str(cpct.resolve()) in build_config

    def test_it_leaves_sources_studio_already_wrote_in_place(self, tmp_path):
        """Studio's multi-file layout writes `src/` before this ever runs.

        This copies `main.c` up into `src/` for the legacy generator, which
        only ever produced `output_dir/main.c`. Studio has already put every
        source there, so the copy must not disturb the siblings.
        """
        cpct = _fake_cpctelera(tmp_path / "cpctelera")
        output = tmp_path / "out"
        (output / "src").mkdir(parents=True)
        (output / "main.c").write_text("void main(void){}\n", encoding="utf-8")
        (output / "src" / "main.c").write_text("void main(void){}\n", encoding="utf-8")
        (output / "src" / "platform.c").write_text("/* platform */\n", encoding="utf-8")

        assert prepare_amstrad_cpc_build_project(output, cpct)

        assert (output / "src" / "platform.c").exists()

    def test_a_project_with_no_main_c_reaches_the_build_instead_of_raising(self, tmp_path):
        """`FileNotFoundError` out of the layout step told nobody anything.

        A design whose program declares no `main.c` is a broken program, and
        the build says so clearly. Blowing up here replaced that with a
        traceback about a missing file in a temporary directory.
        """
        cpct = _fake_cpctelera(tmp_path / "cpctelera")
        output = tmp_path / "out"
        output.mkdir()

        assert prepare_amstrad_cpc_build_project(output, cpct)

    def test_the_templates_ship_with_the_package(self):
        assert (TEMPLATE_DIR / "Makefile").is_file()
        assert (TEMPLATE_DIR / "cfg" / "build_config.mk").is_file()


@pytest.mark.parametrize("name", ["resolve_cpct_path", "prepare_amstrad_cpc_build_project"])
def test_the_studio_compiler_does_not_import_these_from_the_legacy_generator(name):
    """The edge this module exists to cut, pinned so it cannot grow back."""
    source = (Path(__file__).resolve().parents[1] / "llmz80" / "studio" / "compiler.py").read_text(
        encoding="utf-8"
    )

    assert "from llm_z80 import" not in source
    assert name in source


class TestValidateToolchainEnvironment:
    def test_a_missing_spectrum_compiler_is_named(self, monkeypatch):
        monkeypatch.setattr("llmz80.core.toolchain.shutil.which", lambda name: None)

        ok, message = validate_toolchain_environment("spectrum", {})

        assert not ok
        assert "zcc" in message

    def test_the_configured_spectrum_compiler_is_the_one_looked_for(self, monkeypatch):
        seen = []
        monkeypatch.setattr(
            "llmz80.core.toolchain.shutil.which", lambda name: seen.append(name) or None
        )

        validate_toolchain_environment("spectrum", {"compiler": {"spectrum": {"c_compiler": "zx"}}})

        assert seen == ["zx"]

    def test_a_present_spectrum_compiler_passes_with_nothing_to_say(self, monkeypatch):
        monkeypatch.setattr("llmz80.core.toolchain.shutil.which", lambda name: "/usr/bin/zcc")

        assert validate_toolchain_environment("spectrum", {}) == (True, "")

    def test_the_cpc_needs_make(self, monkeypatch):
        monkeypatch.setattr("llmz80.core.toolchain.shutil.which", lambda name: None)

        ok, message = validate_toolchain_environment("amstrad_cpc", {})

        assert not ok
        assert "make" in message

    def test_an_unbuilt_cpctelera_is_reported_here_rather_than_by_make(self, tmp_path, monkeypatch):
        """The whole point of asking before spending anything.

        A clone that never ran CPCtelera's `setup.sh` used to pass this check
        and then die at exit code 127 several minutes and one model call
        later, with a diagnostic naming a missing `sdcc` binary and nothing
        about setup.
        """
        monkeypatch.setattr("llmz80.core.toolchain.shutil.which", lambda name: "/usr/bin/make")
        monkeypatch.setenv("CPCT_PATH", str(_fake_cpctelera(tmp_path / "clone", built=False)))

        ok, message = validate_toolchain_environment("amstrad_cpc", {})

        assert not ok
        assert "setup.sh" in message

    def test_a_working_cpc_toolchain_passes(self, tmp_path, monkeypatch):
        monkeypatch.setattr("llmz80.core.toolchain.shutil.which", lambda name: "/usr/bin/make")
        monkeypatch.setenv("CPCT_PATH", str(_fake_cpctelera(tmp_path / "cpctelera")))

        assert validate_toolchain_environment("amstrad_cpc", {}) == (True, "")

    def test_an_unknown_platform_is_refused_by_name(self):
        ok, message = validate_toolchain_environment("commodore_64", {})

        assert not ok
        assert "commodore_64" in message
