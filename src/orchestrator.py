# =============================================================================
# FILE: src/orchestrator.py
# PURPOSE: Master Pipeline Orchestrator for ShadowMind.
#          Unifies all 4 core pillars into an end-to-end autonomous defense loop:
#          1. Ingests network flow / file telemetry
#          2. Evaluates risk via 3-way ensemble (Spatial CNN + Temporal LSTM + HoneyGraph GNN)
#          3. Routes decision:
#             - BENIGN: Allow & monitor
#             - SUSPICIOUS: Redirect traffic to Dynamic Honeypot
#             - CONFIRMED EXFILTRATION: Redirect to Honeypot + Trigger Poison Pill
#               Vault emergency key rotation in < 50ms + Log SOC Alert
#          4. On session end: executes TTL RAM zero-wipe of all decryption keys.
# =============================================================================

import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import numpy as np
import yaml

from src.detection.engine import DetectionEngine
from src.vault.rotation import emergency_rotate_keys
from src.vault.session_state import SessionState
from src.vault.ttl_destruct import zero_wipe_ram_key
from src.workspace.workspace_vault import ActiveWorkspaceVault

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CONFIG_PATH = Path(__file__).resolve().parents[1] / "configs" / "thresholds.yaml"


class PipelineOrchestrator:
    """
    Coordinates real-time detection, vault rotation, honeypot deception,
    and TTL destruction in a unified autonomous security loop.
    """

    def __init__(self):
        with open(CONFIG_PATH, "r") as f:
            self.cfg = yaml.safe_load(f)

        self.engine = DetectionEngine()
        self.engine.load_weights()
        self.engine.set_eval_mode()
        self.redirector = HoneypotRedirector()
        self.decoy_mgr = DecoyManager()
        self.decoy_mgr.deploy_decoys()
        self.vault_dir = Path(__file__).resolve().parents[1] / "data" / "vault"
        self.vault_dir.mkdir(parents=True, exist_ok=True)

        logger.info("ShadowMind Pipeline Orchestrator initialized and armed.")

    def process_telemetry(
        self,
        features_flat: np.ndarray,
        features_seq: np.ndarray,
        source_ip: str = "127.0.0.1",
        requested_resource: str = "/vault/data"
    ) -> Dict[str, Any]:
        """
        Executes the full defense pipeline on incoming traffic telemetry:
        Ingest ➔ 3-Way ML Predict ➔ Autonomous Response.
        """
        start_time = time.time()

        # Step 1: 3-Way Neural Ensemble Inference (CNN + LSTM + GNN)
        res = self.engine.predict(features_flat, features_seq)
        score = res["risk_score"]
        label = res["threat_label"]

        response_actions = []
        elapsed_rotation_ms = 0.0

        # Step 2: Autonomous Decision Logic
        if label == "BENIGN":
            response_actions.append("ALLOW_AND_MONITOR")

        elif label == "SUSPICIOUS":
            # Redirect to dynamic honeypot sandbox
            redir_entry = self.redirector.handle_redirect(source_ip, requested_resource)
            response_actions.append(f"HONEYPOT_REDIRECT: {redir_entry}")

        elif label == "CONFIRMED EXFILTRATION":
            # Action 1: Deception
            redir_entry = self.redirector.handle_redirect(source_ip, requested_resource)
            response_actions.append(f"HONEYPOT_REDIRECT: {redir_entry}")

            # Action 1.5: Active Workspace Auto-Lockdown (Encrypt all plaintext files instantly!)
            workspace = ActiveWorkspaceVault()
            locked_count = workspace.auto_lockdown()
            if locked_count > 0:
                response_actions.append(f"WORKSPACE_AUTO_LOCKED: {locked_count} active workspace files encrypted into ciphertext")

            # Action 2: Poison Pill Emergency Key Rotation
            protected_files = list(self.vault_dir.glob("*.*"))
            if protected_files:
                old_key = SessionState.get_key()
                new_key, elapsed_rotation_ms = emergency_rotate_keys(old_key, protected_files)
                SessionState.set_key(new_key)
                response_actions.append(f"POISON_PILL_ROTATED: {len(protected_files)} files re-encrypted in {elapsed_rotation_ms:.2f}ms")
            else:
                response_actions.append("POISON_PILL_TRIGGERED: (No active vault files to rotate)")

        total_latency_ms = (time.time() - start_time) * 1000.0

        return {
            "risk_score": score,
            "threat_label": label,
            "source_ip": source_ip,
            "actions_executed": response_actions,
            "rotation_time_ms": elapsed_rotation_ms,
            "total_latency_ms": round(total_latency_ms, 2)
        }

    def terminate_session(self) -> bool:
        """
        Executes TTL Self-Destruct RAM Zero-Wipe upon session logout or expiry.
        """
        active_key = SessionState.get_key()
        success = zero_wipe_ram_key(active_key)
        SessionState.reset()
        logger.info("Orchestrator: Session terminated. All RAM keys destroyed.")
        return success


if __name__ == "__main__":
    orch = PipelineOrchestrator()
    dummy_flat = np.random.randn(1, 13).astype(np.float32)
    dummy_seq  = np.random.randn(1, 50, 13).astype(np.float32)
    result = orch.process_telemetry(dummy_flat, dummy_seq)
    print("Orchestrator Benign Run:", result)
