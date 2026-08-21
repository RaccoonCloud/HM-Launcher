# the port list + helpers to find exes on disk.
# this is the bit I edit when HM drops a new project, REMEMBER TO EDIT AND RUN TOOL PLEASE

from pathlib import Path


class GameDef:
    # one entry in the list. nothing fancy, just the stuff I need per game.
    def __init__(
        self,
        id,
        name,
        blurb,
        repo,
        preferred_exes,
        win_asset_keywords,
        icon_file="",
        extra_assets=(),
        hint_paths=(),
    ):
        self.id = id
        self.name = name
        self.blurb = blurb
        self.repo = repo
        self.preferred_exes = preferred_exes
        self.win_asset_keywords = win_asset_keywords
        self.icon_file = icon_file
        self.extra_assets = extra_assets
        self.hint_paths = hint_paths


# list of ports. if they ship another one, putt it in here.
# hint_paths are folders I already had on this PC so first run can just
# link them instead of downloading the whole project from the internet (git) again.
GAMES = (
    GameDef(
        "soh",
        "Ship of Harkinian",
        "Ocarina of Time PC port",
        "HarbourMasters/Shipwright",
        ("soh.exe",),
        ("win64", "windows"),
        icon_file="ShipOfHarkinian.png",
        hint_paths=(
            r"D:\Ship of Harkinian\SOH",
            r"D:\Ship of Harkinian",
            r"D:\SOH",
        ),
    ),
    GameDef(
        "2ship",
        "2Ship2Harkinian",
        "Majora's Mask PC port",
        "HarbourMasters/2ship2harkinian",
        ("2ship.exe", "2s2h.exe"),
        ("win64", "windows"),
        icon_file="2Ship2Hakinian.png",
        hint_paths=(
            r"D:\Ship of Harkinian\2SHIP",
            r"D:\2SHIP",
        ),
    ),
    GameDef(
        "starship",
        "Starship",
        "Star Fox 64 PC port",
        "HarbourMasters/Starship",
        ("starship.exe",),
        ("windows", "win64"),
        icon_file="Starship.png",
        hint_paths=(r"D:\Starship",),
    ),
    GameDef(
        "spaghettikart",
        "SpaghettiKart",
        "Mario Kart 64 PC port",
        "HarbourMasters/SpaghettiKart",
        ("Spaghettify.exe", "spaghettify.exe"),
        ("win64", "windows", "win"),
        icon_file="SpaghettiKart.png",
        hint_paths=(
            r"D:\SpaghettiKart",
            r"C:\Users\Cloud02\Desktop\SpagettiKart 64",
        ),
    ),
    GameDef(
        "ghostship",
        "Ghostship",
        "Super Mario 64 PC port",
        "HarbourMasters/Ghostship",
        ("ghostship.exe", "Ghostship.exe", "maryceleste.exe"),
        ("win64", "windows"),
        icon_file="Ghostship.png",
        hint_paths=(
            r"D:\Ghostship",
            r"C:\Users\Cloud02\Desktop\GHOSTSHIP",
        ),
    ),
    GameDef(
        "lighthouse",
        "Lighthouse",
        "Banjo-Kazooie PC port",
        "HarbourMasters/Lighthouse",
        ("lighthouse.exe", "Lighthouse.exe"),
        ("win64", "windows"),
        icon_file="Lighthouse.png",
        hint_paths=(
            r"D:\Lighthouse",
            r"C:\Users\Cloud02\Desktop\BanjoKazooieMods",
        ),
    ),
    GameDef(
        "archipelago_soh",
        "Archipelago SoH",
        "Ship of Harkinian + Archipelago (separate from vanilla SoH)",
        "HarbourMasters/Archipelago-SoH",
        ("soh.exe",),
        ("windows", "win64"),
        icon_file="ArchipelagoSoH.png",
        extra_assets=("oot_soh.apworld",),
        hint_paths=(r"D:\Archipelago SoH", r"D:\SoH Archipelago"),
    ),
)


def game_by_id(game_id):
    for g in GAMES:
        if g.id == game_id:
            return g
    return None


def zip_score(name, keywords):
    # I use the release assets and score which zip looks like the windows build.
    # skip linux/mac/switch junk so I dont grab the wrong one by accident as i havve no clue how to do a build for these yet.
    low = name.lower()
    if not low.endswith(".zip"):
        return None
    for junk in ("linux", "mac", "switch", "android", "ios"):
        if junk in low:
            return None
    i = 0
    for kw in keywords:
        if kw in low:
            return 100 - i
        i += 1
    if "win" in low:
        return 1
    return None


def hunt_exe(root, preferred):
    # look for soh.exe etc. I check the top folder first, then dig around folders and files.
    root = Path(root)
    if not root.exists():
        return None
    for name in preferred:
        p = root / name
        if p.is_file():
            return p
    for name in preferred:
        hits = sorted(root.rglob(name))
        if hits:
            return hits[0]
    # last resort, use the first exe that doesnt look like an installer then should work for most cases i hope
    skip = ("uninstall", "crash", "updater", "vc_redist", "setup")
    found = []
    for p in root.rglob("*.exe"):
        n = p.name.lower()
        bad = False
        for s in skip:
            if s in n:
                bad = True
                break
        if not bad:
            found.append(p)
    if not found:
        return None
    # prefer the shallowest one so I dont pick some random tool buried deep in the folder
    found.sort(key=lambda p: (len(p.relative_to(root).parts), p.name.lower()))
    return found[0]


def peek_old_folder(game):
    # if I already had this port installed somewhere, just point at it and should be fine
    for hint in game.hint_paths:
        exe = hunt_exe(hint, game.preferred_exes)
        if exe:
            return exe.parent
    return None


# keep the old names around so I dont break myself and cause the lag again
find_exe_in_dir = hunt_exe
discover_hint_install = peek_old_folder
score_windows_asset = zip_score
