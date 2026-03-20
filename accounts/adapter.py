from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class LFRAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        return "/runs/"

    def get_signup_redirect_url(self, request):
        return "/runs/"


class LFRSocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        user.role = "player"
        user.save(update_fields=["role"])
        return user

    def is_auto_signup_allowed(self, request, sociallogin):
        return True
