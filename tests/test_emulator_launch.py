from pathlib import Path

import llm_z80


class _Completed:
    def __init__(self, returncode=0):
        self.returncode = returncode


def test_cap32_interactive_launcher_mounts_and_autoruns_program_bin(monkeypatch, tmp_path: Path):
    artifact = tmp_path / "output.dsk"
    artifact.write_bytes(b"MV - CPCEMU Disk-File" + bytes(256))
    commands = []

    def fake_run(command, **kwargs):
        commands.append(command)
        return _Completed()

    monkeypatch.setattr(llm_z80.subprocess, "run", fake_run)
    config = {
        "paths": {"amstrad_cpc": {"output_artifact": "output.dsk"}},
        "emulator": {"amstrad_cpc": {"name": "cap32"}},
    }

    llm_z80.launch_emulator_for_platform("amstrad_cpc", tmp_path, config)

    assert commands[0] == ["which", "cap32"]
    assert commands[1] == [
        "cap32",
        "-O", "system.boot_time=75",
        "-a", 'run"program.bin"',
        str(artifact.resolve()),
    ]
