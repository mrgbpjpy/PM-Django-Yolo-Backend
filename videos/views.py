# videos/views.py
import uuid
from django.conf import settings
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.urls import reverse
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from .models import VideoJob

_signer = TimestampSigner(settings.SECRET_KEY)


def _abs(request, path: str) -> str:
    """Return absolute URI for a relative path."""
    return request.build_absolute_uri(path)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_view(request):
    f = request.FILES.get("file")
    if not f:
        return HttpResponseBadRequest("Missing 'file'")

    # Read file bytes
    blob = b"".join(chunk for chunk in f.chunks())

    # Save to DB as a new VideoJob
    job = VideoJob.objects.create(
        owner=request.user,
        filename=f.name,
        mime=f.content_type or "video/mp4",
        status="DONE",   # mark done immediately for demo
        result_mp4=blob,
    )

    # Generate signed access token
    token = _signer.sign(str(job.id))
    play_url = _abs(request, reverse("video_get", args=[job.id])) + f"?t={token}"
    download_url = play_url + "&download=1"

    return JsonResponse(
        {"id": str(job.id), "play_url": play_url, "download_url": download_url},
        status=201,
    )


@api_view(["GET"])
@permission_classes([AllowAny])  # secured by signed token
def video_view(request, job_id):
    token = request.GET.get("t")
    if not token:
        return HttpResponseBadRequest("Missing token")

    try:
        unsigned = _signer.unsign(token, max_age=600)  # 10 minutes
    except SignatureExpired:
        return HttpResponseBadRequest("Token expired")
    except BadSignature:
        return HttpResponseBadRequest("Invalid token")

    if unsigned != str(job_id):
        return HttpResponseBadRequest("Token mismatch")

    try:
        job = VideoJob.objects.get(id=job_id)
    except VideoJob.DoesNotExist:
        return HttpResponseNotFound("Not found")

    if not job.result_mp4:
        return HttpResponseNotFound("No processed video available")

    resp = HttpResponse(job.result_mp4, content_type=job.mime)
    if request.GET.get("download") == "1":
        resp["Content-Disposition"] = f'attachment; filename="{job.filename}"'
    else:
        resp["Content-Disposition"] = f'inline; filename="{job.filename}"'
    resp["Cache-Control"] = "no-store"
    return resp
