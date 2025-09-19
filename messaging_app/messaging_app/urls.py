#!/usr/bin/env python3
"""
Project-level URL routing for messaging_app.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("chats.urls")),          # ✅ API endpoints
    path("api-auth/", include("rest_framework.urls")),  # ✅ DRF login/logout
]
