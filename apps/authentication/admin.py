# -*- coding: utf-8 -*-

from django.contrib import admin
from django.utils.translation import ugettext as _

from apps.authentication.models import AllowedUsername, Email, OnlineUser, Position


class EmailInline(admin.TabularInline):
    model = Email
    extra = 1 


class OnlineUserAdmin(admin.ModelAdmin):
    model = OnlineUser
    inlines = (EmailInline,)
    list_display = ['username', 'first_name', 'last_name', 'ntnu_username', 'field_of_study', 'is_member',]
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups__name')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_(u'Personlig info'), {'fields': ('first_name', 'last_name', 'phone_number', )}),
        (_(u'Studieinformasjon'), {'fields': ('ntnu_username', 'field_of_study', 'started_date', 'compiled',)}),
        (_(u'Adresse'), {'fields': ('address', 'zip_code',)}), 
        (_(u'Viktige datoer'), {'fields': ('last_login', 'date_joined',)}),
        (_(u'Annen info'), { 'fields': ('infomail', 'mark_rules', 'rfid', 'nickname', 'website',) }),
        (_(u'Tilganger'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
    )
    filter_horizontal = ('groups', 'user_permissions',)
    search_fields = ('first_name', 'last_name', 'username', 'ntnu_username',)

admin.site.register(OnlineUser, OnlineUserAdmin)


class AllowedUsernameAdmin(admin.ModelAdmin):
    model = AllowedUsername
    list_display = ('username', 'registered', 'expiration_date', 'note')
    fieldsets = (
        (None, {'fields': ('username', 'registered', 'expiration_date')}),
        (_(u'Notater'), {'fields': ('note', 'description')}),

    )
    search_fields = ('username',)

admin.site.register(AllowedUsername, AllowedUsernameAdmin)


class PositionAdmin(admin.ModelAdmin):
    model = Position

admin.site.register(Position, PositionAdmin)
