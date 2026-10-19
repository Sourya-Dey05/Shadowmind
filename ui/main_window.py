# =============================================================================
# FILE: ui/main_window.py
# PURPOSE: Recreated strictly from Figma Mockup (Section 1.pdf).
#          - Screen 1: Operator Authentication / Secure Access Terminal
#          - Top Header: Node & Session Info, Operator badge, Logout
#          - Navigation: Command Center | File Vault & Workspace
#          - Bottom Bar: Enclave Status, Local Clock, Build OS 2.4.0 Info
# =============================================================================

import sys
import time
import threading
import datetime
from pathlib import Path
import customtkinter as ctk
from tkinter import messagebox

# Path setup
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.auth.auth import login, logout, bootstrap_admin, Session
from ui.theme import (
    COLOR_BG, COLOR_SURFACE, COLOR_CARD, COLOR_CARD_HOVER,
    COLOR_BORDER, COLOR_CYAN, COLOR_SUCCESS, COLOR_WARNING,
    COLOR_DANGER, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY,
    COLOR_TEXT_MUTED, FONT_BRAND, FONT_BODY, FONT_MONO
)
from ui.tabs.dashboard_tab import DashboardTab
from ui.tabs.vault_tab import VaultTab

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# =============================================================================
# SCREEN 1: OPERATOR AUTHENTICATION (Figma Screen 1)
# =============================================================================

class LoginFrame(ctk.CTkFrame):
    """
    Exact recreation of Screen 1:
    - Top bar: SHADOWMIND / v2.4.0 SECURE ACCESS TERMINAL / SM-01 ENCLAVE READY
    - Subtitle badge: TRUST BOUNDARY / LOCAL KERNEL INTEGRITY VERIFIED · SHA-256
    - Center Hero: SHADOWMIND Self-Destructing AI Defense System
    - Card: OPERATOR AUTHENTICATION with USERNAME, PASSWORD fields
    - Action: INITIALIZE SECURE SESSION (glowing cyan)
    - Footnotes: RAM-ONLY KEYS · AUTO-PURGE ON EXIT
    - Bottom bar: AES-256 ENCRYPTION ZERO-TRUST RUNTIME EPHEMERAL BY DESIGN
    """

    def __init__(self, parent, on_login_success):
        super().__init__(parent, fg_color=COLOR_BG)
        self.on_login_success = on_login_success
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # -------------------------------------------------------------
        # 1. Top Terminal Status Bar
        # -------------------------------------------------------------
        top_bar = ctk.CTkFrame(self, fg_color=COLOR_SURFACE, height=36, corner_radius=0)
        top_bar.grid(row=0, column=0, sticky="ew")
        top_bar.grid_columnconfigure(1, weight=1)

        left_tag = ctk.CTkLabel(
            top_bar,
            text="SHADOWMIND / v2.4.0  SECURE ACCESS TERMINAL / SM-01",
            font=ctk.CTkFont(family=FONT_MONO, size=11),
            text_color=COLOR_TEXT_MUTED
        )
        left_tag.grid(row=0, column=0, padx=16, pady=8, sticky="w")

        right_enclave = ctk.CTkLabel(
            top_bar,
            text="● ENCLAVE READY   VERIFIED · SHA-256",
            font=ctk.CTkFont(family=FONT_MONO, size=11, weight="bold"),
            text_color=COLOR_SUCCESS
        )
        right_enclave.grid(row=0, column=2, padx=16, pady=8, sticky="e")

        # -------------------------------------------------------------
        # 2. Sub-Header Trust Boundary
        # -------------------------------------------------------------
        trust_frame = ctk.CTkFrame(self, fg_color="transparent")
        trust_frame.grid(row=1, column=0, pady=(24, 0))

        ctk.CTkLabel(
            trust_frame,
            text="TRUST BOUNDARY / LOCAL KERNEL INTEGRITY",
            font=ctk.CTkFont(family=FONT_MONO, size=10, weight="bold"),
            text_color=COLOR_TEXT_MUTED
        ).pack()

        # -------------------------------------------------------------
        # 3. Main Center Stack
        # -------------------------------------------------------------
        center_container = ctk.CTkFrame(self, fg_color="transparent")
        center_container.grid(row=2, column=0, padx=20, pady=10)

        # Brand Title
        ctk.CTkLabel(
            center_container,
            text="SHADOWMIND",
            font=ctk.CTkFont(family=FONT_BRAND, size=38, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY
        ).pack(pady=(0, 2))

        ctk.CTkLabel(
            center_container,
            text="Self - Destructing AI Defense System",
            font=ctk.CTkFont(family=FONT_BODY, size=13),
            text_color=COLOR_TEXT_SECONDARY
        ).pack(pady=(0, 24))

        # Authentication Card
        card = ctk.CTkFrame(
            center_container,
            fg_color=COLOR_CARD,
            border_width=1,
            border_color=COLOR_BORDER,
            corner_radius=12,
            width=420
        )
        card.pack(padx=20, pady=0)
        card.pack_propagate(False)
        card.configure(height=380)

        # Card Header
        ctk.CTkLabel(
            card,
            text="OPERATOR AUTHENTICATION",
            font=ctk.CTkFont(family=FONT_MONO, size=12, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY
        ).pack(pady=(22, 14))

        # Username Input
        u_frame = ctk.CTkFrame(card, fg_color="transparent")
        u_frame.pack(fill="x", padx=28, pady=(0, 10))
        ctk.CTkLabel(
            u_frame,
            text="USERNAME",
            font=ctk.CTkFont(family=FONT_MONO, size=10, weight="bold"),
            text_color=COLOR_TEXT_MUTED
        ).pack(anchor="w", pady=(0, 4))
        self.username_var = ctk.StringVar(value="admin")
        self.user_entry = ctk.CTkEntry(
            u_frame,
            textvariable=self.username_var,
            font=ctk.CTkFont(family=FONT_MONO, size=13),
            fg_color=COLOR_SURFACE,
            border_color=COLOR_BORDER,
            border_width=1,
            text_color=COLOR_TEXT_PRIMARY,
            height=38
        )
        self.user_entry.pack(fill="x")

        # Password Input
        p_frame = ctk.CTkFrame(card, fg_color="transparent")
        p_frame.pack(fill="x", padx=28, pady=(0, 6))
        ctk.CTkLabel(
            p_frame,
            text="PASSWORD",
            font=ctk.CTkFont(family=FONT_MONO, size=10, weight="bold"),
            text_color=COLOR_TEXT_MUTED
        ).pack(anchor="w", pady=(0, 4))
        self.password_var = ctk.StringVar(value="")
        self.pw_entry = ctk.CTkEntry(
            p_frame,
            textvariable=self.password_var,
            show="•",
            font=ctk.CTkFont(family=FONT_MONO, size=14),
            fg_color=COLOR_SURFACE,
            border_color=COLOR_BORDER,
            border_width=1,
            text_color=COLOR_TEXT_PRIMARY,
            height=38
        )
        self.pw_entry.pack(fill="x")

        # Error label
        self.error_label = ctk.CTkLabel(
            card,
            text="",
            font=ctk.CTkFont(family=FONT_MONO, size=11),
            text_color=COLOR_DANGER
        )
        self.error_label.pack(pady=(2, 6))

        # Glowing CTA Button
        self.login_btn = ctk.CTkButton(
            card,
            text="INITIALIZE SECURE SESSION",
            command=self._attempt_login,
            font=ctk.CTkFont(family=FONT_MONO, size=12, weight="bold"),
            fg_color=COLOR_CYAN,
            hover_color="#38d4ff",
            text_color="#07080e",
            height=42,
            corner_radius=6
        )
        self.login_btn.pack(fill="x", padx=28, pady=(4, 12))
        self.pw_entry.bind("<Return>", lambda e: self._attempt_login())

        # Subtext badge
        ctk.CTkLabel(
            card,
            text="RAM-ONLY KEYS · AUTO-PURGE ON EXIT",
            font=ctk.CTkFont(family=FONT_MONO, size=10),
            text_color=COLOR_TEXT_MUTED
        ).pack(pady=(0, 8))

        # Bottom warning on card
        ctk.CTkLabel(
            center_container,
            text="Restricted to authorized personnel. All access attempts are logged and\ncontinuously monitored.",
            font=ctk.CTkFont(family=FONT_BODY, size=11),
            text_color=COLOR_TEXT_MUTED,
            justify="center"
        ).pack(pady=(16, 0))

        # -------------------------------------------------------------
        # 4. Bottom Footer Security Bar
        # -------------------------------------------------------------
        bot_bar = ctk.CTkFrame(self, fg_color=COLOR_SURFACE, height=36, corner_radius=0)
        bot_bar.grid(row=3, column=0, sticky="ew")
        bot_bar.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            bot_bar,
            text="AES-256 ENCRYPTION   ZERO-TRUST RUNTIME   EPHEMERAL BY DESIGN",
            font=ctk.CTkFont(family=FONT_MONO, size=10),
            text_color=COLOR_TEXT_MUTED
        ).grid(row=0, column=0, padx=16, pady=8, sticky="w")

        now_utc = datetime.datetime.utcnow().strftime("%d %b %Y · %H:%M:%S UTC")
        ctk.CTkLabel(
            bot_bar,
            text=f"SHADOWMIND OS 2.4.0 / BUILD 24.10.19   {now_utc}",
            font=ctk.CTkFont(family=FONT_MONO, size=10),
            text_color=COLOR_TEXT_MUTED
        ).grid(row=0, column=2, padx=16, pady=8, sticky="e")

    def _attempt_login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get()

        if not username or not password:
            self.error_label.configure(text="Credentials required")
            return

        self.login_btn.configure(state="disabled", text="VERIFYING ENCLAVE...")
        self.after(80, lambda: self._do_login(username, password))

    def _do_login(self, username: str, password: str):
        session = login(username, password)
        self.login_btn.configure(state="normal", text="INITIALIZE SECURE SESSION")

        if session is None:
            self.error_label.configure(text="Access denied: invalid credentials")
            self.password_var.set("")
        else:
            self.error_label.configure(text="")
            self.on_login_success(session)


# =============================================================================
# MAIN APP SHELL (Screens 2 & 3: Command Center, File Vault & Workspace)
# =============================================================================

class ShadowMindApp(ctk.CTk):
    """
    Main Application Window.
    Implements exact layout from Figma Section 1.pdf:
    - Persistent Top Header: Brand, Navigation Buttons, Operator Pill, Logout
    - Central Container: Switches between DashboardTab and VaultTab
    - Persistent Footer: Security Protocol Bar, Build Version, Live Clock
    """

    def __init__(self):
        super().__init__()
        self.title("SHADOWMIND / v2.4.0 — Autonomous Zero-Trust Defense")
        self.geometry("1440x900")
        self.minsize(1100, 720)
        self.configure(fg_color=COLOR_BG)

        self.session: Session = None
        self._running = True
        self.current_screen = "dashboard"

        bootstrap_admin()
        self._show_login()

    def _show_login(self):
        for w in self.winfo_children():
            w.destroy()
        LoginFrame(self, on_login_success=self._on_login_success).pack(fill="both", expand=True)

    def _on_login_success(self, session: Session):
        self.session = session
        self._build_main_ui()
        self._start_ttl_timer()

    def _build_main_ui(self):
        for w in self.winfo_children():
            w.destroy()

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # -------------------------------------------------------------
        # TOP HEADER NAVIGATION (Figma Header)
        # -------------------------------------------------------------
        header = ctk.CTkFrame(self, fg_color=COLOR_SURFACE, height=54, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(3, weight=1)

        # Brand / Version
        brand_box = ctk.CTkFrame(header, fg_color="transparent")
        brand_box.grid(row=0, column=0, padx=(16, 20), pady=8, sticky="w")
        ctk.CTkLabel(
            brand_box,
            text="SHADOWMIND",
            font=ctk.CTkFont(family=FONT_BRAND, size=15, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY
        ).pack(side="left")
        ctk.CTkLabel(
            brand_box,
            text=" / v2.4.0",
            font=ctk.CTkFont(family=FONT_MONO, size=11),
            text_color=COLOR_TEXT_MUTED
        ).pack(side="left", padx=(4, 0))

        # Navigation Links
        nav_box = ctk.CTkFrame(header, fg_color="transparent")
        nav_box.grid(row=0, column=1, sticky="w", pady=8)

        self.nav_cmd_btn = ctk.CTkButton(
            nav_box,
            text="Command center",
            font=ctk.CTkFont(family=FONT_BODY, size=12, weight="bold"),
            fg_color=COLOR_CARD,
            hover_color=COLOR_CARD_HOVER,
            text_color=COLOR_CYAN,
            height=32,
            corner_radius=6,
            command=lambda: self._switch_tab("dashboard")
        )
        self.nav_cmd_btn.pack(side="left", padx=(0, 8))

        self.nav_vault_btn = ctk.CTkButton(
            nav_box,
            text="File vault & workspace",
            font=ctk.CTkFont(family=FONT_BODY, size=12),
            fg_color="transparent",
            hover_color=COLOR_CARD_HOVER,
            text_color=COLOR_TEXT_SECONDARY,
            height=32,
            corner_radius=6,
            command=lambda: self._switch_tab("vault")
        )
        self.nav_vault_btn.pack(side="left")

        # Right Status: Operator Info Pill & Logout
        right_box = ctk.CTkFrame(header, fg_color="transparent")
        right_box.grid(row=0, column=4, padx=16, pady=8, sticky="e")

        # User Pill
        user_pill = ctk.CTkFrame(right_box, fg_color=COLOR_CARD, corner_radius=6)
        user_pill.pack(side="left", padx=(0, 10))

        # Avatar badge
        ctk.CTkLabel(
            user_pill,
            text="AD",
            font=ctk.CTkFont(family=FONT_MONO, size=10, weight="bold"),
            fg_color=COLOR_CYAN,
            text_color="#07080e",
            corner_radius=4,
            width=22,
            height=22
        ).pack(side="left", padx=6, pady=4)

        self.user_lbl = ctk.CTkLabel(
            user_pill,
            text=f"{self.session.username} [{self.session.role.value.upper()}]",
            font=ctk.CTkFont(family=FONT_MONO, size=11, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY
        )
        self.user_lbl.pack(side="left", padx=(2, 8))

        self.session_timer_lbl = ctk.CTkLabel(
            user_pill,
            text="SESSION 00:00:00",
            font=ctk.CTkFont(family=FONT_MONO, size=11),
            text_color=COLOR_TEXT_MUTED
        )
        self.session_timer_lbl.pack(side="left", padx=(0, 8))

        # Node Badge
        ctk.CTkLabel(
            right_box,
            text="LOCAL NODE / SM-01",
            font=ctk.CTkFont(family=FONT_MONO, size=10),
            text_color=COLOR_TEXT_MUTED
        ).pack(side="left", padx=(0, 10))

        # Logout button
        ctk.CTkButton(
            right_box,
            text="LOGOUT",
            font=ctk.CTkFont(family=FONT_MONO, size=11, weight="bold"),
            fg_color="#2b1418",
            hover_color=COLOR_DANGER,
            text_color=COLOR_DANGER,
            width=70,
            height=28,
            corner_radius=4,
            command=self._logout
        ).pack(side="left")

        # -------------------------------------------------------------
        # MAIN CONTENT VIEW (Row 1)
        # -------------------------------------------------------------
        self.content_container = ctk.CTkFrame(self, fg_color=COLOR_BG)
        self.content_container.grid(row=1, column=0, sticky="nsew")
        self.content_container.grid_rowconfigure(0, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)

        self.dashboard_tab = DashboardTab(self.content_container, self.session)
        self.vault_tab = VaultTab(self.content_container, self.session)

        # Show initial tab
        self._switch_tab("dashboard")

        # -------------------------------------------------------------
        # BOTTOM STATUS FOOTER (Figma Footer)
        # -------------------------------------------------------------
        self.footer = ctk.CTkFrame(self, fg_color=COLOR_SURFACE, height=32, corner_radius=0)
        self.footer.grid(row=2, column=0, sticky="ew")
        self.footer.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            self.footer,
            text="ENCRYPTED CHANNEL · LOCAL-ONLY PROCESSING",
            font=ctk.CTkFont(family=FONT_MONO, size=10),
            text_color=COLOR_TEXT_MUTED
        ).grid(row=0, column=0, padx=16, pady=6, sticky="w")

        self.footer_clock = ctk.CTkLabel(
            self.footer,
            text="",
            font=ctk.CTkFont(family=FONT_MONO, size=10),
            text_color=COLOR_TEXT_MUTED
        )
        self.footer_clock.grid(row=0, column=2, padx=16, pady=6, sticky="e")

    def _switch_tab(self, tab_name: str):
        self.current_screen = tab_name
        if tab_name == "dashboard":
            self.vault_tab.grid_forget()
            self.dashboard_tab.grid(row=0, column=0, sticky="nsew")
            self.nav_cmd_btn.configure(fg_color=COLOR_CARD, text_color=COLOR_CYAN)
            self.nav_vault_btn.configure(fg_color="transparent", text_color=COLOR_TEXT_SECONDARY)
        else:
            self.dashboard_tab.grid_forget()
            self.vault_tab.grid(row=0, column=0, sticky="nsew")
            self.nav_cmd_btn.configure(fg_color="transparent", text_color=COLOR_TEXT_SECONDARY)
            self.nav_vault_btn.configure(fg_color=COLOR_CARD, text_color=COLOR_CYAN)

    def _start_ttl_timer(self):
        self._running = True
        threading.Thread(target=self._clock_loop, daemon=True).start()

    def _clock_loop(self):
        while self._running:
            if self.session and not self.session.is_valid():
                self.after(0, self._session_expired)
                return

            now = datetime.datetime.utcnow().strftime("%d %b %Y · %H:%M:%S UTC")
            if self.session:
                elapsed = int(time.time() - self.session.created_at)
                h, rem = divmod(elapsed, 3600)
                m, s = divmod(rem, 60)
                session_str = f"SESSION {h:02d}:{m:02d}:{s:02d}"
            else:
                session_str = "SESSION 00:00:00"

            self.after(0, lambda s=session_str, t=now: self._update_clock_labels(s, t))
            time.sleep(1)

    def _update_clock_labels(self, session_str: str, now_str: str):
        try:
            self.session_timer_lbl.configure(text=session_str)
            self.footer_clock.configure(text=f"SHADOWMIND OS 2.4.0 / BUILD 24.10.19   {now_str}")
        except Exception:
            pass

    def _session_expired(self):
        messagebox.showwarning(
            "Session Expired",
            "Session TTL expired.\nDecryption keys zero-wiped from RAM by TTL self-destruct engine."
        )
        self._logout()

    def _logout(self):
        self._running = False
        if self.session:
            logout(self.session)
            self.session = None
        self._show_login()

    def on_closing(self):
        self._running = False
        if self.session:
            logout(self.session)
        self.destroy()


if __name__ == "__main__":
    app = ShadowMindApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
