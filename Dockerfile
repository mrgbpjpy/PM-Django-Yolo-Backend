# ---- Base ----
FROM python:3.11-slim

# Install system deps: ffmpeg + build tools for psycopg2, etc.
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libpq-dev \
    gcc \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python deps first (layer cache)
COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# App source
COPY . .

# Collect static (don’t fail if none)
RUN python manage.py collectstatic --noinput || true

# Make entrypoint executable (covers web-UI commits)
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

# Use entrypoint so $PORT expands at runtime
CMD ["./entrypoint.sh"]
