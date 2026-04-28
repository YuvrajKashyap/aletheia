# Neon Postgres Deployment

This is a readiness guide only. Do not create the hosted database from this step unless the project owner explicitly starts deployment.

## Setup

1. Create a Neon project.
2. Copy the connection string for backend runtime.
3. Use a direct connection string for migrations if Neon recommends it for your plan.
4. Set `DATABASE_URL` in the backend host environment.

Example placeholder:

```text
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST/DB?sslmode=require
```

Do not commit the real connection string.

## Migrations

Windows local command:

```powershell
cd services/api
.\.venv\Scripts\python.exe -m alembic upgrade head
```

Generic production command:

```bash
cd services/api
python -m alembic upgrade head
```

## Data Loading

Load and seed data only through existing CLI or admin workflows. Local Docker Postgres remains the local development database.

Do not add fake documents, chunks, qrels, traces, evaluation rows, replay rows, or index metadata to make hosted pages look populated.
