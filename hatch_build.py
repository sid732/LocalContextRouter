"""Build hook: compile the universal lcr-ocr binary into the wheel.

Runs only for the wheel target and only where Swift is available (macOS). The
result is a platform wheel (``macosx_11_0_universal2``) carrying the on-device
OCR binary, so ``pip install`` gives users working OCR with no extra steps.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

_WHEEL_TAG = "py3-none-macosx_11_0_universal2"
_TARGET = "localcontextrouter/_bin/lcr-ocr"


class CustomBuildHook(BuildHookInterface):
    PLUGIN_NAME = "custom"

    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        if self.target_name != "wheel":
            return
        if version == "editable":
            # Editable installs (pip install -e) don't need the bundled binary;
            # skip the Swift build so dev installs work without a toolchain.
            return
        if shutil.which("swift") is None:
            # No Swift toolchain (e.g. building the sdist on a non-macOS host):
            # produce a pure wheel; OCR then relies on LCR_OCR_BIN or PATH.
            return

        root = Path(self.root)
        ocr_dir = root / "ocr"
        subprocess.run(
            ["swift", "build", "-c", "release", "--arch", "arm64", "--arch", "x86_64"],
            cwd=ocr_dir,
            check=True,
        )
        built = ocr_dir / ".build" / "apple" / "Products" / "Release" / "lcr-ocr"
        if not built.is_file():
            raise FileNotFoundError(f"universal lcr-ocr not found at {built}")

        dest = root / "src" / "localcontextrouter" / "_bin" / "lcr-ocr"
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(built, dest)
        dest.chmod(0o755)

        build_data["pure_python"] = False
        build_data["infer_tag"] = False
        build_data["tag"] = _WHEEL_TAG
        build_data["force_include"][str(dest)] = _TARGET
