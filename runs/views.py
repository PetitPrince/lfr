from django.views.generic import ListView

from casting.mixins import PlayerRequiredMixin
from casting.models import Casting


class PlayerRunListView(PlayerRequiredMixin, ListView):
    template_name = "player/run_list.html"
    context_object_name = "castings"

    def get_queryset(self):
        return (
            Casting.objects.filter(user=self.request.user, run__is_active=True, run__is_template=False)
            .select_related("run", "house", "year", "path")
            .order_by("-run__start_date")
        )
