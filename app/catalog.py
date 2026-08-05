from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class GameDef:
    id: str
    name: str
    blurb: str
    repo: str
    preferred_exes: tuple[str, ...]
    # Ordered patterns; first match wins when scoring assets
    win_asset_keywords: tuple[str, ...]
    # Icon filename under assets/games/ (from harbourmasters.org)
    icon_file: str = ""
    # Extra release assets to offer (e.g. apworld)
    extra_assets: tuple[str, ...] = ()
    # Suggested existing install paths to auto-detect
    hint_paths: tuple[str, ...] = ()


GAMES: tuple[GameDef, ...] = (
    GameDef(
        id="soh",
        name="Ship of Harkinian",
        blurb="Ocarina of Time PC port",
        repo="HarbourMasters/Shipwright",
        preferred_exes=("soh.exe",),
        win_asset_keywords=("win64", "windows"),
        icon_file="ShipOfHarkinian.png",
        hint_paths=(
            r"D:\Ship of Harkinian\SOH",
            r"D:\Ship of Harkinian",
            r"D:\SOH",
        ),
    ),
    GameDef(
        id="2ship",
        name="2Ship2Harkinian",
        blurb="Majora's Mask PC port",
        repo="HarbourMasters/2ship2harkinian",
        preferred_exes=("2ship.exe", "2s2h.exe"),
        win_asset_keywords=("win64", "windows"),
        icon_file="2Ship2Hakinian.png",
        hint_paths=(
            r"D:\Ship of Harkinian\2SHIP",
            r"D:\2SHIP",
        ),
    ),
    GameDef(
        id="starship",
        name="Starship",
        blurb="Star Fox 64 PC port",
        repo="HarbourMasters/Starship",
        preferred_exes=("starship.exe",),
        win_asset_keywords=("windows", "win64"),
        icon_file="Starship.png",
        hint_paths=(r"D:\Starship",),
    ),
    GameDef(
        id="spaghettikart",
        name="SpaghettiKart",
        blurb="Mario Kart 64 PC port",
        repo="HarbourMasters/SpaghettiKart",
        preferred_exes=("Spaghettify.exe", "spaghettify.exe"),
        win_asset_keywords=("win64", "windows", "win"),
        icon_file="SpaghettiKart.png",
        hint_paths=(
            r"D:\SpaghettiKart",
            r"C:\Users\Cloud02\Desktop\SpagettiKart 64",
        ),
    ),
    GameDef(
        id="ghostship",
        name="Ghostship",
        blurb="Super Mario 64 PC port",
        repo="HarbourMasters/Ghostship",
        preferred_exes=("ghostship.exe", "Ghostship.exe", "maryceleste.exe"),
        win_asset_keywords=("win64", "windows"),
        icon_file="Ghostship.png",
        hint_paths=(
            r"D:\Ghostship",
            r"C:\Users\Cloud02\Desktop\GHOSTSHIP",
        ),
    ),
    GameDef(
        id="lighthouse",
        name="Lighthouse",
        blurb="Banjo-Kazooie PC port",
        repo="HarbourMasters/Lighthouse",
        preferred_exes=("lighthouse.exe", "Lighthouse.exe"),
        win_asset_keywords=("win64", "windows"),
        icon_file="Lighthouse.png",
        hint_paths=(
            r"D:\Lighthouse",
            r"C:\Users\Cloud02\Desktop\BanjoKazooieMods",
        ),
    ),
    GameDef(
        id="archipelago_soh",
        name="Archipelago SoH",
        blurb="Ship of Harkinian + Archipelago (separate from vanilla SoH)",
        repo="HarbourMasters/Archipelago-SoH",
        preferred_exes=("soh.exe",),
        win_asset_keywords=("windows", "win64"),
        icon_file="ArchipelagoSoH.png",
        extra_assets=("oot_soh.apworld",),
        hint_paths=(r"D:\Archipelago SoH", r"D:\SoH Archipelago"),
    ),
)


def game_by_id(game_id: str) -> GameDef | None:
    for game in GAMES:
        if game.id == game_id:
            return game
    return None


def score_windows_asset(name: str, keywords: tuple[str, ...]) -> int | None:
    """Return priority score for a zip asset, or None if not a Windows build."""
    lower = name.lower()
    if not lower.endswith(".zip"):
        return None
    # Skip non-desktop platforms
    if any(x in lower for x in ("linux", "mac", "switch", "android", "ios")):
        return None
    for i, kw in enumerate(keywords):
        if kw in lower:
            # Prefer more specific keywords (earlier in list)
            return 100 - i
    # Generic zip with "win" somewhere
    if "win" in lower:
        return 1
    return None


def find_exe_in_dir(root: Path, preferred: tuple[str, ...]) -> Path | None:
    if not root.exists():
        return None
    for name in preferred:
        direct = root / name
        if direct.is_file():
            return direct
    # Prefer shallow preferred matches
    for name in preferred:
        matches = sorted(root.rglob(name))
        if matches:
            return matches[0]
    # Fallback: any .exe that isn't an uninstaller/helper
    skip = ("uninstall", "crash", "updater", "vc_redist", "setup")
    candidates: list[Path] = []
    for path in root.rglob("*.exe"):
        low = path.name.lower()
        if any(s in low for s in skip):
            continue
        candidates.append(path)
    if not candidates:
        return None
    # Prefer exe at shallowest depth
    candidates.sort(key=lambda p: (len(p.relative_to(root).parts), p.name.lower()))
    return candidates[0]


def discover_hint_install(game: GameDef) -> Path | None:
    for hint in game.hint_paths:
        path = Path(hint)
        exe = find_exe_in_dir(path, game.preferred_exes)
        if exe:
            return exe.parent
    return None
