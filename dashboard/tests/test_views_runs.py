import pytest

from runs.models import CustomAttributeDefinition, Run


class TestRunListView:
    def test_shows_runs(self, organizer_client, run):
        resp = organizer_client.get("/organize/")
        assert resp.status_code == 200
        assert run.name in resp.content.decode()

    def test_excludes_template_runs(self, organizer_client, run, template_run):
        resp = organizer_client.get("/organize/")
        content = resp.content.decode()
        assert run.name in content
        assert template_run.name not in content

    def test_empty_state(self, organizer_client):
        resp = organizer_client.get("/organize/")
        assert resp.status_code == 200
        assert "No runs yet" in resp.content.decode()


class TestRunCreateView:
    def test_create_page_loads(self, organizer_client):
        resp = organizer_client.get("/organize/create/")
        assert resp.status_code == 200

    def test_create_run_generates_slug(self, organizer_client):
        resp = organizer_client.post("/organize/create/", {
            "name": "College of Wizardry 27: Wintertide",
            "start_date": "2026-06-01",
            "end_date": "2026-06-05",
        })
        assert resp.status_code == 302
        r = Run.objects.get(slug="college-of-wizardry-27-wintertide")
        assert r.name == "College of Wizardry 27: Wintertide"

    def test_create_run_duplicate_name_increments_slug(self, organizer_client):
        organizer_client.post("/organize/create/", {"name": "Test Run X"})
        organizer_client.post("/organize/create/", {"name": "Test Run X"})
        assert Run.objects.filter(slug="test-run-x").exists()
        assert Run.objects.filter(slug="test-run-x-2").exists()

    def test_create_run_from_template_copies_vocabulary(self, organizer_client, template_run):
        resp = organizer_client.post("/organize/create/", {
            "name": "CoW 28",
            "template": template_run.pk,
        })
        assert resp.status_code == 302
        new_run = Run.objects.get(slug="cow-28")
        assert set(new_run.houses.values_list("name", flat=True)) == set(
            template_run.houses.values_list("name", flat=True)
        )
        assert set(new_run.years.values_list("name", flat=True)) == set(
            template_run.years.values_list("name", flat=True)
        )

    def test_create_run_from_template_copies_custom_attrs(self, organizer_client, template_run):
        CustomAttributeDefinition.objects.create(
            run=template_run, name="Prefect", attr_type="boolean", applies_to="student"
        )
        organizer_client.post("/organize/create/", {
            "name": "CoW 29",
            "template": template_run.pk,
        })
        new_run = Run.objects.get(slug="cow-29")
        assert new_run.custom_attributes.filter(name="Prefect").exists()

    def test_create_run_without_template(self, organizer_client):
        resp = organizer_client.post("/organize/create/", {"name": "Blank Run"})
        assert resp.status_code == 302
        r = Run.objects.get(slug="blank-run")
        assert r.houses.count() == 0

    def test_shows_template_cards(self, organizer_client, template_run):
        resp = organizer_client.get("/organize/create/")
        assert f"New {template_run.name} run" in resp.content.decode()

    def test_player_cannot_create(self, player_client):
        resp = player_client.get("/organize/create/")
        assert resp.status_code == 302  # redirect to login (user_passes_test)


class TestRunDetailView:
    def test_detail_page_loads(self, organizer_client, run):
        resp = organizer_client.get(f"/organize/{run.slug}/")
        assert resp.status_code == 200
        assert run.name in resp.content.decode()

    def test_detail_shows_vocabulary_chips(self, organizer_client, run):
        resp = organizer_client.get(f"/organize/{run.slug}/")
        content = resp.content.decode()
        assert "Libussa" in content
        assert "Faust" in content

    def test_detail_shows_stats(self, organizer_client, run):
        from conftest import CastingFactory

        CastingFactory(run=run)
        CastingFactory(run=run)
        resp = organizer_client.get(f"/organize/{run.slug}/")
        assert resp.context["casting_count"] == 2

    def test_nonexistent_slug_404(self, organizer_client):
        resp = organizer_client.get("/organize/nonexistent/")
        assert resp.status_code == 404

    def test_template_run_slug_404(self, organizer_client, template_run):
        resp = organizer_client.get(f"/organize/{template_run.slug}/")
        assert resp.status_code == 404


class TestRunSettingsView:
    def test_settings_page_loads(self, organizer_client, run):
        resp = organizer_client.get(f"/organize/{run.slug}/settings/")
        assert resp.status_code == 200

    def test_update_settings(self, organizer_client, run):
        resp = organizer_client.post(f"/organize/{run.slug}/settings/", {
            "name": "Updated Name",
            "is_active": True,
        })
        assert resp.status_code == 302
        run.refresh_from_db()
        assert run.name == "Updated Name"
