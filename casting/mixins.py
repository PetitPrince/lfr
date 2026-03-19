from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from casting.models import Casting
from runs.models import Run


class PlayerRequiredMixin(LoginRequiredMixin):
    login_url = "/accounts/login/"


class PlayerRunMixin(PlayerRequiredMixin):
    """Fetches run from slug, verifies player has a casting in this run."""

    def dispatch(self, request, *args, **kwargs):
        self.run = get_object_or_404(Run, slug=kwargs["slug"], is_template=False, is_active=True)
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        try:
            self.casting = Casting.objects.select_related(
                "house", "year", "path", "blood_status", "teaching_subject",
                "monitor_of_house", "monitor_of_club",
            ).prefetch_related("clubs").get(run=self.run, user=request.user)
        except Casting.DoesNotExist:
            raise PermissionDenied("You don't have a casting in this run.")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["run"] = self.run
        ctx["casting"] = self.casting
        return ctx
