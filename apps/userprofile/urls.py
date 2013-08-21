# -*- encoding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('apps.userprofile.views',
    url(r'^$', 'index', name='userprofile'),
    url(r'^/removeprofileimage$', 'confirmDeleteImage', name='confirm_delete_image'),
    url(r'^/saveprofile', 'saveUserProfile', name='save_user_profile'),
)
