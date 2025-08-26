# videos/views.py
import os
import uuid
import cv2
import numpy as np
import tempfile

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

# For signed video URLs
_signer = TimestampSigner(settings.SECRET_KEY)


def _abs(request, path: str) -> str:
    """Return absolute URI for a relative path."""
    return request.build_absolute_uri(path)


def _process_with_opencv(blob: bytes) -> bytes:
    """
    Demo OpenCV pipeline:
    - Save upload to temp file
    - Read frames with cv2.VideoCapture
    - Overlay rectangle + demo text
    - Write processed video to temp mp4 (H264/mp4v)
    - Return final bytes
    """
    in_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    in_file.write(blob)
    in_file.flush()
    in_file.close()

    out_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    out_file.close()

    cap = cv2.VideoCapture(in_file.name)
    if not cap.isOpened():
        raise RuntimeError("Failed to open uploaded video")

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # H264/MP4V codec
    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter(out_file.name, fourcc, fps, (w, h))

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # --- Example overlay (replace with YOLO later) ---
        cv2.rectangle(frame, (50, 50), (w - 50, h - 50), (0, 0, 255), 4)
        cv2.putText(
            frame,
            "OpenCV DEMO",
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

    with open(out_file.name, "rb") as f:
        processed_blob = f.read()

    # Cleanup temp files
    os.unlink(in_file.name)
    os.unlink(out_file.name)

    return processed_blob


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_view(request):
    """Upload + process video with OpenCV overlay."""
    f = request.FILES.get("file")
    if not f:
        return HttpResponseBadRequest("Missing 'file'")

    blob = b"".join(chunk for chunk in f.chunks())

    # Process
    try:
        processed = _process_with_opencv(blob)
        status, error = "DONE", ""
    except Exception as e:
        processed, status, error = None, "ERROR", str(e)

    # Save DB record
    job = VideoJob.objects.create(
        owner=request.user,
        filename=f.name,
        mime="video/mp4",
        status=status,
        result_mp4=processed,
        error=error,
    )

    # Signed access URLs
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
@permission_classes([AllowAny])  # signed token secures access
def video_view(request, job_id):
    """Return processed video if token matches."""
    token = request.GET.get("t")
    if not token:
        return HttpResponseBadRequest("Missing token")

    try:
        unsigned = _signer.unsign(token, max_age=600)  # 10 min validity
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
