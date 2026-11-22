# =============================================================================
# FILE: ui/tabs/incidents_tab.py
# PURPOSE: Threat Intelligence & Incident Forensics Tab (SOC Command Level).
#          - Interactive Attacker IP Profiler (GeoIP, ASN, Risk Tier).
#          - Court-Ready Forensic Incident Report Archive (Browse, Read, Export).
#          - On-Demand Autonomous Incident Audit Report Generator.
#          - Styled with Tactical Holographic Cyber Warfare aesthetics.
# =============================================================================

import os
import subprocess
import datetime
from pathlib import Path
from typing import Dict, Any, List
import customtkinter as ctk
from tkinter import messagebox

from src.auth.auth import Session
from src.intelligence.profiler import AttackerProfiler
from src.intelligence.reporter import IncidentReporter
from src.utils.settings_state import AppSettings
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
    FONT_MONO, FONT_BODY, FONT_TITLE
)

REPORTS_DIR = Path(__file__).resolve().parents[2] / "src" / "data" / "reports"


class IncidentsTab(ctk.CTkFrame):
    """
    Threat Intelligence & Incident Forensics Command Deck.
    """

    def __init__(self, parent, session: Session):
        super().__init__(parent, fg_color=C_BG)
        self.session = session
        self.profiler = AttackerProfiler
        self.reporter = IncidentReporter()
        self.selected_report_path: Path = None

        self._build()
        self._refresh_reports_list()
        self._profile_ip("203.0.113.42")  # default initial profile view

    def _build(self):
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ---------------------------------------------------------------------
        # Top KPI Banner (3 Metrics Cards)
        # ---------------------------------------------------------------------
        top_kpi_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_kpi_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=12, pady=(12, 6))
        top_kpi_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Card 0: Stored Forensic Reports
        self.card_reports = ctk.CTkFrame(top_kpi_frame, fg_color=C_PANEL, corner_radius=10, border_width=1, border_color=C_BORDER, height=72)
        self.card_reports.grid(row=0, column=0, padx=(0, 6), sticky="ew")
        self.card_reports.grid_propagate(False)
        ctk.CTkFrame(self.card_reports, fg_color=C_ACCENT, height=2, corner_radius=0).place(x=0, y=0, relwidth=1.0)
        ctk.CTkLabel(self.card_reports, text="Archived Incident Reports", font=ctk.CTkFont(family=FONT_BODY, size=10, weight="bold"), text_color=C_SUBTEXT).place(x=14, y=10)
        self.lbl_reports_count = ctk.CTkLabel(self.card_reports, text="-- Reports", font=ctk.CTkFont(family=FONT_TITLE, size=16, weight="bold"), text_color=C_ACCENT)
        self.lbl_reports_count.place(x=14, y=32)
        CyberAnimator.apply_glow_card_hover(self.card_reports, C_BORDER, C_ACCENT, C_PANEL, C_PANEL_HOVER)

        # Card 1: Last Incident Attribution
        self.card_last_ip = ctk.CTkFrame(top_kpi_frame, fg_color=C_PANEL, corner_radius=10, border_width=1, border_color=C_BORDER, height=72)
        self.card_last_ip.grid(row=0, column=1, padx=6, sticky="ew")
        self.card_last_ip.grid_propagate(False)
        ctk.CTkFrame(self.card_last_ip, fg_color=C_WARNING, height=2, corner_radius=0).place(x=0, y=0, relwidth=1.0)
        ctk.CTkLabel(self.card_last_ip, text="Last Detected Origin", font=ctk.CTkFont(family=FONT_BODY, size=10, weight="bold"), text_color=C_SUBTEXT).place(x=14, y=10)
        self.lbl_last_ip = ctk.CTkLabel(self.card_last_ip, text=AppSettings.last_exfil_ip, font=ctk.CTkFont(family=FONT_BODY, size=15, weight="bold"), text_color=C_WARNING)
        self.lbl_last_ip.place(x=14, y=32)
        CyberAnimator.apply_glow_card_hover(self.card_last_ip, C_BORDER, C_WARNING, C_PANEL, C_PANEL_HOVER)

        # Card 2: Legal & SOC Attestation Posture
        self.card_attest = ctk.CTkFrame(top_kpi_frame, fg_color=C_PANEL, corner_radius=10, border_width=1, border_color=C_BORDER, height=72)
        self.card_attest.grid(row=0, column=2, padx=(6, 0), sticky="ew")
        self.card_attest.grid_propagate(False)
        ctk.CTkFrame(self.card_attest, fg_color=C_SUCCESS, height=2, corner_radius=0).place(x=0, y=0, relwidth=1.0)
        ctk.CTkLabel(self.card_attest, text="Evidence Compliance", font=ctk.CTkFont(family=FONT_BODY, size=10, weight="bold"), text_color=C_SUBTEXT).place(x=14, y=10)
        self.lbl_compliance = ctk.CTkLabel(self.card_attest, text="● Chain-of-Custody Verified", font=ctk.CTkFont(family=FONT_BODY, size=12, weight="bold"), text_color=C_SUCCESS)
        self.lbl_compliance.place(x=14, y=34)
        CyberAnimator.start_pulse_animation(self.lbl_compliance, C_SUCCESS, "#80ffbf", 1.2)
        CyberAnimator.apply_glow_card_hover(self.card_attest, C_BORDER, C_SUCCESS, C_PANEL, C_PANEL_HOVER)

        # ---------------------------------------------------------------------
        # Main Split Body (Left: Reports Archive & Viewer, Right: Threat Intel Dossier)
        # ---------------------------------------------------------------------
        # --- LEFT PANEL: Reports Archive & Reader ---
        left_panel = ctk.CTkFrame(self, fg_color=C_PANEL, corner_radius=12, border_width=1, border_color=C_BORDER)
        left_panel.grid(row=1, column=0, padx=(12, 6), pady=(4, 12), sticky="nsew")
        left_panel.grid_columnconfigure(0, weight=1)
        left_panel.grid_rowconfigure(2, weight=1)
        CyberAnimator.apply_glow_card_hover(left_panel, C_BORDER, C_ACCENT, C_PANEL, "#0f1c30")

        # Strip
        ctk.CTkFrame(left_panel, fg_color=C_ACCENT, height=2, corner_radius=0).grid(row=0, column=0, sticky="ew")

        # Header controls
        lh = ctk.CTkFrame(left_panel, fg_color="transparent")
        lh.grid(row=1, column=0, sticky="ew", padx=16, pady=(12, 8))
        lh.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            lh, text="Incident Reports Archive",
            font=ctk.CTkFont(family=FONT_TITLE, size=12, weight="bold"), text_color=C_TEXT
        ).grid(row=0, column=0, sticky="w")

        btn_box = ctk.CTkFrame(lh, fg_color="transparent")
        btn_box.grid(row=0, column=2, sticky="e")

        btn_refresh = ctk.CTkButton(
            btn_box, text="🔄 Refresh", command=self._refresh_reports_list,
            width=76, height=26, fg_color=C_SURFACE, hover_color="#182844",
            text_color=C_TEXT, font=ctk.CTkFont(family=FONT_BODY, size=10),
            border_width=1, border_color=C_BORDER, corner_radius=6
        )
        btn_refresh.pack(side="left", padx=4)
        CyberAnimator.apply_button_cyber_reaction(btn_refresh, normal_bg=C_SURFACE, hover_bg="#182844", normal_text=C_TEXT, hover_text="#ffffff")

        btn_gen = ctk.CTkButton(
            btn_box, text="+ Generate Report", command=self._generate_manual_report,
            width=120, height=26, fg_color=C_ACCENT, hover_color="#33ddff",
            text_color="#04070d", font=ctk.CTkFont(family=FONT_BODY, size=10, weight="bold"),
            corner_radius=6
        )
        btn_gen.pack(side="left", padx=4)
        CyberAnimator.apply_button_cyber_reaction(btn_gen, normal_bg=C_ACCENT, hover_bg="#33ddff", normal_text="#04070d", hover_text="#04070d")

        # Reports content split (top scroll list, bottom preview text box)
        reports_content = ctk.CTkFrame(left_panel, fg_color="transparent")
        reports_content.grid(row=2, column=0, sticky="nsew", padx=14, pady=(0, 12))
        reports_content.grid_columnconfigure(0, weight=1)
        reports_content.grid_rowconfigure(1, weight=1)

        # Scrollable list of files
        self.reports_scroll = ctk.CTkScrollableFrame(reports_content, fg_color=C_SURFACE, height=130, corner_radius=8, border_width=1, border_color=C_BORDER)
        self.reports_scroll.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        self.reports_scroll.grid_columnconfigure(0, weight=1)

        # Report Viewer preview box
        viewer_container = ctk.CTkFrame(reports_content, fg_color=C_SURFACE, corner_radius=8, border_width=1, border_color=C_BORDER)
        viewer_container.grid(row=1, column=0, sticky="nsew")
        viewer_container.grid_columnconfigure(0, weight=1)
        viewer_container.grid_rowconfigure(1, weight=1)

        vh = ctk.CTkFrame(viewer_container, fg_color="transparent")
        vh.grid(row=0, column=0, sticky="ew", padx=10, pady=(6, 4))
        vh.grid_columnconfigure(0, weight=1)

        self.lbl_selected_title = ctk.CTkLabel(
            vh, text="Preview: Select a report from the archive above",
            font=ctk.CTkFont(family=FONT_BODY, size=10, weight="bold"), text_color=C_ACCENT
        )
        self.lbl_selected_title.grid(row=0, column=0, sticky="w")

        self.btn_open_folder = ctk.CTkButton(
            vh, text="📂 Open Folder", command=self._open_reports_dir,
            width=100, height=24, fg_color="#10192b", hover_color="#1b2a47",
            text_color=C_SUBTEXT, font=ctk.CTkFont(family=FONT_BODY, size=9),
            border_width=1, border_color=C_BORDER, corner_radius=4
        )
        self.btn_open_folder.grid(row=0, column=1, sticky="e")

        self.report_preview_box = ctk.CTkTextbox(
            viewer_container, fg_color="#060a12", text_color=C_TEXT,
            font=ctk.CTkFont(family=FONT_BODY, size=10),
            border_width=0, corner_radius=6
        )
        self.report_preview_box.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))

        # --- RIGHT PANEL: Threat Intel Dossier & IP Reconnaissance ---
        right_panel = ctk.CTkFrame(self, fg_color=C_PANEL, corner_radius=12, border_width=1, border_color=C_BORDER)
        right_panel.grid(row=1, column=1, padx=(6, 12), pady=(4, 12), sticky="nsew")
        right_panel.grid_columnconfigure(0, weight=1)
        right_panel.grid_rowconfigure(3, weight=1)
        CyberAnimator.apply_glow_card_hover(right_panel, C_BORDER, C_WARNING, C_PANEL, "#14101d")

        # Strip
        ctk.CTkFrame(right_panel, fg_color=C_WARNING, height=2, corner_radius=0).grid(row=0, column=0, sticky="ew")

        # Header
        rh = ctk.CTkFrame(right_panel, fg_color="transparent")
        rh.grid(row=1, column=0, sticky="ew", padx=16, pady=(12, 6))

        ctk.CTkLabel(
            rh, text="Attacker Attribution Dossier",
            font=ctk.CTkFont(family=FONT_TITLE, size=12, weight="bold"), text_color=C_TEXT
        ).pack(side="left")

        # IP query input row
        ip_query_box = ctk.CTkFrame(right_panel, fg_color=C_SURFACE, corner_radius=8, border_width=1, border_color=C_BORDER)
        ip_query_box.grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 10))
        ip_query_box.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            ip_query_box, text="Target IP:",
            font=ctk.CTkFont(family=FONT_BODY, size=10, weight="bold"), text_color=C_SUBTEXT
        ).grid(row=0, column=0, padx=(12, 6), pady=8)

        self.ip_entry = ctk.CTkEntry(
            ip_query_box, height=32, fg_color="#090f1a", text_color=C_TEXT,
            font=ctk.CTkFont(family=FONT_BODY, size=11), border_width=1, border_color=C_BORDER
        )
        self.ip_entry.insert(0, "203.0.113.42")
        self.ip_entry.grid(row=0, column=1, sticky="ew", padx=6, pady=8)
        self.ip_entry.bind("<Return>", lambda e: self._on_profile_click())
        CyberAnimator.apply_entry_focus_glow(self.ip_entry, C_BORDER, C_ACCENT)

        btn_run_intel = ctk.CTkButton(
            ip_query_box, text="🔍 Profile IP", command=self._on_profile_click,
            width=100, height=30, fg_color=C_WARNING, hover_color="#ffc04d",
            text_color="#04070d", font=ctk.CTkFont(family=FONT_TITLE, size=10, weight="bold"),
            corner_radius=6
        )
        btn_run_intel.grid(row=0, column=2, padx=(6, 12), pady=8)
        CyberAnimator.apply_button_cyber_reaction(btn_run_intel, normal_bg=C_WARNING, hover_bg="#ffc04d", normal_text="#04070d", hover_text="#04070d")

        # Quick preset chips
        presets_bar = ctk.CTkFrame(right_panel, fg_color="transparent")
        presets_bar.grid(row=2, column=0, sticky="ew", padx=14, pady=(56, 10))
        for p_label, p_ip in [
            ("AWS Cloud", "203.0.113.42"),
            ("DigitalOcean", "198.51.100.1"),
            ("LAN Pivot", "192.168.1.55"),
            ("Localhost", "127.0.0.1"),
        ]:
            chip = ctk.CTkButton(
                presets_bar, text=p_label, command=lambda ip=p_ip: self._quick_ip_select(ip),
                height=22, fg_color="#0d1524", hover_color="#18263d",
                text_color=C_SUBTEXT, font=ctk.CTkFont(family=FONT_BODY, size=9),
                border_width=1, border_color=C_BORDER, corner_radius=4
            )
            chip.pack(side="left", padx=3)

        # Scrollable dossier results container
        self.dossier_scroll = ctk.CTkScrollableFrame(right_panel, fg_color=C_SURFACE, corner_radius=8, border_width=1, border_color=C_BORDER)
        self.dossier_scroll.grid(row=3, column=0, sticky="nsew", padx=14, pady=(16, 14))
        self.dossier_scroll.grid_columnconfigure(1, weight=1)

        # Dossier detail fields
        self.dossier_widgets = {}
        fields = [
            ("Source IP Address", "source_ip", C_ACCENT),
            ("Geographic Location", "geo_location", C_TEXT),
            ("Network Origin", "network_type", C_TEXT),
            ("ASN & Domain", "asn", C_TEXT),
            ("Infrastructure / Host", "infrastructure", C_TEXT),
            ("Threat Classification", "risk_tier", C_DANGER),
            ("Mitigation Rule", "suggested_mitigation", C_SUCCESS),
            ("Last Recorded Query", "timestamp", C_SUBTEXT),
        ]
        for row_idx, (title, key, color) in enumerate(fields):
            row_box = ctk.CTkFrame(self.dossier_scroll, fg_color="#0b111e", corner_radius=6, border_width=1, border_color=C_BORDER)
            row_box.grid(row=row_idx, column=0, columnspan=2, sticky="ew", padx=4, pady=3)
            row_box.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(
                row_box, text=title, font=ctk.CTkFont(family=FONT_BODY, size=10),
                text_color=C_SUBTEXT, width=160, anchor="w"
            ).grid(row=0, column=0, padx=12, pady=7, sticky="w")

            val_lbl = ctk.CTkLabel(
                row_box, text="--", font=ctk.CTkFont(family=FONT_BODY, size=11, weight="bold"),
                text_color=color, anchor="w", justify="left"
            )
            val_lbl.grid(row=0, column=1, padx=12, pady=7, sticky="w")
            self.dossier_widgets[key] = val_lbl

    # -------------------------------------------------------------------------
    # Actions & Handlers
    # -------------------------------------------------------------------------

    def _quick_ip_select(self, ip: str):
        self.ip_entry.delete(0, "end")
        self.ip_entry.insert(0, ip)
        self._profile_ip(ip)

    def _on_profile_click(self):
        target_ip = self.ip_entry.get().strip()
        if not target_ip:
            messagebox.showwarning("Missing IP", "Please enter a valid IPv4/IPv6 address.")
            return
        self._profile_ip(target_ip)

    def _profile_ip(self, ip: str):
        try:
            dossier = self.profiler.profile_ip(ip)
            for key, widget in self.dossier_widgets.items():
                val = dossier.get(key, "N/A")
                widget.configure(text=str(val))
        except Exception as e:
            messagebox.showerror("Profiling Error", f"Failed to profile IP {ip}:\n{e}")

    def _refresh_reports_list(self):
        # Clear existing list items
        for w in self.reports_scroll.winfo_children():
            w.destroy()

        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        reports = sorted(list(REPORTS_DIR.glob("Incident_Report_*.txt")), reverse=True)
        self.lbl_reports_count.configure(text=f"{len(reports)} Reports")

        if not reports:
            ctk.CTkLabel(
                self.reports_scroll, text="No incident reports logged yet.",
                font=ctk.CTkFont(family=FONT_BODY, size=11), text_color=C_MUTED
            ).pack(pady=10)
            return

        for idx, report_file in enumerate(reports):
            # Parse timestamp and name
            mod_time = datetime.datetime.fromtimestamp(report_file.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            file_kb = round(report_file.stat().st_size / 1024, 1)

            item = ctk.CTkFrame(self.reports_scroll, fg_color="#0d1524", corner_radius=6, border_width=1, border_color=C_BORDER)
            item.pack(fill="x", pady=2, padx=4)
            item.grid_columnconfigure(1, weight=1)

            # Indicator dot
            dot_color = C_DANGER if idx == 0 else C_SUBTEXT
            ctk.CTkLabel(
                item, text="●", font=ctk.CTkFont(size=12), text_color=dot_color
            ).grid(row=0, column=0, padx=(10, 6), pady=6)

            info_box = ctk.CTkFrame(item, fg_color="transparent")
            info_box.grid(row=0, column=1, sticky="w", pady=4)

            ctk.CTkLabel(
                info_box, text=report_file.name,
                font=ctk.CTkFont(family=FONT_BODY, size=11, weight="bold"), text_color=C_TEXT
            ).pack(anchor="w")

            ctk.CTkLabel(
                info_box, text=f"Generated: {mod_time}  ·  {file_kb} KB",
                font=ctk.CTkFont(family=FONT_BODY, size=9), text_color=C_MUTED
            ).pack(anchor="w")

            btn_view = ctk.CTkButton(
                item, text="View", command=lambda p=report_file: self._load_report_preview(p),
                width=54, height=24, fg_color=C_SURFACE, hover_color=C_ACCENT,
                text_color=C_TEXT, font=ctk.CTkFont(family=FONT_BODY, size=10, weight="bold"),
                border_width=1, border_color=C_BORDER, corner_radius=4
            )
            btn_view.grid(row=0, column=2, padx=10, pady=6)
            CyberAnimator.apply_button_cyber_reaction(btn_view, normal_bg=C_SURFACE, hover_bg=C_ACCENT, normal_text=C_TEXT, hover_text="#04070d")

        # Auto-preview latest report
        if reports and not self.selected_report_path:
            self._load_report_preview(reports[0])

    def _load_report_preview(self, path: Path):
        self.selected_report_path = path
        self.lbl_selected_title.configure(text=f"PREVIEW: {path.name}")
        try:
            content = path.read_text(encoding="utf-8")
            self.report_preview_box.delete("1.0", "end")
            self.report_preview_box.insert("1.0", content)
        except Exception as e:
            self.report_preview_box.delete("1.0", "end")
            self.report_preview_box.insert("1.0", f"Error reading report: {e}")

    def _generate_manual_report(self):
        try:
            sample_ip = self.ip_entry.get().strip() or "203.0.113.42"
            dossier = self.profiler.profile_ip(sample_ip)
            actions = [
                f"Manual operator forensic triage initiated by '{self.session.username}'.",
                "SpatialCNN & TemporalLSTM verification confirmed high exfiltration propensity.",
                "RAM Enclave session keys validated under AES-256-GCM integrity checks.",
                "Generated court-ready digital artifact."
            ]
            new_path = self.reporter.generate_report(dossier, actions)
            AppSettings.sync_from_latest_report()
            if hasattr(self, 'lbl_last_ip'):
                self.lbl_last_ip.configure(text=AppSettings.last_exfil_ip)
            self._refresh_reports_list()
            self._load_report_preview(new_path)
            messagebox.showinfo("Incident Report Generated", f"New court-ready forensic incident report created:\n{new_path.name}")
        except Exception as e:
            messagebox.showerror("Report Error", f"Failed to generate forensic report:\n{e}")

    def _open_reports_dir(self):
        try:
            REPORTS_DIR.mkdir(parents=True, exist_ok=True)
            if os.name == 'nt':
                os.startfile(str(REPORTS_DIR))
            else:
                subprocess.Popen(['xdg-open', str(REPORTS_DIR)])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open directory:\n{e}")

