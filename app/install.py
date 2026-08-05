from __future__ import annotations

import shutil
import zipfile
from collections.abc import Callable
from pathlib import Path

import httpx

from app.catalog import GameDef, find_exe_in_dir
from app.github import USER_AGENT, ReleaseAsset

ProgressCb = Callable[[str], None]


def library_game_dir(library_root: Path, game_id: str) -> Path:
    return library_root / game_id


def download_file(
    url: str,
    dest: Path,
    *,
    on_progress: ProgressCb | None = None,
) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    headers = {"User-Agent": USER_AGENT}
    with httpx.Client(timeout=None, follow_redirects=True, headers=headers) as client:
        with client.stream("GET", url) as resp:
            resp.raise_for_status()
            total = int(resp.headers.get("content-length") or 0)
            done = 0
            with dest.open("wb") as out:
                for chunk in resp.iter_bytes(chunk_size=1024 * 256):
                    out.write(chunk)
                    done += len(chunk)
                    if on_progress:
                        if total:
                            pct = int(done * 100 / total)
                            on_progress(f"Downloading… {pct}% ({_fmt_bytes(done)} / {_fmt_bytes(total)})")
                        else:
                            on_progress(f"Downloading… {_fmt_bytes(done)}")
    return dest


def _fmt_bytes(n: int) -> str:
    value = float(n)
    for unit in ("B", "KB", "MB", "GB"):
        if value < 1024 or unit == "GB":
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} {unit}"
        value /= 1024
    return f"{n} B"


def extract_zip(zip_path: Path, dest_dir: Path, *, on_progress: ProgressCb | None = None) -> Path:
    if dest_dir.exists():
        # Keep saves/config where possible: clear only extracted game payload folder contents
        # that we own under library_root — wipe and re-extract for clean updates.
        shutil.rmtree(dest_dir, ignore_errors=True)
    dest_dir.mkdir(parents=True, exist_ok=True)
    if on_progress:
        on_progress("Extracting…")
    with zipfile.ZipFile(zip_path, "r") as zf:
        # If zip has a single top-level folder, extract into dest_dir and flatten if needed
        zf.extractall(dest_dir)
    if on_progress:
        on_progress("Extracted.")
    return dest_dir


def resolve_install_root(extracted: Path) -> Path:
    """If extraction left a single subdirectory, treat that as the install root."""
    children = [p for p in extracted.iterdir() if not p.name.startswith(".")]
    if len(children) == 1 and children[0].is_dir():
        return children[0]
    return extracted


def install_from_asset(
    game: GameDef,
    asset: ReleaseAsset,
    *,
    library_root: Path,
    downloads_dir: Path,
    version_tag: str,
    on_progress: ProgressCb | None = None,
) -> tuple[Path, Path]:
    """Download + extract. Returns (install_dir, exe_path)."""
    library_root.mkdir(parents=True, exist_ok=True)
    downloads_dir.mkdir(parents=True, exist_ok=True)
    zip_path = downloads_dir / f"{game.id}_{version_tag.replace('/', '_')}_{asset.name}"
    if on_progress:
        on_progress(f"Fetching {asset.name}…")
    download_file(asset.download_url, zip_path, on_progress=on_progress)

    dest = library_game_dir(library_root, game.id)
    extract_zip(zip_path, dest, on_progress=on_progress)
    install_dir = resolve_install_root(dest)
    # If flattened single folder exists inside dest, move contents up for stable path
    if install_dir != dest:
        # Keep nested structure — many HM builds expect relative paths from their folder
        pass

    search_root = dest
    exe = find_exe_in_dir(search_root, game.preferred_exes)
    if not exe:
        raise FileNotFoundError(
            f"Installed {game.name}, but no executable was found under {search_root}."
        )
    if on_progress:
        on_progress(f"Ready: {exe.name}")
    return exe.parent, exe


def download_extra_asset(
    asset: ReleaseAsset,
    dest_dir: Path,
    *,
    on_progress: ProgressCb | None = None,
) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / asset.name
    if on_progress:
        on_progress(f"Downloading {asset.name}…")
    download_file(asset.download_url, dest, on_progress=on_progress)
    if on_progress:
        on_progress(f"Saved {dest}")
    return dest
