"""
mysite URL Configuration
"""
from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Inline API views (simple and self-contained)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
def index(_request):
    return Response({
        "message": "Django API is running",
        "endpoints": {
            "admin": "/admin/",
            "token_obtain_pair (POST)": "/api/token/",
            "token_refresh (POST)": "/api/token/refresh/",
            "me (GET, Bearer token)": "/api/me/",
            "healthz (GET)": "/healthz",
        },
    })


@api_view(["GET"])
@permission_classes([AllowAny])
def healthz(_request):
    return Response({"status": "ok"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    user = request.user
    username = user.get_username()
    return Response({
        "message": f"{username} is authenticated.",
        "username": username,
        "is_superuser": user.is_superuser,
        "is_staff": user.is_staff,
    })


urlpatterns = [
    # Index / API root
    path("", index, name="index"),

    # Admin
    path("admin/", admin.site.urls),

    # JWT auth (SimpleJWT)
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Health check
    path("healthz", healthz, name="healthz"),

    # Protected example
    path("api/me/", me, name="api_me"),
]
