# videos/views.py
import io
from django.conf import settings
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.urls import reverse
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser

_signer = TimestampSigner(settings.SECRET_KEY)

def _abs(request, path: str) -> str:
    return request.build_absolute_uri(path)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_view(request):
    f = request.FILES.get("file")
    if not f:
        return HttpResponseBadRequest("Missing 'file'")

    # Read uploaded bytes (placeholder processing)
    blob = b"".join(chunk for chunk in f.chunks())

    # Store once in session just to prove the pipeline
    request.session["demo_blob"] = blob
    request.session.modified = True

    # Use a constant demo id; in real code this would be a UUID from DB
    job_id = "00000000-0000-0000-0000-000000000000"
    token = _signer.sign(job_id)
    play_url = _abs(request, reverse("video_get", args=[job_id])) + f"?t={token}"
    download_url = play_url + "&download=1"

    return JsonResponse({"id": job_id, "play_url": play_url, "download_url": download_url}, status=201)

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

    blob = request.session.pop("demo_blob", None)
    if not blob:
        return HttpResponseNotFound("Not found or already consumed")

    resp = HttpResponse(blob, content_type="video/mp4")
    if request.GET.get("download") == "1":
        resp["Content-Disposition"] = 'attachment; filename="processed.mp4"'
    else:
        resp["Content-Disposition"] = 'inline; filename="processed.mp4"'
    resp["Cache-Control"] = "no-store"
    return resp
