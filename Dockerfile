FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Render injects PORT at runtime; default to 10000 for local docker runs
ENV PORT=10000
EXPOSE 10000

# gthread workers let multiple SSE streams run concurrently without blocking.
# --timeout 0 disables worker timeout so long downloads aren't killed.
CMD ["sh", "-c", "gunicorn -k gthread --workers 1 --threads 8 --timeout 0 -b 0.0.0.0:${PORT} app:app"]
