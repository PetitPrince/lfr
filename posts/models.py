from django.conf import settings
from django.db import models


class Post(models.Model):
    class PostType(models.TextChoices):
        CHARACTER = "character", "Character Introduction"
        OTHER = "other", "Other"

    class OtherCategory(models.TextChoices):
        EXTRACURRICULAR = "extracurricular", "Extracurricular"
        SCHOOL_PLOT = "school_plot", "School-wide Plot"
        CLUB_RECRUITMENT = "club_recruitment", "Club Recruitment"
        OTHER = "other", "Other"

    run = models.ForeignKey("runs.Run", on_delete=models.CASCADE, related_name="posts")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name="posts")
    casting = models.ForeignKey(
        "casting.Casting", on_delete=models.SET_NULL, null=True, blank=True, related_name="posts"
    )
    post_type = models.CharField(max_length=20, choices=PostType.choices)

    # Shared fields
    content = models.TextField(blank=True)

    # "Other" post fields
    title = models.CharField(max_length=500, blank=True)
    category = models.CharField(max_length=30, choices=OtherCategory.choices, blank=True)
    club = models.ForeignKey("runs.Club", on_delete=models.SET_NULL, null=True, blank=True, related_name="posts")

    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        if self.post_type == self.PostType.CHARACTER:
            if self.casting:
                return self.casting.character_name or f"Post #{self.pk}"
            return f"Post #{self.pk}"
        return self.title or f"Post #{self.pk}"


class PostKeyword(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="keywords")
    label = models.CharField(max_length=200)

    def __str__(self):
        return self.label


class LookingForEntry(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="looking_for_entries")
    label = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order"]
        verbose_name_plural = "looking for entries"

    def __str__(self):
        return self.label


class Rumor(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="rumors")
    text = models.TextField()
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return self.text[:80]


class Photo(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="posts/photos/%Y/%m/")
    caption = models.CharField(max_length=500, blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return self.caption or f"Photo #{self.pk}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments")
    body = models.TextField()
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.author} on {self.post}"
