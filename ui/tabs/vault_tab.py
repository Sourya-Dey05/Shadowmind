# =============================================================================
# FILE: ui/tabs/vault_tab.py
# PURPOSE: File Vault tab UI. In Phase 0 this is a layout skeleton showing
#          the protected files list, current session key status panel, and
#          TTL countdown timer. Phase 3 will wire in the actual AES-256
#          encryption, GAN key generation, emergency rotation button logic,
#          and the TTL self-destruct engine. All containers are pre-built here.
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


class VaultTab(ctk.CTkFrame):
    """
    Poison Pill Vault UI: protected files, key status, TTL countdown,
    emergency rotation trigger.
    """

    def __init__(self, parent, session: Session):
        super().__init__(parent, fg_color=C_BG)
        self.session = session
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Left: protected files list ---
        files_frame = ctk.CTkFrame(self, fg_color=C_PANEL, corner_radius=10)
        files_frame.grid(row=0, column=0, padx=(12, 6), pady=12, sticky="nsew")
        files_frame.grid_rowconfigure(1, weight=1)
        files_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            files_frame, text="Protected Files",
            font=ctk.CTkFont(size=14, weight="bold"), text_color=C_TEXT
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(12, 4))

        self.files_box = ctk.CTkTextbox(
            files_frame, fg_color="#0a0c10", text_color=C_TEXT,
            font=ctk.CTkFont(family="Courier New", size=11), state="disabled"
        )
        self.files_box.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="nsew")
        self._append_files("No protected files yet. (Phase 3)")

        # Add file button (placeholder)
        ctk.CTkButton(
            files_frame, text="+ Add File to Vault",
            fg_color=C_ACCENT, hover_color="#009fcc", text_color="#000000",
            state="disabled", corner_radius=8
        ).grid(row=2, column=0, padx=12, pady=(0, 12), sticky="ew")

        # --- Right: key status + TTL + emergency rotation ---
        right = ctk.CTkFrame(self, fg_color=C_BG)
        right.grid(row=0, column=1, padx=(6, 12), pady=12, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)

        # Key status card
        key_card = ctk.CTkFrame(right, fg_color=C_PANEL, corner_radius=10)
        key_card.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        key_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(key_card, text="Session Key",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=C_TEXT).grid(row=0, column=0, sticky="w", padx=16, pady=(12, 4))
        ctk.CTkLabel(key_card, text="Status:",
                     font=ctk.CTkFont(size=11), text_color=C_SUBTEXT).grid(
            row=1, column=0, sticky="w", padx=16)
        ctk.CTkLabel(key_card, text="NOT ISSUED  (Phase 3)",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=C_WARNING).grid(row=2, column=0, sticky="w", padx=16, pady=(0, 4))

        ctk.CTkLabel(key_card, text="Algorithm:",
                     font=ctk.CTkFont(size=11), text_color=C_SUBTEXT).grid(
            row=3, column=0, sticky="w", padx=16)
        ctk.CTkLabel(key_card, text="AES-256 (RAM only)",
                     font=ctk.CTkFont(size=12), text_color=C_TEXT).grid(
            row=4, column=0, sticky="w", padx=16, pady=(0, 4))

        ctk.CTkLabel(key_card, text="Key Source:",
                     font=ctk.CTkFont(size=11), text_color=C_SUBTEXT).grid(
            row=5, column=0, sticky="w", padx=16)
        ctk.CTkLabel(key_card, text="GAN-generated per-session",
                     font=ctk.CTkFont(size=12), text_color=C_TEXT).grid(
            row=6, column=0, sticky="w", padx=16, pady=(0, 12))

        # TTL countdown card
        ttl_card = ctk.CTkFrame(right, fg_color=C_PANEL, corner_radius=10)
        ttl_card.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        ttl_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(ttl_card, text="TTL Self-Destruct",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=C_TEXT).grid(row=0, column=0, sticky="w", padx=16, pady=(12, 4))
        ctk.CTkLabel(ttl_card, text="Key wipes from RAM at session logout",
                     font=ctk.CTkFont(size=11), text_color=C_SUBTEXT).grid(
            row=1, column=0, sticky="w", padx=16, pady=(0, 4))
        ctk.CTkLabel(ttl_card, text="Countdown: see top bar",
                     font=ctk.CTkFont(size=12), text_color=C_ACCENT).grid(
            row=2, column=0, sticky="w", padx=16, pady=(0, 12))

        # Emergency rotation card
        rot_card = ctk.CTkFrame(right, fg_color=C_PANEL, corner_radius=10)
        rot_card.grid(row=2, column=0, sticky="ew")
        rot_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(rot_card, text="Emergency Rotation",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=C_TEXT).grid(row=0, column=0, sticky="w", padx=16, pady=(12, 4))
        ctk.CTkLabel(rot_card,
                     text="Re-encrypts all vault files with a new\nkey in < 500 ms. Stolen data\nbecomes permanently unreadable.",
                     font=ctk.CTkFont(size=11), text_color=C_SUBTEXT,
                     justify="left").grid(row=1, column=0, sticky="w", padx=16, pady=(0, 8))
        ctk.CTkButton(
            rot_card, text="ROTATE KEY NOW",
            fg_color=C_DANGER, hover_color="#cc0000",
            font=ctk.CTkFont(size=13, weight="bold"),
            state="disabled", corner_radius=8
        ).grid(row=2, column=0, padx=12, pady=(0, 12), sticky="ew")

    def _append_files(self, msg: str):
        self.files_box.configure(state="normal")
        self.files_box.insert("end", msg + "\n")
        self.files_box.configure(state="disabled")
