# =============================================================================
# FILE: src/detection/engine.py
# PURPOSE: Detection Engine orchestrator. Combines SpatialCNN, TemporalLSTM,
#          and FusionMLP into a single end-to-end inference pipeline.
#          Takes raw traffic sample(s) or sequence windows, runs them through
#          the ensemble, evaluates against thresholds.yaml, and outputs a
#          structured threat classification: BENIGN, SUSPICIOUS, or
#          CONFIRMED EXFILTRATION. Also handles model saving and loading.
# =============================================================================

import torch
import yaml
import logging
from pathlib import Path
from typing import Dict, Union
import numpy as np

from src.detection.cnn import SpatialCNN
from src.detection.lstm import TemporalLSTM
from src.detection.mlp import FusionMLP

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CONFIG_PATH = Path(__file__).resolve().parents[2] / "configs" / "thresholds.yaml"
MODEL_DIR   = Path(__file__).resolve().parents[2] / "models" / "detection"


class DetectionEngine:
    """
    Orchestrates the CNN + LSTM + MLP ensemble for real-time threat scoring.
    """

    def __init__(self):
        with open(CONFIG_PATH, "r") as f:
            self.cfg = yaml.safe_load(f)

        thresh = self.cfg["detection"]["risk_score"]
        self.benign_max      = thresh["benign_max"]
        self.suspicious_min  = thresh["suspicious_min"]
        self.confirmed_min   = thresh["confirmed_min"]

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"DetectionEngine initializing on device: {self.device}")

        # Instantiate sub-models
        self.cnn = SpatialCNN().to(self.device)
        self.lstm = TemporalLSTM().to(self.device)
        self.mlp = FusionMLP().to(self.device)

        self.set_eval_mode()

    def set_eval_mode(self):
        self.cnn.eval()
        self.lstm.eval()
        self.mlp.eval()

    def set_train_mode(self):
        self.cnn.train()
        self.lstm.train()
        self.mlp.train()

    def classify_risk(self, risk_score: float) -> str:
        """Map numerical risk score [0, 1] to categorical threat label."""
        if risk_score <= self.benign_max:
            return "BENIGN"
        elif risk_score < self.confirmed_min:
            return "SUSPICIOUS"
        else:
            return "CONFIRMED EXFILTRATION"

    def predict(self, x_flat: np.ndarray, x_seq: np.ndarray) -> Dict[str, Union[float, str]]:
        """
        Run inference on a single sample or batch.
        x_flat: shape (batch_size, features) for CNN
        x_seq:  shape (batch_size, seq_len, features) for LSTM
        """
        self.set_eval_mode()
        with torch.no_grad():
            t_flat = torch.tensor(x_flat, dtype=torch.float32).to(self.device)
            t_seq  = torch.tensor(x_seq, dtype=torch.float32).to(self.device)

            cnn_emb  = self.cnn(t_flat)
            lstm_emb = self.lstm(t_seq)
            score_tensor = self.mlp(cnn_emb, lstm_emb)

            score = score_tensor.mean().item()
            label = self.classify_risk(score)

        return {
            "risk_score": round(score, 4),
            "threat_label": label,
        }

    def save_weights(self):
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        torch.save(self.cnn.state_dict(), MODEL_DIR / "cnn.pt")
        torch.save(self.lstm.state_dict(), MODEL_DIR / "lstm.pt")
        torch.save(self.mlp.state_dict(), MODEL_DIR / "mlp.pt")
        logger.info(f"Model weights saved to {MODEL_DIR}")

    def load_weights(self):
        try:
            self.cnn.load_state_dict(torch.load(MODEL_DIR / "cnn.pt", map_location=self.device))
            self.lstm.load_state_dict(torch.load(MODEL_DIR / "lstm.pt", map_location=self.device))
            self.mlp.load_state_dict(torch.load(MODEL_DIR / "mlp.pt", map_location=self.device))
            logger.info(f"Model weights loaded from {MODEL_DIR}")
        except FileNotFoundError:
            logger.warning("No saved model weights found. Using random initialization.")


if __name__ == "__main__":
    engine = DetectionEngine()
    dummy_flat = np.random.randn(1, 13)
    dummy_seq  = np.random.randn(1, 50, 13)
    res = engine.predict(dummy_flat, dummy_seq)
    print("Test inference result:", res)
