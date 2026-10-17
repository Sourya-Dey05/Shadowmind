# =============================================================================
# FILE: src/detection/mlp.py
# PURPOSE: Multi-Layer Perceptron (MLP) fusion layer (3-way upgrade).
#          Concatenates spatial embedding (CNN), temporal embedding (LSTM),
#          and topological embedding (HoneyGraph GNN) into a 96-dim vector,
#          passing it through dense layers to output a unified risk score probability
#          between 0.0 and 1.0.
# =============================================================================

import torch
import torch.nn as nn
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class FusionMLP(nn.Module):
    """
    3-Way MLP fusion layer combining CNN + LSTM + GNN embeddings into a unified risk score.
    Input: concatenated [cnn_emb (32) + lstm_emb (32) + gnn_emb (32)] = 96 dims.
    Output: single scalar probability [0, 1].
    """

    def __init__(self, cnn_dim: int = 32, lstm_dim: int = 32, gnn_dim: int = 32, hidden_dim: int = 64):
        super().__init__()
        in_dim = cnn_dim + lstm_dim + gnn_dim

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
            nn.Sigmoid()
        )

    def forward(self, cnn_emb: torch.Tensor, lstm_emb: torch.Tensor, gnn_emb: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.
        cnn_emb: (batch_size, cnn_dim)
        lstm_emb: (batch_size, lstm_dim)
        gnn_emb: (batch_size, gnn_dim)
        """
        # Ensure batch dimensions match
        if gnn_emb.size(0) != cnn_emb.size(0):
            gnn_emb = gnn_emb.repeat(cnn_emb.size(0), 1)[:cnn_emb.size(0)]

        combined = torch.cat([cnn_emb, lstm_emb, gnn_emb], dim=-1)
        risk_score = self.net(combined)
        return risk_score


if __name__ == "__main__":
    mlp = FusionMLP()
    c = torch.randn(16, 32)
    l = torch.randn(16, 32)
    g = torch.randn(16, 32)
    score = mlp(c, l, g)
    print("FusionMLP 3-way output shape:", score.shape)
