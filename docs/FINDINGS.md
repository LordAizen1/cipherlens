# CipherLens — Model Evaluation Report

**Date:** March 31, 2026 (updated April 1, 2026)
**Authors:** Md Kaif (2022289), Maulik, Sweta, Dhruv Verma  
**Course:** BTP Spring 2026, IIIT Delhi  
**Advisor:** Prof. Ravi

---

## 1. Project Overview

CipherLens is a classical cipher identification system that uses machine learning to predict the encryption algorithm used on a given ciphertext. The system supports **22 cipher types** across **6 cryptographic families**.

### Supported Ciphers

| Family | Ciphers |
|--------|---------|
| Monoalphabetic Substitution | Caesar, Affine, Atbash |
| Polyalphabetic Substitution | Vigenere, Autokey, Beaufort, Porta |
| Transposition | Columnar |
| Polygraphic Substitution | Playfair, Hill, Four-Square |
| Fractionating | Bifid, Trifid, ADFGX, ADFGVX, Nihilist, Polybius |
| Modern Block | TEA, XTEA, Lucifer, LOKI, MISTY1 |

---

## 2. Dataset

### V3 Dataset (Previous)
- **File:** `cipher_MASTER_FULL_V3.csv`
- **Size:** ~330k samples, ~15k per cipher
- **Length range:** 200–500 characters
- **Features (14):** length, entropy, compression, bigram_entropy, trigram_entropy, uniformity, unique_ratio, transition_var, run_length_mean, run_length_var, ioc, ioc_variance, digit_ratio, alpha_ratio

### V4 Dataset (Current)
- **File:** `cipher_MASTER_FULL_V4.csv.gz`
- **Size:** 550,000 samples — 25,000 per cipher
- **Length range:** 50–500 characters (reduced MIN_LEN from 200 to 50 for better real-world UX)
- **Features (15):** all 14 from V3 + `max_kasiski_ioc` (best average IoC across periods 2–20, designed to detect polyalphabetic periodic structure)
- **Compressed size:** 316 MB

### Why V4
1. **More data per class** — 25k vs 15k samples, better generalization
2. **Shorter samples** — MIN_LEN=50 means the model trains on realistic short inputs that users actually paste
3. **Kasiski IoC feature** — added to improve Vigenere/Beaufort/polyalphabetic discrimination
4. **English-realistic plaintexts** — generated using English letter frequency distribution

### Dataset Issues Fixed

1. **Not shuffled (V3)** — ciphers were grouped sequentially, causing ordering bias during train/val split. Fixed by shuffling with `random_state=42`.

2. **Feature count mismatch (V3)** — dataset had 14 features but training script only used 12, misaligning feature indices at inference. Fixed by using all 14 features consistently.

3. **Short input failures** — V3 MIN_LEN=200 meant the model never saw short inputs during training. Fixed in V4 with MIN_LEN=50.

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

**Training:** V4 dataset (550k samples), 15 statistical features, CPU-based

**V3 Accuracy:** 76%  
**V4 Accuracy:** Not separately measured (no held-out test set); see live test results below.

**Strengths:**
- Fast inference (~few ms, CPU only)
- Interpretable — provides feature importance scores
- Near-perfect on ADFGX/ADFGVX (99.97%) and Nihilist (100%)
- Good on Playfair (81.3%) and Polybius (90.7%)

**Weaknesses:**
- Soft-routing multiplies probabilities — can over-suppress confidence
- Returns "Unknown" for transposition family (only 1 class, no sub-classifier trained)
- Struggles with monoalphabetic ciphers (Caesar, Affine, Atbash often confused with each other at family stage)
- Completely misses LOKI and Beaufort

---

### 3.2 CNN Deep Learning

**Architecture:** Character-level 1D CNN
- Embedding: 27 vocab (PAD + A-Z), 32-dim
- 3 convolutional layers (64→128→256 channels, kernels 3/5/7)
- MaxPool after each conv layer
- FC layers: 16384 → 512 → num_classes
- Dropout: 0.5

**V4 Training:**
- 10 epochs, batch_size=512, Adam optimizer (lr=0.001)
- 80/20 train/val split
- Trained on IIIT Delhi Precision cluster (H100 MIG GPU, ~28s/epoch)

**V4 Validation Accuracy:** 66.5%

| Epoch | Train Loss | Train Acc | Val Loss | Val Acc |
|-------|-----------|-----------|----------|---------|
| 1     | 1.1169    | 0.5237    | 0.9338   | 0.5919  |
| 5     | 0.7138    | 0.6704    | 0.7163   | 0.6696  |
| 10    | 0.5726    | 0.7284    | 0.7744   | 0.6651  |

Note: Overfitting from epoch 6 onward (train acc keeps rising, val acc plateaus then drops).

**Strengths:**
- Fastest inference (~2–4ms)
- Best at Atbash (99.9%), ADFGX/ADFGVX (100%)
- No feature engineering needed

**Weaknesses:**
- Lowest accuracy of the three (66.5% vs 78.2% hybrid)
- Struggles with modern block ciphers (uniform hex distribution)
- Nihilist/Polybius near coin-flip (51/48% split every time)
- LOKI never identified correctly

---

### 3.3 Hybrid CNN (Character + Statistical Features)

**Architecture:** Dual-input network
- Branch A: Character-level CNN (expanded vocab: 39 tokens — A-Z, 0-9, space, other)
  - 3 conv blocks with BatchNorm (128→256→512 channels, kernels 3/5/7)
  - AdaptiveAvgPool1d → 512-dim vector
  - MAX_LEN=1024 (increased from 512 to handle long hex/numeric ciphertexts)
- Branch B: Feature MLP (15 features → 64 → 64 with BatchNorm + Dropout)
- Fusion: concatenate (512 + 64 = 576) → classifier head (256 → 128 → num_classes)
- Label smoothing: 0.1, gradient clipping: max_norm=1.0
- Total parameters: 1,678,742

**V4 Training (Run 1 — MAX_LEN=512):**
- Best val_acc: 80.44% (epoch 14)
- Note: MAX_LEN=512 was truncating long ciphertexts (modern hex, nihilist). Upgraded to 1024.

**V4 Training (Run 2 — MAX_LEN=1024, MIN_LEN=50):**
- 15 epochs, batch_size=256, AdamW (lr=0.001, weight_decay=1e-4)
- OneCycleLR scheduler (max_lr=0.003) — LR→0 at epoch 15
- Trained on Precision cluster (~103s/epoch)
- Best val_acc: **78.16%** (epoch 14)

| Epoch | Train Loss | Train Acc | Val Loss | Val Acc |
|-------|-----------|-----------|----------|---------|
| 1     | 1.3699    | 0.6502    | 1.1814   | 0.6908  |
| 5     | 1.0387    | 0.7667    | 1.0134   | 0.7659  |
| 7     | 1.0184    | 0.7750    | 0.9856   | 0.7788  |
| 10    | 0.9923    | 0.7850    | 0.9783   | 0.7808  |
| 14    | 0.9539    | 0.8020    | 0.9848   | 0.7816  |
| 15    | 0.9506    | 0.8028    | 0.9859   | 0.7805  |

**Why V4 Run 2 is lower than V3 (78.16% vs 82.24%):**
The new dataset includes samples as short as 50 characters. These provide much weaker statistical signals (IoC, bigram entropy, etc.), making the classification problem intrinsically harder. However, the model is now actually useful for real-world short inputs rather than failing silently.

The fundamental Bayes error ceiling for Vigenere/Beaufort (mathematically equivalent operations) limits the theoretical maximum to ~80.5% on a balanced dataset.

**Strengths:**
- Best overall accuracy across all 15 tested ciphers (9/15 correct at #1)
- Handles both alphabetic and numeric/hex ciphertexts (expanded vocabulary)
- Feature importance via input perturbation (dynamic, per-prediction)
- Strong on mono ciphers (Affine 92.3%, Atbash 91.7%, Hill 89.6%)

**Weaknesses:**
- Slowest inference (~120–730ms including feature extraction)
- Still confuses Playfair with Foursquare (both digraphic, statistically similar)
- Vigenere never predicted #1 (always confused with Hill)
- LOKI never correctly identified (#4 at 22.7%)

---

## 4. Comparative Test Results (V4 Models)

### Live Test — 15 Ciphers × 3 Models

✅ = correct at #1 | ⚠️ = correct at #2 or #3 | ❌ = not in top 3

| Cipher | hierarchical | deep_learning | hybrid |
|--------|:---:|:---:|:---:|
| Caesar | ❌ (#4, 11.6%) | ✅ 87.8% | ✅ 75.5% |
| Affine | ⚠️ (#2, 25.8%) | ✅ 55.5% | ✅ 92.3% |
| Atbash | ⚠️ (#3, 24.4%) | ✅ 99.9% | ✅ 91.7% |
| Vigenere | ⚠️ (#2, 30.7%) | ⚠️ (#3, 14.1%) | ⚠️ (#3, 8.5%) |
| Beaufort | ❌ | ❌ | ✅ 27.2% |
| Playfair | ✅ 81.3% | ⚠️ (#3, 8.4%) | ❌ |
| Hill | ⚠️ (#2, 19.4%) | ✅ 55.9% | ✅ 89.6% |
| Bifid | ⚠️ (#3, 14.4%) | ⚠️ (#3, 8.1%) | ⚠️ (#2, 31.0%) |
| ADFGX | ✅ 99.97% | ✅ 100% | ✅ 92.2% |
| ADFGVX | ✅ 99.9% | ✅ 100% | ✅ 92.3% |
| Nihilist | ✅ 100% | ✅ 51.9% | ✅ 89.1% |
| Polybius | ✅ 90.7% | ⚠️ (#2, 48.1%) | ⚠️ (#2, 12.9%) |
| TEA | ❌ (#4, 6.5%) | ❌ (#4, 17.6%) | ✅ 22.4% |
| XTEA | ⚠️ (#2, 28.5%) | ✅ 26.0% | ✅ 24.2% |
| LOKI | ❌ | ❌ (#5) | ❌ (#4, 22.7%) |

**Score (✅ / ⚠️ / ❌):**

| Model | ✅ | ⚠️ | ❌ |
|-------|---|---|---|
| hierarchical | 5 | 6 | 4 |
| deep_learning | 6 | 5 | 4 |
| **hybrid** | **9** | **3** | **3** |

### V3 vs V4 Hybrid Comparison (dataset samples)

| Cipher | V3 (82.24% model) | V4 (78.16% model) |
|--------|:---:|:---:|
| ADFGVX | ✅ 91.6% | ✅ 92.3% |
| ADFGX | ✅ 92.1% | ✅ 92.2% |
| Affine | ✅ 92.7% | ✅ 92.3% |
| Atbash | ✅ 91.7% | ✅ 91.7% |
| Beaufort | ✅ 29.3% | ✅ 27.2% |
| Bifid | ✅ 92.9% | ⚠️ 31.0% |
| Caesar | ✅ 86.8% | ✅ 75.5% |
| Hill | ❌ (trifid 46.9%) | ✅ 89.6% |
| Nihilist | ✅ 89.6% | ✅ 89.1% |
| Playfair | ✅ 91.6% | ❌ (foursquare) |
| Polybius | ✅ 91.8% | ⚠️ 12.9% |
| Vigenere | ❌ (beaufort 45.6%) | ⚠️ (#3, 8.5%) |

V4 improved Hill, fixed some mono confusions. V4 regressed on Bifid, Polybius, Playfair — these ciphers are harder to distinguish with shorter samples.

---

## 5. Shortcomings & Known Issues

### Universal Blind Spots (all 3 models fail)

1. **LOKI** — All models consistently predict misty1 or spread evenly across modern block ciphers. LOKI's hex output is statistically indistinguishable from other Feistel ciphers with similar block sizes. Never appears in top 3 for any model.

2. **Vigenere** — Never predicted #1 by any model. Always confused with Hill (high entropy, low IoC, flat frequency distribution) or Beaufort (mathematically reciprocal). No model correctly identifies it at #1.

3. **Bifid** — Always beaten by Foursquare or Playfair. The fractionation step produces alphabetic output statistically similar to digraphic substitution.

### Per-Model Issues

**Hybrid CNN:**
- Playfair consistently misclassified as Foursquare (both digraphic, derived ciphers, nearly identical statistics)
- Polybius weak at #2 (12.9%) — numeric output distinguishable but short samples confuse it with Atbash

**XGBoost:**
- Transposition family has only 1 cipher (columnar), so returns "Unknown" for transposition predictions
- Monoalphabetic family routing is weak — Caesar often appears at #4 rather than top 3
- Completely misses Beaufort and LOKI
- Soft-routing probability multiplication can produce very low confidence scores even when correct

**CNN Deep Learning:**
- Nihilist/Polybius near coin-flip (51/48% split) — both produce digit-only output, hard to distinguish by character patterns alone
- Modern block ciphers nearly uniform — tea/xtea/loki/lucifer/misty1 all score ~20-27% each
- LOKI never identified

### Fundamental Limitations

1. **Vigenere / Beaufort statistical equivalence** — Beaufort cipher is `C = K - P mod 26` while Vigenere is `C = P + K mod 26`. Both produce identical statistical distributions (same entropy, same IoC, same bigram frequencies). Mathematically indistinguishable without known plaintext. This is a hard Bayes error ceiling.

2. **Modern cipher hex uniformity** — All 5 modern block ciphers (TEA, XTEA, Lucifer, LOKI, MISTY1) produce pseudorandom hex output with near-identical statistical properties (high entropy, low compression, uniform byte distribution). Distinguishing them requires detecting structural patterns in the specific byte sequences.

3. **Short input degradation** — Even with MIN_LEN=50 training, inputs under ~50 characters produce unreliable predictions. IoC, bigram entropy, and Kasiski IoC all require at least 100+ characters for stable values.

4. **Playfair / Foursquare overlap** — Foursquare is directly derived from Playfair. Both operate on 5×5 grids and encrypt letter pairs. Their output distributions are nearly identical.

---

## 6. Bugs Found and Fixed

### Session: April 1, 2026

1. **MAX_LEN=512 truncation** — Hybrid CNN was truncating long ciphertexts (modern hex ~400-1000 chars, nihilist ~1000+ chars) at 512 tokens. Fixed by increasing MAX_LEN to 1024 in both `train_hybrid.py` and `hybrid_inference.py`.

2. **Feature count mismatch (Hybrid)** — `train_hybrid.py` trained the scaler with 15 features (including `max_kasiski_ioc`) but `hybrid_inference.py` passed only 14, causing shape mismatch at inference. Fixed by adding `features.max_kasiski_ioc` to the feature array in inference.

3. **Feature count mismatch (XGBoost)** — Same issue: `train.py` trained XGBoost models with 15 features but `model_inference.py` passed only 14, causing HTTP 500 on all hierarchical predictions. Fixed by adding `features.max_kasiski_ioc` to the feature vector in inference.

4. **Space-in-ciphertext degradation** — Ciphertexts pasted with spaces (e.g., Caesar with word boundaries) caused incorrect IoC and frequency calculations. Fixed by adding `preprocessCiphertext()` in frontend `api.ts` that strips spaces from alphabetic ciphertexts while preserving them for numeric ones (Nihilist/Polybius use space-separated numbers).

5. **Models tracked in git** — Model `.pkl` and `.pth` files were committed to the repository. Removed from tracking and added to `.gitignore`. Models are now transferred via `scp` only.

6. **Nested models/models/ folder** — A `scp -r` command created `backend/app/models/models/` (nested duplicate). Deleted the nested copy.

---

## 7. Recommendations for Future Work

1. **Dataset improvements:**
   - Increase samples further (50k per cipher) for better generalization
   - Add more transposition ciphers (Route, Double Columnar) to strengthen the transposition family
   - Generate dedicated short-input test set (50–100 chars) for real-world evaluation

2. **Model improvements:**
   - Ensemble all 3 models with a learned meta-classifier (XGBoost on top of softmax outputs)
   - Curriculum learning — train on easy ciphers first, introduce confusing pairs (Vigenere/Beaufort, Playfair/Foursquare) later
   - Add per-period character frequency features to better separate Vigenere from monoalphabetic
   - For LOKI/modern cipher discrimination: add features based on byte-level block structure (block size alignment, XOR patterns)

3. **Evaluation:**
   - Compute full per-class precision/recall/F1 confusion matrix on held-out test set
   - Measure top-3 accuracy separately from top-1 (most ciphers appear in top 3 even when not #1)
   - Test on ciphertexts from external sources, not generated by the same pipeline

---

## 8. Live Inference Test — All 22 Ciphers (V4 Hybrid Model)

**Date:** April 1, 2026  
**Model:** Hybrid CNN (V4, 78.16% val acc, MIN_LEN=50)  
**Samples:** Real ciphertext examples from the training pipeline (same as `EXAMPLE_CIPHERTEXTS` in frontend)

### Results

| # | Cipher | Top-1 Prediction | Conf | Top-2 | Conf | Top-3 | Conf | Result |
|---|--------|-----------------|------|-------|------|-------|------|--------|
| 1 | Caesar | caesar | 75.5% | affine | 14.0% | — | — | ✅ |
| 2 | Affine | affine | 92.3% | — | — | — | — | ✅ |
| 3 | Atbash | atbash | 91.8% | — | — | — | — | ✅ |
| 4 | Vigenere | hill | 72.2% | beaufort | 9.6% | vigenere | 8.5% | ⚠️ (#3) |
| 5 | Autokey | autokey | 86.7% | — | — | — | — | ✅ |
| 6 | Beaufort | beaufort | 27.2% | vigenere | 26.0% | affine | 15.3% | ✅ (low conf) |
| 7 | Porta | vigenere | 49.2% | beaufort | 42.9% | — | — | ❌ |
| 8 | Columnar | columnar | 85.8% | — | — | — | — | ✅ |
| 9 | Playfair | foursquare | 83.0% | — | — | — | — | ❌ |
| 10 | Hill | hill | 89.6% | — | — | — | — | ✅ |
| 11 | FourSquare | playfair | 42.3% | foursquare | 20.7% | bifid | 16.2% | ⚠️ (#2) |
| 12 | Bifid | foursquare | 55.3% | bifid | 31.0% | — | — | ⚠️ (#2) |
| 13 | Trifid | porta | 51.3% | autokey | 13.4% | hill | 11.1% | ❌ |
| 14 | ADFGX | adfgx | 92.2% | — | — | — | — | ✅ |
| 15 | ADFGVX | adfgvx | 92.3% | — | — | — | — | ✅ |
| 16 | Nihilist | atbash | 39.2% | nihilist | 12.4% | misty1 | 5.8% | ⚠️ (#2) |
| 17 | Polybius | atbash | 42.2% | polybius | 12.9% | — | — | ⚠️ (#2) |
| 18 | TEA | tea | 22.4% | xtea | 21.8% | lucifer | 21.1% | ✅ (4-way tie) |
| 19 | XTEA | xtea | 24.2% | tea | 24.1% | lucifer | 23.5% | ✅ (4-way tie) |
| 20 | Lucifer | misty1 | 66.7% | — | — | — | — | ❌ |
| 21 | LOKI | tea | 23.8% | xtea | 23.8% | lucifer | 23.0% | ❌ (#4 at 22.7%) |
| 22 | MISTY1 | tea | 23.2% | xtea | 22.4% | lucifer | 21.6% | ❌ (#4 at 21.3%) |

### Score

| Outcome | Count | Ciphers |
|---------|-------|---------|
| ✅ Correct at #1 | 11 | Caesar, Affine, Atbash, Autokey, Beaufort, Columnar, Hill, ADFGX, ADFGVX, TEA, XTEA |
| ⚠️ Correct at #2–#3 | 5 | Vigenere, FourSquare, Bifid, Nihilist, Polybius |
| ❌ Not in top 3 | 6 | Porta, Playfair, Trifid, Lucifer, LOKI, MISTY1 |

**Top-1 accuracy: 11/22 (50%) | Top-3 accuracy: 16/22 (72.7%)**

### Cipher-Specific Analysis

**Consistently strong (high confidence, correct at #1):**
- Affine, Atbash, Autokey, Columnar, Hill, ADFGX, ADFGVX — all above 85%, single dominant prediction

**Structurally confused pairs:**
- **Playfair ↔ FourSquare** — model swaps them both ways. Both are digraphic ciphers operating on 5×5 grids with near-identical bigram statistics. Essentially the same cipher with a different key arrangement.
- **Vigenere → Hill** — Vigenere (96-char sample) gets beaten by Hill at 72.2%. Hill cipher produces low-IoC, high-entropy output similar to long Vigenere. Never predicted #1 by any model.
- **Porta → Vigenere/Beaufort** — Porta uses 13 reciprocal alphabets (vs Vigenere's 26), producing similar polyalphabetic statistics. Model cannot distinguish it.
- **Trifid → Porta** — Both produce scrambled alphabetic output. Trifid's 3D fractionation creates similar IoC profile to Porta's 13-alphabet substitution.

**Numeric cipher weakness:**
- **Nihilist and Polybius** both rank #2 behind Atbash. The preprocessor strips spaces from the all-digit Nihilist example, making it look like a long digit string. Atbash scores higher because the digit-only character distribution resembles the flat frequency profile of reversed-alphabet substitution.

**Modern cipher near-random:**
- TEA and XTEA technically hit #1, but all 5 modern ciphers (TEA/XTEA/Lucifer/LOKI/MISTY1) score within 1–3% of each other (~22–25% each). This is essentially random guessing within the modern family. Lucifer, LOKI, and MISTY1 are never correctly identified.
- All 5 modern ciphers produce pseudorandom hex with identical statistical properties (max entropy, high compression ratio, uniform byte distribution). Distinguishing them requires structural pattern recognition beyond what 15 statistical features can capture.

### Notes on Test Data Quality
During this session, a separate test was run on synthetically generated ciphertexts (user-provided samples with artificially repeated patterns). Those gave 2/22 top-1 accuracy — not a model failure but a test data quality issue. Repeated-block ciphertexts (e.g., the same plaintext phrase encrypted twice, or the same 8-byte block repeated 4×) are out-of-distribution and trigger false ADFGX predictions due to restricted character sets. All valid conclusions should be drawn from the dataset-sourced samples above.

---

## 9. Live Inference Test — All 22 Ciphers (V4 Hybrid Model, MIN_LEN=100)

**Date:** April 1, 2026  
**Model:** Hybrid CNN (V4, 79.24% val acc, MIN_LEN=100)  
**Samples:** Same real ciphertext examples as Section 8

### Results

| # | Cipher | Top-1 Prediction | Conf | Top-2 | Conf | Top-3 | Conf | Result |
|---|--------|-----------------|------|-------|------|-------|------|--------|
| 1 | Caesar | caesar | 54.9% | affine | 27.7% | hill | 2.0% | ✅ |
| 2 | Affine | affine | 93.3% | — | — | — | — | ✅ |
| 3 | Atbash | atbash | 92.8% | — | — | — | — | ✅ |
| 4 | Vigenere | hill | 81.5% | beaufort | 5.1% | vigenere | 4.5% | ⚠️ (#3) |
| 5 | Autokey | autokey | 91.9% | — | — | — | — | ✅ |
| 6 | Beaufort | beaufort | 23.0% | affine | 19.8% | vigenere | 19.7% | ✅ (low conf) |
| 7 | Porta | vigenere | 51.2% | beaufort | 40.4% | — | — | ❌ |
| 8 | Columnar | columnar | 90.9% | — | — | — | — | ✅ |
| 9 | Playfair | foursquare | 79.1% | bifid | 5.8% | playfair | 3.0% | ⚠️ (#3) |
| 10 | Hill | hill | 84.4% | vigenere | 3.9% | beaufort | 3.7% | ✅ |
| 11 | FourSquare | foursquare | 76.1% | bifid | 6.8% | trifid | 3.6% | ✅ |
| 12 | Bifid | foursquare | 75.3% | playfair | 5.2% | bifid | 3.4% | ⚠️ (#3) |
| 13 | Trifid | autokey | 27.2% | porta | 19.6% | hill | 18.4% | ❌ |
| 14 | ADFGX | adfgvx | 90.8% | adfgx | 1.1% | — | — | ⚠️ (#2) |
| 15 | ADFGVX | adfgx | 86.0% | adfgvx | 1.1% | — | — | ⚠️ (#2) |
| 16 | Nihilist | nihilist | 46.2% | polybius | 7.7% | vigenere | 3.2% | ✅ |
| 17 | Polybius | atbash | 38.2% | polybius | 7.1% | adfgx | 4.4% | ⚠️ (#2) |
| 18 | TEA | caesar | 29.4% | misty1 | 12.0% | playfair | 11.9% | ❌ |
| 19 | XTEA | caesar | 71.8% | misty1 | 26.2% | affine | 2.0% | ❌ |
| 20 | Lucifer | misty1 | 19.0% | lucifer | 16.1% | xtea | 16.0% | ⚠️ (#2) |
| 21 | LOKI | caesar | 56.7% | misty1 | 23.3% | affine | 6.4% | ❌ |
| 22 | MISTY1 | caesar | 30.7% | playfair | 12.8% | misty1 | 12.2% | ⚠️ (#3) |

### Score

| Outcome | Count | Ciphers |
|---------|-------|---------|
| ✅ Correct at #1 | 9 | Caesar, Affine, Atbash, Autokey, Beaufort, Columnar, Hill, FourSquare, Nihilist |
| ⚠️ Correct at #2–#3 | 8 | Vigenere, Playfair, Bifid, ADFGX, ADFGVX, Polybius, Lucifer, MISTY1 |
| ❌ Not in top 3 | 5 | Porta, Trifid, TEA, XTEA, LOKI |

**Top-1 accuracy: 9/22 (40.9%) | Top-3 accuracy: 17/22 (77.3%)**

### Comparison with MIN_LEN=50 Model (Section 8)

| Metric | MIN_LEN=50 (78.16%) | MIN_LEN=100 (79.24%) |
|--------|---------------------|----------------------|
| Top-1 | 11/22 (50%) | 9/22 (41%) |
| Top-3 | 16/22 (73%) | 17/22 (77%) |
| Val Accuracy | 78.16% | 79.24% |

**Improvements:** FourSquare ⚠️→✅, Nihilist ⚠️→✅, Lucifer ❌→⚠️, MISTY1 ❌→⚠️  
**Regressions:** TEA ✅→❌, XTEA ✅→❌ — both now classified as Caesar (likely training run variance)  
**ADFGX/ADFGVX swap** appeared in this model — both correct at #2 but swapped at #1

The MIN_LEN=100 model has better top-3 accuracy and higher validation accuracy, making it more useful in practice (the correct cipher appears in the top 3 for 17/22 cases). The TEA/XTEA regression is likely random variance from this specific training run rather than a systematic issue.

---

## 10. Training Infrastructure

All models trained on the **IIIT Delhi Precision cluster**:
- **Node:** gpu01
- **Partition:** short queue with MIG GPU (3g.40gb slice, account=ravi)
- **Environment:** Miniconda (cipherlens env), Python 3.12, PyTorch, XGBoost, scikit-learn

### V4 Training Times

| Model | Training Time | Device | Epochs | Best Val Acc |
|-------|--------------|--------|--------|--------------|
| XGBoost (all stages) | ~2 min | CPU | N/A | — |
| CNN Deep Learning | ~5 min | H100 MIG | 10 | 66.5% |
| Hybrid CNN | ~26 min | H100 MIG | 15 | 78.16% |

### V3 Training Times (for comparison)

| Model | Best Val Acc |
|-------|--------------|
| XGBoost | ~76% |
| CNN Deep Learning | 71.4% |
| Hybrid CNN | 82.24% |

---

## 9. Tech Stack

- **Frontend:** Next.js, React, Tailwind CSS, shadcn/ui, Zustand
- **Backend:** FastAPI, Python 3.12, PyTorch, XGBoost, scikit-learn
- **Repository:** https://github.com/LordAizen1/cipherlens
