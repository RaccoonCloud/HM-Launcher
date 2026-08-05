from __future__ import annotations

import threading
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Any

import customtkinter as ctk
import tkinter as tk

from app import branding, catalog, github, icons, install, launch, settings
from app.catalog import GameDef

APP_NAME = "HarbourMaster"

# Nautical-adjacent dark theme
ACCENT = "#1a8a8a"
ACCENT_HOVER = "#147070"
BG = "#12161c"
PANEL = "#1a222c"
CARD = "#222b36"
TEXT = "#e6edf3"
MUTED = "#8b9aab"

# Re-check GitHub while the launcher stays open (matches release cache TTL)
PERIODIC_CHECK_MS = 60 * 60 * 1000

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class GameCard(ctk.CTkFrame):
    def __init__(
        self,
        master: Any,
        game: GameDef,
        *,
        on_launch: Any,
        on_install: Any,
        on_browse: Any,
        on_folder: Any,
        on_apworld: Any | None = None,
        icon_image: ctk.CTkImage | None = None,
    ) -> None:
        super().__init__(master, fg_color=CARD, corner_radius=10)
        self.game = game
        self._icon_ref: ctk.CTkImage | None = icon_image
        self.grid_columnconfigure(1, weight=1)

        icon_wrap = ctk.CTkFrame(self, fg_color="transparent", width=84, height=84)
        icon_wrap.grid(row=0, column=0, rowspan=4, padx=(12, 4), pady=12, sticky="nw")
        icon_wrap.grid_propagate(False)
        self._icon_label = ctk.CTkLabel(icon_wrap, text="")
        self._icon_label.place(relx=0.5, rely=0.5, anchor="center")
        if self._icon_ref is not None:
            self._icon_label.configure(image=self._icon_ref, text="")
        else:
            self._icon_label.configure(text="…", text_color=MUTED, font=ctk.CTkFont(size=18, weight="bold"))

        title = ctk.CTkLabel(
            self,
            text=game.name,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=TEXT,
            anchor="w",
        )
        title.grid(row=0, column=1, sticky="ew", padx=(4, 14), pady=(12, 0))

        self.blurb = ctk.CTkLabel(
            self,
            text=game.blurb,
            font=ctk.CTkFont(size=12),
            text_color=MUTED,
            anchor="w",
        )
        self.blurb.grid(row=1, column=1, sticky="ew", padx=(4, 14), pady=(2, 0))

        self.status_var = ctk.StringVar(value="Checking…")
        self.status = ctk.CTkLabel(
            self,
            textvariable=self.status_var,
            font=ctk.CTkFont(size=12),
            text_color=TEXT,
            anchor="w",
        )
        self.status.grid(row=2, column=1, sticky="ew", padx=(4, 14), pady=(8, 0))

        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.grid(row=3, column=1, sticky="ew", padx=(0, 10), pady=(10, 12))

        self.launch_btn = ctk.CTkButton(
            btns,
            text="Launch",
            width=90,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            command=lambda: on_launch(game),
        )
        self.launch_btn.pack(side="left", padx=4)

        self.install_btn = ctk.CTkButton(
            btns,
            text="Install / Update",
            width=130,
            command=lambda: on_install(game),
        )
        self.install_btn.pack(side="left", padx=4)

        ctk.CTkButton(btns, text="Browse", width=80, command=lambda: on_browse(game)).pack(
            side="left", padx=4
        )
        ctk.CTkButton(btns, text="Folder", width=80, command=lambda: on_folder(game)).pack(
            side="left", padx=4
        )

        if game.id == "archipelago_soh" and on_apworld:
            self.apworld_btn = ctk.CTkButton(
                btns,
                text="Get apworld",
                width=110,
                command=lambda: on_apworld(game),
            )
            self.apworld_btn.pack(side="left", padx=4)

    def set_icon(self, image: ctk.CTkImage) -> None:
        self._icon_ref = image
        self._icon_label.configure(image=image, text="")

    def set_busy(self, busy: bool) -> None:
        state = "disabled" if busy else "normal"
        self.launch_btn.configure(state=state)
        self.install_btn.configure(state=state)


class App(ctk.CTk):
    SPLASH_MIN_MS = 2500  # show animation, then get out of the way

    def __init__(self) -> None:
        super().__init__()
        self.title(APP_NAME)
        self.configure(fg_color=BG)
        self.settings = settings.load_settings()
        self.installs = settings.load_installs()
        self.geometry(self.settings.get("window_geometry", "980x720"))
        self.minsize(860, 600)

        self._releases: dict[str, github.LatestRelease] = {}
        self._busy = False
        self._cards: dict[str, GameCard] = {}
        self._update_queue: list[GameDef] = []
        self._auto_updating = False
        self._splash_photos: list = []
        self._header_photos: list = []
        self._game_ctk_icons: dict[str, ctk.CTkImage] = {}
        self._anim_idx = 0
        self._splash_job: str | None = None
        self._header_job: str | None = None
        self._header_icon: ctk.CTkImage | None = None
        self._splash_started_at = 0.0
        self._boot_ready = False
        self._main_ready = False

        branding.apply_window_icon(self)
        settings.ensure_dirs()
        self._show_splash()
        self.after(1, self._start_splash_animation)
        self.after(1, self._boot_async)

    def _start_splash_animation(self) -> None:
        import time

        self._splash_photos = branding.load_prebaked_photos(branding.ANIM_SPLASH)
        # Fewer header frames = less CPU while using the launcher
        self._header_photos = branding.load_prebaked_photos(branding.ANIM_HEADER, max_frames=18)
        if not self._splash_photos:
            static = branding.load_static_photo((256, 256))
            if static:
                self._splash_photos = [static]
        if self._splash_photos:
            self._splash_label.configure(image=self._splash_photos[0])
            self._splash_started_at = time.monotonic()
            self._anim_idx = 0
            self._animate_splash()
            if hasattr(self, "_splash_status"):
                self._splash_status.configure(text="Starting HarbourMaster…")

    def _show_splash(self) -> None:
        """Animated Harbour Masters mark while the app boots."""
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
        ctk.CTkLabel(
            center,
            text=APP_NAME,
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=TEXT,
        ).pack(pady=(0, 4))
        self._splash_status = ctk.CTkLabel(center, text="Loading…", text_color=MUTED)
        self._splash_status.pack(pady=(0, 24))

        photo = branding.load_static_photo((256, 256))
        if photo:
            self._splash_photos = [photo]
            self._splash_label.configure(image=photo)

    def _animate_splash(self) -> None:
        if not self._splash_photos:
            return
        frame = self._splash_photos[self._anim_idx % len(self._splash_photos)]
        try:
            self._splash_label.configure(image=frame)
        except Exception:  # noqa: BLE001
            return
        self._anim_idx += 1
        self._splash_job = self.after(50, self._animate_splash)

    def _stop_splash(self) -> None:
        if self._splash_job is not None:
            try:
                self.after_cancel(self._splash_job)
            except Exception:  # noqa: BLE001
                pass
            self._splash_job = None
        if hasattr(self, "_splash") and self._splash.winfo_exists():
            self._splash.destroy()
        self._splash_photos = []

    def _boot_async(self) -> None:
        def work() -> None:
            try:
                # Warm icon cache during splash so UI build stays snappy
                icons.preload_all(size=(72, 72))
                self._seed_hint_installs()
            finally:
                self.after(0, self._on_boot_work_done)

        if hasattr(self, "_splash_status"):
            self._splash_status.configure(text="Preparing games…")
        threading.Thread(target=work, daemon=True).start()

    def _on_boot_work_done(self) -> None:
        self._boot_ready = True
        if hasattr(self, "_splash_status"):
            self._splash_status.configure(text="Ready…")
        self._maybe_finish_boot()

    def _maybe_finish_boot(self) -> None:
        import time

        if not self._boot_ready:
            return
        started = self._splash_started_at or time.monotonic()
        elapsed_ms = (time.monotonic() - started) * 1000
        remaining_ms = int(max(0, self.SPLASH_MIN_MS - elapsed_ms))
        if remaining_ms > 0:
            self.after(remaining_ms, self._finish_boot)
        else:
            self._finish_boot()

    def _finish_boot(self) -> None:
        if self._main_ready:
            return
        self._main_ready = True
        self._stop_splash()
        # Drop any leftover splash children / row weight before building the shell
        for child in list(self.winfo_children()):
            try:
                child.destroy()
            except Exception:  # noqa: BLE001
                pass
        self._apply_disk_caches()
        self._build()
        branding.apply_window_icon(self)
        self.after(100, lambda: branding.apply_window_icon(self))
        self._start_header_animation()
        # Attach game icons one-per-tick so the shell stays clickable immediately
        self.after(20, lambda: self._attach_game_icons(0))
        # GitHub can wait — statuses already came from disk cache
        self.after(12000, lambda: self._refresh_releases(force=False, schedule_auto_update=False))
        self.after(PERIODIC_CHECK_MS, self._periodic_check)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _apply_disk_caches(self) -> None:
        for game in catalog.GAMES:
            cached = github.read_cached_release(game, settings.DATA_DIR, allow_stale=True)
            if cached is not None:
                self._releases[game.id] = cached

    def _attach_game_icons(self, index: int = 0) -> None:
        games = [g for g in catalog.GAMES if g.icon_file]
        if index >= len(games):
            return
        game = games[index]
        if game.id not in self._game_ctk_icons:
            pil = icons.load_pil(game.icon_file, size=(72, 72))
            if pil is not None:
                img = ctk.CTkImage(light_image=pil, dark_image=pil, size=(72, 72))
                self._game_ctk_icons[game.id] = img
                card = self._cards.get(game.id)
                if card is not None:
                    card.set_icon(img)
        self.after(1, lambda: self._attach_game_icons(index + 1))

    def _start_header_animation(self) -> None:
        if not self._header_photos or not hasattr(self, "_header_label"):
            return
        self._anim_idx = 0

        def tick() -> None:
            if not self._header_photos:
                return
            try:
                self._header_label.configure(
                    image=self._header_photos[self._anim_idx % len(self._header_photos)]
                )
            except Exception:  # noqa: BLE001
                return
            self._anim_idx += 1
            # Slower loop — less UI jank while scrolling/clicking
            self._header_job = self.after(90, tick)

        tick()

    def _seed_hint_installs(self) -> None:
        changed = False
        for game in catalog.GAMES:
            entry = self.installs.get(game.id) or {}
            exe_path = Path(str(entry.get("exe_path", "")))
            if exe_path.is_file():
                continue
            hinted = catalog.discover_hint_install(game)
            if not hinted:
                continue
            exe = catalog.find_exe_in_dir(hinted, game.preferred_exes)
            if not exe:
                continue
            self.installs = settings.set_install(
                self.installs,
                game.id,
                install_dir=str(exe.parent),
                exe_path=str(exe),
                version_tag=str(entry.get("version_tag", "")),
            )
            changed = True
        if changed:
            self.installs = settings.load_installs()

    def _build(self) -> None:
        # Splash left row 0 weighted — reset so the header stays compact
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)

        top = ctk.CTkFrame(self, fg_color=PANEL, corner_radius=0)
        top.grid(row=0, column=0, sticky="ew")
        top.grid_columnconfigure(1, weight=1)

        brand = ctk.CTkFrame(top, fg_color="transparent")
        brand.grid(row=0, column=0, padx=(12, 8), pady=4, sticky="w")
        # Continuous animated GIF mark (Desktop EXE icons cannot animate on Windows)
        self._header_label = tk.Label(brand, text="", bg=PANEL, bd=0, highlightthickness=0)
        self._header_label.pack(side="left", padx=(0, 8))
        if self._header_photos:
            self._header_label.configure(image=self._header_photos[0])
        elif branding.LOGO_PNG.is_file():
            from PIL import Image, ImageTk

            pil = Image.open(branding.LOGO_PNG).convert("RGBA").resize((40, 40), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(pil)
            self._header_photos = [photo]
            self._header_label.configure(image=photo)
        ctk.CTkLabel(
            brand,
            text=APP_NAME,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=TEXT,
        ).pack(side="left")

        self.library_var = ctk.StringVar(value=str(self.settings.get("library_root", "")))
        lib_row = ctk.CTkFrame(top, fg_color="transparent")
        lib_row.grid(row=0, column=1, sticky="ew", padx=8, pady=4)
        lib_row.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(lib_row, text="Library", text_color=MUTED).grid(row=0, column=0, padx=(0, 6))
        ctk.CTkEntry(lib_row, textvariable=self.library_var, height=28).grid(
            row=0, column=1, sticky="ew"
        )
        ctk.CTkButton(lib_row, text="…", width=36, height=28, command=self._pick_library).grid(
            row=0, column=2, padx=(6, 0)
        )

        ctk.CTkButton(
            top,
            text="Refresh",
            width=90,
            height=28,
            command=lambda: self._refresh_releases(True, schedule_auto_update=True),
        ).grid(row=0, column=2, padx=6, pady=4)
        ctk.CTkButton(top, text="Settings", width=90, height=28, command=self._open_settings).grid(
            row=0, column=3, padx=(6, 12), pady=4
        )

        scroll = ctk.CTkScrollableFrame(self, fg_color=BG)
        scroll.grid(row=1, column=0, sticky="nsew", padx=10, pady=(4, 4))
        scroll.grid_columnconfigure(0, weight=1)

        for i, game in enumerate(catalog.GAMES):
            card = GameCard(
                scroll,
                game,
                on_launch=self._launch_game,
                on_install=self._install_game,
                on_browse=self._browse_game,
                on_folder=self._open_game_folder,
                on_apworld=self._download_apworld,
                icon_image=self._game_ctk_icons.get(game.id),
            )
            card.grid(row=i, column=0, sticky="ew", pady=(0, 4))
            self._cards[game.id] = card
            self._update_card_status(game)

        foot = ctk.CTkFrame(self, fg_color=PANEL, corner_radius=0)
        foot.grid(row=2, column=0, sticky="ew")
        foot.grid_columnconfigure(0, weight=1)
        self.status_var = ctk.StringVar(
            value="Tracks latest releases from github.com/HarbourMasters. Provide your own legal ROMs."
        )
        ctk.CTkLabel(
            foot,
            textvariable=self.status_var,
            text_color=MUTED,
            anchor="w",
            font=ctk.CTkFont(size=12),
        ).grid(row=0, column=0, sticky="ew", padx=(16, 8), pady=8)

        self._discord_icon = branding.load_discord_ctk_image((24, 24))
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
        discord_btn.grid(row=0, column=1, padx=(0, 12), pady=6, sticky="e")

    def _set_status(self, text: str) -> None:
        self.status_var.set(text)

    def _open_discord(self) -> None:
        webbrowser.open(branding.DISCORD_URL)

    def _periodic_check(self) -> None:
        if not self._busy and not self._auto_updating:
            self._refresh_releases(force=False, schedule_auto_update=True)
        self.after(PERIODIC_CHECK_MS, self._periodic_check)

    def _pick_library(self) -> None:
        path = filedialog.askdirectory(title="Library root", initialdir=self.library_var.get() or None)
        if path:
            self.library_var.set(path)
            self.settings["library_root"] = path
            settings.save_settings(self.settings)

    def _open_settings(self) -> None:
        win = ctk.CTkToplevel(self)
        win.title("Settings")
        win.geometry("560x420")
        win.transient(self)
        win.grab_set()

        ctk.CTkLabel(win, text="Library root").pack(anchor="w", padx=16, pady=(16, 4))
        lib_var = ctk.StringVar(value=str(self.settings.get("library_root", "")))
        ctk.CTkEntry(win, textvariable=lib_var, width=500).pack(padx=16, fill="x")

        ctk.CTkLabel(win, text="Archipelago custom worlds folder (for oot_soh.apworld)").pack(
            anchor="w", padx=16, pady=(16, 4)
        )
        ap_var = ctk.StringVar(value=str(self.settings.get("archipelago_custom_worlds", "")))
        ap_row = ctk.CTkFrame(win, fg_color="transparent")
        ap_row.pack(fill="x", padx=16)
        ctk.CTkEntry(ap_row, textvariable=ap_var).pack(side="left", fill="x", expand=True)

        def pick_ap() -> None:
            path = filedialog.askdirectory(title="Archipelago custom worlds")
            if path:
                ap_var.set(path)

        ctk.CTkButton(ap_row, text="…", width=36, command=pick_ap).pack(side="left", padx=(6, 0))

        auto_var = ctk.BooleanVar(value=bool(self.settings.get("auto_update", True)))
        ctk.CTkCheckBox(
            win,
            text="Auto-update installed games when HarbourMasters publishes a new release",
            variable=auto_var,
        ).pack(anchor="w", padx=16, pady=(18, 4))

        apworld_var = ctk.BooleanVar(value=bool(self.settings.get("auto_update_apworld", True)))
        ctk.CTkCheckBox(
            win,
            text="Also auto-download oot_soh.apworld when Archipelago SoH updates",
            variable=apworld_var,
        ).pack(anchor="w", padx=16, pady=(4, 4))

        def save() -> None:
            self.settings["library_root"] = lib_var.get().strip()
            self.settings["archipelago_custom_worlds"] = ap_var.get().strip()
            self.settings["auto_update"] = bool(auto_var.get())
            self.settings["auto_update_apworld"] = bool(apworld_var.get())
            self.library_var.set(self.settings["library_root"])
            settings.save_settings(self.settings)
            win.destroy()
            self._set_status("Settings saved.")

        ctk.CTkButton(win, text="Save", fg_color=ACCENT, hover_color=ACCENT_HOVER, command=save).pack(
            pady=(20, 8)
        )
        ctk.CTkLabel(
            win,
            text="Created by RaccoonCloud for the Harbour Masters team and community",
            text_color=MUTED,
            font=ctk.CTkFont(size=12),
        ).pack(pady=(4, 16))

    def _install_record(self, game_id: str) -> dict[str, Any]:
        return dict(self.installs.get(game_id) or {})

    def _exe_for(self, game: GameDef) -> Path | None:
        entry = self._install_record(game.id)
        exe = Path(str(entry.get("exe_path", "")))
        if exe.is_file():
            return exe
        install_dir = Path(str(entry.get("install_dir", "")))
        if install_dir.is_dir():
            found = catalog.find_exe_in_dir(install_dir, game.preferred_exes)
            if found:
                return found
        return None

    def _needs_update(self, game: GameDef) -> bool:
        """True when this game is installed and latest stable tag differs."""
        if not self._exe_for(game):
            return False
        release = self._releases.get(game.id)
        if not release or not release.tag or not release.windows_zip:
            return False
        installed_tag = str(self._install_record(game.id).get("version_tag", "") or "")
        return installed_tag != release.tag

    def _update_card_status(self, game: GameDef) -> None:
        card = self._cards[game.id]
        entry = self._install_record(game.id)
        exe = self._exe_for(game)
        installed_tag = str(entry.get("version_tag", "") or "")
        release = self._releases.get(game.id)
        latest = release.tag if release else ""

        if not exe:
            status = "Not installed"
            if latest:
                status += f"  ·  latest {latest}"
        else:
            status = f"Ready  ·  {exe.name}"
            if installed_tag:
                status += f"  ·  installed {installed_tag}"
            if latest and installed_tag and latest != installed_tag:
                status += f"  ·  update available ({latest})"
            elif latest and not installed_tag:
                status += f"  ·  latest {latest} (will auto-update)"
            elif latest:
                status += "  ·  up to date"
        card.status_var.set(status)
        card.launch_btn.configure(state="normal" if exe else "disabled")

    def _refresh_all_cards(self) -> None:
        for game in catalog.GAMES:
            self._update_card_status(game)

    def _refresh_releases(
        self,
        force: bool = False,
        *,
        schedule_auto_update: bool = True,
    ) -> None:
        if self._busy or self._auto_updating:
            return
        self._set_status("Checking github.com/HarbourMasters for latest releases…")

        def work() -> None:
            errors: list[str] = []
            results: dict[str, github.LatestRelease] = {}
            for game in catalog.GAMES:
                try:
                    results[game.id] = github.fetch_latest_release(
                        game, settings.DATA_DIR, force=force
                    )
                except Exception as exc:  # noqa: BLE001
                    errors.append(f"{game.name}: {exc}")

            def done() -> None:
                self._releases.update(results)
                self._refresh_all_cards()
                if errors:
                    self._set_status("Some release checks failed: " + "; ".join(errors[:2]))
                else:
                    self._set_status("Release info updated from HarbourMasters.")
                if schedule_auto_update and bool(self.settings.get("auto_update", True)):
                    # Give the UI a beat before any download churn
                    self.after(5000, self._queue_auto_updates)

            self.after(0, done)

        threading.Thread(target=work, daemon=True).start()

    def _queue_auto_updates(self) -> None:
        pending = [g for g in catalog.GAMES if self._needs_update(g)]
        if not pending:
            return
        # Avoid stacking duplicate queue entries
        queued_ids = {g.id for g in self._update_queue}
        for game in pending:
            if game.id not in queued_ids:
                self._update_queue.append(game)
        names = ", ".join(g.name for g in pending)
        self._set_status(f"New builds found — auto-updating: {names}")
        if not self._auto_updating:
            self._process_update_queue()

    def _process_update_queue(self) -> None:
        if not self._update_queue:
            self._auto_updating = False
            self._set_status("All installed games are up to date.")
            return
        if self._busy:
            return
        self._auto_updating = True
        game = self._update_queue.pop(0)
        self._install_game(game, auto=True)

    def _launch_game(self, game: GameDef) -> None:
        exe = self._exe_for(game)
        if not exe:
            messagebox.showwarning(APP_NAME, f"{game.name} is not installed. Use Install / Update or Browse.")
            return
        try:
            launch.launch_exe(exe)
            self._set_status(f"Launched {game.name}")
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror(APP_NAME, str(exc))

    def _open_game_folder(self, game: GameDef) -> None:
        entry = self._install_record(game.id)
        path = Path(str(entry.get("install_dir", "") or entry.get("exe_path", "")))
        if not path.exists():
            lib = Path(self.library_var.get().strip() or r"D:\HarbourMaster") / game.id
            path = lib
        try:
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
            launch.open_folder(path)
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror(APP_NAME, str(exc))

    def _browse_game(self, game: GameDef) -> None:
        initial = self._install_record(game.id).get("install_dir") or self.library_var.get()
        path = filedialog.askdirectory(title=f"Select {game.name} install folder", initialdir=initial or None)
        if not path:
            return
        folder = Path(path)
        exe = catalog.find_exe_in_dir(folder, game.preferred_exes)
        if not exe:
            messagebox.showwarning(
                APP_NAME,
                f"No matching executable found in:\n{folder}\n\nLooked for: {', '.join(game.preferred_exes)}",
            )
            return
        self.installs = settings.set_install(
            self.installs,
            game.id,
            install_dir=str(exe.parent),
            exe_path=str(exe),
            version_tag=str(self._install_record(game.id).get("version_tag", "")),
        )
        self._update_card_status(game)
        self._set_status(f"Linked {game.name} → {exe}")
        if bool(self.settings.get("auto_update", True)) and self._needs_update(game):
            self._queue_auto_updates()

    def _install_game(self, game: GameDef, *, auto: bool = False) -> None:
        if self._busy:
            if auto and game not in self._update_queue:
                self._update_queue.append(game)
            return
        self._busy = True
        card = self._cards[game.id]
        card.set_busy(True)
        label = "Auto-updating" if auto else "Installing"
        self._set_status(f"{label} {game.name}…")

        library_root = Path(self.library_var.get().strip() or r"D:\HarbourMaster")
        self.settings["library_root"] = str(library_root)
        settings.save_settings(self.settings)

        def progress(msg: str) -> None:
            self.after(0, lambda m=msg: self._set_status(f"{game.name}: {m}"))

        def work() -> None:
            err: Exception | None = None
            install_dir: Path | None = None
            exe: Path | None = None
            tag = ""
            try:
                release = github.fetch_latest_release(game, settings.DATA_DIR, force=False)
                self._releases[game.id] = release
                if not release.windows_zip:
                    raise RuntimeError(
                        f"No Windows zip found on the latest release for {game.name}."
                    )
                tag = release.tag
                install_dir, exe = install.install_from_asset(
                    game,
                    release.windows_zip,
                    library_root=library_root,
                    downloads_dir=settings.DATA_DIR / "downloads",
                    version_tag=tag,
                    on_progress=progress,
                )
            except Exception as exc:  # noqa: BLE001
                err = exc

            def done() -> None:
                self._busy = False
                card.set_busy(False)
                if err:
                    if not auto:
                        messagebox.showerror(APP_NAME, str(err))
                    self._set_status(f"Failed: {err}")
                    self._update_card_status(game)
                    if auto:
                        self._process_update_queue()
                    return
                assert install_dir and exe
                self.installs = settings.set_install(
                    self.installs,
                    game.id,
                    install_dir=str(install_dir),
                    exe_path=str(exe),
                    version_tag=tag,
                )
                self._update_card_status(game)
                self._set_status(f"{'Updated' if auto else 'Installed'} {game.name} ({tag})")
                if (
                    auto
                    and game.id == "archipelago_soh"
                    and bool(self.settings.get("auto_update_apworld", True))
                ):
                    self._maybe_auto_apworld(game)
                if auto:
                    self._process_update_queue()

            self.after(0, done)

        threading.Thread(target=work, daemon=True).start()

    def _maybe_auto_apworld(self, game: GameDef) -> None:
        dest = str(self.settings.get("archipelago_custom_worlds", "")).strip()
        if not dest:
            return
        release = self._releases.get(game.id)
        asset = release.extras.get("oot_soh.apworld") if release else None
        if not asset:
            return
        dest_path = Path(dest)

        def progress(msg: str) -> None:
            self.after(0, lambda m=msg: self._set_status(m))

        def work() -> None:
            try:
                out = install.download_extra_asset(asset, dest_path, on_progress=progress)
                self.after(0, lambda: self._set_status(f"Updated apworld → {out}"))
            except Exception as exc:  # noqa: BLE001
                self.after(0, lambda: self._set_status(f"apworld update failed: {exc}"))

        threading.Thread(target=work, daemon=True).start()

    def _download_apworld(self, game: GameDef) -> None:
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
            settings.save_settings(self.settings)

        dest_path = Path(dest)
        self._busy = True
        self._set_status("Downloading oot_soh.apworld…")

        def progress(msg: str) -> None:
            self.after(0, lambda m=msg: self._set_status(m))

        def work() -> None:
            err: Exception | None = None
            out: Path | None = None
            try:
                release = github.fetch_latest_release(game, settings.DATA_DIR, force=False)
                self._releases[game.id] = release
                asset = release.extras.get("oot_soh.apworld")
                if not asset:
                    raise RuntimeError("oot_soh.apworld not found on the latest Archipelago-SoH release.")
                out = install.download_extra_asset(asset, dest_path, on_progress=progress)
            except Exception as exc:  # noqa: BLE001
                err = exc

            def done() -> None:
                self._busy = False
                if err:
                    messagebox.showerror(APP_NAME, str(err))
                    self._set_status(f"Failed: {err}")
                    return
                assert out
                self._set_status(f"Saved apworld to {out}")
                messagebox.showinfo(APP_NAME, f"Saved:\n{out}")

            self.after(0, done)

        threading.Thread(target=work, daemon=True).start()

    def _on_close(self) -> None:
        if self._header_job is not None:
            try:
                self.after_cancel(self._header_job)
            except Exception:  # noqa: BLE001
                pass
        self.settings["window_geometry"] = self.geometry()
        self.settings["library_root"] = self.library_var.get().strip()
        settings.save_settings(self.settings)
        self.destroy()


def run() -> None:
    app = App()
    app.mainloop()
