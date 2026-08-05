from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def _data_root() -> Path:
    """Persist launcher data next to the EXE when frozen; else under the project."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


ROOT = _data_root()
DATA_DIR = ROOT / "data"
SETTINGS_PATH = DATA_DIR / "settings.json"
INSTALLS_PATH = DATA_DIR / "installs.json"


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "cache").mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "downloads").mkdir(parents=True, exist_ok=True)


def default_settings() -> dict[str, Any]:
    return {
        "library_root": r"D:\HarbourMaster",
        "archipelago_custom_worlds": "",
        "window_geometry": "980x720",
        # When True, installed games download the newest stable GitHub release on launch
        "auto_update": True,
        "auto_update_apworld": True,
    }


def load_settings() -> dict[str, Any]:
    ensure_dirs()
    base = default_settings()
    if not SETTINGS_PATH.exists():
        save_settings(base)
        return dict(base)
    try:
        raw = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return dict(base)
    if not isinstance(raw, dict):
        return dict(base)
    base.update(raw)
    return base


def save_settings(settings: dict[str, Any]) -> None:
    ensure_dirs()
    SETTINGS_PATH.write_text(json.dumps(settings, indent=2), encoding="utf-8")


def load_installs() -> dict[str, dict[str, Any]]:
    ensure_dirs()
    if not INSTALLS_PATH.exists():
        return {}
    try:
        raw = json.loads(INSTALLS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return raw if isinstance(raw, dict) else {}


def save_installs(installs: dict[str, dict[str, Any]]) -> None:
    ensure_dirs()
    INSTALLS_PATH.write_text(json.dumps(installs, indent=2), encoding="utf-8")


def set_install(
    installs: dict[str, dict[str, Any]],
    game_id: str,
    *,
    install_dir: str,
    exe_path: str,
    version_tag: str = "",
) -> dict[str, dict[str, Any]]:
    installs[game_id] = {
        "install_dir": install_dir,
        "exe_path": exe_path,
        "version_tag": version_tag,
    }
    save_installs(installs)
    return installs
