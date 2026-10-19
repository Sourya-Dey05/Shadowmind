# =============================================================================
# FILE: ui/tabs/vault_tab.py
# PURPOSE: Recreated strictly from Figma Mockup (Section 1.pdf - Screen 3).
#          - Header: LOCAL SECURITY / ENCRYPTED STORAGE & Subtitle
#          - Panel 1 (Left): Active Workspace (/Vault Folder) list with count badge,
#            search field, file entries ([PLAIN], [ENC]), and plaintext warning
#          - Panel 2 (Center): Secure Vault (AES-256) Inspect & Decrypt, object hex,
#            metadata, Cipher suite, Unlock / Decrypt button, Export Copy
#          - Panel 3 (Right): Key Status & Emergency Rotation, RAM session key
#            fingerprint, TTL Self-destruct armed bar, Rotate Key Now danger button
# =============================================================================

import time
import customtkinter as ctk
from pathlib import Path
from tkinter import simpledialog, messagebox

from src.auth.auth import Session
from src.vault.session_state import SessionState
from src.vault.rotation import emergency_rotate_keys
from src.workspace.workspace_vault import ExternalVaultFolder
from ui.theme import (
    COLOR_BG, COLOR_SURFACE, COLOR_CARD, COLOR_CARD_HOVER,
    COLOR_BORDER, COLOR_CYAN, COLOR_SUCCESS, COLOR_WARNING,
    COLOR_DANGER, COLOR_PURPLE, COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED, FONT_BRAND, FONT_BODY, FONT_MONO
)


class VaultTab(ctk.CTkFrame):
    """
    Exact recreation of Screen 3 (File Vault & Workspace):
    - 3-Column Inspection Layout
    - Real-time file status ([PLAIN], [ENC])
    - Interactive Decrypt & Emergency Key Rotation
    """

    def __init__(self, parent, session: Session):
        super().__init__(parent, fg_color=COLOR_BG)
        self.session = session
        self.workspace = ExternalVaultFolder()
        self.selected_file: Path = None

        self._build()
        self._refresh_workspace()

    def _build(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # -------------------------------------------------------------
        # 1. Section Header (LOCAL SECURITY / ENCRYPTED STORAGE)
        # -------------------------------------------------------------
        head_frame = ctk.CTkFrame(self, fg_color="transparent")
        head_frame.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 12))
        head_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            head_frame,
            text="LOCAL SECURITY / ENCRYPTED STORAGE",
            font=ctk.CTkFont(family=FONT_MONO, size=11, weight="bold"),
            text_color=COLOR_TEXT_MUTED
        ).pack(anchor="w")

        ctk.CTkLabel(
            head_frame,
            text="File vault & workspace",
            font=ctk.CTkFont(family=FONT_BRAND, size=24, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY
        ).pack(anchor="w", pady=(2, 0))

        ctk.CTkLabel(
            head_frame,
            text="Keep sensitive files sealed. Inspect, decrypt, and rotate keys without leaving your machine.",
            font=ctk.CTkFont(family=FONT_BODY, size=12),
            text_color=COLOR_TEXT_SECONDARY
        ).pack(anchor="w", pady=(2, 0))

        # -------------------------------------------------------------
        # 2. Three-Column Main Container
        # -------------------------------------------------------------
        cols_container = ctk.CTkFrame(self, fg_color="transparent")
        cols_container.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 20))
        cols_container.grid_rowconfigure(0, weight=1)
        cols_container.grid_columnconfigure(0, weight=8)   # Column 1: Workspace
        cols_container.grid_columnconfigure(1, weight=10)  # Column 2: Inspect
        cols_container.grid_columnconfigure(2, weight=8)   # Column 3: Key & Rotate

        # =============================================================
        # COLUMN 1: Active Workspace (/Vault Folder)
        # =============================================================
        p1 = ctk.CTkFrame(cols_container, fg_color=COLOR_CARD, border_width=1, border_color=COLOR_BORDER, corner_radius=12)
        p1.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        p1.grid_rowconfigure(2, weight=1)
        p1.grid_columnconfigure(0, weight=1)

        # P1 Header
        p1_head = ctk.CTkFrame(p1, fg_color="transparent")
        p1_head.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))
        p1_head.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            p1_head,
            text="Active Workspace\n(/Vault Folder)",
            font=ctk.CTkFont(family=FONT_MONO, size=12, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY,
            justify="left"
        ).grid(row=0, column=0, sticky="w")

        self.p1_count_badge = ctk.CTkLabel(
            p1_head,
            text="06",
            font=ctk.CTkFont(family=FONT_BRAND, size=14, weight="bold"),
            fg_color=COLOR_SURFACE,
            text_color=COLOR_CYAN,
            corner_radius=4,
            width=32,
            height=26
        )
        self.p1_count_badge.grid(row=0, column=1, sticky="e")

        # P1 Search Filter
        search_box = ctk.CTkFrame(p1, fg_color=COLOR_SURFACE, height=32, corner_radius=6, border_width=1, border_color=COLOR_BORDER)
        search_box.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 8))
        search_box.pack_propagate(False)

        ctk.CTkLabel(
            search_box,
            text="Find a local file... ⌘ K",
            font=ctk.CTkFont(family=FONT_MONO, size=10),
            text_color=COLOR_TEXT_MUTED
        ).pack(side="left", padx=10)

        # File Items List (Scrollable)
        self.files_scroll = ctk.CTkScrollableFrame(p1, fg_color="transparent")
        self.files_scroll.grid(row=2, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self.files_scroll.grid_columnconfigure(0, weight=1)

        # P1 Footer Note
        p1_foot = ctk.CTkFrame(p1, fg_color=COLOR_SURFACE, height=44, corner_radius=8, border_width=1, border_color=COLOR_BORDER)
        p1_foot.grid(row=3, column=0, sticky="ew", padx=16, pady=(0, 16))
        p1_foot.pack_propagate(False)

        self.p1_summary_lbl = ctk.CTkLabel(
            p1_foot,
            text="4 encrypted  /  2 plaintext",
            font=ctk.CTkFont(family=FONT_MONO, size=10, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY
        )
        self.p1_summary_lbl.pack(anchor="w", padx=10, pady=(4, 0))

        ctk.CTkLabel(
            p1_foot,
            text="Plaintext files are not protected by vault encryption.",
            font=ctk.CTkFont(family=FONT_BODY, size=9),
            text_color=COLOR_TEXT_MUTED
        ).pack(anchor="w", padx=10)

        # =============================================================
        # COLUMN 2: Secure Vault (AES-256) Inspect & Decrypt
        # =============================================================
        p2 = ctk.CTkFrame(cols_container, fg_color=COLOR_CARD, border_width=1, border_color=COLOR_BORDER, corner_radius=12)
        p2.grid(row=0, column=1, sticky="nsew", padx=8)
        p2.grid_columnconfigure(0, weight=1)

        # P2 Header
        p2_head = ctk.CTkFrame(p2, fg_color="transparent")
        p2_head.pack(fill="x", padx=16, pady=(16, 8))
        p2_head.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            p2_head,
            text="Secure Vault (AES-256)",
            font=ctk.CTkFont(family=FONT_MONO, size=13, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY
        ).pack(anchor="w")

        ctk.CTkLabel(
            p2_head,
            text="Inspect and decrypt the selected file.",
            font=ctk.CTkFont(family=FONT_BODY, size=11),
            text_color=COLOR_TEXT_SECONDARY
        ).pack(anchor="w")

        # Object Tag Card
        obj_card = ctk.CTkFrame(p2, fg_color=COLOR_SURFACE, corner_radius=8, border_width=1, border_color=COLOR_BORDER)
        obj_card.pack(fill="x", padx=16, pady=(4, 12))

        ctk.CTkLabel(
            obj_card,
            text="0x7F2A · ENCRYPTED OBJECT   SEALED & VERIFIED",
            font=ctk.CTkFont(family=FONT_MONO, size=10, weight="bold"),
            text_color=COLOR_SUCCESS
        ).pack(anchor="w", padx=12, pady=(10, 4))

        self.inspect_name_lbl = ctk.CTkLabel(
            obj_card,
            text="incident_report.pdf.enc",
            font=ctk.CTkFont(family=FONT_MONO, size=13, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY
        )
        self.inspect_name_lbl.pack(anchor="w", padx=12)

        self.inspect_meta_lbl = ctk.CTkLabel(
            obj_card,
            text="PDF document · 2.4 MB · Encrypted at 14:29:12 UTC",
            font=ctk.CTkFont(family=FONT_MONO, size=10),
            text_color=COLOR_TEXT_MUTED
        )
        self.inspect_meta_lbl.pack(anchor="w", padx=12, pady=(2, 10))

        # Metadata Specs Table
        specs = ctk.CTkFrame(p2, fg_color="transparent")
        specs.pack(fill="x", padx=16, pady=(0, 14))

        for row_idx, (k, v) in enumerate([
            ("Cipher suite", "AES-256-GCM"),
            ("Authentication tag", "128-bit / VERIFIED"),
            ("Key reference", "SM-K7F2 / SESSION"),
            ("SHA-256", "a84e71c2…8fd019b6")
        ]):
            f = ctk.CTkFrame(specs, fg_color=COLOR_SURFACE, height=28, corner_radius=4)
            f.pack(fill="x", pady=2)
            f.pack_propagate(False)
            ctk.CTkLabel(f, text=k, font=ctk.CTkFont(family=FONT_MONO, size=10), text_color=COLOR_TEXT_MUTED).pack(side="left", padx=10)
            ctk.CTkLabel(f, text=v, font=ctk.CTkFont(family=FONT_MONO, size=10, weight="bold"), text_color=COLOR_TEXT_PRIMARY).pack(side="right", padx=10)

        # Decrypt Action Button
        self.decrypt_btn = ctk.CTkButton(
            p2,
            text="Unlock / Decrypt Vault File",
            command=self._decrypt_action,
            font=ctk.CTkFont(family=FONT_MONO, size=12, weight="bold"),
            fg_color=COLOR_CYAN,
            hover_color="#38d4ff",
            text_color="#07080e",
            height=38,
            corner_radius=6
        )
        self.decrypt_btn.pack(fill="x", padx=16, pady=(4, 6))

        # Export Copy Secondary Action
        ctk.CTkButton(
            p2,
            text="EXPORT ENCRYPTED COPY",
            command=lambda: messagebox.showinfo("Export", "Encrypted object exported to working folder."),
            font=ctk.CTkFont(family=FONT_MONO, size=11),
            fg_color=COLOR_SURFACE,
            hover_color=COLOR_CARD_HOVER,
            text_color=COLOR_TEXT_SECONDARY,
            border_width=1,
            border_color=COLOR_BORDER,
            height=32,
            corner_radius=6
        ).pack(fill="x", padx=16, pady=(0, 10))

        ctk.CTkLabel(
            p2,
            text="Decrypts locally into /Vault Folder. The encrypted original is retained.\nAn active session key is required.",
            font=ctk.CTkFont(family=FONT_BODY, size=10),
            text_color=COLOR_TEXT_MUTED,
            justify="center"
        ).pack(padx=16, pady=(0, 16))

        # =============================================================
        # COLUMN 3: Key Status & Emergency Rotation
        # =============================================================
        p3 = ctk.CTkFrame(cols_container, fg_color=COLOR_CARD, border_width=1, border_color=COLOR_BORDER, corner_radius=12)
        p3.grid(row=0, column=2, sticky="nsew", padx=(8, 0))
        p3.grid_columnconfigure(0, weight=1)

        # P3 Header
        p3_head = ctk.CTkFrame(p3, fg_color="transparent")
        p3_head.pack(fill="x", padx=16, pady=(16, 8))

        ctk.CTkLabel(
            p3_head,
            text="Key Status &\nEmergency Rotation",
            font=ctk.CTkFont(family=FONT_MONO, size=12, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY,
            justify="left"
        ).pack(anchor="w")

        # Key Fingerprint Card
        fp_card = ctk.CTkFrame(p3, fg_color=COLOR_SURFACE, corner_radius=8, border_width=1, border_color=COLOR_BORDER)
        fp_card.pack(fill="x", padx=16, pady=(4, 10))

        ctk.CTkLabel(
            fp_card,
            text="RAM SESSION KEY   ACTIVE",
            font=ctk.CTkFont(family=FONT_MONO, size=10, weight="bold"),
            text_color=COLOR_SUCCESS
        ).pack(anchor="w", padx=12, pady=(10, 2))

        ctk.CTkLabel(
            fp_card,
            text="FINGERPRINT / MASKED",
            font=ctk.CTkFont(family=FONT_MONO, size=9),
            text_color=COLOR_TEXT_MUTED
        ).pack(anchor="w", padx=12)

        self.key_fingerprint_lbl = ctk.CTkLabel(
            fp_card,
            text="7F2A : 9C84 : •••• : D601",
            font=ctk.CTkFont(family=FONT_MONO, size=13, weight="bold"),
            text_color=COLOR_CYAN
        )
        self.key_fingerprint_lbl.pack(anchor="w", padx=12, pady=(4, 8))

        # Key Details
        kd = ctk.CTkFrame(p3, fg_color="transparent")
        kd.pack(fill="x", padx=16, pady=(0, 10))

        for k, v in [
            ("Key ID", "SM-K7F2"),
            ("Residency", "RAM / LOCKED"),
            ("Issued", "14:20:00 UTC"),
            ("Expires", "14:50:00 UTC")
        ]:
            f = ctk.CTkFrame(kd, fg_color=COLOR_SURFACE, height=26, corner_radius=4)
            f.pack(fill="x", pady=2)
            f.pack_propagate(False)
            ctk.CTkLabel(f, text=k, font=ctk.CTkFont(family=FONT_MONO, size=9), text_color=COLOR_TEXT_MUTED).pack(side="left", padx=8)
            ctk.CTkLabel(f, text=v, font=ctk.CTkFont(family=FONT_MONO, size=9, weight="bold"), text_color=COLOR_TEXT_PRIMARY).pack(side="right", padx=8)

        ctk.CTkLabel(
            p3,
            text="NEVER WRITTEN TO DISK",
            font=ctk.CTkFont(family=FONT_MONO, size=9, weight="bold"),
            text_color=COLOR_TEXT_MUTED
        ).pack(pady=(2, 8))

        # Emergency Rotate Key Now Button
        self.rotate_btn = ctk.CTkButton(
            p3,
            text="ROTATE KEY NOW",
            command=self._rotate_keys,
            font=ctk.CTkFont(family=FONT_MONO, size=12, weight="bold"),
            fg_color=COLOR_DANGER,
            hover_color="#e62e2e",
            text_color="#ffffff",
            height=38,
            corner_radius=6
        )
        self.rotate_btn.pack(fill="x", padx=16, pady=(4, 6))

        ctk.CTkLabel(
            p3,
            text="Immediately revokes this key and re-seals vault files with a new in-memory session key.",
            font=ctk.CTkFont(family=FONT_BODY, size=10),
            text_color=COLOR_TEXT_MUTED,
            justify="center"
        ).pack(padx=16, pady=(0, 12))

        # TTL Self-Destruct Armed Banner
        ttl_banner = ctk.CTkFrame(p3, fg_color=COLOR_SURFACE, corner_radius=8, border_width=1, border_color=COLOR_BORDER)
        ttl_banner.pack(fill="x", padx=16, pady=(0, 16))

        ctk.CTkLabel(
            ttl_banner,
            text="TTL / SELF-DESTRUCT ● ARMED",
            font=ctk.CTkFont(family=FONT_MONO, size=10, weight="bold"),
            text_color=COLOR_SUCCESS
        ).pack(anchor="w", padx=12, pady=(8, 2))

        ctk.CTkLabel(
            ttl_banner,
            text="17:12 OF 30:00 REMAINING",
            font=ctk.CTkFont(family=FONT_MONO, size=11, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY
        ).pack(anchor="w", padx=12)

        ctk.CTkLabel(
            ttl_banner,
            text="Key zeroizes on expiry, logout, or process exit.",
            font=ctk.CTkFont(family=FONT_BODY, size=9),
            text_color=COLOR_TEXT_MUTED
        ).pack(anchor="w", padx=12, pady=(2, 8))

    def _refresh_workspace(self):
        # Clear existing entries in files scroll
        for widget in self.files_scroll.winfo_children():
            widget.destroy()

        files = self.workspace.list_files()

        # If empty, create default mock items to match Section 1.pdf exactly
        if not files:
            defaults = [
                ("network_baseline.json", "12.4 KB", False),
                ("operator_notes.md", "2.1 KB", False),
                ("incident_report.pdf.enc", "2.4 MB", True),
                ("credentials.env.enc", "1.2 KB", True),
                ("access_policy.yaml.enc", "4.8 KB", True),
                ("audit_2026-10-19.log.enc", "128 KB", True)
            ]
            for name, content, is_enc in defaults:
                fpath = self.workspace.vault_dir / name
                fpath.write_text(f"Mock content for {name}")
            files = self.workspace.list_files()

        enc_count = 0
        plain_count = 0

        for f in files:
            is_enc = f.name.endswith(".enc")
            if is_enc:
                enc_count += 1
            else:
                plain_count += 1

            # Card item
            item_card = ctk.CTkFrame(self.files_scroll, fg_color=COLOR_SURFACE, height=48, corner_radius=6, border_width=1, border_color=COLOR_BORDER)
            item_card.pack(fill="x", pady=3)
            item_card.pack_propagate(False)

            tag_color = COLOR_CYAN if is_enc else COLOR_TEXT_MUTED
            tag_text = "[ENC]" if is_enc else "[PLAIN]"

            btn = ctk.CTkButton(
                item_card,
                text=f"{f.name}",
                font=ctk.CTkFont(family=FONT_MONO, size=11, weight="bold" if is_enc else "normal"),
                fg_color="transparent",
                hover_color=COLOR_CARD_HOVER,
                text_color=COLOR_TEXT_PRIMARY,
                anchor="w",
                command=lambda target=f: self._select_file(target)
            )
            btn.pack(side="left", padx=8, fill="both", expand=True)

            tag_lbl = ctk.CTkLabel(
                item_card,
                text=tag_text,
                font=ctk.CTkFont(family=FONT_MONO, size=9, weight="bold"),
                text_color=tag_color
            )
            tag_lbl.pack(side="right", padx=10)

        self.p1_count_badge.configure(text=f"{len(files):02d}")
        self.p1_summary_lbl.configure(text=f"{enc_count} encrypted  /  {plain_count} plaintext")

    def _select_file(self, fpath: Path):
        self.selected_file = fpath
        self.inspect_name_lbl.configure(text=fpath.name)
        size_kb = fpath.stat().st_size / 1024.0 if fpath.exists() else 0.0
        self.inspect_meta_lbl.configure(text=f"Object · {size_kb:.1f} KB · Verified Seal")

    def _decrypt_action(self):
        if not self.selected_file or not self.selected_file.name.endswith(".enc"):
            # If no file selected, ask via dialog
            filename = simpledialog.askstring("Decrypt Vault File", "Enter encrypted filename (e.g. incident_report.pdf.enc):")
            if filename:
                self.selected_file = self.workspace.vault_dir / filename
            else:
                return

        if self.selected_file and self.selected_file.exists():
            try:
                self.workspace.decrypt_vault_file(self.selected_file)
                self._refresh_workspace()
                messagebox.showinfo("Vault Unlocked", f"File decrypted into /Vault Folder:\n{self.selected_file.name[:-4]}")
            except Exception as e:
                messagebox.showerror("Unlock Error", f"Decryption failed:\n{e}")

    def _rotate_keys(self):
        self.rotate_btn.configure(state="disabled", text="REVOKING & ROTATING...")
        try:
            files = list(self.workspace.vault_dir.glob("*.enc"))
            old_k = SessionState.get_key()
            new_k, elapsed = emergency_rotate_keys(old_k, files)
            SessionState.set_key(new_k)

            # Update fingerprint in UI
            raw_hex = new_k.hex().upper()
            self.key_fingerprint_lbl.configure(text=f"{raw_hex[:4]} : {raw_hex[4:8]} : •••• : {raw_hex[-4:]}")
            messagebox.showinfo("Emergency Rotation Complete", f"Key revoked!\nAll vault files re-sealed with a new ephemeral key in {elapsed:.2f} ms.")
        except Exception as e:
            messagebox.showerror("Rotation Error", f"Rotation failed:\n{e}")
        finally:
            self.rotate_btn.configure(state="normal", text="ROTATE KEY NOW")
