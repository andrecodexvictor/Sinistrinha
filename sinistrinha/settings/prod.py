from .base import *
from datetime import timedelta

DEBUG = False
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['.vercel.app'])

CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=["https://sinistrinha.com"])

# ── TLS / Transport Security ──────────────────────────────────────────────
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

# ── HSTS (M4) ─────────────────────────────────────────────────────────────
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

# ── Cookie Hardening ──────────────────────────────────────────────────────
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"

# ── JWT tightening ────────────────────────────────────────────────────────
SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"] = timedelta(minutes=15)

# ── Content Security Policy ───────────────────────────────────────────────
CSP_DEFAULT_SRC = ("'self'",)
CSP_IMG_SRC = ("'self'", "https://your-bucket-url.supabase.co")
CSP_SCRIPT_SRC = ("'self'",)
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")

# ── Frame Options ─────────────────────────────────────────────────────────
X_FRAME_OPTIONS = "DENY"
