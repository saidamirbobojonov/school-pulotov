from pathlib import Path
import os
import sys
import environ

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env(
    DEBUG=(bool, False),
)

environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY", default="django-insecure-portfolio-demo-change-me")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"])
# Allow running `runserver` with DEBUG=False without missing /static and /media.
SERVE_STATICFILES = env.bool("SERVE_STATICFILES", default=bool(DEBUG or ("runserver" in sys.argv)))

INSTALLED_APPS = [
    "unfold",
    "modeltranslation",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts",
    "core",
    "people",
    "academics",
    "clubs",
    "competitions",
    "contacts",
    "events_extracurricular",
    "events_school",
    "news",
    "site_content",
    "navigation",
    "perspective",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "core.middleware.SimpleRateLimitMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "pulatov.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates", BASE_DIR / "templates" / "core"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                "core.context_processors.site_context",
            ],
        },
    }
]

WSGI_APPLICATION = "pulatov.wsgi.application"
ASGI_APPLICATION = "pulatov.asgi.application"

# DATABASES = {
#     "default": {
#         **env.db("DATABASE_URL"),
#         "DISABLE_SERVER_SIDE_CURSORS": True,
#         "CONN_MAX_AGE": 0,
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {
            'timeout': 30,
        },
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGES = [
    ("tg", "Тоҷикӣ"),
    ("ru", "Русский"),
    ("en", "English"),
]
LANGUAGE_CODE = "ru"
TIME_ZONE = "Asia/Dushanbe"
USE_I18N = True
USE_TZ = True

MODELTRANSLATION_LANGUAGES = ("tg", "ru", "en")
MODELTRANSLATION_DEFAULT_LANGUAGE = LANGUAGE_CODE
MODELTRANSLATION_FALLBACK_LANGUAGES = ("ru", "en")

LOCALE_PATHS = [BASE_DIR / "locale"]
FORMAT_MODULE_PATH = ["pulatov.formats"]

STATIC_URL = "/static/"
STATICFILES_DIRS: list[Path] = []
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "accounts.User"

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "resources"
LOGOUT_REDIRECT_URL = "index"

RATELIMIT_ENABLED = os.getenv("DJANGO_RATELIMIT", "0" if DEBUG else "1") == "1"
RATELIMIT_TRUST_PROXY = os.getenv("DJANGO_RATELIMIT_TRUST_PROXY", "0") == "1"
RATELIMIT_RULES = [
    {"name": "login-post", "path_regex": r"^/login/$", "methods": ["POST"], "limit": 10, "window": 300},
    {"name": "contact-post", "path_regex": r"^/contact/$", "methods": ["POST"], "limit": 10, "window": 300},
    {"name": "admissions-post", "path_regex": r"^/admissions/$", "methods": ["POST"], "limit": 6, "window": 300},
    {
        "name": "search-get",
        "path_regex": r"^/(news|clubs|events/school|events/extracurricular|achievements)/$",
        "methods": ["GET"],
        "limit": 120,
        "window": 60,
        "query_param": "q",
    },
]
USE_HTTPS = os.getenv("USE_HTTPS", "0") == "1"



SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "SAMEORIGIN"
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = USE_HTTPS
CSRF_COOKIE_SECURE = USE_HTTPS
SECURE_SSL_REDIRECT = USE_HTTPS
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

UNFOLD = {
    "SITE_TITLE": "Админ-панель школы",
    "SITE_HEADER": "core.unfold_callbacks.admin_site_header",
    "SITE_SUBHEADER": "Управление сайтом",
    "SITE_URL": "/",
    "SITE_ICON": "core.unfold_callbacks.admin_site_icon",
    "SITE_LOGO": "core.unfold_callbacks.admin_site_logo",
    "SITE_SYMBOL": "school",
    "SHOW_LANGUAGES": True,
    "LANGUAGE_FLAGS": {
        "ru": "RU",
        "tg": "TG",
        "en": "EN",
    },
    "BORDER_RADIUS": "12px",
    "COLORS": {
        "base": {
            "50": "#ffffff",
            "100": "#fbfbfb",
            "200": "#f3f4f6",
            "300": "#e5e7eb",
            "400": "#9ca3af",
            "500": "#6b7280",
            "600": "#4b5563",
            "700": "#374151",
            "800": "#1f2937",
            "900": "#0b0b0b",
            "950": "#050505",
        },
        "primary": {
            "50": "#fff6f2",
            "100": "#ffe8df",
            "200": "#ffd2c0",
            "300": "#ffb696",
            "400": "#ff966b",
            "500": "#f47a43",
            "600": "#e55f2b",
            "700": "#c64a22",
            "800": "#a23a1b",
            "900": "#7e2f17",
            "950": "#4b180b",
        },
        "font": {
            "subtle-light": "var(--color-base-500)",
            "subtle-dark": "var(--color-base-400)",
            "default-light": "var(--color-base-600)",
            "default-dark": "var(--color-base-300)",
            "important-light": "var(--color-base-900)",
            "important-dark": "var(--color-base-100)",
        },
    },
    "COMMAND": {
        "search_models": True,
        "show_history": True,
    },
    "DASHBOARD_CALLBACK": "core.admin_dashboard.dashboard",
    "STYLES": [
        "core.unfold_callbacks.admin_custom_style",
    ],
    "SIDEBAR": {
        "show_search": True,
        "command_search": True,
        "show_all_applications": False,
        "navigation": "core.unfold_callbacks.sidebar_navigation",
    },
}
