# -*- encoding: utf-8 -*-

from django.conf.urls import url

from apps.profiles import views

urlpatterns = [
    url(r'^$', views.index, name='profiles'),

    # Show a specific profile.
    url(r'^view/(?P<username>[a-zA-Z0-9_-]+)/$', views.view_profile, name='profiles_view'),

    url(r'^feedback-pending/$', views.feedback_pending, name='feedback_pending'),
    url(r'^edit/$', views.edit_profile, name='profile_edit'),
    url(r'^privacy/$', views.privacy, name='profile_privacy'),
    url(r'^connected_apps/$', views.connected_apps, name='profile_connected_apps'),
    url(r'^password/$', views.password, name='profile_password'),
    url(r'^position/$', views.position, name='profile_position'),
    url(r'^email/$', views.add_email, name='profile_add_email'),
    url(r'^create_gsuite/$', views.GSuiteCreateAccount.as_view(), name='profile_create_gsuite_account'),
    # url(r'^internal_services/$', views.internal_services, name='profile_internal_services'),

    # Ajax views
    url(r'^deleteposition/$', views.delete_position, name='profile_delete_position'),
    url(r'^email/delete_email/$', views.delete_email, name='profile_delete_email'),
    url(r'^email/set_primary/$', views.set_primary, name='profile_set_primary'),
    url(r'^email/verify_email/$', views.verify_email, name='profile_verify_email'),
    url(r'^email/toggle_infomail/$', views.toggle_infomail, name='profile_toggle_infomail'),
    url(r'^email/toggle_jobmail/$', views.toggle_jobmail, name='profile_toggle_jobmail'),
    url(r'^marks/update_mark_rules/$', views.update_mark_rules, name='profile_update_mark_rules'),

    # Endpoint that exposes a json lump of all users but only id and name.
    url(r'^api_plain_user_search/$', views.api_plain_user_search, name='profiles_api_plain_user_search'),

    # Endpoint that exposes a json lump of all users which have set their profile to public.
    url(r'^api_user_search/$', views.api_user_search, name='profiles_api_user_search'),
    url(r'^user_search/$', views.user_search, name='profiles_user_search'),

    # Profile index with active tab.
    url(r'^(?P<active_tab>\w+)/$', views.index, name='profiles_active'),
]
