# MuleCube Watchdog Service
# Auto-restarts failed services, handles thermal/battery shedding

FROM python:3.11-slim-bookworm

LABEL maintainer="Nuclear Lighters Inc."
LABEL description="MuleCube Watchdog - Self-healing daemon"

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./

CMD ["python", "main.py"]
