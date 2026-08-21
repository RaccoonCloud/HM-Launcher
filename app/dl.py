# download zips, unpack them, run games. the boring bit.
# I stream downloads so big HM builds dont sit in memory forever.

import os
import shutil
import subprocess
import zipfile
from pathlib import Path

import httpx

from app.games import hunt_exe
from app.gh import USER_AGENT


def library_game_dir(library_root, game_id):
    # each game gets its own folder under the library root I picked
    return Path(library_root) / game_id


def _fmt_bytes(n):
    # just so the status bar says "45 MB" instead of a huge number
    n = float(n)
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            if unit == "B":
                return str(int(n)) + " B"
            return "%.1f %s" % (n, unit)
        n /= 1024
    return str(n) + " B"


def yank_file(url, dest, on_progress=None):
    # pull a file off the internet. on_progress updates the footer while I wait.
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with httpx.Client(timeout=None, follow_redirects=True, headers={"User-Agent": USER_AGENT}) as c:
        with c.stream("GET", url) as resp:
            resp.raise_for_status()
            total = int(resp.headers.get("content-length") or 0)
            done = 0
            f = dest.open("wb")
            try:
                for chunk in resp.iter_bytes(chunk_size=256 * 1024):
                    f.write(chunk)
                    done += len(chunk)
                    if on_progress:
                        if total:
                            pct = int(done * 100 / total)
                            on_progress("Downloading… %s%% (%s / %s)" % (pct, _fmt_bytes(done), _fmt_bytes(total)))
                        else:
                            on_progress("Downloading… " + _fmt_bytes(done))
            finally:
                f.close()
    return dest


def unzip_into(zip_path, dest_dir, on_progress=None):
    # wipe the old folder then dump the zip in. clean updates, less half-broken installs.
    dest_dir = Path(dest_dir)
    if dest_dir.exists():
        shutil.rmtree(dest_dir, ignore_errors=True)
    dest_dir.mkdir(parents=True, exist_ok=True)
    if on_progress:
        on_progress("Extracting…")
    zf = zipfile.ZipFile(zip_path, "r")
    try:
        zf.extractall(dest_dir)
    finally:
        zf.close()
    if on_progress:
        on_progress("Extracted.")
    return dest_dir


def yank_and_install(game, asset, library_root, downloads_dir, version_tag, on_progress=None):
    # full install path: download zip -> extract under library -> find the exe
    library_root = Path(library_root)
    downloads_dir = Path(downloads_dir)
    library_root.mkdir(parents=True, exist_ok=True)
    downloads_dir.mkdir(parents=True, exist_ok=True)

    safe_tag = version_tag.replace("/", "_")
    zip_path = downloads_dir / ("%s_%s_%s" % (game.id, safe_tag, asset.name))
    if on_progress:
        on_progress("Fetching " + asset.name + "…")
    yank_file(asset.download_url, zip_path, on_progress)

    dest = library_game_dir(library_root, game.id)
    unzip_into(zip_path, dest, on_progress)
    # dont flatten the zip, these ports get mad if you move their files around
    exe = hunt_exe(dest, game.preferred_exes)
    if not exe:
        raise FileNotFoundError("Installed %s but couldn't find the exe under %s" % (game.name, dest))
    if on_progress:
        on_progress("Ready: " + exe.name)
    return exe.parent, exe


def grab_extra(asset, dest_dir, on_progress=None):
    # used for oot_soh.apworld into the archipelago worlds folder
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / asset.name
    if on_progress:
        on_progress("Downloading " + asset.name + "…")
    yank_file(asset.download_url, dest, on_progress)
    if on_progress:
        on_progress("Saved " + str(dest))
    return dest


def run_game(exe):
    exe = Path(exe)
    if not exe.exists():
        raise FileNotFoundError("can't find " + str(exe))
    # cwd has to be the game folder or soh cant find its files
    return subprocess.Popen([str(exe)], cwd=str(exe.parent), shell=False)


def open_in_explorer(path):
    # Folder button — just open wherever that game lives
    path = Path(path)
    if not path.is_dir():
        path = path.parent
    if not path.exists():
        raise FileNotFoundError("folder missing: " + str(path))
    os.startfile(str(path))


# old names
download_file = yank_file
extract_zip = unzip_into
install_from_asset = yank_and_install
download_extra_asset = grab_extra
launch_exe = run_game
open_folder = open_in_explorer
