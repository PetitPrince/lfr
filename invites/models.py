import uuid

from django.conf import settings
from django.db import models


class Invite(models.Model):
    run = models.ForeignKey("runs.Run", on_delete=models.CASCADE, related_name="invites")
    code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    claimed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="invites_claimed"
    )
    claimed_at = models.DateTimeField(null=True, blank=True)

    # Pre-filled casting
    role = models.CharField(
        max_length=20,
        choices=[
            ("student", "Student"),
            ("professor", "Professor"),
            ("staff", "Staff"),
            ("headmaster", "Headmaster"),
        ],
        default="student",
    )
    character_name = models.CharField(max_length=300, blank=True)
    house = models.ForeignKey("runs.House", on_delete=models.SET_NULL, null=True, blank=True)
    year = models.ForeignKey("runs.Year", on_delete=models.SET_NULL, null=True, blank=True)
    path = models.ForeignKey("runs.Path", on_delete=models.SET_NULL, null=True, blank=True)
    clubs = models.ManyToManyField("runs.Club", blank=True)
    blood_status = models.ForeignKey("runs.BloodStatus", on_delete=models.SET_NULL, null=True, blank=True)
    teaching_subjects = models.ManyToManyField("runs.TeachingSubject", blank=True)
    monitor_of_house = models.ForeignKey(
        "runs.House", on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    monitor_of_club = models.ForeignKey(
        "runs.Club", on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    staff_title = models.CharField(max_length=300, blank=True)
    custom_attributes = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invite {self.code} ({self.run})"


class RunMembership(models.Model):
    """Canonical record of a player's participation in a run with their casting."""

    class Role(models.TextChoices):
        STUDENT = "student", "Student"
        PROFESSOR = "professor", "Professor"
        STAFF = "staff", "Staff"
        HEADMASTER = "headmaster", "Headmaster"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="run_memberships")
    run = models.ForeignKey("runs.Run", on_delete=models.CASCADE, related_name="memberships")
    invite = models.OneToOneField(Invite, on_delete=models.SET_NULL, null=True, blank=True, related_name="membership")

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    character_name = models.CharField(max_length=300, blank=True)
    house = models.ForeignKey("runs.House", on_delete=models.SET_NULL, null=True, blank=True)
    year = models.ForeignKey("runs.Year", on_delete=models.SET_NULL, null=True, blank=True)
    path = models.ForeignKey("runs.Path", on_delete=models.SET_NULL, null=True, blank=True)
    clubs = models.ManyToManyField("runs.Club", blank=True)
    blood_status = models.ForeignKey("runs.BloodStatus", on_delete=models.SET_NULL, null=True, blank=True)
    teaching_subjects = models.ManyToManyField("runs.TeachingSubject", blank=True)
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
        unique_together = [("user", "run")]

    def __str__(self):
        return f"{self.user} in {self.run} ({self.get_role_display()})"
