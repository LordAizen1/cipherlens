# CipherLens — Model Evaluation Report

**Date:** March 31, 2026  
**Authors:** Md Kaif (2022289), Maulik, Sweta, Dhruv Verma  
**Course:** BTP Spring 2026, IIIT Delhi  
**Advisor:** Prof. Ravi

---

## 1. Project Overview

CipherLens is a classical cipher identification system that uses machine learning to predict the encryption algorithm used on a given ciphertext. The system supports **22 cipher types** across **7 cryptographic families**.

### Supported Ciphers

| Family | Ciphers |
|--------|---------|
| Monoalphabetic Substitution | Caesar, Affine, Atbash |
| Polyalphabetic Substitution | Vigenere, Autokey, Beaufort, Porta |
| Transposition | Columnar |
| Polygraphic Substitution | Playfair, Hill, Four-Square |
| Fractionating | Bifid, Trifid, ADFGX, ADFGVX, Nihilist, Polybius |
| Modern Block | TEA, XTEA, Lucifer, LOKI, MISTY1 |
| Numeric | (Polybius — classified under Fractionating in dataset) |

---

## 2. Dataset

### Source
- **File:** `cipher_MASTER_FULL_V3.csv`
- **Size:** 329,816 samples, 18 columns
- **Features (14):** length, entropy, compression, bigram_entropy, trigram_entropy, uniformity, unique_ratio, transition_var, run_length_mean, run_length_var, ioc, ioc_variance, digit_ratio, alpha_ratio

### Class Distribution
Highly balanced — ~15,000 samples per cipher:
- 20 ciphers at exactly 15,000 samples
- Affine: 14,950
- Columnar: 14,866

### Dataset Issues Found

1. **Not shuffled** — ciphers were grouped sequentially (all Caesar first, then all Atbash, etc.). This caused ordering bias during train/test split, where the model never saw some ciphers during training. Fixed by shuffling with `random_state=42`.

2. **Feature count mismatch** — dataset has 14 features but original training script (`train.py`) only used 12 (missing `digit_ratio` and `alpha_ratio`). This caused feature index misalignment at inference — the model was interpreting features in wrong positions. Fixed by updating train.py and model_inference.py to use all 14 features.

3. **Ciphertext length** — samples range from ~64 to ~200 characters. Shorter samples (<100 chars) produce unreliable statistical features like IoC, leading to misclassifications.

4. **Transposition family** — only has 1 cipher (columnar), making family-level learning weak for this category.

---

## 3. Models

### 3.1 XGBoost Hierarchical (Soft-Routing)

**Architecture:** Two-stage pipeline
- Stage 1: Family classifier (XGBoost) — predicts cipher family
- Stage 2: Per-family cipher classifier (XGBoost) — predicts specific cipher within family
- Final confidence = family_confidence × cipher_confidence (soft-routing)

**Hyperparameters:**
- Family classifier: 700 estimators, max_depth=10, learning_rate=0.03
- Cipher classifiers: 600 estimators, max_depth=8, learning_rate=0.05
- Both: subsample=0.9, colsample_bytree=0.9, tree_method="hist"

**Training:** ~330k samples, 14 statistical features, CPU-based

**Accuracy:** 76% (reported)

**Strengths:**
- Fast inference (~650ms including model loading)
- Interpretable — provides feature importance scores (IoC is most important at 42.6%)
- Good at family-level classification for modern block ciphers

**Weaknesses:**
- Cannot read character-level patterns — relies entirely on statistical features
- Overconfident when wrong (e.g., 100% confidence on Polybius → misclassified as modern)
- Soft-routing multiplies probabilities, which can amplify or suppress confidence incorrectly

### 3.2 CNN Deep Learning

**Architecture:** Character-level 1D CNN
- Embedding: 27 vocab (PAD + A-Z), 32-dim
- 3 convolutional layers (64→128→256 channels, kernels 3/5/7)
- MaxPool after each conv layer
- FC layers: 16384 → 512 → num_classes
- Dropout: 0.5

**Training:**
- 10 epochs, batch_size=512, Adam optimizer (lr=0.001)
- 80/20 train/val split
- Trained on IIIT Delhi Precision cluster (H100 MIG GPU, ~21s/epoch)

**Validation Accuracy:** 71.4%

| Epoch | Train Loss | Train Acc | Val Loss | Val Acc |
|-------|-----------|-----------|----------|---------|
| 1     | 1.1847    | 0.5216    | 0.9320   | 0.6093  |
| 5     | 0.6998    | 0.7006    | 0.6878   | 0.7032  |
| 10    | 0.5674    | 0.7491    | 0.6865   | 0.7141  |

**Strengths:**
- Reads raw character sequences — can distinguish ciphers by character patterns
- Only model that correctly identifies Polybius (digit-pair patterns)
- No feature engineering needed

**Weaknesses:**
- Lower accuracy than Hybrid
- Ignores non-alphabetic characters (only maps A-Z)
- Val loss starts plateauing around epoch 7 — slight overfitting by epoch 10

### 3.3 Hybrid CNN (Character + Statistical Features)

**Architecture:** Dual-input network
- Branch A: Character-level CNN (expanded vocab: 39 tokens — A-Z, 0-9, space, other)
  - 3 conv blocks with BatchNorm (128→256→512 channels)
  - AdaptiveAvgPool → 512-dim vector
- Branch B: Feature MLP (14 features → 64 → 64 with BatchNorm + Dropout)
- Fusion: concatenate (512 + 64 = 576) → classifier head (256 → 128 → num_classes)
- Label smoothing: 0.1, gradient clipping: max_norm=1.0

**Training:**
- 15 epochs, batch_size=256, AdamW (lr=0.001, weight_decay=1e-4)
- OneCycleLR scheduler (max_lr=0.003)
- Features normalized with StandardScaler
- Total parameters: 1,678,678
- Trained on Precision cluster (~36s/epoch)

**Best Validation Accuracy:** 82.24% (epoch 13)

| Epoch | Train Loss | Train Acc | Val Loss | Val Acc |
|-------|-----------|-----------|----------|---------|
| 1     | 1.4467    | 0.6665    | 1.1335   | 0.7564  |
| 6     | 0.9982    | 0.8173    | 0.9963   | 0.8087  |
| 9     | 0.9453    | 0.8384    | 0.9607   | 0.8211  |
| 13    | 0.8364    | 0.8793    | 1.0083   | 0.8224  |
| 15    | 0.8057    | 0.8909    | 1.0312   | 0.8189  |

**Note:** Previously reported accuracy of 87% was inflated due to unshuffled dataset causing train/val data leakage. 82.24% on properly shuffled data is the honest number.

**Strengths:**
- Best overall accuracy
- Handles both alphabetic and numeric ciphers (expanded vocabulary)
- Combines character pattern recognition with statistical analysis
- Feature importance via input perturbation

**Weaknesses:**
- Slower inference than XGBoost (feature extraction + CNN forward pass)
- Still confuses mathematically similar ciphers (Vigenere/Beaufort, Hill/Trifid)

---

## 4. Comparative Test Results

### Test on Real Dataset Samples (22 ciphers, Hybrid CNN)

**20/22 correct (90.9%)**

| Cipher | Predicted | Confidence | Correct |
|--------|-----------|------------|---------|
| ADFGVX | adfgvx | 91.6% | Yes |
| ADFGX | adfgx | 92.1% | Yes |
| Affine | affine | 92.7% | Yes |
| Atbash | atbash | 91.7% | Yes |
| Autokey | autokey | 93.0% | Yes |
| Beaufort | beaufort | 29.3% | Yes |
| Bifid | bifid | 92.9% | Yes |
| Caesar | caesar | 86.8% | Yes |
| Columnar | columnar | 92.7% | Yes |
| Four-Square | foursquare | 91.5% | Yes |
| **Hill** | **trifid** | **46.9%** | **No** |
| LOKI | loki | 90.3% | Yes |
| Lucifer | lucifer | 91.8% | Yes |
| MISTY1 | misty1 | 91.9% | Yes |
| Nihilist | nihilist | 89.6% | Yes |
| Playfair | playfair | 91.6% | Yes |
| Polybius | polybius | 91.8% | Yes |
| Porta | porta | 91.1% | Yes |
| TEA | tea | 92.1% | Yes |
| Trifid | trifid | 47.5% | Yes |
| **Vigenere** | **beaufort** | **45.6%** | **No** |
| XTEA | xtea | 91.4% | Yes |

### Cross-Model Comparison (Hand-crafted test inputs)

| Input | XGBoost | DL CNN | Hybrid |
|-------|---------|--------|--------|
| Caesar | caesar (44%) | caesar (74%) | caesar (86%) |
| Caesar ROT3 | affine (37%) | caesar (82%) | caesar (89%) |
| Caesar ROT13 | caesar (33%) | caesar (53%) | caesar (89%) |
| Vigenere | caesar (37%) | affine (70%) | trifid (35%) |
| Playfair | bifid (27%) | caesar (55%) | affine (88%) |
| Polybius | lucifer (96%) | polybius (51%) | nihilist (69%) |
| AES hex | tea (44%) | tea (44%) | trifid (20%) |

**Key insight:** No single model dominates across all cipher types. Hybrid is best overall, DL is best for numeric patterns, XGBoost is best for family-level classification of modern ciphers.

---

## 5. Shortcomings & Known Issues

### Model Limitations

1. **Vigenere / Beaufort / Porta confusion** — These three polyalphabetic ciphers are mathematically near-identical (Beaufort is Vigenere with subtraction, Porta uses 13 alphabets vs 26). Statistical features and character patterns are virtually indistinguishable. The model correctly identifies the *family* (polyalphabetic) but cannot reliably distinguish the specific cipher.

2. **Hill / Trifid confusion** — Both produce heavily scrambled alphabetic output with similar entropy and frequency distributions. Hill uses matrix multiplication while Trifid uses 3D coordinate fractionation, but the resulting statistics overlap significantly.

3. **Short input degradation** — Inputs under 100 characters produce unreliable statistical features (IoC, bigram entropy, etc.), leading to low-confidence or incorrect predictions. This is inherent to statistical cryptanalysis.

4. **XGBoost overconfidence** — The soft-routing architecture can produce high confidence on wrong predictions (e.g., 100% for Polybius → classified as modern cipher) when the family classifier is very certain but the within-family classifier picks incorrectly.

5. **Transposition underrepresentation** — Only 1 cipher (Columnar) in the transposition family. The model cannot learn general transposition patterns. Rail Fence, Route cipher, and Double Transposition are not in the dataset.

### Dataset Limitations

1. **No key diversity metadata** — We cannot verify that training samples use diverse keys. If most Caesar samples use similar shifts, the model learns specific letter mappings rather than general monoalphabetic patterns.

2. **Fixed ciphertext length range** — Training samples are 64-200 chars. Very long (1000+) or very short (<50) inputs at inference time are out-of-distribution.

3. **No noise/corruption handling** — Real-world ciphertext may have transcription errors, mixed case, or partial text. The model has no robustness to such noise.

4. **Missing cipher types** — Rail Fence, Enigma, RC4, AES, DES, RSA, and many other classical/modern ciphers are not represented.

### Frontend / UX Limitations

1. **Example dropdown shows cipher name** — Users can see the expected answer before analyzing, which doesn't reflect real-world usage.

2. **No batch processing** — Users must paste one ciphertext at a time.

3. **No explanation of prediction** — Beyond confidence scores and feature values, there's no human-readable explanation of *why* a particular cipher was predicted.

---

## 6. Recommendations for Future Work

1. **Dataset improvements:**
   - Increase minimum ciphertext length to 200+ characters
   - Add more transposition ciphers (Rail Fence, Route, Double Columnar)
   - Ensure key diversity (random keys per sample)
   - Add 500k+ samples for better generalization

2. **Model improvements:**
   - Add Kasiski test score as a feature (specific to Vigenere detection)
   - Add per-period IoC features for polyalphabetic discrimination
   - Ensemble all 3 models with a meta-classifier
   - Train with curriculum learning (easy ciphers first, confusing pairs later)

3. **Evaluation:**
   - Compute per-class precision/recall/F1 on a held-out test set
   - Compute confusion matrix to identify systematic misclassification patterns
   - Test on ciphertexts from external sources (not from the training pipeline)

---

## 7. Training Infrastructure

All models were trained on the **IIIT Delhi Precision cluster**:
- **Node:** gpu01 (2x NVIDIA H100 80GB)
- **Partition:** short queue with MIG GPU (3g.40gb slice)
- **Account:** ravi
- **Environment:** Miniconda, Python 3.12, PyTorch 2.4.0+cu124, XGBoost, scikit-learn

| Model | Training Time | GPU | Epochs |
|-------|--------------|-----|--------|
| XGBoost (all stages) | ~2 min | CPU only | N/A |
| CNN Deep Learning | ~3.5 min | H100 MIG | 10 |
| Hybrid CNN | ~9 min | H100 MIG | 15 |

---

## 8. Tech Stack

- **Frontend:** Next.js 16, React 19, Tailwind CSS, shadcn/ui, Framer Motion, Magic UI, Zustand
- **Backend:** FastAPI, Python 3.12, PyTorch, XGBoost, scikit-learn
- **Deployment:** Docker Compose (planned), configurable CORS
- **Repository:** https://github.com/LordAizen1/cipherlens
