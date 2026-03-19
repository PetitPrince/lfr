from django.contrib.auth.views import LoginView, LogoutView


class DashboardLoginView(LoginView):
    template_name = "dashboard/login.html"
    redirect_authenticated_user = True

    def get_default_redirect_url(self):
        return "/organize/"


class DashboardLogoutView(LogoutView):
    next_page = "/organize/login/"
