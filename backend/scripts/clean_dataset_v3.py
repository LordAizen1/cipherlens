"""
clean_dataset_v3.py — Create cipher_MASTER_FULL_V3.csv from V2

Fixes:
1. Convert modern cipher bytes-repr strings → proper hex strings
2. Remove rows where plaintext == ciphertext (encryption failures)
3. Recalculate ALL 12 features from the cleaned ciphertext
4. Add 'digit_ratio' and 'alpha_ratio' as new features for better discrimination
"""
import os
import ast
import math
import zlib
import numpy as np
import pandas as pd
from collections import Counter
from tqdm import tqdm

INPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "cipher_MASTER_FULL_V2.csv")
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "cipher_MASTER_FULL_V3.csv")
TRAIN_OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "cipher_MASTER_TRAIN_V3.csv")


def bytes_repr_to_hex(s: str) -> str:
    """Convert a Python bytes repr like b'\\x93\\xbb...' to hex string '93bb...'"""
    s = str(s).strip()
    if s.startswith("b'") or s.startswith('b"'):
        try:
            raw_bytes = ast.literal_eval(s)
            if isinstance(raw_bytes, bytes):
                return raw_bytes.hex()
        except Exception:
            pass
    return s


def extract_features(cipher_str: str):
    """Extract 14 features from a ciphertext string."""
    text = cipher_str
    data = text.encode('utf-8', errors='ignore')
    total = len(data)

    if total == 0:
        return [0.0] * 14

    freqs = Counter(data)
    entropy = -sum((f / total) * math.log2(f / total) for f in freqs.values())
    compression = len(zlib.compress(data)) / total

    # Bigram entropy
    if total > 1:
        bigrams = [data[i:i + 2] for i in range(total - 1)]
        f2 = Counter(bigrams)
        t2 = len(bigrams)
        bigram_entropy = -sum((f / t2) * math.log2(f / t2) for f in f2.values())
    else:
        bigram_entropy = 0.0

    # Trigram entropy
    if total > 2:
        trigrams = [data[i:i + 3] for i in range(total - 2)]
        f3 = Counter(trigrams)
        t3 = len(trigrams)
        trigram_entropy = -sum((f / t3) * math.log2(f / t3) for f in f3.values())
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
    run_length_mean = float(np.mean(runs))
    run_length_var = float(np.var(runs))

    # IoC — now works on ANY text, not just pure alphabetic
    alpha_chars = [c for c in text if c.isalpha()]
    if len(alpha_chars) > 1:
        fc = Counter(alpha_chars)
        N = len(alpha_chars)
        ioc = sum(v * (v - 1) for v in fc.values()) / (N * (N - 1))
    else:
        # For digit-only ciphers, compute IoC on digits instead
        digit_chars = [c for c in text if c.isdigit()]
        if len(digit_chars) > 1:
            fc = Counter(digit_chars)
            N = len(digit_chars)
            ioc = sum(v * (v - 1) for v in fc.values()) / (N * (N - 1))
        else:
            ioc = 0.0

    # IoC variance
    work_chars = alpha_chars if len(alpha_chars) > 1 else [c for c in text if c.isdigit()]
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

    # NEW features: digit_ratio, alpha_ratio
    digit_ratio = sum(1 for c in text if c.isdigit()) / max(len(text), 1)
    alpha_ratio = sum(1 for c in text if c.isalpha()) / max(len(text), 1)

    return [
        float(total), entropy, compression, bigram_entropy, trigram_entropy,
        uniformity, unique_ratio, transition_var, run_length_mean,
        run_length_var, ioc, ioc_variance, digit_ratio, alpha_ratio
    ]


def main():
    print(f"Loading {INPUT_PATH}...")
    df = pd.read_csv(INPUT_PATH)
    print(f"  Original: {len(df)} rows, {len(df.columns)} columns")

    # === Step 1: Fix modern cipher encoding ===
    modern_ciphers = ['tea', 'xtea', 'lucifer', 'loki', 'misty1']
    converted = 0
    for cipher in modern_ciphers:
        mask = df['cipher'] == cipher
        original = df.loc[mask, 'ciphertext'].values
        df.loc[mask, 'ciphertext'] = [bytes_repr_to_hex(s) for s in tqdm(original, desc=f"  Converting {cipher}")]
        converted += mask.sum()
    print(f"  Converted {converted} modern cipher texts to hex")

    # === Step 2: Remove plaintext == ciphertext rows ===
    before = len(df)
    # For modern ciphers, plaintext is now hex so this comparison is safe
    same_mask = df['plaintext'].str.upper() == df['ciphertext'].str.upper()
    df = df[~same_mask].reset_index(drop=True)
    removed = before - len(df)
    print(f"  Removed {removed} rows where plaintext == ciphertext")

    # === Step 3: Recalculate ALL features ===
    print("  Recalculating features for all rows...")
    feature_cols = [
        "length", "entropy", "compression", "bigram_entropy", "trigram_entropy",
        "uniformity", "unique_ratio", "transition_var", "run_length_mean",
        "run_length_var", "ioc", "ioc_variance", "digit_ratio", "alpha_ratio"
    ]

    new_features = []
    for text in tqdm(df['ciphertext'].values, desc="  Extracting features"):
        new_features.append(extract_features(str(text)))

    feat_df = pd.DataFrame(new_features, columns=feature_cols)

    # Drop old feature columns
    old_feat_cols = [c for c in feature_cols if c in df.columns]
    df = df.drop(columns=old_feat_cols)

    # Add new features
    df = pd.concat([df, feat_df], axis=1)

    # === Step 4: Final stats ===
    print(f"\n{'=' * 50}")
    print(f"  FINAL: {len(df)} rows, {len(df.columns)} columns")
    print(f"  Columns: {list(df.columns)}")
    print()
    print("  Class distribution:")
    print(df['cipher'].value_counts().to_string())
    print()

    # Verify modern cipher fix
    print("  Modern cipher sample check:")
    for c in modern_ciphers:
        sample = df[df['cipher'] == c]['ciphertext'].iloc[0][:60]
        is_hex = all(ch in '0123456789abcdef' for ch in str(sample))
        print(f"    {c:10s}: {'✅ hex' if is_hex else '⚠️  not hex'} | {sample}")
    print()

    # IoC check
    print("  IoC check (should NOT be 0 for modern ciphers now):")
    for c in modern_ciphers:
        ioc_mean = df[df['cipher'] == c]['ioc'].mean()
        print(f"    {c:10s}: IoC = {ioc_mean:.4f}")
    print()

    # Save
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"  ✅ Saved to {OUTPUT_PATH}")

    train_df = df.drop(columns=["plaintext", "ciphertext"])
    train_df.to_csv(TRAIN_OUTPUT, index=False)
    print(f"  ✅ Train set saved to {TRAIN_OUTPUT}")


if __name__ == "__main__":
    main()
