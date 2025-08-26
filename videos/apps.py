# videos/apps.py
from django.apps import AppConfig

class VideosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "videos"   # <-- if the folder is /app/videos. If it's inside mysite/, use "mysite.videos".
