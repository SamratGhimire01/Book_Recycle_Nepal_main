# bookrecycle_nepal/urls.py

from django.contrib import admin
from django.urls import path, include

# --- ADD THESE TWO IMPORTS ---
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
]

# --- ADD THIS BLOCK AT THE END OF THE FILE ---
# This tells Django to serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)