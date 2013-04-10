from django.conf.urls import patterns, include, url

urlpatterns = patterns('apps.article.views',
    url(r'^$', 'index', name='article_index'),
    url(r'^archive$', 'archive', name='article_archive'),
    url(r'^(?P<article_id>\d+)/$', 'details', name='article_details'),
)
