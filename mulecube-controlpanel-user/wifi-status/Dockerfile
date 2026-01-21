# MuleCube WiFi Status Service
# Exposes WiFi network information via REST API

FROM python:3.11-slim-bookworm

LABEL maintainer="Nuclear Lighters Inc."
LABEL description="MuleCube WiFi Status - Network info API"

RUN apt-get update && apt-get install -y --no-install-recommends \
    iw \
    wireless-tools \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./

EXPOSE 9002

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${API_PORT:-9002}/health || exit 1

CMD ["sh", "-c", "python -m uvicorn main:app --host 0.0.0.0 --port ${API_PORT:-9002}"]
