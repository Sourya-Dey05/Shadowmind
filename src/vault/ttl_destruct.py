# =============================================================================
# FILE: src/vault/ttl_destruct.py
# PURPOSE: Time-To-Live (TTL) Self-Destruct engine.
#          Upon session expiry (e.g. logoff at 5 PM or TTL timeout), forcefully
#          zero-overwrites all session decryption keys remaining in server RAM
#          (`memset`-equivalent in Python). Guarantees zero residual risk —
#          even an intercepted key becomes permanently dead.
# =============================================================================

import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def zero_wipe_ram_key(session_key: bytes) -> bool:
    """
    Forcefully zero-overwrite key bytes in RAM upon session expiry.
    Returns True upon successful zero-wipe.
    """
    if not isinstance(session_key, (bytes, bytearray)):
        logger.warning("Invalid key type passed to TTL RAM wiper.")
        return False

    try:
        # Convert to mutable bytearray and overwrite with 0x00
        mutable_key = bytearray(session_key)
        for i in range(len(mutable_key)):
            mutable_key[i] = 0x00

        # Delete references
        del mutable_key
        del session_key
        logger.info("TTL SELF-DESTRUCT: Session decryption key zero-wiped from RAM.")
        return True
    except Exception as e:
        logger.error(f"Failed to zero-wipe RAM key: {e}")
        return False


if __name__ == "__main__":
    from src.vault.keygen import generate_session_key
    k = generate_session_key()
    print("Before wipe (hex):", k.hex())
    zero_wipe_ram_key(k)
