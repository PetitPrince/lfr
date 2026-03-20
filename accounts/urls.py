from django.urls import path

from accounts.views import PlayerLoginView, PlayerLogoutView, ProfileView

app_name = "accounts"

urlpatterns = [
    path("login/", PlayerLoginView.as_view(), name="login"),
    path("logout/", PlayerLogoutView.as_view(), name="logout"),
    path("profile/", ProfileView.as_view(), name="profile"),
]
