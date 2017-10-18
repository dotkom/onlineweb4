# -*- coding: utf-8 -*-

from django.contrib import admin

from apps.approval.models import CommitteeApplication, CommitteePriority, MembershipApproval


class CommitteePriorityInline(admin.TabularInline):
    model = CommitteePriority


class CommitteeApplicationAdmin(admin.ModelAdmin):
    model = CommitteeApplication
    inlines = [CommitteePriorityInline]
    list_display = ['__str__', 'get_name', 'created', 'prioritized']
    list_filter = ['prioritized', 'committees']
    search_fields = ['name', 'email', 'applicant__first_name', 'applicant__last_name', 'applicant__email']


class MembershipApprovalAdmin(admin.ModelAdmin):
    pass


admin.site.register(CommitteeApplication, CommitteeApplicationAdmin)
admin.site.register(MembershipApproval, MembershipApprovalAdmin)
