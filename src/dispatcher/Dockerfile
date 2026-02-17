FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

# System deps (psycopg2, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install shared requirements first (better layer caching)
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY src /app/src

#-jc Ensure service uses its intended config inside container.
#-jc Without this the loader falls back to common defaults (127.0.0.1 bind).
ENV CONFIG_FILE=/app/src/dispatcher/config/default.ini

WORKDIR /app

EXPOSE 8080

CMD ["python", "src/dispatcher/src/app.py"]
