# version numbers + settings.json live here.
# I mashed them into one file because they were tiny and I kept losing track.

import json
import re
import sys
from pathlib import Path

APP_NAME = "ShipYard"
APP_VERSION = "1.9.0"
# my github. used to be HM-Launcher before I renamed the repo
LAUNCHER_REPO = "RaccoonCloud/ShipYard"


def _strip_v(tag):
    # github tags are like v9.0.0, I just want the numbers
    t = (tag or "").strip()
    if t.lower().startswith("v"):
        t = t[1:]
    m = re.match(r"(\d+(?:\.\d+)*)", t)
    if m:
        return m.group(1)
    return t


def _bits(tag):
    # turn "1.9.0" into (1, 9, 0) so I can compare versions
    out = []
    for p in _strip_v(tag).split("."):
        try:
            out.append(int(p))
        except ValueError:
            out.append(0)
    return out if out else [0]


def is_newer(candidate, current):
    # true if candidate is newer than what I'm running
    if not candidate or not current:
        return False
    a = _bits(candidate)
    b = _bits(current)
    while len(a) < len(b):
        a.append(0)
    while len(b) < len(a):
        b.append(0)
    return tuple(a) > tuple(b)


def _data_root():
    # I keep data next to the exe so I can copy the whole folder
    # (Launcher test on the desktop, whatever) and it still works
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


ROOT = _data_root()
DATA_DIR = ROOT / "data"
SETTINGS_PATH = DATA_DIR / "settings.json"
INSTALLS_PATH = DATA_DIR / "installs.json"


def ensure_dirs():
    # make sure the folders exist before I try writing json into them
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "cache").mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "downloads").mkdir(parents=True, exist_ok=True)


def default_settings():
    return {
        # I use D: for games. change this in Settings if you dont have a D:
        "library_root": r"D:\ShipYard",
        "archipelago_custom_worlds": "",
        "window_geometry": "980x720",
        # auto_update only hits games I already installed with a known version
        "auto_update": True,
        "auto_update_apworld": True,
        "check_launcher_updates": True,
    }


def load_settings():
    # read settings.json, or write defaults the first time
    ensure_dirs()
    base = default_settings()
    if not SETTINGS_PATH.exists():
        save_settings(base)
        return dict(base)
    try:
        raw = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        # broken file? just fall back, dont brick the app
        return dict(base)
    if not isinstance(raw, dict):
        return dict(base)
    base.update(raw)
    return base


def save_settings(settings):
    ensure_dirs()
    SETTINGS_PATH.write_text(json.dumps(settings, indent=2), encoding="utf-8")


def load_installs():
    # where each game lives + which version I last yanked
    ensure_dirs()
    if not INSTALLS_PATH.exists():
        return {}
    try:
        raw = json.loads(INSTALLS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if isinstance(raw, dict):
        return raw
    return {}


def save_installs(installs):
    ensure_dirs()
    INSTALLS_PATH.write_text(json.dumps(installs, indent=2), encoding="utf-8")


def remember_install(installs, game_id, install_dir, exe_path, version_tag=""):
    # after install / browse I stash the paths so Launch just works next time
    installs[game_id] = {
        "install_dir": install_dir,
        "exe_path": exe_path,
        "version_tag": version_tag,
    }
    save_installs(installs)
    return installs


# old name, whatever
set_install = remember_install
