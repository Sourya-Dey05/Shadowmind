# =============================================================================
# FILE: src/vault/keygen.py
# PURPOSE: Generates cryptographically secure per-session AES-256 keys.
#          Utilizes Python's `secrets` module (cryptographically strong random
#          number generator) to produce unique 256-bit keys per login session.
#          Keys are held exclusively in RAM and are never written to persistent disk.
# =============================================================================

import secrets
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def generate_session_key(key_bits: int = 256) -> bytes:
    """
    Generate a cryptographically secure random session key of specified bit length.
    Default is 256 bits (32 bytes) for AES-256.
    """
    byte_length = key_bits // 8
    key = secrets.token_bytes(byte_length)
    logger.info(f"Generated new secure AES-{key_bits} session key in RAM.")
    return key


if __name__ == "__main__":
    k = generate_session_key(256)
    print(f"Generated key (hex): {k.hex()}")
    print(f"Key length: {len(k)} bytes")
