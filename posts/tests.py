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


# ── Player View Tests ──

from posts.models import Comment, Photo, Post


@pytest.fixture
def casting(run, player):
    """A casting linking the player to the run."""
    return CastingFactory(run=run, user=player, role="student", character_name="Nadia Kowalski")


@pytest.fixture
def other_user(db):
    return UserFactory(email="other@test.com", role="player")


@pytest.fixture
def other_casting(run, other_user):
    return CastingFactory(run=run, user=other_user, role="student", character_name="Other Char")


class TestPlayerViewAuthorization:
    """Unauthenticated users get redirected; users without casting get 403."""

    PROTECTED_VIEWS = [
        "/post/{slug}/",
        "/post/{slug}/create/",
        "/post/{slug}/discover/faculty/",
        "/post/{slug}/discover/students/",
        "/post/{slug}/discover/other/",
    ]

    def test_unauthenticated_redirected_to_login(self, run, db, client):
        for pattern in self.PROTECTED_VIEWS:
            url = pattern.format(slug=run.slug)
            resp = client.get(url)
            assert resp.status_code == 302, f"Expected redirect for {url}, got {resp.status_code}"
            assert "/accounts/login/" in resp.url

    def test_unauthenticated_redirected_for_post_detail(self, run, casting, player_client, client):
        post = PostFactory(run=run, casting=casting, author=casting.user)
        resp = client.get(f"/post/{run.slug}/post/{post.pk}/")
        assert resp.status_code == 302
        assert "/accounts/login/" in resp.url

    def test_authenticated_without_casting_gets_403(self, run, db):
        from django.test import Client as DjangoClient
        user = UserFactory(email="nocasting@test.com")
        c = DjangoClient()
        c.login(username=user.email, password="testpass123")
        for pattern in self.PROTECTED_VIEWS:
            url = pattern.format(slug=run.slug)
            resp = c.get(url)
            assert resp.status_code == 403, f"Expected 403 for {url}, got {resp.status_code}"

    def test_player_with_casting_can_access_message_board(self, run, casting, player_client):
        resp = player_client.get(f"/post/{run.slug}/")
        assert resp.status_code == 200

    def test_player_with_casting_can_access_discover_faculty(self, run, casting, player_client):
        resp = player_client.get(f"/post/{run.slug}/discover/faculty/")
        assert resp.status_code == 200

    def test_player_with_casting_can_access_discover_students(self, run, casting, player_client):
        resp = player_client.get(f"/post/{run.slug}/discover/students/")
        assert resp.status_code == 200

    def test_player_with_casting_can_access_discover_other(self, run, casting, player_client):
        resp = player_client.get(f"/post/{run.slug}/discover/other/")
        assert resp.status_code == 200


class TestPostCRUD:
    """Create, edit, and delete posts."""

    def test_create_character_post(self, run, casting, player_client):
        resp = player_client.post(
            f"/post/{run.slug}/create/",
            {
                "post_type": "character",
                "character_name": "Nadia K",
                "content": "A brilliant student.",
                "keywords": "Nerdy,Bookworm",
            },
        )
        assert resp.status_code == 302
        assert Post.objects.filter(run=run, author=casting.user, post_type="character").exists()

    def test_create_other_post(self, run, casting, player_client):
        resp = player_client.post(
            f"/post/{run.slug}/create/",
            {
                "post_type": "other",
                "title": "Duelling Tournament",
                "category": "extracurricular",
                "content": "Sign up now!",
            },
        )
        assert resp.status_code == 302
        assert Post.objects.filter(run=run, post_type="other", title="Duelling Tournament").exists()

    def test_edit_own_post(self, run, casting, player, player_client):
        post = PostFactory(run=run, casting=casting, author=player, content="Original")
        resp = player_client.post(
            f"/post/{run.slug}/post/{post.pk}/edit/",
            {
                "post_type": "character",
                "character_name": "Nadia Updated",
                "content": "Updated content",
                "keywords": "",
            },
        )
        assert resp.status_code == 302
        post.refresh_from_db()
        assert post.content == "Updated content"

    def test_cannot_edit_another_users_post(self, run, casting, player_client, other_casting):
        post = PostFactory(run=run, casting=other_casting, author=other_casting.user)
        resp = player_client.get(f"/post/{run.slug}/post/{post.pk}/edit/")
        assert resp.status_code == 404

    def test_delete_own_post(self, run, casting, player, player_client):
        post = PostFactory(run=run, casting=casting, author=player)
        resp = player_client.post(f"/post/{run.slug}/post/{post.pk}/delete/")
        assert resp.status_code == 302
        assert not Post.objects.filter(pk=post.pk).exists()

    def test_cannot_delete_another_users_post(self, run, casting, player_client, other_casting):
        post = PostFactory(run=run, casting=other_casting, author=other_casting.user)
        resp = player_client.post(f"/post/{run.slug}/post/{post.pk}/delete/")
        assert resp.status_code == 404
        assert Post.objects.filter(pk=post.pk).exists()


class TestComments:
    """Comment creation and threading."""

    def test_create_comment(self, run, casting, player, player_client):
        post = PostFactory(run=run, casting=casting, author=player)
        resp = player_client.post(
            f"/post/{run.slug}/post/{post.pk}/comment/",
            {"body": "Great character!"},
        )
        assert resp.status_code == 200  # returns partial HTML
        assert Comment.objects.filter(post=post, author=player, body="Great character!").exists()

    def test_reply_to_comment(self, run, casting, player, player_client):
        post = PostFactory(run=run, casting=casting, author=player)
        parent = Comment.objects.create(post=post, author=player, body="Parent comment")
        resp = player_client.post(
            f"/post/{run.slug}/post/{post.pk}/comment/{parent.pk}/reply/",
            {"body": "Reply to parent"},
        )
        assert resp.status_code == 200
        reply = Comment.objects.get(body="Reply to parent")
        assert reply.parent_id == parent.pk

    def test_unauthenticated_cannot_comment(self, run, casting, player, client):
        post = PostFactory(run=run, casting=casting, author=player)
        resp = client.post(
            f"/post/{run.slug}/post/{post.pk}/comment/",
            {"body": "Sneaky comment"},
        )
        assert resp.status_code == 302
        assert "/accounts/login/" in resp.url


class TestDiscoverViews:
    """Discover section filtering."""

    def test_faculty_view_returns_faculty_posts(self, run, casting, player_client):
        prof_casting = CastingFactory(run=run, role="professor", character_name="Prof Snape")
        prof_post = PostFactory(run=run, casting=prof_casting, author=prof_casting.user)
        student_post = PostFactory(run=run, casting=casting, author=casting.user)

        resp = player_client.get(f"/post/{run.slug}/discover/faculty/")
        assert resp.status_code == 200
        post_pks = [p.pk for p in resp.context["posts"]]
        assert prof_post.pk in post_pks
        assert student_post.pk not in post_pks

    def test_student_filter_by_house(self, run, casting, player_client):
        house = run.houses.first()
        student_in_house = CastingFactory(run=run, role="student", house=house, character_name="Housed Student")
        post_in_house = PostFactory(run=run, casting=student_in_house, author=student_in_house.user)

        other_house = run.houses.last()
        student_other = CastingFactory(run=run, role="student", house=other_house, character_name="Other Student")
        post_other = PostFactory(run=run, casting=student_other, author=student_other.user)

        resp = player_client.get(f"/post/{run.slug}/discover/students/filter/?house={house.pk}")
        assert resp.status_code == 200
        content = resp.content.decode()
        assert student_in_house.character_name in content

    def test_student_filter_by_keyword(self, run, casting, player_client):
        student = CastingFactory(run=run, role="student", character_name="Keyword Student")
        post = PostFactory(run=run, casting=student, author=student.user)
        PostKeywordFactory(post=post, label="Nerdy")

        other_student = CastingFactory(run=run, role="student", character_name="No Keyword")
        other_post = PostFactory(run=run, casting=other_student, author=other_student.user)
        PostKeywordFactory(post=other_post, label="Athletic")

        resp = player_client.get(f"/post/{run.slug}/discover/students/filter/?keyword=Nerdy")
        assert resp.status_code == 200
        content = resp.content.decode()
        assert "Keyword Student" in content
        assert "No Keyword" not in content

    def test_other_posts_filterable_by_category(self, run, casting, player, player_client):
        extra_post = PostFactory(
            run=run, casting=casting, author=player,
            post_type="other", title="Extracurricular Event", category="extracurricular",
        )
        plot_post = PostFactory(
            run=run, casting=casting, author=player,
            post_type="other", title="School Plot", category="school_plot",
        )

        resp = player_client.get(f"/post/{run.slug}/discover/other/?category=extracurricular")
        assert resp.status_code == 200
        post_pks = [p.pk for p in resp.context["posts"]]
        assert extra_post.pk in post_pks
        assert plot_post.pk not in post_pks


class TestPhotoDeletion:
    """Photo deletion via edit, including IDOR prevention."""

    @pytest.fixture(autouse=True)
    def _use_tmp_media(self, tmp_path, settings):
        settings.MEDIA_ROOT = str(tmp_path)

    @pytest.fixture
    def post_with_photos(self, run, casting, player):
        from django.core.files.uploadedfile import SimpleUploadedFile
        post = PostFactory(run=run, casting=casting, author=player)
        img = SimpleUploadedFile("test.jpg", b"\xff\xd8\xff\xe0" + b"\x00" * 100, content_type="image/jpeg")
        photo1 = Photo.objects.create(post=post, image=img, sort_order=0)
        img2 = SimpleUploadedFile("test2.jpg", b"\xff\xd8\xff\xe0" + b"\x00" * 100, content_type="image/jpeg")
        photo2 = Photo.objects.create(post=post, image=img2, sort_order=1)
        return post, photo1, photo2

    def test_edit_with_delete_photos_removes_specified(self, run, casting, player_client, post_with_photos):
        post, photo1, photo2 = post_with_photos
        resp = player_client.post(
            f"/post/{run.slug}/post/{post.pk}/edit/",
            {
                "post_type": "character",
                "character_name": "Nadia",
                "content": "Updated",
                "keywords": "",
                "delete_photos": [str(photo1.pk)],
            },
        )
        assert resp.status_code == 302
        assert not Photo.objects.filter(pk=photo1.pk).exists()
        assert Photo.objects.filter(pk=photo2.pk).exists()

    def test_delete_photos_from_other_post_ignored(self, run, casting, player, player_client, post_with_photos, other_casting):
        """IDOR prevention: photo IDs from another post should not be deleted."""
        post, photo1, photo2 = post_with_photos
        from django.core.files.uploadedfile import SimpleUploadedFile

        other_post = PostFactory(run=run, casting=other_casting, author=other_casting.user)
        img = SimpleUploadedFile("other.jpg", b"\xff\xd8\xff\xe0" + b"\x00" * 100, content_type="image/jpeg")
        other_photo = Photo.objects.create(post=other_post, image=img, sort_order=0)

        resp = player_client.post(
            f"/post/{run.slug}/post/{post.pk}/edit/",
            {
                "post_type": "character",
                "character_name": "Nadia",
                "content": "Updated",
                "keywords": "",
                "delete_photos": [str(other_photo.pk)],
            },
        )
        assert resp.status_code == 302
        # The other post's photo should NOT have been deleted
        assert Photo.objects.filter(pk=other_photo.pk).exists()
