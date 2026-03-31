import os
import sys
import time
import math
import zlib
import argparse
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import LabelEncoder, StandardScaler
from collections import Counter
import joblib
from tqdm import tqdm

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, '..', 'data', 'cipher_MASTER_FULL_V3_shuffled.csv')
MODEL_DIR = os.path.join(BASE_DIR, 'app', 'models')

MAX_LEN = 512
# Expanded vocabulary: 0=PAD, 1-26=A-Z, 27-36=0-9, 37=SPACE, 38=OTHER
VOCAB_SIZE = 39


def tokenize_char(c):
    """Convert a single character to a token ID."""
    c = c.upper()
    if 'A' <= c <= 'Z':
        return ord(c) - 64       # 1-26
    elif '0' <= c <= '9':
        return ord(c) - 48 + 27  # 27-36
    elif c == ' ':
        return 37
    else:
        return 38  # other/punctuation


def extract_features_fast(text):
    """Extract 14 statistical features matching feature_extraction.py."""
    if isinstance(text, bytes):
        data = text
        txt = None
    else:
        data = text.encode('utf-8', errors='ignore')
        txt = text

    total = len(data)
    if total == 0:
        return np.zeros(14, dtype=np.float32)

    freqs = Counter(data)
    entropy = -sum((f / total) * math.log2(f / total) for f in freqs.values())
    compression = len(zlib.compress(data)) / total

    if total > 1:
        bigrams = [data[i:i + 2] for i in range(total - 1)]
        freqs2 = Counter(bigrams)
        total2 = len(bigrams)
        bigram_entropy = -sum((f / total2) * math.log2(f / total2) for f in freqs2.values())
    else:
        bigram_entropy = 0.0

    if total > 2:
        trigrams = [data[i:i + 3] for i in range(total - 2)]
        freqs3 = Counter(trigrams)
        total3 = len(trigrams)
        trigram_entropy = -sum((f / total3) * math.log2(f / total3) for f in freqs3.values())
    else:
        trigram_entropy = 0.0

    vals = list(freqs.values())
    uniformity = float(np.std(vals)) if vals else 0.0
    unique_ratio = len(freqs) / total

    transitions = Counter(zip(data, data[1:]))
    transition_var = float(np.var(list(transitions.values()))) if transitions else 0.0

    runs = []
    current = 1
    for i in range(1, total):
        if data[i] == data[i - 1]:
            current += 1
        else:
            runs.append(current)
            current = 1
    runs.append(current)
    run_length_mean = float(np.mean(runs)) if runs else 0.0
    run_length_var = float(np.var(runs)) if runs else 0.0

    # IoC — works on alpha chars, falls back to digits
    alpha_chars = [c for c in (txt or '') if c.isalpha()]
    if len(alpha_chars) > 1:
        f = Counter(alpha_chars)
        N = len(alpha_chars)
        ioc = sum(v * (v - 1) for v in f.values()) / (N * (N - 1))
    else:
        digit_chars = [c for c in (txt or '') if c.isdigit()]
        if len(digit_chars) > 1:
            f = Counter(digit_chars)
            N = len(digit_chars)
            ioc = sum(v * (v - 1) for v in f.values()) / (N * (N - 1))
        else:
            ioc = 0.0

    work_chars = alpha_chars if len(alpha_chars) > 1 else [c for c in (txt or '') if c.isdigit()]
    work_text = ''.join(work_chars)
    if len(work_text) > 2:
        iocs = []
        for period in range(2, 10):
            slices = [''.join(work_text[i::period]) for i in range(period)]
            p_vals = []
            for s in slices:
                if len(s) > 1:
                    fc = Counter(s)
                    N2 = len(s)
                    p_vals.append(sum(v * (v - 1) for v in fc.values()) / (N2 * (N2 - 1)))
            if p_vals:
                iocs.append(np.var(p_vals))
        ioc_variance = float(np.mean(iocs)) if iocs else 0.0
    else:
        ioc_variance = 0.0

    txt_len = max(len(txt or ''), 1)
    digit_ratio = sum(1 for c in (txt or '') if c.isdigit()) / txt_len
    alpha_ratio = sum(1 for c in (txt or '') if c.isalpha()) / txt_len

    return np.array([
        float(total), entropy, compression, bigram_entropy, trigram_entropy,
        uniformity, unique_ratio, transition_var, run_length_mean,
        run_length_var, ioc, ioc_variance, digit_ratio, alpha_ratio
    ], dtype=np.float32)


class HybridCipherDataset(Dataset):
    def __init__(self, texts, feature_matrix, labels):
        self.texts = list(texts)
        self.features = feature_matrix  # numpy array (N, 14)
        self.labels = labels

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]

        # Tokenize with expanded vocabulary
        seq = [tokenize_char(c) for c in text]
        if len(seq) > MAX_LEN:
            seq = seq[:MAX_LEN]

        padded = np.zeros(MAX_LEN, dtype=np.int64)
        padded[:len(seq)] = seq

        feats = self.features[idx]

        return (
            torch.tensor(padded, dtype=torch.long),
            torch.tensor(feats, dtype=torch.float32),
            torch.tensor(label, dtype=torch.long),
        )


class HybridCipherNet(nn.Module):
    """Dual-input network: raw characters + statistical features."""

    def __init__(self, num_classes, num_features=12):
        super().__init__()

        # ── Branch A: Character-level CNN ──
        self.embedding = nn.Embedding(VOCAB_SIZE, 64, padding_idx=0)

        self.conv_block1 = nn.Sequential(
            nn.Conv1d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Conv1d(128, 128, kernel_size=3, padding=1),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.MaxPool1d(2),
        )

        self.conv_block2 = nn.Sequential(
            nn.Conv1d(128, 256, kernel_size=5, padding=2),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Conv1d(256, 256, kernel_size=5, padding=2),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.MaxPool1d(2),
        )

        self.conv_block3 = nn.Sequential(
            nn.Conv1d(256, 512, kernel_size=7, padding=3),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.MaxPool1d(2),
        )

        self.global_pool = nn.AdaptiveAvgPool1d(1)  # → (batch, 512, 1)

        # ── Branch B: Feature MLP ──
        self.feature_net = nn.Sequential(
            nn.Linear(num_features, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
        )

        # ── Fusion Head ──
        self.classifier = nn.Sequential(
            nn.Linear(512 + 64, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, num_classes),
        )

    def forward(self, tokens, features):
        # Branch A
        x = self.embedding(tokens)       # (B, 512, 64)
        x = x.transpose(1, 2)            # (B, 64, 512)
        x = self.conv_block1(x)           # (B, 128, 256)
        x = self.conv_block2(x)           # (B, 256, 128)
        x = self.conv_block3(x)           # (B, 512, 64)
        x = self.global_pool(x).squeeze(-1)  # (B, 512)

        # Branch B
        f = self.feature_net(features)    # (B, 64)

        # Fuse
        combined = torch.cat([x, f], dim=1)  # (B, 576)
        return self.classifier(combined)


def train_hybrid(quick_mode=False):
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)

    print(f"Loading data from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)

    if quick_mode:
        print("QUICK MODE: 2200 samples for rapid prototyping.")
        df = df.groupby('cipher').head(100).sample(frac=1, random_state=42).reset_index(drop=True)
        epochs = 3
    else:
        epochs = 15

    texts = df['ciphertext'].values
    y_cipher = df['cipher']

    # ── Extract / load features ──
    feature_cols = [
        "length", "entropy", "compression", "bigram_entropy", "trigram_entropy",
        "uniformity", "unique_ratio", "transition_var", "run_length_mean",
        "run_length_var", "ioc", "ioc_variance", "digit_ratio", "alpha_ratio"
    ]

    if all(c in df.columns for c in feature_cols):
        print("Using pre-computed features from CSV...")
        feature_matrix = df[feature_cols].values.astype(np.float32)
    else:
        print("Extracting features from raw text (this will take a while)...")
        feature_matrix = np.array([extract_features_fast(t) for t in texts], dtype=np.float32)

    # Normalize features
    scaler = StandardScaler()
    feature_matrix = scaler.fit_transform(feature_matrix)
    joblib.dump(scaler, os.path.join(MODEL_DIR, "hybrid_feature_scaler.pkl"))

    # Encode labels
    le = LabelEncoder()
    y_encoded = le.fit_transform(y_cipher)
    joblib.dump(le, os.path.join(MODEL_DIR, "hybrid_label_encoder.pkl"))

    num_classes = len(le.classes_)
    print(f"Classes: {num_classes} — {list(le.classes_)}")

    # ── Create dataset & loaders ──
    dataset = HybridCipherDataset(texts, feature_matrix, y_encoded)

    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_ds, val_ds = torch.utils.data.random_split(dataset, [train_size, val_size],
                                                      generator=torch.Generator().manual_seed(42))

    batch_size = 256
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=0, pin_memory=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=0, pin_memory=True)

    # ── Device ──
    device = torch.device(
        "cuda" if torch.cuda.is_available()
        else "mps" if torch.backends.mps.is_available()
        else "cpu"
    )
    print(f"Training on: {device}")

    # ── Model ──
    num_features = feature_matrix.shape[1]
    model = HybridCipherNet(num_classes=num_classes, num_features=num_features).to(device)
    total_params = sum(p.numel() for p in model.parameters())
    print(f"Model parameters: {total_params:,}")

    # Label smoothing for better generalization
    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
    optimizer = optim.AdamW(model.parameters(), lr=0.001, weight_decay=1e-4)

    # OneCycleLR for faster convergence
    steps_per_epoch = len(train_loader)
    scheduler = optim.lr_scheduler.OneCycleLR(
        optimizer, max_lr=0.003, epochs=epochs, steps_per_epoch=steps_per_epoch
    )

    best_val_acc = 0.0

    print(f"\nStarting training for {epochs} epochs...")
    epoch_bar = tqdm(range(epochs), desc="Epochs", unit="epoch", position=0)
    for epoch in epoch_bar:
        model.train()
        total_loss, correct, total = 0, 0, 0

        start = time.time()
        train_bar = tqdm(train_loader, desc=f"  Train {epoch+1}/{epochs}",
                         unit="batch", position=1, leave=False)
        for batch_tok, batch_feat, batch_y in train_bar:
            batch_tok = batch_tok.to(device)
            batch_feat = batch_feat.to(device)
            batch_y = batch_y.to(device)

            optimizer.zero_grad()
            outputs = model(batch_tok, batch_feat)
            loss = criterion(outputs, batch_y)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            scheduler.step()

            total_loss += loss.item() * batch_tok.size(0)
            _, preds = torch.max(outputs, 1)
            total += batch_y.size(0)
            correct += (preds == batch_y).sum().item()

            # Live update on progress bar
            train_bar.set_postfix(
                loss=f"{total_loss/total:.4f}",
                acc=f"{correct/total:.4f}",
                lr=f"{scheduler.get_last_lr()[0]:.6f}"
            )

        train_acc = correct / total
        train_loss = total_loss / total

        # ── Validation ──
        model.eval()
        val_loss, val_correct, val_total = 0, 0, 0
        val_bar = tqdm(val_loader, desc=f"  Val   {epoch+1}/{epochs}",
                       unit="batch", position=1, leave=False)
        with torch.no_grad():
            for batch_tok, batch_feat, batch_y in val_bar:
                batch_tok = batch_tok.to(device)
                batch_feat = batch_feat.to(device)
                batch_y = batch_y.to(device)

                outputs = model(batch_tok, batch_feat)
                loss = criterion(outputs, batch_y)
                val_loss += loss.item() * batch_tok.size(0)
                _, preds = torch.max(outputs, 1)
                val_total += batch_y.size(0)
                val_correct += (preds == batch_y).sum().item()

                val_bar.set_postfix(
                    loss=f"{val_loss/val_total:.4f}",
                    acc=f"{val_correct/val_total:.4f}"
                )

        val_acc = val_correct / val_total
        val_loss_avg = val_loss / val_total
        elapsed = time.time() - start

        lr_now = scheduler.get_last_lr()[0]

        # Update epoch bar with summary
        epoch_bar.set_postfix(
            train_acc=f"{train_acc:.4f}",
            val_acc=f"{val_acc:.4f}",
            best=f"{best_val_acc:.4f}"
        )
        tqdm.write(f"Epoch {epoch + 1}/{epochs} [{elapsed:.1f}s] "
                   f"Train: loss={train_loss:.4f} acc={train_acc:.4f} | "
                   f"Val: loss={val_loss_avg:.4f} acc={val_acc:.4f} | "
                   f"LR: {lr_now:.6f}")

        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), os.path.join(MODEL_DIR, "hybrid_cnn.pth"))
            tqdm.write(f"  ✅ New best val_acc={val_acc:.4f} — model saved!")

    print(f"\nTraining complete! Best validation accuracy: {best_val_acc:.4f}")
    print(f"Model saved to {os.path.join(MODEL_DIR, 'hybrid_cnn.pth')}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true", help="Quick test with small sample")
    args = parser.parse_args()
    train_hybrid(quick_mode=args.quick)
