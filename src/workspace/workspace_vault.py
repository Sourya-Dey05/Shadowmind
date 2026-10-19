# =============================================================================
# FILE: src/workspace/workspace_vault.py
# PURPOSE: External Local Vault Directory Manager.
#          Automatically creates a real physical folder named "Vault" on the user's
#          computer (e.g. D:\Shadowmind\Vault or Desktop). Users can create, edit,
#          and manage normal files in Windows plaintext freely. Upon attack
#          detection, ShadowMind instantly auto-encrypts all files in that Vault
#          folder into AES-256 ciphertext in place.
# =============================================================================

import os
import logging
from pathlib import Path
from typing import List
from src.vault.aes_vault import AESVault
from src.vault.session_state import SessionState

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Real physical folder on the user's computer
EXTERNAL_VAULT_DIR = Path(__file__).resolve().parents[2] / "Vault"


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

        vault = AESVault(SessionState.get_key())
        encrypted_count = 0

        for fpath in files:
            try:
                enc_path = fpath.with_suffix(fpath.suffix + ".enc")
                vault.encrypt_file(fpath, enc_path)
                fpath.unlink(missing_ok=True)  # Remove plaintext version
                encrypted_count += 1
                logger.info(f"🔒 EXTERNAL VAULT AUTO-ENCRYPTED: {fpath.name} ➔ {enc_path.name}")
            except Exception as e:
                logger.error(f"Failed to auto-encrypt file {fpath.name}: {e}")

        return encrypted_count

    def decrypt_vault_file(self, file_path: Union[str, Path]) -> Path:
        """Decrypt an encrypted .enc file back to plaintext."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Encrypted file not found: {path}")
        
        vault = AESVault(SessionState.get_key())
        original_path = path.with_suffix("") # remove .enc
        vault.decrypt_file(path, original_path)
        path.unlink(missing_ok=True) # remove ciphertext
        logger.info(f"🔓 VAULT FILE UNLOCKED: {original_path.name}")
        return original_path


if __name__ == "__main__":
    v = ExternalVaultFolder()
    print("Vault path:", v.vault_dir)
    print("Files:", v.list_files())
