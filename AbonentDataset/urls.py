"""
URL configuration for AbonentDataset project.

Main URL routing for admin, API, inspector frontend, and media files.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from abonents.urls import inspector_patterns, custom_admin_patterns

urlpatterns = [
    # Admin panel (Django default) - HIDDEN
    # path('admin/', admin.site.urls),
    
    # Custom Admin Panel
    path('boshqaruv/', include(custom_admin_patterns)),
    
    # API endpoints
    path('api/', include('abonents.urls')),
    
    # Inspector frontend
    path('', include(inspector_patterns)),
]

# Media files serving (development only)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
