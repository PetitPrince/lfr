import pytest

from casting.models import Casting
from conftest import CastingFactory, CustomAttributeDefinitionFactory


class TestCastingListView:
    def test_list_page_loads(self, organizer_client, run):
        resp = organizer_client.get(f"/organize/{run.slug}/castings/")
        assert resp.status_code == 200

    def test_list_shows_castings(self, organizer_client, run):
        CastingFactory(run=run, character_name="Nadia Kowalski")
        resp = organizer_client.get(f"/organize/{run.slug}/castings/")
        assert "Nadia Kowalski" in resp.content.decode()

    def test_list_empty_state(self, organizer_client, run):
        resp = organizer_client.get(f"/organize/{run.slug}/castings/")
        assert "No castings yet" in resp.content.decode()


class TestCastingCreateView:
    def test_create_page_loads(self, organizer_client, run):
        resp = organizer_client.get(f"/organize/{run.slug}/castings/create/")
        assert resp.status_code == 200

    def test_create_student(self, organizer_client, run):
        house = run.houses.first()
        year = run.years.first()
        resp = organizer_client.post(f"/organize/{run.slug}/castings/create/", {
            "role": "student",
            "character_name": "Alice",
            "house": house.pk,
            "year": year.pk,
        })
        assert resp.status_code == 302
        assert Casting.objects.filter(run=run, character_name="Alice").exists()

    def test_create_professor(self, organizer_client, run):
        subject = run.teaching_subjects.first()
        resp = organizer_client.post(f"/organize/{run.slug}/castings/create/", {
            "role": "professor",
            "character_name": "Dr. Blackwood",
            "teaching_subject": subject.pk,
        })
        assert resp.status_code == 302
        casting = Casting.objects.get(run=run, character_name="Dr. Blackwood")
        assert casting.role == "professor"
        assert casting.teaching_subject == subject

    def test_create_staff(self, organizer_client, run):
        resp = organizer_client.post(f"/organize/{run.slug}/castings/create/", {
            "role": "staff",
            "character_name": "Agnes",
            "staff_title": "Librarian",
        })
        assert resp.status_code == 302
        casting = Casting.objects.get(run=run, character_name="Agnes")
        assert casting.staff_title == "Librarian"

    def test_create_with_custom_attrs(self, organizer_client, run):
        attr = CustomAttributeDefinitionFactory(
            run=run, name="Prefect", attr_type="boolean", applies_to="student"
        )
        resp = organizer_client.post(f"/organize/{run.slug}/castings/create/", {
            "role": "student",
            "character_name": "Bob",
            f"custom_{attr.pk}": "on",
        })
        assert resp.status_code == 302
        casting = Casting.objects.get(run=run, character_name="Bob")
        assert casting.custom_attributes["Prefect"] is True


class TestCastingEditView:
    def test_edit_page_loads(self, organizer_client, run):
        casting = CastingFactory(run=run)
        resp = organizer_client.get(f"/organize/{run.slug}/castings/{casting.pk}/edit/")
        assert resp.status_code == 200

    def test_edit_updates_casting(self, organizer_client, run):
        casting = CastingFactory(run=run, character_name="Old Name", role="student")
        resp = organizer_client.post(f"/organize/{run.slug}/castings/{casting.pk}/edit/", {
            "role": "student",
            "character_name": "New Name",
        })
        assert resp.status_code == 302
        casting.refresh_from_db()
        assert casting.character_name == "New Name"

    def test_edit_nonexistent_404(self, organizer_client, run):
        resp = organizer_client.get(f"/organize/{run.slug}/castings/99999/edit/")
        assert resp.status_code == 404


class TestCastingDeleteView:
    def test_delete_confirm_page(self, organizer_client, run):
        casting = CastingFactory(run=run)
        resp = organizer_client.get(f"/organize/{run.slug}/castings/{casting.pk}/delete/")
        assert resp.status_code == 200
        assert "Confirm Delete" in resp.content.decode()

    def test_delete_removes_casting(self, organizer_client, run):
        casting = CastingFactory(run=run)
        resp = organizer_client.post(f"/organize/{run.slug}/castings/{casting.pk}/delete/")
        assert resp.status_code == 204
        assert not Casting.objects.filter(pk=casting.pk).exists()

    def test_delete_returns_hx_redirect(self, organizer_client, run):
        casting = CastingFactory(run=run)
        resp = organizer_client.post(f"/organize/{run.slug}/castings/{casting.pk}/delete/")
        assert resp["HX-Redirect"] == f"/organize/{run.slug}/castings/"


class TestCastingRoleFieldsView:
    def test_student_fields(self, organizer_client, run):
        resp = organizer_client.get(f"/organize/{run.slug}/castings/role-fields/?role=student")
        assert resp.status_code == 200
        content = resp.content.decode()
        assert "house" in content.lower()
        assert "teaching_subject" not in content

    def test_professor_fields(self, organizer_client, run):
        resp = organizer_client.get(f"/organize/{run.slug}/castings/role-fields/?role=professor")
        assert resp.status_code == 200
        content = resp.content.decode()
        assert "teaching_subject" in content
        assert "id_house" not in content

    def test_staff_fields(self, organizer_client, run):
        resp = organizer_client.get(f"/organize/{run.slug}/castings/role-fields/?role=staff")
        assert resp.status_code == 200
        content = resp.content.decode()
        assert "staff_title" in content
        assert "id_house" not in content

    def test_custom_attrs_filtered_by_role(self, organizer_client, run):
        student_attr = CustomAttributeDefinitionFactory(
            run=run, name="Prefect", attr_type="boolean", applies_to="student"
        )
        prof_attr = CustomAttributeDefinitionFactory(
            run=run, name="Tenure", attr_type="boolean", applies_to="professor"
        )
        resp = organizer_client.get(f"/organize/{run.slug}/castings/role-fields/?role=student")
        content = resp.content.decode()
        assert "Prefect" in content
        assert "Tenure" not in content
