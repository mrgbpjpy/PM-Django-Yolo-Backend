# ---- Base ----
FROM python:3.11-slim

# Install system deps: ffmpeg + build tools
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .

# Install Python deps
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Optional: collect static files (skip errors if DB not ready)
RUN python manage.py collectstatic --noinput || true

# Railway injects $PORT, default to 8000 for local dev
EXPOSE 8000

# Start gunicorn — bind to Railway's dynamic $PORT
CMD ["sh", "-c", "gunicorn mysite.wsgi:application --bind 0.0.0.0:$PORT"]

