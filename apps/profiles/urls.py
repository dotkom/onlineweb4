# -*- encoding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'apps.profiles.views',
    url(r'^$', 'index', name='profiles'),

    # Show a specific profile.
    url(r'^view/(?P<username>[a-zA-Z0-9_-]+)/$', 'view_profile', name='profiles_view'),

    url(r'^edit/$', 'edit_profile', name='profile_edit'),
    url(r'^privacy/$', 'privacy', name='profile_privacy'),
    url(r'^connected_apps/$', 'connected_apps', name='profile_connected_apps'),
    url(r'^password/$', 'password', name='profile_password'),
    url(r'^position/$', 'position', name='profile_position'),
    url(r'^email/$', 'add_email', name='profile_add_email'),

    # Ajax views
    url(r'^deleteposition/$', 'delete_position', name='profile_delete_position'),
    url(r'^email/delete_email/$', 'delete_email', name='profile_delete_email'),
    url(r'^email/set_primary/$', 'set_primary', name='profile_set_primary'),
    url(r'^email/verify_email/$', 'verify_email', name='profile_verify_email'),
    url(r'^email/toggle_infomail/$', 'toggle_infomail', name='profile_toggle_infomail'),
    url(r'^email/toggle_jobmail/$', 'toggle_jobmail', name='profile_toggle_jobmail'),
    url(r'^marks/update_mark_rules/$', 'update_mark_rules', name='profile_update_mark_rules'),
    
    # Endpoint that exposes a json lump of all users but only id and name. 
    url(r'^api_plain_user_search/$', 'api_plain_user_search', name='profiles_api_plain_user_search'),

    # Endpoint that exposes a json lump of all users which have set their profile to public.
    url(r'^api_user_search/$', 'api_user_search', name='profiles_api_user_search'),
    url(r'^user_search/$', 'user_search', name='profiles_user_search'),

    # Profile index with active tab.
    url(r'^(?P<active_tab>\w+)/$', 'index', name='profiles_active'),
)
