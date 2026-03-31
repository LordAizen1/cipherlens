# CipherLens — Classical Cipher Identification

A machine learning-powered web application that identifies classical cipher types from ciphertext. Supports **22 cipher types** across **7 cryptographic families**.

Built as a B.Tech Project (BTP) at IIIT Delhi, 2025-2026.

## Models

| Model | Architecture | Accuracy | Best For |
|-------|-------------|----------|----------|
| **Hybrid CNN** | Character CNN + Statistical Features MLP | 82% | Best overall (default) |
| **CNN Deep Learning** | Character-level 1D CNN | 71% | Numeric ciphers (Polybius) |
| **XGBoost** | Two-stage family → cipher with soft-routing | 76% | Fast, interpretable |

All models trained on 330k samples (shuffled `cipher_MASTER_FULL_V3` dataset) with 14 statistical features. See [FINDINGS.md](FINDINGS.md) for detailed evaluation.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 16, React 19, TypeScript, Tailwind CSS, shadcn/ui, Magic UI, Framer Motion |
| **State** | Zustand |
| **Backend** | FastAPI, PyTorch, XGBoost, scikit-learn |
| **Infra** | Docker Compose, Gunicorn/Uvicorn |

## Quick Start

### With Docker

```bash
git clone https://github.com/LordAizen1/cipherlens.git
cd cipherlens
docker compose up -d --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

### Without Docker

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

## Supported Ciphers

| Family | Ciphers | Count |
|--------|---------|-------|
| Monoalphabetic Substitution | Caesar, Affine, Atbash | 3 |
| Polyalphabetic Substitution | Vigenere, Autokey, Beaufort, Porta | 4 |
| Transposition | Columnar Transposition | 1 |
| Polygraphic Substitution | Playfair, Hill, Four-Square | 3 |
| Fractionating | Bifid, Trifid, ADFGX, ADFGVX, Nihilist, Polybius | 6 |
| Modern Block | Lucifer, MISTY1, LOKI, TEA, XTEA | 5 |
| **Total** | | **22** |

## Project Structure

```
cipherlens/
├── frontend/                ← Next.js app
│   ├── src/
│   │   ├── app/             — Pages (Home, Ciphers, About)
│   │   ├── components/      — UI components
│   │   ├── lib/             — API client, types, constants
│   │   └── hooks/           — Zustand store
│   └── Dockerfile
├── backend/                 ← FastAPI app
│   ├── app/
│   │   ├── main.py          — App entry point
│   │   ├── routers/         — API endpoints (/predict, /health)
│   │   ├── services/        — Inference (XGBoost, DL, Hybrid)
│   │   └── models/          — Trained .pkl and .pth files
│   ├── scripts/             — Training scripts
│   └── Dockerfile
├── data/                    — Dataset (not in git, transfer via scp)
├── docker-compose.yml
├── FINDINGS.md              — Model evaluation report
└── README.md
```

## Deployment

```bash
# On the server
git clone https://github.com/LordAizen1/cipherlens.git
cd cipherlens
export CORS_ORIGINS='["https://your-domain.iiitd.ac.in"]'
docker compose up -d --build
```

Add Nginx reverse proxy:
```nginx
server {
    server_name cipherlens.iiitd.ac.in;

    location / {
        proxy_pass http://localhost:3000;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
    }
}
```

No database needed — the app is stateless. Models are baked into the Docker image. CPU inference only (no GPU required for serving).

## Training

Models were trained on the IIIT Delhi Precision cluster (H100 MIG GPU). To retrain:

```bash
# Shuffle dataset
python shuffle_dataset.py

# Train XGBoost (CPU)
cd backend && python scripts/train.py

# Train DL / Hybrid (GPU)
python scripts/train_dl.py
python scripts/train_hybrid.py
```

SLURM job scripts (`train_job.sh`, `train_dl_job.sh`, `train_hybrid_job.sh`) are included for cluster submission.

## Team

| Name | Roll | GitHub | LinkedIn |
|------|------|--------|----------|
| Dhruv Verma | 2022172 | [@dhruv22172](https://github.com/dhruv22172) | [LinkedIn](https://www.linkedin.com/in/dhruvverma2022172/) |
| Maulik Mahey | 2022282 | [@maulik-dot](https://github.com/maulik-dot) | [LinkedIn](https://www.linkedin.com/in/maulik-mahey-952a92260/) |
| Md Kaif | 2022289 | [@LordAizen1](https://github.com/LordAizen1) | [LinkedIn](https://www.linkedin.com/in/mohammadkaif007/) |
| Sweta Snigdha | 2022527 | [@cypherei00](https://github.com/cypherei00) | [LinkedIn](https://www.linkedin.com/in/sweta-snigdha-8549a4255/) |

Supervised by **Dr. Ravi Anand** — IIIT Delhi
