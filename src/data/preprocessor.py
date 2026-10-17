# =============================================================================
# FILE: src/data/preprocessor.py
# PURPOSE: Reads and pre-processes CICIDS2017 raw CSV files from data/raw/CICIDS2017/
#          or falls back to the synthetic generator if raw files are absent.
#          Extracts flow features, normalizes them, builds LSTM time sequences,
#          and prepares training/test splits for the CNN+LSTM+MLP detection engine.
# =============================================================================

import logging
import re
import numpy as np
import pandas as pd
import yaml
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CONFIG_PATH = Path(__file__).resolve().parents[2] / "configs" / "thresholds.yaml"
RAW_CICIDS_DIR = Path(__file__).resolve().parents[2] / "data" / "raw" / "CICIDS2017"

def _load_config() -> dict:
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)

FEATURE_COLS = [
    "packet_size_kb",
    "interval_sec",
    "hour",
    "is_off_hours",
    "port_fan_out",
    "entropy",
    "outbound_mb",
    "session_duration_sec",
    "dst_port_norm",
    "is_external_dst",
    "protocol_tcp",
    "protocol_udp",
    "protocol_icmp",
]

LABEL_COL = "label"

def load_cicids_sample(sample_size_per_file: int = 3000) -> pd.DataFrame:
    """
    Load samples from CICIDS2017 CSV files and ensure a balanced 50/50 class distribution
    between Benign and Malicious traffic for robust training and evaluation.
    """
    if not RAW_CICIDS_DIR.exists() or not list(RAW_CICIDS_DIR.glob("*.csv")):
        logger.warning("CICIDS2017 raw files not found. Falling back to synthetic generator.")
        from src.data.generator import generate_dataset
        return generate_dataset()

    csv_files = list(RAW_CICIDS_DIR.glob("*.csv"))
    logger.info(f"Found {len(csv_files)} CICIDS2017 CSV files. Loading and balancing samples...")

    dfs = []
    for csv_path in csv_files:
        try:
            df_chunk = pd.read_csv(csv_path, nrows=sample_size_per_file, low_memory=False)
            df_chunk.columns = df_chunk.columns.str.strip()
            dfs.append(df_chunk)
        except Exception as e:
            logger.error(f"Failed to load {csv_path.name}: {e}")

    if not dfs:
        from src.data.generator import generate_dataset
        return generate_dataset()

    raw_df = pd.concat(dfs, ignore_index=True)

    mapped = pd.DataFrame()
    if 'Fwd Packet Length Mean' in raw_df.columns:
        mapped['packet_size_kb'] = raw_df['Fwd Packet Length Mean'].fillna(1.0) / 1024.0
    elif 'Total Length of Fwd Packets' in raw_df.columns:
        mapped['packet_size_kb'] = raw_df['Total Length of Fwd Packets'].fillna(1.0) / (1024.0 * max(1, raw_df.get('Total Fwd Packets', 1)))
    else:
        mapped['packet_size_kb'] = np.random.uniform(0.5, 50.0, len(raw_df))

    if 'Flow IAT Mean' in raw_df.columns:
        mapped['interval_sec'] = raw_df['Flow IAT Mean'].fillna(10.0) / 1000000.0  
    else:
        mapped['interval_sec'] = np.random.uniform(1.0, 60.0, len(raw_df))

    mapped['hour'] = np.random.randint(0, 24, len(raw_df))
    mapped['is_off_hours'] = mapped['hour'].apply(lambda h: 1 if (h >= 20 or h < 6) else 0)
    mapped['port_fan_out'] = np.random.randint(1, 15, len(raw_df))
    mapped['entropy'] = np.random.uniform(3.0, 7.5, len(raw_df))

    if 'Total Length of Bwd Packets' in raw_df.columns:
        mapped['outbound_mb'] = raw_df['Total Length of Bwd Packets'].fillna(0.0) / (1024.0 * 1024.0)
    else:
        mapped['outbound_mb'] = np.random.uniform(0.1, 10.0, len(raw_df))

    if 'Flow Duration' in raw_df.columns:
        mapped['session_duration_sec'] = raw_df['Flow Duration'].fillna(1000000.0) / 1000000.0
    else:
        mapped['session_duration_sec'] = np.random.randint(30, 3600, len(raw_df))

    if 'Destination Port' in raw_df.columns:
        dst_port = pd.to_numeric(raw_df['Destination Port'], errors='coerce').fillna(80).astype(int)
    else:
        dst_port = np.random.choice([80, 443, 22, 3389], len(raw_df))
    
    mapped['dst_port_norm'] = dst_port / 65535.0
    mapped['is_external_dst'] = np.random.choice([0, 1], len(raw_df), p=[0.7, 0.3])

    mapped['protocol_tcp'] = 1
    mapped['protocol_udp'] = 0
    mapped['protocol_icmp'] = 0

    if 'Label' in raw_df.columns:
        labels_raw = raw_df['Label'].astype(str).str.strip().str.upper()
        mapped['label'] = labels_raw.apply(lambda l: 0 if 'BENIGN' in l else 1)
    else:
        mapped['label'] = 0

    mapped = mapped.clip(lower=0.0)
    mapped['hour'] = mapped['hour'].astype(int)
    mapped['port_fan_out'] = mapped['port_fan_out'].astype(int)
    mapped['label'] = mapped['label'].astype(int)

    # Balance classes: ensure equal benign and malicious samples
    benign_df = mapped[mapped['label'] == 0]
    malicious_df = mapped[mapped['label'] == 1]

    logger.info(f"Raw CICIDS counts — Benign: {len(benign_df)}, Malicious: {len(malicious_df)}")

    if len(malicious_df) < 500:
        # IfCICIDS attack rows are scarce in this chunk sample, supplement with synthetic malicious samples
        logger.info("Supplementing rare CICIDS attacks with controlled synthetic attack samples for balanced training...")
        from src.data.generator import generate_malicious
        cfg = _load_config()
        mal_syn = generate_malicious(len(benign_df) // 2, 42, cfg)
        mal_syn['dst_port_norm'] = mal_syn['dst_port'] / 65535.0
        mal_syn['is_external_dst'] = 1
        mal_syn['protocol_tcp'] = 1
        mal_syn['protocol_udp'] = 0
        mal_syn['protocol_icmp'] = 0
        malicious_df = pd.concat([malicious_df, mal_syn[FEATURE_COLS + ['label']]], ignore_index=True)

    # Downsample / balance to equal numbers
    target_count = min(len(benign_df), len(malicious_df))
    target_count = max(target_count, 2500)  # at least 2500 per class

    benign_balanced = benign_df.sample(n=min(target_count, len(benign_df)), random_state=42)
    malicious_balanced = malicious_df.sample(n=min(target_count, len(malicious_df)), random_state=42, replace=True if len(malicious_df) < target_count else False)

    balanced_df = pd.concat([benign_balanced, malicious_balanced], ignore_index=True)
    balanced_df = balanced_df.sample(frac=1, random_state=42).reset_index(drop=True)

    logger.info(f"Balanced dataset prepared — Total: {len(balanced_df)} ({balanced_df['label'].sum()} malicious)")
    return balanced_df

def load_and_prepare(csv_path: str = None, test_size: float = 0.2):
    """
    Full pipeline: load CICIDS2017 raw CSVs (or fallback) → scale → split.
    """
    cfg = _load_config()
    seq_len = cfg["detection"]["lstm"]["sequence_length"]

    df = load_cicids_sample(sample_size_per_file=3000)

    X = df[FEATURE_COLS].values.astype(np.float32)
    y = df[LABEL_COL].values.astype(np.int64)

    # Ensure stratify works even if class imbalance is extreme
    strat = y if len(np.unique(y)) > 1 and np.min(np.bincount(y)) > 1 else None

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42, stratify=strat
    )

    scaler = MinMaxScaler()
    X_train_sc = scaler.fit_transform(X_train)
    X_test_sc  = scaler.transform(X_test)

    # Build LSTM sequences (padding if not enough rows)
    def make_seqs(X_arr, y_arr):
        X_seq, y_seq = [], []
        if len(X_arr) <= seq_len:
            # Pad if dataset too small
            padded = np.pad(X_arr, ((0, max(0, seq_len - len(X_arr) + 1)), (0, 0)), mode='constant')
            for i in range(len(X_arr)):
                X_seq.append(padded[i:i+seq_len])
                y_seq.append(y_arr[i])
        else:
            for i in range(len(X_arr) - seq_len):
                X_seq.append(X_arr[i:i+seq_len])
                y_seq.append(y_arr[i+seq_len])
        return np.array(X_seq, dtype=np.float32), np.array(y_seq, dtype=np.int64)

    X_train_seq, y_train_seq = make_seqs(X_train_sc, y_train)
    X_test_seq,  y_test_seq  = make_seqs(X_test_sc,  y_test)

    logger.info(f"Prepared features — train: {len(X_train_sc)}, test: {len(X_test_sc)}")

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
    print("y_train distribution:", np.bincount(data["y_train"]))
