# =============================================================================
# FILE: src/honeypot/interaction_log.py
# PURPOSE: Honeypot Attacker Interaction Logger.
#          Records all attacker actions, file touches, credential probes,
#          and access attempts inside the honeypot decoys, compiling an
#          intelligence log for SOC analysts and incident response.
# =============================================================================

import datetime
import logging
from pathlib import Path
from typing import List

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

LOG_PATH = Path(__file__).resolve().parents[2] / "logs" / "honeypot_interactions.log"


class InteractionLogger:
    """
    Logs attacker interactions with honeypot decoys.
    """

    def __init__(self):
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    def log_interaction(self, attacker_ip: str, action: str, decoy_target: str) -> str:
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{ts}] IP: {attacker_ip} | Action: {action} | Decoy Target: {decoy_target}"
        
        with open(LOG_PATH, "a") as f:
            f.write(entry + "\n")

        logger.info(f"Honeypot Intercept: {entry}")
        return entry

    def get_recent_interactions(self, limit: int = 50) -> List[str]:
        if not LOG_PATH.exists():
            return ["No attacker interactions recorded yet."]
        
        with open(LOG_PATH, "r") as f:
            lines = f.readlines()
        return [l.strip() for l in lines[-limit:]]


if __name__ == "__main__":
    logger_inst = InteractionLogger()
    logger_inst.log_interaction("192.168.1.105", "READ", "aws_production_keys.env")
    for l in logger_inst.get_recent_interactions():
        print(l)
