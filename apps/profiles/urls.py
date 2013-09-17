# -*- encoding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('apps.profiles.views',
    url(r'^$', 'index', name='profiles'),
    url(r'^/removeprofileimage$', 'confirmDeleteImage', name='confirm_delete_image'),
    url(r'^/saveprofile', 'saveUserProfile', name='save_user_profile'),
    url(r'^/saveprivacy', 'savePrivacy', name='save_privacy'),
    url(r'^/savepassword', 'savePassword', name='save_password'),
    url(r'^/updateactivetab', 'updateActiveTab', name='update_active_profiles_tab'),
)
