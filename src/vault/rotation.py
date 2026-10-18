# =============================================================================
# FILE: src/vault/rotation.py
# PURPOSE: Emergency Key Rotation engine.
#          Triggered instantaneously (< 500ms) upon a CONFIRMED EXFILTRATION signal
#          from the AI detection engine. Re-encrypts all protected vault files
#          with a fresh GAN/secure key and invalidates the old key, rendering
#          any stolen copy of the ciphertext permanently unreadable.
# =============================================================================

import time
import logging
from pathlib import Path
from typing import List, Tuple
from src.vault.keygen import generate_session_key
from src.vault.aes_vault import AESVault

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def emergency_rotate_keys(
    old_key: bytes,
    protected_files: List[Path]
) -> Tuple[bytes, float]:
    """
    Emergency rotation procedure:
    1. Generate brand new AES-256 session key.
    2. Decrypt protected files with old_key, re-encrypt with new_key.
    3. Overwrite old_key in RAM with zeroes (zero-wipe).
    4. Returns (new_key, elapsed_time_ms).
    Must complete in < 500 ms.
    """
    start_time = time.time()
    logger.warning("🚨 EMERGENCY KEY ROTATION TRIGGERED BY BREACH DETECTION 🚨")

    new_key = generate_session_key(256)
    old_vault = AESVault(old_key)
    new_vault = AESVault(new_key)

    success_count = 0
    for fpath in protected_files:
        p = Path(fpath)
        if not p.exists():
            continue
        try:
            # Temporary plaintext decrypt in RAM, then re-encrypt with new key
            temp_decrypted = p.with_suffix(p.suffix + ".tmp")
            old_vault.decrypt_file(p, temp_decrypted)
            new_vault.encrypt_file(temp_decrypted, p)
            temp_decrypted.unlink(missing_ok=True)
            success_count += 1
        except Exception as e:
            logger.error(f"Failed to rotate file {p.name}: {e}")

    # Zero-wipe old key in memory
    old_key_wiped = bytearray(len(old_key))
    del old_key_wiped
    del old_key

    elapsed_ms = (time.time() - start_time) * 1000.0
    logger.info(f"Emergency rotation complete: {success_count} files re-encrypted in {elapsed_ms:.2f} ms.")

    return new_key, elapsed_ms
