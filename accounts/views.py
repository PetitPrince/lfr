from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View

from accounts.forms import JoinSignupForm, ProfileForm
from casting.models import Casting, Invite


class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        form = ProfileForm(instance=request.user)
        if not request.user.contact_email:
            form.initial["contact_email"] = request.user.email
        return render(request, "player/profile.html", {"form": form})

    def post(self, request):
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("accounts:profile")
        return render(request, "player/profile.html", {"form": form})


class PlayerLoginView(LoginView):
    template_name = "player/login.html"
    redirect_authenticated_user = True

    def get_default_redirect_url(self):
        next_url = self.request.GET.get("next", "")
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={self.request.get_host()}):
            return next_url
        return "/runs/"


class PlayerLogoutView(LogoutView):
    next_page = "/accounts/login/"


class JoinView(View):
    def _get_invite_or_404(self, slug, code):
        invite = get_object_or_404(
            Invite.objects.select_related(
                "casting__run", "casting__house", "casting__year",
                "casting__path", "casting__blood_status",
                "casting__teaching_subject",
            ),
            code=code,
            casting__run__slug=slug,
            casting__run__is_active=True,
        )
        return invite

    def get(self, request, slug, code):
        invite = self._get_invite_or_404(slug, code)
        casting = invite.casting
        context = {"invite": invite, "casting": casting}

        if invite.is_claimed:
            context["error"] = "This invite has already been claimed."
            return render(request, "player/join.html", context)

        if request.user.is_authenticated:
            if Casting.objects.filter(user=request.user, run=casting.run).exists():
                context["error"] = "You already have a character in this run."
                return render(request, "player/join.html", context)
        else:
            context["form"] = JoinSignupForm()

        return render(request, "player/join.html", context)

    def post(self, request, slug, code):
        invite = self._get_invite_or_404(slug, code)
        casting = invite.casting
        context = {"invite": invite, "casting": casting}

        if invite.is_claimed:
            context["error"] = "This invite has already been claimed."
            return render(request, "player/join.html", context)

        if not request.user.is_authenticated:
            # Signup flow
            form = JoinSignupForm(request.POST)
            if form.is_valid():
                user = form.save()
                login(request, user, backend="django.contrib.auth.backends.ModelBackend")
                return redirect(request.path)
            context["form"] = form
            return render(request, "player/join.html", context)

        # Confirm flow (authenticated) — atomic update prevents race condition
        if Casting.objects.filter(user=request.user, run=casting.run).exists():
            context["error"] = "You already have a character in this run."
            return render(request, "player/join.html", context)

        try:
            updated = Casting.objects.filter(pk=casting.pk, user__isnull=True).update(user=request.user)
            if not updated:
                context["error"] = "This invite has already been claimed."
                return render(request, "player/join.html", context)
        except IntegrityError:
            context["error"] = "You already have a character in this run."
            return render(request, "player/join.html", context)

        invite.claimed_at = timezone.now()
        invite.save()
        messages.success(request, f"Welcome! You've joined {casting.run.name}.")
        return redirect("posts:message_board", slug=casting.run.slug)
