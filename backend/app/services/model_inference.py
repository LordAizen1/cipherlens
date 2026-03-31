import os
import time
import joblib
import numpy as np

from app.schemas import CipherPrediction, FeatureImportance, FeatureSet

class CipherModel:
    """Base class for cipher identification models."""
    def predict(self, ciphertext: str, features: FeatureSet, model_type: str) -> tuple[list[CipherPrediction], list[FeatureImportance], float]:
        raise NotImplementedError

class HierarchicalCipherModel(CipherModel):
    def __init__(self, model_dir: str):
        self.model_dir = model_dir
        
        family_model_path = os.path.join(model_dir, "family_classifier.pkl")
        family_le_path = os.path.join(model_dir, "family_label_encoder.pkl")
        
        if os.path.exists(family_model_path) and os.path.exists(family_le_path):
            self.family_clf = joblib.load(family_model_path)
            self.family_le = joblib.load(family_le_path)
        else:
            self.family_clf = None
            self.family_le = None

        self.cipher_clfs = {}
        self.cipher_les = {}
        
        if os.path.exists(model_dir):
            for f in os.listdir(model_dir):
                if f.startswith("cipher_classifier_") and f.endswith(".pkl"):
                    family_name = f.replace("cipher_classifier_", "").replace(".pkl", "")
                    self.cipher_clfs[family_name] = joblib.load(os.path.join(model_dir, f))
                    
                    le_path = os.path.join(model_dir, f"cipher_le_{family_name}.pkl")
                    if os.path.exists(le_path):
                        self.cipher_les[family_name] = joblib.load(le_path)

    def predict(self, ciphertext: str, features: FeatureSet, model_type: str) -> tuple[list[CipherPrediction], list[FeatureImportance], float]:
        start = time.perf_counter()

        if self.family_clf is None or self.family_le is None:
             return [CipherPrediction(cipher_name="ModelsNotTrained", cipher_family="Unknown", confidence=1.0)], [], 0.0
             
        feature_vector = np.array([[
            features.length, features.entropy, features.compression,
            features.bigram_entropy, features.trigram_entropy, features.uniformity,
            features.unique_ratio, features.transition_var, features.run_length_mean,
            features.run_length_var, features.ioc, features.ioc_variance,
            features.digit_ratio, features.alpha_ratio
        ]])

        # Stage 1: Predict Family Probabilities
        family_probs = self.family_clf.predict_proba(feature_vector)[0]
        family_classes = self.family_le.classes_

        # SOFT-ROUTING STAGE 2
        predictions = []
        for fam_idx, fam_name in enumerate(family_classes):
            family_confidence = family_probs[fam_idx]
            
            if family_confidence < 0.01:
                # Cull negligible branches to save compute
                continue

            if fam_name in self.cipher_les:
                cipher_le = self.cipher_les[fam_name]
                cipher_classes = cipher_le.classes_
                
                if fam_name in self.cipher_clfs:
                    cipher_clf = self.cipher_clfs[fam_name]
                    cipher_probs = cipher_clf.predict_proba(feature_vector)[0]
                else:
                    cipher_probs = [1.0] # Only 1 class
                
                for i, c_name in enumerate(cipher_classes):
                    conf = family_confidence * cipher_probs[i]
                    predictions.append(
                        CipherPrediction(
                            cipher_name=c_name,
                            cipher_family=fam_name,
                            confidence=round(float(conf), 4)
                        )
                    )
            else:
                predictions.append(CipherPrediction(cipher_name="Unknown", cipher_family=fam_name, confidence=round(float(family_confidence), 4)))

        # Sort all aggregated probabilities universally
        predictions.sort(key=lambda p: p.confidence, reverse=True)

        feature_names = [
            "length", "entropy", "compression", "bigram_entropy", "trigram_entropy",
            "uniformity", "unique_ratio", "transition_var", "run_length_mean",
            "run_length_var", "ioc", "ioc_variance", "digit_ratio", "alpha_ratio"
        ]
        
        importances = []
        if hasattr(self.family_clf, "feature_importances_"):
            for i, name in enumerate(feature_names):
                importances.append(
                    FeatureImportance(
                        feature_name=name,
                        importance_score=round(float(self.family_clf.feature_importances_[i]), 4)
                    )
                )
            importances.sort(key=lambda x: x.importance_score, reverse=True)

        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        return predictions, importances, elapsed_ms

_cached_model = None

def get_model(use_mock: bool = False, model_dir: str = "app/models") -> CipherModel:
    global _cached_model
    if _cached_model is not None:
        return _cached_model

    _cached_model = HierarchicalCipherModel(model_dir=model_dir)
    return _cached_model
