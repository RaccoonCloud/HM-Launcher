# ShipYard

Unofficial Windows launcher for Harbour Masters PC ports.

**Made by RaccoonCloud** — not an official HM app. I just got tired of hunting zips.

Used to be called HarbourMaster. Renamed to ShipYard so people stop thinking it's from the HM team.

Pulls the latest stable Win64 builds from the HarbourMasters GitHub repos. **Bring your own legal ROMs.** No dumps, no asking, no sharing.

## What you get

- SoH, 2Ship, Starship, SpaghettiKart, Ghostship, Lighthouse, Archipelago SoH in one window
- Install / Update per game (not a bulk download-everything on first open)
- Shows installed vs latest
- What's new from the GitHub release notes
- Optional auto-update for stuff this launcher already installed
- Can update itself
- Archipelago SoH: grab `oot_soh.apworld`
- Discord button

## Download

Grab `ShipYard-v1.9.0.zip` from Releases, extract it, run `ShipYard.exe`.

Windows might yell about an unsigned app — More info → Run anyway. Normal for stuff that isn't code-signed.

## First run

1. Settings → set Library root (default `D:\ShipYard`, change if you need to)
2. Optional: Archipelago custom worlds folder
3. Hit Install on whatever you want

## Build it yourself

```
pip install -r requirements.txt
build_exe.bat
```

That spits out `ShipYard.exe`. Zip that + this README if you're sharing.

Or just `python main.py` if you have Python.

## Looking for help

It’s Python + CustomTkinter, hits GitHub for HM builds. UI is one big ridiculous file of like 900+ lines (I’m sorry). The rest is split into smaller bits.

Not gonna lie — maybe **10–15%** AI help, mostly on code breaks, line errors, and the extreme slow load when **v1.0** was first written. Kept it to a minimum. Still my project, still solo and limited.

Getting a small team to help would be awesome — way better than copy-pasting errors into AI and pasting lines back. Real people who know HM ports / Python / UI would help this grow properly (and maybe help split that UI file someday).

Testing, UI, new ports, install weirdness, whatever you’re good at — **DM me if you’re interested.**

## Credits

- Me: **RaccoonCloud**
- Ports / releases: [HarbourMasters](https://github.com/HarbourMasters)
- Discord: https://discord.com/invite/shipofharkinian

Support the HM projects. Own your ROMs.

---

Special thank you for your friendship, support, and memories over the years!

- Caladius
- Proxysaw
- aMannus
- itsHeckinPat
- Fredomato
- Leggettc18
- MoonlitxShadows
- CardinalNerd
- Smiffic
- SirMagicPenguin
- alwayszchartergirl
- OneSpicyGinger
- Nordic Ryan
- Grimey
- Scorched11
- AGreenSpoon
- Mellar
- PapaChiefo
