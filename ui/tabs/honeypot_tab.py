# =============================================================================
# FILE: ui/tabs/honeypot_tab.py
# PURPOSE: Honeypot tab UI. In Phase 0 this is a layout skeleton showing the
#          active decoys list and the attacker interaction live log panel.
#          Phase 4 will wire in decoy_manager.py, interaction_log.py,
#          ml_adapter.py, and redirector.py. All containers are pre-built here
#          so Phase 4 only needs to inject data, not redesign the layout.
# =============================================================================

import customtkinter as ctk
from src.auth.auth import Session

C_BG      = "#0d0f14"
C_PANEL   = "#13161e"
C_ACCENT  = "#00c8ff"
C_WARNING = "#ffaa00"
C_SUCCESS = "#00cc66"
C_TEXT    = "#e0e0e0"
C_SUBTEXT = "#888888"


class HoneypotTab(ctk.CTkFrame):
    """
    Dynamic Honeypot UI: active decoys, attacker interaction log,
    ML adapter status.
    """

    def __init__(self, parent, session: Session):
        super().__init__(parent, fg_color=C_BG)
        self.session = session
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Status cards ---
        self._card(0, "Active Decoys",      "0",        C_WARNING)
        self._card(1, "Attackers Diverted", "0",        C_SUCCESS)

        # --- Left: decoy list ---
        decoy_frame = ctk.CTkFrame(self, fg_color=C_PANEL, corner_radius=10)
        decoy_frame.grid(row=1, column=0, padx=(12, 6), pady=12, sticky="nsew")
        decoy_frame.grid_rowconfigure(1, weight=1)
        decoy_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            decoy_frame, text="Active Decoys",
            font=ctk.CTkFont(size=14, weight="bold"), text_color=C_TEXT
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(12, 4))

        self.decoy_box = ctk.CTkTextbox(
            decoy_frame, fg_color="#0a0c10", text_color=C_TEXT,
            font=ctk.CTkFont(family="Courier New", size=11), state="disabled"
        )
        self.decoy_box.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="nsew")
        self._append_decoy("No decoys active. (Phase 4)")

        ctk.CTkButton(
            decoy_frame, text="Deploy Decoys",
            fg_color=C_ACCENT, hover_color="#009fcc", text_color="#000000",
            state="disabled", corner_radius=8
        ).grid(row=2, column=0, padx=12, pady=(0, 12), sticky="ew")

        # --- Right: interaction log ---
        log_frame = ctk.CTkFrame(self, fg_color=C_PANEL, corner_radius=10)
        log_frame.grid(row=1, column=1, padx=(6, 12), pady=12, sticky="nsew")
        log_frame.grid_rowconfigure(1, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            log_frame, text="Attacker Interaction Log",
            font=ctk.CTkFont(size=14, weight="bold"), text_color=C_TEXT
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(12, 4))

        self.interaction_box = ctk.CTkTextbox(
            log_frame, fg_color="#0a0c10", text_color=C_TEXT,
            font=ctk.CTkFont(family="Courier New", size=11), state="disabled"
        )
        self.interaction_box.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="nsew")
        self._append_interaction("Waiting for attacker activity... (Phase 4)")

        # ML adapter status
        ml_frame = ctk.CTkFrame(self, fg_color=C_PANEL, corner_radius=10)
        ml_frame.grid(row=2, column=0, columnspan=2, padx=12, pady=(0, 12), sticky="ew")
        ctk.CTkLabel(
            ml_frame,
            text="ML Adapter:  Adjusts decoy realism based on observed attacker behavior  |  Status: NOT LOADED (Phase 4)",
            font=ctk.CTkFont(size=11), text_color=C_SUBTEXT
        ).pack(padx=16, pady=10)

    def _card(self, col: int, title: str, value: str, color: str):
        card = ctk.CTkFrame(self, fg_color=C_PANEL, corner_radius=10, height=80)
        card.grid(row=0, column=col,
                  padx=(12 if col == 0 else 6, 6 if col == 0 else 12),
                  pady=(12, 6), sticky="ew")
        card.grid_propagate(False)
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=11),
                     text_color=C_SUBTEXT).place(x=16, y=10)
        ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=color).place(x=16, y=32)

    def _append_decoy(self, msg: str):
        self.decoy_box.configure(state="normal")
        self.decoy_box.insert("end", msg + "\n")
        self.decoy_box.configure(state="disabled")

    def _append_interaction(self, msg: str):
        self.interaction_box.configure(state="normal")
        self.interaction_box.insert("end", msg + "\n")
        self.interaction_box.configure(state="disabled")
