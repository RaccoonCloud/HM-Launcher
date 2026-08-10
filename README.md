# HarbourMaster

**Version 1.8.0**

Windows launcher for [Harbour Masters](https://github.com/HarbourMasters) PC ports.

**Created by RaccoonCloud** for the Harbour Masters team and everyone who wants an easy way to install, update, and launch the ports.

Game builds come from the HarbourMasters GitHub releases. You must use your own legally obtained ROMs / games. Do not share, ask for, or distribute ROMs.

---

## What it does

- Lists Harbour Masters ports in one place (SoH, 2Ship, Starship, SpaghettiKart, Ghostship, Lighthouse, Archipelago SoH)
- Downloads / updates the latest stable Win64 release from GitHub
- Launches installed games, or lets you point at folders you already have
- Shows **installed** and **latest** version on each game card
- **Update** button per game when a newer build is available
- **What's new** — view that release’s changelog from GitHub
- Optional auto-update when a new game release is published
- Footer shows **HarbourMaster version** plus **Update Launcher**
- Archipelago SoH: download `oot_soh.apworld` into your Archipelago custom worlds folder
- Quick link to the Harbour Masters Discord

---

## Install (new users — ready-made EXE)

This GitHub repo is **source code**. The runnable Windows app is **`HMLauncher.zip`**, which contains `HarbourMaster.exe`.

Get the zip from whoever shared it with you (Discord / Drive / a GitHub **Release** if one is published). Then:

1. Download `HMLauncher.zip`
2. Extract it somewhere easy, for example:
   - `C:\Games\HarbourMaster\`
   - or your Desktop
3. Double-click **HarbourMaster.exe**
4. If Windows shows **Windows protected your PC**:
   - Click **More info**
   - Click **Run anyway**  
   (Normal for apps that are not code-signed.)
5. No Python install is required.

That’s it — the launcher is ready.

> Cloning this repository alone does **not** give you an EXE. Use the zip above, or build from source (below).

---

## First-time setup

1. Open **Settings**
2. Set **Library root** to a folder you own  
   - Default is `D:\HarbourMaster`  
   - Change this if you don’t have a D: drive (e.g. `C:\Games\HarbourMasterLibrary`)
3. (Optional) Set **Archipelago custom worlds** if you use Archipelago SoH
4. Leave **Auto-update** on if you want new builds downloaded for you, or turn it off for manual-only updates
5. Click **Save**

---

## User guide

### Install a game
1. Find the game/project
2. Click **Install**
3. Wait for the download to finish  
   Games install under your library root, each in its own subfolder

### Launch a game
1. Click **Launch**
2. On first run, the port itself will ask for your legal ROM / game files  
   HarbourMaster does not ship ROMs - ALWAYS OWN YOUR OWN LEGAL COPY OF THE GAME! DO NOT ASK FOR ROMS OR DISTRIBUTE ROMS!

### Update a game
1. When a newer build exists, the card shows a yellow **Update** button (and the installed vs latest versions)
2. Click **Update**, or use the yellow banner / auto-update
3. Click **What's new** to read the GitHub release notes for that build

### Already installed somewhere else?
1. Click **Browse**
2. Pick the folder that contains the game’s `.exe`
3. Use **Launch** after that

### Open the install folder
- Click **Folder** on the game card

### Check for updates
- Click **Refresh** in the top bar  
- Or leave auto-update enabled (checks on a delay after startup, on Refresh, and about once an hour while open)
- Footer **Update Launcher** checks/installs a newer HarbourMaster build

### Archipelago SoH apworld
1. Set your Archipelago custom worlds folder in **Settings**
2. On the Archipelago SoH card, click **Get apworld**

### Discord
- Use the Discord button in the bottom-right footer to open the official Harbour Masters Discord

- More help and information can be found here!

---

## What gets created on your PC

| Location | Purpose |
|---|---|
| Next to `HarbourMaster.exe` → `data\` | Launcher settings, install paths, release cache |
| Your **Library root** | Downloaded game builds |
| Archipelago custom worlds folder | `oot_soh.apworld` (if you use that feature) |

You can move the whole HarbourMaster folder later; keep `HarbourMaster.exe` and its `data\` folder together.

---

## Build from source (developers)

If you only have this repo (no zip), build the EXE yourself:

```powershell
cd path\to\harbourmaster-launcher
pip install -r requirements.txt
.\build_exe.bat
```

That creates **`HarbourMaster.exe` in the project root** (and also under `dist\` / Desktop while building).

Share with users by zipping that EXE + this README as `HMLauncher.zip`.

Run without building an EXE:

```powershell
pip install -r requirements.txt
python main.py
```

`build\` and `dist\` are temporary PyInstaller folders — not what end users need.

---

## Credits

- **Created by:** RaccoonCloud
- **Made for:** Harbour Masters team and the community
- **Game ports / releases:** [HarbourMasters](https://github.com/HarbourMasters) on GitHub
- **Discord:** [Harbour Masters](https://discord.com/invite/shipofharkinian)

Please support the Harbour Masters projects and use only ROMs / dumps you personally own.

---

## Future plans

**v1.8.0** adds clearer per-game Update / What's new, installed version on each card, and Update Launcher in the footer. More improvements are still planned, including:

- Further UI polish and quality-of-life tweaks
- Extra helper actions around installs and Archipelago workflows
- Support for new Harbour Masters ports as they appear

Feedback from the team and community will help decide what comes next.

### Note on launcher self-update

Self-update reads the latest release from `RaccoonCloud/HM-Launcher`. For other PCs to download that update automatically.
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
