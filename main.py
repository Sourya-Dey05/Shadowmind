# =============================================================================
# FILE: main.py
# PURPOSE: Entry point for the ShadowMind desktop application. Performs
#          startup safety checks (Python version, required dependencies),
#          configures logging from thresholds.yaml, and launches the
#          CustomTkinter main window. Also generates the synthetic dataset
#          on first run if it doesn't exist yet (so the app is demo-ready
#          without a separate setup step).
# =============================================================================

import sys
import os
import logging
import logging.handlers
from pathlib import Path

# --- Enforce Python 3.10+ ---
if sys.version_info < (3, 10):
    print("ERROR: ShadowMind requires Python 3.10 or higher.")
    sys.exit(1)

# --- Project root on path ---
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

# ---------------------------------------------------------------------------
# Logging setup — must happen before any other import uses logging
# ---------------------------------------------------------------------------

def _setup_logging():
    """Configure logging from thresholds.yaml. Falls back to INFO on error."""
    try:
        import yaml
        cfg_path = ROOT / "configs" / "thresholds.yaml"
        with open(cfg_path, "r") as f:
            cfg = yaml.safe_load(f)
        log_cfg  = cfg.get("logging", {})
        level    = getattr(logging, log_cfg.get("level", "INFO"), logging.INFO)
        to_file  = log_cfg.get("log_to_file", False)
        log_path = ROOT / log_cfg.get("log_path", "logs/shadowmind.log")
    except Exception:
        level, to_file, log_path = logging.INFO, False, None

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.stream = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1, closefd=False)
    handlers = [stdout_handler]

    if to_file and log_path:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(
            logging.handlers.RotatingFileHandler(
                str(log_path), maxBytes=10 * 1024 * 1024, backupCount=3
            )
        )

    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
        handlers=handlers,
    )

_setup_logging()
logger = logging.getLogger("shadowmind.main")

# ---------------------------------------------------------------------------
# Dependency check
# ---------------------------------------------------------------------------

REQUIRED_PACKAGES = [
    ("customtkinter", "customtkinter"),
    ("bcrypt",        "bcrypt"),
    ("yaml",          "pyyaml"),
    ("pandas",        "pandas"),
    ("numpy",         "numpy"),
    # sklearn/scipy checked lazily (only needed by data pipeline, not UI startup)
]

def _check_dependencies():
    missing = []
    for import_name, pip_name in REQUIRED_PACKAGES:
        try:
            __import__(import_name)
        except ImportError:
            missing.append(pip_name)
    if missing:
        print("ERROR: Missing required packages. Install them with:")
        print(f"  pip install {' '.join(missing)}")
        sys.exit(1)
    # Warn (don't crash) if sklearn is broken — data pipeline unavailable
    try:
        import sklearn  # noqa: F401
    except Exception as e:
        logger.warning(f"scikit-learn unavailable (data pipeline disabled): {e}")

_check_dependencies()

# ---------------------------------------------------------------------------
# First-run: generate synthetic dataset if missing
# ---------------------------------------------------------------------------

def _ensure_dataset():
    try:
        import sklearn  # noqa: F401
    except Exception:
        logger.warning("scikit-learn unavailable — skipping dataset generation (UI will still launch)")
        return

    import yaml
    cfg_path = ROOT / "configs" / "thresholds.yaml"
    with open(cfg_path, "r") as f:
        cfg = yaml.safe_load(f)
    out_path = ROOT / cfg["data"]["output_path"]

    if not out_path.exists():
        logger.info("Synthetic dataset not found — generating on first run...")
        from src.data.generator import generate_dataset
        generate_dataset(str(out_path))
        logger.info(f"Dataset ready at {out_path}")
    else:
        logger.info(f"Dataset found at {out_path}")

def _ensure_decoys():
    try:
        from src.honeypot.decoy_manager import DecoyManager
        mgr = DecoyManager()
        mgr.deploy_decoys()
        logger.info("Dynamic honeypot decoys auto-deployed successfully.")
    except Exception as e:
        logger.warning(f"Failed to auto-deploy decoys: {e}")

# ---------------------------------------------------------------------------
# Launch
# ---------------------------------------------------------------------------

def main():
    logger.info("=" * 60)
    logger.info("ShadowMind — AI Defense System starting")
    logger.info("=" * 60)

    _ensure_dataset()
    _ensure_decoys()

    # Import UI only after dependency check passes
    from ui.main_window import ShadowMindApp

    app = ShadowMindApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    logger.info("UI launched")
    app.mainloop()
    logger.info("ShadowMind closed")


if __name__ == "__main__":
    main()
