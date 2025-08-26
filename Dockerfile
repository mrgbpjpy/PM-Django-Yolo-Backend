# ---- Base image ----
FROM python:3.11-slim

# ---- Install system dependencies ----
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# ---- Set workdir ----
WORKDIR /app

# ---- Copy Python dependencies ----
COPY requirements.txt .

# Upgrade pip and install deps
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ---- Copy project code ----
COPY . .

# ---- Collect static files (safe to fail) ----
RUN python manage.py collectstatic --noinput || true

# ---- Expose Django port ----
EXPOSE 8000

# ---- Default CMD ----
CMD ["gunicorn", "mysite.wsgi:application", "--bind", "0.0.0.0:8000"]
