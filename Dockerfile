# ---- Base ----
FROM python:3.11-slim

# Install system deps: ffmpeg + build tools
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Copy Python deps
COPY requirements.txt .

# Install Python deps
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Collect static files (safe fallback)
RUN python manage.py collectstatic --noinput || true

# Expose default port
EXPOSE 8000

# ✅ Use shell form so $PORT expands correctly
CMD sh -c "gunicorn mysite.wsgi:application --bind 0.0.0.0:${PORT:-8000}"
