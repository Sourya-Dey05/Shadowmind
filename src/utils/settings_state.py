# =============================================================================
# FILE: src/utils/settings_state.py
# PURPOSE: Global settings state shared across UI tabs (Theme, Signal Mode,
#          and Last Exfiltration telemetry tracking).
# =============================================================================

class AppSettings:
    theme_mode: str = "Dark"                 # "Dark" or "Light"
    signal_mode: str = "Attack & Benign"     # "Attack & Benign" or "Attack Only (Hide Benign)"
    
    # Last exfiltration telemetry tracking
    last_exfil_time: str = "None recorded"
    last_exfil_ip: str = "None"
    last_exfil_status: str = "No breach detected yet"

    @classmethod
    def record_exfil(cls, ip: str, status: str):
        import datetime
        cls.last_exfil_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        cls.last_exfil_ip = ip
        cls.last_exfil_status = status
