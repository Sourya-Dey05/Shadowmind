# =============================================================================
# FILE: src/detection/cnn.py
# PURPOSE: 1D Convolutional Neural Network (CNN) spatial anomaly detector.
#          Takes normalized network flow feature vectors and extracts spatial
#          patterns (such as sudden large outbound data spikes, unusual port
#          fan-out, and high-entropy payloads characteristic of data exfiltration).
#          Outputs a fixed-size spatial embedding tensor.
# =============================================================================

import torch
import torch.nn as nn
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class SpatialCNN(nn.Module):
    """
    1D CNN for spatial feature extraction from network traffic flows.
    Input shape: (batch_size, num_features, sequence_length=1) or (batch_size, channels, length)
    """

    def __init__(self, in_channels: int = 13, embedding_dim: int = 32):
        super().__init__()
        self.conv1 = nn.Conv1d(in_channels=in_channels, out_channels=32, kernel_size=1)
        self.bn1   = nn.BatchNorm1d(32)
        self.relu  = nn.ReLU()
        self.drop1 = nn.Dropout(0.2)

        self.conv2 = nn.Conv1d(in_channels=32, out_channels=64, kernel_size=1)
        self.bn2   = nn.BatchNorm1d(64)
        self.drop2 = nn.Dropout(0.2)

        self.fc    = nn.Linear(64, embedding_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.
        x shape: (batch_size, num_features) or (batch_size, seq_len, features)
        """
        # If 3D input (batch, seq, features), take mean across seq or permute
        if x.dim() == 3:
            # Shape: (batch, seq, features) -> (batch, features, seq)
            x = x.permute(0, 2, 1)
        elif x.dim() == 2:
            # Shape: (batch, features) -> (batch, features, 1)
            x = x.unsqueeze(-1)

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)
        out = self.drop1(out)

        out = self.conv2(out)
        out = self.bn2(out)
        out = self.relu(out)
        out = self.drop2(out)

        # Global average pooling across length dimension
        out = torch.mean(out, dim=-1)

        embedding = self.fc(out)
        return embedding


if __name__ == "__main__":
    net = SpatialCNN()
    dummy_input = torch.randn(16, 13)  # batch 16, 13 features
    emb = net(dummy_input)
    print("SpatialCNN output shape:", emb.shape)
