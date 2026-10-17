# =============================================================================
# FILE: src/data/preprocessor.py
# PURPOSE: Reads the raw synthetic (or real) traffic CSV produced by
#          generator.py and transforms it into normalized feature tensors
#          ready for the CNN, LSTM, and MLP models in Phase 1.
#          Handles: IP encoding, feature scaling (MinMax), sequence building
#          for LSTM, train/test splitting, and input validation/sanitization
#          to prevent garbage data from reaching the models.
# =============================================================================

import logging
import re
import numpy as np
import pandas as pd
import yaml
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

# --- Logging setup ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# --- Config ---
CONFIG_PATH = Path(__file__).resolve().parents[2] / "configs" / "thresholds.yaml"

def _load_config() -> dict:
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)

# ---------------------------------------------------------------------------
# Feature columns used by the models (order matters for CNN/LSTM input shape)
# ---------------------------------------------------------------------------
FEATURE_COLS = [
    "packet_size_kb",
    "interval_sec",
    "hour",
    "is_off_hours",
    "port_fan_out",
    "entropy",
    "outbound_mb",
    "session_duration_sec",
    "dst_port_norm",   # normalized port number
    "is_external_dst", # derived: 1 if dst is external IP, 0 if internal
    "protocol_tcp",    # one-hot
    "protocol_udp",
    "protocol_icmp",
]

LABEL_COL = "label"

# ---------------------------------------------------------------------------
# Input sanitization
# ---------------------------------------------------------------------------

_IP_RE = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")

def _sanitize_ip(ip: str) -> bool:
    """Return True if ip is a plausible IPv4 string."""
    if not isinstance(ip, str):
        return False
    return bool(_IP_RE.match(ip.strip()))

def _is_external(ip: str) -> int:
    """Return 1 if the IP is outside RFC-1918 ranges, else 0."""
    if not _sanitize_ip(ip):
        return 0
    parts = ip.strip().split(".")
    first, second = int(parts[0]), int(parts[1])
    if first == 10:
        return 0
    if first == 172 and 16 <= second <= 31:
        return 0
    if first == 192 and second == 168:
        return 0
    return 1

def sanitize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate and clean raw traffic DataFrame.
    - Drop rows with missing required columns
    - Clamp numeric values to sane ranges
    - Remove rows with invalid IPs
    - Reject non-numeric labels
    """
    required = {"src_ip", "dst_ip", "packet_size_kb", "interval_sec",
                 "hour", "dst_port", "entropy", "label"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"DataFrame missing required columns: {missing}")

    original_len = len(df)

    # Drop rows with null values in required columns
    df = df.dropna(subset=list(required))

    # Clamp ranges — prevent poisoned/corrupt data from skewing models
    df["packet_size_kb"]       = df["packet_size_kb"].clip(lower=0.0, upper=1_000_000.0)
    df["interval_sec"]         = df["interval_sec"].clip(lower=0.0, upper=86400.0)
    df["hour"]                 = df["hour"].clip(lower=0, upper=23).astype(int)
    df["dst_port"]             = df["dst_port"].clip(lower=1, upper=65535).astype(int)
    df["entropy"]              = df["entropy"].clip(lower=0.0, upper=8.0)
    df["outbound_mb"]          = df["outbound_mb"].clip(lower=0.0, upper=1_000_000.0)
    df["session_duration_sec"] = df["session_duration_sec"].clip(lower=0, upper=604800)
    df["port_fan_out"]         = df["port_fan_out"].clip(lower=1, upper=65535).astype(int)

    # Validate IP columns
    valid_src = df["src_ip"].apply(_sanitize_ip)
    valid_dst = df["dst_ip"].apply(_sanitize_ip)
    df = df[valid_src & valid_dst]

    # Label must be 0 or 1
    df = df[df["label"].isin([0, 1])]

    dropped = original_len - len(df)
    if dropped > 0:
        logger.warning(f"Sanitization dropped {dropped} invalid rows")

    return df.reset_index(drop=True)

# ---------------------------------------------------------------------------
# Feature engineering
# ---------------------------------------------------------------------------

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Derive additional features and encode categoricals.
    Modifies df in place and returns it.
    """
    # Derived: is the destination an external (internet) IP?
    df["is_external_dst"] = df["dst_ip"].apply(_is_external)

    # Normalize port to [0, 1]
    df["dst_port_norm"] = df["dst_port"] / 65535.0

    # One-hot encode protocol
    protocol_upper = df["protocol"].str.upper().fillna("TCP")
    df["protocol_tcp"]  = (protocol_upper == "TCP").astype(int)
    df["protocol_udp"]  = (protocol_upper == "UDP").astype(int)
    df["protocol_icmp"] = (protocol_upper == "ICMP").astype(int)

    return df

# ---------------------------------------------------------------------------
# Scaling
# ---------------------------------------------------------------------------

def scale_features(X_train: np.ndarray, X_test: np.ndarray):
    """
    Fit MinMaxScaler on training data only, then transform both splits.
    Returns (X_train_scaled, X_test_scaled, fitted_scaler).
    Fitting only on train prevents data leakage.
    """
    scaler = MinMaxScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled  = scaler.transform(X_test)
    return X_train_scaled, X_test_scaled, scaler

# ---------------------------------------------------------------------------
# LSTM sequence builder
# ---------------------------------------------------------------------------

def build_sequences(X: np.ndarray, y: np.ndarray, seq_len: int):
    """
    Reshape flat feature rows into overlapping time sequences for LSTM.
    Input:  X shape (N, F), y shape (N,)
    Output: X_seq shape (N - seq_len, seq_len, F), y_seq shape (N - seq_len,)
    """
    X_seq, y_seq = [], []
    for i in range(len(X) - seq_len):
        X_seq.append(X[i : i + seq_len])
        y_seq.append(y[i + seq_len])
    return np.array(X_seq), np.array(y_seq)

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_and_prepare(csv_path: str = None, test_size: float = 0.2):
    """
    Full pipeline: load CSV → sanitize → engineer features → scale → split.

    Returns dict with keys:
        X_train, X_test, y_train, y_test          — flat arrays for CNN/MLP
        X_train_seq, X_test_seq, y_train_seq, y_test_seq  — sequences for LSTM
        scaler                                     — fitted MinMaxScaler
        feature_cols                               — list of feature column names
    """
    cfg = _load_config()
    path = csv_path or cfg["data"]["output_path"]
    seq_len = cfg["detection"]["lstm"]["sequence_length"]

    logger.info(f"Loading dataset from {path}")
    df = pd.read_csv(path)

    df = sanitize_dataframe(df)
    df = engineer_features(df)

    X = df[FEATURE_COLS].values.astype(np.float32)
    y = df[LABEL_COL].values.astype(np.int64)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42, stratify=y
    )

    X_train_sc, X_test_sc, scaler = scale_features(X_train, X_test)

    X_train_seq, y_train_seq = build_sequences(X_train_sc, y_train, seq_len)
    X_test_seq,  y_test_seq  = build_sequences(X_test_sc,  y_test,  seq_len)

    logger.info(
        f"Prepared — train: {len(X_train_sc)}, test: {len(X_test_sc)}, "
        f"LSTM sequences train: {len(X_train_seq)}, test: {len(X_test_seq)}"
    )

    return {
        "X_train":      X_train_sc,
        "X_test":       X_test_sc,
        "y_train":      y_train,
        "y_test":       y_test,
        "X_train_seq":  X_train_seq,
        "X_test_seq":   X_test_seq,
        "y_train_seq":  y_train_seq,
        "y_test_seq":   y_test_seq,
        "scaler":       scaler,
        "feature_cols": FEATURE_COLS,
    }


if __name__ == "__main__":
    data = load_and_prepare()
    print("X_train shape:", data["X_train"].shape)
    print("X_train_seq shape:", data["X_train_seq"].shape)
    print("y_train distribution:", np.bincount(data["y_train"]))
