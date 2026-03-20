import pytest
from collections import Counter

from conftest import (
    CastingFactory,
    ClubFactory,
    HouseFactory,
    PathFactory,
    PostFactory,
    PostKeywordFactory,
    RunFactory,
    UserFactory,
    YearFactory,
)
from posts.hallway import get_biased_hallway_posts


@pytest.fixture
def hallway_run(db):
    """A run with vocabulary for hallway bias tests."""
    r = RunFactory(name="Hallway Run", slug="hallway-run")
    return r


@pytest.fixture
def viewer_casting(hallway_run):
    """The logged-in player's casting with path, house, year."""
    house = HouseFactory(name="Libussa")
    path = PathFactory(name="Herbology")
    year = YearFactory(name="3rd Year")
    hallway_run.houses.add(house)
    hallway_run.paths.add(path)
    hallway_run.years.add(year)
    casting = CastingFactory(
        run=hallway_run, role="student",
        house=house, path=path, year=year,
    )
    return casting


class TestGetBiasedHallwayPosts:
    def test_returns_empty_when_no_posts(self, hallway_run, viewer_casting):
        result = get_biased_hallway_posts(hallway_run, viewer_casting, count=3)
        assert result == []

    def test_returns_up_to_count_posts(self, hallway_run, viewer_casting):
        for _ in range(5):
            c = CastingFactory(run=hallway_run, role="student")
            PostFactory(run=hallway_run, casting=c)
        result = get_biased_hallway_posts(hallway_run, viewer_casting, count=3)
        assert len(result) == 3

    def test_excludes_viewers_own_post(self, hallway_run, viewer_casting):
        PostFactory(run=hallway_run, casting=viewer_casting)
        other = CastingFactory(run=hallway_run, role="student")
        other_post = PostFactory(run=hallway_run, casting=other)
        result = get_biased_hallway_posts(hallway_run, viewer_casting, count=3)
        assert len(result) == 1
        assert result[0].pk == other_post.pk

    def test_excludes_non_student_posts(self, hallway_run, viewer_casting):
        prof = CastingFactory(run=hallway_run, role="professor")
        PostFactory(run=hallway_run, casting=prof)
        result = get_biased_hallway_posts(hallway_run, viewer_casting, count=3)
        assert result == []

    def test_excludes_unpublished_posts(self, hallway_run, viewer_casting):
        c = CastingFactory(run=hallway_run, role="student")
        PostFactory(run=hallway_run, casting=c, is_published=False)
        result = get_biased_hallway_posts(hallway_run, viewer_casting, count=3)
        assert result == []

    def test_path_bias_is_strongest(self, hallway_run, viewer_casting):
        """Over many samples, same-path posts should appear most often."""
        same_path = CastingFactory(
            run=hallway_run, role="student", path=viewer_casting.path,
        )
        same_path_post = PostFactory(run=hallway_run, casting=same_path)

        diff_house = HouseFactory(name="Faust")
        diff_path = PathFactory(name="Alchemy")
        diff_year = YearFactory(name="1st Year")
        other = CastingFactory(
            run=hallway_run, role="student",
            house=diff_house, path=diff_path, year=diff_year,
        )
        other_post = PostFactory(run=hallway_run, casting=other)

        counts = Counter()
        for _ in range(200):
            results = get_biased_hallway_posts(hallway_run, viewer_casting, count=1)
            for p in results:
                counts[p.pk] += 1

        assert counts[same_path_post.pk] > counts[other_post.pk]

    def test_house_bias_over_unrelated(self, hallway_run, viewer_casting):
        """Same-house should appear more than a totally unrelated post."""
        same_house = CastingFactory(
            run=hallway_run, role="student", house=viewer_casting.house,
        )
        same_house_post = PostFactory(run=hallway_run, casting=same_house)

        diff_house = HouseFactory(name="Faust")
        diff_path = PathFactory(name="Alchemy")
        diff_year = YearFactory(name="1st Year")
        unrelated = CastingFactory(
            run=hallway_run, role="student",
            house=diff_house, path=diff_path, year=diff_year,
        )
        unrelated_post = PostFactory(run=hallway_run, casting=unrelated)

        counts = Counter()
        for _ in range(200):
            results = get_biased_hallway_posts(hallway_run, viewer_casting, count=1)
            for p in results:
                counts[p.pk] += 1

        assert counts[same_house_post.pk] > counts[unrelated_post.pk]

    def test_keyword_overlap_adds_bias(self, hallway_run, viewer_casting):
        """Post sharing a keyword with viewer's post should be favored."""
        viewer_post = PostFactory(run=hallway_run, casting=viewer_casting)
        PostKeywordFactory(post=viewer_post, label="Bookworm")

        matching = CastingFactory(run=hallway_run, role="student")
        matching_post = PostFactory(run=hallway_run, casting=matching)
        PostKeywordFactory(post=matching_post, label="Bookworm")

        no_match = CastingFactory(run=hallway_run, role="student")
        no_match_post = PostFactory(run=hallway_run, casting=no_match)
        PostKeywordFactory(post=no_match_post, label="Athletic")

        counts = Counter()
        for _ in range(200):
            results = get_biased_hallway_posts(hallway_run, viewer_casting, count=1)
            for p in results:
                counts[p.pk] += 1

        # viewer's own post should never appear
        assert viewer_post.pk not in counts
        assert counts[matching_post.pk] > counts[no_match_post.pk]

    def test_no_duplicates_in_results(self, hallway_run, viewer_casting):
        for _ in range(5):
            c = CastingFactory(run=hallway_run, role="student")
            PostFactory(run=hallway_run, casting=c)
        for _ in range(50):
            results = get_biased_hallway_posts(hallway_run, viewer_casting, count=3)
            pks = [p.pk for p in results]
            assert len(pks) == len(set(pks))

    def test_all_unrelated_still_returned(self, hallway_run, viewer_casting):
        """Even with no affinity, posts still appear (base weight > 0)."""
        diff_house = HouseFactory(name="Faust")
        diff_path = PathFactory(name="Alchemy")
        diff_year = YearFactory(name="1st Year")
        c = CastingFactory(
            run=hallway_run, role="student",
            house=diff_house, path=diff_path, year=diff_year,
        )
        post = PostFactory(run=hallway_run, casting=c)
        result = get_biased_hallway_posts(hallway_run, viewer_casting, count=1)
        assert len(result) == 1
        assert result[0].pk == post.pk


@pytest.fixture
def club_run(db):
    r = RunFactory(name="Club Run", slug="club-run")
    r.clubs.set([ClubFactory(name="Duelling Club"), ClubFactory(name="Quidditch")])
    r.blood_statuses.set([])
    return r


@pytest.fixture
def club_player(club_run):
    user = UserFactory(email="clubplayer@test.com", role="player")
    casting = CastingFactory(run=club_run, user=user, role="student")
    return user, casting


@pytest.fixture
def club_player_client(club_player):
    from django.test import Client
    user, _ = club_player
    client = Client()
    client.login(username=user.email, password="testpass123")
    return client


class TestPlayerClubEditing:
    def test_create_post_with_clubs(self, club_run, club_player, club_player_client):
        user, casting = club_player
        clubs = list(club_run.clubs.all())
        resp = club_player_client.post(
            f"/post/{club_run.slug}/create/",
            {
                "post_type": "character",
                "character_name": "Test Char",
                "content": "Hello world",
                "keywords": "",
                "clubs": [clubs[0].pk, clubs[1].pk],
            },
        )
        assert resp.status_code == 302
        casting.refresh_from_db()
        assert set(casting.clubs.values_list("pk", flat=True)) == {clubs[0].pk, clubs[1].pk}

    def test_create_post_with_no_clubs(self, club_run, club_player, club_player_client):
        user, casting = club_player
        resp = club_player_client.post(
            f"/post/{club_run.slug}/create/",
            {
                "post_type": "character",
                "character_name": "Test Char",
                "content": "Hello world",
                "keywords": "",
            },
        )
        assert resp.status_code == 302
        casting.refresh_from_db()
        assert casting.clubs.count() == 0

    def test_edit_post_updates_clubs(self, club_run, club_player, club_player_client):
        user, casting = club_player
        clubs = list(club_run.clubs.all())
        casting.clubs.set([clubs[0]])
        post = PostFactory(run=club_run, casting=casting, author=user)

        resp = club_player_client.post(
            f"/post/{club_run.slug}/post/{post.pk}/edit/",
            {
                "post_type": "character",
                "character_name": "Test Char",
                "content": "Updated",
                "keywords": "",
                "clubs": [clubs[1].pk],
            },
        )
        assert resp.status_code == 302
        casting.refresh_from_db()
        assert set(casting.clubs.values_list("pk", flat=True)) == {clubs[1].pk}

    def test_edit_post_clears_clubs(self, club_run, club_player, club_player_client):
        user, casting = club_player
        clubs = list(club_run.clubs.all())
        casting.clubs.set(clubs)
        post = PostFactory(run=club_run, casting=casting, author=user)

        resp = club_player_client.post(
            f"/post/{club_run.slug}/post/{post.pk}/edit/",
            {
                "post_type": "character",
                "character_name": "Test Char",
                "content": "Updated",
                "keywords": "",
                # no clubs field = clear all
            },
        )
        assert resp.status_code == 302
        casting.refresh_from_db()
        assert casting.clubs.count() == 0

    def test_clubs_only_from_run_vocabulary(self, club_run, club_player, club_player_client):
        """Players can only pick clubs that belong to the run."""
        user, casting = club_player
        rogue_club = ClubFactory(name="Rogue Club")  # not in club_run

        resp = club_player_client.post(
            f"/post/{club_run.slug}/create/",
            {
                "post_type": "character",
                "character_name": "Test Char",
                "content": "Hello",
                "keywords": "",
                "clubs": [rogue_club.pk],
            },
        )
        # Form should reject the invalid choice — re-renders with errors (200)
        assert resp.status_code == 200
        casting.refresh_from_db()
        assert casting.clubs.count() == 0

    def test_edit_form_preselects_existing_clubs(self, club_run, club_player, club_player_client):
        user, casting = club_player
        clubs = list(club_run.clubs.all())
        casting.clubs.set([clubs[0]])
        post = PostFactory(run=club_run, casting=casting, author=user)

        resp = club_player_client.get(f"/post/{club_run.slug}/post/{post.pk}/edit/")
        assert resp.status_code == 200
        content = resp.content.decode()
        # The selected club should have 'selected' attribute
        assert f'value="{clubs[0].pk}" selected' in content or f"value=\"{clubs[0].pk}\" selected" in content
