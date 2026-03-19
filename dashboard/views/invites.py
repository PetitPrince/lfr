from django.contrib import messages
from django.shortcuts import render
from django.views import View

from casting.models import Invite
from dashboard.mixins import RunMixin


class InviteListView(RunMixin, View):
    def get(self, request, slug):
        invites = Invite.objects.filter(
            casting__run=self.run
        ).select_related("casting", "casting__user").order_by("-created_at")
        return render(request, "dashboard/invites/list.html", {
            "run": self.run,
            "invites": invites,
        })


class InviteGenerateView(RunMixin, View):
    """Generate invite codes for all castings that don't have one."""

    def post(self, request, slug):
        castings_without_invites = self.run.castings.filter(invite__isnull=True)
        new_invites = []
        for casting in castings_without_invites:
            invite = Invite.objects.create(casting=casting)
            new_invites.append(invite)

        if new_invites:
            messages.success(request, f"{len(new_invites)} invite code(s) generated.")
        else:
            messages.info(request, "All castings already have invite codes.")

        return render(request, "dashboard/invites/_generated.html", {
            "run": self.run,
            "new_invites": new_invites,
        })
