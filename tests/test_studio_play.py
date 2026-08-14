"""`llmz80 play`, judged as a launcher: what would be started, and in what.

Not one emulator is started here. `play` takes the thing that starts the
process as a parameter -- the same reason `make_game` takes its stages -- so
every test below reads back the argv and the environment that a real run
would have used, and no window ever opens on the machine running the suite.

What is worth pinning, and why each one is here rather than trusted:

* the two commands, whole. They are the answer to "how does a tape load
  itself", and a flag silently dropped from either is a game that sits in
  BASIC waiting for somebody to type `LOAD ""`.
* `SDL_VIDEODRIVER=dummy`, the one variable that makes an emulator invisible.
  The gates set it on purpose; inheriting it here would produce a `play` that
  emulates perfectly and shows nobody.
* the refusals. "Not built yet" and "no emulator installed" are the two ways
  this ordinarily fails, and both have to name the way out.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from llmz80.studio import play as play_module
from llmz80.studio.make import artifact_path
from llmz80.studio.models import TargetPlatform
from llmz80.studio.play import (
    ARTIFACTS,
    Launch,
    NotPlayable,
    configured_emulator,
    find_artifact,
    how_to_play,
    plan,
    play,
)
from llmz80.studio.services import StudioService

#: Stands in for `shutil.which`: everything is installed, at a path a test can
#: recognise.
INSTALLED = lambda command: f"/usr/bin/{command}"  # noqa: E731

#: And nothing is.
MISSING = lambda _command: None  # noqa: E731

#: `config.yml`'s own emulator section, passed explicitly so a test never
#: depends on the file being next to whatever directory pytest ran in.
CONFIG = {
    "emulator": {
        "spectrum": {"name": "zesarux", "params": "--machine 48k"},
        "amstrad_cpc": {"name": "cap32", "params": "--machine 6128"},
    }
}


class _Recorder:
    """A `start` that records instead of starting."""

    def __init__(self) -> None:
        self.launches: list[tuple[Launch, bool]] = []

    def __call__(self, launch: Launch, *, wait: bool) -> int:
        self.launches.append((launch, wait))
        return 0


def _tape(directory: Path, name: str = "output.tap") -> Path:
    build = directory / "build"
    build.mkdir(parents=True, exist_ok=True)
    artifact = build / name
    artifact.write_bytes(b"\x13\x00\x00" + bytes(20))
    return artifact


# --- the command, per machine ----------------------------------------------


def test_a_spectrum_tape_is_smartloaded_so_nobody_types_load(tmp_path: Path):
    """The whole point of the command, as one assertion: the tape is handed to
    ZEsarUX positionally -- which is SmartLoad, the mode that inserts *and*
    autoloads -- at top speed, on the 48K the gates verified it on."""
    artifact = _tape(tmp_path)

    launch = plan(tmp_path, config=CONFIG, which=INSTALLED)

    assert launch.platform == "spectrum"
    assert launch.command == [
        "/usr/bin/zesarux",
        "--noconfigfile",
        "--machine",
        "48k",
        "--realvideo",
        "--nosplash",
        "--zoom",
        "2",
        "--fastautoload",
        "--quickexit",
        str(artifact),
    ]
    # Not --tape: that inserts the tape and leaves the machine in BASIC.
    assert "--tape" not in launch.command
    # And nothing that would make it invisible or bounded: this is the half of
    # the project that has a person in front of it.
    assert not {"--vo", "--exit-after", "--vofile"} & set(launch.command)


def test_a_cpc_disk_is_run_by_name_after_the_firmware_is_up(tmp_path: Path):
    """A mounted DSK stops at the BASIC prompt, so Caprice32 is given the
    `run"..."` to type -- the same one the smoke harness types."""
    build = tmp_path / "build"
    build.mkdir()
    artifact = build / "output.dsk"
    artifact.write_bytes(b"MV - CPCEMU Disk-File" + bytes(64))

    launch = plan(tmp_path, config=CONFIG, which=INSTALLED)

    assert launch.platform == "amstrad_cpc"
    assert launch.command == [
        "/usr/bin/cap32",
        "-O",
        "system.boot_time=75",
        "-a",
        'run"program.bin"',
        str(artifact),
    ]
    # `emulator.amstrad_cpc.params` in config.yml says `--machine 6128`, which
    # Caprice32 has no such option for; only the emulator's *name* is read
    # from there.
    assert "--machine" not in launch.command


def test_the_emulator_name_comes_from_the_configuration(tmp_path: Path):
    _tape(tmp_path)

    launch = plan(tmp_path, config={"emulator": {"spectrum": {"name": "fuse"}}}, which=INSTALLED)

    assert launch.emulator == "fuse"
    assert launch.command[0] == "/usr/bin/fuse"


def test_an_absent_configuration_falls_back_to_the_emulator_the_gates_drive():
    assert configured_emulator("spectrum", {}) == "zesarux"
    assert configured_emulator("amstrad_cpc", {}) == "cap32"


# --- the environment -------------------------------------------------------


def test_the_variable_that_makes_the_gates_invisible_is_dropped(tmp_path: Path, monkeypatch):
    """`emulator_smoke.py` sets SDL_VIDEODRIVER=dummy so Caprice32 runs with no
    display at all. Inherited here it would open no window and read as a
    hang."""
    _tape(tmp_path)
    monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")

    launch = plan(tmp_path, config=CONFIG, which=INSTALLED)

    assert "SDL_VIDEODRIVER" not in launch.env


def test_a_video_driver_somebody_chose_on_purpose_is_left_alone(tmp_path: Path, monkeypatch):
    _tape(tmp_path)
    monkeypatch.setenv("SDL_VIDEODRIVER", "wayland")

    assert plan(tmp_path, config=CONFIG, which=INSTALLED).env["SDL_VIDEODRIVER"] == "wayland"


def test_the_rest_of_the_environment_is_inherited(tmp_path: Path, monkeypatch):
    _tape(tmp_path)
    monkeypatch.setenv("DISPLAY", ":1")

    assert plan(tmp_path, config=CONFIG, which=INSTALLED).env["DISPLAY"] == ":1"


# --- which file ------------------------------------------------------------


def test_the_project_directory_the_order_leaves_is_enough(tmp_path: Path):
    artifact = _tape(tmp_path)

    assert find_artifact(tmp_path) == artifact


def test_the_artifact_itself_is_accepted(tmp_path: Path):
    artifact = _tape(tmp_path)

    assert find_artifact(artifact) == artifact
    assert find_artifact(artifact.parent) == artifact


def test_play_and_make_look_for_the_very_same_file(tmp_path: Path):
    """A `play` that looked for a different name than `make` publishes would
    be a command that never finds a finished game."""
    service = StudioService.at(tmp_path)
    for platform in TargetPlatform:
        project, directory = service.create_project(platform.value.title(), platform)
        assert artifact_path(project, directory).name == ARTIFACTS[platform.value]


def test_a_project_with_no_build_is_told_how_to_get_one(tmp_path: Path):
    with pytest.raises(NotPlayable) as refusal:
        find_artifact(tmp_path)

    said = " ".join(refusal.value.lines)
    assert "No game has been built" in said
    assert f"llmz80 project build {tmp_path}" in said
    assert "llmz80 make" in said


def test_a_file_that_is_not_a_game_is_refused(tmp_path: Path):
    source = tmp_path / "main.c"
    source.write_text("int main(void) { return 0; }", encoding="utf-8")

    with pytest.raises(NotPlayable) as refusal:
        find_artifact(source)

    assert ".tap" in str(refusal.value) and ".dsk" in str(refusal.value)


def test_a_path_that_is_not_there_says_so(tmp_path: Path):
    with pytest.raises(NotPlayable) as refusal:
        find_artifact(tmp_path / "nowhere")

    assert "There is nothing at" in str(refusal.value)


# --- refusing rather than starting something that cannot work --------------


def test_a_missing_emulator_is_named_along_with_how_to_get_it(tmp_path: Path):
    _tape(tmp_path)

    with pytest.raises(NotPlayable) as refusal:
        plan(tmp_path, config=CONFIG, which=MISSING)

    said = " ".join(refusal.value.lines)
    assert "zesarux is not on PATH" in said
    assert "ZEsarUX" in said


def test_play_reports_a_refusal_and_exits_non_zero(tmp_path: Path):
    said: list[str] = []
    started = _Recorder()

    code = play(tmp_path, say=said.append, config=CONFIG, which=MISSING, start=started)

    assert code == 1
    assert started.launches == []
    assert any("no game has been built" in line.casefold() for line in said)


# --- waiting, or letting it go ---------------------------------------------


def test_the_command_waits_for_the_emulator_by_default(tmp_path: Path):
    """Somebody typed `llmz80 play` to play now: the terminal has nothing else
    to do until they stop, and the exit code is the emulator's."""
    artifact = _tape(tmp_path)
    started = _Recorder()

    code = play(tmp_path, say=lambda _line: None, config=CONFIG, which=INSTALLED, start=started)

    assert code == 0
    ((launch, waited),) = started.launches
    assert waited is True
    assert launch.artifact == artifact


def test_a_caller_with_a_screen_to_keep_drawing_does_not_wait(tmp_path: Path):
    _tape(tmp_path)
    started = _Recorder()

    play(
        tmp_path,
        wait=False,
        say=lambda _line: None,
        config=CONFIG,
        which=INSTALLED,
        start=started,
    )

    assert started.launches[0][1] is False


def test_letting_it_go_detaches_it_from_the_terminal(monkeypatch, tmp_path: Path):
    """The screen's launch must survive the viewer and never print over it."""
    seen: dict[str, object] = {}

    class _Popen:
        def __init__(self, command, **kwargs):
            seen.update(kwargs, command=command)

    monkeypatch.setattr(play_module.subprocess, "Popen", _Popen)
    launch = Launch("zesarux", "spectrum", tmp_path / "output.tap", ["zesarux"], {})

    assert play_module.start(launch, wait=False) == 0
    assert seen["start_new_session"] is True
    assert seen["stdout"] == play_module.subprocess.DEVNULL
    assert seen["stderr"] == play_module.subprocess.DEVNULL


def test_waiting_uses_the_emulators_own_exit_code(monkeypatch, tmp_path: Path):
    class _Completed:
        returncode = 3

    monkeypatch.setattr(play_module.subprocess, "run", lambda *a, **k: _Completed())
    launch = Launch("zesarux", "spectrum", tmp_path / "output.tap", ["zesarux"], {})

    assert play_module.start(launch, wait=True) == 3


def test_how_to_play_is_the_order_a_person_can_copy(tmp_path: Path):
    assert how_to_play(tmp_path) == f"llmz80 play {tmp_path}"
