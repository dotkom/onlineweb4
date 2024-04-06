# -*- coding: utf-8 -*-

from django.contrib import admin

from apps.approval.models import MembershipApproval


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
