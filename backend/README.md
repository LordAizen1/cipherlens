# CipherLens Backend

FastAPI backend for the Classical Cipher Identification system.

## Quick Start

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run dev server
uvicorn app.main:app --reload --port 8000
```

API docs: [http://localhost:8000/api/docs](http://localhost:8000/api/docs)

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/predict` | Classify ciphertext |
| GET | `/api/health` | Health check |

## Mock Mode

The backend runs with mock inference by default (`USE_MOCK_MODEL=true`). When real ML models are ready:

1. Place `.joblib` files in `models/`
2. Implement `RealCipherModel` in `app/services/model_inference.py`
3. Set `USE_MOCK_MODEL=false` in `.env`
