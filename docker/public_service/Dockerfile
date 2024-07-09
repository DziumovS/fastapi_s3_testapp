FROM python:3.12-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .
COPY ./public_api ./public_api

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev curl nano && \
    pip install --upgrade pip && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir --no-deps -r requirements.txt && \
    useradd -ms /bin/bash www && \
    chown -R www:www /app && \
    chmod -R 755 /app

USER www

CMD ["uvicorn", "public_api.app:app", "--host", "0.0.0.0", "--port", "8002", "--reload"]