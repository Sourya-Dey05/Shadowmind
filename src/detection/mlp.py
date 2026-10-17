# =============================================================================
# FILE: src/detection/mlp.py
# PURPOSE: Multi-Layer Perceptron (MLP) fusion layer.
#          Concatenates the spatial embedding from SpatialCNN and the temporal
#          embedding from TemporalLSTM, and passes them through dense layers with
#          dropout and batch normalization. Outputs a unified risk score probability
#          between 0.0 and 1.0 (where 0.0 = Benign, 1.0 = Confirmed Exfiltration).
# =============================================================================

import torch
import torch.nn as nn
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class FusionMLP(nn.Module):
    """
    MLP fusion layer combining CNN and LSTM embeddings into a unified risk score.
    Input: concatenated [cnn_embedding (32) + lstm_embedding (32)] = 64 dims.
    Output: single scalar probability [0, 1].
    """

    def __init__(self, cnn_emb_dim: int = 32, lstm_emb_dim: int = 32, hidden_dim: int = 64):
        super().__init__()
        in_dim = cnn_emb_dim + lstm_emb_dim

        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.3),

            nn.Linear(hidden_dim, 32),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.Dropout(0.2),

            nn.Linear(32, 1),
            nn.Sigmoid()  # output probability [0, 1]
        )

    def forward(self, cnn_emb: torch.Tensor, lstm_emb: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.
        cnn_emb shape: (batch_size, cnn_emb_dim)
        lstm_emb shape: (batch_size, lstm_emb_dim)
        """
        combined = torch.cat([cnn_emb, lstm_emb], dim=-1)
        risk_score = self.net(combined)
        return risk_score


if __name__ == "__main__":
    mlp = FusionMLP()
    c = torch.randn(16, 32)
    l = torch.randn(16, 32)
    score = mlp(c, l)
    print("FusionMLP output shape:", score.shape)
