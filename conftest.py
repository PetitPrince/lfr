import factory
import pytest
from django.test import Client

from accounts.models import User
from casting.models import Casting, Invite
from posts.models import Post, PostKeyword
from runs.models import (
    BloodStatus,
    Club,
    CustomAttributeDefinition,
    House,
    Path,
    Run,
    TeachingSubject,
    Year,
)


# ── Vocabulary Factories ──


class HouseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = House
        django_get_or_create = ("name",)

    name = factory.Sequence(lambda n: f"House {n}")


class PathFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Path
        django_get_or_create = ("name",)

    name = factory.Sequence(lambda n: f"Path {n}")


class YearFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Year
        django_get_or_create = ("name",)

    name = factory.Sequence(lambda n: f"Year {n}")


class ClubFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Club
        django_get_or_create = ("name",)

    name = factory.Sequence(lambda n: f"Club {n}")


class TeachingSubjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TeachingSubject
        django_get_or_create = ("name",)

    name = factory.Sequence(lambda n: f"Subject {n}")


class BloodStatusFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BloodStatus
        django_get_or_create = ("name",)

    name = factory.Sequence(lambda n: f"BloodStatus {n}")


# ── Run Factory ──


class RunFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Run

    name = factory.Sequence(lambda n: f"Run {n}")
    slug = factory.Sequence(lambda n: f"run-{n}")
    is_active = True
    is_template = False


# ── User Factory ──


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@test.com")
    role = User.Role.PLAYER

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        password = kwargs.pop("password", "testpass123")
        user = model_class(*args, **kwargs)
        user.set_password(password)
        user.save()
        return user


# ── Casting & Invite Factories ──


class CastingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Casting

    run = factory.SubFactory(RunFactory)
    role = Casting.Role.STUDENT
    character_name = factory.Sequence(lambda n: f"Character {n}")


class InviteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Invite

    casting = factory.SubFactory(CastingFactory)


class PostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Post

    run = factory.SubFactory(RunFactory)
    casting = factory.SubFactory(CastingFactory)
    post_type = Post.PostType.CHARACTER
    content = "A character post."
    is_published = True


class PostKeywordFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PostKeyword

    post = factory.SubFactory(PostFactory)
    label = factory.Sequence(lambda n: f"keyword-{n}")


class CustomAttributeDefinitionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CustomAttributeDefinition

    run = factory.SubFactory(RunFactory)
    name = factory.Sequence(lambda n: f"Attr {n}")
    attr_type = CustomAttributeDefinition.AttrType.BOOLEAN
    applies_to = CustomAttributeDefinition.AppliesTo.ALL


# ── Fixtures ──


@pytest.fixture
def organizer(db):
    return UserFactory(email="organizer@test.com", role=User.Role.ORGANIZER)


@pytest.fixture
def admin_user(db):
    return UserFactory(email="admin@test.com", role=User.Role.ADMIN)


@pytest.fixture
def player(db):
    return UserFactory(email="player@test.com", role=User.Role.PLAYER)


@pytest.fixture
def organizer_client(organizer):
    client = Client()
    client.login(username=organizer.email, password="testpass123")
    return client


@pytest.fixture
def player_client(player):
    client = Client()
    client.login(username=player.email, password="testpass123")
    return client


@pytest.fixture
def run(db):
    """A run with some vocabulary attached."""
    r = RunFactory(name="Test Run", slug="test-run")
    h1 = HouseFactory(name="Libussa")
    h2 = HouseFactory(name="Faust")
    r.houses.set([h1, h2])
    y1 = YearFactory(name="1st Year")
    y2 = YearFactory(name="3rd Year")
    r.years.set([y1, y2])
    p1 = PathFactory(name="Herbology")
    r.paths.set([p1])
    c1 = ClubFactory(name="Duelling Club")
    c2 = ClubFactory(name="Quidditch")
    r.clubs.set([c1, c2])
    s1 = TeachingSubjectFactory(name="Potions")
    r.teaching_subjects.set([s1])
    bs = BloodStatusFactory(name="Pure-blood")
    r.blood_statuses.set([bs])
    return r


@pytest.fixture
def template_run(db):
    """A template run used as blueprint."""
    r = RunFactory(name="Czocha Template", slug="czocha-template", is_template=True)
    h = HouseFactory(name="Libussa")
    r.houses.set([h])
    y = YearFactory(name="1st Year")
    r.years.set([y])
    return r
