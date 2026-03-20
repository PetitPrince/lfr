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

    def test_signup_page_has_social_buttons(self):
        response = self.client.get(reverse("accounts:signup"))
        content = response.content.decode()
        self.assertIn("Google", content)
        self.assertIn("Discord", content)
        self.assertIn("Facebook", content)

    def test_landing_page_has_social_buttons(self):
        response = self.client.get(reverse("landing"))
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

    def test_signup_social_buttons_preserve_next(self):
        response = self.client.get(reverse("accounts:signup") + "?next=/accounts/claim/abc/")
        content = response.content.decode()
        self.assertIn("next=", content)


class SocialUserAccessTests(TestCase):
    def test_social_created_player_cannot_access_organizer_dashboard(self):
        user = User.objects.create_user(email="social@test.com", password="testpass123", role="player")
        self.client.login(email="social@test.com", password="testpass123")
        response = self.client.get(reverse("dashboard:run_list"))
        self.assertIn(response.status_code, [302, 403])


class AllauthSignupBlockedTests(TestCase):
    def test_allauth_signup_blocked(self):
        adapter = LFRAccountAdapter()
        self.assertFalse(adapter.is_open_for_signup(None))

    def test_allauth_signup_url_rejected(self):
        response = self.client.get("/accounts/social/account/signup/")
        # allauth should redirect away or show closed message, not a signup form
        self.assertNotEqual(response.status_code, 200)
