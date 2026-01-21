# MuleCube Hardware Monitor Service
FROM python:3.11-slim-bookworm

LABEL maintainer="Nuclear Lighters Inc."
LABEL description="MuleCube Hardware Monitor - Pi 5 metrics API"

RUN apt-get update && apt-get install -y --no-install-recommends \
    i2c-tools \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./

RUN mkdir -p /app/data

EXPOSE 8080

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
