import pytest
from collections import Counter

from conftest import (
    CastingFactory,
    HouseFactory,
    PathFactory,
    PostFactory,
    PostKeywordFactory,
    RunFactory,
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
