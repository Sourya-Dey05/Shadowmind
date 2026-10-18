# =============================================================================
# FILE: src/honeypot/decoy_manager.py
# PURPOSE: Dynamic Honeypot Decoy Manager.
#          Creates and manages realistic fake files, decoy shares, and trap
#          credentials (e.g., fake database configs, financial spreadsheets)
#          to deceive attackers, waste their time, and harvest intelligence
#          when they attempt unauthorized access.
# =============================================================================

import os
import logging
from pathlib import Path
from typing import List

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DECOY_DIR = Path(__file__).resolve().parents[2] / "data" / "honeypot"


class DecoyManager:
    """
    Manages deployment and cleanup of dynamic honeypot decoys.
    """

    def __init__(self):
        self.decoy_dir = DECOY_DIR
        self.decoy_dir.mkdir(parents=True, exist_ok=True)
        self.active_decoys = []

    def deploy_decoys(self) -> List[Path]:
        """
        Deploy realistic decoy trap files into the honeypot directory.
        """
        decoys = [
            ("financial_passwords_2026.xlsx", "STRICTLY CONFIDENTIAL: root / admin_pass_9981"),
            ("customer_database_dump.sql", "CREATE TABLE users (id INT, username TEXT, cc_number TEXT); INSERT INTO users VALUES (1, 'john_doe', '4532-xxxx-xxxx-8910');"),
            ("executive_payroll_salaries.pdf", "%PDF-1.4 [FAKE PAYROLL INTEL: CEO $500k, CTO $450k]"),
            ("aws_production_keys.env", "AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE\nAWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"),
            ("internal_network_topology.txt", "Gateway: 192.168.1.1\nDomain Controller: 10.0.0.5\nVault Storage: 10.0.0.50 (HONEYPOT TRAP)")
        ]

        deployed = []
        for name, content in decoys:
            dpath = self.decoy_dir / name
            if not dpath.exists():
                dpath.write_text(content)
            if dpath not in self.active_decoys:
                self.active_decoys.append(dpath)
            deployed.append(dpath)

        logger.info(f"Deployed {len(deployed)} dynamic honeypot decoys to {self.decoy_dir}")
        return deployed

    def get_active_decoys(self) -> List[Path]:
        if not self.active_decoys:
            self.active_decoys = list(self.decoy_dir.glob("*.*"))
        return self.active_decoys


if __name__ == "__main__":
    mgr = DecoyManager()
    files = mgr.deploy_decoys()
    for f in files:
        print(f"Decoy active: {f.name}")
