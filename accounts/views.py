from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View

from accounts.forms import ProfileForm, JoinSignupForm
from casting.models import Casting, Invite


class PlayerSignupView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("runs:run_list")
        form = JoinSignupForm()
        return render(request, "player/signup.html", {"form": form})

    def post(self, request):
        if request.user.is_authenticated:
            return redirect("runs:run_list")
        form = JoinSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            next_url = request.GET.get("next", "")
            if next_url:
                return redirect(next_url)
            return redirect("runs:run_list")
        return render(request, "player/signup.html", {"form": form})


class ProfileView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect(f"/accounts/login/?next={request.path}")
        form = ProfileForm(instance=request.user)
        if not request.user.contact_email:
            form.initial["contact_email"] = request.user.email
        return render(request, "player/profile.html", {"form": form})

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect(f"/accounts/login/?next={request.path}")
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
        return self.request.GET.get("next", "/runs/")


class PlayerLogoutView(LogoutView):
    next_page = "/accounts/login/"


class ClaimInviteView(View):
    def get(self, request, code):
        invite = get_object_or_404(
            Invite.objects.select_related("casting__run", "casting__house", "casting__year", "casting__path"),
            code=code,
        )
        if invite.is_claimed:
            messages.error(request, "This invite has already been claimed.")
            return redirect("accounts:login")
        if not request.user.is_authenticated:
            return redirect(f"/accounts/login/?next=/accounts/claim/{code}/")
        # Check if user already has a casting in this run
        if Casting.objects.filter(user=request.user, run=invite.casting.run).exists():
            messages.error(request, "You already have a character in this run.")
            return redirect("runs:run_list")
        return render(request, "player/claim_invite.html", {"invite": invite, "casting": invite.casting})

    def post(self, request, code):
        invite = get_object_or_404(
            Invite.objects.select_related("casting__run"),
            code=code,
        )
        if not request.user.is_authenticated:
            return redirect(f"/accounts/login/?next=/accounts/claim/{code}/")
        if invite.is_claimed:
            messages.error(request, "This invite has already been claimed.")
            return redirect("accounts:login")
        if Casting.objects.filter(user=request.user, run=invite.casting.run).exists():
            messages.error(request, "You already have a character in this run.")
            return redirect("runs:run_list")
        invite.casting.user = request.user
        invite.casting.save()
        invite.claimed_at = timezone.now()
        invite.save()
        messages.success(request, f"Welcome! You've joined {invite.casting.run.name}.")
        return redirect("posts:message_board", slug=invite.casting.run.slug)
