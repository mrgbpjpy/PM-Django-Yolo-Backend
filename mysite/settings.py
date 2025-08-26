"""
Django settings for mysite project (Railway + React CORS/CSRF + JWT)
Django 5.x
"""
from pathlib import Path
import os
from datetime import timedelta

# ---------- Paths ----------
BASE_DIR = Path(__file__).resolve().parent.parent

# ---------- Helpers ----------
def env_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).lower() in {"1", "true", "yes", "on"}

def env_list(name: str, default_list):
    raw = os.getenv(name)
    return [x.strip() for x in raw.split(",")] if raw else default_list

# ---------- Core ----------
SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-rc^*w^w&6g9_(uvx#6s*bnt!w)l0rdi%!l7mv#y%uc&x%wo5pk",  # dev fallback only
)
DEBUG = env_bool("DJANGO_DEBUG", False)

ALLOWED_HOSTS = env_list(
    "DJANGO_ALLOWED_HOSTS",
    [
        "server-lpz7-production.up.railway.app",  # your Railway domain
        ".railway.app",                           # allow Railway subdomains (optional)
        "localhost",
        "127.0.0.1",
    ],
)

# CSRF: include scheme. On Django 5+, wildcard patterns like *.vercel.app are allowed.
CSRF_TRUSTED_ORIGINS = env_list(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    [
        "https://server-lpz7-production.up.railway.app",
        "https://*.vercel.app",
        "http://localhost:3000",
    ],
)

# ---------- Security / Proxy ----------
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Cookies: keep secure in prod; SameSite=None only if you plan to use cross-site cookies (e.g., session auth).
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = "None"
CSRF_COOKIE_SAMESITE = "None"

# ---------- Apps ----------
INSTALLED_APPS = [
    # Django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "corsheaders",                 # CORS support
    "rest_framework",              # Django REST Framework
    "rest_framework_simplejwt",    # JWT auth

    # Local apps
    "videos",                      # your video upload/processing app
]

# ---------- DRF / Auth ----------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    # Default permissions: leave endpoints open/closed explicitly in views.
    # "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# ---------- Middleware ----------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",     # keep right after Security

    "django.contrib.sessions.middleware.SessionMiddleware",

    "corsheaders.middleware.CorsMiddleware",          # CORS BEFORE CommonMiddleware
    "django.middleware.common.CommonMiddleware",

    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "mysite.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "mysite.wsgi.application"

# ---------- Database (Railway Postgres via env PG*) ----------
# Railway sets PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["PGDATABASE"],
        "USER": os.environ["PGUSER"],
        "PASSWORD": os.environ["PGPASSWORD"],
        "HOST": os.environ["PGHOST"],
        "PORT": os.environ["PGPORT"],
    }
}

# ---------- Password validation ----------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------- i18n ----------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ---------- Static files ----------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"] if (BASE_DIR / "static").exists() else []
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------- CORS (React) ----------
# Exact origins (NO trailing slash)
CORS_ALLOWED_ORIGINS = env_list(
    "DJANGO_CORS_ALLOWED_ORIGINS",
    [
        """"
Django settings for mysite project (Railway + React CORS/CSRF + JWT)
Django 5.x
"""
from pathlib import Path
import os
from datetime import timedelta

# ---------- Paths ----------
BASE_DIR = Path(__file__).resolve().parent.parent

# ---------- Helpers ----------
def env_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).lower() in {"1", "true", "yes", "on"}

def env_list(name: str, default_list):
    raw = os.getenv(name)
    return [x.strip() for x in raw.split(",")] if raw else default_list

# ---------- Core ----------
SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-rc^*w^w&6g9_(uvx#6s*bnt!w)l0rdi%!l7mv#y%uc&x%wo5pk",  # dev fallback only
)
DEBUG = env_bool("DJANGO_DEBUG", False)

ALLOWED_HOSTS = env_list(
    "DJANGO_ALLOWED_HOSTS",
    [
        "server-lpz7-production.up.railway.app",  # your Railway domain
        ".railway.app",                           # allow Railway subdomains (optional)
        "localhost",
        "127.0.0.1",
    ],
)

# CSRF: include scheme. On Django 5+, wildcard patterns like *.vercel.app are allowed.
CSRF_TRUSTED_ORIGINS = env_list(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    [
        "https://server-lpz7-production.up.railway.app",
        "https://*.vercel.app",
        "http://localhost:3000",
    ],
)

# ---------- Security / Proxy ----------
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Cookies: keep secure in prod; SameSite=None only if you plan to use cross-site cookies (e.g., session auth).
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = "None"
CSRF_COOKIE_SAMESITE = "None"

# ---------- Apps ----------
INSTALLED_APPS = [
    # Django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "corsheaders",                 # CORS support
    "rest_framework",              # Django REST Framework
    "rest_framework_simplejwt",    # JWT auth

    # Local apps
    "videos",                      # your video upload/processing app
]

# ---------- DRF / Auth ----------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    # Default permissions: leave endpoints open/closed explicitly in views.
    # "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# ---------- Middleware ----------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",     # keep right after Security

    "django.contrib.sessions.middleware.SessionMiddleware",

    "corsheaders.middleware.CorsMiddleware",          # CORS BEFORE CommonMiddleware
    "django.middleware.common.CommonMiddleware",

    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "mysite.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "mysite.wsgi.application"

# ---------- Database (Railway Postgres via env PG*) ----------
# Railway sets PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["PGDATABASE"],
        "USER": os.environ["PGUSER"],
        "PASSWORD": os.environ["PGPASSWORD"],
        "HOST": os.environ["PGHOST"],
        "PORT": os.environ["PGPORT"],
    }
}

# ---------- Password validation ----------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------- i18n ----------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ---------- Static files ----------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"] if (BASE_DIR / "static").exists() else []
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------- CORS (React) ----------
# Exact origins (NO trailing slash)
CORS_ALLOWED_ORIGINS = env_list(
    "DJANGO_CORS_ALLOWED_ORIGINS",
    [
        "https://84fl4c.csb.app",  # your Vercel frontend
        "http://localhost:3000",
    ],
)

# Allow any preview under your Vercel scope (future-proof previews)
CORS_ALLOWED_ORIGIN_REGEXES = env_list(
    "DJANGO_CORS_ALLOWED_ORIGIN_REGEXES",
    [
        r"^https://.*\.vercel\.app$",
    ],
)

# Send cookies across sites only if you actually use cookie auth:
CORS_ALLOW_CREDENTIALS = True
# If you need extra headers/methods, you can extend:
# from corsheaders.defaults import default_headers, default_methods
# CORS_ALLOW_HEADERS = list(default_headers) + ["Authorization", "X-CSRFToken"]
# CORS_ALLOW_METHODS = list(default_methods) + ["PATCH"]
",  # your Vercel frontend
        "http://localhost:3000",
        
    ],
)

# Allow any preview under your Vercel scope (future-proof previews)
CORS_ALLOWED_ORIGIN_REGEXES = env_list(
    "DJANGO_CORS_ALLOWED_ORIGIN_REGEXES",
    [
        r"^https://.*\.vercel\.app$",
    ],
)

# Send cookies across sites only if you actually use cookie auth:
CORS_ALLOW_CREDENTIALS = True
# If you need extra headers/methods, you can extend:
# from corsheaders.defaults import default_headers, default_methods
# CORS_ALLOW_HEADERS = list(default_headers) + ["Authorization", "X-CSRFToken"]
# CORS_ALLOW_METHODS = list(default_methods) + ["PATCH"]
