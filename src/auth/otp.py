# =============================================================================
# FILE: src/auth/otp.py
# PURPOSE: Simulated Secure OTP (One-Time Password) Generator & Verifier.
#          Generates a cryptographically secure 6-digit code for offline
#          two-factor authentication (2FA) during operator login.
#          Prints the OTP to the local secure console (or simulates dispatch)
#          so offline environments can demonstrate 2FA without external SMS APIs.
# =============================================================================

import secrets
import logging
import time

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class OTPManager:
    _active_otp = None
    _expires_at = 0.0

    @classmethod
    def generate_otp(cls) -> str:
        """Generate a secure 6-digit OTP valid for 3 minutes."""
        code = f"{secrets.randbelow(900000) + 100000}"
        cls._active_otp = code
        cls._expires_at = time.time() + 180  # 3 minutes validity
        logger.info(f"[SECURE 2FA] Generated OTP Code: {code} (Valid for 3 mins)")
        print(f"\n==================================================")
        print(f" [SHADOWMIND SECURE 2FA] LOGIN OTP CODE: {code}")
        print(f"==================================================\n")
        return code

    @classmethod
    def verify_otp(cls, entered_code: str) -> bool:
        """Verify entered OTP against active code and check expiration."""
        if not cls._active_otp:
            return False
        if time.time() > cls._expires_at:
            logger.warning("OTP verification failed: Code expired.")
            cls._active_otp = None
            return False
        
        if entered_code.strip() == cls._active_otp:
            logger.info("OTP verification successful.")
            cls._active_otp = None  # One-time use
            return True
        
        logger.warning("OTP verification failed: Incorrect code.")
        return False
