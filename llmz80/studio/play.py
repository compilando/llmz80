"""Play the game: the emulator, visible, with the game already loading.

Everything else in this package builds an artifact and then looks at it
through a machine -- `quality/emulator_smoke.py` starts the very same two
emulators, but with `--vo null` or `SDL_VIDEODRIVER=dummy`, because it wants
a framebuffer to hash, not a window to sit in front of. This module is the
other half of that: the same emulators, the same machine, no capture, and a
window.

Three things decide the command, and all three are read off what the gates
already do rather than invented here:

* **Which emulator.** `config.yml`'s `emulator.<platform>.name`, with the
  installed defaults as the fallback. Only the *name* comes from there: that
  section's `params` are not valid options for the emulators it names
  (`cap32` has no `--machine`), so the arguments are built here instead.
* **Which machine.** The one the gates verified the game on -- a 48K
  Spectrum, and Caprice32's own default CPC. Playing on a different model
  than the one that passed the gates would make the verdict meaningless.
* **How it loads itself.** Nobody should have to type `LOAD ""` into BASIC.
  On the Spectrum a file given as a positional argument is ZEsarUX's
  SmartLoad, which inserts the tape *and* autoloads it (`--noautoload` is
  what turns that off), and `--fastautoload` does that at top speed so the
  wait is seconds rather than the tape's real minutes. On the CPC mounting a
  DSK only reaches the BASIC prompt, so Caprice32 is handed the `run"..."`
  through its autocmd queue after the firmware boot delay -- exactly what
  the smoke harness does.

The environment matters as much as the command: `SDL_VIDEODRIVER=dummy` is
what makes the harness invisible, and a `play` inheriting it from a shell
that ran the harness would open no window at all and look like a hang.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Mapping

#: The canonical artifact per platform. The same two names `make.artifact_path`
#: and `release.export_release` use -- a test holds them to it, because a
#: `play` that looked for a different file than `make` writes would be a
#: command that never finds a finished game.
ARTIFACTS = {"spectrum": "output.tap", "amstrad_cpc": "output.dsk"}

#: Which platform an artifact belongs to, read off its extension. The only
#: thing a bare `.tap` or `.dsk` on disk can be asked.
PLATFORMS = {".tap": "spectrum", ".dsk": "amstrad_cpc"}

#: Used when `config.yml` is not where this runs, or says nothing about an
#: emulator. Both are the emulator the gates drive for that platform.
DEFAULT_EMULATORS = {"spectrum": "zesarux", "amstrad_cpc": "cap32"}

#: How to get each emulator, said to somebody who has just been told it is
#: missing. Package names rather than a distribution's command, since the
#: command differs and the name mostly does not.
INSTALL_HINT = {
    "zesarux": "ZEsarUX (package `zesarux`)",
    "cap32": "Caprice32 (package `cap32` or `caprice32`)",
    "caprice32": "Caprice32 (package `caprice32` or `cap32`)",
}

#: The AMSDOS file the CPC build publishes inside the disk image, and what
#: `run"…"` has to name. The same string `emulator_smoke._run_caprice32`
#: types.
CPC_PROGRAM = "program.bin"

#: Frames of firmware boot Caprice32 waits before it starts typing. Below
#: this the `run"…"` is swallowed by a CPC that is still coming up.
CPC_BOOT_FRAMES = 75


class NotPlayable(Exception):
    """There is nothing to play, or nothing to play it with.

    Carries the sentences a person needs, not a stack trace: what is missing
    and the order that produces it. Raised rather than printed so the screen
    and the command can each say it their own way.
    """

    def __init__(self, *lines: str) -> None:
        super().__init__(lines[0] if lines else "")
        self.lines = list(lines)


@dataclass(frozen=True)
class Launch:
    """Exactly what would be started, before anything is.

    A value rather than a side effect so it can be read: printed by the
    command, asserted by a test, and -- the point -- shown in a bug report
    when an emulator does something surprising.
    """

    emulator: str
    platform: str
    artifact: Path
    command: list[str]
    env: dict[str, str]


def find_artifact(target: Path) -> Path:
    """The tape or disk image `target` means, or a refusal that says why.

    `target` may be the artifact itself, the project directory `make` left,
    or that project's `build/` -- the three things somebody has in front of
    them when they want to play. Anything else, and the refusal names the
    order that builds one, because "not built yet" is the overwhelmingly
    likely reason a path holds no game.
    """
    target = target.expanduser()
    if target.is_file():
        if target.suffix.lower() not in PLATFORMS:
            raise NotPlayable(
                f"{target} is not a game: expected a .tap (Spectrum) or a .dsk (CPC)."
            )
        return target.resolve()
    if not target.is_dir():
        raise NotPlayable(f"There is nothing at {target}.")
    for directory in (target / "build", target):
        for name in ARTIFACTS.values():
            candidate = directory / name
            if candidate.is_file():
                return candidate.resolve()
    raise NotPlayable(
        f"No game has been built in {target} yet.",
        f"Build it with `llmz80 project build {target}`, "
        "or make one from scratch with `llmz80 make 'what the game should be'`.",
    )


def configured_emulator(platform: str, config: Mapping | None = None) -> str:
    """The emulator named for `platform`, from `config.yml` or the default.

    Only the name is taken. `emulator.<platform>.params` is left alone on
    purpose: it says `--machine 6128` for Caprice32, which has no such
    option and would refuse to start.
    """
    if config is None:
        from llmz80.utils.config import load_config

        config = load_config("config.yml")
    named = (config.get("emulator") or {}).get(platform) or {}
    return str(named.get("name") or DEFAULT_EMULATORS[platform])


def _environment() -> dict[str, str]:
    """The caller's environment, minus the one variable that hides windows.

    `SDL_VIDEODRIVER=dummy` is how `emulator_smoke.py` runs Caprice32 with no
    display at all. Exported into a shell -- or inherited from one that ran
    the gates -- it would make this command emulate the game perfectly and
    show nobody. Only that value is dropped: somebody who set the variable to
    `wayland` or `x11` meant it.
    """
    environment = dict(os.environ)
    if environment.get("SDL_VIDEODRIVER", "").strip().casefold() == "dummy":
        del environment["SDL_VIDEODRIVER"]
    return environment


def plan(
    target: Path,
    *,
    config: Mapping | None = None,
    which: Callable[[str], str | None] = shutil.which,
) -> Launch:
    """Everything needed to start the game, with nothing started.

    Refuses -- rather than starting a process that cannot work -- when there
    is no artifact or the emulator for its platform is not installed.
    """
    artifact = find_artifact(target)
    platform = PLATFORMS[artifact.suffix.lower()]
    emulator = configured_emulator(platform, config)
    executable = which(emulator)
    if not executable:
        raise NotPlayable(
            f"The emulator for this game is not installed: {emulator} is not on PATH.",
            f"Install {INSTALL_HINT.get(emulator, emulator)} and run this again.",
        )
    if platform == "spectrum":
        command = [
            executable,
            # First, and ZEsarUX insists on that: any later and it is ignored.
            # A person's own .zesaruxrc could have set a different machine, or
            # turned autoload off, and then the game would sit in BASIC.
            "--noconfigfile",
            "--machine",
            "48k",
            "--realvideo",
            "--nosplash",
            "--zoom",
            "2",
            # The tape loads itself, and quickly. Without this the artifact
            # is only inserted and somebody has to type LOAD "" -- and then
            # wait out the real loading time of a real cassette.
            "--fastautoload",
            # Closing the window is how a person stops playing; a modal
            # "are you sure?" over a game they have already left is noise.
            "--quickexit",
            # No --tape: a bare filename is SmartLoad, which is the mode that
            # inserts *and* autoloads.
            str(artifact),
        ]
    else:
        command = [
            executable,
            "-O",
            f"system.boot_time={CPC_BOOT_FRAMES}",
            # A mounted DSK stops at the BASIC prompt. Caprice32's autocmd
            # queue types the AMSDOS filename once the firmware is up, and
            # then hands the machine over.
            "-a",
            f'run"{CPC_PROGRAM}"',
            str(artifact),
        ]
    return Launch(
        emulator=emulator,
        platform=platform,
        artifact=artifact,
        command=command,
        env=_environment(),
    )


def start(launch: Launch, *, wait: bool) -> int:
    """Start the emulator, waiting for it or letting it go.

    Both, because the two callers want opposite things and neither is wrong.
    `llmz80 play` waits: somebody typed it to play now, the terminal has
    nothing else to do meanwhile, and Ctrl-C reaching the emulator is what
    they would expect. The Studio screen does not: it has to keep reading the
    diary and answering its own keys, and a window opening in front of a
    frozen viewer would read as a crash. What is let go is fully detached --
    its own session, and its output thrown away rather than printed over
    whatever drew the terminal.
    """
    if wait:
        return subprocess.run(launch.command, env=launch.env, check=False).returncode
    subprocess.Popen(
        launch.command,
        env=launch.env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    return 0


def how_to_play(target: Path) -> str:
    """The order that plays this game, spelled out for somebody to copy."""
    return f"llmz80 play {target}"


def play(
    target: Path,
    *,
    wait: bool = True,
    say: Callable[[str], None] = print,
    config: Mapping | None = None,
    which: Callable[[str], str | None] = shutil.which,
    start: Callable[..., int] = start,
) -> int:
    """Start the game and return the exit code the command should use.

    `start` is injected for the same reason `make_game` takes its stages: the
    only way to test what would be run -- and in what environment -- is to be
    able to run it against something that opens no window.
    """
    try:
        launch = plan(target, config=config, which=which)
    except NotPlayable as refusal:
        for line in refusal.lines:
            say(line)
        return 1
    say(f"Playing {launch.artifact} on {launch.emulator}.")
    return start(launch, wait=wait)
