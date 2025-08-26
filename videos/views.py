# videos/views.py
import io
import uuid
import cv2
import numpy as np

from django.conf import settings
from django.http import (
    HttpResponse,
    JsonResponse,
    HttpResponseBadRequest,
    HttpResponseNotFound,
)
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


def _process_with_opencv(blob: bytes) -> bytes:
    """
    Simple demo pipeline:
    - Decode video from bytes
    - Draw overlay on each frame
    - Encode back to mp4 (H264 in mp4 container)
    """
    # Write input blob to buffer file for cv2.VideoCapture
    in_buf = "/tmp/input.mp4"
    out_buf = "/tmp/output.mp4"
    with open(in_buf, "wb") as f:
        f.write(blob)

    cap = cv2.VideoCapture(in_buf)
    if not cap.isOpened():
        raise RuntimeError("Failed to open video for processing")

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter(out_buf, fourcc, fps, (w, h))

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # --- Demo overlay: red rectangle + YOLO DEMO text ---
        cv2.rectangle(frame, (50, 50), (w - 50, h - 50), (0, 0, 255), 4)
        cv2.putText(
            frame,
            "YOLO DEMO",
            (60, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            2,
            (0, 255, 0),
            3,
            cv2.LINE_AA,
        )

        out.write(frame)

    cap.release()
    out.release()

    # Read processed file back into memory
    with open(out_buf, "rb") as f:
        processed_blob = f.read()

    return processed_blob


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_view(request):
    f = request.FILES.get("file")
    if not f:
        return HttpResponseBadRequest("Missing 'file'")

    # Read file bytes
    blob = b"".join(chunk for chunk in f.chunks())

    # --- Process with OpenCV overlay ---
    try:
        processed = _process_with_opencv(blob)
        status = "DONE"
        error = ""
    except Exception as e:
        processed = None
        status = "ERROR"
        error = str(e)

    # Save to DB as a new VideoJob
    job = VideoJob.objects.create(
        owner=request.user,
        filename=f.name,
        mime="video/mp4",
        status=status,
        result_mp4=processed,
        error=error,
    )

    # Generate signed access token
    token = _signer.sign(str(job.id))
    play_url = _abs(request, reverse("video_get", args=[job.id])) + f"?t={token}"
    download_url = play_url + "&download=1"

    return JsonResponse(
        {
            "id": str(job.id),
            "status": status,
            "error": error,
            "play_url": play_url,
            "download_url": download_url,
        },
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

    resp = HttpResponse(job.result_mp4, content_type="video/mp4")
    if request.GET.get("download") == "1":
        resp["Content-Disposition"] = f'attachment; filename="{job.filename}"'
    else:
        resp["Content-Disposition"] = f'inline; filename="{job.filename}"'
    resp["Cache-Control"] = "no-store"
    return resp
