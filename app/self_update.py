from __future__ import annotations

import shutil
import subprocess
import sys
import zipfile
from collections.abc import Callable
from pathlib import Path

from app.github import ReleaseAsset
from app.install import download_file

ProgressCb = Callable[[str], None]


def find_exe_in_extract(root: Path) -> Path | None:
    direct = root / "HarbourMaster.exe"
    if direct.is_file():
        return direct
    for path in root.rglob("HarbourMaster.exe"):
        if path.is_file():
            return path
    return None


def apply_launcher_update(
    asset: ReleaseAsset,
    *,
    downloads_dir: Path,
    on_progress: ProgressCb | None = None,
) -> None:
    """
    Download the release asset and replace this frozen EXE, then restart.
    Must only be called when running as a built EXE (sys.frozen).
    """
    if not getattr(sys, "frozen", False):
        raise RuntimeError("Launcher self-update only works from the built HarbourMaster.exe")

    current_exe = Path(sys.executable).resolve()
    app_dir = current_exe.parent
    downloads_dir.mkdir(parents=True, exist_ok=True)

    staging = downloads_dir / "launcher_update"
    if staging.exists():
        shutil.rmtree(staging, ignore_errors=True)
    staging.mkdir(parents=True, exist_ok=True)

    name = asset.name or "update.bin"
    archive = staging / name
    if on_progress:
        on_progress("Downloading launcher update…")
    download_file(asset.download_url, archive, on_progress=on_progress)

    new_exe: Path | None = None
    if archive.suffix.lower() == ".zip":
        extract_dir = staging / "extracted"
        extract_dir.mkdir(parents=True, exist_ok=True)
        if on_progress:
            on_progress("Extracting launcher update…")
        with zipfile.ZipFile(archive, "r") as zf:
            zf.extractall(extract_dir)
        new_exe = find_exe_in_extract(extract_dir)
    elif archive.suffix.lower() == ".exe":
        new_exe = archive

    if new_exe is None or not new_exe.is_file():
        raise RuntimeError("Update package did not contain HarbourMaster.exe")

    pending = app_dir / "HarbourMaster.exe.new"
    shutil.copy2(new_exe, pending)

    bat = app_dir / "harbourmaster_apply_update.bat"
    bat.write_text(
        "\r\n".join(
            [
                "@echo off",
                "setlocal",
                f'cd /d "{app_dir}"',
                "echo Updating HarbourMaster…",
                "ping 127.0.0.1 -n 3 >nul",
                f'if exist "{pending.name}" (',
                f'  move /Y "{pending.name}" "{current_exe.name}" >nul',
                ")",
                f'start "" "{current_exe.name}"',
                'del "%~f0" >nul 2>&1',
                "",
            ]
        ),
        encoding="utf-8",
    )

    if on_progress:
        on_progress("Restarting to finish update…")

    flags = 0x00000008 | 0x00000200  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
    subprocess.Popen(  # noqa: S603
        ["cmd.exe", "/c", str(bat)],
        cwd=str(app_dir),
        creationflags=flags,
        close_fds=True,
    )
