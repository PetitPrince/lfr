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


class HouseInline(admin.TabularInline):
    model = House
    extra = 1


class PathInline(admin.TabularInline):
    model = Path
    extra = 1


class YearInline(admin.TabularInline):
    model = Year
    extra = 1


class ClubInline(admin.TabularInline):
    model = Club
    extra = 1


class TeachingSubjectInline(admin.TabularInline):
    model = TeachingSubject
    extra = 1


class BloodStatusInline(admin.TabularInline):
    model = BloodStatus
    extra = 1


class CustomAttributeDefinitionInline(admin.TabularInline):
    model = CustomAttributeDefinition
    extra = 0


@admin.register(Run)
class RunAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "start_date", "end_date", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}
    inlines = [
        HouseInline,
        PathInline,
        YearInline,
        ClubInline,
        TeachingSubjectInline,
        BloodStatusInline,
        CustomAttributeDefinitionInline,
    ]


@admin.register(House)
class HouseAdmin(admin.ModelAdmin):
    list_display = ["name", "run", "sort_order"]
    list_filter = ["run"]


@admin.register(Path)
class PathAdmin(admin.ModelAdmin):
    list_display = ["name", "run", "sort_order"]
    list_filter = ["run"]


@admin.register(Year)
class YearAdmin(admin.ModelAdmin):
    list_display = ["name", "run", "sort_order"]
    list_filter = ["run"]


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ["name", "run", "sort_order"]
    list_filter = ["run"]


@admin.register(TeachingSubject)
class TeachingSubjectAdmin(admin.ModelAdmin):
    list_display = ["name", "run", "sort_order"]
    list_filter = ["run"]


@admin.register(BloodStatus)
class BloodStatusAdmin(admin.ModelAdmin):
    list_display = ["name", "run", "sort_order"]
    list_filter = ["run"]


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
