# =============================================================================
# FILE: src/detection/gnn.py
# PURPOSE: HoneyGraph Graph Neural Network (GNN).
#          Reasons over the enterprise network topology (hosts as nodes, flows
#          as edges) using Message Passing (GCNConv / GraphSAGE).
#          Detects coordinated, distributed slow exfiltration that appears
#          benign when viewed on a single host.
#          Outputs a fixed-size topological embedding tensor.
# =============================================================================

import torch
import torch.nn as nn
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

try:
    from torch_geometric.nn import GCNConv, global_mean_pool
    PYG_AVAILABLE = True
except ImportError:
    PYG_AVAILABLE = False


class HoneyGraphGNN(nn.Module):
    """
    Graph Neural Network (HoneyGraph) for network topology reasoning.
    Takes node features and edge indices, and outputs a topological embedding.
    """

    def __init__(self, in_channels: int = 8, hidden_dim: int = 32, embedding_dim: int = 32):
        super().__init__()
        if PYG_AVAILABLE:
            self.conv1 = GCNConv(in_channels, hidden_dim)
            self.conv2 = GCNConv(hidden_dim, hidden_dim)
        else:
            # Fallback linear layers if PyG is not installed in environment
            self.fc_fallback = nn.Linear(in_channels, hidden_dim)

        self.fc = nn.Linear(hidden_dim, embedding_dim)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.2)

    def forward(self, x: torch.Tensor, edge_index: torch.Tensor, batch: torch.Tensor = None) -> torch.Tensor:
        """
        Forward pass.
        x: node feature matrix [num_nodes, in_channels]
        edge_index: graph connectivity [2, num_edges]
        batch: batch vector for graph batching [num_nodes]
        """
        if PYG_AVAILABLE:
            out = self.conv1(x, edge_index)
            out = self.relu(out)
            out = self.dropout(out)

            out = self.conv2(out, edge_index)
            out = self.relu(out)

            if batch is None:
                batch = torch.zeros(x.size(0), dtype=torch.long, device=x.device)

            out = global_mean_pool(out, batch)
        else:
            out = self.relu(self.fc_fallback(x))
            out = out.mean(dim=0, keepdim=True)

        embedding = self.fc(out)
        return embedding


if __name__ == "__main__":
    gnn = HoneyGraphGNN()
    x = torch.randn(10, 8)  # 10 nodes, 8 features
    edge_index = torch.tensor([[0, 1, 2, 3, 4], [1, 2, 3, 4, 0]], dtype=torch.long)
    emb = gnn(x, edge_index)
    print("HoneyGraphGNN output shape:", emb.shape)
