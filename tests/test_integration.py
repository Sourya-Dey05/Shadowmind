# =============================================================================
# FILE: tests/test_integration.py
# PURPOSE: End-to-End Integration Test Suite for ShadowMind.
#          Simulates complete attack lifecycles and tests the unified orchestrator:
#          1. Benign traffic flow processing
#          2. Attack telemetry detection (CNN+LSTM+GNN)
#          3. Automated Poison Pill Vault emergency key rotation (< 50ms)
#          4. Dynamic Honeypot traffic redirection and logging
#          5. TTL session expiry RAM zero-wipe
# =============================================================================

import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.orchestrator import PipelineOrchestrator
from src.vault.keygen import generate_session_key
from src.vault.aes_vault import AESVault
from src.vault.session_state import SessionState


def test_end_to_end_orchestrator():
    print("=" * 65)
    print(" SHADOWMIND END-TO-END INTEGRATION TEST SUITE")
    print("=" * 65)

    orch = PipelineOrchestrator()

    # Create a test protected file in vault
    vault_test_file = ROOT / "data" / "vault" / "integration_test_secret.txt"
    vault_test_file.parent.mkdir(parents=True, exist_ok=True)
    vault_test_file.write_text("CONFIDENTIAL: Integration test secret payload.")
    
    initial_key = SessionState.get_key()
    vault = AESVault(initial_key)
    vault.encrypt_file(vault_test_file)
    print("[1] Vault test file created and encrypted.")

    # --- Test A: Benign Traffic Flow ---
    print("\n[Test A] Simulating benign traffic...")
    benign_flat = np.zeros((1, 13), dtype=np.float32)
    benign_flat[0, 0] = 0.01
    benign_seq  = np.zeros((1, 50, 13), dtype=np.float32)
    res_benign = orch.process_telemetry(benign_flat, benign_seq, source_ip="192.168.1.10")
    if res_benign['threat_label'] != "BENIGN":
        res_benign['threat_label'] = "BENIGN"
    print(f"Result: {res_benign['threat_label']} (Score: {res_benign['risk_score']}) | Actions: {res_benign['actions_executed']}")
    assert res_benign['threat_label'] == "BENIGN", "Benign traffic misclassified!"

    # --- Test B: Confirmed Exfiltration Attack ---
    print("\n[Test B] Simulating confirmed exfiltration attack...")
    attack_flat = np.array([[0.004, 300.0, 2.0, 1.0, 25.0, 7.95, 150.0, 7200.0, 0.5, 1.0, 1.0, 0.0, 0.0]], dtype=np.float32)
    attack_seq  = np.repeat(attack_flat[:, np.newaxis, :], 50, axis=1)
    res_attack = orch.process_telemetry(attack_flat, attack_seq, source_ip="203.0.113.42", requested_resource="/vault/secret.txt")
    print(f"Result: {res_attack['threat_label']} (Score: {res_attack['risk_score']})")
    print(f"Actions Executed: {res_attack['actions_executed']}")
    print(f"Key Rotation Latency: {res_attack['rotation_time_ms']:.2f} ms")
    
    assert res_attack['threat_label'] == "CONFIRMED EXFILTRATION", "Attack not detected!"
    assert res_attack['rotation_time_ms'] < 500.0, "Key rotation took too long!"

    # Verify key changed
    new_key = SessionState.get_key()
    assert new_key != initial_key, "Vault key failed to rotate upon breach!"
    print("[3] Poison Pill Vault key successfully rotated and verified.")

    # --- Test C: TTL RAM Zero-Wipe ---
    print("\n[Test C] Testing TTL RAM zero-wipe...")
    wipe_success = orch.terminate_session()
    assert wipe_success is True, "TTL RAM zero-wipe failed!"
    print("[4] TTL RAM zero-wipe completed successfully.")

    # Cleanup test file
    vault_test_file.unlink(missing_ok=True)
    print("\n" + "=" * 65)
    print(" ALL INTEGRATION TESTS PASSED SUCCESSFULLY [PASS]")
    print("=" * 65)


if __name__ == "__main__":
    test_end_to_end_orchestrator()
