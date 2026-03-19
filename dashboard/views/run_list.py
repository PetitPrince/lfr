from django.views.generic import ListView

from dashboard.mixins import OrganizerRequiredMixin
from runs.models import Run


class RunListView(OrganizerRequiredMixin, ListView):
    template_name = "dashboard/run_list.html"
    context_object_name = "runs"

    def get_queryset(self):
        return Run.objects.filter(is_template=False).order_by("-start_date", "-created_at")
