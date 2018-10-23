from django.conf import settings
from django.urls import include, path
from django.contrib import admin

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path(
        "api/v1/",
        include("invoice_api.core.urls_api", namespace="api")

    ),
]
