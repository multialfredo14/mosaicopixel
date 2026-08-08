from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = os.environ.get("DATA_DIR")

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-change-me")
DEBUG = os.environ.get("DJANGO_DEBUG", "0") == "1"

_hosts = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,0.0.0.0,testserver")
ALLOWED_HOSTS = [h.strip() for h in _hosts.split(",") if h.strip()]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "social_django",
    "accounts",
    "generator",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "mosaicopixel.urls"

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
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
            ],
        },
    },
]

WSGI_APPLICATION = "mosaicopixel.wsgi.application"

if DATA_DIR:
    Path(DATA_DIR).mkdir(parents=True, exist_ok=True)
    _db_path = Path(DATA_DIR) / "django.db"
else:
    _db_path = BASE_DIR / "db.sqlite3"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": _db_path,
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "es-mx"
TIME_ZONE = os.environ.get("TZ", "America/Chicago")
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "webapp" / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "index"
LOGOUT_REDIRECT_URL = "login"

AUTHENTICATION_BACKENDS = (
    "social_core.backends.google.GoogleOAuth2",
    "django.contrib.auth.backends.ModelBackend",
)

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get("GOOGLE_OAUTH2_KEY", "")
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get("GOOGLE_OAUTH2_SECRET", "")
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = ["email", "profile"]
SOCIAL_AUTH_LOGIN_REDIRECT_URL = LOGIN_REDIRECT_URL
SOCIAL_AUTH_NEW_USER_REDIRECT_URL = LOGIN_REDIRECT_URL
SOCIAL_AUTH_RAISE_EXCEPTIONS = DEBUG
