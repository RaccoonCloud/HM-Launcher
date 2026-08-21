# the window. CustomTkinter because I wanted dark mode , as who doesnt like dark mode, maybe do a choice of light and dark mode in future....maybe
# downloads run on a background thread so the UI doesnt freeze and lag like it was doing and again ran that error through A free AI as im not paying for that and too scared to bother the devs so upfront no lies here.
# this code is massive yeah happy for you cool devs who read this to help me out and shrink some stuff maybe clean it, and yeah FREE AI helped me with breaks and line finds and apparently better code lines ALSO BRACKETS I KEPT FORGETTING THEM AND SYNAX LINE ERRORs PYTHON AM I RIGHT YAH ITS PYTHON WITH CUSTOM TKINTER HELPS FOR THE FANCYNESS WITH VALUES AND SIZING




import sys
import threading
import time
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk
import tkinter as tk

from app import art, config, dl, games, gh
from app.config import APP_NAME, APP_VERSION, is_newer

# Dark theme. teal + yellow it was red but red lights spell danger so Update actually stands out
ACCENT = "#1a8a8a"
ACCENT_HOVER = "#147070"
WARN = "#c9a227"
WARN_HOVER = "#a8861f"
BG = "#12161c"
PANEL = "#1a222c"
CARD = "#222b36"
TEXT = "#e6edf3"
MUTED = "#8b9aab"

# check github about once an hour while the window is open ( this could be longer if user wants maybe make that a setting as I dont think it updates every hour, devs know best NO DEV ROLE FOR THIS GUY)

HOUR_MS = 60 * 60 * 1000

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")
 # DO PEOPLE WANT CUSTOM THEMES AND COLOURS!! TELL ME DEVS IF YOU ARE CHECKING THISCODE!!

class PortRow(ctk.CTkFrame):
    # one game card. buttons come and go depending on install / update state.
    def __init__(self, master, game, on_launch, on_install, on_browse, on_folder, on_changelog=None, on_apworld=None, icon_image=None):
        super().__init__(master, fg_color=CARD, corner_radius=10)
        self.game = game
        self._icon_ref = icon_image
        self.grid_columnconfigure(1, weight=1)

        icon_wrap = ctk.CTkFrame(self, fg_color="transparent", width=84, height=84)
        icon_wrap.grid(row=0, column=0, rowspan=5, padx=(12, 4), pady=12, sticky="nw")
        icon_wrap.grid_propagate(False)
        self._icon_label = ctk.CTkLabel(icon_wrap, text="")
        self._icon_label.place(relx=0.5, rely=0.5, anchor="center")
        if self._icon_ref is not None:
            self._icon_label.configure(image=self._icon_ref, text="")
        else:
            self._icon_label.configure(text="…", text_color=MUTED, font=ctk.CTkFont(size=18, weight="bold"))

        title = ctk.CTkLabel(self, text=game.name, font=ctk.CTkFont(size=18, weight="bold"), text_color=TEXT, anchor="w")
        title.grid(row=0, column=1, sticky="ew", padx=(4, 14), pady=(12, 0))

        self.blurb = ctk.CTkLabel(self, text=game.blurb, font=ctk.CTkFont(size=12), text_color=MUTED, anchor="w")
        self.blurb.grid(row=1, column=1, sticky="ew", padx=(4, 14), pady=(2, 0))

        self.version_var = ctk.StringVar(value="Installed: —")
        self.version = ctk.CTkLabel(self, textvariable=self.version_var, font=ctk.CTkFont(size=12), text_color=MUTED, anchor="w")
        self.version.grid(row=2, column=1, sticky="ew", padx=(4, 14), pady=(4, 0))

        self.status_var = ctk.StringVar(value="Checking…")
        self.status = ctk.CTkLabel(self, textvariable=self.status_var, font=ctk.CTkFont(size=12), text_color=TEXT, anchor="w")
        self.status.grid(row=3, column=1, sticky="ew", padx=(4, 14), pady=(4, 0))

        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.grid(row=4, column=1, sticky="ew", padx=(0, 10), pady=(10, 12))

        self.launch_btn = ctk.CTkButton(btns, text="Launch", width=90, fg_color=ACCENT, hover_color=ACCENT_HOVER, command=lambda: on_launch(game))
        self.launch_btn.pack(side="left", padx=4)

        self.install_btn = ctk.CTkButton(btns, text="Install", width=100, fg_color="#1f6aa5", hover_color="#144870", command=lambda: on_install(game))
        self.install_btn.pack(side="left", padx=4)

        self.update_btn = ctk.CTkButton(btns, text="Update", width=100, fg_color=WARN, hover_color=WARN_HOVER, text_color="#1a1a1a", command=lambda: on_install(game))
        # I only pack Update when that game actually needs it
        self._update_shown = False

        self.changelog_btn = ctk.CTkButton(btns, text="What's new", width=100, fg_color="#3a4555", hover_color="#2f3947", command=lambda: on_changelog(game) if on_changelog else None)
        self._notes_shown = False

        ctk.CTkButton(btns, text="Browse", width=80, command=lambda: on_browse(game)).pack(side="left", padx=4)
        ctk.CTkButton(btns, text="Folder", width=80, command=lambda: on_folder(game)).pack(side="left", padx=4)

        if game.id == "archipelago_soh" and on_apworld:
            self.apworld_btn = ctk.CTkButton(btns, text="Get apworld", width=110, command=lambda: on_apworld(game))
            self.apworld_btn.pack(side="left", padx=4)
 #i WANT LIE ARCHI STUFF IS LIKE YYYEAAAHHH IMMA GET SOME HELP PLEASE OR EXPECT BREAKS AND FREE AI HELP!!
    def set_icon(self, image):
        self._icon_ref = image
        self._icon_label.configure(image=image, text="")

    def set_versions(self, installed, latest):
        if not installed:
            installed = "—"
        if not latest:
            latest = "—"
        self.version_var.set("Installed: %s   ·   Latest: %s" % (installed, latest))

    def set_update_available(self, available, latest_tag=""):
        if available:
            if latest_tag:
                self.update_btn.configure(text="Update to " + latest_tag)
            else:
                self.update_btn.configure(text="Update")
            if not self._update_shown:
                self.update_btn.pack(side="left", padx=4, after=self.install_btn)
                self._update_shown = True
        else:
            if self._update_shown:
                self.update_btn.pack_forget()
                self._update_shown = False
        self.install_btn.configure(text="Install")

    def remember_installed(self, installed):
        # keep saying Install. Reinstall made it look like I already
        # shoved a copy in when I just found their old folder
        self.install_btn.configure(text="Install")

    def set_changelog_available(self, available):
        if available and not self._notes_shown:
            after = self.update_btn if self._update_shown else self.install_btn
            self.changelog_btn.pack(side="left", padx=4, after=after)
            self._notes_shown = True
        elif not available and self._notes_shown:
            self.changelog_btn.pack_forget()
            self._notes_shown = False

    def set_busy(self, busy):
        st = "disabled" if busy else "normal"
        self.launch_btn.configure(state=st)
        self.install_btn.configure(state=st)
        self.update_btn.configure(state=st)
        self.changelog_btn.configure(state=st)


class App(ctk.CTk):
    # splash for a couple seconds so icons can warm up, then the real UI the reason was the crashing at the start and slow load ups this code was lookoed over by AI but cleaned up by me
    SPLASH_MIN_MS = 2500

    def __init__(self):
        super().__init__()
        self.title(APP_NAME + " " + APP_VERSION)
        self.configure(fg_color=BG)
        self.settings = config.load_settings()
        self.installs = config.load_installs()
        self.geometry(self.settings.get("window_geometry", "980x720"))
        self.minsize(860, 600)

        self._releases = {}
        self._busy = False
        self._cards = {}
        self._update_queue = []
        self._auto_updating = False
        self._splash_photos = []
        self._header_photos = []
        self._game_ctk_icons = {}
        self._anim_idx = 0
        self._splash_job = None
        self._header_job = None
        self._splash_started_at = 0.0
        self._boot_ready = False
        self._main_ready = False
        self._launcher_release = None
        self._game_update_prompted = False
        self._launcher_prompted = False

        art.apply_window_icon(self)
        config.ensure_dirs()
        self._show_splash()
        self.after(1, self._start_splash_animation)
        self.after(1, self._boot_async)

    def _start_splash_animation(self):
        self._splash_photos = art.load_prebaked_photos(art.ANIM_SPLASH)
        # header gif is huge, 18 frames is enough and keeps scrolling smooth
        self._header_photos = art.load_prebaked_photos(art.ANIM_HEADER, max_frames=18)
        if not self._splash_photos:
            static = art.load_static_photo((256, 256))
            if static:
                self._splash_photos = [static]
        if self._splash_photos:
            self._splash_label.configure(image=self._splash_photos[0])
            self._splash_started_at = time.monotonic()
            self._anim_idx = 0
            self._animate_splash()
            if hasattr(self, "_splash_status"):
                self._splash_status.configure(text="Starting ShipYard…")

    def _show_splash(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._splash = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        self._splash.grid(row=0, column=0, sticky="nsew")
        self._splash.grid_columnconfigure(0, weight=1)
        self._splash.grid_rowconfigure(0, weight=1)

        center = ctk.CTkFrame(self._splash, fg_color=BG)
        center.grid(row=0, column=0)

        self._splash_label = tk.Label(center, text="", bg=BG, bd=0, highlightthickness=0)
        self._splash_label.pack(padx=24, pady=(24, 8))
        ctk.CTkLabel(center, text=APP_NAME, font=ctk.CTkFont(size=22, weight="bold"), text_color=TEXT).pack(pady=(0, 4))
        self._splash_status = ctk.CTkLabel(center, text="Loading…", text_color=MUTED)
        self._splash_status.pack(pady=(0, 24))

        photo = art.load_static_photo((256, 256))
        if photo:
            self._splash_photos = [photo]
            self._splash_label.configure(image=photo)

    def _animate_splash(self):
        if not self._splash_photos:
            return
        try:
            self._splash_label.configure(image=self._splash_photos[self._anim_idx % len(self._splash_photos)])
        except Exception:
            return
        self._anim_idx += 1
        self._splash_job = self.after(50, self._animate_splash)

    def _stop_splash(self):
        if self._splash_job is not None:
            try:
                self.after_cancel(self._splash_job)
            except Exception:
                pass
            self._splash_job = None
        if hasattr(self, "_splash") and self._splash.winfo_exists():
            self._splash.destroy()
        self._splash_photos = []

    def _boot_async(self):
        # splash thread: warm icons + link any ports I already had on disk
        def work():
            try:
                art.warm_icons(size=(72, 72))
                self._seed_hint_installs()
            finally:
                self.after(0, self._on_boot_work_done)

        if hasattr(self, "_splash_status"):
            self._splash_status.configure(text="Preparing games…")
        threading.Thread(target=work, daemon=True).start()

    def _on_boot_work_done(self):
        self._boot_ready = True
        if hasattr(self, "_splash_status"):
            self._splash_status.configure(text="Ready…")
        self._maybe_finish_boot()

    def _maybe_finish_boot(self):
        if not self._boot_ready:
            return
        started = self._splash_started_at or time.monotonic()
        left = int(max(0, self.SPLASH_MIN_MS - (time.monotonic() - started) * 1000))
        if left > 0:
            self.after(left, self._finish_boot)
        else:
            self._finish_boot()

    def _finish_boot(self):
        if self._main_ready:
            return
        self._main_ready = True
        self._stop_splash()
        for child in list(self.winfo_children()):
            try:
                child.destroy()
            except Exception:
                pass
        self._apply_disk_caches()
        self._build()
        art.apply_window_icon(self)
        self.after(100, lambda: art.apply_window_icon(self))
        self._start_header_animation()
        self.after(20, lambda: self._attach_game_icons(0))
        # let the window come up first, then poke github (was freezing boot before)
        self.after(12000, lambda: self._refresh_releases(False, False))
        self.after(14000, lambda: self._check_launcher_update(False, True))
        self.after(HOUR_MS, self._periodic_check)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _apply_disk_caches(self):
        # show last known tags instantly from disk, network fills in later
        for game in games.GAMES:
            cached = gh.cached_game_release(game, config.DATA_DIR, True)
            if cached is not None:
                self._releases[game.id] = cached

    def _attach_game_icons(self, index=0):
        with_icons = [g for g in games.GAMES if g.icon_file]
        if index >= len(with_icons):
            return
        game = with_icons[index]
        if game.id not in self._game_ctk_icons:
            pil = art.load_pil(game.icon_file, (72, 72))
            if pil is not None:
                img = ctk.CTkImage(light_image=pil, dark_image=pil, size=(72, 72))
                self._game_ctk_icons[game.id] = img
                card = self._cards.get(game.id)
                if card is not None:
                    card.set_icon(img)
        self.after(1, lambda: self._attach_game_icons(index + 1))

    def _start_header_animation(self):
        if not self._header_photos or not hasattr(self, "_header_label"):
            return
        self._anim_idx = 0

        def tick():
            if not self._header_photos:
                return
            try:
                self._header_label.configure(image=self._header_photos[self._anim_idx % len(self._header_photos)])
            except Exception:
                return
            self._anim_idx += 1
            self._header_job = self.after(90, tick)

        tick()

    def _seed_hint_installs(self):
        # first launch used to treat every folder I already had as
        # "needs update" and start downloading everything this cdid cause lag so yyyeeaahhhhh. just link them.
        for game in games.GAMES:
            entry = self.installs.get(game.id) or {}
            exe_path = Path(str(entry.get("exe_path", "")))
            if exe_path.is_file():
                continue
            hinted = games.peek_old_folder(game)
            if not hinted:
                continue
            exe = games.hunt_exe(hinted, game.preferred_exes)
            if not exe:
                continue
            self.installs = config.remember_install(
                self.installs,
                game.id,
                str(exe.parent),
                str(exe),
                str(entry.get("version_tag", "")),
            )
        self.installs = config.load_installs()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=0)

        top = ctk.CTkFrame(self, fg_color=PANEL, corner_radius=0)
        top.grid(row=0, column=0, sticky="ew")
        top.grid_columnconfigure(1, weight=1)

        brand = ctk.CTkFrame(top, fg_color="transparent")
        brand.grid(row=0, column=0, padx=(12, 8), pady=4, sticky="w")
        self._header_label = tk.Label(brand, text="", bg=PANEL, bd=0, highlightthickness=0)
        self._header_label.pack(side="left", padx=(0, 8))
        if self._header_photos:
            self._header_label.configure(image=self._header_photos[0])
        elif art.LOGO_PNG.is_file():
            from PIL import Image, ImageTk

            pil = Image.open(art.LOGO_PNG).convert("RGBA").resize((40, 40), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(pil)
            self._header_photos = [photo]
            self._header_label.configure(image=photo)
        ctk.CTkLabel(brand, text=APP_NAME, font=ctk.CTkFont(size=20, weight="bold"), text_color=TEXT).pack(side="left")

        self.library_var = ctk.StringVar(value=str(self.settings.get("library_root", "")))
        lib_row = ctk.CTkFrame(top, fg_color="transparent")
        lib_row.grid(row=0, column=1, sticky="ew", padx=8, pady=4)
        lib_row.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(lib_row, text="Library", text_color=MUTED).grid(row=0, column=0, padx=(0, 6))
        ctk.CTkEntry(lib_row, textvariable=self.library_var, height=28).grid(row=0, column=1, sticky="ew")
        ctk.CTkButton(lib_row, text="…", width=36, height=28, command=self._pick_library).grid(row=0, column=2, padx=(6, 0))

        ctk.CTkButton(top, text="Refresh", width=90, height=28, command=lambda: self._refresh_releases(True, True)).grid(row=0, column=2, padx=6, pady=4)
        ctk.CTkButton(top, text="Settings", width=90, height=28, command=self._open_settings).grid(row=0, column=3, padx=(6, 12), pady=4)

        self._notify = ctk.CTkFrame(self, fg_color="#2a2416", corner_radius=0)
        self._notify.grid(row=1, column=0, sticky="ew")
        self._notify.grid_columnconfigure(0, weight=1)
        self._notify_var = ctk.StringVar(value="")
        ctk.CTkLabel(self._notify, textvariable=self._notify_var, text_color="#f0e6c8", anchor="w", font=ctk.CTkFont(size=13, weight="bold")).grid(row=0, column=0, sticky="ew", padx=(16, 8), pady=8)
        self._notify_action_btn = ctk.CTkButton(self._notify, text="Update", width=110, height=28, fg_color=WARN, hover_color=WARN_HOVER, text_color="#1a1a1a", command=self._on_notify_action)
        self._notify_action_btn.grid(row=0, column=1, padx=6, pady=6)
        ctk.CTkButton(self._notify, text="Dismiss", width=80, height=28, fg_color="transparent", hover_color="#3a3424", command=self._hide_notify).grid(row=0, column=2, padx=(0, 12), pady=6)
        self._notify_action = ""
        self._hide_notify()

        scroll = ctk.CTkScrollableFrame(self, fg_color=BG)
        scroll.grid(row=2, column=0, sticky="nsew", padx=10, pady=(4, 4))
        scroll.grid_columnconfigure(0, weight=1)

        i = 0
        for game in games.GAMES:
            card = PortRow(
                scroll,
                game,
                self._launch_game,
                self._install_game,
                self._browse_game,
                self._open_game_folder,
                self._show_game_changelog,
                self._download_apworld,
                self._game_ctk_icons.get(game.id),
            )
            card.grid(row=i, column=0, sticky="ew", pady=(0, 4))
            self._cards[game.id] = card
            self._update_card_status(game)
            i += 1

        foot = ctk.CTkFrame(self, fg_color=PANEL, corner_radius=0)
        foot.grid(row=3, column=0, sticky="ew")
        foot.grid_columnconfigure(0, weight=1)
        self.status_var = ctk.StringVar(value="Pulls latest builds from gh.com/HarbourMasters. Use your own legal ROMs.")
        ctk.CTkLabel(foot, textvariable=self.status_var, text_color=MUTED, anchor="w", font=ctk.CTkFont(size=12)).grid(row=0, column=0, sticky="ew", padx=(16, 8), pady=8)

        self._launcher_version_var = ctk.StringVar(value="v" + APP_VERSION)
        ctk.CTkLabel(foot, textvariable=self._launcher_version_var, text_color=MUTED, font=ctk.CTkFont(size=12)).grid(row=0, column=1, padx=(8, 6), pady=8)

        self._launcher_update_btn = ctk.CTkButton(foot, text="Update Launcher", width=130, height=28, fg_color="#3a4555", hover_color="#2f3947", command=self._on_footer_launcher_update)
        self._launcher_update_btn.grid(row=0, column=2, padx=6, pady=6)

        self._discord_icon = art.load_discord_ctk_image((24, 24))
        discord_btn = ctk.CTkButton(
            foot,
            text="" if self._discord_icon else "Discord",
            image=self._discord_icon,
            width=34,
            height=28,
            fg_color="transparent",
            hover_color="#2a3340",
            corner_radius=6,
            command=self._open_discord,
        )
        discord_btn.grid(row=0, column=3, padx=(0, 12), pady=6, sticky="e")
        self._refresh_launcher_footer()

    def _set_status(self, text):
        self.status_var.set(text)

    def _hide_notify(self):
        self._notify_action = ""
        self._notify_var.set("")
        self._notify.grid_remove()

    def _show_notify(self, text, action, button="Update"):
        self._notify_action = action
        self._notify_var.set(text)
        self._notify_action_btn.configure(text=button)
        self._notify.grid()

    def _on_notify_action(self):
        if self._notify_action == "games":
            self._hide_notify()
            self._queue_auto_updates()
        elif self._notify_action == "launcher":
            self._hide_notify()
            self._start_launcher_update()

    def _open_discord(self):
        webbrowser.open(art.DISCORD_URL)

    def _periodic_check(self):
        if not self._busy and not self._auto_updating:
            self._refresh_releases(False, True)
            self._check_launcher_update(False, True)
        self.after(HOUR_MS, self._periodic_check)

    def _pick_library(self):
        path = filedialog.askdirectory(title="Library root", initialdir=self.library_var.get() or None)
        if path:
            self.library_var.set(path)
            self.settings["library_root"] = path
            config.save_settings(self.settings)

    def _open_settings(self):
        win = ctk.CTkToplevel(self)
        win.title("Settings")
        win.geometry("560x480")
        win.transient(self)
        win.grab_set()

        ctk.CTkLabel(win, text="Library root").pack(anchor="w", padx=16, pady=(16, 4))
        lib_var = ctk.StringVar(value=str(self.settings.get("library_root", "")))
        ctk.CTkEntry(win, textvariable=lib_var, width=500).pack(padx=16, fill="x")

        ctk.CTkLabel(win, text="Archipelago custom worlds folder (for oot_soh.apworld)").pack(anchor="w", padx=16, pady=(16, 4))
        ap_var = ctk.StringVar(value=str(self.settings.get("archipelago_custom_worlds", "")))
        ap_row = ctk.CTkFrame(win, fg_color="transparent")
        ap_row.pack(fill="x", padx=16)
        ctk.CTkEntry(ap_row, textvariable=ap_var).pack(side="left", fill="x", expand=True)

        def pick_ap():
            path = filedialog.askdirectory(title="Archipelago custom worlds")
            if path:
                ap_var.set(path)

        ctk.CTkButton(ap_row, text="…", width=36, command=pick_ap).pack(side="left", padx=(6, 0))

        auto_var = ctk.BooleanVar(value=bool(self.settings.get("auto_update", True)))
        ctk.CTkCheckBox(win, text="Auto-update installed games when HarbourMasters publishes a new release", variable=auto_var).pack(anchor="w", padx=16, pady=(18, 4))
        ctk.CTkLabel(
            win,
            text="Only games this launcher installed (known version). Detected/linked folders stay until you click Update.",
            text_color=MUTED,
            wraplength=500,
            justify="left",
            anchor="w",
            font=ctk.CTkFont(size=11),
        ).pack(anchor="w", padx=16, pady=(0, 8))

        apworld_var = ctk.BooleanVar(value=bool(self.settings.get("auto_update_apworld", True)))
        ctk.CTkCheckBox(win, text="Also auto-download oot_soh.apworld when Archipelago SoH updates", variable=apworld_var).pack(anchor="w", padx=16, pady=(4, 4))

        launcher_var = ctk.BooleanVar(value=bool(self.settings.get("check_launcher_updates", True)))
        ctk.CTkCheckBox(win, text="Check for ShipYard launcher updates on startup", variable=launcher_var).pack(anchor="w", padx=16, pady=(4, 4))

        def save():
            self.settings["library_root"] = lib_var.get().strip()
            self.settings["archipelago_custom_worlds"] = ap_var.get().strip()
            self.settings["auto_update"] = bool(auto_var.get())
            self.settings["auto_update_apworld"] = bool(apworld_var.get())
            self.settings["check_launcher_updates"] = bool(launcher_var.get())
            self.library_var.set(self.settings["library_root"])
            config.save_settings(self.settings)
            win.destroy()
            self._set_status("Settings saved.")

        btn_row = ctk.CTkFrame(win, fg_color="transparent")
        btn_row.pack(pady=(18, 8))
        ctk.CTkButton(btn_row, text="Check for launcher update", width=190, command=lambda: self._check_launcher_update(True, True)).pack(side="left", padx=6)
        ctk.CTkButton(btn_row, text="Save", width=100, fg_color=ACCENT, hover_color=ACCENT_HOVER, command=save).pack(side="left", padx=6)

        ctk.CTkLabel(
            win,
            text="ShipYard v%s\nCreated by RaccoonCloud for the Harbour Masters team and community" % APP_VERSION,
            text_color=MUTED,
            font=ctk.CTkFont(size=12),
            justify="center",
        ).pack(pady=(8, 16))

    def _install_record(self, game_id):
        return dict(self.installs.get(game_id) or {})

    def _exe_for(self, game):
        entry = self._install_record(game.id)
        exe = Path(str(entry.get("exe_path", "")))
        if exe.is_file():
            return exe
        install_dir = Path(str(entry.get("install_dir", "")))
        if install_dir.is_dir():
            found = games.hunt_exe(install_dir, game.preferred_exes)
            if found:
                return found
        return None

    def _needs_update(self, game):
        # only auto-update and ONLY if I know what version I installed as this could cause laaaaaggg again and that wasnt fun to sort
        # linked folders with no tag stay alone until you click Update.
        if not self._exe_for(game):
            return False
        release = self._releases.get(game.id)
        if not release or not release.tag or not release.windows_zip:
            return False
        installed = str(self._install_record(game.id).get("version_tag", "") or "")
        # no version saved = I only linked HM folder. leave it alone as it could couse breaking and the headache isnt worth it atm

        # until they hit Update on that one game.
        if not installed:
            return False
        return installed != release.tag

    def _update_card_status(self, game):
        card = self._cards[game.id]
        entry = self._install_record(game.id)
        exe = self._exe_for(game)
        installed = str(entry.get("version_tag", "") or "")
        release = self._releases.get(game.id)
        latest = release.tag if release else ""
        body = ""
        if release and release.body:
            body = release.body

        if exe:
            card.set_versions(installed, latest or "—")
        else:
            card.set_versions("—", latest or "—")

        if not exe:
            status = "Not installed"
            if latest:
                status += "  ·  latest " + latest
        else:
            status = "Ready  ·  " + exe.name
            if latest and installed and latest != installed:
                status += "  ·  UPDATE AVAILABLE (" + latest + ")"
            elif latest and not installed:
                status += "  ·  version unknown (use Update to sync)"
            elif latest:
                status += "  ·  up to date"
        card.status_var.set(status)
        card.launch_btn.configure(state="normal" if exe else "disabled")

        show_update = False
        if exe and latest:
            if (installed and latest != installed) or (not installed):
                show_update = True
        card.remember_installed(bool(exe))
        card.set_update_available(show_update, latest if show_update else "")
        card.set_changelog_available(bool(body.strip()) or bool(latest))

    def _show_game_changelog(self, game):
        # What's new — I just show the github release body in a window SIMPLES!!
        release = self._releases.get(game.id)
        if release is None:
            messagebox.showinfo(APP_NAME, "No release info yet for %s. Try Refresh." % game.name)
            return
        body = (release.body or "").strip()
        if not body:
            if release.html_url:
                if messagebox.askyesno(APP_NAME, "No changelog text was published for %s %s.\n\nOpen the GitHub release page instead?" % (game.name, release.tag)):
                    webbrowser.open(release.html_url)
            else:
                messagebox.showinfo(APP_NAME, "No changelog available for %s." % game.name)
            return
        self._open_changelog_window(game.name + " — " + release.tag, body, release.html_url)

    def _open_changelog_window(self, title, body, html_url=""):
        win = ctk.CTkToplevel(self)
        win.title(title)
        win.geometry("720x480")
        win.transient(self)
        win.grab_set()
        ctk.CTkLabel(win, text=title, font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT, anchor="w").pack(fill="x", padx=16, pady=(16, 8))
        box = ctk.CTkTextbox(win, wrap="word", font=ctk.CTkFont(size=13))
        box.pack(fill="both", expand=True, padx=16, pady=(0, 8))
        box.insert("1.0", body)
        box.configure(state="disabled")
        row = ctk.CTkFrame(win, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=(0, 16))
        if html_url:
            ctk.CTkButton(row, text="Open on GitHub", width=140, command=lambda: webbrowser.open(html_url)).pack(side="left")
        ctk.CTkButton(row, text="Close", width=100, command=win.destroy).pack(side="right")

    def _refresh_launcher_footer(self):
        release = self._launcher_release
        if release and is_newer(release.tag, APP_VERSION):
            self._launcher_version_var.set("v%s  →  %s" % (APP_VERSION, release.tag))
            self._launcher_update_btn.configure(text="Update Launcher", fg_color=WARN, hover_color=WARN_HOVER, text_color="#1a1a1a", state="normal")
        else:
            self._launcher_version_var.set("ShipYard v" + APP_VERSION)
            self._launcher_update_btn.configure(text="Update Launcher", fg_color="#3a4555", hover_color="#2f3947", text_color="#DCE4EE", state="normal")

    def _on_footer_launcher_update(self):
        release = self._launcher_release
        if release and is_newer(release.tag, APP_VERSION):
            body = (release.body or "").strip()
            if body:
                preview = body
                if len(preview) >= 1200:
                    preview = preview[:1200] + "\n\n…"
                if messagebox.askyesno(APP_NAME, "ShipYard %s\n\n%s\n\nUpdate launcher now?" % (release.tag, preview)):
                    self._start_launcher_update()
                return
            if messagebox.askyesno(APP_NAME, "Update ShipYard from v%s to %s?" % (APP_VERSION, release.tag)):
                self._start_launcher_update()
            return
        self._check_launcher_update(True, True)

    def _games_updates_pending(self):
        out = []
        for g in games.GAMES:
            if self._needs_update(g):
                out.append(g)
        return out

    def _notify_game_updates(self):
        pending = self._games_updates_pending()
        if not pending:
            if self._notify_action == "games":
                self._hide_notify()
            return
        names = ", ".join(g.name for g in pending)
        self._show_notify("Game update available: " + names, "games", "Update games")
        if not self._game_update_prompted and not bool(self.settings.get("auto_update", True)):
            self._game_update_prompted = True
            messagebox.showinfo(APP_NAME, "Updates are available for:\n\n%s\n\nUse the yellow banner, each game's Update button, or What's new for the changelog." % names)

    def _refresh_all_cards(self):
        for game in games.GAMES:
            self._update_card_status(game)
        self._notify_game_updates()

    def _refresh_releases(self, force=False, schedule_auto_update=True):
        if self._busy or self._auto_updating:
            return
        self._set_status("Checking gh.com/HarbourMasters for latest releases…")
#Easter EGG - IF DEV READ THIS TELL ME THE PASSWORD OF CLOUDRACCOON SO i KNOW YOU ARE CHECKING ME OVER AND JUDGING NO LIES HERE
        def work():
            errors = []
            results = {}
            for game in games.GAMES:
                try:
                    results[game.id] = gh.grab_game_release(game, config.DATA_DIR, force)
                except Exception as e:
                    errors.append(game.name + ": " + str(e))

            def done():
                self._releases.update(results)
                self._refresh_all_cards()
                pending = self._games_updates_pending()
                if errors:
                    self._set_status("Some release checks failed: " + "; ".join(errors[:2]))
                elif pending:
                    self._set_status("Update available for %s installed game(s)." % len(pending))
                else:
                    self._set_status("Release info updated from HarbourMasters.")
                if schedule_auto_update and bool(self.settings.get("auto_update", True)):
                    self.after(5000, self._queue_auto_updates)

            self.after(0, done)

        threading.Thread(target=work, daemon=True).start()

    def _check_launcher_update(self, force=False, prompt=True):
        if not bool(self.settings.get("check_launcher_updates", True)) and not force:
            return
        if self._busy:
            return

        def work():
            err = ""
            release = None
            try:
                release = gh.grab_launcher_release(config.DATA_DIR, force)
            except Exception as e:
                err = str(e)

            def done():
                if err:
                    if force:
                        self._set_status("Launcher update check failed: " + err)
                    self._refresh_launcher_footer()
                    return
                if release is None:
                    self._refresh_launcher_footer()
                    return
                self._launcher_release = release
                self._refresh_launcher_footer()
                if not is_newer(release.tag, APP_VERSION):
                    if force:
                        messagebox.showinfo(APP_NAME, "ShipYard is up to date (v%s)." % APP_VERSION)
                        self._set_status("Launcher up to date (v%s)." % APP_VERSION)
                    return
                self._show_notify("ShipYard update available: %s (you have v%s)" % (release.tag, APP_VERSION), "launcher", "Update launcher")
                self._set_status("Launcher update available: " + release.tag)
                if prompt and not self._launcher_prompted:
                    self._launcher_prompted = True
                    body = (release.body or "").strip()
                    extra = ""
                    if body:
                        extra = "\n\n" + body[:800]
                        if len(body) > 800:
                            extra += "…"
                    if messagebox.askyesno(APP_NAME, "A new ShipYard is available: %s\n\nYou are on v%s.%s\n\nUpdate now from the launcher?" % (release.tag, APP_VERSION, extra)):
                        self._start_launcher_update()

            self.after(0, done)

        threading.Thread(target=work, daemon=True).start()

    def _start_launcher_update(self):
        release = self._launcher_release
        if release is None or release.asset is None:
            messagebox.showwarning(APP_NAME, "No downloadable launcher package found on the latest release.")
            return
        if not getattr(sys, "frozen", False):
            messagebox.showinfo(APP_NAME, "Self-update runs from the built ShipYard.exe.\nOpen the release page instead:\n" + (release.html_url or ""))
            if release.html_url:
                webbrowser.open(release.html_url)
            return
        if self._busy:
            return
        self._busy = True
        self._set_status("Updating ShipYard to %s…" % release.tag)

        def work():
            err = None
            try:
                gh.do_self_update(release.asset, config.DATA_DIR / "downloads", lambda msg: self.after(0, lambda m=msg: self._set_status(m)))
            except Exception as e:
                err = e

            def done():
                self._busy = False
                if err is not None:
                    messagebox.showerror(APP_NAME, "Launcher update failed:\n" + str(err))
                    self._set_status("Launcher update failed: " + str(err))
                    return
                self.destroy()

            self.after(0, done)

        threading.Thread(target=work, daemon=True).start()

    def _queue_auto_updates(self):
        # line up outdated games and install them one at a time, IF ALL AT ONCE WEELLL YOU BROKE IT OR LAGGED IT
        pending = []
        for g in games.GAMES:
            if self._needs_update(g):
                pending.append(g)
        if not pending:
            return
        already = set()
        for g in self._update_queue:
            already.add(g.id)
        for game in pending:
            if game.id not in already:
                self._update_queue.append(game)
        names = ", ".join(g.name for g in pending)
        self._set_status("New builds found — auto-updating: " + names)
        if not self._auto_updating:
            self._process_update_queue()

    def _process_update_queue(self):
        if not self._update_queue:
            self._auto_updating = False
            self._set_status("All installed games are up to date.")
            return
        if self._busy:
            return
        self._auto_updating = True
        game = self._update_queue.pop(0)
        self._install_game(game, True)

    def _launch_game(self, game):
        exe = self._exe_for(game)
        if not exe:
            messagebox.showwarning(APP_NAME, game.name + " is not installed. Use Install / Update or Browse.")
            return
        try:
            dl.run_game(exe)
            self._set_status("Launched " + game.name)
        except Exception as e:
            messagebox.showerror(APP_NAME, str(e))

    def _open_game_folder(self, game):
        entry = self._install_record(game.id)
        path = Path(str(entry.get("install_dir", "") or entry.get("exe_path", "")))
        if not path.exists():
            path = Path(self.library_var.get().strip() or r"D:\ShipYard") / game.id
        try:
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
            dl.open_in_explorer(path)
        except Exception as e:
            messagebox.showerror(APP_NAME, str(e))

    def _browse_game(self, game):
        initial = self._install_record(game.id).get("install_dir") or self.library_var.get()
        path = filedialog.askdirectory(title="Select %s install folder" % game.name, initialdir=initial or None)
        if not path:
            return
        folder = Path(path)
        exe = games.hunt_exe(folder, game.preferred_exes)
        if not exe:
            messagebox.showwarning(APP_NAME, "No matching executable found in:\n%s\n\nLooked for: %s" % (folder, ", ".join(game.preferred_exes)))
            return
        self.installs = config.remember_install(
            self.installs,
            game.id,
            str(exe.parent),
            str(exe),
            str(self._install_record(game.id).get("version_tag", "")),
        )
        self._update_card_status(game)
        self._set_status("Linked %s → %s" % (game.name, exe))
        if bool(self.settings.get("auto_update", True)) and self._needs_update(game):
            self._queue_auto_updates()

    def _install_game(self, game, auto=False):
        # Install and Update both land here. auto=True means the queue kicked it off.
        if self._busy:
            if auto and game not in self._update_queue:
                self._update_queue.append(game)
            return
        self._busy = True
        card = self._cards[game.id]
        card.set_busy(True)
        if auto:
            self._set_status("Auto-updating " + game.name + "…")
        else:
            self._set_status("Installing " + game.name + "…")

        library_root = Path(self.library_var.get().strip() or r"D:\ShipYard")
        self.settings["library_root"] = str(library_root)
        config.save_settings(self.settings)

        def progress(msg):
            self.after(0, lambda m=msg: self._set_status(game.name + ": " + m))

        def work():
            err = None
            install_dir = None
            exe = None
            tag = ""
            try:
                release = gh.grab_game_release(game, config.DATA_DIR, False)
                self._releases[game.id] = release
                if not release.windows_zip:
                    raise RuntimeError("No Windows zip found on the latest release for " + game.name + ".")
                tag = release.tag
                install_dir, exe = dl.yank_and_install(
                    game,
                    release.windows_zip,
                    library_root,
                    config.DATA_DIR / "downloads",
                    tag,
                    progress,
                )
            except Exception as e:
                err = e

            def done():
                self._busy = False
                card.set_busy(False)
                if err:
                    if not auto:
                        messagebox.showerror(APP_NAME, str(err))
                    self._set_status("Failed: " + str(err))
                    self._update_card_status(game)
                    if auto:
                        self._process_update_queue()
                    return
                self.installs = config.remember_install(self.installs, game.id, str(install_dir), str(exe), tag)
                self._update_card_status(game)
                if auto:
                    self._set_status("Updated %s (%s)" % (game.name, tag))
                else:
                    self._set_status("Installed %s (%s)" % (game.name, tag))
                if auto and game.id == "archipelago_soh" and bool(self.settings.get("auto_update_apworld", True)):
                    self._maybe_auto_apworld(game)
                if auto:
                    self._process_update_queue()

            self.after(0, done)

        threading.Thread(target=work, daemon=True).start()

    def _maybe_auto_apworld(self, game):
        dest = str(self.settings.get("archipelago_custom_worlds", "")).strip()
        if not dest:
            return
        release = self._releases.get(game.id)
        asset = None
        if release:
            asset = release.extras.get("oot_soh.apworld")
        if not asset:
            return
        dest_path = Path(dest)

        def progress(msg):
            self.after(0, lambda m=msg: self._set_status(m))

        def work():
            try:
                out = dl.grab_extra(asset, dest_path, progress)
                self.after(0, lambda: self._set_status("Updated apworld → " + str(out)))
            except Exception as e:
                self.after(0, lambda: self._set_status("apworld update failed: " + str(e)))

        threading.Thread(target=work, daemon=True).start()

    def _download_apworld(self, game):
        if game.id != "archipelago_soh":
            return
        if self._busy:
            return

        dest = str(self.settings.get("archipelago_custom_worlds", "")).strip()
        if not dest:
            dest = filedialog.askdirectory(title="Select Archipelago custom worlds folder")
            if not dest:
                return
            self.settings["archipelago_custom_worlds"] = dest
            config.save_settings(self.settings)

        dest_path = Path(dest)
        self._busy = True
        self._set_status("Downloading oot_soh.apworld…")

        def progress(msg):
            self.after(0, lambda m=msg: self._set_status(m))

        def work():
            err = None
            out = None
            try:
                release = gh.grab_game_release(game, config.DATA_DIR, False)
                self._releases[game.id] = release
                asset = release.extras.get("oot_soh.apworld")
                if not asset:
                    raise RuntimeError("oot_soh.apworld not found on the latest Archipelago-SoH release.")
                out = dl.grab_extra(asset, dest_path, progress)
            except Exception as e:
                err = e

            def done():
                self._busy = False
                if err:
                    messagebox.showerror(APP_NAME, str(err))
                    self._set_status("Failed: " + str(err))
                    return
                self._set_status("Saved apworld to " + str(out))
                messagebox.showinfo(APP_NAME, "Saved:\n" + str(out))

            self.after(0, done)

        threading.Thread(target=work, daemon=True).start()

    def _on_close(self):
        # remember window size + library path so next launch is user custom because I got annoyed having to hit full screen each time it was annoying.
        if self._header_job is not None:
            try:
                self.after_cancel(self._header_job)
            except Exception:
                pass
        self.settings["window_geometry"] = self.geometry()
        self.settings["library_root"] = self.library_var.get().strip()
        config.save_settings(self.settings)
        self.destroy()


def run():
    # main.py calls this so it makes the app work near 99.9% of the time
    app = App()
    app.mainloop()

#remeber to use close brackets at the end of fiel to make codes readbale work as i fudged alot up with basics
