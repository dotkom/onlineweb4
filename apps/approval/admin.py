# -*- coding: utf-8 -*-

from django.contrib import admin

from apps.approval.models import (
    CommitteeApplication,
    CommitteeApplicationPeriod,
    CommitteePriority,
    MembershipApproval,
)


@admin.register(CommitteeApplicationPeriod)
class CommitteeApplicationPeriodAdmin(admin.ModelAdmin):
    model = CommitteeApplicationPeriod
    list_display = ["title", "year", "start", "deadline"]
    search_fields = ["title", "start", "deadline"]
    list_filter = ["committees"]


class CommitteePriorityInline(admin.TabularInline):
    model = CommitteePriority


@admin.register(CommitteeApplication)
class CommitteeApplicationAdmin(admin.ModelAdmin):
    model = CommitteeApplication
    inlines = [CommitteePriorityInline]
    list_display = ["__str__", "get_name", "created", "prioritized"]
    list_filter = ["application_period", "prioritized", "committees"]
    search_fields = [
        "name",
        "email",
        "applicant__first_name",
        "applicant__last_name",
        "applicant__email",
    ]


@admin.register(MembershipApproval)
class MembershipApprovalAdmin(admin.ModelAdmin):
    model = MembershipApproval
    list_display = (
        "__str__",
        "applicant",
        "approver",
        "created",
        "processed",
        "approved",
    )
    list_filter = ("approved", "processed")
    search_fields = (
        "applicant__first_name",
        "applicant__last_name",
        "applicant__username",
        "applicant__ntnu_username",
    )
