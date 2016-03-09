# -*- coding: utf-8 -*-

from apps.approval.models import MembershipApproval
from django.contrib import admin


class MembershipApprovalAdmin(admin.ModelAdmin):
    pass


admin.site.register(MembershipApproval, MembershipApprovalAdmin)
