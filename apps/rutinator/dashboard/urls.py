from django.conf.urls import patterns, url
from apps.rutinator.dashboard.views import TaskListView, CreateTaskView

urlpatterns = patterns(
    'apps.rutinator.dashboard.views',
    url(r'^$', TaskListView.as_view(), name='task_view'),
    url(r'^create/$', CreateTaskView.as_view(), name='task_create')
)
