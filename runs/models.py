from django.db import models


class Run(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return self.name


class House(models.Model):
    run = models.ForeignKey(Run, on_delete=models.CASCADE, related_name="houses")
    name = models.CharField(max_length=100)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        unique_together = [("run", "name")]

    def __str__(self):
        return self.name


class Path(models.Model):
    run = models.ForeignKey(Run, on_delete=models.CASCADE, related_name="paths")
    name = models.CharField(max_length=100)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        unique_together = [("run", "name")]

    def __str__(self):
        return self.name


class Year(models.Model):
    run = models.ForeignKey(Run, on_delete=models.CASCADE, related_name="years")
    name = models.CharField(max_length=100)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order"]
        unique_together = [("run", "name")]

    def __str__(self):
        return self.name


class Club(models.Model):
    run = models.ForeignKey(Run, on_delete=models.CASCADE, related_name="clubs")
    name = models.CharField(max_length=200)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        unique_together = [("run", "name")]

    def __str__(self):
        return self.name


class TeachingSubject(models.Model):
    run = models.ForeignKey(Run, on_delete=models.CASCADE, related_name="teaching_subjects")
    name = models.CharField(max_length=200)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        unique_together = [("run", "name")]

    def __str__(self):
        return self.name


class BloodStatus(models.Model):
    run = models.ForeignKey(Run, on_delete=models.CASCADE, related_name="blood_statuses")
    name = models.CharField(max_length=100)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        unique_together = [("run", "name")]
        verbose_name_plural = "blood statuses"

    def __str__(self):
        return self.name


class CustomAttributeDefinition(models.Model):
    class AttrType(models.TextChoices):
        BOOLEAN = "boolean", "Boolean"
        CHOICE = "choice", "Choice"
        TEXT = "text", "Text"

    class AppliesTo(models.TextChoices):
        STUDENT = "student", "Student"
        PROFESSOR = "professor", "Professor"
        STAFF = "staff", "Staff"
        ALL = "all", "All"

    run = models.ForeignKey(Run, on_delete=models.CASCADE, related_name="custom_attributes")
    name = models.CharField(max_length=200)
    attr_type = models.CharField(max_length=20, choices=AttrType.choices)
    choices = models.JSONField(default=list, blank=True, help_text="List of allowed values for choice type")
    applies_to = models.CharField(max_length=20, choices=AppliesTo.choices, default=AppliesTo.ALL)
    is_filterable = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        unique_together = [("run", "name")]

    def __str__(self):
        return f"{self.name} ({self.run})"


class GlobalKeyword(models.Model):
    label = models.CharField(max_length=200, unique=True)

    class Meta:
        ordering = ["label"]

    def __str__(self):
        return self.label


class GlobalLookingForLabel(models.Model):
    label = models.CharField(max_length=200, unique=True)

    class Meta:
        ordering = ["label"]

    def __str__(self):
        return self.label
