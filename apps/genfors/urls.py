from django.conf.urls import patterns, include, url

urlpatterns = patterns('apps.genfors.views',
	url(r'^$', 'genfors', name='genfors_index'),
	url(r'^admin$', 'admin', name='genfors_admin'),
)
