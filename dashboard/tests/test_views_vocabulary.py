import pytest

from conftest import CustomAttributeDefinitionFactory, HouseFactory
from runs.models import CustomAttributeDefinition, House


class TestVocabularyEditView:
    def test_get_returns_checkbox_list(self, organizer_client, run):
        resp = organizer_client.get(f"/organize/{run.slug}/vocabulary/houses/")
        assert resp.status_code == 200
        content = resp.content.decode()
        assert "Libussa" in content
        assert "Faust" in content

    def test_post_updates_m2m(self, organizer_client, run):
        libussa = run.houses.get(name="Libussa")
        # Only keep Libussa, remove Faust
        resp = organizer_client.post(
            f"/organize/{run.slug}/vocabulary/houses/",
            {"items": [libussa.pk]},
        )
        assert resp.status_code == 200
        assert set(run.houses.values_list("name", flat=True)) == {"Libussa"}

    def test_post_empty_clears_m2m(self, organizer_client, run):
        organizer_client.post(f"/organize/{run.slug}/vocabulary/houses/", {})
        assert run.houses.count() == 0

    def test_invalid_vocab_type_returns_400(self, organizer_client, run):
        resp = organizer_client.get(f"/organize/{run.slug}/vocabulary/invalid/")
        assert resp.status_code == 400


class TestVocabularyAddView:
    def test_add_new_item(self, organizer_client, run):
        resp = organizer_client.post(
            f"/organize/{run.slug}/vocabulary/houses/add/",
            {"name": "Molin"},
        )
        assert resp.status_code == 200
        assert House.objects.filter(name="Molin").exists()
        assert run.houses.filter(name="Molin").exists()

    def test_add_existing_item_links_it(self, organizer_client, run):
        HouseFactory(name="Durentius")
        assert not run.houses.filter(name="Durentius").exists()
        organizer_client.post(
            f"/organize/{run.slug}/vocabulary/houses/add/",
            {"name": "Durentius"},
        )
        assert run.houses.filter(name="Durentius").exists()

    def test_add_blank_name_ignored(self, organizer_client, run):
        count_before = run.houses.count()
        organizer_client.post(f"/organize/{run.slug}/vocabulary/houses/add/", {"name": ""})
        assert run.houses.count() == count_before


class TestCustomAttributeViews:
    def test_list_loads(self, organizer_client, run):
        CustomAttributeDefinitionFactory(run=run, name="Prefect")
        resp = organizer_client.get(f"/organize/{run.slug}/custom-attributes/")
        assert resp.status_code == 200
        assert "Prefect" in resp.content.decode()

    def test_create_custom_attr(self, organizer_client, run):
        resp = organizer_client.post(f"/organize/{run.slug}/custom-attributes/", {
            "name": "House Rep",
            "attr_type": "boolean",
            "applies_to": "student",
            "is_filterable": True,
            "sort_order": 0,
            "choices": "[]",
        })
        assert resp.status_code == 200
        assert run.custom_attributes.filter(name="House Rep").exists()

    def test_delete_custom_attr(self, organizer_client, run):
        attr = CustomAttributeDefinitionFactory(run=run, name="ToDelete")
        resp = organizer_client.post(
            f"/organize/{run.slug}/custom-attributes/{attr.pk}/delete/"
        )
        assert resp.status_code == 200
        assert not CustomAttributeDefinition.objects.filter(pk=attr.pk).exists()

    def test_delete_other_runs_attr_404(self, organizer_client, run):
        from conftest import RunFactory

        other_run = RunFactory(slug="other-run")
        attr = CustomAttributeDefinitionFactory(run=other_run, name="Foreign")
        resp = organizer_client.post(
            f"/organize/{run.slug}/custom-attributes/{attr.pk}/delete/"
        )
        assert resp.status_code == 404
