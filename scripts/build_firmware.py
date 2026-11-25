#!/usr/bin/env python3
"""Build stock and 8 MHz AI-on-the-Edge v16.1.0 ESP32-CAM images."""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT / "upstream"
CODE = UPSTREAM / "code"
BUILD = CODE / ".pio" / "build" / "esp32cam"
SITE = ROOT / "site"


def run(args: list[str], cwd: Path | None = None) -> None:
    print("+", " ".join(args), flush=True)
    subprocess.run(args, cwd=cwd, check=True)


def set_xclk_8mhz() -> None:
    config = CODE / "platformio.ini"
    original = config.read_text(encoding="utf-8")
    if "-D XCLK_FREQ_MHZ=8" in original:
        return

    marker = "    -D BOARD_ESP32CAM_AITHINKER"
    if original.count(marker) != 1:
        raise RuntimeError("Could not identify the unique ESP32-CAM build flag in platformio.ini")

    modified = original.replace(
        marker,
        marker + "\n    -D XCLK_FREQ_MHZ=8",
        1,
    )
    config.write_text(modified, encoding="utf-8")


def build_variant(name: str, xclk_8mhz: bool) -> None:
    if xclk_8mhz:
        set_xclk_8mhz()

    # Force a clean application build after changing the compiler definition.
    if BUILD.exists():
        shutil.rmtree(BUILD)

    run(["pio", "run", "--environment", "esp32cam"], cwd=CODE)

    required = ["bootloader.bin", "partitions.bin", "firmware.bin"]
    missing = [filename for filename in required if not (BUILD / filename).is_file()]
    if missing:
        raise RuntimeError(f"PlatformIO did not produce required files: {missing}")

    target = SITE / "firmware" / name
    target.mkdir(parents=True, exist_ok=True)

    for filename in required:
        shutil.copy2(BUILD / filename, target / filename)

    # Merge ESP-IDF images for ESP Web Tools. A full erase is prompted by
    # the manifest before installation; this also clears stale OTA selection.
    # ESP32-CAM PlatformIO board profile is 4 MB, DIO, 40 MHz.
    run(
        [
            "python", "-m", "esptool",
            "--chip", "esp32", "merge_bin",
            "-o", str(target / "merged.bin"),
            "--flash_mode", "dio",
            "--flash_freq", "40m",
            "--flash_size", "4MB",
            "0x1000", str(target / "bootloader.bin"),
            "0x8000", str(target / "partitions.bin"),
            "0x10000", str(target / "firmware.bin"),
        ]
    )

    manifest = {
        "name": f"AI-on-the-Edge v16.1.0 - {name}",
        "version": "16.1.0-xclk8-test" if xclk_8mhz else "16.1.0-stock-20mhz",
        "new_install_prompt_erase": True,
        "builds": [
            {
                "chipFamily": "ESP32",
                "parts": [{"path": "merged.bin", "offset": 0}],
            }
        ],
    }
    (target / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    if not CODE.is_dir():
        raise RuntimeError("Upstream source checkout missing at ./upstream")

    source_file = CODE / "components" / "jomjol_controlcamera" / "ClassControllCamera.cpp"
    source = source_file.read_text(encoding="utf-8")
    if "XCLK_FREQ_MHZ" not in source or "int xclk = 20" not in source:
        raise RuntimeError("Upstream camera source no longer matches the expected v16.1.0 XCLK implementation")

    build_variant("stock", xclk_8mhz=False)
    build_variant("8mhz", xclk_8mhz=True)

    print("Both firmware variants and ESP Web Tools manifests created successfully.")


if __name__ == "__main__":
    main()
