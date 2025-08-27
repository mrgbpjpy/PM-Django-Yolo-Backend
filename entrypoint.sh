#!/bin/sh
set -e

# Run DB migrations on boot (safe if there are none)
python manage.py migrate || true

# Start gunicorn on the port provided by Railway
exec gunicorn mysite.wsgi:application --bind 0.0.0.0:${PORT:-8000}
