# =============================================================================
# FILE: src/honeypot/redirector.py
# PURPOSE: Traffic Redirector & Honeypot Adapter.
#          When the AI detection engine flags traffic as SUSPICIOUS or
#          CONFIRMED EXFILTRATION, this module steers the attacker away
#          from real production assets and redirects them into the dynamic
#          honeypot sandbox environment, logging their every move.
# =============================================================================

import logging
from pathlib import Path
from src.honeypot.decoy_manager import DecoyManager
from src.honeypot.interaction_log import InteractionLogger

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class HoneypotRedirector:
    """
    Manages automated redirection of malicious traffic to honeypot decoys.
    """

    def __init__(self):
        self.decoy_mgr = DecoyManager()
        self.logger_inst = InteractionLogger()
        self.decoy_mgr.deploy_decoys()

    def handle_redirect(self, attacker_ip: str, requested_resource: str) -> str:
        """
        Intercepts attacker request, logs interaction, and serves a decoy asset.
        """
        decoys = self.decoy_mgr.get_active_decoys()
        # Select a matching decoy or default to the first one
        chosen_decoy = decoys[0] if decoys else "fake_asset.txt"

        log_entry = self.logger_inst.log_interaction(
            attacker_ip=attacker_ip,
            action="REDIRECTED_ACCESS",
            decoy_target=Path(chosen_decoy).name
        )

        logger.warning(f"🍯 HONEYPOT REDIRECT: Attacker {attacker_ip} redirected from '{requested_resource}' ➔ '{Path(chosen_decoy).name}'")
        return log_entry


if __name__ == "__main__":
    redir = HoneypotRedirector()
    res = redir.handle_redirect("192.168.1.99", "/vault/secret_project_intel.txt")
    print(res)
