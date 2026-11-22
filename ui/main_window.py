# =============================================================================
# FILE: ui/main_window.py
# PURPOSE: Enterprise Cyber Defense SOC Command Center (ShadowMind Main Shell).
#          - Collapsible Tactical Left Navigation Sidebar (Expanded 230px / Collapsed 68px).
#          - Compact Top Navigation Flight Deck with breadcrumbs, DEFCON posture,
#            live TTL countdown, and emergency purge actions.
#          - Zero-Latency View Container switching between:
#            1. Overview / Dashboard
#            2. AI Detection Matrix
#            3. Ephemeral File Vault
#            4. Honeypot Deception
#            5. Threat Intelligence & Forensics
#            6. System Settings
# =============================================================================

import time
import logging
import threading
import customtkinter as ctk
from tkinter import messagebox
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.auth.auth import login, logout, require_role, bootstrap_admin, Role, Session
from ui.tabs.dashboard_tab import DashboardTab
from ui.tabs.ai_matrix_tab import AIDetectionTab as AIMatrixTab
from ui.tabs.vault_tab import VaultTab
from ui.tabs.honeypot_tab import HoneypotTab
from ui.tabs.incidents_tab import IncidentsTab
from ui.tabs.settings_tab import SettingsTab
from ui.animations import CyberAnimator

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

from ui.theme import (
    COLOR_BG as C_BG,
    COLOR_CARD as C_PANEL,
    COLOR_CARD_HOVER as C_PANEL_HOVER,
    COLOR_CYAN as C_ACCENT,
    COLOR_CYAN_DIM as C_ACCENT_DIM,
    COLOR_DANGER as C_DANGER,
    COLOR_WARNING as C_WARNING,
    COLOR_SUCCESS as C_SUCCESS,
    COLOR_TEXT_PRIMARY as C_TEXT,
    COLOR_TEXT_SECONDARY as C_SUBTEXT,
    COLOR_TEXT_MUTED as C_MUTED,
    COLOR_BORDER as C_BORDER,
    COLOR_BORDER_FOCUS as C_FOCUS,
    COLOR_SURFACE as C_SURFACE,
    FONT_BRAND, FONT_MONO, FONT_BODY, FONT_TITLE
)


def _load_emblem_image(size=(48, 40)):
    try:
        from PIL import Image
        logo_path = ROOT_DIR / "Futuristic Shadowmind Emblem Logo.png"
        if logo_path.exists():
            pil_img = Image.open(str(logo_path))
            return ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=size)
    except Exception:
        pass
    return None


# =============================================================================
# Login Frame (Holographic Tactical Gateway)
# =============================================================================

class LoginFrame(ctk.CTkFrame):
    """
    Shown before authentication. Collects operator credentials with high-tech
    holographic HUD elements, interactive focus glows, and tactile responses.
    """

    def __init__(self, parent, on_login_success):
        super().__init__(parent, fg_color=C_BG)
        self.on_login_success = on_login_success
        self.logo_img = _load_emblem_image(size=(80, 64))
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # Top holographic status HUD
        top_banner = ctk.CTkFrame(self, fg_color=C_SURFACE, height=36, corner_radius=0, border_width=1, border_color=C_BORDER)
        top_banner.grid(row=0, column=0, sticky="ew")
        top_banner.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            top_banner,
            text="ShadowMind Security Gateway",
            font=ctk.CTkFont(family=FONT_TITLE, size=11, weight="bold"),
            text_color=C_SUBTEXT
        ).grid(row=0, column=0, padx=20, pady=8, sticky="w")

        self.enclave_status_label = ctk.CTkLabel(
            top_banner,
            text="● System Ready · AES-256 Verified",
            font=ctk.CTkFont(family=FONT_BODY, size=10, weight="bold"),
            text_color=C_SUCCESS
        )
        self.enclave_status_label.grid(row=0, column=2, padx=20, pady=8, sticky="e")
        CyberAnimator.start_pulse_animation(self.enclave_status_label, C_SUCCESS, "#80ffbf", 1.2)

        # Brand centerpiece with logo emblem
        brand_container = ctk.CTkFrame(self, fg_color="transparent")
        brand_container.grid(row=2, column=0, pady=(24, 16))

        if self.logo_img:
            logo_frame = ctk.CTkFrame(brand_container, fg_color="#08101d", corner_radius=12, border_width=1, border_color=C_BORDER)
            logo_frame.pack(side="top", pady=(0, 8), padx=10)
            ctk.CTkLabel(logo_frame, text="", image=self.logo_img).pack(padx=14, pady=10)

        ctk.CTkLabel(
            brand_container,
            text="SHADOWMIND",
            font=ctk.CTkFont(family=FONT_TITLE, size=30, weight="bold"),
            text_color=C_TEXT
        ).pack()

        ctk.CTkLabel(
            brand_container,
            text="Autonomous AI Cyber Defense Platform",
            font=ctk.CTkFont(family=FONT_BODY, size=12),
            text_color=C_ACCENT
        ).pack(pady=(2, 0))

        # Main login authentication card
        card = ctk.CTkFrame(
            self, fg_color=C_PANEL, corner_radius=14,
            border_width=1, border_color=C_BORDER,
            width=460
        )
        card.grid(row=3, column=0, padx=40, pady=(0, 20), sticky="n")
        card.grid_columnconfigure(0, weight=1)
        CyberAnimator.apply_glow_card_hover(card, C_BORDER, C_ACCENT, C_PANEL, C_PANEL_HOVER)

        ctk.CTkFrame(card, fg_color=C_ACCENT, height=2, corner_radius=0).grid(row=0, column=0, sticky="ew")

        ctk.CTkLabel(
            card,
            text="Sign In",
            font=ctk.CTkFont(family=FONT_TITLE, size=15, weight="bold"),
            text_color=C_TEXT
        ).grid(row=1, column=0, pady=(18, 2), padx=24, sticky="w")

        ctk.CTkLabel(
            card,
            text="Enter authorized operator credentials to access the console.",
            font=ctk.CTkFont(family=FONT_BODY, size=11),
            text_color=C_SUBTEXT
        ).grid(row=2, column=0, pady=(0, 16), padx=24, sticky="w")

        # Username
        ctk.CTkLabel(
            card, text="Operator Identifier",
            font=ctk.CTkFont(family=FONT_BODY, size=11, weight="bold"),
            text_color=C_SUBTEXT
        ).grid(row=3, column=0, padx=24, sticky="w")

        self.username_var = ctk.StringVar(value="souryanew@shadowmind.com")
        self.user_entry = ctk.CTkEntry(
            card, textvariable=self.username_var, height=38,
            fg_color="#090f1a", text_color=C_TEXT,
            font=ctk.CTkFont(family=FONT_BODY, size=12),
            border_width=1, border_color=C_BORDER, corner_radius=8
        )
        self.user_entry.grid(row=4, column=0, padx=24, pady=(4, 14), sticky="ew")
        CyberAnimator.apply_entry_focus_glow(self.user_entry, C_BORDER, C_ACCENT)

        # Password
        ctk.CTkLabel(
            card, text="Password",
            font=ctk.CTkFont(family=FONT_BODY, size=11, weight="bold"),
            text_color=C_SUBTEXT
        ).grid(row=5, column=0, padx=24, sticky="w")

        self.password_var = ctk.StringVar(value="Sourya@2026dey")
        self.pw_entry = ctk.CTkEntry(
            card, textvariable=self.password_var, show="●", height=38,
            fg_color="#090f1a", text_color=C_TEXT,
            font=ctk.CTkFont(family=FONT_BODY, size=12),
            border_width=1, border_color=C_BORDER, corner_radius=8
        )
        self.pw_entry.grid(row=6, column=0, padx=24, pady=(4, 14), sticky="ew")
        CyberAnimator.apply_entry_focus_glow(self.pw_entry, C_BORDER, C_ACCENT)

        # Error readout
        self.error_label = ctk.CTkLabel(
            card, text="",
            font=ctk.CTkFont(family=FONT_BODY, size=11, weight="bold"),
            text_color=C_DANGER
        )
        self.error_label.grid(row=7, column=0, padx=24, pady=(0, 6), sticky="w")

        # Login button
        self.login_btn = ctk.CTkButton(
            card,
            text="⚡ Sign In to Console",
            command=self._attempt_login,
            height=42,
            fg_color=C_ACCENT, hover_color="#38d4ff",
            text_color="#04070d",
            font=ctk.CTkFont(family=FONT_TITLE, size=12, weight="bold"),
            corner_radius=8
        )
        self.login_btn.grid(row=8, column=0, padx=24, pady=(4, 14), sticky="ew")
        CyberAnimator.apply_button_cyber_reaction(
            self.login_btn, normal_bg=C_ACCENT, hover_bg="#38d4ff",
            normal_text="#04070d", hover_text="#04070d", press_bg="#00a8b3"
        )

        ctk.CTkLabel(
            card,
            text="🔒 Zero-knowledge ephemeral memory protection",
            font=ctk.CTkFont(family=FONT_BODY, size=9),
            text_color=C_MUTED
        ).grid(row=9, column=0, pady=(0, 16))

        # Bottom status banner
        bot_banner = ctk.CTkFrame(self, fg_color=C_SURFACE, height=32, corner_radius=0, border_width=1, border_color=C_BORDER)
        bot_banner.grid(row=4, column=0, sticky="ew")
        bot_banner.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            bot_banner,
            text="AES-256-GCM Ephemeral Encryption · Real-Time AI Detection Engine",
            font=ctk.CTkFont(family=FONT_BODY, size=9),
            text_color=C_MUTED
        ).grid(row=0, column=0, padx=20, pady=6, sticky="w")

        ctk.CTkLabel(
            bot_banner,
            text="ShadowMind v2.4.0",
            font=ctk.CTkFont(family=FONT_BODY, size=9),
            text_color=C_MUTED
        ).grid(row=0, column=2, padx=20, pady=6, sticky="e")

        self.pw_entry.bind("<Return>", lambda e: self._attempt_login())

    def _attempt_login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get()
        if not username or not password:
            self.error_label.configure(text="Username and password are required")
            return

        self.login_btn.configure(state="disabled", text="Signing in...")
        self.after(100, lambda: self._do_login(username, password))

    def _do_login(self, username: str, password: str):
        session = login(username, password)
        self.login_btn.configure(state="normal", text="⚡ Sign In to Console")

        if session is None:
            self.error_label.configure(text="Invalid credentials or account locked")
            self.password_var.set("")
        else:
            self.error_label.configure(text="")
            self.on_login_success(session)


# =============================================================================
# Main Application Window (Enterprise SOC Command Shell)
# =============================================================================

class ShadowMindApp(ctk.CTk):
    """
    Root window hosting the Collapsible Left Sidebar Shell,
    Top Flight Deck, and Zero-Flicker View Container.
    """

    def __init__(self):
        super().__init__()
        self.title("ShadowMind — Autonomous AI Cyber Defense System")
        self.geometry("1340x840")
        self.minsize(1080, 720)
        self.configure(fg_color=C_BG)

        try:
            ico_path = ROOT_DIR / "shadowmind_icon.ico"
            if ico_path.exists():
                self.iconbitmap(str(ico_path))
        except Exception:
            pass

        self.session: Session = None
        self._running = True
        self.sidebar_expanded = True
        self.sidebar_width_expanded = 224
        self.sidebar_width_collapsed = 64
        self.current_tab_name = "Dashboard"

        self.header_logo = _load_emblem_image(size=(32, 26))
        self.side_logo = _load_emblem_image(size=(38, 30))

        bootstrap_admin()
        self._show_login()

    def _show_login(self):
        for w in self.winfo_children():
            w.destroy()
        LoginFrame(self, on_login_success=self._on_login_success).pack(fill="both", expand=True)

    def _on_login_success(self, session: Session):
        self.session = session

        for w in self.winfo_children():
            w.destroy()

        loading_frame = ctk.CTkFrame(self, fg_color=C_BG)
        loading_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(
            loading_frame, text="● Initializing Security Console...",
            font=ctk.CTkFont(family=FONT_TITLE, size=15, weight="bold"),
            text_color=C_ACCENT
        ).place(relx=0.5, rely=0.47, anchor="center")

        ctk.CTkLabel(
            loading_frame, text="Loading AI detection models & establishing secure session",
            font=ctk.CTkFont(family=FONT_BODY, size=11),
            text_color=C_SUBTEXT
        ).place(relx=0.5, rely=0.53, anchor="center")

        self.update()
        time.sleep(0.2)

        self._build_main_shell()
        self._start_ttl_watcher()

    # -------------------------------------------------------------------------
    # Application Shell Builder
    # -------------------------------------------------------------------------

    def _build_main_shell(self):
        for w in self.winfo_children():
            w.destroy()

        # Grid configuration: Row 0 is Topbar, Row 1 is Main Body
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ---------------------------------------------------------------------
        # 1. TOP FLIGHT DECK HEADER
        # ---------------------------------------------------------------------
        self.topbar = ctk.CTkFrame(self, fg_color=C_SURFACE, height=52, corner_radius=0, border_width=1, border_color=C_BORDER)
        self.topbar.grid(row=0, column=0, sticky="ew")
        self.topbar.pack_propagate(False)

        # Left brand & breadcrumbs
        left_box = ctk.CTkFrame(self.topbar, fg_color="transparent")
        left_box.pack(side="left", padx=16)

        self.btn_toggle_sidebar = ctk.CTkButton(
            left_box, text="☰", command=self._toggle_sidebar,
            width=32, height=32, fg_color=C_PANEL, hover_color=C_PANEL_HOVER,
            text_color=C_TEXT, font=ctk.CTkFont(size=14, weight="bold"),
            border_width=1, border_color=C_BORDER, corner_radius=6
        )
        self.btn_toggle_sidebar.pack(side="left", padx=(0, 10))
        CyberAnimator.apply_button_cyber_reaction(self.btn_toggle_sidebar, normal_bg=C_PANEL, hover_bg=C_PANEL_HOVER, normal_text=C_TEXT, hover_text=C_ACCENT)

        if self.header_logo:
            ctk.CTkLabel(left_box, text="", image=self.header_logo).pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            left_box, text="SHADOWMIND",
            font=ctk.CTkFont(family=FONT_TITLE, size=15, weight="bold"), text_color=C_TEXT
        ).pack(side="left")

        self.lbl_breadcrumb = ctk.CTkLabel(
            left_box, text="  ›  Dashboard",
            font=ctk.CTkFont(family=FONT_BODY, size=11, weight="bold"), text_color=C_ACCENT
        )
        self.lbl_breadcrumb.pack(side="left")

        # Center status HUD
        center_hud = ctk.CTkFrame(self.topbar, fg_color="#081424", corner_radius=6, border_width=1, border_color=C_BORDER)
        center_hud.pack(side="left", padx=(20, 0))

        self.posture_live_dot = ctk.CTkLabel(
            center_hud, text="● Defense Posture: Optimal",
            font=ctk.CTkFont(family=FONT_BODY, size=10, weight="bold"), text_color=C_SUCCESS
        )
        self.posture_live_dot.pack(side="left", padx=(10, 8), pady=4)
        CyberAnimator.start_pulse_animation(self.posture_live_dot, C_SUCCESS, "#80ffbf", 1.0)

        ctk.CTkLabel(
            center_hud, text="·  Ingest: 1.45 MB/s",
            font=ctk.CTkFont(family=FONT_BODY, size=10), text_color=C_SUBTEXT
        ).pack(side="left", padx=(0, 10), pady=4)

        # Right operator & logout actions
        right_box = ctk.CTkFrame(self.topbar, fg_color="transparent")
        right_box.pack(side="right", padx=16)

        # User pill
        user_pill = ctk.CTkFrame(right_box, fg_color=C_PANEL, corner_radius=6, border_width=1, border_color=C_BORDER)
        user_pill.pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            user_pill, text="OP", font=ctk.CTkFont(family=FONT_TITLE, size=9, weight="bold"),
            fg_color=C_ACCENT, text_color="#04070d", corner_radius=3, width=22, height=20
        ).pack(side="left", padx=5, pady=3)

        role_str = self.session.role.value.capitalize()
        ctk.CTkLabel(
            user_pill, text=f"{self.session.username} · {role_str}",
            font=ctk.CTkFont(family=FONT_BODY, size=11), text_color=C_TEXT
        ).pack(side="left", padx=(2, 8))

        # TTL Chip
        ttl_box = ctk.CTkFrame(right_box, fg_color="#071220", corner_radius=6, border_width=1, border_color=C_BORDER)
        ttl_box.pack(side="left", padx=(0, 8))

        self.ttl_label = ctk.CTkLabel(
            ttl_box, text="TTL: --:--:--", font=ctk.CTkFont(family=FONT_BODY, size=10, weight="bold"), text_color=C_ACCENT
        )
        self.ttl_label.pack(side="left", padx=10, pady=3)

        # Logout button
        btn_logout = ctk.CTkButton(
            right_box, text="Sign Out", command=self._logout,
            width=84, height=28, fg_color="#220a13", hover_color=C_DANGER,
            text_color=C_DANGER, font=ctk.CTkFont(family=FONT_BODY, size=10, weight="bold"),
            border_width=1, border_color="#521220", corner_radius=6
        )
        btn_logout.pack(side="left")
        CyberAnimator.apply_button_cyber_reaction(btn_logout, normal_bg="#220a13", hover_bg=C_DANGER, normal_text=C_DANGER, hover_text="#ffffff", press_bg="#80002b")

        # ---------------------------------------------------------------------
        # 2. MAIN HORIZONTAL BODY (Sidebar + Central Container)
        # ---------------------------------------------------------------------
        self.body_container = ctk.CTkFrame(self, fg_color=C_BG)
        self.body_container.grid(row=1, column=0, sticky="nsew")
        self.body_container.grid_rowconfigure(0, weight=1)
        self.body_container.grid_columnconfigure(1, weight=1)

        # Left Collapsible Sidebar
        self.sidebar = ctk.CTkFrame(
            self.body_container, fg_color=C_SURFACE,
            width=self.sidebar_width_expanded, corner_radius=0,
            border_width=1, border_color=C_BORDER
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_columnconfigure(0, weight=1)
        self.sidebar.grid_rowconfigure(1, weight=1)

        # Build Sidebar Navigation Items
        self._build_sidebar_items()

        # Central View Container Frame
        self.view_container = ctk.CTkFrame(self.body_container, fg_color=C_BG)
        self.view_container.grid(row=0, column=1, sticky="nsew")
        self.view_container.grid_rowconfigure(0, weight=1)
        self.view_container.grid_columnconfigure(0, weight=1)

        # Instantiate all tabs once for instant 0ms zero-latency switching
        self.views = {
            "Dashboard": DashboardTab(self.view_container, self.session),
            "AI Matrix": AIMatrixTab(self.view_container, self.session),
            "File Vault": VaultTab(self.view_container, self.session),
            "Honeypot": HoneypotTab(self.view_container, self.session),
            "Incidents": IncidentsTab(self.view_container, self.session),
        }
        if require_role(self.session, Role.ADMIN):
            self.views["Settings"] = SettingsTab(self.view_container, self.session)

        # Place all views in the same grid cell so geometries are negotiated once (sub-millisecond tab switching)
        for view in self.views.values():
            view.grid(row=0, column=0, sticky="nsew")

        # Display initial tab
        self._switch_view("Dashboard")

    # -------------------------------------------------------------------------
    # Sidebar Navigation
    # -------------------------------------------------------------------------

    def _build_sidebar_items(self):
        # Top branding header in sidebar
        side_head = ctk.CTkFrame(self.sidebar, fg_color="transparent", height=50)
        side_head.grid(row=0, column=0, sticky="ew", padx=10, pady=(12, 10))

        if self.side_logo:
            self.side_logo_label = ctk.CTkLabel(side_head, text="", image=self.side_logo)
            self.side_logo_label.pack(side="left", padx=(4, 8))

        self.side_title_label = ctk.CTkLabel(
            side_head, text="Command Center\nSecurity Console",
            font=ctk.CTkFont(family=FONT_TITLE, size=10, weight="bold"),
            text_color=C_SUBTEXT, justify="left"
        )
        self.side_title_label.pack(side="left")

        # Scrollable navigation buttons list
        self.nav_scroll = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.nav_scroll.grid(row=1, column=0, sticky="nsew", padx=6)
        self.nav_scroll.grid_columnconfigure(0, weight=1)

        self.nav_buttons = {}
        nav_defs = [
            ("Dashboard", "📊", "Dashboard"),
            ("AI Matrix", "🧠", "AI Detection"),
            ("File Vault", "🔒", "File Vault"),
            ("Honeypot", "🍯", "Honeypots"),
            ("Incidents", "⚡", "Threat Intel"),
        ]
        if require_role(self.session, Role.ADMIN):
            nav_defs.append(("Settings", "⚙️", "Settings"))

        for key, icon, label in nav_defs:
            btn = ctk.CTkButton(
                self.nav_scroll,
                text=f"  {icon}   {label}" if self.sidebar_expanded else icon,
                command=lambda k=key: self._switch_view(k),
                height=40,
                fg_color="transparent",
                hover_color=C_PANEL,
                text_color=C_SUBTEXT,
                font=ctk.CTkFont(family=FONT_BODY, size=11, weight="bold"),
                anchor="w" if self.sidebar_expanded else "center",
                corner_radius=8
            )
            btn.pack(fill="x", pady=3)
            self.nav_buttons[key] = (btn, icon, label)

        # Bottom footer in sidebar
        self.side_footer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.side_footer.grid(row=2, column=0, sticky="ew", padx=10, pady=12)

        self.lbl_side_health = ctk.CTkLabel(
            self.side_footer, text="● System Online" if self.sidebar_expanded else "●",
            font=ctk.CTkFont(family=FONT_BODY, size=10, weight="bold"), text_color=C_SUCCESS
        )
        self.lbl_side_health.pack(anchor="w" if self.sidebar_expanded else "center")
        CyberAnimator.start_pulse_animation(self.lbl_side_health, C_SUCCESS, "#80ffbf", 1.0)

        self.lbl_side_ver = ctk.CTkLabel(
            self.side_footer, text="Version 2.4.0" if self.sidebar_expanded else "v2.4",
            font=ctk.CTkFont(family=FONT_BODY, size=9), text_color=C_MUTED
        )
        self.lbl_side_ver.pack(anchor="w" if self.sidebar_expanded else "center")

    def _toggle_sidebar(self):
        self.sidebar_expanded = not self.sidebar_expanded
        target_width = self.sidebar_width_expanded if self.sidebar_expanded else self.sidebar_width_collapsed
        self.sidebar.configure(width=target_width)

        # Update labels in sidebar buttons
        for key, (btn, icon, label) in self.nav_buttons.items():
            btn.configure(
                text=f"  {icon}   {label}" if self.sidebar_expanded else icon,
                anchor="w" if self.sidebar_expanded else "center"
            )

        if self.sidebar_expanded:
            self.side_title_label.pack(side="left")
            self.lbl_side_health.configure(text="● System Online")
            self.lbl_side_ver.configure(text="Version 2.4.0")
        else:
            self.side_title_label.pack_forget()
            self.lbl_side_health.configure(text="●")
            self.lbl_side_ver.configure(text="v2.4")

    def _switch_view(self, target_tab: str):
        if target_tab not in self.views:
            return

        self.current_tab_name = target_tab
        display_names = {
            "Dashboard": "Dashboard",
            "AI Matrix": "AI Detection",
            "File Vault": "File Vault",
            "Honeypot": "Honeypots",
            "Incidents": "Threat Intel",
            "Settings": "Settings"
        }
        crumb_text = display_names.get(target_tab, target_tab)
        self.lbl_breadcrumb.configure(text=f"  ›  {crumb_text}")

        # Update nav buttons active appearance
        for key, (btn, icon, label) in self.nav_buttons.items():
            if key == target_tab:
                btn.configure(fg_color="#0e1b2f", text_color=C_ACCENT, border_width=1, border_color=C_ACCENT_DIM)
            else:
                btn.configure(fg_color="transparent", text_color=C_SUBTEXT, border_width=0)

        # Instant sub-millisecond view raise (zero re-layout or widget remap lag)
        target_view = self.views[target_tab]
        target_view.tkraise()

    # -------------------------------------------------------------------------
    # Session TTL Watcher & Auto-Logout
    # -------------------------------------------------------------------------

    def _start_ttl_watcher(self):
        self._ttl_thread = threading.Thread(target=self._ttl_loop, daemon=True)
        self._ttl_thread.start()

    def _ttl_loop(self):
        while self._running:
            if not self._running:
                break
            if self.session and not self.session.is_valid():
                logger.info("Session TTL expired — auto logout triggered")
                try:
                    self.after(0, self._logout_expired)
                except Exception:
                    pass
                return
            if self.session:
                remaining = int(self.session.ttl_seconds - (time.time() - self.session.created_at))
                h, rem = divmod(max(remaining, 0), 3600)
                m, s = divmod(rem, 60)
                ttl_str = f"TTL: {h:02d}:{m:02d}:{s:02d}"
                try:
                    self.after(0, lambda t=ttl_str: self._update_ttl_label(t))
                except Exception:
                    pass
            time.sleep(1)

    def _update_ttl_label(self, text: str):
        try:
            self.ttl_label.configure(text=text)
        except Exception:
            pass

    def _logout_expired(self):
        messagebox.showwarning(
            "Session Expired",
            "Your session TTL has elapsed.\nAll keys zero-wiped from volatile RAM.\nPlease log in again."
        )
        self._logout()

    def _logout(self):
        self._running = False
        try:
            from src.workspace.workspace_vault import wipe_session_keystore
            from src.vault.session_state import SessionState
            wipe_session_keystore()
            SessionState.reset()
        except Exception:
            pass
        if self.session:
            logout(self.session)
            self.session = None
        self._running = True
        self._show_login()

    def on_closing(self):
        self._running = False
        try:
            from src.workspace.workspace_vault import wipe_session_keystore
            from src.vault.session_state import SessionState
            wipe_session_keystore()
            SessionState.reset()
        except Exception:
            pass
        if self.session:
            logout(self.session)
        self.destroy()
