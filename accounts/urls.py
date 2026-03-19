from django.urls import path

from accounts.views import ClaimInviteView, PlayerLoginView, PlayerLogoutView, PlayerSignupView

app_name = "accounts"

urlpatterns = [
    path("signup/", PlayerSignupView.as_view(), name="signup"),
    path("login/", PlayerLoginView.as_view(), name="login"),
    path("logout/", PlayerLogoutView.as_view(), name="logout"),
    path("claim/<uuid:code>/", ClaimInviteView.as_view(), name="claim_invite"),
]
