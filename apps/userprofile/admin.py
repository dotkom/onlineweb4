# -*- coding: utf-8 -*-

from django.forms import models
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from apps.userprofile.models import UserProfile

admin.site.unregister(User)

class NoDeleteInline(models.BaseInlineFormSet):
    """ 
    Custom formset to prevent deletion

    Used by the inline for userprofiles to prevent the possibility
    of deleting the profile object
    """
    def __init__(self, *args, **kwargs):
        super(NoDeleteInline, self).__init__(*args, **kwargs)
        self.can_delete = False

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    formset = NoDeleteInline
    # Prevents the userprofile inline from being collapsed when
    # the user admin detail screen is opened.
    inline_classes = ('grp-collapse', 'grp-open',)

class UserProfileAdmin(UserAdmin):
    inlines = [UserProfileInline,]
    list_display = ('username', 'first_name', 'last_name', 'field_of_study',)
    list_filter = ('groups', 'is_staff', 'is_superuser')
    filter_horizontal = ('groups',)

    def field_of_study(self, obj):
        return obj.get_profile().get_field_of_study_display()
    field_of_study.short_description = "Studieretning"

admin.site.register(User, UserProfileAdmin)
