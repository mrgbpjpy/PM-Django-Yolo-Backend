# videos/apps.py
from django.apps import AppConfig

class VideosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "videos"            # matches folder: /app/videos
    verbose_name = "Video Processing"
