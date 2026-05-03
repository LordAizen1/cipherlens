import os
import time
import numpy as np
import torch
import torch.nn as nn
import joblib

from app.schemas import CipherPrediction, FeatureImportance, FeatureSet

MAX_LEN = 1024
VOCAB_SIZE = 39  # PAD + A-Z + 0-9 + SPACE + OTHER


def tokenize_char(c):
    c = c.upper()
    if 'A' <= c <= 'Z':
        return ord(c) - 64
    elif '0' <= c <= '9':
        return ord(c) - 48 + 27
    elif c == ' ':
        return 37
    else:
        return 38


class HybridCipherNet(nn.Module):
    def __init__(self, num_classes, num_features=14):
        super().__init__()
        self.embedding = nn.Embedding(VOCAB_SIZE, 64, padding_idx=0)

        self.conv_block1 = nn.Sequential(
            nn.Conv1d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm1d(128), nn.ReLU(),
            nn.Conv1d(128, 128, kernel_size=3, padding=1),
            nn.BatchNorm1d(128), nn.ReLU(),
            nn.MaxPool1d(2),
        )
        self.conv_block2 = nn.Sequential(
            nn.Conv1d(128, 256, kernel_size=5, padding=2),
            nn.BatchNorm1d(256), nn.ReLU(),
            nn.Conv1d(256, 256, kernel_size=5, padding=2),
            nn.BatchNorm1d(256), nn.ReLU(),
            nn.MaxPool1d(2),
        )
        self.conv_block3 = nn.Sequential(
            nn.Conv1d(256, 512, kernel_size=7, padding=3),
            nn.BatchNorm1d(512), nn.ReLU(),
            nn.MaxPool1d(2),
        )
        self.global_pool = nn.AdaptiveAvgPool1d(1)

        self.feature_net = nn.Sequential(
            nn.Linear(num_features, 64), nn.BatchNorm1d(64), nn.ReLU(), nn.Dropout(0.2),
            nn.Linear(64, 64), nn.BatchNorm1d(64), nn.ReLU(),
        )

        self.classifier = nn.Sequential(
            nn.Linear(512 + 64, 256), nn.BatchNorm1d(256), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(256, 128), nn.BatchNorm1d(128), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(128, num_classes),
        )

    def forward(self, tokens, features):
        x = self.embedding(tokens).transpose(1, 2)
        x = self.conv_block1(x)
        x = self.conv_block2(x)
        x = self.conv_block3(x)
        x = self.global_pool(x).squeeze(-1)
        f = self.feature_net(features)
        return self.classifier(torch.cat([x, f], dim=1))


class HybridCipherModel:
    def __init__(self, model_dir: str):
        self.model_dir = model_dir
        self.device = torch.device("cpu")  # CPU for inference stability
        self.is_loaded = False

        le_path = os.path.join(model_dir, "hybrid_label_encoder.pkl")
        scaler_path = os.path.join(model_dir, "hybrid_feature_scaler.pkl")
        model_path = os.path.join(model_dir, "hybrid_cnn.pth")

        if all(os.path.exists(p) for p in [le_path, scaler_path, model_path]):
            self.le = joblib.load(le_path)
            self.scaler = joblib.load(scaler_path)
            num_classes = len(self.le.classes_)

            self.model = HybridCipherNet(num_classes, num_features=self.scaler.n_features_in_)
            self.model.load_state_dict(torch.load(model_path, map_location=self.device, weights_only=True))
            self.model.to(self.device)
            self.model.eval()
            self.is_loaded = True

    def predict(self, ciphertext: str, features: FeatureSet, model_type: str):
        start = time.perf_counter()

        if not self.is_loaded:
            return (
                [CipherPrediction(cipher_name="Hybrid Model Not Found", cipher_family="Unknown", confidence=1.0)],
                [],
                0.0,
            )

        # Tokenize
        seq = [tokenize_char(c) for c in ciphertext]
        if len(seq) > MAX_LEN:
            seq = seq[:MAX_LEN]
        padded = np.zeros(MAX_LEN, dtype=np.int64)
        padded[:len(seq)] = seq
        token_tensor = torch.tensor([padded], dtype=torch.long).to(self.device)

        # Feature vector (normalized) — 15 features matching train_hybrid.py feature_cols
        feat_arr = np.array([[
            features.length, features.entropy, features.compression,
            features.bigram_entropy, features.trigram_entropy, features.uniformity,
            features.unique_ratio, features.transition_var, features.run_length_mean,
            features.run_length_var, features.ioc, features.ioc_variance,
            features.digit_ratio, features.alpha_ratio, features.max_kasiski_ioc
        ]], dtype=np.float32)
        feat_arr = self.scaler.transform(feat_arr)
        feat_tensor = torch.tensor(feat_arr, dtype=torch.float32).to(self.device)

        with torch.no_grad():
            outputs = self.model(token_tensor, feat_tensor)
            probs = torch.softmax(outputs, dim=1)[0].cpu().numpy()
            
        top_idx = int(np.argmax(probs))
        base_conf = probs[top_idx]

        # Calculate dynamic feature importance via input perturbation
        feature_names = [
            "length", "entropy", "compression", "bigram_entropy", "trigram_entropy",
            "uniformity", "unique_ratio", "transition_var", "run_length_mean",
            "run_length_var", "ioc", "ioc_variance", "digit_ratio", "alpha_ratio",
            "max_kasiski_ioc"
        ]
        drops = []
        with torch.no_grad():
            for i in range(len(feature_names)):
                # Clone the scaled features
                pert_arr = feat_arr.copy()
                # Zeroing out a standard-scaled feature sets it to the dataset mean
                pert_arr[0, i] = 0.0  
                pert_tensor = torch.tensor(pert_arr, dtype=torch.float32).to(self.device)
                p_outputs = self.model(token_tensor, pert_tensor)
                p_probs = torch.softmax(p_outputs, dim=1)[0].cpu().numpy()
                
                # How much did confidence for the top prediction drop?
                drop = base_conf - p_probs[top_idx]
                drops.append(max(0.0, float(drop)))
                
        # Normalize drops to sum to 1.0
        total_drop = sum(drops)
        if total_drop < 1e-6:
            norm_drops = [1.0 / len(feature_names)] * len(feature_names)
        else:
            norm_drops = [d / total_drop for d in drops]

        importances = [
            FeatureImportance(feature_name=feature_names[i], importance_score=round(norm_drops[i], 4))
            for i in range(len(feature_names))
        ]

        CIPHER_FAMILY_MAP = {
            'caesar': 'mono', 'affine': 'mono', 'atbash': 'mono',
            'vigenere': 'poly', 'autokey': 'poly', 'beaufort': 'poly', 'porta': 'poly',
            'columnar': 'transposition',
            'playfair': 'polygraphic', 'hill': 'polygraphic', 'foursquare': 'polygraphic',
            'bifid': 'fractionating', 'trifid': 'fractionating', 'adfgx': 'fractionating',
            'adfgvx': 'fractionating', 'nihilist': 'fractionating', 'polybius': 'fractionating',
            'tea': 'modern', 'xtea': 'modern', 'lucifer': 'modern', 'loki': 'modern', 'misty1': 'modern',
        }

        predictions = []
        for i, c_name in enumerate(self.le.classes_):
            family = CIPHER_FAMILY_MAP.get(c_name, 'unknown')
            predictions.append(
                CipherPrediction(
                    cipher_name=c_name,
                    cipher_family=family,
                    confidence=round(float(probs[i]), 4),
                )
            )

        predictions.sort(key=lambda p: p.confidence, reverse=True)
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)

        return predictions, importances, elapsed_ms


_cached_hybrid = None


def get_hybrid_model(model_dir: str = None) -> HybridCipherModel:
    global _cached_hybrid
    if _cached_hybrid is not None:
        return _cached_hybrid
    
    if model_dir is None:
        # Find models folder relative to this file: ../models
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_dir = os.path.join(os.path.dirname(current_dir), "models")
        
    _cached_hybrid = HybridCipherModel(model_dir=model_dir)
    return _cached_hybrid
