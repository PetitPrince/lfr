import pytest
from django.test import Client


class TestLoginView:
    def test_login_page_accessible(self, db):
        resp = Client().get("/organize/login/")
        assert resp.status_code == 200
        assert "dashboard/login.html" in [t.name for t in resp.templates]

    def test_login_with_valid_credentials(self, organizer):
        client = Client()
        resp = client.post("/organize/login/", {"username": organizer.email, "password": "testpass123"})
        assert resp.status_code == 302
        assert resp.url == "/organize/"

    def test_login_with_invalid_credentials(self, db):
        client = Client()
        resp = client.post("/organize/login/", {"username": "bad@test.com", "password": "wrong"})
        assert resp.status_code == 200  # re-renders form


class TestLogoutView:
    def test_logout_redirects(self, organizer_client):
        resp = organizer_client.post("/organize/logout/")
        assert resp.status_code == 302
        assert resp.url == "/organize/login/"


class TestPermissions:
    def test_anonymous_redirected_to_login(self, db):
        resp = Client().get("/organize/")
        assert resp.status_code == 302
        assert "/organize/login/" in resp.url

    def test_player_gets_403(self, player_client):
        resp = player_client.get("/organize/")
        assert resp.status_code == 403

    def test_organizer_gets_200(self, organizer_client):
        resp = organizer_client.get("/organize/")
        assert resp.status_code == 200

    def test_admin_gets_200(self, admin_user):
        client = Client()
        client.login(username=admin_user.email, password="testpass123")
        resp = client.get("/organize/")
        assert resp.status_code == 200
