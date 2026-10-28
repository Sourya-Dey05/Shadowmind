# =============================================================================
# FILE: ui/main_window.py
# PURPOSE: Main CustomTkinter desktop window for ShadowMind. Hosts the login
#          screen and, after successful authentication, a tabbed interface with:
#          Dashboard, File Vault, Honeypot, and Settings tabs. Each tab is a
#          placeholder in Phase 0 — real content is plugged in during Phases
#          1-5. Also manages the active Session object and TTL countdown display.
# =============================================================================

import time
import logging
import threading
import customtkinter as ctk
from tkinter import messagebox
from pathlib import Path
import sys

# Add project root to path so src imports work
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.auth.auth import login, logout, require_role, bootstrap_admin, Role, Session
from src.auth.otp import OTPManager
from ui.tabs.dashboard_tab import DashboardTab
from ui.tabs.vault_tab import VaultTab
from ui.tabs.honeypot_tab import HoneypotTab
from ui.tabs.settings_tab import SettingsTab
from ui.animations import CyberAnimator

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# --- Appearance ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

from ui.theme import (
    COLOR_BG as C_BG,
    COLOR_CARD as C_PANEL,
    COLOR_CYAN as C_ACCENT,
    COLOR_DANGER as C_DANGER,
    COLOR_WARNING as C_WARNING,
    COLOR_SUCCESS as C_SUCCESS,
    COLOR_TEXT_PRIMARY as C_TEXT,
    COLOR_TEXT_SECONDARY as C_SUBTEXT,
    COLOR_BORDER as C_BORDER,
    COLOR_SURFACE as C_SURFACE,
    FONT_BRAND, FONT_MONO, FONT_BODY, FONT_TITLE
)

# =============================================================================
# Login Frame
# =============================================================================

class LoginFrame(ctk.CTkFrame):
    """
    Shown before authentication. Collects username + password, enforces
    input validation via auth.py, and calls on_login_success on success.
    """

    def __init__(self, parent, on_login_success):
        super().__init__(parent, fg_color=C_BG)
        self.on_login_success = on_login_success
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)

        # Top status banner matching Figma Screen 1
        top_banner = ctk.CTkFrame(self, fg_color=C_SURFACE, height=34, corner_radius=0)
        top_banner.grid(row=0, column=0, sticky="ew")
        top_banner.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            top_banner,
            text="SHADOWMIND / v2.4.0  SECURE ACCESS TERMINAL / SM-01",
            font=ctk.CTkFont(family=FONT_MONO, size=10),
            text_color=C_SUBTEXT
        ).grid(row=0, column=0, padx=16, pady=6, sticky="w")

        ctk.CTkLabel(
            top_banner,
            text="● ENCLAVE READY   VERIFIED · SHA-256",
            font=ctk.CTkFont(family=FONT_MONO, size=10, weight="bold"),
            text_color=C_SUCCESS
        ).grid(row=0, column=2, padx=16, pady=6, sticky="e")

        # Subtitle trust tag
        ctk.CTkLabel(
            self,
            text="TRUST BOUNDARY / LOCAL KERNEL INTEGRITY",
            font=ctk.CTkFont(family=FONT_MONO, size=9, weight="bold"),
            text_color=C_SUBTEXT
        ).grid(row=1, column=0, pady=(20, 0))

        # Logo / title
        ctk.CTkLabel(
            self, text="SHADOWMIND",
            font=ctk.CTkFont(family=FONT_TITLE, size=40, weight="bold"),
            text_color=C_TEXT
        ).grid(row=2, column=0, pady=(6, 2))

        ctk.CTkLabel(
            self, text="Self - Destructing AI Defense System",
            font=ctk.CTkFont(family=FONT_BODY, size=13),
            text_color=C_SUBTEXT
        ).grid(row=3, column=0, pady=(0, 20))

        # Login card matching Figma
        card = ctk.CTkFrame(self, fg_color=C_PANEL, corner_radius=12, width=380, border_width=1, border_color=C_BORDER)
        card.grid(row=4, column=0, padx=40, pady=0, sticky="n")
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card, text="OPERATOR AUTHENTICATION",
            font=ctk.CTkFont(family=FONT_MONO, size=11, weight="bold"),
            text_color=C_TEXT
        ).grid(row=0, column=0, pady=(22, 14))

        self.username_var = ctk.StringVar(value="souryanew@shadowmind.com")
        self.password_var = ctk.StringVar(value="")

        ctk.CTkLabel(
            card, text="OPERATOR EMAIL", text_color=C_SUBTEXT,
            font=ctk.CTkFont(family=FONT_MONO, size=9, weight="bold")
        ).grid(row=1, column=0, sticky="w", padx=28)
        self.user_entry = ctk.CTkEntry(
            card, textvariable=self.username_var, placeholder_text="Enter admin email",
            width=324, height=38, corner_radius=6,
            fg_color=C_SURFACE, border_color=C_BORDER, text_color=C_TEXT,
            font=ctk.CTkFont(family=FONT_MONO, size=12)
        )
        self.user_entry.grid(row=2, column=0, padx=28, pady=(2, 12))

        ctk.CTkLabel(
            card, text="PASSWORD", text_color=C_SUBTEXT,
            font=ctk.CTkFont(family=FONT_MONO, size=9, weight="bold")
        ).grid(row=3, column=0, sticky="w", padx=28)
        self.pw_entry = ctk.CTkEntry(
            card, textvariable=self.password_var, placeholder_text="Enter password",
            show="•", width=324, height=38, corner_radius=6,
            fg_color=C_SURFACE, border_color=C_BORDER, text_color=C_TEXT,
            font=ctk.CTkFont(family=FONT_MONO, size=14)
        )
        self.pw_entry.grid(row=4, column=0, padx=28, pady=(2, 6))

        self.error_label = ctk.CTkLabel(
            card, text="", text_color=C_DANGER,
            font=ctk.CTkFont(family=FONT_MONO, size=10)
        )
        self.error_label.grid(row=5, column=0, pady=(0, 4))

        self.login_btn = ctk.CTkButton(
            card, text="INITIALIZE SECURE SESSION", command=self._attempt_login,
            width=324, height=42, corner_radius=6,
            fg_color=C_ACCENT, hover_color="#38d4ff", text_color="#07080e",
            font=ctk.CTkFont(family=FONT_MONO, size=11, weight="bold")
        )
        self.login_btn.grid(row=6, column=0, padx=28, pady=(4, 12))
        CyberAnimator.apply_button_hover(self.login_btn, C_ACCENT, "#38d4ff")

        ctk.CTkLabel(
            card,
            text="RAM-ONLY KEYS · AUTO-PURGE ON EXIT",
            font=ctk.CTkFont(family=FONT_MONO, size=9),
            text_color=C_SUBTEXT
        ).grid(row=7, column=0, pady=(0, 16))

        # Bottom guidance
        ctk.CTkLabel(
            self,
            text="Restricted to authorized personnel. All access attempts are logged and\ncontinuously monitored.",
            font=ctk.CTkFont(family=FONT_BODY, size=11),
            text_color=C_SUBTEXT, justify="center"
        ).grid(row=5, column=0, pady=(16, 0))

        # Bottom bar
        bot_banner = ctk.CTkFrame(self, fg_color=C_SURFACE, height=32, corner_radius=0)
        bot_banner.grid(row=6, column=0, sticky="ew", pady=(24, 0))
        bot_banner.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            bot_banner,
            text="AES-256 ENCRYPTION   ZERO-TRUST RUNTIME   EPHEMERAL BY DESIGN",
            font=ctk.CTkFont(family=FONT_MONO, size=9),
            text_color=C_SUBTEXT
        ).grid(row=0, column=0, padx=16, pady=6, sticky="w")

        ctk.CTkLabel(
            bot_banner,
            text="SHADOWMIND OS 2.4.0 / BUILD 24.10.19",
            font=ctk.CTkFont(family=FONT_MONO, size=9),
            text_color=C_SUBTEXT
        ).grid(row=0, column=2, padx=16, pady=6, sticky="e")

        # Bind Enter key
        self.pw_entry.bind("<Return>", lambda e: self._attempt_login())

    def _attempt_login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get()

        # Basic client-side sanity check (real validation is in auth.py)
        if not username or not password:
            self._show_error("Username and password are required")
            return

        # Disable button to prevent double-click
        self.login_btn.configure(state="disabled", text="Authenticating...")
        self.after(100, lambda: self._do_login(username, password))

    def _do_login(self, username: str, password: str):
        session = login(username, password)
        self.login_btn.configure(state="normal", text="INITIALIZE SECURE SESSION")

        if session is None:
            self._show_error("Invalid credentials or account locked")
            self.password_var.set("")
        else:
            self.error_label.configure(text="")
            self.on_login_success(session)

    def _show_error(self, msg: str):
        self.error_label.configure(text=msg)


# =============================================================================
# Main Application Window
# =============================================================================

class ShadowMindApp(ctk.CTk):
    """
    Root window. Manages the login → main tab transition and the active session.
    Runs a background TTL countdown thread that auto-logs-out on session expiry.
    """

    def __init__(self):
        super().__init__()
        self.title("ShadowMind — AI Defense System")
        self.geometry("1200x750")
        self.minsize(900, 600)
        self.configure(fg_color=C_BG)

        self.session: Session = None
        self._ttl_thread = None
        self._running = True

        # Ensure at least one admin exists on first run
        bootstrap_admin()

        self._show_login()

    # -------------------------------------------------------------------------
    # Navigation
    # -------------------------------------------------------------------------

    def _show_login(self):
        """Destroy main UI (if any) and show the login screen."""
        for w in self.winfo_children():
            w.destroy()
        LoginFrame(self, on_login_success=self._on_login_success).pack(fill="both", expand=True)

    def _on_login_success(self, session: Session):
        self.session = session
        
        # Smooth transition effect: flash loading state
        for w in self.winfo_children():
            w.destroy()
        
        loading_frame = ctk.CTkFrame(self, fg_color=C_BG)
        loading_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(
            loading_frame, text="● ESTABLISHING SECURE ZERO-TRUST TUNNEL...",
            font=ctk.CTkFont(family=FONT_MONO, size=15, weight="bold"),
            text_color=C_ACCENT
        ).place(relx=0.5, rely=0.48, anchor="center")

        ctk.CTkLabel(
            loading_frame, text="ALLOCATING RAM ENCLAVE · VALIDATING LOCAL INTEGRITY",
            font=ctk.CTkFont(family=FONT_MONO, size=10),
            text_color=C_SUBTEXT
        ).place(relx=0.5, rely=0.53, anchor="center")
        
        self.update()
        import time
        time.sleep(0.4)
        
        self._build_main_ui()
        self._start_ttl_watcher()

    def _build_main_ui(self):
        """Build the tabbed main interface after successful login."""
        for w in self.winfo_children():
            w.destroy()

        # Top bar with Figma header aesthetics
        topbar = ctk.CTkFrame(self, fg_color=C_SURFACE, height=50, corner_radius=0, border_width=1, border_color=C_BORDER)
        topbar.pack(fill="x", side="top")
        topbar.pack_propagate(False)

        brand_frame = ctk.CTkFrame(topbar, fg_color="transparent")
        brand_frame.pack(side="left", padx=16)

        ctk.CTkLabel(
            brand_frame, text="SHADOWMIND",
            font=ctk.CTkFont(family=FONT_TITLE, size=16, weight="bold"),
            text_color=C_TEXT
        ).pack(side="left")

        ctk.CTkLabel(
            brand_frame, text=" / v2.4.0",
            font=ctk.CTkFont(family=FONT_MONO, size=11),
            text_color=C_SUBTEXT
        ).pack(side="left", padx=(2, 0))

        # Right side info container
        right_info = ctk.CTkFrame(topbar, fg_color="transparent")
        right_info.pack(side="right", padx=16)

        # Operator pill
        pill = ctk.CTkFrame(right_info, fg_color=C_PANEL, corner_radius=6, border_width=1, border_color=C_BORDER)
        pill.pack(side="left", padx=(0, 12))

        ctk.CTkLabel(
            pill, text="AD",
            font=ctk.CTkFont(family=FONT_MONO, size=10, weight="bold"),
            fg_color=C_ACCENT, text_color="#07080e",
            corner_radius=4, width=22, height=22
        ).pack(side="left", padx=6, pady=4)

        ctk.CTkLabel(
            pill,
            text=f"{self.session.username} [{self.session.role.value.upper()}]",
            font=ctk.CTkFont(family=FONT_MONO, size=11, weight="bold"),
            text_color=C_TEXT
        ).pack(side="left", padx=(2, 8))

        self.ttl_label = ctk.CTkLabel(
            pill, text="", font=ctk.CTkFont(family=FONT_MONO, size=11), text_color=C_SUBTEXT
        )
        self.ttl_label.pack(side="left", padx=(0, 10))

        ctk.CTkLabel(
            right_info,
            text="LOCAL NODE / SM-01",
            font=ctk.CTkFont(family=FONT_MONO, size=10),
            text_color=C_SUBTEXT
        ).pack(side="left", padx=(0, 12))

        logout_btn = ctk.CTkButton(
            right_info, text="LOGOUT", command=self._logout,
            width=72, height=28, fg_color="#2b1418", hover_color=C_DANGER,
            text_color=C_DANGER, font=ctk.CTkFont(family=FONT_MONO, size=10, weight="bold"),
            corner_radius=4
        )
        logout_btn.pack(side="left")
        CyberAnimator.apply_button_hover(logout_btn, "#2b1418", C_DANGER, C_DANGER, "#ffffff")

        # Tab view with Figma border & surface styling
        self.tabs = ctk.CTkTabview(self, fg_color=C_BG,
                                   segmented_button_fg_color=C_SURFACE,
                                   segmented_button_selected_color=C_PANEL,
                                   segmented_button_selected_hover_color=C_PANEL,
                                   segmented_button_unselected_color=C_SURFACE,
                                   segmented_button_unselected_hover_color=C_SURFACE,
                                   text_color=C_TEXT)
        self.tabs.pack(fill="both", expand=True, padx=0, pady=0)

        self.tabs.add("Dashboard")
        self.tabs.add("File Vault")
        self.tabs.add("Honeypot")
        if require_role(self.session, Role.ADMIN):
            self.tabs.add("Settings")

        # Inject tab content
        DashboardTab(self.tabs.tab("Dashboard"), self.session).pack(fill="both", expand=True)
        VaultTab(self.tabs.tab("File Vault"), self.session).pack(fill="both", expand=True)
        HoneypotTab(self.tabs.tab("Honeypot"), self.session).pack(fill="both", expand=True)
        if require_role(self.session, Role.ADMIN):
            SettingsTab(self.tabs.tab("Settings"), self.session).pack(fill="both", expand=True)

    # -------------------------------------------------------------------------
    # TTL watcher
    # -------------------------------------------------------------------------

    def _start_ttl_watcher(self):
        """Background thread that checks session TTL every second."""
        self._ttl_thread = threading.Thread(target=self._ttl_loop, daemon=True)
        self._ttl_thread.start()

    def _ttl_loop(self):
        while self._running:
            if self.session and not self.session.is_valid():
                logger.info("Session TTL expired — auto logout triggered")
                self.after(0, self._logout_expired)
                return
            if self.session:
                remaining = int(self.session.ttl_seconds - (time.time() - self.session.created_at))
                h, rem = divmod(max(remaining, 0), 3600)
                m, s   = divmod(rem, 60)
                ttl_str = f"Session expires in: {h:02d}:{m:02d}:{s:02d}"
                self.after(0, lambda t=ttl_str: self._update_ttl_label(t))
            time.sleep(1)

    def _update_ttl_label(self, text: str):
        try:
            self.ttl_label.configure(text=text)
        except Exception:
            pass

    def _logout_expired(self):
        messagebox.showwarning(
            "Session Expired",
            "Your session has expired.\nAll session keys have been wiped from memory.\nPlease log in again."
        )
        self._logout()

    # -------------------------------------------------------------------------
    # Logout
    # -------------------------------------------------------------------------

    def _logout(self):
        """Log out, wipe session, return to login screen."""
        self._running = False
        if self.session:
            logout(self.session)
            # Phase 3: vault TTL destruct will be triggered here
            self.session = None
        self._running = True
        self._show_login()

    def on_closing(self):
        """Called when the X button is pressed."""
        self._running = False
        if self.session:
            logout(self.session)
        self.destroy()
