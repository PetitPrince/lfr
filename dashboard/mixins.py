from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404

from runs.models import Run


class OrganizerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = "/organize/login/"

    def test_func(self):
        return self.request.user.role in ("organizer", "admin")


class RunMixin(OrganizerRequiredMixin):
    """Fetches the run from URL slug and makes it available as self.run."""

    def dispatch(self, request, *args, **kwargs):
        self.run = get_object_or_404(Run, slug=kwargs["slug"], is_template=False)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["run"] = self.run
        return ctx
