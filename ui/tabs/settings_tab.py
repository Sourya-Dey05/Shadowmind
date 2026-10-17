# =============================================================================
# FILE: ui/tabs/settings_tab.py
# PURPOSE: Settings tab — ADMIN ONLY. Exposes editable controls for detection
#          thresholds, TTL duration, monitored file extensions, honeypot toggle,
#          and logging level. In Phase 0 all fields display the current values
#          from configs/thresholds.yaml but writes are disabled (read-only
#          preview). Phase 6 will wire in live config persistence. Admin role
#          is enforced by main_window.py — this tab is never shown to USER role.
# =============================================================================

import yaml
import customtkinter as ctk
from pathlib import Path
from src.auth.auth import Session

C_BG      = "#0d0f14"
C_PANEL   = "#13161e"
C_ACCENT  = "#00c8ff"
C_TEXT    = "#e0e0e0"
C_SUBTEXT = "#888888"
C_WARNING = "#ffaa00"

CONFIG_PATH = Path(__file__).resolve().parents[3] / "configs" / "thresholds.yaml"


def _load_cfg() -> dict:
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


class SettingsTab(ctk.CTkFrame):
    """
    Admin-only settings panel. Displays current config values.
    Write support added in Phase 6.
    """

    def __init__(self, parent, session: Session):
        super().__init__(parent, fg_color=C_BG)
        self.session = session
        self.cfg = _load_cfg()
        self._build()

    def _build(self):
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Left column ---
        left = ctk.CTkScrollableFrame(self, fg_color=C_BG)
        left.grid(row=0, column=0, padx=(12, 6), pady=12, sticky="nsew")
        left.grid_columnconfigure(0, weight=1)

        self._section(left, 0, "Detection Thresholds")
        d = self.cfg["detection"]["risk_score"]
        self._row(left, 1, "Benign max score",      str(d["benign_max"]))
        self._row(left, 2, "Suspicious min score",  str(d["suspicious_min"]))
        self._row(left, 3, "Confirmed min score",   str(d["confirmed_min"]))

        self._section(left, 4, "Authentication")
        a = self.cfg["auth"]
        self._row(left, 5, "Max login attempts",    str(a["max_login_attempts"]))
        self._row(left, 6, "Lockout duration (s)",  str(a["lockout_duration_seconds"]))
        self._row(left, 7, "Session TTL (s)",       str(a["session_ttl_seconds"]))
        self._row(left, 8, "Min password length",   str(a["min_password_length"]))

        self._section(left, 9, "Slow Exfil Detection")
        s = self.cfg["detection"]["slow_exfil"]
        self._row(left, 10, "Max beacon packet (KB)", str(s["max_packet_kb"]))
        self._row(left, 11, "Off-hours start (hr)",   str(s["off_hours_start"]))
        self._row(left, 12, "Off-hours end (hr)",     str(s["off_hours_end"]))

        # --- Right column ---
        right = ctk.CTkScrollableFrame(self, fg_color=C_BG)
        right.grid(row=0, column=1, padx=(6, 12), pady=12, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)

        self._section(right, 0, "Vault")
        v = self.cfg["vault"]
        self._row(right, 1, "AES key bits",           str(v["aes_key_bits"]))
        self._row(right, 2, "Rotation on breach",     str(v["key_rotation_on_breach"]))
        self._row(right, 3, "Rotation timeout (ms)",  str(v["rotation_timeout_ms"]))
        self._row(right, 4, "TTL wipe on logoff",     str(v["ttl_wipe_on_logoff"]))

        self._section(right, 5, "Honeypot")
        h = self.cfg["honeypot"]
        self._row(right, 6, "Enabled",                str(h["enabled"]))
        self._row(right, 7, "Decoy count",            str(h["decoy_count"]))
        self._row(right, 8, "Redirect on suspicious", str(h["redirect_on_suspicious"]))

        self._section(right, 9, "Logging")
        lg = self.cfg["logging"]
        self._row(right, 10, "Level",        lg["level"])
        self._row(right, 11, "Log to file",  str(lg["log_to_file"]))
        self._row(right, 12, "Log path",     lg["log_path"])

        # Notice
        notice = ctk.CTkFrame(self, fg_color=C_PANEL, corner_radius=8)
        notice.grid(row=1, column=0, columnspan=2, padx=12, pady=(0, 12), sticky="ew")
        ctk.CTkLabel(
            notice,
            text="Settings editing will be enabled in Phase 6. Edit configs/thresholds.yaml directly until then.",
            font=ctk.CTkFont(size=11), text_color=C_WARNING
        ).pack(padx=16, pady=10)

    def _section(self, parent, row: int, title: str):
        ctk.CTkLabel(
            parent, text=title,
            font=ctk.CTkFont(size=13, weight="bold"), text_color=C_ACCENT
        ).grid(row=row, column=0, sticky="w", padx=8, pady=(16, 4))

    def _row(self, parent, row: int, label: str, value: str):
        f = ctk.CTkFrame(parent, fg_color=C_PANEL, corner_radius=6)
        f.grid(row=row, column=0, sticky="ew", padx=4, pady=2)
        f.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(f, text=label, font=ctk.CTkFont(size=11),
                     text_color=C_SUBTEXT, width=180, anchor="w").grid(
            row=0, column=0, padx=10, pady=6, sticky="w")
        ctk.CTkLabel(f, text=value, font=ctk.CTkFont(size=11),
                     text_color=C_TEXT, anchor="w").grid(
            row=0, column=1, padx=10, pady=6, sticky="w")
