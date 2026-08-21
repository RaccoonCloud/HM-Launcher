# talking to github. also the "update myself" bat nonsense lives here.
# I cache release json for an hour so Refresh isnt yelling at the API constantly.

import json
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path

import httpx

from app.config import APP_NAME, APP_VERSION, LAUNCHER_REPO
from app.games import zip_score

# dont hammer github every click, cache for an hour
CACHE_SECS = 3600

# I stick my app name on requests so github knows who I am.
# empty user-agents get blocked / rate limited and I was tired of weird errors.
USER_AGENT = "ShipYard/" + APP_VERSION


class ReleaseAsset:
    # one file on a release (the win64 zip, apworld, etc)
    def __init__(self, name, download_url, size=0):
        self.name = name
        self.download_url = download_url
        self.size = size


class LatestRelease:
    # whatever github said was latest for a game repo
    def __init__(self, tag, name, html_url, windows_zip, extras, fetched_at, body=""):
        self.tag = tag
        self.name = name
        self.html_url = html_url
        self.windows_zip = windows_zip
        self.extras = extras
        self.fetched_at = fetched_at
        self.body = body  # release notes text for What's new


class LauncherRelease:
    # same idea but for ShipYard itself
    def __init__(self, tag, name, html_url, asset, fetched_at, body=""):
        self.tag = tag
        self.name = name
        self.html_url = html_url
        self.asset = asset
        self.fetched_at = fetched_at
        self.body = body


def _cache_file(data_dir, game_id):
    return Path(data_dir) / "cache" / (game_id + "_latest.json")


def _launcher_cache(data_dir):
    return Path(data_dir) / "cache" / "launcher_latest.json"


def _asset_from_dict(d):
    if not d:
        return None
    return ReleaseAsset(d.get("name", ""), d.get("download_url", ""), int(d.get("size") or 0))


def _asset_to_dict(a):
    if not a:
        return None
    return {"name": a.name, "download_url": a.download_url, "size": a.size}


def _parse_game_cache(raw):
    extras = {}
    for k, v in (raw.get("extras") or {}).items():
        extras[k] = _asset_from_dict(v)
    return LatestRelease(
        str(raw.get("tag", "")),
        str(raw.get("name", "")),
        str(raw.get("html_url", "")),
        _asset_from_dict(raw.get("windows_zip")),
        extras,
        float(raw.get("fetched_at", 0)),
        str(raw.get("body", "") or ""),
    )


def _load_cache(path, allow_stale=False):
    path = Path(path)
    if not path.exists():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    age = time.time() - float(raw.get("fetched_at", 0))
    if not allow_stale and age > CACHE_SECS:
        return None
    return _parse_game_cache(raw)


def cached_game_release(game, data_dir, allow_stale=True):
    # used on boot so the cards show something before the network finishes
    return _load_cache(_cache_file(data_dir, game.id), allow_stale)


def _save_cache(path, release):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    extras = {}
    for k, v in release.extras.items():
        extras[k] = _asset_to_dict(v)
    blob = {
        "tag": release.tag,
        "name": release.name,
        "html_url": release.html_url,
        "windows_zip": _asset_to_dict(release.windows_zip),
        "extras": extras,
        "fetched_at": release.fetched_at,
        "body": release.body,
    }
    path.write_text(json.dumps(blob, indent=2), encoding="utf-8")


def _pick_win_zip(assets, game):
    best = None
    best_score = -1
    for a in assets:
        name = str(a.get("name", ""))
        score = zip_score(name, game.win_asset_keywords)
        if score is None:
            continue
        url = str(a.get("browser_download_url", ""))
        if not url:
            continue
        if score > best_score:
            best_score = score
            best = ReleaseAsset(name, url, int(a.get("size") or 0))
    return best


def grab_game_release(game, data_dir, force=False):
    # hit /releases/latest for that HM repo, pick the windows zip, remember it
    cache = _cache_file(data_dir, game.id)
    if not force:
        hit = _load_cache(cache)
        if hit:
            return hit

    url = "https://api.github.com/repos/" + game.repo + "/releases/latest"
    headers = {"User-Agent": USER_AGENT, "Accept": "application/vnd.github+json"}
    with httpx.Client(timeout=60.0, follow_redirects=True, headers=headers) as c:
        r = c.get(url)
        r.raise_for_status()
        data = r.json()

    assets = list(data.get("assets") or [])
    extras = {}
    for wanted in game.extra_assets:
        for a in assets:
            if str(a.get("name", "")).lower() == wanted.lower():
                extras[wanted] = ReleaseAsset(
                    str(a.get("name", "")),
                    str(a.get("browser_download_url", "")),
                    int(a.get("size") or 0),
                )
                break

    rel = LatestRelease(
        str(data.get("tag_name") or ""),
        str(data.get("name") or data.get("tag_name") or ""),
        str(data.get("html_url") or ""),
        _pick_win_zip(assets, game),
        extras,
        time.time(),
        str(data.get("body") or ""),
    )
    _save_cache(cache, rel)
    return rel


def _pick_launcher_asset(assets):
    # ShipYard zip first. old zips were called HMLauncher / HarbourMaster
    # because that name confused people with Harbour Masters themselves.
    best = None
    best_score = -1
    for a in assets:
        name = str(a.get("name", ""))
        url = str(a.get("browser_download_url", ""))
        if not url:
            continue
        low = name.lower()
        score = -1
        if low.endswith(".zip") and "shipyard" in low:
            score = 400
        elif low.endswith(".zip") and "hmlauncher" in low:
            score = 300
        elif low.endswith(".zip") and "harbourmaster" in low:
            score = 200
        elif low.endswith(".zip"):
            score = 100
        elif low == "shipyard.exe":
            score = 80
        elif low == "harbourmaster.exe":
            score = 50
        if score > best_score:
            best_score = score
            best = ReleaseAsset(name, url, int(a.get("size") or 0))
    return best


def grab_launcher_release(data_dir, force=False):
    # check my own ShipYard releases so Update Launcher has something to do
    cache = _launcher_cache(data_dir)
    if not force and cache.exists():
        try:
            raw = json.loads(cache.read_text(encoding="utf-8"))
            age = time.time() - float(raw.get("fetched_at", 0))
            if age <= CACHE_SECS:
                return LauncherRelease(
                    str(raw.get("tag", "")),
                    str(raw.get("name", "")),
                    str(raw.get("html_url", "")),
                    _asset_from_dict(raw.get("asset")),
                    float(raw.get("fetched_at", 0)),
                    str(raw.get("body", "") or ""),
                )
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            pass

    url = "https://api.github.com/repos/" + LAUNCHER_REPO + "/releases/latest"
    headers = {"User-Agent": USER_AGENT, "Accept": "application/vnd.github+json"}
    with httpx.Client(timeout=60.0, follow_redirects=True, headers=headers) as c:
        r = c.get(url)
        r.raise_for_status()
        data = r.json()

    rel = LauncherRelease(
        str(data.get("tag_name") or ""),
        str(data.get("name") or data.get("tag_name") or ""),
        str(data.get("html_url") or ""),
        _pick_launcher_asset(list(data.get("assets") or [])),
        time.time(),
        str(data.get("body") or ""),
    )
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(
        json.dumps(
            {
                "tag": rel.tag,
                "name": rel.name,
                "html_url": rel.html_url,
                "asset": _asset_to_dict(rel.asset),
                "fetched_at": rel.fetched_at,
                "body": rel.body,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return rel


# ---- self update (windows is annoying about replacing a running exe) ----
# I download the new zip, drop ShipYard.exe.new next to me, then a bat
# waits a second and swaps the file after I quit.

# still accept the old exe name so people on 1.8 can update
_EXE_NAMES = (APP_NAME + ".exe", "ShipYard.exe", "HarbourMaster.exe")


def _find_new_exe(root):
    root = Path(root)
    for name in _EXE_NAMES:
        p = root / name
        if p.is_file():
            return p
    for name in _EXE_NAMES:
        for p in root.rglob(name):
            if p.is_file():
                return p
    return None


def do_self_update(asset, downloads_dir, on_progress=None):
    from app.dl import yank_file

    if not getattr(sys, "frozen", False):
        raise RuntimeError("self-update only works from the built " + APP_NAME + ".exe")

    current = Path(sys.executable).resolve()
    app_dir = current.parent
    downloads_dir = Path(downloads_dir)
    downloads_dir.mkdir(parents=True, exist_ok=True)

    staging = downloads_dir / "launcher_update"
    if staging.exists():
        shutil.rmtree(staging, ignore_errors=True)
    staging.mkdir(parents=True, exist_ok=True)

    archive = staging / (asset.name or "update.bin")
    if on_progress:
        on_progress("Downloading launcher update…")
    yank_file(asset.download_url, archive, on_progress)

    new_exe = None
    if archive.suffix.lower() == ".zip":
        extract_dir = staging / "extracted"
        extract_dir.mkdir(parents=True, exist_ok=True)
        if on_progress:
            on_progress("Extracting launcher update…")
        zf = zipfile.ZipFile(archive, "r")
        try:
            zf.extractall(extract_dir)
        finally:
            zf.close()
        new_exe = _find_new_exe(extract_dir)
    elif archive.suffix.lower() == ".exe":
        new_exe = archive

    if new_exe is None or not new_exe.is_file():
        raise RuntimeError("update zip didn't have " + APP_NAME + ".exe in it")

    pending = app_dir / (current.name + ".new")
    shutil.copy2(new_exe, pending)

    bat = app_dir / "shipyard_apply_update.bat"
    lines = [
        "@echo off",
        "setlocal",
        'cd /d "' + str(app_dir) + '"',
        "echo Updating " + APP_NAME + "…",
        "ping 127.0.0.1 -n 3 >nul",
        'if exist "' + pending.name + '" (',
        '  move /Y "' + pending.name + '" "' + current.name + '" >nul',
        ")",
        'start "" "' + current.name + '"',
        'del "%~f0" >nul 2>&1',
        "",
    ]
    bat.write_text("\r\n".join(lines), encoding="utf-8")

    if on_progress:
        on_progress("Restarting to finish update…")

    flags = 0x00000008 | 0x00000200
    subprocess.Popen(["cmd.exe", "/c", str(bat)], cwd=str(app_dir), creationflags=flags, close_fds=True)


# aliases so I dont have to remember
read_cached_release = cached_game_release
fetch_latest_release = grab_game_release
fetch_launcher_latest = grab_launcher_release
apply_launcher_update = do_self_update
