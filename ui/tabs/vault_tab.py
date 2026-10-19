# =============================================================================
# FILE: ui/tabs/vault_tab.py
# PURPOSE: File Vault & Active Workspace Tab UI (Fully wired in Phases 3 & 5).
#          - File Vault: Static encrypted storage with AES-256 session keys.
#          - Active Workspace Vault: Plaintext working directory for normal daily use
#            (create, edit, delete freely) that auto-locks into AES ciphertext instantly
#            upon attack detection.
# =============================================================================

import customtkinter as ctk
from tkinter import filedialog, messagebox, simpledialog
from pathlib import Path
import time
import threading

from src.auth.auth import Session
from src.vault.keygen import generate_session_key
from src.vault.aes_vault import AESVault
from src.vault.rotation import emergency_rotate_keys
from src.vault.ttl_destruct import zero_wipe_ram_key
from src.vault.session_state import SessionState
from src.workspace.workspace_vault import LocalStorageVault

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
    Poison Pill Vault & Active Workspace UI.
    """

    def __init__(self, parent, session: Session):
        super().__init__(parent, fg_color=C_BG)
        self.session = session
        
        self.vault = AESVault(SessionState.get_key())
        self.workspace = LocalStorageVault()
        self.protected_files = []

        self._build()
        self._load_default_vault_files()
        self._refresh_workspace_display()

    def _build(self):
        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure(0, weight=1)

        # =====================================================================
        # COLUMN 0: Active Workspace Vault (Plaintext, Auto-Locking)
        # =====================================================================
        ws_frame = ctk.CTkFrame(self, fg_color=C_PANEL, corner_radius=10)
        ws_frame.grid(row=0, column=0, padx=(12, 6), pady=12, sticky="nsew")
        ws_frame.grid_rowconfigure(1, weight=1)
        ws_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            ws_frame, text="Active Workspace (Plaintext)",
            font=ctk.CTkFont(size=14, weight="bold"), text_color=C_TEXT
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(12, 4))

        self.ws_box = ctk.CTkTextbox(
            ws_frame, fg_color="#0a0c10", text_color=C_TEXT,
            font=ctk.CTkFont(family="Courier New", size=11), state="disabled"
        )
        self.ws_box.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="nsew")

        ctk.CTkButton(
            ws_frame, text="+ Create / Edit File",
            command=self._workspace_create_file,
            fg_color=C_SUCCESS, hover_color="#00994d", text_color="#000000",
            corner_radius=8
        ).grid(row=2, column=0, padx=12, pady=(0, 6), sticky="ew")

        ctk.CTkButton(
            ws_frame, text="🗑️ Delete File",
            command=self._workspace_delete_file,
            fg_color="#333842", hover_color="#444a56", text_color=C_TEXT,
            corner_radius=8
        ).grid(row=3, column=0, padx=12, pady=(0, 6), sticky="ew")

        ctk.CTkLabel(
            ws_frame,
            text="💡 Normal daily files.\nAuto-encrypts instantly on breach!",
            font=ctk.CTkFont(size=10), text_color=C_SUBTEXT, justify="center"
        ).grid(row=4, column=0, padx=12, pady=(0, 12), sticky="ew")

        # =====================================================================
        # COLUMN 1: Static Poison Pill Vault (Encrypted Storage)
        # =====================================================================
        files_frame = ctk.CTkFrame(self, fg_color=C_PANEL, corner_radius=10)
        files_frame.grid(row=0, column=1, padx=6, pady=12, sticky="nsew")
        files_frame.grid_rowconfigure(1, weight=1)
        files_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            files_frame, text="Secure Vault (AES-256)",
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

        warning_lbl = ctk.CTkLabel(
            files_frame,
            text="⚠️ RAM-only keys.\nDecrypt before logout!",
            font=ctk.CTkFont(size=10), text_color=C_WARNING, justify="center"
        )
        warning_lbl.grid(row=4, column=0, padx=12, pady=(0, 12), sticky="ew")

        # =====================================================================
        # COLUMN 2: Key Status, TTL, & Emergency Rotation
        # =====================================================================
        right = ctk.CTkFrame(self, fg_color=C_BG)
        right.grid(row=0, column=2, padx=(6, 12), pady=12, sticky="nsew")
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

        ctk.CTkButton(
            key_card, text="🔍 View Active Key (RAM)",
            command=self._show_active_key,
            fg_color="#1f2430", hover_color="#2b3140", text_color=C_ACCENT,
            font=ctk.CTkFont(size=11), corner_radius=6, height=28
        ).grid(row=3, column=0, padx=16, pady=(0, 12), sticky="ew")

        # TTL countdown card
        ttl_card = ctk.CTkFrame(right, fg_color=C_PANEL, corner_radius=10)
        ttl_card.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        ttl_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(ttl_card, text="TTL Self-Destruct Engine",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=C_TEXT).grid(row=0, column=0, sticky="w", padx=16, pady=(12, 4))
        self.ttl_status_lbl = ctk.CTkLabel(ttl_card, text="Status: Armed & Active",
                                           font=ctk.CTkFont(size=12, weight="bold"),
                                           text_color=C_ACCENT)
        self.ttl_status_lbl.grid(row=1, column=0, sticky="w", padx=16, pady=(0, 12))

        # Emergency rotation card
        rot_card = ctk.CTkFrame(right, fg_color=C_PANEL, corner_radius=10)
        rot_card.grid(row=2, column=0, sticky="ew")
        rot_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(rot_card, text="Emergency Key Rotation",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=C_TEXT).grid(row=0, column=0, sticky="w", padx=16, pady=(12, 4))
        
        self.rotate_btn = ctk.CTkButton(
            rot_card, text="ROTATE KEY NOW",
            command=self._trigger_emergency_rotation,
            fg_color=C_DANGER, hover_color="#cc0000",
            font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=8
        )
        self.rotate_btn.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="ew")

    # --- Workspace Handlers ---
    def _workspace_create_file(self):
        filename = simpledialog.askstring("Workspace File", "Enter filename (e.g. notes.txt):")
        if filename:
            content = simpledialog.askstring("File Content", "Enter plaintext content:")
            if content is not None:
                self.workspace.create_or_edit_file(filename, content)
                self._refresh_workspace_display()
                messagebox.showinfo("Workspace", f"Plaintext file created/edited: {filename}")

    def _workspace_delete_file(self):
        filename = simpledialog.askstring("Delete File", "Enter exact filename to delete:")
        if filename:
            if self.workspace.delete_file(filename):
                self._refresh_workspace_display()
                messagebox.showinfo("Workspace", f"File deleted: {filename}")
            else:
                messagebox.showerror("Error", f"File not found: {filename}")

    def _refresh_workspace_display(self):
        files = self.workspace.list_workspace_files()
        self.ws_box.configure(state="normal")
        self.ws_box.delete("1.0", "end")
        if not files:
            self.ws_box.insert("end", "Workspace empty.\nCreate files freely.\nThey auto-lock on attack!")
        else:
            for f in files:
                self.ws_box.insert("end", f"📄 [PLAIN] {f.name}\n")
        self.ws_box.configure(state="disabled")

    # --- Vault Handlers ---
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
            self._refresh_files_display()
        except Exception as e:
            pass

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
                messagebox.showerror("Unlock Error", f"Failed to decrypt file:\n{e}")

    def _show_active_key(self):
        key_hex = SessionState.get_key().hex()
        messagebox.showinfo(
            "Active RAM Session Key",
            f"Active AES-256 Key (in RAM only):\n\n{key_hex}\n\nNote: Zero-wiped upon session logout."
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
                f"All files re-encrypted successfully in {elapsed:.2f} ms!"
            )
        except Exception as e:
            messagebox.showerror("Rotation Error", f"Emergency rotation failed:\n{e}")
        finally:
            self.rotate_btn.configure(state="normal", text="ROTATE KEY NOW")

    def _refresh_files_display(self):
        self.files_box.configure(state="normal")
        self.files_box.delete("1.0", "end")
        vault_dir = Path(__file__).resolve().parents[2] / "data" / "vault"
        all_encrypted = list(vault_dir.glob("*.*"))
        if not all_encrypted:
            self.files_box.insert("end", "No encrypted files in vault.\n")
        else:
            for f in all_encrypted:
                self.files_box.insert("end", f"🔒 [AES-256] {f.name}\n")
        self.files_box.configure(state="disabled")

    def destroy(self):
        if SessionState.get_key():
            zero_wipe_ram_key(SessionState.get_key())
        super().destroy()
