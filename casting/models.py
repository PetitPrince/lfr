import uuid

from django.conf import settings
from django.db import models


class Casting(models.Model):
    """A player's casting in a run. Created by organizers with user=null,
    then linked to a player when they claim an invite code."""

    class Role(models.TextChoices):
        STUDENT = "student", "Student"
        PROFESSOR = "professor", "Professor"
        STAFF = "staff", "Staff"
        HEADMASTER = "headmaster", "Headmaster"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="castings"
    )
    run = models.ForeignKey("runs.Run", on_delete=models.CASCADE, related_name="castings")

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    character_name = models.CharField(max_length=300, blank=True)
    house = models.ForeignKey("runs.House", on_delete=models.SET_NULL, null=True, blank=True)
    year = models.ForeignKey("runs.Year", on_delete=models.SET_NULL, null=True, blank=True)
    path = models.ForeignKey("runs.Path", on_delete=models.SET_NULL, null=True, blank=True)
    clubs = models.ManyToManyField("runs.Club", blank=True)
    blood_status = models.ForeignKey("runs.BloodStatus", on_delete=models.SET_NULL, null=True, blank=True)
    teaching_subject = models.ForeignKey("runs.TeachingSubject", on_delete=models.SET_NULL, null=True, blank=True)
    monitor_of_house = models.ForeignKey(
        "runs.House", on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    monitor_of_club = models.ForeignKey(
        "runs.Club", on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    staff_title = models.CharField(max_length=300, blank=True)
    custom_attributes = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "run"], name="unique_user_per_run", condition=models.Q(user__isnull=False)),
        ]

    def __str__(self):
        if self.user:
            return f"{self.user} in {self.run} ({self.get_role_display()})"
        return f"Unclaimed slot in {self.run} ({self.get_role_display()})"


class Invite(models.Model):
    """Thin claim token. Points to a Casting. Claiming sets casting.user."""

    casting = models.OneToOneField(Casting, on_delete=models.CASCADE, related_name="invite")
    code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    claimed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invite {self.code} ({self.casting.run})"

    @property
    def is_claimed(self):
        return self.casting.user is not None
