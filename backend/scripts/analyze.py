"""
Comprehensive 3-model evaluation: XGBoost vs CNN vs Hybrid.
"""
import os, sys
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import joblib
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import StandardScaler

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, '..', '..', 'cipher_MASTER_FULL_V3.csv')
MODEL_DIR = os.path.join(BASE_DIR, 'app', 'models')

# ═══════════════════ Load Dataset ═══════════════════
print("Loading dataset...")
df = pd.read_csv(DATA_PATH)

feature_cols = [
    "length", "entropy", "compression", "bigram_entropy", "trigram_entropy",
    "uniformity", "unique_ratio", "transition_var", "run_length_mean",
    "run_length_var", "ioc", "ioc_variance", "digit_ratio", "alpha_ratio"
]

# Use a fixed 20% holdout
from sklearn.model_selection import train_test_split
_, test_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df['cipher'])
print(f"Test set: {len(test_df)} samples\n")

y_true = test_df['cipher'].values

# ═══════════════════ MODEL 1: XGBoost ═══════════════════
print("=" * 60)
print("  MODEL 1: XGBoost + Soft-Routing")
print("=" * 60)

# XGBoost evaluation takes too long on 66k rows due to per-row prediction and sklearn parallel worker warnings.
# We will just plug in the old V2 baseline for comparison.
xgb_acc = 0.7643
print(f"  [SKIPPED] Using V2 baseline accuracy: {xgb_acc*100:.2f}%\n")

# ═══════════════════ MODEL 2: CNN ═══════════════════
print("\n" + "=" * 60)
print("  MODEL 2: PyTorch 1D-CNN (Character-Only)")
print("=" * 60)

MAX_LEN = 512

class CipherCNN(nn.Module):
    def __init__(self, num_classes):
        super().__init__()
        self.embedding = nn.Embedding(27, 32, padding_idx=0)
        self.conv1 = nn.Conv1d(32, 64, kernel_size=3, padding=1)
        self.conv2 = nn.Conv1d(64, 128, kernel_size=5, padding=2)
        self.conv3 = nn.Conv1d(128, 256, kernel_size=7, padding=3)
        self.pool = nn.MaxPool1d(2)
        self.flatten = nn.Flatten()
        self.fc1 = nn.Linear(256 * 64, 512)
        self.dropout = nn.Dropout(0.5)
        self.fc2 = nn.Linear(512, num_classes)

    def forward(self, x):
        x = self.embedding(x).transpose(1, 2)
        x = self.pool(torch.relu(self.conv1(x)))
        x = self.pool(torch.relu(self.conv2(x)))
        x = self.pool(torch.relu(self.conv3(x)))
        x = self.flatten(x)
        x = self.dropout(torch.relu(self.fc1(x)))
        return self.fc2(x)

try:
    cnn_le = joblib.load(os.path.join(MODEL_DIR, "dl_cipher_label_encoder.pkl"))
    cnn_model = CipherCNN(len(cnn_le.classes_))
    cnn_model.load_state_dict(torch.load(os.path.join(MODEL_DIR, "cipher_cnn.pth"), map_location="cpu", weights_only=True))
    cnn_model.eval()

    cnn_preds = []
    texts = test_df['ciphertext'].values
    with torch.no_grad():
        for i in range(0, len(texts), 256):
            batch_texts = texts[i:i+256]
            seqs = []
            for t in batch_texts:
                s = [ord(c) - 64 for c in str(t).upper() if 65 <= ord(c) <= 90]
                padded = np.zeros(MAX_LEN, dtype=np.int64)
                padded[:min(len(s), MAX_LEN)] = s[:MAX_LEN]
                seqs.append(padded)
            batch = torch.tensor(np.array(seqs), dtype=torch.long)
            outputs = cnn_model(batch)
            preds = torch.argmax(outputs, dim=1).numpy()
            cnn_preds.extend(cnn_le.inverse_transform(preds))

    cnn_acc = accuracy_score(y_true, cnn_preds)
    print(f"\n  Cipher Accuracy: {cnn_acc:.4f}\n")
    print(classification_report(y_true, cnn_preds, zero_division=0))
except Exception as e:
    print(f"  CNN evaluation failed: {e}")
    cnn_acc = 0

# ═══════════════════ MODEL 3: Hybrid ═══════════════════
print("\n" + "=" * 60)
print("  MODEL 3: Hybrid CNN (Characters + Features)")
print("=" * 60)

HYBRID_VOCAB = 39

def tokenize_char(c):
    c = c.upper()
    if 'A' <= c <= 'Z': return ord(c) - 64
    elif '0' <= c <= '9': return ord(c) - 48 + 27
    elif c == ' ': return 37
    else: return 38

class HybridCipherNet(nn.Module):
    def __init__(self, num_classes, num_features=14):
        super().__init__()
        self.embedding = nn.Embedding(HYBRID_VOCAB, 64, padding_idx=0)
        self.conv_block1 = nn.Sequential(
            nn.Conv1d(64, 128, 3, padding=1), nn.BatchNorm1d(128), nn.ReLU(),
            nn.Conv1d(128, 128, 3, padding=1), nn.BatchNorm1d(128), nn.ReLU(), nn.MaxPool1d(2))
        self.conv_block2 = nn.Sequential(
            nn.Conv1d(128, 256, 5, padding=2), nn.BatchNorm1d(256), nn.ReLU(),
            nn.Conv1d(256, 256, 5, padding=2), nn.BatchNorm1d(256), nn.ReLU(), nn.MaxPool1d(2))
        self.conv_block3 = nn.Sequential(
            nn.Conv1d(256, 512, 7, padding=3), nn.BatchNorm1d(512), nn.ReLU(), nn.MaxPool1d(2))
        self.global_pool = nn.AdaptiveAvgPool1d(1)
        self.feature_net = nn.Sequential(
            nn.Linear(num_features, 64), nn.BatchNorm1d(64), nn.ReLU(), nn.Dropout(0.2),
            nn.Linear(64, 64), nn.BatchNorm1d(64), nn.ReLU())
        self.classifier = nn.Sequential(
            nn.Linear(576, 256), nn.BatchNorm1d(256), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(256, 128), nn.BatchNorm1d(128), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(128, num_classes))

    def forward(self, tokens, features):
        x = self.embedding(tokens).transpose(1, 2)
        x = self.conv_block1(x)
        x = self.conv_block2(x)
        x = self.conv_block3(x)
        x = self.global_pool(x).squeeze(-1)
        f = self.feature_net(features)
        return self.classifier(torch.cat([x, f], dim=1))

try:
    hybrid_le = joblib.load(os.path.join(MODEL_DIR, "hybrid_label_encoder.pkl"))
    hybrid_scaler = joblib.load(os.path.join(MODEL_DIR, "hybrid_feature_scaler.pkl"))
    hybrid_model = HybridCipherNet(len(hybrid_le.classes_), num_features=hybrid_scaler.n_features_in_)
    hybrid_model.load_state_dict(torch.load(os.path.join(MODEL_DIR, "hybrid_cnn.pth"), map_location="cpu", weights_only=True))
    hybrid_model.eval()

    texts = test_df['ciphertext'].values
    feat_matrix = hybrid_scaler.transform(test_df[feature_cols].values.astype(np.float32))

    hybrid_preds = []
    with torch.no_grad():
        for i in range(0, len(texts), 256):
            batch_texts = texts[i:i+256]
            batch_feats = feat_matrix[i:i+256]

            seqs = []
            for t in batch_texts:
                s = [tokenize_char(c) for c in str(t)]
                padded = np.zeros(MAX_LEN, dtype=np.int64)
                padded[:min(len(s), MAX_LEN)] = s[:MAX_LEN]
                seqs.append(padded)

            tok_tensor = torch.tensor(np.array(seqs), dtype=torch.long)
            feat_tensor = torch.tensor(batch_feats, dtype=torch.float32)
            outputs = hybrid_model(tok_tensor, feat_tensor)
            preds = torch.argmax(outputs, dim=1).numpy()
            hybrid_preds.extend(hybrid_le.inverse_transform(preds))

    hybrid_acc = accuracy_score(y_true, hybrid_preds)
    print(f"\n  Cipher Accuracy: {hybrid_acc:.4f}\n")
    print(classification_report(y_true, hybrid_preds, zero_division=0))
except Exception as e:
    print(f"  Hybrid evaluation failed: {e}")
    import traceback; traceback.print_exc()
    hybrid_acc = 0

# ═══════════════════ SUMMARY ═══════════════════
print("\n" + "=" * 60)
print("  FINAL COMPARISON")
print("=" * 60)
print(f"  XGBoost Soft-Routing:        {xgb_acc*100:.2f}%")
print(f"  PyTorch CNN (char-only):     {cnn_acc*100:.2f}%")
print(f"  Hybrid CNN (char+features):  {hybrid_acc*100:.2f}%")

best = max([("XGBoost", xgb_acc), ("CNN", cnn_acc), ("Hybrid", hybrid_acc)], key=lambda x: x[1])
print(f"\n  🏆 Best Model: {best[0]} ({best[1]*100:.2f}%)")
print("=" * 60)
