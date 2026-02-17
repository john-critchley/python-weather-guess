FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY src /app/src

#-jc Ensure service uses its intended config inside container.
#-jc Without this the loader falls back to common defaults (127.0.0.1 bind).
ENV CONFIG_FILE=/app/src/reporting/config/default.ini


WORKDIR /app

EXPOSE 8082

CMD ["python", "src/reporting/src/app.py"]

