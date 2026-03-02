# Easy Ecom

Easy Ecom uses a **stateless Streamlit UI** and a **FastAPI + PostgreSQL backend** as the single source of truth.

## Architecture (AWS-ready shape)

- `streamlit` container (`Dockerfile.streamlit`): UI only (no CSV, no DB file access).
- `backend` container (`Dockerfile.api`): FastAPI + SQLAlchemy + Alembic.
- `db` container: PostgreSQL.
- `nginx` container:
  - `/` -> Streamlit (`streamlit:8501`)
  - `/api/*` -> FastAPI (`backend:8000`)
  - `/health` -> FastAPI `/health`

Legacy `DB/` CSV files are retained only as historical artifacts and are ignored by git/runtime.

## Core runtime flow

1. User opens `http://localhost/` (nginx).
2. Streamlit pages call FastAPI via `services/api_client.py` using `API_BASE_URL`.
3. FastAPI persists data in Postgres (`ui_users`, `ui_products`, `ui_sales`).
4. Alembic migrations are applied at API startup (`alembic upgrade head`).

## Environment variables

Use `.env.example` as the template.

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
- API via nginx: `http://localhost/api/products`
- Health: `http://localhost/api/health`

## API endpoints used by Streamlit

- `POST /auth/login`
- `GET /products`
- `POST /products`
- `GET /sales`
- `POST /sales`
- `GET /health`

## Notes for cloud deployment

- Keep two app images (`Dockerfile.api`, `Dockerfile.streamlit`) and one Postgres instance (RDS in AWS).
- Keep nginx as the edge router to preserve `/` + `/api/*` split.
