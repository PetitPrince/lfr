from django.contrib import admin

from .models import Comment, LookingForEntry, Photo, Post, PostKeyword, Rumor


class PostKeywordInline(admin.TabularInline):
    model = PostKeyword
    extra = 1


class LookingForEntryInline(admin.TabularInline):
    model = LookingForEntry
    extra = 1


class RumorInline(admin.TabularInline):
    model = Rumor
    extra = 0


class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 0


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["__str__", "post_type", "run", "author", "is_published", "created_at"]
    list_filter = ["run", "post_type", "is_published"]
    search_fields = ["title", "content"]
    raw_id_fields = ["author", "casting"]
    inlines = [PostKeywordInline, LookingForEntryInline, RumorInline, PhotoInline]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["__str__", "post", "author", "parent", "is_deleted", "created_at"]
    list_filter = ["post__run", "is_deleted"]
    search_fields = ["body", "author__email"]
    raw_id_fields = ["author", "post", "parent"]
