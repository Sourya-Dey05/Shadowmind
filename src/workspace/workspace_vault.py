# =============================================================================
# FILE: src/workspace/workspace_vault.py
# PURPOSE: Active Workspace Vault Manager.
#          Provides a plaintext working directory where users can create, edit,
#          modify, and delete files freely with zero encryption friction.
#          Upon breach detection (AI engine / network attack), automatically
#          locks down and encrypts all workspace files into ciphertext in milliseconds.
# =============================================================================

import os
import logging
from pathlib import Path
from typing import List, Union
from src.vault.aes_vault import AESVault
from src.vault.session_state import SessionState

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

WORKSPACE_DIR = Path(__file__).resolve().parents[2] / "data" / "workspace"
LOCKED_DIR    = Path(__file__).resolve().parents[2] / "data" / "vault"


class ActiveWorkspaceVault:
    """
    Manages active plaintext workspace files and emergency auto-lockdown.
    """

    def __init__(self):
        self.workspace_dir = WORKSPACE_DIR
        self.locked_dir = LOCKED_DIR
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        self.locked_dir.mkdir(parents=True, exist_ok=True)

    def list_workspace_files(self) -> List[Path]:
        """List all active plaintext files in the workspace."""
        return [f for f in self.workspace_dir.glob("*.*") if not f.name.endswith(".enc")]

    def create_or_edit_file(self, filename: str, content: str) -> Path:
        """Create or edit a plaintext file in the active workspace."""
        path = self.workspace_dir / filename
        path.write_text(content, encoding="utf-8")
        logger.info(f"Workspace file created/edited: {filename}")
        return path

    def read_file(self, filename: str) -> str:
        """Read a plaintext workspace file."""
        path = self.workspace_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"File not found in workspace: {filename}")
        return path.read_text(encoding="utf-8")

    def delete_file(self, filename: str) -> bool:
        """Delete a workspace file."""
        path = self.workspace_dir / filename
        if path.exists():
            path.unlink()
            logger.info(f"Workspace file deleted: {filename}")
            return True
        return False

    def auto_lockdown(self) -> int:
        """
        Emergency Auto-Lockdown:
        Instantly encrypts all plaintext files in the active workspace into
        AES-256 ciphertext upon breach detection.
        """
        files = self.list_workspace_files()
        if not files:
            logger.info("Auto-lockdown: No active plaintext files in workspace.")
            return 0

        vault = AESVault(SessionState.get_key())
        locked_count = 0

        for fpath in files:
            try:
                # Encrypt into locked vault directory with .enc extension
                enc_path = self.locked_dir / (fpath.name + ".enc")
                vault.encrypt_file(fpath, enc_path)
                # Remove plaintext version from active workspace
                fpath.unlink(missing_ok=True)
                locked_count += 1
                logger.info(f"🔒 WORKSPACE AUTO-LOCKED: {fpath.name} ➔ {enc_path.name}")
            except Exception as e:
                logger.error(f"Failed to auto-lock workspace file {fpath.name}: {e}")

        return locked_count


if __name__ == "__main__":
    ws = ActiveWorkspaceVault()
    p = ws.create_or_edit_file("test_note.txt", "Confidential meeting notes.")
    print("Created:", p)
    print("Files:", ws.list_workspace_files())
    locked = ws.auto_lockdown()
    print("Locked count:", locked)
