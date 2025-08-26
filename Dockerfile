# ---- Base ----
FROM python:3.11-slim

# Install system deps: ffmpeg + build tools
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Python deps
COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy app source
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

# Start gunicorn
CMD ["gunicorn", "mysite.wsgi:application", "--bind", "0.0.0.0:8000"]
