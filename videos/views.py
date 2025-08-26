# videos/views.py
import os
import uuid
import cv2
import numpy as np
import tempfile
import subprocess
import urllib.parse

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

# Signed URLs
_signer = TimestampSigner(settings.SECRET_KEY)


def _abs(request, path: str) -> str:
    return request.build_absolute_uri(path)


def _process_with_opencv(blob: bytes, use_yolo: bool = False) -> bytes:
    """Process video with OpenCV or YOLO overlay, then re-encode via ffmpeg."""
    in_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    in_file.write(blob)
    in_file.flush()
    in_file.close()

    raw_out = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    raw_out.close()

    cap = cv2.VideoCapture(in_file.name)
    if not cap.isOpened():
        raise RuntimeError("Failed to open uploaded video")

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter(raw_out.name, fourcc, fps, (w, h))

    # Load YOLO if requested
    yolo_model = None
    if use_yolo:
        try:
            from ultralytics import YOLO
            yolo_model = YOLO("yolov8n.pt")
        except ImportError:
            print("YOLO requested but ultralytics not installed, falling back to OpenCV.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if yolo_model:
            results = yolo_model.predict(frame, verbose=False)
            for r in results:
                for box in r.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    conf = float(box.conf[0])
                    cls = int(box.cls[0])
                    label = f"{yolo_model.names[cls]} {conf:.2f}"
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(
                        frame, label, (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
                    )
        else:
            # Fallback demo overlay
            cv2.rectangle(frame, (50, 50), (w - 50, h - 50), (0, 0, 255), 4)
            cv2.putText(
                frame, "OpenCV DEMO",
                (60, 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                2, (0, 255, 0), 3, cv2.LINE_AA
            )

        out.write(frame)

    cap.release()
    out.release()

    # Re-encode with ffmpeg for browser playback
    final_out = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    final_out.close()
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", raw_out.name,
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", "-movflags", "+faststart",
            final_out.name,
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    with open(final_out.name, "rb") as f:
        processed_blob = f.read()

    # Cleanup
    os.unlink(in_file.name)
    os.unlink(raw_out.name)
    os.unlink(final_out.name)

    return processed_blob


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_view(request):
    """Upload + process video with OpenCV/YOLO overlay."""
    f = request.FILES.get("file")
    if not f:
        return HttpResponseBadRequest("Missing 'file'")

    blob = b"".join(chunk for chunk in f.chunks())

    try:
        use_yolo = request.GET.get("yolo") == "1"
        processed = _process_with_opencv(blob, use_yolo=use_yolo)
        status, error = "DONE", ""
    except Exception as e:
        processed, status, error = None, "ERROR", str(e)

    job = VideoJob.objects.create(
        owner=request.user,
        filename=f.name,
        mime="video/mp4",
        status=status,
        result_mp4=processed,
        error=error,
    )

    # Encode token safely for URLs
    token = _signer.sign(str(job.id))
    safe_token = urllib.parse.quote(token, safe="")
    play_url = _abs(request, reverse("video_get", args=[job.id])) + f"?t={safe_token}"
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
    """Return processed video with HTTP Range support."""
    token = request.GET.get("t")
    if not token:
        return HttpResponseBadRequest("Missing token")

    try:
        unsigned = _signer.unsign(token, max_age=600)
    except (SignatureExpired, BadSignature):
        return HttpResponseBadRequest("Invalid/expired token")

    if unsigned != str(job_id):
        return HttpResponseBadRequest("Token mismatch")

    try:
        job = VideoJob.objects.get(id=job_id)
    except VideoJob.DoesNotExist:
        return HttpResponseNotFound("Not found")

    if not job.result_mp4:
        return HttpResponseNotFound("No processed video available")

    blob = job.result_mp4
    size = len(blob)

    range_header = request.headers.get("Range")
    if range_header:
        # Example: Range: bytes=0-1023
        start, end = range_header.replace("bytes=", "").split("-")
        start = int(start) if start else 0
        end = int(end) if end else size - 1
        end = min(end, size - 1)

        chunk = blob[start:end + 1]
        resp = HttpResponse(chunk, status=206, content_type="video/mp4")
        resp["Content-Range"] = f"bytes {start}-{end}/{size}"
        resp["Accept-Ranges"] = "bytes"
        resp["Content-Length"] = str(len(chunk))
        return resp

    # No Range: return entire video
    resp = HttpResponse(blob, content_type="video/mp4")
    resp["Content-Length"] = str(size)
    return resp
