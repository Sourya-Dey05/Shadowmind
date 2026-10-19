# =============================================================================
# FILE: src/workspace/workspace_vault.py
# PURPOSE: Active Workspace Folder Manager.
#          Monitors a local storage directory where users create and edit files
#          normally in plaintext. Upon breach detection, automatically auto-encrypts
#          the contents of that entire folder in place.
# =============================================================================

import os
import logging
from pathlib import Path
from typing import List, Union
from src.vault.aes_vault import AESVault
from src.vault.session_state import SessionState

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

LOCAL_STORAGE_DIR = Path(__file__).resolve().parents[2] / "data" / "local_storage"


class LocalStorageVault:
    """
    Manages local storage folder where users work in plaintext,
    with automated emergency encryption upon breach detection.
    """

    def __init__(self):
        self.storage_dir = LOCAL_STORAGE_DIR
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def list_files(self) -> List[Path]:
        """List all files in local storage."""
        return [f for f in self.storage_dir.glob("*.*") if not f.name.endswith(".enc")]

    def list_workspace_files(self) -> List[Path]:
        """Alias for compatibility with vault tab."""
        return self.list_files()

    def save_file(self, filename: str, content: str) -> Path:
        """Create or edit a file in local storage in plaintext."""
        path = self.storage_dir / filename
        path.write_text(content, encoding="utf-8")
        logger.info(f"Local storage file saved: {filename}")
        return path

    def delete_file(self, filename: str) -> bool:
        """Delete a file from local storage."""
        path = self.storage_dir / filename
        if path.exists():
            path.unlink()
            logger.info(f"Local storage file deleted: {filename}")
            return True
        return False

    def auto_encrypt_storage(self) -> int:
        """
        Emergency Auto-Encrypt:
        Instantly encrypts all plaintext files in local storage into AES-256
        ciphertext upon breach detection.
        """
        files = self.list_files()
        if not files:
            logger.info("Auto-encrypt: No plaintext files in local storage.")
            return 0

        vault = AESVault(SessionState.get_key())
        encrypted_count = 0

        for fpath in files:
            try:
                # Encrypt in place or with .enc extension
                enc_path = fpath.with_suffix(fpath.suffix + ".enc")
                vault.encrypt_file(fpath, enc_path)
                fpath.unlink(missing_ok=True)  # Remove plaintext version
                encrypted_count += 1
                logger.info(f"🔒 LOCAL STORAGE AUTO-ENCRYPTED: {fpath.name}")
            except Exception as e:
                logger.error(f"Failed to auto-encrypt local file {fpath.name}: {e}")

        return encrypted_count


if __name__ == "__main__":
    store = LocalStorageVault()
    p = store.save_file("report.txt", "Quarterly earnings report.")
    print("Saved:", p)
    print("Files:", store.list_files())
    enc_count = store.auto_encrypt_storage()
    print("Encrypted count:", enc_count)
