from __future__ import annotations

import sys
from pathlib import Path

import httpx
from PIL import Image

from app.github import USER_AGENT

_pil_cache: dict[str, Image.Image] = {}


def _project_root() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return Path(__file__).resolve().parent.parent


ASSETS_DIR = _project_root() / "assets" / "games"
ICON_BASE = "https://www.harbourmasters.org/icons/games"

REMOTE_ICONS: dict[str, str] = {
    "ShipOfHarkinian.png": "ShipOfHarkinian.png",
    "2Ship2Hakinian.png": "2Ship2Hakinian.png",
    "Starship.png": "Starship.png",
    "SpaghettiKart.png": "SpaghettiKart.png",
    "Ghostship.png": "Ghostship.png",
    "Lighthouse.png": "Lighthouse.png",
    "ArchipelagoSoH.png": "ShipOfHarkinian.png",
}


def _writable_cache_dir() -> Path:
    if getattr(sys, "frozen", False):
        base = Path(sys.executable).resolve().parent / "data" / "icons"
    else:
        base = Path(__file__).resolve().parent.parent / "data" / "icons"
    base.mkdir(parents=True, exist_ok=True)
    return base


def icon_path(filename: str) -> Path:
    bundled = ASSETS_DIR / filename
    if bundled.is_file():
        return bundled
    return _writable_cache_dir() / filename


def ensure_icon(filename: str) -> Path | None:
    path = icon_path(filename)
    if path.is_file() and path.stat().st_size > 0:
        return path
    remote = REMOTE_ICONS.get(filename)
    if not remote:
        return None
    url = f"{ICON_BASE}/{remote}"
    dest = _writable_cache_dir() / filename
    try:
        with httpx.Client(timeout=20.0, follow_redirects=True, headers={"User-Agent": USER_AGENT}) as client:
            resp = client.get(url)
            resp.raise_for_status()
            dest.write_bytes(resp.content)
        return dest
    except Exception:  # noqa: BLE001
        return path if path.is_file() else None


def load_pil(filename: str, size: tuple[int, int] = (72, 72)) -> Image.Image | None:
    key = f"{filename}:{size[0]}x{size[1]}"
    cached = _pil_cache.get(key)
    if cached is not None:
        return cached
    path = ensure_icon(filename)
    if not path or not path.is_file():
        return None
    try:
        img = Image.open(path).convert("RGBA").resize(size, Image.Resampling.BILINEAR)
        _pil_cache[key] = img
        return img
    except Exception:  # noqa: BLE001
        return None


def preload_all(size: tuple[int, int] = (72, 72)) -> None:
    """Warm the PIL cache (safe to call from a worker thread)."""
    for filename in REMOTE_ICONS:
        load_pil(filename, size=size)


def ensure_all_icons() -> None:
    for filename in REMOTE_ICONS:
        ensure_icon(filename)
