# Easy Ecom

Easy Ecom runs as a **stateless Streamlit UI** backed by **FastAPI + PostgreSQL** as the only source of truth.

## Architecture (AWS ECS + RDS shape)

- `streamlit` container (`Dockerfile.streamlit`): UI-only HTTP client.
- `backend` container (`Dockerfile.api`): FastAPI, validation, business logic, persistence.
- `db` container: PostgreSQL (RDS-compatible setup).
- `nginx` container:
  - `/` -> Streamlit (`streamlit:8501`)
  - `/api/` -> FastAPI (`backend:8000`)
  - `/health` -> FastAPI `/health`

## Runtime data flow

1. User interacts with Streamlit pages.
2. Streamlit uses `services/api_client.py` only.
3. API calls hit backend endpoints for auth/products/sales.
4. FastAPI persists entities through SQLAlchemy models into Postgres.
5. Alembic migrations are applied on startup to keep schema in sync.

## Core dependency ownership

- **Streamlit**: presentation + API requests only.
- **FastAPI**: validation, business rules, persistence.
- **Postgres**: durable storage for horizontal-scale deployments.

## Environment variables

Use `.env.example` as template.

### Backend
- `DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/easy_ecom`
- `JWT_SECRET=change-me`
- `CORS_ORIGINS=http://localhost`

### Streamlit
- `API_BASE_URL=http://localhost/api`

## Local run

```bash
cp .env.example .env
docker compose up -d --build
```

Then verify:

- UI: `http://localhost/`
- API: `http://localhost/api/products?client_id=demo_client`
- Health: `http://localhost/health`

## API endpoints currently used by Streamlit

- `POST /auth/login`
- `GET /products`
- `POST /products`
- `GET /sales`
- `POST /sales`
- `GET /health`
