# Invite-Only Registration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace open registration with an invite-link-based flow where `/<run-slug>/join/<uuid>/` is the single entry point for new players.

**Architecture:** The existing `ClaimInviteView` and `PlayerSignupView` are replaced by a single `JoinView` at `/<run-slug>/join/<uuid>/`. Unauthenticated users see casting details + signup form + social buttons. Authenticated users see casting details + confirm button. The standalone signup page and its URL are removed entirely.

**Tech Stack:** Django views, Django forms, django-allauth (social login), Pico CSS, HTMX (not needed for this feature).

**Spec:** `docs/superpowers/specs/2026-03-20-invite-only-registration-design.md`

---

### Task 1: Block allauth's built-in signup

Allauth exposes `/accounts/social/account/signup/` which allows open registration. Block it by adding `is_open_for_signup` to the account adapter.

**Files:**
- Modify: `accounts/adapter.py:5-10`
- Test: `accounts/tests.py`

- [ ] **Step 1: Write the failing test**

Add to `accounts/tests.py`:

```python
class AllauthSignupBlockedTests(TestCase):
    def test_allauth_signup_blocked(self):
        adapter = LFRAccountAdapter()
        self.assertFalse(adapter.is_open_for_signup(None))

    def test_allauth_signup_url_rejected(self):
        response = self.client.get("/accounts/social/account/signup/")
        # allauth should redirect away or show closed message, not a signup form
        self.assertNotEqual(response.status_code, 200)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python -m pytest accounts/tests.py::AllauthSignupBlockedTests -v`
Expected: FAIL — `is_open_for_signup` not defined, allauth signup returns 200.

- [ ] **Step 3: Implement `is_open_for_signup` on both adapters**

In `accounts/adapter.py`, update both adapter classes:

```python
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
```

**Why both:** `DefaultSocialAccountAdapter.is_open_for_signup` delegates to the account adapter by default. Without the override on the social adapter, setting `is_open_for_signup=False` on the account adapter would also block new accounts via Google/Discord/Facebook — breaking social login entirely.

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/python -m pytest accounts/tests.py::AllauthSignupBlockedTests -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add accounts/adapter.py accounts/tests.py
git commit -m "Block allauth built-in signup — registration is invite-only"
```

---

### Task 2: Rename SignupForm to JoinSignupForm

The form stays the same but gets renamed to reflect its new purpose — it's used on the join page, not a standalone signup page.

**Files:**
- Modify: `accounts/forms.py:13`

- [ ] **Step 1: Rename `SignupForm` to `JoinSignupForm`**

In `accounts/forms.py`, rename the class:

```python
class JoinSignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm password")

    class Meta:
        model = User
        fields = ["email"]

    def clean_password_confirm(self):
        p1 = self.cleaned_data.get("password")
        p2 = self.cleaned_data.get("password_confirm")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.role = User.Role.PLAYER
        if commit:
            user.save()
        return user
```

- [ ] **Step 2: Update the import in `accounts/views.py`**

Change line 8 from:
```python
from accounts.forms import ProfileForm, SignupForm
```
to:
```python
from accounts.forms import ProfileForm, JoinSignupForm
```

Also update `PlayerSignupView` references from `SignupForm` to `JoinSignupForm` (lines 16, 22). This view will be removed in Task 5, but keeping it working avoids broken tests in the meantime.

- [ ] **Step 3: Run full test suite to verify nothing breaks**

Run: `.venv/bin/python -m pytest --tb=short`
Expected: all 129+ tests pass.

- [ ] **Step 4: Commit**

```bash
git add accounts/forms.py accounts/views.py
git commit -m "Rename SignupForm to JoinSignupForm"
```

---

### Task 3: Create JoinView and join template (TDD)

The core of the feature — a new view that handles both signup and invite claiming.

**Files:**
- Create: `templates/player/join.html`
- Modify: `accounts/views.py` (add `JoinView`)
- Modify: `config/urls.py` (add join route)
- Test: `accounts/tests.py`

- [ ] **Step 1: Write failing tests for the join view**

Add to `accounts/tests.py`. These tests use `django.test.TestCase` and create test data inline (matching the existing test style in this file):

```python
class JoinViewTests(TestCase):
    def setUp(self):
        from runs.models import Run
        from casting.models import Casting, Invite

        self.run = Run.objects.create(name="Test Run", slug="test-run", is_active=True)
        self.casting = Casting.objects.create(
            run=self.run, role="student", character_name="Nadia Kowalski"
        )
        self.invite = Invite.objects.create(casting=self.casting)
        self.join_url = f"/{self.run.slug}/join/{self.invite.code}/"

    # --- GET unauthenticated ---

    def test_join_page_shows_casting_details_unauthenticated(self):
        response = self.client.get(self.join_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nadia Kowalski")
        self.assertContains(response, "Test Run")

    def test_join_page_shows_signup_form_unauthenticated(self):
        response = self.client.get(self.join_url)
        self.assertContains(response, 'name="email"')
        self.assertContains(response, 'name="password"')
        self.assertContains(response, 'name="password_confirm"')

    def test_join_page_shows_social_buttons_unauthenticated(self):
        response = self.client.get(self.join_url)
        content = response.content.decode()
        self.assertIn("Google", content)
        self.assertIn("Discord", content)
        self.assertIn("Facebook", content)

    def test_join_page_social_buttons_preserve_next(self):
        response = self.client.get(self.join_url)
        content = response.content.decode()
        self.assertIn(f"next=", content)

    def test_join_page_shows_login_link_unauthenticated(self):
        response = self.client.get(self.join_url)
        self.assertContains(response, "Already have an account?")
        self.assertContains(response, "/accounts/login/")

    # --- GET authenticated ---

    def test_join_page_shows_confirm_button_authenticated(self):
        User.objects.create_user(email="p@test.com", password="testpass123")
        self.client.login(email="p@test.com", password="testpass123")
        response = self.client.get(self.join_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nadia Kowalski")
        self.assertContains(response, "Join as")

    # --- POST signup (unauthenticated) ---

    def test_signup_via_join_creates_player(self):
        response = self.client.post(self.join_url, {
            "email": "new@test.com",
            "password": "testpass123",
            "password_confirm": "testpass123",
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(email="new@test.com")
        self.assertEqual(user.role, "player")

    def test_signup_via_join_redirects_back_to_join(self):
        response = self.client.post(self.join_url, {
            "email": "new@test.com",
            "password": "testpass123",
            "password_confirm": "testpass123",
        })
        self.assertRedirects(response, self.join_url, fetch_redirect_response=False)

    def test_signup_via_join_logs_user_in(self):
        self.client.post(self.join_url, {
            "email": "new@test.com",
            "password": "testpass123",
            "password_confirm": "testpass123",
        })
        response = self.client.get(self.join_url)
        # Now authenticated — should see confirm button, not signup form
        self.assertContains(response, "Join as")
        self.assertNotContains(response, 'name="password_confirm"')

    # --- POST confirm (authenticated) ---

    def test_confirm_claims_invite(self):
        user = User.objects.create_user(email="p@test.com", password="testpass123")
        self.client.login(email="p@test.com", password="testpass123")
        response = self.client.post(self.join_url)
        self.casting.refresh_from_db()
        self.invite.refresh_from_db()
        self.assertEqual(self.casting.user, user)
        self.assertIsNotNone(self.invite.claimed_at)

    def test_confirm_redirects_to_message_board(self):
        User.objects.create_user(email="p@test.com", password="testpass123")
        self.client.login(email="p@test.com", password="testpass123")
        response = self.client.post(self.join_url)
        self.assertRedirects(
            response,
            f"/post/{self.run.slug}/",
            fetch_redirect_response=False,
        )

    # --- Validation ---

    def test_already_claimed_shows_error(self):
        other_user = User.objects.create_user(email="other@test.com", password="testpass123")
        self.casting.user = other_user
        self.casting.save()
        response = self.client.get(self.join_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already been claimed")

    def test_already_in_run_shows_error(self):
        from casting.models import Casting
        user = User.objects.create_user(email="p@test.com", password="testpass123")
        Casting.objects.create(run=self.run, user=user, character_name="Other Char")
        self.client.login(email="p@test.com", password="testpass123")
        response = self.client.get(self.join_url)
        self.assertContains(response, "already have a character")

    def test_wrong_run_slug_returns_404(self):
        response = self.client.get(f"/wrong-slug/join/{self.invite.code}/")
        self.assertEqual(response.status_code, 404)

    def test_inactive_run_returns_404(self):
        self.run.is_active = False
        self.run.save()
        response = self.client.get(self.join_url)
        self.assertEqual(response.status_code, 404)

    def test_concurrent_confirm_handled_gracefully(self):
        from unittest.mock import patch
        from casting.models import Casting
        user = User.objects.create_user(email="p@test.com", password="testpass123")
        self.client.login(email="p@test.com", password="testpass123")
        # Mock the exists() check to return False (simulating race: another tab claimed between check and save)
        with patch.object(Casting.objects, "filter") as mock_filter:
            mock_filter.return_value.exists.return_value = False
            # But the save will hit the unique constraint because we link user to run right now
            Casting.objects.create(run=self.run, user=user, character_name="Race Winner")
            response = self.client.post(self.join_url)
        # Should not crash — friendly error
        self.assertIn(response.status_code, [200, 302])
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python -m pytest accounts/tests.py::JoinViewTests -v`
Expected: FAIL — URL does not exist yet.

- [ ] **Step 3: Create the join template**

Create `templates/player/join.html`:

```html
<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Join {{ casting.run.name }} — LFR</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css">
</head>
<body>
    <main class="container" style="max-width: 500px; margin-top: 6vh;">
        <article>
            <header>
                <h2>Join {{ casting.run.name }}</h2>
            </header>

            {% if error %}
            <p style="color: var(--pico-del-color);">{{ error }}</p>
            {% endif %}

            {# --- Casting details --- #}
            <table>
                <tr><th>Character Name</th><td>{{ casting.character_name }}</td></tr>
                <tr><th>Role</th><td>{{ casting.get_role_display }}</td></tr>
                {% if casting.house %}<tr><th>House</th><td>{{ casting.house }}</td></tr>{% endif %}
                {% if casting.year %}<tr><th>Year</th><td>{{ casting.year }}</td></tr>{% endif %}
                {% if casting.path %}<tr><th>Path</th><td>{{ casting.path }}</td></tr>{% endif %}
                {% if casting.blood_status %}<tr><th>Blood Status</th><td>{{ casting.blood_status }}</td></tr>{% endif %}
                {% if casting.teaching_subject %}<tr><th>Teaching Subject</th><td>{{ casting.teaching_subject }}</td></tr>{% endif %}
                {% if casting.staff_title %}<tr><th>Title</th><td>{{ casting.staff_title }}</td></tr>{% endif %}
            </table>

            {% if not error %}
                {% if user.is_authenticated %}
                {# --- Authenticated: confirm --- #}
                <form method="post">
                    {% csrf_token %}
                    <button type="submit">Join as {{ casting.character_name }}</button>
                </form>

                {% else %}
                {# --- Unauthenticated: signup form + social + login link --- #}
                <hr>
                <h3>Create an account to join</h3>

                {% if form.errors %}
                {% for field, errors in form.errors.items %}
                {% for err in errors %}
                <p style="color: var(--pico-del-color);">{{ err }}</p>
                {% endfor %}
                {% endfor %}
                {% endif %}

                <form method="post">
                    {% csrf_token %}
                    <label for="id_email">Email</label>
                    <input type="email" name="email" id="id_email" value="{{ form.email.value|default:'' }}" required autofocus>

                    <label for="id_password">Password</label>
                    <input type="password" name="password" id="id_password" required>

                    <label for="id_password_confirm">Confirm Password</label>
                    <input type="password" name="password_confirm" id="id_password_confirm" required>

                    <button type="submit">Sign up</button>
                </form>

                {% load socialaccount %}
                <hr>
                <p style="text-align:center; opacity:0.7; font-size:0.9em;">Or continue with</p>
                <div style="display:flex; flex-direction:column; gap:0.5em;">
                    <a href="{% provider_login_url 'google' next=request.path %}" role="button" class="outline">Google</a>
                    <a href="{% provider_login_url 'discord' next=request.path %}" role="button" class="outline">Discord</a>
                    <a href="{% provider_login_url 'facebook' next=request.path %}" role="button" class="outline">Facebook</a>
                </div>

                <p style="text-align:center; margin-top:1em;">Already have an account? <a href="/accounts/login/?next={{ request.path|urlencode }}">Log in</a></p>
                {% endif %}
            {% endif %}
        </article>
    </main>
</body>
</html>
```

- [ ] **Step 4: Implement `JoinView`**

Add to `accounts/views.py`:

```python
from django.db import IntegrityError

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

        # Confirm flow (authenticated)
        if Casting.objects.filter(user=request.user, run=casting.run).exists():
            context["error"] = "You already have a character in this run."
            return render(request, "player/join.html", context)

        try:
            casting.user = request.user
            casting.save()
        except IntegrityError:
            context["error"] = "You already have a character in this run."
            return render(request, "player/join.html", context)

        invite.claimed_at = timezone.now()
        invite.save()
        messages.success(request, f"Welcome! You've joined {casting.run.name}.")
        return redirect("posts:message_board", slug=casting.run.slug)
```

Also update the import at the top of `accounts/views.py`:

```python
from django.db import IntegrityError
```

- [ ] **Step 5: Add URL route in `config/urls.py`**

Add **after** all prefix-based includes (before the `if settings.DEBUG` block):

```python
from accounts.views import JoinView

# ... existing urlpatterns ...
urlpatterns = [
    path("", landing, name="landing"),
    path("admin/", admin.site.urls),
    path("organize/", include("dashboard.urls")),
    path("accounts/social/", include("allauth.urls")),
    path("accounts/", include("accounts.urls")),
    path("runs/", include("runs.urls")),
    path("post/", include("posts.urls")),
    path("casting/", include("casting.urls")),
    path("<slug:slug>/join/<uuid:code>/", JoinView.as_view(), name="join"),
]
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `.venv/bin/python -m pytest accounts/tests.py::JoinViewTests -v`
Expected: all JoinViewTests pass.

- [ ] **Step 7: Run full test suite**

Run: `.venv/bin/python -m pytest --tb=short`
Expected: all tests pass (existing tests still work since old views haven't been removed yet).

- [ ] **Step 8: Commit**

```bash
git add accounts/views.py config/urls.py templates/player/join.html accounts/tests.py
git commit -m "Add JoinView — invite-link-based signup and claim in one flow"
```

---

### Task 4: Remove old signup and claim views, URLs, and templates

Now that the join view is in place, remove the old code.

**Files:**
- Modify: `accounts/views.py` (remove `PlayerSignupView`, `ClaimInviteView`)
- Modify: `accounts/urls.py` (remove `signup/`, `claim/` routes)
- Delete: `templates/player/signup.html`
- Delete: `templates/player/claim_invite.html`
- Modify: `accounts/tests.py` (remove/rewrite broken tests, add 404 test)

- [ ] **Step 1: Remove old views from `accounts/views.py`**

Delete the `PlayerSignupView` class (lines 12-30) and the `ClaimInviteView` class (lines 65-100). Remove the `SignupForm` / `JoinSignupForm` import if it's no longer used here (it's now only used by `JoinView` which is in the same file, so keep the import).

The resulting imports should be:

```python
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View

from accounts.forms import JoinSignupForm, ProfileForm
from casting.models import Casting, Invite
```

Keep: `ProfileView`, `PlayerLoginView`, `PlayerLogoutView`, `JoinView`.

- [ ] **Step 2: Remove old URL routes from `accounts/urls.py`**

```python
from django.urls import path

from accounts.views import PlayerLoginView, PlayerLogoutView, ProfileView

app_name = "accounts"

urlpatterns = [
    path("login/", PlayerLoginView.as_view(), name="login"),
    path("logout/", PlayerLogoutView.as_view(), name="logout"),
    path("profile/", ProfileView.as_view(), name="profile"),
]
```

- [ ] **Step 3: Delete old templates**

```bash
rm templates/player/signup.html
rm templates/player/claim_invite.html
```

- [ ] **Step 4: Update tests — remove broken tests, add signup-404 test**

In `accounts/tests.py`:

Remove these tests:
- `SocialLoginButtonTests.test_signup_page_has_social_buttons` (references `accounts:signup`)
- `SocialLoginNextParameterTests.test_signup_social_buttons_preserve_next` (references `accounts:signup`)

Keep `AccountAdapterRedirectTests.test_signup_redirect` — it documents the fallback behavior of the kept method.

Add to existing or new test class:

```python
class SignupRemovedTests(TestCase):
    def test_signup_url_returns_404(self):
        response = self.client.get("/accounts/signup/")
        self.assertEqual(response.status_code, 404)
```

- [ ] **Step 5: Run full test suite**

Run: `.venv/bin/python -m pytest --tb=short`
Expected: all tests pass. Some test count will decrease (removed tests) but no failures.

- [ ] **Step 6: Commit**

```bash
git add accounts/views.py accounts/urls.py accounts/tests.py
git rm templates/player/signup.html templates/player/claim_invite.html
git commit -m "Remove standalone signup and old claim views — replaced by JoinView"
```

---

### Task 5: Update landing page and login page

Remove signup references from the landing page and login page.

**Files:**
- Modify: `templates/player/landing.html`
- Modify: `templates/player/login.html`
- Test: `accounts/tests.py`

- [ ] **Step 1: Write failing tests**

Add to `accounts/tests.py`:

```python
class LandingPageInviteOnlyTests(TestCase):
    def test_landing_has_no_signup_button(self):
        response = self.client.get(reverse("landing"))
        content = response.content.decode()
        self.assertNotIn("Sign up", content)

    def test_landing_has_no_social_buttons(self):
        response = self.client.get(reverse("landing"))
        content = response.content.decode()
        self.assertNotIn("provider_login_url", content)

    def test_landing_has_login_button(self):
        response = self.client.get(reverse("landing"))
        self.assertContains(response, "Log in")

    def test_landing_mentions_invite(self):
        response = self.client.get(reverse("landing"))
        self.assertContains(response, "invite")


class LoginPageInviteOnlyTests(TestCase):
    def test_login_page_has_no_signup_link(self):
        response = self.client.get(reverse("accounts:login"))
        content = response.content.decode()
        self.assertNotIn("Sign up", content)
        self.assertNotIn("Don't have an account?", content)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python -m pytest accounts/tests.py::LandingPageInviteOnlyTests accounts/tests.py::LoginPageInviteOnlyTests -v`
Expected: FAIL — landing still has signup button and social buttons, login still has signup link.

- [ ] **Step 3: Update `templates/player/landing.html`**

Replace the hero `actions` div and social buttons with login-only:

```html
            <div class="actions">
                <a href="{% url 'accounts:login' %}" role="button">Log in</a>
            </div>
            <p style="opacity:0.7; font-size:0.9em; margin-top:1em;">Got an invite link? Use it to join your run.</p>
```

Remove the `{% load socialaccount %}` tag and all social button `<a>` tags from the landing page.

- [ ] **Step 4: Update `templates/player/login.html`**

Remove the "Don't have an account? Sign up" paragraph at the bottom. Keep everything else (email/password form + social login buttons — social login is still useful for returning users).

- [ ] **Step 5: Run tests to verify they pass**

Run: `.venv/bin/python -m pytest accounts/tests.py::LandingPageInviteOnlyTests accounts/tests.py::LoginPageInviteOnlyTests -v`
Expected: PASS

- [ ] **Step 6: Also update the `SocialLoginButtonTests`**

The `test_landing_page_has_social_buttons` test now expects the opposite behavior. Remove it (landing no longer has social buttons). The `test_login_page_has_social_buttons` and `test_dashboard_login_has_no_social_buttons` tests remain valid.

- [ ] **Step 7: Run full test suite**

Run: `.venv/bin/python -m pytest --tb=short`
Expected: all tests pass.

- [ ] **Step 8: Commit**

```bash
git add templates/player/landing.html templates/player/login.html accounts/tests.py
git commit -m "Update landing and login pages for invite-only registration"
```

---

### Task 6: Update dashboard invite templates to show full URLs

Organizers need to copy full invite URLs, not raw UUID codes.

**Files:**
- Modify: `templates/dashboard/invites/list.html:35,47`
- Modify: `templates/dashboard/invites/_generated.html:15,19`
- Test: `dashboard/tests/test_views_invites.py`

- [ ] **Step 1: Write failing test**

Add to `TestInviteListView` in `dashboard/tests/test_views_invites.py` (uses pytest fixtures, not Django TestCase):

```python
def test_invite_list_shows_full_join_url(self, organizer_client, run):
    casting = CastingFactory(run=run, character_name="Nadia")
    invite = InviteFactory(casting=casting)
    resp = organizer_client.get(f"/organize/{run.slug}/invites/")
    expected_path = f"/{run.slug}/join/{invite.code}/"
    assert expected_path in resp.content.decode()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest dashboard/tests/test_views_invites.py -k "full_join_url" -v`
Expected: FAIL — template still shows raw UUID.

- [ ] **Step 3: Update `templates/dashboard/invites/list.html`**

Change line 35 from:
```html
<td><code>{{ invite.code }}</code></td>
```
to:
```html
<td><code>/{{ invite.casting.run.slug }}/join/{{ invite.code }}/</code></td>
```

Change line 47 from:
```html
onclick="copyToClipboard('{{ invite.code }}', this)">
```
to:
```html
onclick="copyToClipboard('{{ request.scheme }}://{{ request.get_host }}/{{ invite.casting.run.slug }}/join/{{ invite.code }}/', this)">
```

- [ ] **Step 4: Update `templates/dashboard/invites/_generated.html`**

Change line 15 from:
```html
<td><code>{{ invite.code }}</code></td>
```
to:
```html
<td><code>/{{ invite.casting.run.slug }}/join/{{ invite.code }}/</code></td>
```

Change line 19 from:
```html
onclick="copyToClipboard('{{ invite.code }}', this)">
```
to:
```html
onclick="copyToClipboard('{{ request.scheme }}://{{ request.get_host }}/{{ invite.casting.run.slug }}/join/{{ invite.code }}/', this)">
```

- [ ] **Step 5: Run test to verify it passes**

Run: `.venv/bin/python -m pytest dashboard/tests/test_views_invites.py -k "full_join_url" -v`
Expected: PASS

- [ ] **Step 6: Run full test suite**

Run: `.venv/bin/python -m pytest --tb=short`
Expected: all tests pass.

- [ ] **Step 7: Commit**

```bash
git add templates/dashboard/invites/list.html templates/dashboard/invites/_generated.html dashboard/tests/test_views_invites.py
git commit -m "Dashboard invite templates show full join URLs instead of raw UUIDs"
```

---

### Task 7: Final cleanup and full verification

Verify everything works together and clean up any remaining references.

**Files:**
- Possibly: any file with stale references to `accounts:signup` or `accounts:claim_invite`

- [ ] **Step 1: Search for stale references**

```bash
grep -r "accounts:signup\|accounts:claim_invite\|/accounts/signup\|/accounts/claim/" --include="*.py" --include="*.html" .
```

Fix any remaining references found. Common places: other templates, views that redirect to signup, etc.

- [ ] **Step 2: Run full test suite**

Run: `.venv/bin/python -m pytest --tb=short`
Expected: all tests pass.

- [ ] **Step 3: Run Django system checks**

Run: `.venv/bin/python manage.py check`
Expected: no errors.

- [ ] **Step 4: Commit any remaining fixes**

```bash
git add -A
git commit -m "Clean up stale references to removed signup and claim URLs"
```
