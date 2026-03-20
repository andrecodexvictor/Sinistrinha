from .base import *

DEBUG = False
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['.vercel.app'])

CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=["https://sinistrinha.com"])

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True

CSP_DEFAULT_SRC = ("'self'",)
CSP_IMG_SRC = ("'self'", "https://your-bucket-url.supabase.co")
CSP_SCRIPT_SRC = ("'self'",)
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
