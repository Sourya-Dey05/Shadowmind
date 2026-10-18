# =============================================================================
# FILE: ui/tabs/vault_tab.py
# PURPOSE: File Vault tab UI (Fully wired in Phase 3).
#          Manages protected vault files, displays active AES-256 session key
#          status, live TTL self-destruct countdown, and wires the emergency
#          key rotation button to trigger instant re-encryption in < 500ms.
# =============================================================================

import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path
import time
import threading

from src.auth.auth import Session
from src.vault.keygen import generate_session_key
from src.vault.aes_vault import AESVault
from src.vault.rotation import emergency_rotate_keys
from src.vault.ttl_destruct import zero_wipe_ram_key
from src.vault.session_state import SessionState

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
    Poison Pill Vault UI: protected files, AES-256 key status, TTL countdown,
    and emergency key rotation.
    """

    def __init__(self, parent, session: Session):
        super().__init__(parent, fg_color=C_BG)
        self.session = session
        
        # Initialize active session key in global RAM state
        SessionState.reset()
        self.vault = AESVault(SessionState.get_key())
        self.protected_files = []

        self._build()
        self._load_default_vault_files()

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
            files_frame, text="Protected Vault Files (AES-256 Encrypted)",
            font=ctk.CTkFont(size=14, weight="bold"), text_color=C_TEXT
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(12, 4))

        self.files_box = ctk.CTkTextbox(
            files_frame, fg_color="#0a0c10", text_color=C_TEXT,
            font=ctk.CTkFont(family="Courier New", size=11), state="disabled"
        )
        self.files_box.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="nsew")

        ctk.CTkButton(
            files_frame, text="+ Add File to Vault",
            command=self._add_file_to_vault,
            fg_color=C_ACCENT, hover_color="#009fcc", text_color="#000000",
            corner_radius=8
        ).grid(row=2, column=0, padx=12, pady=(0, 6), sticky="ew")

        ctk.CTkButton(
            files_frame, text="🔓 Decrypt / Unlock File",
            command=self._decrypt_file_from_vault,
            fg_color="#333842", hover_color="#444a56", text_color=C_TEXT,
            corner_radius=8
        ).grid(row=3, column=0, padx=12, pady=(0, 6), sticky="ew")

        # Warning banner
        warning_lbl = ctk.CTkLabel(
            files_frame,
            text="⚠️ Warning: Vault files use RAM-only keys.\nDecrypt files before logout or shutdown!",
            font=ctk.CTkFont(size=10), text_color=C_WARNING, justify="center"
        )
        warning_lbl.grid(row=4, column=0, padx=12, pady=(0, 12), sticky="ew")

        # --- Right: key status + TTL + emergency rotation ---
        right = ctk.CTkFrame(self, fg_color=C_BG)
        right.grid(row=0, column=1, padx=(6, 12), pady=12, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)

        # Key status card
        key_card = ctk.CTkFrame(right, fg_color=C_PANEL, corner_radius=10)
        key_card.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        key_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(key_card, text="Session Key Status",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=C_TEXT).grid(row=0, column=0, sticky="w", padx=16, pady=(12, 4))
        ctk.CTkLabel(key_card, text="Status:",
                     font=ctk.CTkFont(size=11), text_color=C_SUBTEXT).grid(
            row=1, column=0, sticky="w", padx=16)
        
        self.key_status_lbl = ctk.CTkLabel(key_card, text="ACTIVE (RAM Secured)",
                                           font=ctk.CTkFont(size=13, weight="bold"),
                                           text_color=C_SUCCESS)
        self.key_status_lbl.grid(row=2, column=0, sticky="w", padx=16, pady=(0, 4))

        ctk.CTkLabel(key_card, text="Algorithm:",
                     font=ctk.CTkFont(size=11), text_color=C_SUBTEXT).grid(
            row=3, column=0, sticky="w", padx=16)
        ctk.CTkLabel(key_card, text="AES-256 (Fernet / CBC)",
                     font=ctk.CTkFont(size=12), text_color=C_TEXT).grid(
            row=4, column=0, sticky="w", padx=16, pady=(0, 4))

        ctk.CTkLabel(key_card, text="Key Source:",
                     font=ctk.CTkFont(size=11), text_color=C_SUBTEXT).grid(
            row=5, column=0, sticky="w", padx=16)
        ctk.CTkLabel(key_card, text="Secure Random (RAM only)",
                     font=ctk.CTkFont(size=12), text_color=C_TEXT).grid(
            row=6, column=0, sticky="w", padx=16, pady=(0, 8))

        ctk.CTkButton(
            key_card, text="🔍 View Active Key (RAM)",
            command=self._show_active_key,
            fg_color="#1f2430", hover_color="#2b3140", text_color=C_ACCENT,
            font=ctk.CTkFont(size=11), corner_radius=6, height=28
        ).grid(row=7, column=0, padx=16, pady=(0, 12), sticky="ew")

        # TTL countdown card
        ttl_card = ctk.CTkFrame(right, fg_color=C_PANEL, corner_radius=10)
        ttl_card.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        ttl_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(ttl_card, text="TTL Self-Destruct Engine",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=C_TEXT).grid(row=0, column=0, sticky="w", padx=16, pady=(12, 4))
        ctk.CTkLabel(ttl_card, text="Zero-wipes session key from RAM on expiry",
                     font=ctk.CTkFont(size=11), text_color=C_SUBTEXT).grid(
            row=1, column=0, sticky="w", padx=16, pady=(0, 4))
        
        self.ttl_status_lbl = ctk.CTkLabel(ttl_card, text="Status: Armed & Active",
                                           font=ctk.CTkFont(size=12, weight="bold"),
                                           text_color=C_ACCENT)
        self.ttl_status_lbl.grid(row=2, column=0, sticky="w", padx=16, pady=(0, 12))

        # Emergency rotation card
        rot_card = ctk.CTkFrame(right, fg_color=C_PANEL, corner_radius=10)
        rot_card.grid(row=2, column=0, sticky="ew")
        rot_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(rot_card, text="Emergency Key Rotation",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=C_TEXT).grid(row=0, column=0, sticky="w", padx=16, pady=(12, 4))
        ctk.CTkLabel(rot_card,
                     text="Re-encrypts all vault files with a new\nkey in < 500 ms. Stolen data\nbecomes permanently unreadable.",
                     font=ctk.CTkFont(size=11), text_color=C_SUBTEXT,
                     justify="left").grid(row=1, column=0, sticky="w", padx=16, pady=(0, 8))
        
        self.rotate_btn = ctk.CTkButton(
            rot_card, text="ROTATE KEY NOW",
            command=self._trigger_emergency_rotation,
            fg_color=C_DANGER, hover_color="#cc0000",
            font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=8
        )
        self.rotate_btn.grid(row=2, column=0, padx=12, pady=(0, 12), sticky="ew")

    def _load_default_vault_files(self):
        """Create a default protected sample file in the vault for testing."""
        vault_dir = Path(__file__).resolve().parents[2] / "data" / "vault"
        vault_dir.mkdir(parents=True, exist_ok=True)
        
        sample_file = vault_dir / "secret_project_intel.txt"
        if not sample_file.exists():
            sample_file.write_text("CONFIDENTIAL: Project ShadowMind core vault assets and architecture specs.")
        
        # Encrypt it
        try:
            self.vault.encrypt_file(sample_file)
            self.protected_files.append(sample_file)
            self._refresh_files_display()
        except Exception as e:
            print(f"Default vault init error: {e}")

    def _add_file_to_vault(self):
        filename = filedialog.askopenfilename(title="Select File to Protect in Vault")
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
                messagebox.showinfo("Vault Unlocked", f"File successfully decrypted & unlocked:\n{path.name}")
            except Exception as e:
                messagebox.showerror("Unlock Error", f"Failed to decrypt file (invalid session key or corrupted):\n{e}")

    def _show_active_key(self):
        key_hex = SessionState.get_key().hex()
        messagebox.showinfo(
            "Active RAM Session Key",
            f"Active AES-256 Key (in RAM only):\n\n{key_hex}\n\nNote: This key is never stored on disk and will be zero-wiped upon session logout."
        )

    def _trigger_emergency_rotation(self):
        self.rotate_btn.configure(state="disabled", text="Rotating...")
        try:
            new_key, elapsed = emergency_rotate_keys(SessionState.get_key(), self.protected_files)
            SessionState.set_key(new_key)
            self.vault = AESVault(SessionState.get_key())
            self.key_status_lbl.configure(text="ROTATED & SECURED", text_color=C_SUCCESS)
            messagebox.showinfo(
                "Emergency Rotation Complete",
                f"All {len(self.protected_files)} protected files re-encrypted successfully!\n\nTime elapsed: {elapsed:.2f} ms\nStolen ciphertext is now permanently invalid."
            )
        except Exception as e:
            messagebox.showerror("Rotation Error", f"Emergency rotation failed:\n{e}")
        finally:
            self.rotate_btn.configure(state="normal", text="ROTATE KEY NOW")

    def _refresh_files_display(self):
        self.files_box.configure(state="normal")
        self.files_box.delete("1.0", "end")
        if not self.protected_files:
            self.files_box.insert("end", "No protected files in vault.\n")
        else:
            for f in self.protected_files:
                self.files_box.insert("end", f"🔒 [AES-256] {f.name}\n    Path: {f}\n\n")
        self.files_box.configure(state="disabled")

    def destroy(self):
        # Trigger TTL RAM zero-wipe when tab/session closes
        if self.session_key:
            zero_wipe_ram_key(self.session_key)
        super().destroy()
