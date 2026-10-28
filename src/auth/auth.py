# =============================================================================
# FILE: src/auth/auth.py
# PURPOSE: Handles all authentication and authorization for the ShadowMind
#          desktop app. Responsibilities:
#          - Secure password hashing with bcrypt (never stores plaintext)
#          - Login attempt tracking with account lockout after N failures
#          - Role-based access control (USER vs ADMIN)
#          - Session token generation and validation
#          - Input sanitization on all auth inputs to prevent injection
#          This is the security gatekeeper — every other module checks here
#          before granting access.
# =============================================================================

import os
import re
import time
import hmac
import hashlib
import logging
import sqlite3
import secrets
import yaml
from pathlib import Path
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional

import bcrypt

# --- Logging (no sensitive data in logs) ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# --- Config ---
CONFIG_PATH = Path(__file__).resolve().parents[2] / "configs" / "thresholds.yaml"
DB_PATH     = Path(__file__).resolve().parents[2] / "data" / "shadowmind_auth.db"

def _load_config() -> dict:
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)

# ---------------------------------------------------------------------------
# Roles
# ---------------------------------------------------------------------------

class Role(str, Enum):
    USER  = "user"
    ADMIN = "admin"

# ---------------------------------------------------------------------------
# Session (in-memory, never persisted to disk)
# ---------------------------------------------------------------------------

@dataclass
class Session:
    username: str
    role: Role
    token: str
    created_at: float = field(default_factory=time.time)
    ttl_seconds: int  = 28800  # overridden from config on creation

    def is_valid(self) -> bool:
        return (time.time() - self.created_at) < self.ttl_seconds

# ---------------------------------------------------------------------------
# Input sanitization
# ---------------------------------------------------------------------------

_EMAIL_RE = re.compile(r"^[\w\.\-_]+@([\w\-_]+\.)+[\w\-]{2,4}$")

def sanitize_email(email: str) -> str:
    """Validate email address format."""
    if not isinstance(email, str):
        raise ValueError("Email must be a string")
    email = email.strip().lower()
    if not _EMAIL_RE.match(email):
        raise ValueError("Invalid email format")
    return email

def sanitize_password(password: str) -> str:
    """
    Validate password is a non-empty string within bcrypt's 72-byte limit.
    Does NOT log or return the password.
    """
    if not isinstance(password, str):
        raise ValueError("Password must be a string")
    if len(password) < 1:
        raise ValueError("Password cannot be empty")
    if len(password) > 72:
        raise ValueError("Password exceeds maximum length")
    return password

# ---------------------------------------------------------------------------
# Database helpers (SQLite with restricted permissions)
# ---------------------------------------------------------------------------

def _get_db() -> sqlite3.Connection:
    """
    Open the auth SQLite database.
    File permissions are set to owner-only (600) on creation.
    """
    db_dir = DB_PATH.parent
    db_dir.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))

    # Restrict file permissions to owner only (Unix); no-op on Windows
    try:
        os.chmod(str(DB_PATH), 0o600)
    except Exception:
        pass

    conn.execute("PRAGMA journal_mode=WAL")   # safer concurrent writes
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def _init_db() -> None:
    """Create the users table if it does not exist."""
    with _get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                username        TEXT    NOT NULL UNIQUE,
                password_hash   TEXT    NOT NULL,
                role            TEXT    NOT NULL DEFAULT 'user',
                failed_attempts INTEGER NOT NULL DEFAULT 0,
                locked_until    REAL    NOT NULL DEFAULT 0.0,
                created_at      REAL    NOT NULL
            )
        """)
        conn.commit()
    logger.info("Auth DB initialized")

# ---------------------------------------------------------------------------
# Core auth functions
# ---------------------------------------------------------------------------

def hash_password(password: str) -> str:
    """
    Hash a plaintext password with bcrypt.
    Cost factor is read from config (default 12 ≈ 300 ms — safe against brute force).
    Returns the hashed string (safe to store in DB).
    """
    cfg = _load_config()
    rounds = cfg["auth"]["bcrypt_rounds"]
    pw_bytes = sanitize_password(password).encode("utf-8")
    hashed = bcrypt.hashpw(pw_bytes, bcrypt.gensalt(rounds=rounds))
    return hashed.decode("utf-8")

def verify_password(password: str, password_hash: str) -> bool:
    """
    Constant-time bcrypt verification.
    Returns True if password matches the stored hash.
    """
    try:
        pw_bytes   = password.encode("utf-8")
        hash_bytes = password_hash.encode("utf-8")
        return bcrypt.checkpw(pw_bytes, hash_bytes)
    except Exception:
        return False

def register_user(email: str, password: str, role: Role = Role.USER) -> bool:
    """
    Register a new user by email. Returns True on success, False if email taken.
    """
    _init_db()
    cfg = _load_config()
    min_len = cfg["auth"]["min_password_length"]

    email = sanitize_email(email)
    password = sanitize_password(password)

    if len(password) < min_len:
        raise ValueError(f"Password must be at least {min_len} characters")

    pw_hash = hash_password(password)

    try:
        with _get_db() as conn:
            conn.execute(
                "INSERT INTO users (username, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
                (email, pw_hash, role.value, time.time())
            )
            conn.commit()
        logger.info(f"User registered: {email} [{role.value}]")
        return True
    except sqlite3.IntegrityError:
        logger.warning(f"Registration failed — email already exists: {email}")
        return False

def login(email: str, password: str) -> Optional[Session]:
    """
    Authenticate a user via email. Returns a Session on success, None on failure.
    """
    _init_db()
    cfg = _load_config()
    max_attempts   = cfg["auth"]["max_login_attempts"]
    lockout_dur    = cfg["auth"]["lockout_duration_seconds"]
    session_ttl    = cfg["auth"]["session_ttl_seconds"]

    try:
        email = sanitize_email(email)
        password = sanitize_password(password)
    except ValueError as e:
        logger.warning(f"Login rejected — input validation failed: {e}")
        return None

    with _get_db() as conn:
        row = conn.execute(
            "SELECT password_hash, role, failed_attempts, locked_until FROM users WHERE username = ?",
            (email,)
        ).fetchone()

    if row is None:
        bcrypt.checkpw(b"dummy", bcrypt.hashpw(b"dummy", bcrypt.gensalt(4)))
        logger.warning(f"Login failed (unknown email): {email}")
        return None

    pw_hash, role_str, failed, locked_until = row

    if time.time() < locked_until:
        remaining = int(locked_until - time.time())
        logger.warning(f"Login blocked — account locked for {remaining}s: {email}")
        return None

    if not verify_password(password, pw_hash):
        new_failed = failed + 1
        new_locked = time.time() + lockout_dur if new_failed >= max_attempts else 0.0
        with _get_db() as conn:
            conn.execute(
                "UPDATE users SET failed_attempts = ?, locked_until = ? WHERE username = ?",
                (new_failed, new_locked, email)
            )
            conn.commit()
        return None

    with _get_db() as conn:
        conn.execute(
            "UPDATE users SET failed_attempts = 0, locked_until = 0.0 WHERE username = ?",
            (email,)
        )
        conn.commit()

    token = secrets.token_hex(32)
    session = Session(
        username=email,
        role=Role(role_str),
        token=token,
        created_at=time.time(),
        ttl_seconds=session_ttl,
    )
    logger.info(f"Login success: {email} [{role_str}]")
    return session

def require_role(session: Optional[Session], required: Role) -> bool:
    """
    Check that a session is valid and has the required role.
    Use this in every UI tab / action that should be role-restricted.

    Example:
        if not auth.require_role(session, Role.ADMIN):
            show_access_denied()
            return
    """
    if session is None or not session.is_valid():
        return False
    role_order = {Role.USER: 1, Role.ADMIN: 2}
    return role_order.get(session.role, 0) >= role_order.get(required, 99)

def logout(session: Optional[Session]) -> None:
    """
    Invalidate the session by clearing its token in memory.
    The caller is responsible for triggering TTL key wipe (vault) after this.
    """
    if session is not None:
        # Zero out the token string in memory (best-effort in Python)
        session.token = "0" * len(session.token)
        session.created_at = 0.0
    logger.info("Session logged out")


# ---------------------------------------------------------------------------
# Bootstrap: create default admin on first run
# ---------------------------------------------------------------------------

def bootstrap_admin(email: str = "souryanew@shadowmind.com", password: str = "Sourya@2026dey") -> None:
    """
    Create the default admin account with email authentication and Sourya@2026dey password.
    If database exists, ensures admin email is updated with the correct password hash.
    """
    _init_db()
    pw_hash = hash_password(password)
    with _get_db() as conn:
        row = conn.execute("SELECT id FROM users WHERE username = ?", (email,)).fetchone()
        if row is None:
            conn.execute(
                "INSERT INTO users (username, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
                (email, pw_hash, Role.ADMIN.value, time.time())
            )
            logger.info(f"Admin bootstrap created: {email}")
        else:
            conn.execute(
                "UPDATE users SET password_hash = ?, role = ? WHERE username = ?",
                (pw_hash, Role.ADMIN.value, email)
            )
            logger.info(f"Admin credentials updated: {email}")
        conn.commit()


if __name__ == "__main__":
    bootstrap_admin()
    s = login("admin", "wrongpassword")
    print("Bad password:", s)
