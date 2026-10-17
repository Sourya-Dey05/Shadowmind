# =============================================================================
# FILE: src/detection/train.py
# PURPOSE: Training script for the ShadowMind AI Detection Engine.
#          Loads CICIDS2017 flow data via preprocessor.py, trains the CNN, LSTM,
#          and MLP fusion layers jointly using Binary Cross Entropy loss and Adam,
#          computes validation accuracy / F1 score, and saves the trained weights
#          to models/detection/.
# =============================================================================

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
import numpy as np
import logging
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.data.preprocessor import load_and_prepare
from src.detection.engine import DetectionEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def train_model(epochs: int = 5, batch_size: int = 64, lr: float = 0.001):
    logger.info("Loading and preprocessing dataset for training...")
    data = load_and_prepare()

    X_train = data["X_train"]
    X_train_seq = data["X_train_seq"]
    y_train = data["y_train"]

    X_test = data["X_test"]
    X_test_seq = data["X_test_seq"]
    y_test = data["y_test"]

    # Align sequence count with flat array count if needed
    min_train = min(len(X_train), len(X_train_seq), len(y_train))
    X_train = X_train[:min_train]
    X_train_seq = X_train_seq[:min_train]
    y_train = y_train[:min_train]

    min_test = min(len(X_test), len(X_test_seq), len(y_test))
    X_test = X_test[:min_test]
    X_test_seq = X_test_seq[:min_test]
    y_test = y_test[:min_test]

    train_dataset = TensorDataset(
        torch.tensor(X_train, dtype=torch.float32),
        torch.tensor(X_train_seq, dtype=torch.float32),
        torch.tensor(y_train, dtype=torch.float32).unsqueeze(1)
    )
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    engine = DetectionEngine()
    engine.set_train_mode()

    # Joint optimizer for cnn, lstm, mlp
    optimizer = optim.Adam(
        list(engine.cnn.parameters()) + list(engine.lstm.parameters()) + list(engine.mlp.parameters()),
        lr=lr
    )
    criterion = nn.BCELoss()

    logger.info(f"Starting training for {epochs} epochs on device: {engine.device}...")

    for epoch in range(epochs):
        total_loss = 0.0
        correct = 0
        total = 0

        for batch_flat, batch_seq, batch_y in train_loader:
            batch_flat = batch_flat.to(engine.device)
            batch_seq = batch_seq.to(engine.device)
            batch_y = batch_y.to(engine.device)

            optimizer.zero_grad()

            cnn_emb = engine.cnn(batch_flat)
            lstm_emb = engine.lstm(batch_seq)
            preds = engine.mlp(cnn_emb, lstm_emb)

            loss = criterion(preds, batch_y)
            loss.backward()
            optimizer.step()

            total_loss += loss.item() * len(batch_y)
            predicted_labels = (preds >= 0.5).float()
            correct += (predicted_labels == batch_y).sum().item()
            total += len(batch_y)

        epoch_loss = total_loss / total
        epoch_acc = correct / total
        logger.info(f"Epoch [{epoch+1}/{epochs}] — Loss: {epoch_loss:.4f} — Accuracy: {epoch_acc*100:.2f}%")

    # Evaluation on test set
    engine.set_eval_mode()
    with torch.no_grad():
        t_flat = torch.tensor(X_test, dtype=torch.float32).to(engine.device)
        t_seq = torch.tensor(X_test_seq, dtype=torch.float32).to(engine.device)
        t_y = torch.tensor(y_test, dtype=torch.float32).unsqueeze(1).to(engine.device)

        c_emb = engine.cnn(t_flat)
        l_emb = engine.lstm(t_seq)
        test_preds = engine.mlp(c_emb, l_emb)

        test_labels = (test_preds >= 0.5).float()
        test_acc = (test_labels == t_y).sum().item() / len(t_y)
        logger.info(f"Test Evaluation — Accuracy: {test_acc*100:.2f}%")

    # Save trained weights
    engine.save_weights()
    logger.info("Training complete. Weights saved successfully.")


if __name__ == "__main__":
    train_model(epochs=3)
