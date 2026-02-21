# CipherLens — Classical Cipher Identification

A machine learning-powered web application that identifies classical cipher types from ciphertext. Supports **22 cipher types** across **7 cryptographic families**.

Built as a B.Tech Project (BTP) at IIIT Delhi, Spring 2026.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 14 (App Router), TypeScript, Tailwind CSS, shadcn/ui, Magic UI |
| **State** | Zustand (client) + TanStack Query (server) |
| **Backend** | FastAPI, Pydantic, scikit-learn, XGBoost, LightGBM |
| **Database** | PostgreSQL, MongoDB, Redis |
| **Infra** | Docker, Nginx, Gunicorn/Uvicorn |

## Quick Start

### With Docker (recommended)

```bash
docker-compose up --build
```

- Frontend: [http://localhost:3000](http://localhost:3000)
- Backend: [http://localhost:8000](http://localhost:8000) (when ready)

### Without Docker

```bash
# Frontend
cd frontend
npm install
npm run dev

# Backend (when ready)
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Project Structure

```
cipherlens/
├── frontend/               ← Next.js app
│   ├── src/
│   │   ├── app/            — Pages (Home, Ciphers, About)
│   │   ├── components/     — UI components
│   │   ├── lib/            — API client, types, constants
│   │   ├── hooks/          — Zustand store
│   │   └── providers/      — Theme & Query providers
│   ├── Dockerfile
│   └── package.json
├── backend/                ← FastAPI app (teammates)
│   └── ...
├── docker-compose.yml      ← Orchestrates all services
└── README.md
```

## Supported Ciphers

| Family | Ciphers |
|--------|---------|
| Monoalphabetic Substitution | Caesar, Affine, Atbash |
| Polyalphabetic Substitution | Vigenere, Autokey, Beaufort, Porta |
| Transposition | Columnar Transposition |
| Polygraphic Substitution | Playfair, Hill, Four-Square |
| Fractionating | Bifid, Trifid, ADFGX, ADFGVX, Nihilist |
| Modern Block | Lucifer, MISTY1, LOKI, TEA, XTEA |
| Numeric | Polybius Square |

## Connecting Frontend to Backend

The frontend currently uses a mock API layer (`frontend/src/lib/api.ts`). When the FastAPI backend is ready:

1. Update `frontend/src/lib/api.ts` — replace the mock `predictCipher()` function with a real Axios call
2. Uncomment the `backend` service in `docker-compose.yml`
3. Set the `NEXT_PUBLIC_API_URL` environment variable to point to the backend

## Team

- Dhruv Verma (2022172)
- Maulik Mahey (2022282)
- Md Kaif (2022289)
- Sweta Snigdha (2022527)

Supervised by **Dr. Ravi Anand** — IIIT Delhi
