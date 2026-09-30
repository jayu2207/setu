from django.contrib import admin
from django.urls import path, include, re_path

from api.views_frontend import frontend

urlpatterns = [
    path('django-admin/', admin.site.urls),  # Django's own admin site (kept out of the way of /api/admin routes)
    path('api/', include('api.urls')),

    # ---------- serve the frontend for everything else (SPA-style fallback) ----------
    re_path(r'^(?P<path>.*)$', frontend),
]
