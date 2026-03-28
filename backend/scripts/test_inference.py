import os
import math
import zlib
import time
import numpy as np
import joblib
from collections import Counter

def extract_features(cipher: str) -> list[float]:
    if isinstance(cipher, bytes):
        data = cipher
        text = None
    else:
        data = cipher.encode('utf-8', errors='ignore')
        text = cipher

    total = len(data)
    if total == 0:
        return [0.0]*12

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

    if text and text.isalpha():
        f = Counter(text)
        N = len(text)
        ioc = sum(v*(v-1) for v in f.values()) / (N*(N-1)) if N > 1 else 0.0
    else:
        ioc = 0.0

    if text and text.isalpha():
        iocs = []
        for period in range(2, 10):
            slices = [''.join(text[i::period]) for i in range(period)]
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

    return [
        float(total), float(entropy), float(compression), float(bigram_entropy),
        float(trigram_entropy), float(uniformity), float(unique_ratio),
        float(transition_var), float(run_length_mean), float(run_length_var),
        float(ioc), float(ioc_variance)
    ]

def main():
    import string
    def caesar(text, s):
        res = ""
        for c in text:
            if c.isalpha():
                res += chr((ord(c) - 65 + s) % 26 + 65)
        return res
        
    plain = "THEQUICKBROWNFOXJUMPSOVERTHELAZYDOGTHEQUICKBROWNFOXJUMPSOVERTHELAZYDOGTHEQUICKBROWNFOXJUMPSOVERTHELAZYDOG"
    sample_caesar = caesar(plain, 14)
    print(f"Testing local inference on ciphertext: {sample_caesar}")
    
    features = extract_features(sample_caesar)
    print(f"Extracted Features array: {features}")
    
    model_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app", "models")
    
    # Load Family Classifier and Encoder
    family_clf = joblib.load(os.path.join(model_dir, "family_classifier.pkl"))
    family_le = joblib.load(os.path.join(model_dir, "family_label_encoder.pkl"))
    
    start = time.perf_counter()
    feature_vector = np.array([features])
    
    # Stage 1: Predict Family Probabilities
    family_probs = family_clf.predict_proba(feature_vector)[0]
    family_classes = family_le.classes_

    print("\n--- SOFT-ROUTING ---")
    predictions = []
    for fam_idx, fam_name in enumerate(family_classes):
        family_confidence = family_probs[fam_idx]
        
        if family_confidence < 0.01:
            continue

        cipher_model_path = os.path.join(model_dir, f"cipher_classifier_{fam_name}.pkl")
        le_path = os.path.join(model_dir, f"cipher_le_{fam_name}.pkl")
        
        if os.path.exists(cipher_model_path) and os.path.exists(le_path):
            cipher_clf = joblib.load(cipher_model_path)
            cipher_le = joblib.load(le_path)
            
            cipher_probs = cipher_clf.predict_proba(feature_vector)[0]
            cipher_classes = cipher_le.classes_
            
            for i, c_name in enumerate(cipher_classes):
                conf = family_confidence * cipher_probs[i]
                predictions.append({
                    "cipher": c_name,
                    "family": fam_name,
                    "confidence": conf
                })

    predictions.sort(key=lambda p: p["confidence"], reverse=True)
    
    print("\n[TOP 3 PREDICTIONS]")
    for i, p in enumerate(predictions[:3]):
        print(f"#{i+1} Cipher: {p['cipher']} (Family: {p['family']}) - Prob: {p['confidence']:.4f}")
        
    print(f"\nInference completed in {(time.perf_counter() - start) * 1000:.2f} ms")

if __name__ == "__main__":
    main()
