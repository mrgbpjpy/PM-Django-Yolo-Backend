web: sh -c "python manage.py migrate || true && gunicorn mysite.wsgi:application --bind 0.0.0.0:${PORT:-8000}"
