# =============================================================================
# FILE: src/detection/lstm.py
# PURPOSE: Long Short-Term Memory (LSTM) temporal anomaly detector.
#          Takes time-series sequences of network traffic events and detects
#          temporal anomalies such as periodic low-and-slow beacons (< 5 KB
#          packets at regular long intervals over hours) and login-time drift.
#          Outputs a fixed-size temporal embedding tensor.
# =============================================================================

import torch
import torch.nn as nn
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class TemporalLSTM(nn.Module):
    """
    LSTM network for temporal sequence analysis of network traffic.
    Input shape: (batch_size, sequence_length, num_features)
    """

    def __init__(self, input_dim: int = 13, hidden_dim: int = 64, embedding_dim: int = 32, num_layers: int = 2):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.2 if num_layers > 1 else 0.0
        )
        self.fc = nn.Linear(hidden_dim, embedding_dim)
        self.relu = nn.ReLU()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.
        x shape: (batch_size, seq_len, features)
        """
        # LSTM output: (batch, seq_len, hidden_dim)
        lstm_out, (hn, cn) = self.lstm(x)

        # Take the output of the final time step
        last_step = lstm_out[:, -1, :]

        out = self.fc(last_step)
        embedding = self.relu(out)
        return embedding


if __name__ == "__main__":
    net = TemporalLSTM()
    dummy_seq = torch.randn(16, 50, 13)  # batch 16, 50 time steps, 13 features
    emb = net(dummy_seq)
    print("TemporalLSTM output shape:", emb.shape)
