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

# Color palette
C_BG       = "#0d0f14"   # near-black background
C_PANEL    = "#13161e"   # panel background
C_ACCENT   = "#00c8ff"   # ShadowMind cyan
C_DANGER   = "#ff4444"
C_WARNING  = "#ffaa00"
C_SUCCESS  = "#00cc66"
C_TEXT     = "#e0e0e0"
C_SUBTEXT  = "#888888"

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

        # Logo / title
        ctk.CTkLabel(
            self, text="SHADOWMIND",
            font=ctk.CTkFont(family="Courier New", size=36, weight="bold"),
            text_color=C_ACCENT
        ).grid(row=0, column=0, pady=(60, 4))

        ctk.CTkLabel(
            self, text="Self-Destructing AI Defense System",
            font=ctk.CTkFont(size=13),
            text_color=C_SUBTEXT
        ).grid(row=1, column=0, pady=(0, 40))

        # Login card
        card = ctk.CTkFrame(self, fg_color=C_PANEL, corner_radius=12, width=360)
        card.grid(row=2, column=0, padx=40, pady=10, sticky="n")
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(card, text="Sign In", font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=C_TEXT).grid(row=0, column=0, pady=(24, 16))

        self.username_var = ctk.StringVar()
        self.password_var = ctk.StringVar()

        ctk.CTkLabel(card, text="Username", text_color=C_SUBTEXT,
                     font=ctk.CTkFont(size=12)).grid(row=1, column=0, sticky="w", padx=24)
        ctk.CTkEntry(
            card, textvariable=self.username_var, placeholder_text="Enter username",
            width=312, height=38, corner_radius=8
        ).grid(row=2, column=0, padx=24, pady=(2, 12))

        ctk.CTkLabel(card, text="Password", text_color=C_SUBTEXT,
                     font=ctk.CTkFont(size=12)).grid(row=3, column=0, sticky="w", padx=24)
        self.pw_entry = ctk.CTkEntry(
            card, textvariable=self.password_var, placeholder_text="Enter password",
            show="*", width=312, height=38, corner_radius=8
        )
        self.pw_entry.grid(row=4, column=0, padx=24, pady=(2, 8))

        self.error_label = ctk.CTkLabel(card, text="", text_color=C_DANGER,
                                        font=ctk.CTkFont(size=11))
        self.error_label.grid(row=5, column=0, pady=(0, 4))

        self.login_btn = ctk.CTkButton(
            card, text="INITIALIZE SECURE SESSION", command=self._attempt_login,
            width=312, height=44, corner_radius=8,
            fg_color=C_ACCENT, hover_color="#009fcc", text_color="#000000",
            font=ctk.CTkFont(family="Courier New", size=13, weight="bold")
        )
        self.login_btn.grid(row=6, column=0, padx=24, pady=(4, 24))
        CyberAnimator.apply_glow_effect(self.login_btn, C_ACCENT, "#33d6ff", C_ACCENT)

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
        self.login_btn.configure(state="normal", text="Login")

        if session is None:
            self._show_error("Invalid credentials or account locked")
            self.password_var.set("")  # clear password field on failure
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
            loading_frame, text="ESTABLISHING SECURE ZERO-TRUST TUNNEL...",
            font=ctk.CTkFont(family="Courier New", size=16, weight="bold"),
            text_color=C_ACCENT
        ).place(relx=0.5, rely=0.5, anchor="center")
        
        self.update()
        import time
        time.sleep(0.6)  # High quality cinematic transition delay
        
        self._build_main_ui()
        self._start_ttl_watcher()

    def _build_main_ui(self):
        """Build the tabbed main interface after successful login."""
        for w in self.winfo_children():
            w.destroy()

        # Top bar
        topbar = ctk.CTkFrame(self, fg_color=C_PANEL, height=52, corner_radius=0)
        topbar.pack(fill="x", side="top")
        topbar.pack_propagate(False)

        ctk.CTkLabel(
            topbar, text="  SHADOWMIND",
            font=ctk.CTkFont(family="Courier New", size=18, weight="bold"),
            text_color=C_ACCENT
        ).pack(side="left", padx=8)

        # Session info + TTL
        self.ttl_label = ctk.CTkLabel(
            topbar, text="", font=ctk.CTkFont(size=12), text_color=C_SUBTEXT
        )
        self.ttl_label.pack(side="right", padx=16)

        self.user_label = ctk.CTkLabel(
            topbar,
            text=f"  {self.session.username}  [{self.session.role.value.upper()}]",
            font=ctk.CTkFont(size=12), text_color=C_TEXT
        )
        self.user_label.pack(side="right", padx=4)

        ctk.CTkButton(
            topbar, text="Logout", command=self._logout,
            width=80, height=32, fg_color=C_DANGER, hover_color="#cc0000",
            font=ctk.CTkFont(size=12)
        ).pack(side="right", padx=8)

        # Tab view
        self.tabs = ctk.CTkTabview(self, fg_color=C_BG, segmented_button_fg_color=C_PANEL,
                                   segmented_button_selected_color=C_ACCENT,
                                   segmented_button_selected_hover_color="#009fcc",
                                   segmented_button_unselected_color=C_PANEL,
                                   segmented_button_unselected_hover_color="#1e2230")
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
