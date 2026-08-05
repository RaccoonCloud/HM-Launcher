from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import httpx

from app.catalog import GameDef, score_windows_asset

CACHE_TTL_SECONDS = 3600
USER_AGENT = "HarbourMaster/1.0"


@dataclass
class ReleaseAsset:
    name: str
    download_url: str
    size: int


@dataclass
class LatestRelease:
    tag: str
    name: str
    html_url: str
    windows_zip: ReleaseAsset | None
    extras: dict[str, ReleaseAsset]
    fetched_at: float


def _cache_path(data_dir: Path, game_id: str) -> Path:
    return data_dir / "cache" / f"{game_id}_latest.json"


def _parse_cache(raw: dict[str, Any]) -> LatestRelease:
    zip_raw = raw.get("windows_zip")
    windows_zip = ReleaseAsset(**zip_raw) if zip_raw else None
    extras = {k: ReleaseAsset(**v) for k, v in (raw.get("extras") or {}).items()}
    return LatestRelease(
        tag=str(raw.get("tag", "")),
        name=str(raw.get("name", "")),
        html_url=str(raw.get("html_url", "")),
        windows_zip=windows_zip,
        extras=extras,
        fetched_at=float(raw.get("fetched_at", 0)),
    )


def _load_cache(path: Path, *, allow_stale: bool = False) -> LatestRelease | None:
    if not path.exists():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    fetched = float(raw.get("fetched_at", 0))
    if not allow_stale and time.time() - fetched > CACHE_TTL_SECONDS:
        return None
    return _parse_cache(raw)


def read_cached_release(
    game: GameDef,
    data_dir: Path,
    *,
    allow_stale: bool = True,
) -> LatestRelease | None:
    """Disk-only release info for instant UI — never hits the network."""
    return _load_cache(_cache_path(data_dir, game.id), allow_stale=allow_stale)


def _save_cache(path: Path, release: LatestRelease) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {
        "tag": release.tag,
        "name": release.name,
        "html_url": release.html_url,
        "windows_zip": asdict(release.windows_zip) if release.windows_zip else None,
        "extras": {k: asdict(v) for k, v in release.extras.items()},
        "fetched_at": release.fetched_at,
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def pick_windows_zip(assets: list[dict[str, Any]], game: GameDef) -> ReleaseAsset | None:
    best: tuple[int, ReleaseAsset] | None = None
    for asset in assets:
        name = str(asset.get("name", ""))
        score = score_windows_asset(name, game.win_asset_keywords)
        if score is None:
            continue
        candidate = ReleaseAsset(
            name=name,
            download_url=str(asset.get("browser_download_url", "")),
            size=int(asset.get("size") or 0),
        )
        if not candidate.download_url:
            continue
        if best is None or score > best[0]:
            best = (score, candidate)
    return best[1] if best else None


def fetch_latest_release(
    game: GameDef,
    data_dir: Path,
    *,
    force: bool = False,
) -> LatestRelease:
    cache_file = _cache_path(data_dir, game.id)
    if not force:
        cached = _load_cache(cache_file)
        if cached:
            return cached

    url = f"https://api.github.com/repos/{game.repo}/releases/latest"
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/vnd.github+json",
    }
    with httpx.Client(timeout=60.0, follow_redirects=True, headers=headers) as client:
        resp = client.get(url)
        resp.raise_for_status()
        data = resp.json()

    assets = list(data.get("assets") or [])
    windows_zip = pick_windows_zip(assets, game)
    extras: dict[str, ReleaseAsset] = {}
    for wanted in game.extra_assets:
        for asset in assets:
            name = str(asset.get("name", ""))
            if name.lower() == wanted.lower():
                extras[wanted] = ReleaseAsset(
                    name=name,
                    download_url=str(asset.get("browser_download_url", "")),
                    size=int(asset.get("size") or 0),
                )
                break

    release = LatestRelease(
        tag=str(data.get("tag_name") or ""),
        name=str(data.get("name") or data.get("tag_name") or ""),
        html_url=str(data.get("html_url") or ""),
        windows_zip=windows_zip,
        extras=extras,
        fetched_at=time.time(),
    )
    _save_cache(cache_file, release)
    return release
