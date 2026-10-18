# =============================================================================
# FILE: src/vault/session_state.py
# PURPOSE: Global shared session state for ShadowMind. Stores the active
#          AES-256 session key in RAM so background network listeners (Phase 2)
#          and UI tabs (Phase 3) can access and rotate it synchronously.
# =============================================================================

from src.vault.keygen import generate_session_key

class SessionState:
    _active_key = generate_session_key(256)

    @classmethod
    def get_key(cls) -> bytes:
        return cls._active_key

    @classmethod
    def set_key(cls, new_key: bytes):
        cls._active_key = new_key

    @classmethod
    def reset(cls):
        cls._active_key = generate_session_key(256)
