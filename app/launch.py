from __future__ import annotations

import os
import subprocess
from pathlib import Path


def launch_exe(exe: Path) -> subprocess.Popen:
    if not exe.exists():
        raise FileNotFoundError(f"Executable not found: {exe}")
    return subprocess.Popen(  # noqa: S603
        [str(exe)],
        cwd=str(exe.parent),
        shell=False,
    )


def open_folder(path: Path) -> None:
    path = path if path.is_dir() else path.parent
    if not path.exists():
        raise FileNotFoundError(f"Folder not found: {path}")
    os.startfile(str(path))  # noqa: S606
