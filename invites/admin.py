from django.contrib import admin

from .models import Invite, RunMembership


@admin.register(Invite)
class InviteAdmin(admin.ModelAdmin):
    list_display = ["code", "run", "role", "character_name", "claimed_by", "claimed_at"]
    list_filter = ["run", "role"]
    search_fields = ["code", "character_name"]
    raw_id_fields = ["claimed_by"]
    readonly_fields = ["code"]


@admin.register(RunMembership)
class RunMembershipAdmin(admin.ModelAdmin):
    list_display = ["user", "run", "role", "character_name", "house", "year", "path"]
    list_filter = ["run", "role"]
    search_fields = ["user__email", "character_name"]
    raw_id_fields = ["user", "invite"]
