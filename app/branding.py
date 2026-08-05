from __future__ import annotations

import shutil
import sys
from pathlib import Path

from PIL import Image, ImageTk


def _bundle_root() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return Path(__file__).resolve().parent.parent


ASSETS = _bundle_root() / "assets"
LOGO_GIF = ASSETS / "hm_logo.gif"
LOGO_ICO = ASSETS / "hm_icon_v3.ico"
LOGO_PNG = ASSETS / "hm_icon_v3.png"
DISCORD_PNG = ASSETS / "discord.png"
DISCORD_URL = "https://discord.com/invite/shipofharkinian"
ANIM_SPLASH = ASSETS / "anim" / "splash"
ANIM_HEADER = ASSETS / "anim" / "header"


def logo_ico_path() -> Path | None:
    return LOGO_ICO if LOGO_ICO.is_file() else None


def window_ico_path() -> Path | None:
    """
    Windows iconbitmap() is unreliable for files inside PyInstaller _MEIPASS.
    Copy the same EXE ico next to the executable (or into data/) and use that.
    """
    src = logo_ico_path()
    if not src:
        return None
    if getattr(sys, "frozen", False):
        dest = Path(sys.executable).resolve().parent / "HarbourMaster.ico"
        try:
            # Always refresh so a rebuilt teal icon replaces an older red one
            shutil.copy2(src, dest)
            return dest
        except OSError:
            return src
    return src


def apply_window_icon(window) -> None:
    """Match the window/taskbar icon to the EXE icon (same hm_icon_v3 asset)."""
    ico = window_ico_path()
    if ico and ico.suffix.lower() == ".ico":
        try:
            window.iconbitmap(default=str(ico))
            window.iconbitmap(str(ico))
        except Exception:  # noqa: BLE001
            pass
    # Also set iconphoto from the same PNG so the title bar matches on all DPI modes
    if LOGO_PNG.is_file():
        try:
            img = Image.open(LOGO_PNG).convert("RGBA")
            photos = []
            for size in (16, 32, 48, 256):
                photos.append(ImageTk.PhotoImage(img.resize((size, size), Image.Resampling.LANCZOS)))
            window.iconphoto(True, *photos)
            window._hm_icon_photos = photos  # keep refs
        except Exception:  # noqa: BLE001
            pass


def load_prebaked_photos(folder: Path, *, max_frames: int | None = None) -> list[ImageTk.PhotoImage]:
    """Load numbered PNGs from a folder — much faster than decoding the full GIF."""
    if not folder.is_dir():
        return []
    paths = sorted(folder.glob("*.png"))
    if max_frames is not None:
        paths = paths[:max_frames]
    photos: list[ImageTk.PhotoImage] = []
    for path in paths:
        try:
            photos.append(ImageTk.PhotoImage(Image.open(path).convert("RGBA")))
        except Exception:  # noqa: BLE001
            continue
    return photos


def load_static_photo(size: tuple[int, int] = (256, 256)) -> ImageTk.PhotoImage | None:
    if not LOGO_PNG.is_file():
        return None
    img = Image.open(LOGO_PNG).convert("RGBA").resize(size, Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(img)


def load_discord_ctk_image(size: tuple[int, int] = (22, 22)):
    """Footer Discord button icon (CustomTkinter)."""
    import customtkinter as ctk

    if not DISCORD_PNG.is_file():
        return None
    pil = Image.open(DISCORD_PNG).convert("RGBA").resize(size, Image.Resampling.LANCZOS)
    return ctk.CTkImage(light_image=pil, dark_image=pil, size=size)
