import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.config import Settings
from app.schemas import PredictionRequest, PredictionResponse
from app.services.feature_extraction import extract_features
from app.services.model_inference import get_model

router = APIRouter()


@router.post("/api/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    if len(request.ciphertext.strip()) < 2:
        raise HTTPException(status_code=400, detail="Ciphertext too short (min 2 characters).")

    settings = Settings()
    model = get_model(
        use_mock=settings.USE_MOCK_MODEL,
        model_dir=settings.MODEL_DIR,
    )

    features = extract_features(request.ciphertext)
    predictions, importances, inference_ms = model.predict(
        ciphertext=request.ciphertext,
        features=features,
        model_type=request.model_type,
    )

    # Apply confidence threshold
    filtered = [p for p in predictions if p.confidence >= request.confidence_threshold]
    if not filtered:
        filtered = [predictions[0]]

    return PredictionResponse(
        request_id=f"pred_{uuid.uuid4().hex[:12]}",
        timestamp=datetime.now(timezone.utc).isoformat(),
        top_prediction=predictions[0],
        all_predictions=filtered,
        features=features if request.include_features else None,
        feature_importance=importances,
        model_used=request.model_type,
        inference_time_ms=inference_ms,
    )
