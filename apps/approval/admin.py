# -*- coding: utf-8 -*-

from django.contrib import admin

from apps.approval.models import MembershipApproval


class MembershipApprovalAdmin(admin.ModelAdmin):
    pass


admin.site.register(MembershipApproval, MembershipApprovalAdmin)
