# =============================================================================
# FILE: ui/tabs/honeypot_tab.py
# PURPOSE: Enterprise Deception & Dynamic Honeypot Command Center.
#          - Interactive Canary Token & Decoy Asset Matrix.
#          - Real-Time Attacker Interception & Multi-Hop Redirection Feed.
#          - Live Sandbox Quarantine Status with Sub-Millisecond Lure Arming.
# =============================================================================

import customtkinter as ctk
from pathlib import Path
from tkinter import messagebox

from src.auth.auth import Session
from src.honeypot.decoy_manager import DecoyManager
from src.honeypot.interaction_log import InteractionLogger
from ui.widgets.scrollable_log import InteractiveLogViewer
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


class HoneypotTab(ctk.CTkFrame):
    """
    User-friendly Dynamic Honeypot Deception UI.
    """

    def __init__(self, parent, session: Session):
        super().__init__(parent, fg_color=C_BG)
        self.session = session
        self.decoy_mgr = DecoyManager()
        self.interaction_logger = InteractionLogger()
        self._build()
        self._refresh_data()

    def _build(self):
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ---------------------------------------------------------------------
        # TOP ROW: Deception KPI Cards (3 Cards)
        # ---------------------------------------------------------------------
        kpi_row = ctk.CTkFrame(self, fg_color="transparent")
        kpi_row.grid(row=0, column=0, columnspan=2, sticky="ew", padx=12, pady=(12, 6))
        kpi_row.grid_columnconfigure((0, 1, 2), weight=1)

        # Card 0: Active Decoys
        self.card_decoys, self.lbl_decoys_count = self._create_kpi_card(
            kpi_row, 0, "Active Decoys", "5 Armed", C_WARNING,
            "High-interaction canary tokens", C_WARNING
        )

        # Card 1: Diverted Attackers
        self.card_divert, self.lbl_divert_count = self._create_kpi_card(
            kpi_row, 1, "Attackers Intercepted", "0 Diverted", C_SUCCESS,
            "Dynamic forensic traps active", C_ACCENT
        )

        # Card 2: Sandbox Isolation
        self.card_sandbox, self.lbl_sandbox_status = self._create_kpi_card(
            kpi_row, 2, "Honeypot Sandbox", "● Sandbox Active", C_ACCENT,
            "Listening on Port 8080", "#7667FF"
        )
        CyberAnimator.start_pulse_animation(self.lbl_sandbox_status, C_ACCENT, "#80e5ff", 1.2)

        # ---------------------------------------------------------------------
        # MAIN BODY: Split View (Left: Decoy Assets, Right: Interception Feed)
        # ---------------------------------------------------------------------
        # --- LEFT PANEL: Deployed Decoy Assets ---
        decoy_panel = ctk.CTkFrame(self, fg_color=C_PANEL, corner_radius=12, border_width=1, border_color=C_BORDER)
        decoy_panel.grid(row=1, column=0, padx=(12, 6), pady=(0, 12), sticky="nsew")
        decoy_panel.grid_columnconfigure(0, weight=1)
        decoy_panel.grid_rowconfigure(2, weight=1)
        CyberAnimator.apply_glow_card_hover(decoy_panel, C_BORDER, C_ACCENT, C_PANEL, "#0f1c30")

        # Strip
        ctk.CTkFrame(decoy_panel, fg_color=C_ACCENT, height=2, corner_radius=0).grid(row=0, column=0, sticky="ew")

        # Header
        dh = ctk.CTkFrame(decoy_panel, fg_color="transparent")
        dh.grid(row=1, column=0, sticky="ew", padx=16, pady=(12, 6))
        dh.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            dh, text="Active Decoy Assets",
            font=ctk.CTkFont(family=FONT_TITLE, size=12, weight="bold"), text_color=C_TEXT
        ).grid(row=0, column=0, sticky="w")

        btn_deploy = ctk.CTkButton(
            dh, text="⚡ Reset Decoys", command=self._deploy_decoys,
            width=100, height=26, fg_color=C_SURFACE, hover_color="#182740",
            text_color=C_ACCENT, font=ctk.CTkFont(family=FONT_BODY, size=10, weight="bold"),
            border_width=1, border_color=C_BORDER, corner_radius=4
        )
        btn_deploy.grid(row=0, column=2, sticky="e")
        CyberAnimator.apply_button_cyber_reaction(btn_deploy, normal_bg=C_SURFACE, hover_bg="#182740", normal_text=C_ACCENT, hover_text="#ffffff")

        # Scrollable decoy cards
        self.decoy_scroll = ctk.CTkScrollableFrame(decoy_panel, fg_color=C_SURFACE, corner_radius=8, border_width=1, border_color=C_BORDER)
        self.decoy_scroll.grid(row=2, column=0, padx=12, pady=(0, 10), sticky="nsew")
        self.decoy_scroll.grid_columnconfigure(0, weight=1)

        # Footer note
        ctk.CTkLabel(
            decoy_panel,
            text="Any interaction with canary files triggers instant defense alerts and key rotation.",
            font=ctk.CTkFont(family=FONT_BODY, size=9), text_color=C_MUTED, justify="center"
        ).grid(row=3, column=0, padx=12, pady=(0, 12), sticky="ew")

        # --- RIGHT PANEL: Attacker Interception Timeline ---
        feed_panel = ctk.CTkFrame(self, fg_color=C_PANEL, corner_radius=12, border_width=1, border_color=C_BORDER)
        feed_panel.grid(row=1, column=1, padx=(6, 12), pady=(0, 12), sticky="nsew")
        feed_panel.grid_columnconfigure(0, weight=1)
        feed_panel.grid_rowconfigure(2, weight=1)
        CyberAnimator.apply_glow_card_hover(feed_panel, C_BORDER, C_WARNING, C_PANEL, "#14101c")

        # Strip
        ctk.CTkFrame(feed_panel, fg_color=C_WARNING, height=2, corner_radius=0).grid(row=0, column=0, sticky="ew")

        # Header
        fh = ctk.CTkFrame(feed_panel, fg_color="transparent")
        fh.grid(row=1, column=0, sticky="ew", padx=16, pady=(12, 6))
        fh.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            fh, text="Interception Feed",
            font=ctk.CTkFont(family=FONT_TITLE, size=12, weight="bold"), text_color=C_TEXT
        ).grid(row=0, column=0, sticky="w")

        btn_feed_refresh = ctk.CTkButton(
            fh, text="🔄 Refresh Feed", command=self._refresh_data,
            width=100, height=26, fg_color=C_SURFACE, hover_color="#182740",
            text_color=C_SUBTEXT, font=ctk.CTkFont(family=FONT_BODY, size=10),
            border_width=1, border_color=C_BORDER, corner_radius=4
        )
        btn_feed_refresh.grid(row=0, column=2, sticky="e")
        CyberAnimator.apply_button_cyber_reaction(btn_feed_refresh, normal_bg=C_SURFACE, hover_bg="#182740", normal_text=C_SUBTEXT, hover_text="#ffffff")

        # Log viewer ($O(1)$ fast rendering)
        self.interaction_box = InteractiveLogViewer(feed_panel, corner_radius=8, border_width=1, border_color=C_BORDER)
        self.interaction_box.grid(row=2, column=0, padx=12, pady=(0, 10), sticky="nsew")

        # Test decoy click simulator button
        test_btn = ctk.CTkButton(
            feed_panel, text="🧪 Simulate Attacker Decoy Click (Test)",
            command=self._simulate_decoy_click,
            fg_color=C_SURFACE, hover_color="#2b1a10", text_color=C_WARNING,
            font=ctk.CTkFont(family=FONT_TITLE, size=11, weight="bold"),
            border_width=1, border_color="#4d2c14", corner_radius=6, height=34
        )
        test_btn.grid(row=3, column=0, padx=12, pady=(0, 12), sticky="ew")
        CyberAnimator.apply_button_cyber_reaction(test_btn, normal_bg=C_SURFACE, hover_bg="#2b1a10", normal_text=C_WARNING, hover_text="#ffffff")

    def _create_kpi_card(self, parent, col: int, title: str, value: str, val_color: str, subtitle: str, strip_color: str):
        card = ctk.CTkFrame(parent, fg_color=C_PANEL, corner_radius=10, height=84, border_width=1, border_color=C_BORDER)
        card.grid(row=0, column=col, padx=(0 if col == 0 else 6, 0 if col == 2 else 6), sticky="ew")
        card.grid_propagate(False)

        strip = ctk.CTkFrame(card, fg_color=strip_color, height=2, corner_radius=0)
        strip.place(x=0, y=0, relwidth=1.0)

        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(family=FONT_BODY, size=10, weight="bold"), text_color=C_SUBTEXT).place(x=14, y=10)
        lbl_val = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(family=FONT_TITLE, size=16, weight="bold"), text_color=val_color)
        lbl_val.place(x=14, y=32)

        if subtitle:
            ctk.CTkLabel(card, text=subtitle, font=ctk.CTkFont(family=FONT_BODY, size=9), text_color=C_MUTED).place(x=14, y=58)

        CyberAnimator.apply_glow_card_hover(card, C_BORDER, strip_color, C_PANEL, C_PANEL_HOVER)
        return card, lbl_val
        lbl_val = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(family=FONT_MONO, size=16, weight="bold"), text_color=val_color)
        lbl_val.place(x=14, y=32)

        if subtitle:
            ctk.CTkLabel(card, text=subtitle, font=ctk.CTkFont(family=FONT_MONO, size=8), text_color=C_MUTED).place(x=14, y=58)

        CyberAnimator.apply_glow_card_hover(card, C_BORDER, strip_color, C_PANEL, C_PANEL_HOVER)
        return card, lbl_val

    def _deploy_decoys(self):
        self.decoy_mgr.deploy_decoys()
        self._refresh_data()
        messagebox.showinfo("Swarm Synchronized", "All 5 canary deception lures deployed & active in honeypot sandbox.")

    def _simulate_decoy_click(self):
        import random
        sample_ips = ["203.0.113.42", "198.51.100.89", "192.168.1.105"]
        sample_files = ["financial_passwords_2026.xlsx", "customer_database_dump.sql", "aws_production_keys.env"]
        ip = random.choice(sample_ips)
        file = random.choice(sample_files)
        self.interaction_logger.log_interaction(ip, f"TEST_DOWNLOAD_ATTEMPT: {file}", file)
        self._refresh_data()

    def _refresh_data(self):
        for w in self.decoy_scroll.winfo_children():
            w.destroy()

        decoys = self.decoy_mgr.get_active_decoys()

        icon_map = {
            ".xlsx": ("📊", "#20d6a0", "Financial Spreadsheet"),
            ".sql":  ("🗄️", "#00d5ff", "Database Dump"),
            ".pdf":  ("📑", "#ffb547", "Executive Payroll"),
            ".env":  ("🔑", "#ff4568", "API Credentials"),
            ".txt":  ("🌐", "#a78bfa", "Network Map")
        }

        for d in decoys:
            suffix = d.suffix.lower()
            icon, icon_c, desc = icon_map.get(suffix, ("🍯", C_ACCENT, "Canary Token"))

            item = ctk.CTkFrame(self.decoy_scroll, fg_color="#091322", corner_radius=8, border_width=1, border_color=C_BORDER)
            item.pack(fill="x", pady=4, padx=2)
            item.grid_columnconfigure(1, weight=1)
            CyberAnimator.apply_glow_card_hover(item, C_BORDER, C_ACCENT, "#091322", "#0f1f38")

            ctk.CTkLabel(item, text=icon, font=ctk.CTkFont(size=14)).grid(row=0, column=0, padx=(10, 6), pady=8)

            info = ctk.CTkFrame(item, fg_color="transparent")
            info.grid(row=0, column=1, sticky="w", pady=6)

            ctk.CTkLabel(
                info, text=d.name,
                font=ctk.CTkFont(family=FONT_BODY, size=11, weight="bold"), text_color=C_TEXT
            ).pack(anchor="w")

            ctk.CTkLabel(
                info, text=f"{desc}  ·  Port 8080 Active",
                font=ctk.CTkFont(family=FONT_BODY, size=9), text_color=C_MUTED
            ).pack(anchor="w")

            status_pill = ctk.CTkLabel(
                item, text="● Armed",
                font=ctk.CTkFont(family=FONT_BODY, size=10, weight="bold"), text_color=C_SUCCESS
            )
            status_pill.grid(row=0, column=2, padx=12, pady=8)

        self.lbl_decoys_count.configure(text=f"{len(decoys)} Armed")

        logs = self.interaction_logger.get_recent_interactions(50)
        self.interaction_box.clear()
        if not logs or (len(logs) == 1 and logs[0].startswith("No")):
            self.interaction_box.append_log("No attacker interactions intercepted yet. Honeypot traps listening...", "INFO")
            self.lbl_divert_count.configure(text="0 Diverted")
        else:
            for l in logs:
                lvl = "ALERT" if any(kw in l.upper() for kw in ["REDIRECT", "DOWNLOAD", "ATTEMPT"]) else "INFO"
                self.interaction_box.append_log(l, lvl)
            self.lbl_divert_count.configure(text=f"{len(logs)} Interceptions")
