from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect, render
from django.urls import include, path

from accounts.views import JoinView


def landing(request):
    if request.user.is_authenticated:
        return redirect("runs:run_list")
    return render(request, "player/landing.html")


urlpatterns = [
    path("", landing, name="landing"),
    path("admin/", admin.site.urls),
    path("organize/", include("dashboard.urls")),
    path("accounts/social/", include("allauth.urls")),
    path("accounts/", include("accounts.urls")),
    path("runs/", include("runs.urls")),
    path("post/", include("posts.urls")),
    path("casting/", include("casting.urls")),
    path("<slug:slug>/join/<uuid:code>/", JoinView.as_view(), name="join"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
