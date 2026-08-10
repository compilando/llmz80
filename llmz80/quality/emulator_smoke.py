"""Bounded runtime verification for generated Spectrum and CPC artifacts."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import socket
import subprocess
import time
import uuid
from pathlib import Path
from typing import Any

from PIL import Image


def discover_adapter(platform: str) -> dict[str, Any]:
    candidates = (
        [("zesarux", {"headless": True, "frames": True, "scripted_input": True}),
         ("fuse", {"headless": False, "frames": False, "scripted_input": False})]
        if platform == "spectrum"
        else [("cap32", {"headless": True, "frames": True, "scripted_input": True}),
              ("caprice32", {"headless": True, "frames": True, "scripted_input": True}),
              ("cpcec", {"headless": False, "frames": False, "scripted_input": False})]
    )
    for command, capabilities in candidates:
        executable = shutil.which(command)
        if executable:
            return {"name": command, "executable": executable, "capabilities": capabilities}
    return {"name": None, "executable": None, "capabilities": {}}


def _artifact_valid(platform: str, artifact: Path) -> tuple[bool, str]:
    if not artifact.is_file() or artifact.stat().st_size == 0:
        return False, "canonical artifact is missing or empty"
    data = artifact.read_bytes()
    if platform == "spectrum":
        if len(data) < 4:
            return False, "TAP is too small to contain a block"
        block_size = int.from_bytes(data[:2], "little")
        if block_size == 0 or block_size + 2 > len(data):
            return False, "TAP first block length is invalid"
        return True, "TAP contains a structurally valid first block"
    signatures = (b"MV - CPCEMU Disk-File", b"EXTENDED CPC DSK File")
    if not any(data.startswith(signature) for signature in signatures):
        return False, "DSK header is not a supported CPCEMU format"
    return True, "DSK has a recognised CPCEMU header"


def _source_observations(source: str) -> tuple[bool, bool]:
    draw_calls = (
        "printf", "zx_cls", "zx_pxy2saddr", "llmz80_draw_sprite8",
        "cpct_drawSprite", "cpct_drawString", "cpct_drawSolidBox", "cpct_clearScreen",
    )
    transition_tokens = (
        "in_inkey", "in_key_pressed", "cpct_isKeyPressed", "++", "--", "+=", "-=",
        "state =", "score =",
    )
    return any(token in source for token in draw_calls), any(token in source for token in transition_tokens)


def _frame_dir(output_dir: Path, platform: str) -> Path:
    path = output_dir / "smoke_frames" / f"{platform}_{uuid.uuid4().hex[:10]}"
    path.mkdir(parents=True, exist_ok=False)
    return path


def _image_observation(path: Path) -> dict[str, Any]:
    with Image.open(path) as original:
        image = original.convert("RGB")
        width, height = image.size
        # Exclude emulator overlays and most of the border. The crop still includes
        # the complete 8-bit machine viewport on the supported adapters.
        crop = image.crop((width // 20, height // 12, width * 19 // 20, height * 11 // 12))
        colours = crop.getcolors(maxcolors=crop.width * crop.height)
        if colours is None:
            unique_colours = crop.width * crop.height
            dominant_pixels = 0
        else:
            unique_colours = len(colours)
            dominant_pixels = max(count for count, _colour in colours)
        pixels = crop.width * crop.height
        non_dominant_pixels = pixels - dominant_pixels
        digest = hashlib.sha256(crop.tobytes()).hexdigest()
    return {
        "path": str(path),
        "sha256": digest,
        "width": width,
        "height": height,
        "unique_colours": unique_colours,
        "non_dominant_pixels": non_dominant_pixels,
        "dominant_fraction": round(dominant_pixels / pixels, 6) if pixels else 1.0,
        "non_blank": unique_colours > 1 and non_dominant_pixels >= 32,
    }


_SPECTRUM_ROWS = {
    "v": (0, 4), "c": (0, 3), "x": (0, 2), "z": (0, 1),
    "g": (1, 4), "f": (1, 3), "d": (1, 2), "s": (1, 1), "a": (1, 0),
    "t": (2, 4), "r": (2, 3), "e": (2, 2), "w": (2, 1), "q": (2, 0),
    "5": (3, 4), "4": (3, 3), "3": (3, 2), "2": (3, 1), "1": (3, 0),
    "6": (4, 4), "7": (4, 3), "8": (4, 2), "9": (4, 1), "0": (4, 0),
    "y": (5, 4), "u": (5, 3), "i": (5, 2), "o": (5, 1), "p": (5, 0),
    "h": (6, 4), "j": (6, 3), "k": (6, 2), "l": (6, 1), "enter": (6, 0),
    "b": (7, 4), "n": (7, 3), "m": (7, 2), "space": (7, 0),
}


def _spectrum_input(source: str) -> tuple[str, str, str]:
    found = {match.lower() for match in re.findall(r"IN_KEY_SCANCODE_([A-Za-z0-9]+)", source)}
    # Prefer controls whose effect normally persists long enough to capture.
    for key in ("p", "d", "l", "o", "a", "q", "w", "s", "space"):
        if key in found and key in _SPECTRUM_ROWS:
            row, bit = _SPECTRUM_ROWS[key]
            values = [0x1F] * 8
            values[row] &= ~(1 << bit)
            pressed = "".join(f"{value:02x}" for value in values) + "00"
            released = "1f" * 8 + "00"
            return key, pressed, released
    return "joystick_right", "1f" * 8 + "01", "1f" * 8 + "00"


def _free_local_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


def _connect_zrcp(port: int, deadline: float) -> socket.socket:
    last_error: OSError | None = None
    while time.monotonic() < deadline:
        try:
            connection = socket.create_connection(("127.0.0.1", port), timeout=0.3)
            connection.settimeout(0.2)
            return connection
        except OSError as exc:
            last_error = exc
            time.sleep(0.05)
    raise OSError(f"ZEsarUX remote protocol did not start: {last_error}")


def _zrcp_command(connection: socket.socket, command: str) -> None:
    connection.sendall((command + "\n").encode("utf-8"))
    time.sleep(0.12)
    try:
        while connection.recv(65536):
            pass
    except (TimeoutError, socket.timeout):
        pass


def _wait_for_file(path: Path, timeout: float = 1.5) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if path.is_file() and path.stat().st_size:
            return True
        time.sleep(0.05)
    return False


def _run_zesarux(
    adapter: dict[str, Any], artifact: Path, output_dir: Path, source: str, seconds: int,
) -> dict[str, Any]:
    capture_dir = _frame_dir(output_dir, "spectrum")
    raw_frames = capture_dir / "frames.raw"
    before = capture_dir / "before.bmp"
    after = capture_dir / "after.bmp"
    port = _free_local_port()
    run_seconds = max(6, seconds)
    command = [
        adapter["executable"], "--noconfigfile", "--machine", "48k",
        "--vo", "null", "--ao", "null", "--vofile", str(raw_frames),
        "--vofilefps", "5", "--fastautoload", "--quickexit",
        "--enable-remoteprotocol", "--remoteprotocol-port", str(port),
        "--exit-after", str(run_seconds), str(artifact),
    ]
    process = subprocess.Popen(
        command, cwd=output_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    input_name, pressed, released = _spectrum_input(source)
    remote_error: str | None = None
    try:
        connection = _connect_zrcp(port, time.monotonic() + 2.5)
        with connection:
            time.sleep(1.4)
            _zrcp_command(connection, f'save-screen "{before}"')
            _wait_for_file(before)
            _zrcp_command(connection, f"set-ui-io-ports {pressed}")
            time.sleep(0.45)
            _zrcp_command(connection, f'save-screen "{after}"')
            _wait_for_file(after)
            _zrcp_command(connection, f"set-ui-io-ports {released}")
    except OSError as exc:
        remote_error = str(exc)
    try:
        stdout, stderr = process.communicate(timeout=run_seconds + 5)
    except subprocess.TimeoutExpired:
        process.terminate()
        stdout, stderr = process.communicate(timeout=3)
        remote_error = remote_error or "ZEsarUX exceeded its bounded runtime"

    observations = [_image_observation(path) for path in (before, after) if path.is_file()]
    raw = raw_frames.read_bytes() if raw_frames.exists() else b""
    chunk_size = max(1, len(raw) // 6)
    raw_chunks = [
        hashlib.sha256(raw[index:index + chunk_size]).hexdigest()
        for index in range(0, len(raw), chunk_size)
    ] if raw else []
    raw_frame_change = len(set(raw_chunks)) > 1
    if len(observations) >= 2:
        screenshot_change = observations[0]["sha256"] != observations[1]["sha256"]
        visual_change = screenshot_change or raw_frame_change
        non_blank = any(item["non_blank"] for item in observations)
    else:
        screenshot_change = False
        visual_change = raw_frame_change
        non_blank = len(set(raw[::max(1, len(raw) // 4096)])) > 1 if raw else False
    result = {
        "command": command,
        "return_code": process.returncode,
        "boot": process.returncode == 0 and bool(raw or observations),
        "program_loaded": bool(raw or observations),
        "non_blank_output": non_blank,
        "visual_change": visual_change,
        "screenshot_change": screenshot_change,
        "raw_frame_change": raw_frame_change,
        "scripted_input": input_name,
        "scripted_input_sent": remote_error is None,
        "input_transition": remote_error is None and visual_change,
        "frames": observations,
        "frame_bytes": len(raw),
        "capture_dir": str(capture_dir),
        "stdout_tail": stdout[-1000:],
        "stderr_tail": stderr[-1000:],
    }
    if remote_error:
        result["remote_error"] = remote_error
    return result


def runtime_rejection_diagnostics(report: dict[str, Any]) -> list[str]:
    """Translate emulator evidence into concise, repair-oriented diagnostics."""
    diagnostics = ["RUNTIME QUALITY REJECTION: the binary compiled but failed emulator QA."]
    if report.get("emulator_error"):
        diagnostics.append(f"Emulator error: {report['emulator_error']}")
    for field in (
        "runtime_verified", "boot", "program_loaded", "non_blank_output",
        "visual_change", "scripted_input_sent", "input_transition",
    ):
        diagnostics.append(f"{field}: {bool(report.get(field, False))}")
    if report.get("scripted_input"):
        diagnostics.append(f"Scripted input: {report['scripted_input']}")
    if report.get("program_loaded") and report.get("non_blank_output") and not report.get("visual_change"):
        diagnostics.append(
            "The program is visible but remains visually static; ensure animation or the detected control "
            "changes pixels within a few frames and keep 50 Hz frame pacing."
        )
    elif not report.get("program_loaded"):
        diagnostics.append("Ensure the generated artifact autostarts the program rather than remaining in BASIC.")
    elif not report.get("non_blank_output"):
        diagnostics.append("Draw visible non-background pixels immediately after startup.")
    return diagnostics


_CPC_CURSOR_KEYS = {
    "Key_CursorDown": 117,
    "Key_CursorLeft": 118,
    "Key_CursorRight": 119,
    "Key_CursorUp": 120,
}


def _cpc_input(source: str) -> tuple[str, str]:
    # A jump changes scanlines immediately. Cursor movement often needs four
    # pixels before Mode 1 changes its byte address, so repeat cursor taps.
    space_action_evidence = re.search(
        r"\b(?:jump|grounded|velocity_y|vy|STATE_TITLE|ST_TITLE|title_screen)\b",
        source,
        re.IGNORECASE,
    )
    if "Key_Space" in source and space_action_evidence:
        return "Key_Space", " "
    for token in ("Key_CursorRight", "Key_CursorLeft", "Key_CursorUp", "Key_CursorDown"):
        if token in source:
            # Caprice32's autocmd encoding is BEL followed by the CPC_KEYS enum value.
            return token, ("\a" + chr(_CPC_CURSOR_KEYS[token])) * 5
    letters = re.findall(r"\bKey_([A-Z])\b", source)
    if letters:
        return f"Key_{letters[0]}", letters[0].lower()
    if "Key_Space" in source:
        return "Key_Space", " "
    return "Key_Space_fallback", " "


def _run_caprice32(
    adapter: dict[str, Any], artifact: Path, output_dir: Path, source: str, seconds: int,
) -> dict[str, Any]:
    capture_dir = _frame_dir(output_dir, "amstrad_cpc")
    input_name, input_event = _cpc_input(source)
    delay_frames = max(50, min(150, max(1, seconds) * 25))
    command = [
        adapter["executable"],
        "-O", f"file.sdump_dir={capture_dir}/",
        "-O", "sound.enabled=0",
        "-O", "video.scr_scale=1",
        "-O", "video.scr_fps=0",
        "-O", f"system.boot_time={delay_frames}",
        "-a", "CAP32_SCRNSHOT",
        "-a", 'run"program.bin"',
        "-a", "CAP32_DELAY",
        "-a", "CAP32_DELAY",
        "-a", "CAP32_SCRNSHOT",
        "-a", input_event,
        # Caprice32 names screenshots with one-second resolution. Without a
        # delay the post-input capture can overwrite the application capture.
        "-a", "CAP32_DELAY",
        "-a", "CAP32_SCRNSHOT",
        "-a", "CAP32_EXIT",
        str(artifact),
    ]
    environment = os.environ.copy()
    environment["SDL_VIDEODRIVER"] = "dummy"
    # Caprice32 advances at emulated 50 Hz and virtual-key events are serialized.
    # Keep a hard bound, but leave enough margin for AMSDOS loading on slow hosts.
    timeout = max(30, seconds + 25)
    completed = subprocess.run(
        command, cwd=output_dir, env=environment, capture_output=True, text=True,
        timeout=timeout, check=False,
    )
    screenshots = sorted(capture_dir.glob("screenshot_*.png"), key=lambda path: path.stat().st_mtime_ns)
    observations = [_image_observation(path) for path in screenshots]
    primary_observation_count = len(observations)
    boot_frame = observations[0] if len(observations) >= 1 else None
    app_frame = observations[1] if len(observations) >= 2 else None
    input_frame = observations[2] if len(observations) >= 3 else None
    program_loaded = bool(
        boot_frame and app_frame and boot_frame["sha256"] != app_frame["sha256"]
    )
    visual_change = bool(
        app_frame and input_frame and app_frame["sha256"] != input_frame["sha256"]
    )
    fallback_command = None
    fallback_completed = None
    fallback_observations: list[dict[str, Any]] = []
    if app_frame and not visual_change:
        # A periodic animation can return to exactly the same pixels during a
        # CAP32_DELAY (for example, a complete jump). Capture the same startup
        # timeline again, this time immediately after input and in a separate
        # directory so Caprice32's second-resolution filenames cannot collide.
        fallback_dir = _frame_dir(output_dir, "amstrad_cpc_input")
        fallback_command = [
            adapter["executable"],
            "-O", f"file.sdump_dir={fallback_dir}/",
            "-O", "sound.enabled=0",
            "-O", "video.scr_scale=1",
            "-O", "video.scr_fps=0",
            "-O", f"system.boot_time={delay_frames}",
            "-a", 'run"program.bin"',
            "-a", "CAP32_DELAY",
            "-a", "CAP32_DELAY",
            "-a", input_event,
            "-a", "CAP32_SCRNSHOT",
            "-a", "CAP32_EXIT",
            str(artifact),
        ]
        fallback_completed = subprocess.run(
            fallback_command, cwd=output_dir, env=environment, capture_output=True, text=True,
            timeout=timeout, check=False,
        )
        fallback_screenshots = sorted(
            fallback_dir.glob("screenshot_*.png"), key=lambda path: path.stat().st_mtime_ns
        )
        fallback_observations = [_image_observation(path) for path in fallback_screenshots]
        if fallback_observations:
            input_frame = fallback_observations[-1]
            visual_change = app_frame["sha256"] != input_frame["sha256"]
            observations.extend(fallback_observations)
    return {
        "command": command,
        "fallback_command": fallback_command,
        "return_code": completed.returncode,
        "boot": completed.returncode == 0 and primary_observation_count >= 3,
        "program_loaded": program_loaded,
        "non_blank_output": bool(app_frame and app_frame["non_blank"]),
        "visual_change": visual_change,
        "scripted_input": input_name,
        "scripted_input_sent": primary_observation_count >= 3 or bool(fallback_observations),
        "input_transition": visual_change,
        "frames": observations,
        "capture_dir": str(capture_dir),
        "stdout_tail": completed.stdout[-1000:],
        "stderr_tail": (
            completed.stderr
            + (fallback_completed.stderr if fallback_completed is not None else "")
        )[-1000:],
    }


def smoke_test(output_dir: Path, platform: str, full: bool = False, seconds: int = 3) -> dict[str, Any]:
    output_dir = output_dir.resolve()
    artifact = output_dir / ("output.tap" if platform == "spectrum" else "output.dsk")
    source_path = output_dir / "main.c"
    source = source_path.read_text(encoding="utf-8", errors="ignore") if source_path.exists() else ""
    artifact_ok, artifact_evidence = _artifact_valid(platform, artifact)
    source_draws, source_transitions = _source_observations(source)
    adapter = discover_adapter(platform)
    report: dict[str, Any] = {
        "schema_version": 2,
        "platform": platform,
        "mode": "portable_static",
        "requested_full": full,
        "runtime_verified": False,
        "adapter": adapter,
        "boot": False,
        "program_loaded": False,
        "non_blank_output": False,
        "visual_change": False,
        "input_transition": False,
        "static_pass": bool(artifact_ok and source_draws),
        "evidence": [artifact_evidence, "source draw/update observations only"],
        "source_transition_observation": source_transitions,
        "transition_required": source_transitions,
    }
    supported_full = (
        (platform == "spectrum" and adapter["name"] == "zesarux")
        or (platform == "amstrad_cpc" and adapter["name"] in {"cap32", "caprice32"})
    )
    if full and supported_full and artifact_ok:
        try:
            if platform == "spectrum":
                report.update(_run_zesarux(adapter, artifact, output_dir, source, seconds))
                report["evidence"].append("bounded ZEsarUX framebuffer capture and ZRCP input")
            else:
                report.update(_run_caprice32(adapter, artifact, output_dir, source, seconds))
                report["evidence"].append("bounded Caprice32 internal screenshots and virtual input")
            report["mode"] = "emulator_headless"
            report["runtime_verified"] = True
        except (OSError, subprocess.SubprocessError, ValueError) as exc:
            report["emulator_error"] = str(exc)
    elif full:
        report["emulator_error"] = "no supported full-runtime adapter is installed"
    transition_ok = report["visual_change"] if report["transition_required"] else True
    report["quality_pass"] = bool(
        report["runtime_verified"]
        and report["boot"]
        and report["program_loaded"]
        and report["non_blank_output"]
        and transition_ok
    )
    return report


def write_smoke_report(report: dict[str, Any], path: Path) -> None:
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
