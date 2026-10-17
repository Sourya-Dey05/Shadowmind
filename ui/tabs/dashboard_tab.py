# =============================================================================
# FILE: ui/tabs/dashboard_tab.py
# PURPOSE: Dashboard tab shown after login. In Phase 0 this is a placeholder
#          with static layout. Phase 1 will wire in the live threat score graph,
#          session status indicator, real-time traffic event log, and the
#          CNN+LSTM+MLP risk score gauge. The layout skeleton is built now
#          so every Phase 1 widget has a container ready to receive it.
# =============================================================================

import customtkinter as ctk
from src.auth.auth import Session

C_BG      = "#0d0f14"
C_PANEL   = "#13161e"
C_ACCENT  = "#00c8ff"
C_SUCCESS = "#00cc66"
C_WARNING = "#ffaa00"
C_DANGER  = "#ff4444"
C_TEXT    = "#e0e0e0"
C_SUBTEXT = "#888888"


class DashboardTab(ctk.CTkFrame):
    """
    Main monitoring dashboard. Shows system status, threat score, and event log.
    """

    def __init__(self, parent, session: Session):
        super().__init__(parent, fg_color=C_BG)
        self.session = session
        self._build()

    def _build(self):
        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Status cards row ---
        self._status_card(0, "System Status", "ACTIVE", C_SUCCESS)
        self._status_card(1, "Threat Level",  "BENIGN", C_SUCCESS)
        self._status_card(2, "Session Key",   "ISSUED", C_SUCCESS)

        # --- Threat score graph placeholder ---
        graph_frame = ctk.CTkFrame(self, fg_color=C_PANEL, corner_radius=10)
        graph_frame.grid(row=1, column=0, columnspan=2, padx=(12, 6), pady=12, sticky="nsew")
        ctk.CTkLabel(
            graph_frame,
            text="[ Threat Score Graph ]\nWired in Phase 1",
            font=ctk.CTkFont(size=13), text_color=C_SUBTEXT
        ).place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(
            graph_frame, text="Live Threat Score",
            font=ctk.CTkFont(size=14, weight="bold"), text_color=C_TEXT
        ).place(x=16, y=12)

        # --- Event log placeholder ---
        log_frame = ctk.CTkFrame(self, fg_color=C_PANEL, corner_radius=10)
        log_frame.grid(row=1, column=2, padx=(6, 12), pady=12, sticky="nsew")
        log_frame.grid_rowconfigure(1, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            log_frame, text="Event Log",
            font=ctk.CTkFont(size=14, weight="bold"), text_color=C_TEXT
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(12, 4))

        self.log_box = ctk.CTkTextbox(
            log_frame, fg_color="#0a0c10", text_color=C_TEXT,
            font=ctk.CTkFont(family="Courier New", size=11), state="disabled"
        )
        self.log_box.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="nsew")
        self._append_log("ShadowMind started.")
        self._append_log(f"Logged in as: {self.session.username} [{self.session.role.value}]")
        self._append_log("Detection engine: NOT YET LOADED (Phase 1)")
        self._append_log("Vault: NOT YET LOADED (Phase 3)")
        self._append_log("Honeypot: NOT YET LOADED (Phase 4)")

    def _status_card(self, col: int, title: str, value: str, color: str):
        card = ctk.CTkFrame(self, fg_color=C_PANEL, corner_radius=10, height=90)
        card.grid(row=0, column=col, padx=(12 if col == 0 else 6, 6 if col < 2 else 12),
                  pady=(12, 6), sticky="ew")
        card.grid_propagate(False)
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=11),
                     text_color=C_SUBTEXT).place(x=16, y=12)
        ctk.CTkLabel(card, text=value,
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=color).place(x=16, y=36)

    def _append_log(self, msg: str):
        import datetime
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"[{ts}] {msg}\n")
        self.log_box.configure(state="disabled")
        self.log_box.see("end")
