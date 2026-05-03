import os
import time
import numpy as np
import torch
import torch.nn as nn
import joblib

from app.schemas import CipherPrediction, FeatureImportance, FeatureSet

MAX_LEN = 512
VOCAB_SIZE = 27

class CipherCNN(nn.Module):
    def __init__(self, num_classes):
        super(CipherCNN, self).__init__()
        self.embedding = nn.Embedding(num_embeddings=VOCAB_SIZE, embedding_dim=32, padding_idx=0)
        self.conv1 = nn.Conv1d(in_channels=32, out_channels=64, kernel_size=3, padding=1)
        self.relu1 = nn.ReLU()
        self.pool1 = nn.MaxPool1d(kernel_size=2)
        self.conv2 = nn.Conv1d(in_channels=64, out_channels=128, kernel_size=5, padding=2)
        self.relu2 = nn.ReLU()
        self.pool2 = nn.MaxPool1d(kernel_size=2)
        self.conv3 = nn.Conv1d(in_channels=128, out_channels=256, kernel_size=7, padding=3)
        self.relu3 = nn.ReLU()
        self.pool3 = nn.MaxPool1d(kernel_size=2)
        self.flatten = nn.Flatten()
        self.fc1 = nn.Linear(256 * 64, 512)
        self.dropout = nn.Dropout(0.5)
        self.fc2 = nn.Linear(512, num_classes)
        
    def forward(self, x):
        x = self.embedding(x)
        x = x.transpose(1, 2)
        x = self.pool1(self.relu1(self.conv1(x)))
        x = self.pool2(self.relu2(self.conv2(x)))
        x = self.pool3(self.relu3(self.conv3(x)))
        x = self.flatten(x)
        x = self.dropout(torch.relu(self.fc1(x)))
        x = self.fc2(x)
        return x

class DeepLearningCipherModel:
    def __init__(self, model_dir: str):
        self.model_dir = model_dir
        self.device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
        
        le_path = os.path.join(model_dir, "dl_cipher_label_encoder.pkl")
        model_path = os.path.join(model_dir, "cipher_cnn.pth")
        
        self.is_loaded = False
        if os.path.exists(le_path) and os.path.exists(model_path):
            self.le = joblib.load(le_path)
            num_classes = len(self.le.classes_)
            
            self.model = CipherCNN(num_classes)
            self.model.load_state_dict(torch.load(model_path, map_location=self.device, weights_only=True))
            self.model.to(self.device)
            self.model.eval()
            self.is_loaded = True

    def predict(self, ciphertext: str, features: FeatureSet, model_type: str) -> tuple[list[CipherPrediction], list[FeatureImportance], float]:
        start = time.perf_counter()

        if not self.is_loaded:
             return [CipherPrediction(cipher_name="DL Model Not Found", cipher_family="Unknown", confidence=1.0)], [], 0.0
             
        # Tokenize purely from raw ciphertext
        seq = [ord(c) - 64 for c in ciphertext.upper() if 65 <= ord(c) <= 90]
        if len(seq) > MAX_LEN:
            seq = seq[:MAX_LEN]
            
        padded_seq = np.zeros(MAX_LEN, dtype=np.int64)
        padded_seq[:len(seq)] = seq
        
        input_tensor = torch.tensor([padded_seq], dtype=torch.long).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(input_tensor)
            probs = torch.softmax(outputs, dim=1)[0].cpu().numpy()
            
        predictions = []
        for i, c_name in enumerate(self.le.classes_):
            # Deep Learning infers the exact cipher directly. We don't have a family hierarchy embedded here, 
            # but we can look it up or just return the cipher name.
            predictions.append(
                CipherPrediction(
                    cipher_name=c_name,
                    cipher_family="deep_learning_inferred",
                    confidence=round(float(probs[i]), 4)
                )
            )

        predictions.sort(key=lambda p: p.confidence, reverse=True)
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        
        # DL models don't have classical tabular feature importance
        importances = []
        
        return predictions, importances, elapsed_ms

_cached_dl_model = None

def get_dl_model(model_dir: str = None) -> DeepLearningCipherModel:
    global _cached_dl_model
    if _cached_dl_model is not None:
        return _cached_dl_model

    if model_dir is None:
        # Find models folder relative to this file: ../models
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_dir = os.path.join(os.path.dirname(current_dir), "models")

    _cached_dl_model = DeepLearningCipherModel(model_dir=model_dir)
    return _cached_dl_model
