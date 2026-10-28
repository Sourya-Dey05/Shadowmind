# =============================================================================
# FILE: ui/tabs/settings_tab.py
# PURPOSE: Admin Settings tab — fully interactive controls for:
#          1. Light Mode / Dark Mode switching
#          2. Signal Detection Mode (Attack & Benign vs. Attack Only)
#          3. Last Exfiltration Telemetry Inspector (Time, IP, and Status)
# =============================================================================

import yaml
import customtkinter as ctk
from pathlib import Path
from src.auth.auth import Session
from src.utils.settings_state import AppSettings

from ui.theme import (
    COLOR_BG as C_BG,
    COLOR_CARD as C_PANEL,
    COLOR_CYAN as C_ACCENT,
    COLOR_TEXT_PRIMARY as C_TEXT,
    COLOR_TEXT_SECONDARY as C_SUBTEXT,
    COLOR_WARNING as C_WARNING,
    COLOR_BORDER as C_BORDER,
    COLOR_SURFACE as C_SURFACE,
    FONT_BRAND, FONT_MONO, FONT_BODY
)

from src.utils.path_helper import get_resource_path

CONFIG_PATH = get_resource_path("configs/thresholds.yaml")


class SettingsTab(ctk.CTkFrame):
    """
    Admin-only interactive settings panel.
    """

    def __init__(self, parent, session: Session):
        super().__init__(parent, fg_color=C_BG)
        self.session = session
        with open(CONFIG_PATH, "r") as f:
            self.cfg = yaml.safe_load(f)
        self._build()

    def tkraise(self, above_this=None):
        super().tkraise(above_this)
        self._refresh_audit_display()

    def _build(self):
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Left column: Interactive Controls (Theme, Signal Mode) ---
        left = ctk.CTkScrollableFrame(self, fg_color=C_BG)
        left.grid(row=0, column=0, padx=(12, 6), pady=12, sticky="nsew")
        left.grid_columnconfigure(0, weight=1)

        self._section(left, 0, "Telemetry & Detection Filtering")

        # Turn on/off signal detection every 2s (Attack Only vs All)
        signal_card = ctk.CTkFrame(left, fg_color=C_PANEL, corner_radius=6, border_width=1, border_color=C_BORDER)
        signal_card.grid(row=1, column=0, sticky="ew", padx=4, pady=4)
        signal_card.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(signal_card, text="Signal Display Mode", font=ctk.CTkFont(family=FONT_MONO, size=11), text_color=C_SUBTEXT).grid(row=0, column=0, padx=12, pady=10, sticky="w")
        
        self.signal_menu = ctk.CTkOptionMenu(
            signal_card, values=["Attack & Benign", "Attack Only (Hide Benign)"],
            command=self._on_signal_mode_changed,
            fg_color=C_SURFACE, button_color=C_ACCENT, button_hover_color="#38d4ff",
            text_color=C_TEXT, font=ctk.CTkFont(family=FONT_MONO, size=11)
        )
        self.signal_menu.set(AppSettings.signal_mode)
        self.signal_menu.grid(row=0, column=1, padx=12, pady=10, sticky="e")

        self._section(left, 2, "System Thresholds Reference")
        d = self.cfg["detection"]["risk_score"]
        self._row(left, 3, "Benign max score",      str(d["benign_max"]))
        self._row(left, 4, "Suspicious min score",  str(d["suspicious_min"]))
        self._row(left, 5, "Confirmed min score",   str(d["confirmed_min"]))

        # --- Right column: Last Exfiltration Telemetry Inspector ---
        right = ctk.CTkScrollableFrame(self, fg_color=C_BG)
        right.grid(row=0, column=1, padx=(6, 12), pady=12, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)

        self._section(right, 0, "Last Exfiltration Incident Audit")

        exfil_card = ctk.CTkFrame(right, fg_color=C_PANEL, corner_radius=8, border_width=1, border_color=C_BORDER)
        exfil_card.grid(row=1, column=0, sticky="ew", padx=4, pady=4)
        exfil_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(exfil_card, text="BREACH AUDIT TELEMETRY", font=ctk.CTkFont(family=FONT_MONO, size=11, weight="bold"), text_color=C_ACCENT).pack(anchor="w", padx=16, pady=(14, 4))
        
        self.time_lbl = ctk.CTkLabel(exfil_card, text=f"Timestamp: {AppSettings.last_exfil_time}", font=ctk.CTkFont(family=FONT_MONO, size=11), text_color=C_TEXT)
        self.time_lbl.pack(anchor="w", padx=16, pady=4)

        self.ip_lbl = ctk.CTkLabel(exfil_card, text=f"Attacker IP: {AppSettings.last_exfil_ip}", font=ctk.CTkFont(family=FONT_MONO, size=11), text_color=C_TEXT)
        self.ip_lbl.pack(anchor="w", padx=16, pady=4)

        self.status_lbl = ctk.CTkLabel(exfil_card, text=f"Status: {AppSettings.last_exfil_status}", font=ctk.CTkFont(family=FONT_MONO, size=11), text_color=C_WARNING)
        self.status_lbl.pack(anchor="w", padx=16, pady=(4, 14))

        refresh_audit_btn = ctk.CTkButton(
            exfil_card, text="🔄 REFRESH AUDIT LOG",
            command=self._refresh_audit_display,
            fg_color=C_SURFACE, hover_color=C_BORDER, text_color=C_TEXT,
            font=ctk.CTkFont(family=FONT_MONO, size=11), corner_radius=6, height=32
        )
        refresh_audit_btn.pack(padx=16, pady=(0, 16), fill="x")

        self._section(right, 2, "Vault & Honeypot Config")
        v = self.cfg["vault"]
        self._row(right, 3, "AES key bits",           str(v["aes_key_bits"]))
        self._row(right, 4, "Rotation on breach",     str(v["key_rotation_on_breach"]))
        self._row(right, 5, "TTL wipe on logoff",     str(v["ttl_wipe_on_logoff"]))

        h = self.cfg["honeypot"]
        self._row(right, 6, "Honeypot Enabled",       str(h["enabled"]))
        self._row(right, 7, "Decoy count",            str(h["decoy_count"]))

    def _on_theme_changed(self, choice: str):
        AppSettings.theme_mode = choice
        if choice == "Light":
            ctk.set_appearance_mode("light")
        else:
            ctk.set_appearance_mode("dark")

    def _on_signal_mode_changed(self, choice: str):
        AppSettings.signal_mode = choice

    def _refresh_audit_display(self):
        self.time_lbl.configure(text=f"Timestamp: {AppSettings.last_exfil_time}")
        self.ip_lbl.configure(text=f"Attacker IP: {AppSettings.last_exfil_ip}")
        self.status_lbl.configure(text=f"Status: {AppSettings.last_exfil_status}")

    def _section(self, parent, row: int, title: str):
        ctk.CTkLabel(
            parent, text=title.upper(),
            font=ctk.CTkFont(family=FONT_MONO, size=11, weight="bold"), text_color=C_ACCENT
        ).grid(row=row, column=0, sticky="w", padx=8, pady=(16, 4))

    def _row(self, parent, row: int, label: str, value: str):
        f = ctk.CTkFrame(parent, fg_color=C_PANEL, corner_radius=6, border_width=1, border_color=C_BORDER)
        f.grid(row=row, column=0, sticky="ew", padx=4, pady=2)
        f.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(f, text=label, font=ctk.CTkFont(family=FONT_MONO, size=11),
                     text_color=C_SUBTEXT, width=180, anchor="w").grid(
            row=0, column=0, padx=10, pady=6, sticky="w")
        ctk.CTkLabel(f, text=value, font=ctk.CTkFont(family=FONT_MONO, size=11),
                     text_color=C_TEXT, anchor="w").grid(
            row=0, column=1, padx=10, pady=6, sticky="w")
