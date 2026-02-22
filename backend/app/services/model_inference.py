import random
import re
import time
from abc import ABC, abstractmethod

from app.schemas import CipherPrediction, FeatureImportance, FeatureSet
from app.services.cipher_data import CIPHER_CATALOG


class CipherModel(ABC):
    """Base class for cipher identification models."""

    @abstractmethod
    def predict(
        self, ciphertext: str, features: FeatureSet, model_type: str
    ) -> tuple[list[CipherPrediction], list[FeatureImportance], float]:
        """
        Returns (predictions_sorted_desc, feature_importances, inference_time_ms).
        """
        ...


class MockCipherModel(CipherModel):
    """Heuristic-based mock model. Replace with real ML models later."""

    def predict(
        self, ciphertext: str, features: FeatureSet, model_type: str
    ) -> tuple[list[CipherPrediction], list[FeatureImportance], float]:
        start = time.perf_counter()

        predictions = self._generate_predictions(ciphertext, features)
        importances = self._generate_importances()

        elapsed_ms = round((time.perf_counter() - start) * 1000, 1)
        return predictions, importances, elapsed_ms

    def _generate_predictions(
        self, ciphertext: str, features: FeatureSet
    ) -> list[CipherPrediction]:
        cleaned = ciphertext.upper().replace(" ", "")
        is_numeric_only = bool(re.fullmatch(r"[\d\s]+", ciphertext))
        is_hex = bool(re.fullmatch(r"[0-9A-Fa-f]+", cleaned))
        is_adfgx = bool(re.fullmatch(r"[ADFGX]+", cleaned))
        is_adfgvx = bool(re.fullmatch(r"[ADFGVX]+", cleaned))

        # Default guess
        top_cipher = "Vigenere"
        top_family = "Polyalphabetic Substitution"

        if is_numeric_only and features.has_spaces:
            top_cipher = "Nihilist"
            top_family = "Fractionating"
        elif is_numeric_only:
            top_cipher = "Polybius Square"
            top_family = "Numeric"
        elif is_hex and len(cleaned) >= 16:
            top_cipher = "TEA"
            top_family = "Modern Block"
        elif is_adfgx and features.alphabet_size <= 5:
            top_cipher = "ADFGX"
            top_family = "Fractionating"
        elif is_adfgvx and features.alphabet_size <= 6:
            top_cipher = "ADFGVX"
            top_family = "Fractionating"
        elif features.alphabet_size <= 20 and len(cleaned) > 10:
            if features.ioc > 0.06:
                top_cipher = "Caesar"
                top_family = "Monoalphabetic Substitution"

        # Build predictions for all 22 ciphers
        predictions: list[CipherPrediction] = []
        for cipher in CIPHER_CATALOG:
            if cipher["name"] == top_cipher:
                conf = random.uniform(0.78, 0.95)
            elif cipher["family"] == top_family:
                conf = random.uniform(0.35, 0.72)
            else:
                conf = random.uniform(0.01, 0.25)

            predictions.append(
                CipherPrediction(
                    cipher_name=cipher["name"],
                    cipher_family=cipher["family"],
                    confidence=round(conf, 4),
                )
            )

        predictions.sort(key=lambda p: p.confidence, reverse=True)
        return predictions

    def _generate_importances(self) -> list[FeatureImportance]:
        raw = [
            ("Index of Coincidence", random.uniform(0.15, 0.35)),
            ("Shannon Entropy", random.uniform(0.10, 0.25)),
            ("Chi-Square", random.uniform(0.08, 0.20)),
            ("Bigram Entropy", random.uniform(0.05, 0.15)),
            ("Alphabet Size", random.uniform(0.04, 0.12)),
            ("Digit Ratio", random.uniform(0.02, 0.10)),
            ("Trigram Entropy", random.uniform(0.02, 0.08)),
            ("Text Length", random.uniform(0.01, 0.05)),
        ]
        raw.sort(key=lambda x: x[1], reverse=True)
        return [
            FeatureImportance(feature_name=name, importance_score=round(score, 4))
            for name, score in raw
        ]


# ── Future: Real model loading ────────────────────────────────────────
#
# class RealCipherModel(CipherModel):
#     def __init__(self, model_dir: str):
#         import joblib
#         self.hierarchical = joblib.load(f"{model_dir}/hierarchical.joblib")
#         self.unified = joblib.load(f"{model_dir}/unified.joblib")
#
#     def predict(self, ciphertext, features, model_type):
#         model = self.hierarchical if model_type == "hierarchical" else self.unified
#         feature_vector = self._features_to_array(features)
#         probas = model.predict_proba(feature_vector.reshape(1, -1))[0]
#         ...


_cached_model: CipherModel | None = None


def get_model(use_mock: bool = True, model_dir: str = "models/") -> CipherModel:
    global _cached_model
    if _cached_model is not None:
        return _cached_model

    if use_mock:
        _cached_model = MockCipherModel()
    else:
        raise NotImplementedError(
            "Real model loading not yet implemented. Set USE_MOCK_MODEL=true."
        )

    return _cached_model
