# =============================================================================
# FILE: src/vault/aes_vault.py
# PURPOSE: AES-256 encryption and decryption engine for protected files.
#          Uses Fernet (AES-128/256 CBC with HMAC authentication) from the
#          `cryptography` library to encrypt sensitive documents and vault files
#          using the active session key. Ensures unauthorized file reads fail.
# =============================================================================

import os
import logging
from pathlib import Path
from cryptography.fernet import Fernet
import base64

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def _key_to_fernet_token(raw_key: bytes) -> bytes:
    """Convert raw 32-byte key into a URL-safe base64-encoded 32-byte Fernet key."""
    # Ensure exactly 32 bytes
    if len(raw_key) != 32:
        raw_key = raw_key.ljust(32, b'\0')[:32]
    return base64.urlsafe_b64encode(raw_key)


class AESVault:
    """
    Manages AES-256 file encryption and decryption for protected vault items.
    """

    def __init__(self, session_key: bytes):
        self.fernet_key = _key_to_fernet_token(session_key)
        self.cipher = Fernet(self.fernet_key)

    def encrypt_file(self, file_path: Union[str, Path], output_path: Union[str, Path] = None) -> Path:
        """
        Encrypt a file using AES-256 session key.
        Overwrites original file or writes to output_path.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found for encryption: {path}")

        with open(path, "rb") as f:
            plaintext = f.read()

        ciphertext = self.cipher.encrypt(plaintext)

        out = Path(output_path) if output_path else path
        with open(out, "wb") as f:
            f.write(ciphertext)

        logger.info(f"File encrypted successfully: {path.name}")
        return out

    def decrypt_file(self, file_path: Union[str, Path], output_path: Union[str, Path] = None) -> Path:
        """
        Decrypt an encrypted vault file back to plaintext using session key.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Encrypted file not found: {path}")

        with open(path, "rb") as f:
            ciphertext = f.read()

        try:
            plaintext = self.cipher.decrypt(ciphertext)
        except Exception as e:
            logger.error(f"Decryption failed — invalid key or corrupted file: {path.name}")
            raise ValueError("Decryption failed: incorrect session key or poisoned vault file.") from e

        out = Path(output_path) if output_path else path
        with open(out, "wb") as f:
            f.write(plaintext)

        logger.info(f"File decrypted successfully: {path.name}")
        return out


if __name__ == "__main__":
    from src.vault.keygen import generate_session_key
    key = generate_session_key()
    vault = AESVault(key)
    
    test_file = Path("D:/Shadowmind/data/test_vault.txt")
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text("Secret enterprise intel data.")

    vault.encrypt_file(test_file)
    print("Encrypted test file.")
    try:
        vault.decrypt_file(test_file)
        print("Decrypted successfully:", test_file.read_text())
    except Exception as e:
        print("Failed:", e)
    
    test_file.unlink(missing_ok=True)
