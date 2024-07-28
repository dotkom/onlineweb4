from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext as _
from reversion.admin import VersionAdmin

from apps.authentication.models import (
    GroupMember,
    GroupRole,
    Membership,
    OnlineGroup,
    OnlineUser,
    Position,
    SpecialPosition,
)
from apps.marks.models import MarkDelay, MarkUser, Suspended, Suspension, user_sanctions


class MarkUserInline(admin.TabularInline):
    model = MarkUser
    extra = 0
    fields = ("mark",)
    readonly_fields = ("mark",)

    verbose_name = _("Prikk")
    verbose_name_plural = _("Prikker")


class SuspensionInline(admin.TabularInline):
    model = Suspension
    extra = 0
    show_change_link = True
    fields = ("title", "created_time", "expiration_date")
    readonly_fields = ("title", "created_time", "expiration_date")

    verbose_name = _("Suspensjon")
    verbose_name_plural = _("Suspensjoner")


class OnlineUserAdmin(UserAdmin, VersionAdmin):
    model = OnlineUser
    inlines = (
        MarkUserInline,
        SuspensionInline,
    )
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
        (None, {"fields": ("email", "username", "auth0_subject")}),
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
        (
            _("Sanksjoner"),
            {
                "fields": ("current_total_sanctions",),
            },
        ),
    )
    filter_horizontal = ("groups", "user_permissions")
    search_fields = ("first_name", "last_name", "username", "ntnu_username")
    readonly_fields = (
        "mark_rules_accepted",
        "auth0_subject",
        "current_total_sanctions",
    )

    def current_total_sanctions(self, instance: OnlineUser):
        match user_sanctions(instance):
            case Suspended():
                return "Suspendert"
            case MarkDelay(delay):
                return _("Forsinket påmelding med %s") % delay
            case None:
                return "-"

    current_total_sanctions.str = True
    current_total_sanctions.short_description = "Nåværende sanksjoner"

    def is_member(self, instance: OnlineUser):
        return instance.is_member

    is_member.boolean = True

    def mark_rules_accepted(self, instance: OnlineUser):
        return instance.mark_rules_accepted

    mark_rules_accepted.boolean = True

    def get_queryset(self, *args, **kwargs):
        return (
            super()
            .get_queryset(*args, **kwargs)
            .prefetch_related("marks", "suspension_set")
        )


admin.site.register(OnlineUser, OnlineUserAdmin)


class MembershipAdmin(VersionAdmin):
    model = Membership
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


admin.site.register(Membership, MembershipAdmin)


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

    def get_queryset(self, *args):
        return (
            super().get_queryset(*args).select_related("user").prefetch_related("roles")
        )


@admin.register(OnlineGroup)
class OnlineGroupAdmin(VersionAdmin):
    model = OnlineGroup
    list_display = ("name_short", "name_long", "member_count", "verbose_type")
    list_display_links = ("name_short", "name_long")
    search_fields = ("name_short", "name_long", "group_type", "email")
    inlines = (GroupMemberInlineAdmin,)

    def member_count(self, group: OnlineGroup):
        return f"{group.members.count()} ({group.group.user_set.count()})"

    member_count.admin_order_field = "members__count"
    member_count.short_description = "Antall medlemmer (synkronisert)"

    def get_queryset(self, *args):
        return (
            super()
            .get_queryset(*args)
            .select_related("group")
            .prefetch_related("group__user_set", "members", "members__roles")
        )


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
        return (
            super().get_queryset(*args).select_related("user").prefetch_related("roles")
        )


@admin.register(GroupRole)
class GroupRoleAdmin(VersionAdmin):
    model = GroupRole
    fields = ("role_type",)
    list_display = ("role_type", "verbose_name")
    search_fields = ("role_type",)
