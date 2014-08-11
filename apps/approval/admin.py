#-*- coding: utf-8 -*-

from django.contrib import admin

from apps.approval.models import MembershipApproval, FieldOfStudyApproval


class MembershipApprovalAdmin(admin.ModelAdmin):
    pass


class FieldOfStudyApprovalAdmin(admin.ModelAdmin):
    pass


admin.site.register(MembershipApproval, MembershipApprovalAdmin)
admin.site.register(FieldOfStudyApproval, FieldOfStudyApprovalAdmin)
