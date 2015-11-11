from django.conf.urls import patterns, url
from apps.rutinator.dashboard.views import TaskListView

urlpatterns = patterns(
    'apps.rutinator.dashboard.views',
    url(r'^$', TaskListView.as_view(), name='task_view'),
)
