# =============================================================================
# FILE: ui/tabs/honeypot_tab.py
# PURPOSE: Dynamic Honeypot Tab UI (Polished user-friendly dashboard view).
#          Replaces raw terminal textboxes with structured, color-coded cards
#          for deployed traps and live attacker interception intel.
# =============================================================================

import customtkinter as ctk
from src.auth.auth import Session
from src.honeypot.decoy_manager import DecoyManager
from src.honeypot.interaction_log import InteractionLogger
from ui.animations import CyberAnimator

from ui.theme import (
    COLOR_BG as C_BG,
    COLOR_CARD as C_PANEL,
    COLOR_CYAN as C_ACCENT,
    COLOR_WARNING as C_WARNING,
    COLOR_SUCCESS as C_SUCCESS,
    COLOR_DANGER as C_DANGER,
    COLOR_TEXT_PRIMARY as C_TEXT,
    COLOR_TEXT_SECONDARY as C_SUBTEXT,
    COLOR_BORDER as C_BORDER,
    COLOR_SURFACE as C_SURFACE,
    FONT_BRAND, FONT_MONO, FONT_BODY
)


class HoneypotTab(ctk.CTkFrame):
    """
    User-friendly Dynamic Honeypot UI: active decoys cards, live structured
    attacker interaction intel feed, and ML deception adapter status.
    """

    def __init__(self, parent, session: Session):
        super().__init__(parent, fg_color=C_BG)
        self.session = session
        self.decoy_mgr = DecoyManager()
        self.interaction_logger = InteractionLogger()
        self._build()
        self._refresh_data()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # --- Status cards ---
        self.decoy_card, self.decoy_val_lbl = self._card(0, "Active Deception Traps", "0", C_WARNING, "SANDBOX ISOLATED")
        self.diverted_card, self.diverted_val_lbl = self._card(1, "Attackers Diverted", "0", C_SUCCESS, "TRAPS TRIGGERED")

        # --- Left: decoy structured cards list ---
        decoy_frame = ctk.CTkFrame(self, fg_color=C_PANEL, corner_radius=12, border_width=1, border_color=C_BORDER)
        decoy_frame.grid(row=2, column=0, padx=(16, 8), pady=(0, 16), sticky="nsew")
        decoy_frame.grid_rowconfigure(1, weight=1)
        decoy_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            decoy_frame, text="DEPLOYED DECOY ASSETS",
            font=ctk.CTkFont(family=FONT_MONO, size=11, weight="bold"), text_color=C_TEXT
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(16, 8))

        self.decoy_scroll = ctk.CTkScrollableFrame(decoy_frame, fg_color="transparent")
        self.decoy_scroll.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.decoy_scroll.grid_columnconfigure(0, weight=1)

        deploy_btn = ctk.CTkButton(
            decoy_frame, text="⚡ DEPLOY / REFRESH TRAPS",
            command=self._deploy_decoys,
            fg_color=C_SURFACE, hover_color=C_BORDER, text_color=C_ACCENT,
            font=ctk.CTkFont(family=FONT_MONO, size=11, weight="bold"),
            border_width=1, border_color=C_BORDER,
            corner_radius=6, height=36
        )
        deploy_btn.grid(row=2, column=0, padx=16, pady=(0, 16), sticky="ew")
        CyberAnimator.apply_button_hover(deploy_btn, C_SURFACE, C_BORDER)

        # --- Right: interaction log (using CTkTextbox with wrap="none" for horizontal scrolling) ---
        log_frame = ctk.CTkFrame(self, fg_color=C_PANEL, corner_radius=12, border_width=1, border_color=C_BORDER)
        log_frame.grid(row=2, column=1, padx=(8, 16), pady=(0, 16), sticky="nsew")
        log_frame.grid_rowconfigure(1, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            log_frame, text="ATTACKER INTERCEPTION FEED (SOC INTEL)",
            font=ctk.CTkFont(family=FONT_MONO, size=11, weight="bold"), text_color=C_TEXT
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(16, 8))

        self.interaction_box = ctk.CTkTextbox(
            log_frame, fg_color="#05070a", text_color=C_TEXT,
            font=ctk.CTkFont(family=FONT_MONO, size=11), state="disabled",
            border_width=1, border_color=C_BORDER, corner_radius=6,
            wrap="none"
        )
        self.interaction_box.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 12))

        refresh_log_btn = ctk.CTkButton(
            log_frame, text="🔄 REFRESH INTEL FEED",
            command=self._refresh_data,
            fg_color=C_SURFACE, hover_color=C_BORDER, text_color=C_SUBTEXT,
            font=ctk.CTkFont(family=FONT_MONO, size=11),
            border_width=1, border_color=C_BORDER,
            corner_radius=6, height=36
        )
        refresh_log_btn.grid(row=2, column=0, padx=16, pady=(0, 16), sticky="ew")
        CyberAnimator.apply_button_hover(refresh_log_btn, C_SURFACE, C_BORDER)

    def _card(self, col: int, title: str, value: str, color: str, subtitle: str):
        card = ctk.CTkFrame(self, fg_color=C_PANEL, corner_radius=10, height=86, border_width=1, border_color=C_BORDER)
        card.grid(row=1, column=col,
                  padx=(16 if col == 0 else 8, 8 if col == 0 else 16),
                  pady=(0, 16), sticky="ew")
        card.grid_propagate(False)
        ctk.CTkLabel(card, text=title.upper(), font=ctk.CTkFont(family=FONT_MONO, size=10, weight="bold"),
                     text_color=C_SUBTEXT).place(x=16, y=10)
        val_lbl = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(family=FONT_MONO, size=16, weight="bold"),
                               text_color=color)
        val_lbl.place(x=16, y=32)
        ctk.CTkLabel(card, text=subtitle, font=ctk.CTkFont(family=FONT_MONO, size=9),
                     text_color=C_SUBTEXT).place(x=16, y=58)
        return card, val_lbl

    def _deploy_decoys(self):
        self.decoy_mgr.deploy_decoys()
        self._refresh_data()

    def _refresh_data(self):
        # Clear decoys UI
        for w in self.decoy_scroll.winfo_children():
            w.destroy()

        decoys = self.decoy_mgr.get_active_decoys()
        for d in decoys:
            item = ctk.CTkFrame(self.decoy_scroll, fg_color=C_SURFACE, corner_radius=6, border_width=1, border_color=C_BORDER)
            item.pack(fill="x", pady=3)
            
            ctk.CTkLabel(
                item, text=f"🍯 {d.name}",
                font=ctk.CTkFont(family=FONT_MONO, size=11, weight="bold"), text_color=C_ACCENT
            ).pack(side="left", padx=12, pady=10)

            ctk.CTkLabel(
                item, text="TRAP ACTIVE",
                font=ctk.CTkFont(family=FONT_MONO, size=9, weight="bold"), text_color=C_SUCCESS
            ).pack(side="right", padx=12, pady=10)

        self.decoy_val_lbl.configure(text=str(len(decoys)))

        # Update interactions UI using interaction_box textbox
        logs = self.interaction_logger.get_recent_interactions(50)
        self.interaction_box.configure(state="normal")
        self.interaction_box.delete("1.0", "end")
        if not logs:
            self.interaction_box.insert("end", "No attacker interactions intercepted yet.\n")
        else:
            for l in logs:
                self.interaction_box.insert("end", f"{l}\n")
        self.interaction_box.configure(state="disabled")

        self.diverted_val_lbl.configure(text=str(len(logs) if not (len(logs) == 1 and logs[0].startswith("No")) else 0))
