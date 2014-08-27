# -*- encoding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('apps.profiles.views',
    url(r'^$', 'index', name='profiles'),
    url(r'^saveprofile/$', 'saveUserProfile', name='save_user_profile'),
    url(r'^saveprivacy/$', 'savePrivacy', name='save_privacy'),
    url(r'^savepassword/$', 'savePassword', name='save_password'),
    url(r'^saveposition/$', 'save_position', name='save_position'),
    url(r'^deleteposition/$', 'delete_position', name='delete_position'),
    url(r'^updateactivetab/$', 'updateActiveTab', name='update_active_profiles_tab'),
    url(r'^add_email/$', 'add_email', name='profile_add_email'),
    url(r'^delete_email/$', 'delete_email', name='profile_delete_email'),
    url(r'^set_primary/$', 'set_primary', name='profile_set_primary'),
    url(r'^verify_email/$', 'verify_email', name='profile_verify_email'),
    url(r'^save_membership_details/$', 'save_membership_details', name='profile_save_membership_details'),
    url(r'^update_mark_rules/$', 'update_mark_rules', name='update_mark_rules'),
    
    url(r'^api_user_search/$', 'api_user_search', name='profiles_api_user_search'),
    url(r'^user_search/$', 'user_search', name='profiles_user_search'),
    url(r'^(?P<username>[a-zA-Z0-9_-]+)/$', 'view_profile', name='profiles_view'),
)
