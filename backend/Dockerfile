# 1. Use a lightweight Python base image
FROM python:3.10-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
       build-essential \
       libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home appuser
WORKDIR /home/appuser

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt


COPY ./app ./app


EXPOSE 8000


USER appuser


ENV PYTHONPATH=/home/appuser


CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
