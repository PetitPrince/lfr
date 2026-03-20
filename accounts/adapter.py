from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class LFRAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        """Standalone signup is disabled. Players register through invite links only."""
        return False

    def get_login_redirect_url(self, request):
        return "/runs/"

    def get_signup_redirect_url(self, request):
        # Standalone signup is removed. Kept as fallback for allauth internals
        # (e.g. social login flows that call this before the next param kicks in).
        return "/runs/"


class LFRSocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request, sociallogin):
        """Social signup is allowed — accounts created via OAuth are gated by invite links."""
        return True

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        user.role = "player"
        user.save(update_fields=["role"])
        return user

    def is_auto_signup_allowed(self, request, sociallogin):
        return True
