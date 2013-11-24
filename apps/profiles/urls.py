# -*- encoding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('apps.profiles.views',
    url(r'^$', 'index', name='profiles'),
    url(r'^removeprofileimage/$', 'confirm_delete_image', name='confirm_delete_image'),
    url(r'^saveprofile/$', 'save_user_profile', name='save_user_profile'),
    url(r'^saveprivacy/$', 'save_privacy', name='save_privacy'),
    url(r'^savepassword/$', 'save_password', name='save_password'),
    url(r'^updateactivetab/$', 'update_active_tab', name='update_active_profiles_tab'),
    url(r'^uploadimage/$', 'upload_image', name='upload_image'),
    url(r'^add_email/$', 'add_email', name='profile_add_email'),
    url(r'^delete_email/$', 'delete_email', name='profile_delete_email'),
    url(r'^set_primary/$', 'set_primary', name='profile_set_primary'),
    url(r'^verify_email/$', 'verify_email', name='profile_verify_email'),
    url(r'^save_membership_details/$', 'save_membership_details', name='profile_save_membership_details'),
)
