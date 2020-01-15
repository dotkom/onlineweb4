from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import GroupSync, GsuiteAlias, GsuiteGroup


@admin.register(GroupSync)
class GroupSyncAdmin(VersionAdmin):
    model = GroupSync
    list_display = ("online_group", "gsuite_group", "all_roles", "gsuite_role")
    search_fields = (
        "online_group__name_short",
        "online_group__name_long",
        "gsuite_group__email_name",
        "gsuite_role",
        "roles__role_type",
    )

    def all_roles(self, group_sync: GroupSync):
        return ", ".join([role.verbose_name for role in group_sync.roles.all()])

    all_roles.short_description = "Roller"

    def get_queryset(self, *args):
        return super().get_queryset(*args).prefetch_related("roles")


class GsuiteAliasInlineAdmin(admin.StackedInline):
    model = GsuiteAlias
    extra = 0


@admin.register(GsuiteGroup)
class GsuiteGroupAdmin(VersionAdmin):
    model = GsuiteGroup
    list_display = ("name", "email")
    search_fields = ("email_name", "main_group__name_long", "main_group__name_short")
    inlines = (GsuiteAliasInlineAdmin,)
