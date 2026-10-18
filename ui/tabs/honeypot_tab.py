# =============================================================================
# FILE: ui/tabs/honeypot_tab.py
# PURPOSE: Honeypot tab UI (Fully wired in Phase 4).
#          Displays active deployed decoys, attacker interaction logs, and
#          real-time telemetry from the HoneypotRedirector and InteractionLogger.
# =============================================================================

import customtkinter as ctk
from src.auth.auth import Session
from src.honeypot.decoy_manager import DecoyManager
from src.honeypot.interaction_log import InteractionLogger

C_BG      = "#0d0f14"
C_PANEL   = "#13161e"
C_ACCENT  = "#00c8ff"
C_WARNING = "#ffaa00"
C_SUCCESS = "#00cc66"
C_TEXT    = "#e0e0e0"
C_SUBTEXT = "#888888"


class HoneypotTab(ctk.CTkFrame):
    """
    Dynamic Honeypot UI: active decoys, live attacker interaction log,
    and redirection metrics.
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
        self.grid_rowconfigure(1, weight=1)

        # --- Status cards ---
        self.decoy_count_card, self.decoy_val_lbl = self._card(0, "Active Decoys", "0", C_WARNING)
        self.diverted_card, self.diverted_val_lbl = self._card(1, "Attackers Diverted", "0", C_SUCCESS)

        # --- Left: decoy list ---
        decoy_frame = ctk.CTkFrame(self, fg_color=C_PANEL, corner_radius=10)
        decoy_frame.grid(row=1, column=0, padx=(12, 6), pady=12, sticky="nsew")
        decoy_frame.grid_rowconfigure(1, weight=1)
        decoy_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            decoy_frame, text="Active Deception Traps",
            font=ctk.CTkFont(size=14, weight="bold"), text_color=C_TEXT
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(12, 4))

        self.decoy_box = ctk.CTkTextbox(
            decoy_frame, fg_color="#0a0c10", text_color=C_TEXT,
            font=ctk.CTkFont(family="Courier New", size=11), state="disabled"
        )
        self.decoy_box.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="nsew")

        ctk.CTkButton(
            decoy_frame, text="Deploy / Refresh Decoys",
            command=self._deploy_decoys,
            fg_color=C_ACCENT, hover_color="#009fcc", text_color="#000000",
            corner_radius=8
        ).grid(row=2, column=0, padx=12, pady=(0, 12), sticky="ew")

        # --- Right: interaction log ---
        log_frame = ctk.CTkFrame(self, fg_color=C_PANEL, corner_radius=10)
        log_frame.grid(row=1, column=1, padx=(6, 12), pady=12, sticky="nsew")
        log_frame.grid_rowconfigure(1, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            log_frame, text="Attacker Interaction Log (Honeypot Intel)",
            font=ctk.CTkFont(size=14, weight="bold"), text_color=C_TEXT
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(12, 4))

        self.interaction_box = ctk.CTkTextbox(
            log_frame, fg_color="#0a0c10", text_color=C_TEXT,
            font=ctk.CTkFont(family="Courier New", size=11), state="disabled"
        )
        self.interaction_box.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="nsew")

        # ML adapter status
        ml_frame = ctk.CTkFrame(self, fg_color=C_PANEL, corner_radius=10)
        ml_frame.grid(row=2, column=0, columnspan=2, padx=12, pady=(0, 12), sticky="ew")
        ctk.CTkLabel(
            ml_frame,
            text="ML Adapter: Adapts decoy realism based on attacker behavior  |  Status: ACTIVE (Phase 4)",
            font=ctk.CTkFont(size=11), text_color=C_SUCCESS
        ).pack(padx=16, pady=10)

    def _card(self, col: int, title: str, value: str, color: str):
        card = ctk.CTkFrame(self, fg_color=C_PANEL, corner_radius=10, height=80)
        card.grid(row=0, column=col,
                  padx=(12 if col == 0 else 6, 6 if col == 0 else 12),
                  pady=(12, 6), sticky="ew")
        card.grid_propagate(False)
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=11),
                     text_color=C_SUBTEXT).place(x=16, y=10)
        val_lbl = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=22, weight="bold"),
                               text_color=color)
        val_lbl.place(x=16, y=32)
        return card, val_lbl

    def _deploy_decoys(self):
        self.decoy_mgr.deploy_decoys()
        self._refresh_data()

    def _refresh_data(self):
        # Decoys
        decoys = self.decoy_mgr.get_active_decoys()
        self.decoy_box.configure(state="normal")
        self.decoy_box.delete("1.0", "end")
        for d in decoys:
            self.decoy_box.insert("end", f"🍯 [TRAP] {d.name}\n    Path: {d}\n\n")
        self.decoy_box.configure(state="disabled")
        self.decoy_val_lbl.configure(text=str(len(decoys)))

        # Interactions
        logs = self.interaction_logger.get_recent_interactions(50)
        self.interaction_box.configure(state="normal")
        self.interaction_box.delete("1.0", "end")
        for l in logs:
            self.interaction_box.insert("end", f"{l}\n")
        self.interaction_box.configure(state="disabled")
        self.diverted_val_lbl.configure(text=str(len(logs)))
