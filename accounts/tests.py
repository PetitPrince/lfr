from unittest.mock import patch

from django.test import TestCase, Client
from django.urls import reverse

from accounts.adapter import LFRAccountAdapter, LFRSocialAccountAdapter
from accounts.models import User


class ProfileViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email="player@test.com", password="testpass123")
        self.profile_url = reverse("accounts:profile")

    def test_profile_requires_login(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_profile_loads_for_authenticated_user(self):
        self.client.login(email="player@test.com", password="testpass123")
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "discord")

    def test_contact_email_prefilled_from_account_email(self):
        self.client.login(email="player@test.com", password="testpass123")
        response = self.client.get(self.profile_url)
        form = response.context["form"]
        self.assertEqual(form.initial.get("contact_email") or form["contact_email"].value(), "player@test.com")

    def test_contact_email_not_overwritten_if_already_set(self):
        self.user.contact_email = "other@test.com"
        self.user.save()
        self.client.login(email="player@test.com", password="testpass123")
        response = self.client.get(self.profile_url)
        form = response.context["form"]
        self.assertEqual(form["contact_email"].value(), "other@test.com")

    def test_profile_saves_social_links(self):
        self.client.login(email="player@test.com", password="testpass123")
        response = self.client.post(self.profile_url, {
            "contact_email": "public@test.com",
            "discord_username": "player#1234",
            "facebook_url": "https://facebook.com/player",
            "instagram_url": "https://instagram.com/player",
        })
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.contact_email, "public@test.com")
        self.assertEqual(self.user.discord_username, "player#1234")
        self.assertEqual(self.user.facebook_url, "https://facebook.com/player")
        self.assertEqual(self.user.instagram_url, "https://instagram.com/player")

    def test_profile_rejects_invalid_urls(self):
        self.client.login(email="player@test.com", password="testpass123")
        response = self.client.post(self.profile_url, {
            "contact_email": "",
            "discord_username": "",
            "facebook_url": "not-a-url",
            "instagram_url": "",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context["form"], "facebook_url", ["Enter a valid URL."])

    def test_profile_allows_blank_fields(self):
        self.client.login(email="player@test.com", password="testpass123")
        response = self.client.post(self.profile_url, {
            "contact_email": "",
            "discord_username": "",
            "facebook_url": "",
            "instagram_url": "",
        })
        self.assertEqual(response.status_code, 302)


class ContactLinksDisplayTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.author = User.objects.create_user(email="author@test.com", password="testpass123")
        self.viewer = User.objects.create_user(email="viewer@test.com", password="testpass123")

    def _create_post_with_casting(self):
        from runs.models import Run
        from casting.models import Casting
        from posts.models import Post

        run = Run.objects.create(name="Test Run", slug="test-run")
        Casting.objects.create(run=run, user=self.viewer, character_name="Viewer Char")
        casting = Casting.objects.create(run=run, user=self.author, character_name="Test Char")
        post = Post.objects.create(run=run, author=self.author, casting=casting, post_type="character", content="Hello")
        return run, post

    def test_contact_links_shown_when_author_has_social(self):
        self.author.discord_username = "author_discord"
        self.author.contact_email = "author@public.com"
        self.author.save()
        run, post = self._create_post_with_casting()
        self.client.login(email="viewer@test.com", password="testpass123")
        response = self.client.get(reverse("posts:post_detail", kwargs={"slug": run.slug, "pk": post.pk}))
        self.assertContains(response, "author_discord")
        self.assertContains(response, "author@public.com")

    def test_contact_links_hidden_when_author_has_no_social(self):
        run, post = self._create_post_with_casting()
        self.client.login(email="viewer@test.com", password="testpass123")
        response = self.client.get(reverse("posts:post_detail", kwargs={"slug": run.slug, "pk": post.pk}))
        self.assertNotContains(response, "contact-links")


class SocialLoginButtonTests(TestCase):
    def test_login_page_has_social_buttons(self):
        response = self.client.get(reverse("accounts:login"))
        content = response.content.decode()
        self.assertIn("Google", content)
        self.assertIn("Discord", content)
        self.assertIn("Facebook", content)

    def test_dashboard_login_has_no_social_buttons(self):
        response = self.client.get(reverse("dashboard:login"))
        content = response.content.decode()
        self.assertNotIn("provider_login_url", content)
        self.assertNotIn("socialaccount", content)


class SocialAccountAdapterTests(TestCase):
    def test_save_user_sets_role_player(self):
        adapter = LFRSocialAccountAdapter()
        saved_user = User.objects.create_user(email="social@test.com", password="testpass123")

        with patch.object(
            LFRSocialAccountAdapter.__bases__[0], "save_user", return_value=saved_user
        ):
            user = adapter.save_user(None, None, form=None)
        self.assertEqual(user.role, "player")

    def test_is_auto_signup_allowed(self):
        adapter = LFRSocialAccountAdapter()
        self.assertTrue(adapter.is_auto_signup_allowed(None, None))


class AccountAdapterRedirectTests(TestCase):
    def test_login_redirect(self):
        adapter = LFRAccountAdapter()
        self.assertEqual(adapter.get_login_redirect_url(None), "/runs/")

    def test_signup_redirect(self):
        adapter = LFRAccountAdapter()
        self.assertEqual(adapter.get_signup_redirect_url(None), "/runs/")


class SocialLoginNextParameterTests(TestCase):
    def test_login_social_buttons_preserve_next(self):
        response = self.client.get(reverse("accounts:login") + "?next=/accounts/claim/abc/")
        content = response.content.decode()
        self.assertIn("next=", content)

class SocialUserAccessTests(TestCase):
    def test_social_created_player_cannot_access_organizer_dashboard(self):
        user = User.objects.create_user(email="social@test.com", password="testpass123", role="player")
        self.client.login(email="social@test.com", password="testpass123")
        response = self.client.get(reverse("dashboard:run_list"))
        self.assertIn(response.status_code, [302, 403])


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
        self.assertIn("next=", content)

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
        self.assertContains(response, "Log In")

    def test_landing_mentions_invite(self):
        response = self.client.get(reverse("landing"))
        self.assertContains(response, "invite")


class LoginPageInviteOnlyTests(TestCase):
    def test_login_page_has_no_signup_link(self):
        response = self.client.get(reverse("accounts:login"))
        content = response.content.decode()
        self.assertNotIn("Sign up", content)
        self.assertNotIn("Don't have an account?", content)


class SignupRemovedTests(TestCase):
    def test_signup_url_returns_404(self):
        response = self.client.get("/accounts/signup/")
        self.assertEqual(response.status_code, 404)


class AllauthSignupBlockedTests(TestCase):
    def test_allauth_signup_blocked(self):
        adapter = LFRAccountAdapter()
        self.assertFalse(adapter.is_open_for_signup(None))

    def test_allauth_signup_url_rejected(self):
        response = self.client.get("/accounts/social/account/signup/")
        # allauth should redirect away or show closed message, not a signup form
        self.assertNotEqual(response.status_code, 200)


# ── Security Tests (pytest-style) ──

import pytest
from conftest import CastingFactory, InviteFactory, RunFactory, UserFactory


class TestOpenRedirectPrevention:
    """Login view must not redirect to external URLs."""

    @pytest.fixture
    def login_user(self, db):
        return UserFactory(email="redirect@test.com")

    def _login(self, client, next_url):
        return client.post(
            f"/accounts/login/?next={next_url}",
            {"username": "redirect@test.com", "password": "testpass123"},
        )

    def test_safe_next_url_works(self, client, login_user):
        resp = self._login(client, "/runs/")
        assert resp.status_code == 302
        assert resp.url == "/runs/"

    def test_external_https_url_blocked(self, client, login_user):
        resp = self._login(client, "https://evil.com")
        assert resp.status_code == 302
        assert "evil.com" not in resp.url
        assert resp.url == "/runs/"

    def test_protocol_relative_url_blocked(self, client, login_user):
        resp = self._login(client, "//evil.com")
        assert resp.status_code == 302
        assert "evil.com" not in resp.url
        assert resp.url == "/runs/"


class TestPasswordValidation:
    """JoinView signup rejects weak passwords."""

    @pytest.fixture
    def join_context(self, db):
        run = RunFactory(name="PW Run", slug="pw-run", is_active=True)
        casting = CastingFactory(run=run, character_name="Test Char")
        invite = InviteFactory(casting=casting)
        return run, invite

    def test_weak_password_rejected(self, client, join_context):
        run, invite = join_context
        resp = client.post(
            f"/{run.slug}/join/{invite.code}/",
            {
                "email": "weak@test.com",
                "password": "123",
                "password_confirm": "123",
            },
        )
        # Should re-render the form (200), not redirect (302)
        assert resp.status_code == 200
        assert not User.objects.filter(email="weak@test.com").exists()

    def test_valid_password_succeeds(self, client, join_context):
        run, invite = join_context
        resp = client.post(
            f"/{run.slug}/join/{invite.code}/",
            {
                "email": "strong@test.com",
                "password": "V3ryStr0ng!Pass",
                "password_confirm": "V3ryStr0ng!Pass",
            },
        )
        assert resp.status_code == 302
        assert User.objects.filter(email="strong@test.com").exists()
