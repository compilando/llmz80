import math
import subprocess

from PIL import Image

from llmz80.quality import emulator_smoke

from llmz80.quality.emulator_smoke import (
    _cpc_input,
    _image_observation,
    _spectrum_input,
    runtime_rejection_diagnostics,
    smoke_test,
)


def _tap_block(payload: bytes) -> bytes:
    return len(payload).to_bytes(2, "little") + payload


def test_spectrum_portable_smoke_is_explicitly_not_runtime_verified(tmp_path):
    (tmp_path / "output.tap").write_bytes(_tap_block(b"header"))
    (tmp_path / "main.c").write_text(
        "void main(void){int x=0;while(1){printf(\"X\");x++;}}", encoding="utf-8"
    )
    report = smoke_test(tmp_path, "spectrum")
    assert report["static_pass"] is True
    assert report["runtime_verified"] is False
    assert report["quality_pass"] is False


def test_cpc_portable_smoke_validates_dsk_header(tmp_path):
    (tmp_path / "output.dsk").write_bytes(b"MV - CPCEMU Disk-File" + bytes(256))
    (tmp_path / "main.c").write_text(
        "void main(void){cpct_drawSprite(a,b,1,1);cpct_isKeyPressed(Key_A);}", encoding="utf-8"
    )
    report = smoke_test(tmp_path, "amstrad_cpc")
    assert report["static_pass"] is True
    assert report["quality_pass"] is False


def test_empty_artifact_fails_boot(tmp_path):
    (tmp_path / "output.tap").write_bytes(b"")
    assert smoke_test(tmp_path, "spectrum")["quality_pass"] is False


def test_frame_observation_rejects_a_blank_machine_screen(tmp_path):
    blank = tmp_path / "blank.png"
    visible = tmp_path / "visible.png"
    Image.new("RGB", (384, 270), (0, 0, 127)).save(blank)
    image = Image.new("RGB", (384, 270), (0, 0, 127))
    for x in range(100, 120):
        for y in range(100, 110):
            image.putpixel((x, y), (255, 255, 0))
    image.save(visible)
    assert _image_observation(blank)["non_blank"] is False
    assert _image_observation(visible)["non_blank"] is True


def test_cpc_input_prefers_immediately_visible_jump_transition():
    name, event = _cpc_input(
        "if (grounded && cpct_isKeyPressed(Key_Space)) jump(); "
        "cpct_isKeyPressed(Key_CursorRight);"
    )
    assert name == "Key_Space"
    assert event == " "


def test_cpc_input_uses_cursor_when_space_only_restarts_finished_state():
    name, event = _cpc_input(
        "if (state == FINISHED && cpct_isKeyPressed(Key_Space)) restart(); "
        "cpct_isKeyPressed(Key_CursorRight);"
    )
    assert name == "Key_CursorRight"
    assert event == ("\a" + chr(119)) * 5


def test_cpc_input_uses_space_to_leave_title_state():
    name, event = _cpc_input(
        "if (state == STATE_TITLE && cpct_isKeyPressed(Key_Space)) start(); "
        "cpct_isKeyPressed(Key_CursorRight);"
    )
    assert name == "Key_Space"
    assert event == " "


def test_spectrum_input_uses_space_to_leave_title_state():
    name, pressed, released = _spectrum_input(
        "/* title_screen */ if (in_key_pressed(IN_KEY_SCANCODE_SPACE)) start(); "
        "in_key_pressed(IN_KEY_SCANCODE_p);"
    )
    assert name == "space"
    assert pressed != released


def test_cpc_cursor_input_repeats_until_mode_one_byte_changes():
    name, event = _cpc_input("cpct_isKeyPressed(Key_CursorRight);")
    assert name == "Key_CursorRight"
    assert event == ("\a" + chr(119)) * 5


def test_static_portable_report_records_that_transition_is_not_required(tmp_path):
    (tmp_path / "output.tap").write_bytes(_tap_block(b"header"))
    (tmp_path / "main.c").write_text(
        'void main(void){printf("STATIC");while(1){}}', encoding="utf-8"
    )
    report = smoke_test(tmp_path, "spectrum")
    assert report["transition_required"] is False


def test_runtime_rejection_diagnostics_are_actionable():
    diagnostics = runtime_rejection_diagnostics({
        "runtime_verified": True,
        "boot": True,
        "program_loaded": True,
        "non_blank_output": True,
        "visual_change": False,
        "scripted_input_sent": True,
        "input_transition": False,
        "scripted_input": "space",
    })
    assert any("visually static" in line for line in diagnostics)
    assert any("visual_change: False" in line for line in diagnostics)


def test_caprice32_delays_post_input_screenshot(monkeypatch, tmp_path):
    captured = {}

    def fake_run(command, **kwargs):
        captured["command"] = command
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(emulator_smoke.subprocess, "run", fake_run)
    report = emulator_smoke._run_caprice32(
        {"executable": "/usr/bin/cap32"},
        tmp_path / "output.dsk",
        tmp_path,
        "if (cpct_isKeyPressed(Key_Space)) {}",
        3,
    )

    command = captured["command"]
    input_index = command.index(" ", command.index('run"program.bin"') + 1)
    assert command[input_index + 1 : input_index + 5] == [
        "-a", "CAP32_DELAY", "-a", "CAP32_SCRNSHOT"
    ]
    assert report["boot"] is False


def test_zesarux_step_reading_carries_the_step_hold(monkeypatch, tmp_path):
    """Wiring check, no real emulator needed: a scripted step's own `hold`
    reaches `step_readings` unchanged, so `animation_report` can classify a
    step as moving or idle from a fact instead of guessing from its id.

    The Caprice32 (Amstrad CPC) path above never builds `step_readings` at
    all -- `_run_caprice32` takes no `script` argument and its report has no
    such key -- which is the memory-probe limitation the CPC has: there is no
    ZRCP-style remote protocol to read memory through, so this field, like
    the rest of `step_readings`, simply does not exist there.
    """

    class _FakeConnection:
        def __enter__(self):
            return self

        def __exit__(self, *exc_info):
            return False

    class _FakeProcess:
        returncode = 0

        def communicate(self, timeout=None):
            return "", ""

    monkeypatch.setattr(emulator_smoke, "_connect_zrcp", lambda port, deadline: _FakeConnection())
    monkeypatch.setattr(emulator_smoke, "_zrcp_command", lambda *args, **kwargs: None)
    monkeypatch.setattr(emulator_smoke, "_wait_for_file", lambda *args, **kwargs: True)
    monkeypatch.setattr(emulator_smoke, "_read_probes", lambda *args, **kwargs: {"g_anim_frame": 7})
    # Patched for the same reason as `_read_probes`: the fake connection answers
    # nothing, and a screen read is not what this test is about.
    monkeypatch.setattr(emulator_smoke, "_read_screen", lambda connection: b"")
    monkeypatch.setattr(emulator_smoke.subprocess, "Popen", lambda *args, **kwargs: _FakeProcess())
    monkeypatch.setattr(emulator_smoke.time, "sleep", lambda *args, **kwargs: None)

    report = emulator_smoke._run_zesarux(
        {"executable": "/usr/bin/zesarux"},
        tmp_path / "output.tap",
        tmp_path,
        "",
        3,
        probes={"addresses": {"g_anim_frame": 32768}, "widths": {"g_anim_frame": 1}},
        script=[{"id": "rest", "hold": "none", "frames": 50}],
    )

    assert report["step_readings"] == [
        {"id": "rest", "hold": "none", "read": {"g_anim_frame": 7}}
    ]


def _observation_shaped_script() -> list[dict]:
    """Eleven steps shaped like the one `studio.observation` really emits: ten
    that press a key and a keyless idle step, which is the case the budget has
    to cover and the one it used to be cut short by."""
    directions = ("left", "right", "up", "down")
    return (
        [
            {"id": "hold_action_a", "hold": "action", "key": "space", "frames": 50},
            {"id": "hold_action_b", "hold": "action", "key": "space", "frames": 50},
        ]
        + [
            {"id": f"hold_{name}_{repeat}", "hold": name, "key": "5", "frames": 50}
            for repeat in ("a", "b")
            for name in directions
        ]
        + [{"id": "idle", "hold": "none", "key": None, "frames": 50}]
    )


def test_the_emulator_lifetime_covers_a_scripted_run():
    """A script whose steps outlive `--exit-after` loses its tail, and the tail
    is where the idle step -- half of what the animation gate claims -- lives.

    Pinned exactly rather than as a lower bound. A bound is satisfied by a
    budget that dropped a whole term: the version of this test that asserted
    `>=` stayed green with `command_cost` deleted outright, which is precisely
    the omission that truncated scripted runs in the first place.
    """
    from llmz80.quality.emulator_smoke import scripted_run_seconds

    script = _observation_shaped_script()
    probes = {"addresses": {f"g_{index}": index for index in range(8)}}

    budget = scripted_run_seconds(seconds=3, steps=script, probes=probes)

    # 6s floor + 12 reads of 8 symbols + 11 holds of a second + 10 keyed steps
    # pressing and releasing + the one screen read + the harness overhead,
    # rounded up.
    exchange = emulator_smoke._ZRCP_ROUNDTRIP * emulator_smoke._ZRCP_MARGIN
    assert budget == math.ceil(
        6
        + 12 * 8 * exchange
        + 11 * 1.0
        + 10 * 2 * exchange
        + exchange
        + emulator_smoke._HARNESS_OVERHEAD
    )
    assert budget == 64


def test_the_budget_outlasts_the_schedule_the_harness_actually_sleeps(monkeypatch, tmp_path):
    """`scripted_run_seconds` claims to say how long ZEsarUX must live to finish
    the script; the test above only pins that its arithmetic has not drifted.
    This one checks the claim, by walking `_run_zesarux` itself with every sleep
    and every socket drain accounted for and demanding the budget outlast the
    total. Written against the harness rather than against a second copy of the
    arithmetic: a re-derivation would agree with a wrong budget.
    """
    spent: list[float] = []

    class _TimedConnection:
        """Answers nothing, and charges for the wait like the real socket does."""

        def sendall(self, payload):
            return None

        def recv(self, size):
            # Every ZRCP exchange drains until the socket timeout expires; that
            # wait is not a `sleep` and so is invisible to the patch below.
            spent.append(emulator_smoke._ZRCP_DRAIN)
            raise TimeoutError

        def settimeout(self, value):
            return None

        def __enter__(self):
            return self

        def __exit__(self, *exc_info):
            return False

    class _FakeProcess:
        returncode = 0

        def communicate(self, timeout=None):
            return "", ""

    monkeypatch.setattr(emulator_smoke, "_connect_zrcp", lambda port, deadline: _TimedConnection())
    monkeypatch.setattr(emulator_smoke, "_wait_for_file", lambda *args, **kwargs: True)
    monkeypatch.setattr(emulator_smoke.subprocess, "Popen", lambda *args, **kwargs: _FakeProcess())
    monkeypatch.setattr(emulator_smoke.time, "sleep", lambda seconds: spent.append(seconds))

    script = _observation_shaped_script()
    probes = {
        "addresses": {f"g_{index}": 32768 + index for index in range(8)},
        "widths": {f"g_{index}": 1 for index in range(8)},
    }

    emulator_smoke._run_zesarux(
        {"executable": "/usr/bin/zesarux"},
        tmp_path / "output.tap",
        tmp_path,
        "",
        3,
        probes=probes,
        script=script,
    )

    assert sum(spent) < emulator_smoke.scripted_run_seconds(seconds=3, steps=script, probes=probes)


def test_a_screen_answer_becomes_the_bytes_the_machine_had():
    """ZRCP answers `read-memory` in hex pairs and then its own prompt; the
    prompt must not become pixels."""
    from llmz80.quality.emulator_smoke import _screen_from_answer

    answer = " ".join(f"{value % 256:02X}" for value in range(6912)) + "\ncommand@ deadbeef"

    screen = _screen_from_answer(answer)

    assert len(screen) == 6912
    assert screen[0] == 0
    assert screen[257] == 1


def test_a_truncated_screen_answer_is_no_screen_at_all():
    from llmz80.quality.emulator_smoke import _screen_from_answer

    assert _screen_from_answer("00 01 02") == b""


def test_the_cpc_is_driven_by_zesarux_ahead_of_caprice32(monkeypatch):
    """Caprice32 reads no memory, so a CPC run driven by it can only ever be
    judged on pixels and every behaviour gate abstains. ZEsarUX comes first
    wherever both are installed; Caprice32 stays behind it as the fallback."""
    installed = {"zesarux": "/usr/bin/zesarux", "cap32": "/usr/bin/cap32"}
    monkeypatch.setattr(emulator_smoke.shutil, "which", installed.get)

    adapter = emulator_smoke.discover_adapter("amstrad_cpc")

    assert adapter["name"] == "zesarux"
    assert adapter["capabilities"]["scripted_input"] is True

    monkeypatch.setattr(emulator_smoke.shutil, "which", {"cap32": "/usr/bin/cap32"}.get)
    assert emulator_smoke.discover_adapter("amstrad_cpc")["name"] == "cap32"


def test_the_cpc_is_typed_into_running_and_then_driven_by_key_events(monkeypatch, tmp_path):
    """The whole CPC adapter in one wiring check, no emulator needed.

    Four things here are each a silent failure if they drift. The machine must
    be the 6128, the only emulated CPC with the disc drive a .dsk needs. The
    banner ZEsarUX greets a connection with must be drained before anything
    parses an answer, because a hex-pair regex reads a banner as bytes. The
    program must be asked for by name at the BASIC prompt -- a .dsk does not
    autostart the way a .tap does -- and the `"` must arrive as SHIFT and 2,
    because ZEsarUX types no punctuation on this machine. And a held key must
    become `send-keys-event`, not the 48K keyboard-matrix bytes.
    """
    commands: list[str] = []

    class _FakeConnection:
        def __enter__(self):
            return self

        def __exit__(self, *exc_info):
            return False

    class _FakeProcess:
        returncode = 0

        def communicate(self, timeout=None):
            return "", ""

    monkeypatch.setattr(emulator_smoke, "_connect_zrcp", lambda port, deadline: _FakeConnection())
    monkeypatch.setattr(
        emulator_smoke, "_zrcp_command", lambda connection, command: commands.append(command)
    )
    monkeypatch.setattr(emulator_smoke, "_wait_for_file", lambda *args, **kwargs: True)
    monkeypatch.setattr(emulator_smoke, "_read_probes", lambda *args, **kwargs: {"g_score": 5})
    monkeypatch.setattr(emulator_smoke.subprocess, "Popen", lambda *args, **kwargs: _FakeProcess())
    monkeypatch.setattr(emulator_smoke.time, "sleep", lambda *args, **kwargs: None)

    report = emulator_smoke._run_zesarux(
        {"executable": "/usr/bin/zesarux"},
        tmp_path / "output.dsk",
        tmp_path,
        "cpct_isKeyPressed(Key_Space);",
        3,
        probes={"addresses": {"g_score": 32768}, "widths": {"g_score": 2}},
        script=[{"id": "hold_left_a", "hold": "left", "key": "left", "frames": 50}],
        platform="amstrad_cpc",
    )

    assert report["command"][report["command"].index("--machine") + 1] == "CPC6128"
    assert commands[0] == "noop"
    assert "send-keys-string 60 run" in commands
    # SHIFT held down, 2 pressed and released underneath it, SHIFT let go.
    quote = commands.index("send-keys-event 133 1")
    assert commands[quote : quote + 4] == [
        "send-keys-event 133 1",
        "send-keys-event 50 1",
        "send-keys-event 50 0",
        "send-keys-event 133 0",
    ]
    assert "send-keys-string 60 program" in commands
    assert "send-keys-ascii 60 13" in commands
    # The scripted step holds the CPC's own cursor-left key, 142 in ZEsarUX's
    # util_teclas, and lets it go again.
    assert "send-keys-event 142 1" in commands
    assert "send-keys-event 142 0" in commands
    assert not any(command.startswith("set-ui-io-ports") for command in commands)
    assert report["step_readings"] == [
        {"id": "hold_left_a", "hold": "left", "read": {"g_score": 5}}
    ]
    # No display file: the CPC keeps no attribute area, so `attributes` must
    # abstain rather than be handed CPC memory to interpret as Spectrum cells.
    assert report["screen_dump"] is None
