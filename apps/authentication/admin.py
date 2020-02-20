# -*- coding: utf-8 -*-

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext as _
from reversion.admin import VersionAdmin

from apps.authentication.models import (
    AllowedUsername,
    Email,
    GroupMember,
    GroupRole,
    OnlineGroup,
    OnlineUser,
    Position,
    SpecialPosition,
)


class EmailInline(admin.TabularInline):
    model = Email
    extra = 1


class OnlineUserAdmin(UserAdmin, VersionAdmin):
    model = OnlineUser
    inlines = (EmailInline,)
    list_display = [
        "username",
        "first_name",
        "last_name",
        "ntnu_username",
        "field_of_study",
        "is_member",
    ]
    list_filter = ("is_staff", "is_superuser", "is_active", "groups__name")
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Personlig info"),
            {"fields": ("first_name", "last_name", "phone_number", "online_mail")},
        ),
        (
            _("Studieinformasjon"),
            {"fields": ("ntnu_username", "field_of_study", "started_date", "compiled")},
        ),
        (_("Adresse"), {"fields": ("address", "zip_code")}),
        (_("Viktige datoer"), {"fields": ("last_login", "date_joined")}),
        (
            _("Annen info"),
            {
                "fields": (
                    "infomail",
                    "jobmail",
                    "mark_rules_accepted",
                    "rfid",
                    "nickname",
                    "website",
                )
            },
        ),
        (
            _("Tilganger"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
    )
    filter_horizontal = ("groups", "user_permissions")
    search_fields = ("first_name", "last_name", "username", "ntnu_username")
    readonly_fields = ("mark_rules_accepted",)

    def is_member(self, instance: OnlineUser):
        return instance.is_member

    is_member.boolean = True

    def mark_rules_accepted(self, instance: OnlineUser):
        return instance.mark_rules_accepted

    mark_rules_accepted.boolean = True


admin.site.register(OnlineUser, OnlineUserAdmin)


class AllowedUsernameAdmin(VersionAdmin):
    model = AllowedUsername
    list_display = ("username", "registered", "expiration_date", "note", "is_active")
    fieldsets = (
        (None, {"fields": ("username", "registered", "expiration_date")}),
        (_("Notater"), {"fields": ("note", "description")}),
    )
    search_fields = ("username",)

    def save_model(self, request, obj, form, change):
        if not change:
            # Try to fetch user with this username
            try:
                user = OnlineUser.objects.get(ntnu_username=obj.username)
            except OnlineUser.DoesNotExist:
                user = None

            # If username was found, set infomail to True
            if user and user.infomail is False:
                user.infomail = True
                user.save()
        obj.save()

    def is_active(self, instance):
        return instance.is_active

    is_active.boolean = True


admin.site.register(AllowedUsername, AllowedUsernameAdmin)


class PositionAdmin(VersionAdmin):
    model = Position


admin.site.register(Position, PositionAdmin)


class SpecialPositionAdmin(VersionAdmin):
    model = SpecialPosition


admin.site.register(SpecialPosition, SpecialPositionAdmin)


class GroupMemberInlineAdmin(admin.StackedInline):
    model = GroupMember
    extra = 0
    fk_name = "group"


@admin.register(OnlineGroup)
class OnlineGroupAdmin(VersionAdmin):
    model = OnlineGroup
    list_display = ("name_short", "name_long", "member_count", "verbose_type", "leader")
    list_display_links = ("name_short", "name_long")
    search_fields = ("name_short", "name_long", "group_type", "email")
    inlines = (GroupMemberInlineAdmin,)

    def member_count(self, group: OnlineGroup):
        return f"{group.members.count()} ({group.group.user_set.count()})"

    member_count.admin_order_field = "members__count"
    member_count.short_description = "Antall medlemmer (synkronisert)"


class MemberRoleInline(admin.TabularInline):
    model = GroupMember.roles.through
    extra = 0


@admin.register(GroupMember)
class GroupMemberAdmin(VersionAdmin):
    model = GroupMember
    list_display = ("user", "group", "all_roles")
    list_filter = ("group", "roles")
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "group__name_short",
        "group__name_long",
        "roles__role_type",
    )
    inlines = (MemberRoleInline,)

    def all_roles(self, member: GroupMember):
        return ", ".join([role.verbose_name for role in member.roles.all()])

    all_roles.short_description = "Roller"

    def get_queryset(self, *args):
        return super().get_queryset(*args).prefetch_related("roles")


@admin.register(GroupRole)
class GroupRoleAdmin(VersionAdmin):
    model = GroupRole
    list_display = ("role_type", "verbose_name")
    search_fields = ("role_type",)
