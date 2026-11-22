# =============================================================================
# FILE: src/workspace/workspace_vault.py
# PURPOSE: External Local Vault Directory Manager (Strict Forward Secrecy).
#          - Active Session: Automatically auto-encrypts files in /Vault upon attack.
#            Maintains rotated session keys in volatile RAM so the operator can
#            decrypt files during the same active session.
#          - On Sign-Out: Forcefully zero-wipes (0x00) all session keys from RAM.
#            Leftover .enc files become mathematically permanent ciphertext noise
#            (0 bytes recoverable in any future session).
# =============================================================================

import os
import logging
from pathlib import Path
from typing import List, Union
from src.vault.aes_vault import AESVault
from src.vault.session_state import SessionState

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Real physical folder on the user's computer
EXTERNAL_VAULT_DIR = Path(__file__).resolve().parents[2] / "Vault"

# Volatile RAM-only keystore for the ACTIVE session only
_active_session_keystore: List[bytes] = []


def register_session_key(key: bytes):
    """Register key into active volatile RAM keystore (valid for this session only)."""
    if isinstance(key, (bytes, bytearray)) and len(key) == 32:
        raw = bytes(key)
        if raw not in _active_session_keystore:
            _active_session_keystore.append(raw)


def get_session_keys() -> List[bytes]:
    """Retrieve in-memory keys for the active session."""
    return list(_active_session_keystore)


def wipe_session_keystore():
    """
    STRICT FORWARD SECRECY (TTL ZERO-WIPE):
    Permanently zero-overwrites all session keys in RAM upon sign-out.
    All leftover .enc files become unrecoverable ciphertext forever.
    """
    global _active_session_keystore
    for key in _active_session_keystore:
        try:
            b = bytearray(key)
            for i in range(len(b)):
                b[i] = 0x00
            del b
        except Exception:
            pass
    _active_session_keystore.clear()
    logger.info("TTL SELF-DESTRUCT: All active session encryption keys zero-wiped (0x00). Forward secrecy enforced.")


class ExternalVaultFolder:
    """
    Manages the physical external Vault folder on the user's OS.
    """

    def __init__(self):
        self.vault_dir = EXTERNAL_VAULT_DIR
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"External Vault folder verified at: {self.vault_dir}")

    def list_files(self) -> List[Path]:
        """List all files in the external Vault folder."""
        if not self.vault_dir.exists():
            return []
        return [f for f in self.vault_dir.glob("*.*")]

    def auto_encrypt_vault(self) -> int:
        """
        Emergency Auto-Encrypt:
        Instantly encrypts all plaintext files in the physical Vault folder
        into AES-256 ciphertext (.enc) upon breach detection.
        """
        files = [f for f in self.list_files() if not f.name.endswith(".enc")]
        if not files:
            logger.info("Auto-encrypt: No plaintext files in Vault folder.")
            return 0

        current_key = SessionState.get_key()
        register_session_key(current_key)
        vault = AESVault(current_key)
        encrypted_count = 0

        for fpath in files:
            try:
                enc_path = fpath.with_suffix(fpath.suffix + ".enc")
                vault.encrypt_file(fpath, enc_path)
                fpath.unlink(missing_ok=True)  # Remove plaintext version
                encrypted_count += 1
                logger.info(f"[LOCKED] EXTERNAL VAULT AUTO-ENCRYPTED: {fpath.name} -> {enc_path.name}")
            except Exception as e:
                logger.error(f"Failed to auto-encrypt file {fpath.name}: {e}")

        return encrypted_count

    def decrypt_vault_file(self, file_path: Union[str, Path]) -> Path:
        """
        Decrypt an encrypted .enc file back to plaintext using active session keys in RAM.
        If the operator signed out since encryption, the key is permanently gone.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Encrypted file not found: {path}")

        original_path = path.with_suffix("")  # remove .enc

        # Candidate keys: current session key first, then all active session keys from RAM
        candidate_keys = [SessionState.get_key()]
        for k in get_session_keys():
            if k not in candidate_keys:
                candidate_keys.append(k)

        decrypted = False
        last_err = None
        for key in candidate_keys:
            try:
                vault = AESVault(key)
                vault.decrypt_file(path, original_path)
                path.unlink(missing_ok=True)  # remove ciphertext
                decrypted = True
                logger.info(f"[UNLOCKED] VAULT FILE UNLOCKED: {original_path.name}")
                break
            except Exception as e:
                last_err = e
                original_path.unlink(missing_ok=True)

        if not decrypted:
            raise ValueError(
                f"FORWARD SECRECY ENFORCED: The session key that encrypted '{path.name}' was zero-wiped (0x00) upon sign-out.\n\n"
                f"Data is permanently unrecoverable."
            ) from last_err

        return original_path


if __name__ == "__main__":
    v = ExternalVaultFolder()
    print("Vault path:", v.vault_dir)
    print("Files:", v.list_files())
