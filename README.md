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

## Deployment Plan

### Architecture Overview

```
                    ┌──────────────┐
    Users ────────► │    Nginx     │ (reverse proxy, SSL, static files)
                    │   :80/:443   │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              ▼                         ▼
     ┌────────────────┐      ┌──────────────────┐
     │   Next.js App  │      │   FastAPI App     │
     │    :3000       │      │   (Gunicorn +     │
     │                │ ───► │    Uvicorn)        │
     │   Frontend     │      │    :8000          │
     └────────────────┘      └────────┬──────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                  ▼
             ┌────────────┐  ┌──────────────┐  ┌──────────────┐
             │ PostgreSQL │  │    Redis     │  │   MongoDB    │
             │   :5432    │  │    :6379     │  │   :27017     │
             │ (users,    │  │ (cache,      │  │ (prediction  │
             │  sessions) │  │  rate limit) │  │  logs)       │
             └────────────┘  └──────────────┘  └──────────────┘
```

### Option A: College Server (Recommended for BTP)

Since IIIT Delhi provides server access for BTP projects, this is the most straightforward path.

**Prerequisites:**
- SSH access to a college server (or VM)
- Docker & Docker Compose installed on the server
- A subdomain or port allocation (e.g., `cipherlens.iiitd.edu.in` or `server-ip:3000`)

**Steps:**

```bash
# 1. SSH into the college server
ssh username@server.iiitd.edu.in

# 2. Clone the repo
git clone https://github.com/LordAizen1/cipherlens.git
cd cipherlens

# 3. Create production environment file
cp .env.example .env
# Edit .env with production secrets (DB passwords, API keys, etc.)

# 4. Build and start all services
docker-compose -f docker-compose.yml up -d --build

# 5. Verify everything is running
docker-compose ps
curl http://localhost:3000   # Frontend
curl http://localhost:8000   # Backend
```

**Nginx config (if college provides Nginx):**

```nginx
server {
    listen 80;
    server_name cipherlens.iiitd.edu.in;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Option B: Cloud Deployment (Alternative)

If college infra isn't available or for public demo purposes.

| Service | Platform | Free Tier |
|---------|----------|-----------|
| Frontend | Vercel | Yes (already deployed for preview) |
| Backend | Railway / Render | 500 hrs/month free |
| PostgreSQL | Supabase / Neon | Yes |
| Redis | Upstash | 10K commands/day free |
| MongoDB | MongoDB Atlas | 512MB free |

**Steps for cloud:**

1. **Frontend** — already on Vercel, set `NEXT_PUBLIC_API_URL` to the backend URL
2. **Backend** — deploy to Railway:
   ```bash
   cd backend
   railway init
   railway up
   ```
3. **Databases** — use managed services (Supabase for Postgres, Atlas for Mongo, Upstash for Redis)
4. **Environment variables** — set connection strings in Railway dashboard

### Pre-Deployment Checklist

- [ ] All ML models exported and placed in `backend/models/`
- [ ] `frontend/src/lib/api.ts` updated to call real backend (replace mock)
- [ ] `docker-compose.yml` backend service uncommented
- [ ] `.env` file created with production secrets
- [ ] CORS configured in FastAPI to allow frontend origin
- [ ] Rate limiting enabled via Redis
- [ ] Database migrations run (if using an ORM)
- [ ] SSL/TLS configured (Let's Encrypt or college cert)
- [ ] Health check endpoints tested (`/health` on backend)
- [ ] Load tested with sample ciphertexts

### Monitoring & Maintenance

- **Logs**: `docker-compose logs -f` or `docker-compose logs backend`
- **Restart**: `docker-compose restart backend`
- **Update**: `git pull && docker-compose up -d --build`
- **Backup DB**: `docker-compose exec postgres pg_dump -U cipherlens cipherlens > backup.sql`

## Team

- Dhruv Verma (2022172)
- Maulik Mahey (2022282)
- Md Kaif (2022289)
- Sweta Snigdha (2022527)

Supervised by **Dr. Ravi Anand** — IIIT Delhi
