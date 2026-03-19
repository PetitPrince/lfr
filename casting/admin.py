from django.contrib import admin

from .models import Casting, Invite

RUN_SCOPED_FK_FIELDS = {
    "house": "houses",
    "year": "years",
    "path": "paths",
    "blood_status": "blood_statuses",
    "monitor_of_house": "houses",
    "monitor_of_club": "clubs",
    "teaching_subject": "teaching_subjects",
}

RUN_SCOPED_M2M_FIELDS = {
    "clubs": "clubs",
}


class RunScopedAdminMixin:
    """Filters vocabulary FK/M2M dropdowns to only show options from the object's run."""

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in RUN_SCOPED_FK_FIELDS:
            obj = self._get_obj_from_request(request)
            if obj and obj.run_id:
                m2m_name = RUN_SCOPED_FK_FIELDS[db_field.name]
                kwargs["queryset"] = getattr(obj.run, m2m_name).all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name in RUN_SCOPED_M2M_FIELDS:
            obj = self._get_obj_from_request(request)
            if obj and obj.run_id:
                m2m_name = RUN_SCOPED_M2M_FIELDS[db_field.name]
                kwargs["queryset"] = getattr(obj.run, m2m_name).all()
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def _get_obj_from_request(self, request):
        from django.urls import resolve

        resolved = resolve(request.path_info)
        pk = resolved.kwargs.get("object_id")
        if pk:
            return self.model.objects.filter(pk=pk).select_related("run").first()
        return None


class InviteInline(admin.StackedInline):
    model = Invite
    extra = 0
    readonly_fields = ["code", "claimed_at"]


@admin.register(Casting)
class CastingAdmin(RunScopedAdminMixin, admin.ModelAdmin):
    list_display = ["__str__", "run", "role", "character_name", "house", "year", "path", "is_claimed"]
    list_filter = ["run", "role"]
    search_fields = ["user__email", "character_name"]
    raw_id_fields = ["user"]
    inlines = [InviteInline]

    @admin.display(boolean=True, description="Claimed")
    def is_claimed(self, obj):
        return obj.user is not None


@admin.register(Invite)
class InviteAdmin(admin.ModelAdmin):
    list_display = ["code", "casting", "is_claimed", "claimed_at"]
    search_fields = ["code"]
    readonly_fields = ["code", "claimed_at"]
    raw_id_fields = ["casting"]

    @admin.display(boolean=True, description="Claimed")
    def is_claimed(self, obj):
        return obj.is_claimed
