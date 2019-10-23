# -*- coding: utf-8 -*-

from django.conf.urls import url

from apps.events.dashboard import views

urlpatterns = [
    url(r'^$', views.index, name='dashboard_events_index'),
    url(r'^past$', views.past, name='dashboard_events_past'),

    url(r'^create/$', views.CreateEventView.as_view(), name='dashboard_event_create'),
    # details views
    url(r'^(?P<event_id>\d+)/$', views.event_details, name='dashboard_event_details'),
    url(r'^(?P<event_id>\d+)/edit/$', views.UpdateEventView.as_view(), name='dashboard_events_edit'),
    url(r'^(?P<event_id>\d+)/create_attendance/$', views.AddAttendanceView.as_view(),
        name='dashboard_event_create_attendance'),
    url(r'^(?P<event_id>\d+)/edit_attendance/$', views.UpdateAttendanceView.as_view(),
        name='dashboard_events_edit_attendance'),
    url(r'^(?P<event_id>\d+)/add_company/$', views.AddCompanyEventView.as_view(),
        name='dashboard_events_add_company'),
    url(r'^(?P<event_id>\d+)/remove_company/(?P<pk>\d+)/$', views.RemoveCompanyEventView.as_view(),
        name='dashboard_events_remove_company'),
    url(r'^(?P<event_id>\d+)/add_feedback/$', views.AddFeedbackRelationView.as_view(),
        name='dashboard_events_add_feedback'),
    url(r'^(?P<event_id>\d+)/remove_feedback/(?P<pk>\d+)/$', views.RemoveFeedbackRelationView.as_view(),
        name='dashboard_events_remove_feedback'),
    url(r'^(?P<event_id>\d+)/add_payment/$', views.AddPaymentView.as_view(),
        name='dashboard_events_add_payment'),
    url(r'^(?P<event_id>\d+)/remove_payment/(?P<pk>\d+)/$', views.RemovePaymentView.as_view(),
        name='dashboard_events_remove_payment'),
    url(r'^(?P<event_id>\d+)/add_payment_price/(?P<pk>\d+)$', views.AddPaymentPriceView.as_view(),
        name='dashboard_events_add_payment_price'),
    url(r'^(?P<event_id>\d+)/remove_payment_price/(?P<pk>\d+)/$', views.RemovePaymentPriceView.as_view(),
        name='dashboard_events_remove_payment_price'),
    # url endpoints for saving forms
    url(r'^(?P<event_id>\d+)/attendance/$', views.event_change_attendance, name='dashboard_event_change_attendance'),
    url(r'^(?P<event_id>\d+)/attendees/$', views.event_change_attendees, name='dashboard_event_change_attendees'),
    url(r'^(?P<event_id>\d+)/reservation/$', views.event_change_reservation, name='dashboard_event_change_reservation'),
    # catch-all for other tabs
    url(r'^(?P<event_id>\d+)/(?P<active_tab>\w+)/$', views.event_details, name='dashboard_event_details_active'),


    url(r'^attendee/(?P<attendee_id>\d+)/$', views.attendee_details, name='dashboard_attendee_details'),
]
