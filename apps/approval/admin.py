# -*- coding: utf-8 -*-

from django.contrib import admin
from django.contrib.admin import register

from apps.approval.models import CommitteeApplication, CommitteePriority, MembershipApproval


class CommitteePriorityInline(admin.TabularInline):
    model = CommitteePriority


class CommitteeApplicationAdmin(admin.ModelAdmin):
    model = CommitteeApplication
    inlines = [CommitteePriorityInline]
    list_display = ['__str__', 'get_name', 'created', 'prioritized']
    list_filter = ['prioritized', 'committees']
    search_fields = ['name', 'email', 'applicant__first_name', 'applicant__last_name', 'applicant__email']


@register(MembershipApproval)
class MembershipApprovalAdmin(admin.ModelAdmin):
    model = MembershipApproval
    list_display = (
        '__str__', 'applicant', 'approver', 'created', 'processed', 'approved',
    )
    list_filter = ('approved', 'processed')
    search_fields = (
        'applicant__first_name', 'applicant__last_name', 'applicant__username', 'applicant__ntnu_username',
    )


admin.site.register(CommitteeApplication, CommitteeApplicationAdmin)
