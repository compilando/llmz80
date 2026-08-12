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
