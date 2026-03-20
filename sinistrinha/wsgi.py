import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sinistrinha.settings.dev')

target_application = get_wsgi_application()

def application(environ, start_response):
    return target_application(environ, start_response)

# Vercel serverless expectation
app = application
