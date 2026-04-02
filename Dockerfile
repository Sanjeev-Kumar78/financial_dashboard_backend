FROM python:3.11-slim

WORKDIR /app

# Install system dependencies required for psycopg2 and argon2-cffi
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies using standard pip for the pyproject.toml
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Copy application files
COPY . .

EXPOSE 8000

# Run migrations and then start the server
CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000
