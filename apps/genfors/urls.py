from django.conf.urls import url

from apps.genfors import views

urlpatterns = [
    url(r'^$', views.genfors, name='genfors_index'),
    url(r'^logout$', views.logout, name='genfors_logout'),
    url(r'^admin/$', views.admin, name='genfors_admin'),
    url(r'^admin/logout$', views.admin_logout, name='genfors_admin_logout'),
    url(r'^admin/question/new$', views.question_admin, name='genfors_question_new'),
    url(r'^admin/question/(?P<question_id>\d+)/$', views.question_admin, name='genfors_question_edit'),
    url(r'^admin/question/(?P<question_id>\d+)/close$', views.question_close, name='genfors_question_close'),
    url(r'^admin/question/(?P<question_id>\d+)/reset$', views.question_reset, name='genfors_question_reset'),
    url(r'^admin/question/(?P<question_id>\d+)/delete$', views.question_delete, name='genfors_question_delete'),
    url(r'^admin/users$', views.registered_voters, name='genfors_users'),
    url(r'^admin/user/can_vote$', views.user_can_vote, name='genfors_user_can_vote'),
    url(r'^admin/end$', views.genfors_end, name='genfors_admin_end'),
    url(r'^admin/lock_registration$', views.genfors_lock_registration, name='genfors_admin_lock_registration'),
    url(r'^admin/open_registration$', views.genfors_open_registration, name='genfors_admin_open_registration'),
    url(r'^vote$', views.vote, name='genfors_vote'),
    url(r'^api/admin$', views.api_admin, name='api_admin'),
    url(r'^api/user$', views.api_user, name='api_user'),
]
