# =============================================================================
# FILE: src/utils/settings_state.py
# PURPOSE: Global settings state shared across UI tabs (Theme, Signal Mode,
#          and Last Exfiltration telemetry tracking).
# =============================================================================

import datetime
from pathlib import Path


class AppSettings:
    theme_mode: str = "Dark"                 # "Dark" or "Light"
    signal_mode: str = "Attack & Benign"     # "Attack & Benign" or "Attack Only (Hide Benign)"
    
    # Last exfiltration telemetry tracking
    last_exfil_time: str = "None recorded"
    last_exfil_ip: str = "None"
    last_exfil_status: str = "No breach detected yet"

    @classmethod
    def record_exfil(cls, ip: str, status: str, timestamp: str = None):
        cls.last_exfil_time = timestamp or datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        cls.last_exfil_ip = ip
        cls.last_exfil_status = status

    @classmethod
    def sync_from_latest_report(cls) -> bool:
        """
        Scan forensic report directory and sync the latest breach telemetry.
        Returns True if a report was found and loaded.
        """
        possible_dirs = [
            Path(__file__).resolve().parents[1] / "data" / "reports",
            Path(__file__).resolve().parents[2] / "src" / "data" / "reports",
            Path(__file__).resolve().parents[2] / "data" / "reports",
        ]
        
        reports = []
        for d in possible_dirs:
            if d.exists():
                reports.extend(list(d.glob("Incident_Report_*.txt")))
                
        if not reports:
            return False

        # Sort by modification time and filename descending
        reports.sort(key=lambda p: (p.stat().st_mtime, p.name), reverse=True)
        latest_report = reports[0]

        try:
            content = latest_report.read_text(encoding="utf-8")
            ts = None
            ip = None
            status = "CONFIRMED EXFILTRATION"
            confidence = ""

            for line in content.splitlines():
                line_str = line.strip()
                if "Generated (UTC):" in line_str:
                    ts = line_str.split("Generated (UTC):", 1)[1].strip()
                elif "- Source IP Address" in line_str:
                    ip = line_str.split(":", 1)[1].strip()
                elif "- Threat Classification" in line_str:
                    status = line_str.split(":", 1)[1].strip()
                elif "- Model Confidence" in line_str:
                    confidence = line_str.split(":", 1)[1].strip()

            if ts and ip:
                if confidence:
                    status_display = f"{status} (Score: {confidence})"
                else:
                    status_display = status
                cls.last_exfil_time = ts
                cls.last_exfil_ip = ip
                cls.last_exfil_status = status_display
                return True
        except Exception:
            pass

        return False


# Automatically initialize with latest report if available
try:
    AppSettings.sync_from_latest_report()
except Exception:
    pass
