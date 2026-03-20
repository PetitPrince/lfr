from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("organize/", include("dashboard.urls")),
    path("accounts/", include("accounts.urls")),
    path("runs/", include("runs.urls")),
    path("post/", include("posts.urls")),
    path("casting/", include("casting.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
