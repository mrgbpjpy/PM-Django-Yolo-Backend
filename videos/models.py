# videos/models.py
import uuid
from django.db import models
from django.contrib.auth import get_user_model

class VideoJob(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        DONE = "DONE", "Done"
        ERROR = "ERROR", "Error"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="video_jobs")
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)

    filename = models.CharField(max_length=255, blank=True)
    mime = models.CharField(max_length=64, default="video/mp4")

    # temporary storage of processed mp4; served once then deleted
    result_mp4 = models.BinaryField(null=True, blank=True)

    error = models.TextField(blank=True, default="")

    def __str__(self) -> str:
        return f"{self.id} [{self.status}] {self.filename or ''}"
