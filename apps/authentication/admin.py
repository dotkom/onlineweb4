# -*- coding: utf-8 -*-

from django.contrib import admin
from django.utils.translation import ugettext as _

from apps.authentication.models import OnlineUser

class OnlineUserAdmin(admin.ModelAdmin):
    model = OnlineUser
    list_display = ['username', 'first_name', 'last_name', 'field_of_study', 'is_online',]
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    fieldsets = (
        (None, {
            'fields': (
                'username',
                'password'
            )
        }),
        (_('Personal info'), {
            'fields': (
                'first_name',
                'last_name',
                'email',
                'phone_number',
            )
        }),
        (_('Studieinformasjon'), {
            'fields': (
                'ntnu_username',
                'field_of_study',
                'started_date',
                'compiled',
            )
        }),
        (_('Address'), {
            'fields': (
                'address',
                'zip_code',
            )
        }),
        (_('Important dates'), {
            'fields': (
                'last_login',
                'date_joined',
            )
        }),
        (_('Allergies'), {
           'fields': (
               'allergies',
           )
        }),
        (_('Other info'), {
           'fields': (
               'infomail',
               'mark_rules',
               'rfid',
               'nickname',
               'website',
               'image',
           )
        }),
        (_('Permissions'), {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            )
        }),
    )
    filter_horizontal = ('groups', 'user_permissions',)

admin.site.register(OnlineUser, OnlineUserAdmin)
