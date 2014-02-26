from django.conf.urls import patterns, include, url

urlpatterns = patterns('apps.genfors.views',
    url(r'^$', 'genfors', name='genfors_index'),
    url(r'^admin$', 'admin', name='genfors_admin'),
    url(r'^admin/logout$', 'admin_logout', name='genfors_admin_logout'),
    url(r'^vote', 'vote', name='genfors_vote'),
)
