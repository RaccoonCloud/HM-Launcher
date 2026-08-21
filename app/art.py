# logos, splash frames, game icons. all the picture stuff.
# I bake splash/header frames as pngs because decoding the full gif every time was laggy.

import shutil
import sys
from pathlib import Path

import httpx
from PIL import Image, ImageTk

from app.gh import USER_AGENT

_pil_cache = {}


def _bundle_root():
    # pyinstaller dumps assets into a temp folder when frozen
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent


ASSETS = _bundle_root() / "assets"
LOGO_GIF = ASSETS / "hm_logo.gif"
LOGO_ICO = ASSETS / "hm_icon_v3.ico"
LOGO_PNG = ASSETS / "hm_icon_v3.png"
DISCORD_PNG = ASSETS / "discord.png"
DISCORD_URL = "https://discord.com/invite/shipofharkinian"
ANIM_SPLASH = ASSETS / "anim" / "splash"
ANIM_HEADER = ASSETS / "anim" / "header"
GAMES_DIR = ASSETS / "games"
ICON_BASE = "https://www.harbourmasters.org/icons/games"

# archipelago just reuses the soh art — I didnt bother making a separate icon
REMOTE_ICONS = {
    "ShipOfHarkinian.png": "ShipOfHarkinian.png",
    "2Ship2Hakinian.png": "2Ship2Hakinian.png",
    "Starship.png": "Starship.png",
    "SpaghettiKart.png": "SpaghettiKart.png",
    "Ghostship.png": "Ghostship.png",
    "Lighthouse.png": "Lighthouse.png",
    "ArchipelagoSoH.png": "ShipOfHarkinian.png",
}


def logo_ico_path():
    if LOGO_ICO.is_file():
        return LOGO_ICO
    return None


def window_ico_path():
    # windows wont use the ico from inside the packed exe, copy it out
    src = logo_ico_path()
    if not src:
        return None
    if getattr(sys, "frozen", False):
        dest = Path(sys.executable).resolve().parent / "ShipYard.ico"
        try:
            shutil.copy2(src, dest)
            return dest
        except OSError:
            return src
    return src


def apply_window_icon(window):
    # taskbar + title bar. I set both ico and png because windows is picky
    ico = window_ico_path()
    if ico and ico.suffix.lower() == ".ico":
        try:
            window.iconbitmap(default=str(ico))
            window.iconbitmap(str(ico))
        except Exception:
            pass
    if LOGO_PNG.is_file():
        try:
            img = Image.open(LOGO_PNG).convert("RGBA")
            photos = []
            for sz in (16, 32, 48, 256):
                photos.append(ImageTk.PhotoImage(img.resize((sz, sz), Image.Resampling.LANCZOS)))
            window.iconphoto(True, *photos)
            window._hm_icon_photos = photos
        except Exception:
            pass


def load_prebaked_photos(folder, max_frames=None):
    # numbered pngs for the splash / header loop
    folder = Path(folder)
    if not folder.is_dir():
        return []
    paths = sorted(folder.glob("*.png"))
    if max_frames is not None:
        paths = paths[:max_frames]
    out = []
    for p in paths:
        try:
            out.append(ImageTk.PhotoImage(Image.open(p).convert("RGBA")))
        except Exception:
            pass
    return out


def load_static_photo(size=(256, 256)):
    if not LOGO_PNG.is_file():
        return None
    img = Image.open(LOGO_PNG).convert("RGBA").resize(size, Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(img)


def load_discord_ctk_image(size=(22, 22)):
    # little discord button in the footer
    import customtkinter as ctk

    if not DISCORD_PNG.is_file():
        return None
    pil = Image.open(DISCORD_PNG).convert("RGBA").resize(size, Image.Resampling.LANCZOS)
    return ctk.CTkImage(light_image=pil, dark_image=pil, size=size)


def _icon_cache_dir():
    # if an icon is missing from the build I download it into data/icons
    if getattr(sys, "frozen", False):
        base = Path(sys.executable).resolve().parent / "data" / "icons"
    else:
        base = Path(__file__).resolve().parent.parent / "data" / "icons"
    base.mkdir(parents=True, exist_ok=True)
    return base


def _icon_path(filename):
    bundled = GAMES_DIR / filename
    if bundled.is_file():
        return bundled
    return _icon_cache_dir() / filename


def ensure_icon(filename):
    path = _icon_path(filename)
    if path.is_file() and path.stat().st_size > 0:
        return path
    remote = REMOTE_ICONS.get(filename)
    if not remote:
        return None
    dest = _icon_cache_dir() / filename
    try:
        with httpx.Client(timeout=20.0, follow_redirects=True, headers={"User-Agent": USER_AGENT}) as c:
            r = c.get(ICON_BASE + "/" + remote)
            r.raise_for_status()
            dest.write_bytes(r.content)
        return dest
    except Exception:
        if path.is_file():
            return path
        return None


def load_pil(filename, size=(72, 72)):
    # resize once and keep it, the cards ask for these a lot
    key = "%s:%sx%s" % (filename, size[0], size[1])
    if key in _pil_cache:
        return _pil_cache[key]
    path = ensure_icon(filename)
    if not path or not path.is_file():
        return None
    try:
        img = Image.open(path).convert("RGBA").resize(size, Image.Resampling.BILINEAR)
        _pil_cache[key] = img
        return img
    except Exception:
        return None


def warm_icons(size=(72, 72)):
    # I call this during splash so the main window doesnt hitch loading icons
    for fn in REMOTE_ICONS:
        load_pil(fn, size)


preload_all = warm_icons
