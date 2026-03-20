from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from apps.game.admin import CasinoDashboardAdminSite

# Custom admin site with casino dashboard
admin_site = CasinoDashboardAdminSite(name='admin')

# Auto-discover admin registrations
from django.contrib import admin as django_admin
admin_site._registry = django_admin.site._registry

urlpatterns = [
    path('admin/', admin_site.urls),
    # OpenAPI Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # Apps URLs
    path('api/', include('apps.users.urls')),
    path('api/game/', include('apps.game.urls')),
    path('api/payments/', include('apps.payments.urls')),
]
