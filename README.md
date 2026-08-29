# AI-Powered Personal Finance & Investment Advisor

## Running the application

The repository contains the existing FastAPI backend and React/Vite frontend. Market analytics use Yahoo Finance through `yfinance`, with the local cache used when live data is unavailable. LLM features are optional and fall back to the deterministic analytics assistant.

## Repository layout

- `backend/`
  - `app/` - application factory and runtime entrypoint
  - `api/v1/` - versioned API routers planned for REST endpoints
  - `core/` - configuration, logging, security utilities, exceptions
  - `database/` - SQLAlchemy setup, database sessions, migrations
  - `domain/` - business entities and domain logic boundaries
  - `models/` - ORM models and persistence schema definitions
  - `repositories/` - repository pattern for data access abstraction
  - `schemas/` - Pydantic request and response schemas
  - `services/` - business service layer and orchestration
  - `ml/` - machine learning pipelines, model workflows, and inference
  - `utils/` - shared utilities and helpers
  - `tests/` - structured unit and integration tests
- `datasets/`
  - `raw/` - raw source datasets (ignored in version control)
  - `processed/` - cleaned and feature-engineered artifact outputs
  - `external/` - third-party reference or external enrichment data
  - `trained_models/` - serialized model artifacts (ignored in version control)
- `docs/` - architecture, design, and project roadmap documentation
- `scripts/` - automation scripts for data preparation, training, deployment
- `notebooks/` - exploratory data science and model experiments
- `frontend/` - placeholder for future React frontend assets

## Configuration

Copy `.env.example` to `.env` and replace `JWT_SECRET_KEY` with a long random value. Keep `.env` out of source control. For a separately hosted frontend, copy `frontend/.env.example` to `frontend/.env` and set `VITE_API_URL` to the deployed API's `/api/v1` URL.

## Local development

Backend:

```bash
python -m pip install -r requirements.txt
copy .env.example .env
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Frontend, in a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`; API documentation is at `http://127.0.0.1:8000/docs`.

## Production deployment

Use Railway MySQL for production storage; SQLite is supported only for local development. Set all production values through the host's secret manager—never commit a real connection string or API key.

### Railway MySQL URL

```text
mysql+pymysql://USER:PASSWORD@HOST:PORT/DATABASE
```

The username and password portions must be URL-encoded if they contain reserved characters. For example, `p@ss:word/1` becomes `p%40ss%3Aword%2F1`. Railway supplies the host, port, database, username, and password in its MySQL service variables.

### Render backend settings

- Runtime: Docker
- Dockerfile path: `./Dockerfile`
- Health check path: `/health`
- Start command (when not using Docker): `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
- Required environment variables: `ENVIRONMENT=production`, `DATABASE_URL`, `JWT_SECRET_KEY`, and `CORS_ORIGINS=https://<your-vercel-project>.vercel.app`
- Optional variables: `GEMINI_API_KEY`, `LLM_PROVIDER`, `LLM_MODEL`, `ALPHA_VANTAGE_API_KEY`, `REDIS_URL`

Render owns `PORT`; do not set a fixed production port. The application creates missing tables at startup without dropping existing tables, so a redeploy/restart preserves data in Railway MySQL.

### Vercel frontend settings

- Root directory: `frontend`
- Framework preset: Vite
- Build command: `npm run build`
- Output directory: `dist`
- Environment variable: `VITE_API_URL=https://<your-render-service>.onrender.com/api/v1`

`VITE_API_URL` is compiled into the browser bundle, so set it for the production Vercel environment and redeploy after changing it. The local Vite proxy remains available for development.

Run the backend with:

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
```

The included `docker-compose.yml` starts the backend with MySQL 8.4 for local container testing; create a local `.env` first, then run `docker compose up --build`.

## Data isolation

Income, expense, budget, advisor-result, prediction, and chat records carry a foreign-key `user_id`. Protected routes derive that ID from the validated JWT; repository queries scope reads and writes to the authenticated user.

## Dataset review summary

Three dataset sources were analyzed:

1. **Global India Markets Macro**
   - `daily_market_data.csv`: daily market and commodity indicators for time-series forecasting
   - `monthly_macro_data.csv`: monthly macroeconomic series for feature enrichment and long-term forecasts
2. **Synthetic Personal Finance**
   - `synthetic_personal_finance_dataset.csv`: user financial profiles for risk scoring and investment recommendation
3. **House Price India**
   - `House Price India.csv`: housing attributes and price target for real estate value prediction

## Next steps

1. Approve the Phase 0 architecture and structure
2. Begin Phase 1 with backend scaffolding and package implementation
3. Add database models, repository patterns, and service layers
4. Implement authentication and user profile features
5. Develop ML preprocessing and model integration after data engineering is finalized

## How to run the backend

1. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```
2. Create a local `.env` file based on `.env.example`.
3. Start the backend:
   ```bash
   python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
   ```
4. Open Swagger UI at `http://127.0.0.1:8000/docs`

## Available development endpoints

- Health check: `GET /api/v1/health`
- Version: `GET /api/v1/version`
- Swagger: `GET /docs`
