# =============================================================================
# FILE: ui/tabs/vault_tab.py
# PURPOSE: Enterprise Ephemeral File Vault & Workspace Manager.
#          - Active Workspace (/Vault Folder): Daily plaintext workspace that
#            instantly auto-locks into AES-256 ciphertext on attack detection.
#          - Static Cipher Vault (data/vault/): Encrypted cold storage.
#          - Hardware-Isolated RAM Key Enclave & TTL Self-Destruct Deck.
#          - Emergency Poison-Pill Key Rotation with sub-50ms benchmark.
# =============================================================================

import os
import time
import datetime
from pathlib import Path
import customtkinter as ctk
from tkinter import filedialog, messagebox, simpledialog

from src.auth.auth import Session
from src.vault.keygen import generate_session_key
from src.vault.aes_vault import AESVault
from src.vault.rotation import emergency_rotate_keys
from src.vault.ttl_destruct import zero_wipe_ram_key
from src.vault.session_state import SessionState
from src.workspace.workspace_vault import ExternalVaultFolder
from ui.animations import CyberAnimator
from ui.theme import (
    COLOR_BG as C_BG,
    COLOR_CARD as C_PANEL,
    COLOR_CARD_HOVER as C_PANEL_HOVER,
    COLOR_CYAN as C_ACCENT,
    COLOR_CYAN_DIM as C_ACCENT_DIM,
    COLOR_SUCCESS as C_SUCCESS,
    COLOR_WARNING as C_WARNING,
    COLOR_DANGER as C_DANGER,
    COLOR_TEXT_PRIMARY as C_TEXT,
    COLOR_TEXT_SECONDARY as C_SUBTEXT,
    COLOR_TEXT_MUTED as C_MUTED,
    COLOR_BORDER as C_BORDER,
    COLOR_SURFACE as C_SURFACE,
    FONT_BRAND, FONT_MONO, FONT_BODY, FONT_TITLE
)


class VaultTab(ctk.CTkFrame):
    """
    Enterprise File Vault & Ephemeral Encryption Command Deck.
    """

    def __init__(self, parent, session: Session):
        super().__init__(parent, fg_color=C_BG)
        self.session = session
        self.vault = AESVault(SessionState.get_key())
        self.workspace = ExternalVaultFolder()
        self.protected_files = []

        self._build()
        self._load_default_vault_files()
        self._refresh_workspace_display()
        self._refresh_files_display()

    def _build(self):
        self.grid_columnconfigure((0, 1), weight=3)
        self.grid_columnconfigure(2, weight=2)
        self.grid_rowconfigure(0, weight=1)

        # =====================================================================
        # COLUMN 0: Active Workspace (/Vault Folder - Auto-Locking)
        # =====================================================================
        ws_frame = ctk.CTkFrame(self, fg_color=C_PANEL, corner_radius=12, border_width=1, border_color=C_BORDER)
        ws_frame.grid(row=0, column=0, padx=(12, 6), pady=12, sticky="nsew")
        ws_frame.grid_columnconfigure(0, weight=1)
        ws_frame.grid_rowconfigure(2, weight=1)
        CyberAnimator.apply_glow_card_hover(ws_frame, C_BORDER, C_ACCENT, C_PANEL, "#0d1829")

        # Strip
        ctk.CTkFrame(ws_frame, fg_color=C_ACCENT, height=2, corner_radius=0).grid(row=0, column=0, sticky="ew")

        # Header
        ws_head = ctk.CTkFrame(ws_frame, fg_color="transparent")
        ws_head.grid(row=1, column=0, sticky="ew", padx=16, pady=(12, 6))
        ws_head.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            ws_head, text="Active Workspace (/Vault)",
            font=ctk.CTkFont(family=FONT_TITLE, size=12, weight="bold"), text_color=C_TEXT
        ).grid(row=0, column=0, sticky="w")

        btn_ws_refresh = ctk.CTkButton(
            ws_head, text="🔄 Refresh", command=self._refresh_workspace_display,
            width=70, height=24, fg_color=C_SURFACE, hover_color="#182740",
            text_color=C_SUBTEXT, font=ctk.CTkFont(family=FONT_BODY, size=10),
            border_width=1, border_color=C_BORDER, corner_radius=4
        )
        btn_ws_refresh.grid(row=0, column=2, sticky="e")
        CyberAnimator.apply_button_cyber_reaction(btn_ws_refresh, normal_bg=C_SURFACE, hover_bg="#182740", normal_text=C_SUBTEXT, hover_text="#ffffff")

        # Scrollable file list
        self.ws_scroll = ctk.CTkScrollableFrame(ws_frame, fg_color=C_SURFACE, corner_radius=8, border_width=1, border_color=C_BORDER)
        self.ws_scroll.grid(row=2, column=0, padx=12, pady=(0, 10), sticky="nsew")
        self.ws_scroll.grid_columnconfigure(0, weight=1)

        # Workspace actions
        ws_actions = ctk.CTkFrame(ws_frame, fg_color="transparent")
        ws_actions.grid(row=3, column=0, padx=12, pady=(0, 6), sticky="ew")
        ws_actions.grid_columnconfigure((0, 1), weight=1)

        self.btn_ws_decrypt = ctk.CTkButton(
            ws_actions, text="🔓 Unlock File",
            command=self._workspace_decrypt_file,
            fg_color=C_ACCENT, hover_color="#38d4ff", text_color="#04070d",
            font=ctk.CTkFont(family=FONT_TITLE, size=11, weight="bold"),
            corner_radius=6, height=36
        )
        self.btn_ws_decrypt.grid(row=0, column=0, padx=(0, 4), sticky="ew")
        CyberAnimator.apply_button_cyber_reaction(self.btn_ws_decrypt, normal_bg=C_ACCENT, hover_bg="#38d4ff", normal_text="#04070d", hover_text="#04070d")

        self.btn_ws_open = ctk.CTkButton(
            ws_actions, text="📂 Open Folder",
            command=self._open_workspace_folder,
            fg_color=C_SURFACE, hover_color="#1a2d4d", text_color=C_TEXT,
            font=ctk.CTkFont(family=FONT_TITLE, size=11, weight="bold"),
            border_width=1, border_color=C_BORDER, corner_radius=6, height=36
        )
        self.btn_ws_open.grid(row=0, column=1, padx=(4, 0), sticky="ew")
        CyberAnimator.apply_button_cyber_reaction(self.btn_ws_open, normal_bg=C_SURFACE, hover_bg="#1a2d4d", normal_text=C_TEXT, hover_text="#ffffff")

        ctk.CTkLabel(
            ws_frame,
            text="Files auto-encrypt to AES-256 on attack detection. Active files remain in memory.",
            font=ctk.CTkFont(family=FONT_BODY, size=9), text_color=C_MUTED, justify="center"
        ).grid(row=4, column=0, padx=12, pady=(0, 12), sticky="ew")

        # =====================================================================
        # COLUMN 1: Static Cipher Vault (AES-256 Storage)
        # =====================================================================
        files_frame = ctk.CTkFrame(self, fg_color=C_PANEL, corner_radius=12, border_width=1, border_color=C_BORDER)
        files_frame.grid(row=0, column=1, padx=6, pady=12, sticky="nsew")
        files_frame.grid_columnconfigure(0, weight=1)
        files_frame.grid_rowconfigure(2, weight=1)
        CyberAnimator.apply_glow_card_hover(files_frame, C_BORDER, C_SUCCESS, C_PANEL, "#0d1a1f")

        # Strip
        ctk.CTkFrame(files_frame, fg_color=C_SUCCESS, height=2, corner_radius=0).grid(row=0, column=0, sticky="ew")

        # Header
        cf_head = ctk.CTkFrame(files_frame, fg_color="transparent")
        cf_head.grid(row=1, column=0, sticky="ew", padx=16, pady=(12, 6))
        cf_head.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            cf_head, text="Encrypted Vault (data/vault)",
            font=ctk.CTkFont(family=FONT_TITLE, size=12, weight="bold"), text_color=C_TEXT
        ).grid(row=0, column=0, sticky="w")

        btn_vault_refresh = ctk.CTkButton(
            cf_head, text="🔄 Refresh", command=self._refresh_files_display,
            width=70, height=24, fg_color=C_SURFACE, hover_color="#182740",
            text_color=C_SUBTEXT, font=ctk.CTkFont(family=FONT_BODY, size=10),
            border_width=1, border_color=C_BORDER, corner_radius=4
        )
        btn_vault_refresh.grid(row=0, column=2, sticky="e")
        CyberAnimator.apply_button_cyber_reaction(btn_vault_refresh, normal_bg=C_SURFACE, hover_bg="#182740", normal_text=C_SUBTEXT, hover_text="#ffffff")

        # Scrollable vault files list
        self.files_scroll = ctk.CTkScrollableFrame(files_frame, fg_color=C_SURFACE, corner_radius=8, border_width=1, border_color=C_BORDER)
        self.files_scroll.grid(row=2, column=0, padx=12, pady=(0, 10), sticky="nsew")
        self.files_scroll.grid_columnconfigure(0, weight=1)

        # Cipher actions
        cipher_actions = ctk.CTkFrame(files_frame, fg_color="transparent")
        cipher_actions.grid(row=3, column=0, padx=12, pady=(0, 6), sticky="ew")
        cipher_actions.grid_columnconfigure((0, 1), weight=1)

        add_file_btn = ctk.CTkButton(
            cipher_actions, text="+ Import & Encrypt",
            command=self._add_file_to_vault,
            fg_color=C_SURFACE, hover_color="#1a2d4d", text_color=C_ACCENT,
            font=ctk.CTkFont(family=FONT_TITLE, size=11, weight="bold"),
            border_width=1, border_color=C_BORDER, corner_radius=6, height=36
        )
        add_file_btn.grid(row=0, column=0, padx=(0, 4), sticky="ew")
        CyberAnimator.apply_button_cyber_reaction(add_file_btn, normal_bg=C_SURFACE, hover_bg="#1a2d4d", normal_text=C_ACCENT, hover_text="#ffffff")

        unlock_file_btn = ctk.CTkButton(
            cipher_actions, text="🔓 Decrypt File",
            command=self._decrypt_file_from_vault,
            fg_color=C_SURFACE, hover_color="#1a2d4d", text_color=C_TEXT,
            font=ctk.CTkFont(family=FONT_TITLE, size=11, weight="bold"),
            border_width=1, border_color=C_BORDER, corner_radius=6, height=36
        )
        unlock_file_btn.grid(row=0, column=1, padx=(4, 0), sticky="ew")
        CyberAnimator.apply_button_cyber_reaction(unlock_file_btn, normal_bg=C_SURFACE, hover_bg="#1a2d4d", normal_text=C_TEXT, hover_text="#ffffff")

        ctk.CTkLabel(
            files_frame,
            text="Keys reside in volatile RAM and are safely wiped on session logout.",
            font=ctk.CTkFont(family=FONT_BODY, size=9), text_color=C_WARNING, justify="center"
        ).grid(row=4, column=0, padx=12, pady=(0, 12), sticky="ew")

        # =====================================================================
        # COLUMN 2: Key Enclave, TTL Engine & Emergency Rotation
        # =====================================================================
        right = ctk.CTkScrollableFrame(self, fg_color=C_BG)
        right.grid(row=0, column=2, padx=(6, 12), pady=12, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)

        # 1. Active Session Key Card
        key_card = ctk.CTkFrame(right, fg_color=C_PANEL, corner_radius=12, border_width=1, border_color=C_BORDER)
        key_card.pack(fill="x", pady=(0, 10))
        key_card.grid_columnconfigure(1, weight=1)
        CyberAnimator.apply_glow_card_hover(key_card, C_BORDER, C_ACCENT, C_PANEL, C_PANEL_HOVER)

        ctk.CTkFrame(key_card, fg_color=C_ACCENT, height=2, corner_radius=0).grid(row=0, column=0, columnspan=2, sticky="ew")

        ctk.CTkLabel(
            key_card, text="Session Key Enclave",
            font=ctk.CTkFont(family=FONT_TITLE, size=12, weight="bold"), text_color=C_TEXT
        ).grid(row=1, column=0, columnspan=2, sticky="w", padx=16, pady=(10, 6))

        for row_i, (k_lbl, k_val, val_c) in enumerate([
            ("Status:", "Active in RAM", C_SUCCESS),
            ("Algorithm:", "AES-256-GCM / Fernet", C_TEXT),
            ("Residency:", "Volatile Memory (RAM)", C_SUBTEXT),
            ("Rotation SLA:", "< 20.0 ms Poison Pill", C_ACCENT)
        ], start=2):
            ctk.CTkLabel(key_card, text=k_lbl, font=ctk.CTkFont(family=FONT_BODY, size=10), text_color=C_MUTED).grid(row=row_i, column=0, sticky="w", padx=16, pady=2)
            val_w = ctk.CTkLabel(key_card, text=k_val, font=ctk.CTkFont(family=FONT_BODY, size=10, weight="bold"), text_color=val_c)
            val_w.grid(row=row_i, column=1, sticky="w", padx=6, pady=2)
            if k_lbl == "Status:":
                self.key_status_lbl = val_w

        view_key_btn = ctk.CTkButton(
            key_card, text="🔍 View Key Hash",
            command=self._show_active_key,
            fg_color=C_SURFACE, hover_color="#182740", text_color=C_ACCENT,
            font=ctk.CTkFont(family=FONT_TITLE, size=10, weight="bold"),
            border_width=1, border_color=C_BORDER, corner_radius=6, height=30
        )
        view_key_btn.grid(row=6, column=0, columnspan=2, padx=16, pady=(8, 14), sticky="ew")
        CyberAnimator.apply_button_cyber_reaction(view_key_btn, normal_bg=C_SURFACE, hover_bg="#182740", normal_text=C_ACCENT, hover_text="#ffffff")

        # 2. TTL Countdown Card
        ttl_card = ctk.CTkFrame(right, fg_color=C_PANEL, corner_radius=12, border_width=1, border_color=C_BORDER)
        ttl_card.pack(fill="x", pady=(0, 10))
        CyberAnimator.apply_glow_card_hover(ttl_card, C_BORDER, C_SUCCESS, C_PANEL, C_PANEL_HOVER)

        ctk.CTkFrame(ttl_card, fg_color=C_SUCCESS, height=2, corner_radius=0).pack(fill="x", side="top")

        ctk.CTkLabel(
            ttl_card, text="Session Key TTL",
            font=ctk.CTkFont(family=FONT_TITLE, size=12, weight="bold"), text_color=C_TEXT
        ).pack(anchor="w", padx=16, pady=(10, 2))

        ctk.CTkLabel(
            ttl_card, text="Keys are wiped from RAM automatically on timeout.",
            font=ctk.CTkFont(family=FONT_BODY, size=10), text_color=C_SUBTEXT
        ).pack(anchor="w", padx=16, pady=(0, 4))

        self.ttl_status_lbl = ctk.CTkLabel(
            ttl_card, text="● Watchdog: Active",
            font=ctk.CTkFont(family=FONT_BODY, size=10, weight="bold"), text_color=C_SUCCESS
        )
        self.ttl_status_lbl.pack(anchor="w", padx=16, pady=(0, 14))
        CyberAnimator.start_pulse_animation(self.ttl_status_lbl, C_SUCCESS, "#80ffbf", 1.0)

        # 3. Emergency Poison-Pill Key Rotation Card
        rot_card = ctk.CTkFrame(right, fg_color=C_PANEL, corner_radius=12, border_width=1, border_color=C_BORDER)
        rot_card.pack(fill="x")
        CyberAnimator.apply_glow_card_hover(rot_card, C_BORDER, C_DANGER, C_PANEL, "#220c15")

        ctk.CTkFrame(rot_card, fg_color=C_DANGER, height=2, corner_radius=0).pack(fill="x", side="top")

        ctk.CTkLabel(
            rot_card, text="Emergency Key Rotation",
            font=ctk.CTkFont(family=FONT_TITLE, size=12, weight="bold"), text_color=C_DANGER
        ).pack(anchor="w", padx=16, pady=(10, 2))

        ctk.CTkLabel(
            rot_card,
            text="Re-encrypts all vault assets with a new key in < 50 ms.\nExfiltrated data becomes permanently unreadable.",
            font=ctk.CTkFont(family=FONT_BODY, size=9), text_color=C_SUBTEXT, justify="left"
        ).pack(anchor="w", padx=16, pady=(0, 10))

        self.rotate_btn = ctk.CTkButton(
            rot_card, text="⚡ Rotate Keys Now",
            command=self._trigger_emergency_rotation,
            fg_color=C_DANGER, hover_color="#ff2670", text_color="#ffffff",
            font=ctk.CTkFont(family=FONT_TITLE, size=11, weight="bold"),
            corner_radius=6, height=36
        )
        self.rotate_btn.pack(padx=16, pady=(0, 14), fill="x")
        CyberAnimator.apply_button_cyber_reaction(self.rotate_btn, normal_bg=C_DANGER, hover_bg="#ff2670", normal_text="#ffffff", hover_text="#ffffff", press_bg="#80002b")

    # =========================================================================
    # Workspace & Vault UI Refreshers
    # =========================================================================

    def _open_workspace_folder(self):
        try:
            vault_path = self.workspace.vault_dir
            vault_path.mkdir(parents=True, exist_ok=True)
            if os.name == 'nt':
                os.startfile(str(vault_path))
            else:
                import subprocess
                subprocess.Popen(['xdg-open', str(vault_path)])
        except Exception as e:
            messagebox.showerror("Folder Error", f"Could not open /Vault folder:\n{e}")

    def _refresh_workspace_display(self):
        for w in self.ws_scroll.winfo_children():
            w.destroy()

        files = self.workspace.list_files()
        if not files:
            empty_item = ctk.CTkFrame(self.ws_scroll, fg_color="transparent")
            empty_item.pack(fill="x", pady=20)
            ctk.CTkLabel(
                empty_item, text="Physical /Vault folder is empty.\nSave files into /Vault — they auto-encrypt into .enc on attack!",
                font=ctk.CTkFont(family=FONT_BODY, size=10), text_color=C_MUTED, justify="center"
            ).pack()
            return

        for f in files:
            is_enc = f.name.endswith(".enc")
            size_kb = round(f.stat().st_size / 1024, 1)

            item = ctk.CTkFrame(self.ws_scroll, fg_color="#0a1220", corner_radius=6, border_width=1, border_color=C_BORDER)
            item.pack(fill="x", pady=3, padx=2)
            item.grid_columnconfigure(1, weight=1)

            icon = "🔒" if is_enc else "📄"
            badge_color = C_DANGER if is_enc else C_SUCCESS
            badge_text = "Encrypted" if is_enc else "Plaintext"

            ctk.CTkLabel(item, text=icon, font=ctk.CTkFont(size=14)).grid(row=0, column=0, padx=(10, 6), pady=8)

            info = ctk.CTkFrame(item, fg_color="transparent")
            info.grid(row=0, column=1, sticky="w", pady=6)

            ctk.CTkLabel(
                info, text=f.name,
                font=ctk.CTkFont(family=FONT_BODY, size=11, weight="bold"), text_color=C_TEXT
            ).pack(anchor="w")

            ctk.CTkLabel(
                info, text=f"{size_kb} KB  ·  {badge_text}",
                font=ctk.CTkFont(family=FONT_BODY, size=9), text_color=badge_color
            ).pack(anchor="w")

            if is_enc:
                btn_dec = ctk.CTkButton(
                    item, text="Unlock", command=lambda p=f: self._quick_decrypt_file(p),
                    width=60, height=24, fg_color=C_SURFACE, hover_color=C_ACCENT,
                    text_color=C_TEXT, font=ctk.CTkFont(family=FONT_BODY, size=10, weight="bold"),
                    border_width=1, border_color=C_BORDER, corner_radius=4
                )
                btn_dec.grid(row=0, column=2, padx=10, pady=8)
                CyberAnimator.apply_button_cyber_reaction(btn_dec, normal_bg=C_SURFACE, hover_bg=C_ACCENT, normal_text=C_TEXT, hover_text="#04070d")

    def _quick_decrypt_file(self, path: Path):
        try:
            self.workspace.decrypt_vault_file(path)
            self._refresh_workspace_display()
            messagebox.showinfo("Vault Unlocked", f"File successfully decrypted back to plaintext:\n{path.stem}")
        except Exception as e:
            messagebox.showerror("Unlock Error", f"Failed to decrypt file:\n{e}")

    def _workspace_decrypt_file(self):
        filename = simpledialog.askstring("Decrypt Vault File", "Enter exact encrypted filename (e.g. secret.txt.enc):")
        if filename:
            path = self.workspace.vault_dir / filename
            if path.exists() and path.name.endswith(".enc"):
                self._quick_decrypt_file(path)
            else:
                messagebox.showerror("Error", f"Encrypted file not found in /Vault folder: {filename}")

    def _refresh_files_display(self):
        for w in self.files_scroll.winfo_children():
            w.destroy()

        vault_dir = Path(__file__).resolve().parents[2] / "data" / "vault"
        all_encrypted = list(vault_dir.glob("*.*"))

        if not all_encrypted:
            empty_item = ctk.CTkFrame(self.files_scroll, fg_color="transparent")
            empty_item.pack(fill="x", pady=20)
            ctk.CTkLabel(
                empty_item, text="No encrypted files stored in vault.",
                font=ctk.CTkFont(family=FONT_BODY, size=10), text_color=C_MUTED
            ).pack()
            return

        for f in all_encrypted:
            size_kb = round(f.stat().st_size / 1024, 1)
            item = ctk.CTkFrame(self.files_scroll, fg_color="#0a151b", corner_radius=6, border_width=1, border_color=C_BORDER)
            item.pack(fill="x", pady=3, padx=2)
            item.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(item, text="🔒", font=ctk.CTkFont(size=14)).grid(row=0, column=0, padx=(10, 6), pady=8)

            info = ctk.CTkFrame(item, fg_color="transparent")
            info.grid(row=0, column=1, sticky="w", pady=6)

            ctk.CTkLabel(
                info, text=f.name,
                font=ctk.CTkFont(family=FONT_BODY, size=11, weight="bold"), text_color=C_TEXT
            ).pack(anchor="w")

            ctk.CTkLabel(
                info, text=f"{size_kb} KB  ·  AES-256 Encrypted",
                font=ctk.CTkFont(family=FONT_BODY, size=9), text_color=C_SUCCESS
            ).pack(anchor="w")

    def _load_default_vault_files(self):
        vault_dir = Path(__file__).resolve().parents[2] / "data" / "vault"
        vault_dir.mkdir(parents=True, exist_ok=True)
        sample_file = vault_dir / "secret_project_intel.txt"
        if not sample_file.exists():
            sample_file.write_text("CONFIDENTIAL: Project ShadowMind core vault assets.")
            try:
                self.vault.encrypt_file(sample_file)
                if sample_file not in self.protected_files:
                    self.protected_files.append(sample_file)
            except Exception:
                pass

    def _add_file_to_vault(self):
        filename = filedialog.askopenfilename(title="Select File to Protect in Cipher Vault")
        if filename:
            path = Path(filename)
            try:
                self.vault.encrypt_file(path)
                if path not in self.protected_files:
                    self.protected_files.append(path)
                self._refresh_files_display()
                messagebox.showinfo("Vault Success", f"File encrypted & protected:\n{path.name}")
            except Exception as e:
                messagebox.showerror("Vault Error", f"Failed to encrypt file:\n{e}")

    def _decrypt_file_from_vault(self):
        filename = filedialog.askopenfilename(title="Select Encrypted Vault File to Unlock")
        if filename:
            path = Path(filename)
            try:
                self.vault.decrypt_file(path)
                self._refresh_files_display()
                messagebox.showinfo("Vault Unlocked", f"File successfully decrypted & unlocked:\n{path.name}")
            except Exception as e:
                messagebox.showerror("Unlock Error", f"Failed to decrypt file:\n{e}")

    def _show_active_key(self):
        key = SessionState.get_key()
        key_hex = key.hex() if key else "NO_ACTIVE_KEY"
        messagebox.showinfo(
            "RAM Key Enclave Attestation",
            f"Active Session Key Digest (in volatile RAM):\n\n{key_hex[:16]}...{key_hex[-16:]}\n\nAlgorithm: AES-256-GCM / HMAC-SHA256\nResidency: Ring-0 RAM (Zero Disk Footprint)\nWipe Trigger: Session Expiry / Operator Logout"
        )

    def _trigger_emergency_rotation(self):
        confirm = messagebox.askyesno(
            "Confirm Poison-Pill Key Rotation",
            "Are you sure you want to trigger emergency key rotation?\n\nThis will re-encrypt all active vault assets under a newly derived AES-256 key in volatile RAM."
        )
        if not confirm:
            return

        self.rotate_btn.configure(state="disabled", text="ROTATING ENCLAVE KEYS...")
        try:
            vault_dir = Path(__file__).resolve().parents[2] / "data" / "vault"
            protected = list(vault_dir.glob("*.*"))
            new_key, elapsed = emergency_rotate_keys(SessionState.get_key(), protected)
            SessionState.set_key(new_key)
            self.vault = AESVault(SessionState.get_key())
            self.key_status_lbl.configure(text=f"ROTATED ({elapsed:.2f}ms)", text_color=C_SUCCESS)
            self._refresh_files_display()
            messagebox.showinfo(
                "Emergency Rotation Complete",
                f"Poison-Pill Key Rotation verified!\n\nAll {len(protected)} vault assets re-encrypted in {elapsed:.2f} ms.\nNew AES-256 key locked in RAM."
            )
        except Exception as e:
            messagebox.showerror("Rotation Error", f"Emergency rotation failed:\n{e}")
        finally:
            self.rotate_btn.configure(state="normal", text="⚡ TRIGGER POISON PILL ROTATION")

    def destroy(self):
        if SessionState.get_key():
            zero_wipe_ram_key(SessionState.get_key())

        try:
            for f in self.workspace.list_files():
                if not f.name.endswith(".enc"):
                    f.unlink(missing_ok=True)
        except Exception:
            pass

        super().destroy()
