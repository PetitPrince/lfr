from django.contrib import admin

from .models import (
    BloodStatus,
    Club,
    CustomAttributeDefinition,
    GlobalKeyword,
    GlobalLookingForLabel,
    House,
    Path,
    Run,
    TeachingSubject,
    Year,
)


class CustomAttributeDefinitionInline(admin.TabularInline):
    model = CustomAttributeDefinition
    extra = 0


@admin.register(Run)
class RunAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "start_date", "end_date", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ["houses", "paths", "years", "clubs", "teaching_subjects", "blood_statuses"]
    inlines = [CustomAttributeDefinitionInline]


@admin.register(House)
class HouseAdmin(admin.ModelAdmin):
    list_display = ["name", "color", "sort_order"]
    search_fields = ["name"]


@admin.register(Path)
class PathAdmin(admin.ModelAdmin):
    list_display = ["name", "sort_order"]
    search_fields = ["name"]


@admin.register(Year)
class YearAdmin(admin.ModelAdmin):
    list_display = ["name", "color", "sort_order"]
    search_fields = ["name"]


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ["name", "sort_order"]
    search_fields = ["name"]


@admin.register(TeachingSubject)
class TeachingSubjectAdmin(admin.ModelAdmin):
    list_display = ["name", "sort_order"]
    search_fields = ["name"]


@admin.register(BloodStatus)
class BloodStatusAdmin(admin.ModelAdmin):
    list_display = ["name", "sort_order"]
    search_fields = ["name"]


@admin.register(CustomAttributeDefinition)
class CustomAttributeDefinitionAdmin(admin.ModelAdmin):
    list_display = ["name", "run", "attr_type", "applies_to", "is_filterable"]
    list_filter = ["run", "attr_type", "applies_to", "is_filterable"]


@admin.register(GlobalKeyword)
class GlobalKeywordAdmin(admin.ModelAdmin):
    list_display = ["label"]
    search_fields = ["label"]


@admin.register(GlobalLookingForLabel)
class GlobalLookingForLabelAdmin(admin.ModelAdmin):
    list_display = ["label"]
    search_fields = ["label"]
