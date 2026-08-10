from __future__ import annotations

import re

APP_NAME = "HarbourMaster"
APP_VERSION = "1.8.0"

# GitHub repo that publishes HarbourMaster / HMLauncher releases
LAUNCHER_REPO = "RaccoonCloud/HM-Launcher"


def normalize_version(tag: str) -> str:
    text = (tag or "").strip()
    if text.lower().startswith("v"):
        text = text[1:]
    # Keep primary semver-ish token (1.5.0 from v1.5.0-beta etc.)
    match = re.match(r"(\d+(?:\.\d+)*)", text)
    return match.group(1) if match else text


def version_tuple(tag: str) -> tuple[int, ...]:
    parts = normalize_version(tag).split(".")
    out: list[int] = []
    for part in parts:
        try:
            out.append(int(part))
        except ValueError:
            out.append(0)
    return tuple(out) if out else (0,)


def is_newer(candidate: str, current: str) -> bool:
    """True when candidate version is greater than current."""
    if not candidate or not current:
        return False
    a = version_tuple(candidate)
    b = version_tuple(current)
    # Pad for compare
    n = max(len(a), len(b))
    a = a + (0,) * (n - len(a))
    b = b + (0,) * (n - len(b))
    return a > b
