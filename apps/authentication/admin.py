# -*- coding: utf-8 -*-

from django.contrib import admin

from apps.authentication.models import OnlineUser

class OnlineUserAdmin(admin.ModelAdmin):
    model = OnlineUser
    list_display = ['username', 'first_name', 'last_name', 'field_of_study',]

admin.site.register(OnlineUser, OnlineUserAdmin)
