# =============================================================================
# FILE: src/data/generator.py
# PURPOSE: Generates synthetic labeled network traffic data for training and
#          testing the ShadowMind detection engine. Produces two classes:
#          BENIGN (label=0) — normal user traffic during business hours, and
#          MALICIOUS (label=1) — slow exfiltration beacons (< 5 KB packets at
#          random long intervals, off-hours). Output is a CSV that all ML
#          modules in Phase 1+ consume. No real network traffic is required.
# =============================================================================

import random
import pandas as pd
import numpy as np
import yaml
import os
import logging
from pathlib import Path

# --- Logging setup ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# --- Load config ---
CONFIG_PATH = Path(__file__).resolve().parents[2] / "configs" / "thresholds.yaml"

def _load_config() -> dict:
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _random_internal_ip() -> str:
    """Return a fake RFC-1918 LAN IP (simulates an employee workstation)."""
    return f"192.168.1.{random.randint(2, 200)}"

def _random_external_ip() -> str:
    """Return a fake attacker C2 or cloud destination IP."""
    return f"203.0.113.{random.randint(1, 254)}"

def _random_internal_dst() -> str:
    """Return a fake internal server IP (file share, DB)."""
    return f"10.0.0.{random.randint(1, 50)}"

# ---------------------------------------------------------------------------
# Benign traffic generator
# ---------------------------------------------------------------------------

def generate_benign(n: int, seed: int) -> pd.DataFrame:
    """
    Generate n rows of normal user traffic.

    Characteristics:
    - Business hours (7 AM – 7 PM)
    - Packet size 10 KB – 2 MB (regular file transfers, emails, browsing)
    - Short inter-arrival times (1 – 120 seconds)
    - Internal destinations only
    - Low entropy (structured data)
    - Low port fan-out (1–3 distinct ports per session)
    """
    rng = random.Random(seed)
    np_rng = np.random.default_rng(seed)
    records = []

    for _ in range(n):
        hour = rng.randint(7, 19)
        records.append({
            "src_ip":           _random_internal_ip(),
            "dst_ip":           _random_internal_dst(),
            "packet_size_kb":   np_rng.uniform(10.0, 2048.0),
            "interval_sec":     rng.uniform(1.0, 120.0),
            "hour":             hour,
            "is_off_hours":     0,
            "dst_port":         rng.choice([80, 443, 445, 3389, 8080]),
            "port_fan_out":     rng.randint(1, 3),
            "entropy":          round(np_rng.uniform(3.0, 5.5), 4),
            "outbound_mb":      round(np_rng.uniform(0.01, 20.0), 4),
            "session_duration_sec": rng.randint(30, 3600),
            "protocol":         rng.choice(["TCP", "UDP", "TCP"]),  # TCP weighted
            "label":            0,  # BENIGN
        })

    return pd.DataFrame(records)

# ---------------------------------------------------------------------------
# Malicious (slow exfiltration) traffic generator
# ---------------------------------------------------------------------------

def generate_malicious(n: int, seed: int, cfg: dict) -> pd.DataFrame:
    """
    Generate n rows of slow-exfiltration (low-and-slow) attack traffic.

    Characteristics:
    - Off-hours (8 PM – 6 AM) to avoid SOC attention
    - Tiny packets (< 5 KB) at long random intervals (5–60 minutes)
    - External destination IPs (attacker C2 server)
    - High entropy (encrypted/compressed stolen data)
    - High port fan-out (attacker rotates ports to evade detection)
    - Large cumulative outbound volume despite small individual packets
    """
    rng = random.Random(seed + 1)
    np_rng = np.random.default_rng(seed + 1)
    records = []

    max_pkt = cfg["detection"]["slow_exfil"]["max_packet_kb"]
    off_start = cfg["detection"]["slow_exfil"]["off_hours_start"]
    off_end = cfg["detection"]["slow_exfil"]["off_hours_end"]
    min_interval = cfg["detection"]["slow_exfil"]["beacon_interval_min_sec"]

    for _ in range(n):
        # Off-hours: either late night or early morning
        if rng.random() < 0.7:
            hour = rng.randint(off_start, 23)
        else:
            hour = rng.randint(0, off_end)

        records.append({
            "src_ip":           _random_internal_ip(),
            "dst_ip":           _random_external_ip(),       # exfil to external
            "packet_size_kb":   round(np_rng.uniform(0.1, max_pkt), 4),
            "interval_sec":     rng.uniform(min_interval, 3600.0),
            "hour":             hour,
            "is_off_hours":     1,
            "dst_port":         rng.randint(1024, 65535),    # random high port
            "port_fan_out":     rng.randint(5, 20),
            "entropy":          round(np_rng.uniform(6.5, 8.0), 4),  # high = encrypted
            "outbound_mb":      round(np_rng.uniform(0.0001, 0.005), 6),  # tiny per packet
            "session_duration_sec": rng.randint(3600, 86400),  # long sessions
            "protocol":         rng.choice(["TCP", "UDP", "ICMP"]),
            "label":            1,  # MALICIOUS
        })

    return pd.DataFrame(records)

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_dataset(output_path: str = None) -> pd.DataFrame:
    """
    Generate the full labeled synthetic dataset and save to CSV.

    Returns the combined DataFrame (benign + malicious, shuffled).
    Reads sample counts and seed from configs/thresholds.yaml.
    """
    cfg = _load_config()
    n_benign   = cfg["data"]["synthetic"]["benign_samples"]
    n_malicious = cfg["data"]["synthetic"]["malicious_samples"]
    seed       = cfg["data"]["synthetic"]["random_seed"]
    out_path   = output_path or cfg["data"]["output_path"]

    logger.info(f"Generating {n_benign} benign + {n_malicious} malicious samples (seed={seed})")

    df_benign   = generate_benign(n_benign, seed)
    df_malicious = generate_malicious(n_malicious, seed, cfg)

    df = pd.concat([df_benign, df_malicious], ignore_index=True)
    df = df.sample(frac=1, random_state=seed).reset_index(drop=True)  # shuffle

    # Ensure output directory exists
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    df.to_csv(out_path, index=False)
    logger.info(f"Dataset saved → {out_path}  ({len(df)} rows, {df['label'].sum()} malicious)")

    return df


if __name__ == "__main__":
    df = generate_dataset()
    print(df.head(10))
    print(f"\nClass distribution:\n{df['label'].value_counts()}")
