import pytest

from casting.models import Invite
from conftest import CastingFactory, InviteFactory


class TestInviteListView:
    def test_list_page_loads(self, organizer_client, run):
        resp = organizer_client.get(f"/organize/{run.slug}/invites/")
        assert resp.status_code == 200

    def test_list_shows_invites(self, organizer_client, run):
        casting = CastingFactory(run=run, character_name="Nadia")
        invite = InviteFactory(casting=casting)
        resp = organizer_client.get(f"/organize/{run.slug}/invites/")
        assert str(invite.code) in resp.content.decode()

    def test_list_empty_state(self, organizer_client, run):
        resp = organizer_client.get(f"/organize/{run.slug}/invites/")
        assert "No invite codes" in resp.content.decode()

    def test_invite_list_shows_full_join_url(self, organizer_client, run):
        casting = CastingFactory(run=run, character_name="Nadia")
        invite = InviteFactory(casting=casting)
        resp = organizer_client.get(f"/organize/{run.slug}/invites/")
        expected_path = f"/{run.slug}/join/{invite.code}/"
        assert expected_path in resp.content.decode()


class TestInviteGenerateView:
    def test_generates_codes_for_unclaimed_castings(self, organizer_client, run):
        CastingFactory(run=run)
        CastingFactory(run=run)
        resp = organizer_client.post(f"/organize/{run.slug}/invites/generate/")
        assert resp.status_code == 200
        assert Invite.objects.filter(casting__run=run).count() == 2

    def test_skips_castings_that_already_have_invites(self, organizer_client, run):
        casting1 = CastingFactory(run=run)
        casting2 = CastingFactory(run=run)
        InviteFactory(casting=casting1)

        organizer_client.post(f"/organize/{run.slug}/invites/generate/")
        assert Invite.objects.filter(casting__run=run).count() == 2

    def test_no_castings_shows_message(self, organizer_client, run):
        resp = organizer_client.post(f"/organize/{run.slug}/invites/generate/")
        assert resp.status_code == 200
        # No new invites partial content

    def test_all_castings_already_have_invites(self, organizer_client, run):
        casting = CastingFactory(run=run)
        InviteFactory(casting=casting)
        resp = organizer_client.post(f"/organize/{run.slug}/invites/generate/")
        assert resp.status_code == 200
        assert Invite.objects.filter(casting__run=run).count() == 1  # no new ones
