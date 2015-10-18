# -*- coding: utf-8 -*-

from django.contrib import admin
from django.utils.translation import ugettext as _

from apps.authentication.models import AllowedUsername, Email, OnlineUser, Position, SpecialPosition

from reversion.admin import VersionAdmin


class EmailInline(admin.TabularInline):
    model = Email
    extra = 1 


class OnlineUserAdmin(VersionAdmin):
    model = OnlineUser
    inlines = (EmailInline,)
    list_display = ['username', 'first_name', 'last_name', 'ntnu_username', 'field_of_study', 'is_member',]
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups__name')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_(u'Personlig info'), {'fields': ('first_name', 'last_name', 'phone_number', 'online_mail' )}),
        (_(u'Studieinformasjon'), {'fields': ('ntnu_username', 'field_of_study', 'started_date', 'compiled',)}),
        (_(u'Adresse'), {'fields': ('address', 'zip_code',)}), 
        (_(u'Viktige datoer'), {'fields': ('last_login', 'date_joined',)}),
        (_(u'Annen info'), { 'fields': ('infomail', 'jobmail', 'mark_rules', 'rfid', 'nickname', 'website',) }),
        (_(u'Tilganger'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
    )
    filter_horizontal = ('groups', 'user_permissions',)
    search_fields = ('first_name', 'last_name', 'username', 'ntnu_username',)

admin.site.register(OnlineUser, OnlineUserAdmin)


class AllowedUsernameAdmin(VersionAdmin):
    model = AllowedUsername
    list_display = ('username', 'registered', 'expiration_date', 'note')
    fieldsets = (
        (None, {'fields': ('username', 'registered', 'expiration_date')}),
        (_(u'Notater'), {'fields': ('note', 'description')}),

    )
    search_fields = ('username',)
    
    def save_model(self, request, obj, form, change):
        if not change:
            # Try to fetch user with this username
            try:
                user = OnlineUser.objects.get(ntnu_username=obj.username)
            except OnlineUser.DoesNotExist:
                user = None
            
            # If username was found, set infomail to True
            if user and user.infomail is False:
                user.infomail = True
                user.save()
        obj.save()

admin.site.register(AllowedUsername, AllowedUsernameAdmin)


class PositionAdmin(VersionAdmin):
    model = Position

admin.site.register(Position, PositionAdmin)


class SpecialPositionAdmin(VersionAdmin):
    model = SpecialPosition

admin.site.register(SpecialPosition, SpecialPositionAdmin)
