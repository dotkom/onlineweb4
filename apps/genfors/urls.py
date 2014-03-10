from django.conf.urls import patterns, include, url

urlpatterns = patterns('apps.genfors.views',
    url(r'^$', 'genfors', name='genfors_index'),
    url(r'^admin/$', 'admin', name='genfors_admin'),
    url(r'^admin/logout$', 'admin_logout', name='genfors_admin_logout'),
    url(r'^admin/question/new$', 'question_admin', name='genfors_question_new'),
    url(r'^admin/question/(?P<question_id>\d+)/$', 'question_admin', name='genfors_question_edit'),
    url(r'^admin/question/(?P<question_id>\d+)/close$', 'question_close', name='genfors_question_close'),
    url(r'^admin/question/(?P<question_id>\d+)/reset$', 'question_reset', name='genfors_question_reset'),
    url(r'^admin/question/(?P<question_id>\d+)/delete$', 'question_delete', name='genfors_question_delete'),
    url(r'^admin/users$', 'registered_voters', name='genfors_users'),
    url(r'^admin/end$', 'genfors_end', name='genfors_admin_end'),
    url(r'^admin/lock_registration$', 'genfors_lock_registration', name='genfors_admin_lock_registration'),
    url(r'^admin/open_registration$', 'genfors_open_registration', name='genfors_admin_open_registration'),
    url(r'^vote', 'vote', name='genfors_vote'),
)
