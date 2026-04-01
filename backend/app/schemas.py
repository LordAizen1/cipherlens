from pydantic import BaseModel, Field
from typing import Literal


class PredictionRequest(BaseModel):
    ciphertext: str = Field(..., min_length=1, max_length=10000)
    model_type: Literal["hierarchical", "unified", "deep_learning", "hybrid"] = "hybrid"
    confidence_threshold: float = Field(default=0.6, ge=0.0, le=1.0)
    include_features: bool = True


class CipherPrediction(BaseModel):
    cipher_name: str
    cipher_family: str
    confidence: float


class FeatureSet(BaseModel):
    length: float
    entropy: float
    compression: float
    bigram_entropy: float
    trigram_entropy: float
    uniformity: float
    unique_ratio: float
    transition_var: float
    run_length_mean: float
    run_length_var: float
    ioc: float
    ioc_variance: float
    digit_ratio: float = 0.0
    alpha_ratio: float = 0.0
    max_kasiski_ioc: float = 0.0


class FeatureImportance(BaseModel):
    feature_name: str
    importance_score: float


class PredictionResponse(BaseModel):
    request_id: str
    timestamp: str
    top_prediction: CipherPrediction
    all_predictions: list[CipherPrediction]
    features: FeatureSet | None = None
    feature_importance: list[FeatureImportance]
    model_used: Literal["hierarchical", "unified", "deep_learning", "hybrid"]
    inference_time_ms: float
