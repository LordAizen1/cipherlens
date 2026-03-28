import math
import zlib
import numpy as np
from collections import Counter
from app.schemas import FeatureSet

def extract_features(cipher: str) -> FeatureSet:
    """
    Extracts 12 statistical features from a ciphertext string and returns a FeatureSet.
    Matches the exact logic from the jupyter notebook.
    """
    if isinstance(cipher, bytes):
        data = cipher
        text = None
    else:
        # Avoid encode errors
        data = cipher.encode('utf-8', errors='ignore')
        text = cipher

    total = len(data)
    if total == 0:
        return FeatureSet(
            length=0.0, entropy=0.0, compression=0.0, bigram_entropy=0.0,
            trigram_entropy=0.0, uniformity=0.0, unique_ratio=0.0, transition_var=0.0,
            run_length_mean=0.0, run_length_var=0.0, ioc=0.0, ioc_variance=0.0
        )

    freqs = Counter(data)
    entropy = -sum((f/total)*math.log2(f/total) for f in freqs.values())
    compression = len(zlib.compress(data)) / total

    if total > 1:
        bigrams = [data[i:i+2] for i in range(total-1)]
        freqs2 = Counter(bigrams)
        total2 = len(bigrams)
        bigram_entropy = -sum((f/total2)*math.log2(f/total2) for f in freqs2.values())
    else:
        bigram_entropy = 0.0

    if total > 2:
        trigrams = [data[i:i+3] for i in range(total-2)]
        freqs3 = Counter(trigrams)
        total3 = len(trigrams)
        trigram_entropy = -sum((f/total3)*math.log2(f/total3) for f in freqs3.values())
    else:
        trigram_entropy = 0.0

    vals = list(freqs.values())
    uniformity = float(np.std(vals)) if len(vals) > 0 else 0.0
    unique_ratio = len(freqs) / total

    transitions = Counter(zip(data, data[1:]))
    transition_var = float(np.var(list(transitions.values()))) if transitions else 0.0

    runs = []
    current = 1
    for i in range(1, total):
        if data[i] == data[i-1]:
            current += 1
        else:
            runs.append(current)
            current = 1
    runs.append(current)

    run_length_mean = float(np.mean(runs)) if runs else 0.0
    run_length_var = float(np.var(runs)) if runs else 0.0

    # IoC — works on alpha chars, falls back to digits for numeric ciphers
    alpha_chars = [c for c in (text or '') if c.isalpha()]
    if len(alpha_chars) > 1:
        f = Counter(alpha_chars)
        N = len(alpha_chars)
        ioc = sum(v*(v-1) for v in f.values()) / (N*(N-1))
    else:
        digit_chars = [c for c in (text or '') if c.isdigit()]
        if len(digit_chars) > 1:
            f = Counter(digit_chars)
            N = len(digit_chars)
            ioc = sum(v*(v-1) for v in f.values()) / (N*(N-1))
        else:
            ioc = 0.0

    work_chars = alpha_chars if len(alpha_chars) > 1 else [c for c in (text or '') if c.isdigit()]
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
                    p_vals.append(sum(v*(v-1) for v in fc.values())/(N2*(N2-1)))
            if p_vals:
                iocs.append(np.var(p_vals))
        ioc_variance = float(np.mean(iocs)) if iocs else 0.0
    else:
        ioc_variance = 0.0

    # New features
    txt_len = max(len(text or ''), 1)
    digit_ratio = sum(1 for c in (text or '') if c.isdigit()) / txt_len
    alpha_ratio = sum(1 for c in (text or '') if c.isalpha()) / txt_len

    return FeatureSet(
        length=float(total),
        entropy=float(entropy),
        compression=float(compression),
        bigram_entropy=float(bigram_entropy),
        trigram_entropy=float(trigram_entropy),
        uniformity=float(uniformity),
        unique_ratio=float(unique_ratio),
        transition_var=float(transition_var),
        run_length_mean=float(run_length_mean),
        run_length_var=float(run_length_var),
        ioc=float(ioc),
        ioc_variance=float(ioc_variance),
        digit_ratio=float(digit_ratio),
        alpha_ratio=float(alpha_ratio),
    )
