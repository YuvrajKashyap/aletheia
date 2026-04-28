FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app/services/api

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY services/api/pyproject.toml ./pyproject.toml
COPY services/api/app ./app

RUN python -m pip install --upgrade pip \
    && python -m pip install .

COPY services/api/alembic.ini ./alembic.ini
COPY services/api/alembic ./alembic

EXPOSE 8000

CMD ["sh", "-c", "python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
