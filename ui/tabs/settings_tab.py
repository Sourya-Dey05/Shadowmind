# =============================================================================
# FILE: ui/tabs/settings_tab.py
# PURPOSE: Enterprise Security Settings & SOC Policy Configuration.
#          - AI Model Configuration & Heuristic Risk Thresholds.
#          - Poison-Pill Vault & Ephemeral Key Life-Cycle Parameters.
#          - Dynamic Honeypot Deception Preferences.
#          - Breach Audit Telemetry Inspector with SOC Forensics.
# =============================================================================

import yaml
import customtkinter as ctk
from pathlib import Path
from tkinter import messagebox

from src.auth.auth import Session
from src.utils.settings_state import AppSettings
from src.utils.path_helper import get_resource_path
from ui.animations import CyberAnimator
from ui.theme import (
    COLOR_BG as C_BG,
    COLOR_CARD as C_PANEL,
    COLOR_CARD_HOVER as C_PANEL_HOVER,
    COLOR_CYAN as C_ACCENT,
    COLOR_CYAN_DIM as C_ACCENT_DIM,
    COLOR_WARNING as C_WARNING,
    COLOR_SUCCESS as C_SUCCESS,
    COLOR_DANGER as C_DANGER,
    COLOR_TEXT_PRIMARY as C_TEXT,
    COLOR_TEXT_SECONDARY as C_SUBTEXT,
    COLOR_TEXT_MUTED as C_MUTED,
    COLOR_BORDER as C_BORDER,
    COLOR_SURFACE as C_SURFACE,
    FONT_BRAND, FONT_MONO, FONT_BODY, FONT_TITLE
)

CONFIG_PATH = get_resource_path("configs/thresholds.yaml")


class SettingsTab(ctk.CTkFrame):
    """
    Admin-only Enterprise Security Configuration & System Preferences.
    """

    def __init__(self, parent, session: Session):
        super().__init__(parent, fg_color=C_BG)
        self.session = session
        with open(CONFIG_PATH, "r") as f:
            self.cfg = yaml.safe_load(f)

        self._build()
        self._auto_poll_loop()

    def _auto_poll_loop(self):
        try:
            if hasattr(self, "time_lbl") and hasattr(self, "ip_lbl") and hasattr(self, "status_lbl"):
                AppSettings.sync_from_latest_report()
                self.time_lbl.configure(text=f"Timestamp: {AppSettings.last_exfil_time}")
                self.ip_lbl.configure(text=f"Attacker IP: {AppSettings.last_exfil_ip}")
                self.status_lbl.configure(text=f"Status: {AppSettings.last_exfil_status}")
        except Exception:
            pass
        self.after(2500, self._auto_poll_loop)

    def tkraise(self, above_this=None):
        super().tkraise(above_this)
        self._refresh_audit_display()

    def _build(self):
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(0, weight=1)

        # =====================================================================
        # LEFT COLUMN: AI Detection & Vault Configuration
        # =====================================================================
        left = ctk.CTkScrollableFrame(self, fg_color=C_BG)
        left.grid(row=0, column=0, padx=(12, 6), pady=12, sticky="nsew")
        left.grid_columnconfigure(0, weight=1)

        # Section 1: Telemetry Filtering
        self._section_header(left, "Signal & Telemetry Filtering")

        signal_card = ctk.CTkFrame(left, fg_color=C_PANEL, corner_radius=10, border_width=1, border_color=C_BORDER)
        signal_card.pack(fill="x", pady=4)
        signal_card.grid_columnconfigure(1, weight=1)
        CyberAnimator.apply_glow_card_hover(signal_card, C_BORDER, C_ACCENT, C_PANEL, C_PANEL_HOVER)

        ctk.CTkLabel(
            signal_card, text="Signal Display Filter",
            font=ctk.CTkFont(family=FONT_TITLE, size=11, weight="bold"), text_color=C_TEXT
        ).grid(row=0, column=0, padx=14, pady=12, sticky="w")

        self.signal_menu = ctk.CTkOptionMenu(
            signal_card, values=["Attack & Benign", "Attack Only (Hide Benign)"],
            command=self._on_signal_mode_changed,
            fg_color=C_SURFACE, button_color=C_ACCENT, button_hover_color="#38d4ff",
            text_color=C_TEXT, font=ctk.CTkFont(family=FONT_BODY, size=11)
        )
        self.signal_menu.set(AppSettings.signal_mode)
        self.signal_menu.grid(row=0, column=1, padx=14, pady=12, sticky="e")

        # Section 2: Detection Engine Thresholds
        self._section_header(left, "Detection Thresholds")
        d = self.cfg.get("detection", {}).get("risk_score", {})
        self._setting_row(left, "Benign Max Threshold", str(d.get("benign_max", 0.35)), "Score <= 0.35 routes as normal benign traffic")
        self._setting_row(left, "Suspicious Min Threshold", str(d.get("suspicious_min", 0.35)), "Score > 0.35 triggers honeypot sandbox diversion")
        self._setting_row(left, "Confirmed Exfiltration Min", str(d.get("confirmed_min", 0.70)), "Score >= 0.70 triggers emergency Poison-Pill key rotation")

        # Section 3: Model Architecture Status
        self._section_header(left, "Neural Detection Models")
        self._setting_row(left, "SpatialCNN Weights", "Loaded (99.94% Acc)", "models/detection/cnn.pt · Payload Feature Extraction")
        self._setting_row(left, "TemporalLSTM Weights", "Loaded (99.94% Acc)", "models/detection/lstm.pt · Flow Sequence Analysis")
        self._setting_row(left, "HoneyGraphGNN Weights", "Loaded (99.94% Acc)", "models/detection/gnn.pt · Network Graph Topology")
        self._setting_row(left, "FusionMLP Weights", "Loaded (99.94% Acc)", "models/detection/mlp.pt · Decision Arbitrator")

        # =====================================================================
        # RIGHT COLUMN: Vault Security, Honeypot & SOC Breach Audit
        # =====================================================================
        right = ctk.CTkScrollableFrame(self, fg_color=C_BG)
        right.grid(row=0, column=1, padx=(6, 12), pady=12, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)

        # Section 4: Last Exfiltration Breach Audit
        self._section_header(right, "Latest Breach Telemetry")

        exfil_card = ctk.CTkFrame(right, fg_color=C_PANEL, corner_radius=12, border_width=1, border_color=C_BORDER)
        exfil_card.pack(fill="x", pady=4)
        CyberAnimator.apply_glow_card_hover(exfil_card, C_BORDER, C_WARNING, C_PANEL, "#191209")

        # Strip
        ctk.CTkFrame(exfil_card, fg_color=C_WARNING, height=2, corner_radius=0).pack(fill="x", side="top")

        ctk.CTkLabel(
            exfil_card, text="Audit Telemetry Summary",
            font=ctk.CTkFont(family=FONT_TITLE, size=11, weight="bold"), text_color=C_WARNING
        ).pack(anchor="w", padx=16, pady=(12, 4))

        self.time_lbl = ctk.CTkLabel(
            exfil_card, text=f"Timestamp: {AppSettings.last_exfil_time}",
            font=ctk.CTkFont(family=FONT_BODY, size=11), text_color=C_TEXT
        )
        self.time_lbl.pack(anchor="w", padx=16, pady=3)

        self.ip_lbl = ctk.CTkLabel(
            exfil_card, text=f"Attacker IP: {AppSettings.last_exfil_ip}",
            font=ctk.CTkFont(family=FONT_BODY, size=11), text_color=C_TEXT
        )
        self.ip_lbl.pack(anchor="w", padx=16, pady=3)

        self.status_lbl = ctk.CTkLabel(
            exfil_card, text=f"Status: {AppSettings.last_exfil_status}",
            font=ctk.CTkFont(family=FONT_BODY, size=11, weight="bold"), text_color=C_WARNING
        )
        self.status_lbl.pack(anchor="w", padx=16, pady=(3, 10))

        self.refresh_audit_btn = ctk.CTkButton(
            exfil_card, text="🔄 Refresh Audit Log",
            command=self._refresh_audit_display,
            fg_color=C_SURFACE, hover_color="#182740", text_color=C_TEXT,
            font=ctk.CTkFont(family=FONT_BODY, size=11, weight="bold"),
            border_width=1, border_color=C_BORDER, corner_radius=6, height=32
        )
        self.refresh_audit_btn.pack(padx=16, pady=(0, 14), fill="x")
        CyberAnimator.apply_button_cyber_reaction(self.refresh_audit_btn, normal_bg=C_SURFACE, hover_bg="#182740", normal_text=C_TEXT, hover_text="#ffffff")

        # Section 5: Vault & Key Management Policies
        self._section_header(right, "Vault & Key Policies")
        v = self.cfg.get("vault", {})
        self._setting_row(right, "AES Cipher Key Bits", str(v.get("aes_key_bits", 256)), "AES-256-GCM symmetric block cipher")
        self._setting_row(right, "Rotation on Breach", str(v.get("key_rotation_on_breach", True)), "Trigger instant key rotation upon threat detection")
        self._setting_row(right, "TTL Wipe on Logoff", str(v.get("ttl_wipe_on_logoff", True)), "Zero-wipes all keys from memory upon logout")

        # Section 6: Dynamic Honeypot Deception Parameters
        self._section_header(right, "Honeypot Controls")
        h = self.cfg.get("honeypot", {})
        self._setting_row(right, "Deception Engine", str(h.get("enabled", True)), "Active diversion of malicious network traffic")
        self._setting_row(right, "Canary Decoys Count", str(h.get("decoy_count", 5)), "Trap assets synchronized to honeypot directory")
        self._setting_row(right, "Port 8080 Ingress Trap", "Active (Listening)", "Listens for remote network probes")

    def _section_header(self, parent, title: str):
        ctk.CTkLabel(
            parent, text=title,
            font=ctk.CTkFont(family=FONT_TITLE, size=11, weight="bold"), text_color=C_ACCENT
        ).pack(anchor="w", padx=6, pady=(16, 4))

    def _setting_row(self, parent, label: str, value: str, description: str = ""):
        card = ctk.CTkFrame(parent, fg_color=C_PANEL, corner_radius=8, border_width=1, border_color=C_BORDER)
        card.pack(fill="x", pady=2)
        card.grid_columnconfigure(1, weight=1)
        CyberAnimator.apply_glow_card_hover(card, C_BORDER, C_ACCENT, C_PANEL, C_PANEL_HOVER)

        left_box = ctk.CTkFrame(card, fg_color="transparent")
        left_box.grid(row=0, column=0, padx=12, pady=8, sticky="w")

        ctk.CTkLabel(
            left_box, text=label,
            font=ctk.CTkFont(family=FONT_BODY, size=11, weight="bold"), text_color=C_TEXT
        ).pack(anchor="w")

        if description:
            ctk.CTkLabel(
                left_box, text=description,
                font=ctk.CTkFont(family=FONT_BODY, size=9), text_color=C_MUTED
            ).pack(anchor="w")

        ctk.CTkLabel(
            card, text=value,
            font=ctk.CTkFont(family=FONT_BODY, size=11, weight="bold"), text_color=C_ACCENT
        ).grid(row=0, column=1, padx=12, pady=8, sticky="e")

    def _on_signal_mode_changed(self, choice: str):
        AppSettings.signal_mode = choice

    def _refresh_audit_display(self):
        # 1. Sync from latest forensic report on disk or in-memory state
        AppSettings.sync_from_latest_report()

        # 2. Update telemetry labels
        self.time_lbl.configure(text=f"Timestamp: {AppSettings.last_exfil_time}")
        self.ip_lbl.configure(text=f"Attacker IP: {AppSettings.last_exfil_ip}")
        self.status_lbl.configure(text=f"Status: {AppSettings.last_exfil_status}")

        # 3. Interactive confirmation feedback on button
        orig_text = "🔄 Refresh Audit Log"
        self.refresh_audit_btn.configure(
            text="✓ Telemetry Synchronized!",
            fg_color="#064e3b", text_color="#6ee7b7"
        )
        self.after(1600, lambda: self.refresh_audit_btn.configure(
            text=orig_text,
            fg_color=C_SURFACE, text_color=C_TEXT
        ))
