from django.conf.urls import patterns, url

urlpatterns = patterns(
    'apps.genfors.views',
    url(r'^$', 'genfors', name='genfors_index'),
    url(r'^logout$', 'logout', name='genfors_logout'),
    url(r'^admin/$', 'admin', name='genfors_admin'),
    url(r'^admin/logout$', 'admin_logout', name='genfors_admin_logout'),
    url(r'^admin/question/new$', 'question_admin', name='genfors_question_new'),
    url(r'^admin/question/(?P<question_id>\d+)/$', 'question_admin', name='genfors_question_edit'),
    url(r'^admin/question/(?P<question_id>\d+)/close$', 'question_close', name='genfors_question_close'),
    url(r'^admin/question/(?P<question_id>\d+)/reset$', 'question_reset', name='genfors_question_reset'),
    url(r'^admin/question/(?P<question_id>\d+)/delete$', 'question_delete', name='genfors_question_delete'),
    url(r'^admin/users$', 'registered_voters', name='genfors_users'),
    url(r'^admin/user/can_vote$', 'user_can_vote', name='genfors_user_can_vote'),
    url(r'^admin/end$', 'genfors_end', name='genfors_admin_end'),
    url(r'^admin/lock_registration$', 'genfors_lock_registration', name='genfors_admin_lock_registration'),
    url(r'^admin/open_registration$', 'genfors_open_registration', name='genfors_admin_open_registration'),
    url(r'^vote$', 'vote', name='genfors_vote'),
    url(r'^api/admin$', 'api_admin', name='api_admin'),
    url(r'^api/user$', 'api_user', name='api_user'),
)
