FROM python:3.11.9-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy requirements and install system deps needed by some Python packages
COPY requirements.txt ./

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       gcc \
       libssl-dev \
       libffi-dev \
       default-libmysqlclient-dev \
       netcat-openbsd \
    && pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y --auto-remove build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . /app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
