# ============================================================
# VetNurse Backend — Production Dockerfile
# Python 3.11 + FastAPI + Uvicorn
# ============================================================

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for aiomysql / cryptography
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

EXPOSE 8000

# Run with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
