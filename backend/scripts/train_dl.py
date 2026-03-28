import os
import time
import argparse
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import LabelEncoder
import joblib

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, '..', '..', 'cipher_MASTER_FULL_V2.csv')
MODEL_DIR = os.path.join(BASE_DIR, 'app', 'models')

MAX_LEN = 512
VOCAB_SIZE = 27  # 0 for PAD, 1-26 for A-Z

class CipherTextDataset(Dataset):
    def __init__(self, texts, labels):
        self.texts = list(texts)
        self.labels = labels
        
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = self.texts[idx]
        label = self.labels[idx]
        
        # Convert chars to int (A=1, B=2...)
        # Ignore non-alphabetic
        seq = [ord(c) - 64 for c in text.upper() if 65 <= ord(c) <= 90]
        
        # Truncate
        if len(seq) > MAX_LEN:
            seq = seq[:MAX_LEN]
            
        # Pad with 0
        padded_seq = np.zeros(MAX_LEN, dtype=np.int64)
        padded_seq[:len(seq)] = seq
        
        return torch.tensor(padded_seq, dtype=torch.long), torch.tensor(label, dtype=torch.long)

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
        
        # 512 -> pool 256 -> pool 128 -> pool 64. 256 channels * 64 = 16384
        self.fc1 = nn.Linear(256 * 64, 512)
        self.dropout = nn.Dropout(0.5)
        self.fc2 = nn.Linear(512, num_classes)
        
    def forward(self, x):
        # x: (batch, seq_len)
        x = self.embedding(x) # (batch, seq_len, embed_dim)
        x = x.transpose(1, 2) # (batch, embed_dim, seq_len) for Conv1d
        
        x = self.pool1(self.relu1(self.conv1(x)))
        x = self.pool2(self.relu2(self.conv2(x)))
        x = self.pool3(self.relu3(self.conv3(x)))
        
        x = self.flatten(x)
        x = self.dropout(torch.relu(self.fc1(x)))
        x = self.fc2(x)
        return x

def train_dl(quick_mode=False):
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)

    print(f"Loading raw data from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    
    if quick_mode:
        print("QUICK MODE ACTIVE: Truncating dataset to 2200 samples for rapid prototyping.")
        # Ensure stratify by taking 100 per class
        df = df.groupby('cipher').head(100).sample(frac=1).reset_index(drop=True)
        epochs = 2
    else:
        epochs = 10
        
    texts = df['ciphertext']
    y_cipher = df['cipher']
    
    # Encode Target Labels
    le = LabelEncoder()
    y_encoded = le.fit_transform(y_cipher)
    
    joblib.dump(le, os.path.join(MODEL_DIR, "dl_cipher_label_encoder.pkl"))
    
    dataset = CipherTextDataset(texts, y_encoded)
    
    # Split 80/20 train/val manually to observe loss
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size])
    
    batch_size = 512
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
    print(f"Training on device: {device}")
    
    num_classes = len(le.classes_)
    model = CipherCNN(num_classes).to(device)
    
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    print(f"Starting Training for {epochs} Epochs...")
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        correct = 0
        total = 0
        
        start_time = time.time()
        for batch_X, batch_y in train_loader:
            batch_X, batch_y = batch_X.to(device), batch_y.to(device)
            
            optimizer.zero_grad()
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item() * batch_X.size(0)
            _, predicted = torch.max(outputs, 1)
            total += batch_y.size(0)
            correct += (predicted == batch_y).sum().item()
            
        train_acc = correct / total
        train_loss = total_loss / total
        
        model.eval()
        val_loss = 0
        val_correct = 0
        val_total = 0
        with torch.no_grad():
            for batch_X, batch_y in val_loader:
                batch_X, batch_y = batch_X.to(device), batch_y.to(device)
                outputs = model(batch_X)
                loss = criterion(outputs, batch_y)
                val_loss += loss.item() * batch_X.size(0)
                
                _, predicted = torch.max(outputs, 1)
                val_total += batch_y.size(0)
                val_correct += (predicted == batch_y).sum().item()
                
        val_acc = val_correct / val_total
        val_loss = val_loss / val_total
        
        elapsed = time.time() - start_time
        print(f"Epoch {epoch+1}/{epochs} [{elapsed:.1f}s] - Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f} - Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}")
        
    torch.save(model.state_dict(), os.path.join(MODEL_DIR, "cipher_cnn.pth"))
    print("\nPyTorch Model saved to app/models/cipher_cnn.pth!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true", help="Run quick train mode on small sample")
    args = parser.parse_args()
    
    train_dl(quick_mode=args.quick)
