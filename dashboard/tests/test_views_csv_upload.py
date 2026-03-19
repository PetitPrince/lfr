import pytest

from casting.models import Casting
from conftest import CastingFactory


class TestCSVUploadView:
    def test_upload_page_loads(self, organizer_client, run):
        resp = organizer_client.get(f"/organize/{run.slug}/castings/upload/")
        assert resp.status_code == 200


class TestCSVUploadPreviewView:
    def test_preview_valid_csv(self, organizer_client, run):
        csv_text = "role,character_name,house\nstudent,Alice,Libussa"
        resp = organizer_client.post(
            f"/organize/{run.slug}/castings/upload/preview/",
            {"csv_text": csv_text},
        )
        assert resp.status_code == 200
        content = resp.content.decode()
        assert "Alice" in content
        assert "Valid" in content

    def test_preview_invalid_csv(self, organizer_client, run):
        csv_text = "role,character_name,house\nstudent,Alice,FakeHouse"
        resp = organizer_client.post(
            f"/organize/{run.slug}/castings/upload/preview/",
            {"csv_text": csv_text},
        )
        assert resp.status_code == 200
        assert "Unknown house" in resp.content.decode()

    def test_preview_empty_input(self, organizer_client, run):
        resp = organizer_client.post(
            f"/organize/{run.slug}/castings/upload/preview/",
            {"csv_text": ""},
        )
        assert resp.status_code == 200
        assert "provide" in resp.content.decode().lower()

    def test_preview_stores_data_in_session(self, organizer_client, run):
        csv_text = "role,character_name\nstudent,Alice"
        organizer_client.post(
            f"/organize/{run.slug}/castings/upload/preview/",
            {"csv_text": csv_text},
        )
        session = organizer_client.session
        assert "csv_parsed_rows" in session
        assert len(session["csv_parsed_rows"]) == 1


class TestCSVUploadConfirmView:
    def test_confirm_creates_castings(self, organizer_client, run):
        # First preview to store data in session
        csv_text = "role,character_name,house\nstudent,Alice,Libussa\nstudent,Bob,Faust"
        organizer_client.post(
            f"/organize/{run.slug}/castings/upload/preview/",
            {"csv_text": csv_text},
        )
        resp = organizer_client.post(f"/organize/{run.slug}/castings/upload/confirm/")
        assert resp.status_code == 302
        assert Casting.objects.filter(run=run).count() == 2
        assert Casting.objects.filter(run=run, character_name="Alice", house__name="Libussa").exists()

    def test_confirm_skips_invalid_rows(self, organizer_client, run):
        csv_text = "role,character_name,house\nstudent,Alice,Libussa\nstudent,Bob,FakeHouse"
        organizer_client.post(
            f"/organize/{run.slug}/castings/upload/preview/",
            {"csv_text": csv_text},
        )
        organizer_client.post(f"/organize/{run.slug}/castings/upload/confirm/")
        assert Casting.objects.filter(run=run).count() == 1
        assert Casting.objects.filter(run=run, character_name="Alice").exists()

    def test_confirm_without_session_data_redirects(self, organizer_client, run):
        resp = organizer_client.post(f"/organize/{run.slug}/castings/upload/confirm/")
        assert resp.status_code == 302
        assert "upload" in resp.url

    def test_confirm_clears_session_data(self, organizer_client, run):
        csv_text = "role,character_name\nstudent,Alice"
        organizer_client.post(
            f"/organize/{run.slug}/castings/upload/preview/",
            {"csv_text": csv_text},
        )
        organizer_client.post(f"/organize/{run.slug}/castings/upload/confirm/")
        assert "csv_parsed_rows" not in organizer_client.session
