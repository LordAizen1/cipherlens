import math
import re
from collections import Counter

import numpy as np

from app.schemas import FeatureSet


def _shannon_entropy(text: str) -> float:
    """Shannon entropy in bits per character."""
    if not text:
        return 0.0
    counts = Counter(text)
    length = len(text)
    return -sum(
        (c / length) * math.log2(c / length) for c in counts.values()
    )


def _index_of_coincidence(text: str) -> float:
    """Index of Coincidence: sum(f*(f-1)) / (N*(N-1))."""
    n = len(text)
    if n <= 1:
        return 0.0
    counts = Counter(text)
    numerator = sum(f * (f - 1) for f in counts.values())
    return numerator / (n * (n - 1))


def _chi_square(text: str) -> float:
    """Chi-square statistic against uniform letter distribution (26 letters)."""
    alpha_only = re.sub(r"[^A-Z]", "", text.upper())
    n = len(alpha_only)
    if n == 0:
        return 0.0
    expected = n / 26.0
    counts = Counter(alpha_only)
    observed = np.array([counts.get(chr(i), 0) for i in range(65, 91)], dtype=float)
    return float(np.sum((observed - expected) ** 2 / expected))


def _ngram_entropy(text: str, n: int) -> float:
    """Shannon entropy over overlapping n-grams."""
    if len(text) < n:
        return 0.0
    ngrams = [text[i : i + n] for i in range(len(text) - n + 1)]
    counts = Counter(ngrams)
    total = len(ngrams)
    return -sum(
        (c / total) * math.log2(c / total) for c in counts.values()
    )


def extract_features(ciphertext: str) -> FeatureSet:
    """Extract cryptanalytic features from raw ciphertext."""
    cleaned = ciphertext.upper().replace(" ", "")
    length = len(cleaned) or 1  # avoid division by zero

    digit_count = sum(1 for c in cleaned if c.isdigit())
    alpha_count = sum(1 for c in cleaned if c.isalpha())

    return FeatureSet(
        entropy=round(_shannon_entropy(cleaned), 4),
        ioc=round(_index_of_coincidence(cleaned), 6),
        chi_square=round(_chi_square(cleaned), 2),
        alphabet_size=len(set(cleaned)),
        has_spaces=" " in ciphertext,
        digit_ratio=round(digit_count / length, 4),
        alpha_ratio=round(alpha_count / length, 4),
        bigram_entropy=round(_ngram_entropy(cleaned, 2), 4),
        trigram_entropy=round(_ngram_entropy(cleaned, 3), 4),
    )
