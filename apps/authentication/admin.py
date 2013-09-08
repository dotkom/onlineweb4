# -*- coding: utf-8 -*-

from django.contrib import admin
from django.utils.translation import ugettext as _

from apps.authentication.models import OnlineUser, AllowedUsername

class OnlineUserAdmin(admin.ModelAdmin):
    model = OnlineUser
    list_display = ['username', 'first_name', 'last_name', 'field_of_study', 'is_member',]
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_(u'Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone_number', )}),
        (_(u'Studieinformasjon'), {'fields': ('ntnu_username', 'field_of_study', 'started_date', 'compiled',)}),
        (_(u'Address'), {'fields': ('address', 'zip_code',)}), 
        (_(u'Important dates'), {'fields': ('last_login', 'date_joined',)}),
        (_(u'Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
    )
    filter_horizontal = ('groups', 'user_permissions',)

admin.site.register(OnlineUser, OnlineUserAdmin)

class AllowedUsernameAdmin(admin.ModelAdmin):
    model = AllowedUsername
    list_display = ('username', 'registered', 'expiration_date', 'note')
    fieldsets = (
        (None, {'fields': ('username', 'registered', 'expiration_date')}),
        (_(u'Notater'), {'fields': ('note', 'description')}),

    )

admin.site.register(AllowedUsername, AllowedUsernameAdmin)
